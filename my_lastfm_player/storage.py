from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import tempfile
from dataclasses import replace
from pathlib import Path
from threading import RLock
from typing import Any, Protocol

from my_lastfm_player.models import Track, TrackStatus

LOGGER = logging.getLogger(__name__)

APP_DIR_NAME = "myLastFmPlayer"
TRACKS_DIR_NAME = "tracks"
CACHE_FILENAME = "download-cache.json"
LOOKUP_CACHE_FILENAME = "lookup-cache.json"
CREDENTIALS_FILENAME = "lastfm-credentials.json"
DEFAULT_DOWNLOADS_DIR = "downloads"
SECRET_TOOL_ATTRIBUTE_APP = "myLastFmPlayer"


class StorageError(RuntimeError):
    """Raised when persisted application data cannot be read or written."""


class SessionKeyStore(Protocol):
    """Storage boundary for Last.fm session keys."""

    def load(self, username: str) -> str:
        """Return the stored session key for ``username`` or an empty string."""

    def save(self, username: str, session_key: str) -> None:
        """Persist ``session_key`` for ``username`` when secure storage is available."""


class SecretToolSessionKeyStore:
    """Store Last.fm session keys in the desktop secret service via ``secret-tool``."""

    def __init__(self, executable: str = "secret-tool") -> None:
        self.executable = executable

    def load(self, username: str) -> str:
        if not username or shutil.which(self.executable) is None:
            return ""
        try:
            result = subprocess.run(
                [
                    self.executable,
                    "lookup",
                    "application",
                    SECRET_TOOL_ATTRIBUTE_APP,
                    "username",
                    username,
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=5,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            LOGGER.warning("Could not load Last.fm session key from secret service: %s", error)
            return ""
        if result.returncode != 0:
            return ""
        return result.stdout.strip()

    def save(self, username: str, session_key: str) -> None:
        if not username or not session_key or shutil.which(self.executable) is None:
            return
        try:
            subprocess.run(
                [
                    self.executable,
                    "store",
                    "--label",
                    f"myLastFmPlayer Last.fm session for {username}",
                    "application",
                    SECRET_TOOL_ATTRIBUTE_APP,
                    "username",
                    username,
                ],
                input=session_key,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=5,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            LOGGER.warning("Could not save Last.fm session key to secret service: %s", error)


class JsonTrackRepository:
    """Repository that stores track lists and download cache data as JSON files."""

    def __init__(
        self,
        data_dir: Path | None = None,
        downloads_dir: Path | None = None,
        session_key_store: SessionKeyStore | None = None,
    ) -> None:
        self.data_dir = data_dir or default_data_dir()
        self.downloads_dir = downloads_dir or self.data_dir / DEFAULT_DOWNLOADS_DIR
        self.tracks_dir = self.data_dir / TRACKS_DIR_NAME
        self.cache_path = self.data_dir / CACHE_FILENAME
        self.lookup_cache_path = self.data_dir / LOOKUP_CACHE_FILENAME
        self._session_key_store = session_key_store or SecretToolSessionKeyStore()
        self._lock = RLock()

    @property
    def credentials_path(self) -> Path:
        """Return the path for non-secret Last.fm credential preferences."""

        return self.data_dir / CREDENTIALS_FILENAME

    def load_tracks(self, username: str) -> list[Track]:
        """Load all stored tracks for ``username``."""

        with self._lock:
            path = self.user_tracks_path(username)
            if not path.exists():
                return []

            data = _read_json_file(path)
            if not isinstance(data, list):
                raise StorageError(f"{path} must contain a JSON array of tracks")

            return [_normalize_download_file_state(Track.from_dict(item)) for item in data]

    def save_tracks(self, username: str, tracks: list[Track]) -> None:
        """Atomically save ``tracks`` for ``username``."""

        path = self.user_tracks_path(username)
        with self._lock:
            _atomic_write_json(path, [track.to_dict() for track in tracks])

    def merge_tracks(self, username: str, updates: list[Track]) -> list[Track]:
        """Merge ``updates`` into the stored tracks for ``username`` and save them."""

        with self._lock:
            merged_tracks = merge_track_updates(self.load_tracks(username), updates)
            self.save_tracks(username, merged_tracks)
            return merged_tracks

    def delete_tracks(self, username: str) -> None:
        """Delete the stored track list for ``username`` if it exists."""

        with self._lock:
            path = self.user_tracks_path(username)
            if path.exists():
                path.unlink()

    def user_tracks_path(self, username: str) -> Path:
        """Return the JSON path for ``username``."""

        return self.tracks_dir / f"{sanitize_path_component(username)}.json"

    def wipe(self) -> None:
        """Delete all cached data files (credentials, track lists, caches).

        Audio files in the downloads directory are intentionally kept.
        Deletion errors are printed to stdout and silently skipped.
        """

        with self._lock:
            targets: list[Path] = [self.credentials_path, self.cache_path, self.lookup_cache_path]
            if self.tracks_dir.is_dir():
                targets.extend(self.tracks_dir.iterdir())
            for path in targets:
                try:
                    if path.is_file():
                        path.unlink()
                except OSError as error:
                    LOGGER.warning("Could not delete %s during wipe: %s", path, error)

    def load_download_cache(self) -> dict[str, Track]:
        """Load cached downloaded tracks keyed by cache key."""

        with self._lock:
            if not self.cache_path.exists():
                return {}

            data = _read_json_file(self.cache_path)
            if not isinstance(data, list):
                raise StorageError(f"{self.cache_path} must contain a JSON array of cached tracks")

            tracks = [
                track
                for item in data
                if (track := _normalize_download_file_state(Track.from_dict(item))).local_path
            ]
            return {track.cache_key: track for track in tracks}

    def save_download_cache(self, tracks: list[Track]) -> None:
        """Persist downloaded tracks that have a local file path."""

        cached_tracks = [
            track
            for track in (_normalize_download_file_state(track) for track in tracks)
            if track.local_path
        ]
        deduplicated = {track.cache_key: track for track in cached_tracks}
        sorted_tracks = sorted(deduplicated.values(), key=lambda item: item.cache_key)
        with self._lock:
            _atomic_write_json(
                self.cache_path,
                [track.to_dict() for track in sorted_tracks],
            )

    def mark_cached_downloads(self, tracks: list[Track]) -> list[Track]:
        """Return ``tracks`` with cached local download paths restored."""

        cache = self.load_download_cache()
        marked_tracks: list[Track] = []
        for track in tracks:
            cached_track = cache.get(track.cache_key)
            if cached_track is None:
                marked_tracks.append(track)
                continue
            marked_tracks.append(
                replace(
                    track,
                    youtube_url=track.youtube_url or cached_track.youtube_url,
                    local_path=cached_track.local_path,
                    status=TrackStatus.DOWNLOADED,
                    error=None,
                    file_type=track.file_type or cached_track.file_type,
                    bitrate_kbps=track.bitrate_kbps or cached_track.bitrate_kbps,
                )
            )
        return marked_tracks

    def load_lookup_cache(self) -> dict[str, Track]:
        """Load cached YouTube lookup results keyed by cache key."""

        with self._lock:
            if not self.lookup_cache_path.exists():
                return {}

            data = _read_json_file(self.lookup_cache_path)
            if not isinstance(data, list):
                raise StorageError(
                    f"{self.lookup_cache_path} must contain a JSON array of cached lookups"
                )

            tracks = [Track.from_dict(item) for item in data]
            return {track.cache_key: track for track in tracks}

    def save_lookup_cache(self, tracks: list[Track]) -> None:
        """Persist tracks with resolved or known-missing YouTube lookup state."""

        with self._lock:
            existing_cache = self.load_lookup_cache()
            lookup_tracks = [
                track
                for track in tracks
                if track.youtube_url or track.status is TrackStatus.NOT_FOUND
            ]
            merged_cache = {**existing_cache, **{track.cache_key: track for track in lookup_tracks}}
            sorted_tracks = sorted(merged_cache.values(), key=lambda item: item.cache_key)
            _atomic_write_json(
                self.lookup_cache_path,
                [track.to_dict() for track in sorted_tracks],
            )

    def forget_lookup_cache_keys(self, cache_keys: set[str]) -> None:
        """Remove cached YouTube lookup results for ``cache_keys``."""

        if not cache_keys:
            return
        with self._lock:
            existing_cache = self.load_lookup_cache()
            filtered_tracks = [
                track for key, track in existing_cache.items() if key not in cache_keys
            ]
            sorted_tracks = sorted(filtered_tracks, key=lambda item: item.cache_key)
            _atomic_write_json(
                self.lookup_cache_path,
                [track.to_dict() for track in sorted_tracks],
            )

    def mark_cached_lookups(self, tracks: list[Track]) -> list[Track]:
        """Return ``tracks`` with cached YouTube lookup results restored."""

        cache = self.load_lookup_cache()
        marked_tracks: list[Track] = []
        for track in tracks:
            cached_track = cache.get(track.cache_key)
            if cached_track is None:
                marked_tracks.append(track)
                continue
            if cached_track.youtube_url:
                marked_tracks.append(
                    replace(
                        track,
                        youtube_url=track.youtube_url or cached_track.youtube_url,
                        status=(
                            track.status
                            if track.status is TrackStatus.DOWNLOADED
                            else TrackStatus.QUEUED
                        ),
                        error=None,
                    )
                )
                continue
            if cached_track.status is TrackStatus.NOT_FOUND:
                marked_tracks.append(
                    replace(
                        track,
                        youtube_url=None,
                        status=TrackStatus.NOT_FOUND,
                        error=cached_track.error,
                    )
                )
                continue
            marked_tracks.append(track)
        return marked_tracks


    def load_credentials(self) -> dict[str, object]:
        """Load persisted Last.fm credentials, returning an empty dict if absent or corrupt."""

        with self._lock:
            if not self.credentials_path.exists():
                return {}
            try:
                data = _read_json_file(self.credentials_path)
            except StorageError:
                return {}
            if not isinstance(data, dict):
                return {}
            credentials = dict(data)
            username = credentials.get("username", "")
            credentials.pop("session_key", None)
            if isinstance(username, str):
                session_key = self._session_key_store.load(username)
                if session_key:
                    credentials["session_key"] = session_key
            return credentials

    def save_credentials(self, credentials: dict[str, object]) -> None:
        """Atomically persist Last.fm credentials."""

        with self._lock:
            stored_credentials = dict(credentials)
            session_key = stored_credentials.pop("session_key", "")
            username = stored_credentials.get("username", "")
            if isinstance(username, str) and isinstance(session_key, str):
                self._session_key_store.save(username, session_key)
            _atomic_write_json(self.credentials_path, stored_credentials)


def default_data_dir() -> Path:
    """Return the XDG-style data directory used by default."""

    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home) / APP_DIR_NAME
    return Path.home() / ".local" / "share" / APP_DIR_NAME


def sanitize_path_component(value: str) -> str:
    """Return ``value`` normalized for safe use as one path component."""

    safe_value = "".join(
        character if character.isalnum() or character in ".-_" else "_" for character in value
    )
    safe_value = safe_value.strip("._")
    if not safe_value:
        raise ValueError("Path component must contain at least one safe character")
    return safe_value


def _read_json_file(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as error:
        raise StorageError(f"{path} contains invalid JSON: {error}") from error
    except OSError as error:
        raise StorageError(f"Could not read {path}: {error}") from error


def _normalize_download_file_state(track: Track) -> Track:
    if not track.local_path:
        if track.status is TrackStatus.DOWNLOADED:
            return _track_needing_download(track)
        return track

    if Path(track.local_path).is_file():
        return track

    return _track_needing_download(track)


def _track_needing_download(track: Track) -> Track:
    return replace(
        track,
        local_path=None,
        status=TrackStatus.QUEUED if track.youtube_url else TrackStatus.FETCHED,
        file_type=None,
        bitrate_kbps=None,
        error=None,
    )


def merge_track_updates(existing_tracks: list[Track], updates: list[Track]) -> list[Track]:
    """Return ``existing_tracks`` with matching ``updates`` applied, appending new tracks.

    Each matching update is applied via ``Track.merge_preserving`` so that already-resolved
    status and optional fields (youtube_url, local_path, …) are never overwritten by a
    lower-ranked incoming snapshot (e.g. a partial Last.fm fetch arriving while lookup runs).
    """
    updates_by_key = {track.cache_key: track for track in updates}
    merged_tracks: list[Track] = []
    seen_keys: set[str] = set()
    for track in existing_tracks:
        incoming = updates_by_key.get(track.cache_key)
        merged = Track.merge_preserving(track, incoming) if incoming is not None else track
        merged_tracks.append(merged)
        seen_keys.add(track.cache_key)
    merged_tracks.extend(track for track in updates if track.cache_key not in seen_keys)
    return merged_tracks


def _atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())
        temp_path.replace(path)
    except OSError as error:
        raise StorageError(f"Could not write {path}: {error}") from error
    finally:
        if temp_path.exists():
            temp_path.unlink()

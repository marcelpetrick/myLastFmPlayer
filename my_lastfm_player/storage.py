from __future__ import annotations

import json
import os
import tempfile
from dataclasses import replace
from pathlib import Path
from typing import Any

from my_lastfm_player.models import Track, TrackStatus

APP_DIR_NAME = "myLastFmPlayer"
TRACKS_DIR_NAME = "tracks"
CACHE_FILENAME = "download-cache.json"
DEFAULT_DOWNLOADS_DIR = "downloads"


class StorageError(RuntimeError):
    """Raised when persisted application data cannot be read or written."""


class JsonTrackRepository:
    """Repository that stores track lists and download cache data as JSON files."""

    def __init__(self, data_dir: Path | None = None, downloads_dir: Path | None = None) -> None:
        self.data_dir = data_dir or default_data_dir()
        self.downloads_dir = downloads_dir or self.data_dir / DEFAULT_DOWNLOADS_DIR
        self.tracks_dir = self.data_dir / TRACKS_DIR_NAME
        self.cache_path = self.data_dir / CACHE_FILENAME

    def load_tracks(self, username: str) -> list[Track]:
        """Load all stored tracks for ``username``."""

        path = self.user_tracks_path(username)
        if not path.exists():
            return []

        data = _read_json_file(path)
        if not isinstance(data, list):
            raise StorageError(f"{path} must contain a JSON array of tracks")

        return [Track.from_dict(item) for item in data]

    def save_tracks(self, username: str, tracks: list[Track]) -> None:
        """Atomically save ``tracks`` for ``username``."""

        path = self.user_tracks_path(username)
        _atomic_write_json(path, [track.to_dict() for track in tracks])

    def delete_tracks(self, username: str) -> None:
        """Delete the stored track list for ``username`` if it exists."""

        path = self.user_tracks_path(username)
        if path.exists():
            path.unlink()

    def user_tracks_path(self, username: str) -> Path:
        """Return the JSON path for ``username``."""

        return self.tracks_dir / f"{sanitize_path_component(username)}.json"

    def load_download_cache(self) -> dict[str, Track]:
        """Load cached downloaded tracks keyed by cache key."""

        if not self.cache_path.exists():
            return {}

        data = _read_json_file(self.cache_path)
        if not isinstance(data, list):
            raise StorageError(f"{self.cache_path} must contain a JSON array of cached tracks")

        tracks = [Track.from_dict(item) for item in data]
        return {track.cache_key: track for track in tracks}

    def save_download_cache(self, tracks: list[Track]) -> None:
        """Persist downloaded tracks that have a local file path."""

        cached_tracks = [track for track in tracks if track.local_path]
        deduplicated = {track.cache_key: track for track in cached_tracks}
        sorted_tracks = sorted(deduplicated.values(), key=lambda item: item.cache_key)
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
                )
            )
        return marked_tracks


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

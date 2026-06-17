from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, replace
from enum import StrEnum
from typing import Any


class TrackStatus(StrEnum):
    """Track lifecycle states used by fetch, lookup, download, and playback workflows."""

    FETCHED = "Fetched"
    QUEUED = "Queued"
    SEARCHING = "Searching"
    DOWNLOADING = "Downloading"
    DOWNLOADED = "Downloaded"
    FAILED = "Failed"
    NOT_FOUND = "Not found"


INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
COLLAPSED_WHITESPACE = re.compile(r"\s+")
MAX_FILENAME_LENGTH = 240
CACHE_KEY_SEPARATOR = "\x1f"
AUDIO_STEM_HASH_LENGTH = 10

_ALLOWED_STATUS_TRANSITIONS: dict[TrackStatus, set[TrackStatus]] = {
    TrackStatus.FETCHED: {
        TrackStatus.SEARCHING,
        TrackStatus.QUEUED,
        TrackStatus.DOWNLOADING,
        TrackStatus.DOWNLOADED,
        TrackStatus.FAILED,
        TrackStatus.NOT_FOUND,
    },
    TrackStatus.SEARCHING: {
        TrackStatus.QUEUED,
        TrackStatus.DOWNLOADING,
        TrackStatus.DOWNLOADED,
        TrackStatus.FAILED,
        TrackStatus.NOT_FOUND,
    },
    TrackStatus.QUEUED: {
        TrackStatus.DOWNLOADING,
        TrackStatus.DOWNLOADED,
        TrackStatus.FAILED,
        TrackStatus.NOT_FOUND,
    },
    TrackStatus.DOWNLOADING: {
        TrackStatus.DOWNLOADED,
        TrackStatus.FAILED,
        TrackStatus.NOT_FOUND,
    },
    TrackStatus.FAILED: {
        TrackStatus.DOWNLOADED,
        TrackStatus.NOT_FOUND,
    },
    TrackStatus.NOT_FOUND: {
        TrackStatus.QUEUED,
        TrackStatus.DOWNLOADING,
        TrackStatus.DOWNLOADED,
    },
    TrackStatus.DOWNLOADED: set(),
}


@dataclass(frozen=True, slots=True)
class Track:  # pylint: disable=too-many-instance-attributes  # domain model
    """Immutable representation of one Last.fm track and its local processing state."""

    artist: str
    title: str
    lastfm_url: str | None = None
    loved_at: str | None = None
    youtube_url: str | None = None
    local_path: str | None = None
    status: TrackStatus = TrackStatus.FETCHED
    retry_count: int = 0
    error: str | None = None
    file_type: str | None = None
    bitrate_kbps: int | None = None

    def __post_init__(self) -> None:
        if not self.artist:
            raise ValueError("Track artist must not be empty")
        if not self.title:
            raise ValueError("Track title must not be empty")
        if self.retry_count < 0:
            raise ValueError("Track retry_count must not be negative")
        if self.bitrate_kbps is not None and self.bitrate_kbps < 0:
            raise ValueError("Track bitrate_kbps must not be negative")

    @property
    def cache_key(self) -> str:
        """Return the stable key used for persistence and cache lookups."""

        return build_track_cache_key(self.artist, self.title)

    @property
    def audio_base_name(self) -> str:
        """Return the sanitized human-readable base filename (no extension)."""

        return build_audio_base_name(self.artist, self.title)

    @property
    def audio_file_stem(self) -> str:
        """Return a collision-resistant base filename (no extension) for downloads."""

        return build_audio_file_stem(self.artist, self.title)

    def with_status(self, status: TrackStatus, error: str | None = None) -> Track:
        """Return a copy with ``status`` and an optional error message applied."""

        return replace(self, status=status, error=error)

    def increment_retry(self, error: str | None = None) -> Track:
        """Return a copy with the retry count increased by one."""

        return replace(self, retry_count=self.retry_count + 1, error=error)

    @classmethod
    def merge_preserving(cls, old: Track, new: Track) -> Track:
        """Merge two snapshots without letting stale workflow updates win."""
        merged_status = _merge_status(old, new)
        merged_error = new.error if merged_status is new.status else old.error
        return cls(
            artist=new.artist,
            title=new.title,
            lastfm_url=new.lastfm_url if new.lastfm_url is not None else old.lastfm_url,
            loved_at=new.loved_at if new.loved_at is not None else old.loved_at,
            youtube_url=new.youtube_url if new.youtube_url is not None else old.youtube_url,
            local_path=new.local_path if new.local_path is not None else old.local_path,
            status=merged_status,
            retry_count=max(old.retry_count, new.retry_count),
            error=merged_error,
            file_type=new.file_type if new.file_type is not None else old.file_type,
            bitrate_kbps=new.bitrate_kbps if new.bitrate_kbps is not None else old.bitrate_kbps,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the track to a JSON-compatible dictionary."""

        return {
            "artist": self.artist,
            "title": self.title,
            "lastfm_url": self.lastfm_url,
            "loved_at": self.loved_at,
            "youtube_url": self.youtube_url,
            "local_path": self.local_path,
            "status": self.status.value,
            "retry_count": self.retry_count,
            "error": self.error,
            "file_type": self.file_type,
            "bitrate_kbps": self.bitrate_kbps,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Track:
        """Deserialize a track from persisted JSON data."""

        status = _parse_status(data.get("status", TrackStatus.FETCHED.value))
        return cls(
            artist=_require_string(data, "artist"),
            title=_require_string(data, "title"),
            lastfm_url=_optional_string(data, "lastfm_url"),
            loved_at=_optional_string(data, "loved_at"),
            youtube_url=_optional_string(data, "youtube_url"),
            local_path=_optional_string(data, "local_path"),
            status=status,
            retry_count=int(data.get("retry_count", 0)),
            error=_optional_string(data, "error"),
            file_type=_optional_string(data, "file_type"),
            bitrate_kbps=_optional_int(data, "bitrate_kbps"),
        )


def _merge_status(old: Track, new: Track) -> TrackStatus:
    if old.status is new.status:
        return new.status

    if old.status is TrackStatus.DOWNLOADED:
        return old.status

    if old.status is TrackStatus.NOT_FOUND and not (
        new.youtube_url or new.local_path
    ):
        return old.status

    if new.status in _ALLOWED_STATUS_TRANSITIONS[old.status]:
        return new.status

    return old.status


def build_track_cache_key(artist: str, title: str) -> str:
    """Build the exact cache key for ``artist`` and ``title``."""

    return f"{artist}{CACHE_KEY_SEPARATOR}{title}"


def build_audio_base_name(artist: str, title: str) -> str:
    """Build a safe base filename (no extension) for ``artist`` and ``title``."""

    base_name = sanitize_filename_part(f"{artist} - {title}")
    # Reserve 5 chars for the longest common audio extension (e.g. .webm, .opus).
    max_base = MAX_FILENAME_LENGTH - 5
    if len(base_name) <= max_base:
        return base_name
    return base_name[:max_base].rstrip()


def build_audio_file_stem(artist: str, title: str) -> str:
    """Build a safe, collision-resistant base filename for ``artist`` and ``title``."""

    digest = hashlib.sha1(build_track_cache_key(artist, title).encode("utf-8")).hexdigest()
    suffix = f" [{digest[:AUDIO_STEM_HASH_LENGTH]}]"
    base_name = sanitize_filename_part(f"{artist} - {title}")
    max_base = MAX_FILENAME_LENGTH - 5 - len(suffix)
    if len(base_name) > max_base:
        base_name = base_name[:max_base].rstrip()
    return f"{base_name}{suffix}"


def sanitize_filename_part(value: str) -> str:
    """Sanitize one filename component and return a non-empty fallback if needed."""

    safe_value = COLLAPSED_WHITESPACE.sub(" ", value)
    safe_value = INVALID_FILENAME_CHARS.sub("_", safe_value)
    safe_value = safe_value.strip(" .")
    return safe_value or "Unknown Track"


def _require_string(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"Track field {key!r} must be a non-empty string")
    return value


def _optional_string(data: dict[str, Any], key: str) -> str | None:
    value = data.get(key)
    if value is None or isinstance(value, str):
        return value
    raise ValueError(f"Track field {key!r} must be a string or null")


def _optional_int(data: dict[str, Any], key: str) -> int | None:
    value = data.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"Track field {key!r} must be an integer or null")
    return value


def _parse_status(value: Any) -> TrackStatus:
    try:
        return TrackStatus(value)
    except ValueError as error:
        raise ValueError(f"Track field 'status' has an unknown value: {value!r}") from error

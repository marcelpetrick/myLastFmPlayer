from __future__ import annotations

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


@dataclass(frozen=True, slots=True)
class Track:
    """Immutable representation of one Last.fm track and its local processing state."""

    artist: str
    title: str
    lastfm_url: str | None = None
    youtube_url: str | None = None
    local_path: str | None = None
    status: TrackStatus = TrackStatus.FETCHED
    retry_count: int = 0
    error: str | None = None

    def __post_init__(self) -> None:
        if not self.artist:
            raise ValueError("Track artist must not be empty")
        if not self.title:
            raise ValueError("Track title must not be empty")
        if self.retry_count < 0:
            raise ValueError("Track retry_count must not be negative")

    @property
    def cache_key(self) -> str:
        """Return the stable key used for persistence and cache lookups."""

        return build_track_cache_key(self.artist, self.title)

    @property
    def mp3_filename(self) -> str:
        """Return the sanitized MP3 filename used for downloads."""

        return build_mp3_filename(self.artist, self.title)

    def with_status(self, status: TrackStatus, error: str | None = None) -> Track:
        """Return a copy with ``status`` and an optional error message applied."""

        return replace(self, status=status, error=error)

    def increment_retry(self, error: str | None = None) -> Track:
        """Return a copy with the retry count increased by one."""

        return replace(self, retry_count=self.retry_count + 1, error=error)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the track to a JSON-compatible dictionary."""

        return {
            "artist": self.artist,
            "title": self.title,
            "lastfm_url": self.lastfm_url,
            "youtube_url": self.youtube_url,
            "local_path": self.local_path,
            "status": self.status.value,
            "retry_count": self.retry_count,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Track:
        """Deserialize a track from persisted JSON data."""

        status = _parse_status(data.get("status", TrackStatus.FETCHED.value))
        return cls(
            artist=_require_string(data, "artist"),
            title=_require_string(data, "title"),
            lastfm_url=_optional_string(data, "lastfm_url"),
            youtube_url=_optional_string(data, "youtube_url"),
            local_path=_optional_string(data, "local_path"),
            status=status,
            retry_count=int(data.get("retry_count", 0)),
            error=_optional_string(data, "error"),
        )


def build_track_cache_key(artist: str, title: str) -> str:
    """Build the exact cache key for ``artist`` and ``title``."""

    return f"{artist}{CACHE_KEY_SEPARATOR}{title}"


def build_mp3_filename(artist: str, title: str) -> str:
    """Build a safe MP3 filename for ``artist`` and ``title``."""

    base_name = sanitize_filename_part(f"{artist} - {title}")
    filename = f"{base_name}.mp3"
    if len(filename) <= MAX_FILENAME_LENGTH:
        return filename

    suffix = ".mp3"
    return f"{base_name[: MAX_FILENAME_LENGTH - len(suffix)].rstrip()}{suffix}"


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


def _parse_status(value: Any) -> TrackStatus:
    try:
        return TrackStatus(value)
    except ValueError as error:
        raise ValueError(f"Track field 'status' has an unknown value: {value!r}") from error

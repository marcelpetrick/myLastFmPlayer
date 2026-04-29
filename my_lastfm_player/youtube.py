from __future__ import annotations

import json
import subprocess
from collections.abc import Callable, Sequence
from dataclasses import replace
from typing import Any

from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.storage import JsonTrackRepository

YTDLP_SEARCH_PREFIX = "ytsearch1:"

CommandRunner = Callable[..., subprocess.CompletedProcess[str]]


class YouTubeLookupError(RuntimeError):
    """Raised when YouTube lookup fails unexpectedly."""


class YouTubeResolver:
    def __init__(
        self,
        command_runner: CommandRunner = subprocess.run,
        executable: str = "yt-dlp",
    ) -> None:
        self.command_runner = command_runner
        self.executable = executable

    def build_query(self, track: Track) -> str:
        return f"{track.artist} {track.title}"

    def resolve_track(self, track: Track) -> Track:
        search_result = self.search_first_result(self.build_query(track))
        if search_result is None:
            return replace(track, youtube_url=None, status=TrackStatus.NOT_FOUND)
        return replace(track, youtube_url=search_result, status=TrackStatus.QUEUED, error=None)

    def resolve_tracks(self, tracks: list[Track]) -> list[Track]:
        resolved_tracks: list[Track] = []
        for track in tracks:
            if track.youtube_url:
                resolved_tracks.append(track)
                continue
            resolved_tracks.append(self.resolve_track(replace(track, status=TrackStatus.SEARCHING)))
        return resolved_tracks

    def resolve_and_store_tracks(
        self,
        username: str,
        repository: JsonTrackRepository,
    ) -> list[Track]:
        tracks = repository.load_tracks(username)
        resolved_tracks = self.resolve_tracks(tracks)
        repository.save_tracks(username, resolved_tracks)
        return resolved_tracks

    def search_first_result(self, query: str) -> str | None:
        command = [
            self.executable,
            "--dump-single-json",
            "--no-playlist",
            f"{YTDLP_SEARCH_PREFIX}{query}",
        ]
        completed = self._run(command)
        if completed.returncode != 0:
            if _looks_like_no_result(completed.stderr):
                return None
            raise YouTubeLookupError(completed.stderr.strip() or "yt-dlp lookup failed")
        if not completed.stdout.strip():
            return None
        return _extract_youtube_url(completed.stdout)

    def _run(self, command: Sequence[str]) -> subprocess.CompletedProcess[str]:
        try:
            return self.command_runner(
                command,
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError as error:
            raise YouTubeLookupError(f"Could not run {self.executable}: {error}") from error


def _extract_youtube_url(stdout: str) -> str | None:
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as error:
        raise YouTubeLookupError(f"yt-dlp returned invalid JSON: {error}") from error

    if not isinstance(payload, dict):
        raise YouTubeLookupError("yt-dlp returned an unexpected JSON shape")

    entries = payload.get("entries")
    if isinstance(entries, list):
        first_entry = _first_dict(entries)
        if first_entry is None:
            return None
        return _url_from_payload(first_entry)

    return _url_from_payload(payload)


def _first_dict(values: list[Any]) -> dict[str, Any] | None:
    for value in values:
        if isinstance(value, dict):
            return value
    return None


def _url_from_payload(payload: dict[str, Any]) -> str | None:
    for key in ("webpage_url", "original_url", "url"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    video_id = payload.get("id")
    if isinstance(video_id, str) and video_id:
        return f"https://www.youtube.com/watch?v={video_id}"
    return None


def _looks_like_no_result(stderr: str) -> bool:
    lowered = stderr.lower()
    return "no video results" in lowered or "no results" in lowered

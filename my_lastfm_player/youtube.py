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
ProgressCallback = Callable[[int, str], None]
TrackUpdateCallback = Callable[[Track], None]


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

    def resolve_tracks(
        self,
        tracks: list[Track],
        progress_callback: ProgressCallback | None = None,
        track_update_callback: TrackUpdateCallback | None = None,
        priority_cache_key: str | None = None,
        max_tracks: int | None = None,
    ) -> list[Track]:
        resolved_tracks: list[Track] = []
        unresolved_indexes = [
            index for index, track in enumerate(tracks) if not track.youtube_url
        ]
        unresolved_indexes = _prioritize_indexes(
            unresolved_indexes,
            tracks,
            priority_cache_key,
        )
        if max_tracks is not None:
            unresolved_indexes = unresolved_indexes[:max_tracks]
        indexes_to_resolve = set(unresolved_indexes)
        total_to_resolve = len(unresolved_indexes)
        resolved_count = 0

        for index, track in enumerate(tracks):
            if track.youtube_url:
                resolved_tracks.append(track)
                continue
            if index not in indexes_to_resolve:
                resolved_tracks.append(track)
                continue
            resolved_count += 1
            _report(
                progress_callback,
                _percent(resolved_count - 1, total_to_resolve),
                f"Searching {resolved_count}/{total_to_resolve}: {track.artist} - {track.title}",
            )
            searching_track = replace(track, status=TrackStatus.SEARCHING)
            _report_track_update(track_update_callback, searching_track)
            resolved_track = self.resolve_track(searching_track)
            _report_track_update(track_update_callback, resolved_track)
            resolved_tracks.append(resolved_track)
            _report(
                progress_callback,
                _percent(resolved_count, total_to_resolve),
                _resolved_message(resolved_count, total_to_resolve, resolved_track),
            )
        return resolved_tracks

    def resolve_and_store_tracks(
        self,
        username: str,
        repository: JsonTrackRepository,
        progress_callback: ProgressCallback | None = None,
        track_update_callback: TrackUpdateCallback | None = None,
        priority_cache_key: str | None = None,
        max_tracks: int | None = None,
    ) -> list[Track]:
        tracks = repository.load_tracks(username)
        resolved_tracks = self.resolve_tracks(
            tracks,
            progress_callback=progress_callback,
            track_update_callback=track_update_callback,
            priority_cache_key=priority_cache_key,
            max_tracks=max_tracks,
        )
        resolved_tracks = _merge_existing_download_state(
            resolved_tracks,
            repository.load_tracks(username),
        )
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


def _prioritize_indexes(
    indexes: list[int],
    tracks: list[Track],
    priority_cache_key: str | None,
) -> list[int]:
    if priority_cache_key is None:
        return indexes
    return sorted(indexes, key=lambda index: tracks[index].cache_key != priority_cache_key)


def _percent(done: int, total: int) -> int:
    if total == 0:
        return 100
    return min(99, int(done / total * 100))


def _resolved_message(done: int, total: int, track: Track) -> str:
    if track.youtube_url:
        return f"Resolved {done}/{total}: {track.artist} - {track.title}"
    return f"No YouTube result {done}/{total}: {track.artist} - {track.title}"


def _report(
    progress_callback: ProgressCallback | None,
    value: int,
    message: str,
) -> None:
    print(f"[myLastFmPlayer] YouTube lookup progress {value}%: {message}", flush=True)
    if progress_callback is not None:
        progress_callback(value, message)


def _report_track_update(
    track_update_callback: TrackUpdateCallback | None,
    track: Track,
) -> None:
    if track_update_callback is not None:
        track_update_callback(track)


def _merge_existing_download_state(
    resolved_tracks: list[Track],
    current_tracks: list[Track],
) -> list[Track]:
    current_by_key = {track.cache_key: track for track in current_tracks}
    merged_tracks: list[Track] = []
    for track in resolved_tracks:
        current_track = current_by_key.get(track.cache_key)
        if (
            current_track is not None
            and current_track.status is TrackStatus.DOWNLOADED
            and current_track.local_path
        ):
            merged_tracks.append(
                replace(
                    track,
                    youtube_url=track.youtube_url or current_track.youtube_url,
                    local_path=current_track.local_path,
                    status=TrackStatus.DOWNLOADED,
                    error=None,
                )
            )
            continue
        merged_tracks.append(track)
    return merged_tracks

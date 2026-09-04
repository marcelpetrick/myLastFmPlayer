from __future__ import annotations

import json
import logging
import re
import subprocess
from collections.abc import Callable, Sequence
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import replace
from threading import Event
from typing import Any

from my_lastfm_player.i18n import translate
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.storage import JsonTrackRepository
from my_lastfm_player.youtube_work import (
    WorkCancelled,
    YouTubeWorkLimiter,
    run_cancellable_command,
)

LOGGER = logging.getLogger(__name__)

YTDLP_SEARCH_PREFIX = "ytsearch1:"
LOOKUP_TIMEOUT_SECONDS = 120
# An empty search result is transient often enough (YouTube gating, an over-specific
# artist field) that NOT_FOUND is re-checked this many times before it sticks.
MAX_LOOKUP_ATTEMPTS = 3
DEFAULT_LOOKUP_CONCURRENCY = 5
# Last.fm artist fields carry store suffixes ("Name - EU Store") and decorative symbols
# ("ETHER ensemble", "artist -*-") that YouTube search matches literally and so finds nothing.
ARTIST_SUFFIX_SEPARATOR = " - "
DECORATIVE_CHARS = re.compile(r"[^\w\s&\'()./-]", re.UNICODE)
COLLAPSED_WHITESPACE = re.compile(r"\s+")

CommandRunner = Callable[..., subprocess.CompletedProcess[str]]
ProgressCallback = Callable[[int, str], None]
TrackUpdateCallback = Callable[[Track], None]


class YouTubeLookupError(RuntimeError):
    """Raised when YouTube lookup fails unexpectedly."""


class YouTubeResolver:
    """Resolve tracks to YouTube URLs by invoking ``yt-dlp`` search."""

    def __init__(
        self,
        command_runner: CommandRunner = subprocess.run,
        executable: str = "yt-dlp",
        cookies_browser: str = "",
        work_limiter: YouTubeWorkLimiter | None = None,
    ) -> None:
        self.command_runner = command_runner
        self.executable = executable
        self.cookies_browser = cookies_browser
        self.work_limiter = work_limiter or YouTubeWorkLimiter()

    def build_query(self, track: Track) -> str:
        """Return the primary search query used for ``track``."""

        return f"{track.artist} {track.title}"

    def build_queries(self, track: Track) -> list[str]:
        """Return the ordered search queries tried for ``track``, most specific first."""

        simplified_artist = _simplify_artist(track.artist)
        candidates = [
            self.build_query(track),
            f"{simplified_artist} {track.title}" if simplified_artist else "",
            track.title,
        ]
        return list(dict.fromkeys(query for query in candidates if query.strip()))

    def resolve_track(self, track: Track, stop_event: Event | None = None) -> Track:
        """Resolve one track and return a copy with its lookup status updated."""

        last_error: YouTubeLookupError | None = None
        for query in self.build_queries(track):
            if stop_event is not None and stop_event.is_set():
                return replace(track, status=TrackStatus.FETCHED, error=None)
            try:
                search_result = self.search_first_result(query, stop_event, track.cache_key)
            except WorkCancelled:
                return replace(track, status=TrackStatus.FETCHED, error=None)
            except YouTubeLookupError as error:
                last_error = error
                continue
            if search_result is not None:
                return replace(
                    track,
                    youtube_url=search_result,
                    status=TrackStatus.QUEUED,
                    error=None,
                )
        if last_error is not None:
            raise last_error
        return replace(
            track,
            youtube_url=None,
            status=TrackStatus.NOT_FOUND,
            retry_count=track.retry_count + 1,
        )

    def resolve_tracks(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        tracks: list[Track],
        progress_callback: ProgressCallback | None = None,
        track_update_callback: TrackUpdateCallback | None = None,
        priority_cache_key: str | None = None,
        max_tracks: int | None = None,
        concurrency: int = DEFAULT_LOOKUP_CONCURRENCY,
        stop_event: Event | None = None,
    ) -> list[Track]:
        """Resolve eligible tracks concurrently with independent per-track failures."""

        if concurrency < 1:
            raise ValueError("concurrency must be at least 1")

        resolved_tracks: list[Track] = list(tracks)
        unresolved_indexes = [
            index
            for index, track in enumerate(tracks)
            if not track.youtube_url and _needs_lookup(track)
        ]
        unresolved_indexes = _prioritize_indexes(
            unresolved_indexes,
            tracks,
            priority_cache_key,
        )
        if max_tracks is not None:
            unresolved_indexes = unresolved_indexes[:max_tracks]
        total_to_resolve = len(unresolved_indexes)
        if not unresolved_indexes:
            return resolved_tracks

        pending_indexes = iter(unresolved_indexes)
        completed_count = 0
        futures: dict[Future[Track], int] = {}

        def submit_next(executor: ThreadPoolExecutor) -> bool:
            if stop_event is not None and stop_event.is_set():
                return False
            try:
                index = next(pending_indexes)
            except StopIteration:
                return False
            track = tracks[index]
            searching_track = replace(track, status=TrackStatus.SEARCHING, error=None)
            resolved_tracks[index] = searching_track
            _report_track_update(track_update_callback, searching_track)
            _report(
                progress_callback,
                _percent(completed_count, total_to_resolve),
                translate(
                    "YouTubeResolver",
                    "Searching {done}/{total}: {artist} - {title}",
                    done=completed_count + len(futures) + 1,
                    total=total_to_resolve,
                    artist=track.artist,
                    title=track.title,
                ),
            )
            future = executor.submit(self.resolve_track, searching_track, stop_event)
            futures[future] = index
            return True

        with ThreadPoolExecutor(max_workers=min(concurrency, total_to_resolve)) as executor:
            for _unused in range(min(concurrency, total_to_resolve)):
                submit_next(executor)
            while futures:
                completed, _pending = wait(futures, return_when=FIRST_COMPLETED)
                for future in completed:
                    index = futures.pop(future)
                    searching_track = resolved_tracks[index]
                    try:
                        resolved_track = future.result()
                    except YouTubeLookupError as exc:
                        resolved_track = replace(
                            searching_track,
                            youtube_url=None,
                            status=TrackStatus.FAILED,
                            retry_count=searching_track.retry_count + 1,
                            error=str(exc),
                        )
                    except Exception as exc:  # noqa: BLE001 - isolate one failed lookup.
                        LOGGER.exception(
                            "Unexpected lookup failure for %s - %s",
                            searching_track.artist,
                            searching_track.title,
                        )
                        resolved_track = replace(
                            searching_track,
                            youtube_url=None,
                            status=TrackStatus.FAILED,
                            retry_count=searching_track.retry_count + 1,
                            error=str(exc),
                        )
                    resolved_tracks[index] = resolved_track
                    _report_track_update(track_update_callback, resolved_track)
                    completed_count += 1
                    _report(
                        progress_callback,
                        _percent(completed_count, total_to_resolve),
                        _resolved_message(completed_count, total_to_resolve, resolved_track),
                    )
                    submit_next(executor)
        return resolved_tracks

    def resolve_and_store_tracks(  # pylint: disable=too-many-arguments
        self,
        username: str,
        repository: JsonTrackRepository,
        progress_callback: ProgressCallback | None = None,
        track_update_callback: TrackUpdateCallback | None = None,
        priority_cache_key: str | None = None,
        max_tracks: int | None = None,
        concurrency: int = DEFAULT_LOOKUP_CONCURRENCY,
        stop_event: Event | None = None,
    ) -> list[Track]:
        """Resolve stored tracks for ``username`` and persist the updated list."""

        tracks = repository.mark_cached_lookups(repository.load_tracks(username))

        def persist_track_update(track: Track) -> None:
            if track.status is not TrackStatus.SEARCHING:
                repository.append_track_update(username, track)
            _report_track_update(track_update_callback, track)

        resolved_tracks = self.resolve_tracks(
            tracks,
            progress_callback=progress_callback,
            track_update_callback=persist_track_update,
            priority_cache_key=priority_cache_key,
            max_tracks=max_tracks,
            concurrency=concurrency,
            stop_event=stop_event,
        )
        resolved_tracks = _merge_existing_download_state(
            resolved_tracks,
            repository.load_tracks(username),
        )
        merged_tracks = repository.merge_tracks(username, resolved_tracks)
        repository.save_lookup_cache(merged_tracks)
        return merged_tracks

    def search_first_result(
        self,
        query: str,
        stop_event: Event | None = None,
        work_key: str | None = None,
    ) -> str | None:
        """Return the first YouTube URL for ``query`` or ``None`` when no result exists."""

        command = [self.executable, "--dump-single-json", "--no-playlist", "--flat-playlist"]
        if self.cookies_browser:
            command += ["--cookies-from-browser", self.cookies_browser]
        command.append(f"{YTDLP_SEARCH_PREFIX}{query}")
        completed = self._run(command, stop_event, work_key)
        if completed.returncode != 0:
            if _looks_like_no_result(completed.stderr):
                return None
            raise YouTubeLookupError(completed.stderr.strip() or "yt-dlp lookup failed")
        if not completed.stdout.strip():
            return None
        return _extract_youtube_url(completed.stdout)

    def _run(
        self,
        command: Sequence[str],
        stop_event: Event | None = None,
        work_key: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        try:
            if self.command_runner is subprocess.run:
                with self.work_limiter.slot(stop_event, work_key) as acquired:
                    if not acquired:
                        raise WorkCancelled("YouTube lookup cancelled")
                    return run_cancellable_command(
                        command,
                        stop_event=stop_event,
                        timeout=LOOKUP_TIMEOUT_SECONDS,
                    )
            return self.command_runner(
                command,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=LOOKUP_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as error:
            raise YouTubeLookupError(
                f"{self.executable} lookup timed out after {LOOKUP_TIMEOUT_SECONDS}s"
            ) from error
        except OSError as error:
            raise YouTubeLookupError(f"Could not run {self.executable}: {error}") from error


def _needs_lookup(track: Track) -> bool:
    if track.status is TrackStatus.FAILED:
        return False
    if track.status is not TrackStatus.NOT_FOUND:
        return True
    return track.retry_count < MAX_LOOKUP_ATTEMPTS


def _simplify_artist(artist: str) -> str:
    """Return ``artist`` without store suffixes and decorative symbols."""

    simplified = artist.split(ARTIST_SUFFIX_SEPARATOR, 1)[0]
    simplified = DECORATIVE_CHARS.sub(" ", simplified)
    return COLLAPSED_WHITESPACE.sub(" ", simplified).strip()


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
        return translate(
            "YouTubeResolver",
            "Resolved {done}/{total}: {artist} - {title}",
            done=done,
            total=total,
            artist=track.artist,
            title=track.title,
        )
    return translate(
        "YouTubeResolver",
        "No YouTube result {done}/{total}: {artist} - {title}",
        done=done,
        total=total,
        artist=track.artist,
        title=track.title,
    )


def _report(
    progress_callback: ProgressCallback | None,
    value: int,
    message: str,
) -> None:
    LOGGER.info("YouTube lookup progress %s%%: %s", value, message)
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
    return [
        Track.merge_preserving(current_by_key[track.cache_key], track)
        if track.cache_key in current_by_key
        else track
        for track in resolved_tracks
    ]

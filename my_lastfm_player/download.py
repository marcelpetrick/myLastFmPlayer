from __future__ import annotations

import json
import logging
import random
import subprocess
import time
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace
from pathlib import Path
from threading import Event

from my_lastfm_player.i18n import translate
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.storage import JsonTrackRepository
from my_lastfm_player.youtube_work import (
    WorkCancelled,
    YouTubeWorkLimiter,
    run_cancellable_command,
)

LOGGER = logging.getLogger(__name__)

DEFAULT_CONCURRENCY = 5
# YouTube gates some innertube clients behind a PO token. A gated client reports no media
# formats at all ("Requested format is not available", whatever -f asks for) or serves a
# 403 on the media fetch, and both stick for as long as that client answers - so retrying
# the same one is pointless. Each attempt therefore forces a different client family; the
# empty entry keeps yt-dlp's own rotation as the first and fastest try. Names must exist in
# yt-dlp's INNERTUBE_CLIENTS, otherwise the attempt is silently skipped and wasted.
PLAYER_CLIENT_LADDER: tuple[str, ...] = (
    "",
    "web_embedded,android_vr",
    "tv_downgraded,android,web_creator",
)
# Fall back to a combined stream for the rare video that exposes no audio-only format.
AUDIO_FORMAT_SELECTOR = "bestaudio/bestaudio*/best"
MAX_RETRIES = len(PLAYER_CLIENT_LADDER)
BACKOFF_RANGE_SECONDS = (1.0, 5.0)
DOWNLOAD_TIMEOUT_SECONDS = 600
PROBE_TIMEOUT_SECONDS = 30

CommandRunner = Callable[..., subprocess.CompletedProcess[str]]
Sleeper = Callable[[float], None]
BackoffFactory = Callable[[], float]
ProgressCallback = Callable[[int, str], None]
TrackUpdateCallback = Callable[[Track], None]


class DownloadError(RuntimeError):
    """Raised when a track cannot be downloaded."""


class DownloadManager:  # pylint: disable=too-many-instance-attributes
    """Download resolved tracks with retry, pause/resume, and progress reporting."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        command_runner: CommandRunner = subprocess.run,
        executable: str = "yt-dlp",
        max_retries: int = MAX_RETRIES,
        backoff_factory: BackoffFactory | None = None,
        sleeper: Sleeper = time.sleep,
        cookies_browser: str = "",
        work_limiter: YouTubeWorkLimiter | None = None,
    ) -> None:
        self.command_runner = command_runner
        self.executable = executable
        self.cookies_browser = cookies_browser
        self.max_retries = max_retries
        self.backoff_factory = backoff_factory or (
            lambda: random.uniform(*BACKOFF_RANGE_SECONDS)
        )
        self.sleeper = sleeper
        self.work_limiter = work_limiter or YouTubeWorkLimiter()

    def download_and_store_tracks(  # pylint: disable=too-many-arguments
        self,
        username: str,
        repository: JsonTrackRepository,
        concurrency: int = DEFAULT_CONCURRENCY,
        progress_callback: ProgressCallback | None = None,
        track_update_callback: TrackUpdateCallback | None = None,
        priority_cache_key: str | None = None,
        max_downloads: int | None = None,
        stop_event: Event | None = None,
    ) -> list[Track]:
        """Load tracks, download eligible items, and persist results."""

        tracks = repository.mark_cached_downloads(repository.load_tracks(username))

        def persist_track_update(track: Track) -> None:
            if track.status is not TrackStatus.DOWNLOADING:
                repository.append_track_update(username, track)
            _report_track_update(track_update_callback, track)

        downloaded_tracks = self.download_tracks(
            tracks,
            repository.downloads_dir,
            concurrency=concurrency,
            progress_callback=progress_callback,
            track_update_callback=persist_track_update,
            priority_cache_key=priority_cache_key,
            max_downloads=max_downloads,
            stop_event=stop_event,
        )
        merged_tracks = repository.merge_tracks(username, downloaded_tracks)
        repository.merge_download_cache(merged_tracks)
        return merged_tracks

    def download_tracks(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        tracks: list[Track],
        downloads_dir: Path,
        concurrency: int = DEFAULT_CONCURRENCY,
        progress_callback: ProgressCallback | None = None,
        track_update_callback: TrackUpdateCallback | None = None,
        priority_cache_key: str | None = None,
        max_downloads: int | None = None,
        stop_event: Event | None = None,
    ) -> list[Track]:
        """Download eligible tracks into ``downloads_dir`` and return updated tracks."""

        if concurrency < 1:
            raise ValueError("concurrency must be at least 1")

        downloads_dir.mkdir(parents=True, exist_ok=True)
        results: list[Track] = list(tracks)
        candidates = [
            (index, track)
            for index, track in enumerate(tracks)
            if _should_download(track)
        ]
        candidates = _prioritize_candidates(candidates, priority_cache_key)
        if max_downloads is not None:
            candidates = candidates[:max_downloads]
        _report(
            progress_callback,
            0,
            translate("DownloadManager", "Queued {count} downloads", count=len(candidates)),
        )
        if not candidates:
            return results

        completed_count = 0
        max_workers = min(concurrency, len(candidates))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for index, track in candidates:
                downloading_track = replace(track, status=TrackStatus.DOWNLOADING, error=None)
                results[index] = downloading_track
                _report_track_update(track_update_callback, downloading_track)
            future_to_index = {
                executor.submit(
                    self._download_track_with_retries,
                    results[index],
                    downloads_dir,
                    stop_event,
                ): index
                for index, _track in candidates
            }
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as error:  # noqa: BLE001 - isolate one failed download.
                    failed_track = results[index]
                    LOGGER.exception(
                        "Unexpected download failure for %s - %s",
                        failed_track.artist,
                        failed_track.title,
                    )
                    results[index] = replace(
                        failed_track,
                        status=TrackStatus.FAILED,
                        retry_count=failed_track.retry_count + 1,
                        error=str(error),
                    )
                _report_track_update(track_update_callback, results[index])
                completed_count += 1
                percent = int(completed_count / len(candidates) * 100)
                _report(
                    progress_callback,
                    percent,
                    translate(
                        "DownloadManager",
                        "Downloaded {done}/{total} tracks",
                        done=completed_count,
                        total=len(candidates),
                    ),
                )

        return results

    def _download_track_with_retries(
        self,
        track: Track,
        downloads_dir: Path,
        stop_event: Event | None = None,
    ) -> Track:
        current_track = replace(track, status=TrackStatus.DOWNLOADING, error=None)
        last_error: str | None = None

        for attempt in range(1, self.max_retries + 1):
            if stop_event is not None and stop_event.is_set():
                return replace(track, status=TrackStatus.QUEUED, error=None)
            try:
                local_path = self._download_track(
                    current_track, downloads_dir, attempt, stop_event
                )
                file_type, bitrate_kbps = _probe_audio_file(local_path, stop_event)
                return replace(
                    current_track,
                    local_path=str(local_path),
                    status=TrackStatus.DOWNLOADED,
                    error=None,
                    file_type=file_type,
                    bitrate_kbps=bitrate_kbps,
                )
            except DownloadError as error:
                last_error = str(error)
                current_track = current_track.increment_retry(last_error)
                LOGGER.warning(
                    "Download attempt %s/%s failed for %s - %s: %s",
                    attempt,
                    self.max_retries,
                    track.artist,
                    track.title,
                    last_error,
                )
                if attempt < self.max_retries:
                    self.sleeper(self.backoff_factory())
            except WorkCancelled:
                return replace(track, status=TrackStatus.QUEUED, error=None)

        return replace(current_track, status=TrackStatus.FAILED, error=last_error)

    def _download_track(
        self,
        track: Track,
        downloads_dir: Path,
        attempt: int = 1,
        stop_event: Event | None = None,
    ) -> Path:
        if not track.youtube_url:
            raise DownloadError("Track has no YouTube URL")

        output_template = str(downloads_dir / f"{track.audio_base_name}.%(ext)s")
        command = [self.executable, "-f", AUDIO_FORMAT_SELECTOR, "--no-playlist"]
        player_client = _player_client_for_attempt(attempt)
        if player_client:
            command += ["--extractor-args", f"youtube:player_client={player_client}"]
        if self.cookies_browser:
            command += ["--cookies-from-browser", self.cookies_browser]
        command += ["--output", output_template, track.youtube_url]
        completed = self._run(command, stop_event, track.cache_key)
        if completed.returncode != 0:
            raise DownloadError(completed.stderr.strip() or "yt-dlp download failed")

        candidates = sorted(
            [p for p in downloads_dir.iterdir() if p.stem == track.audio_base_name],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not candidates:
            raise DownloadError("Downloaded file not found after yt-dlp succeeded")
        return candidates[0]

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
                        raise WorkCancelled("YouTube download cancelled")
                    return run_cancellable_command(
                        command,
                        stop_event=stop_event,
                        timeout=DOWNLOAD_TIMEOUT_SECONDS,
                    )
            return self.command_runner(
                command,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=DOWNLOAD_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as error:
            raise DownloadError(
                f"{self.executable} download timed out after {DOWNLOAD_TIMEOUT_SECONDS}s"
            ) from error
        except OSError as error:
            raise DownloadError(f"Could not run {self.executable}: {error}") from error


def _player_client_for_attempt(attempt: int) -> str:
    """Return the YouTube player client to force on a one-based retry ``attempt``."""

    return PLAYER_CLIENT_LADDER[(attempt - 1) % len(PLAYER_CLIENT_LADDER)]


def _should_download(track: Track) -> bool:
    return bool(track.youtube_url) and track.status not in {
        TrackStatus.DOWNLOADED,
        TrackStatus.NOT_FOUND,
    }


def _prioritize_candidates(
    candidates: list[tuple[int, Track]],
    priority_cache_key: str | None,
) -> list[tuple[int, Track]]:
    if priority_cache_key is None:
        return candidates
    return sorted(candidates, key=lambda item: item[1].cache_key != priority_cache_key)


def _report(progress_callback: ProgressCallback | None, value: int, message: str) -> None:
    LOGGER.info("Download progress %s%%: %s", value, message)
    if progress_callback is not None:
        progress_callback(value, message)


def _report_track_update(
    track_update_callback: TrackUpdateCallback | None,
    track: Track,
) -> None:
    if track_update_callback is not None:
        track_update_callback(track)


def _probe_audio_file(
    path: Path, stop_event: Event | None = None
) -> tuple[str | None, int | None]:
    file_type = _file_type_from_path(path)
    try:
        command = [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=format_name,bit_rate",
                "-of",
                "json",
                str(path),
            ]
        if stop_event is None:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=PROBE_TIMEOUT_SECONDS,
            )
        else:
            completed = run_cancellable_command(
                command, stop_event=stop_event, timeout=PROBE_TIMEOUT_SECONDS
            )
    except (OSError, subprocess.TimeoutExpired, WorkCancelled):
        return file_type, None

    if completed.returncode != 0:
        return file_type, None

    try:
        data = json.loads(completed.stdout or "{}")
    except json.JSONDecodeError:
        return file_type, None

    format_data = data.get("format")
    if not isinstance(format_data, dict):
        return file_type, None

    probed_type = _format_name_to_file_type(format_data.get("format_name")) or file_type
    return probed_type, _bit_rate_to_kbps(format_data.get("bit_rate"))


def _file_type_from_path(path: Path) -> str | None:
    suffix = path.suffix.lstrip(".")
    return suffix.upper() if suffix else None


def _format_name_to_file_type(value: object) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    formats = [item.strip().lower() for item in value.split(",") if item.strip()]
    for preferred_format in ("mp3", "m4a", "webm", "opus", "ogg", "flac", "wav"):
        if preferred_format in formats:
            return preferred_format.upper()
    first_format = formats[0] if formats else ""
    return first_format.upper() if first_format else None


def _bit_rate_to_kbps(value: object) -> int | None:
    try:
        bits_per_second = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    if bits_per_second <= 0:
        return None
    return round(bits_per_second / 1000)

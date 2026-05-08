from __future__ import annotations

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

LOGGER = logging.getLogger(__name__)

DEFAULT_CONCURRENCY = 2
MAX_RETRIES = 3
BACKOFF_RANGE_SECONDS = (1.0, 5.0)

CommandRunner = Callable[..., subprocess.CompletedProcess[str]]
Sleeper = Callable[[float], None]
BackoffFactory = Callable[[], float]
ProgressCallback = Callable[[int, str], None]
TrackUpdateCallback = Callable[[Track], None]


class DownloadError(RuntimeError):
    """Raised when a track cannot be downloaded."""


class DownloadManager:
    """Download resolved tracks with retry, pause/resume, and progress reporting."""

    def __init__(
        self,
        command_runner: CommandRunner = subprocess.run,
        executable: str = "yt-dlp",
        max_retries: int = MAX_RETRIES,
        backoff_factory: BackoffFactory | None = None,
        sleeper: Sleeper = time.sleep,
    ) -> None:
        self.command_runner = command_runner
        self.executable = executable
        self.max_retries = max_retries
        self.backoff_factory = backoff_factory or (
            lambda: random.uniform(*BACKOFF_RANGE_SECONDS)
        )
        self.sleeper = sleeper
        self._resume_event = Event()
        self._resume_event.set()

    def pause(self) -> None:
        """Pause the queue before the next retry or download starts."""

        LOGGER.info("Download queue paused")
        self._resume_event.clear()

    def resume(self) -> None:
        """Resume a paused queue."""

        LOGGER.info("Download queue resumed")
        self._resume_event.set()

    def download_and_store_tracks(
        self,
        username: str,
        repository: JsonTrackRepository,
        concurrency: int = DEFAULT_CONCURRENCY,
        progress_callback: ProgressCallback | None = None,
        track_update_callback: TrackUpdateCallback | None = None,
        priority_cache_key: str | None = None,
        max_downloads: int | None = None,
    ) -> list[Track]:
        """Load tracks, download eligible items, and persist results."""

        tracks = repository.mark_cached_downloads(repository.load_tracks(username))
        downloaded_tracks = self.download_tracks(
            tracks,
            repository.downloads_dir,
            concurrency=concurrency,
            progress_callback=progress_callback,
            track_update_callback=track_update_callback,
            priority_cache_key=priority_cache_key,
            max_downloads=max_downloads,
        )
        repository.save_tracks(username, downloaded_tracks)
        repository.save_download_cache(downloaded_tracks)
        return downloaded_tracks

    def download_tracks(
        self,
        tracks: list[Track],
        downloads_dir: Path,
        concurrency: int = DEFAULT_CONCURRENCY,
        progress_callback: ProgressCallback | None = None,
        track_update_callback: TrackUpdateCallback | None = None,
        priority_cache_key: str | None = None,
        max_downloads: int | None = None,
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
                ): index
                for index, _track in candidates
            }
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                results[index] = future.result()
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

    def _download_track_with_retries(self, track: Track, downloads_dir: Path) -> Track:
        current_track = replace(track, status=TrackStatus.DOWNLOADING, error=None)
        last_error: str | None = None

        for attempt in range(1, self.max_retries + 1):
            self._resume_event.wait()
            try:
                local_path = self._download_track(current_track, downloads_dir)
                return replace(
                    current_track,
                    local_path=str(local_path),
                    status=TrackStatus.DOWNLOADED,
                    error=None,
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

        return replace(current_track, status=TrackStatus.FAILED, error=last_error)

    def _download_track(self, track: Track, downloads_dir: Path) -> Path:
        if not track.youtube_url:
            raise DownloadError("Track has no YouTube URL")

        output_template = str(downloads_dir / f"{track.audio_base_name}.%(ext)s")
        command = [
            self.executable,
            "-f",
            "bestaudio",
            "--no-playlist",
            "--output",
            output_template,
            track.youtube_url,
        ]
        completed = self._run(command)
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

    def _run(self, command: Sequence[str]) -> subprocess.CompletedProcess[str]:
        try:
            return self.command_runner(
                command,
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError as error:
            raise DownloadError(f"Could not run {self.executable}: {error}") from error


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
    print(f"[myLastFmPlayer] Download progress {value}%: {message}", flush=True)
    if progress_callback is not None:
        progress_callback(value, message)


def _report_track_update(
    track_update_callback: TrackUpdateCallback | None,
    track: Track,
) -> None:
    if track_update_callback is not None:
        track_update_callback(track)

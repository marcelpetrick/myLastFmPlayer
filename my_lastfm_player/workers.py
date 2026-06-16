from __future__ import annotations

import logging
import time
from threading import Event

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from my_lastfm_player.download import DEFAULT_CONCURRENCY, DownloadManager
from my_lastfm_player.i18n import translate
from my_lastfm_player.lastfm import FetchProgress, LastFmArtistInfoClient, LastFmLovedTracksScraper
from my_lastfm_player.storage import JsonTrackRepository
from my_lastfm_player.youtube import YouTubeResolver

LOGGER = logging.getLogger(__name__)


class ArtistImageWorker(QObject):
    """Qt worker that fetches Last.fm artist image metadata in the background."""

    artist_image_loaded = pyqtSignal(object)
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, artist: str, client: LastFmArtistInfoClient) -> None:
        super().__init__()
        self.artist = artist
        self.client = client

    @pyqtSlot()
    def run(self) -> None:
        """Fetch artist image information and emit the result."""

        try:
            LOGGER.info("Worker started fetching artist image for %s", self.artist)
            self.artist_image_loaded.emit(self.client.fetch_artist_image(self.artist))
        except Exception as error:  # noqa: BLE001 - worker boundary must report all failures.
            LOGGER.exception("Artist image fetch failed for %s", self.artist)
            self.error.emit(str(error))
        finally:
            LOGGER.info("Worker finished fetching artist image for %s", self.artist)
            self.finished.emit()


class FetchLovedTracksWorker(QObject):
    """Qt worker that fetches Last.fm loved tracks on a background thread."""

    tracks_loaded = pyqtSignal(str, object)
    tracks_updated = pyqtSignal(str, object)
    fetch_stopped = pyqtSignal(str, object)
    progress = pyqtSignal(int, str)
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(
        self,
        username: str,
        scraper: LastFmLovedTracksScraper,
        repository: JsonTrackRepository,
        expected_count: int | None = None,
    ) -> None:
        super().__init__()
        self.username = username
        self.scraper = scraper
        self.repository = repository
        self.expected_count = expected_count
        self._resume_event = Event()
        self._resume_event.set()
        self._stop_requested = False

    @pyqtSlot()
    def run(self) -> None:
        """Execute the fetch workflow and emit progress, track, and completion signals."""

        try:
            LOGGER.info("Worker started fetching loved tracks for %s", self.username)
            self.progress.emit(
                0,
                translate(
                    "FetchLovedTracksWorker",
                    "Looking up Last.fm user {username}",
                    username=self.username,
                ),
            )
            tracks = self.scraper.fetch_and_store_loved_tracks(
                self.username,
                self.repository,
                progress_callback=self._report_fetch_progress,
                tracks_callback=self._report_partial_tracks,
                control_callback=self._can_continue_fetching,
            )
            if self._stop_requested:
                self.progress.emit(
                    0,
                    translate(
                        "FetchLovedTracksWorker",
                        "Stopped fetch after {count} tracks",
                        count=len(tracks),
                    ),
                )
                self.fetch_stopped.emit(self.username, tracks)
            else:
                self.progress.emit(
                    100,
                    translate(
                        "FetchLovedTracksWorker",
                        "Fetched {count} tracks",
                        count=len(tracks),
                    ),
                )
                self.tracks_loaded.emit(self.username, tracks)
        except Exception as error:  # noqa: BLE001 - worker boundary must report all failures.
            LOGGER.exception("Loved-track fetch failed for %s", self.username)
            self.error.emit(str(error))
        finally:
            LOGGER.info("Worker finished fetching loved tracks for %s", self.username)
            self.finished.emit()

    def _report_fetch_progress(self, progress: FetchProgress) -> None:
        total = progress.total_count or self.expected_count
        percent = min(99, int(progress.fetched_count / total * 100)) if total else 0
        LOGGER.info("Worker progress for %s: %s%% %s", self.username, percent, progress.message)
        self.progress.emit(percent, progress.message)

    def _report_partial_tracks(self, tracks: list[object]) -> None:
        LOGGER.info("Worker partial fetch for %s: %d tracks", self.username, len(tracks))
        self.tracks_updated.emit(self.username, tracks)

    def pause_fetch(self) -> None:
        """Pause pagination before the next cooperative fetch checkpoint."""

        self._resume_event.clear()

    def resume_fetch(self) -> None:
        """Resume a paused fetch."""

        self._resume_event.set()

    def stop_fetch(self) -> None:
        """Request fetch cancellation and resume the worker if it is paused."""

        self._stop_requested = True
        self._resume_event.set()

    def _can_continue_fetching(self) -> bool:
        while not self._stop_requested and not self._resume_event.is_set():
            time.sleep(0.05)
        return not self._stop_requested


class LookupTracksWorker(QObject):
    """Qt worker that resolves stored tracks to YouTube URLs."""

    tracks_resolved = pyqtSignal(str, object)
    track_updated = pyqtSignal(str, object)
    progress = pyqtSignal(int, str)
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(
        self,
        username: str,
        resolver: YouTubeResolver,
        repository: JsonTrackRepository,
        priority_cache_key: str | None = None,
        max_tracks: int | None = None,
    ) -> None:
        super().__init__()
        self.username = username
        self.resolver = resolver
        self.repository = repository
        self.priority_cache_key = priority_cache_key
        self.max_tracks = max_tracks

    @pyqtSlot()
    def run(self) -> None:
        """Execute YouTube lookup and emit per-track and final-result signals."""

        try:
            LOGGER.info("Worker started resolving YouTube URLs for %s", self.username)
            self.progress.emit(
                0,
                translate(
                    "LookupTracksWorker",
                    "Resolving YouTube URLs for {username}",
                    username=self.username,
                ),
            )
            tracks = self.resolver.resolve_and_store_tracks(
                self.username,
                self.repository,
                progress_callback=self.progress.emit,
                track_update_callback=self._report_track_update,
                priority_cache_key=self.priority_cache_key,
                max_tracks=self.max_tracks,
            )
            self.progress.emit(
                100,
                translate(
                    "LookupTracksWorker",
                    "Resolved {count} tracks",
                    count=len(tracks),
                ),
            )
            self.tracks_resolved.emit(self.username, tracks)
        except Exception as error:  # noqa: BLE001 - worker boundary must report all failures.
            LOGGER.exception("YouTube lookup failed for %s", self.username)
            self.error.emit(str(error))
        finally:
            LOGGER.info("Worker finished resolving YouTube URLs for %s", self.username)
            self.finished.emit()

    def _report_track_update(self, track: object) -> None:
        self.track_updated.emit(self.username, track)


class DownloadTracksWorker(QObject):
    """Qt worker that downloads resolved tracks on a background thread."""

    tracks_downloaded = pyqtSignal(str, object)
    track_updated = pyqtSignal(str, object)
    progress = pyqtSignal(int, str)
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(  # pylint: disable=too-many-arguments
        self,
        username: str,
        download_manager: DownloadManager,
        repository: JsonTrackRepository,
        concurrency: int = DEFAULT_CONCURRENCY,
        priority_cache_key: str | None = None,
        max_downloads: int | None = None,
    ) -> None:
        super().__init__()
        self.username = username
        self.download_manager = download_manager
        self.repository = repository
        self.concurrency = concurrency
        self.priority_cache_key = priority_cache_key
        self.max_downloads = max_downloads

    @pyqtSlot()
    def run(self) -> None:
        """Execute downloads and emit progress, per-track updates, and final results."""

        try:
            LOGGER.info("Worker started downloading tracks for %s", self.username)
            tracks = self.download_manager.download_and_store_tracks(
                self.username,
                self.repository,
                concurrency=self.concurrency,
                progress_callback=self.progress.emit,
                track_update_callback=self._report_track_update,
                priority_cache_key=self.priority_cache_key,
                max_downloads=self.max_downloads,
            )
            self.tracks_downloaded.emit(self.username, tracks)
        except Exception as error:  # noqa: BLE001 - worker boundary must report all failures.
            LOGGER.exception("Download failed for %s", self.username)
            self.error.emit(str(error))
        finally:
            LOGGER.info("Worker finished downloading tracks for %s", self.username)
            self.finished.emit()

    def _report_track_update(self, track: object) -> None:
        self.track_updated.emit(self.username, track)

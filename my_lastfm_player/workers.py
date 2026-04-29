from __future__ import annotations

import logging

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from my_lastfm_player.download import DEFAULT_CONCURRENCY, DownloadManager
from my_lastfm_player.lastfm import FetchProgress, LastFmLovedTracksScraper
from my_lastfm_player.storage import JsonTrackRepository
from my_lastfm_player.youtube import YouTubeResolver

LOGGER = logging.getLogger(__name__)


class FetchLovedTracksWorker(QObject):
    tracks_loaded = pyqtSignal(str, object)
    progress = pyqtSignal(int, str)
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(
        self,
        username: str,
        scraper: LastFmLovedTracksScraper,
        repository: JsonTrackRepository,
    ) -> None:
        super().__init__()
        self.username = username
        self.scraper = scraper
        self.repository = repository

    @pyqtSlot()
    def run(self) -> None:
        try:
            LOGGER.info("Worker started fetching loved tracks for %s", self.username)
            print(
                f"[myLastFmPlayer] Worker started fetching loved tracks for {self.username}",
                flush=True,
            )
            self.progress.emit(0, f"Looking up Last.fm user {self.username}")
            tracks = self.scraper.fetch_and_store_loved_tracks(
                self.username,
                self.repository,
                progress_callback=self._report_fetch_progress,
            )
            self.progress.emit(100, f"Fetched {len(tracks)} tracks")
            self.tracks_loaded.emit(self.username, tracks)
        except Exception as error:  # noqa: BLE001 - worker boundary must report all failures.
            LOGGER.exception("Loved-track fetch failed for %s", self.username)
            print(
                f"[myLastFmPlayer] Loved-track fetch failed for {self.username}: {error}",
                flush=True,
            )
            self.error.emit(str(error))
        finally:
            LOGGER.info("Worker finished fetching loved tracks for %s", self.username)
            print(
                f"[myLastFmPlayer] Worker finished fetching loved tracks for {self.username}",
                flush=True,
            )
            self.finished.emit()

    def _report_fetch_progress(self, progress: FetchProgress) -> None:
        if progress.total_count:
            percent = min(99, int(progress.fetched_count / progress.total_count * 100))
        else:
            percent = 0
        print(
            f"[myLastFmPlayer] Worker progress for {self.username}: "
            f"{percent}% {progress.message}",
            flush=True,
        )
        self.progress.emit(percent, progress.message)


class LookupTracksWorker(QObject):
    tracks_resolved = pyqtSignal(str, object)
    progress = pyqtSignal(int, str)
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(
        self,
        username: str,
        resolver: YouTubeResolver,
        repository: JsonTrackRepository,
    ) -> None:
        super().__init__()
        self.username = username
        self.resolver = resolver
        self.repository = repository

    @pyqtSlot()
    def run(self) -> None:
        try:
            LOGGER.info("Worker started resolving YouTube URLs for %s", self.username)
            self.progress.emit(0, f"Resolving YouTube URLs for {self.username}")
            tracks = self.resolver.resolve_and_store_tracks(self.username, self.repository)
            self.progress.emit(100, f"Resolved {len(tracks)} tracks")
            self.tracks_resolved.emit(self.username, tracks)
        except Exception as error:  # noqa: BLE001 - worker boundary must report all failures.
            LOGGER.exception("YouTube lookup failed for %s", self.username)
            self.error.emit(str(error))
        finally:
            LOGGER.info("Worker finished resolving YouTube URLs for %s", self.username)
            self.finished.emit()


class DownloadTracksWorker(QObject):
    tracks_downloaded = pyqtSignal(str, object)
    progress = pyqtSignal(int, str)
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(
        self,
        username: str,
        download_manager: DownloadManager,
        repository: JsonTrackRepository,
        concurrency: int = DEFAULT_CONCURRENCY,
    ) -> None:
        super().__init__()
        self.username = username
        self.download_manager = download_manager
        self.repository = repository
        self.concurrency = concurrency

    @pyqtSlot()
    def run(self) -> None:
        try:
            LOGGER.info("Worker started downloading tracks for %s", self.username)
            print(
                f"[myLastFmPlayer] Worker started downloading tracks for {self.username}",
                flush=True,
            )
            tracks = self.download_manager.download_and_store_tracks(
                self.username,
                self.repository,
                concurrency=self.concurrency,
                progress_callback=self.progress.emit,
            )
            self.tracks_downloaded.emit(self.username, tracks)
        except Exception as error:  # noqa: BLE001 - worker boundary must report all failures.
            LOGGER.exception("Download failed for %s", self.username)
            print(f"[myLastFmPlayer] Download failed for {self.username}: {error}", flush=True)
            self.error.emit(str(error))
        finally:
            LOGGER.info("Worker finished downloading tracks for %s", self.username)
            print(
                f"[myLastFmPlayer] Worker finished downloading tracks for {self.username}",
                flush=True,
            )
            self.finished.emit()

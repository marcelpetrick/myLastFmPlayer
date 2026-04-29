from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from my_lastfm_player.lastfm import LastFmLovedTracksScraper
from my_lastfm_player.storage import JsonTrackRepository
from my_lastfm_player.youtube import YouTubeResolver


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
            self.progress.emit(0, f"Fetching loved tracks for {self.username}")
            tracks = self.scraper.fetch_and_store_loved_tracks(self.username, self.repository)
            self.progress.emit(100, f"Fetched {len(tracks)} tracks")
            self.tracks_loaded.emit(self.username, tracks)
        except Exception as error:  # noqa: BLE001 - worker boundary must report all failures.
            self.error.emit(str(error))
        finally:
            self.finished.emit()


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
            self.progress.emit(0, f"Resolving YouTube URLs for {self.username}")
            tracks = self.resolver.resolve_and_store_tracks(self.username, self.repository)
            self.progress.emit(100, f"Resolved {len(tracks)} tracks")
            self.tracks_resolved.emit(self.username, tracks)
        except Exception as error:  # noqa: BLE001 - worker boundary must report all failures.
            self.error.emit(str(error))
        finally:
            self.finished.emit()


class DownloadPlaceholderWorker(QObject):
    progress = pyqtSignal(int, str)
    error = pyqtSignal(str)
    finished = pyqtSignal()

    @pyqtSlot()
    def run(self) -> None:
        self.progress.emit(0, "Download worker is not implemented yet")
        self.finished.emit()

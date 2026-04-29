from __future__ import annotations

import logging
from collections.abc import Callable

from PyQt6.QtCore import QObject, QThread

from my_lastfm_player.dependencies import DependencyCheckResult, check_external_dependencies
from my_lastfm_player.download import DownloadManager
from my_lastfm_player.lastfm import LastFmLovedTracksScraper
from my_lastfm_player.storage import JsonTrackRepository
from my_lastfm_player.ui.main_window import MainWindow
from my_lastfm_player.workers import (
    DownloadTracksWorker,
    FetchLovedTracksWorker,
    LookupTracksWorker,
)
from my_lastfm_player.youtube import YouTubeResolver

LOGGER = logging.getLogger(__name__)

DependencyChecker = Callable[[], DependencyCheckResult]
FetchWorkerFactory = Callable[
    [str, LastFmLovedTracksScraper, JsonTrackRepository],
    FetchLovedTracksWorker,
]
LookupWorkerFactory = Callable[
    [str, YouTubeResolver, JsonTrackRepository],
    LookupTracksWorker,
]
DownloadWorkerFactory = Callable[
    [str, DownloadManager, JsonTrackRepository, int],
    DownloadTracksWorker,
]
WorkflowWorker = FetchLovedTracksWorker | LookupTracksWorker | DownloadTracksWorker


class ApplicationController(QObject):
    def __init__(
        self,
        window: MainWindow,
        repository: JsonTrackRepository | None = None,
        scraper: LastFmLovedTracksScraper | None = None,
        youtube_resolver: YouTubeResolver | None = None,
        download_manager: DownloadManager | None = None,
        dependency_checker: DependencyChecker = check_external_dependencies,
        fetch_worker_factory: FetchWorkerFactory = FetchLovedTracksWorker,
        lookup_worker_factory: LookupWorkerFactory = LookupTracksWorker,
        download_worker_factory: DownloadWorkerFactory = DownloadTracksWorker,
    ) -> None:
        super().__init__(window)
        self.window = window
        self.repository = repository or JsonTrackRepository()
        self.scraper = scraper or LastFmLovedTracksScraper()
        self.youtube_resolver = youtube_resolver or YouTubeResolver()
        self.download_manager = download_manager or DownloadManager()
        self.dependency_checker = dependency_checker
        self.fetch_worker_factory = fetch_worker_factory
        self.lookup_worker_factory = lookup_worker_factory
        self.download_worker_factory = download_worker_factory
        self._active_threads: list[QThread] = []
        self._active_workers: list[WorkflowWorker] = []

    def start(self) -> None:
        LOGGER.info("Starting application controller")
        print("[myLastFmPlayer] Starting application controller", flush=True)
        self.window.fetch_requested.connect(self.fetch_loved_tracks)
        self.window.download_requested.connect(self.download_tracks)
        self.check_dependencies()

    def check_dependencies(self) -> DependencyCheckResult:
        result = self.dependency_checker()
        LOGGER.info(
            "Dependency check result: installed=%s missing=%s",
            result.installed,
            result.missing,
        )
        self.window.set_dependency_status(result.is_ok, result.user_message())
        if not result.is_ok:
            self.window.append_feedback(result.user_message())
        return result

    def fetch_loved_tracks(self) -> None:
        username = self.window.username()
        if not username:
            LOGGER.warning("Fetch requested without a Last.fm username")
            self.window.append_feedback("Enter a Last.fm username before fetching tracks.")
            return

        LOGGER.info("Fetch requested for Last.fm user %s", username)
        print(f"[myLastFmPlayer] UI fetch requested for Last.fm user {username}", flush=True)
        self.window.set_fetch_enabled(False)
        self.window.set_progress(0, "Starting fetch")
        worker = self.fetch_worker_factory(username, self.scraper, self.repository)
        self._run_worker(worker)

    def resolve_youtube_urls(self) -> None:
        username = self.window.username()
        if not username:
            LOGGER.warning("Lookup requested without a Last.fm username")
            self.window.append_feedback("Enter a Last.fm username before resolving tracks.")
            return

        LOGGER.info("YouTube lookup requested for Last.fm user %s", username)
        self.window.set_progress(0, "Starting YouTube lookup")
        worker = self.lookup_worker_factory(username, self.youtube_resolver, self.repository)
        self._run_worker(worker)

    def download_tracks(self) -> None:
        username = self.window.username()
        if not username:
            LOGGER.warning("Download requested without a Last.fm username")
            self.window.append_feedback("Enter a Last.fm username before downloading tracks.")
            return

        concurrency = self.window.concurrency_input.value()
        LOGGER.info(
            "Download requested for Last.fm user %s with concurrency %s",
            username,
            concurrency,
        )
        self.window.set_progress(0, "Starting downloads")
        worker = self.download_worker_factory(
            username,
            self.download_manager,
            self.repository,
            concurrency,
        )
        self._run_worker(worker)

    def _run_worker(self, worker: WorkflowWorker) -> None:
        thread = QThread(self)
        worker_name = worker.__class__.__name__
        print(f"[myLastFmPlayer] Preparing {worker_name} on background thread", flush=True)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        thread.started.connect(
            lambda worker_name=worker_name: print(
                f"[myLastFmPlayer] Thread started for {worker_name}",
                flush=True,
            )
        )
        worker.progress.connect(self.window.set_progress)
        worker.error.connect(self._handle_worker_error)
        if isinstance(worker, FetchLovedTracksWorker):
            worker.tracks_loaded.connect(self._handle_tracks_loaded)
        if isinstance(worker, LookupTracksWorker):
            worker.tracks_resolved.connect(self._handle_tracks_resolved)
        if isinstance(worker, DownloadTracksWorker):
            worker.tracks_downloaded.connect(self._handle_tracks_downloaded)
        worker.finished.connect(lambda: self.window.set_fetch_enabled(True))
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda: self._forget_thread(thread))
        thread.finished.connect(lambda worker=worker: self._forget_worker(worker))

        self._active_threads.append(thread)
        self._active_workers.append(worker)
        LOGGER.info("Starting worker thread for %s", worker_name)
        print(
            f"[myLastFmPlayer] Starting thread for {worker_name}; "
            f"active_threads={len(self._active_threads)} "
            f"active_workers={len(self._active_workers)}",
            flush=True,
        )
        thread.start()

    def _handle_tracks_loaded(self, username: str, tracks: object) -> None:
        if not isinstance(tracks, list):
            self.window.append_feedback(f"Fetch for {username} returned invalid track data.")
            return

        self.window.set_tracks(tracks)
        self.window.append_feedback(f"Fetched and stored {len(tracks)} tracks for {username}.")
        LOGGER.info("Loaded %s fetched tracks into UI for %s", len(tracks), username)
        print(
            f"[myLastFmPlayer] UI loaded {len(tracks)} fetched tracks for {username}",
            flush=True,
        )

    def _handle_tracks_resolved(self, username: str, tracks: object) -> None:
        if not isinstance(tracks, list):
            self.window.append_feedback(f"Lookup for {username} returned invalid track data.")
            return

        self.window.set_tracks(tracks)
        self.window.append_feedback(f"Resolved YouTube URLs for {len(tracks)} tracks.")
        LOGGER.info("Loaded %s resolved tracks into UI for %s", len(tracks), username)

    def _handle_tracks_downloaded(self, username: str, tracks: object) -> None:
        if not isinstance(tracks, list):
            self.window.append_feedback(f"Download for {username} returned invalid track data.")
            return

        self.window.set_tracks(tracks)
        self.window.append_feedback(f"Downloaded {len(tracks)} tracks for {username}.")
        LOGGER.info("Loaded %s downloaded tracks into UI for %s", len(tracks), username)

    def _handle_worker_error(self, message: str) -> None:
        LOGGER.error("Worker error: %s", message)
        print(f"[myLastFmPlayer] Worker error shown in UI: {message}", flush=True)
        self.window.append_feedback(message)
        self.window.set_progress(0, "Failed")

    def _forget_thread(self, thread: QThread) -> None:
        if thread in self._active_threads:
            self._active_threads.remove(thread)
        print(
            f"[myLastFmPlayer] Thread finished; active_threads={len(self._active_threads)}",
            flush=True,
        )

    def _forget_worker(self, worker: WorkflowWorker) -> None:
        if worker in self._active_workers:
            self._active_workers.remove(worker)
        print(
            f"[myLastFmPlayer] Worker released; active_workers={len(self._active_workers)}",
            flush=True,
        )

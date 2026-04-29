from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtCore import QObject, QThread

from my_lastfm_player.dependencies import DependencyCheckResult, check_external_dependencies
from my_lastfm_player.lastfm import LastFmLovedTracksScraper
from my_lastfm_player.storage import JsonTrackRepository
from my_lastfm_player.ui.main_window import MainWindow
from my_lastfm_player.workers import FetchLovedTracksWorker, LookupTracksWorker
from my_lastfm_player.youtube import YouTubeResolver

DependencyChecker = Callable[[], DependencyCheckResult]
FetchWorkerFactory = Callable[
    [str, LastFmLovedTracksScraper, JsonTrackRepository],
    FetchLovedTracksWorker,
]
LookupWorkerFactory = Callable[
    [str, YouTubeResolver, JsonTrackRepository],
    LookupTracksWorker,
]


class ApplicationController(QObject):
    def __init__(
        self,
        window: MainWindow,
        repository: JsonTrackRepository | None = None,
        scraper: LastFmLovedTracksScraper | None = None,
        youtube_resolver: YouTubeResolver | None = None,
        dependency_checker: DependencyChecker = check_external_dependencies,
        fetch_worker_factory: FetchWorkerFactory = FetchLovedTracksWorker,
        lookup_worker_factory: LookupWorkerFactory = LookupTracksWorker,
    ) -> None:
        super().__init__(window)
        self.window = window
        self.repository = repository or JsonTrackRepository()
        self.scraper = scraper or LastFmLovedTracksScraper()
        self.youtube_resolver = youtube_resolver or YouTubeResolver()
        self.dependency_checker = dependency_checker
        self.fetch_worker_factory = fetch_worker_factory
        self.lookup_worker_factory = lookup_worker_factory
        self._active_threads: list[QThread] = []

    def start(self) -> None:
        self.window.fetch_requested.connect(self.fetch_loved_tracks)
        self.check_dependencies()

    def check_dependencies(self) -> DependencyCheckResult:
        result = self.dependency_checker()
        self.window.set_dependency_status(result.is_ok, result.user_message())
        if not result.is_ok:
            self.window.append_feedback(result.user_message())
        return result

    def fetch_loved_tracks(self) -> None:
        username = self.window.username()
        if not username:
            self.window.append_feedback("Enter a Last.fm username before fetching tracks.")
            return

        self.window.set_fetch_enabled(False)
        self.window.set_progress(0, "Starting fetch")
        worker = self.fetch_worker_factory(username, self.scraper, self.repository)
        self._run_worker(worker)

    def resolve_youtube_urls(self) -> None:
        username = self.window.username()
        if not username:
            self.window.append_feedback("Enter a Last.fm username before resolving tracks.")
            return

        self.window.set_progress(0, "Starting YouTube lookup")
        worker = self.lookup_worker_factory(username, self.youtube_resolver, self.repository)
        self._run_worker(worker)

    def _run_worker(self, worker: FetchLovedTracksWorker | LookupTracksWorker) -> None:
        thread = QThread(self)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.progress.connect(self.window.set_progress)
        worker.error.connect(self._handle_worker_error)
        if isinstance(worker, FetchLovedTracksWorker):
            worker.tracks_loaded.connect(self._handle_tracks_loaded)
        if isinstance(worker, LookupTracksWorker):
            worker.tracks_resolved.connect(self._handle_tracks_resolved)
        worker.finished.connect(lambda: self.window.set_fetch_enabled(True))
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda: self._forget_thread(thread))

        self._active_threads.append(thread)
        thread.start()

    def _handle_tracks_loaded(self, username: str, tracks: object) -> None:
        if not isinstance(tracks, list):
            self.window.append_feedback(f"Fetch for {username} returned invalid track data.")
            return

        self.window.set_tracks(tracks)
        self.window.append_feedback(f"Fetched and stored {len(tracks)} tracks for {username}.")

    def _handle_tracks_resolved(self, username: str, tracks: object) -> None:
        if not isinstance(tracks, list):
            self.window.append_feedback(f"Lookup for {username} returned invalid track data.")
            return

        self.window.set_tracks(tracks)
        self.window.append_feedback(f"Resolved YouTube URLs for {len(tracks)} tracks.")

    def _handle_worker_error(self, message: str) -> None:
        self.window.append_feedback(message)
        self.window.set_progress(0, "Failed")

    def _forget_thread(self, thread: QThread) -> None:
        if thread in self._active_threads:
            self._active_threads.remove(thread)

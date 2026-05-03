from __future__ import annotations

import logging
from collections.abc import Callable

from PyQt6.QtCore import QObject, QThread

from my_lastfm_player.dependencies import DependencyCheckResult, check_external_dependencies
from my_lastfm_player.download import DownloadManager
from my_lastfm_player.i18n import translate
from my_lastfm_player.lastfm import LastFmLovedTracksScraper
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.playback import PlaybackError, PlaybackService
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
    [str, YouTubeResolver, JsonTrackRepository, str | None, int | None],
    LookupTracksWorker,
]
DownloadWorkerFactory = Callable[
    [str, DownloadManager, JsonTrackRepository, int, str | None, int | None],
    DownloadTracksWorker,
]
WorkflowWorker = FetchLovedTracksWorker | LookupTracksWorker | DownloadTracksWorker


class ApplicationController(QObject):
    """Coordinate UI events, background workers, persistence, and playback."""

    def __init__(
        self,
        window: MainWindow,
        repository: JsonTrackRepository | None = None,
        scraper: LastFmLovedTracksScraper | None = None,
        youtube_resolver: YouTubeResolver | None = None,
        download_manager: DownloadManager | None = None,
        playback_service: PlaybackService | None = None,
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
        self._playback_service = playback_service
        self.dependency_checker = dependency_checker
        self.fetch_worker_factory = fetch_worker_factory
        self.lookup_worker_factory = lookup_worker_factory
        self.download_worker_factory = download_worker_factory
        self._active_threads: list[QThread] = []
        self._active_workers: list[WorkflowWorker] = []
        self._running_worker_count = 0
        self._pending_play_cache_key: str | None = None
        self._active_fetch_worker: FetchLovedTracksWorker | None = None
        self._fetch_paused = False
        self._playback_callbacks_connected = False

    @property
    def playback_service(self) -> PlaybackService:
        """Return the playback service, creating the Qt backend only when needed."""

        if self._playback_service is None:
            self._playback_service = PlaybackService()
        self._connect_playback_callbacks()
        return self._playback_service

    def start(self) -> None:
        """Connect UI signals and run the startup dependency check."""

        LOGGER.info("Starting application controller")
        print("[myLastFmPlayer] Starting application controller", flush=True)
        self.window.fetch_requested.connect(self.fetch_loved_tracks)
        self.window.username_input.editingFinished.connect(
            self.load_cached_tracks_for_entered_username
        )
        self.window.fetch_pause_requested.connect(self.toggle_fetch_pause)
        self.window.fetch_stop_requested.connect(self.stop_fetch)
        self.window.download_requested.connect(self.download_tracks)
        self.window.play_requested.connect(self.play_selected_track)
        self.window.pause_requested.connect(self.pause_playback)
        self.window.stop_requested.connect(self.stop_playback)
        self.window.seek_requested.connect(self.seek_playback)
        self.check_dependencies()

    def load_cached_tracks_for_entered_username(self) -> bool:
        """Load locally stored tracks for the entered username when available."""

        username = self.window.username()
        if not username:
            return False

        tracks = self.repository.load_tracks(username)
        if not tracks:
            return False

        tracks = self.repository.mark_cached_downloads(
            self.repository.mark_cached_lookups(tracks)
        )
        self.repository.save_tracks(username, tracks)
        self.window.set_tracks(tracks)
        self.window.append_feedback(
            translate(
                "ApplicationController",
                "Loaded {count} cached tracks for {username}; skipped Last.fm fetch.",
                count=len(tracks),
                username=username,
            )
        )
        return True

    def check_dependencies(self) -> DependencyCheckResult:
        """Check external tools and update dependency status in the window."""

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
        """Start fetching loved tracks for the username entered in the UI."""

        username = self.window.username()
        if not username:
            LOGGER.warning("Fetch requested without a Last.fm username")
            self.window.append_feedback(
                translate(
                    "ApplicationController",
                    "Enter a Last.fm username before fetching tracks.",
                )
            )
            return

        if self.load_cached_tracks_for_entered_username():
            self.window.set_fetch_control_state(active=False, paused=False)
            self.window.set_progress(
                100,
                translate("ApplicationController", "Loaded cached tracks"),
            )
            return

        LOGGER.info("Fetch requested for Last.fm user %s", username)
        print(f"[myLastFmPlayer] UI fetch requested for Last.fm user {username}", flush=True)
        self.window.set_workflow_enabled(False)
        self.window.set_fetch_control_state(active=True, paused=False)
        self._fetch_paused = False
        self.window.set_progress(0, translate("ApplicationController", "Starting fetch"))
        worker = self.fetch_worker_factory(username, self.scraper, self.repository)
        self._active_fetch_worker = worker
        self._run_worker(worker)

    def toggle_fetch_pause(self) -> None:
        """Pause or resume the active Last.fm fetch worker."""

        if self._active_fetch_worker is None:
            return
        if self._fetch_paused:
            self._active_fetch_worker.resume_fetch()
            self._fetch_paused = False
            self.window.set_fetch_control_state(active=True, paused=False)
            self.window.append_feedback(translate("ApplicationController", "Fetch resumed."))
            return
        self._active_fetch_worker.pause_fetch()
        self._fetch_paused = True
        self.window.set_fetch_control_state(active=True, paused=True)
        self.window.append_feedback(translate("ApplicationController", "Fetch paused."))

    def stop_fetch(self) -> None:
        """Request cancellation of the active Last.fm fetch worker."""

        if self._active_fetch_worker is None:
            return
        self._active_fetch_worker.stop_fetch()
        self._fetch_paused = False
        self.window.set_fetch_control_state(active=False, paused=False)
        self.window.append_feedback(translate("ApplicationController", "Stopping fetch."))

    def resolve_youtube_urls(
        self,
        username: str | None = None,
        priority_cache_key: str | None = None,
        max_tracks: int | None = None,
    ) -> None:
        """Start resolving YouTube URLs for stored tracks."""

        username = username or self.window.username()
        if not username:
            LOGGER.warning("Lookup requested without a Last.fm username")
            self.window.append_feedback(
                translate(
                    "ApplicationController",
                    "Enter a Last.fm username before resolving tracks.",
                )
            )
            return

        LOGGER.info("YouTube lookup requested for Last.fm user %s", username)
        print(f"[myLastFmPlayer] Starting YouTube lookup for {username}", flush=True)
        self.window.set_progress(
            0,
            translate("ApplicationController", "Starting YouTube lookup"),
        )
        worker = self.lookup_worker_factory(
            username,
            self.youtube_resolver,
            self.repository,
            priority_cache_key,
            max_tracks,
        )
        self._run_worker(worker)

    def download_tracks(
        self,
        username: str | None = None,
        priority_cache_key: str | None = None,
        max_downloads: int | None = None,
    ) -> None:
        """Start downloading queued tracks for the active or supplied username."""

        username = username or self.window.username()
        if not username:
            LOGGER.warning("Download requested without a Last.fm username")
            self.window.append_feedback(
                translate(
                    "ApplicationController",
                    "Enter a Last.fm username before downloading tracks.",
                )
            )
            return

        concurrency = self.window.concurrency_input.value()
        LOGGER.info(
            "Download requested for Last.fm user %s with concurrency %s",
            username,
            concurrency,
        )
        print(
            f"[myLastFmPlayer] Starting downloads for {username} "
            f"with concurrency {concurrency}",
            flush=True,
        )
        self.window.set_progress(0, translate("ApplicationController", "Starting downloads"))
        worker = self.download_worker_factory(
            username,
            self.download_manager,
            self.repository,
            concurrency,
            priority_cache_key,
            max_downloads,
        )
        self._run_worker(worker)

    def play_selected_track(self) -> None:
        """Play the selected track or prepare it for playback when needed."""

        selected_row = self.window.selected_track_row()
        selected_track = self.window.selected_track()
        if selected_row is None or selected_track is None:
            self.window.append_feedback(
                translate("ApplicationController", "Select a downloaded track before playing.")
            )
            return

        self._play_track(selected_row, selected_track)

    def pause_playback(self) -> None:
        """Pause active playback and show the result in the feedback log."""

        try:
            self.playback_service.pause()
        except PlaybackError as error:
            self.window.append_feedback(str(error))
            return
        self.window.append_feedback(translate("ApplicationController", "Playback paused."))

    def stop_playback(self) -> None:
        """Stop active playback and persist the restored downloaded state."""

        stopped_track = self.playback_service.stop()
        if stopped_track is None:
            self.window.append_feedback(
                translate("ApplicationController", "No track is currently playing.")
            )
            return

        self._update_track_by_cache_key(stopped_track)
        self.window.reset_playback_timeline()
        self.window.append_feedback(translate("ApplicationController", "Playback stopped."))
        self._save_visible_tracks()

    def seek_playback(self, position_ms: int) -> None:
        """Seek active playback to ``position_ms`` and refresh the timeline."""

        try:
            self.playback_service.seek(position_ms)
        except PlaybackError as error:
            self.window.append_feedback(str(error))
            return
        self.window.set_playback_timeline(
            self.playback_service.position_ms(),
            self.playback_service.duration_ms(),
        )

    def _run_worker(self, worker: WorkflowWorker) -> None:
        thread = QThread(self)
        worker_name = worker.__class__.__name__
        print(f"[myLastFmPlayer] Preparing {worker_name} on background thread", flush=True)
        worker.moveToThread(thread)
        self._running_worker_count += 1
        self.window.set_workflow_enabled(False)

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
            worker.tracks_updated.connect(self._handle_tracks_updated)
            worker.tracks_loaded.connect(self._handle_tracks_loaded)
            worker.fetch_stopped.connect(self._handle_fetch_stopped)
        if isinstance(worker, LookupTracksWorker):
            worker.track_updated.connect(self._handle_track_updated)
            worker.tracks_resolved.connect(self._handle_tracks_resolved)
        if isinstance(worker, DownloadTracksWorker):
            worker.track_updated.connect(self._handle_track_updated)
            worker.tracks_downloaded.connect(self._handle_tracks_downloaded)
        worker.finished.connect(self._complete_worker_run)
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
            self.window.append_feedback(
                translate(
                    "ApplicationController",
                    "Fetch for {username} returned invalid track data.",
                    username=username,
                )
            )
            return

        self.window.set_tracks(tracks)
        self.window.append_feedback(
            translate(
                "ApplicationController",
                "Fetched and stored {count} tracks for {username}.",
                count=len(tracks),
                username=username,
            )
        )
        self._active_fetch_worker = None
        self._fetch_paused = False
        self.window.set_fetch_control_state(active=False, paused=False)
        LOGGER.info("Loaded %s fetched tracks into UI for %s", len(tracks), username)
        print(
            f"[myLastFmPlayer] UI loaded {len(tracks)} fetched tracks for {username}",
            flush=True,
        )
        if tracks:
            self._start_automatic_lookup(username, len(tracks))

    def _handle_fetch_stopped(self, username: str, tracks: object) -> None:
        self._active_fetch_worker = None
        self._fetch_paused = False
        self.window.set_fetch_control_state(active=False, paused=False)
        if not isinstance(tracks, list):
            self.window.append_feedback(
                translate(
                    "ApplicationController",
                    "Stopped fetch for {username} returned invalid data.",
                    username=username,
                )
            )
            return

        self.window.set_tracks(tracks)
        self.window.append_feedback(
            translate(
                "ApplicationController",
                "Stopped fetch for {username} after {count} tracks.",
                username=username,
                count=len(tracks),
            )
        )

    def _handle_tracks_updated(self, username: str, tracks: object) -> None:
        if not isinstance(tracks, list):
            self.window.append_feedback(
                translate(
                    "ApplicationController",
                    "Fetch for {username} returned invalid partial data.",
                    username=username,
                )
            )
            return

        self.window.set_tracks(tracks)
        self.window.show_status(
            translate(
                "ApplicationController",
                "Fetched {count} tracks for {username}",
                count=len(tracks),
                username=username,
            )
        )
        LOGGER.info("Loaded %s partial fetched tracks into UI for %s", len(tracks), username)

    def _handle_track_updated(self, username: str, track: object) -> None:
        if not isinstance(track, Track):
            self.window.append_feedback(
                translate(
                    "ApplicationController",
                    "Workflow for {username} returned an invalid track update.",
                    username=username,
                )
            )
            return

        self._update_track_by_cache_key(track)

    def _handle_tracks_resolved(self, username: str, tracks: object) -> None:
        if not isinstance(tracks, list):
            self.window.append_feedback(
                translate(
                    "ApplicationController",
                    "Lookup for {username} returned invalid track data.",
                    username=username,
                )
            )
            return

        self.window.set_tracks(tracks)
        self.window.append_feedback(
            translate(
                "ApplicationController",
                "Resolved YouTube URLs for {count} tracks.",
                count=len(tracks),
            )
        )
        LOGGER.info("Loaded %s resolved tracks into UI for %s", len(tracks), username)
        if self._pending_play_cache_key and self._track_has_youtube_url(
            tracks,
            self._pending_play_cache_key,
        ):
            self._start_priority_download(username, self._pending_play_cache_key)
        elif self._has_download_candidates(tracks):
            self._start_automatic_download(username)
        else:
            self.window.append_feedback(
                translate("ApplicationController", "No queued tracks are ready for download.")
            )

    def _handle_tracks_downloaded(self, username: str, tracks: object) -> None:
        if not isinstance(tracks, list):
            self.window.append_feedback(
                translate(
                    "ApplicationController",
                    "Download for {username} returned invalid track data.",
                    username=username,
                )
            )
            return

        self.window.set_tracks(tracks)
        self.window.append_feedback(
            translate(
                "ApplicationController",
                "Downloaded {count} tracks for {username}.",
                count=len(tracks),
                username=username,
            )
        )
        LOGGER.info("Loaded %s downloaded tracks into UI for %s", len(tracks), username)
        if self._pending_play_cache_key:
            self._play_prepared_track(self._pending_play_cache_key)

    def _handle_worker_error(self, message: str) -> None:
        LOGGER.error("Worker error: %s", message)
        print(f"[myLastFmPlayer] Worker error shown in UI: {message}", flush=True)
        self.window.append_feedback(message)
        self.window.set_progress(0, translate("ApplicationController", "Failed"))

    def _restore_previous_playing_track(
        self,
        previous_track: Track | None,
        selected_track: Track,
    ) -> None:
        if previous_track is None or previous_track.cache_key == selected_track.cache_key:
            return
        self._update_track_by_cache_key(previous_track.with_status(TrackStatus.DOWNLOADED))

    def _update_track_by_cache_key(self, track: Track) -> None:
        for row, visible_track in enumerate(self.window.tracks()):
            if visible_track.cache_key == track.cache_key:
                self.window.update_track(row, track)
                return

    def _save_visible_tracks(self) -> None:
        username = self.window.username()
        if username:
            self.repository.save_tracks(username, self.window.tracks())

    def _play_track(self, row: int, track: Track) -> None:
        if self._can_prepare_for_playback(track):
            self._prepare_selected_track_for_playback(track)
            return

        previous_track = self.playback_service.current_track
        try:
            playing_track = self.playback_service.play(track)
        except PlaybackError as error:
            self.window.append_feedback(str(error))
            return

        self._restore_previous_playing_track(previous_track, track)
        self.window.update_track(row, playing_track)
        self.window.set_playback_timeline(
            self.playback_service.position_ms(),
            self.playback_service.duration_ms(),
        )
        self.window.append_feedback(
            translate(
                "ApplicationController",
                "Playing {artist} - {title}.",
                artist=playing_track.artist,
                title=playing_track.title,
            )
        )
        self._save_visible_tracks()

    def _can_prepare_for_playback(self, track: Track) -> bool:
        return track.status not in {TrackStatus.DOWNLOADED, TrackStatus.PLAYING} or (
            track.status is TrackStatus.DOWNLOADED and not track.local_path
        )

    def _prepare_selected_track_for_playback(self, track: Track) -> None:
        username = self.window.username()
        if not username:
            self.window.append_feedback(
                translate(
                    "ApplicationController",
                    "Enter a Last.fm username before preparing playback.",
                )
            )
            return
        self._pending_play_cache_key = track.cache_key
        self._save_visible_tracks()
        self.window.append_feedback(
            translate(
                "ApplicationController",
                "Preparing {artist} - {title} for playback.",
                artist=track.artist,
                title=track.title,
            )
        )
        if track.youtube_url:
            self._start_priority_download(username, track.cache_key)
            return
        self.resolve_youtube_urls(
            username,
            priority_cache_key=track.cache_key,
            max_tracks=1,
        )

    def _start_automatic_lookup(self, username: str, track_count: int) -> None:
        message = translate(
            "ApplicationController",
            "Starting automatic YouTube lookup for {count} fetched tracks.",
            count=track_count,
        )
        LOGGER.info("%s User=%s", message, username)
        print(f"[myLastFmPlayer] {message} user={username}", flush=True)
        self.window.append_feedback(message)
        self.resolve_youtube_urls(username)

    def _start_automatic_download(self, username: str) -> None:
        message = translate(
            "ApplicationController",
            "Starting automatic download queue for resolved tracks.",
        )
        LOGGER.info("%s User=%s", message, username)
        print(f"[myLastFmPlayer] {message} user={username}", flush=True)
        self.window.append_feedback(message)
        self.download_tracks(username)

    def _start_priority_download(self, username: str, cache_key: str) -> None:
        message = translate(
            "ApplicationController",
            "Starting priority download for selected track.",
        )
        LOGGER.info("%s User=%s cache_key=%s", message, username, cache_key)
        print(
            f"[myLastFmPlayer] {message} user={username} cache_key={cache_key}",
            flush=True,
        )
        self.window.append_feedback(message)
        self.download_tracks(
            username,
            priority_cache_key=cache_key,
            max_downloads=1,
        )

    def _has_download_candidates(self, tracks: list[Track]) -> bool:
        return any(
            bool(track.youtube_url)
            and track.status not in {TrackStatus.DOWNLOADED, TrackStatus.NOT_FOUND}
            for track in tracks
        )

    def _track_has_youtube_url(self, tracks: list[Track], cache_key: str) -> bool:
        return any(track.cache_key == cache_key and bool(track.youtube_url) for track in tracks)

    def _play_prepared_track(self, cache_key: str) -> None:
        for row, track in enumerate(self.window.tracks()):
            if track.cache_key != cache_key:
                continue
            if track.status is not TrackStatus.DOWNLOADED:
                return
            self._pending_play_cache_key = None
            self._play_track(row, track)
            return

    def _connect_playback_callbacks(self) -> None:
        if self._playback_callbacks_connected or self._playback_service is None:
            return
        self._playback_service.on_position_changed(self._handle_playback_position_changed)
        self._playback_service.on_duration_changed(self._handle_playback_duration_changed)
        self._playback_service.on_finished(self._handle_playback_finished)
        self._playback_callbacks_connected = True

    def _handle_playback_position_changed(self, position_ms: int) -> None:
        self.window.set_playback_timeline(position_ms, self.playback_service.duration_ms())

    def _handle_playback_duration_changed(self, duration_ms: int) -> None:
        self.window.set_playback_timeline(self.playback_service.position_ms(), duration_ms)

    def _handle_playback_finished(self) -> None:
        finished_track = self.playback_service.finish_current()
        if finished_track is None:
            return

        self._update_track_by_cache_key(finished_track)
        self.window.reset_playback_timeline()
        next_track = self.window.next_track_after(finished_track.cache_key)
        if next_track is None:
            self.window.append_feedback(
                translate("ApplicationController", "Playback finished.")
            )
            self._save_visible_tracks()
            return

        next_row, track = next_track
        self.window.select_track_row(next_row)
        self.window.append_feedback(
            translate(
                "ApplicationController",
                "Continuing with next track: {artist} - {title}.",
                artist=track.artist,
                title=track.title,
            )
        )
        self._play_track(next_row, track)

    def _complete_worker_run(self) -> None:
        self._running_worker_count = max(0, self._running_worker_count - 1)
        if self._running_worker_count == 0:
            self.window.set_workflow_enabled(True)
            self.window.set_fetch_control_state(active=False, paused=False)

    def _forget_thread(self, thread: QThread) -> None:
        if thread in self._active_threads:
            self._active_threads.remove(thread)
        print(
            f"[myLastFmPlayer] Thread finished; active_threads={len(self._active_threads)}",
            flush=True,
        )

    def _forget_worker(self, worker: WorkflowWorker) -> None:
        if worker is self._active_fetch_worker:
            self._active_fetch_worker = None
            self._fetch_paused = False
        if worker in self._active_workers:
            self._active_workers.remove(worker)
        print(
            f"[myLastFmPlayer] Worker released; active_workers={len(self._active_workers)}",
            flush=True,
        )

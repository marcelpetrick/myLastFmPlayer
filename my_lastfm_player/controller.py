# pylint: disable=too-many-lines  # god object; tracked for future decomposition
from __future__ import annotations

import logging
import random
import time
from collections.abc import Callable
from concurrent.futures import Future
from dataclasses import replace
from pathlib import Path
from typing import Any

from PyQt6.QtCore import QObject, QThread, QUrl
from PyQt6.QtGui import QDesktopServices

from my_lastfm_player.app_credentials import (
    LASTFM_API_KEY_ENV,
    LASTFM_API_SECRET_ENV,
    lastfm_api_credentials,
)
from my_lastfm_player.background_tasks import BackgroundTaskRunner
from my_lastfm_player.dependencies import DependencyCheckResult, check_external_dependencies
from my_lastfm_player.download import DownloadManager
from my_lastfm_player.i18n import translate
from my_lastfm_player.lastfm import (
    ArtistImage,
    LastFmArtistInfoClient,
    LastFmLovedTracksScraper,
)
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.playback import PlaybackError, PlaybackService
from my_lastfm_player.scrobbling import SCROBBLE_THRESHOLD, ScrobblingService
from my_lastfm_player.settings import AppSettings
from my_lastfm_player.storage import JsonTrackRepository, StorageError
from my_lastfm_player.ui.main_window import MainWindow
from my_lastfm_player.workers import (
    ArtistImageWorker,
    DownloadTracksWorker,
    FetchLovedTracksWorker,
    LookupTracksWorker,
)
from my_lastfm_player.youtube import YouTubeResolver

LOGGER = logging.getLogger(__name__)
THREAD_SHUTDOWN_TIMEOUT_MS = 3000

DependencyChecker = Callable[[], DependencyCheckResult]
FetchWorkerFactory = Callable[
    [str, LastFmLovedTracksScraper, JsonTrackRepository, int | None],
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
ArtistImageWorkerFactory = Callable[[str, LastFmArtistInfoClient], ArtistImageWorker]
WorkflowWorker = FetchLovedTracksWorker | LookupTracksWorker | DownloadTracksWorker


class ApplicationController(QObject):  # pylint: disable=too-many-instance-attributes  # god object
    """Coordinate UI events, background workers, persistence, and playback."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        window: MainWindow,
        repository: JsonTrackRepository | None = None,
        scraper: LastFmLovedTracksScraper | None = None,
        youtube_resolver: YouTubeResolver | None = None,
        download_manager: DownloadManager | None = None,
        playback_service: PlaybackService | None = None,
        artist_info_client: LastFmArtistInfoClient | None = None,
        dependency_checker: DependencyChecker = check_external_dependencies,
        fetch_worker_factory: FetchWorkerFactory = FetchLovedTracksWorker,
        lookup_worker_factory: LookupWorkerFactory = LookupTracksWorker,
        download_worker_factory: DownloadWorkerFactory = DownloadTracksWorker,
        artist_image_worker_factory: ArtistImageWorkerFactory = ArtistImageWorker,
        artist_images_enabled: bool = True,
    ) -> None:
        super().__init__(window)
        self.window = window
        self.repository = repository or JsonTrackRepository()
        self.scraper = scraper or LastFmLovedTracksScraper()
        self.youtube_resolver = youtube_resolver or YouTubeResolver()
        self.download_manager = download_manager or DownloadManager()
        self._playback_service = playback_service
        self.artist_info_client = artist_info_client or LastFmArtistInfoClient()
        self._artist_images_enabled = artist_images_enabled
        self.dependency_checker = dependency_checker
        self.fetch_worker_factory = fetch_worker_factory
        self.lookup_worker_factory = lookup_worker_factory
        self.download_worker_factory = download_worker_factory
        self.artist_image_worker_factory = artist_image_worker_factory
        self._active_threads: list[QThread] = []
        self._active_workers: list[WorkflowWorker] = []
        self._active_artist_image_workers: list[ArtistImageWorker] = []
        self._running_worker_count = 0
        self._pending_play_cache_key: str | None = None
        self._pending_retry_cache_key: str | None = None
        self._active_fetch_worker: FetchLovedTracksWorker | None = None
        self._fetch_paused = False
        self._started_incremental_lookup_for_fetch = False
        self._download_worker_active = False
        self._download_stop_requested = False
        self._playback_callbacks_connected = False
        self._scrobbling_service: ScrobblingService | None = None
        self._scrobbling_tasks = BackgroundTaskRunner(
            "lastfm-scrobbling",
            "Background Last.fm scrobbling task failed",
        )
        self._scrobbling_futures = self._scrobbling_tasks.futures
        self._scrobble_submitted = False
        self._scrobble_seek_start_ms: int = 0
        self._playback_start_time: int | None = None
        self._artist_image_cache: dict[str, ArtistImage | None] = {}
        self._random = random.SystemRandom()

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
        self.window.fetch_requested.connect(self.fetch_loved_tracks)
        self.window.username_input.editingFinished.connect(
            self.load_cached_tracks_for_entered_username
        )
        self.window.fetch_pause_requested.connect(self.toggle_fetch_pause)
        self.window.fetch_stop_requested.connect(self.stop_fetch)
        self.window.download_requested.connect(self.download_tracks)
        self.window.download_stop_requested.connect(self.stop_downloads)
        self.window.retry_download_requested.connect(self.retry_track_download)
        self.window.play_requested.connect(self.play_selected_track)
        self.window.pause_requested.connect(self.pause_playback)
        self.window.stop_requested.connect(self.stop_playback)
        self.window.next_requested.connect(self.play_next_track)
        self.window.seek_requested.connect(self.seek_playback)
        self.window.artist_page_requested.connect(self.open_artist_page)
        self.window.language_changed.connect(self.check_dependencies)
        self.window.randomize_playback_changed.connect(AppSettings().set_randomize_playback)
        self.window.preferences_requested.connect(self._show_preferences)
        self.window.file_cache_requested.connect(self.open_file_cache)
        self.window.quit_requested.connect(self._handle_quit)
        self._init_scrobbling()
        self._apply_ytdlp_settings()
        self.check_dependencies()

    def _handle_quit(self) -> None:
        self._shutdown_background_work()
        if not AppSettings().keep_data_on_quit():
            self.repository.wipe()

    def _shutdown_background_work(self) -> None:
        if self._active_fetch_worker is not None:
            self._active_fetch_worker.stop_fetch()
            self._fetch_paused = False
            self.window.set_fetch_control_state(active=False, paused=False)
        if self._download_worker_active or self._has_active_download_worker():
            self._download_worker_active = False
            self._download_stop_requested = True
            self.download_manager.stop()
            self.window.set_download_active(False)
        for thread in list(self._active_threads):
            if hasattr(thread, "quit"):
                thread.quit()
            if hasattr(thread, "wait"):
                thread.wait(THREAD_SHUTDOWN_TIMEOUT_MS)
        self._scrobbling_tasks.shutdown()

    def _report_user_action(self, message: str) -> None:
        LOGGER.info("User action: %s", message)
        self.window.append_feedback(message)

    def _report_storage_error(self, action: str, error: StorageError) -> None:
        LOGGER.error("Storage error while %s: %s", action, error)
        self.window.append_feedback(
            translate(
                "ApplicationController",
                "Storage error while {action}: {error}",
                action=action,
                error=str(error),
            )
        )
        self.window.set_progress(0, translate("ApplicationController", "Storage error"))

    def load_cached_tracks_for_entered_username(self, *, verify_online_count: bool = False) -> bool:
        """Load locally stored tracks for the entered username when available."""

        if self._active_fetch_worker is not None:
            LOGGER.info("Skipped cached-track load because a fresh fetch is active")
            return False

        username = self.window.username()
        if not username:
            return False

        try:
            tracks = self.repository.load_tracks(username)
        except StorageError as error:
            self._report_storage_error(
                translate(
                    "ApplicationController",
                    "loading cached tracks for {username}",
                    username=username,
                ),
                error,
            )
            return False
        if not tracks:
            if verify_online_count:
                self._report_user_action(
                    translate(
                        "ApplicationController",
                        "No cached tracks found for {username}; fetching from Last.fm.",
                        username=username,
                    )
                )
            return False

        cached_count = len(tracks)
        if verify_online_count:
            self._report_user_action(
                translate(
                    "ApplicationController",
                    "Found {count} cached tracks for {username}; using local cache.",
                    count=cached_count,
                    username=username,
                )
            )

        try:
            tracks = self.repository.mark_cached_downloads(
                self.repository.mark_cached_lookups(tracks)
            )
            tracks = self.repository.merge_tracks(username, tracks)
        except StorageError as error:
            self._report_storage_error(
                translate(
                    "ApplicationController",
                    "applying cached track state for {username}",
                    username=username,
                ),
                error,
            )
            return False
        self.window.set_tracks(tracks)
        self._report_user_action(
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
        self._report_user_action(
            translate(
                "ApplicationController",
                "Dependency check finished: {message}",
                message=result.user_message(),
            )
        )
        return result

    def open_file_cache(self) -> None:
        """Open the application data folder (tracks, cache, credentials) in the file manager."""

        data_dir = self.repository.data_dir
        try:
            data_dir.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            LOGGER.exception("Could not create data directory %s", data_dir)
            self.window.append_feedback(
                translate(
                    "ApplicationController",
                    "Could not open data folder: {error}",
                    error=error,
                )
            )
            return

        if QDesktopServices.openUrl(QUrl.fromLocalFile(str(data_dir))):
            self._report_user_action(
                translate(
                    "ApplicationController",
                    "Opened data folder: {path}",
                    path=data_dir,
                )
            )
            return

        self.window.append_feedback(
            translate(
                "ApplicationController",
                "Could not open data folder: {path}",
                path=data_dir,
            )
        )

    def open_artist_page(self, url: str) -> None:
        """Open an artist Last.fm page in the user's default browser."""

        if not QDesktopServices.openUrl(QUrl(url)):
            self.window.append_feedback(
                translate(
                    "ApplicationController",
                    "Could not open artist page: {url}",
                    url=url,
                )
            )

    def _init_scrobbling(self) -> None:
        app_credentials = lastfm_api_credentials()
        if not app_credentials.is_configured:
            self._report_user_action(
                translate(
                    "ApplicationController",
                    "Last.fm scrobbling is disabled because "
                    "{api_key_env}/{api_secret_env} are not configured and "
                    "no bundled credentials are available.",
                    api_key_env=LASTFM_API_KEY_ENV,
                    api_secret_env=LASTFM_API_SECRET_ENV,
                )
            )
            return
        creds = self.repository.load_credentials()
        scrobbling_enabled = AppSettings().scrobbling_enabled(
            default_enabled=bool(creds.get("scrobbling_enabled", True))
        )
        self._report_user_action(
            translate(
                "ApplicationController",
                "Loaded Last.fm scrobbling settings; stored session key is {state}.",
                state=(
                    translate("ApplicationController", "present")
                    if creds.get("session_key")
                    else translate("ApplicationController", "missing")
                ),
            )
        )
        self._scrobbling_service = ScrobblingService(
            api_key=app_credentials.api_key,
            api_secret=app_credentials.api_secret,
            session_key=str(creds.get("session_key", "")),
            username=str(creds.get("username", "")),
            scrobbling_enabled=scrobbling_enabled,
        )
        if self._scrobbling_service.session_key:
            self._report_user_action(
                translate(
                    "ApplicationController",
                    "Verifying stored Last.fm session key in the background.",
                )
            )
            self._submit_scrobbling_task(self._scrobbling_service.try_connect)

    def _show_preferences(self) -> None:
        from my_lastfm_player.ui.preferences_dialog import PreferencesDialog  # noqa: PLC0415

        self._report_user_action(translate("ApplicationController", "Opening preferences."))
        dialog = PreferencesDialog(self.window, self._scrobbling_service)
        dialog.exec()
        self._save_scrobbling_credentials()
        self._apply_ytdlp_settings()

    def _apply_ytdlp_settings(self) -> None:
        browser = AppSettings().ytdlp_cookies_browser()
        self.youtube_resolver.cookies_browser = browser
        self.download_manager.cookies_browser = browser

    def _save_scrobbling_credentials(self) -> None:
        if self._scrobbling_service is None:
            self._report_user_action(
                translate(
                    "ApplicationController",
                    "Preferences closed; no Last.fm scrobbling service is active.",
                )
            )
            return
        AppSettings().set_scrobbling_enabled(self._scrobbling_service.scrobbling_enabled)
        try:
            self.repository.save_credentials(self._scrobbling_service.credentials_dict())
        except StorageError as error:
            self._report_storage_error(
                translate("ApplicationController", "saving Last.fm preferences"),
                error,
            )
            return
        self._report_user_action(
            translate(
                "ApplicationController",
                "Saved Last.fm scrobbling preferences for {username}.",
                username=self._scrobbling_service.username
                or translate("ApplicationController", "no user"),
            )
        )

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

        if self.load_cached_tracks_for_entered_username(verify_online_count=True):
            self.window.set_fetch_control_state(active=False, paused=False)
            self.window.set_progress(
                100,
                translate("ApplicationController", "Loaded cached tracks"),
            )
            tracks = self.window.tracks()
            if tracks:
                self._start_automatic_lookup(username, len(tracks))
            return

        expected_count: int | None = None

        LOGGER.info(
            "Fresh fetch requested for Last.fm user %s (expected=%s)", username, expected_count
        )
        self._report_user_action(
            translate(
                "ApplicationController",
                "Starting fresh Last.fm fetch for {username}.",
                username=username,
            )
        )
        self.window.set_workflow_enabled(False)
        self.window.set_fetch_control_state(active=True, paused=False)
        self._fetch_paused = False
        self.window.set_progress(0, translate("ApplicationController", "Starting fetch"))
        worker = self.fetch_worker_factory(username, self.scraper, self.repository, expected_count)
        self._active_fetch_worker = worker
        self._started_incremental_lookup_for_fetch = False
        self._run_worker(worker)

    def toggle_fetch_pause(self) -> None:
        """Pause or resume the active Last.fm fetch worker."""

        if self._active_fetch_worker is None:
            return
        if self._fetch_paused:
            self._active_fetch_worker.resume_fetch()
            self._fetch_paused = False
            self.window.set_fetch_control_state(active=True, paused=False)
            self._report_user_action(
                translate("ApplicationController", "Fetch resumed.")
            )
            return
        self._active_fetch_worker.pause_fetch()
        self._fetch_paused = True
        self.window.set_fetch_control_state(active=True, paused=True)
        self._report_user_action(translate("ApplicationController", "Fetch paused."))

    def stop_fetch(self) -> None:
        """Request cancellation of the active Last.fm fetch worker."""

        if self._active_fetch_worker is None:
            return
        self._active_fetch_worker.stop_fetch()
        self._fetch_paused = False
        self.window.set_fetch_control_state(active=False, paused=False)
        self._report_user_action(translate("ApplicationController", "Stopping fetch."))

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
        self._report_user_action(
            translate(
                "ApplicationController",
                "Starting YouTube lookup for {username}; "
                "priority={priority}, limit={limit}.",
                username=username,
                priority=priority_cache_key
                or translate("ApplicationController", "none"),
                limit=(
                    max_tracks
                    if max_tracks is not None
                    else translate("ApplicationController", "all")
                ),
            )
        )
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

        if self._download_worker_active or self._has_active_download_worker():
            LOGGER.info("Download request ignored because a download worker is already active")
            self.window.append_feedback(
                translate(
                    "ApplicationController",
                    "Downloads are already running.",
                )
            )
            return

        concurrency = AppSettings().download_concurrency()
        LOGGER.info(
            "Download requested for Last.fm user %s with concurrency %s",
            username,
            concurrency,
        )
        self._report_user_action(
            translate(
                "ApplicationController",
                "Starting downloads for {username}; concurrency={concurrency}, "
                "priority={priority}, limit={limit}.",
                username=username,
                concurrency=concurrency,
                priority=priority_cache_key
                or translate("ApplicationController", "none"),
                limit=(
                    max_downloads
                    if max_downloads is not None
                    else translate("ApplicationController", "all")
                ),
            )
        )
        self.download_manager.resume()
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
        if priority_cache_key is None:
            self._download_worker_active = True
            self._download_stop_requested = False
            self.window.set_download_active(True)

    def play_selected_track(self) -> None:
        """Play the selected track or prepare it for playback when needed."""

        selected_track = self.window.selected_track()
        if selected_track is None:
            choice = self._random.choice if self.window.randomize_playback() else None
            fallback = self.window.first_or_random_downloaded_track(choice)
            if fallback is None:
                self.window.append_feedback(
                    translate("ApplicationController", "Select a downloaded track before playing.")
                )
                return
            row, selected_track = fallback
            self.window.select_track_row(row)

        self._play_track(selected_track)

    def pause_playback(self) -> None:
        """Toggle between pause and resume for active playback."""

        if self.playback_service.is_paused():
            try:
                self.playback_service.resume()
            except PlaybackError as error:
                self.window.append_feedback(str(error))
                return
            self._report_user_action(
                translate("ApplicationController", "Playback resumed.")
            )
        else:
            try:
                self.playback_service.pause()
            except PlaybackError as error:
                self.window.append_feedback(str(error))
                return
            self._report_user_action(
                translate("ApplicationController", "Playback paused.")
            )

    def stop_playback(self) -> None:
        """Stop active playback and clear the playing-row indicator."""

        stopped_track = self.playback_service.stop()
        if stopped_track is None:
            self.window.append_feedback(
                translate("ApplicationController", "No track is currently playing.")
            )
            return

        self.window.set_playing_track(None)
        self.window.set_now_playing(None)
        self.window.set_artist_image(None, None)
        self.window.reset_playback_timeline()
        self.window.set_playback_controls(active=False)
        self._scrobble_submitted = False
        self._playback_start_time = None
        self._report_user_action(translate("ApplicationController", "Playback stopped."))

    def play_next_track(self) -> None:
        """Skip active playback to the next track using normal continuation rules."""

        current_track = self.playback_service.current_track
        if current_track is None:
            self.window.append_feedback(
                translate("ApplicationController", "No track is currently playing.")
            )
            return

        self._continue_playback_from(current_track.cache_key)

    def seek_playback(self, position_ms: int) -> None:
        """Seek active playback to ``position_ms`` and refresh the timeline."""

        try:
            self.playback_service.seek(position_ms)
        except PlaybackError as error:
            self.window.append_feedback(str(error))
            return
        self._scrobble_submitted = False
        self._scrobble_seek_start_ms = position_ms
        self.window.set_playback_timeline(
            self.playback_service.position_ms(),
            self.playback_service.duration_ms(),
        )
        self._report_user_action(
            translate(
                "ApplicationController",
                "Seeked playback to {seconds} seconds.",
                seconds=position_ms // 1000,
            )
        )

    def _run_worker(self, worker: WorkflowWorker) -> None:
        thread = QThread(self)
        worker_name = worker.__class__.__name__
        LOGGER.info("Preparing %s on background thread", worker_name)
        worker.moveToThread(thread)
        self._running_worker_count += 1
        self.window.set_workflow_enabled(False)

        thread.started.connect(worker.run)
        worker.progress.connect(self.window.set_progress)
        worker.error.connect(
            lambda message, worker=worker: self._handle_worker_error(worker, message)
        )
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
        LOGGER.info(
            "Starting thread for %s; active_threads=%d active_workers=%d",
            worker_name,
            len(self._active_threads),
            len(self._active_workers),
        )
        thread.start()

    def _run_artist_image_worker(self, worker: ArtistImageWorker) -> None:
        thread = QThread(self)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.artist_image_loaded.connect(self._handle_artist_image_loaded)
        worker.error.connect(self._handle_artist_image_error)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda: self._forget_thread(thread))
        thread.finished.connect(lambda worker=worker: self._forget_artist_image_worker(worker))

        self._active_threads.append(thread)
        self._active_artist_image_workers.append(worker)
        LOGGER.info("Starting artist image worker for %s", worker.artist)
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
        self._report_user_action(
            translate(
                "ApplicationController",
                "Fetched and stored {count} tracks for {username}.",
                count=len(tracks),
                username=username,
            )
        )
        already_started_lookup = self._started_incremental_lookup_for_fetch
        self._active_fetch_worker = None
        self._fetch_paused = False
        self._started_incremental_lookup_for_fetch = False
        self.window.set_fetch_control_state(active=False, paused=False)
        LOGGER.info("Loaded %s fetched tracks into UI for %s", len(tracks), username)
        if tracks and not already_started_lookup:
            self._start_automatic_lookup(username, len(tracks))

    def _handle_fetch_stopped(self, username: str, tracks: object) -> None:
        self._active_fetch_worker = None
        self._fetch_paused = False
        self._started_incremental_lookup_for_fetch = False
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
        self._report_user_action(
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
        LOGGER.info("Loaded %s partial fetched tracks into UI for %s", len(tracks), username)
        self._report_user_action(
            translate(
                "ApplicationController",
                "Fetch progress for {username}: {count} tracks are visible now.",
                username=username,
                count=len(tracks),
            )
        )
        self.window.show_status(
            translate(
                "ApplicationController",
                "Fetched {count} tracks for {username}",
                count=len(tracks),
                username=username,
            )
        )
        if (
            tracks
            and self._active_fetch_worker is not None
            and not self._started_incremental_lookup_for_fetch
        ):
            self._started_incremental_lookup_for_fetch = True
            try:
                self.repository.merge_tracks(username, tracks)
            except StorageError as error:
                self._report_storage_error(
                    translate(
                        "ApplicationController",
                        "saving partial fetch results for {username}",
                        username=username,
                    ),
                    error,
                )
                return
            self._start_automatic_lookup(username, len(tracks))

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
        self._report_user_action(
            translate(
                "ApplicationController",
                "Track update from {username}: {artist} - {title} is now {status}.",
                username=username,
                artist=track.artist,
                title=track.title,
                status=track.status.value,
            )
        )
        if track.status is TrackStatus.QUEUED and track.youtube_url:
            self._handle_track_ready_for_download(username, track)

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

        # Reload from the repository so the UI shows the full current state.
        try:
            current_tracks = self.repository.load_tracks(username)
        except StorageError as error:
            self._report_storage_error(
                translate(
                    "ApplicationController",
                    "loading resolved tracks for {username}",
                    username=username,
                ),
                error,
            )
            return
        self.window.set_tracks(current_tracks)
        resolved_count = sum(1 for t in current_tracks if t.youtube_url)
        not_found_count = sum(
            1 for t in current_tracks if t.status is TrackStatus.NOT_FOUND
        )
        self._report_user_action(
            translate(
                "ApplicationController",
                "Resolved YouTube URLs for {resolved_count}/{count} tracks; "
                "{not_found_count} were not found.",
                count=len(current_tracks),
                resolved_count=resolved_count,
                not_found_count=not_found_count,
            )
        )
        LOGGER.info("Loaded %s resolved tracks into UI for %s", len(current_tracks), username)
        if self._pending_play_cache_key and self._track_has_youtube_url(
            current_tracks,
            self._pending_play_cache_key,
        ):
            self._start_priority_download(username, self._pending_play_cache_key)
        elif self._pending_retry_cache_key and self._track_has_youtube_url(
            current_tracks,
            self._pending_retry_cache_key,
        ):
            self._start_priority_download(username, self._pending_retry_cache_key)
        elif (
            self._has_download_candidates(current_tracks)
            and not self._download_worker_active
            and not self._has_active_download_worker()
        ):
            self._start_automatic_download(username)
        elif not self._has_download_candidates(current_tracks):
            self._report_user_action(
                translate("ApplicationController", "No queued tracks are ready for download.")
            )

    def _handle_tracks_downloaded(self, username: str, tracks: object) -> None:
        was_bulk = self._download_worker_active
        stop_was_requested = self._download_stop_requested
        self._download_worker_active = False
        self._download_stop_requested = False
        self.window.set_download_active(False)
        if not isinstance(tracks, list):
            self.window.append_feedback(
                translate(
                    "ApplicationController",
                    "Download for {username} returned invalid track data.",
                    username=username,
                )
            )
            return

        # Reload from the repository so the UI shows the full current state, not the
        # stale snapshot the worker started with (which may be a small partial list if
        # the fetch was still running when this worker was spawned).
        try:
            current_tracks = self.repository.load_tracks(username)
        except StorageError as error:
            self._report_storage_error(
                translate(
                    "ApplicationController",
                    "loading downloaded tracks for {username}",
                    username=username,
                ),
                error,
            )
            return
        self.window.set_tracks(current_tracks)
        downloaded_count = sum(
            1 for t in current_tracks if t.status is TrackStatus.DOWNLOADED
        )
        failed_count = sum(
            1 for t in current_tracks if t.status is TrackStatus.FAILED
        )
        self._report_user_action(
            translate(
                "ApplicationController",
                "Download run for {username} finished: "
                "{downloaded_count}/{count} tracks downloaded, {failed_count} failed.",
                count=len(current_tracks),
                username=username,
                downloaded_count=downloaded_count,
                failed_count=failed_count,
            )
        )
        LOGGER.info("Loaded %s downloaded tracks into UI for %s", len(current_tracks), username)
        if self._pending_play_cache_key:
            self._play_prepared_track(self._pending_play_cache_key)
            return
        if self._pending_retry_cache_key:
            self._pending_retry_cache_key = None
            return
        if (
            was_bulk
            and not stop_was_requested
            and self._has_download_candidates(current_tracks)
        ):
            self._start_automatic_download(username)

    def _handle_worker_error(self, worker: WorkflowWorker, message: str) -> None:
        LOGGER.error("Worker error: %s", message)
        if isinstance(worker, FetchLovedTracksWorker):
            self._active_fetch_worker = None
            self._fetch_paused = False
            self._started_incremental_lookup_for_fetch = False
            self.window.set_fetch_control_state(active=False, paused=False)
        if isinstance(worker, DownloadTracksWorker):
            self._download_worker_active = False
            self._download_stop_requested = False
            self.window.set_download_active(False)
        self.window.append_feedback(message)
        self.window.set_progress(0, translate("ApplicationController", "Failed"))

    def _update_track_by_cache_key(self, track: Track) -> None:
        for row, visible_track in enumerate(self.window.tracks()):
            if visible_track.cache_key == track.cache_key:
                self.window.update_track(row, track)
                return

    def _save_visible_tracks(self) -> None:
        username = self.window.username()
        if username:
            try:
                self.repository.merge_tracks(username, self.window.tracks())
            except StorageError as error:
                self._report_storage_error(
                    translate(
                        "ApplicationController",
                        "saving visible tracks for {username}",
                        username=username,
                    ),
                    error,
                )

    def _play_track(self, track: Track) -> None:
        if self._can_prepare_for_playback(track):
            self._prepare_selected_track_for_playback(track)
            return

        try:
            self.playback_service.play(track)
        except PlaybackError as error:
            self.window.append_feedback(str(error))
            return

        self.window.set_playing_track(track.cache_key)
        self.window.set_now_playing(track)
        self.window.set_playback_controls(active=True)
        self.window.set_playback_timeline(
            self.playback_service.position_ms(),
            self.playback_service.duration_ms(),
        )
        self._load_artist_image(track.artist)
        self._scrobble_submitted = False
        self._scrobble_seek_start_ms = 0
        self._playback_start_time = int(time.time())
        if self._scrobbling_service is not None:
            duration_s = self.playback_service.duration_ms() // 1000
            self._report_user_action(
                translate(
                    "ApplicationController",
                    "Updating Last.fm now-playing for {artist} - {title}.",
                    artist=track.artist,
                    title=track.title,
                )
            )
            self._submit_scrobbling_task(
                self._scrobbling_service.update_now_playing,
                track.artist,
                track.title,
                duration_s,
            )
        self._report_user_action(
            translate(
                "ApplicationController",
                "Playing {artist} - {title}.",
                artist=track.artist,
                title=track.title,
            )
        )

    def _load_artist_image(self, artist: str) -> None:
        if not self._artist_images_enabled:
            return

        cached_image = self._artist_image_cache.get(artist)
        if artist in self._artist_image_cache:
            self._show_artist_image(cached_image)
            return

        self.window.set_artist_image(None, None)
        worker = self.artist_image_worker_factory(artist, self.artist_info_client)
        self._run_artist_image_worker(worker)

    def _handle_artist_image_loaded(self, artist_image: object) -> None:
        if not isinstance(artist_image, ArtistImage):
            self._handle_artist_image_error(
                translate("ApplicationController", "Last.fm returned invalid artist image data.")
            )
            return

        self._artist_image_cache[artist_image.artist] = artist_image
        current_track = self.playback_service.current_track
        if current_track is None or current_track.artist != artist_image.artist:
            return
        self._show_artist_image(artist_image)

    def _handle_artist_image_error(self, message: str) -> None:
        LOGGER.warning("Artist image lookup failed: %s", message)

    def _show_artist_image(self, artist_image: ArtistImage | None) -> None:
        if artist_image is None:
            self.window.set_artist_image(None, None)
            return
        self.window.set_artist_image(artist_image.image_bytes, artist_image.page_url)

    def _can_prepare_for_playback(self, track: Track) -> bool:
        return (
            track.status is not TrackStatus.DOWNLOADED
            or not track.local_path
            or not Path(track.local_path).is_file()
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
        self._report_user_action(
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
        self._report_user_action(message)
        self.resolve_youtube_urls(username)

    def stop_downloads(self) -> None:
        """Pause the download manager and clear the active-download UI state."""

        self._download_worker_active = False
        self._download_stop_requested = True
        self.download_manager.stop()
        self.window.set_download_active(False)
        self._report_user_action(
            translate("ApplicationController", "Downloads stopped by user.")
        )

    def retry_track_download(self, cache_key: str) -> None:
        """Reset a track's state and trigger priority lookup + download for it."""

        username = self.window.username()
        if not username:
            self.window.append_feedback(
                translate(
                    "ApplicationController",
                    "Enter a Last.fm username before retrying a download.",
                )
            )
            return
        try:
            tracks = self.repository.load_tracks(username)
        except StorageError as error:
            self._report_storage_error(
                translate(
                    "ApplicationController",
                    "loading tracks for retry for {username}",
                    username=username,
                ),
                error,
            )
            return
        track = next((t for t in tracks if t.cache_key == cache_key), None)
        if track is None:
            return
        if track.status in {TrackStatus.NOT_FOUND, TrackStatus.FAILED}:
            reset_track = replace(track, status=TrackStatus.FETCHED, youtube_url=None, error=None)
            updated = [reset_track if t.cache_key == cache_key else t for t in tracks]
            try:
                self.repository.save_tracks(username, updated)
                self.repository.forget_lookup_cache_keys({cache_key})
            except StorageError as error:
                self._report_storage_error(
                    translate(
                        "ApplicationController",
                        "resetting track retry state for {username}",
                        username=username,
                    ),
                    error,
                )
                return
            self.window.set_tracks(updated)
            track = reset_track
        self._pending_retry_cache_key = cache_key
        self._report_user_action(
            translate(
                "ApplicationController",
                "Retrying download for {artist} - {title}.",
                artist=track.artist,
                title=track.title,
            )
        )
        if track.youtube_url:
            self._start_priority_download(username, cache_key)
        else:
            self.resolve_youtube_urls(username, priority_cache_key=cache_key, max_tracks=1)

    def _start_automatic_download(self, username: str) -> None:
        message = translate(
            "ApplicationController",
            "Starting automatic download queue for resolved tracks.",
        )
        self._report_user_action(message)
        self.download_tracks(username)

    def _start_priority_download(self, username: str, cache_key: str) -> None:
        message = translate(
            "ApplicationController",
            "Starting priority download for selected track.",
        )
        self._report_user_action(message)
        self.download_tracks(
            username,
            priority_cache_key=cache_key,
            max_downloads=1,
        )

    def _handle_track_ready_for_download(self, username: str, track: Track) -> None:
        try:
            merged_tracks = self.repository.merge_tracks(username, [track])
            self.repository.save_lookup_cache(merged_tracks)
        except StorageError as error:
            self._report_storage_error(
                translate(
                    "ApplicationController",
                    "saving ready track for {username}",
                    username=username,
                ),
                error,
            )
            return
        if self._pending_play_cache_key == track.cache_key:
            self._start_priority_download(username, track.cache_key)
            return
        if self._pending_retry_cache_key == track.cache_key:
            self._start_priority_download(username, track.cache_key)
            return
        if (
            not self._download_worker_active
            and not self._has_active_download_worker()
            and not self._has_active_lookup_worker()
        ):
            self._start_automatic_download(username)

    def _has_download_candidates(self, tracks: list[Track]) -> bool:
        return any(
            bool(track.youtube_url)
            and track.status not in {TrackStatus.DOWNLOADED, TrackStatus.NOT_FOUND}
            for track in tracks
        )

    def _has_active_download_worker(self) -> bool:
        return any(isinstance(worker, DownloadTracksWorker) for worker in self._active_workers)

    def _has_active_lookup_worker(self) -> bool:
        return any(isinstance(worker, LookupTracksWorker) for worker in self._active_workers)

    def _track_has_youtube_url(self, tracks: list[Track], cache_key: str) -> bool:
        return any(track.cache_key == cache_key and bool(track.youtube_url) for track in tracks)

    def _play_prepared_track(self, cache_key: str) -> None:
        for track in self.window.tracks():
            if track.cache_key != cache_key:
                continue
            if track.status is not TrackStatus.DOWNLOADED:
                return
            self._pending_play_cache_key = None
            self._play_track(track)
            return

    def _connect_playback_callbacks(self) -> None:
        if self._playback_callbacks_connected or self._playback_service is None:
            return
        self._playback_service.on_position_changed(self._handle_playback_position_changed)
        self._playback_service.on_duration_changed(self._handle_playback_duration_changed)
        self._playback_service.on_finished(self._handle_playback_finished)
        self._playback_callbacks_connected = True

    def _handle_playback_position_changed(self, position_ms: int) -> None:
        duration_ms = self.playback_service.duration_ms()
        self.window.set_playback_timeline(position_ms, duration_ms)
        self._maybe_scrobble(position_ms, duration_ms)

    def _maybe_scrobble(self, position_ms: int, duration_ms: int) -> None:
        elapsed_ms = position_ms - self._scrobble_seek_start_ms
        if (
            self._scrobbling_service is None
            or self._scrobble_submitted
            or self._playback_start_time is None
            or duration_ms <= 0
            or elapsed_ms < SCROBBLE_THRESHOLD * duration_ms
        ):
            return
        current_track = self.playback_service.current_track
        if current_track is None:
            return
        self._scrobble_submitted = True
        self._report_user_action(
            translate(
                "ApplicationController",
                "Submitting Last.fm scrobble for {artist} - {title}.",
                artist=current_track.artist,
                title=current_track.title,
            )
        )
        self._submit_scrobbling_task(
            self._scrobbling_service.scrobble,
            artist=current_track.artist,
            title=current_track.title,
            timestamp=self._playback_start_time,
            duration_seconds=duration_ms // 1000,
        )

    def _submit_scrobbling_task(self, task: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        self._scrobbling_tasks.submit(task, *args, **kwargs)

    def _handle_scrobbling_task_done(self, future: Future[Any]) -> None:
        self._scrobbling_tasks.handle_task_done(future)

    def _wait_for_scrobbling_tasks(self) -> None:
        self._scrobbling_tasks.wait(timeout=5)

    def _handle_playback_duration_changed(self, duration_ms: int) -> None:
        self.window.set_playback_timeline(self.playback_service.position_ms(), duration_ms)

    def _handle_playback_finished(self) -> None:
        finished_track = self.playback_service.finish_current()
        if finished_track is None:
            return

        self.window.set_playing_track(None)
        self.window.set_now_playing(None)
        self.window.set_artist_image(None, None)
        self.window.reset_playback_timeline()
        self.window.set_playback_controls(active=False)
        self._scrobble_submitted = False
        self._playback_start_time = None
        self._report_user_action(
            translate(
                "ApplicationController",
                "Finished playback for {artist} - {title}.",
                artist=finished_track.artist,
                title=finished_track.title,
            )
        )
        next_track = self._next_playback_track(finished_track.cache_key)
        if next_track is None:
            self._report_user_action(
                translate("ApplicationController", "Playback finished.")
            )
            return

        self._continue_playback_with(next_track)

    def _continue_playback_from(self, cache_key: str) -> None:
        next_track = self._next_playback_track(cache_key)
        if next_track is None:
            self._report_user_action(
                translate("ApplicationController", "Playback finished.")
            )
            return

        self._continue_playback_with(next_track)

    def _continue_playback_with(self, next_track: tuple[int, Track]) -> None:
        next_row, track = next_track
        self.window.select_track_row(next_row)
        if self.window.randomize_playback():
            self._report_user_action(
                translate(
                    "ApplicationController",
                    "Continuing with random track: {artist} - {title}.",
                    artist=track.artist,
                    title=track.title,
                )
            )
            self._play_track(track)
            return

        self._report_user_action(
            translate(
                "ApplicationController",
                "Continuing with next track: {artist} - {title}.",
                artist=track.artist,
                title=track.title,
            )
        )
        self._play_track(track)

    def _next_playback_track(self, finished_cache_key: str) -> tuple[int, Track] | None:
        if self.window.randomize_playback():
            return self.window.random_track_excluding(finished_cache_key, self._random.choice)
        return self.window.next_track_after(finished_cache_key)

    def _complete_worker_run(self) -> None:
        self._running_worker_count = max(0, self._running_worker_count - 1)
        if self._running_worker_count == 0:
            self.window.set_workflow_enabled(True)
            self.window.set_fetch_control_state(active=False, paused=False)
            self._report_user_action(
                translate(
                    "ApplicationController",
                    "All background work is finished; controls are enabled again.",
                )
            )

    def _forget_thread(self, thread: QThread) -> None:
        if thread in self._active_threads:
            self._active_threads.remove(thread)
        LOGGER.info("Thread finished; active_threads=%d", len(self._active_threads))

    def _forget_worker(self, worker: WorkflowWorker) -> None:
        if worker is self._active_fetch_worker:
            self._active_fetch_worker = None
            self._fetch_paused = False
        if worker in self._active_workers:
            self._active_workers.remove(worker)
        LOGGER.info("Worker released; active_workers=%d", len(self._active_workers))

    def _forget_artist_image_worker(self, worker: ArtistImageWorker) -> None:
        if worker in self._active_artist_image_workers:
            self._active_artist_image_workers.remove(worker)
        LOGGER.info(
            "Artist image worker released; active_artist_image_workers=%d",
            len(self._active_artist_image_workers),
        )

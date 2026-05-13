from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path

from PyQt6.QtCore import QObject, QThread, QUrl
from PyQt6.QtGui import QDesktopServices

from my_lastfm_player.app_credentials import (
    LASTFM_API_KEY_ENV,
    LASTFM_API_SECRET_ENV,
    lastfm_api_credentials,
)
from my_lastfm_player.dependencies import DependencyCheckResult, check_external_dependencies
from my_lastfm_player.download import DownloadManager
from my_lastfm_player.i18n import translate
from my_lastfm_player.lastfm import LastFmError, LastFmLovedTracksScraper
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.playback import PlaybackError, PlaybackService
from my_lastfm_player.scrobbling import SCROBBLE_THRESHOLD, ScrobblingService
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
        self._pending_retry_cache_key: str | None = None
        self._active_fetch_worker: FetchLovedTracksWorker | None = None
        self._fetch_paused = False
        self._started_incremental_lookup_for_fetch = False
        self._download_worker_active = False
        self._download_stop_requested = False
        self._playback_callbacks_connected = False
        self._scrobbling_service: ScrobblingService | None = None
        self._scrobble_submitted = False
        self._scrobble_seek_start_ms: int = 0
        self._playback_start_time: int | None = None

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
        self.window.download_stop_requested.connect(self.stop_downloads)
        self.window.retry_download_requested.connect(self.retry_track_download)
        self.window.play_requested.connect(self.play_selected_track)
        self.window.pause_requested.connect(self.pause_playback)
        self.window.stop_requested.connect(self.stop_playback)
        self.window.seek_requested.connect(self.seek_playback)
        self.window.language_changed.connect(self.check_dependencies)
        self.window.preferences_requested.connect(self._show_preferences)
        self.window.file_cache_requested.connect(self.open_file_cache)
        self._init_scrobbling()
        self._apply_ytdlp_settings()
        self.check_dependencies()

    def _report_user_action(self, message: str) -> None:
        LOGGER.info("User action: %s", message)
        self.window.append_feedback(message)

    def load_cached_tracks_for_entered_username(self, *, verify_online_count: bool = False) -> bool:
        """Load locally stored tracks for the entered username when available."""

        username = self.window.username()
        if not username:
            return False

        tracks = self.repository.load_tracks(username)
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
                    "Found {count} cached tracks for {username}; "
                    "checking Last.fm before using them.",
                    count=cached_count,
                    username=username,
                )
            )
        if verify_online_count and not self._cached_track_count_matches_lastfm(
            username,
            cached_count,
        ):
            return False

        tracks = self.repository.mark_cached_downloads(
            self.repository.mark_cached_lookups(tracks)
        )
        self.repository.save_tracks(username, tracks)
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

    def _cached_track_count_matches_lastfm(self, username: str, cached_count: int) -> bool:
        try:
            online_count = self.scraper.fetch_loved_track_count(username)
        except LastFmError as error:
            self._report_cache_status(
                translate(
                    "ApplicationController",
                    "Could not verify Last.fm loved-track count for {username}; "
                    "using {count} cached tracks: {error}",
                    username=username,
                    count=cached_count,
                    error=error,
                )
            )
            return True

        if online_count is None:
            self._report_cache_status(
                translate(
                    "ApplicationController",
                    "Could not read Last.fm loved-track count for {username}; "
                    "fetching fresh data instead of trusting {count} cached tracks.",
                    username=username,
                    count=cached_count,
                )
            )
            return False

        if online_count == cached_count:
            self._report_cache_status(
                translate(
                    "ApplicationController",
                    "Last.fm reports {online_count} loved tracks for {username}; "
                    "cached track count matches.",
                    username=username,
                    online_count=online_count,
                )
            )
            return True

        self._report_cache_status(
            translate(
                "ApplicationController",
                "Last.fm reports {online_count} loved tracks for {username}, "
                "but the cache has {cached_count}; fetching fresh data.",
                username=username,
                online_count=online_count,
                cached_count=cached_count,
            )
        )
        return False

    def _report_cache_status(self, message: str) -> None:
        self._report_user_action(message)

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
        """Open the local downloaded-track cache with the system file manager."""

        cache_dir = self.repository.downloads_dir
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            LOGGER.exception("Could not create file cache directory %s", cache_dir)
            self.window.append_feedback(
                translate(
                    "ApplicationController",
                    "Could not open file cache: {error}",
                    error=error,
                )
            )
            return

        if QDesktopServices.openUrl(QUrl.fromLocalFile(str(cache_dir))):
            self._report_user_action(
                translate(
                    "ApplicationController",
                    "Opened file cache: {path}",
                    path=cache_dir,
                )
            )
            return

        self.window.append_feedback(
            translate(
                "ApplicationController",
                "Could not open file cache: {path}",
                path=cache_dir,
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
            scrobbling_enabled=bool(creds.get("scrobbling_enabled", True)),
        )
        if self._scrobbling_service.session_key:
            if self._scrobbling_service.try_connect():
                self._report_user_action(
                    translate(
                        "ApplicationController",
                        "Connected Last.fm scrobbling as {username}.",
                        username=self._scrobbling_service.username,
                    )
                )
            else:
                self._report_user_action(
                    translate(
                        "ApplicationController",
                        "Stored Last.fm session key could not be verified; "
                        "scrobbling remains disconnected.",
                    )
                )

    def _show_preferences(self) -> None:
        from my_lastfm_player.ui.preferences_dialog import PreferencesDialog  # noqa: PLC0415

        self._report_user_action(translate("ApplicationController", "Opening preferences."))
        dialog = PreferencesDialog(self.window, self._scrobbling_service)
        dialog.exec()
        self._save_scrobbling_credentials()
        self._apply_ytdlp_settings()

    def _apply_ytdlp_settings(self) -> None:
        from my_lastfm_player.settings import AppSettings  # noqa: PLC0415

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
        self.repository.save_credentials(self._scrobbling_service.credentials_dict())
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

        LOGGER.info("Fetch requested for Last.fm user %s", username)
        print(f"[myLastFmPlayer] UI fetch requested for Last.fm user {username}", flush=True)
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
        worker = self.fetch_worker_factory(username, self.scraper, self.repository)
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
        print(f"[myLastFmPlayer] Starting YouTube lookup for {username}", flush=True)
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
            self.window.append_feedback(
                translate("ApplicationController", "Select a downloaded track before playing.")
            )
            return

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
        self.window.reset_playback_timeline()
        self.window.set_playback_controls(active=False)
        self._scrobble_submitted = False
        self._playback_start_time = None
        self._report_user_action(translate("ApplicationController", "Playback stopped."))

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
        print(
            f"[myLastFmPlayer] UI loaded {len(tracks)} fetched tracks for {username}",
            flush=True,
        )
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
            self.repository.merge_tracks(username, tracks)
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
        resolved_count = sum(
            1 for track in tracks if isinstance(track, Track) and track.youtube_url
        )
        not_found_count = sum(
            1
            for track in tracks
            if isinstance(track, Track) and track.status is TrackStatus.NOT_FOUND
        )
        self._report_user_action(
            translate(
                "ApplicationController",
                "Resolved YouTube URLs for {resolved_count}/{count} tracks; "
                "{not_found_count} were not found.",
                count=len(tracks),
                resolved_count=resolved_count,
                not_found_count=not_found_count,
            )
        )
        LOGGER.info("Loaded %s resolved tracks into UI for %s", len(tracks), username)
        if self._pending_play_cache_key and self._track_has_youtube_url(
            tracks,
            self._pending_play_cache_key,
        ):
            self._start_priority_download(username, self._pending_play_cache_key)
        elif self._pending_retry_cache_key and self._track_has_youtube_url(
            tracks,
            self._pending_retry_cache_key,
        ):
            self._start_priority_download(username, self._pending_retry_cache_key)
        elif self._has_download_candidates(tracks) and not self._download_worker_active:
            self._start_automatic_download(username)
        elif not self._has_download_candidates(tracks):
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

        self.window.set_tracks(tracks)
        downloaded_count = sum(
            1
            for track in tracks
            if isinstance(track, Track) and track.status is TrackStatus.DOWNLOADED
        )
        failed_count = sum(
            1
            for track in tracks
            if isinstance(track, Track) and track.status is TrackStatus.FAILED
        )
        self._report_user_action(
            translate(
                "ApplicationController",
                "Download run for {username} finished: "
                "{downloaded_count}/{count} tracks downloaded, {failed_count} failed.",
                count=len(tracks),
                username=username,
                downloaded_count=downloaded_count,
                failed_count=failed_count,
            )
        )
        LOGGER.info("Loaded %s downloaded tracks into UI for %s", len(tracks), username)
        if self._pending_play_cache_key:
            self._play_prepared_track(self._pending_play_cache_key)
            return
        if self._pending_retry_cache_key:
            self._pending_retry_cache_key = None
            return
        if (
            was_bulk
            and not stop_was_requested
            and self._has_download_candidates([t for t in tracks if isinstance(t, Track)])
        ):
            self._start_automatic_download(username)

    def _handle_worker_error(self, message: str) -> None:
        LOGGER.error("Worker error: %s", message)
        print(f"[myLastFmPlayer] Worker error shown in UI: {message}", flush=True)
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
            self.repository.save_tracks(username, self.window.tracks())

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
            self._scrobbling_service.update_now_playing(track.artist, track.title, duration_s)
        self._report_user_action(
            translate(
                "ApplicationController",
                "Playing {artist} - {title}.",
                artist=track.artist,
                title=track.title,
            )
        )

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
        self.download_manager.pause()
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
        tracks = self.repository.load_tracks(username)
        track = next((t for t in tracks if t.cache_key == cache_key), None)
        if track is None:
            return
        if track.status in {TrackStatus.NOT_FOUND, TrackStatus.FAILED}:
            reset_track = replace(track, status=TrackStatus.FETCHED, youtube_url=None, error=None)
            updated = [reset_track if t.cache_key == cache_key else t for t in tracks]
            self.repository.save_tracks(username, updated)
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

    def _has_download_candidates(self, tracks: list[Track]) -> bool:
        return any(
            bool(track.youtube_url)
            and track.status not in {TrackStatus.DOWNLOADED, TrackStatus.NOT_FOUND}
            for track in tracks
        )

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
        self._scrobbling_service.scrobble(
            artist=current_track.artist,
            title=current_track.title,
            timestamp=self._playback_start_time,
            duration_seconds=duration_ms // 1000,
        )

    def _handle_playback_duration_changed(self, duration_ms: int) -> None:
        self.window.set_playback_timeline(self.playback_service.position_ms(), duration_ms)

    def _handle_playback_finished(self) -> None:
        finished_track = self.playback_service.finish_current()
        if finished_track is None:
            return

        self.window.set_playing_track(None)
        self.window.set_now_playing(None)
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
        next_track = self.window.next_track_after(finished_track.cache_key)
        if next_track is None:
            self._report_user_action(
                translate("ApplicationController", "Playback finished.")
            )
            return

        next_row, track = next_track
        self.window.select_track_row(next_row)
        self._report_user_action(
            translate(
                "ApplicationController",
                "Continuing with next track: {artist} - {title}.",
                artist=track.artist,
                title=track.title,
            )
        )
        self._play_track(track)

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

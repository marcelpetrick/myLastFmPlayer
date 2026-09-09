# pylint: disable=too-many-lines  # god object; tracked for future decomposition
from __future__ import annotations

import logging
import random
import time
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path
from threading import Thread

from PyQt6.QtCore import QObject, QProcess, QThread, QUrl
from PyQt6.QtGui import QDesktopServices

from my_lastfm_player.app_credentials import (
    LASTFM_API_KEY_ENV,
    LASTFM_API_SECRET_ENV,
    lastfm_api_credentials,
)
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
from my_lastfm_player.storage import JsonTrackRepository, merge_track_updates
from my_lastfm_player.ui.main_window import MainWindow
from my_lastfm_player.workers import (
    ArtistImageWorker,
    BackgroundCallWorker,
    DownloadTracksWorker,
    FetchLovedTracksWorker,
    LookupTracksWorker,
)
from my_lastfm_player.youtube import YouTubeResolver
from my_lastfm_player.youtube_work import YouTubeWorkLimiter

LOGGER = logging.getLogger(__name__)

DependencyChecker = Callable[[], DependencyCheckResult]
FetchWorkerFactory = Callable[
    [str, LastFmLovedTracksScraper, JsonTrackRepository, int | None],
    FetchLovedTracksWorker,
]
LookupWorkerFactory = Callable[
    [str, YouTubeResolver, JsonTrackRepository, str | None, int | None, int],
    LookupTracksWorker,
]
DownloadWorkerFactory = Callable[
    [str, DownloadManager, JsonTrackRepository, int, str | None, int | None],
    DownloadTracksWorker,
]
ArtistImageWorkerFactory = Callable[[str, LastFmArtistInfoClient], ArtistImageWorker]
WorkflowWorker = FetchLovedTracksWorker | LookupTracksWorker | DownloadTracksWorker
BackgroundResultCallback = Callable[[object], None]
BackgroundErrorCallback = Callable[[Exception], None]


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
    ) -> None:
        super().__init__(window)
        self.window = window
        self.repository = repository or JsonTrackRepository()
        self.scraper = scraper or LastFmLovedTracksScraper()
        self._youtube_work_limiter = YouTubeWorkLimiter(AppSettings().download_concurrency())
        self.youtube_resolver = youtube_resolver or YouTubeResolver(
            work_limiter=self._youtube_work_limiter
        )
        self.download_manager = download_manager or DownloadManager(
            work_limiter=self._youtube_work_limiter
        )
        self.youtube_resolver.work_limiter = self._youtube_work_limiter
        self.download_manager.work_limiter = self._youtube_work_limiter
        self._playback_service = playback_service
        self.artist_info_client = artist_info_client or LastFmArtistInfoClient()
        self._artist_images_enabled = (
            playback_service is None
            or artist_info_client is not None
            or artist_image_worker_factory is not ArtistImageWorker
        )
        self.dependency_checker = dependency_checker
        self.fetch_worker_factory = fetch_worker_factory
        self.lookup_worker_factory = lookup_worker_factory
        self.download_worker_factory = download_worker_factory
        self.artist_image_worker_factory = artist_image_worker_factory
        self._active_threads: list[QThread] = []
        self._active_workers: list[WorkflowWorker] = []
        self._active_artist_image_workers: list[ArtistImageWorker] = []
        self._active_background_workers: list[BackgroundCallWorker] = []
        self._background_callbacks: dict[
            BackgroundCallWorker,
            tuple[BackgroundResultCallback | None, BackgroundErrorCallback | None],
        ] = {}
        self._running_worker_count = 0
        self._pending_play_cache_key: str | None = None
        self._pending_retry_cache_key: str | None = None
        self._workflow_username: str | None = self.window.username() or None
        self._workflow_generation = 0
        self._username_edit_active = False
        self._worker_generations: dict[WorkflowWorker, int] = {}
        self._pending_lookup_users: set[str] = set()
        self._active_fetch_worker: FetchLovedTracksWorker | None = None
        self._active_fetch_preflight: BackgroundCallWorker | None = None
        self._fetch_preflight_username: str | None = None
        self._fetch_paused = False
        self._started_incremental_lookup_for_fetch = False
        self._download_worker_active = False
        self._youtube_stop_requested = False
        self._playback_callbacks_connected = False
        self._scrobbling_service: ScrobblingService | None = None
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
        self.window.username_input.textEdited.connect(self._handle_username_text_edited)
        self.window.username_input.editingFinished.connect(
            self.load_cached_tracks_for_entered_username
        )
        self.window.fetch_pause_requested.connect(self.toggle_fetch_pause)
        self.window.fetch_stop_requested.connect(self.stop_fetch)
        self.window._youtube_resume_requested.connect(self._resume_youtube_work)
        self.window._youtube_stop_requested.connect(self.stop_youtube_work)
        self.window.retry_download_requested.connect(self.retry_track_download)
        self.window.play_requested.connect(self.play_selected_track)
        self.window.pause_requested.connect(self.pause_playback)
        self.window.stop_requested.connect(self.stop_playback)
        self.window.next_requested.connect(self.play_next_track)
        self.window.seek_requested.connect(self.seek_playback)
        self.window.artist_page_requested.connect(self.open_artist_page)
        self.window.language_changed.connect(self.check_dependencies)
        self.window.randomize_playback_changed.connect(AppSettings().set_randomize_playback)
        self.window.volume_changed.connect(self.set_volume)
        self.window.mute_toggled.connect(self.set_muted)
        self.window.preferences_requested.connect(self._show_preferences)
        self.window.file_cache_requested.connect(self.open_file_cache)
        self.window.quit_requested.connect(self._handle_quit)
        self._init_scrobbling()
        self._apply_ytdlp_settings()
        self.check_dependencies()
        self._recheck_stuck_tracks()

    def _recheck_stuck_tracks(self) -> None:
        """Re-check tracks earlier runs gave up on and let the normal queues take over.

        A NOT_FOUND verdict and a FAILED download both come from a YouTube state that is
        usually temporary (search gating, a client that serves no formats), so each start
        gives them one more pass instead of leaving them stuck for good.
        """

        username = self.window.username()
        if not username:
            return

        tracks = self.repository.load_tracks(username)
        missing_count = sum(1 for track in tracks if track.status is TrackStatus.NOT_FOUND)
        failed_count = sum(
            1 for track in tracks if track.status in {TrackStatus.FAILED, TrackStatus.LOOKUP_FAILED}
        )
        if not missing_count and not failed_count:
            return

        if missing_count:
            self.repository.clear_not_found_lookups()
            tracks = [
                replace(
                    track,
                    status=TrackStatus.FETCHED,
                    youtube_url=None,
                    retry_count=0,
                    error=None,
                )
                if track.status is TrackStatus.NOT_FOUND
                else track
                for track in tracks
            ]
        tracks = [
            replace(
                track,
                status=TrackStatus.QUEUED if track.youtube_url else TrackStatus.FETCHED,
                error=None,
            )
            if track.status in {TrackStatus.FAILED, TrackStatus.LOOKUP_FAILED}
            else track
            for track in tracks
        ]
        self.repository.save_tracks(username, tracks)
        self.window.set_tracks(tracks)
        self._report_user_action(
            translate(
                "ApplicationController",
                "Re-checking {missing} not-found and {failed} failed tracks from the last run.",
                missing=missing_count,
                failed=failed_count,
            )
        )
        if missing_count or any(
            track.status is TrackStatus.FETCHED and not track.youtube_url for track in tracks
        ):
            self.resolve_youtube_urls(username)
        else:
            self.download_tracks(username)

    def _handle_quit(self) -> None:
        if not AppSettings().keep_data_on_quit():
            self.repository.wipe()

    def _report_user_action(self, message: str) -> None:
        LOGGER.info("User action: %s", message)
        self.window.append_feedback(message)

    def _handle_username_text_edited(self, text: str) -> None:
        """Retire work for the previous user as soon as a different name is entered."""

        username = text.strip()
        previous_username = self._workflow_username
        if not self._username_edit_active and username == previous_username:
            return
        if not self._username_edit_active:
            self._workflow_generation += 1
            self._username_edit_active = True
            self.window.reset_workflow_progress()
        if previous_username:
            self._cancel_work_for_username(previous_username)
        # Typed text is not a committed identity. Ignore all stale worker signals until
        # editing finishes or Fetch explicitly commits the complete value.
        self._workflow_username = None
        self._pending_play_cache_key = None
        self._pending_retry_cache_key = None
        self.window.set_tracks([])
        self.window.set_fetch_control_state(active=False, paused=False)
        self.window.set_workflow_enabled(True)

    def _cancel_work_for_username(self, username: str) -> None:
        """Cooperatively cancel queued work belonging to ``username``."""

        cancelled = False
        if self._active_fetch_preflight is not None and self._fetch_preflight_username == username:
            self._active_fetch_preflight.cancel()
            self._active_fetch_preflight = None
            self._fetch_preflight_username = None
            cancelled = True
        for worker in tuple(self._active_workers):
            if getattr(worker, "username", None) != username:
                continue
            if isinstance(worker, FetchLovedTracksWorker):
                worker.stop_fetch()
            elif isinstance(worker, LookupTracksWorker):
                worker.stop_lookup()
            elif isinstance(worker, DownloadTracksWorker):
                worker.stop_download()
            cancelled = True
        if self._active_fetch_worker is not None and (
            getattr(self._active_fetch_worker, "username", username) == username
        ):
            self._active_fetch_worker.stop_fetch()
            self._active_fetch_worker = None
        self._fetch_paused = False
        self._started_incremental_lookup_for_fetch = False
        self._pending_lookup_users.discard(username)
        self._download_worker_active = False
        self._youtube_stop_requested = False
        self.window.set_youtube_work_state(active=False)
        if cancelled:
            self._report_user_action(
                translate(
                    "ApplicationController",
                    "Stopping background work for {username}; completed items remain saved.",
                    username=username,
                )
            )

    def _has_active_worker_for_username(self, username: str) -> bool:
        return (
            self._active_fetch_preflight is not None and self._fetch_preflight_username == username
        ) or any(
            getattr(worker, "username", None) == username
            and self._worker_generations.get(worker, self._workflow_generation)
            == self._workflow_generation
            for worker in self._active_workers
        )

    def _is_current_workflow_username(self, username: str) -> bool:
        return username == self._workflow_username

    def _is_current_worker_context(self, username: str, generation: int) -> bool:
        return generation == self._workflow_generation and self._is_current_workflow_username(
            username
        )

    def _commit_workflow_username(self, username: str) -> None:
        previous_username = self._workflow_username
        if not self._username_edit_active and previous_username != username:
            self._workflow_generation += 1
            self.window.reset_workflow_progress()
            if previous_username:
                self._cancel_work_for_username(previous_username)
        self._workflow_username = username
        self._username_edit_active = False

    def load_cached_tracks_for_entered_username(self) -> bool:
        """Load locally stored tracks for the entered username when available."""

        username = self.window.username()
        if not username:
            return False
        self._commit_workflow_username(username)
        if self._active_fetch_worker is not None or self._active_fetch_preflight is not None:
            LOGGER.info("Skipped cached-track load because a fresh fetch is active")
            return False

        tracks = self.repository.load_tracks(username)
        if not tracks:
            return False

        tracks = self.repository.mark_cached_downloads(self.repository.mark_cached_lookups(tracks))
        tracks = self.repository.merge_tracks(username, tracks)
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
        """Open the application data folder (tracks, cache, credentials) in the file manager."""

        data_dir = self.repository.data_dir
        try:
            data_dir.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            LOGGER.exception("Could not create data directory %s", data_dir)
            self.window.append_error(
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

        self.window.append_error(
            translate(
                "ApplicationController",
                "Could not open data folder: {path}",
                path=data_dir,
            )
        )

    def open_artist_page(self, url: str) -> None:
        """Open an artist Last.fm page in a Firefox private window."""

        if not _open_firefox_private_window(url):
            self.window.append_error(
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
            self._submit_background_call(
                self._scrobbling_service.try_connect,
                self._handle_scrobbling_connect_result,
                self._handle_scrobbling_connect_error,
            )

    def _handle_scrobbling_connect_result(self, connected: object) -> None:
        if connected and self._scrobbling_service is not None:
            self._report_user_action(
                translate(
                    "ApplicationController",
                    "Connected Last.fm scrobbling as {username}.",
                    username=self._scrobbling_service.username,
                )
            )
            return
        self._report_user_action(
            translate(
                "ApplicationController",
                "Stored Last.fm session key could not be verified; "
                "scrobbling remains disconnected.",
            )
        )

    def _handle_scrobbling_connect_error(self, error: Exception) -> None:
        LOGGER.warning("Stored Last.fm session verification failed: %s", error)
        self._handle_scrobbling_connect_result(False)

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

        self._commit_workflow_username(username)
        if self._has_active_worker_for_username(username):
            self._report_user_action(
                translate(
                    "ApplicationController",
                    "Background work is already running for {username}.",
                    username=username,
                )
            )
            return
        self.window.reset_workflow_progress()
        self._youtube_stop_requested = False
        cached_tracks = self.repository.load_tracks(username)
        if cached_tracks:
            self._report_user_action(
                translate(
                    "ApplicationController",
                    "Found {count} cached tracks for {username}; "
                    "checking Last.fm before using them.",
                    count=len(cached_tracks),
                    username=username,
                )
            )
        self.window.set_workflow_enabled(False)
        self.window.set_fetch_control_state(True, can_pause=False)
        self.window.set_progress(0, translate("ApplicationController", "Starting fetch"))
        generation = self._workflow_generation
        worker = BackgroundCallWorker(lambda: self.scraper.fetch_loved_track_count(username))
        self._active_fetch_preflight = worker
        self._fetch_preflight_username = username
        self._start_background_worker(
            worker,
            lambda count: self._handle_fetch_preflight_result(
                username, generation, cached_tracks, count
            ),
            lambda error: self._handle_fetch_preflight_error(
                username, generation, cached_tracks, error
            ),
        )

    def _handle_fetch_preflight_result(
        self,
        username: str,
        generation: int,
        cached_tracks: list[Track],
        result: object,
    ) -> None:
        if not self._is_current_worker_context(username, generation):
            return
        self._active_fetch_preflight = None
        self._fetch_preflight_username = None
        online_count = result if isinstance(result, int) else None
        if cached_tracks and self._cached_count_matches_value(
            username, len(cached_tracks), online_count
        ):
            self._load_cached_tracks(username, cached_tracks)
            self.window.set_fetch_control_state(False)
            self.window.set_progress(
                100,
                translate("ApplicationController", "Loaded cached tracks"),
            )
            self.window.set_workflow_enabled(True)
            tracks = self.window.tracks()
            if tracks:
                self._start_automatic_lookup(username, len(tracks))
            return
        self._start_fresh_fetch(username, online_count)

    def _handle_fetch_preflight_error(
        self,
        username: str,
        generation: int,
        cached_tracks: list[Track],
        error: Exception,
    ) -> None:
        if not self._is_current_worker_context(username, generation):
            return
        self._active_fetch_preflight = None
        self._fetch_preflight_username = None
        if cached_tracks:
            self._report_cache_status(
                translate(
                    "ApplicationController",
                    "Could not verify Last.fm loved-track count for {username}; "
                    "using {count} cached tracks: {error}",
                    username=username,
                    count=len(cached_tracks),
                    error=error,
                )
            )
            self._load_cached_tracks(username, cached_tracks)
            self.window.set_fetch_control_state(False)
            self.window.set_progress(
                100,
                translate("ApplicationController", "Loaded cached tracks"),
            )
            self.window.set_workflow_enabled(True)
            tracks = self.window.tracks()
            if tracks:
                self._start_automatic_lookup(username, len(tracks))
            return
        self.window.set_fetch_control_state(False)
        self.window.set_workflow_enabled(True)
        self._report_user_action(
            translate(
                "ApplicationController",
                "Could not reach Last.fm for {username}: {error}",
                username=username,
                error=error,
            )
        )

    def _cached_count_matches_value(
        self, username: str, cached_count: int, online_count: int | None
    ) -> bool:
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

    def _load_cached_tracks(self, username: str, tracks: list[Track]) -> None:
        tracks = self.repository.mark_cached_downloads(self.repository.mark_cached_lookups(tracks))
        tracks = self.repository.merge_tracks(username, tracks)
        self.window.set_tracks(tracks)
        self._report_user_action(
            translate(
                "ApplicationController",
                "Loaded {count} cached tracks for {username}; skipped Last.fm fetch.",
                count=len(tracks),
                username=username,
            )
        )

    def _start_fresh_fetch(self, username: str, expected_count: int | None) -> None:
        """Launch the paginated worker after asynchronous preflight succeeds."""

        LOGGER.info(
            "Fresh fetch requested for Last.fm user %s (expected=%s)", username, expected_count
        )
        if expected_count is not None:
            self._report_user_action(
                translate(
                    "ApplicationController",
                    "Starting fresh Last.fm fetch for {username}; {count} tracks expected.",
                    username=username,
                    count=expected_count,
                )
            )
        else:
            self._report_user_action(
                translate(
                    "ApplicationController",
                    "Starting fresh Last.fm fetch for {username}.",
                    username=username,
                )
            )
        self.window.set_fetch_control_state(True, can_pause=True)
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
            self._report_user_action(translate("ApplicationController", "Fetch resumed."))
            return
        self._active_fetch_worker.pause_fetch()
        self._fetch_paused = True
        self.window.set_fetch_control_state(active=True, paused=True)
        self._report_user_action(translate("ApplicationController", "Fetch paused."))

    def stop_fetch(self) -> None:
        """Request cancellation of the active Last.fm fetch worker."""

        if self._active_fetch_preflight is not None:
            self._active_fetch_preflight.cancel()
            self._active_fetch_preflight = None
            self._fetch_preflight_username = None
            self.window.set_fetch_control_state(False)
            self.window.set_workflow_enabled(True)
            self._report_user_action(translate("ApplicationController", "Stopping fetch."))
            return
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
                "Starting YouTube lookup for {username}; priority={priority}, limit={limit}.",
                username=username,
                priority=priority_cache_key or translate("ApplicationController", "none"),
                limit=(
                    max_tracks
                    if max_tracks is not None
                    else translate("ApplicationController", "all")
                ),
            )
        )
        self.window.set_stage_progress(
            "lookup",
            0,
            translate("ApplicationController", "Starting YouTube lookup"),
        )
        worker = self.lookup_worker_factory(
            username,
            self.youtube_resolver,
            self.repository,
            priority_cache_key,
            max_tracks,
            AppSettings().download_concurrency(),
        )
        self._youtube_work_limiter.configure(AppSettings().download_concurrency())
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
                priority=priority_cache_key or translate("ApplicationController", "none"),
                limit=(
                    max_downloads
                    if max_downloads is not None
                    else translate("ApplicationController", "all")
                ),
            )
        )
        self._youtube_work_limiter.configure(concurrency)
        self.window.set_stage_progress(
            "download",
            0,
            translate("ApplicationController", "Starting downloads"),
        )
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

    def play_selected_track(self) -> None:
        """Play the selected track or prepare it for playback when needed."""

        if self.playback_service.is_paused():
            self.pause_playback()
            return
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
                self.window.append_error(str(error))
                return
            self._report_user_action(translate("ApplicationController", "Playback resumed."))
            self.window.set_playback_controls(active=True, paused=False)
        else:
            try:
                self.playback_service.pause()
            except PlaybackError as error:
                self.window.append_error(str(error))
                return
            self._report_user_action(translate("ApplicationController", "Playback paused."))
            self.window.set_playback_controls(active=True, paused=True)

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

    def set_volume(self, volume_percent: int) -> None:
        """Apply and persist the playback volume."""

        self.playback_service.set_volume(volume_percent)
        AppSettings().set_volume_percent(volume_percent)

    def set_muted(self, muted: bool) -> None:
        """Apply and persist the mute state."""

        self.playback_service.set_muted(muted)
        AppSettings().set_muted(muted)

    def _apply_audio_settings(self) -> None:
        self.playback_service.set_volume(self.window.volume_percent())
        self.playback_service.set_muted(self.window.is_muted())

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
            self.window.append_error(str(error))
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
        worker_username = getattr(worker, "username", self._workflow_username) or ""
        worker_generation = self._workflow_generation
        progress_stage = self._worker_progress_stage(worker)
        self._worker_generations[worker] = worker_generation

        thread.started.connect(worker.run)
        worker.progress.connect(
            lambda value, label, username=worker_username, generation=worker_generation: (
                self._handle_worker_progress(username, value, label, progress_stage)
                if self._is_current_worker_context(username, generation)
                else None
            )
        )
        worker.error.connect(
            lambda message, username=worker_username, generation=worker_generation: (
                self._handle_worker_error_for(username, message, progress_stage)
                if self._is_current_worker_context(username, generation)
                else None
            )
        )
        if isinstance(worker, FetchLovedTracksWorker):
            worker.tracks_updated.connect(
                lambda username, tracks, generation=worker_generation: (
                    self._handle_tracks_updated(username, tracks)
                    if self._is_current_worker_context(username, generation)
                    else None
                )
            )
            worker.tracks_loaded.connect(
                lambda username, tracks, generation=worker_generation: (
                    self._handle_tracks_loaded(username, tracks)
                    if self._is_current_worker_context(username, generation)
                    else None
                )
            )
            worker.fetch_stopped.connect(
                lambda username, tracks, generation=worker_generation: (
                    self._handle_fetch_stopped(username, tracks)
                    if self._is_current_worker_context(username, generation)
                    else None
                )
            )
        if isinstance(worker, LookupTracksWorker):
            worker.track_updated.connect(
                lambda username, track, generation=worker_generation: (
                    self._handle_track_updated(username, track)
                    if self._is_current_worker_context(username, generation)
                    else None
                )
            )
            worker.tracks_resolved.connect(
                lambda username, tracks, generation=worker_generation: (
                    self._handle_tracks_resolved(username, tracks)
                    if self._is_current_worker_context(username, generation)
                    else None
                )
            )
        if isinstance(worker, DownloadTracksWorker):
            worker.track_updated.connect(
                lambda username, track, generation=worker_generation: (
                    self._handle_track_updated(username, track)
                    if self._is_current_worker_context(username, generation)
                    else None
                )
            )
            worker.tracks_downloaded.connect(
                lambda username, tracks, generation=worker_generation: (
                    self._handle_tracks_downloaded(username, tracks)
                    if self._is_current_worker_context(username, generation)
                    else None
                )
            )
        worker.finished.connect(self._complete_worker_run)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda: self._forget_thread(thread))
        thread.finished.connect(lambda worker=worker: self._forget_worker(worker))

        self._active_threads.append(thread)
        self._active_workers.append(worker)
        if isinstance(worker, (LookupTracksWorker, DownloadTracksWorker)):
            self.window.set_youtube_work_state(active=True)
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

    def _submit_background_call(
        self,
        operation: Callable[[], object],
        on_result: BackgroundResultCallback | None = None,
        on_error: BackgroundErrorCallback | None = None,
    ) -> BackgroundCallWorker:
        """Run a blocking service call without occupying the Qt UI thread."""

        worker = BackgroundCallWorker(operation)
        self._start_background_worker(worker, on_result, on_error)
        return worker

    def _start_background_worker(
        self,
        worker: BackgroundCallWorker,
        on_result: BackgroundResultCallback | None = None,
        on_error: BackgroundErrorCallback | None = None,
    ) -> None:
        """Register and start an already-created service-call worker."""

        self._background_callbacks[worker] = (on_result, on_error)
        worker.result.connect(self._handle_background_result)
        worker.failed.connect(self._handle_background_error)
        worker.finished.connect(self._forget_background_worker)
        self._active_background_workers.append(worker)
        Thread(
            target=worker.run,
            name="myLastFmPlayer-service-call",
            daemon=True,
        ).start()

    def _handle_background_result(self, worker: BackgroundCallWorker, result: object) -> None:
        callbacks = self._background_callbacks.get(worker)
        if callbacks is not None and callbacks[0] is not None and not worker.is_cancelled:
            callbacks[0](result)

    def _handle_background_error(self, worker: BackgroundCallWorker, error: Exception) -> None:
        callbacks = self._background_callbacks.get(worker)
        if callbacks is not None and callbacks[1] is not None and not worker.is_cancelled:
            callbacks[1](error)
            return
        LOGGER.warning("Background service call failed: %s", error)

    def _forget_background_worker(self, worker: BackgroundCallWorker) -> None:
        self._background_callbacks.pop(worker, None)
        if worker in self._active_background_workers:
            self._active_background_workers.remove(worker)
        if worker is self._active_fetch_preflight:
            self._active_fetch_preflight = None
            self._fetch_preflight_username = None

    def _handle_tracks_loaded(self, username: str, tracks: object) -> None:
        if not self._is_current_workflow_username(username):
            return
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
        self._active_fetch_worker = None
        self._fetch_paused = False
        self._started_incremental_lookup_for_fetch = False
        self.window.set_fetch_control_state(active=False, paused=False)
        LOGGER.info("Loaded %s fetched tracks into UI for %s", len(tracks), username)
        if self._has_lookup_candidates(tracks):
            self._ensure_automatic_lookup(username, len(tracks))

    def _handle_fetch_stopped(self, username: str, tracks: object) -> None:
        if not self._is_current_workflow_username(username):
            return
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
        if not self._is_current_workflow_username(username):
            return
        if not isinstance(tracks, list):
            self.window.append_feedback(
                translate(
                    "ApplicationController",
                    "Fetch for {username} returned invalid partial data.",
                    username=username,
                )
            )
            return

        merged_tracks = merge_track_updates(self.window.tracks(), tracks)
        self.window.set_tracks(merged_tracks)
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
        if self._has_lookup_candidates(merged_tracks):
            self._ensure_automatic_lookup(username, len(merged_tracks))

    def _handle_track_updated(self, username: str, track: object) -> None:
        if not self._is_current_workflow_username(username):
            return
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
        if not self._is_current_workflow_username(username):
            return
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
        current_tracks = self.repository.load_tracks(username)
        self.window.set_tracks(current_tracks)
        resolved_count = sum(1 for t in current_tracks if t.youtube_url)
        not_found_count = sum(1 for t in current_tracks if t.status is TrackStatus.NOT_FOUND)
        if self._youtube_stop_requested:
            self._report_user_action(
                translate(
                    "ApplicationController",
                    "YouTube work stopped; completed items remain saved.",
                )
            )
        else:
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
        if self._youtube_stop_requested:
            return
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
        elif self._has_download_candidates(current_tracks):
            self._ensure_automatic_download(username)
        elif not self._has_download_candidates(current_tracks):
            self._report_user_action(
                translate("ApplicationController", "No queued tracks are ready for download.")
            )

    def _handle_tracks_downloaded(self, username: str, tracks: object) -> None:
        if not self._is_current_workflow_username(username):
            return
        was_bulk = self._download_worker_active
        stop_was_requested = self._youtube_stop_requested
        self._download_worker_active = False
        self._youtube_stop_requested = stop_was_requested
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
        current_tracks = self.repository.load_tracks(username)
        self.window.set_tracks(current_tracks)
        downloaded_count = sum(1 for t in current_tracks if t.status is TrackStatus.DOWNLOADED)
        failed_count = sum(1 for t in current_tracks if t.status is TrackStatus.FAILED)
        if stop_was_requested:
            self._report_user_action(
                translate(
                    "ApplicationController",
                    "YouTube work stopped; completed items remain saved.",
                )
            )
        else:
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
        if was_bulk and not stop_was_requested and self._has_download_candidates(current_tracks):
            self._ensure_automatic_download(username)

    @staticmethod
    def _worker_progress_stage(worker: WorkflowWorker) -> str:
        if isinstance(worker, LookupTracksWorker):
            return "lookup"
        if isinstance(worker, DownloadTracksWorker):
            return "download"
        return "discovery"

    def _handle_worker_error(self, message: str, stage: str = "discovery") -> None:
        LOGGER.error("Worker error: %s", message)
        self.window.append_error(message)
        self.window.set_stage_progress(
            stage,
            0,
            translate("ApplicationController", "Failed"),
        )

    def _handle_worker_error_for(
        self, username: str, message: str, stage: str = "discovery"
    ) -> None:
        if self._is_current_workflow_username(username):
            self._handle_worker_error(message, stage)

    def _handle_worker_progress(
        self, username: str, value: int, label: str, stage: str = "discovery"
    ) -> None:
        if self._is_current_workflow_username(username):
            self.window.set_stage_progress(stage, value, label)

    def _update_track_by_cache_key(self, track: Track) -> None:
        for row, visible_track in enumerate(self.window.tracks()):
            if visible_track.cache_key == track.cache_key:
                self.window.update_track(row, track)
                return

    def _save_visible_tracks(self) -> None:
        username = self.window.username()
        if username:
            self.repository.merge_tracks(username, self.window.tracks())

    def _play_track(self, track: Track) -> None:
        if self._can_prepare_for_playback(track):
            self._prepare_selected_track_for_playback(track)
            return

        try:
            self.playback_service.play(track)
        except PlaybackError as error:
            self.window.append_error(str(error))
            return

        self._apply_audio_settings()
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
            service = self._scrobbling_service
            self._submit_background_call(
                lambda: service.update_now_playing(track.artist, track.title, duration_s)
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

        self.window.set_artist_image(None, None, artist)
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
        self.window.set_artist_image(
            artist_image.image_bytes,
            artist_image.page_url,
            artist_image.artist,
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
        self._youtube_stop_requested = False
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

    def _ensure_automatic_lookup(self, username: str, track_count: int) -> None:
        if self._youtube_stop_requested:
            return
        if self._has_active_lookup_worker(username):
            self._pending_lookup_users.add(username)
            return
        self._pending_lookup_users.discard(username)
        self._start_automatic_lookup(username, track_count)

    def stop_youtube_work(self) -> None:
        """Cancel current YouTube checks/downloads and retain completed items."""

        self._download_worker_active = False
        self._youtube_stop_requested = True
        username = self.window.username()
        stopped_worker = False
        for worker in tuple(self._active_workers):
            if worker.username != username:
                continue
            if isinstance(worker, LookupTracksWorker):
                worker.stop_lookup()
                stopped_worker = True
            elif isinstance(worker, DownloadTracksWorker):
                worker.stop_download()
                stopped_worker = True
        self._pending_lookup_users.discard(username)
        self._pending_play_cache_key = None
        self._pending_retry_cache_key = None
        self.window.set_youtube_work_state(
            active=stopped_worker,
            stopping=stopped_worker,
        )
        self._report_user_action(
            translate(
                "ApplicationController",
                "Stopping YouTube checks and downloads; completed items remain saved.",
            )
        )

    def _resume_youtube_work(self) -> None:
        """Resume unresolved checks or queued downloads for the current user."""

        username = self.window.username()
        if not username:
            return
        self._youtube_stop_requested = False
        self.window.set_youtube_work_state(active=False)
        tracks = self.repository.load_tracks(username)
        self._report_user_action(translate("ApplicationController", "Resuming YouTube work."))
        if self._has_lookup_candidates(tracks):
            self._ensure_automatic_lookup(username, len(tracks))
        elif self._has_download_candidates(tracks):
            self._ensure_automatic_download(username)
        else:
            self._report_user_action(
                translate(
                    "ApplicationController",
                    "No YouTube work remains to resume.",
                )
            )

    def retry_track_download(self, cache_key: str) -> None:
        """Retry the failed stage for one track with priority."""

        username = self.window.username()
        if not username:
            self.window.append_feedback(
                translate(
                    "ApplicationController",
                    "Enter a Last.fm username before retrying a track.",
                )
            )
            return
        tracks = self.repository.load_tracks(username)
        track = next((t for t in tracks if t.cache_key == cache_key), None)
        if track is None:
            return
        if track.status not in {
            TrackStatus.NOT_FOUND,
            TrackStatus.LOOKUP_FAILED,
            TrackStatus.FAILED,
        }:
            return
        self._youtube_stop_requested = False
        needs_lookup = track.status is not TrackStatus.FAILED or not track.youtube_url
        reset_track = replace(
            track,
            status=TrackStatus.FETCHED if needs_lookup else TrackStatus.QUEUED,
            youtube_url=None if needs_lookup else track.youtube_url,
            error=None,
        )
        updated = [reset_track if t.cache_key == cache_key else t for t in tracks]
        self.repository.save_tracks(username, updated)
        self.window.set_tracks(updated)
        track = reset_track
        self._pending_retry_cache_key = cache_key
        if needs_lookup:
            self._report_user_action(
                translate(
                    "ApplicationController",
                    "Retrying YouTube check for {artist} - {title}.",
                    artist=track.artist,
                    title=track.title,
                )
            )
        else:
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

    def _ensure_automatic_download(self, username: str) -> None:
        if self._youtube_stop_requested:
            return
        if self._download_worker_active or self._has_active_download_worker(username):
            return
        self._start_automatic_download(username)

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
        if self._pending_play_cache_key == track.cache_key:
            self._start_priority_download(username, track.cache_key)
            return
        if self._pending_retry_cache_key == track.cache_key:
            self._start_priority_download(username, track.cache_key)
            return
        if not self._youtube_stop_requested:
            self._ensure_automatic_download(username)

    def _has_download_candidates(self, tracks: list[Track]) -> bool:
        return any(
            bool(track.youtube_url)
            and track.status
            not in {
                TrackStatus.DOWNLOADED,
                TrackStatus.NOT_FOUND,
                TrackStatus.LOOKUP_FAILED,
                TrackStatus.FAILED,
            }
            for track in tracks
        )

    def _has_active_download_worker(self, username: str | None = None) -> bool:
        username = username or self._workflow_username
        return any(
            isinstance(worker, DownloadTracksWorker)
            and getattr(worker, "username", None) == username
            and self._worker_generations.get(worker, self._workflow_generation)
            == self._workflow_generation
            for worker in self._active_workers
        )

    def _has_active_lookup_worker(self, username: str | None = None) -> bool:
        username = username or self._workflow_username
        return any(
            isinstance(worker, LookupTracksWorker)
            and getattr(worker, "username", None) == username
            and self._worker_generations.get(worker, self._workflow_generation)
            == self._workflow_generation
            for worker in self._active_workers
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
        service = self._scrobbling_service
        timestamp = self._playback_start_time
        self._submit_background_call(
            lambda: service.scrobble(
                artist=current_track.artist,
                title=current_track.title,
                timestamp=timestamp,
                duration_seconds=duration_ms // 1000,
            )
        )

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
        self._continue_playback_from(finished_track.cache_key)

    def _continue_playback_from(self, cache_key: str) -> None:
        next_track = self._next_playback_track(cache_key)
        if next_track is None:
            self._report_user_action(translate("ApplicationController", "Playback finished."))
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
        worker_generation = self._worker_generations.pop(worker, self._workflow_generation)
        if worker is self._active_fetch_worker:
            self._active_fetch_worker = None
            self._fetch_paused = False
        if worker in self._active_workers:
            self._active_workers.remove(worker)
        username = getattr(worker, "username", None)
        if (
            username == self._workflow_username
            and worker_generation == self._workflow_generation
            and isinstance(worker, LookupTracksWorker)
            and not self._youtube_stop_requested
        ):
            tracks = self.repository.load_tracks(username)
            if username in self._pending_lookup_users:
                self._pending_lookup_users.discard(username)
                if self._has_lookup_candidates(tracks):
                    self._ensure_automatic_lookup(username, len(tracks))
            if self._has_download_candidates(tracks):
                self._ensure_automatic_download(username)
        if (
            username == self._workflow_username
            and worker_generation == self._workflow_generation
            and isinstance(worker, DownloadTracksWorker)
        ):
            tracks = self.repository.load_tracks(username)
            if self._has_download_candidates(tracks) and not self._youtube_stop_requested:
                self._ensure_automatic_download(username)
        if (
            isinstance(worker, (LookupTracksWorker, DownloadTracksWorker))
            and username == self._workflow_username
            and worker_generation == self._workflow_generation
        ):
            self._update_youtube_work_state(username)
        LOGGER.info("Worker released; active_workers=%d", len(self._active_workers))

    def _update_youtube_work_state(self, username: str) -> None:
        active = self._has_active_lookup_worker(username) or self._has_active_download_worker(
            username
        )
        if active:
            self.window.set_youtube_work_state(
                active=True,
                stopping=self._youtube_stop_requested,
            )
            return
        tracks = self.repository.load_tracks(username)
        resumable = self._has_lookup_candidates(tracks) or self._has_download_candidates(tracks)
        self.window.set_youtube_work_state(
            active=False,
            stopped=self._youtube_stop_requested and resumable,
        )

    @staticmethod
    def _has_lookup_candidates(tracks: list[Track]) -> bool:
        return any(
            not track.youtube_url and track.status is TrackStatus.FETCHED for track in tracks
        )

    def _forget_artist_image_worker(self, worker: ArtistImageWorker) -> None:
        if worker in self._active_artist_image_workers:
            self._active_artist_image_workers.remove(worker)
        LOGGER.info(
            "Artist image worker released; active_artist_image_workers=%d",
            len(self._active_artist_image_workers),
        )


def _open_firefox_private_window(url: str) -> bool:
    started, _pid = QProcess.startDetached("firefox", ["--private-window", url])
    if not started:
        LOGGER.error("Could not open artist page in Firefox private window: %s", url)
        return False
    return True

"""Pin the exact effects of the controller's workflow methods.

Every test here asserts what the controller passes to the window, repository,
workers and services, or which state it leaves behind, so that a changed argument,
flag or condition in ``my_lastfm_player.controller`` is detected.
"""

from __future__ import annotations

import logging
from functools import partial
from types import SimpleNamespace
from unittest.mock import MagicMock, call

import pytest

from my_lastfm_player import controller as controller_module
from my_lastfm_player.app_credentials import (
    LASTFM_API_KEY_ENV,
    LASTFM_API_SECRET_ENV,
    LastFmApiCredentials,
)
from my_lastfm_player.controller import ApplicationController, _open_artist_page
from my_lastfm_player.dependencies import DependencyCheckResult
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.settings import AppSettings
from my_lastfm_player.storage import JsonTrackRepository
from my_lastfm_player.ui.main_window import MainWindow, UnloveAvailability


class Signal:
    def __init__(self) -> None:
        self.callbacks: list = []

    def connect(self, callback) -> None:
        self.callbacks.append(callback)


class Worker:
    def __init__(self, username: str | None = None, *_args) -> None:
        if username is not None:
            self.username = username
        self.progress = Signal()
        self.error = Signal()
        self.finished = Signal()
        self.events: list[str] = []


class FetchWorker(Worker):
    def __init__(self, username=None, *args) -> None:
        super().__init__(username)
        self.args = args
        self.tracks_updated = Signal()
        self.tracks_loaded = Signal()
        self.fetch_stopped = Signal()

    def stop_fetch(self) -> None:
        self.events.append("stop_fetch")

    def pause_fetch(self) -> None:
        self.events.append("pause_fetch")

    def resume_fetch(self) -> None:
        self.events.append("resume_fetch")


class LookupWorker(Worker):
    def __init__(self, username=None, *args) -> None:
        super().__init__(username)
        self.args = args
        self.track_updated = Signal()
        self.tracks_resolved = Signal()

    def stop_lookup(self) -> None:
        self.events.append("stop_lookup")


class DownloadWorker(Worker):
    def __init__(self, username=None, *args) -> None:
        super().__init__(username)
        self.args = args
        self.track_updated = Signal()
        self.tracks_downloaded = Signal()

    def stop_download(self) -> None:
        self.events.append("stop_download")


class Preflight:
    def __init__(self) -> None:
        self.cancelled = False

    def cancel(self) -> None:
        self.cancelled = True


@pytest.fixture
def env(qapp, tmp_path, monkeypatch):
    monkeypatch.setattr(controller_module, "FetchLovedTracksWorker", FetchWorker)
    monkeypatch.setattr(controller_module, "LookupTracksWorker", LookupWorker)
    monkeypatch.setattr(controller_module, "DownloadTracksWorker", DownloadWorker)
    monkeypatch.setattr(AppSettings, "download_concurrency", lambda self: 3)
    window = MainWindow()
    window.set_username("alice")
    repository = JsonTrackRepository(data_dir=tmp_path / "data")
    controller = ApplicationController(
        window,
        repository=repository,
        artist_images_enabled=False,
        dependency_checker=lambda: DependencyCheckResult(installed=(), missing=()),
    )
    controller._workflow_username = "alice"
    controller.fetch_worker_factory = FetchWorker  # type: ignore[assignment]
    controller.lookup_worker_factory = LookupWorker  # type: ignore[assignment]
    controller.download_worker_factory = DownloadWorker  # type: ignore[assignment]
    started: list[tuple] = []
    monkeypatch.setattr(
        controller._threads,
        "start",
        lambda worker, on_finished=None: started.append((worker, on_finished)),
    )

    def spy(*names: str) -> None:
        for name in names:
            monkeypatch.setattr(window, name, MagicMock(wraps=getattr(window, name)))

    def feedback() -> str:
        return window.feedback_log.toPlainText()

    return SimpleNamespace(
        window=window,
        repository=repository,
        controller=controller,
        started=started,
        spy=spy,
        feedback=feedback,
        monkeypatch=monkeypatch,
    )


def record(env, name: str) -> list[tuple]:
    calls: list[tuple] = []
    env.monkeypatch.setattr(env.controller, name, lambda *args, **kwargs: calls.append(args))
    return calls


def errors(env) -> list[str]:
    return [args[0] for args, _kwargs in env.window.append_error.call_args_list]


# --- _open_artist_page / open_artist_page -------------------------------------------


def test_open_artist_page_reports_firefox_success_without_fallback(qapp, monkeypatch) -> None:
    fallback: list[object] = []
    monkeypatch.setattr(controller_module.QProcess, "startDetached", lambda *_args: (True, 1))
    monkeypatch.setattr(
        controller_module.QDesktopServices,
        "openUrl",
        lambda url: fallback.append(url) or False,
    )

    assert _open_artist_page("https://example.invalid/a") is True
    assert fallback == []


def test_open_artist_page_reports_the_failed_url(env) -> None:
    env.spy("append_error")
    env.monkeypatch.setattr(controller_module, "_open_artist_page", lambda _url: False)

    env.controller.open_artist_page("https://example.invalid/artist")

    assert errors(env) == ["Could not open artist page: https://example.invalid/artist"]


# --- open_file_cache ------------------------------------------------------------------


def test_open_file_cache_creates_missing_parents_and_reports_the_path(env, tmp_path) -> None:
    env.spy("append_error")
    opened: list[str] = []
    env.monkeypatch.setattr(
        controller_module.QDesktopServices,
        "openUrl",
        lambda url: opened.append(url.toLocalFile()) or True,
    )
    data_dir = tmp_path / "nested" / "deeper" / "data"
    env.repository.data_dir = data_dir

    env.controller.open_file_cache()

    assert data_dir.is_dir()
    assert opened == [str(data_dir)]
    assert errors(env) == []
    assert f"Opened data folder: {data_dir}" in env.feedback()


def test_open_file_cache_reports_the_path_when_opening_fails(env, tmp_path) -> None:
    env.spy("append_error")
    env.monkeypatch.setattr(controller_module.QDesktopServices, "openUrl", lambda _url: False)
    env.repository.data_dir = tmp_path / "data"

    env.controller.open_file_cache()

    assert errors(env) == [f"Could not open data folder: {tmp_path / 'data'}"]


def test_open_file_cache_reports_the_mkdir_error(env, tmp_path) -> None:
    env.spy("append_error")
    blocker = tmp_path / "file"
    blocker.write_text("x")
    env.repository.data_dir = blocker / "data"
    try:
        (blocker / "data").mkdir(parents=True, exist_ok=True)
    except OSError as error:
        expected = str(error)

    env.controller.open_file_cache()

    assert errors(env) == [f"Could not open data folder: {expected}"]


# --- _cancel_work_for_username --------------------------------------------------------


def test_cancel_reports_nothing_when_no_work_belongs_to_the_user(env) -> None:
    env.controller._cancel_work_for_username("alice")

    assert "Stopping background work" not in env.feedback()


def test_cancel_stops_a_preflight_and_reports_it(env) -> None:
    preflight = Preflight()
    env.controller._active_fetch_preflight = preflight  # type: ignore[assignment]
    env.controller._fetch_preflight_username = "alice"

    env.controller._cancel_work_for_username("alice")

    assert preflight.cancelled
    assert env.controller._active_fetch_preflight is None
    assert env.controller._fetch_preflight_username is None
    assert "Stopping background work for alice; completed items remain saved." in env.feedback()


def test_cancel_leaves_a_preflight_of_another_user_alone(env) -> None:
    preflight = Preflight()
    env.controller._active_fetch_preflight = preflight  # type: ignore[assignment]
    env.controller._fetch_preflight_username = "bob"

    env.controller._cancel_work_for_username("alice")

    assert not preflight.cancelled
    assert env.controller._fetch_preflight_username == "bob"


def test_cancel_without_a_preflight_object_ignores_the_stale_preflight_username(env) -> None:
    env.controller._fetch_preflight_username = "alice"

    env.controller._cancel_work_for_username("alice")

    assert "Stopping background work" not in env.feedback()


def test_cancel_stops_only_workers_of_the_user_and_reports_it(env) -> None:
    anonymous = Worker()
    other = LookupWorker("bob")
    fetch = FetchWorker("alice")
    lookup = LookupWorker("alice")
    download = DownloadWorker("alice")
    env.controller._active_workers = [anonymous, other, fetch, lookup, download]  # type: ignore[list-item]

    env.controller._cancel_work_for_username("alice")

    assert other.events == []
    assert fetch.events == ["stop_fetch"]
    assert lookup.events == ["stop_lookup"]
    assert download.events == ["stop_download"]
    assert "Stopping background work for alice; completed items remain saved." in env.feedback()


def test_cancel_resets_the_youtube_and_fetch_flags(env) -> None:
    env.spy("set_youtube_work_state")
    controller = env.controller
    controller._fetch_paused = True
    controller._started_incremental_lookup_for_fetch = True
    controller._download_worker_active = True
    controller._youtube_stop_requested = True
    controller._pending_lookup_users = {"alice", "bob"}

    controller._cancel_work_for_username("alice")

    assert controller._fetch_paused is False
    assert controller._started_incremental_lookup_for_fetch is False
    assert controller._download_worker_active is False
    assert controller._youtube_stop_requested is False
    assert controller._pending_lookup_users == {"bob"}
    env.window.set_youtube_work_state.assert_called_once_with(active=False)


def test_cancel_stops_the_active_fetch_worker_of_the_user_only(env) -> None:
    foreign = FetchWorker("bob")
    env.controller._active_fetch_worker = foreign  # type: ignore[assignment]

    env.controller._cancel_work_for_username("alice")

    assert foreign.events == []
    assert env.controller._active_fetch_worker is foreign


def test_cancel_stops_an_active_fetch_worker_without_a_username(env) -> None:
    anonymous = FetchWorker()
    env.controller._active_fetch_worker = anonymous  # type: ignore[assignment]

    env.controller._cancel_work_for_username("alice")

    assert anonymous.events == ["stop_fetch"]
    assert env.controller._active_fetch_worker is None


# --- username editing and committing --------------------------------------------------


def test_commit_increments_the_generation_and_ends_editing(env) -> None:
    controller = env.controller
    controller._workflow_generation = 5

    controller._commit_workflow_username("bob")

    assert controller._workflow_generation == 6
    assert controller._workflow_username == "bob"

    controller._username_edit_active = True
    controller._commit_workflow_username("carol")

    assert controller._username_edit_active is False


def test_username_edit_resets_pending_state_and_controls(env) -> None:
    env.spy("set_fetch_control_state")
    controller = env.controller
    controller._workflow_generation = 5
    controller._pending_play_cache_key = "play"
    controller._pending_retry_cache_key = "retry"

    controller._handle_username_text_edited("bob")

    assert controller._workflow_generation == 6
    assert controller._pending_play_cache_key is None
    assert controller._pending_retry_cache_key is None
    env.window.set_fetch_control_state.assert_called_once_with(active=False, paused=False)


# --- worker queries -------------------------------------------------------------------


def test_has_active_worker_for_username_variants(env) -> None:
    controller = env.controller
    controller._workflow_generation = 2
    anonymous = Worker()
    other = LookupWorker("bob")
    controller._active_workers = [anonymous, other]  # type: ignore[list-item]
    controller._worker_generations = {other: 2}  # type: ignore[dict-item]

    assert controller._has_active_worker_for_username("alice") is False

    mine = DownloadWorker("alice")
    controller._active_workers.append(mine)  # type: ignore[arg-type]
    assert controller._has_active_worker_for_username("alice") is True

    controller._worker_generations[mine] = 1  # type: ignore[index]
    assert controller._has_active_worker_for_username("alice") is False

    controller._fetch_preflight_username = "alice"
    assert controller._has_active_worker_for_username("alice") is False

    controller._active_fetch_preflight = Preflight()  # type: ignore[assignment]
    controller._fetch_preflight_username = "bob"
    assert controller._has_active_worker_for_username("alice") is False
    assert controller._has_active_worker_for_username("bob") is True


def test_has_active_download_worker_variants(env) -> None:
    controller = env.controller
    controller._workflow_generation = 2
    anonymous = DownloadWorker()
    controller._active_workers = [anonymous]  # type: ignore[list-item]

    assert controller._has_active_download_worker("alice") is False

    mine = DownloadWorker("alice")
    controller._active_workers.append(mine)  # type: ignore[arg-type]
    assert controller._has_active_download_worker("alice") is True
    assert controller._has_active_download_worker() is True
    assert controller._has_active_download_worker("bob") is False

    controller._worker_generations[mine] = 1  # type: ignore[index]
    assert controller._has_active_download_worker("alice") is False


def test_has_active_lookup_worker_variants(env) -> None:
    controller = env.controller
    anonymous = LookupWorker()
    mine = LookupWorker("alice")
    controller._active_workers = [anonymous, mine]  # type: ignore[list-item]

    assert controller._has_active_lookup_worker() is True
    assert controller._has_active_lookup_worker("bob") is False


def test_has_any_worker_for_username_variants(env) -> None:
    controller = env.controller
    controller._active_workers = [Worker()]  # type: ignore[list-item]

    assert controller._has_any_worker_for_username("alice") is False

    controller._fetch_preflight_username = "alice"
    assert controller._has_any_worker_for_username("alice") is False

    controller._active_fetch_preflight = Preflight()  # type: ignore[assignment]
    assert controller._has_any_worker_for_username("alice") is True
    assert controller._has_any_worker_for_username("bob") is False

    controller._active_fetch_preflight = None
    controller._active_fetch_worker = FetchWorker("bob")  # type: ignore[assignment]
    assert controller._has_any_worker_for_username("alice") is True


def test_candidate_and_url_predicates(env) -> None:
    controller = env.controller
    plain = Track(artist="A", title="Fetched")
    resolved = Track(artist="A", title="Resolved", youtube_url="u", status=TrackStatus.FETCHED)
    other = Track(artist="A", title="Other", youtube_url="v", status=TrackStatus.QUEUED)
    downloaded = Track(artist="A", title="Done", status=TrackStatus.DOWNLOADED)

    assert controller._has_download_candidates([plain]) is False
    assert controller._has_lookup_candidates([resolved, downloaded]) is False
    assert controller._track_has_youtube_url([plain, other], plain.cache_key) is False


# --- automatic lookup / download ------------------------------------------------------


def test_ensure_download_respects_the_bulk_flag_and_the_users_worker(env) -> None:
    started = record(env, "_start_automatic_download")
    controller = env.controller

    controller._download_worker_active = True
    controller._ensure_automatic_download("alice")
    assert started == []

    controller._download_worker_active = False
    controller._active_workers = [DownloadWorker("bob")]  # type: ignore[list-item]
    controller._ensure_automatic_download("bob")
    assert started == []


def test_ensure_lookup_checks_the_given_user_and_clears_the_pending_mark(env) -> None:
    started = record(env, "_start_automatic_lookup")
    controller = env.controller
    controller._active_workers = [LookupWorker("bob")]  # type: ignore[list-item]

    controller._ensure_automatic_lookup("bob", 3)
    assert started == []
    assert controller._pending_lookup_users == {"bob"}

    controller._active_workers = []
    controller._ensure_automatic_lookup("bob", 3)
    assert started == [("bob", 3)]
    assert controller._pending_lookup_users == set()


def test_start_automatic_lookup_reports_the_count(env) -> None:
    record(env, "resolve_youtube_urls")

    env.controller._start_automatic_lookup("alice", 7)

    assert "Starting automatic YouTube lookup for 7 fetched tracks." in env.feedback()


# --- _forget_worker / _update_youtube_work_state --------------------------------------


def test_forget_lookup_worker_clears_pending_user_without_candidates(env) -> None:
    record(env, "_update_youtube_work_state")
    controller = env.controller
    worker = LookupWorker("alice")
    controller._active_workers = [worker]  # type: ignore[list-item]
    controller._pending_lookup_users = {"alice"}

    controller._forget_worker(worker)  # type: ignore[arg-type]

    assert controller._pending_lookup_users == set()


def test_forget_download_worker_of_another_user_starts_nothing(env) -> None:
    record(env, "_update_youtube_work_state")
    ensured = record(env, "_ensure_automatic_download")
    env.repository.save_tracks(
        "bob", [Track(artist="A", title="T", youtube_url="u", status=TrackStatus.QUEUED)]
    )
    worker = DownloadWorker("bob")
    env.controller._active_workers = [worker]  # type: ignore[list-item]

    env.controller._forget_worker(worker)  # type: ignore[arg-type]

    assert ensured == []


def test_forget_download_worker_without_candidates_starts_nothing(env) -> None:
    record(env, "_update_youtube_work_state")
    ensured = record(env, "_ensure_automatic_download")
    worker = DownloadWorker("alice")
    env.controller._active_workers = [worker]  # type: ignore[list-item]

    env.controller._forget_worker(worker)  # type: ignore[arg-type]

    assert ensured == []


def test_update_youtube_work_state_while_a_worker_of_the_user_runs(env) -> None:
    env.spy("set_youtube_work_state")
    controller = env.controller
    controller._youtube_stop_requested = True
    controller._active_workers = [LookupWorker("bob")]  # type: ignore[list-item]

    controller._update_youtube_work_state("bob")

    env.window.set_youtube_work_state.assert_called_once_with(active=True, stopping=True)

    env.window.set_youtube_work_state.reset_mock()
    controller._active_workers = [DownloadWorker("bob")]  # type: ignore[list-item]
    controller._update_youtube_work_state("bob")

    env.window.set_youtube_work_state.assert_called_once_with(active=True, stopping=True)


def test_update_youtube_work_state_when_idle_with_resumable_work(env) -> None:
    env.spy("set_youtube_work_state")
    env.repository.save_tracks("alice", [Track(artist="A", title="T")])

    env.controller._update_youtube_work_state("alice")

    env.window.set_youtube_work_state.assert_called_once_with(active=False, stopped=False)


# --- fetch flow -----------------------------------------------------------------------


def test_fetch_reports_a_running_worker_for_the_user(env) -> None:
    env.controller._active_workers = [FetchWorker("alice")]  # type: ignore[list-item]

    env.controller.fetch_loved_tracks()

    assert "Background work is already running for alice." in env.feedback()


def test_fetch_starts_the_preflight_with_cached_tracks(env) -> None:
    env.spy("set_progress")
    preflights = record(env, "_start_background_worker")
    env.repository.save_tracks("alice", [Track(artist="A", title="T")])
    env.controller._youtube_stop_requested = True

    env.controller.fetch_loved_tracks()

    assert env.controller._youtube_stop_requested is False
    assert "Found 1 cached tracks for alice; checking Last.fm before using them." in (
        env.feedback()
    )
    env.window.set_progress.assert_called_once_with(0, "Starting fetch")
    assert len(preflights) == 1


def test_preflight_result_with_matching_cache_loads_it(env) -> None:
    env.spy("set_fetch_control_state", "set_progress", "set_workflow_enabled")
    lookups = record(env, "_start_automatic_lookup")
    cached = [Track(artist="A", title="T")]
    controller = env.controller
    controller._fetch_preflight_username = "alice"

    controller._handle_fetch_preflight_result("alice", 0, cached, 1)

    assert controller._fetch_preflight_username is None
    env.window.set_fetch_control_state.assert_called_once_with(False)
    env.window.set_progress.assert_called_once_with(100, "Loaded cached tracks")
    env.window.set_workflow_enabled.assert_called_once_with(True)
    assert lookups == [("alice", 1)]


def test_preflight_error_with_cache_loads_it(env) -> None:
    env.spy("set_fetch_control_state", "set_progress", "set_workflow_enabled")
    record(env, "_start_automatic_lookup")
    cached = [Track(artist="A", title="T")]
    controller = env.controller
    controller._fetch_preflight_username = "alice"

    controller._handle_fetch_preflight_error("alice", 0, cached, RuntimeError("offline"))

    assert controller._fetch_preflight_username is None
    assert (
        "Could not verify Last.fm loved-track count for alice; using 1 cached tracks: offline"
        in env.feedback()
    )
    env.window.set_fetch_control_state.assert_called_once_with(False)
    env.window.set_progress.assert_called_once_with(100, "Loaded cached tracks")
    env.window.set_workflow_enabled.assert_called_once_with(True)


def test_preflight_error_without_cache_reports_and_reenables(env) -> None:
    env.spy("set_fetch_control_state", "set_workflow_enabled")

    env.controller._handle_fetch_preflight_error("alice", 0, [], RuntimeError("offline"))

    env.window.set_fetch_control_state.assert_called_once_with(False)
    env.window.set_workflow_enabled.assert_called_once_with(True)
    assert "Could not reach Last.fm for alice: offline" in env.feedback()


def test_cached_count_messages(env) -> None:
    controller = env.controller

    assert controller._cached_count_matches_value("alice", 3, None) is False
    assert controller._cached_count_matches_value("alice", 3, 3) is True
    assert controller._cached_count_matches_value("alice", 3, 4) is False

    text = env.feedback()
    assert (
        "Could not read Last.fm loved-track count for alice; "
        "fetching fresh data instead of trusting 3 cached tracks." in text
    )
    assert "Last.fm reports 3 loved tracks for alice; cached track count matches." in text
    assert (
        "Last.fm reports 4 loved tracks for alice, but the cache has 3; fetching fresh data."
        in text
    )


@pytest.mark.parametrize(
    ("expected", "message"),
    [
        (5, "Starting fresh Last.fm fetch for alice; 5 tracks expected."),
        (None, "Starting fresh Last.fm fetch for alice."),
    ],
)
def test_start_fresh_fetch_sets_controls_and_starts_the_worker(env, expected, message) -> None:
    env.spy("set_fetch_control_state", "set_progress")
    runs = record(env, "_run_worker")
    controller = env.controller
    controller._fetch_paused = True
    controller._started_incremental_lookup_for_fetch = True

    controller._start_fresh_fetch("alice", expected)

    assert message in env.feedback()
    env.window.set_fetch_control_state.assert_called_once_with(True, can_pause=True)
    env.window.set_progress.assert_called_once_with(0, "Starting fetch")
    assert controller._fetch_paused is False
    assert controller._started_incremental_lookup_for_fetch is False
    worker = runs[0][0]
    assert worker.username == "alice"
    assert worker.args == (controller.scraper, env.repository, expected)


def test_toggle_fetch_pause_sets_exact_control_states(env) -> None:
    env.spy("set_fetch_control_state")
    controller = env.controller
    worker = FetchWorker("alice")
    controller._active_fetch_worker = worker  # type: ignore[assignment]

    controller.toggle_fetch_pause()
    assert controller._fetch_paused is True
    controller.toggle_fetch_pause()
    assert controller._fetch_paused is False

    assert worker.events == ["pause_fetch", "resume_fetch"]
    assert env.window.set_fetch_control_state.call_args_list == [
        call(active=True, paused=True),
        call(active=True, paused=False),
    ]


def test_stop_fetch_of_a_preflight(env) -> None:
    env.spy("set_fetch_control_state")
    controller = env.controller
    controller._active_fetch_preflight = Preflight()  # type: ignore[assignment]
    controller._fetch_preflight_username = "alice"

    controller.stop_fetch()

    assert controller._fetch_preflight_username is None
    env.window.set_fetch_control_state.assert_called_once_with(False)


def test_stop_fetch_of_a_worker(env) -> None:
    env.spy("set_fetch_control_state")
    controller = env.controller
    controller._active_fetch_worker = FetchWorker("alice")  # type: ignore[assignment]
    controller._fetch_paused = True

    controller.stop_fetch()

    assert controller._fetch_paused is False
    env.window.set_fetch_control_state.assert_called_once_with(active=False, paused=False)


def test_complete_worker_run_resets_the_fetch_controls(env) -> None:
    env.spy("set_fetch_control_state")
    env.controller._running_worker_count = 1

    env.controller._complete_worker_run()

    env.window.set_fetch_control_state.assert_called_once_with(active=False, paused=False)


def test_tracks_loaded_resets_fetch_state(env) -> None:
    env.spy("set_fetch_control_state")
    controller = env.controller
    controller._fetch_paused = True
    controller._started_incremental_lookup_for_fetch = True

    controller._handle_tracks_loaded("alice", [Track(artist="A", title="T", youtube_url="u")])

    assert "Fetched and stored 1 tracks for alice." in env.feedback()
    assert controller._fetch_paused is False
    assert controller._started_incremental_lookup_for_fetch is False
    env.window.set_fetch_control_state.assert_called_once_with(active=False, paused=False)


def test_fetch_stopped_resets_fetch_state(env) -> None:
    env.spy("set_fetch_control_state")
    controller = env.controller
    controller._fetch_paused = True
    controller._started_incremental_lookup_for_fetch = True

    controller._handle_fetch_stopped("alice", [Track(artist="A", title="T")])

    assert controller._fetch_paused is False
    assert controller._started_incremental_lookup_for_fetch is False
    env.window.set_fetch_control_state.assert_called_once_with(active=False, paused=False)
    assert "Stopped fetch for alice after 1 tracks." in env.feedback()


@pytest.mark.parametrize(
    ("handler", "message"),
    [
        ("_handle_tracks_loaded", "Fetch for alice returned invalid track data."),
        ("_handle_fetch_stopped", "Stopped fetch for alice returned invalid data."),
        ("_handle_tracks_updated", "Fetch for alice returned invalid partial data."),
        ("_handle_track_updated", "Workflow for alice returned an invalid track update."),
        ("_handle_tracks_resolved", "Lookup for alice returned invalid track data."),
        ("_handle_tracks_downloaded", "Download for alice returned invalid track data."),
    ],
)
def test_invalid_worker_payload_messages_name_the_user(env, handler, message) -> None:
    getattr(env.controller, handler)("alice", "not a list")

    assert message in env.feedback()


def test_tracks_updated_reports_progress_and_status(env) -> None:
    env.spy("show_status")

    env.controller._handle_tracks_updated("alice", [Track(artist="A", title="T", youtube_url="u")])

    assert "Fetch progress for alice: 1 tracks are visible now." in env.feedback()
    assert env.window.show_status.call_args_list[-1] == call("Fetched 1 tracks for alice")


def test_track_updated_reports_and_only_queues_resolved_tracks(env) -> None:
    ready = record(env, "_handle_track_ready_for_download")
    track = Track(artist="Artist", title="Title", status=TrackStatus.QUEUED)
    env.window.set_tracks([track])

    env.controller._handle_track_updated("alice", track)
    env.controller._handle_track_updated(
        "alice", Track(artist="Artist", title="Title", youtube_url="u", status=TrackStatus.FAILED)
    )

    assert "Track update from alice: Artist - Title is now Queued." in env.feedback()
    assert ready == []


def test_tracks_resolved_reports_exact_counts(env) -> None:
    record(env, "_ensure_automatic_download")
    env.repository.save_tracks(
        "alice",
        [
            Track(artist="A", title="One", youtube_url="u", status=TrackStatus.QUEUED),
            Track(artist="A", title="Two", status=TrackStatus.NOT_FOUND),
            Track(artist="A", title="Three"),
        ],
    )

    env.controller._handle_tracks_resolved("alice", [])

    assert "Resolved YouTube URLs for 1/3 tracks; 1 were not found." in env.feedback()


def test_tracks_downloaded_reports_exact_counts(env, tmp_path) -> None:
    audio = tmp_path / "two.mp3"
    audio.write_bytes(b"x")
    env.repository.save_tracks(
        "alice",
        [
            Track(artist="A", title="One", status=TrackStatus.FAILED),
            Track(artist="A", title="Two", local_path=str(audio), status=TrackStatus.DOWNLOADED),
        ],
    )

    env.controller._handle_tracks_downloaded("alice", [])

    assert "Download run for alice finished: 1/2 tracks downloaded, 1 failed." in env.feedback()


def test_tracks_downloaded_continues_only_a_bulk_run_with_candidates(env) -> None:
    ensured = record(env, "_ensure_automatic_download")
    controller = env.controller
    env.repository.save_tracks(
        "alice", [Track(artist="A", title="T", youtube_url="u", status=TrackStatus.QUEUED)]
    )

    controller._download_worker_active = False
    controller._handle_tracks_downloaded("alice", [])
    assert ensured == []

    env.repository.save_tracks("alice", [Track(artist="A", title="T")])
    controller._download_worker_active = True
    controller._handle_tracks_downloaded("alice", [])
    assert ensured == []


def test_load_cached_tracks_for_entered_username_reports_count(env) -> None:
    env.repository.save_tracks("alice", [Track(artist="A", title="T")])

    assert env.controller.load_cached_tracks_for_entered_username() is True

    assert "Loaded 1 cached tracks for alice; skipped Last.fm fetch." in env.feedback()


# --- resolve / download ---------------------------------------------------------------


def test_resolve_youtube_urls_reports_and_passes_its_arguments(env) -> None:
    env.spy("set_stage_progress")
    runs = record(env, "_run_worker")
    controller = env.controller

    controller.resolve_youtube_urls("alice")
    controller.resolve_youtube_urls("alice", priority_cache_key="key", max_tracks=1)

    text = env.feedback()
    assert "Starting YouTube lookup for alice; priority=none, limit=all." in text
    assert "Starting YouTube lookup for alice; priority=key, limit=1." in text
    assert env.window.set_stage_progress.call_args_list == [
        call("lookup", 0, "Starting YouTube lookup"),
        call("lookup", 0, "Starting YouTube lookup"),
    ]
    resolver = controller.youtube_resolver
    assert runs[0][0].args == (resolver, env.repository, None, None, 3)
    assert runs[1][0].args == (resolver, env.repository, "key", 1, 3)


def test_download_tracks_reports_and_passes_its_arguments(env) -> None:
    env.spy("set_stage_progress")
    runs = record(env, "_run_worker")
    controller = env.controller

    controller.download_tracks("alice")
    controller.download_tracks("alice", priority_cache_key="key", max_downloads=1)

    text = env.feedback()
    assert "Starting downloads for alice; concurrency=3, priority=none, limit=all." in text
    assert "Starting downloads for alice; concurrency=3, priority=key, limit=1." in text
    assert env.window.set_stage_progress.call_args_list == [
        call("download", 0, "Starting downloads"),
        call("download", 0, "Starting downloads"),
    ]
    manager = controller.download_manager
    assert runs[0][0].args == (manager, env.repository, 3, None, None)
    assert runs[1][0].args == (manager, env.repository, 3, "key", 1)


# --- stop / resume / retry ------------------------------------------------------------


def test_stop_youtube_work_stops_matching_workers_and_clears_pending(env) -> None:
    env.spy("set_youtube_work_state")
    controller = env.controller
    other = DownloadWorker("bob")
    mine = DownloadWorker("alice")
    controller._active_workers = [other, mine]  # type: ignore[list-item]
    controller._pending_lookup_users = {"alice"}
    controller._pending_play_cache_key = "play"
    controller._pending_retry_cache_key = "retry"

    controller.stop_youtube_work()

    assert other.events == []
    assert mine.events == ["stop_download"]
    assert controller._pending_lookup_users == set()
    assert controller._pending_play_cache_key is None
    assert controller._pending_retry_cache_key is None
    env.window.set_youtube_work_state.assert_called_once_with(active=True, stopping=True)


def test_retry_of_a_not_found_track_with_url_resets_it_for_lookup(env) -> None:
    resolves = record(env, "resolve_youtube_urls")
    stuck = Track(
        artist="A", title="Stuck", youtube_url="u", status=TrackStatus.NOT_FOUND, error="gone"
    )
    keep = Track(artist="A", title="Keep", youtube_url="k", status=TrackStatus.QUEUED)
    env.repository.save_tracks("alice", [stuck, keep])
    env.controller._youtube_stop_requested = True

    env.controller.retry_track_download(stuck.cache_key)

    saved = env.repository.load_tracks("alice")
    assert saved[0].status is TrackStatus.FETCHED
    assert saved[0].youtube_url is None
    assert saved[0].error is None
    assert saved[1] == keep
    assert env.controller._youtube_stop_requested is False
    assert resolves == [("alice",)]


# --- startup recheck ------------------------------------------------------------------


def test_recheck_resets_stuck_tracks_and_reports_counts(env) -> None:
    resolves = record(env, "resolve_youtube_urls")
    env.repository.save_tracks(
        "alice",
        [
            Track(
                artist="A",
                title="Missing",
                youtube_url="u",
                status=TrackStatus.NOT_FOUND,
                error="x",
            ),
            Track(
                artist="A", title="Failed", youtube_url="v", status=TrackStatus.FAILED, error="y"
            ),
        ],
    )

    env.controller._recheck_stuck_tracks()

    missing, failed = env.repository.load_tracks("alice")
    assert missing.youtube_url is None
    assert missing.error is None
    assert failed.status is TrackStatus.QUEUED
    assert failed.error is None
    assert "Re-checking 1 not-found and 1 failed tracks from the last run." in env.feedback()
    assert resolves == [("alice",)]


def test_recheck_of_failed_downloads_goes_straight_to_download(env) -> None:
    resolves = record(env, "resolve_youtube_urls")
    downloads = record(env, "download_tracks")
    env.repository.save_tracks(
        "alice",
        [
            Track(artist="A", title="Failed", youtube_url="v", status=TrackStatus.FAILED),
            Track(artist="A", title="Resolved", youtube_url="w", status=TrackStatus.FETCHED),
        ],
    )

    env.controller._recheck_stuck_tracks()

    assert resolves == []
    assert downloads == [("alice",)]


# --- scrobbling setup -----------------------------------------------------------------


class FakeScrobblingService:
    instances: list[FakeScrobblingService] = []

    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        self.session_key = kwargs["session_key"]
        self.username = kwargs["username"]
        FakeScrobblingService.instances.append(self)

    def try_connect(self) -> bool:
        raise RuntimeError("offline")


@pytest.fixture
def scrobbling(env):
    FakeScrobblingService.instances = []
    defaults: list[bool] = []
    env.monkeypatch.setattr(controller_module, "ScrobblingService", FakeScrobblingService)
    env.monkeypatch.setattr(
        controller_module,
        "lastfm_api_credentials",
        lambda: LastFmApiCredentials(api_key="key", api_secret="secret"),
    )
    env.monkeypatch.setattr(
        AppSettings,
        "scrobbling_enabled",
        lambda self, default_enabled=True: defaults.append(default_enabled) or default_enabled,
    )

    def run_inline(operation, on_result=None, on_error=None):
        try:
            result = operation()
        except Exception as error:  # noqa: BLE001 - mirrors BackgroundCallWorker
            if on_error is not None:
                on_error(error)
            return None
        if on_result is not None:
            on_result(result)
        return None

    env.monkeypatch.setattr(env.controller, "_submit_background_call", run_inline)
    return defaults


def test_init_scrobbling_without_stored_credentials(env, scrobbling) -> None:
    env.controller._init_scrobbling()

    service = FakeScrobblingService.instances[0]
    assert service.kwargs == {
        "api_key": "key",
        "api_secret": "secret",
        "session_key": "",
        "username": "",
        "scrobbling_enabled": True,
    }
    assert scrobbling == [True]
    assert "Loaded Last.fm scrobbling settings; stored session key is missing." in env.feedback()


def test_init_scrobbling_with_stored_credentials(env, scrobbling) -> None:
    env.repository.save_credentials(
        {"session_key": "sess", "username": "listener", "scrobbling_enabled": False}
    )

    env.controller._init_scrobbling()

    service = FakeScrobblingService.instances[0]
    assert service.kwargs["session_key"] == "sess"
    assert service.kwargs["username"] == "listener"
    assert service.kwargs["scrobbling_enabled"] is False
    assert scrobbling == [False]
    text = env.feedback()
    assert "Loaded Last.fm scrobbling settings; stored session key is present." in text
    assert (
        "Stored Last.fm session key could not be verified; scrobbling remains disconnected." in text
    )


def test_init_scrobbling_reports_the_missing_environment_variables(env, monkeypatch) -> None:
    monkeypatch.setattr(
        controller_module,
        "lastfm_api_credentials",
        lambda: LastFmApiCredentials(api_key="", api_secret=""),
    )

    env.controller._init_scrobbling()

    assert (
        f"Last.fm scrobbling is disabled because {LASTFM_API_KEY_ENV}/{LASTFM_API_SECRET_ENV} "
        "are not configured and no bundled credentials are available." in env.feedback()
    )


@pytest.mark.parametrize(("username", "shown"), [("listener", "listener"), ("", "no user")])
def test_save_scrobbling_credentials_names_the_user(env, monkeypatch, username, shown) -> None:
    saved: list[bool] = []
    monkeypatch.setattr(
        AppSettings, "set_scrobbling_enabled", lambda self, value: saved.append(value)
    )
    env.controller._scrobbling_service = SimpleNamespace(  # type: ignore[assignment]
        scrobbling_enabled=True,
        username=username,
        credentials_dict=lambda: {"username": username},
    )

    env.controller._save_scrobbling_credentials()

    assert saved == [True]
    assert f"Saved Last.fm scrobbling preferences for {shown}." in env.feedback()


def test_show_preferences_passes_the_scrobbling_service(env, monkeypatch) -> None:
    from my_lastfm_player.ui import preferences_dialog

    created: list[tuple] = []

    class Dialog:
        def __init__(self, *args) -> None:
            created.append(args)

        def exec(self) -> int:
            return 0

    monkeypatch.setattr(preferences_dialog, "PreferencesDialog", Dialog)
    monkeypatch.setattr(env.controller, "_save_scrobbling_credentials", lambda: None)
    monkeypatch.setattr(env.controller, "_apply_ytdlp_settings", lambda: None)
    service = object()
    env.controller._scrobbling_service = service  # type: ignore[assignment]

    env.controller._show_preferences()

    assert created == [(env.window, service)]


def test_start_registers_the_unlove_availability_provider(env, monkeypatch) -> None:
    monkeypatch.setattr(env.controller, "_init_scrobbling", lambda: None)
    monkeypatch.setattr(env.controller, "_apply_ytdlp_settings", lambda: None)
    monkeypatch.setattr(env.controller, "_recheck_stuck_tracks", lambda: None)
    env.spy("set_unlove_availability_provider")

    env.controller.start()

    env.window.set_unlove_availability_provider.assert_called_once_with(
        env.controller._unlove_availability
    )


# --- unlove ---------------------------------------------------------------------------


def unlove_service(username: str = "alice"):
    calls: list[tuple] = []
    service = SimpleNamespace(
        can_write_loves=True,
        username=username,
        unlove_track=lambda artist, title: calls.append((artist, title)),
    )
    return service, calls


def test_unlove_availability_reasons_and_account(env) -> None:
    controller = env.controller
    service, _calls = unlove_service()
    controller._scrobbling_service = service  # type: ignore[assignment]

    assert controller._unlove_availability() == UnloveAvailability(enabled=True, account="alice")

    controller._workflow_username = "bob"
    assert controller._unlove_availability() == UnloveAvailability(
        enabled=False,
        reason="Only your own loved tracks can be unloved (connected as alice).",
        account="alice",
    )
    controller._workflow_username = "alice"

    controller._unlove_in_flight = "key"
    assert controller._unlove_availability() == UnloveAvailability(
        enabled=False,
        reason="Another unlove is still being sent to Last.fm.",
        account="alice",
    )
    controller._unlove_in_flight = None

    controller._active_workers = [LookupWorker("alice")]  # type: ignore[list-item]
    assert controller._unlove_availability() == UnloveAvailability(
        enabled=False,
        reason="Wait until fetching and YouTube work have finished, or stop them.",
        account="alice",
    )


def test_unlove_track_ignores_unknown_tracks_and_marks_the_request(env) -> None:
    controller = env.controller
    service, calls = unlove_service()
    controller._scrobbling_service = service  # type: ignore[assignment]
    track = Track(artist="Artist", title="Title")
    env.repository.save_tracks("alice", [track])
    submitted: list[tuple] = []
    env.monkeypatch.setattr(
        controller, "_submit_background_call", lambda *args: submitted.append(args)
    )

    controller.unlove_track("unknown")
    assert submitted == []

    controller.unlove_track(track.cache_key)

    assert controller._unlove_in_flight == track.cache_key
    assert "Unloving Artist - Title on Last.fm." in env.feedback()
    submitted[0][0]()
    assert calls == [("Artist", "Title")]


def test_unlove_result_leaves_the_table_of_another_entered_user(env) -> None:
    env.window.set_username("bob")
    env.spy("set_tracks")

    env.controller._handle_unlove_result("alice", Track(artist="A", title="T"))

    env.window.set_tracks.assert_not_called()


def test_unlove_error_names_the_error(env) -> None:
    env.spy("append_error")

    env.controller._handle_unlove_error(Track(artist="A", title="T"), RuntimeError("denied"))

    assert errors(env) == ["Could not unlove A - T on Last.fm: denied"]


# --- worker plumbing ------------------------------------------------------------------


def test_worker_error_and_progress_default_to_the_discovery_stage(env) -> None:
    env.spy("set_stage_progress")

    env.controller._handle_worker_progress("alice", 40, "Fetching")
    env.controller._handle_worker_error_for("alice", "boom")

    assert env.window.set_stage_progress.call_args_list == [
        call("discovery", 40, "Fetching"),
        call("discovery", 0, "Failed"),
    ]


def test_run_worker_logs_the_worker_class(env, caplog) -> None:
    caplog.set_level(logging.INFO, logger=controller_module.LOGGER.name)

    env.controller._run_worker(FetchWorker("alice"))  # type: ignore[arg-type]

    assert "Preparing FetchWorker on background thread" in caplog.text


def test_run_artist_image_worker_releases_the_worker_when_its_thread_ends(env) -> None:
    worker = SimpleNamespace(artist="A", artist_image_loaded=Signal(), error=Signal())

    env.controller._run_artist_image_worker(worker)  # type: ignore[arg-type]

    started_worker, on_finished = env.started[0]
    assert started_worker is worker
    assert isinstance(on_finished, partial)
    on_finished()
    assert env.controller._active_artist_image_workers == []


# --- playback -------------------------------------------------------------------------


class Playback:
    def __init__(self) -> None:
        self.current_track: Track | None = None
        self.registrations = 0
        self.paused = False
        self.duration = 0

    def is_paused(self) -> bool:
        return self.paused

    def play(self, track: Track) -> None:
        self.current_track = track

    def stop(self) -> Track | None:
        track, self.current_track = self.current_track, None
        return track

    def finish_current(self) -> Track | None:
        return self.stop()

    def pause(self) -> None:
        self.paused = True

    def resume(self) -> None:
        self.paused = False

    def seek(self, _position_ms: int) -> None:
        return None

    def position_ms(self) -> int:
        return 0

    def duration_ms(self) -> int:
        return self.duration

    def set_volume(self, _volume: int) -> None:
        return None

    def set_muted(self, _muted: bool) -> None:
        return None

    def on_position_changed(self, _callback) -> None:
        self.registrations += 1

    def on_duration_changed(self, _callback) -> None:
        return None

    def on_finished(self, _callback) -> None:
        return None


@pytest.fixture
def playback(env):
    service = Playback()
    env.controller._playback_service = service  # type: ignore[assignment]
    return service


def test_playback_callbacks_are_connected_once_and_not_without_a_service(env) -> None:
    env.controller._connect_playback_callbacks()
    assert env.controller._playback_callbacks_connected is False

    service = Playback()
    env.controller._playback_service = service  # type: ignore[assignment]
    _ = env.controller.playback_service
    _ = env.controller.playback_service

    assert service.registrations == 1


def test_play_track_announces_now_playing_with_duration(env, playback, tmp_path) -> None:
    env.spy("set_now_playing")
    path = tmp_path / "a.mp3"
    path.write_bytes(b"x")
    track = Track(
        artist="Artist", title="Title", local_path=str(path), status=TrackStatus.DOWNLOADED
    )
    playback.duration = 200_000
    updates: list[tuple] = []
    env.controller._scrobbling_service = SimpleNamespace(  # type: ignore[assignment]
        update_now_playing=lambda *args: updates.append(args)
    )
    submitted: list = []
    env.monkeypatch.setattr(
        env.controller, "_submit_background_call", lambda operation: submitted.append(operation)
    )

    env.controller._play_track(track)

    env.window.set_now_playing.assert_called_once_with(track)
    assert "Updating Last.fm now-playing for Artist - Title." in env.feedback()
    submitted[0]()
    assert updates == [("Artist", "Title", 200)]


def test_load_artist_image_shows_the_artist_while_loading(env) -> None:
    env.spy("set_artist_image")
    created: list[str] = []
    env.controller.artist_image_worker_factory = lambda artist, _client: created.append(artist)  # type: ignore[assignment]
    record(env, "_run_artist_image_worker")

    env.controller._load_artist_image("Artist")
    assert created == []

    env.controller._artist_images_enabled = True
    env.controller._load_artist_image("Artist")

    env.window.set_artist_image.assert_called_once_with(None, None, "Artist")
    assert created == ["Artist"]


@pytest.mark.parametrize(
    ("position", "duration", "expected"),
    [(0, 0, []), (1, 1, [0]), (200_000, 200_000, [200])],
)
def test_maybe_scrobble_threshold_and_payload(env, playback, position, duration, expected) -> None:
    scrobbles: list[dict] = []
    env.controller._scrobbling_service = SimpleNamespace(  # type: ignore[assignment]
        scrobble=lambda **kwargs: scrobbles.append(kwargs)
    )
    env.controller._playback_start_time = 1234
    playback.current_track = Track(artist="Artist", title="Title")
    env.monkeypatch.setattr(
        env.controller, "_submit_background_call", lambda operation: operation()
    )

    env.controller._maybe_scrobble(position, duration)

    assert scrobbles == [
        {"artist": "Artist", "title": "Title", "timestamp": 1234, "duration_seconds": seconds}
        for seconds in expected
    ]
    announced = "Submitting Last.fm scrobble for Artist - Title." in env.feedback()
    assert announced is bool(expected)


def test_play_prepared_track_finds_the_track_after_others(env, playback, tmp_path) -> None:
    path = tmp_path / "b.mp3"
    path.write_bytes(b"x")
    target = Track(artist="A", title="Target", local_path=str(path), status=TrackStatus.DOWNLOADED)
    env.window.set_tracks([Track(artist="A", title="Other"), target])

    env.controller._play_prepared_track(target.cache_key)

    assert playback.current_track == target


def test_prepare_selected_track_clears_a_youtube_stop(env) -> None:
    record(env, "resolve_youtube_urls")
    env.controller._youtube_stop_requested = True

    env.controller._prepare_selected_track_for_playback(Track(artist="A", title="T"))

    assert env.controller._youtube_stop_requested is False


def test_play_selected_track_passes_no_choice_without_randomize(env, playback) -> None:
    env.spy("first_or_random_downloaded_track")

    env.controller.play_selected_track()

    env.window.first_or_random_downloaded_track.assert_called_once_with(None)


def test_pause_toggle_back_sets_unpaused_controls(env, playback) -> None:
    env.spy("set_playback_controls")
    playback.paused = True

    env.controller.pause_playback()

    env.window.set_playback_controls.assert_called_once_with(active=True, paused=False)


def test_stop_and_finish_reset_scrobble_state(env, playback) -> None:
    env.spy("set_playback_controls")
    record(env, "_continue_playback_from")
    playback.current_track = Track(artist="A", title="T")
    env.controller._scrobble_submitted = True

    env.controller.stop_playback()
    assert env.controller._scrobble_submitted is False

    playback.current_track = Track(artist="A", title="T")
    env.controller._scrobble_submitted = True
    env.controller._handle_playback_finished()

    assert env.controller._scrobble_submitted is False
    assert env.window.set_playback_controls.call_args_list == [
        call(active=False),
        call(active=False),
    ]


def test_seek_reports_whole_seconds(env, playback) -> None:
    env.controller.seek_playback(100_000)

    assert "Seeked playback to 100 seconds." in env.feedback()

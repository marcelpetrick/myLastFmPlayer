"""Fire every signal _run_worker connects and check which handler gets what.

Counting connected callbacks is not enough: a callback that drops the username,
passes the wrong payload or ignores the worker generation would still be counted.
"""

from __future__ import annotations

import pytest

from my_lastfm_player import controller as controller_module
from my_lastfm_player import worker_threads as worker_threads_module
from my_lastfm_player.controller import ApplicationController
from my_lastfm_player.ui.main_window import MainWindow


class Signal:
    def __init__(self) -> None:
        self.callbacks: list = []

    def connect(self, callback) -> None:
        self.callbacks.append(callback)

    def fire(self, *args) -> None:
        for callback in self.callbacks:
            callback(*args)


class Thread:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.started = Signal()
        self.finished = Signal()

    def start(self) -> None:
        return None

    def quit(self) -> None:
        return None

    def deleteLater(self) -> None:  # noqa: N802 - Qt API
        return None


class Worker:
    def __init__(self, username: str | None = None) -> None:
        if username is not None:
            self.username = username
        self.progress = Signal()
        self.error = Signal()
        self.finished = Signal()

    def moveToThread(self, _thread) -> None:  # noqa: N802 - Qt API
        return None

    def run(self) -> None:
        return None

    def deleteLater(self) -> None:  # noqa: N802 - Qt API
        return None


class FetchWorker(Worker):
    def __init__(self, username=None) -> None:
        super().__init__(username)
        self.tracks_updated = Signal()
        self.tracks_loaded = Signal()
        self.fetch_stopped = Signal()


class LookupWorker(Worker):
    def __init__(self, username=None) -> None:
        super().__init__(username)
        self.track_updated = Signal()
        self.tracks_resolved = Signal()


class DownloadWorker(Worker):
    def __init__(self, username=None) -> None:
        super().__init__(username)
        self.track_updated = Signal()
        self.tracks_downloaded = Signal()


HANDLERS = (
    "_handle_tracks_updated",
    "_handle_tracks_loaded",
    "_handle_fetch_stopped",
    "_handle_track_updated",
    "_handle_tracks_resolved",
    "_handle_tracks_downloaded",
)


@pytest.fixture
def wired(qapp, monkeypatch):
    threads: list[Thread] = []

    def make_thread(parent):
        thread = Thread(parent)
        threads.append(thread)
        return thread

    monkeypatch.setattr(worker_threads_module, "QThread", make_thread)
    monkeypatch.setattr(controller_module, "FetchLovedTracksWorker", FetchWorker)
    monkeypatch.setattr(controller_module, "LookupTracksWorker", LookupWorker)
    monkeypatch.setattr(controller_module, "DownloadTracksWorker", DownloadWorker)
    window = MainWindow()
    controller = ApplicationController(window)
    controller._workflow_username = "alice"
    calls: list[tuple] = []
    for name in HANDLERS:
        monkeypatch.setattr(
            controller, name, lambda user, payload, name=name: calls.append((name, user, payload))
        )
    monkeypatch.setattr(
        controller,
        "_handle_worker_progress",
        lambda user, value, label, stage: calls.append(("progress", user, value, label, stage)),
    )
    monkeypatch.setattr(
        controller,
        "_handle_worker_error_for",
        lambda user, message, stage: calls.append(("error", user, message, stage)),
    )
    youtube_states: list[bool] = []
    monkeypatch.setattr(
        window, "set_youtube_work_state", lambda active: youtube_states.append(active)
    )
    return controller, window, calls, threads, youtube_states


def test_fetch_worker_signals_reach_their_handlers_with_username_and_payload(wired) -> None:
    controller, _window, calls, _threads, youtube_states = wired
    worker = FetchWorker("alice")

    controller._run_worker(worker)  # type: ignore[arg-type]
    worker.progress.fire(40, "Fetching")
    worker.error.fire("boom")
    worker.tracks_updated.fire("alice", ["u"])
    worker.tracks_loaded.fire("alice", ["l"])
    worker.fetch_stopped.fire("alice", ["s"])

    assert calls == [
        ("progress", "alice", 40, "Fetching", "discovery"),
        ("error", "alice", "boom", "discovery"),
        ("_handle_tracks_updated", "alice", ["u"]),
        ("_handle_tracks_loaded", "alice", ["l"]),
        ("_handle_fetch_stopped", "alice", ["s"]),
    ]
    assert youtube_states == []


@pytest.mark.parametrize(
    ("worker_type", "stage", "signals"),
    [
        (LookupWorker, "lookup", ("track_updated", "tracks_resolved")),
        (DownloadWorker, "download", ("track_updated", "tracks_downloaded")),
    ],
)
def test_youtube_worker_signals_reach_their_handlers(wired, worker_type, stage, signals) -> None:
    controller, _window, calls, _threads, youtube_states = wired
    worker = worker_type("alice")

    controller._run_worker(worker)  # type: ignore[arg-type]
    worker.progress.fire(10, "Working")
    worker.error.fire("bad")
    for signal in signals:
        getattr(worker, signal).fire("alice", signal)

    handler = {
        "track_updated": "_handle_track_updated",
        "tracks_resolved": "_handle_tracks_resolved",
        "tracks_downloaded": "_handle_tracks_downloaded",
    }
    assert calls == [
        ("progress", "alice", 10, "Working", stage),
        ("error", "alice", "bad", stage),
        *[(handler[signal], "alice", signal) for signal in signals],
    ]
    assert youtube_states == [True]


@pytest.mark.parametrize("worker_type", [FetchWorker, LookupWorker, DownloadWorker])
def test_stale_or_foreign_emissions_are_dropped(wired, worker_type) -> None:
    controller, _window, calls, _threads, _states = wired
    worker = worker_type("alice")
    controller._run_worker(worker)  # type: ignore[arg-type]
    payload_signals = [
        name
        for name in (
            "tracks_updated",
            "tracks_loaded",
            "fetch_stopped",
            "track_updated",
            "tracks_resolved",
            "tracks_downloaded",
        )
        if hasattr(worker, name)
    ]

    for name in payload_signals:
        getattr(worker, name).fire("bob", [])
    controller._workflow_generation += 1
    worker.progress.fire(1, "late")
    worker.error.fire("late")
    for name in payload_signals:
        getattr(worker, name).fire("alice", [])

    assert calls == []


def test_progress_from_a_worker_of_another_user_is_dropped(wired) -> None:
    controller, _window, calls, _threads, _states = wired
    worker = FetchWorker("bob")

    controller._run_worker(worker)  # type: ignore[arg-type]
    worker.progress.fire(5, "x")
    worker.error.fire("x")

    assert calls == []


def test_worker_without_username_reports_for_the_current_workflow_user(wired) -> None:
    controller, _window, calls, _threads, _states = wired
    worker = Worker()

    controller._run_worker(worker)  # type: ignore[arg-type]
    worker.progress.fire(7, "generic")

    assert calls == [("progress", "alice", 7, "generic", "discovery")]


def test_run_worker_bookkeeping_and_completion_wiring(wired) -> None:
    controller, window, _calls, threads, _states = wired
    controller._workflow_generation = 4
    first, second = FetchWorker("alice"), LookupWorker("alice")

    controller._run_worker(first)  # type: ignore[arg-type]
    controller._run_worker(second)  # type: ignore[arg-type]

    assert controller._running_worker_count == 2
    assert controller._worker_generations[first] == 4
    assert controller._active_workers == [first, second]
    assert not window.fetch_button.isEnabled()
    assert controller._complete_worker_run in first.finished.callbacks

    threads[0].finished.fire()

    assert controller._active_workers == [second]
    assert first not in controller._worker_generations

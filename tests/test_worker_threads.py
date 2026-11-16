from __future__ import annotations

from PyQt6 import sip
from PyQt6.QtCore import QCoreApplication, QDeadlineTimer, QEvent, QObject, QThread, pyqtSignal

from my_lastfm_player import worker_threads
from my_lastfm_player.worker_threads import (
    SHUTDOWN_TERMINATE_WAIT_MS,
    SHUTDOWN_WAIT_MS,
    WorkerThreadPool,
)


class _Worker(QObject):
    finished = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.ran = False

    def run(self) -> None:
        self.ran = True
        self.finished.emit()


def _process_events_until(condition, timeout_ms: int = 5000) -> None:
    deadline = QDeadlineTimer(timeout_ms)
    while not condition() and not deadline.hasExpired():
        QCoreApplication.processEvents()
    assert condition()


def _join(thread: QThread) -> None:
    """Let the thread fully exit before its parent can be garbage-collected."""

    if not sip.isdeleted(thread):
        assert thread.wait(5000)
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete.value)


def test_started_thread_is_owned_by_the_parent_and_reports_completion(qapp) -> None:
    parent = QObject()
    pool = WorkerThreadPool(parent)
    worker = _Worker()
    finished: list[bool] = []

    thread = pool.start(worker, on_finished=lambda: finished.append(True))

    assert thread.parent() is parent
    assert pool.active_count == 1
    _process_events_until(lambda: finished == [True] and pool.active_count == 0)
    _join(thread)
    assert worker.ran


def test_start_without_completion_callback_still_forgets_the_thread(qapp) -> None:
    parent = QObject()
    pool = WorkerThreadPool(parent)

    worker = _Worker()  # callers own the worker; an unreferenced one is collected

    thread = pool.start(worker)

    _process_events_until(lambda: pool.active_count == 0)
    _join(thread)
    assert worker.ran


class _StuckThread:
    def __init__(self, *, stops: bool) -> None:
        self.stops = stops
        self.calls: list[tuple] = []

    def quit(self) -> None:
        self.calls.append(("quit",))

    def wait(self, milliseconds: int) -> bool:
        self.calls.append(("wait", milliseconds))
        return self.stops

    def terminate(self) -> None:
        self.calls.append(("terminate",))


def test_shutdown_joins_a_cooperative_thread_without_terminating_it() -> None:
    pool = WorkerThreadPool(QObject())
    thread = _StuckThread(stops=True)
    pool._threads.append(thread)  # type: ignore[arg-type]

    pool.shutdown()

    assert thread.calls == [("quit",), ("wait", SHUTDOWN_WAIT_MS)]


def test_shutdown_terminates_a_thread_that_does_not_stop_in_time() -> None:
    pool = WorkerThreadPool(QObject())
    thread = _StuckThread(stops=False)
    pool._threads.append(thread)  # type: ignore[arg-type]

    pool.shutdown()

    assert thread.calls == [
        ("quit",),
        ("wait", SHUTDOWN_WAIT_MS),
        ("terminate",),
        ("wait", SHUTDOWN_TERMINATE_WAIT_MS),
    ]


def test_shutdown_budgets_are_three_seconds_then_one_second() -> None:
    assert worker_threads.SHUTDOWN_WAIT_MS == 3000
    assert worker_threads.SHUTDOWN_TERMINATE_WAIT_MS == 1000

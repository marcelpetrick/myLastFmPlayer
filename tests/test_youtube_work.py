from __future__ import annotations

import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from my_lastfm_player import youtube_work
from my_lastfm_player.youtube_work import (
    WorkCancelled,
    YouTubeWorkLimiter,
    run_cancellable_command,
)


def test_limiter_caps_all_work_and_serializes_matching_tracks() -> None:
    limiter = YouTubeWorkLimiter(2)
    state_lock = threading.Lock()
    active = 0
    max_active = 0
    active_keys: set[str] = set()

    def work(key: str) -> None:
        nonlocal active, max_active
        with limiter.slot(work_key=key) as acquired:
            assert acquired
            with state_lock:
                assert key not in active_keys
                active_keys.add(key)
                active += 1
                max_active = max(max_active, active)
            time.sleep(0.03)
            with state_lock:
                active -= 1
                active_keys.remove(key)

    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(work, ["same", "same", "other-1", "other-2"]))

    assert max_active == 2
    assert limiter.active == 0
    assert limiter.limit == 2

    limiter.configure(99)
    assert limiter.limit == 5
    limiter.configure(0)
    assert limiter.limit == 1


def test_waiting_limiter_slot_wakes_on_operation_cancellation() -> None:
    limiter = YouTubeWorkLimiter(1)
    stop_event = threading.Event()
    result: list[bool] = []

    with limiter.slot() as acquired:
        assert acquired
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_try_slot, limiter, stop_event, result)
            stop_event.set()
            future.result(timeout=2)

    assert result == [False]


def test_limiter_rejects_an_already_cancelled_operation() -> None:
    stop_event = threading.Event()
    stop_event.set()

    with YouTubeWorkLimiter().slot(stop_event) as acquired:
        assert not acquired


def _try_slot(
    limiter: YouTubeWorkLimiter, stop_event: threading.Event, result: list[bool]
) -> None:
    with limiter.slot(stop_event) as acquired:
        result.append(acquired)


def test_cancellable_command_terminates_active_process_promptly() -> None:
    stop_event = threading.Event()
    timer = threading.Timer(0.1, stop_event.set)
    timer.start()
    started = time.monotonic()
    try:
        with pytest.raises(WorkCancelled):
            run_cancellable_command(
                [sys.executable, "-c", "import time; time.sleep(30)"],
                stop_event=stop_event,
                timeout=30,
            )
    finally:
        timer.cancel()

    assert time.monotonic() - started < 3


def test_cancellable_command_returns_completed_output() -> None:
    completed = run_cancellable_command(
        [sys.executable, "-c", "print('ready')"],
        stop_event=None,
        timeout=2,
    )

    assert completed.returncode == 0
    assert completed.stdout.strip() == "ready"


def test_cancellable_command_enforces_timeout() -> None:
    with pytest.raises(subprocess.TimeoutExpired):
        run_cancellable_command(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            stop_event=None,
            timeout=0.05,
        )


def test_process_group_is_killed_if_terminate_does_not_finish(monkeypatch) -> None:
    calls: list[int] = []

    class FakeProcess:
        pid = 123

        def communicate(self, timeout=None):
            if timeout is not None:
                raise subprocess.TimeoutExpired("command", timeout)
            return "", ""

    monkeypatch.setattr(youtube_work.os, "killpg", lambda _pid, sig: calls.append(sig))

    youtube_work._terminate_process(FakeProcess())  # type: ignore[arg-type]

    assert calls == [youtube_work.signal.SIGTERM, youtube_work.signal.SIGKILL]

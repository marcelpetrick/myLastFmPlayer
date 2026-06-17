from __future__ import annotations

from concurrent.futures import Future

import pytest

from my_lastfm_player.background_tasks import BackgroundTaskRunner


def test_background_task_runner_tracks_and_waits_for_successful_tasks() -> None:
    runner = BackgroundTaskRunner("test-success", "task failed")
    results: list[str] = []

    try:
        runner.submit(results.append, "done")
        runner.wait()
    finally:
        runner.shutdown()

    assert results == ["done"]
    assert runner.futures == set()


def test_background_task_runner_logs_unexpected_failures(caplog) -> None:
    runner = BackgroundTaskRunner("test-failure", "custom failure")
    future: Future[object] = Future()
    future.set_exception(RuntimeError("boom"))

    runner.handle_task_done(future)
    runner.shutdown()

    assert "custom failure" in caplog.text
    assert runner.futures == set()


def test_background_task_runner_wait_propagates_task_failure() -> None:
    runner = BackgroundTaskRunner("test-wait-failure", "task failed")
    future: Future[object] = Future()
    future.set_exception(RuntimeError("boom"))
    runner.futures.add(future)

    try:
        with pytest.raises(RuntimeError, match="boom"):
            runner.wait()
    finally:
        runner.shutdown()

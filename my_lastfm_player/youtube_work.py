"""Shared concurrency and cancellation primitives for yt-dlp work."""

from __future__ import annotations

import os
import signal
import subprocess
import time
from collections.abc import Hashable, Iterator, Sequence
from contextlib import contextmanager
from threading import Condition, Event

MIN_PARALLEL_WORK = 1
MAX_PARALLEL_WORK = 5
PROCESS_POLL_SECONDS = 0.05
PROCESS_TERMINATE_SECONDS = 2.0


class WorkCancelled(RuntimeError):
    """Raised after an active external process is terminated by cancellation."""


class YouTubeWorkLimiter:
    """Enforce one process limit across lookup and download operations."""

    def __init__(self, limit: int = MAX_PARALLEL_WORK) -> None:
        self._condition = Condition()
        self._active = 0
        self._active_keys: set[Hashable] = set()
        self._limit = _clamp_limit(limit)

    @property
    def limit(self) -> int:
        with self._condition:
            return self._limit

    @property
    def active(self) -> int:
        with self._condition:
            return self._active

    def configure(self, limit: int) -> None:
        """Apply a new limit to work that has not acquired a slot yet."""

        with self._condition:
            self._limit = _clamp_limit(limit)
            self._condition.notify_all()

    @contextmanager
    def slot(
        self,
        stop_event: Event | None = None,
        work_key: Hashable | None = None,
    ) -> Iterator[bool]:
        """Acquire global capacity and serialize operations targeting one track."""

        acquired = False
        with self._condition:
            while self._active >= self._limit or (
                work_key is not None and work_key in self._active_keys
            ):
                if stop_event is not None and stop_event.is_set():
                    yield False
                    return
                self._condition.wait(PROCESS_POLL_SECONDS)
            if stop_event is not None and stop_event.is_set():
                yield False
                return
            self._active += 1
            if work_key is not None:
                self._active_keys.add(work_key)
            acquired = True
        try:
            yield True
        finally:
            if acquired:
                with self._condition:
                    self._active -= 1
                    if work_key is not None:
                        self._active_keys.remove(work_key)
                    self._condition.notify_all()


def run_cancellable_command(
    command: Sequence[str],
    *,
    stop_event: Event | None,
    timeout: float,
) -> subprocess.CompletedProcess[str]:
    """Run a command while supporting prompt terminate/kill cancellation."""

    process = subprocess.Popen(  # pylint: disable=consider-using-with
        # noqa: S603 - command is assembled without a shell.
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        start_new_session=os.name != "nt",
    )
    started_at = time.monotonic()
    while True:
        if stop_event is not None and stop_event.is_set():
            _terminate_process(process)
            raise WorkCancelled("YouTube work cancelled")
        remaining = timeout - (time.monotonic() - started_at)
        if remaining <= 0:
            _terminate_process(process)
            raise subprocess.TimeoutExpired(command, timeout)
        try:
            stdout, stderr = process.communicate(timeout=min(PROCESS_POLL_SECONDS, remaining))
        except subprocess.TimeoutExpired:
            continue
        return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


def _terminate_process(process: subprocess.Popen[str]) -> None:
    if os.name == "nt":  # pragma: no cover - Windows process API
        process.terminate()
    else:
        os.killpg(process.pid, signal.SIGTERM)
    try:
        process.communicate(timeout=PROCESS_TERMINATE_SECONDS)
    except subprocess.TimeoutExpired:
        if os.name == "nt":  # pragma: no cover - Windows process API
            process.kill()
        else:
            os.killpg(process.pid, signal.SIGKILL)
        process.communicate()


def _clamp_limit(limit: int) -> int:
    return max(MIN_PARALLEL_WORK, min(MAX_PARALLEL_WORK, int(limit)))

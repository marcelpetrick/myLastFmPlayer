from __future__ import annotations

import logging
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any

LOGGER = logging.getLogger(__name__)


class BackgroundTaskRunner:
    """Run fire-and-forget background tasks and log unexpected failures."""

    def __init__(self, thread_name_prefix: str, failure_message: str) -> None:
        self._executor = ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix=thread_name_prefix,
        )
        self._failure_message = failure_message
        self.futures: set[Future[Any]] = set()

    def submit(self, task: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        future = self._executor.submit(task, *args, **kwargs)
        self.futures.add(future)
        future.add_done_callback(self.handle_task_done)

    def handle_task_done(self, future: Future[Any]) -> None:
        self.futures.discard(future)
        try:
            future.result()
        except Exception:  # noqa: BLE001 - executor boundary logs unexpected failures.
            LOGGER.exception(self._failure_message)

    def wait(self, timeout: float = 5) -> None:
        for future in list(self.futures):
            future.result(timeout=timeout)

    def shutdown(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=True)

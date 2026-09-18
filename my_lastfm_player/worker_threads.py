"""Ownership of the ``QThread`` lifecycle shared by every background worker."""

from __future__ import annotations

import logging
from collections.abc import Callable

from PyQt6.QtCore import QObject, QThread

LOGGER = logging.getLogger(__name__)

# A cancelled yt-dlp call ends within one poll interval; a Last.fm page request can
# still be inside its 20s HTTP timeout, so quitting does not wait for that.
SHUTDOWN_WAIT_MS = 3000
SHUTDOWN_TERMINATE_WAIT_MS = 1000


class WorkerThreadPool:
    """Start worker objects on owned threads and retire them together.

    Workflow, artwork, and service-call workers all need the same wiring: move the
    worker to a fresh thread, run it when the thread starts, quit the thread when the
    worker finishes, and delete both afterwards. Keeping that in one place also gives
    shutdown a single list of threads to join, which is what stops the application
    from destroying a running thread on its way out.
    """

    def __init__(self, parent: QObject) -> None:
        self._parent = parent
        self._threads: list[QThread] = []

    @property
    def active_count(self) -> int:
        """Return how many worker threads have not finished yet."""

        return len(self._threads)

    def start(self, worker: QObject, on_finished: Callable[[], None] | None = None) -> QThread:
        """Run ``worker`` on a new owned thread and return that thread.

        ``worker`` must expose a ``run`` slot and a ``finished`` signal. ``on_finished``
        runs on the UI thread once the worker's thread has fully stopped.
        """

        thread = QThread(self._parent)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda: self._forget(thread))
        if on_finished is not None:
            thread.finished.connect(on_finished)
        self._threads.append(thread)
        LOGGER.info(
            "Starting thread for %s; active_threads=%d",
            worker.__class__.__name__,
            len(self._threads),
        )
        thread.start()
        return thread

    def shutdown(self) -> None:
        """Join every owned thread within a bounded time before they are destroyed."""

        for thread in tuple(self._threads):
            self._join(thread)

    def _forget(self, thread: QThread) -> None:
        if thread in self._threads:
            self._threads.remove(thread)
        LOGGER.info("Thread finished; active_threads=%d", len(self._threads))

    @staticmethod
    def _join(thread: QThread) -> None:
        thread.quit()
        if thread.wait(SHUTDOWN_WAIT_MS):
            return
        LOGGER.warning(
            "Background thread did not stop within %sms; terminating it", SHUTDOWN_WAIT_MS
        )
        thread.terminate()
        thread.wait(SHUTDOWN_TERMINATE_WAIT_MS)

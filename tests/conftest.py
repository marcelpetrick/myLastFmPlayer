from __future__ import annotations

import os
import sys
from collections.abc import Iterator

import pytest
from PyQt6.QtWidgets import QApplication

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    return QApplication.instance() or QApplication([])


@pytest.fixture(autouse=True)
def fail_on_unhandled_qt_slot_exception() -> Iterator[None]:
    """Turn an exception raised inside a Qt slot into a test failure.

    Without a custom ``sys.excepthook`` PyQt aborts the whole process on such an
    exception, which kills the pytest run (and every mutmut worker) instead of
    failing the one test that triggered it.
    """

    errors: list[BaseException] = []
    previous_hook = sys.excepthook
    sys.excepthook = lambda _type, value, _traceback: errors.append(value)
    try:
        yield
    finally:
        sys.excepthook = previous_hook
    if errors:
        pytest.fail(f"Unhandled exception in a Qt slot: {errors[0]!r}")

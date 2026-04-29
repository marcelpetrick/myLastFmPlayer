from __future__ import annotations

from PyQt6.QtWidgets import QApplication

from my_lastfm_player import __version__
from my_lastfm_player.ui.main_window import MainWindow


def test_package_version_is_defined() -> None:
    assert __version__ == "0.1.0"


def test_main_window_builds_mvp_shell() -> None:
    app = QApplication.instance() or QApplication([])

    window = MainWindow()

    assert app.applicationName() in {"", "myLastFmPlayer"}
    assert window.windowTitle() == "myLastFmPlayer"
    assert window.username_input.placeholderText() == "Enter username"
    assert window.track_table.columnCount() == 3
    assert window.track_table.rowCount() == 2
    assert window.concurrency_input.value() == 2
    assert window.progress_bar.format() == "Idle"


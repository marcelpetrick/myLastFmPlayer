from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from my_lastfm_player import __version__
from my_lastfm_player.controller import ApplicationController
from my_lastfm_player.logging_config import configure_logging
from my_lastfm_player.ui.main_window import MainWindow


def main() -> int:
    """Create the Qt application, start the controller, and return the exit code."""

    configure_logging()
    print(f"myLastFmPlayer {__version__}")

    app = QApplication(sys.argv)
    app.setApplicationName("myLastFmPlayer")
    app.setOrganizationName("Marcel Petrick")

    window = MainWindow()
    controller = ApplicationController(window)
    controller.start()
    window.show()

    return app.exec()

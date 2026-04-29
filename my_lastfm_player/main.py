from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from my_lastfm_player.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("myLastFmPlayer")
    app.setOrganizationName("Marcel Petrick")

    window = MainWindow()
    window.show()

    return app.exec()


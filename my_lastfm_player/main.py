from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from my_lastfm_player import __display_version__
from my_lastfm_player.controller import ApplicationController
from my_lastfm_player.i18n import TranslationManager
from my_lastfm_player.logging_config import configure_logging
from my_lastfm_player.settings import AppSettings
from my_lastfm_player.themes import ThemeMode, apply_theme
from my_lastfm_player.ui.main_window import MainWindow


def main() -> int:
    """Create the Qt application, start the controller, and return the exit code."""

    configure_logging()
    print(f"myLastFmPlayer {__display_version__}")

    app = QApplication(sys.argv)
    app.setApplicationName("myLastFmPlayer")
    app.setOrganizationName("Marcel Petrick")

    settings = AppSettings()
    translation_manager = TranslationManager(app)
    translation_manager.set_language(settings.language_code())
    apply_theme(app, settings.theme_mode())
    window = MainWindow(translation_manager=translation_manager)
    window.set_theme_mode(settings.theme_mode().value)
    window.theme_requested.connect(lambda mode: _apply_and_save_theme(app, settings, mode))
    window.language_changed.connect(
        lambda: settings.set_language_code(translation_manager.current_language)
    )
    controller = ApplicationController(window)
    controller.start()
    window.show()

    return app.exec()


def _apply_and_save_theme(app: QApplication, settings: AppSettings, mode: str) -> None:
    theme_mode = ThemeMode(mode)
    apply_theme(app, theme_mode)
    settings.set_theme_mode(theme_mode)

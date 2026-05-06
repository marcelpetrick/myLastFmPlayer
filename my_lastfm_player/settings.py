"""Persisted user settings backed by Qt's platform settings store."""

from __future__ import annotations

from PyQt6.QtCore import QSettings

from my_lastfm_player.i18n import DEFAULT_LANGUAGE_CODE, language_by_code
from my_lastfm_player.themes import ThemeMode

THEME_KEY = "appearance/theme"
LANGUAGE_KEY = "appearance/language"


class AppSettings:
    """Load and save application preferences that should survive restarts."""

    def __init__(self, settings: QSettings | None = None) -> None:
        self._settings = settings or QSettings()

    def theme_mode(self) -> ThemeMode:
        """Return the persisted theme, falling back to light when invalid or absent."""

        value = self._settings.value(THEME_KEY, ThemeMode.LIGHT.value, str)
        try:
            return ThemeMode(value)
        except ValueError:
            return ThemeMode.LIGHT

    def set_theme_mode(self, mode: ThemeMode) -> None:
        """Persist the selected theme mode."""

        self._settings.setValue(THEME_KEY, mode.value)

    def language_code(self) -> str:
        """Return the persisted language code, falling back to English when invalid."""

        value = self._settings.value(LANGUAGE_KEY, DEFAULT_LANGUAGE_CODE, str)
        try:
            return language_by_code(value).code
        except ValueError:
            return DEFAULT_LANGUAGE_CODE

    def set_language_code(self, code: str) -> None:
        """Persist the selected language code."""

        self._settings.setValue(LANGUAGE_KEY, language_by_code(code).code)

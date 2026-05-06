from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QSettings

from my_lastfm_player.settings import LANGUAGE_KEY, THEME_KEY, AppSettings
from my_lastfm_player.themes import ThemeMode


def _ini_settings(path: Path) -> QSettings:
    return QSettings(str(path), QSettings.Format.IniFormat)


def test_settings_persist_theme_and_language(tmp_path: Path) -> None:
    path = tmp_path / "settings.ini"
    settings = AppSettings(_ini_settings(path))

    settings.set_theme_mode(ThemeMode.LILAC)
    settings.set_language_code("de")

    reloaded = AppSettings(_ini_settings(path))
    assert reloaded.theme_mode() is ThemeMode.LILAC
    assert reloaded.language_code() == "de"


def test_settings_fall_back_for_invalid_values(tmp_path: Path) -> None:
    raw_settings = _ini_settings(tmp_path / "settings.ini")
    raw_settings.setValue(THEME_KEY, "sepia")
    raw_settings.setValue(LANGUAGE_KEY, "xx")

    settings = AppSettings(raw_settings)

    assert settings.theme_mode() is ThemeMode.LIGHT
    assert settings.language_code() == "en"

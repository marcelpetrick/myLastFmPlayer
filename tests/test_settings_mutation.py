"""Type conversion and sanitising contract of AppSettings against a real QSettings store."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QByteArray, QSettings

from my_lastfm_player.settings import (
    LANGUAGE_KEY,
    LAST_USERNAME_KEY,
    MUTED_KEY,
    RANDOMIZE_PLAYBACK_KEY,
    SCROBBLING_ENABLED_KEY,
    THEME_KEY,
    AppSettings,
)
from my_lastfm_player.themes import ThemeMode


def _raw(tmp_path: Path) -> QSettings:
    return QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)


def test_theme_and_language_stored_as_bytes_are_read_as_text(tmp_path: Path) -> None:
    raw = _raw(tmp_path)
    raw.setValue(THEME_KEY, QByteArray(b"dark"))
    raw.setValue(LANGUAGE_KEY, QByteArray(b"de"))

    settings = AppSettings(raw)

    assert settings.theme_mode() is ThemeMode.DARK
    assert settings.language_code() == "de"


def test_last_username_converts_non_text_values_to_text(tmp_path: Path) -> None:
    raw = _raw(tmp_path)
    raw.setValue(LAST_USERNAME_KEY, 42)

    assert AppSettings(raw).last_username() == "42"


def test_last_username_ignores_a_stored_list(tmp_path: Path) -> None:
    raw = _raw(tmp_path)
    raw.setValue(LAST_USERNAME_KEY, ["alice", "bob"])

    assert AppSettings(raw).last_username() == ""


def test_textual_false_flags_are_read_as_false(tmp_path: Path) -> None:
    raw = _raw(tmp_path)
    for key in (MUTED_KEY, RANDOMIZE_PLAYBACK_KEY, SCROBBLING_ENABLED_KEY):
        raw.setValue(key, "false")

    settings = AppSettings(raw)

    assert settings.muted() is False
    assert settings.randomize_playback() is False
    assert settings.scrobbling_enabled() is False

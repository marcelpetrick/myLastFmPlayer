from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QSettings

from my_lastfm_player.settings import (
    DEFAULT_DOWNLOAD_CONCURRENCY,
    DOWNLOAD_CONCURRENCY_KEY,
    KEEP_DATA_ON_QUIT_KEY,
    LANGUAGE_KEY,
    MAX_DOWNLOAD_CONCURRENCY,
    MIN_DOWNLOAD_CONCURRENCY,
    RANDOMIZE_PLAYBACK_KEY,
    THEME_KEY,
    AppSettings,
)
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


def test_scrobbling_enabled_defaults_to_true_and_persists(tmp_path: Path) -> None:
    path = tmp_path / "settings.ini"
    settings = AppSettings(_ini_settings(path))

    assert settings.scrobbling_enabled()

    settings.set_scrobbling_enabled(False)

    reloaded = AppSettings(_ini_settings(path))
    assert not reloaded.scrobbling_enabled()


def test_scrobbling_enabled_can_use_legacy_default(tmp_path: Path) -> None:
    raw = _ini_settings(tmp_path / "settings.ini")
    raw.setValue(KEEP_DATA_ON_QUIT_KEY, True)  # unrelated write to confirm key import works

    assert not AppSettings(raw).scrobbling_enabled(default_enabled=False)


def test_keep_data_on_quit_defaults_to_false_and_persists(tmp_path: Path) -> None:
    path = tmp_path / "settings.ini"
    settings = AppSettings(_ini_settings(path))

    assert settings.keep_data_on_quit() is False

    settings.set_keep_data_on_quit(True)

    reloaded = AppSettings(_ini_settings(path))
    assert reloaded.keep_data_on_quit() is True


def test_randomize_playback_defaults_to_false_and_persists(tmp_path: Path) -> None:
    path = tmp_path / "settings.ini"
    settings = AppSettings(_ini_settings(path))

    assert settings.randomize_playback() is False

    settings.set_randomize_playback(True)

    reloaded = AppSettings(_ini_settings(path))
    assert reloaded.randomize_playback() is True


def test_randomize_playback_reads_raw_settings_bool(tmp_path: Path) -> None:
    raw = _ini_settings(tmp_path / "settings.ini")
    raw.setValue(RANDOMIZE_PLAYBACK_KEY, True)

    assert AppSettings(raw).randomize_playback() is True


def test_ytdlp_cookies_browser_defaults_to_empty_and_persists(tmp_path: Path) -> None:
    path = tmp_path / "settings.ini"
    settings = AppSettings(_ini_settings(path))

    assert settings.ytdlp_cookies_browser() == ""

    settings.set_ytdlp_cookies_browser("firefox")

    reloaded = AppSettings(_ini_settings(path))
    assert reloaded.ytdlp_cookies_browser() == "firefox"


def test_ytdlp_cookies_browser_rejects_unknown_browser(tmp_path: Path) -> None:
    raw = _ini_settings(tmp_path / "settings.ini")
    raw.setValue(KEEP_DATA_ON_QUIT_KEY, True)  # unrelated write to confirm key import works

    settings = AppSettings(raw)
    settings.set_ytdlp_cookies_browser("edge")

    assert settings.ytdlp_cookies_browser() == ""


def test_download_concurrency_defaults_persists_and_clamps(tmp_path: Path) -> None:
    path = tmp_path / "settings.ini"
    settings = AppSettings(_ini_settings(path))

    assert settings.download_concurrency() == DEFAULT_DOWNLOAD_CONCURRENCY

    settings.set_download_concurrency(7)
    assert AppSettings(_ini_settings(path)).download_concurrency() == 7

    settings.set_download_concurrency(0)
    assert settings.download_concurrency() == MIN_DOWNLOAD_CONCURRENCY

    settings.set_download_concurrency(99)
    assert settings.download_concurrency() == MAX_DOWNLOAD_CONCURRENCY


def test_download_concurrency_uses_default_for_invalid_raw_value(tmp_path: Path) -> None:
    raw = _ini_settings(tmp_path / "settings.ini")
    raw.setValue(DOWNLOAD_CONCURRENCY_KEY, "many")

    assert AppSettings(raw).download_concurrency() == DEFAULT_DOWNLOAD_CONCURRENCY

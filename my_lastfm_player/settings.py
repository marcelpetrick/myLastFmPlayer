"""Persisted user settings backed by Qt's platform settings store."""

from __future__ import annotations

from PyQt6.QtCore import QByteArray, QSettings

from my_lastfm_player.i18n import DEFAULT_LANGUAGE_CODE, language_by_code
from my_lastfm_player.playback import clamp_volume
from my_lastfm_player.themes import ThemeMode

THEME_KEY = "appearance/theme"
LANGUAGE_KEY = "appearance/language"
SCROBBLING_ENABLED_KEY = "lastfm/scrobblingenabled"
YTDLP_BROWSER_KEY = "download/cookiesbrowser"
DOWNLOAD_CONCURRENCY_KEY = "download/concurrency"
KEEP_DATA_ON_QUIT_KEY = "privacy/keepdataonquit"
RANDOMIZE_PLAYBACK_KEY = "playback/randomize"
VOLUME_KEY = "playback/volume"
MUTED_KEY = "playback/muted"
LAST_USERNAME_KEY = "lastfm/lastusername"
WINDOW_GEOMETRY_KEY = "window/geometry"

DEFAULT_VOLUME_PERCENT = 100

YTDLP_BROWSER_CHOICES = ["", "firefox", "chromium", "chrome", "brave"]
DEFAULT_DOWNLOAD_CONCURRENCY = 5
MIN_DOWNLOAD_CONCURRENCY = 1
MAX_DOWNLOAD_CONCURRENCY = 5


class AppSettings:  # pylint: disable=too-many-public-methods  # getter/setter pair per setting
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

    def scrobbling_enabled(self, default_enabled: bool = True) -> bool:
        """Return whether Last.fm scrobbling should be enabled."""

        return bool(self._settings.value(SCROBBLING_ENABLED_KEY, default_enabled, bool))

    def set_scrobbling_enabled(self, enabled: bool) -> None:
        """Persist whether Last.fm scrobbling should be enabled."""

        self._settings.setValue(SCROBBLING_ENABLED_KEY, enabled)

    def ytdlp_cookies_browser(self) -> str:
        """Return the browser name to pass to yt-dlp --cookies-from-browser, or empty string."""

        value = self._settings.value(YTDLP_BROWSER_KEY, "", str)
        return value if value in YTDLP_BROWSER_CHOICES else ""

    def set_ytdlp_cookies_browser(self, browser: str) -> None:
        """Persist the browser used for yt-dlp cookie authentication."""

        safe = browser if browser in YTDLP_BROWSER_CHOICES else ""
        self._settings.setValue(YTDLP_BROWSER_KEY, safe)

    def download_concurrency(self) -> int:
        """Return the configured number of parallel download workers."""

        value = self._settings.value(DOWNLOAD_CONCURRENCY_KEY, DEFAULT_DOWNLOAD_CONCURRENCY)
        return _clamp_download_concurrency(value)

    def set_download_concurrency(self, concurrency: int) -> None:
        """Persist the configured number of parallel download workers."""

        self._settings.setValue(
            DOWNLOAD_CONCURRENCY_KEY,
            _clamp_download_concurrency(concurrency),
        )

    def keep_data_on_quit(self) -> bool:
        """Return True when the user opted to keep cached data after the app closes."""

        return bool(self._settings.value(KEEP_DATA_ON_QUIT_KEY, False, bool))

    def set_keep_data_on_quit(self, keep: bool) -> None:
        """Persist the keep-data-on-quit preference."""

        self._settings.setValue(KEEP_DATA_ON_QUIT_KEY, keep)

    def randomize_playback(self) -> bool:
        """Return True when playback should continue with a random track."""

        return bool(self._settings.value(RANDOMIZE_PLAYBACK_KEY, False, bool))

    def set_randomize_playback(self, enabled: bool) -> None:
        """Persist whether playback should continue with a random track."""

        self._settings.setValue(RANDOMIZE_PLAYBACK_KEY, enabled)


    def volume_percent(self) -> int:
        """Return the persisted playback volume as a 0-100 percentage."""

        return clamp_volume(_as_int(self._settings.value(VOLUME_KEY, DEFAULT_VOLUME_PERCENT)))

    def set_volume_percent(self, volume_percent: int) -> None:
        """Persist the playback volume percentage."""

        self._settings.setValue(VOLUME_KEY, clamp_volume(volume_percent))

    def muted(self) -> bool:
        """Return True when playback should start muted."""

        return bool(self._settings.value(MUTED_KEY, False, bool))

    def set_muted(self, muted: bool) -> None:
        """Persist whether playback is muted."""

        self._settings.setValue(MUTED_KEY, muted)


    def last_username(self) -> str:
        """Return the Last.fm username used in the previous session."""

        value = self._settings.value(LAST_USERNAME_KEY, "", str)
        return value.strip() if isinstance(value, str) else ""

    def set_last_username(self, username: str) -> None:
        """Persist the Last.fm username for the next session."""

        self._settings.setValue(LAST_USERNAME_KEY, username.strip())

    def window_geometry(self) -> QByteArray | None:
        """Return the persisted main-window geometry, or None when unset."""

        value = self._settings.value(WINDOW_GEOMETRY_KEY)
        if isinstance(value, QByteArray) and not value.isEmpty():
            return value
        return None

    def set_window_geometry(self, geometry: QByteArray) -> None:
        """Persist the main-window geometry."""

        self._settings.setValue(WINDOW_GEOMETRY_KEY, geometry)


def _as_int(value: object) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return DEFAULT_VOLUME_PERCENT


def _clamp_download_concurrency(value: object) -> int:
    try:
        concurrency = int(value)
    except (TypeError, ValueError):
        return DEFAULT_DOWNLOAD_CONCURRENCY
    return max(MIN_DOWNLOAD_CONCURRENCY, min(MAX_DOWNLOAD_CONCURRENCY, concurrency))

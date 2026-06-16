"""Last.fm authentication and scrobbling via pylast."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

LOGGER = logging.getLogger(__name__)

SCROBBLE_THRESHOLD = 0.33


class ScrobblingService:  # pylint: disable=too-many-instance-attributes
    """Wraps pylast for Last.fm web-auth and track scrobbling.

    API key and secret are the *application* credentials obtained from
    https://www.last.fm/api/account/create.  The session key is per-user
    and is obtained through the web-auth flow.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        api_key: str,
        api_secret: str,
        session_key: str = "",
        username: str = "",
        scrobbling_enabled: bool = True,
        network_factory: Callable[..., Any] | None = None,
        sg_factory: Callable[[Any], Any] | None = None,
    ) -> None:
        self._api_key = api_key
        self._api_secret = api_secret
        self._session_key = session_key
        self._username = username
        self.scrobbling_enabled = scrobbling_enabled
        self._network: Any | None = None
        self._sg: Any | None = None
        self._pending_auth_url: str | None = None
        self._authenticated = False
        self._network_factory = network_factory or _pylast_network_factory
        self._sg_factory = sg_factory or _pylast_sg_factory

    @property
    def is_authenticated(self) -> bool:
        """Return ``True`` when a valid Last.fm session is active."""
        return self._authenticated

    @property
    def auth_in_progress(self) -> bool:
        """Return ``True`` while waiting for the user to authorize in the browser."""
        return self._pending_auth_url is not None

    @property
    def username(self) -> str:
        """Return the authenticated Last.fm username."""
        return self._username

    @property
    def session_key(self) -> str:
        """Return the current session key (not logged)."""
        return self._session_key

    @property
    def has_api_credentials(self) -> bool:
        """Return ``True`` when API key and secret are both non-empty."""
        return bool(self._api_key and self._api_secret)

    def try_connect(self) -> bool:
        """Verify stored session key against Last.fm.  Returns ``True`` on success."""
        if not self._session_key or not self.has_api_credentials:
            return False
        if not self._username:
            # Legacy credentials may have lost the username; without it pylast
            # cannot issue user.getInfo to verify the session.  Force re-auth.
            LOGGER.warning("Stored Last.fm session has no username; please re-authenticate")
            self._authenticated = False
            return False
        try:
            network = self._network_factory(
                api_key=self._api_key,
                api_secret=self._api_secret,
                session_key=self._session_key,
                username=self._username,
            )
            self._username = network.get_authenticated_user().get_name(
                properly_capitalized=True
            )
            self._network = network
            self._authenticated = True
            LOGGER.info("Last.fm connected as %s", self._username)
            return True
        except Exception:  # noqa: BLE001
            LOGGER.warning("Last.fm connect failed; session key may be expired")
            self._authenticated = False
            return False

    def start_web_auth(self) -> str | None:
        """Start the Last.fm OAuth flow.  Returns the authorization URL or ``None``."""
        if not self.has_api_credentials:
            return None
        try:
            network = self._network_factory(
                api_key=self._api_key,
                api_secret=self._api_secret,
            )
            self._sg = self._sg_factory(network)
            url = self._sg.get_web_auth_url()
            self._pending_auth_url = url
            return url
        except Exception:  # noqa: BLE001
            LOGGER.warning("Failed to start Last.fm web auth")
            self._sg = None
            self._pending_auth_url = None
            return None

    def complete_web_auth(self) -> bool:
        """Finish the OAuth flow after the user has authorized.  Returns ``True`` on success."""
        if self._sg is None or self._pending_auth_url is None:
            return False
        try:
            # auth.getSession returns both session key and username; use the
            # combined call so we don't need a follow-up user.getInfo (which
            # would fail with 400 because the network has no username yet).
            session_key, username = self._sg.get_web_auth_session_key_username(
                self._pending_auth_url
            )
            network = self._network_factory(
                api_key=self._api_key,
                api_secret=self._api_secret,
                session_key=session_key,
                username=username,
            )
            self._username = username
            self._session_key = session_key
            self._network = network
            self._authenticated = True
            self._sg = None
            self._pending_auth_url = None
            LOGGER.info("Last.fm authenticated as %s", self._username)
            return True
        except Exception:  # noqa: BLE001
            LOGGER.warning("Last.fm web auth completion failed")
            return False

    def disconnect(self) -> None:
        """Clear the session key and mark as not authenticated."""
        self._session_key = ""
        self._network = None
        self._authenticated = False
        self._sg = None
        self._pending_auth_url = None
        LOGGER.info("Last.fm disconnected")

    def scrobble(self, artist: str, title: str, timestamp: int, duration_seconds: int = 0) -> None:
        """Submit a scrobble.  Silently skipped when not authenticated or disabled."""
        if not self._can_scrobble():
            return
        try:
            self._network.scrobble(  # type: ignore[union-attr]
                artist=artist,
                title=title,
                timestamp=timestamp,
                duration=duration_seconds or None,
            )
            LOGGER.info("Scrobbled: %s - %s", artist, title)
        except Exception:  # noqa: BLE001
            LOGGER.warning("Scrobble failed for %s - %s", artist, title)

    def update_now_playing(self, artist: str, title: str, duration_seconds: int = 0) -> None:
        """Send a now-playing notification.  Silently skipped when not authenticated."""
        if not self._can_scrobble():
            return
        try:
            self._network.update_now_playing(  # type: ignore[union-attr]
                artist=artist,
                title=title,
                duration=duration_seconds or None,
            )
            LOGGER.info("Now-playing: %s - %s", artist, title)
        except Exception:  # noqa: BLE001
            LOGGER.warning("Now-playing update failed for %s - %s", artist, title)

    def credentials_dict(self) -> dict[str, object]:
        """Return serializable credentials.  The session key value is not logged."""
        return {
            "username": self._username,
            "session_key": self._session_key,
            "scrobbling_enabled": self.scrobbling_enabled,
        }

    def _can_scrobble(self) -> bool:
        return self._authenticated and self.scrobbling_enabled and self._network is not None


def _pylast_network_factory(**kwargs: Any) -> Any:
    import pylast  # noqa: PLC0415

    return pylast.LastFMNetwork(**kwargs)


def _pylast_sg_factory(network: Any) -> Any:
    import pylast  # noqa: PLC0415

    return pylast.SessionKeyGenerator(network)

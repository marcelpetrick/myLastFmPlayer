"""Application-level service credentials with user override support."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

LASTFM_API_KEY_ENV = "LASTFM_API_KEY"
LASTFM_API_SECRET_ENV = "LASTFM_API_SECRET"

DEFAULT_LASTFM_API_KEY = "d36dce7154716e08a1d2907b7badadf7"
DEFAULT_LASTFM_API_SECRET = "ed22747b03cabe49ab93f7215afc06fc"


@dataclass(frozen=True)
class LastFmApiCredentials:
    """Last.fm application credentials used to sign authenticated API calls."""

    api_key: str
    api_secret: str

    @property
    def is_configured(self) -> bool:
        """Return ``True`` when both credential values are non-empty."""

        return bool(self.api_key and self.api_secret)


def lastfm_api_credentials(
    environ: Mapping[str, str] | None = None,
) -> LastFmApiCredentials:
    """Return Last.fm app credentials, preferring environment overrides."""

    values = os.environ if environ is None else environ
    return LastFmApiCredentials(
        api_key=values.get(LASTFM_API_KEY_ENV, DEFAULT_LASTFM_API_KEY).strip(),
        api_secret=values.get(LASTFM_API_SECRET_ENV, DEFAULT_LASTFM_API_SECRET).strip(),
    )

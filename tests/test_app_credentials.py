from __future__ import annotations

from my_lastfm_player.app_credentials import (
    DEFAULT_LASTFM_API_KEY,
    DEFAULT_LASTFM_API_SECRET,
    LASTFM_API_KEY_ENV,
    LASTFM_API_SECRET_ENV,
    LastFmApiCredentials,
    lastfm_api_credentials,
)


def test_lastfm_api_credentials_use_bundled_defaults() -> None:
    credentials = lastfm_api_credentials({})

    assert credentials.api_key == DEFAULT_LASTFM_API_KEY
    assert credentials.api_secret == DEFAULT_LASTFM_API_SECRET
    assert credentials.is_configured


def test_lastfm_api_credentials_prefer_environment_overrides() -> None:
    credentials = lastfm_api_credentials(
        {
            LASTFM_API_KEY_ENV: " custom-key ",
            LASTFM_API_SECRET_ENV: " custom-secret ",
        }
    )

    assert credentials.api_key == "custom-key"
    assert credentials.api_secret == "custom-secret"


def test_lastfm_api_credentials_report_missing_secret() -> None:
    credentials = LastFmApiCredentials(api_key="key", api_secret="")

    assert not credentials.is_configured

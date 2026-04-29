from __future__ import annotations

import os

import pytest

from my_lastfm_player.lastfm import LastFmLovedTracksScraper

LIVE_LASTFM_ENV = "MY_LASTFM_PLAYER_RUN_LASTFM_E2E"
LIVE_LASTFM_USERNAME = "first"


@pytest.mark.skipif(
    os.getenv(LIVE_LASTFM_ENV) != "1",
    reason=f"set {LIVE_LASTFM_ENV}=1 to run the live Last.fm e2e test",
)
def test_live_lastfm_first_loved_tracks_end_to_end(capsys: pytest.CaptureFixture[str]) -> None:
    scraper = LastFmLovedTracksScraper()

    tracks = scraper.fetch_loved_tracks(LIVE_LASTFM_USERNAME)

    with capsys.disabled():
        print(f"\nLive Last.fm loved tracks for user {LIVE_LASTFM_USERNAME}:")
        for index, track in enumerate(tracks, start=1):
            print(f"{index:03d}. {track.artist} - {track.title}")

    assert tracks
    assert all(track.artist and track.title for track in tracks)

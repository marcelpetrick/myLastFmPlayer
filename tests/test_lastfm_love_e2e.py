"""Live love/unlove round trip against the real Last.fm account stored by the app.

This test WRITES to Last.fm, so it has its own opt-in, separate from the read-only
live test: set ``MY_LASTFM_PLAYER_RUN_LASTFM_WRITE_E2E=1``.  It uses the session
the app saved after "Connect to Last.fm" in Preferences, loves a sentinel track via
``ScrobblingService`` (the code path the app uses), then unloves it again.  When the
sentinel is already loved it skips instead of touching a real love.
"""

from __future__ import annotations

import os
import time

import pytest

from my_lastfm_player.app_credentials import lastfm_api_credentials
from my_lastfm_player.scrobbling import ScrobblingService
from my_lastfm_player.storage import JsonTrackRepository

LIVE_LASTFM_WRITE_ENV = "MY_LASTFM_PLAYER_RUN_LASTFM_WRITE_E2E"
SENTINEL_ARTIST = "Kevin MacLeod"
SENTINEL_TITLE = "Monkeys Spinning Monkeys"
POLL_TIMEOUT_SECONDS = 30.0
POLL_INTERVAL_SECONDS = 2.0


def _wait_for_loved_state(service: ScrobblingService, expected: bool) -> bool:
    deadline = time.monotonic() + POLL_TIMEOUT_SECONDS
    while True:
        if service.is_track_loved(SENTINEL_ARTIST, SENTINEL_TITLE) is expected:
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(POLL_INTERVAL_SECONDS)


@pytest.mark.skipif(
    os.getenv(LIVE_LASTFM_WRITE_ENV) != "1",
    reason=f"set {LIVE_LASTFM_WRITE_ENV}=1 to run the live Last.fm love/unlove e2e test",
)
def test_live_lastfm_love_then_unlove_round_trip(capsys: pytest.CaptureFixture[str]) -> None:
    credentials = JsonTrackRepository().load_credentials()
    app_credentials = lastfm_api_credentials()
    service = ScrobblingService(
        api_key=app_credentials.api_key,
        api_secret=app_credentials.api_secret,
        session_key=str(credentials.get("session_key", "")),
        username=str(credentials.get("username", "")),
    )
    if not service.try_connect():
        pytest.skip("no verified Last.fm session; connect in the app's Preferences first")
    if service.is_track_loved(SENTINEL_ARTIST, SENTINEL_TITLE):
        pytest.skip(f"{SENTINEL_ARTIST} - {SENTINEL_TITLE} is already loved; not touching it")

    with capsys.disabled():
        print(f"\nLive Last.fm love/unlove as {service.username}:")
        print(f"  sentinel: {SENTINEL_ARTIST} - {SENTINEL_TITLE}")
    try:
        service.love_track(SENTINEL_ARTIST, SENTINEL_TITLE)
        assert _wait_for_loved_state(service, expected=True), "love did not reach Last.fm"
        with capsys.disabled():
            print("  loved: confirmed by track.getInfo")
    finally:
        service.unlove_track(SENTINEL_ARTIST, SENTINEL_TITLE)
    assert _wait_for_loved_state(service, expected=False), "unlove did not reach Last.fm"
    with capsys.disabled():
        print("  unloved: confirmed by track.getInfo")


@pytest.mark.skipif(
    os.getenv(LIVE_LASTFM_WRITE_ENV) != "1",
    reason=f"set {LIVE_LASTFM_WRITE_ENV}=1 to run the live Last.fm love/unlove e2e test",
)
def test_live_lastfm_unlove_through_the_app(
    qapp, tmp_path, monkeypatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Love the sentinel via the API, then unlove it through the app's context-menu flow."""

    from PyQt6.QtTest import QTest  # noqa: PLC0415

    from my_lastfm_player.controller import ApplicationController  # noqa: PLC0415
    from my_lastfm_player.dependencies import DependencyCheckResult  # noqa: PLC0415
    from my_lastfm_player.models import Track  # noqa: PLC0415
    from my_lastfm_player.ui import main_window as main_window_module  # noqa: PLC0415

    credentials = JsonTrackRepository().load_credentials()
    app_credentials = lastfm_api_credentials()
    service = ScrobblingService(
        api_key=app_credentials.api_key,
        api_secret=app_credentials.api_secret,
        session_key=str(credentials.get("session_key", "")),
        username=str(credentials.get("username", "")),
    )
    if not service.try_connect():
        pytest.skip("no verified Last.fm session; connect in the app's Preferences first")
    if service.is_track_loved(SENTINEL_ARTIST, SENTINEL_TITLE):
        pytest.skip(f"{SENTINEL_ARTIST} - {SENTINEL_TITLE} is already loved; not touching it")

    username = service.username
    sentinel = Track(artist=SENTINEL_ARTIST, title=SENTINEL_TITLE)
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_tracks(username, [sentinel])
    window = main_window_module.MainWindow()
    window.set_username(username)
    controller = ApplicationController(
        window,
        repository=repository,
        dependency_checker=lambda: DependencyCheckResult(installed=(), missing=()),
        artist_images_enabled=False,
    )
    controller.start()
    controller._scrobbling_service = service
    assert controller.load_cached_tracks_for_entered_username()

    try:
        service.love_track(SENTINEL_ARTIST, SENTINEL_TITLE)
        assert _wait_for_loved_state(service, expected=True), "love did not reach Last.fm"
        with capsys.disabled():
            print(f"\nApp unlove as {username}: loved {SENTINEL_ARTIST} - {SENTINEL_TITLE}")

        confirmations: list[str] = []
        monkeypatch.setattr(
            main_window_module.QMenu,
            "exec",
            lambda menu, _pos: menu.actions()[-1],
        )
        monkeypatch.setattr(
            window,
            "_confirm_unlove",
            lambda track, account: confirmations.append(account) or True,
        )
        window._show_track_context_menu(
            window.track_table.visualRect(window.track_sort_model.index(0, 0)).center()
        )
        assert confirmations == [username], "unlove was not offered for the user's own list"

        deadline = time.monotonic() + POLL_TIMEOUT_SECONDS
        while window.tracks() and time.monotonic() < deadline:
            QTest.qWait(100)
        assert window.tracks() == [], window.feedback_log.toPlainText()
        assert repository.load_tracks(username) == []
        assert _wait_for_loved_state(service, expected=False), "unlove did not reach Last.fm"
        with capsys.disabled():
            print("  unloved through the app: row removed, confirmed by track.getInfo")
    finally:
        if service.is_track_loved(SENTINEL_ARTIST, SENTINEL_TITLE):
            service.unlove_track(SENTINEL_ARTIST, SENTINEL_TITLE)
        controller._shutdown_background_work()

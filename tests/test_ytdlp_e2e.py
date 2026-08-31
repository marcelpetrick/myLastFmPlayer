from __future__ import annotations

import os
import subprocess

import pytest

from my_lastfm_player.download import (
    AUDIO_FORMAT_SELECTOR,
    PLAYER_CLIENT_LADDER,
    DownloadManager,
)
from my_lastfm_player.models import Track, TrackStatus

LIVE_YTDLP_ENV = "MY_LASTFM_PLAYER_RUN_YTDLP_E2E"
# A long-standing music upload; only used read-only, to probe client support.
LIVE_VIDEO_URL = "https://www.youtube.com/watch?v=wUcKgzE0Ghk"
UNSUPPORTED_CLIENT_MARKER = "Skipping unsupported client"

live_only = pytest.mark.skipif(
    os.getenv(LIVE_YTDLP_ENV) != "1",
    reason=f"set {LIVE_YTDLP_ENV}=1 to run the live yt-dlp e2e tests",
)


def _forced_clients() -> list[str]:
    return [client for rung in PLAYER_CLIENT_LADDER[1:] for client in rung.split(",") if rung]


@live_only
def test_every_ladder_client_is_supported_by_the_installed_ytdlp() -> None:
    """Guard against a ladder rung yt-dlp silently skips, which wastes a whole retry."""

    unsupported: list[str] = []
    for client in _forced_clients():
        completed = subprocess.run(
            [
                "yt-dlp",
                "--simulate",
                "--no-playlist",
                "--extractor-args",
                f"youtube:player_client={client}",
                LIVE_VIDEO_URL,
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
        )
        if UNSUPPORTED_CLIENT_MARKER in completed.stderr:
            unsupported.append(client)

    assert not unsupported, f"yt-dlp does not support these ladder clients: {unsupported}"


@live_only
def test_ladder_downloads_a_track_that_a_single_client_cannot_fetch(tmp_path) -> None:
    """The whole point of the ladder: some client in it must complete a real download."""

    manager = DownloadManager(backoff_factory=lambda: 0.5)
    track = Track(artist="Ladder", title="Probe", youtube_url=LIVE_VIDEO_URL)

    tracks = manager.download_tracks([track], tmp_path)

    assert tracks[0].status is TrackStatus.DOWNLOADED, tracks[0].error
    assert tracks[0].bitrate_kbps


@live_only
def test_audio_format_selector_resolves_against_youtube() -> None:
    """The selector must keep resolving; a bad one fails every download identically."""

    completed = subprocess.run(
        ["yt-dlp", "--simulate", "--no-playlist", "-f", AUDIO_FORMAT_SELECTOR, LIVE_VIDEO_URL],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )

    assert completed.returncode == 0, completed.stderr

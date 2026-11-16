"""Scheduling, failure state and progress catalog context of the YouTube resolver."""

from __future__ import annotations

import threading

from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.youtube import YouTubeLookupError, YouTubeResolver

URL = "https://www.youtube.com/watch?v=abc"


def test_failed_lookups_clear_an_empty_url(monkeypatch) -> None:
    def fake_resolve(track, _stop):
        if track.title == "Known":
            raise YouTubeLookupError("no result")
        raise RuntimeError("crash")

    resolver = YouTubeResolver()
    monkeypatch.setattr(resolver, "resolve_track", fake_resolve)

    results = resolver.resolve_tracks(
        [Track("Artist", "Known", youtube_url=""), Track("Artist", "Unknown", youtube_url="")]
    )

    assert [(track.status, track.youtube_url) for track in results] == [
        (TrackStatus.LOOKUP_FAILED, None),
        (TrackStatus.LOOKUP_FAILED, None),
    ]


def test_progress_messages_use_the_resolver_catalog_context(qapp, monkeypatch) -> None:
    def fake_resolve(track, _stop):
        if track.title == "Found":
            return Track(track.artist, track.title, youtube_url=URL, status=TrackStatus.QUEUED)
        return Track(track.artist, track.title, status=TrackStatus.NOT_FOUND)

    resolver = YouTubeResolver()
    monkeypatch.setattr(resolver, "resolve_track", fake_resolve)
    messages: list[str] = []

    resolver.resolve_tracks(
        [Track("Artist", "Found"), Track("Artist", "Missing")],
        progress_callback=lambda _value, message: messages.append(message),
        concurrency=1,
    )

    assert messages == [
        "Searching 1/2: Artist - Found",
        "Resolved 1/2: Artist - Found",
        "Searching 2/2: Artist - Missing",
        "No YouTube result 2/2: Artist - Missing",
    ]


def test_a_finished_lookup_frees_its_slot_while_others_still_run(monkeypatch) -> None:
    third_started = threading.Event()

    def fake_resolve(track, _stop):
        if track.title == "Third":
            third_started.set()
        elif track.title == "Slow" and not third_started.wait(1.0):
            return Track(track.artist, track.title, status=TrackStatus.LOOKUP_FAILED)
        return Track(track.artist, track.title, youtube_url=URL, status=TrackStatus.QUEUED)

    resolver = YouTubeResolver()
    monkeypatch.setattr(resolver, "resolve_track", fake_resolve)

    results = resolver.resolve_tracks(
        [Track("Artist", "Slow"), Track("Artist", "Fast"), Track("Artist", "Third")],
        concurrency=2,
    )

    assert [track.status for track in results] == [TrackStatus.QUEUED] * 3

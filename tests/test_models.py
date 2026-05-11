from __future__ import annotations

import pytest

from my_lastfm_player.models import (
    Track,
    TrackStatus,
    build_audio_base_name,
    build_track_cache_key,
    sanitize_filename_part,
)


def test_track_status_values_match_srs() -> None:
    assert [status.value for status in TrackStatus] == [
        "Fetched",
        "Queued",
        "Searching",
        "Downloading",
        "Downloaded",
        "Failed",
        "Not found",
    ]


def test_track_serializes_to_json_ready_dict() -> None:
    track = Track(
        artist="Artist",
        title="Title",
        lastfm_url="https://last.fm/music/Artist/_/Title",
        youtube_url="https://youtube.example/watch?v=abc",
        local_path="/music/Artist - Title.mp3",
        status=TrackStatus.DOWNLOADED,
        retry_count=2,
        error=None,
        file_type="MP3",
        bitrate_kbps=192,
    )

    assert track.to_dict() == {
        "artist": "Artist",
        "title": "Title",
        "lastfm_url": "https://last.fm/music/Artist/_/Title",
        "youtube_url": "https://youtube.example/watch?v=abc",
        "local_path": "/music/Artist - Title.mp3",
        "status": "Downloaded",
        "retry_count": 2,
        "error": None,
        "file_type": "MP3",
        "bitrate_kbps": 192,
    }


def test_track_deserializes_from_json_ready_dict() -> None:
    track = Track.from_dict(
        {
            "artist": "Artist",
            "title": "Title",
            "lastfm_url": None,
            "youtube_url": None,
            "local_path": None,
            "status": "Searching",
            "retry_count": 1,
            "error": "temporary failure",
            "file_type": "WEBM",
            "bitrate_kbps": 128,
        }
    )

    assert track == Track(
        artist="Artist",
        title="Title",
        status=TrackStatus.SEARCHING,
        retry_count=1,
        error="temporary failure",
        file_type="WEBM",
        bitrate_kbps=128,
    )


def test_track_deserialization_defaults_status_and_retry_count() -> None:
    track = Track.from_dict({"artist": "Artist", "title": "Title"})

    assert track.status == TrackStatus.FETCHED
    assert track.retry_count == 0
    assert track.file_type is None
    assert track.bitrate_kbps is None


def test_track_rejects_invalid_serialized_values() -> None:
    with pytest.raises(ValueError, match="artist"):
        Track.from_dict({"artist": "", "title": "Title"})

    with pytest.raises(ValueError, match="status"):
        Track.from_dict({"artist": "Artist", "title": "Title", "status": "Unknown"})

    with pytest.raises(ValueError, match="lastfm_url"):
        Track.from_dict({"artist": "Artist", "title": "Title", "lastfm_url": 123})

    with pytest.raises(ValueError, match="bitrate_kbps"):
        Track.from_dict({"artist": "Artist", "title": "Title", "bitrate_kbps": "128"})


def test_track_constructor_rejects_invalid_core_values() -> None:
    with pytest.raises(ValueError, match="artist"):
        Track(artist="", title="Title")

    with pytest.raises(ValueError, match="title"):
        Track(artist="Artist", title="")

    with pytest.raises(ValueError, match="retry_count"):
        Track(artist="Artist", title="Title", retry_count=-1)

    with pytest.raises(ValueError, match="bitrate_kbps"):
        Track(artist="Artist", title="Title", bitrate_kbps=-1)


def test_track_status_transition_returns_updated_copy() -> None:
    fetched = Track(artist="Artist", title="Title")
    queued = fetched.with_status(TrackStatus.QUEUED)
    failed = queued.with_status(TrackStatus.FAILED, error="network failure")

    assert fetched.status == TrackStatus.FETCHED
    assert queued.status == TrackStatus.QUEUED
    assert failed.status == TrackStatus.FAILED
    assert failed.error == "network failure"


def test_retry_increment_returns_updated_copy() -> None:
    track = Track(artist="Artist", title="Title")

    retried = track.increment_retry(error="timeout")

    assert track.retry_count == 0
    assert retried.retry_count == 1
    assert retried.error == "timeout"


def test_cache_key_uses_exact_artist_and_title() -> None:
    lower = build_track_cache_key("artist", "title")
    original = build_track_cache_key("Artist", "Title")
    spaced = build_track_cache_key(" Artist ", "Title")

    assert lower != original
    assert spaced != original
    assert Track(artist="Artist", title="Title").cache_key == original


def test_audio_base_name_uses_artist_title_and_sanitizes_invalid_characters() -> None:
    assert build_audio_base_name('AC/DC', 'Track: "Live"?') == "AC_DC - Track_ _Live__"
    assert Track(artist="Artist", title="Title").audio_base_name == "Artist - Title"


def test_filename_sanitizer_handles_blank_or_unsafe_values() -> None:
    assert sanitize_filename_part("   ...   ") == "Unknown Track"
    assert sanitize_filename_part(" Artist\tName  -  Title\nName ") == "Artist Name - Title Name"


def test_audio_base_name_is_limited_to_safe_length() -> None:
    base = build_audio_base_name("A" * 300, "B" * 300)

    assert len(base) <= 235

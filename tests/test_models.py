from __future__ import annotations

import pytest

from my_lastfm_player.models import (
    Track,
    TrackStatus,
    build_audio_base_name,
    build_audio_file_stem,
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
        "loved_at": None,
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


def test_audio_file_stem_adds_stable_hash_to_avoid_sanitized_collisions() -> None:
    slash_stem = build_audio_file_stem("AC/DC", "Song")
    underscore_stem = build_audio_file_stem("AC_DC", "Song")

    assert slash_stem.startswith("AC_DC - Song [")
    assert underscore_stem.startswith("AC_DC - Song [")
    assert slash_stem != underscore_stem
    assert Track(artist="AC/DC", title="Song").audio_file_stem == slash_stem


def test_filename_sanitizer_handles_blank_or_unsafe_values() -> None:
    assert sanitize_filename_part("   ...   ") == "Unknown Track"
    assert sanitize_filename_part(" Artist\tName  -  Title\nName ") == "Artist Name - Title Name"


def test_audio_base_name_is_limited_to_safe_length() -> None:
    base = build_audio_base_name("A" * 300, "B" * 300)

    assert len(base) <= 235


def test_audio_file_stem_is_limited_to_safe_length() -> None:
    stem = build_audio_file_stem("A" * 300, "B" * 300)

    assert len(stem) <= 235
    assert stem.endswith("]")


# ---------------------------------------------------------------------------
# Track.merge_preserving
# ---------------------------------------------------------------------------


def _track(**kwargs) -> Track:
    artist = kwargs.pop("artist", "Artist")
    title = kwargs.pop("title", "Title")
    return Track(artist=artist, title=title, **kwargs)


def test_merge_preserving_takes_forward_status() -> None:
    old = _track(status=TrackStatus.FETCHED)
    new = _track(status=TrackStatus.QUEUED, youtube_url="https://yt/1")

    result = Track.merge_preserving(old, new)

    assert result.status == TrackStatus.QUEUED
    assert result.youtube_url == "https://yt/1"


def test_merge_preserving_never_downgrades_downloaded() -> None:
    old = _track(
        status=TrackStatus.DOWNLOADED,
        local_path="/music/Artist - Title.mp3",
        youtube_url="https://yt/1",
    )
    new = _track(status=TrackStatus.QUEUED, youtube_url="https://yt/1")

    result = Track.merge_preserving(old, new)

    assert result.status == TrackStatus.DOWNLOADED
    assert result.local_path == "/music/Artist - Title.mp3"


def test_merge_preserving_never_downgrades_not_found() -> None:
    old = _track(status=TrackStatus.NOT_FOUND)
    new = _track(status=TrackStatus.FETCHED)

    result = Track.merge_preserving(old, new)

    assert result.status == TrackStatus.NOT_FOUND


def test_merge_preserving_never_downgrades_failed() -> None:
    old = _track(status=TrackStatus.FAILED, error="network error")
    new = _track(status=TrackStatus.DOWNLOADING)

    result = Track.merge_preserving(old, new)

    assert result.status == TrackStatus.FAILED


def test_merge_preserving_allows_failed_to_advance_to_not_found() -> None:
    old = _track(status=TrackStatus.FAILED)
    new = _track(status=TrackStatus.NOT_FOUND)

    result = Track.merge_preserving(old, new)

    assert result.status == TrackStatus.NOT_FOUND


def test_merge_preserving_preserves_youtube_url_when_new_is_none() -> None:
    old = _track(youtube_url="https://yt/old", status=TrackStatus.QUEUED)
    new = _track(status=TrackStatus.FETCHED)

    result = Track.merge_preserving(old, new)

    assert result.youtube_url == "https://yt/old"


def test_merge_preserving_takes_new_youtube_url_when_set() -> None:
    old = _track(youtube_url="https://yt/old", status=TrackStatus.QUEUED)
    new = _track(youtube_url="https://yt/new", status=TrackStatus.QUEUED)

    result = Track.merge_preserving(old, new)

    assert result.youtube_url == "https://yt/new"


def test_merge_preserving_preserves_local_path_when_new_is_none() -> None:
    old = _track(local_path="/music/song.mp3", status=TrackStatus.DOWNLOADED)
    new = _track(status=TrackStatus.QUEUED, youtube_url="https://yt/1")

    result = Track.merge_preserving(old, new)

    assert result.local_path == "/music/song.mp3"


def test_merge_preserving_preserves_loved_at_when_new_is_none() -> None:
    old = _track(loved_at="20230101-120000")
    new = _track()

    result = Track.merge_preserving(old, new)

    assert result.loved_at == "20230101-120000"


def test_merge_preserving_clears_error_when_new_error_is_none() -> None:
    old = _track(error="download failed", status=TrackStatus.FAILED)
    new = _track(status=TrackStatus.FAILED)

    result = Track.merge_preserving(old, new)

    assert result.error is None


def test_merge_preserving_takes_max_retry_count() -> None:
    old = _track(retry_count=3)
    new = _track(retry_count=1)

    result = Track.merge_preserving(old, new)

    assert result.retry_count == 3


def test_merge_preserving_preserves_file_type_and_bitrate_when_new_is_none() -> None:
    old = _track(
        status=TrackStatus.DOWNLOADED,
        local_path="/f.mp3",
        file_type="MP3",
        bitrate_kbps=320,
    )
    new = _track(
        status=TrackStatus.QUEUED,
        youtube_url="https://yt/1",
        file_type=None,
        bitrate_kbps=None,
    )

    result = Track.merge_preserving(old, new)

    assert result.file_type == "MP3"
    assert result.bitrate_kbps == 320


def test_merge_preserving_full_pipeline_progression() -> None:
    fetched = _track()
    searching = _track(status=TrackStatus.SEARCHING)
    queued = _track(youtube_url="https://yt/1", status=TrackStatus.QUEUED)
    downloading = _track(youtube_url="https://yt/1", status=TrackStatus.DOWNLOADING)
    downloaded = _track(
        youtube_url="https://yt/1",
        local_path="/music/Artist - Title.mp3",
        status=TrackStatus.DOWNLOADED,
        file_type="OPUS",
        bitrate_kbps=160,
    )

    after_search = Track.merge_preserving(fetched, searching)
    after_queue = Track.merge_preserving(after_search, queued)
    after_dl = Track.merge_preserving(after_queue, downloading)
    after_done = Track.merge_preserving(after_dl, downloaded)

    assert after_done.status == TrackStatus.DOWNLOADED
    assert after_done.local_path == "/music/Artist - Title.mp3"
    assert after_done.youtube_url == "https://yt/1"

    stale_fetch = _track()
    after_stale = Track.merge_preserving(after_done, stale_fetch)

    assert after_stale.status == TrackStatus.DOWNLOADED
    assert after_stale.local_path == "/music/Artist - Title.mp3"

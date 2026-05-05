from __future__ import annotations

import json
from pathlib import Path

import pytest

from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.storage import (
    CACHE_FILENAME,
    LOOKUP_CACHE_FILENAME,
    TRACKS_DIR_NAME,
    JsonTrackRepository,
    StorageError,
    default_data_dir,
    sanitize_path_component,
)


def test_repository_saves_and_loads_per_user_tracks(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    tracks = [
        Track(
            artist="Artist",
            title="Title",
            lastfm_url="https://last.fm/music/Artist/_/Title",
            youtube_url="https://youtube.example/watch?v=abc",
            local_path="/music/Artist - Title.mp3",
            status=TrackStatus.DOWNLOADED,
            retry_count=1,
            error=None,
        )
    ]

    repository.save_tracks("user/name", tracks)

    assert repository.user_tracks_path("user/name") == tmp_path / TRACKS_DIR_NAME / "user_name.json"
    assert repository.load_tracks("user/name") == tracks


def test_repository_returns_empty_list_for_unknown_user(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)

    assert repository.load_tracks("missing") == []


def test_repository_delete_tracks_removes_only_user_json(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_tracks("first", [Track(artist="Artist", title="Title")])
    repository.save_tracks("second", [Track(artist="Other", title="Track")])

    repository.delete_tracks("first")

    assert repository.load_tracks("first") == []
    assert repository.load_tracks("second") == [Track(artist="Other", title="Track")]


def test_repository_raises_storage_error_for_corrupt_user_json(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    path = repository.user_tracks_path("user")
    path.parent.mkdir(parents=True)
    path.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(StorageError, match="invalid JSON"):
        repository.load_tracks("user")


def test_repository_raises_storage_error_for_wrong_user_json_shape(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    path = repository.user_tracks_path("user")
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"artist": "Artist"}), encoding="utf-8")

    with pytest.raises(StorageError, match="JSON array"):
        repository.load_tracks("user")


def test_download_cache_saves_only_tracks_with_local_paths(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    cached = Track(
        artist="Artist",
        title="Title",
        youtube_url="https://youtube.example/watch?v=abc",
        local_path="/music/Artist - Title.mp3",
        status=TrackStatus.DOWNLOADED,
    )

    repository.save_download_cache([cached, Track(artist="Missing", title="Path")])

    cache = repository.load_download_cache()
    assert cache == {cached.cache_key: cached}
    assert (tmp_path / CACHE_FILENAME).is_file()


def test_download_cache_deduplicates_by_exact_artist_title(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    first = Track(artist="Artist", title="Title", local_path="/old.mp3")
    second = Track(artist="Artist", title="Title", local_path="/new.mp3")
    different_case = Track(artist="artist", title="Title", local_path="/case.mp3")

    repository.save_download_cache([first, second, different_case])

    cache = repository.load_download_cache()
    assert cache[first.cache_key].local_path == "/new.mp3"
    assert cache[different_case.cache_key].local_path == "/case.mp3"


def test_mark_cached_downloads_updates_matching_tracks_only(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_download_cache(
        [
            Track(
                artist="Artist",
                title="Title",
                youtube_url="https://youtube.example/watch?v=abc",
                local_path="/music/Artist - Title.mp3",
                status=TrackStatus.DOWNLOADED,
            )
        ]
    )

    marked_tracks = repository.mark_cached_downloads(
        [
            Track(artist="Artist", title="Title", status=TrackStatus.FETCHED),
            Track(artist="artist", title="Title", status=TrackStatus.FETCHED),
        ]
    )

    assert marked_tracks[0].status == TrackStatus.DOWNLOADED
    assert marked_tracks[0].youtube_url == "https://youtube.example/watch?v=abc"
    assert marked_tracks[0].local_path == "/music/Artist - Title.mp3"
    assert marked_tracks[1].status == TrackStatus.FETCHED
    assert marked_tracks[1].local_path is None


def test_mark_cached_downloads_keeps_existing_youtube_url(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_download_cache(
        [
            Track(
                artist="Artist",
                title="Title",
                youtube_url="https://youtube.example/watch?v=cached",
                local_path="/music/Artist - Title.mp3",
            )
        ]
    )

    marked_track = repository.mark_cached_downloads(
        [Track(artist="Artist", title="Title", youtube_url="https://youtube.example/watch?v=current")]
    )[0]

    assert marked_track.youtube_url == "https://youtube.example/watch?v=current"


def test_lookup_cache_restores_resolved_and_missing_tracks(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    resolved = Track(
        artist="Artist",
        title="Title",
        youtube_url="https://youtube.example/watch?v=abc",
        status=TrackStatus.QUEUED,
    )
    missing = Track(artist="Missing", title="Track", status=TrackStatus.NOT_FOUND)

    repository.save_lookup_cache([resolved, missing, Track(artist="Uncached", title="Track")])

    marked_tracks = repository.mark_cached_lookups(
        [
            Track(artist="Artist", title="Title", status=TrackStatus.FETCHED),
            Track(artist="Missing", title="Track", status=TrackStatus.FETCHED),
            Track(artist="Other", title="Track", status=TrackStatus.FETCHED),
        ]
    )

    assert (tmp_path / LOOKUP_CACHE_FILENAME).is_file()
    assert marked_tracks[0].youtube_url == "https://youtube.example/watch?v=abc"
    assert marked_tracks[0].status == TrackStatus.QUEUED
    assert marked_tracks[1].status == TrackStatus.NOT_FOUND
    assert marked_tracks[2].status == TrackStatus.FETCHED


def test_atomic_write_replaces_existing_json_without_temp_files(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)

    repository.save_tracks("user", [Track(artist="First", title="Track")])
    repository.save_tracks("user", [Track(artist="Second", title="Track")])

    assert repository.load_tracks("user") == [Track(artist="Second", title="Track")]
    assert list(repository.user_tracks_path("user").parent.glob("*.tmp")) == []


def test_sanitize_path_component() -> None:
    assert sanitize_path_component("user/name@example.com") == "user_name_example.com"

    with pytest.raises(ValueError, match="safe character"):
        sanitize_path_component("///")


def test_default_data_dir_respects_xdg_data_home(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))

    assert default_data_dir() == tmp_path / "myLastFmPlayer"


def test_credentials_round_trip(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    credentials = {"username": "testuser", "session_key": "abc123", "scrobbling_enabled": True}

    repository.save_credentials(credentials)
    loaded = repository.load_credentials()

    assert loaded == credentials


def test_credentials_returns_empty_dict_when_missing(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)

    assert repository.load_credentials() == {}


def test_credentials_returns_empty_dict_for_corrupt_file(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.credentials_path.parent.mkdir(parents=True, exist_ok=True)
    repository.credentials_path.write_text("[not a dict]", encoding="utf-8")

    assert repository.load_credentials() == {}

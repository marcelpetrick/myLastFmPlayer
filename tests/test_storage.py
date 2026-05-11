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
    audio_path = tmp_path / "Artist - Title.mp3"
    audio_path.touch()
    tracks = [
        Track(
            artist="Artist",
            title="Title",
            lastfm_url="https://last.fm/music/Artist/_/Title",
            youtube_url="https://youtube.example/watch?v=abc",
            local_path=str(audio_path),
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


def test_download_cache_raises_storage_error_for_wrong_shape(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.cache_path.write_text(json.dumps({"artist": "Artist"}), encoding="utf-8")

    with pytest.raises(StorageError, match="JSON array"):
        repository.load_download_cache()


def test_download_cache_saves_only_tracks_with_local_paths(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    audio_path = tmp_path / "Artist - Title.mp3"
    audio_path.touch()
    cached = Track(
        artist="Artist",
        title="Title",
        youtube_url="https://youtube.example/watch?v=abc",
        local_path=str(audio_path),
        status=TrackStatus.DOWNLOADED,
    )

    repository.save_download_cache([cached, Track(artist="Missing", title="Path")])

    cache = repository.load_download_cache()
    assert cache == {cached.cache_key: cached}
    assert (tmp_path / CACHE_FILENAME).is_file()


def test_download_cache_deduplicates_by_exact_artist_title(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    old_path = tmp_path / "old.mp3"
    new_path = tmp_path / "new.mp3"
    case_path = tmp_path / "case.mp3"
    old_path.touch()
    new_path.touch()
    case_path.touch()
    first = Track(artist="Artist", title="Title", local_path=str(old_path))
    second = Track(artist="Artist", title="Title", local_path=str(new_path))
    different_case = Track(artist="artist", title="Title", local_path=str(case_path))

    repository.save_download_cache([first, second, different_case])

    cache = repository.load_download_cache()
    assert cache[first.cache_key].local_path == str(new_path)
    assert cache[different_case.cache_key].local_path == str(case_path)


def test_mark_cached_downloads_updates_matching_tracks_only(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    audio_path = tmp_path / "Artist - Title.mp3"
    audio_path.touch()
    repository.save_download_cache(
        [
            Track(
                artist="Artist",
                title="Title",
                youtube_url="https://youtube.example/watch?v=abc",
                local_path=str(audio_path),
                status=TrackStatus.DOWNLOADED,
                file_type="MP3",
                bitrate_kbps=192,
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
    assert marked_tracks[0].local_path == str(audio_path)
    assert marked_tracks[0].file_type == "MP3"
    assert marked_tracks[0].bitrate_kbps == 192
    assert marked_tracks[1].status == TrackStatus.FETCHED
    assert marked_tracks[1].local_path is None


def test_mark_cached_downloads_keeps_existing_youtube_url(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    audio_path = tmp_path / "Artist - Title.mp3"
    audio_path.touch()
    repository.save_download_cache(
        [
            Track(
                artist="Artist",
                title="Title",
                youtube_url="https://youtube.example/watch?v=cached",
                local_path=str(audio_path),
            )
        ]
    )

    marked_track = repository.mark_cached_downloads(
        [Track(artist="Artist", title="Title", youtube_url="https://youtube.example/watch?v=current")]
    )[0]

    assert marked_track.youtube_url == "https://youtube.example/watch?v=current"


def test_stale_download_paths_are_requeued_for_download(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    stale_path = tmp_path / "missing.mp3"
    track = Track(
        artist="Artist",
        title="Title",
        youtube_url="https://youtube.example/watch?v=abc",
        local_path=str(stale_path),
        status=TrackStatus.DOWNLOADED,
        file_type="MP3",
        bitrate_kbps=192,
    )

    repository.save_tracks("user", [track])

    loaded_track = repository.load_tracks("user")[0]
    assert loaded_track.local_path is None
    assert loaded_track.status is TrackStatus.QUEUED
    assert loaded_track.youtube_url == "https://youtube.example/watch?v=abc"
    assert loaded_track.file_type is None
    assert loaded_track.bitrate_kbps is None


def test_download_cache_ignores_missing_files(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.cache_path.parent.mkdir(parents=True, exist_ok=True)
    repository.cache_path.write_text(
        json.dumps(
            [
                Track(
                    artist="Artist",
                    title="Title",
                    youtube_url="https://youtube.example/watch?v=abc",
                    local_path=str(tmp_path / "missing.mp3"),
                    status=TrackStatus.DOWNLOADED,
                ).to_dict()
            ]
        ),
        encoding="utf-8",
    )

    assert repository.load_download_cache() == {}


def test_lookup_cache_raises_storage_error_for_wrong_shape(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.lookup_cache_path.write_text(json.dumps({"artist": "Artist"}), encoding="utf-8")

    with pytest.raises(StorageError, match="JSON array"):
        repository.load_lookup_cache()


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


def test_lookup_cache_leaves_unresolved_cached_tracks_unchanged(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.lookup_cache_path.write_text(
        json.dumps([Track(artist="Artist", title="Title").to_dict()]),
        encoding="utf-8",
    )

    marked_tracks = repository.mark_cached_lookups(
        [Track(artist="Artist", title="Title", status=TrackStatus.FETCHED)]
    )

    assert marked_tracks == [Track(artist="Artist", title="Title", status=TrackStatus.FETCHED)]


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


def test_credentials_returns_empty_dict_for_non_dict_json(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.credentials_path.parent.mkdir(parents=True, exist_ok=True)
    repository.credentials_path.write_text(json.dumps(["not", "a", "dict"]), encoding="utf-8")

    assert repository.load_credentials() == {}

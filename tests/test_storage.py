from __future__ import annotations

import json
import tempfile
import threading
from pathlib import Path
from unittest import mock

import pytest

from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.storage import (
    CACHE_FILENAME,
    LOOKUP_CACHE_FILENAME,
    TRACKS_DIR_NAME,
    JsonTrackRepository,
    StorageError,
    _atomic_write_json,
    _read_json_file,
    default_data_dir,
    merge_track_updates,
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
            download_attempts=1,
            error=None,
        )
    ]

    repository.save_tracks("user/name", tracks)

    assert repository.user_tracks_path("user/name") == tmp_path / TRACKS_DIR_NAME / "user_name.json"
    assert repository.load_tracks("user/name") == tracks


def test_repository_returns_empty_list_for_unknown_user(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)

    assert repository.load_tracks("missing") == []


def test_repository_journals_independent_updates_and_compacts_on_save(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    original = Track(artist="Artist", title="Title")
    resolved = Track(
        artist="Artist",
        title="Title",
        youtube_url="https://youtu.be/result",
        status=TrackStatus.QUEUED,
    )
    repository.save_tracks("user", [original])

    repository.append_track_update("user", resolved)

    assert repository.load_tracks("user") == [resolved]
    assert repository.user_updates_path("user").is_file()

    repository.merge_tracks("user", [])

    assert repository.load_tracks("user") == [resolved]
    assert not repository.user_updates_path("user").exists()


def test_repository_journals_batch_with_one_fsync(tmp_path: Path, monkeypatch) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    tracks = [Track(artist="Artist", title=f"Title {index}") for index in range(3)]
    fsync_calls: list[int] = []
    monkeypatch.setattr("my_lastfm_player.storage.os.fsync", fsync_calls.append)

    repository.append_track_updates("user", tracks)

    assert repository.load_tracks("user") == tracks
    assert len(fsync_calls) == 1


def test_repository_ignores_empty_journal_batch(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)

    repository.append_track_updates("user", [])

    assert not repository.user_updates_path("user").exists()


def test_repository_ignores_a_truncated_journal_entry(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    track = Track(artist="Artist", title="Title")
    repository.save_tracks("user", [track])
    repository.user_updates_path("user").write_text("{truncated\n", encoding="utf-8")

    assert repository.load_tracks("user") == [track]


def test_repository_ignores_non_object_journal_entry(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.tracks_dir.mkdir(parents=True)
    repository.user_updates_path("user").write_text("[]\n", encoding="utf-8")

    assert repository.load_tracks("user") == []


def test_repository_wraps_journal_read_error(tmp_path: Path, monkeypatch) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.tracks_dir.mkdir(parents=True)
    journal_path = repository.user_updates_path("user")
    journal_path.write_text("{}\n", encoding="utf-8")
    original_read_text = Path.read_text

    def read_text(path: Path, *args, **kwargs) -> str:
        if path == journal_path:
            raise OSError("denied")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read_text)

    with pytest.raises(StorageError, match="Could not read"):
        repository.load_tracks("user")


def test_repository_delete_tracks_removes_only_user_json(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_tracks("first", [Track(artist="Artist", title="Title")])
    repository.save_tracks("second", [Track(artist="Other", title="Track")])

    repository.delete_tracks("first")

    assert repository.load_tracks("first") == []
    assert repository.load_tracks("second") == [Track(artist="Other", title="Track")]


def test_repository_delete_tracks_is_noop_for_missing_user(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)

    repository.delete_tracks("missing")

    assert repository.load_tracks("missing") == []


def test_repository_raises_storage_error_for_corrupt_user_json(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    path = repository.user_tracks_path("user")
    path.parent.mkdir(parents=True)
    path.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(StorageError, match="invalid JSON"):
        repository.load_tracks("user")


def test_read_json_file_wraps_oserror() -> None:
    class UnreadablePath:
        def open(self, *_args, **_kwargs):
            raise OSError("permission denied")

        def __str__(self) -> str:
            return "/blocked.json"

    with pytest.raises(StorageError, match="Could not read /blocked.json"):
        _read_json_file(UnreadablePath())  # type: ignore[arg-type]


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


def test_merge_download_cache_keeps_existing_entries(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    first_path = tmp_path / "first.mp3"
    second_path = tmp_path / "second.mp3"
    first_path.touch()
    second_path.touch()
    first = Track(
        artist="First",
        title="Track",
        local_path=str(first_path),
        status=TrackStatus.DOWNLOADED,
    )
    second = Track(
        artist="Second",
        title="Track",
        local_path=str(second_path),
        status=TrackStatus.DOWNLOADED,
    )
    repository.save_download_cache([first])

    repository.merge_download_cache([second])

    assert repository.load_download_cache() == {
        first.cache_key: first,
        second.cache_key: second,
    }
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


def test_merge_track_updates_preserves_queued_state_when_partial_fetch_arrives() -> None:
    queued = Track(
        artist="Artist",
        title="Title",
        youtube_url="https://youtube.example/watch?v=abc",
        status=TrackStatus.QUEUED,
    )
    partial_fetch = Track(artist="Artist", title="Title")

    result = merge_track_updates([queued], [partial_fetch])

    assert result[0].status == TrackStatus.QUEUED
    assert result[0].youtube_url == "https://youtube.example/watch?v=abc"


def test_merge_track_updates_does_not_overwrite_downloaded_state() -> None:
    downloaded = Track(
        artist="Artist",
        title="Title",
        youtube_url="https://youtube.example/watch?v=abc",
        local_path="/music/song.mp3",
        status=TrackStatus.DOWNLOADED,
    )
    fetched_update = Track(artist="Artist", title="Title")

    result = merge_track_updates([downloaded], [fetched_update])

    assert result[0].status == TrackStatus.DOWNLOADED
    assert result[0].local_path == "/music/song.mp3"
    assert result[0].youtube_url == "https://youtube.example/watch?v=abc"


def test_merge_track_updates_preserves_existing_order_and_appends_new_tracks() -> None:
    first = Track(artist="First", title="Track")
    second = Track(artist="Second", title="Track")
    updated_first = Track(
        artist="First",
        title="Track",
        youtube_url="https://youtu.be/first",
        status=TrackStatus.QUEUED,
    )
    new_track = Track(artist="New", title="Track")

    assert merge_track_updates([first, second], [updated_first, new_track]) == [
        updated_first,
        second,
        new_track,
    ]


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


def test_clear_not_found_lookups_drops_only_the_missing_entries(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    resolved = Track(
        artist="Artist",
        title="Title",
        youtube_url="https://youtube.example/watch?v=abc",
        status=TrackStatus.QUEUED,
    )
    missing = Track(
        artist="Missing",
        title="Track",
        status=TrackStatus.NOT_FOUND,
        lookup_attempts=3,
    )
    repository.save_lookup_cache([resolved, missing])

    assert repository.clear_not_found_lookups() == 1

    cache = repository.load_lookup_cache()
    assert set(cache) == {resolved.cache_key}
    # A second sweep has nothing left to drop.
    assert repository.clear_not_found_lookups() == 0


def test_lookup_cache_restores_the_not_found_attempt_count(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    missing = Track(
        artist="Missing",
        title="Track",
        status=TrackStatus.NOT_FOUND,
        lookup_attempts=2,
    )

    repository.save_lookup_cache([missing])
    marked_tracks = repository.mark_cached_lookups(
        [Track(artist="Missing", title="Track", status=TrackStatus.FETCHED)]
    )

    assert marked_tracks[0].status == TrackStatus.NOT_FOUND
    assert marked_tracks[0].lookup_attempts == 2


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


def test_wipe_removes_credentials_cache_and_track_files(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    track = Track(artist="A", title="T")

    repository.save_credentials({"key": "val"})
    repository.save_tracks("user", [track])
    repository.save_download_cache([])
    repository.save_lookup_cache([])

    assert repository.credentials_path.exists()
    assert repository.cache_path.exists()
    assert repository.lookup_cache_path.exists()
    assert repository.user_tracks_path("user").exists()

    repository.wipe()

    assert not repository.credentials_path.exists()
    assert not repository.cache_path.exists()
    assert not repository.lookup_cache_path.exists()
    assert not repository.user_tracks_path("user").exists()


def test_wipe_keeps_downloaded_audio_files(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    audio_file = repository.downloads_dir / "song.mp3"
    audio_file.parent.mkdir(parents=True, exist_ok=True)
    audio_file.write_text("audio", encoding="utf-8")

    repository.save_credentials({"key": "val"})
    repository.wipe()

    assert audio_file.exists()
    assert not repository.credentials_path.exists()


def test_wipe_tolerates_oserror_without_raising(tmp_path: Path, caplog) -> None:
    import logging

    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_credentials({"key": "val"})

    credentials_path = repository.credentials_path
    credentials_path.chmod(0o444)
    credentials_path.parent.chmod(0o555)
    try:
        with caplog.at_level(logging.WARNING, logger="my_lastfm_player.storage"):
            repository.wipe()
    finally:
        credentials_path.parent.chmod(0o755)

    assert "Could not delete" in caplog.text


def test_wipe_is_idempotent_when_nothing_exists(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.wipe()  # must not raise


def test_atomic_write_json_wraps_replace_error_and_cleans_temp(
    tmp_path: Path,
    monkeypatch,
) -> None:
    target = tmp_path / "data.json"
    real_replace = Path.replace

    def failing_replace(self: Path, target_path: Path) -> Path:
        if target_path == target:
            raise OSError("disk full")
        return real_replace(self, target_path)

    monkeypatch.setattr(Path, "replace", failing_replace)

    with pytest.raises(StorageError, match="Could not write"):
        _atomic_write_json(target, {"key": "value"})

    assert not list(tmp_path.glob(".data.json.*.tmp"))


def test_wipe_serializes_against_concurrent_journal_appends(tmp_path) -> None:
    repository = JsonTrackRepository(tmp_path)
    repository.save_tracks("user", [Track(artist="Artist", title="Title")])
    inside_wipe = threading.Event()
    release = threading.Event()
    original_iterdir = Path.iterdir
    appended: list[str] = []

    def blocking_iterdir(self):
        if self == repository.tracks_dir:
            inside_wipe.set()
            release.wait(5)
        return original_iterdir(self)

    def append_update() -> None:
        repository.append_track_update("user", Track(artist="Other", title="Song"))
        appended.append("done")

    with mock.patch.object(Path, "iterdir", blocking_iterdir):
        wiper = threading.Thread(target=repository.wipe)
        wiper.start()
        assert inside_wipe.wait(5)
        appender = threading.Thread(target=append_update)
        appender.start()
        appender.join(0.2)
        assert not appended, "journal append must wait for the wipe to release the lock"
        release.set()
        appender.join(5)
        wiper.join(5)

    assert appended == ["done"]


def test_delete_tracks_is_safe_when_nothing_was_stored(tmp_path) -> None:
    repository = JsonTrackRepository(tmp_path)

    repository.delete_tracks("unknown-user")

    assert not repository.user_tracks_path("unknown-user").exists()
    assert not repository.user_updates_path("unknown-user").exists()


# --- Mutation-testing hardening: pin exact on-disk format and edge behaviour. ---


def test_writes_create_missing_parent_directories(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path / "a" / "b" / "c")

    repository.append_track_update("alice", Track("Artist", "Title"))
    repository.save_credentials({"session_key": "k"})

    assert repository.user_updates_path("alice").is_file()
    assert repository.credentials_path.is_file()


def test_json_files_keep_unicode_readable_and_are_indented(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)

    repository.save_tracks("alice", [Track("Björk", "Jóga")])
    repository.append_track_update("bob", Track("Sigur Rós", "Hoppípolla"))

    saved = repository.user_tracks_path("alice").read_bytes().decode("utf-8")
    assert saved.startswith('[\n  {\n    "artist": "Björk",\n')
    assert saved.endswith("}\n]\n")
    journal = repository.user_updates_path("bob").read_bytes().decode("utf-8")
    assert journal.startswith('{"artist": "Sigur Rós", "title": "Hoppípolla"')
    assert journal.endswith("}\n")


def test_atomic_write_uses_a_hidden_temp_file_next_to_the_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[dict] = []
    real_mkstemp = tempfile.mkstemp

    def spy_mkstemp(**kwargs):
        calls.append(kwargs)
        return real_mkstemp(**kwargs)

    monkeypatch.setattr("my_lastfm_player.storage.tempfile.mkstemp", spy_mkstemp)
    target = tmp_path / "data.json"

    _atomic_write_json(target, {"key": "value"})

    assert calls == [{"prefix": ".data.json.", "suffix": ".tmp", "dir": tmp_path}]
    assert sorted(path.name for path in tmp_path.iterdir()) == ["data.json"]


def test_invalid_journal_lines_are_skipped_and_logged_with_their_line_number(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.append_track_update("alice", Track("Artist", "Valid"))
    with repository.user_updates_path("alice").open("a", encoding="utf-8") as handle:
        handle.write("[1, 2]\n")

    with caplog.at_level("WARNING", logger="my_lastfm_player.storage"):
        tracks = repository.load_tracks("alice")

    assert [track.title for track in tracks] == ["Valid"]
    assert caplog.messages == [
        f"Ignoring invalid track update {repository.user_updates_path('alice')}:2: "
        "track update must be a JSON object"
    ]


def test_clear_not_found_lookups_rewrites_the_rest_sorted_by_cache_key(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    entries = [
        Track("Zed", "Song", youtube_url="https://youtu.be/z"),
        Track("Gone", "Song", status=TrackStatus.NOT_FOUND),
        Track("Abba", "Song", youtube_url="https://youtu.be/a"),
    ]
    repository.lookup_cache_path.write_text(
        json.dumps([track.to_dict() for track in entries]), encoding="utf-8"
    )

    assert repository.clear_not_found_lookups() == 1

    stored = json.loads(repository.lookup_cache_path.read_text(encoding="utf-8"))
    assert [item["artist"] for item in stored] == ["Abba", "Zed"]


def test_mark_cached_lookups_handles_every_track_after_a_cache_miss(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_lookup_cache(
        [
            Track("Hit", "Song", youtube_url="https://youtu.be/hit"),
            Track("Missing", "Song", status=TrackStatus.NOT_FOUND, lookup_attempts=3,
                  error="no match"),
        ]
    )

    marked = repository.mark_cached_lookups(
        [
            Track("Unknown", "Song"),
            Track("Hit", "Song", error="old error"),
            Track("Hit", "Song", status=TrackStatus.DOWNLOADED, local_path=None),
            Track("Missing", "Song", youtube_url="https://stale", lookup_attempts=1),
        ]
    )

    assert marked[0] == Track("Unknown", "Song")
    assert marked[1].youtube_url == "https://youtu.be/hit"
    assert marked[1].status is TrackStatus.QUEUED
    assert marked[1].error is None
    assert marked[2].status is TrackStatus.DOWNLOADED
    assert marked[3].youtube_url is None
    assert marked[3].status is TrackStatus.NOT_FOUND
    assert marked[3].lookup_attempts == 3
    assert marked[3].error == "no match"


def test_mark_cached_downloads_clears_a_stale_error(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    audio = tmp_path / "song.opus"
    audio.write_bytes(b"audio")
    repository.save_download_cache(
        [Track("Artist", "Song", local_path=str(audio), status=TrackStatus.DOWNLOADED)]
    )

    (marked,) = repository.mark_cached_downloads(
        [Track("Artist", "Song", status=TrackStatus.FAILED, error="timeout")]
    )

    assert marked.status is TrackStatus.DOWNLOADED
    assert marked.local_path == str(audio)
    assert marked.error is None


def test_downloaded_track_without_a_file_goes_back_to_the_right_state(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_tracks(
        "alice",
        [
            Track("No", "Url", status=TrackStatus.DOWNLOADED, local_path=str(tmp_path / "x"),
                  error="e", file_type="opus", bitrate_kbps=160),
            Track("Has", "Url", status=TrackStatus.DOWNLOADED, youtube_url="https://y",
                  local_path=str(tmp_path / "y"), error="e"),
        ],
    )

    no_url, has_url = repository.load_tracks("alice")

    assert (no_url.status, no_url.local_path, no_url.error) == (TrackStatus.FETCHED, None, None)
    assert (no_url.file_type, no_url.bitrate_kbps) == (None, None)
    assert (has_url.status, has_url.error) == (TrackStatus.QUEUED, None)


def test_default_data_dir_without_xdg_uses_local_share(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))

    assert default_data_dir() == tmp_path / ".local" / "share" / "myLastFmPlayer"


def test_sanitize_path_component_keeps_safe_characters_and_trims_edges() -> None:
    assert sanitize_path_component("X.a-b_c.X") == "X.a-b_c.X"
    assert sanitize_path_component("._Xavier_.") == "Xavier"
    message = "^Path component must contain at least one safe character$"
    with pytest.raises(ValueError, match=message):
        sanitize_path_component("._/")

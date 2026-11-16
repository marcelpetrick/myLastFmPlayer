"""Retry state, scheduling and helper contracts of the downloader."""

from __future__ import annotations

import threading
from pathlib import Path

from my_lastfm_player import download
from my_lastfm_player.download import (
    DownloadError,
    DownloadManager,
    _file_type_from_path,
    _format_name_to_file_type,
)
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.storage import JsonTrackRepository

URL = "https://www.youtube.com/watch?v=abc"


def _track(title: str = "Title", **kwargs) -> Track:
    return Track("Artist", title, youtube_url=URL, **kwargs)


def test_file_type_strips_only_the_dot() -> None:
    assert _file_type_from_path(Path("song.XM")) == "XM"


def test_preferred_formats_win_over_earlier_unknown_ones() -> None:
    assert _format_name_to_file_type("aac,ogg") == "OGG"
    assert _format_name_to_file_type("aac,flac") == "FLAC"
    assert _format_name_to_file_type("aac,wav") == "WAV"


def test_retries_pass_a_clean_downloading_track_and_the_previous_error(
    tmp_path: Path, monkeypatch
) -> None:
    calls: list[tuple[Track, int, object]] = []

    def fake_download(track, downloads_dir, attempt, stop_event):
        calls.append((track, attempt, stop_event))
        if attempt == 1:
            raise DownloadError("boom")
        return downloads_dir / "Artist - Title.mp3"

    manager = DownloadManager(max_retries=2, sleeper=lambda _seconds: None)
    monkeypatch.setattr(manager, "_download_track", fake_download)
    monkeypatch.setattr(download, "_probe_audio_file", lambda _path, _stop: ("MP3", 320))
    stop_event = threading.Event()

    result = manager._download_track_with_retries(
        _track(status=TrackStatus.QUEUED, error="old failure"), tmp_path, stop_event
    )

    assert [(track.status, track.error, attempt) for track, attempt, _ in calls] == [
        (TrackStatus.DOWNLOADING, None, 1),
        (TrackStatus.DOWNLOADING, "boom", 2),
    ]
    assert all(passed is stop_event for _, _, passed in calls)
    assert result.status is TrackStatus.DOWNLOADED
    assert result.error is None


def test_zero_retries_fail_without_an_error_message(tmp_path: Path) -> None:
    manager = DownloadManager(max_retries=0)

    result = manager._download_track_with_retries(_track(error="old"), tmp_path)

    assert result.status is TrackStatus.FAILED
    assert result.error is None


def test_download_and_store_passes_the_concurrency(tmp_path: Path, monkeypatch) -> None:
    received: dict = {}

    def fake_download_tracks(tracks, downloads_dir, **kwargs):
        received.update(kwargs)
        return tracks

    manager = DownloadManager()
    monkeypatch.setattr(manager, "download_tracks", fake_download_tracks)

    manager.download_and_store_tracks(
        "alice", JsonTrackRepository(data_dir=tmp_path), concurrency=2
    )

    assert received["concurrency"] == 2


def test_progress_messages_use_the_download_manager_catalog_context(
    qapp, tmp_path: Path, monkeypatch
) -> None:
    manager = DownloadManager()
    monkeypatch.setattr(
        manager,
        "_download_track_with_retries",
        lambda track, _dir, _stop: Track(
            track.artist, track.title, youtube_url=URL, status=TrackStatus.DOWNLOADED
        ),
    )
    messages: list[str] = []

    manager.download_tracks(
        [_track()], tmp_path, progress_callback=lambda _value, message: messages.append(message)
    )

    assert messages == ["Queued 1 downloads", "Downloaded 1/1 tracks"]


def test_a_finished_download_frees_its_slot_while_others_still_run(
    tmp_path: Path, monkeypatch
) -> None:
    third_started = threading.Event()

    def fake_retries(track, _dir, _stop):
        if track.title == "Third":
            third_started.set()
        elif track.title == "Slow" and not third_started.wait(1.0):
            return Track(track.artist, track.title, status=TrackStatus.FAILED)
        return Track(track.artist, track.title, youtube_url=URL, status=TrackStatus.DOWNLOADED)

    manager = DownloadManager()
    monkeypatch.setattr(manager, "_download_track_with_retries", fake_retries)

    results = manager.download_tracks(
        [_track("Slow"), _track("Fast"), _track("Third")], tmp_path, concurrency=2
    )

    assert [track.status for track in results] == [TrackStatus.DOWNLOADED] * 3

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from my_lastfm_player.download import DownloadManager
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.storage import JsonTrackRepository


class FakeRunner:
    def __init__(self, return_codes: list[int] | None = None) -> None:
        self.return_codes = return_codes or [0]
        self.commands: list[list[str]] = []

    def __call__(self, command, **_kwargs) -> subprocess.CompletedProcess[str]:
        self.commands.append(list(command))
        return_code = self.return_codes.pop(0) if self.return_codes else 0
        stderr = "download failed" if return_code else ""
        return subprocess.CompletedProcess(command, return_code, stdout="", stderr=stderr)


def test_download_manager_downloads_queued_tracks(tmp_path: Path) -> None:
    runner = FakeRunner()
    manager = DownloadManager(
        command_runner=runner,
        backoff_factory=lambda: 0,
        sleeper=lambda _seconds: None,
    )
    track = Track(
        artist="Artist",
        title="Title",
        youtube_url="https://youtu.be/example",
        status=TrackStatus.QUEUED,
    )
    progress: list[tuple[int, str]] = []

    tracks = manager.download_tracks(
        [track],
        tmp_path,
        progress_callback=lambda value, message: progress.append((value, message)),
    )

    assert tracks == [
        Track(
            artist="Artist",
            title="Title",
            youtube_url="https://youtu.be/example",
            local_path=str(tmp_path / "Artist - Title.mp3"),
            status=TrackStatus.DOWNLOADED,
        )
    ]
    assert runner.commands == [
        [
            "yt-dlp",
            "--extract-audio",
            "--audio-format",
            "mp3",
            "--no-playlist",
            "--output",
            str(tmp_path / "Artist - Title.%(ext)s"),
            "https://youtu.be/example",
        ]
    ]
    assert progress == [(0, "Queued 1 downloads"), (100, "Downloaded 1/1 tracks")]


def test_download_manager_retries_and_marks_failed(tmp_path: Path) -> None:
    runner = FakeRunner(return_codes=[1, 1, 1])
    manager = DownloadManager(
        command_runner=runner,
        backoff_factory=lambda: 0,
        sleeper=lambda _seconds: None,
    )
    track = Track(artist="Artist", title="Title", youtube_url="https://youtu.be/example")

    tracks = manager.download_tracks([track], tmp_path)

    assert len(runner.commands) == 3
    assert tracks[0].status == TrackStatus.FAILED
    assert tracks[0].retry_count == 3
    assert tracks[0].error == "download failed"


def test_download_manager_skips_cached_downloads(tmp_path: Path) -> None:
    runner = FakeRunner()
    repository = JsonTrackRepository(data_dir=tmp_path)
    cached_track = Track(
        artist="Artist",
        title="Title",
        youtube_url="https://youtu.be/cached",
        local_path="/music/Artist - Title.mp3",
        status=TrackStatus.DOWNLOADED,
    )
    repository.save_download_cache([cached_track])
    repository.save_tracks(
        "user",
        [
            Track(
                artist="Artist",
                title="Title",
                youtube_url="https://youtu.be/current",
                status=TrackStatus.QUEUED,
            )
        ],
    )

    tracks = DownloadManager(command_runner=runner).download_and_store_tracks("user", repository)

    assert runner.commands == []
    assert tracks[0].status == TrackStatus.DOWNLOADED
    assert tracks[0].youtube_url == "https://youtu.be/current"
    assert tracks[0].local_path == "/music/Artist - Title.mp3"
    assert repository.load_tracks("user") == tracks


def test_download_manager_validates_concurrency(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="concurrency"):
        DownloadManager().download_tracks([], tmp_path, concurrency=0)


def test_download_manager_prioritizes_selected_track(tmp_path: Path) -> None:
    runner = FakeRunner()
    repository = JsonTrackRepository(data_dir=tmp_path)
    first = Track(artist="First", title="Track", youtube_url="https://youtu.be/first")
    second = Track(artist="Second", title="Track", youtube_url="https://youtu.be/second")
    repository.save_tracks("user", [first, second])

    DownloadManager(command_runner=runner).download_and_store_tracks(
        "user",
        repository,
        concurrency=1,
        priority_cache_key=second.cache_key,
    )

    assert runner.commands[0][-1] == "https://youtu.be/second"
    assert [track.artist for track in repository.load_tracks("user")] == ["First", "Second"]


def test_download_manager_can_limit_priority_download_to_one_track(tmp_path: Path) -> None:
    runner = FakeRunner()
    repository = JsonTrackRepository(data_dir=tmp_path)
    first = Track(artist="First", title="Track", youtube_url="https://youtu.be/first")
    second = Track(artist="Second", title="Track", youtube_url="https://youtu.be/second")
    repository.save_tracks("user", [first, second])

    DownloadManager(command_runner=runner).download_and_store_tracks(
        "user",
        repository,
        concurrency=2,
        priority_cache_key=second.cache_key,
        max_downloads=1,
    )

    assert len(runner.commands) == 1
    assert runner.commands[0][-1] == "https://youtu.be/second"
    tracks = repository.load_tracks("user")
    assert tracks[0].status == TrackStatus.FETCHED
    assert tracks[1].status == TrackStatus.DOWNLOADED

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from my_lastfm_player.download import DownloadManager, _probe_audio_file
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.storage import JsonTrackRepository


class FakeRunner:
    def __init__(
        self,
        return_codes: list[int] | None = None,
        error: OSError | None = None,
    ) -> None:
        self.return_codes = return_codes or [0]
        self.error = error
        self.commands: list[list[str]] = []

    def __call__(self, command, **_kwargs) -> subprocess.CompletedProcess[str]:
        self.commands.append(list(command))
        if self.error is not None:
            raise self.error
        return_code = self.return_codes.pop(0) if self.return_codes else 0
        stderr = "download failed" if return_code else ""
        if return_code == 0 and "--output" in command:
            output_idx = list(command).index("--output") + 1
            template = command[output_idx]
            Path(template.replace("%(ext)s", "webm")).touch()
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
    track_updates: list[Track] = []

    tracks = manager.download_tracks(
        [track],
        tmp_path,
        progress_callback=lambda value, message: progress.append((value, message)),
        track_update_callback=track_updates.append,
    )

    assert tracks == [
        Track(
            artist="Artist",
            title="Title",
            youtube_url="https://youtu.be/example",
            local_path=str(tmp_path / "Artist - Title.webm"),
            status=TrackStatus.DOWNLOADED,
            file_type="WEBM",
        )
    ]
    assert runner.commands == [
        [
            "yt-dlp",
            "-f",
            "bestaudio",
            "--no-playlist",
            "--output",
            str(tmp_path / "Artist - Title.%(ext)s"),
            "https://youtu.be/example",
        ]
    ]
    assert progress == [(0, "Queued 1 downloads"), (100, "Downloaded 1/1 tracks")]
    assert [track.status for track in track_updates] == [
        TrackStatus.DOWNLOADING,
        TrackStatus.DOWNLOADED,
    ]
    assert track_updates[-1].file_type == "WEBM"


def test_probe_audio_file_reads_ffprobe_metadata(monkeypatch, tmp_path: Path) -> None:
    audio_path = tmp_path / "Artist - Title.m4a"
    audio_path.touch()

    def fake_run(command, **_kwargs) -> subprocess.CompletedProcess[str]:
        assert command[-1] == str(audio_path)
        return subprocess.CompletedProcess(
            command,
            0,
            stdout='{"format": {"format_name": "mov,mp4,m4a", "bit_rate": "191500"}}',
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert _probe_audio_file(audio_path) == ("M4A", 192)


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


def test_download_manager_pause_and_resume_toggle_queue_state() -> None:
    manager = DownloadManager()

    manager.pause()
    assert not manager._resume_event.is_set()

    manager.resume()
    assert manager._resume_event.is_set()


def test_download_manager_reports_zero_candidates(tmp_path: Path) -> None:
    progress: list[tuple[int, str]] = []
    tracks = [Track(artist="Artist", title="Title")]

    result = DownloadManager(command_runner=FakeRunner()).download_tracks(
        tracks,
        tmp_path,
        progress_callback=lambda value, message: progress.append((value, message)),
    )

    assert result == tracks
    assert progress == [(0, "Queued 0 downloads")]


def test_download_manager_handles_missing_url_and_command_error(tmp_path: Path) -> None:
    missing_url_track = Track(artist="Artist", title="Title", status=TrackStatus.QUEUED)

    missing_url_result = DownloadManager(
        command_runner=FakeRunner(),
        max_retries=1,
    )._download_track_with_retries(missing_url_track, tmp_path)

    assert missing_url_result.status == TrackStatus.FAILED
    assert missing_url_result.error == "Track has no YouTube URL"

    command_error_result = DownloadManager(
        command_runner=FakeRunner(error=OSError("missing executable")),
        max_retries=1,
    ).download_tracks(
        [
            Track(
                artist="Artist",
                title="Title",
                youtube_url="https://youtu.be/example",
                status=TrackStatus.QUEUED,
            )
        ],
        tmp_path,
    )

    assert command_error_result[0].status == TrackStatus.FAILED
    assert "Could not run yt-dlp" in command_error_result[0].error


def test_download_manager_skips_cached_downloads(tmp_path: Path) -> None:
    runner = FakeRunner()
    repository = JsonTrackRepository(data_dir=tmp_path)
    audio_path = tmp_path / "Artist - Title.mp3"
    audio_path.touch()
    cached_track = Track(
        artist="Artist",
        title="Title",
        youtube_url="https://youtu.be/cached",
        local_path=str(audio_path),
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
    assert tracks[0].local_path == str(audio_path)
    assert repository.load_tracks("user") == tracks


def test_download_manager_redownloads_stale_download_paths(tmp_path: Path) -> None:
    runner = FakeRunner()
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_tracks(
        "user",
        [
            Track(
                artist="Artist",
                title="Title",
                youtube_url="https://youtu.be/current",
                local_path=str(tmp_path / "missing.mp3"),
                status=TrackStatus.DOWNLOADED,
            )
        ],
    )

    tracks = DownloadManager(command_runner=runner).download_and_store_tracks("user", repository)

    assert len(runner.commands) == 1
    assert tracks[0].status == TrackStatus.DOWNLOADED
    assert tracks[0].local_path == str(tmp_path / "downloads" / "Artist - Title.webm")


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

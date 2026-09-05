from __future__ import annotations

import re
import subprocess
import threading
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from my_lastfm_player import download as download_module
from my_lastfm_player.download import (
    MAX_RETRIES,
    PLAYER_CLIENT_LADDER,
    DownloadManager,
    _bit_rate_to_kbps,
    _format_name_to_file_type,
    _player_client_for_attempt,
    _probe_audio_file,
)
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.storage import JsonTrackRepository
from my_lastfm_player.youtube_work import WorkCancelled


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


class BlockingRunner:
    def __init__(self, expected_parallel: int) -> None:
        self.expected_parallel = expected_parallel
        self.commands: list[list[str]] = []
        self.active = 0
        self.max_active = 0
        self.lock = threading.Lock()
        self.release = threading.Event()

    def __call__(self, command, **_kwargs) -> subprocess.CompletedProcess[str]:
        self.commands.append(list(command))
        with self.lock:
            self.active += 1
            self.max_active = max(self.max_active, self.active)
            if self.active == self.expected_parallel:
                self.release.set()
        try:
            assert self.release.wait(timeout=2), "download workers did not reach concurrency"
            if "--output" in command:
                output_idx = list(command).index("--output") + 1
                template = command[output_idx]
                Path(template.replace("%(ext)s", "webm")).touch()
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
        finally:
            with self.lock:
                self.active -= 1


def queued_track(
    artist: str = "Artist",
    title: str = "Title",
    youtube_url: str = "https://youtu.be/example",
) -> Track:
    """Return a queued track with a resolved YouTube URL."""

    return Track(
        artist=artist,
        title=title,
        youtube_url=youtube_url,
        status=TrackStatus.QUEUED,
    )


def test_download_manager_downloads_queued_tracks(tmp_path: Path) -> None:
    runner = FakeRunner()
    manager = DownloadManager(
        command_runner=runner,
        backoff_factory=lambda: 0,
        sleeper=lambda _seconds: None,
    )
    track = queued_track()
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
            "bestaudio/bestaudio*/best",
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


def test_download_manager_uses_configured_parallel_worker_count(tmp_path: Path) -> None:
    runner = BlockingRunner(expected_parallel=4)
    manager = DownloadManager(
        command_runner=runner,
        max_retries=1,
        backoff_factory=lambda: 0,
        sleeper=lambda _seconds: None,
    )
    tracks = [
        Track(
            artist=f"Artist {index}",
            title=f"Title {index}",
            youtube_url=f"https://youtu.be/example-{index}",
            status=TrackStatus.QUEUED,
        )
        for index in range(4)
    ]

    result = manager.download_tracks(tracks, tmp_path, concurrency=4)

    assert len(runner.commands) == 4
    assert runner.max_active == 4
    assert [track.status for track in result] == [TrackStatus.DOWNLOADED] * 4


def test_download_manager_only_marks_active_window_and_leaves_unscheduled_on_stop(
    tmp_path: Path,
) -> None:
    manager = DownloadManager()
    started = threading.Event()
    release = threading.Event()
    stop_event = threading.Event()
    active = 0
    lock = threading.Lock()
    updates: list[Track] = []

    def download(track: Track, _downloads_dir: Path, _stop_event=None) -> Track:
        nonlocal active
        with lock:
            active += 1
            if active == 2:
                started.set()
        assert release.wait(timeout=2)
        return track.with_status(TrackStatus.DOWNLOADED)

    manager._download_track_with_retries = download  # type: ignore[method-assign]
    tracks = [queued_track(title=str(index)) for index in range(8)]

    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            manager.download_tracks,
            tracks,
            tmp_path,
            concurrency=2,
            track_update_callback=updates.append,
            stop_event=stop_event,
        )
        assert started.wait(timeout=2)
        assert [track.status for track in updates] == [
            TrackStatus.DOWNLOADING,
            TrackStatus.DOWNLOADING,
        ]
        stop_event.set()
        release.set()
        result = future.result(timeout=5)

    assert [track.status for track in result[:2]] == [TrackStatus.DOWNLOADED] * 2
    assert [track.status for track in result[2:]] == [TrackStatus.QUEUED] * 6


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
    runner = FakeRunner(return_codes=[1] * MAX_RETRIES)
    manager = DownloadManager(
        command_runner=runner,
        backoff_factory=lambda: 0,
        sleeper=lambda _seconds: None,
    )
    track = Track(artist="Artist", title="Title", youtube_url="https://youtu.be/example")

    tracks = manager.download_tracks([track], tmp_path)

    assert len(runner.commands) == MAX_RETRIES
    assert tracks[0].status == TrackStatus.FAILED
    assert tracks[0].retry_count == MAX_RETRIES
    assert tracks[0].error == "download failed"


def test_download_manager_walks_the_player_client_ladder_across_retries(tmp_path: Path) -> None:
    runner = FakeRunner(return_codes=[1] * MAX_RETRIES)
    manager = DownloadManager(
        command_runner=runner,
        backoff_factory=lambda: 0,
        sleeper=lambda _seconds: None,
    )
    track = Track(artist="Artist", title="Title", youtube_url="https://youtu.be/example")

    manager.download_tracks([track], tmp_path)

    forced_clients = [
        command[command.index("--extractor-args") + 1] if "--extractor-args" in command else ""
        for command in runner.commands
    ]
    assert forced_clients == [
        f"youtube:player_client={client}" if client else "" for client in PLAYER_CLIENT_LADDER
    ]


def test_download_manager_recovers_when_a_later_player_client_succeeds(tmp_path: Path) -> None:
    runner = FakeRunner(return_codes=[1, 0])
    manager = DownloadManager(
        command_runner=runner,
        backoff_factory=lambda: 0,
        sleeper=lambda _seconds: None,
    )
    track = Track(artist="Artist", title="Title", youtube_url="https://youtu.be/example")

    tracks = manager.download_tracks([track], tmp_path)

    assert tracks[0].status == TrackStatus.DOWNLOADED
    assert len(runner.commands) == 2
    assert "--extractor-args" not in runner.commands[0]
    assert runner.commands[1][runner.commands[1].index("--extractor-args") + 1] == (
        f"youtube:player_client={PLAYER_CLIENT_LADDER[1]}"
    )


def test_player_client_ladder_only_names_usable_clients() -> None:
    # yt-dlp silently skips a client name it does not know ("Skipping unsupported client"),
    # which turns that rung into a wasted retry. The live e2e test checks the names against
    # the installed yt-dlp; this one catches the structural mistakes offline.
    assert PLAYER_CLIENT_LADDER, "the ladder must offer at least one attempt"
    assert PLAYER_CLIENT_LADDER[0] == "", "attempt 1 must use yt-dlp's own client rotation"

    forced_clients = [
        client for rung in PLAYER_CLIENT_LADDER[1:] for client in rung.split(",") if rung
    ]
    assert forced_clients, "every retry after the first must force explicit clients"
    assert all(re.fullmatch(r"[a-z][a-z0-9_]*", client) for client in forced_clients), (
        f"ladder holds a malformed client name: {forced_clients}"
    )
    assert len(forced_clients) == len(set(forced_clients)), (
        f"a client repeated across rungs wastes a retry: {forced_clients}"
    )


def test_player_client_for_attempt_wraps_around_the_ladder() -> None:
    assert _player_client_for_attempt(1) == PLAYER_CLIENT_LADDER[0]
    assert _player_client_for_attempt(2) == PLAYER_CLIENT_LADDER[1]
    assert _player_client_for_attempt(len(PLAYER_CLIENT_LADDER) + 1) == PLAYER_CLIENT_LADDER[0]


def test_download_manager_stop_wakes_blocked_threads_and_marks_failed(tmp_path: Path) -> None:
    blocked = threading.Event()
    released = threading.Event()

    def blocking_runner(command, **_kwargs):
        blocked.set()
        released.wait(timeout=2)
        raise subprocess.TimeoutExpired(command, 600)

    manager = DownloadManager(
        command_runner=blocking_runner,
        max_retries=1,
        backoff_factory=lambda: 0,
        sleeper=lambda _: None,
    )
    track = queued_track()

    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(manager.download_tracks, [track], tmp_path)
        blocked.wait(timeout=2)
        released.set()
        tracks = future.result(timeout=5)

    assert tracks[0].status == TrackStatus.FAILED


def test_operation_stop_aborts_pending_retries_without_affecting_other_runs(
    tmp_path: Path,
) -> None:
    manager = DownloadManager(
        command_runner=FakeRunner(return_codes=[1]),
        max_retries=3,
        backoff_factory=lambda: 0,
        sleeper=lambda _: None,
    )
    stop_event = threading.Event()
    stop_event.set()
    track = queued_track()

    tracks = manager.download_tracks([track], tmp_path, stop_event=stop_event)

    assert tracks[0].status == TrackStatus.QUEUED
    assert tracks[0].error is None


def test_work_cancelled_during_download_returns_track_to_queue(tmp_path: Path) -> None:
    manager = DownloadManager(max_retries=1)
    manager._download_track = MagicMock(side_effect=WorkCancelled("stopped"))

    result = manager._download_track_with_retries(queued_track(), tmp_path)

    assert result.status is TrackStatus.QUEUED
    assert result.error is None


def test_operation_stop_keeps_pending_download_queued(tmp_path: Path) -> None:
    runner = FakeRunner()
    manager = DownloadManager(command_runner=runner)
    stop_event = threading.Event()
    stop_event.set()

    tracks = manager.download_tracks([queued_track()], tmp_path, stop_event=stop_event)

    assert tracks[0].status is TrackStatus.QUEUED
    assert runner.commands == []


def test_unexpected_download_failure_is_isolated_to_one_track(tmp_path: Path) -> None:
    manager = DownloadManager()
    broken = queued_track(artist="Broken")
    fine = queued_track(artist="Fine")

    def download(track: Track, _downloads_dir: Path, _stop_event=None) -> Track:
        if track.artist == "Broken":
            raise RuntimeError("isolated failure")
        return track.with_status(TrackStatus.DOWNLOADED)

    manager._download_track_with_retries = download  # type: ignore[method-assign]

    tracks = manager.download_tracks([broken, fine], tmp_path, concurrency=2)

    assert tracks[0].status is TrackStatus.FAILED
    assert tracks[0].error == "isolated failure"
    assert tracks[1].status is TrackStatus.DOWNLOADED


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


def test_download_manager_preserves_tracks_added_while_download_runs(tmp_path: Path) -> None:
    runner = FakeRunner()
    repository = JsonTrackRepository(data_dir=tmp_path)
    first = Track(
        artist="First",
        title="Track",
        youtube_url="https://youtu.be/first",
        status=TrackStatus.QUEUED,
    )
    later = Track(artist="Later", title="Track")
    repository.save_tracks("user", [first])

    def add_later_track(_value: int, _message: str) -> None:
        repository.save_tracks("user", [first, later])

    tracks = DownloadManager(command_runner=runner).download_and_store_tracks(
        "user",
        repository,
        progress_callback=add_later_track,
    )

    assert [track.artist for track in tracks] == ["First", "Later"]
    assert tracks[0].status == TrackStatus.DOWNLOADED
    assert tracks[1] == later
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


def test_download_manager_includes_cookies_browser_flag(tmp_path: Path) -> None:
    runner = FakeRunner()
    manager = DownloadManager(
        command_runner=runner,
        cookies_browser="firefox",
        backoff_factory=lambda: 0,
        sleeper=lambda _: None,
    )
    track = queued_track()

    manager.download_tracks([track], tmp_path)

    assert "--cookies-from-browser" in runner.commands[0]
    assert "firefox" in runner.commands[0]


def test_download_manager_fails_when_output_file_not_found(tmp_path: Path) -> None:
    def no_file_runner(command, **_kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    manager = DownloadManager(
        command_runner=no_file_runner,
        backoff_factory=lambda: 0,
        sleeper=lambda _: None,
        max_retries=1,
    )
    track = queued_track()

    tracks = manager.download_tracks([track], tmp_path)

    assert tracks[0].status == TrackStatus.FAILED
    assert "not found" in tracks[0].error.lower()


def test_probe_audio_file_returns_path_type_when_subprocess_raises(
    monkeypatch, tmp_path: Path
) -> None:
    audio_path = tmp_path / "Artist - Title.mp3"
    audio_path.touch()

    def raise_os_error(*_args, **_kwargs):
        raise OSError("ffprobe not found")

    monkeypatch.setattr(subprocess, "run", raise_os_error)

    file_type, bitrate = _probe_audio_file(audio_path)

    assert file_type == "MP3"
    assert bitrate is None


def test_probe_audio_file_returns_path_type_when_ffprobe_returns_invalid_json(
    monkeypatch, tmp_path: Path
) -> None:
    audio_path = tmp_path / "Artist - Title.mp3"
    audio_path.touch()

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *_a, **_k: subprocess.CompletedProcess([], 0, stdout="not valid json", stderr=""),
    )

    file_type, bitrate = _probe_audio_file(audio_path)

    assert file_type == "MP3"
    assert bitrate is None


def test_probe_audio_file_uses_cancellable_runner_and_handles_probe_failure(
    monkeypatch, tmp_path: Path
) -> None:
    audio_path = tmp_path / "track.mp3"
    audio_path.touch()
    stop_event = threading.Event()
    monkeypatch.setattr(
        download_module,
        "run_cancellable_command",
        lambda command, **_kwargs: subprocess.CompletedProcess(command, 1, "", "failed"),
    )

    assert _probe_audio_file(audio_path, stop_event) == ("MP3", None)


def test_probe_audio_file_returns_path_type_when_format_is_not_dict(
    monkeypatch, tmp_path: Path
) -> None:
    audio_path = tmp_path / "Artist - Title.mp3"
    audio_path.touch()

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *_a, **_k: subprocess.CompletedProcess(
            [], 0, stdout='{"format": "string not a dict"}', stderr=""
        ),
    )

    file_type, bitrate = _probe_audio_file(audio_path)

    assert file_type == "MP3"
    assert bitrate is None


def test_format_name_to_file_type_returns_none_for_non_string_or_empty() -> None:
    assert _format_name_to_file_type(None) is None
    assert _format_name_to_file_type("") is None
    assert _format_name_to_file_type(42) is None


def test_format_name_to_file_type_falls_back_to_first_unknown_format() -> None:
    assert _format_name_to_file_type("flv") == "FLV"


def test_bit_rate_to_kbps_returns_none_for_non_numeric_input() -> None:
    assert _bit_rate_to_kbps("not-a-number") is None
    assert _bit_rate_to_kbps(None) is None


def test_bit_rate_to_kbps_returns_none_for_non_positive_values() -> None:
    assert _bit_rate_to_kbps(0) is None
    assert _bit_rate_to_kbps(-1000) is None


def test_download_manager_marks_failed_on_timeout(tmp_path: Path) -> None:
    def timeout_runner(command, **_kwargs):
        raise subprocess.TimeoutExpired(command, 600)

    manager = DownloadManager(
        command_runner=timeout_runner,
        max_retries=1,
        backoff_factory=lambda: 0,
        sleeper=lambda _: None,
    )
    track = queued_track()

    tracks = manager.download_tracks([track], tmp_path)

    assert tracks[0].status == TrackStatus.FAILED
    assert "timed out" in tracks[0].error.lower()


def test_probe_audio_file_returns_path_type_when_ffprobe_times_out(
    monkeypatch, tmp_path: Path
) -> None:
    audio_path = tmp_path / "Artist - Title.mp3"
    audio_path.touch()

    def raise_timeout(*_args, **_kwargs):
        raise subprocess.TimeoutExpired(["ffprobe"], 30)

    monkeypatch.setattr(subprocess, "run", raise_timeout)

    file_type, bitrate = _probe_audio_file(audio_path)

    assert file_type == "MP3"
    assert bitrate is None

"""Exact subprocess contract of the downloader and ffprobe audio probing."""

from __future__ import annotations

import os
import subprocess
import threading
from dataclasses import replace
from pathlib import Path

import pytest

from my_lastfm_player import download
from my_lastfm_player.download import (
    AUDIO_FORMAT_SELECTOR,
    DOWNLOAD_TIMEOUT_SECONDS,
    MAX_RETRIES,
    PROBE_TIMEOUT_SECONDS,
    DownloadError,
    DownloadManager,
    _bit_rate_to_kbps,
    _file_type_from_path,
    _format_name_to_file_type,
    _probe_audio_file,
)
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.storage import JsonTrackRepository
from my_lastfm_player.youtube_work import WorkCancelled, YouTubeWorkLimiter

FFPROBE_ARGS = ["ffprobe", "-v", "error", "-show_entries", "format=format_name,bit_rate"]


def _completed(stdout: str = "", returncode: int = 0) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(["cmd"], returncode, stdout, "")


def test_custom_runner_receives_exact_subprocess_options() -> None:
    calls: list[tuple] = []

    def runner(command, **kwargs):
        calls.append((command, kwargs))
        return _completed("ok")

    manager = DownloadManager(command_runner=runner)

    result = manager._run(["yt-dlp", "--version"])

    assert result.stdout == "ok"
    assert calls == [
        (
            ["yt-dlp", "--version"],
            {
                "check": False,
                "capture_output": True,
                "text": True,
                "encoding": "utf-8",
                "timeout": DOWNLOAD_TIMEOUT_SECONDS,
            },
        )
    ]


def test_default_runner_goes_through_the_limiter_and_cancellable_command(monkeypatch) -> None:
    slots: list[tuple] = []
    commands: list[tuple] = []

    class SpyLimiter(YouTubeWorkLimiter):
        def slot(self, stop_event, work_key=None):
            slots.append((stop_event, work_key))
            return super().slot(stop_event, work_key)

    def fake_command(command, *, stop_event, timeout):
        commands.append((command, stop_event, timeout))
        return _completed("done")

    monkeypatch.setattr(download, "run_cancellable_command", fake_command)
    stop_event = threading.Event()
    manager = DownloadManager(work_limiter=SpyLimiter())

    result = manager._run(["yt-dlp", "url"], stop_event=stop_event, work_key="download:x")

    assert result.stdout == "done"
    assert slots == [(stop_event, "download:x")]
    assert commands == [(["yt-dlp", "url"], stop_event, DOWNLOAD_TIMEOUT_SECONDS)]


def test_default_runner_refuses_to_start_once_stopped(monkeypatch) -> None:
    monkeypatch.setattr(
        download, "run_cancellable_command", lambda *_a, **_k: pytest.fail("must not run")
    )
    stop_event = threading.Event()
    stop_event.set()

    with pytest.raises(WorkCancelled, match="^YouTube download cancelled$"):
        DownloadManager()._run(["yt-dlp"], stop_event=stop_event, work_key="download:x")


def test_default_runner_only_blocks_the_same_work_key(monkeypatch) -> None:
    """A busy key must not stall a different key, and the stop event must be honoured."""

    limiter = YouTubeWorkLimiter(limit=2)
    monkeypatch.setattr(download, "run_cancellable_command", lambda *_a, **_k: _completed())
    manager = DownloadManager(work_limiter=limiter)
    stop_event = threading.Event()

    with limiter.slot(None, "download:busy"):
        manager._run(["yt-dlp"], stop_event=stop_event, work_key="download:other")
        stop_event.set()
        with pytest.raises(WorkCancelled):
            manager._run(["yt-dlp"], stop_event=stop_event, work_key="download:busy")


def test_runner_errors_become_download_errors() -> None:
    def timeout_runner(command, **_kwargs):
        raise subprocess.TimeoutExpired(command, DOWNLOAD_TIMEOUT_SECONDS)

    def missing_runner(_command, **_kwargs):
        raise FileNotFoundError("no such file")

    with pytest.raises(DownloadError, match="^yt-dlp download timed out after 600s$"):
        DownloadManager(command_runner=timeout_runner)._run(["yt-dlp"])
    with pytest.raises(DownloadError, match="^Could not run yt-dlp: no such file$"):
        DownloadManager(command_runner=missing_runner)._run(["yt-dlp"])


def test_probe_runs_ffprobe_with_exact_arguments(monkeypatch, tmp_path: Path) -> None:
    calls: list[tuple] = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return _completed('{"format": {"format_name": "matroska,webm", "bit_rate": "131500"}}')

    monkeypatch.setattr(download.subprocess, "run", fake_run)
    audio = tmp_path / "song.webm"

    assert _probe_audio_file(audio) == ("WEBM", 132)
    assert calls == [
        (
            [*FFPROBE_ARGS, "-of", "json", str(audio)],
            {
                "check": False,
                "capture_output": True,
                "text": True,
                "encoding": "utf-8",
                "timeout": PROBE_TIMEOUT_SECONDS,
            },
        )
    ]


def test_cancellable_probe_passes_the_stop_event_and_timeout(monkeypatch, tmp_path: Path) -> None:
    calls: list[tuple] = []

    def fake_command(command, *, stop_event, timeout):
        calls.append((command, stop_event, timeout))
        return _completed('{"format": {"format_name": "ogg", "bit_rate": "96000"}}')

    monkeypatch.setattr(download, "run_cancellable_command", fake_command)
    stop_event = threading.Event()
    audio = tmp_path / "song.opus"

    assert _probe_audio_file(audio, stop_event) == ("OGG", 96)
    expected_command = [*FFPROBE_ARGS, "-of", "json", str(audio)]
    assert calls == [(expected_command, stop_event, PROBE_TIMEOUT_SECONDS)]


@pytest.mark.parametrize(
    ("stdout", "expected"),
    [
        ("", ("MP3", None)),
        ('{"format": {"bit_rate": "128000"}}', ("MP3", 128)),
        ('{"format": {"format_name": "", "bit_rate": "x"}}', ("MP3", None)),
    ],
)
def test_probe_falls_back_to_the_file_extension(monkeypatch, tmp_path, stdout, expected) -> None:
    monkeypatch.setattr(download.subprocess, "run", lambda *_a, **_k: _completed(stdout))

    assert _probe_audio_file(tmp_path / "song.mp3") == expected


@pytest.mark.parametrize(
    ("format_name", "expected"),
    [
        ("mp3", "MP3"),
        ("mov,mp4,m4a,3gp,3g2,mj2", "M4A"),
        ("matroska,webm", "WEBM"),
        ("opus", "OPUS"),
        ("ogg", "OGG"),
        ("flac", "FLAC"),
        ("wav", "WAV"),
        ("webm,mp3", "MP3"),
        ("ogg,opus", "OPUS"),
        (" AAC , adts", "AAC"),
        (",,", None),
        ("", None),
        (None, None),
    ],
)
def test_format_name_prefers_known_audio_formats(format_name, expected) -> None:
    assert _format_name_to_file_type(format_name) == expected


def test_file_type_and_bit_rate_helpers() -> None:
    assert _file_type_from_path(Path("a/b.opus")) == "OPUS"
    assert _file_type_from_path(Path("a/b")) is None
    assert _bit_rate_to_kbps("128499") == 128
    assert _bit_rate_to_kbps("1") == 0
    assert _bit_rate_to_kbps("0") is None
    assert _bit_rate_to_kbps(None) is None


# --- retry ladder and orchestration ---------------------------------------------------


def _track(**kwargs) -> Track:
    values = {"artist": "Artist", "title": "Title", "youtube_url": "https://youtu.be/x"}
    values.update(kwargs)
    return Track(status=values.pop("status", TrackStatus.QUEUED), **values)


class FakeYtDlp:
    """Command runner that writes the file yt-dlp would have written."""

    def __init__(self, *, fail: int = 0, stderr: str = "boom\n") -> None:
        self.commands: list[list[str]] = []
        self.fail = fail
        self.stderr = stderr

    def __call__(self, command, **_kwargs):
        self.commands.append(list(command))
        if len(self.commands) <= self.fail:
            return subprocess.CompletedProcess(command, 1, "", self.stderr)
        template = command[command.index("--output") + 1]
        Path(template.replace("%(ext)s", "opus")).write_bytes(b"audio")
        return subprocess.CompletedProcess(command, 0, "", "")


@pytest.fixture
def probe_calls(monkeypatch) -> list[tuple]:
    calls: list[tuple] = []

    def fake_probe(path, stop_event=None):
        calls.append((path, stop_event))
        return "OPUS", 160

    monkeypatch.setattr(download, "_probe_audio_file", fake_probe)
    return calls


def test_download_command_per_attempt_is_exact(tmp_path: Path) -> None:
    runner = FakeYtDlp()
    manager = DownloadManager(command_runner=runner, cookies_browser="firefox")
    track = _track()
    output = str(tmp_path / "Artist - Title.%(ext)s")

    manager._download_track(track, tmp_path)
    manager._download_track(track, tmp_path, attempt=2)

    base = ["yt-dlp", "-f", AUDIO_FORMAT_SELECTOR, "--no-playlist"]
    tail = ["--cookies-from-browser", "firefox", "--output", output, "https://youtu.be/x"]
    assert runner.commands == [
        [*base, *tail],
        [*base, "--extractor-args", "youtube:player_client=web_embedded,android_vr", *tail],
    ]


def test_download_track_passes_stop_event_and_file_work_key(tmp_path: Path) -> None:
    manager = DownloadManager(command_runner=FakeYtDlp())
    calls: list[tuple] = []
    real_run = manager._run

    def spy_run(command, stop_event=None, work_key=None):
        calls.append((stop_event, work_key))
        return real_run(command, stop_event, work_key)

    manager._run = spy_run  # type: ignore[method-assign]
    stop_event = threading.Event()

    manager._download_track(_track(), tmp_path, 1, stop_event)

    assert calls == [(stop_event, "download:Artist - Title")]


def test_download_failure_messages(tmp_path: Path) -> None:
    track = _track()

    with pytest.raises(DownloadError, match="^boom$"):
        DownloadManager(command_runner=FakeYtDlp(fail=1))._download_track(track, tmp_path)
    with pytest.raises(DownloadError, match="^yt-dlp download failed$"):
        DownloadManager(command_runner=FakeYtDlp(fail=1, stderr=" \n"))._download_track(
            track, tmp_path
        )

    def succeed_without_file(command, **_kwargs):
        return subprocess.CompletedProcess(command, 0, "", "")

    with pytest.raises(DownloadError, match="^Downloaded file not found after yt-dlp succeeded$"):
        DownloadManager(command_runner=succeed_without_file)._download_track(track, tmp_path)


def test_download_track_returns_the_newest_matching_file(tmp_path: Path) -> None:
    def runner(command, **_kwargs):
        return subprocess.CompletedProcess(command, 0, "", "")

    older = tmp_path / "Artist - Title.zzz"
    newer = tmp_path / "Artist - Title.aaa"
    for path, mtime in ((older, 1_000_000), (newer, 2_000_000)):
        path.write_bytes(b"audio")
        os.utime(path, (mtime, mtime))
    (tmp_path / "Other - Song.opus").write_bytes(b"audio")

    assert DownloadManager(command_runner=runner)._download_track(_track(), tmp_path) == newer


def test_successful_retry_records_probe_results(tmp_path: Path, probe_calls) -> None:
    sleeps: list[float] = []
    manager = DownloadManager(
        command_runner=FakeYtDlp(fail=1), backoff_factory=lambda: 2.5, sleeper=sleeps.append
    )
    stop_event = threading.Event()

    result = manager._download_track_with_retries(_track(error="old"), tmp_path, stop_event)

    assert result.status is TrackStatus.DOWNLOADED
    assert result.local_path == str(tmp_path / "Artist - Title.opus")
    assert (result.file_type, result.bitrate_kbps) == ("OPUS", 160)
    assert result.error is None
    assert result.download_attempts == 1
    assert sleeps == [2.5]
    assert probe_calls == [(tmp_path / "Artist - Title.opus", stop_event)]


def test_exhausted_retries_fail_with_the_last_error(tmp_path: Path) -> None:
    sleeps: list[float] = []
    manager = DownloadManager(
        command_runner=FakeYtDlp(fail=99), backoff_factory=lambda: 1.5, sleeper=sleeps.append
    )

    result = manager._download_track_with_retries(_track(download_attempts=2), tmp_path)

    assert result.status is TrackStatus.FAILED
    assert result.error == "boom"
    assert result.download_attempts == 2 + MAX_RETRIES
    assert sleeps == [1.5] * (MAX_RETRIES - 1)


@pytest.mark.parametrize("cancel", ["before", "during"])
def test_cancelled_download_goes_back_to_the_queue(tmp_path: Path, cancel: str) -> None:
    stop_event = threading.Event()

    def runner(_command, **_kwargs):
        raise WorkCancelled("cancelled")

    if cancel == "before":
        stop_event.set()
    manager = DownloadManager(command_runner=runner)

    result = manager._download_track_with_retries(
        _track(status=TrackStatus.DOWNLOADING, error="old"), tmp_path, stop_event
    )

    assert result.status is TrackStatus.QUEUED
    assert result.error is None


def test_default_backoff_is_random_within_one_to_five_seconds() -> None:
    values = {DownloadManager().backoff_factory() for _ in range(20)}

    assert all(1.0 <= value <= 5.0 for value in values)
    assert len(values) > 1


def test_download_tracks_reports_exact_progress_and_updates(tmp_path: Path, probe_calls) -> None:
    progress: list[tuple[int, str]] = []
    updates: list[Track] = []
    tracks = [
        _track(title="One", error="old"),
        _track(title="Two"),
        _track(title="Skip", youtube_url=None, status=TrackStatus.FETCHED),
    ]
    downloads = tmp_path / "nested" / "downloads"

    results = DownloadManager(command_runner=FakeYtDlp()).download_tracks(
        tracks,
        downloads,
        concurrency=1,
        progress_callback=lambda value, message: progress.append((value, message)),
        track_update_callback=updates.append,
    )

    assert downloads.is_dir()
    assert progress == [
        (0, "Queued 2 downloads"),
        (50, "Downloaded 1/2 tracks"),
        (100, "Downloaded 2/2 tracks"),
    ]
    assert [(u.title, u.status, u.error) for u in updates] == [
        ("One", TrackStatus.DOWNLOADING, None),
        ("One", TrackStatus.DOWNLOADED, None),
        ("Two", TrackStatus.DOWNLOADING, None),
        ("Two", TrackStatus.DOWNLOADED, None),
    ]
    assert [r.status for r in results] == [
        TrackStatus.DOWNLOADED,
        TrackStatus.DOWNLOADED,
        TrackStatus.FETCHED,
    ]


def test_download_tracks_rejects_zero_concurrency(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="^concurrency must be at least 1$"):
        DownloadManager().download_tracks([], tmp_path, concurrency=0)


def test_download_tracks_isolates_an_unexpected_failure(tmp_path: Path, monkeypatch) -> None:
    manager = DownloadManager()
    stop_events: list = []

    def explode(track, _downloads_dir, stop_event=None):
        stop_events.append(stop_event)
        raise RuntimeError("disk full")

    monkeypatch.setattr(manager, "_download_track_with_retries", explode)
    stop_event = threading.Event()

    (result,) = manager.download_tracks(
        [_track(download_attempts=1)], tmp_path, stop_event=stop_event
    )

    assert (result.status, result.download_attempts, result.error) == (
        TrackStatus.FAILED,
        2,
        "disk full",
    )
    assert stop_events == [stop_event]


def test_download_tracks_stops_submitting_once_stopped(tmp_path: Path, monkeypatch) -> None:
    manager = DownloadManager()
    stop_event = threading.Event()
    started: list[str] = []

    def first_stops(track, _downloads_dir, _stop_event=None):
        started.append(track.title)
        stop_event.set()
        return replace(track, status=TrackStatus.QUEUED)

    monkeypatch.setattr(manager, "_download_track_with_retries", first_stops)

    results = manager.download_tracks(
        [_track(title="One"), _track(title="Two")], tmp_path, concurrency=1, stop_event=stop_event
    )

    assert started == ["One"]
    assert [r.status for r in results] == [TrackStatus.QUEUED, TrackStatus.QUEUED]


def test_download_and_store_journals_only_settled_updates(tmp_path: Path, probe_calls) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_tracks("alice", [_track(title="One")])
    seen: list[TrackStatus] = []
    stop_event = threading.Event()

    merged = DownloadManager(command_runner=FakeYtDlp()).download_and_store_tracks(
        "alice",
        repository,
        concurrency=1,
        track_update_callback=lambda track: seen.append(track.status),
        stop_event=stop_event,
    )

    assert seen == [TrackStatus.DOWNLOADING, TrackStatus.DOWNLOADED]
    journal = repository.user_updates_path("alice")
    assert not journal.exists()  # merge_tracks folded the journal into the saved list
    assert merged[0].status is TrackStatus.DOWNLOADED
    assert probe_calls[0][1] is stop_event


def test_download_and_store_writes_journal_lines_for_settled_updates(
    tmp_path: Path, probe_calls, monkeypatch
) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_tracks("alice", [_track(title="One")])
    journaled: list[TrackStatus] = []
    monkeypatch.setattr(
        repository, "append_track_update", lambda _user, track: journaled.append(track.status)
    )

    DownloadManager(command_runner=FakeYtDlp()).download_and_store_tracks(
        "alice", repository, concurrency=1
    )

    assert journaled == [TrackStatus.DOWNLOADED]

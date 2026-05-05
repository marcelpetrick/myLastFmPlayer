from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.storage import JsonTrackRepository
from my_lastfm_player.youtube import YouTubeLookupError, YouTubeResolver, _percent


class FakeRunner:
    def __init__(
        self,
        stdout: str = "",
        stderr: str = "",
        returncode: int = 0,
        error: OSError | None = None,
    ) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
        self.error = error
        self.commands: list[list[str]] = []

    def __call__(self, command, **_kwargs) -> subprocess.CompletedProcess[str]:
        self.commands.append(list(command))
        if self.error is not None:
            raise self.error
        return subprocess.CompletedProcess(
            args=command,
            returncode=self.returncode,
            stdout=self.stdout,
            stderr=self.stderr,
        )


def test_resolver_builds_exact_artist_title_query() -> None:
    track = Track(artist=" Artist ", title="Title (Live)")

    assert YouTubeResolver().build_query(track) == " Artist  Title (Live)"


def test_search_first_result_uses_ytdlp_search_and_webpage_url() -> None:
    runner = FakeRunner(stdout=json.dumps({"webpage_url": "https://youtube.example/watch?v=abc"}))
    resolver = YouTubeResolver(command_runner=runner, executable="yt-dlp-test")

    assert resolver.search_first_result("Artist Title") == "https://youtube.example/watch?v=abc"
    assert runner.commands == [
        [
            "yt-dlp-test",
            "--dump-single-json",
            "--no-playlist",
            "ytsearch1:Artist Title",
        ]
    ]


def test_search_first_result_uses_first_entry_when_entries_are_returned() -> None:
    runner = FakeRunner(
        stdout=json.dumps(
            {
                "entries": [
                    {"webpage_url": "https://youtube.example/watch?v=first"},
                    {"webpage_url": "https://youtube.example/watch?v=second"},
                ]
            }
        )
    )

    assert YouTubeResolver(command_runner=runner).search_first_result("query") == (
        "https://youtube.example/watch?v=first"
    )


def test_search_first_result_falls_back_to_video_id() -> None:
    runner = FakeRunner(stdout=json.dumps({"id": "abc123"}))

    assert YouTubeResolver(command_runner=runner).search_first_result("query") == (
        "https://www.youtube.com/watch?v=abc123"
    )


def test_search_first_result_falls_back_to_original_or_direct_url() -> None:
    original_runner = FakeRunner(stdout=json.dumps({"original_url": "https://youtu.be/original"}))
    direct_runner = FakeRunner(stdout=json.dumps({"url": "https://youtu.be/direct"}))

    assert YouTubeResolver(command_runner=original_runner).search_first_result("query") == (
        "https://youtu.be/original"
    )
    assert YouTubeResolver(command_runner=direct_runner).search_first_result("query") == (
        "https://youtu.be/direct"
    )


def test_search_first_result_returns_none_for_empty_or_unusable_payloads() -> None:
    assert (
        YouTubeResolver(command_runner=FakeRunner(stdout="")).search_first_result("query")
        is None
    )
    assert (
        YouTubeResolver(command_runner=FakeRunner(stdout=json.dumps({"entries": [None, "x"]})))
        .search_first_result("query")
        is None
    )
    assert (
        YouTubeResolver(command_runner=FakeRunner(stdout=json.dumps({"title": "No URL"})))
        .search_first_result("query")
        is None
    )


def test_search_first_result_raises_for_unexpected_json_shape() -> None:
    runner = FakeRunner(stdout=json.dumps(["not", "a", "dict"]))

    with pytest.raises(YouTubeLookupError, match="unexpected JSON shape"):
        YouTubeResolver(command_runner=runner).search_first_result("query")


def test_search_first_result_returns_none_for_no_results() -> None:
    runner = FakeRunner(stderr="ERROR: no video results", returncode=1)

    assert YouTubeResolver(command_runner=runner).search_first_result("query") is None


def test_search_first_result_raises_for_command_failure() -> None:
    runner = FakeRunner(stderr="network failed", returncode=1)

    with pytest.raises(YouTubeLookupError, match="network failed"):
        YouTubeResolver(command_runner=runner).search_first_result("query")


def test_search_first_result_raises_for_invalid_json() -> None:
    runner = FakeRunner(stdout="{not json")

    with pytest.raises(YouTubeLookupError, match="invalid JSON"):
        YouTubeResolver(command_runner=runner).search_first_result("query")


def test_search_first_result_raises_when_executable_cannot_run() -> None:
    runner = FakeRunner(error=OSError("missing executable"))

    with pytest.raises(YouTubeLookupError, match="Could not run"):
        YouTubeResolver(command_runner=runner).search_first_result("query")


def test_resolve_track_marks_found_as_queued() -> None:
    runner = FakeRunner(stdout=json.dumps({"webpage_url": "https://youtube.example/watch?v=abc"}))
    resolver = YouTubeResolver(command_runner=runner)

    resolved = resolver.resolve_track(Track(artist="Artist", title="Title"))

    assert resolved.youtube_url == "https://youtube.example/watch?v=abc"
    assert resolved.status == TrackStatus.QUEUED


def test_resolve_track_marks_missing_as_not_found() -> None:
    runner = FakeRunner(stderr="no results", returncode=1)
    resolver = YouTubeResolver(command_runner=runner)

    resolved = resolver.resolve_track(Track(artist="Artist", title="Title"))

    assert resolved.youtube_url is None
    assert resolved.status == TrackStatus.NOT_FOUND


def test_resolve_tracks_reports_no_result_progress() -> None:
    runner = FakeRunner(stderr="no results", returncode=1)
    resolver = YouTubeResolver(command_runner=runner)
    progress: list[tuple[int, str]] = []

    tracks = resolver.resolve_tracks(
        [Track(artist="Artist", title="Title")],
        progress_callback=lambda value, message: progress.append((value, message)),
    )

    assert tracks[0].status == TrackStatus.NOT_FOUND
    assert progress == [
        (0, "Searching 1/1: Artist - Title"),
        (99, "No YouTube result 1/1: Artist - Title"),
    ]


def test_resolve_tracks_skips_tracks_that_already_have_youtube_urls() -> None:
    runner = FakeRunner(stdout=json.dumps({"webpage_url": "https://youtube.example/watch?v=new"}))
    resolver = YouTubeResolver(command_runner=runner)
    existing = Track(artist="Artist", title="Title", youtube_url="https://youtube.example/current")

    assert resolver.resolve_tracks([existing]) == [existing]
    assert runner.commands == []


def test_resolve_tracks_skips_cached_not_found_tracks() -> None:
    runner = FakeRunner(stdout=json.dumps({"webpage_url": "https://youtube.example/watch?v=new"}))
    resolver = YouTubeResolver(command_runner=runner)
    missing = Track(artist="Artist", title="Title", status=TrackStatus.NOT_FOUND)

    assert resolver.resolve_tracks([missing]) == [missing]
    assert runner.commands == []


def test_resolve_tracks_prioritizes_and_limits_selected_track() -> None:
    runner = FakeRunner(stdout=json.dumps({"webpage_url": "https://youtube.example/watch?v=new"}))
    resolver = YouTubeResolver(command_runner=runner)
    first = Track(artist="First", title="Track")
    second = Track(artist="Second", title="Track")
    progress: list[tuple[int, str]] = []
    track_updates: list[Track] = []

    tracks = resolver.resolve_tracks(
        [first, second],
        progress_callback=lambda value, message: progress.append((value, message)),
        track_update_callback=track_updates.append,
        priority_cache_key=second.cache_key,
        max_tracks=1,
    )

    assert tracks[0] == first
    assert tracks[1].youtube_url == "https://youtube.example/watch?v=new"
    assert runner.commands[0][-1] == "ytsearch1:Second Track"
    assert progress == [
        (0, "Searching 1/1: Second - Track"),
        (99, "Resolved 1/1: Second - Track"),
    ]
    assert [track.status for track in track_updates] == [
        TrackStatus.SEARCHING,
        TrackStatus.QUEUED,
    ]
    assert [track.cache_key for track in track_updates] == [
        second.cache_key,
        second.cache_key,
    ]


def test_resolve_and_store_tracks_persists_results(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_tracks("example", [Track(artist="Artist", title="Title")])
    runner = FakeRunner(stdout=json.dumps({"webpage_url": "https://youtube.example/watch?v=abc"}))

    tracks = YouTubeResolver(command_runner=runner).resolve_and_store_tracks("example", repository)

    assert tracks == repository.load_tracks("example")
    assert repository.load_tracks("example")[0].youtube_url == "https://youtube.example/watch?v=abc"
    assert repository.load_lookup_cache()[tracks[0].cache_key].youtube_url == (
        "https://youtube.example/watch?v=abc"
    )


def test_resolve_and_store_tracks_uses_lookup_cache(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    track = Track(artist="Artist", title="Title")
    repository.save_tracks("example", [track])
    repository.save_lookup_cache(
        [
            Track(
                artist="Artist",
                title="Title",
                youtube_url="https://youtube.example/watch?v=cached",
                status=TrackStatus.QUEUED,
            )
        ]
    )
    runner = FakeRunner(stdout=json.dumps({"webpage_url": "https://youtube.example/watch?v=new"}))

    tracks = YouTubeResolver(command_runner=runner).resolve_and_store_tracks("example", repository)

    assert runner.commands == []
    assert tracks[0].youtube_url == "https://youtube.example/watch?v=cached"
    assert repository.load_tracks("example")[0].youtube_url == (
        "https://youtube.example/watch?v=cached"
    )


def test_resolve_and_store_tracks_keeps_existing_download_state(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_tracks(
        "example",
        [
            Track(
                artist="Artist",
                title="Title",
                local_path="/music/Artist - Title.mp3",
                status=TrackStatus.DOWNLOADED,
            )
        ],
    )
    runner = FakeRunner(stdout=json.dumps({"webpage_url": "https://youtube.example/watch?v=abc"}))

    tracks = YouTubeResolver(command_runner=runner).resolve_and_store_tracks("example", repository)

    assert tracks[0].status == TrackStatus.DOWNLOADED
    assert tracks[0].local_path == "/music/Artist - Title.mp3"
    assert tracks[0].youtube_url == "https://youtube.example/watch?v=abc"


def test_percent_handles_zero_total_and_caps_before_complete() -> None:
    assert _percent(0, 0) == 100
    assert _percent(999, 1000) == 99

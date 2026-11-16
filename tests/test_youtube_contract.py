"""Exact contract of the YouTube resolver: commands, progress, states and parsing."""

from __future__ import annotations

import json
import subprocess
import threading
from pathlib import Path

import pytest

from my_lastfm_player import youtube
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.storage import JsonTrackRepository
from my_lastfm_player.youtube import (
    LOOKUP_TIMEOUT_SECONDS,
    YouTubeLookupError,
    YouTubeResolver,
    _extract_youtube_url,
    _merge_existing_download_state,
    _percent,
    _simplify_artist,
    _url_from_payload,
)
from my_lastfm_player.youtube_work import WorkCancelled, YouTubeWorkLimiter


def _completed(stdout: str = "", returncode: int = 0, stderr: str = ""):
    return subprocess.CompletedProcess(["cmd"], returncode, stdout, stderr)


def _hit(video_id: str) -> str:
    return json.dumps({"entries": [{"id": video_id}]})


class ScriptedSearch:
    """Answer each query from a dict: str = video id, None = no result, Exception = raise."""

    def __init__(self, answers: dict) -> None:
        self.answers = answers
        self.calls: list[tuple] = []

    def __call__(self, query, stop_event=None, work_key=None):
        self.calls.append((query, stop_event, work_key))
        answer = self.answers.get(query)
        if isinstance(answer, BaseException):
            raise answer
        return None if answer is None else f"https://www.youtube.com/watch?v={answer}"


def test_resolver_defaults_and_injected_limiter() -> None:
    limiter = YouTubeWorkLimiter()

    default = YouTubeResolver()
    custom = YouTubeResolver(cookies_browser="brave", work_limiter=limiter)

    assert default.executable == "yt-dlp"
    assert default.cookies_browser == ""
    assert isinstance(default.work_limiter, YouTubeWorkLimiter)
    assert custom.cookies_browser == "brave"
    assert custom.work_limiter is limiter


def test_build_queries_go_from_specific_to_title_only() -> None:
    resolver = YouTubeResolver()

    assert resolver.build_queries(Track("Björk - EU Store", "Jóga")) == [
        "Björk - EU Store Jóga",
        "Björk Jóga",
        "Jóga",
    ]
    assert resolver.build_queries(Track("✦✦", "Song")) == ["✦✦ Song", "Song"]


def test_simplify_artist_cuts_at_the_first_store_suffix() -> None:
    assert _simplify_artist("Band - EU Store - Vinyl") == "Band"
    assert _simplify_artist("ETHER ✦ ensemble") == "ETHER ensemble"


def test_resolve_track_passes_stop_event_and_lookup_key_and_tries_next_query() -> None:
    resolver = YouTubeResolver()
    search = ScriptedSearch({"A - Shop Song": YouTubeLookupError("HTTP 500"), "A Song": "id1"})
    resolver.search_first_result = search  # type: ignore[method-assign]
    stop_event = threading.Event()

    result = resolver.resolve_track(Track("A - Shop", "Song", error="old"), stop_event)

    assert result.youtube_url == "https://www.youtube.com/watch?v=id1"
    assert (result.status, result.error) == (TrackStatus.QUEUED, None)
    key = "lookup:A - Shop\x1fSong"
    assert search.calls == [
        ("A - Shop Song", stop_event, key),
        ("A Song", stop_event, key),
    ]


def test_resolve_track_reports_not_found_and_raises_when_every_query_errored() -> None:
    resolver = YouTubeResolver()
    resolver.search_first_result = ScriptedSearch({})  # type: ignore[method-assign]

    missing = resolver.resolve_track(
        Track("A", "Song", youtube_url="https://stale", lookup_attempts=1)
    )

    assert (missing.status, missing.youtube_url, missing.lookup_attempts) == (
        TrackStatus.NOT_FOUND,
        None,
        2,
    )

    resolver.search_first_result = ScriptedSearch(  # type: ignore[method-assign]
        {"A Song": YouTubeLookupError("first"), "Song": YouTubeLookupError("last")}
    )
    with pytest.raises(YouTubeLookupError, match="^last$"):
        resolver.resolve_track(Track("A", "Song"))


@pytest.mark.parametrize("how", ["stopped", "cancelled"])
def test_interrupted_lookup_returns_to_fetched_without_error(how: str) -> None:
    resolver = YouTubeResolver()
    resolver.search_first_result = ScriptedSearch(  # type: ignore[method-assign]
        {"A Song": WorkCancelled("stop")}
    )
    stop_event = threading.Event()
    if how == "stopped":
        stop_event.set()

    result = resolver.resolve_track(
        Track("A", "Song", status=TrackStatus.SEARCHING, error="old"), stop_event
    )

    assert (result.status, result.error) == (TrackStatus.FETCHED, None)


def test_resolve_tracks_progress_messages_and_states() -> None:
    resolver = YouTubeResolver()
    resolver.search_first_result = ScriptedSearch({"A One": "id1"})  # type: ignore[method-assign]
    progress: list[tuple[int, str]] = []
    updates: list[tuple] = []

    results = resolver.resolve_tracks(
        [Track("A", "One", error="old"), Track("B", "Two")],
        progress_callback=lambda value, message: progress.append((value, message)),
        track_update_callback=lambda t: updates.append((t.title, t.status, t.error)),
        concurrency=1,
    )

    assert progress == [
        (0, "Searching 1/2: A - One"),
        (50, "Resolved 1/2: A - One"),
        (50, "Searching 2/2: B - Two"),
        (99, "No YouTube result 2/2: B - Two"),
    ]
    assert updates[0] == ("One", TrackStatus.SEARCHING, None)
    assert [r.status for r in results] == [TrackStatus.QUEUED, TrackStatus.NOT_FOUND]


def test_resolve_tracks_numbers_parallel_searches_in_submission_order() -> None:
    resolver = YouTubeResolver()
    release = threading.Event()

    def slow_search(query, stop_event=None, work_key=None):
        release.wait(5)
        return None

    resolver.search_first_result = slow_search  # type: ignore[method-assign]
    messages: list[str] = []

    def record(_value: int, message: str) -> None:
        messages.append(message)
        if message.startswith("Searching 3/"):
            release.set()

    resolver.resolve_tracks(
        [Track("A", "1"), Track("B", "2"), Track("C", "3")],
        progress_callback=record,
        concurrency=3,
    )

    assert [m for m in messages if m.startswith("Searching")] == [
        "Searching 1/3: A - 1",
        "Searching 2/3: B - 2",
        "Searching 3/3: C - 3",
    ]


@pytest.mark.parametrize("error", [YouTubeLookupError("HTTP 429"), RuntimeError("boom")])
def test_failed_lookup_marks_the_track_and_counts_the_attempt(error) -> None:
    resolver = YouTubeResolver()
    stop_events: list = []

    def failing(track, stop_event=None):
        stop_events.append(stop_event)
        raise error

    resolver.resolve_track = failing  # type: ignore[method-assign]
    stop_event = threading.Event()

    (result,) = resolver.resolve_tracks(
        [Track("A", "Song", lookup_attempts=1)], stop_event=stop_event
    )

    assert (result.status, result.youtube_url, result.lookup_attempts, result.error) == (
        TrackStatus.LOOKUP_FAILED,
        None,
        2,
        str(error),
    )
    assert stop_events == [stop_event]


def test_resolve_tracks_rejects_zero_concurrency_with_exact_message() -> None:
    with pytest.raises(ValueError, match="^concurrency must be at least 1$"):
        YouTubeResolver().resolve_tracks([Track("A", "B")], concurrency=0)


def test_resolve_and_store_forwards_options_and_journals_settled_tracks(
    tmp_path: Path, monkeypatch
) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_tracks("alice", [Track("A", "Song")])
    resolver = YouTubeResolver()
    resolver.search_first_result = ScriptedSearch({"A Song": "id1"})  # type: ignore[method-assign]
    received: dict = {}
    real_resolve = resolver.resolve_tracks

    def spy(tracks, **kwargs):
        received.update(kwargs)
        return real_resolve(tracks, **kwargs)

    resolver.resolve_tracks = spy  # type: ignore[method-assign]
    journaled: list[TrackStatus] = []
    real_append = repository.append_track_update
    monkeypatch.setattr(
        repository,
        "append_track_update",
        lambda user, track: (journaled.append(track.status), real_append(user, track)),
    )
    seen: list[TrackStatus] = []
    stop_event = threading.Event()

    def progress(_value, _message):
        return None

    merged = resolver.resolve_and_store_tracks(
        "alice",
        repository,
        progress_callback=progress,
        track_update_callback=lambda t: seen.append(t.status),
        priority_cache_key="A\x1fSong",
        max_tracks=7,
        concurrency=2,
        stop_event=stop_event,
    )

    assert received["progress_callback"] is progress
    assert received["priority_cache_key"] == "A\x1fSong"
    assert received["max_tracks"] == 7
    assert received["concurrency"] == 2
    assert received["stop_event"] is stop_event
    assert seen == [TrackStatus.SEARCHING, TrackStatus.QUEUED]
    assert journaled == [TrackStatus.QUEUED]
    assert merged[0].youtube_url == "https://www.youtube.com/watch?v=id1"


def test_merge_existing_download_state_keeps_finished_downloads(tmp_path: Path) -> None:
    current = [Track("A", "Song", status=TrackStatus.DOWNLOADED, local_path="/a.opus")]
    resolved = [
        Track("A", "Song", youtube_url="https://y", status=TrackStatus.QUEUED),
        Track("New", "Song", youtube_url="https://n", status=TrackStatus.QUEUED),
    ]

    merged = _merge_existing_download_state(resolved, current)

    assert (merged[0].status, merged[0].local_path) == (TrackStatus.DOWNLOADED, "/a.opus")
    assert merged[1] == resolved[1]


def test_search_command_and_runner_arguments_are_exact() -> None:
    calls: list[tuple] = []

    def runner(command, **kwargs):
        calls.append((command, kwargs))
        return _completed(_hit("abc"))

    resolver = YouTubeResolver(command_runner=runner, cookies_browser="chrome")

    assert resolver.search_first_result("A Song") == "https://www.youtube.com/watch?v=abc"
    assert calls == [
        (
            [
                "yt-dlp",
                "--dump-single-json",
                "--no-playlist",
                "--flat-playlist",
                "--cookies-from-browser",
                "chrome",
                "ytsearch1:A Song",
            ],
            {
                "check": False,
                "capture_output": True,
                "text": True,
                "encoding": "utf-8",
                "timeout": LOOKUP_TIMEOUT_SECONDS,
            },
        )
    ]


def test_search_passes_stop_event_and_work_key_to_the_runner() -> None:
    resolver = YouTubeResolver(command_runner=lambda *_a, **_k: _completed(_hit("x")))
    calls: list[tuple] = []
    real_run = resolver._run

    def spy(command, stop_event=None, work_key=None):
        calls.append((stop_event, work_key))
        return real_run(command, stop_event, work_key)

    resolver._run = spy  # type: ignore[method-assign]
    stop_event = threading.Event()

    resolver.search_first_result("q", stop_event, "lookup:k")

    assert calls == [(stop_event, "lookup:k")]


def test_search_failure_messages() -> None:
    def failing(stderr):
        return YouTubeResolver(command_runner=lambda *_a, **_k: _completed("", 1, stderr))

    with pytest.raises(YouTubeLookupError, match="^HTTP Error 403$"):
        failing("HTTP Error 403\n").search_first_result("q")
    with pytest.raises(YouTubeLookupError, match="^yt-dlp lookup failed$"):
        failing("  ").search_first_result("q")
    assert failing("ERROR: No video results").search_first_result("q") is None


def test_default_runner_uses_the_limiter_and_cancellable_command(monkeypatch) -> None:
    slots: list[tuple] = []
    commands: list[tuple] = []

    class SpyLimiter(YouTubeWorkLimiter):
        def slot(self, stop_event, work_key=None):
            slots.append((stop_event, work_key))
            return super().slot(stop_event, work_key)

    def fake_command(command, *, stop_event, timeout):
        commands.append((command, stop_event, timeout))
        return _completed(_hit("z"))

    monkeypatch.setattr(youtube, "run_cancellable_command", fake_command)
    stop_event = threading.Event()
    resolver = YouTubeResolver(work_limiter=SpyLimiter())

    resolver._run(["yt-dlp", "q"], stop_event, "lookup:k")

    assert slots == [(stop_event, "lookup:k")]
    assert commands == [(["yt-dlp", "q"], stop_event, LOOKUP_TIMEOUT_SECONDS)]

    stop_event.set()
    with pytest.raises(WorkCancelled, match="^YouTube lookup cancelled$"):
        resolver._run(["yt-dlp", "q"], stop_event, "lookup:k")


def test_default_runner_does_not_wait_for_other_keys(monkeypatch) -> None:
    limiter = YouTubeWorkLimiter(limit=2)
    monkeypatch.setattr(youtube, "run_cancellable_command", lambda *_a, **_k: _completed())
    resolver = YouTubeResolver(work_limiter=limiter)

    with limiter.slot(None, "lookup:busy"):
        resolver._run(["yt-dlp"], None, "lookup:other")


def test_url_extraction_ignores_non_string_fields() -> None:
    assert _url_from_payload({"webpage_url": 5, "id": "abc"}) == (
        "https://www.youtube.com/watch?v=abc"
    )
    assert _url_from_payload({"id": 7}) is None
    assert _url_from_payload({"url": "", "original_url": "https://o"}) == "https://o"
    with pytest.raises(YouTubeLookupError, match="^yt-dlp returned an unexpected JSON shape$"):
        _extract_youtube_url("[1, 2]")


@pytest.mark.parametrize(
    ("done", "total", "expected"), [(0, 3, 0), (1, 2, 50), (2, 3, 66), (3, 3, 99), (0, 0, 100)]
)
def test_percent_is_floored_and_capped_below_completion(done, total, expected) -> None:
    assert _percent(done, total) == expected

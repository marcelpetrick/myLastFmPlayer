"""Workers hand their limits through unchanged and report fetch progress exactly."""

from __future__ import annotations

from pathlib import Path

from my_lastfm_player.lastfm import FetchProgress
from my_lastfm_player.storage import JsonTrackRepository
from my_lastfm_player.workers import (
    DownloadTracksWorker,
    FetchLovedTracksWorker,
    LookupTracksWorker,
)


class RecordingResolver:
    def __init__(self) -> None:
        self.kwargs: dict = {}

    def resolve_and_store_tracks(self, username, repository, **kwargs):
        self.kwargs = kwargs
        return []


class RecordingDownloadManager:
    def __init__(self) -> None:
        self.kwargs: dict = {}

    def download_and_store_tracks(self, username, repository, **kwargs):
        self.kwargs = kwargs
        return []


def test_lookup_worker_passes_priority_and_limit(tmp_path: Path) -> None:
    resolver = RecordingResolver()
    worker = LookupTracksWorker(
        "alice",
        resolver,  # type: ignore[arg-type]
        JsonTrackRepository(data_dir=tmp_path),
        priority_cache_key="artist\x1ftitle",
        max_tracks=3,
    )

    worker.run()

    assert resolver.kwargs["priority_cache_key"] == "artist\x1ftitle"
    assert resolver.kwargs["max_tracks"] == 3


def test_download_worker_passes_priority_and_limit(tmp_path: Path) -> None:
    manager = RecordingDownloadManager()
    worker = DownloadTracksWorker(
        "alice",
        manager,  # type: ignore[arg-type]
        JsonTrackRepository(data_dir=tmp_path),
        priority_cache_key="artist\x1ftitle",
        max_downloads=2,
    )

    worker.run()

    assert manager.kwargs["priority_cache_key"] == "artist\x1ftitle"
    assert manager.kwargs["max_downloads"] == 2


def test_fetch_progress_percent_is_truncated_share_of_total(tmp_path: Path) -> None:
    worker = FetchLovedTracksWorker(
        "alice",
        object(),  # type: ignore[arg-type]
        JsonTrackRepository(data_dir=tmp_path),
    )
    events: list[tuple[int, str]] = []
    worker.progress.connect(lambda percent, message: events.append((percent, message)))

    worker._report_fetch_progress(FetchProgress(2, "two of three", total_count=3))

    assert events == [(66, "two of three")]

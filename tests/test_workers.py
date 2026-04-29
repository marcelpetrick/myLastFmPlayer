from __future__ import annotations

from pathlib import Path

from my_lastfm_player.download import DownloadManager
from my_lastfm_player.lastfm import FetchProgress
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.storage import JsonTrackRepository
from my_lastfm_player.workers import (
    DownloadTracksWorker,
    FetchLovedTracksWorker,
    LookupTracksWorker,
)


class FakeScraper:
    def __init__(self, tracks: list[Track] | None = None, error: Exception | None = None) -> None:
        self.tracks = tracks or []
        self.error = error
        self.called_with: tuple[str, JsonTrackRepository] | None = None

    def fetch_and_store_loved_tracks(
        self,
        username: str,
        repository: JsonTrackRepository,
        progress_callback=None,
    ) -> list[Track]:
        self.called_with = (username, repository)
        if self.error is not None:
            raise self.error
        if progress_callback is not None:
            progress_callback(FetchProgress(1, "Fetched 1/1 tracks", total_count=1))
        repository.save_tracks(username, self.tracks)
        return self.tracks


class FakeResolver:
    def __init__(self, tracks: list[Track] | None = None, error: Exception | None = None) -> None:
        self.tracks = tracks or []
        self.error = error
        self.called_with: tuple[str, JsonTrackRepository] | None = None

    def resolve_and_store_tracks(
        self,
        username: str,
        repository: JsonTrackRepository,
    ) -> list[Track]:
        self.called_with = (username, repository)
        if self.error is not None:
            raise self.error
        repository.save_tracks(username, self.tracks)
        return self.tracks


def test_fetch_worker_emits_progress_tracks_and_finished(tmp_path: Path) -> None:
    tracks = [Track(artist="Artist", title="Title")]
    repository = JsonTrackRepository(data_dir=tmp_path)
    scraper = FakeScraper(tracks=tracks)
    worker = FetchLovedTracksWorker("example", scraper, repository)  # type: ignore[arg-type]
    progress_events: list[tuple[int, str]] = []
    loaded_events: list[tuple[str, list[Track]]] = []
    finished_events: list[bool] = []

    worker.progress.connect(lambda value, label: progress_events.append((value, label)))
    worker.tracks_loaded.connect(lambda username, loaded: loaded_events.append((username, loaded)))
    worker.finished.connect(lambda: finished_events.append(True))

    worker.run()

    assert scraper.called_with == ("example", repository)
    assert progress_events == [
        (0, "Looking up Last.fm user example"),
        (99, "Fetched 1/1 tracks"),
        (100, "Fetched 1 tracks"),
    ]
    assert loaded_events == [("example", tracks)]
    assert finished_events == [True]
    assert repository.load_tracks("example") == tracks


def test_fetch_worker_emits_error_and_finished(tmp_path: Path) -> None:
    worker = FetchLovedTracksWorker(
        "example",
        FakeScraper(error=RuntimeError("network failed")),  # type: ignore[arg-type]
        JsonTrackRepository(data_dir=tmp_path),
    )
    errors: list[str] = []
    finished_events: list[bool] = []

    worker.error.connect(errors.append)
    worker.finished.connect(lambda: finished_events.append(True))

    worker.run()

    assert errors == ["network failed"]
    assert finished_events == [True]


def test_lookup_worker_emits_progress_tracks_and_finished(tmp_path: Path) -> None:
    tracks = [Track(artist="Artist", title="Title", youtube_url="https://youtu.be/example")]
    repository = JsonTrackRepository(data_dir=tmp_path)
    resolver = FakeResolver(tracks=tracks)
    worker = LookupTracksWorker("example", resolver, repository)  # type: ignore[arg-type]
    progress_events: list[tuple[int, str]] = []
    resolved_events: list[tuple[str, list[Track]]] = []
    finished_events: list[bool] = []

    worker.progress.connect(lambda value, label: progress_events.append((value, label)))
    worker.tracks_resolved.connect(
        lambda username, loaded: resolved_events.append((username, loaded))
    )
    worker.finished.connect(lambda: finished_events.append(True))

    worker.run()

    assert resolver.called_with == ("example", repository)
    assert progress_events == [
        (0, "Resolving YouTube URLs for example"),
        (100, "Resolved 1 tracks"),
    ]
    assert resolved_events == [("example", tracks)]
    assert finished_events == [True]
    assert repository.load_tracks("example") == tracks


def test_lookup_worker_emits_error_and_finished(tmp_path: Path) -> None:
    worker = LookupTracksWorker(
        "example",
        FakeResolver(error=RuntimeError("lookup failed")),  # type: ignore[arg-type]
        JsonTrackRepository(data_dir=tmp_path),
    )
    errors: list[str] = []
    finished_events: list[bool] = []

    worker.error.connect(errors.append)
    worker.finished.connect(lambda: finished_events.append(True))

    worker.run()

    assert errors == ["lookup failed"]
    assert finished_events == [True]


class FakeDownloadManager:
    def __init__(self, tracks: list[Track] | None = None, error: Exception | None = None) -> None:
        self.tracks = tracks or []
        self.error = error
        self.called_with: tuple[str, JsonTrackRepository, int] | None = None

    def download_and_store_tracks(
        self,
        username: str,
        repository: JsonTrackRepository,
        concurrency: int,
        progress_callback=None,
    ) -> list[Track]:
        self.called_with = (username, repository, concurrency)
        if self.error is not None:
            raise self.error
        if progress_callback is not None:
            progress_callback(100, "Downloaded 1/1 tracks")
        repository.save_tracks(username, self.tracks)
        return self.tracks


def test_download_worker_emits_progress_tracks_and_finish(tmp_path: Path) -> None:
    tracks = [Track(artist="Artist", title="Title", status=TrackStatus.DOWNLOADED)]
    repository = JsonTrackRepository(data_dir=tmp_path)
    manager = FakeDownloadManager(tracks=tracks)
    worker = DownloadTracksWorker(
        "example",
        manager,  # type: ignore[arg-type]
        repository,
        concurrency=2,
    )
    progress_events: list[tuple[int, str]] = []
    downloaded_events: list[tuple[str, list[Track]]] = []
    finished_events: list[bool] = []

    worker.progress.connect(lambda value, label: progress_events.append((value, label)))
    worker.tracks_downloaded.connect(
        lambda username, loaded: downloaded_events.append((username, loaded))
    )
    worker.finished.connect(lambda: finished_events.append(True))

    worker.run()

    assert manager.called_with == ("example", repository, 2)
    assert progress_events == [(100, "Downloaded 1/1 tracks")]
    assert downloaded_events == [("example", tracks)]
    assert finished_events == [True]


def test_download_worker_emits_error_and_finished(tmp_path: Path) -> None:
    worker = DownloadTracksWorker(
        "example",
        FakeDownloadManager(error=RuntimeError("download failed")),  # type: ignore[arg-type]
        JsonTrackRepository(data_dir=tmp_path),
    )
    errors: list[str] = []
    finished_events: list[bool] = []

    worker.error.connect(errors.append)
    worker.finished.connect(lambda: finished_events.append(True))

    worker.run()

    assert errors == ["download failed"]
    assert finished_events == [True]


def test_download_worker_accepts_real_manager(tmp_path: Path) -> None:
    worker = DownloadTracksWorker(
        "example",
        DownloadManager(),
        JsonTrackRepository(data_dir=tmp_path),
    )

    assert worker.concurrency == 2

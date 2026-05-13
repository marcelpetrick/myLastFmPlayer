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
        tracks_callback=None,
        control_callback=None,
    ) -> list[Track]:
        self.called_with = (username, repository)
        if self.error is not None:
            raise self.error
        if control_callback is not None and not control_callback():
            repository.save_tracks(username, [])
            return []
        if progress_callback is not None:
            progress_callback(FetchProgress(1, "Fetched 1/1 tracks", total_count=1))
        if tracks_callback is not None:
            tracks_callback(self.tracks)
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
        progress_callback=None,
        track_update_callback=None,
        priority_cache_key: str | None = None,
        max_tracks: int | None = None,
    ) -> list[Track]:
        self.called_with = (username, repository)
        if self.error is not None:
            raise self.error
        if progress_callback is not None:
            progress_callback(50, "Resolved 1/1: Artist - Title")
        if track_update_callback is not None and self.tracks:
            track_update_callback(self.tracks[0])
        repository.save_tracks(username, self.tracks)
        return self.tracks


def test_fetch_worker_emits_progress_tracks_and_finished(tmp_path: Path) -> None:
    tracks = [Track(artist="Artist", title="Title")]
    repository = JsonTrackRepository(data_dir=tmp_path)
    scraper = FakeScraper(tracks=tracks)
    worker = FetchLovedTracksWorker("example", scraper, repository)  # type: ignore[arg-type]
    progress_events: list[tuple[int, str]] = []
    loaded_events: list[tuple[str, list[Track]]] = []
    updated_events: list[tuple[str, list[Track]]] = []
    finished_events: list[bool] = []

    worker.progress.connect(lambda value, label: progress_events.append((value, label)))
    worker.tracks_updated.connect(
        lambda username, loaded: updated_events.append((username, loaded))
    )
    worker.tracks_loaded.connect(lambda username, loaded: loaded_events.append((username, loaded)))
    worker.finished.connect(lambda: finished_events.append(True))

    worker.run()

    assert scraper.called_with == ("example", repository)
    assert progress_events == [
        (0, "Looking up Last.fm user example"),
        (99, "Fetched 1/1 tracks"),
        (100, "Fetched 1 tracks"),
    ]
    assert updated_events == [("example", tracks)]
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


def test_fetch_worker_can_stop_before_loading_tracks(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    worker = FetchLovedTracksWorker(
        "example",
        FakeScraper(tracks=[Track(artist="Artist", title="Title")]),  # type: ignore[arg-type]
        repository,
    )
    stopped_events: list[tuple[str, list[Track]]] = []
    loaded_events: list[tuple[str, list[Track]]] = []
    worker.fetch_stopped.connect(
        lambda username, loaded: stopped_events.append((username, loaded))
    )
    worker.tracks_loaded.connect(lambda username, loaded: loaded_events.append((username, loaded)))

    worker.stop_fetch()
    worker.run()

    assert stopped_events == [("example", [])]
    assert loaded_events == []


def test_lookup_worker_emits_progress_tracks_and_finished(tmp_path: Path) -> None:
    tracks = [Track(artist="Artist", title="Title", youtube_url="https://youtu.be/example")]
    repository = JsonTrackRepository(data_dir=tmp_path)
    resolver = FakeResolver(tracks=tracks)
    worker = LookupTracksWorker("example", resolver, repository)  # type: ignore[arg-type]
    progress_events: list[tuple[int, str]] = []
    resolved_events: list[tuple[str, list[Track]]] = []
    updated_events: list[tuple[str, Track]] = []
    finished_events: list[bool] = []

    worker.progress.connect(lambda value, label: progress_events.append((value, label)))
    worker.track_updated.connect(
        lambda username, track: updated_events.append((username, track))
    )
    worker.tracks_resolved.connect(
        lambda username, loaded: resolved_events.append((username, loaded))
    )
    worker.finished.connect(lambda: finished_events.append(True))

    worker.run()

    assert resolver.called_with == ("example", repository)
    assert progress_events == [
        (0, "Resolving YouTube URLs for example"),
        (50, "Resolved 1/1: Artist - Title"),
        (100, "Resolved 1 tracks"),
    ]
    assert updated_events == [("example", tracks[0])]
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
        track_update_callback=None,
        priority_cache_key: str | None = None,
        max_downloads: int | None = None,
    ) -> list[Track]:
        self.called_with = (username, repository, concurrency)
        if self.error is not None:
            raise self.error
        if progress_callback is not None:
            progress_callback(100, "Downloaded 1/1 tracks")
        if track_update_callback is not None and self.tracks:
            track_update_callback(self.tracks[0])
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
    updated_events: list[tuple[str, Track]] = []
    finished_events: list[bool] = []

    worker.progress.connect(lambda value, label: progress_events.append((value, label)))
    worker.track_updated.connect(
        lambda username, track: updated_events.append((username, track))
    )
    worker.tracks_downloaded.connect(
        lambda username, loaded: downloaded_events.append((username, loaded))
    )
    worker.finished.connect(lambda: finished_events.append(True))

    worker.run()

    assert manager.called_with == ("example", repository, 2)
    assert progress_events == [(100, "Downloaded 1/1 tracks")]
    assert updated_events == [("example", tracks[0])]
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


def test_fetch_worker_reports_zero_percent_when_total_count_is_unknown(tmp_path: Path) -> None:
    class ScraperNoTotal:
        def fetch_and_store_loved_tracks(
            self, username, repository, progress_callback=None, **_kwargs
        ):
            if progress_callback is not None:
                progress_callback(FetchProgress(1, "Fetched 1 track"))
            repository.save_tracks(username, [])
            return []

    worker = FetchLovedTracksWorker(
        "example",
        ScraperNoTotal(),  # type: ignore[arg-type]
        JsonTrackRepository(data_dir=tmp_path),
    )
    progress_events: list[tuple[int, str]] = []
    worker.progress.connect(lambda value, label: progress_events.append((value, label)))

    worker.run()

    assert (0, "Fetched 1 track") in progress_events


def test_fetch_worker_pause_and_resume_toggle_event(tmp_path: Path) -> None:
    worker = FetchLovedTracksWorker(
        "example",
        FakeScraper(),
        JsonTrackRepository(data_dir=tmp_path),
    )

    worker.pause_fetch()
    assert not worker._resume_event.is_set()

    worker.resume_fetch()
    assert worker._resume_event.is_set()


def test_fetch_worker_sleeps_while_paused_then_returns_true_on_resume(
    monkeypatch, tmp_path: Path
) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    worker = FetchLovedTracksWorker("example", FakeScraper(), repository)
    worker.pause_fetch()
    sleep_calls: list[float] = []

    def fake_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)
        worker.resume_fetch()

    monkeypatch.setattr("my_lastfm_player.workers.time.sleep", fake_sleep)

    result = worker._can_continue_fetching()

    assert sleep_calls == [0.05]
    assert result is True

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtTest import QTest

from my_lastfm_player import controller as controller_module
from my_lastfm_player.app_credentials import LastFmApiCredentials
from my_lastfm_player.controller import ApplicationController
from my_lastfm_player.dependencies import DependencyCheckResult
from my_lastfm_player.lastfm import ArtistImage
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.scrobbling import ScrobblingService
from my_lastfm_player.settings import AppSettings
from my_lastfm_player.storage import JsonTrackRepository
from my_lastfm_player.ui.main_window import MainWindow
from my_lastfm_player.workers import (
    DownloadTracksWorker,
    FetchLovedTracksWorker,
    LookupTracksWorker,
)


class FakeScrobbleNetwork:
    """Minimal pylast network stand-in that records submitted scrobbles."""

    def __init__(self, scrobbles: list[dict]) -> None:
        self.scrobbles = scrobbles

    def get_authenticated_user(self) -> SimpleNamespace:
        return SimpleNamespace(get_name=lambda properly_capitalized=False: "user")

    def scrobble(self, **kwargs) -> None:
        self.scrobbles.append(kwargs)

    def update_now_playing(self, **kwargs) -> None:
        pass


def scrobbling_controller(window, playback) -> tuple[ApplicationController, list[dict]]:
    """Return a controller wired to a connected scrobbling service and its recorded scrobbles."""

    scrobbles: list[dict] = []
    service = ScrobblingService(
        api_key="k",
        api_secret="s",
        session_key="sess",
        username="user",
        network_factory=lambda **_kwargs: FakeScrobbleNetwork(scrobbles),
    )
    service.try_connect()
    controller = ApplicationController(window, playback_service=playback)  # type: ignore[arg-type]
    controller._scrobbling_service = service
    return controller, scrobbles


def downloaded_track(tmp_path, artist: str = "Artist", title: str = "Title") -> Track:
    """Create one downloaded track backed by a fake audio file."""

    return downloaded_tracks(tmp_path, ((artist, title),))[0]


def downloaded_tracks(tmp_path, specs: tuple[tuple[str, str], ...]) -> list[Track]:
    """Create downloaded tracks backed by real (fake-content) audio files."""

    tracks: list[Track] = []
    for index, (artist, title) in enumerate(specs):
        audio_path = tmp_path / f"track{index}.mp3"
        audio_path.write_bytes(b"fake mp3")
        tracks.append(
            Track(
                artist=artist,
                title=title,
                local_path=str(audio_path),
                status=TrackStatus.DOWNLOADED,
            )
        )
    return tracks


class FakeSignal:
    def __init__(self) -> None:
        self.callbacks: list[object] = []

    def connect(self, callback: object) -> None:
        self.callbacks.append(callback)


class GenericWorker:
    def __init__(self) -> None:
        self.progress = FakeSignal()
        self.error = FakeSignal()
        self.finished = FakeSignal()
        self.moved_to_thread = None
        self.deleted = False
        self.ran = False

    def moveToThread(self, thread: object) -> None:
        self.moved_to_thread = thread

    def run(self) -> None:
        self.ran = True

    def deleteLater(self) -> None:
        self.deleted = True


class CountCheckingScraper:
    def __init__(self, online_count: int | None | Exception) -> None:
        self.online_count = online_count
        self.checked_usernames: list[str] = []

    def fetch_loved_track_count(self, username: str) -> int | None:
        self.checked_usernames.append(username)
        if isinstance(self.online_count, Exception):
            raise self.online_count
        return self.online_count


class FakeThread:
    def __init__(self, parent: object) -> None:
        self.parent = parent
        self.started = FakeSignal()
        self.finished = FakeSignal()
        self.started_flag = False
        self.quit_called = False
        self.deleted = False

    def start(self) -> None:
        self.started_flag = True

    def quit(self) -> None:
        self.quit_called = True

    def deleteLater(self) -> None:
        self.deleted = True


class FakeArtistImageWorker:
    def __init__(self, artist: str, client: object) -> None:
        self.artist = artist
        self.client = client
        self.artist_image_loaded = FakeSignal()
        self.error = FakeSignal()
        self.finished = FakeSignal()
        self.moved_to_thread = None
        self.deleted = False
        self.ran = False

    def moveToThread(self, thread: object) -> None:
        self.moved_to_thread = thread

    def run(self) -> None:
        self.ran = True

    def deleteLater(self) -> None:
        self.deleted = True


def test_controller_start_connects_fetch_signal_and_checks_dependencies(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(
        window,
        dependency_checker=lambda: DependencyCheckResult(installed=("ffmpeg",), missing=()),
    )

    controller.start()

    assert controller.check_dependencies().is_ok
    assert window.dependency_label.text() == "🟢 Dependencies installed: ffmpeg"


def test_controller_reports_missing_dependencies(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(
        window,
        dependency_checker=lambda: DependencyCheckResult(installed=(), missing=("yt-dlp",)),
    )

    result = controller.check_dependencies()

    assert not result.is_ok
    assert window.dependency_label.text() == "🔴 Missing dependencies: yt-dlp"
    assert "🔴 Missing dependencies: yt-dlp" in window.feedback_log.toPlainText()


def test_controller_retranslates_dependency_label_on_language_change(qapp) -> None:
    call_count = 0

    def counting_checker() -> DependencyCheckResult:
        nonlocal call_count
        call_count += 1
        return DependencyCheckResult(installed=("ffmpeg",), missing=())

    window = MainWindow()
    ApplicationController(window, dependency_checker=counting_checker).start()
    calls_after_start = call_count

    window.language_changed.emit()

    assert call_count == calls_after_start + 1


def test_controller_start_connects_file_cache_menu_action(qapp, tmp_path, monkeypatch) -> None:
    opened_paths: list[str] = []

    def fake_open_url(url) -> bool:
        opened_paths.append(url.toLocalFile())
        return True

    monkeypatch.setattr(controller_module.QDesktopServices, "openUrl", fake_open_url)
    window = MainWindow()
    repository = JsonTrackRepository(data_dir=tmp_path)
    controller = ApplicationController(
        window,
        repository=repository,
        dependency_checker=lambda: DependencyCheckResult(installed=(), missing=()),
    )

    controller.start()
    window.file_cache_action.trigger()

    assert opened_paths == [str(repository.data_dir)]
    assert repository.data_dir.is_dir()
    assert "Opened data folder:" in window.feedback_log.toPlainText()


def _stuck_track_controller(tmp_path, tracks: list[Track]) -> tuple:
    """Return a controller whose queues are recorded instead of started."""

    window = MainWindow()
    window.set_username("user")
    repository = JsonTrackRepository(data_dir=tmp_path)
    # load_tracks re-queues a download whose file has vanished, so give them a real one.
    for track in tracks:
        if track.local_path:
            Path(track.local_path).touch()
    repository.save_tracks("user", tracks)
    repository.save_lookup_cache(tracks)
    controller = ApplicationController(
        window,
        repository=repository,
        dependency_checker=lambda: DependencyCheckResult(installed=(), missing=()),
    )
    started: dict[str, list] = {"lookup": [], "download": []}
    controller.resolve_youtube_urls = lambda *a, **k: started["lookup"].append((a, k))
    controller.download_tracks = lambda *a, **k: started["download"].append((a, k))
    return controller, window, repository, started


def test_start_rechecks_not_found_tracks(qapp, tmp_path) -> None:
    tracks = [
        Track(artist="Missing", title="Track", status=TrackStatus.NOT_FOUND, retry_count=3),
        Track(
            artist="Done",
            title="Track",
            youtube_url="https://youtube.example/watch?v=ok",
            local_path=str(tmp_path / "Done - Track.webm"),
            status=TrackStatus.DOWNLOADED,
        ),
    ]
    controller, _window, repository, started = _stuck_track_controller(tmp_path, tracks)

    controller.start()

    stored = {track.artist: track for track in repository.load_tracks("user")}
    assert stored["Missing"].status is TrackStatus.FETCHED
    assert stored["Missing"].retry_count == 0
    assert stored["Done"].status is TrackStatus.DOWNLOADED
    assert repository.load_lookup_cache().get("Missing\x1fTrack") is None
    assert started["lookup"] == [(("user",), {})]
    assert started["download"] == []


def test_start_retries_failed_downloads_without_a_lookup_pass(qapp, tmp_path) -> None:
    tracks = [
        Track(
            artist="Failed",
            title="Track",
            youtube_url="https://youtube.example/watch?v=ok",
            status=TrackStatus.FAILED,
        )
    ]
    controller, _window, repository, started = _stuck_track_controller(tmp_path, tracks)

    controller.start()

    # A failed download already has its URL, so it goes straight back to the download queue.
    assert started["download"] == [(("user",), {})]
    assert started["lookup"] == []
    assert repository.load_tracks("user")[0].status is TrackStatus.QUEUED


def test_start_retries_lookup_failures_through_lookup(qapp, tmp_path) -> None:
    tracks = [
        Track(
            artist="Failed lookup",
            title="Track",
            status=TrackStatus.LOOKUP_FAILED,
            error="network unavailable",
        )
    ]
    controller, _window, repository, started = _stuck_track_controller(tmp_path, tracks)

    controller.start()

    assert started["lookup"] == [(("user",), {})]
    assert started["download"] == []
    assert repository.load_tracks("user")[0].status is TrackStatus.FETCHED


def test_start_leaves_a_healthy_library_alone(qapp, tmp_path) -> None:
    tracks = [
        Track(
            artist="Done",
            title="Track",
            youtube_url="https://youtube.example/watch?v=ok",
            local_path=str(tmp_path / "Done - Track.webm"),
            status=TrackStatus.DOWNLOADED,
        )
    ]
    controller, window, _repository, started = _stuck_track_controller(tmp_path, tracks)

    controller.start()

    assert started["lookup"] == []
    assert started["download"] == []
    assert "Re-checking" not in window.feedback_log.toPlainText()


def test_start_skips_the_recheck_without_a_username(qapp, tmp_path) -> None:
    tracks = [Track(artist="Missing", title="Track", status=TrackStatus.NOT_FOUND)]
    controller, window, _repository, started = _stuck_track_controller(tmp_path, tracks)
    window.set_username("")

    controller.start()

    assert started["lookup"] == []
    assert started["download"] == []


def test_controller_reports_file_cache_open_failure(qapp, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        controller_module.QDesktopServices,
        "openUrl",
        lambda _url: False,
    )
    window = MainWindow()
    repository = JsonTrackRepository(data_dir=tmp_path)
    controller = ApplicationController(window, repository=repository)

    controller.open_file_cache()

    assert repository.data_dir.is_dir()
    assert "Could not open data folder:" in window.feedback_log.toPlainText()


def test_controller_initializes_scrobbling_with_bundled_credentials(qapp, tmp_path) -> None:
    window = MainWindow()
    controller = ApplicationController(
        window,
        repository=JsonTrackRepository(data_dir=tmp_path),
    )

    controller._init_scrobbling()

    assert controller._scrobbling_service is not None
    assert controller._scrobbling_service.has_api_credentials


def test_controller_loads_scrobbling_enabled_from_settings(
    qapp, tmp_path, monkeypatch
) -> None:
    from my_lastfm_player import settings as settings_module

    monkeypatch.setattr(
        settings_module.AppSettings,
        "scrobbling_enabled",
        lambda self, default_enabled=True: False,
    )
    window = MainWindow()
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_credentials({"scrobbling_enabled": True})
    controller = ApplicationController(window, repository=repository)

    controller._init_scrobbling()

    assert controller._scrobbling_service is not None
    assert not controller._scrobbling_service.scrobbling_enabled


def test_controller_skips_scrobbling_when_credentials_are_empty(
    qapp, tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(
        controller_module,
        "lastfm_api_credentials",
        lambda: LastFmApiCredentials(api_key="", api_secret=""),
    )
    window = MainWindow()
    controller = ApplicationController(
        window,
        repository=JsonTrackRepository(data_dir=tmp_path),
    )

    controller._init_scrobbling()

    assert controller._scrobbling_service is None


def test_controller_rejects_empty_username(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(window)

    controller.fetch_loved_tracks()

    assert "Enter a Last.fm username" in window.feedback_log.toPlainText()


def test_controller_loads_cached_tracks_without_fetching(qapp, tmp_path) -> None:
    window = MainWindow()
    window.username_input.setText("example")
    cached_track = Track(
        artist="Artist",
        title="Title",
        youtube_url="https://youtube.example/watch?v=cached",
        status=TrackStatus.QUEUED,
    )
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_tracks("example", [cached_track])
    fetch_calls: list[str] = []

    def fail_fetch_factory(*_args):
        fetch_calls.append("fetch")
        raise AssertionError("web fetch should not start when cached tracks exist")

    controller = ApplicationController(
        window,
        repository=repository,
        scraper=CountCheckingScraper(1),  # type: ignore[arg-type]
        fetch_worker_factory=fail_fetch_factory,  # type: ignore[arg-type]
    )
    workers: list[object] = []
    controller._run_worker = workers.append  # type: ignore[method-assign]

    controller.fetch_loved_tracks()

    assert fetch_calls == []
    assert window.tracks() == [cached_track]
    assert len(workers) == 1
    assert "Loaded 1 cached tracks for example" in window.feedback_log.toPlainText()
    assert "cached track count matches" in window.feedback_log.toPlainText()


def test_controller_fetches_fresh_tracks_when_online_count_differs(qapp, tmp_path) -> None:
    window = MainWindow()
    window.username_input.setText("example")
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_tracks("example", [Track(artist="Cached", title="Track")])
    scraper = CountCheckingScraper(2)
    controller = ApplicationController(
        window,
        repository=repository,
        scraper=scraper,  # type: ignore[arg-type]
    )
    workers: list[object] = []
    controller._run_worker = workers.append  # type: ignore[method-assign]

    controller.fetch_loved_tracks()

    assert scraper.checked_usernames == ["example"]
    assert len(workers) == 1
    assert controller._active_fetch_worker is workers[0]
    assert "cache has 1" in window.feedback_log.toPlainText()
    assert "fetching fresh data" in window.feedback_log.toPlainText()


def test_controller_fetches_fresh_tracks_when_online_count_is_unknown(qapp, tmp_path) -> None:
    window = MainWindow()
    window.username_input.setText("example")
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_tracks("example", [Track(artist="Cached", title="Track")])
    controller = ApplicationController(
        window,
        repository=repository,
        scraper=CountCheckingScraper(None),  # type: ignore[arg-type]
    )
    workers: list[object] = []
    controller._run_worker = workers.append  # type: ignore[method-assign]

    controller.fetch_loved_tracks()

    assert len(workers) == 1
    assert "Could not read Last.fm loved-track count" in window.feedback_log.toPlainText()


def test_controller_uses_cache_when_online_count_check_fails(qapp, tmp_path) -> None:
    window = MainWindow()
    window.username_input.setText("example")
    cached_track = Track(artist="Cached", title="Track")
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_tracks("example", [cached_track])
    controller = ApplicationController(
        window,
        repository=repository,
        scraper=CountCheckingScraper(controller_module.LastFmError("network down")),  # type: ignore[arg-type]
    )
    workers: list[object] = []
    controller._run_worker = workers.append  # type: ignore[method-assign]

    controller.fetch_loved_tracks()

    assert len(workers) == 1
    assert window.tracks() == [cached_track]
    assert "using 1 cached tracks" in window.feedback_log.toPlainText()


def test_controller_aborts_fresh_fetch_when_lastfm_is_unreachable(qapp, tmp_path) -> None:
    window = MainWindow()
    window.username_input.setText("example")
    repository = JsonTrackRepository(data_dir=tmp_path)
    # No tracks saved — no cache, so pre-flight runs.
    scraper = CountCheckingScraper(controller_module.LastFmError("user not found"))
    controller = ApplicationController(
        window,
        repository=repository,
        scraper=scraper,  # type: ignore[arg-type]
    )
    workers: list[object] = []
    controller._run_worker = workers.append  # type: ignore[method-assign]

    controller.fetch_loved_tracks()

    assert len(workers) == 0
    assert scraper.checked_usernames == ["example"]
    assert "Could not reach Last.fm for example" in window.feedback_log.toPlainText()


def test_controller_shows_expected_count_before_fresh_fetch(qapp, tmp_path) -> None:
    window = MainWindow()
    window.username_input.setText("example")
    repository = JsonTrackRepository(data_dir=tmp_path)
    # No cache — pre-flight returns a known count.
    scraper = CountCheckingScraper(523)
    controller = ApplicationController(
        window,
        repository=repository,
        scraper=scraper,  # type: ignore[arg-type]
    )
    workers: list[object] = []
    controller._run_worker = workers.append  # type: ignore[method-assign]

    controller.fetch_loved_tracks()

    assert len(workers) == 1
    assert scraper.checked_usernames == ["example"]
    assert "523 tracks expected" in window.feedback_log.toPlainText()
    assert workers[0].expected_count == 523  # type: ignore[union-attr]


def test_controller_skips_preflight_when_cache_count_already_checked(qapp, tmp_path) -> None:
    window = MainWindow()
    window.username_input.setText("example")
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_tracks("example", [Track(artist="Cached", title="Track")])
    scraper = CountCheckingScraper(2)  # count mismatch triggers fresh fetch
    controller = ApplicationController(
        window,
        repository=repository,
        scraper=scraper,  # type: ignore[arg-type]
    )
    workers: list[object] = []
    controller._run_worker = workers.append  # type: ignore[method-assign]

    controller.fetch_loved_tracks()

    # fetch_loved_track_count called once only (from cache check, not again in pre-flight)
    assert scraper.checked_usernames == ["example"]
    assert len(workers) == 1


def test_controller_rejects_empty_username_for_lookup(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(window)

    controller.resolve_youtube_urls()

    assert "Enter a Last.fm username before resolving tracks." in window.feedback_log.toPlainText()


def test_controller_rejects_empty_username_for_download(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(window)

    controller.download_tracks()

    assert (
        "Enter a Last.fm username before downloading tracks."
        in window.feedback_log.toPlainText()
    )


def test_controller_handles_resolved_tracks(qapp, tmp_path) -> None:
    window = MainWindow()
    window.set_username("example")
    controller = ApplicationController(window, repository=JsonTrackRepository(data_dir=tmp_path))

    controller._handle_tracks_resolved("example", [])

    assert window.track_model.rowCount() == 0
    assert "Resolved YouTube URLs for 0/0 tracks; 0 were not found." in (
        window.feedback_log.toPlainText()
    )
    assert "No queued tracks are ready for download." in window.feedback_log.toPlainText()


def test_controller_starts_lookup_after_successful_fetch(qapp, tmp_path) -> None:
    window = MainWindow()
    window.set_username("example")
    controller = ApplicationController(window, repository=JsonTrackRepository(data_dir=tmp_path))
    calls: list[tuple[str, int]] = []

    def fake_start_lookup(username: str, track_count: int) -> None:
        calls.append((username, track_count))

    controller._start_automatic_lookup = fake_start_lookup  # type: ignore[method-assign]

    controller._handle_tracks_loaded("example", [Track(artist="Artist", title="Title")])

    assert calls == [("example", 1)]
    assert window.track_model.rowCount() == 1
    assert not window.fetch_pause_button.isEnabled()
    assert not window.fetch_stop_button.isEnabled()


def test_controller_updates_table_during_paginated_fetch(qapp, tmp_path) -> None:
    window = MainWindow()
    window.set_username("example")
    controller = ApplicationController(window, repository=JsonTrackRepository(data_dir=tmp_path))
    lookup_calls: list[tuple[str, int]] = []
    controller._ensure_automatic_lookup = lambda username, count: lookup_calls.append(  # type: ignore[method-assign]
        (username, count)
    )

    controller._handle_tracks_updated(
        "example",
        [Track(artist="Artist", title="Title")],
    )

    assert window.track_model.rowCount() == 1
    assert "Fetched 1 tracks for example" in window.statusBar().currentMessage()
    assert lookup_calls == [("example", 1)]


class FakeFetchWorker:
    def __init__(self) -> None:
        self.events: list[str] = []

    def pause_fetch(self) -> None:
        self.events.append("pause")

    def resume_fetch(self) -> None:
        self.events.append("resume")

    def stop_fetch(self) -> None:
        self.events.append("stop")


def test_controller_pauses_resumes_and_stops_active_fetch(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(window)
    worker = FakeFetchWorker()
    controller._active_fetch_worker = worker  # type: ignore[assignment]
    window.set_fetch_control_state(active=True, paused=False)

    controller.toggle_fetch_pause()
    controller.toggle_fetch_pause()
    controller.stop_fetch()

    assert worker.events == ["pause", "resume", "stop"]
    assert not window.fetch_pause_button.isEnabled()
    assert not window.fetch_stop_button.isEnabled()


def test_controller_ignores_fetch_controls_without_active_worker(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(window)

    controller.toggle_fetch_pause()
    controller.stop_fetch()

    assert window.feedback_log.toPlainText() == ""


def test_controller_handles_stopped_fetch_without_starting_lookup(qapp) -> None:
    window = MainWindow()
    window.set_username("example")
    controller = ApplicationController(window)
    calls: list[tuple[str, int]] = []
    controller._start_automatic_lookup = lambda username, count: calls.append(  # type: ignore[method-assign]
        (username, count)
    )

    controller._handle_fetch_stopped("example", [Track(artist="Artist", title="Title")])

    assert calls == []
    assert window.track_model.rowCount() == 1
    assert "Stopped fetch for example after 1 tracks." in window.feedback_log.toPlainText()


def test_controller_updates_single_track_during_lookup_or_download(qapp) -> None:
    window = MainWindow()
    window.set_username("example")
    track = Track(artist="Artist", title="Title")
    window.set_tracks([track])
    controller = ApplicationController(window)

    controller._handle_track_updated(
        "example",
        track.with_status(TrackStatus.SEARCHING),
    )

    assert window.track_model.track_at(0).status == TrackStatus.SEARCHING


def test_controller_starts_download_from_first_resolved_track_update(qapp, tmp_path) -> None:
    window = MainWindow()
    window.username_input.setText("user")
    repository = JsonTrackRepository(data_dir=tmp_path)
    track = Track(artist="Artist", title="Title")
    repository.save_tracks("user", [track])
    window.set_tracks([track])
    controller = ApplicationController(window, repository=repository)
    auto_calls: list[str] = []
    controller._start_automatic_download = lambda username: auto_calls.append(username)  # type: ignore[method-assign]
    resolved = track.with_status(TrackStatus.QUEUED)
    resolved = replace(resolved, youtube_url="https://youtu.be/example")

    controller._handle_track_updated("user", resolved)

    assert auto_calls == ["user"]


def test_controller_does_not_start_parallel_bulk_download_when_worker_active(
    qapp, tmp_path
) -> None:
    window = MainWindow()
    repository = JsonTrackRepository(data_dir=tmp_path)
    track = Track(
        artist="Artist",
        title="Title",
        youtube_url="https://youtu.be/example",
        status=TrackStatus.QUEUED,
    )
    repository.save_tracks("user", [track])
    controller = ApplicationController(window, repository=repository)
    controller._download_worker_active = True
    auto_calls: list[str] = []
    controller._start_automatic_download = lambda username: auto_calls.append(username)  # type: ignore[method-assign]

    controller._handle_track_updated("user", track)

    assert auto_calls == []


def test_controller_starts_download_after_successful_lookup(qapp, tmp_path) -> None:
    window = MainWindow()
    window.set_username("example")
    repository = JsonTrackRepository(data_dir=tmp_path)
    track = Track(
        artist="Artist",
        title="Title",
        youtube_url="https://youtu.be/example",
        status=TrackStatus.QUEUED,
    )
    repository.save_tracks("example", [track])
    controller = ApplicationController(window, repository=repository)
    calls: list[str] = []

    def fake_start_download(username: str) -> None:
        calls.append(username)

    controller._start_automatic_download = fake_start_download  # type: ignore[method-assign]

    controller._handle_tracks_resolved("example", [track])

    assert calls == ["example"]


def test_controller_stop_downloads_stops_only_current_operation_and_clears_ui(qapp) -> None:
    window = MainWindow()

    class FakeManager:
        pass

    controller = ApplicationController(window, download_manager=FakeManager())  # type: ignore[arg-type]
    window.set_download_active(True)
    controller._download_worker_active = True

    controller.stop_downloads()

    assert not controller._download_worker_active
    assert controller._download_stop_requested
    assert not window._download_active


def test_controller_starts_priority_download_after_lookup_for_pending_play(qapp, tmp_path) -> None:
    window = MainWindow()
    window.set_username("user")
    repository = JsonTrackRepository(data_dir=tmp_path)
    track = Track(
        artist="Artist",
        title="Title",
        youtube_url="https://youtu.be/example",
        status=TrackStatus.QUEUED,
    )
    repository.save_tracks("user", [track])
    controller = ApplicationController(window, repository=repository)
    calls: list[tuple[str, str]] = []
    controller._pending_play_cache_key = track.cache_key
    controller._start_priority_download = lambda username, cache_key: calls.append(  # type: ignore[method-assign]
        (username, cache_key)
    )

    controller._handle_tracks_resolved("user", [track])

    assert calls == [("user", track.cache_key)]


def test_controller_reenables_workflow_after_last_worker(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(window)
    controller._running_worker_count = 2
    window.set_workflow_enabled(False)

    controller._complete_worker_run()

    assert not window.fetch_button.isEnabled()

    controller._complete_worker_run()

    assert window.fetch_button.isEnabled()


def test_controller_run_worker_tracks_thread_lifecycle(qapp, monkeypatch) -> None:
    from my_lastfm_player import controller as controller_module

    window = MainWindow()
    controller = ApplicationController(window)
    worker = GenericWorker()
    created_threads: list[FakeThread] = []

    def fake_thread_factory(parent: object) -> FakeThread:
        thread = FakeThread(parent)
        created_threads.append(thread)
        return thread

    monkeypatch.setattr(controller_module, "QThread", fake_thread_factory)

    controller._run_worker(worker)  # type: ignore[arg-type]
    thread = created_threads[0]

    assert worker.moved_to_thread is thread
    assert thread.started_flag
    assert controller._active_threads == [thread]
    assert controller._active_workers == [worker]
    assert not window.fetch_button.isEnabled()
    assert worker.run in thread.started.callbacks
    assert worker.deleteLater in worker.finished.callbacks
    assert thread.quit in worker.finished.callbacks
    assert thread.deleteLater in thread.finished.callbacks


def test_controller_run_worker_connects_typed_worker_signals(qapp, monkeypatch) -> None:
    from my_lastfm_player import controller as controller_module

    class FakeFetchWorker(GenericWorker):
        def __init__(self) -> None:
            super().__init__()
            self.tracks_updated = FakeSignal()
            self.tracks_loaded = FakeSignal()
            self.fetch_stopped = FakeSignal()

    class FakeLookupWorker(GenericWorker):
        def __init__(self) -> None:
            super().__init__()
            self.track_updated = FakeSignal()
            self.tracks_resolved = FakeSignal()

    class FakeDownloadWorker(GenericWorker):
        def __init__(self) -> None:
            super().__init__()
            self.track_updated = FakeSignal()
            self.tracks_downloaded = FakeSignal()

    created_threads: list[FakeThread] = []

    def fake_thread_factory(parent: object) -> FakeThread:
        thread = FakeThread(parent)
        created_threads.append(thread)
        return thread

    monkeypatch.setattr(controller_module, "QThread", fake_thread_factory)
    monkeypatch.setattr(controller_module, "FetchLovedTracksWorker", FakeFetchWorker)
    monkeypatch.setattr(controller_module, "LookupTracksWorker", FakeLookupWorker)
    monkeypatch.setattr(controller_module, "DownloadTracksWorker", FakeDownloadWorker)
    window = MainWindow()
    controller = ApplicationController(window)

    fetch_worker = FakeFetchWorker()
    lookup_worker = FakeLookupWorker()
    download_worker = FakeDownloadWorker()

    controller._run_worker(fetch_worker)  # type: ignore[arg-type]
    controller._run_worker(lookup_worker)  # type: ignore[arg-type]
    controller._run_worker(download_worker)  # type: ignore[arg-type]

    assert len(fetch_worker.tracks_updated.callbacks) == 1
    assert len(fetch_worker.tracks_loaded.callbacks) == 1
    assert len(fetch_worker.fetch_stopped.callbacks) == 1
    assert len(lookup_worker.track_updated.callbacks) == 1
    assert len(lookup_worker.tracks_resolved.callbacks) == 1
    assert len(download_worker.track_updated.callbacks) == 1
    assert len(download_worker.tracks_downloaded.callbacks) == 1


def test_controller_run_artist_image_worker_tracks_lifecycle(qapp, monkeypatch) -> None:
    created_threads: list[FakeThread] = []

    def fake_thread_factory(parent: object) -> FakeThread:
        thread = FakeThread(parent)
        created_threads.append(thread)
        return thread

    monkeypatch.setattr(controller_module, "QThread", fake_thread_factory)
    window = MainWindow()
    controller = ApplicationController(window)
    worker = FakeArtistImageWorker("Artist", object())

    controller._run_artist_image_worker(worker)  # type: ignore[arg-type]
    thread = created_threads[0]

    assert worker.moved_to_thread is thread
    assert thread.started_flag
    assert controller._active_threads == [thread]
    assert controller._active_artist_image_workers == [worker]
    assert worker.run in thread.started.callbacks
    assert controller._handle_artist_image_loaded in worker.artist_image_loaded.callbacks
    assert controller._handle_artist_image_error in worker.error.callbacks
    assert thread.quit in worker.finished.callbacks
    assert worker.deleteLater in worker.finished.callbacks


def test_controller_play_on_unresolved_track_starts_priority_lookup(qapp, tmp_path) -> None:
    window = MainWindow()
    window.username_input.setText("user")
    track = Track(artist="Artist", title="Title", status=TrackStatus.FETCHED)
    window.set_tracks([track])
    window.track_table.selectRow(0)
    controller = ApplicationController(window, repository=JsonTrackRepository(data_dir=tmp_path))
    lookup_calls: list[tuple[str | None, str | None, int | None]] = []

    def fake_lookup(
        username: str | None = None,
        priority_cache_key: str | None = None,
        max_tracks: int | None = None,
    ) -> None:
        lookup_calls.append((username, priority_cache_key, max_tracks))

    controller.resolve_youtube_urls = fake_lookup  # type: ignore[method-assign]

    controller.play_selected_track()

    assert lookup_calls == [("user", track.cache_key, 1)]
    assert "Preparing Artist - Title for playback." in window.feedback_log.toPlainText()


def test_controller_play_on_resolved_track_starts_priority_download(qapp, tmp_path) -> None:
    window = MainWindow()
    window.username_input.setText("user")
    track = Track(
        artist="Artist",
        title="Title",
        youtube_url="https://youtu.be/example",
        status=TrackStatus.QUEUED,
    )
    window.set_tracks([track])
    window.track_table.selectRow(0)
    controller = ApplicationController(window, repository=JsonTrackRepository(data_dir=tmp_path))
    download_calls: list[tuple[str | None, str | None, int | None]] = []

    def fake_download(
        username: str | None = None,
        priority_cache_key: str | None = None,
        max_downloads: int | None = None,
    ) -> None:
        download_calls.append((username, priority_cache_key, max_downloads))

    controller.download_tracks = fake_download  # type: ignore[method-assign]

    controller.play_selected_track()

    assert download_calls == [("user", track.cache_key, 1)]
    assert "Starting priority download for selected track." in window.feedback_log.toPlainText()


class FakePlaybackService:
    def __init__(self) -> None:
        self.current_track: Track | None = None
        self.events: list[str] = []
        self.position = 0
        self.duration = 0
        self.position_callback = None
        self.duration_callback = None
        self.finished_callback = None
        self.fail_pause = False
        self.fail_seek = False
        self._paused = False
        self.volume_percent: int | None = None
        self.muted: bool | None = None

    def play(self, track: Track) -> Track:
        self.events.append(f"play:{track.title}")
        self.current_track = track
        self._paused = False
        return track

    def is_paused(self) -> bool:
        return self._paused

    def pause(self) -> None:
        if self.fail_pause:
            from my_lastfm_player.playback import PlaybackError

            raise PlaybackError("pause failed")
        self.events.append("pause")
        self._paused = True

    def resume(self) -> None:
        self.events.append("resume")
        self._paused = False

    def stop(self) -> Track | None:
        self.events.append("stop")
        stopped_track = self.current_track
        self.current_track = None
        return stopped_track

    def finish_current(self) -> Track | None:
        stopped_track = self.current_track
        self.current_track = None
        return stopped_track

    def seek(self, position_ms: int) -> None:
        if self.fail_seek:
            from my_lastfm_player.playback import PlaybackError

            raise PlaybackError("seek failed")
        self.events.append(f"seek:{position_ms}")
        self.position = position_ms

    def position_ms(self) -> int:
        return self.position

    def duration_ms(self) -> int:
        return self.duration

    def on_position_changed(self, callback) -> None:
        self.position_callback = callback

    def on_duration_changed(self, callback) -> None:
        self.duration_callback = callback

    def on_finished(self, callback) -> None:
        self.finished_callback = callback

    def set_volume(self, volume_percent: int) -> None:
        self.volume_percent = volume_percent

    def set_muted(self, muted: bool) -> None:
        self.muted = muted


def test_controller_plays_selected_downloaded_track(qapp, tmp_path) -> None:
    window = MainWindow()
    window.username_input.setText("user")
    track = downloaded_track(tmp_path)
    window.set_tracks([track])
    window.track_table.selectRow(0)
    playback = FakePlaybackService()
    playback.duration = 180_000
    controller = ApplicationController(
        window,
        repository=JsonTrackRepository(data_dir=tmp_path),
        playback_service=playback,  # type: ignore[arg-type]
    )

    controller.play_selected_track()

    assert playback.events == ["play:Title"]
    assert window.track_model.track_at(0).status == TrackStatus.DOWNLOADED
    assert window.track_model.playing_cache_key() == track.cache_key
    assert window.playback_slider.maximum() == 180_000
    assert "Playing Artist - Title." in window.feedback_log.toPlainText()


def test_controller_fetches_artist_image_when_playback_starts(qapp, tmp_path) -> None:
    window = MainWindow()
    track = downloaded_track(tmp_path)
    window.set_tracks([track])
    window.track_table.selectRow(0)
    playback = FakePlaybackService()
    controller = ApplicationController(
        window,
        playback_service=playback,  # type: ignore[arg-type]
        artist_info_client=object(),  # type: ignore[arg-type]
        artist_image_worker_factory=FakeArtistImageWorker,  # type: ignore[arg-type]
    )
    workers: list[FakeArtistImageWorker] = []
    controller._run_artist_image_worker = workers.append  # type: ignore[method-assign]

    controller.play_selected_track()

    assert len(workers) == 1
    assert workers[0].artist == "Artist"


def test_controller_shows_cached_artist_image_and_opens_artist_page(
    qapp,
    tmp_path,
    monkeypatch,
) -> None:
    opened_commands: list[tuple[str, list[str]]] = []

    def fake_start_detached(program: str, arguments: list[str]) -> tuple[bool, int]:
        opened_commands.append((program, arguments))
        return True, 1234

    monkeypatch.setattr(controller_module.QProcess, "startDetached", fake_start_detached)
    window = MainWindow()
    track = downloaded_track(tmp_path)
    window.set_tracks([track])
    window.track_table.selectRow(0)
    playback = FakePlaybackService()
    controller = ApplicationController(
        window,
        playback_service=playback,  # type: ignore[arg-type]
        artist_info_client=object(),  # type: ignore[arg-type]
        artist_image_worker_factory=FakeArtistImageWorker,  # type: ignore[arg-type]
    )
    artist_image = ArtistImage(
        artist="Artist",
        page_url="https://www.last.fm/music/Artist",
        image_url="https://last.fm/image.jpg",
        image_bytes=b"not-a-real-image",
    )
    controller._artist_image_cache["Artist"] = artist_image
    controller._run_artist_image_worker = lambda _worker: None  # type: ignore[method-assign]
    image_calls: list[tuple[bytes | None, str | None, str | None]] = []

    def capture_artist_image(
        image_bytes: bytes | None,
        page_url: str | None,
        artist_name: str | None = None,
    ) -> None:
        image_calls.append((image_bytes, page_url, artist_name))

    window.set_artist_image = capture_artist_image  # type: ignore[method-assign]

    controller.play_selected_track()
    controller.open_artist_page("https://www.last.fm/music/Artist")

    assert image_calls == [(artist_image.image_bytes, artist_image.page_url, "Artist")]
    assert opened_commands == [
        ("firefox", ["--private-window", "https://www.last.fm/music/Artist"])
    ]


def test_controller_shows_artist_image_only_for_the_current_track(qapp) -> None:
    window = MainWindow()
    playback = FakePlaybackService()
    playback.current_track = Track(artist="Current", title="Title")
    controller = ApplicationController(window, playback_service=playback)  # type: ignore[arg-type]
    shown: list[tuple[bytes | None, str | None, str | None]] = []
    window.set_artist_image = (  # type: ignore[method-assign]
        lambda image_bytes, page_url, artist_name=None: shown.append(
            (image_bytes, page_url, artist_name)
        )
    )

    stale = ArtistImage(
        artist="Previous",
        page_url="https://www.last.fm/music/Previous",
        image_bytes=b"stale",
    )
    current = ArtistImage(
        artist="Current",
        page_url="https://www.last.fm/music/Current",
        image_bytes=b"current",
    )
    controller._handle_artist_image_loaded(stale)
    controller._handle_artist_image_loaded(current)

    assert shown == [(b"current", "https://www.last.fm/music/Current", "Current")]
    assert controller._artist_image_cache["Previous"] is stale


def test_controller_handles_artist_image_edge_cases(qapp, monkeypatch) -> None:
    def fail_start_detached(_program: str, _arguments: list[str]) -> tuple[bool, int]:
        return False, -1

    monkeypatch.setattr(controller_module.QProcess, "startDetached", fail_start_detached)
    window = MainWindow()
    image_calls: list[tuple[bytes | None, str | None]] = []
    window.set_artist_image = (  # type: ignore[method-assign]
        lambda image, url, artist=None: image_calls.append((image, url))
    )
    controller = ApplicationController(window)

    controller.open_artist_page("https://www.last.fm/music/Artist")
    controller._handle_artist_image_loaded(object())
    controller._show_artist_image(None)
    worker = FakeArtistImageWorker("Artist", object())
    controller._active_artist_image_workers.append(worker)  # type: ignore[arg-type]
    controller._forget_artist_image_worker(worker)  # type: ignore[arg-type]

    feedback = window.feedback_log.toPlainText()
    assert "Could not open artist page:" in feedback
    assert image_calls == [(None, None)]
    assert controller._active_artist_image_workers == []


@dataclass(frozen=True)
class ContinuationCase:
    """One playback-continuation scenario for the parametrized tests below."""

    tracks: tuple[tuple[str, str], ...]
    selected_row: int
    expected_events: tuple[str, ...]
    expected_row: int
    sort_by_artist: bool = False
    filter_text: str = ""
    advance: str = "finished"
    expected_log: str = ""
    expected_candidates: tuple[tuple[int, int], ...] | None = None


def advance_playback(controller: ApplicationController, playback, advance: str) -> None:
    """Finish the current track or press Next, depending on ``advance``."""

    if advance == "finished":
        assert playback.finished_callback is not None
        playback.finished_callback()
        return
    controller.play_next_track()


def run_continuation_case(case: ContinuationCase, tmp_path, randomize: bool):
    """Play the selected track, advance once, and return the window and recorded picks."""

    window = MainWindow()
    window.username_input.setText("user")
    tracks = downloaded_tracks(tmp_path, case.tracks)
    window.set_tracks(tracks)
    if case.sort_by_artist:
        window.track_sort_model.sort(0, Qt.SortOrder.AscendingOrder)
    if case.filter_text:
        window.track_filter_input.setText(case.filter_text)
    window.select_track_row(case.selected_row)
    window.set_randomize_playback(randomize)
    playback = FakePlaybackService()
    controller = ApplicationController(
        window,
        repository=JsonTrackRepository(data_dir=tmp_path),
        playback_service=playback,  # type: ignore[arg-type]
    )
    offered_candidates: list[list[tuple[int, Track]]] = []
    if randomize:
        def choose(candidates: list[tuple[int, Track]]) -> tuple[int, Track]:
            offered_candidates.append(candidates)
            return candidates[-1]

        controller._random = SimpleNamespace(choice=choose)  # type: ignore[assignment]

    controller.play_selected_track()
    advance_playback(controller, playback, case.advance)

    assert list(playback.events) == list(case.expected_events)
    assert window.selected_track() == tracks[case.expected_row]
    assert window.track_model.playing_cache_key() == tracks[case.expected_row].cache_key
    if case.expected_log:
        assert case.expected_log in window.feedback_log.toPlainText()
    return tracks, offered_candidates


@pytest.mark.parametrize(
    "case",
    [
        pytest.param(
            ContinuationCase(
                tracks=(("Zed", "Last"), ("Alpha", "First"), ("Middle", "Second")),
                sort_by_artist=True,
                selected_row=1,
                expected_events=("play:First", "play:Second"),
                expected_row=2,
                expected_log="Continuing with next track: Middle - Second.",
            ),
            id="follows_sort_order",
        ),
        pytest.param(
            ContinuationCase(
                tracks=(("Zed", "Last"), ("Alpha", "First")),
                sort_by_artist=True,
                selected_row=0,
                expected_events=("play:Last", "play:First"),
                expected_row=1,
                expected_log="Continuing with next track: Alpha - First.",
            ),
            id="wraps_after_last_track",
        ),
        pytest.param(
            ContinuationCase(
                tracks=(("Alpha", "Keep One"), ("Beta", "Skip"), ("Gamma", "Keep Two")),
                sort_by_artist=True,
                filter_text="keep",
                selected_row=0,
                expected_events=("play:Keep One", "play:Keep Two"),
                expected_row=2,
                expected_log="Continuing with next track: Gamma - Keep Two.",
            ),
            id="skips_filtered_out_rows",
        ),
        pytest.param(
            ContinuationCase(
                tracks=(("Alpha", "Keep One"), ("Beta", "Skip"), ("Gamma", "Keep Two")),
                filter_text="keep",
                selected_row=0,
                advance="next",
                expected_events=("play:Keep One", "play:Keep Two"),
                expected_row=2,
                expected_log="Continuing with next track: Gamma - Keep Two.",
            ),
            id="next_button_skips_filtered_out_rows",
        ),
    ],
)
def test_controller_continues_playback_in_order(case: ContinuationCase, qapp, tmp_path) -> None:
    run_continuation_case(case, tmp_path, randomize=False)


@pytest.mark.parametrize(
    "case",
    [
        pytest.param(
            ContinuationCase(
                tracks=(("Artist", "One"), ("Artist", "Two"), ("Artist", "Three")),
                selected_row=0,
                expected_events=("play:One", "play:Three"),
                expected_row=2,
                expected_log="Continuing with random track: Artist - Three.",
                expected_candidates=((1, 1), (2, 2)),
            ),
            id="random_after_finished",
        ),
        pytest.param(
            ContinuationCase(
                tracks=(("Artist", "Keep One"), ("Artist", "Keep Two"), ("Other", "Skip")),
                filter_text="keep",
                selected_row=0,
                expected_events=("play:Keep One", "play:Keep Two"),
                expected_row=1,
                expected_candidates=((1, 1),),
            ),
            id="random_within_filtered_rows",
        ),
        pytest.param(
            ContinuationCase(
                tracks=(("Artist", "One"), ("Artist", "Two"), ("Artist", "Three")),
                selected_row=0,
                advance="next",
                expected_events=("play:One", "play:Three"),
                expected_row=2,
                expected_log="Continuing with random track: Artist - Three.",
                expected_candidates=((1, 1), (2, 2)),
            ),
            id="next_button_picks_random",
        ),
    ],
)
def test_controller_continues_playback_randomly(case: ContinuationCase, qapp, tmp_path) -> None:
    tracks, offered_candidates = run_continuation_case(case, tmp_path, randomize=True)

    assert case.expected_candidates is not None
    assert offered_candidates == [
        [(row, tracks[index]) for row, index in case.expected_candidates]
    ]


def test_controller_pause_and_stop_playback(qapp, tmp_path) -> None:
    window = MainWindow()
    track = downloaded_track(tmp_path)
    window.set_tracks([track])
    window.set_playing_track(track.cache_key)
    playback = FakePlaybackService()
    playback.current_track = track
    controller = ApplicationController(window, playback_service=playback)  # type: ignore[arg-type]

    controller.pause_playback()
    controller.stop_playback()

    assert playback.events == ["pause", "stop"]
    assert window.track_model.track_at(0).status == TrackStatus.DOWNLOADED
    assert window.track_model.playing_cache_key() is None
    assert window.playback_slider.maximum() == 0
    assert "Playback paused." in window.feedback_log.toPlainText()
    assert "Playback stopped." in window.feedback_log.toPlainText()


def test_controller_pause_toggles_to_resume(qapp, tmp_path) -> None:
    window = MainWindow()
    track = downloaded_track(tmp_path)
    playback = FakePlaybackService()
    playback.current_track = track
    controller = ApplicationController(window, playback_service=playback)  # type: ignore[arg-type]

    controller.pause_playback()
    assert playback.events == ["pause"]
    assert "Playback paused." in window.feedback_log.toPlainText()

    controller.pause_playback()
    assert playback.events == ["pause", "resume"]
    assert "Playback resumed." in window.feedback_log.toPlainText()


def test_playback_button_states(qapp, tmp_path) -> None:
    window = MainWindow()
    track = downloaded_track(tmp_path)
    window.set_tracks([track])
    playback = FakePlaybackService()
    controller = ApplicationController(window, playback_service=playback)  # type: ignore[arg-type]

    assert window.play_button.isEnabled()
    assert not window.pause_button.isEnabled()
    assert not window.stop_button.isEnabled()
    assert not window.next_button.isEnabled()

    controller._play_track(track)

    assert not window.play_button.isEnabled()
    assert window.pause_button.isEnabled()
    assert window.stop_button.isEnabled()
    assert window.next_button.isEnabled()

    controller.stop_playback()

    assert window.play_button.isEnabled()
    assert not window.pause_button.isEnabled()
    assert not window.stop_button.isEnabled()
    assert not window.next_button.isEnabled()


def test_controller_seeks_active_playback(qapp) -> None:
    window = MainWindow()
    playback = FakePlaybackService()
    playback.current_track = Track(artist="Artist", title="Title", status=TrackStatus.DOWNLOADED)
    playback.duration = 240_000
    controller = ApplicationController(window, playback_service=playback)  # type: ignore[arg-type]

    controller.seek_playback(75_000)

    assert playback.events == ["seek:75000"]
    assert window.playback_slider.value() == 75_000
    assert window.total_time_label.text() == "4:00"


def test_controller_reports_playback_errors(qapp, tmp_path) -> None:
    from my_lastfm_player.playback import PlaybackError

    window = MainWindow()
    playback = FakePlaybackService()
    audio_path = tmp_path / "track.mp3"
    audio_path.write_bytes(b"fake mp3")

    def fail_play(_track: Track) -> Track:
        raise PlaybackError("play failed")

    playback.play = fail_play  # type: ignore[method-assign]
    playback.fail_seek = True
    playback.fail_pause = True
    track = Track(
        artist="Artist",
        title="Title",
        status=TrackStatus.DOWNLOADED,
        local_path=str(audio_path),
    )
    controller = ApplicationController(window, playback_service=playback)  # type: ignore[arg-type]

    controller._play_track(track)
    controller.pause_playback()
    controller.seek_playback(10)

    assert "play failed" in window.feedback_log.toPlainText()
    assert "pause failed" in window.feedback_log.toPlainText()
    assert "seek failed" in window.feedback_log.toPlainText()


def test_controller_reports_no_selection_and_no_active_playback(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(window, playback_service=FakePlaybackService())  # type: ignore[arg-type]

    controller.play_selected_track()
    controller.stop_playback()
    controller.play_next_track()

    feedback = window.feedback_log.toPlainText()
    assert "Select a downloaded track before playing." in feedback
    assert feedback.count("No track is currently playing.") == 2


def test_controller_plays_first_downloaded_track_when_nothing_is_selected(
    qapp, tmp_path
) -> None:
    window = MainWindow()
    fetched_path = tmp_path / "one.mp3"
    fetched_path.write_bytes(b"fake mp3")
    downloaded_path = tmp_path / "two.mp3"
    downloaded_path.write_bytes(b"fake mp3")
    tracks = [
        Track(artist="Artist", title="Fetched", status=TrackStatus.FETCHED),
        Track(
            artist="Artist",
            title="First Downloaded",
            local_path=str(fetched_path),
            status=TrackStatus.DOWNLOADED,
        ),
        Track(
            artist="Artist",
            title="Second Downloaded",
            local_path=str(downloaded_path),
            status=TrackStatus.DOWNLOADED,
        ),
    ]
    window.set_tracks(tracks)
    playback = FakePlaybackService()
    controller = ApplicationController(
        window,
        repository=JsonTrackRepository(data_dir=tmp_path),
        playback_service=playback,  # type: ignore[arg-type]
    )

    controller.play_selected_track()

    assert playback.events == ["play:First Downloaded"]
    assert window.selected_track() == tracks[1]
    assert "Playing Artist - First Downloaded." in window.feedback_log.toPlainText()


def test_controller_plays_random_downloaded_track_when_nothing_is_selected_and_randomize_on(
    qapp, tmp_path
) -> None:
    window = MainWindow()
    audio_paths = [tmp_path / "one.mp3", tmp_path / "two.mp3"]
    for p in audio_paths:
        p.write_bytes(b"fake mp3")
    tracks = [
        Track(
            artist="Artist",
            title="One",
            local_path=str(audio_paths[0]),
            status=TrackStatus.DOWNLOADED,
        ),
        Track(
            artist="Artist",
            title="Two",
            local_path=str(audio_paths[1]),
            status=TrackStatus.DOWNLOADED,
        ),
    ]
    window.set_tracks(tracks)
    window.set_randomize_playback(True)
    playback = FakePlaybackService()
    controller = ApplicationController(
        window,
        repository=JsonTrackRepository(data_dir=tmp_path),
        playback_service=playback,  # type: ignore[arg-type]
    )
    random_candidates: list[list[tuple[int, Track]]] = []

    def choose(candidates: list[tuple[int, Track]]) -> tuple[int, Track]:
        random_candidates.append(candidates)
        return candidates[-1]

    controller._random = SimpleNamespace(choice=choose)  # type: ignore[assignment]

    controller.play_selected_track()

    assert playback.events == ["play:Two"]
    assert random_candidates == [[(0, tracks[0]), (1, tracks[1])]]
    assert window.selected_track() == tracks[1]
    assert "Playing Artist - Two." in window.feedback_log.toPlainText()


def test_controller_handles_invalid_worker_payloads(qapp) -> None:
    window = MainWindow()
    window.set_username("user")
    controller = ApplicationController(window)

    controller._handle_tracks_loaded("user", object())
    controller._handle_fetch_stopped("user", object())
    controller._handle_tracks_updated("user", object())
    controller._handle_track_updated("user", object())
    controller._handle_tracks_resolved("user", object())
    controller._handle_tracks_downloaded("user", object())
    controller._handle_worker_error("boom")

    feedback = window.feedback_log.toPlainText()
    assert "invalid track data" in feedback
    assert "invalid data" in feedback
    assert "invalid partial data" in feedback
    assert "invalid track update" in feedback
    assert "boom" in feedback
    assert window.progress_bar.format() == "Failed — %p%"


def test_controller_handles_downloaded_tracks_and_pending_play(qapp, tmp_path) -> None:
    window = MainWindow()
    window.set_username("user")
    repository = JsonTrackRepository(data_dir=tmp_path)
    dummy_file = tmp_path / "Artist - Title.mp3"
    dummy_file.write_bytes(b"")
    track = Track(
        artist="Artist",
        title="Title",
        status=TrackStatus.DOWNLOADED,
        local_path=str(dummy_file),
    )
    repository.save_tracks("user", [track])
    controller = ApplicationController(window, repository=repository)
    calls: list[str] = []
    controller._pending_play_cache_key = track.cache_key
    controller._play_prepared_track = lambda cache_key: calls.append(cache_key)  # type: ignore[method-assign]

    controller._handle_tracks_downloaded("user", [track])

    assert calls == [track.cache_key]
    assert "Download run for user finished: 1/1 tracks downloaded, 0 failed." in (
        window.feedback_log.toPlainText()
    )


def test_controller_starts_fetch_lookup_and_download_workers(
    qapp, tmp_path, monkeypatch
) -> None:
    from my_lastfm_player import settings as settings_module

    window = MainWindow()
    window.username_input.setText("user")
    controller = ApplicationController(
        window,
        repository=JsonTrackRepository(data_dir=tmp_path),
        scraper=CountCheckingScraper(42),  # type: ignore[arg-type]
    )
    workers: list[tuple[str, object]] = []
    monkeypatch.setattr(settings_module.AppSettings, "download_concurrency", lambda self: 4)

    def fake_run_worker(worker: object) -> None:
        workers.append((worker.__class__.__name__, worker))

    controller._run_worker = fake_run_worker  # type: ignore[method-assign]

    controller.fetch_loved_tracks()
    controller.resolve_youtube_urls(priority_cache_key="track", max_tracks=1)
    controller.download_tracks(priority_cache_key="track", max_downloads=1)

    assert [name for name, _worker in workers] == [
        "FetchLovedTracksWorker",
        "LookupTracksWorker",
        "DownloadTracksWorker",
    ]
    assert controller._active_fetch_worker is workers[0][1]
    assert not window.fetch_button.isEnabled()
    lookup_worker = workers[1][1]
    assert isinstance(lookup_worker, controller_module.LookupTracksWorker)
    assert lookup_worker.concurrency == 4
    download_worker = workers[2][1]
    assert isinstance(download_worker, controller_module.DownloadTracksWorker)
    assert download_worker.concurrency == 4


def test_controller_pipelines_lookup_during_paginated_fetch(qapp, tmp_path) -> None:
    window = MainWindow()
    window.username_input.setText("user")
    repository = JsonTrackRepository(data_dir=tmp_path)
    controller = ApplicationController(window, repository=repository)
    track = Track(artist="Artist", title="Title")
    lookup_calls: list[tuple[str | None, str | None, int | None]] = []

    def fake_resolve_youtube_urls(
        username: str | None = None,
        priority_cache_key: str | None = None,
        max_tracks: int | None = None,
    ) -> None:
        lookup_calls.append((username, priority_cache_key, max_tracks))

    controller.resolve_youtube_urls = fake_resolve_youtube_urls  # type: ignore[method-assign]
    controller._active_fetch_worker = object()  # type: ignore[assignment]

    controller._handle_tracks_updated("user", [track])
    controller._handle_tracks_updated("user", [track, Track(artist="Later", title="Track")])

    assert lookup_calls == [("user", None, None), ("user", None, None)]
    assert len(window.tracks()) == 2


def test_controller_playback_callbacks_update_timeline_once(qapp) -> None:
    window = MainWindow()
    playback = FakePlaybackService()
    playback.position = 30_000
    playback.duration = 120_000
    controller = ApplicationController(window, playback_service=playback)  # type: ignore[arg-type]

    assert controller.playback_service is playback
    assert controller.playback_service is playback
    assert playback.position_callback is not None
    assert playback.duration_callback is not None

    playback.position_callback(45_000)
    playback.duration = 180_000
    playback.duration_callback(180_000)

    assert window.playback_slider.value() == 30_000
    assert window.total_time_label.text() == "3:00"


def test_controller_creates_lazy_playback_service_and_connects_callbacks(
    qapp,
    monkeypatch,
) -> None:
    window = MainWindow()
    monkeypatch.setattr(controller_module, "PlaybackService", FakePlaybackService)
    controller = ApplicationController(window)

    playback = controller.playback_service

    assert isinstance(playback, FakePlaybackService)
    assert playback.position_callback is not None
    assert playback.duration_callback is not None
    assert playback.finished_callback is not None


def test_controller_helper_branches(qapp, tmp_path) -> None:
    window = MainWindow()
    downloaded = Track(artist="Artist", title="Downloaded", status=TrackStatus.DOWNLOADED)
    queued = Track(
        artist="Artist",
        title="Queued",
        status=TrackStatus.QUEUED,
        youtube_url="https://youtu.be/example",
    )
    window.username_input.setText("user")
    window.set_tracks([downloaded, queued])
    repository = JsonTrackRepository(data_dir=tmp_path)
    controller = ApplicationController(window, repository=repository)
    lookup_calls: list[tuple[str | None, str | None, int | None]] = []
    download_calls: list[tuple[str | None, str | None, int | None]] = []

    def fake_resolve_youtube_urls(
        username: str | None = None,
        priority_cache_key: str | None = None,
        max_tracks: int | None = None,
    ) -> None:
        lookup_calls.append((username, priority_cache_key, max_tracks))

    def fake_download_tracks(
        username: str | None = None,
        priority_cache_key: str | None = None,
        max_downloads: int | None = None,
    ) -> None:
        download_calls.append((username, priority_cache_key, max_downloads))

    controller.resolve_youtube_urls = fake_resolve_youtube_urls  # type: ignore[method-assign]
    controller.download_tracks = fake_download_tracks  # type: ignore[method-assign]

    controller._save_visible_tracks()
    controller._start_automatic_lookup("user", 2)
    controller._start_automatic_download("user")
    controller._start_priority_download("user", queued.cache_key)

    assert repository.load_tracks("user")
    assert lookup_calls == [("user", None, None)]
    assert download_calls == [("user", None, None), ("user", queued.cache_key, 1)]
    assert controller._has_download_candidates([queued])
    assert controller._track_has_youtube_url([queued], queued.cache_key)


def test_controller_prepare_and_play_prepared_edge_cases(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(window)
    track = Track(artist="Artist", title="Title", status=TrackStatus.FETCHED)
    window.set_tracks([track])

    controller._prepare_selected_track_for_playback(track)
    controller._play_prepared_track(track.cache_key)

    assert (
        "Enter a Last.fm username before preparing playback."
        in window.feedback_log.toPlainText()
    )
    assert controller._pending_play_cache_key is None


def test_controller_prepares_stale_downloaded_track_again(qapp, tmp_path) -> None:
    window = MainWindow()
    window.username_input.setText("user")
    track = Track(
        artist="Artist",
        title="Title",
        youtube_url="https://youtu.be/example",
        local_path=str(tmp_path / "missing.mp3"),
        status=TrackStatus.DOWNLOADED,
    )
    controller = ApplicationController(window)
    calls: list[tuple[str, str]] = []
    controller._start_priority_download = lambda username, cache_key: calls.append(  # type: ignore[method-assign]
        (username, cache_key)
    )

    controller._play_track(track)

    assert calls == [("user", track.cache_key)]
    assert controller._pending_play_cache_key == track.cache_key


def test_controller_scrobbles_at_33_percent(qapp, tmp_path) -> None:
    window = MainWindow()
    track = downloaded_track(tmp_path)
    window.set_tracks([track])
    playback = FakePlaybackService()
    playback.duration = 200_000
    controller, scrobbles = scrobbling_controller(window, playback)

    controller._play_track(track)
    controller._maybe_scrobble(65_999, 200_000)  # just below 33%
    assert scrobbles == []

    controller._maybe_scrobble(66_000, 200_000)  # exactly 33%
    assert len(scrobbles) == 1
    assert scrobbles[0]["artist"] == "Artist"
    assert scrobbles[0]["title"] == "Title"

    controller._maybe_scrobble(100_000, 200_000)  # only submitted once
    assert len(scrobbles) == 1


def test_controller_scrobble_resets_on_seek(qapp, tmp_path) -> None:
    window = MainWindow()
    track = downloaded_track(tmp_path)
    window.set_tracks([track])
    playback = FakePlaybackService()
    playback.duration = 200_000
    controller, scrobbles = scrobbling_controller(window, playback)

    controller._play_track(track)
    # Seek to 50% — 33% threshold now requires reaching 50%+33%=83%
    controller.seek_playback(100_000)
    assert not controller._scrobble_submitted
    assert controller._scrobble_seek_start_ms == 100_000

    controller._maybe_scrobble(165_999, 200_000)  # 65_999 ms elapsed < 66_000 threshold
    assert scrobbles == []

    controller._maybe_scrobble(166_000, 200_000)  # exactly 33% from seek point
    assert len(scrobbles) == 1


def test_controller_scrobble_resets_on_new_track(qapp, tmp_path) -> None:
    window = MainWindow()
    track = downloaded_track(tmp_path)
    window.set_tracks([track])
    playback = FakePlaybackService()
    playback.duration = 100_000

    controller, scrobbles = scrobbling_controller(window, playback)

    controller._play_track(track)
    controller._maybe_scrobble(33_000, 100_000)
    assert len(scrobbles) == 1

    controller._play_track(track)  # restart same track
    assert not controller._scrobble_submitted

    controller._maybe_scrobble(33_000, 100_000)
    assert len(scrobbles) == 2


def test_controller_forgets_threads_and_workers(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(window)
    thread = object()
    worker = GenericWorker()
    controller._active_threads.append(thread)  # type: ignore[arg-type]
    controller._active_workers.append(worker)  # type: ignore[arg-type]
    controller._active_fetch_worker = worker  # type: ignore[assignment]
    controller._fetch_paused = True

    controller._forget_thread(thread)  # type: ignore[arg-type]
    controller._forget_worker(worker)  # type: ignore[arg-type]

    assert controller._active_threads == []
    assert controller._active_workers == []
    assert controller._active_fetch_worker is None
    assert not controller._fetch_paused


def test_controller_forget_thread_and_worker_when_not_registered(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(window)
    unregistered_thread = object()
    unregistered_worker = GenericWorker()

    controller._forget_thread(unregistered_thread)  # type: ignore[arg-type]
    controller._forget_worker(unregistered_worker)  # type: ignore[arg-type]

    assert controller._active_threads == []
    assert controller._active_workers == []


def test_controller_handle_quit_wipes_when_keep_data_is_false(qapp, tmp_path, monkeypatch) -> None:
    from my_lastfm_player import settings as settings_module

    window = MainWindow()
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_credentials({"key": "val"})
    controller = ApplicationController(window, repository=repository)

    monkeypatch.setattr(settings_module.AppSettings, "keep_data_on_quit", lambda self: False)
    controller._handle_quit()

    assert not repository.credentials_path.exists()


def test_controller_handle_quit_skips_wipe_when_keep_data_is_true(
    qapp, tmp_path, monkeypatch
) -> None:
    from my_lastfm_player import settings as settings_module

    window = MainWindow()
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_credentials({"key": "val"})
    controller = ApplicationController(window, repository=repository)

    monkeypatch.setattr(settings_module.AppSettings, "keep_data_on_quit", lambda self: True)
    controller._handle_quit()

    assert repository.credentials_path.exists()


def test_controller_load_cached_tracks_returns_false_for_empty_username(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(window)

    result = controller.load_cached_tracks_for_entered_username()

    assert result is False


def test_controller_load_cached_tracks_reports_when_no_cached_tracks_and_verify(
    qapp, tmp_path
) -> None:
    window = MainWindow()
    window.username_input.setText("user")
    controller = ApplicationController(window, repository=JsonTrackRepository(data_dir=tmp_path))

    result = controller.load_cached_tracks_for_entered_username(verify_online_count=True)

    assert result is False
    assert "No cached tracks found for user" in window.feedback_log.toPlainText()


def test_controller_load_cached_tracks_returns_false_without_verify_message(
    qapp,
    tmp_path,
) -> None:
    window = MainWindow()
    window.username_input.setText("user")
    controller = ApplicationController(window, repository=JsonTrackRepository(data_dir=tmp_path))

    result = controller.load_cached_tracks_for_entered_username()

    assert result is False
    assert "No cached tracks found" not in window.feedback_log.toPlainText()


def test_controller_load_cached_tracks_uses_cache_without_online_verify(
    qapp,
    tmp_path,
) -> None:
    window = MainWindow()
    window.username_input.setText("user")
    repository = JsonTrackRepository(data_dir=tmp_path)
    track = Track(artist="A", title="T")
    repository.save_tracks("user", [track])
    controller = ApplicationController(window, repository=repository)

    result = controller.load_cached_tracks_for_entered_username()

    assert result is True
    assert window.tracks() == [track]
    assert "checking Last.fm before using them" not in window.feedback_log.toPlainText()


def test_controller_load_cached_tracks_reports_count_when_verify_and_tracks_present(
    qapp, tmp_path
) -> None:
    window = MainWindow()
    window.username_input.setText("user")
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_tracks("user", [Track(artist="A", title="T")])
    controller = ApplicationController(
        window,
        repository=repository,
        scraper=CountCheckingScraper(1),  # type: ignore[arg-type]
    )

    result = controller.load_cached_tracks_for_entered_username(verify_online_count=True)

    assert result is True
    assert "Found 1 cached tracks for user" in window.feedback_log.toPlainText()


def test_controller_does_not_reload_cache_while_fresh_fetch_is_active(qapp, tmp_path) -> None:
    window = MainWindow()
    window.username_input.setText("user")
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_tracks("user", [Track(artist="Cached", title="Track")])
    controller = ApplicationController(window, repository=repository)
    active_worker = object()
    controller._active_fetch_worker = active_worker  # type: ignore[assignment]

    result = controller.load_cached_tracks_for_entered_username()

    assert result is False
    assert controller._active_fetch_worker is active_worker
    assert [track.artist for track in window.tracks()] != ["Cached"]


def test_controller_open_file_cache_reports_mkdir_failure(qapp, tmp_path, monkeypatch) -> None:
    from pathlib import Path

    window = MainWindow()
    repository = JsonTrackRepository(data_dir=tmp_path / "data")
    controller = ApplicationController(window, repository=repository)

    def _fail_mkdir(*_a, **_kw) -> None:
        raise OSError("denied")

    monkeypatch.setattr(Path, "mkdir", _fail_mkdir)
    controller.open_file_cache()

    assert "Could not open data folder:" in window.feedback_log.toPlainText()


def test_controller_init_scrobbling_reports_session_key_not_verified(
    qapp, tmp_path, monkeypatch
) -> None:
    from my_lastfm_player import controller as controller_module
    from my_lastfm_player.scrobbling import ScrobblingService

    class FailNetwork:
        def get_authenticated_user(self):
            raise RuntimeError("auth failed")

    window = MainWindow()
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_credentials({"session_key": "stale"})

    monkeypatch.setattr(
        controller_module,
        "ScrobblingService",
        lambda **kw: ScrobblingService(
            **{**kw, "network_factory": lambda **_: FailNetwork()}
        ),
    )
    controller = ApplicationController(window, repository=repository)
    controller._init_scrobbling()

    assert "could not be verified" in window.feedback_log.toPlainText()


def test_controller_save_scrobbling_credentials_without_service(qapp, tmp_path) -> None:
    window = MainWindow()
    controller = ApplicationController(
        window,
        repository=JsonTrackRepository(data_dir=tmp_path),
    )
    controller._scrobbling_service = None

    controller._save_scrobbling_credentials()

    assert "no Last.fm scrobbling service is active" in window.feedback_log.toPlainText()


def test_controller_show_preferences_opens_dialog_and_saves(qapp, tmp_path, monkeypatch) -> None:
    import my_lastfm_player.ui.preferences_dialog as prefs_module
    from my_lastfm_player import settings as settings_module
    from my_lastfm_player.scrobbling import ScrobblingService

    exec_calls: list[int] = []
    saved_scrobbling: list[bool] = []

    class FakeDialog:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        def exec(self) -> None:
            exec_calls.append(1)

    monkeypatch.setattr(prefs_module, "PreferencesDialog", FakeDialog)
    monkeypatch.setattr(
        settings_module.AppSettings,
        "set_scrobbling_enabled",
        lambda self, enabled: saved_scrobbling.append(enabled),
    )

    window = MainWindow()
    controller = ApplicationController(
        window,
        repository=JsonTrackRepository(data_dir=tmp_path),
    )
    controller._scrobbling_service = ScrobblingService(
        api_key="key",
        api_secret="secret",
        username="testuser",
        scrobbling_enabled=False,
    )
    controller._show_preferences()

    assert exec_calls == [1]
    assert saved_scrobbling == [False]
    assert "Opening preferences." in window.feedback_log.toPlainText()


def test_controller_download_tracks_sets_active_flag_for_non_priority_run(
    qapp, tmp_path
) -> None:
    window = MainWindow()
    window.username_input.setText("user")
    controller = ApplicationController(window, repository=JsonTrackRepository(data_dir=tmp_path))
    controller._run_worker = lambda _w: None  # type: ignore[method-assign]

    controller.download_tracks()

    assert controller._download_worker_active
    assert not controller._download_stop_requested


def test_controller_pause_playback_reports_resume_failure(qapp) -> None:
    from my_lastfm_player.playback import PlaybackError

    window = MainWindow()
    playback = FakePlaybackService()
    playback._paused = True

    def fail_resume() -> None:
        raise PlaybackError("resume failed")

    playback.resume = fail_resume  # type: ignore[method-assign]
    controller = ApplicationController(window, playback_service=playback)  # type: ignore[arg-type]

    controller.pause_playback()

    assert "resume failed" in window.feedback_log.toPlainText()


def test_controller_handle_tracks_loaded_starts_lookup_after_complete_fetch(
    qapp, tmp_path
) -> None:
    window = MainWindow()
    window.set_username("user")
    controller = ApplicationController(window, repository=JsonTrackRepository(data_dir=tmp_path))
    controller._started_incremental_lookup_for_fetch = True
    lookup_calls: list[int] = []
    controller._start_automatic_lookup = lambda _username, _count: lookup_calls.append(1)  # type: ignore[method-assign]

    controller._handle_tracks_loaded("user", [Track(artist="A", title="T")])

    assert lookup_calls == [1]
    assert window.track_model.rowCount() == 1


def test_username_change_cancels_old_work_and_ignores_late_updates(qapp, tmp_path) -> None:
    window = MainWindow()
    window.set_username("old-user")
    old_track = Track(artist="Old", title="Track")
    window.set_tracks([old_track])
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_tracks("old-user", [old_track])
    controller = ApplicationController(window, repository=repository)
    lookup = LookupTracksWorker("old-user", controller.youtube_resolver, repository)
    download = DownloadTracksWorker("old-user", controller.download_manager, repository)
    controller._active_workers.extend([lookup, download])

    window.set_username("new-user")
    controller._handle_username_text_edited("new-user")

    assert lookup._stop_event.is_set()
    assert download._stop_event.is_set()
    assert repository.load_tracks("old-user") == [old_track]
    assert window.tracks() == []
    assert window.username_input.isEnabled()

    controller._handle_track_updated(
        "old-user", replace(old_track, status=TrackStatus.NOT_FOUND)
    )
    assert window.tracks() == []


def test_username_change_cancels_fetch_and_skips_other_users(qapp, tmp_path) -> None:
    window = MainWindow()
    window.set_username("old-user")
    repository = JsonTrackRepository(data_dir=tmp_path)
    controller = ApplicationController(window, repository=repository)
    old_fetch = FetchLovedTracksWorker("old-user", controller.scraper, repository)
    other_lookup = LookupTracksWorker("other-user", controller.youtube_resolver, repository)
    controller._active_workers.extend([other_lookup, old_fetch])
    controller._active_fetch_worker = old_fetch

    window.set_username("new-user")
    controller._handle_username_text_edited("new-user")

    assert old_fetch._stop_requested
    assert not other_lookup._stop_event.is_set()
    assert controller._active_fetch_worker is None


def test_username_edit_handles_same_and_initial_username(qapp, tmp_path) -> None:
    window = MainWindow()
    controller = ApplicationController(
        window,
        repository=JsonTrackRepository(data_dir=tmp_path),
    )

    controller._handle_username_text_edited("")
    controller._handle_username_text_edited("new-user")

    assert controller._workflow_username is None
    assert window.tracks() == []


def test_username_can_be_replaced_through_qt_while_work_is_active(qapp, tmp_path) -> None:
    window = MainWindow()
    window.set_username("old-user")
    old_track = Track(artist="Old", title="Track")
    window.set_tracks([old_track])
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_tracks("old-user", [old_track])
    controller = ApplicationController(window, repository=repository)
    lookup = LookupTracksWorker("old-user", controller.youtube_resolver, repository)
    download = DownloadTracksWorker("old-user", controller.download_manager, repository)
    controller._active_workers.extend([lookup, download])
    window.username_input.textEdited.connect(controller._handle_username_text_edited)
    window.username_input.editingFinished.connect(
        controller.load_cached_tracks_for_entered_username
    )
    window.show()
    window.username_input.setFocus()
    window.username_input.selectAll()

    QTest.keyClicks(window.username_input, "new-user")
    qapp.processEvents()

    assert window.username_input.isEnabled()
    assert lookup._stop_event.is_set()
    assert download._stop_event.is_set()
    assert controller._workflow_username is None
    assert sorted(path.name for path in repository.tracks_dir.glob("*.json")) == [
        "old-user.json"
    ]

    QTest.keyClick(window.username_input, Qt.Key.Key_Return)
    qapp.processEvents()

    assert controller._workflow_username == "new-user"


def test_stale_worker_signals_do_not_change_current_user_ui(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(window)
    controller._workflow_username = "new-user"
    track = Track(artist="Old", title="Track")

    controller._handle_tracks_loaded("old-user", [track])
    controller._handle_fetch_stopped("old-user", [track])
    controller._handle_tracks_updated("old-user", [track])
    controller._handle_tracks_resolved("old-user", [track])
    controller._handle_tracks_downloaded("old-user", [track])
    controller._handle_worker_progress("old-user", 50, "old progress")
    controller._handle_worker_error_for("old-user", "old error")

    assert window.tracks() == []
    assert "old progress" not in window.statusBar().currentMessage()
    assert "old error" not in window.feedback_log.toPlainText()


def test_uncommitted_empty_username_rejects_all_worker_updates(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(window)
    track = Track(artist="Old", title="Track")

    controller._handle_tracks_updated("old-user", [track])
    controller._handle_track_updated("old-user", track)

    assert window.tracks() == []


def test_returning_to_same_username_does_not_accept_previous_generation(qapp) -> None:
    window = MainWindow()
    window.set_username("user")
    controller = ApplicationController(window)
    previous_generation = controller._workflow_generation

    window.set_username("")
    controller._handle_username_text_edited("")
    window.set_username("user")
    controller.load_cached_tracks_for_entered_username()

    assert controller._workflow_username == "user"
    assert controller._workflow_generation == previous_generation + 1
    assert not controller._is_current_worker_context("user", previous_generation)


def test_previous_generation_workers_do_not_block_same_username_work(qapp, tmp_path) -> None:
    window = MainWindow()
    window.set_username("user")
    repository = JsonTrackRepository(data_dir=tmp_path)
    controller = ApplicationController(window, repository=repository)
    lookup = LookupTracksWorker("user", controller.youtube_resolver, repository)
    download = DownloadTracksWorker("user", controller.download_manager, repository)
    controller._active_workers.extend([lookup, download])
    controller._worker_generations[lookup] = controller._workflow_generation
    controller._worker_generations[download] = controller._workflow_generation

    controller._workflow_generation += 1

    assert not controller._has_active_lookup_worker("user")
    assert not controller._has_active_download_worker("user")


def test_current_worker_progress_and_error_reach_ui(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(window)
    controller._workflow_username = "user"

    controller._handle_worker_progress("user", 50, "halfway")
    controller._handle_worker_error_for("user", "failed item")

    assert window.progress_bar.value() == 0
    assert "failed item" in window.feedback_log.toPlainText()


def test_controller_handle_tracks_resolved_starts_priority_download_for_pending_retry(
    qapp, tmp_path
) -> None:
    window = MainWindow()
    window.set_username("user")
    repository = JsonTrackRepository(data_dir=tmp_path)
    track = Track(
        artist="Artist",
        title="Title",
        youtube_url="https://youtu.be/x",
        status=TrackStatus.QUEUED,
    )
    repository.save_tracks("user", [track])
    controller = ApplicationController(window, repository=repository)
    controller._pending_retry_cache_key = track.cache_key
    calls: list[tuple[str, str]] = []
    controller._start_priority_download = lambda username, key: calls.append((username, key))  # type: ignore[method-assign]

    controller._handle_tracks_resolved("user", [track])

    assert calls == [("user", track.cache_key)]


def test_controller_handle_tracks_resolved_reports_no_candidates_when_worker_active(
    qapp, tmp_path
) -> None:
    window = MainWindow()
    window.set_username("user")
    repository = JsonTrackRepository(data_dir=tmp_path)
    queued = Track(
        artist="A",
        title="T",
        youtube_url="https://youtu.be/y",
        status=TrackStatus.QUEUED,
    )
    repository.save_tracks("user", [queued])
    controller = ApplicationController(window, repository=repository)
    controller._download_worker_active = True

    controller._handle_tracks_resolved("user", [queued])

    log = window.feedback_log.toPlainText()
    assert "Resolved YouTube URLs" in log
    assert "No queued tracks are ready for download." not in log


def test_controller_handle_tracks_downloaded_clears_pending_retry(qapp) -> None:
    window = MainWindow()
    window.set_username("user")
    controller = ApplicationController(window)
    controller._pending_retry_cache_key = "some_key"

    controller._handle_tracks_downloaded("user", [])

    assert controller._pending_retry_cache_key is None


def test_controller_handle_tracks_downloaded_continues_bulk_download(qapp, tmp_path) -> None:
    window = MainWindow()
    window.set_username("user")
    repository = JsonTrackRepository(data_dir=tmp_path)
    queued = Track(
        artist="A",
        title="T",
        youtube_url="https://youtu.be/z",
        status=TrackStatus.QUEUED,
    )
    repository.save_tracks("user", [queued])
    controller = ApplicationController(window, repository=repository)
    controller._download_worker_active = True
    auto_calls: list[str] = []
    controller._start_automatic_download = lambda username: auto_calls.append(username)  # type: ignore[method-assign]

    controller._handle_tracks_downloaded("user", [queued])

    assert auto_calls == ["user"]


def test_controller_update_track_by_cache_key_does_nothing_on_miss(qapp) -> None:
    window = MainWindow()
    track = Track(artist="Artist", title="Title")
    window.set_tracks([track])
    controller = ApplicationController(window)

    controller._update_track_by_cache_key(Track(artist="Other", title="Track"))

    assert window.track_model.track_at(0).artist == "Artist"


def test_controller_save_visible_tracks_does_nothing_without_username(qapp, tmp_path) -> None:
    window = MainWindow()
    repository = JsonTrackRepository(data_dir=tmp_path)
    controller = ApplicationController(window, repository=repository)
    window.set_tracks([Track(artist="A", title="T")])

    controller._save_visible_tracks()

    assert not any(repository.tracks_dir.iterdir()) if repository.tracks_dir.exists() else True


def test_controller_retry_track_download_requires_username(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(window)

    controller.retry_track_download("some_key")

    assert "Enter a Last.fm username before retrying" in window.feedback_log.toPlainText()


def test_controller_retry_track_download_does_nothing_for_unknown_track(
    qapp, tmp_path
) -> None:
    window = MainWindow()
    window.username_input.setText("user")
    repository = JsonTrackRepository(data_dir=tmp_path)
    controller = ApplicationController(window, repository=repository)

    controller.retry_track_download("nonexistent_key")

    assert window.feedback_log.toPlainText() == ""


@pytest.mark.parametrize(
    "failed_status",
    [TrackStatus.NOT_FOUND, TrackStatus.LOOKUP_FAILED],
)
def test_controller_retry_track_download_resets_lookup_state_and_starts_lookup(
    qapp, tmp_path, failed_status
) -> None:
    window = MainWindow()
    window.username_input.setText("user")
    repository = JsonTrackRepository(data_dir=tmp_path)
    track = Track(artist="A", title="T", status=failed_status, error="lookup failed")
    repository.save_tracks("user", [track])
    window.set_tracks([track])
    controller = ApplicationController(window, repository=repository)
    lookup_calls: list[dict] = []

    def fake_resolve(username=None, priority_cache_key=None, max_tracks=None):
        lookup_calls.append({"username": username, "key": priority_cache_key, "n": max_tracks})

    controller.resolve_youtube_urls = fake_resolve  # type: ignore[method-assign]

    controller.retry_track_download(track.cache_key)

    assert controller._pending_retry_cache_key == track.cache_key
    assert lookup_calls == [{"username": "user", "key": track.cache_key, "n": 1}]
    reloaded = repository.load_tracks("user")
    assert reloaded[0].status == TrackStatus.FETCHED


def test_controller_retry_track_download_starts_priority_download_when_url_known(
    qapp, tmp_path
) -> None:
    window = MainWindow()
    window.username_input.setText("user")
    repository = JsonTrackRepository(data_dir=tmp_path)
    track = Track(
        artist="A",
        title="T",
        youtube_url="https://youtu.be/x",
        status=TrackStatus.FAILED,
        error="download failed",
    )
    repository.save_tracks("user", [track])
    window.set_tracks([track])
    controller = ApplicationController(window, repository=repository)
    download_calls: list[tuple] = []
    def fake_priority_download(username, key):
        download_calls.append((username, key))

    controller._start_priority_download = fake_priority_download  # type: ignore[method-assign]

    controller.retry_track_download(track.cache_key)

    assert controller._pending_retry_cache_key == track.cache_key
    assert download_calls == [("user", track.cache_key)]
    reloaded = repository.load_tracks("user")[0]
    assert reloaded.status is TrackStatus.QUEUED
    assert reloaded.youtube_url == "https://youtu.be/x"


def test_controller_play_prepared_track_key_not_in_visible_tracks(qapp) -> None:
    window = MainWindow()
    window.set_tracks([Track(artist="A", title="T")])
    controller = ApplicationController(window)

    controller._play_prepared_track("nonexistent_key")


def test_controller_play_prepared_track_not_yet_downloaded(qapp) -> None:
    window = MainWindow()
    track = Track(artist="A", title="T", status=TrackStatus.QUEUED)
    window.set_tracks([track])
    controller = ApplicationController(window, playback_service=FakePlaybackService())  # type: ignore[arg-type]

    controller._play_prepared_track(track.cache_key)

    assert controller._pending_play_cache_key is None


def test_controller_play_prepared_track_plays_when_downloaded(qapp, tmp_path) -> None:
    window = MainWindow()
    track = downloaded_track(tmp_path, artist="A", title="T")
    window.set_tracks([track])
    playback = FakePlaybackService()
    controller = ApplicationController(window, playback_service=playback)  # type: ignore[arg-type]
    controller._pending_play_cache_key = track.cache_key

    controller._play_prepared_track(track.cache_key)

    assert playback.events == [f"play:{track.title}"]
    assert controller._pending_play_cache_key is None


def test_controller_track_ready_starts_pending_play_priority_download(
    qapp,
    tmp_path,
) -> None:
    window = MainWindow()
    repository = JsonTrackRepository(data_dir=tmp_path)
    track = Track(
        artist="A",
        title="T",
        youtube_url="https://youtu.be/a",
        status=TrackStatus.QUEUED,
    )
    controller = ApplicationController(window, repository=repository)
    controller._pending_play_cache_key = track.cache_key
    calls: list[tuple[str, str]] = []
    controller._start_priority_download = lambda username, key: calls.append((username, key))  # type: ignore[method-assign]

    controller._handle_track_ready_for_download("user", track)

    assert calls == [("user", track.cache_key)]


def test_controller_track_ready_starts_pending_retry_priority_download(
    qapp,
    tmp_path,
) -> None:
    window = MainWindow()
    repository = JsonTrackRepository(data_dir=tmp_path)
    track = Track(
        artist="A",
        title="T",
        youtube_url="https://youtu.be/a",
        status=TrackStatus.QUEUED,
    )
    controller = ApplicationController(window, repository=repository)
    controller._pending_retry_cache_key = track.cache_key
    calls: list[tuple[str, str]] = []
    controller._start_priority_download = lambda username, key: calls.append((username, key))  # type: ignore[method-assign]

    controller._handle_track_ready_for_download("user", track)

    assert calls == [("user", track.cache_key)]


def test_controller_track_ready_starts_download_while_lookup_active(
    qapp,
    tmp_path,
) -> None:
    window = MainWindow()
    repository = JsonTrackRepository(data_dir=tmp_path)
    track = Track(
        artist="A",
        title="T",
        youtube_url="https://youtu.be/a",
        status=TrackStatus.QUEUED,
    )
    controller = ApplicationController(window, repository=repository)
    auto_calls: list[str] = []
    controller._start_automatic_download = lambda username: auto_calls.append(username)  # type: ignore[method-assign]

    # Simulate a LookupTracksWorker being active.
    fake_lookup_worker = MagicMock(spec=LookupTracksWorker)
    controller._active_workers.append(fake_lookup_worker)

    controller._handle_track_ready_for_download("user", track)

    assert auto_calls == ["user"]


def test_controller_track_ready_starts_auto_download_when_no_lookup_active(
    qapp,
    tmp_path,
) -> None:
    window = MainWindow()
    repository = JsonTrackRepository(data_dir=tmp_path)
    track = Track(
        artist="A",
        title="T",
        youtube_url="https://youtu.be/a",
        status=TrackStatus.QUEUED,
    )
    controller = ApplicationController(window, repository=repository)
    auto_calls: list[str] = []
    controller._start_automatic_download = lambda username: auto_calls.append(username)  # type: ignore[method-assign]

    controller._handle_track_ready_for_download("user", track)

    assert auto_calls == ["user"]


def test_controller_queues_next_lookup_wave_until_current_worker_retires(
    qapp, tmp_path
) -> None:
    window = MainWindow()
    window.set_username("user")
    repository = JsonTrackRepository(data_dir=tmp_path)
    controller = ApplicationController(window, repository=repository)
    worker = LookupTracksWorker("user", controller.youtube_resolver, repository)
    controller._active_workers.append(worker)
    starts: list[tuple[str, int]] = []
    controller._start_automatic_lookup = lambda username, count: starts.append(  # type: ignore[method-assign]
        (username, count)
    )

    controller._ensure_automatic_lookup("user", 2)

    assert starts == []
    assert controller._pending_lookup_users == {"user"}

    repository.save_tracks("user", [Track(artist="New", title="Track")])
    controller._forget_worker(worker)

    assert starts == [("user", 1)]


def test_controller_retires_download_worker_and_starts_remaining_queue(
    qapp, tmp_path
) -> None:
    window = MainWindow()
    window.set_username("user")
    repository = JsonTrackRepository(data_dir=tmp_path)
    queued = Track(
        artist="Artist",
        title="Track",
        youtube_url="https://youtu.be/result",
        status=TrackStatus.QUEUED,
    )
    repository.save_tracks("user", [queued])
    controller = ApplicationController(window, repository=repository)
    worker = DownloadTracksWorker("user", controller.download_manager, repository)
    controller._active_workers.append(worker)
    starts: list[str] = []
    controller._start_automatic_download = lambda username: starts.append(username)  # type: ignore[method-assign]
    controller._download_worker_active = False

    controller._forget_worker(worker)

    assert starts == ["user"]


def test_controller_stop_downloads_sets_each_current_worker_event(qapp, tmp_path) -> None:
    window = MainWindow()
    window.set_username("user")
    repository = JsonTrackRepository(data_dir=tmp_path)
    controller = ApplicationController(window, repository=repository)
    current = DownloadTracksWorker("user", controller.download_manager, repository)
    other = DownloadTracksWorker("other", controller.download_manager, repository)
    controller._active_workers.extend([current, other])

    controller.stop_downloads()

    assert current._stop_event.is_set()
    assert not other._stop_event.is_set()


def test_controller_does_not_auto_download_after_explicit_stop(qapp, tmp_path) -> None:
    window = MainWindow()
    controller = ApplicationController(
        window, repository=JsonTrackRepository(data_dir=tmp_path)
    )
    controller._download_stop_requested = True
    starts: list[str] = []
    controller._start_automatic_download = lambda username: starts.append(username)  # type: ignore[method-assign]

    controller._handle_track_ready_for_download(
        "user",
        Track(
            artist="Artist",
            title="Track",
            youtube_url="https://youtu.be/result",
            status=TrackStatus.QUEUED,
        ),
    )

    assert starts == []


def test_controller_maybe_scrobble_does_nothing_when_no_current_track(qapp) -> None:
    from my_lastfm_player.scrobbling import ScrobblingService

    window = MainWindow()
    playback = FakePlaybackService()

    class FakeNetwork:
        def get_authenticated_user(self):
            class U:
                def get_name(self, properly_capitalized=False):
                    return "user"
            return U()

        def scrobble(self, **kwargs):
            pass

        def update_now_playing(self, **kwargs):
            pass

    svc = ScrobblingService(
        api_key="k", api_secret="s", session_key="sess", username="user",
        network_factory=lambda **kw: FakeNetwork(),
    )
    svc.try_connect()
    controller = ApplicationController(window, playback_service=playback)  # type: ignore[arg-type]
    controller._scrobbling_service = svc
    controller._playback_start_time = 1000
    playback.current_track = None

    controller._maybe_scrobble(100_000, 200_000)

    assert not controller._scrobble_submitted


def test_controller_handle_playback_finished_does_nothing_when_no_track(qapp) -> None:
    window = MainWindow()
    playback = FakePlaybackService()
    controller = ApplicationController(window, playback_service=playback)  # type: ignore[arg-type]

    controller._handle_playback_finished()

    assert window.feedback_log.toPlainText() == ""


def test_controller_handle_playback_finished_reports_done_when_no_next(qapp, tmp_path) -> None:
    window = MainWindow()
    track = Track(artist="Artist", title="Title", status=TrackStatus.DOWNLOADED)
    playback = FakePlaybackService()
    playback.current_track = track
    controller = ApplicationController(
        window,
        repository=JsonTrackRepository(data_dir=tmp_path),
        playback_service=playback,  # type: ignore[arg-type]
    )

    controller._handle_playback_finished()

    log = window.feedback_log.toPlainText()
    assert "Finished playback for Artist - Title." in log
    assert "Playback finished." in log


def test_controller_applies_and_persists_volume_and_mute(qapp, tmp_path) -> None:
    window = MainWindow()
    playback = FakePlaybackService()
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    controller = ApplicationController(
        window,
        playback_service=playback,  # type: ignore[arg-type]
    )
    controller.window.volume_changed.connect(controller.set_volume)
    controller.window.mute_toggled.connect(controller.set_muted)

    with patch.object(controller_module, "AppSettings", lambda: AppSettings(settings)):
        window.volume_slider.setValue(30)
        window.mute_checkbox.setChecked(True)

    assert playback.volume_percent == 30
    assert playback.muted is True
    assert AppSettings(settings).volume_percent() == 30
    assert AppSettings(settings).muted()


def test_controller_applies_audio_settings_when_playback_starts(qapp, tmp_path) -> None:
    track = downloaded_track(tmp_path)
    window = MainWindow()
    window.set_tracks([track])
    window.track_table.selectRow(0)
    window.set_volume_percent(70)
    window.set_muted(True)
    playback = FakePlaybackService()
    controller = ApplicationController(
        window,
        playback_service=playback,  # type: ignore[arg-type]
    )

    controller.play_selected_track()

    assert playback.volume_percent == 70
    assert playback.muted is True

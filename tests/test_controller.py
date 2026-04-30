from __future__ import annotations

from my_lastfm_player.controller import ApplicationController
from my_lastfm_player.dependencies import DependencyCheckResult
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.storage import JsonTrackRepository
from my_lastfm_player.ui.main_window import MainWindow


def test_controller_start_connects_fetch_signal_and_checks_dependencies(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(
        window,
        dependency_checker=lambda: DependencyCheckResult(installed=("ffmpeg",), missing=()),
    )

    controller.start()

    assert controller.check_dependencies().is_ok
    assert window.dependency_label.text() == "Dependencies installed: ffmpeg"


def test_controller_reports_missing_dependencies(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(
        window,
        dependency_checker=lambda: DependencyCheckResult(installed=(), missing=("yt-dlp",)),
    )

    result = controller.check_dependencies()

    assert not result.is_ok
    assert window.dependency_label.text() == "Missing dependencies: yt-dlp"
    assert "Missing dependencies: yt-dlp" in window.feedback_log.toPlainText()


def test_controller_rejects_empty_username(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(window)

    controller.fetch_loved_tracks()

    assert "Enter a Last.fm username" in window.feedback_log.toPlainText()


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


def test_controller_handles_resolved_tracks(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(window)

    controller._handle_tracks_resolved("example", [])

    assert window.track_model.rowCount() == 0
    assert "Resolved YouTube URLs for 0 tracks." in window.feedback_log.toPlainText()
    assert "No queued tracks are ready for download." in window.feedback_log.toPlainText()


def test_controller_starts_lookup_after_successful_fetch(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(window)
    calls: list[tuple[str, int]] = []

    def fake_start_lookup(username: str, track_count: int) -> None:
        calls.append((username, track_count))

    controller._start_automatic_lookup = fake_start_lookup  # type: ignore[method-assign]

    controller._handle_tracks_loaded("example", [Track(artist="Artist", title="Title")])

    assert calls == [("example", 1)]
    assert window.track_model.rowCount() == 1
    assert not window.fetch_pause_button.isEnabled()
    assert not window.fetch_stop_button.isEnabled()


def test_controller_updates_table_during_paginated_fetch(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(window)

    controller._handle_tracks_updated(
        "example",
        [Track(artist="Artist", title="Title")],
    )

    assert window.track_model.rowCount() == 1
    assert "Fetched 1 tracks for example" in window.statusBar().currentMessage()


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


def test_controller_handles_stopped_fetch_without_starting_lookup(qapp) -> None:
    window = MainWindow()
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
    track = Track(artist="Artist", title="Title")
    window.set_tracks([track])
    controller = ApplicationController(window)

    controller._handle_track_updated(
        "example",
        track.with_status(TrackStatus.SEARCHING),
    )

    assert window.track_model.track_at(0).status == TrackStatus.SEARCHING


def test_controller_starts_download_after_successful_lookup(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(window)
    calls: list[str] = []

    def fake_start_download(username: str) -> None:
        calls.append(username)

    controller._start_automatic_download = fake_start_download  # type: ignore[method-assign]

    controller._handle_tracks_resolved(
        "example",
        [
            Track(
                artist="Artist",
                title="Title",
                youtube_url="https://youtu.be/example",
                status=TrackStatus.QUEUED,
            )
        ],
    )

    assert calls == ["example"]


def test_controller_reenables_workflow_after_last_worker(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(window)
    controller._running_worker_count = 2
    window.set_workflow_enabled(False)

    controller._complete_worker_run()

    assert not window.fetch_button.isEnabled()

    controller._complete_worker_run()

    assert window.fetch_button.isEnabled()
    assert window.download_toggle_button.isEnabled()


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

    def play(self, track: Track) -> Track:
        self.events.append(f"play:{track.title}")
        playing_track = track.with_status(TrackStatus.PLAYING)
        self.current_track = playing_track
        return playing_track

    def pause(self) -> None:
        self.events.append("pause")

    def stop(self) -> Track | None:
        self.events.append("stop")
        stopped_track = (
            self.current_track.with_status(TrackStatus.DOWNLOADED)
            if self.current_track
            else None
        )
        self.current_track = None
        return stopped_track


def test_controller_plays_selected_downloaded_track(qapp, tmp_path) -> None:
    window = MainWindow()
    window.username_input.setText("user")
    track = Track(
        artist="Artist",
        title="Title",
        local_path=str(tmp_path / "track.mp3"),
        status=TrackStatus.DOWNLOADED,
    )
    window.set_tracks([track])
    window.track_table.selectRow(0)
    playback = FakePlaybackService()
    controller = ApplicationController(
        window,
        repository=JsonTrackRepository(data_dir=tmp_path),
        playback_service=playback,  # type: ignore[arg-type]
    )

    controller.play_selected_track()

    assert playback.events == ["play:Title"]
    assert window.track_model.track_at(0).status == TrackStatus.PLAYING
    assert "Playing Artist - Title." in window.feedback_log.toPlainText()


def test_controller_pause_and_stop_playback(qapp, tmp_path) -> None:
    window = MainWindow()
    track = Track(
        artist="Artist",
        title="Title",
        local_path=str(tmp_path / "track.mp3"),
        status=TrackStatus.PLAYING,
    )
    window.set_tracks([track])
    playback = FakePlaybackService()
    playback.current_track = track
    controller = ApplicationController(window, playback_service=playback)  # type: ignore[arg-type]

    controller.pause_playback()
    controller.stop_playback()

    assert playback.events == ["pause", "stop"]
    assert window.track_model.track_at(0).status == TrackStatus.DOWNLOADED
    assert "Playback paused." in window.feedback_log.toPlainText()
    assert "Playback stopped." in window.feedback_log.toPlainText()

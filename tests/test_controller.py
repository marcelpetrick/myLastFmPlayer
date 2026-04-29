from __future__ import annotations

from my_lastfm_player.controller import ApplicationController
from my_lastfm_player.dependencies import DependencyCheckResult
from my_lastfm_player.models import Track, TrackStatus
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
    controller = ApplicationController(window, playback_service=playback)  # type: ignore[arg-type]

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

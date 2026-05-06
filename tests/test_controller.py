from __future__ import annotations

from PyQt6.QtCore import Qt

from my_lastfm_player import controller as controller_module
from my_lastfm_player.app_credentials import LastFmApiCredentials
from my_lastfm_player.controller import ApplicationController
from my_lastfm_player.dependencies import DependencyCheckResult
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.storage import JsonTrackRepository
from my_lastfm_player.ui.main_window import MainWindow


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

    assert opened_paths == [str(repository.downloads_dir)]
    assert repository.downloads_dir.is_dir()
    assert "Opened file cache:" in window.feedback_log.toPlainText()


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

    assert repository.downloads_dir.is_dir()
    assert "Could not open file cache:" in window.feedback_log.toPlainText()


def test_controller_initializes_scrobbling_with_bundled_credentials(qapp, tmp_path) -> None:
    window = MainWindow()
    controller = ApplicationController(
        window,
        repository=JsonTrackRepository(data_dir=tmp_path),
    )

    controller._init_scrobbling()

    assert controller._scrobbling_service is not None
    assert controller._scrobbling_service.has_api_credentials


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

    controller.fetch_loved_tracks()

    assert fetch_calls == []
    assert window.tracks() == [cached_track]
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

    assert workers == []
    assert window.tracks() == [cached_track]
    assert "using 1 cached tracks" in window.feedback_log.toPlainText()


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
    assert "Resolved YouTube URLs for 0/0 tracks; 0 were not found." in (
        window.feedback_log.toPlainText()
    )
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


def test_controller_ignores_fetch_controls_without_active_worker(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(window)

    controller.toggle_fetch_pause()
    controller.stop_fetch()

    assert window.feedback_log.toPlainText() == ""


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


def test_controller_starts_priority_download_after_lookup_for_pending_play(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(window)
    track = Track(
        artist="Artist",
        title="Title",
        youtube_url="https://youtu.be/example",
        status=TrackStatus.QUEUED,
    )
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
    assert window.download_toggle_button.isEnabled()


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


def test_controller_auto_plays_next_track_after_finished_in_sort_order(
    qapp,
    tmp_path,
) -> None:
    window = MainWindow()
    window.username_input.setText("user")
    tracks = [
        Track(
            artist="Zed",
            title="Last",
            local_path=str(tmp_path / "last.mp3"),
            status=TrackStatus.DOWNLOADED,
        ),
        Track(
            artist="Alpha",
            title="First",
            local_path=str(tmp_path / "first.mp3"),
            status=TrackStatus.DOWNLOADED,
        ),
        Track(
            artist="Middle",
            title="Second",
            local_path=str(tmp_path / "second.mp3"),
            status=TrackStatus.DOWNLOADED,
        ),
    ]
    window.set_tracks(tracks)
    window.track_sort_model.sort(0, Qt.SortOrder.AscendingOrder)
    window.select_track_row(1)
    playback = FakePlaybackService()
    controller = ApplicationController(
        window,
        repository=JsonTrackRepository(data_dir=tmp_path),
        playback_service=playback,  # type: ignore[arg-type]
    )

    controller.play_selected_track()
    assert playback.finished_callback is not None
    playback.finished_callback()

    assert playback.events == ["play:First", "play:Second"]
    assert window.track_model.track_at(1).status == TrackStatus.DOWNLOADED
    assert window.track_model.track_at(2).status == TrackStatus.DOWNLOADED
    assert window.track_model.playing_cache_key() == tracks[2].cache_key
    assert window.selected_track() == tracks[2]
    assert "Continuing with next track: Middle - Second." in window.feedback_log.toPlainText()


def test_controller_wraps_to_first_sorted_track_after_last_track_finishes(
    qapp,
    tmp_path,
) -> None:
    window = MainWindow()
    window.username_input.setText("user")
    tracks = [
        Track(
            artist="Zed",
            title="Last",
            local_path=str(tmp_path / "last.mp3"),
            status=TrackStatus.DOWNLOADED,
        ),
        Track(
            artist="Alpha",
            title="First",
            local_path=str(tmp_path / "first.mp3"),
            status=TrackStatus.DOWNLOADED,
        ),
    ]
    window.set_tracks(tracks)
    window.track_sort_model.sort(0, Qt.SortOrder.AscendingOrder)
    window.select_track_row(0)
    playback = FakePlaybackService()
    controller = ApplicationController(
        window,
        repository=JsonTrackRepository(data_dir=tmp_path),
        playback_service=playback,  # type: ignore[arg-type]
    )

    controller.play_selected_track()
    assert playback.finished_callback is not None
    playback.finished_callback()

    assert playback.events == ["play:Last", "play:First"]
    assert window.track_model.track_at(0).status == TrackStatus.DOWNLOADED
    assert window.track_model.track_at(1).status == TrackStatus.DOWNLOADED
    assert window.track_model.playing_cache_key() == tracks[1].cache_key
    assert window.selected_track() == tracks[1]


def test_controller_pause_and_stop_playback(qapp, tmp_path) -> None:
    window = MainWindow()
    track = Track(
        artist="Artist",
        title="Title",
        local_path=str(tmp_path / "track.mp3"),
        status=TrackStatus.DOWNLOADED,
    )
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
    track = Track(
        artist="Artist",
        title="Title",
        local_path=str(tmp_path / "track.mp3"),
        status=TrackStatus.DOWNLOADED,
    )
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
    audio_path = tmp_path / "track.mp3"
    audio_path.write_bytes(b"fake mp3")
    window = MainWindow()
    track = Track(
        artist="Artist",
        title="Title",
        local_path=str(audio_path),
        status=TrackStatus.DOWNLOADED,
    )
    window.set_tracks([track])
    playback = FakePlaybackService()
    controller = ApplicationController(window, playback_service=playback)  # type: ignore[arg-type]

    assert window.play_button.isEnabled()
    assert not window.pause_button.isEnabled()
    assert not window.stop_button.isEnabled()

    controller._play_track(track)

    assert not window.play_button.isEnabled()
    assert window.pause_button.isEnabled()
    assert window.stop_button.isEnabled()

    controller.stop_playback()

    assert window.play_button.isEnabled()
    assert not window.pause_button.isEnabled()
    assert not window.stop_button.isEnabled()


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


def test_controller_reports_playback_errors(qapp) -> None:
    from my_lastfm_player.playback import PlaybackError

    window = MainWindow()
    playback = FakePlaybackService()

    def fail_play(_track: Track) -> Track:
        raise PlaybackError("play failed")

    playback.play = fail_play  # type: ignore[method-assign]
    playback.fail_seek = True
    playback.fail_pause = True
    track = Track(artist="Artist", title="Title", status=TrackStatus.DOWNLOADED, local_path="x")
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

    feedback = window.feedback_log.toPlainText()
    assert "Select a downloaded track before playing." in feedback
    assert "No track is currently playing." in feedback


def test_controller_handles_invalid_worker_payloads(qapp) -> None:
    window = MainWindow()
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
    assert window.progress_bar.format() == "Failed"


def test_controller_handles_downloaded_tracks_and_pending_play(qapp) -> None:
    window = MainWindow()
    controller = ApplicationController(window)
    track = Track(artist="Artist", title="Title", status=TrackStatus.DOWNLOADED)
    calls: list[str] = []
    controller._pending_play_cache_key = track.cache_key
    controller._play_prepared_track = lambda cache_key: calls.append(cache_key)  # type: ignore[method-assign]

    controller._handle_tracks_downloaded("user", [track])

    assert calls == [track.cache_key]
    assert "Download run for user finished: 1/1 tracks downloaded, 0 failed." in (
        window.feedback_log.toPlainText()
    )


def test_controller_starts_fetch_lookup_and_download_workers(qapp, tmp_path) -> None:
    window = MainWindow()
    window.username_input.setText("user")
    controller = ApplicationController(window, repository=JsonTrackRepository(data_dir=tmp_path))
    workers: list[tuple[str, object]] = []

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


def test_controller_scrobbles_at_ten_percent(qapp, tmp_path) -> None:
    window = MainWindow()
    audio_path = tmp_path / "track.mp3"
    audio_path.write_bytes(b"fake")
    track = Track(
        artist="Artist",
        title="Title",
        local_path=str(audio_path),
        status=TrackStatus.DOWNLOADED,
    )
    window.set_tracks([track])
    playback = FakePlaybackService()
    playback.duration = 200_000
    from my_lastfm_player.scrobbling import ScrobblingService

    scrobbles: list[dict] = []

    class FakeNetwork:
        def get_authenticated_user(self):
            class U:
                def get_name(self):
                    return "user"
            return U()

        def scrobble(self, **kwargs):
            scrobbles.append(kwargs)

        def update_now_playing(self, **kwargs):
            pass

    svc = ScrobblingService(
        api_key="k", api_secret="s", session_key="sess",
        network_factory=lambda **kw: FakeNetwork(),
    )
    svc.try_connect()
    controller = ApplicationController(window, playback_service=playback)  # type: ignore[arg-type]
    controller._scrobbling_service = svc

    controller._play_track(track)
    controller._maybe_scrobble(19_999, 200_000)  # just below 10%
    assert scrobbles == []

    controller._maybe_scrobble(20_000, 200_000)  # exactly 10%
    assert len(scrobbles) == 1
    assert scrobbles[0]["artist"] == "Artist"
    assert scrobbles[0]["title"] == "Title"

    controller._maybe_scrobble(100_000, 200_000)  # only submitted once
    assert len(scrobbles) == 1


def test_controller_scrobble_resets_on_new_track(qapp, tmp_path) -> None:
    window = MainWindow()
    track = Track(
        artist="Artist",
        title="Title",
        local_path=str(tmp_path / "t.mp3"),
        status=TrackStatus.DOWNLOADED,
    )
    window.set_tracks([track])
    playback = FakePlaybackService()
    playback.duration = 100_000

    from my_lastfm_player.scrobbling import ScrobblingService

    scrobbles: list[dict] = []

    class FakeNetwork:
        def get_authenticated_user(self):
            class U:
                def get_name(self):
                    return "user"
            return U()

        def scrobble(self, **kwargs):
            scrobbles.append(kwargs)

        def update_now_playing(self, **kwargs):
            pass

    svc = ScrobblingService(
        api_key="k", api_secret="s", session_key="sess",
        network_factory=lambda **kw: FakeNetwork(),
    )
    svc.try_connect()
    controller = ApplicationController(window, playback_service=playback)  # type: ignore[arg-type]
    controller._scrobbling_service = svc

    controller._play_track(track)
    controller._maybe_scrobble(10_000, 100_000)
    assert len(scrobbles) == 1

    controller._play_track(track)  # restart same track
    assert not controller._scrobble_submitted

    controller._maybe_scrobble(10_000, 100_000)
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

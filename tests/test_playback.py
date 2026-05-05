from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from my_lastfm_player import playback as playback_module
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.playback import PlaybackError, PlaybackService, QtPlaybackBackend


class FakePlaybackBackend:
    def __init__(self) -> None:
        self.events: list[tuple[str, Path | None]] = []
        self.position = 0
        self.duration = 180_000
        self.position_callbacks: list[Callable[[int], None]] = []
        self.duration_callbacks: list[Callable[[int], None]] = []
        self.finished_callbacks: list[Callable[[], None]] = []

    def play(self, path: Path) -> None:
        self.events.append(("play", path))

    def pause(self) -> None:
        self.events.append(("pause", None))

    def resume(self) -> None:
        self.events.append(("resume", None))

    def stop(self) -> None:
        self.events.append(("stop", None))

    def seek(self, position_ms: int) -> None:
        self.position = position_ms
        self.events.append(("seek", None))

    def position_ms(self) -> int:
        return self.position

    def duration_ms(self) -> int:
        return self.duration

    def on_position_changed(self, callback: Callable[[int], None]) -> None:
        self.position_callbacks.append(callback)

    def on_duration_changed(self, callback: Callable[[int], None]) -> None:
        self.duration_callbacks.append(callback)

    def on_finished(self, callback: Callable[[], None]) -> None:
        self.finished_callbacks.append(callback)


def test_playback_service_plays_downloaded_track(tmp_path: Path) -> None:
    audio_path = tmp_path / "track.mp3"
    audio_path.write_bytes(b"fake mp3")
    backend = FakePlaybackBackend()
    service = PlaybackService(backend=backend)
    track = Track(
        artist="Artist",
        title="Title",
        local_path=str(audio_path),
        status=TrackStatus.DOWNLOADED,
    )

    playing_track = service.play(track)

    assert playing_track is track
    assert playing_track.status == TrackStatus.DOWNLOADED
    assert service.current_track is track
    assert backend.events == [("play", audio_path)]


def test_playback_service_stops_previous_track_when_switching(tmp_path: Path) -> None:
    first_path = tmp_path / "first.mp3"
    second_path = tmp_path / "second.mp3"
    first_path.write_bytes(b"first")
    second_path.write_bytes(b"second")
    backend = FakePlaybackBackend()
    service = PlaybackService(backend=backend)

    service.play(
        Track(
            artist="First",
            title="Track",
            local_path=str(first_path),
            status=TrackStatus.DOWNLOADED,
        )
    )
    service.play(
        Track(
            artist="Second",
            title="Track",
            local_path=str(second_path),
            status=TrackStatus.DOWNLOADED,
        )
    )

    assert backend.events == [
        ("play", first_path),
        ("stop", None),
        ("play", second_path),
    ]


def test_playback_service_pause_and_stop(tmp_path: Path) -> None:
    audio_path = tmp_path / "track.mp3"
    audio_path.write_bytes(b"fake mp3")
    backend = FakePlaybackBackend()
    service = PlaybackService(backend=backend)
    service.play(
        Track(
            artist="Artist",
            title="Title",
            local_path=str(audio_path),
            status=TrackStatus.DOWNLOADED,
        )
    )

    service.pause()
    stopped_track = service.stop()

    assert stopped_track is not None
    assert stopped_track.status == TrackStatus.DOWNLOADED
    assert service.current_track is None
    assert backend.events[-2:] == [("pause", None), ("stop", None)]


def test_playback_service_finishes_current_track_without_stopping_backend(
    tmp_path: Path,
) -> None:
    audio_path = tmp_path / "track.mp3"
    audio_path.write_bytes(b"fake mp3")
    backend = FakePlaybackBackend()
    service = PlaybackService(backend=backend)
    service.play(
        Track(
            artist="Artist",
            title="Title",
            local_path=str(audio_path),
            status=TrackStatus.DOWNLOADED,
        )
    )

    finished_track = service.finish_current()

    assert finished_track is not None
    assert finished_track.status == TrackStatus.DOWNLOADED
    assert service.current_track is None
    assert backend.events == [("play", audio_path)]


def test_playback_service_seeks_current_track(tmp_path: Path) -> None:
    audio_path = tmp_path / "track.mp3"
    audio_path.write_bytes(b"fake mp3")
    backend = FakePlaybackBackend()
    service = PlaybackService(backend=backend)
    service.play(
        Track(
            artist="Artist",
            title="Title",
            local_path=str(audio_path),
            status=TrackStatus.DOWNLOADED,
        )
    )

    service.seek(42_500)

    assert service.position_ms() == 42_500
    assert service.duration_ms() == 180_000
    assert backend.events[-1] == ("seek", None)


def test_playback_service_rejects_missing_or_not_downloaded_tracks(tmp_path: Path) -> None:
    service = PlaybackService(backend=FakePlaybackBackend())

    with pytest.raises(PlaybackError, match="not downloaded"):
        service.play(Track(artist="Artist", title="Title", status=TrackStatus.QUEUED))

    with pytest.raises(PlaybackError, match="does not exist"):
        service.play(
            Track(
                artist="Artist",
                title="Title",
                local_path=str(tmp_path / "missing.mp3"),
                status=TrackStatus.DOWNLOADED,
            )
        )


def test_playback_service_rejects_pause_without_current_track() -> None:
    service = PlaybackService(backend=FakePlaybackBackend())

    with pytest.raises(PlaybackError, match="No track"):
        service.pause()

    with pytest.raises(PlaybackError, match="No track"):
        service.seek(10_000)


class FakeSignal:
    def __init__(self) -> None:
        self.callbacks: list[Callable[[int], None]] = []

    def connect(self, callback: Callable[[int], None]) -> None:
        self.callbacks.append(callback)


class FakeQtMediaPlayer:
    def __init__(self) -> None:
        self.positionChanged = FakeSignal()
        self.durationChanged = FakeSignal()
        self.mediaStatusChanged = FakeSignal()
        self.audio_output = None
        self.source = None
        self.play_called = False
        self.pause_called = False
        self.stop_called = False
        self.position_value = -10
        self.duration_value = -20

    def setAudioOutput(self, audio_output) -> None:
        self.audio_output = audio_output

    def setSource(self, source) -> None:
        self.source = source

    def play(self) -> None:
        self.play_called = True

    def pause(self) -> None:
        self.pause_called = True

    def stop(self) -> None:
        self.stop_called = True

    def setPosition(self, position: int) -> None:
        self.position_value = position

    def position(self) -> int:
        return self.position_value

    def duration(self) -> int:
        return self.duration_value


def test_qt_playback_backend_wraps_player_and_normalizes_values(
    monkeypatch, tmp_path: Path
) -> None:
    created_players: list[FakeQtMediaPlayer] = []

    def fake_player_factory() -> FakeQtMediaPlayer:
        player = FakeQtMediaPlayer()
        created_players.append(player)
        return player

    monkeypatch.setattr(playback_module, "QAudioOutput", lambda: "audio-output")
    monkeypatch.setattr(playback_module, "QMediaPlayer", fake_player_factory)

    backend = QtPlaybackBackend()
    player = created_players[0]
    positions: list[int] = []
    durations: list[int] = []
    finished: list[bool] = []
    audio_path = tmp_path / "track.mp3"
    audio_path.write_bytes(b"fake")

    backend.on_position_changed(positions.append)
    backend.on_duration_changed(durations.append)
    backend.on_finished(lambda: finished.append(True))
    backend.play(audio_path)
    backend.pause()
    backend.stop()
    backend.seek(-100)
    backend._notify_position_changed(-5)
    backend._notify_duration_changed(-9)
    backend._notify_media_status_changed(object())
    backend._notify_media_status_changed(playback_module._END_OF_MEDIA_STATUS)

    assert player.audio_output == "audio-output"
    assert player.source is not None
    assert player.play_called
    assert player.pause_called
    assert player.stop_called
    assert player.position_value == 0
    assert backend.position_ms() == 0
    assert backend.duration_ms() == 0
    assert positions == [0]
    assert durations == [0]
    assert finished == [True]

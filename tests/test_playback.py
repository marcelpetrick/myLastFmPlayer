from __future__ import annotations

from pathlib import Path

import pytest

from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.playback import PlaybackError, PlaybackService


class FakePlaybackBackend:
    def __init__(self) -> None:
        self.events: list[tuple[str, Path | None]] = []

    def play(self, path: Path) -> None:
        self.events.append(("play", path))

    def pause(self) -> None:
        self.events.append(("pause", None))

    def stop(self) -> None:
        self.events.append(("stop", None))


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

    assert playing_track.status == TrackStatus.PLAYING
    assert service.current_track == playing_track
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

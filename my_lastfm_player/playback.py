from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Protocol

from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer

from my_lastfm_player.models import Track, TrackStatus

LOGGER = logging.getLogger(__name__)


class PlaybackError(RuntimeError):
    """Raised when local playback cannot start or change state."""


class PlaybackBackend(Protocol):
    """Backend protocol used by :class:`PlaybackService`."""

    def play(self, path: Path) -> None:
        """Start playing the audio file at ``path``."""

        ...

    def pause(self) -> None:
        """Pause current playback."""

        ...

    def stop(self) -> None:
        """Stop current playback."""

        ...

    def seek(self, position_ms: int) -> None:
        """Seek current playback to ``position_ms``."""

        ...

    def position_ms(self) -> int:
        """Return the current playback position in milliseconds."""

        ...

    def duration_ms(self) -> int:
        """Return the current media duration in milliseconds."""

        ...

    def on_position_changed(self, callback: Callable[[int], None]) -> None:
        """Register ``callback`` for backend position changes."""

        ...

    def on_duration_changed(self, callback: Callable[[int], None]) -> None:
        """Register ``callback`` for backend duration changes."""

        ...


class QtPlaybackBackend:
    """PyQt multimedia backend for local audio playback."""

    def __init__(self) -> None:
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)
        self._position_callbacks: list[Callable[[int], None]] = []
        self._duration_callbacks: list[Callable[[int], None]] = []
        self.player.positionChanged.connect(self._notify_position_changed)
        self.player.durationChanged.connect(self._notify_duration_changed)

    def play(self, path: Path) -> None:
        """Start playing ``path`` through ``QMediaPlayer``."""

        self.player.setSource(QUrl.fromLocalFile(str(path)))
        self.player.play()

    def pause(self) -> None:
        """Pause the Qt media player."""

        self.player.pause()

    def stop(self) -> None:
        """Stop the Qt media player."""

        self.player.stop()

    def seek(self, position_ms: int) -> None:
        """Seek the Qt media player to ``position_ms``."""

        self.player.setPosition(max(0, position_ms))

    def position_ms(self) -> int:
        """Return the Qt media player's current position."""

        return max(0, self.player.position())

    def duration_ms(self) -> int:
        """Return the Qt media player's current duration."""

        return max(0, self.player.duration())

    def on_position_changed(self, callback: Callable[[int], None]) -> None:
        """Register ``callback`` for Qt position changes."""

        self._position_callbacks.append(callback)

    def on_duration_changed(self, callback: Callable[[int], None]) -> None:
        """Register ``callback`` for Qt duration changes."""

        self._duration_callbacks.append(callback)

    def _notify_position_changed(self, position_ms: int) -> None:
        for callback in self._position_callbacks:
            callback(max(0, position_ms))

    def _notify_duration_changed(self, duration_ms: int) -> None:
        for callback in self._duration_callbacks:
            callback(max(0, duration_ms))


class PlaybackService:
    """Validate tracks and coordinate playback state transitions."""

    def __init__(self, backend: PlaybackBackend | None = None) -> None:
        self.backend = backend or QtPlaybackBackend()
        self.current_track: Track | None = None

    def play(self, track: Track) -> Track:
        """Play ``track`` and return the same track marked as playing."""

        path = _validated_local_path(track)
        if self.current_track is not None and self.current_track.cache_key != track.cache_key:
            self.backend.stop()

        LOGGER.info("Starting playback for %s - %s", track.artist, track.title)
        print(f"[myLastFmPlayer] Starting playback: {track.artist} - {track.title}", flush=True)
        self.backend.play(path)
        playing_track = track.with_status(TrackStatus.PLAYING, error=None)
        self.current_track = playing_track
        return playing_track

    def pause(self) -> None:
        """Pause the current track or raise ``PlaybackError`` when idle."""

        if self.current_track is None:
            raise PlaybackError("No track is currently playing")
        LOGGER.info(
            "Pausing playback for %s - %s",
            self.current_track.artist,
            self.current_track.title,
        )
        print("[myLastFmPlayer] Pausing playback", flush=True)
        self.backend.pause()

    def stop(self) -> Track | None:
        """Stop playback and return the track restored to downloaded state."""

        if self.current_track is None:
            return None
        LOGGER.info(
            "Stopping playback for %s - %s",
            self.current_track.artist,
            self.current_track.title,
        )
        print("[myLastFmPlayer] Stopping playback", flush=True)
        self.backend.stop()
        stopped_track = self.current_track.with_status(TrackStatus.DOWNLOADED, error=None)
        self.current_track = None
        return stopped_track

    def seek(self, position_ms: int) -> None:
        """Seek the current track or raise ``PlaybackError`` when idle."""

        if self.current_track is None:
            raise PlaybackError("No track is currently playing")
        self.backend.seek(max(0, position_ms))

    def position_ms(self) -> int:
        """Return the current playback position in milliseconds."""

        return self.backend.position_ms()

    def duration_ms(self) -> int:
        """Return the current media duration in milliseconds."""

        return self.backend.duration_ms()

    def on_position_changed(self, callback: Callable[[int], None]) -> None:
        """Register ``callback`` for playback position updates."""

        self.backend.on_position_changed(callback)

    def on_duration_changed(self, callback: Callable[[int], None]) -> None:
        """Register ``callback`` for playback duration updates."""

        self.backend.on_duration_changed(callback)


def _validated_local_path(track: Track) -> Path:
    if track.status is not TrackStatus.DOWNLOADED and track.status is not TrackStatus.PLAYING:
        raise PlaybackError("Selected track is not downloaded")
    if not track.local_path:
        raise PlaybackError("Selected track has no local file path")

    path = Path(track.local_path)
    if not path.is_file():
        raise PlaybackError(f"Local audio file does not exist: {path}")
    return path

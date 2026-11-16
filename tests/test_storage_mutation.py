"""Directory creation contract of the atomic JSON writer."""

from __future__ import annotations

from pathlib import Path

from my_lastfm_player.models import Track
from my_lastfm_player.storage import JsonTrackRepository


def test_atomic_save_creates_every_missing_parent_directory(tmp_path: Path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path / "a" / "b")

    repository.save_tracks("alice", [Track("Artist", "Title")])

    assert repository.load_tracks("alice") == [Track("Artist", "Title")]

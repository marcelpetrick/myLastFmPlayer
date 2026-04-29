from __future__ import annotations

import pytest
from PyQt6.QtCore import Qt

from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.ui.track_table_model import TrackTableModel, example_tracks


def test_track_table_model_exposes_artist_title_and_status() -> None:
    model = TrackTableModel(
        [
            Track(artist="Artist", title="Title", status=TrackStatus.SEARCHING),
        ]
    )

    assert model.rowCount() == 1
    assert model.columnCount() == 3
    assert model.headerData(0, Qt.Orientation.Horizontal) == "Artist"
    assert model.headerData(1, Qt.Orientation.Horizontal) == "Title"
    assert model.headerData(2, Qt.Orientation.Horizontal) == "Status"
    assert model.data(model.index(0, 0)) == "Artist"
    assert model.data(model.index(0, 1)) == "Title"
    assert model.data(model.index(0, 2)) == "Searching"


def test_track_table_model_replaces_and_returns_tracks() -> None:
    model = TrackTableModel()
    tracks = [Track(artist="Artist", title="Title")]

    model.set_tracks(tracks)

    assert model.tracks() == tracks
    assert model.track_at(0) == tracks[0]


def test_track_table_model_updates_existing_row() -> None:
    model = TrackTableModel([Track(artist="Artist", title="Title")])
    updated_track = Track(artist="Artist", title="Title", status=TrackStatus.DOWNLOADED)

    model.update_track(0, updated_track)

    assert model.track_at(0) == updated_track
    assert model.data(model.index(0, 2)) == "Downloaded"


def test_track_table_model_rejects_out_of_range_updates() -> None:
    model = TrackTableModel()

    with pytest.raises(IndexError, match="out of range"):
        model.update_track(0, Track(artist="Artist", title="Title"))


def test_example_tracks_match_mvp_shell() -> None:
    tracks = example_tracks()

    assert [track.status for track in tracks] == [TrackStatus.FETCHED, TrackStatus.QUEUED]

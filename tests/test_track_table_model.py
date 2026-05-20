from __future__ import annotations

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontMetrics, QPainter, QPixmap
from PyQt6.QtWidgets import QApplication, QStyle, QStyleOptionViewItem

from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.ui.track_table_model import (
    ElidedTextDelegate,
    TrackTableModel,
    example_tracks,
    translated_track_status,
)


def test_track_table_model_exposes_artist_title_and_status() -> None:
    model = TrackTableModel(
        [
            Track(artist="Artist", title="Title", status=TrackStatus.SEARCHING),
        ]
    )

    assert model.rowCount() == 1
    assert model.columnCount() == 5
    assert model.headerData(0, Qt.Orientation.Horizontal) == "Artist"
    assert model.headerData(1, Qt.Orientation.Horizontal) == "Title"
    assert model.headerData(2, Qt.Orientation.Horizontal) == "Loved at"
    assert model.headerData(3, Qt.Orientation.Horizontal) == "Status"
    assert model.headerData(4, Qt.Orientation.Horizontal) == "File"
    assert model.data(model.index(0, 0)) == "Artist"
    assert model.data(model.index(0, 1)) == "Title"
    assert model.data(model.index(0, 2)) == ""
    assert model.data(model.index(0, 3)) == "Searching"
    assert model.data(model.index(0, 4)) == ""


def test_track_table_model_returns_user_role_cache_key_and_edit_value() -> None:
    track = Track(artist="Artist", title="Title", status=TrackStatus.QUEUED)
    model = TrackTableModel([track])

    assert model.data(model.index(0, 0), Qt.ItemDataRole.EditRole) == "Artist"
    assert model.data(model.index(0, 0), Qt.ItemDataRole.UserRole) == track.cache_key
    assert model.data(model.index(0, 99)) is None
    assert model._display_value(track, 99) is None


def test_track_table_model_ignores_invalid_indexes_and_parent_rows() -> None:
    model = TrackTableModel([Track(artist="Artist", title="Title")])
    parent = model.index(0, 0)

    assert model.rowCount(parent) == 0
    assert model.columnCount(parent) == 0
    assert model.data(model.index(99, 0)) is None
    assert model.headerData(0, Qt.Orientation.Vertical) is None
    assert model.headerData(0, Qt.Orientation.Horizontal, Qt.ItemDataRole.UserRole) is None
    assert model.flags(model.index(-1, -1)) == Qt.ItemFlag.NoItemFlags


def test_track_table_model_displays_all_known_statuses() -> None:
    statuses = {
        TrackStatus.FETCHED: "Fetched",
        TrackStatus.QUEUED: "Queued",
        TrackStatus.SEARCHING: "Searching",
        TrackStatus.DOWNLOADING: "Downloading",
        TrackStatus.DOWNLOADED: "Downloaded",
        TrackStatus.FAILED: "Failed",
        TrackStatus.NOT_FOUND: "Not found",
    }
    model = TrackTableModel(
        [Track(artist="Artist", title=status.value, status=status) for status in statuses]
    )

    assert [
        model.data(model.index(row, 3))
        for row in range(model.rowCount())
    ] == list(statuses.values())


def test_track_table_model_displays_downloaded_file_details_only() -> None:
    downloaded = Track(
        artist="Artist",
        title="Title",
        local_path="/music/Artist - Title.mp3",
        status=TrackStatus.DOWNLOADED,
        file_type="mp3",
        bitrate_kbps=192,
    )
    extension_fallback = Track(
        artist="Other",
        title="Title",
        local_path="/music/Other - Title.m4a",
        status=TrackStatus.DOWNLOADED,
    )
    queued = Track(
        artist="Queued",
        title="Title",
        local_path="/music/Queued - Title.webm",
        status=TrackStatus.QUEUED,
        file_type="WEBM",
        bitrate_kbps=128,
    )
    model = TrackTableModel([downloaded, extension_fallback, queued])

    assert model.data(model.index(0, 4)) == "MP3, 192 kbps"
    assert model.data(model.index(1, 4)) == "M4A"
    assert model.data(model.index(2, 4)) == ""


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
    assert model.data(model.index(0, 3)) == "Downloaded"


def test_track_table_model_rejects_out_of_range_updates() -> None:
    model = TrackTableModel()

    with pytest.raises(IndexError, match="out of range"):
        model.update_track(0, Track(artist="Artist", title="Title"))


def test_example_tracks_match_mvp_shell() -> None:
    tracks = example_tracks()

    assert [track.status for track in tracks] == [TrackStatus.FETCHED, TrackStatus.QUEUED]


def test_track_table_model_bolds_currently_playing_row() -> None:
    first = Track(artist="Artist", title="First", status=TrackStatus.DOWNLOADED)
    second = Track(artist="Artist", title="Second", status=TrackStatus.DOWNLOADED)
    model = TrackTableModel([first, second])
    changes: list[tuple[int, list[int]]] = []
    model.dataChanged.connect(
        lambda top_left, _bottom_right, roles: changes.append((top_left.row(), list(roles)))
    )

    model.set_playing_track(second.cache_key)

    assert model.playing_cache_key() == second.cache_key
    assert model.data(model.index(0, 0), Qt.ItemDataRole.FontRole) is None
    bold_font = model.data(model.index(1, 0), Qt.ItemDataRole.FontRole)
    assert isinstance(bold_font, QFont)
    assert bold_font.bold()
    assert (1, [int(Qt.ItemDataRole.FontRole)]) in changes

    model.set_playing_track(second.cache_key)
    repeat_count = len(changes)
    model.set_playing_track(second.cache_key)
    assert len(changes) == repeat_count

    model.set_playing_track(None)

    assert model.playing_cache_key() is None
    assert model.data(model.index(1, 0), Qt.ItemDataRole.FontRole) is None


def test_elided_text_delegate_paints_selected_row(qapp) -> None:
    model = TrackTableModel([Track(artist="Artist", title="A very long title")])
    delegate = ElidedTextDelegate()
    pixmap = QPixmap(160, 32)
    pixmap.fill(Qt.GlobalColor.white)
    painter = QPainter(pixmap)
    option = QStyleOptionViewItem()
    option.rect = pixmap.rect()
    option.widget = None
    option.state = QStyle.StateFlag.State_Selected
    option.palette = QApplication.palette()
    option.font = QApplication.font()
    option.fontMetrics = QFontMetrics(option.font)

    try:
        delegate.paint(painter, option, model.index(0, 1))
    finally:
        painter.end()

    assert not pixmap.isNull()


def test_track_table_model_retranslate_emits_header_and_data_changes() -> None:
    model = TrackTableModel([Track(artist="Artist", title="Title")])
    headers: list[tuple[int, int]] = []
    data_roles: list[list[int]] = []
    model.headerDataChanged.connect(
        lambda _orientation, first, last: headers.append((first, last))
    )
    model.dataChanged.connect(
        lambda _top_left, _bottom_right, roles: data_roles.append(list(roles))
    )

    model.retranslate()

    assert headers == [(0, 4)]
    assert [int(Qt.ItemDataRole.DisplayRole)] in data_roles


def test_track_table_model_retranslate_on_empty_model_emits_only_headers() -> None:
    model = TrackTableModel()
    headers: list[tuple[int, int]] = []
    data_changes: list[object] = []
    model.headerDataChanged.connect(
        lambda _orientation, first, last: headers.append((first, last))
    )
    model.dataChanged.connect(lambda *_args: data_changes.append(True))

    model.retranslate()

    assert headers == [(0, 4)]
    assert data_changes == []


def test_track_table_model_header_data_returns_none_for_out_of_range_section() -> None:
    model = TrackTableModel([Track(artist="Artist", title="Title")])

    assert model.headerData(5, Qt.Orientation.Horizontal) is None
    assert model.headerData(99, Qt.Orientation.Horizontal) is None


def test_download_file_details_returns_empty_for_downloaded_track_without_path_extension() -> None:
    track = Track(
        artist="Artist",
        title="Title",
        local_path="/music/no_extension",
        status=TrackStatus.DOWNLOADED,
    )
    model = TrackTableModel([track])

    assert model.data(model.index(0, 4)) == ""


def test_translated_track_status_falls_back_to_status_value() -> None:
    class CustomStatus:
        value = "custom"

    assert translated_track_status(CustomStatus()) == "custom"  # type: ignore[arg-type]

"""Precise contracts of the track table model and its eliding delegate."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from PyQt6.QtCore import QRect, Qt, QTranslator
from PyQt6.QtGui import QColor, QFontMetrics, QPainter, QPalette, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QProxyStyle,
    QStyle,
    QStyleOption,
    QStyleOptionViewItem,
    QWidget,
)

from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.ui.track_table_model import (
    ElidedTextDelegate,
    TrackTableModel,
    translated_track_status,
)


def _tracks(count: int) -> list[Track]:
    return [Track(artist=f"Artist {i}", title=f"Title {i}") for i in range(count)]


def _record_data_changes(model: TrackTableModel) -> list[tuple[int, int, int, int]]:
    changes: list[tuple[int, int, int, int]] = []
    model.dataChanged.connect(
        lambda top_left, bottom_right, _roles: changes.append(
            (top_left.row(), top_left.column(), bottom_right.row(), bottom_right.column())
        )
    )
    return changes


# --- data() bounds -------------------------------------------------------------------


def test_data_returns_none_for_valid_foreign_index_beyond_the_last_row() -> None:
    model = TrackTableModel(_tracks(1))
    bigger = TrackTableModel(_tracks(3))

    assert model.data(bigger.index(1, 0)) is None  # row == len
    assert model.data(bigger.index(2, 0)) is None  # row > len
    assert model.data(bigger.index(0, 0)) == "Artist 0"


# --- update_track / set_playing_track / retranslate ranges ---------------------------


def test_update_track_rejects_row_equal_to_length_with_own_message() -> None:
    model = TrackTableModel(_tracks(1))

    with pytest.raises(IndexError) as excinfo:
        model.update_track(1, Track(artist="A", title="B"))

    assert str(excinfo.value) == "Track row out of range: 1"


def test_update_track_signals_the_full_row() -> None:
    model = TrackTableModel(_tracks(3))
    changes = _record_data_changes(model)

    model.update_track(1, Track(artist="New", title="Row"))

    assert changes == [(1, 0, 1, 4)]


def test_set_playing_track_refreshes_full_previous_and_new_rows() -> None:
    tracks = _tracks(3)
    model = TrackTableModel(tracks)
    model.set_playing_track(tracks[0].cache_key)
    changes = _record_data_changes(model)

    model.set_playing_track(tracks[2].cache_key)

    assert changes == [(0, 0, 0, 4), (2, 0, 2, 4)]


def test_retranslate_signals_every_cell() -> None:
    model = TrackTableModel(_tracks(3))
    changes = _record_data_changes(model)

    model.retranslate()

    assert changes == [(0, 0, 2, 4)]


def test_retranslate_header_signal_depends_on_column_count() -> None:
    class NoColumns(TrackTableModel):
        HEADERS = ()

    class OneColumn(TrackTableModel):
        HEADERS = ("Artist",)

    for model_class, expected in ((NoColumns, []), (OneColumn, [(0, 0)])):
        model = model_class()
        headers: list[tuple[int, int]] = []
        model.headerDataChanged.connect(
            lambda _orientation, first, last, headers=headers: headers.append((first, last))
        )
        model.retranslate()
        assert headers == expected


# --- translations ------------------------------------------------------------------


class _MarkingTranslator(QTranslator):
    def translate(self, context, source_text, disambiguation=None, n=-1):  # noqa: ARG002
        if context == "TrackTableModel":
            return f"<{source_text}>"
        return None


@pytest.fixture
def marking_translator(qapp) -> Iterator[None]:
    translator = _MarkingTranslator()
    qapp.installTranslator(translator)
    try:
        yield
    finally:
        qapp.removeTranslator(translator)


@pytest.mark.usefixtures("marking_translator")
@pytest.mark.parametrize("status", list(TrackStatus))
def test_translated_track_status_goes_through_the_translator(status: TrackStatus) -> None:
    assert translated_track_status(status) == f"<{status.value}>"


# --- file details -------------------------------------------------------------------


def test_file_type_from_extension_only_strips_the_leading_dot() -> None:
    track = Track(
        artist="Artist",
        title="Title",
        local_path="/music/song.XM",
        status=TrackStatus.DOWNLOADED,
    )
    model = TrackTableModel([track])

    assert model.data(model.index(0, 4)) == "XM"


# --- delegate -----------------------------------------------------------------------


class _RecordingStyle(QProxyStyle):
    def __init__(self) -> None:
        super().__init__()
        self.draw_calls: list[tuple[object, str | None, object]] = []
        self.sub_rect_calls: list[tuple[object, bool, object]] = []

    def drawControl(self, element, option, painter, widget=None):  # noqa: N802
        text = option.text if isinstance(option, QStyleOptionViewItem) else None
        self.draw_calls.append((element, text, widget))
        if option is not None:
            super().drawControl(element, option, painter, widget)

    def subElementRect(self, element, option, widget=None):  # noqa: N802
        self.sub_rect_calls.append((element, isinstance(option, QStyleOption), widget))
        return QRect(2, 2, 150, 28)


class _RecordingPainter(QPainter):
    def __init__(self, device: QPixmap) -> None:
        super().__init__(device)
        self.pens: list[QColor] = []
        self.texts: list[tuple[QRect, int, str]] = []

    def setPen(self, color) -> None:  # type: ignore[override]  # noqa: N802
        self.pens.append(QColor(color))
        super().setPen(color)

    def drawText(self, rect, flags, text) -> None:  # type: ignore[override]  # noqa: N802
        self.texts.append((QRect(rect), int(flags), text))
        super().drawText(rect, flags, text)


def _paint(state: QStyle.StateFlag) -> tuple[_RecordingStyle, _RecordingPainter, QWidget]:
    widget = QWidget()
    style = _RecordingStyle()
    widget.setStyle(style)
    model = TrackTableModel([Track(artist="Artist", title="Title")])
    palette = QPalette(QApplication.palette())
    palette.setColor(QPalette.ColorRole.Text, QColor("#102030"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#A0B0C0"))
    option = QStyleOptionViewItem()
    option.rect = QRect(0, 0, 160, 32)
    option.widget = widget
    option.state = state
    option.palette = palette
    option.font = QApplication.font()
    option.fontMetrics = QFontMetrics(option.font)
    pixmap = QPixmap(160, 32)
    painter = _RecordingPainter(pixmap)
    try:
        ElidedTextDelegate().paint(painter, option, model.index(0, 1))
    finally:
        painter.end()
    return style, painter, widget


def test_delegate_uses_widget_style_with_blank_text_and_widget(qapp) -> None:
    style, painter, widget = _paint(QStyle.StateFlag.State_Enabled)

    assert style.draw_calls == [(QStyle.ControlElement.CE_ItemViewItem, "", widget)]
    # The base style queries sub-rects itself while drawing; the delegate's own query is last.
    assert style.sub_rect_calls[-1] == (QStyle.SubElement.SE_ItemViewItemText, True, widget)
    assert painter.texts == [
        (
            QRect(2, 2, 150, 28),
            int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
            "Title",
        )
    ]


def test_delegate_pen_follows_selection_state(qapp) -> None:
    _style, unselected, _w1 = _paint(QStyle.StateFlag.State_Enabled)
    _style, selected, _w2 = _paint(QStyle.StateFlag.State_Selected)

    assert [c.name() for c in unselected.pens] == ["#102030"]
    assert [c.name() for c in selected.pens] == ["#a0b0c0"]

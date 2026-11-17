"""Behaviour pins for ``my_lastfm_player.ui.main_window`` found by mutation testing.

Each test asserts an exact, user-visible effect (widget state, texts, emitted signals,
layout positions) that a small change to the window code would alter.
"""

from __future__ import annotations

import types
from collections.abc import Iterator
from dataclasses import replace
from html import escape
from math import ceil

import pytest
from PyQt6.QtCore import QBuffer, QByteArray, QEvent, QIODevice, QPointF, QSize, Qt, QTime
from PyQt6.QtGui import (
    QColor,
    QImage,
    QKeyEvent,
    QMouseEvent,
    QPalette,
    QPixmap,
    QResizeEvent,
    QStandardItemModel,
    QTextDocument,
)
from PyQt6.QtWidgets import (
    QApplication,
    QDialogButtonBox,
    QGridLayout,
    QHeaderView,
    QLabel,
    QTextBrowser,
    QWidget,
)

from my_lastfm_player import __display_version__
from my_lastfm_player.i18n import TranslationManager
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.ui import main_window as mw
from my_lastfm_player.ui.main_window import (
    ArtistImageLabel,
    ElidedLabel,
    MainWindow,
    TrackFilterProxyModel,
    UnloveAvailability,
    format_feedback_message,
    shorten_error,
)
from my_lastfm_player.ui.track_table_model import (
    ElidedTextDelegate,
    TrackTableModel,
    translated_track_status,
)

PARAGRAPH = '<p style="margin: 0 0 8px 0;">'


def _png_bytes(*colors: str) -> bytes:
    """Return a PNG one pixel high with one pixel per colour."""

    image = QImage(len(colors), 1, QImage.Format.Format_RGB32)
    for x_position, color in enumerate(colors):
        image.setPixelColor(x_position, 0, QColor(color))
    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(data)


def _press(x_position: float, y_position: float = 10) -> QMouseEvent:
    return QMouseEvent(
        QEvent.Type.MouseButtonPress,
        QPointF(x_position, y_position),
        QPointF(x_position, y_position),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )


def _key(key: Qt.Key) -> QKeyEvent:
    return QKeyEvent(QEvent.Type.KeyPress, key, Qt.KeyboardModifier.NoModifier)


@pytest.fixture
def translation_manager(qapp) -> Iterator[TranslationManager]:
    manager = TranslationManager(qapp)
    yield manager
    manager.set_language("en")


# --- module helpers -------------------------------------------------------------


class _FakeGeometry:
    def height(self) -> int:
        return 1234


class _FakeScreen:
    def availableGeometry(self) -> _FakeGeometry:  # noqa: N802 - Qt naming
        return _FakeGeometry()


def test_available_screen_height_uses_the_widget_screen(qapp) -> None:
    widget = types.SimpleNamespace(screen=_FakeScreen)

    assert mw._available_screen_height(widget) == 1234  # type: ignore[arg-type]


def test_html_paragraphs_are_concatenated_without_separator() -> None:
    assert mw._html_paragraphs(["a", "b"]) == f"{PARAGRAPH}a</p>{PARAGRAPH}b</p>"


def test_feedback_timestamp_is_24_hour_with_seconds() -> None:
    assert format_feedback_message("hi", QTime(13, 5, 9)) == "13:05:09: hi"


def test_shorten_error_strips_trailing_space_before_the_ellipsis() -> None:
    assert shorten_error("abc def", max_length=5) == "abc…"


def test_rich_text_dialog_width_switches_only_above_the_threshold() -> None:
    threshold = mw.RICH_TEXT_DIALOG_WIDE_THRESHOLD
    assert mw._rich_text_dialog_width("x" * threshold) == mw.RICH_TEXT_DIALOG_WIDTH
    assert mw._rich_text_dialog_width("x" * (threshold + 1)) == mw.RICH_TEXT_DIALOG_WIDE_WIDTH


def _reference_height(font, text: str, text_width: int) -> int:
    document = QTextDocument()
    document.setDefaultFont(font)
    document.setDocumentMargin(0)
    document.setHtml(text)
    document.setTextWidth(text_width)
    return ceil(document.size().height()) + mw.RICH_TEXT_DIALOG_CONTENT_PADDING


def test_rich_text_content_height_measures_at_the_reserved_text_width(qapp) -> None:
    browser = QTextBrowser()
    font = browser.font()
    dialog_width = mw.RICH_TEXT_DIALOG_WIDTH
    scrollbar_extent = 10
    text_width = dialog_width - 2 * mw.RICH_TEXT_DIALOG_MARGIN - scrollbar_extent
    # A paragraph whose line count changes when the width shrinks by one margin.
    text = next(
        (
            candidate
            for candidate in (f"<p>{'word ' * count}</p>" for count in range(1, 400))
            if _reference_height(font, candidate, text_width)
            != _reference_height(font, candidate, text_width - mw.RICH_TEXT_DIALOG_MARGIN)
        ),
        None,
    )
    if text is None:
        # Headless runners without real fonts measure every paragraph alike.
        pytest.skip("platform font metrics cannot distinguish the two text widths")

    assert mw._rich_text_content_height(
        browser, text, dialog_width, scrollbar_extent
    ) == _reference_height(font, text, text_width)


def test_rich_text_dialog_layout_and_size(qapp, monkeypatch) -> None:
    dialogs: list = []
    monkeypatch.setattr(mw.QDialog, "exec", lambda self: dialogs.append(self) or 0)
    parent = QWidget()
    text = "<p>Hello <b>world</b></p>"

    mw._show_rich_text_dialog(parent, "Title", text)

    dialog = dialogs[0]
    assert dialog.parent() is parent
    assert dialog.windowTitle() == "Title"
    layout = dialog.layout()
    assert layout.count() == 2
    browser = layout.itemAt(0).widget()
    assert isinstance(browser, QTextBrowser)
    assert browser.isReadOnly()
    assert browser.document().documentMargin() == 0
    assert browser.toPlainText() == "Hello world"
    assert layout.stretch(0) == 1
    button_box = layout.itemAt(1).widget()
    assert isinstance(button_box, QDialogButtonBox)
    assert button_box.standardButtons() == QDialogButtonBox.StandardButton.Ok
    chrome_height = (
        2 * mw.RICH_TEXT_DIALOG_MARGIN
        + mw.RICH_TEXT_DIALOG_SPACING
        + button_box.sizeHint().height()
    )
    content_height = _reference_height(
        browser.font(),
        text,
        mw.RICH_TEXT_DIALOG_WIDTH - 2 * mw.RICH_TEXT_DIALOG_MARGIN - mw._scrollbar_extent(dialog),
    )
    assert dialog.width() == mw.RICH_TEXT_DIALOG_WIDTH
    assert dialog.height() == content_height + chrome_height


# --- ElidedLabel / ArtistImageLabel / TrackFilterProxyModel ----------------------


def test_elided_label_construction_defaults(qapp) -> None:
    parent = QWidget()
    label = ElidedLabel(parent)

    assert label.parent() is parent
    assert label.full_text() == ""
    assert label.minimumWidth() == 0
    assert label.minimumSizeHint().width() == 0


def test_elided_label_resize_event_reelides(qapp) -> None:
    label = ElidedLabel()
    label.resize(40, 20)
    label.setText("A very long label text that cannot fit")

    label.resize(400, 20)
    label.resizeEvent(QResizeEvent(QSize(400, 20), QSize(40, 20)))

    assert label.text() == "A very long label text that cannot fit"
    assert label.toolTip() == ""


def test_artist_image_scales_smoothly_to_the_label(qapp) -> None:
    image_bytes = _png_bytes("#ff0000", "#0000ff")
    source = QPixmap()
    assert source.loadFromData(image_bytes)
    smooth = source.scaled(
        QSize(mw.ARTIST_IMAGE_SIZE, mw.ARTIST_IMAGE_SIZE),
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    ).toImage()
    fast = source.scaled(
        QSize(mw.ARTIST_IMAGE_SIZE, mw.ARTIST_IMAGE_SIZE),
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.FastTransformation,
    ).toImage()
    assert smooth != fast
    label = ArtistImageLabel()

    label.set_artist_image(image_bytes, None)

    assert label.pixmap().toImage() == smooth
    assert label.focusPolicy() == Qt.FocusPolicy.NoFocus
    label.resizeEvent(QResizeEvent(label.size(), label.size()))
    assert label.pixmap().toImage() == smooth


@pytest.mark.parametrize(
    ("width", "height", "scaled"),
    [(0, 50, False), (50, 0, False), (1, 50, True), (50, 1, True)],
)
def test_artist_image_skips_scaling_only_for_empty_sizes(qapp, width, height, scaled) -> None:
    label = ArtistImageLabel()
    label.setFixedSize(width, height)
    calls: list = []
    label.setPixmap = calls.append  # type: ignore[method-assign]

    label.set_artist_image(_png_bytes("#ff0000", "#0000ff"), "https://last.fm/a")

    assert bool(calls) is scaled


def test_artist_image_page_url_requires_an_image(qapp) -> None:
    label = ArtistImageLabel()
    requested: list[str] = []
    label.artist_page_requested.connect(requested.append)

    label.set_artist_image(None, "https://last.fm/a")
    label.keyPressEvent(_key(Qt.Key.Key_Return))
    label.mousePressEvent(_press(4, 4))

    assert requested == []


def test_artist_image_without_page_url_ignores_activation_keys(qapp) -> None:
    label = ArtistImageLabel()
    requested: list[str] = []
    label.artist_page_requested.connect(requested.append)
    label.set_artist_image(_png_bytes("#ff0000"), None)

    label.keyPressEvent(_key(Qt.Key.Key_Return))

    assert requested == []


def test_artist_image_passes_other_keys_to_qlabel(qapp) -> None:
    label = ArtistImageLabel()
    requested: list[str] = []
    label.artist_page_requested.connect(requested.append)
    label.set_artist_image(_png_bytes("#ff0000"), "https://last.fm/a")
    event = _key(Qt.Key.Key_A)

    label.keyPressEvent(event)

    assert requested == []
    assert not event.isAccepted()
    assert label.focusPolicy() == Qt.FocusPolicy.StrongFocus


def test_track_filter_proxy_keeps_parent_and_ignores_missing_errors(qapp) -> None:
    parent = QWidget()
    proxy = TrackFilterProxyModel(parent)
    model = TrackTableModel()
    model.set_tracks([Track(artist="Artist", title="Title")])
    proxy.setSourceModel(model)

    proxy.set_track_filter_text("xxxx")

    assert proxy.parent() is parent
    assert proxy.rowCount() == 0


# --- MainWindow construction -------------------------------------------------------


def _grid_positions(layout: QGridLayout, widgets: dict[str, QWidget]) -> dict:
    return {
        name: tuple(layout.getItemPosition(layout.indexOf(widget)))
        for name, widget in widgets.items()
    }


def test_source_panel_grid(qapp) -> None:
    window = MainWindow()
    layout = window.username_label.parentWidget().layout()
    assert isinstance(layout, QGridLayout)

    assert _grid_positions(
        layout,
        {
            "username_label": window.username_label,
            "username_input": window.username_input,
            "fetch": window.fetch_button,
            "pause": window.fetch_pause_button,
            "stop": window.fetch_stop_button,
            "count": window.track_count_label,
            "dependency": window.dependency_label,
            "youtube": window.youtube_work_button,
        },
    ) == {
        "username_label": (0, 0, 1, 1),
        "username_input": (0, 1, 1, 1),
        "fetch": (0, 2, 1, 1),
        "pause": (0, 3, 1, 1),
        "stop": (0, 4, 1, 1),
        "count": (1, 0, 1, 1),
        "dependency": (1, 1, 1, 3),
        "youtube": (1, 4, 1, 1),
    }
    assert [layout.columnStretch(column) for column in range(5)] == [0, 1, 0, 0, 0]


def test_feedback_panel_grid(qapp) -> None:
    window = MainWindow()
    layout = window.discovery_progress_label.parentWidget().layout().itemAt(0).layout()
    assert isinstance(layout, QGridLayout)

    assert _grid_positions(
        layout,
        {
            "discovery_label": window.discovery_progress_label,
            "discovery_bar": window.discovery_progress_bar,
            "lookup_label": window.lookup_progress_label,
            "lookup_bar": window.lookup_progress_bar,
            "download_label": window.download_progress_label,
            "download_bar": window.download_progress_bar,
            "clear": window.clear_feedback_button,
        },
    ) == {
        "discovery_label": (0, 0, 1, 1),
        "discovery_bar": (0, 1, 1, 1),
        "lookup_label": (1, 0, 1, 1),
        "lookup_bar": (1, 1, 1, 1),
        "download_label": (2, 0, 1, 1),
        "download_bar": (2, 1, 1, 1),
        "clear": (0, 2, 3, 1),
    }
    assert [layout.columnStretch(column) for column in range(3)] == [0, 1, 0]
    assert layout.horizontalSpacing() == 8
    assert layout.verticalSpacing() == 4


def test_controls_panel_and_status_bar_details(qapp) -> None:
    window = MainWindow()

    assert window.artist_image_group.layout().itemAt(0).alignment() == (
        Qt.AlignmentFlag.AlignCenter
    )
    assert window.playback_slider.minimumWidth() == 280
    assert window.total_time_label.minimumWidth() == 48
    assert window.error_indicator_label.styleSheet() == f"color: {mw.ERROR_TEXT_COLOR};"
    assert window._new_progress_bar().format() == "Idle — %p%"


def test_track_table_header_delegates_and_proxy_parent(qapp) -> None:
    window = MainWindow()
    header = window.track_table.horizontalHeader()
    stretch = QHeaderView.ResizeMode.Stretch
    fit = QHeaderView.ResizeMode.ResizeToContents

    assert [header.sectionResizeMode(column) for column in range(5)] == [
        stretch,
        stretch,
        fit,
        fit,
        fit,
    ]
    assert window.track_table.verticalHeader().isHidden()
    assert window.track_sort_model.parent() is window
    delegate = window.track_table.itemDelegateForColumn(0)
    assert isinstance(delegate, ElidedTextDelegate)
    assert delegate.parent() is window.track_table
    assert window.track_table.itemDelegateForColumn(1) is delegate
    assert window.track_table.itemDelegateForColumn(2) is None

    # Columns the default model does not have keep Qt's interactive default mode.
    window.track_table.setModel(QStandardItemModel(1, 7))
    assert [header.sectionResizeMode(column) for column in (5, 6)] == [
        QHeaderView.ResizeMode.Interactive,
        QHeaderView.ResizeMode.Interactive,
    ]


# --- context menu, retry and unlove ------------------------------------------------


def _open_context_menu(window: MainWindow, monkeypatch) -> dict:
    seen: dict = {}

    def fake_exec(menu, _global_pos):
        actions = [action for action in menu.actions() if not action.isSeparator()]
        seen["menu_parent"] = menu.parent()
        seen["tooltips_visible"] = menu.toolTipsVisible()
        seen["actions"] = [
            (action.text(), action.toolTip(), action.parent() is menu) for action in actions
        ]
        return None

    monkeypatch.setattr(mw.QMenu, "exec", fake_exec)
    window._show_track_context_menu(
        window.track_table.visualRect(window.track_sort_model.index(0, 0)).center()
    )
    return seen


def test_context_menu_structure_for_failed_track(qapp, monkeypatch) -> None:
    window = MainWindow()
    window.set_tracks([Track(artist="Artist", title="Title", status=TrackStatus.FAILED)])
    window.set_unlove_availability_provider(
        lambda: UnloveAvailability(enabled=True, reason="unused", account="me")
    )

    seen = _open_context_menu(window, monkeypatch)

    assert seen == {
        "menu_parent": window,
        "tooltips_visible": True,
        "actions": [
            ("Retry YouTube Check", "Search YouTube again for the selected track", True),
            (
                "Unlove on Last.fm…",
                "Remove this track from your loved tracks on Last.fm",
                True,
            ),
        ],
    }


def test_context_menu_retry_download_tooltip(qapp, monkeypatch) -> None:
    window = MainWindow()
    window.set_tracks(
        [
            Track(
                artist="Artist",
                title="Title",
                status=TrackStatus.FAILED,
                youtube_url="https://youtu.be/example",
            )
        ]
    )

    seen = _open_context_menu(window, monkeypatch)

    assert seen["actions"][0] == (
        "Retry Download",
        "Download the selected YouTube result again",
        True,
    )


@pytest.mark.parametrize(
    ("track", "text", "tooltip"),
    [
        (
            Track(artist="A", title="T", status=TrackStatus.NOT_FOUND),
            "Retry YouTube Check",
            "Search YouTube again for the selected track",
        ),
        (
            Track(
                artist="A",
                title="T",
                status=TrackStatus.FAILED,
                youtube_url="https://youtu.be/example",
            ),
            "Retry Download",
            "Download the selected YouTube result again",
        ),
    ],
)
def test_retry_button_reflects_selected_failed_track(qapp, track, text, tooltip) -> None:
    window = MainWindow()
    window.set_tracks([track])

    window.select_track_row(0)

    assert window.retry_selected_button.isEnabled()
    assert window.retry_selected_button.text() == text
    assert window.retry_selected_button.toolTip() == tooltip


def _capture_unlove_dialog(window: MainWindow, monkeypatch, track: Track) -> dict:
    seen: dict = {}

    def fake_exec(dialog):
        seen["parent"] = dialog.parent()
        seen["title"] = dialog.windowTitle()
        seen["text"] = dialog.text()
        return 0

    monkeypatch.setattr(mw.QMessageBox, "exec", fake_exec)
    seen["result"] = window._confirm_unlove(track, "me")
    return seen


def test_unlove_dialog_without_loved_date(qapp, monkeypatch) -> None:
    window = MainWindow()

    seen = _capture_unlove_dialog(window, monkeypatch, Track(artist="Artist", title="Title"))

    assert seen == {
        "parent": window,
        "title": "Unlove on Last.fm?",
        "text": (
            "This WRITES TO YOUR LAST.FM ACCOUNT (me).\n\n"
            '"Artist – Title" will be removed from your loved tracks on last.fm.'
        ),
        "result": False,
    }


def test_unlove_dialog_with_loved_date(qapp, monkeypatch) -> None:
    window = MainWindow()

    seen = _capture_unlove_dialog(
        window, monkeypatch, Track(artist="Artist", title="Title", loved_at="2026-09-01")
    )

    assert seen["text"] == (
        "This WRITES TO YOUR LAST.FM ACCOUNT (me).\n\n"
        '"Artist – Title" will be removed from your loved tracks on last.fm.'
        "\nLoved on: 2026-09-01"
    )


# --- focus handling ----------------------------------------------------------------


def test_space_shortcut_follows_focus(qapp) -> None:
    window = MainWindow()
    shortcut = window.play_pause_shortcut

    window._update_playback_shortcut_for_focus(None, window.username_input)
    assert not shortcut.isEnabled()
    window._update_playback_shortcut_for_focus(None, window.track_table)
    assert shortcut.isEnabled()
    window._update_playback_shortcut_for_focus(None, window.artist_image_label)
    assert not shortcut.isEnabled()
    window._update_playback_shortcut_for_focus(None, None)
    assert shortcut.isEnabled()


def test_space_shortcut_focus_update_tolerates_a_partly_built_window(qapp) -> None:
    states: list[bool] = []
    partial = types.SimpleNamespace(
        play_pause_shortcut=types.SimpleNamespace(setEnabled=states.append)
    )

    MainWindow._update_playback_shortcut_for_focus(partial, None, QLabel())  # type: ignore[arg-type]

    assert states == [True]


# --- playback timeline -------------------------------------------------------------


def test_timeline_seek_needs_only_a_positive_duration(qapp) -> None:
    window = MainWindow()
    seeks: list[int] = []
    window.seek_requested.connect(seeks.append)

    window.set_playback_timeline(0, 1)
    window._emit_timeline_seek()

    assert seeks == [0]


def _sized_timeline(window: MainWindow, width: int, duration: int) -> None:
    window.playback_slider.setMinimumWidth(0)
    window.playback_slider.resize(width, 30)
    window.set_playback_timeline(0, duration)


def test_timeline_value_for_x_position(qapp) -> None:
    window = MainWindow()
    _sized_timeline(window, 200, 10_000)

    assert window._timeline_value_for_x_position(-5) == 0
    assert window._timeline_value_for_x_position(100) == 5_000
    assert window._timeline_value_for_x_position(500) == 10_000

    window.playback_slider.resize(1, 30)
    assert window._timeline_value_for_x_position(1) == 10_000


def test_timeline_click_seeks_only_with_a_positive_duration(qapp) -> None:
    window = MainWindow()
    seeks: list[int] = []
    window.seek_requested.connect(seeks.append)

    _sized_timeline(window, 200, 0)
    assert window.eventFilter(window.playback_slider, _press(100)) is False
    assert seeks == []

    _sized_timeline(window, 200, 1)
    assert window.eventFilter(window.playback_slider, _press(150)) is True
    assert seeks == [1]


def test_timeline_click_inside_a_styled_handle_is_left_to_the_slider(qapp) -> None:
    window = MainWindow()
    seeks: list[int] = []
    window.seek_requested.connect(seeks.append)
    window.playback_slider.setStyleSheet(
        "QSlider::groove:horizontal { background: #888; height: 6px; border: 1px solid #333; }"
        "QSlider::handle:horizontal { background: #fff; width: 80px; margin: -4px 0; }"
    )
    _sized_timeline(window, 300, 10_000)

    assert window.eventFilter(window.playback_slider, _press(50, 15)) is False
    assert seeks == []


def test_timeline_event_filter_is_installed_on_the_slider(qapp) -> None:
    window = MainWindow()
    seeks: list[int] = []
    window.seek_requested.connect(seeks.append)
    _sized_timeline(window, 300, 10_000)

    QApplication.sendEvent(window.playback_slider, _press(150, 15))

    assert seeks == [5_000]
    assert window.playback_slider.value() == 5_000


def test_set_playback_timeline_bounds_enables_and_stays_silent(qapp) -> None:
    window = MainWindow()
    values: list[int] = []
    window.playback_slider.valueChanged.connect(values.append)

    window.set_playback_timeline(-5, 1_000)
    assert window.playback_slider.value() == 0
    window.set_playback_timeline(500, 1_000)
    window.set_playback_timeline(0, 1_000)
    assert window.playback_slider.value() == 0
    assert values == []

    window.set_playback_timeline(0, 0)
    assert not window.playback_slider.isEnabled()
    window.set_playback_timeline(0, 1)
    assert window.playback_slider.isEnabled()


# --- silent setters --------------------------------------------------------------


def test_silent_setters_restore_signal_delivery(qapp) -> None:
    window = MainWindow()
    randomize: list[bool] = []
    volumes: list[int] = []
    mutes: list[bool] = []
    window.randomize_playback_changed.connect(randomize.append)
    window.volume_changed.connect(volumes.append)
    window.mute_toggled.connect(mutes.append)

    window.set_randomize_playback(True)
    window.set_volume_percent(40)
    window.set_muted(True)
    assert (randomize, volumes, mutes) == ([], [], [])

    window.randomize_checkbox.setChecked(False)
    window.volume_slider.setValue(50)
    window.mute_checkbox.setChecked(False)
    assert (randomize, volumes, mutes) == ([False], [50], [False])


def test_fetch_control_state_defaults_and_resume_texts(qapp) -> None:
    window = MainWindow()

    window.set_fetch_control_state(True)
    assert window.fetch_pause_button.isEnabled()
    assert window.fetch_pause_button.text() == "Pause"
    assert window.fetch_pause_button.toolTip() == "Pause the active Last.fm fetch"

    window.set_fetch_control_state(True, True)
    assert window.fetch_pause_button.text() == "Resume"
    assert window.fetch_pause_button.toolTip() == "Resume the paused Last.fm fetch"


def test_dependency_status_property_drives_the_style(qapp) -> None:
    window = MainWindow()
    window.setStyleSheet(
        'QLabel[status="missing"] { color: #ff0000; } QLabel[status="ok"] { color: #00ff00; }'
    )
    label = window.dependency_label

    window.set_dependency_status(False, "missing tools")
    assert label.property("status") == "missing"
    assert label.palette().color(QPalette.ColorRole.WindowText).name() == "#ff0000"

    window.set_dependency_status(True, "all good")
    assert label.property("status") == "ok"
    assert label.palette().color(QPalette.ColorRole.WindowText).name() == "#00ff00"
    assert label.text() == "all good"


# --- tracks and status -------------------------------------------------------------


def test_set_tracks_keeps_current_column_and_reports_count(qapp) -> None:
    window = MainWindow()
    tracks = [Track(artist="A", title="One"), Track(artist="B", title="Two")]
    window.set_tracks(tracks)
    window.track_table.setCurrentIndex(window.track_sort_model.index(1, 0))
    window.track_table.selectRow(1)

    window.set_tracks(tracks)

    assert window.track_table.currentIndex().column() == 0
    assert window.statusBar().currentMessage() == "Loaded 2 tracks"


def test_update_track_reports_artist_title_and_status(qapp) -> None:
    window = MainWindow()
    track = Track(artist="Artist", title="Title")
    window.set_tracks([track])

    window.update_track(0, replace(track, status=TrackStatus.DOWNLOADED))

    status = translated_track_status(TrackStatus.DOWNLOADED)
    assert window.statusBar().currentMessage() == f"Updated Artist - Title: {status}"


def test_set_now_playing_none_shows_not_playing(qapp) -> None:
    window = MainWindow()
    window.set_now_playing(Track(artist="A", title="T"))

    window.set_now_playing(None)

    assert window.now_playing_label.full_text() == "Not playing"


def test_retranslate_keeps_artist_title_and_custom_status(qapp) -> None:
    window = MainWindow()
    window.set_artist_image(_png_bytes("#ff0000"), "https://last.fm/a", "Björk")
    window.show_status("Hello")

    window.retranslate_ui()

    assert window.artist_image_group.title() == "Artist: Björk"
    assert window.statusBar().currentMessage() == "Hello"


# --- language switching ------------------------------------------------------------


def _bar_formats(window: MainWindow) -> list[str]:
    return [
        window.discovery_progress_bar.format(),
        window.lookup_progress_bar.format(),
        window.download_progress_bar.format(),
    ]


def test_language_switch_retranslates_idle_state(qapp, translation_manager) -> None:
    window = MainWindow(translation_manager)
    window.set_now_playing(Track(artist="A", title="T"))
    window.set_now_playing(None)

    window.set_language("de")

    assert _bar_formats(window) == ["Leerlauf — %p%"] * 3
    assert window.statusBar().currentMessage() == "Bereit"
    assert window.now_playing_label.full_text() == "Es läuft nichts"
    assert {code: action.isChecked() for code, action in window.language_actions.items()} == {
        code: code == "de" for code in window.language_actions
    }


def test_reset_workflow_progress_marks_stages_idle_for_retranslation(
    qapp, translation_manager
) -> None:
    window = MainWindow(translation_manager)
    for stage in ("discovery", "lookup", "download"):
        window.set_stage_progress(stage, 50, "Working")

    window.reset_workflow_progress()
    window.set_language("de")

    assert _bar_formats(window) == ["Leerlauf — %p%"] * 3


# --- dialog texts ------------------------------------------------------------------


def _paragraphs(html: str) -> list[str]:
    assert html.startswith(PARAGRAPH)
    assert html.endswith("</p>")
    return html[len(PARAGRAPH) : -len("</p>")].split(f"</p>{PARAGRAPH}")


def test_about_dialog_text(qapp) -> None:
    paragraphs = _paragraphs(MainWindow().about_dialog_text())

    assert len(paragraphs) == 6
    assert paragraphs[0] == f"<b>{escape(f'myLastFmPlayer {__display_version__}')}</b>"
    assert paragraphs[2:] == [
        "License: GNU GPLv3 or later.",
        "This application fetches a user's public loved tracks from Last.fm, "
        "keeps local metadata, resolves playable sources through yt-dlp, "
        "downloads the best available audio, and plays it locally.",
        "It is intended as a practical Linux desktop helper for rebuilding "
        "a personal loved-track collection without manually searching every song.",
        "Optional Last.fm scrobbling can connect the local playback workflow "
        "back to the user's Last.fm account.",
    ]


LICENSES = [
    ("Python", "Python Software Foundation License; runtime for the application."),
    ("PyQt6", "GNU GPL v3; Python bindings for the Qt desktop interface."),
    ("Qt 6", "GNU LGPL v3 / GPL v3; cross-platform UI toolkit."),
    ("requests", "Apache License 2.0; HTTP client for Last.fm API calls."),
    ("pylast", "Apache License 2.0; Last.fm scrobbling integration."),
    ("yt-dlp", "Unlicense; media lookup and download helper."),
    (
        "FFmpeg",
        "LGPL/GPL family licenses depending on the installed build; audio conversion backend.",
    ),
]


def test_open_source_licenses_dialog_text(qapp) -> None:
    paragraphs = _paragraphs(MainWindow().open_source_licenses_dialog_text())

    assert paragraphs == [
        "myLastFmPlayer is GPLv3-or-later software and uses these open-source "
        "libraries and external tools:",
        *(f"<b>{name}</b> - {text}" for name, text in LICENSES),
        "Development tools include <b>pytest</b>, <b>pytest-cov</b>, <b>coverage.py</b>, "
        "<b>Ruff</b>, <b>Pylint</b>, <b>Sphinx</b>, <b>build</b> under their respective "
        "open-source licenses.",
        "This summary is informational; the complete license texts are provided "
        "by the installed projects and system packages.",
    ]


def test_open_source_licenses_plain_text(qapp) -> None:
    assert MainWindow().open_source_licenses_plain_text() == "\n\n".join(
        f"{name} - {text}" for name, text in LICENSES
    )

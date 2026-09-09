from __future__ import annotations

import runpy
import sys
import types
from dataclasses import replace

import pytest
from PyQt6.QtCore import (
    QBuffer,
    QByteArray,
    QEvent,
    QIODevice,
    QModelIndex,
    QPoint,
    QPointF,
    QSettings,
    Qt,
    QTime,
)
from PyQt6.QtGui import QColor, QKeySequence, QMouseEvent, QPixmap, QStandardItemModel
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QSizePolicy, QStyle, QStyleOptionSlider

from my_lastfm_player import __display_version__, __version__
from my_lastfm_player import main as main_module
from my_lastfm_player.i18n import SUPPORTED_LANGUAGES, TranslationManager
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.settings import AppSettings
from my_lastfm_player.themes import ThemeMode
from my_lastfm_player.ui import main_window as main_window_module
from my_lastfm_player.ui.main_window import (
    ERROR_TEXT_COLOR,
    ArtistImageLabel,
    MainWindow,
    TrackFilterProxyModel,
    application_title,
    format_feedback_message,
    format_playback_time,
    format_progress_text,
    shorten_error,
)
from my_lastfm_player.version import display_version


def png_bytes() -> bytes:
    image = QPixmap(1, 1)
    image.fill(QColor("#336699"))
    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(data)


def test_package_version_is_defined() -> None:
    assert __version__ == "0.0.172"
    assert __display_version__ == "0.0.172"


def test_display_version_adds_build_commit_suffix() -> None:
    assert display_version("1.2.3", "abcdef123") == "1.2.3+abcdef"
    assert display_version("1.2.3", "") == "1.2.3"


def test_display_version_loads_generated_build_info(monkeypatch) -> None:
    fake_build_info = types.SimpleNamespace(__commit__="123456789")
    monkeypatch.setitem(sys.modules, "my_lastfm_player._build_info", fake_build_info)

    assert display_version("1.2.3") == "1.2.3+123456"


def test_display_version_ignores_non_string_build_commit(monkeypatch) -> None:
    fake_build_info = types.SimpleNamespace(__commit__=123456)
    monkeypatch.setitem(sys.modules, "my_lastfm_player._build_info", fake_build_info)

    assert display_version("1.2.3") == "1.2.3"


def test_python_module_entrypoint_exits_with_main_return_code(monkeypatch) -> None:
    fake_main_module = types.ModuleType("my_lastfm_player.main")
    fake_main_module.main = lambda: 7
    monkeypatch.setitem(sys.modules, "my_lastfm_player.main", fake_main_module)

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_module("my_lastfm_player.__main__", run_name="__main__")

    assert exc_info.value.code == 7


def test_main_window_builds_mvp_shell(qapp) -> None:
    window = MainWindow()

    assert qapp.applicationName() in {"", "myLastFmPlayer"}
    assert window.windowTitle() == f"myLastFmPlayer v{__display_version__}"
    assert window.username_input.placeholderText() == "Enter username"
    assert window.track_model.columnCount() == 5
    assert window.track_model.rowCount() == 0
    assert window.progress_bar.format() == "Idle — %p%"
    assert window.fetch_pause_button.text() == "Pause"
    assert window.fetch_stop_button.text() == "Stop"
    assert not window.fetch_pause_button.isEnabled()
    assert not window.fetch_stop_button.isEnabled()
    assert window.fetch_pause_button.toolTip()
    assert window.fetch_stop_button.toolTip()


def test_main_window_menu_actions_have_icons(qapp) -> None:
    window = MainWindow()

    assert not window.preferences_action.icon().isNull()
    assert not window.file_cache_action.icon().isNull()
    assert not window.quit_action.icon().isNull()
    assert not window.theme_menu.icon().isNull()
    assert not window.theme_light_action.icon().isNull()
    assert not window.theme_dark_action.icon().isNull()
    assert not window.theme_lilac_action.icon().isNull()
    assert not window.theme_mint_action.icon().isNull()


def test_application_title_includes_version_suffix() -> None:
    assert application_title("1.2.3+abcdef") == "myLastFmPlayer v1.2.3+abcdef"


def test_main_prints_version_at_startup(monkeypatch, capsys) -> None:
    saved_languages: list[str] = []
    saved_themes: list[ThemeMode] = []
    applied_themes: list[ThemeMode] = []
    selected_themes: list[str] = []
    selected_randomize: list[bool] = []
    selected_volumes: list[int] = []
    selected_mutes: list[bool] = []
    restored_usernames: list[str] = []
    saved_usernames: list[str] = []
    saved_geometries: list[QByteArray] = []

    class FakeApplication:
        def __init__(self, _args: list[str]) -> None:
            self.application_name = ""
            self.organization_name = ""

        def setApplicationName(self, name: str) -> None:
            self.application_name = name

        def setOrganizationName(self, name: str) -> None:
            self.organization_name = name

        def exec(self) -> int:
            return 0

    class _FakeSignal:
        def __init__(self) -> None:
            self.callbacks: list[object] = []

        def connect(self, _slot) -> None:
            self.callbacks.append(_slot)

        def emit(self, *args) -> None:
            for callback in self.callbacks:
                callback(*args)

    class FakeMainWindow:
        def __init__(self, **_kwargs) -> None:
            self.theme_requested = _FakeSignal()
            self.language_changed = _FakeSignal()
            self.randomize_playback_changed = _FakeSignal()
            self.quit_requested = _FakeSignal()
            self.restored_geometry: QByteArray | None = None

        def set_username(self, username: str) -> None:
            restored_usernames.append(username)

        def username(self) -> str:
            return "typed-name"

        def restoreGeometry(self, geometry: QByteArray) -> bool:
            self.restored_geometry = geometry
            return True

        def saveGeometry(self) -> QByteArray:
            return QByteArray(b"saved-geometry")

        def set_theme_mode(self, mode: str) -> None:
            selected_themes.append(mode)

        def set_randomize_playback(self, enabled: bool) -> None:
            selected_randomize.append(enabled)

        def set_volume_percent(self, volume_percent: int) -> None:
            selected_volumes.append(volume_percent)

        def set_muted(self, muted: bool) -> None:
            selected_mutes.append(muted)

        def show(self) -> None:
            return None

    class FakeController:
        def __init__(self, _window: FakeMainWindow) -> None:
            self.started = False

        def start(self) -> None:
            self.started = True

    class FakeSettings:
        def language_code(self) -> str:
            return "de"

        def theme_mode(self) -> ThemeMode:
            return ThemeMode.MINT

        def randomize_playback(self) -> bool:
            return True

        def volume_percent(self) -> int:
            return 55

        def muted(self) -> bool:
            return True

        def last_username(self) -> str:
            return "stored-name"

        def window_geometry(self) -> QByteArray | None:
            return QByteArray(b"stored-geometry")

        def set_last_username(self, username: str) -> None:
            saved_usernames.append(username)

        def set_window_geometry(self, geometry: QByteArray) -> None:
            saved_geometries.append(geometry)

        def set_language_code(self, code: str) -> None:
            saved_languages.append(code)

        def set_theme_mode(self, mode: ThemeMode) -> None:
            saved_themes.append(mode)

    class FakeTranslationManager:
        def __init__(self, _app: FakeApplication) -> None:
            self.current_language = "en"

        def set_language(self, code: str) -> bool:
            self.current_language = code
            return True

    created_windows: list[FakeMainWindow] = []

    def make_window(**kwargs) -> FakeMainWindow:
        window = FakeMainWindow(**kwargs)
        created_windows.append(window)
        return window

    monkeypatch.setattr(main_module, "QApplication", FakeApplication)
    monkeypatch.setattr(main_module, "MainWindow", make_window)
    monkeypatch.setattr(main_module, "ApplicationController", FakeController)
    monkeypatch.setattr(main_module, "TranslationManager", FakeTranslationManager)
    monkeypatch.setattr(main_module, "apply_theme", lambda _app, mode: applied_themes.append(mode))
    monkeypatch.setattr(main_module, "AppSettings", FakeSettings)

    assert main_module.main() == 0

    window_instance = created_windows[0]
    assert bytes(window_instance.restored_geometry or QByteArray()) == b"stored-geometry"
    assert capsys.readouterr().out == f"myLastFmPlayer {__display_version__}\n"
    assert applied_themes == [ThemeMode.MINT]
    assert selected_themes == ["mint"]
    assert selected_randomize == [True]
    assert selected_volumes == [55]
    assert selected_mutes == [True]
    assert restored_usernames == ["stored-name"]

    window_instance.quit_requested.emit()

    assert saved_usernames == ["typed-name"]
    assert [bytes(geometry) for geometry in saved_geometries] == [b"saved-geometry"]
    assert saved_languages == []
    assert saved_themes == []


def test_main_session_helpers_round_trip_username_and_geometry(qapp, tmp_path) -> None:
    settings = AppSettings(QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat))
    saved_window = MainWindow()
    saved_window.set_username("  marcel  ")
    saved_window.resize(900, 640)

    main_module._save_session(saved_window, settings)

    assert settings.last_username() == "marcel"

    restored_window = MainWindow()
    main_module._restore_session(restored_window, settings)

    assert restored_window.username() == "marcel"
    # Width can be clamped to the available screen area, height is restored verbatim.
    assert restored_window.height() == saved_window.height()
    assert restored_window.size() != MainWindow().size()


def test_main_restore_session_keeps_default_geometry_when_unset(qapp, tmp_path) -> None:
    settings = AppSettings(QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat))
    window = MainWindow()
    default_size = window.size()

    main_module._restore_session(window, settings)

    assert window.username() == ""
    assert window.size() == default_size


def test_main_theme_handler_applies_and_persists_theme(monkeypatch) -> None:
    applied_themes: list[ThemeMode] = []
    saved_themes: list[ThemeMode] = []
    settings = types.SimpleNamespace(set_theme_mode=saved_themes.append)
    monkeypatch.setattr(main_module, "apply_theme", lambda _app, mode: applied_themes.append(mode))

    main_module._apply_and_save_theme(object(), settings, "lilac")  # type: ignore[arg-type]

    assert applied_themes == [ThemeMode.LILAC]
    assert saved_themes == [ThemeMode.LILAC]


def test_main_window_binds_track_data_and_selection(qapp) -> None:
    window = MainWindow()
    tracks = [
        Track(artist="Zed", title="Last", status=TrackStatus.FETCHED),
        Track(artist="Alpha", title="First", status=TrackStatus.DOWNLOADED),
    ]

    window.set_tracks(tracks)
    window.track_table.selectRow(1)

    assert window.track_model.rowCount() == 2
    assert window.track_model.data(window.track_model.index(0, 0)) == "Zed"
    assert window.track_model.data(window.track_model.index(1, 3)) == "Downloaded"
    assert window.selected_track() == tracks[1]


def test_main_window_preserves_selection_and_scroll_across_track_refresh(qapp) -> None:
    window = MainWindow()
    tracks = [Track(artist=f"Keep {index:03}", title=f"Track {index}") for index in range(80)]
    window.resize(800, 600)
    window.show()
    window.set_tracks(tracks)
    window.track_filter_input.setText("keep")
    window.track_sort_model.sort(0, Qt.SortOrder.DescendingOrder)
    source_index = window.track_model.index(30, 2)
    proxy_index = window.track_sort_model.mapFromSource(source_index)
    window.track_table.selectRow(proxy_index.row())
    window.track_table.setCurrentIndex(proxy_index)
    scrollbar = window.track_table.verticalScrollBar()
    scrollbar.setValue(min(15, scrollbar.maximum()))
    scroll_value = scrollbar.value()

    window.set_tracks([replace(track, status=TrackStatus.SEARCHING) for track in tracks])

    assert window.selected_track() == replace(tracks[30], status=TrackStatus.SEARCHING)
    assert window.track_table.currentIndex().column() == 2
    assert scrollbar.value() == scroll_value


def test_main_window_drops_selection_when_selected_track_disappears(qapp) -> None:
    window = MainWindow()
    first = Track(artist="First", title="Track")
    second = Track(artist="Second", title="Track")
    window.set_tracks([first, second])
    window.select_track_row(1)

    window.set_tracks([first])

    assert window.selected_track() is None


def test_main_window_selection_helpers_handle_empty_and_invalid_rows(qapp) -> None:
    window = MainWindow()

    assert window.selected_track() is None
    assert window.selected_track_row() is None
    assert window.next_track_after("missing") is None

    window.select_track_row(-1)
    window.select_track_row(window.track_model.rowCount())

    assert window.selected_track() is None


def test_main_window_finds_next_track_in_current_sort_order(qapp) -> None:
    window = MainWindow()
    tracks = [
        Track(artist="Zed", title="Last", status=TrackStatus.DOWNLOADED),
        Track(artist="Alpha", title="First", status=TrackStatus.DOWNLOADED),
        Track(artist="Middle", title="Second", status=TrackStatus.DOWNLOADED),
    ]
    window.set_tracks(tracks)
    window.track_sort_model.sort(0, Qt.SortOrder.AscendingOrder)

    next_track = window.next_track_after(tracks[1].cache_key)

    assert next_track == (2, tracks[2])
    assert window.next_track_after(tracks[0].cache_key) == (1, tracks[1])

    window.select_track_row(2)

    assert window.selected_track() == tracks[2]


def test_main_window_filters_track_details_while_preserving_sort(qapp) -> None:
    window = MainWindow()
    tracks = [
        Track(artist="Zed", title="Last", status=TrackStatus.DOWNLOADED),
        Track(artist="Alpha", title="First", status=TrackStatus.DOWNLOADED),
        Track(artist="Middle", title="Second", status=TrackStatus.DOWNLOADED),
        Track(artist="Band", title="Alpine", status=TrackStatus.DOWNLOADED),
    ]
    window.set_tracks(tracks)
    window.track_sort_model.sort(0, Qt.SortOrder.AscendingOrder)

    window.track_filter_input.setText("Al")

    assert window.track_sort_model.rowCount() == 2
    assert [
        window.track_sort_model.data(window.track_sort_model.index(row, 0))
        for row in range(window.track_sort_model.rowCount())
    ] == ["Alpha", "Band"]
    assert [
        window.track_sort_model.data(window.track_sort_model.index(row, 1))
        for row in range(window.track_sort_model.rowCount())
    ] == ["First", "Alpine"]

    window.track_filter_reset_button.click()

    assert window.track_filter_input.text() == ""
    assert window.track_sort_model.rowCount() == 4

    failed = Track(
        artist="Other",
        title="Unrelated",
        status=TrackStatus.LOOKUP_FAILED,
        error="HTTP 429 quota exceeded",
    )
    window.set_tracks([*tracks, failed])
    window.track_filter_input.setText("429")
    assert window.track_sort_model.rowCount() == 1
    assert window.track_sort_model.data(window.track_sort_model.index(0, 0)) == "Other"

    window.track_filter_input.setText("lookup failed")
    assert window.track_sort_model.rowCount() == 1
    assert window.track_sort_model.data(window.track_sort_model.index(0, 0)) == "Other"


def test_main_window_filter_is_case_insensitive_and_hard_filters(qapp) -> None:
    window = MainWindow()
    tracks = [
        Track(artist="Artist", title="Blue Song", status=TrackStatus.DOWNLOADED),
        Track(artist="Other", title="Track", status=TrackStatus.DOWNLOADED),
    ]
    window.set_tracks(tracks)

    window.track_filter_input.setText("blue")

    assert window.track_sort_model.rowCount() == 1
    assert window.track_sort_model.data(window.track_sort_model.index(0, 1)) == "Blue Song"
    assert window.next_track_after(tracks[1].cache_key) == (0, tracks[0])


def test_main_window_filter_handles_empty_visible_set_and_hidden_selection(qapp) -> None:
    window = MainWindow()
    tracks = [
        Track(artist="Artist", title="Visible", status=TrackStatus.DOWNLOADED),
        Track(artist="Other", title="Hidden", status=TrackStatus.DOWNLOADED),
    ]
    window.set_tracks(tracks)
    window.track_filter_input.setText("missing")
    window.track_sort_model.set_track_filter_text("missing")

    assert window.track_sort_model.rowCount() == 0
    assert window.next_track_after(tracks[0].cache_key) is None
    assert (
        window.random_track_excluding(tracks[0].cache_key, lambda candidates: candidates[0]) is None
    )

    window.track_filter_input.setText("visible")
    window.select_track_row(1)

    assert window.selected_track() is None


def test_track_filter_proxy_falls_back_for_non_track_models(qapp) -> None:
    proxy = TrackFilterProxyModel()
    model = QStandardItemModel(1, 1)
    proxy.setSourceModel(model)
    proxy.set_track_filter_text("anything")

    assert proxy.filterAcceptsRow(0, QModelIndex())


def test_main_window_random_track_uses_full_track_list(qapp) -> None:
    window = MainWindow()
    tracks = [
        Track(artist="Zed", title="Last", status=TrackStatus.DOWNLOADED),
        Track(artist="Alpha", title="First", status=TrackStatus.DOWNLOADED),
        Track(artist="Middle", title="Second", status=TrackStatus.DOWNLOADED),
    ]
    window.set_tracks(tracks)
    choices: list[list[tuple[int, Track]]] = []

    def choose(candidates: list[tuple[int, Track]]) -> tuple[int, Track]:
        choices.append(candidates)
        return candidates[-1]

    selected = window.random_track_excluding(tracks[1].cache_key, choose)

    assert selected == (2, tracks[2])
    assert choices == [[(0, tracks[0]), (2, tracks[2])]]


def test_main_window_random_track_uses_only_filtered_rows(qapp) -> None:
    window = MainWindow()
    tracks = [
        Track(artist="Artist", title="One", status=TrackStatus.DOWNLOADED),
        Track(artist="Artist", title="Two", status=TrackStatus.DOWNLOADED),
        Track(artist="Other", title="Three", status=TrackStatus.DOWNLOADED),
    ]
    window.set_tracks(tracks)
    window.track_filter_input.setText("artist")
    choices: list[list[tuple[int, Track]]] = []

    def choose(candidates: list[tuple[int, Track]]) -> tuple[int, Track]:
        choices.append(candidates)
        return candidates[-1]

    selected = window.random_track_excluding(tracks[0].cache_key, choose)

    assert selected == (1, tracks[1])
    assert choices == [[(1, tracks[1])]]


def test_main_window_randomize_toggle_emits_setting_change(qapp) -> None:
    window = MainWindow()
    emissions: list[bool] = []
    window.randomize_playback_changed.connect(emissions.append)

    window.randomize_checkbox.setChecked(True)

    assert window.randomize_playback()
    assert emissions == [True]


def test_main_window_updates_progress_and_feedback(qapp) -> None:
    window = MainWindow()

    window.set_progress(140, "Downloading")
    window.set_stage_progress("lookup", 80, "Checked 4/5")
    window.set_stage_progress("download", 10, "Downloaded 1/10")
    window.append_feedback("Network error")

    assert window.progress_bar.value() == 100
    assert window.progress_bar.format() == "Downloading — %p%"
    assert window.lookup_progress_bar.value() == 80
    assert window.lookup_progress_bar.format() == "Checked 4/5 — %p%"
    assert window.download_progress_bar.value() == 10
    assert window.download_progress_bar.format() == "Downloaded 1/10 — %p%"
    assert window.discovery_progress_label.text() == "Last.fm discovery"
    assert window.lookup_progress_label.text() == "YouTube checks"
    assert window.download_progress_label.text() == "Downloads"
    assert "Network error" in window.feedback_log.toPlainText()


def test_main_window_volume_and_mute_emit_changes(qapp) -> None:
    window = MainWindow()
    volumes: list[int] = []
    mutes: list[bool] = []
    window.volume_changed.connect(volumes.append)
    window.mute_toggled.connect(mutes.append)

    assert window.volume_percent() == 100
    assert not window.is_muted()
    assert window.volume_label.text() == "Volume"
    assert window.mute_checkbox.text() == "Mute"

    window.volume_slider.setValue(40)
    window.mute_checkbox.setChecked(True)

    assert volumes == [40]
    assert mutes == [True]
    assert window.volume_percent() == 40
    assert window.is_muted()


def test_main_window_restores_volume_and_mute_without_emitting(qapp) -> None:
    window = MainWindow()
    volumes: list[int] = []
    mutes: list[bool] = []
    window.volume_changed.connect(volumes.append)
    window.mute_toggled.connect(mutes.append)

    window.set_volume_percent(25)
    window.set_muted(True)

    assert window.volume_percent() == 25
    assert window.is_muted()
    assert volumes == []
    assert mutes == []


def test_main_window_starts_empty_and_hides_the_hint_once_tracks_load(qapp) -> None:
    window = MainWindow()
    window.show()

    assert window.track_model.rowCount() == 0
    assert window.track_count_label.text() == "Playlist: 0 titles"
    assert window.empty_state_label.isVisible()

    window.set_tracks([Track(artist="Artist", title="Title")])

    assert not window.empty_state_label.isVisible()
    assert window.track_count_label.text() == "Playlist: 1 titles"

    window.set_tracks([])

    assert window.empty_state_label.isVisible()


def test_main_window_marks_errors_in_the_log_and_status_bar(qapp) -> None:
    window = MainWindow()

    window.append_feedback("Routine progress")
    window.append_error("Could not open data folder: /home/x")

    document = window.feedback_log.document()
    routine_block = document.findBlockByNumber(0)
    error_block = document.findBlockByNumber(1)
    routine_colors = {run.format.foreground().color().name() for run in routine_block.textFormats()}
    error_colors = {run.format.foreground().color().name() for run in error_block.textFormats()}

    assert ERROR_TEXT_COLOR not in routine_colors
    assert error_colors == {ERROR_TEXT_COLOR}
    assert "Could not open data folder: /home/x" in window.feedback_log.toPlainText()
    assert not window.error_indicator_label.isHidden()
    assert window.error_indicator_label.text() == "⚠ Could not open data folder: /home/x"
    assert window.error_indicator_label.toolTip() == "Could not open data folder: /home/x"
    assert window.statusBar().currentMessage() == "Could not open data folder: /home/x"


def test_main_window_clearing_the_log_also_clears_the_error_indicator(qapp) -> None:
    window = MainWindow()
    window.append_error("Download failed")
    assert window.error_indicator_label.text()

    window.clear_feedback_button.click()

    assert window.error_indicator_label.text() == ""
    assert window.error_indicator_label.toolTip() == ""
    assert window.error_indicator_label.isHidden()


def test_progress_format_keeps_label_and_shows_percentage() -> None:
    assert format_progress_text("Searching 3/282") == "Searching 3/282 — %p%"


def test_error_indicator_text_is_collapsed_and_truncated() -> None:
    assert shorten_error("short\n  message") == "short message"
    long_message = "y" * 120
    shortened = shorten_error(long_message)
    assert len(shortened) == 80
    assert shortened.endswith("…")
    assert shorten_error("y" * 80) == "y" * 80


def test_feedback_messages_include_timestamp_prefix() -> None:
    assert format_feedback_message("Network error", QTime(9, 8, 7)) == ("09:08:07: Network error")


def test_main_window_clear_feedback_button_clears_log_and_resets_scrollbars(qapp) -> None:
    window = MainWindow()
    window.resize(360, 260)
    window.show()
    for index in range(80):
        window.append_feedback(f"Network error {index} {'x' * 120}")
    qapp.processEvents()
    window.feedback_log.verticalScrollBar().setValue(
        window.feedback_log.verticalScrollBar().maximum()
    )
    window.feedback_log.horizontalScrollBar().setValue(
        window.feedback_log.horizontalScrollBar().maximum()
    )

    window.clear_feedback_button.click()

    assert window.feedback_log.toPlainText() == ""
    assert window.feedback_log.verticalScrollBar().value() == (
        window.feedback_log.verticalScrollBar().minimum()
    )
    assert window.feedback_log.horizontalScrollBar().value() == (
        window.feedback_log.horizontalScrollBar().minimum()
    )


def test_main_window_fetch_controls_emit_fetch_signal(qapp) -> None:
    window = MainWindow()
    emissions: list[bool] = []
    window.fetch_requested.connect(lambda: emissions.append(True))

    window.fetch_button.click()
    window.refresh_action.trigger()

    assert emissions == [True, True]


def test_main_window_has_language_menu(qapp) -> None:
    window = MainWindow()

    assert window.language_menu.title() == "Language"
    assert {action.text() for action in window.language_menu.actions()} == {
        language.native_name for language in SUPPORTED_LANGUAGES
    }
    assert window.language_actions["en"].isChecked()


def test_main_window_has_help_menu_actions(qapp) -> None:
    window = MainWindow()

    assert window.help_menu.title() == "Help"
    assert [action.text() for action in window.help_menu.actions()] == [
        "About myLastFmPlayer",
        "Open Source Licenses",
    ]


def test_main_window_has_main_menu_actions_in_requested_order(qapp) -> None:
    window = MainWindow()

    assert window.main_menu.title() == "Main"
    assert [action.text() for action in window.main_menu.actions() if not action.isSeparator()] == [
        "Fetch loved tracks",
        "Theme",
        "Preferences",
        "Open data folder in file manager",
        "Quit",
    ]


def test_main_window_fetch_action_is_reachable_from_the_main_menu(qapp) -> None:
    window = MainWindow()
    emissions: list[bool] = []
    window.fetch_requested.connect(lambda: emissions.append(True))

    assert window.refresh_action in window.main_menu.actions()
    assert window.refresh_action.shortcut() == QKeySequence(QKeySequence.StandardKey.Refresh)

    window.main_menu.actions()[0].trigger()

    assert emissions == [True]


def test_main_window_file_cache_menu_action_emits_request(qapp) -> None:
    window = MainWindow()
    emissions: list[bool] = []
    window.file_cache_requested.connect(lambda: emissions.append(True))

    window.file_cache_action.trigger()

    assert emissions == [True]


def test_main_window_about_text_contains_author_license_and_intent(qapp) -> None:
    window = MainWindow()

    about_text = window.about_dialog_text()

    assert 'href="mailto:mail@marcelpetrick.it"' in about_text
    assert "Marcel Petrick" in about_text
    assert "GNU GPLv3 or later" in about_text
    assert "fetches a user's public loved tracks from Last.fm" in about_text
    assert "downloads MP3 files" in about_text


def test_main_window_open_source_license_text_lists_runtime_tools(qapp) -> None:
    window = MainWindow()

    license_text = window.open_source_licenses_plain_text()

    for expected in ("PyQt6", "requests", "pylast", "yt-dlp", "FFmpeg"):
        assert expected in license_text


def test_main_window_open_source_license_text_bolds_components(qapp) -> None:
    window = MainWindow()

    license_text = window.open_source_licenses_dialog_text()

    for expected in ("<b>PyQt6</b>", "<b>requests</b>", "<b>yt-dlp</b>", "<b>FFmpeg</b>"):
        assert expected in license_text


def test_main_window_retranslates_idle_now_playing_label(qapp) -> None:
    translation_manager = TranslationManager(qapp)
    assert translation_manager.set_language("zh")
    window = MainWindow(translation_manager)

    window.retranslate_ui()

    assert window.now_playing_label.text() == "未播放"
    translation_manager.set_language("en")


def test_main_window_does_not_retranslate_active_now_playing_label(qapp) -> None:
    translation_manager = TranslationManager(qapp)
    assert translation_manager.set_language("zh")
    window = MainWindow(translation_manager)
    window.set_now_playing(Track(artist="Artist", title="Title"))

    window.retranslate_ui()

    assert window.now_playing_label.text() == "Artist — Title"
    translation_manager.set_language("en")


def test_main_window_help_actions_open_dialogs(qapp, monkeypatch) -> None:
    window = MainWindow()
    calls: list[tuple[object, str, str]] = []

    monkeypatch.setattr(
        main_window_module,
        "_show_rich_text_dialog",
        lambda parent, title, text: calls.append((parent, title, text)),
    )

    window.about_action.trigger()
    window.open_source_licenses_action.trigger()

    assert calls[0][0] is window
    assert calls[0][1] == "About myLastFmPlayer"
    assert "Marcel Petrick" in calls[0][2]
    assert calls[1][1] == "Open Source Licenses"
    assert "<b>PyQt6</b>" in calls[1][2]


def test_rich_text_dialog_supports_clickable_links(qapp, monkeypatch) -> None:
    dialogs: list[main_window_module.QDialog] = []

    def fake_exec(self) -> int:
        dialogs.append(self)
        return 0

    monkeypatch.setattr(main_window_module.QDialog, "exec", fake_exec)

    main_window_module._show_rich_text_dialog(
        MainWindow(),
        "About",
        '<p><a href="mailto:mail@marcelpetrick.it">mail@marcelpetrick.it</a></p>',
    )

    assert len(dialogs) == 1
    assert dialogs[0].size().height() == 280
    text_browser = dialogs[0].findChild(main_window_module.QTextBrowser)
    assert text_browser is not None
    assert text_browser.openExternalLinks()


def test_rich_text_dialog_uses_larger_scrollable_layout_for_long_text(qapp, monkeypatch) -> None:
    dialogs: list[main_window_module.QDialog] = []

    def fake_exec(self) -> int:
        dialogs.append(self)
        return 0

    monkeypatch.setattr(main_window_module.QDialog, "exec", fake_exec)

    main_window_module._show_rich_text_dialog(MainWindow(), "Licenses", "<p>Text</p>" * 140)

    assert dialogs[0].size().height() == 520
    text_browser = dialogs[0].findChild(main_window_module.QTextBrowser)
    assert text_browser is not None
    assert text_browser.verticalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAsNeeded


def test_main_window_youtube_button_stops_and_resumes_work(qapp) -> None:
    window = MainWindow()
    events: list[str] = []
    window._youtube_stop_requested.connect(lambda: events.append("stop"))
    window._youtube_resume_requested.connect(lambda: events.append("resume"))

    assert not window.youtube_work_button.isEnabled()
    assert "automatically" in window.fetch_button.toolTip()
    window.set_youtube_work_state(active=True)
    assert window.youtube_work_button.text() == "Stop YouTube"
    window.youtube_work_button.click()

    window.set_youtube_work_state(active=True, stopping=True)
    assert window.youtube_work_button.text() == "Stopping YouTube…"
    assert not window.youtube_work_button.isEnabled()

    window.set_youtube_work_state(active=False, stopped=True)
    assert window.youtube_work_button.text() == "Resume YouTube"
    window.youtube_work_button.click()

    assert events == ["stop", "resume"]


def test_main_window_workflow_enabled_toggles_fetch_controls(qapp) -> None:
    window = MainWindow()

    window.set_workflow_enabled(False)

    assert not window.fetch_button.isEnabled()
    assert window.username_input.isEnabled()
    assert not window.refresh_action.isEnabled()

    window.set_workflow_enabled(True)

    assert window.fetch_button.isEnabled()
    assert window.username_input.isEnabled()
    assert window.refresh_action.isEnabled()


def test_main_window_playback_controls_emit_signals(qapp) -> None:
    window = MainWindow()
    events: list[str] = []
    window.play_requested.connect(lambda: events.append("play"))
    window.pause_requested.connect(lambda: events.append("pause"))
    window.stop_requested.connect(lambda: events.append("stop"))
    window.next_requested.connect(lambda: events.append("next"))

    window.play_button.click()
    window.set_playback_controls(active=True)
    window.pause_button.click()
    window.stop_button.click()
    window.next_button.click()

    assert events == ["play", "pause", "stop", "next"]


def test_main_window_paused_transport_state_survives_retranslation(qapp) -> None:
    window = MainWindow()

    window.set_playback_controls(active=True, paused=True)
    window.retranslate_ui()

    assert window.play_button.isEnabled()
    assert window.pause_button.isEnabled()
    assert window.pause_button.text() == "Resume"
    assert window.pause_button.toolTip() == "Resume playback"


def test_artist_image_label_keeps_a_bounded_size(qapp) -> None:
    label = ArtistImageLabel()
    label.show()

    assert label.pixmap().isNull()  # nothing loaded yet, so nothing to scale

    label.set_artist_image(png_bytes(), "https://www.last.fm/music/Artist")
    qapp.processEvents()
    original_size = label.size()
    label.resize(260, 260)
    qapp.processEvents()

    assert label.size() == original_size
    assert label.width() == main_window_module.ARTIST_IMAGE_SIZE
    assert label.height() == main_window_module.ARTIST_IMAGE_SIZE


def test_main_window_artist_image_is_clickable(qapp) -> None:
    window = MainWindow()
    requested_pages: list[str] = []
    window.artist_page_requested.connect(requested_pages.append)
    controls_layout = window.artist_image_group.parentWidget().layout()

    window.set_artist_image(png_bytes(), "https://www.last.fm/music/Artist", "Artist")

    assert controls_layout.itemAt(0).widget() is window.playback_group
    assert controls_layout.itemAt(1).widget() is window.artist_image_group
    assert controls_layout.count() == 2
    assert controls_layout.stretch(0) == 1
    assert controls_layout.stretch(1) == 0
    assert window.artist_image_group.title() == "Artist: Artist"
    assert window.artist_image_group.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Fixed
    assert window.playback_group.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Expanding
    assert window.artist_image_label.parentWidget() is window.artist_image_group
    assert window.artist_image_label.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Fixed
    assert not window.artist_image_group.isHidden()
    assert not window.artist_image_label.isHidden()
    assert window.artist_image_label.pixmap() is not None

    event = QMouseEvent(
        QEvent.Type.MouseButtonPress,
        QPointF(4, 4),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    window.artist_image_label.mousePressEvent(event)

    assert requested_pages == ["https://www.last.fm/music/Artist"]

    window.set_artist_image(None, None)

    assert window.artist_image_label.isHidden()
    assert window.artist_image_group.isHidden()
    assert window.artist_image_group.title() == "Artist"


def test_artist_image_does_not_expand_controls_or_collapse_library(qapp) -> None:
    window = MainWindow()
    window.resize(1120, 720)
    window.show()
    qapp.processEvents()
    controls_height = window.playback_group.height()
    table_height = window.track_table.height()

    window.set_artist_image(png_bytes(), "https://www.last.fm/music/Artist", "Artist")
    qapp.processEvents()

    assert window.playback_group.height() == controls_height
    assert window.artist_image_group.sizePolicy().verticalPolicy() == QSizePolicy.Policy.Fixed
    assert window.playback_group.sizePolicy().verticalPolicy() == QSizePolicy.Policy.Fixed
    assert window.artist_image_group.width() == main_window_module.ARTIST_IMAGE_PANEL_WIDTH
    assert window.track_table.height() == table_height


def test_main_window_artist_image_ignores_invalid_data_and_non_left_clicks(qapp) -> None:
    window = MainWindow()
    requested_pages: list[str] = []
    window.artist_page_requested.connect(requested_pages.append)

    window.set_artist_image(b"invalid image", "https://www.last.fm/music/Artist")

    assert window.artist_image_label.isHidden()

    event = QMouseEvent(
        QEvent.Type.MouseButtonPress,
        QPointF(4, 4),
        Qt.MouseButton.RightButton,
        Qt.MouseButton.RightButton,
        Qt.KeyboardModifier.NoModifier,
    )
    window.artist_image_label.mousePressEvent(event)

    assert requested_pages == []


def test_main_window_double_clicking_track_requests_playback(qapp) -> None:
    window = MainWindow()
    events: list[str] = []
    window.play_requested.connect(lambda: events.append("play"))

    source_index = window.track_model.index(0, 0)
    proxy_index = window.track_sort_model.mapFromSource(source_index)
    window.track_table.doubleClicked.emit(proxy_index)

    assert events == ["play"]


def test_main_window_playback_timeline_formats_and_seeks(qapp) -> None:
    window = MainWindow()
    seeks: list[int] = []
    window.seek_requested.connect(seeks.append)

    assert not window.playback_slider.isEnabled()
    assert window.current_time_label.text() == "0:00"
    assert window.total_time_label.text() == "0:00"

    window.set_playback_timeline(65_000, 185_000)

    assert window.playback_slider.isEnabled()
    assert window.playback_slider.maximum() == 185_000
    assert window.playback_slider.value() == 65_000
    assert window.current_time_label.text() == "1:05"
    assert window.total_time_label.text() == "3:05"

    window.playback_slider.setValue(90_000)
    window.playback_slider.sliderReleased.emit()

    assert seeks == [90_000]


def test_main_window_timeline_seek_is_ignored_without_duration(qapp) -> None:
    window = MainWindow()
    seeks: list[int] = []
    window.seek_requested.connect(seeks.append)

    window.playback_slider.setValue(0)
    window.playback_slider.sliderReleased.emit()

    assert seeks == []


def test_main_window_playback_timeline_click_seeks_immediately(qapp) -> None:
    window = MainWindow()
    seeks: list[int] = []
    window.seek_requested.connect(seeks.append)
    window.set_playback_timeline(0, 200_000)
    window.playback_slider.resize(200, window.playback_slider.height())

    event = QMouseEvent(
        QEvent.Type.MouseButtonPress,
        QPointF(50, 4),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    expected_position = window._timeline_value_for_x_position(50)

    assert window.eventFilter(window.playback_slider, event)
    assert window.playback_slider.value() == expected_position
    assert window.current_time_label.text() == format_playback_time(expected_position)
    assert seeks == [expected_position]


def test_main_window_playback_timeline_handle_can_be_dragged(qapp) -> None:
    window = MainWindow()
    seeks: list[int] = []
    window.seek_requested.connect(seeks.append)
    window.show()
    window.playback_slider.resize(300, window.playback_slider.height())
    window.set_playback_timeline(50_000, 200_000)
    option = QStyleOptionSlider()
    window.playback_slider.initStyleOption(option)
    handle = window.playback_slider.style().subControlRect(
        QStyle.ComplexControl.CC_Slider,
        option,
        QStyle.SubControl.SC_SliderHandle,
        window.playback_slider,
    )
    start = handle.center()
    target = QPoint(window.playback_slider.width() * 3 // 4, start.y())

    QTest.mousePress(window.playback_slider, Qt.MouseButton.LeftButton, pos=start)
    assert window.playback_slider.isSliderDown()
    QTest.mouseMove(window.playback_slider, target)
    QTest.mouseRelease(window.playback_slider, Qt.MouseButton.LeftButton, pos=target)

    assert not window.playback_slider.isSliderDown()
    assert window.playback_slider.value() > 100_000
    assert seeks == [window.playback_slider.value()]


def test_main_window_playback_timeline_keyboard_actions_seek(qapp) -> None:
    window = MainWindow()
    seeks: list[int] = []
    window.seek_requested.connect(seeks.append)
    window.set_playback_timeline(60_000, 200_000)
    window.playback_slider.setFocus()

    QTest.keyClick(window.playback_slider, Qt.Key.Key_Right)
    assert window.playback_slider.value() == 65_000
    assert seeks[-1] == 65_000

    QTest.keyClick(window.playback_slider, Qt.Key.Key_PageUp)
    assert window.playback_slider.value() == 95_000
    assert seeks[-1] == 95_000

    QTest.keyClick(window.playback_slider, Qt.Key.Key_Home)
    assert window.playback_slider.value() == 0
    assert seeks[-1] == 0

    QTest.keyClick(window.playback_slider, Qt.Key.Key_End)
    assert window.playback_slider.value() == 200_000
    assert seeks[-1] == 200_000


def test_playback_updates_do_not_overwrite_an_active_timeline_drag(qapp) -> None:
    window = MainWindow()
    window.set_playback_timeline(50_000, 200_000)
    window.playback_slider.setSliderDown(True)
    window.playback_slider.setSliderPosition(150_000)

    window.set_playback_timeline(55_000, 210_000)

    assert window.playback_slider.sliderPosition() == 150_000
    assert window.current_time_label.text() == "2:30"
    assert window.total_time_label.text() == "3:30"


def test_format_playback_time_handles_hours() -> None:
    assert format_playback_time(3_723_000) == "1:02:03"


def test_main_window_theme_menu_emits_theme_requested(qapp) -> None:
    window = MainWindow()
    themes: list[str] = []
    window.theme_requested.connect(themes.append)

    window.theme_dark_action.trigger()
    window.theme_lilac_action.trigger()
    window.theme_mint_action.trigger()
    window.theme_light_action.trigger()

    assert themes == ["dark", "lilac", "mint", "light"]


def test_main_window_theme_actions_are_exclusive(qapp) -> None:
    window = MainWindow()

    assert window.theme_light_action.isChecked()
    assert not window.theme_dark_action.isChecked()
    assert not window.theme_lilac_action.isChecked()
    assert not window.theme_mint_action.isChecked()

    window.theme_mint_action.trigger()

    assert not window.theme_light_action.isChecked()
    assert not window.theme_dark_action.isChecked()
    assert not window.theme_lilac_action.isChecked()
    assert window.theme_mint_action.isChecked()


def test_main_window_can_mark_persisted_theme_without_emitting_request(qapp) -> None:
    window = MainWindow()
    themes: list[str] = []
    window.theme_requested.connect(themes.append)

    window.set_theme_mode("lilac")

    assert not window.theme_light_action.isChecked()
    assert window.theme_lilac_action.isChecked()
    assert themes == []


def test_main_window_ignores_theme_actions_without_string_data(qapp) -> None:
    window = MainWindow()
    themes: list[str] = []
    window.theme_requested.connect(themes.append)

    window._on_theme_action_triggered(window.help_menu.menuAction())

    assert themes == []


def test_main_window_set_language_updates_manager_actions_and_visible_text(qapp) -> None:
    translation_manager = TranslationManager(qapp)
    window = MainWindow(translation_manager)
    changes: list[bool] = []
    window.language_changed.connect(lambda: changes.append(True))

    window.set_language("zh")

    assert translation_manager.current_language == "zh"
    assert window.language_actions["zh"].isChecked()
    assert window.now_playing_label.text() == "未播放"
    assert changes == [True]
    window.set_language("en")


def test_main_window_retranslate_refreshes_empty_state_and_idle_labels(qapp) -> None:
    TranslationManager(qapp).set_language("en")
    window = MainWindow()
    window.dependency_label.clear()
    window._last_progress_label = "Idle"
    window._last_status_message = "Ready"

    window.retranslate_ui()

    assert window.track_model.rowCount() == 0
    assert window.empty_state_label.text() == (
        "Enter your Last.fm username and press Fetch to load your loved tracks."
    )
    assert (
        window.dependency_label.text()
        == "Dependencies: yt-dlp, ffmpeg, and ffprobe not checked yet"
    )
    assert window.progress_bar.format() == "Idle — %p%"
    assert window.statusBar().currentMessage() == "Ready"


def test_main_window_context_menu_emits_retry_for_track(qapp, monkeypatch) -> None:
    window = MainWindow()
    window.set_tracks([Track(artist="Artist", title="Title", status=TrackStatus.FAILED)])
    retries: list[str] = []
    window.retry_download_requested.connect(retries.append)
    index = window.track_sort_model.index(0, 0)
    pos = window.track_table.visualRect(index).center()

    monkeypatch.setattr(
        main_window_module.QMenu,
        "exec",
        lambda self, _global_pos: self.actions()[0],
    )

    window._show_track_context_menu(pos)

    assert retries == [window.track_model.track_at(0).cache_key]


@pytest.mark.parametrize(
    ("track", "button_text"),
    [
        (
            Track(artist="Artist", title="Missing", status=TrackStatus.NOT_FOUND),
            "Retry YouTube Check",
        ),
        (
            Track(
                artist="Artist",
                title="Lookup",
                status=TrackStatus.LOOKUP_FAILED,
                error="service unavailable",
            ),
            "Retry YouTube Check",
        ),
        (
            Track(
                artist="Artist",
                title="Download",
                status=TrackStatus.FAILED,
                youtube_url="https://youtu.be/example",
                error="disk full",
            ),
            "Retry Download",
        ),
    ],
)
def test_main_window_exposes_keyboard_reachable_retry_for_failed_track(
    qapp, track, button_text
) -> None:
    window = MainWindow()
    window.set_tracks([track])
    retries: list[str] = []
    window.retry_download_requested.connect(retries.append)

    window.select_track_row(0)

    assert window.retry_selected_button.isEnabled()
    assert window.retry_selected_button.text() == button_text
    window.retry_selected_button.setFocus()
    QTest.keyClick(window.retry_selected_button, Qt.Key.Key_Space)
    assert retries == [track.cache_key]


def test_main_window_hides_retry_for_successful_track(qapp, monkeypatch) -> None:
    window = MainWindow()
    track = Track(artist="Artist", title="Ready", status=TrackStatus.DOWNLOADED)
    window.set_tracks([track])
    window.select_track_row(0)
    menu_calls: list[bool] = []
    monkeypatch.setattr(
        main_window_module.QMenu,
        "exec",
        lambda *_args: menu_calls.append(True),
    )

    window._show_track_context_menu(
        window.track_table.visualRect(window.track_sort_model.index(0, 0)).center()
    )

    assert not window.retry_selected_button.isEnabled()
    assert window.retry_selected_button.text() == "Retry"
    assert menu_calls == []


def test_main_window_context_menu_ignores_clicks_outside_any_row(qapp, monkeypatch) -> None:
    window = MainWindow()
    retries: list[str] = []
    window.retry_download_requested.connect(retries.append)
    monkeypatch.setattr(
        main_window_module.QMenu,
        "exec",
        lambda self, _global_pos: self.actions()[0],
    )

    window._show_track_context_menu(QPoint(5, 5))

    assert retries == []


def test_main_window_next_track_after_unknown_key_without_filter_returns_none(qapp) -> None:
    window = MainWindow()
    window.set_tracks([Track(artist="Artist", title="Title")])

    assert window.next_track_after("missing-cache-key") is None


def test_main_window_selection_and_random_fallbacks(qapp) -> None:
    track = Track(artist="Only", title="Track")
    window = MainWindow()
    window.set_tracks([track])
    window.track_table.selectRow(0)

    assert window.selected_track_row() == 0
    assert window.random_track_excluding(track.cache_key, lambda candidates: candidates[0]) is None


def test_main_window_close_event_accepts_and_requests_quit(qapp) -> None:
    class FakeCloseEvent:
        def __init__(self) -> None:
            self.accepted = False

        def accept(self) -> None:
            self.accepted = True

    window = MainWindow()
    event = FakeCloseEvent()
    quits: list[bool] = []
    window.quit_requested.connect(lambda: quits.append(True))

    window.closeEvent(event)  # type: ignore[arg-type]

    assert quits == [True]
    assert event.accepted

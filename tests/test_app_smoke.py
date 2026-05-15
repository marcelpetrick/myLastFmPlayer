from __future__ import annotations

import runpy
import sys
import types

import pytest
from PyQt6.QtCore import QEvent, QPointF, Qt, QTime
from PyQt6.QtGui import QMouseEvent

from my_lastfm_player import __display_version__, __version__
from my_lastfm_player import main as main_module
from my_lastfm_player.i18n import SUPPORTED_LANGUAGES
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.themes import ThemeMode
from my_lastfm_player.ui.main_window import (
    MainWindow,
    application_title,
    format_feedback_message,
    format_playback_time,
)
from my_lastfm_player.version import display_version


def test_package_version_is_defined() -> None:
    assert __version__ == "0.0.86"
    assert __display_version__ == "0.0.86"


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
    assert window.windowTitle() == "myLastFmPlayer v0.0.86"
    assert window.username_input.placeholderText() == "Enter username"
    assert window.track_model.columnCount() == 5
    assert window.track_model.rowCount() == 2
    assert window.progress_bar.format() == "Idle"
    assert window.fetch_pause_button.text() == "Pause"
    assert window.fetch_stop_button.text() == "Stop"
    assert not window.fetch_pause_button.isEnabled()
    assert not window.fetch_stop_button.isEnabled()
    assert window.fetch_pause_button.toolTip()
    assert window.fetch_stop_button.toolTip()


def test_application_title_includes_version_suffix() -> None:
    assert application_title("1.2.3+abcdef") == "myLastFmPlayer v1.2.3+abcdef"


def test_main_prints_version_at_startup(monkeypatch, capsys) -> None:
    saved_languages: list[str] = []
    saved_themes: list[ThemeMode] = []
    applied_themes: list[ThemeMode] = []
    selected_themes: list[str] = []

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

        def set_theme_mode(self, mode: str) -> None:
            selected_themes.append(mode)

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

    monkeypatch.setattr(main_module, "QApplication", FakeApplication)
    monkeypatch.setattr(main_module, "MainWindow", FakeMainWindow)
    monkeypatch.setattr(main_module, "ApplicationController", FakeController)
    monkeypatch.setattr(main_module, "TranslationManager", FakeTranslationManager)
    monkeypatch.setattr(main_module, "apply_theme", lambda _app, mode: applied_themes.append(mode))
    monkeypatch.setattr(main_module, "AppSettings", FakeSettings)

    assert main_module.main() == 0

    assert capsys.readouterr().out == "myLastFmPlayer 0.0.86\n"
    assert applied_themes == [ThemeMode.MINT]
    assert selected_themes == ["mint"]
    assert saved_languages == []
    assert saved_themes == []


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


def test_main_window_updates_progress_and_feedback(qapp) -> None:
    window = MainWindow()

    window.set_progress(140, "Downloading")
    window.append_feedback("Network error")

    assert window.progress_bar.value() == 100
    assert window.progress_bar.format() == "Downloading"
    assert "Network error" in window.feedback_log.toPlainText()


def test_feedback_messages_include_timestamp_prefix() -> None:
    assert format_feedback_message("Network error", QTime(9, 8, 7)) == (
        "09:08:07: Network error"
    )


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


def test_main_window_has_main_menu_actions_in_requested_order(qapp) -> None:
    window = MainWindow()

    assert window.main_menu.title() == "Main"
    assert [action.text() for action in window.main_menu.actions()] == [
        "Theme",
        "Preferences",
        "Open data folder in file manager",
        "Quit",
    ]


def test_main_window_file_cache_menu_action_emits_request(qapp) -> None:
    window = MainWindow()
    emissions: list[bool] = []
    window.file_cache_requested.connect(lambda: emissions.append(True))

    window.file_cache_action.trigger()

    assert emissions == [True]


def test_main_window_download_control_emits_download_signal(qapp) -> None:
    window = MainWindow()
    emissions: list[bool] = []
    window.download_requested.connect(lambda: emissions.append(True))

    window.download_toggle_button.click()

    assert emissions == [True]
    assert window.download_toggle_button.text() == "Start Downloads"


def test_main_window_download_toggle_switches_to_stop_and_back(qapp) -> None:
    window = MainWindow()
    stop_emissions: list[bool] = []
    start_emissions: list[bool] = []
    window.download_stop_requested.connect(lambda: stop_emissions.append(True))
    window.download_requested.connect(lambda: start_emissions.append(True))

    window.set_download_active(True)
    assert window.download_toggle_button.text() == "Stop Downloads"
    assert window.download_toggle_button.isEnabled()
    window.download_toggle_button.click()
    assert stop_emissions == [True]
    assert start_emissions == []

    window.set_download_active(False)
    assert window.download_toggle_button.text() == "Start Downloads"
    window.download_toggle_button.click()
    assert start_emissions == [True]


def test_main_window_workflow_enabled_toggles_fetch_and_download_controls(qapp) -> None:
    window = MainWindow()

    window.set_workflow_enabled(False)

    assert not window.fetch_button.isEnabled()
    assert not window.username_input.isEnabled()
    assert not window.refresh_action.isEnabled()
    assert not window.download_toggle_button.isEnabled()

    window.set_workflow_enabled(True)

    assert window.fetch_button.isEnabled()
    assert window.username_input.isEnabled()
    assert window.refresh_action.isEnabled()
    assert window.download_toggle_button.isEnabled()


def test_main_window_download_button_stays_enabled_while_active(qapp) -> None:
    window = MainWindow()

    window.set_download_active(True)
    window.set_workflow_enabled(False)

    assert window.download_toggle_button.isEnabled()
    assert window.download_toggle_button.text() == "Stop Downloads"


def test_main_window_playback_controls_emit_signals(qapp) -> None:
    window = MainWindow()
    events: list[str] = []
    window.play_requested.connect(lambda: events.append("play"))
    window.pause_requested.connect(lambda: events.append("pause"))
    window.stop_requested.connect(lambda: events.append("stop"))

    window.play_button.click()
    window.set_playback_controls(active=True)
    window.pause_button.click()
    window.stop_button.click()

    assert events == ["play", "pause", "stop"]


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

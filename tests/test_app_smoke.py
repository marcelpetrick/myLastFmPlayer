from __future__ import annotations

from PyQt6.QtCore import QEvent, QPointF, Qt
from PyQt6.QtGui import QMouseEvent

from my_lastfm_player import __display_version__, __version__
from my_lastfm_player import main as main_module
from my_lastfm_player.i18n import SUPPORTED_LANGUAGES
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.ui.main_window import MainWindow, application_title, format_playback_time
from my_lastfm_player.version import display_version


def test_package_version_is_defined() -> None:
    assert __version__ == "0.0.44"
    assert __display_version__ == "0.0.44"


def test_display_version_adds_build_commit_suffix() -> None:
    assert display_version("1.2.3", "abcdef123") == "1.2.3+abcdef"
    assert display_version("1.2.3", "") == "1.2.3"


def test_main_window_builds_mvp_shell(qapp) -> None:
    window = MainWindow()

    assert qapp.applicationName() in {"", "myLastFmPlayer"}
    assert window.windowTitle() == "myLastFmPlayer v0.0.44"
    assert window.username_input.placeholderText() == "Enter username"
    assert window.track_model.columnCount() == 3
    assert window.track_model.rowCount() == 2
    assert window.concurrency_input.value() == 2
    assert window.progress_bar.format() == "Idle"
    assert not window.fetch_pause_button.isEnabled()
    assert not window.fetch_stop_button.isEnabled()
    assert window.fetch_pause_button.toolTip()
    assert window.fetch_stop_button.toolTip()


def test_application_title_includes_version_suffix() -> None:
    assert application_title("1.2.3+abcdef") == "myLastFmPlayer v1.2.3+abcdef"


def test_main_prints_version_at_startup(monkeypatch, capsys) -> None:
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
        def connect(self, _slot) -> None:
            pass

    class FakeMainWindow:
        def __init__(self, **_kwargs) -> None:
            self.theme_requested = _FakeSignal()

        def show(self) -> None:
            return None

    class FakeController:
        def __init__(self, _window: FakeMainWindow) -> None:
            self.started = False

        def start(self) -> None:
            self.started = True

    monkeypatch.setattr(main_module, "QApplication", FakeApplication)
    monkeypatch.setattr(main_module, "MainWindow", FakeMainWindow)
    monkeypatch.setattr(main_module, "ApplicationController", FakeController)

    assert main_module.main() == 0

    assert capsys.readouterr().out == "myLastFmPlayer 0.0.44\n"


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
    assert window.track_model.data(window.track_model.index(1, 2)) == "Downloaded"
    assert window.selected_track() == tracks[1]


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
        "Fetch loved tracks",
        "Preferences",
        "Theme",
        "Quit",
    ]


def test_main_window_download_control_emits_download_signal(qapp) -> None:
    window = MainWindow()
    emissions: list[bool] = []
    window.download_requested.connect(lambda: emissions.append(True))

    window.download_toggle_button.click()

    assert emissions == [True]


def test_main_window_workflow_enabled_toggles_fetch_and_download_controls(qapp) -> None:
    window = MainWindow()

    window.set_workflow_enabled(False)

    assert not window.fetch_button.isEnabled()
    assert not window.username_input.isEnabled()
    assert not window.refresh_action.isEnabled()
    assert not window.download_toggle_button.isEnabled()
    assert not window.concurrency_input.isEnabled()

    window.set_workflow_enabled(True)

    assert window.fetch_button.isEnabled()
    assert window.username_input.isEnabled()
    assert window.refresh_action.isEnabled()
    assert window.download_toggle_button.isEnabled()
    assert window.concurrency_input.isEnabled()


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
    window.theme_light_action.trigger()

    assert themes == ["dark", "light"]


def test_main_window_theme_actions_are_exclusive(qapp) -> None:
    window = MainWindow()

    assert window.theme_light_action.isChecked()
    assert not window.theme_dark_action.isChecked()

    window.theme_dark_action.trigger()

    assert not window.theme_light_action.isChecked()
    assert window.theme_dark_action.isChecked()

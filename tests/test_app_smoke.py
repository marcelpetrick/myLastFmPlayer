from __future__ import annotations

import runpy
import sys
import types

import pytest
from PyQt6.QtCore import QBuffer, QByteArray, QEvent, QIODevice, QModelIndex, QPointF, Qt, QTime
from PyQt6.QtGui import QColor, QMouseEvent, QPixmap, QStandardItemModel
from PyQt6.QtWidgets import QSizePolicy

from my_lastfm_player import __display_version__, __version__
from my_lastfm_player import main as main_module
from my_lastfm_player.i18n import SUPPORTED_LANGUAGES, TranslationManager
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.themes import ThemeMode
from my_lastfm_player.ui import main_window as main_window_module
from my_lastfm_player.ui.main_window import (
    MainWindow,
    TrackFilterProxyModel,
    application_title,
    format_feedback_message,
    format_playback_time,
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
    assert __version__ == "0.0.132"
    assert __display_version__ == "0.0.132"


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
    assert window.windowTitle() == "myLastFmPlayer v0.0.132"
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

        def set_theme_mode(self, mode: str) -> None:
            selected_themes.append(mode)

        def set_randomize_playback(self, enabled: bool) -> None:
            selected_randomize.append(enabled)

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

    assert capsys.readouterr().out == "myLastFmPlayer 0.0.132\n"
    assert applied_themes == [ThemeMode.MINT]
    assert selected_themes == ["mint"]
    assert selected_randomize == [True]
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


def test_main_window_filters_tracks_by_artist_or_title_while_preserving_sort(qapp) -> None:
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
        window.random_track_excluding(tracks[0].cache_key, lambda candidates: candidates[0])
        is None
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
    window.next_requested.connect(lambda: events.append("next"))

    window.play_button.click()
    window.set_playback_controls(active=True)
    window.pause_button.click()
    window.stop_button.click()
    window.next_button.click()

    assert events == ["play", "pause", "stop", "next"]


def test_main_window_artist_image_is_clickable(qapp) -> None:
    window = MainWindow()
    requested_pages: list[str] = []
    window.artist_page_requested.connect(requested_pages.append)
    controls_layout = window.artist_image_group.parentWidget().layout()

    window.set_artist_image(png_bytes(), "https://www.last.fm/music/Artist")

    assert controls_layout.itemAt(0).widget() is window.playback_group
    assert controls_layout.itemAt(1).widget() is window.artist_image_group
    assert controls_layout.itemAt(2).widget() is window.downloads_group
    assert controls_layout.stretch(1) == 1
    assert window.artist_image_group.title() == "Artist"
    assert (
        window.artist_image_group.sizePolicy().horizontalPolicy()
        == QSizePolicy.Policy.Expanding
    )
    assert window.playback_group.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Minimum
    assert window.downloads_group.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Minimum
    assert window.artist_image_label.parentWidget() is window.artist_image_group
    assert (
        window.artist_image_label.sizePolicy().horizontalPolicy()
        == QSizePolicy.Policy.Expanding
    )
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


def test_main_window_retranslate_refreshes_example_rows_and_idle_labels(qapp) -> None:
    TranslationManager(qapp).set_language("en")
    window = MainWindow()
    window.dependency_label.clear()
    window._last_progress_label = "Idle"
    window._last_status_message = "Ready"

    window.retranslate_ui()

    assert window.track_model.rowCount() == 2
    assert (
        window.dependency_label.text()
        == "Dependencies: yt-dlp, ffmpeg, and ffprobe not checked yet"
    )
    assert window.progress_bar.format() == "Idle"
    assert window.statusBar().currentMessage() == "Ready"


def test_main_window_context_menu_emits_retry_for_track(qapp, monkeypatch) -> None:
    window = MainWindow()
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

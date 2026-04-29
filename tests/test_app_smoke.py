from __future__ import annotations

from my_lastfm_player import __version__
from my_lastfm_player import main as main_module
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.ui.main_window import MainWindow


def test_package_version_is_defined() -> None:
    assert __version__ == "00.00.10"


def test_main_window_builds_mvp_shell(qapp) -> None:
    window = MainWindow()

    assert qapp.applicationName() in {"", "myLastFmPlayer"}
    assert window.windowTitle() == "myLastFmPlayer v00.00.10"
    assert window.username_input.placeholderText() == "Enter username"
    assert window.track_model.columnCount() == 3
    assert window.track_model.rowCount() == 2
    assert window.concurrency_input.value() == 2
    assert window.progress_bar.format() == "Idle"


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

    class FakeMainWindow:
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

    assert capsys.readouterr().out == "myLastFmPlayer 00.00.10\n"


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


def test_main_window_updates_progress_and_feedback(qapp) -> None:
    window = MainWindow()

    window.set_progress(140, "Downloading")
    window.append_feedback("Network error")

    assert window.progress_bar.value() == 100
    assert window.progress_bar.format() == "Downloading"
    assert "Network error" in window.feedback_log.toPlainText()

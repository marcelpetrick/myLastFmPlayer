from __future__ import annotations

from PyQt6.QtWidgets import QApplication

from my_lastfm_player import __version__
from my_lastfm_player import main as main_module
from my_lastfm_player.ui.main_window import MainWindow


def test_package_version_is_defined() -> None:
    assert __version__ == "00.00.03"


def test_main_window_builds_mvp_shell() -> None:
    app = QApplication.instance() or QApplication([])

    window = MainWindow()

    assert app.applicationName() in {"", "myLastFmPlayer"}
    assert window.windowTitle() == "myLastFmPlayer v00.00.03"
    assert window.username_input.placeholderText() == "Enter username"
    assert window.track_table.columnCount() == 3
    assert window.track_table.rowCount() == 2
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

    monkeypatch.setattr(main_module, "QApplication", FakeApplication)
    monkeypatch.setattr(main_module, "MainWindow", FakeMainWindow)

    assert main_module.main() == 0

    assert capsys.readouterr().out == "myLastFmPlayer 00.00.03\n"

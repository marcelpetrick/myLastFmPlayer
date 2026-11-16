"""Reviewed snapshots of the constructed UI.

Regenerate after an intentional UI change and review the JSON diff::

    MY_LASTFM_PLAYER_UPDATE_GOLDEN=1 python -m pytest tests/test_ui_snapshots.py
"""

from __future__ import annotations

from pathlib import Path

import pytest
from PyQt6.QtCore import QSettings
from qt_snapshot import assert_matches_golden

from my_lastfm_player import settings as settings_module
from my_lastfm_player.scrobbling import ScrobblingService
from my_lastfm_player.ui.main_window import MainWindow
from my_lastfm_player.ui.preferences_dialog import PreferencesDialog


@pytest.fixture
def isolated_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Give AppSettings() a fresh INI store so the snapshot never sees user settings."""

    path = tmp_path / "settings.ini"
    real_init = settings_module.AppSettings.__init__

    def init(self, settings=None):
        real_init(self, settings or QSettings(str(path), QSettings.Format.IniFormat))

    monkeypatch.setattr(settings_module.AppSettings, "__init__", init)


def test_main_window_construction_matches_snapshot(qapp, isolated_settings) -> None:
    assert_matches_golden(MainWindow(), "ui_main_window")


def _service(state: str) -> ScrobblingService | None:
    if state == "without_credentials":
        return None
    service = ScrobblingService("key", "secret", username="Listener", scrobbling_enabled=False)
    if state == "connected":
        service._authenticated = True
        service._network = object()
    elif state == "authorizing":
        service._pending_auth_url = "https://www.last.fm/api/auth/?token=t"
    return service


@pytest.mark.parametrize(
    "state", ["without_credentials", "not_connected", "authorizing", "connected"]
)
def test_preferences_dialog_matches_snapshot_in_every_auth_state(
    qapp, isolated_settings, state
) -> None:
    parent = MainWindow()

    assert_matches_golden(PreferencesDialog(parent, _service(state)), f"ui_preferences_{state}")

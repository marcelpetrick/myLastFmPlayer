"""Exact contracts of the preferences dialog: sizing, auth flow, settings handlers."""

from __future__ import annotations

from typing import Any

import pytest
from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QFrame, QWidget
from test_preferences_dialog import FakeSettings, _make_svc

from my_lastfm_player.ui import preferences_dialog as preferences_module
from my_lastfm_player.ui.preferences_dialog import PreferencesDialog
from my_lastfm_player.workers import BackgroundCallWorker


class RecordingSettings(FakeSettings):
    def __init__(self) -> None:
        super().__init__()
        self.writes: list[tuple[str, object]] = []

    def set_ytdlp_cookies_browser(self, browser: str) -> None:
        self.writes.append(("browser", browser))
        super().set_ytdlp_cookies_browser(browser)

    def set_keep_data_on_quit(self, keep: bool) -> None:
        self.writes.append(("keep_data", keep))
        super().set_keep_data_on_quit(keep)

    def set_download_concurrency(self, concurrency: int) -> None:
        self.writes.append(("concurrency", concurrency))
        super().set_download_concurrency(concurrency)

    def set_scrobbling_enabled(self, enabled: bool) -> None:
        self.writes.append(("scrobbling", enabled))
        super().set_scrobbling_enabled(enabled)


@pytest.fixture
def settings(monkeypatch) -> RecordingSettings:
    recording = RecordingSettings()
    monkeypatch.setattr(preferences_module, "AppSettings", lambda: recording)
    return recording


def _hold_workers(dialog: PreferencesDialog) -> list[BackgroundCallWorker]:
    """Capture auth workers instead of running them, so busy state stays observable."""

    held: list[BackgroundCallWorker] = []
    dialog._start_auth_worker = held.append  # type: ignore[method-assign]
    return held


# --- widget tree and keyboard order ------------------------------------------------


def test_tab_order_follows_the_visual_layout(qapp) -> None:
    dialog = PreferencesDialog(None, None)  # type: ignore[arg-type]
    names = {
        id(widget): name for name, widget in vars(dialog).items() if isinstance(widget, QWidget)
    }

    chain: list[str] = []
    widget = dialog.nextInFocusChain()
    while widget is not dialog and len(chain) < 200:
        if id(widget) in names:
            chain.append(names[id(widget)])
        widget = widget.nextInFocusChain()

    assert chain == [
        "scroll_area",
        "scroll_content",
        "auth_group",
        "status_label",
        "authenticate_button",
        "authorize_button",
        "disconnect_button",
        "scrobbling_group",
        "scrobbling_checkbox",
        "scrobbling_hint",
        "youtube_group",
        "browser_label",
        "browser_combo",
        "concurrency_label",
        "concurrency_input",
        "youtube_hint",
        "privacy_group",
        "keep_data_checkbox",
        "keep_data_hint",
        "buttons",
    ]


# --- browser combo ---------------------------------------------------------------


def test_browser_combo_lists_every_choice_with_its_value(qapp, settings) -> None:
    dialog = PreferencesDialog(None, None)  # type: ignore[arg-type]
    combo = dialog.browser_combo

    assert [combo.itemText(i) for i in range(combo.count())] == [
        "None (disabled)",
        "firefox",
        "chromium",
        "chrome",
        "brave",
    ]
    assert [combo.itemData(i) for i in range(combo.count())] == [
        "",
        "firefox",
        "chromium",
        "chrome",
        "brave",
    ]


def test_browser_combo_labels_the_empty_choice_before_retranslation(
    qapp, settings, monkeypatch
) -> None:
    # Patched on the class: a subclass would change the tr() context.
    monkeypatch.setattr(PreferencesDialog, "retranslate_ui", lambda self: None)

    dialog = PreferencesDialog(None, None)  # type: ignore[arg-type]

    assert dialog.browser_combo.itemText(0) == "None (disabled)"


@pytest.mark.parametrize(("saved", "expected_index"), [("chrome", 3), ("", 0), ("opera", 0)])
def test_browser_combo_restores_saved_choice(qapp, settings, saved, expected_index) -> None:
    settings.browser = saved

    dialog = PreferencesDialog(None, None)  # type: ignore[arg-type]

    assert dialog.browser_combo.currentIndex() == expected_index


@pytest.mark.parametrize(
    ("index", "expected"),
    [(0, ""), (1, "firefox"), (4, "brave"), (5, ""), (-1, "")],
)
def test_browser_change_persists_only_valid_indexes(qapp, settings, index, expected) -> None:
    dialog = PreferencesDialog(None, None)  # type: ignore[arg-type]
    settings.browser = "unchanged"

    dialog._on_browser_changed(index)

    assert settings.browser == expected


def test_browser_change_maps_the_first_choice_itself(qapp, settings, monkeypatch) -> None:
    monkeypatch.setattr(preferences_module, "YTDLP_BROWSER_CHOICES", ["firefox", "chrome"])
    dialog = PreferencesDialog(None, None)  # type: ignore[arg-type]

    dialog._on_browser_changed(0)

    assert settings.browser == "firefox"


# --- restoring settings must not write them back --------------------------------------


def test_construction_does_not_write_back_restored_settings(qapp, settings) -> None:
    settings.concurrency = 4
    settings.keep_data = True

    PreferencesDialog(None, _make_svc())  # type: ignore[arg-type]

    assert [name for name, _value in settings.writes if name != "browser"] == []


def test_keep_data_toggle_persists_checked_state(qapp, settings) -> None:
    settings.keep_data = False
    dialog = PreferencesDialog(None, None)  # type: ignore[arg-type]

    dialog.keep_data_checkbox.setChecked(True)

    assert settings.writes[-1] == ("keep_data", True)


# --- refresh / busy states ----------------------------------------------------------


def test_missing_credentials_hide_the_authorize_button(qapp) -> None:
    dialog = PreferencesDialog(None, None)  # type: ignore[arg-type]

    assert dialog.authorize_button.isHidden()
    assert not dialog.disconnect_button.isEnabled()


def test_authenticate_shows_busy_state_while_worker_runs(qapp) -> None:
    dialog = PreferencesDialog(None, _make_svc())  # type: ignore[arg-type]
    held = _hold_workers(dialog)

    dialog._on_authenticate()

    assert len(held) == 1
    assert dialog.status_label.text() == "Starting Last.fm authentication…"
    assert not dialog.authenticate_button.isEnabled()
    assert not dialog.authorize_button.isEnabled()
    assert not dialog.disconnect_button.isEnabled()


def test_authorize_shows_busy_state_and_disables_disconnect(qapp) -> None:
    svc = _make_svc(session_key="k", username="testuser")
    svc.try_connect()
    dialog = PreferencesDialog(None, svc)  # type: ignore[arg-type]
    assert dialog.disconnect_button.isEnabled()
    held = _hold_workers(dialog)

    dialog._on_authorize()

    assert len(held) == 1
    assert dialog.status_label.text() == "Confirming Last.fm authorization…"
    assert not dialog.authenticate_button.isEnabled()
    assert not dialog.disconnect_button.isEnabled()


def test_authenticate_worker_tolerates_service_removed_meanwhile(qapp) -> None:
    dialog = PreferencesDialog(None, _make_svc())  # type: ignore[arg-type]
    held = _hold_workers(dialog)
    dialog._on_authenticate()
    dialog._service = None

    held[0].run()

    assert dialog.status_label.text() == (
        "⚠ Could not start authentication. Check API credentials."
    )


# --- worker thread ---------------------------------------------------------------------


def test_auth_worker_runs_on_a_named_daemon_thread(monkeypatch) -> None:
    created: list[dict[str, Any]] = []

    class FakeThread:
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs
            created.append(kwargs)
            self.started = False

        def start(self) -> None:
            created.append({"started": True})

    monkeypatch.setattr(preferences_module, "Thread", FakeThread)
    worker = BackgroundCallWorker(lambda: None)

    PreferencesDialog._start_auth_worker(worker)

    assert created == [
        {"target": worker.run, "name": "myLastFmPlayer-auth-call", "daemon": True},
        {"started": True},
    ]


# --- sizing ------------------------------------------------------------------------------


class _FakeScreen:
    def __init__(self, width: int, height: int) -> None:
        self._rect = QRect(0, 0, width, height)

    def availableGeometry(self) -> QRect:  # noqa: N802
        return self._rect


def _dialog_on_screen(monkeypatch, width: int, height: int) -> PreferencesDialog:
    screen = _FakeScreen(width, height)
    # Patched on the class: a subclass would change the tr() context.
    monkeypatch.setattr(PreferencesDialog, "screen", lambda self: screen)
    return PreferencesDialog(None, None)  # type: ignore[arg-type]


def test_small_screen_limits_never_drop_below_320(qapp, monkeypatch) -> None:
    dialog = _dialog_on_screen(monkeypatch, 300, 300)

    assert dialog.maximumWidth() == 320
    assert dialog.maximumHeight() == 320
    assert dialog.minimumWidth() == 320
    assert dialog.minimumHeight() == 320


def test_dialog_size_is_content_plus_margins_frame_buttons_and_spacing(qapp, monkeypatch) -> None:
    dialog = _dialog_on_screen(monkeypatch, 3000, 3000)
    filler = QWidget()
    filler.setMinimumSize(900, 900)
    dialog.scroll_content.layout().addWidget(filler)
    dialog.scroll_area.setFrameShape(QFrame.Shape.Box)
    dialog.scroll_area.setLineWidth(3)
    frame = dialog.scroll_area.frameWidth()
    assert frame > 0

    dialog._fit_to_content()

    content = dialog.scroll_content.sizeHint()
    assert content.width() >= 900
    assert dialog.width() == content.width() + 16 + 16 + 2 * frame
    assert dialog.height() == content.height() + dialog.buttons.sizeHint().height() + 16 + 16 + 12

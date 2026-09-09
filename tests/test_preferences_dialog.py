from __future__ import annotations

from threading import Event

from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from my_lastfm_player.scrobbling import ScrobblingService
from my_lastfm_player.ui import preferences_dialog as preferences_module
from my_lastfm_player.ui.preferences_dialog import PreferencesDialog
from my_lastfm_player.workers import BackgroundCallWorker


class FakeUser:
    def get_name(self, properly_capitalized: bool = False) -> str:
        return "testuser"


class FakeNetwork:
    def __init__(self, **kwargs) -> None:
        self.scrobbles: list[dict] = []
        self.now_playing: list[dict] = []

    def get_authenticated_user(self) -> FakeUser:
        return FakeUser()

    def scrobble(self, **kwargs) -> None:
        self.scrobbles.append(kwargs)

    def update_now_playing(self, **kwargs) -> None:
        self.now_playing.append(kwargs)


class FakeSG:
    def __init__(self, network) -> None:
        pass

    def get_web_auth_url(self) -> str:
        return "https://last.fm/api/auth/?token=tok"

    def get_web_auth_session_key(self, url: str) -> str:
        return "new_session_key"

    def get_web_auth_session_key_username(self, url: str) -> tuple[str, str]:
        return "new_session_key", "testuser"


class BrokenAuthSG:
    def __init__(self, network) -> None:
        pass

    def get_web_auth_url(self) -> str:
        raise RuntimeError("auth unavailable")


def _make_svc(**kwargs) -> ScrobblingService:
    return ScrobblingService(
        api_key="key",
        api_secret="secret",
        network_factory=lambda **kw: FakeNetwork(**kw),
        sg_factory=FakeSG,
        **kwargs,
    )


def run_auth_workers_inline(dialog: PreferencesDialog) -> None:
    """Make authentication workers deterministic for focused dialog tests."""

    dialog._start_auth_worker = lambda worker: worker.run()  # type: ignore[method-assign]


class FakeSettings:
    def __init__(self) -> None:
        self.browser = ""
        self.keep_data = True
        self.concurrency = 4
        self.scrobbling = True

    def ytdlp_cookies_browser(self) -> str:
        return self.browser

    def set_ytdlp_cookies_browser(self, browser: str) -> None:
        self.browser = browser

    def keep_data_on_quit(self) -> bool:
        return self.keep_data

    def set_keep_data_on_quit(self, keep: bool) -> None:
        self.keep_data = keep

    def download_concurrency(self) -> int:
        return self.concurrency

    def set_download_concurrency(self, concurrency: int) -> None:
        self.concurrency = concurrency

    def set_scrobbling_enabled(self, enabled: bool) -> None:
        self.scrobbling = enabled


def test_preferences_dialog_shows_not_connected(qapp) -> None:
    svc = _make_svc()
    dialog = PreferencesDialog(None, svc)  # type: ignore[arg-type]

    assert "Not connected" in dialog.status_label.text()
    assert dialog.authenticate_button.isEnabled()
    assert dialog.authorize_button.isHidden()
    assert not dialog.disconnect_button.isEnabled()
    assert dialog.scrobbling_checkbox.isEnabled()


def test_preferences_dialog_shows_connected(qapp) -> None:
    svc = _make_svc(session_key="k", username="testuser")
    svc.try_connect()
    dialog = PreferencesDialog(None, svc)  # type: ignore[arg-type]

    assert "testuser" in dialog.status_label.text()
    assert not dialog.authenticate_button.isEnabled()
    assert dialog.authorize_button.isHidden()
    assert dialog.disconnect_button.isEnabled()


def test_preferences_dialog_shows_no_credentials(qapp) -> None:
    svc = ScrobblingService(api_key="", api_secret="")
    dialog = PreferencesDialog(None, svc)  # type: ignore[arg-type]

    assert "API credentials not configured" in dialog.status_label.text()
    assert not dialog.authenticate_button.isEnabled()
    assert not dialog.scrobbling_checkbox.isEnabled()


def test_preferences_dialog_none_service(qapp) -> None:
    dialog = PreferencesDialog(None, None)  # type: ignore[arg-type]

    assert "API credentials not configured" in dialog.status_label.text()
    assert not dialog.authenticate_button.isEnabled()


def test_preferences_dialog_authenticate_starts_auth(qapp, monkeypatch) -> None:
    opened: list[str] = []
    monkeypatch.setattr("webbrowser.open", lambda url: not opened.append(url))
    svc = _make_svc()
    dialog = PreferencesDialog(None, svc)  # type: ignore[arg-type]
    run_auth_workers_inline(dialog)

    dialog.authenticate_button.click()

    assert svc.auth_in_progress
    assert opened == ["https://last.fm/api/auth/?token=tok"]
    assert not dialog.authorize_button.isHidden()


def test_preferences_dialog_authenticate_failure_shows_error(qapp) -> None:
    svc = ScrobblingService(
        api_key="key",
        api_secret="secret",
        network_factory=lambda **kw: FakeNetwork(**kw),
        sg_factory=BrokenAuthSG,
    )
    dialog = PreferencesDialog(None, svc)  # type: ignore[arg-type]
    run_auth_workers_inline(dialog)

    dialog._on_authenticate()

    assert not svc.auth_in_progress
    assert "Could not start authentication" in dialog.status_label.text()


def test_preferences_dialog_browser_failure_keeps_manual_link(qapp, monkeypatch) -> None:
    monkeypatch.setattr("webbrowser.open", lambda _url: False)
    svc = _make_svc()
    dialog = PreferencesDialog(None, svc)  # type: ignore[arg-type]
    run_auth_workers_inline(dialog)

    dialog._on_authenticate()

    assert "Could not open the browser" in dialog.status_label.text()
    assert "https://last.fm/api/auth/?token=tok" in dialog.status_label.text()
    assert dialog.status_label.textInteractionFlags() & Qt.TextInteractionFlag.TextSelectableByMouse
    assert dialog.authorize_button.isEnabled()


def test_preferences_dialog_authorization_keeps_controls_responsive(qapp) -> None:
    started = Event()
    release = Event()
    svc = _make_svc()
    assert svc.start_web_auth()

    def complete_auth() -> bool:
        started.set()
        release.wait(timeout=2)
        return False

    svc.complete_web_auth = complete_auth  # type: ignore[method-assign]
    dialog = PreferencesDialog(None, svc)  # type: ignore[arg-type]

    dialog._on_authorize()

    assert started.wait(timeout=1)
    assert not dialog.authorize_button.isEnabled()
    assert dialog.concurrency_input.isEnabled()

    release.set()
    for _attempt in range(20):
        QTest.qWait(10)
        if not dialog._active_auth_workers:
            break
    assert not dialog._active_auth_workers
    assert "Authorization not confirmed" in dialog.status_label.text()


def test_preferences_dialog_close_invalidates_in_flight_authentication(qapp) -> None:
    started = Event()
    release = Event()
    svc = _make_svc()
    assert svc.start_web_auth()

    def complete_auth() -> bool:
        started.set()
        release.wait(timeout=2)
        return True

    svc.complete_web_auth = complete_auth  # type: ignore[method-assign]
    dialog = PreferencesDialog(None, svc)  # type: ignore[arg-type]
    dialog._on_authorize()
    assert started.wait(timeout=1)

    dialog.reject()
    release.set()
    for _attempt in range(20):
        QTest.qWait(10)
        if not dialog._active_auth_workers:
            break

    assert not svc.is_authenticated
    assert not svc.auth_in_progress
    assert not dialog._active_auth_workers


def test_preferences_dialog_reports_unexpected_background_auth_error(qapp) -> None:
    dialog = PreferencesDialog(None, _make_svc())  # type: ignore[arg-type]
    run_auth_workers_inline(dialog)

    def fail() -> object:
        raise RuntimeError("transport unavailable")

    dialog._run_auth_call(fail, lambda _result: None)

    assert "Last.fm authentication failed: transport unavailable" in dialog.status_label.text()
    assert dialog._active_auth_workers == []
    dialog._forget_auth_worker(BackgroundCallWorker(lambda: None))


def test_preferences_dialog_authorize_completes_auth(qapp, monkeypatch) -> None:
    monkeypatch.setattr("webbrowser.open", lambda url: True)
    svc = _make_svc()
    dialog = PreferencesDialog(None, svc)  # type: ignore[arg-type]
    run_auth_workers_inline(dialog)

    dialog.authenticate_button.click()
    dialog.authorize_button.click()

    assert svc.is_authenticated
    assert svc.username == "testuser"
    assert not svc.auth_in_progress
    assert "testuser" in dialog.status_label.text()


def test_preferences_dialog_authorize_without_start_shows_error(qapp) -> None:
    svc = _make_svc()
    dialog = PreferencesDialog(None, svc)  # type: ignore[arg-type]
    run_auth_workers_inline(dialog)
    dialog.authorize_button.setVisible(True)

    dialog._on_authorize()

    assert not svc.is_authenticated


def test_preferences_dialog_disconnect_clears_session(qapp) -> None:
    svc = _make_svc(session_key="k", username="testuser")
    svc.try_connect()
    dialog = PreferencesDialog(None, svc)  # type: ignore[arg-type]

    dialog.disconnect_button.click()

    assert not svc.is_authenticated
    assert "Not connected" in dialog.status_label.text()


def test_preferences_dialog_scrobbling_toggle(qapp) -> None:
    svc = _make_svc()
    dialog = PreferencesDialog(None, svc)  # type: ignore[arg-type]

    dialog.scrobbling_checkbox.setChecked(False)
    assert not svc.scrobbling_enabled

    dialog.scrobbling_checkbox.setChecked(True)
    assert svc.scrobbling_enabled


def test_preferences_dialog_scrobbling_toggle_persists(qapp, monkeypatch) -> None:
    settings = FakeSettings()
    monkeypatch.setattr(preferences_module, "AppSettings", lambda: settings)
    svc = _make_svc()
    dialog = PreferencesDialog(None, svc)  # type: ignore[arg-type]

    dialog.scrobbling_checkbox.setChecked(False)

    assert not svc.scrobbling_enabled
    assert not settings.scrobbling


def test_preferences_dialog_scrobbling_checkbox_checked_by_default(qapp) -> None:
    svc = _make_svc()
    dialog = PreferencesDialog(None, svc)  # type: ignore[arg-type]

    assert dialog.scrobbling_checkbox.isChecked()


def test_preferences_dialog_auth_in_progress_state(qapp, monkeypatch) -> None:
    monkeypatch.setattr("webbrowser.open", lambda url: True)
    svc = _make_svc()
    dialog = PreferencesDialog(None, svc)  # type: ignore[arg-type]
    run_auth_workers_inline(dialog)

    dialog._on_authenticate()

    status = dialog.status_label.text().lower()
    assert "authorized" in status or "browser" in status
    assert not dialog.authenticate_button.isEnabled()
    assert not dialog.authorize_button.isHidden()
    assert not dialog.disconnect_button.isEnabled()


def test_preferences_dialog_buttons_ignore_none_service(qapp) -> None:
    dialog = PreferencesDialog(None, None)  # type: ignore[arg-type]
    run_auth_workers_inline(dialog)

    dialog._on_authenticate()
    dialog._on_authorize()
    dialog._on_disconnect()
    dialog._on_scrobbling_toggled(1)


def test_preferences_dialog_download_concurrency_persists(qapp, monkeypatch) -> None:
    settings = FakeSettings()
    monkeypatch.setattr(preferences_module, "AppSettings", lambda: settings)

    dialog = PreferencesDialog(None, None)  # type: ignore[arg-type]

    assert dialog.concurrency_input.minimum() == 1
    assert dialog.concurrency_input.maximum() == 5
    assert dialog.concurrency_input.value() == 4

    dialog.concurrency_input.setValue(5)

    assert settings.concurrency == 5


def test_preferences_dialog_keep_data_toggle_persists(qapp, monkeypatch) -> None:
    settings = FakeSettings()
    monkeypatch.setattr(preferences_module, "AppSettings", lambda: settings)

    dialog = PreferencesDialog(None, None)  # type: ignore[arg-type]
    assert dialog.keep_data_checkbox.isChecked()
    assert "Downloaded audio files remain" in dialog.keep_data_hint.text()

    dialog.keep_data_checkbox.setChecked(False)

    assert not settings.keep_data


def test_preferences_dialog_bounds_content_and_keeps_close_button_outside_scroll(qapp) -> None:
    dialog = PreferencesDialog(None, None)  # type: ignore[arg-type]
    available = dialog.screen().availableGeometry()

    assert dialog.minimumWidth() >= preferences_module.PREFERENCES_MINIMUM_WIDTH
    assert dialog.maximumWidth() <= int(
        available.width() * preferences_module.PREFERENCES_SCREEN_FRACTION
    )
    assert dialog.maximumHeight() <= int(
        available.height() * preferences_module.PREFERENCES_SCREEN_FRACTION
    )
    assert dialog.scroll_area.widget() is dialog.scroll_content
    assert dialog.buttons.parentWidget() is dialog


def test_preferences_dialog_scrolls_at_large_font_with_close_reachable(qapp) -> None:
    dialog = PreferencesDialog(None, None)  # type: ignore[arg-type]
    font = dialog.font()
    font.setPointSize(16)
    dialog.setFont(font)
    dialog.retranslate_ui()
    dialog.show()
    qapp.processEvents()
    available = dialog.screen().availableGeometry()

    assert dialog.height() <= int(
        available.height() * preferences_module.PREFERENCES_SCREEN_FRACTION
    )
    assert dialog.scroll_area.verticalScrollBar().maximum() > 0
    assert dialog.buttons.isVisible()
    assert dialog.buttons.geometry().bottom() <= dialog.contentsRect().bottom()


def test_preferences_dialog_keeps_sections_fixed_when_expanded(qapp) -> None:
    dialog = PreferencesDialog(None, None)  # type: ignore[arg-type]

    fixed_policy = preferences_module.QSizePolicy.Policy.Fixed

    assert dialog.auth_group.sizePolicy().verticalPolicy() == fixed_policy
    assert dialog.scrobbling_group.sizePolicy().verticalPolicy() == fixed_policy
    assert dialog.youtube_group.sizePolicy().verticalPolicy() == fixed_policy
    assert dialog.privacy_group.sizePolicy().verticalPolicy() == fixed_policy

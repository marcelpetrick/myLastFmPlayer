"""Last.fm preferences dialog: authentication and scrobbling settings."""

from __future__ import annotations

import webbrowser
from collections.abc import Callable
from threading import Thread

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from my_lastfm_player.scrobbling import ScrobblingService
from my_lastfm_player.settings import (
    MAX_DOWNLOAD_CONCURRENCY,
    MIN_DOWNLOAD_CONCURRENCY,
    YTDLP_BROWSER_CHOICES,
    AppSettings,
)
from my_lastfm_player.workers import BackgroundCallWorker

PREFERENCES_MINIMUM_WIDTH = 520
PREFERENCES_MINIMUM_HEIGHT = 360
PREFERENCES_SCREEN_FRACTION = 0.9


class PreferencesDialog(QDialog):  # pylint: disable=too-many-instance-attributes
    """Modal preferences dialog for Last.fm authentication and scrobbling."""

    def __init__(self, parent: QWidget, service: ScrobblingService | None) -> None:
        super().__init__(parent)
        self._service = service
        self._settings = AppSettings()
        self._active_auth_workers: list[BackgroundCallWorker] = []
        self.setMinimumWidth(PREFERENCES_MINIMUM_WIDTH)
        self._build_ui()
        self.retranslate_ui()
        self._refresh()
        self._fit_to_content()

    def _build_ui(self) -> None:  # pylint: disable=too-many-statements
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll_content = QWidget(self.scroll_area)
        content_layout = QVBoxLayout(self.scroll_content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area, stretch=1)

        # ── Authentication group ────────────────────────────────────────
        self.auth_group = QGroupBox(self)
        self.auth_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        auth_layout = QVBoxLayout(self.auth_group)

        self.status_label = QLabel(self)
        self.status_label.setWordWrap(True)

        btn_row = QHBoxLayout()
        self.authenticate_button = QPushButton(self)
        self.authorize_button = QPushButton(self)
        self.disconnect_button = QPushButton(self)
        btn_row.addWidget(self.authenticate_button)
        btn_row.addWidget(self.authorize_button)
        btn_row.addWidget(self.disconnect_button)
        btn_row.addStretch()

        auth_layout.addWidget(self.status_label)
        auth_layout.addLayout(btn_row)
        content_layout.addWidget(self.auth_group)

        # ── Scrobbling group ────────────────────────────────────────────
        self.scrobbling_group = QGroupBox(self)
        self.scrobbling_group.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        scrobbling_layout = QVBoxLayout(self.scrobbling_group)
        self.scrobbling_checkbox = QCheckBox(self)
        self.scrobbling_hint = QLabel(self)
        self.scrobbling_hint.setWordWrap(True)
        scrobbling_layout.addWidget(self.scrobbling_checkbox)
        scrobbling_layout.addWidget(self.scrobbling_hint)
        content_layout.addWidget(self.scrobbling_group)

        # ── YouTube group ───────────────────────────────────────────────
        self.youtube_group = QGroupBox(self)
        self.youtube_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        youtube_layout = QVBoxLayout(self.youtube_group)
        browser_row = QHBoxLayout()
        self.browser_label = QLabel(self)
        self.browser_combo = QComboBox(self)
        self.browser_label.setBuddy(self.browser_combo)
        self._browser_values = YTDLP_BROWSER_CHOICES
        browser_row.addWidget(self.browser_label)
        browser_row.addWidget(self.browser_combo)
        browser_row.addStretch()
        concurrency_row = QHBoxLayout()
        self.concurrency_label = QLabel(self)
        self.concurrency_input = QSpinBox(self)
        self.concurrency_label.setBuddy(self.concurrency_input)
        self.concurrency_input.setRange(MIN_DOWNLOAD_CONCURRENCY, MAX_DOWNLOAD_CONCURRENCY)
        concurrency_row.addWidget(self.concurrency_label)
        concurrency_row.addWidget(self.concurrency_input)
        concurrency_row.addStretch()
        self.youtube_hint = QLabel(self)
        self.youtube_hint.setWordWrap(True)
        youtube_layout.addLayout(browser_row)
        youtube_layout.addLayout(concurrency_row)
        youtube_layout.addWidget(self.youtube_hint)
        content_layout.addWidget(self.youtube_group)

        # ── Privacy group ───────────────────────────────────────────────
        self.privacy_group = QGroupBox(self)
        self.privacy_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        privacy_layout = QVBoxLayout(self.privacy_group)
        self.keep_data_checkbox = QCheckBox(self)
        self.keep_data_hint = QLabel(self)
        self.keep_data_hint.setWordWrap(True)
        privacy_layout.addWidget(self.keep_data_checkbox)
        privacy_layout.addWidget(self.keep_data_hint)
        content_layout.addWidget(self.privacy_group)
        content_layout.addStretch(1)

        # ── Close button ────────────────────────────────────────────────
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, self)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        # Connections
        self.authenticate_button.clicked.connect(self._on_authenticate)
        self.authorize_button.clicked.connect(self._on_authorize)
        self.disconnect_button.clicked.connect(self._on_disconnect)
        self.scrobbling_checkbox.stateChanged.connect(self._on_scrobbling_toggled)
        self.browser_combo.currentIndexChanged.connect(self._on_browser_changed)
        self.concurrency_input.valueChanged.connect(self._on_concurrency_changed)
        self.keep_data_checkbox.stateChanged.connect(self._on_keep_data_toggled)

        # Populate and restore browser selection
        current_browser = self._settings.ytdlp_cookies_browser()
        for value in self._browser_values:
            self.browser_combo.addItem(value or self.tr("None (disabled)"), value)
        saved_index = (
            self._browser_values.index(current_browser)
            if current_browser in self._browser_values
            else 0
        )
        self.browser_combo.setCurrentIndex(saved_index)

        self.concurrency_input.blockSignals(True)
        self.concurrency_input.setValue(self._settings.download_concurrency())
        self.concurrency_input.blockSignals(False)

        # Restore keep-data-on-quit setting
        self.keep_data_checkbox.blockSignals(True)
        self.keep_data_checkbox.setChecked(self._settings.keep_data_on_quit())
        self.keep_data_checkbox.blockSignals(False)

    def retranslate_ui(self) -> None:
        """Apply current translations to all static labels."""

        self.setWindowTitle(self.tr("Preferences"))
        self.auth_group.setTitle(self.tr("Last.fm Authentication"))
        self.authenticate_button.setText(self.tr("Authenticate with Last.fm"))
        self.authorize_button.setText(self.tr("I've authorized"))
        self.disconnect_button.setText(self.tr("Disconnect"))
        self.scrobbling_group.setTitle(self.tr("Scrobbling"))
        self.scrobbling_checkbox.setText(self.tr("Enable scrobbling"))
        self.scrobbling_hint.setText(
            self.tr("Submits to Last.fm after 33% of each track has been played.")
        )
        self.youtube_group.setTitle(self.tr("YouTube Downloads"))
        self.browser_label.setText(self.tr("Browser cookies:"))
        self.concurrency_label.setText(self.tr("Parallel YouTube checks and downloads:"))
        self.browser_combo.setAccessibleName(self.tr("Browser cookies:"))
        self.concurrency_input.setAccessibleName(
            self.tr("Parallel YouTube checks and downloads:")
        )
        self.youtube_hint.setText(
            self.tr(
                "Select the browser whose YouTube login cookies yt-dlp should use. "
                "Required for age-restricted videos. You must be signed into YouTube "
                "in the selected browser. The parallel-work limit applies to new YouTube "
                "checks and downloads."
            )
        )
        self.browser_combo.setItemText(0, self.tr("None (disabled)"))
        self.privacy_group.setTitle(self.tr("Privacy"))
        self.keep_data_checkbox.setText(
            self.tr("Keep saved library and Last.fm session after quitting")
        )
        self.keep_data_hint.setText(
            self.tr(
                "When disabled, closing the app deletes saved track lists, lookup and "
                "download caches, and Last.fm authentication. Downloaded audio files remain."
            )
        )
        self._fit_to_content()

    def _refresh(self) -> None:
        if self._service is None or not self._service.has_api_credentials:
            self.status_label.setText(
                self.tr(
                    "⚠ API credentials not configured.\n"
                    "Set LASTFM_API_KEY and LASTFM_API_SECRET environment variables."
                )
            )
            self.authenticate_button.setEnabled(False)
            self.authorize_button.setVisible(False)
            self.disconnect_button.setEnabled(False)
            self.scrobbling_checkbox.setEnabled(False)
            self._fit_to_content()
            return

        self.scrobbling_checkbox.setEnabled(True)
        self.scrobbling_checkbox.blockSignals(True)
        self.scrobbling_checkbox.setChecked(self._service.scrobbling_enabled)
        self.scrobbling_checkbox.blockSignals(False)

        if self._service.is_authenticated:
            self.status_label.setText(
                self.tr("🟢 Connected as {username}").format(
                    username=self._service.username
                )
            )
            self.authenticate_button.setEnabled(False)
            self.authorize_button.setVisible(False)
            self.authorize_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
        elif self._service.auth_in_progress:
            self.status_label.setText(
                self.tr("🔵 Browser opened — authorize the app, then click «I've authorized».")
            )
            self.authenticate_button.setEnabled(False)
            self.authorize_button.setVisible(True)
            self.authorize_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)
        else:
            self.status_label.setText(self.tr("🔴 Not connected"))
            self.authenticate_button.setEnabled(True)
            self.authorize_button.setVisible(False)
            self.authorize_button.setEnabled(False)
            self.disconnect_button.setEnabled(False)
        self._fit_to_content()

    def _fit_to_content(self) -> None:
        self.layout().activate()
        self.scroll_content.adjustSize()
        available = self.screen().availableGeometry()
        maximum_width = max(320, int(available.width() * PREFERENCES_SCREEN_FRACTION))
        maximum_height = max(320, int(available.height() * PREFERENCES_SCREEN_FRACTION))
        margins = self.layout().contentsMargins()
        frame_width = self.scroll_area.frameWidth() * 2
        content_hint = self.scroll_content.sizeHint()
        target_width = min(
            maximum_width,
            max(
                PREFERENCES_MINIMUM_WIDTH,
                content_hint.width() + margins.left() + margins.right() + frame_width,
            ),
        )
        target_height = min(
            maximum_height,
            content_hint.height()
            + self.buttons.sizeHint().height()
            + margins.top()
            + margins.bottom()
            + self.layout().spacing(),
        )
        self.setMinimumSize(
            min(PREFERENCES_MINIMUM_WIDTH, maximum_width),
            min(PREFERENCES_MINIMUM_HEIGHT, maximum_height),
        )
        self.setMaximumSize(maximum_width, maximum_height)
        self.resize(target_width, max(self.minimumHeight(), target_height))

    def _on_authenticate(self) -> None:
        if self._service is None:
            return
        self._set_auth_busy(self.tr("Starting Last.fm authentication…"))

        def start_auth() -> tuple[str | None, bool]:
            url = self._service.start_web_auth() if self._service is not None else None
            return url, bool(url and webbrowser.open(url))

        self._run_auth_call(start_auth, self._handle_auth_started)

    def _handle_auth_started(self, result: object) -> None:
        url, browser_opened = result if isinstance(result, tuple) else (None, False)
        self._refresh()
        if not url:
            self.status_label.setText(
                self.tr("⚠ Could not start authentication. Check API credentials.")
            )
        elif not browser_opened:
            self.status_label.setText(
                self.tr(
                    "⚠ Could not open the browser. Open this authorization link manually: "
                    "{url}"
                ).format(url=url)
            )
            self.status_label.setTextInteractionFlags(
                self.status_label.textInteractionFlags()
                | Qt.TextInteractionFlag.TextSelectableByMouse
            )
        self._fit_to_content()

    def _on_authorize(self) -> None:
        if self._service is None:
            return
        self._set_auth_busy(self.tr("Confirming Last.fm authorization…"))
        self._run_auth_call(
            self._service.complete_web_auth,
            self._handle_auth_completed,
        )

    def _handle_auth_completed(self, result: object) -> None:
        self._refresh()
        if not result:
            self.status_label.setText(
                self.tr(
                    "⚠ Authorization not confirmed yet. "
                    "Authorize in the browser, then try again."
                )
            )
            self._fit_to_content()

    def _set_auth_busy(self, message: str) -> None:
        self.status_label.setText(message)
        self.authenticate_button.setEnabled(False)
        self.authorize_button.setEnabled(False)
        self.disconnect_button.setEnabled(False)

    def _run_auth_call(
        self,
        operation: Callable[[], object],
        on_result: Callable[[object], None],
    ) -> None:
        worker = BackgroundCallWorker(operation)
        worker.result.connect(lambda _worker, result: on_result(result))
        worker.failed.connect(self._handle_auth_call_error)
        worker.finished.connect(self._forget_auth_worker)
        self._active_auth_workers.append(worker)
        self._start_auth_worker(worker)

    @staticmethod
    def _start_auth_worker(worker: BackgroundCallWorker) -> None:
        Thread(
            target=worker.run,
            name="myLastFmPlayer-auth-call",
            daemon=True,
        ).start()

    def _handle_auth_call_error(
        self, _worker: BackgroundCallWorker, error: Exception
    ) -> None:
        self._refresh()
        self.status_label.setText(
            self.tr("⚠ Last.fm authentication failed: {error}").format(error=error)
        )
        self._fit_to_content()

    def _forget_auth_worker(self, worker: BackgroundCallWorker) -> None:
        if worker in self._active_auth_workers:
            self._active_auth_workers.remove(worker)

    def reject(self) -> None:
        """Close the dialog without allowing late authentication state changes."""

        if self._active_auth_workers:
            for worker in tuple(self._active_auth_workers):
                worker.cancel()
            if self._service is not None:
                self._service.cancel_pending_authentication()
        super().reject()

    def _on_disconnect(self) -> None:
        if self._service is None:
            return
        self._service.disconnect()
        self._refresh()

    def _on_scrobbling_toggled(self, state: int) -> None:
        if self._service is None:
            return
        enabled = bool(state)
        self._service.scrobbling_enabled = enabled
        self._settings.set_scrobbling_enabled(enabled)

    def _on_browser_changed(self, index: int) -> None:
        browser = self._browser_values[index] if 0 <= index < len(self._browser_values) else ""
        self._settings.set_ytdlp_cookies_browser(browser)

    def _on_concurrency_changed(self, value: int) -> None:
        self._settings.set_download_concurrency(value)

    def _on_keep_data_toggled(self, state: int) -> None:
        self._settings.set_keep_data_on_quit(bool(state))

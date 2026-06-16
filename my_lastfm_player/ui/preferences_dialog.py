"""Last.fm preferences dialog: authentication and scrobbling settings."""

from __future__ import annotations

import webbrowser

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
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

PREFERENCES_MINIMUM_WIDTH = 520


class PreferencesDialog(QDialog):  # pylint: disable=too-many-instance-attributes
    """Modal preferences dialog for Last.fm authentication and scrobbling."""

    def __init__(self, parent: QWidget, service: ScrobblingService | None) -> None:
        super().__init__(parent)
        self._service = service
        self._settings = AppSettings()
        self.setMinimumWidth(PREFERENCES_MINIMUM_WIDTH)
        self._build_ui()
        self.retranslate_ui()
        self._refresh()
        self._fit_to_content()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # ── Authentication group ────────────────────────────────────────
        self.auth_group = QGroupBox(self)
        self.auth_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        auth_layout = QVBoxLayout(self.auth_group)

        self.status_label = QLabel(self)

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
        layout.addWidget(self.auth_group)

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
        layout.addWidget(self.scrobbling_group)

        # ── YouTube group ───────────────────────────────────────────────
        self.youtube_group = QGroupBox(self)
        self.youtube_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        youtube_layout = QVBoxLayout(self.youtube_group)
        browser_row = QHBoxLayout()
        self.browser_label = QLabel(self)
        self.browser_combo = QComboBox(self)
        self._browser_values = YTDLP_BROWSER_CHOICES
        browser_row.addWidget(self.browser_label)
        browser_row.addWidget(self.browser_combo)
        browser_row.addStretch()
        concurrency_row = QHBoxLayout()
        self.concurrency_label = QLabel(self)
        self.concurrency_input = QSpinBox(self)
        self.concurrency_input.setRange(MIN_DOWNLOAD_CONCURRENCY, MAX_DOWNLOAD_CONCURRENCY)
        concurrency_row.addWidget(self.concurrency_label)
        concurrency_row.addWidget(self.concurrency_input)
        concurrency_row.addStretch()
        self.youtube_hint = QLabel(self)
        self.youtube_hint.setWordWrap(True)
        youtube_layout.addLayout(browser_row)
        youtube_layout.addLayout(concurrency_row)
        youtube_layout.addWidget(self.youtube_hint)
        layout.addWidget(self.youtube_group)

        # ── Privacy group ───────────────────────────────────────────────
        self.privacy_group = QGroupBox(self)
        self.privacy_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        privacy_layout = QVBoxLayout(self.privacy_group)
        self.keep_data_checkbox = QCheckBox(self)
        privacy_layout.addWidget(self.keep_data_checkbox)
        layout.addWidget(self.privacy_group)
        layout.addStretch(1)

        # ── Close button ────────────────────────────────────────────────
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, self)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

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
        self.concurrency_label.setText(self.tr("Parallel downloads:"))
        self.youtube_hint.setText(
            self.tr(
                "Select the browser whose YouTube login cookies yt-dlp should use. "
                "Required for age-restricted videos. You must be signed into YouTube "
                "in the selected browser. Parallel download changes apply to new work."
            )
        )
        self.browser_combo.setItemText(0, self.tr("None (disabled)"))
        self.privacy_group.setTitle(self.tr("Privacy"))
        self.keep_data_checkbox.setText(self.tr("Keep cached data after quitting"))
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
            self.disconnect_button.setEnabled(True)
        elif self._service.auth_in_progress:
            self.status_label.setText(
                self.tr("🔵 Browser opened — authorize the app, then click «I've authorized».")
            )
            self.authenticate_button.setEnabled(False)
            self.authorize_button.setVisible(True)
            self.disconnect_button.setEnabled(False)
        else:
            self.status_label.setText(self.tr("🔴 Not connected"))
            self.authenticate_button.setEnabled(True)
            self.authorize_button.setVisible(False)
            self.disconnect_button.setEnabled(False)
        self._fit_to_content()

    def _fit_to_content(self) -> None:
        self.layout().activate()
        minimum_size = self.minimumSizeHint()
        self.setMinimumSize(
            max(PREFERENCES_MINIMUM_WIDTH, minimum_size.width()),
            minimum_size.height(),
        )
        self.resize(max(self.width(), self.minimumWidth()), self.minimumHeight())

    def _on_authenticate(self) -> None:
        if self._service is None:
            return
        url = self._service.start_web_auth()
        if url:
            webbrowser.open(url)
        else:
            self.status_label.setText(
                self.tr("⚠ Could not start authentication. Check API credentials.")
            )
        self._refresh()

    def _on_authorize(self) -> None:
        if self._service is None:
            return
        if self._service.complete_web_auth():
            self._refresh()
        else:
            self.status_label.setText(
                self.tr(
                    "⚠ Authorization not confirmed yet. "
                    "Authorize in the browser, then try again."
                )
            )

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

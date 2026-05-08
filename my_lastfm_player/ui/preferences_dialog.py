"""Last.fm preferences dialog: authentication and scrobbling settings."""

from __future__ import annotations

import webbrowser

from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from my_lastfm_player.scrobbling import ScrobblingService


class PreferencesDialog(QDialog):
    """Modal preferences dialog for Last.fm authentication and scrobbling."""

    def __init__(self, parent: QWidget, service: ScrobblingService | None) -> None:
        super().__init__(parent)
        self._service = service
        self.setMinimumWidth(420)
        self._build_ui()
        self.retranslate_ui()
        self._refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # ── Authentication group ────────────────────────────────────────
        self.auth_group = QGroupBox(self)
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
        scrobbling_layout = QVBoxLayout(self.scrobbling_group)
        self.scrobbling_checkbox = QCheckBox(self)
        self.scrobbling_hint = QLabel(self)
        self.scrobbling_hint.setWordWrap(True)
        scrobbling_layout.addWidget(self.scrobbling_checkbox)
        scrobbling_layout.addWidget(self.scrobbling_hint)
        layout.addWidget(self.scrobbling_group)

        # ── Close button ────────────────────────────────────────────────
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, self)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Connections
        self.authenticate_button.clicked.connect(self._on_authenticate)
        self.authorize_button.clicked.connect(self._on_authorize)
        self.disconnect_button.clicked.connect(self._on_disconnect)
        self.scrobbling_checkbox.stateChanged.connect(self._on_scrobbling_toggled)

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
        self._service.scrobbling_enabled = bool(state)

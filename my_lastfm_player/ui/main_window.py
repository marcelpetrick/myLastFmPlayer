from __future__ import annotations

import logging

from PyQt6.QtCore import QEvent, QSortFilterProxyModel, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QMouseEvent
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSlider,
    QSpinBox,
    QTableView,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from my_lastfm_player import __display_version__
from my_lastfm_player.i18n import DEFAULT_LANGUAGE_CODE, SUPPORTED_LANGUAGES, TranslationManager
from my_lastfm_player.models import Track
from my_lastfm_player.ui.track_table_model import TrackTableModel, example_tracks

LOGGER = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Initial MVP shell for the Last.fm player desktop UI."""

    fetch_requested = pyqtSignal()
    fetch_pause_requested = pyqtSignal()
    fetch_stop_requested = pyqtSignal()
    download_requested = pyqtSignal()
    play_requested = pyqtSignal()
    pause_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    seek_requested = pyqtSignal(int)

    def __init__(self, translation_manager: TranslationManager | None = None) -> None:
        super().__init__()
        self.translation_manager = translation_manager
        self._fetch_paused = False
        self._last_progress_label = "Idle"
        self._last_status_message = "Ready"
        self._playback_duration_ms = 0
        self.set_application_title(__display_version__)
        self.resize(1120, 720)

        self._build_actions()
        self._build_menus()
        self._build_toolbar()
        self._build_central_widget()
        self.set_tracks(example_tracks())
        self.statusBar().showMessage(self.tr("Ready"))
        self.retranslate_ui()

    def set_application_title(self, version: str) -> None:
        """Set the window title using the current application ``version``."""

        self.setWindowTitle(application_title(version))

    def _build_actions(self) -> None:
        self.refresh_action = QAction(self)
        self.refresh_action.triggered.connect(self.fetch_requested.emit)

        self.quit_action = QAction(self)
        self.quit_action.triggered.connect(self.close)

        self.language_actions: dict[str, QAction] = {}
        for language in SUPPORTED_LANGUAGES:
            action = QAction(language.native_name, self)
            action.setCheckable(True)
            action.triggered.connect(
                lambda _checked=False, code=language.code: self.set_language(code)
            )
            self.language_actions[language.code] = action

    def _build_menus(self) -> None:
        self.language_menu = QMenu(self)
        for language in SUPPORTED_LANGUAGES:
            self.language_menu.addAction(self.language_actions[language.code])
        self.menuBar().addMenu(self.language_menu)

    def _build_toolbar(self) -> None:
        self.toolbar = QToolBar(self)
        self.toolbar.setMovable(False)
        self.toolbar.addAction(self.refresh_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.quit_action)
        self.addToolBar(self.toolbar)

    def _build_central_widget(self) -> None:
        root = QWidget(self)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        layout.addWidget(self._build_source_panel())
        layout.addWidget(self._build_table(), stretch=1)
        layout.addWidget(self._build_controls_panel())
        layout.addWidget(self._build_feedback_panel())

        self.setCentralWidget(root)

    def _build_source_panel(self) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QGridLayout(frame)
        layout.setColumnStretch(1, 1)

        self.username_label = QLabel()
        self.username_input = QLineEdit()
        self.username_input.returnPressed.connect(self.fetch_requested.emit)

        self.fetch_button = QPushButton()
        self.fetch_pause_button = QPushButton()
        self.fetch_stop_button = QPushButton()
        self.fetch_button.clicked.connect(self.fetch_requested.emit)
        self.fetch_pause_button.clicked.connect(self.fetch_pause_requested.emit)
        self.fetch_stop_button.clicked.connect(self.fetch_stop_requested.emit)
        self.set_fetch_control_state(active=False, paused=False)

        self.dependency_label = QLabel()
        self.dependency_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        layout.addWidget(self.username_label, 0, 0)
        layout.addWidget(self.username_input, 0, 1)
        layout.addWidget(self.fetch_button, 0, 2)
        layout.addWidget(self.fetch_pause_button, 0, 3)
        layout.addWidget(self.fetch_stop_button, 0, 4)
        layout.addWidget(self.dependency_label, 1, 0, 1, 5)

        return frame

    def _build_table(self) -> QTableView:
        self.track_model = TrackTableModel()
        self.track_sort_model = QSortFilterProxyModel(self)
        self.track_sort_model.setSourceModel(self.track_model)
        self.track_sort_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        self.track_table = QTableView()
        self.track_table.setModel(self.track_sort_model)
        self.track_table.setAlternatingRowColors(True)
        self.track_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.track_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.track_table.setSortingEnabled(True)
        self.track_table.doubleClicked.connect(lambda _index: self.play_requested.emit())
        self.track_table.verticalHeader().setVisible(False)
        header = self.track_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        return self.track_table

    def _build_controls_panel(self) -> QWidget:
        panel = QWidget()
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.playback_group = QGroupBox()
        playback_layout = QVBoxLayout(self.playback_group)
        playback_button_layout = QHBoxLayout()
        self.play_button = QPushButton()
        self.pause_button = QPushButton()
        self.stop_button = QPushButton()
        self.play_button.clicked.connect(self.play_requested.emit)
        self.pause_button.clicked.connect(self.pause_requested.emit)
        self.stop_button.clicked.connect(self.stop_requested.emit)
        for button in (self.play_button, self.pause_button, self.stop_button):
            playback_button_layout.addWidget(button)

        playback_timeline_layout = QHBoxLayout()
        self.playback_slider = QSlider(Qt.Orientation.Horizontal)
        self.playback_slider.setRange(0, 0)
        self.playback_slider.setEnabled(False)
        self.playback_slider.setMinimumWidth(280)
        self.playback_slider.installEventFilter(self)
        self.playback_slider.sliderReleased.connect(self._emit_timeline_seek)
        self.current_time_label = QLabel(format_playback_time(0))
        self.current_time_label.setMinimumWidth(48)
        self.current_time_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.time_separator_label = QLabel("/")
        self.total_time_label = QLabel(format_playback_time(0))
        self.total_time_label.setMinimumWidth(48)
        playback_timeline_layout.addWidget(self.playback_slider, stretch=1)
        playback_timeline_layout.addWidget(self.current_time_label)
        playback_timeline_layout.addWidget(self.time_separator_label)
        playback_timeline_layout.addWidget(self.total_time_label)
        playback_layout.addLayout(playback_button_layout)
        playback_layout.addLayout(playback_timeline_layout)

        self.downloads_group = QGroupBox()
        self.downloads_layout = QFormLayout(self.downloads_group)
        self.download_toggle_button = QPushButton()
        self.download_toggle_button.clicked.connect(self.download_requested.emit)
        self.concurrency_label = QLabel()
        self.concurrency_input = QSpinBox()
        self.concurrency_input.setRange(1, 8)
        self.concurrency_input.setValue(2)
        self.downloads_layout.addRow(self.concurrency_label, self.concurrency_input)
        self.downloads_layout.addRow(self.download_toggle_button)

        layout.addWidget(self.playback_group)
        layout.addWidget(self.downloads_group)
        layout.addStretch(1)

        return panel

    def _build_feedback_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat(self.tr("Idle"))

        self.feedback_log = QPlainTextEdit()
        self.feedback_log.setReadOnly(True)
        self.feedback_log.setMaximumBlockCount(500)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.feedback_log)

        return panel

    def set_tracks(self, tracks: list[Track]) -> None:
        """Replace the visible table contents with ``tracks``."""

        self.track_model.set_tracks(tracks)
        self.track_table.resizeRowsToContents()
        print(f"[myLastFmPlayer] Table now contains {len(tracks)} tracks", flush=True)
        self.show_status(self.tr("Loaded {count} tracks").format(count=len(tracks)))

    def username(self) -> str:
        """Return the trimmed Last.fm username currently entered by the user."""

        return self.username_input.text().strip()

    def set_fetch_enabled(self, enabled: bool) -> None:
        """Enable or disable username entry and fetch actions."""

        self.fetch_button.setEnabled(enabled)
        self.username_input.setEnabled(enabled)
        self.refresh_action.setEnabled(enabled)

    def set_fetch_control_state(self, active: bool, paused: bool = False) -> None:
        """Enable pause/stop fetch controls and show pause or resume state."""

        self.fetch_pause_button.setEnabled(active)
        self.fetch_stop_button.setEnabled(active)
        self._fetch_paused = paused
        self.fetch_pause_button.setText(self.tr("Resume") if paused else self.tr("Pause"))
        if paused:
            self.fetch_pause_button.setToolTip(self.tr("Resume the paused Last.fm fetch"))
        else:
            self.fetch_pause_button.setToolTip(self.tr("Pause the active Last.fm fetch"))
        self.fetch_stop_button.setToolTip(self.tr("Stop the active Last.fm fetch"))

    def set_workflow_enabled(self, enabled: bool) -> None:
        """Enable or disable controls that start long-running workflows."""

        self.set_fetch_enabled(enabled)
        self.download_toggle_button.setEnabled(enabled)
        self.concurrency_input.setEnabled(enabled)

    def set_dependency_status(self, is_ok: bool, message: str) -> None:
        """Display dependency check status in the source panel."""

        self.dependency_label.setText(message)
        property_value = "ok" if is_ok else "missing"
        self.dependency_label.setProperty("status", property_value)
        self.dependency_label.style().unpolish(self.dependency_label)
        self.dependency_label.style().polish(self.dependency_label)

    def selected_track(self) -> Track | None:
        """Return the selected track, or ``None`` when no row is selected."""

        selected_rows = self.track_table.selectionModel().selectedRows()
        if not selected_rows:
            return None

        source_index = self.track_sort_model.mapToSource(selected_rows[0])
        return self.track_model.track_at(source_index.row())

    def selected_track_row(self) -> int | None:
        """Return the source-model row for the current selection."""

        selected_rows = self.track_table.selectionModel().selectedRows()
        if not selected_rows:
            return None

        source_index = self.track_sort_model.mapToSource(selected_rows[0])
        return source_index.row()

    def update_track(self, row: int, track: Track) -> None:
        """Replace one visible row with ``track`` and update the status bar."""

        self.track_model.update_track(row, track)
        status = self.tr(track.status.value)
        self.show_status(
            self.tr("Updated {artist} - {title}: {status}").format(
                artist=track.artist,
                title=track.title,
                status=status,
            )
        )

    def tracks(self) -> list[Track]:
        """Return a copy of the tracks currently visible in the table."""

        return self.track_model.tracks()

    def set_progress(self, value: int, label: str) -> None:
        """Update the progress bar and status bar with bounded ``value``."""

        bounded_value = max(0, min(100, value))
        self.progress_bar.setValue(bounded_value)
        self.progress_bar.setFormat(label)
        self._last_progress_label = label
        self.show_status(label)

    def append_feedback(self, message: str) -> None:
        """Append ``message`` to the feedback log and status bar."""

        self.feedback_log.appendPlainText(message)
        self.show_status(message)

    def show_status(self, message: str) -> None:
        """Show ``message`` in the status bar and terminal log."""

        LOGGER.info("UI status: %s", message)
        print(f"[myLastFmPlayer] UI status: {message}", flush=True)
        self._last_status_message = message
        self.statusBar().showMessage(message)

    def set_playback_timeline(self, position_ms: int, duration_ms: int) -> None:
        """Update the playback timeline slider and readable time labels."""

        bounded_duration = max(0, duration_ms)
        bounded_position = max(0, min(max(0, position_ms), bounded_duration))
        self._playback_duration_ms = bounded_duration
        self.playback_slider.setEnabled(bounded_duration > 0)
        self.playback_slider.setMaximum(bounded_duration)
        self.playback_slider.blockSignals(True)
        self.playback_slider.setValue(bounded_position)
        self.playback_slider.blockSignals(False)
        self.current_time_label.setText(format_playback_time(bounded_position))
        self.total_time_label.setText(format_playback_time(bounded_duration))

    def reset_playback_timeline(self) -> None:
        """Reset the playback timeline to an idle state."""

        self.set_playback_timeline(0, 0)

    def _emit_timeline_seek(self) -> None:
        if self._playback_duration_ms <= 0:
            return
        self.seek_requested.emit(self.playback_slider.value())

    def eventFilter(self, watched: object, event: QEvent) -> bool:
        """Handle immediate seeking when the playback timeline groove is clicked."""

        if (
            watched is self.playback_slider
            and event.type() == QEvent.Type.MouseButtonPress
            and isinstance(event, QMouseEvent)
            and event.button() == Qt.MouseButton.LeftButton
            and self._playback_duration_ms > 0
        ):
            value = self._timeline_value_for_x_position(round(event.position().x()))
            self.set_playback_timeline(value, self._playback_duration_ms)
            self.seek_requested.emit(value)
            return True
        return super().eventFilter(watched, event)

    def _timeline_value_for_x_position(self, x_position: int) -> int:
        slider_width = max(1, self.playback_slider.width())
        bounded_position = max(0, min(x_position, slider_width))
        return round(self._playback_duration_ms * bounded_position / slider_width)

    def _show_not_implemented(self) -> None:
        message = self.tr("This control is part of the MVP shell and will be wired in later steps.")
        self.append_feedback(message)

    def set_language(self, code: str) -> None:
        """Switch the active UI language and update visible widgets immediately."""

        if self.translation_manager is not None:
            self.translation_manager.set_language(code)
        for language_code, action in self.language_actions.items():
            action.setChecked(language_code == code)
        self.retranslate_ui()

    def retranslate_ui(self) -> None:
        """Apply current translations to all static widgets."""

        self.refresh_action.setText(self.tr("Fetch loved tracks"))
        self.quit_action.setText(self.tr("Quit"))
        self.language_menu.setTitle(self.tr("Language"))
        self.toolbar.setWindowTitle(self.tr("Main"))
        self.username_label.setText(self.tr("Last.fm username"))
        self.username_input.setPlaceholderText(self.tr("Enter username"))
        self.fetch_button.setText(self.tr("Fetch"))
        self.playback_group.setTitle(self.tr("Playback"))
        self.play_button.setText(self.tr("Play"))
        self.pause_button.setText(self.tr("Pause"))
        self.stop_button.setText(self.tr("Stop"))
        self.playback_slider.setToolTip(self.tr("Playback position"))
        self.downloads_group.setTitle(self.tr("Downloads"))
        self.download_toggle_button.setText(self.tr("Download Queued"))
        self.concurrency_label.setText(self.tr("Concurrency"))
        self.feedback_log.setPlaceholderText(
            self.tr("Status updates and errors will appear here.")
        )
        if not self.dependency_label.text():
            self.dependency_label.setText(
                self.tr("Dependencies: yt-dlp and ffmpeg not checked yet")
            )
        if self._last_progress_label == "Idle":
            self.progress_bar.setFormat(self.tr("Idle"))
        self.set_fetch_control_state(
            active=self.fetch_pause_button.isEnabled(),
            paused=self._fetch_paused,
        )
        self.track_model.retranslate()
        if self._last_status_message == "Ready":
            self.statusBar().showMessage(self.tr("Ready"))
        self.language_actions[
            self.translation_manager.current_language
            if self.translation_manager is not None
            else DEFAULT_LANGUAGE_CODE
        ].setChecked(True)


def application_title(version: str) -> str:
    """Return the application title with ``version`` as a suffix."""

    return f"myLastFmPlayer v{version}"


def format_playback_time(milliseconds: int) -> str:
    """Format ``milliseconds`` as a compact human-readable playback time."""

    total_seconds = max(0, milliseconds) // 1000
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02}:{seconds:02}"
    return f"{minutes}:{seconds:02}"

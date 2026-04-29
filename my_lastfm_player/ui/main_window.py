from __future__ import annotations

import logging

from PyQt6.QtCore import QSortFilterProxyModel, Qt, pyqtSignal
from PyQt6.QtGui import QAction
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
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTableView,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from my_lastfm_player import __version__
from my_lastfm_player.models import Track
from my_lastfm_player.ui.track_table_model import TrackTableModel, example_tracks

LOGGER = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Initial MVP shell for the Last.fm player desktop UI."""

    fetch_requested = pyqtSignal()
    download_requested = pyqtSignal()
    play_requested = pyqtSignal()
    pause_requested = pyqtSignal()
    stop_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"myLastFmPlayer v{__version__}")
        self.resize(1120, 720)

        self._build_actions()
        self._build_toolbar()
        self._build_central_widget()
        self.set_tracks(example_tracks())
        self.statusBar().showMessage("Ready")

    def _build_actions(self) -> None:
        self.refresh_action = QAction("Fetch loved tracks", self)
        self.refresh_action.triggered.connect(self.fetch_requested.emit)

        self.quit_action = QAction("Quit", self)
        self.quit_action.triggered.connect(self.close)

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Main")
        toolbar.setMovable(False)
        toolbar.addAction(self.refresh_action)
        toolbar.addSeparator()
        toolbar.addAction(self.quit_action)
        self.addToolBar(toolbar)

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

        username_label = QLabel("Last.fm username")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.returnPressed.connect(self.fetch_requested.emit)

        self.fetch_button = QPushButton("Fetch")
        self.fetch_button.clicked.connect(self.fetch_requested.emit)

        self.dependency_label = QLabel("Dependencies: yt-dlp and ffmpeg not checked yet")
        self.dependency_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        layout.addWidget(username_label, 0, 0)
        layout.addWidget(self.username_input, 0, 1)
        layout.addWidget(self.fetch_button, 0, 2)
        layout.addWidget(self.dependency_label, 1, 0, 1, 3)

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

        playback_group = QGroupBox("Playback")
        playback_layout = QHBoxLayout(playback_group)
        self.play_button = QPushButton("Play")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")
        self.play_button.clicked.connect(self.play_requested.emit)
        self.pause_button.clicked.connect(self.pause_requested.emit)
        self.stop_button.clicked.connect(self.stop_requested.emit)
        for button in (self.play_button, self.pause_button, self.stop_button):
            playback_layout.addWidget(button)

        downloads_group = QGroupBox("Downloads")
        downloads_layout = QFormLayout(downloads_group)
        self.download_toggle_button = QPushButton("Download Queued")
        self.download_toggle_button.clicked.connect(self.download_requested.emit)
        self.concurrency_input = QSpinBox()
        self.concurrency_input.setRange(1, 8)
        self.concurrency_input.setValue(2)
        downloads_layout.addRow("Concurrency", self.concurrency_input)
        downloads_layout.addRow(self.download_toggle_button)

        layout.addWidget(playback_group)
        layout.addWidget(downloads_group)
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
        self.progress_bar.setFormat("Idle")

        self.feedback_log = QPlainTextEdit()
        self.feedback_log.setReadOnly(True)
        self.feedback_log.setMaximumBlockCount(500)
        self.feedback_log.setPlaceholderText("Status updates and errors will appear here.")

        layout.addWidget(self.progress_bar)
        layout.addWidget(self.feedback_log)

        return panel

    def set_tracks(self, tracks: list[Track]) -> None:
        self.track_model.set_tracks(tracks)
        self.track_table.resizeRowsToContents()
        print(f"[myLastFmPlayer] Table now contains {len(tracks)} tracks", flush=True)
        self.show_status(f"Loaded {len(tracks)} tracks")

    def username(self) -> str:
        return self.username_input.text().strip()

    def set_fetch_enabled(self, enabled: bool) -> None:
        self.fetch_button.setEnabled(enabled)
        self.username_input.setEnabled(enabled)
        self.refresh_action.setEnabled(enabled)

    def set_workflow_enabled(self, enabled: bool) -> None:
        self.set_fetch_enabled(enabled)
        self.download_toggle_button.setEnabled(enabled)
        self.concurrency_input.setEnabled(enabled)

    def set_dependency_status(self, is_ok: bool, message: str) -> None:
        self.dependency_label.setText(message)
        property_value = "ok" if is_ok else "missing"
        self.dependency_label.setProperty("status", property_value)
        self.dependency_label.style().unpolish(self.dependency_label)
        self.dependency_label.style().polish(self.dependency_label)

    def selected_track(self) -> Track | None:
        selected_rows = self.track_table.selectionModel().selectedRows()
        if not selected_rows:
            return None

        source_index = self.track_sort_model.mapToSource(selected_rows[0])
        return self.track_model.track_at(source_index.row())

    def selected_track_row(self) -> int | None:
        selected_rows = self.track_table.selectionModel().selectedRows()
        if not selected_rows:
            return None

        source_index = self.track_sort_model.mapToSource(selected_rows[0])
        return source_index.row()

    def update_track(self, row: int, track: Track) -> None:
        self.track_model.update_track(row, track)
        self.show_status(f"Updated {track.artist} - {track.title}: {track.status.value}")

    def tracks(self) -> list[Track]:
        return self.track_model.tracks()

    def set_progress(self, value: int, label: str) -> None:
        bounded_value = max(0, min(100, value))
        self.progress_bar.setValue(bounded_value)
        self.progress_bar.setFormat(label)
        self.show_status(label)

    def append_feedback(self, message: str) -> None:
        self.feedback_log.appendPlainText(message)
        self.show_status(message)

    def show_status(self, message: str) -> None:
        LOGGER.info("UI status: %s", message)
        print(f"[myLastFmPlayer] UI status: {message}", flush=True)
        self.statusBar().showMessage(message)

    def _show_not_implemented(self) -> None:
        message = "This control is part of the MVP shell and will be wired in later steps."
        self.append_feedback(message)

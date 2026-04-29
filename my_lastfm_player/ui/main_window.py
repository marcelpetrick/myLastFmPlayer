from __future__ import annotations

from PyQt6.QtCore import Qt
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
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    """Initial MVP shell for the Last.fm player desktop UI."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("myLastFmPlayer")
        self.resize(1120, 720)

        self._build_actions()
        self._build_toolbar()
        self._build_central_widget()
        self._seed_placeholder_rows()
        self.statusBar().showMessage("Ready")

    def _build_actions(self) -> None:
        self.refresh_action = QAction("Fetch loved tracks", self)
        self.refresh_action.triggered.connect(self._show_not_implemented)

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
        self.username_input.returnPressed.connect(self._show_not_implemented)

        self.fetch_button = QPushButton("Fetch")
        self.fetch_button.clicked.connect(self._show_not_implemented)

        self.dependency_label = QLabel("Dependencies: yt-dlp and ffmpeg not checked yet")
        self.dependency_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(username_label, 0, 0)
        layout.addWidget(self.username_input, 0, 1)
        layout.addWidget(self.fetch_button, 0, 2)
        layout.addWidget(self.dependency_label, 1, 0, 1, 3)

        return frame

    def _build_table(self) -> QTableWidget:
        self.track_table = QTableWidget(0, 3)
        self.track_table.setHorizontalHeaderLabels(["Artist", "Title", "Status"])
        self.track_table.setAlternatingRowColors(True)
        self.track_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.track_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.track_table.setSortingEnabled(True)
        self.track_table.verticalHeader().setVisible(False)
        self.track_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.track_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.track_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
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
        for button in (self.play_button, self.pause_button, self.stop_button):
            button.clicked.connect(self._show_not_implemented)
            playback_layout.addWidget(button)

        downloads_group = QGroupBox("Downloads")
        downloads_layout = QFormLayout(downloads_group)
        self.download_toggle_button = QPushButton("Pause Downloads")
        self.download_toggle_button.clicked.connect(self._show_not_implemented)
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

    def _seed_placeholder_rows(self) -> None:
        rows = [
            ("Example Artist", "Example Track", "Fetched"),
            ("Another Artist", "Waiting for implementation", "Queued"),
        ]
        self.track_table.setSortingEnabled(False)
        for artist, title, status in rows:
            row = self.track_table.rowCount()
            self.track_table.insertRow(row)
            self.track_table.setItem(row, 0, QTableWidgetItem(artist))
            self.track_table.setItem(row, 1, QTableWidgetItem(title))
            self.track_table.setItem(row, 2, QTableWidgetItem(status))
        self.track_table.setSortingEnabled(True)

    def _show_not_implemented(self) -> None:
        message = "This control is part of the MVP shell and will be wired in later steps."
        self.feedback_log.appendPlainText(message)
        self.statusBar().showMessage(message, 5000)

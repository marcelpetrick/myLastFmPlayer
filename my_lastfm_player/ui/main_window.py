from __future__ import annotations

import logging

from PyQt6.QtCore import QEvent, QPoint, QSortFilterProxyModel, Qt, QTime, pyqtSignal
from PyQt6.QtGui import QAction, QActionGroup, QMouseEvent
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
    QVBoxLayout,
    QWidget,
)

from my_lastfm_player import __display_version__
from my_lastfm_player.i18n import DEFAULT_LANGUAGE_CODE, SUPPORTED_LANGUAGES, TranslationManager
from my_lastfm_player.models import Track
from my_lastfm_player.ui.flags import flag_icon
from my_lastfm_player.ui.track_table_model import (
    ElidedTextDelegate,
    TrackTableModel,
    example_tracks,
)

LOGGER = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Initial MVP shell for the Last.fm player desktop UI."""

    fetch_requested = pyqtSignal()
    fetch_pause_requested = pyqtSignal()
    fetch_stop_requested = pyqtSignal()
    download_requested = pyqtSignal()
    download_stop_requested = pyqtSignal()
    retry_download_requested = pyqtSignal(str)
    play_requested = pyqtSignal()
    pause_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    seek_requested = pyqtSignal(int)
    language_changed = pyqtSignal()
    theme_requested = pyqtSignal(str)
    preferences_requested = pyqtSignal()
    file_cache_requested = pyqtSignal()

    def __init__(self, translation_manager: TranslationManager | None = None) -> None:
        super().__init__()
        self.translation_manager = translation_manager
        self._fetch_paused = False
        self._download_active = False
        self._last_progress_label = "Idle"
        self._last_status_message = "Ready"
        self._playback_duration_ms = 0
        self._track_count = 0
        self.set_application_title(__display_version__)
        self.resize(1120, 720)

        self._build_actions()
        self._build_menus()
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

        self.preferences_action = QAction(self)
        self.preferences_action.triggered.connect(self.preferences_requested.emit)

        self.file_cache_action = QAction(self)
        self.file_cache_action.triggered.connect(self.file_cache_requested.emit)

        self.quit_action = QAction(self)
        self.quit_action.triggered.connect(self.close)

        self.theme_light_action = QAction(self)
        self.theme_light_action.setCheckable(True)
        self.theme_light_action.setChecked(True)
        self.theme_dark_action = QAction(self)
        self.theme_dark_action.setCheckable(True)
        self.theme_lilac_action = QAction(self)
        self.theme_lilac_action.setCheckable(True)
        self.theme_mint_action = QAction(self)
        self.theme_mint_action.setCheckable(True)
        self.theme_light_action.setData("light")
        self.theme_dark_action.setData("dark")
        self.theme_lilac_action.setData("lilac")
        self.theme_mint_action.setData("mint")
        self._theme_group = QActionGroup(self)
        self._theme_group.setExclusive(True)
        self._theme_group.addAction(self.theme_light_action)
        self._theme_group.addAction(self.theme_dark_action)
        self._theme_group.addAction(self.theme_lilac_action)
        self._theme_group.addAction(self.theme_mint_action)
        self._theme_group.triggered.connect(self._on_theme_action_triggered)

        self.language_actions: dict[str, QAction] = {}
        for language in SUPPORTED_LANGUAGES:
            action = QAction(language.native_name, self)
            action.setIcon(flag_icon(language.code))
            action.setCheckable(True)
            action.triggered.connect(
                lambda _checked=False, code=language.code: self.set_language(code)
            )
            self.language_actions[language.code] = action

    def _build_menus(self) -> None:
        self.theme_menu = QMenu(self)
        self.theme_menu.addAction(self.theme_light_action)
        self.theme_menu.addAction(self.theme_dark_action)
        self.theme_menu.addAction(self.theme_lilac_action)
        self.theme_menu.addAction(self.theme_mint_action)

        self.main_menu = QMenu(self)
        self.main_menu.addMenu(self.theme_menu)
        self.main_menu.addAction(self.preferences_action)
        self.main_menu.addAction(self.file_cache_action)
        self.main_menu.addAction(self.quit_action)
        self.menuBar().addMenu(self.main_menu)

        self.language_menu = QMenu(self)
        for language in SUPPORTED_LANGUAGES:
            self.language_menu.addAction(self.language_actions[language.code])
        self.menuBar().addMenu(self.language_menu)

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

        self.track_count_label = QLabel()

        self.dependency_label = QLabel()
        self.dependency_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        layout.addWidget(self.username_label, 0, 0)
        layout.addWidget(self.username_input, 0, 1)
        layout.addWidget(self.fetch_button, 0, 2)
        layout.addWidget(self.fetch_pause_button, 0, 3)
        layout.addWidget(self.fetch_stop_button, 0, 4)
        layout.addWidget(self.track_count_label, 1, 0)
        layout.addWidget(self.dependency_label, 1, 1, 1, 4)

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
        self.track_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.track_table.customContextMenuRequested.connect(self._show_track_context_menu)
        self.track_table.verticalHeader().setVisible(False)
        self.track_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        elide_delegate = ElidedTextDelegate(self.track_table)
        self.track_table.setItemDelegateForColumn(0, elide_delegate)
        self.track_table.setItemDelegateForColumn(1, elide_delegate)
        header = self.track_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        return self.track_table

    def _show_track_context_menu(self, pos: QPoint) -> None:
        index = self.track_table.indexAt(pos)
        if not index.isValid():
            return
        source_index = self.track_sort_model.mapToSource(index)
        cache_key = self.track_model.data(source_index, Qt.ItemDataRole.UserRole)
        if not isinstance(cache_key, str):
            return
        menu = QMenu(self)
        retry_action = QAction(self.tr("Retry Download"), menu)
        menu.addAction(retry_action)
        if menu.exec(self.track_table.viewport().mapToGlobal(pos)) == retry_action:
            self.retry_download_requested.emit(cache_key)

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
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
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
        self.now_playing_label = QLabel()
        self.now_playing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        playback_layout.addWidget(self.now_playing_label)
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

        feedback_header_layout = QHBoxLayout()
        feedback_header_layout.setContentsMargins(0, 0, 0, 0)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat(self.tr("Idle"))

        self.clear_feedback_button = QPushButton()
        self.clear_feedback_button.clicked.connect(self.clear_feedback_log)

        self.feedback_log = QPlainTextEdit()
        self.feedback_log.setReadOnly(True)
        self.feedback_log.setMaximumBlockCount(500)

        feedback_header_layout.addWidget(self.progress_bar, stretch=1)
        feedback_header_layout.addWidget(self.clear_feedback_button)
        layout.addLayout(feedback_header_layout)
        layout.addWidget(self.feedback_log)

        return panel

    def set_tracks(self, tracks: list[Track]) -> None:
        """Replace the visible table contents with ``tracks``."""

        self.track_model.set_tracks(tracks)
        self._track_count = len(tracks)
        self._update_track_count_label()
        print(f"[myLastFmPlayer] Table now contains {len(tracks)} tracks", flush=True)
        self.show_status(self.tr("Loaded {count} tracks").format(count=len(tracks)))

    def _update_track_count_label(self) -> None:
        self.track_count_label.setText(
            self.tr("Playlist: {count} titles").format(count=self._track_count)
        )

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
        self.fetch_stop_button.setText(self.tr("Stop"))
        if paused:
            self.fetch_pause_button.setToolTip(self.tr("Resume the paused Last.fm fetch"))
        else:
            self.fetch_pause_button.setToolTip(self.tr("Pause the active Last.fm fetch"))
        self.fetch_stop_button.setToolTip(self.tr("Stop the active Last.fm fetch"))

    def set_download_active(self, active: bool) -> None:
        """Switch the download button between Start and Stop state."""

        if self._download_active == active:
            return
        self._download_active = active
        self.download_toggle_button.clicked.disconnect()
        if active:
            self.download_toggle_button.setText(self.tr("Stop Downloads"))
            self.download_toggle_button.clicked.connect(self.download_stop_requested.emit)
            self.download_toggle_button.setEnabled(True)
        else:
            self.download_toggle_button.setText(self.tr("Start Downloads"))
            self.download_toggle_button.clicked.connect(self.download_requested.emit)

    def set_workflow_enabled(self, enabled: bool) -> None:
        """Enable or disable controls that start long-running workflows."""

        self.set_fetch_enabled(enabled)
        if not self._download_active:
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

    def next_track_after(self, cache_key: str) -> tuple[int, Track] | None:
        """Return the next source row after ``cache_key`` in sort order, wrapping at end."""

        for proxy_row in range(self.track_sort_model.rowCount()):
            proxy_index = self.track_sort_model.index(proxy_row, 0)
            source_index = self.track_sort_model.mapToSource(proxy_index)
            track = self.track_model.track_at(source_index.row())
            if track.cache_key != cache_key:
                continue
            next_proxy_row = proxy_row + 1
            if next_proxy_row >= self.track_sort_model.rowCount():
                next_proxy_row = 0
            next_source_index = self.track_sort_model.mapToSource(
                self.track_sort_model.index(next_proxy_row, 0)
            )
            next_source_row = next_source_index.row()
            return next_source_row, self.track_model.track_at(next_source_row)
        return None

    def select_track_row(self, source_row: int) -> None:
        """Select ``source_row`` in the table while respecting the active sort order."""

        if not 0 <= source_row < self.track_model.rowCount():
            return
        source_index = self.track_model.index(source_row, 0)
        proxy_index = self.track_sort_model.mapFromSource(source_index)
        if not proxy_index.isValid():
            return
        self.track_table.selectRow(proxy_index.row())

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

    def set_playing_track(self, cache_key: str | None) -> None:
        """Highlight the row matching ``cache_key`` as the currently playing track."""

        self.track_model.set_playing_track(cache_key)

    def set_now_playing(self, track: Track | None) -> None:
        """Display ``track`` info above the playback controls, or clear it when ``None``."""

        if track is None:
            self.now_playing_label.setText(self.tr("Not playing"))
        else:
            self.now_playing_label.setText(f"{track.artist} — {track.title}")

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

        self.feedback_log.appendPlainText(format_feedback_message(message))
        self.show_status(message)

    def clear_feedback_log(self) -> None:
        """Clear the feedback log and reset its scroll bars."""

        self.feedback_log.clear()
        self.feedback_log.verticalScrollBar().setValue(
            self.feedback_log.verticalScrollBar().minimum()
        )
        self.feedback_log.horizontalScrollBar().setValue(
            self.feedback_log.horizontalScrollBar().minimum()
        )

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

    def set_playback_controls(self, *, active: bool) -> None:
        """Update playback button states.

        When ``active`` is ``True`` (playing or paused) Play is disabled and
        Pause/Stop are enabled.  When ``False`` (idle) only Play is enabled.
        """

        self.play_button.setEnabled(not active)
        self.pause_button.setEnabled(active)
        self.stop_button.setEnabled(active)

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

    def _on_theme_action_triggered(self, action: QAction) -> None:
        mode = action.data()
        if isinstance(mode, str):
            self.theme_requested.emit(mode)

    def set_theme_mode(self, mode: str) -> None:
        """Mark ``mode`` as selected in the theme menu without emitting a change request."""

        for action in self._theme_group.actions():
            action.setChecked(action.data() == mode)

    def set_language(self, code: str) -> None:
        """Switch the active UI language and update visible widgets immediately."""

        if self.translation_manager is not None:
            self.translation_manager.set_language(code)
        for language_code, action in self.language_actions.items():
            action.setChecked(language_code == code)
        self.retranslate_ui()
        self.language_changed.emit()

    def retranslate_ui(self) -> None:
        """Apply current translations to all static widgets."""

        self.refresh_action.setText(self.tr("Fetch loved tracks"))
        self.preferences_action.setText(self.tr("Preferences"))
        self.file_cache_action.setText(self.tr("Open data folder in file manager"))
        self.quit_action.setText(self.tr("Quit"))
        self.main_menu.setTitle(self.tr("Main"))
        self.theme_menu.setTitle(self.tr("Theme"))
        self.theme_light_action.setText(self.tr("Light"))
        self.theme_dark_action.setText(self.tr("Dark"))
        self.theme_lilac_action.setText(self.tr("Lilac"))
        self.theme_mint_action.setText(self.tr("Mint"))
        self.language_menu.setTitle(self.tr("Language"))
        self.username_label.setText(self.tr("Last.fm username"))
        self.username_input.setPlaceholderText(self.tr("Enter username"))
        self.fetch_button.setText(self.tr("Fetch"))
        self.playback_group.setTitle(self.tr("Playback"))
        if self.now_playing_label.text() in ("", "Not playing"):
            self.now_playing_label.setText(self.tr("Not playing"))
        self.play_button.setText(self.tr("Play"))
        self.pause_button.setText(self.tr("Pause"))
        self.stop_button.setText(self.tr("Stop"))
        self.playback_slider.setToolTip(self.tr("Playback position"))
        self.downloads_group.setTitle(self.tr("Downloads"))
        self.download_toggle_button.setText(
            self.tr("Stop Downloads") if self._download_active else self.tr("Start Downloads")
        )
        self.concurrency_label.setText(self.tr("Concurrency"))
        self.clear_feedback_button.setText(self.tr("Clear log"))
        self.clear_feedback_button.setToolTip(self.tr("Clear status updates and errors"))
        self.feedback_log.setPlaceholderText(
            self.tr("Status updates and errors will appear here.")
        )
        self._update_track_count_label()
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


def format_feedback_message(message: str, time: QTime | None = None) -> str:
    """Return ``message`` with a user-readable timestamp prefix."""

    timestamp = (time or QTime.currentTime()).toString("HH:mm:ss")
    return f"{timestamp}: {message}"


def format_playback_time(milliseconds: int) -> str:
    """Format ``milliseconds`` as a compact human-readable playback time."""

    total_seconds = max(0, milliseconds) // 1000
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02}:{seconds:02}"
    return f"{minutes}:{seconds:02}"

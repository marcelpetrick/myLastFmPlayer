from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QAbstractTableModel, QCoreApplication, QModelIndex, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QStyle, QStyledItemDelegate, QStyleOptionViewItem

from my_lastfm_player.models import Track, TrackStatus


class ElidedTextDelegate(QStyledItemDelegate):
    """Item delegate that elides overflowing text with '…' instead of wrapping."""

    def paint(self, painter, option: QStyleOptionViewItem, index) -> None:  # type: ignore[override]
        self.initStyleOption(option, index)
        text = option.text
        option.text = ""
        style = option.widget.style() if option.widget else QApplication.style()
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem, option, painter, option.widget)
        text_rect = style.subElementRect(
            QStyle.SubElement.SE_ItemViewItemText, option, option.widget
        )
        elided = option.fontMetrics.elidedText(
            text, Qt.TextElideMode.ElideRight, text_rect.width()
        )

        painter.save()
        painter.setFont(option.font)
        if option.state & QStyle.StateFlag.State_Selected:
            painter.setPen(option.palette.highlightedText().color())
        else:
            painter.setPen(option.palette.text().color())
        painter.drawText(
            text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, elided
        )
        painter.restore()


class TrackTableModel(QAbstractTableModel):
    """Qt table model exposing track metadata and download state columns."""

    HEADERS = ("Artist", "Title", "Loved at", "Status", "File")

    def __init__(self, tracks: list[Track] | None = None) -> None:
        super().__init__()
        self._tracks = tracks or []
        self._playing_cache_key: str | None = None

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        """Return the number of top-level track rows."""

        if parent is not None and parent.isValid():
            return 0
        return len(self._tracks)

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        """Return the number of columns shown for each track."""

        if parent is not None and parent.isValid():
            return 0
        return len(self.HEADERS)

    def data(
        self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole
    ) -> str | QFont | None:
        """Return display, user-role, or font data for ``index``."""

        if not index.isValid() or not 0 <= index.row() < len(self._tracks):
            return None

        track = self._tracks[index.row()]
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return self._display_value(track, index.column())
        if role == Qt.ItemDataRole.UserRole:
            return track.cache_key
        if role == Qt.ItemDataRole.FontRole and self._is_playing_row(track):
            font = QFont()
            font.setBold(True)
            return font
        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> str | None:
        """Return horizontal header labels for display roles."""

        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            match section:
                case 0:
                    return self.tr("Artist")
                case 1:
                    return self.tr("Title")
                case 2:
                    return self.tr("Loved at")
                case 3:
                    return self.tr("Status")
                case 4:
                    return self.tr("File")
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """Return item flags for selectable, read-only rows."""

        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def set_tracks(self, tracks: list[Track]) -> None:
        """Replace the model contents with ``tracks``."""

        self.beginResetModel()
        self._tracks = list(tracks)
        self.endResetModel()

    def update_track(self, row: int, track: Track) -> None:
        """Replace one row and emit a data-changed signal for all columns."""

        if not 0 <= row < len(self._tracks):
            raise IndexError(f"Track row out of range: {row}")
        self._tracks[row] = track
        top_left = self.index(row, 0)
        bottom_right = self.index(row, self.columnCount() - 1)
        self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.DisplayRole])

    def track_at(self, row: int) -> Track:
        """Return the track at ``row``."""

        return self._tracks[row]

    def tracks(self) -> list[Track]:
        """Return a copy of the model's tracks."""

        return list(self._tracks)

    def set_playing_track(self, cache_key: str | None) -> None:
        """Mark ``cache_key`` as the currently playing track and refresh fonts."""

        if cache_key == self._playing_cache_key:
            return
        previous_key = self._playing_cache_key
        self._playing_cache_key = cache_key
        for row, track in enumerate(self._tracks):
            if track.cache_key in (previous_key, cache_key):
                top_left = self.index(row, 0)
                bottom_right = self.index(row, self.columnCount() - 1)
                self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.FontRole])

    def playing_cache_key(self) -> str | None:
        """Return the cache key of the currently playing track, if any."""

        return self._playing_cache_key

    def _is_playing_row(self, track: Track) -> bool:
        return self._playing_cache_key is not None and track.cache_key == self._playing_cache_key

    def _display_value(self, track: Track, column: int) -> str | None:
        match column:
            case 0:
                return track.artist
            case 1:
                return track.title
            case 2:
                return track.loved_at or ""
            case 3:
                match track.status:
                    case TrackStatus.FETCHED:
                        return self.tr("Fetched")
                    case TrackStatus.QUEUED:
                        return self.tr("Queued")
                    case TrackStatus.SEARCHING:
                        return self.tr("Searching")
                    case TrackStatus.DOWNLOADING:
                        return self.tr("Downloading")
                    case TrackStatus.DOWNLOADED:
                        return self.tr("Downloaded")
                    case TrackStatus.FAILED:
                        return self.tr("Failed")
                    case TrackStatus.NOT_FOUND:
                        return self.tr("Not found")
                    case _:
                        return track.status.value
            case 4:
                return _download_file_details(track)
            case _:
                return None

    def retranslate(self) -> None:
        """Notify views that translated headers and status labels changed."""

        if self.columnCount() > 0:
            self.headerDataChanged.emit(
                Qt.Orientation.Horizontal,
                0,
                self.columnCount() - 1,
            )
        if self.rowCount() > 0:
            top_left = self.index(0, 0)
            bottom_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
            self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.DisplayRole])


def example_tracks() -> list[Track]:
    """Return placeholder tracks used before real data is loaded."""

    return [
        Track(
            artist=QCoreApplication.translate("TrackTableModel", "Example Artist"),
            title=QCoreApplication.translate("TrackTableModel", "Example Track"),
            status=TrackStatus.FETCHED,
        ),
        Track(
            artist=QCoreApplication.translate("TrackTableModel", "Another Artist"),
            title=QCoreApplication.translate("TrackTableModel", "Waiting for implementation"),
            status=TrackStatus.QUEUED,
        ),
    ]


def _download_file_details(track: Track) -> str:
    if track.status is not TrackStatus.DOWNLOADED or not track.local_path:
        return ""

    details = []
    file_type = track.file_type or Path(track.local_path).suffix.lstrip(".")
    if file_type:
        details.append(file_type.upper())
    if track.bitrate_kbps is not None:
        details.append(
            QCoreApplication.translate(
                "TrackTableModel",
                "{bitrate} kbps",
            ).format(bitrate=track.bitrate_kbps)
        )
    return ", ".join(details)

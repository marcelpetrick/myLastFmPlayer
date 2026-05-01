from __future__ import annotations

from PyQt6.QtCore import QAbstractTableModel, QCoreApplication, QModelIndex, Qt

from my_lastfm_player.models import Track, TrackStatus


class TrackTableModel(QAbstractTableModel):
    """Qt table model exposing track artist, title, and status columns."""

    HEADERS = ("Artist", "Title", "Status")

    def __init__(self, tracks: list[Track] | None = None) -> None:
        super().__init__()
        self._tracks = tracks or []

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

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> str | None:
        """Return display or user-role data for ``index``."""

        if not index.isValid() or not 0 <= index.row() < len(self._tracks):
            return None

        track = self._tracks[index.row()]
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return self._display_value(track, index.column())
        if role == Qt.ItemDataRole.UserRole:
            return track.cache_key
        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> str | None:
        """Return horizontal header labels for display roles."""

        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.tr(self.HEADERS[section])
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

    def _display_value(self, track: Track, column: int) -> str | None:
        match column:
            case 0:
                return track.artist
            case 1:
                return track.title
            case 2:
                return self.tr(track.status.value)
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

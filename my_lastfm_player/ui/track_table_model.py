from __future__ import annotations

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt

from my_lastfm_player.models import Track, TrackStatus


class TrackTableModel(QAbstractTableModel):
    HEADERS = ("Artist", "Title", "Status")

    def __init__(self, tracks: list[Track] | None = None) -> None:
        super().__init__()
        self._tracks = tracks or []

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        if parent is not None and parent.isValid():
            return 0
        return len(self._tracks)

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        if parent is not None and parent.isValid():
            return 0
        return len(self.HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> str | None:
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
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.HEADERS[section]
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def set_tracks(self, tracks: list[Track]) -> None:
        self.beginResetModel()
        self._tracks = list(tracks)
        self.endResetModel()

    def update_track(self, row: int, track: Track) -> None:
        if not 0 <= row < len(self._tracks):
            raise IndexError(f"Track row out of range: {row}")
        self._tracks[row] = track
        top_left = self.index(row, 0)
        bottom_right = self.index(row, self.columnCount() - 1)
        self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.DisplayRole])

    def track_at(self, row: int) -> Track:
        return self._tracks[row]

    def tracks(self) -> list[Track]:
        return list(self._tracks)

    def _display_value(self, track: Track, column: int) -> str | None:
        match column:
            case 0:
                return track.artist
            case 1:
                return track.title
            case 2:
                return track.status.value
            case _:
                return None


def example_tracks() -> list[Track]:
    return [
        Track(artist="Example Artist", title="Example Track", status=TrackStatus.FETCHED),
        Track(
            artist="Another Artist",
            title="Waiting for implementation",
            status=TrackStatus.QUEUED,
        ),
    ]

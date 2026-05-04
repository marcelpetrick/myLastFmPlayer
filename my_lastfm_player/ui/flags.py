from __future__ import annotations

import math

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap, QPolygonF

_W = 24
_H = 16


def _new_pixmap() -> QPixmap:
    pm = QPixmap(_W, _H)
    pm.fill(Qt.GlobalColor.transparent)
    return pm


def _hstripes(colors: list[str]) -> QPixmap:
    pm = _new_pixmap()
    p = QPainter(pm)
    n = len(colors)
    for i, color in enumerate(colors):
        y = round(i * _H / n)
        h = round((i + 1) * _H / n) - y
        p.fillRect(0, y, _W, h, QColor(color))
    p.end()
    return pm


def _star_polygon(cx: float, cy: float, r_out: float, r_in: float) -> QPolygonF:
    pts = []
    for i in range(10):
        angle = math.radians(i * 36 - 90)
        r = r_out if i % 2 == 0 else r_in
        pts.append(QPointF(cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return QPolygonF(pts)


def _en() -> QPixmap:
    pm = _new_pixmap()
    p = QPainter(pm)
    p.fillRect(0, 0, _W, _H, QColor("#012169"))
    # White diagonals
    p.setPen(QPen(QColor("#FFFFFF"), max(2, _H // 5)))
    p.drawLine(0, 0, _W - 1, _H - 1)
    p.drawLine(_W - 1, 0, 0, _H - 1)
    # White cross arms
    cross_w = max(2, _H // 3)
    p.fillRect((_W - cross_w) // 2, 0, cross_w, _H, QColor("#FFFFFF"))
    p.fillRect(0, (_H - cross_w) // 2, _W, cross_w, QColor("#FFFFFF"))
    # Red cross arms (narrower)
    red_w = max(1, _H // 5)
    p.fillRect((_W - red_w) // 2, 0, red_w, _H, QColor("#C8102E"))
    p.fillRect(0, (_H - red_w) // 2, _W, red_w, QColor("#C8102E"))
    p.end()
    return pm


def _de() -> QPixmap:
    return _hstripes(["#000000", "#DD0000", "#FFCE00"])


def _hr() -> QPixmap:
    return _hstripes(["#FF0000", "#FFFFFF", "#0035A9"])


def _uk() -> QPixmap:
    return _hstripes(["#005BBB", "#FFD500"])


def _zh() -> QPixmap:
    pm = _new_pixmap()
    p = QPainter(pm)
    p.fillRect(0, 0, _W, _H, QColor("#DE2910"))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#FFDE00"))
    p.drawPolygon(_star_polygon(cx=5.5, cy=8.0, r_out=4.0, r_in=1.7))
    p.end()
    return pm


_BUILDERS = {
    "en": _en,
    "de": _de,
    "hr": _hr,
    "uk": _uk,
    "zh": _zh,
}


def flag_icon(code: str) -> QIcon:
    """Return a small rendered flag QIcon for the given language ``code``."""
    builder = _BUILDERS.get(code)
    if builder is None:
        return QIcon()
    return QIcon(builder())

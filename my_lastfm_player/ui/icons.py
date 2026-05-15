from __future__ import annotations

import math

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap

_ICON_SIZE = 24


def preferences_icon() -> QIcon:
    """Return a grey cogwheel icon for the preferences action."""

    pm = _new_pixmap()
    p = _painter(pm)
    center = QPointF(12, 12)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#73777F"))
    for index in range(8):
        angle = math.radians(index * 45)
        p.save()
        p.translate(center)
        p.rotate(math.degrees(angle))
        p.drawRoundedRect(QRectF(5.5, -1.8, 4.6, 3.6), 1.0, 1.0)
        p.restore()
    p.setBrush(QColor("#8F949C"))
    p.drawEllipse(center, 7.2, 7.2)
    p.setBrush(QColor("#F5F5F5"))
    p.drawEllipse(center, 3.1, 3.1)
    p.end()
    return QIcon(pm)


def folder_icon() -> QIcon:
    """Return a light beige folder icon for opening the local data folder."""

    pm = _new_pixmap()
    p = _painter(pm)
    p.setPen(QPen(QColor("#B89D65"), 1.1))
    p.setBrush(QColor("#E8D6A8"))
    p.drawRoundedRect(QRectF(3.0, 7.0, 18.0, 11.0), 2.0, 2.0)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#F2E3BA"))
    p.drawRoundedRect(QRectF(4.0, 5.0, 8.0, 4.5), 1.6, 1.6)
    p.setBrush(QColor("#F7EAC5"))
    p.drawRoundedRect(QRectF(4.0, 9.0, 16.0, 8.0), 1.6, 1.6)
    p.end()
    return QIcon(pm)


def quit_icon() -> QIcon:
    """Return a red power icon for the quit action."""

    pm = _new_pixmap()
    p = _painter(pm)
    p.setPen(QPen(QColor("#C84A4A"), 2.4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    p.drawLine(QPointF(12, 4.8), QPointF(12, 11.6))
    p.drawArc(QRectF(5.4, 7.0, 13.2, 13.2), 35 * 16, 290 * 16)
    p.end()
    return QIcon(pm)


def palette_icon() -> QIcon:
    """Return a color palette icon for theme selection."""

    pm = _new_pixmap()
    p = _painter(pm)
    palette = QPainterPath()
    palette.addEllipse(QRectF(3.2, 4.0, 17.5, 15.5))
    palette.addEllipse(QRectF(13.8, 13.2, 5.0, 4.5))
    p.setPen(QPen(QColor("#676C73"), 1.0))
    p.setBrush(QColor("#F4F0E8"))
    p.drawPath(palette.simplified())
    p.setPen(Qt.PenStyle.NoPen)
    for color, x, y in (
        ("#E85D75", 8.0, 8.5),
        ("#F7C948", 12.0, 7.4),
        ("#4FA3D1", 15.0, 10.5),
        ("#5FBF8F", 10.5, 12.3),
    ):
        p.setBrush(QColor(color))
        p.drawEllipse(QPointF(x, y), 1.7, 1.7)
    p.end()
    return QIcon(pm)


def theme_swatch_icon(fill: str, border: str = "#6F747B") -> QIcon:
    """Return a compact color swatch icon for a specific theme action."""

    pm = _new_pixmap()
    p = _painter(pm)
    p.setPen(QPen(QColor(border), 1.1))
    p.setBrush(QColor(fill))
    p.drawRoundedRect(QRectF(5.0, 6.0, 14.0, 12.0), 2.4, 2.4)
    p.end()
    return QIcon(pm)


def _new_pixmap() -> QPixmap:
    pm = QPixmap(_ICON_SIZE, _ICON_SIZE)
    pm.fill(Qt.GlobalColor.transparent)
    return pm


def _painter(pm: QPixmap) -> QPainter:
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    return p

"""Exact checks for drawing details that the tolerant golden-image test cannot see.

The golden comparison allows a few levels per channel, so a slightly different corner
radius or a one-degree rotated star slips through. These tests compare against a
reference painted in the same process (same raster engine, so exact equality is
stable) or against the geometry itself.
"""

from __future__ import annotations

import math

import pytest
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QImage, QPainter, QPen, QPixmap

from my_lastfm_player.ui.flags import _star_polygon
from my_lastfm_player.ui.icons import _ICON_SIZE, folder_icon


def _image(pm: QPixmap) -> QImage:
    return pm.toImage().convertToFormat(QImage.Format.Format_ARGB32)


def _reference_folder() -> QImage:
    pm = QPixmap(_ICON_SIZE, _ICON_SIZE)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p.setPen(QPen(QColor("#B89D65"), 1.1))
    p.setBrush(QColor("#E8D6A8"))
    p.drawRoundedRect(QRectF(3.0, 7.0, 18.0, 11.0), 2.0, 2.0)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#F2E3BA"))
    p.drawRoundedRect(QRectF(4.0, 5.0, 8.0, 4.5), 1.6, 1.6)
    p.setBrush(QColor("#F7EAC5"))
    p.drawRoundedRect(QRectF(4.0, 9.0, 16.0, 8.0), 1.6, 1.6)
    p.end()
    return _image(pm)


@pytest.mark.usefixtures("qapp")
def test_folder_icon_matches_reference_painting_exactly() -> None:
    actual = _image(folder_icon().pixmap(_ICON_SIZE, _ICON_SIZE))
    expected = _reference_folder()
    differing = [
        (x, y)
        for y in range(_ICON_SIZE)
        for x in range(_ICON_SIZE)
        if actual.pixel(x, y) != expected.pixel(x, y)
    ]
    assert differing == []


def test_star_polygon_points_start_at_top_and_run_clockwise() -> None:
    polygon = _star_polygon(cx=5.5, cy=8.0, r_out=4.0, r_in=1.7)
    points = [(polygon[i].x(), polygon[i].y()) for i in range(polygon.size())]
    expected = []
    for i in range(10):
        angle = math.radians(i * 36 - 90)
        r = 4.0 if i % 2 == 0 else 1.7
        expected.append((5.5 + r * math.cos(angle), 8.0 + r * math.sin(angle)))
    assert len(points) == 10
    for (x, y), (ex, ey) in zip(points, expected, strict=True):
        assert x == pytest.approx(ex, abs=1e-9)
        assert y == pytest.approx(ey, abs=1e-9)
    # Top tip, then the first inner point to its right.
    assert points[0] == pytest.approx((5.5, 4.0))
    assert points[1][0] > 5.5
    assert isinstance(polygon[0], QPointF)

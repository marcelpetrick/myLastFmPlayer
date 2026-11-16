"""Pixel-compare the hand-drawn icons and flags against reviewed golden images.

The icons are painted in code, so a changed coordinate, angle or colour silently
changes what the user sees. Each image is compared with a small per-channel
tolerance: the raster engine's SIMD paths may differ by a level or two between
CPUs, while any real drawing change moves edge pixels by far more.

After an intentional drawing change, regenerate and review the PNGs with::

    MY_LASTFM_PLAYER_UPDATE_GOLDEN=1 python -m pytest tests/test_golden_images.py
"""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path

import pytest
from PyQt6.QtGui import QIcon, QImage

from my_lastfm_player.ui.flags import _H, _W, flag_icon
from my_lastfm_player.ui.icons import (
    _ICON_SIZE,
    folder_icon,
    palette_icon,
    preferences_icon,
    quit_icon,
    theme_swatch_icon,
)

GOLDEN_DIR = Path(__file__).resolve().parent / "fixtures" / "golden"
CHANNEL_TOLERANCE = 3
UPDATE_GOLDEN = os.environ.get("MY_LASTFM_PLAYER_UPDATE_GOLDEN") == "1"

ICONS: dict[str, tuple[Callable[[], QIcon], int, int]] = {
    "icon_preferences": (preferences_icon, _ICON_SIZE, _ICON_SIZE),
    "icon_folder": (folder_icon, _ICON_SIZE, _ICON_SIZE),
    "icon_quit": (quit_icon, _ICON_SIZE, _ICON_SIZE),
    "icon_palette": (palette_icon, _ICON_SIZE, _ICON_SIZE),
    "icon_swatch_default_border": (lambda: theme_swatch_icon("#F3EEE3"), _ICON_SIZE, _ICON_SIZE),
    "icon_swatch_custom_border": (
        lambda: theme_swatch_icon("#1E2328", "#C8A2C8"),
        _ICON_SIZE,
        _ICON_SIZE,
    ),
    **{
        f"flag_{code}": (lambda code=code: flag_icon(code), _W, _H)
        for code in ("en", "de", "hr", "uk", "zh")
    },
}


def render(icon: QIcon, width: int, height: int) -> QImage:
    return icon.pixmap(width, height).toImage().convertToFormat(QImage.Format.Format_ARGB32)


def max_channel_difference(actual: QImage, expected: QImage) -> tuple[int, int, int]:
    """Return the largest per-channel difference and the pixel where it occurs."""

    worst = (0, 0, 0)
    for y in range(actual.height()):
        for x in range(actual.width()):
            a = actual.pixel(x, y)
            e = expected.pixel(x, y)
            diff = max(
                abs(((a >> shift) & 0xFF) - ((e >> shift) & 0xFF)) for shift in (0, 8, 16, 24)
            )
            if diff > worst[0]:
                worst = (diff, x, y)
    return worst


@pytest.mark.usefixtures("qapp")
@pytest.mark.parametrize("name", sorted(ICONS))
def test_drawn_image_matches_golden(name: str) -> None:
    factory, width, height = ICONS[name]
    actual = render(factory(), width, height)
    golden_path = GOLDEN_DIR / f"{name}.png"

    if UPDATE_GOLDEN:
        GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
        assert actual.save(str(golden_path), "PNG")
        pytest.skip(f"updated {golden_path.name}")

    expected = QImage(str(golden_path)).convertToFormat(QImage.Format.Format_ARGB32)
    assert not expected.isNull(), f"missing golden image {golden_path}"
    assert (actual.width(), actual.height()) == (expected.width(), expected.height())
    diff, x, y = max_channel_difference(actual, expected)
    assert diff <= CHANNEL_TOLERANCE, f"{name} differs by {diff} at pixel ({x}, {y})"


def test_max_channel_difference_reports_worst_pixel(qapp) -> None:
    base = QImage(3, 2, QImage.Format.Format_ARGB32)
    base.fill(0xFF102030)
    changed = base.copy()
    changed.setPixel(2, 1, 0xFF102A30)

    assert max_channel_difference(base, base) == (0, 0, 0)
    assert max_channel_difference(changed, base) == (10, 2, 1)

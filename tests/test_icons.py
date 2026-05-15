from __future__ import annotations

import pytest
from PyQt6.QtGui import QColor

from my_lastfm_player.ui.icons import (
    _ICON_SIZE,
    folder_icon,
    palette_icon,
    preferences_icon,
    quit_icon,
    theme_swatch_icon,
)


@pytest.mark.usefixtures("qapp")
class TestMenuIcons:
    @pytest.mark.parametrize(
        "icon_factory",
        [preferences_icon, folder_icon, quit_icon, palette_icon, theme_swatch_icon],
    )
    def test_icons_are_non_empty(self, icon_factory) -> None:
        icon = icon_factory("#F3EEE3") if icon_factory is theme_swatch_icon else icon_factory()

        assert not icon.isNull()

    @pytest.mark.parametrize(
        "icon_factory",
        [preferences_icon, folder_icon, quit_icon, palette_icon, theme_swatch_icon],
    )
    def test_icon_pixmap_dimensions(self, icon_factory) -> None:
        icon = icon_factory("#F3EEE3") if icon_factory is theme_swatch_icon else icon_factory()
        pm = icon.pixmap(_ICON_SIZE, _ICON_SIZE)

        assert pm.width() == _ICON_SIZE
        assert pm.height() == _ICON_SIZE

    def test_preferences_icon_contains_grey_pixels(self) -> None:
        image = preferences_icon().pixmap(_ICON_SIZE, _ICON_SIZE).toImage()

        assert _contains_color_near(image, QColor("#8F949C"))

    def test_folder_icon_contains_light_beige_pixels(self) -> None:
        image = folder_icon().pixmap(_ICON_SIZE, _ICON_SIZE).toImage()

        assert _contains_color_near(image, QColor("#F7EAC5"))

    def test_quit_icon_contains_red_pixels(self) -> None:
        image = quit_icon().pixmap(_ICON_SIZE, _ICON_SIZE).toImage()

        assert _contains_color_near(image, QColor("#C84A4A"))


def _contains_color_near(image, expected: QColor, tolerance: int = 12) -> bool:
    for y in range(image.height()):
        for x in range(image.width()):
            color = image.pixelColor(x, y)
            if color.alpha() and all(
                abs(actual - target) <= tolerance
                for actual, target in (
                    (color.red(), expected.red()),
                    (color.green(), expected.green()),
                    (color.blue(), expected.blue()),
                )
            ):
                return True
    return False

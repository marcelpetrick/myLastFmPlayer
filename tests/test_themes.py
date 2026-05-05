from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette

from my_lastfm_player.themes import ThemeMode, apply_theme


def test_apply_light_theme_sets_fusion_style(qapp) -> None:
    apply_theme(qapp, ThemeMode.LIGHT)

    assert qapp.style().objectName().lower() == "fusion"


def test_apply_dark_theme_sets_fusion_style(qapp) -> None:
    apply_theme(qapp, ThemeMode.DARK)

    assert qapp.style().objectName().lower() == "fusion"


def test_apply_dark_theme_uses_dark_window_color(qapp) -> None:
    apply_theme(qapp, ThemeMode.DARK)

    palette = qapp.palette()
    assert palette.color(QPalette.ColorRole.Window) == QColor(53, 53, 53)


def test_apply_dark_theme_uses_white_text(qapp) -> None:
    apply_theme(qapp, ThemeMode.DARK)

    palette = qapp.palette()
    assert palette.color(QPalette.ColorRole.WindowText) == QColor(Qt.GlobalColor.white)


def test_apply_dark_theme_uses_blue_accent(qapp) -> None:
    apply_theme(qapp, ThemeMode.DARK)

    palette = qapp.palette()
    assert palette.color(QPalette.ColorRole.Highlight) == QColor(42, 130, 218)


def test_apply_light_theme_after_dark_restores_light_palette(qapp) -> None:
    apply_theme(qapp, ThemeMode.DARK)
    apply_theme(qapp, ThemeMode.LIGHT)

    palette = qapp.palette()
    assert palette.color(QPalette.ColorRole.Window) != QColor(53, 53, 53)


def test_theme_mode_enum_values() -> None:
    assert ThemeMode.LIGHT.value == "light"
    assert ThemeMode.DARK.value == "dark"
    assert ThemeMode("light") is ThemeMode.LIGHT
    assert ThemeMode("dark") is ThemeMode.DARK

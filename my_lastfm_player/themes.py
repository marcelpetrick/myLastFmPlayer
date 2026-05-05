"""Application color theme support using Qt Fusion style and custom palettes."""

from __future__ import annotations

from enum import Enum

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication, QStyleFactory


class ThemeMode(Enum):
    """Available application color themes."""

    LIGHT = "light"
    DARK = "dark"


def apply_theme(app: QApplication, mode: ThemeMode) -> None:
    """Switch ``app`` to ``mode`` using the Fusion style.

    Both themes use the Fusion style for cross-platform consistency.
    Light mode uses the style's standard palette; dark mode uses a custom
    palette with neutral dark grays and a blue accent.
    """

    style = QStyleFactory.create("Fusion")
    if style is None:
        return
    app.setStyle(style)
    app.setPalette(_dark_palette() if mode is ThemeMode.DARK else style.standardPalette())


def _dark_palette() -> QPalette:
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    disabled = QPalette.ColorGroup.Disabled
    palette.setColor(disabled, QPalette.ColorRole.WindowText, QColor(127, 127, 127))
    palette.setColor(disabled, QPalette.ColorRole.Text, QColor(127, 127, 127))
    palette.setColor(disabled, QPalette.ColorRole.ButtonText, QColor(127, 127, 127))
    palette.setColor(disabled, QPalette.ColorRole.Highlight, QColor(80, 80, 80))
    palette.setColor(disabled, QPalette.ColorRole.HighlightedText, QColor(127, 127, 127))
    return palette

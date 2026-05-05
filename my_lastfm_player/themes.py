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
    LILAC = "lilac"
    MINT = "mint"


def apply_theme(app: QApplication, mode: ThemeMode) -> None:
    """Switch ``app`` to ``mode`` using the Fusion style.

    All themes use the Fusion style for cross-platform consistency. Light mode
    uses the style's standard palette; named color themes use custom palettes.
    """

    style = QStyleFactory.create("Fusion")
    if style is None:
        return
    app.setStyle(style)
    match mode:
        case ThemeMode.DARK:
            palette = _dark_palette()
        case ThemeMode.LILAC:
            palette = _tinted_palette(
                window=QColor(248, 244, 255),
                base=QColor(255, 252, 255),
                alternate_base=QColor(238, 229, 250),
                button=QColor(231, 218, 246),
                text=QColor(49, 37, 66),
                accent=QColor(151, 104, 196),
            )
        case ThemeMode.MINT:
            palette = _tinted_palette(
                window=QColor(239, 251, 246),
                base=QColor(252, 255, 253),
                alternate_base=QColor(221, 244, 235),
                button=QColor(207, 236, 225),
                text=QColor(28, 60, 50),
                accent=QColor(42, 157, 116),
            )
        case ThemeMode.LIGHT:
            palette = style.standardPalette()
    app.setPalette(palette)


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


def _tinted_palette(
    *,
    window: QColor,
    base: QColor,
    alternate_base: QColor,
    button: QColor,
    text: QColor,
    accent: QColor,
) -> QPalette:
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, window)
    palette.setColor(QPalette.ColorRole.WindowText, text)
    palette.setColor(QPalette.ColorRole.Base, base)
    palette.setColor(QPalette.ColorRole.AlternateBase, alternate_base)
    palette.setColor(QPalette.ColorRole.ToolTipBase, text)
    palette.setColor(QPalette.ColorRole.ToolTipText, base)
    palette.setColor(QPalette.ColorRole.Text, text)
    palette.setColor(QPalette.ColorRole.BrightText, QColor(170, 0, 0))
    palette.setColor(QPalette.ColorRole.Button, button)
    palette.setColor(QPalette.ColorRole.ButtonText, text)
    palette.setColor(QPalette.ColorRole.Link, accent)
    palette.setColor(QPalette.ColorRole.Highlight, accent)
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    disabled = QPalette.ColorGroup.Disabled
    disabled_text = QColor(118, 126, 122)
    palette.setColor(disabled, QPalette.ColorRole.WindowText, disabled_text)
    palette.setColor(disabled, QPalette.ColorRole.Text, disabled_text)
    palette.setColor(disabled, QPalette.ColorRole.ButtonText, disabled_text)
    palette.setColor(disabled, QPalette.ColorRole.Highlight, alternate_base)
    palette.setColor(disabled, QPalette.ColorRole.HighlightedText, disabled_text)
    return palette

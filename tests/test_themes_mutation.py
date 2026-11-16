"""apply_theme really switches the application style to Fusion."""

from __future__ import annotations

from PyQt6.QtWidgets import QStyleFactory

from my_lastfm_player.themes import ThemeMode, apply_theme


def test_apply_theme_replaces_a_different_style_with_fusion(qapp) -> None:
    available_styles = QStyleFactory.keys()
    other_styles = [key for key in available_styles if key.lower() != "fusion"]
    assert other_styles, "the test needs a second Qt style"
    qapp.setStyle(other_styles[0])
    assert qapp.style().name().lower() != "fusion"

    apply_theme(qapp, ThemeMode.LIGHT)

    assert qapp.style().name().lower() == "fusion"

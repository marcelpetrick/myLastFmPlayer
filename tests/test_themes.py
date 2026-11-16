from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette

from my_lastfm_player.themes import ThemeMode, apply_theme


def test_apply_theme_returns_when_fusion_style_is_unavailable(qapp, monkeypatch) -> None:
    original_style_name = qapp.style().objectName()
    monkeypatch.setattr("my_lastfm_player.themes.QStyleFactory.create", lambda _name: None)

    apply_theme(qapp, ThemeMode.DARK)

    assert qapp.style().objectName() == original_style_name


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


def test_apply_lilac_theme_uses_lilac_accent(qapp) -> None:
    apply_theme(qapp, ThemeMode.LILAC)

    palette = qapp.palette()
    assert palette.color(QPalette.ColorRole.Window) == QColor(248, 244, 255)
    assert palette.color(QPalette.ColorRole.Highlight) == QColor(151, 104, 196)


def test_apply_mint_theme_uses_mint_accent(qapp) -> None:
    apply_theme(qapp, ThemeMode.MINT)

    palette = qapp.palette()
    assert palette.color(QPalette.ColorRole.Window) == QColor(239, 251, 246)
    assert palette.color(QPalette.ColorRole.Highlight) == QColor(42, 157, 116)


def test_apply_light_theme_after_dark_restores_light_palette(qapp) -> None:
    apply_theme(qapp, ThemeMode.DARK)
    apply_theme(qapp, ThemeMode.LIGHT)

    palette = qapp.palette()
    assert palette.color(QPalette.ColorRole.Window) != QColor(53, 53, 53)


def test_theme_mode_enum_values() -> None:
    assert ThemeMode.LIGHT.value == "light"
    assert ThemeMode.DARK.value == "dark"
    assert ThemeMode.LILAC.value == "lilac"
    assert ThemeMode.MINT.value == "mint"
    assert ThemeMode("light") is ThemeMode.LIGHT
    assert ThemeMode("dark") is ThemeMode.DARK
    assert ThemeMode("lilac") is ThemeMode.LILAC
    assert ThemeMode("mint") is ThemeMode.MINT


GOLDEN_PALETTES = Path(__file__).resolve().parent / "fixtures" / "golden" / "theme_palettes.json"
PALETTE_GROUPS = (
    QPalette.ColorGroup.Active,
    QPalette.ColorGroup.Inactive,
    QPalette.ColorGroup.Disabled,
)
PALETTE_ROLES = tuple(role for role in QPalette.ColorRole if role.name != "NColorRoles")


def palette_snapshot(palette: QPalette) -> dict[str, str]:
    return {
        f"{group.name}.{role.name}": palette.color(group, role).name(QColor.NameFormat.HexArgb)
        for group in PALETTE_GROUPS
        for role in PALETTE_ROLES
    }


def test_every_theme_palette_matches_reviewed_snapshot(qapp) -> None:
    """Pin every colour of every theme; regenerate with MY_LASTFM_PLAYER_UPDATE_GOLDEN=1."""

    snapshots = {}
    for mode in ThemeMode:
        apply_theme(qapp, mode)
        snapshots[mode.value] = palette_snapshot(qapp.palette())
    apply_theme(qapp, ThemeMode.LIGHT)

    if os.environ.get("MY_LASTFM_PLAYER_UPDATE_GOLDEN") == "1":
        GOLDEN_PALETTES.write_text(json.dumps(snapshots, indent=2, sort_keys=True) + "\n")
        pytest.skip("updated theme_palettes.json")

    expected = json.loads(GOLDEN_PALETTES.read_text())
    for mode, colors in expected.items():
        mismatches = {
            key: (snapshots[mode][key], value)
            for key, value in colors.items()
            if snapshots[mode][key] != value
        }
        assert not mismatches, f"{mode} palette changed (actual, expected): {mismatches}"
    assert snapshots.keys() == expected.keys()

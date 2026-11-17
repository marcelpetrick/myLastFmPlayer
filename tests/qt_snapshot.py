"""Deterministic JSON snapshot of a Qt widget tree for reviewed golden tests.

Records, for every widget reachable from a root: its attribute name on the root (or a
class/index path), its class, every readable scalar Qt property except those that
depend on fonts, the screen, focus or the current geometry, and the complete layout
tree (spacing, margins, item order, stretch factors). Menus and their actions are
included. A UI construction change - a widget dropped from a layout, a spacing or
range changed, a flag flipped - changes the snapshot.
"""

from __future__ import annotations

import enum
import json
import os
from pathlib import Path

from PyQt6.QtCore import QObject
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QLayout, QSpacerItem, QWidget

from my_lastfm_player import __display_version__

GOLDEN_DIR = Path(__file__).resolve().parent / "fixtures" / "golden"
UPDATE_GOLDEN = os.environ.get("MY_LASTFM_PLAYER_UPDATE_GOLDEN") == "1"

# Properties that depend on the platform font, screen, window manager, focus, or the
# geometry computed for the current content, and so are not stable across machines.
VOLATILE_PROPERTIES = {
    "acceptDrops",
    "baseSize",
    "childrenRect",
    "childrenRegion",
    "cursor",
    "focus",
    "font",
    "frameGeometry",
    "frameSize",
    "fullScreen",
    "geometry",
    "height",
    "isActiveWindow",
    "locale",
    "maximized",
    "maximumHeight",
    "maximumSize",
    "maximumWidth",
    "minimized",
    "minimumHeight",
    "minimumSize",
    "minimumSizeHint",
    "minimumSectionSize",
    "minimumWidth",
    "normalGeometry",
    "palette",
    "pos",
    "rect",
    "size",
    "sizeHint",
    "sizeIncrement",
    "styleSheet",
    "visible",
    "width",
    "windowFilePath",
    "windowIcon",
    "windowIconText",
    "windowModality",
    "windowOpacity",
    "x",
    "y",
}


def _scalar(value: object) -> object:
    if isinstance(value, bool | int | float | str) or value is None:
        if isinstance(value, str):
            return value.replace(__display_version__, "<version>")
        return value
    if isinstance(value, enum.Enum):
        return f"{type(value).__name__}.{value.name}"
    return _UNSUPPORTED


_UNSUPPORTED = object()


def _properties(obj: QObject) -> dict[str, object]:
    meta = obj.metaObject()
    values: dict[str, object] = {}
    for index in range(meta.propertyCount()):
        prop = meta.property(index)
        name = prop.name()
        if name in VOLATILE_PROPERTIES or not prop.isReadable():
            continue
        value = _scalar(prop.read(obj))
        if value is not _UNSUPPORTED:
            values[name] = value
    return values


class _Namer:
    def __init__(self, root: QObject) -> None:
        self.names: dict[int, str] = {}
        for attribute, value in vars(root).items():
            if isinstance(value, QObject | QLayout) and id(value) not in self.names:
                self.names[id(value)] = attribute

    def name(self, obj: object, fallback: str) -> str:
        return self.names.get(id(obj), fallback)


def _layout_tree(layout: QLayout, namer: _Namer, path: str) -> dict[str, object]:
    margins = layout.contentsMargins()
    items: list[object] = []
    for index in range(layout.count()):
        item = layout.itemAt(index)
        stretch = layout.stretch(index) if hasattr(layout, "stretch") else 0
        entry: dict[str, object] = {"stretch": stretch}
        if item.widget() is not None:
            entry["widget"] = namer.name(item.widget(), type(item.widget()).__name__)
        elif item.layout() is not None:
            entry["layout"] = _layout_tree(item.layout(), namer, f"{path}/{index}")
        elif isinstance(item, QSpacerItem) or item.spacerItem() is not None:
            policy = item.spacerItem().sizePolicy()
            entry["spacer"] = [
                f"{policy.horizontalPolicy().name}",
                f"{policy.verticalPolicy().name}",
            ]
        items.append(entry)
    return {
        "name": namer.name(layout, path),
        "class": type(layout).__name__,
        "spacing": layout.spacing(),
        "margins": [margins.left(), margins.top(), margins.right(), margins.bottom()],
        "items": items,
    }


def snapshot(root: QWidget) -> dict[str, object]:
    """Return the JSON-ready snapshot of ``root`` and everything below it."""

    namer = _Namer(root)
    widgets: dict[str, object] = {}
    counter = 0
    for widget in [root, *root.findChildren(QWidget)]:
        key = namer.name(widget, "")
        if not key:
            counter += 1
            key = f"{type(widget).__name__}#{counter}"
        parent = widget.parentWidget()
        entry: dict[str, object] = {
            "class": type(widget).__name__,
            "parent": namer.name(parent, type(parent).__name__) if parent else None,
            "properties": _properties(widget),
        }
        if widget.layout() is not None:
            entry["layout"] = _layout_tree(widget.layout(), namer, key)
        widgets[key] = entry
    actions = {}
    for index, action in enumerate(root.findChildren(QAction)):
        actions[namer.name(action, f"QAction#{index}")] = _properties(action)
    return {"widgets": widgets, "actions": actions}


def assert_matches_golden(root: QWidget, name: str) -> None:
    """Compare ``root`` with ``fixtures/golden/<name>.json`` (or rewrite it)."""

    actual = json.loads(json.dumps(snapshot(root), sort_keys=True))
    path = GOLDEN_DIR / f"{name}.json"
    if UPDATE_GOLDEN:
        path.write_text(json.dumps(actual, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        return
    expected = json.loads(path.read_text(encoding="utf-8"))
    differences = _diff(expected, actual, name)
    assert not differences, "UI snapshot changed:\n" + "\n".join(differences[:20])


def _diff(expected: object, actual: object, path: str) -> list[str]:
    if isinstance(expected, dict) and isinstance(actual, dict):
        lines: list[str] = []
        for key in sorted(set(expected) | set(actual)):
            if key not in actual:
                lines.append(f"{path}/{key}: missing")
            elif key not in expected:
                lines.append(f"{path}/{key}: unexpected {actual[key]!r}"[:200])
            else:
                lines.extend(_diff(expected[key], actual[key], f"{path}/{key}"))
        return lines
    if expected != actual:
        return [f"{path}: expected {expected!r}, got {actual!r}"[:300]]
    return []

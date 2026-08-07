from __future__ import annotations

import re
from pathlib import Path

from my_lastfm_player import __version__

REPO_ROOT = Path(__file__).resolve().parents[1]
README_PATH = REPO_ROOT / "README.md"
README_VERSION_PATTERN = re.compile(r"^Current version: `([^`]+)`", re.MULTILINE)


def readme_version() -> str:
    match = README_VERSION_PATTERN.search(README_PATH.read_text(encoding="utf-8"))
    assert match is not None, "README.md must state 'Current version: `X.Y.Z`'"
    return match.group(1)


def test_readme_version_matches_package_version() -> None:
    assert readme_version() == __version__

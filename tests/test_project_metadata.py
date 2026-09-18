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


def test_current_documents_carry_no_version_that_can_go_stale() -> None:
    import sys

    sys.path.insert(0, str(REPO_ROOT / "tools"))
    import check_docs

    assert check_docs.check_current_document_versions(REPO_ROOT) == []


def test_current_document_version_check_rejects_a_stale_stamp(tmp_path) -> None:
    import sys

    sys.path.insert(0, str(REPO_ROOT / "tools"))
    import check_docs

    document = tmp_path / check_docs.CURRENT_DOCUMENTS[0]
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text("# Doc\n\nDescribes myLastFmPlayer 0.0.1.\n", encoding="utf-8")

    errors = check_docs.check_current_document_versions(tmp_path)

    assert len(errors) == 1
    assert "0.0.1" in errors[0]

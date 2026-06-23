from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

from tools.build_release_artifacts import ARCHIVE_DESCRIPTIONS, build_release_artifacts


def _write(path: Path, content: str = "content") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_release_artifacts_creates_complete_described_zip_set(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    report_dir = repo_root / "release-artifacts/raw"
    output_dir = repo_root / "release-artifacts/assets"

    _write(repo_root / "dist/my_lastfm_player-1.2.3-py3-none-any.whl")
    _write(repo_root / "dist/my_lastfm_player-1.2.3.tar.gz")
    _write(repo_root / "docs/architecture.rst", "Architecture")
    _write(repo_root / "docs/_build/html/index.html", "Sphinx")
    _write(repo_root / "docs/_build/html/architecture.html", "C4")
    _write(repo_root / "docs/_build/html/_static/basic.css", "CSS")
    _write(repo_root / "docs/_build/html/_images/graphviz-context.png", "PNG")
    _write(repo_root / "docs/_build/html/_images/inheritance-main.png", "PNG")
    _write(repo_root / "htmlcov/index.html", "Coverage")

    for report_name in (
        "coverage.xml",
        "docs.log",
        "environment.txt",
        "import-check.log",
        "junit.xml",
        "pipeline-console.log",
        "pylint.log",
        "pytest.log",
        "ruff.log",
        "sphinx.log",
        "summary.txt",
        "translations.log",
    ):
        _write(report_dir / report_name, report_name)

    created = build_release_artifacts(
        repo_root=repo_root,
        report_dir=report_dir,
        output_dir=output_dir,
        version="1.2.3",
        commit="abcdef123456",
        run_id="42",
        generated_at="2026-06-23T12:00:00Z",
    )

    assert [path.name for path in created] == [
        f"my-lastfm-player-1.2.3-{name}.zip" for name in ARCHIVE_DESCRIPTIONS
    ]

    for archive_path in created:
        with ZipFile(archive_path) as archive:
            readme = archive.read("README.txt").decode()
            assert "Application version: 1.2.3" in readme
            assert "Commit: abcdef123456" in readme
            assert "GitHub Actions run ID: 42" in readme
            assert "Generated at: 2026-06-23T12:00:00Z" in readme

    with ZipFile(output_dir / "my-lastfm-player-1.2.3-c4-architecture.zip") as archive:
        assert "architecture.rst" in archive.namelist()
        assert "architecture.html" in archive.namelist()
        assert "_images/graphviz-context.png" in archive.namelist()
        assert "_images/inheritance-main.png" in archive.namelist()

    with ZipFile(output_dir / "my-lastfm-player-1.2.3-test-results.zip") as archive:
        assert {"pytest.log", "junit.xml"} <= set(archive.namelist())

    with ZipFile(output_dir / "my-lastfm-player-1.2.3-pipeline-trace.zip") as archive:
        assert "pipeline-trace/summary.txt" in archive.namelist()
        assert "pipeline-trace/environment.txt" in archive.namelist()

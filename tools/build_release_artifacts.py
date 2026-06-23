from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from collections.abc import Iterable
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ARCHIVE_DESCRIPTIONS = {
    "packages": "Installable Python wheel and source distribution.",
    "sphinx-docs": "Browsable Sphinx HTML documentation. Open index.html.",
    "c4-architecture": (
        "C4 architecture source, rendered architecture page, and generated diagrams. "
        "Open architecture.html."
    ),
    "test-results": "Pytest console output and machine-readable JUnit XML test results.",
    "coverage": "HTML and XML unit-test coverage reports. Open htmlcov/index.html.",
    "static-analysis": "Ruff and Pylint static-analysis console reports.",
    "pipeline-trace": (
        "Pipeline summary, build logs, documentation and translation checks, "
        "package verification, and environment metadata."
    ),
}


def _git_output(repo_root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip() if completed.returncode == 0 else ""


def _readme_text(
    *,
    archive_name: str,
    description: str,
    version: str,
    commit: str,
    run_id: str,
    generated_at: str,
) -> str:
    return (
        f"{archive_name}\n"
        f"{'=' * len(archive_name)}\n\n"
        f"{description}\n\n"
        f"Application version: {version}\n"
        f"Commit: {commit or 'unknown'}\n"
        f"GitHub Actions run ID: {run_id or 'local'}\n"
        f"Generated at: {generated_at or 'unknown'}\n"
        "Pipeline command: ./localPipeline.sh --noRun --report-dir release-artifacts/raw\n"
        "Archive command: python tools/build_release_artifacts.py\n"
    )


def _iter_files(path: Path) -> Iterable[Path]:
    if path.is_file():
        yield path
    elif path.is_dir():
        yield from sorted(candidate for candidate in path.rglob("*") if candidate.is_file())


def _add_path(archive: ZipFile, source: Path, archive_path: Path) -> None:
    if source.is_file():
        archive.write(source, archive_path.as_posix())
        return

    for file_path in _iter_files(source):
        relative_path = file_path.relative_to(source)
        archive.write(file_path, (archive_path / relative_path).as_posix())


def _create_archive(
    *,
    output_path: Path,
    readme: str,
    paths: Iterable[tuple[Path, Path]],
) -> None:
    with ZipFile(output_path, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        archive.writestr("README.txt", readme)
        for source, archive_path in paths:
            if source.exists():
                _add_path(archive, source, archive_path)


def _require_paths(paths: Iterable[Path]) -> None:
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Required release inputs are missing: {', '.join(missing)}")


def _copy_c4_assets(repo_root: Path, staging_dir: Path) -> None:
    html_dir = repo_root / "docs/_build/html"
    shutil.copy2(repo_root / "docs/architecture.rst", staging_dir / "architecture.rst")
    shutil.copy2(html_dir / "architecture.html", staging_dir / "architecture.html")
    shutil.copytree(html_dir / "_static", staging_dir / "_static")

    images_dir = staging_dir / "_images"
    images_dir.mkdir()
    for pattern in ("graphviz-*", "inheritance-*"):
        for image_path in sorted((html_dir / "_images").glob(pattern)):
            if image_path.is_file():
                shutil.copy2(image_path, images_dir / image_path.name)


def build_release_artifacts(
    *,
    repo_root: Path,
    report_dir: Path,
    output_dir: Path,
    version: str,
    commit: str = "",
    run_id: str = "",
    generated_at: str = "",
) -> list[Path]:
    commit = commit or _git_output(repo_root, "rev-parse", "HEAD")
    run_id = run_id or os.environ.get("GITHUB_RUN_ID", "")
    generated_at = generated_at or os.environ.get("RELEASE_GENERATED_AT", "")
    prefix = f"my-lastfm-player-{version}"

    output_dir.mkdir(parents=True, exist_ok=True)
    for old_archive in output_dir.glob(f"{prefix}-*.zip"):
        old_archive.unlink()

    c4_staging = output_dir / ".c4-staging"
    _require_paths(
        [
            repo_root / "dist",
            repo_root / "docs/architecture.rst",
            repo_root / "docs/_build/html/index.html",
            repo_root / "docs/_build/html/architecture.html",
            repo_root / "docs/_build/html/_static",
            repo_root / "docs/_build/html/_images",
            repo_root / "htmlcov/index.html",
            report_dir / "pytest.log",
            report_dir / "junit.xml",
            report_dir / "coverage.xml",
            report_dir / "ruff.log",
            report_dir / "pylint.log",
            report_dir / "summary.txt",
            report_dir / "environment.txt",
        ]
    )
    shutil.rmtree(c4_staging, ignore_errors=True)
    c4_staging.mkdir()
    _copy_c4_assets(repo_root, c4_staging)

    archive_inputs: dict[str, list[tuple[Path, Path]]] = {
        "packages": [(repo_root / "dist", Path("dist"))],
        "sphinx-docs": [(repo_root / "docs/_build/html", Path("sphinx-html"))],
        "c4-architecture": [(c4_staging, Path("."))],
        "test-results": [
            (report_dir / "pytest.log", Path("pytest.log")),
            (report_dir / "junit.xml", Path("junit.xml")),
        ],
        "coverage": [
            (repo_root / "htmlcov", Path("htmlcov")),
            (report_dir / "coverage.xml", Path("coverage.xml")),
        ],
        "static-analysis": [
            (report_dir / "ruff.log", Path("ruff.log")),
            (report_dir / "pylint.log", Path("pylint.log")),
        ],
        "pipeline-trace": [
            (report_dir, Path("pipeline-trace")),
        ],
    }

    created: list[Path] = []
    for archive_name, paths in archive_inputs.items():
        output_path = output_dir / f"{prefix}-{archive_name}.zip"
        readme = _readme_text(
            archive_name=output_path.name,
            description=ARCHIVE_DESCRIPTIONS[archive_name],
            version=version,
            commit=commit,
            run_id=run_id,
            generated_at=generated_at,
        )
        _create_archive(output_path=output_path, readme=readme, paths=paths)
        created.append(output_path)

    shutil.rmtree(c4_staging)
    return created


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build ZIP archives for a GitHub Release.")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--report-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--commit", default="")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--generated-at", default="")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    created = build_release_artifacts(
        repo_root=args.repo_root.resolve(),
        report_dir=args.report_dir.resolve(),
        output_dir=args.output_dir.resolve(),
        version=args.version,
        commit=args.commit,
        run_id=args.run_id,
        generated_at=args.generated_at,
    )
    for archive_path in created:
        print(archive_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

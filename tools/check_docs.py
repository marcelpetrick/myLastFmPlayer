from __future__ import annotations

from pathlib import Path

REQUIRED_FILES = [
    Path("README.md"),
    Path("LICENSE"),
    Path("documents/00_REQUIREMENTS.md"),
    Path("documents/01_IMPLEMENTATION_PLAN.md"),
    Path("documents/02_DEVELOPMENT_PLAN.md"),
    Path("documents/03_ARCHITECTURE.md"),
    Path("documents/IMPROVEMENTS.md"),
]

REQUIRED_README_SNIPPETS = [
    "Author: Marcel Petrick <mail@marcelpetrick.it>",
    "License: GPLv3 or later.",
    "Current version: `00.00.12`",
    "MAJOR.MINOR.PATCH",
    "every future commit should increase the `PATCH` number",
    "python3 -m venv .venv",
    "python -m pip install -e .",
]


def _has_trailing_whitespace(line: str) -> bool:
    return line.rstrip("\n\r").endswith((" ", "\t"))


def check_required_files(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for relative_path in REQUIRED_FILES:
        path = repo_root / relative_path
        if not path.is_file():
            errors.append(f"Missing required documentation file: {relative_path}")
    return errors


def check_markdown(repo_root: Path) -> list[str]:
    errors: list[str] = []
    markdown_files = sorted(repo_root.glob("**/*.md"))
    markdown_files = [path for path in markdown_files if ".venv" not in path.parts]

    if not markdown_files:
        return ["No Markdown files found"]

    for path in markdown_files:
        relative_path = path.relative_to(repo_root)
        text = path.read_text(encoding="utf-8")
        if not any(line.startswith("# ") for line in text.splitlines()):
            errors.append(f"{relative_path}: file should contain a top-level Markdown heading")
        if not text.endswith("\n"):
            errors.append(f"{relative_path}: file should end with a newline")
        for line_number, line in enumerate(text.splitlines(keepends=True), start=1):
            if _has_trailing_whitespace(line):
                errors.append(f"{relative_path}:{line_number}: trailing whitespace")
    return errors


def check_readme(repo_root: Path) -> list[str]:
    readme_path = repo_root / "README.md"
    if not readme_path.is_file():
        return []

    readme = readme_path.read_text(encoding="utf-8")
    return [
        f"README.md: missing required text: {snippet}"
        for snippet in REQUIRED_README_SNIPPETS
        if snippet not in readme
    ]


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    errors = [
        *check_required_files(repo_root),
        *check_markdown(repo_root),
        *check_readme(repo_root),
    ]

    if errors:
        print("Documentation check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Documentation check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

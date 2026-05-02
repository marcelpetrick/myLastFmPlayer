from __future__ import annotations

import ast
import subprocess
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py
from setuptools.command.sdist import sdist as _sdist

PACKAGE_NAME = "my_lastfm_player"
BUILD_INFO_MODULE = "_build_info.py"
COMMIT_HASH_LENGTH = 6


def read_existing_commit(root: Path) -> str:
    build_info_path = root / PACKAGE_NAME / BUILD_INFO_MODULE
    if not build_info_path.is_file():
        return ""

    for line in build_info_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("__commit__"):
            _, value = line.split("=", 1)
            commit = ast.literal_eval(value.strip())
            return commit if isinstance(commit, str) else ""
    return ""


def resolve_commit(root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", f"--short={COMMIT_HASH_LENGTH}", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return read_existing_commit(root)

    return completed.stdout.strip()[:COMMIT_HASH_LENGTH]


def build_info_content(commit: str) -> str:
    return (
        '"""Generated build metadata."""\n'
        "\n"
        f'__commit__ = "{commit}"\n'
    )


def write_build_info(target_root: Path, commit: str) -> None:
    target_path = target_root / PACKAGE_NAME / BUILD_INFO_MODULE
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(build_info_content(commit), encoding="utf-8")


class build_py(_build_py):
    def run(self) -> None:
        super().run()
        root = Path(__file__).resolve().parent
        write_build_info(Path(self.build_lib), resolve_commit(root))


class sdist(_sdist):
    def make_release_tree(self, base_dir: str, files: list[str]) -> None:
        super().make_release_tree(base_dir, files)
        root = Path(__file__).resolve().parent
        write_build_info(Path(base_dir), resolve_commit(root))


setup(cmdclass={"build_py": build_py, "sdist": sdist})

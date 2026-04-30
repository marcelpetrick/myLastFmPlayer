from __future__ import annotations

import shutil
from collections.abc import Callable, Iterable
from dataclasses import dataclass

REQUIRED_EXTERNAL_TOOLS = ("yt-dlp", "ffmpeg")


@dataclass(frozen=True, slots=True)
class DependencyCheckResult:
    """Result of checking whether required external commands are installed."""

    installed: tuple[str, ...]
    missing: tuple[str, ...]

    @property
    def is_ok(self) -> bool:
        """Return ``True`` when no required command is missing."""

        return not self.missing

    def user_message(self) -> str:
        """Return a concise status message for display in the UI."""

        if self.is_ok:
            return f"Dependencies installed: {', '.join(self.installed)}"
        return f"Missing dependencies: {', '.join(self.missing)}"


def check_external_dependencies(
    required_tools: Iterable[str] = REQUIRED_EXTERNAL_TOOLS,
    which: Callable[[str], str | None] = shutil.which,
) -> DependencyCheckResult:
    """Check all ``required_tools`` with ``which`` and return their availability."""

    installed: list[str] = []
    missing: list[str] = []

    for tool in required_tools:
        if which(tool):
            installed.append(tool)
        else:
            missing.append(tool)

    return DependencyCheckResult(installed=tuple(installed), missing=tuple(missing))

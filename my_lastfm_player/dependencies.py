from __future__ import annotations

import shutil
from collections.abc import Callable, Iterable
from dataclasses import dataclass

from my_lastfm_player.i18n import translate

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

        tools = ", ".join(self.installed if self.is_ok else self.missing)
        if self.is_ok:
            return translate(
                "DependencyCheckResult",
                "Dependencies installed: {tools}",
                tools=tools,
            )
        return translate("DependencyCheckResult", "Missing dependencies: {tools}", tools=tools)


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

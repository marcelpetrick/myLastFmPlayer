"""Application version information."""

from __future__ import annotations

from importlib import import_module

__version__ = "0.0.75"

_COMMIT_HASH_LENGTH = 6


def build_commit() -> str:
    """Return the build-time git commit suffix when packaged metadata exists."""

    try:
        build_info = import_module("my_lastfm_player._build_info")
    except ModuleNotFoundError:
        return ""

    commit = getattr(build_info, "__commit__", "")
    if not isinstance(commit, str):
        return ""

    return commit.strip()[:_COMMIT_HASH_LENGTH]


def display_version(version: str = __version__, commit: str | None = None) -> str:
    """Return the user-visible version string."""

    resolved_commit = build_commit() if commit is None else commit.strip()
    if not resolved_commit:
        return version
    return f"{version}+{resolved_commit[:_COMMIT_HASH_LENGTH]}"


__commit__ = build_commit()
__display_version__ = display_version(__version__, __commit__)

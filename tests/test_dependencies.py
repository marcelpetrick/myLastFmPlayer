from __future__ import annotations

from my_lastfm_player.dependencies import (
    REQUIRED_EXTERNAL_TOOLS,
    DependencyCheckResult,
    check_external_dependencies,
)


def test_required_external_tools_includes_ffprobe() -> None:
    assert "ffprobe" in REQUIRED_EXTERNAL_TOOLS
    assert "yt-dlp" in REQUIRED_EXTERNAL_TOOLS
    assert "ffmpeg" in REQUIRED_EXTERNAL_TOOLS


def test_dependency_check_reports_installed_and_missing_tools() -> None:
    def fake_which(tool: str) -> str | None:
        return f"/usr/bin/{tool}" if tool == "ffmpeg" else None

    result = check_external_dependencies(("ffmpeg", "yt-dlp"), which=fake_which)

    assert result == DependencyCheckResult(installed=("ffmpeg",), missing=("yt-dlp",))
    assert not result.is_ok
    assert result.user_message() == "🔴 Missing dependencies: yt-dlp"


def test_dependency_check_reports_success_message() -> None:
    result = check_external_dependencies(("ffmpeg",), which=lambda tool: f"/usr/bin/{tool}")

    assert result.is_ok
    assert result.user_message() == "🟢 Dependencies installed: ffmpeg"

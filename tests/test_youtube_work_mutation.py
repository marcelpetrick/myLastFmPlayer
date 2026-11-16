"""run_cancellable_command treats an exhausted time budget as a timeout."""

from __future__ import annotations

import subprocess
from types import SimpleNamespace

import pytest

from my_lastfm_player import youtube_work
from my_lastfm_player.youtube_work import run_cancellable_command


class InstantProcess:
    pid = 4321
    returncode = 0

    def __init__(self, command, **kwargs) -> None:
        self.command = command

    def communicate(self, timeout=None):
        return "out", "err"


def test_a_zero_budget_times_out_before_waiting_for_output(monkeypatch) -> None:
    terminated: list[InstantProcess] = []
    fake_subprocess = SimpleNamespace(
        Popen=InstantProcess,
        PIPE=subprocess.PIPE,
        TimeoutExpired=subprocess.TimeoutExpired,
        CompletedProcess=subprocess.CompletedProcess,
    )
    monkeypatch.setattr(youtube_work, "subprocess", fake_subprocess)
    monkeypatch.setattr(youtube_work, "time", SimpleNamespace(monotonic=lambda: 100.0))
    monkeypatch.setattr(youtube_work, "_terminate_process", terminated.append)

    with pytest.raises(subprocess.TimeoutExpired):
        run_cancellable_command(["yt-dlp", "--version"], stop_event=None, timeout=0)

    assert len(terminated) == 1

"""Every text file and subprocess pipe is opened with an explicit UTF-8 encoding.

Several ``encoding="utf-8"`` lines carry ``# pragma: no mutate`` because ``"UTF-8"`` is
the same codec. That pragma also hides the ``encoding=None`` mutant, which is not
equivalent: on a non-UTF-8 locale (e.g. Windows cp1252) artist names would be
corrupted. These spies keep that guarantee independent of the test machine's locale.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from my_lastfm_player import storage, youtube_work
from my_lastfm_player.models import Track
from my_lastfm_player.storage import JsonTrackRepository


def test_storage_reads_and_writes_text_as_utf8(tmp_path: Path, monkeypatch) -> None:
    encodings: list[tuple[str, object]] = []
    real_open = Path.open
    real_read_text = Path.read_text
    real_fdopen = os.fdopen

    def spy_open(self, mode="r", *args, **kwargs):
        encodings.append((f"open:{mode}", kwargs.get("encoding")))
        return real_open(self, mode, *args, **kwargs)

    def spy_read_text(self, *args, **kwargs):
        encodings.append(("read_text", kwargs.get("encoding")))
        return real_read_text(self, *args, **kwargs)

    def spy_fdopen(fd, mode="r", *args, **kwargs):
        encodings.append((f"fdopen:{mode}", kwargs.get("encoding")))
        return real_fdopen(fd, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", spy_open)
    monkeypatch.setattr(Path, "read_text", spy_read_text)
    monkeypatch.setattr(storage.os, "fdopen", spy_fdopen)
    repository = JsonTrackRepository(data_dir=tmp_path)

    repository.save_tracks("alice", [Track("Björk", "Jóga")])
    repository.append_track_update("alice", Track("Sigur Rós", "Hoppípolla"))
    tracks = repository.load_tracks("alice")

    assert [track.artist for track in tracks] == ["Björk", "Sigur Rós"]
    used = {kind for kind, _encoding in encodings}
    assert {"fdopen:w", "open:a", "open:r", "read_text"} <= used
    assert all(encoding == "utf-8" for _kind, encoding in encodings), encodings


def test_cancellable_command_decodes_output_as_utf8_text(monkeypatch) -> None:
    captured: dict = {}

    class FakePopen:
        pid = 1
        returncode = 0

        def __init__(self, command, **kwargs) -> None:
            captured.update(kwargs)

        def communicate(self, timeout=None):
            return "out", "err"

    monkeypatch.setattr(youtube_work.subprocess, "Popen", FakePopen)

    youtube_work.run_cancellable_command(["tool"], stop_event=None, timeout=5)

    assert captured["encoding"] == "utf-8"
    assert captured["text"] is True
    assert captured["stdout"] is subprocess.PIPE
    assert captured["stderr"] is subprocess.PIPE


@pytest.mark.parametrize("module", [storage, youtube_work])
def test_modules_name_utf8_explicitly(module) -> None:
    """A cheap backstop: the source must not rely on the locale default anywhere."""

    source = Path(module.__file__).read_text(encoding="utf-8")

    assert "encoding=None" not in source
    assert 'encoding="utf-8"' in source

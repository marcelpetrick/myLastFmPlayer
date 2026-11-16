"""configure_logging writes to the standard output stream current at call time."""

from __future__ import annotations

import io
import logging
import sys

from my_lastfm_player.logging_config import configure_logging


def test_configure_logging_writes_to_stdout(monkeypatch) -> None:
    root_logger = logging.getLogger()
    saved_handlers = list(root_logger.handlers)
    saved_level = root_logger.level
    stream = io.StringIO()
    monkeypatch.setattr(sys, "stdout", stream)
    try:
        configure_logging(logging.INFO)
        logging.getLogger("my_lastfm_player.test").info("hello stdout")
        handler_streams = [getattr(handler, "stream", None) for handler in root_logger.handlers]
    finally:
        for handler in list(root_logger.handlers):
            root_logger.removeHandler(handler)
        for handler in saved_handlers:
            root_logger.addHandler(handler)
        root_logger.setLevel(saved_level)

    assert handler_streams == [stream]
    assert "INFO [my_lastfm_player.test] hello stdout" in stream.getvalue()

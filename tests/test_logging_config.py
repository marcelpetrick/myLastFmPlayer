from __future__ import annotations

import logging

from my_lastfm_player.logging_config import LOG_FORMAT, configure_logging


def test_configure_logging_sets_root_level() -> None:
    configure_logging(logging.DEBUG)

    root_logger = logging.getLogger()
    assert root_logger.level == logging.DEBUG
    assert root_logger.handlers
    assert root_logger.handlers[0].formatter is not None
    assert root_logger.handlers[0].formatter._fmt == LOG_FORMAT

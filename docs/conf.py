from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

project = "myLastFmPlayer"
author = "Marcel Petrick"
copyright = "2026, Marcel Petrick"

from my_lastfm_player.version import __version__  # noqa: E402

release = __version__
version = __version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "exclude-members": (
        "download_requested,error,fetch_pause_requested,fetch_requested,"
        "fetch_stop_requested,fetch_stopped,finished,pause_requested,"
        "play_requested,progress,seek_requested,stop_requested,track_updated,tracks_downloaded,"
        "tracks_loaded,tracks_resolved,tracks_updated"
    ),
}
autodoc_typehints = "description"
autodoc_typehints_format = "short"
html_theme = "alabaster"
nitpicky = False

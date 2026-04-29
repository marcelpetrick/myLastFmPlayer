# myLastFmPlayer

`myLastFmPlayer` is a Linux desktop application for collecting a user's loved tracks from Last.fm, preparing them for lookup/download, and eventually playing downloaded audio locally. The MVP is implemented in Python with PyQt.

Author: Marcel Petrick <mail@marcelpetrick.it>

License: GPLv3 or later. See `LICENSE`.

## Requirements

- Linux x86_64
- Python 3.11 or newer
- `venv` support for Python

Later MVP steps will also require:

- `yt-dlp`
- `ffmpeg`

On Manjaro:

```bash
sudo pacman -S yt-dlp ffmpeg
```

## Build and Run with a Virtual Environment

Create the virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install the app in editable mode:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

Run the app:

```bash
my-lastfm-player
```

Alternatively:

```bash
python -m my_lastfm_player
```

## Current State

Step 0 of the development plan is implemented: a basic PyQt application shell with the main controls and table needed for the MVP. Feature implementations for scraping, storage, downloads, and playback are planned in `documents/02_DEVELOPMENT_PLAN.md`.

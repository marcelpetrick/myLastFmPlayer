# myLastFmPlayer

`myLastFmPlayer` is a (Linux) desktop application for collecting a user's loved tracks from Last.fm, preparing them for lookup/download, and eventually playing downloaded audio locally. The MVP is implemented in Python with PyQt.

Author: Marcel Petrick <mail@marcelpetrick.it>

License: GPLv3 or later. See `LICENSE`.

Current version: `00.00.03`

## Versioning

This project uses a two-digit SemVer-style version number:

```text
MAJOR.MINOR.PATCH
```

Each numeric part is written with two digits. The first version was `00.00.01`.

- `MAJOR`: incompatible or breaking changes.
- `MINOR`: backwards-compatible feature additions.
- `PATCH`: fixes, documentation, tooling, and other incremental changes.

For this project, every future commit should increase the `PATCH` number unless the change intentionally requires a `MINOR` or `MAJOR` bump.

## Requirements

- Linux x86_64
- Python 3.11 or newer
- `venv` support for Python

Later MVP steps will also require:

- `yt-dlp`
- `ffmpeg`

On Manjaro:

```sh
sudo pacman -S yt-dlp ffmpeg
```

## Build and Run with a Virtual Environment

Create the virtual environment:

```sh
python3 -m venv .venv
```

Activate it:

```sh
source .venv/bin/activate
```

Install the app in editable mode:

```sh
python -m pip install --upgrade pip
python -m pip install -e .
```

Run the app:

```sh
my-lastfm-player
```

Alternatively:

```sh
python -m my_lastfm_player
```

## Local Pipeline

Install development dependencies and run the full local build, lint, documentation, test, coverage, package, and install verification sequence:

```sh
./localPipeline.sh
```

The pipeline uses `.venv`, creates it when missing, installs the project with development dependencies, runs Ruff, checks required documentation, runs pytest with coverage, builds the package, installs the built wheel, and verifies the package can be imported.

After the pipeline completes, open the HTML coverage report at:

```sh
htmlcov/index.html
```

## Current State

Steps 0 and 1 of the development plan are implemented: a basic PyQt application shell plus the local testing, coverage, linting, documentation, build, and package verification workflow. Feature implementations for scraping, storage, downloads, and playback are planned in `documents/02_DEVELOPMENT_PLAN.md`.

# myLastFmPlayer

`myLastFmPlayer` is a (Linux) desktop application for collecting a user's loved tracks from Last.fm, preparing them for lookup/download, and eventually playing downloaded audio locally. The MVP is implemented in Python with PyQt.

**Author: Marcel Petrick <mail@marcelpetrick.it>**

**Note: projected is generated with AI.**

**License: GPLv3 or later. See `LICENSE`.**

Current version: `00.00.28` - work in progress; tons of features are not implemented

## Current state

![](media/currentState.png)

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

## How to Use the Player

Start the application, enter a Last.fm username, and press Fetch. The app loads that user's public loved-track list from Last.fm, stores it locally, resolves the tracks through `yt-dlp`, and starts downloading playable MP3 files into the local downloads directory.

The normal workflow is:

1. Enter a Last.fm username.
2. Press Fetch.
3. Wait while the loved-track list is fetched and shown in the table.
4. The app automatically starts YouTube lookup for the fetched tracks.
5. The app automatically starts the download queue for resolved tracks.
6. Select a downloaded track and press Play.

```mermaid
flowchart TD
    A["Enter Last.fm username"] --> B["Press Fetch"]
    B --> C["Fetch public loved-track list from Last.fm"]
    C --> D["Show tracks in the table"]
    D --> E["Resolve tracks through yt-dlp search"]
    E --> F["Queue resolved tracks for download"]
    F --> G["Download MP3 files"]
    G --> H["Select downloaded track"]
    H --> I["Press Play"]
    I --> J["Play local MP3"]
```

If you press Play on a track that is not downloaded yet, the app prepares that selection first. It prioritizes the selected track, resolves its YouTube URL if needed, downloads only that track first, and then starts playback when the local file is ready.

```mermaid
flowchart TD
    A["Select track"] --> B["Press Play"]
    B --> C{"Already downloaded?"}
    C -->|yes| D["Play local MP3"]
    C -->|no| E{"YouTube URL known?"}
    E -->|no| F["Priority lookup for selected track"]
    E -->|yes| G["Priority download for selected track"]
    F --> G
    G --> H["Store downloaded MP3 path"]
    H --> D
```

Progress and errors are shown in the status bar at the bottom of the window and in the feedback area. The terminal also prints detailed logging when the app is started from `localPipeline.sh` or from a shell.

## Stored Files

By default, downloaded MP3 files are stored here:

```text
~/.local/share/myLastFmPlayer/downloads/
```

Per-user track lists are stored as JSON files here:

```text
~/.local/share/myLastFmPlayer/tracks/
```

The shared download cache is stored here:

```text
~/.local/share/myLastFmPlayer/download-cache.json
```

If `XDG_DATA_HOME` is set, the base directory changes to:

```text
$XDG_DATA_HOME/myLastFmPlayer/
```

For example, with `XDG_DATA_HOME=/tmp/app-data`, downloads are stored in:

```text
/tmp/app-data/myLastFmPlayer/downloads/
```

## Local Pipeline

Install development dependencies and run the full local build, lint, documentation, test, coverage, package, install verification sequence, and then start the installed application:

```sh
./localPipeline.sh
```

The pipeline uses `.venv`, creates it when missing, installs the project with development dependencies, runs Ruff, checks required documentation, runs pytest with coverage, opens the HTML coverage report when possible, builds the package, installs the built wheel, verifies the package can be imported, and then starts `my-lastfm-player` like a user would.

### Build Workflow

`localPipeline.sh` is the canonical local build workflow. It records each stage as `PASS`, `FAIL`, `SKIP`, or `WARN` and prints the complete summary at the end, so a developer can see the build state in one place.

```mermaid
flowchart TD
    A["Start ./localPipeline.sh"] --> B{"--noRun provided?"}
    B -->|yes| C["Set RUN_APP=false"]
    B -->|no| D["Keep RUN_APP=true"]
    C --> E{"Is .venv/bin/python executable?"}
    D --> E
    E -->|no| F["Create .venv with python3 -m venv"]
    E -->|yes| G["Use existing .venv"]
    F --> H["Install project in editable mode with dev dependencies"]
    G --> H
    H --> I["Ruff lint check"]
    I --> J["Documentation check"]
    J --> K["Pytest with coverage and HTML report"]
    K --> L["Open htmlcov/index.html when possible"]
    L --> M["Remove old build artifacts"]
    M --> N["Build source/wheel distributions"]
    N --> O["Find built wheel in dist/"]
    O --> P["Force reinstall built wheel without dependencies"]
    P --> Q["Import package and print version"]
    Q --> R{"RUN_APP=true?"}
    R -->|yes| S["Start installed my-lastfm-player command"]
    R -->|no| T["Skip GUI startup"]
    S --> U["Print stage summary and exit"]
    T --> U
```

The workflow phases are:

1. Argument handling: accepts only `--noRun`; any other argument stops the pipeline with usage help.
2. Environment preparation: creates `.venv` only when `.venv/bin/python` is missing, otherwise reuses the existing virtual environment.
3. Dependency installation: runs `python -m pip install -e ".[dev]"` so the app and development tools come from the same environment.
4. Quality gates: runs Ruff, required documentation checks, and pytest with configured coverage reporting.
5. Report opening: prints `htmlcov/index.html` and tries to open it with the desktop opener when `xdg-open` or `open` is available; a failed auto-open is reported as `WARN`, not as a failed build.
6. Package build: removes stale `build/`, `dist/`, and egg-info output before running `python -m build`.
7. Install verification: installs the freshly built wheel and imports `my_lastfm_player` to confirm the packaged application exposes its version.
8. Runtime smoke check: starts `my-lastfm-player` unless `--noRun` was provided.
9. Final summary: prints a stage-by-stage table so the developer can see which parts passed, failed, were skipped, or only produced warnings.

To run every check without launching the GUI at the end:

```sh
./localPipeline.sh --noRun
```

After the pipeline completes, open the HTML coverage report at:

```sh
htmlcov/index.html
```

The normal pipeline does not require internet access. To include the live Last.fm end-to-end test for the hardwired user `first`, run:

```sh
MY_LASTFM_PLAYER_RUN_LASTFM_E2E=1 ./localPipeline.sh --noRun
```

That test fetches all loved-track pages from Last.fm for `first` and prints the tracks during the test run.

## Current State

Steps 0 through 10 of the development plan are implemented for the local MVP path: fetching a username now continues automatically into YouTube lookup and the download queue, and downloaded tracks can be played locally. Pressing Play on a not-yet-downloaded track starts a priority lookup/download for that selection. Remaining hardening topics are tracked in `documents/05_IMPROVEMENTS.md`.

# Agent Guidelines

Rules and repository notes for every automated coding assistant working on this
project.

## Common commands

All commands assume the project's `.venv` is active or that binaries are invoked
through `.venv/bin/`.

- Full local pipeline: `./localPipeline.sh`
- Pre-commit pipeline without launching the GUI: `./localPipeline.sh --noRun`
- Run the app from source: `my-lastfm-player` or `python -m my_lastfm_player`
- Lint: `python -m ruff check .`
- Tests with coverage: `python -m pytest`
- Single test: `python -m pytest tests/test_controller.py::test_name -v`
- Live Last.fm end-to-end test:
  `MY_LASTFM_PLAYER_RUN_LASTFM_E2E=1 python -m pytest tests/test_lastfm_e2e.py`
- Documentation gate: `python tools/check_docs.py`
- Sphinx docs:
  `python -m sphinx -W --keep-going -b html docs build/sphinx/html`
- Regenerate Qt translation source files after changing user-visible strings:
  `tools/update_translations.sh`
- Compile Qt translation files after regeneration:
  `tools/compile_translations.sh`

`./localPipeline.sh --noRun` is the canonical check before every commit.

## Commit messages

Use Conventional Commits format for every commit subject:

```text
<type>(<scope>): <short summary>
```

Common types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.

Include a body that explains why the change was made, what problem it solves,
and any non-obvious decisions. Reference the improvement or bug number when
applicable.

## Versioning

`my_lastfm_player/version.py` is the single source of truth for `__version__`.
`pyproject.toml` reads it through `attr =`.

Bump `my_lastfm_player/version.py` with every commit that changes user-facing
behaviour:

- `PATCH` for bug fixes and small improvements
- `MINOR` for new features
- `MAJOR` for breaking changes

Update `README.md` (`Current version: `x.y.z``) in the same commit. Update the
version assertion in `tests/test_app_smoke.py` in the same commit.

Built packages can include a generated `_build_info.py` commit suffix. Source
tree runs intentionally show only the base version when that generated file is
absent.

## Pipeline

Run `./localPipeline.sh --noRun` before every commit and ensure all mandatory
stages pass. A red pipeline means no commit.

Stages that must be green: Ruff lint, docs check, Sphinx, tests, and coverage.
The configured coverage gate is the source of truth for the required minimum.

## Architecture notes

This is a PyQt6 desktop app that fetches a user's Last.fm loved tracks, resolves
them to YouTube via `yt-dlp`, downloads MP3s, and plays them locally. The
codebase is organized around a controller-mediated, worker-thread pipeline:
Fetch -> Lookup -> Download -> Playback.

- `main.py`: wires `QApplication`, `TranslationManager`, `MainWindow`, and
  `ApplicationController`.
- `controller.py`: central orchestrator. Owns worker `QThread` lifecycle,
  connects `MainWindow` signals, and chains fetch, lookup, download, and
  playback workflows.
- `workers.py`: `FetchLovedTracksWorker`, `LookupTracksWorker`, and
  `DownloadTracksWorker`. Worker `run()` methods catch exceptions at the thread
  boundary, emit `error`, and always emit `finished`.
- `lastfm.py`: `LastFmLovedTracksScraper` orchestrates pagination. Fetching is
  split into HTTP fetcher, BeautifulSoup parser, and scraper coordination.
- `youtube.py`: shells out to
  `yt-dlp --dump-single-json --no-playlist ytsearch1:<artist title>`.
- `download.py`: runs `yt-dlp --extract-audio --audio-format mp3` with a FIFO
  queue, configurable concurrency, retry/backoff, priority download support, and
  optional per-run limits.
- `playback.py`: wraps `QMediaPlayer`. The Qt backend is lazy-instantiated
  through `ApplicationController.playback_service` so headless tests do not need
  multimedia objects until playback is requested.
- `storage.py`: manages per-user tracks, download cache, lookup cache, and
  Last.fm credentials. New persisted JSON should use `_atomic_write_json`.
- `models.py`: `Track.cache_key` is the project-wide identity for tracks across
  UI rows, persistence, and caches.
- `ui/main_window.py` and `ui/track_table_model.py`: UI shell and table model.
  The window emits semantic signals; the controller performs the work.
- `dependencies.py`: checks external `yt-dlp` and `ffmpeg` availability.
- `i18n.py`: `TranslationManager` and `translate(...)` helpers for live language
  switching.

## Conventions

- Worker boundaries: never let exceptions escape `Worker.run()`. Emit through
  the `error` signal and emit `finished` from `finally`.
- Cache key identity: when locating a track inside lists, persisted data, or
  caches, match by `cache_key`, not by `(artist, title)` tuples or row index.
- Atomic writes: do not write user-facing JSON files in place. Use repository
  helpers that call `_atomic_write_json`.
- Translatable strings: user-visible strings in `controller.py`, `workers.py`,
  and `ui/*` should use `translate(...)` or Qt translation APIs. After changing
  them, run `tools/update_translations.sh` and `tools/compile_translations.sh`
  and include updated `.ts`/`.qm` files.
- Qt tests: use the `qapp` fixture for Qt-touching tests so the suite remains
  headless.
- New modules: add public modules to `docs/api.rst`.
- Improvement tracking: when completing an item from `documents/05_IMPROVEMENTS.md`,
  mark it as `fixed:`.

## Documentation

`tools/check_docs.py` enforces required documentation files and Markdown hygiene.
Every Markdown file must have a top-level `# ` heading, avoid trailing
whitespace, and end with a newline.

## Quality checklist

1. `./localPipeline.sh --noRun` passes.
2. New modules are added to `docs/api.rst`.
3. Version is bumped in `version.py`, `README.md`, and smoke tests when required.
4. Translations are regenerated and compiled when user-visible strings changed.
5. Relevant improvement or bug entries are marked `fixed:` when applicable.

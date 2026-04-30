# Improvements

This document collects follow-up improvements noticed during implementation. These are not blockers for the current development-plan step, but they should be revisited before the MVP is considered finished.

## Workflow
* fixed: 0. fetching loved tracks updates the table after each paginated Last.fm page and reports progress in the status bar.
* fixed: 1. the application window title reports the current version as a suffix.
* fixed: 2. lookup and download workflows update the table row by row as each track changes state.
* 5. make it possible to pause and also to stop the fetching projects. of the tracks. like add a pause and a stop button. with tooltips to the ui. near the fetch button. should be self explainining,. while no fetch is runing, those are disabled. when fetch is active then make the enabled too. when pressing pause, the user can resume. when pressing stop, the whole fetching is topped. tie this to the backend. and prepare unit.testing for that too.


## Documentation
* fixed: 3. Sphinx is configured for Python API documentation and runs in the local pipeline with warnings treated as errors.
* fixed: 4. public classes, functions, and methods have Sphinx-readable API documentation, and the Sphinx run is warning-free.

## UI design
* switch to use qml isntead of a widget based app? benefits
* themes, color schemes? dakr light mode at least
* i18n for the project?

## Packaging and Versioning

- Python package metadata normalizes two-digit versions such as `00.00.20` to `0.0.20` for built wheel filenames. The app-facing version keeps the requested two-digit format, but release tooling should make this distinction explicit.
- The documented rule says every future commit should increase the patch number. This is easy to forget manually; a small pre-commit or release helper could enforce it.

## Pipeline

- `localPipeline.sh` installs dependencies on every run. This is simple and reliable, but it will become slow as dependencies grow. A future pipeline could skip reinstalling when `pyproject.toml` has not changed.
- The project still uses dependency ranges instead of a lock file. A lock or constraints file would make CI and local builds more reproducible.

## Architecture

- The controller now owns the fetch workflow, but worker lifecycle management is still minimal. Later steps should add cancellation and clearer shutdown behavior before long downloads are introduced.
- Lookup and download now start automatically after a successful fetch. A future UI pass should decide whether advanced users still need separate manual lookup/download actions for recovery and debugging.
- Automatic workflow chaining currently lives in the controller. If the workflow grows, a dedicated workflow coordinator object would make sequencing and failure handling easier to test.
- Priority playback preparation can run while the normal lookup workflow is active. The storage merge protects downloaded state, but a dedicated job queue would make this behavior easier to reason about.

## YouTube Lookup

- `yt-dlp` returns package-normalized errors and search result shapes that may vary by version. The resolver handles common shapes, but live integration testing should be added once network-dependent checks are acceptable.
- YouTube lookup is currently sequential and simple, which matches the MVP rule. Later queue integration should avoid blocking all downloads behind slow or failing lookups.
- Storage returns domain objects directly. That is fine for the JSON MVP, but the storage abstraction should remain narrow so a future SQLite migration does not leak database concerns upward.

## Scraping

- Last.fm scraping depends on public HTML structure. Fixture tests protect the parser shape we support, but Step 4 and later should keep parsing errors visible in the UI so site changes are diagnosable.
- Loved-track total counts are parsed from common Last.fm page text patterns. If Last.fm changes the copy or hides the count, the UI still reports cumulative fetched tracks but cannot show `fetched/total`.

## Logging

- Logging currently writes to stdout for pipeline visibility. A future desktop-friendly setup should add a rotating log file in the app data directory and expose its path in the UI.

## Downloads

- The download manager captures coarse queue progress only. A later pass should parse `yt-dlp` progress hooks or subprocess output so the UI can show per-track byte/percent progress.
- The queue has pause/resume primitives in the manager, but the UI currently exposes a start-download action. A follow-up should add a true pause/resume toggle once long-running download cancellation semantics are settled.
- Download concurrency is handled at the queue level. If `yt-dlp` itself starts parallel fragment downloads, we may need to cap or document that separately.

## Playback

- Playback uses `QMediaPlayer`, which keeps the app inside PyQt but means codec support depends on the user's Qt multimedia backend. A future startup check could verify MP3 playback support and show a clear warning.
- Playback status currently persists the selected track as `Playing` while active and restores it to `Downloaded` when stopped. If the app exits during playback, startup should normalize any stale `Playing` rows back to `Downloaded`.
- The controller saves visible table tracks after playback state changes. A future storage abstraction should provide a narrower single-track update API to avoid rewriting large user files for a single status change.

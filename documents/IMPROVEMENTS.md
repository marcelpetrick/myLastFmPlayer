# Improvements

This document collects follow-up improvements noticed during implementation. These are not blockers for the current development-plan step, but they should be revisited before the MVP is considered finished.

## Packaging and Versioning

- Python package metadata normalizes two-digit versions such as `00.00.13` to `0.0.13` for built wheel filenames. The app-facing version keeps the requested two-digit format, but release tooling should make this distinction explicit.
- The documented rule says every future commit should increase the patch number. This is easy to forget manually; a small pre-commit or release helper could enforce it.

## Pipeline

- `localPipeline.sh` installs dependencies on every run. This is simple and reliable, but it will become slow as dependencies grow. A future pipeline could skip reinstalling when `pyproject.toml` has not changed.
- The project still uses dependency ranges instead of a lock file. A lock or constraints file would make CI and local builds more reproducible.

## Architecture

- The controller now owns the fetch workflow, but worker lifecycle management is still minimal. Later steps should add cancellation and clearer shutdown behavior before long downloads are introduced.
- The lookup worker exists, but it is not exposed through a dedicated UI control yet. Step 8 or the controller integration pass should decide whether lookup starts automatically after fetching or through an explicit command.
- A placeholder worker still exists for the future download phase. Step 8 should replace it with a real queue manager or remove it if a different worker split is better.

## YouTube Lookup

- `yt-dlp` returns package-normalized errors and search result shapes that may vary by version. The resolver handles common shapes, but live integration testing should be added once network-dependent checks are acceptable.
- YouTube lookup is currently sequential and simple, which matches the MVP rule. Later queue integration should avoid blocking all downloads behind slow or failing lookups.
- Storage returns domain objects directly. That is fine for the JSON MVP, but the storage abstraction should remain narrow so a future SQLite migration does not leak database concerns upward.

## Scraping

- Last.fm scraping depends on public HTML structure. Fixture tests protect the parser shape we support, but Step 4 and later should keep parsing errors visible in the UI so site changes are diagnosable.
- Loved-track total counts are parsed from common Last.fm page text patterns. If Last.fm changes the copy or hides the count, the UI still reports cumulative fetched tracks but cannot show `fetched/total`.

## Logging

- Logging currently writes to stderr. A future desktop-friendly setup should add a rotating log file in the app data directory and expose its path in the UI.

# Improvements

This document collects follow-up improvements noticed during implementation. These are not blockers for the current development-plan step, but they should be revisited before the MVP is considered finished.

## Packaging and Versioning

- Python package metadata normalizes `00.00.06` to `0.0.6` for built wheel filenames. The app-facing version keeps the requested two-digit format, but release tooling should make this distinction explicit.
- The documented rule says every future commit should increase the patch number. This is easy to forget manually; a small pre-commit or release helper could enforce it.

## Pipeline

- `localPipeline.sh` installs dependencies on every run. This is simple and reliable, but it will become slow as dependencies grow. A future pipeline could skip reinstalling when `pyproject.toml` has not changed.
- The project still uses dependency ranges instead of a lock file. A lock or constraints file would make CI and local builds more reproducible.

## Architecture

- The controller now owns the fetch workflow, but worker lifecycle management is still minimal. Later steps should add cancellation and clearer shutdown behavior before long downloads are introduced.
- Placeholder workers exist for the future lookup/download phases. Step 7 and Step 8 should replace those placeholders with real implementations or remove them if a different worker split is better.
- Storage returns domain objects directly. That is fine for the JSON MVP, but the storage abstraction should remain narrow so a future SQLite migration does not leak database concerns upward.

## Scraping

- Last.fm scraping depends on public HTML structure. Fixture tests protect the parser shape we support, but Step 4 and later should keep parsing errors visible in the UI so site changes are diagnosable.

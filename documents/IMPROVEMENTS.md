# Improvements

This document collects follow-up improvements noticed during implementation. These are not blockers for the current development-plan step, but they should be revisited before the MVP is considered finished.

## Packaging and Versioning

- Python package metadata normalizes `00.00.04` to `0.0.4` for built wheel filenames. The app-facing version keeps the requested two-digit format, but release tooling should make this distinction explicit.
- The documented rule says every future commit should increase the patch number. This is easy to forget manually; a small pre-commit or release helper could enforce it.

## Pipeline

- `localPipeline.sh` installs dependencies on every run. This is simple and reliable, but it will become slow as dependencies grow. A future pipeline could skip reinstalling when `pyproject.toml` has not changed.
- The project still uses dependency ranges instead of a lock file. A lock or constraints file would make CI and local builds more reproducible.

## Architecture

- The UI currently uses `QTableWidget`, which is acceptable for the shell but awkward for large track lists. Step 5 should replace this with a proper table model before the app handles thousands of rows.
- Storage returns domain objects directly. That is fine for the JSON MVP, but the storage abstraction should remain narrow so a future SQLite migration does not leak database concerns upward.

## Scraping

- Last.fm scraping depends on public HTML structure. Fixture tests protect the parser shape we support, but Step 4 and later should keep parsing errors visible in the UI so site changes are diagnosable.

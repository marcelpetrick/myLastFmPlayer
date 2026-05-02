# Improvements

This document collects follow-up improvements noticed during implementation. These are not blockers for the current development-plan step, but they should be revisited before the MVP is considered finished.

## Workflow
* fixed: 0. fetching loved tracks updates the table after each paginated Last.fm page and reports progress in the status bar.
* fixed: 1. the application window title reports the current version as a suffix.
* fixed: 2. lookup and download workflows update the table row by row as each track changes state.
* fixed: 5. Last.fm fetching has pause/resume and stop controls beside the fetch button, with backend cancellation support and unit coverage.
* fixed: 6. local pipeline HTML report opening now prefers `MY_LASTFM_PLAYER_REPORT_BROWSER`, then Firefox, then `xdg-open`, then `open`, and reports which opener accepted each file.
* fixed: 7. `localPipeline.sh` now starts the installed app once unless `--noRun` is provided and does not reopen it after the user quits.
* fixed: 11. built packages show the first six digits of the build-time git commit hash as a user-facing version suffix.
* fixed: 12. `my_lastfm_player/version.py` is the single source of truth for the base version; package metadata and documentation checks read that value.
* fixed: 13. playback now has a seekable timeline slider with current and total time labels; clicking the timeline jumps immediately to that position.
* 14. scrobble the songs back to last fm: first auth to last.fm, then scrobble the song - how does this even work?
* 15. playlist feature? like drag and drop for the songs? and then those are played one after each other?
* fixed: 16. double-clicking a song in the track list now starts the same playback flow as the Play button.

## Documentation
* fixed: 3. Sphinx is configured for Python API documentation and runs in the local pipeline with warnings treated as errors.
* fixed: 4. public classes, functions, and methods have Sphinx-readable API documentation, and the Sphinx run is warning-free.

## UI design
* 8. switch to use qml isntead of a widget based app? benefits
* 9. themes, color schemes? dark light mode at least
* fixed: 10. the app has Qt translation support, translation file generation commands, and a live language-selection menu.

## Packaging and Versioning

- fixed: 16. versioning now uses unpadded `0.0.x` values directly, so package metadata, wheel filenames, and app-facing base versions match.
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

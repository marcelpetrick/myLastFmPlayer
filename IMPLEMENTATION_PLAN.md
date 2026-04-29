# Implementation Plan

This plan turns `documents/REQUIREMENTS.md` into a ten-step implementation sequence for the Linux PyQt MVP. The repository currently has no application code, so the first steps establish a maintainable Python project before adding Last.fm scraping, storage, download orchestration, playback, and UI behavior.

## 1. Create the Python Project Skeleton

Set up a conventional Python package for the desktop app.

Deliverables:

- `pyproject.toml` with runtime dependencies and developer tooling.
- Application package, for example `my_lastfm_player/`.
- Entry point such as `python -m my_lastfm_player` or a console script.
- Initial module layout:
  - `app.py` or `main.py`
  - `models.py`
  - `storage.py`
  - `lastfm.py`
  - `youtube.py`
  - `download.py`
  - `playback.py`
  - `controller.py`
  - `ui/`
- Basic test directory.

Validation:

- The application starts and exits cleanly.
- Unit test runner can execute at least one smoke test.

## 2. Define Core Models and Status Lifecycle

Implement the track data model and status values before any service code depends on them.

Deliverables:

- `TrackStatus` enum containing:
  - `Fetched`
  - `Queued`
  - `Searching`
  - `Downloading`
  - `Downloaded`
  - `Playing`
  - `Failed`
  - `Not found`
- `Track` model with:
  - artist
  - title
  - Last.fm URL
  - YouTube URL
  - local file path
  - status
  - retry count
  - error
- Stable cache key helper based on exact `artist + title`.
- Filename helper for `<Artist> - <Title>.mp3` with filesystem-safe sanitization.

Validation:

- Unit tests cover serialization, deserialization, cache keys, and filename generation.

## 3. Implement JSON Storage and Shared Cache Lookup

Build the MVP storage layer behind a small abstraction so SQLite can replace it later.

Deliverables:

- JSON repository for per-user track lists.
- Shared downloaded-track cache using exact artist/title matching.
- Atomic writes to avoid corrupting JSON on crash.
- Manual data deletion support by keeping data in predictable user-owned files.
- Configurable data and download directories, defaulting to a Linux user data location.

Validation:

- Tracks persist and reload without losing optional fields.
- Existing downloaded tracks are detected and marked as available without re-downloading.
- Corrupt or missing JSON files produce clear errors and do not crash the UI layer.

## 4. Build Last.fm Loved Tracks Scraper

Implement public HTML scraping with pagination and no API credentials.

Deliverables:

- Loved-track fetcher for a Last.fm username.
- Pagination traversal until no additional loved-track page exists.
- Extraction of artist, title, and track URL when present.
- Network timeout handling.
- Parser failure reporting with enough context for debugging.

Validation:

- Unit tests use saved HTML fixtures for single-page and multi-page results.
- Service returns a list of `Track` objects in page/list order.
- Empty or inaccessible profiles produce a user-displayable error.

## 5. Create the PyQt Main Window and Track Table

Implement the initial UI shell and connect it to storage-backed data.

Deliverables:

- Main window with:
  - Last.fm username input.
  - Sortable table with Artist, Title, and Status columns.
  - Row selection support.
  - Play, Pause, Stop buttons.
  - Pause/Resume Downloads button.
  - Download concurrency control.
- Status/error/progress display area.
- Table model that can handle at least 1000 tracks without blocking.

Validation:

- UI can load saved tracks for a username.
- Sorting and selection work.
- Large in-memory track lists remain responsive.

## 6. Add Controller and Background Worker Boundaries

Wire UI actions to services while keeping all blocking work off the UI thread.

Deliverables:

- Controller layer that owns user workflows.
- QThread or worker-based execution for:
  - Last.fm fetching.
  - YouTube lookup.
  - Downloads.
- Signal/slot updates for track status, progress, and errors.
- Startup dependency check for `yt-dlp` and `ffmpeg`.

Validation:

- Entering a username starts fetching without freezing the UI.
- Missing external dependencies are reported clearly.
- Worker failures update track status instead of crashing the app.

## 7. Implement YouTube Resolver

Resolve tracks to YouTube using exact Last.fm strings and first-result-only MVP behavior.

Deliverables:

- Query builder using `<artist> <title>`.
- Resolver powered by `yt-dlp` search or another no-credential approach.
- First-result selection only.
- `Not found` status when no result exists.
- Error propagation for network/tool failures.

Validation:

- Unit tests mock resolver output for found, not found, and failure cases.
- Resolved tracks store YouTube URL in JSON.
- UI shows `Searching`, `Queued`, `Not found`, or error states correctly.

## 8. Implement Download Manager with Queueing, Retry, and Backoff

Download MP3 files automatically after fetch/lookup while respecting MVP queue rules.

Deliverables:

- FIFO download queue.
- Default concurrency of 2 with user-configurable limit.
- Pause/resume downloads.
- Random 1-5 second delay between downloads.
- Up to 3 attempts per track.
- `Failed` state after max retries.
- Skip logic for tracks already downloaded locally.
- Selected-track priority insertion.
- Progress updates from `yt-dlp` where available.

Validation:

- Queue obeys concurrency limits.
- Pausing stops new work from starting while active downloads finish or pause according to implementation limits.
- Retry count and error fields persist.
- Existing MP3 files are skipped.

## 9. Implement Local Playback

Provide one-track-at-a-time playback with Play, Pause, and Stop controls.

Deliverables:

- Playback service using a PyQt-compatible audio backend.
- Play selected downloaded track.
- Pause and stop current playback.
- Starting another track stops the previous one.
- Status transition to `Playing` while preserving download state where needed.

Validation:

- Only one track plays at a time.
- Selecting another track stops prior playback.
- Missing local files produce a clear UI error.

## 10. Integrate End-to-End, Package, and Harden

Complete MVP behavior, documentation, and acceptance testing.

Deliverables:

- End-to-end flow:
  - username input
  - Last.fm fetch
  - JSON persistence
  - YouTube lookup
  - MP3 download
  - local playback
- README with Linux setup, Manjaro dependency command, and run instructions.
- Basic logging for service errors and external tool output.
- Acceptance test checklist based on the SRS.
- Minimal packaging path for Linux development use.

Validation:

- User enters a Last.fm username and tracks appear.
- Downloads start automatically in list order.
- Already downloaded tracks are skipped.
- Tracks can be played locally.
- Download queue respects concurrency and backoff.
- UI remains responsive with at least 1000 tracks.

## Suggested Build Order

Implement steps 1-4 first with unit tests, because these create the data foundation and scraper behavior. Then build steps 5-6 to make the app usable and responsive. Finish with steps 7-9 for resolver, downloads, and playback, then use step 10 to close gaps against the acceptance criteria.

## Key Risks to Track During Implementation

- Last.fm HTML can change, so scraper tests should use fixtures and parsing code should fail clearly.
- YouTube search results can vary, so resolver behavior must be deterministic within the first-result-only MVP rule.
- `yt-dlp` and `ffmpeg` are external dependencies, so startup checks and download error handling are required early.
- Downloaded audio may raise legal or terms-of-service concerns depending on user behavior and jurisdiction; the app should avoid implying that all downloads are permitted.

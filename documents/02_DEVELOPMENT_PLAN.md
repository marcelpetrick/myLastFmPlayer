# MVP Development Plan

This is a short execution plan for building the MVP described in `documents/REQUIREMENTS.md`. The steps are numbered `0` through `10` so the setup and quality pipeline are established before feature work begins.

## Step 0: Basic PyQt App Setup

Create the initial Python/PyQt application shell.

- Add `pyproject.toml` with Python package metadata and PyQt dependency.
- Create the application package and entry point.
- Add a main window with a username input, empty track table, and placeholder controls.
- Verify the app starts without blocking or crashing.

## Step 1: Testing, Pipeline, Linting, and Documentation Checks

Add the local engineering workflow before feature implementation grows.

- Add a unit-testing framework such as `pytest`.
- Add coverage reporting with a minimum threshold that can rise over time.
- Add a linter/formatter step, for example `ruff`.
- Add a documentation check for Markdown and required project docs.
- Add `localPipeline.sh` that runs all build, lint, documentation, test, coverage, and deploy/package checks in sequence.
- Document how to run the pipeline locally.

## Step 2: Track Model and Status Lifecycle

Implement the core data model used by every feature.

- Add the `Track` entity.
- Add status values: `Fetched`, `Queued`, `Searching`, `Downloading`, `Downloaded`, `Playing`, `Failed`, and `Not found`.
- Add helpers for exact artist/title cache keys and safe MP3 filenames.
- Unit-test serialization and status transitions.

## Step 3: JSON Storage and Shared Cache

Persist user track data and downloaded-track metadata.

- Store per-user track lists in JSON.
- Save artist, title, Last.fm URL, YouTube URL, local path, status, retry count, and error.
- Detect already downloaded tracks by exact artist/title match.
- Use atomic writes so JSON files are not easily corrupted.

## Step 4: Last.fm Loved Tracks Scraper

Fetch loved tracks from public Last.fm pages.

- Scrape loved tracks without API credentials.
- Handle pagination.
- Extract artist, title, and Last.fm track URL.
- Store fetched tracks immediately.
- Add fixture-based parser tests.

## Step 5: Responsive UI Data Binding

Connect stored and fetched data to the PyQt interface.

- Populate the table with Artist, Title, and Status columns.
- Support sorting and row selection.
- Show current status, errors, and download progress.
- Ensure large lists stay responsive.

## Step 6: Background Worker and Controller Layer

Move blocking operations out of the UI thread.

- Add a controller for the main workflow.
- Run scraping, YouTube lookup, and downloads in worker threads.
- Use Qt signals for progress, status, and error updates.
- Check `yt-dlp` and `ffmpeg` on startup and report missing dependencies.

## Step 7: YouTube Lookup

Resolve fetched tracks to YouTube URLs.

- Build queries from exact Last.fm artist and title strings.
- Use first search result only for the MVP.
- Mark tracks as `Not found` when no result exists.
- Persist resolved YouTube URLs.

## Step 8: Download Queue

Download resolved tracks as MP3 files.

- Start downloads automatically after fetch and lookup.
- Process tracks FIFO with default concurrency of 2.
- Allow user-configurable concurrency.
- Add pause/resume downloads.
- Apply random 1-5 second backoff and up to 3 retries.
- Skip files already present in the shared cache.

## Step 9: Playback

Add local playback controls.

- Play selected downloaded tracks.
- Support pause and stop.
- Ensure only one track plays at a time.
- Stop current playback when switching tracks.
- Show playback errors for missing or invalid files.

## Step 10: MVP Integration and Release Check

Finish the end-to-end MVP and confirm acceptance criteria.

- Test the complete flow from username input to playback.
- Confirm downloads respect queue order, concurrency, backoff, retries, and cache skips.
- Update README with Linux setup, Manjaro dependency install command, and run instructions.
- Run `localPipeline.sh` cleanly.
- Prepare a basic Linux development package or runnable command.

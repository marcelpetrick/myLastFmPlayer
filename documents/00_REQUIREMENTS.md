# Software Requirements Specification

This is the current product requirements baseline for `myLastFmPlayer` 0.0.168.
It describes the implemented and vetted application rather than an unfinished MVP.
Runtime design details are in [`03_ARCHITECTURE.md`](03_ARCHITECTURE.md).

## 1. Purpose and Scope

The product shall provide a Linux desktop workflow that turns a Last.fm user's
public loved-track history into a persistent, playable local library:

1. discover loved tracks through Last.fm;
2. resolve playable sources through YouTube;
3. download audio locally;
4. browse, filter, sort, and play the library;
5. optionally report now-playing and scrobble playback to Last.fm.

The supported runtime is Linux x86_64 with Python 3.14 or newer and PyQt6.
`yt-dlp`, `ffmpeg`, and `ffprobe` are required external commands.

## 2. Functional Requirements

### 2.1 User and Last.fm Discovery

- The user shall be able to enter and fetch any public Last.fm username without
  authenticating a personal Last.fm account.
- The application shall fetch every available `user.getLovedTracks` page and retain
  artist, title, track URL, and loved-at time when supplied by Last.fm.
- Partial pages shall appear in the table as they arrive instead of waiting for the
  complete library.
- The UI shall expose fetch progress, Pause/Resume Fetch, and Stop Fetch.
- Network and parsing failures shall produce visible, actionable feedback.
- Per-user cached libraries shall be loadable and refreshable.

### 2.2 Independent Pipeline Processing

- YouTube lookup shall begin automatically for eligible tracks and may overlap later
  Last.fm pages.
- Download shall begin automatically as soon as a resolved track is eligible and may
  overlap lookup.
- Every track shall be processed independently; a miss or failure shall not abort the
  remaining queue.
- One shared parallel-work limit shall cover lookup and download together.
- The limit shall default to five and be configurable in Preferences from one to five.
- A selected unavailable track shall be prioritized for lookup and download when the
  user requests playback.

### 2.3 YouTube Lookup

- The application shall use `yt-dlp` search and consult a shared lookup cache first.
- Lookup shall use a bounded query ladder that includes exact artist/title, a cleaned
  artist/title variation, and title alone.
- A resolved entry shall store its YouTube URL and become `Queued`.
- Transient lookup errors shall become `Lookup failed`; exhausted empty-result attempts
  shall become `Not found`.
- Failed and not-found entries shall remain eligible for bounded recovery rather than
  becoming permanently stuck.

### 2.4 Downloading

- The application shall request the best available audio through `yt-dlp` without
  artificially increasing its quality.
- Output names shall be safe file-system forms of `<Artist> - <Title>`.
- Successful downloads shall record the local path, detected media type, and bitrate
  when `ffprobe` supplies it.
- Existing files in the shared download cache shall not be downloaded again.
- A bounded retry ladder shall handle changing YouTube client behavior, with jittered
  backoff between attempts.
- Exhausted downloads shall become `Failed` without stopping peer downloads.

### 2.5 Cancellation, Resume, and User Switching

- The main window shall expose one Stop YouTube action for active lookup and download.
- Cancellation shall stop queued work, wake capacity waiters, and terminate owned
  external processes promptly.
- Completed results shall remain saved after cancellation.
- The UI shall show a stopping state until owned workers finish, then offer Resume
  YouTube when unresolved or queued entries remain.
- Resume shall process only eligible remaining work.
- The username field shall remain editable during fetch, lookup, and download.
- Changing the username shall cancel the previous user's active workflow and isolate
  the new table from late callbacks belonging to the old username or generation.

### 2.6 Library and Playback

- The main table shall show artist, title, status, file information, and loved-at time.
- The table shall support selection, sorting, filtering, tooltips for truncated text,
  and status-aware display.
- Local playback shall support Play, Pause, Stop, seek, volume, mute, and next-track.
- Timeline seeking shall support groove clicks, handle dragging, arrow and page keys,
  and Home/End without playback updates overriding an active drag.
- The application shall optionally continue with a random downloaded track.
- Only one local track shall play at a time.
- An artist preview shall load in the background for the selected or playing track.
- The artwork and playback controls shall remain compact and shall not reduce the
  track table's height when an image is loaded.
- Clicking available artwork shall open the artist's Last.fm page in a private Firefox
  window.

### 2.7 Scrobbling

- Scrobbling shall be optional and disabled until the user chooses it.
- Desktop authentication shall open Last.fm in a browser and persist the resulting
  user session.
- Playback shall send now-playing information and scrobble only after the configured
  listening threshold is reached.
- Public library discovery shall continue to work without scrobbling authentication.

### 2.8 Preferences and Localization

- Preferences shall include theme, language, YouTube cookie browser, parallel-work
  limit, scrobbling, playback behavior, and data-retention controls.
- The UI shall provide Light, Dark, Lilac, and Mint themes.
- English shall be the source language, with complete Croatian, German, Mandarin, and
  Ukrainian translations.
- Username, window geometry, volume, mute, and other user preferences shall survive
  restart.

## 3. Data and State Requirements

### 3.1 Track Model

Each persistent track shall support:

```json
{
  "artist": "string",
  "title": "string",
  "lastfm_url": "string|null",
  "loved_at": "string|null",
  "youtube_url": "string|null",
  "local_path": "string|null",
  "status": "enum",
  "retry_count": "integer",
  "error": "string|null",
  "file_type": "string|null",
  "bitrate_kbps": "integer|null"
}
```

Durable statuses shall be `Fetched`, `Searching`, `Lookup failed`, `Queued`,
`Downloading`, `Downloaded`, `Failed`, and `Not found`. Playback state is runtime
state and shall not destroy the durable downloaded state.

### 3.2 Persistence

- Track snapshots shall be stored per sanitized username.
- Lookup and download caches shall be shared across users by exact artist/title key.
- Per-track results shall be appended durably while work is active and compacted into
  the full snapshot after a completed run.
- Reads and writes shall have a consistent lock boundary.
- Snapshot and cache replacement shall be atomic.
- Metadata and credentials shall be retained on quit by default.
- If the user opts out of retention, track metadata, caches, and credentials shall be
  removed on quit; downloaded audio shall remain untouched.
- Application preferences shall use the platform `QSettings` store.

## 4. Non-Functional Requirements

### 4.1 Responsiveness and Performance

- All network, paginated HTTP fetch, lookup, download, image, and media-probe operations
  shall execute outside the Qt UI thread.
- The UI shall stay responsive with libraries of at least 1,000 entries.
- Incremental results shall be visible without requiring the full pipeline to finish.
- The configured shared limit shall prevent unbounded external process creation.

### 4.2 Reliability

- Active external commands shall have timeouts and cancellation boundaries.
- One track's exception shall not terminate unrelated track processing.
- Late worker results shall not cross username or workflow-generation boundaries.
- Completed results shall survive a stop, username change, application restart, or
  crash after the journal flush.
- Missing dependencies and service errors shall be reported to the user.

### 4.3 Maintainability and Verification

- UI, controller, services, workers, immutable domain model, storage, and settings
  shall remain separately testable.
- Every commit shall pass Ruff, Pylint at 10.00/10, complete translation checks,
  warning-free Sphinx documentation, pytest at the configured 99% coverage threshold,
  package construction, installed-package import, and application launch verification.
- Live Last.fm and `yt-dlp` integration checks shall remain available as opt-in tests.
- Releases shall be reproducible through the manual GitHub Actions release workflow
  and include packages plus test, coverage, documentation, architecture, static
  analysis, and pipeline provenance artifacts.

### 4.4 Security and Privacy

- Shell interpolation shall not be used to execute usernames, track metadata, URLs,
  or file paths.
- User credentials shall not be logged.
- Last.fm desktop credentials may be bundled because they identify the public desktop
  application; a user's authorized session remains local application data.
- The data-retention preference shall state exactly which metadata is removed and that
  downloaded audio is retained.

## 5. Acceptance Criteria

The product is acceptable when all of the following are true:

- entering a valid username shows partial and then complete loved-track results;
- lookup and download overlap while respecting the shared one-to-five limit;
- individual misses and failures leave other entries progressing;
- Stop YouTube ends owned work cleanly and Resume continues eligible entries;
- entering another username during active work leaves the field usable, cancels the
  old workflow, and prevents stale UI updates;
- downloaded tracks play with the documented controls and optional scrobbling;
- saved libraries and completed work survive restart by default;
- all deterministic local and CI quality gates pass; and
- the installable wheel starts successfully in an isolated environment.

## 6. Product Evolution

The core product workflow is complete and vetted. Future changes are maintenance,
compatibility work, usability improvements, or scoped extensions such as playlist
management, richer ranking, metadata tagging, export, alternative persistence, and
additional platforms. These are opportunities, not missing acceptance criteria for
the current product.

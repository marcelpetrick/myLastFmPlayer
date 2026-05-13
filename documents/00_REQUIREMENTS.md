Below is a **complete, consistent, and implementation-ready Software Requirements Specification (SRS)** incorporating all decisions made.

---

# Software Requirements Specification (SRS)

## 1. Overview

### 1.1 Purpose

This document specifies the requirements for a Linux desktop application that retrieves a user’s loved tracks from Last.fm, resolves corresponding audio tracks from YouTube, downloads them locally, and provides playback functionality.

### 1.2 Scope

The system is a standalone desktop application built with:

* **Language:** Python
* **GUI Framework:** PyQt
* **Target Platform:** Linux (x86_64)

The application will:

1. Fetch loved tracks from Last.fm (via web scraping)
2. Store metadata locally in JSON
3. Resolve corresponding YouTube tracks
4. Download audio (MP3)
5. Provide playback and UI interaction

---

## 2. System Context

### 2.1 External Systems

* Last.fm (public loved-track HTML scraping plus authenticated scrobbling API calls)
* YouTube (search + download via tools such as yt-dlp)

### 2.2 External Tools

* **yt-dlp** (YouTube extraction)
* **ffmpeg** (audio conversion)

### 2.3 Constraints

* Public loved-track fetching must not require a user-supplied API key.
* Scrobbling may use bundled Last.fm desktop application credentials and a user-authorized session key.
* Dependence on public HTML structure
* Linux-only target for MVP

---

## 3. Functional Requirements

### 3.1 User Input

* The system shall allow entry of a Last.fm username via the UI
* Upon input, the system shall immediately start fetching loved tracks

---

### 3.2 Last.fm Scraping

* The system shall retrieve loved tracks via public web pages

* The system shall:

  * Handle pagination
  * Extract:

    * Artist name
    * Track title
    * Last.fm track URL (if available)

* The system shall store retrieved tracks locally in JSON

---

### 3.3 Data Storage (MVP)

* Storage format: **JSON file**

* The system shall persist:

  * Artist
  * Title
  * Last.fm URL
  * YouTube URL (if found)
  * Local file path
  * Status
  * Retry count (optional)
  * Error information (optional)

* The system shall:

  * Allow deletion of JSON data by the user (manual)
  * Not manage deletion of downloaded audio files

---

### 3.4 Track Lifecycle & Status

Each track shall move through the following states:

* `Fetched`
* `Queued`
* `Searching`
* `Downloading`
* `Downloaded`
* `Playing`
* `Failed`
* `Not found`

---

### 3.5 YouTube Lookup

* The system shall construct search queries using:

  ```
  <artist> + <title>
  ```

* The system shall:

  * Use exact strings from Last.fm (no normalization or fuzzy matching)
  * Select the **first search result only**
  * Not implement ranking or scoring in MVP

* If no result is found:

  * The track shall be marked as `Not found`
  * The user shall be informed via UI

---

### 3.6 Downloading

* The system shall:

  * Use yt-dlp for downloading
  * Use ffmpeg for audio extraction/conversion

* Output:

  * Format: **MP3**
  * Quality: best available (no artificial upscaling)

* File naming:

  ```
  <Artist> - <Title>.mp3
  ```

---

### 3.7 Download Behavior

* Downloads shall:

  * Start automatically after fetching tracks
  * Proceed in list order (FIFO)

* Concurrency:

  * Default: **2 parallel downloads**
  * User-configurable in Preferences, minimum **1**, maximum **10**

* Backoff:

  * Random delay between downloads: **1–5 seconds**

* Retry:

  * Up to **3 attempts per track**
  * After max retries → mark as `Failed`

---

### 3.8 Preloading & Priority

* The system shall preload tracks sequentially
* When a user selects a track:

  * It shall be prioritized for lookup/download

---

### 3.9 Duplicate Detection & Caching

* The system shall:

  * Avoid re-downloading tracks that already exist locally

* Matching rule (MVP):

  * Exact match of:

    ```
    Artist + Title
    ```
  * No normalization, no fuzzy matching

* Cache shall be shared across users

---

### 3.10 Multi-User Support

* The system shall:

  * Allow entering different Last.fm usernames
  * Load tracks per username dynamically

* The system shall:

  * Not implement profile management (MVP)
  * Reuse cached/downloaded tracks across users

---

### 3.11 Playback

* The system shall provide:

  * Play
  * Pause
  * Stop

* Behavior:

  * Only one track may play at a time
  * Playing a new track stops the current one
  * Switching tracks stops previous playback

---

### 3.12 UI Requirements

#### Main Table

* Columns:

  * Artist
  * Title
  * Status

* Features:

  * Sortable columns
  * Selection support

---

#### Controls

* Input field for Last.fm username
* Play / Pause / Stop buttons
* Global **Pause/Resume Downloads** button

---

#### Feedback

* Display:

  * Current status per track
  * Download progress
  * Errors

---

### 3.13 Dependency Check

* On startup, the system shall verify:

  * `yt-dlp` is installed
  * `ffmpeg` is installed

* If missing:

  * The system shall notify the user

#### Manjaro Installation

```bash
sudo pacman -S yt-dlp ffmpeg
```

---

## 4. Non-Functional Requirements

### 4.1 Performance

* UI must remain responsive at all times
* Background operations shall not block UI
* Must handle large track lists (≥ 1000 entries)

---

### 4.2 Reliability

* Handle:

  * Network failures
  * Parsing failures
* Apply retry logic with backoff

---

### 4.3 Maintainability

* Modular architecture:

  * Scraper
  * Storage
  * YouTube resolver
  * Downloader
  * UI

* Storage abstraction must allow future DB migration

---

### 4.4 Portability

* Target platform: Linux x86_64
* Avoid OS-specific dependencies beyond Linux baseline

---

### 4.5 Usability

* No user-provided API keys required for the default app build
* Minimal setup
* Clear UI feedback

---

## 5. Architecture Overview

### 5.1 Components

* UI Layer (PyQt)
* Controller Layer
* Service Layer:

  * Last.fm Scraper
  * YouTube Resolver
  * Download Manager
* Storage Layer (JSON)

---

### 5.2 Concurrency Model

* Use:

  * QThread or async workers
* Ensure:

  * UI thread is never blocked

---

## 6. Data Model

### Track Entity

```json
{
  "artist": "string",
  "title": "string",
  "lastfm_url": "string",
  "youtube_url": "string|null",
  "local_path": "string|null",
  "status": "enum",
  "retry_count": "integer",
  "error": "string|null"
}
```

---

## 7. Risks & Assumptions

### Risks

* Last.fm HTML changes
* YouTube search variability
* External tool availability
* Legal considerations for downloading content

### Assumptions

* Public pages remain accessible
* Users install required dependencies
* Exact matching is sufficient for MVP

---

## 8. Future Enhancements

* SQLite migration
* Fuzzy matching for duplicates
* Improved YouTube selection heuristics
* Metadata tagging (ID3)
* Playlist export
* Cross-platform support

---

## 9. Acceptance Criteria

* User enters Last.fm username → tracks appear
* Tracks automatically begin lookup/download
* Already downloaded tracks are skipped
* Tracks can be played locally
* Only one track plays at a time
* Download queue respects concurrency and backoff
* UI remains responsive under load

---

If you want the next step, I can convert this into:

* a **clean Python project skeleton**, or
* a **task breakdown with implementation order (very useful before coding)**

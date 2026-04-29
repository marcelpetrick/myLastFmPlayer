# Architecture

This document describes the workflow implemented in the application as of version `00.00.15`. It focuses on how a Last.fm username such as `first` is fetched, stored, and shown in the UI.

## Current Scope

Implemented:

- PyQt desktop shell.
- Last.fm loved-track scraping from public HTML pages.
- Background worker boundary for fetching.
- Per-user JSON storage.
- Track table model and UI data binding.
- YouTube lookup service and worker entry point.
- Download queue service and worker entry point.
- Startup checks for `yt-dlp` and `ffmpeg`.
- Status-bar progress and stdout logging.

Not yet implemented:

- Automatic YouTube lookup after fetching.
- Automatic download start after lookup.
- True pause/resume UI for active downloads.
- Playback.
- Full controller workflow from fetch to lookup to download to playback.

## Data Sources

The app currently uses these data sources:

| Source | Used For | Code |
| --- | --- | --- |
| Last.fm public HTML | Fetching loved tracks by username | `LastFmLovedTracksFetcher`, `LastFmLovedTracksParser`, `LastFmLovedTracksScraper` |
| Local JSON files | Persisting per-user track metadata | `JsonTrackRepository` |
| Shared local JSON cache | Remembering downloaded tracks by exact artist/title | `JsonTrackRepository` |
| `yt-dlp` command | YouTube first-result lookup and MP3 download | `YouTubeResolver`, `DownloadManager` |
| `shutil.which` | Startup dependency checks for `yt-dlp` and `ffmpeg` | `check_external_dependencies` |

For a username such as `first`, the Last.fm fetch URL is:

```text
https://www.last.fm/user/first/loved
```

Pagination follows links found in the HTML, for example:

```text
https://www.last.fm/user/first/loved?page=2
```

## High-Level Components

```mermaid
flowchart LR
    User[User] --> UI[MainWindow]
    UI --> Controller[ApplicationController]
    Controller --> FetchWorker[FetchLovedTracksWorker]
    Controller --> DownloadWorker[DownloadTracksWorker]
    FetchWorker --> Scraper[LastFmLovedTracksScraper]
    Scraper --> Fetcher[LastFmLovedTracksFetcher]
    Scraper --> Parser[LastFmLovedTracksParser]
    Fetcher --> LastFm[Last.fm public HTML]
    FetchWorker --> Storage[JsonTrackRepository]
    DownloadWorker --> DownloadManager[DownloadManager]
    DownloadManager --> Ytdlp[yt-dlp]
    DownloadManager --> Storage
    Storage --> Json[(Local JSON files)]
    FetchWorker --> Controller
    Controller --> UI
    UI --> TableModel[TrackTableModel]
```

## Fetch Workflow

When the user enters `first` and clicks `Fetch`, this is the implemented workflow:

```mermaid
sequenceDiagram
    actor User
    participant UI as MainWindow
    participant Controller as ApplicationController
    participant Thread as QThread
    participant Worker as FetchLovedTracksWorker
    participant Scraper as LastFmLovedTracksScraper
    participant Fetcher as LastFmLovedTracksFetcher
    participant Parser as LastFmLovedTracksParser
    participant LastFm as Last.fm public HTML
    participant Storage as JsonTrackRepository
    participant Table as TrackTableModel

    User->>UI: Enter "first" and click Fetch
    UI->>Controller: fetch_requested signal
    Controller->>UI: Disable username/fetch controls
    Controller->>UI: Status "Starting fetch"
    Controller->>Thread: Start worker thread
    Thread->>Worker: run()
    Worker->>UI: Status "Looking up Last.fm user first"
    Worker->>Scraper: fetch_and_store_loved_tracks("first")
    Scraper->>Fetcher: loved_tracks_url("first")
    Fetcher-->>Scraper: /user/first/loved
    Scraper->>Fetcher: fetch_page(page URL)
    Fetcher->>LastFm: GET /user/first/loved
    LastFm-->>Fetcher: HTML document
    Fetcher-->>Scraper: FetchedHtmlPage
    Scraper->>Worker: Progress "Found Last.fm user first"
    Scraper->>Parser: parse(html, page URL)
    Parser-->>Scraper: LovedTracksPage
    Scraper->>Worker: Progress "Fetched N/T tracks" if total is known
    Scraper->>Fetcher: fetch_page(next page) if pagination exists
    Fetcher->>LastFm: GET next page
    LastFm-->>Fetcher: HTML document 2..N
    Fetcher-->>Scraper: FetchedHtmlPage
    Scraper->>Parser: parse(html, page URL)
    Scraper-->>Worker: list[Track]
    Worker->>Storage: save_tracks("first", tracks)
    Storage-->>Worker: JSON written
    Worker->>UI: Status "Fetched X tracks"
    Worker->>Controller: tracks_loaded("first", tracks)
    Controller->>UI: set_tracks(tracks)
    UI->>Table: Replace table data
    Controller->>UI: Status "Fetched and stored X tracks for first."
    Controller->>UI: Re-enable username/fetch controls
```

## Last.fm Parsing

The Last.fm implementation is split into three pieces:

- `LastFmLovedTracksFetcher`: recognizes the user URL and fetches HTML documents.
- `LastFmLovedTracksParser`: parses fetched HTML with BeautifulSoup.
- `LastFmLovedTracksScraper`: orchestrates pagination, progress, and storage-facing results.

The parser extracts tracks from Last.fm HTML table rows.

```mermaid
flowchart TD
    Html[Last.fm HTML page] --> Rows[Find tr.chartlist-row]
    Rows --> Name[Read .chartlist-name a]
    Rows --> Artist[Read .chartlist-artist a]
    Name --> Title[Track title]
    Artist --> ArtistName[Artist name]
    Name --> Url[Last.fm track URL]
    Title --> Track[Track object]
    ArtistName --> Track
    Url --> Track
```

Each parsed `Track` currently stores:

- artist
- title
- Last.fm URL
- YouTube URL, initially `null`
- local file path, initially `null`
- status, initially `Fetched`
- retry count
- error

## Status-Bar Feedback

Fetch progress is sent through the worker to the UI status bar.

```mermaid
flowchart LR
    ScraperProgress[FetchProgress] --> WorkerSignal[worker.progress]
    WorkerSignal --> ControllerConnection[Qt signal connection]
    ControllerConnection --> UIProgress[MainWindow.set_progress]
    UIProgress --> ProgressBar[Progress bar label]
    UIProgress --> StatusBar[Status bar message]
```

Examples of messages:

```text
Looking up Last.fm user first
Found Last.fm user first
Fetched 99/200 tracks
Fetched 200 tracks
Fetched and stored 200 tracks for first.
```

If the total count cannot be parsed from the page, the app still shows cumulative progress:

```text
Fetched 99 tracks
```

Errors follow the same path and are shown in the status bar and feedback log.

## Local Storage Layout

By default, user data is stored below:

```text
~/.local/share/myLastFmPlayer/
```

The important files are:

```mermaid
flowchart TD
    DataDir["~/.local/share/myLastFmPlayer"] --> TracksDir["tracks/"]
    TracksDir --> UserJson["first.json"]
    DataDir --> Cache["download-cache.json"]
    DataDir --> Downloads["downloads/"]
```

For username `first`, the per-user file is:

```text
~/.local/share/myLastFmPlayer/tracks/first.json
```

The JSON contains an array of track records.

## YouTube Lookup Workflow

The YouTube resolver is implemented, but it is not yet automatically started after fetching.

```mermaid
sequenceDiagram
    participant Controller as ApplicationController
    participant Worker as LookupTracksWorker
    participant Storage as JsonTrackRepository
    participant Resolver as YouTubeResolver
    participant Ytdlp as yt-dlp

    Controller->>Worker: resolve_youtube_urls()
    Worker->>Storage: load_tracks(username)
    Storage-->>Worker: tracks
    Worker->>Resolver: resolve_tracks(tracks)
    Resolver->>Ytdlp: yt-dlp --dump-single-json --no-playlist ytsearch1:<artist title>
    Ytdlp-->>Resolver: first result JSON
    Resolver-->>Worker: tracks with youtube_url/status
    Worker->>Storage: save_tracks(username, resolved_tracks)
    Worker->>Controller: tracks_resolved(username, tracks)
```

Current lookup rules:

- Query is exactly `<artist> <title>`.
- First result only.
- Found track becomes `Queued`.
- No result becomes `Not found`.

## Download Queue Workflow

Downloads are implemented as an explicit user action for queued tracks that already have a YouTube URL.

```mermaid
sequenceDiagram
    participant UI as MainWindow
    participant Controller as ApplicationController
    participant Worker as DownloadTracksWorker
    participant Manager as DownloadManager
    participant Storage as JsonTrackRepository
    participant Ytdlp as yt-dlp

    UI->>Controller: download_requested signal
    Controller->>Worker: run in QThread
    Worker->>Manager: download_and_store_tracks(username, repository, concurrency)
    Manager->>Storage: load_tracks(username)
    Manager->>Storage: mark_cached_downloads(tracks)
    Manager->>Ytdlp: yt-dlp --extract-audio --audio-format mp3 <youtube_url>
    Ytdlp-->>Manager: downloaded MP3 or error
    Manager->>Storage: save_tracks(username, updated_tracks)
    Manager->>Storage: save_download_cache(updated_tracks)
    Worker->>Controller: tracks_downloaded(username, tracks)
    Controller->>UI: set_tracks(tracks)
```

Current download rules:

- FIFO queue order by default.
- Default concurrency is `2`, controlled by the UI spin box.
- Tracks already in the shared cache are marked `Downloaded` and skipped.
- Each failing download is retried up to `3` times.
- Retry backoff is random between `1` and `5` seconds.
- A selected-track priority hook exists in the manager, but the UI does not expose it yet.

## Logging

The app configures logging to stdout at startup.

```mermaid
flowchart LR
    Main[main.py] --> Logging[configure_logging]
    Controller[ApplicationController] --> Logs[stdout logs]
    Worker[Workers] --> Logs
    Download[DownloadManager] --> Logs
    Fetcher[LastFmLovedTracksFetcher] --> Logs
    Parser[LastFmLovedTracksParser] --> Logs
    Scraper[LastFmLovedTracksScraper] --> Logs
    UI[MainWindow status updates] --> Logs
```

This makes fetch activity visible in the terminal when running:

```sh
my-lastfm-player
```

## Important Current Limitation

Fetching and displaying the Last.fm loved-track list is implemented, but the app still depends on Last.fm public HTML structure. If Last.fm changes class names or pagination markup, the scraper may need selector updates.

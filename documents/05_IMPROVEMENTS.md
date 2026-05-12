# Improvements

This document collects unresolved follow-up improvements noticed during
implementation. These are not blockers for the current development-plan step,
but they should be revisited before the MVP is considered finished.

## Workflow

- 15. Playlist feature: support dragging and dropping songs into a playlist, then play them one after another.
- fixed: 19. Bug with the download state: cached track files are downloaded again when double-clicked. Cached files should only be shown when they exist. Do a file-system check if we have a result; otherwise, download them. Also check whether the queued-download mechanism really triggers downloads for the remaining tracks.
- fixed: bug 22: in general, when the playlist of a user is available, immediately start to download the tracks. Given the download-in-parallel feature, which defaults to two, do not wait for user input. Start from the top. This can happen as soon as the very first track is in the list.
- 21. Bug: after seeking first, pressing Play does not start playback at the selected position.
- bug 22: problem with download; age verification. can this be circumvented - blocked songs?!? by sstting a cookie or something else? this is the runtime error `16:00:23: Track update from hamadryas: Ignite - How Is This Progress is now Searching.
16:00:26: ERROR: [youtube] MWtxIYUc0DI: Sign in to confirm your age. This video may be inappropriate for some users. Use --cookies-from-browser or --cookies for the authentication. See  https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp  for how to manually pass cookies. Also see  https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies  for tips on effectively exporting YouTube cookies
16:00:26: All background work is finished; controls are enabled again.`
- fixed: feature 23: the button "download queued" has to be rename: "start downloads"; when downloading the text switches to "stop downloads". getting tracks which are not locally availalble trigger the download. unless user presses the button for stop. end when everything is downloaded. skip over non available songs.

## UI Design

- 8. Consider switching from the widget-based UI to QML. Reassess whether this still has benefits after the theme work. #lowprio

## Packaging and Versioning

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
- The controller saves visible table tracks after playback state changes. A future storage abstraction should provide a narrower single-track update API to avoid rewriting large user files for a single status change.

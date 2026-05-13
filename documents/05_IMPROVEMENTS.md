# Improvements

This document collects unresolved follow-up improvements noticed during
implementation. These are not blockers for the current development-plan step,
but they should be revisited before the MVP is considered finished.

## Workflow

- 15. Playlist feature: support dragging and dropping songs into a playlist, then play them one after another.
- fixed: 19. Bug with the download state: cached track files are downloaded again when double-clicked. Cached files should only be shown when they exist. Do a file-system check if we have a result; otherwise, download them. Also check whether the queued-download mechanism really triggers downloads for the remaining tracks.
- fixed: bug 22: in general, when the playlist of a user is available, immediately start to download the tracks. Given the download-in-parallel feature, which defaults to two, do not wait for user input. Start from the top. This can happen as soon as the very first track is in the list.
- 21. Bug: after seeking first, pressing Play does not start playback at the selected position.
- fixed: bug 22: problem with download; age verification. Preferences › YouTube Downloads › Browser cookies lets the user select the browser whose YouTube session cookies yt-dlp uses, enabling age-restricted video access.
- fixed: feature 23: the button "download queued" has to be rename: "start downloads"; when downloading the text switches to "stop downloads". getting tracks which are not locally availalble trigger the download. unless user presses the button for stop. end when everything is downloaded. skip over non available songs.
- change request 24: track titles which are longer than the space inside one cell of th table shal be truncated (at the end). not wrapped onto a two line cell which in the end has a double height
- improvement 25: the URl-resolving of the tracks and the download can happen in parallel - not just resolve all of them first and THEN download. no. afte th first is resolved, start a download
- feature 26: show the currently playing track with artistname and title also above the playduriatio and stuff. if the tracklist is long, it could be that the plaiyng song is not visible. this feature shall not be removed, just augmented by that additional information.
- change 27: move the downlod thread setting to the preferences; make it by default 2, up to ten. minimum 1. user chan change it whenever. eachtime new work is "picked", the cehck and spawn more workers, if possible.
- change 28: wording of cache files-actinon-menu: it shall point to the folder with all cached information". find a good wording.
- change 29: by default, when turning off the app (official quit), then also delete all credentials and all stored info! wipe. just if the user sets "Don't wipe data at quitting" (a checkbox), then skip this step. So by default everything is wiped. cybersecurity. when deleting somehing fails, then just prnt to stdout, but don't stop or abort the quit.
- change 30: do a check if everthing in the software is UTF-8 compatbile. and all th strings only rely on UTF-8. i am quite sure this is the case.
* change 31: unit-testing for all calsses above 95%. controller.py is bad.

## UI Design

- 8. Consider switching from the widget-based UI to QML. Reassess whether this still has benefits after the theme work. #lowprio

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

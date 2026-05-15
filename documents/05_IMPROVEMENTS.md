# Improvements

This document collects unresolved follow-up improvements noticed during
implementation. These are not blockers for the current development-plan step,
but they should be revisited before the MVP is considered finished.

## General

- 15. Playlist feature: support dragging and dropping songs into a playlist, then play them one after another.
- fixed: 19. Bug with the download state: cached track files are downloaded again when double-clicked. Cached files should only be shown when they exist. Do a file-system check if we have a result; otherwise, download them. Also check whether the queued-download mechanism really triggers downloads for the remaining tracks.
- fixed: bug 22: in general, when the playlist of a user is available, immediately start to download the tracks. Given the download-in-parallel feature, which defaults to two, do not wait for user input. Start from the top. This can happen as soon as the very first track is in the list.
- 21. Bug: after seeking first, pressing Play does not start playback at the selected position.
- fixed: bug 22: problem with download; age verification. Preferences › YouTube Downloads › Browser cookies lets the user select the browser whose YouTube session cookies yt-dlp uses, enabling age-restricted video access.
- fixed: feature 23: the button "download queued" has to be rename: "start downloads"; when downloading the text switches to "stop downloads". getting tracks which are not locally availalble trigger the download. unless user presses the button for stop. end when everything is downloaded. skip over non available songs.
- fixed: change request 24: Track titles that are longer than the available cell width shall be truncated with an ellipsis, not wrapped into a taller two-line cell.
- fixed: improvement 25: URL resolving and downloading can run in parallel — as soon as the first track is resolved, start its download without waiting for all resolutions to finish.
- fixed: feature 26: Show the currently playing track (artist and title) above the playback duration controls. When the track list is long the playing row may scroll out of view; this label keeps that information always visible.
- fixed: change 27: Move the download-thread-count setting to Preferences. Default to 2, maximum 10, minimum 1. The user can change it at any time; each time new work is picked up, check and spawn additional workers if the limit allows.
- fixed: change 28: Rename the cached-songs menu action to "Open data folder in file manager" and point it at the full application data directory (credentials, track lists, and both caches).
- fixed: change 29: By default, when the application quits, wipe all credentials and cached data. Only skip the wipe if the user has checked "Keep cached data after quitting" in Preferences › Privacy. Deletion failures are printed to stdout without aborting the quit.
- fixed: change 30: Audit all code for UTF-8 compatibility. Add explicit `encoding="utf-8"` to every subprocess call that uses `text=True` (yt-dlp runner and ffprobe). All file I/O already used UTF-8.
- fixed: change 31: Raise unit-test coverage for all modules above 95%. Controller.py was at 85%; targeted new tests brought overall project coverage to 97%.
- feature 32: all downloads are with uneven volume, so some low and some loud. some equalizer would help. which automatically then adjusts the rest of the next plays to the loudness of the current song? or should it be better that all songs are converted to mp3 and then mp3gain is run? with 89db? convert them first to 320 CBR-mp3 and then "gain" them? and only the gained copy is played? so we have the original downloads and also their conversion?!?

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

## Last.fm API

- Loved-track fetching now uses Last.fm's `user.getLovedTracks` API instead of public HTML scraping. The old parser fixture tests remain useful as regression coverage for legacy page parsing, but the normal workflow no longer depends on Last.fm page markup.
- API errors are surfaced in the UI through the existing worker error path. If Last.fm omits total-count metadata, the UI still reports cumulative fetched tracks but cannot show `fetched/total`.

## Logging

- Logging currently writes to stdout for pipeline visibility. A future desktop-friendly setup should add a rotating log file in the app data directory and expose its path in the UI.

## Downloads

- The download manager captures coarse queue progress only. A later pass should parse `yt-dlp` progress hooks or subprocess output so the UI can show per-track byte/percent progress.
- The queue has pause/resume primitives in the manager, but the UI currently exposes a start-download action. A follow-up should add a true pause/resume toggle once long-running download cancellation semantics are settled.
- Download concurrency is handled at the queue level. If `yt-dlp` itself starts parallel fragment downloads, we may need to cap or document that separately.

## Playback

- Playback uses `QMediaPlayer`, which keeps the app inside PyQt but means codec support depends on the user's Qt multimedia backend. A future startup check could verify MP3 playback support and show a clear warning.
- The controller saves visible table tracks after playback state changes. A future storage abstraction should provide a narrower single-track update API to avoid rewriting large user files for a single status change.

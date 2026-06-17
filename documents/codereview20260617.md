# Code Review 2026-06-17

## What Changed Since 2026-06-15

The previous review was `documents/codereview20260615.md`. Several of its concrete runtime findings have been addressed in the current code:

- `ffprobe` is now part of the external dependency check.
- `yt-dlp` lookup, `yt-dlp` download, and `ffprobe` calls now have timeouts.
- Download stop handling now sets a stop flag and wakes paused download workers.
- Automatic downloads are deferred while lookup work is still active.
- The BeautifulSoup runtime dependency mismatch was removed by replacing that path with stdlib parsing.
- Most global Pylint complexity disables were re-enabled in `pyproject.toml`; remaining known complexity is now suppressed locally on specific large objects or methods.

The major unresolved items from 2026-06-15 are still present: `ApplicationController` and `MainWindow` remain god objects, Last.fm session credentials are still persisted as plain JSON, and repository locking still has inconsistent read/write boundaries.

## Ten Worst Current Findings

1. FIXED: **Retrying a `NOT_FOUND` track is likely broken by stale lookup-cache state.**
   `my_lastfm_player/controller.py:1158` resets `NOT_FOUND` and `FAILED` tracks in the per-user track file, but it does not clear the lookup cache entry for the same cache key. The retry path then calls `resolve_youtube_urls()` at `my_lastfm_player/controller.py:1176`; `YouTubeResolver.resolve_and_store_tracks()` immediately reapplies cached lookup state via `repository.mark_cached_lookups()` at `my_lastfm_player/youtube.py:132`; `mark_cached_lookups()` restores stale `NOT_FOUND` at `my_lastfm_player/storage.py:209`; and `resolve_tracks()` skips `NOT_FOUND` rows at `my_lastfm_player/youtube.py:65`. A visible "Retry Download" action can therefore fail to retry the exact class of tracks users most need it for.

2. FIXED: **Main-thread network calls can still freeze the Qt event loop.**
   `fetch_loved_tracks()` performs synchronous Last.fm checks before it starts a worker: cache verification at `my_lastfm_player/controller.py:439` and fresh-user preflight at `my_lastfm_player/controller.py:456`. Startup scrobbling verification runs synchronously at `my_lastfm_player/controller.py:373`, and playback callbacks synchronously call Last.fm now-playing and scrobble operations at `my_lastfm_player/controller.py:1041` and `my_lastfm_player/controller.py:1275`. Those calls sit on top of request timeouts and retry settings in `my_lastfm_player/lastfm.py:24` and `my_lastfm_player/lastfm.py:25`, with actual blocking requests at `my_lastfm_player/lastfm.py:162`. The app has worker infrastructure, but several ordinary UI actions can still block the UI thread on network I/O.

3. FIXED: **Worker errors do not clean up controller/UI workflow state consistently.**
   `_handle_worker_error()` only logs feedback and resets progress at `my_lastfm_player/controller.py:993`. Download state is cleared in the success handler `_handle_tracks_downloaded()` at `my_lastfm_player/controller.py:941`, so an exception before `tracks_downloaded` can leave `_download_worker_active` and the download button state stale. Fetch cleanup is also split across success/stop handlers and `_forget_worker()` at `my_lastfm_player/controller.py:1371`, while the error path does not explicitly restore fetch controls. Cleanup should be tied to lifecycle completion, not only successful result signals.

4. FIXED: **Application shutdown accepts close immediately while background work may still run.**
   `MainWindow.closeEvent()` emits `quit_requested` and immediately accepts at `my_lastfm_player/ui/main_window.py:1034`. The controller's quit handler may wipe repository data at `my_lastfm_player/controller.py:153`, but it does not stop or wait for active threads tracked in `_active_threads` at `my_lastfm_player/controller.py:97`. Fetch, lookup, download, or artist-image workers can therefore keep running while shutdown and optional data deletion proceed, risking lost updates, partial cleanup, or Qt thread lifetime problems.

5. FIXED: **Download cancellation is bounded but still cannot stop an active `yt-dlp` process.**
   `stop_downloads()` marks downloads stopped at `my_lastfm_player/controller.py:1131`, and `DownloadManager.stop()` flips `_stop_requested` at `my_lastfm_player/download.py:74`. However, download workers only check that flag before an attempt at `my_lastfm_player/download.py:178`. Once `_run()` enters blocking `subprocess.run()` at `my_lastfm_player/download.py:231`, the user-facing Stop action cannot terminate the active `yt-dlp`; it waits for process exit or the 600-second timeout at `my_lastfm_player/download.py:239`. This is an improvement over no timeout, but it is not real cancellation.

6. **A shared mutable `DownloadManager` lets overlapping download workflows interfere.**
   The controller injects the same `DownloadManager` instance into every download worker at `my_lastfm_player/controller.py:619`. Starting any download calls `self.download_manager.resume()` at `my_lastfm_player/controller.py:615`, which clears the shared stop flag in `my_lastfm_player/download.py:67`. Priority downloads do not set `_download_worker_active` unless `priority_cache_key is None` at `my_lastfm_player/controller.py:626`, so priority and bulk runs can overlap while sharing pause/stop state, retry settings, and cookie settings. Download state should be per run or managed by an explicit queue.

7. **Repository corruption and storage failures can escape interactive controller paths.**
   Storage raises `StorageError` for invalid JSON and write failures at `my_lastfm_player/storage.py:263` and `my_lastfm_player/storage.py:315`. Worker `run()` methods catch broad exceptions, but controller paths call repository methods directly without recovery: cached-track loading at `my_lastfm_player/controller.py:172`, fetch preflight cache checks at `my_lastfm_player/controller.py:453`, and visible-track saving at `my_lastfm_player/controller.py:1004`. A corrupt local JSON file or write failure can still crash an interactive action instead of producing recoverable UI feedback.

8. **Download filenames are not collision-safe.**
   `Track.audio_base_name` is only sanitized and truncated `"artist - title"` text at `my_lastfm_player/models.py:147`. Downloads use it as the full output stem at `my_lastfm_player/download.py:213`, then discover the newest matching file by stem at `my_lastfm_player/download.py:222`. Different tracks can sanitize or truncate to the same stem, causing overwrites or incorrect local-path attribution. The domain model has a stable `cache_key`, but the filesystem boundary does not use a collision-resistant identifier.

9. **Workflow conflict resolution is encoded as one fragile global status rank.**
   `_STATUS_RANK` in `my_lastfm_player/models.py:26` drives `Track.merge_preserving()` at `my_lastfm_player/models.py:86`. That linear rank tries to cover branches such as fetched, searching, queued, downloading, failed, not-found, downloaded, retry, and re-lookup. Because `NOT_FOUND` outranks `FAILED`, `QUEUED`, and `DOWNLOADING`, a stale terminal lookup state can win during merges even when later workflow intent wants to retry or move forward. This policy belongs in explicit workflow transitions rather than a single global ordering.

10. **The controller and main window remain explicit god objects.**
    `my_lastfm_player/controller.py:1` and `my_lastfm_player/ui/main_window.py:1` both carry file-level `too-many-lines` suppressions, and the primary classes add more complexity suppressions at `my_lastfm_player/controller.py:61` and `my_lastfm_player/ui/main_window.py:148`. `ApplicationController` still owns dependency checks, repository writes, Last.fm fetch orchestration, YouTube lookup, downloads, playback, scrobbling, settings, artist images, and `QThread` lifecycle. `MainWindow` still owns menus, layout construction, filtering, table behavior, playback controls, dialogs, feedback logging, translation, and state formatting. The issues above are symptoms of this concentration: success handlers, error handlers, lifecycle cleanup, and UI state all cross through the same mutable coordinator.

## Still Important From The Previous Review

- Last.fm session credentials are still stored as plain JSON. `ScrobblingService.credentials_dict()` includes `session_key` at `my_lastfm_player/scrobbling.py:184`, and `JsonTrackRepository.save_credentials()` writes it directly at `my_lastfm_player/storage.py:236`.
- Repository locking is still inconsistent. Writes and merges use `_lock` at `my_lastfm_player/storage.py:57` and `my_lastfm_player/storage.py:63`, but reads such as `load_tracks()`, `load_download_cache()`, and `load_lookup_cache()` at `my_lastfm_player/storage.py:40`, `my_lastfm_player/storage.py:97`, and `my_lastfm_player/storage.py:153` remain outside that boundary.
- Pylint complexity visibility improved, but the biggest objects now rely on local suppressions instead of decomposition.

## Review Method

- Read the current repository structure and `documents/codereview20260615.md`.
- Compared recent commits since the previous review, especially fixes from `v0.0.111` through `v0.0.125`.
- Used two read-only subagents: one for independent architecture findings, one for comparison with the previous review.
- Did not modify application code.

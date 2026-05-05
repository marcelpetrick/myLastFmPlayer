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
* 17. make the localization options using a country flag for easy recognition
* 18. menu-options to immediately jump to the stored files directory (open with dolphin or whatever explorer user has set)
* 19. bug with the download-state: when using cached track-files, then they are downloaded when double-cicked. But should they not exist? What about the download queued mechnaism - does not look like it really triggers the download for the "rest" (the not downloaded files)
* fixed: 20: bug with translations; switch to mandarin, then playing a track by double click leads to crash; version 0.0.41:
```
2026-05-04 18:42:56,714 INFO [my_lastfm_player.playback] Starting playback for Die Irrlichter - Gaudete
[myLastFmPlayer] Starting playback: Die Irrlichter - Gaudete
Traceback (most recent call last):
  File "/home/mpetrick/repos/myLastFmPlayer/.venv/lib/python3.14/site-packages/my_lastfm_player/controller.py", line 286, in play_selected_track
    self._play_track(selected_track)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^
  File "/home/mpetrick/repos/myLastFmPlayer/.venv/lib/python3.14/site-packages/my_lastfm_player/controller.py", line 550, in _play_track
    translate(
    ~~~~~~~~~^
        "ApplicationController",
        ^^^^^^^^^^^^^^^^^^^^^^^^
    ...<2 lines>...
        title=track.title,
        ^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/home/mpetrick/repos/myLastFmPlayer/.venv/lib/python3.14/site-packages/my_lastfm_player/i18n.py", line 74, in translate
    return translated.format(**values)
           ~~~~~~~~~~~~~~~~~^^^^^^^^^^
KeyError: '艺术家'
zsh: IOT instruction (core dumped)  .venv/bin/my-lastfm-player
```
* 21. bug: setting progress first, the pressing play does not start at this position insid the track
* fixed: 22. bug: ui, when a song is playing, the pause and stop shall be enabled. pause stops (so pressing pause again continues to play), stop really stops playing. play shall be disabled when pause and stop are active. before anything is played, only play is enabled, stop and pause are disabled.
* fixed: 23. remove the separator at the top of the ui.
* 24. bug: "dependencies installed"" is not translated; mark when available this with a green emoji-circle (ball), else when one at least is missing, red emoji ball - so that the user immeidately gets whats wrong

## Documentation
* fixed: 3. Sphinx is configured for Python API documentation and runs in the local pipeline with warnings treated as errors.
* fixed: 4. public classes, functions, and methods have Sphinx-readable API documentation, and the Sphinx run is warning-free.

## UI design
* 8. switch to use qml isntead of a widget based app? benefits
* 9. themes, color schemes? dark light mode at least
* fixed: 10. the app has Qt translation support, translation file generation commands, and a live language-selection menu.

-----
# scrobbling!

## Requirements: Last.fm setup and scrobbling with `pylast`

### Goal

Enable users to connect their Last.fm account, persist the connection, fetch loved tracks, and scrobble playback history.

### Preferences menu

The app must include a **Last.fm preferences menu** where the user can:

1. Enter their Last.fm username.
2. Start Last.fm authentication.
3. See whether Last.fm is connected/authenticated.
4. Disconnect Last.fm.

The username and authentication state must be persisted.

### Authentication flow

When the user clicks **Authenticate with Last.fm**:

1. App creates a `pylast.LastFMNetwork` using app API key and secret.
2. App generates a Last.fm web authorization URL via `pylast.SessionKeyGenerator`.
3. App opens the URL in the user’s browser.
4. User authorizes the app on Last.fm.
5. App retrieves the Last.fm `session_key`.
6. App persists:

   * Last.fm username
   * `session_key`
   * authenticated status

The app must **not** ask for or store the user’s Last.fm password.

### Runtime behavior

On app startup:

1. Load persisted Last.fm username.
2. Load persisted Last.fm session key.
3. If a session key exists, initialize `pylast.LastFMNetwork` with it.
4. Mark Last.fm as connected only if authenticated API access works.
5. If authentication fails, keep username but mark Last.fm as not authenticated.

### Fetching loved songs

Fetching loved songs is separate from scrobbling.

The app must support fetching loved tracks for the configured username, using the Last.fm API.

Requirements:

1. User must have a configured Last.fm username.
2. Authentication is preferred but not necessarily required for public loved tracks.
3. Fetching loved tracks must not depend on whether scrobbling is currently active.
4. Results should be cached or stored according to the app’s normal library/indexing behavior.

### Scrobbling

Scrobbling requires a valid authenticated Last.fm session.

The app must only scrobble when:

1. Last.fm username is configured.
2. Last.fm session key exists.
3. Last.fm authentication is valid.
4. User has enabled scrobbling, if the app has a separate scrobbling toggle.

For each scrobble, send:

* artist
* track title
* album, if available
* timestamp
* duration, if available

If the app cannot scrobble, it must fail gracefully and explain why, for example:

* Last.fm is not authenticated
* missing username
* missing track metadata
* network/API error

### Persistence

Persist the following:

* Last.fm username
* Last.fm session key
* authentication status
* scrobbling enabled/disabled state, if applicable

The session key must be stored securely where possible and must not be written to logs.

### Acceptance criteria

Implementation is complete when:

1. User can enter Last.fm username in preferences.
2. User can authenticate via browser from preferences.
3. App persists username and auth session after restart.
4. App can fetch loved songs for the configured user.
5. App can scrobble after successful authentication.
6. App does not ask for the Last.fm password.
7. App clearly shows “connected” or “not connected” state.
8. App handles failed/expired auth without crashing.

END OF SCROBBLING

-----


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
- fixed: Playback no longer mutates persisted track status; the `Playing` enum value was removed and the currently playing row is highlighted in bold instead, so the table sort order is preserved across play/stop.
- The controller saves visible table tracks after playback state changes. A future storage abstraction should provide a narrower single-track update API to avoid rewriting large user files for a single status change.

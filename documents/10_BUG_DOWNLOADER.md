# Resolved Bug: Background Download Did Not Start for Cached Tracks

> **Historical fixed-bug record:** This investigation describes an earlier downloader
> implementation. The current overlapping, bounded workflow is documented in
> [`03_ARCHITECTURE.md`](03_ARCHITECTURE.md).

## Original Fix Plan

Fix background auto-download for cached and freshly fetched tracks.

## Context

Bug 22 was declared fixed ("immediately start downloads when a playlist is available;
do not wait for user input"). Downloads did not start automatically in the common case
where a user's tracks were already cached on disk. The fresh-fetch path also had a race
in which two lookup workers could trigger concurrent downloads of the same files.

## Root Cause Analysis

### Bug A — No Automatic Download on the Cache Path

Original location: `controller.py:363–401` (`fetch_loved_tracks`)

```python
if self.load_cached_tracks_for_entered_username(verify_online_count=True):
    self.window.set_fetch_control_state(active=False, paused=False)
    self.window.set_progress(100, ...)
    return  # No worker started; queued tracks stayed idle.
```

When cached tracks existed, the method returned after populating the UI.
`load_cached_tracks_for_entered_username` applied both `mark_cached_lookups` and
`mark_cached_downloads`, but queued tracks whose files were absent never started
downloading.

### Bug B — Double Lookup Could Start Two Downloads

Original locations: `controller.py:712–748` (`_handle_tracks_updated`) and
`controller.py:655–685` (`_handle_tracks_loaded`)

`_handle_tracks_updated` started an incremental lookup. `_handle_tracks_loaded` then
started a second full lookup because its guard flag was reset too early. Both completion
paths could create a `DownloadTracksWorker`, load the same queued tracks, and write the
same output files.

## Proposed Changes

### Change 1 — Start Lookup After Loading the Cache

After the early cache path succeeded, `fetch_loved_tracks` would call
`_start_automatic_lookup`. The lookup worker's `resolve_and_store_tracks` path skipped
already resolved tracks without running `yt-dlp`.

```python
if self.load_cached_tracks_for_entered_username(verify_online_count=True):
    self.window.set_fetch_control_state(active=False, paused=False)
    self.window.set_progress(100, translate("ApplicationController", "Loaded cached tracks"))
    tracks = self.window.tracks()
    if tracks:
        self._start_automatic_lookup(username, len(tracks))
    return
```

### Change 2 — Guard Against Concurrent Download Workers

Add `_download_worker_active: bool = False` to `__init__`.

Set `_download_worker_active = True` in `_start_automatic_download`.

In `_handle_tracks_downloaded`, reset the flag, check whether the completed run left
queued candidates, and start a follow-up download when needed.

In `_handle_tracks_resolved`, call `_start_automatic_download` only when no download
worker is active.

This turns the "two downloads fire and race" pattern into a clean "chain": first download runs, finishes, sees any remaining
candidates, starts a second pass if needed.

### Change 3 — Prevent the Second Lookup

Save `_started_incremental_lookup_for_fetch` before resetting it, then skip the
redundant lookup when incremental work already started:

```python
already_started = self._started_incremental_lookup_for_fetch
self._active_fetch_worker = None
self._fetch_paused = False
self._started_incremental_lookup_for_fetch = False
# ...
if tracks and not already_started:
    self._start_automatic_lookup(username, len(tracks))
```

The incremental lookup started from `_handle_tracks_updated` and loaded the repository
snapshot when the worker started. Tracks arriving after that snapshot would be picked up
through the cache path in the next session.

## Original Files Changed

- `my_lastfm_player/controller.py`: `__init__`, `fetch_loved_tracks`,
  `_handle_tracks_loaded`, `_start_automatic_download`, `_handle_tracks_resolved`, and
  `_handle_tracks_downloaded`.

No changes were proposed for `download.py`, `workers.py`, `storage.py`, or `youtube.py`.

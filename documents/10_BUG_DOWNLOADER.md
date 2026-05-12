# Bug: Background download does not start for cached tracks

fixed

Plan: Fix background auto-download for cached and freshly-fetched tracks

Context

Bug 22 was declared fixed ("immediately start downloads when a playlist is available, don't wait for user input"). However, downloads do
not actually start automatically in the common case where a user's tracks are already cached on disk. Additionally, the fresh-fetch code
path has a race condition where two lookup workers can both trigger a download worker, causing concurrent downloads that overwrite each
other.

Root Cause Analysis

Bug A — No auto-download on cache-path (primary bug)

File: controller.py:363–401 (fetch_loved_tracks)

 if self.load_cached_tracks_for_entered_username(verify_online_count=True):
     self.window.set_fetch_control_state(active=False, paused=False)
     self.window.set_progress(100, ...)
     return   # <— no worker started; QUEUED tracks silently sit idle

When cached tracks exist (the normal case after the first run), the method returns after populating the UI.
load_cached_tracks_for_entered_username applies both mark_cached_lookups (sets QUEUED for tracks with a known YouTube URL) and
mark_cached_downloads (marks DOWNLOADED for files that exist on disk). Tracks that are QUEUED — youtube_url known, file not yet on disk —
are never downloaded automatically.

Bug B — Double lookup → potential double download (secondary bug)

File: controller.py:712–748 (_handle_tracks_updated) and controller.py:655–685 (_handle_tracks_loaded)

_handle_tracks_updated starts an incremental lookup (one-time, guarded by _started_incremental_lookup_for_fetch). Then
_handle_tracks_loaded always starts a second full lookup (the flag is reset before the check, so it is never effective here). Both
lookups call _handle_tracks_resolved, and both can call _start_automatic_download, spawning two concurrent DownloadTracksWorker instances
that both load the same QUEUED tracks from disk and race to write the same output files.

Proposed Changes (controller.py only)

Change 1 — Auto-start lookup after cache load

In fetch_loved_tracks, after the early-return path succeeds, call _start_automatic_lookup. The lookup worker calls
resolve_and_store_tracks, which:
- Skips already-resolved tracks (QUEUED) with no yt-dlp calls — O(n) in-memory pass

    if self.load_cached_tracks_for_entered_username(verify_online_count=True):
        self.window.set_fetch_control_state(active=False, paused=False)
        self.window.set_progress(100, translate("ApplicationController", "Loaded cached tracks"))
        tracks = self.window.tracks()
        if tracks:
            self._start_automatic_lookup(username, len(tracks))
        return

Change 2 — Guard against concurrent download workers

Add _download_worker_active: bool = False to __init__.

In _start_automatic_download (which calls download_tracks): set _download_worker_active = True.

In _handle_tracks_downloaded: reset _download_worker_active = False, then re-check whether the completed download run left any QUEUED
candidates (from a second lookup that resolved new tracks concurrently) and start a follow-up download if so.

In _handle_tracks_resolved: only call _start_automatic_download when _download_worker_active is False.

This turns the "two downloads fire and race" pattern into a clean "chain": first download runs, finishes, sees any remaining
candidates, starts a second pass if needed.

Change 3 — Fix _handle_tracks_loaded double-lookup

Save the _started_incremental_lookup_for_fetch flag before resetting it, and skip the redundant automatic lookup when the incremental
lookup was already started:

    already_started = self._started_incremental_lookup_for_fetch
    self._active_fetch_worker = None
    self._fetch_paused = False
    self._started_incremental_lookup_for_fetch = False
    ...
    if tracks and not already_started:
        self._start_automatic_lookup(username, len(tracks))

The incremental lookup starts from _handle_tracks_updated and calls load_tracks(username) at worker start — by that point the fetch is
typically far enough along (or complete) that the repository snapshot is sufficient. Any tracks missed by the incremental lookup
because they arrived after the snapshot will be picked up in the next session's cache-path (Change 1).

Files changed

- my_lastfm_player/controller.py: __init__ (+1 flag), fetch_loved_tracks, _handle_tracks_loaded,
  _start_automatic_download, _handle_tracks_resolved, _handle_tracks_downloaded

No changes to download.py, workers.py, storage.py, or youtube.py.

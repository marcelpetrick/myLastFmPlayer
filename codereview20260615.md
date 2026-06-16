# Code Review 2026-06-15

## Ten Worst Findings

1. **God controller mixes almost every application responsibility.**
   `my_lastfm_player/controller.py:60` defines `ApplicationController`, and `my_lastfm_player/controller.py:63` starts an initializer that wires UI, repository, Last.fm scraping, YouTube lookup, downloads, playback, artist images, dependency checks, settings, scrobbling, and worker factories. The class runs until `my_lastfm_player/controller.py:1372`. This makes workflow behavior hard to reason about, pushes state coordination into booleans such as `_download_worker_active`, `_pending_play_cache_key`, and `_started_incremental_lookup_for_fetch`, and makes smaller domain services difficult to test independently.

2. **Main window is also a god object and owns too much non-view logic.**
   `my_lastfm_player/ui/main_window.py:147` defines an 870-line `MainWindow`. It builds menus, layout, filtering, table selection, playback controls, feedback logging, about text, license text, timeline seeking, language switching, and state formatting in one class through `my_lastfm_player/ui/main_window.py:1016`. The UI layer therefore contains policy and content that should be split into smaller widgets, presenters, or view-model helpers.

3. **Pylint is configured to ignore the exact complexity signals this codebase needs.**
   `pyproject.toml:80` starts a broad `disable` list that includes `too-many-arguments`, `too-many-branches`, `too-many-instance-attributes`, `too-many-lines`, `too-many-locals`, `too-many-public-methods`, and `too-many-statements` through `pyproject.toml:101`. Those disabled checks would flag the controller and main window problems above, so the quality gate has been tuned to pass around architectural debt instead of making it visible.

4. FIXED: **The dependency check misses a command the code actually invokes.**
   `my_lastfm_player/dependencies.py:536` requires only `yt-dlp` and `ffmpeg`, but `my_lastfm_player/download.py:264` invokes `ffprobe` directly. A system can pass the startup dependency check and still fail to show audio metadata because `ffprobe` is absent.

5. **External subprocesses have no timeout or cancellation boundary.**
   `my_lastfm_player/youtube.py:485` runs `yt-dlp` lookup with `subprocess.run` but no `timeout`. `my_lastfm_player/download.py:218` does the same for downloads, and `my_lastfm_player/download.py:264` does it again for `ffprobe`. If `yt-dlp` or `ffprobe` hangs, the worker thread can hang indefinitely and the UI only sees a stuck workflow.

6. **Stopping downloads is not real cancellation and can leave workers blocked.**
   `my_lastfm_player/controller.py:1125` handles stop by setting flags, calling `DownloadManager.pause()`, and updating the button. `my_lastfm_player/download.py:58` implements pause by clearing an event, while `my_lastfm_player/download.py:167` waits on that event before attempts. There is no stop token passed into active downloads and no subprocess termination, so stop can pause future attempts while already-submitted futures keep running or block before retry.

7. **Workflow orchestration can start overlapping lookup/download work from partial fetch updates.**
   `my_lastfm_player/controller.py:855` starts an automatic lookup after the first partial fetch batch, before the fetch worker has completed. `my_lastfm_player/controller.py:886` starts download handling as soon as a single track becomes queued, and `my_lastfm_player/controller.py:1201` can start automatic downloads whenever no active download worker is detected. This creates a fragile multi-worker pipeline with repository merges as the synchronization mechanism, instead of an explicit workflow state machine or queue.

8. **Credential persistence stores the Last.fm session key as plain JSON.**
   `my_lastfm_player/scrobbling.py:459` returns a credentials dictionary containing `session_key`, and `my_lastfm_player/storage.py:236` writes it through `_atomic_write_json`. There is no OS keyring integration, no file permission hardening, and no separation between low-sensitivity track cache data and account session material.

9. **Installed runtime dependencies do not match public runtime code paths.**
   `pyproject.toml:21` puts `beautifulsoup4` only in the `dev` extra, but `my_lastfm_player/lastfm.py:618` exposes `parse_loved_tracks_page`, and `my_lastfm_player/lastfm.py:788` imports BeautifulSoup at runtime for that parser. A normal package install can import the app successfully but fail when this public parser path is used.

10. **Repository locking is inconsistent despite concurrent worker access.**
    `my_lastfm_player/storage.py:38` creates an `RLock`, and write paths such as `my_lastfm_player/storage.py:53` use it. Read paths such as `my_lastfm_player/storage.py:40`, `my_lastfm_player/storage.py:97`, and `my_lastfm_player/storage.py:153` do not. Because fetch, lookup, and download workers all read and merge repository state concurrently, the repository should define a consistent locking boundary for read-modify-write workflows instead of relying on atomic file replacement alone.

## Five Good Things

1. **The domain model is immutable and validates core invariants.**
   `my_lastfm_player/models.py:367` uses a frozen, slotted dataclass for `Track`, and `my_lastfm_player/models.py:383` validates empty artist/title and negative numeric fields.

2. **JSON writes use a reasonably robust atomic-write pattern.**
   `my_lastfm_player/storage.py:315` writes to a temp file in the target directory, `my_lastfm_player/storage.py:323` flushes, `my_lastfm_player/storage.py:324` fsyncs the file, and `my_lastfm_player/storage.py:325` replaces the target path.

3. **The codebase is highly test-oriented.**
   `pyproject.toml:44` configures strict pytest options, coverage reporting, and `pyproject.toml:51` sets a 99% coverage gate. The repository also has focused test modules for controller, workers, storage, Last.fm, YouTube, playback, settings, i18n, and UI models.

4. **External integrations are injectable enough to test without real services.**
   `my_lastfm_player/controller.py:63` accepts repository, scraper, resolver, download manager, playback service, worker factories, and dependency checker. `my_lastfm_player/youtube.py:352` and `my_lastfm_player/download.py:38` accept command runners, which keeps subprocess behavior testable.

5. **Long-running UI work is kept off the main Qt thread.**
   `my_lastfm_player/controller.py:717` moves workflow workers to `QThread`, connects progress/error/finished signals, and cleans up thread and worker references through `my_lastfm_player/controller.py:739` to `my_lastfm_player/controller.py:743`.

## Verification

- `python -m ruff check .` passed.
- `python -m pytest -q` could not run in this environment because `PyQt6` is not installed.
- `python -m pylint my_lastfm_player --score=no` could not complete usefully because `PyQt6` and `pylast` are not installed in this environment.

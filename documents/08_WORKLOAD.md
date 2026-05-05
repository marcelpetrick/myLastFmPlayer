# Workload Estimate

This document estimates the implementation workload represented by the current
git history. The estimates are in person-hours and are based on commit message,
diff size, affected surface area, and likely verification effort.

Assumptions:

- The estimate is implementation effort for a competent developer familiar with
  Python, PyQt, pytest, and desktop packaging.
- Each row includes the commit's likely coding, documentation, test, review, and
  local verification effort.
- Generated translation and packaging changes are estimated by integration and
  verification effort, not by raw line count.
- The three-point values are `Best`, `Expected`, and `Worst`.
- `PERT` uses `(Best + 4 * Expected + Worst) / 6`.

## Summary Chart

```text
Best      | #############                         189.7 h
Expected  | #######################               340.0 h
PERT      | ########################              356.3 h
Worst     | ####################################  588.0 h
```

| Estimate | Hours |
| --- | ---: |
| Best-case total | 189.7 |
| Expected total | 340.0 |
| Worst-case total | 588.0 |
| PERT-weighted total | 356.3 |

## Per-Commit Three-Point Estimate

| # | Commit | Date | Commit message | Best | Expected | Worst |
| ---: | --- | --- | --- | ---: | ---: | ---: |
| 1 | `c9756cd` | 2026-04-29 | Initial commit | 1.5 | 3.0 | 6.0 |
| 2 | `4632490` | 2026-04-29 | start of project: added requirements and updated the git-ignore | 1.0 | 2.0 | 4.0 |
| 3 | `d1b3316` | 2026-04-29 | docs: add implementation plan | 1.5 | 3.0 | 5.0 |
| 4 | `14b1199` | 2026-04-29 | docu: prepared the development plan; moved and renamed documents for homogenized view | 1.0 | 2.0 | 3.5 |
| 5 | `f3e1761` | 2026-04-29 | feat: scaffold PyQt application | 4.0 | 7.0 | 12.0 |
| 6 | `38c21c4` | 2026-04-29 | test: add local quality pipeline | 3.0 | 5.0 | 8.0 |
| 7 | `2667372` | 2026-04-29 | docu: renaming | 0.25 | 0.5 | 1.0 |
| 8 | `d0b330c` | 2026-04-29 | coverage covered in the localPipeline.sh | 0.5 | 1.0 | 2.0 |
| 9 | `d5924d5` | 2026-04-29 | chore: add application versioning | 1.0 | 2.0 | 3.5 |
| 10 | `20f70b3` | 2026-04-29 | feat: add track domain model | 2.0 | 4.0 | 7.0 |
| 11 | `5d84fa8` | 2026-04-29 | feat: add JSON track storage | 3.0 | 6.0 | 10.0 |
| 12 | `bc8cc25` | 2026-04-29 | feat: add Last.fm loved tracks scraper | 5.0 | 9.0 | 16.0 |
| 13 | `4659f35` | 2026-04-29 | feat: bind tracks to table model | 3.0 | 5.5 | 9.0 |
| 14 | `5006962` | 2026-04-29 | feat: add controller worker boundary | 5.0 | 8.0 | 14.0 |
| 15 | `adb2941` | 2026-04-29 | feat: add YouTube resolver | 4.0 | 7.0 | 12.0 |
| 16 | `89e0d43` | 2026-04-29 | feat: improve fetch progress feedback | 2.0 | 4.0 | 7.0 |
| 17 | `032ca77` | 2026-04-29 | refactor: wrap Last.fm fetching and parsing | 4.0 | 7.0 | 12.0 |
| 18 | `31249c5` | 2026-04-29 | fix: handle transient Last.fm fetch failures | 2.0 | 4.0 | 7.0 |
| 19 | `eb4a212` | 2026-04-29 | chore: launch app after local pipeline | 1.0 | 2.0 | 4.0 |
| 20 | `0f8699b` | 2026-04-29 | Document local build workflow | 0.8 | 1.5 | 2.5 |
| 21 | `de9456a` | 2026-04-29 | fix: align Last.fm e2e with UI fetch | 1.5 | 3.0 | 5.0 |
| 22 | `87df7c5` | 2026-04-29 | fix: wire toolbar fetch action | 0.5 | 1.0 | 2.0 |
| 23 | `9012889` | 2026-04-29 | fix: retain background fetch workers | 1.0 | 2.0 | 4.0 |
| 24 | `3452711` | 2026-04-29 | feat: add download queue manager | 7.0 | 12.0 | 20.0 |
| 25 | `4f242d2` | 2026-04-29 | feat: add local playback controls | 6.0 | 10.0 | 16.0 |
| 26 | `d7a2922` | 2026-04-29 | feat: chain mvp fetch workflow | 3.0 | 5.0 | 9.0 |
| 27 | `303c4b7` | 2026-04-29 | docs: add development plan review | 1.0 | 2.0 | 3.0 |
| 28 | `b0d8242` | 2026-04-29 | fix: prioritize playback preparation | 4.0 | 7.0 | 12.0 |
| 29 | `986618f` | 2026-04-29 | docs: explain player workflow and storage | 1.0 | 2.0 | 3.0 |
| 30 | `f09137b` | 2026-04-29 | git-ignore: remove codex | 0.1 | 0.25 | 0.5 |
| 31 | `e8ed7cf` | 2026-04-30 | Add local pipeline stage summary | 4.0 | 7.0 | 11.0 |
| 32 | `55f8c28` | 2026-04-30 | improvements: moved and named the file and added tons of ideas | 0.5 | 1.0 | 2.0 |
| 33 | `10b22f0` | 2026-04-30 | Fix local pipeline documentation gate | 0.5 | 1.0 | 2.0 |
| 34 | `b469bb7` | 2026-04-30 | Docu: added information and a screenshot; invalidated the docu-stage | 0.5 | 1.0 | 2.0 |
| 35 | `ecc1e99` | 2026-04-30 | Update table during paginated fetch | 2.0 | 4.0 | 7.0 |
| 36 | `ae9a046` | 2026-04-30 | Make versioned window title explicit | 0.75 | 1.5 | 3.0 |
| 37 | `e32387d` | 2026-04-30 | Update track rows during lookup and download | 2.0 | 4.0 | 7.0 |
| 38 | `f65d25d` | 2026-04-30 | Add Sphinx documentation pipeline | 3.0 | 5.5 | 9.0 |
| 39 | `af921b3` | 2026-04-30 | Document public Python API | 2.0 | 4.0 | 7.0 |
| 40 | `5354ad3` | 2026-04-30 | Add fetch pause and stop controls | 4.0 | 7.0 | 12.0 |
| 41 | `6c28501` | 2026-04-30 | Prefer Firefox for pipeline reports | 1.0 | 2.0 | 4.0 |
| 42 | `09af70e` | 2026-04-30 | README:update | 0.5 | 1.0 | 2.0 |
| 43 | `61f8dc1` | 2026-05-01 | fix: start app once from local pipeline | 1.0 | 2.0 | 4.0 |
| 44 | `89c2220` | 2026-05-01 | feat: load cached tracks and lookups | 4.0 | 7.0 | 12.0 |
| 45 | `b4560f9` | 2026-05-02 | feat: add Qt translation workflow | 8.0 | 14.0 | 24.0 |
| 46 | `465b44d` | 2026-05-02 | improvedment: improved the improvements with new ideas | 0.5 | 1.0 | 2.0 |
| 47 | `b3b4ea6` | 2026-05-03 | fix: normalize version metadata | 3.0 | 5.0 | 9.0 |
| 48 | `54493cb` | 2026-05-03 | feat: add playback timeline seeking | 4.0 | 7.0 | 12.0 |
| 49 | `27f8a1e` | 2026-05-03 | fix: seek timeline on click | 1.0 | 2.0 | 4.0 |
| 50 | `39d3721` | 2026-05-03 | test: require ninety percent coverage | 3.0 | 5.0 | 8.0 |
| 51 | `ab09b61` | 2026-05-03 | feat: play tracks on double click | 1.0 | 2.0 | 4.0 |
| 52 | `d551f28` | 2026-05-03 | Update 05_IMPROVEMENTS.md | 1.0 | 2.0 | 3.0 |
| 53 | `94911f3` | 2026-05-03 | feat: continue playback with sorted next track | 6.0 | 10.0 | 18.0 |
| 54 | `e8c8352` | 2026-05-03 | feat: move primary actions into main menu | 3.0 | 5.0 | 9.0 |
| 55 | `30fadd7` | 2026-05-03 | README: fresh screenshot | 0.25 | 0.5 | 1.0 |
| 56 | `32c3e70` | 2026-05-03 | git ignore: CLAUDE.md | 0.1 | 0.25 | 0.5 |
| 57 | `260a9cf` | 2026-05-03 | fix(playback): preserve table sort order while playing | 3.0 | 5.0 | 9.0 |
| 58 | `13e9960` | 2026-05-04 | review: noted done some ideas for improvements; added bug-reports | 0.25 | 0.5 | 1.0 |
| 59 | `f4f0a9f` | 2026-05-04 | updated the ts-files | 1.0 | 2.0 | 4.0 |
| 60 | `b8e8ce3` | 2026-05-04 | feat(i18n): add rendered flag icons to language menu entries | 3.0 | 5.0 | 9.0 |
| 61 | `1b53528` | 2026-05-04 | fix(tests): update version assertions to 0.0.41 | 0.25 | 0.5 | 1.0 |
| 62 | `cbce904` | 2026-05-04 | translations: compiled & translations for all four non-english languages | 1.5 | 3.0 | 5.0 |
| 63 | `a4aaedf` | 2026-05-04 | feat(i18n): mark table headers and TrackStatus values for translation && translations: doen with CuteLingoExpress 0.2.1 | 4.0 | 7.0 | 12.0 |
| 64 | `f005e4a` | 2026-05-04 | bug report: language based crash | 0.5 | 1.0 | 2.0 |
| 65 | `c1fbc5e` | 2026-05-05 | fix(i18n): replace translated placeholder names with English keys in all .ts files | 2.0 | 4.0 | 7.0 |
| 66 | `9738137` | 2026-05-05 | fix(ui): remove empty toolbar that rendered as a separator line | 0.5 | 1.0 | 2.0 |
| 67 | `86c64c7` | 2026-05-05 | fix(ui): enforce correct Play/Pause/Stop enabled states during playback | 4.0 | 7.0 | 12.0 |
| 68 | `62e43b4` | 2026-05-05 | fix(ui): add status emoji to dependency label and retranslate on language switch | 3.0 | 5.5 | 9.0 |
| 69 | `44dec64` | 2026-05-05 | feat(ui): add light/dark theme switching via Main > Theme menu | 5.0 | 8.0 | 14.0 |
| 70 | `1363540` | 2026-05-05 | feat(scrobbling): add Last.fm OAuth authentication and scrobbling at 10% threshold | 12.0 | 20.0 | 34.0 |
| 71 | `64f322b` | 2026-05-05 | docs(scrobbling): add setup checklist for developer and user onboarding | 1.0 | 2.0 | 3.5 |
| 72 | `ea7f65d` | 2026-05-05 | chore(deps): refresh stable dependency floors | 2.0 | 4.0 | 6.0 |
| 73 | `a752b84` | 2026-05-05 | feat(ui): add lilac and mint themes | 3.0 | 5.5 | 9.0 |
| 74 | `a8c1205` | 2026-05-05 | feat(scrobbling): bundle Last.fm app credentials | 2.0 | 4.0 | 7.0 |
| 75 | `55b545e` | 2026-05-05 | test: raise coverage for small branch gaps | 2.0 | 4.0 | 7.0 |
| 76 | `c1c3f36` | 2026-05-05 | test: reach ninety five percent coverage | 4.0 | 7.0 | 12.0 |
| 77 | `4558735` | 2026-05-05 | docs: move agent guidelines into documents | 1.5 | 3.0 | 5.0 |
| 78 | `535f6ca` | 2026-05-05 | feat(ui): open file cache from menu | 4.0 | 6.5 | 11.0 |
| 79 | `6ebe97f` | 2026-05-05 | ci: add pylint to local pipeline | 3.0 | 5.0 | 8.0 |
| **Total** |  |  |  | **189.7** | **340.0** | **588.0** |

---------------------------------------------------------------------

Alternative view.

## Known-Upfront Straight Implementation Scenario

This scenario estimates the workload if the complete current feature set,
requirements, quality gates, and wishes had been known from the beginning and a
human developer implemented them in a planned sequence without bug-fix churn.
It is lower than the per-commit estimate because it removes exploratory commits,
version-fix commits, translation repair commits, UI rework, and other iteration
costs. It still includes normal engineering work: design, coding, tests,
documentation, packaging, local verification, and some integration polish.

### Known Features, Wishes, and Requirements

Core application:

- Linux x86_64 desktop app written in Python with PyQt.
- Last.fm username input.
- Fetch loved tracks from public Last.fm pages without requiring a user API key.
- Handle Last.fm pagination, parsing failures, transient fetch failures, and
  progress reporting.
- Persist per-user loved tracks in JSON.
- Persist track metadata: artist, title, Last.fm URL, YouTube URL, local path,
  status, retry count, and error information.
- Track states for fetched, queued, searching, downloading, downloaded, failed,
  and not found.
- Load cached tracks and cached YouTube lookups for a username.
- Share downloaded-track cache across users.
- Avoid re-downloading files that already exist locally.
- Exact artist/title cache matching for MVP.
- Multi-user username switching without full profile management.

YouTube and downloads:

- Resolve YouTube tracks with `yt-dlp` using `<artist> <title>`.
- Select the first YouTube result only for MVP.
- Mark tracks as not found when lookup fails.
- Download audio through `yt-dlp`.
- Convert/extract MP3 through `ffmpeg`.
- Use `<Artist> - <Title>.mp3` filenames.
- Automatic lookup and download after fetching.
- FIFO download queue.
- Default concurrency of two downloads, configurable in the UI.
- Random 1-5 second backoff between downloads.
- Up to three download attempts per track, then mark failed.
- Priority lookup/download when the user selects or starts a track.
- Download pause/resume and stop/cancel semantics where exposed.
- Menu action to open the local file cache in the system file manager.

Playback:

- Local playback through `QMediaPlayer`.
- Play, pause/resume, and stop controls.
- Correct enabled/disabled states for Play/Pause/Stop.
- Only one track plays at a time.
- Playing a new track stops previous playback.
- Double-clicking a track starts playback.
- Playback timeline with current time, total time, drag seeking, and click-to-seek.
- Continue playback with the next track in the current table sort order.
- Preserve table sort order while playing.
- Highlight the currently playing row without mutating persisted track status.

UI and user feedback:

- Main table with artist, title, and status columns.
- Sortable table columns and row selection.
- Row-by-row table updates during fetch, lookup, and download.
- Status bar and feedback log for progress and errors.
- Dependency check for `yt-dlp` and `ffmpeg` on startup.
- Green/red dependency status marker.
- Main menu for primary actions.
- Preferences dialog.
- Light and dark themes.
- Lilac and mint themes.
- Language menu with rendered flag icons.
- Live translation support for static UI text, table headers, statuses, and
  controller feedback.
- Remove empty toolbar/separator artifacts.
- Versioned window title.

Last.fm scrobbling:

- Preferences UI for Last.fm authentication state.
- Bundled Last.fm desktop app API key and shared secret.
- Environment variable overrides for custom Last.fm API credentials.
- Browser-based Last.fm authorization flow.
- Persist Last.fm username, session key, and scrobbling-enabled state.
- Reconnect authenticated Last.fm session on startup.
- Show connected/not-connected state.
- Send now-playing notification when playback starts.
- Scrobble after 10 percent of a track has played.
- Fail gracefully when scrobbling is disabled, unauthenticated, missing metadata,
  or blocked by network/API errors.
- Never ask for or store a Last.fm password.

Engineering, documentation, and delivery:

- Conventional commits and version metadata.
- `my_lastfm_player/version.py` as version source of truth.
- Build-time commit suffix in packaged artifacts.
- README current-state documentation and screenshots.
- Required project documents.
- Sphinx API documentation with warnings treated as errors.
- Local pipeline that installs dev dependencies, runs Ruff, Pylint, docs checks,
  Sphinx, pytest with coverage, report opening, package build, wheel install,
  import verification, and optional app launch.
- Ruff linting.
- Pylint static analysis at 10/10 for the configured application scope.
- Pytest coverage gate, raised first to 90 percent and then to about 95 percent.
- Tests for storage, scraping, controller workflows, workers, playback, UI
  smoke behavior, translations, themes, scrobbling, dependencies, YouTube
  lookup, and packaging/version behavior.

Open wishes and follow-up ideas:

- Playlist feature with drag-and-drop ordering and sequential playback.
- QML UI migration evaluation.
- Improve cached-download state handling for double-click playback and queued
  downloads.
- Start playback at an already selected progress position.
- Lock or constraints file for reproducible dependency resolution.
- Faster local pipeline when dependencies did not change.
- Dedicated workflow coordinator if sequencing grows.
- Dedicated job queue for priority playback/download behavior.
- Live YouTube integration tests when network-dependent checks are acceptable.
- Future SQLite migration.
- Fuzzy duplicate matching.
- Better YouTube ranking/scoring.
- Metadata tagging such as ID3.
- Playlist export.
- Cross-platform support.
- Rotating desktop log file exposed in the UI.
- Per-track byte/percent download progress from `yt-dlp`.
- MP3 playback backend capability check.

### Straight Implementation Estimate

```text
Best      | ###############                       152.0 h
Expected  | #########################             252.0 h
PERT      | ##########################            261.5 h
Worst     | ##################################### 409.0 h
```

| Work package | Best | Expected | Worst |
| --- | ---: | ---: | ---: |
| Product clarification and implementation plan | 6.0 | 10.0 | 18.0 |
| Project setup, versioning, docs skeleton, and local pipeline | 14.0 | 22.0 | 34.0 |
| Domain model, JSON storage, cache identity, and multi-user loading | 12.0 | 20.0 | 32.0 |
| Last.fm loved-track scraping, pagination, retries, and progress | 16.0 | 26.0 | 42.0 |
| YouTube lookup, download manager, cache reuse, concurrency, and priority work | 20.0 | 34.0 | 55.0 |
| PyQt table UI, playback controls, timeline seeking, sorted-next playback, and file-cache menu | 22.0 | 36.0 | 58.0 |
| Preferences, themes, translations, flag icons, and Last.fm scrobbling | 30.0 | 50.0 | 82.0 |
| Tests, coverage raising, Sphinx API docs, README, and delivery polish | 22.0 | 36.0 | 58.0 |
| Final integration, packaging, wheel verification, and acceptance pass | 10.0 | 18.0 | 30.0 |
| **Total** | **152.0** | **252.0** | **409.0** |
| **PERT-weighted total** |  | **261.5** |  |

For a single human developer, the expected straight-through workload is roughly
252 hours, or about 6.3 full-time 40-hour weeks. The PERT-weighted total is
about 261.5 hours, or about 6.5 full-time weeks.

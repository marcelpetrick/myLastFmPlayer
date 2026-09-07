# UI/UX review

Reviewed: 2026-09-07. Application: v0.0.160, commit `2a4c1fd`.
Scope: the whole current desktop interface and its controller-driven interactions,
not a branch diff. This report is published with the documentation version bump to v0.0.161.

## Method and priorities

Inspected the main window, table model, preferences, themes, translations, session
settings, and the fetch/download/playback/authentication paths. Ran the real Qt widgets
offscreen with isolated settings, 60 synthetic tracks, and a 640×480 test image;
inspected rendered screenshots and exercised selection, filtering, and timeline input.
Checked preferences in English, German, Croatian, Ukrainian, and Chinese, plus a larger font.
The historical review in `documents/15_uireview20260804.md` was checked against current code;
previously fixed issues such as missing volume controls are not repeated.

These are local UI probes and code traces, not a live Last.fm/YouTube end-to-end run or
a screen-reader audit. Pixel measurements are specific to the offscreen Qt/Fusion setup;
the reproduced layout and interaction failures do not depend on live services.

HIGH means a major obstruction to normal use or unexpected loss of saved state.
MEDIUM means a confirmed interaction, feedback, or accessibility defect.
LOW means a clarity or convenience improvement. There are 15 findings: 3 HIGH,
9 MEDIUM, and 3 LOW. Suggested fixes below are proposals, not implemented changes.

## Findings

### 1. HIGH — Artist artwork expands the entire playback row and collapses the library — Fixed in v0.0.162

Evidence: `my_lastfm_player/ui/main_window.py:110`, `:145`, `:412`, and `:481`.
The image label is expanding in both directions with no maximum size. Its scaled
pixmap contributes to its size hint, while the image group and playback group share
one horizontally arranged row without a vertical bound. Showing artwork therefore
increases both groups' height and spreads the transport controls far apart.

| Window size | Artwork | Playback group height | Track table height |
|---|---|---:|---:|
| 1120×720 | Hidden | 171 px | 113 px |
| 1120×720 | Loaded | 221 px | 70 px |
| 1600×1000 | Hidden | 171 px | 393 px |
| 1600×1000 | Loaded | 494 px | 70 px |

At the larger size, the library shows roughly two rows while artwork and empty space
dominate. The permanently visible log also takes 192 px in that probe, even when empty;
when artwork is unavailable, its empty group box still occupies horizontal space.

Improve: use a compact transport area whose height follows its controls, with a bounded
artwork slot independent of pixmap size hints. Preserve aspect ratio, avoid unlimited
upscaling, and give surplus height to the library. Make diagnostic output collapsible;
use a compact artwork placeholder or hide the empty group without moving transport buttons.

Acceptance: loading, clearing, and replacing portrait/landscape artwork must not increase
transport height or shrink the library. Enlarging the window must reveal more track rows.

Fixed in v0.0.162: artwork is bounded to 120×120 pixels in a compact 180-pixel-wide
panel, the playback group has a fixed vertical policy, and surplus width goes to playback.
The artist panel is hidden when it has no valid image. A Qt geometry regression test verifies
that loading artwork changes neither playback-group height nor track-table height.

### 2. HIGH — Closing the app deletes saved library state and authentication by default

Evidence: `my_lastfm_player/settings.py:101`, `my_lastfm_player/controller.py:233`,
and `my_lastfm_player/storage.py:129`.
`keep_data_on_quit()` defaults to false; closing calls `wipe()`, deleting saved track
lists/journals, lookup/download caches, and credentials. Audio files are deliberately
retained. The preference only says “Keep cached data after quitting,” and closing the
window gives no explanation of the loss of library state or authentication.

Improve: retain data by default. Make deletion an explicit privacy action or opt-in mode,
with an exact explanation of what is deleted and what remains. Preserve an intentionally
selected privacy mode when changing defaults.

Acceptance: a fresh profile can fetch, close, and reopen without losing its saved library
or session. Explicit cleanup has a clear scope and predictable result.

### 3. HIGH — Users cannot stop the automatic YouTube workflow from the UI

Evidence: `my_lastfm_player/ui/main_window.py:165`, `:314`, and `:573`;
`my_lastfm_player/controller.py:686` and `:1402`.
The source panel's Pause/Stop buttons affect only the Last.fm fetch. YouTube lookup and
downloads continue independently; once fetching ends, those buttons are disabled.
`download_stop_requested` exists and is connected, but no button or menu action emits it.
`set_download_active()` only records a flag. Changing the username can retire background
work, but it is not a discoverable way to stop the current queue while keeping its view.

Improve: expose explicit workflow pause/stop controls and distinguish their scope from
playback controls. Stop must cancel queued and active work across the intended stages,
retain completed items, and show “Stopping…” until cancellation finishes. Explain near
Fetch that discovering tracks also starts YouTube checks and downloads.

Acceptance: stop with five operations active, verify that no new operations start, and
resume remaining items without changing usernames or restarting the app.

### 4. MEDIUM — Some network operations still block the UI thread

Evidence: `my_lastfm_player/controller.py:376`, `:585`, `:1268`, and `:1556`;
`my_lastfm_player/ui/preferences_dialog.py:233` and `:245`;
`my_lastfm_player/scrobbling.py:98` and `:117`.
The Fetch handler performs Last.fm count/preflight requests before starting its worker.
Authentication, now-playing updates, and scrobble submission also call network-backed
services directly from UI handlers. A slow response blocks repainting, controls, and
username editing despite the input remaining enabled.

Improve: move these calls to background tasks, retain generation checks for account changes,
and show a cancellable busy state immediately. Scrobbling should not delay local playback.

Acceptance: delayed/failing service doubles must leave a UI heartbeat, typing, playback
controls, and cancellation responsive throughout preflight and authentication.

### 5. MEDIUM — The playback timeline supports clicks but breaks dragging and keyboard seeking

Evidence: `my_lastfm_player/ui/main_window.py:446`, `:961`, and `:997`.
The event filter consumes every left-button press, including presses on the slider handle,
preventing Qt from beginning its normal drag. Keyboard changes are not connected to seeking;
only `sliderReleased` and the mouse-press filter emit the request. Playback updates also
overwrite the slider value without checking whether a user is interacting with it.

Probe: Right changed the displayed value from 30000 to 30001 ms but emitted no seek request.
A press-drag-release from one-quarter to three-quarters stayed at the first position;
`isSliderDown()` remained false.

Improve: preserve normal handle dragging, implement groove-click seeking separately, and
route keyboard actions to the backend. Do not overwrite an active drag with position updates.

Acceptance: mouse click, drag, arrows, Page Up/Down, and Home/End all move actual playback
as expected, including while position signals arrive.

### 6. MEDIUM — Background table refreshes discard the user's selection

Evidence: `my_lastfm_player/ui/track_table_model.py:112`;
`my_lastfm_player/controller.py:1080`, `:1142`, and `:1190`.
Partial fetch and worker-completion handlers replace the full model via `beginResetModel()`.
Selection is not restored. In the probe, selecting Track 5 and updating with the identical
list changed `selected_track()` to `None`. A subsequent Play can choose the fallback track
instead of the one the user selected.

Improve: insert/update rows incrementally, or preserve selection, current index, and scroll
position by stable track key across unavoidable resets.

Acceptance: select and scroll during incremental fetch, lookup completion, and download
completion; selection must survive while that track remains present, including under filtering.

### 7. MEDIUM — Paused playback still presents “Pause” and disables “Play”

Evidence: `my_lastfm_player/controller.py:820`;
`my_lastfm_player/ui/main_window.py:980` and `:1070`.
The Pause handler toggles pause/resume internally, but never changes its label or the
transport state. Play remains disabled while paused. Only a log/status message explains
the change, so the visible action for resuming playback is still labelled “Pause.”

Improve: model idle, preparing, playing, and paused states explicitly. Use a Play/Pause
toggle or change Pause to Resume; show the state near the current track and retain it
when the language changes.

Acceptance: each state exposes the correct action, including after failed playback and
language switching. A paused user can identify Resume without reading the log.

### 8. MEDIUM — Track failures lack an accessible explanation and clear recovery action

Evidence: `my_lastfm_player/ui/track_table_model.py:65`;
`my_lastfm_player/ui/main_window.py:398`;
`my_lastfm_player/controller.py:1115` and `:1416`.
Rows display status but do not expose `Track.error` as details or a tooltip. Per-track
failures are logged as ordinary status updates. The context menu always offers “Retry
Download,” even for a failed lookup or an already downloaded track, and is the only
explicit retry action. Users cannot readily determine why a row failed or what retry does.

Improve: expose error details and a visible, keyboard-reachable retry action. Tailor its
label/enabled state to lookup versus download failures, and offer a way to find failed rows.
Keep details attached to their track even after routine log messages have scrolled away.

Acceptance: lookup failure, no match, and download failure each explain their cause and
appropriate next action; successful rows do not suggest a misleading retry.

### 9. MEDIUM — One progress bar mixes unrelated concurrent stages

Evidence: `my_lastfm_player/controller.py:911`, `:1244`, and `:1253`;
`my_lastfm_player/ui/main_window.py:780`.
All current-user workers write directly to the same percentage and label, with no stage
aggregation. A lookup update at 80% followed by a download update at 10% changes the bar
to 10%; a single worker failure sets it to “Failed” even if other work is continuing.
The percentage does not tell the user how much of the library is ready to play.

Improve: show separate discovery/check/download counts, or a summary with discovered,
active, ready, and failed counts. Represent indeterminate discovery honestly and distinguish
partial failures from a stopped workflow. Keep diagnostic messages in the expandable log.

Acceptance: interleaved progress and failure signals cannot falsely indicate overall
completion or failure; active work and remaining items stay understandable.

### 10. MEDIUM — Long content and larger fonts can force windows beyond useful dimensions

Evidence: `my_lastfm_player/ui/main_window.py:444`, `:459`, and `:746`;
`my_lastfm_player/ui/preferences_dialog.py:224`.
The now-playing label has no elision/wrapping policy that bounds its minimum width. A long
synthetic title expanded the 1120 px window to 1471 px. Preferences forces its minimum
height to its content hint and has no scroll container; at a 16-point font it measured
619×771 before window decorations, exceeding a 768 px-high desktop.

Improve: elide now-playing text with full details available on demand, permit transport
reflow at narrow widths, and make preferences scroll within available screen geometry.
Avoid treating a fixed pixel dimension as a complete solution to finding 1.

Acceptance: long artist/title strings and translated labels remain usable on a 1366×768
desktop with larger fonts; Close and essential playback controls remain reachable.

### 11. MEDIUM — Keyboard and accessible labelling support is incomplete

Evidence: `my_lastfm_player/ui/main_window.py:100`, `:209`, `:320`, and `:358`;
`my_lastfm_player/ui/preferences_dialog.py:89` and `:97`.
F5 is implemented and ordinary Qt tab navigation exists, but there are no application
shortcuts for filter focus, play/pause, or quit. Input labels have no buddies, and controls
such as the timeline lack explicit accessible names. The clickable artist image has
`NoFocus` and a mouse handler only, so its Last.fm link is unavailable from the keyboard.

Improve: add conventional shortcuts and label associations, expose names and values for
sliders, and make the artist link a focusable action. Scope playback shortcuts so typing
spaces in username/filter fields continues to work.

Acceptance: fetch, filter, select, play, pause, seek, retry, open the artist page, and close
preferences can be completed without a mouse. Verify the resulting names with a screen reader.

### 12. MEDIUM — Authentication failure feedback is overwritten immediately

Evidence: `my_lastfm_player/ui/preferences_dialog.py:181` and `:233`.
When `start_web_auth()` returns no URL, the dialog sets “Could not start authentication”
and immediately calls `_refresh()`, which replaces it with “Not connected.” A failed-auth
service double reproduced this. The browser-opening return value is also ignored, so an
unsuccessful launch can leave instructions claiming that the browser opened.

Improve: retain actionable failure text independently of the connection state. Check the
browser launch result and provide a selectable authorization link and a retry action.

Acceptance: service failure and browser-launch failure each leave a persistent explanation;
retrying successfully clears it without hiding unresolved authorization instructions.

### 13. LOW — A filter with no matches looks like an unexplained empty library

Evidence: `my_lastfm_player/ui/main_window.py:395` and `:536`.
The empty-state label depends only on the source track count, not the filtered row count.
Filtering the 60-track probe to zero matches left a blank table with “Playlist: 60 titles”
and no explanation. Both an inline clear icon and a Reset button exist, but no message
connects those controls to the empty result.

Improve: show “0 of 60 tracks — no matches” with Clear filter, separate from first-run,
loading, empty Last.fm library, and fetch-error states.

Acceptance: filtering to zero and clearing the filter updates the count and explanation
without changing the underlying library.

### 14. LOW — Table metadata is hard to interpret and truncated text cannot be inspected easily

Evidence: `my_lastfm_player/ui/track_table_model.py:16`, `:65`, `:160`, and `:212`;
`my_lastfm_player/ui/main_window.py:380` and `:398`.
“Loved at” displays raw values such as `20090806-090753`; “File” displays format/bitrate,
not a filename. Artist and title columns elide text without a full-text tooltip, and the
row menu offers no copy/details/file-location action.

Improve: format dates for the active locale while sorting on a separate raw value; rename
File to Format or Quality. Provide full-text details and copy/open-file-location actions.

Acceptance: dates remain chronologically sortable, long titles can be read in full, and
a downloaded track's actual file is discoverable from its row.

### 15. LOW — Preferences does not explain saving or consistently translate standard buttons

Evidence: `my_lastfm_player/ui/preferences_dialog.py:120`, `:271`, `:275`, and `:278`;
`my_lastfm_player/controller.py:551`; `my_lastfm_player/i18n.py:37`.
Preferences writes changes immediately, but only presents Close with no saving explanation.
Browser-cookie settings are applied to services when the dialog closes, which is not
explained. In the rendered German dialog, custom labels were German but the standard
button still read “Close”; the translation manager loads only the application catalog.

Improve: explicitly explain automatic saving and when changes affect running/new work,
or provide consistent Apply/Cancel semantics. Load the matching Qt widget translations
or translate standard button text explicitly.

Acceptance: closing or pressing Escape has documented, consistent effects; standard
buttons match the selected UI language, including in About and license dialogs.

## Suggested implementation order

1. Fix the artwork/transport geometry and long-content constraints (1, 10). Give the
   library most of the window and make the log an optional detail panel.
2. Resolve retention and workflow control (2, 3), then remove blocking UI calls (4).
3. Correct transport input/state and preserve selection (5–7).
4. Improve per-track recovery, concurrent progress, keyboard access, and authentication
   feedback (8, 9, 11, 12).
5. Finish search states, metadata presentation, and settings clarity (13–15).

Keep existing strengths: editable usernames with generation-scoped worker handling,
the 1–5 parallel-work preference with default 5, volume/mute persistence, F5 refresh,
sort/filter support, selectable themes/languages, and remembered window geometry.
Turn the acceptance checks into focused regression tests when implementing the fixes;
the current automated gate alone does not exercise these usability outcomes.

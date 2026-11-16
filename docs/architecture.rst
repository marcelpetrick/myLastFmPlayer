Architecture
============

myLastFmPlayer is a single-process Linux desktop application written in Python
with a PyQt6 GUI. The controller coordinates the UI and operation lifecycle;
short-lived workers on owned threads bridge domain services and storage without
giving those services knowledge of the Qt interface.

The diagrams below follow the **C4 model** (Simon Brown): each level zooms one
step further in, from the system boundary down to individual components.

Level 1 — System Context
-------------------------

Who uses the system, and which external systems does it depend on?

.. graphviz::
   :caption: System context — myLastFmPlayer in its environment

   digraph system_context {
       graph [rankdir=TB, splines=ortho, pad=0.6, nodesep=1.0, ranksep=1.2];
       node [fontname="Helvetica", fontsize=11, margin="0.3,0.15"];
       edge [fontname="Helvetica", fontsize=9];

       user [label="Last.fm User\n[Person]\n\nA Linux desktop user who has\nloved tracks on Last.fm.",
             shape=box, style="rounded,filled",
             fillcolor="#08427b", fontcolor=white, color="#052e56"];

       app [label="myLastFmPlayer\n[Software System]\n\nFetches a user's loved tracks, resolves\nthem to YouTube audio, downloads audio\nfiles, and plays them locally with\noptional Last.fm scrobbling.",
            shape=box, style="rounded,filled",
            fillcolor="#1168bd", fontcolor=white, color="#0b4884"];

       lastfm_web [label="Last.fm Website\n[External System]\n\nArtist pages opened by the user\nand inspected for preview images.",
                   shape=box, style="rounded,filled",
                   fillcolor="#999999", fontcolor=white, color="#6b6b6b"];

       lastfm_api [label="Last.fm API\n[External System]\n\nLoved-track and artist metadata\nplus authenticated now-playing,\nscrobbling, and unlove.",
                   shape=box, style="rounded,filled",
                   fillcolor="#999999", fontcolor=white, color="#6b6b6b"];

       youtube [label="YouTube\n[External System]\n\nSearched by yt-dlp for the\nbest-matching audio stream\nfor each track.",
                shape=box, style="rounded,filled",
                fillcolor="#999999", fontcolor=white, color="#6b6b6b"];

       user -> app       [label="clicks, playback controls,\nusername input"];
       app -> lastfm_api [label="requests API (loved tracks + artist info)\npylast API (auth, now-playing,\nscrobble, unlove)"];
       app -> lastfm_web [label="artist pages in a Firefox private window\n(default browser as fallback)"];
       app -> youtube    [label="yt-dlp search + audio stream download"];
   }

Level 2 — Container View
-------------------------

What are the major deployable or runnable parts, and what technology do they use?

.. graphviz::
   :caption: Container view — processes, external tools, and storage

   digraph containers {
       graph [rankdir=LR, splines=ortho, pad=0.5, nodesep=0.8, ranksep=1.3];
       node [fontname="Helvetica", fontsize=10, margin="0.25,0.12"];
       edge [fontname="Helvetica", fontsize=9];

       user [label="Last.fm User\n[Person]",
             shape=box, style="rounded,filled",
             fillcolor="#08427b", fontcolor=white, color="#052e56"];

       subgraph cluster_system {
           label="myLastFmPlayer [Software System]";
           style=dashed; color="#888888"; fontname="Helvetica"; fontsize=11;

           desktop [label="Desktop Application\n[Container: Python 3.14+ / PyQt6]\n\nAll UI, business logic, and service\norchestration. Single OS process\nlaunched via my-lastfm-player CLI.",
                    shape=box, style="rounded,filled",
                    fillcolor="#1168bd", fontcolor=white, color="#0b4884"];

           json_store [label="JSON Data Store\n[Container: File System]\n\n~/.local/share/myLastFmPlayer/\nTrack lists, lookup cache,\ndownload cache, credentials.",
                       shape=cylinder, style="filled",
                       fillcolor="#1168bd", fontcolor=white, color="#0b4884"];

           audio_files [label="Downloaded Audio\n[Container: File System]\n\n~/.local/share/myLastFmPlayer/downloads/\naudio files named after resolved tracks.",
                        shape=cylinder, style="filled",
                        fillcolor="#1168bd", fontcolor=white, color="#0b4884"];

           qt_settings [label="Platform Settings\n[Container: QSettings]\n\nOS-native key-value store.\nAppearance, playback, session,\nscrobbling, YouTube, and\nretention preferences.",
                        shape=cylinder, style="filled",
                        fillcolor="#1168bd", fontcolor=white, color="#0b4884"];
       }

       ytdlp  [label="yt-dlp\n[External CLI tool]\n\nYouTube search and\naudio stream download.",
               shape=box, style="rounded,filled",
               fillcolor="#999999", fontcolor=white, color="#6b6b6b"];

       ffmpeg [label="ffmpeg + ffprobe\n[External CLI tools]\n\nAudio conversion, post-processing,\nand metadata probing.",
               shape=box, style="rounded,filled",
               fillcolor="#999999", fontcolor=white, color="#6b6b6b"];

       lastfm_web [label="Last.fm Website\n[External System]",
                   shape=box, style="rounded,filled",
                   fillcolor="#999999", fontcolor=white, color="#6b6b6b"];

       lastfm_api [label="Last.fm API\n[External System]",
                   shape=box, style="rounded,filled",
                   fillcolor="#999999", fontcolor=white, color="#6b6b6b"];

       user     -> desktop    [label="interactions"];
       desktop  -> json_store [label="read/write\ntracks and caches"];
       desktop  -> audio_files[label="reads for local playback\n(QMediaPlayer)"];
       desktop  -> qt_settings[label="load/save\npreferences"];
       desktop  -> ytdlp      [label="subprocess\n(search + download)"];
       desktop  -> ffmpeg      [label="metadata probe\n(ffprobe)"];
       ytdlp    -> ffmpeg      [label="post-process\naudio"];
       ytdlp    -> audio_files [label="writes audio"];
       desktop  -> lastfm_api  [label="requests API calls\n(loved tracks + artist info)\npylast API calls\n(auth, scrobble, unlove)"];
       desktop  -> lastfm_web  [label="artist page HTML (preview image);\nfirefox --private-window links"];
   }

Level 3 — Component View
-------------------------

What are the principal building blocks inside the desktop process?

.. graphviz::
   :caption: Component view — modules inside the PyQt6 process

   digraph components {
       graph [rankdir=TB, splines=ortho, pad=0.5, nodesep=0.5, ranksep=0.8];
       node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=9,
             fillcolor="#dae8fc", color="#6c8ebf", margin="0.2,0.1"];
       edge [fontname="Helvetica", fontsize=8, color="#555555"];

       main [label="main.py\n[Component: Startup]\n\nBootstraps QApplication;\napplies theme + language;\nrestores session; wires\nMainWindow to controller.",
             fillcolor="#e8f0fe", color="#5577cc"];

       subgraph cluster_ui {
           label="UI Layer";
           style=filled; fillcolor="#f0f0f8"; color="#aaaacc";
           fontname="Helvetica"; fontsize=10;

           window      [label="MainWindow\n[PyQt6 QMainWindow]\n\nMenus, filterable track table,\ncontext menu (retry, unlove),\nplayback controls, progress."];
           table_model [label="TrackTableModel\n[QAbstractTableModel]\n\nAdapter between the\ntrack list and the\nQTableView widget."];
           prefs       [label="PreferencesDialog\n[QDialog]\n\nTheme, language, Last.fm auth,\nscrobbling, concurrency, cookie\nbrowser, data retention."];
           painted     [label="icons.py + flags.py\n[QPainter]\n\nMenu icons and language\nflags drawn in code."];
       }

       controller [label="ApplicationController\n[Component: Coordinator]\n\nThe single cross-layer hub.\nHandles UI signals, starts workers,\nscopes results by username and\ngeneration, drives playback.",
                   fillcolor="#fff2cc", color="#d6b656", margin="0.3,0.15"];

       subgraph cluster_workers {
           label="Background Workers (QThread)";
           style=filled; fillcolor="#f5fff9"; color="#6b8f7a";
           fontname="Helvetica"; fontsize=10;

           pool       [label="WorkerThreadPool\n[QThread owner]\n\nmoveToThread + start;\nretires threads on finished;\nbounded join on quit."];
           fetch_w    [label="FetchLovedTracksWorker\n[QObject on QThread]\n\nFetches Last.fm pages; emits\nprogress + track batches per page;\nsupports pause and stop."];
           lookup_w   [label="LookupTracksWorker\n[QObject on QThread]\n\nResolves tracks that need\na YouTube URL; cancellable."];
           download_w [label="DownloadTracksWorker\n[QObject on QThread]\n\nDownloads tracks with a URL;\nreports per-track progress;\ncancellable."];
           image_w    [label="ArtistImageWorker\n[QObject on QThread]\n\nLoads artist metadata\nand preview image."];
           call_w     [label="BackgroundCallWorker\n[QObject on QThread]\n\nOne blocking call: count preflight,\nsession check, now-playing,\nscrobble, unlove."];
       }

       subgraph cluster_services {
           label="Domain / Service Layer";
           style=filled; fillcolor="#f9f9f9"; color="#aaaaaa";
           fontname="Helvetica"; fontsize=10;

           scraper     [label="LastFmLovedTracksScraper\n[HTTP Client]\n\nFetches Last.fm Web API pages;\nretries with a fixed delay;\nwaits between pages."];
           artist_info [label="LastFmArtistInfoClient\n[HTTP Client]\n\nFetches artist.getInfo metadata;\nloads artist page preview images\nwith a stdlib HTML parser."];
           resolver    [label="YouTubeResolver\n[yt-dlp wrapper]\n\nChecks lookup-cache first;\nruns concurrent yt-dlp searches over a\nquery ladder; updates cache."];
           download_mgr[label="DownloadManager\n[yt-dlp wrapper]\n\nConcurrent audio downloads with\nretry + jitter backoff; each retry forces\nanother YouTube player client; ffprobe."];
           work_limiter[label="YouTubeWorkLimiter\n[Concurrency coordinator]\n\nShares 1–5 process slots across lookup\nand download; serializes per work key;\ncooperative cancellation."];
           playback    [label="PlaybackService\n[Qt Multimedia]\n\nWraps QMediaPlayer;\nplay, pause, seek, stop,\nvolume, mute."];
           scrobbling  [label="ScrobblingService\n[pylast]\n\nLast.fm desktop auth;\nnow-playing, scrobble,\nlove and unlove."];
           deps        [label="check_external_dependencies\n[shutil.which]\n\nVerifies yt-dlp, ffmpeg,\nand ffprobe are present on PATH\nat application startup."];
       }

       subgraph cluster_data {
           label="Data Layer";
           style=filled; fillcolor="#fff8f0"; color="#ccaa88";
           fontname="Helvetica"; fontsize=10;

           repo     [label="JsonTrackRepository\n[File I/O]\n\nThread-safe JSON store backed\nby RLock; atomic writes via\ntemp-file rename; fsynced journal."];
           models   [label="Track / TrackStatus\n[Immutable dataclass]\n\nCache-key identity and\nmerge rules."];
           settings [label="AppSettings\n[QSettings wrapper]\n\nTyped accessors and defaults\nfor every persisted preference."];
           creds    [label="lastfm_api_credentials\n[Env / Bundled]\n\nLast.fm API key + secret;\nenv-var overrides bundled\ndefaults."];
       }

       subgraph cluster_cross {
           label="Cross-Cutting";
           style=filled; fillcolor="#fdf6ff"; color="#ccaadd";
           fontname="Helvetica"; fontsize=10;

           i18n    [label="TranslationManager\n[QTranslator wrapper]\n\nLoads .qm files at runtime;\nEnglish plus four translations."];
           themes  [label="apply_theme\n[QPalette builder]\n\nFusion style with\nLight / Dark / Lilac / Mint."];
           log_cfg [label="configure_logging\n[stdlib logging]\n\nProcess-wide logging\nto stdout at INFO."];
           qt_sig  [label="qt_signal.pyqtSignal\n[Typing shim]\n\nPyQt's pyqtSignal at runtime;\ncorrected signature for\nthe type checker."];
       }

       main -> settings;
       main -> i18n;
       main -> themes;
       main -> log_cfg;
       main -> window;
       main -> controller;

       window -> table_model;
       window -> painted;
       window -> controller   [label="Qt signals"];
       controller -> prefs    [label="opens"];
       prefs  -> scrobbling   [label="auth calls\n(daemon thread)"];

       controller -> repo      [label="load / save"];
       controller -> playback;
       controller -> deps;
       controller -> settings;
       controller -> creds;
       controller -> window    [label="update UI"];
       controller -> pool      [label="start workers"];

       pool -> fetch_w;
       pool -> lookup_w;
       pool -> download_w;
       pool -> image_w;
       pool -> call_w;

       fetch_w    -> scraper;
       fetch_w    -> repo;
       image_w    -> artist_info;
       call_w     -> scraper     [label="count preflight"];
       call_w     -> scrobbling;
       lookup_w   -> resolver;
       download_w -> download_mgr;
       resolver   -> work_limiter;
       download_mgr -> work_limiter;
       resolver   -> repo;
       download_mgr -> repo;
       repo       -> models;
       window     -> qt_sig     [style=dashed];
   }

Track Lifecycle
---------------

A ``Track`` moves through a fixed set of states from discovery to local
playback. Transitions are persisted immediately through the repository so
progress survives a restart.

.. graphviz::
   :caption: Track state machine

   digraph track_states {
       graph [rankdir=LR, pad=0.4, nodesep=0.6, ranksep=1.0];
       node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=10,
             fillcolor="#eaf4fb", color="#6699bb"];
       edge [fontname="Helvetica", fontsize=9, color="#446688"];

       FETCHED     [label="FETCHED\n(loved by user on Last.fm)"];
       SEARCHING   [label="SEARCHING\n(yt-dlp lookup in progress)"];
       LOOKUP_FAILED [label="LOOKUP FAILED\n(transient lookup error)",
                      fillcolor="#fde8e8", color="#b05050"];
       QUEUED      [label="QUEUED\n(YouTube URL resolved)"];
       DOWNLOADING [label="DOWNLOADING\n(audio download in progress)"];
       DOWNLOADED  [label="DOWNLOADED\n(audio on disk — ready to play)",
                    fillcolor="#d5f0d5", color="#5a9a5a"];
       NOT_FOUND   [label="NOT FOUND\n(no YouTube result)",
                    fillcolor="#fdf0d5", color="#b89050"];
       FAILED      [label="FAILED\n(download error after retries)",
                    fillcolor="#fde8e8", color="#b05050"];

       FETCHED     -> SEARCHING   [label="lookup starts\n(no cache hit)"];
       FETCHED     -> QUEUED      [label="lookup-cache hit\n(URL already known)"];
       FETCHED     -> DOWNLOADED  [label="download-cache hit\n(file already local)"];
       SEARCHING   -> QUEUED      [label="URL resolved\n(any query in the ladder)"];
       SEARCHING   -> LOOKUP_FAILED [label="lookup command failed"];
       SEARCHING   -> NOT_FOUND   [label="every query missed"];
       SEARCHING   -> FETCHED     [label="cancelled", style=dotted];
       LOOKUP_FAILED -> FETCHED   [label="app start / user retries", style=dashed];
       QUEUED      -> DOWNLOADING [label="download starts"];
       DOWNLOADING -> DOWNLOADED  [label="audio written\n(any client in the ladder)"];
       DOWNLOADING -> FAILED      [label="every client failed"];
       DOWNLOADING -> QUEUED      [label="cancelled", style=dotted];
       NOT_FOUND   -> SEARCHING   [label="re-checked while under\nthe attempt bound",
                                   style=dashed];
       NOT_FOUND   -> FETCHED     [label="app start / user retries", style=dashed];
       FAILED      -> DOWNLOADING [label="next download pass", style=dashed];
       FAILED      -> QUEUED      [label="app start / user retries\n(URL known; else FETCHED)",
                                   style=dashed];
   }

Recovering Stuck Tracks
-----------------------

``NOT FOUND`` and ``FAILED`` are verdicts about YouTube, not about the track, and
YouTube changes its mind. Both states are therefore treated as provisional.

YouTube gates some of its internal player clients behind a proof-of-origin token.
A gated client answers with no media formats at all, so ``yt-dlp`` reports
*"Requested format is not available"* whatever format is asked for, or serves a
``403`` on the media fetch. Which clients are gated changes over time, so no single
choice stays correct. ``DownloadManager`` therefore treats its retries as a ladder:
the first attempt uses ``yt-dlp``'s own client rotation, and each retry forces a
different client family. Repeating one client would only reproduce the same refusal.

Lookup has the same shape. A single ``artist title`` search misses when the Last.fm
artist field carries store suffixes or decorative symbols, so ``YouTubeResolver``
walks a query ladder — exact, artist stripped of that noise, then title alone — and
searches flat so a gated client cannot break the search itself. An empty result is
counted as one bounded attempt rather than a permanent verdict, with the count kept
in ``lookup-cache.json`` so it survives a restart.

On startup the controller sweeps whatever the previous run gave up on: ``NOT FOUND``
tracks are cleared from the lookup cache and re-searched, while ``FAILED`` and
``LOOKUP FAILED`` tracks go back to the download queue when their URL is known and to
lookup otherwise. ``Track.merge_preserving`` normally refuses to
move a status backwards, which would discard such a recovery, so it makes one
exception: a track may leave ``NOT FOUND`` once a lookup finally produces a URL.

Worker Lifecycle
----------------

Every background job of the controller runs on a ``QThread`` owned by
``WorkerThreadPool``, which uses Qt's ``moveToThread`` pattern, quits and deletes the
thread when the worker emits ``finished``, and on quit joins every remaining thread
within a bounded wait before Qt destroys the window. Results reach the main thread
through queued Qt signals, keeping UI handlers responsive.

Paginated fetching, lookup, download (including ``ffprobe`` probing), and artwork
retrieval use their dedicated workers. Short blocking service calls — the loved-track
count preflight, stored-session verification, now-playing updates, scrobble
submission, and unlove — run through ``BackgroundCallWorker``, which suppresses
delivery once cancelled. ``PreferencesDialog`` runs its authentication calls through
the same worker class on short-lived daemon Python threads. Late preflight results are
discarded after cancellation or a username-generation change; authentication
generations likewise prevent an old verification from reconnecting a deliberately
disconnected session.

Inside the lookup and download workers, a ``ThreadPoolExecutor`` fans out per-track
work; each ``yt-dlp`` or ``ffprobe`` subprocess first acquires a ``YouTubeWorkLimiter``
slot.

Last.fm pages feed YouTube lookup as they arrive, and resolved tracks feed downloading
without waiting for the lookup batch to finish. One shared coordinator, restricted to
one through five operations and defaulting to five, caps all lookup and download
subprocesses together. Each completed track is first written to an append-only, ``fsync``-ed journal; the
full JSON library and shared caches are compacted once at the end of a run.

When the username changes, the controller cancels the old user's operation-owned stop
events. Running ``yt-dlp``/``ffprobe`` process groups are terminated promptly, queued
items return to retryable states (cancelled lookups to ``FETCHED``, cancelled
downloads to ``QUEUED``), and completed journal entries remain available.
Username- and generation-scoped signal filtering prevents late updates from replacing
the new user's UI state, while a per-target coordinator key prevents two overlapping
users from writing the same audio file concurrently.

The visible **Stop YouTube** action cancels lookup and download work as one workflow.
The button remains in a stopping state until every owned worker has completed cleanup,
then becomes **Resume YouTube** when retryable work remains. Resume starts only the
unresolved or queued entries; completed tracks are never discarded. Fetch has separate
pause and stop controls because Last.fm discovery is an independent operation.

.. graphviz::
   :caption: Background worker lifecycle

   digraph worker_lifecycle {
       graph [rankdir=LR, pad=0.4, nodesep=0.7, ranksep=1.0];
       node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=10,
             fillcolor="#f5fff9", color="#6b8f7a"];
       edge [fontname="Helvetica", fontsize=9, color="#466354"];

       signal  [label="UI Signal\n(e.g. fetch clicked)"];
       ctrl    [label="ApplicationController"];
       pool    [label="WorkerThreadPool"];
       thread  [label="QThread"];
       worker  [label="Worker\n(Fetch / Lookup / Download /\nArtistImage / BackgroundCall)"];
       service [label="Service\n(Scraper / Resolver / DownloadManager)"];
       repo    [label="JsonTrackRepository"];
       ui      [label="MainWindow"];

       signal  -> ctrl;
       ctrl    -> worker   [label="create + connect\nscoped signals"];
       ctrl    -> pool     [label="start(worker)"];
       pool    -> thread   [label="create, moveToThread,\nstart"];
       thread  -> worker   [label="started -> run()"];
       worker  -> service  [label="calls service methods"];
       service -> repo     [label="journal / save tracks"];
       worker  -> ctrl     [label="progress + result signals\n(queued connection)"];
       worker  -> thread   [label="finished -> quit"];
       pool    -> thread   [label="delete on finished;\nbounded join on quit"];
       ctrl    -> repo     [label="persist state"];
       ctrl    -> ui       [label="refresh table\n+ status bar"];
   }

Persisted Data
--------------

All mutable application data lives under ``$XDG_DATA_HOME/myLastFmPlayer/``
(defaulting to ``~/.local/share/myLastFmPlayer/`` when ``XDG_DATA_HOME`` is
not set). Snapshot, cache, and credential writes are atomic: data is first written
to a temp file in the same directory and then renamed, preventing corrupt reads on
crash. Journal appends are flushed and ``fsync``-ed.

Appearance and behaviour preferences are stored separately in the
platform-native ``QSettings`` store (``~/.config/`` on Linux).

.. list-table:: Storage layout
   :header-rows: 1
   :widths: 38 18 44

   * - Path
     - Format
     - Contents
   * - ``tracks/<username>.json``
     - JSON array
     - Full track list including status, YouTube URL, local path, and error
       for each user; one file per username.
   * - ``tracks/<username>.updates.jsonl``
     - JSON Lines
     - Append-only per-track updates written during active work; replayed on load and
       compacted into the full track list after a completed run.
   * - ``lookup-cache.json``
     - JSON array
     - Track snapshots with a resolved YouTube URL or a bounded ``NOT FOUND``
       state, keyed on load by ``Track.cache_key`` (artist and title joined by
       ``\x1f``); consulted before invoking ``yt-dlp`` search.
   * - ``download-cache.json``
     - JSON array
     - Downloaded-track snapshots including the local path, keyed on load by
       ``Track.cache_key``; avoids re-downloading when the audio file still exists.
   * - ``lastfm-credentials.json``
     - JSON object
     - Authorized Last.fm username, session key, and scrobbling choice obtained
       through the desktop auth flow; required for now-playing, scrobbling, and
       unlove.
   * - ``downloads/``
     - Directory
     - Downloaded audio files named ``<Artist> - <Title>``.
   * - QSettings (OS store)
     - Platform-native
     - Theme, UI language, volume, mute, randomized continuation, last username,
       window geometry, scrobbling enabled, YouTube-work concurrency, yt-dlp cookie
       browser, and keep-data-on-quit flag. Retention is enabled by default; opting
       out removes track lists, journals, caches, and credentials on quit but not
       downloaded audio.

Key Design Decisions
--------------------

**Single controller, no service-to-service calls.**
``ApplicationController`` is the only class that knows about all others.
Services such as ``LastFmLovedTracksScraper``, ``YouTubeResolver``,
``DownloadManager``, ``PlaybackService``, and ``ScrobblingService`` do not call
each other and do not touch widgets; ``YouTubeResolver`` and ``DownloadManager``
only share the injected ``YouTubeWorkLimiter`` and persist through the
repository. Each is individually testable without a running application.

**Workers are stateless and short-lived.**
A fresh worker object is created for every operation, given references to the
relevant service and the repository, and discarded after the ``finished``
signal. The repository is the single source of truth; workers read from it and
write back through it, but never own any persistent state themselves.

**External tools as subprocesses, validated at startup.**
``yt-dlp``, ``ffmpeg``, and ``ffprobe`` are invoked via subprocesses rather than
linked as Python libraries. This keeps the runtime dependency surface small and
lets users upgrade CLI tools independently of the application version.
``check_external_dependencies`` verifies all three are on ``PATH`` at startup
and surfaces a warning in the UI if any are missing.

**Last.fm Web API for loved tracks, pylast for account writes.**
Loved-track fetching uses Last.fm's ``user.getLovedTracks`` JSON API through
``requests`` and the bundled or environment-provided application API key. Artist
preview metadata uses ``artist.getInfo`` and, when needed, a small stdlib HTML
parser for page image metadata. Desktop authentication, now-playing, scrobble,
and unlove calls remain on ``pylast`` because they require the user's Last.fm
session key.

**Private artist-page launches prefer Firefox.**
Clicking the artist preview opens the Last.fm artist page with
``firefox --private-window <url>``. The application calls Firefox directly for
this path because ``xdg-open`` and desktop portals do not provide a portable
private-window option. When Firefox cannot be started, the page opens in the
default browser through ``QDesktopServices`` instead of failing.

**QThread + moveToThread, not QRunnable.**
The controller's background work uses ``QThread`` with worker objects moved to
the thread rather than ``QRunnable``. This makes progress and completion signals
cross back to the Qt event loop naturally through Qt's queued-connection
mechanism — no explicit locking or queue management needed in the controller.
``WorkerThreadPool`` keeps the wiring in one place and gives shutdown a single
list of threads to join. Per-track fan-out inside lookup and download uses a
plain ``ThreadPoolExecutor``, and the Preferences authentication calls use
short-lived daemon threads; both report back through Qt signals.

**Atomic JSON writes with RLock.**
``JsonTrackRepository`` wraps all file access in a ``threading.RLock`` and
writes via a temp-file rename so that concurrent reads from a worker thread
never see a half-written file, and an application crash during a write does not
corrupt the stored data.

Quality Tooling
---------------

``localPipeline.sh`` is the canonical gate, run locally before every commit and
replicated by the GitHub workflows with ``--noRun --noOpen``. ``--noRun`` skips
the final application launch; ``--noOpen`` keeps the Sphinx and coverage HTML
reports from opening in a browser. Every stage up to the import check is
mandatory, including complete translations; the application launch only warns,
and the mutation gate runs only with ``--mutation``.

.. graphviz::
   :caption: Local pipeline stages

   digraph pipeline {
       graph [rankdir=LR, pad=0.4, nodesep=0.4, ranksep=0.5];
       node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=9,
             fillcolor="#f5fff9", color="#6b8f7a"];
       edge [color="#466354"];

       venv   [label=".venv +\neditable dev install"];
       ruff   [label="Ruff"];
       pylint [label="Pylint\n10.00/10"];
       mypy   [label="mypy\n0 errors"];
       tr     [label="Translation\ncompleteness\n0 untranslated"];
       docs   [label="tools/check_docs.py"];
       sphinx [label="Sphinx\n-W --keep-going"];
       tests  [label="pytest\n>= 99% line + branch"];
       build  [label="sdist + wheel"];
       inst   [label="wheel install\n+ import check"];
       mut    [label="Mutation gate\n>= 99%\n(--mutation)",
               fillcolor="#fff2cc", color="#d6b656"];
       launch [label="Launch app\n(unless --noRun)"];

       venv -> ruff -> pylint -> mypy -> tr -> docs -> sphinx -> tests
            -> build -> inst -> mut -> launch;
   }

- **mypy** checks ``my_lastfm_player/`` with ``[tool.mypy]`` from
  ``pyproject.toml``; ``union-attr`` and ``override`` are disabled because the
  PyQt6 stubs mark nearly every Qt getter and event parameter as optional.
  ``my_lastfm_player.qt_signal`` re-exports PyQt's ``pyqtSignal`` unchanged at
  runtime and only gives mypy a signature with the default the stubs omit.
- **Mutation testing**: ``tools/run_mutation_tests.sh`` runs mutmut over
  ``my_lastfm_player/`` with ``forkserver`` isolation (Qt is not fork-safe) and
  mypy as a type-check pre-filter, skipping log calls. Killed, mypy-rejected,
  timed-out, and crashing mutants count as detected. ``tools/mutation_score.py``
  prints the score, writes ``mutants/mutation-score.json``, and fails below
  ``MUTATION_SCORE_MIN`` percent (default 99).
- **Translation-catalog check**: ``tests/conftest.py`` installs a
  ``QTranslator`` that records every runtime ``tr()``/``translate()`` lookup
  missing from the German ``.ts`` catalog and fails the triggering test.
- **Slot-exception hook**: a per-test ``sys.excepthook`` turns an exception
  raised inside a Qt slot into a test failure instead of a process abort.
- **Golden images**: ``tests/fixtures/golden/`` holds reviewed PNGs of the
  painted icons and flags, compared with a small per-channel tolerance, and a
  JSON snapshot of every theme palette. ``MY_LASTFM_PLAYER_UPDATE_GOLDEN=1``
  regenerates them for review.

Core Class Relationships
------------------------

.. inheritance-diagram::
   my_lastfm_player.controller.ApplicationController
   my_lastfm_player.ui.main_window.MainWindow
   my_lastfm_player.ui.preferences_dialog.PreferencesDialog
   my_lastfm_player.ui.track_table_model.TrackTableModel
   my_lastfm_player.models.Track
   my_lastfm_player.storage.JsonTrackRepository
   my_lastfm_player.scrobbling.ScrobblingService
   :parts: 2
   :caption: Principal application classes

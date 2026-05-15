Architecture
============

myLastFmPlayer is a single-process Linux desktop application written in Python
with a PyQt6 GUI. The controller is the only component that crosses layer
boundaries, keeping the UI, domain services, background workers, and storage
decoupled from each other.

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

       app [label="myLastFmPlayer\n[Software System]\n\nFetches a user's loved tracks, resolves\nthem to YouTube audio, downloads mp3\nfiles, and plays them locally with\nLast.fm scrobbling.",
            shape=box, style="rounded,filled",
            fillcolor="#1168bd", fontcolor=white, color="#0b4884"];

       lastfm_web [label="Last.fm Website\n[External System]\n\nPublic profile pages scraped\nfor the loved-tracks list\n(no API key required).",
                   shape=box, style="rounded,filled",
                   fillcolor="#999999", fontcolor=white, color="#6b6b6b"];

       lastfm_api [label="Last.fm API\n[External System]\n\nAuthenticated API used for\nnow-playing updates and\ntrack scrobbling.",
                   shape=box, style="rounded,filled",
                   fillcolor="#999999", fontcolor=white, color="#6b6b6b"];

       youtube [label="YouTube\n[External System]\n\nSearched by yt-dlp for the\nbest-matching audio stream\nfor each track.",
                shape=box, style="rounded,filled",
                fillcolor="#999999", fontcolor=white, color="#6b6b6b"];

       user -> app       [label="clicks, playback controls,\nusername input"];
       app -> lastfm_web [label="HTTPS scrape (loved-track pages)"];
       app -> lastfm_api [label="pylast API (now-playing + scrobble)"];
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

           desktop [label="Desktop Application\n[Container: Python 3.12 / PyQt6]\n\nAll UI, business logic, and service\norchestration. Single OS process\nlaunched via my-lastfm-player CLI.",
                    shape=box, style="rounded,filled",
                    fillcolor="#1168bd", fontcolor=white, color="#0b4884"];

           json_store [label="JSON Data Store\n[Container: File System]\n\n~/.local/share/myLastFmPlayer/\nTrack lists, lookup cache,\ndownload cache, credentials.",
                       shape=cylinder, style="filled",
                       fillcolor="#1168bd", fontcolor=white, color="#0b4884"];

           audio_files [label="Downloaded Audio\n[Container: File System]\n\n~/.local/share/myLastFmPlayer/downloads/\nmp3 files named after resolved tracks.",
                        shape=cylinder, style="filled",
                        fillcolor="#1168bd", fontcolor=white, color="#0b4884"];

           qt_settings [label="Platform Settings\n[Container: QSettings]\n\nOS-native key-value store.\nTheme, language, scrobbling toggle,\nconcurrency, cookie browser.",
                        shape=cylinder, style="filled",
                        fillcolor="#1168bd", fontcolor=white, color="#0b4884"];
       }

       ytdlp  [label="yt-dlp\n[External CLI tool]\n\nYouTube search and\naudio stream download.",
               shape=box, style="rounded,filled",
               fillcolor="#999999", fontcolor=white, color="#6b6b6b"];

       ffmpeg [label="ffmpeg\n[External CLI tool]\n\nAudio conversion and\npost-processing (via yt-dlp).",
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
       ytdlp    -> ffmpeg      [label="post-process\naudio"];
       ytdlp    -> audio_files [label="writes mp3"];
       desktop  -> lastfm_web  [label="HTTPS scrape\n(requests + BeautifulSoup)"];
       desktop  -> lastfm_api  [label="pylast API calls\n(scrobble)"];
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

       main [label="main.py\n[Component: Startup]\n\nBootstraps QApplication;\napplies theme + language;\nwires MainWindow to controller.",
             fillcolor="#e8f0fe", color="#5577cc"];

       subgraph cluster_ui {
           label="UI Layer";
           style=filled; fillcolor="#f0f0f8"; color="#aaaacc";
           fontname="Helvetica"; fontsize=10;

           window      [label="MainWindow\n[PyQt6 QMainWindow]\n\nMenus, track table,\nplayback controls,\nprogress + status bar."];
           table_model [label="TrackTableModel\n[QAbstractTableModel]\n\nAdapter between the\ntrack list and the\nQTableView widget."];
           prefs       [label="PreferencesDialog\n[QDialog]\n\nTheme, language, scrobbling,\nconcurrency, cookie browser,\ndata retention settings."];
       }

       controller [label="ApplicationController\n[Component: Coordinator]\n\nThe single cross-layer hub.\nHandles UI signals, creates workers,\nmanages playback lifecycle, persists\nstate through the repository.",
                   fillcolor="#fff2cc", color="#d6b656", margin="0.3,0.15"];

       subgraph cluster_services {
           label="Domain / Service Layer";
           style=filled; fillcolor="#f9f9f9"; color="#aaaaaa";
           fontname="Helvetica"; fontsize=10;

           scraper     [label="LastFmLovedTracksScraper\n[HTTP Client]\n\nScrapes Last.fm profile pages\npage-by-page; retries with\nback-off; rate-limits between pages."];
           resolver    [label="YouTubeResolver\n[yt-dlp wrapper]\n\nChecks lookup-cache first;\nruns yt-dlp search subprocess;\nupdates cache on hit."];
           download_mgr[label="DownloadManager\n[yt-dlp wrapper]\n\nConcurrent mp3 download pool\nwith retry + jitter backoff;\nchecks download-cache to skip existing."];
           playback    [label="PlaybackService\n[Qt Multimedia]\n\nWraps QMediaPlayer;\nseek, pause, stop;\ntracks scrobble threshold."];
           scrobbling  [label="ScrobblingService\n[pylast]\n\nLast.fm web-auth flow;\nnow-playing + scrobble\nAPI calls via pylast."];
           deps        [label="DependencyChecker\n[shutil.which]\n\nVerifies yt-dlp and ffmpeg\nare present on PATH\nat application startup."];
       }

       subgraph cluster_workers {
           label="Background Workers (QThread)";
           style=filled; fillcolor="#f5fff9"; color="#6b8f7a";
           fontname="Helvetica"; fontsize=10;

           fetch_w    [label="FetchLovedTracksWorker\n[QObject on QThread]\n\nFetches Last.fm pages; emits\nprogress + track batches per page;\nsupports pause and stop."];
           lookup_w   [label="LookupTracksWorker\n[QObject on QThread]\n\nResolves FETCHED tracks to\nYouTube URLs; uses internal\nthread pool for concurrency."];
           download_w [label="DownloadTracksWorker\n[QObject on QThread]\n\nDownloads QUEUED tracks;\nreports per-file progress;\nrespects stop signal."];
       }

       subgraph cluster_data {
           label="Data Layer";
           style=filled; fillcolor="#fff8f0"; color="#ccaa88";
           fontname="Helvetica"; fontsize=10;

           repo     [label="JsonTrackRepository\n[File I/O]\n\nThread-safe JSON store backed\nby RLock; atomic writes via\ntemp-file rename."];
           settings [label="AppSettings\n[QSettings wrapper]\n\nPersists theme, language,\nscrobbling toggle, concurrency,\ncookie browser, data retention."];
           creds    [label="AppCredentials\n[Env / Bundled]\n\nLast.fm API key + secret;\nenv-var overrides bundled\ndefaults at startup."];
       }

       subgraph cluster_cross {
           label="Cross-Cutting";
           style=filled; fillcolor="#fdf6ff"; color="#ccaadd";
           fontname="Helvetica"; fontsize=10;

           i18n    [label="TranslationManager\n[QTranslator wrapper]\n\nLoads .qm files at runtime;\nfour UI languages supported."];
           themes  [label="ThemeManager\n[QPalette builder]\n\nBuilds palettes for\nLight / Dark / Lilac / Mint."];
           log_cfg [label="LoggingConfig\n[stdlib logging]\n\nConfigures process-wide\nlogging to stdout at INFO."];
       }

       main -> settings;
       main -> i18n;
       main -> themes;
       main -> window;
       main -> controller;

       window -> table_model;
       window -> prefs;
       window -> controller   [label="Qt signals"];

       controller -> repo      [label="load / save"];
       controller -> scraper;
       controller -> resolver;
       controller -> download_mgr;
       controller -> playback;
       controller -> scrobbling;
       controller -> deps;
       controller -> fetch_w   [label="create + start"];
       controller -> lookup_w  [label="create + start"];
       controller -> download_w[label="create + start"];
       controller -> window    [label="update UI"];
       controller -> creds;

       fetch_w    -> scraper;
       fetch_w    -> repo;
       lookup_w   -> resolver;
       lookup_w   -> repo;
       download_w -> download_mgr;
       download_w -> repo;
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
       QUEUED      [label="QUEUED\n(YouTube URL resolved)"];
       DOWNLOADING [label="DOWNLOADING\n(audio download in progress)"];
       DOWNLOADED  [label="DOWNLOADED\n(mp3 on disk — ready to play)",
                    fillcolor="#d5f0d5", color="#5a9a5a"];
       NOT_FOUND   [label="NOT FOUND\n(no YouTube result)",
                    fillcolor="#fdf0d5", color="#b89050"];
       FAILED      [label="FAILED\n(download error after retries)",
                    fillcolor="#fde8e8", color="#b05050"];

       FETCHED     -> SEARCHING   [label="lookup starts\n(no cache hit)"];
       FETCHED     -> QUEUED      [label="lookup-cache hit\n(URL already known)"];
       SEARCHING   -> QUEUED      [label="URL resolved"];
       SEARCHING   -> NOT_FOUND   [label="no yt-dlp result"];
       QUEUED      -> DOWNLOADING [label="download starts"];
       DOWNLOADING -> DOWNLOADED  [label="mp3 written"];
       DOWNLOADING -> FAILED      [label="error / retries exhausted"];
       NOT_FOUND   -> FETCHED     [label="user retries", style=dashed];
       FAILED      -> FETCHED     [label="user retries", style=dashed];
   }

Worker Lifecycle
----------------

Long-running network and I/O operations run on dedicated ``QThread`` instances
to keep the UI responsive. The controller owns both the thread and the worker;
the worker is moved to the thread before the thread starts (Qt's
``moveToThread`` pattern). Progress and completion signals cross back to the
main thread through Qt's queued connections.

.. graphviz::
   :caption: Background worker lifecycle

   digraph worker_lifecycle {
       graph [rankdir=LR, pad=0.4, nodesep=0.7, ranksep=1.0];
       node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=10,
             fillcolor="#f5fff9", color="#6b8f7a"];
       edge [fontname="Helvetica", fontsize=9, color="#466354"];

       signal  [label="UI Signal\n(e.g. fetch clicked)"];
       ctrl    [label="ApplicationController"];
       thread  [label="QThread"];
       worker  [label="Worker\n(Fetch / Lookup / Download)"];
       service [label="Service\n(Scraper / Resolver / DownloadManager)"];
       repo    [label="JsonTrackRepository"];
       ui      [label="MainWindow"];

       signal  -> ctrl;
       ctrl    -> thread   [label="create + start"];
       ctrl    -> worker   [label="create + moveToThread"];
       worker  -> service  [label="calls service methods"];
       service -> repo     [label="read / write tracks"];
       worker  -> ctrl     [label="progress signal\n(queued connection)"];
       worker  -> ctrl     [label="finished signal"];
       ctrl    -> repo     [label="persist state"];
       ctrl    -> ui       [label="refresh table\n+ status bar"];
       ctrl    -> thread   [label="quit + delete on finished"];
   }

Persisted Data
--------------

All mutable application data lives under ``$XDG_DATA_HOME/myLastFmPlayer/``
(defaulting to ``~/.local/share/myLastFmPlayer/`` when ``XDG_DATA_HOME`` is
not set). Writes are atomic: data is first written to a temp file in the same
directory and then renamed, preventing corrupt reads on crash.

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
   * - ``lookup-cache.json``
     - JSON object
     - Maps ``artist\x1ftrack`` → YouTube URL; consulted before invoking
       ``yt-dlp`` search to avoid redundant network calls.
   * - ``download-cache.json``
     - JSON object
     - Maps a download cache key → local file path; avoids re-downloading
       when the audio file still exists on disk.
   * - ``lastfm-credentials.json``
     - JSON object
     - Per-user Last.fm session key obtained through the web-auth flow;
       required for now-playing and scrobbling.
   * - ``downloads/``
     - Directory
     - Default output folder for downloaded mp3 files (overridable).
   * - QSettings (OS store)
     - Platform-native
     - Theme, UI language, scrobbling enabled, download concurrency,
       yt-dlp cookie browser, and keep-data-on-quit flag.

Key Design Decisions
--------------------

**Single controller, no service-to-service calls.**
``ApplicationController`` is the only class that knows about all others.
Services such as ``LastFmLovedTracksScraper``, ``YouTubeResolver``,
``DownloadManager``, ``PlaybackService``, and ``ScrobblingService`` are unaware
of each other and of the Qt event loop, making them individually testable
without a running application.

**Workers are stateless and short-lived.**
A fresh worker object is created for every operation, given references to the
relevant service and the repository, and discarded after the ``finished``
signal. The repository is the single source of truth; workers read from it and
write back through it, but never own any persistent state themselves.

**External tools as subprocesses, validated at startup.**
``yt-dlp`` and ``ffmpeg`` are invoked via ``subprocess.run`` rather than
linked as Python libraries. This keeps the runtime dependency surface small and
lets users upgrade CLI tools independently of the application version.
``DependencyChecker`` verifies both are on ``PATH`` at startup and surfaces a
warning in the UI if either is missing.

**Scraping, not the API, for the loved-tracks list.**
The Last.fm public loved-tracks page is scraped with ``requests`` +
``BeautifulSoup`` rather than the authenticated API endpoint. The API paginates
at 50 tracks per call and throttles aggressively at scale; scraping the public
page is faster, requires no API key, and the HTML structure has been stable for
years. The authenticated API is still used for the scrobble path where the rate
limits are appropriate and a session key is already required.

**QThread + moveToThread, not QRunnable.**
Background work uses ``QThread`` with worker objects moved to the thread rather
than ``QRunnable`` or Python ``threading.Thread``. This makes progress and
completion signals cross back to the Qt event loop naturally through Qt's
queued-connection mechanism — no explicit locking or queue management needed in
the controller.

**Atomic JSON writes with RLock.**
``JsonTrackRepository`` wraps all file access in a ``threading.RLock`` and
writes via a temp-file rename so that concurrent reads from a worker thread
never see a half-written file, and an application crash during a write does not
corrupt the stored data.

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

Architecture
============

The application is a PyQt desktop app with a small controller layer around
Last.fm fetching, YouTube lookup, download management, local playback, and
Last.fm scrobbling.

Runtime Flow
------------

.. graphviz::
   :caption: Main runtime collaborators

   digraph runtime_flow {
       graph [rankdir=LR, splines=ortho];
       node [shape=box, style="rounded,filled", fillcolor="#f7f7fb", color="#777777"];
       edge [color="#555555"];

       user [label="User"];
       main [label="main.py\nQApplication startup"];
       settings [label="AppSettings\nQSettings"];
       window [label="MainWindow\nmenus, table, controls"];
       controller [label="ApplicationController"];
       storage [label="JsonTrackRepository\nJSON cache files"];
       lastfm [label="LastFmLovedTracksScraper"];
       youtube [label="YouTubeResolver"];
       download [label="DownloadManager"];
       playback [label="PlaybackService"];
       scrobbling [label="ScrobblingService"];

       user -> window [label="clicks / selections"];
       main -> settings [label="load theme + language"];
       main -> window [label="create"];
       main -> controller [label="start"];
       window -> controller [label="Qt signals"];
       controller -> storage [label="load/save tracks,\nlookup cache,\ncredentials"];
       controller -> lastfm [label="fetch loved tracks"];
       controller -> youtube [label="resolve URLs"];
       controller -> download [label="download audio"];
       controller -> playback [label="play/pause/seek/stop"];
       controller -> scrobbling [label="now-playing + scrobble"];
       settings -> window [label="restore language\nand checked theme"];
   }

Worker Flow
-----------

Long-running fetch, lookup, and download operations run in Qt worker threads.
Workers report progress back to the controller; the controller updates the
window and persists changed track state through the repository.

.. graphviz::
   :caption: Background worker lifecycle

   digraph worker_lifecycle {
       graph [rankdir=TB];
       node [shape=box, style="rounded,filled", fillcolor="#f5fff9", color="#6b8f7a"];
       edge [color="#466354"];

       request [label="Window signal"];
       controller [label="ApplicationController"];
       thread [label="QThread"];
       worker [label="Fetch / Lookup / Download worker"];
       progress [label="progress signal"];
       finished [label="finished signal"];
       ui [label="MainWindow update"];
       repo [label="JsonTrackRepository"];

       request -> controller;
       controller -> thread [label="create"];
       controller -> worker [label="create + moveToThread"];
       thread -> worker [label="run"];
       worker -> progress;
       progress -> controller;
       controller -> ui;
       controller -> repo;
       worker -> finished;
       finished -> controller [label="cleanup thread/worker"];
   }

Persisted Settings
------------------

Only appearance preferences are stored through ``QSettings``:

* selected color theme
* selected language

The Last.fm username used for fetching tracks is intentionally not persisted as
an application setting. Track lists, lookup caches, download caches, and
Last.fm scrobbling credentials remain in the JSON repository files.

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

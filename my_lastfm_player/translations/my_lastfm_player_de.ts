<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>ApplicationController</name>
    <message>
        <location filename="../controller.py" line="152" />
        <source>No cached tracks found for {username}; fetching from Last.fm.</source>
        <translation>Für {username} wurden keine zwischengespeicherten Titel gefunden. Abrufen von Last.fm.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="163" />
        <source>Found {count} cached tracks for {username}; checking Last.fm before using them.</source>
        <translation>{count} zwischengespeicherte Tracks für {username} gefunden; Überprüfen Sie Last.fm, bevor Sie sie verwenden.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="183" />
        <source>Loaded {count} cached tracks for {username}; skipped Last.fm fetch.</source>
        <translation>{count} zwischengespeicherte Tracks für {username} geladen; Last.fm-Abruf übersprungen.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="197" />
        <source>Could not verify Last.fm loved-track count for {username}; using {count} cached tracks: {error}</source>
        <translation>Die Anzahl der von Last.fm geliebten Titel für {username} konnte nicht überprüft werden. {count} zwischengespeicherte Titel werden verwendet: {error}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="210" />
        <source>Could not read Last.fm loved-track count for {username}; fetching fresh data instead of trusting {count} cached tracks.</source>
        <translation>Die Anzahl der von Last.fm geliebten Titel für {username} konnte nicht gelesen werden. Abrufen neuer Daten, anstatt {count} zwischengespeicherten Tracks zu vertrauen.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="222" />
        <source>Last.fm reports {online_count} loved tracks for {username}; cached track count matches.</source>
        <translation>Last.fm meldet {online_count} beliebte Titel für {username}; zwischengespeicherte Titelanzahl-Übereinstimmungen.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="233" />
        <source>Last.fm reports {online_count} loved tracks for {username}, but the cache has {cached_count}; fetching fresh data.</source>
        <translation>Last.fm meldet {online_count} geliebte Titel für {username}, aber der Cache enthält {cached_count}; Abrufen neuer Daten.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="258" />
        <source>Dependency check finished: {message}</source>
        <translation>Abhängigkeitsprüfung abgeschlossen: {message}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="275" />
        <source>Could not open data folder: {error}</source>
        <translation>Datenordner konnte nicht geöffnet werden: {error}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="285" />
        <source>Opened data folder: {path}</source>
        <translation>Datenordner geöffnet: {path}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="294" />
        <source>Could not open data folder: {path}</source>
        <translation>Datenordner konnte nicht geöffnet werden: {path}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="305" />
        <source>Last.fm scrobbling is disabled because {api_key_env}/{api_secret_env} are not configured and no bundled credentials are available.</source>
        <translation>Das Scrobbeln von Last.fm ist deaktiviert, da {api_key_env}/{api_secret_env} nicht konfiguriert sind und keine gebündelten Anmeldeinformationen verfügbar sind.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="320" />
        <source>Loaded Last.fm scrobbling settings; stored session key is {state}.</source>
        <translation>Last.fm-Scrobbeleinstellungen geladen; Der gespeicherte Sitzungsschlüssel ist {state}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="324" />
        <source>present</source>
        <translation>gegenwärtig</translation>
    </message>
    <message>
        <location filename="../controller.py" line="326" />
        <source>missing</source>
        <translation>fehlen</translation>
    </message>
    <message>
        <location filename="../controller.py" line="340" />
        <source>Connected Last.fm scrobbling as {username}.</source>
        <translation>Verbunden mit Last.fm, scrobbelt als {username}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="348" />
        <source>Stored Last.fm session key could not be verified; scrobbling remains disconnected.</source>
        <translation>Der gespeicherte Last.fm-Sitzungsschlüssel konnte nicht überprüft werden; Das Scrobbeln bleibt unterbrochen.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="358" />
        <source>Opening preferences.</source>
        <translation>Voreinstellungen öffnen.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="372" />
        <source>Preferences closed; no Last.fm scrobbling service is active.</source>
        <translation>Einstellungen geschlossen; Es ist kein Last.fm-Scrobbeldienst aktiv.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="381" />
        <source>Saved Last.fm scrobbling preferences for {username}.</source>
        <translation>Last.fm-Scrobbeleinstellungen für {username} gespeichert.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="385" />
        <source>no user</source>
        <translation>kein Benutzer</translation>
    </message>
    <message>
        <location filename="../controller.py" line="396" />
        <source>Enter a Last.fm username before fetching tracks.</source>
        <translation>Geben Sie einen Last.fm-Benutzernamen ein, bevor Sie Titel abrufen.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="407" />
        <source>Loaded cached tracks</source>
        <translation>Zwischengespeicherte Titel geladen</translation>
    </message>
    <message>
        <location filename="../controller.py" line="424" />
        <source>Could not reach Last.fm for {username}: {error}</source>
        <translation>Last.fm für {username} nicht erreichbar: {error}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="438" />
        <source>Starting fresh Last.fm fetch for {username}; {count} tracks expected.</source>
        <translation>Neuen Last.fm-Abruf für {username} starten; {count} Titel erwartet.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="447" />
        <source>Starting fresh Last.fm fetch for {username}.</source>
        <translation>Neuen Last.fm-Abruf für {username} starten.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="456" />
        <source>Starting fetch</source>
        <translation>Abruf wird gestartet</translation>
    </message>
    <message>
        <location filename="../controller.py" line="472" />
        <source>Fetch resumed.</source>
        <translation>Der Abruf wurde fortgesetzt.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="478" />
        <source>Fetch paused.</source>
        <translation>Abruf pausiert.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="488" />
        <source>Stopping fetch.</source>
        <translation>Abruf wird gestoppt.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="502" />
        <source>Enter a Last.fm username before resolving tracks.</source>
        <translation>Geben Sie einen Last.fm-Benutzernamen ein, bevor Sie Titel auflösen.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="511" />
        <source>Starting YouTube lookup for {username}; priority={priority}, limit={limit}.</source>
        <translation>YouTube-Suche für {username} wird gestartet; Priorität={priority}, Limit={limit}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="571" />
        <location filename="../controller.py" line="517" />
        <source>none</source>
        <translation>keiner</translation>
    </message>
    <message>
        <location filename="../controller.py" line="575" />
        <location filename="../controller.py" line="521" />
        <source>all</source>
        <translation>alle</translation>
    </message>
    <message>
        <location filename="../controller.py" line="527" />
        <source>Starting YouTube lookup</source>
        <translation>YouTube-Suche wird gestartet</translation>
    </message>
    <message>
        <location filename="../controller.py" line="550" />
        <source>Enter a Last.fm username before downloading tracks.</source>
        <translation>Geben Sie einen Last.fm-Benutzernamen ein, bevor Sie Titel herunterladen.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="564" />
        <source>Starting downloads for {username}; concurrency={concurrency}, priority={priority}, limit={limit}.</source>
        <translation>Downloads für {username} werden gestartet; Parallelität={concurrency}, Priorität={priority}, Limit={limit}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="580" />
        <source>Starting downloads</source>
        <translation>Downloads starten</translation>
    </message>
    <message>
        <location filename="../controller.py" line="601" />
        <source>Select a downloaded track before playing.</source>
        <translation>Wählen Sie vor der Wiedergabe einen heruntergeladenen Titel aus.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="617" />
        <source>Playback resumed.</source>
        <translation>Die Wiedergabe wurde fortgesetzt.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="626" />
        <source>Playback paused.</source>
        <translation>Wiedergabe pausiert.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="635" />
        <source>No track is currently playing.</source>
        <translation>Derzeit wird kein Titel abgespielt.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="645" />
        <source>Playback stopped.</source>
        <translation>Die Wiedergabe wurde gestoppt.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="662" />
        <source>Seeked playback to {seconds} seconds.</source>
        <translation>Gesuchte Wiedergabe auf {seconds} Sekunden.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="710" />
        <source>Fetch for {username} returned invalid track data.</source>
        <translation>Der Abruf für {username} hat ungültige Trackdaten zurückgegeben.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="720" />
        <source>Fetched and stored {count} tracks for {username}.</source>
        <translation>{count} Tracks für {username} abgerufen und gespeichert.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="743" />
        <source>Stopped fetch for {username} returned invalid data.</source>
        <translation>Der Abruf für {username} wurde gestoppt und lieferte ungültige Daten.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="753" />
        <source>Stopped fetch for {username} after {count} tracks.</source>
        <translation>Der Abruf für {username} wurde nach {count} Tracks gestoppt.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="764" />
        <source>Fetch for {username} returned invalid partial data.</source>
        <translation>Der Abruf für {username} hat ungültige Teildaten zurückgegeben.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="775" />
        <source>Fetch progress for {username}: {count} tracks are visible now.</source>
        <translation>Abruffortschritt für {username}: {count} Titel sind jetzt sichtbar.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="783" />
        <source>Fetched {count} tracks for {username}</source>
        <translation>{count} Titel für {username} abgerufen</translation>
    </message>
    <message>
        <location filename="../controller.py" line="802" />
        <source>Workflow for {username} returned an invalid track update.</source>
        <translation>Der Workflow für {username} hat eine ungültige Trackaktualisierung zurückgegeben.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="812" />
        <source>Track update from {username}: {artist} - {title} is now {status}.</source>
        <translation>Titelaktualisierung von {username}: {artist} – {title} ist jetzt {status}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="827" />
        <source>Lookup for {username} returned invalid track data.</source>
        <translation>Bei der Suche nach {username} wurden ungültige Trackdaten zurückgegeben.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="843" />
        <source>Resolved YouTube URLs for {resolved_count}/{count} tracks; {not_found_count} were not found.</source>
        <translation>Aufgelöste YouTube-URLs für {resolved_count}/{count} Titel; {not_found_count} wurden nicht gefunden.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="867" />
        <source>No queued tracks are ready for download.</source>
        <translation>Es stehen keine Titel in der Warteschlange zum Download bereit.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="878" />
        <source>Download for {username} returned invalid track data.</source>
        <translation>Der Download für {username} hat ungültige Trackdaten zurückgegeben.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="898" />
        <source>Download run for {username} finished: {downloaded_count}/{count} tracks downloaded, {failed_count} failed.</source>
        <translation>Download-Lauf für {username} abgeschlossen: {downloaded_count}/{count} Titel heruntergeladen, {failed_count} fehlgeschlagen.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="925" />
        <source>Failed</source>
        <translation>Fehlgeschlagen</translation>
    </message>
    <message>
        <location filename="../controller.py" line="962" />
        <source>Updating Last.fm now-playing for {artist} - {title}.</source>
        <translation>Aktualisierung der Last.fm-Wiedergabe für {artist} – {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="971" />
        <source>Playing {artist} - {title}.</source>
        <translation>Ich spiele {artist} – {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="990" />
        <source>Enter a Last.fm username before preparing playback.</source>
        <translation>Geben Sie einen Last.fm-Benutzernamen ein, bevor Sie die Wiedergabe vorbereiten.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="999" />
        <source>Preparing {artist} - {title} for playback.</source>
        <translation>{artist} – {title} wird für die Wiedergabe vorbereitet.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1016" />
        <source>Starting automatic YouTube lookup for {count} fetched tracks.</source>
        <translation>Automatische YouTube-Suche nach {count} abgerufenen Titeln wird gestartet.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1032" />
        <source>Downloads stopped by user.</source>
        <translation>Downloads vom Benutzer gestoppt.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1041" />
        <source>Enter a Last.fm username before retrying a download.</source>
        <translation>Geben Sie einen Last.fm-Benutzernamen ein, bevor Sie einen Download erneut versuchen.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1059" />
        <source>Retrying download for {artist} - {title}.</source>
        <translation>Download für {artist} - {title} wird erneut versucht.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1072" />
        <source>Starting automatic download queue for resolved tracks.</source>
        <translation>Automatische Download-Warteschlange für gelöste Titel wird gestartet.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1080" />
        <source>Starting priority download for selected track.</source>
        <translation>Prioritäts-Download für den ausgewählten Titel wird gestartet.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1154" />
        <source>Submitting Last.fm scrobble for {artist} - {title}.</source>
        <translation>Einreichen des Last.fm-Scrobbles für {artist} – {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1183" />
        <source>Finished playback for {artist} - {title}.</source>
        <translation>Wiedergabe für {artist} – {title} abgeschlossen.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1193" />
        <source>Playback finished.</source>
        <translation>Wiedergabe beendet.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1200" />
        <source>Continuing with next track: {artist} - {title}.</source>
        <translation>Weiter mit dem nächsten Titel: {artist} – {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1215" />
        <source>All background work is finished; controls are enabled again.</source>
        <translation>Alle Hintergrundarbeiten sind abgeschlossen; Die Steuerung ist wieder aktiviert.</translation>
    </message>
    <message>
        <source>Could not open file cache: {error}</source>
        <translation type="vanished">Dateicache konnte nicht geöffnet werden: {error}</translation>
    </message>
    <message>
        <source>Opened file cache: {path}</source>
        <translation type="vanished">Geöffneter Dateicache: {path}</translation>
    </message>
    <message>
        <source>Could not open file cache: {path}</source>
        <translation type="vanished">Der Dateicache konnte nicht geöffnet werden: {path}</translation>
    </message>
    <message>
        <source>Resolved YouTube URLs for {count} tracks.</source>
        <translation type="vanished">Aufgelöste YouTube-URLs für {count} Titel.</translation>
    </message>
    <message>
        <source>Downloaded {count} tracks for {username}.</source>
        <translation type="vanished">{count} Titel für {username} heruntergeladen.</translation>
    </message>
</context><context>
    <name>DependencyCheckResult</name>
    <message>
        <location filename="../dependencies.py" line="30" />
        <source>Dependencies installed: {tools}</source>
        <translation>Installierte Abhängigkeiten: {tools}</translation>
    </message>
    <message>
        <location filename="../dependencies.py" line="35" />
        <source>Missing dependencies: {tools}</source>
        <translation>Fehlende Abhängigkeiten: {tools}</translation>
    </message>
</context><context>
    <name>DownloadManager</name>
    <message>
        <location filename="../download.py" line="124" />
        <source>Queued {count} downloads</source>
        <translation>{count} Downloads in der Warteschlange</translation>
    </message>
    <message>
        <location filename="../download.py" line="153" />
        <source>Downloaded {done}/{total} tracks</source>
        <translation>{done}/{total} Titel heruntergeladen</translation>
    </message>
</context><context>
    <name>FetchLovedTracksWorker</name>
    <message>
        <location filename="../workers.py" line="52" />
        <source>Looking up Last.fm user {username}</source>
        <translation>Suche nach Last.fm-Benutzer {username}</translation>
    </message>
    <message>
        <location filename="../workers.py" line="68" />
        <source>Stopped fetch after {count} tracks</source>
        <translation>Der Abruf wurde nach {count} Titeln gestoppt</translation>
    </message>
    <message>
        <location filename="../workers.py" line="78" />
        <source>Fetched {count} tracks</source>
        <translation>{count} Titel abgerufen</translation>
    </message>
</context><context>
    <name>LastFmLovedTracksScraper</name>
    <message>
        <location filename="../lastfm.py" line="381" />
        <source>Found Last.fm user {username}</source>
        <translation>Last.fm-Benutzer {username} gefunden</translation>
    </message>
    <message>
        <location filename="../lastfm.py" line="666" />
        <source>Fetched {count} tracks</source>
        <translation>{count} Titel abgerufen</translation>
    </message>
    <message>
        <location filename="../lastfm.py" line="671" />
        <source>Fetched {done}/{total} tracks</source>
        <translation>{done}/{total} Tracks abgerufen</translation>
    </message>
</context><context>
    <name>LookupTracksWorker</name>
    <message>
        <location filename="../workers.py" line="156" />
        <source>Resolving YouTube URLs for {username}</source>
        <translation>Auflösen von YouTube-URLs für {username}</translation>
    </message>
    <message>
        <location filename="../workers.py" line="172" />
        <source>Resolved {count} tracks</source>
        <translation>{count} Tracks gelöst</translation>
    </message>
</context><context>
    <name>MainWindow</name>
    <message>
        <location filename="../ui/main_window.py" line="801" />
        <location filename="../ui/main_window.py" line="80" />
        <source>Ready</source>
        <translation>Bereit</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="247" />
        <source>Retry Download</source>
        <translation>Download erneut versuchen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="794" />
        <location filename="../ui/main_window.py" line="322" />
        <source>Idle</source>
        <translation>Leerlauf</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="346" />
        <source>Loaded {count} tracks</source>
        <translation>{count} Titel geladen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="357" />
        <source>Playlist: {count} titles</source>
        <translation>Playlist: {count} Titel</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="378" />
        <source>Resume</source>
        <translation>Wieder aufnehmen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="774" />
        <location filename="../ui/main_window.py" line="378" />
        <source>Pause</source>
        <translation>Pause</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="775" />
        <location filename="../ui/main_window.py" line="379" />
        <source>Stop</source>
        <translation>Stoppen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="381" />
        <source>Resume the paused Last.fm fetch</source>
        <translation>Setzen Sie den angehaltenen Last.fm-Abruf fort</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="383" />
        <source>Pause the active Last.fm fetch</source>
        <translation>Unterbrechen Sie den aktiven Last.fm-Abruf</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="384" />
        <source>Stop the active Last.fm fetch</source>
        <translation>Stoppen Sie den aktiven Last.fm-Abruf</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="779" />
        <location filename="../ui/main_window.py" line="394" />
        <source>Stop Downloads</source>
        <translation>Downloads stoppen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="779" />
        <location filename="../ui/main_window.py" line="398" />
        <source>Start Downloads</source>
        <translation>Downloads starten</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="473" />
        <source>Updated {artist} - {title}: {status}</source>
        <translation>Aktualisiert {artist} – {title}: {status}</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="772" />
        <location filename="../ui/main_window.py" line="490" />
        <source>Not playing</source>
        <translation>Keine Wiedergabe</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="756" />
        <location filename="../ui/main_window.py" line="543" />
        <source>About myLastFmPlayer</source>
        <translation>Über myLastFmPlayer</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="549" />
        <source>myLastFmPlayer {version}</source>
        <translation>myLastFmPlayer {version}</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="550" />
        <source>Author: Marcel Petrick &lt;a href="mailto:mail@marcelpetrick.it"&gt;mail@marcelpetrick.it&lt;/a&gt;</source>
        <translation>Autor: Marcel Petrick &lt;a href="mailto:mail@marcelpetrick.it"&gt;mail@marcelpetrick.it&lt;/a&gt;</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="554" />
        <source>License: GNU GPLv3 or later.</source>
        <translation>Lizenz: GNU GPLv3 oder neuer.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="555" />
        <source>This application fetches a user's public loved tracks from Last.fm, keeps local metadata, resolves playable sources through yt-dlp, downloads MP3 files, and plays them locally.</source>
        <translation>Diese Anwendung lädt die öffentlichen Lieblingslieder eines Benutzers von Last.fm, speichert lokale Metadaten, ermittelt abspielbare Quellen über yt-dlp, lädt MP3-Dateien herunter und spielt sie lokal ab.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="560" />
        <source>It is intended as a practical Linux desktop helper for rebuilding a personal loved-track collection without manually searching every song.</source>
        <translation>Sie ist als praktischer Linux-Desktophelfer gedacht, um eine persönliche Sammlung geliebter Titel wiederaufzubauen, ohne jedes Lied manuell zu suchen.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="564" />
        <source>Optional Last.fm scrobbling can connect the local playback workflow back to the user's Last.fm account.</source>
        <translation>Optionales Last.fm-Scrobbling kann den lokalen Wiedergabeablauf wieder mit dem Last.fm-Konto des Benutzers verbinden.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="757" />
        <location filename="../ui/main_window.py" line="574" />
        <source>Open Source Licenses</source>
        <translation>Open-Source-Lizenzen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="580" />
        <source>myLastFmPlayer is GPLv3-or-later software and uses these open-source libraries and external tools:</source>
        <translation>myLastFmPlayer ist GPLv3-oder-neuer-Software und verwendet diese Open-Source-Bibliotheken und externen Werkzeuge:</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="648" />
        <location filename="../ui/main_window.py" line="586" />
        <source>Python Software Foundation License; runtime for the application.</source>
        <translation>Python Software Foundation License; Laufzeitumgebung für die Anwendung.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="650" />
        <location filename="../ui/main_window.py" line="590" />
        <source>GNU GPL v3; Python bindings for the Qt desktop interface.</source>
        <translation>GNU GPL v3; Python-Bindings für die Qt-Desktopoberfläche.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="651" />
        <location filename="../ui/main_window.py" line="594" />
        <source>GNU LGPL v3 / GPL v3; cross-platform UI toolkit.</source>
        <translation>GNU LGPL v3 / GPL v3; plattformübergreifendes UI-Toolkit.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="653" />
        <location filename="../ui/main_window.py" line="598" />
        <source>Apache License 2.0; HTTP client for Last.fm API calls.</source>
        <translation>Apache License 2.0; HTTP-Client für Last.fm-API-Aufrufe.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="655" />
        <location filename="../ui/main_window.py" line="602" />
        <source>MIT License; legacy Last.fm HTML parser support.</source>
        <translation>MIT License; Unterstützung für den alten Last.fm-HTML-Parser.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="656" />
        <location filename="../ui/main_window.py" line="606" />
        <source>Apache License 2.0; Last.fm scrobbling integration.</source>
        <translation>Apache License 2.0; Last.fm-Scrobbling-Integration.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="657" />
        <location filename="../ui/main_window.py" line="610" />
        <source>Unlicense; media lookup and download helper.</source>
        <translation>Unlicense; Helfer für Mediensuche und Download.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="659" />
        <location filename="../ui/main_window.py" line="614" />
        <source>LGPL/GPL family licenses depending on the installed build; audio conversion backend.</source>
        <translation>LGPL/GPL-Lizenzfamilie je nach installierter Version; Backend für Audiokonvertierung.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="619" />
        <source>Development tools include {tools} under their respective open-source licenses.</source>
        <translation>Zu den Entwicklungswerkzeugen gehören {tools} unter ihren jeweiligen Open-Source-Lizenzen.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="635" />
        <source>This summary is informational; the complete license texts are provided by the installed projects and system packages.</source>
        <translation>Diese Zusammenfassung dient zur Information; die vollständigen Lizenztexte werden von den installierten Projekten und Systempaketen bereitgestellt.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="753" />
        <source>Fetch loved tracks</source>
        <translation>Holen Sie sich beliebte Titel</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="754" />
        <source>Preferences</source>
        <translation>Präferenzen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="755" />
        <source>Open data folder in file manager</source>
        <translation>Datenordner im Dateimanager öffnen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="758" />
        <source>Quit</source>
        <translation>Aufhören</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="759" />
        <source>Main</source>
        <translation>Hauptsächlich</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="760" />
        <source>Theme</source>
        <translation>Thema</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="761" />
        <source>Light</source>
        <translation>Licht</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="762" />
        <source>Dark</source>
        <translation>Dunkel</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="763" />
        <source>Lilac</source>
        <translation>Lila</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="764" />
        <source>Mint</source>
        <translation>Minze</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="765" />
        <source>Language</source>
        <translation>Sprache</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="766" />
        <source>Help</source>
        <translation>Hilfe</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="767" />
        <source>Last.fm username</source>
        <translation>Last.fm-Benutzername</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="768" />
        <source>Enter username</source>
        <translation>Geben Sie den Benutzernamen ein</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="769" />
        <source>Fetch</source>
        <translation>Bringen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="770" />
        <source>Playback</source>
        <translation>Wiedergabe</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="773" />
        <source>Play</source>
        <translation>Spielen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="776" />
        <source>Playback position</source>
        <translation>Wiedergabeposition</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="777" />
        <source>Downloads</source>
        <translation>Downloads</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="781" />
        <source>Clear log</source>
        <translation>Protokoll löschen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="782" />
        <source>Clear status updates and errors</source>
        <translation>Klare Statusaktualisierungen und Fehler</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="784" />
        <source>Status updates and errors will appear here.</source>
        <translation>Hier werden Statusaktualisierungen und Fehler angezeigt.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="791" />
        <source>Dependencies: yt-dlp and ffmpeg not checked yet</source>
        <translation>Abhängigkeiten: yt-dlp und ffmpeg noch nicht überprüft</translation>
    </message>
    <message>
        <source>Author: Marcel Petrick &lt;mail@marcelpetrick.it&gt;</source>
        <translation type="vanished">Autor: Marcel Petrick &lt;mail@marcelpetrick.it&gt;</translation>
    </message>
    <message>
        <source>Python - Python Software Foundation License; runtime for the application.</source>
        <translation type="vanished">Python - Python Software Foundation License; Laufzeitumgebung für die Anwendung.</translation>
    </message>
    <message>
        <source>PyQt6 - GNU GPL v3; Python bindings for the Qt desktop interface.</source>
        <translation type="vanished">PyQt6 - GNU GPL v3; Python-Bindings für die Qt-Desktopoberfläche.</translation>
    </message>
    <message>
        <source>Qt 6 - GNU LGPL v3 / GPL v3; cross-platform UI toolkit.</source>
        <translation type="vanished">Qt 6 - GNU LGPL v3 / GPL v3; plattformübergreifendes UI-Toolkit.</translation>
    </message>
    <message>
        <source>requests - Apache License 2.0; HTTP client for Last.fm API calls.</source>
        <translation type="vanished">requests - Apache License 2.0; HTTP-Client für Last.fm-API-Aufrufe.</translation>
    </message>
    <message>
        <source>beautifulsoup4 - MIT License; legacy Last.fm HTML parser support.</source>
        <translation type="vanished">beautifulsoup4 - MIT License; Unterstützung für den alten Last.fm-HTML-Parser.</translation>
    </message>
    <message>
        <source>pylast - Apache License 2.0; Last.fm scrobbling integration.</source>
        <translation type="vanished">pylast - Apache License 2.0; Last.fm-Scrobbling-Integration.</translation>
    </message>
    <message>
        <source>yt-dlp - Unlicense; media lookup and download helper.</source>
        <translation type="vanished">yt-dlp - Unlicense; Helfer für Mediensuche und Download.</translation>
    </message>
    <message>
        <source>FFmpeg - LGPL/GPL family licenses depending on the installed build; audio conversion backend.</source>
        <translation type="vanished">FFmpeg - LGPL/GPL-Lizenzfamilie je nach installierter Version; Backend für Audiokonvertierung.</translation>
    </message>
    <message>
        <source>Development tools include pytest, pytest-cov, coverage.py, Ruff, Pylint, Sphinx, and build under their respective open-source licenses.</source>
        <translation type="vanished">Zu den Entwicklungswerkzeugen gehören pytest, pytest-cov, coverage.py, Ruff, Pylint, Sphinx und build unter ihren jeweiligen Open-Source-Lizenzen.</translation>
    </message>
    <message>
        <source>Cached songs storage location</source>
        <translation type="vanished">Speicherort für zwischengespeicherte Songs</translation>
    </message>
    <message>
        <source>Download Queued</source>
        <translation type="vanished">Download in der Warteschlange</translation>
    </message>
    <message>
        <source>Concurrency</source>
        <translation type="vanished">Parallelität</translation>
    </message>
    <message>
        <source>This control is part of the MVP shell and will be wired in later steps.</source>
        <translation type="vanished">Dieses Steuerelement ist Teil der MVP-Shell und wird in späteren Schritten verkabelt.</translation>
    </message>
</context><context>
    <name>PreferencesDialog</name>
    <message>
        <location filename="../ui/preferences_dialog.py" line="163" />
        <location filename="../ui/preferences_dialog.py" line="123" />
        <source>None (disabled)</source>
        <translation>Keine (deaktiviert)</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="143" />
        <source>Preferences</source>
        <translation>Präferenzen</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="144" />
        <source>Last.fm Authentication</source>
        <translation>Last.fm-Authentifizierung</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="145" />
        <source>Authenticate with Last.fm</source>
        <translation>Authentifizieren Sie sich mit Last.fm</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="146" />
        <source>I've authorized</source>
        <translation>Ich habe autorisiert</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="147" />
        <source>Disconnect</source>
        <translation>Trennen</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="148" />
        <source>Scrobbling</source>
        <translation>Scrobbeln</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="149" />
        <source>Enable scrobbling</source>
        <translation>Scrobbeln aktivieren</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="151" />
        <source>Submits to Last.fm after 33% of each track has been played.</source>
        <translation>Wird an Last.fm übermittelt, nachdem 33 % jedes Titels abgespielt wurden.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="153" />
        <source>YouTube Downloads</source>
        <translation>YouTube-Downloads</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="154" />
        <source>Browser cookies:</source>
        <translation>Browser-Cookies:</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="155" />
        <source>Parallel downloads:</source>
        <translation>Parallele Downloads:</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="157" />
        <source>Select the browser whose YouTube login cookies yt-dlp should use. Required for age-restricted videos. You must be signed into YouTube in the selected browser. Parallel download changes apply to new work.</source>
        <translation>Wählen Sie den Browser, dessen YouTube-Anmelde-Cookies yt-dlp verwenden soll. Erforderlich für altersbeschränkte Videos. Sie müssen im ausgewählten Browser bei YouTube angemeldet sein. Änderungen an parallelen Downloads gelten für neue Aufgaben.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="164" />
        <source>Privacy</source>
        <translation>Datenschutz</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="165" />
        <source>Keep cached data after quitting</source>
        <translation>Zwischengespeicherte Daten nach dem Beenden behalten</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="170" />
        <source>⚠ API credentials not configured.
Set LASTFM_API_KEY and LASTFM_API_SECRET environment variables.</source>
        <translation>⚠ API-Anmeldeinformationen nicht konfiguriert. 
Legen Sie die Umgebungsvariablen LASTFM_API_KEY und LASTFM_API_SECRET fest.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="188" />
        <source>🟢 Connected as {username}</source>
        <translation>🟢 Verbunden als {username}</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="197" />
        <source>🔵 Browser opened — authorize the app, then click «I've authorized».</source>
        <translation>🔵 Browser geöffnet – Autorisieren Sie die App und klicken Sie dann auf „Ich habe autorisiert“.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="203" />
        <source>🔴 Not connected</source>
        <translation>🔴 Nicht verbunden</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="216" />
        <source>⚠ Could not start authentication. Check API credentials.</source>
        <translation>⚠ Die Authentifizierung konnte nicht gestartet werden. Überprüfen Sie die API-Anmeldeinformationen.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="227" />
        <source>⚠ Authorization not confirmed yet. Authorize in the browser, then try again.</source>
        <translation>⚠ Autorisierung noch nicht bestätigt. Autorisieren Sie im Browser und versuchen Sie es dann erneut.</translation>
    </message>
    <message>
        <source>Submits to Last.fm after 10 % of each track has been played.</source>
        <translation type="vanished">Wird an Last.fm übermittelt, nachdem 10 % jedes Titels abgespielt wurden.</translation>
    </message>
</context><context>
    <name>TrackTableModel</name>
    <message>
        <location filename="../ui/track_table_model.py" line="94" />
        <source>Artist</source>
        <translation>Künstlerin Künstler</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="96" />
        <source>Title</source>
        <translation>Titel</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="98" />
        <source>Loved at</source>
        <translation>Geliebt am</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="100" />
        <source>Status</source>
        <translation>Status</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="102" />
        <source>File</source>
        <translation>Datei</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="195" />
        <source>Example Artist</source>
        <translation>Beispielkünstler</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="196" />
        <source>Example Track</source>
        <translation>Beispiel-Track</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="200" />
        <source>Another Artist</source>
        <translation>Ein anderer Künstler</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="201" />
        <source>Waiting for implementation</source>
        <translation>Warten auf die Umsetzung</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="210" />
        <source>Fetched</source>
        <translation>Abgeholt</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="212" />
        <source>Queued</source>
        <translation>In der Warteschlange</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="214" />
        <source>Searching</source>
        <translation>Suchen</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="216" />
        <source>Downloading</source>
        <translation>Herunterladen</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="218" />
        <source>Downloaded</source>
        <translation>Heruntergeladen</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="220" />
        <source>Failed</source>
        <translation>Fehlgeschlagen</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="222" />
        <source>Not found</source>
        <translation>Nicht gefunden</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="237" />
        <source>{bitrate} kbps</source>
        <translation>{bitrate} kbps</translation>
    </message>
</context><context>
    <name>YouTubeResolver</name>
    <message>
        <location filename="../youtube.py" line="91" />
        <source>Searching {done}/{total}: {artist} - {title}</source>
        <translation>Suche nach {done}/{total}: ​​{artist} - {title}</translation>
    </message>
    <message>
        <location filename="../youtube.py" line="236" />
        <source>Resolved {done}/{total}: {artist} - {title}</source>
        <translation>Gelöst {done}/{total}: ​​{artist} - {title}</translation>
    </message>
    <message>
        <location filename="../youtube.py" line="244" />
        <source>No YouTube result {done}/{total}: {artist} - {title}</source>
        <translation>Kein YouTube-Ergebnis {done}/{total}: ​​{artist} – {title}</translation>
    </message>
</context></TS>

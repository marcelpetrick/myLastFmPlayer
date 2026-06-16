<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>ApplicationController</name>
    <message>
        <location filename="../controller.py" line="175" />
        <source>No cached tracks found for {username}; fetching from Last.fm.</source>
        <translation>Keine zwischengespeicherten Titel für {username} gefunden; Abruf von Last.fm wird gestartet.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="186" />
        <source>Found {count} cached tracks for {username}; checking Last.fm before using them.</source>
        <translation>{count} zwischengespeicherte Titel für {username} gefunden; Last.fm wird vor der Verwendung geprüft.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="206" />
        <source>Loaded {count} cached tracks for {username}; skipped Last.fm fetch.</source>
        <translation>{count} zwischengespeicherte Titel für {username} geladen; Last.fm-Abruf übersprungen.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="220" />
        <source>Could not verify Last.fm loved-track count for {username}; using {count} cached tracks: {error}</source>
        <translation>Die Anzahl der Last.fm-Lieblingstitel für {username} konnte nicht überprüft werden. {count} zwischengespeicherte Titel werden verwendet: {error}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="233" />
        <source>Could not read Last.fm loved-track count for {username}; fetching fresh data instead of trusting {count} cached tracks.</source>
        <translation>Die Anzahl der Last.fm-Lieblingstitel für {username} konnte nicht gelesen werden. Es werden neue Daten abgerufen, statt {count} zwischengespeicherten Titeln zu vertrauen.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="245" />
        <source>Last.fm reports {online_count} loved tracks for {username}; cached track count matches.</source>
        <translation>Last.fm meldet {online_count} Lieblingstitel für {username}; die Anzahl der zwischengespeicherten Titel stimmt überein.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="256" />
        <source>Last.fm reports {online_count} loved tracks for {username}, but the cache has {cached_count}; fetching fresh data.</source>
        <translation>Last.fm meldet {online_count} Lieblingstitel für {username}, aber der Cache enthält {cached_count}; neue Daten werden abgerufen.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="281" />
        <source>Dependency check finished: {message}</source>
        <translation>Abhängigkeitsprüfung abgeschlossen: {message}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="298" />
        <source>Could not open data folder: {error}</source>
        <translation>Datenordner konnte nicht geöffnet werden: {error}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="308" />
        <source>Opened data folder: {path}</source>
        <translation>Datenordner geöffnet: {path}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="317" />
        <source>Could not open data folder: {path}</source>
        <translation>Datenordner konnte nicht geöffnet werden: {path}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="329" />
        <source>Could not open artist page: {url}</source>
        <translation>Künstlerseite konnte nicht geöffnet werden: {url}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="340" />
        <source>Last.fm scrobbling is disabled because {api_key_env}/{api_secret_env} are not configured and no bundled credentials are available.</source>
        <translation>Das Scrobbeln von Last.fm ist deaktiviert, da {api_key_env}/{api_secret_env} nicht konfiguriert sind und keine gebündelten Anmeldeinformationen verfügbar sind.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="355" />
        <source>Loaded Last.fm scrobbling settings; stored session key is {state}.</source>
        <translation>Last.fm-Scrobbling-Einstellungen geladen; der gespeicherte Sitzungsschlüssel ist {state}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="359" />
        <source>present</source>
        <translation>vorhanden</translation>
    </message>
    <message>
        <location filename="../controller.py" line="361" />
        <source>missing</source>
        <translation>fehlt</translation>
    </message>
    <message>
        <location filename="../controller.py" line="375" />
        <source>Connected Last.fm scrobbling as {username}.</source>
        <translation>Mit Last.fm verbunden; Scrobbling als {username}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="383" />
        <source>Stored Last.fm session key could not be verified; scrobbling remains disconnected.</source>
        <translation>Der gespeicherte Last.fm-Sitzungsschlüssel konnte nicht überprüft werden; Scrobbling bleibt getrennt.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="393" />
        <source>Opening preferences.</source>
        <translation>Einstellungen werden geöffnet.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="407" />
        <source>Preferences closed; no Last.fm scrobbling service is active.</source>
        <translation>Einstellungen geschlossen; es ist kein Last.fm-Scrobbling-Dienst aktiv.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="416" />
        <source>Saved Last.fm scrobbling preferences for {username}.</source>
        <translation>Last.fm-Scrobbling-Einstellungen für {username} gespeichert.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="420" />
        <source>no user</source>
        <translation>kein Benutzer</translation>
    </message>
    <message>
        <location filename="../controller.py" line="431" />
        <source>Enter a Last.fm username before fetching tracks.</source>
        <translation>Geben Sie einen Last.fm-Benutzernamen ein, bevor Sie Titel abrufen.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="442" />
        <source>Loaded cached tracks</source>
        <translation>Zwischengespeicherte Titel geladen</translation>
    </message>
    <message>
        <location filename="../controller.py" line="459" />
        <source>Could not reach Last.fm for {username}: {error}</source>
        <translation>Last.fm für {username} nicht erreichbar: {error}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="473" />
        <source>Starting fresh Last.fm fetch for {username}; {count} tracks expected.</source>
        <translation>Neuen Last.fm-Abruf für {username} starten; {count} Titel erwartet.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="482" />
        <source>Starting fresh Last.fm fetch for {username}.</source>
        <translation>Neuen Last.fm-Abruf für {username} starten.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="491" />
        <source>Starting fetch</source>
        <translation>Abruf wird gestartet</translation>
    </message>
    <message>
        <location filename="../controller.py" line="507" />
        <source>Fetch resumed.</source>
        <translation>Der Abruf wurde fortgesetzt.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="513" />
        <source>Fetch paused.</source>
        <translation>Abruf pausiert.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="523" />
        <source>Stopping fetch.</source>
        <translation>Abruf wird gestoppt.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="537" />
        <source>Enter a Last.fm username before resolving tracks.</source>
        <translation>Geben Sie einen Last.fm-Benutzernamen ein, bevor Sie Titel auflösen.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="546" />
        <source>Starting YouTube lookup for {username}; priority={priority}, limit={limit}.</source>
        <translation>YouTube-Suche für {username} wird gestartet; Priorität={priority}, Limit={limit}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="606" />
        <location filename="../controller.py" line="552" />
        <source>none</source>
        <translation>keine</translation>
    </message>
    <message>
        <location filename="../controller.py" line="610" />
        <location filename="../controller.py" line="556" />
        <source>all</source>
        <translation>alle</translation>
    </message>
    <message>
        <location filename="../controller.py" line="562" />
        <source>Starting YouTube lookup</source>
        <translation>YouTube-Suche wird gestartet</translation>
    </message>
    <message>
        <location filename="../controller.py" line="585" />
        <source>Enter a Last.fm username before downloading tracks.</source>
        <translation>Geben Sie einen Last.fm-Benutzernamen ein, bevor Sie Titel herunterladen.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="599" />
        <source>Starting downloads for {username}; concurrency={concurrency}, priority={priority}, limit={limit}.</source>
        <translation>Downloads für {username} werden gestartet; parallele Downloads={concurrency}, Priorität={priority}, Limit={limit}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="615" />
        <source>Starting downloads</source>
        <translation>Downloads starten</translation>
    </message>
    <message>
        <location filename="../controller.py" line="636" />
        <source>Select a downloaded track before playing.</source>
        <translation>Wählen Sie vor der Wiedergabe einen heruntergeladenen Titel aus.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="652" />
        <source>Playback resumed.</source>
        <translation>Die Wiedergabe wurde fortgesetzt.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="661" />
        <source>Playback paused.</source>
        <translation>Wiedergabe pausiert.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="689" />
        <location filename="../controller.py" line="670" />
        <source>No track is currently playing.</source>
        <translation>Derzeit wird kein Titel abgespielt.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="681" />
        <source>Playback stopped.</source>
        <translation>Die Wiedergabe wurde gestoppt.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="710" />
        <source>Seeked playback to {seconds} seconds.</source>
        <translation>Wiedergabe auf {seconds} Sekunden gesetzt.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="775" />
        <source>Fetch for {username} returned invalid track data.</source>
        <translation>Der Abruf für {username} hat ungültige Titeldaten zurückgegeben.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="785" />
        <source>Fetched and stored {count} tracks for {username}.</source>
        <translation>{count} Titel für {username} abgerufen und gespeichert.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="808" />
        <source>Stopped fetch for {username} returned invalid data.</source>
        <translation>Der Abruf für {username} wurde gestoppt und lieferte ungültige Daten.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="818" />
        <source>Stopped fetch for {username} after {count} tracks.</source>
        <translation>Der Abruf für {username} wurde nach {count} Titeln gestoppt.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="829" />
        <source>Fetch for {username} returned invalid partial data.</source>
        <translation>Der Abruf für {username} hat ungültige Teildaten zurückgegeben.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="840" />
        <source>Fetch progress for {username}: {count} tracks are visible now.</source>
        <translation>Abruffortschritt für {username}: {count} Titel sind jetzt sichtbar.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="848" />
        <source>Fetched {count} tracks for {username}</source>
        <translation>{count} Titel für {username} abgerufen</translation>
    </message>
    <message>
        <location filename="../controller.py" line="867" />
        <source>Workflow for {username} returned an invalid track update.</source>
        <translation>Der Workflow für {username} hat eine ungültige Titelaktualisierung zurückgegeben.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="877" />
        <source>Track update from {username}: {artist} - {title} is now {status}.</source>
        <translation>Titelaktualisierung von {username}: {artist} – {title} ist jetzt {status}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="892" />
        <source>Lookup for {username} returned invalid track data.</source>
        <translation>Die Suche für {username} hat ungültige Titeldaten zurückgegeben.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="908" />
        <source>Resolved YouTube URLs for {resolved_count}/{count} tracks; {not_found_count} were not found.</source>
        <translation>YouTube-URLs für {resolved_count}/{count} Titel aufgelöst; {not_found_count} wurden nicht gefunden.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="932" />
        <source>No queued tracks are ready for download.</source>
        <translation>Es stehen keine Titel in der Warteschlange zum Download bereit.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="943" />
        <source>Download for {username} returned invalid track data.</source>
        <translation>Der Download für {username} hat ungültige Titeldaten zurückgegeben.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="963" />
        <source>Download run for {username} finished: {downloaded_count}/{count} tracks downloaded, {failed_count} failed.</source>
        <translation>Download-Lauf für {username} abgeschlossen: {downloaded_count}/{count} Titel heruntergeladen, {failed_count} fehlgeschlagen.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="990" />
        <source>Failed</source>
        <translation>Fehlgeschlagen</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1028" />
        <source>Updating Last.fm now-playing for {artist} - {title}.</source>
        <translation>Last.fm-Wiedergabestatus für {artist} – {title} wird aktualisiert.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1037" />
        <source>Playing {artist} - {title}.</source>
        <translation>{artist} – {title} wird abgespielt.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1061" />
        <source>Last.fm returned invalid artist image data.</source>
        <translation>Last.fm hat ungültige Künstlerbilddaten zurückgegeben.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1091" />
        <source>Enter a Last.fm username before preparing playback.</source>
        <translation>Geben Sie einen Last.fm-Benutzernamen ein, bevor Sie die Wiedergabe vorbereiten.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1100" />
        <source>Preparing {artist} - {title} for playback.</source>
        <translation>{artist} – {title} wird für die Wiedergabe vorbereitet.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1117" />
        <source>Starting automatic YouTube lookup for {count} fetched tracks.</source>
        <translation>Automatische YouTube-Suche für {count} abgerufene Titel wird gestartet.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1133" />
        <source>Downloads stopped by user.</source>
        <translation>Downloads vom Benutzer gestoppt.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1142" />
        <source>Enter a Last.fm username before retrying a download.</source>
        <translation>Geben Sie einen Last.fm-Benutzernamen ein, bevor Sie einen Download erneut versuchen.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1160" />
        <source>Retrying download for {artist} - {title}.</source>
        <translation>Download für {artist} – {title} wird erneut versucht.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1173" />
        <source>Starting automatic download queue for resolved tracks.</source>
        <translation>Automatische Download-Warteschlange für aufgelöste Titel wird gestartet.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1181" />
        <source>Starting priority download for selected track.</source>
        <translation>Prioritäts-Download für den ausgewählten Titel wird gestartet.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1255" />
        <source>Submitting Last.fm scrobble for {artist} - {title}.</source>
        <translation>Last.fm-Scrobble für {artist} – {title} wird gesendet.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1285" />
        <source>Finished playback for {artist} - {title}.</source>
        <translation>Wiedergabe für {artist} – {title} abgeschlossen.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1305" />
        <location filename="../controller.py" line="1295" />
        <source>Playback finished.</source>
        <translation>Wiedergabe beendet.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1316" />
        <source>Continuing with random track: {artist} - {title}.</source>
        <translation>Weiter mit zufälligem Titel: {artist} – {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1327" />
        <source>Continuing with next track: {artist} - {title}.</source>
        <translation>Weiter mit dem nächsten Titel: {artist} – {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1347" />
        <source>All background work is finished; controls are enabled again.</source>
        <translation>Alle Hintergrundarbeiten sind abgeschlossen; die Steuerung ist wieder aktiviert.</translation>
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
        <location filename="../workers.py" line="79" />
        <source>Looking up Last.fm user {username}</source>
        <translation>Suche nach Last.fm-Benutzer {username}</translation>
    </message>
    <message>
        <location filename="../workers.py" line="95" />
        <source>Stopped fetch after {count} tracks</source>
        <translation>Der Abruf wurde nach {count} Titeln gestoppt</translation>
    </message>
    <message>
        <location filename="../workers.py" line="105" />
        <source>Fetched {count} tracks</source>
        <translation>{count} Titel abgerufen</translation>
    </message>
</context><context>
    <name>LastFmLovedTracksScraper</name>
    <message>
        <location filename="../lastfm.py" line="514" />
        <source>Found Last.fm user {username}</source>
        <translation>Last.fm-Benutzer {username} gefunden</translation>
    </message>
    <message>
        <location filename="../lastfm.py" line="904" />
        <source>Fetched {count} tracks</source>
        <translation>{count} Titel abgerufen</translation>
    </message>
    <message>
        <location filename="../lastfm.py" line="909" />
        <source>Fetched {done}/{total} tracks</source>
        <translation>{done}/{total} Titel abgerufen</translation>
    </message>
</context><context>
    <name>LookupTracksWorker</name>
    <message>
        <location filename="../workers.py" line="183" />
        <source>Resolving YouTube URLs for {username}</source>
        <translation>Auflösen von YouTube-URLs für {username}</translation>
    </message>
    <message>
        <location filename="../workers.py" line="199" />
        <source>Resolved {count} tracks</source>
        <translation>{count} Titel aufgelöst</translation>
    </message>
</context><context>
    <name>MainWindow</name>
    <message>
        <location filename="../ui/main_window.py" line="1007" />
        <location filename="../ui/main_window.py" line="187" />
        <source>Ready</source>
        <translation>Bereit</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="385" />
        <source>Retry Download</source>
        <translation>Download erneut versuchen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1000" />
        <location filename="../ui/main_window.py" line="478" />
        <source>Idle</source>
        <translation>Leerlauf</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="502" />
        <source>Loaded {count} tracks</source>
        <translation>{count} Titel geladen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="513" />
        <source>Playlist: {count} titles</source>
        <translation>Playlist: {count} Titel</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="534" />
        <source>Resume</source>
        <translation>Wieder aufnehmen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="976" />
        <location filename="../ui/main_window.py" line="534" />
        <source>Pause</source>
        <translation>Pause</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="977" />
        <location filename="../ui/main_window.py" line="535" />
        <source>Stop</source>
        <translation>Stoppen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="537" />
        <source>Resume the paused Last.fm fetch</source>
        <translation>Angehaltenen Last.fm-Abruf fortsetzen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="539" />
        <source>Pause the active Last.fm fetch</source>
        <translation>Aktiven Last.fm-Abruf pausieren</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="540" />
        <source>Stop the active Last.fm fetch</source>
        <translation>Aktiven Last.fm-Abruf stoppen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="985" />
        <location filename="../ui/main_window.py" line="550" />
        <source>Stop Downloads</source>
        <translation>Downloads stoppen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="985" />
        <location filename="../ui/main_window.py" line="554" />
        <source>Start Downloads</source>
        <translation>Downloads starten</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="672" />
        <source>Updated {artist} - {title}: {status}</source>
        <translation>Aktualisiert {artist} – {title}: {status}</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="974" />
        <location filename="../ui/main_window.py" line="689" />
        <source>Not playing</source>
        <translation>Keine Wiedergabe</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="955" />
        <location filename="../ui/main_window.py" line="747" />
        <source>About myLastFmPlayer</source>
        <translation>Über myLastFmPlayer</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="753" />
        <source>myLastFmPlayer {version}</source>
        <translation>myLastFmPlayer {version}</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="754" />
        <source>Author: Marcel Petrick &lt;a href="mailto:mail@marcelpetrick.it"&gt;mail@marcelpetrick.it&lt;/a&gt;</source>
        <translation>Autor: Marcel Petrick &lt;a href="mailto:mail@marcelpetrick.it"&gt;mail@marcelpetrick.it&lt;/a&gt;</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="758" />
        <source>License: GNU GPLv3 or later.</source>
        <translation>Lizenz: GNU GPLv3 oder neuer.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="759" />
        <source>This application fetches a user's public loved tracks from Last.fm, keeps local metadata, resolves playable sources through yt-dlp, downloads MP3 files, and plays them locally.</source>
        <translation>Diese Anwendung lädt die öffentlichen Lieblingslieder eines Benutzers von Last.fm, speichert lokale Metadaten, ermittelt abspielbare Quellen über yt-dlp, lädt MP3-Dateien herunter und spielt sie lokal ab.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="764" />
        <source>It is intended as a practical Linux desktop helper for rebuilding a personal loved-track collection without manually searching every song.</source>
        <translation>Sie ist als praktischer Linux-Desktophelfer gedacht, um eine persönliche Sammlung von Lieblingstiteln wiederaufzubauen, ohne jedes Lied manuell zu suchen.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="768" />
        <source>Optional Last.fm scrobbling can connect the local playback workflow back to the user's Last.fm account.</source>
        <translation>Optionales Last.fm-Scrobbling kann den lokalen Wiedergabeablauf wieder mit dem Last.fm-Konto des Benutzers verbinden.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="956" />
        <location filename="../ui/main_window.py" line="778" />
        <source>Open Source Licenses</source>
        <translation>Open-Source-Lizenzen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="784" />
        <source>myLastFmPlayer is GPLv3-or-later software and uses these open-source libraries and external tools:</source>
        <translation>myLastFmPlayer ist Software unter GPLv3 oder neuer und verwendet diese Open-Source-Bibliotheken und externen Werkzeuge:</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="848" />
        <location filename="../ui/main_window.py" line="790" />
        <source>Python Software Foundation License; runtime for the application.</source>
        <translation>Python Software Foundation License; Laufzeitumgebung für die Anwendung.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="850" />
        <location filename="../ui/main_window.py" line="794" />
        <source>GNU GPL v3; Python bindings for the Qt desktop interface.</source>
        <translation>GNU GPL v3; Python-Bindings für die Qt-Desktopoberfläche.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="851" />
        <location filename="../ui/main_window.py" line="798" />
        <source>GNU LGPL v3 / GPL v3; cross-platform UI toolkit.</source>
        <translation>GNU LGPL v3 / GPL v3; plattformübergreifendes UI-Toolkit.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="853" />
        <location filename="../ui/main_window.py" line="802" />
        <source>Apache License 2.0; HTTP client for Last.fm API calls.</source>
        <translation>Apache License 2.0; HTTP-Client für Last.fm-API-Aufrufe.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="854" />
        <location filename="../ui/main_window.py" line="806" />
        <source>Apache License 2.0; Last.fm scrobbling integration.</source>
        <translation>Apache License 2.0; Last.fm-Scrobbling-Integration.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="855" />
        <location filename="../ui/main_window.py" line="810" />
        <source>Unlicense; media lookup and download helper.</source>
        <translation>Unlicense; Helfer für Mediensuche und Download.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="857" />
        <location filename="../ui/main_window.py" line="814" />
        <source>LGPL/GPL family licenses depending on the installed build; audio conversion backend.</source>
        <translation>LGPL/GPL-Lizenzfamilie je nach installierter Version; Backend für Audiokonvertierung.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="819" />
        <source>Development tools include {tools} under their respective open-source licenses.</source>
        <translation>Zu den Entwicklungswerkzeugen gehören {tools} unter ihren jeweiligen Open-Source-Lizenzen.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="835" />
        <source>This summary is informational; the complete license texts are provided by the installed projects and system packages.</source>
        <translation>Diese Zusammenfassung dient zur Information; die vollständigen Lizenztexte werden von den installierten Projekten und Systempaketen bereitgestellt.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="952" />
        <source>Fetch loved tracks</source>
        <translation>Lieblingstitel abrufen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="953" />
        <source>Preferences</source>
        <translation>Einstellungen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="954" />
        <source>Open data folder in file manager</source>
        <translation>Datenordner im Dateimanager öffnen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="957" />
        <source>Quit</source>
        <translation>Beenden</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="958" />
        <source>Main</source>
        <translation>Hauptmenü</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="959" />
        <source>Theme</source>
        <translation>Thema</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="960" />
        <source>Light</source>
        <translation>Licht</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="961" />
        <source>Dark</source>
        <translation>Dunkel</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="962" />
        <source>Lilac</source>
        <translation>Lila</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="963" />
        <source>Mint</source>
        <translation>Minze</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="964" />
        <source>Language</source>
        <translation>Sprache</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="965" />
        <source>Help</source>
        <translation>Hilfe</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="966" />
        <source>Last.fm username</source>
        <translation>Last.fm-Benutzername</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="967" />
        <source>Enter username</source>
        <translation>Benutzernamen eingeben</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="968" />
        <source>Fetch</source>
        <translation>Abrufen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="969" />
        <source>Filter</source>
        <translation>Filter</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="970" />
        <source>Artist or track title</source>
        <translation>Künstler oder Titel</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="971" />
        <source>Reset</source>
        <translation>Zurücksetzen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="972" />
        <source>Playback</source>
        <translation>Wiedergabe</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="975" />
        <source>Play</source>
        <translation>Abspielen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="978" />
        <source>Next</source>
        <translation>Weiter</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="979" />
        <source>Randomize</source>
        <translation>Zufallswiedergabe</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="980" />
        <source>Artist</source>
        <translation>Künstler</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="981" />
        <source>Open artist page on Last.fm</source>
        <translation>Künstlerseite auf Last.fm öffnen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="982" />
        <source>Playback position</source>
        <translation>Wiedergabeposition</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="983" />
        <source>Downloads</source>
        <translation>Downloads</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="987" />
        <source>Clear log</source>
        <translation>Protokoll löschen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="988" />
        <source>Clear status updates and errors</source>
        <translation>Statusmeldungen und Fehler löschen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="990" />
        <source>Status updates and errors will appear here.</source>
        <translation>Statusmeldungen und Fehler werden hier angezeigt.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="997" />
        <source>Dependencies: yt-dlp, ffmpeg, and ffprobe not checked yet</source>
        <translation>Abhängigkeiten: yt-dlp, ffmpeg und ffprobe noch nicht überprüft</translation>
    </message>
    <message>
        <source>MIT License; legacy Last.fm HTML parser support.</source>
        <translation type="vanished">MIT License; Unterstützung für den alten Last.fm-HTML-Parser.</translation>
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
        <location filename="../ui/preferences_dialog.py" line="175" />
        <location filename="../ui/preferences_dialog.py" line="135" />
        <source>None (disabled)</source>
        <translation>Keine (deaktiviert)</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="155" />
        <source>Preferences</source>
        <translation>Einstellungen</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="156" />
        <source>Last.fm Authentication</source>
        <translation>Last.fm-Authentifizierung</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="157" />
        <source>Authenticate with Last.fm</source>
        <translation>Mit Last.fm authentifizieren</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="158" />
        <source>I've authorized</source>
        <translation>Ich habe autorisiert</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="159" />
        <source>Disconnect</source>
        <translation>Trennen</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="160" />
        <source>Scrobbling</source>
        <translation>Scrobbeln</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="161" />
        <source>Enable scrobbling</source>
        <translation>Scrobbeln aktivieren</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="163" />
        <source>Submits to Last.fm after 33% of each track has been played.</source>
        <translation>Wird an Last.fm übermittelt, nachdem 33 % jedes Titels abgespielt wurden.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="165" />
        <source>YouTube Downloads</source>
        <translation>YouTube-Downloads</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="166" />
        <source>Browser cookies:</source>
        <translation>Browser-Cookies:</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="167" />
        <source>Parallel downloads:</source>
        <translation>Parallele Downloads:</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="169" />
        <source>Select the browser whose YouTube login cookies yt-dlp should use. Required for age-restricted videos. You must be signed into YouTube in the selected browser. Parallel download changes apply to new work.</source>
        <translation>Wählen Sie den Browser, dessen YouTube-Anmelde-Cookies yt-dlp verwenden soll. Erforderlich für altersbeschränkte Videos. Sie müssen im ausgewählten Browser bei YouTube angemeldet sein. Änderungen an parallelen Downloads gelten für neue Aufgaben.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="176" />
        <source>Privacy</source>
        <translation>Datenschutz</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="177" />
        <source>Keep cached data after quitting</source>
        <translation>Zwischengespeicherte Daten nach dem Beenden behalten</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="183" />
        <source>⚠ API credentials not configured.
Set LASTFM_API_KEY and LASTFM_API_SECRET environment variables.</source>
        <translation>⚠ API-Anmeldeinformationen nicht konfiguriert. 
Legen Sie die Umgebungsvariablen LASTFM_API_KEY und LASTFM_API_SECRET fest.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="202" />
        <source>🟢 Connected as {username}</source>
        <translation>🟢 Verbunden als {username}</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="211" />
        <source>🔵 Browser opened — authorize the app, then click «I've authorized».</source>
        <translation>🔵 Browser geöffnet – Autorisieren Sie die App und klicken Sie dann auf „Ich habe autorisiert“.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="217" />
        <source>🔴 Not connected</source>
        <translation>🔴 Nicht verbunden</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="240" />
        <source>⚠ Could not start authentication. Check API credentials.</source>
        <translation>⚠ Die Authentifizierung konnte nicht gestartet werden. Überprüfen Sie die API-Anmeldeinformationen.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="251" />
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
        <translation>Künstler</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="96" />
        <source>Title</source>
        <translation>Titel</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="98" />
        <source>Loved at</source>
        <translation>Favorisiert am</translation>
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
        <translation>Wartet auf Umsetzung</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="210" />
        <source>Fetched</source>
        <translation>Abgerufen</translation>
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
        <translation>Suche {done}/{total}: {artist} – {title}</translation>
    </message>
    <message>
        <location filename="../youtube.py" line="236" />
        <source>Resolved {done}/{total}: {artist} - {title}</source>
        <translation>Aufgelöst {done}/{total}: {artist} – {title}</translation>
    </message>
    <message>
        <location filename="../youtube.py" line="244" />
        <source>No YouTube result {done}/{total}: {artist} - {title}</source>
        <translation>Kein YouTube-Ergebnis {done}/{total}: {artist} – {title}</translation>
    </message>
</context></TS>

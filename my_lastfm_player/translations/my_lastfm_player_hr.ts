<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>ApplicationController</name>
    <message>
        <location filename="../controller.py" line="149" />
        <source>No cached tracks found for {username}; fetching from Last.fm.</source>
        <translation>Nisu pronađene predmemorirane staze za {username}; dohvaćanje s Last.fm.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="160" />
        <source>Found {count} cached tracks for {username}; checking Last.fm before using them.</source>
        <translation>Pronađeno {count} predmemoriranih zapisa za {username}; provjeravajući Last.fm prije korištenja.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="180" />
        <source>Loaded {count} cached tracks for {username}; skipped Last.fm fetch.</source>
        <translation>Učitano {count} predmemoriranih zapisa za {username}; preskočen Last.fm dohvaćanje.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="194" />
        <source>Could not verify Last.fm loved-track count for {username}; using {count} cached tracks: {error}</source>
        <translation>Nije moguće potvrditi Last.fm broj voljenih pjesama za {username}; korištenje {count} predmemoriranih staza: {error}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="207" />
        <source>Could not read Last.fm loved-track count for {username}; fetching fresh data instead of trusting {count} cached tracks.</source>
        <translation>Nije moguće pročitati Last.fm broj omiljenih pjesama za {username}; dohvaćanje svježih podataka umjesto vjerovanja {count} predmemoriranim stazama.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="219" />
        <source>Last.fm reports {online_count} loved tracks for {username}; cached track count matches.</source>
        <translation>Last.fm izvještava o {online_count} omiljenih pjesama za {username}; predmemorirana podudaranja broja pjesama.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="230" />
        <source>Last.fm reports {online_count} loved tracks for {username}, but the cache has {cached_count}; fetching fresh data.</source>
        <translation>Last.fm izvještava o {online_count} omiljenih pjesama za {username}, ali predmemorija ima {cached_count}; dohvaćanje svježih podataka.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="255" />
        <source>Dependency check finished: {message}</source>
        <translation>Provjera ovisnosti završena: {message}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="272" />
        <source>Could not open data folder: {error}</source>
        <translation>Nije moguće otvoriti mapu podataka: {error}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="282" />
        <source>Opened data folder: {path}</source>
        <translation>Otvorena mapa podataka: {path}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="291" />
        <source>Could not open data folder: {path}</source>
        <translation>Nije moguće otvoriti mapu podataka: {path}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="302" />
        <source>Last.fm scrobbling is disabled because {api_key_env}/{api_secret_env} are not configured and no bundled credentials are available.</source>
        <translation>Listanje po Last.fm-u je onemogućeno jer {api_key_env}/{api_secret_env} nisu konfigurirani i nisu dostupne skupne vjerodajnice.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="317" />
        <source>Loaded Last.fm scrobbling settings; stored session key is {state}.</source>
        <translation>Učitane postavke listanja po Last.fm-u; pohranjeni ključ sesije je {state}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="321" />
        <source>present</source>
        <translation>predstaviti</translation>
    </message>
    <message>
        <location filename="../controller.py" line="323" />
        <source>missing</source>
        <translation>nedostaje</translation>
    </message>
    <message>
        <location filename="../controller.py" line="337" />
        <source>Connected Last.fm scrobbling as {username}.</source>
        <translation>Povezan Last.fm listajući kao {username}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="345" />
        <source>Stored Last.fm session key could not be verified; scrobbling remains disconnected.</source>
        <translation>Pohranjeni Last.fm ključ sesije ne može se provjeriti; scrobbling ostaje isključen.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="355" />
        <source>Opening preferences.</source>
        <translation>Otvaranje postavki.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="369" />
        <source>Preferences closed; no Last.fm scrobbling service is active.</source>
        <translation>Postavke zatvorene; usluga skrobiranja Last.fm nije aktivna.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="378" />
        <source>Saved Last.fm scrobbling preferences for {username}.</source>
        <translation>Spremljene postavke skrobiranja Last.fm za {username}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="382" />
        <source>no user</source>
        <translation>nema korisnika</translation>
    </message>
    <message>
        <location filename="../controller.py" line="393" />
        <source>Enter a Last.fm username before fetching tracks.</source>
        <translation>Unesite Last.fm korisničko ime prije dohvaćanja zapisa.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="404" />
        <source>Loaded cached tracks</source>
        <translation>Učitane staze u predmemoriju</translation>
    </message>
    <message>
        <location filename="../controller.py" line="414" />
        <source>Starting fresh Last.fm fetch for {username}.</source>
        <translation>Pokretanje novog dohvaćanja Last.fm-a za {username}.</translation>
    </message>
    <message>
        <source>Could not reach Last.fm for {username}: {error}</source>
        <translation>Last.fm za {username} nije dostupan: {error}</translation>
    </message>
    <message>
        <source>Starting fresh Last.fm fetch for {username}; {count} tracks expected.</source>
        <translation>Pokretanje novog dohvaćanja Last.fm-a za {username}; očekuje se {count} zapisa.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="423" />
        <source>Starting fetch</source>
        <translation>Počinje dohvaćanje</translation>
    </message>
    <message>
        <location filename="../controller.py" line="439" />
        <source>Fetch resumed.</source>
        <translation>Dohvaćanje je nastavljeno.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="445" />
        <source>Fetch paused.</source>
        <translation>Dohvaćanje pauzirano.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="455" />
        <source>Stopping fetch.</source>
        <translation>Zaustavljanje dohvaćanja.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="469" />
        <source>Enter a Last.fm username before resolving tracks.</source>
        <translation>Unesite Last.fm korisničko ime prije rješavanja zapisa.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="479" />
        <source>Starting YouTube lookup for {username}; priority={priority}, limit={limit}.</source>
        <translation>Pokretanje YouTube traženja za {username}; prioritet={priority}, limit={limit}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="544" />
        <location filename="../controller.py" line="485" />
        <source>none</source>
        <translation>nikakav</translation>
    </message>
    <message>
        <location filename="../controller.py" line="548" />
        <location filename="../controller.py" line="489" />
        <source>all</source>
        <translation>sve</translation>
    </message>
    <message>
        <location filename="../controller.py" line="495" />
        <source>Starting YouTube lookup</source>
        <translation>Pokretanje YouTube pretraživanja</translation>
    </message>
    <message>
        <location filename="../controller.py" line="518" />
        <source>Enter a Last.fm username before downloading tracks.</source>
        <translation>Unesite Last.fm korisničko ime prije preuzimanja pjesama.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="537" />
        <source>Starting downloads for {username}; concurrency={concurrency}, priority={priority}, limit={limit}.</source>
        <translation>Pokretanje preuzimanja za {username}; concurrency={concurrency}, priority={priority}, limit={limit}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="553" />
        <source>Starting downloads</source>
        <translation>Pokretanje preuzimanja</translation>
    </message>
    <message>
        <location filename="../controller.py" line="574" />
        <source>Select a downloaded track before playing.</source>
        <translation>Odaberite preuzetu pjesmu prije reprodukcije.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="590" />
        <source>Playback resumed.</source>
        <translation>Reprodukcija je nastavljena.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="599" />
        <source>Playback paused.</source>
        <translation>Reprodukcija je pauzirana.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="608" />
        <source>No track is currently playing.</source>
        <translation>Trenutno se ne reproducira nijedna pjesma.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="618" />
        <source>Playback stopped.</source>
        <translation>Reprodukcija zaustavljena.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="635" />
        <source>Seeked playback to {seconds} seconds.</source>
        <translation>Tražena reprodukcija do {seconds} sekundi.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="690" />
        <source>Fetch for {username} returned invalid track data.</source>
        <translation>Dohvaćanje za {username} vratilo je nevažeće podatke o stazi.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="700" />
        <source>Fetched and stored {count} tracks for {username}.</source>
        <translation>Dohvaćeno i pohranjeno {count} zapisa za {username}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="727" />
        <source>Stopped fetch for {username} returned invalid data.</source>
        <translation>Zaustavljeno dohvaćanje za {username} vratilo je nevažeće podatke.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="737" />
        <source>Stopped fetch for {username} after {count} tracks.</source>
        <translation>Zaustavljeno dohvaćanje za {username} nakon {count} zapisa.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="748" />
        <source>Fetch for {username} returned invalid partial data.</source>
        <translation>Dohvaćanje za {username} vratilo je nevažeće djelomične podatke.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="759" />
        <source>Fetch progress for {username}: {count} tracks are visible now.</source>
        <translation>Dohvaćanje napretka za {username}: sada je vidljivo {count} zapisa.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="767" />
        <source>Fetched {count} tracks for {username}</source>
        <translation>Dohvaćeno {count} zapisa za {username}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="786" />
        <source>Workflow for {username} returned an invalid track update.</source>
        <translation>Tijek rada za {username} vratio je nevažeće ažuriranje zapisa.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="796" />
        <source>Track update from {username}: {artist} - {title} is now {status}.</source>
        <translation>Ažuriranje pjesme od {username}: {artist} - {title} je sada {status}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="811" />
        <source>Lookup for {username} returned invalid track data.</source>
        <translation>Traženje za {username} vratilo je nevažeće podatke o stazi.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="829" />
        <source>Resolved YouTube URLs for {resolved_count}/{count} tracks; {not_found_count} were not found.</source>
        <translation>Riješeni YouTube URL-ovi za {resolved_count}/{count} pjesama; {not_found_count} nije pronađeno.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="853" />
        <source>No queued tracks are ready for download.</source>
        <translation>Nijedna pjesma u redu čekanja nije spremna za preuzimanje.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="864" />
        <source>Download for {username} returned invalid track data.</source>
        <translation>Preuzimanje za {username} vratilo je nevažeće podatke o stazi.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="884" />
        <source>Download run for {username} finished: {downloaded_count}/{count} tracks downloaded, {failed_count} failed.</source>
        <translation>Preuzimanje za {username} je završeno: {downloaded_count}/{count} zapisa preuzeto, {failed_count} nije uspjelo.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="912" />
        <source>Failed</source>
        <translation>neuspješno</translation>
    </message>
    <message>
        <location filename="../controller.py" line="949" />
        <source>Updating Last.fm now-playing for {artist} - {title}.</source>
        <translation>Ažuriranje Last.fm-a sada svira za {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="958" />
        <source>Playing {artist} - {title}.</source>
        <translation>Sviranje {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="977" />
        <source>Enter a Last.fm username before preparing playback.</source>
        <translation>Unesite Last.fm korisničko ime prije pripreme reprodukcije.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="986" />
        <source>Preparing {artist} - {title} for playback.</source>
        <translation>Priprema {artist} - {title} za reprodukciju.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1003" />
        <source>Starting automatic YouTube lookup for {count} fetched tracks.</source>
        <translation>Pokretanje automatskog YouTube traženja {count} dohvaćenih pjesama.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1019" />
        <source>Downloads stopped by user.</source>
        <translation>Preuzimanja je zaustavio korisnik.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1028" />
        <source>Enter a Last.fm username before retrying a download.</source>
        <translation>Unesite Last.fm korisničko ime prije ponovnog pokušaja preuzimanja.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1046" />
        <source>Retrying download for {artist} - {title}.</source>
        <translation>Ponovni pokušaj preuzimanja za {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1059" />
        <source>Starting automatic download queue for resolved tracks.</source>
        <translation>Pokretanje automatskog čekanja za preuzimanje za riješene zapise.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1067" />
        <source>Starting priority download for selected track.</source>
        <translation>Pokretanje prioritetnog preuzimanja za odabranu pjesmu.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1141" />
        <source>Submitting Last.fm scrobble for {artist} - {title}.</source>
        <translation>Slanje Last.fm scrobble za {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1170" />
        <source>Finished playback for {artist} - {title}.</source>
        <translation>Završena reprodukcija za {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1180" />
        <source>Playback finished.</source>
        <translation>Reprodukcija završena.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1187" />
        <source>Continuing with next track: {artist} - {title}.</source>
        <translation>Nastavak sa sljedećom pjesmom: {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1202" />
        <source>All background work is finished; controls are enabled again.</source>
        <translation>Svi pozadinski radovi su završeni; kontrole su ponovno omogućene.</translation>
    </message>
    <message>
        <source>Could not open file cache: {error}</source>
        <translation type="vanished">Nije moguće otvoriti predmemoriju datoteke: {error}</translation>
    </message>
    <message>
        <source>Opened file cache: {path}</source>
        <translation type="vanished">Otvorena predmemorija datoteke: {path}</translation>
    </message>
    <message>
        <source>Could not open file cache: {path}</source>
        <translation type="vanished">Nije moguće otvoriti predmemoriju datoteke: {path}</translation>
    </message>
    <message>
        <source>Resolved YouTube URLs for {count} tracks.</source>
        <translation type="vanished">Riješeni YouTube URL-ovi za {count} pjesama.</translation>
    </message>
    <message>
        <source>Downloaded {count} tracks for {username}.</source>
        <translation type="vanished">Preuzeto {count} pjesama za {username}.</translation>
    </message>
</context><context>
    <name>DependencyCheckResult</name>
    <message>
        <location filename="../dependencies.py" line="30" />
        <source>Dependencies installed: {tools}</source>
        <translation>Instalirane ovisnosti: {tools}</translation>
    </message>
    <message>
        <location filename="../dependencies.py" line="35" />
        <source>Missing dependencies: {tools}</source>
        <translation>Nedostaju ovisnosti: {tools}</translation>
    </message>
</context><context>
    <name>DownloadManager</name>
    <message>
        <location filename="../download.py" line="124" />
        <source>Queued {count} downloads</source>
        <translation>U redu {count} preuzimanja</translation>
    </message>
    <message>
        <location filename="../download.py" line="153" />
        <source>Downloaded {done}/{total} tracks</source>
        <translation>Preuzeto {done}/{total} pjesama</translation>
    </message>
</context><context>
    <name>FetchLovedTracksWorker</name>
    <message>
        <location filename="../workers.py" line="54" />
        <source>Looking up Last.fm user {username}</source>
        <translation>Traženje Last.fm korisnika {username}</translation>
    </message>
    <message>
        <location filename="../workers.py" line="70" />
        <source>Stopped fetch after {count} tracks</source>
        <translation>Zaustavljeno dohvaćanje nakon {count} zapisa</translation>
    </message>
    <message>
        <location filename="../workers.py" line="80" />
        <source>Fetched {count} tracks</source>
        <translation>Dohvaćeno {count} zapisa</translation>
    </message>
</context><context>
    <name>LastFmLovedTracksScraper</name>
    <message>
        <location filename="../lastfm.py" line="253" />
        <source>Found Last.fm user {username}</source>
        <translation>Pronađen Last.fm korisnik {username}</translation>
    </message>
    <message>
        <location filename="../lastfm.py" line="455" />
        <source>Fetched {count} tracks</source>
        <translation>Dohvaćeno {count} zapisa</translation>
    </message>
    <message>
        <location filename="../lastfm.py" line="460" />
        <source>Fetched {done}/{total} tracks</source>
        <translation>Dohvaćeno {done}/{total} pjesama</translation>
    </message>
</context><context>
    <name>LookupTracksWorker</name>
    <message>
        <location filename="../workers.py" line="176" />
        <source>Resolving YouTube URLs for {username}</source>
        <translation>Rješavanje YouTube URL-ova za {username}</translation>
    </message>
    <message>
        <location filename="../workers.py" line="192" />
        <source>Resolved {count} tracks</source>
        <translation>Riješeno {count} zapisa</translation>
    </message>
</context><context>
    <name>MainWindow</name>
    <message>
        <location filename="../ui/main_window.py" line="643" />
        <location filename="../ui/main_window.py" line="77" />
        <source>Ready</source>
        <translation>Spreman</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="233" />
        <source>Retry Download</source>
        <translation>Ponovi preuzimanje</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="636" />
        <location filename="../ui/main_window.py" line="308" />
        <source>Idle</source>
        <translation>besposlen</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="332" />
        <source>Loaded {count} tracks</source>
        <translation>Učitano {count} zapisa</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="343" />
        <source>Playlist: {count} titles</source>
        <translation>Popis za reprodukciju: {count} naslova</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="364" />
        <source>Resume</source>
        <translation>Nastavi</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="616" />
        <location filename="../ui/main_window.py" line="364" />
        <source>Pause</source>
        <translation>Pauza</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="617" />
        <location filename="../ui/main_window.py" line="365" />
        <source>Stop</source>
        <translation>Stop</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="367" />
        <source>Resume the paused Last.fm fetch</source>
        <translation>Nastavite pauzirano dohvaćanje Last.fm-a</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="369" />
        <source>Pause the active Last.fm fetch</source>
        <translation>Pauzirajte aktivno dohvaćanje Last.fm-a</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="370" />
        <source>Stop the active Last.fm fetch</source>
        <translation>Zaustavite aktivno dohvaćanje Last.fm-a</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="621" />
        <location filename="../ui/main_window.py" line="380" />
        <source>Stop Downloads</source>
        <translation>Zaustavi preuzimanja</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="621" />
        <location filename="../ui/main_window.py" line="384" />
        <source>Start Downloads</source>
        <translation>Pokreni preuzimanja</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="459" />
        <source>Updated {artist} - {title}: {status}</source>
        <translation>Ažurirano {artist} - {title}: {status}</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="614" />
        <location filename="../ui/main_window.py" line="475" />
        <source>Not playing</source>
        <translation>Ne reproducira se</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="598" />
        <source>Fetch loved tracks</source>
        <translation>Dohvatite omiljene pjesme</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="599" />
        <source>Preferences</source>
        <translation>Postavke</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="600" />
        <source>Open data folder in file manager</source>
        <translation>Otvori mapu podataka u upravitelju datoteka</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="601" />
        <source>Quit</source>
        <translation>Prestati</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="602" />
        <source>Main</source>
        <translation>Glavni</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="603" />
        <source>Theme</source>
        <translation>Tema</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="604" />
        <source>Light</source>
        <translation>Svjetlo</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="605" />
        <source>Dark</source>
        <translation>tamno</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="606" />
        <source>Lilac</source>
        <translation>Lila</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="607" />
        <source>Mint</source>
        <translation>Kovnica</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="608" />
        <source>Language</source>
        <translation>Jezik</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="609" />
        <source>Last.fm username</source>
        <translation>Last.fm korisničko ime</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="610" />
        <source>Enter username</source>
        <translation>Unesite korisničko ime</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="611" />
        <source>Fetch</source>
        <translation>Dohvati</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="612" />
        <source>Playback</source>
        <translation>Reprodukcija</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="615" />
        <source>Play</source>
        <translation>Igrati</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="618" />
        <source>Playback position</source>
        <translation>Položaj reprodukcije</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="619" />
        <source>Downloads</source>
        <translation>Preuzimanja</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="623" />
        <source>Clear log</source>
        <translation>Obriši dnevnik</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="624" />
        <source>Clear status updates and errors</source>
        <translation>Obriši ažuriranja statusa i pogreške</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="626" />
        <source>Status updates and errors will appear here.</source>
        <translation>Ovdje će se pojaviti ažuriranja statusa i pogreške.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="633" />
        <source>Dependencies: yt-dlp and ffmpeg not checked yet</source>
        <translation>Zavisnosti: yt-dlp i ffmpeg još nisu provjereni</translation>
    </message>
    <message>
        <source>Cached songs storage location</source>
        <translation type="vanished">Mjesto pohrane spremljenih pjesama</translation>
    </message>
    <message>
        <source>Download Queued</source>
        <translation type="vanished">Preuzimanje na čekanju</translation>
    </message>
    <message>
        <source>Concurrency</source>
        <translation type="vanished">Podudarnost</translation>
    </message>
    <message>
        <source>This control is part of the MVP shell and will be wired in later steps.</source>
        <translation type="vanished">Ova kontrola je dio MVP ljuske i bit će spojena u kasnijim koracima.</translation>
    </message>
</context><context>
    <name>PreferencesDialog</name>
    <message>
        <location filename="../ui/preferences_dialog.py" line="163" />
        <location filename="../ui/preferences_dialog.py" line="123" />
        <source>None (disabled)</source>
        <translation>Nijedan (onemogućeno)</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="143" />
        <source>Preferences</source>
        <translation>Postavke</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="144" />
        <source>Last.fm Authentication</source>
        <translation>Last.fm Autentifikacija</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="145" />
        <source>Authenticate with Last.fm</source>
        <translation>Autentificirajte se s Last.fm</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="146" />
        <source>I've authorized</source>
        <translation>Ovlastio sam</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="147" />
        <source>Disconnect</source>
        <translation>Prekini vezu</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="148" />
        <source>Scrobbling</source>
        <translation>Scrobbling</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="149" />
        <source>Enable scrobbling</source>
        <translation>Omogući listanje</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="151" />
        <source>Submits to Last.fm after 33% of each track has been played.</source>
        <translation>Šalje se na Last.fm nakon što se 33% svake pjesme pusti.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="153" />
        <source>YouTube Downloads</source>
        <translation>YouTube preuzimanja</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="154" />
        <source>Browser cookies:</source>
        <translation>Kolačići preglednika:</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="155" />
        <source>Parallel downloads:</source>
        <translation>Paralelna preuzimanja:</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="157" />
        <source>Select the browser whose YouTube login cookies yt-dlp should use. Required for age-restricted videos. You must be signed into YouTube in the selected browser. Parallel download changes apply to new work.</source>
        <translation>Odaberite preglednik čije YouTube kolačiće prijave yt-dlp treba koristiti. Potrebno za videozapise s dobnim ograničenjem. Morate biti prijavljeni na YouTube u odabranom pregledniku. Promjene paralelnih preuzimanja primjenjuju se na novi rad.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="164" />
        <source>Privacy</source>
        <translation>Privatnost</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="165" />
        <source>Keep cached data after quitting</source>
        <translation>Zadrži predmemorirane podatke nakon izlaska</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="170" />
        <source>⚠ API credentials not configured.
Set LASTFM_API_KEY and LASTFM_API_SECRET environment variables.</source>
        <translation>⚠ API vjerodajnice nisu konfigurirane. 
Postavite varijable okoline LASTFM_API_KEY i LASTFM_API_SECRET.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="188" />
        <source>🟢 Connected as {username}</source>
        <translation>🟢 Povezan kao {username}</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="197" />
        <source>🔵 Browser opened — authorize the app, then click «I've authorized».</source>
        <translation>🔵 Preglednik je otvoren — autorizirajte aplikaciju, zatim kliknite «Autorizirao sam».</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="203" />
        <source>🔴 Not connected</source>
        <translation>🔴 Nije povezano</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="216" />
        <source>⚠ Could not start authentication. Check API credentials.</source>
        <translation>⚠ Nije moguće pokrenuti provjeru autentičnosti. Provjerite API vjerodajnice.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="227" />
        <source>⚠ Authorization not confirmed yet. Authorize in the browser, then try again.</source>
        <translation>⚠ Autorizacija još nije potvrđena. Autorizirajte se u pregledniku, a zatim pokušajte ponovno.</translation>
    </message>
    <message>
        <source>Submits to Last.fm after 10 % of each track has been played.</source>
        <translation type="vanished">Predaje se na Last.fm nakon puštanja 10 % svake pjesme.</translation>
    </message>
</context><context>
    <name>TrackTableModel</name>
    <message>
        <location filename="../ui/track_table_model.py" line="94" />
        <source>Artist</source>
        <translation>Umjetnik</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="96" />
        <source>Title</source>
        <translation>Titula</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="98" />
        <source>Loved at</source>
        <translation>Označeno kao omiljeno</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="100" />
        <source>Status</source>
        <translation>Status</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="102" />
        <source>File</source>
        <translation>File</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="195" />
        <source>Example Artist</source>
        <translation>Primjer umjetnika</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="196" />
        <source>Example Track</source>
        <translation>Primjer zapisa</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="200" />
        <source>Another Artist</source>
        <translation>Još jedan umjetnik</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="201" />
        <source>Waiting for implementation</source>
        <translation>Čeka se implementacija</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="210" />
        <source>Fetched</source>
        <translation>Dohvaćeno</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="212" />
        <source>Queued</source>
        <translation>U redu čekanja</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="214" />
        <source>Searching</source>
        <translation>Traženje</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="216" />
        <source>Downloading</source>
        <translation>Preuzimanje</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="218" />
        <source>Downloaded</source>
        <translation>Preuzeto</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="220" />
        <source>Failed</source>
        <translation>neuspješno</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="222" />
        <source>Not found</source>
        <translation>Nije pronađeno</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="237" />
        <source>{bitrate} kbps</source>
        <translation>{bitrate} kbps</translation>
    </message>
</context><context>
    <name>YouTubeResolver</name>
    <message>
        <location filename="../youtube.py" line="88" />
        <source>Searching {done}/{total}: {artist} - {title}</source>
        <translation>Pretraživanje {done}/{total}: ​​{artist} - {title}</translation>
    </message>
    <message>
        <location filename="../youtube.py" line="233" />
        <source>Resolved {done}/{total}: {artist} - {title}</source>
        <translation>Riješeno {done}/{total}: {artist} - {title}</translation>
    </message>
    <message>
        <location filename="../youtube.py" line="241" />
        <source>No YouTube result {done}/{total}: {artist} - {title}</source>
        <translation>Nema YouTube rezultata {done}/{total}: ​​{artist} - {title}</translation>
    </message>
</context></TS>

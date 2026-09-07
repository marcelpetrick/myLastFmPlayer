<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>ApplicationController</name>
    <message>
        <location filename="../controller.py" line="219" />
        <source>Re-checking {missing} not-found and {failed} failed tracks from the last run.</source>
        <translation>Ponovna provjera {missing} nepronađenih i {failed} neuspjelih pjesama iz prošlog pokretanja.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="289" />
        <source>Stopping background work for {username}; completed items remain saved.</source>
        <translation>Zaustavlja se pozadinski rad za {username}; dovršene stavke ostaju spremljene.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="336" />
        <source>No cached tracks found for {username}; fetching from Last.fm.</source>
        <translation>Nema spremljenih pjesama za {username}; dohvaćaju se s Last.fm-a.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="347" />
        <source>Found {count} cached tracks for {username}; checking Last.fm before using them.</source>
        <translation>Pronađeno je {count} spremljenih pjesama za {username}; provjerava se Last.fm prije korištenja.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="367" />
        <source>Loaded {count} cached tracks for {username}; skipped Last.fm fetch.</source>
        <translation>Učitano je {count} spremljenih pjesama za {username}; preskočeno je dohvaćanje s Last.fm-a.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="381" />
        <source>Could not verify Last.fm loved-track count for {username}; using {count} cached tracks: {error}</source>
        <translation>Nije moguće provjeriti broj omiljenih pjesama na Last.fm-u za {username}; koristi se {count} spremljenih pjesama: {error}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="394" />
        <source>Could not read Last.fm loved-track count for {username}; fetching fresh data instead of trusting {count} cached tracks.</source>
        <translation>Nije moguće pročitati broj omiljenih pjesama na Last.fm-u za {username}; dohvaćaju se novi podaci umjesto korištenja {count} spremljenih pjesama.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="406" />
        <source>Last.fm reports {online_count} loved tracks for {username}; cached track count matches.</source>
        <translation>Last.fm javlja {online_count} omiljenih pjesama za {username}; broj spremljenih pjesama se podudara.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="417" />
        <source>Last.fm reports {online_count} loved tracks for {username}, but the cache has {cached_count}; fetching fresh data.</source>
        <translation>Last.fm javlja {online_count} omiljenih pjesama za {username}, ali lokalno je spremljeno {cached_count}; dohvaćaju se novi podaci.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="442" />
        <source>Dependency check finished: {message}</source>
        <translation>Provjera ovisnosti završena: {message}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="459" />
        <source>Could not open data folder: {error}</source>
        <translation>Nije moguće otvoriti mapu podataka: {error}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="469" />
        <source>Opened data folder: {path}</source>
        <translation>Otvorena mapa podataka: {path}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="478" />
        <source>Could not open data folder: {path}</source>
        <translation>Nije moguće otvoriti mapu podataka: {path}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="490" />
        <source>Could not open artist page: {url}</source>
        <translation>Nije moguće otvoriti stranicu izvođača: {url}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="501" />
        <source>Last.fm scrobbling is disabled because {api_key_env}/{api_secret_env} are not configured and no bundled credentials are available.</source>
        <translation>Last.fm skroblanje je onemogućeno jer {api_key_env}/{api_secret_env} nisu konfigurirani i nisu dostupne isporučene vjerodajnice.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="516" />
        <source>Loaded Last.fm scrobbling settings; stored session key is {state}.</source>
        <translation>Učitane su postavke Last.fm skroblanja; pohranjeni ključ sesije je {state}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="520" />
        <source>present</source>
        <translation>prisutan</translation>
    </message>
    <message>
        <location filename="../controller.py" line="522" />
        <source>missing</source>
        <translation>nedostaje</translation>
    </message>
    <message>
        <location filename="../controller.py" line="536" />
        <source>Connected Last.fm scrobbling as {username}.</source>
        <translation>Last.fm skroblanje povezano je za korisnika {username}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="544" />
        <source>Stored Last.fm session key could not be verified; scrobbling remains disconnected.</source>
        <translation>Pohranjeni Last.fm ključ sesije nije moguće provjeriti; skroblanje ostaje nepovezano.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="554" />
        <source>Opening preferences.</source>
        <translation>Otvaranje postavki.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="568" />
        <source>Preferences closed; no Last.fm scrobbling service is active.</source>
        <translation>Postavke su zatvorene; nijedna usluga Last.fm skroblanja nije aktivna.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="577" />
        <source>Saved Last.fm scrobbling preferences for {username}.</source>
        <translation>Spremljene su postavke Last.fm skroblanja za {username}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="581" />
        <source>no user</source>
        <translation>nema korisnika</translation>
    </message>
    <message>
        <location filename="../controller.py" line="592" />
        <source>Enter a Last.fm username before fetching tracks.</source>
        <translation>Unesite korisničko ime za Last.fm prije dohvaćanja pjesama.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="602" />
        <source>Background work is already running for {username}.</source>
        <translation>Pozadinski rad za {username} već je pokrenut.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="614" />
        <source>Loaded cached tracks</source>
        <translation>Učitane predmemorirane pjesme</translation>
    </message>
    <message>
        <location filename="../controller.py" line="631" />
        <source>Could not reach Last.fm for {username}: {error}</source>
        <translation>Last.fm za {username} nije dostupan: {error}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="645" />
        <source>Starting fresh Last.fm fetch for {username}; {count} tracks expected.</source>
        <translation>Pokreće se novo dohvaćanje s Last.fm-a za {username}; očekuje se {count} pjesama.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="654" />
        <source>Starting fresh Last.fm fetch for {username}.</source>
        <translation>Pokreće se novo dohvaćanje s Last.fm-a za {username}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="663" />
        <source>Starting fetch</source>
        <translation>Pokreće se dohvaćanje</translation>
    </message>
    <message>
        <location filename="../controller.py" line="679" />
        <source>Fetch resumed.</source>
        <translation>Dohvaćanje je nastavljeno.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="685" />
        <source>Fetch paused.</source>
        <translation>Dohvaćanje je pauzirano.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="695" />
        <source>Stopping fetch.</source>
        <translation>Zaustavljanje dohvaćanja.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="709" />
        <source>Enter a Last.fm username before resolving tracks.</source>
        <translation>Unesite korisničko ime za Last.fm prije pronalaženja pjesama.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="718" />
        <source>Starting YouTube lookup for {username}; priority={priority}, limit={limit}.</source>
        <translation>Pokreće se pretraga YouTube izvora za {username}; prioritet={priority}, ograničenje={limit}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="780" />
        <location filename="../controller.py" line="724" />
        <source>none</source>
        <translation>nema</translation>
    </message>
    <message>
        <location filename="../controller.py" line="784" />
        <location filename="../controller.py" line="728" />
        <source>all</source>
        <translation>sve</translation>
    </message>
    <message>
        <location filename="../controller.py" line="734" />
        <source>Starting YouTube lookup</source>
        <translation>Pokretanje pretrage YouTube izvora</translation>
    </message>
    <message>
        <location filename="../controller.py" line="759" />
        <source>Enter a Last.fm username before downloading tracks.</source>
        <translation>Unesite korisničko ime za Last.fm prije preuzimanja pjesama.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="773" />
        <source>Starting downloads for {username}; concurrency={concurrency}, priority={priority}, limit={limit}.</source>
        <translation>Pokreće se preuzimanje za {username}; paralelno={concurrency}, prioritet={priority}, ograničenje={limit}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="789" />
        <source>Starting downloads</source>
        <translation>Pokretanje preuzimanja</translation>
    </message>
    <message>
        <location filename="../controller.py" line="811" />
        <source>Select a downloaded track before playing.</source>
        <translation>Odaberite preuzetu pjesmu prije reprodukcije.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="829" />
        <source>Playback resumed.</source>
        <translation>Reprodukcija je nastavljena.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="838" />
        <source>Playback paused.</source>
        <translation>Reprodukcija je pauzirana.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="882" />
        <location filename="../controller.py" line="847" />
        <source>No track is currently playing.</source>
        <translation>Trenutno se ne reproducira nijedna pjesma.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="858" />
        <source>Playback stopped.</source>
        <translation>Reprodukcija je zaustavljena.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="903" />
        <source>Seeked playback to {seconds} seconds.</source>
        <translation>Reprodukcija je premotana na {seconds} sekundi.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1029" />
        <source>Fetch for {username} returned invalid track data.</source>
        <translation>Dohvaćanje za {username} vratilo je nevažeće podatke o pjesmi.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1039" />
        <source>Fetched and stored {count} tracks for {username}.</source>
        <translation>Dohvaćeno je i pohranjeno {count} pjesama za {username}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1063" />
        <source>Stopped fetch for {username} returned invalid data.</source>
        <translation>Zaustavljeno dohvaćanje za {username} vratilo je nevažeće podatke.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1073" />
        <source>Stopped fetch for {username} after {count} tracks.</source>
        <translation>Dohvaćanje za {username} zaustavljeno je nakon {count} pjesama.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1086" />
        <source>Fetch for {username} returned invalid partial data.</source>
        <translation>Dohvaćanje za {username} vratilo je nevažeće djelomične podatke.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1098" />
        <source>Fetch progress for {username}: {count} tracks are visible now.</source>
        <translation>Napredak dohvaćanja za {username}: sada je vidljivo {count} pjesama.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1106" />
        <source>Fetched {count} tracks for {username}</source>
        <translation>Dohvaćeno {count} pjesama za {username}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1121" />
        <source>Workflow for {username} returned an invalid track update.</source>
        <translation>Tijek rada za {username} vratio je nevažeće ažuriranje pjesme.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1131" />
        <source>Track update from {username}: {artist} - {title} is now {status}.</source>
        <translation>Ažuriranje pjesme za {username}: {artist} - {title} sada ima status {status}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1148" />
        <source>Lookup for {username} returned invalid track data.</source>
        <translation>Pretraživanje za {username} vratilo je nevažeće podatke o pjesmi.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1231" />
        <location filename="../controller.py" line="1165" />
        <source>YouTube work stopped; completed items remain saved.</source>
        <translation>Rad s YouTubeom zaustavljen je; dovršene stavke ostaju spremljene.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1172" />
        <source>Resolved YouTube URLs for {resolved_count}/{count} tracks; {not_found_count} were not found.</source>
        <translation>Pronađeni su YouTube URL-ovi za {resolved_count}/{count} pjesama; {not_found_count} nije pronađeno.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1198" />
        <source>No queued tracks are ready for download.</source>
        <translation>Nijedna pjesma u redu čekanja nije spremna za preuzimanje.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1210" />
        <source>Download for {username} returned invalid track data.</source>
        <translation>Preuzimanje za {username} vratilo je nevažeće podatke o pjesmi.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1238" />
        <source>Download run for {username} finished: {downloaded_count}/{count} tracks downloaded, {failed_count} failed.</source>
        <translation>Preuzimanje za {username} je završeno: preuzeto je {downloaded_count}/{count} pjesama, {failed_count} nije uspjelo.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1265" />
        <source>Failed</source>
        <translation>Neuspješno</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1312" />
        <source>Updating Last.fm now-playing for {artist} - {title}.</source>
        <translation>Ažurira se status "sada svira" na Last.fm-u za {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1321" />
        <source>Playing {artist} - {title}.</source>
        <translation>Reproducira se {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1345" />
        <source>Last.fm returned invalid artist image data.</source>
        <translation>Last.fm je vratio nevažeće podatke o slici izvođača.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1379" />
        <source>Enter a Last.fm username before preparing playback.</source>
        <translation>Unesite korisničko ime za Last.fm prije pripreme reprodukcije.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1389" />
        <source>Preparing {artist} - {title} for playback.</source>
        <translation>Priprema {artist} - {title} za reprodukciju.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1406" />
        <source>Starting automatic YouTube lookup for {count} fetched tracks.</source>
        <translation>Pokreće se automatska pretraga YouTube izvora za {count} dohvaćenih pjesama.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1447" />
        <source>Stopping YouTube checks and downloads; completed items remain saved.</source>
        <translation>Zaustavljaju se YouTube provjere i preuzimanja; dovršene stavke ostaju spremljene.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1463" />
        <source>Resuming YouTube work.</source>
        <translation>Nastavlja se rad s YouTubeom.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1471" />
        <source>No YouTube work remains to resume.</source>
        <translation>Nema preostalog rada s YouTubeom za nastavak.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1483" />
        <source>Enter a Last.fm username before retrying a download.</source>
        <translation>Unesite korisničko ime za Last.fm prije ponovnog pokušaja preuzimanja.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1512" />
        <source>Retrying download for {artist} - {title}.</source>
        <translation>Ponovni pokušaj preuzimanja za {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1525" />
        <source>Starting automatic download queue for resolved tracks.</source>
        <translation>Pokreće se automatski red preuzimanja za pronađene pjesme.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1540" />
        <source>Starting priority download for selected track.</source>
        <translation>Pokreće se prioritetno preuzimanje odabrane pjesme.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1635" />
        <source>Submitting Last.fm scrobble for {artist} - {title}.</source>
        <translation>Šalje se zapis skroblanja na Last.fm za {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1665" />
        <source>Finished playback for {artist} - {title}.</source>
        <translation>Završena je reprodukcija za {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1678" />
        <source>Playback finished.</source>
        <translation>Reprodukcija je završena.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1689" />
        <source>Continuing with random track: {artist} - {title}.</source>
        <translation>Nastavlja se s nasumičnom pjesmom: {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1700" />
        <source>Continuing with next track: {artist} - {title}.</source>
        <translation>Nastavlja se sa sljedećom pjesmom: {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1720" />
        <source>All background work is finished; controls are enabled again.</source>
        <translation>Sav pozadinski rad je završen; kontrole su ponovno omogućene.</translation>
    </message>
    <message>
        <source>Downloads stopped by user.</source>
        <translation type="vanished">Korisnik je zaustavio preuzimanja.</translation>
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
        <location filename="../download.py" line="141" />
        <source>Queued {count} downloads</source>
        <translation>U redu čekanja je {count} preuzimanja</translation>
    </message>
    <message>
        <location filename="../download.py" line="198" />
        <source>Downloaded {done}/{total} tracks</source>
        <translation>Preuzeto {done}/{total} pjesama</translation>
    </message>
</context><context>
    <name>FetchLovedTracksWorker</name>
    <message>
        <location filename="../workers.py" line="81" />
        <source>Looking up Last.fm user {username}</source>
        <translation>Traži se Last.fm korisnik {username}</translation>
    </message>
    <message>
        <location filename="../workers.py" line="97" />
        <source>Stopped fetch after {count} tracks</source>
        <translation>Dohvaćanje je zaustavljeno nakon {count} pjesama</translation>
    </message>
    <message>
        <location filename="../workers.py" line="107" />
        <source>Fetched {count} tracks</source>
        <translation>Dohvaćeno {count} pjesama</translation>
    </message>
</context><context>
    <name>LastFmLovedTracksScraper</name>
    <message>
        <location filename="../lastfm.py" line="392" />
        <source>Found Last.fm user {username}</source>
        <translation>Pronađen je Last.fm korisnik {username}</translation>
    </message>
    <message>
        <location filename="../lastfm.py" line="695" />
        <source>Fetched {count} tracks</source>
        <translation>Dohvaćeno {count} pjesama</translation>
    </message>
    <message>
        <location filename="../lastfm.py" line="700" />
        <source>Fetched {done}/{total} tracks</source>
        <translation>Dohvaćeno {done}/{total} pjesama</translation>
    </message>
</context><context>
    <name>LookupTracksWorker</name>
    <message>
        <location filename="../workers.py" line="193" />
        <source>Resolving YouTube URLs for {username}</source>
        <translation>Pronalaženje YouTube URL-ova za {username}</translation>
    </message>
    <message>
        <location filename="../workers.py" line="212" />
        <source>YouTube lookup stopped</source>
        <translation>Pretraživanje YouTubea zaustavljeno</translation>
    </message>
    <message>
        <location filename="../workers.py" line="217" />
        <source>Resolved {count} tracks</source>
        <translation>Pronađeno {count} pjesama</translation>
    </message>
</context><context>
    <name>MainWindow</name>
    <message>
        <location filename="../ui/main_window.py" line="1147" />
        <location filename="../ui/main_window.py" line="204" />
        <source>Ready</source>
        <translation>Spremno</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="414" />
        <source>Retry Download</source>
        <translation>Ponovi preuzimanje</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1140" />
        <location filename="../ui/main_window.py" line="523" />
        <source>Idle</source>
        <translation>Mirovanje</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="546" />
        <source>Loaded {count} tracks</source>
        <translation>Učitano {count} pjesama</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="550" />
        <source>Playlist: {count} titles</source>
        <translation>Popis za reprodukciju: {count} naslova</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="577" />
        <source>Resume</source>
        <translation>Nastavi</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1119" />
        <location filename="../ui/main_window.py" line="577" />
        <source>Pause</source>
        <translation>Pauziraj</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1120" />
        <location filename="../ui/main_window.py" line="578" />
        <source>Stop</source>
        <translation>Zaustavi</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="580" />
        <source>Resume the paused Last.fm fetch</source>
        <translation>Nastavi pauzirano dohvaćanje s Last.fm-a</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="582" />
        <source>Pause the active Last.fm fetch</source>
        <translation>Pauziraj aktivno dohvaćanje s Last.fm-a</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="583" />
        <source>Stop the active Last.fm fetch</source>
        <translation>Zaustavi aktivno dohvaćanje s Last.fm-a</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="608" />
        <source>Stopping YouTube…</source>
        <translation>Zaustavljanje YouTubea…</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="610" />
        <source>Resume YouTube</source>
        <translation>Nastavi YouTube</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="612" />
        <source>Stop YouTube</source>
        <translation>Zaustavi YouTube</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="615" />
        <source>Stop or resume YouTube checks and downloads</source>
        <translation>Zaustavi ili nastavi YouTube provjere i preuzimanja</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="619" />
        <source>Fetch</source>
        <translation>Dohvati</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="621" />
        <source>Fetch loved tracks, then automatically check and download them from YouTube</source>
        <translation>Dohvati omiljene pjesme, zatim ih automatski provjeri i preuzmi s YouTubea</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="782" />
        <source>Updated {artist} - {title}: {status}</source>
        <translation>Ažurirano {artist} - {title}: {status}</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1117" />
        <location filename="../ui/main_window.py" line="799" />
        <source>Not playing</source>
        <translation>Ne reproducira se</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="818" />
        <source>Artist</source>
        <translation>Izvođač</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1094" />
        <location filename="../ui/main_window.py" line="886" />
        <source>About myLastFmPlayer</source>
        <translation>O myLastFmPlayeru</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="892" />
        <source>myLastFmPlayer {version}</source>
        <translation>myLastFmPlayer {version}</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="893" />
        <source>Author: Marcel Petrick &lt;a href="mailto:mail@marcelpetrick.it"&gt;mail@marcelpetrick.it&lt;/a&gt;</source>
        <translation>Autor: Marcel Petrick &lt;a href="mailto:mail@marcelpetrick.it"&gt;mail@marcelpetrick.it&lt;/a&gt;</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="897" />
        <source>License: GNU GPLv3 or later.</source>
        <translation>Licenca: GNU GPLv3 ili novija.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="898" />
        <source>This application fetches a user's public loved tracks from Last.fm, keeps local metadata, resolves playable sources through yt-dlp, downloads MP3 files, and plays them locally.</source>
        <translation>Ova aplikacija dohvaća korisnikove javne omiljene pjesme s Last.fm-a, čuva lokalne metapodatke, pronalazi izvore za reprodukciju putem yt-dlp-a, preuzima MP3 datoteke i reproducira ih lokalno.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="903" />
        <source>It is intended as a practical Linux desktop helper for rebuilding a personal loved-track collection without manually searching every song.</source>
        <translation>Namijenjena je kao praktičan Linux desktop alat za obnovu osobne zbirke omiljenih pjesama bez ručnog traženja svake pjesme.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="907" />
        <source>Optional Last.fm scrobbling can connect the local playback workflow back to the user's Last.fm account.</source>
        <translation>Neobavezno Last.fm skroblanje može povezati lokalni tijek reprodukcije s korisnikovim Last.fm računom.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1095" />
        <location filename="../ui/main_window.py" line="917" />
        <source>Open Source Licenses</source>
        <translation>Licence otvorenog koda</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="923" />
        <source>myLastFmPlayer is GPLv3-or-later software and uses these open-source libraries and external tools:</source>
        <translation>myLastFmPlayer je softver pod licencom GPLv3 ili novijom i koristi ove biblioteke otvorenog koda i vanjske alate:</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="987" />
        <location filename="../ui/main_window.py" line="929" />
        <source>Python Software Foundation License; runtime for the application.</source>
        <translation>Python Software Foundation License; izvršno okruženje aplikacije.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="989" />
        <location filename="../ui/main_window.py" line="933" />
        <source>GNU GPL v3; Python bindings for the Qt desktop interface.</source>
        <translation>GNU GPL v3; Python vezanja za Qt sučelje radne površine.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="990" />
        <location filename="../ui/main_window.py" line="937" />
        <source>GNU LGPL v3 / GPL v3; cross-platform UI toolkit.</source>
        <translation>GNU LGPL v3 / GPL v3; višeplatformski alatni skup za korisničko sučelje.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="992" />
        <location filename="../ui/main_window.py" line="941" />
        <source>Apache License 2.0; HTTP client for Last.fm API calls.</source>
        <translation>Apache License 2.0; HTTP klijent za Last.fm API pozive.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="993" />
        <location filename="../ui/main_window.py" line="945" />
        <source>Apache License 2.0; Last.fm scrobbling integration.</source>
        <translation>Apache License 2.0; integracija Last.fm skroblanja.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="994" />
        <location filename="../ui/main_window.py" line="949" />
        <source>Unlicense; media lookup and download helper.</source>
        <translation>Unlicense; pomoćni alat za pretraživanje i preuzimanje medija.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="996" />
        <location filename="../ui/main_window.py" line="953" />
        <source>LGPL/GPL family licenses depending on the installed build; audio conversion backend.</source>
        <translation>Obitelj licenci LGPL/GPL, ovisno o instaliranoj verziji; pozadinski alat za pretvorbu zvuka.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="958" />
        <source>Development tools include {tools} under their respective open-source licenses.</source>
        <translation>Razvojni alati uključuju {tools} pod njihovim odgovarajućim licencama otvorenog koda.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="974" />
        <source>This summary is informational; the complete license texts are provided by the installed projects and system packages.</source>
        <translation>Ovaj sažetak je informativan; potpune tekstove licenci pružaju instalirani projekti i sistemski paketi.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1091" />
        <source>Fetch loved tracks</source>
        <translation>Dohvati omiljene pjesme</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1092" />
        <source>Preferences</source>
        <translation>Postavke</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1093" />
        <source>Open data folder in file manager</source>
        <translation>Otvori mapu podataka u upravitelju datoteka</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1096" />
        <source>Quit</source>
        <translation>Izlaz</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1097" />
        <source>Main</source>
        <translation>Glavno</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1098" />
        <source>Theme</source>
        <translation>Tema</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1099" />
        <source>Light</source>
        <translation>Svijetla</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1100" />
        <source>Dark</source>
        <translation>Tamna</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1101" />
        <source>Lilac</source>
        <translation>Lila</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1102" />
        <source>Mint</source>
        <translation>Menta</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1103" />
        <source>Language</source>
        <translation>Jezik</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1104" />
        <source>Help</source>
        <translation>Pomoć</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1105" />
        <source>Last.fm username</source>
        <translation>Korisničko ime za Last.fm</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1106" />
        <source>Enter username</source>
        <translation>Unesite korisničko ime</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1109" />
        <source>Filter</source>
        <translation>Filtar</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1110" />
        <source>Artist or track title</source>
        <translation>Izvođač ili naslov pjesme</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1111" />
        <source>Reset</source>
        <translation>Poništi</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1113" />
        <source>Enter your Last.fm username and press Fetch to load your loved tracks.</source>
        <translation>Unesite svoje korisničko ime za Last.fm i pritisnite «Dohvati» za učitavanje omiljenih pjesama.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1115" />
        <source>Playback</source>
        <translation>Reprodukcija</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1118" />
        <source>Play</source>
        <translation>Reproduciraj</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1121" />
        <source>Next</source>
        <translation>Sljedeća</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1123" />
        <location filename="../ui/main_window.py" line="1122" />
        <source>Volume</source>
        <translation>Glasnoća</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1124" />
        <source>Mute</source>
        <translation>Bez zvuka</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1125" />
        <source>Randomize</source>
        <translation>Nasumični redoslijed</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1127" />
        <source>Open artist page on Last.fm</source>
        <translation>Otvori stranicu izvođača na Last.fm-u u privatnom prozoru</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1128" />
        <source>Playback position</source>
        <translation>Položaj reprodukcije</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1129" />
        <source>Clear log</source>
        <translation>Obriši dnevnik</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1130" />
        <source>Clear status updates and errors</source>
        <translation>Obriši ažuriranja statusa i pogreške</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1132" />
        <source>Status updates and errors will appear here.</source>
        <translation>Ovdje će se pojaviti ažuriranja statusa i pogreške.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1137" />
        <source>Dependencies: yt-dlp, ffmpeg, and ffprobe not checked yet</source>
        <translation>Ovisnosti: yt-dlp, ffmpeg i ffprobe još nisu provjereni</translation>
    </message>
    <message>
        <source>Stop Downloads</source>
        <translation type="vanished">Zaustavi preuzimanja</translation>
    </message>
    <message>
        <source>Start Downloads</source>
        <translation type="vanished">Pokreni preuzimanja</translation>
    </message>
    <message>
        <source>Downloads</source>
        <translation type="vanished">Preuzimanja</translation>
    </message>
    <message>
        <source>MIT License; legacy Last.fm HTML parser support.</source>
        <translation type="vanished">MIT License; podrška za naslijeđeni Last.fm HTML parser.</translation>
    </message>
    <message>
        <source>Author: Marcel Petrick &lt;mail@marcelpetrick.it&gt;</source>
        <translation type="vanished">Autor: Marcel Petrick &lt;mail@marcelpetrick.it&gt;</translation>
    </message>
    <message>
        <source>Python - Python Software Foundation License; runtime for the application.</source>
        <translation type="vanished">Python - Python Software Foundation License; izvršno okruženje aplikacije.</translation>
    </message>
    <message>
        <source>PyQt6 - GNU GPL v3; Python bindings for the Qt desktop interface.</source>
        <translation type="vanished">PyQt6 - GNU GPL v3; Python povezivanja za Qt desktop sučelje.</translation>
    </message>
    <message>
        <source>Qt 6 - GNU LGPL v3 / GPL v3; cross-platform UI toolkit.</source>
        <translation type="vanished">Qt 6 - GNU LGPL v3 / GPL v3; višeplatformski UI alatni skup.</translation>
    </message>
    <message>
        <source>requests - Apache License 2.0; HTTP client for Last.fm API calls.</source>
        <translation type="vanished">requests - Apache License 2.0; HTTP klijent za Last.fm API pozive.</translation>
    </message>
    <message>
        <source>beautifulsoup4 - MIT License; legacy Last.fm HTML parser support.</source>
        <translation type="vanished">beautifulsoup4 - MIT License; podrška za naslijeđeni Last.fm HTML parser.</translation>
    </message>
    <message>
        <source>pylast - Apache License 2.0; Last.fm scrobbling integration.</source>
        <translation type="vanished">pylast - Apache License 2.0; integracija Last.fm skroblanja.</translation>
    </message>
    <message>
        <source>yt-dlp - Unlicense; media lookup and download helper.</source>
        <translation type="vanished">yt-dlp - Unlicense; pomoćni alat za pretragu i preuzimanje medija.</translation>
    </message>
    <message>
        <source>FFmpeg - LGPL/GPL family licenses depending on the installed build; audio conversion backend.</source>
        <translation type="vanished">FFmpeg - LGPL/GPL obitelj licenci ovisno o instaliranoj verziji; pozadinski alat za pretvorbu zvuka.</translation>
    </message>
    <message>
        <source>Development tools include pytest, pytest-cov, coverage.py, Ruff, Pylint, Sphinx, and build under their respective open-source licenses.</source>
        <translation type="vanished">Razvojni alati uključuju pytest, pytest-cov, coverage.py, Ruff, Pylint, Sphinx i build pod njihovim odgovarajućim licencama otvorenog koda.</translation>
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
        <location filename="../ui/preferences_dialog.py" line="179" />
        <location filename="../ui/preferences_dialog.py" line="138" />
        <source>None (disabled)</source>
        <translation>Nijedan (onemogućeno)</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="158" />
        <source>Preferences</source>
        <translation>Postavke</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="159" />
        <source>Last.fm Authentication</source>
        <translation>Autentifikacija na Last.fm-u</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="160" />
        <source>Authenticate with Last.fm</source>
        <translation>Autentificiraj se putem Last.fm-a</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="161" />
        <source>I've authorized</source>
        <translation>Autorizirao sam</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="162" />
        <source>Disconnect</source>
        <translation>Prekini vezu</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="163" />
        <source>Scrobbling</source>
        <translation>Skroblanje</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="164" />
        <source>Enable scrobbling</source>
        <translation>Omogući skroblanje</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="166" />
        <source>Submits to Last.fm after 33% of each track has been played.</source>
        <translation>Šalje na Last.fm nakon što se reproducira 33% svake pjesme.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="168" />
        <source>YouTube Downloads</source>
        <translation>YouTube preuzimanja</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="169" />
        <source>Browser cookies:</source>
        <translation>Kolačići preglednika:</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="170" />
        <source>Parallel YouTube checks and downloads:</source>
        <translation>Paralelne YouTube provjere i preuzimanja:</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="172" />
        <source>Select the browser whose YouTube login cookies yt-dlp should use. Required for age-restricted videos. You must be signed into YouTube in the selected browser. The parallel-work limit applies to new YouTube checks and downloads.</source>
        <translation>Odaberite preglednik čije kolačiće za prijavu na YouTube treba koristiti yt-dlp. To je potrebno za videozapise s dobnim ograničenjem. Morate biti prijavljeni na YouTube u odabranom pregledniku. Ograničenje paralelnog rada primjenjuje se na nove YouTube provjere i preuzimanja.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="180" />
        <source>Privacy</source>
        <translation>Privatnost</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="182" />
        <source>Keep saved library and Last.fm session after quitting</source>
        <translation>Zadrži spremljenu zbirku i Last.fm sesiju nakon zatvaranja</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="185" />
        <source>When disabled, closing the app deletes saved track lists, lookup and download caches, and Last.fm authentication. Downloaded audio files remain.</source>
        <translation>Kada je isključeno, zatvaranjem aplikacije brišu se spremljeni popisi pjesama, predmemorije pretraživanja i preuzimanja te Last.fm autentifikacija. Preuzete zvučne datoteke ostaju.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="195" />
        <source>⚠ API credentials not configured.
Set LASTFM_API_KEY and LASTFM_API_SECRET environment variables.</source>
        <translation>⚠ API vjerodajnice nisu konfigurirane.
Postavite varijable okoline LASTFM_API_KEY i LASTFM_API_SECRET.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="214" />
        <source>🟢 Connected as {username}</source>
        <translation>🟢 Povezano kao {username}</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="223" />
        <source>🔵 Browser opened — authorize the app, then click «I've authorized».</source>
        <translation>🔵 Preglednik je otvoren — autorizirajte aplikaciju, zatim kliknite «Autorizirao sam».</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="229" />
        <source>🔴 Not connected</source>
        <translation>🔴 Nije povezano</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="252" />
        <source>⚠ Could not start authentication. Check API credentials.</source>
        <translation>⚠ Nije moguće pokrenuti provjeru autentičnosti. Provjerite API vjerodajnice.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="263" />
        <source>⚠ Authorization not confirmed yet. Authorize in the browser, then try again.</source>
        <translation>⚠ Autorizacija još nije potvrđena. Autorizirajte se u pregledniku, a zatim pokušajte ponovno.</translation>
    </message>
    <message>
        <source>Keep cached data after quitting</source>
        <translation type="vanished">Zadrži predmemorirane podatke nakon izlaska</translation>
    </message>
    <message>
        <source>Parallel downloads:</source>
        <translation type="vanished">Paralelna preuzimanja:</translation>
    </message>
    <message>
        <source>Select the browser whose YouTube login cookies yt-dlp should use. Required for age-restricted videos. You must be signed into YouTube in the selected browser. Parallel download changes apply to new work.</source>
        <translation type="vanished">Odaberite preglednik čije YouTube kolačiće za prijavu yt-dlp treba koristiti. Potrebno za videozapise s dobnim ograničenjem. Morate biti prijavljeni na YouTube u odabranom pregledniku. Promjene paralelnih preuzimanja primjenjuju se na nove zadatke.</translation>
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
        <translation>Izvođač</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="96" />
        <source>Title</source>
        <translation>Naslov</translation>
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
        <translation>Datoteka</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="193" />
        <source>Fetched</source>
        <translation>Dohvaćeno</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="195" />
        <source>Queued</source>
        <translation>U redu čekanja</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="197" />
        <source>Searching</source>
        <translation>Traženje</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="199" />
        <source>Lookup failed</source>
        <translation>Pretraživanje nije uspjelo</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="201" />
        <source>Downloading</source>
        <translation>Preuzimanje</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="203" />
        <source>Downloaded</source>
        <translation>Preuzeto</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="205" />
        <source>Failed</source>
        <translation>Neuspješno</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="207" />
        <source>Not found</source>
        <translation>Nije pronađeno</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="222" />
        <source>{bitrate} kbps</source>
        <translation>{bitrate} kbps</translation>
    </message>
</context><context>
    <name>YouTubeResolver</name>
    <message>
        <location filename="../youtube.py" line="156" />
        <source>Searching {done}/{total}: {artist} - {title}</source>
        <translation>Pretraživanje {done}/{total}: {artist} - {title}</translation>
    </message>
    <message>
        <location filename="../youtube.py" line="377" />
        <source>Resolved {done}/{total}: {artist} - {title}</source>
        <translation>Pronađeno {done}/{total}: {artist} - {title}</translation>
    </message>
    <message>
        <location filename="../youtube.py" line="385" />
        <source>No YouTube result {done}/{total}: {artist} - {title}</source>
        <translation>Nema YouTube rezultata {done}/{total}: {artist} - {title}</translation>
    </message>
</context></TS>

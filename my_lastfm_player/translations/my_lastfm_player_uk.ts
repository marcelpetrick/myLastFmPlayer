<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>ApplicationController</name>
    <message>
        <location filename="../controller.py" line="149" />
        <source>No cached tracks found for {username}; fetching from Last.fm.</source>
        <translation>Не знайдено кешованих треків для {username}; отримання з Last.fm.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="160" />
        <source>Found {count} cached tracks for {username}; checking Last.fm before using them.</source>
        <translation>Знайдено {count} кешованих треків для {username}; перевірка Last.fm перед їх використанням.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="180" />
        <source>Loaded {count} cached tracks for {username}; skipped Last.fm fetch.</source>
        <translation>Завантажено {count} кешованих треків для {username}; пропущено отримання Last.fm.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="194" />
        <source>Could not verify Last.fm loved-track count for {username}; using {count} cached tracks: {error}</source>
        <translation>Не вдалося перевірити кількість улюблених треків Last.fm для {username}; використання {count} кешованих треків: {error}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="207" />
        <source>Could not read Last.fm loved-track count for {username}; fetching fresh data instead of trusting {count} cached tracks.</source>
        <translation>Не вдалося прочитати кількість улюблених треків Last.fm для {username}; отримання свіжих даних замість довіри {count} кешованих треків.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="219" />
        <source>Last.fm reports {online_count} loved tracks for {username}; cached track count matches.</source>
        <translation>Last.fm повідомляє {online_count} улюблених треків для {username}; збіги кешованої кількості треків.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="230" />
        <source>Last.fm reports {online_count} loved tracks for {username}, but the cache has {cached_count}; fetching fresh data.</source>
        <translation>Last.fm повідомляє {online_count} улюблених треків для {username}, але в кеші є {cached_count}; отримання свіжих даних.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="255" />
        <source>Dependency check finished: {message}</source>
        <translation>Перевірку залежностей завершено: {message}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="272" />
        <source>Could not open data folder: {error}</source>
        <translation>Не вдалося відкрити теку даних: {error}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="282" />
        <source>Opened data folder: {path}</source>
        <translation>Відкрито теку даних: {path}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="291" />
        <source>Could not open data folder: {path}</source>
        <translation>Не вдалося відкрити теку даних: {path}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="302" />
        <source>Last.fm scrobbling is disabled because {api_key_env}/{api_secret_env} are not configured and no bundled credentials are available.</source>
        <translation>Прокручування Last.fm вимкнено, оскільки {api_key_env}/{api_secret_env} не налаштовано та недоступні пакетні облікові дані.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="317" />
        <source>Loaded Last.fm scrobbling settings; stored session key is {state}.</source>
        <translation>Завантажено налаштування прокручування Last.fm; збережений ключ сеансу – {state}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="321" />
        <source>present</source>
        <translation>присутній</translation>
    </message>
    <message>
        <location filename="../controller.py" line="323" />
        <source>missing</source>
        <translation>відсутній</translation>
    </message>
    <message>
        <location filename="../controller.py" line="337" />
        <source>Connected Last.fm scrobbling as {username}.</source>
        <translation>Підключено Last.fm, гортаючи як {username}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="345" />
        <source>Stored Last.fm session key could not be verified; scrobbling remains disconnected.</source>
        <translation>Не вдалося перевірити збережений ключ сеансу Last.fm; скроблінг залишається відключеним.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="355" />
        <source>Opening preferences.</source>
        <translation>Відкриття налаштувань.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="369" />
        <source>Preferences closed; no Last.fm scrobbling service is active.</source>
        <translation>Налаштування закрито; жодна служба скроблінгу Last.fm не активна.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="378" />
        <source>Saved Last.fm scrobbling preferences for {username}.</source>
        <translation>Збережено параметри гортання Last.fm для {username}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="382" />
        <source>no user</source>
        <translation>немає користувача</translation>
    </message>
    <message>
        <location filename="../controller.py" line="393" />
        <source>Enter a Last.fm username before fetching tracks.</source>
        <translation>Введіть ім’я користувача Last.fm, перш ніж завантажувати треки.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="404" />
        <source>Loaded cached tracks</source>
        <translation>Завантажено кешовані треки</translation>
    </message>
    <message>
        <location filename="../controller.py" line="414" />
        <source>Starting fresh Last.fm fetch for {username}.</source>
        <translation>Початок свіжого отримання Last.fm для {username}.</translation>
    </message>
    <message>
        <source>Could not reach Last.fm for {username}: {error}</source>
        <translation>Last.fm для {username} недоступний: {error}</translation>
    </message>
    <message>
        <source>Starting fresh Last.fm fetch for {username}; {count} tracks expected.</source>
        <translation>Початок свіжого отримання Last.fm для {username}; очікується {count} треків.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="423" />
        <source>Starting fetch</source>
        <translation>Початок отримання</translation>
    </message>
    <message>
        <location filename="../controller.py" line="439" />
        <source>Fetch resumed.</source>
        <translation>Отримання відновлено.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="445" />
        <source>Fetch paused.</source>
        <translation>Отримання призупинено.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="455" />
        <source>Stopping fetch.</source>
        <translation>Зупинка отримання.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="469" />
        <source>Enter a Last.fm username before resolving tracks.</source>
        <translation>Введіть ім’я користувача Last.fm, перш ніж розпізнавати треки.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="479" />
        <source>Starting YouTube lookup for {username}; priority={priority}, limit={limit}.</source>
        <translation>Початок пошуку на YouTube для {username}; пріоритет={priority}, ліміт={limit}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="544" />
        <location filename="../controller.py" line="485" />
        <source>none</source>
        <translation>немає</translation>
    </message>
    <message>
        <location filename="../controller.py" line="548" />
        <location filename="../controller.py" line="489" />
        <source>all</source>
        <translation>все</translation>
    </message>
    <message>
        <location filename="../controller.py" line="495" />
        <source>Starting YouTube lookup</source>
        <translation>Початок пошуку на YouTube</translation>
    </message>
    <message>
        <location filename="../controller.py" line="518" />
        <source>Enter a Last.fm username before downloading tracks.</source>
        <translation>Перед завантаженням треків введіть ім’я користувача Last.fm.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="537" />
        <source>Starting downloads for {username}; concurrency={concurrency}, priority={priority}, limit={limit}.</source>
        <translation>Початок завантажень для {username}; concurrency={concurrency}, priority={priority}, limit={limit}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="553" />
        <source>Starting downloads</source>
        <translation>Початок завантажень</translation>
    </message>
    <message>
        <location filename="../controller.py" line="574" />
        <source>Select a downloaded track before playing.</source>
        <translation>Виберіть завантажений трек перед відтворенням.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="590" />
        <source>Playback resumed.</source>
        <translation>Playback resumed.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="599" />
        <source>Playback paused.</source>
        <translation>Відтворення призупинено.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="608" />
        <source>No track is currently playing.</source>
        <translation>Жоден трек зараз не відтворюється.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="618" />
        <source>Playback stopped.</source>
        <translation>Відтворення зупинено.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="635" />
        <source>Seeked playback to {seconds} seconds.</source>
        <translation>Шукав відтворення до {seconds} секунд.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="690" />
        <source>Fetch for {username} returned invalid track data.</source>
        <translation>Fetch для {username} повернув недійсні дані треку.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="700" />
        <source>Fetched and stored {count} tracks for {username}.</source>
        <translation>Отримано та збережено {count} треків для {username}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="727" />
        <source>Stopped fetch for {username} returned invalid data.</source>
        <translation>Зупинена вибірка для {username} повернула недійсні дані.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="737" />
        <source>Stopped fetch for {username} after {count} tracks.</source>
        <translation>Зупинено вибірку для {username} після {count} треків.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="748" />
        <source>Fetch for {username} returned invalid partial data.</source>
        <translation>Вибір для {username} повернув недійсні часткові дані.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="759" />
        <source>Fetch progress for {username}: {count} tracks are visible now.</source>
        <translation>Отримати прогрес для {username}: {count} доріжок видно зараз.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="767" />
        <source>Fetched {count} tracks for {username}</source>
        <translation>Отримано {count} треків для {username}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="786" />
        <source>Workflow for {username} returned an invalid track update.</source>
        <translation>Робочий процес для {username} повернув недійсне оновлення доріжки.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="796" />
        <source>Track update from {username}: {artist} - {title} is now {status}.</source>
        <translation>Оновлення композиції від {username}: {artist} – {title} тепер {status}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="811" />
        <source>Lookup for {username} returned invalid track data.</source>
        <translation>Пошук для {username} повернув недійсні дані треку.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="829" />
        <source>Resolved YouTube URLs for {resolved_count}/{count} tracks; {not_found_count} were not found.</source>
        <translation>Виправлені URL-адреси YouTube для {resolved_count}/{count} треків; {not_found_count} не знайдено.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="853" />
        <source>No queued tracks are ready for download.</source>
        <translation>Жодна композиція в черзі не готова для завантаження.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="864" />
        <source>Download for {username} returned invalid track data.</source>
        <translation>Завантаження для {username} повернуло недійсні дані доріжки.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="884" />
        <source>Download run for {username} finished: {downloaded_count}/{count} tracks downloaded, {failed_count} failed.</source>
        <translation>Завантаження для {username} завершено: {downloaded_count}/{count} треків завантажено, {failed_count} не вдалося.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="912" />
        <source>Failed</source>
        <translation>Не вдалося</translation>
    </message>
    <message>
        <location filename="../controller.py" line="949" />
        <source>Updating Last.fm now-playing for {artist} - {title}.</source>
        <translation>Оновлення Last.fm зараз грає для {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="958" />
        <source>Playing {artist} - {title}.</source>
        <translation>Грає {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="977" />
        <source>Enter a Last.fm username before preparing playback.</source>
        <translation>Перед підготовкою відтворення введіть ім’я користувача Last.fm.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="986" />
        <source>Preparing {artist} - {title} for playback.</source>
        <translation>Підготовка {artist} - {title} до відтворення.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1003" />
        <source>Starting automatic YouTube lookup for {count} fetched tracks.</source>
        <translation>Початок автоматичного пошуку {count} отриманих композицій на YouTube.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1019" />
        <source>Downloads stopped by user.</source>
        <translation>Завантаження зупинено користувачем.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1028" />
        <source>Enter a Last.fm username before retrying a download.</source>
        <translation>Введіть ім’я користувача Last.fm перед повторною спробою завантаження.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1046" />
        <source>Retrying download for {artist} - {title}.</source>
        <translation>Повторна спроба завантаження для {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1059" />
        <source>Starting automatic download queue for resolved tracks.</source>
        <translation>Запуск черги автоматичного завантаження для вирішених треків.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1067" />
        <source>Starting priority download for selected track.</source>
        <translation>Початок пріоритетного завантаження вибраного треку.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1141" />
        <source>Submitting Last.fm scrobble for {artist} - {title}.</source>
        <translation>Надсилання Scrobble Last.fm для {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1170" />
        <source>Finished playback for {artist} - {title}.</source>
        <translation>Завершено відтворення для {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1180" />
        <source>Playback finished.</source>
        <translation>Відтворення завершено.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1187" />
        <source>Continuing with next track: {artist} - {title}.</source>
        <translation>Продовжуємо наступний трек: {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1202" />
        <source>All background work is finished; controls are enabled again.</source>
        <translation>Вся фонова робота завершена; елементи керування знову ввімкнено.</translation>
    </message>
    <message>
        <source>Could not open file cache: {error}</source>
        <translation type="vanished">Could not open file cache: {error}</translation>
    </message>
    <message>
        <source>Opened file cache: {path}</source>
        <translation type="vanished">Opened file cache: {path}</translation>
    </message>
    <message>
        <source>Could not open file cache: {path}</source>
        <translation type="vanished">Could not open file cache: {path}</translation>
    </message>
    <message>
        <source>Resolved YouTube URLs for {count} tracks.</source>
        <translation type="vanished">Вирішено URL-адреси YouTube для {count} треків.</translation>
    </message>
    <message>
        <source>Downloaded {count} tracks for {username}.</source>
        <translation type="vanished">Завантажено {count} треків для {username}.</translation>
    </message>
</context><context>
    <name>DependencyCheckResult</name>
    <message>
        <location filename="../dependencies.py" line="30" />
        <source>Dependencies installed: {tools}</source>
        <translation>Установлено залежності: {tools}</translation>
    </message>
    <message>
        <location filename="../dependencies.py" line="35" />
        <source>Missing dependencies: {tools}</source>
        <translation>Відсутні залежності: {tools}</translation>
    </message>
</context><context>
    <name>DownloadManager</name>
    <message>
        <location filename="../download.py" line="124" />
        <source>Queued {count} downloads</source>
        <translation>У черзі {count} завантажень</translation>
    </message>
    <message>
        <location filename="../download.py" line="153" />
        <source>Downloaded {done}/{total} tracks</source>
        <translation>Завантажено композицій: {done}/{total}</translation>
    </message>
</context><context>
    <name>FetchLovedTracksWorker</name>
    <message>
        <location filename="../workers.py" line="54" />
        <source>Looking up Last.fm user {username}</source>
        <translation>Пошук користувача Last.fm {username}</translation>
    </message>
    <message>
        <location filename="../workers.py" line="70" />
        <source>Stopped fetch after {count} tracks</source>
        <translation>Зупинено вибірку після {count} треків</translation>
    </message>
    <message>
        <location filename="../workers.py" line="80" />
        <source>Fetched {count} tracks</source>
        <translation>Отримано {count} треків</translation>
    </message>
</context><context>
    <name>LastFmLovedTracksScraper</name>
    <message>
        <location filename="../lastfm.py" line="253" />
        <source>Found Last.fm user {username}</source>
        <translation>Знайдено користувача Last.fm {username}</translation>
    </message>
    <message>
        <location filename="../lastfm.py" line="455" />
        <source>Fetched {count} tracks</source>
        <translation>Отримано {count} треків</translation>
    </message>
    <message>
        <location filename="../lastfm.py" line="460" />
        <source>Fetched {done}/{total} tracks</source>
        <translation>Отримано {done}/{total} треків</translation>
    </message>
</context><context>
    <name>LookupTracksWorker</name>
    <message>
        <location filename="../workers.py" line="176" />
        <source>Resolving YouTube URLs for {username}</source>
        <translation>Розпізнавання URL-адрес YouTube для {username}</translation>
    </message>
    <message>
        <location filename="../workers.py" line="192" />
        <source>Resolved {count} tracks</source>
        <translation>Вирішено {count} треків</translation>
    </message>
</context><context>
    <name>MainWindow</name>
    <message>
        <location filename="../ui/main_window.py" line="643" />
        <location filename="../ui/main_window.py" line="77" />
        <source>Ready</source>
        <translation>Готовий</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="233" />
        <source>Retry Download</source>
        <translation>Повторити завантаження</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="636" />
        <location filename="../ui/main_window.py" line="308" />
        <source>Idle</source>
        <translation>Бездіяльність</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="332" />
        <source>Loaded {count} tracks</source>
        <translation>Завантажено {count} треків</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="343" />
        <source>Playlist: {count} titles</source>
        <translation>Список відтворення: {count} назв</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="364" />
        <source>Resume</source>
        <translation>Резюме</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="616" />
        <location filename="../ui/main_window.py" line="364" />
        <source>Pause</source>
        <translation>Пауза</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="617" />
        <location filename="../ui/main_window.py" line="365" />
        <source>Stop</source>
        <translation>СТІЙ</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="367" />
        <source>Resume the paused Last.fm fetch</source>
        <translation>Відновити призупинене отримання Last.fm</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="369" />
        <source>Pause the active Last.fm fetch</source>
        <translation>Призупинити активне отримання Last.fm</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="370" />
        <source>Stop the active Last.fm fetch</source>
        <translation>Зупиніть активне отримання Last.fm</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="621" />
        <location filename="../ui/main_window.py" line="380" />
        <source>Stop Downloads</source>
        <translation>Зупинити завантаження</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="621" />
        <location filename="../ui/main_window.py" line="384" />
        <source>Start Downloads</source>
        <translation>Почати завантаження</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="459" />
        <source>Updated {artist} - {title}: {status}</source>
        <translation>Оновлено {artist} - {title}: {status}</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="614" />
        <location filename="../ui/main_window.py" line="475" />
        <source>Not playing</source>
        <translation>Не відтворюється</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="598" />
        <source>Fetch loved tracks</source>
        <translation>Отримайте улюблені треки</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="599" />
        <source>Preferences</source>
        <translation>Уподобання</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="600" />
        <source>Open data folder in file manager</source>
        <translation>Відкрити теку даних у файловому менеджері</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="601" />
        <source>Quit</source>
        <translation>Вийти</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="602" />
        <source>Main</source>
        <translation>Головна</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="603" />
        <source>Theme</source>
        <translation>Theme</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="604" />
        <source>Light</source>
        <translation>Light</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="605" />
        <source>Dark</source>
        <translation>Dark</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="606" />
        <source>Lilac</source>
        <translation>Lilac</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="607" />
        <source>Mint</source>
        <translation>Mint</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="608" />
        <source>Language</source>
        <translation>Мова</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="609" />
        <source>Last.fm username</source>
        <translation>Ім'я користувача Last.fm</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="610" />
        <source>Enter username</source>
        <translation>Введіть ім'я користувача</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="611" />
        <source>Fetch</source>
        <translation>Принести</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="612" />
        <source>Playback</source>
        <translation>Відтворення</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="615" />
        <source>Play</source>
        <translation>грати</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="618" />
        <source>Playback position</source>
        <translation>Позиція відтворення</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="619" />
        <source>Downloads</source>
        <translation>Завантаження</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="623" />
        <source>Clear log</source>
        <translation>Очистити журнал</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="624" />
        <source>Clear status updates and errors</source>
        <translation>Очистити оновлення статусу та помилки</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="626" />
        <source>Status updates and errors will appear here.</source>
        <translation>Тут відображатимуться оновлення статусу та помилки.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="633" />
        <source>Dependencies: yt-dlp and ffmpeg not checked yet</source>
        <translation>Залежності: yt-dlp і ffmpeg ще не перевірено</translation>
    </message>
    <message>
        <source>Cached songs storage location</source>
        <translation type="vanished">Cached songs storage location</translation>
    </message>
    <message>
        <source>Download Queued</source>
        <translation type="vanished">Завантаження в черзі</translation>
    </message>
    <message>
        <source>Concurrency</source>
        <translation type="vanished">Паралелізм</translation>
    </message>
    <message>
        <source>This control is part of the MVP shell and will be wired in later steps.</source>
        <translation type="vanished">Цей елемент керування є частиною оболонки MVP і буде підключений на наступних етапах.</translation>
    </message>
</context><context>
    <name>PreferencesDialog</name>
    <message>
        <location filename="../ui/preferences_dialog.py" line="163" />
        <location filename="../ui/preferences_dialog.py" line="123" />
        <source>None (disabled)</source>
        <translation>Немає (вимкнено)</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="143" />
        <source>Preferences</source>
        <translation>Preferences</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="144" />
        <source>Last.fm Authentication</source>
        <translation>Last.fm Authentication</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="145" />
        <source>Authenticate with Last.fm</source>
        <translation>Authenticate with Last.fm</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="146" />
        <source>I've authorized</source>
        <translation>I've authorized</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="147" />
        <source>Disconnect</source>
        <translation>Disconnect</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="148" />
        <source>Scrobbling</source>
        <translation>Scrobbling</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="149" />
        <source>Enable scrobbling</source>
        <translation>Enable scrobbling</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="151" />
        <source>Submits to Last.fm after 33% of each track has been played.</source>
        <translation>Надсилається на Last.fm після відтворення 33% кожного треку.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="153" />
        <source>YouTube Downloads</source>
        <translation>Завантаження YouTube</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="154" />
        <source>Browser cookies:</source>
        <translation>Cookie браузера:</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="155" />
        <source>Parallel downloads:</source>
        <translation>Паралельні завантаження:</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="157" />
        <source>Select the browser whose YouTube login cookies yt-dlp should use. Required for age-restricted videos. You must be signed into YouTube in the selected browser. Parallel download changes apply to new work.</source>
        <translation>Виберіть браузер, чиї cookie входу YouTube має використовувати yt-dlp. Потрібно для відео з віковими обмеженнями. Ви маєте бути ввійшли в YouTube у вибраному браузері. Зміни паралельних завантажень застосовуються до нових завдань.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="164" />
        <source>Privacy</source>
        <translation>Приватність</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="165" />
        <source>Keep cached data after quitting</source>
        <translation>Зберігати кешовані дані після виходу</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="170" />
        <source>⚠ API credentials not configured.
Set LASTFM_API_KEY and LASTFM_API_SECRET environment variables.</source>
        <translation>⚠ API credentials not configured.
Set LASTFM_API_KEY and LASTFM_API_SECRET environment variables.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="188" />
        <source>🟢 Connected as {username}</source>
        <translation>🟢 Connected as {username}</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="197" />
        <source>🔵 Browser opened — authorize the app, then click «I've authorized».</source>
        <translation>🔵 Browser opened — authorize the app, then click «I've authorized».</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="203" />
        <source>🔴 Not connected</source>
        <translation>🔴 Not connected</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="216" />
        <source>⚠ Could not start authentication. Check API credentials.</source>
        <translation>⚠ Could not start authentication. Check API credentials.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="227" />
        <source>⚠ Authorization not confirmed yet. Authorize in the browser, then try again.</source>
        <translation>⚠ Authorization not confirmed yet. Authorize in the browser, then try again.</translation>
    </message>
    <message>
        <source>Submits to Last.fm after 10 % of each track has been played.</source>
        <translation type="vanished">Submits to Last.fm after 10 % of each track has been played.</translation>
    </message>
</context><context>
    <name>TrackTableModel</name>
    <message>
        <location filename="../ui/track_table_model.py" line="94" />
        <source>Artist</source>
        <translation>Художник</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="96" />
        <source>Title</source>
        <translation>Назва</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="98" />
        <source>Loved at</source>
        <translation>Уподобано о</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="100" />
        <source>Status</source>
        <translation>Статус</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="102" />
        <source>File</source>
        <translation>Файл</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="195" />
        <source>Example Artist</source>
        <translation>Приклад художника</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="196" />
        <source>Example Track</source>
        <translation>Приклад доріжки</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="200" />
        <source>Another Artist</source>
        <translation>Ще один художник</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="201" />
        <source>Waiting for implementation</source>
        <translation>Очікування реалізації</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="210" />
        <source>Fetched</source>
        <translation>Принесено</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="212" />
        <source>Queued</source>
        <translation>У черзі</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="214" />
        <source>Searching</source>
        <translation>Пошук</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="216" />
        <source>Downloading</source>
        <translation>Завантаження</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="218" />
        <source>Downloaded</source>
        <translation>Завантажено</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="220" />
        <source>Failed</source>
        <translation>Не вдалося</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="222" />
        <source>Not found</source>
        <translation>Не знайдено</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="237" />
        <source>{bitrate} kbps</source>
        <translation>{bitrate} кбіт/с</translation>
    </message>
</context><context>
    <name>YouTubeResolver</name>
    <message>
        <location filename="../youtube.py" line="88" />
        <source>Searching {done}/{total}: {artist} - {title}</source>
        <translation>Пошук {done}/{total}: ​​{artist} - {title}</translation>
    </message>
    <message>
        <location filename="../youtube.py" line="233" />
        <source>Resolved {done}/{total}: {artist} - {title}</source>
        <translation>Вирішено {done}/{total}: ​​{artist} - {title}</translation>
    </message>
    <message>
        <location filename="../youtube.py" line="241" />
        <source>No YouTube result {done}/{total}: {artist} - {title}</source>
        <translation>Немає результатів YouTube {done}/{total}: ​​{artist} - {title}</translation>
    </message>
</context></TS>

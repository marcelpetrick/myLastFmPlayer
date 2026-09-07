<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>ApplicationController</name>
    <message>
        <location filename="../controller.py" line="219" />
        <source>Re-checking {missing} not-found and {failed} failed tracks from the last run.</source>
        <translation>Повторна перевірка {missing} незнайдених і {failed} невдалих треків з минулого запуску.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="289" />
        <source>Stopping background work for {username}; completed items remain saved.</source>
        <translation>Фонову роботу для {username} зупинено; завершені елементи залишаються збереженими.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="336" />
        <source>No cached tracks found for {username}; fetching from Last.fm.</source>
        <translation>Збережених треків для {username} не знайдено; отримуємо дані з Last.fm.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="347" />
        <source>Found {count} cached tracks for {username}; checking Last.fm before using them.</source>
        <translation>Знайдено {count} збережених треків для {username}; перед використанням перевіряємо Last.fm.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="367" />
        <source>Loaded {count} cached tracks for {username}; skipped Last.fm fetch.</source>
        <translation>Завантажено {count} збережених треків для {username}; отримання з Last.fm пропущено.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="381" />
        <source>Could not verify Last.fm loved-track count for {username}; using {count} cached tracks: {error}</source>
        <translation>Не вдалося перевірити кількість улюблених треків Last.fm для {username}; використовуємо {count} збережених треків: {error}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="394" />
        <source>Could not read Last.fm loved-track count for {username}; fetching fresh data instead of trusting {count} cached tracks.</source>
        <translation>Не вдалося прочитати кількість улюблених треків Last.fm для {username}; отримуємо свіжі дані замість використання {count} збережених треків.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="406" />
        <source>Last.fm reports {online_count} loved tracks for {username}; cached track count matches.</source>
        <translation>Last.fm повідомляє про {online_count} улюблених треків для {username}; кількість збережених треків збігається.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="417" />
        <source>Last.fm reports {online_count} loved tracks for {username}, but the cache has {cached_count}; fetching fresh data.</source>
        <translation>Last.fm повідомляє про {online_count} улюблених треків для {username}, але локально збережено {cached_count}; отримуємо свіжі дані.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="442" />
        <source>Dependency check finished: {message}</source>
        <translation>Перевірку залежностей завершено: {message}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="459" />
        <source>Could not open data folder: {error}</source>
        <translation>Не вдалося відкрити теку даних: {error}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="469" />
        <source>Opened data folder: {path}</source>
        <translation>Відкрито теку даних: {path}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="478" />
        <source>Could not open data folder: {path}</source>
        <translation>Не вдалося відкрити теку даних: {path}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="490" />
        <source>Could not open artist page: {url}</source>
        <translation>Не вдалося відкрити сторінку виконавця: {url}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="501" />
        <source>Last.fm scrobbling is disabled because {api_key_env}/{api_secret_env} are not configured and no bundled credentials are available.</source>
        <translation>Скроблінг Last.fm вимкнено, оскільки {api_key_env}/{api_secret_env} не налаштовано, а надані облікові дані недоступні.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="516" />
        <source>Loaded Last.fm scrobbling settings; stored session key is {state}.</source>
        <translation>Завантажено налаштування скроблінгу Last.fm; збережений ключ сеансу: {state}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="520" />
        <source>present</source>
        <translation>наявний</translation>
    </message>
    <message>
        <location filename="../controller.py" line="522" />
        <source>missing</source>
        <translation>відсутній</translation>
    </message>
    <message>
        <location filename="../controller.py" line="536" />
        <source>Connected Last.fm scrobbling as {username}.</source>
        <translation>Скроблінг Last.fm підключено як {username}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="544" />
        <source>Stored Last.fm session key could not be verified; scrobbling remains disconnected.</source>
        <translation>Не вдалося перевірити збережений ключ сеансу Last.fm; скроблінг залишається від'єднаним.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="554" />
        <source>Opening preferences.</source>
        <translation>Відкриваємо налаштування.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="568" />
        <source>Preferences closed; no Last.fm scrobbling service is active.</source>
        <translation>Налаштування закрито; жодна служба скроблінгу Last.fm не активна.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="577" />
        <source>Saved Last.fm scrobbling preferences for {username}.</source>
        <translation>Збережено параметри скроблінгу Last.fm для {username}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="581" />
        <source>no user</source>
        <translation>немає користувача</translation>
    </message>
    <message>
        <location filename="../controller.py" line="592" />
        <source>Enter a Last.fm username before fetching tracks.</source>
        <translation>Введіть ім’я користувача Last.fm, перш ніж завантажувати треки.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="602" />
        <source>Background work is already running for {username}.</source>
        <translation>Фонова робота для {username} уже виконується.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="614" />
        <source>Loaded cached tracks</source>
        <translation>Завантажено кешовані треки</translation>
    </message>
    <message>
        <location filename="../controller.py" line="631" />
        <source>Could not reach Last.fm for {username}: {error}</source>
        <translation>Last.fm для {username} недоступний: {error}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="645" />
        <source>Starting fresh Last.fm fetch for {username}; {count} tracks expected.</source>
        <translation>Починаємо нове отримання з Last.fm для {username}; очікується {count} треків.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="654" />
        <source>Starting fresh Last.fm fetch for {username}.</source>
        <translation>Починаємо нове отримання з Last.fm для {username}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="663" />
        <source>Starting fetch</source>
        <translation>Починаємо отримання</translation>
    </message>
    <message>
        <location filename="../controller.py" line="679" />
        <source>Fetch resumed.</source>
        <translation>Отримання відновлено.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="685" />
        <source>Fetch paused.</source>
        <translation>Отримання призупинено.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="695" />
        <source>Stopping fetch.</source>
        <translation>Зупинка отримання.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="709" />
        <source>Enter a Last.fm username before resolving tracks.</source>
        <translation>Введіть ім’я користувача Last.fm, перш ніж шукати треки.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="718" />
        <source>Starting YouTube lookup for {username}; priority={priority}, limit={limit}.</source>
        <translation>Починаємо пошук джерел на YouTube для {username}; пріоритет={priority}, обмеження={limit}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="780" />
        <location filename="../controller.py" line="724" />
        <source>none</source>
        <translation>немає</translation>
    </message>
    <message>
        <location filename="../controller.py" line="784" />
        <location filename="../controller.py" line="728" />
        <source>all</source>
        <translation>усі</translation>
    </message>
    <message>
        <location filename="../controller.py" line="734" />
        <source>Starting YouTube lookup</source>
        <translation>Починаємо пошук джерел на YouTube</translation>
    </message>
    <message>
        <location filename="../controller.py" line="759" />
        <source>Enter a Last.fm username before downloading tracks.</source>
        <translation>Перед завантаженням треків введіть ім’я користувача Last.fm.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="773" />
        <source>Starting downloads for {username}; concurrency={concurrency}, priority={priority}, limit={limit}.</source>
        <translation>Починаємо завантаження для {username}; паралельних={concurrency}, пріоритет={priority}, обмеження={limit}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="789" />
        <source>Starting downloads</source>
        <translation>Починаємо завантаження</translation>
    </message>
    <message>
        <location filename="../controller.py" line="811" />
        <source>Select a downloaded track before playing.</source>
        <translation>Виберіть завантажений трек перед відтворенням.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="829" />
        <source>Playback resumed.</source>
        <translation>Відтворення відновлено.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="838" />
        <source>Playback paused.</source>
        <translation>Відтворення призупинено.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="882" />
        <location filename="../controller.py" line="847" />
        <source>No track is currently playing.</source>
        <translation>Жоден трек зараз не відтворюється.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="858" />
        <source>Playback stopped.</source>
        <translation>Відтворення зупинено.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="903" />
        <source>Seeked playback to {seconds} seconds.</source>
        <translation>Перемотано відтворення до {seconds} с.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1029" />
        <source>Fetch for {username} returned invalid track data.</source>
        <translation>Отримання для {username} повернуло некоректні дані треку.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1039" />
        <source>Fetched and stored {count} tracks for {username}.</source>
        <translation>Отримано та збережено {count} треків для {username}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1063" />
        <source>Stopped fetch for {username} returned invalid data.</source>
        <translation>Зупинене отримання для {username} повернуло некоректні дані.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1073" />
        <source>Stopped fetch for {username} after {count} tracks.</source>
        <translation>Отримання для {username} зупинено після {count} треків.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1086" />
        <source>Fetch for {username} returned invalid partial data.</source>
        <translation>Отримання для {username} повернуло некоректні часткові дані.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1098" />
        <source>Fetch progress for {username}: {count} tracks are visible now.</source>
        <translation>Перебіг отримання для {username}: зараз видно {count} треків.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1106" />
        <source>Fetched {count} tracks for {username}</source>
        <translation>Отримано {count} треків для {username}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1121" />
        <source>Workflow for {username} returned an invalid track update.</source>
        <translation>Робочий процес для {username} повернув некоректне оновлення треку.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1131" />
        <source>Track update from {username}: {artist} - {title} is now {status}.</source>
        <translation>Оновлення треку для {username}: {artist} - {title} тепер має статус {status}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1148" />
        <source>Lookup for {username} returned invalid track data.</source>
        <translation>Пошук для {username} повернув некоректні дані треку.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1231" />
        <location filename="../controller.py" line="1165" />
        <source>YouTube work stopped; completed items remain saved.</source>
        <translation>Роботу з YouTube зупинено; завершені елементи залишаються збереженими.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1172" />
        <source>Resolved YouTube URLs for {resolved_count}/{count} tracks; {not_found_count} were not found.</source>
        <translation>Знайдено URL-адреси YouTube для {resolved_count}/{count} треків; {not_found_count} не знайдено.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1198" />
        <source>No queued tracks are ready for download.</source>
        <translation>У черзі немає треків, готових до завантаження.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1210" />
        <source>Download for {username} returned invalid track data.</source>
        <translation>Завантаження для {username} повернуло некоректні дані треку.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1238" />
        <source>Download run for {username} finished: {downloaded_count}/{count} tracks downloaded, {failed_count} failed.</source>
        <translation>Завантаження для {username} завершено: {downloaded_count}/{count} треків завантажено, {failed_count} не вдалося.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1265" />
        <source>Failed</source>
        <translation>Не вдалося</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1312" />
        <source>Updating Last.fm now-playing for {artist} - {title}.</source>
        <translation>Оновлюємо «зараз відтворюється» Last.fm для {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1321" />
        <source>Playing {artist} - {title}.</source>
        <translation>Відтворюється {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1345" />
        <source>Last.fm returned invalid artist image data.</source>
        <translation>Last.fm повернув некоректні дані зображення виконавця.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1379" />
        <source>Enter a Last.fm username before preparing playback.</source>
        <translation>Перед підготовкою відтворення введіть ім’я користувача Last.fm.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1389" />
        <source>Preparing {artist} - {title} for playback.</source>
        <translation>Готуємо {artist} - {title} до відтворення.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1406" />
        <source>Starting automatic YouTube lookup for {count} fetched tracks.</source>
        <translation>Починаємо автоматичний пошук джерел на YouTube для {count} отриманих треків.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1447" />
        <source>Stopping YouTube checks and downloads; completed items remain saved.</source>
        <translation>Зупинення перевірок і завантажень YouTube; завершені елементи залишаються збереженими.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1463" />
        <source>Resuming YouTube work.</source>
        <translation>Відновлення роботи з YouTube.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1471" />
        <source>No YouTube work remains to resume.</source>
        <translation>Немає роботи з YouTube, яку можна відновити.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1483" />
        <source>Enter a Last.fm username before retrying a download.</source>
        <translation>Введіть ім’я користувача Last.fm перед повторною спробою завантаження.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1512" />
        <source>Retrying download for {artist} - {title}.</source>
        <translation>Повторна спроба завантаження для {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1525" />
        <source>Starting automatic download queue for resolved tracks.</source>
        <translation>Запускаємо чергу автоматичного завантаження для знайдених треків.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1540" />
        <source>Starting priority download for selected track.</source>
        <translation>Починаємо пріоритетне завантаження вибраного треку.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1635" />
        <source>Submitting Last.fm scrobble for {artist} - {title}.</source>
        <translation>Надсилаємо скробл Last.fm для {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1665" />
        <source>Finished playback for {artist} - {title}.</source>
        <translation>Завершено відтворення {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1678" />
        <source>Playback finished.</source>
        <translation>Відтворення завершено.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1689" />
        <source>Continuing with random track: {artist} - {title}.</source>
        <translation>Продовжуємо випадковим треком: {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1700" />
        <source>Continuing with next track: {artist} - {title}.</source>
        <translation>Продовжуємо наступним треком: {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1720" />
        <source>All background work is finished; controls are enabled again.</source>
        <translation>Вся фонова робота завершена; елементи керування знову ввімкнено.</translation>
    </message>
    <message>
        <source>Downloads stopped by user.</source>
        <translation type="vanished">Завантаження зупинено користувачем.</translation>
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
        <location filename="../download.py" line="141" />
        <source>Queued {count} downloads</source>
        <translation>У черзі {count} завантажень</translation>
    </message>
    <message>
        <location filename="../download.py" line="198" />
        <source>Downloaded {done}/{total} tracks</source>
        <translation>Завантажено треків: {done}/{total}</translation>
    </message>
</context><context>
    <name>FetchLovedTracksWorker</name>
    <message>
        <location filename="../workers.py" line="81" />
        <source>Looking up Last.fm user {username}</source>
        <translation>Пошук користувача Last.fm {username}</translation>
    </message>
    <message>
        <location filename="../workers.py" line="97" />
        <source>Stopped fetch after {count} tracks</source>
        <translation>Отримання зупинено після {count} треків</translation>
    </message>
    <message>
        <location filename="../workers.py" line="107" />
        <source>Fetched {count} tracks</source>
        <translation>Отримано {count} треків</translation>
    </message>
</context><context>
    <name>LastFmLovedTracksScraper</name>
    <message>
        <location filename="../lastfm.py" line="392" />
        <source>Found Last.fm user {username}</source>
        <translation>Знайдено користувача Last.fm {username}</translation>
    </message>
    <message>
        <location filename="../lastfm.py" line="695" />
        <source>Fetched {count} tracks</source>
        <translation>Отримано {count} треків</translation>
    </message>
    <message>
        <location filename="../lastfm.py" line="700" />
        <source>Fetched {done}/{total} tracks</source>
        <translation>Отримано {done}/{total} треків</translation>
    </message>
</context><context>
    <name>LookupTracksWorker</name>
    <message>
        <location filename="../workers.py" line="193" />
        <source>Resolving YouTube URLs for {username}</source>
        <translation>Пошук URL-адрес YouTube для {username}</translation>
    </message>
    <message>
        <location filename="../workers.py" line="212" />
        <source>YouTube lookup stopped</source>
        <translation>Пошук у YouTube зупинено</translation>
    </message>
    <message>
        <location filename="../workers.py" line="217" />
        <source>Resolved {count} tracks</source>
        <translation>Знайдено {count} треків</translation>
    </message>
</context><context>
    <name>MainWindow</name>
    <message>
        <location filename="../ui/main_window.py" line="1147" />
        <location filename="../ui/main_window.py" line="204" />
        <source>Ready</source>
        <translation>Готово</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="414" />
        <source>Retry Download</source>
        <translation>Повторити завантаження</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1140" />
        <location filename="../ui/main_window.py" line="523" />
        <source>Idle</source>
        <translation>Очікування</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="546" />
        <source>Loaded {count} tracks</source>
        <translation>Завантажено {count} треків</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="550" />
        <source>Playlist: {count} titles</source>
        <translation>Список відтворення: {count} треків</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="577" />
        <source>Resume</source>
        <translation>Відновити</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1119" />
        <location filename="../ui/main_window.py" line="577" />
        <source>Pause</source>
        <translation>Пауза</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1120" />
        <location filename="../ui/main_window.py" line="578" />
        <source>Stop</source>
        <translation>Зупинити</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="580" />
        <source>Resume the paused Last.fm fetch</source>
        <translation>Відновити призупинене отримання Last.fm</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="582" />
        <source>Pause the active Last.fm fetch</source>
        <translation>Призупинити активне отримання Last.fm</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="583" />
        <source>Stop the active Last.fm fetch</source>
        <translation>Зупинити активне отримання Last.fm</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="608" />
        <source>Stopping YouTube…</source>
        <translation>Зупинення YouTube…</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="610" />
        <source>Resume YouTube</source>
        <translation>Відновити YouTube</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="612" />
        <source>Stop YouTube</source>
        <translation>Зупинити YouTube</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="615" />
        <source>Stop or resume YouTube checks and downloads</source>
        <translation>Зупинити або відновити перевірки й завантаження YouTube</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="619" />
        <source>Fetch</source>
        <translation>Отримати</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="621" />
        <source>Fetch loved tracks, then automatically check and download them from YouTube</source>
        <translation>Отримати улюблені композиції, потім автоматично перевірити й завантажити їх із YouTube</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="782" />
        <source>Updated {artist} - {title}: {status}</source>
        <translation>Оновлено {artist} - {title}: {status}</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1117" />
        <location filename="../ui/main_window.py" line="799" />
        <source>Not playing</source>
        <translation>Не відтворюється</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="818" />
        <source>Artist</source>
        <translation>Виконавець</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1094" />
        <location filename="../ui/main_window.py" line="886" />
        <source>About myLastFmPlayer</source>
        <translation>Про myLastFmPlayer</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="892" />
        <source>myLastFmPlayer {version}</source>
        <translation>myLastFmPlayer {version}</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="893" />
        <source>Author: Marcel Petrick &lt;a href="mailto:mail@marcelpetrick.it"&gt;mail@marcelpetrick.it&lt;/a&gt;</source>
        <translation>Автор: Marcel Petrick &lt;a href="mailto:mail@marcelpetrick.it"&gt;mail@marcelpetrick.it&lt;/a&gt;</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="897" />
        <source>License: GNU GPLv3 or later.</source>
        <translation>Ліцензія: GNU GPLv3 або новіша.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="898" />
        <source>This application fetches a user's public loved tracks from Last.fm, keeps local metadata, resolves playable sources through yt-dlp, downloads MP3 files, and plays them locally.</source>
        <translation>Ця програма отримує публічні улюблені треки користувача з Last.fm, зберігає локальні метадані, знаходить джерела для відтворення через yt-dlp, завантажує MP3-файли й відтворює їх локально.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="903" />
        <source>It is intended as a practical Linux desktop helper for rebuilding a personal loved-track collection without manually searching every song.</source>
        <translation>Вона задумана як практичний помічник для робочого столу Linux, щоб відновити особисту колекцію улюблених треків без ручного пошуку кожної пісні.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="907" />
        <source>Optional Last.fm scrobbling can connect the local playback workflow back to the user's Last.fm account.</source>
        <translation>Необов'язковий скроблінг Last.fm може пов'язати локальне відтворення з обліковим записом користувача Last.fm.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1095" />
        <location filename="../ui/main_window.py" line="917" />
        <source>Open Source Licenses</source>
        <translation>Ліцензії відкритого коду</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="923" />
        <source>myLastFmPlayer is GPLv3-or-later software and uses these open-source libraries and external tools:</source>
        <translation>myLastFmPlayer є програмою за ліцензією GPLv3 або новішою та використовує ці бібліотеки відкритого коду й зовнішні інструменти:</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="987" />
        <location filename="../ui/main_window.py" line="929" />
        <source>Python Software Foundation License; runtime for the application.</source>
        <translation>Python Software Foundation License; середовище виконання програми.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="989" />
        <location filename="../ui/main_window.py" line="933" />
        <source>GNU GPL v3; Python bindings for the Qt desktop interface.</source>
        <translation>GNU GPL v3; прив'язки Python для настільного інтерфейсу Qt.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="990" />
        <location filename="../ui/main_window.py" line="937" />
        <source>GNU LGPL v3 / GPL v3; cross-platform UI toolkit.</source>
        <translation>GNU LGPL v3 / GPL v3; кросплатформний інструментарій інтерфейсу.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="992" />
        <location filename="../ui/main_window.py" line="941" />
        <source>Apache License 2.0; HTTP client for Last.fm API calls.</source>
        <translation>Apache License 2.0; HTTP-клієнт для викликів API Last.fm.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="993" />
        <location filename="../ui/main_window.py" line="945" />
        <source>Apache License 2.0; Last.fm scrobbling integration.</source>
        <translation>Apache License 2.0; інтеграція скроблінгу Last.fm.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="994" />
        <location filename="../ui/main_window.py" line="949" />
        <source>Unlicense; media lookup and download helper.</source>
        <translation>Unlicense; допоміжний інструмент для пошуку й завантаження медіа.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="996" />
        <location filename="../ui/main_window.py" line="953" />
        <source>LGPL/GPL family licenses depending on the installed build; audio conversion backend.</source>
        <translation>Родина ліцензій LGPL/GPL залежно від установленої збірки; бекенд перетворення аудіо.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="958" />
        <source>Development tools include {tools} under their respective open-source licenses.</source>
        <translation>Інструменти розробки включають {tools} за відповідними ліцензіями відкритого коду.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="974" />
        <source>This summary is informational; the complete license texts are provided by the installed projects and system packages.</source>
        <translation>Цей підсумок є інформаційним; повні тексти ліцензій надаються встановленими проєктами та системними пакетами.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1091" />
        <source>Fetch loved tracks</source>
        <translation>Отримати улюблені треки</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1092" />
        <source>Preferences</source>
        <translation>Налаштування</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1093" />
        <source>Open data folder in file manager</source>
        <translation>Відкрити теку даних у файловому менеджері</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1096" />
        <source>Quit</source>
        <translation>Вийти</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1097" />
        <source>Main</source>
        <translation>Головна</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1098" />
        <source>Theme</source>
        <translation>Тема</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1099" />
        <source>Light</source>
        <translation>Світла</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1100" />
        <source>Dark</source>
        <translation>Темна</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1101" />
        <source>Lilac</source>
        <translation>Бузкова</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1102" />
        <source>Mint</source>
        <translation>М'ятна</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1103" />
        <source>Language</source>
        <translation>Мова</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1104" />
        <source>Help</source>
        <translation>Довідка</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1105" />
        <source>Last.fm username</source>
        <translation>Ім'я користувача Last.fm</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1106" />
        <source>Enter username</source>
        <translation>Введіть ім'я користувача</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1109" />
        <source>Filter</source>
        <translation>Фільтр</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1110" />
        <source>Artist or track title</source>
        <translation>Виконавець або назва треку</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1111" />
        <source>Reset</source>
        <translation>Скинути</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1113" />
        <source>Enter your Last.fm username and press Fetch to load your loved tracks.</source>
        <translation>Введіть ім'я користувача Last.fm і натисніть «Отримати», щоб завантажити улюблені треки.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1115" />
        <source>Playback</source>
        <translation>Відтворення</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1118" />
        <source>Play</source>
        <translation>Відтворити</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1121" />
        <source>Next</source>
        <translation>Далі</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1123" />
        <location filename="../ui/main_window.py" line="1122" />
        <source>Volume</source>
        <translation>Гучність</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1124" />
        <source>Mute</source>
        <translation>Без звуку</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1125" />
        <source>Randomize</source>
        <translation>У випадковому порядку</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1127" />
        <source>Open artist page on Last.fm</source>
        <translation>Відкрити сторінку виконавця на Last.fm у приватному вікні</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1128" />
        <source>Playback position</source>
        <translation>Позиція відтворення</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1129" />
        <source>Clear log</source>
        <translation>Очистити журнал</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1130" />
        <source>Clear status updates and errors</source>
        <translation>Очистити оновлення статусу та помилки</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1132" />
        <source>Status updates and errors will appear here.</source>
        <translation>Тут відображатимуться оновлення статусу та помилки.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1137" />
        <source>Dependencies: yt-dlp, ffmpeg, and ffprobe not checked yet</source>
        <translation>Залежності: yt-dlp, ffmpeg і ffprobe ще не перевірено</translation>
    </message>
    <message>
        <source>Stop Downloads</source>
        <translation type="vanished">Зупинити завантаження</translation>
    </message>
    <message>
        <source>Start Downloads</source>
        <translation type="vanished">Почати завантаження</translation>
    </message>
    <message>
        <source>Downloads</source>
        <translation type="vanished">Завантаження</translation>
    </message>
    <message>
        <source>MIT License; legacy Last.fm HTML parser support.</source>
        <translation type="vanished">MIT License; підтримка застарілого HTML-парсера Last.fm.</translation>
    </message>
    <message>
        <source>Author: Marcel Petrick &lt;mail@marcelpetrick.it&gt;</source>
        <translation type="vanished">Автор: Marcel Petrick &lt;mail@marcelpetrick.it&gt;</translation>
    </message>
    <message>
        <source>Python - Python Software Foundation License; runtime for the application.</source>
        <translation type="vanished">Python - Python Software Foundation License; середовище виконання програми.</translation>
    </message>
    <message>
        <source>PyQt6 - GNU GPL v3; Python bindings for the Qt desktop interface.</source>
        <translation type="vanished">PyQt6 - GNU GPL v3; прив'язки Python для настільного інтерфейсу Qt.</translation>
    </message>
    <message>
        <source>Qt 6 - GNU LGPL v3 / GPL v3; cross-platform UI toolkit.</source>
        <translation type="vanished">Qt 6 - GNU LGPL v3 / GPL v3; кросплатформний набір інструментів UI.</translation>
    </message>
    <message>
        <source>requests - Apache License 2.0; HTTP client for Last.fm API calls.</source>
        <translation type="vanished">requests - Apache License 2.0; HTTP-клієнт для викликів API Last.fm.</translation>
    </message>
    <message>
        <source>beautifulsoup4 - MIT License; legacy Last.fm HTML parser support.</source>
        <translation type="vanished">beautifulsoup4 - MIT License; підтримка застарілого HTML-парсера Last.fm.</translation>
    </message>
    <message>
        <source>pylast - Apache License 2.0; Last.fm scrobbling integration.</source>
        <translation type="vanished">pylast - Apache License 2.0; інтеграція скроблінгу Last.fm.</translation>
    </message>
    <message>
        <source>yt-dlp - Unlicense; media lookup and download helper.</source>
        <translation type="vanished">yt-dlp - Unlicense; допоміжний інструмент для пошуку й завантаження медіа.</translation>
    </message>
    <message>
        <source>FFmpeg - LGPL/GPL family licenses depending on the installed build; audio conversion backend.</source>
        <translation type="vanished">FFmpeg - родина ліцензій LGPL/GPL залежно від установленої збірки; бекенд перетворення аудіо.</translation>
    </message>
    <message>
        <source>Development tools include pytest, pytest-cov, coverage.py, Ruff, Pylint, Sphinx, and build under their respective open-source licenses.</source>
        <translation type="vanished">Інструменти розробки включають pytest, pytest-cov, coverage.py, Ruff, Pylint, Sphinx і build під їхніми відповідними ліцензіями відкритого коду.</translation>
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
        <location filename="../ui/preferences_dialog.py" line="179" />
        <location filename="../ui/preferences_dialog.py" line="138" />
        <source>None (disabled)</source>
        <translation>Немає (вимкнено)</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="158" />
        <source>Preferences</source>
        <translation>Налаштування</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="159" />
        <source>Last.fm Authentication</source>
        <translation>Автентифікація Last.fm</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="160" />
        <source>Authenticate with Last.fm</source>
        <translation>Увійти через Last.fm</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="161" />
        <source>I've authorized</source>
        <translation>Я авторизувався</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="162" />
        <source>Disconnect</source>
        <translation>Від'єднати</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="163" />
        <source>Scrobbling</source>
        <translation>Скроблінг</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="164" />
        <source>Enable scrobbling</source>
        <translation>Увімкнути скроблінг</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="166" />
        <source>Submits to Last.fm after 33% of each track has been played.</source>
        <translation>Надсилати на Last.fm після відтворення 33% кожного треку.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="168" />
        <source>YouTube Downloads</source>
        <translation>Завантаження YouTube</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="169" />
        <source>Browser cookies:</source>
        <translation>Cookie браузера:</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="170" />
        <source>Parallel YouTube checks and downloads:</source>
        <translation>Паралельні перевірки YouTube і завантаження:</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="172" />
        <source>Select the browser whose YouTube login cookies yt-dlp should use. Required for age-restricted videos. You must be signed into YouTube in the selected browser. The parallel-work limit applies to new YouTube checks and downloads.</source>
        <translation>Виберіть браузер, чиї cookie входу в YouTube має використовувати yt-dlp. Це необхідно для відео з віковими обмеженнями. У вибраному браузері потрібно ввійти в YouTube. Обмеження паралельної роботи застосовується до нових перевірок YouTube і завантажень.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="180" />
        <source>Privacy</source>
        <translation>Конфіденційність</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="182" />
        <source>Keep saved library and Last.fm session after quitting</source>
        <translation>Зберігати бібліотеку та сеанс Last.fm після виходу</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="185" />
        <source>When disabled, closing the app deletes saved track lists, lookup and download caches, and Last.fm authentication. Downloaded audio files remain.</source>
        <translation>Якщо вимкнено, під час закриття програми видаляються збережені списки композицій, кеші пошуку й завантажень та автентифікація Last.fm. Завантажені аудіофайли зберігаються.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="195" />
        <source>⚠ API credentials not configured.
Set LASTFM_API_KEY and LASTFM_API_SECRET environment variables.</source>
        <translation>⚠ Облікові дані API не налаштовано.
Задайте змінні середовища LASTFM_API_KEY і LASTFM_API_SECRET.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="214" />
        <source>🟢 Connected as {username}</source>
        <translation>🟢 Підключено як {username}</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="223" />
        <source>🔵 Browser opened — authorize the app, then click «I've authorized».</source>
        <translation>🔵 Браузер відкрито — авторизуйте застосунок, а потім натисніть «Я авторизувався».</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="229" />
        <source>🔴 Not connected</source>
        <translation>🔴 Не підключено</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="252" />
        <source>⚠ Could not start authentication. Check API credentials.</source>
        <translation>⚠ Не вдалося почати автентифікацію. Перевірте облікові дані API.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="263" />
        <source>⚠ Authorization not confirmed yet. Authorize in the browser, then try again.</source>
        <translation>⚠ Авторизацію ще не підтверджено. Авторизуйтеся в браузері, а потім спробуйте ще раз.</translation>
    </message>
    <message>
        <source>Keep cached data after quitting</source>
        <translation type="vanished">Зберігати кешовані дані після закриття</translation>
    </message>
    <message>
        <source>Parallel downloads:</source>
        <translation type="vanished">Паралельні завантаження:</translation>
    </message>
    <message>
        <source>Select the browser whose YouTube login cookies yt-dlp should use. Required for age-restricted videos. You must be signed into YouTube in the selected browser. Parallel download changes apply to new work.</source>
        <translation type="vanished">Виберіть браузер, cookie входу YouTube з якого має використовувати yt-dlp. Це потрібно для відео з віковими обмеженнями. У вибраному браузері потрібно ввійти в YouTube. Зміни паралельних завантажень застосовуються до нових завдань.</translation>
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
        <translation>Виконавець</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="96" />
        <source>Title</source>
        <translation>Назва</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="98" />
        <source>Loved at</source>
        <translation>Уподобано</translation>
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
        <location filename="../ui/track_table_model.py" line="193" />
        <source>Fetched</source>
        <translation>Отримано</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="195" />
        <source>Queued</source>
        <translation>У черзі</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="197" />
        <source>Searching</source>
        <translation>Пошук</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="199" />
        <source>Lookup failed</source>
        <translation>Помилка пошуку</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="201" />
        <source>Downloading</source>
        <translation>Завантаження</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="203" />
        <source>Downloaded</source>
        <translation>Завантажено</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="205" />
        <source>Failed</source>
        <translation>Не вдалося</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="207" />
        <source>Not found</source>
        <translation>Не знайдено</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="222" />
        <source>{bitrate} kbps</source>
        <translation>{bitrate} кбіт/с</translation>
    </message>
</context><context>
    <name>YouTubeResolver</name>
    <message>
        <location filename="../youtube.py" line="156" />
        <source>Searching {done}/{total}: {artist} - {title}</source>
        <translation>Пошук {done}/{total}: {artist} - {title}</translation>
    </message>
    <message>
        <location filename="../youtube.py" line="377" />
        <source>Resolved {done}/{total}: {artist} - {title}</source>
        <translation>Знайдено {done}/{total}: {artist} - {title}</translation>
    </message>
    <message>
        <location filename="../youtube.py" line="385" />
        <source>No YouTube result {done}/{total}: {artist} - {title}</source>
        <translation>Немає результату YouTube {done}/{total}: {artist} - {title}</translation>
    </message>
</context></TS>

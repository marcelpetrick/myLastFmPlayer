<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>ApplicationController</name>
    <message>
        <location filename="../controller.py" line="175" />
        <source>No cached tracks found for {username}; fetching from Last.fm.</source>
        <translation>Кешованих треків для {username} не знайдено; отримуємо дані з Last.fm.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="186" />
        <source>Found {count} cached tracks for {username}; checking Last.fm before using them.</source>
        <translation>Знайдено {count} кешованих треків для {username}; перед використанням перевіряємо Last.fm.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="206" />
        <source>Loaded {count} cached tracks for {username}; skipped Last.fm fetch.</source>
        <translation>Завантажено {count} кешованих треків для {username}; отримання з Last.fm пропущено.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="220" />
        <source>Could not verify Last.fm loved-track count for {username}; using {count} cached tracks: {error}</source>
        <translation>Не вдалося перевірити кількість улюблених треків Last.fm для {username}; використовуємо {count} кешованих треків: {error}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="233" />
        <source>Could not read Last.fm loved-track count for {username}; fetching fresh data instead of trusting {count} cached tracks.</source>
        <translation>Не вдалося прочитати кількість улюблених треків Last.fm для {username}; отримуємо свіжі дані замість використання {count} кешованих треків.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="245" />
        <source>Last.fm reports {online_count} loved tracks for {username}; cached track count matches.</source>
        <translation>Last.fm повідомляє про {online_count} улюблених треків для {username}; кількість у кеші збігається.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="256" />
        <source>Last.fm reports {online_count} loved tracks for {username}, but the cache has {cached_count}; fetching fresh data.</source>
        <translation>Last.fm повідомляє про {online_count} улюблених треків для {username}, але в кеші є {cached_count}; отримуємо свіжі дані.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="281" />
        <source>Dependency check finished: {message}</source>
        <translation>Перевірку залежностей завершено: {message}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="298" />
        <source>Could not open data folder: {error}</source>
        <translation>Не вдалося відкрити теку даних: {error}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="308" />
        <source>Opened data folder: {path}</source>
        <translation>Відкрито теку даних: {path}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="317" />
        <source>Could not open data folder: {path}</source>
        <translation>Не вдалося відкрити теку даних: {path}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="329" />
        <source>Could not open artist page: {url}</source>
        <translation>Не вдалося відкрити сторінку виконавця: {url}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="340" />
        <source>Last.fm scrobbling is disabled because {api_key_env}/{api_secret_env} are not configured and no bundled credentials are available.</source>
        <translation>Скроблінг Last.fm вимкнено, оскільки {api_key_env}/{api_secret_env} не налаштовано, а вбудовані облікові дані недоступні.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="355" />
        <source>Loaded Last.fm scrobbling settings; stored session key is {state}.</source>
        <translation>Завантажено налаштування скроблінгу Last.fm; збережений ключ сеансу: {state}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="359" />
        <source>present</source>
        <translation>наявний</translation>
    </message>
    <message>
        <location filename="../controller.py" line="361" />
        <source>missing</source>
        <translation>відсутній</translation>
    </message>
    <message>
        <location filename="../controller.py" line="375" />
        <source>Connected Last.fm scrobbling as {username}.</source>
        <translation>Скроблінг Last.fm підключено як {username}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="383" />
        <source>Stored Last.fm session key could not be verified; scrobbling remains disconnected.</source>
        <translation>Не вдалося перевірити збережений ключ сеансу Last.fm; скроблінг залишається від'єднаним.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="393" />
        <source>Opening preferences.</source>
        <translation>Відкриваємо налаштування.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="407" />
        <source>Preferences closed; no Last.fm scrobbling service is active.</source>
        <translation>Налаштування закрито; жодна служба скроблінгу Last.fm не активна.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="416" />
        <source>Saved Last.fm scrobbling preferences for {username}.</source>
        <translation>Збережено параметри скроблінгу Last.fm для {username}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="420" />
        <source>no user</source>
        <translation>немає користувача</translation>
    </message>
    <message>
        <location filename="../controller.py" line="431" />
        <source>Enter a Last.fm username before fetching tracks.</source>
        <translation>Введіть ім’я користувача Last.fm, перш ніж завантажувати треки.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="442" />
        <source>Loaded cached tracks</source>
        <translation>Завантажено кешовані треки</translation>
    </message>
    <message>
        <location filename="../controller.py" line="459" />
        <source>Could not reach Last.fm for {username}: {error}</source>
        <translation>Last.fm для {username} недоступний: {error}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="473" />
        <source>Starting fresh Last.fm fetch for {username}; {count} tracks expected.</source>
        <translation>Починаємо нове отримання з Last.fm для {username}; очікується {count} треків.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="482" />
        <source>Starting fresh Last.fm fetch for {username}.</source>
        <translation>Починаємо нове отримання з Last.fm для {username}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="491" />
        <source>Starting fetch</source>
        <translation>Починаємо отримання</translation>
    </message>
    <message>
        <location filename="../controller.py" line="507" />
        <source>Fetch resumed.</source>
        <translation>Отримання відновлено.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="513" />
        <source>Fetch paused.</source>
        <translation>Отримання призупинено.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="523" />
        <source>Stopping fetch.</source>
        <translation>Зупинка отримання.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="537" />
        <source>Enter a Last.fm username before resolving tracks.</source>
        <translation>Введіть ім’я користувача Last.fm, перш ніж шукати треки.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="546" />
        <source>Starting YouTube lookup for {username}; priority={priority}, limit={limit}.</source>
        <translation>Починаємо пошук на YouTube для {username}; пріоритет={priority}, обмеження={limit}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="606" />
        <location filename="../controller.py" line="552" />
        <source>none</source>
        <translation>немає</translation>
    </message>
    <message>
        <location filename="../controller.py" line="610" />
        <location filename="../controller.py" line="556" />
        <source>all</source>
        <translation>усі</translation>
    </message>
    <message>
        <location filename="../controller.py" line="562" />
        <source>Starting YouTube lookup</source>
        <translation>Починаємо пошук на YouTube</translation>
    </message>
    <message>
        <location filename="../controller.py" line="585" />
        <source>Enter a Last.fm username before downloading tracks.</source>
        <translation>Перед завантаженням треків введіть ім’я користувача Last.fm.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="599" />
        <source>Starting downloads for {username}; concurrency={concurrency}, priority={priority}, limit={limit}.</source>
        <translation>Починаємо завантаження для {username}; паралельних={concurrency}, пріоритет={priority}, обмеження={limit}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="615" />
        <source>Starting downloads</source>
        <translation>Починаємо завантаження</translation>
    </message>
    <message>
        <location filename="../controller.py" line="636" />
        <source>Select a downloaded track before playing.</source>
        <translation>Виберіть завантажений трек перед відтворенням.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="652" />
        <source>Playback resumed.</source>
        <translation>Відтворення відновлено.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="661" />
        <source>Playback paused.</source>
        <translation>Відтворення призупинено.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="689" />
        <location filename="../controller.py" line="670" />
        <source>No track is currently playing.</source>
        <translation>Жоден трек зараз не відтворюється.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="681" />
        <source>Playback stopped.</source>
        <translation>Відтворення зупинено.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="710" />
        <source>Seeked playback to {seconds} seconds.</source>
        <translation>Перемотано відтворення до {seconds} с.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="775" />
        <source>Fetch for {username} returned invalid track data.</source>
        <translation>Отримання для {username} повернуло некоректні дані треку.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="785" />
        <source>Fetched and stored {count} tracks for {username}.</source>
        <translation>Отримано та збережено {count} треків для {username}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="808" />
        <source>Stopped fetch for {username} returned invalid data.</source>
        <translation>Зупинене отримання для {username} повернуло некоректні дані.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="818" />
        <source>Stopped fetch for {username} after {count} tracks.</source>
        <translation>Отримання для {username} зупинено після {count} треків.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="829" />
        <source>Fetch for {username} returned invalid partial data.</source>
        <translation>Отримання для {username} повернуло некоректні часткові дані.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="840" />
        <source>Fetch progress for {username}: {count} tracks are visible now.</source>
        <translation>Перебіг отримання для {username}: зараз видно {count} треків.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="848" />
        <source>Fetched {count} tracks for {username}</source>
        <translation>Отримано {count} треків для {username}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="867" />
        <source>Workflow for {username} returned an invalid track update.</source>
        <translation>Робочий процес для {username} повернув некоректне оновлення треку.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="877" />
        <source>Track update from {username}: {artist} - {title} is now {status}.</source>
        <translation>Оновлення треку для {username}: {artist} - {title} тепер {status}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="892" />
        <source>Lookup for {username} returned invalid track data.</source>
        <translation>Пошук для {username} повернув некоректні дані треку.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="908" />
        <source>Resolved YouTube URLs for {resolved_count}/{count} tracks; {not_found_count} were not found.</source>
        <translation>Знайдено URL-адреси YouTube для {resolved_count}/{count} треків; не знайдено {not_found_count}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="932" />
        <source>No queued tracks are ready for download.</source>
        <translation>У черзі немає треків, готових до завантаження.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="943" />
        <source>Download for {username} returned invalid track data.</source>
        <translation>Завантаження для {username} повернуло некоректні дані треку.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="963" />
        <source>Download run for {username} finished: {downloaded_count}/{count} tracks downloaded, {failed_count} failed.</source>
        <translation>Завантаження для {username} завершено: {downloaded_count}/{count} треків завантажено, {failed_count} не вдалося.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="990" />
        <source>Failed</source>
        <translation>Не вдалося</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1028" />
        <source>Updating Last.fm now-playing for {artist} - {title}.</source>
        <translation>Оновлюємо «зараз відтворюється» Last.fm для {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1037" />
        <source>Playing {artist} - {title}.</source>
        <translation>Відтворюється {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1061" />
        <source>Last.fm returned invalid artist image data.</source>
        <translation>Last.fm повернув некоректні дані зображення виконавця.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1091" />
        <source>Enter a Last.fm username before preparing playback.</source>
        <translation>Перед підготовкою відтворення введіть ім’я користувача Last.fm.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1100" />
        <source>Preparing {artist} - {title} for playback.</source>
        <translation>Готуємо {artist} - {title} до відтворення.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1117" />
        <source>Starting automatic YouTube lookup for {count} fetched tracks.</source>
        <translation>Починаємо автоматичний пошук на YouTube для {count} отриманих треків.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1133" />
        <source>Downloads stopped by user.</source>
        <translation>Завантаження зупинено користувачем.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1142" />
        <source>Enter a Last.fm username before retrying a download.</source>
        <translation>Введіть ім’я користувача Last.fm перед повторною спробою завантаження.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1160" />
        <source>Retrying download for {artist} - {title}.</source>
        <translation>Повторна спроба завантаження для {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1173" />
        <source>Starting automatic download queue for resolved tracks.</source>
        <translation>Запускаємо чергу автоматичного завантаження для знайдених треків.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1181" />
        <source>Starting priority download for selected track.</source>
        <translation>Починаємо пріоритетне завантаження вибраного треку.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1255" />
        <source>Submitting Last.fm scrobble for {artist} - {title}.</source>
        <translation>Надсилаємо скробл Last.fm для {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1285" />
        <source>Finished playback for {artist} - {title}.</source>
        <translation>Завершено відтворення {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1305" />
        <location filename="../controller.py" line="1295" />
        <source>Playback finished.</source>
        <translation>Відтворення завершено.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1316" />
        <source>Continuing with random track: {artist} - {title}.</source>
        <translation>Продовжуємо випадковим треком: {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1327" />
        <source>Continuing with next track: {artist} - {title}.</source>
        <translation>Продовжуємо наступним треком: {artist} - {title}.</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1347" />
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
        <translation>Завантажено треків: {done}/{total}</translation>
    </message>
</context><context>
    <name>FetchLovedTracksWorker</name>
    <message>
        <location filename="../workers.py" line="79" />
        <source>Looking up Last.fm user {username}</source>
        <translation>Пошук користувача Last.fm {username}</translation>
    </message>
    <message>
        <location filename="../workers.py" line="95" />
        <source>Stopped fetch after {count} tracks</source>
        <translation>Отримання зупинено після {count} треків</translation>
    </message>
    <message>
        <location filename="../workers.py" line="105" />
        <source>Fetched {count} tracks</source>
        <translation>Отримано {count} треків</translation>
    </message>
</context><context>
    <name>LastFmLovedTracksScraper</name>
    <message>
        <location filename="../lastfm.py" line="514" />
        <source>Found Last.fm user {username}</source>
        <translation>Знайдено користувача Last.fm {username}</translation>
    </message>
    <message>
        <location filename="../lastfm.py" line="904" />
        <source>Fetched {count} tracks</source>
        <translation>Отримано {count} треків</translation>
    </message>
    <message>
        <location filename="../lastfm.py" line="909" />
        <source>Fetched {done}/{total} tracks</source>
        <translation>Отримано {done}/{total} треків</translation>
    </message>
</context><context>
    <name>LookupTracksWorker</name>
    <message>
        <location filename="../workers.py" line="183" />
        <source>Resolving YouTube URLs for {username}</source>
        <translation>Пошук URL-адрес YouTube для {username}</translation>
    </message>
    <message>
        <location filename="../workers.py" line="199" />
        <source>Resolved {count} tracks</source>
        <translation>Знайдено {count} треків</translation>
    </message>
</context><context>
    <name>MainWindow</name>
    <message>
        <location filename="../ui/main_window.py" line="1007" />
        <location filename="../ui/main_window.py" line="187" />
        <source>Ready</source>
        <translation>Готово</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="385" />
        <source>Retry Download</source>
        <translation>Повторити завантаження</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1000" />
        <location filename="../ui/main_window.py" line="478" />
        <source>Idle</source>
        <translation>Очікування</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="502" />
        <source>Loaded {count} tracks</source>
        <translation>Завантажено {count} треків</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="513" />
        <source>Playlist: {count} titles</source>
        <translation>Список відтворення: {count} треків</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="534" />
        <source>Resume</source>
        <translation>Відновити</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="976" />
        <location filename="../ui/main_window.py" line="534" />
        <source>Pause</source>
        <translation>Пауза</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="977" />
        <location filename="../ui/main_window.py" line="535" />
        <source>Stop</source>
        <translation>Зупинити</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="537" />
        <source>Resume the paused Last.fm fetch</source>
        <translation>Відновити призупинене отримання Last.fm</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="539" />
        <source>Pause the active Last.fm fetch</source>
        <translation>Призупинити активне отримання Last.fm</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="540" />
        <source>Stop the active Last.fm fetch</source>
        <translation>Зупинити активне отримання Last.fm</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="985" />
        <location filename="../ui/main_window.py" line="550" />
        <source>Stop Downloads</source>
        <translation>Зупинити завантаження</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="985" />
        <location filename="../ui/main_window.py" line="554" />
        <source>Start Downloads</source>
        <translation>Почати завантаження</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="672" />
        <source>Updated {artist} - {title}: {status}</source>
        <translation>Оновлено {artist} - {title}: {status}</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="974" />
        <location filename="../ui/main_window.py" line="689" />
        <source>Not playing</source>
        <translation>Не відтворюється</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="955" />
        <location filename="../ui/main_window.py" line="747" />
        <source>About myLastFmPlayer</source>
        <translation>Про myLastFmPlayer</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="753" />
        <source>myLastFmPlayer {version}</source>
        <translation>myLastFmPlayer {version}</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="754" />
        <source>Author: Marcel Petrick &lt;a href="mailto:mail@marcelpetrick.it"&gt;mail@marcelpetrick.it&lt;/a&gt;</source>
        <translation>Автор: Marcel Petrick &lt;a href="mailto:mail@marcelpetrick.it"&gt;mail@marcelpetrick.it&lt;/a&gt;</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="758" />
        <source>License: GNU GPLv3 or later.</source>
        <translation>Ліцензія: GNU GPLv3 або новіша.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="759" />
        <source>This application fetches a user's public loved tracks from Last.fm, keeps local metadata, resolves playable sources through yt-dlp, downloads MP3 files, and plays them locally.</source>
        <translation>Ця програма отримує публічні улюблені треки користувача з Last.fm, зберігає локальні метадані, знаходить джерела для відтворення через yt-dlp, завантажує MP3-файли й відтворює їх локально.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="764" />
        <source>It is intended as a practical Linux desktop helper for rebuilding a personal loved-track collection without manually searching every song.</source>
        <translation>Вона задумана як практичний помічник для робочого столу Linux, щоб відновити особисту колекцію улюблених треків без ручного пошуку кожної пісні.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="768" />
        <source>Optional Last.fm scrobbling can connect the local playback workflow back to the user's Last.fm account.</source>
        <translation>Необов'язковий скроблінг Last.fm може пов'язати локальне відтворення з обліковим записом користувача Last.fm.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="956" />
        <location filename="../ui/main_window.py" line="778" />
        <source>Open Source Licenses</source>
        <translation>Ліцензії відкритого коду</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="784" />
        <source>myLastFmPlayer is GPLv3-or-later software and uses these open-source libraries and external tools:</source>
        <translation>myLastFmPlayer є програмою за ліцензією GPLv3 або новішою та використовує ці бібліотеки відкритого коду й зовнішні інструменти:</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="848" />
        <location filename="../ui/main_window.py" line="790" />
        <source>Python Software Foundation License; runtime for the application.</source>
        <translation>Python Software Foundation License; середовище виконання програми.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="850" />
        <location filename="../ui/main_window.py" line="794" />
        <source>GNU GPL v3; Python bindings for the Qt desktop interface.</source>
        <translation>GNU GPL v3; прив'язки Python для настільного інтерфейсу Qt.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="851" />
        <location filename="../ui/main_window.py" line="798" />
        <source>GNU LGPL v3 / GPL v3; cross-platform UI toolkit.</source>
        <translation>GNU LGPL v3 / GPL v3; кросплатформний інструментарій інтерфейсу.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="853" />
        <location filename="../ui/main_window.py" line="802" />
        <source>Apache License 2.0; HTTP client for Last.fm API calls.</source>
        <translation>Apache License 2.0; HTTP-клієнт для викликів API Last.fm.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="854" />
        <location filename="../ui/main_window.py" line="806" />
        <source>Apache License 2.0; Last.fm scrobbling integration.</source>
        <translation>Apache License 2.0; інтеграція скроблінгу Last.fm.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="855" />
        <location filename="../ui/main_window.py" line="810" />
        <source>Unlicense; media lookup and download helper.</source>
        <translation>Unlicense; допоміжний інструмент для пошуку й завантаження медіа.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="857" />
        <location filename="../ui/main_window.py" line="814" />
        <source>LGPL/GPL family licenses depending on the installed build; audio conversion backend.</source>
        <translation>Родина ліцензій LGPL/GPL залежно від установленої збірки; бекенд перетворення аудіо.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="819" />
        <source>Development tools include {tools} under their respective open-source licenses.</source>
        <translation>Інструменти розробки включають {tools} за відповідними ліцензіями відкритого коду.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="835" />
        <source>This summary is informational; the complete license texts are provided by the installed projects and system packages.</source>
        <translation>Цей підсумок є інформаційним; повні тексти ліцензій надаються встановленими проєктами та системними пакетами.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="952" />
        <source>Fetch loved tracks</source>
        <translation>Отримати улюблені треки</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="953" />
        <source>Preferences</source>
        <translation>Налаштування</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="954" />
        <source>Open data folder in file manager</source>
        <translation>Відкрити теку даних у файловому менеджері</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="957" />
        <source>Quit</source>
        <translation>Вийти</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="958" />
        <source>Main</source>
        <translation>Головна</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="959" />
        <source>Theme</source>
        <translation>Тема</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="960" />
        <source>Light</source>
        <translation>Світла</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="961" />
        <source>Dark</source>
        <translation>Темна</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="962" />
        <source>Lilac</source>
        <translation>Бузкова</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="963" />
        <source>Mint</source>
        <translation>М'ятна</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="964" />
        <source>Language</source>
        <translation>Мова</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="965" />
        <source>Help</source>
        <translation>Довідка</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="966" />
        <source>Last.fm username</source>
        <translation>Ім'я користувача Last.fm</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="967" />
        <source>Enter username</source>
        <translation>Введіть ім'я користувача</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="968" />
        <source>Fetch</source>
        <translation>Отримати</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="969" />
        <source>Filter</source>
        <translation>Фільтр</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="970" />
        <source>Artist or track title</source>
        <translation>Виконавець або назва треку</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="971" />
        <source>Reset</source>
        <translation>Скинути</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="972" />
        <source>Playback</source>
        <translation>Відтворення</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="975" />
        <source>Play</source>
        <translation>Відтворити</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="978" />
        <source>Next</source>
        <translation>Далі</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="979" />
        <source>Randomize</source>
        <translation>У випадковому порядку</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="980" />
        <source>Artist</source>
        <translation>Виконавець</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="981" />
        <source>Open artist page on Last.fm</source>
        <translation>Відкрити сторінку виконавця на Last.fm</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="982" />
        <source>Playback position</source>
        <translation>Позиція відтворення</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="983" />
        <source>Downloads</source>
        <translation>Завантаження</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="987" />
        <source>Clear log</source>
        <translation>Очистити журнал</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="988" />
        <source>Clear status updates and errors</source>
        <translation>Очистити оновлення статусу та помилки</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="990" />
        <source>Status updates and errors will appear here.</source>
        <translation>Тут відображатимуться оновлення статусу та помилки.</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="997" />
        <source>Dependencies: yt-dlp, ffmpeg, and ffprobe not checked yet</source>
        <translation>Залежності: yt-dlp, ffmpeg і ffprobe ще не перевірено</translation>
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
        <location filename="../ui/preferences_dialog.py" line="175" />
        <location filename="../ui/preferences_dialog.py" line="135" />
        <source>None (disabled)</source>
        <translation>Немає (вимкнено)</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="155" />
        <source>Preferences</source>
        <translation>Налаштування</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="156" />
        <source>Last.fm Authentication</source>
        <translation>Автентифікація Last.fm</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="157" />
        <source>Authenticate with Last.fm</source>
        <translation>Увійти через Last.fm</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="158" />
        <source>I've authorized</source>
        <translation>Я авторизувався</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="159" />
        <source>Disconnect</source>
        <translation>Від'єднати</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="160" />
        <source>Scrobbling</source>
        <translation>Скроблінг</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="161" />
        <source>Enable scrobbling</source>
        <translation>Увімкнути скроблінг</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="163" />
        <source>Submits to Last.fm after 33% of each track has been played.</source>
        <translation>Надсилати на Last.fm після відтворення 33% кожного треку.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="165" />
        <source>YouTube Downloads</source>
        <translation>Завантаження YouTube</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="166" />
        <source>Browser cookies:</source>
        <translation>Cookie браузера:</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="167" />
        <source>Parallel downloads:</source>
        <translation>Паралельні завантаження:</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="169" />
        <source>Select the browser whose YouTube login cookies yt-dlp should use. Required for age-restricted videos. You must be signed into YouTube in the selected browser. Parallel download changes apply to new work.</source>
        <translation>Виберіть браузер, cookie входу YouTube з якого має використовувати yt-dlp. Це потрібно для відео з віковими обмеженнями. У вибраному браузері потрібно ввійти в YouTube. Зміни паралельних завантажень застосовуються до нових завдань.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="176" />
        <source>Privacy</source>
        <translation>Конфіденційність</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="177" />
        <source>Keep cached data after quitting</source>
        <translation>Зберігати кешовані дані після закриття</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="183" />
        <source>⚠ API credentials not configured.
Set LASTFM_API_KEY and LASTFM_API_SECRET environment variables.</source>
        <translation>⚠ Облікові дані API не налаштовано.
Задайте змінні середовища LASTFM_API_KEY і LASTFM_API_SECRET.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="202" />
        <source>🟢 Connected as {username}</source>
        <translation>🟢 Підключено як {username}</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="211" />
        <source>🔵 Browser opened — authorize the app, then click «I've authorized».</source>
        <translation>🔵 Браузер відкрито — авторизуйте застосунок, а потім натисніть «Я авторизувався».</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="217" />
        <source>🔴 Not connected</source>
        <translation>🔴 Не підключено</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="240" />
        <source>⚠ Could not start authentication. Check API credentials.</source>
        <translation>⚠ Не вдалося почати автентифікацію. Перевірте облікові дані API.</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="251" />
        <source>⚠ Authorization not confirmed yet. Authorize in the browser, then try again.</source>
        <translation>⚠ Авторизацію ще не підтверджено. Авторизуйтеся в браузері, а потім спробуйте ще раз.</translation>
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
        <location filename="../ui/track_table_model.py" line="195" />
        <source>Example Artist</source>
        <translation>Приклад виконавця</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="196" />
        <source>Example Track</source>
        <translation>Приклад треку</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="200" />
        <source>Another Artist</source>
        <translation>Інший виконавець</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="201" />
        <source>Waiting for implementation</source>
        <translation>Очікування реалізації</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="210" />
        <source>Fetched</source>
        <translation>Отримано</translation>
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
        <location filename="../youtube.py" line="91" />
        <source>Searching {done}/{total}: {artist} - {title}</source>
        <translation>Пошук {done}/{total}: {artist} - {title}</translation>
    </message>
    <message>
        <location filename="../youtube.py" line="236" />
        <source>Resolved {done}/{total}: {artist} - {title}</source>
        <translation>Знайдено {done}/{total}: {artist} - {title}</translation>
    </message>
    <message>
        <location filename="../youtube.py" line="244" />
        <source>No YouTube result {done}/{total}: {artist} - {title}</source>
        <translation>Немає результату YouTube {done}/{total}: {artist} - {title}</translation>
    </message>
</context></TS>

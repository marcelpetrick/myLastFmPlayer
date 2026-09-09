<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>ApplicationController</name>
    <message>
        <location filename="../controller.py" line="227" />
        <source>Re-checking {missing} not-found and {failed} failed tracks from the last run.</source>
        <translation>正在重新检查上次运行中 {missing} 首未找到和 {failed} 首失败的曲目。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="302" />
        <source>Stopping background work for {username}; completed items remain saved.</source>
        <translation>正在停止 {username} 的后台任务；已完成的项目仍会保留。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="699" />
        <location filename="../controller.py" line="355" />
        <source>Loaded {count} cached tracks for {username}; skipped Last.fm fetch.</source>
        <translation>已为 {username} 加载 {count} 首本地曲目；已跳过 Last.fm 获取。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="378" />
        <source>Dependency check finished: {message}</source>
        <translation>依赖项检查完成：{message}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="395" />
        <source>Could not open data folder: {error}</source>
        <translation>无法打开数据文件夹：{error}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="405" />
        <source>Opened data folder: {path}</source>
        <translation>已打开数据文件夹：{path}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="414" />
        <source>Could not open data folder: {path}</source>
        <translation>无法打开数据文件夹：{path}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="426" />
        <source>Could not open artist page: {url}</source>
        <translation>无法打开艺术家页面：{url}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="437" />
        <source>Last.fm scrobbling is disabled because {api_key_env}/{api_secret_env} are not configured and no bundled credentials are available.</source>
        <translation>Last.fm 播放记录同步已禁用，因为未配置 {api_key_env}/{api_secret_env}，且没有可用的内置凭据。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="452" />
        <source>Loaded Last.fm scrobbling settings; stored session key is {state}.</source>
        <translation>已加载 Last.fm 播放记录同步设置；已保存的会话密钥状态为 {state}。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="456" />
        <source>present</source>
        <translation>存在</translation>
    </message>
    <message>
        <location filename="../controller.py" line="458" />
        <source>missing</source>
        <translation>缺失</translation>
    </message>
    <message>
        <location filename="../controller.py" line="479" />
        <source>Connected Last.fm scrobbling as {username}.</source>
        <translation>已以 {username} 身份连接 Last.fm 播放记录同步。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="487" />
        <source>Stored Last.fm session key could not be verified; scrobbling remains disconnected.</source>
        <translation>无法验证已保存的 Last.fm 会话密钥；播放记录同步仍处于断开状态。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="501" />
        <source>Opening preferences.</source>
        <translation>正在打开偏好设置。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="515" />
        <source>Preferences closed; no Last.fm scrobbling service is active.</source>
        <translation>偏好设置已关闭；没有活动的 Last.fm 播放记录同步服务。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="524" />
        <source>Saved Last.fm scrobbling preferences for {username}.</source>
        <translation>已保存 {username} 的 Last.fm 播放记录同步偏好设置。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="528" />
        <source>no user</source>
        <translation>无用户</translation>
    </message>
    <message>
        <location filename="../controller.py" line="539" />
        <source>Enter a Last.fm username before fetching tracks.</source>
        <translation>获取曲目前请输入 Last.fm 用户名。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="549" />
        <source>Background work is already running for {username}.</source>
        <translation>{username} 的后台任务已在运行。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="560" />
        <source>Found {count} cached tracks for {username}; checking Last.fm before using them.</source>
        <translation>找到 {username} 的 {count} 首本地曲目；使用前正在检查 Last.fm。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="732" />
        <location filename="../controller.py" line="570" />
        <source>Starting fetch</source>
        <translation>开始获取</translation>
    </message>
    <message>
        <location filename="../controller.py" line="639" />
        <location filename="../controller.py" line="604" />
        <source>Loaded cached tracks</source>
        <translation>已加载本地曲目</translation>
    </message>
    <message>
        <location filename="../controller.py" line="626" />
        <source>Could not verify Last.fm loved-track count for {username}; using {count} cached tracks: {error}</source>
        <translation>无法验证 {username} 的 Last.fm 喜爱曲目数量；将使用 {count} 首本地曲目：{error}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="649" />
        <source>Could not reach Last.fm for {username}: {error}</source>
        <translation>无法为 {username} 访问 Last.fm：{error}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="662" />
        <source>Could not read Last.fm loved-track count for {username}; fetching fresh data instead of trusting {count} cached tracks.</source>
        <translation>无法读取 {username} 的 Last.fm 喜爱曲目数量；将重新获取数据，而不使用 {count} 首本地曲目。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="673" />
        <source>Last.fm reports {online_count} loved tracks for {username}; cached track count matches.</source>
        <translation>Last.fm 显示 {username} 有 {online_count} 首喜爱曲目；本地曲目数量匹配。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="683" />
        <source>Last.fm reports {online_count} loved tracks for {username}, but the cache has {cached_count}; fetching fresh data.</source>
        <translation>Last.fm 显示 {username} 有 {online_count} 首喜爱曲目，但本地有 {cached_count} 首；正在重新获取数据。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="715" />
        <source>Starting fresh Last.fm fetch for {username}; {count} tracks expected.</source>
        <translation>开始为 {username} 重新从 Last.fm 获取；预计 {count} 首曲目。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="724" />
        <source>Starting fresh Last.fm fetch for {username}.</source>
        <translation>开始为 {username} 重新从 Last.fm 获取。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="747" />
        <source>Fetch resumed.</source>
        <translation>获取已恢复。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="752" />
        <source>Fetch paused.</source>
        <translation>获取已暂停。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="770" />
        <location filename="../controller.py" line="763" />
        <source>Stopping fetch.</source>
        <translation>停止获取。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="784" />
        <source>Enter a Last.fm username before resolving tracks.</source>
        <translation>解析曲目前请输入 Last.fm 用户名。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="793" />
        <source>Starting YouTube lookup for {username}; priority={priority}, limit={limit}.</source>
        <translation>开始为 {username} 查找 YouTube 来源；优先级={priority}，限制={limit}。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="853" />
        <location filename="../controller.py" line="797" />
        <source>none</source>
        <translation>无</translation>
    </message>
    <message>
        <location filename="../controller.py" line="857" />
        <location filename="../controller.py" line="801" />
        <source>all</source>
        <translation>全部</translation>
    </message>
    <message>
        <location filename="../controller.py" line="808" />
        <source>Starting YouTube lookup</source>
        <translation>开始查找 YouTube 来源</translation>
    </message>
    <message>
        <location filename="../controller.py" line="833" />
        <source>Enter a Last.fm username before downloading tracks.</source>
        <translation>下载曲目前请输入 Last.fm 用户名。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="847" />
        <source>Starting downloads for {username}; concurrency={concurrency}, priority={priority}, limit={limit}.</source>
        <translation>开始为 {username} 下载；并发数={concurrency}，优先级={priority}，限制={limit}。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="865" />
        <source>Starting downloads</source>
        <translation>开始下载</translation>
    </message>
    <message>
        <location filename="../controller.py" line="891" />
        <source>Select a downloaded track before playing.</source>
        <translation>播放前选择下载的曲目。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="908" />
        <source>Playback resumed.</source>
        <translation>播放已恢复。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="916" />
        <source>Playback paused.</source>
        <translation>播放已暂停。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="960" />
        <location filename="../controller.py" line="925" />
        <source>No track is currently playing.</source>
        <translation>当前没有正在播放的曲目。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="936" />
        <source>Playback stopped.</source>
        <translation>播放已停止。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="981" />
        <source>Seeked playback to {seconds} seconds.</source>
        <translation>已将播放位置跳转到 {seconds} 秒。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1159" />
        <source>Fetch for {username} returned invalid track data.</source>
        <translation>为 {username} 获取时返回了无效曲目数据。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1169" />
        <source>Fetched and stored {count} tracks for {username}.</source>
        <translation>已获取并存储 {username} 的 {count} 首曲目。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1193" />
        <source>Stopped fetch for {username} returned invalid data.</source>
        <translation>停止为 {username} 获取后返回了无效数据。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1203" />
        <source>Stopped fetch for {username} after {count} tracks.</source>
        <translation>为 {username} 获取到 {count} 首曲目后已停止。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1216" />
        <source>Fetch for {username} returned invalid partial data.</source>
        <translation>为 {username} 获取时返回了无效的部分数据。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1228" />
        <source>Fetch progress for {username}: {count} tracks are visible now.</source>
        <translation>{username} 的获取进度：当前已显示 {count} 首曲目。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1236" />
        <source>Fetched {count} tracks for {username}</source>
        <translation>已获取 {username} 的 {count} 首曲目</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1251" />
        <source>Workflow for {username} returned an invalid track update.</source>
        <translation>{username} 的工作流程返回了无效曲目更新。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1261" />
        <source>Track update from {username}: {artist} - {title} is now {status}.</source>
        <translation>{username} 的曲目更新：{artist} - {title} 现在状态为 {status}。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1278" />
        <source>Lookup for {username} returned invalid track data.</source>
        <translation>为 {username} 查找时返回了无效曲目数据。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1355" />
        <location filename="../controller.py" line="1293" />
        <source>YouTube work stopped; completed items remain saved.</source>
        <translation>YouTube 工作已停止；已完成的项目会保留。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1300" />
        <source>Resolved YouTube URLs for {resolved_count}/{count} tracks; {not_found_count} were not found.</source>
        <translation>已为 {resolved_count}/{count} 首曲目解析 YouTube 网址；{not_found_count} 首未找到。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1326" />
        <source>No queued tracks are ready for download.</source>
        <translation>队列中没有可下载的曲目。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1338" />
        <source>Download for {username} returned invalid track data.</source>
        <translation>为 {username} 下载时返回了无效曲目数据。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1362" />
        <source>Download run for {username} finished: {downloaded_count}/{count} tracks downloaded, {failed_count} failed.</source>
        <translation>{username} 的下载任务已完成：已下载 {downloaded_count}/{count} 首曲目，{failed_count} 首失败。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1396" />
        <source>Failed</source>
        <translation>失败</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1448" />
        <source>Updating Last.fm now-playing for {artist} - {title}.</source>
        <translation>正在向 Last.fm 更新当前播放：{artist} - {title}。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1460" />
        <source>Playing {artist} - {title}.</source>
        <translation>正在播放 {artist} - {title}。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1484" />
        <source>Last.fm returned invalid artist image data.</source>
        <translation>Last.fm 返回了无效的艺术家图片数据。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1518" />
        <source>Enter a Last.fm username before preparing playback.</source>
        <translation>准备播放前请输入 Last.fm 用户名。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1528" />
        <source>Preparing {artist} - {title} for playback.</source>
        <translation>正在准备 {artist} - {title} 以供播放。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1545" />
        <source>Starting automatic YouTube lookup for {count} fetched tracks.</source>
        <translation>开始为 {count} 首已获取曲目自动查找 YouTube 来源。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1586" />
        <source>Stopping YouTube checks and downloads; completed items remain saved.</source>
        <translation>正在停止 YouTube 检查和下载；已完成的项目会保留。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1601" />
        <source>Resuming YouTube work.</source>
        <translation>正在恢复 YouTube 工作。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1608" />
        <source>No YouTube work remains to resume.</source>
        <translation>没有可恢复的 YouTube 工作。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1620" />
        <source>Enter a Last.fm username before retrying a track.</source>
        <translation>重试曲目前请输入 Last.fm 用户名。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1651" />
        <source>Retrying YouTube check for {artist} - {title}.</source>
        <translation>正在重试 {artist} - {title} 的 YouTube 检查。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1660" />
        <source>Retrying download for {artist} - {title}.</source>
        <translation>正在重试下载 {artist} - {title}。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1673" />
        <source>Starting automatic download queue for resolved tracks.</source>
        <translation>正在为已解析的曲目启动自动下载队列。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1688" />
        <source>Starting priority download for selected track.</source>
        <translation>开始优先下载所选曲目。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1783" />
        <source>Submitting Last.fm scrobble for {artist} - {title}.</source>
        <translation>正在向 Last.fm 提交播放记录：{artist} - {title}。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1817" />
        <source>Finished playback for {artist} - {title}.</source>
        <translation>已完成播放 {artist} - {title}。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1829" />
        <source>Playback finished.</source>
        <translation>播放完毕。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1839" />
        <source>Continuing with random track: {artist} - {title}.</source>
        <translation>继续播放随机曲目：{artist} - {title}。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1850" />
        <source>Continuing with next track: {artist} - {title}.</source>
        <translation>继续播放下一首曲目：{artist} - {title}。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1870" />
        <source>All background work is finished; controls are enabled again.</source>
        <translation>全部后台任务已完成；控件已重新启用。</translation>
    </message>
    <message>
        <source>Enter a Last.fm username before retrying a download.</source>
        <translation type="vanished">重试下载前请输入 Last.fm 用户名。</translation>
    </message>
    <message>
        <source>No cached tracks found for {username}; fetching from Last.fm.</source>
        <translation type="vanished">未找到 {username} 的本地曲目；正在从 Last.fm 获取。</translation>
    </message>
    <message>
        <source>Downloads stopped by user.</source>
        <translation type="vanished">下载已由用户停止。</translation>
    </message>
    <message>
        <source>Could not open file cache: {error}</source>
        <translation type="vanished">无法打开文件缓存：{error}</translation>
    </message>
    <message>
        <source>Opened file cache: {path}</source>
        <translation type="vanished">打开的文件缓存：{path}</translation>
    </message>
    <message>
        <source>Could not open file cache: {path}</source>
        <translation type="vanished">无法打开文件缓存：{path}</translation>
    </message>
    <message>
        <source>Resolved YouTube URLs for {count} tracks.</source>
        <translation type="vanished">已解析 {count} 首曲目的 YouTube 网址。</translation>
    </message>
    <message>
        <source>Downloaded {count} tracks for {username}.</source>
        <translation type="vanished">已下载 {username} 的 {count} 首曲目。</translation>
    </message>
</context><context>
    <name>DependencyCheckResult</name>
    <message>
        <location filename="../dependencies.py" line="30" />
        <source>Dependencies installed: {tools}</source>
        <translation>已安装依赖项：{tools}</translation>
    </message>
    <message>
        <location filename="../dependencies.py" line="35" />
        <source>Missing dependencies: {tools}</source>
        <translation>缺少依赖项：{tools}</translation>
    </message>
</context><context>
    <name>DownloadManager</name>
    <message>
        <location filename="../download.py" line="141" />
        <source>Queued {count} downloads</source>
        <translation>已加入 {count} 个下载任务</translation>
    </message>
    <message>
        <location filename="../download.py" line="198" />
        <source>Downloaded {done}/{total} tracks</source>
        <translation>已下载 {done}/{total} 首曲目</translation>
    </message>
</context><context>
    <name>FetchLovedTracksWorker</name>
    <message>
        <location filename="../workers.py" line="121" />
        <source>Looking up Last.fm user {username}</source>
        <translation>正在查找 Last.fm 用户 {username}</translation>
    </message>
    <message>
        <location filename="../workers.py" line="137" />
        <source>Stopped fetch after {count} tracks</source>
        <translation>获取到 {count} 首曲目后已停止</translation>
    </message>
    <message>
        <location filename="../workers.py" line="147" />
        <source>Fetched {count} tracks</source>
        <translation>已获取 {count} 首曲目</translation>
    </message>
</context><context>
    <name>LastFmLovedTracksScraper</name>
    <message>
        <location filename="../lastfm.py" line="396" />
        <source>Found Last.fm user {username}</source>
        <translation>找到 Last.fm 用户 {username}</translation>
    </message>
    <message>
        <location filename="../lastfm.py" line="699" />
        <source>Fetched {count} tracks</source>
        <translation>已获取 {count} 首曲目</translation>
    </message>
    <message>
        <location filename="../lastfm.py" line="704" />
        <source>Fetched {done}/{total} tracks</source>
        <translation>已获取 {done}/{total} 首曲目</translation>
    </message>
</context><context>
    <name>LookupTracksWorker</name>
    <message>
        <location filename="../workers.py" line="233" />
        <source>Resolving YouTube URLs for {username}</source>
        <translation>正在为 {username} 解析 YouTube 网址</translation>
    </message>
    <message>
        <location filename="../workers.py" line="252" />
        <source>YouTube lookup stopped</source>
        <translation>YouTube 查找已停止</translation>
    </message>
    <message>
        <location filename="../workers.py" line="257" />
        <source>Resolved {count} tracks</source>
        <translation>已解析 {count} 首曲目</translation>
    </message>
</context><context>
    <name>MainWindow</name>
    <message>
        <location filename="../ui/main_window.py" line="1278" />
        <location filename="../ui/main_window.py" line="216" />
        <source>Ready</source>
        <translation>就绪</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="450" />
        <source>Retry</source>
        <translation>重试</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="452" />
        <source>Select a failed track to retry</source>
        <translation>选择失败的曲目进行重试</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="464" />
        <source>Retry YouTube Check</source>
        <translation>重试 YouTube 检查</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="465" />
        <source>Search YouTube again for the selected track</source>
        <translation>再次在 YouTube 上搜索所选曲目</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="468" />
        <source>Retry Download</source>
        <translation>重试下载</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="469" />
        <source>Download the selected YouTube result again</source>
        <translation>再次下载所选 YouTube 结果</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1271" />
        <location filename="../ui/main_window.py" line="616" />
        <source>Idle</source>
        <translation>空闲</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="634" />
        <source>Loaded {count} tracks</source>
        <translation>已加载 {count} 首曲目</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="649" />
        <source>Playlist: {count} titles</source>
        <translation>播放列表：{count} 首曲目</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1147" />
        <location filename="../ui/main_window.py" line="678" />
        <source>Resume</source>
        <translation>恢复</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1150" />
        <location filename="../ui/main_window.py" line="678" />
        <source>Pause</source>
        <translation>暂停</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1249" />
        <location filename="../ui/main_window.py" line="679" />
        <source>Stop</source>
        <translation>停止</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="681" />
        <source>Resume the paused Last.fm fetch</source>
        <translation>恢复暂停的 Last.fm 获取</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="683" />
        <source>Pause the active Last.fm fetch</source>
        <translation>暂停活动的 Last.fm 获取</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="684" />
        <source>Stop the active Last.fm fetch</source>
        <translation>停止活动的 Last.fm 获取</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="709" />
        <source>Stopping YouTube…</source>
        <translation>正在停止 YouTube…</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="711" />
        <source>Resume YouTube</source>
        <translation>恢复 YouTube</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="713" />
        <source>Stop YouTube</source>
        <translation>停止 YouTube</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="715" />
        <source>Stop or resume YouTube checks and downloads</source>
        <translation>停止或恢复 YouTube 检查和下载</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="718" />
        <source>Fetch</source>
        <translation>获取</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="720" />
        <source>Fetch loved tracks, then automatically check and download them from YouTube</source>
        <translation>获取喜爱曲目，然后自动从 YouTube 检查并下载</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="880" />
        <source>Updated {artist} - {title}: {status}</source>
        <translation>已更新 {artist} - {title}：{status}</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1247" />
        <location filename="../ui/main_window.py" line="897" />
        <source>Not playing</source>
        <translation>未播放</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="916" />
        <source>Artist</source>
        <translation>艺术家</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1223" />
        <location filename="../ui/main_window.py" line="991" />
        <source>About myLastFmPlayer</source>
        <translation>关于 myLastFmPlayer</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="997" />
        <source>myLastFmPlayer {version}</source>
        <translation>myLastFmPlayer {version}</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="998" />
        <source>Author: Marcel Petrick &lt;a href="mailto:mail@marcelpetrick.it"&gt;mail@marcelpetrick.it&lt;/a&gt;</source>
        <translation>作者：Marcel Petrick &lt;a href="mailto:mail@marcelpetrick.it"&gt;mail@marcelpetrick.it&lt;/a&gt;</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1002" />
        <source>License: GNU GPLv3 or later.</source>
        <translation>许可证：GNU GPLv3 或更高版本。</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1003" />
        <source>This application fetches a user's public loved tracks from Last.fm, keeps local metadata, resolves playable sources through yt-dlp, downloads MP3 files, and plays them locally.</source>
        <translation>此应用会从 Last.fm 获取用户公开标记为喜爱的曲目，保留本地元数据，通过 yt-dlp 解析可播放来源，下载 MP3 文件并在本地播放。</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1008" />
        <source>It is intended as a practical Linux desktop helper for rebuilding a personal loved-track collection without manually searching every song.</source>
        <translation>它可作为实用的 Linux 桌面助手，帮助重建个人喜爱曲目收藏，而不必手动搜索每一首歌。</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1012" />
        <source>Optional Last.fm scrobbling can connect the local playback workflow back to the user's Last.fm account.</source>
        <translation>可选的 Last.fm 播放记录同步可将本地播放流程连接回用户的 Last.fm 账户。</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1224" />
        <location filename="../ui/main_window.py" line="1022" />
        <source>Open Source Licenses</source>
        <translation>开源许可证</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1028" />
        <source>myLastFmPlayer is GPLv3-or-later software and uses these open-source libraries and external tools:</source>
        <translation>myLastFmPlayer 是 GPLv3 或更高版本许可的软件，并使用以下开源库和外部工具：</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1092" />
        <location filename="../ui/main_window.py" line="1034" />
        <source>Python Software Foundation License; runtime for the application.</source>
        <translation>Python Software Foundation License；应用的运行时。</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1093" />
        <location filename="../ui/main_window.py" line="1038" />
        <source>GNU GPL v3; Python bindings for the Qt desktop interface.</source>
        <translation>GNU GPL v3；Qt 桌面界面的 Python 绑定。</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1094" />
        <location filename="../ui/main_window.py" line="1042" />
        <source>GNU LGPL v3 / GPL v3; cross-platform UI toolkit.</source>
        <translation>GNU LGPL v3 / GPL v3；跨平台 UI 工具包。</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1095" />
        <location filename="../ui/main_window.py" line="1046" />
        <source>Apache License 2.0; HTTP client for Last.fm API calls.</source>
        <translation>Apache License 2.0；用于 Last.fm API 调用的 HTTP 客户端。</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1096" />
        <location filename="../ui/main_window.py" line="1050" />
        <source>Apache License 2.0; Last.fm scrobbling integration.</source>
        <translation>Apache License 2.0；Last.fm 播放记录同步集成。</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1097" />
        <location filename="../ui/main_window.py" line="1054" />
        <source>Unlicense; media lookup and download helper.</source>
        <translation>Unlicense；媒体查找和下载辅助工具。</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1099" />
        <location filename="../ui/main_window.py" line="1058" />
        <source>LGPL/GPL family licenses depending on the installed build; audio conversion backend.</source>
        <translation>根据已安装构建而定的 LGPL/GPL 系列许可证；音频转换后端。</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1063" />
        <source>Development tools include {tools} under their respective open-source licenses.</source>
        <translation>开发工具包括 {tools}，它们分别使用各自的开源许可证。</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1079" />
        <source>This summary is informational; the complete license texts are provided by the installed projects and system packages.</source>
        <translation>此摘要仅供参考；完整许可证文本由已安装的项目和系统软件包提供。</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1145" />
        <source>Play</source>
        <translation>播放</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1148" />
        <source>Resume playback</source>
        <translation>继续播放</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1151" />
        <source>Pause playback</source>
        <translation>暂停播放</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1220" />
        <source>Fetch loved tracks</source>
        <translation>获取喜爱曲目</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1221" />
        <source>Preferences</source>
        <translation>偏好设置</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1222" />
        <source>Open data folder in file manager</source>
        <translation>在文件管理器中打开数据文件夹</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1225" />
        <source>Quit</source>
        <translation>退出</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1226" />
        <source>Main</source>
        <translation>主界面</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1227" />
        <source>Theme</source>
        <translation>主题</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1228" />
        <source>Light</source>
        <translation>浅色</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1229" />
        <source>Dark</source>
        <translation>深色</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1230" />
        <source>Lilac</source>
        <translation>淡紫</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1231" />
        <source>Mint</source>
        <translation>薄荷绿</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1232" />
        <source>Language</source>
        <translation>语言</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1233" />
        <source>Help</source>
        <translation>帮助</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1234" />
        <source>Last.fm username</source>
        <translation>Last.fm 用户名</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1235" />
        <source>Enter username</source>
        <translation>输入用户名</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1238" />
        <source>Filter</source>
        <translation>筛选</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1239" />
        <source>Artist, title, status, or error</source>
        <translation>艺人、标题、状态或错误</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1240" />
        <source>Reset</source>
        <translation>重置</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1243" />
        <source>Enter your Last.fm username and press Fetch to load your loved tracks.</source>
        <translation>请输入您的 Last.fm 用户名并点击「获取」以加载喜爱曲目。</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1245" />
        <source>Playback</source>
        <translation>播放</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1250" />
        <source>Next</source>
        <translation>下一首</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1252" />
        <location filename="../ui/main_window.py" line="1251" />
        <source>Volume</source>
        <translation>音量</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1253" />
        <source>Mute</source>
        <translation>静音</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1254" />
        <source>Randomize</source>
        <translation>随机播放</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1256" />
        <source>Open artist page on Last.fm</source>
        <translation>在隐私窗口中打开 Last.fm 艺术家页面</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1257" />
        <source>Playback position</source>
        <translation>播放位置</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1258" />
        <source>Last.fm discovery</source>
        <translation>Last.fm 发现</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1259" />
        <source>YouTube checks</source>
        <translation>YouTube 检查</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1260" />
        <source>Downloads</source>
        <translation>下载</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1261" />
        <source>Clear log</source>
        <translation>清除日志</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1262" />
        <source>Clear status updates and errors</source>
        <translation>清除状态更新和错误</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1263" />
        <source>Status updates and errors will appear here.</source>
        <translation>状态更新和错误将显示在此处。</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="1267" />
        <source>Dependencies: yt-dlp, ffmpeg, and ffprobe not checked yet</source>
        <translation>依赖项：yt-dlp、ffmpeg 和 ffprobe 尚未检查</translation>
    </message>
    <message>
        <source>Artist or track title</source>
        <translation type="vanished">艺术家或曲名</translation>
    </message>
    <message>
        <source>Stop Downloads</source>
        <translation type="vanished">停止下载</translation>
    </message>
    <message>
        <source>Start Downloads</source>
        <translation type="vanished">开始下载</translation>
    </message>
    <message>
        <source>MIT License; legacy Last.fm HTML parser support.</source>
        <translation type="vanished">MIT License；旧版 Last.fm HTML 解析器支持。</translation>
    </message>
    <message>
        <source>Author: Marcel Petrick &lt;mail@marcelpetrick.it&gt;</source>
        <translation type="vanished">作者：Marcel Petrick &lt;mail@marcelpetrick.it&gt;</translation>
    </message>
    <message>
        <source>Python - Python Software Foundation License; runtime for the application.</source>
        <translation type="vanished">Python - Python Software Foundation License；应用的运行时。</translation>
    </message>
    <message>
        <source>PyQt6 - GNU GPL v3; Python bindings for the Qt desktop interface.</source>
        <translation type="vanished">PyQt6 - GNU GPL v3；Qt 桌面界面的 Python 绑定。</translation>
    </message>
    <message>
        <source>Qt 6 - GNU LGPL v3 / GPL v3; cross-platform UI toolkit.</source>
        <translation type="vanished">Qt 6 - GNU LGPL v3 / GPL v3；跨平台 UI 工具包。</translation>
    </message>
    <message>
        <source>requests - Apache License 2.0; HTTP client for Last.fm API calls.</source>
        <translation type="vanished">requests - Apache License 2.0；用于 Last.fm API 调用的 HTTP 客户端。</translation>
    </message>
    <message>
        <source>beautifulsoup4 - MIT License; legacy Last.fm HTML parser support.</source>
        <translation type="vanished">beautifulsoup4 - MIT License；旧版 Last.fm HTML 解析器支持。</translation>
    </message>
    <message>
        <source>pylast - Apache License 2.0; Last.fm scrobbling integration.</source>
        <translation type="vanished">pylast - Apache License 2.0；Last.fm scrobbling 集成。</translation>
    </message>
    <message>
        <source>yt-dlp - Unlicense; media lookup and download helper.</source>
        <translation type="vanished">yt-dlp - Unlicense；媒体查找和下载辅助工具。</translation>
    </message>
    <message>
        <source>FFmpeg - LGPL/GPL family licenses depending on the installed build; audio conversion backend.</source>
        <translation type="vanished">FFmpeg - 根据已安装构建而定的 LGPL/GPL 系列许可证；音频转换后端。</translation>
    </message>
    <message>
        <source>Development tools include pytest, pytest-cov, coverage.py, Ruff, Pylint, Sphinx, and build under their respective open-source licenses.</source>
        <translation type="vanished">开发工具包括 pytest、pytest-cov、coverage.py、Ruff、Pylint、Sphinx 和 build，它们分别使用各自的开源许可证。</translation>
    </message>
    <message>
        <source>Cached songs storage location</source>
        <translation type="vanished">缓存歌曲存储位置</translation>
    </message>
    <message>
        <source>Download Queued</source>
        <translation type="vanished">下载排队</translation>
    </message>
    <message>
        <source>Concurrency</source>
        <translation type="vanished">并发性</translation>
    </message>
    <message>
        <source>This control is part of the MVP shell and will be wired in later steps.</source>
        <translation type="vanished">该控件是 MVP shell 的一部分，将在后面的步骤中进行连接。</translation>
    </message>
</context><context>
    <name>PreferencesDialog</name>
    <message>
        <location filename="../ui/preferences_dialog.py" line="184" />
        <location filename="../ui/preferences_dialog.py" line="143" />
        <source>None (disabled)</source>
        <translation>无（已禁用）</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="163" />
        <source>Preferences</source>
        <translation>偏好设置</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="164" />
        <source>Last.fm Authentication</source>
        <translation>Last.fm 身份验证</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="165" />
        <source>Authenticate with Last.fm</source>
        <translation>通过 Last.fm 进行身份验证</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="166" />
        <source>I've authorized</source>
        <translation>我已授权</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="167" />
        <source>Disconnect</source>
        <translation>断开连接</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="168" />
        <source>Scrobbling</source>
        <translation>播放记录同步</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="169" />
        <source>Enable scrobbling</source>
        <translation>启用播放记录同步</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="171" />
        <source>Submits to Last.fm after 33% of each track has been played.</source>
        <translation>每首曲目播放 33% 后将播放记录提交到 Last.fm。</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="173" />
        <source>YouTube Downloads</source>
        <translation>YouTube 下载</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="174" />
        <source>Browser cookies:</source>
        <translation>浏览器 Cookie：</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="175" />
        <source>Parallel YouTube checks and downloads:</source>
        <translation>并行 YouTube 检查和下载：</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="177" />
        <source>Select the browser whose YouTube login cookies yt-dlp should use. Required for age-restricted videos. You must be signed into YouTube in the selected browser. The parallel-work limit applies to new YouTube checks and downloads.</source>
        <translation>选择 yt-dlp 应使用其 YouTube 登录 Cookie 的浏览器。播放有年龄限制的视频时必须使用此选项。您必须已在所选浏览器中登录 YouTube。并行任务限制适用于新的 YouTube 检查和下载。</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="185" />
        <source>Privacy</source>
        <translation>隐私</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="187" />
        <source>Keep saved library and Last.fm session after quitting</source>
        <translation>退出后保留已保存的曲库和 Last.fm 会话</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="190" />
        <source>When disabled, closing the app deletes saved track lists, lookup and download caches, and Last.fm authentication. Downloaded audio files remain.</source>
        <translation>禁用后，关闭应用会删除已保存的曲目列表、查找和下载缓存以及 Last.fm 身份验证信息。已下载的音频文件会保留。</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="200" />
        <source>⚠ API credentials not configured.
Set LASTFM_API_KEY and LASTFM_API_SECRET environment variables.</source>
        <translation>⚠ 未配置 API 凭据。
设置 LASTFM_API_KEY 和 LASTFM_API_SECRET 环境变量。</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="219" />
        <source>🟢 Connected as {username}</source>
        <translation>🟢 已以 {username} 身份连接</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="229" />
        <source>🔵 Browser opened — authorize the app, then click «I've authorized».</source>
        <translation>🔵 浏览器已打开 — 请授权此应用，然后点击“我已授权”。</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="236" />
        <source>🔴 Not connected</source>
        <translation>🔴 未连接</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="255" />
        <source>Starting Last.fm authentication…</source>
        <translation>正在启动 Last.fm 身份验证…</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="268" />
        <source>⚠ Could not start authentication. Check API credentials.</source>
        <translation>⚠ 无法启动身份验证。请检查 API 凭据。</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="272" />
        <source>⚠ Could not open the browser. Open this authorization link manually: {url}</source>
        <translation>⚠ 无法打开浏览器。请手动打开此授权链接：{url}</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="286" />
        <source>Confirming Last.fm authorization…</source>
        <translation>正在确认 Last.fm 授权…</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="296" />
        <source>⚠ Authorization not confirmed yet. Authorize in the browser, then try again.</source>
        <translation>⚠ 授权尚未确认。请先在浏览器中授权，然后重试。</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="334" />
        <source>⚠ Last.fm authentication failed: {error}</source>
        <translation>⚠ Last.fm 身份验证失败：{error}</translation>
    </message>
    <message>
        <source>Keep cached data after quitting</source>
        <translation type="vanished">退出后保留缓存数据</translation>
    </message>
    <message>
        <source>Parallel downloads:</source>
        <translation type="vanished">并行下载：</translation>
    </message>
    <message>
        <source>Select the browser whose YouTube login cookies yt-dlp should use. Required for age-restricted videos. You must be signed into YouTube in the selected browser. Parallel download changes apply to new work.</source>
        <translation type="vanished">选择 yt-dlp 要使用哪一浏览器中的 YouTube 登录 Cookie。年龄受限视频需要此设置。你必须已在所选浏览器中登录 YouTube。并行下载的更改会应用于新任务。</translation>
    </message>
    <message>
        <source>Submits to Last.fm after 10 % of each track has been played.</source>
        <translation type="vanished">每首曲目播放 10% 后提交至 Last.fm。</translation>
    </message>
</context><context>
    <name>TrackTableModel</name>
    <message>
        <location filename="../ui/track_table_model.py" line="94" />
        <source>Artist</source>
        <translation>艺术家</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="96" />
        <source>Title</source>
        <translation>曲名</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="98" />
        <source>Loved at</source>
        <translation>标记喜爱时间</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="100" />
        <source>Status</source>
        <translation>状态</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="102" />
        <source>File</source>
        <translation>文件</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="181" />
        <source>{status}: {error}</source>
        <translation>{status}：{error}</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="186" />
        <source>No matching YouTube result was found.</source>
        <translation>未找到匹配的 YouTube 结果。</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="207" />
        <source>Fetched</source>
        <translation>已获取</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="209" />
        <source>Queued</source>
        <translation>已排队</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="211" />
        <source>Searching</source>
        <translation>正在搜索</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="213" />
        <source>Lookup failed</source>
        <translation>查找失败</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="215" />
        <source>Downloading</source>
        <translation>正在下载</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="217" />
        <source>Downloaded</source>
        <translation>已下载</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="219" />
        <source>Failed</source>
        <translation>失败</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="221" />
        <source>Not found</source>
        <translation>未找到</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="236" />
        <source>{bitrate} kbps</source>
        <translation>{bitrate} kbps</translation>
    </message>
</context><context>
    <name>YouTubeResolver</name>
    <message>
        <location filename="../youtube.py" line="156" />
        <source>Searching {done}/{total}: {artist} - {title}</source>
        <translation>正在搜索 {done}/{total}：{artist} - {title}</translation>
    </message>
    <message>
        <location filename="../youtube.py" line="377" />
        <source>Resolved {done}/{total}: {artist} - {title}</source>
        <translation>已解析 {done}/{total}：{artist} - {title}</translation>
    </message>
    <message>
        <location filename="../youtube.py" line="385" />
        <source>No YouTube result {done}/{total}: {artist} - {title}</source>
        <translation>未找到 YouTube 结果 {done}/{total}：{artist} - {title}</translation>
    </message>
</context></TS>

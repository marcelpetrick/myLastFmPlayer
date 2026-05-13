<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>ApplicationController</name>
    <message>
        <location filename="../controller.py" line="149" />
        <source>No cached tracks found for {username}; fetching from Last.fm.</source>
        <translation>找不到 {username} 的缓存曲目； 从 Last.fm 获取。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="160" />
        <source>Found {count} cached tracks for {username}; checking Last.fm before using them.</source>
        <translation>找到 {username} 的 {count} 条缓存曲目； 在使用它们之前检查 Last.fm。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="180" />
        <source>Loaded {count} cached tracks for {username}; skipped Last.fm fetch.</source>
        <translation>已为 {username} 加载 {count} 首缓存曲目； 跳过 Last.fm 获取。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="194" />
        <source>Could not verify Last.fm loved-track count for {username}; using {count} cached tracks: {error}</source>
        <translation>无法验证 {username} 的 Last.fm 喜爱曲目计数； 使用 {count} 个缓存曲目：{error}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="207" />
        <source>Could not read Last.fm loved-track count for {username}; fetching fresh data instead of trusting {count} cached tracks.</source>
        <translation>无法读取 {username} 的 Last.fm 喜爱曲目计数； 获取新数据而不是信任 {count} 个缓存曲目。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="219" />
        <source>Last.fm reports {online_count} loved tracks for {username}; cached track count matches.</source>
        <translation>Last.fm 报告了 {online_count} 个喜欢 {username} 的曲目； 缓存的曲目计数匹配。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="230" />
        <source>Last.fm reports {online_count} loved tracks for {username}, but the cache has {cached_count}; fetching fresh data.</source>
        <translation>Last.fm 报告 {username} 有 {online_count} 个喜欢的曲目，但缓存有 {cached_count}； 获取新数据。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="255" />
        <source>Dependency check finished: {message}</source>
        <translation>依赖性检查完成：{message}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="272" />
        <source>Could not open data folder: {error}</source>
        <translation>无法打开数据文件夹：{error}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="282" />
        <source>Opened data folder: {path}</source>
        <translation>已打开数据文件夹：{path}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="291" />
        <source>Could not open data folder: {path}</source>
        <translation>无法打开数据文件夹：{path}</translation>
    </message>
    <message>
        <location filename="../controller.py" line="302" />
        <source>Last.fm scrobbling is disabled because {api_key_env}/{api_secret_env} are not configured and no bundled credentials are available.</source>
        <translation>Last.fm 记录已禁用，因为未配置 {api_key_env}/{api_secret_env} 并且没有可用的捆绑凭据。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="317" />
        <source>Loaded Last.fm scrobbling settings; stored session key is {state}.</source>
        <translation>加载 Last.fm 乱码设置； 存储的会话密钥是{state}。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="321" />
        <source>present</source>
        <translation>展示</translation>
    </message>
    <message>
        <location filename="../controller.py" line="323" />
        <source>missing</source>
        <translation>丢失的</translation>
    </message>
    <message>
        <location filename="../controller.py" line="337" />
        <source>Connected Last.fm scrobbling as {username}.</source>
        <translation>以 {username} 身份连接 Last.fm。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="345" />
        <source>Stored Last.fm session key could not be verified; scrobbling remains disconnected.</source>
        <translation>无法验证存储的 Last.fm 会话密钥； 乱写保持断开状态。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="355" />
        <source>Opening preferences.</source>
        <translation>打开首选项。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="369" />
        <source>Preferences closed; no Last.fm scrobbling service is active.</source>
        <translation>偏好设置已关闭； 没有 Last.fm 乱码服务处于活动状态。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="378" />
        <source>Saved Last.fm scrobbling preferences for {username}.</source>
        <translation>已保存 {username} 的 Last.fm 乱码首选项。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="382" />
        <source>no user</source>
        <translation>没有用户</translation>
    </message>
    <message>
        <location filename="../controller.py" line="393" />
        <source>Enter a Last.fm username before fetching tracks.</source>
        <translation>在获取曲目之前输入 Last.fm 用户名。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="404" />
        <source>Loaded cached tracks</source>
        <translation>加载缓存曲目</translation>
    </message>
    <message>
        <location filename="../controller.py" line="414" />
        <source>Starting fresh Last.fm fetch for {username}.</source>
        <translation>开始对 {username} 进行新的 Last.fm 提取。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="423" />
        <source>Starting fetch</source>
        <translation>开始获取</translation>
    </message>
    <message>
        <location filename="../controller.py" line="439" />
        <source>Fetch resumed.</source>
        <translation>恢复恢复。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="445" />
        <source>Fetch paused.</source>
        <translation>获取已暂停。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="455" />
        <source>Stopping fetch.</source>
        <translation>停止获取。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="469" />
        <source>Enter a Last.fm username before resolving tracks.</source>
        <translation>在解析曲目之前输入 Last.fm 用户名。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="479" />
        <source>Starting YouTube lookup for {username}; priority={priority}, limit={limit}.</source>
        <translation>开始在 YouTube 上查找 {username}； 优先级={priority}，限制={limit}。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="544" />
        <location filename="../controller.py" line="485" />
        <source>none</source>
        <translation>没有任何</translation>
    </message>
    <message>
        <location filename="../controller.py" line="548" />
        <location filename="../controller.py" line="489" />
        <source>all</source>
        <translation>全部</translation>
    </message>
    <message>
        <location filename="../controller.py" line="495" />
        <source>Starting YouTube lookup</source>
        <translation>开始 YouTube 查找</translation>
    </message>
    <message>
        <location filename="../controller.py" line="518" />
        <source>Enter a Last.fm username before downloading tracks.</source>
        <translation>下载曲目之前输入 Last.fm 用户名。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="537" />
        <source>Starting downloads for {username}; concurrency={concurrency}, priority={priority}, limit={limit}.</source>
        <translation>开始下载 {username}； 并发={concurrency}，优先级={priority}，限制={limit}。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="553" />
        <source>Starting downloads</source>
        <translation>开始下载</translation>
    </message>
    <message>
        <location filename="../controller.py" line="574" />
        <source>Select a downloaded track before playing.</source>
        <translation>播放前选择下载的曲目。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="590" />
        <source>Playback resumed.</source>
        <translation>播放恢复。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="599" />
        <source>Playback paused.</source>
        <translation>播放暂停。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="608" />
        <source>No track is currently playing.</source>
        <translation>当前没有播放任何曲目。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="618" />
        <source>Playback stopped.</source>
        <translation>播放停止。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="635" />
        <source>Seeked playback to {seconds} seconds.</source>
        <translation>寻求播放到 {seconds} 秒。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="690" />
        <source>Fetch for {username} returned invalid track data.</source>
        <translation>获取 {username} 返回了无效的曲目数据。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="700" />
        <source>Fetched and stored {count} tracks for {username}.</source>
        <translation>已获取并存储 {username} 的 {count} 首曲目。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="727" />
        <source>Stopped fetch for {username} returned invalid data.</source>
        <translation>停止获取 {username} 返回了无效数据。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="737" />
        <source>Stopped fetch for {username} after {count} tracks.</source>
        <translation>在 {count} 个曲目之后停止提取 {username}。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="748" />
        <source>Fetch for {username} returned invalid partial data.</source>
        <translation>获取 {username} 返回了无效的部分数据。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="759" />
        <source>Fetch progress for {username}: {count} tracks are visible now.</source>
        <translation>获取 {username} 的进度：现在可以看到 {count} 条曲目。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="767" />
        <source>Fetched {count} tracks for {username}</source>
        <translation>已获取 {username} 的 {count} 首曲目</translation>
    </message>
    <message>
        <location filename="../controller.py" line="786" />
        <source>Workflow for {username} returned an invalid track update.</source>
        <translation>{username} 的工作流程返回了无效的曲目更新。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="796" />
        <source>Track update from {username}: {artist} - {title} is now {status}.</source>
        <translation>来自 {username} 的曲目更新：{artist} - {title} 现在为 {status}。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="811" />
        <source>Lookup for {username} returned invalid track data.</source>
        <translation>查找 {username} 返回了无效的曲目数据。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="829" />
        <source>Resolved YouTube URLs for {resolved_count}/{count} tracks; {not_found_count} were not found.</source>
        <translation>已解析 {resolved_count}/{count} 首曲目的 YouTube 网址； 未找到 {not_found_count}。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="853" />
        <source>No queued tracks are ready for download.</source>
        <translation>没有排队的曲目可供下载。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="864" />
        <source>Download for {username} returned invalid track data.</source>
        <translation>{username} 的下载返回了无效的曲目数据。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="884" />
        <source>Download run for {username} finished: {downloaded_count}/{count} tracks downloaded, {failed_count} failed.</source>
        <translation>{username} 的下载运行已完成：已下载 {downloaded_count}/{count} 个曲目，{failed_count} 失败。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="912" />
        <source>Failed</source>
        <translation>失败的</translation>
    </message>
    <message>
        <location filename="../controller.py" line="949" />
        <source>Updating Last.fm now-playing for {artist} - {title}.</source>
        <translation>正在更新 {artist} - {title} 正在播放的 Last.fm。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="958" />
        <source>Playing {artist} - {title}.</source>
        <translation>正在播放{artist} - {title}。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="977" />
        <source>Enter a Last.fm username before preparing playback.</source>
        <translation>在准备播放之前输入 Last.fm 用户名。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="986" />
        <source>Preparing {artist} - {title} for playback.</source>
        <translation>正在准备播放 {artist} - {title}。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1003" />
        <source>Starting automatic YouTube lookup for {count} fetched tracks.</source>
        <translation>开始自动 YouTube 查找 {count} 个提取的曲目。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1019" />
        <source>Downloads stopped by user.</source>
        <translation>下载已由用户停止。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1028" />
        <source>Enter a Last.fm username before retrying a download.</source>
        <translation>重试下载前请输入 Last.fm 用户名。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1046" />
        <source>Retrying download for {artist} - {title}.</source>
        <translation>正在重试下载 {artist} - {title}。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1059" />
        <source>Starting automatic download queue for resolved tracks.</source>
        <translation>启动已解析曲目的自动下载队列。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1067" />
        <source>Starting priority download for selected track.</source>
        <translation>开始优先下载所选曲目。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1141" />
        <source>Submitting Last.fm scrobble for {artist} - {title}.</source>
        <translation>正在提交 {artist} - {title} 的 Last.fm scrobble。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1170" />
        <source>Finished playback for {artist} - {title}.</source>
        <translation>已完成播放{artist} - {title}。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1180" />
        <source>Playback finished.</source>
        <translation>播放完毕。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1187" />
        <source>Continuing with next track: {artist} - {title}.</source>
        <translation>继续下一首曲目：{artist} - {title}。</translation>
    </message>
    <message>
        <location filename="../controller.py" line="1202" />
        <source>All background work is finished; controls are enabled again.</source>
        <translation>全部后台工作完成； 控件再次启用。</translation>
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
        <translation>安装的依赖项：{tools}</translation>
    </message>
    <message>
        <location filename="../dependencies.py" line="35" />
        <source>Missing dependencies: {tools}</source>
        <translation>缺少依赖项：{tools}</translation>
    </message>
</context><context>
    <name>DownloadManager</name>
    <message>
        <location filename="../download.py" line="124" />
        <source>Queued {count} downloads</source>
        <translation>已排队 {count} 个下载</translation>
    </message>
    <message>
        <location filename="../download.py" line="153" />
        <source>Downloaded {done}/{total} tracks</source>
        <translation>已下载 {done}/{total} 首曲目</translation>
    </message>
</context><context>
    <name>FetchLovedTracksWorker</name>
    <message>
        <location filename="../workers.py" line="54" />
        <source>Looking up Last.fm user {username}</source>
        <translation>查找 Last.fm 用户 {username}</translation>
    </message>
    <message>
        <location filename="../workers.py" line="70" />
        <source>Stopped fetch after {count} tracks</source>
        <translation>在 {count} 个曲目后停止获取</translation>
    </message>
    <message>
        <location filename="../workers.py" line="80" />
        <source>Fetched {count} tracks</source>
        <translation>已获取 {count} 首曲目</translation>
    </message>
</context><context>
    <name>LastFmLovedTracksScraper</name>
    <message>
        <location filename="../lastfm.py" line="253" />
        <source>Found Last.fm user {username}</source>
        <translation>找到 Last.fm 用户 {username}</translation>
    </message>
    <message>
        <location filename="../lastfm.py" line="455" />
        <source>Fetched {count} tracks</source>
        <translation>已获取 {count} 首曲目</translation>
    </message>
    <message>
        <location filename="../lastfm.py" line="460" />
        <source>Fetched {done}/{total} tracks</source>
        <translation>已获取 {done}/{total} 首曲目</translation>
    </message>
</context><context>
    <name>LookupTracksWorker</name>
    <message>
        <location filename="../workers.py" line="176" />
        <source>Resolving YouTube URLs for {username}</source>
        <translation>解析 {username} 的 YouTube 网址</translation>
    </message>
    <message>
        <location filename="../workers.py" line="192" />
        <source>Resolved {count} tracks</source>
        <translation>已解决 {count} 个曲目</translation>
    </message>
</context><context>
    <name>MainWindow</name>
    <message>
        <location filename="../ui/main_window.py" line="643" />
        <location filename="../ui/main_window.py" line="77" />
        <source>Ready</source>
        <translation>准备好</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="233" />
        <source>Retry Download</source>
        <translation>重试下载</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="636" />
        <location filename="../ui/main_window.py" line="308" />
        <source>Idle</source>
        <translation>闲置的</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="332" />
        <source>Loaded {count} tracks</source>
        <translation>已加载 {count} 首曲目</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="343" />
        <source>Playlist: {count} titles</source>
        <translation>播放列表：{count} 个标题</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="364" />
        <source>Resume</source>
        <translation>恢复</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="616" />
        <location filename="../ui/main_window.py" line="364" />
        <source>Pause</source>
        <translation>暂停</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="617" />
        <location filename="../ui/main_window.py" line="365" />
        <source>Stop</source>
        <translation>停止</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="367" />
        <source>Resume the paused Last.fm fetch</source>
        <translation>恢复暂停的 Last.fm 获取</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="369" />
        <source>Pause the active Last.fm fetch</source>
        <translation>暂停活动的 Last.fm 获取</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="370" />
        <source>Stop the active Last.fm fetch</source>
        <translation>停止活动的 Last.fm 获取</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="621" />
        <location filename="../ui/main_window.py" line="380" />
        <source>Stop Downloads</source>
        <translation>停止下载</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="621" />
        <location filename="../ui/main_window.py" line="384" />
        <source>Start Downloads</source>
        <translation>开始下载</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="459" />
        <source>Updated {artist} - {title}: {status}</source>
        <translation>更新了{artist} - {title}：{status}</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="614" />
        <location filename="../ui/main_window.py" line="475" />
        <source>Not playing</source>
        <translation>未播放</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="598" />
        <source>Fetch loved tracks</source>
        <translation>获取喜爱的曲目</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="599" />
        <source>Preferences</source>
        <translation>偏好设置</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="600" />
        <source>Open data folder in file manager</source>
        <translation>在文件管理器中打开数据文件夹</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="601" />
        <source>Quit</source>
        <translation>辞职</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="602" />
        <source>Main</source>
        <translation>主要的</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="603" />
        <source>Theme</source>
        <translation>主题</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="604" />
        <source>Light</source>
        <translation>光</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="605" />
        <source>Dark</source>
        <translation>黑暗的</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="606" />
        <source>Lilac</source>
        <translation>紫丁香</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="607" />
        <source>Mint</source>
        <translation>薄荷</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="608" />
        <source>Language</source>
        <translation>语言</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="609" />
        <source>Last.fm username</source>
        <translation>Last.fm 用户名</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="610" />
        <source>Enter username</source>
        <translation>输入用户名</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="611" />
        <source>Fetch</source>
        <translation>拿来</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="612" />
        <source>Playback</source>
        <translation>回放</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="615" />
        <source>Play</source>
        <translation>玩</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="618" />
        <source>Playback position</source>
        <translation>播放位置</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="619" />
        <source>Downloads</source>
        <translation>下载</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="623" />
        <source>Clear log</source>
        <translation>清除日志</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="624" />
        <source>Clear status updates and errors</source>
        <translation>清除状态更新和错误</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="626" />
        <source>Status updates and errors will appear here.</source>
        <translation>状态更新和错误将显示在此处。</translation>
    </message>
    <message>
        <location filename="../ui/main_window.py" line="633" />
        <source>Dependencies: yt-dlp and ffmpeg not checked yet</source>
        <translation>依赖项： yt-dlp 和 ffmpeg 尚未检查</translation>
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
        <location filename="../ui/preferences_dialog.py" line="163" />
        <location filename="../ui/preferences_dialog.py" line="123" />
        <source>None (disabled)</source>
        <translation>无（已禁用）</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="143" />
        <source>Preferences</source>
        <translation>偏好设置</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="144" />
        <source>Last.fm Authentication</source>
        <translation>Last.fm 身份验证</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="145" />
        <source>Authenticate with Last.fm</source>
        <translation>使用 Last.fm 进行身份验证</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="146" />
        <source>I've authorized</source>
        <translation>我已授权</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="147" />
        <source>Disconnect</source>
        <translation>断开</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="148" />
        <source>Scrobbling</source>
        <translation>乱写乱画</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="149" />
        <source>Enable scrobbling</source>
        <translation>启用乱码</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="151" />
        <source>Submits to Last.fm after 33% of each track has been played.</source>
        <translation>每首曲目播放 33% 后提交到 Last.fm。</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="153" />
        <source>YouTube Downloads</source>
        <translation>YouTube 下载</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="154" />
        <source>Browser cookies:</source>
        <translation>浏览器 Cookie：</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="155" />
        <source>Parallel downloads:</source>
        <translation>并行下载：</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="157" />
        <source>Select the browser whose YouTube login cookies yt-dlp should use. Required for age-restricted videos. You must be signed into YouTube in the selected browser. Parallel download changes apply to new work.</source>
        <translation>选择 yt-dlp 应使用其 YouTube 登录 Cookie 的浏览器。年龄受限视频需要此设置。你必须已在所选浏览器中登录 YouTube。并行下载的更改会应用于新的任务。</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="164" />
        <source>Privacy</source>
        <translation>隐私</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="165" />
        <source>Keep cached data after quitting</source>
        <translation>退出后保留缓存数据</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="170" />
        <source>⚠ API credentials not configured.
Set LASTFM_API_KEY and LASTFM_API_SECRET environment variables.</source>
        <translation>⚠ 未配置 API 凭据。 
设置 LASTFM_API_KEY 和 LASTFM_API_SECRET 环境变量。</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="188" />
        <source>🟢 Connected as {username}</source>
        <translation>🟢 以 {username} 连接</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="197" />
        <source>🔵 Browser opened — authorize the app, then click «I've authorized».</source>
        <translation>🔵 浏览器已打开 — 授权该应用程序，然后单击“我已授权”。</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="203" />
        <source>🔴 Not connected</source>
        <translation>🔴未连接</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="216" />
        <source>⚠ Could not start authentication. Check API credentials.</source>
        <translation>⚠ 无法启动身份验证。 检查 API 凭据。</translation>
    </message>
    <message>
        <location filename="../ui/preferences_dialog.py" line="227" />
        <source>⚠ Authorization not confirmed yet. Authorize in the browser, then try again.</source>
        <translation>⚠ 授权尚未确认。 在浏览器中授权，然后重试。</translation>
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
        <translation>标题</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="98" />
        <source>Loved at</source>
        <translation>喜欢时间</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="100" />
        <source>Status</source>
        <translation>地位</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="102" />
        <source>File</source>
        <translation>文件</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="195" />
        <source>Example Artist</source>
        <translation>示例艺术家</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="196" />
        <source>Example Track</source>
        <translation>示例曲目</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="200" />
        <source>Another Artist</source>
        <translation>另一位艺术家</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="201" />
        <source>Waiting for implementation</source>
        <translation>等待实施</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="210" />
        <source>Fetched</source>
        <translation>已获取</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="212" />
        <source>Queued</source>
        <translation>排队</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="214" />
        <source>Searching</source>
        <translation>搜寻中</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="216" />
        <source>Downloading</source>
        <translation>正在下载</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="218" />
        <source>Downloaded</source>
        <translation>已下载</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="220" />
        <source>Failed</source>
        <translation>失败的</translation>
    </message>
    <message>
        <location filename="../ui/track_table_model.py" line="222" />
        <source>Not found</source>
        <translation>未找到</translation>
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
        <translation>搜索{done}/{total}：{artist} - {title}</translation>
    </message>
    <message>
        <location filename="../youtube.py" line="233" />
        <source>Resolved {done}/{total}: {artist} - {title}</source>
        <translation>已解析{done}/{total}：{artist} - {title}</translation>
    </message>
    <message>
        <location filename="../youtube.py" line="241" />
        <source>No YouTube result {done}/{total}: {artist} - {title}</source>
        <translation>没有 YouTube 结果{done}/{total}：{artist} - {title}</translation>
    </message>
</context></TS>

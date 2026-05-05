# Scrobbling Setup Checklist

## Developer side (one-time)

1. Register the app at <https://www.last.fm/api/account/create> — fill in app
   name, description, and a callback URL (any value works for desktop).
   You receive an **API key** and **API secret**.
2. The app now bundles its Last.fm desktop application credentials:
   - API key: `d36dce7154716e08a1d2907b7badadf7`
   - Shared secret: `ed22747b03cabe49ab93f7215afc06fc`
3. `LASTFM_API_KEY` and `LASTFM_API_SECRET` remain available as overrides for
   developers, packagers, or users who want to use their own Last.fm API account.

## User side (per-device, one-time)

1. Open the app -> **Main -> Preferences**.
2. Click **Authenticate with Last.fm**. The browser opens.
3. Log in to Last.fm and click **Allow** on the authorization page.
4. Return to the app and click **I've authorized**.
5. Status shows `Connected as <username>`. The session key is saved and
   reconnects automatically on the next launch.
6. Enable the **Enable scrobbling** checkbox if it is not already checked.

After that: play tracks normally. Scrobbles are submitted silently after
10 % of each track has been played, and a now-playing notification is sent
when playback starts.

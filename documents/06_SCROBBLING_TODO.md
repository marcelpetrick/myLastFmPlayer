# Scrobbling Setup Guide

Scrobbling is implemented and optional. This checklist describes the current desktop
authentication flow rather than unfinished work.

## Developer Setup

No setup is needed: the app bundles its Last.fm desktop application credentials.

- API key: `d36dce7154716e08a1d2907b7badadf7`
- Shared secret: `ed22747b03cabe49ab93f7215afc06fc`

`LASTFM_API_KEY` and `LASTFM_API_SECRET` override them for developers, packagers, or
users who want their own Last.fm API account. To get one, register an application at
<https://www.last.fm/api/account/create> (any callback URL works for desktop use).

## User Setup

1. Open the app -> **Main -> Preferences**.
2. Click **Authenticate with Last.fm**. The browser opens.
3. Log in to Last.fm and click **Allow** on the authorization page.
4. Return to the app and click **I've authorized**.
5. Status shows `Connected as <username>`. The session key is saved and
   reconnects automatically on the next launch.
6. Enable the **Enable scrobbling** checkbox if it is not already checked.

After that, play tracks normally. Scrobbles are submitted after
33 % of each track has been played, and a now-playing notification is sent
when playback starts.

The same connection enables **Unlove on Last.fm…** in the track context menu for
your own loved-track list; see the README section "Unloving Tracks on Last.fm".

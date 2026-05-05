Developer side — one-time setup:                                                                                                         
                                         
  1. Register the app at https://www.last.fm/api/account/create — fill in app name, description, callback URL (can be anything for         
  desktop). You get an API key and API secret.                                                             
  2. Decide how to ship them. Right now the code reads them from env vars (LASTFM_API_KEY / LASTFM_API_SECRET). For a real release you have
   two options:                                                                                                                            
    - Bundle them in the package (common for desktop apps; Last.fm expects this — the key/secret are not truly secret for desktop clients).
   Add them to a _app_credentials.py or similar that falls back to env vars.                                                               
    - Keep the env-var-only approach and document that users must supply their own API app credentials (unusual UX for end users).
  3. Optionally add a UI field in the Preferences dialog for users to paste in their own key/secret if you go the "user-supplied           
  credentials" route.                                                                                                                      
                                                                                                                                           
  User side — per-device, one-time:                                                                                                        
                                                                                                           
  1. If credentials are not bundled: set LASTFM_API_KEY and LASTFM_API_SECRET before launching.                                            
  2. Open the app → Main → Preferences.
  3. Click Authenticate with Last.fm — browser opens.                                                                                      
  4. Log in to Last.fm and click Allow on the authorization page.                                          
  5. Return to the app and click I've authorized.                                                                                          
  6. Status shows 🟢 Connected as <username> — session key is saved, reconnects automatically on next launch.
  7. Enable the Enable scrobbling checkbox if it isn't already.                                                                            
                                                                                                           
  After that: just play tracks normally. Scrobbles are submitted silently after 10% of each track is played, and now-playing is sent when  
  playback starts.                                                                                         
                                                                                                                                         

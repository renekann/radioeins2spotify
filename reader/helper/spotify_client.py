import os

import spotipy
from spotipy import MemoryCacheHandler, SpotifyOAuth

from helper.secret_utils import get_secret
from helper.utils import isDevStage

spotify_refresh_token = get_secret("spotifyRefreshToken")
spotify_access_token = get_secret("spotifyAccessToken")
spotify_token_expires_at = get_secret("spotifyTokenExpiresAt")
spotify_client_id = get_secret("spotifyClientId")
spotify_client_secret = get_secret("spotifyClientSecret")
spotify_scopes = [
    "user-read-private",
    "user-read-email",
    "playlist-read-private",
    "playlist-read-collaborative",
    "user-library-modify",
    "playlist-modify-private",
    "playlist-modify-public",
]

if os.environ.get('PLAYLIST_PREFIX') is not None:
    spotify_playlist_name_prefix = os.environ['PLAYLIST_PREFIX']
else:
    spotify_playlist_name_prefix = "Test playlist"

if isDevStage():
    spotify_playlist_name_prefix = f"[{os.environ['STAGE']}] {spotify_playlist_name_prefix}"

memory_cache_handler = MemoryCacheHandler()
memory_cache_handler.save_token_to_cache(
    {
        "refresh_token": spotify_refresh_token,
        "scope": " ".join(spotify_scopes),
        "expires_at": spotify_token_expires_at,
        "access_token": spotify_access_token
    }
)

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=spotify_scopes,
                                                    client_id=spotify_client_id,
                                                    client_secret=spotify_client_secret,
                                                    redirect_uri="/",
                                                    open_browser=False,
                                                    cache_handler=memory_cache_handler))
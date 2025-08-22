import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Replace these with your actual credentials from Spotify Developer Dashboard
CLIENT_ID = "b07935f4f9c941d69f8849d55e85bf6a"
CLIENT_SECRET = "08b294fdf8f24b5486dc3b189491d0d1"
REDIRECT_URI = "http://127.0.0.1:5000/callback"

# Scope defines the permissions your app needs
SCOPE = "user-read-private user-read-email playlist-read-private"

def create_spotify_client():
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        show_dialog=True
    )
    sp = spotipy.Spotify(auth_manager=auth_manager)
    return sp

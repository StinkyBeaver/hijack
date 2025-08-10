import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def get_spotify_client():
    return spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    ))

def extract_metadata(track):
    return {
        "title": track['name'],
        "artist": track['artists'][0]['name'],
        "album": track['album']['name'],
        "artwork_url": track['album']['images'][0]['url'] if track['album']['images'] else None
    }

def get_tracks_from_spotify_url(url):
    sp = get_spotify_client()

    spotify_id = url.split("/")[-1].split("?")[0]
    url_type = url.split("/")[-2]

    tracks = []
    playlist_folder = None

    if url_type == "track":
        track = sp.track(spotify_id)
        metadata = extract_metadata(track)
        tracks.append((f"{track['name']} {track['artists'][0]['name']}", metadata))
        return tracks, "artist_album", None

    elif url_type == "album":
        album = sp.album(spotify_id)
        playlist_folder = sanitize_filename(album['name'])
        for item in sp.album_tracks(spotify_id)['items']:
            track = sp.track(item['id'])
            metadata = extract_metadata(track)
            tracks.append((f"{track['name']} {track['artists'][0]['name']}", metadata))
        return tracks, "album", playlist_folder

    elif url_type == "playlist":
        playlist = sp.playlist(spotify_id)
        playlist_folder = sanitize_filename(playlist['name'])
        offset = 0
        limit = 100
        while True:
            results = sp.playlist_tracks(spotify_id, offset=offset, limit=limit)
            items = results.get("items", [])
            if not items:
                break
            for item in items:
                track = item['track']
                if track:
                    metadata = extract_metadata(track)
                    tracks.append((f"{track['name']} {track['artists'][0]['name']}", metadata))
            offset += limit
        return tracks, "playlist", playlist_folder

    else:
        raise Exception("Unsupported Spotify URL type.")

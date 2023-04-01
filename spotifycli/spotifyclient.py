import os
import sys

import spotipy as spotipy
from spotipy import SpotifyOAuth

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

class SpotifyClient:

    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                            client_secret=CLIENT_SECRET,
                                                            redirect_uri=REDIRECT_URI,
                                                            scope=["playlist-modify-public", "playlist-read-private",
                                                                   "user-library-read"]))

    def create_playlist(self, playlist_name):
        """Create playlist on Spotify account."""
        user_id = self.sp.me()['id']
        print(f"creating playlist {playlist_name}")
        return self.sp.user_playlist_create(user_id, playlist_name)

    def remove_playlist(self, playlist):
        """Remove playlist on Spotify account."""
        print(f"removing playlist {playlist['name']}")
        return self.sp.current_user_unfollow_playlist(playlist['id'])

    def fetch_playlist(self, playlist_name):
        playlists = self.sp.current_user_playlists()
        for playlist in playlists['items']:
            if playlist['name'] == playlist_name:
                print(f"found playlist {playlist_name}")
                return playlist

    def get_or_create_playlist(self, playlist_name):
        playlist = self.fetch_playlist(playlist_name)
        if playlist is not None:
            return playlist
        else:
            return self.create_playlist(playlist_name)

    def recreate_playlist(self, playlist_name):
        playlist = self.fetch_playlist(playlist_name)
        if playlist is not None:
            self.remove_playlist(playlist)

        return self.create_playlist(playlist_name)

    def add_tracks_to_playlist(self, track_uris, playlist):
        self.sp.playlist_add_items(playlist['id'], track_uris)
        print(f"{len(track_uris)} tracks added to {playlist['name']}")

    def find_track_uris_from_stdin(self):
        """read stdin lines and find tracks"""
        track_uris = []
        for line in sys.stdin:
            line = line.strip()
            print(f'searching {line}')
            splits = line.split(':')
            track_uri = self.find_track(splits[0], splits[1])
            print(track_uri)
            if not track_uri is None:
                track_uris.append(track_uri)
        return track_uris

    def find_track(self, artist, track):
        query = f'track:{track} artist:{artist}'
        response = self.sp.search(query)
        return response['tracks']['items'][0]['uri']

    def create_from_liked(self, playlist):
        added = 0
        total = 0
        limit = 50
        offset = 0
        while added == 0 or added < total:
            track_uris = []
            response = self.sp.current_user_saved_tracks(limit=limit, offset=offset)
            total = response['total']
            for item in response['items']:
                print(item['track']['name'])
                track_uris.append(item['track']['uri'])

            self.add_tracks_to_playlist(track_uris, playlist)
            offset += limit
            added += len(track_uris)

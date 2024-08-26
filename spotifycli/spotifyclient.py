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
        chunk_size = 50
        while track_uris:
            chunk, track_uris = track_uris[:chunk_size], track_uris[chunk_size:]
            self.sp.playlist_add_items(playlist['id'], chunk)

    def remove_tracks_from_playlist(self, track_uris, playlist):
        chunk_size = 50
        while track_uris:
            chunk, track_uris = track_uris[:chunk_size], track_uris[chunk_size:]
            self.sp.playlist_remove_all_occurrences_of_items(playlist['id'], chunk)

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

    def get_liked_tracks(self):
        return self.get_tracks_from_fn(
            lambda limit, offset: self.sp.current_user_saved_tracks(limit=limit, offset=offset))

    def get_tracks_from_playlist(self, playlist):
        return self.get_tracks_from_fn(
            lambda limit, offset: self.sp.playlist_items(playlist_id=playlist['id'], limit=limit, offset=offset))

    @staticmethod
    def get_tracks_from_fn(fn):
        tracks = []
        total = -1
        limit = 50
        offset = 0
        while total == -1 or len(tracks) < total:
            response = fn(limit, offset)
            total = response['total']
            for item in response['items']:
                tracks.append(item['track'])
            offset += limit

        return tracks

    def dump_playlist_id(self, playlist_id):
        done = 0
        total = -1
        limit = 50
        offset = 0
        while total == -1 or done < total:
            response = self.sp.playlist_items(playlist_id=playlist_id, limit=limit, offset=offset)
            total = response['total']
            for item in response['items']:
                track = item['track']
                print(f"{item['added_at']}\t{track['artists'][0]['name']}: {track['name']}")
                done+=1
            offset += limit

    def sync_liked_with_playlist(self, playlist):
        playlist_tracks_by_uri = {track['uri']: track for track in self.get_tracks_from_playlist(playlist)}
        liked_tracks_by_uri = {track['uri']: track for track in self.get_liked_tracks()}

        print(f"playlist track count: {len(playlist_tracks_by_uri)}")
        print(f"liked track count: {len(liked_tracks_by_uri)}")

        playlist_track_uris = set(playlist_tracks_by_uri.keys())
        liked_track_uris = set(liked_tracks_by_uri.keys())

        uris_to_add = liked_track_uris.difference(playlist_track_uris)
        uris_to_remove = playlist_track_uris.difference(liked_track_uris)

        self.log_tracks("adding", liked_tracks_by_uri, uris_to_add)
        self.add_tracks_to_playlist(list(uris_to_add), playlist)

        self.log_tracks("removing", playlist_tracks_by_uri, uris_to_remove)
        self.remove_tracks_from_playlist(list(uris_to_remove), playlist)

    def log_tracks(self, prefix, tracks_by_uri, uris):
        print(f"{prefix} {len(uris)} tracks")
        for uri in uris:
            track = tracks_by_uri.get(uri)
            print(f"{prefix} {track['artists'][0]['name']}: {track['name']}")

    def find_playlist(self, playlist_name):
        query = f'q={playlist_name}'
        response = self.sp.search(query, type="playlist")
        print(response)
        return response

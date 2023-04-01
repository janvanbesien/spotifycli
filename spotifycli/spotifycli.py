import sys
from argparse import ArgumentParser

from spotifyclient import SpotifyClient


class SpotifyCli:

    def __init__(self):
        parser = ArgumentParser(description='spotifycli')
        parser.add_argument('command')

        parser.add_argument('--playlist', help='The name of the playlist', required=False)

        self.args = parser.parse_args(sys.argv[1:])

        command_method = "command_" + self.args.command.replace("-", "_")
        if not hasattr(self, command_method):
            print('Unrecognized command')
            parser.print_help()
            exit(1)

        self.client = SpotifyClient()

        getattr(self, command_method)()

    def command_create(self):
        """Create a playlist with tracks from stdin"""
        if self.args.playlist is None:
            raise 'Playlist name is missing'

        track_uris = self.client.find_track_uris_from_stdin()
        playlist = self.client.get_or_create_playlist(self.args.playlist)
        self.client.add_tracks_to_playlist(track_uris, playlist)

    def command_createfromliked(self):
        """Create a playlist from liked songs"""
        if self.args.playlist is None:
            raise 'Playlist name is missing'

        playlist = self.client.recreate_playlist(self.args.playlist)
        self.client.create_from_liked(playlist)


def main():
    SpotifyCli()


if __name__ == '__main__':
    SpotifyCli()

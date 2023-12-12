from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from os import getenv
from re import sub
import pandas as pd

# Load Spotify API credentials
load_dotenv()
REDIRECT_URI = getenv('REDIRECT_URI')
CLIENT_ID = getenv('CLIENT_ID')
CLIENT_SECRET = getenv('CLIENT_SECRET')


class SpotifyData(Spotify):
    def __init__(self, spotify_playlist):
        """
        Creates dictionary from Spotify playlist, which includes:
        - uri: Uniform Resource Indicator - unique ID for Spotify tracks
        - img_url: image URL of track artwork
        - preview_url: URL to a preview of the track
        - artists: string of artist names
        - tracktitle: string of track title
        :param spotify_playlist: Spotify playlist URL
        """
        super().__init__()

        self.auth_manager = SpotifyOAuth(
            scope="user-library-read",
            redirect_uri=REDIRECT_URI,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            show_dialog=True
        )

        self.playlist_id = spotify_playlist  # Get Spotify playlists
        self.playlist = self.playlist(playlist_id=self.playlist_id)
        self.playlist_total_items = self.playlist['tracks']['total']
        self.music_dict = {}

        # Spotify playlist tracks
        offset = 0
        limit = 100
        iterations = int(self.playlist_total_items / limit)
        self.playlist_music = []
        for i in range(0, iterations + 1):  # Loop through entire Spotify library in bins of 100 tracks
            subset_playlist_music = self.playlist_items(self.playlist_id,
                                                        limit=limit,
                                                        offset=offset,
                                                        fields='items,name,uri',
                                                        additional_types=['track'])
            self.playlist_music.extend(subset_playlist_music['items'])
            offset += limit

        # Create dictionary containing track names as keys and Spotify data as items
        for n in range(0, len(self.playlist_music)):
            uri = self.playlist_music[n]['track']['uri']

            track_title = self.playlist_music[n]['track']['name']
            if " - " in track_title:  # reformat remix titles etc.
                track_title = track_title.replace("- ", "(") + ")"

            n_contributing_artists = len(self.playlist_music[n]['track']['artists'])
            contributing_artists = [self.playlist_music[n]['track']['artists'][x]['name'] for x in
                                    range(0, n_contributing_artists)]
            contributing_artists_joined = ', '.join(contributing_artists)
            artists_and_title = contributing_artists_joined + " - " + track_title

            # Deal with illegal characters
            illegal_characters = '\/:*?"<>|'
            char_list = [c for c in artists_and_title if c in illegal_characters]
            char_list = list(dict.fromkeys(char_list))  # Remove duplicates from list
            for c in char_list:
                artists_and_title = artists_and_title.replace(c, '')
            artists_and_title = sub(' +', ' ', artists_and_title)  # Remove double spaces

            self.music_dict.update(
                {
                    artists_and_title:
                        {
                            "uri": uri,
                            "img_url": self.playlist_music[n]['track']['album']['images'][0]['url'],
                            "preview_url": self.playlist_music[n]['track']['preview_url'],
                            "artists": contributing_artists_joined,
                            "tracktitle": track_title,
                        }
                }
            )

    def export_playlist(self):
        pd.DataFrame(self.music_dict.keys()).to_csv('../output/Spotify_playlist.txt', sep='\t', header=False)

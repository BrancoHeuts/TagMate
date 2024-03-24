from spotify_data import SpotifyData
from os import path, makedirs
import yaml
from music_tagger import MusicTagger

ABS_PATH = path.abspath(path.dirname(__file__))

# Load config (yaml)
with open('../config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Accessing configuration settings
MUSIC_DIR = config.get('music_dir', '')
LIBRARY = config.get('library', {})
MODE = config.get('mode', 'manual')

print("Running main.py using the following configurations:"
      f"\n - {MUSIC_DIR}"
      f"\n - {LIBRARY}"
      f"\n - {MODE}")

# Set constant variables
LIBRARY_NAME = list(LIBRARY.keys())[0]
LIBRARY_URL = list(LIBRARY.values())[0]
LOCAL_DIR = f"{MUSIC_DIR}/{LIBRARY_NAME}/music_to_be_tagged"
POSSIBLE_MISMATCH_DIR = f"{MUSIC_DIR}/{LIBRARY_NAME}/possible_mismatch"
COLLECTION_DIR = f"{MUSIC_DIR}/{LIBRARY_NAME}/{LIBRARY_NAME}_collection"

# Check if directories exist, if not, create them
for directory in [LOCAL_DIR, POSSIBLE_MISMATCH_DIR, COLLECTION_DIR]:
    if not path.exists(directory):
        makedirs(directory)

# Load Spotify data
sd = SpotifyData(LIBRARY_URL)
SPOTIFY_DATA = sd.music_dict

# Export track names from Spotify playlist
sd.export_playlist()

if __name__ == '__main__':
    mt = MusicTagger(LOCAL_DIR, POSSIBLE_MISMATCH_DIR, COLLECTION_DIR, LIBRARY_NAME, MODE)
    mt.tag_music(spotify_data=SPOTIFY_DATA)
    mt.transfer_tags()
    mt.process_primary_or_substitute_tracks()
    mt.reveal_missing_local_tracks(spotify_data=SPOTIFY_DATA)
    mt.reveal_missing_spotify_tracks(spotify_data=SPOTIFY_DATA)

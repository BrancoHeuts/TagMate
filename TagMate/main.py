from spotify_data import SpotifyData
from pathlib import Path
from music_tag import load_file
from urllib.request import urlretrieve
from os import listdir, remove, path, makedirs
from genre_gui import GenreSelectionGUI
from beatport_data import BeatportScraper
import pandas as pd
from shutil import move
import yaml
import tempfile

ABS_PATH = path.abspath(path.dirname(__file__))


def load_config():
    with open('../config.yaml', 'r') as file:
        yaml_config = yaml.safe_load(file)
    return yaml_config


config = load_config()

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


class MusicTagger:
    def __init__(self, local_dir, possible_mismatch_dir, collection_dir, library_name, mode):
        self.LOCAL_DIR = local_dir
        self.POSSIBLE_MISMATCH_DIR = possible_mismatch_dir
        self.COLLECTION_DIR = collection_dir
        self.LIBRARY_NAME = library_name
        self.MODE = mode

    def _add_metadata_to_track(self, spotify_data, track_name, id3_tags):
        """
        Add metadata to an MP3 track.

        :param spotify_data: Dictionary containing Spotify music data
        :param track_name: Music file name, without extension
        :param id3_tags: id3_object for editing tags
        """
        # Extract track information from Spotify data dictionary
        track_info = spotify_data[track_name]

        # Add title & artist tags
        id3_tags['tracktitle'] = track_info['tracktitle']
        id3_tags['artist'] = track_info['artists']

        # Add filler tags
        id3_tags['genre'] = 'NA'
        id3_tags['comment'] = ''

        # Genre
        move_file = False
        if self.MODE == 'manual':
            manual_genre_selection = GenreSelectionGUI(track=track_name,
                                                       preview_url=track_info['preview_url'],
                                                       library=self.LIBRARY_NAME)
            id3_tags['genre'] = manual_genre_selection.picked_genre
            id3_tags['comment'] = f"/* {self.LIBRARY_NAME} */"
        else:
            # Automatically add Beatport data (genre & label)
            try:
                beatport_info = BeatportScraper(track_name=track_name).scrape_track_data()

                # Load string (scrape query) similarity ratios
                similarity_ratio_artists = beatport_info['similarity_ratios']['similarity_ratio_artists']
                similarity_ratio_title = beatport_info['similarity_ratios']['similarity_ratio_title']
                similarity_ratio_mix = beatport_info['similarity_ratios']['similarity_ratio_mix']

                # Load genre and label name
                id3_tags['genre'] = beatport_info['track_metadata']['query_genre_name']
                query_label_name = beatport_info['track_metadata']['query_label_name']

                # Add comments
                id3_tags['comment'] = f"/* {self.LIBRARY_NAME} / {query_label_name} */"

                # Filter query tracks based on similarity ratios (confidence threshold)
                if similarity_ratio_artists < 90 or similarity_ratio_mix < 70 or similarity_ratio_title < 70:
                    move_file = True
            except Exception as e:
                raise Exception(f"Error getting Beatport data: {e}")

        # Add artwork (only works on .mp3 and .aif files)
        artwork_url = track_info['img_url']
        save_name = "./artwork_image.jfif"
        urlretrieve(artwork_url, save_name)

        with open(save_name, 'rb') as img_in:
            id3_tags['artwork'] = img_in.read()

        art = id3_tags['artwork']
        art.first.thumbnail([64, 64])
        id3_tags.save()
        remove(save_name)

        if move_file:
            # List of file extensions to check
            extension_list = ['mp3', 'aif', 'wav']

            # Iterate over each extension and move the file if it exists
            for extension in extension_list:
                music_file = f"{self.LOCAL_DIR}/{track_name}.{extension}"
                if move_file and path.exists(music_file):
                    move(music_file, self.POSSIBLE_MISMATCH_DIR)

    def tag_music(self, spotify_data):
        """
        Add ID3 tags (Spotify and/or Beatport metadata) to the local music library files.

        IMPORTANT: Filenames need to match 100% with the corresponding track name in your Spotify playlist.
        :param spotify_data: dictionary generated by spotify_data.py
        """
        mp3_files = [file for file in listdir(self.LOCAL_DIR) if file.endswith('.mp3')]

        not_on_spotify_list = []
        for file in mp3_files:
            path_to_file = path.join(self.LOCAL_DIR, file)
            id3_object = load_file(path_to_file)  # music_tag object
            track_name = Path(path_to_file).stem

            # Add metadata to tracks
            if track_name in spotify_data:
                self._add_metadata_to_track(spotify_data=spotify_data,
                                            track_name=track_name,
                                            id3_tags=id3_object)
            else:
                # add metadata and export track names that are missing in Spotify playlist
                id3_object['artist'] = track_name.split(' - ')[0]
                id3_object['tracktitle'] = track_name.split(' - ')[1]
                id3_object['comment'] = ''

                if self.MODE == 'manual':
                    preview_and_choose = GenreSelectionGUI(track=track_name,
                                                           preview_url='None',
                                                           library=str(self.LIBRARY_NAME))
                    id3_object['genre'] = preview_and_choose.picked_genre
                    id3_object['comment'] = f"/* {str(self.LIBRARY_NAME)} */"
                else:
                    id3_object['comment'] = f"/* {str(self.LIBRARY_NAME)} / NA */"

                id3_object.save()
                print(f"Warning: '{track_name}' not found in Spotify playlist.")
                not_on_spotify_list.append(track_name)

            if len(not_on_spotify_list) > 0:
                pd.DataFrame(not_on_spotify_list).to_csv('../output/Tagged_tracks_not_in_Spotify_playlist.txt', sep='\t', header=False)

    def _extract_mp3_info(self):
        """
        Stores ID3 tags from MP3 files into dictionary.
        :return: dictionary storing MP3 track metadata
        """
        mp3_info = {}

        mp3_files = [file for file in listdir(self.LOCAL_DIR) if file.endswith('.mp3')]
        for file in mp3_files:
            path_to_file = path.join(self.LOCAL_DIR, file)
            id3_object = load_file(path_to_file)
            track_name = Path(path_to_file).stem

            mp3_info[track_name] = {
                'tracktitle': str(id3_object['tracktitle']),
                'artist': str(id3_object['artist']),
                'genre': str(id3_object['genre']),
                'comment': str(id3_object['comment']),
                'artwork': id3_object['artwork'],
            }
        return mp3_info

    def _transfer_tags_to_wav_and_aif(self, mp3_info):
        """
        Transfer tags from MP3 files to AIF and/or WAV files.

        :param mp3_info: dictionary storing MP3 track metadata
        """
        wav_and_aif_files = [file for file in listdir(self.LOCAL_DIR) if file.endswith(('.aif', '.wav'))]
        for file in wav_and_aif_files:
            path_to_file = path.join(self.LOCAL_DIR, file)
            id3_object = load_file(path_to_file)
            track_name = Path(path_to_file).stem

            if track_name in mp3_info:
                id3_object['tracktitle'] = mp3_info[track_name]['tracktitle']
                id3_object['artist'] = mp3_info[track_name]['artist']
                id3_object['genre'] = mp3_info[track_name]['genre']
                id3_object['comment'] = mp3_info[track_name]['comment']
                id3_object.save()

                # Add artwork (does not work with WAV files)
                try:
                    save_name = "./artwork_image.jfif"
                    urlretrieve(mp3_info[track_name]['img_url'], save_name)
                    with open(save_name, 'rb') as img_in:
                        id3_object['artwork'] = img_in.read()
                    art = id3_object['artwork']
                    art.first.thumbnail([64, 64])
                    id3_object.save()
                    remove("./artwork_image.jfif")
                except Exception as e:
                    print(f"\tError processing artwork for {track_name}: {e}")

    def transfer_tags(self):
        """
        The MP3 is the most common audio file available and MP3 files have a standardized and embedded way of
        storing metadata through ID3 tags. I typically store two versions of a track in my music library: MP3 and AIF.
        To circumvent redundant tagging of these versions, I first tag the MP3 files and then transfer the tags to AIF
        or WAV files. I use AIF because WAV does not allow artwork images to be stored.
        """
        mp3_info = self._extract_mp3_info()
        self._transfer_tags_to_wav_and_aif(mp3_info)

    def reveal_missing_local_tracks(self, spotify_data):
        """
        Compare music playlist from Spotify with the local directory to reveal missing tracks in the local directory.

        :param spotify_data: Dictionary of Spotify music data.
        """
        local_tracks = {Path(file).stem for file in Path(self.COLLECTION_DIR).iterdir() if file.is_file()}
        missing_tracks = [track for track in spotify_data.keys() if track not in local_tracks]

        if missing_tracks:
            pd.DataFrame(missing_tracks).to_csv('../output/Missing_tracks_in_local_collection.txt', sep='\t', header=False)

    def reveal_missing_spotify_tracks(self, spotify_data):
        """
        Compare local tracks with the music playlist from Spotify to reveal missing tracks in the Spotify dictionary.

        :param spotify_data: Dictionary of Spotify music data.
        """
        local_tracks = {Path(file).stem for file in Path(self.COLLECTION_DIR).iterdir() if file.is_file()}
        missing_tracks = [track for track in local_tracks if track not in spotify_data.keys()]

        if missing_tracks:
            pd.DataFrame(missing_tracks).to_csv('../output/Missing_tracks_in_Spotify_playlist.txt', sep='\t', header=False)

    def _tag_primary_or_substitute_tracks(self, local_directory, condition):
        """
        MP3 files use lossy compression, sacrificing some audio quality for reduced file size,
        while AIFF/WAV files are uncompressed, preserving higher sound quality but resulting in larger file sizes.
        If both MP3 and AIF/WAV versions exist, mark the AIF/WAV file as 'Primary' for higher sound quality. Otherwise,
        if only the MP3 file exists tag this MP3 file as 'Primary'.

        :param local_directory: path of directory of tracks that requires tagging
        :param condition: 'Primary' or 'Substitute' tag
        """
        files = [file for file in listdir(local_directory) if file.endswith(('.mp3', '.aif', '.wav'))]

        for file in files:
            path_to_file = path.join(local_directory, file)
            id3_object = load_file(path_to_file)

            # Extract relevant information from the comment
            comment = str(id3_object['comment'])
            comment_parts = [s.strip("/* ").strip(" */") for s in comment.split(' / ')]

            # Tag comment according to the presence of record label information
            if comment_parts[0] == self.LIBRARY_NAME and len(comment_parts) == 2:
                # Comment = /* LIBRARY_NAME / Primary or Substitute / Record label name */
                id3_object['comment'] = f"/* {comment_parts[0]} / {condition} / {comment_parts[1]} */"
            elif comment_parts[0] == self.LIBRARY_NAME and len(comment_parts) == 1:
                # Comment = /* LIBRARY_NAME / Primary or Substitute */
                id3_object['comment'] = f"/* {comment_parts[0]} / {condition} */"
            else:
                raise ValueError

            id3_object.save()

    def process_primary_or_substitute_tracks(self):
        """
        If both MP3 and AIF/WAV versions exist, mark the AIF/WAV file as 'Primary' for higher sound quality. Otherwise,
        if only the MP3 file exists tag this MP3 file as 'Primary'. When both exist, tag the lower quality MP3 file
        as 'Substitute'. This function sorts the files that need to be tagged accordingly.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            track_extensions = {}  # Dictionary to store filenames without extensions as keys and extensions as values
            files = [file for file in listdir(self.LOCAL_DIR) if file.endswith(('.mp3', '.aif', '.wav'))]

            for file in files:
                track_name = Path(file).stem
                extension = file.split('.')[-1]

                if track_name in track_extensions:
                    track_extensions[track_name].append(extension)
                else:
                    track_extensions[track_name] = [extension]

            # Move substitute files to temporary directory
            for track, extensions in track_extensions.items():
                if len(extensions) >= 2 and "mp3" in extensions:
                    file_name = f"{track}.mp3"
                    source_path = path.join(self.LOCAL_DIR, file_name)
                    destination_path = path.join(temp_dir, file_name)
                    move(source_path, destination_path)

            # Process files in the temporary directory
            self._tag_primary_or_substitute_tracks(temp_dir, "Substitute")

            # Process files in the local directory
            self._tag_primary_or_substitute_tracks(self.LOCAL_DIR, "Primary")

            # Move files back to the original directory
            for file in listdir(temp_dir):
                source_path = Path(temp_dir) / file
                destination_path = Path(self.LOCAL_DIR) / file
                move(source_path, destination_path)


if __name__ == '__main__':
    mt = MusicTagger(LOCAL_DIR, POSSIBLE_MISMATCH_DIR, COLLECTION_DIR, LIBRARY_NAME, MODE)
    mt.tag_music(spotify_data=SPOTIFY_DATA)
    mt.transfer_tags()
    mt.process_primary_or_substitute_tracks()
    mt.reveal_missing_local_tracks(spotify_data=SPOTIFY_DATA)
    mt.reveal_missing_spotify_tracks(spotify_data=SPOTIFY_DATA)

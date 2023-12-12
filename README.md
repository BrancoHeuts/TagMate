# TagMate

This project is designed to automate and standardize the metadata of my local music collection. 

The tagger operates in two distinct modes:

1. **Manual Genre Tagging:**
   - Personalize genre categorization by manually tagging tracks based on a custom list of genres.

2. **Automatic Mode with Beatport.com Integration:**
   - In automatic mode, the script scrapes Beatport.com for genre and label information, automating the genre tagging process.

## Metadata tags

The script adds the following metadata to the music files (MP3, AIF or WAV):

- **Title and Artist Information:**
  - Track titles and contributing artist names derived from Spotify's database.

- **Genre Tagging:**
  - Manual genre tagging based on a custom list or automatic tagging using Beatport.com information.

- **Comments:**
  - Additional comments, including information about the music library source and, in automatic mode, details about the record label.

- **Artwork:**
  - Album artwork from Spotify for a visually appealing and organized music library. (Does not work for WAV files)

Follow the steps below to configure and use the script effectively:

## Download and Installation

To download and install the Music-Library-Tagger package from GitHub, follow these steps:

1. Clone the repository:

    ```bash
    git clone https://github.com/branco-heuts/TagMate.git
    ```


2. Navigate to the project directory:

    ```bash
    cd TagMate
    ```

3. Install the package using pip:

    ```bash
    pip install .
    ```

   This will install all the necessary dependencies specified in the `setup.py` file.


## Spotify API Initialization

Before running the script, initialize the Spotify API by providing your credentials in the .env file:

```plaintext
REDIRECT_URI="http://example.com"
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
```
&nbsp;
#### Here is how:

1. Go to your [Spotify for Developers Dashboard](https://developer.spotify.com/dashboard/).
2. Log in to your Spotify account.
3. Create an App.
4. Go to 'Edit Settings'.
5. Add 'http://example.com' to 'Redirect URIs'.
   - Click 'Add'.
6. Copy and paste 'Client ID' and 'Client Secret' to .env.
7. Run `main.py`.
   - If Spotify authentication was successful, you should see a Spotify page asking you to agree to their terms.
8. Click 'Agree'.
9. Copy the entire URL and paste it into the prompt of your IDE.
10. Close and restart your IDE.


## Usage

- #### STEP 0: Configure YAML file
  - Open the `config.yaml` file. 
  - Fill in the required fields, including the path to your music directory, and other settings. 
  - Save the file.



- #### STEP 1: Run main.py
  - The script will export track names from the specified Spotify playlist to a text file (`Spotify_playlist.txt`).
    ```bash
    python main.py
    ```

- #### STEP 2: Rename tracks according to Spotify track names
    - Rename your music files to match the exact track names exported from Spotify. Ensure a 100% match for successful tagging.

- #### STEP 3: Remove all tags using [Mp3tag software](https://www.mp3tag.de/en/)
    - Remove all unwanted tags from your music files using 'Mp3tag' or a similar tag removal tool.

- #### STEP 4: Run main.py again
    ```bash
    python main.py
    ```

- #### STEP 5: Add tracks to main music collection directory and import in Rekordbox
  - Organize the tagged files into a collection directory.
  - Import the files into Rekordbox for integration into the DJing workflow.

## Output files

- `Tagged_tracks_not_in_Spotify_playlist.txt`:
  A text file containing a list of tracks tagged but not found in the specified Spotify playlist.

- `Missing_tracks_in_local_collection.txt`:
  A text file listing tracks present in the Spotify playlist but missing from the local collection.

- `Missing_tracks_in_Spotify_playlist.txt`:
  A text file listing tracks present in the local collection but missing from the Spotify playlist.

## Notes

- Filenames in the local collection must match 100% with the corresponding track names in the Spotify playlist.

- Artwork is added to MP3 and AIF files based on Spotify track information.

- Beatport.com is an important platform for electronic music releases. Since the majority of my music library consists of tracks released on this website, I leverage the website's genre system."

## License

This script is released under the [MIT License](LICENSE). Feel free to customize and share it according to your needs.
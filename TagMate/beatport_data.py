from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as bs
from re import sub, search
from rapidfuzz import fuzz
import json
from unidecode import unidecode


class BeatportScraper:
    def __init__(self, track_name):
        self.track_name = track_name
        self.track_artists, self.track_title_cleaned, self.track_version_type = self._extract_track_info()

    def _extract_track_version_type(self, track_name):
        """
        # Use regex to find the parenthesized pattern that contains "Mix" or "Remix" but not "feat."
        :param track_name: Full track name, including artists, title, and version type.
        :return: Track version type string
        """
        regex_pattern = r'\((?!feat\.)[^)]*(Mix|Remix)[^)]*\)'
        match = search(regex_pattern, track_name)

        if match:
            return match.group()
        else:
            return None

    def _extract_track_info(self):
        """
        Extract artists, title, and track version type (e.g. Original Mix or Remix) from track name.
        :return: cleaned up strings containing artist names, title, and version type, respectively.
        """
        track_artists = unidecode(self.track_name.split(' - ')[0].lower())
        track_title_cleaned = sub(r'\([^)]*ix[^)]*\)\s*', '', self.track_name.split(' - ')[1].lower())
        track_title_cleaned = sub(r'\([^)]*edit[^)]*\)\s*', '', track_title_cleaned)
        track_title_cleaned = track_title_cleaned.rstrip()
        track_version_type = self._extract_track_version_type(self.track_name)
        if track_version_type is not None:
            track_version_type = track_version_type.replace("(", "").replace(")", "")
        return track_artists, track_title_cleaned, track_version_type

    def _format_query_string(self, track_name):
        """
        Step1: Remove non-alphabet characters (except spaces)
        Step2: Replace one or more spaces with a single space
        Step3: Replace single spaces with '+'
        :param track_name: Full track name, including artists, title, and version type
        :return:
        """
        step1 = sub(r'[^a-zA-Z\s]', '', track_name)
        step2 = sub(r'\s+', ' ', step1)
        formatted_track_name = sub(r' ', '+', step2)
        return formatted_track_name

    def scrape_track_data(self):
        """
        Scrapes track genre and label from Beatport.com. To evaluate query string similarity ratios are used.
        :return: Nested dictionaries: track_metadata and similarity_ratios
        """
        req = Request(
            url="https://www.beatport.com/search/tracks?q=" + self._format_query_string(self.track_name),
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        webpage = urlopen(req).read()
        soup = bs(webpage, "html.parser")

        # Extract the JSON data from the script content
        script_content = soup.find('script', {'id': '__NEXT_DATA__'}).string
        start_index = script_content.find('{')
        end_index = script_content.rfind('}')
        json_data = script_content[start_index:end_index + 1]
        data_dict = json.loads(json_data)

        # Access the desired data from the dictionary
        # 150 tracks max query by default
        query_results = data_dict['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']['data'][0]
        all_artist_names = [artist['artist_name'] for artist in query_results['artists']]
        query_all_artist_names = ', '.join(all_artist_names)
        query_all_artist_names = unidecode(query_all_artist_names).lower()
        query_track_name = unidecode(query_results['track_name']).lower()
        query_mix_name = query_results['mix_name']

        if isinstance(query_results['genre'], list):
            query_genre_name = query_results['genre'][0]['genre_name']
        else:
            query_genre_name = query_results['genre']['genre_name']

        if isinstance(query_results['label'], list):
            query_label_name = query_results['label'][0]['label_name']
        else:
            query_label_name = query_results['label']['label_name']

        # String similarity ratios to predict whether the query is correct
        similarity_ratio_artists = fuzz.token_set_ratio(query_all_artist_names, self.track_artists)
        similarity_ratio_title = fuzz.ratio(query_track_name, self.track_title_cleaned)
        similarity_ratio_mix = fuzz.ratio(query_mix_name, self.track_version_type)

        if similarity_ratio_mix == 0 and (query_mix_name == 'Original Mix' or query_mix_name == 'Extended Mix'):
            similarity_ratio_mix = 100.0

        track_metadata = {
            'query_genre_name': query_genre_name,
            'query_label_name': query_label_name
        }

        similarity_ratios = {
            'similarity_ratio_artists': similarity_ratio_artists,
            'similarity_ratio_title': similarity_ratio_title,
            'similarity_ratio_mix': similarity_ratio_mix
        }

        return {
            'track_metadata': track_metadata,
            'similarity_ratios': similarity_ratios
        }

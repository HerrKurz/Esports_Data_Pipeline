"""
Enriches the data by handling additional extractions and data transformations.
"""
from config import FIELDS
import itertools
import json
import mwclient
import pandas as pd
import requests
from src.data_extractor import GetData
from src.utils import append_id, append_country_to_player, append_player_info, clean_countries_list, clean_json, \
     convert_to_json
from tqdm import tqdm



class DataEnricher:
    def __init__(self, data):
        self.lol_site = mwclient.Site('lol.fandom.com', path='/')
        self.wiki_site = mwclient.Site('en.wikipedia.org')
        self.players = self.extract_players()
        self.complementary_dict = self.transform_player_data(data, self.players)
        self.countries = self.get_player_countries(self.complementary_dict)
        self.countries_missing_coords = []
        self.coords = self.get_country_coordinates()
        self.missing_coords = self.get_missing_coordinates()
        self.final_coords = self.coords | self.missing_coords
        self.country_code = self.get_country_codes()

    def enrich_data(self, main_df: pd.DataFrame) -> list:
        """Transforms the main data frame."""
        append_player_info(main_df, self.complementary_dict)
        append_country_to_player(main_df, self.complementary_dict)
        self.append_geo_coordinates(main_df)
        self.append_country_codes(main_df)
        append_id(main_df)
        return convert_to_json(main_df)

    def extract_players(self) -> list:
        """Extracts player data from Leaguepedia API."""
        player_list = []
        for players_batch in tqdm(range(0, 17000, 500), colour='CYAN', desc=f'Extracting player data from Leaguepedia'):
            response = self.lol_site.api('cargoquery',
                                         limit='max',
                                         tables="Players",
                                         offset=players_batch,
                                         fields=FIELDS,
                                         format="json")
            try:
                parsed = json.loads(json.dumps(response["cargoquery"]))
                player_list.append(parsed)
            except KeyError as e:
                print(f"EXCEPTION: {e} with {response}.")

        flat_player_list = list(itertools.chain(*player_list))
        print(f"Total number of players downloaded {len(flat_player_list)}.")
        flat_player_list = clean_json(flat_player_list, "title")
        return flat_player_list

    def transform_player_data(self, data: GetData, player_list: list):
        """Complements enriched player info form Leaguepedia with the players list from Oracle's Elixir match data."""
        return {player["ID"]: player for player in player_list if player.get("ID") in data.player_names}

    def get_player_countries(self, enriched_dict: dict) -> list:
        """Takes a dictionary of enriched player data and returns the list
        of unique countries associated with the players."""
        player_countries_list = list(set([player_val.get("Country") for player, player_val in enriched_dict.items()]))
        return clean_countries_list(player_countries_list)

    def get_country_coordinates(self) -> dict:
        """Extracts geographic coordinates (longitude and latitude) from MediaWiki API."""
        coords = {}
        for country in tqdm(self.countries, colour='CYAN', desc=f'Extracting geographic coordinates from MediaWiki API'):
            result = self.wiki_site.api('query', prop='coordinates', titles=country)
            try:
                for page in result['query']['pages'].values():
                    if 'coordinates' in page:
                        coords[country] = [page['coordinates'][0]['lon'], page['coordinates'][0]['lat']]
                    else:
                        self.countries_missing_coords.append(page['title'])
            except KeyError as e:
                print(f"EXCEPTION:{e}, Country {country} not found")
        print(f"Countries without coords matching {self.countries_missing_coords}.")
        return coords

    def get_missing_coordinates(self) -> dict:
        """Extracts missing geographic coordinates (longitude and latitude) from REST Countries API."""
        missing_coords = {}
        for country in tqdm(self.countries_missing_coords, colour='CYAN', desc=f'Filling missing geographic coordinates from REST Countries API'):
            try:
                response = requests.get(f"https://restcountries.com/v3.1/name/{country}")
                response_json = response.json()[0]["latlng"]
                response_json.reverse()
                missing_coords[country] = [int(coordinate) for coordinate in response_json]
            except KeyError as e:
                print(f"EXCEPTION:{e}, Country {country} not found.")
        return missing_coords

    def append_geo_coordinates(self, df_match: pd.DataFrame) -> pd.DataFrame:
        """Adds a new column with geographic coordinates (longitude and latitude)."""
        df_match["Coordinates"] = df_match["Country"].map(self.final_coords)
        return df_match

    def get_country_codes(self) -> dict:
        """Extracts country codes in ISO 3166-1 numeric encoding system from REST Countries API."""
        country_code = {}
        countries_without_code = []
        for country in tqdm(self.countries, colour='CYAN', desc=f'Extracting country codes from REST Countries API'):
            try:
                response = requests.get(f"https://restcountries.com/v3.1/name/{country}")
                country_code[country] = response.json()[0]["ccn3"]
            except KeyError as e:
                countries_without_code.append(country)
                print(f"Error {e} for {countries_without_code}. Can't find matching country code.")
                continue
        return country_code

    def append_country_codes(self, df_match: pd.DataFrame) -> pd.DataFrame:
        """Adds a new column with country codes in ISO 3166-1 numeric encoding system."""
        df_match["Country_code"] = df_match["Country"].map(self.country_code)
        return df_match

"""
Enriches the data by handling additional extractions and data transformations.
"""
import itertools
import mwclient
import json
import pandas as pd
import requests
from src.data_extractor import GetData
from src.utils import convert_to_json, add_id_column, clean_countries_list, append_country_to_player, clean_json
from config import FIELDS


class DataEnricher:
    def __init__(self, data):
        self.lol_site = mwclient.Site('lol.fandom.com', path='/')
        self.wiki_site = mwclient.Site('en.wikipedia.org')
        self.players = self.extract_players()
        self.complementary_dict = self.transform_player_data(data, self.players)
        self.countries = self.add_player_countries(self.complementary_dict)
        self.countries_missing_coords = []
        self.coords = self.get_country_coordinates()
        self.missing_coords = self.fill_missing_coordinates()
        self.final_coords = self.coords | self.missing_coords
        self.country_code = self.get_country_codes()

    def enrich_data(self, main_df: pd.DataFrame) -> list:
        """Transforms the main data frame."""
        main_df["Player_info"] = main_df["playername"].map(self.complementary_dict)
        append_country_to_player(main_df, self.complementary_dict)
        self.append_coordinates_to_country(main_df)
        self.append_country_codes_to_country(main_df)
        add_id_column(main_df)
        return convert_to_json(main_df)

    def extract_players(self) -> list:
        """Extracts player data from Leaguepedia API."""
        player_list = []
        for players_batch in range(0, 17000, 500):
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
                print(f"KeyError EXCEPTION!!! {e} {response}.")

        flat_player_list = list(itertools.chain(*player_list))
        print(f"Total number of players downloaded {len(flat_player_list)}.")
        flat_player_list = clean_json(flat_player_list, "title")
        return flat_player_list

    def transform_player_data(self, data: GetData, player_list: list):
        """Complements enriched player info form Leaguepedia with the players list from Oracle's Elixir match data."""
        players_dict = {}
        for player in player_list:
            if player.get("ID") in data.player_names:
                players_dict[player.get("ID")] = player

        print(f"Number of players matched: {len(players_dict)}.")
        return players_dict

    def add_player_countries(self, enriched_dict: dict) -> list:
        """Takes a dictionary of enriched player data and returns the list
        of unique countries associated with the players."""
        list_of_player_countries = list(set([player_val.get("Country") for player, player_val in enriched_dict.items()]))
        return clean_countries_list(list_of_player_countries)

    def get_country_coordinates(self) -> dict:
        """Collects geographical coordinates - GeoPoint(longitude, latitude) for unique list
        of countries using MediaWiki API."""
        coords = {}
        for country in self.countries:
            result = self.wiki_site.api('query', prop='coordinates', titles=country)
            try:
                for page in result['query']['pages'].values():
                    if 'coordinates' in page:
                        coords[country] = [page['coordinates'][0]['lon'], page['coordinates'][0]['lat']]
                    else:
                        self.countries_missing_coords.append(page['title'])

            except KeyError as e:
                print(f"Coords not found {e}.")
                continue
        print(f"Countries without coords matching {self.countries_missing_coords}.")
        return coords

    def fill_missing_coordinates(self) -> dict:
        """Fetches missing geographical coordinates using backup Countries REST API."""
        missing_coords = {}
        for country in self.countries_missing_coords:
            try:
                response = requests.get(f"https://restcountries.com/v3.1/name/{country}")
                response_json = response.json()[0]["latlng"]
                response_json.reverse()
                missing_coords[country] = [int(coordinate) for coordinate in response_json]

            except KeyError as e:
                print(f"Error {e} for {country}.")
                continue
        return missing_coords

    def append_coordinates_to_country(self, df_match: pd.DataFrame) -> pd.DataFrame:
        """Adds new column with geographic coordinates (longitude and latitude)."""
        print(self.final_coords)
        df_match["Coordinates"] = df_match["Country"].map(self.final_coords)
        return df_match

    def get_country_codes(self) -> dict:
        """Extracts country codes in ISO 3166-1 numeric encoding system from REST Countries API."""
        country_code = {}
        countries = self.countries
        # countries = [country.replace('China', 'CN') for country in self.countries]
        countries_without_code = []
        for country in countries:
            try:
                response = requests.get(f"https://restcountries.com/v3.1/name/{country}")
                country_code[country] = response.json()[0]["ccn3"]
            except KeyError as e:
                countries_without_code.append(country)
                print(f"Error {e} for {countries_without_code}. Can't find matching country code.")
                continue
        # country_code["China"] = country_code.pop("CN")
        return country_code

    def append_country_codes_to_country(self, df_match: pd.DataFrame) -> pd.DataFrame:
        """Adds new column with country codes in ISO 3166-1 numeric encoding system."""
        print(self.country_code)
        df_match["Country_code"] = df_match["Country"].map(self.country_code)
        return df_match

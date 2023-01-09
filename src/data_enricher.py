"""
Handles additional extractions and data transformations.
"""

import mwclient
import json
import pandas as pd
import requests
from src.data_extractor import GetData
from src.utils import convert_to_json, add_id_column, clean_countries_list
from config import FIELDS, COUNTRIES_TRANSLATE_DICT


class DataEnricher:
    def __init__(self, data):
        self.lol_site = mwclient.Site('lol.fandom.com', path='/')
        self.wiki_site = mwclient.Site('en.wikipedia.org')
        self.countries = []
        self.countries_missing_coords = []
        self.complementary_dict = self.enrich_player_data(data)
        self.coords = self.get_country_coordinates()
        self.missing_coords = self.fill_missing_coordinates()
        self.final_coords = self.coords | self.missing_coords
        self.country_code = self.get_country_codes()

    def enrich_data(self, main_df: pd.DataFrame) -> list:
        """Takes main data frame and applies the transformations on the data."""
        main_df["Player_info"] = main_df["playername"].map(self.complementary_dict)
        self.append_coordinates_to_country(main_df)
        self.append_country_codes_to_country(main_df)
        add_id_column(main_df)
        return convert_to_json(main_df)

    def enrich_player_data(self, data: GetData) -> dict:
        """Extracts data about the players from Leaguepedia API."""
        player_dict = {}
        missing_players = []
        countries = []
        for count, player in enumerate(data.player_names):
            response = self.lol_site.api('cargoquery',
                limit = 'max',
                tables = "Players",
                fields = FIELDS,
                where=f'id="{player}"',
                format = "json")
            try:
                parsed = json.loads(json.dumps(response["cargoquery"]))[0]["title"]
                print(f"Getting player {player} {count + 1}/{len(data.player_names)} of players from Leaguepedia.")
                player_dict[parsed["ID"]] = parsed
                countries.append(parsed["Country"])

            except KeyError as e:
                print(f"KeyError EXCEPTION!!! {e} {response}.")
                continue
            except IndexError as e:
                print(f"Missing player {player} at Leaguepedia. With error {e}.")
                missing_players.append(player)
                continue
        print(f"{len(missing_players)} players weren't fetched from Leaguepedia, their names: {missing_players}.")

        try:
            player_country_dict = {player_name: country["Country"] for player_name, country in player_dict.items()}
            data.df_matches['Country'] = data.df_matches['playername'].map(player_country_dict)
        except KeyError as e:
            data.df_matches['Country'] = ""
            print(f"Key error {e}.")

        self.countries = clean_countries_list(countries)
        print(self.countries)

        # for k, v in COUNTRIES_TRANSLATE_DICT.items():
        #     try:
        #         result = player_dict[]
        #     except KeyError as e:
        #         print(f"{e}")
        #         continue

        return player_dict

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
                        print(coords[country])
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
                missing_coords[country] = [int(i) for i in response_json]

            except KeyError as e:
                print(f"Error {e} for {country}.")
                continue
        return missing_coords

    def append_coordinates_to_country(self, df_match: pd.DataFrame) -> pd.DataFrame:
        """Adds new column which contains longitude and latitude to main dataframe based on mapped "Country" values."""
        print(self.final_coords)
        df_match["Coordinates"] = df_match["Country"].map(self.final_coords)
        return df_match

    def get_country_codes(self) -> dict:
        """Fetches country codes in ISO 3166-1 numeric encoding system."""
        country_code = {}
        countries_without_code = []
        for country in self.countries:
            try:
                response = requests.get(f"https://restcountries.com/v3.1/name/{country}")
                country_code[country] = response.json()[0]["ccn3"]
            except KeyError as e:
                countries_without_code.append(country)
                print(f"Error {e} for {countries_without_code}. Can't find matching country code.")
                continue
        return country_code

    def append_country_codes_to_country(self, df_match: pd.DataFrame) -> pd.DataFrame:
        """Adds new column which contains country code to main dataframe based on mapped "Country" values."""
        print(self.country_code)
        df_match["Country_code"] = df_match["Country"].map(self.country_code)
        return df_match

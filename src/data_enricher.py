"""
Enriches the data by handling additional extractions and data transformations.
"""
import itertools
import json

import mwclient
import pandas as pd
import requests
from tqdm import tqdm

from config import FIELDS, TEAM_FIELDS
from src.data_extractor import GetData
from src.utils import (
    adjust_dict_values,
    append_country_to_player,
    append_id,
    append_player_info,
    append_team_info,
    clean_countries_list,
    clean_json,
    convert_to_json,
)


class DataEnricher:
    def __init__(self, data):
        self.lol_site = mwclient.Site("lol.fandom.com", path="/")
        self.wiki_site = mwclient.Site("en.wikipedia.org")
        self.players = self.extract_players()
        self.teams = self.extract_teams()
        self.complementary_dict = self.transform_player_data(data, self.players)
        self.complementary_team = self.transform_team_data(data, self.teams)
        self.countries = self.get_player_countries(self.complementary_dict)
        self.countries_missing_coords = []
        self.coords = self.get_country_coordinates()
        self.missing_coords = self.get_missing_coordinates()
        self.final_coords = self.coords | self.missing_coords
        self.country_code = self.get_country_codes()

    def enrich_data(self, main_df: pd.DataFrame) -> list:
        """Transforms the main data frame.

        Parameters:
            main_df (pd.DataFrame): The main DataFrame to be transformed.

        Returns:
            list: The transformed DataFrame converted to a list of JSON objects.
        """
        append_player_info(main_df, self.complementary_dict)
        append_team_info(main_df, self.complementary_team)
        append_country_to_player(main_df, self.complementary_dict)
        self.append_geo_coordinates(main_df)
        self.append_country_codes(main_df)
        append_id(main_df)
        return convert_to_json(main_df)

    def extract_players(self) -> list:
        """Extracts player data from Leaguepedia API endpoint.

        Returns:
            list: A list of player data.
        """
        player_list = []
        for players_batch in tqdm(
            range(0, 17000, 500),
            colour="CYAN",
            desc=f"Extracting player data from Leaguepedia",
        ):
            response = self.lol_site.api(
                "cargoquery",
                limit="max",
                tables="Players",
                offset=players_batch,
                fields=FIELDS,
                format="json",
            )
            try:
                parsed = json.loads(json.dumps(response["cargoquery"]))
                player_list.append(parsed)
            except KeyError as e:
                print(f"EXCEPTION: {e} with {response}.")

        flat_player_list = list(itertools.chain(*player_list))
        print(f"Total number of players downloaded {len(flat_player_list)}.")
        return clean_json(flat_player_list, "title")

    def extract_teams(self) -> list:
        """Extracts team data from Leaguepedia API.

        Returns:
            list: A list of team data.
        """
        team_list = []
        for team_batch in tqdm(
            range(0, 3500, 500),
            colour="CYAN",
            desc=f"Extracting team data from Leaguepedia",
        ):
            response = self.lol_site.api(
                "cargoquery",
                limit="max",
                tables="Teams",
                offset=team_batch,
                fields=TEAM_FIELDS,
                format="json",
            )
            try:
                parsed = json.loads(json.dumps(response["cargoquery"]))
                team_list.append(parsed)
            except KeyError as e:
                print(f"EXCEPTION: {e} with {response}.")

        flat_team_list = list(itertools.chain(*team_list))
        print(f"Total number of teams downloaded {len(flat_team_list)}.")
        return clean_json(flat_team_list, "title")

    def transform_player_data(self, data: GetData, player_list: list):
        """Complements enriched player data form Leaguepedia with the players list from Oracle's Elixir match data.

        Parameters:
            data (GetData): An instance of the GetData class.
            player_list (list): A list of player data.

        Returns:
            _type_: A dictionary containing the transformed player data.
        """
        return {
            player["ID"]: player
            for player in player_list
            if player.get("ID") in data.player_names
        }

    def transform_team_data(self, data: GetData, team_list: list):
        """Complements enriched team data form Leaguepedia with a team names list from Oracle's Elixir match data.

        Parameters:
            data (GetData): An instance of the GetData class.
            team_list (list): A list of team data.

        Returns:
            _type_: A dictionary containing the transformed team data.
        """
        return {
            team["OverviewPage"]: team
            for team in team_list
            if team.get("OverviewPage") in data.team_names
        }

    def get_player_countries(self, enriched_dict: dict) -> list:
        """Takes a dictionary of enriched player data and returns the list
        of unique countries associated with the players.

        Parameters:
            enriched_dict (dict): A dictionary of enriched player data.

        Returns:
            list: A list of unique countries associated with the players.
        """
        player_countries_list = list(
            set(
                [
                    player_val.get("Country")
                    for player, player_val in enriched_dict.items()
                ]
            )
        )
        return clean_countries_list(player_countries_list)

    def get_country_coordinates(self) -> dict:
        """Extracts geographic coordinates (longitude and latitude) from MediaWiki API.

        Returns:
            dict: A dictionary containing the country coordinates.
        """
        coords = {}
        for country in tqdm(
            self.countries,
            colour="CYAN",
            desc=f"Extracting geographic coordinates from MediaWiki API",
        ):
            result = self.wiki_site.api("query", prop="coordinates", titles=country)
            try:
                for page in result["query"]["pages"].values():
                    if "coordinates" in page:
                        coords[country] = [
                            page["coordinates"][0]["lon"],
                            page["coordinates"][0]["lat"],
                        ]
                    else:
                        self.countries_missing_coords.append(page["title"])
            except KeyError as e:
                print(f"EXCEPTION:{e}, Country {country} not found")
        print(f"Countries without coords matching {self.countries_missing_coords}.")
        return coords

    def get_missing_coordinates(self) -> dict:
        """Extracts missing geographic coordinates (longitude and latitude) from REST Countries API.

        Returns:
            dict: A dictionary containing the missing country coordinates.
        """
        missing_coords = {}
        for country in tqdm(
            self.countries_missing_coords,
            colour="CYAN",
            desc=f"Filling missing geographic coordinates from REST Countries API",
        ):
            try:
                response = requests.get(
                    f"https://restcountries.com/v3.1/name/{country}"
                )
                response_json = response.json()[0]["latlng"]
                response_json.reverse()
                missing_coords[country] = [
                    int(coordinate) for coordinate in response_json
                ]
            except KeyError as e:
                print(f"EXCEPTION:{e}, Country {country} not found.")
        adjust_dict_values(missing_coords)
        return missing_coords

    def append_geo_coordinates(self, df_match: pd.DataFrame) -> pd.DataFrame:
        """Adds a new column with geographic coordinates - longitude and latitude.

        Parameters:
            df_match (pd.DataFrame): The main DataFrame to be transformed.

        Returns:
            pd.DataFrame: The main DataFrame with the appended coordinates column.
        """
        df_match["Coordinates"] = df_match["Country"].map(self.final_coords)
        return df_match

    def get_country_codes(self) -> dict:
        """Extracts country codes in ISO 3166-1 numeric encoding system from REST Countries API.

        Returns:
            dict: A dictionary containing the country codes.
        """
        country_code = {}
        countries_without_code = []
        for country in tqdm(
            self.countries,
            colour="CYAN",
            desc=f"Extracting country codes from REST Countries API",
        ):
            try:
                response = requests.get(
                    f"https://restcountries.com/v3.1/name/{country}"
                )
                country_code[country] = response.json()[0]["ccn3"]
            except KeyError as e:
                countries_without_code.append(country)
                print(
                    f"Error {e} for {countries_without_code}. Can't find matching country code."
                )
                continue
        adjust_dict_values(country_code)
        return country_code

    def append_country_codes(self, df_match: pd.DataFrame) -> pd.DataFrame:
        """ "Adds a new column with country codes in ISO 3166-1 numeric encoding system.

        Parameters:
            df_match (pd.DataFrame): The main DataFrame to be transformed.

        Returns:
            pd.DataFrame: The main DataFrame with the appended country codes column.
        """
        df_match["Country_code"] = df_match["Country"].map(self.country_code)
        return df_match

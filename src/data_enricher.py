import mwclient
import json
import pandas as pd
from src.utils import convert_to_json


class DataEnricher:
    def __init__(self, list_of_players, df_matches):
        self.lol_site = mwclient.Site('lol.fandom.com', path='/')
        self.wiki_site = mwclient.Site('en.wikipedia.org')
        self.countries = []
        self.complementary_dict = self.enrich_player_data(list_of_players, df_matches)
        self.coords = self.get_country_coordinates()

    def enrich_data(self, main_df: pd.DataFrame) -> list:
        main_df["Player_info"] = main_df["playername"].map(self.complementary_dict)
        # add function backfill liquipedia api/ or scraping
        self.append_coordinates_to_country(main_df)
        # fix append coords, to fetch and return 2 things (country code + coords)
        return convert_to_json(main_df)

    def enrich_player_data(self, list_of_players: list, df_match: pd.DataFrame) -> dict:
        player_dict = {}
        missing_players = []
        for count, player in enumerate(list_of_players):
            response = self.lol_site.api('cargoquery',
                limit = 'max',
                tables = "Players",
                # add fields to config.py
                fields = "ID, OverviewPage, Player, Image, Name, NativeName, NameAlphabet, NameFull, Country, Nationality, NationalityPrimary, Age, Birthdate, ResidencyFormer, Team, Team2, CurrentTeams, TeamSystem, Team2System, Residency, Role, FavChamps, SoloqueueIds, Askfm, Discord, Facebook, Instagram, Lolpros, Reddit, Snapchat, Stream, Twitter, Vk, Website, Weibo, Youtube, TeamLast, RoleLast, IsRetired, ToWildrift, IsPersonality, IsSubstitute, IsTrainee, IsLowercase, IsAutoTeam, IsLowContent",
                where=f'id="{player}"',
                format = "json")
            try:
                parsed = json.loads(json.dumps(response["cargoquery"]))[0]["title"]
                print(f"Getting player {player} {count + 1}/{len(list_of_players)} of players from Leaguepedia.")
                player_dict[parsed["ID"]] = parsed
                self.countries.append(parsed["Country"])
            except KeyError as e:
                print(f"KeyError EXCEPTION!!! {e} {response}.")
                continue
            except IndexError:
                print(f"Missing player {player} at Leaguepedia.")
                missing_players.append(player)
                continue
        print(f"{len(missing_players)} players weren't fetched from Leaguepedia, their names: {missing_players}.")

        try:
            player_country_dict = {player_name: country["Country"] for player_name, country in player_dict.items()}
            df_match['Country'] = df_match['playername'].map(player_country_dict)
        except KeyError as e:
            df_match['Country'] = ""
            print(f"Key error {e}.")
        return player_dict

    def get_country_coordinates(self) -> dict:
        """Provides X"""
        coords = {}
        countries = set(self.countries)
        for country in countries:
            result = self.wiki_site.api('query', prop='coordinates', titles=country)
            try:
                for page in result['query']['pages'].values():
                    if 'coordinates' in page:
                        coords[country] = [page['coordinates'][0]['lon'], page['coordinates'][0]['lat']]
            except KeyError:
                continue
        print(coords) # remove the prints
        return coords

    def append_coordinates_to_country(self, df_match: pd.DataFrame) -> pd.DataFrame:
        df_match["Coordinates"] = df_match["Country"].map(self.coords)
        return df_match


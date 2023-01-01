"""

"""

import pandas as pd
from config import CSV_2014, CSV_2023

class GetData:
    """Downloads .csv file with LoL esports match data from OraclesElixir and returns it as a dataframe"""
    def __init__(self, limits: int or None = None):
        self.df_matches = self.download_csv(limits=20)
        self.player_names = self.get_player_name(self.df_matches)

    def download_csv(self, limits: int or None) -> pd.DataFrame:
        """Downloads .csv file with LoL esports match data from OraclesElixir and returns it as a dataframe"""
        try:
            url = "https://drive.google.com/uc?id=12syQsRH2QnKrQZTQQ6G5zyVeTG2pAYvu"
            df = pd.read_csv(url, low_memory=False)
            print("File successfully downloaded.")
            return df[:limits] if limits else df
        except Exception as e:
            print(f"An exception {e} has occurred. File NOT downloaded.")

    @staticmethod
    def get_player_name(df: pd.DataFrame) -> list:
        """Gets unique, non-empty player list from a dataframe"""
        df_playername = df["playername"].dropna().unique()
        player_list = list(df_playername)
        return player_list

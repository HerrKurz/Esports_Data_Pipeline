"""

"""

import pandas as pd
# import datetime


class GetData:
    """A class that extracts main data source"""
    def __init__(self, limits = None):
        # self.date_now = str(datetime.date.today()).replace("-", "")
        self.df_matches = self.download_csv(limits)
        self.player_names = self.get_player_name(self.df_matches)

    @staticmethod
    def download_csv(limits: int or None) -> pd.DataFrame:
        """Downloads .csv file with 2022 LoL esports match data from OraclesElixir and returns it as a dataframe"""
        try:
            # url = f"https://oracleselixir-downloadable-match-data.s3-us-west-2.amazonaws.com/2022_LoL_esports_match_data_from_OraclesElixir_{self.date_now}.csv"
            url = "https://drive.google.com/uc?id=1EHmptHyzY8owv0BAcNKtkQpMwfkURwRy"
            # Dodać do configa i pobierać z niego URL NP. URL_CSV
            df = pd.read_csv(url, low_memory=False)
            print("File successfully downloaded.")
            return df[:limits] if limits else df
        except Exception as e:
            print(f"An exception {e} has occurred.")

    @staticmethod
    def get_player_name(df: pd.DataFrame) -> list:
        """Gets unique, non-empty player list from a dataframe"""
        df_playername = df["playername"].dropna().unique()
        player_list = list(df_playername)
        return player_list

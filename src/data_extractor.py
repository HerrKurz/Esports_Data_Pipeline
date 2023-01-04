"""
Handles the main extraction part, enables to choose the dataset sample size for selected years.
"""
import pandas as pd
import datetime
from src.utils import convert_years_to_url, merge_csv_files


class GetData:
    def __init__(self, year: list, retries=1, limits: int or None = None):
        self.retries = retries
        self.current_year = datetime.date.today().year-1
        self.df_matches = self.download_csv(limits, year)
        self.player_names = self.get_player_name()

    def download_csv(self, limits: int or None, year: list) -> pd.DataFrame:
        """
        Downloads .csv file with LoL e-sport match data from OraclesElixir and returns it as a dataframe.
        Takes the unique list of years which are later converted to the corresponding URL.
        """
        counter = 0
        while counter < self.retries:
            try:
                url_list = convert_years_to_url(year, self.current_year)
                print(url_list)
                df = merge_csv_files(url_list)
                print(f"Dataframe consists of {df.shape[0]} rows and {df.shape[1]} columns.")
                return df[:limits] if limits else df
            except pd.errors.EmptyDataError as e:
                print(f"{e} for year {self.current_year}. Trying to fetch previous year.")
                self.current_year = self.current_year - 1
                convert_years_to_url(year, self.current_year)
                counter += 1

    def get_player_name(self) -> set:
        """Gets unique, non-empty player list from a dataframe used later to enrich the dataset."""
        df_playername = self.df_matches["playername"].dropna().unique()
        player_list = set(list(df_playername))
        return player_list

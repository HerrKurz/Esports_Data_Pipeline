"""
Handles the main extraction part, enables to choose the dataset sample size for selected years.
"""
import datetime

import pandas as pd

from src.utils import convert_years_to_url, merge_csv_files

CURRENT_YEAR = datetime.date.today().year


class GetData:
    def __init__(
        self,
        year: list = f"{CURRENT_YEAR}",
        retries: int = 1,
        limits: int or None = None,
    ):
        self.retries = retries
        self.df_matches = self.download_csv(limits, year)
        self.player_names = self.get_player_name()
        self.team_names = self.get_team_name()

    def download_csv(self, limits: int or None, year: list) -> pd.DataFrame:
        """Downloads .csv file with LoL e-sport match data from OraclesElixir and returns it as a dataframe.
        Takes the unique list of years which are later converted to the corresponding URL.

        Parameters:
            limits (intorNone): Narrows down the number of rows we want to extract from a data frame. By default, it takes None, so the entire data frame is processed instead.
            year (list): Provides the list of years from 2014 to 2023 (included). Takes a current year as a default argument.

        Returns:
            pd.DataFrame: DataFrame with downloaded match data.
        """
        counter = 0
        while counter < self.retries:
            try:
                url_list = convert_years_to_url(year, CURRENT_YEAR)
                df = merge_csv_files(url_list)
                print(
                    f"Downloaded matches data frame consists of {df.shape[0]} rows and {df.shape[1]} columns."
                )
                return df[:limits] if limits else df
            except pd.errors.EmptyDataError as e:
                print(f"{e} for year {CURRENT_YEAR}. Trying to fetch previous year.")
                convert_years_to_url(year, CURRENT_YEAR)
                counter += 1

    def get_player_name(self) -> list:
        """Gets unique, non-empty player list from a DataFrame used later to enrich the dataset.

        Returns:
            list: List of non-empty unique players from downloaded match data.
        """
        df_playername = self.df_matches["playername"].dropna().unique()
        return list(df_playername)

    def get_team_name(self) -> list:
        """Gets unique, non-empty team list from a DataFrame used later to enrich the dataset.

        Returns:
            list: List of non-empty unique teams from downloaded match data.
        """
        df_team_name = self.df_matches["teamname"].dropna().unique()
        return list(df_team_name)

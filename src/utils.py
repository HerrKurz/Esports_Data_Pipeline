"""
Utilities related to the project. Mainly contains the functions responsible for data transformations.
"""
import json

import pandas as pd

from config import COUNTRIES_TRANSLATE_DICT, CSV_FILES

pd.options.mode.chained_assignment = None


def append_id(df: pd.DataFrame) -> None:
    """Adds a new column with a unique id for each row.

    Parameters:
        df (pd.DataFrame): The main Data Frame with match data.
    """
    df["_id"] = df[["gameid", "participantid"]].apply(
        lambda x: "-".join(x.map(str)), axis=1
    )


def append_player_info(df: pd.DataFrame, players_dict: dict):
    """Adds the player info for each player occurrence in 'playername' column.

    Parameters:
        df (pd.DataFrame): The main Data Frame containing match data.
        players_dict (dict): Dictionary of player data from Leaguepedia.
    """
    df["Player_info"] = df["playername"].map(players_dict)


def append_country_to_player(df: pd.DataFrame, player_dict: dict) -> pd.DataFrame:
    """Adds a new column with a country name for a player.

    Parameters:
        df (pd.DataFrame): The main Data Frame with match data.
        player_dict (dict): Dictionary of player data from Leaguepedia.

    Returns:
        pd.DataFrame: The main Data Frame containing match data.
    """
    try:
        player_country_dict = {
            player_name: country["Country"]
            for player_name, country in player_dict.items()
        }
        df["Country"] = df["playername"].map(player_country_dict)
    except KeyError as e:
        df["Country"] = ""
        print(f"Key error {e}.")
    return df


def append_team_info(df: pd.DataFrame, teams_dict: dict):
    """Adds a team info for each team occurrence in 'teamname' column.

    Parameters:
        df (pd.DataFrame): The main Data Frame containing match data.
        teams_dict (dict): Dictionary of team data from Leaguepedia.
    """
    df["Team_info"] = df["teamname"].map(teams_dict)


def clean_json(batch: list, pop_item_name: str) -> list:
    """Removes a provided element from the list of dictionaries.

    Parameters:
        batch (list): List of dictionaries.
        pop_item_name (str): Name of the item to be removed.

    Returns:
        list: List of dictionaries with specified item removed.
    """
    return list(map(lambda elem: elem.pop(pop_item_name), batch))


def convert_to_json(df: pd.DataFrame) -> list:
    """Converts a dataframe to json.

    Parameters:
        df (pd.DataFrame): The main Data Frame containing match data.

    Returns:
        list: List of dictionaries containing match data.
    """
    df = json.loads(df.to_json(orient="table"))
    return df["data"]


def convert_years_to_url(years: list, current_year: int) -> list:
    """Gets the list of URL links for provided list of years.

    Parameters:
        years (list): List of selected years.
        current_year (int): Current year.

    Returns:
        list: Returns the list of config URLs for provided years.
    """
    return list(
        set(
            [
                CSV_FILES.get(f"{year}", CSV_FILES[f"{current_year}"])
                for year in years
                if year
            ]
        )
    )


def create_msg_batches(messages: list, batch_size: int) -> list:
    """Splits the list of items into batches of specified sizes.

    Parameters:
        messages (list): List of dictionaries containing the data.
        batch_size (int): Number of items per each batch.

    Returns:
        list: List of dictionaries containing the data split into the batches.
    """
    return [
        messages[i * batch_size : (i + 1) * batch_size]
        for i in range((len(messages) + batch_size - 1) // batch_size)
    ]


def merge_csv_files(csv_files: list) -> pd.DataFrame:
    """Merges the list of downloaded .csv files into single dataframe.

    Parameters:
        csv_files (list): A list of filenames of the downloaded .csv files to be merged.

    Returns:
        pd.DataFrame: A DataFrame containing the merged data from all the .csv files.
    """
    return pd.concat(map(pd.read_csv, csv_files), ignore_index=True)


def clean_countries_list(country_list: list) -> list:
    """Converts country names to fit the endpoint at REST countries.

    Parameters:
        country_list (list): List of country names.

    Returns:
        list: List of country names to fit the endpoint at REST countries
    """
    return [
        country.replace(country, COUNTRIES_TRANSLATE_DICT.get(country, country))
        for country in set(country_list)
        if country
    ]


def adjust_dict_values(data_dict: dict) -> dict:
    """Handling the United States and China name abbreviations."""
    data_dict["United States"] = data_dict.pop("USA")
    data_dict["China"] = data_dict.pop("CN")
    return data_dict

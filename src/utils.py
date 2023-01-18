"""
Utilities related to the project. Mainly contains the functions responsible for data transformations.
"""
from config import COUNTRIES_TRANSLATE_DICT, CSV_FILES
import json
import pandas as pd
pd.options.mode.chained_assignment = None


def append_id(df: pd.DataFrame) -> None:
    """Adds a new column with a unique id for each row."""
    df['_id'] = df[['gameid', 'participantid']].apply(lambda x: '-'.join(x.map(str)), axis=1)


def append_country_to_player(df: pd.DataFrame, player_dict: dict) -> pd.DataFrame:
    """Adds a new column with a country name for a player."""
    try:
        player_country_dict = {player_name: country["Country"] for player_name, country in player_dict.items()}
        df['Country'] = df['playername'].map(player_country_dict)
    except KeyError as e:
        df['Country'] = ""
        print(f"Key error {e}.")
    return df


def append_player_info(df: pd.DataFrame, players_dict: dict):
    """Adds the player info for each player occurrence in 'playername' column."""
    df["Player_info"] = df["playername"].map(players_dict)


def clean_json(batch: list, pop_item_name: str) -> list:
    """Removes a provided element from the list of dictionaries."""
    return list(map(lambda elem: elem.pop(pop_item_name), batch))


def convert_to_json(df: pd.DataFrame) -> list:
    """Converts a dataframe to json."""
    df = json.loads(df.to_json(orient='table'))
    return df["data"]


def convert_years_to_url(years: list, current_year: int) -> list:
    """Gets the list of URL links for provided list of years."""
    return list(set([CSV_FILES.get(f"{year}", CSV_FILES[f"{current_year}"]) for year in years if year]))


def create_msg_batches(messages: list, batch_size: int) -> list:
    """Splits the list of items into batches of specified sizes."""
    return [messages[i * batch_size:(i + 1) * batch_size] for i in range((len(messages) + batch_size - 1) // batch_size)]


def merge_csv_files(csv_files: list) -> pd.DataFrame:
    """Merges the list of downloaded .csv files into single dataframe."""
    return pd.concat(map(pd.read_csv, csv_files), ignore_index=True)


def clean_countries_list(country_list: list) -> list:
    """Converts country names to fit the endpoint at REST countries."""
    return [country.replace(country, COUNTRIES_TRANSLATE_DICT.get(country, country)) for country in set(country_list) if country]


def change_dict_values(dictionary: dict) -> dict:
    """Hotfix for data visualization purpose."""
    for k, v in dictionary.items():
        if v['Country'] == "United States":
            v['Country'] = "USA"
    return dictionary



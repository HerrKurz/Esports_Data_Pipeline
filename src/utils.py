"""
Utilities related to the project. Mostly contains the functions responsible for data transformations.
"""

import json
import pandas as pd
from config import COUNTRIES_TRANSLATE_DICT, CSV_FILES
pd.options.mode.chained_assignment = None


def clean_json(batch: list) -> list:
    """Removes index key created by pandas dataframe."""
    return list(map(lambda elem: elem.pop("index"), batch))


def convert_to_json(df: pd.DataFrame) -> list:
    """Converts a dataframe to json, to help loading it into Elasticsearch."""
    df = json.loads(df.to_json(orient='table'))
    return df["data"]


def create_msg_batches(messages: list, batch_size: int) -> list:
    """Splits the list of items into batches of specified size."""
    return [messages[i * batch_size:(i + 1) * batch_size] for i in range((len(messages) + batch_size - 1) // batch_size)]


def add_id_column(df: pd.DataFrame) -> None:
    """Creates a column with a unique id for each row."""
    df['_id'] = df[['gameid', 'participantid']].apply(lambda x: '-'.join(x.map(str)), axis=1)


def clean_countries_list(country_list: list) -> list:
    """Converts country names to fit the endpoint at REST countries."""
    return [country.replace(country, COUNTRIES_TRANSLATE_DICT.get(country, country)) for country in set(country_list) if country]


def convert_years_to_url(years: list, current_year: int) -> list:
    """Gets the list of URL links for provided list of years."""
    return list(set([CSV_FILES.get(f"{year}", CSV_FILES[f"{current_year}"]) for year in years if year]))


def merge_csv_files(csv_files: list) -> pd.DataFrame:
    """Merges the list of downloaded .csv files into single dataframe."""
    return pd.concat(map(pd.read_csv, csv_files), ignore_index=True)


def change_dict_values(dictionary: dict) -> dict:
    """Hotfix for data visualization purpose."""
    for k, v in dictionary.items():
        if v['Country'] == "United States":
            v['Country'] = "USA"
    return dictionary

import json
import pandas as pd
from config import COUNTRIES_TRANSLATE_DICT, CSV_FILES
pd.options.mode.chained_assignment = None


def clean_json(batch: list) -> list:
    """Removes index key, created by using pandas dataframe."""
    return list(map(lambda elem: elem.pop("index"), batch))


def convert_to_json(df: pd.DataFrame) -> list:
    """Converts a dataframe to json, to help loading it into Elasticsearch."""
    df = json.loads(df.to_json(orient='table'))
    return df["data"]


def create_msg_batches(messages: list, batch_size: int) -> list:
    return [messages[i * batch_size:(i + 1) * batch_size] for i in range((len(messages) + batch_size - 1) // batch_size)]


def add_id_column(df: pd.DataFrame) -> None:
    df['_id'] = df[['gameid', 'participantid']].apply(lambda x: '-'.join(x.map(str)), axis=1)


# def add_id_column_test(df: pd.DataFrame) -> None:
#     df['_id'] = f"{df['gameid']}-{df['playerid'] if df['playerid'].empty else df['teamid']}"


def clean_countries_list(country_list: list) -> list:
    """ Convert country names to fit an endpoint at REST countries."""
    return [country.replace(country, COUNTRIES_TRANSLATE_DICT.get(country, country)) for country in set(country_list) if country is not None]


def convert_years_to_url(years: list, current_year: int) -> list:
    """Convert list of years to list of URLs to download."""
    return list(set([CSV_FILES.get(f"{year}", CSV_FILES[f"{current_year}"]) for year in years if year is not None]))


def merge_csv_files(url_list: list) -> pd.DataFrame:
    """Merges .csv files on columns into single dataframe."""
    return pd.concat(map(pd.read_csv, url_list), ignore_index=True)

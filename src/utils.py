import json
import pandas as pd


def clean_json(batch: list) -> list:
    clean_list = []
    for elem in batch:
        elem.pop("index")
        clean_list.append(elem)
    return clean_list


def convert_to_json(df: pd.DataFrame) -> list:
    df = json.loads(df.to_json(orient='table'))
    return df["data"]


def create_msg_batches(messages: list, batch_size: int) -> list:
    return [messages[i * batch_size:(i + 1) * batch_size] for i in range((len(messages) + batch_size - 1) // batch_size)]



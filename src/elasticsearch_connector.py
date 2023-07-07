"""
Handles the connection between Python and Elasticsearch and loads the data to the database.
"""
import datetime

import urllib3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.helpers import bulk
from tqdm import tqdm

from config import ELASTIC_PASSWORD, ELASTIC_USERNAME, PORT, URL
from src.utils import clean_json, create_msg_batches

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
TODAY = str(datetime.date.today())

"""Setup for a communication between Python and Elasticsearch. Can specify True if localhost."""


class ElasticsearchConnector:
    def __init__(self, local: bool = False):
        self.es_client = Elasticsearch(
            hosts=[{"host": URL if not local else "localhost", "port": PORT}],
            # http_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD),
            scheme="http",
            use_ssl=False,
            verify_certs=False,
            connection_class=RequestsHttpConnection,
            retry_on_timeout=False,
            timeout=5000,
        )

        """Loads the data as a list of dicts into Elasticsearch using bulks of specified batch size.
        Possible to specify the name of the Elasticsearch index as an argument.
        """

    # def send_data(self, message_list: list, batch_size: int = 500, index: str = f"esports-data-{TODAY}"):
    def send_data(
        self,
        message_list: list,
        batch_size: int = 500,
        index: str = f"esports-data-2023-06-30",
    ):
        """
        Loads the data as a list of dicts into Elasticsearch using bulks of specified batch size.
        Possible to specify the name of the Elasticsearch index as an argument

        Parameters:
            message_list (list): List of dictionaries containing the data.
            batch_size (int, optional): Splits the list of items into batches of specified size. Defaults to 500.
            index (str, optional): Specifies the name of an index where the data is loaded. It's recommended to provide the index name matching the pattern "esports-data*", which uses created template settings and mappings for indices. Defaults to f"esports-data-{TODAY}".
        """
        msg_batches = create_msg_batches(message_list, batch_size)
        for batch in tqdm(
            msg_batches, colour="CYAN", desc=f"Sending data to the index {index}"
        ):
            clean_json(batch, "index")
            resp = bulk(
                client=self.es_client,
                index=index,
                actions=batch,
            )
        print(f"Loading data to Elasticsearch to index {index} has been completed.")

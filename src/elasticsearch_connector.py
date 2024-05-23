import datetime
import json
import urllib3
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from tqdm import tqdm
from config import ELASTIC_PASSWORD, ELASTIC_USERNAME, PORT, URL
from src.utils import clean_json, create_msg_batches

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
TODAY = str(datetime.date.today())


class ElasticsearchConnector:
    def __init__(self, local: bool = False):
        if local:
            self.es_client = Elasticsearch(
                "http://localhost:9200",
                basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD),
                verify_certs=False,
                request_timeout=5000,
            )
        else:
            self.es_client = Elasticsearch(
                f"{URL}:{PORT}",
                basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD),
                verify_certs=True,
                request_timeout=5000,
            )

    def read_mappings(self, file_path: str) -> dict:
        """Read mappings from a file."""
        with open(file_path, "r") as file:
            mappings = json.load(file)
        return mappings

    def create_index_with_mappings(self, index: str, mappings: dict):
        """Create an index with the given mappings."""
        if not self.es_client.indices.exists(index=index):
            self.es_client.indices.create(index=index, body=mappings)
            print(f"Index {index} created with mappings.")
        else:
            print(f"Index {index} already exists.")

    def send_data(
        self,
        message_list: list,
        batch_size: int = 500,
        index: str = f"esports-data-{TODAY}",
        mappings_file: str = "./Elasticsearch/mapping.txt",
    ):
        """
        Loads the data as a list of dicts into Elasticsearch using bulks of specified batch size.
        Possible to specify the name of the Elasticsearch index as an argument.

        Parameters:
            message_list (list): List of dictionaries containing the data.
            batch_size (int, optional): Splits the list of items into batches of specified size. Defaults to 500.
            index (str, optional): Specifies the name of an index where the data is loaded. It's recommended to provide the index name matching the pattern "esports-data*", which uses created template settings and mappings for indices. Defaults to f"esports-data-{TODAY}".
            mappings_file (str, optional): Path to the mappings file. Defaults to "Elasticsearch/mappings.txt".
        """
        mappings = self.read_mappings(mappings_file)
        self.create_index_with_mappings(index, mappings)

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

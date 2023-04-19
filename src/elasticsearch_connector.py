"""
Handles the connection between Python and Elasticsearch and loads the data to the database.
"""
from tqdm import tqdm
from config import URL, PORT, ELASTIC_USERNAME, ELASTIC_PASSWORD
import datetime
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.helpers import bulk
from src.utils import clean_json, create_msg_batches
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
TODAY = str(datetime.date.today())


class ElasticsearchConnector:
    """Setup for a communication between Python and Elasticsearch. Can specify True if localhost."""
    def __init__(self, local: bool = False):
        self.es_client = Elasticsearch(
            hosts=[{'host': URL if not local else "localhost", 'port': PORT}],
            http_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD),
            scheme='http',
            use_ssl=True,
            verify_certs=False,
            connection_class=RequestsHttpConnection,
            retry_on_timeout=False,
            timeout=5000
        )
    # def send_data(self, message_list: list, batch_size: int = 500, index: str = f"esports-data-{TODAY}"):
    def send_data(self, message_list: list, batch_size: int = 500, index: str = f"also-teams{TODAY}"):
        """Loads the data as a list of dicts into Elasticsearch using bulks of specified batch size.
        Possible to specify the name of the Elasticsearch index as an argument.
        """
        msg_batches = create_msg_batches(message_list, batch_size)
        for batch in tqdm(msg_batches, colour='CYAN', desc=f'Sending data to the index {index}'):
            clean_json(batch, "index")
            resp = bulk(
                client=self.es_client,
                index=index,
                actions=batch,
            )
        print(f"Loading data to Elasticsearch to index {index} has been completed.")

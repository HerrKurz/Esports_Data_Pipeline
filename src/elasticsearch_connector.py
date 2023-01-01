"""
Loads transformed and enriched data into Elasticsearch.
"""
import datetime
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.helpers import bulk
from config import URL, PORT, ELASTIC_USERNAME, ELASTIC_PASSWORD
from src.utils import clean_json, create_msg_batches
TODAY = str(datetime.date.today())


class ElasticsearchConnector:
    """Provides a mapping from Python to Elasticsearch REST API."""
    def __init__(self, elastic_url=URL):
        self.es_client = Elasticsearch(
            hosts=[{'host': elastic_url, 'port': PORT}],
            http_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD),
            scheme='http',
            use_ssl=True,
            verify_certs=False,
            connection_class=RequestsHttpConnection,
            retry_on_timeout=False,
            timeout=5000
        )
        self.today = str(datetime.date.today())

    def send_data(self, message_list: list, batch_size: int, index: str = f"esports-data-{TODAY}"):
        """Loads the data as a list of dicts into Elasticsearch using bulks of specified batch size.
        Possible to specify the name of the Elasticsearch index as an argument"""
        msg_batches = create_msg_batches(message_list, batch_size)
        for batch in msg_batches:
            counter = 0
            clean_json(batch)
            resp = bulk(
                client=self.es_client,
                index=index,
                actions=batch,
            )
            counter += 1
            print(f"Sending: batch {counter}/{len(msg_batches)}, to index {index} with response: {resp}.")
        print(f"Loading data to Elasticsearch at index {index} has been completed.")

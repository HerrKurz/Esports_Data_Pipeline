"""
Loads transformed and enriched data into Elasticsearch deployed at AWS EC2.
"""
import datetime
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.helpers import bulk
from config import url, port, username, password
from src.utils import clean_json, create_msg_batches


class ElasticsearchConnector:
    def __init__(self):
        self.es_client = Elasticsearch(
            hosts=[{'host': url, 'port': port}],
            http_auth=(username, password),
            scheme='http',
            use_ssl=True,
            verify_certs=False,
            connection_class=RequestsHttpConnection,
            retry_on_timeout=False,
            timeout=5000
        )
        self.today = str(datetime.date.today())

    def send_data(self, message_list: list, batch_size: int):
        msg_batches = create_msg_batches(message_list, batch_size)
        for batch in msg_batches:
            batch = clean_json(batch)
            resp = bulk(
                client=self.es_client,
                index=f"test-index-v2",
                actions=batch,
            )
            print(f"Sending: {len(msg_batches)}, response: {resp}")
        print(f"Loading data to Elasticsearch has been completed.")

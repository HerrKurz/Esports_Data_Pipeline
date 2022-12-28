from src.data_enricher import DataEnricher
from src.data_extractor import GetData
from src.elasticsearch_connector import ElasticsearchConnector
import os

if __name__ == "__main__":
    elasticsearch_connector = ElasticsearchConnector()
    data = GetData()
    print(os.environ)
    data_enricher = DataEnricher(data.player_names, data.df_matches)
    enriched_data = data_enricher.enrich_data(data.df_matches)
    elasticsearch_connector.send_data(enriched_data, 5000)



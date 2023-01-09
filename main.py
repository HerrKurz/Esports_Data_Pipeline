from src.data_enricher import DataEnricher
from src.data_extractor import GetData
from src.elasticsearch_connector import ElasticsearchConnector

if __name__ == "__main__":
    elasticsearch_connector = ElasticsearchConnector()
    data = GetData(limits=None, year=["2014"])
    data_enricher = DataEnricher(data)
    enriched_data = data_enricher.enrich_data(data.df_matches)
    elasticsearch_connector.send_data(message_list=enriched_data, batch_size=5000, index="test-index-jan")

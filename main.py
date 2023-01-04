from config import ALL_YEARS
from src.data_enricher import DataEnricher
from src.data_extractor import GetData
from src.elasticsearch_connector import ElasticsearchConnector
import time
st = time.time()

if __name__ == "__main__":
    elasticsearch_connector = ElasticsearchConnector()
    data = GetData(limits=None, year=['2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022'])
    data_enricher = DataEnricher(data)
    enriched_data = data_enricher.enrich_data(data.df_matches)
    elasticsearch_connector.send_data(message_list=enriched_data, batch_size=5000)
    et = time.time()
    elapsed_time = et - st
    print('Execution time:', elapsed_time, 'seconds')
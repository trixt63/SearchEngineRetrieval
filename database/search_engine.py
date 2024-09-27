import logging
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from config import SearchEngineConfig


class SearchEngine:
    def __init__(self, host=SearchEngineConfig.HOST,
                 username=SearchEngineConfig.USERNAME,
                 password=SearchEngineConfig.PASSWORD):
        self.es = Elasticsearch(hosts=[f"http://{host}:9200"],
                                http_auth=(username, password),
                                verify_certs=True)
        if self.es.ping():
            print("Connected to Elasticsearch!")
        else:
            logging.exception(f"Cannot connect to {host}")

    def match_all(self, index):
        res = self.es.search(index=index, body={"query": {"match_all": {}}})
        result = [hit for hit in res["hits"]["hits"]]
        return result

    def import_bulk(self, documents, index_name):
        bulk(self.es, generate_bulk_data(documents, index_name))


# Bulk data generator
def generate_bulk_data(documents, index_name):
    for i, doc in enumerate(documents):
        yield {
            "_index": index_name,
            "_id": doc['_id'],
            "_source": doc
        }

import logging
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from config import SearchEngineConfig
from utils.logger_utils import get_logger

logger = get_logger("Elasticsearch")


class SearchEngine:
    def __init__(self, host=SearchEngineConfig.HOST,
                 username=SearchEngineConfig.USERNAME,
                 password=SearchEngineConfig.PASSWORD,
                 ca_certs=SearchEngineConfig.CA_CERT_PATH):
        self._client = Elasticsearch(hosts=[f"https://{host}:9200"],
                                     http_auth=(username, password),
                                     ca_certs=ca_certs,
                                     verify_certs=True)
        # if self.es.ping():
        #     logger.info("Connected to Elasticsearch!")
        # else:
        #     logger.exception(f"Cannot connect to {host}")

        logger.info("Creating index")
        try:
            self.create_index(index_name=SearchEngineConfig.INDEX_NAME)
        except Exception as ex:
            logger.exception(f'Failed to create index {SearchEngineConfig.INDEX_NAME}: {ex}')

    def match_all(self, index):
        res = self._client.search(index=index, body={"query": {"match_all": {}}})
        result = [hit for hit in res["hits"]["hits"]]
        return result

    def import_bulk(self, documents: dict, index_name=SearchEngineConfig.INDEX_NAME):
        docs_to_insert = [
            {
                "_index": index_name,
                "_id": _id,
                "_source": doc
            }
            for _id, doc in documents.items()
        ]
        bulk(self._client, docs_to_insert)

    def create_index(self, index_name):
        """Creates an index in Elasticsearch if one isn't already there."""
        self._client.indices.create(
            index=index_name,
            body={
                "settings": {"number_of_shards": 1},
                "mappings": {
                    "properties": {
                        "page_number": {"type": "integer"},
                        "lines": {"type": "integer", "index": "false"},
                        "text": {"type": "text", "analyzer": "standard"},
                        "section": {"type": "keyword"},
                    }
                },
            },
            ignore=400,
        )


# Bulk data generator
def generate_bulk_data(documents, index_name):
    for i, doc in enumerate(documents):
        yield {
            "_index": index_name,
            "_id": doc['_id'],
            "_source": doc
        }

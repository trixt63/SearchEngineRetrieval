import logging
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from config import SearchEngineConfig
from utils.logger_utils import get_logger

logger = get_logger("Elasticsearch")


class SearchEngine:
    def __init__(self,
                 host=SearchEngineConfig.HOST,
                 port=SearchEngineConfig.PORT,
                 username=SearchEngineConfig.USERNAME,
                 password=SearchEngineConfig.PASSWORD,
                 ca_cert=SearchEngineConfig.CA_CERT_PATH):
        self._client = Elasticsearch(hosts=[f"https://{host}:{port}"],
                                     http_auth=(username, password),
                                     ca_certs=ca_cert,
                                     verify_certs=True)
        logger.info("Creating index")
        try:
            self._create_index(index_name=SearchEngineConfig.INDEX_NAME)
        except Exception as ex:
            logger.exception(f'Failed to create index {SearchEngineConfig.INDEX_NAME}: {ex}')

    def _create_index(self, index_name):
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
                        "section": {"type": "text", "analyzer": "standard"},
                        "subsection": {"type": "text", "analyzer": "standard"},
                        "subsubsection": {"type": "text", "analyzer": "standard"},
                    }
                },
            },
            ignore=400,
        )

    def import_bulk(self, documents: dict, index_name=SearchEngineConfig.INDEX_NAME):
        bulk(self._client, self._generate_bulk_data(documents, index_name))

    def search_keyword(self, index_name=None, query="") -> list:
        if not index_name:
            index_name = SearchEngineConfig.INDEX_NAME

        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["section", "subsection", "subsubsection", "text"],
                    "type": "phrase"
                }
            }
        }

        try:
            response = self._client.search(index=index_name, body=search_body)
            hits = response.get('hits', {}).get('hits', [])
            return hits
        except Exception as e:
            print(f"Error executing search: {str(e)}")
            return []

    @staticmethod
    def _generate_bulk_data(documents: dict, index_name):
        for _id, doc in documents.items():
            yield {
                "_index": index_name,
                "_id": _id,
                "_source": doc
            }

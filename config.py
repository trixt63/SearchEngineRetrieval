import os
from dotenv import load_dotenv

load_dotenv()


class SearchEngineConfig:
    HOST = os.environ.get("ES_HOST", 'localhost')
    PORT = os.environ.get("ES_PORT", '9200')
    USERNAME = os.environ.get("ES_USERNAME", "elastic")
    PASSWORD = os.environ.get("ELASTIC_PASSWORD")

    CA_CERT_PATH = os.environ.get("CA_CERT_PATH")
    INDEX_NAME = os.environ.get("INDEX_NAME", "s3-userguide")

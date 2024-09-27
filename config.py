import os
from dotenv import load_dotenv

load_dotenv()


class SearchEngineConfig:
    HOST = os.environ.get("ES_HOST", '0.0.0.0')
    PORT = os.environ.get("ES_PORT", '9200')
    USERNAME = os.environ.get("ES_USERNAME", "elastic")
    PASSWORD = os.environ.get("ELASTIC_PASSWORD")

    BOOK_INDEX = 's3-userguide'

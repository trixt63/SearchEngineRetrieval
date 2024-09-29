import argparse
import json

from config import SearchEngineConfig
from database.search_engine import SearchEngine
from utils.logger_utils import get_logger

logger = get_logger("Search keyword")


def main():
    parser = argparse.ArgumentParser(description="Search keyword from Elasticsearch")
    parser.add_argument("--index", default=SearchEngineConfig.INDEX_NAME,
                        help="The name of the Elasticsearch index to search from")
    parser.add_argument("--query", required=True,
                        help="The search keyword or phrase")
    parser.add_argument("--host", default=SearchEngineConfig.HOST,
                        help="Elasticsearch host)")
    parser.add_argument("--port", default=9200, type=int,
                        help="Elasticsearch port")
    parser.add_argument("--username", default=SearchEngineConfig.USERNAME,
                        help="Elasticsearch username")
    parser.add_argument("--password", default=SearchEngineConfig.PASSWORD,
                        help="Elasticsearch password")
    parser.add_argument("--ca_cert", default=SearchEngineConfig.CA_CERT_PATH,
                        help="Path to CA certificate file")

    args = parser.parse_args()

    search_engine = SearchEngine(host=args.host,
                                 port=args.port,
                                 username=args.username,
                                 password=args.password,
                                 ca_cert=args.ca_cert)
    results = search_engine.search_keyword(index_name=args.index,
                                           query=args.query)

    if results:
        print_search_result(results=results, query=args.query)
    else:
        logger.info("No results found.")


def print_search_result(results: list[dict], query=None):
    logger.info(f"Search results for query {query}: {len(results)} results:")
    for _i, result in enumerate(results):
        _info = result.get("_source", {})
        page_number, line0, line1, section, text = (_info['page_number'], _info['lines'][0], _info['lines'][1],
                                                    _info['section'], _info['text'])
        output_str = f'Page {page_number}; line {line0} to {line1}; section "{section}'
        if _info.get("subsection"):
            output_str += f" > {_info['subsection']}"
            if _info.get("subsubsection"):
                output_str += f" > {_info['subsubsection']}"

        output_str += f'" \n\t Related text: "{text}"'

        print(output_str)


if __name__ == "__main__":
    main()

# Search engine retrieval
You are given a documentation on S3
https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-userguide.pdf
You are tasked with:
- Deploy Elasticsearch or Open Search Single Node Cluster using Docker or similar
technologies
- Break and ingest the given documentation into Search Clusters. Note that:
o The documentation is a long form documents, they have Title, sections based on
tree of contents
o You will need to read the text from the pdf files.
o Long documents need to be broken down to short chunks of text, ideally by
paragraph
o Each chunk of text needs to have metadata related to pages in documents, line
number in page, section header, subsection (if available).

- Given a keyword, we would like to search documents according to these precedent
rules:
o Title
o Section Title
o Related Paragraph that contains the keyword.

## 0. Create Python environment
- Create a Python virtual environment, then install the requirements: 
```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
## 1. Install Elasticsearch
- Fill the `.env` file (following the `.env.example` file format): 
```cp .env.example .env```

- Install Elasticsearch and Kibana by using the following command:
```sh
docker-compose up -d
```
- With this, you will be able to open the following urls :
    - http://localhost:5601/ - Kibana Web UI interface
    - http://localhost:9200/ - Elastic Search API
- Login with user *elastic* ib tge Kibana Web UI, and run the following commands in the Kibana console to test the deployment:
```
GET _cluster/health
GET _nodes/stats
```

## 2. Ingest data from book
- First, create a subfolder `data/` and put the pdf file there: `data/s3-userguide.pdf`
- Create a index on Elasticsearch cluster with name *s3-userguide*
- Run Python script in `ingestion.py`: 
```
python3 ingestion.py
```

## 3. Search with keyword
- Open Kibana WebUI on http://localhost:5601/, then search with the following syntax on the console:
```
GET s3-userguide/_search
{
  "query": {
    "multi_match": {
      "query": "enter keyword",
      "fields": [
        "section",
        "subsection",
        "subsubsection", 
        "text"
      ],
      "type": "phrase"
    }
  }
}
```
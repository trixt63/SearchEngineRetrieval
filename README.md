## Install Elasticsearch
Version: 8.13.2
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
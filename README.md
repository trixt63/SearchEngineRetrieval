## Install Elasticsearch
- elasticsearch:7.11.1
- kibana:7.11.1
- Create a network:
```sh
docker network create elasticnet
```
Install Elasticsearch and Kibana by using the following command:
```sh
docker-compose up -d
```
The previous command is going to spin up two docker containers that will be in the same Docker network and in detached mode. With this, you will be able to open the following urls :

* http://localhost:5601/ - Kibana Web UI interface
* http://localhost:9200/ - Elastic Search API

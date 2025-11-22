# Rag for scraped retail data

A fully-automated RAG pipeline that scrapes fossil products, chunks and embeds their data, stores vector representations in PostgreSQL (pgvector), and provides evaluation and optimization tools to measure and improve retrieval quality.

Currently we scrape all the products on this page:

https://vantony.com/4-fosili

And have a chatbox answering questions about them. 

## How to run locally

### Prerequisites

1. Installed and configured Docker and Docker compose
2. OPEN_AI_API_KEY set in .env file 

Create .env file inside the root directory. Not pushed to the repo for security reasons. Example:

```
export DB_USER="postgres"
export DB_PASS="postgres"
export DB_PORT="5432"
export DB_NAME="embeddings"
export EMBEDDING_MODEL="text-embedding-3-small"
export PGADMIN_DEFAULT_EMAIL="admin@admin.com" #for pgadmin
export PGADMIN_DEFAULT_PASSWORD="admin" #for pgadmin
export OPEN_AI_API_KEY="YOUR API KEY"

```

Then you just run:

`docker compose up --build`

And wait until all the services are built. You can use to confirm everything is OK:

`docker ps`

3 containers should remain up - pgvector, pgadmin and fastapi. If that's the case. Just open the **client.html** and you will connect through the websocket with this small ugly js connection. 

## Architecture

This project is built as a modular microservice-based RAG pipeline, where each component runs inside its own Docker container. The goal is to automatically scrape fossil products, extract structured data, embed and store it in PostgreSQL with pgvector, and then evaluate and optimize retrieval quality.

All microservices are orchestrated using docker-compose, which spins up:

1. scraper — crawls the website and saves raw product JSON.

2. data_processor — cleans text, chunks descriptions, and produces structured chunks for embedding.

3. data_ingestor — generates embeddings via OpenAI, stores vectors + metadata in PostgreSQL.

4. fastapi — exposes a WebSocket/HTTP interface for retrieval queries.

5. db/postgres — database with pgvector extension and schema auto-bootstrap.

6. pgadmin - nice UI addition you can find on http://localhost:5050/, helping to debug and do SQL stuff easily.

7. rag_orchestrator - a crucial service that helps us evaluate and improve the entire pipeline. It acts as evaluation and optmization frameworks. Uses command line interface to create reports which we use to finetune parameters and improve overall performance.


Each service builds from its own Dockerfile and communicates with others through shared volumes and the internal Docker network.

## Why this architecture

This design provides solutions to couple very important concerns regarding this product:

1. Scalability 

    - horizontal scalability is inevitable - we can expect a rise in I/O tasks as the users grow - more requests, more db operations. More scrapers + more file reading and writing..
    - vertical scalability is likely - currently we use OPENAI API but what if we decide to build our own embedders? Or our own LLM for security issues? Then we will need to scale vertically, add computation power. Its likely we will need to achieve real parallelism in that case

2. Maintenance - the implementation of the scalability described above would be a nightmare in some other architecture (like monolith e.g.). Just imagine in one sprint you solve people's complains about the connection being slow and the next sprint you have to achieve parallelism with multiprocessing because your custom embedders need computational power. All in the same place...

3. Fault isolation - we guarantee one service fails - the others will continue to work. Avoids single point of failure, typical for the monolithical architectures. 

4. This product is just too complex for a monolith


## Future improvements and roadmap

- testing - the code coverage is currently literally 0%
- research how to make the model aggregates. e.g. if I ask it how many products are there in total - its hallucinating because it depends on the top_k context provided.
- add another service (workers or schedulers or something like that) - that remains up and periodically scrapes, processeses and ingests data. So we don't have to do it manually or rely on redemployment as it is now.
- scrape more data and then check performance, latency and all the network metrics but also relevancy and faithfulness, creativity and other AI metrics.
- simple UI - another monitoring service - specifically delegated for evaluation and optmization - can be customized or grafana/prometheus 
- add better logging - custom or elasticsearch/kibana or solar?
- add option for hybrid retrieval - old school keyword search might even outperform the similarity search for retail data, as its not very complex

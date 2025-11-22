# Data Ingestion Service

This service defines the logic for ingesting the data into a vector database that we will later use for retrieval.

Technologies:

- pg and pgvector
- sqalchemy
- openai api for embeddings


This is run on containers' build so you dont need to worry about the initial ingeston of the data. Currently there are no chron jobs or any schedulers implemented so if you want to update the data or add more scrapers, you will have to run it with:

`python3 run`

Or just re-up the container again.

## Quick Architectural overview

Using OOP principles with common design and patterns.

- run.py - the main Python executable. Acts as template and facade as it hides the business logic
- ingestor.py - the main business logic resides here. It reads from "/data/processed" (the output from *Data Processing Service*) creates or updates the tables with the embeddings using openai api models.
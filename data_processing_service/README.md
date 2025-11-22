# Data Processing Service

This service cleans the data from the *Scraper service* in /data/raw, prepares the chunks for the embeddings and stores the cleaned files inside "data/processed/".

Similarly, its run on containers' build so you don't need to worry about it initially. If you want to rerun again later just:

`python3 run`

Or re-up the containers.

## Quick Architectural overview

Using OOP principles with common design and patterns.

- chunker.py - the main embedding logic. 
- utils.py - place for common cleaning functions.
- processor.py - common class for saving the results post processing
- run.py - the main Python executable. Acts as template and facade as it hides the business logic
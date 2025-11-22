# Scraper Service

Minimalistic scraping service (based on beautifulsoup and requests packages). The scraped products are stored in "/data/raw" as json documents.

This is run on containers' build so you dont need to worry about initial getting of the data. Currently there are no chron jobs or any schedulers implemented so if you want to update the data or add more scrapers, you will have to run it with:

`python3 run`

Or just re-up the container again.

## Currently scraping pages:

- https://vantony.com/4-fosili

## Quick Architectural overview

Using OOP principles with common design and patterns.

- run.py - the main Python executable. Acts as template and facade as it hides the business logic
- base_scraper.py - the parent of the children implementing the common methods they all share - requesting, parsing data, saving files.
- fosil_scraper - the only current children, hold the logic for scraping and extracting data specifically for "vantony" and fosils' page (but can be used for the entire website and all products).
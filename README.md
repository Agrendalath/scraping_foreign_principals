# Scraping Foreign Principals
The following projects was created for scraping Active Foreign Principals from [FARA](https://www.fara.gov/quick-search.html).

## Installation
This project uses [Pipenv](https://github.com/pypa/pipenv) for dependency management. To install it, please follow [Pipenv installation guide](https://docs.pipenv.org/install/).

To install dependencies, run

    pipenv sync
    
    
If you **really** don't want to install Pipenv, you can install requirements with

    pip install -r requirements.txt

    
## Running
To run the scraper, issue the following command:

    pipenv run scrapy crawl principals -o output.json

The output will be in `output.json` file.

### Additional parameters
If you want to change number of principals that are downloaded at once, you can provide extra argument,  

    pipenv run scrapy crawl principals -o output.json -a rows=30
    
By default, 30 rows are downloaded.
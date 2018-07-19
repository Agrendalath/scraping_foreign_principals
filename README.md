# Scraping Foreign Principals
The following projects was created for scraping Active Foreign Principals from [FARA](https://www.fara.gov/quick-search.html).

## Installation
This project uses [Pipenv](https://github.com/pypa/pipenv) for dependency management. To install it, please follow [Pipenv installation guide](https://docs.pipenv.org/install/).

To install dependencies, run:

    pipenv sync
    
    
If you **really** don't want to install Pipenv, you can install requirements with:

    pip install -r requirements.txt

    
## Usage
### Scraping
To run the scraper, issue the following command:

    pipenv run scrapy crawl principals -o output.json

The output will be in `output.json` file. Single row has the following format:
```json
{
    "url":"https://efile.fara.gov/pls/apex/f?p=185:200:3009375006631::NO:RP,200:P200_REG_NUMBER,P200_DOC_TYPE,P200_COUNTRY:6367,Exhibit%20AB,JORDAN",
    "foreign_principal":"Royal Hashemite Court of Jordan",
    "date":"2016-08-10T00:00:00Z",
    "address":"Amman",
    "state":null,
    "country":"JORDAN",
    "registrant":"West Wing Writers, LLC",
    "reg_num":"6367",
    "exhibit_url":[
        "http://www.fara.gov/docs/6317-Exhibit-AB-20180417-5.pdf",
        "http://www.fara.gov/docs/6317-Exhibit-AB-20170417-4.pdf",
        "http://www.fara.gov/docs/6317-Exhibit-AB-20161101-3.pdf",
        "http://www.fara.gov/docs/6317-Exhibit-AB-20160503-2.pdf",
        "http://www.fara.gov/docs/6317-Exhibit-AB-20150918-1.pdf"
    ]
}
```

### Additional parameters
If you want to change number of principals that are downloaded at once, you can provide extra argument:

    pipenv run scrapy crawl principals -o output.json -a rows=30
    
By default, 30 rows are downloaded.

### Testing
To run tests, run:

    pipenv run python scraping_foreign_principals/tests.py 


### Linters
To run formatting checks (pylint and black), you need to install dev dependencies with:
    
    pipenv sync --dev
    
Then issue the following commands:

    pipenv run pylint scraping_foreign_principals
    pipenv run black --check -Sl 80 scraping_foreign_principals
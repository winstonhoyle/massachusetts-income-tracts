## Massachusetts Income By Census Tract (2023)

A simple webmapping application to show different categories of income data by census tract. The map is a static html file using the data process below.
[Try Me!](https://raw.githack.com/winstonhoyle/massachusetts-income-tracts/main/app/index.html)

## Data
* [2023 Census Tracts](https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2023&layergroup=Census+Tracts)
* [2023 Income in the Psat 12 Months (in 2023 Inflation-Adjusted Dollars)](https://data.census.gov/table?q=income&g=040XX00US25$1400000)
* [Zip Codes](https://www.mass.gov/info-details/massgis-data-zip-codes-5-digit-from-here-navteq)

## Formatting the data
Download the data then run [format_data.py](format_data.py). Follow these commands:
```
python3.11 -m venv .venv
source .venv/bin/activate
python3.11 -m pip install -r requirements.txt
python3.11 format_data.py
```
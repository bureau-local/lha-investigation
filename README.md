# LHA property analysis

This repository contains the scripts we used to gather and analyse data about private rent across the UK to investigate whether the rate of Local Housing Allowance (LHA) is sufficient for people to afford to rent property across the UK.

This read me details the technical methodology and the scripts content. If you are looking for the reporting recipe and data from this project, please refer to [this document](https://docs.google.com/document/d/1ydf6xjYjCQtHPCefNGRZyQEmAG23UOJpCoyIk0UL6HA/).

## Methodology

### Data collection
This data was collected using the [Nestoria API](https://www.nestoria.co.uk/help/api). Note -- this data collection will not capture all rental properties on the market. We also only collected data on England, Wales and Scotland. Because Northern Ireland uses different sites, it was not included in this data collection and analysis.

Nestoria aggregates property data from the following sites that allow their data to be exposed through the API:
* homelike
* Findproperly
* Home.co.uk
* Citylets
* Moving Soon
* S1Homes
* NetHousePrices
* Ideal flatmate
* OnTheMarket.com
* SpotAHome
* Movebubble

The process of gathering data is as follows; for each UK postcode ([postcode-districts.csv](postcode-districts.csv)):
* Make a call to the Nestoria API of the form:
    ```
    https://api.nestoria.co.uk/api?action=search_listings&encoding=json&country=uk&number_of_results=50&listing_type=rent&place_name=<POSTCODE>&page=1&bedroom_min=2&bedroom_max=2
    ```
* Repeat for all pages returned by the API
* Any properties that do not have a valid location, price, or number of bedrooms (all of which are necessary for calculating affordability) are discarded

The code for this stage can be found in `properties.py`.

### Cleaning the data
Because we are pulling down results for each postcode and then combining in one database, we will sometimes have the same property listed multiple times. Therefore, it is important to detect and remove any duplicates in the list. To do this, we check for any duplicate URLs.

The code for this stage can be found in `cleaner.py`.

### Applying Boundaries
The next stage is to determine the appropriate Broad Rental Market Area (BRMA) for each property, as these are the boundaries that determine the amount of LHA per area and then determine whether it would be affordable for the local amount of LHA.

We obtained the shapefiles from the government’s [Valuation Office Agency (VOA)](https://www.gov.uk/government/organisations/valuation-office-agency).

As LHA is specified per week, but the majority of rents are specified per calendar month, the following calculation was used to convert between the two:
* Weekly Price = (Monthly Price * 12)/52.1429
* Monthly Price = (Weekly Price * 52.1429)/12

For each property:
* Loop through the BRMA location file (BRMA/) until a match is found
* Cache the matching BRMA so this can be checked first next time, as nearby properties are likely to share the same BRMA
* Using the matched BRMA, look up the appropriate LHA rate ([weekly-lha.csv](weekly-lha.csv))
* Compare the property rent to the LHA rent for the BRMA to determine affordability

The code for this stage can be found in `boundaries.py`.

### Analysis
This stage provides an overview of affordable properties by BRMA, and as well as the increase in LHA that would be necessary to make the 30th percentile of available properties affordable (according to government recommendations).

The code for this stage can be found in `analysis.py`.

## User guide

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Make sure to install the prerequisites with:

```
pip install -r requirements.txt
```

**Note:** if installing on Windows, you may need to download the [Shapely wheel files](https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely) directly


Ensure the following files are present:
* weekly-lha.csv
* postcode-districts.csv
* BRMA/gb-brma.shp
* BRMA/gb-brma.dbf


### Running the code

Import the library with:

```
import lha_investigation
```

Below is an example of a full run of the system (also provided in `lha_investigation.py`:

```
if __name__ == "__main__":
    import sys
    import traceback
    from datetime import datetime

    # Scrape information from the web about currently available properties in the UK
    # based on a list of UK postcodes (optionally starting from a given postcode)
    try:
        from properties import snapshot_properties
        print("Collecting properties....")
        start_time = datetime.now()
        snapshot_properties(outfile="output/properties.csv", short_run=False, min_beds=2, max_beds=2)    
        end_time = datetime.now()
        print("Finished running in: {}".format(end_time - start_time))
    except:
        end_time = datetime.now()
        traceback.print_exc()
        print("Crashed in: {}".format(end_time - start_time))
        sys.exit(1)

    # Remove duplicates from the list of properties we found
    try:
        from cleaner import remove_duplicates
        print("Removing duplicates....")
        start_time = datetime.now()
        remove_duplicates(infile="output/properties.csv", outfile="output/properties.csv")    
        end_time = datetime.now()
        print("Finished running in: {}".format(end_time - start_time))
    except:
        end_time = datetime.now()
        traceback.print_exc()
        print("Crashed in: {}".format(end_time - start_time))
        sys.exit(1)

    # Go through each property and check it against the file of BRMAs
    try:
        from boundaries import apply_boundaries
        print("Applying boundaries....")
        start_time = datetime.now()
        apply_boundaries(infile="output/properties.csv", outfile="output/properties.csv", overwrite=True)
        end_time = datetime.now()
        print("Finished running in: {}".format(end_time - start_time))
    except:
        end_time = datetime.now()
        traceback.print_exc()
        print("Crashed in: {}".format(end_time - start_time))
        sys.exit(1)

    # Go through the gathered data, analyse the results
    # and write the summary figures per BRMA to a file
    try:
        from analysis import analysis_to_file, create_overview_by_brma, total_listings, count_recent_scraped_listings, count_recent_listings
        print("Analysing data....")
        start_time = datetime.now()
        analysis_to_file(infile="output/test/properties.csv", outfile="output/test/analysis.csv")
        create_overview_by_brma("output/test/properties.csv", "output/test/by brma.csv")
        end_time = datetime.now()
        print("Finished running in: {}".format(end_time - start_time))
    except:
        end_time = datetime.now()
        traceback.print_exc()
        print("Crashed in: {}".format(end_time - start_time))
        sys.exit(1)
```

## Authors

* **Tom Blount** - *Initial work* - [http://tomblount.co.uk](http://tomblount.co.uk)
* **Charles Boutaud** - *Code review and maintenance* - [The Bureau of Investigative Journalism](https://www.thebureauinvestigates.com/)

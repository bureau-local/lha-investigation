import csv
import time
import requests
import os.path
from json import loads
from constants import FIELDS
from datetime import datetime, timedelta


DELAY = 1.25

def snapshot_properties(outfile, start_from=None, short_run=False, min_beds=None, max_beds=None):
    """Create a snapshot of 'all' (or as many as can be found) properties available for rent in the UK"""

    # Initialise list of postcodes
    postcodes = []
    with open("postcode-districts.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            postcodes.append(row["Postcode"])

    # To continue from a previous run, set start_from to the postcode you want
    # (just make sure to remove existing instances to avoid duplicates)
    postcodes = postcodes[postcodes.index(start_from):] if start_from else postcodes
    if start_from:
        print("#####################################")
        print("Starting from {}".format(start_from))
        print("#####################################")

    if not os.path.isfile(outfile):
        with open(outfile, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(FIELDS)

    for postcode in postcodes:
        get_nestoria_properties(outfile, postcode, short_run, min_beds, max_beds)


def get_nestoria_properties(outfile, postcode, short_run, min_beds, max_beds):

    start = None
    page = 1

    # Pagination
    while True:

        end = time.time()
        function_time = end - start if start else 0
        if(DELAY - function_time > 0):
            time.sleep(DELAY - function_time)


        url_min_beds = "&bedroom_min={}".format(min_beds) if min_beds else ""
        url_max_beds = "&bedroom_max={}".format(max_beds) if max_beds else ""

        url = "https://api.nestoria.co.uk/api?action=search_listings&encoding=json&country=uk&number_of_results=50&listing_type=rent&place_name={}&page={}{}{}".format(
            postcode,
            page,
            url_min_beds,
            url_max_beds
        )

        timeout = 2
        while True:
            try:
                response = requests.get(url)
                break
            except:
                print("Couldn't connect to Nestoria, waiting {} seconds and trying again...".format(timeout))
                time.sleep(timeout)
                timeout *= 2

        start = time.time()

        json = loads(response.text)["response"]

        try:
            x = json["listings"]
        except KeyError:
            print("No listings returned for postcode: {}".format(postcode))
            print(url)
            print(json)

        for listing in json["listings"]:

            print(listing["title"])

            try:
                x = listing["latitude"]
                x = listing["longitude"]
                price = float(listing["price"])
                price_type = listing["price_type"]
                bedrooms = int(listing["bedroom_number"])
            # Skip if one of the required properties for assessment is missing
            except KeyError:
                print(listing)
                continue
            # Skip if, e.g. "bedroom_number" is an empty-string
            except ValueError:
                continue

            if not (price_type == "weekly" or price_type == "monthly"):
                continue

            # If the number of bedrooms is, for whatever reason,
            # outside our specified bounds, then continue
            if (min_beds and not min_beds <= bedrooms) or (max_beds and not bedrooms <= max_beds):
                continue

            if bedrooms == 0 or bedrooms == 1:
                cat = "B"
            elif bedrooms == 2:
                cat = "C"
            elif bedrooms == 3:
                cat = "D"
            elif bedrooms == 4:
                cat = "E"
            else:
                cat = None

            # Manually check for this lister because we can (comfortably?)
            # assume that anything listed on it is CAT A
            if listing["datasource_name"] == "Ideal flatmate":
                cat = "A"

            # ...which then lets us remove it if we don't care about it
            # (We could remove it directly, but this way is more extensible)
            if cat == "A" and min_beds > 1:
                continue

            try:
                title = listing["title"]
            except KeyError:
                title = ""

            with open(outfile, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    (datetime.now() - timedelta(days=int(listing["updated_in_days"]))).strftime("%Y-%m-%d"),
                    listing["latitude"],
                    listing["longitude"],
                    title,
                    postcode,
                    "", #Add boundaries later
                    bedrooms,
                    "CAT {}".format(cat) if cat else "N/A",
                    listing["price"] if listing["price_type"] == "weekly" else "",
                    listing["price"] if listing["price_type"] == "monthly" else "",
                    "",
                    "Nestoria",
                    listing["datasource_name"] if listing["datasource_name"] else "Unknown",
                    listing["lister_url"] if listing["lister_url"] else "Unknown",
                    listing["img_url"] if listing["img_url"] else "",
                    "",
                    "",
                    listing["summary"],
                    ""
                ])

        # If in short run mode, only get the first page of results per postcode
        if short_run:
            break

        try:
            if not json["page"] < json["total_pages"]:
                break
            else:
                page = json["page"]+1

        except KeyError:
            break

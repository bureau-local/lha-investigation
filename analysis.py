import csv
import math
from constants import FIELDS, load_LHA
from datetime import datetime, timedelta


def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier

def count_recent_scraped_listings(infile, diff=timedelta(days=7)):
    """Return the number of listings that were scraped within a specified time (default 1 week) of being listed"""
    with open(infile) as csvfile:
        reader = csv.DictReader(csvfile)
        return sum(1 for _ in filter(lambda row: datetime.strptime(row["Listed Date"], "%Y-%m-%d") >= datetime.strptime(row["Scraped Date"], "%Y-%m-%d %H:%M:%S") - diff, reader))


def count_recent_listings(infile, diff=timedelta(days=7)):
    """Return the number of properties that were listed less than a specified time (default 1 week) ago"""
    with open(infile) as csvfile:
        reader = csv.DictReader(csvfile)
        return sum(1 for _ in filter(lambda row: datetime.strptime(row["Listed Date"], "%Y-%m-%d") >= datetime.now() - diff, reader))


def total_listings(infile, postcode=None, brma=None, cat=None):
    """Count the total number of listings found"""

    with open(infile) as csvfile:
        reader = csv.DictReader(csvfile)
        return sum(1 for _ in filter(lambda row: (not postcode or row["Postcode (District)"].lower() == postcode.lower()) and (not brma or row["BRMA"].lower() == brma.lower()) and (not cat or row["Category"].lower() == cat.lower()), reader))


def affordable_listings(infile, postcode=None, brma=None, cat=None, weekly_top_up=0):
    """Calculate how many of the listings are affordable for their particular BRMA
    Optionally, specify a particular postcode, BRMA, and Category to only consider properties that match these conditions.
    Optionally, specify a "monthly top-up"; extra money that a person could put towards their rent, to factor into the affordability
    calculation
    """

    if cat and cat not in ["CAT A", "CAT B", "CAT C", "CAT D", "CAT E"]:
        raise ValueError("Category must be in form e.g. 'CAT A'")

    with open(infile) as csvfile:
        reader = csv.DictReader(csvfile)
        filtered_rows = filter(lambda row: (not postcode or row["Postcode (District)"].lower() == postcode.lower()) and (not brma or row["BRMA"].lower() == brma.lower()) and (not cat or row["Category"].lower() == cat.lower()), reader)

        return sum([1 for row in filtered_rows if row["Affordable"].lower() == "true"])


def required_LHA_percentile(infile, brma, cat, percentage=0.30):
    """Calculate the required increase in housing allowance (for a particular area and category of property) to make a given percentage of the market 'affordable'"""

    with open(infile) as csvfile:
        reader = csv.DictReader(csvfile)
        filtered_rows = list(filter(lambda row: row["BRMA"].lower() == brma.lower() and row["Category"].lower() == cat.lower(), reader))

        weekly_rents = []
        for row in filtered_rows:
            try:
                weekly_rents.append((float(row["Monthly Rent"])*12)/52.1429)
            except ValueError:
                weekly_rents.append(float(row["Weekly Rent"]))

        sorted_rows = sorted(weekly_rents)

        # Do best to convert if percentage is not given as decimal, e.g. 30
        if percentage > 1:
            percentage = percentage/100

        try:
            required_percentile = sorted_rows[int(len(sorted_rows)*percentage)]
        except IndexError:
            return None

        return required_percentile

def analysis_to_file(infile, outfile):
    boundaries = []

    with open("weekly-lha.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            boundaries.append(row["BRMA"])


    with open(outfile, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow([
            "Broad Rental Market Area",

            # "Total Listings",
            # "Affordable Listings",
            # "(%)",

            # "Total CAT A Listings",
            # "Affordable CAT A Listings",
            # "(%)",

            # "Total CAT B Listings",
            # "Affordable CAT B Listings",
            # "(%)",

            "Two-bed listings",
            "Affordable two-bed listings",
            "Affordable two-bed listings (%)",
            "Current LHA per week",
            "30th percentile rent",
            "LHA/week increase required for 30% affordability",
            "LHA/month increase required for 30% affordability"

            # "Total CAT D Listings",
            # "Affordable CAT D Listings",
            # "(%)",

            # "Total CAT E Listings",
            # "Affordable CAT E Listings",
            # "(%)"
        ])

        for boundary in boundaries:

            print("Analysing {}...".format(boundary))

            # total = total_listings(infile, brma=boundary)
            # affordable = affordable_listings(infile, brma=boundary)
            # percent = round((affordable/total)*100, 2)

            # total_cat_a = total_listings(brma=boundary, cat="CAT A")
            # affordable_cat_a = affordable_listings(brma=boundary, cat="CAT A") if total_cat_a > 0 else 0
            # percent_cat_a = round((affordable_cat_a/total_cat_a)*100, 2) if total_cat_a > 100 else "-"

            # total_cat_b = total_listings(brma=boundary, cat="CAT B")
            # affordable_cat_b = affordable_listings(brma=boundary, cat="CAT B") if total_cat_b > 0 else 0
            # percent_cat_b = round((affordable_cat_b/total_cat_b)*100, 2) if total_cat_b > 100 else "-"

            total_cat_c = total_listings(infile, brma=boundary, cat="CAT C")
            affordable_cat_c = affordable_listings(infile, brma=boundary, cat="CAT C") if total_cat_c > 0 else 0
            percent_cat_c = round((affordable_cat_c/total_cat_c), 4) if total_cat_c >= 100 else "-"
            weekly_LHA_cat_c = float(load_LHA()[boundary]["CAT C"])
            percentile_cat_c = required_LHA_percentile(infile, brma=boundary, cat="CAT C", percentage=0.30)
            percentile_rounded_cat_c = round_up(percentile_cat_c, 2) if percentile_cat_c else "-"
            increase_cat_c = max(round_up(percentile_cat_c - weekly_LHA_cat_c, 2), 0.00) if percentile_cat_c else "-"
            increase_monthly_cat_c = max(round_up((((percentile_cat_c - weekly_LHA_cat_c) * 52.1429) / 12), 2), 0.00) if percentile_cat_c else "-"

            # total_cat_d = total_listings(brma=boundary, cat="CAT D")
            # affordable_cat_d = affordable_listings(brma=boundary, cat="CAT D") if total_cat_d > 0 else 0
            # percent_cat_d = round((affordable_cat_d/total_cat_d)*100, 2) if total_cat_d > 100 else "-"

            # total_cat_e = total_listings(brma=boundary, cat="CAT E")
            # affordable_cat_e = affordable_listings(brma=boundary, cat="CAT E") if total_cat_e > 0 else 0
            # percent_cat_e = round((affordable_cat_e/total_cat_e)*100, 2) if total_cat_e > 100 else "-"


            writer.writerow([
                boundary,

                # total,
                # affordable,
                # percent,

                # total_cat_a,
                # affordable_cat_a,
                # percent_cat_a,
                # required_LHA_increase(infile, brma=boundary, cat="CAT A", percentage=0.3),

                # total_cat_b,
                # affordable_cat_b,
                # percent_cat_b,
                # required_LHA_increase(infile, brma=boundary, cat="CAT B", percentage=0.3),

                total_cat_c,
                affordable_cat_c,
                percent_cat_c,
                weekly_LHA_cat_c,
                percentile_rounded_cat_c,
                increase_cat_c,
                increase_monthly_cat_c,

                # total_cat_d,
                # affordable_cat_d,
                # percent_cat_d,
                # required_LHA_increase(infile, brma=boundary, cat="CAT D", percentage=0.3),

                # total_cat_e,
                # affordable_cat_e,
                # percent_cat_e
                # required_LHA_increase(infile, brma=boundary, cat="CAT E", percentage=0.3),

            ])

    print("Analysis complete")


def create_overview_by_brma(infile, outfile):
    locations = {}

    with open(infile, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=FIELDS)
        next(reader)
        for row in reader:
            try:
                x = locations[row["BRMA"]]
            except KeyError:
                locations[row["BRMA"]] = {}
                locations[row["BRMA"]]["Total"] = 0
                locations[row["BRMA"]]["Affordable"] = 0
                locations[row["BRMA"]]["Both"] = 0
                locations[row["BRMA"]]["Phone"] = 0
                locations[row["BRMA"]]["Email"] = 0
                locations[row["BRMA"]]["Neither"] = 0

            locations[row["BRMA"]]["Total"] += 1

            if row["Affordable"].lower() == "true":
                locations[row["BRMA"]]["Affordable"] += 1

                if row["Contact Email"] and row["Contact Phone"]:
                    locations[row["BRMA"]]["Both"] += 1
                elif row["Contact Phone"]:
                    locations[row["BRMA"]]["Phone"] += 1
                elif row["Contact Email"]:
                    locations[row["BRMA"]]["Email"] += 1
                else:
                    locations[row["BRMA"]]["Neither"] += 1


    with open(outfile, 'w', newline='') as outcsv:
        writer = csv.DictWriter(outcsv, fieldnames=["BRMA", "Total", "Affordable", "Both", "Phone", "Email", "Neither"])
        writer.writeheader()
        for location in locations:
            writer.writerow({
                "BRMA": location,
                "Total": locations[location]["Total"],
                "Affordable": locations[location]["Affordable"],
                "Both": locations[location]["Both"],
                "Phone": locations[location]["Phone"],
                "Email": locations[location]["Email"],
                "Neither": locations[location]["Neither"]
            })

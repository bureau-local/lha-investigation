import csv

FIELDS = [
    "Scraped Date",
    "Listed Date",
    "Lat",
    "Long",
    "Title",
    "Postcode (District)",
    "BRMA",
    "Bedrooms",
    "Category",
    "Weekly Rent",
    "Monthly Rent",
    "Affordable",
    "Primary Listing",
    "Secondary Listing",
    "Source URL",
    "Image URL",
    "Contact Email",
    "Contact Phone",
    "Listing Summary",
    "Listing Text"
]


def load_LHA():
    weekly_LHA = {}
    with open("weekly-lha.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            weekly_LHA[row["BRMA"]] = {
                "CAT A": row["CAT A"],
                "CAT B": row["CAT B"],
                "CAT C": row["CAT C"],
                "CAT D": row["CAT D"],
                "CAT E": row["CAT E"]
            }
    return weekly_LHA

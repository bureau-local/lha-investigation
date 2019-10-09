import csv
from tempfile import NamedTemporaryFile
import shutil
import os.path
from constants import FIELDS

def remove_duplicates(infile, outfile):
    """Attempt to remove all duplicates from a given file

    Note: these are not (only) duplicates that are identical, it should also include
    different listings for the same property (while ignoring listings for different
    properties in the same building)
    """

    def file_loop(reader, writer):
        current_postcode = None
        seen = set()

        next(reader)
        properties_to_check = list(reader)

        writer.writeheader()

        while properties_to_check:

            row = properties_to_check.pop(0)

            postcode = row["Postcode (District)"]

            if current_postcode != postcode:
                current_postcode = postcode
                print("[*] Now removing duplicates for " + current_postcode)

            url_start = row["Source URL"].split("title")[0]
            if url_start not in seen:
                seen.add(url_start)
                writer.writerow(row)
            else:
                continue

    if infile == outfile:
        tempfile = NamedTemporaryFile(mode='w', delete=False, newline='')
        with open(infile, 'r', newline='') as csvfile, tempfile:
            reader = csv.DictReader(csvfile, fieldnames=FIELDS)
            writer = csv.DictWriter(tempfile, fieldnames=FIELDS)
            file_loop(reader, writer)
        shutil.move(tempfile.name, infile)

    else:
        with open(infile, 'r', newline='') as csvfile, open(outfile, 'w', newline='') as outcsv:
            reader = csv.DictReader(csvfile, fieldnames=FIELDS)
            writer = csv.DictWriter(outcsv, fieldnames=FIELDS)
            file_loop(reader, writer)

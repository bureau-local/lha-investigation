import csv
import shapefile
from shapely.geometry import Point, shape
from tempfile import NamedTemporaryFile
import shutil
import os.path
from constants import FIELDS, load_LHA
from OSGridConverter import latlong2grid


class UnregognisedPropertyLocationException(Exception):
    """This exception is raised if a given location cannot be mapped to a BRMA"""
    pass


def load_boundary_files():
    
    boundaries = {}
    shp = shapefile.Reader("BRMA/gb-brma")
    all_shapes = shp.shapes()
    all_records = shp.records()

    for i in range(len(all_shapes)):
        brma_name = all_records[i][0]
        brma_shape = shape(all_shapes[i].__geo_interface__)
        if not brma_shape.is_valid:
            brma_shape = brma_shape.buffer(0) 
        boundaries[brma_name] = brma_shape

    return boundaries


def apply_boundaries(infile, outfile, overwrite=False):

    weekly_LHA = load_LHA()

    #Cache shapefile boundaries
    boundaries = load_boundary_files()

    def get_property_boundary(lat, lon, likely_boundary=None):

        point = latlong2grid(lat, lon)
        point = (point.E, point.N)

        # Check the likely boundary first to save time
        if likely_boundary and Point(point).within(shape(boundaries[likely_boundary])):
            return likely_boundary

        for boundary in boundaries:
            if Point(point).within(boundaries[boundary]):
                return boundary

        raise UnregognisedPropertyLocationException("{},{}".format(lat, lon))

    def file_loop(reader, writer):
        last_boundary = None
        
        writer.writeheader()
        next(reader)
        for row in reader:
            r = row

            if overwrite or not row['BRMA']:
                try:
                    boundary = get_property_boundary(float(row["Lat"]), float(row["Long"]), last_boundary)
                    r["BRMA"] = boundary
                    last_boundary = boundary
                    
                    if row["Category"] != "N/A":

                        try:
                            lha = float(weekly_LHA[boundary][row["Category"]])
                            try:
                                rent = (float(row["Monthly Rent"]) * 12)/52.1429
                            except ValueError:
                                rent = float(row["Weekly Rent"])
                                
                            r["Affordable"] = lha >= rent
                        
                        #If the BRMA is not defined (shouldn't happen)
                        except KeyError:
                            print()                        
                            print("[!] Error with:" + row["BRMA"])
                            print("[!] BRMA name inconsistent across files")
                            print()

                except UnregognisedPropertyLocationException:
                    last_boundary = None
                    coords = row["Lat"] + "," + row["Long"]
                    print("[!] No boundary found for coordinates: " + coords)

            writer.writerow(r)

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

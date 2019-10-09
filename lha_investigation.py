
if __name__ == "__main__":
    import sys
    import traceback
    from datetime import datetime

    # # Scrape information from the web about currently available properties in the UK
    # # based on a list of UK postcodes (optionally starting from a given postcode)
    # try:
    #     from properties import snapshot_properties
    #     print("Collecting properties....")
    #     start_time = datetime.now()
    #     snapshot_properties(outfile="output/test/properties.csv", short_run=False, min_beds=2, max_beds=2)
    #     end_time = datetime.now()
    #     print("Finished running in: {}".format(end_time - start_time))
    # except:
    #     end_time = datetime.now()
    #     traceback.print_exc()
    #     print("Crashed in: {}".format(end_time - start_time))
    #     sys.exit(1)

    # # Remove duplicates from the list of properties we found
    # try:
    #     from cleaner import remove_duplicates
    #     print("Removing duplicates....")
    #     start_time = datetime.now()
    #     remove_duplicates(infile="output/test/properties.csv", outfile="output/test/properties.csv")
    #     end_time = datetime.now()
    #     print("Finished running in: {}".format(end_time - start_time))
    # except:
    #     end_time = datetime.now()
    #     traceback.print_exc()
    #     print("Crashed in: {}".format(end_time - start_time))
    #     sys.exit(1)

    # # Go through each property and check it against the file of BRMAs
    # try:
    #     from boundaries import apply_boundaries
    #     print("Applying boundaries....")
    #     start_time = datetime.now()
    #     apply_boundaries(infile="output/test/properties.csv", outfile="output/test/properties.csv", overwrite=True)
    #     end_time = datetime.now()
    #     print("Finished running in: {}".format(end_time - start_time))
    # except:
    #     end_time = datetime.now()
    #     traceback.print_exc()
    #     print("Crashed in: {}".format(end_time - start_time))
    #     sys.exit(1)

    # # Go through the gathered data, analyse the results
    # # and write the summary figures per BRMA to a file
    # try:
    #     from analysis import analysis_to_file, create_overview_by_brma, total_listings, count_recent_scraped_listings, count_recent_listings
    #     print("Analysing data....")
    #     start_time = datetime.now()
    #     analysis_to_file(infile="output/test/properties.csv", outfile="output/test/analysis.csv")
    #     create_overview_by_brma("output/test/properties.csv", "output/test/by brma.csv")
    #     end_time = datetime.now()
    #     print("Finished running in: {}".format(end_time - start_time))
    # except:
    #     end_time = datetime.now()
    #     traceback.print_exc()
    #     print("Crashed in: {}".format(end_time - start_time))
    #     sys.exit(1)

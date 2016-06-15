import json
import time
import requests
import StringIO
import logging
import sys
from datetime import datetime
from kafka import KafkaProducer
import pupynere as netcdf


def main(controlfile):
    # Read the control file's JSON into an array
    with open(controlfile, "r") as myfile:
        data = json.load(myfile)
    # Initialise logging
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.basicConfig(filename=data["logfile"],
                        format="%(asctime)s %(message)s",
                        level=logging.INFO)
    # Iterate over the floats
    for floats in data["floats"]:
        # Handle null profile number for this float - just get the last profile
        if data["floats"][floats] is None:
            idx = requests.get(data["baseURL"]["url"].
                               replace("{floatID}", str(floats)).
                               rsplit("/", 1)[0])
            if idx.status_code == 404:
                raise Exception("Internet", "Could not load FTP index page")
            data["floats"][floats] = \
                int(idx.content.rsplit("<a href=", 1)[1].
                    split("_")[1].split(".")[0]) - 1
        # Iterate over the profiles for this float
        profile_not_found = False
        while not profile_not_found:
            time.sleep(5)  # A bit of net-etiquette
            r = requests.get(data["baseURL"]["url"]
                             .replace("{floatID}", str(floats))
                             .replace("{profileID}",
                                      str(data["floats"][floats] + 1).
                                      zfill(data["baseURL"]["padProfileID"])))
            if r.status_code == 404:
                profile_not_found = True
            else:
                # Shift the request result to a StringIO buffer
                try:
                    f = netcdf.netcdf_file(StringIO.StringIO(r.content), "r")
                    # Add some attributes we want to have when we get to Erddap
                    setattr(f, "FLOAT_WMO_ID", str(floats))
                    setattr(f, "FLOAT_PROFILE_SEQUENCE_NUMBER",
                            str(data["floats"][floats] + 1))
                    setattr(f, "SOURCE_URL", data["baseURL"]["url"]
                            .replace("{floatID}", str(floats))
                            .replace("{profileID}", str(data["floats"][floats] + 1)
                                     .zfill(data["baseURL"]["padProfileID"])))
                    setattr(f, "LAST_MODIFIED_DATETIME",
                            datetime.strftime(datetime.strptime(r.headers["Last-Modified"],
                                                                "%a, %d %b %Y %H:%M:%S %Z"),
                                              "%Y-%m-%d %H:%M:%S"))
                    f.close()
                    logging.info("%s %s %s %s", f.FLOAT_WMO_ID,
                                 f.FLOAT_PROFILE_SEQUENCE_NUMBER, f.SOURCE_URL,
                                 f.LAST_MODIFIED_DATETIME)
                    #
                    # ToDo: Write to Kafka...
                    #
                except AssertionError:
                    pass
                data["floats"][floats] += 1
    # Save the new state of the control file
    with open(controlfile, "w") as outfile:
        json.dump(data, outfile, indent=4)
    return


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise Exception("Invocation", "Wrong number of input arguments...")
    if sys.argv[1].lower() != "-c":
        raise Exception("Invocation", "No control file flag specified...")
    main(sys.argv[2])

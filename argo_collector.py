import json
import time
import requests
import base64
import logging
import sys
from datetime import datetime
from scipy.io import netcdf
from pykafka import KafkaClient
import parsedatetime as pdt
import argparse


def commit(controlfile,data):
    # Save the new state of the control file
    with open(controlfile, "w") as outfile:
        json.dump(data, outfile, indent=4)

def format_url(base_url,floats,index,quality,pad):
    return base_url.replace("{floatID}",
              str(floats)).replace("{profileID}",
              str(index).zfill(pad)).replace("{quality}",str(quality))

def main(controlfile):
    # Read the control file's JSON into an array
    with open(controlfile, "r") as myfile:
        data = json.load(myfile)
    base_url = data["baseURL"]["url"]
    pad = data["baseURL"]["padProfileID"]
    kafka_hosts = data["kafka"]["hosts"]
    kafka_topic = data["kafka"]["topic"]

    kafka_client = KafkaClient(hosts=kafka_hosts)
    topic = kafka_client.topics[kafka_topic.encode("utf-8")]
    # Initialise logging
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.basicConfig(filename=data["logfile"],
                        format="%(asctime)s %(message)s",
                        level=logging.INFO)
    # Iterate over the floats
    for floats in data["floats"]:
        # Handle null profile number for this float - just get the last profile
        if data["floats"][floats] is None:
            idx = requests.get(base_url.
                               replace("{floatID}", str(floats)).
                               rsplit("/", 1)[0])
            if idx.status_code == 404:
                raise Exception("Internet", "Could not load FTP index page")
            data["floats"][floats] = \
                int(idx.content.rsplit("<a href=", 1)[1].
                    split("_")[1].split(".")[0]) - 1
        # Iterate over the profiles for this float
        profile_found = True
        while profile_found:
            sequence_no = data["floats"][floats] + 1
            profile_found = False
            profile_quality = None
            for quality in ["D","R"]:
              url = format_url(base_url,floats,sequence_no,quality,pad)
              with open('tmp.nc', 'wb') as handle: 
                   r = requests.get(url, stream=True)
                   if r.status_code == 404:
                       continue
                   if not r.ok:
                       logging.info("Problem with %s",url)
                       continue
                   profile_found = True
                   profile_quality = quality
                   for block in r.iter_content(1024):
                     handle.write(block)
                   break

            if profile_found:
                try:
                    last_modified = datetime.strftime(
                         datetime.strptime(
                             r.headers["Last-Modified"],
                              "%a, %d %b %Y %H:%M:%S %Z"),
                              "%Y-%m-%dT%H:%M:%SZ")
                    f = netcdf.netcdf_file("tmp.nc", "rw")
                    # Add some attributes we want to have when we get to Erddap
                    setattr(f, "FLOAT_WMO_ID", str(floats))
                    setattr(f, "FLOAT_PROFILE_SEQUENCE_NUMBER",
                            str(sequence_no))
                    setattr(f, "SOURCE_URL",url)
                    setattr(f, "QUALITY",quality)
                    setattr(f, "LAST_MODIFIED_DATETIME", last_modified)
                    f.close()
                    logging.info("%s %s %s %s %s", f.FLOAT_WMO_ID,
                                 f.FLOAT_PROFILE_SEQUENCE_NUMBER, f.SOURCE_URL,
                                 f.LAST_MODIFIED_DATETIME,f.QUALITY)
                    with open("tmp.nc", "rb") as nc_file:
                        nc_encoded = base64.b64encode(nc_file.read())
                    outdata = {"source_url": url, 
                               "last_modified": last_modified,
                               "netcdf": nc_encoded,
                               "float": floats,
                               "quality": profile_quality,
                               "sequence_no": sequence_no}

                    with topic.get_sync_producer() as producer:
                        producer.produce(json.dumps(outdata).encode("utf-8"))
                    print(url)
                except AssertionError:
                    pass
                data["floats"][floats] += 1
                commit(controlfile,data)

            time.sleep(5)  # A bit of net-etiquette
    return


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise Exception("Invocation", "Wrong number of input arguments...")
    if sys.argv[1].lower() != "-c":
        raise Exception("Invocation", "No control file flag specified...")
    main(sys.argv[2])

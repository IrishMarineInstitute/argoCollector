import json
import time
import requests
import base64
import logging
import sys
from datetime import datetime
import parsedatetime as pdt
import os
from tempfile import mkstemp
import pystache

class HttpModule:

  def __init__(self):
    logging.getLogger("requests").setLevel(logging.WARNING)

  def format_url(self,base_url,floats,index,quality,pad):
      return pystache.render(base_url,{
             "floatID": floats,
             "profileID": str(index).zfill(pad),
             "quality": quality
          })

  def produce(self,data):
    base_url = data["http"]["url"]
    pad = data["http"]["padProfileID"]
    fd, temp_nc = mkstemp()
    os.close(fd)
    try:
      # Iterate over the floats
      for floats in data["floats"]:
        # Handle null profile number for this float - just get the last profile
        if data["floats"][floats] is None:
            url = pystache.render(base_url, {"floatID": floats} ).rsplit("/", 1)[0]
            idx = requests.get(url)
            if idx.status_code == 404:
                raise Exception("Internet", "Could not load FTP index {0}".format(url))
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
              url = self.format_url(base_url,floats,sequence_no,quality,pad)
              with open(temp_nc, 'wb') as handle: 
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

                    with open(temp_nc, "rb") as nc_file:
                        nc_encoded = base64.b64encode(nc_file.read())
                    result = {"source_url": url, 
                               "last_modified": last_modified,
                               "netcdf": nc_encoded,
                               "float": floats,
                               "quality": profile_quality,
                               "sequence_no": sequence_no}

                    data["floats"][floats] += 1
                    yield (data, result)
                except AssertionError:
                    pass
            for i in range(5*10):
               time.sleep(0.1)

    finally:
        try:
            os.remove(temp_nc)
        except OSError:
            pass 

def create_instance(config):
   return HttpModule()

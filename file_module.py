import json
import base64
import os
import pystache

class FileModule:
  target = None
  def __init__(self,config):
    self.target = config["file"]["target"]

  def publish(self,data):
     data["basename"] = os.path.basename(data["source_url"])
     target = pystache.render(self.target,data)
     directory = os.path.dirname(target)
     if not os.path.exists(directory):
         os.makedirs(directory)
     with open(target, 'wb') as handle: 
          handle.write(base64.b64decode(data["netcdf"]))

def create_instance(config):
   return FileModule(config)


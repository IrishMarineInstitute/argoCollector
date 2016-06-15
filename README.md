# argoFTPCollector
Collect Argo float profiles as NetCDF from the Data Assembly Centre and push to Erddap via Kafka

## Requirements
- Developed on Python 2.7
- Dependencies are detailied in the requirements.txt file
  - netcdf4==1.2.4
  - pykafka==2.3.1
  - pupynere==1.0.15

## Invocation
python argoFTPCollector.py -c /path/to/controlfile.json

## Control File
The control file is a JSON file which specifies various parameters
- logfile
- baseURL
  -  url
  -  padProfileID
- floats
  - floatID
  - last profile ID processed
- kafka
  - topic
  - server

An example control file is given below
```javascript
{
    "logfile": "c:/users/aleadbetter/documents/python/argo_log.txt", 
    "baseURL": {
        "url": "http://www.usgodae.org/ftp/outgoing/argo/dac/bodc/{floatID}/profiles/R{floatID}_{profileID}.nc", 
        "padProfileID": 3
    }, 
    "floats": {
        "6900444": 185, 
        "6900658": 185
    }, 
    "kafka": {
        "topic": "argo", 
        "server": "127.0.0"
    }
}
```

# argoCollector
Collect Argo float profiles as NetCDF from the Global Data Assembly Centre and push to Erddap via Kafka

## Requirements
- Developed on Python 2.7
- Dependencies are detailied in the [requirements.txt](https://github.com/IrishMarineInstitute/argoFTPCollector/blob/master/requirements.txt) file
  - netcdf4==1.2.4
  - pykafka==2.3.1
  - pupynere==1.0.15

## Invocation
python argoFTPCollector.py -c /path/to/controlfile.json

## Control File
The control file is a JSON file which specifies various parameters
- logfile - A string giving the full path to which the app will log
- baseURL - a JSON object
  -  url - A string giving the GDAC URL pattern to poll data from {floatID} and {profileID} will be replaced in the app
  -  padProfileID - An integer giving how many digits to pad the profile ID out to (i.e. for a pattern of 001, 002, 003 use 3)
- floats - A JSON object of multiple "floatID": lastProfileIDProcessed key-value-pairs
  - floatID - A string identifying this float
  - lastProfileIDProcessed - An integer giving the last profile processed for this float. Use null to begin with the last profile. received by the GDAC. Use 0 to start from the first profile received for a given float
- kafka - a JSON object
  - topic - a string giving the topic to send messages to
  - server - a string identifying the server on which the topic is hosted

An example control file is given below, and [here](https://github.com/IrishMarineInstitute/argoFTPCollector/blob/master/argo.json)
```javascript
{
    "logfile": "~/logs/argo_log.txt", 
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

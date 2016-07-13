# argoCollector
Collect Argo float profiles as NetCDF from the Global Data Assembly Centre and push to Erddap via Kafka

## Requirements
- Developed on Python 2.7
- Dependencies are detailied in the [requirements.txt](https://github.com/IrishMarineInstitute/argoCollector/blob/master/requirements.txt) file

## Invocation

to store data from http to kafka:

    ./argo_collector.py -c argo.json --input http --output kafka

to store data from kafka to the file system:

    ./argo_collector.py -c argo.json --input http --output file --no-commit

or to store data from http to the file system:

    ./argo_collector.py -c argo.json --input http --output file --no-commit

## Control File
The control file is a JSON file which specifies various parameters
- logfile - A string giving the full path to which the app will log
- http - a JSON object
  -  url - A string giving the GDAC URL pattern to poll data from {{floatID}} and {{quality}} and {{profileID}} will be replaced in the app
  -  padProfileID - An integer giving how many digits to pad the profile ID out to (i.e. for a pattern of 001, 002, 003 use 3)
- file - a JSON object
  -  target - A string giving the target file path, {{float}} and {{basename}} will be replaced by the app
- kafka - a JSON object
  - topic - a string giving the topic to send messages to
  - hosts - a comma separated string of server:port kafka servers
  - consumer_group - a string so used to commit offsets in kafka
- floats - A JSON object of multiple "floatID": lastProfileIDProcessed key-value-pairs
  - floatID - A string identifying this float
  - lastProfileIDProcessed - An integer giving the last profile processed for this float. Use null to begin with the last profile. received by the GDAC. Use 0 to start from the first profile received for a given float

An example control file is given below, and [here](https://github.com/IrishMarineInstitute/argoFTPCollector/blob/master/argo.json)
```javascript
{
    "logfile": "~/logs/argo_log.txt", 
    "http": {
        "url": "http://www.usgodae.org/ftp/outgoing/argo/dac/bodc/{{floatID}}/profiles/{{quality}}{{floatID}}_{{profileID}}.nc", 
        "padProfileID": 3
    }, 
    "floats": {
        "6900444": 185, 
        "6900658": 185
    }, 
    "kafka": {
        "topic": "argo", 
        "hosts": "127.0.0.1:9092",
        "consumer_group": "kafka"
    }
}
```

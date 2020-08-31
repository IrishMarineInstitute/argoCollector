# Standard Operating Procedure

## Adding a new float

1. PI sends email to data management team listing new float number/numbers eg. 
  Please be advised that argo float 1234567 (IMEI 123456789012234567890) has been deployed this am.
2. Data management run the following commands on erddap3 server
```
/opt/argos/add_float 1234567
/opt/argos/update_floats
cd /opt/argos
git commit -a -n 'added float 1234567'
git push
```
3. Once float has surfaced, data should appear in [ERDDAP](https://erddap3.marine.ie?erddap/tabledap/argoFloats.html)
4. Data is collected on an ongoing basis due to a cron job running on erddap3 server.
5. The log file on erddap3 server can be used in diagnosing data collection problems `/home/dmuser/update_floats.log`


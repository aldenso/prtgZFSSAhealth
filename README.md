# prtgZFSSAhealth

PRTG Python Advanced script to get health status from ZFSSA using Rest service.

## Dependencies

request (use pip and the [requirements.txt](requirements.txt) file provided) and paepy (included in prtg).

It is a good idea to get pip for your prtg server, so use any of the following links in how to get pip:

* <https://packaging.python.org/installing/#requirements-for-installing-packages>
* <https://github.com/BurntSushi/nfldb/wiki/Python-&-pip-Windows-installation>

Open powershell with privileges.

```text
Start-Process powershell -Verb runAs
```

Then install the requirements.

```text
& 'C:\Program Files (x86)\PRTG Network Monitor\Python34\Scripts\pip.exe' install -r requirements.txt
```

### Usage

Copy your script to "\Custom Sensors\python" directory (example: *C:\Program Files (x86)\PRTG Network Monitor\Custom Sensors\python*).

Include your sensor as **Python Script Advanced**.

In **Additional Parameters** tab, use some pattern like the next examples:

for Standalone:

    --host <zfssanode1> --username <username> --password <password>

for Cluster:

    --host <zfssanode1,zfssanode2> --username <username> --password <password>

### Notes

* You need a ZFSSA user with minimum privileges to retrieve data from the system.
* The Rest service must be enabled in the ZFSSA.
* Be careful about the sensor frequency, the pools takes some time to return a response depending on you configuration.
* You need Administrator privileges in the PRTG server to copy the scripts, install pip and the packages with pip.
* Copy the file **prtg.custom.yesno.problems.ovl** to the custom lookups directory "\lookups\custom" (example: *C:\Program Files (x86)\PRTG Network Monitor\lookups\custom*), for more info check <https://www.paessler.com/manuals/prtg/define_lookups>.

### Available status at the moment

* System problems.
* Pools status
* Pools Usage Percent (Warning: 85, Error: 90 )
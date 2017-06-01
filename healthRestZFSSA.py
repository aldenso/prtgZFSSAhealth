#!/usr/bin/python
# -*- coding: utf-8 -*-
# @CreateTime: May 9, 2017 10:09 AM 
# @Author: Aldo Sotolongo 
# @Contact: aldenso@gmail.com 
# @Last Modified By: Aldo Sotolongo
# @Last Modified Time: May 20, 2017 11:50 AM
# @Description: prtg script to monitor zfs pools status, pool usage percent
# and problems in a cluster or standalone ZFSSA.
# Usage: on additional parameters for sensor you can use:
# --hosts <zfssa1_ip,zfssa2_ip> --username <username> --password <password>

import sys
import json
import getopt
import requests
# from requests.packages.urllib3.exceptions import InsecureRequestWarning  # for older requests
from urllib3.exceptions import InsecureRequestWarning
from paepy.ChannelDefinition import CustomSensorResult

# to disable warning
# InsecureRequestWarning: Unverified HTTPS request is being made.
# Adding certificate verification is strongly advised. See:
# https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

###############################################################################
# Holders for PRTG additional parameters
###############################################################################
HOSTS = ""
USERNAME = ""
PASSWORD = ""

###############################################################################
# Get PRTG Additional Parameters
###############################################################################
PRTGPARAMS = json.loads(sys.argv[1:][0])
PARAMS = str.split(PRTGPARAMS["params"])
OPTS, ARGS = getopt.getopt(PARAMS, "h:u:p",
                           ["hosts=", "username=", "password=", ])
for opt, arg in OPTS:
    if opt in ("-h", "--hosts"):
        HOSTS = arg.split(",")
    elif opt in ("-u", "--username"):
        USERNAME = str(arg)
    elif opt in ("-p", "--password"):
        PASSWORD = str(arg)

###############################################################################
# constants
###############################################################################
ZAUTH = (USERNAME, PASSWORD)
HEADER = {"Content-Type": "application/json"}
TIMEOUT = 35
VALUELOOKUP = "prtg.custom.yesno.problems"

###############################################################################
# return channels
###############################################################################
channels = CustomSensorResult()


###############################################################################
# functions
###############################################################################
def checkpools(host):
    """Check Pools status and usage."""
    try:
        req = requests.get(url="https://{}:215/api/storage/v1/pools"
                           .format(host),
                           auth=ZAUTH,
                           verify=False,
                           headers=HEADER,
                           timeout=TIMEOUT)
        j = json.loads(req.text)
        req.close()
        for pools in j.values():
            for pool in pools:
                if pool['status'] != "exported":
                    poolpct = (pool['usage']['usage_total'] /
                               pool['usage']['total'] *
                               100)
                    channels.add_channel(channel_name="{} Usage Percent"
                                         .format(pool['name']),
                                         value=float(format(poolpct, '.2f')),
                                         is_float=True,
                                         unit="Percent",
                                         limit_max_warning=85,
                                         limit_max_error=90,
                                         is_limit_mode=1)
                    if pool['status'] == "online":
                        channels.add_channel(channel_name="{} Status"
                                             .format(pool['name']),
                                             value=0,
                                             value_lookup=VALUELOOKUP,
                                             unit="Custom")
                    else:
                        channels.add_channel(channel_name="{} Status"
                                             .format(pool['name']),
                                             value=1,
                                             value_lookup=VALUELOOKUP,
                                             unit="Custom")
    except Exception:
        if channels.sensor_message == "OK":
            channels.sensor_message = "| can't check pools in {} |".format(host)
        else:
            channels.sensor_message += "| can't check pools in {} |".format(host)


def checkproblems(host, key):
    """Check for problems in ZFSSA."""
    primary = bool(key == 0)
    try:
        req = requests.get(url="https://{}:215/api/problem/v1/problems"
                           .format(host),
                           auth=ZAUTH,
                           verify=False,
                           headers=HEADER,
                           timeout=TIMEOUT)
        j = json.loads(req.text)
        req.close()

        problemfound = 0
        for problems in j.values():
            for problem in problems:
                problemfound += 1
                message = ("| Description: {} |"
                           .format(problem["description"]))
                if message not in channels.sensor_message:
                    if channels.sensor_message == "OK":
                        channels.sensor_message = message
                    else:
                        channels.sensor_message += message
        if problemfound != 0:
            channels.add_channel(channel_name="zfssa problems {}"
                                 .format(host),
                                 value=1,
                                 value_lookup=VALUELOOKUP,
                                 unit="Custom",
                                 primary_channel=primary)
        else:
            channels.add_channel(channel_name="zfssa problems {}"
                                 .format(host),
                                 value=0,
                                 value_lookup=VALUELOOKUP,
                                 unit="Custom",
                                 primary_channel=primary)
    except Exception:
        if channels.sensor_message == "OK":
            channels.sensor_message = "| can't check problems in {} |".format(host)
        else:
            channels.sensor_message += "| can't check problems in {} |".format(host)


def main():
    for key, host in enumerate(HOSTS):
        checkproblems(host, key)
        checkpools(host)
    if not channels.channels:
        channels.add_error("No channels can be retrieved")
    # Make sure return text max length is 2000 characters
    if len(channels.sensor_message) > 2000:
        channels.sensor_message = channels.sensor_message[:2000]
    print(channels.get_json_result())

if __name__ == "__main__":
    main()

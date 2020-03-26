import api_processor
import requests
import sys
import json

logfile = "call_api"


def call_api(url, method, payload, headers):
    response = ""
    # noinspection PyBroadException
    try:
        if method == "post":
            response = requests.post(url, headers=headers, json=payload, verify=False)
            api_processor.libhandler.writelog(logfile, f"{url} Api call:{response.text}")
            return response.json()

        elif method == "get":
            response = requests.get(url, headers=headers, json=payload, verify=False)
            api_processor.libhandler.writelog(logfile, f"{url} Api call:{response.text}")
            return response.json()

    except:
        etype = sys.exc_info()[0]
        evalue = sys.exc_info()[1]
        api_processor.libhandler.log_error_detailed(logfile, f"API Error: {etype} - {evalue}")


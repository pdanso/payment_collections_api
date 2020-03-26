import api_processor
import requests
import sys

logfile = "call_api"


def call_api(url, method, modul, action, payload, api_version="v2"):
    response = ""
    # noinspection PyBroadException
    try:
        if method == "post":
            url = f"{url}/{api_version}/{modul}/{action}/{payload}"
            response = requests.post(url, verify=False, timeout=10)
            api_processor.libhandler.writelog(logfile, f"{action} Api call:{response.text}")
            return response.text

        elif method == "get":
            url = f"{url}/{api_version}/{modul}/{action}/{payload}"
            response = requests.get(url, verify=False, timeout=10)
            api_processor.libhandler.writelog(logfile, f"{action} Api call:{response.text}")
            return response.text

        elif method == "json":
            url = f"{url}/{api_version}/{modul}/{action}/"
            response = requests.post(url, json=payload, verify=False)
            api_processor.libhandler.writelog(logfile, f"{action} Api call:{response.json()}")
            return response.json()

    except:
        etype = sys.exc_info()[0]
        evalue = sys.exc_info()[1]
        api_processor.libhandler.log_error_detailed(logfile, f"API Error: {etype} - {evalue}")

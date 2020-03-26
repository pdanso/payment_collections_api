import api_processor
import requests
import sys

logfile = "api_post"


def api_post(url, payload, package, modul, action, api_version="v2"):
        response = ""
        # noinspection PyBroadException
        try:
            url = f"{url}/{package}/{api_version}/{modul}/{action}/{payload}"
            response = requests.post(url, verify=False, timeout=10)
            api_processor.libhandler.writelog(logfile, f"{action} Api call:{response.text}")

        except:
            etype = sys.exc_info()[0]
            evalue = sys.exc_info()[1]
            api_processor.libhandler.log_error_detailed(logfile, f"API Error: {etype} - {evalue}")

        return response.text

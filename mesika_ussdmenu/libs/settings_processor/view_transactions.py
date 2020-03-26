import settings_processor
import core_processor

logfile = "view_transactions"


def view_transactions(request, data, url, goback_message, modul):
    data = ""
    message = "You will receive the last 5 transactions you performed via SMS shortly."
    menu_response = core_processor.goto_start.goto_start(request, message, data, goback_message)
    settings_processor.libhandler.writelog(logfile, f"Message: {message}")

    # payload = {"msisdn": self.msisdn}
    # response = api_processor.call_api(url, "get", modul, "viewTransactions", payload")
    # status = response['status']

    return menu_response

import settings_processor
import core_processor

logfile = "view_transactions"


def view_transactions(data, url, goback_message, modul):
    data = ""
    message = "You will receive the last 5 transactions you performed via SMS shortly."
    menu_response = core_processor.goto_start.goto_start(message, data, goback_message)
    settings_processor.libhandler.writelog(logfile, f"Message: {message}")

    # payload = {"msisdn": self.msisdn}
    # response = self.core_processor.call_api(url, payload, "cowrybank", "getCustomerProfile")
    # status = response['status']

    return menu_response

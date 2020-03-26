import settings_processor
import core_processor
import api_processor

logfile = "view_commissions"


def view_commissions(request,data, url, goback_message, modul):
    data = ""
    message = "You will receive your last 5 commissions earned via SMS shortly."
    menu_response = core_processor.goto_start.goto_start(request, message, data, goback_message)
    settings_processor.libhandler.writelog(logfile, f"Message: {message}")

    # payload = {"msisdn": self.msisdn}
    # response = api_processor.call_api(url, "get", modul, action, payload)
    # status = response['status']

    return menu_response
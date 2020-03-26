import settings_processor
import core_processor

logfile = "view_profile"


def view_profile(data, url, goback_message, modul):
    # payload = {"msisdn": self.msisdn}
    # response = self.core_processor.call_api(url, payload, "cowrybank", "getCustomerProfile")
    # status = response['status']

    status = 200

    if status == 200:
        message = "Your profile will be sent to you shortly."
        menu_response = core_processor.goto_start.goto_start(message, data, goback_message)
        settings_processor.libhandler.writelog(logfile, f"Message: {message}")

    else:
        message = "Your profile cannot be viewed right now!."
        menu_response = core_processor.goto_start.goto_start(message, data, goback_message)
        settings_processor.libhandler.writelog(logfile, f"Message: {message}")

    return menu_response

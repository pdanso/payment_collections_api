import settings_processor
import core_processor

logfile = "view_profile"


def view_profile(request, data, url, goback_message, modul):
    # payload = {"msisdn": self.msisdn}
    # response = api_processor.call_api(url, "get", modul, "getCustomerProfile", payload)
    # status = response['status']

    status = 200

    if status == 200:
        #<list the profile here>
        message = "Your profile will be sent to you shortly."
        menu_response = core_processor.goto_start.goto_start(request, message, data, goback_message)
        settings_processor.libhandler.writelog(logfile, f"Message: {message}")

    else:
        message = "Your profile cannot be viewed right now!."
        menu_response = core_processor.goto_start.goto_start(request, message, data, goback_message)
        settings_processor.libhandler.writelog(logfile, f"Message: {message}")

    return menu_response

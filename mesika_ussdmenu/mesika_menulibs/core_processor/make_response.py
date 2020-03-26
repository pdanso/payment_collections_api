import core_processor

logfile = "make_response"


def make_response(request, mode, message):
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = mode
    userdata = request.GET["userdata"]

    ussd_message = message.title()  # capitalises first letter of every word
    menu_response = f"{networkid}|{mode}|{msisdn}|{sessionid}|{ussd_message}"
    core_processor.libhandler.writelog(logfile, f"Message: {menu_response}")

    return menu_response


def notitle_response(request, mode, message):
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = mode
    userdata = request.GET["userdata"]

    menu_response = f"{networkid}|{mode}|{msisdn}|{sessionid}|{message}"
    core_processor.libhandler.writelog(logfile, f"Message: {menu_response}")

    return menu_response


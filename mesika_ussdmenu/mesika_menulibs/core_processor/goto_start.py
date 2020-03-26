import core_processor
import session_processor

logfile = "goto_start"


def goto_start(request, msg, data, goback_message):
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    message = f"{msg}^{goback_message}"
    menu_response = core_processor.make_response.make_response(request, "more", message)
    session_processor.store_session.store_session(msisdn, sessionid, networkid, f"GOBACK|{data}")
    core_processor.libhandler.writelog(logfile, f"Message: {menu_response}")

    return menu_response


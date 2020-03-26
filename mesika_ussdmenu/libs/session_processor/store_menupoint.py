import session_processor

logfile = "menu_point"


def store_menupoint(request, content, data):
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    """Store session data"""

    session_processor.store_session.store_session(msisdn, sessionid, networkid, f"{content}|{data}")
    session_processor.libhandler.writelog(logfile, f"Content: {content}")

    return

import session_processor

logfile = "menu_point"


def store_menupoint(content, data):
    """Store session data"""

    session_processor.store_session.store_session(session_processor.msisdn, session_processor.sessionid,
                                                  session_processor.networkid, f"{content}|{data}")

    return

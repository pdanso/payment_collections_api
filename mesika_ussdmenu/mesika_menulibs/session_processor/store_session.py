import session_processor

logfile = "store_session"


def store_session(msisdn, sessionid, networkid, content):
    """Store session data"""

    session_name = f"USESSION_{msisdn}_{sessionid}_{networkid}"
    session_processor.session_cache.store_in_cache(session_name, content)
    session_processor.libhandler.writelog(logfile, f"{session_name}")
    return


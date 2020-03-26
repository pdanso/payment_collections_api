import session_processor

logfile = "last_step"


def get_last_step(msisdn, sessionid, networkid):
    """Get the last point in the transaction tree"""

    session_name = f"USESSION_{msisdn}_{sessionid}_{networkid}"
    step = session_processor.session_cache.get_cache_value(session_name)
    session_processor.libhandler.writelog(logfile, f"Last Step: {step}")
    return step


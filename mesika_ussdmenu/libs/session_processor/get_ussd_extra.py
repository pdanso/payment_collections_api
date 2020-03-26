import session_processor

logfile = "get_extra"


def get_ussd_extra(stored_string):
    """ Returns the stored strings after a USSD command """
    # extra = (stored_string.split("|")[1]).lstrip(' \t\n\r')

    data_len = len(stored_string)
    extra = (stored_string[7:data_len]).lstrip(' \t\n\r')
    extra = extra.rstrip(' \t\n\r')
    session_processor.libhandler.writelog(logfile, f"Returning extra [{extra}] from {stored_string}")

    return extra


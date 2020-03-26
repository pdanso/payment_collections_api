from mesika_libs.logging import Logger

__all__ = ['goto_start',
           'make_response',
           'unknown_option',
           'date_validation',
           'disable_service']

""" Initialising the logger """
host = "127.0.0.1"
port = 24777
libhandler = Logger("ussd_core_processor", host, port)

menu_response = ""
goback_message = ""
userdata = ""
sessionid = ""
networkid = ""
bank_id = ""
bank_code = ""
modul = ""
msisdn = ""
mode = ""

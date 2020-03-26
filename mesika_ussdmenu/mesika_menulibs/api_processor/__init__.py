from mesika_libs.logging import Logger

__all__ = ['api_get', 'api_json', 'api_post']

""" Initialising the logger """
host = "10.85.85.80"
port = 24777
libhandler = Logger("ussd_api_calls", host, port)

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

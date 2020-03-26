from mesika_libs.logging import Logger
from mesika_libs.Caching import Cacher

__all__ = ['get_alph_id', 'get_num_id', 'get_secret_id']

""" Initialising the logger """
host = "127.0.0.1"
port = 24777
libhandler = Logger("ussd_transaction_id", host, port)

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



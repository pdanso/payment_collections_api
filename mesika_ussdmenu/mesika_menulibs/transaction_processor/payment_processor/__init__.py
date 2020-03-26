from mesika_libs.logging import Logger
from mesika_libs.Caching import Cacher

__all__ = ['payment_methods', 'bank', 'momo', 'loansmomo',]

""" Initialising the logger """
host = "127.0.0.1"
port = 24777
libhandler = Logger("ussd_payment_processor", host, port)

""" Initialising the cacher """
session_cache = Cacher()

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



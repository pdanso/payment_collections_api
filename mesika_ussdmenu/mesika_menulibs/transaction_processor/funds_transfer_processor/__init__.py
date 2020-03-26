from mesika_libs.logging import Logger
from mesika_libs.Caching import Cacher

__all__ = ['gip', 'internal', 'funds_transfer']

""" Initialising the logger """
host = "logmaster"
port = 24777
#libhandler = Logger("ussd_funds_transfer", host, port)
libhandler = Logger("Progressive", host, port)

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



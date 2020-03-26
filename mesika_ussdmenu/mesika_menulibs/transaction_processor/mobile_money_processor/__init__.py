from mesika_libs.logging import Logger
from mesika_libs.Caching import Cacher

__all__ = ['bankwallet','bank_wallet', 'wallet_bank', 'momo']

""" Initialising the logger """
host = "logmaster.mesika.org"
port = 24777
libhandler = Logger("ussd_momo_wallet", host, port)

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



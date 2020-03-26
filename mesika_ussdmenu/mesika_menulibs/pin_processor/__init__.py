from mesika_libs.logging import Logger
from mesika_libs.Caching import Cacher

__all__ = ['pin_reset']

""" Initialising the logger """
host = "logmaster.mesika.org"
port = 24777
libhandler = Logger("Progressive", host, port)

""" Initialising the cacher """
session_cache = Cacher()

menu_response = ""
goback_message = ""
userdata = ""
sessionid = "156983"
networkid = "459862"
bank_id = ""
bank_code = ""
modul = ""
msisdn = "233504169784"
mode = ""



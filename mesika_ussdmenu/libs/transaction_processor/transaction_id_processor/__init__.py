from mesika_libs.logging import Logger
from mesika_libs.Caching import Cacher

__all__ = ['get_trxid']

""" Initialising the logger """
host = "127.0.0.1"
port = 24777
libhandler = Logger("ussd_transaction_id", host, port)

bank_code = ""

''' connect from json file'''
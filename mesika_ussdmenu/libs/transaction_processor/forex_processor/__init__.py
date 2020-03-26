from mesika_libs.logging import Logger
from mesika_libs.Caching import Cacher

__all__ = ['forex']

""" Initialising the logger """
host = "127.0.0.1"
port = 24777
libhandler = Logger("ussd_forex_processor", host, port)

""" Initialising the cacher """
session_cache = Cacher()
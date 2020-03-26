from mesika_libs.logging import Logger
from mesika_libs.Caching import Cacher

__all__ = ['store_session',
           'store_menupoint',
           'get_last_step',
           'get_ussd_extra']

""" Initialising the logger """
host = "127.0.0.1"
port = 24777
libhandler = Logger("ussd_sesssion_processor", host, port)

""" Initialising the cacher """
session_cache = Cacher()


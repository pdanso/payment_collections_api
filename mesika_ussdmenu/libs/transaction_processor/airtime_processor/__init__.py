from mesika_libs.logging import Logger
from mesika_libs.Caching import Cacher

__all__ = ['airtime']

""" Initialising the logger """
host = "127.0.0.1"
port = 24777
libhandler = Logger("ussd_airtime_processor", host, port)
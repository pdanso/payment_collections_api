from mesika_libs.logging import Logger
from mesika_libs.Caching import Cacher

__all__ = ['full_signup', 'partial_signup']

""" Initialising the logger """
host = "127.0.0.1"
port = 24777
libhandler = Logger("ussd_selfsignup_processor", host, port)

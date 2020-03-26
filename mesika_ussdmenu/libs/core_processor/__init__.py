from mesika_libs.logging import Logger

__all__ = ['make_response',
           'goto_start',
           'unknown_option',
           'date_validation',
           'disable_service']

""" Initialising the logger """
host = "127.0.0.1"
port = 24777
libhandler = Logger("ussd_core_processor", host, port)

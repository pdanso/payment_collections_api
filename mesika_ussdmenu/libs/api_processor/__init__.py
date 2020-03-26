from mesika_libs.logging import Logger

__all__ = ['call_api']

""" Initialising the logger """
host = "127.0.0.1"
port = 24777
libhandler = Logger("ussd_api_processor", host, port)
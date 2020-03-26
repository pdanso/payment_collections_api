from mesika_libs.logging import Logger

__all__ = ['agent_collections', 'magnet_agent', 'magnet_customer', 'mobile_banking']

""" Initialising the logger """
host = "127.0.0.1"
port = 24777
libhandler = Logger("ussd_product_views", host, port)
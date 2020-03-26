"""
Django settings for authenticator project.

"""
import os
import sys
import socket

current_dir = os.getcwd()
current_os = sys.platform

host = socket.gethostname()

production_host = ["api2.mesika.org"]
uat_host = []

if host in uat_host:
    from uat_settings.settings import *
elif host in production_host:
    from production_settings.settings import *
else:
    from development_settings.settings import *



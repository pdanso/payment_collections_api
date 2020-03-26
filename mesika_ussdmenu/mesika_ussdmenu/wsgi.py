"""
WSGI config for mesika_ussdmenu project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
import sys

sys.path.append("/client_deploy/non_rfi/cem/production/ussdmenu/mesika_ussdmenu/mesika_menulibs/")
#sys.path.append("/legacy_demo/2.0/mesika_ussdmenu/libs/")

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mesika_ussdmenu.settings")

application = get_wsgi_application()

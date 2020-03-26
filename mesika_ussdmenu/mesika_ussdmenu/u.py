"""mesika_ussdmenu URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from menuhub.magnet_agent import view as agentview
from menuhub.herbaltech import view as herbaltechview
from menuhub.herbalagent import view as herbalview
from menuhub.magnet_cust import view as custtechview
from menuhub.xplore_live import view as xploreliveview
from menuhub.xplore_test import view as xploretestview
from menuhub.finaplus_uat import view as finaplusuatview
from menuhub.fina_agent import view as finagentview
from menuhub.menu_858 import view as mainmenuview
from menuhub.ghpolice_hospital import view as policehospitalview
from menuhub.template_test import view as templateview

urlpatterns = [
   # url(r'^admin/', include(admin.site.urls)),
    url(r'^magnet/agent/$', agentview),
    url(r'^herbaltech/$', herbaltechview),
    url(r'^herbaltech/marketers/$', herbalview),
    url(r'^magnet/cust/$', custtechview),
    url(r'^xplore/live/$', xploreliveview),
    url(r'^xplore/test/$', xploretestview),
    url(r'^finaplus/uat/$', finaplusuatview),
    url(r'^finaplus_agent/uat/$', finagentview),
    url(r'^mainmenu_858/$', mainmenuview),
    url(r'^ghana_police/uat/$', policehospitalview),
    url(r'^template/test/$', templateview),
]

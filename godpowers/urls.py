#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.conf.urls import url

from . import views

app_name = 'godpowers'
urlpatterns = [
    url(r'visitorsoverview/$', views.visitorsProposalOverview, name='visitorsproposalsoverview'),
    url(r'^visitoroverview/(?P<pk>[0-9]+)/$', views.visitorOverview, name='visitoroverview'),
    url(r'^visitors/$', views.visitorsMenu, name='visitorsmenu'),
    url(r'^clearcache/$', views.clearCache, name='clearcache'),
    url(r'^getvisitors/(?P<pk>[0-9]+)/$', views.getVisitors, name='getvisitors'),
    url(r'^sessions/list/$', views.sessionList, name='sessionlist'),
    url(r'^sessions/kill/(?P<pk>[0-9]+)/$', views.killSession, name='killsession'),
]

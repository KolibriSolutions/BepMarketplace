#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.urls import path

from . import views

app_name = 'godpowers'
urlpatterns = [
    path('visitorsoverview/', views.visitorsProposalOverview, name='visitorsproposalsoverview'),
    path('visitoroverview/<int:pk>/', views.visitorOverview, name='visitoroverview'),
    path('visitors/', views.visitorsMenu, name='visitorsmenu'),
    path('clearcache/', views.clearCache, name='clearcache'),
    path('getvisitors/<int:pk>/', views.getVisitors, name='getvisitors'),
    path('sessions/list/', views.sessionList, name='sessionlist'),
    path('sessions/kill/<int:pk>/', views.killSession, name='killsession'),
]

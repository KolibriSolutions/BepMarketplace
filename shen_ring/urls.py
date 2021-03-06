#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.urls import path

from . import views

app_name = 'shen_ring'
urlpatterns = [
    path('login/', views.login, name='login'),
    path('callback/', views.callback, name='callback'),
]

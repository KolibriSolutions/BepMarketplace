#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.urls import path

from . import views

app_name = 'canvas'

urlpatterns = [
    path('', views.lti, name='lti'),  # url used in canvas, make sure to set url to /canvas/ in canvas.
]

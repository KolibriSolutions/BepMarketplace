#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.urls import path, re_path
from . import consumers

websocket_urlpatterns = [
    path('tracking/viewnumber/<int:pk>/', consumers.CurrentViewNumberConsumer.as_asgi()),
]

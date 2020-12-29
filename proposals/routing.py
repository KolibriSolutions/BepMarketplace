#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('projects/favorite/', consumers.FavoriteConsumer.as_asgi()),
    path('projects/cpvprogress/', consumers.CPVProgressConsumer.as_asgi()),

]

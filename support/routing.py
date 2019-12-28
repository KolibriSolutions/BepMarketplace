#  Bep Marketplace ELE
#  Copyright (c) 2016-2019 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('support/mailprogress/', consumers.MailProgressConsumer),
]

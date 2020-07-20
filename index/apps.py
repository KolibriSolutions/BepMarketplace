#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.apps import AppConfig


class IndexConfig(AppConfig):
    name = 'index'

    def ready(self):
        import index.signals.handlers

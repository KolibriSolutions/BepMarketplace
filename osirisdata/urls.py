#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.conf.urls import url

from . import views

app_name = 'osirisdata'

urlpatterns = [
    url('^list/$', views.listOsiris, name='list'),
    url('^tometa/$', views.osirisToMeta, name='tometa'),
]

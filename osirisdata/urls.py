#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.urls import path

from . import views

app_name = 'osirisdata'

urlpatterns = [
    path('upload/', views.uploadOsiris, name='upload'),
    path('list/', views.listOsiris, name='list'),
    path('tometa/', views.osirisToMeta, name='tometa'),
]

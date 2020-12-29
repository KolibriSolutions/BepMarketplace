#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.urls import path

from . import views

app_name = 'timeline'

urlpatterns = [
    path('timeslot/list/', views.list_timeslots, name='list_timeslots'),
    path('timeslot/add/', views.add_timeslot, name='add_timeslot'),
    path('timeslot/<int:timeslot>/', views.edit_timeslot, name='edit_timeslot'),
    path('timeslot/<int:timeslot>/list/', views.list_timephases, name='list_timephases'),
    path('timeslot/<int:timeslot>/add/', views.add_timephase, name='add_timephase'),
    path('timephase/<int:timephase>/', views.edit_timephase, name='edit_timephase'),
    path('timephase/<int:timephase>/delete/', views.delete_timephase, name='delete_timephase'),
    path('copy/', views.copy_timephases, name='copy_timephases'),
]

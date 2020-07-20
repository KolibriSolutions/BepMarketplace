#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.urls import path

from . import views

app_name = 'presentations'

urlpatterns = [
    path('wizard/step1/', views.wizard_step1, name='presentationswizardstep1'),
    path('wizard/step2/', views.wizard_step2, name='presentationswizardstep2'),
    path('wizard/step3/', views.wizard_step3, name='presentationswizardstep3'),
    path('wizard/step4/', views.wizard_step4, name='presentationswizardstep4'),
    path('list/', views.list_presentations, name='presentationsplanning'),
    path('excel/', views.export_presentations, name='presentationsplanningxls'),
    path('', views.calendar, name='presentationscalendar'),
    path('own/', views.calendar, {'own': True}, name='presentationscalendarown')
]

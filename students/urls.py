#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.urls import path

from . import views

app_name = 'students'
urlpatterns = [
    path('applications/', views.list_applications, name='listapplications'),

    path('apply/<int:pk>/', views.apply, name='apply'),
    path('application/confirm/<int:pk>/', views.confirm_apply, name='confirmapply'),
    path('application/up/<int:application_id>/', views.prio_up, name='prioUp'),
    path('application/down/<int:application_id>/', views.prio_down, name='prioDown'),

    path('application/retract/<int:application_id>/', views.retract_application, name='retractapplication'),

    # path('files/add/', views.add_file, name='addfile'),
    # path('files/edit/<int:pk>/', views.edit_file, name='editfile'),

    # view for staff
    path('list/nots/', views.list_students, name='liststudents'),  # error on no timeslot for students, but still a view to reach the tabcontrol. /nots is needed for relative links to ../<ts> to work.
    path('list/<int:timeslot>/', views.list_students, name='liststudents'),
    path('list/xlsx/<int:timeslot>/', views.list_students_xlsx, name='liststudents_xls'),
    path('download/<int:timeslot>/', views.download_files, name='download_files'),

]

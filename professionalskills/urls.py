#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.urls import path

from . import views

app_name = 'professionalskills'

urlpatterns = [
    path('filetype/list/', views.list_filetypes, name='list'),
    path('filetype/create/', views.create_filetype, name='create'),
    path('filetype/<int:pk>/edit/', views.edit_filetype, name='edit'),
    path('filetype/<int:pk>/delete/', views.delete_filetype, name='delete'),
    path('filetype/<int:pk>/export/', views.export_filetype_xlsx, name='filetype_export'),

    path('filetype/<int:pk>/grading/', views.list_filetype_aspects, name='list_aspects'),
    path('filetype/<int:pk>/grading/add/', views.add_filetype_aspect, name='add_aspect'),
    path('filetype/grading/<int:pk>/edit/', views.edit_filetype_aspect, name='edit_aspect'),
    path('filetype/grading/<int:pk>/delete/', views.delete_filetype_aspect, name='delete_aspect'),
    path('copy/<int:pk>/<int:from_pk>/', views.copy, name='copy'),
    path('copy/<int:pk>/', views.copy, name='copy_overview'),

    path('extensions/', views.edit_extensions, name='extensions'),

    path('filetype/<int:pk>/upload/', views.student_upload, name='upload'),
    path('student/', views.student, name='student'),
    path('student/<int:pk>/', views.student, name='student'),

    path('files/type/<int:pk>/all/', views.list_files_of_type, name='listfileoftype'),
    path('files/type/<int:pk>/missing/', views.list_missing_of_type, name='listmissingoftype'),
    path('file/<int:pk>/respond/', views.respond_file, name='respond'),
    path('file/<int:pk>/', views.view_response, name='response'),

    path('mail/overdue/', views.mail_overdue_students, name='mailoverduestudents'),
    path('print/forms/', views.print_forms, name='printprvforms'),
    path('download/type/<int:pk>/', views.download_all_of_type, name='downloadall'),


    path('group/create/<int:pk>/', views.create_group, name='creategroup'),
    path('group/create/', views.create_group, name='creategroup'),
    path('group/edit/<int:pk>/', views.edit_group, name='editgroup'),
    path('group/listall/<int:pk>/', views.list_groups, name='listgroups'),
    path('group/assign/<int:pk>/', views.assign, name='assignshuffle'),
    path('group/', views.list_own_groups, name='listowngroups'),
    # path('group/switch/<int:frompk>/<int:topk>)/', views.switch_group, name='switchgroups'),
    path('group/switch/<int:pk>/', views.switch_group, name='switchgroups'),
    path('group/members/<int:pk>/', views.list_group_members, name='listgroupmembers'),



]

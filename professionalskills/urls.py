#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.urls import path

from . import views

app_name = 'professionalskills'

urlpatterns = [
    path('filetype/create/', views.create_filetype, name='filetypecreate'),
    path('filetype/edit/<int:pk>/', views.edit_filetype, name='filetypeedit'),
    path('filetype/grading/<int:pk>/', views.list_filetype_aspects, name='filetypeaspects'),
    path('filetype/grading/add/<int:pk>/', views.add_filetype_aspect, name='addaspect'),
    path('filetype/grading/edit/<int:pk>/', views.edit_filetype_aspect, name='editaspect'),
    path('filetype/grading/delete/<int:pk>/', views.delete_filetype_aspect, name='deleteaspect'),
    path('filetype/delete/<int:pk>/', views.delete_filetype, name='filetypedelete'),
    path('filetype/list/', views.list_filetypes, name='filetypelist'),
    path('studentfiles/<int:pk>/', views.list_student_files, name='liststudentfiles'),
    path('files/', views.list_own_files, name='listownfiles'),
    path('files/type/<int:pk>/all/', views.list_files_of_type, name='listfileoftype'),
    path('files/type/<int:pk>/missing/', views.list_missing_of_type, name='listmissingoftype'),
    path('file/<int:pk>/respond/', views.respond_file, name='respondfile'),
    path('file/<int:pk>/', views.view_response, name='viewresponse'),

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

    path('extensions/', views.edit_extensions, name='extensions'),
]

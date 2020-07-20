#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.urls import path, re_path

from . import views

app_name = 'proposals'

# urlpatterns are split for tests.

general_urlpatterns = [
    # public list
    path('', views.list_public_projects, name='list'),
    path('favorites/', views.list_favorite_projects, name='favorites'),

    # proposal
    path('create/', views.create_project, name='create'),
    re_path(r'^share/(?P<token>[0-9A-Za-z_\-:]+)/$', views.view_share_link, name='viewsharelink'),

    # lists
    path('pending/', views.list_pending, name='pending'),
    path('own/future/', views.list_own_projects, name='chooseedit'),
    path('own/<int:timeslot>/', views.list_own_projects, name='chooseedit'),
    path('track/future/', views.list_track, name='listtrackproposals'),
    path('track/<int:timeslot>/', views.list_track, name='listtrackproposals'),
    path('private/future/', views.list_private_projects, name='privateproposals'),
    path('private/<int:timeslot>/', views.list_private_projects, name='privateproposals'),
    path('group/future/', views.list_group_projects, name='listgroupproposals'),
    path('group/<int:timeslot>/', views.list_group_projects, name='listgroupproposals'),

    # stats
    path('stats/future/', views.project_stats, name='stats'),
    path('stats/<int:timeslot>/', views.project_stats, name='stats'),

    path('stats/<int:timeslot>/personal/', views.stats_personal, name='statspersonal'),
    path('stats/<int:timeslot>/personal/<int:step>/', views.stats_personal, name='statspersonal'),
    # path('stats/general/', views.stats_general, name='statsgeneral'),
    # path('stats/general/<int:step>/', views.stats_general, name='statsgeneral'),

    # cpv
    path('contentpolicy/', views.content_policy_view, name='contentpolicy'),
    path('contentpolicy/calc/', views.content_policy_calc, name='contentpolicycalc'),
]
status_urlpatterns = [
    path('details/<int:pk>/', views.detail_project, name='details'),
    path('edit/<int:pk>/', views.edit_project, name='edit'),
    path('copy/<int:pk>/', views.copy_project, name='copy'),
    path('getshare/<int:pk>/', views.share, name='sharelink'),

    path('files/add/<str:ty>/<int:pk>/', views.add_file, name='addfile'),
    path('files/edit/<str:ty>/<int:pk>/', views.edit_file, name='editfile'),

    path('delete/ask/<int:pk>/', views.ask_delete_project, name='askdeleteproposal'),
    path('delete/<int:pk>/', views.delete_project, name='deleteproposal'),

    path('status/upgrade/<int:pk>/', views.upgrade_status, name='upgradestatus'),
    path('status/downgrade/<int:pk>/', views.downgrade_status, name='downgradestatusmessage'),
]

urlpatterns = general_urlpatterns + status_urlpatterns

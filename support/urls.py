#  Bep Marketplace ELE
#  Copyright (c) 2016-2019 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.urls import path

from . import views

app_name = 'support'

urlpatterns = [

    path('mail/', views.mailing, name='mailinglist'),
    path('mail/templates/<int:pk>/', views.mailing, name='mailinglisttemplate'),
    path('mail/confirm', views.confirm_mailing, name='mailingconfirm'),
    path('mail/templates/', views.list_mailing_templates, name='mailingtemplates'),
    path('mail/templates/delete/<int:pk>/', views.delete_mailing_template, name='deletemailingtemplate'),
    path('mail/trackheads/', views.mail_track_heads, name='mailtrackheads'),

    # path('ectsform/', views.ECTSForm, name='ectsform'), #deprecated due to osirisdata
    # path('stats/', views.stats, name='stats'),

    # public files
    path('files/add/', views.add_file, name='addfile'),
    path('files/edit/', views.edit_files, name='editfiles'),
    path('files/edit/<int:pk>/', views.edit_file, name='editfile'),
    path('files/delete/<int:pk>/', views.delete_file, name='deletefile'),

    # lists
    path('users/', views.list_users, name='listusers'),
    path('users/<int:pk>', views.user_info, name='userinfo'),
    # path('users/clearcache/', views.list_users_clear_cache, name='clearcacheuserlist'),
    # path('users/upgrade/<int:pk>/', views.upgrade_user, name='upgradeuser'),
    # path('users/downgrade/<int:pk>/', views.downgrade_user, name='downgradeuser'),
    path('users/overruleusermeta/<int:pk>/', views.usermeta_overrule, name='overruleusermeta'),
    path('users/groups/<int:pk>/', views.edit_user_groups, name='usergroups'),
    path('user/toggle/<int:pk>/', views.toggle_disable_user, name='toggledisable'),

    path('capacitygroup/list/', views.list_capacity_groups, name='listcapacitygroups'),  # listing new way of all capacitygroups
    path('capacitygroup/add/', views.add_capacity_group, name='addcapacitygroup'),
    path('capacitygroup/edit/<int:pk>/', views.edit_capacity_group, name='editcapacitygroup'),
    path('capacitygroup/delete/<int:pk>/', views.delete_capacity_group, name='deletecapacitygroup'),
    # path('groupadministrator/', views.groupadministrators_form, name='groupadministratorsform'),  # new way of setting capacity group administrators. Not yet enabled.
    # path('capacitygroupadministration/', views.capacity_group_administration, name='capacitygroupadministration'),  # DEPRICATED old way of capacity groups admins using hardcoded list.
    path('groupadministrator/', views.groupadministrators_form, name='groupadministratorsform'),

    path('staff/', views.list_staff, name='liststaff'),
    path('staff/projects/<int:pk>/', views.list_staff_projects, name='liststaffproposals'),
    # path('staff/xlsx/', views.list_staff_xlsx, name='liststaffXls'),  # depricated
    # path('students/', views.list_students, name='liststudents'), # depricated replaced by dist-timeslot view.
    path('students/<int:timeslot>/', views.list_students, name='liststudents'),
    path('students/xlsx/', views.list_students_xlsx, name='liststudentsXls'),

    # path('liststudentsldap/', views.listStudentsLdap, name='liststudentsldap'),# might be re-introduced when OSIRIS link is finished.
    # path('clearcacheallstudentslist/', views.clearCacheAllStudentsList, name='clearcacheallstudentslist'),

    path('verifyassistants/', views.verify_assistants, name='verifyassistants'),

    path('history/', views.history, name='history'),
    path('history_download/<int:timeslot>/<str:download>/', views.history_download, name='history_download'),
]

#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.urls import re_path, path

from . import views

# define all kinds of file downloads here.
# Files can be downloaded using their filename (for backward compatibility with file edit) or using their object ID
app_name = 'download'

reguuid = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}.[A-z]{1,5}"  # regex for uuid with extension

urlpatterns = [
    # public files
    path('publicfile/<int:fileid>', views.public_files, name='publicfile'),  # by object-id
    re_path(r'public_files/(?P<timeslot>[0-9]+)/(?P<fileid>' + reguuid + ')$', views.public_files, name='public_files'),
    # uri

    # proposal attachements
    path('proposalfile/<str:ty>/<int:fileid>', views.project_files, name='proposalfile'),  # object-id
    re_path(r'proposal_(?P<project_id>[0-9]+)/(?P<fileid>' + reguuid + ')$', views.project_files,
            name='proposal_files'),  # uri
    path('projectfile/<str:ty>/<int:fileid>', views.project_files, name='projectfile'),
    re_path(r'project_(?P<project_id>[0-9]+)/(?P<fileid>' + reguuid + ')$', views.project_files, name='project_files'),
    # direct url

    # student files (professionalskills)
    path('studentfile/<int:fileid>', views.student_files, name='studentfile'),  # object-id
    re_path(r'dist_(?P<distid>[0-9]+)/(?P<fileid>' + reguuid + ')$', views.student_files, name='student_files'),  # uri
]

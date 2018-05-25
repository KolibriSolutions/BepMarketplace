from django.urls import path, re_path

from proposals.views import view_share_link
from . import views

app_name = 'api'

urlpatterns = [
    path('', views.api_info, name='api'),

    path('status/upgrade/<int:pk>/', views.upgrade_status_api, name='upgradestatus'),
    path('status/downgrade/<int:pk>/', views.downgrade_status_api, name='downgradestatus'),
    path('verify/assistant/<int:pk>/', views.verify_assistant, name='verifyassistant'),
    path('getgroupadmins/', views.get_group_admins, name='getgroupadmins'),
    path('getgroupadmins/<str:group>/', views.get_group_admins, name='getgroupadminsarg'),
    re_path(r'^share/(?P<token>[0-9A-Za-z_\-:]+)/$', view_share_link, name='viewsharelink'),  # depricated, moved to proposals
    path('projects/', views.list_published_api, name='listpublished'),
    path('projects/group/', views.list_public_projects_api, name='listpublishedpergroup'),
    path('projects/titles/', views.list_public_projects_titles_api, name='listpublishedtitles'),
    path('projects/<int:pk>/', views.detail_proposal_api, name='getpublisheddetail'),
]

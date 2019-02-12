from django.urls import path, re_path

from . import views

app_name = 'proposals'

urlpatterns = [
    path('', views.list_public_projects, name='list'),
    path('favorites/', views.list_favorited_projects, name='favorites'),
    path('details/<int:pk>/', views.detail_project, name='details'),
    path('create/', views.create_project, name='create'),
    path('edit/', views.list_own_projects, name='chooseedit'),
    path('edit/<int:pk>/', views.edit_project, name='edit'),
    path('copy/<int:pk>/', views.copy_project, name='copy'),

    path('files/add/<str:ty>/<int:pk>/', views.add_file, name='addfile'),
    path('files/edit/<str:ty>/<int:pk>/', views.edit_file, name='editfile'),

    path('delete/ask/<int:pk>/', views.ask_delete_project, name='askdeleteproposal'),
    path('delete/<int:pk>/', views.delete_project, name='deleteproposal'),

    path('status/upgrade/<int:pk>/', views.upgrade_status, name='upgradestatus'),
    path('status/downgrade/<int:pk>/', views.downgrade_status, name='downgradestatusmessage'),

    path('pending/', views.list_pending, name='pending'),

    path('share/<int:pk>/', views.share, name='sharelink'),
    re_path(r'^share/(?P<token>[0-9A-Za-z_\-:]+)/$', views.view_share_link, name='viewsharelink'),

    path('track/', views.list_track, name='listtrackproposals'),

    path('stats/', views.project_stats, name='stats'),
    path('stats/<int:timeslot>', views.project_stats, name='stats'),

    path('stats/personal', views.stats_personal, name='statspersonal'),
    path('stats/personal/<int:step>/', views.stats_personal, name='statspersonal'),
    path('stats/general/', views.stats_general, name='statsgeneral'),
    path('stats/general/<int:step>/', views.stats_general, name='statsgeneral'),
]

from django.urls import path

from . import views

app_name = 'proposals'
urlpatterns = [
    path('', views.list_public_proposals, name='list'),
    path('details/<int:pk>/', views.detail_proposal, name='details'),
    path('create/', views.create_proposal, name='create'),
    path('edit/', views.list_own_proposals, name='chooseedit'),
    path('edit/<int:pk>/', views.edit_proposal, name='edit'),
    path('copy/<int:pk>/', views.copy_proposal, name='copy'),

    path('files/add/<str:ty>/<int:pk>/', views.add_file, name='addfile'),
    path('files/edit/<str:ty>/<int:pk>/', views.edit_file, name='editfile'),

    path('delete/ask/<int:pk>/', views.ask_delete_proposal, name='askdeleteproposal'),
    path('delete/<int:pk>/', views.delete_proposal, name='deleteproposal'),

    path('status/upgrade/<int:pk>/', views.upgrade_status, name='upgradestatus'),
    path('status/downgrade/<int:pk>/', views.downgrade_status, name='downgradestatusmessage'),

    path('pending/', views.list_pending, name='pending'),

    path('share/<int:pk>/', views.share, name='sharelink'),
    path('track/', views.list_track, name='listtrackproposals'),

    path('stats/', views.stats_personal, name='stats'),
    path('stats/<int:step>/', views.stats_personal, name='stats'),
    path('stats/general/', views.stats_general, name='statsgeneral'),
    path('stats/general/<int:step>/', views.stats_general, name='statsgeneral'),
]

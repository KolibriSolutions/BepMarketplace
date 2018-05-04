from django.urls import path

from . import views

app_name = 'tracking'
urlpatterns = [
    path('user/login', views.list_user_login, name='listuserlog'),
    path('proposal/', views.list_proposal_status_change, name='statuslist'),
    path('application/', views.list_application_change, name='applicationlist'),
    path('stream/', views.live_streamer, name='livestreamer'),
    path('user/<int:pk>/', views.telemetry_user_detail, name='userdetail'),
]

from django.urls import path

from . import views

app_name = 'distributions'

urlpatterns = [
    path('manual/', views.manual, name='supportDistributeApplications'),
    path('api/distribute/', views.api_distribute, name='distribute'),
    path('api/undistribute/', views.api_undistribute, name='undistribute'),
    path('api/redistribute/', views.api_redistribute, name='changedistribute'),
    path('mail/', views.mail_distributions, name='maildistributions'),

    path('automatic/', views.automatic_options, name='automaticoptions'),
    path('automatic/<int:dist_type>/<int:distribute_random>/<int:automotive_preference>/', views.automatic, name='distributeproposaloption'),
    path('automatic/<int:dist_type>/', views.automatic, name='distributeproposal'),
    path('secondchoice/', views.list_second_choice, name='secondchoice'),
    path('delete/randoms/', views.delete_random_distributions, name='deleterandoms'),
]

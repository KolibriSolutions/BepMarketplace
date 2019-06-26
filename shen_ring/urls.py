from django.urls import path

from . import views

app_name = 'shen_ring'
urlpatterns = [
    path('login/', views.login, name='login'),
    path('callback/', views.callback, name='callback'),
]
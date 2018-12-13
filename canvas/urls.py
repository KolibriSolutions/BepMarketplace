from django.urls import path

from . import views

app_name = 'canvas'

urlpatterns = [
    path('', views.lti, name='lti'),
]
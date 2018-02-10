from django.conf.urls import url

from . import views

app_name = 'osirisdata'

urlpatterns = [
    url('^list/$', views.listOsiris, name='list'),
    url('^tometa/$', views.osirisToMeta, name='tometa'),
]
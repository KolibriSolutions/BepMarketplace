from django.conf.urls import url

from . import views

app_name = 'timeline'

urlpatterns = [
    url(r'^timeslot/list/$', views.list_timeslots, name='list_timeslots'),
    url(r'^timeslot/add/$', views.add_timeslot, name='add_timeslot'),
    url(r'^timeslot/(?P<timeslot>[0-9]+)/$', views.edit_timeslot, name='edit_timeslot'),
    url(r'^timeslot/(?P<timeslot>[0-9]+)/list/$', views.list_timephases, name='list_timephases'),
    url(r'^timeslot/(?P<timeslot>[0-9]+)/add/$', views.add_timephase, name='add_timephase'),
    url(r'^timephase/(?P<timephase>[0-9]+)/$', views.edit_timephase, name='edit_timephase'),
]
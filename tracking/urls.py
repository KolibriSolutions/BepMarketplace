from django.conf.urls import url

from . import views

app_name = 'tracking'
urlpatterns = [
    url(r'^listuserlog/$', views.listUserLog, name='listuserlog'),
    url(r'^statuslist/$', views.viewTrackingStatusList, name='statuslist'),
    url(r'^applicationlist/$', views.viewTrackingApplicationList, name='applicationlist'),
    url(r'^livestreamer/$', views.liveStreamer, name='livestreamer'),
    url(r'^userdetail/(?P<pk>[0-9]+)/$', views.userDetail, name='userdetail'),
]
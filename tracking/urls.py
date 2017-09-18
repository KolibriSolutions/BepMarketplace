from django.conf.urls import url

from . import views

app_name = 'tracking'
urlpatterns = [
    url(r'^statuslist/$', views.viewTrackingStatusList, name='statuslist'),
    url(r'^applicationlist/$', views.viewTrackingApplicationList, name='applicationlist'),
    url(r'^listuserlog/$', views.listUserLog, name='listuserlog'),
    url(r'^livestreamer/$', views.liveStreamer, name='livestreamer'),
]
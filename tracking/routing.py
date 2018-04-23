from django.conf.urls import url
from . import consumers

websocket_urlpatterns = [
    url(r'^tracking/viewnumber/(?P<pk>[0-9]+)/$', consumers.CurrentViewNumberConsumer),
    url(r'^tracking/live/$', consumers.LiveStreamConsumer),
    url(r'^tracking/telemetry/(?P<key>[a-zA-Z0-9]+)/$', consumers.TelemetryAPIConsumer),
    url(r'^tracking/telemetry/user/(?P<pk>[0-9]+)/$', consumers.TelemetryUserConsumer)
]
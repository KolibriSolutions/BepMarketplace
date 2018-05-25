from django.urls import path, re_path
from . import consumers

websocket_urlpatterns = [
    path('tracking/viewnumber/<int:pk>/', consumers.CurrentViewNumberConsumer),
    path('tracking/live/', consumers.LiveStreamConsumer),
    re_path(r'^tracking/telemetry/(?P<key>[a-zA-Z0-9]+)/$', consumers.TelemetryAPIConsumer),
    path('tracking/telemetry/user/<int:pk>/', consumers.TelemetryUserConsumer)
]

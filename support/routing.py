# from channels.routing import route
# from support import consumers
#
# channel_routing = [
#     route('websocket.connect', consumers.mailProgress, path=r'^mailprogress/$'),
#     # route('websocket.connect', consumers.ECTSConnect, path=r'^ectssubmit/$'), #depricated due to osirisdata
#     # route('websocket.receive', consumers.ECTSSubmit, path=r'^ectssubmit/$'),
# ]

from django.conf.urls import url
from . import consumers

websocket_urlpatterns = [
    url(r'^support/mailprogress/$', consumers.MailProgressConsumer),
]
from channels.routing import route
from tracking import consumers

channel_routing = [
   route('websocket.connect', consumers.connectCurrentViewnumber, path=r'^viewnumber/(?P<pk>[0-9]+)/$'),
   route('websocket.connect', consumers.connectLiveStream, path=r'live/$'),
   #route('websocket.disconnect', views.disconnectCurrentViewnumber),
]

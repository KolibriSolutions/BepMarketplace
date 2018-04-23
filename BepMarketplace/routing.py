from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
import tracking.routing
import support.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            support.routing.websocket_urlpatterns +
            tracking.routing.websocket_urlpatterns
        )
    ),
})

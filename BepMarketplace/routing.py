from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

import support.routing
import tracking.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                support.routing.websocket_urlpatterns +
                tracking.routing.websocket_urlpatterns
            )
        )
    ),
})

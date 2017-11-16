from channels.routing import include

channel_routing = [
    include('tracking.routing.channel_routing', path=r'^/tracking/'),
    include('support.routing.channel_routing', path=r'^/support/'),
]

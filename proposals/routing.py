from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('projects/favorite/', consumers.FavoriteConsumer),
]

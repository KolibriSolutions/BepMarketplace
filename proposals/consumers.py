import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import get_object_or_404

from .models import Project, Favorite


class FavoriteConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            # forbidden for anonymous users.
            await self.close()

        await self.channel_layer.group_add(
            'project_favorite_{}'.format(self.user.pk),
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            'project_favorite_{}'.format(self.user.pk),
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Receive a number of project to favorite, unfavorite

        :param text_data:
        :return:
        """
        a = json.loads(text_data)
        proj = get_object_or_404(Project, pk=a)
        q = Favorite.objects.filter(Project=proj, User=self.user)
        # toggle favorite
        if q.exists():
            q.first().delete()
            fav = False
        else:
            f = Favorite(
                User=self.user,
                Project=proj
            )
            f.save()
            fav = True
        await self.channel_layer.group_send('project_favorite_{}'.format(self.user.pk), {'type': 'update', 'text': json.dumps([proj.pk, fav])})

    async def update(self, event):
        # Handles the messages on channel
        await self.send(text_data=event["text"])

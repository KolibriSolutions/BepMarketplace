from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import Group


class MailProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if await database_sync_to_async(Group.objects.get)(name='type3staff') \
                not in await database_sync_to_async(self.user.groups.all)() \
                and not self.user.is_superuser:
            await self.close()
        else:
            await self.channel_layer.group_add(
                'email_progress',
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            'email_progress',
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def update(self, event):
        # Handles the messages on channel
        await self.send(text_data=event["text"])

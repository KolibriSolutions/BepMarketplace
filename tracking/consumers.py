from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import Group, User
from .models import TelemetryKey
from tracking.utils import get_ProposalTracking
from django.shortcuts import get_object_or_404
from django.contrib import auth
from channels.db import database_sync_to_async
from proposals.utils import get_cached_project




def checkauthcurrentviewnumber(user, track):
    if user != track.Subject.ResponsibleStaff and \
                    user not in track.Subject.Assistants.all() and \
                    auth.models.Group.objects.get(name="type3staff") not in user.groups.all() and \
                    not user.is_superuser:
        return True
    return False


class CurrentViewNumberConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.pk = self.scope['url_route']['kwargs']['pk']
        self.prop = await database_sync_to_async(get_cached_project)(self.pk)
        self.track = await database_sync_to_async(get_ProposalTracking)(self.prop)
        self.user = self.scope['user']
        if self.track.Subject.Status != 4:
            await self.close()
            return
        if await database_sync_to_async(checkauthcurrentviewnumber)(self.user, self.track):
            await self.close()
            return

        await self.channel_layer.group_add(
                'viewnumber{}'.format(self.pk),
                self.channel_name
            )
        await self.accept()
        await self.send(text_data=str(await database_sync_to_async(self.track.UniqueVisitors.count)()))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            'viewnumber{}'.format(self.pk),
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def update(self, event):
        # Handles the messages on channel
        await self.send(text_data=event["text"])

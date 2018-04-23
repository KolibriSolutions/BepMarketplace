from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import Group, User
from .models import TelemetryKey
from .views import getTrack
from django.shortcuts import get_object_or_404
from django.contrib import auth
from channels.db import database_sync_to_async
from proposals.cacheprop import getProp

class LiveStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if await database_sync_to_async(Group.objects.get)(name='type3staff') \
                not in await database_sync_to_async(self.user.groups.all)() \
                and not self.user.is_superuser:
            await self.close()
        else:
            await self.channel_layer.group_add(
                'liveview_telemetry',
                self.channel_name
            )
            await self.accept()
    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            'liveview_telemetry',
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def update(self, event):
        # Handles the messages on channel
        await self.send(text_data=event["text"])


class TelemetryAPIConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        key = self.scope['url_route']['kwargs']['key']
        if len(key) != 64:
            await self.close()
            return
        try:
            obj = await database_sync_to_async(TelemetryKey.objects.get)(Key=key)
        except TelemetryKey.DoesNotExist:
            await self.close()
            return

        if not obj.is_valid():
            await self.close()
            return

        await self.channel_layer.group_add(
            'telemetry',
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard (
            'telemetry',
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def update(self, event):
        # Handles the messages on channel
        await self.send(text_data=event["text"])


class TelemetryUserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_superuser:
            await self.close()
            return
        self.userpk = self.scope['url_route']['kwargs']['pk']
        try:
            self.target = await database_sync_to_async(get_object_or_404)(User, pk=self.userpk)
        except:
            await self.close()
            return

        await self.channel_layer.group_add(
            'live_{}'.format(self.target.username),
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        try:
            await self.channel_layer.group_discard (
                'live_{}'.format(self.target.username),
                self.channel_name
            )
        except:
            pass
    async def receive(self, text_data):
        pass

    async def update(self, event):
        # Handles the messages on channel
        await self.send(text_data=event["text"])


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
        self.prop = await database_sync_to_async(getProp)(self.pk)
        self.track = await database_sync_to_async(getTrack)(self.prop)
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
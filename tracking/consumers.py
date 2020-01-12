#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib import auth
from django.contrib.auth.models import Group

from proposals.utils import get_cached_project
from tracking.utils import get_ProposalTracking


def checkauthcurrentviewnumber(user, track):
    # user | has_group: "any" and project.Status == 3
    if track.Subject.Status != 4 or not user.groups.exists():
        return True  # deny student and unpublished
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

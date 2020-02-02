#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from proposals.utils import get_cached_project
from .utils import get_project_tracking


class CurrentViewNumberConsumer(WebsocketConsumer):
    def connect(self):
        self.pk = self.scope['url_route']['kwargs']['pk']
        self.track = get_project_tracking(get_cached_project(self.pk))
        if self.track.Subject.Status != 4:
            self.close()
            return
        if not self.scope['user'].groups.exists():
            self.close()
            return

        async_to_sync(self.channel_layer.group_add)(
            'viewnumber{}'.format(self.pk),
            self.channel_name
        )
        self.accept()
        self.send(text_data=str(self.track.UniqueVisitors.count()))

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            'viewnumber{}'.format(self.pk),
            self.channel_name
        )

    def update(self, event):
        # Handles the messages on channel
        self.send(text_data=event["text"])

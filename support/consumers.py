#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import Group


class MailProgressConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        if Group.objects.get(name='type3staff') not in self.user.groups.all() and not self.user.is_superuser:
            self.close()
        else:
            async_to_sync(self.channel_layer.group_add)(
                'email_progress',
                self.channel_name
            )
            self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            'email_progress',
            self.channel_name
        )

    def update(self, event):
        # Handles the messages on channel
        self.send(text_data=event["text"])

#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, JsonWebsocketConsumer
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404

from .models import Project, Favorite
from .utils import get_favorites


class FavoriteConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            # forbidden for anonymous users.
            self.close()

        async_to_sync(self.channel_layer.group_add)(
            'project_favorite_{}'.format(self.user.pk),
            self.channel_name
        )
        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            'project_favorite_{}'.format(self.user.pk),
            self.channel_name
        )

    def receive_json(self, content):
        """
        Receive a number of project to favorite, unfavorite

        :param content: json decoded message content
        :return:
        """
        t = content['req']
        if t == 'all':  # get all favorites of this user
            self.send_json(content={'req': 'all', 'list': get_favorites(self.user)})
        else:
            proj = get_object_or_404(Project, pk=int(content['proj']))
            q = Favorite.objects.filter(Project=proj, User=self.user)
            if t == 'ask':
                fav = q.exists()
                # update only this websocket, not the whole channel.
                self.send_json(content={'req': 'ask', 'proj': proj.pk, 'fav': fav})
            elif t == 'set':
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
                # update all connected websockets (channel group) that this project is (un)favorited.
                async_to_sync(self.channel_layer.group_send)('project_favorite_{}'.format(self.user.pk), {'type': 'update', 'content': {'req': 'set', 'proj': proj.pk, 'fav': fav}})

    def update(self, event):
        """
        Any message sent to that channel name - or to a group the channel name was added to -
        will be received by the consumer much like an event from its connected client, and dispatched to a named method on the consumer.
        The name of the method will be the type of the event with periods replaced by underscores -
        so, for example, an event coming in over the channel layer with a type of chat.join will be handled by the method chat_join.

        This function responds to channel messages of 'type':'update', and forwards them to the websocket.
        :param event:
        :return:
        """
        self.send_json(content=event["content"])


class CPVProgressConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        if Group.objects.get(name='type3staff') not in self.user.groups.all() and not self.user.is_superuser:
            self.close()
        else:
            async_to_sync(self.channel_layer.group_add)(
                'cpv_progress',
                self.channel_name
            )
            self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            'cpv_progress',
            self.channel_name
        )

    def update(self, event):
        # Handles the messages on channel
        self.send(text_data=event["text"])

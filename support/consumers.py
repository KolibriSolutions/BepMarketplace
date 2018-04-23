from channels.generic.websocket import AsyncWebsocketConsumer

class MailProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            'emailprogress',
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard (
            'emailprogress',
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def update(self, event):
        # Handles the messages on channel
        await self.send(text_data=event["text"])
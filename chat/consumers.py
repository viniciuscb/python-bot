# chat/consumers.py
import json

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core import serializers
from django.utils.timezone import now

from chat.models import Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # send last messages on connection
        last_messages = await self.get_last_messages(self.room_name)
        #json_messages = self.serialize_messages(last_messages)

        await self.send(text_data=serializers.serialize("json", last_messages))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        message_object = self.new_message_object(self.scope['user'], self.room_name, message)

        # Send message to room group
        # (before inserting in database to fast response)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': serializers.serialize("json",[message_object])
            }
        )

        # Store message in database
        await self.insert_message(message_object)

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=message)

    @database_sync_to_async
    def get_last_messages(self, room_name):
        return Message.objects.filter(room_name=room_name).order_by("-created_at")[:3][::-1]

    @database_sync_to_async
    def insert_message(self, message_object):
        message_object.save()

    def new_message_object(self, sender, room_name, message_content):
        message = Message()
        message.sender = sender
        message.room_name = room_name
        message.content = message_content
        message.created_at = now()
        return message


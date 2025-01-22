import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Verify user has access to this room
        if not await self.can_access_room():
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            
            # Save message to database
            saved_message = await self.save_message(self.user, message)
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user': self.user.username,
                    'timestamp': saved_message.timestamp.strftime('%H:%M')
                }
            )
        except Exception as e:
            print(f"Error in receive: {e}")

    async def chat_message(self, event):
        try:
            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'message': event['message'],
                'user': event['user'],
                'timestamp': event['timestamp']
            }))
        except Exception as e:
            print(f"Error in chat_message: {e}")

    @database_sync_to_async
    def save_message(self, user, message):
        room = ChatRoom.objects.get(name=self.room_name)
        return Message.objects.create(
            room=room,
            user=user,
            content=message
        )

    @database_sync_to_async
    def can_access_room(self):
        try:
            room = ChatRoom.objects.get(name=self.room_name)
            if self.user.is_instructor:
                return room.course.instructor == self.user
            else:
                return room.course.students.filter(id=self.user.id).exists()
        except ChatRoom.DoesNotExist:
            return False
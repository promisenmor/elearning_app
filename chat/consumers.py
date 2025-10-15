import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info(f"Attempting WebSocket connection for user: {self.scope['user']}")
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            logger.warning(f"Unauthenticated user attempted to connect to WebSocket")
            await self.close()
            return

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        logger.info(f"Attempting to connect to room: {self.room_name}")
        self.room_group_name = f'chat_{self.room_name}'

        # Verify user has access to this room
        if not await self.can_access_room():
            logger.warning(f"User {self.user.username} does not have access to room {self.room_name}")
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"User {self.user.username} successfully connected to room {self.room_name}")
        await self.accept()

    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnected with code: {close_code}")
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
            logger.info(f"Found chat room: {room.name} for course: {room.course.title}")
            if self.user.is_instructor:
                has_access = room.course.instructor == self.user
                logger.info(f"Instructor access check: {has_access}")
                return has_access
            else:
                has_access = room.course.students.filter(id=self.user.id).exists()
                logger.info(f"Student access check: {has_access}")
                return has_access
        except ChatRoom.DoesNotExist:
            logger.error(f"Chat room not found: {self.room_name}")
            return False
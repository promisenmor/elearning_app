from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model

User = get_user_model()

class WebSocketAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        scope['user'] = await self.get_user(scope)
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user(self, scope):
        if 'session' not in scope:
            return AnonymousUser()
        
        session_key = scope['session'].session_key
        if not session_key:
            return AnonymousUser()
            
        try:
            user = User.objects.get(id=scope['session']['_auth_user_id'])
            return user
        except (User.DoesNotExist, KeyError):
            return AnonymousUser() 
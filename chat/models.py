from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from courses.models import Course

User = get_user_model()

class ChatRoom(models.Model):
    name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} - {self.name}"

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.user.username}: {self.content[:50]}' 
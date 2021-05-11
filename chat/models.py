from django.contrib.auth.models import AbstractUser
from django.db import models
#from datetime import now


class ChatUser(AbstractUser):
    def __str__(self):
        return self.get_full_name() if self.get_full_name() != "" else self.username


class Message(models.Model):
    sender = models.ForeignKey(ChatUser, models.CASCADE, related_name="messages", null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    room_name = models.CharField(max_length=100)
    content = models.CharField(max_length=140)

    def to_dict(self):

        return {
            'created_at' : self.created_at if self.created_at is not None else None,
            'room_name': self.room_name,
            'content': self.content
        }


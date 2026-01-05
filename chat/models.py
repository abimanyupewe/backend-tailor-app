from django.db import models
from django.contrib.auth import get_user_model
from users.models import TailorProfile

User = get_user_model()

class ChatRoom(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_as_customer')
    tailor = models.ForeignKey(TailorProfile, on_delete=models.CASCADE, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('customer', 'tailor')

    def __str__(self):
        return f"Chat: {self.customer.username} - {self.tailor.user.username}"

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.text[:20]}"

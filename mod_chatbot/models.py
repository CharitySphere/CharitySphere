from django.contrib.auth.models import User
from django.db import models


class ChatHistory(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chat_sessions"
    )
    user_message = models.TextField()
    bot_response = models.TextField()
    sentiment = models.CharField(max_length=50, blank=True, null=True)
    language = models.CharField(max_length=20, default="English")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"Chat with {self.user.username} at {self.timestamp}"

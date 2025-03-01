from django.db import models
import uuid

class Conversation(models.Model):
    # Conversation status
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'

    STATUS_CHOICES = [
        (OPEN, 'Open'),
        (CLOSED, 'Closed'),
    ]

    # Conversation fields
    id = models.UUIDField(primary_key=True)
    status = models.CharField(max_length=6, choices=STATUS_CHOICES, default=OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation {self.id} ({self.status})"


class Message(models.Model):
    # Message direction
    SENT = 'SENT'
    RECEIVED = 'RECEIVED'

    DIRECTION_CHOICES = [
        (SENT, 'Sent'),
        (RECEIVED, 'Received'),
    ]

    # Message fields
    id = models.UUIDField(primary_key=True)
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    direction = models.CharField(max_length=8, choices=DIRECTION_CHOICES)
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.id} ({self.direction})"

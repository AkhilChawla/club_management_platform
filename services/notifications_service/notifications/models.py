import uuid
from django.db import models


class Notification(models.Model):
    """Represents a notification sent by the notification service."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Event information
    event_type = models.CharField(max_length=50, help_text="Type of event that triggered this notification")
    event_data = models.JSONField(help_text="Original event data from the source service")
    
    # User information (extracted from event data)
    user_id = models.CharField(max_length=100, blank=True, help_text="ID of the user to notify")
    user_email = models.EmailField(blank=True, help_text="Email of the user to notify")
    user_name = models.CharField(max_length=200, blank=True, help_text="Name of the user to notify")
    
    # Notification content
    subject = models.CharField(max_length=200, help_text="Notification subject/title")
    message = models.TextField(help_text="Notification message content")
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True, help_text="When the notification was actually sent")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Source service information
    source_service = models.CharField(max_length=50, help_text="Which service generated the original event")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type']),
            models.Index(fields=['user_id']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self) -> str:
        return f"Notification {self.event_type} - {self.user_name or self.user_id} ({self.status})"

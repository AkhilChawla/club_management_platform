import uuid
from django.db import models


class Event(models.Model):
    """Represents an event created by a club."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    club_id = models.UUIDField()
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_time']

    def __str__(self) -> str:
        return self.name


class RSVP(models.Model):
    """Represents a student's RSVP to an event."""
    id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, related_name='rsvps', on_delete=models.CASCADE)
    user_id = models.CharField(max_length=100)
    user_name = models.CharField(max_length=200)
    rsvp_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user_id')
        ordering = ['rsvp_time']

    def __str__(self) -> str:
        return f"{self.user_name} RSVP'd"
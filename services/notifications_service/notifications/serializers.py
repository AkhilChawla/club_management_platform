"""Serializers for the notifications app."""

from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'event_type',
            'event_data',
            'user_id',
            'user_name',
            'user_email',
            'subject',
            'message',
            'status',
            'sent_at',
            'created_at',
            'updated_at',
            'source_service'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

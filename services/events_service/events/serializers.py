"""Serializers for the events service."""

from rest_framework import serializers
from .models import Event, RSVP


class EventSerializer(serializers.ModelSerializer):
    startTime = serializers.DateTimeField(source='start_time')
    endTime = serializers.DateTimeField(source='end_time')

    class Meta:
        model = Event
        fields = [
            'id',
            'club_id',
            'name',
            'description',
            'startTime',
            'endTime',
            'location',
        ]


class EventInputSerializer(serializers.ModelSerializer):
    startTime = serializers.DateTimeField(source='start_time')
    endTime = serializers.DateTimeField(source='end_time')

    class Meta:
        model = Event
        fields = [
            'club_id',
            'name',
            'description',
            'startTime',
            'endTime',
            'location',
        ]


class RSVPSerializer(serializers.ModelSerializer):
    rsvpTime = serializers.DateTimeField(source='rsvp_time', read_only=True)

    class Meta:
        model = RSVP
        fields = ['id', 'user_id', 'user_name', 'rsvpTime']
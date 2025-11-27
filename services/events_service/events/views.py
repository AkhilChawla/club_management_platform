"""API views for the events service."""

from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Event, RSVP
from .serializers import EventSerializer, EventInputSerializer, RSVPSerializer

import os
import json
try:
    import pika
except ImportError:
    pika = None

def publish_event(event_type: str, data: dict) -> None:
    if pika is None:
        return
    host = os.environ.get('RABBITMQ_HOST', 'localhost')
    user = os.environ.get('RABBITMQ_USER', 'guest')
    password = os.environ.get('RABBITMQ_PASS', 'guest')
    try:
        credentials = pika.PlainCredentials(user, password)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, credentials=credentials))
        channel = connection.channel()
        channel.queue_declare(queue='events', durable=True)
        message = json.dumps({'type': event_type, 'data': data})
        channel.basic_publish(exchange='', routing_key='events', body=message)
        connection.close()
    except Exception:
        pass


class EventListCreateView(generics.ListCreateAPIView):

    queryset = Event.objects.all()

    def get_serializer_class(self):
        return EventInputSerializer if self.request.method == 'POST' else EventSerializer

    def list(self, request, *args, **kwargs):
        club_id = request.query_params.get('clubId')
        events = self.get_queryset()
        if club_id:
            events = events.filter(club_id=club_id)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = EventInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.save()
        publish_event('event_created', {
            'id': str(event.id),
            'club_id': str(event.club_id),
            'name': event.name,
            'start_time': event.start_time.isoformat() if hasattr(event.start_time, 'isoformat') else None,
            'end_time': event.end_time.isoformat() if hasattr(event.end_time, 'isoformat') else None,
        })
        output = EventSerializer(event)
        return Response(output.data, status=status.HTTP_201_CREATED)


class EventDetailView(generics.RetrieveAPIView):

    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = 'pk'


class EventRSVPListCreateView(generics.ListCreateAPIView):

    serializer_class = RSVPSerializer

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        return RSVP.objects.filter(event_id=event_id)

    def list(self, request, *args, **kwargs):
        rsvps = self.get_queryset()
        serializer = RSVPSerializer(rsvps, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        event_id = self.kwargs.get('event_id')
        event = get_object_or_404(Event, pk=event_id)
        serializer = RSVPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rsvp = serializer.save(event=event)
        publish_event('rsvp_created', {
            'event_id': str(event.id),
            'rsvp_id': str(rsvp.id),
            'user_id': rsvp.user_id,
            'user_name': rsvp.user_name,
        })
        return Response(serializer.data, status=status.HTTP_201_CREATED)
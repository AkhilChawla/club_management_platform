"""API views for the payments service."""

from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import TicketType, Order
from .serializers import TicketTypeSerializer, OrderSerializer, OrderInputSerializer

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


class EventTicketsListView(generics.ListAPIView):

    serializer_class = TicketTypeSerializer

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        return TicketType.objects.filter(event_id=event_id)


class OrderCreateView(generics.CreateAPIView):

    serializer_class = OrderInputSerializer

    def create(self, request, *args, **kwargs):
        serializer = OrderInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        items = []
        for item in order.items.all():
            try:
                items.append({
                    'ticket_type_id': str(item.ticket_type_id),
                    'quantity': item.quantity,
                })
            except Exception:
                pass
        publish_event('order_created', {
            'id': str(order.id),
            'user_id': order.user_id,
            'items': items,
        })
        output = OrderSerializer(order)
        return Response(output.data, status=status.HTTP_201_CREATED)


class OrderDetailView(generics.RetrieveAPIView):

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'pk'
"""API views for the clubs service."""

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Club, Membership
from django.db import IntegrityError
from .serializers import (
    ClubSerializer,
    ClubInputSerializer,
    MembershipSerializer,
)

import os
import json
try:
    import pika
except ImportError:
    pika = None

def publish_event(event_type: str, data: dict) -> None:
    """Publish a JSON message to the RabbitMQ 'events' queue."""
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


class ClubListCreateView(generics.ListCreateAPIView):
    """List all clubs or create a new club."""

    queryset = Club.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ClubInputSerializer
        return ClubSerializer

    def list(self, request, *args, **kwargs):
        status_filter = request.query_params.get('status')
        qs = self.get_queryset()
        if not status_filter:
            qs = qs.filter(status='active')
        elif status_filter != 'all':
            qs = qs.filter(status=status_filter)
        serializer = ClubSerializer(qs, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer: ClubInputSerializer) -> Club:
        # New clubs start in pending_approval status.
        club = serializer.save(status='pending_approval')
        publish_event('club_created', {
            'id': str(club.id),
            'name': club.name,
            'status': club.status,
        })
        return club

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        club = self.perform_create(serializer)
        output_serializer = ClubSerializer(club)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class ClubDetailView(generics.RetrieveAPIView):
    """Retrieve a single club by its UUID."""

    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    lookup_field = 'pk'


class ClubMemberListCreateView(generics.ListCreateAPIView):
    """List members of a club or add the current user to the club."""

    serializer_class = MembershipSerializer

    def get_queryset(self):
        club_id = self.kwargs.get('club_id')
        return Membership.objects.filter(club_id=club_id)

    def list(self, request, *args, **kwargs):
        memberships = self.get_queryset()
        serializer = MembershipSerializer(memberships, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        club_id = self.kwargs.get('club_id')
        club = get_object_or_404(Club, pk=club_id)
        serializer = MembershipSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            membership = serializer.save(club=club)
        except IntegrityError:
            return Response(
                {"detail": "Member already exists for this club."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        publish_event('member_added', {
            'club_id': str(club.id),
            'member_id': str(membership.id),
            'user_id': membership.user_id,
            'user_name': membership.user_name,
            'role': membership.role,
        })
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ClubApproveView(APIView):
    """Endpoint to approve a club by setting its status to active."""

    def post(self, request, club_id: str, *args, **kwargs) -> Response:
        club = get_object_or_404(Club, pk=club_id)
        club.status = 'active'
        club.save(update_fields=['status'])
        publish_event('club_approved', {
            'id': str(club.id),
            'name': club.name,
        })
        serializer = ClubSerializer(club)
        return Response(serializer.data, status=status.HTTP_200_OK)

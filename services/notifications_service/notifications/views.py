"""API views for the notifications service."""

from rest_framework import generics, status
from rest_framework.response import Response
from django.db.models import Q

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    """List all notifications received by the service."""
    
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        """Get queryset with optional filtering."""
        queryset = Notification.objects.all()
        
        # Filter by event type if provided
        event_type = self.request.query_params.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        # Filter by status if provided
        notification_status = self.request.query_params.get('status')
        if notification_status:
            queryset = queryset.filter(status=notification_status)
        
        # Filter by source service if provided
        source_service = self.request.query_params.get('source_service')
        if source_service:
            queryset = queryset.filter(source_service=source_service)
        
        # Filter by user if provided
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Search in subject and message if search query provided
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(subject__icontains=search) | 
                Q(message__icontains=search) |
                Q(user_name__icontains=search)
            )
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """List notifications with additional statistics."""
        queryset = self.get_queryset()
        
        # Get paginated results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            
            # Add summary statistics
            total_count = queryset.count()
            status_counts = {}
            for status_choice in Notification.STATUS_CHOICES:
                status_counts[status_choice[0]] = queryset.filter(status=status_choice[0]).count()
            
            event_type_counts = {}
            for event_type in queryset.values_list('event_type', flat=True).distinct():
                event_type_counts[event_type] = queryset.filter(event_type=event_type).count()
            
            paginated_response.data['summary'] = {
                'total_notifications': total_count,
                'status_counts': status_counts,
                'event_type_counts': event_type_counts,
            }
            
            return paginated_response
        
        # If no pagination, return simple list
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

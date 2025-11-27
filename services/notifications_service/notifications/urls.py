"""URL configuration for the notifications app."""

from django.urls import path
from . import views

urlpatterns = [
    # List all notifications
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
]

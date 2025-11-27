"""URL patterns for the payments service."""

from django.urls import path
from . import views

urlpatterns = [
    path('events/<uuid:event_id>/tickets/', views.EventTicketsListView.as_view(), name='event-tickets'),
    path('orders/', views.OrderCreateView.as_view(), name='order-create'),
    path('orders/<uuid:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
]
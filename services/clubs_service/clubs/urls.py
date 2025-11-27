"""URL patterns for the clubs service."""

from django.urls import path
from . import views

urlpatterns = [
    path('clubs/', views.ClubListCreateView.as_view(), name='club-list'),
    path('clubs/<uuid:pk>/', views.ClubDetailView.as_view(), name='club-detail'),
    path('clubs/<uuid:club_id>/members/', views.ClubMemberListCreateView.as_view(), name='club-members'),
    path('clubs/<uuid:club_id>/approve/', views.ClubApproveView.as_view(), name='club-approve'),
]
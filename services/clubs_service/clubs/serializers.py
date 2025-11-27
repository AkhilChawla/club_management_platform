"""Serializers for the clubs service."""

from rest_framework import serializers
from .models import Club, Membership


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ['id', 'user_id', 'user_name', 'role', 'join_date']


class ClubSerializer(serializers.ModelSerializer):
    memberCount = serializers.IntegerField(source='member_count', read_only=True)

    class Meta:
        model = Club
        fields = ['id', 'name', 'description', 'status', 'memberCount']


class ClubInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ['name', 'description']
"""Serializers for the payments service."""

from typing import List
from rest_framework import serializers
from .models import TicketType, Order, OrderItem


class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = ['id', 'event_id', 'name', 'price', 'quantity']


class OrderItemSerializer(serializers.ModelSerializer):
    ticketTypeId = serializers.UUIDField(source='ticket_type.id', read_only=True)
    ticketTypeName = serializers.CharField(source='ticket_type.name', read_only=True)
    price = serializers.FloatField(source='ticket_type.price', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['ticketTypeId', 'ticketTypeName', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user_id', 'total_amount', 'status', 'created_at', 'items']


class OrderItemInputSerializer(serializers.Serializer):
    ticketTypeId = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)


class OrderInputSerializer(serializers.Serializer):
    userId = serializers.CharField(max_length=100)
    items = OrderItemInputSerializer(many=True)

    def validate(self, data):
        items_data: List[dict] = data['items']
        for item in items_data:
            try:
                ticket_type = TicketType.objects.get(pk=item['ticketTypeId'])
            except TicketType.DoesNotExist as exc:
                raise serializers.ValidationError(f"Ticket type {item['ticketTypeId']} not found") from exc
            if item['quantity'] > ticket_type.quantity:
                raise serializers.ValidationError(
                    f"Not enough tickets available for {ticket_type.name}. Only {ticket_type.quantity} left."
                )
        return data

    def create(self, validated_data):
        user_id = validated_data['userId']
        items_data = validated_data['items']
        total = 0.0
        order = Order.objects.create(user_id=user_id, total_amount=0, status='completed')
        for item in items_data:
            ticket_type = TicketType.objects.get(pk=item['ticketTypeId'])
            quantity = item['quantity']
            total += ticket_type.price * quantity
            OrderItem.objects.create(order=order, ticket_type=ticket_type, quantity=quantity)
            ticket_type.quantity -= quantity
            ticket_type.save()
        order.total_amount = total
        order.save()
        return order
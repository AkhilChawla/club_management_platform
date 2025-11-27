import uuid
from django.db import models


class TicketType(models.Model):
    """Represents a type of ticket for an event."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_id = models.UUIDField()
    name = models.CharField(max_length=200)
    price = models.FloatField()
    quantity = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.name} (${self.price:.2f})"


class Order(models.Model):
    """Represents an order for one or more tickets."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=100)
    total_amount = models.FloatField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Order {self.id}"


class OrderItem(models.Model):
    """Represents a line item within an order."""
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.quantity} x {self.ticket_type.name}"
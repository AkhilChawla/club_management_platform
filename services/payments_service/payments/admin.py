from django.contrib import admin
from .models import TicketType, Order, OrderItem

@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "event_id", "name", "price", "quantity")
    search_fields = ("name",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user_id", "total_amount", "status", "created_at")
    inlines = [OrderItemInline]
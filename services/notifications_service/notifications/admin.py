from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'user_name', 'user_email', 'subject', 'status', 'created_at', 'source_service']
    list_filter = ['event_type', 'status', 'source_service', 'created_at']
    search_fields = ['user_name', 'user_email', 'subject', 'message']
    readonly_fields = ['id', 'event_data', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('event_type', 'source_service', 'event_data')
        }),
        ('User Information', {
            'fields': ('user_id', 'user_name', 'user_email')
        }),
        ('Notification Content', {
            'fields': ('subject', 'message')
        }),
        ('Status', {
            'fields': ('status', 'sent_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

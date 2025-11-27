from django.contrib import admin
from .models import Event, RSVP

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "club_id", "start_time", "location")
    search_fields = ("name",)

@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "user_name", "rsvp_time")
    search_fields = ("user_name",)
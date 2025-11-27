from django.contrib import admin
from .models import Club, Membership

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "status", "member_count")
    search_fields = ("name",)

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("id", "club", "user_name", "role", "join_date")
    search_fields = ("user_name",)
    list_filter = ("role",)
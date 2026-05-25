from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'title', 'is_read', 'email_sent', 'created_at']
    list_filter = ['type', 'is_read', 'email_sent']
    search_fields = ['user__email', 'title']
    readonly_fields = ['created_at']

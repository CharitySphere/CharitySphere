from django.contrib import admin

from .models import EmergencyAlert


@admin.register(EmergencyAlert)
class EmergencyAlertAdmin(admin.ModelAdmin):
    list_display = ("title", "region", "severity", "is_active")
    list_filter = ("severity", "is_active", "region")
    search_fields = ("title", "description", "region")

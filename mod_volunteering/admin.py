from django.contrib import admin

from .models import (CampaignApplication, OrgInvitation, VolunteerCampaign,
                     VolunteerTask)


@admin.register(VolunteerCampaign)
class VolunteerCampaignAdmin(admin.ModelAdmin):
    list_display = ("title", "institution", "status", "created_at")
    list_filter = ("status", "institution")
    search_fields = ("title", "description")


@admin.register(VolunteerTask)
class VolunteerTaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "campaign",
        "institution",
        "date",
        "status",
        "assigned_volunteer",
    )
    list_filter = ("status", "date", "task_type")
    search_fields = ("title", "location")


@admin.register(CampaignApplication)
class CampaignApplicationAdmin(admin.ModelAdmin):
    list_display = ("campaign", "volunteer", "status", "applied_at")
    list_filter = ("status",)


@admin.register(OrgInvitation)
class OrgInvitationAdmin(admin.ModelAdmin):
    list_display = ("institution", "volunteer", "status", "sent_at")
    list_filter = ("status",)

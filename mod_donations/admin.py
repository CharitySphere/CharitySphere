from django.contrib import admin

from .models import DonationCampaign, DonationRecord


@admin.register(DonationCampaign)
class DonationCampaignAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "institution",
        "category",
        "goal_amount",
        "current_amount",
        "is_urgent",
        "created_at",
    )
    list_filter = ("category", "is_urgent", "institution")
    search_fields = ("title", "description")


@admin.register(DonationRecord)
class DonationRecordAdmin(admin.ModelAdmin):
    list_display = ("donor", "campaign", "amount", "timestamp")
    list_filter = ("campaign", "timestamp")
    search_fields = ("donor__user_profile__user__username", "campaign__title")

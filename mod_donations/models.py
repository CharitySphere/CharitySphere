from django.db import models
from django.db.models import Sum

from mod_authentication.models import Donor, Institution


class DonationCampaign(models.Model):
    CATEGORY_CHOICES = [
        ("food", "Food"),
        ("clothes", "Clothes"),
        ("hygiene", "Hygiene"),
        ("medicine", "Medicines"),
        ("funds", "Funds"),
    ]
    title = models.CharField(max_length=200)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    goal_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_urgent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Campaign Location
    location_name = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Explicit typing
    donationrecord_set: models.Manager["DonationRecord"]

    @property
    def current_amount(self):
        # Calculates sum of all records for this campaign
        return self.donationrecord_set.aggregate(total=Sum("amount"))["total"] or 0

    @property
    def get_percentage(self):
        if not self.goal_amount or self.goal_amount <= 0:
            return 0
        percentage = (self.current_amount / self.goal_amount) * 100
        return min(int(percentage), 100)

    def __str__(self):
        return self.title


class DonationRecord(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending Pickup"),
        ("shipped", "In Transit"),
        ("received", "Received"),
    ]

    donor = models.ForeignKey(Donor, on_delete=models.SET_NULL, null=True)
    campaign = models.ForeignKey(DonationCampaign, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    item_details = models.TextField(blank=True)  # For physical items
    timestamp = models.DateTimeField(auto_now_add=True)

    # Item Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    current_location = models.CharField(max_length=255, blank=True, help_text="Current city or hub")

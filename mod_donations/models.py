from django.db import models
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
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_urgent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class DonationRecord(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.SET_NULL, null=True)
    campaign = models.ForeignKey(DonationCampaign, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    item_details = models.TextField(blank=True)  # For physical items
    timestamp = models.DateTimeField(auto_now_add=True)

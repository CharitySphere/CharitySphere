from django.db import models
from mod_authentication.models import Volunteer, Institution


class VolunteerCampaign(models.Model):
    STATUS_CHOICES = [("pending", "Pending"), ("active", "Active"), ("completed", "Completed")]
    title = models.CharField(max_length=200)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="campaigns")
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class VolunteerTask(models.Model):
    STATUS_CHOICES = [("open", "Open"), ("in_progress", "In Progress"), ("completed", "Completed")]
    campaign = models.ForeignKey(VolunteerCampaign, on_delete=models.CASCADE, related_name="tasks", null=True)
    title = models.CharField(max_length=200)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    date = models.DateField()
    location = models.CharField(max_length=255)
    task_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    description = models.TextField()
    assigned_volunteer = models.ForeignKey(Volunteer, on_delete=models.SET_NULL, null=True, blank=True)


class CampaignApplication(models.Model):
    STATUS_CHOICES = [("pending", "Pending"), ("accepted", "Accepted"), ("rejected", "Rejected")]
    campaign = models.ForeignKey(VolunteerCampaign, on_delete=models.CASCADE, related_name="applications")
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    applied_at = models.DateTimeField(auto_now_add=True)


class OrgInvitation(models.Model):
    """Request from Institution to Volunteer to join the organization"""
    STATUS_CHOICES = [("pending", "Pending"), ("accepted", "Accepted"), ("rejected", "Rejected")]
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    sent_at = models.DateTimeField(auto_now_add=True)

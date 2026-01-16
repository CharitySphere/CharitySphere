from django.db import models


class EmergencyAlert(models.Model):
    region = models.CharField(max_length=100)
    title = models.CharField(max_length=200)  # eg: Kerala Flood Relief
    description = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_active = models.BooleanField(default=True)
    severity = models.CharField(max_length=20, default="High")

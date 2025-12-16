from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    USER_TYPE_CHOICES = (
        ('donor', 'Donor'),
        ('volunteer', 'Volunteer'),
        ('institution', 'Institution'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.user_type}"

class Donor(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    # Donor-specific fields
    donation_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class Volunteer(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    # Volunteer-specific fields
    skills = models.TextField(blank=True)
    availability = models.CharField(max_length=100, blank=True)

class Institution(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    # Institution-specific fields
    organization_name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=100)

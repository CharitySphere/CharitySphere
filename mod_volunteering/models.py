from django.db import models
from mod_authentication.models import Volunteer, Institution


class VolunteerTask(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]
    title = models.CharField(max_length=200)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    date = models.DateField()
    location = models.CharField(max_length=255)
    task_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    description = models.TextField()


class TaskApplication(models.Model):
    task = models.ForeignKey(VolunteerTask, on_delete=models.CASCADE)
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)

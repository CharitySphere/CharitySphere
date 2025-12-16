from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Donor, Institution, UserProfile, Volunteer


class DonorRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=True)
        profile = UserProfile.objects.create(user=user, user_type="donor")
        Donor.objects.create(user_profile=profile)
        return user


class VolunteerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    skills = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=True)
        profile = UserProfile.objects.create(user=user, user_type="volunteer")
        Volunteer.objects.create(
            user_profile=profile, skills=self.cleaned_data.get("skills", "")
        )
        return user


class InstitutionRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    organization_name = forms.CharField(max_length=200)
    registration_number = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=True)
        profile = UserProfile.objects.create(user=user, user_type="institution")
        Institution.objects.create(
            user_profile=profile,
            organization_name=self.cleaned_data["organization_name"],
            registration_number=self.cleaned_data["registration_number"],
        )
        return user

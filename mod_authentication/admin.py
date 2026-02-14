from django.contrib import admin

from .models import Donor, Institution, UserProfile, Volunteer


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "user_type")
    list_filter = ("user_type",)
    search_fields = ("user__username", "user__email")


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ("user_profile",)
    search_fields = ("user_profile__user__username",)


@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ("user_profile", "availability")
    search_fields = ("user_profile__user__username", "skills")


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("organization_name", "registration_number", "user_profile")
    search_fields = ("organization_name", "registration_number")

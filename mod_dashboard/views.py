from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from mod_authentication.models import (Donor, Institution, UserProfile,
                                       Volunteer)


@login_required
def dashboard(request):
    """Redirect to appropriate dashboard based on user type"""
    try:
        print(f"request.user: {request.user}, {request.user.username}, {request.user.id}")
        user_profile = UserProfile.objects.get(user=request.user)
        user_type = user_profile.user_type

        if user_type == "donor":
            return redirect("donor_dashboard")
        elif user_type == "volunteer":
            return redirect("volunteer_dashboard")
        elif user_type == "institution":
            return redirect("institution_dashboard")
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found. Please contact support.")
        return redirect("login")

    return redirect("login")


@login_required
def donor_dashboard(request):
    """Dashboard for donors"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)

        # Verify user is a donor
        if user_profile.user_type != "donor":
            messages.error(request, "Access denied. This dashboard is for donors only.")
            return redirect("dashboard")

        donor = Donor.objects.get(user_profile=user_profile)

        # Calculate statistics
        total_donations = donor.donation_amount
        active_campaigns = 0  # Placeholder - implement when you add campaigns
        impact_score = int(total_donations / 10) if total_donations > 0 else 0

        # Recent activities (placeholder)
        recent_activities = []

        context = {
            "user_profile": user_profile,
            "donor": donor,
            "total_donations": total_donations,
            "active_campaigns": active_campaigns,
            "impact_score": impact_score,
            "recent_activities": recent_activities,
        }

        return render(request, "mod_dashboard/donor_dashboard.html", context)

    except (UserProfile.DoesNotExist, Donor.DoesNotExist):
        messages.error(request, "Donor profile not found.")
        return redirect("dashboard")


@login_required
def volunteer_dashboard(request):
    """Dashboard for volunteers"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)

        # Verify user is a volunteer
        if user_profile.user_type != "volunteer":
            messages.error(
                request, "Access denied. This dashboard is for volunteers only."
            )
            return redirect("dashboard")

        volunteer = Volunteer.objects.get(user_profile=user_profile)

        # Calculate statistics
        hours_volunteered = 0  # Placeholder - implement when you add time tracking
        upcoming_events = 0  # Placeholder
        completed_projects = 0  # Placeholder

        # Recent opportunities (placeholder)
        recent_opportunities = []

        context = {
            "user_profile": user_profile,
            "volunteer": volunteer,
            "hours_volunteered": hours_volunteered,
            "upcoming_events": upcoming_events,
            "completed_projects": completed_projects,
            "recent_opportunities": recent_opportunities,
        }

        return render(request, "mod_dashboard/volunteer_dashboard.html", context)

    except (UserProfile.DoesNotExist, Volunteer.DoesNotExist):
        messages.error(request, "Volunteer profile not found.")
        return redirect("dashboard")


@login_required
def institution_dashboard(request):
    """Dashboard for institutions"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)

        # Verify user is an institution
        if user_profile.user_type != "institution":
            messages.error(
                request, "Access denied. This dashboard is for institutions only."
            )
            return redirect("dashboard")

        institution = Institution.objects.get(user_profile=user_profile)

        # Calculate statistics
        active_campaigns = 0  # Placeholder
        active_volunteers = 0  # Placeholder
        funds_raised = 0  # Placeholder

        # Recent activity (placeholder)
        recent_activities = []

        context = {
            "user_profile": user_profile,
            "institution": institution,
            "active_campaigns": active_campaigns,
            "active_volunteers": active_volunteers,
            "funds_raised": funds_raised,
            "recent_activities": recent_activities,
        }

        return render(request, "mod_dashboard/institution_dashboard.html", context)

    except (UserProfile.DoesNotExist, Institution.DoesNotExist):
        messages.error(request, "Institution profile not found.")
        return redirect("dashboard")


@login_required
def profile_settings(request):
    """User profile settings page"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)

        # Get type-specific profile
        type_profile = None
        if user_profile.user_type == "donor":
            type_profile = Donor.objects.get(user_profile=user_profile)
        elif user_profile.user_type == "volunteer":
            type_profile = Volunteer.objects.get(user_profile=user_profile)
        elif user_profile.user_type == "institution":
            type_profile = Institution.objects.get(user_profile=user_profile)

        if request.method == "POST":
            # Update user info
            request.user.first_name = request.POST.get("first_name", "")
            request.user.last_name = request.POST.get("last_name", "")
            request.user.email = request.POST.get("email", "")
            request.user.save()

            # Update type-specific info
            if user_profile.user_type == "volunteer":
                type_profile.skills = request.POST.get("skills", "")
                type_profile.availability = request.POST.get("availability", "")
                type_profile.save()
            elif user_profile.user_type == "institution":
                type_profile.organization_name = request.POST.get(
                    "organization_name", ""
                )
                type_profile.save()

            messages.success(request, "Profile updated successfully!")
            return redirect("profile_settings")

        context = {
            "user_profile": user_profile,
            "type_profile": type_profile,
        }

        return render(request, "mod_dashboard/profile_settings.html", context)

    except UserProfile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect("dashboard")

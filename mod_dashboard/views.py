from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from mod_authentication.models import (Donor, Institution, UserProfile,
                                       Volunteer)
from mod_donations.models import DonationCampaign, DonationRecord
from mod_reputation.models import ReputationScore
from mod_volunteering.models import VolunteerCampaign, CampaignApplication, OrgInvitation


@login_required
def dashboard(request):
    """Redirect to appropriate dashboard based on user type"""
    try:
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
    user_profile = get_object_or_404(UserProfile, user=request.user)
    donor = get_object_or_404(Donor, user_profile=user_profile)

    donations_qs = DonationRecord.objects.filter(donor=donor)
    total_donations = (
        DonationRecord.objects.filter(donor=donor).aggregate(Sum("amount"))[
            "amount__sum"
        ]
        or 0
    )
    active_campaigns = DonationCampaign.objects.count()

    # IMPACT SCORE SYSTEM
    # ===================
    # Base: 1 point per 10 currency units
    base_points = float(total_donations) / 10

    # Bonus: 50 points for every urgent campaign contribution
    urgent_bonus = donations_qs.filter(campaign__is_urgent=True).count() * 50

    # Bonus: 20 points for every unique organization supported
    diversity_bonus = donations_qs.values('campaign__institution').distinct().count() * 20

    impact_score = int(base_points + urgent_bonus + diversity_bonus)
    rep, _ = ReputationScore.objects.get_or_create(user_profile=user_profile)
    rep.score = impact_score
    rep.save()

    # IMPACT METRICS (CATEGORY BREAKDOWN)
    # ===================================
    meals = DonationRecord.objects.filter(
        donor=donor, campaign__category="food"
    ).count()
    clothes = DonationRecord.objects.filter(
        donor=donor, campaign__category="clothes"
    ).count()
    recent_activities = DonationRecord.objects.filter(donor=donor).order_by(
        "-timestamp"
    )[:5]

    context = {
        "total_donations": total_donations,
        "active_campaigns": active_campaigns,
        "impact_score": impact_score,
        "recent_activities": recent_activities,
        "meals_count": meals,
        "clothes_count": clothes,
    }
    return render(request, "donor_dashboard.html", context)


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

        return render(request, "volunteer_dashboard.html", context)

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

        # Metrics
        v_campaigns = VolunteerCampaign.objects.filter(
            institution=institution, status="active"
        )
        d_campaigns = DonationCampaign.objects.filter(institution=institution)
        active_campaigns_count = v_campaigns.count() + d_campaigns.count()

        # Total funds raised across all donation campaigns
        funds_raised = (
            DonationRecord.objects.filter(campaign__institution=institution).aggregate(
                Sum("amount")
            )["amount__sum"]
            or 0
        )

        # Unique active volunteers (Accepted applications OR Accepted invitations)
        active_volunteers = Volunteer.objects.filter(
            campaignapplication__campaign__institution=institution,
            campaignapplication__status='accepted'
        ).distinct().count()

        # Notification Badges
        pending_apps = CampaignApplication.objects.filter(campaign__institution=institution, status='pending').count()
        pending_invites = OrgInvitation.objects.filter(institution=institution, status='pending').count()

        recent_donations = DonationRecord.objects.filter(campaign__institution=institution).order_by('-timestamp')[:5]

        context = {
            "institution": institution,
            "active_campaigns": active_campaigns_count,
            "active_volunteers": active_volunteers,
            "funds_raised": funds_raised,
            "pending_apps": pending_apps,
            "pending_invites": pending_invites,
            "recent_donations": recent_donations,
            "v_campaigns": v_campaigns[:3], # Show a few active volunteer campaigns
        }

        return render(request, "institution_dashboard.html", context)

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
                # HACK: Duplication for LSP static typing :/
                type_profile = Volunteer.objects.get(user_profile=user_profile)
                type_profile.skills = request.POST.get("skills", "")
                type_profile.availability = request.POST.get("availability", "")
                type_profile.save()
            elif user_profile.user_type == "institution":
                # HACK: Duplication for LSP static typing :/
                type_profile = Institution.objects.get(user_profile=user_profile)
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

        return render(request, "profile_settings.html", context)

    except UserProfile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect("dashboard")

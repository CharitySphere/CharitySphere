from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render

from mod_authentication.models import Donor, UserProfile

from .models import DonationCampaign, DonationRecord, Institution


@login_required
def campaign_list(request):
    """List all active donation campaigns"""
    campaigns = DonationCampaign.objects.annotate(
        calc_current=Sum("donationrecord__amount")
    ).order_by("-is_urgent", "-created_at")

    # Filter by category if specified
    category = request.GET.get("category")
    if category:
        campaigns = campaigns.filter(category=category)

    context = {
        "campaigns": campaigns,
        "selected_category": category,
        "categories": DonationCampaign.CATEGORY_CHOICES,
    }
    return render(request, "donation/campaign_list.html", context)


@login_required
def campaign_detail(request, campaign_id):
    """View campaign details and make donations"""
    campaign = get_object_or_404(DonationCampaign, id=campaign_id)

    # Get donation history for this campaign
    donations = DonationRecord.objects.filter(campaign=campaign).order_by("-timestamp")[
        :10
    ]

    # Calculate progress percentage
    progress_percentage = 0
    if campaign.goal_amount > 0:
        progress_percentage = min(
            (campaign.current_amount / campaign.goal_amount) * 100, 100
        )

    context = {
        "campaign": campaign,
        "donations": donations,
        "progress_percentage": progress_percentage,
    }
    return render(request, "donation/campaign_detail.html", context)


@login_required
def make_donation(request, campaign_id):
    """Process donation to a campaign"""
    campaign = get_object_or_404(DonationCampaign, id=campaign_id)

    try:
        user_profile = UserProfile.objects.get(user=request.user)

        if user_profile.user_type != "donor":
            messages.error(request, "Only donors can make donations.")
            return redirect("campaign_detail", campaign_id=campaign_id)

        donor = Donor.objects.get(user_profile=user_profile)

        if request.method == "POST":
            donation_type = request.POST.get("donation_type")
            amount = 0
            details = ""

            if donation_type == "money":
                amount = float(request.POST.get("amount", 0))
                payment_method = request.POST.get("payment_method")
                details = f"Payment via {payment_method}"
            elif donation_type == "items":
                amount = float(request.POST.get("estimated_value", 0))
                details = request.POST.get("item_description")

            if amount <= 0:
                messages.error(request, "Please enter a valid amount or value.")
                return redirect("donations:campaign_detail", campaign_id=campaign_id)

            DonationRecord.objects.create(
                donor=donor, campaign=campaign, amount=amount, item_details=details
            )

            messages.success(
                request, f"Thank you! Your donation has been processed successfully."
            )
            return redirect("donations:campaign_detail", campaign_id=campaign_id)

    except (UserProfile.DoesNotExist, Donor.DoesNotExist):
        messages.error(request, "Donor profile not found.")
    return redirect("donations:campaign_detail", campaign_id=campaign_id)


@login_required
def donation_history(request):
    """View donation history for logged-in donor"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)

        if user_profile.user_type != "donor":
            messages.error(request, "Access denied.")
            return redirect("dashboard")

        donor = Donor.objects.get(user_profile=user_profile)
        donations = DonationRecord.objects.filter(donor=donor).order_by("-timestamp")

        context = {
            "donations": donations,
            "donor": donor,
        }
        return render(request, "donation/donation_history.html", context)

    except (UserProfile.DoesNotExist, Donor.DoesNotExist):
        messages.error(request, "Donor profile not found.")
        return redirect("dashboard")


@login_required
def institution_donation_campaigns(request):
    """List and manage donation campaigns for an institution"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != "institution":
            return redirect("dashboard")

        institution = Institution.objects.get(user_profile=user_profile)
        # Fetch campaigns and annotate them with total records and amount raised
        campaigns = (
            DonationCampaign.objects.filter(institution=institution)
            .annotate(total_donors=Count("donationrecord", distinct=True))
            .order_by("-created_at")
        )

        return render(
            request,
            "donation/institution_campaigns.html",
            {"campaigns": campaigns, "institution": institution},
        )
    except (UserProfile.DoesNotExist, Institution.DoesNotExist):
        return redirect("dashboard")


@login_required
def manage_donation_campaign(request, campaign_id=None):
    """Create or update a donation campaign"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    institution = get_object_or_404(Institution, user_profile=user_profile)

    if request.method == "POST":
        title = request.POST.get("title")
        category = request.POST.get("category")
        description = request.POST.get("description")
        goal_amount = request.POST.get("goal_amount")
        is_urgent = request.POST.get("is_urgent") == "on"

        if campaign_id:
            campaign = get_object_or_404(
                DonationCampaign, id=campaign_id, institution=institution
            )
            campaign.title = title
            campaign.category = category
            campaign.description = description
            campaign.goal_amount = goal_amount
            campaign.is_urgent = is_urgent
            campaign.save()
            messages.success(request, "Donation campaign updated.")
        else:
            DonationCampaign.objects.create(
                institution=institution,
                title=title,
                category=category,
                description=description,
                goal_amount=goal_amount,
                is_urgent=is_urgent,
            )
            messages.success(request, "Donation campaign launched successfully.")
    return redirect("donations:institution_donation_campaigns")


@login_required
def delete_donation_campaign(request, campaign_id):
    """Delete a campaign if it has no donations yet"""
    if request.method == "POST":
        user_profile = get_object_or_404(UserProfile, user=request.user)
        institution = get_object_or_404(Institution, user_profile=user_profile)
        campaign = get_object_or_404(
            DonationCampaign, id=campaign_id, institution=institution
        )

        if campaign.donationrecord_set.exists():
            messages.error(
                request, "Cannot delete a campaign that has already received donations."
            )
        else:
            campaign.delete()
            messages.success(request, "Campaign removed.")

    return redirect("donations:institution_donation_campaigns")

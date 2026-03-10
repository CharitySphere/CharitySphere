import os

import razorpay
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

from mod_authentication.models import Donor, UserProfile

from .models import DonationCampaign, DonationRecord, Institution

load_dotenv()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


def get_donor_or_error(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != "donor":
            return None, "Only donors can perform this action."
        return Donor.objects.get(user_profile=user_profile), None
    except (UserProfile.DoesNotExist, Donor.DoesNotExist):
        return None, "Donor profile not found."


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

                if amount <= 0:
                    messages.error(request, "Please enter a valid amount or value.")
                    return redirect(
                        "donations:campaign_detail", campaign_id=campaign_id
                    )

                DonationRecord.objects.create(
                    donor=donor,
                    campaign=campaign,
                    amount=amount,
                    item_details=details,
                )

                messages.success(
                    request,
                    f"Thank you! Your donation has been processed successfully.",
                )

            elif donation_type == "items":
                amount = float(request.POST.get("estimated_value", 0))
                details = request.POST.get("item_description")
                # Default to profile location if not provided
                location = donor.user_profile.address
                lat = donor.user_profile.latitude
                lng = donor.user_profile.longitude

                DonationRecord.objects.create(
                    donor=donor,
                    campaign=campaign,
                    amount=amount,
                    item_details=details,
                    current_location=location,
                    latitude=lat,
                    longitude=lng,
                    status="pending",
                )

                messages.success(
                    request, "Donation item logged. Please arrange for shipping/pickup."
                )
                return redirect("donations:campaign_detail", campaign_id=campaign_id)

            return redirect("donations:campaign_detail", campaign_id=campaign_id)

    except (UserProfile.DoesNotExist, Donor.DoesNotExist):
        messages.error(request, "Donor profile not found.")
    return redirect("donations:campaign_detail", campaign_id=campaign_id)


@login_required
def razorpay_create_order(request, campaign_id):
    """API view to initialize Razorpay order"""
    campaign = get_object_or_404(DonationCampaign, id=campaign_id)
    donor, error = get_donor_or_error(request)
    if error:
        return JsonResponse({"error": error}, status=403)

    try:
        amount = float(request.POST.get("amount", 0))
        if amount < 1:
            return JsonResponse({"error": "Minimum donation is ₹1"}, status=400)

        razorpay_order = razorpay_client.order.create(
            {"amount": int(amount * 100), "currency": "INR", "payment_capture": "1"}
        )

        return JsonResponse(
            {
                "order_id": razorpay_order["id"],
                "amount": amount,  # This is returned to frontend for the Modal
                "key_id": RAZORPAY_KEY_ID,
                "campaign_title": campaign.title,
                "user_email": request.user.email,
            }
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
@csrf_exempt
def verify_payment(request):
    """Verifies Razorpay Signature and saves donation"""
    if request.method == "POST":
        data = request.POST

        # Verify the signature
        params_dict = {
            "razorpay_order_id": data.get("razorpay_order_id"),
            "razorpay_payment_id": data.get("razorpay_payment_id"),
            "razorpay_signature": data.get("razorpay_signature"),
        }

        try:
            razorpay_client.utility.verify_payment_signature(params_dict)

            # Signature is valid. Create the record
            campaign_id = data.get("campaign_id")
            campaign = DonationCampaign.objects.get(id=campaign_id)
            amount = float(data.get("amount"))

            user_profile = UserProfile.objects.get(user=request.user)
            donor = Donor.objects.get(user_profile=user_profile)

            DonationRecord.objects.create(
                donor=donor,
                campaign=campaign,
                amount=amount,
                item_details=f"Razorpay Payment ID: {data.get('razorpay_payment_id')}",
            )

            messages.success(
                request, "Payment successful! Thank you for your donation."
            )
            return JsonResponse({"status": "success"})

        except Exception as e:
            return JsonResponse({"status": "failed", "error": str(e)}, status=400)

    return JsonResponse({"status": "failed", "error": "Invalid request"}, status=400)


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
            {
                "campaigns": campaigns,
                "institution": institution,
                "categories": DonationCampaign.CATEGORY_CHOICES,
            },
        )
    except (UserProfile.DoesNotExist, Institution.DoesNotExist):
        return redirect("dashboard")


@login_required
def update_donation_status(request, donation_id):
    """Institution updates the tracking status of a donation item"""
    donation = get_object_or_404(DonationRecord, id=donation_id)
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if (
        user_profile.user_type != "institution"
        or donation.campaign.institution.user_profile != user_profile
    ):
        messages.error(request, "Unauthorized.")
        return redirect("dashboard")

    if request.method == "POST":
        new_status = request.POST.get("status")
        new_location = request.POST.get("current_location")

        donation.status = new_status
        if new_location:
            donation.current_location = new_location
        donation.save()
        messages.success(
            request, f"Donation status updated to {donation.get_status_display()}."
        )

    return redirect("donations:institution_donation_campaigns")


@login_required
def manage_donation_campaign(request, campaign_id=None):
    # Updated to include latitude/longitude/location_name from POST
    user_profile = get_object_or_404(UserProfile, user=request.user)
    institution = get_object_or_404(Institution, user_profile=user_profile)

    if request.method == "POST":
        title = request.POST.get("title")
        category = request.POST.get("category")
        description = request.POST.get("description")
        goal_amount = request.POST.get("goal_amount")
        is_urgent = request.POST.get("is_urgent") == "on"

        location_name = request.POST.get("location_name")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")

        if campaign_id:
            campaign = get_object_or_404(
                DonationCampaign, id=campaign_id, institution=institution
            )
            campaign.title = title
            campaign.category = category
            campaign.description = description
            campaign.goal_amount = goal_amount
            campaign.is_urgent = is_urgent
            campaign.location_name = location_name
            campaign.latitude = latitude if latitude else None
            campaign.longitude = longitude if longitude else None
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
                location_name=location_name,
                latitude=latitude if latitude else None,
                longitude=longitude if longitude else None,
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


@login_required
def update_item_status(request, record_id):
    """Commit 2: Institution updates the location/status of a physical donation"""
    record = get_object_or_404(DonationRecord, id=record_id)
    if record.campaign.institution.user_profile.user != request.user:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    if request.method == "POST":
        record.status = request.POST.get("status")
        record.current_location = request.POST.get("current_location")
        record.save()
        messages.success(
            request,
            f"Status updated for donation from {record.donor.user_profile.user.username}",
        )

    return redirect("donations:institution_donation_campaigns")


@login_required
def track_item(request, record_id):
    record = get_object_or_404(DonationRecord, id=record_id)
    if record.donor.user_profile.user != request.user:
        messages.error(request, "Unauthorized")
        return redirect("dashboard")

    # Define the status sequence with enriched metadata
    status_configs = [
        {
            "slug": "pending",
            "label": "Ready your package",
            "desc": "Prepare your items for collection or drop-off.",
            "icon": "bi-box-seam"
        },
        {
            "slug": "collected",
            "label": "Picked Up",
            "desc": "Item has been collected by our logistics partner.",
            "icon": "bi-truck-flatbed"
        },
        {
            "slug": "transit",
            "label": "In Transit",
            "desc": f"Moving towards destination. Currently at: {record.current_location or 'Processing Hub'}",
            "icon": "bi-geo-alt-fill"
        },
        {
            "slug": "received",
            "label": "At Institution",
            "desc": f"Successfully reached {record.campaign.institution.organization_name}.",
            "icon": "bi-building-check"
        },
        {
            "slug": "delivered",
            "label": "Distributed",
            "desc": "Items have been handed over to the beneficiaries.",
            "icon": "bi-heart-fill"
        }
    ]

    status_order = [s["slug"] for s in status_configs]

    try:
        current_idx = status_order.index(record.status)
    except ValueError:
        current_idx = 0

    progress_pct = ((current_idx) / (len(status_order) - 1)) * 100

    steps_data = []
    for i, config in enumerate(status_configs):
        steps_data.append({
            "label": config["label"],
            "description": config["desc"],
            "icon": config["icon"],
            "is_complete": i < current_idx,
            "is_current": i == current_idx,
            "display_number": i + 1,
        })

    return render(
        request,
        "donation/track_item.html",
        {
            "id": f"CS-00{record.pk}-{record.timestamp.strftime('%Y%m%d')}",
            "record": record,
            "progress_pct": progress_pct,
            "steps_data": steps_data,
            "current_step": status_configs[current_idx]
        },
    )


@login_required
def manage_transit_items(request):
    """Institution view to manage all items in progress"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.user_type != "institution":
        return redirect("dashboard")

    institution = get_object_or_404(Institution, user_profile=user_profile)
    items_in_transit = (
        DonationRecord.objects.filter(campaign__institution=institution)
        .exclude(status="delivered")
        .order_by("-timestamp")
    )

    if request.method == "POST":
        record_id = request.POST.get("record_id")
        record = get_object_or_404(
            DonationRecord, id=record_id, campaign__institution=institution
        )

        record.status = request.POST.get("status")
        record.current_location = request.POST.get("current_location")

        # Institution can override donor's initial inputs
        record.amount = request.POST.get("amount")
        record.item_details = request.POST.get("item_details")

        # Update coordinates if provided (for map tracking)
        lat = request.POST.get("latitude")
        lng = request.POST.get("longitude")
        if lat and lng:
            record.latitude = lat
            record.longitude = lng

        record.save()
        messages.success(request, f"Updated tracking for record #{record.pk}")
        return redirect("donations:manage_transit_items")

    return render(request, "donation/manage_transit.html", {"items": items_in_transit})

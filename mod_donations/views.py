from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404

from mod_authentication.models import Donor, Institution, UserProfile
from .models import DonationCampaign, DonationRecord


@login_required
def campaign_list(request):
    """List all active donation campaigns"""
    campaigns = DonationCampaign.objects.all().order_by('-is_urgent', '-created_at')

    # Filter by category if specified
    category = request.GET.get('category')
    if category:
        campaigns = campaigns.filter(category=category)

    context = {
        'campaigns': campaigns,
        'selected_category': category,
        'categories': DonationCampaign.CATEGORY_CHOICES,
    }
    return render(request, 'donation/campaign_list.html', context)


@login_required
def campaign_detail(request, campaign_id):
    """View campaign details and make donations"""
    campaign = get_object_or_404(DonationCampaign, id=campaign_id)

    # Get donation history for this campaign
    donations = DonationRecord.objects.filter(campaign=campaign).order_by('-timestamp')[:10]

    # Calculate progress percentage
    progress_percentage = 0
    if campaign.goal_amount > 0:
        progress_percentage = min((campaign.current_amount / campaign.goal_amount) * 100, 100)

    context = {
        'campaign': campaign,
        'donations': donations,
        'progress_percentage': progress_percentage,
    }
    return render(request, 'donation/campaign_detail.html', context)


@login_required
def make_donation(request, campaign_id):
    """Process donation to a campaign"""
    campaign = get_object_or_404(DonationCampaign, id=campaign_id)

    try:
        user_profile = UserProfile.objects.get(user=request.user)

        if user_profile.user_type != 'donor':
            messages.error(request, "Only donors can make donations.")
            return redirect('campaign_detail', campaign_id=campaign_id)

        donor = Donor.objects.get(user_profile=user_profile)

        if request.method == 'POST':
            donation_type = request.POST.get('donation_type')

            if donation_type == 'money':
                amount = float(request.POST.get('amount', 0))

                if amount <= 0:
                    messages.error(request, "Please enter a valid amount.")
                    return redirect('campaign_detail', campaign_id=campaign_id)

                # Mock payment processing
                payment_method = request.POST.get('payment_method')

                # Create donation record
                donation = DonationRecord.objects.create(
                    donor=donor,
                    campaign=campaign,
                    amount=amount,
                    item_details=f"Payment via {payment_method}"
                )

                # Update campaign and donor totals
                campaign.current_amount += amount
                campaign.save()

                donor.donation_amount += amount
                donor.save()

                messages.success(request, f"Thank you! Your donation of ₹{amount} has been processed successfully.")

            elif donation_type == 'items':
                item_description = request.POST.get('item_description')
                estimated_value = float(request.POST.get('estimated_value', 0))

                if not item_description:
                    messages.error(request, "Please describe the items you're donating.")
                    return redirect('campaign_detail', campaign_id=campaign_id)

                # Create donation record
                donation = DonationRecord.objects.create(
                    donor=donor,
                    campaign=campaign,
                    amount=estimated_value,
                    item_details=item_description
                )

                # Update campaign total
                campaign.current_amount += estimated_value
                campaign.save()

                donor.donation_amount += estimated_value
                donor.save()

                messages.success(request, "Thank you! Your item donation has been recorded successfully.")

            return redirect('campaign_detail', campaign_id=campaign_id)

    except (UserProfile.DoesNotExist, Donor.DoesNotExist):
        messages.error(request, "Donor profile not found.")
        return redirect('campaign_detail', campaign_id=campaign_id)

    return redirect('campaign_detail', campaign_id=campaign_id)


@login_required
def donation_history(request):
    """View donation history for logged-in donor"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)

        if user_profile.user_type != 'donor':
            messages.error(request, "Access denied.")
            return redirect('dashboard')

        donor = Donor.objects.get(user_profile=user_profile)
        donations = DonationRecord.objects.filter(donor=donor).order_by('-timestamp')

        context = {
            'donations': donations,
            'donor': donor,
        }
        return render(request, 'donation/donation_history.html', context)

    except (UserProfile.DoesNotExist, Donor.DoesNotExist):
        messages.error(request, "Donor profile not found.")
        return redirect('dashboard')

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render

from mod_authentication.models import Donor, UserProfile
from mod_donations.models import DonationRecord

from .models import ReputationScore
from .utils import get_impact_score


@login_required
def impact_score_detail(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.user_type != "donor":
        return redirect("dashboard")

    donor = get_object_or_404(Donor, user_profile=user_profile)
    donations = DonationRecord.objects.filter(donor=donor).order_by("-timestamp")

    # Impact Score
    impact_score = get_impact_score(donor)
    total_score = impact_score["total_score"]
    base_points = impact_score["base_points"]
    urgency_points = impact_score["urgency_points"]
    diversity_points = impact_score["diversity_points"]
    item_points = impact_score["item_points"]

    # Donations
    financial_total = donations.aggregate(Sum("amount"))["amount__sum"] or 0
    urgent_donations = donations.filter(campaign__is_urgent=True)
    unique_orgs = donations.values("campaign__institution").distinct().count()

    # Update the actual ReputationScore model
    rep, _ = ReputationScore.objects.get_or_create(user_profile=user_profile)
    rep.score = total_score
    rep.save()

    # Define "Levels"
    next_level_score = 1000 if total_score < 1000 else 5000
    progress_percent = min((total_score / next_level_score) * 100, 100)

    context = {
        "total_score": total_score,
        "base_points": base_points,
        "urgency_points": urgency_points,
        "diversity_points": diversity_points,
        "item_points": item_points,
        "donations": donations,
        "progress_percent": progress_percent,
        "next_level_score": next_level_score,
        "financial_total": financial_total,
        "urgent_count": urgent_donations.count(),
        "org_count": unique_orgs,
    }

    return render(request, "reputation/impact_score.html", context)

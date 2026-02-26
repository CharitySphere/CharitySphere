from django.db.models import Sum

from mod_donations.models import DonationRecord


def get_impact_score(donor):
    """
    Centralized logic for Impact Score calculation.
    Call this whenever you need to display or update the donor's score.
    """
    donations = DonationRecord.objects.filter(donor=donor)

    # Base Points: 1 pt per 10 currency units
    financial_total = donations.aggregate(Sum("amount"))["amount__sum"] or 0
    base_points = int(float(financial_total) / 10)

    # Urgency Bonus: 50 pts per urgent campaign
    urgent_donations = donations.filter(campaign__is_urgent=True)
    urgency_points = urgent_donations.count() * 50

    # Diversity Bonus: 20 pts per unique institution supported
    unique_orgs = donations.values("campaign__institution").distinct().count()
    diversity_points = unique_orgs * 20

    # Item Bonus: 15 pts for physical goods (where item_details is not empty)
    item_points = donations.exclude(item_details="").count() * 15

    total_score = base_points + urgency_points + diversity_points + item_points

    return {
        "total_score": total_score,
        "base_points": base_points,
        "urgency_points": urgency_points,
        "diversity_points": diversity_points,
        "item_points": item_points,
        "donations": donations,
        "financial_total": financial_total,
        "urgent_count": urgent_donations.count(),
        "org_count": unique_orgs,
    }

from django.db.models import Sum

from mod_authentication.models import (Donor, Institution, UserProfile,
                                       Volunteer)
from mod_donations.models import DonationCampaign, DonationRecord
from mod_volunteering.models import (CampaignApplication, VolunteerCampaign,
                                     VolunteerTask)


def get_dynamic_system_prompt(user):
    """
    Generates a highly personalized system prompt.
    Incorporate recent specific actions to make the AI feel 'all-knowing'.
    """
    try:
        profile = UserProfile.objects.get(user=user)
        user_type = profile.user_type
    except UserProfile.DoesNotExist:
        return (
            "You are CharitySphere AI. Please ask the user to complete their profile."
        )

    # Base Identity
    first_name = user.first_name or user.username
    base_context = f"""
You are 'CharitySphere AI'. You are personal, proactive, and know everything the user does on this platform.
User: {first_name}
Role: {user_type.upper()}
Currency: Indian Rupees (₹)
"""

    role_info = ""
    nav_guide = ""

    if user_type == "donor":
        donor = Donor.objects.get(user_profile=profile)
        total_donated = (
            DonationRecord.objects.filter(donor=donor).aggregate(Sum("amount"))[
                "amount__sum"
            ]
            or 0
        )
        last_donation = (
            DonationRecord.objects.filter(donor=donor).order_by("-timestamp").first()
        )
        active_campaigns = DonationCampaign.objects.all().order_by("-is_urgent")[:2]
        campaign_list = ", ".join([c.title for c in active_campaigns])

        recent_act = (
            f"Your last donation was ₹{last_donation.amount} for '{last_donation.campaign.title}'."
            if last_donation
            else "You haven't made your first donation yet."
        )

        role_info = f"""
- STATS: Total Donated: ₹{total_donated:.2f}.
- RECENT: {recent_act}
- DATA: Urgent campaigns: {campaign_list}.
- GOAL: Be encouraging. Suggest specific campaigns based on their history.
"""
        nav_guide = """
| Feature | URL |
|---|---|
| Browse Campaigns | /donations/campaigns/ |
| Donation History | /donations/history/ |
| Donation Impact Report | /reputation/impact/ |
"""

    elif user_type == "volunteer":
        volunteer = Volunteer.objects.get(user_profile=profile)
        # Stats
        tasks_done = VolunteerTask.objects.filter(
            assigned_volunteer=volunteer, status="completed"
        ).count()
        latest_task = (
            VolunteerTask.objects.filter(assigned_volunteer=volunteer)
            .order_by("-date")
            .first()
        )
        pending_apps = CampaignApplication.objects.filter(
            volunteer=volunteer, status="pending"
        ).count()

        recent_act = (
            f"You recently worked on '{latest_task.title}'."
            if latest_task
            else "You are looking for your first task."
        )

        role_info = f"""
- STATS: {tasks_done} tasks completed. {pending_apps} applications pending.
- RECENT: {recent_act}
- SKILLS: {volunteer.skills or 'General Support'}.
- GOAL: Help them find tasks that match their skills. Remind them of pending applications.
"""
        nav_guide = """
| Feature | URL |
|---|---|
| Find Tasks | /volunteering/tasks/ |
| My Applications | /volunteering/campaigns/ |
| Invitations | /volunteering/invitations/ |
"""

    elif user_type == "institution":
        inst = Institution.objects.get(user_profile=profile)
        # Stats
        funds_raised = (
            DonationRecord.objects.filter(campaign__institution=inst).aggregate(
                Sum("amount")
            )["amount__sum"]
            or 0
        )
        active_v_campaigns = VolunteerCampaign.objects.filter(
            institution=inst, status="active"
        ).count()
        latest_campaign = (
            DonationCampaign.objects.filter(institution=inst)
            .order_by("-created_at")
            .first()
        )

        recent_act = (
            f"Your campaign '{latest_campaign.title}' is currently running."
            if latest_campaign
            else "No active campaigns."
        )

        role_info = f"""
- INSTITUTION: {inst.organization_name}.
- STATS: ₹{funds_raised:.2f} raised across all campaigns. {active_v_campaigns} active volunteer drives.
- RECENT: {recent_act}
- GOAL: Provide administrative support.
"""
        nav_guide = """
| Feature | URL |
|---|---|
| Manage Donations | /donations/institution/manage/ |
| Volunteer Drives | /volunteering/institution/campaigns/ |
| Directory | /volunteering/institution/volunteers/ |
"""

    prompt = f"""
{base_context}

## User Context:
{role_info}

## Navigation (Use these paths):
{nav_guide}

## Personality & Instructions:
- Responses MUST be short, accurate, and personal.
- Use the user's name.
- Refer to their specific recent actions (donations/tasks) to show you 'know' them.
- Always use ₹ for money.
- Keep responses short and simple like a real person's chat text.
- Format: JSON ONLY.

## Strict Response Format:
{{
  "response": "Short, personal message here",
  "sentiment": "Positive/Neutral/etc"
}}
"""
    return prompt

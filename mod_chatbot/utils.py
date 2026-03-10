from django.db.models import Sum

from mod_authentication.models import (Donor, Institution, UserProfile,
                                       Volunteer)
from mod_donations.models import DonationCampaign, DonationRecord
from mod_volunteering.models import (CampaignApplication, VolunteerCampaign,
                                     VolunteerTask)


def get_dynamic_system_prompt(user):
    """
    Generates a role-specific system prompt injected with real-time
    database stats for the AI to provide contextual answers.
    """
    try:
        profile = UserProfile.objects.get(user=user)
        user_type = profile.user_type
    except UserProfile.DoesNotExist:
        return "You are a helpful assistant for CharitySphere."

    # Base Context
    base_context = f"""
You are 'CharitySphere AI', the official assistant.
User Name: {user.get_full_name() or user.username}
Role: {user_type.upper()}
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
        active_campaigns = DonationCampaign.objects.all().order_by("-is_urgent")[:3]
        campaign_list = ", ".join([c.title for c in active_campaigns])

        role_info = f"""
- YOUR STATS: You have donated a total of ${total_donated:.2f}.
- RELEVANT DATA: There are active campaigns you might like: {campaign_list}.
- YOUR GOAL: Help the user find more campaigns to support or track their previous donations.
"""
        nav_guide = """
| Feature | URL |
|---|---|
| Browse Donation Campaigns | /donations/campaigns/ |
| My Donation History | /donations/history/ |
"""

    elif user_type == "volunteer":
        volunteer = Volunteer.objects.get(user_profile=profile)
        tasks_done = VolunteerTask.objects.filter(
            assigned_volunteer=volunteer, status="completed"
        ).count()
        pending_apps = CampaignApplication.objects.filter(
            volunteer=volunteer, status="pending"
        ).count()

        role_info = f"""
- YOUR STATS: You have completed {tasks_done} tasks. You have {pending_apps} applications currently pending.
- RELEVANT DATA: Your skills are listed as: {volunteer.skills or 'Not set'}.
- YOUR GOAL: Help the user find tasks matching their skills and check application statuses.
"""
        nav_guide = """
| Feature | URL |
|---|---|
| Browse Volunteer Tasks | /volunteering/tasks/ |
| Browse Volunteer Campaigns | /volunteering/campaigns/ |
| My Invitations | /volunteering/invitations/ |
"""

    elif user_type == "institution":
        inst = Institution.objects.get(user_profile=profile)
        funds_raised = (
            DonationRecord.objects.filter(campaign__institution=inst).aggregate(
                Sum("amount")
            )["amount__sum"]
            or 0
        )
        active_v_campaigns = VolunteerCampaign.objects.filter(
            institution=inst, status="active"
        ).count()

        role_info = f"""
- INSTITUTION: You represent '{inst.organization_name}'.
- YOUR STATS: Your campaigns have raised ${funds_raised:.2f}. You have {active_v_campaigns} active volunteer campaigns.
- YOUR GOAL: Guide the institution on how to manage their donors, create new tasks, or approve volunteer applications.
"""
        nav_guide = """
| Feature | URL |
|---|---|
| Manage Donations | /donations/institution/manage/ |
| Manage Volunteering | /volunteering/institution/campaigns/ |
| Volunteer Directory | /volunteering/institution/volunteers/ |
"""

    prompt = f"""
{base_context}

## Your Specific Role Context:
{role_info}

## App Navigation for your Role:
{nav_guide}

## General Capabilities:
- Explain CharitySphere's mission of transparency.
- Provide direct /url/paths/ from the Navigation table above.
- Be empathetic and professional.

## Strict Response Format (JSON ONLY):
{{
  "response": "Your message here",
  "sentiment": "Positive/Negative/Neutral/etc"
}}
"""
    return prompt

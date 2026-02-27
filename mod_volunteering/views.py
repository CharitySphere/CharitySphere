from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404

from mod_authentication.models import Volunteer, Institution, UserProfile
from .models import VolunteerCampaign, VolunteerTask, CampaignApplication, OrgInvitation, DonationCampaign


# ========== VOLUNTEER VIEWS ==========

@login_required
def volunteer_campaigns(request):
    """List all volunteer campaigns"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)

        if user_profile.user_type != 'volunteer':
            messages.error(request, "Access denied.")
            return redirect('dashboard')

        volunteer = Volunteer.objects.get(user_profile=user_profile)

        campaigns = VolunteerCampaign.objects.filter(status='active').select_related('donation_campaign').order_by('-created_at')

        applied_campaign_ids = CampaignApplication.objects.filter(
            volunteer=volunteer
        ).values_list('campaign_id', flat=True)

        context = {
            'campaigns': campaigns,
            'applied_campaign_ids': list(applied_campaign_ids),
        }
        return render(request, 'volunteering/campaign_list.html', context)

    except (UserProfile.DoesNotExist, Volunteer.DoesNotExist):
        messages.error(request, "Volunteer profile not found.")
        return redirect('dashboard')


@login_required
def apply_to_campaign(request, campaign_id):
    """Volunteer applies to join a campaign"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        volunteer = Volunteer.objects.get(user_profile=user_profile)
        campaign = get_object_or_404(VolunteerCampaign, id=campaign_id)

        # Check if already applied
        existing = CampaignApplication.objects.filter(
            volunteer=volunteer,
            campaign=campaign
        ).first()

        if existing:
            messages.warning(request, "You have already applied to this campaign.")
        else:
            CampaignApplication.objects.create(
                volunteer=volunteer,
                campaign=campaign,
                status='pending'
            )
            messages.success(request, "Your application has been submitted successfully!")

        return redirect('volunteering:campaign_list')

    except (UserProfile.DoesNotExist, Volunteer.DoesNotExist):
        messages.error(request, "Volunteer profile not found.")
        return redirect('dashboard')


@login_required
def volunteer_tasks(request):
    """List all available volunteer tasks"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        volunteer = Volunteer.objects.get(user_profile=user_profile)

        # Filter tasks
        task_type = request.GET.get('task_type')
        location = request.GET.get('location')
        date = request.GET.get('date')

        tasks = VolunteerTask.objects.filter(status='open').order_by('date')

        if task_type:
            tasks = tasks.filter(task_type=task_type)
        if location:
            tasks = tasks.filter(location__icontains=location)
        if date:
            tasks = tasks.filter(date=date)

        # Get my assigned tasks
        my_tasks = VolunteerTask.objects.filter(assigned_volunteer=volunteer)

        context = {
            'tasks': tasks,
            'my_tasks': my_tasks,
            'selected_task_type': task_type,
            'selected_location': location,
            'selected_date': date,
        }
        return render(request, 'volunteering/task_list.html', context)

    except (UserProfile.DoesNotExist, Volunteer.DoesNotExist):
        messages.error(request, "Volunteer profile not found.")
        return redirect('dashboard')


@login_required
def volunteer_for_task(request, task_id):
    """Volunteer assigns themselves to a task"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        volunteer = Volunteer.objects.get(user_profile=user_profile)
        task = get_object_or_404(VolunteerTask, id=task_id)

        if task.assigned_volunteer:
            messages.warning(request, "This task is already assigned.")
        else:
            task.assigned_volunteer = volunteer
            task.status = 'in_progress'
            task.save()
            messages.success(request, "You have successfully volunteered for this task!")

        return redirect('volunteering:task_list')

    except (UserProfile.DoesNotExist, Volunteer.DoesNotExist):
        messages.error(request, "Volunteer profile not found.")
        return redirect('dashboard')


@login_required
def org_invitations(request):
    """View and respond to organization invitations"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        volunteer = Volunteer.objects.get(user_profile=user_profile)

        invitations = OrgInvitation.objects.filter(volunteer=volunteer).order_by('-sent_at')

        context = {
            'invitations': invitations,
        }
        return render(request, 'volunteering/org_invitations.html', context)

    except (UserProfile.DoesNotExist, Volunteer.DoesNotExist):
        messages.error(request, "Volunteer profile not found.")
        return redirect('dashboard')


@login_required
def respond_to_invitation(request, invitation_id):
    """Accept or reject organization invitation"""
    if request.method == 'POST':
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            volunteer = Volunteer.objects.get(user_profile=user_profile)
            invitation = get_object_or_404(OrgInvitation, id=invitation_id, volunteer=volunteer)

            action = request.POST.get('action')

            if action == 'accept':
                invitation.status = 'accepted'
                invitation.save()
                messages.success(request, f"You have joined {invitation.institution.organization_name}!")
            elif action == 'reject':
                invitation.status = 'rejected'
                invitation.save()
                messages.info(request, "Invitation declined.")

            return redirect('volunteering:org_invitations')

        except (UserProfile.DoesNotExist, Volunteer.DoesNotExist):
            messages.error(request, "Volunteer profile not found.")
            return redirect('dashboard')

    return redirect('volunteering:org_invitations')


# ========== INSTITUTION VIEWS ==========

@login_required
def institution_campaigns(request):
    """Manage campaigns for institution"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)

        if user_profile.user_type != 'institution':
            messages.error(request, "Access denied.")
            return redirect('dashboard')

        institution = Institution.objects.get(user_profile=user_profile)
        campaigns = VolunteerCampaign.objects.filter(institution=institution).order_by('-created_at')
        d_campaigns = DonationCampaign.objects.filter(institution=institution)

        context = {
            'campaigns': campaigns,
            'institution': institution,
            "d_campaigns": d_campaigns, # for 'Create Volunteer Campaign' dropdown
        }
        return render(request, 'institution/campaign_management.html', context)

    except (UserProfile.DoesNotExist, Institution.DoesNotExist):
        messages.error(request, "Institution profile not found.")
        return redirect('dashboard')


@login_required
def create_campaign(request):
    """Create new volunteer campaign"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        institution = Institution.objects.get(user_profile=user_profile)

        if request.method == 'POST':
            title = request.POST.get('title')
            description = request.POST.get('description')
            donation_campaign_id = request.POST.get('donation_campaign_id')
            status = request.POST.get('status', 'pending')

            if not title or not description:
                messages.error(request, "Title and description are required.")
                return redirect('volunteering:institution_campaigns')

            donation_campaign = get_object_or_404(DonationCampaign, id=donation_campaign_id, institution=institution)

            VolunteerCampaign.objects.create(
                title=title,
                institution=institution,
                donation_campaign=donation_campaign,
                description=description,
                status=status
            )

            messages.success(request, "Campaign created successfully!")
            return redirect('volunteering:institution_campaigns')

    except (UserProfile.DoesNotExist, Institution.DoesNotExist):
        messages.error(request, "Institution profile not found.")
        return redirect('dashboard')

    return redirect('volunteering:institution_campaigns')


@login_required
def update_campaign(request, campaign_id):
    """Update existing campaign"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        institution = Institution.objects.get(user_profile=user_profile)
        campaign = get_object_or_404(VolunteerCampaign, id=campaign_id, institution=institution)

        if request.method == 'POST':
            campaign.title = request.POST.get('title')
            campaign.description = request.POST.get('description')
            campaign.status = request.POST.get('status')
            campaign.save()

            messages.success(request, "Campaign updated successfully!")
            return redirect('volunteering:institution_campaigns')

    except (UserProfile.DoesNotExist, Institution.DoesNotExist):
        messages.error(request, "Institution profile not found.")
        return redirect('dashboard')

    return redirect('volunteering:institution_campaigns')


@login_required
def delete_campaign(request, campaign_id):
    """Delete campaign if no active tasks"""
    if request.method == 'POST':
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            institution = Institution.objects.get(user_profile=user_profile)
            campaign = get_object_or_404(VolunteerCampaign, id=campaign_id, institution=institution)

            # Check for active tasks
            active_tasks = VolunteerTask.objects.filter(
                campaign=campaign,
                status__in=['open', 'in_progress']
            ).exists()

            if active_tasks:
                messages.error(request, "Cannot delete campaign with active tasks.")
            else:
                campaign.delete()
                messages.success(request, "Campaign deleted successfully!")

            return redirect('volunteering:institution_campaigns')

        except (UserProfile.DoesNotExist, Institution.DoesNotExist):
            messages.error(request, "Institution profile not found.")
            return redirect('dashboard')

    return redirect('volunteering:institution_campaigns')


@login_required
def campaign_applications(request, campaign_id):
    """View and manage campaign applications"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        institution = Institution.objects.get(user_profile=user_profile)
        campaign = get_object_or_404(VolunteerCampaign, id=campaign_id, institution=institution)

        applications = CampaignApplication.objects.filter(campaign=campaign).order_by('-applied_at')

        context = {
            'campaign': campaign,
            'applications': applications,
        }
        return render(request, 'institution/campaign_applications.html', context)

    except (UserProfile.DoesNotExist, Institution.DoesNotExist):
        messages.error(request, "Institution profile not found.")
        return redirect('dashboard')


@login_required
def respond_to_application(request, application_id):
    """Accept or reject volunteer application"""
    if request.method == 'POST':
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            institution = Institution.objects.get(user_profile=user_profile)
            application = get_object_or_404(CampaignApplication, id=application_id)

            # Verify this application is for the institution's campaign
            if application.campaign.institution != institution:
                messages.error(request, "Access denied.")
                return redirect('volunteering:institution_campaigns')

            action = request.POST.get('action')

            if action == 'accept':
                application.status = 'accepted'
                application.save()
                messages.success(request, f"Accepted {application.volunteer.user_profile.user.username}!")
            elif action == 'reject':
                application.status = 'rejected'
                application.save()
                messages.info(request, "Application rejected.")

            return redirect('volunteering:campaign_applications', campaign_id=application.campaign.id)

        except (UserProfile.DoesNotExist, Institution.DoesNotExist):
            messages.error(request, "Institution profile not found.")
            return redirect('dashboard')

    return redirect('volunteering:institution_campaigns')


@login_required
def manage_tasks(request, campaign_id):
    """Manage tasks for a campaign"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        institution = Institution.objects.get(user_profile=user_profile)
        campaign = get_object_or_404(VolunteerCampaign, id=campaign_id, institution=institution)

        tasks = VolunteerTask.objects.filter(campaign=campaign).order_by('date')

        context = {
            'campaign': campaign,
            'tasks': tasks,
        }
        return render(request, 'institution/task_management.html', context)

    except (UserProfile.DoesNotExist, Institution.DoesNotExist):
        messages.error(request, "Institution profile not found.")
        return redirect('dashboard')


@login_required
def add_task(request, campaign_id):
    """Add task to campaign"""
    if request.method == 'POST':
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            institution = Institution.objects.get(user_profile=user_profile)
            campaign = get_object_or_404(VolunteerCampaign, id=campaign_id, institution=institution)

            title = request.POST.get('title')
            description = request.POST.get('description')
            date = request.POST.get('date')
            location = request.POST.get('location')
            task_type = request.POST.get('task_type')

            if not all([title, description, date, location, task_type]):
                messages.error(request, "All fields are required.")
                return redirect('volunteering:manage_tasks', campaign_id=campaign_id)

            VolunteerTask.objects.create(
                campaign=campaign,
                title=title,
                institution=institution,
                date=date,
                location=location,
                task_type=task_type,
                description=description
            )

            messages.success(request, "Task added successfully!")
            return redirect('volunteering:manage_tasks', campaign_id=campaign_id)

        except (UserProfile.DoesNotExist, Institution.DoesNotExist):
            messages.error(request, "Institution profile not found.")
            return redirect('dashboard')

    return redirect('volunteering:institution_campaigns')


@login_required
def remove_volunteer_from_task(request, task_id):
    """Remove volunteer from a task"""
    if request.method == 'POST':
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            institution = Institution.objects.get(user_profile=user_profile)
            task = get_object_or_404(VolunteerTask, id=task_id, institution=institution)

            task.assigned_volunteer = None
            task.status = 'open'
            task.save()

            messages.success(request, "Volunteer removed from task.")
            return redirect('volunteering:manage_tasks', campaign_id=task.campaign.id)

        except (UserProfile.DoesNotExist, Institution.DoesNotExist):
            messages.error(request, "Institution profile not found.")
            return redirect('dashboard')

    return redirect('volunteering:institution_campaigns')


@login_required
def send_org_invitation(request):
    """Send invitation to volunteer to join organization"""
    if request.method == 'POST':
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            institution = Institution.objects.get(user_profile=user_profile)

            volunteer_id = request.POST.get('volunteer_id')
            volunteer = get_object_or_404(Volunteer, id=volunteer_id)

            # Check if invitation already exists
            existing = OrgInvitation.objects.filter(
                institution=institution,
                volunteer=volunteer,
                status='pending'
            ).exists()

            if existing:
                messages.warning(request, "Invitation already sent to this volunteer.")
            else:
                OrgInvitation.objects.create(
                    institution=institution,
                    volunteer=volunteer
                )
                messages.success(request, "Invitation sent successfully!")

            return redirect('volunteering:institution_campaigns')

        except (UserProfile.DoesNotExist, Institution.DoesNotExist):
            messages.error(request, "Institution profile not found.")
            return redirect('dashboard')

    return redirect('volunteering:institution_campaigns')


@login_required
def volunteer_directory(request):
    """View all volunteers for sending invitations"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)

        if user_profile.user_type != 'institution':
            messages.error(request, "Access denied.")
            return redirect('dashboard')

        institution = Institution.objects.get(user_profile=user_profile)
        volunteers = Volunteer.objects.all()

        # Get volunteers already invited
        invited_volunteer_ids = OrgInvitation.objects.filter(
            institution=institution,
            status='pending'
        ).values_list('volunteer_id', flat=True)

        context = {
            'volunteers': volunteers,
            'invited_volunteer_ids': list(invited_volunteer_ids),
        }
        return render(request, 'institution/volunteer_directory.html', context)

    except (UserProfile.DoesNotExist, Institution.DoesNotExist):
        messages.error(request, "Institution profile not found.")
        return redirect('dashboard')

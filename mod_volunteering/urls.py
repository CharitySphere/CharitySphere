from django.urls import path
from . import views

app_name = 'volunteering'

urlpatterns = [
    # Volunteer URLs
    path('campaigns/', views.volunteer_campaigns, name='campaign_list'),
    path('campaigns/<int:campaign_id>/apply/', views.apply_to_campaign, name='apply_to_campaign'),
    path('tasks/', views.volunteer_tasks, name='task_list'),
    path('tasks/<int:task_id>/volunteer/', views.volunteer_for_task, name='volunteer_for_task'),
    path('invitations/', views.org_invitations, name='org_invitations'),
    path('invitations/<int:invitation_id>/respond/', views.respond_to_invitation, name='respond_to_invitation'),

    # Institution URLs
    path('institution/campaigns/', views.institution_campaigns, name='institution_campaigns'),
    path('institution/campaigns/create/', views.create_campaign, name='create_campaign'),
    path('institution/campaigns/<int:campaign_id>/update/', views.update_campaign, name='update_campaign'),
    path('institution/campaigns/<int:campaign_id>/delete/', views.delete_campaign, name='delete_campaign'),
    path('institution/campaigns/<int:campaign_id>/applications/', views.campaign_applications, name='campaign_applications'),
    path('institution/applications/<int:application_id>/respond/', views.respond_to_application, name='respond_to_application'),
    path('institution/campaigns/<int:campaign_id>/tasks/', views.manage_tasks, name='manage_tasks'),
    path('institution/campaigns/<int:campaign_id>/tasks/add/', views.add_task, name='add_task'),
    path('institution/tasks/<int:task_id>/remove-volunteer/', views.remove_volunteer_from_task, name='remove_volunteer_from_task'),
    path('institution/volunteers/', views.volunteer_directory, name='volunteer_directory'),
    path('institution/volunteers/invite/', views.send_org_invitation, name='send_org_invitation'),
]

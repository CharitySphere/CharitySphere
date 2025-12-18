from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("donor/", views.donor_dashboard, name="donor_dashboard"),
    path("volunteer/", views.volunteer_dashboard, name="volunteer_dashboard"),
    path("institution/", views.institution_dashboard, name="institution_dashboard"),
    path("settings/", views.profile_settings, name="profile_settings"),
]

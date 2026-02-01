from django.urls import path
from . import views

app_name = 'donations'

urlpatterns = [
    path('campaigns/', views.campaign_list, name='campaign_list'),
    path('campaigns/<int:campaign_id>/', views.campaign_detail, name='campaign_detail'),
    path('campaigns/<int:campaign_id>/donate/', views.make_donation, name='make_donation'),
    path('history/', views.donation_history, name='donation_history'),
]

from django.urls import path
from . import views

app_name = 'donations'

urlpatterns = [
    path('campaigns/', views.campaign_list, name='campaign_list'),
    path('campaigns/<int:campaign_id>/', views.campaign_detail, name='campaign_detail'),
    path('campaigns/<int:campaign_id>/donate/', views.make_donation, name='make_donation'),
    path('history/', views.donation_history, name='donation_history'),
    path('institution/donation/<int:donation_id>/status/', views.update_donation_status, name='update_donation_status'),
    path('institution/manage/', views.institution_donation_campaigns, name='institution_donation_campaigns'),
    path('institution/manage/add/', views.manage_donation_campaign, name='create_donation_campaign'),
    path('institution/manage/edit/<int:campaign_id>/', views.manage_donation_campaign, name='edit_donation_campaign'),
    path('institution/manage/delete/<int:campaign_id>/', views.delete_donation_campaign, name='delete_donation_campaign'),
    path('institution/record/<int:record_id>/status/', views.update_item_status, name='update_item_status'),
    path('campaigns/<int:campaign_id>/razorpay-init/', views.razorpay_create_order, name='razorpay_init'),
    path('payment/verify/', views.verify_payment, name='verify_payment'),
]

from django.urls import path

from . import views

app_name = "reputation"

urlpatterns = [
    path("impact/", views.impact_score_detail, name="impact_detail"),
]

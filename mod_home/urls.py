from django.urls import path

from . import views

urlpatterns = [
    path("", views.home1, name="homepage"),
    path("home2/", views.home2, name="homepage2"),
]

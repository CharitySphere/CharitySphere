from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.auth, name="auth"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="login.html"),
        name="login",
    ),
    path("logout/", views.logout_view, name="logout"),

    path("signup/", views.signup_step_1, name="signup_step_1"), # Role
    path("signup/step-2/", views.signup_step_2, name="signup_step_2"), # Account
    path("signup/step-3/", views.signup_step_3, name="signup_step_3"), # Details

    path("register/donor/", views.register_donor, name="register_donor"),
    path("register/volunteer/", views.register_volunteer, name="register_volunteer"),
    path(
        "register/institution/", views.register_institution, name="register_institution"
    ),
]

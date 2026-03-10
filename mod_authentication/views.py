from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import redirect, render

from .forms import (DonorRegistrationForm, InstitutionRegistrationForm,
                    VolunteerRegistrationForm)
from .models import Donor, Institution, UserProfile, Volunteer


def auth(request):
    return render(request, "auth.html")


def logout_view(request):
    logout(request)
    return redirect("homepage")


def signup_step_1(request):
    """Step 1: Select User Type"""
    if request.method == "POST":
        user_type = request.POST.get("user_type")
        if user_type in ["donor", "volunteer", "institution"]:
            request.session["signup_user_type"] = user_type
            return redirect("signup_step_2")
    return render(request, "signup/step_1.html")


def signup_step_2(request):
    """Step 2: Basic Account Information"""
    user_type = request.session.get("signup_user_type")
    if not user_type:
        return redirect("signup_step_1")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Manual Validation
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match")
        else:
            # Store in session, don't save to DB yet
            request.session["signup_account_data"] = {
                "username": username,
                "email": email,
                "password": password,
            }
            return redirect("signup_step_3")

    return render(request, "signup/step_2.html", {"user_type": user_type})


def signup_step_3(request):
    """Step 3: Role-specific details + Location and Manual Creation"""
    user_type = request.session.get("signup_user_type")
    account_data = request.session.get("signup_account_data")

    if not user_type or not account_data:
        return redirect("signup_step_1")

    if request.method == "POST":
        try:
            with transaction.atomic():
                # 1. Create the Base User
                user = User.objects.create_user(
                    username=account_data["username"],
                    email=account_data["email"],
                    password=account_data["password"],
                )

                # 2. Extract Location Data from POST
                address = request.POST.get("address")
                lat = request.POST.get("latitude")
                lng = request.POST.get("longitude")

                # 3. Create the UserProfile
                profile = UserProfile.objects.create(
                    user=user,
                    user_type=user_type,
                    address=address,
                    latitude=lat if lat else None,
                    longitude=lng if lng else None,
                )

                # 4. Create Specific Role Model
                redirect_url = "login"
                if user_type == "donor":
                    Donor.objects.create(user_profile=profile)
                    redirect_url = "donor_dashboard"

                elif user_type == "volunteer":
                    Volunteer.objects.create(
                        user_profile=profile,
                        skills=request.POST.get("skills"),
                        availability=request.POST.get("availability"),
                    )
                    redirect_url = "volunteer_dashboard"

                elif user_type == "institution":
                    Institution.objects.create(
                        user_profile=profile,
                        organization_name=request.POST.get("organization_name"),
                        registration_number=request.POST.get("registration_number"),
                    )
                    redirect_url = "institution_dashboard"

                # Cleanup session and Login
                del request.session["signup_user_type"]
                del request.session["signup_account_data"]
                login(request, user)
                return redirect(redirect_url)

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    return render(request, "signup/step_3.html", {"user_type": user_type})


def register_donor(request):
    if request.method == "POST":
        form = DonorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("donor_dashboard")
    else:
        form = DonorRegistrationForm()
    return render(request, "register_donor.html", {"form": form})


def register_volunteer(request):
    if request.method == "POST":
        form = VolunteerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("volunteer_dashboard")
    else:
        form = VolunteerRegistrationForm()
    return render(request, "register_volunteer.html", {"form": form})


def register_institution(request):
    if request.method == "POST":
        form = InstitutionRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("institution_dashboard")
    else:
        form = InstitutionRegistrationForm()
    return render(request, "register_institution.html", {"form": form})

from django.contrib.auth import login, logout
from django.shortcuts import redirect, render

from .forms import (DonorRegistrationForm, InstitutionRegistrationForm,
                    VolunteerRegistrationForm)


def logout_view(request):
    logout(request)
    return redirect("homepage")


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

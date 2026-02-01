import json
import os
import sys
from pathlib import Path

import django
from django.contrib.auth.hashers import make_password
from faker import Faker

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

fake = Faker()
fixtures = []


def create_volunteer_fixture(pk, username, password, email, skills, avail):
    fixtures.append(
        {
            "model": "auth.user",
            "pk": pk,
            "fields": {
                "username": username,
                "password": make_password(password),
                "email": email,
                "is_active": True,
            },
        }
    )
    fixtures.append(
        {
            "model": "mod_authentication.userprofile",
            "pk": pk,
            "fields": {"user": pk, "user_type": "volunteer"},
        }
    )
    fixtures.append(
        {
            "model": "mod_authentication.volunteer",
            "pk": pk,
            "fields": {"user_profile": pk, "skills": skills, "availability": avail},
        }
    )


# CREATE: Test Volunteer
create_volunteer_fixture(
    pk=2,
    username="volunteer",
    password="volunteer",
    email="volunteer@charitysphere.org",
    skills="First Aid, Logistics",
    avail="Weekends",
)

# CREATE: Random Volunteers (PK range 20-29)
for i in range(20, 30):
    skills = ", ".join(fake.words(nb=3))
    avail = fake.day_of_week()
    create_volunteer_fixture(
        pk=i,
        username=fake.user_name(),
        password="pass123",
        email=fake.email(),
        skills=skills,
        avail=avail,
    )

with open("mod_authentication/fixtures/volunteers.json", "w") as f:
    json.dump(fixtures, f, indent=4)

print("Generated mod_authentication/fixtures/volunteers.json")

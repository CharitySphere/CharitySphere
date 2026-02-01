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


def create_donor_fixture(pk, username, password, email, amount):
    # Auth User
    fixtures.append(
        {
            "model": "auth.user",
            "pk": pk,
            "fields": {
                "username": username,
                "password": make_password(password),
                "email": email,
                "is_staff": False,
                "is_superuser": False,
                "is_active": True,
            },
        }
    )
    # User Profile
    fixtures.append(
        {
            "model": "mod_authentication.userprofile",
            "pk": pk,
            "fields": {"user": pk, "user_type": "donor"},
        }
    )
    # Donor Specific
    fixtures.append(
        {
            "model": "mod_authentication.donor",
            "pk": pk,
            "fields": {"user_profile": pk, "donation_amount": str(amount)},
        }
    )


# CREATE: Test Donor
create_donor_fixture(
    pk=1,
    username="donor",
    password="donor",
    email="donor@charitysphere.org",
    amount=0.00,
)

# CREATE: Random Donors (PK range 10-19)
for i in range(10, 20):
    create_donor_fixture(
        pk=i,
        username=fake.user_name(),
        password="pass123",
        email=fake.email(),
        amount=0,
    )

with open("mod_authentication/fixtures/donors.json", "w") as f:
    json.dump(fixtures, f, indent=4)

print("Generated mod_authentication/fixtures/donors.json")

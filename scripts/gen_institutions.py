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


def create_institution_fixture(pk, username, password, email, org_name, reg_num):
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
            "fields": {"user": pk, "user_type": "institution"},
        }
    )
    fixtures.append(
        {
            "model": "mod_authentication.institution",
            "pk": pk,
            "fields": {
                "user_profile": pk,
                "organization_name": org_name,
                "registration_number": reg_num,
            },
        }
    )


# CREATE: Test Institution
create_institution_fixture(
    pk=3,
    username="institution",
    password="institution",
    email="admin@charitysphere.org",
    org_name="CharitySphere HQ",
    reg_num="CS-999-2023",
)

# CREATE: Random Institutions (PK range 30-39)
for i in range(30, 40):
    create_institution_fixture(
        pk=i,
        username=fake.company_email().split("@")[0],
        password="pass123",
        email=fake.company_email(),
        org_name=fake.company(),
        reg_num=fake.bothify(text="??-###-####"),
    )

with open("mod_authentication/fixtures/institutions.json", "w") as f:
    json.dump(fixtures, f, indent=4)

print("Generated mod_authentication/fixtures/institutions.json")

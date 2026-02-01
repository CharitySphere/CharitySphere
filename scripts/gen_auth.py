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

def create_user_bundle(pk, username, user_type, email, **kwargs):
    # 1. Auth User
    fixtures.append({
        "model": "auth.user",
        "pk": pk,
        "fields": {
            "username": username,
            "password": make_password(username), # Password same as username for testing
            "email": email,
            "is_active": True,
        }
    })
    # 2. User Profile
    fixtures.append({
        "model": "mod_authentication.userprofile",
        "pk": pk,
        "fields": {"user": pk, "user_type": user_type}
    })

    # 3. Specific Role
    if user_type == "donor":
        fixtures.append({
            "model": "mod_authentication.donor",
            "pk": pk,
            "fields": {"user_profile": pk, "donation_amount": str(kwargs.get('amount', 0))}
        })
    elif user_type == "volunteer":
        fixtures.append({
            "model": "mod_authentication.volunteer",
            "pk": pk,
            "fields": {
                "user_profile": pk,
                "skills": kwargs.get('skills', ""),
                "availability": kwargs.get('avail', "")
            }
        })
    elif user_type == "institution":
        fixtures.append({
            "model": "mod_authentication.institution",
            "pk": pk,
            "fields": {
                "user_profile": pk,
                "organization_name": kwargs.get('org_name', fake.company()),
                "registration_number": kwargs.get('reg_num', fake.bothify("??-###"))
            }
        })

# --- Generate Data ---
# Test Accounts (PK 1-3)
create_user_bundle(1, "donor", "donor", "donor@charitysphere.org", amount=500.00)
create_user_bundle(2, "volunteer", "volunteer", "volunteer@charitysphere.org", skills="Logistics, First Aid", avail="Weekends")
create_user_bundle(3, "institution", "institution", "admin@charitysphere.org", org_name="CharitySphere HQ")

# Random Donors (PK 10-19)
for i in range(10, 20):
    create_user_bundle(i, fake.user_name(), "donor", fake.email())

# Random Volunteers (PK 20-29)
for i in range(20, 30):
    create_user_bundle(i, fake.user_name(), "volunteer", fake.email(), skills=", ".join(fake.words(3)), avail=fake.day_of_week())

# Random Institutions (PK 30-39)
for i in range(30, 40):
    create_user_bundle(i, fake.user_name(), "institution", fake.company_email())

os.makedirs("fixtures", exist_ok=True)
with open("fixtures/auth_data.json", "w") as f:
    json.dump(fixtures, f, indent=4)

print("Generated fixtures/auth_data.json")

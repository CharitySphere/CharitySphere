import json
import os
import sys
import random
from pathlib import Path
import django

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from faker import Faker
fake = Faker()
fixtures = []

# PK Ranges from gen_auth.py
INSTITUTION_PKS = [3] + list(range(30, 40))
DONOR_PKS = [1] + list(range(10, 20))
CATEGORIES = ["food", "clothes", "hygiene", "medicine", "funds"]

# Create 15 Donation Campaigns
for i in range(1, 16):
    goal = random.randint(1000, 10000)
    current = random.randint(0, goal)
    fixtures.append({
        "model": "mod_donations.donationcampaign",
        "pk": i,
        "fields": {
            "title": fake.catch_phrase(),
            "institution": random.choice(INSTITUTION_PKS),
            "category": random.choice(CATEGORIES),
            "description": fake.paragraph(),
            "goal_amount": str(goal),
            "current_amount": str(current),
            "is_urgent": random.choice([True, False]),
            "created_at": "2023-10-01T12:00:00Z"
        }
    })

    # Create 2-4 donation records per campaign
    for j in range(random.randint(2, 4)):
        fixtures.append({
            "model": "mod_donations.donationrecord",
            "fields": {
                "donor": random.choice(DONOR_PKS),
                "campaign": i,
                "amount": str(random.randint(10, 500)),
                "item_details": fake.sentence() if random.random() > 0.5 else "",
                "timestamp": "2023-11-01T10:00:00Z"
            }
        })

os.makedirs("fixtures", exist_ok=True)
with open("fixtures/donations_data.json", "w") as f:
    json.dump(fixtures, f, indent=4)

print("Generated fixtures/donations_data.json")

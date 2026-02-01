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

INSTITUTION_PKS = [3] + list(range(30, 40))
VOLUNTEER_PKS = [2] + list(range(20, 30))

# 1. Volunteer Campaigns
for i in range(1, 11):
    fixtures.append({
        "model": "mod_volunteering.volunteercampaign",
        "pk": i,
        "fields": {
            "title": f"Project {fake.bs().title()}",
            "institution": random.choice(INSTITUTION_PKS),
            "description": fake.text(),
            "status": random.choice(["pending", "active", "completed"]),
            "created_at": "2023-09-01T08:00:00Z"
        }
    })

    # 2. Tasks for each campaign
    for t in range(1, 4):
        fixtures.append({
            "model": "mod_volunteering.volunteertask",
            "fields": {
                "campaign": i,
                "title": f"Task: {fake.job()}",
                "institution": random.choice(INSTITUTION_PKS),
                "date": "2024-12-25",
                "location": fake.address(),
                "task_type": "Field Work",
                "status": random.choice(["open", "in_progress"]),
                "description": fake.sentence(),
                "assigned_volunteer": random.choice(VOLUNTEER_PKS) if random.random() > 0.7 else None
            }
        })

# 3. Campaign Applications
for i in range(20):
    fixtures.append({
        "model": "mod_volunteering.campaignapplication",
        "fields": {
            "campaign": random.randint(1, 10),
            "volunteer": random.choice(VOLUNTEER_PKS),
            "status": random.choice(["pending", "accepted", "rejected"]),
            "applied_at": "2023-11-15T14:20:00Z"
        }
    })

# 4. Org Invitations
for i in range(10):
    fixtures.append({
        "model": "mod_volunteering.orginvitation",
        "fields": {
            "institution": random.choice(INSTITUTION_PKS),
            "volunteer": random.choice(VOLUNTEER_PKS),
            "status": "pending",
            "sent_at": "2023-12-01T09:00:00Z"
        }
    })

os.makedirs("fixtures", exist_ok=True)
with open("fixtures/volunteering_data.json", "w") as f:
    json.dump(fixtures, f, indent=4)

print("Generated fixtures/volunteering_data.json")

#!/bin/env bash

set -e  # Stop the script on any error

args=$1

# REQUIREMENT: manage.py from Django
if [ ! -f "manage.py" ]; then
  echo "manage.py not found. Exiting..."
  exit 1
fi

# REQUIREMENT: packages
echo "--- Installing Requirements ---"
pip install -r "requirements.txt"

# REQUIREMENT: db.sqlite3
if [ ! -f "db.sqlite3" ]; then
  echo "Database not found. Running migrations..."
  python manage.py migrate
else
  echo "Database found. Flushing data..."
  python manage.py flush --no-input
  python manage.py migrate
fi

# REQUIREMENT: fixtures directory
mkdir -p mod_authentication/fixtures

if [ "$args" == "--random" ]; then
  echo "--- Generating Test Fixtures ---"
  # ACTION: Fixtures
  # These match the filenames provided in the previous step
  python scripts/gen_auth.py
  python scripts/gen_donations.py
  python scripts/gen_volunteering.py

  echo "--- Loading Random Data ---"
  # Loading auth first is mandatory to satisfy foreign key constraints
  python manage.py loaddata fixtures/auth_data.json
  python manage.py loaddata fixtures/donations_data.json
  python manage.py loaddata fixtures/volunteering_data.json
  echo "--- Success: Database populated with random data ---"
else
  echo "--- Loading Custom Data ---"
  python manage.py loaddata fixtures/00_test_users.json
  python manage.py loaddata fixtures/01_users.json
  python manage.py loaddata fixtures/02_profiles.json
  python manage.py loaddata fixtures/03_donors_volunteers_institutions.json
  python manage.py loaddata fixtures/04_donation_campaigns.json
  python manage.py loaddata fixtures/05_donation_records.json
  python manage.py loaddata fixtures/06_volunteer_campaigns.json
  python manage.py loaddata fixtures/07_volunteer_tasks.json
  python manage.py loaddata fixtures/08_campaign_applications.json
  python manage.py loaddata fixtures/09_org_invitations.json
  python manage.py loaddata fixtures/10_emergency_alerts.json
  python manage.py loaddata fixtures/11_reputation_scores.json
  python manage.py loaddata fixtures/12_reviews.json
  echo "--- Success: Database populated with custom data ---"
fi

# ACTION: Create admin user
echo "Creating admin user..."
python manage.py shell -c "
from django.contrib.auth.models import User;
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Admin user created.')
else:
    print('Admin user already exists.')
"

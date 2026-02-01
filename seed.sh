#!/bin/env bash

set -e  # Stop the script on any error

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

# ACTION: Fixtures
echo "--- Generating Test Fixtures ---"
# These match the filenames provided in the previous step
python scripts/gen_auth.py
python scripts/gen_donations.py
python scripts/gen_volunteering.py

echo "--- Loading Data ---"
# Loading auth first is mandatory to satisfy foreign key constraints
python manage.py loaddata fixtures/auth_data.json
python manage.py loaddata fixtures/donations_data.json
python manage.py loaddata fixtures/volunteering_data.json

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


echo "--- Success: Database populated with test users and random data ---"

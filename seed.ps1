# Stop the script on any error
$ErrorActionPreference = "Stop"

# REQUIREMENT: manage.py from Django
if (-not (Test-Path "manage.py")) {
    Write-Host "manage.py not found. Exiting..."
    exit 1
}

# REQUIREMENT: packages
Write-Host "--- Installing Requirements ---"
pip install -r "requirements.txt"

# REQUIREMENT: db.sqlite3
if (-not (Test-Path "db.sqlite3")) {
    Write-Host "Database not found. Running migrations..."
    python manage.py migrate
} else {
    Write-Host "Database found. Flushing data..."
    python manage.py flush --no-input
    python manage.py migrate
}

# REQUIREMENT: fixtures directory
$fixturesPath = "mod_authentication/fixtures"
if (-not (Test-Path $fixturesPath)) {
    New-Item -ItemType Directory -Path $fixturesPath | Out-Null
}

# ACTION: Fixtures
Write-Host "--- Generating Test Fixtures ---"
python scripts/gen_auth.py
python scripts/gen_donations.py
python scripts/gen_volunteering.py

Write-Host "--- Loading Data ---"
# Loading auth first is mandatory to satisfy foreign key constraints
python manage.py loaddata fixtures/auth_data.json
python manage.py loaddata fixtures/donations_data.json
python manage.py loaddata fixtures/volunteering_data.json

# ACTION: Create admin user
Write-Host "Creating admin user..."
python manage.py shell -c @"
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Admin user created.')
else:
    print('Admin user already exists.')
"@

Write-Host "--- Success: Database populated with test users and random data ---"

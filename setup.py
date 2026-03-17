#!/usr/bin/env python
"""
Run once to initialise the database and create the Super Admin.
Usage:  python setup.py
"""
import os
import sys
import subprocess

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_saas.settings')

print("=" * 50)
print("  IndiaERP Setup")
print("=" * 50)

# ✅ STEP 1: Always create migrations first
print("\n[1/3] Creating migration files...")
r = subprocess.run([sys.executable, 'manage.py', 'makemigrations'])
if r.returncode != 0:
    sys.exit(1)

# ✅ STEP 2: Apply migrations
print("\n[2/3] Running migrations...")
r = subprocess.run([sys.executable, 'manage.py', 'migrate'])
if r.returncode != 0:
    sys.exit(1)

# ✅ STEP 3: Create super admin
print("\n[3/3] Creating Super Admin...")

import django
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile

SA_USER  = 'superadmin'
SA_PASS  = 'SuperAdmin@123'
SA_EMAIL = 'admin@indiaerp.in'

user, created = User.objects.get_or_create(
    username=SA_USER,
    defaults={'email': SA_EMAIL}
)

if created:
    user.set_password(SA_PASS)
    user.is_superuser = True
    user.is_staff = True
    user.save()

profile, _ = UserProfile.objects.get_or_create(
    user=user,
    defaults={
        'role': 'superadmin',
        'company': None,
        'is_active': True
    }
)

profile.role = 'superadmin'
profile.company = None
profile.is_active = True
profile.save()

print("\n" + "=" * 50)
print("  SUCCESS!")
print(f"  URL      : http://127.0.0.1:8000/login/")
print(f"  Username : {SA_USER}")
print(f"  Password : {SA_PASS}")
print("=" * 50)
print("\nNext step:  python manage.py runserver\n")

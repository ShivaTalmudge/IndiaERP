import os, django
from datetime import date, timedelta
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "erp_saas.settings")
django.setup()

from django.contrib.auth.models import User
from core.models import Company, UserProfile

def setup():
    # 1. Create Company
    company, created = Company.objects.get_or_create(
        company_name="SVR CHEMICALS",
        defaults={
            "contact_email": "admin@svrchemicals.com",
            "gst_number": "36AAACS1234D1ZX",
            "city": "Hyderabad",
            "state": "TG",
            "license_start_date": date.today(),
            "license_end_date": date.today() + timedelta(days=365)
        }
    )
    if created: print("✓ Company SVR CHEMICALS created.")

    # 2. Create Owner (Admin)
    admin_user, created = User.objects.get_or_create(
        username="admin",
        defaults={
            "email": "admin@svrchemicals.com",
            "first_name": "SVR",
            "last_name": "Admin",
            "is_staff": True,
            "is_superuser": True
        }
    )
    if created:
        admin_user.set_password("admin123")
        admin_user.save()
        print("✓ Admin user created (admin / admin123).")
    
    UserProfile.objects.get_or_create(
        user=admin_user,
        defaults={
            "company": company,
            "role": "admin",
            "can_view_sales": True, "can_edit_sales": True,
            "can_view_purchase": True, "can_edit_purchase": True,
            "can_view_masters": True, "can_edit_masters": True,
            "can_view_reports": True
        }
    )

    # 3. Create Staff User
    staff_user, created = User.objects.get_or_create(
        username="staff",
        defaults={
            "email": "staff@svrchemicals.com",
            "first_name": "Test",
            "last_name": "Staff",
            "is_staff": True
        }
    )
    if created:
        staff_user.set_password("staff123")
        staff_user.save()
        print("✓ Staff user created (staff / staff123).")
    
    UserProfile.objects.get_or_create(
        user=staff_user,
        defaults={
            "company": company,
            "role": "staff",
            "can_view_sales": True,
            "can_view_purchase": True,
            "can_view_masters": True,
            "can_view_reports": True
        }
    )

if __name__ == "__main__":
    setup()

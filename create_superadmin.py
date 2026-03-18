import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "erp_saas.settings")
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile

def create_superadmin():
    user, created = User.objects.get_or_create(
        username="superadmin",
        defaults={
            "email": "superadmin@indiaerp.com",
            "first_name": "IndiaERP",
            "last_name": "SuperAdmin",
            "is_staff": True,
            "is_superuser": True
        }
    )
    if created:
        user.set_password("superadmin123")
        user.save()
        print("✓ Super Admin user created.")
    
    # Ensure UserProfile exists with superadmin role
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            "role": "superadmin",
            "is_active": True,
            "can_view_sales": True, "can_edit_sales": True,
            "can_view_purchase": True, "can_edit_purchase": True,
            "can_view_masters": True, "can_edit_masters": True,
            "can_view_reports": True
        }
    )
    if not created and profile.role != 'superadmin':
        profile.role = 'superadmin'
        profile.save()
        print("✓ UserProfile role updated to superadmin.")

if __name__ == "__main__":
    create_superadmin()

import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "erp_saas.settings")
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile, Company

def create_test_user(username, password, role, company_name=None):
    user, created = User.objects.get_or_create(username=username)
    user.set_password(password)
    user.is_staff = (role == 'superadmin')
    user.is_superuser = (role == 'superadmin')
    user.save()
    
    company = None
    if company_name:
        company = Company.objects.filter(company_name=company_name).first()
    
    profile, p_created = UserProfile.objects.get_or_create(user=user)
    profile.role = role
    profile.company = company
    profile.is_active = True
    
    # Give all permissions for testing
    profile.can_view_sales = True
    profile.can_edit_sales = True
    profile.can_view_purchase = True
    profile.can_edit_purchase = True
    profile.can_view_masters = True
    profile.can_edit_masters = True
    profile.can_view_reports = True
    profile.save()
    
    status = "created" if created else "updated"
    print(f"User '{username}' {status} with role '{role}'")

if __name__ == "__main__":
    company_name = "SVR CHEMICALS"
    
    # 1. Super Admin
    create_test_user("superadmin_test", "admin@123", "superadmin")
    
    # 2. Company Admin
    create_test_user("admin_test", "admin@123", "admin", company_name)
    
    # 3. Staff
    create_test_user("staff_test", "admin@123", "staff", company_name)
    
    print("\nTest users are ready.")
    print("SuperAdmin: superadmin_test / admin@123")
    print("Admin:      admin_test      / admin@123")
    print("Staff:      staff_test      / admin@123")

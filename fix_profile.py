import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "erp_saas.settings")
django.setup()
from django.contrib.auth.models import User
from core.models import UserProfile, Company

u = User.objects.filter(is_superuser=True).first()
if u:
    print(f"Found superuser: {u.username}")
    p, created = UserProfile.objects.get_or_create(user=u, defaults={'role': 'admin', 'is_active': True})
    if created:
        print(f"Created profile for {u.username}")
    else:
        print(f"Profile exists for {u.username}: {p.role}")
    
    # Ensure it's admin so menus show
    if p.role != 'admin' and p.role != 'superadmin':
        p.role = 'admin'
        p.save()
        print(f"Updated {u.username} role to admin")
        
    # Link to a company if not linked
    if not p.company:
        c = Company.objects.first()
        if c:
            p.company = c
            p.save()
            print(f"Linked {u.username} to company {c.company_name}")
else:
    print("No superuser found.")

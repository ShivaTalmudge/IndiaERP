import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_saas.settings')
django.setup()

from django.test import Client
from core.models import SalesInvoice, User

c = Client()
user = User.objects.filter(is_superuser=True).first()
if user:
    c.force_login(user)
    invoices = SalesInvoice.objects.all()
    for invoice in invoices:
        response = c.get(f'/sales/{invoice.pk}/', HTTP_HOST='localhost')
        print(f"Testing invoice {invoice.pk}")
        if response.status_code >= 400:
            print(f"Error on invoice {invoice.pk}: {response.status_code}")
            # print(response.content.decode()[:1000])
    print("Test finished.")
else:
    print("No user.")

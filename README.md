# IndiaERP — Multi-Tenant SaaS ERP

A Django-based ERP SaaS platform with multi-company support, GST invoicing, purchase orders, inventory management, and role-based access control.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Auth protection | django-axes |
| Static files | WhiteNoise |
| Date utilities | python-dateutil |
| Config | python-decouple |

---

## Quick Start (Development)

### 1. Clone and create virtual environment
```bash
git clone <your-repo-url>
cd erp_final
python -m venv venv
```

### 2. Activate venv
```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
copy .env.example .env   # Windows
cp .env.example .env     # macOS/Linux
# Edit .env with your SECRET_KEY and other values
```

### 5. Apply migrations
```bash
python manage.py migrate
```

### 6. Create a superadmin user
```bash
python manage.py shell -c "
from django.contrib.auth.models import User
from core.models import UserProfile
u = User.objects.create_superuser('superadmin', 'admin@example.com', 'your-password')
UserProfile.objects.create(user=u, role='superadmin', is_active=True)
print('Superadmin created!')
"
```

### 7. Collect static files (optional in dev)
```bash
python manage.py collectstatic --noinput
```

### 8. Run the dev server
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

---

## Project Structure

```
erp_final/
├── core/
│   ├── views/              # Split view modules (auth, dashboard, sales, etc.)
│   │   ├── __init__.py     # Re-exports all views
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── superadmin.py
│   │   ├── staff.py
│   │   ├── masters.py
│   │   ├── sales.py
│   │   ├── purchase.py
│   │   └── reports.py
│   ├── services.py         # Business logic (invoice/PO creation)
│   ├── models.py           # All data models
│   ├── forms.py            # All forms
│   ├── admin.py            # Django admin registrations
│   ├── decorators.py       # Auth permission decorators
│   ├── middleware.py       # License + company context middleware
│   └── urls.py             # URL routing
├── erp_saas/
│   └── settings.py         # Environment-based settings
├── templates/
│   ├── core/               # Base, dashboard, login, reports
│   ├── masters/            # Product, customer, supplier forms/lists
│   ├── sales/              # Invoice forms/lists/detail
│   ├── purchase/           # PO forms/lists/detail
│   ├── superadmin/         # Company management
│   └── includes/           # Reusable snippets (pagination)
├── static/
│   └── css/main.css        # Application stylesheet
├── .env                    # Secret config (git-ignored)
├── .env.example            # Template for .env
├── .gitignore
└── requirements.txt
```

---

## User Roles

| Role | Access |
|------|--------|
| `superadmin` | Manage all companies, create admins |
| `admin` | Full access to company data + staff management |
| `staff` | Granular permissions per module (view/edit) |

---

## Key Features

- ✅ Multi-company SaaS with license expiry enforcement
- ✅ GST Invoicing (CGST + SGST + IGST) with line-item breakdown
- ✅ Purchase Orders with stock auto-update
- ✅ Invoice/PO cancellation with stock reversal
- ✅ Payment tracking per invoice (Unpaid / Partial / Paid)
- ✅ Low-stock alerts on dashboard (DB-level query)
- ✅ Sales / Purchase / Stock reports with CSV export
- ✅ Role-based granular permissions
- ✅ Brute-force login protection (django-axes, 5 attempts)
- ✅ Paginated list views (25 records/page)
- ✅ Full Django Admin with inline line items

---

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Set `ALLOWED_HOSTS=yourdomain.com` in `.env`
3. Switch to PostgreSQL (set `DB_ENGINE`, `DB_NAME`, etc. in `.env`)
4. Run `python manage.py collectstatic`
5. Serve with `gunicorn erp_saas.wsgi:application` (Linux/macOS)
   - On Windows use `waitress`: `pip install waitress` → `waitress-serve --port=8000 erp_saas.wsgi:application`
6. Set up Nginx/Apache as reverse proxy

---

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | *required* |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `127.0.0.1` |
| `DB_ENGINE` | Database backend | `sqlite3` |
| `DB_NAME` | DB name (PostgreSQL) | — |
| `DB_USER` | DB user | — |
| `DB_PASSWORD` | DB password | — |
| `EMAIL_HOST` | SMTP server | `smtp.gmail.com` |
| `EMAIL_HOST_USER` | SMTP username | — |
| `EMAIL_HOST_PASSWORD` | SMTP password | — |

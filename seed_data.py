"""
seed_data.py — Populate SVR CHEMICALS with comprehensive test data.
Run: python seed_data.py
"""
import os, sys, django
from decimal import Decimal
from datetime import date, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "erp_saas.settings")
django.setup()

from django.contrib.auth.models import User
from core.models import (
    Company, UserProfile,
    ProductCategory, UnitMaster, HSNCode, TaxMaster,
    Supplier, Customer, Product,
    SalesInvoice, SalesLineItem,
    PurchaseOrder, PurchaseLineItem,
    Quotation, QuotationLineItem,
    EWayBill,
)

# ── Helper ────────────────────────────────────────────────────────────────────
def p(msg): print(f"  ✓ {msg}")
def h(msg): print(f"\n{'─'*55}\n  {msg}\n{'─'*55}")

TODAY = date.today()
def days_ago(n): return TODAY - timedelta(days=n)
def days_ahead(n): return TODAY + timedelta(days=n)

# ── Get Company ───────────────────────────────────────────────────────────────
company = Company.objects.filter(company_name="SVR CHEMICALS").first()
if not company:
    print("ERROR: SVR CHEMICALS company not found. Cannot seed.")
    sys.exit(1)

# Ensure company has location for GST logic
company.city = "Hyderabad"
company.state = "TG"
company.pincode = "500001"
company.save()

h("Seeding SVR CHEMICALS ERP Test Data")
print(f"  Company: {company.company_name} | GST: {company.gst_number} | State: {company.state}")

# ── 1. Units of Measure ───────────────────────────────────────────────────────
h("1. Units of Measure")
units_data = [
    ("Kilogram",     "KG"),
    ("Gram",         "GM"),
    ("Litre",        "LTR"),
    ("Millilitre",   "ML"),
    ("Piece",        "PCS"),
    ("Box",          "BOX"),
    ("Bag",          "BAG"),
    ("Drum",         "DRM"),
    ("Metric Ton",   "MT"),
    ("Number",       "NOS"),
]
units = {}
for name, short in units_data:
    u, created = UnitMaster.objects.get_or_create(
        company=company, short_name=short,
        defaults={"name": name}
    )
    units[short] = u
    if created: p(f"Unit: {name} ({short})")

# ── 2. Product Categories ─────────────────────────────────────────────────────
h("2. Product Categories")
cats_data = [
    ("Industrial Chemicals",  "Raw materials for industrial processes"),
    ("Cleaning Agents",       "Detergents and cleaning solutions"),
    ("Lab Chemicals",         "Laboratory grade chemicals"),
    ("Solvents",              "Organic and inorganic solvents"),
    ("Acids & Bases",         "Acid and alkali products"),
    ("Safety Equipment",      "PPE and safety gear"),
    ("Packaging Materials",   "Drums, bags, containers"),
]
cats = {}
for name, desc in cats_data:
    c_obj, created = ProductCategory.objects.get_or_create(
        company=company, name=name,
        defaults={"description": desc}
    )
    cats[name] = c_obj
    if created: p(f"Category: {name}")

# ── 3. HSN Codes ──────────────────────────────────────────────────────────────
h("3. HSN Codes")
hsn_data = [
    ("2807", "Sulphuric Acid",            "Acids & Bases"),
    ("2815", "Sodium Hydroxide (Caustic Soda)", "Acids & Bases"),
    ("2836", "Sodium Carbonate (Soda Ash)", "Industrial Chemicals"),
    ("2905", "Isopropyl Alcohol (IPA)",   "Solvents"),
    ("3402", "Detergent Raw Materials",   "Cleaning Agents"),
    ("3824", "Chemical Preparations",    "Industrial Chemicals"),
    ("3811", "Anti-knock Compounds",     "Industrial Chemicals"),
    ("2804", "Hydrogen Peroxide",        "Lab Chemicals"),
    ("6305", "HDPE Bags",               "Packaging Materials"),
    ("3926", "Plastic Drums",           "Packaging Materials"),
]
hsns = {}
for code, desc, cat_name in hsn_data:
    h_obj, created = HSNCode.objects.get_or_create(
        company=company, code=code,
        defaults={"description": desc}
    )
    hsns[code] = h_obj
    if created: p(f"HSN {code}: {desc}")

# ── 4. Tax Masters ────────────────────────────────────────────────────────────
h("4. GST Tax Slabs")
tax_data = [
    ("GST 5%",  Decimal("2.5"),  Decimal("2.5"),  Decimal("5.0")),
    ("GST 12%", Decimal("6.0"),  Decimal("6.0"),  Decimal("12.0")),
    ("GST 18%", Decimal("9.0"),  Decimal("9.0"),  Decimal("18.0")),
    ("GST 28%", Decimal("14.0"), Decimal("14.0"), Decimal("28.0")),
]
taxes = {}
for name, cgst, sgst, igst in tax_data:
    t_obj, created = TaxMaster.objects.get_or_create(
        company=company, name=name,
        defaults={"cgst_percent": cgst, "sgst_percent": sgst, "igst_percent": igst}
    )
    taxes[name] = t_obj
    if created: p(f"Tax: {name}")

# ── 5. Suppliers ──────────────────────────────────────────────────────────────
h("5. Suppliers")
suppliers_data = [
    {
        "name": "Aditya Chemicals Pvt Ltd",
        "contact_person": "Mr. Rajan Mehta",
        "phone": "9845101010",
        "email": "sales@adityachem.com",
        "address": "Plot 45, MIDC Industrial Area, Pune",
        "city": "Pune",
        "state": "MH",
        "pincode": "411019",
        "gst_number": "27AACCA1234C1ZK",
    },
    {
        "name": "National Chemical Distributors",
        "contact_person": "Ms. Priya Sharma",
        "phone": "9811202020",
        "email": "procurement@nationalchem.in",
        "address": "12, Chemical Zone, Sector 58",
        "city": "Noida",
        "state": "UP",
        "pincode": "201301",
        "gst_number": "09AAACN5678B1ZM",
    },
    {
        "name": "Bharat Solvents & Acids",
        "contact_person": "Mr. Suresh Iyer",
        "phone": "9944303030",
        "email": "info@bharatsolv.co.in",
        "address": "Survey No. 88, Ambattur Industrial Estate",
        "city": "Chennai",
        "state": "TN",
        "pincode": "600058",
        "gst_number": "33AAFCB9012D1ZP",
    },
    {
        "name": "Hydra Chemicals TG",
        "contact_person": "Mr. Satish Reddy",
        "phone": "9440506070",
        "email": "sales@hydrachems.in",
        "address": "Uppal Industrial Area",
        "city": "Hyderabad",
        "state": "TG",
        "pincode": "500039",
        "gst_number": "36AAACH3333C1ZT",
    },
]
suppliers = {}
for s in suppliers_data:
    s_obj, created = Supplier.objects.get_or_create(
        company=company, name=s["name"],
        defaults=s
    )
    suppliers[s["name"]] = s_obj
    if created: p(f"Supplier: {s['name']}")

# ── 6. Customers ──────────────────────────────────────────────────────────────
h("6. Customers")
customers_data = [
    {
        "name": "Mahindra Agri Solutions Ltd",
        "contact_person": "Mr. Vikram Desai",
        "phone": "9820505050",
        "email": "purchase@mahindraagri.com",
        "address": "Gateway House, Apollo Bunder",
        "city": "Mumbai",
        "state": "MH",
        "pincode": "400001",
        "gst_number": "27AABCM1111A1ZR",
    },
    {
        "name": "Tata Chemicals Limited",
        "contact_person": "Ms. Ritu Nair",
        "phone": "9820606060",
        "email": "chem.purchase@tata.com",
        "address": "Bombay House, 24 Homi Mody Street",
        "city": "Mumbai",
        "state": "MH",
        "pincode": "400001",
        "gst_number": "27AAACT2222B1ZS",
    },
    {
        "name": "Hindustan Unilever - Industrial",
        "contact_person": "Mr. Deepak Malhotra",
        "phone": "9820707070",
        "email": "ind.purchase@hul.com",
        "address": "Unilever House, BB Nakashe Marg, Chakala, Andheri (E)",
        "city": "Mumbai",
        "state": "MH",
        "pincode": "400099",
        "gst_number": "27AAACH3333C1ZT",
    },
    {
        "name": "Excel Industries Pvt Ltd",
        "contact_person": "Mr. Nikhil Joshi",
        "phone": "9820808080",
        "email": "purchases@excelindustries.net",
        "address": "184-87 Swami Vivekanand Road, Jogeshwari (W)",
        "city": "Mumbai",
        "state": "MH",
        "pincode": "400102",
        "gst_number": "27AAACE4444D1ZU",
    },
    {
        "name": "Telangana Pharma Hub",
        "contact_person": "Mr. K. Rao",
        "phone": "9848011223",
        "email": "procurement@tpharma.in",
        "address": "Genome Valley, Shameerpet",
        "city": "Hyderabad",
        "state": "TG",
        "pincode": "500078",
        "gst_number": "36AAACT1111A1ZR",
    },
    {
        "name": "Andhra Petrochemicals Limited",
        "contact_person": "Mr. Ramesh Babu",
        "phone": "9440101010",
        "email": "rm.purchase@apl.in",
        "address": "Kondapalli Village, Krishna District",
        "city": "Vijayawada",
        "state": "AP",
        "pincode": "521228",
        "gst_number": "37AAACA6666F1ZW",
    },
]
customers = {}
for c_data in customers_data:
    c_obj, created = Customer.objects.get_or_create(
        company=company, name=c_data["name"],
        defaults=c_data
    )
    customers[c_data["name"]] = c_obj
    if created: p(f"Customer: {c_data['name']}")

# ── 7. Products ───────────────────────────────────────────────────────────────
h("7. Products")
products_data = [
    # name, category, unit, hsn, tax, price, stock, reorder
    ("Sulphuric Acid 98% (Technical)",  "Acids & Bases",          "KG",  "2807", "GST 18%", 45.00,  2500, 500),
    ("Sodium Hydroxide Flakes 99%",     "Acids & Bases",          "KG",  "2815", "GST 18%", 38.50,  3200, 600),
    ("Soda Ash Light (Dense)",          "Industrial Chemicals",   "MT",  "2836", "GST 18%", 22500,  15,    3),
    ("Isopropyl Alcohol (IPA) 99%",     "Solvents",               "LTR", "2905", "GST 18%", 95.00,  800,  150),
    ("Hydrochloric Acid 33%",           "Acids & Bases",          "KG",  "2807", "GST 18%", 18.00,  4000, 800),
    ("Hydrogen Peroxide 50%",           "Lab Chemicals",          "KG",  "2804", "GST 12%", 62.00,  600,  100),
    ("Sodium Hypochlorite 10%",         "Cleaning Agents",        "LTR", "3402", "GST 18%", 12.50,  5000, 1000),
    ("Linear Alkyl Benzene Sulphonate", "Cleaning Agents",        "KG",  "3402", "GST 18%", 88.00,  1200, 200),
    ("Methanol (Methyl Alcohol)",       "Solvents",               "LTR", "2905", "GST 18%", 42.00,  1500, 300),
    ("Acetone (Dimethyl Ketone)",       "Solvents",               "LTR", "2905", "GST 18%", 68.00,  900,  180),
    ("Caustic Potash (KOH) Flakes",     "Acids & Bases",          "KG",  "2815", "GST 18%", 72.00,  700,  100),
    ("Ferric Chloride Anhydrous",       "Industrial Chemicals",   "KG",  "3824", "GST 18%", 35.00,  1800, 350),
    ("HDPE Drum 200 Litre",             "Packaging Materials",    "NOS", "3926", "GST 18%", 1250.00, 150, 30),
    ("PP Woven Bag 50 KG",              "Packaging Materials",    "NOS", "6305", "GST 5%",  28.00,  2000, 400),
    ("Glacial Acetic Acid",             "Lab Chemicals",          "LTR", "2905", "GST 18%", 85.00,  500,  100),
]
products = {}
for row in products_data:
    name, cat_name, unit_short, hsn_code, tax_name, price, stock, reorder = row
    p_obj, created = Product.objects.get_or_create(
        company=company, name=name,
        defaults={
            "category":      cats.get(cat_name),
            "unit":          units.get(unit_short),
            "hsn_code":      hsns.get(hsn_code),
            "tax":           taxes.get(tax_name),
            "price":         Decimal(str(price)),
            "stock":         Decimal(str(stock)),
            "reorder_level": Decimal(str(reorder)),
            "is_active":     True,
        }
    )
    products[name] = p_obj
    if created: p(f"Product: {name}")

# ── 8. Users for Seeding ──────────────────────────────────────────────────────
# Ensure admin user exists or fallback to first superuser
admin_user = User.objects.filter(username="admin").first() or User.objects.first()

# ── 9. Purchase Orders ────────────────────────────────────────────────────────
h("8. Purchase Orders")
PurchaseOrder.objects.filter(company=company).delete()
po_data = [
    {
        "supplier": "Aditya Chemicals Pvt Ltd",
        "date": days_ago(45),
        "status": "received",
        "items": [
            ("Sulphuric Acid 98% (Technical)",  500, 32.00, 18),
            ("Hydrochloric Acid 33%",           800, 12.50, 18),
        ]
    },
    {
        "supplier": "National Chemical Distributors",
        "date": days_ago(30),
        "status": "received",
        "items": [
            ("Sodium Hydroxide Flakes 99%",     600, 28.00, 18),
            ("Sodium Hypochlorite 10%",        1000,  8.00, 18),
        ]
    },
    {
        "supplier": "Bharat Solvents & Acids",
        "date": days_ago(20),
        "status": "received",
        "items": [
            ("Isopropyl Alcohol (IPA) 99%",    200, 72.00, 18),
            ("Methanol (Methyl Alcohol)",       300, 32.00, 18),
            ("Acetone (Dimethyl Ketone)",       150, 52.00, 18),
        ]
    },
    {
        "supplier": "Hydra Chemicals TG",
        "date": days_ago(15),
        "status": "received",
        "items": [
            ("HDPE Drum 200 Litre",              50, 950.00,  18),
            ("PP Woven Bag 50 KG",             500,  20.00,   5),
        ]
    },
    {
        "supplier": "Aditya Chemicals Pvt Ltd",
        "date": days_ago(5),
        "status": "pending",
        "items": [
            ("Sulphuric Acid 98% (Technical)", 1000, 32.00, 18),
            ("Glacial Acetic Acid", 100, 65.00, 18),
        ]
    },
    {
        "supplier": "National Chemical Distributors",
        "date": TODAY,
        "status": "pending",
        "items": [
            ("Hydrogen Peroxide 50%",           200, 45.00, 12),
            ("Linear Alkyl Benzene Sulphonate", 300, 65.00, 18),
        ]
    },
]

po_count = 0
created_pos = []

for i, po in enumerate(po_data):
    po_count += 1
    year = po["date"].year
    po_number = f"PO/{year}/{po_count:03d}"
    supplier = suppliers[po["supplier"]]

    subtotal = total_cgst = total_sgst = total_igst = Decimal("0")
    line_items_data = []
    
    is_interstate = (company.state != supplier.state) if (company.state and supplier.state) else False
    
    for prod_name, qty, cost, gst_rate in po["items"]:
        prod = products.get(prod_name)
        if not prod:
            continue
        tax = taxes.get(f"GST {gst_rate}%")
        
        cgst_pct = tax.cgst_percent if (not is_interstate and tax) else Decimal("0")
        sgst_pct = tax.sgst_percent if (not is_interstate and tax) else Decimal("0")
        igst_pct = tax.igst_percent if (is_interstate and tax) else Decimal("0")
        
        q = Decimal(str(qty))
        up = Decimal(str(cost))
        taxable = q * up
        cgst_amt = taxable * cgst_pct / 100
        sgst_amt = taxable * sgst_pct / 100
        igst_amt = taxable * igst_pct / 100
        line_total = taxable + cgst_amt + sgst_amt + igst_amt
        subtotal   += taxable
        total_cgst += cgst_amt
        total_sgst += sgst_amt
        total_igst += igst_amt
        line_items_data.append({
            "product": prod, "quantity": q, "unit_price": up,
            "cgst_percent": cgst_pct, "sgst_percent": sgst_pct, "igst_percent": igst_pct,
            "taxable_amount": taxable, "cgst_amount": cgst_amt, "sgst_amount": sgst_amt,
            "igst_amount": igst_amt, "line_total": line_total,
        })

    grand_total = subtotal + total_cgst + total_sgst + total_igst
    po_obj = PurchaseOrder.objects.create(
        company=company, supplier=supplier,
        po_number=po_number, order_date=po["date"],
        status=po["status"],
        subtotal=subtotal, total_cgst=total_cgst, total_sgst=total_sgst,
        total_igst=total_igst, grand_total=grand_total,
        notes=f"Routine supply order #{po_count}",
        created_by=admin_user,
    )
    for li in line_items_data:
        PurchaseLineItem.objects.create(order=po_obj, **li)

    p(f"PO: {po_number} | {po['supplier'][:30]} | ₹{grand_total:,.2f} [{po['status']}]")
    created_pos.append(po_obj)

# ── 10. Sales Invoices ────────────────────────────────────────────────────────
h("9. Sales Invoices")
SalesInvoice.objects.filter(company=company).delete()

inv_data = [
    {
        "customer": "Mahindra Agri Solutions Ltd",
        "date": days_ago(60),
        "status": "confirmed",
        "is_paid": True,
        "items": [
            ("Sulphuric Acid 98% (Technical)", 200, 45.00),
            ("Hydrochloric Acid 33%",          300, 18.00),
        ]
    },
    {
        "customer": "Tata Chemicals Limited",
        "date": days_ago(45),
        "status": "confirmed",
        "is_paid": True,
        "items": [
            ("Sodium Hydroxide Flakes 99%",    500,  38.50),
            ("Soda Ash Light (Dense)",           2, 22500.00),
        ]
    },
    {
        "customer": "Hindustan Unilever - Industrial",
        "date": days_ago(30),
        "status": "confirmed",
        "items": [
            ("Linear Alkyl Benzene Sulphonate", 400, 88.00),
            ("Sodium Hypochlorite 10%",        1000, 12.50),
        ]
    },
    {
        "customer": "Excel Industries Pvt Ltd",
        "date": days_ago(20),
        "status": "confirmed",
        "items": [
            ("Isopropyl Alcohol (IPA) 99%",    100,  95.00),
            ("Methanol (Methyl Alcohol)",       200,  42.00),
            ("Acetone (Dimethyl Ketone)",        80,  68.00),
        ]
    },
    {
        "customer": "Telangana Pharma Hub",
        "date": days_ago(12),
        "status": "confirmed",
        "items": [
            ("Linear Alkyl Benzene Sulphonate", 600, 88.00),
            ("Caustic Potash (KOH) Flakes",    200, 72.00),
        ]
    },
    {
        "customer": "Andhra Petrochemicals Limited",
        "date": days_ago(7),
        "status": "confirmed",
        "items": [
            ("Sulphuric Acid 98% (Technical)", 300, 45.00),
            ("Ferric Chloride Anhydrous",      200, 35.00),
        ]
    },
    {
        "customer": "Mahindra Agri Solutions Ltd",
        "date": days_ago(3),
        "status": "confirmed",
        "items": [
            ("Hydrochloric Acid 33%",          500, 18.00),
            ("HDPE Drum 200 Litre",             20, 1250.00),
        ]
    },
    {
        "customer": "Tata Chemicals Limited",
        "date": TODAY,
        "status": "draft",
        "items": [
            ("Glacial Acetic Acid",            100,  85.00),
            ("Hydrogen Peroxide 50%",          150,  62.00),
        ]
    },
]

inv_count = 0
created_invoices = []

for inv in inv_data:
    inv_count += 1
    year = inv["date"].year
    inv_number = f"INV/{year}/{inv_count:03d}"
    customer = customers[inv["customer"]]

    subtotal = total_cgst = total_sgst = total_igst = Decimal("0")
    line_items_data = []
    
    is_interstate = (company.state != customer.state) if (company.state and customer.state) else False
    
    for prod_name, qty, price in inv["items"]:
        prod = products.get(prod_name)
        if not prod:
            continue
        tax = prod.tax
        
        cgst_pct = tax.cgst_percent if (not is_interstate and tax) else Decimal("0")
        sgst_pct = tax.sgst_percent if (not is_interstate and tax) else Decimal("0")
        igst_pct = tax.igst_percent if (is_interstate and tax) else Decimal("0")
        
        q       = Decimal(str(qty))
        up      = Decimal(str(price))
        taxable = q * up
        cgst_amt = taxable * cgst_pct / 100
        sgst_amt = taxable * sgst_pct / 100
        igst_amt = taxable * igst_pct / 100
        line_total = taxable + cgst_amt + sgst_amt + igst_amt
        subtotal   += taxable
        total_cgst += cgst_amt
        total_sgst += sgst_amt
        total_igst += igst_amt
        line_items_data.append({
            "product": prod, "quantity": q, "unit_price": up,
            "discount_percent": Decimal("0"),
            "cgst_percent": cgst_pct, "sgst_percent": sgst_pct, "igst_percent": igst_pct,
            "taxable_amount": taxable, "cgst_amount": cgst_amt,
            "sgst_amount": sgst_amt, "igst_amount": igst_amt,
            "line_total": line_total,
        })

    grand_total = subtotal + total_cgst + total_sgst + total_igst
    due_date = inv["date"] + timedelta(days=30)
    payment_status = "paid" if inv.get("is_paid", False) else "unpaid"
    
    inv_obj = SalesInvoice.objects.create(
        company=company, customer=customer,
        invoice_number=inv_number,
        invoice_date=inv["date"],
        due_date=due_date,
        status=inv["status"],
        subtotal=subtotal, total_cgst=total_cgst, total_sgst=total_sgst,
        total_igst=total_igst, grand_total=grand_total,
        created_by=admin_user,
        notes="Payment by NEFT/RTGS within credit period.",
        payment_status=payment_status,
        amount_paid=grand_total if payment_status == "paid" else Decimal("0"),
    )
    for li in line_items_data:
        SalesLineItem.objects.create(invoice=inv_obj, **li)

    p(f"Invoice: {inv_number} | {inv['customer'][:30]} | ₹{grand_total:,.2f} [{inv['status']}]")
    created_invoices.append(inv_obj)

# ── 11. Quotations ────────────────────────────────────────────────────────────
h("10. Quotations")
Quotation.objects.filter(company=company).delete()
quot_data = [
    {
        "customer": "Mahindra Agri Solutions Ltd",
        "date": days_ago(20), "valid": days_ahead(10),
        "status": "sent",
        "items": [
            ("Sulphuric Acid 98% (Technical)", 500, 45.00, 2),
            ("Hydrochloric Acid 33%",         1000, 18.00, 2),
        ]
    },
    {
        "customer": "Excel Industries Pvt Ltd",
        "date": days_ago(10), "valid": days_ahead(20),
        "status": "approved",
        "items": [
            ("Isopropyl Alcohol (IPA) 99%",   300, 95.00, 1),
            ("Acetone (Dimethyl Ketone)",      200, 68.00, 1),
        ]
    },
    {
        "customer": "Telangana Pharma Hub",
        "date": days_ago(5), "valid": days_ahead(25),
        "status": "draft",
        "items": [
            ("Linear Alkyl Benzene Sulphonate", 1000, 88.00, 2),
            ("Sodium Hydroxide Flakes 99%",      500, 38.50, 2),
            ("Caustic Potash (KOH) Flakes",      300, 72.00, 2),
        ]
    },
]

q_count = 0
for q_data in quot_data:
    q_count += 1
    year = q_data["date"].year
    q_number = f"QT/{year}/{q_count:03d}"
    customer = customers[q_data["customer"]]

    subtotal = total_cgst = total_sgst = total_igst = Decimal("0")
    line_items_data = []
    
    is_interstate = (company.state != customer.state) if (company.state and customer.state) else False

    for prod_name, qty, price, disc in q_data["items"]:
        prod = products.get(prod_name)
        if not prod: continue
        tax = prod.tax
        cgst_pct = tax.cgst_percent if (not is_interstate and tax) else Decimal("0")
        sgst_pct = tax.sgst_percent if (not is_interstate and tax) else Decimal("0")
        igst_pct = tax.igst_percent if (is_interstate and tax) else Decimal("0")

        q_qty   = Decimal(str(qty))
        up      = Decimal(str(price))
        disc_pct = Decimal(str(disc))
        taxable = q_qty * up * (1 - disc_pct / 100)
        cgst_amt = taxable * cgst_pct / 100
        sgst_amt = taxable * sgst_pct / 100
        igst_amt = taxable * igst_pct / 100
        line_total = taxable + cgst_amt + sgst_amt + igst_amt
        subtotal   += taxable
        total_cgst += cgst_amt
        total_sgst += sgst_amt
        total_igst += igst_amt
        line_items_data.append({
            "product": prod,
            "quantity": q_qty, "unit_price": up, "discount_percent": disc_pct,
            "cgst_percent": cgst_pct, "sgst_percent": sgst_pct, "igst_percent": igst_pct,
            "taxable_amount": taxable, "cgst_amount": cgst_amt,
            "sgst_amount": sgst_amt, "igst_amount": igst_amt,
            "line_total": line_total,
        })

    grand_total = subtotal + total_cgst + total_sgst + total_igst
    quot_obj = Quotation.objects.create(
        company=company, customer=customer,
        quotation_number=q_number,
        quotation_date=q_data["date"],
        valid_until=q_data["valid"],
        status=q_data["status"],
        subtotal=subtotal, total_cgst=total_cgst, total_sgst=total_sgst,
        total_igst=total_igst, grand_total=grand_total,
        created_by=admin_user,
        notes="Prices valid for the period mentioned.",
        terms="Payment: 50% advance.",
    )
    for li in line_items_data:
        QuotationLineItem.objects.create(quotation=quot_obj, **li)

    p(f"Quotation: {q_number} | ₹{grand_total:,.2f}")

h("✅ Seeding Complete")

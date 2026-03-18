"""core/views/dashboard.py — Main dashboard for admin/staff users."""
import json
from datetime import date
from dateutil.relativedelta import relativedelta

from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.db.models import Sum, F

from ..models import Product, Customer, Supplier, SalesInvoice
from ..decorators import login_required_custom


def _profile(user):
    try:
        return user.profile
    except Exception:
        return None


@login_required_custom
def dashboard(request):
    p = _profile(request.user)
    if p is None:
        logout(request)
        messages.error(request, "Account setup incomplete. Contact administrator.")
        return redirect("login")
    if p.role == "superadmin":
        return redirect("superadmin_dashboard")

    company = request.company
    today = date.today()
    month_start = today.replace(day=1)

    # ── KPI queries ───────────────────────────────────────────────────────────
    products = Product.objects.for_user(request.user).filter(is_active=True)

    # DB-level low-stock filter (no Python loop)
    low_stock_qs = products.filter(stock__lte=F("reorder_level"))

    monthly_sales = (
        SalesInvoice.objects.for_user(request.user).filter(
            invoice_date__gte=month_start, status="confirmed"
        ).aggregate(t=Sum("grand_total"))["t"] or 0
    )

    from ..models import PurchaseOrder
    monthly_purchases = (
        PurchaseOrder.objects.for_user(request.user).filter(
            order_date__gte=month_start, status="received"
        ).aggregate(t=Sum("grand_total"))["t"] or 0
    )

    # ── Chart: last 6 calendar months (Optimized to single query) ────────────
    six_months_ago = (today - relativedelta(months=5)).replace(day=1)
    all_sales = SalesInvoice.objects.for_user(request.user).filter(
        status="confirmed", invoice_date__gte=six_months_ago
    ).values("invoice_date", "grand_total")

    # Group by month in Python to avoid N+1 queries
    labels, sales_data = [], []
    for i in range(5, -1, -1):
        ms = (today - relativedelta(months=i)).replace(day=1)
        me = ms + relativedelta(months=1) - relativedelta(days=1)
        
        # Filter from the pre-fetched list
        amt = sum(
            inv["grand_total"] for inv in all_sales 
            if ms <= inv["invoice_date"] <= me
        )
        
        labels.append(ms.strftime("%b %Y"))
        sales_data.append(float(amt))

    return render(request, "core/dashboard.html", {
        "total_products":     products.count(),
        "total_customers":    Customer.objects.for_user(request.user).count(),
        "total_suppliers":    Supplier.objects.for_user(request.user).count(),
        "low_stock_count":    low_stock_qs.count(),
        "low_stock_products": low_stock_qs.select_related("unit")[:5],
        "monthly_sales":      monthly_sales,
        "monthly_purchases":  monthly_purchases,
        "recent_invoices":    SalesInvoice.objects.for_user(request.user)
                               .select_related("customer").order_by("-created_at")[:5],
        "chart_labels":       json.dumps(labels),
        "chart_sales":        json.dumps(sales_data),
    })

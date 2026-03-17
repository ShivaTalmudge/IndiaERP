"""core/views/superadmin.py — Super-admin company management."""
import json
from datetime import date
from dateutil.relativedelta import relativedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.db import transaction

from ..models import Company, UserProfile
from ..forms import CompanyForm, CompanyEditForm
from ..decorators import superadmin_required


@superadmin_required
def superadmin_dashboard(request):
    today = date.today()
    companies = Company.objects.all().order_by("-created_at")

    labels, reg_data = [], []
    for i in range(5, -1, -1):
        ms = (today - relativedelta(months=i)).replace(day=1)
        me = ms + relativedelta(months=1) - relativedelta(days=1)
        cnt = Company.objects.filter(
            created_at__date__gte=ms, created_at__date__lte=me
        ).count()
        labels.append(ms.strftime("%b %Y"))
        reg_data.append(cnt)

    return render(request, "superadmin/dashboard.html", {
        "total_companies":  companies.count(),
        "active_companies": companies.filter(is_active=True).count(),
        "expired_licenses": companies.filter(license_end_date__lt=today).count(),
        "companies":        companies[:10],
        "chart_labels":     json.dumps(labels),
        "chart_reg":        json.dumps(reg_data),
    })


@superadmin_required
def company_list(request):
    q = request.GET.get("q", "")
    qs = Company.objects.all().order_by("-created_at")
    if q:
        qs = qs.filter(Q(company_name__icontains=q) | Q(contact_email__icontains=q))
    return render(request, "superadmin/company_list.html", {"companies": qs, "q": q})


@superadmin_required
def company_add(request):
    form = CompanyForm()
    if request.method == "POST":
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            uname = form.cleaned_data["admin_username"]
            if User.objects.filter(username=uname).exists():
                form.add_error("admin_username", "Username already taken.")
            else:
                with transaction.atomic():
                    company = form.save()
                    u = User.objects.create_user(
                        username=uname,
                        password=form.cleaned_data["admin_password"],
                        email=form.cleaned_data.get("admin_email", ""),
                    )
                    UserProfile.objects.create(
                        user=u, company=company, role="admin", is_active=True
                    )
                messages.success(
                    request,
                    f"Company '{company.company_name}' created. Admin: {uname}",
                )
                return redirect("company_list")
    return render(
        request, "superadmin/company_form.html", {"form": form, "title": "Add Company"}
    )


@superadmin_required
def company_edit(request, pk):
    company = get_object_or_404(Company, pk=pk)
    form = CompanyEditForm(instance=company)
    if request.method == "POST":
        form = CompanyEditForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, "Company updated.")
            return redirect("company_list")
    return render(
        request,
        "superadmin/company_form.html",
        {"form": form, "title": "Edit Company", "company": company},
    )


@superadmin_required
def company_toggle(request, pk):
    """Toggle company active state — POST only to prevent CSRF via URL."""
    if request.method != "POST":
        return redirect("company_list")
    company = get_object_or_404(Company, pk=pk)
    company.is_active = not company.is_active
    company.save()
    state = "activated" if company.is_active else "deactivated"
    messages.success(request, f"'{company.company_name}' {state}.")
    return redirect("company_list")

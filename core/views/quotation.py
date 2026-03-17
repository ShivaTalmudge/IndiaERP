"""core/views/quotation.py — Quotation CRUD + status tracking."""
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
import csv

from ..models import Product, Customer, Quotation, QuotationLineItem, SalesInvoice, SalesLineItem
from ..decorators import permission_required
from ..utils import _decimal
from django.db import transaction

PAGE_SIZE = 25


@permission_required("can_view_sales")
def quotation_list(request):
    q      = request.GET.get("q", "")
    status = request.GET.get("status", "")
    qs = Quotation.objects.filter(company=request.company).select_related("customer")
    if q:
        qs = qs.filter(Q(quotation_number__icontains=q) | Q(customer__name__icontains=q))
    if status:
        qs = qs.filter(status=status)
    page = Paginator(qs, PAGE_SIZE).get_page(request.GET.get("page"))
    return render(request, "sales/quotation_list.html", {
        "page_obj": page, "quotations": page.object_list, "q": q, "status_filter": status,
        "status_choices": Quotation.STATUS,
    })


@permission_required("can_edit_sales")
def quotation_create(request):
    company  = request.company
    products = Product.objects.filter(company=company, is_active=True).select_related("tax", "unit")
    customers = Customer.objects.filter(company=company)

    if request.method == "POST":
        try:
            quotation = _save_quotation(None, company, request.user, request.POST)
            messages.success(request, f"Quotation {quotation.quotation_number} created.")
            return redirect("quotation_detail", pk=quotation.pk)
        except ValueError as e:
            messages.error(request, str(e))

    return render(request, "sales/quotation_form.html", {
        "products": products, "customers": customers, "action": "Create",
    })


@permission_required("can_edit_sales")
def quotation_edit(request, pk):
    company   = request.company
    quotation = get_object_or_404(Quotation, pk=pk, company=company)
    products  = Product.objects.filter(company=company, is_active=True).select_related("tax", "unit")
    customers = Customer.objects.filter(company=company)

    if request.method == "POST":
        try:
            quotation = _save_quotation(quotation, company, request.user, request.POST)
            messages.success(request, f"Quotation {quotation.quotation_number} updated.")
            return redirect("quotation_detail", pk=quotation.pk)
        except ValueError as e:
            messages.error(request, str(e))

    return render(request, "sales/quotation_form.html", {
        "quotation": quotation, "products": products, "customers": customers, "action": "Edit",
    })


@permission_required("can_view_sales")
def quotation_detail(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk, company=request.company)
    company   = request.company
    return render(request, "sales/quotation_detail.html", {
        "quotation": quotation, "company": company,
    })


@permission_required("can_view_sales")
def quotation_print_view(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk, company=request.company)
    company   = request.company
    return render(request, "sales/quotation_print.html", {
        "quotation": quotation, "company": company,
    })


@permission_required("can_edit_sales")
def quotation_status(request, pk):
    """Update quotation status via POST."""
    if request.method != "POST":
        return redirect("quotation_list")
    quotation  = get_object_or_404(Quotation, pk=pk, company=request.company)
    new_status = request.POST.get("status")
    valid = [s[0] for s in Quotation.STATUS]
    if new_status not in valid:
        messages.error(request, "Invalid status.")
    else:
        quotation.status = new_status
        quotation.save(update_fields=["status"])
        messages.success(request, f"Status updated to {quotation.get_status_display()}.")
    return redirect("quotation_detail", pk=pk)


@permission_required("can_edit_sales")
@transaction.atomic
def quotation_convert(request, pk):
    """Convert approved quotation to a confirmed Sales Invoice and update stock."""
    if request.method != "POST":
        return redirect("quotation_list")
    quotation = get_object_or_404(Quotation, pk=pk, company=request.company, status="approved")
    company   = request.company

    # Generate invoice number
    from datetime import date
    year  = date.today().year
    count = SalesInvoice.objects.filter(company=company).count() + 1
    inv_no = f"INV/{year}/{count:03d}"
    while SalesInvoice.objects.filter(company=company, invoice_number=inv_no).exists():
        count += 1
        inv_no = f"INV/{year}/{count:03d}"

    invoice = SalesInvoice.objects.create(
        company=company, invoice_number=inv_no, customer=quotation.customer,
        invoice_date=date.today(), status="confirmed",
        notes=quotation.notes, subtotal=quotation.subtotal,
        total_cgst=quotation.total_cgst, total_sgst=quotation.total_sgst,
        total_igst=quotation.total_igst, grand_total=quotation.grand_total,
        created_by=request.user,
    )
    for li in quotation.line_items.select_for_update().select_related("product").all():
        SalesLineItem.objects.create(
            invoice=invoice, product=li.product, quantity=li.quantity,
            unit_price=li.unit_price, discount_percent=li.discount_percent,
            cgst_percent=li.cgst_percent, sgst_percent=li.sgst_percent,
            igst_percent=li.igst_percent, taxable_amount=li.taxable_amount,
            cgst_amount=li.cgst_amount, sgst_amount=li.sgst_amount,
            igst_amount=li.igst_amount, line_total=li.line_total,
        )
        # BUG FIX: Decrement stock when converting to invoice
        li.product.stock -= li.quantity
        li.product.save(update_fields=["stock"])

    messages.success(request, f"Invoice {inv_no} created from Quotation {quotation.quotation_number}.")
    return redirect("sales_detail", pk=invoice.pk)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _save_quotation(quotation, company, user, POST):
    customer_id = POST.get("customer")
    q_number    = POST.get("quotation_number", "").strip()
    q_date      = POST.get("quotation_date") or None
    valid_until = POST.get("valid_until") or None
    status      = POST.get("status", "draft")
    notes       = POST.get("notes", "")
    terms       = POST.get("terms", "")

    if not customer_id or not q_number:
        raise ValueError("Customer and Quotation Number are required.")

    customer = get_object_or_404(Customer, pk=customer_id, company=company)

    if quotation is None:
        if Quotation.objects.filter(company=company, quotation_number=q_number).exists():
            raise ValueError(f"Quotation number '{q_number}' already exists.")
        quotation = Quotation(company=company, created_by=user)
    
    quotation.customer         = customer
    quotation.quotation_number = q_number
    quotation.quotation_date   = q_date
    quotation.valid_until      = valid_until
    quotation.status           = status
    quotation.notes            = notes
    quotation.terms            = terms
    quotation.save()

    # Delete old line items and recreate
    quotation.line_items.all().delete()

    products  = POST.getlist("product[]")
    qtys      = POST.getlist("quantity[]")
    prices    = POST.getlist("unit_price[]")
    discounts = POST.getlist("discount[]")

    subtotal = total_cgst = total_sgst = total_igst = Decimal("0")

    for i, pid in enumerate(products):
        if not pid:
            continue
        try:
            prod = Product.objects.select_related("tax").get(pk=pid, company=company)
        except Product.DoesNotExist:
            continue
        is_interstate = (company.state != customer.state) if (company.state and customer.state) else False
        
        cgst_p = prod.tax.cgst_percent if (not is_interstate and prod.tax) else Decimal("0")
        sgst_p = prod.tax.sgst_percent if (not is_interstate and prod.tax) else Decimal("0")
        igst_p = prod.tax.igst_percent if (is_interstate and prod.tax) else Decimal("0")

        li = QuotationLineItem(
            quotation=quotation, product=prod,
            quantity=_decimal(qtys[i] or "0"),
            unit_price=_decimal(prices[i] or "0"),
            discount_percent=_decimal(discounts[i] or "0") if i < len(discounts) else Decimal("0"),
            cgst_percent=cgst_p,
            sgst_percent=sgst_p,
            igst_percent=igst_p,
        )
        li.calculate()
        li.save()
        subtotal   += li.taxable_amount
        total_cgst += li.cgst_amount
        total_sgst += li.sgst_amount
        total_igst += li.igst_amount

    quotation.subtotal    = subtotal
    quotation.total_cgst  = total_cgst
    quotation.total_sgst  = total_sgst
    quotation.total_igst  = total_igst
    quotation.grand_total = subtotal + total_cgst + total_sgst + total_igst
    quotation.save()
    return quotation

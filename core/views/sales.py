"""core/views/sales.py — Sales invoice views."""
from datetime import date
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse
from django.db import transaction

from ..models import Product, SalesInvoice, Customer
from ..forms import SalesInvoiceForm
from ..decorators import permission_required
from ..services import create_sales_invoice
from ..utils import number_to_words, log_action

PAGE_SIZE = 25


@permission_required("can_view_sales")
def sales_list(request):
    q = request.GET.get("q", "")
    # Automatically filtered by middleware/manager
    qs = SalesInvoice.objects.filter(company=request.company).select_related("customer")
    if q:
        qs = qs.filter(
            Q(invoice_number__icontains=q) | Q(customer__name__icontains=q)
        )
    page = Paginator(qs, PAGE_SIZE).get_page(request.GET.get("page"))
    return render(request, "sales/invoice_list.html", {
        "page_obj": page, "invoices": page.object_list, "q": q,
    })


@permission_required("can_edit_sales")
def sales_create(request):
    company = request.company
    # Use filter to ensure we only get items belonging to the current user's company
    products = Product.objects.filter(company=request.company, is_active=True).select_related("tax", "unit")
    customers = Customer.objects.filter(company=request.company)

    if request.method == "POST":
        form = SalesInvoiceForm(request.POST, company=company)
        if form.is_valid():
            try:
                invoice = create_sales_invoice(company, request.user, form, request.POST)
                log_action(request, "create", "SalesInvoice", invoice.invoice_number, f"Total: {invoice.grand_total}")
                messages.success(request, f"Invoice {invoice.invoice_number} created successfully!")
                return redirect("sales_detail", pk=invoice.pk)
            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # Generate next invoice number
        year  = date.today().year
        count = SalesInvoice.objects.filter(company=request.company).count() + 1
        suggested_no = f"INV/{year}/{count:03d}"
        while SalesInvoice.objects.filter(company=request.company, invoice_number=suggested_no).exists():
            count += 1
            suggested_no = f"INV/{year}/{count:03d}"
        form = SalesInvoiceForm(initial={"invoice_number": suggested_no}, company=company)

    return render(request, "sales/invoice_form.html", {
        "form": form, "products": products, "customers": customers,
    })


@permission_required("can_view_sales")
def sales_detail(request, pk):
    invoice = get_object_or_404(SalesInvoice, pk=pk, company=request.company)
    company  = request.company

    # 3 copies
    copies = ["ORIGINAL", "DUPLICATE FOR TRANSPORTER", "TRIPLICATE FOR CONSIGNEE"]

    # Amount in words
    amount_in_words = number_to_words(invoice.grand_total).upper()
    tax_total = (invoice.total_cgst or Decimal("0")) + (invoice.total_sgst or Decimal("0")) + (invoice.total_igst or Decimal("0"))
    tax_in_words = number_to_words(tax_total).upper()

    # WhatsApp share URL
    invoice_url = request.build_absolute_uri(
        reverse("sales_detail", args=[pk])
    )
    wa_text = f"Invoice {invoice.invoice_number} from {company.company_name}\nAmount: ₹{invoice.grand_total}\nDate: {invoice.invoice_date}\nCustomer: {invoice.customer.name}\nView: {invoice_url}"
    import urllib.parse
    whatsapp_url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(wa_text)}"

    return render(request, "sales/invoice_detail.html", {
        "invoice":         invoice,
        "company":         company,
        "copies":          copies,
        "amount_in_words": amount_in_words,
        "tax_in_words":    tax_in_words,
        "tax_total":       tax_total,
        "whatsapp_url":    whatsapp_url,
    })


@permission_required("can_edit_sales")
@transaction.atomic
def sales_cancel(request, pk):
    """Cancel a confirmed invoice (POST only)."""
    if request.method != "POST":
        return redirect("sales_list")
    
    # We use select_for_update to lock the record and prevent race conditions
    invoice = get_object_or_404(
        SalesInvoice.objects.select_for_update(), pk=pk, company=request.company
    )
    
    if invoice.status != "confirmed":
        messages.warning(request, f"Invoice {invoice.invoice_number} cannot be cancelled (Status: {invoice.status}).")
        return redirect("sales_detail", pk=pk)

    # Reverse stock deduction
    for li in invoice.line_items.select_for_update().select_related("product").all():
        li.product.stock += li.quantity
        li.product.save(update_fields=["stock"])
    
    invoice.status = "cancelled"
    invoice.save(update_fields=["status"])
    
    log_action(request, "cancel", "SalesInvoice", invoice.invoice_number)
    messages.success(request, f"Invoice {invoice.invoice_number} cancelled successfully.")
    return redirect("sales_detail", pk=pk)

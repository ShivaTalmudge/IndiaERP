"""
core/services.py
Business logic for creating Sales Invoices and Purchase Orders.
Views call these functions instead of embedding raw logic.
"""
from decimal import Decimal
from django.db import transaction

from .models import (
    Product, SalesInvoice, SalesLineItem,
    PurchaseOrder, PurchaseLineItem,
)


from .utils import _decimal


@transaction.atomic
def create_sales_invoice(company, user, form, post_data):
    """
    Saves a confirmed SalesInvoice with all line items and updates stock.
    Returns the saved SalesInvoice instance.
    Raises ValueError with a user-facing message on validation failure.
    """
    pids   = post_data.getlist("product_id[]")
    qtys   = post_data.getlist("quantity[]")
    prices = post_data.getlist("unit_price[]")
    discs  = post_data.getlist("discount[]")

    valid_rows = [(pid, qty, price, disc)
                  for pid, qty, price, disc in zip(pids, qtys, prices, discs)
                  if pid]
    if not valid_rows:
        raise ValueError("Add at least one product.")

    inv_num = form.cleaned_data["invoice_number"]
    if SalesInvoice.objects.filter(company=company, invoice_number=inv_num).exists():
        raise ValueError(f"Invoice number '{inv_num}' already exists.")

    invoice = form.save(commit=False)
    invoice.company    = company
    invoice.created_by = user
    invoice.status     = "confirmed"
    invoice.save()

    sub = cgst = sgst = igst = Decimal("0")

    for pid, qty, price, disc in valid_rows:
        try:
            prod = Product.objects.select_for_update().get(pk=int(pid), company=company)
        except (Product.DoesNotExist, ValueError):
            continue

        # Decide which taxes to apply based on state
        is_interstate = (company.state != prod.company.state) # This is wrong, should be company vs customer
        # Wait, the invoice is for a customer.
        customer = invoice.customer
        is_interstate = (company.state != customer.state) if (company.state and customer.state) else False
        
        cgst_p = prod.tax.cgst_percent if (not is_interstate and prod.tax) else Decimal("0")
        sgst_p = prod.tax.sgst_percent if (not is_interstate and prod.tax) else Decimal("0")
        igst_p = prod.tax.igst_percent if (is_interstate and prod.tax) else Decimal("0")

        li = SalesLineItem(
            invoice=invoice,
            product=prod,
            quantity=_decimal(qty),
            unit_price=_decimal(price),
            discount_percent=_decimal(disc),
            cgst_percent=cgst_p,
            sgst_percent=sgst_p,
            igst_percent=igst_p,
        )
        li.calculate()
        li.save()

        prod.stock -= _decimal(qty)
        prod.save(update_fields=["stock"])

        sub  += li.taxable_amount
        cgst += li.cgst_amount
        sgst += li.sgst_amount
        igst += li.igst_amount

    invoice.subtotal    = sub
    invoice.total_cgst  = cgst
    invoice.total_sgst  = sgst
    invoice.total_igst  = igst
    invoice.grand_total = sub + cgst + sgst + igst
    invoice.save()
    return invoice


@transaction.atomic
def create_purchase_order(company, user, form, post_data):
    """
    Saves a received PurchaseOrder with all line items and updates stock.
    Returns the saved PurchaseOrder instance.
    Raises ValueError with a user-facing message on validation failure.
    """
    pids   = post_data.getlist("product_id[]")
    qtys   = post_data.getlist("quantity[]")
    prices = post_data.getlist("unit_price[]")

    valid_rows = [(pid, qty, price)
                  for pid, qty, price in zip(pids, qtys, prices)
                  if pid]
    if not valid_rows:
        raise ValueError("Add at least one product.")

    po_num = form.cleaned_data["po_number"]
    if PurchaseOrder.objects.filter(company=company, po_number=po_num).exists():
        raise ValueError(f"PO number '{po_num}' already exists.")

    order = form.save(commit=False)
    order.company    = company
    order.created_by = user
    order.status     = "received"
    order.save()

    sub = cgst = sgst = igst = Decimal("0")

    for pid, qty, price in valid_rows:
        try:
            prod = Product.objects.select_for_update().get(pk=int(pid), company=company)
        except (Product.DoesNotExist, ValueError):
            continue

        supplier = order.supplier
        is_interstate = (company.state != supplier.state) if (company.state and supplier.state) else False

        cgst_p = prod.tax.cgst_percent if (not is_interstate and prod.tax) else Decimal("0")
        sgst_p = prod.tax.sgst_percent if (not is_interstate and prod.tax) else Decimal("0")
        igst_p = prod.tax.igst_percent if (is_interstate and prod.tax) else Decimal("0")

        li = PurchaseLineItem(
            order=order,
            product=prod,
            quantity=_decimal(qty),
            unit_price=_decimal(price),
            cgst_percent=cgst_p,
            sgst_percent=sgst_p,
            igst_percent=igst_p,
        )
        li.calculate()
        li.save()

        prod.stock += _decimal(qty)
        prod.save(update_fields=["stock"])

        sub  += li.taxable_amount
        cgst += li.cgst_amount
        sgst += li.sgst_amount
        igst += li.igst_amount

    order.subtotal    = sub
    order.total_cgst  = cgst
    order.total_sgst  = sgst
    order.total_igst  = igst
    order.grand_total = sub + cgst + sgst + igst
    order.save()
    return order

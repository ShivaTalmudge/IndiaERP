"""core/views/reports.py — All reports: Sales, Purchase, Stock, GSTR-1/2B/3B/7, HSN, TDS/TCS."""
import csv
from decimal import Decimal
from datetime import date

from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum, Count, Q

from ..models import SalesInvoice, SalesLineItem, PurchaseOrder, PurchaseLineItem, Product, HSNCode
from ..decorators import permission_required


def _months():
    return date.today().replace(day=1).isoformat(), date.today().isoformat()


@permission_required("can_view_reports")
def reports_home(request):
    from django.urls import reverse
    general_reports = [
        {"name": "Sales Report",      "icon": "bi-graph-up-arrow", "desc": "Invoice-wise sales with GST", "url": reverse("sales_report")},
        {"name": "Purchase Report",   "icon": "bi-graph-down-arrow","desc": "PO-wise purchase with GST",  "url": reverse("purchase_report")},
        {"name": "Stock Report",      "icon": "bi-boxes",           "desc": "Current inventory levels",   "url": reverse("stock_report")},
        {"name": "Sale by HSN",       "icon": "bi-upc-scan",        "desc": "HSN-wise taxable summary",   "url": reverse("hsn_summary_report")},
    ]
    gst_reports = [
        {"name": "GSTR - 1",  "icon": "bi-file-text", "desc": "Outward supplies (B2B & B2C)", "url": reverse("gstr1_report")},
        {"name": "GSTR - 2B", "icon": "bi-file-text", "desc": "Input Tax Credit statement",   "url": reverse("gstr2b_report")},
        {"name": "GSTR - 3B", "icon": "bi-file-text", "desc": "Monthly GST liability summary","url": reverse("gstr3b_report")},
        {"name": "GSTR - 7",  "icon": "bi-file-text", "desc": "TDS under GST",                "url": reverse("gstr7_report")},
    ]
    tds_reports = [
        {"name": "TDS Receivable", "icon": "bi-arrow-down-circle", "desc": "TDS credit receivable",   "url": reverse("tds_receivable_report")},
        {"name": "TDS Payable",    "icon": "bi-arrow-up-circle",   "desc": "TDS to be deposited",     "url": reverse("tds_payable_report")},
        {"name": "TCS Receivable", "icon": "bi-arrow-down-circle", "desc": "TCS credit receivable",   "url": reverse("tcs_receivable_report")},
        {"name": "TCS Payable",    "icon": "bi-arrow-up-circle",   "desc": "TCS to be deposited",     "url": reverse("tcs_payable_report")},
    ]
    return render(request, "core/reports_home.html", {
        "general_reports": general_reports,
        "gst_reports": gst_reports,
        "tds_reports": tds_reports,
    })


# ── Existing Reports ───────────────────────────────────────────────────────────

@permission_required("can_view_reports")
def sales_report(request):
    company   = request.company
    from_date = request.GET.get("from_date", _months()[0])
    to_date   = request.GET.get("to_date",   _months()[1])
    invoices  = SalesInvoice.objects.filter(
        company=company, status="confirmed",
        invoice_date__gte=from_date, invoice_date__lte=to_date,
    ).select_related("customer").order_by("invoice_date")
    totals = invoices.aggregate(
        total_subtotal=Sum("subtotal"), total_cgst=Sum("total_cgst"),
        total_sgst=Sum("total_sgst"),  total_igst=Sum("total_igst"),
        total_grand=Sum("grand_total"),
    )
    if "export" in request.GET:
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = 'attachment; filename="sales_report.csv"'
        w = csv.writer(resp)
        w.writerow(["Invoice No", "Date", "Customer", "Subtotal", "CGST", "SGST", "IGST", "Grand Total"])
        for inv in invoices:
            w.writerow([inv.invoice_number, inv.invoice_date, inv.customer.name,
                        inv.subtotal, inv.total_cgst, inv.total_sgst, inv.total_igst, inv.grand_total])
        return resp
    return render(request, "core/sales_report.html", {
        "invoices": invoices, "totals": totals,
        "from_date": from_date, "to_date": to_date,
    })


@permission_required("can_view_reports")
def purchase_report(request):
    company   = request.company
    from_date = request.GET.get("from_date", _months()[0])
    to_date   = request.GET.get("to_date",   _months()[1])
    orders    = PurchaseOrder.objects.filter(
        company=company, status="received",
        order_date__gte=from_date, order_date__lte=to_date,
    ).select_related("supplier").order_by("order_date")
    totals = orders.aggregate(
        total_subtotal=Sum("subtotal"), total_cgst=Sum("total_cgst"),
        total_sgst=Sum("total_sgst"),  total_igst=Sum("total_igst"),
        total_grand=Sum("grand_total"),
    )
    if "export" in request.GET:
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = 'attachment; filename="purchase_report.csv"'
        w = csv.writer(resp)
        w.writerow(["PO No", "Date", "Supplier", "Subtotal", "CGST", "SGST", "IGST", "Grand Total"])
        for o in orders:
            w.writerow([o.po_number, o.order_date, o.supplier.name,
                        o.subtotal, o.total_cgst, o.total_sgst, o.total_igst, o.grand_total])
        return resp
    return render(request, "core/purchase_report.html", {
        "orders": orders, "totals": totals,
        "from_date": from_date, "to_date": to_date,
    })


@permission_required("can_view_reports")
def stock_report(request):
    products = Product.objects.filter(
        company=request.company, is_active=True
    ).select_related("category", "unit")
    if "export" in request.GET:
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = 'attachment; filename="stock_report.csv"'
        w = csv.writer(resp)
        w.writerow(["Product", "Category", "Unit", "Price", "Stock", "Reorder Level", "Status"])
        for p in products:
            w.writerow([p.name, p.category.name if p.category else "",
                        p.unit.short_name if p.unit else "",
                        p.price, p.stock, p.reorder_level,
                        "Low Stock" if p.is_low_stock() else "OK"])
        return resp
    return render(request, "core/stock_report.html", {"products": products})


# ── GSTR Reports ──────────────────────────────────────────────────────────────

def _invoice_qs(company, from_date, to_date):
    return SalesInvoice.objects.filter(
        company=company, status="confirmed",
        invoice_date__gte=from_date, invoice_date__lte=to_date,
    ).select_related("customer").prefetch_related("line_items__product__hsn_code")


@permission_required("can_view_reports")
def gstr1_report(request):
    """GSTR-1: Outward supplies — B2B invoice listing by customer GSTIN."""
    company   = request.company
    from_date = request.GET.get("from_date", _months()[0])
    to_date   = request.GET.get("to_date",   _months()[1])
    invoices  = _invoice_qs(company, from_date, to_date).order_by("invoice_date")

    # Separate B2B (customer has GSTIN) and B2C
    b2b = [i for i in invoices if i.customer.gst_number]
    b2c = [i for i in invoices if not i.customer.gst_number]

    totals = invoices.aggregate(
        total_taxable=Sum("subtotal"), total_cgst=Sum("total_cgst"),
        total_sgst=Sum("total_sgst"),  total_igst=Sum("total_igst"),
        total_grand=Sum("grand_total"),
    )

    if "export" in request.GET:
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = 'attachment; filename="GSTR1_report.csv"'
        w = csv.writer(resp)
        w.writerow(["Type", "Invoice No", "Date", "GSTIN/UIN", "Customer", "Taxable Value",
                    "CGST", "SGST", "IGST", "Invoice Value"])
        for inv in invoices:
            w.writerow([
                "B2B" if inv.customer.gst_number else "B2C",
                inv.invoice_number, inv.invoice_date,
                inv.customer.gst_number or "Consumer",
                inv.customer.name, inv.subtotal,
                inv.total_cgst, inv.total_sgst, inv.total_igst, inv.grand_total,
            ])
        return resp

    return render(request, "core/gstr1_report.html", {
        "b2b": b2b, "b2c": b2c, "totals": totals,
        "from_date": from_date, "to_date": to_date,
        "all_invoices": invoices,
    })


@permission_required("can_view_reports")
def gstr2b_report(request):
    """GSTR-2B: Input Tax Credit from purchases."""
    company   = request.company
    from_date = request.GET.get("from_date", _months()[0])
    to_date   = request.GET.get("to_date",   _months()[1])
    orders    = PurchaseOrder.objects.filter(
        company=company, status="received",
        order_date__gte=from_date, order_date__lte=to_date,
    ).select_related("supplier").order_by("order_date")
    totals = orders.aggregate(
        total_taxable=Sum("subtotal"), total_cgst=Sum("total_cgst"),
        total_sgst=Sum("total_sgst"),  total_igst=Sum("total_igst"),
        total_itc=Sum("grand_total"),
    )
    if "export" in request.GET:
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = 'attachment; filename="GSTR2B_report.csv"'
        w = csv.writer(resp)
        w.writerow(["PO No", "Date", "Supplier GSTIN", "Supplier", "Taxable Value",
                    "CGST", "SGST", "IGST", "Total ITC"])
        for o in orders:
            w.writerow([o.po_number, o.order_date,
                        o.supplier.gst_number or "—", o.supplier.name,
                        o.subtotal, o.total_cgst, o.total_sgst, o.total_igst, o.grand_total])
        return resp
    return render(request, "core/gstr2b_report.html", {
        "orders": orders, "totals": totals,
        "from_date": from_date, "to_date": to_date,
    })


@permission_required("can_view_reports")
def gstr3b_report(request):
    """GSTR-3B: Monthly summary of GST liabilities and ITC."""
    company   = request.company
    from_date = request.GET.get("from_date", _months()[0])
    to_date   = request.GET.get("to_date",   _months()[1])

    # Outward supplies
    sales = SalesInvoice.objects.filter(
        company=company, status="confirmed",
        invoice_date__gte=from_date, invoice_date__lte=to_date,
    ).aggregate(
        taxable=Sum("subtotal") or Decimal("0"),
        cgst=Sum("total_cgst") or Decimal("0"),
        sgst=Sum("total_sgst") or Decimal("0"),
        igst=Sum("total_igst") or Decimal("0"),
        total=Sum("grand_total") or Decimal("0"),
    )

    # ITC from purchases
    purchases = PurchaseOrder.objects.filter(
        company=company, status="received",
        order_date__gte=from_date, order_date__lte=to_date,
    ).aggregate(
        taxable=Sum("subtotal") or Decimal("0"),
        cgst=Sum("total_cgst") or Decimal("0"),
        sgst=Sum("total_sgst") or Decimal("0"),
        igst=Sum("total_igst") or Decimal("0"),
    )

    s_cgst  = sales["cgst"]  or Decimal("0")
    s_sgst  = sales["sgst"]  or Decimal("0")
    s_igst  = sales["igst"]  or Decimal("0")
    p_cgst  = purchases["cgst"] or Decimal("0")
    p_sgst  = purchases["sgst"] or Decimal("0")
    p_igst  = purchases["igst"] or Decimal("0")

    net_cgst = s_cgst - p_cgst
    net_sgst = s_sgst - p_sgst
    net_igst = s_igst - p_igst

    return render(request, "core/gstr3b_report.html", {
        "sales": sales, "purchases": purchases,
        "net_cgst": net_cgst, "net_sgst": net_sgst, "net_igst": net_igst,
        "net_total": net_cgst + net_sgst + net_igst,
        "from_date": from_date, "to_date": to_date,
    })


@permission_required("can_view_reports")
def gstr7_report(request):
    """GSTR-7: TDS deducted (placeholder — requires TDS configuration)."""
    company   = request.company
    from_date = request.GET.get("from_date", _months()[0])
    to_date   = request.GET.get("to_date",   _months()[1])
    return render(request, "core/gstr7_report.html", {
        "from_date": from_date, "to_date": to_date,
    })


@permission_required("can_view_reports")
def hsn_summary_report(request):
    """Sales Summary by HSN — Groups outward supply line items by HSN code."""
    company   = request.company
    from_date = request.GET.get("from_date", _months()[0])
    to_date   = request.GET.get("to_date",   _months()[1])

    line_items = SalesLineItem.objects.filter(
        invoice__company=company,
        invoice__status="confirmed",
        invoice__invoice_date__gte=from_date,
        invoice__invoice_date__lte=to_date,
    ).select_related("product__hsn_code")

    # Aggregate by HSN
    from collections import defaultdict
    hsn_data = defaultdict(lambda: {"qty": Decimal("0"), "taxable": Decimal("0"),
                                    "cgst": Decimal("0"), "sgst": Decimal("0"),
                                    "igst": Decimal("0"), "total": Decimal("0")})
    for li in line_items:
        code = li.product.hsn_code.code if li.product.hsn_code else "N/A"
        hsn_data[code]["qty"]     += li.quantity
        hsn_data[code]["taxable"] += li.taxable_amount
        hsn_data[code]["cgst"]    += li.cgst_amount
        hsn_data[code]["sgst"]    += li.sgst_amount
        hsn_data[code]["igst"]    += li.igst_amount
        hsn_data[code]["total"]   += li.line_total

    rows = [{"hsn": k, **v} for k, v in sorted(hsn_data.items())]

    if "export" in request.GET:
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = 'attachment; filename="HSN_Summary.csv"'
        w = csv.writer(resp)
        w.writerow(["HSN/SAC", "Qty", "Taxable Value", "CGST", "SGST", "IGST", "Total"])
        for r in rows:
            w.writerow([r["hsn"], r["qty"], r["taxable"],
                        r["cgst"], r["sgst"], r["igst"], r["total"]])
        return resp

    return render(request, "core/hsn_summary_report.html", {
        "rows": rows, "from_date": from_date, "to_date": to_date,
    })


@permission_required("can_view_reports")
def tds_receivable_report(request):
    """TDS Receivable — placeholder (requires TDS fields on invoices)."""
    from_date = request.GET.get("from_date", _months()[0])
    to_date   = request.GET.get("to_date",   _months()[1])
    return render(request, "core/tds_report.html", {
        "report_type": "TDS Receivable",
        "from_date": from_date, "to_date": to_date,
    })


@permission_required("can_view_reports")
def tds_payable_report(request):
    """TDS Payable — placeholder."""
    from_date = request.GET.get("from_date", _months()[0])
    to_date   = request.GET.get("to_date",   _months()[1])
    return render(request, "core/tds_report.html", {
        "report_type": "TDS Payable",
        "from_date": from_date, "to_date": to_date,
    })


@permission_required("can_view_reports")
def tcs_receivable_report(request):
    """TCS Receivable — placeholder."""
    from_date = request.GET.get("from_date", _months()[0])
    to_date   = request.GET.get("to_date",   _months()[1])
    return render(request, "core/tds_report.html", {
        "report_type": "TCS Receivable",
        "from_date": from_date, "to_date": to_date,
    })


@permission_required("can_view_reports")
def tcs_payable_report(request):
    """TCS Payable — placeholder."""
    from_date = request.GET.get("from_date", _months()[0])
    to_date   = request.GET.get("to_date",   _months()[1])
    return render(request, "core/tds_report.html", {
        "report_type": "TCS Payable",
        "from_date": from_date, "to_date": to_date,
    })

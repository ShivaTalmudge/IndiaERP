"""core/views/eway.py — E-Way Bill generation and management."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django import forms

from ..models import SalesInvoice, EWayBill
from ..decorators import permission_required

PAGE_SIZE = 25
fc = {'class': 'form-control'}


class EWayBillForm(forms.ModelForm):
    class Meta:
        model = EWayBill
        fields = [
            'eway_bill_number', 'generated_date', 'valid_upto',
            'transporter_name', 'transporter_id', 'vehicle_number',
            'distance_km', 'supply_type', 'notes',
        ]
        widgets = {
            'eway_bill_number': forms.TextInput(attrs=fc),
            'generated_date':   forms.DateInput(attrs={**fc, 'type': 'date'}),
            'valid_upto':       forms.DateInput(attrs={**fc, 'type': 'date'}),
            'transporter_name': forms.TextInput(attrs=fc),
            'transporter_id':   forms.TextInput(attrs=fc),
            'vehicle_number':   forms.TextInput(attrs=fc),
            'distance_km':      forms.NumberInput(attrs=fc),
            'supply_type':      forms.TextInput(attrs=fc),
            'notes':            forms.Textarea(attrs={**fc, 'rows': 3}),
        }


@permission_required("can_view_sales")
def eway_list(request):
    qs   = EWayBill.objects.filter(company=request.company).select_related("invoice")
    page = Paginator(qs, PAGE_SIZE).get_page(request.GET.get("page"))
    return render(request, "sales/eway_list.html", {"page_obj": page, "eways": page.object_list})


@permission_required("can_edit_sales")
def eway_create(request, invoice_pk):
    """Generate an E-Way Bill for an invoice."""
    invoice = get_object_or_404(SalesInvoice, pk=invoice_pk, company=request.company)

    # Check if already exists
    if hasattr(invoice, 'eway_bill'):
        messages.warning(request, "E-Way Bill already exists for this invoice.")
        return redirect("eway_detail", pk=invoice.eway_bill.pk)

    if request.method == "POST":
        form = EWayBillForm(request.POST)
        if form.is_valid():
            eway = form.save(commit=False)
            eway.company    = request.company
            eway.invoice    = invoice
            eway.created_by = request.user
            eway.save()
            messages.success(request, f"E-Way Bill {eway.eway_bill_number} generated.")
            return redirect("eway_detail", pk=eway.pk)
    else:
        form = EWayBillForm(initial={'supply_type': 'Outward'})

    return render(request, "sales/eway_form.html", {"form": form, "invoice": invoice})


@permission_required("can_view_sales")
def eway_detail(request, pk):
    eway = get_object_or_404(EWayBill, pk=pk, company=request.company)
    return render(request, "sales/eway_detail.html", {"eway": eway})


@permission_required("can_edit_sales")
def eway_cancel(request, pk):
    if request.method != "POST":
        return redirect("eway_list")
    eway = get_object_or_404(EWayBill, pk=pk, company=request.company)
    eway.status = 'cancelled'
    eway.save(update_fields=['status'])
    messages.success(request, f"E-Way Bill {eway.eway_bill_number} cancelled.")
    return redirect("eway_detail", pk=pk)

@permission_required("can_view_sales")
def eway_print_view(request, pk):
    eway = get_object_or_404(EWayBill, pk=pk, company=request.company)
    # Get total value of goods, assume invoice exists
    total_val = eway.invoice.grand_total if eway.invoice else 0
    hsn_code = ""
    if eway.invoice and eway.invoice.line_items.exists():
        first_line = eway.invoice.line_items.first()
        if first_line.product and first_line.product.hsn_code:
            hsn_code = first_line.product.hsn_code.code

    context = {
        'eway': eway,
        'company': request.company,
        'total_value': total_val,
        'hsn_code': hsn_code,
    }
    return render(request, "sales/eway_print.html", context)


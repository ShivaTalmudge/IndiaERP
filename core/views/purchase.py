"""core/views/purchase.py — Purchase order views."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction

from ..models import Product, PurchaseOrder, Supplier
from ..forms import PurchaseOrderForm
from ..decorators import permission_required
from ..services import create_purchase_order
from ..utils import log_action

PAGE_SIZE = 25


@permission_required("can_view_purchase")
def purchase_list(request):
    q = request.GET.get("q", "")
    qs = PurchaseOrder.objects.filter(company=request.company).select_related("supplier")
    if q:
        qs = qs.filter(Q(po_number__icontains=q) | Q(supplier__name__icontains=q))
    page = Paginator(qs, PAGE_SIZE).get_page(request.GET.get("page"))
    return render(request, "purchase/purchase_list.html", {"page_obj": page, "orders": page.object_list, "q": q})


@permission_required("can_edit_purchase")
def purchase_create(request):
    company  = request.company
    products = Product.objects.filter(company=company, is_active=True).select_related("tax", "unit")
    suppliers = Supplier.objects.filter(company=company)

    if request.method == "POST":
        form = PurchaseOrderForm(request.POST, company=company)
        if form.is_valid():
            try:
                order = create_purchase_order(company, request.user, form, request.POST)
                log_action(request, "create", "PurchaseOrder", order.po_number, f"Total: {order.grand_total}")
                messages.success(request, f"Purchase Order {order.po_number} created.")
                return redirect("purchase_detail", pk=order.pk)
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = PurchaseOrderForm(company=company)
    
    return render(request, "purchase/purchase_form.html", {
        "form": form, "products": products, "suppliers": suppliers,
    })


@permission_required("can_view_purchase")
def purchase_detail(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk, company=request.company)
    return render(request, "purchase/purchase_detail.html", {"order": order, "company": request.company})


@permission_required("can_edit_purchase")
@transaction.atomic
def purchase_cancel(request, pk):
    """Cancel a PO — reverse stock (POST only)."""
    if request.method != "POST":
        return redirect("purchase_list")
    order = get_object_or_404(PurchaseOrder, pk=pk, company=request.company, status="received")
    
    # Select for update products
    for li in order.line_items.select_for_update().select_related("product").all():
        li.product.stock -= li.quantity
        li.product.save(update_fields=["stock"])
    
    order.status = "cancelled"
    order.save()
    
    log_action(request, "cancel", "PurchaseOrder", order.po_number)
    messages.success(request, f"Purchase Order {order.po_number} cancelled.")
    return redirect("purchase_detail", pk=pk)

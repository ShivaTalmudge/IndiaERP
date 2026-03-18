"""core/views/masters.py — CRUD for all master data + product AJAX."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator

from ..models import (
    ProductCategory, UnitMaster, HSNCode, TaxMaster,
    Supplier, Customer, Product,
)
from ..forms import (
    ProductCategoryForm, UnitMasterForm, HSNCodeForm, TaxMasterForm,
    SupplierForm, CustomerForm, ProductForm,
)
from ..decorators import permission_required, login_required_custom

PAGE_SIZE = 25


# ── Generic helpers ───────────────────────────────────────────────────────────

def _list(request, model, tpl, search_field="name"):
    q = request.GET.get("q", "")
    qs = model.objects.filter(company=request.company)
    if q:
        qs = qs.filter(**{f"{search_field}__icontains": q})
    page = Paginator(qs, PAGE_SIZE).get_page(request.GET.get("page"))
    return render(request, tpl, {"page_obj": page, "objects": page.object_list, "q": q})


def _add(request, FormClass, tpl, redir):
    company = request.company
    form = FormClass()
    if request.method == "POST":
        form = FormClass(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.company = company
            obj.save()
            messages.success(request, "Added successfully.")
            return redirect(redir)
    return render(request, tpl, {"form": form, "action": "Add"})


def _edit(request, model, FormClass, tpl, redir, pk):
    obj = get_object_or_404(model, company=request.company, pk=pk)
    form = FormClass(instance=obj)
    if request.method == "POST":
        form = FormClass(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated.")
            return redirect(redir)
    return render(request, tpl, {"form": form, "action": "Edit", "object": obj})


def _delete(request, model, redir, pk):
    obj = get_object_or_404(model, company=request.company, pk=pk)
    if request.method == "POST":
        try:
            obj.delete()
            messages.success(request, "Deleted.")
        except Exception:
            messages.error(request, "Cannot delete — record is in use.")
    return redirect(redir)


# ── Category ──────────────────────────────────────────────────────────────────
@permission_required("can_view_masters")
def category_list(request):
    return _list(request, ProductCategory, "masters/category_list.html")

@permission_required("can_edit_masters")
def category_add(request):
    return _add(request, ProductCategoryForm, "masters/category_form.html", "category_list")

@permission_required("can_edit_masters")
def category_edit(request, pk):
    return _edit(request, ProductCategory, ProductCategoryForm, "masters/category_form.html", "category_list", pk)

@permission_required("can_edit_masters")
def category_delete(request, pk):
    return _delete(request, ProductCategory, "category_list", pk)


# ── Unit ──────────────────────────────────────────────────────────────────────
@permission_required("can_view_masters")
def unit_list(request):
    return _list(request, UnitMaster, "masters/unit_list.html")

@permission_required("can_edit_masters")
def unit_add(request):
    return _add(request, UnitMasterForm, "masters/unit_form.html", "unit_list")

@permission_required("can_edit_masters")
def unit_edit(request, pk):
    return _edit(request, UnitMaster, UnitMasterForm, "masters/unit_form.html", "unit_list", pk)

@permission_required("can_edit_masters")
def unit_delete(request, pk):
    return _delete(request, UnitMaster, "unit_list", pk)


# ── HSN ───────────────────────────────────────────────────────────────────────
@permission_required("can_view_masters")
def hsn_list(request):
    return _list(request, HSNCode, "masters/hsn_list.html", search_field="code")

@permission_required("can_edit_masters")
def hsn_add(request):
    return _add(request, HSNCodeForm, "masters/hsn_form.html", "hsn_list")

@permission_required("can_edit_masters")
def hsn_edit(request, pk):
    return _edit(request, HSNCode, HSNCodeForm, "masters/hsn_form.html", "hsn_list", pk)

@permission_required("can_edit_masters")
def hsn_delete(request, pk):
    return _delete(request, HSNCode, "hsn_list", pk)


# ── Tax ───────────────────────────────────────────────────────────────────────
@permission_required("can_view_masters")
def tax_list(request):
    return _list(request, TaxMaster, "masters/tax_list.html")

@permission_required("can_edit_masters")
def tax_add(request):
    return _add(request, TaxMasterForm, "masters/tax_form.html", "tax_list")

@permission_required("can_edit_masters")
def tax_edit(request, pk):
    return _edit(request, TaxMaster, TaxMasterForm, "masters/tax_form.html", "tax_list", pk)

@permission_required("can_edit_masters")
def tax_delete(request, pk):
    return _delete(request, TaxMaster, "tax_list", pk)


# ── Supplier ──────────────────────────────────────────────────────────────────
@permission_required("can_view_masters")
def supplier_list(request):
    return _list(request, Supplier, "masters/supplier_list.html")

@permission_required("can_edit_masters")
def supplier_add(request):
    return _add(request, SupplierForm, "masters/supplier_form.html", "supplier_list")

@permission_required("can_edit_masters")
def supplier_edit(request, pk):
    return _edit(request, Supplier, SupplierForm, "masters/supplier_form.html", "supplier_list", pk)

@permission_required("can_edit_masters")
def supplier_delete(request, pk):
    return _delete(request, Supplier, "supplier_list", pk)


# ── Customer ──────────────────────────────────────────────────────────────────
@permission_required("can_view_masters")
def customer_list(request):
    return _list(request, Customer, "masters/customer_list.html")

@permission_required("can_edit_masters")
def customer_add(request):
    return _add(request, CustomerForm, "masters/customer_form.html", "customer_list")

@permission_required("can_edit_masters")
def customer_edit(request, pk):
    return _edit(request, Customer, CustomerForm, "masters/customer_form.html", "customer_list", pk)

@permission_required("can_edit_masters")
def customer_delete(request, pk):
    return _delete(request, Customer, "customer_list", pk)


# ── Product ───────────────────────────────────────────────────────────────────
@permission_required("can_view_masters")
def product_list(request):
    q = request.GET.get("q", "")
    qs = Product.objects.filter(company=request.company).select_related("category", "unit", "tax")
    if q:
        qs = qs.filter(name__icontains=q)
    page = Paginator(qs, PAGE_SIZE).get_page(request.GET.get("page"))
    return render(request, "masters/product_list.html", {
        "page_obj": page, "objects": page.object_list, "q": q,
    })

@permission_required("can_edit_masters")
def product_add(request):
    form = ProductForm(company=request.company)
    if request.method == "POST":
        form = ProductForm(request.POST, company=request.company)
        if form.is_valid():
            p = form.save(commit=False)
            p.company = request.company
            p.save()
            messages.success(request, f"Product '{p.name}' added.")
            return redirect("product_list")
    return render(request, "masters/product_form.html", {"form": form, "action": "Add"})

@permission_required("can_edit_masters")
def product_edit(request, pk):
    product = get_object_or_404(Product, company=request.company, pk=pk)
    form = ProductForm(instance=product, company=request.company)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product, company=request.company)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated.")
            return redirect("product_list")
    return render(request, "masters/product_form.html", {"form": form, "action": "Edit", "object": product})

@permission_required("can_edit_masters")
def product_delete(request, pk):
    return _delete(request, Product, "product_list", pk)


# ── AJAX ──────────────────────────────────────────────────────────────────────
@login_required_custom
def product_info(request, pk):
    try:
        p = Product.objects.select_related("tax", "unit").get(company=request.company, pk=pk)
        return JsonResponse({
            "price": float(p.price),
            "cgst":  float(p.tax.cgst_percent) if p.tax else 0,
            "sgst":  float(p.tax.sgst_percent) if p.tax else 0,
            "igst":  float(p.tax.igst_percent) if p.tax else 0,
            "unit":  p.unit.short_name if p.unit else "",
            "stock": float(p.stock),
        })
    except Product.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

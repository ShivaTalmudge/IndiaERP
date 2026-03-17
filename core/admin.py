from django.contrib import admin
from .models import (
    Company, UserProfile,
    ProductCategory, UnitMaster, HSNCode, TaxMaster,
    Supplier, Customer, Product,
    SalesInvoice, SalesLineItem,
    PurchaseOrder, PurchaseLineItem,
)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display  = ['company_name', 'state', 'contact_email', 'is_active', 'license_end_date', 'created_at']
    list_filter   = ['is_active']
    search_fields = ['company_name', 'contact_email', 'gst_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'company', 'role', 'is_active']
    list_filter   = ['role', 'is_active']
    search_fields = ['user__username', 'company__company_name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ['name', 'company', 'category', 'price', 'stock', 'reorder_level', 'is_active']
    list_filter   = ['company', 'is_active', 'category']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display  = ['name', 'company', 'city', 'state', 'phone']
    search_fields = ['name', 'email', 'phone']
    list_filter   = ['company']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display  = ['name', 'company', 'city', 'state', 'phone']
    search_fields = ['name', 'email', 'phone']
    list_filter   = ['company']


class SalesLineItemInline(admin.TabularInline):
    model = SalesLineItem
    extra = 0
    readonly_fields = ['taxable_amount', 'cgst_amount', 'sgst_amount', 'igst_amount', 'line_total']


@admin.register(SalesInvoice)
class SalesInvoiceAdmin(admin.ModelAdmin):
    list_display   = ['invoice_number', 'company', 'customer', 'invoice_date', 'grand_total', 'status', 'payment_status']
    list_filter    = ['status', 'payment_status', 'company']
    search_fields  = ['invoice_number', 'customer__name']
    readonly_fields = ['created_at', 'updated_at', 'subtotal', 'total_cgst', 'total_sgst', 'total_igst', 'grand_total']
    inlines        = [SalesLineItemInline]


class PurchaseLineItemInline(admin.TabularInline):
    model = PurchaseLineItem
    extra = 0
    readonly_fields = ['taxable_amount', 'cgst_amount', 'sgst_amount', 'igst_amount', 'line_total']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display   = ['po_number', 'company', 'supplier', 'order_date', 'grand_total', 'status']
    list_filter    = ['status', 'company']
    search_fields  = ['po_number', 'supplier__name']
    readonly_fields = ['created_at', 'updated_at', 'subtotal', 'total_cgst', 'total_sgst', 'total_igst', 'grand_total']
    inlines        = [PurchaseLineItemInline]


# Simple registrations
admin.site.register(ProductCategory)
admin.site.register(UnitMaster)
admin.site.register(HSNCode)
admin.site.register(TaxMaster)

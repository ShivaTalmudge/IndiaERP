from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Company, UserProfile, ProductCategory, UnitMaster, HSNCode,
    TaxMaster, Supplier, Customer, Product, SalesInvoice, PurchaseOrder
)

fc = {'class': 'form-control'}
fs = {'class': 'form-select'}


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={**fc, 'placeholder': 'Username', 'autofocus': True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={**fc, 'placeholder': 'Password'})
    )


# ── Shared Company widget config ──────────────────────────────────────────────
_COMPANY_WIDGETS = {
    'company_name':          forms.TextInput(attrs=fc),
    'gst_number':            forms.TextInput(attrs=fc),
    'pan_number':            forms.TextInput(attrs=fc),
    'address':               forms.Textarea(attrs={**fc, 'rows': 3}),
    'contact_email':         forms.EmailInput(attrs=fc),
    'contact_phone':         forms.TextInput(attrs=fc),
    'logo':                  forms.ClearableFileInput(attrs={'class': 'form-control'}),
    'bank_name':             forms.TextInput(attrs=fc),
    'account_number':        forms.TextInput(attrs=fc),
    'ifsc_code':             forms.TextInput(attrs=fc),
    'bank_branch':           forms.TextInput(attrs=fc),
    'authorized_signatory':  forms.TextInput(attrs=fc),
    'declaration':           forms.Textarea(attrs={**fc, 'rows': 3}),
    'payment_terms':         forms.TextInput(attrs=fc),
    'city':                  forms.TextInput(attrs=fc),
    'state':                 forms.Select(attrs=fs),
    'pincode':               forms.TextInput(attrs=fc),
    'license_start_date':    forms.DateInput(attrs={**fc, 'type': 'date'}),
    'license_end_date':      forms.DateInput(attrs={**fc, 'type': 'date'}),
}

_COMPANY_FIELDS = [
    'company_name', 'gst_number', 'pan_number', 'address', 'city', 'state', 'pincode',
    'contact_email', 'contact_phone',
    'logo',
    'bank_name', 'account_number', 'ifsc_code', 'bank_branch',
    'authorized_signatory', 'declaration', 'payment_terms',
    'license_start_date', 'license_end_date', 'is_active',
]


class CompanyBaseForm(forms.ModelForm):
    """Shared base for Company add/edit."""
    class Meta:
        model   = Company
        fields  = _COMPANY_FIELDS
        widgets = _COMPANY_WIDGETS


from django.contrib.auth.password_validation import validate_password


class CompanyForm(CompanyBaseForm):
    """Company creation — also creates the first admin user."""
    admin_username = forms.CharField(max_length=150, widget=forms.TextInput(attrs=fc))
    admin_password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs=fc),
        help_text='Minimum 8 characters.',
    )
    admin_email = forms.EmailField(required=False, widget=forms.EmailInput(attrs=fc))

    def clean_admin_password(self):
        password = self.cleaned_data.get("admin_password")
        if password:
            validate_password(password)
        return password


class CompanyEditForm(CompanyBaseForm):
    """Company editing — no admin user fields."""
    pass


class StaffForm(forms.ModelForm):
    username   = forms.CharField(max_length=150, widget=forms.TextInput(attrs=fc))
    password   = forms.CharField(
        required=False,
        min_length=8,
        widget=forms.PasswordInput(attrs={**fc, 'placeholder': 'Leave blank to keep existing'}),
        help_text='Minimum 8 characters.',
    )
    email      = forms.EmailField(required=False, widget=forms.EmailInput(attrs=fc))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs=fc))
    last_name  = forms.CharField(required=False, widget=forms.TextInput(attrs=fc))

    class Meta:
        model  = UserProfile
        fields = [
            'phone', 'is_active',
            'can_view_sales', 'can_edit_sales',
            'can_view_purchase', 'can_edit_purchase',
            'can_view_masters', 'can_edit_masters',
            'can_view_reports',
        ]
        widgets = {'phone': forms.TextInput(attrs=fc)}

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
            validate_password(password)
        return password



class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model   = ProductCategory
        fields  = ['name', 'description']
        widgets = {
            'name':        forms.TextInput(attrs=fc),
            'description': forms.Textarea(attrs={**fc, 'rows': 3}),
        }


class UnitMasterForm(forms.ModelForm):
    class Meta:
        model   = UnitMaster
        fields  = ['name', 'short_name']
        widgets = {
            'name':       forms.TextInput(attrs=fc),
            'short_name': forms.TextInput(attrs=fc),
        }


class HSNCodeForm(forms.ModelForm):
    class Meta:
        model   = HSNCode
        fields  = ['code', 'description']
        widgets = {
            'code':        forms.TextInput(attrs=fc),
            'description': forms.Textarea(attrs={**fc, 'rows': 3}),
        }


class TaxMasterForm(forms.ModelForm):
    class Meta:
        model   = TaxMaster
        fields  = ['name', 'cgst_percent', 'sgst_percent', 'igst_percent']
        widgets = {
            'name':         forms.TextInput(attrs=fc),
            'cgst_percent': forms.NumberInput(attrs={**fc, 'step': '0.01'}),
            'sgst_percent': forms.NumberInput(attrs={**fc, 'step': '0.01'}),
            'igst_percent': forms.NumberInput(attrs={**fc, 'step': '0.01'}),
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model   = Supplier
        fields  = ['name', 'gst_number', 'address', 'city', 'state', 'pincode', 'contact_person', 'phone', 'email']
        widgets = {
            'name':           forms.TextInput(attrs=fc),
            'gst_number':     forms.TextInput(attrs=fc),
            'address':        forms.Textarea(attrs={**fc, 'rows': 3}),
            'city':           forms.TextInput(attrs=fc),
            'state':          forms.Select(attrs=fs),
            'pincode':        forms.TextInput(attrs=fc),
            'contact_person': forms.TextInput(attrs=fc),
            'phone':          forms.TextInput(attrs=fc),
            'email':          forms.EmailInput(attrs=fc),
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model   = Customer
        fields  = ['name', 'gst_number', 'address', 'city', 'state', 'pincode', 'contact_person', 'phone', 'email']
        widgets = {
            'name':           forms.TextInput(attrs=fc),
            'gst_number':     forms.TextInput(attrs=fc),
            'address':        forms.Textarea(attrs={**fc, 'rows': 3}),
            'city':           forms.TextInput(attrs=fc),
            'state':          forms.Select(attrs=fs),
            'pincode':        forms.TextInput(attrs=fc),
            'contact_person': forms.TextInput(attrs=fc),
            'phone':          forms.TextInput(attrs=fc),
            'email':          forms.EmailInput(attrs=fc),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model   = Product
        fields  = ['name', 'category', 'hsn_code', 'unit', 'tax', 'price', 'stock', 'reorder_level', 'is_active']
        widgets = {
            'name':          forms.TextInput(attrs=fc),
            'price':         forms.NumberInput(attrs={**fc, 'step': '0.01'}),
            'stock':         forms.NumberInput(attrs={**fc, 'step': '0.001'}),
            'reorder_level': forms.NumberInput(attrs={**fc, 'step': '0.001'}),
            'category':      forms.Select(attrs=fs),
            'hsn_code':      forms.Select(attrs=fs),
            'unit':          forms.Select(attrs=fs),
            'tax':           forms.Select(attrs=fs),
        }

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        if company:
            self.fields['category'].queryset = ProductCategory.objects.filter(company=company)
            self.fields['hsn_code'].queryset  = HSNCode.objects.filter(company=company)
            self.fields['unit'].queryset      = UnitMaster.objects.filter(company=company)
            self.fields['tax'].queryset       = TaxMaster.objects.filter(company=company)


class SalesInvoiceForm(forms.ModelForm):
    class Meta:
        model   = SalesInvoice
        fields  = ['invoice_number', 'customer', 'invoice_date', 'due_date', 'notes']
        widgets = {
            'invoice_number': forms.TextInput(attrs=fc),
            'customer':       forms.Select(attrs=fs),
            'invoice_date':   forms.DateInput(attrs={**fc, 'type': 'date'}),
            'due_date':       forms.DateInput(attrs={**fc, 'type': 'date'}),
            'notes':          forms.Textarea(attrs={**fc, 'rows': 2}),
        }

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        if company:
            self.fields['customer'].queryset = Customer.objects.filter(company=company)


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model   = PurchaseOrder
        fields  = ['po_number', 'supplier', 'order_date', 'notes']
        widgets = {
            'po_number':  forms.TextInput(attrs=fc),
            'supplier':   forms.Select(attrs=fs),
            'order_date': forms.DateInput(attrs={**fc, 'type': 'date'}),
            'notes':      forms.Textarea(attrs={**fc, 'rows': 2}),
        }

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        if company:
            self.fields['supplier'].queryset = Supplier.objects.filter(company=company)

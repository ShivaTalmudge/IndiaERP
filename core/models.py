from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from .constants import STATE_CHOICES


class CompanyManager(models.Manager):
    """
    Manager to automatically filter querysets by the current user's company.
    Usage: Model.objects.for_user(request.user).all()
    """
    def for_user(self, user):
        if not user or not user.is_authenticated:
            return self.get_queryset().none()
        try:
            profile = user.profile
            if profile.role == 'superadmin':
                return self.get_queryset()
            return self.get_queryset().filter(company=profile.company)
        except Exception:
            return self.get_queryset().none()


class CompanyAwareModel(models.Model):
    """
    Abstract base model that provides a company field and a custom manager.
    """
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    objects = CompanyManager()

    class Meta:
        abstract = True


class Company(models.Model):
    company_name         = models.CharField(max_length=200)
    gst_number           = models.CharField(max_length=20, blank=True)
    pan_number           = models.CharField(max_length=20, blank=True)
    address              = models.TextField(blank=True)
    contact_email        = models.EmailField(unique=True)
    contact_phone        = models.CharField(max_length=15, blank=True)
    city                 = models.CharField(max_length=100, blank=True)
    state                = models.CharField(max_length=100, choices=STATE_CHOICES, blank=True)
    pincode              = models.CharField(max_length=10, blank=True)
    logo                 = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    # Bank details for invoice
    bank_name            = models.CharField(max_length=100, blank=True)
    account_number       = models.CharField(max_length=30, blank=True)
    ifsc_code            = models.CharField(max_length=20, blank=True)
    bank_branch          = models.CharField(max_length=100, blank=True)
    authorized_signatory = models.CharField(max_length=100, blank=True)
    declaration          = models.TextField(blank=True, default=(
        "Goods once sold will not be taken back or exchange.\n"
        "We declare that this invoice shows the actual price of\n"
        "the goods described and that all particulars are true and\n"
        "correct."
    ))
    payment_terms        = models.CharField(max_length=200, blank=True)
    license_start_date   = models.DateField()
    license_end_date     = models.DateField()
    is_active            = models.BooleanField(default=True)
    created_at           = models.DateTimeField(auto_now_add=True)
    updated_at           = models.DateTimeField(auto_now=True)

    def is_license_valid(self):
        return self.is_active and self.license_end_date >= timezone.now().date()

    def __str__(self):
        return self.company_name

    class Meta:
        ordering = ['company_name']
        verbose_name_plural = 'Companies'


class UserProfile(models.Model):
    ROLE_CHOICES = [('superadmin', 'Super Admin'), ('admin', 'Admin'), ('staff', 'Staff')]
    user              = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company           = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    role              = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    phone             = models.CharField(max_length=15, blank=True)
    is_active         = models.BooleanField(default=True)
    can_view_sales    = models.BooleanField(default=False)
    can_edit_sales    = models.BooleanField(default=False)
    can_view_purchase = models.BooleanField(default=False)
    can_edit_purchase = models.BooleanField(default=False)
    can_view_masters  = models.BooleanField(default=False)
    can_edit_masters  = models.BooleanField(default=False)
    can_view_reports  = models.BooleanField(default=False)
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    def is_superadmin(self):
        return self.role == 'superadmin'

    def is_owner(self):
        return self.role == 'admin'

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class ProductCategory(CompanyAwareModel):
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('company', 'name')
        ordering = ['name']

    def __str__(self):
        return self.name


class UnitMaster(CompanyAwareModel):
    name       = models.CharField(max_length=50)
    short_name = models.CharField(max_length=10)

    class Meta:
        unique_together = ('company', 'name')
        ordering = ['name']

    def __str__(self):
        return self.short_name


class HSNCode(CompanyAwareModel):
    code        = models.CharField(max_length=20)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('company', 'code')
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.description[:40]}"


class TaxMaster(CompanyAwareModel):
    name         = models.CharField(max_length=100)
    cgst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sgst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    igst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


# ── Shared party base ─────────────────────────────────────────────────────────
class PartyBase(CompanyAwareModel):
    name           = models.CharField(max_length=200)
    gst_number     = models.CharField(max_length=20, blank=True)
    address        = models.TextField(blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    phone          = models.CharField(max_length=15, blank=True)
    email          = models.EmailField(blank=True)
    city           = models.CharField(max_length=100, blank=True)
    state          = models.CharField(max_length=100, choices=STATE_CHOICES, blank=True)
    pincode        = models.CharField(max_length=10, blank=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name


class Supplier(PartyBase):
    pass


class Customer(PartyBase):
    pass


class Product(CompanyAwareModel):
    name          = models.CharField(max_length=200)
    category      = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True)
    hsn_code      = models.ForeignKey(HSNCode, on_delete=models.SET_NULL, null=True, blank=True)
    unit          = models.ForeignKey(UnitMaster, on_delete=models.SET_NULL, null=True, blank=True)
    tax           = models.ForeignKey(TaxMaster, on_delete=models.SET_NULL, null=True, blank=True)
    price         = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock         = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    reorder_level = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    is_active     = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def is_low_stock(self):
        return self.stock <= self.reorder_level


class SalesInvoice(CompanyAwareModel):
    STATUS = [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')]
    PAYMENT_STATUS = [('unpaid', 'Unpaid'), ('partial', 'Partial'), ('paid', 'Paid')]

    invoice_number = models.CharField(max_length=50)
    customer       = models.ForeignKey(Customer, on_delete=models.PROTECT)
    invoice_date   = models.DateField(default=timezone.now)
    due_date       = models.DateField(null=True, blank=True)
    status         = models.CharField(max_length=20, choices=STATUS, default='draft')
    notes          = models.TextField(blank=True)
    subtotal       = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_cgst     = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_sgst     = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_igst     = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total    = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    amount_paid    = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='unpaid')
    payment_date   = models.DateField(null=True, blank=True)
    created_by     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('company', 'invoice_number')
        ordering = ['-created_at']

    def __str__(self):
        return self.invoice_number

    @property
    def balance_due(self):
        return self.grand_total - self.amount_paid


class SalesLineItem(models.Model):
    invoice          = models.ForeignKey(SalesInvoice, on_delete=models.CASCADE, related_name='line_items')
    product          = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity         = models.DecimalField(max_digits=10, decimal_places=3)
    unit_price       = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cgst_percent     = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sgst_percent     = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    igst_percent     = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    taxable_amount   = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    cgst_amount      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sgst_amount      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    igst_amount      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    line_total       = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.product.name} x {self.quantity} (Inv: {self.invoice.invoice_number})"

    def calculate(self):
        D = Decimal
        taxable = self.quantity * self.unit_price * (1 - self.discount_percent / D('100'))
        self.taxable_amount = taxable.quantize(D('0.01'))
        self.cgst_amount    = (taxable * self.cgst_percent / D('100')).quantize(D('0.01'))
        self.sgst_amount    = (taxable * self.sgst_percent / D('100')).quantize(D('0.01'))
        self.igst_amount    = (taxable * self.igst_percent / D('100')).quantize(D('0.01'))
        self.line_total     = self.taxable_amount + self.cgst_amount + self.sgst_amount + self.igst_amount


class PurchaseOrder(CompanyAwareModel):
    STATUS = [('draft', 'Draft'), ('received', 'Received'), ('cancelled', 'Cancelled')]

    po_number   = models.CharField(max_length=50)
    supplier    = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    order_date  = models.DateField(default=timezone.now)
    status      = models.CharField(max_length=20, choices=STATUS, default='draft')
    notes       = models.TextField(blank=True)
    subtotal    = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_cgst  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_sgst  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_igst  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('company', 'po_number')
        ordering = ['-created_at']

    def __str__(self):
        return self.po_number


class PurchaseLineItem(models.Model):
    order          = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='line_items')
    product        = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity       = models.DecimalField(max_digits=10, decimal_places=3)
    unit_price     = models.DecimalField(max_digits=12, decimal_places=2)
    cgst_percent   = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sgst_percent   = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    igst_percent   = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    taxable_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    cgst_amount    = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sgst_amount    = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    igst_amount    = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    line_total     = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.product.name} x {self.quantity} (PO: {self.order.po_number})"

    def calculate(self):
        D = Decimal
        taxable = self.quantity * self.unit_price
        self.taxable_amount = taxable.quantize(D('0.01'))
        self.cgst_amount    = (taxable * self.cgst_percent / D('100')).quantize(D('0.01'))
        self.sgst_amount    = (taxable * self.sgst_percent / D('100')).quantize(D('0.01'))
        self.igst_amount    = (taxable * self.igst_percent / D('100')).quantize(D('0.01'))
        self.line_total     = self.taxable_amount + self.cgst_amount + self.sgst_amount + self.igst_amount


# ── Quotation ─────────────────────────────────────────────────────────────────
class Quotation(CompanyAwareModel):
    STATUS = [
        ('draft',    'Draft'),
        ('sent',     'Sent'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    quotation_number = models.CharField(max_length=50)
    customer         = models.ForeignKey(Customer, on_delete=models.PROTECT)
    quotation_date   = models.DateField(default=timezone.now)
    valid_until      = models.DateField(null=True, blank=True)
    status           = models.CharField(max_length=20, choices=STATUS, default='draft')
    notes            = models.TextField(blank=True)
    terms            = models.TextField(blank=True)
    subtotal         = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_cgst       = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_sgst       = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_igst       = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total      = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_by       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('company', 'quotation_number')
        ordering = ['-created_at']

    def __str__(self):
        return self.quotation_number

    def convert_to_invoice(self):
        """Returns True if status allows conversion."""
        return self.status == 'approved'


class QuotationLineItem(models.Model):
    quotation        = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='line_items')
    product          = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity         = models.DecimalField(max_digits=10, decimal_places=3)
    unit_price       = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cgst_percent     = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sgst_percent     = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    igst_percent     = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    taxable_amount   = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    cgst_amount      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sgst_amount      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    igst_amount      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    line_total       = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def calculate(self):
        D = Decimal
        taxable = self.quantity * self.unit_price * (1 - self.discount_percent / D('100'))
        self.taxable_amount = taxable.quantize(D('0.01'))
        self.cgst_amount    = (taxable * self.cgst_percent / D('100')).quantize(D('0.01'))
        self.sgst_amount    = (taxable * self.sgst_percent / D('100')).quantize(D('0.01'))
        self.igst_amount    = (taxable * self.igst_percent / D('100')).quantize(D('0.01'))
        self.line_total     = self.taxable_amount + self.cgst_amount + self.sgst_amount + self.igst_amount


# ── E-Way Bill ────────────────────────────────────────────────────────────────
class EWayBill(CompanyAwareModel):
    STATUS = [('active', 'Active'), ('cancelled', 'Cancelled'), ('expired', 'Expired')]

    invoice          = models.OneToOneField(SalesInvoice, on_delete=models.CASCADE,
                                            related_name='eway_bill', null=True, blank=True)
    eway_bill_number = models.CharField(max_length=50, blank=True)
    generated_date   = models.DateField(default=timezone.now)
    valid_upto       = models.DateField(null=True, blank=True)
    status           = models.CharField(max_length=20, choices=STATUS, default='active')
    transporter_name = models.CharField(max_length=200, blank=True)
    transporter_id   = models.CharField(max_length=50, blank=True)
    vehicle_number   = models.CharField(max_length=20, blank=True)
    distance_km      = models.PositiveIntegerField(default=0)
    supply_type      = models.CharField(max_length=50, blank=True, default='Outward')
    notes            = models.TextField(blank=True)
    created_by       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

# ── Audit Log ──────────────────────────────────────────────────────────────────
class AuditLog(CompanyAwareModel):
    ACTIONS = [
        ('create',  'Created'),
        ('edit',    'Edited'),
        ('delete',  'Deleted'),
        ('cancel',  'Cancelled'),
        ('convert', 'Converted'),
        ('login',   'Logged In'),
    ]

    user         = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action       = models.CharField(max_length=20, choices=ACTIONS)
    resource_type = models.CharField(max_length=50) # 'SalesInvoice', 'Product', etc.
    resource_id  = models.CharField(max_length=50, blank=True)
    details      = models.TextField(blank=True)     # JSON or descriptive text
    ip_address   = models.GenericIPAddressField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} {self.action} {self.resource_type} ({self.created_at})"

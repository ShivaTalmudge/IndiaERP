"""
core/views/__init__.py
Re-exports every view so existing urls.py works with zero changes.
"""
from .auth import landing_page, terms_page, privacy_page, login_view, logout_view
from .dashboard import dashboard
from .superadmin import (
    superadmin_dashboard, company_list, company_add,
    company_edit, company_toggle,
    impersonate_company, stop_impersonating,
)
from .staff import staff_list, staff_add, staff_edit, staff_delete
from .masters import (
    category_list, category_add, category_edit, category_delete,
    unit_list, unit_add, unit_edit, unit_delete,
    hsn_list, hsn_add, hsn_edit, hsn_delete,
    tax_list, tax_add, tax_edit, tax_delete,
    supplier_list, supplier_add, supplier_edit, supplier_delete,
    customer_list, customer_add, customer_edit, customer_delete,
    product_list, product_add, product_edit, product_delete,
    product_info,
)
from .sales import sales_list, sales_create, sales_detail, sales_cancel
from .purchase import purchase_list, purchase_create, purchase_detail, purchase_cancel
from .reports import (
    reports_home, sales_report, purchase_report, stock_report,
    gstr1_report, gstr2b_report, gstr3b_report, gstr7_report,
    hsn_summary_report,
    tds_receivable_report, tds_payable_report,
    tcs_receivable_report, tcs_payable_report,
)
from .quotation import (
    quotation_list, quotation_create, quotation_edit,
    quotation_detail, quotation_print_view, quotation_status, quotation_convert,
)
from .profile import profile_view, change_password
from .eway import eway_list, eway_create, eway_detail, eway_cancel, eway_print_view

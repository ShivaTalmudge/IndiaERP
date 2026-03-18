from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.landing_page, name='landing'),
    path('terms/', views.terms_page, name='terms'),
    path('privacy/', views.privacy_page, name='privacy'),
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Profile & Password
    path('profile/', views.profile_view, name='profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    # Super Admin
    path('superadmin/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('superadmin/companies/', views.company_list, name='company_list'),
    path('superadmin/companies/add/', views.company_add, name='company_add'),
    path('superadmin/companies/<int:pk>/edit/', views.company_edit, name='company_edit'),
    path('superadmin/companies/<int:pk>/toggle/', views.company_toggle, name='company_toggle'),
    path('superadmin/companies/<int:pk>/impersonate/', views.impersonate_company, name='impersonate_company'),
    path('superadmin/stop-impersonating/', views.stop_impersonating, name='stop_impersonating'),
    # Staff
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/add/', views.staff_add, name='staff_add'),
    path('staff/<int:pk>/edit/', views.staff_edit, name='staff_edit'),
    path('staff/<int:pk>/delete/', views.staff_delete, name='staff_delete'),
    # Masters
    path('masters/categories/', views.category_list, name='category_list'),
    path('masters/categories/add/', views.category_add, name='category_add'),
    path('masters/categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('masters/categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('masters/units/', views.unit_list, name='unit_list'),
    path('masters/units/add/', views.unit_add, name='unit_add'),
    path('masters/units/<int:pk>/edit/', views.unit_edit, name='unit_edit'),
    path('masters/units/<int:pk>/delete/', views.unit_delete, name='unit_delete'),
    path('masters/hsn/', views.hsn_list, name='hsn_list'),
    path('masters/hsn/add/', views.hsn_add, name='hsn_add'),
    path('masters/hsn/<int:pk>/edit/', views.hsn_edit, name='hsn_edit'),
    path('masters/hsn/<int:pk>/delete/', views.hsn_delete, name='hsn_delete'),
    path('masters/tax/', views.tax_list, name='tax_list'),
    path('masters/tax/add/', views.tax_add, name='tax_add'),
    path('masters/tax/<int:pk>/edit/', views.tax_edit, name='tax_edit'),
    path('masters/tax/<int:pk>/delete/', views.tax_delete, name='tax_delete'),
    path('masters/suppliers/', views.supplier_list, name='supplier_list'),
    path('masters/suppliers/add/', views.supplier_add, name='supplier_add'),
    path('masters/suppliers/<int:pk>/edit/', views.supplier_edit, name='supplier_edit'),
    path('masters/suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),
    path('masters/customers/', views.customer_list, name='customer_list'),
    path('masters/customers/add/', views.customer_add, name='customer_add'),
    path('masters/customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('masters/customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    path('masters/products/', views.product_list, name='product_list'),
    path('masters/products/add/', views.product_add, name='product_add'),
    path('masters/products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('masters/products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    # AJAX
    path('api/product/<int:pk>/', views.product_info, name='product_info'),
    # Sales / Invoices
    path('sales/', views.sales_list, name='sales_list'),
    path('sales/create/', views.sales_create, name='sales_create'),
    path('sales/<int:pk>/', views.sales_detail, name='sales_detail'),
    path('sales/<int:pk>/cancel/', views.sales_cancel, name='sales_cancel'),
    path('sales/<int:invoice_pk>/eway/', views.eway_create, name='eway_create'),
    # Purchase
    path('purchase/', views.purchase_list, name='purchase_list'),
    path('purchase/create/', views.purchase_create, name='purchase_create'),
    path('purchase/<int:pk>/', views.purchase_detail, name='purchase_detail'),
    path('purchase/<int:pk>/cancel/', views.purchase_cancel, name='purchase_cancel'),
    # Quotations
    path('quotations/', views.quotation_list, name='quotation_list'),
    path('quotations/create/', views.quotation_create, name='quotation_create'),
    path('quotations/<int:pk>/', views.quotation_detail, name='quotation_detail'),
    path('quotations/<int:pk>/edit/', views.quotation_edit, name='quotation_edit'),
    path('quotations/<int:pk>/status/', views.quotation_status, name='quotation_status'),
    path('quotations/<int:pk>/convert/', views.quotation_convert, name='quotation_convert'),
    path('quotations/<int:pk>/print/', views.quotation_print_view, name='quotation_print'),
    # E-Way Bills
    path('eway/', views.eway_list, name='eway_list'),
    path('eway/<int:pk>/', views.eway_detail, name='eway_detail'),
    path('eway/<int:pk>/cancel/', views.eway_cancel, name='eway_cancel'),
    path('eway/<int:pk>/print/', views.eway_print_view, name='eway_print'),
    # Reports
    path('reports/', views.reports_home, name='reports_home'),
    path('reports/sales/', views.sales_report, name='sales_report'),
    path('reports/purchase/', views.purchase_report, name='purchase_report'),
    path('reports/stock/', views.stock_report, name='stock_report'),
    # GST Reports
    path('reports/gstr1/', views.gstr1_report, name='gstr1_report'),
    path('reports/gstr2b/', views.gstr2b_report, name='gstr2b_report'),
    path('reports/gstr3b/', views.gstr3b_report, name='gstr3b_report'),
    path('reports/gstr7/', views.gstr7_report, name='gstr7_report'),
    path('reports/hsn-summary/', views.hsn_summary_report, name='hsn_summary_report'),
    # TDS / TCS
    path('reports/tds-receivable/', views.tds_receivable_report, name='tds_receivable_report'),
    path('reports/tds-payable/', views.tds_payable_report, name='tds_payable_report'),
    path('reports/tcs-receivable/', views.tcs_receivable_report, name='tcs_receivable_report'),
    path('reports/tcs-payable/', views.tcs_payable_report, name='tcs_payable_report'),
]

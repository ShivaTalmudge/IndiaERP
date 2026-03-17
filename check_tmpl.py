import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'erp_saas.settings'
sys.path.insert(0, r'e:\erp_final')

import django
django.setup()

from django.template.loader import get_template
templates = [
    'sales/invoice_detail.html',
    'core/gstr1_report.html',
    'core/gstr2b_report.html',
    'core/gstr3b_report.html',
    'core/gstr7_report.html',
    'core/hsn_summary_report.html',
    'core/tds_report.html',
    'core/reports_home.html',
]
for tmpl in templates:
    try:
        get_template(tmpl)
        print(f"  OK  {tmpl}")
    except Exception as e:
        print(f"  ERR {tmpl}: {e}")

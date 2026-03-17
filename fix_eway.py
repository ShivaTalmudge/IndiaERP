import os, re

eway_print = "e:/erp_final/templates/sales/eway_print.html"
eway_detail = "e:/erp_final/templates/sales/eway_detail.html"

with open(eway_print, "r", encoding="utf-8") as f:
    pt = f.read()

styles = re.search(r"(?s)<style>(.*?)</style>", pt).group(1)
body_html = re.search(r"(?s)<body>(.*?)</body>", pt).group(1)

with open(eway_detail, "r", encoding="utf-8") as f:
    dt = f.read()

# Eway detail split before the <div class="row g-4">
header_part = dt.split('<div class="row g-4">')[0]
header_part = header_part.replace('<div class="d-flex align-items-center justify-content-between mb-4">', '<div class="no-print d-flex align-items-center justify-content-between mb-4">')

# Fix print button
header_part = header_part.replace('href="{% url \'eway_print\' eway.pk %}" target="_blank"', 'href="javascript:window.print()"')

new_detail = header_part + """
{% block extra_css %}
<style>
@media print {
    body { background: #fff !important; margin: 0; }
    #sidebar, .topbar, .no-print, .btn, .breadcrumb { display: none !important; }
    #main { margin-left: 0 !important; padding:0 !important;}
    .page-body { padding: 0 !important;}
    .page-wrap { box-shadow:none !important; padding:0 !important; max-width:100% !important;}
}
""" + styles + """
/* Formats */
.page-wrap { max-width: 800px; margin: 0 auto; background: #fff; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); font-family: 'Roboto', Arial, sans-serif; font-size:11px; }
</style>
{% endblock %}
""" + body_html + "\n{% endblock %}"

# remove no-print from body_html because we already have it handled top.
new_detail = re.sub(r'(?s)<div class="no-print">.*?</div>', '', new_detail)

with open(eway_detail, "w", encoding="utf-8") as f:
    f.write(new_detail)

print("Eway detail fixed.")

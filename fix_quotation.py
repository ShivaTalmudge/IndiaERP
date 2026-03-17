import os, re

q_print = "e:/erp_final/templates/sales/quotation_print.html"
q_detail = "e:/erp_final/templates/sales/quotation_detail.html"

with open(q_print, "r", encoding="utf-8") as f:
    pt = f.read()

styles = re.search(r"(?s)<style>(.*?)</style>", pt).group(1)
body_html = re.search(r"(?s)<body>(.*?)</body>", pt).group(1)

with open(q_detail, "r", encoding="utf-8") as f:
    dt = f.read()

header_part = dt.split('<div class="row g-4">')[0]
header_part = header_part.replace('<div class="d-flex align-items-start', '<div class="no-print d-flex align-items-start')
header_part = header_part.replace('href="{% url \'quotation_print\' quotation.pk %}" target="_blank"', 'href="javascript:window.print()"')

status_update = """
        <div class="no-print card shadow-sm mb-4" style="max-width:400px">
            <div class="card-header py-2 fw-semibold">Update Status</div>
            <div class="card-body">
                <form method="post" action="{% url 'quotation_status' quotation.pk %}" class="d-flex gap-2 align-items-center">
                    {% csrf_token %}
                    <select name="status" class="form-select form-select-sm">
                        <option value="draft" {% if status == 'draft' %}selected{% endif %}>Draft</option>
                        <option value="sent" {% if status == 'sent' %}selected{% endif %}>Sent</option>
                        <option value="approved" {% if status == 'approved' %}selected{% endif %}>Approved</option>
                        <option value="rejected" {% if status == 'rejected' %}selected{% endif %}>Rejected</option>
                    </select>
                    <button type="submit" class="btn btn-primary btn-sm">Update</button>
                </form>
            </div>
        </div>
"""

new_detail = header_part + """
{% block extra_css %}
<style>
@media print {
    body { background: #fff !important; margin: 0; }
    #sidebar, .topbar, .no-print, .btn, .breadcrumb { display: none !important; }
    #main { margin-left: 0 !important; padding:0 !important;}
    .page-body { padding: 0 !important;}
    .q-wrap { border: none !important; margin: 0 !important; max-width: 100% !important; border-radius: 0 !important; box-shadow:none;}
}
""" + styles + """
/* Fix overlapping padding */
.q-wrap { max-width: 900px; margin:20px auto; background:#fff; }
</style>
{% endblock %}
""" + status_update + body_html + "\n{% endwith %}\n{% endblock %}"

new_detail = re.sub(r'(?s)<div class="print-bar">.*?</div>', '', new_detail)

with open(q_detail, "w", encoding="utf-8") as f:
    f.write(new_detail)

print("Quotation detail fixed.")

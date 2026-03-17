import os

fpath = r'e:\erp_final\templates\sales\quotation_detail.html'
with open(fpath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix spacing in status update form
fixes = {
    "status=='draft'": "status == 'draft'",
    "status=='sent'": "status == 'sent'",
    "status=='approved'": "status == 'approved'",
    "status=='rejected'": "status == 'rejected'",
    'status=="draft"': 'status == "draft"',
    'status=="sent"': 'status == "sent"',
    'status=="approved"': 'status == "approved"',
    'status=="rejected"': 'status == "rejected"',
}

for old, new in fixes.items():
    content = content.replace(old, new)

with open(fpath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Fixed {fpath}")

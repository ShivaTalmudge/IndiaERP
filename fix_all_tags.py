import os, re

files = [
    r'e:\erp_final\templates\sales\quotation_detail.html',
    r'e:\erp_final\templates\sales\eway_detail.html',
    r'e:\erp_final\templates\core\sales_report.html',
]

def collapse_tags(content):
    # Regex to find {{ ... }} tags that may span multiple lines
    # and replace internal newlines/excess whitespace with single spaces
    def replacer(match):
        tag_content = match.group(1)
        # Collapse all whitespace and newlines inside the tag
        collapsed = " ".join(tag_content.split())
        return f"{{{{ {collapsed} }}}}"
    
    # Non-greedy match for content between {{ and }}
    return re.sub(r'\{\{(.*?)\}\}', replacer, content, flags=re.DOTALL)

for fpath in files:
    if os.path.exists(fpath):
        with open(fpath, 'r', encoding='utf-8') as f:
            old_content = f.read()
        new_content = collapse_tags(old_content)
        if old_content != new_content:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Collapsed tags in {fpath}")
        else:
            print(f"No changes needed in {fpath}")
    else:
        print(f"File not found: {fpath}")

# Specifically fix the 'status == 'draft'' thing again just in case
for fpath in files:
    if os.path.exists(fpath):
        with open(fpath, 'r', encoding='utf-8') as f:
            c = f.read()
        c = c.replace("{%if", "{% if ").replace("%}", " %}")
        # Ensure spaces around == in if tags
        # Non-greedy match for content between {% and %}
        def fix_if_logic(match):
            inner = match.group(1)
            # Add spaces around == if missing
            inner = re.sub(r'([^\s=])==', r'\1 ==', inner)
            inner = re.sub(r'==([^\s=])', r'== \1', inner)
            # Normalize internal spaces
            inner = " ".join(inner.split())
            return f"{{% {inner} %}}"
        
        c = re.sub(r'\{%(.*?)%\}', fix_if_logic, c, flags=re.DOTALL)
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f"Normalized logic tags in {fpath}")

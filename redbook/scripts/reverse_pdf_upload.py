"""
Reverse-engineer Xiaohongshu PDF/document upload API.
Analyzes the creator page JS bundles to find the document upload endpoints.
"""
import re, requests, json

# Download the main publish component JS
JS_URLS = [
    "https://fe-static.xhscdn.com/formula-static/ugc/public/resource/js/project-publish-components.4ae42cdb.js",
    "https://fe-static.xhscdn.com/formula-static/ugc/public/resource/js/project-publish-vue.24aa412c.js",
]

for url in JS_URLS:
    print(f"\n{'='*60}")
    print(f"Analyzing: {url.split('/')[-1][:50]}")
    resp = requests.get(url, timeout=30)
    js = resp.text
    print(f"Size: {len(js)} chars")

    # Search for API endpoints
    api_pattern = r'(?:["\x27])((?:/api|/web_api)/[^"\x27]{3,80})(?:["\x27])'
    apis = list(set(re.findall(api_pattern, js)))
    apis.sort()

    doc_related = [a for a in apis if any(k in a.lower() for k in
        ['doc', 'file', 'attach', 'upload', 'galaxy', 'material', 'media'])]
    if doc_related:
        print(f"\n  Document/upload related APIs:")
        for a in doc_related[:20]:
            print(f"    {a}")

    # Also search for specific field names
    field_pattern = r'"(doc_id|related_file|file_id|attachment|fileType|file_type|fileName|file_name)"'
    fields = re.findall(field_pattern, js)
    if fields:
        print(f"\n  Related fields found: {list(set(fields))}")

    # Search for document upload function calls
    func_pattern = r'(uploadFile|uploadDoc|addFile|attachFile|createDoc|uploadDocument)[^)]*'
    funcs = re.findall(func_pattern, js)
    if funcs:
        print(f"\n  Upload functions found:")
        for f in list(set(funcs))[:10]:
            print(f"    {f[:120]}")

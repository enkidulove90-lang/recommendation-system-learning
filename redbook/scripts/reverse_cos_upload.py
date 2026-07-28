"""
Reverse-engineer COS file upload API from Xiaohongshu creator JS bundles.
"""
import requests, re, json

# Latest publish-components JS
JS_URLS = [
    "https://fe-static.xhscdn.com/formula-static/ugc/public/resource/js/project-publish-components.4ae42c5f.js",
    "https://fe-static.xhscdn.com/formula-static/ugc/public/resource/js/index.d8bcb8c3.js",
    "https://fe-static.xhscdn.com/formula-static/ugc/public/resource/js/4526.b04502af.js",
]

for url in JS_URLS:
    print(f"\n{'='*60}")
    print(f"Analyzing: {url.split('/')[-1][:60]}")
    try:
        resp = requests.get(url, timeout=30)
        js = resp.text
        print(f"Size: {len(js):,} chars")
    except Exception as e:
        print(f"Download failed: {e}")
        continue

    # Search for COS/document/file upload related APIs
    patterns = [
        r'/api/galaxy/[^"\']{5,80}',
        r'/api/media/[^"\']{5,80}',
        r'/api/sns/[^"\']{5,80}',
    ]

    all_apis = set()
    for p in patterns:
        all_apis.update(re.findall(p, js))

    # Filter for upload/doc/file/cos related
    keywords = ['upload', 'doc', 'file', 'attach', 'cos', 'credential', 'permit',
                'temp', 'token', 'gen_id', 'material']
    relevant = []
    for api in sorted(all_apis):
        if any(k in api.lower() for k in keywords):
            relevant.append(api)

    if relevant:
        print(f"\n  Relevant APIs ({len(relevant)}):")
        for api in relevant[:30]:
            print(f"    {api}")

    # Also search for COS specific patterns
    cos_patterns = [
        r'(getCredentials|getAuthorization|getCosToken|fetchToken)[^)]{0,100}',
        r'(cos|COS|Cos)[^,;]{0,80}',
        r'(ststoken|sts_token|tmpSecretId|tmpSecretKey|sessionToken)[^,;]{0,80}',
    ]
    for p in cos_patterns:
        matches = re.findall(p, js, re.IGNORECASE)
        if matches:
            unique = list(set(matches))[:5]
            print(f"\n  COS pattern [{p[:50]}]: {unique}")

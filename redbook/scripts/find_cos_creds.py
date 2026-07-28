"""
Find COS credentials API, bucket, region from XHS creator JS bundles.
"""
import requests, re, json, os

JS_URLS = [
    "https://fe-static.xhscdn.com/formula-static/ugc/public/resource/js/index.d8bcb8c3.js",
    "https://fe-static.xhscdn.com/formula-static/ugc/public/resource/js/4526.b04502af.js",
    "https://fe-static.xhscdn.com/formula-static/ugc/public/resource/js/project-publish-components.4ae42c5f.js",
]

found = {"apis": set(), "buckets": set(), "regions": set(), "configs": []}

for url in JS_URLS:
    print(f"\n{'='*60}")
    print(f"File: {os.path.basename(url)[:50]}")
    resp = requests.get(url, timeout=30)
    js = resp.text
    print(f"Size: {len(js):,} chars")

    # Search for COS credential patterns
    # Pattern 1: API endpoints for credentials
    cred_apis = re.findall(r'["\x27](/api/[^"\x27]{10,120})["\x27]', js)
    for api in cred_apis:
        if any(k in api.lower() for k in ['credential', 'token', 'sts', 'cos', 'authorization', 'tmp', 'secret']):
            found["apis"].add(api)
            print(f"  Cred API: {api}")

    # Pattern 2: Bucket names
    buckets = re.findall(r'Bucket["\s:=]+["\x27]([^"\x27]{5,60})["\x27]', js)
    for b in buckets:
        if 'xh' in b.lower() or 'spectrum' in b.lower() or 'cos' in b.lower() or 'ros' in b.lower():
            found["buckets"].add(b)
            print(f"  Bucket: {b}")

    # Pattern 3: Regions
    regions = re.findall(r'Region["\s:=]+["\x27]([^"\x27]{4,30})["\x27]', js)
    for r in regions:
        if 'ap-' in r or 'accelerate' in r:
            found["regions"].add(r)
            print(f"  Region: {r}")

    # Pattern 4: getAuthorization context
    for m in re.finditer(r'getAuthorization[^}]{0,300}', js):
        ctx = js[m.start():m.end()]
        # Extract URLs and config
        urls = re.findall(r'["\x27](/api/[^"\x27]+)["\x27]', ctx)
        for u in urls:
            found["apis"].add(u)
            print(f"  getAuth API: {u}")
        break  # Just first match

    # Pattern 5: COS SDK init/config
    for m in re.finditer(r'new\s+\w+\(\{[^}]{0,400}getAuthorization', js):
        ctx = js[m.start():m.end()+200]
        print(f"\n  COS init context ({len(ctx)} chars):")
        # Print first 500 chars
        print(f"  {ctx[:500]}")

print(f"\n{'='*60}")
print("SUMMARY:")
print(f"  Cred APIs: {sorted(found['apis'])}")
print(f"  Buckets: {sorted(found['buckets'])}")
print(f"  Regions: {sorted(found['regions'])}")

"""Extract COS config from creator page HTML."""
import requests, re, json
from pathlib import Path

cookies = json.loads(Path.home().joinpath('.xiaohongshu-cli','cookies.json').read_text())
session = requests.Session()
for k,v in cookies.items():
    session.cookies.set(k, v, domain='.xiaohongshu.com')

resp = session.get('https://creator.xiaohongshu.com/publish/publish',
                    headers={'User-Agent': 'Mozilla/5.0'},
                    timeout=15)
html = resp.text
print(f"HTML size: {len(html):,} chars")

# Pattern 1: COS credentials in inline scripts
print("\n=== COS credentials ===")
for m in re.finditer(r'(SecretId|secretId|TmpSecretId|tmpSecretId)\S{0,50}', html):
    print(f"  {m.group()[:100]}")

print("\n=== Bucket ===")
for m in re.finditer(r'(Bucket|bucket)\S{0,30}', html):
    val = m.group()[:80]
    if any(c.isalpha() for c in val):
        print(f"  {val}")

print("\n=== Region ===")
for m in re.finditer(r'(Region|region)\S{0,30}', html):
    val = m.group()[:80]
    if any(c.isalpha() for c in val):
        print(f"  {val}")

# Pattern 2: Search inline scripts for COS init
print("\n=== Inline scripts with COS ===")
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
for i, s in enumerate(scripts):
    if 'cos' in s.lower() or 'COS' in s or 'getAuthorization' in s:
        # Print first 1000 chars
        clean = s.replace('\\n', '\n').replace('\\"', '"')[:1000]
        print(f"\n  Script[{i}] ({len(s)} chars):")
        print(f"  {clean}")
        break

# Pattern 3: Check window.__INITIAL_STATE__
print("\n=== __INITIAL_STATE__ ===")
m = re.search(r'window\.__INITIAL_STATE__\s*=\s*({[^<]{0,500})', html)
if m:
    state_snippet = m.group(1)[:500]
    print(f"  {state_snippet}")
else:
    print("  Not found in HTML (loaded dynamically)")

# Pattern 4: All API endpoints visible in HTML
print("\n=== API endpoints in HTML ===")
apis = set(re.findall(r'(/api/[a-zA-Z0-9_/.-]{10,120})', html))
for a in sorted(apis):
    if any(k in a.lower() for k in ['upload', 'doc', 'file', 'cos', 'credential', 'token', 'sts']):
        print(f"  {a}")

# Save HTML for manual inspection
html_path = Path.home() / 'creator_page.html'
html_path.write_text(html, encoding='utf-8')
print(f"\nHTML saved to: {html_path}")

"""
Brute-force search for the document upload API endpoint.
"""
import json, requests
from pathlib import Path
from xhs_cli.commands._common import get_cookies

browser, cookies = get_cookies('auto')
session = requests.Session()
for k, v in cookies.items():
    session.cookies.set(k, v, domain='.xiaohongshu.com')

PDF = r'c:\Users\xu.yan1\papers\recommendation-system-learning\data\parsed\2604.08011\SSR_paper.pdf'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Origin': 'https://creator.xiaohongshu.com',
    'Referer': 'https://creator.xiaohongshu.com/publish/publish',
}

# 1. Get a doc_id first
resp = session.post('https://creator.xiaohongshu.com/api/galaxy/v2/creator/doc/gen_id',
                     json={}, headers=HEADERS, timeout=10)
doc_id = resp.json().get('id', '')
print(f'doc_id: {doc_id}')

# 2. Try ALL possible upload endpoints
endpoints = [
    # Direct doc upload
    f'/api/galaxy/v2/creator/doc/upload',
    f'/api/galaxy/v2/creator/doc/upload/{doc_id}',
    f'/api/galaxy/v2/creator/doc/{doc_id}/upload',
    # Media upload variants
    '/api/media/v1/upload/doc',
    '/api/media/v1/upload/file',
    '/api/media/v1/upload/attachment',
    # COS direct
    '/api/media/v1/upload/cos/credential',
    '/api/media/v1/upload/sts',
    # File/material upload
    '/api/galaxy/v2/creator/material/upload',
    '/api/galaxy/v2/creator/file/upload',
    '/api/sns/web/v1/upload/doc',
]

with open(PDF, 'rb') as f:
    pdf_data = f.read()

for path in endpoints:
    url = f'https://creator.xiaohongshu.com{path}'

    # Try POST with JSON
    try:
        r = session.post(url, json={'doc_id': str(doc_id), 'name': 'test.pdf'},
                        headers=HEADERS, timeout=10)
        if r.status_code not in [404, 406]:
            print(f'POST JSON {path}: {r.status_code} - {r.text[:150]}')
    except Exception as e:
        pass

    # Try POST with multipart form
    try:
        files = {'file': ('test.pdf', pdf_data, 'application/pdf')}
        data = {'doc_id': str(doc_id)}
        r = session.post(url, files=files, data=data, headers=HEADERS, timeout=15)
        if r.status_code not in [404, 406]:
            print(f'POST MULTIPART {path}: {r.status_code} - {r.text[:200]}')
    except Exception as e:
        pass

print("\nDone. If nothing printed above 406/404, all endpoints returned standard errors.")

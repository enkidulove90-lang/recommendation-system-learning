"""Upload PDF via web_doc permit and attach to note."""
import json, os, sys

sys.path.insert(0, r'c:\Users\xu.yan1\AppData\Roaming\Python\Python311\site-packages')
from xhs_cli.commands._common import get_cookies
from xhs_cli.client import XhsClient

PDF = r'c:\Users\xu.yan1\papers\recommendation-system-learning\data\parsed\2604.08011\SSR_paper.pdf'

browser, cookies = get_cookies('auto')
client = XhsClient(cookies)

with client:
    # Step 1: Get doc_id
    doc = client._creator_post('/api/galaxy/v2/creator/doc/gen_id', {})
    doc_id = str(doc['id'])
    print(f'doc_id: {doc_id}')

    # Step 2: Get upload permit for web_doc
    permit_resp = client._creator_get('/api/media/v1/upload/creator/permit', {
        'biz_name': 'sns', 'scene': 'web_doc',
        'file_count': 1, 'version': 1, 'source': 'web',
    })
    permit = permit_resp['uploadTempPermits'][0]
    fid = permit['fileIds'][0]
    token = permit['token']
    addr = permit['uploadAddr']
    print(f'fid: {fid}')
    print(f'addr: {addr}')

    # Step 3: Upload PDF to ROS
    with open(PDF, 'rb') as f:
        pdf_data = f.read()
    print(f'PDF: {len(pdf_data):,} bytes')

    url = f'https://{addr}/{fid}'
    resp = client._request_with_retry('PUT', url, headers={
        'X-Cos-Security-Token': token,
        'Content-Type': 'application/pdf',
    }, content=pdf_data)
    print(f'Upload status: {resp.status_code}')

    if resp.status_code < 400:
        print('PDF UPLOADED!')
        result = {
            'doc_id': doc_id,
            'file_id': fid,
            'file_name': 'SSR_paper.pdf',
            'file_size': len(pdf_data),
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f'Upload failed: {resp.status_code}')
        print(resp.text[:500] if hasattr(resp, 'text') else '')

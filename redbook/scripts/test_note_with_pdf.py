"""Test creating a note with PDF attachment (draft only)."""
import json, os, sys
sys.path.insert(0, r'c:\Users\xu.yan1\AppData\Roaming\Python\Python311\site-packages')
from xhs_cli.commands._common import get_cookies
from xhs_cli.client import XhsClient
from xhs_cli.constants import CREATOR_HOST

PDF = r'c:\Users\xu.yan1\papers\recommendation-system-learning\data\parsed\2604.08011\SSR_paper.pdf'
IMG = r'c:\Users\xu.yan1\papers\recommendation-system-learning\data\parsed\2604.08011\images_hd\model.jpg'

browser, cookies = get_cookies('auto')
client = XhsClient(cookies)

with client:
    # 1. Get doc_id
    doc = client._creator_post('/api/galaxy/v2/creator/doc/gen_id', {})
    doc_id = str(doc['id'])
    print(f'doc_id: {doc_id}')

    # 2. Upload PDF
    permit = client._creator_get('/api/media/v1/upload/creator/permit', {
        'biz_name': 'sns', 'scene': 'web_doc',
        'file_count': 1, 'version': 1, 'source': 'web',
    })
    p = permit['uploadTempPermits'][0]
    with open(PDF, 'rb') as f:
        pdf_data = f.read()
    url = f"https://{p['uploadAddr']}/{p['fileIds'][0]}"
    resp = client._request_with_retry('PUT', url, headers={
        'X-Cos-Security-Token': p['token'],
        'Content-Type': 'application/pdf',
    }, content=pdf_data)
    print(f'PDF upload: {resp.status_code}')

    # 3. Upload image
    img_permit = client._creator_get('/api/media/v1/upload/creator/permit', {
        'biz_name': 'spectrum', 'scene': 'image',
        'file_count': 1, 'version': 1, 'source': 'web',
    })
    ip = img_permit['uploadTempPermits'][0]
    img_fid = ip['fileIds'][0]
    with open(IMG, 'rb') as f:
        img_data = f.read()
    img_url = f"https://{ip['uploadAddr']}/{img_fid}"
    resp2 = client._request_with_retry('PUT', img_url, headers={
        'X-Cos-Security-Token': ip['token'],
        'Content-Type': 'image/jpeg',
    }, content=img_data)
    print(f'Image upload: {resp2.status_code}, fid={img_fid}')

    # 4. Create note with PDF attachment
    images = [{'file_id': img_fid, 'metadata': {'source': -1}}]
    business_binds = json.dumps({
        'version': 1, 'noteId': 0, 'noteOrderBind': {},
        'notePostTiming': {'postTime': None}, 'noteCollectionBind': {'id': ''},
    })

    related_file = {
        'doc_id': doc_id,
        'name': 'SSR_paper.pdf',
    }

    payload = {
        'common': {
            'type': 'normal', 'title': 'PDF附件测试-SSR', 'note_id': '',
            'desc': '测试PDF附件上传功能',
            'source': '{"type":"web","ids":"","extraInfo":"{\\"subType\\":\\"official\\"}"}',
            'business_binds': business_binds,
            'ats': [], 'hash_tag': [], 'post_loc': {},
            'privacy_info': {'op_type': 1, 'type': 0},
        },
        'image_info': {'images': images},
        'video_info': None,
        'related_file': related_file,
    }

    result = client._main_api_post('/web_api/sns/v2/note', payload, {
        'origin': CREATOR_HOST, 'referer': f'{CREATOR_HOST}/',
    })
    print(f'\nNote result:')
    print(json.dumps(result, indent=2, ensure_ascii=False)[:800])

    note_id = result.get('data', {}).get('id', result.get('id', ''))
    if note_id:
        print(f'\nPUBLISHED! ID: {note_id}')
        print(f'URL: https://www.xiaohongshu.com/explore/{note_id}')

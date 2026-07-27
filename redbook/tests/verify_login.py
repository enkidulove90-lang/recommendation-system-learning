"""Verify login status with saved cookies."""
import sys
sys.path.insert(0, r'c:\Users\xu.yan1\papers\recommendation-system-learning\redbook')

import playwright_browser

class _FakeCSyncApi:
    Camoufox = playwright_browser.PlaywrightBrowser
class _FakeC:
    sync_api = _FakeCSyncApi()
sys.modules['camoufox'] = _FakeC
sys.modules['camoufox.sync_api'] = _FakeCSyncApi()

from xhs_cli.auth import get_cookie_string, COOKIE_FILE, cookie_str_to_dict
from xhs_cli.client import XhsClient
import json

print(f'Cookie file exists: {COOKIE_FILE.exists()}')
if COOKIE_FILE.exists():
    data = json.loads(COOKIE_FILE.read_text())
    print(f'Keys: {list(data.get("cookies", {}).keys())}')

cookie = get_cookie_string()
if cookie:
    print('Session string found!')
    with XhsClient(cookie_str_to_dict(cookie)) as client:
        info = client.get_self_info()
        print(f'Info keys: {list(info.keys())[:10]}')
        nickname = ''
        if isinstance(info, dict):
            for key in ['userInfo', 'basicInfo', 'userPageData']:
                sub = info.get(key, {})
                if isinstance(sub, dict):
                    nickname = sub.get('nickname', '') or sub.get('nickName', '')
                    if nickname: break
            if not nickname:
                nickname = info.get('nickname', '')
        if nickname:
            print(f'SUCCESS: Logged in as [{nickname}]')
        else:
            print('WARNING: Could not extract nickname')
            # Print snippets
            if 'userPageData' in info:
                ud = info['userPageData']
                if isinstance(ud, dict):
                    bi = ud.get('basicInfo', {})
                    if isinstance(bi, dict):
                        print(f'  basicInfo: nickname={bi.get("nickname")}, userId={bi.get("userId")}')
else:
    print('ERROR: No session found')

playwright_browser.shutdown()
print('Done.')

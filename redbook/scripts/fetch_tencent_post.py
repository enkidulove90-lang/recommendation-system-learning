"""Find the specific Tencent post from 乌萨奇今天读paper了吗."""
import sys
sys.path.insert(0, r'c:\Users\xu.yan1\papers\recommendation-system-learning\redbook')

import playwright_browser
class _F: Camoufox = playwright_browser.PlaywrightBrowser
class _M: sync_api = _F()
sys.modules['camoufox'] = _M
sys.modules['camoufox.sync_api'] = _F

from xhs_cli.auth import get_cookie_string, cookie_str_to_dict
from xhs_cli.client import XhsClient

def main():
    cookie = get_cookie_string()
    if not cookie:
        print("Not logged in!")
        return

    with XhsClient(cookie_str_to_dict(cookie)) as client:
        # Search with multiple queries to find the Tencent post
        queries = [
            "腾讯 端到端 视觉思维链",
            "腾讯 端到端强化 多模态",
            "腾讯 视觉思维链",
            "端到端强化多模态视觉思维链",
        ]

        for q in queries:
            print(f"\n{'='*60}")
            print(f"Query: {q}")
            try:
                results = client.search_notes(q)
                for i, r in enumerate(results):
                    nid = r.get("id", "")
                    nc = r.get("noteCard", {})
                    title = nc.get("displayTitle", "")
                    user = nc.get("user", {})
                    nickname = user.get("nickname", "")
                    if "腾讯" in title or "端到端" in title:
                        print(f"  *** MATCH [{i}]: {title[:80]}")
                        print(f"  Note ID: {nid}")
                        print(f"  Author: {nickname}")
                        print(f"  xsec: {r.get('xsecToken', '')[:50]}")

                        # Get full detail
                        try:
                            detail = client.get_note_detail(nid, r.get('xsecToken', ''))
                            nd = detail.get("note", detail)
                            desc = nd.get("desc", "")
                            print(f"\n  === FULL CONTENT ===")
                            print(f"  Title: {nd.get('title', title)}")
                            print(f"  Desc ({len(desc)} chars):")
                            print(desc[:2000])
                            print(f"\n  Tags: {nd.get('tagList', nd.get('tags', []))}")
                            imgs = nd.get("imageList", [])
                            print(f"  Images: {len(imgs)}")
                            for j, img in enumerate(imgs):
                                url = img.get("url", "") if isinstance(img, dict) else str(img)
                                print(f"    [{j}] {url[:120]}")
                        except Exception as e:
                            print(f"  Detail error: {e}")
            except Exception as e:
                print(f"  Search error: {e}")

    playwright_browser.shutdown()

if __name__ == "__main__":
    main()

"""Search for target user and get their posts with correct ID extraction."""
import sys, json
sys.path.insert(0, r'c:\Users\xu.yan1\papers\recommendation-system-learning\redbook')

import playwright_browser
class _F: Camoufox = playwright_browser.PlaywrightBrowser
class _M: sync_api = _F()
sys.modules['camoufox'] = _M
sys.modules['camoufox.sync_api'] = _F

from xhs_cli.auth import get_cookie_string, cookie_str_to_dict
from xhs_cli.client import XhsClient

def extract_note_id(card):
    """Try multiple paths to extract note_id from card."""
    if isinstance(card, str):
        return card
    for key in ['noteId', 'note_id', 'id', 'nid']:
        val = card.get(key, '')
        if val:
            return val
    # Try nested
    for sub in ['noteCard', 'note']:
        sub_obj = card.get(sub, {})
        if isinstance(sub_obj, dict):
            for key in ['noteId', 'note_id', 'id']:
                val = sub_obj.get(key, '')
                if val:
                    return val
    return ''

def main():
    cookie = get_cookie_string()
    if not cookie:
        print("Not logged in!")
        return

    with XhsClient(cookie_str_to_dict(cookie)) as client:
        # Step 1: Search for user
        print("Searching for: 乌萨奇今天读paper了吗 ...")
        results = client.search_notes("乌萨奇今天读paper了吗")

        # Debug: dump first result structure
        if results:
            r0 = results[0]
            print(f"\nFirst result type: {type(r0).__name__}")
            if isinstance(r0, dict):
                print(f"Keys: {list(r0.keys())[:15]}")
                for k, v in r0.items():
                    if isinstance(v, (str, int, float)):
                        print(f"  {k} = {str(v)[:100]}")
                    elif isinstance(v, dict):
                        print(f"  {k} = dict with keys {list(v.keys())[:10]}")
                    elif isinstance(v, list):
                        print(f"  {k} = list[{len(v)}]")

            # Find the user ID from any result
            target_user_id = None
            target_nickname = ""
            for r in results[:10]:
                card = r.get("noteCard", r) if isinstance(r, dict) else {}
                user = card.get("user", {})
                if isinstance(user, dict):
                    nick = user.get("nickname", user.get("nickName", ""))
                    uid = user.get("userId", user.get("user_id", ""))
                    if nick == "乌萨奇今天读paper了吗" and uid:
                        target_user_id = uid
                        target_nickname = nick
                        break

            if not target_user_id:
                # Try from noteCard.noteCard.user
                for r in results[:10]:
                    inner = r.get("noteCard", {})
                    if isinstance(inner, dict):
                        user = inner.get("user", {})
                        if isinstance(user, dict):
                            nick = user.get("nickname", user.get("nickName", ""))
                            uid = user.get("userId", user.get("user_id", ""))
                            if nick and uid:
                                target_user_id = uid
                                target_nickname = nick
                                break

            print(f"\nTarget user: {target_nickname}, ID: {target_user_id}")

            if target_user_id:
                # Step 2: Get user's posts
                print(f"\nFetching posts from user {target_user_id}...")
                posts = client.get_user_posts(target_user_id)
                print(f"Found {len(posts)} posts")

                for i, post in enumerate(posts[:15]):
                    if isinstance(post, dict):
                        nid = extract_note_id(post)
                        title = post.get("displayTitle", post.get("title", ""))
                        note_type = post.get("type", post.get("noteType", ""))
                        print(f"  [{i}] [{note_type}] {title[:80]} (ID:{nid})")

                        # Check for the Tencent post
                        if "腾讯" in title or "端到端" in title:
                            print(f"\n  *** FOUND TARGET POST ***")
                            print(f"  Note ID: {nid}")
                            xsec = post.get("xsecToken", post.get("xsec_token", ""))
                            print(f"  xsec_token: {str(xsec)[:50]}")

                            # Get detail
                            try:
                                detail = client.get_note_detail(nid, xsec)
                                note_data = detail.get("note", detail)
                                desc = note_data.get("desc", "")
                                print(f"  Description ({len(desc)} chars):")
                                print(f"    {desc[:800]}")
                                images = note_data.get("imageList", note_data.get("image_list", []))
                                print(f"  Images: {len(images)}")
                                for idx, img in enumerate(images):
                                    if isinstance(img, dict):
                                        url = img.get("url", "")
                                        print(f"    [{idx}] {url[:100]}")
                            except Exception as e:
                                print(f"  Error fetching detail: {e}")
        else:
            print("No results found.")

    playwright_browser.shutdown()

if __name__ == "__main__":
    main()

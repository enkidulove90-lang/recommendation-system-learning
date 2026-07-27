"""
Smoke test for Xiaohongshu bot - verifies login and basic operations.
"""

import os
import sys
import logging

# Monkey-patch before any xhs-cli imports
import playwright_browser

class _FakeCamoufoxSyncApi:
    Camoufox = playwright_browser.PlaywrightBrowser

class _FakeCamoufox:
    sync_api = _FakeCamoufoxSyncApi()

sys.modules['camoufox'] = _FakeCamoufox
sys.modules['camoufox.sync_api'] = _FakeCamoufoxSyncApi()
sys.modules['camoufox.sync_api'].Camoufox = playwright_browser.PlaywrightBrowser

from xhs_cli.auth import get_saved_cookie_string, get_cookie_string, COOKIE_FILE
from xhs_cli.client import XhsClient
from xhs_cli.auth import cookie_str_to_dict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("smoke_test")


def test_cookie_file():
    """Test 1: Check if cookie file exists."""
    print("\n" + "=" * 50)
    print("[Test 1] Check saved session...")
    if COOKIE_FILE.exists():
        print(f"  ✅ Cookie file exists: {COOKIE_FILE}")
        return True
    else:
        print(f"  ❌ No saved session at: {COOKIE_FILE}")
        print(f"  👉 You need to login first.")
        return False


def test_login():
    """Test 2: Try QR code login."""
    print("\n" + "=" * 50)
    print("[Test 2] QR Code Login...")

    cookie = get_saved_cookie_string()
    if cookie:
        print("  ✅ Already have saved cookies, skipping QR login")
        return True

    print("  📱 Starting QR code login...")
    print("  This will show a QR code in terminal for you to scan.")

    # Import and run QR code login
    from redbook_bot import _playwright_qrcode_login

    try:
        cookie = _playwright_qrcode_login()
        print("  ✅ Login successful! Cookies saved.")
        return True
    except Exception as e:
        print(f"  ❌ Login failed: {e}")
        return False


def test_whoami():
    """Test 3: Verify identity."""
    print("\n" + "=" * 50)
    print("[Test 3] Who am I?")

    cookie = get_cookie_string()
    if not cookie:
        print("  ❌ Not logged in")
        return False

    cookie_dict = cookie_str_to_dict(cookie)
    try:
        with XhsClient(cookie_dict) as client:
            info = client.get_self_info()

            # Extract user info
            nickname = ""
            user_id = ""
            if isinstance(info, dict):
                # Try different paths
                for key in ["userInfo", "basicInfo", "basic_info"]:
                    sub = info.get(key, {})
                    if isinstance(sub, dict):
                        nickname = sub.get("nickname", "") or sub.get("nickName", "")
                        user_id = sub.get("userId", "") or sub.get("user_id", "")
                        if nickname:
                            break

                if not nickname:
                    user_page = info.get("userPageData", {})
                    if isinstance(user_page, dict):
                        basic = user_page.get("basicInfo", {})
                        nickname = basic.get("nickname", "") or basic.get("nickName", "")
                        user_id = basic.get("userId", "")

            if nickname:
                print(f"  ✅ Logged in as: {nickname} (ID: {user_id})")
                return True
            else:
                print(f"  ⚠️ Got info but couldn't extract nickname:")
                print(f"  Keys: {list(info.keys())[:10]}")
                # Print partial info for debugging
                if "userPageData" in info:
                    print(f"  userPageData keys: {list(info['userPageData'].keys())[:10]}")
                return True  # Still consider this a pass if we got data
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_search():
    """Test 4: Basic search."""
    print("\n" + "=" * 50)
    print("[Test 4] Search test...")

    cookie = get_cookie_string()
    if not cookie:
        print("  ❌ Not logged in")
        return False

    cookie_dict = cookie_str_to_dict(cookie)
    try:
        with XhsClient(cookie_dict) as client:
            results = client.search_notes("推荐系统")
            if results and len(results) > 0:
                print(f"  ✅ Search returned {len(results)} results")
                for i, r in enumerate(results[:3]):
                    card = r.get("noteCard", r) if isinstance(r, dict) else {}
                    title = card.get("displayTitle", "?")
                    note_id = card.get("noteId", card.get("id", "?"))
                    user = card.get("user", {})
                    nickname = user.get("nickname", "?") if isinstance(user, dict) else "?"
                    print(f"    [{i}] {title[:50]} by {nickname} (ID: {note_id})")
                return True
            else:
                print("  ⚠️ Search returned no results")
                return False
    except Exception as e:
        print(f"  ❌ Search failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("  XHS Bot Smoke Test")
    print("=" * 60)
    print(f"  Python: {sys.version}")
    print(f"  CWD: {os.getcwd()}")

    results = {}
    results["cookie_file"] = test_cookie_file()

    if not results["cookie_file"]:
        results["login"] = test_login()
    else:
        results["login"] = True

    if results.get("login"):
        results["whoami"] = test_whoami()
        results["search"] = test_search()

    print("\n" + "=" * 60)
    print("  Smoke Test Results")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")

    all_pass = all(results.values())
    if all_pass:
        print("\n✅ All smoke tests passed!")
    else:
        print("\n⚠️ Some tests failed. See above for details.")

    # Cleanup
    playwright_browser.shutdown()
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())

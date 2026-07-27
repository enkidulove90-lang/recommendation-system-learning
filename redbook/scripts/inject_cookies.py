"""
Extract Xiaohongshu cookies from Chrome browser and save them
in xhs-cli format (~/.xhs-cli/cookies.json).

Usage: python inject_cookies.py
- Close Chrome before running for best results.
- Run as admin if encountering decryption errors.
"""

import json
import sys
from pathlib import Path

COOKIE_DOMAIN = ".xiaohongshu.com"
COOKIE_FILE_PATH = Path.home() / ".xhs-cli" / "cookies.json"

# Key cookie names that xhs-cli expects
REQUIRED_NAMES = {"a1", "web_session"}
EXTRA_NAMES = {"webId", "web_session_sec", "id_token", "gid", "websectiga",
               "sec_poison_id", "xsecappid", "abRequestId", "webBuild", "loadts"}


def extract_and_save_cookies():
    """Extract cookies from Chrome and save in xhs-cli format."""
    print(f"Extracting cookies for domain '{COOKIE_DOMAIN}' from Chrome...")

    try:
        import browser_cookie3
    except ImportError:
        print("ERROR: browser-cookie3 not installed. Run: pip install browser-cookie3")
        return False

    # Try multiple browsers in order
    browsers = [
        ("Chrome", lambda: browser_cookie3.chrome(domain_name=COOKIE_DOMAIN)),
        ("Edge", lambda: browser_cookie3.edge(domain_name=COOKIE_DOMAIN)),
        ("Brave", lambda: browser_cookie3.brave(domain_name=COOKIE_DOMAIN)),
        ("Firefox", lambda: browser_cookie3.firefox(domain_name=COOKIE_DOMAIN)),
    ]

    cookies_dict = {}
    source_browser = None

    for name, loader in browsers:
        try:
            cj = loader()
            for cookie in cj:
                if cookie.name in REQUIRED_NAMES or cookie.name in EXTRA_NAMES:
                    cookies_dict[cookie.name] = cookie.value
            if REQUIRED_NAMES.issubset(cookies_dict.keys()):
                source_browser = name
                break
            else:
                cookies_dict = {}  # reset if incomplete
        except Exception as e:
            print(f"  {name}: failed - {e}")
            continue

    if not source_browser:
        print("\nERROR: Could not extract required cookies (a1, web_session).")
        print("Make sure:")
        print("  1. You are logged into xiaohongshu.com in Chrome/Edge")
        print("  2. All browser windows are closed")
        print("  3. Run as Administrator if decryption fails")
        return False

    print(f"  Extracted {len(cookies_dict)} cookies from {source_browser}")
    print(f"  Key cookies: {[k for k in cookies_dict if k in REQUIRED_NAMES]}")

    # Save in xhs-cli format: {"cookies": {...}}
    COOKIE_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

    data = {"cookies": cookies_dict}
    with open(COOKIE_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Set file permissions (owner-only on Unix)
    try:
        COOKIE_FILE_PATH.chmod(0o600)
    except (OSError, AttributeError):
        pass  # Windows doesn't support chmod

    print(f"\nCookies saved to: {COOKIE_FILE_PATH}")
    return True


if __name__ == "__main__":
    success = extract_and_save_cookies()
    sys.exit(0 if success else 1)

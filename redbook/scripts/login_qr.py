"""
Standalone QR code login for Xiaohongshu using Playwright Chromium.
Displays QR code in terminal, user scans with app, cookies are saved.

Usage: python login_qr.py
"""

import json
import sys
import time
from pathlib import Path

import playwright_browser

# xhs-cli constants
CONFIG_DIR = Path.home() / ".xhs-cli"
COOKIE_FILE = CONFIG_DIR / "cookies.json"
REQUIRED_COOKIES = {"a1", "web_session"}
BROWSER_EXPORT_COOKIE_NAMES = (
    "a1", "webId", "web_session", "web_session_sec",
    "id_token", "websectiga", "sec_poison_id",
    "xsecappid", "gid", "abRequestId", "webBuild", "loadts",
)

LOGIN_URL = "https://www.xiaohongshu.com/login"
QR_CREATE_ENDPOINT = "/api/sns/web/v1/login/qrcode/create"
QR_STATUS_ENDPOINT = "/api/sns/web/v1/login/qrcode/status"
QR_USERINFO_ENDPOINT = "/api/qrcode/userinfo"


def display_qr_terminal(qr_text: str):
    """Display QR code as terminal block art."""
    try:
        import qrcode
        qr = qrcode.QRCode(border=0)
        qr.add_data(qr_text)
        qr.make(fit=True)
        matrix = qr.get_matrix()
        if not matrix:
            print(f"QR URL: {qr_text}")
            return

        border = 2
        width = len(matrix[0]) + border * 2
        padded = [[False] * width for _ in range(border)]
        for row in matrix:
            padded.append(([False] * border) + row + ([False] * border))
        padded.extend([[False] * width for _ in range(border)])

        chars = {
            (False, False): " ",
            (True, False): "▀",   # upper half block
            (False, True): "▄",    # lower half block
            (True, True): "█",     # full block
        }
        lines = []
        for y in range(0, len(padded), 2):
            top = padded[y]
            bottom = padded[y + 1] if y + 1 < len(padded) else [False] * width
            line = "".join(chars[(top[x], bottom[x])] for x in range(width))
            lines.append(line)
        print("\n".join(lines))
    except ImportError:
        print(f"QR URL: {qr_text}")


def save_cookies_to_file(cookies: dict):
    """Save cookies in xhs-cli format."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data = {"cookies": cookies}
    COOKIE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    try:
        COOKIE_FILE.chmod(0o600)
    except (OSError, AttributeError):
        pass
    print(f"Cookies saved to: {COOKIE_FILE}")


def qrcode_login():
    """Interactive QR code login flow."""
    print("=" * 60)
    print("  Xiaohongshu QR Code Login")
    print("=" * 60)
    print()

    with playwright_browser.PlaywrightBrowser(headless=True) as browser:
        page = browser.new_page()

        # Monitor QR scan status
        state = {"last_status": -1, "scanned": False}

        def handle_response(response):
            if QR_USERINFO_ENDPOINT in response.url:
                try:
                    payload = response.json()
                    data = payload.get("data", payload)
                    code_status = int(data.get("codeStatus", -1))
                    if code_status != state["last_status"]:
                        state["last_status"] = code_status
                        if code_status == 1:
                            print("[QR] Scanned! Waiting for confirmation on phone...")
                            state["scanned"] = True
                        elif code_status == 2:
                            print("[QR] Login confirmed!")
                except Exception:
                    pass

        page.on("response", handle_response)

        # Step 1: Navigate to login page and get QR code
        print("Loading login page...")
        try:
            with page.expect_response(
                lambda r: QR_CREATE_ENDPOINT in r.url and r.request.method == "POST",
                timeout=20_000,
            ) as qr_info:
                page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=20_000)
        except Exception as e:
            print(f"ERROR: Failed to load login page: {e}")
            print("The site might be unreachable or blocked.")
            return False

        qr_response = qr_info.value
        qr_data = qr_response.json()
        qr_payload = qr_data.get("data", qr_data)
        qr_url = qr_payload.get("url", "").strip()

        if not qr_url:
            print(f"ERROR: No QR URL in response")
            return False

        # Step 2: Display QR code
        print()
        print("Scan the QR code below with your Xiaohongshu app:")
        print()
        display_qr_terminal(qr_url)
        print()
        print("Waiting for scan (4 minute timeout)...")
        print("  1. Open Xiaohongshu app on your phone")
        print("  2. Tap the scan icon (top-right corner)")
        print("  3. Scan the QR code above")
        print("  4. Confirm login on your phone")
        print()

        # Step 3: Wait for QR status completion
        try:
            with page.expect_response(
                lambda r: QR_STATUS_ENDPOINT in r.url and r.request.method == "GET",
                timeout=240_000,
            ) as completion_info:
                pass
        except Exception:
            print("ERROR: QR login timed out (4 minutes). Try again.")
            return False

        # Step 4: Wait for session to stabilize
        try:
            page.wait_for_url("**/explore*", timeout=8_000)
        except Exception:
            pass
        time.sleep(2)

        # Step 5: Extract cookies
        completion_data = completion_info.value.json()
        completion_data = completion_data.get("data", completion_data)

        raw_cookies = page.context.cookies()
        cookies = {}
        for entry in raw_cookies:
            name = entry.get("name")
            value = entry.get("value")
            domain = entry.get("domain", "")
            if (isinstance(name, str) and isinstance(value, str)
                    and name in BROWSER_EXPORT_COOKIE_NAMES
                    and "xiaohongshu.com" in domain):
                cookies[name] = value

        # Add web_session from login response if missing
        login_info = completion_data.get("login_info", {}) or {}
        session = login_info.get("session") or completion_data.get("session")
        secure_session = login_info.get("secure_session") or completion_data.get("secure_session")
        if isinstance(session, str) and session:
            cookies["web_session"] = session
        if isinstance(secure_session, str) and secure_session:
            cookies["web_session_sec"] = secure_session

        if not REQUIRED_COOKIES.issubset(cookies.keys()):
            print(f"ERROR: Incomplete cookies: {sorted(cookies.keys())}")
            print(f"Required: {REQUIRED_COOKIES}")
            return False

        # Step 6: Save cookies
        save_cookies_to_file(cookies)
        print(f"Login successful! ({len(cookies)} cookies saved)")
        return True


if __name__ == "__main__":
    success = qrcode_login()
    playwright_browser.shutdown()
    sys.exit(0 if success else 1)

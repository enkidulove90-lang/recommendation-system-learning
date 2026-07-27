"""
Xiaohongshu (小红书) bot using Playwright Chromium.

Capabilities:
- QR code login with session persistence
- Search users and posts
- Read post details (text + images)
- Publish image posts
"""

from __future__ import annotations

import json
import logging
import os
import random
import re
import sys
import time
from pathlib import Path
from typing import Any

# Patch camoufox BEFORE any xhs-cli imports
# We replace camoufox.sync_api.Camoufox with our Playwright browser
import importlib

import playwright_browser

# Create a fake camoufox.sync_api module
class _FakeCamoufoxSyncApi:
    """Fake module that replaces camoufox.sync_api."""
    Camoufox = playwright_browser.PlaywrightBrowser

class _FakeCamoufox:
    sync_api = _FakeCamoufoxSyncApi()

# Register fake modules BEFORE importing xhs_cli
sys.modules['camoufox'] = _FakeCamoufox
sys.modules['camoufox.sync_api'] = _FakeCamoufoxSyncApi()
sys.modules['camoufox.sync_api'].Camoufox = playwright_browser.PlaywrightBrowser

# Now it's safe to import xhs_cli modules
from xhs_cli.auth import (
    COOKIE_FILE, CONFIG_DIR, REQUIRED_COOKIES,
    get_cookie_string, get_saved_cookie_string,
    save_cookies, clear_cookies, cookie_str_to_dict,
    _browser_assisted_qrcode_login,
)
from xhs_cli.client import XhsClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("redbook_bot")


# ============================================================
# QR Code Login (override to use Playwright instead of camoufox)
# ============================================================

# Override the auth module's qrcode_login to use our browser
import xhs_cli.auth as auth_module

def _playwright_qrcode_login() -> str:
    """Login via QR code using Playwright Chromium."""
    from playwright_browser import PlaywrightBrowser

    QR_CREATE_ENDPOINT = "/api/sns/web/v1/login/qrcode/create"
    QR_USERINFO_ENDPOINT = "/api/qrcode/userinfo"
    QR_STATUS_ENDPOINT = "/api/sns/web/v1/login/qrcode/status"
    LOGIN_URL = "https://www.xiaohongshu.com/login"

    print("🔑 Starting QR code login (Playwright Chromium)...")

    with PlaywrightBrowser(headless=True) as browser:
        page = browser.new_page()
        state = {"last_status": -1}

        def _handle_response(response) -> None:
            if QR_USERINFO_ENDPOINT not in response.url:
                return
            try:
                payload = response.json()
                data = payload.get("data", payload)
            except Exception:
                return

            code_status = int(data.get("codeStatus", -1))
            if code_status == state["last_status"]:
                return
            state["last_status"] = code_status

            if code_status == 1:
                print("📲 Scanned! Waiting for confirmation...")
            elif code_status == 2:
                print("✅ Login confirmed!")

        page.on("response", _handle_response)

        try:
            with page.expect_response(
                lambda response: (
                    QR_CREATE_ENDPOINT in response.url
                    and response.request.method == "POST"
                ),
                timeout=20_000,
            ) as qr_response_info:
                page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=20_000)
        except Exception as exc:
            raise RuntimeError(f"Failed to load Xiaohongshu login page: {exc}")

        qr_data = qr_response_info.value.json()
        qr_payload = qr_data.get("data", qr_data)
        qr_url = str(qr_payload.get("url", "")).strip()
        if not qr_url:
            raise RuntimeError(f"QR login did not return a QR URL: {qr_payload}")

        print("\n📱 Scan the QR code below with the Xiaohongshu app:\n")
        _display_qr_text(qr_url)
        print("\n⏳ Waiting for QR code scan (4 minute timeout)...")

        try:
            with page.expect_response(
                lambda response: (
                    QR_STATUS_ENDPOINT in response.url
                    and response.request.method == "GET"
                ),
                timeout=240_000,
            ) as completion_info:
                pass
        except Exception as exc:
            raise RuntimeError("QR code login timed out after 4 minutes") from exc

        completion_response = completion_info.value
        completion_data = completion_response.json()
        completion_data = completion_data.get("data", completion_data)

        # Wait for session to settle
        try:
            page.wait_for_url("**/explore*", timeout=5_000)
        except Exception:
            pass
        time.sleep(2)

        # Extract cookies
        raw_cookies = page.context.cookies()
        cookies = _normalize_cookies(raw_cookies)

        login_info = completion_data.get("login_info", {}) or {}
        session = login_info.get("session") or completion_data.get("session")
        secure_session = login_info.get("secure_session") or completion_data.get("secure_session")
        if isinstance(session, str) and session:
            cookies["web_session"] = session
        if isinstance(secure_session, str) and secure_session:
            cookies["web_session_sec"] = secure_session

        if not REQUIRED_COOKIES.issubset(cookies.keys()):
            raise RuntimeError(
                "QR login succeeded, but exported cookies were incomplete: "
                f"keys={', '.join(sorted(cookies.keys()))}"
            )

        cookie_str = auth_module._dict_to_cookie_str(cookies)
        save_cookies(cookie_str)
        return cookie_str


def _normalize_cookies(raw_cookies: list[dict]) -> dict[str, str]:
    """Normalize browser cookies to our storage format."""
    from xhs_cli.auth import BROWSER_EXPORT_COOKIE_NAMES
    cookies: dict[str, str] = {}
    for entry in raw_cookies:
        name = entry.get("name")
        value = entry.get("value")
        domain = entry.get("domain", "")
        if not isinstance(name, str) or not isinstance(value, str):
            continue
        if name not in BROWSER_EXPORT_COOKIE_NAMES:
            continue
        if not isinstance(domain, str) or "xiaohongshu.com" not in domain:
            continue
        cookies[name] = value
    return cookies


def _display_qr_text(qr_text: str) -> bool:
    """Display QR code as terminal text art."""
    try:
        import qrcode
    except ImportError:
        print(f"QR URL: {qr_text}")
        return False

    try:
        qr = qrcode.QRCode(border=0)
        qr.add_data(qr_text)
        qr.make(fit=True)
        matrix = qr.get_matrix()
        if not matrix:
            return False

        border = 2
        width = len(matrix[0]) + border * 2
        padded = [[False] * width for _ in range(border)]
        for row in matrix:
            padded.append(([False] * border) + row + ([False] * border))
        padded.extend([[False] * width for _ in range(border)])

        chars = {
            (False, False): " ",
            (True, False): "▀",
            (False, True): "▄",
            (True, True): "█",
        }

        lines = []
        for y in range(0, len(padded), 2):
            top = padded[y]
            bottom = padded[y + 1] if y + 1 < len(padded) else [False] * width
            line = "".join(chars[(top[x], bottom[x])] for x in range(width))
            lines.append(line)

        print("\n".join(lines))
        return True
    except Exception:
        print(f"QR URL: {qr_text}")
        return False


# Monkey-patch the auth module's qrcode_login
auth_module.qrcode_login = _playwright_qrcode_login
auth_module._browser_assisted_qrcode_login = _playwright_qrcode_login


# ============================================================
# High-level bot functions
# ============================================================

def ensure_login() -> bool:
    """Ensure we have a valid login session. Returns True if logged in."""
    cookie = get_saved_cookie_string()
    if cookie:
        print("✅ Found saved login session")
        return True

    print("❌ No saved session found. Starting QR code login...")
    print("📱 Please scan the QR code with your Xiaohongshu app.")
    try:
        cookie = _playwright_qrcode_login()
        print("✅ Login successful!")
        return True
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False


def search_user_by_name(keyword: str) -> list[dict]:
    """Search for users by keyword (name or小红书号)."""
    cookie = get_cookie_string()
    if not cookie:
        raise RuntimeError("Not logged in")

    cookie_dict = cookie_str_to_dict(cookie)
    with XhsClient(cookie_dict) as client:
        results = client.search_notes(keyword)
        return results


def get_user_posts(user_id: str) -> list[dict]:
    """Get all posts from a specific user."""
    cookie = get_cookie_string()
    if not cookie:
        raise RuntimeError("Not logged in")

    cookie_dict = cookie_str_to_dict(cookie)
    with XhsClient(cookie_dict) as client:
        return client.get_user_posts(user_id)


def get_note_detail(note_id: str, xsec_token: str = "") -> dict:
    """Get detailed content of a note."""
    cookie = get_cookie_string()
    if not cookie:
        raise RuntimeError("Not logged in")

    cookie_dict = cookie_str_to_dict(cookie)
    with XhsClient(cookie_dict) as client:
        return client.get_note_detail(note_id, xsec_token)


def publish_note(title: str, image_paths: list[str], content: str = "") -> dict:
    """Publish a new note with images and text."""
    cookie = get_cookie_string()
    if not cookie:
        raise RuntimeError("Not logged in")

    # Verify images exist
    for path in image_paths:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Image not found: {path}")

    cookie_dict = cookie_str_to_dict(cookie)
    with XhsClient(cookie_dict) as client:
        result = client.publish_note(title, image_paths, content, return_detail=True)
        return result


def get_self_info() -> dict:
    """Get current logged-in user info."""
    cookie = get_cookie_string()
    if not cookie:
        raise RuntimeError("Not logged in")

    cookie_dict = cookie_str_to_dict(cookie)
    with XhsClient(cookie_dict) as client:
        return client.get_self_info()


# ============================================================
# Image selection helper
# ============================================================

def get_image_paths_from_paper(paper_dir: str, image_hashes: list[str]) -> list[str]:
    """Get absolute paths for selected images from a paper directory."""
    images_dir = os.path.join(paper_dir, "images")
    paths = []
    for h in image_hashes:
        p = os.path.join(images_dir, f"{h}.jpg")
        if os.path.exists(p):
            paths.append(p)
        else:
            logger.warning(f"Image not found: {p}")
    return paths


# ============================================================
# Post content generation
# ============================================================

def generate_post_content(summary_path: str) -> dict:
    """Generate post title and content from a paper summary.

    Returns dict with: title, content, tags
    """
    with open(summary_path, 'r', encoding='utf-8') as f:
        summary_text = f.read()

    # Parse the summary
    lines = summary_text.strip().split('\n')

    # Extract paper title
    title_line = ""
    en_title = ""
    arxiv_id = ""
    for line in lines:
        line = line.strip()
        if line.startswith('# ') and not line.startswith('## '):
            title_line = line[2:].strip()
        if line.startswith('**英文标题**'):
            en_title = line.split('**:', 1)[-1].strip() if '**:' in line else line.split('**', 2)[-1].strip()
        if line.startswith('**arXiv ID**'):
            arxiv_id = line.split('**:', 1)[-1].strip() if '**:' in line else line.split('**', 2)[-1].strip()

    # Build post content in the style of "乌萨奇今天读paper了吗"
    # Common format: Title with emoji, key contributions, source info

    post_title = f"📄 {title_line}" if title_line else "📄 今日论文分享"

    # Extract key sections
    contributions = ""
    innovations = ""
    methodology = ""
    benchmarks = ""
    results = ""
    takeaways = ""

    in_section = None
    section_text = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('## 主要贡献'):
            in_section = 'contributions'
            continue
        elif stripped.startswith('## 创新点'):
            if in_section == 'contributions':
                contributions = '\n'.join(section_text).strip()
            in_section = 'innovations'
            section_text = []
            continue
        elif stripped.startswith('## 方法论'):
            if in_section == 'innovations':
                innovations = '\n'.join(section_text).strip()
            in_section = 'methodology'
            section_text = []
            continue
        elif stripped.startswith('## Benchmark'):
            if in_section == 'methodology':
                methodology = '\n'.join(section_text).strip()
            in_section = 'benchmarks'
            section_text = []
            continue
        elif stripped.startswith('## 实验效果'):
            if in_section == 'benchmarks':
                benchmarks = '\n'.join(section_text).strip()
            in_section = 'results'
            section_text = []
            continue
        elif stripped.startswith('## 对推荐系统'):
            if in_section == 'results':
                results = '\n'.join(section_text).strip()
            in_section = 'takeaways'
            section_text = []
            continue
        elif stripped.startswith('---') or stripped.startswith('*由 '):
            if in_section == 'takeaways':
                takeaways = '\n'.join(section_text).strip()
            in_section = None
            continue

        if in_section and stripped and not stripped.startswith('#'):
            section_text.append(stripped)

    # Build the post content
    post_content_parts = []

    # Intro
    post_content_parts.append(f"今日论文速递 📖")
    post_content_parts.append(f"论文标题：{en_title}")
    if arxiv_id:
        post_content_parts.append(f"arXiv：{arxiv_id}")
    post_content_parts.append("")

    # Core contributions
    if contributions:
        post_content_parts.append("🔑 核心贡献：")
        post_content_parts.append(contributions[:500])
        post_content_parts.append("")

    # Innovations
    if innovations:
        post_content_parts.append("💡 创新点：")
        # Truncate each point
        for line in innovations.split('\n')[:5]:
            if line.strip():
                post_content_parts.append(line.strip()[:200])
        post_content_parts.append("")

    # Methodology summary
    if methodology:
        post_content_parts.append("⚙️ 方法概述：")
        post_content_parts.append(methodology[:300])
        post_content_parts.append("")

    # Results
    if results:
        post_content_parts.append("📊 实验效果：")
        post_content_parts.append(results[:400])
        post_content_parts.append("")

    # Takeaways
    if takeaways:
        post_content_parts.append("🎯 对推荐系统的借鉴：")
        for line in takeaways.split('\n')[:4]:
            if line.strip():
                post_content_parts.append(line.strip()[:200])

    post_content_parts.append("")
    post_content_parts.append("#推荐系统 #LLM #多模态 #Agent #论文分享 #AI")

    post_content = '\n'.join(post_content_parts)

    return {
        "title": post_title[:20],  # xiaohongshu titles are limited to ~20 chars
        "content": post_content,
    }


# ============================================================
# Main orchestration
# ============================================================

def main():
    """Main entry point - orchestrates the full workflow."""
    print("=" * 60)
    print("  Xiaohongshu Paper Sharing Bot")
    print("=" * 60)

    # Step 1: Login
    print("\n[1/5] Checking login status...")
    if not ensure_login():
        print("❌ Cannot proceed without login.")
        sys.exit(1)

    # Step 2: Search for target user
    print("\n[2/5] Searching for target user...")
    try:
        # Search for the user by their小红书号
        results = search_user_by_name("乌萨奇今天读paper了吗")
        if results:
            print(f"Found {len(results)} search results")
            for i, r in enumerate(results[:3]):
                note_card = r.get("noteCard", r)
                user_info = note_card.get("user", {})
                print(f"  [{i}] Note: {note_card.get('displayTitle', '?'):.50s} | "
                      f"User: {user_info.get('nickname', '?')} | "
                      f"ID: {note_card.get('noteId', note_card.get('id', '?'))}")

            # Find the target post: "腾讯：端到端强化多模态视觉思维链"
            target_post = None
            for r in results:
                note_card = r.get("noteCard", r)
                title = note_card.get("displayTitle", "")
                if "腾讯" in title or "端到端" in title or "视觉思维链" in title:
                    target_post = note_card
                    break

            if target_post:
                note_id = target_post.get("noteId", target_post.get("id", ""))
                print(f"\n🎯 Found target post! ID: {note_id}")
                print(f"   Title: {target_post.get('displayTitle', '?')}")
                print(f"   Type: {target_post.get('type', '?')}")

                # Get the note detail
                detail = get_note_detail(note_id)
                note_data = detail.get("note", {})
                print(f"   Content: {(note_data.get('desc', '') or note_data.get('title', ''))[:200]}")
                print(f"   Images: {len(note_data.get('imageList', []))} images")
            else:
                print("\n⚠️ Target post not found in first page of results.")
                print("Search results:")
                for r in results[:5]:
                    note_card = r.get("noteCard", r)
                    print(f"   - {note_card.get('displayTitle', '?')[:80]}")
        else:
            print("No results found.")
    except Exception as e:
        print(f"⚠️ Search failed: {e}")
        import traceback
        traceback.print_exc()

    # Step 3: Prepare post content
    print("\n[3/5] Preparing post content...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    summary_path = os.path.join(
        base_dir, "data", "summaries",
        "2607.07108_多模态记忆增强的推荐智能体协作_summary.md"
    )
    paper_dir = os.path.join(
        base_dir, "data", "parsed",
        "2607.07108_多模态记忆增强的推荐智能体协作"
    )

    post_data = generate_post_content(summary_path)
    print(f"   Title: {post_data['title']}")
    print(f"   Content: {len(post_data['content'])} chars")

    # Step 4: Select images
    print("\n[4/5] Selecting images...")
    # Select architecture images (not formula images)
    selected_images = [
        "98edc660de228c64ca9f1fa89d330eb2d5da132f1ae5e3f3e3c4828baaf36ad2.jpg",  # Figure 1: Architecture Comparison
        "e02c05bb31ecbd466fc7f94c9a49f7785e8ae293062b7743720b68da8ba8c48d.jpg",  # Figure 2: MMEACR Framework Overview
        "6edeb0db2c0c406203dfaedcd9eec722c9dafc14ce5c2be420b0b8ad8b6675aa.jpg",  # Figure 3: Case Study Results
        "2c78718cef0428c9eb986d573dae74271c7b03fea7751776f47efe9aa04ced9b.jpg",  # Figure 6: Query Template
        "fb67018f8bca96b1bb6322872a8a24f3a444b51fcb68b3335c1c75e243a5cfcb.jpg",  # Figure 8: Prompt Template
    ]

    image_paths = get_image_paths_from_paper(paper_dir, selected_images)
    print(f"   Selected {len(image_paths)} images:")
    for p in image_paths:
        print(f"   - {os.path.basename(p)}")

    # Step 5: Publish
    print("\n[5/5] Publishing post...")
    print("⚠️  This will publish to your account! Type 'yes' to confirm:")
    confirm = input("> ").strip().lower()
    if confirm != 'yes':
        print("❌ Cancelled.")
        sys.exit(0)

    try:
        result = publish_note(
            title=post_data["title"],
            image_paths=image_paths,
            content=post_data["content"],
        )
        if isinstance(result, dict):
            if result.get("success"):
                print(f"✅ Post published successfully!")
                print(f"   Note ID: {result.get('note_id', '?')}")
                print(f"   URL: {result.get('url', '?')}")
            else:
                print(f"⚠️ Publish result unclear: {result}")
        else:
            print(f"✅ Publish returned: {result}")
    except Exception as e:
        print(f"❌ Publish failed: {e}")
        import traceback
        traceback.print_exc()

    # Cleanup
    playwright_browser.shutdown()
    print("\n✅ Done!")


if __name__ == "__main__":
    main()

"""
Playwright Chromium replacement for camoufox.sync_api.Camoufox.

This module provides a drop-in replacement for camoufox's Camoufox context manager
using Playwright's Chromium, which is already installed locally.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any

from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

# Global playwright instance (shared across sessions)
_playwright = None


def _get_playwright():
    global _playwright
    if _playwright is None:
        _playwright = sync_playwright().start()
    return _playwright


class PlaywrightBrowser:
    """Mimics camoufox.sync_api.Camoufox context manager interface.

    Usage:
        with PlaywrightBrowser(headless=True) as browser:
            page = browser.new_page()
            ...
    """

    def __init__(self, headless: bool = True, **kwargs):
        self._headless = headless
        self._kwargs = kwargs
        self._pw = None
        self._browser = None
        self._context = None
        # For compatibility with camoufox API
        self.browser = None
        self.context = None

    def __enter__(self):
        self._pw = _get_playwright()

        import os, socket

        # Resolve creator.xiaohongshu.com IP (Playwright DNS has issues with this domain)
        creator_ip = ""
        try:
            creator_ip = socket.getaddrinfo('creator.xiaohongshu.com', 443,
                                           socket.AF_INET, socket.SOCK_STREAM)[0][4][0]
        except Exception:
            creator_ip = "113.137.55.111"  # fallback

        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--ignore-certificate-errors",
            "--disable-web-security",
            # DNS fix: map creator domain to direct IP (Chromium can't resolve it)
            f"--host-resolver-rules=MAP creator.xiaohongshu.com {creator_ip}",
        ]

        # Use system proxy if configured
        for proxy_env in ['HTTPS_PROXY', 'https_proxy', 'HTTP_PROXY', 'http_proxy']:
            proxy_url = os.environ.get(proxy_env, '')
            if proxy_url:
                launch_args.append(f'--proxy-server={proxy_url}')
                break

        self._browser = self._pw.chromium.launch(
            headless=self._headless,
            args=launch_args,
        )
        self._context = self._browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/148.0.0.0 Safari/537.36"
            ),
        )
        # Inject stealth scripts to hide automation
        self._context.add_init_script("""
            // Overwrite the navigator.webdriver property
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            // Overwrite chrome object
            window.chrome = { runtime: {} };
            // Overwrite permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
            );
            // Overwrite plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            // Overwrite languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en'],
            });
        """)
        self.browser = self._context  # for new_page() compatibility
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._context:
            try:
                self._context.close()
            except Exception:
                pass
        if self._browser:
            try:
                self._browser.close()
            except Exception:
                pass
        return False

    def new_page(self):
        """Create a new page (compatible with camoufox API)."""
        if self._context is None:
            raise RuntimeError("Browser not started. Use as context manager.")
        return self._context.new_page()


def shutdown():
    """Shutdown global playwright instance."""
    global _playwright
    if _playwright:
        try:
            _playwright.stop()
        except Exception:
            pass
        _playwright = None

"""
Python client for OpenCLI daemon CDP bridge.

Protocol reverse-engineered from:
  daemon-client.js + page.js + daemon-transport.js

Usage:
  from opencli_cdp import OpenCliCdp
  cdp = OpenCliCdp()
  cdp.navigate("https://creator.xiaohongshu.com/publish/publish")
  result = cdp.exec("document.title")
"""
import requests, json, time, uuid

DAEMON = "http://127.0.0.1:19825"
HEADERS = {"X-OpenCLI": "1", "Content-Type": "application/json"}

class OpenCliCdp:
    """Client for OpenCLI daemon's CDP bridge."""

    def __init__(self, context_id=None, verbose=True):
        self.context_id = context_id
        self.session = None
        self.page = None  # targetId
        self.verbose = verbose
        self._get_context()

    def _get_context(self):
        """Get contextId from daemon status."""
        if self.context_id:
            return
        try:
            r = requests.get(f"{DAEMON}/status", headers=HEADERS, timeout=3)
            data = r.json()
            profiles = data.get("profiles", [])
            if profiles:
                self.context_id = profiles[0].get("contextId", "")
            if self.verbose:
                print(f"[CDP] contextId={self.context_id}, ext={data.get('extensionVersion','?')}")
        except Exception as e:
            raise RuntimeError(f"Daemon not reachable: {e}")

    def _cmd(self, action, params=None, timeout=120):
        """Send command to daemon, return result."""
        from datetime import timezone as _tz
        cmd_id = f"py_{int(time.time()*1000)}_{action}"
        body = {
            "id": cmd_id,
            "action": action,
            "surface": "browser",
            "timeout": timeout,
            **(params or {}),
        }
        # session goes via params (handled by bind action) or from self.session
        if "session" not in body:
            body["session"] = self.session
        if self.context_id:
            body["contextId"] = self.context_id
        if self.page:
            body["page"] = self.page

        if self.verbose:
            print(f"[CDP] -> {action}: {json.dumps({k:v for k,v in body.items() if k not in ('deadlineAt','code')}, ensure_ascii=False)[:200]}")

        r = requests.post(f"{DAEMON}/command", json=body, headers=HEADERS,
                         timeout=timeout + 10)
        result = r.json()

        if not result.get("ok"):
            err = result.get("error", str(result)[:200])
            raise RuntimeError(f"Command {action} failed: {err}")

        # Update page identity if returned
        if result.get("page"):
            self.page = result["page"]

        return result

    def bind(self, session_name="py-auto"):
        """Bind to browser session. Session name is arbitrary."""
        # Session must be non-empty — daemon creates it on first use
        result = self._cmd("bind", {"session": session_name})
        self.session = session_name
        if self.verbose:
            print(f"[CDP] Session: {self.session}")
        return self.session

    def navigate(self, url):
        """Navigate to URL. Returns page identity."""
        if not self.session:
            self.bind()
        result = self._cmd("navigate", {"url": url})
        if result.get("page"):
            self.page = result["page"]
            if self.verbose:
                print(f"[CDP] Page: {self.page}")
        return self.page

    def exec(self, code, timeout=60):
        """Execute JavaScript in the current page."""
        if not self.session:
            self.bind()
        result = self._cmd("exec", {"code": code}, timeout=timeout)
        # Result data may be in result.data or as a string
        data = result.get("data", result.get("result", ""))
        return data

    def tabs(self, op="list", url=None):
        """Tab operations: list, open, close."""
        params = {"op": op}
        if url:
            params["url"] = url
        return self._cmd("tabs", params)

    def cookies(self):
        """Get cookies for current page."""
        return self._cmd("cookies")


def main():
    """Test: connect, navigate to creator, execute JS."""
    cdp = OpenCliCdp()

    # Bind session
    cdp.bind()

    # Navigate to creator publish page
    print("\n=== Navigating to creator ===")
    cdp.navigate("https://creator.xiaohongshu.com/publish/publish?from=menu_left&target=image")
    import time; time.sleep(3)  # wait for page load

    # Execute JS to find page elements
    print("\n=== Executing JS ===")
    js = """
    (function() {
        const buttons = Array.from(document.querySelectorAll('button, [role="button"]'))
            .filter(b => b.offsetParent !== null)
            .slice(0, 10)
            .map(b => (b.textContent || '').trim().slice(0, 60));
        const fileInputs = document.querySelectorAll('input[type="file"]');
        return JSON.stringify({
            url: location.href,
            title: document.title.slice(0, 80),
            buttons: buttons,
            fileInputs: fileInputs.length,
            addComponentBtns: buttons.filter(b => b.includes('添加') || b.includes('组件')),
        });
    })()
    """
    result = cdp.exec(js)
    print(result[:1000] if isinstance(result, str) else json.dumps(result, ensure_ascii=False)[:1000])


if __name__ == "__main__":
    main()

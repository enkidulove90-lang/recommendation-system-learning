"""
Use OpenCLI daemon to send CDP commands for PDF upload automation.

Architecture:
    Python script → HTTP POST /command → Daemon(19825) → Extension → Chrome CDP
"""
import requests, json, time, sys, os

DAEMON = "http://127.0.0.1:19825"
HEADERS = {"X-OpenCLI": "1", "Content-Type": "application/json"}
PDF = r"c:\Users\xu.yan1\papers\recommendation-system-learning\data\parsed\2604.08011\SSR_paper.pdf"

def send_cdp(tab_id, method, params=None, timeout=60):
    """Send a CDP command through the daemon to the browser tab."""
    cmd_id = f"cdp_{int(time.time()*1000)}_{method.replace('.','_')}"
    body = {
        "id": cmd_id,
        "type": "cdp",
        "tabId": tab_id,
        "method": method,
        "params": params or {},
        "timeout": timeout,
    }
    resp = requests.post(f"{DAEMON}/command", json=body, headers=HEADERS, timeout=timeout + 10)
    return resp.json()

def main():
    # First, find the active tab
    print("Finding active creator tab...")
    # Open creator publish page (this should use the existing tab or open new one)
    # For now, use the draft list page

    # Get daemon status to verify extension is connected
    r = requests.get(f"{DAEMON}/status", headers=HEADERS, timeout=5)
    status = r.json()
    print(f"Daemon status: {json.dumps(status, ensure_ascii=False, indent=2)[:500]}")

    if not status.get("extensionConnected"):
        print("ERROR: Extension not connected. Open Chrome with OpenCLI extension installed.")
        return

    # Try to navigate to the creator page via the daemon
    print("\nNavigating to creator publish page...")
    tab_info = status.get("activeTab", status.get("tabs", [{}])[0] if status.get("tabs") else {})
    tab_id = tab_info.get("id", tab_info.get("tabId", 0))
    print(f"Active tab: {tab_id}")

    if tab_id:
        # Navigate to creator page
        result = send_cdp(tab_id, "Page.navigate", {
            "url": "https://creator.xiaohongshu.com/publish/publish?from=menu_left&target=image"
        })
        print(f"Navigate result: {json.dumps(result, ensure_ascii=False)[:300]}")
        time.sleep(3)

        # Execute JS to find file upload elements
        js = """
        (function() {
            // Find all buttons
            const buttons = Array.from(document.querySelectorAll('button, [role="button"], span[class*="add"]'));
            const info = buttons.slice(0, 10).map(b => ({
                text: (b.textContent || '').trim().slice(0, 50),
                class: (b.className || '').slice(0, 50),
                visible: b.offsetParent !== null
            }));
            return JSON.stringify({buttons: info, url: location.href});
        })()
        """
        result = send_cdp(tab_id, "Runtime.evaluate", {"expression": js, "returnByValue": True})
        print(f"Page info: {json.dumps(result, ensure_ascii=False)[:800]}")
    else:
        print("No active tab found. Please open creator.xiaohongshu.com in Chrome first.")

if __name__ == "__main__":
    main()

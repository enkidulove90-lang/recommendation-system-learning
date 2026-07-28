"""
Use CDP (Chrome DevTools Protocol) to automate adding a PDF file
to an existing draft in the Xiaohongshu creator page.

Connects to the existing Chrome instance via OpenCLI's managed browser.
"""
import json, time, websocket, os, sys

# The OpenCLI daemon exposes CDP via its extension WebSocket.
# We connect via localhost:19825 which is the daemon port.
# The daemon forwards CDP commands to the browser extension.

DAEMON_URL = "ws://localhost:19825"
PDF_PATH = r"c:\Users\xu.yan1\papers\recommendation-system-learning\data\parsed\2604.08011\SSR_paper.pdf"

def send_cdp(ws, method, params=None):
    """Send a CDP command and wait for response."""
    msg_id = int(time.time() * 1000)
    payload = {
        "id": msg_id,
        "method": method,
        "params": params or {}
    }
    ws.send(json.dumps(payload))
    # Wait for response
    while True:
        resp = json.loads(ws.recv())
        if resp.get("id") == msg_id:
            return resp
        # Check for events
        if "method" in resp:
            print(f"  Event: {resp['method'][:80]}")

def main():
    print("Connecting to Chrome CDP via OpenCLI daemon...")
    ws = websocket.create_connection(DAEMON_URL)
    print(f"Connected!")

    # Navigate to creator draft page
    print("\nNavigating to creator publish page...")
    send_cdp(ws, "Page.navigate", {
        "url": "https://creator.xiaohongshu.com/publish/publish?from=menu_left&target=image"
    })
    time.sleep(3)

    # Execute JavaScript to trigger file upload
    print("Looking for file upload component...")

    # The creator page has a Vue component for file upload.
    # Try clicking "添加组件" button and selecting "文件"
    js_find_upload = """
    (function() {
        // Find all buttons that might be "添加组件"
        const buttons = Array.from(document.querySelectorAll('button, [role="button"], .btn, [class*="add"]'));
        const addBtn = buttons.find(b =>
            b.textContent.includes('添加组件') ||
            b.textContent.includes('添加') ||
            b.getAttribute('aria-label')?.includes('添加')
        );
        if (addBtn) {
            addBtn.click();
            return 'clicked add button';
        }

        // Try finding file input directly
        const fileInput = document.querySelector('input[type="file"]');
        if (fileInput) {
            return 'found file input: ' + (fileInput.accept || 'no accept attr');
        }

        return 'no button or input found. Buttons: ' + buttons.slice(0,5).map(b => b.textContent.trim()).join(', ');
    })()
    """

    result = send_cdp(ws, "Runtime.evaluate", {"expression": js_find_upload})
    print(f"Result: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}")

    ws.close()

if __name__ == "__main__":
    main()

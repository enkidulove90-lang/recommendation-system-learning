"""
CDP: Use browser's native file upload to handle PDF + collect API automatically.

Strategy: Instead of calling COS + collect API manually (which needs protobuf),
we use CDP to find the hidden file input for "添加组件→文件" and set its files.
The browser's own JS handles the upload + collect flow.
"""
import requests, json, time, os

DAEMON = "http://127.0.0.1:19825"
HEADERS = {"X-OpenCLI": "1", "Content-Type": "application/json"}
CONTEXT = "z47nyea3"
SESSION = "py-pdf-upload-v2"
PDF = r"c:\Users\xu.yan1\papers\recommendation-system-learning\data\parsed\2604.08011\SSR_paper.pdf"

def cmd(action, params=None, timeout=60):
    body = {
        "id": f"pdf_{int(time.time()*1000)}_{action}",
        "action": action, "surface": "browser",
        "session": SESSION, "contextId": CONTEXT,
        "timeout": timeout,
        "deadlineAt": int(time.time() * 1000) + timeout * 1000,
        **(params or {}),
    }
    r = requests.post(f"{DAEMON}/command", json=body, headers=HEADERS, timeout=timeout+10)
    return r.json()

def exec_js(code, timeout=60):
    result = cmd("exec", {"code": code}, timeout=timeout)
    return result.get("data", result.get("result", ""))

# Step 1: Navigate to the draft editing page
print("[1/4] Loading draft editor...")
r = cmd("navigate", {
    "url": "https://creator.xiaohongshu.com/publish/publish?from=homepage&target=image&useDraft=true",
    "session": SESSION,
}, timeout=30)
print(f"  URL: {r.get('data',{}).get('url','?')[:100]}")
time.sleep(5)

# Step 2: Find ALL file inputs (including hidden ones for 添加组件→文件)
print("\n[2/4] Scanning for file inputs...")
js_scan = """
(function() {
    const inputs = document.querySelectorAll('input[type="file"]');
    const results = [];
    inputs.forEach(function(el, i) {
        const parent = el.closest('[class*="upload"], [class*="add"], [class*="component"], div, span');
        const parentText = parent ? (parent.textContent || '').trim().slice(0, 80) : '';
        results.push({
            idx: i,
            accept: el.getAttribute('accept') || '(any)',
            visible: el.offsetParent !== null,
            parentTag: parent ? parent.tagName : '?',
            parentClass: (parent?.className || '').slice(0, 60),
            parentText: parentText,
        });
    });
    return JSON.stringify(results);
})()
"""
result = exec_js(js_scan)
data = json.loads(result) if isinstance(result, str) else result
print(f"  Found {len(data)} file inputs:")
for inp in data:
    print(f"    [{inp['idx']}] accept={inp['accept'][:40]} visible={inp['visible']} parentTag={inp['parentTag']}")
    if inp['parentText']:
        print(f"         parent: [{inp['parentText'][:80]}]")

# If no suitable file input found, try clicking various UI elements
print("\n[3/4] Done scanning.")
print("[4/4] Review output above. If a pdf-accepting input is found, we can set it via CDP.")

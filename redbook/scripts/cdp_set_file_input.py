"""
CDP: Set file input to PDF via DOM.setFileInputFiles.
The key insight: use CDP's DOM domain to find and inject files into
ANY file input, bypassing the accept attribute restriction.
"""
import requests, json, time

DAEMON = "http://127.0.0.1:19825"
HEADERS = {"X-OpenCLI": "1", "Content-Type": "application/json"}
CONTEXT = "z47nyea3"
SESSION = "py-set-file"
PDF = r"c:\Users\xu.yan1\papers\recommendation-system-learning\data\parsed\2604.08011\SSR_paper.pdf"

def cmd(action, params=None, timeout=60):
    body = {
        "id": f"sf_{int(time.time()*1000)}_{action}",
        "action": action, "surface": "browser",
        "session": SESSION, "contextId": CONTEXT,
        "timeout": timeout,
        "deadlineAt": int(time.time() * 1000) + timeout * 1000,
        **(params or {}),
    }
    r = requests.post(f"{DAEMON}/command", json=body, headers=HEADERS, timeout=timeout+10)
    return r.json()

# Step 1: Bind to fresh session
print("[1] Binding session...")
r = cmd("bind", {"session": SESSION})
page_id = r.get("page", "")
print(f"  Page: {page_id}")

# Step 2: First, find the EXISTING file input using CDP DOM domain
print("[2] Getting document root...")
# Use exec to get the file input via JS (more reliable than DOM.querySelector via CDP)
js = """
(function() {
    const inputs = document.querySelectorAll('input[type="file"]');
    const results = [];
    inputs.forEach(function(el, i) {
        results.push({
            idx: i,
            accept: el.accept || '(any)',
            visible: el.offsetParent !== null,
            id: el.id || '',
            name: el.name || '',
            // Get the closest container with text
            containerText: (el.closest('[class*="upload"], [class*="publish"], form, div')?.textContent || '').trim().slice(0, 100),
        });
    });
    return JSON.stringify(results);
})()
"""
r = cmd("exec", {"code": js, "page": page_id})
data = json.loads(r.get("data", "[]"))
print(f"  File inputs: {len(data)}")
for d in data:
    print(f"    [{d['idx']}] accept={d['accept'][:40]} visible={d['visible']}")

# Step 3: Try DOM.setFileInputFiles via exec (using browser's internal API)
# This is a workaround: execute JS that creates a file input, sets it, and triggers change
print("\n[3] Injecting PDF into file input via JS...")
js_inject = """
(async function() {
    // Strategy: create a hidden file input or use the existing one
    // Then use the browser's native file handling

    // Find any file input - the browser will accept our file regardless of accept attr
    const input = document.querySelector('input[type="file"]');
    if (!input) return 'no file input found';

    // Create a DataTransfer with our file to bypass accept restriction
    // But we can't create File objects from CDP JS (no local file access)

    // Alternative: try to find the 添加组件 button and click it first
    // Search ALL text nodes for "添加组件" or "组件" or "文件"
    const treeWalker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const matches = [];
    let node;
    while (node = treeWalker.nextNode()) {
        const text = node.textContent;
        if (text.includes('组件') || text.includes('添加') || text.includes('文件')) {
            const el = node.parentElement;
            if (el && el.offsetParent !== null && text.trim().length < 30) {
                matches.push({
                    text: text.trim().slice(0, 30),
                    tag: el.tagName,
                    class: (el.className||'').slice(0, 40),
                    rect: el.getBoundingClientRect() ? {
                        x: Math.round(el.getBoundingClientRect().x),
                        y: Math.round(el.getBoundingClientRect().y),
                    } : null,
                });
            }
        }
    }

    if (matches.length === 0) {
        // Last resort: check iframe
        const iframes = document.querySelectorAll('iframe');
        let iframeText = '';
        iframes.forEach(function(f) {
            try { iframeText += f.contentDocument?.body?.textContent?.slice(0, 200) || ''; } catch(e) {}
        });
        return JSON.stringify({error: 'no matches found', iframeCount: iframes.length, iframeText: iframeText.slice(0, 200)});
    }

    return JSON.stringify(matches.slice(0, 15));
})()
"""
r = cmd("exec", {"code": js_inject, "page": page_id}, timeout=30)
result = r.get("data", "")
print(f"  Result: {result[:1500]}")

"""
CDP: Find and click "添加组件" → select "文件" → upload PDF.
"""
import requests, json, time

DAEMON = "http://127.0.0.1:19825"
HEADERS = {"X-OpenCLI": "1", "Content-Type": "application/json"}
CONTEXT = "z47nyea3"
SESSION = "py-add-component"
PDF = r"c:\Users\xu.yan1\papers\recommendation-system-learning\data\parsed\2604.08011\SSR_paper.pdf"

def cmd(action, params=None, timeout=60):
    body = {
        "id": f"cmp_{int(time.time()*1000)}_{action}",
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

# Bind session
cmd("bind", {"session": SESSION})

# Step 1: Find ALL elements that might be "添加组件" or contain "文件"
js = """
(function() {
    const results = [];
    // Find by text content
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
    let node;
    while (node = walker.nextNode()) {
        if (node.offsetParent === null) continue;
        const text = (node.textContent || '').trim();
        const tag = node.tagName.toLowerCase();

        if (text.includes('添加组件') || text.includes('文件') || text.includes('组件') || text.includes('附件')) {
            results.push({
                tag: tag,
                text: text.slice(0, 80),
                class: (node.className || '').slice(0, 60),
                id: node.id || '',
                rect: node.getBoundingClientRect ? {
                    x: Math.round(node.getBoundingClientRect().x),
                    y: Math.round(node.getBoundingClientRect().y),
                    w: Math.round(node.getBoundingClientRect().width),
                    h: Math.round(node.getBoundingClientRect().height),
                } : null,
            });
        }
        // Don't go into children if we already found the text at this level
        if (results.length > 20) break;
    }
    return JSON.stringify(results.slice(0, 15));
})()
"""
result = exec_js(js)
data = json.loads(result) if isinstance(result, str) else result
print("=== Elements matching '添加组件' or '文件' ===")
for el in data:
    print(f"  <{el['tag']}> [{el['text'][:60]}] class={el['class'][:40]} rect={el['rect']}")

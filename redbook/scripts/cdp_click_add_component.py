"""
CDP: Click "添加组件" tab, then upload PDF.
The creator page has tabs: 上传视频 | 上传图片 | 写文字 | 添加组件 | 草稿箱(N)
"""
import requests, json, time

DAEMON = "http://127.0.0.1:19825"
HEADERS = {"X-OpenCLI": "1", "Content-Type": "application/json"}
CONTEXT = "z47nyea3"
SESSION = "py-click-add"

def cmd(action, params=None, timeout=60):
    body = {
        "id": f"clk_{int(time.time()*1000)}_{action}",
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

# Bind
cmd("bind", {"session": SESSION})

# Step 1: Find the tabs in the creator header
js_find_tabs = """
(function() {
    // Look for the tab bar with 上传视频/上传图片/写文字/添加组件/草稿箱
    const tabs = [];
    // Search all clickable items
    document.querySelectorAll('span, div, button, a, li').forEach(el => {
        const text = (el.textContent || '').trim();
        if (text === '添加组件' || text === '草稿箱' || text === '上传图片' || text === '写文字') {
            const tag = el.tagName.toLowerCase();
            // Get the precise clickable element
            let clickTarget = el;
            // Try the parent if this is a span inside a button
            const parent = el.parentElement;
            if (parent && (parent.onclick || parent.getAttribute('role') === 'tab' || parent.className.includes('tab'))) {
                clickTarget = parent;
            }
            tabs.push({
                text: text,
                tag: tag,
                clickTag: clickTarget.tagName.toLowerCase(),
                class: (el.className || '').slice(0, 60),
                parentClass: (parent?.className || '').slice(0, 60),
                rect: el.getBoundingClientRect ? {
                    x: Math.round(el.getBoundingClientRect().x),
                    y: Math.round(el.getBoundingClientRect().y),
                } : null,
                selector: el.id ? '#'+el.id : null,
            });
        }
    });
    return JSON.stringify(tabs);
})()
"""
result = exec_js(js_find_tabs)
data = json.loads(result) if isinstance(result, str) else result
print("=== Tab elements ===")
for el in data:
    print(f"  [{el['text']}] <{el['tag']}> class={el['class'][:40]} rect={el['rect']}")

# Step 2: Click "添加组件" tab
js_click = """
(function() {
    // Find the "添加组件" span/div and click its parent
    const allEls = document.querySelectorAll('span, div');
    for (const el of allEls) {
        if (el.textContent.trim() === '添加组件' && el.offsetParent !== null) {
            // Try clicking the parent first
            const parent = el.parentElement;
            if (parent && parent.offsetParent !== null) {
                parent.click();
                return 'clicked parent: ' + parent.tagName + '.' + (parent.className||'').slice(0,30);
            }
            el.click();
            return 'clicked el: ' + el.tagName + '.' + (el.className||'').slice(0,30);
        }
    }
    return '添加组件 not found';
})();
"""
result = exec_js(js_click)
print(f"\nClick result: {result}")
time.sleep(2)

# Step 3: After clicking "添加组件", find "文件" option
js_find_file = """
(function() {
    // Look for "文件" option in the component menu
    const items = [];
    document.querySelectorAll('span, div, li, button').forEach(el => {
        const text = (el.textContent || '').trim();
        if (text === '文件' || text.includes('文件') || text === '附件') {
            items.push({
                text: text.slice(0, 40),
                tag: el.tagName.toLowerCase(),
                class: (el.className||'').slice(0, 60),
                visible: el.offsetParent !== null,
            });
        }
    });
    return JSON.stringify(items);
})();
"""
result = exec_js(js_find_file)
data = json.loads(result) if isinstance(result, str) else result
print(f"\n=== '文件' elements ===")
for el in data:
    print(f"  [{el['text']}] <{el['tag']}> class={el['class'][:40]} visible={el['visible']}")

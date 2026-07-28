"""
CDP: Find the tab nav, click "添加组件", select "文件", upload PDF.

Strategy: use XPath/attribute matching since encoding is garbled.
"""
import requests, json, time, os

DAEMON = "http://127.0.0.1:19825"
HEADERS = {"X-OpenCLI": "1", "Content-Type": "application/json"}
CONTEXT = "z47nyea3"
SESSION = "py-final-upload"
PDF = r"c:\Users\xu.yan1\papers\recommendation-system-learning\data\parsed\2604.08011\SSR_paper.pdf"

def cmd(action, params=None, timeout=60):
    body = {
        "id": f"fin_{int(time.time()*1000)}_{action}",
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

# Step 1: Find nav items by matching the tab structure
# The tabs are rendered as spans inside a nav bar
js = """
(function() {
    // Try finding by aria-role or known class patterns
    const results = {};

    // Method 1: Look for role="tablist" or similar
    const tablist = document.querySelector('[role="tablist"], [class*="tab-bar"], [class*="nav-bar"], [class*="header-tabs"]');
    if (tablist) {
        results.tablist = {tag: tablist.tagName, class: (tablist.className||'').slice(0, 60)};
        const tabs = tablist.querySelectorAll('[role="tab"], [class*="tab-item"], span, div');
        const tabInfo = [];
        tabs.forEach(t => {
            const text = (t.textContent||'').trim();
            if (text.length < 20 && text.length > 0) {
                tabInfo.push({text: text.slice(0,20), tag: t.tagName, class: (t.className||'').slice(0,40)});
            }
        });
        results.tabs = tabInfo.slice(0, 10);
    }

    // Method 2: Find by looking for the container that has all the tab text
    // The body text showed: "上传视频上传图片写文字添加组件草稿箱(2)"
    // This is likely inside a flex container
    const containers = document.querySelectorAll('.upload-wrapper *, .publish-vue-container *, .microapp-container *');
    for (const el of containers) {
        const text = (el.textContent||'').trim();
        if (text.includes('上传视频') || text.includes('添加组件')) {
            // Check children
            const children = Array.from(el.children).map(c => ({
                tag: c.tagName.toLowerCase(),
                text: (c.textContent||'').trim().slice(0, 30),
                class: (c.className||'').slice(0, 50),
            }));
            if (children.length >= 3 && children.length <= 10) {
                results.foundContainer = {
                    parentTag: el.tagName,
                    parentClass: (el.className||'').slice(0, 60),
                    children: children,
                };
                break;
            }
        }
    }

    return JSON.stringify(results);
})()
"""
result = exec_js(js)
data = json.loads(result) if isinstance(result, str) else result
print(json.dumps(data, ensure_ascii=False, indent=2)[:1500])

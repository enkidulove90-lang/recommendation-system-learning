"""
CDP: Inject PDF into hidden file input, trigger upload + collect flow.

The page has a hidden <input type="file" accept=".pdf,.doc,.docx,.ppt,.pptx">
at index [2]. Setting files on it via CDP should trigger the browser's
native change event handler → upload → collect → attach to note.
"""
import requests, json, time

DAEMON = "http://127.0.0.1:19825"
HEADERS = {"X-OpenCLI": "1", "Content-Type": "application/json"}
CONTEXT = "z47nyea3"
SESSION = "py-trigger-pdf"
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

# Bind
r = cmd("bind", {"session": SESSION})
page = r.get("page", "")
print(f"Page: {page}")

# Step 1: Make the PDF file input visible and set files via JS
# Since DOM.setFileInputFiles might not be available through the daemon action,
# we use a JS workaround: create a visible file input, trigger click, then
# the browser's own change handler processes the upload.
js = """
(async function() {
    // Find the hidden PDF-accepting file input
    const inputs = document.querySelectorAll('input[type="file"]');
    let pdfInput = null;
    inputs.forEach(function(el) {
        if (el.accept && el.accept.includes('.pdf')) {
            pdfInput = el;
        }
    });

    if (!pdfInput) return 'no pdf input found';

    // Make it visible temporarily
    const origDisplay = pdfInput.style.display;
    pdfInput.style.display = 'block';
    pdfInput.style.position = 'fixed';
    pdfInput.style.top = '0';
    pdfInput.style.left = '0';
    pdfInput.style.zIndex = '99999';

    // We cannot create File objects in CDP JS directly.
    // Instead, we need to find what triggers the file input to appear.
    // The PDF input appears after clicking "添加组件→文件".

    // Strategy: find the parent container and look for the click handler
    // that reveals this input
    let parent = pdfInput.parentElement;
    let depth = 0;
    while (parent && depth < 10) {
        const cls = (parent.className || '').slice(0, 50);
        const tag = parent.tagName;
        // Check for Vue event handlers
        const listeners = parent.__vueParentComponent || parent.__vue__;
        if (listeners) {
            return JSON.stringify({
                found: 'vue component',
                tag: tag,
                class: cls,
                depth: depth,
            });
        }
        parent = parent.parentElement;
        depth++;
    }

    // Restore
    pdfInput.style.display = origDisplay;

    // Return info about the input's context
    const container = pdfInput.closest('[class*="upload"], [class*="component"], [class*="add"], form, div');
    return JSON.stringify({
        status: 'input found but need trigger',
        accept: pdfInput.accept,
        parentTag: pdfInput.parentElement?.tagName,
        parentClass: (pdfInput.parentElement?.className || '').slice(0, 60),
        containerTag: container?.tagName,
        containerClass: (container?.className || '').slice(0, 80),
        path: pdfInput.parentElement?.parentElement?.parentElement?.className?.slice(0, 60),
    });
})()
"""
r = cmd("exec", {"code": js, "page": page}, timeout=30)
print(f"PDF input analysis: {r.get('data', '')[:1000]}")

# Step 2: Try a different approach - find the Vue app and call its upload method
js_vue = """
(function() {
    // Try to access Vue app instance
    const appEl = document.querySelector('#app, [data-v-app], .publish-vue-container');
    if (!appEl) return 'no vue app found';

    const vueApp = appEl.__vue_app__;
    if (!vueApp) return 'no __vue_app__';

    // Try to find the upload/collect related store or component
    const info = {
        hasApp: true,
        config: Object.keys(vueApp.config || {}).slice(0, 10),
    };

    // Check Pinia stores
    if (vueApp.config?.globalProperties?.$pinia) {
        const stores = vueApp.config.globalProperties.$pinia._s;
        const storeKeys = Object.keys(stores || {});
        info.piniaStores = storeKeys.slice(0, 10);

        // Look for a store that might handle uploads
        storeKeys.forEach(function(k) {
            const state = stores[k]?.$state || stores[k];
            const keys = Object.keys(state || {}).slice(0, 10);
            if (keys.some(function(k2) { return k2.includes('file') || k2.includes('upload') || k2.includes('doc'); })) {
                info.uploadStore = {name: k, keys: keys};
            }
        });
    }

    return JSON.stringify(info);
})()
"""
r = cmd("exec", {"code": js_vue, "page": page}, timeout=30)
print(f"\nVue app info: {r.get('data', '')[:1000]}")

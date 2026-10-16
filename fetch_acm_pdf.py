# -*- coding: utf-8 -*-
"""用 OpenCLI 的真实 Chrome 会话从 ACM DL 取开放获取 PDF（绕开对爬虫的 403）。

思路：
1. 真实浏览器打开 ACM 文章页（过 Cloudflare）；
2. 在该页上下文里 fetch 官方 PDF（带 cookie），把字节挂到 window.__pdf；
3. 分块 eval 取回 base64，Python 落盘成 PDF。

用法：python fetch_acm_pdf.py <doi> <输出pdf路径> [session名]
例：  python fetch_acm_pdf.py 10.1145/3847662 data/parsed/sihg/10.1145_3847662.pdf acm
"""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

PROBE_JS = "JSON.stringify({title: document.title, url: location.href, body: document.body ? document.body.innerText.slice(0,300) : ''})"

STORE_JS = (
    "(async () => {"
    "  const r = await fetch(PDFURL, {credentials:'include'});"
    "  const ok = r.ok; const ct = r.headers.get('content-type') || '';"
    "  const b = await r.arrayBuffer();"
    "  window.__pdf = new Uint8Array(b);"
    "  const head = Array.from(window.__pdf.slice(0,5)).map(c=>String.fromCharCode(c)).join('');"
    "  return JSON.stringify({ok, status:r.status, ct, bytes:window.__pdf.length, head});"
    "})()"
)

CHUNK_JS = (
    "(function(off, len){"
    "  const v = window.__pdf.subarray(off, Math.min(off+len, window.__pdf.length));"
    "  let s=''; const CH=0x8000;"
    "  for (let i=0;i<v.length;i+=CH){ s += String.fromCharCode.apply(null, v.subarray(i,i+CH)); }"
    "  return btoa(s);"
    "})"
)


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    doi, out = sys.argv[1], Path(sys.argv[2])
    session = sys.argv[3] if len(sys.argv) > 3 else "acm"

    import os

    skip_open = os.environ.get("SKIP_OPEN") == "1"

    from redbook.infrastructure import opencli_runtime

    rt = opencli_runtime.resolve_runtime()
    art = f"https://dl.acm.org/doi/{doi}"
    pdf = f"https://dl.acm.org/doi/pdf/{doi}"

    def run(*parts, timeout=180):
        r = rt.run(*parts, timeout=timeout)
        return (r.stdout or "").strip(), r.returncode

    if skip_open:
        print("[1] skip open (SKIP_OPEN=1)，复用已有会话")
    else:
        print("[1] open", art)
        out_s, rc = run("browser", session, "open", art, "--window", "background", timeout=240)
        print("    rc=%s out=%s" % (rc, out_s[:200]))

    print("[2] probe page")
    out_s, rc = run("browser", session, "eval", PROBE_JS, timeout=120)
    print("    rc=%s %s" % (rc, out_s[:500]))

    print("[3] fetch PDF into window.__pdf")
    js = STORE_JS.replace("PDFURL", json.dumps(pdf))
    out_s, rc = run("browser", session, "eval", js, timeout=300)
    print("    rc=%s %s" % (rc, out_s[:400]))
    try:
        meta = json.loads(out_s)
    except Exception:
        print("!! 无法解析 fetch 结果，可能被拦截或需要登录")
        return 1
    if not meta.get("ok") or not meta.get("bytes"):
        print("!! fetch 未成功:", meta)
        return 1

    total = int(meta["bytes"])
    print("[4] downloading bytes:", total, "head=", meta.get("head"), "ct=", meta.get("ct"))

    chunk = 2 * 1024 * 1024          # base64 前原始字节
    buf = bytearray()
    off = 0
    while off < total:
        js = "%s(%d, %d)" % (CHUNK_JS, off, chunk)
        out_s, rc = run("browser", session, "eval", js, timeout=300)
        txt = out_s.strip()
        if txt.startswith('"') and txt.endswith('"'):
            txt = json.loads(txt)
        if not txt:
            print("!! 空分块 @", off)
            return 1
        buf += base64.b64decode(txt)
        off += chunk
        print("    %d / %d" % (len(buf), total))

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(bytes(buf))
    print("[5] saved", out, len(buf), "bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

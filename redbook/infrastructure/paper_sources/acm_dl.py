"""ACM DL 开放获取 PDF 抓取与 Cloudflare 放行探测。

由根目录 ``fetch_acm_pdf.py`` + ``acm_wait_pass.py`` 合并而来，与
``arxiv_source.py`` / ``openreview_source.py`` 同属 paper_sources 层。

思路（不要改成普通 requests：ACM 对爬虫直接 403）
------------------------------------------------
1. 用 OpenCLI 的真实 Chrome 会话打开文章页（带登录态、过 Cloudflare）；
2. 在该页上下文里 ``fetch`` 官方 PDF，字节挂到 ``window.__pdf``；
3. 分块 eval 取回 base64，Python 落盘。

CLI::

    python -m redbook.infrastructure.paper_sources.acm_dl fetch <doi> <out.pdf> [session]
    python -m redbook.infrastructure.paper_sources.acm_dl wait [session] [rounds] [gap]
"""
from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import sys
import time
from typing import Any, Sequence

PROBE_JS = "JSON.stringify({title: document.title, url: location.href, body: document.body ? document.body.innerText.slice(0,300) : ''})"
READY_JS = "JSON.stringify({title: document.title, url: location.href, ready: document.readyState, len: document.body ? document.body.innerText.length : 0})"

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


def resolve_runtime():
    from redbook.infrastructure import opencli_runtime
    return opencli_runtime.resolve_runtime()


def wait_for_cloudflare(session: str = "acm", rounds: int = 8, gap: float = 8.0,
                        runtime=None) -> dict[str, Any]:
    """反复探测 Cloudflare 挑战是否已放行；返回结构化结果，不靠人看控制台。"""
    rt = runtime or resolve_runtime()
    history: list[dict[str, Any]] = []
    for index in range(rounds):
        result = rt.run("browser", session, "eval", READY_JS, timeout=120)
        raw = (result.stdout or "").strip()
        passed = "challenge" not in raw.lower() and "just a moment" not in raw.lower()
        history.append({"round": index + 1, "rc": result.returncode, "output": raw[:260], "passed": passed})
        if passed and len(raw) > 60:
            return {"ok": True, "rounds": index + 1, "history": history}
        time.sleep(gap)
    return {"ok": False, "rounds": rounds, "history": history}


def fetch_acm_pdf(doi: str, output: str | Path, session: str = "acm", *,
                  skip_open: bool | None = None, runtime=None) -> dict[str, Any]:
    """从 ACM DL 取 PDF 并落盘；返回结构化回执（bytes / head / path）。"""
    rt = runtime or resolve_runtime()
    target = Path(output)
    article_url = f"https://dl.acm.org/doi/{doi}"
    pdf_url = f"https://dl.acm.org/doi/pdf/{doi}"
    if skip_open is None:
        skip_open = os.environ.get("SKIP_OPEN") == "1"

    def run(*parts, timeout: int = 180):
        result = rt.run(*parts, timeout=timeout)
        return (result.stdout or "").strip(), result.returncode

    steps: list[dict[str, Any]] = []
    if not skip_open:
        out, rc = run("browser", session, "open", article_url, "--window", "background", timeout=240)
        steps.append({"step": "open", "rc": rc, "output": out[:200]})
    out, rc = run("browser", session, "eval", PROBE_JS, timeout=120)
    steps.append({"step": "probe", "rc": rc, "output": out[:500]})

    out, rc = run("browser", session, "eval", STORE_JS.replace("PDFURL", json.dumps(pdf_url)), timeout=300)
    try:
        meta = json.loads(out)
    except (json.JSONDecodeError, TypeError):
        return {"ok": False, "error": "fetch result unparseable (blocked or login required)",
                "output": out[:400], "steps": steps}
    if not meta.get("ok") or not meta.get("bytes"):
        return {"ok": False, "error": "fetch did not succeed", "meta": meta, "steps": steps}

    total = int(meta["bytes"])
    chunk = 2 * 1024 * 1024
    buffer = bytearray()
    offset = 0
    while offset < total:
        out, rc = run("browser", session, "eval", "%s(%d, %d)" % (CHUNK_JS, offset, chunk), timeout=300)
        text = out.strip()
        if text.startswith('"') and text.endswith('"'):
            text = json.loads(text)
        if not text:
            return {"ok": False, "error": f"empty chunk at {offset}", "steps": steps}
        buffer += base64.b64decode(text)
        offset += chunk
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(bytes(buffer))
    return {
        "ok": True, "path": str(target), "bytes": len(buffer),
        "head": meta.get("head"), "content_type": meta.get("ct"), "steps": steps,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ACM DL PDF acquisition helpers")
    actions = parser.add_subparsers(dest="action", required=True)
    fetch = actions.add_parser("fetch")
    fetch.add_argument("doi")
    fetch.add_argument("output", type=Path)
    fetch.add_argument("session", nargs="?", default="acm")
    wait = actions.add_parser("wait")
    wait.add_argument("session", nargs="?", default="acm")
    wait.add_argument("rounds", nargs="?", type=int, default=8)
    wait.add_argument("gap", nargs="?", type=float, default=8.0)
    args = parser.parse_args(argv)
    if args.action == "fetch":
        result = fetch_acm_pdf(args.doi, args.output, args.session)
    else:
        result = wait_for_cloudflare(args.session, args.rounds, args.gap)
    print(json.dumps(result, ensure_ascii=False, indent=2)[:2000])
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

# -*- coding: utf-8 -*-
"""反复探测 Cloudflare 挑战是否已放行（配合 fetch_acm_pdf.py 使用）。

用法：python acm_wait_pass.py [session] [轮数] [间隔秒]
"""
from __future__ import annotations

import sys
import time

JS = "JSON.stringify({title: document.title, url: location.href, ready: document.readyState, len: document.body ? document.body.innerText.length : 0})"


def main() -> int:
    session = sys.argv[1] if len(sys.argv) > 1 else "acm"
    rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    gap = float(sys.argv[3]) if len(sys.argv) > 3 else 8.0

    from redbook.infrastructure import opencli_runtime

    rt = opencli_runtime.resolve_runtime()
    for i in range(rounds):
        r = rt.run("browser", session, "eval", JS, timeout=120)
        out = (r.stdout or "").strip()
        print("round %d: %s" % (i + 1, out[:260]), flush=True)
        low = out.lower()
        if "安全验证" not in out and "just a moment" not in low and "稍候" not in out and out:
            print("=> 挑战已过（页面标题不再是验证页）")
            return 0
        time.sleep(gap)
    print("=> 仍在挑战中")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

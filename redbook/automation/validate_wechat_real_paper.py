"""Validate the new 代码随想录-style WeChat skeleton on a REAL parsed paper.

The earlier ``validate_wechat_template.py`` ran the skeleton against a hand-mapped
non-paper post that lacked ``datasets`` / ``benchmark`` fields.  This script loads
a genuine 11-dimension summary (LightGCL 2302.08191) through the same
``load_assets`` path the production CLI uses, then renders + stages + publishes so
we can confirm the new skeleton renders REAL datasets/benchmark/innovations and the
whole thing still reaches the WeChat draft box end-to-end.
"""
from __future__ import annotations

import json
from pathlib import Path

from redbook.automation.paper_to_xhs import load_assets
from redbook.automation.paper_to_wechat import (
    render_article_body, render_wechat_article,
    build_package, _datasets_line,
    TITLE_MAX, BODY_MIN, BODY_MAX,
)
from redbook.automation.publishing import WeChatPublisher


PAPER_ID = "2302.08191"


def _checks(assets, body_markdown: str, wechat_body: str) -> list[str]:
    """Field-level assertions so a silent degradation is caught."""
    s = assets.summary
    out: list[str] = []

    ds_line = _datasets_line(s)
    out.append(f"[datasets] line = '{ds_line}'  -> {'OK' if 'Yelp' in ds_line and 'Tmall' in ds_line else 'MISSING'}")

    # WeChat-flavored body MUST NOT carry Markdown syntax that UEditor renders literally
    out.append(f"[wechat body 无 Markdown 残留] "
               f"** : {'OK' if '**' not in wechat_body else 'LEAK'}, "
               f"## : {'OK' if '##' not in wechat_body else 'LEAK'}")

    metrics = "/".join(str(m) for m in s.get("benchmark", {}).get("metrics", [])[:4])
    out.append(f"[§5 metrics 落到 wechat body] '{metrics}' -> "
               f"{'OK' if metrics in wechat_body else 'NOT FOUND'}")

    mr = s.get("benchmark", {}).get("main_results", "")
    has_number = any(k in wechat_body for k in ("提升10%", "提升16%", "提升23%", "0.0793"))
    out.append(f"[§2 main_results 去重后保留] {'OK' if has_number else 'DROPPED (可能误去重)'}")

    out.append(f"[limitations 清洁] {'OK' if '[阅读者判断]' not in wechat_body else 'LEAKED SCAFFOLD'}")

    title = assets.title_zh[:TITLE_MAX]
    out.append(f"[title len] {len(title)} (≤{TITLE_MAX}) -> {'OK' if len(title) <= TITLE_MAX else 'TOO LONG'}")
    out.append(f"[wechat body len] {len(wechat_body)} (范围 {BODY_MIN}-{BODY_MAX}) -> "
               f"{'OK' if BODY_MIN <= len(wechat_body) <= BODY_MAX else 'OUT OF RANGE'}")
    return out


def main() -> None:
    root = Path.cwd()
    assets = load_assets(PAPER_ID, root)

    print("=" * 72)
    print(f"STEP 1 — load_assets({PAPER_ID}) 真实 11 维摘要")
    print("=" * 72)
    print(f"parsed_dir : {assets.parsed_dir}")
    print(f"pdf_path   : {assets.pdf_path}")
    print(f"figures    : {len(assets.figures)} 条（图视觉描述）")
    print(f"title_zh   : {assets.title_zh}")

    print()
    print("=" * 72)
    print("STEP 2 — render_wechat_article（公众号纯文本：无 ** / ## / ---）")
    print("=" * 72)
    wechat_body = render_wechat_article(assets)
    print(wechat_body)

    print()
    print("=" * 72)
    print("STEP 2b — render_article_body（Markdown 源，仅作 audit 留存）前 500 字")
    print("=" * 72)
    print(render_article_body(assets)[:500])

    print()
    print("=" * 72)
    print("STEP 3 — 字段级校验")
    print("=" * 72)
    for line in _checks(assets, render_article_body(assets), wechat_body):
        print(" ", line)

    print()
    print("=" * 72)
    print("STEP 4 — build_package + WeChatPublisher.stage → publish（真实端到端）")
    print("=" * 72)
    package = build_package(assets, canonical_url=f"https://arxiv.org/abs/{PAPER_ID}")
    print(f"staged package: paper_id={package.paper_id} images={len(package.image_paths)} "
          f"title='{package.title}' body_chars={len(package.body_markdown)}")
    publisher = WeChatPublisher(root)
    staged = publisher.stage(package)
    print("stage:", json.dumps(staged, ensure_ascii=False)[:200])
    if not staged.get("ok"):
        print("STAGE FAILED:", staged)
        return
    result = publisher.publish(staged["staged_id"])
    print("publish result:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

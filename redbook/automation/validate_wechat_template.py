"""Validate the new 代码随想录-style WeChat skeleton end-to-end.

Feeds the crawled 代码随想录 post (data/weixin_crawl/代码随想录_再见Superpowers_结构.md)
through ``paper_to_wechat.render_article_body`` + the real ``WeChatPublisher``
stage→publish path, to confirm the WeChat end can produce a publishable post.

The post is not a parsed paper, so we build a ``PaperAssets`` populated with the
post's real content mapped onto the 11-dimension summary schema (the same field
names ``render_article_body`` consumes).  A placeholder cover image is borrowed
from an existing parsed paper so both the create-draft and HTML-fallback paths
have something to attach.
"""
from __future__ import annotations

import json
from pathlib import Path

from redbook.automation.paper_to_xhs import PaperAssets
from redbook.automation.paper_to_wechat import render_article_body, build_package, TITLE_MAX, BODY_MIN, BODY_MAX
from redbook.automation.publishing import WeChatPublisher


# --- 代码随想录《再见Superpowers》真实内容，映射到 11 维摘要 schema ------------ #
POST_SUMMARY = {
    "title_zh": "再见Superpowers!恭喜还没用这些skill的朋友们!现在不用学了!",
    "one_line_summary": (
        "GPT-5.6 后模型能力大涨，普通开发者没必要先装一大包 Agent Skill；"
        "默认顺序应反过来：先让模型直接做，做不好再补一个最小 Skill。"
    ),
    "problem_definition": {
        "task_type": "软件开发方法论 / Agent Skill 工程纪律",
        "input": "过去一年火爆的 Agent Skill 套件（如 Superpowers）",
    },
    "innovations": [
        {"point": "Superpowers 把开发拆成可自动触发的 Skill：澄清需求→设计→TDD→子Agent→验证，给模型装了一套外置工程纪律。"},
        {"point": "GPT-5.6 把『外置纪律』吃进了模型：更精简的系统 Prompt 让评测分数提高约 10%~15%，总 Token 减少 41%~66%，成本减少 33%~67%。"},
        {"point": "最先没必要的四类 Skill：只提醒模型认真一点 / 重复 Agent 原生能力 / 为所有任务强制同一套重流程 / 从来没有被评测过。"},
    ],
    "modules": [
        {"name": "外置工程纪律（brainstorm→plan→TDD→review）"},
        {"name": "最小 Skill 补丁（什么时候触发/读什么/执行什么/如何验收/何时停止）"},
    ],
    "training": {
        "loss": "（本文不训练模型，而是给出『先裸跑，再加最小 Skill』的五步法：定义结果→裸跑基线→只看可复现失败→补最小补丁→再跑同组任务对比）",
    },
    "benchmark": {
        "metrics": ["评测分数", "总Token", "成本"],
        "baselines": [],
        "main_results": (
            "OpenAI 官方内部评测：更精简的系统 Prompt 让评测分数提高约 10%~15%，"
            "总 Token 减少 41%~66%，成本减少 33%~67%。"
        ),
        "significance": "模型变强后，更多说明不一定带来更多能力，反而可能制造更多噪声。",
    },
    "limitations": (
        "模型能力的保质期太短，方法论会过期；不是所有 Skill 都该删——"
        "项目专属规则、确定性脚本、外部工具与连接、高风险流程仍值得保留。"
    ),
}


def _borrow_cover() -> tuple[Path, Path]:
    """Pick any existing parsed figure as a placeholder cover + its parsed dir."""
    hits = sorted(Path("data/parsed").glob("*/images/*.jpg"))
    if not hits:
        raise RuntimeError("no placeholder cover image available under data/parsed")
    img = hits[0]
    return img, img.parent.parent


def main() -> None:
    cover_img, parsed_dir = _borrow_cover()
    assets = PaperAssets(
        paper_id="weixin:代码随想录-再见Superpowers",
        summary=POST_SUMMARY,
        parsed_dir=parsed_dir,
        pdf_path=parsed_dir / "placeholder.pdf",  # 公众号无 PDF，仅占位
        figures=[{"image_file": cover_img.name, "figure_type": "other",
                  "description": "placeholder cover"}],
    )

    print("=" * 70)
    print("STEP 1 — render_article_body（新骨架：开场钩子→…→写在最后）")
    print("=" * 70)
    body = render_article_body(assets)
    print(body)
    print("-" * 70)
    print(f"标题(≤{TITLE_MAX}): {assets.title_zh[:TITLE_MAX]}  (len={len(assets.title_zh[:TITLE_MAX])})")
    print(f"正文长度: {len(body)}  (限制 {BODY_MIN}–{BODY_MAX})  ->",
          "OK" if BODY_MIN <= len(body) <= BODY_MAX else "OUT OF RANGE")
    print()

    print("=" * 70)
    print("STEP 2 — build_package + WeChatPublisher.stage → publish")
    print("=" * 70)
    package = build_package(assets, canonical_url="https://mp.weixin.qq.com/s/placeholder")
    publisher = WeChatPublisher(Path("data"))
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

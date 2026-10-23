from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_intake.adapters import NotionDraft, NotionGateway
from paper_intake.article import (
    PaperArticle,
    publication_year,
    render_article_markdown,
    validate_article,
)
from paper_intake.references import link_reference_titles


JOB_ID = "59f84ea0-d55a-4ec7-b637-c00967cbc3f8"
BUNDLE = ROOT / "data" / "workflow_state" / "paper_intake" / "remote" / JOB_ID
SOURCE_MARKDOWN = ROOT / "data" / "parsed" / "2603.00700_soda" / "2603.00700.md"


def figure(name: str, section: str, explanation: str) -> dict[str, str]:
    path = BUNDLE / "images" / name
    if not path.is_file():
        raise FileNotFoundError(path)
    return {
        "path": f"images/{name}",
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "section": section,
        "explanation": explanation,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Repair the published SODA article deterministically")
    parser.add_argument("--sync-notion", action="store_true")
    args = parser.parse_args()
    article_path = BUNDLE / "article.json"
    article = PaperArticle.model_validate_json(article_path.read_text(encoding="utf-8"))
    plain_references = [
        re.sub(r"\[([^\]]+)\]\(https?://[^)]+\)", r"\1", reference)
        for reference in article.article.references
    ]
    references = link_reference_titles(
        plain_references,
        SOURCE_MARKDOWN.read_text(encoding="utf-8"),
    )
    figures = [
        figure(
            "b8110e77b38098acf0f3884ce1d59cad2475cfc5ad16117b191db88eb55f513a.jpg",
            "method",
            "图中上路由分词器把目标物品映射为多层码本概率分布，下路由推荐器把用户历史映射为正、负分布；三者通过对称 KL 散度构造 SODA 对比损失，体现了分布级监督如何连接分词器与推荐器。",
        ),
        figure(
            "f70d3df34d238938976780b892c7ecc1aa47517daf7522c5257acd017f814dda.jpg",
            "experiments",
            "主结果表比较 Beauty、Pet 与 Upwork 上的传统模型和三种生成式主干。加粗列显示 SODA-T、SODA-L、SODA-E 相对各自主干在 Recall 与 NDCG 指标上的变化，用于检验框架跨数据集与跨主干的稳定性。",
        ),
        figure(
            "106564989fc42158a3116e3f65a46a44453d938235ab937072bef985c4b70222.jpg",
            "experiments",
            "消融表在 Beauty 数据集上分别移除负项、分布级损失与交替优化。各变体的 Recall 和 NDCG 均可与完整 SODA-T、SODA-L 直接对照，从而区分对比负样本、软分布监督和交替训练的贡献。",
        ),
    ]
    payload = article.model_dump()
    payload["article"]["references"] = references
    payload["figures"] = figures
    article = PaperArticle.model_validate(payload)
    result = validate_article(article, artifact_root=BUNDLE)
    if not result.publishable:
        raise RuntimeError("repair failed quality gate: " + ", ".join(result.issue_codes))
    article_path.write_text(article.model_dump_json(indent=2), encoding="utf-8")
    (BUNDLE / "article.md").write_text(render_article_markdown(article), encoding="utf-8")
    notion_page_id = ""
    if args.sync_notion:
        config = dotenv_values(ROOT / ".env")
        notion = NotionGateway(
            str(config.get("NOTION_TOKEN") or ""),
            str(config.get("NOTION_DATABASE_ID") or ""),
            proxy_url="http://127.0.0.1:7897",
        )
        page = notion.upsert_published(
            NotionDraft(
                arxiv_id=article.paper.canonical_id,
                title=article.paper.chinese_title or article.paper.title,
                slug=f"paper-{article.paper.canonical_id}",
                summary=article.article.introduction[:500],
                markdown=(BUNDLE / "article.md").read_text(encoding="utf-8"),
                figure_paths=tuple((BUNDLE / item.path).resolve() for item in article.figures),
                categories=tuple(article.classification.categories),
                tags=tuple(article.classification.tags),
                year=publication_year(article),
                venue_type=article.classification.venue_type,
                venue_name=article.classification.venue_name,
            )
        )
        notion_page_id = page.page_id
    print(
        json.dumps(
            {
                "job_id": JOB_ID,
                "figure_count": len(article.figures),
                "reference_count": len(article.article.references),
                "quality_issue_codes": result.issue_codes,
                "notion_page_id": notion_page_id,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

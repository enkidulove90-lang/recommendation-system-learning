from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_intake.adapters import DeepSeekArticleAdapter, NotionDraft, NotionGateway
from paper_intake.article import (
    PaperArticle,
    publication_year,
    render_article_markdown,
    validate_article,
)
from paper_intake.references import link_reference_titles


TAU_BUNDLE = ROOT / "data" / "workflow_state" / "paper_intake" / "remote" / "eef3a94b-094f-4c8b-843d-0eeb3ed40770"
TAU_SOURCE = ROOT / "data" / "parsed" / "2606.10156_tau_rec" / "2606.10156.md"
BONSAI_BUNDLE = ROOT / "data" / "workflow_state" / "paper_intake" / "cached" / "2607.16633"
BONSAI_SOURCE = ROOT / "data" / "parsed" / "2607.16633_bonsai" / "2607.16633.md"
BONSAI_VISUALS = ROOT / "data" / "parsed" / "2607.16633_bonsai" / "editorial_visuals"


@dataclass(frozen=True, slots=True)
class PreparedPaper:
    article: PaperArticle
    bundle: Path


def _plain_references(article: PaperArticle) -> list[str]:
    return [
        re.sub(r"\[([^\]]+)\]\(https?://[^)]+\)", r"\1", reference)
        for reference in article.article.references
    ]


def _normalize_tau_text(value: str) -> str:
    value = re.sub(r"\\passhat\{([^{}]+)\}", r"\\mathrm{pass}^{\1}", value)
    value = re.sub(
        r"\\texttt\{((?:\\[{}]|[^{}])*)\}",
        lambda match: "`" + match.group(1).replace(r"\_", "_").replace(r"\{", "{").replace(r"\}", "}") + "`",
        value,
    )
    return value


def repair_tau_article(article: PaperArticle, source_markdown: str, bundle: Path) -> PaperArticle:
    sections = article.article.model_copy(
        update={
            "introduction": _normalize_tau_text(article.article.introduction),
            "method": _normalize_tau_text(article.article.method),
            "experiments": _normalize_tau_text(article.article.experiments),
            "conclusion": _normalize_tau_text(article.article.conclusion),
            "references": link_reference_titles(_plain_references(article), source_markdown),
        }
    )
    figures = []
    for figure in article.figures:
        path = bundle / figure.path
        with Image.open(path) as image:
            width, height = image.size
        if width >= 320 and height >= 120:
            figures.append(figure.model_copy(update={"explanation": _normalize_tau_text(figure.explanation)}))
    repaired = article.model_copy(update={"article": sections, "figures": figures})
    _assert_supported_math(repaired)
    return repaired


def _assert_supported_math(article: PaperArticle) -> None:
    serialized = article.model_dump_json()
    unsupported = [command for command in (r"\bm", r"\boldsymbol", r"\passhat") if command in serialized]
    if unsupported:
        raise RuntimeError("unsupported MathJax commands remain: " + ", ".join(unsupported))


def _save(prepared: PreparedPaper) -> dict[str, object]:
    result = validate_article(prepared.article, artifact_root=prepared.bundle)
    if not result.publishable:
        raise RuntimeError("quality gate failed: " + ", ".join(result.issue_codes))
    prepared.bundle.mkdir(parents=True, exist_ok=True)
    (prepared.bundle / "article.json").write_text(
        prepared.article.model_dump_json(indent=2), encoding="utf-8"
    )
    (prepared.bundle / "article.md").write_text(
        render_article_markdown(prepared.article), encoding="utf-8"
    )
    return {
        "canonical_id": prepared.article.paper.canonical_id,
        "title": prepared.article.paper.chinese_title or prepared.article.paper.title,
        "figure_count": len(prepared.article.figures),
        "reference_count": len(prepared.article.article.references),
        "quality_issue_codes": list(result.issue_codes),
    }


def prepare_tau() -> PreparedPaper:
    article = PaperArticle.model_validate_json((TAU_BUNDLE / "article.json").read_text(encoding="utf-8"))
    repaired = repair_tau_article(article, TAU_SOURCE.read_text(encoding="utf-8"), TAU_BUNDLE)
    return PreparedPaper(repaired, TAU_BUNDLE)


def _bonsai_metadata() -> dict[str, object]:
    source = (ROOT / "data" / "workflow_state" / "2607.16633" / "arxiv_source" / "main.tex").read_text(
        encoding="utf-8"
    )
    authors = [" ".join(value.split()) for value in re.findall(r"\\author\{([^{}]+)\}", source)]
    return {
        "canonical_id": "2607.16633",
        "title": "Beyond Fixed Depths and Widths: Optimizing Textual Decoding Tries in LLM-based Generative Recommendation",
        "authors": authors,
        "paper_url": "https://arxiv.org/abs/2607.16633",
        "pdf_url": "https://arxiv.org/pdf/2607.16633.pdf",
        "code_url": "https://github.com/Liu-Jingzhe/BONSAI",
        "year": "2026",
        "venue_type": "会议",
        "venue_name": "ACM RecSys 2026",
        "metadata_source": "local_arxiv_source",
    }


def _copy_bonsai_figures() -> list[dict[str, object]]:
    image_dir = BONSAI_BUNDLE / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    figures: list[dict[str, object]] = []
    for source in sorted(BONSAI_VISUALS.glob("*.png")):
        if source.name == "visual_manifest.json":
            continue
        destination = image_dir / source.name
        shutil.copy2(source, destination)
        with Image.open(destination) as image:
            width, height = image.size
        figures.append(
            {
                "path": destination.relative_to(BONSAI_BUNDLE).as_posix(),
                "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
                "width": width,
                "height": height,
            }
        )
    return figures


def prepare_bonsai(*, regenerate: bool = False) -> PreparedPaper:
    article_path = BONSAI_BUNDLE / "article.json"
    if article_path.is_file() and not regenerate:
        article = PaperArticle.model_validate_json(article_path.read_text(encoding="utf-8"))
    else:
        config = dotenv_values(ROOT / ".env")
        adapter = DeepSeekArticleAdapter(
            api_key=str(config.get("DEEPSEEK_API_KEY") or ""),
            model=str(config.get("DEEPSEEK_MODEL") or "deepseek-chat"),
        )
        adapter.preflight()
        metadata = _bonsai_metadata()
        article = adapter.generate(
            markdown=BONSAI_SOURCE.read_text(encoding="utf-8"),
            metadata=metadata,
            figures=_copy_bonsai_figures(),
            failure_path=BONSAI_BUNDLE / "diagnostics" / "deepseek-invalid-response.json",
        )
        article = article.model_copy(
            update={
                "paper": article.paper.model_copy(
                    update={
                        "canonical_id": metadata["canonical_id"],
                        "title": metadata["title"],
                        "authors": metadata["authors"],
                        "paper_url": metadata["paper_url"],
                        "code_url": metadata["code_url"],
                    }
                ),
                "classification": article.classification.model_copy(
                    update={"year": "2026", "venue_type": "会议", "venue_name": "ACM RecSys 2026"}
                ),
            }
        )
    linked = link_reference_titles(_plain_references(article), BONSAI_SOURCE.read_text(encoding="utf-8"))
    article = article.model_copy(
        update={"article": article.article.model_copy(update={"references": linked})}
    )
    _assert_supported_math(article)
    return PreparedPaper(article, BONSAI_BUNDLE)


def sync_notion(prepared: PreparedPaper) -> str:
    config = dotenv_values(ROOT / ".env")
    notion = NotionGateway(
        str(config.get("NOTION_TOKEN") or ""),
        str(config.get("NOTION_DATABASE_ID") or ""),
        proxy_url=str(config.get("PAPER_INTAKE_NOTION_PROXY_URL") or "http://127.0.0.1:7897"),
    )
    notion.preflight_schema()
    article = prepared.article
    markdown = (prepared.bundle / "article.md").read_text(encoding="utf-8")
    page = notion.upsert_published(
        NotionDraft(
            arxiv_id=article.paper.canonical_id,
            title=article.paper.chinese_title or article.paper.title,
            slug=f"paper-{article.paper.canonical_id}",
            summary=article.article.introduction[:500],
            markdown=markdown,
            figure_paths=tuple((prepared.bundle / item.path).resolve() for item in article.figures),
            categories=tuple(article.classification.categories),
            tags=tuple(article.classification.tags),
            year=publication_year(article),
            venue_type=article.classification.venue_type,
            venue_name=article.classification.venue_name,
        )
    )
    return page.page_id


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish papers whose MinerU output already exists locally")
    parser.add_argument("paper", choices=("tau", "bonsai", "all"))
    parser.add_argument("--regenerate", action="store_true")
    parser.add_argument("--sync-notion", action="store_true")
    args = parser.parse_args()
    prepared = []
    if args.paper in {"tau", "all"}:
        prepared.append(prepare_tau())
    if args.paper in {"bonsai", "all"}:
        prepared.append(prepare_bonsai(regenerate=args.regenerate))
    output = []
    for paper in prepared:
        item = _save(paper)
        item["notion_page_id"] = sync_notion(paper) if args.sync_notion else ""
        output.append(item)
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()

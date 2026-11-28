"""Compile a local, pending blog/Notion review package without remote writes.

The package contains inputs shaped for the existing blog ArticleDraft.  It is
not itself an ArticleDraft, has not passed the blog gate, and is not a Notion
receipt.  Identity readiness is distinct from full blog validation.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from PIL import Image, UnidentifiedImageError

from .fact_pack import (
    FactFormula,
    extract_references,
    locate_formula,
    parse_fact_pack_response,
    stamp_location_verification,
)
from .models import CompilationInputs
from .note_compiler import select_figures


@dataclass(frozen=True, slots=True)
class NotionCompilationResult:
    status: str
    path: Path
    content_hash: str
    blog_compatibility: str


def _identity(canonical_id: str, paper_url: str) -> tuple[str, str, str]:
    bare = canonical_id.rsplit(":", 1)[-1]
    parsed = urlsplit(paper_url)
    host = (parsed.hostname or "").lower()
    arxiv = re.fullmatch(r"(?:\d{4}\.\d{4,5}|[a-z][a-z.-]+/\d{7})(?:v\d+)?", bare, re.I)
    arxiv_id = re.sub(r"v\d+$", "", bare, flags=re.I) if arxiv else ""
    if arxiv_id and host in {
        "arxiv.org", "www.arxiv.org", "export.arxiv.org"
    }:
        url_id = urlsplit(paper_url).path.removeprefix("/abs/").removeprefix("/pdf/").removesuffix(".pdf")
        if re.sub(r"v\d+$", "", url_id) != arxiv_id:
            raise ValueError("arXiv URL does not match canonical identity")
    acl_pattern = r"(?:\d{4}\.[a-z0-9][a-z0-9.-]*\.\d+|[A-Z]\d{2}-\d{4,5})"
    acl_id = ""
    if host in {"aclanthology.org", "www.aclanthology.org"}:
        acl_id = parsed.path.strip("/").removesuffix(".pdf")
    elif host in {"doi.org", "dx.doi.org"} and parsed.path.lower().startswith("/10.18653/v1/"):
        acl_id = parsed.path[len("/10.18653/v1/"):].strip("/")
    if acl_id and re.fullmatch(acl_pattern, acl_id, re.I):
        doi = "10.18653/v1/" + acl_id
        if not arxiv_id and bare not in {acl_id, doi}:
            raise ValueError("ACL DOI URL does not match canonical identity")
        return ("both" if arxiv_id else "acl_doi"), arxiv_id, doi
    if arxiv_id and host in {"arxiv.org", "www.arxiv.org", "export.arxiv.org"}:
        return "arxiv", arxiv_id, ""
    if re.fullmatch(r"10\.\d{4,9}/\S+", bare, re.IGNORECASE):
        return "none", "", bare
    return "none", "", ""


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _review_markdown(title: str, paper_url: str, code_url: str, image_id: str, facts: dict[str, Any],
                     homepage: dict[str, Any], references: list[dict[str, Any]],
                     figures: list[dict[str, Any]], *, formulae: list[FactFormula] | None = None,
                     source_markdown: str = "",
                     figure_notes: dict[str, str] | None = None) -> tuple[str, list[dict[str, Any]]]:
    """Render the homepage manuscript: five numbered sections, nothing else.

    Site spec (2026-11-28): the body never repeats the title, never prints a
    "not provided" placeholder, and drops any section it has no content for.
    Every figure carries a readable note instead of a "图示解释：" caption stub.
    """
    figure_notes = {str(key): str(value) for key, value in (figure_notes or {}).items() if value}
    lead = _clean(homepage.get("summary_para") or homepage.get("summary_1line"))
    blocks: list[str] = []

    # 论文自身的链接放在导语下一行，不占用 References 的位置。
    links = []
    if _is_http(paper_url):
        links.append(f"[论文]({paper_url})")
    if _is_http(code_url):
        links.append(f"[代码]({code_url})")
    if lead:
        blocks.append(lead)
    if links:
        blocks.append("> " + "　".join(links))

    background = _clean(facts.get("background") or facts.get("problem"))
    if background:
        blocks += ["## 研究背景与问题", background]

    method_summary = _clean(facts.get("method_summary"))
    method_heading = f"## 方法：{method_summary}" if method_summary else "## 方法"
    method_blocks: list[str] = []
    overview = _clean(facts.get("method_overview") or facts.get("method"))
    if overview:
        method_blocks.append(overview)
    unplaced: list[dict[str, Any]] = []
    for formula in formulae or []:
        position = locate_formula(source_markdown, formula)
        if position is None:
            unplaced.append({**formula.model_dump(), "status": "pending_review",
                             "reason": "source_not_uniquely_located"})
            continue
        latex = source_markdown[position[0]:position[1]]
        method_blocks.append(f"$$\n{latex}\n$$" if formula.display_mode == "block" else f"${latex}$")
    methods = [item for item in (facts.get("methods") or []) if isinstance(item, dict)]
    for index, item in enumerate(methods, 1):
        heading = _clean(item.get("heading"))
        detail = _clean(item.get("detail"))
        if not (heading or detail):
            continue
        if heading:
            method_blocks += [f"### {heading}", detail]
        else:
            method_blocks.append(detail)
    method_figures, result_figures = _split_figures(figures, figure_notes, image_id)
    method_blocks.extend(method_figures)
    if method_blocks:
        blocks.append(method_heading)
        blocks.extend(method_blocks)

    experiment_highlight = _clean(facts.get("experiment_highlight"))
    experiment_heading = (f"## 实验：{experiment_highlight}" if experiment_highlight
                          else "## 实验")
    experiment_blocks: list[str] = []
    datasets = [str(item).strip() for item in (facts.get("datasets") or []) if str(item).strip()]
    if datasets:
        experiment_blocks += ["### 数据集与 Benchmark",
                              "\n".join(f"- {item}" for item in datasets)]
    protocol = _clean(facts.get("experiment_protocol"))
    if protocol:
        experiment_blocks += ["### 实验方法", protocol]
    metrics = [str(item).strip() for item in (facts.get("metrics") or []) if str(item).strip()]
    hyper = _clean(facts.get("hyperparameters"))
    if metrics or hyper:
        lines = []
        if metrics:
            lines.append("**评测指标**：" + "；".join(metrics))
        if hyper:
            lines.append(f"**参数设置**：{hyper}")
        experiment_blocks += ["### 实验指标与参数设置", "\n\n".join(lines)]
    legacy_results = facts.get("experiments") or []
    legacy_text = ("\n".join(f"- {item}" for item in legacy_results)
                   if isinstance(legacy_results, list) else "")
    analysis = _clean(facts.get("results_analysis")) or legacy_text
    ablation = _clean(facts.get("ablation"))
    if analysis or ablation:
        section = [part for part in (analysis, ablation) if part]
        experiment_blocks += ["### 实验结果与分析", "\n\n".join(section)]
    experiment_blocks.extend(result_figures)
    if experiment_blocks:
        blocks.append(experiment_heading)
        blocks.extend(experiment_blocks)

    summary_highlight = _clean(facts.get("summary_highlight"))
    summary_heading = (f"## 论文总结：{summary_highlight}" if summary_highlight
                       else "## 论文总结")
    # 总结可以退回到 takeaway / 导语：只要这一节还能说出一句人话就渲染它。
    summary = _clean(facts.get("takeaway") or homepage.get("summary_para")
                     or homepage.get("summary_1line"))
    if summary:
        blocks += [summary_heading, summary]

    rendered_refs = [line for line in (_render_reference(item) for item in references) if line]
    if rendered_refs:
        blocks.append("## References")
        blocks.extend(rendered_refs)

    return "\n\n".join(block for block in blocks if block).strip() + "\n", unplaced


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _is_http(url: str) -> bool:
    parsed = urlsplit(str(url or ""))
    return parsed.scheme in {"http", "https"} and bool(parsed.hostname)


_FIGURE_METHOD_HINTS = ("framework", "architecture", "overview", "pipeline", "workflow",
                        "整体", "框架", "架构", "流程", "总览")


def _figure_block(figure: dict[str, Any], note: str, image_id: str) -> list[str]:
    caption = _clean(figure.get("caption"))
    alt = (note or caption).replace("[", "\\[").replace("]", "\\]")
    block = [f"![{alt}](/images/papers/{image_id}/{Path(figure['path']).name})"]
    if note:
        block.append(note)
    elif caption:
        block.append(caption)
    return block


def _split_figures(figures: list[dict[str, Any]], notes: dict[str, str],
                   image_id: str) -> tuple[list[str], list[str]]:
    """Method figures sit under section 2, everything else under 3.4."""
    method_blocks: list[str] = []
    result_blocks: list[str] = []
    for figure in figures:
        figure_id = _clean(figure.get("figure_id"))
        note = notes.get(figure_id, "")
        caption = _clean(figure.get("caption"))
        haystack = f"{figure_id} {caption} {note}".casefold()
        target = method_blocks if any(hint in haystack for hint in _FIGURE_METHOD_HINTS) else result_blocks
        target.extend(_figure_block(figure, note, image_id))
    return method_blocks, result_blocks


def _render_reference(reference: dict[str, Any]) -> str:
    """One bibliography line: Authors. Year. **Title**(link). Venue. （代码：url）"""
    title = _clean(reference.get("title")).replace("[", "\\[").replace("]", "\\]")
    if not title:
        return ""
    link = str(reference.get("paper_url") or "")
    code = str(reference.get("code_url") or "")
    authors = [str(name).strip() for name in (reference.get("authors") or []) if str(name).strip()]
    year = _clean(reference.get("year"))
    venue = _clean(reference.get("venue"))
    head = ""
    if authors:
        head = ", ".join(authors[:-1]) + (f", and {authors[-1]}" if len(authors) > 1 else authors[0])
        head += ". "
    if year:
        head += f"{year}. "
    body = f"**[{title}]({link})**" if _is_http(link) else f"**{title}**"
    line = f"{head}{body}."
    if venue:
        line += f" {venue}."
    if _is_http(code):
        line += f" （代码：{code}）"
    return line


def compile_notion_package(inputs: CompilationInputs, *, output_dir: Path) -> NotionCompilationResult:
    """Write a content-addressed local review artifact; never write to Notion."""
    if not inputs.fact_pack_path or not inputs.figure_manifest_path:
        raise ValueError("FactPack and selected figure manifest are required")
    if not inputs.canonical_id or not inputs.job_id:
        raise ValueError("canonical identity and job_id are required")
    for url in (inputs.paper_url, inputs.pdf_url, *([inputs.code_url] if inputs.code_url else [])):
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("paper and PDF URLs must be supplied as HTTP(S) URLs")
    pdf = Path(inputs.pdf_path).resolve()
    with pdf.open("rb") as handle:
        if handle.read(5) != b"%PDF-":
            raise ValueError("source PDF has an invalid header")
    markdown = Path(inputs.markdown_path).resolve()
    source_text = markdown.read_text(encoding="utf-8")
    pack = parse_fact_pack_response(Path(inputs.fact_pack_path).read_text(encoding="utf-8"), inputs.canonical_id)
    if pack.get("canonical_id") != inputs.canonical_id:
        raise ValueError("FactPack identity does not match producing job")
    # A model-proposed city is not evidence: verify it against the paper's own
    # affiliation header, otherwise the publisher drops the location silently.
    pack = stamp_location_verification(pack, pdf_markdown=source_text)
    source_hash = str(pack.get("source_hash") or "")
    if not source_hash or _hash_file(markdown) != source_hash:
        raise ValueError("FactPack source hash missing or does not match parsed Markdown")
    facts = pack["facts"]
    homepage = pack.get("homepage_draft") or {}
    if not isinstance(homepage, dict):
        raise ValueError("homepage_draft must be an object")
    selected = select_figures(markdown.parent, manifest_path=inputs.figure_manifest_path,
                              canonical_id=inputs.canonical_id, max_figures=10000)
    figures = []
    for item in selected:
        path = (markdown.parent / item["file"]).resolve()
        try:
            with Image.open(path) as image:
                width, height = image.size
        except (OSError, UnidentifiedImageError) as error:
            raise ValueError(f"selected figure is not a readable image: {path}") from error
        figures.append({
            "figure_id": item.get("figure_id", ""), "path": str(path),
            "caption": item.get("caption", ""), "dimensions": [width, height],
            "is_hd": width >= 1280 or height >= 720,
            "provenance": item.get("source_type", ""), "sha256": _hash_file(path),
            "manifest_sha256": item.get("sha256", ""), "visual_review": item.get("visual_review"),
        })
    identity_kind, arxiv_id, doi = _identity(inputs.canonical_id, inputs.paper_url)
    safe_id = re.sub(r"[^A-Za-z0-9._-]+", "-", inputs.canonical_id).strip(".-")[:70] or "paper"
    slug = f"paper-{safe_id}-{hashlib.sha256(inputs.canonical_id.encode('utf-8')).hexdigest()[:8]}"
    title = str(facts.get("paper_title") or facts.get("one_line") or inputs.canonical_id)
    # The paper's own bibliography is the faithful source for a reference list:
    # it is printed in the PDF, so authors/year/venue need no model guess. Model
    # supplied references stay as a fallback for papers whose section is missing.
    references = [item.model_dump() for item in extract_references(source_text)] or (pack.get("references") or [])
    formulae = pack.get("formulae") or []
    location = pack.get("location")
    fact_provenance = pack.get("fact_provenance")
    figure_notes = {
        str(item.get("figure_id") or ""): str(item.get("explanation") or "")
        for item in (pack.get("figures") or []) if isinstance(item, dict)
    }
    review_md, unplaced_formulae = _review_markdown(
        title, inputs.paper_url, inputs.code_url, arxiv_id or safe_id,
        facts, homepage, references, figures,
        formulae=[FactFormula.model_validate(item) for item in formulae], source_markdown=source_text,
        figure_notes=figure_notes)
    missing = []
    if not facts.get("paper_title"):
        missing.append("paper_title")
    if not facts.get("authors"):
        missing.append("authors")
    if not inputs.code_url:
        missing.append("official_code_url_unverified_or_missing")
    if not references:
        missing.append("references")
    if not location:
        missing.append("location")
    if any(not figure["caption"] or not figure["is_hd"] for figure in figures):
        missing.append("figure_caption_or_hd")
    # Identity readiness is not a claim that review, upload or blog validation passed.
    identity_status = ("ready" if identity_kind in {"arxiv", "both"} else
                       "ready_non_arxiv" if identity_kind == "acl_doi" else "blocked_non_arxiv")
    compatibility = "not_validated" if identity_kind in {"arxiv", "both", "acl_doi"} else "blocked_non_arxiv"
    package = {
        "schema_version": "notion-review/v1", "review_status": "pending",
        "canonical_id": inputs.canonical_id, "job_id": inputs.job_id,
        "identity": {"canonical_id": inputs.canonical_id, "catalog_canonical_id": inputs.catalog_canonical_id,
                     "kind": identity_kind, "paper_url": inputs.paper_url, "pdf_url": inputs.pdf_url,
                     "code_url": inputs.code_url},
        "provenance": {"markdown_path": str(markdown), "markdown_sha256": source_hash,
                       "pdf_sha256": _hash_file(pdf),
                       "fact_pack_path": str(Path(inputs.fact_pack_path).resolve()),
                       "fact_pack_sha256": _hash_file(Path(inputs.fact_pack_path)),
                       "figure_manifest_path": str(Path(inputs.figure_manifest_path).resolve()),
                       "figure_manifest_sha256": _hash_file(Path(inputs.figure_manifest_path))},
        "article_input": {"arxiv_id": arxiv_id, "doi": doi, "paper_url": inputs.paper_url,
            "canonical_id": inputs.canonical_id, "title": title, "slug": slug,
            "markdown": review_md, "source_text": source_text, "source_pdf": str(pdf),
            "source_spans": {"source_hash": source_hash}, "figures": figures},
        "facts": facts, "homepage_draft": homepage, "location": location,
        "fact_provenance": fact_provenance,
        "references": references, "formulae": formulae, "unplaced_formulae": unplaced_formulae, "figures": figures,
        "missing_fields": missing, "identity_status": identity_status, "blog_compatibility": compatibility,
        "blog_validation_performed": False, "notion_written": False,
    }
    encoded = json.dumps(package, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8")
    digest = hashlib.sha256(encoded).hexdigest()
    target = Path(output_dir) / digest[:32] / "notion.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with target.open("xb") as handle:
            handle.write(encoded)
    except FileExistsError:
        if target.read_bytes() != encoded:
            raise FileExistsError(f"review package collision; refusing to overwrite: {target}")
    return NotionCompilationResult("compiled", target, digest, compatibility)

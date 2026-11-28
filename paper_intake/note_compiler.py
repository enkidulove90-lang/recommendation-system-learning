"""Deterministic compiler: publish-ready fact_pack JSON -> redbook note YAML.

No agent and no vision model are involved.  Figures are selected in PAPER order
from ``figure_manifest.json`` (arxiv latex / MinerU), falling back to natural
filename order (fig1, fig2, ...) when no manifest exists.  The visual review
record is built from structural probes (image size, format, figure caption),
never from a generative vision model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
NOTES_DIR = ROOT / "redbook" / "notes"

# Section headings are fixed so the body always passes the gate's dedicated
# section-line check.  Content comes from xhs_draft.sections (model-generated).
SECTION_HEADINGS = {
    "contribution": "🎓 主要贡献与创新",
    "method": "🧠 核心方法",
    "experiment": "🧪 实验条件",
    "result": "📊 核心结果",
}
SECTION_ORDER = ("contribution", "method", "experiment", "result")

# Mirrors config/xhs_content_rules.yaml topic_allowlist (single source of
# truth is the yaml; we load it at runtime in _allowed_topics()).
DEFAULT_TOPICS = ["论文分享", "人工智能", "推荐系统", "深度学习", "AI"]


def _load_rules() -> dict[str, Any]:
    rules_path = ROOT / "config" / "xhs_content_rules.yaml"
    if not rules_path.is_file():
        return {}
    with rules_path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _allowed_topics() -> set[str]:
    rules = _load_rules()
    return {str(item).strip() for item in rules.get("topic_allowlist", DEFAULT_TOPICS)}


def _normalize_topic(value: str) -> str:
    return str(value).strip().lstrip("#").strip().casefold()


def load_fact_pack(path: Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"fact_pack is not an object: {path}")
    if "xhs_draft" not in payload or not isinstance(payload["xhs_draft"], dict):
        raise ValueError(
            f"fact_pack has no xhs_draft block (need fact-pack/v2+): {path}")
    return payload


def _natural_key(name: str) -> tuple:
    """Sort fig2 < fig10 by splitting digit runs."""
    return tuple(
        int(part) if part.isdigit() else part
        for part in re.split(r"(\d+)", name)
    )


def select_figures(
    parsed_dir: Path,
    *,
    figure_intents: list[dict[str, Any]] | None = None,
    max_figures: int = 9,
    manifest_path: Path | None = None,
    canonical_id: str = "",
) -> list[dict[str, str]]:
    """Pick figures in PAPER order (manifest first, filename fallback).

    Returns a list of ``{file, type, description}`` ready for the note YAML,
    where ``file`` is relative to ``parsed_dir``.
    """
    parsed_dir = Path(parsed_dir)
    if not parsed_dir.is_dir():
        raise FileNotFoundError(f"parsed dir missing: {parsed_dir}")

    if manifest_path is not None:
        data = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        if isinstance(data, dict) and canonical_id and data.get("canonical_id") != canonical_id:
            raise ValueError("figure manifest identity does not match paper")
        manifest = data.get("figures") if isinstance(data, dict) else data
        if not isinstance(manifest, list):
            raise ValueError("figure manifest must contain a figures list")
    else:
        manifest = _find_manifest(parsed_dir, canonical_id=canonical_id)
    candidates: list[dict[str, Any]] = []
    if manifest is not None:
        for row in manifest:
            if not isinstance(row, dict) or row.get("selected") is False:
                continue
            rel = str(row.get("path") or "")
            target = (parsed_dir / rel).resolve() if manifest_path is not None and rel else _resolve_figure_path(parsed_dir, rel)
            if manifest_path is not None and target is not None:
                try:
                    target.relative_to(parsed_dir.resolve())
                except ValueError as error:
                    raise ValueError("figure path escapes parsed directory") from error
            if target is not None and target.is_file():
                candidates.append({
                    "file": _relative_to(parsed_dir, target),
                    "figure_id": str(row.get("figure_id") or ""),
                    "caption": str(row.get("caption") or ""),
                    **{key: row[key] for key in ("sha256", "source_type", "width", "height", "visual_review", "role")
                       if key in row},
                })
        if manifest_path is None:
            candidates.sort(key=lambda item: _natural_key(item["figure_id"] or item["file"]))

    if not candidates:
        if manifest is not None:
            raise ValueError("figure manifest has no usable selected figures")
        # Fallback: scan image files in natural filename order.
        images_dir = parsed_dir / "images"
        scan_dir = images_dir if images_dir.is_dir() else parsed_dir
        suffixes = {".png", ".jpg", ".jpeg", ".webp"}
        files = [
            path for path in scan_dir.rglob("*")
            if path.suffix.lower() in suffixes and path.is_file()
        ]
        files.sort(key=lambda path: _natural_key(path.name))
        for path in files:
            candidates.append({
                "file": _relative_to(parsed_dir, path),
                "figure_id": "",
                "caption": "",
            })

    if not candidates:
        raise ValueError(f"no figures found under {parsed_dir}")

    intents = list(figure_intents or [])
    selected: list[dict[str, str]] = []
    for index, candidate in enumerate(candidates[:max_figures]):
        # Explicit manifests describe the actual selected file.  Model figure
        # intents are positional suggestions and must not override its caption.
        intent = intents[index] if manifest_path is None and index < len(intents) else {}
        description = str(intent.get("description") or "").strip()
        if not description:
            description = candidate["caption"] or (
                f"论文图 {index + 1}：{candidate['file']}"
            )
        selected.append({
            "file": candidate["file"],
            "figure_id": candidate["figure_id"],
            "caption": candidate["caption"],
            "type": str(candidate.get("role") or intent.get("intent") or _infer_type(index, description)),
            "description": description,
            **{key: candidate[key] for key in ("sha256", "source_type", "width", "height", "visual_review")
               if key in candidate},
        })
    return selected


def _infer_type(index: int, description: str) -> str:
    text = description.casefold()
    if any(word in text for word in ("architecture", "framework", "架构", "框架", "流程")):
        return "architecture"
    if any(word in text for word in ("result", "experiment", "结果", "实验", "compare", "对比")):
        return "result"
    return "motivation" if index == 0 else "result"


def _find_manifest(parsed_dir: Path, *, canonical_id: str = "") -> list[dict[str, Any]] | None:
    for candidate in (
        parsed_dir / "figure_manifest.json",
        parsed_dir / "images" / "figure_manifest.json",
        parsed_dir / "images_source" / "figure_manifest.json",
    ):
        if candidate.is_file():
            data = json.loads(candidate.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and isinstance(data.get("figures"), list):
                if canonical_id and data.get("canonical_id") != canonical_id:
                    raise ValueError("figure manifest identity does not match paper")
                return data["figures"]
    return None


def _resolve_figure_path(parsed_dir: Path, relative: str) -> Path | None:
    if not relative:
        return None
    direct = parsed_dir / relative
    if direct.is_file():
        return direct
    images = parsed_dir / "images" / Path(relative).name
    if images.is_file():
        return images
    matches = list(parsed_dir.rglob(Path(relative).name))
    return matches[0] if matches else None


def _relative_to(base: Path, target: Path) -> str:
    try:
        return target.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return target.resolve().as_posix()


def build_body(
    xhs_draft: dict[str, Any],
    *,
    paper_url: str = "",
    code_url: str = "",
    max_chars: int = 980,
) -> str:
    """Assemble the template-style body; never emits Markdown markers.

    Rules (template v3):
      - each section heading is followed by ONE newline, content on the next
        line (heading and content are no longer on the same line);
      - bullet points keep their newlines (one item per line);
      - 🌐 prefix on the opening, newline, then '核心痛点：' on its own line;
      - after the last content block, single newlines lead to the reference
        links:  📎 论文链接 → 💻 代码链接.  The body does NOT contain literal
        '#话题' text: on the platform, typing '#' opens the topic picker and
        the draft keeps real topic entities (keyword + hyperlink).  Topics are
        typed and bound by the delivery layer from the note's ``topics`` list;
      - 借鉴/局限/限制 sections are omitted entirely (template rule).
    """
    opening = str(xhs_draft.get("opening") or "").strip()
    pain = str(xhs_draft.get("pain_point") or "").strip()
    sections = xhs_draft.get("sections") or {}
    lines: list[str] = []

    if opening:
        opening = _plain(opening)
        if not opening.startswith("🌐"):
            opening = "🌐 " + opening
        if pain:
            pain = _plain(pain)
            if not pain.startswith("核心痛点"):
                pain = "核心痛点：" + pain
            opening = opening + "\n" + pain  # newline after 🌐 hook
        lines.append(opening)

    for key in SECTION_ORDER:
        content = str(sections.get(key) or "").strip()
        if not content:
            continue
        content = _plain(content)
        # Heading on its own line; content starts on the NEXT line (single
        # newline, never a blank line).  Bullet newlines inside content
        # (①...\n②...) are preserved.
        lines.append(SECTION_HEADINGS[key] + "\n" + content)

    main = "\n\n".join(lines)

    # Reference tail: result paragraph → 📎 paper link → 💻 code link, all
    # separated by single newlines.  No literal '#tag' text here — topics are
    # bound as platform entities by the delivery layer.  The tail is protected
    # from trimming: the main body shrinks to make room for it instead.
    tail_lines: list[str] = []
    if str(paper_url).strip():
        tail_lines.append("📎 论文链接：" + str(paper_url).strip())
    if str(code_url).strip():
        tail_lines.append("💻 代码链接：" + str(code_url).strip())
    tail = "\n".join(tail_lines)

    if not tail:
        if len(main) > max_chars:
            main = _trim_body(main, max_chars)
        return main
    if not main:
        return tail[:max_chars]
    budget = max_chars - len(tail) - 1
    if len(main) > budget:
        main = _trim_body(main, budget)
    return main + "\n" + tail


def _fit_title(title: str, *, limit: int = 20) -> str:
    """Fit a literary title to the gate's hard char limit, keeping its style.

    DeepSeek writes e.g. "WWW 2026 | RecCLIP：协同过滤的视觉显影" (28 chars).
    Drop conference-year prefixes and compact whitespace first; if still too
    long, keep the method name + the poetic tail.  Never emit an empty title.
    """
    cleaned = re.sub(r"\s+", "", str(title).strip())
    # "WWW2026|", "ACM2025|", "KDD2026:" etc.
    cleaned = re.sub(r"^(?:WWW|KDD|SIGIR|ACM|ICLR|NeurIPS|IJCAI|AAAI|CIKM|RecSys|SIGMOD)\d{4}[|：:丨]?", "", cleaned, flags=re.IGNORECASE)
    if len(cleaned) <= limit:
        return cleaned
    # Prefer a '：' split: keep "Method：poetic tail" and trim the tail.
    if "：" in cleaned:
        head, tail = cleaned.split("：", 1)
        budget = limit - len(head) - 1
        if budget > 0:
            return f"{head}：{tail[:budget]}"
    return cleaned[:limit]


def _plain(text: str) -> str:
    """Strip any Markdown-ish markers the model might have leaked."""
    cleaned = text.replace("**", "").replace("__", "").replace("`", "")
    cleaned = cleaned.replace("~~", "")
    cleaned = re.sub(r"(?m)^#{1,6}\s*", "", cleaned)
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    return cleaned.strip()


def _trim_body(body: str, limit: int) -> str:
    """Trim to limit by dropping trailing content blocks (never the hook)."""
    blocks = body.split("\n\n")
    budget = limit
    kept: list[str] = []
    used = 0
    for block in blocks:
        addition = len(block) + (2 if kept else 0)
        if used + addition > budget:
            break
        kept.append(block)
        used += addition
    return "\n\n".join(kept)[:limit]


def _probe_review(figures: list[dict[str, str]], parsed_dir: Path) -> str:
    """Structural (non-vision) per-image verification note for the gate."""
    notes: list[str] = []
    try:
        from PIL import Image
    except ImportError:  # pragma: no cover - Pillow is a project dependency
        Image = None  # type: ignore[assignment]

    for index, figure in enumerate(figures, start=1):
        path = parsed_dir / figure["file"]
        detail = f"图{index} {figure['file']}"
        if path.is_file():
            detail += f" 存在({path.stat().st_size}B"
            if Image is not None:
                try:
                    with Image.open(path) as image:
                        detail += f", {image.width}x{image.height} {image.format}"
                except Exception:
                    detail += ", 尺寸读取失败"
            detail += ")"
        else:
            detail += " 缺失"
        if figure.get("description"):
            detail += f"，图注：{figure['description'][:40]}"
        notes.append(detail)
    return "按论文图序做结构核验（非视觉模型）：" + "；".join(notes)


def compile_note(
    fact_pack_path: Path,
    *,
    canonical_id: str,
    parsed_dir: Path,
    pdf_path: Path | None,
    notes_dir: Path = NOTES_DIR,
    title_style: str = "literary",
    figure_manifest_path: Path | None = None,
    paper_url: str | None = None,
    pdf_url: str | None = None,
    code_url: str | None = None,
) -> Path:
    """Compile one redbook note YAML from a fact-pack JSON. Returns its path."""
    payload = load_fact_pack(fact_pack_path)
    draft = payload["xhs_draft"]

    paper_id = canonical_id.rsplit(":", 1)[-1]
    title = str(draft.get("title_%s" % title_style) or draft.get("title_literary") or "").strip()
    if not title:
        raise ValueError("xhs_draft has no title_%s" % title_style)
    title = _fit_title(title, limit=20)

    figures = select_figures(parsed_dir, figure_intents=draft.get("figure_intents"),
                             manifest_path=figure_manifest_path, canonical_id=canonical_id)
    facts = payload.get("facts") or {}

    topics: list[str] = []
    allowed = _allowed_topics()
    for topic in draft.get("topics") or DEFAULT_TOPICS:
        text = str(topic).strip().lstrip("#").strip()
        if _normalize_topic(text) in {_normalize_topic(item) for item in allowed}:
            # Keep the canonical spelling from the allowlist for byte-stability.
            canonical = next(
                (item for item in allowed if _normalize_topic(item) == _normalize_topic(text)),
                text,
            )
            if canonical not in topics:
                topics.append(canonical)
    if not topics:
        topics = list(DEFAULT_TOPICS[:3])

    links = {
        "paper": paper_url if paper_url is not None else _paper_url(paper_id, payload),
        "pdf": pdf_url if pdf_url is not None else _pdf_url(paper_id),
        "code": code_url if code_url is not None else str((facts.get("code_url") or "")).strip(),
    }
    # Template omits 借鉴/局限 sections; the tail carries the reference links
    # (topics are typed + bound as entities at delivery time, not in the body).
    body = build_body(
        draft,
        paper_url=links["paper"],
        code_url=links["code"],
    )
    base_slug = re.sub(r"[^A-Za-z0-9._-]+", "_", paper_id).strip("._") or "paper"
    if base_slug != paper_id or len(base_slug) > 100:
        base_slug = base_slug[:80] + "-" + hashlib.sha256(canonical_id.encode("utf-8")).hexdigest()[:10]
    spec = {
        "paper_id": paper_id,
        "slug": base_slug,
        "title": title,
        "status": "draft",
        "source": "handwritten",
        "parsed_dir": _relative_to(ROOT, parsed_dir),
        "pdf_path": _relative_to(ROOT, pdf_path) if pdf_path and pdf_path.is_file() else "",
        "body": body,
        "figures": figures,
        "topics": topics,
        "links": links,
        "visual_review": "pending",
        "review_status": "pending",
        "metadata": {
            "author": str(facts.get("author") or ""),
            "source_attribution": "图片按论文图序取自原文解析产物，仅作学术解读。",
            "generated_by": "paper_intake.note_compiler",
            "fact_pack_schema": payload.get("schema_version", "fact-pack/v2"),
            "figure_structural_check": _probe_review(figures, parsed_dir),
        },
    }

    note_dir = Path(notes_dir)
    note_dir.mkdir(parents=True, exist_ok=True)
    base_text = yaml.safe_dump(spec, allow_unicode=True, sort_keys=False, default_flow_style=False)
    revision = hashlib.sha256(base_text.encode("utf-8")).hexdigest()[:12]
    for slug in (base_slug, f"{base_slug}-{revision}"):
        spec["slug"] = slug
        text = yaml.safe_dump(spec, allow_unicode=True, sort_keys=False, default_flow_style=False)
        target = note_dir / f"{slug}.yaml"
        try:
            with target.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(text)
            return target
        except FileExistsError:
            if target.read_text(encoding="utf-8") == text:
                return target
    raise FileExistsError(f"note revision collision; refusing to overwrite: {target}")


def _paper_url(paper_id: str, payload: dict[str, Any]) -> str:
    raw = str((payload.get("links") or {}).get("paper") or "").strip()
    if raw:
        return raw
    if paper_id.replace(".", "").isdigit():
        return f"https://arxiv.org/abs/{paper_id}"
    return f"https://doi.org/{paper_id}"


def _pdf_url(paper_id: str) -> str:
    if paper_id.replace(".", "").isdigit():
        return f"https://arxiv.org/pdf/{paper_id}"
    return f"https://doi.org/{paper_id}"


def main() -> int:
    parser = argparse.ArgumentParser(description="compile a redbook note from fact_pack JSON")
    parser.add_argument("--fact-pack", type=Path, required=True)
    parser.add_argument("--canonical-id", required=True)
    parser.add_argument("--parsed-dir", type=Path, required=True)
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("--notes-dir", type=Path, default=NOTES_DIR)
    parser.add_argument("--title-style", choices=("literary", "question"), default="literary")
    args = parser.parse_args()
    target = compile_note(
        args.fact_pack,
        canonical_id=args.canonical_id,
        parsed_dir=args.parsed_dir,
        pdf_path=args.pdf,
        notes_dir=args.notes_dir,
        title_style=args.title_style,
    )
    print(json.dumps({"ok": True, "note": str(target.relative_to(ROOT))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

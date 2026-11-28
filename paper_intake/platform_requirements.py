"""Per-platform required-field manifest + material validity checks.

Motivation (user decision 2026-11-28): "字段齐全 ≠ 可上传" — a package can
have all the text fields yet carry an invalid asset (e.g. a 0-byte figure),
which makes the real platform upload fail silently. So before delivery we run
an explicit pre-flight that reports, per platform:

  - which required fields are missing,
  - which fields are present but invalid,
  - which material files are invalid (missing / empty / bad magic bytes).

The report is *advisory*: it names exactly what must be regenerated. It never
calls the model itself ("字段不全回补 fact_pack 不是死循环") — a human/upstream
step decides to regenerate the fact_pack, avoiding an unbounded retry loop.

This module is pure (no network, no redbook import) so both the compilers
(paper_intake) and the delivery stage (scripts) can share one source of truth.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Iterable

# ---------------------------------------------------------------------------
# Material validity
# ---------------------------------------------------------------------------
#: File signatures that the real platforms accept for an image upload.
_IMAGE_MAGIC: tuple[tuple[bytes, str], ...] = (
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"\xff\xd8\xff", "jpg"),
    (b"GIF87a", "gif"),
    (b"GIF89a", "gif"),
)
_MIN_IMAGE_BYTES = 1024          # anything smaller is almost certainly broken
_MIN_PDF_BYTES = 1024


def check_image_file(path: str | Path) -> str:
    """Return '' when the image is valid, else a human reason string."""
    p = Path(path)
    if not p.is_file():
        return f"missing image: {p}"
    size = p.stat().st_size
    if size < _MIN_IMAGE_BYTES:
        return f"invalid image (only {size} bytes, likely empty/corrupt): {p.name}"
    with p.open("rb") as fh:
        head = fh.read(12)
    if head.startswith(b"RIFF") and b"WEBP" in head:
        return ""
    for magic, _name in _IMAGE_MAGIC:
        if head.startswith(magic):
            return ""
    return f"invalid image header (not png/jpg/gif/webp): {p.name}"


def check_pdf_file(path: str | Path) -> str:
    p = Path(path)
    if not p.is_file():
        return f"missing pdf: {p}"
    size = p.stat().st_size
    if size < _MIN_PDF_BYTES:
        return f"invalid pdf (only {size} bytes): {p.name}"
    with p.open("rb") as fh:
        if fh.read(5) != b"%PDF-":
            return f"invalid pdf header: {p.name}"
    return ""


# ---------------------------------------------------------------------------
# Platform manifests
# ---------------------------------------------------------------------------
#: Human-readable required fields, one dict per platform. Kept as data so a
#: report can list field *names* even when the package omits them entirely.
PLATFORM_FIELDS: dict[str, dict[str, str]] = {
    "xhs": {
        "paper_id": "论文身份 id",
        "title": "标题（1-20 字）",
        "body": "正文",
        "topics": "话题（≥1 个，白名单内）",
        "figures": "图片（1-9 张，文件有效）",
        "slug": "slug",
    },
    "wechat": {
        "paper_id": "论文身份 id",
        "title": "标题（1-64 字）",
        "body_markdown": "正文（≥200 字）",
        "image_paths": "图片（1-9 张，文件有效）",
        "links.paper": "论文链接",
        "links.pdf": "PDF 链接",
    },
    "notion": {
        "canonical_id": "论文身份 id",
        "article_input.title": "标题",
        "article_input.slug": "slug",
        "article_input.markdown": "正文 Markdown",
        "article_input.figures": "图片（≥1 张，文件有效）",
    },
}


def _get(data: dict, dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def _xhs_image_paths(data: dict) -> list[Path]:
    base = Path(str(data.get("parsed_dir") or ""))
    out: list[Path] = []
    for fig in data.get("figures") or []:
        if isinstance(fig, dict) and fig.get("file"):
            rel = Path(str(fig["file"]))
            out.append(rel if rel.is_absolute() else base / rel)
    return out


def _wechat_image_paths(data: dict) -> list[Path]:
    return [Path(str(p)) for p in (data.get("image_paths") or [])]


def _notion_image_paths(data: dict) -> list[Path]:
    figs = (data.get("article_input") or {}).get("figures") or []
    return [Path(str(f.get("path"))) for f in figs if isinstance(f, dict) and f.get("path")]


_IMAGE_GETTERS: dict[str, Callable[[dict], list[Path]]] = {
    "xhs": _xhs_image_paths,
    "wechat": _wechat_image_paths,
    "notion": _notion_image_paths,
}


def check_package(platform: str, data: dict) -> dict[str, Any]:
    """Pre-flight one platform package. Returns a structured report.

    Keys: ok, missing_fields (dotted names), invalid_fields (reasons),
    invalid_materials (reasons), needs_regeneration (field names to regenerate).
    """
    if platform not in PLATFORM_FIELDS:
        raise ValueError(f"unknown platform: {platform}")
    missing: list[str] = []
    invalid: list[str] = []
    materials: list[str] = []

    # Field presence/value checks per platform.
    if platform == "xhs":
        if not str(data.get("paper_id") or "").strip():
            missing.append("paper_id")
        title = str(data.get("title") or "")
        if not title.strip():
            missing.append("title")
        elif len(title) > 20:
            invalid.append(f"title too long ({len(title)}>20)")
        if not str(data.get("body") or "").strip():
            missing.append("body")
        if not (data.get("topics") or []):
            missing.append("topics")
        figs = data.get("figures") or []
        if not figs:
            missing.append("figures")
        elif not (1 <= len(figs) <= 9):
            invalid.append(f"figure count {len(figs)} outside 1-9")
        if not str(data.get("slug") or "").strip():
            missing.append("slug")

    elif platform == "wechat":
        if not str(data.get("paper_id") or "").strip():
            missing.append("paper_id")
        title = str(data.get("title") or "")
        if not title.strip():
            missing.append("title")
        elif len(title) > 64:
            invalid.append(f"title too long ({len(title)}>64)")
        body = str(data.get("body_markdown") or "")
        if not body.strip():
            missing.append("body_markdown")
        elif len(body) < 200:
            invalid.append(f"body too short ({len(body)}<200)")
        imgs = data.get("image_paths") or []
        if not imgs:
            missing.append("image_paths")
        elif not (1 <= len(imgs) <= 9):
            invalid.append(f"image count {len(imgs)} outside 1-9")
        links = data.get("links") or {}
        if not str(links.get("paper") or "").strip():
            missing.append("links.paper")
        if not str(links.get("pdf") or "").strip():
            missing.append("links.pdf")

    elif platform == "notion":
        if not str(data.get("canonical_id") or "").strip():
            missing.append("canonical_id")
        ai = data.get("article_input") or {}
        if not str(ai.get("title") or "").strip():
            missing.append("article_input.title")
        if not str(ai.get("slug") or "").strip():
            missing.append("article_input.slug")
        if not str(ai.get("markdown") or "").strip():
            missing.append("article_input.markdown")
        figs = ai.get("figures") or []
        if not figs:
            missing.append("article_input.figures")

    # Material validity — the "字段齐全≠可上传" part.
    getter = _IMAGE_GETTERS[platform]
    try:
        for path in getter(data):
            reason = check_image_file(path)
            if reason:
                materials.append(reason)
    except (OSError, TypeError):
        materials.append("could not resolve image paths")

    # XHS/WeChat PDF attachment is optional; validate when declared.
    pdf = data.get("pdf_path") or (data.get("metadata") or {}).get("pdf_path")
    if platform in ("xhs", "wechat") and pdf:
        reason = check_pdf_file(Path(str(pdf)))
        if reason:
            materials.append(reason)

    ok = not missing and not invalid and not materials
    needs_regeneration = sorted(set(missing + [m.split(":")[0] for m in invalid]))
    return {
        "platform": platform,
        "ok": ok,
        "missing_fields": missing,
        "invalid_fields": invalid,
        "invalid_materials": materials,
        "needs_regeneration": needs_regeneration,
    }


def check_all(results: dict[str, dict]) -> dict[str, dict]:
    """Run check_package for each platform present in a compile_shared result.

    ``results`` maps platform -> a dict that carries at least the package data.
    The delivery layer passes the already-loaded package bodies here.
    """
    return {platform: check_package(platform, data)
            for platform, data in results.items() if platform in PLATFORM_FIELDS}

"""Build a Xiaohongshu (小红书) draft for one parsed paper, following the XHS chain.

Pipeline
--------
1. ``load_assets`` collects the 11-dimension summary, parsed dir, figures and PDF.
2. ``render_note`` (paper_to_xhs) composes the 300-700 char note with emoji voice,
   derives real topic entities (关键词) from the paper content, and binds the PDF.
3. ``XhsPublisher.stage`` writes an immutable review package under
   ``data/publish_queue/<content_hash>/xhs.json``.

This mirrors ``paper_to_wechat.py``'s ``--paper-id`` CLI.  The older
``cli stage --paper paper_card.json`` path uses ``render_package``/``_render_xhs``,
which does NOT derive topics, so this module is the canonical XHS draft builder.

Pass ``--publish`` to additionally push the draft to the XHS draft box (requires a
logged-in xiaohongshu session); otherwise only the staged review package is produced.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from ..infrastructure import opencli_runtime
from .paper_to_xhs import RenderError, load_assets, render_note
from .publishing import PublicationPackage, XhsPublisher


def build_package(
    assets, canonical_url: str, code_url: str = "", project_url: str = "", title: str = ""
) -> PublicationPackage:
    """Assemble a platform-ready XHS package from parsed paper assets.

    Topics and the PDF path ride in ``metadata`` so the delivery adapter can bind
    real topic entities and attach the paper PDF (the order the platform enforces:
    topics -> PDF -> draft).

    ``title`` (optional) overrides the auto-generated note title. ``canonical_url``
    and ``code_url`` are also injected into the article body as clickable links so
    readers can reach the arXiv paper and the GitHub repo directly from the post.
    """
    note = render_note(assets)

    if title:
        note.title = title

    links = {
        "paper": canonical_url or f"https://arxiv.org/abs/{assets.paper_id}",
        "pdf": canonical_url or f"https://arxiv.org/pdf/{assets.paper_id}",
        "code": code_url or "",
    }
    if project_url:
        links["project"] = project_url

    # Inject clickable paper + GitHub links into the article body, replacing the
    # bare "📄 arXiv: <id>" line that render_note appends (it has no URL). The
    # label stays generic ("论文") so it reads correctly for DOI/venue links too,
    # not only arXiv.
    body = note.body
    body = re.sub(r"\n?📄\s*arXiv:[^\n]*\n?", "", body).strip()
    footer: list[str] = []
    if links["paper"]:
        footer.append(f"📄 论文：{links['paper']}")
    if links["code"]:
        footer.append(f"💻 代码 GitHub：{links['code']}")
    if project_url:
        footer.append(f"🌐 项目页：{project_url}")
    if footer:
        body = body + "\n\n" + "\n".join(footer)

    package = PublicationPackage(
        paper_id=assets.paper_id,
        platform="xhs",
        canonical_url=canonical_url or links["paper"],
        title=note.title,
        body_markdown=body,
        image_paths=[str(p) for p in note.image_paths],
        links=links,
    )
    package.metadata["topics"] = list(note.topics)
    package.metadata["pdf_path"] = str(note.pdf_path)
    package.metadata["author"] = ""
    return package


def deliver_draft(
    assets, canonical_url: str = "", code_url: str = "", project_url: str = "",
    publish: bool = False, title: str = ""
) -> dict[str, Any]:
    """Stage (and optionally publish) a Xiaohongshu draft for one parsed paper.

    Staging is pure local file I/O and does NOT require OpenCLI; only the live
    ``--publish`` push (which drives a logged-in creator session via CDP) needs it.
    """
    package = build_package(
        assets, canonical_url, code_url=code_url, project_url=project_url, title=title
    )
    publisher = XhsPublisher(Path("data"))
    staged = publisher.stage(package)
    if not staged.get("ok"):
        return {"ok": False, "stage_error": staged}

    if not publish:
        return staged

    if not opencli_runtime.is_available():
        raise RenderError("OpenCLI not found; set OPENCLI_NODE and OPENCLI_MAIN")
    return publisher.publish(staged["staged_id"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a Xiaohongshu draft from a parsed paper")
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--data-root", type=Path, default=Path("data"))
    parser.add_argument("--canonical-url", default="")
    parser.add_argument("--code-url", default="", help="GitHub / code link (e.g. https://github.com/microsoft/Loopsbench)")
    parser.add_argument("--project-url", default="", help="Project page (e.g. https://loopsbench.ai/)")
    parser.add_argument("--title", default="", help="Override the auto-generated note title (XHS limit 20 chars)")
    parser.add_argument("--publish", action="store_true", help="also push to XHS draft box (requires login)")
    args = parser.parse_args()

    assets = load_assets(args.paper_id, Path.cwd())
    result = deliver_draft(
        assets,
        canonical_url=args.canonical_url,
        code_url=args.code_url,
        project_url=args.project_url,
        publish=args.publish,
        title=args.title,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

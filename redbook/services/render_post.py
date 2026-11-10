"""统一内容生产入口（落地 docs/publishing-pipeline-diagnosis.md §4.1）。

``render_post(platform, summary, figures)`` 是小红书论文帖**唯一**的内容生成入口。
此前仓库里有三条互不相同的生成路径，导致两台机器/两个 IDE 产出的草稿差异巨大：

1. ``PersonaPostComposer`` → ``redbook.cli compose-post``       （Codex 走）
2. 手写 ``BODY`` + ``PublicationPackage`` + ``XhsPublisher``    （WorkBuddy 走）
3. ``content_composer.compose_content`` 的冻结 7 段口径         （另一条验收线）

现在 1 收敛为本模块的薄调用方，2 由 ``render_package`` 从同一份 post 组装；
``compose-post`` 与 ``XhsPublisher.validate`` 共用
``xhs_content_gate`` + ``config/xhs_content_rules.yaml`` 的同一份闸门规则。

分工边界：
- ``render_post``            → 生成内容 + 内容闸门（纯文本/字数/局限段/话题）
- ``XhsPublisher.validate`` → 发布闸门（在前者之上再查图片数与目检标记）
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .persona_composer import PersonaPostComposer
from .xhs_content_gate import ContentSpecError, load_rules, validate_xhs_content, validate_xhs_post


def _as_summary_markdown(summary: str | Mapping[str, str]) -> str:
    """接受 MinerU/paper_brief 的 Markdown 字符串，或 {题头: 段落} 映射。"""
    if isinstance(summary, str):
        return summary
    return "\n\n".join(f"## {key}\n{value}" for key, value in summary.items())


def _as_image_paths(figures: Sequence[Any] | None) -> list[str]:
    """归一化图片资产：路径字符串 / Path / 含 path 或 image_file 键的 dict。"""
    result: list[str] = []
    for item in figures or ():
        if isinstance(item, Mapping):
            item = item.get("path") or item.get("image_file") or ""
        if item:
            result.append(str(item))
    return result


def _adopt_post(platform: str, body: str, figures: Sequence[Any] | None, *,
                arxiv_id: str, title: str, topics: Sequence[str] | None,
                visual_review: str | None, metadata: Mapping[str, Any] | None,
                source: str, rules: Mapping[str, Any]) -> dict[str, Any]:
    """人工定稿正文分支：跳过 PersonaPostComposer，只过同一份发布闸门。

    14 篇已发布的 note 是逐字打磨的中文正文（钩子、局限段、口语化改写），
    若塞回 persona 模板会退化成填表稿。因此「内容生成」与「内容准入」在此
    解耦：body 由 note spec 提供，本模块只负责校验与组装，出口仍是 render_package。
    """
    post_metadata: dict[str, Any] = {
        "visual_review": visual_review or "",
        "source": source,
        "persona_id": "handwritten",
    }
    if metadata:
        post_metadata.update(dict(metadata))
    post: dict[str, Any] = {
        "platform": platform,
        "paper_id": arxiv_id,
        "persona_id": "handwritten",
        "persona_selection_reason": "note spec 提供人工定稿正文，跳过模板生成",
        "title": title,
        "body": body,
        "topics": [str(item) for item in (topics or ())],
        "comment_prompt": "",
        "generation_prompt": "",
        "images": _as_image_paths(figures),
        "metadata": post_metadata,
    }
    errors = validate_xhs_post(post, require_visual_review=True, rules=rules)
    if errors:
        raise ContentSpecError("xhs content gate failed: " + "; ".join(errors))
    return post


def render_post(
    platform: str,
    summary: str | Mapping[str, str] | None = None,
    figures: Sequence[Any] | None = None,
    *,
    arxiv_id: str = "",
    persona_id: str = "research_translator",
    github_url: str = "",
    paper_title: str = "",
    topics: Sequence[str] | None = None,
    visual_review: str | None = None,
    metadata: Mapping[str, Any] | None = None,
    rules_path: Path | None = None,
    body: str | None = None,
    title: str = "",
    source: str = "render_post",
) -> dict[str, Any]:
    """生成一篇受仓库闸门约束的平台帖子，返回可直接落盘的 dict。

    ``summary`` 是论文事实摘要（MinerU Markdown 或分节映射）；``figures``
    是已选好的图片资产。传入 ``body`` 时走「人工定稿正文」分支：不调用
    persona 模板，正文由 ``redbook/notes/<paper_id>.yaml`` 提供，只过闸门。
    两条分支共用同一份规则、同一个 ``render_package`` 出口，不产生第二条内容路径。

    生成的 dict 同时兼容两条投递路径：

    - ``redbook.cli save-xhs-draft --draft`` 读 ``title`` / ``body`` / ``topics``
    - ``render_package()`` 读全量字段组装 ``PublicationPackage``

    内容不合规时抛 :class:`ContentSpecError`，不产出半合规草稿。
    """
    if platform != "xhs":
        raise NotImplementedError(
            f"render_post supports 'xhs' only for now, got {platform!r}; "
            "add a platform branch in render_post.py instead of reviving a second content path"
        )
    spec = load_rules(rules_path)
    if body is not None:
        return _adopt_post(
            platform, body, figures, arxiv_id=arxiv_id, title=title, topics=topics,
            visual_review=visual_review, metadata=metadata, source=source, rules=spec,
        )
    if summary is None:
        raise ContentSpecError("render_post needs either a summary or a handwritten body")
    draft = PersonaPostComposer().compose(
        _as_summary_markdown(summary), arxiv_id, persona_id, github_url, paper_title
    )
    chosen_topics = [str(item) for item in (topics if topics is not None else draft.topics)]
    post_metadata: dict[str, Any] = {
        "visual_review": visual_review or "pending",
        "source": source,
        "persona_id": draft.persona_id,
    }
    if metadata:
        post_metadata.update(dict(metadata))

    post: dict[str, Any] = {
        "platform": platform,
        "paper_id": arxiv_id,
        "persona_id": draft.persona_id,
        "persona_selection_reason": draft.persona_selection_reason,
        "title": draft.title,
        "body": draft.body,
        "topics": chosen_topics,
        "comment_prompt": draft.comment_prompt,
        "generation_prompt": draft.generation_prompt,
        "images": _as_image_paths(figures),
        "metadata": post_metadata,
    }

    errors = validate_xhs_content(post["body"], post["topics"], rules=spec)
    if not post["title"] or len(post["title"]) > int(spec["title_max_chars"]):
        errors.append(f"title must be 1-{spec['title_max_chars']} chars, got {len(post['title'])}")
    if errors:
        raise ContentSpecError("xhs content gate failed: " + "; ".join(errors))
    return post


def render_package(
    post: Mapping[str, Any],
    *,
    canonical_url: str,
    links: Mapping[str, str] | None = None,
    pdf_path: str | Path | None = None,
    review_status: str = "pending",
):
    """把 render_post 的产物组装成 PublicationPackage（唯一的投递载体）。

    图片目检标记随 ``metadata`` 一起带过去，``XhsPublisher.validate`` 会强制核验。
    """
    from ..automation.publishing import PublicationPackage

    metadata = dict(post.get("metadata") or {})
    metadata["topics"] = list(post.get("topics") or ())
    if pdf_path is not None:
        metadata["pdf_path"] = str(pdf_path)
    return PublicationPackage(
        paper_id=str(post.get("paper_id", "")),
        platform=str(post.get("platform", "xhs")),
        canonical_url=canonical_url,
        title=str(post["title"]),
        body_markdown=str(post["body"]),
        image_paths=list(post.get("images") or ()),
        links=dict(links or {}),
        metadata=metadata,
        review_status=review_status,
    )

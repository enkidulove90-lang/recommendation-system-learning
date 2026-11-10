"""小红书论文帖发布闸门：把用户级 skill 铁律下沉为仓库内可执行的校验。

规则数据只存在 ``config/xhs_content_rules.yaml``，本模块不含硬编码常量。
三个调用方共用同一份规则：

- ``redbook.services.render_post.render_post``  → 内容生成后自查
- ``redbook.cli compose-post``                  → 走 render_post，间接受约束
- ``XhsPublisher.validate``                    → stage/publish 前强制闸门

与 ``redbook.services.content_spec``（2026-10-28 冻结的 7 段口径、明确
"不限制总字数"）是**两层不同的契约**：content_spec 管正文结构组装，
本模块管平台发布准入。不要互相替换，也不要把 1000 字上限塞回 content_spec。
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

#: 仓库根 config/。刻意用 .yaml 而非 .json：根 .gitignore 有 ``*.json``，
#: 规则文件必须能被 git 跟踪，否则另一台机器/另一个 IDE 拉不到同一份约束。
RULES_PATH = Path(__file__).resolve().parents[2] / "config" / "xhs_content_rules.yaml"


class ContentSpecError(ValueError):
    """内容未通过发布闸门；render_post 用它中止生成，不产出半合规草稿。"""


def load_rules(path: Path | None = None) -> dict[str, Any]:
    """加载单一事实源；缺失文件或字段时直接报错，不静默降级。"""
    source = path or RULES_PATH
    rules = yaml.safe_load(source.read_text(encoding="utf-8")) or {}
    for key in ("title_max_chars", "body_max_chars", "forbidden_body_markers",
                "required_section_keywords", "topic_allowlist", "visual_review_key"):
        if key not in rules:
            raise ContentSpecError(f"xhs content rules missing key {key!r}: {source}")
    return rules


def normalize_topic(topic: str) -> str:
    """话题归一：去 #、去空白、casefold，与 delivery._norm 口径一致。"""
    return str(topic).lstrip("#").replace(" ", "").strip().casefold()


def validate_xhs_content(body: str, topics: Sequence[str] | None = None,
                         *, rules: Mapping[str, Any] | None = None) -> list[str]:
    """内容四条铁律：纯文本、字数上限、局限段、话题白名单。返回错误列表。"""
    spec = dict(rules or load_rules())
    errors: list[str] = []

    for marker in spec["forbidden_body_markers"]:
        if marker in body:
            errors.append(
                f"body contains {marker!r}: Xiaohongshu renders plain text only; "
                "remove Markdown syntax and bind topics via real platform entities"
            )

    limit = int(spec["body_max_chars"])
    if len(body) > limit:
        errors.append(f"body is {len(body)} chars, over the {limit}-char hard limit")

    short_lines = [line.strip() for line in body.splitlines() if len(line.strip()) <= 24]
    for keyword in spec["required_section_keywords"]:
        if not any(keyword in line for line in short_lines):
            errors.append(f"body must contain a dedicated '{keyword}' section (short header line)")

    allowed = {normalize_topic(item) for item in spec["topic_allowlist"]}
    for topic in topics or ():
        if normalize_topic(topic) not in allowed:
            errors.append(
                f"topic {topic!r} is not in config/xhs_content_rules.yaml allowlist; "
                "use a real vertical topic entity instead of a traffic tag"
            )
    return errors


def validate_visual_review(metadata: Mapping[str, Any] | None = None,
                           *, rules: Mapping[str, Any] | None = None) -> list[str]:
    """图片目检标记：必须显式记录逐张目视结果，不能缺失或停在 pending。"""
    spec = dict(rules or load_rules())
    key = str(spec["visual_review_key"])
    value = (metadata or {}).get(key)
    pending = {str(item).strip().casefold() for item in spec.get("visual_review_pending_values", ())}
    if value is None or str(value).strip().casefold() in pending:
        return [f"metadata.{key} must record an actual per-image visual review; "
                "add it after inspecting every image (see redbook/docs/xhs-content-spec.md)"]
    return []


def validate_xhs_post(post: Mapping[str, Any], *, require_visual_review: bool = True,
                      rules: Mapping[str, Any] | None = None) -> list[str]:
    """完整准入检查（标题/正文/话题/图片数/目检标记），供 render_post 使用。"""
    spec = dict(rules or load_rules())
    errors: list[str] = []
    title = str(post.get("title", ""))
    if not title or len(title) > int(spec["title_max_chars"]):
        errors.append(f"title must be 1-{spec['title_max_chars']} chars, got {len(title)}")

    errors.extend(validate_xhs_content(str(post.get("body", "")),
                                      post.get("topics") or (), rules=spec))

    images = list(post.get("images") or ())
    if not int(spec["images_min"]) <= len(images) <= int(spec["images_max"]):
        errors.append(f"image count {len(images)} outside "
                      f"{spec['images_min']}-{spec['images_max']}")
    if require_visual_review:
        errors.extend(validate_visual_review(post.get("metadata"), rules=spec))
    return errors

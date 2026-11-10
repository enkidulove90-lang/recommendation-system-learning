"""内容生成层：按冻结 7 段口径组装论文帖（2026-10-28）。

- ``compose_content()`` 输出固定 7 段正文 + 已校验标题。
- 标题：先判 venue；有 venue 走 ``【VenueAlias Year】Hook``，无 venue 只产 Hook。
- 缺失段统一写 ``原文未披露``（标题除外）；组装结果必须通过 ``content_spec`` 自校验。
- 路线二手写的 10 段模板不作为默认或可选模板（已作废旧口径）。
"""
from __future__ import annotations

from collections.abc import Mapping

from redbook.services.content_spec import (
    PLACEHOLDER,
    SECTION_HEADERS,
    validate_body,
    validate_title,
)


def compose_content(
    sections: Mapping[str, str],
    *,
    venue: str | None = None,
    year: int | str | None = None,
    hook: str = "",
) -> dict[str, str]:
    """按 7 段固定结构组装正文并生成校验后的标题。

    ``sections`` 以 ``content_spec.SECTION_HEADERS`` 的题头字符串为键；
    缺失或空段自动写 ``原文未披露``。返回 ``{"title": ..., "body": ...}``。
    """
    filled = {
        header: (sections.get(header) or "").strip() or PLACEHOLDER
        for header in SECTION_HEADERS
    }
    body = "\n\n".join(f"{header}\n{filled[header]}" for header in SECTION_HEADERS)
    validate_body(body)
    title = validate_title(venue=venue, year=year, hook=hook)
    return {"title": title, "body": body}

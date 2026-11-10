"""冻结的论文帖内容规范（2026-10-28 口径，不再反复）。

标题规则：
- 有会议/期刊：标题 = ``【VenueAlias Year】Hook``；年份缺失写 ``【VenueAlias 年份未披露】`` 并告警。
- 无 venue：标题 = 纯 Hook；不写 ``【】``、不写 ``原文未披露``、不写 arXiv 标识。
- **平台 20 字上限为硬预算，前缀计入**：合成标题超过 20 个显示字符抛 ``TitleHookLengthError``。
- Hook：无 venue 时 15-20（只计汉字/字母/数字，标点、空白、emoji 不计）；有 venue 时前缀
  消耗预算，Hook 只要求非空，总长不超过 20 显示字符。
- VenueAlias 必须在 ``config/venue_alias.json`` 登记，未登记抛 ``VenueAliasUnregistered``。

正文规则：
- 固定 7 段，顺序固定，每段非空；缺失写 ``原文未披露``，禁止虚构。
- 不限制总字数/分段字数；字数只作日志指标。
- 纯文本禁 Markdown；正文禁止 ``#``；话题只走真实实体绑定（投递层闸门）。

失败码：
- ``VenueAliasUnregistered`` / ``TitleHookLengthError``（含 Hook 区间与 20 字总预算两种失败）
  / ``TemplateSectionMissing`` / ``HashtagInBodyError`` / ``MarkdownInBodyError``
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

#: 固定 7 段题头（顺序即正文段序，题头行必须与常量整行相等）。
SECTION_HEADERS: tuple[str, ...] = (
    "📌 解决什么问题",
    "✨ 创新点/贡献",
    "🧪 Benchmark",
    "⚙️ 实验条件",
    "📊 效果",
    "📎 arXiv",
    "💻 GitHub",
)

#: 段内容缺失时的统一占位（仅用于正文段；标题不使用）。
PLACEHOLDER = "原文未披露"

#: Hook 有效字数（只计汉字/字母/数字）。
HOOK_MIN, HOOK_MAX = 15, 20

#: 平台标题硬限制（显示字符数），前缀计入预算。
PLATFORM_TITLE_LIMIT = 20

#: venue 别名表默认路径（仓库根 config/venue_alias.json）。
_VENUE_ALIAS_PATH = Path(__file__).resolve().parents[2] / "config" / "venue_alias.json"

#: 视为 Markdown 的最小特征集（正文出现即失败）。
_MARKDOWN_MARKERS: tuple[str, ...] = ("**", "__", "~~", "`", "](")


class VenueAliasUnregistered(ValueError):
    """venue 未在 venue_alias.json 登记。"""


class TitleHookLengthError(ValueError):
    """Hook 有效字数不在 15-20 区间。"""


class TemplateSectionMissing(ValueError):
    """7 段缺段、空段或段序错误。"""


class HashtagInBodyError(ValueError):
    """正文出现 ``#``。"""


class MarkdownInBodyError(ValueError):
    """正文出现 Markdown 特征。"""


def load_venue_alias(path: Path | None = None) -> dict[str, str]:
    """加载 venue 别名表（键已 casefold）。"""
    source = path or _VENUE_ALIAS_PATH
    data = json.loads(source.read_text(encoding="utf-8"))
    return {str(key).strip().casefold(): str(value).strip() for key, value in data["aliases"].items()}


def hook_weight(text: str) -> int:
    """Hook 有效字数：只计汉字/字母/数字；标点、空白、emoji 不计。"""
    return sum(1 for ch in text if ch.isalnum())


def validate_hook(hook: str) -> int:
    """硬校验 Hook 长度，返回有效字数。"""
    count = hook_weight(hook)
    if not HOOK_MIN <= count <= HOOK_MAX:
        raise TitleHookLengthError(
            f"hook counts {count} chars (letters/digits/CJK only), must be {HOOK_MIN}-{HOOK_MAX}: {hook!r}"
        )
    return count


def validate_title(venue: str | None, year: int | str | None, hook: str) -> str:
    """按冻结口径合成标题并校验，返回最终标题文本。

    平台 20 字上限是硬预算：前缀（含括号/空格/年份）计入，因此有 venue 时
    Hook 不再要求 15-20，只需非空且 ``前缀+Hook`` 总显示字符 ≤ 20。
    """
    if venue is None:
        validate_hook(hook)
        title = hook
    else:
        alias = load_venue_alias().get(venue.strip().casefold())
        if alias is None:
            raise VenueAliasUnregistered(
                f"venue {venue!r} is not registered in config/venue_alias.json; register it first"
            )
        year_text = str(year).strip() if year is not None else ""
        if year_text:
            prefix = f"【{alias} {year_text}】"
        else:
            prefix = f"【{alias} 年份未披露】"
            logging.warning("venue %s has no year; title uses 年份未披露", alias)
        if not hook.strip():
            raise TitleHookLengthError("hook is required alongside the venue prefix")
        title = prefix + hook
    if len(title) > PLATFORM_TITLE_LIMIT:
        raise TitleHookLengthError(
            f"composed title is {len(title)} display chars, over the hard platform budget of "
            f"{PLATFORM_TITLE_LIMIT} (the venue prefix counts into the budget): {title!r}"
        )
    return title


def _section_slices(body: str) -> list[tuple[str, int, int]]:
    """定位 7 段题头行，返回 (题头, 起始行, 结束行) 列表。"""
    lines = body.splitlines()
    positions: list[int] = []
    for header in SECTION_HEADERS:
        match = next((i for i, line in enumerate(lines) if line.strip() == header), None)
        if match is None:
            continue
        if positions and match <= positions[-1]:
            raise TemplateSectionMissing(f"section {header!r} appears out of order")
        positions.append(match)
    missing = [header for header in SECTION_HEADERS
               if not any(lines[i].strip() == header for i in positions)]
    if missing:
        raise TemplateSectionMissing(f"missing sections: {missing}")
    bounds = positions + [len(lines)]
    return [(header, start, bounds[i + 1])
            for i, (header, start) in enumerate(zip(SECTION_HEADERS, positions))]


def validate_body(body: str) -> None:
    """校验正文 7 段结构/占位/禁则；字数只记日志，不做闸门。"""
    if "#" in body:
        raise HashtagInBodyError("body contains '#'; topics must bind via real platform entities only")
    for marker in _MARKDOWN_MARKERS:
        if marker in body:
            raise MarkdownInBodyError(f"body contains markdown marker {marker!r}")
    for header, start, end in _section_slices(body):
        content = "\n".join(body.splitlines()[start + 1:end]).strip()
        if not content:
            raise TemplateSectionMissing(f"section {header!r} is empty")
    logging.info("body length metric: %d chars (advisory only)", len(body))

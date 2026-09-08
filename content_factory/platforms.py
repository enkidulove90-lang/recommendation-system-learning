"""Stage 6 多平台适配（M12 多平台文案改写规则执行器）。

每平台规则来自 platforms.yaml（长度上限 / 语气 / emoji 策略 / 是否陈述句 / 话题上限）。
LLM 改写交给既有 redbook 渲染层；本模块只做「规则即代码」的硬约束改写，
与 docs/content-factory-engineering.md §6.2 一致。
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

_EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002700-\U000027BF\U0001F1E6-\U0001F1FF\u2600-\u27BF]"
)

DEFAULT_PLATFORM = {
    "max_title_len": 64,
    "tone": "neutral",
    "emoji": "allow",
    "statement_only": False,
    "topics_max": 10,
}


class PlatformAdapter:
    def __init__(self, config: dict[str, Any]) -> None:
        self._cfg = config

    @classmethod
    def from_file(cls, path: str | Path) -> "PlatformAdapter":
        p = Path(path)
        if not p.is_file():
            return cls({})
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        return cls(data.get("platforms", {}))

    def adapt(self, platform: str, title: str, lead: str = "") -> dict[str, Any]:
        rules = {**DEFAULT_PLATFORM, **(self._cfg.get(platform, {}) or {})}
        new_title = title

        # 长度硬约束
        max_len = int(rules.get("max_title_len", 64))
        if len(new_title) > max_len:
            new_title = new_title[: max_len - 1] + "…"

        # emoji 策略
        if rules.get("emoji") == "forbid":
            new_title = _EMOJI_RE.sub("", new_title).strip()

        # 是否必须为陈述句（如 HN）：去掉末尾问号
        if rules.get("statement_only"):
            new_title = re.sub(r"[?？]+$", "", new_title).strip()

        # 导语长度提示（不截断正文，仅提示）
        topics_max = int(rules.get("topics_max", 10))
        return {
            "platform": platform,
            "title": new_title,
            "lead": lead,
            "tone": rules.get("tone", "neutral"),
            "topics_max": topics_max,
            "changed": new_title != title,
        }


def load_platforms(path: str | Path) -> PlatformAdapter:
    return PlatformAdapter.from_file(path)

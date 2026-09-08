"""L1/L2 共用类型：ThemeTokens（双轨单一事实源）+ CardNode + Document。

ThemeTokens 同时服务两条轨道：
- A 轨：``color()`` / ``font()`` 返回可直接内联进 style 的字符串；
- B 轨：``to_satori()`` 返回 Satori 需要的数值/色值 JSON。
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Union

from ..tokens import derive_tokens, load_theme_raw

CJK = "一-鿿㐀-䶿"


def leaf(text: str) -> str:
    """把含中文的文字节点用 <span leaf=""> 包裹（公众号粘贴保样式的铁律）。

    纯英文/数字/URL 不包裹（避免误伤代码与链接），仅含 CJK 才包。
    """
    for ch in text:
        if "一" <= ch <= "鿿" or "㐀" <= ch <= "䶿":
            return f'<span leaf="">{text}</span>'
    return text


def wrap_cjk(text: str) -> str:
    """按句/词切分，对含中文的片段逐个 leaf 包裹（A 轨正文用）。"""
    out, buf = [], []
    for ch in text:
        buf.append(ch)
    # 简单策略：整体含中文则整体包；否则原样。细粒度切分交由组件在已知结构处处理。
    return leaf(text)


@dataclass
class ThemeTokens:
    name: str
    raw: Dict[str, Any]
    colors: Dict[str, str] = field(default_factory=dict)
    type: Dict[str, Any] = field(default_factory=dict)
    spacing: Dict[str, Any] = field(default_factory=dict)
    radius: int = 8
    brand: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, name: str) -> "ThemeTokens":
        raw = derive_tokens(load_theme_raw(name))
        return cls(
            name=raw["name"],
            raw=raw,
            colors=raw["colors"],
            type=raw["type"],
            spacing=raw["spacing"],
            radius=raw["radius"],
            brand=raw["brand"],
        )

    # —— A 轨：内联样式取值 ——
    def color(self, key: str, default: str = "#000000") -> str:
        return self.colors.get(key, default)

    def font(self, role: str) -> float:
        return self.type["roles"].get(role, self.type["roles"]["body"])

    def px(self, key: str) -> str:
        return f"{self.type['roles'].get(key, self.type['roles']['body'])}px"

    def space(self, mult: int = 1) -> int:
        return int(self.spacing.get("base", 8)) * mult

    # —— B 轨：Satori JSON ——
    def to_satori(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "colors": self.colors,
            "type": self.type,
            "spacing": self.spacing,
            "radius": self.radius,
            "brand": self.brand,
        }


@dataclass
class CardNode:
    """B 轨卡片块（平台无关），由 to_card 产出，再由 card 渲染器落 HTML/SVG。"""
    type: str
    style: Dict[str, Any] = field(default_factory=dict)
    children: List[Union["CardNode", str]] = field(default_factory=list)
    text: str = ""

    def add(self, *kids: Union["CardNode", str]) -> "CardNode":
        self.children.extend(kids)
        return self


@dataclass
class Block:
    """结构化文档的一个块：组件名 + props。"""
    type: str
    props: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Document:
    """双轨文档模型：一组 Block + 元信息。两轨共用，保证视觉一致。"""
    title: str = ""
    subtitle: str = ""
    theme: str = "recsys-blue"
    blocks: List[Block] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)

    def add(self, type: str, **props) -> "Document":
        self.blocks.append(Block(type=type, props=props))
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "theme": self.theme,
            "meta": self.meta,
            "blocks": [{"type": b.type, "props": b.props} for b in self.blocks],
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Document":
        doc = cls(title=d.get("title", ""), subtitle=d.get("subtitle", ""),
                  theme=d.get("theme", "recsys-blue"), meta=d.get("meta", {}))
        for b in d.get("blocks", []):
            doc.blocks.append(Block(type=b["type"], props=b.get("props", {})))
        return doc

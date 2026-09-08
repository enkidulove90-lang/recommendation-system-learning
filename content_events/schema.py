"""内容事件编排层 —— 核心数据模型（schema）。

对应设计文档 docs/content-event-orchestration-design.md §2/§3。
- EventType：内容生命周期事件（M18 视角）
- ContentState：状态机状态（合并内容工厂 §5.3 与发布设计 04 review_status）
- ContentItem：队列事实包 + content_hash 幂等键
- content_hash：paper_id + platform + 关键字段的确定性指纹
仅依赖标准库，便于单测与无依赖运行。
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class EventType(str, Enum):
    CONTENT_INTAKE = "content_intake"
    RENDER_REQUEST = "render_request"
    RENDERED = "rendered"
    VALIDATED = "validated"
    STAGED = "staged"
    PUBLISHED = "published"
    FEEDBACK_SAMPLED = "feedback_sampled"
    DECISION_MADE = "decision_made"
    ARCHIVED = "archived"
    NEEDS_REVIEW = "needs_review"


class ContentState(str, Enum):
    DRAFT = "draft"
    RENDERED = "rendered"
    VALIDATED = "validated"
    STAGED = "staged"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    NEEDS_REVIEW = "needs_review"


PLATFORMS = ("xhs", "wechat", "zhihu_answer", "x_thread", "jike", "notion", "blog")


@dataclass
class ContentItem:
    """队列事实包（复用设计 04 §统一 Publisher 输入）。"""

    paper_id: str
    platform: str
    canonical_url: str = ""
    title: str = ""
    body_markdown: str = ""
    image_paths: List[str] = field(default_factory=list)
    links: Dict[str, str] = field(default_factory=dict)
    review_status: str = "pending"  # pending | approved | needs_review
    source_attribution: str = "图表摘自论文，仅作学术解读"
    content_hash: str = ""
    state: ContentState = ContentState.DRAFT
    external_id: str = ""
    errors: List[str] = field(default_factory=list)

    @staticmethod
    def from_queue_json(data: Dict[str, Any]) -> "ContentItem":
        item = ContentItem(
            paper_id=str(data.get("paper_id", "")),
            platform=str(data.get("platform", "")),
            canonical_url=str(data.get("canonical_url", "")),
            title=str(data.get("title", "")),
            body_markdown=str(data.get("body_markdown", "")),
            image_paths=list(data.get("image_paths", []) or []),
            links=dict(data.get("links", {}) or {}),
            review_status=str(data.get("review_status", "pending")),
            source_attribution=str(
                data.get("source_attribution", "图表摘自论文，仅作学术解读")
            ),
        )
        item.content_hash = content_hash(item)
        return item

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "paper_id": self.paper_id,
            "platform": self.platform,
            "canonical_url": self.canonical_url,
            "title": self.title,
            "body_markdown": self.body_markdown,
            "image_paths": self.image_paths,
            "links": self.links,
            "review_status": self.review_status,
            "source_attribution": self.source_attribution,
            "content_hash": self.content_hash,
            "state": self.state.value,
            "external_id": self.external_id,
            "errors": self.errors,
        }
        return d

    @property
    def idem_key(self) -> str:
        """幂等键（设计 04 §风控 2）：paper_id::platform::content_hash。"""
        return f"{self.paper_id}::{self.platform}::{self.content_hash}"


def content_hash(item: ContentItem) -> str:
    """确定性指纹：标题 + 正文 + 图片路径 + 链接。忽略 state/external_id 等运行态。"""
    payload = json.dumps(
        {
            "paper_id": item.paper_id,
            "platform": item.platform,
            "title": item.title,
            "body_markdown": item.body_markdown,
            "image_paths": sorted(item.image_paths),
            "links": dict(sorted(item.links.items())),
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def fs_safe(s: str) -> str:
    """把任意字符串转为文件系统安全名（Windows 禁止 < > : " / \\ | ? * 及控制字符）。

    idem_key 形如 'arxiv:3806231::xhs::<hash>'，含冒号在 Windows 非法，必须转义才能做目录/文件名。
    幂等逻辑仍用原始 idem_key（在内存/JSON 中），仅落盘路径用本函数。
    """
    illegal = '<>:"/\\|?*\t\n\r\x00'
    out = []
    for ch in s:
        out.append("_" if ch in illegal or ord(ch) < 32 else ch)
    return "".join(out)


@dataclass
class ContentEvent:
    """不可变内容生命周期事件（追加到 events.jsonl）。"""

    type: EventType
    item_key: str
    ts: str
    detail: Dict[str, Any] = field(default_factory=dict)

    def to_line(self) -> str:
        return json.dumps(
            {
                "type": self.type.value,
                "item_key": self.item_key,
                "ts": self.ts,
                "detail": self.detail,
            },
            ensure_ascii=False,
        )

    @classmethod
    def from_line(cls, line: str) -> "ContentEvent":
        d = json.loads(line)
        return cls(
            type=EventType(d["type"]),
            item_key=d["item_key"],
            ts=d["ts"],
            detail=d.get("detail", {}),
        )


@dataclass
class RunSummary:
    """一次 process-queue 运行的聚合摘要（O6 可观测性）。

    scanned：扫到的队列目录数
    processed：成功推进到 staged/published 的项数
    skipped_idempotent：因幂等（已终态）跳过的项数
    skipped_other：因无包/坏包等跳过
    needs_review：进入 needs_review 的项数
    published：真实 published 项数（沙箱通常为 0）
    errors：处理中抛出的未预期错误数
    """

    scanned: int = 0
    processed: int = 0
    skipped_idempotent: int = 0
    skipped_other: int = 0
    needs_review: int = 0
    published: int = 0
    errors: int = 0
    skipped_detail: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, object]:
        return {
            "scanned": self.scanned,
            "processed": self.processed,
            "skipped_idempotent": self.skipped_idempotent,
            "skipped_other": self.skipped_other,
            "needs_review": self.needs_review,
            "published": self.published,
            "errors": self.errors,
        }

    def render(self) -> str:
        return (
            f"扫描 {self.scanned} | 处理 {self.processed} | "
            f"幂等跳过 {self.skipped_idempotent} | 其他跳过 {self.skipped_other} | "
            f"需人工 {self.needs_review} | 已发布 {self.published} | 错误 {self.errors}"
        )

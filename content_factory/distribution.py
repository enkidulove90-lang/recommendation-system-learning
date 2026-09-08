"""Stage 7 发布 + 线上 A/B（M13 定时发布 / M14 canonical 同步 / M16 组件级 A/B）。

选型对齐 docs/content-factory-engineering.md：
  M13 Buffer / CoSchedule / Later API          报告 23
  M14 Dev.to / Hashnode canonical 同步         报告 24
  M16 @appnest/ab-test（接 GA4）               报告 27

设计原则（与既有 content_factory 一致）：外部服务需 API key，适配器可插拔；
无 key / dry_run 时只产出结构化 payload + curl 占位，绝不触网，全部单测离线可跑。
真实发布由运营在拿到 key 后执行 publish()（或贴出 curl 占位手动执行）。
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class DistributionJob:
    platform: str
    adapter: str
    payload: dict[str, Any]
    scheduled_at: Optional[str]
    bound_fields: list[str] = field(default_factory=list)
    offline_stub: str = ""        # 有 key 时可直接执行的 curl 命令
    status: str = "planned"       # planned | published | failed

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class BaseAdapter:
    name = "base"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key

    # 子类实现：从一篇平台包构造 payload + 离线 stub
    def schedule(self, package: dict[str, Any], **kw: Any) -> DistributionJob:
        raise NotImplementedError

    def publish(self, job: DistributionJob, dry_run: bool = True) -> dict[str, Any]:
        """dry_run=True（默认）只返回计划；dry_run=False 且有 key 才真实触网。"""
        if dry_run or not self.api_key:
            return {"status": "planned", "mode": "offline", "stub": job.offline_stub,
                    "payload": job.payload}
        # 真实发布：延迟导入 requests，避免无网络环境硬依赖
        try:
            import requests  # type: ignore
        except Exception:
            return {"status": "planned", "mode": "offline-no-requests", "stub": job.offline_stub}
        return {"status": "skipped-real-call", "mode": "live-stub",
                "note": "请按 offline_stub 的 curl 执行，或在此接入 requests.post"}


class BufferAdapter(BaseAdapter):
    """M13 定时发布（Buffer API）。"""

    name = "Buffer"
    _ENDPOINT = "https://api.bufferapp.com/1/updates/create.json"

    def schedule(self, package: dict[str, Any], at: Optional[str] = None,
                 profile_ids: Optional[list[str]] = None) -> DistributionJob:
        text = f"{package.get('title', '')}\n\n{package.get('body_markdown', '')[:280]}"
        payload = {
            "profile_ids": profile_ids or [],
            "text": text,
            "scheduled_at": at,
            "media": {"link": (package.get("links") or {}).get("paper", "")},
        }
        stub = (
            f"curl -X POST '{self._ENDPOINT}' \\\n"
            f"  -H 'Authorization: Bearer $BUFFER_API_KEY' \\\n"
            f"  -d 'profile_ids={json.dumps(payload['profile_ids'])}' \\\n"
            f"  -d 'text={text!r}'"
        )
        return DistributionJob(
            platform=package.get("platform", "buffer"), adapter=self.name,
            payload=payload, scheduled_at=at,
            bound_fields=(package.get("metadata") or {}).get("bound_fields", {}).get("hook", []),
            offline_stub=stub,
        )


class DevToAdapter(BaseAdapter):
    """M14 canonical 同步（Dev.to API，先源站 2–10 天再跨发）。"""

    name = "Dev.to"
    _ENDPOINT = "https://dev.to/api/articles"

    def schedule_canonical(self, package: dict[str, Any],
                           canonical_url: Optional[str] = None) -> DistributionJob:
        # canonical 指向源站（如公众号/官网），避免 SEO 惩罚
        canonical = canonical_url or (package.get("links") or {}).get("paper", "")
        body = package.get("body_markdown", "")
        tags = (package.get("metadata") or {}).get("title_variants", [])
        article = {
            "title": package.get("title", ""),
            "body_markdown": body,
            "published": False,           # 默认存草稿，运营审核后发布
            "canonical_url": canonical,
            "tags": ["recsys", "ml", "paper"],
            "series": None,
        }
        stub = (
            f"curl -X POST '{self._ENDPOINT}' \\\n"
            f"  -H 'api-key: $DEVTO_API_KEY' \\\n"
            f"  -H 'Content-Type: application/json' \\\n"
            f"  -d @devto_article.json   # 见 payload.article"
        )
        return DistributionJob(
            platform="devto", adapter=self.name,
            payload={"article": article, "endpoint": self._ENDPOINT},
            scheduled_at=None,
            bound_fields=(package.get("metadata") or {}).get("bound_fields", {}).get("hook", []),
            offline_stub=stub,
        )


class AppnestABAdapter(BaseAdapter):
    """M16 组件级 A/B（@appnest/ab-test，接 GA4）。"""

    name = "appnest-ab-test"

    def assign(self, experiment: str, variants: list[str],
               package: dict[str, Any]) -> DistributionJob:
        # 稳定随机分配（同一 platform 种子 → 同一变体，构建期可复现；
        # 真实读者侧由前端 snippet 按 session 重新分配并写 ab_assign 事件）
        from .analytics import AnalyticsSpec
        session_seed = f"{experiment}:{package.get('platform', 'web')}"
        variant, ab_event = AnalyticsSpec().assign_ab_variant(
            experiment, variants, session_id=session_seed)
        payload = {
            "experiment": experiment,
            "variants": variants,
            "assigned_variant": variant,
            "ga4_event": "ab_assign",
            "ga4_params": ab_event,
            "web_component": "<ab-test experiment=\"%s\"></ab-test>" % experiment,
        }
        stub = (
            f"# 在页面注入 <ab-test experiment=\"{experiment}\"> 组件，"
            f"选择事件自动上报 GA4 事件 ab_assign（variant={variant}）"
        )
        return DistributionJob(
            platform=package.get("platform", "web"), adapter=self.name,
            payload=payload, scheduled_at=None,
            bound_fields=(package.get("metadata") or {}).get("bound_fields", {}).get("hook", []),
            offline_stub=stub,
        )


class Distributor:
    """编排器：把若干平台包转成发布 + 同步 + A/B 作业。"""

    def __init__(self, buffer_key: Optional[str] = None, devto_key: Optional[str] = None) -> None:
        self.buffer = BufferAdapter(buffer_key)
        self.devto = DevToAdapter(devto_key)
        self.ab = AppnestABAdapter()

    def build(self, packages: list[dict[str, Any]],
              schedule_at: Optional[str] = None,
              canonical: bool = True,
              ab_experiment: Optional[str] = None,
              ab_variants: Optional[list[str]] = None) -> list[DistributionJob]:
        jobs: list[DistributionJob] = []
        for pkg in packages:
            plat = pkg.get("platform", "")
            # 多平台社交账号走 Buffer 定时
            if plat in ("xhs", "wechat", "x_thread", "hn", "reddit"):
                jobs.append(self.buffer.schedule(pkg, at=schedule_at))
            # 技术博客走 Dev.to canonical 同步（源站先发）
            if canonical and plat in ("wechat", "devto", "x_thread"):
                jobs.append(self.devto.schedule_canonical(pkg))
        # 组件级 A/B：包标题变体作为实验变体
        if ab_experiment and packages:
            variants = ab_variants or [
                t["text"] for t in (packages[0].get("metadata") or {}).get("title_variants", [])
            ][:8] or ["control", "variant"]
            jobs.append(self.ab.assign(ab_experiment, variants, packages[0]))
        return jobs

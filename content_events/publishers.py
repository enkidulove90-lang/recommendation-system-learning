"""统一 Publisher 接口与适配器（content_events/publishers.py）。

对应设计 §5（复用设计 04 §统一 Publisher 接口）。
- Publisher(Protocol)：validate / stage / publish / metrics
- DryRunPublisher：沙箱/测试用，永远成功，写本地待发布包（设计 04 §风控 1）
- _GuardedRedbookPublisher：守卫导入 redbook 基础设施；dry_run=True 时只写本地包，
  不触达真实平台；dry_run=False 且真实类可用时尝试真实 stage（沙箱无会话→needs_review）
- PlaceholderPublisher：未知平台显式本地占位 + 告警（修复 A4，不再静默 DryRun）

安全边界（设计 04 §风控 / 设计 05 §实施 3）：
  任何平台默认只 stage；publish 仅在 review_status=approved 且人工审核后调用；
  网络/登录/审核失败 → 抛 PublishingError，由编排层转 needs_review，不自动重试。
"""
from __future__ import annotations

import inspect
import json
import logging
import os
from typing import Any, Dict, List, Optional, Protocol

from .schema import ContentItem

logger = logging.getLogger(__name__)


class PublishingError(RuntimeError):
    pass


class Publisher(Protocol):
    platform: str

    def validate(self, package: Dict[str, Any]) -> List[str]:
        ...

    def stage(self, package: Dict[str, Any]) -> Dict[str, Any]:
        ...

    def publish(self, staged_id: str) -> Dict[str, Any]:
        ...

    def metrics(self, external_id: str) -> Dict[str, Any]:
        ...


def _validate_common(item: ContentItem) -> List[str]:
    errs: List[str] = []
    if not item.paper_id:
        errs.append("paper_id 缺失")
    if not item.platform:
        errs.append("platform 缺失")
    if not item.title:
        errs.append("title 缺失")
    if not item.body_markdown:
        errs.append("body_markdown 缺失")
    if item.platform not in __import__("content_events.schema", fromlist=["PLATFORMS"]).PLATFORMS:
        errs.append(f"未知 platform: {item.platform}")
    return errs


def _write_local_package(results_dir: str, item: ContentItem, package: Dict[str, Any],
                          prefix: str, mode: str, warning: str = "") -> Dict[str, Any]:
    """写本地待发布包（dryrun / 本地降级 / 占位共用）。原子性由调用方保证。"""
    os.makedirs(results_dir, exist_ok=True)
    from .schema import fs_safe

    out = os.path.join(results_dir, f"{prefix}_{fs_safe(item.idem_key)}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(package, f, ensure_ascii=False, indent=2)
    return {
        "external_id": f"{prefix}:{item.idem_key}",
        "path": out,
        "mode": mode,
        **({"warning": warning} if warning else {}),
    }


class DryRunPublisher:
    """沙箱/测试用：写本地待发布包，不触达真实平台。"""

    platform = "dryrun"

    def __init__(self, results_dir: str):
        self.results_dir = results_dir

    def validate(self, package: Dict[str, Any]) -> List[str]:
        item = ContentItem.from_queue_json(package)
        return _validate_common(item)

    def stage(self, package: Dict[str, Any]) -> Dict[str, Any]:
        item = ContentItem.from_queue_json(package)
        errs = _validate_common(item)
        if errs:
            raise PublishingError("; ".join(errs))
        return _write_local_package(self.results_dir, item, package, "dryrun", "dryrun")

    def publish(self, staged_id: str) -> Dict[str, Any]:
        return {"published": False, "note": "dryrun 不公开发布", "staged_id": staged_id}

    def metrics(self, external_id: str) -> Dict[str, Any]:
        return {"available": False, "reason": "dryrun"}


class _GuardedRedbookPublisher:
    """守卫导入 redbook 基础设施；尊重 dry_run 控制真实 stage（修复 A3）。

    - dry_run=True 或真实类不可用 → 写本地包（沙箱安全）。
    - dry_run=False 且真实类可用 → 尝试真实 stage；沙箱无活跃会话会失败 → PublishingError → needs_review。
    真实端到端（PublicationPackage 构造 + 活跃会话）属 Phase 2（设计文档 §5/§实施计划）。
    """

    platform = "guarded"

    def __init__(self, results_dir: str, delivery_cls_name: str, module_path: str, dry_run: bool = True):
        self.results_dir = results_dir
        self._delivery_cls_name = delivery_cls_name
        self._module_path = module_path
        self.dry_run = dry_run
        self._delivery_cls = self._try_import()

    def _try_import(self):
        try:
            import importlib

            mod = importlib.import_module(self._module_path)
            return getattr(mod, self._delivery_cls_name, None)
        except (ImportError, AttributeError) as e:  # 具体异常 + 告警（修复 D4）
            logger.warning("[publishers] %s 导入失败，降级本地包: %s", self._module_path, e)
            return None

    def validate(self, package: Dict[str, Any]) -> List[str]:
        item = ContentItem.from_queue_json(package)
        errs = _validate_common(item)
        # 真实适配器 validate 可能无 package 参数（D3：wechat_delivery/xiaohongshu_delivery 用 validate(self)）
        if self._delivery_cls is not None and not self.dry_run:
            try:
                inst = self._delivery_cls()
                sig = inspect.signature(inst.validate)
                if len(sig.parameters) == 0:
                    inst.validate()
                else:
                    inst.validate(package)
            except Exception as e:  # noqa: BLE001
                logger.warning("[publishers] 真实 validate 告警（不阻断）: %s", e)
        return errs

    def stage(self, package: Dict[str, Any]) -> Dict[str, Any]:
        item = ContentItem.from_queue_json(package)
        errs = _validate_common(item)
        if errs:
            raise PublishingError("; ".join(errs))
        if self.dry_run or self._delivery_cls is None:
            warning = "" if not self.dry_run else ""
            if self._delivery_cls is None:
                warning = f"{self._module_path} 不可用，已降级本地包"
            return _write_local_package(
                self.results_dir, item, package, "local", "local_fallback", warning
            )
        # dry_run=False 且真实类可用 → 尝试真实 stage（沙箱通常无会话 → 失败转 needs_review）
        try:
            return self._real_stage(item, package)
        except PublishingError:
            raise
        except Exception as e:  # noqa: BLE001
            raise PublishingError(f"{self._delivery_cls_name} stage 失败: {e}") from e

    def _real_stage(self, item: ContentItem, package: Dict[str, Any]) -> Dict[str, Any]:
        # Phase 2 接通点：构造 redbook.automation.publishing.PublicationPackage 并调用
        # WeChatPublisher/XhsPublisher.stage(pkg)。当前无活跃会话，明确转 needs_review。
        raise PublishingError(
            f"{self._delivery_cls_name} 真实 stage 需活跃平台会话；"
            f"dry_run=False 但沙箱/未登录，转 needs_review（设计 §8）"
        )

    def publish(self, staged_id: str) -> Dict[str, Any]:
        raise PublishingError("publish 仅人工审核后调用，编排层不自动执行")

    def metrics(self, external_id: str) -> Dict[str, Any]:
        return {"available": False, "reason": "未接入"}


class PlaceholderPublisher:
    """未知平台：显式本地占位包 + 告警（修复 A4，不再静默 DryRun）。"""

    platform = "placeholder"

    def __init__(self, results_dir: str, platform_name: str):
        self.results_dir = results_dir
        self.platform_name = platform_name

    def validate(self, package: Dict[str, Any]) -> List[str]:
        item = ContentItem.from_queue_json(package)
        errs = _validate_common(item)
        # 平台未知本身不算阻断错误（渲染/校验仍可进行），仅记录告警
        return errs

    def stage(self, package: Dict[str, Any]) -> Dict[str, Any]:
        item = ContentItem.from_queue_json(package)
        errs = _validate_common(item)
        if errs:
            raise PublishingError("; ".join(errs))
        logger.warning("[publishers] 未知平台 '%s' → 写占位本地包", self.platform_name)
        return _write_local_package(
            self.results_dir, item, package, f"placeholder_{self.platform_name}", "placeholder"
        )

    def publish(self, staged_id: str) -> Dict[str, Any]:
        raise PublishingError("未知平台不支持 publish")

    def metrics(self, external_id: str) -> Dict[str, Any]:
        return {"available": False, "reason": f"unknown_platform:{self.platform_name}"}


# 已知真实平台 → (delivery 类名, 模块路径)
_REDBOOK_TARGETS = {
    "wechat": ("WeChatDraftDelivery", "redbook.infrastructure.wechat_delivery"),
    "xhs": ("OpenCliXiaohongshuDelivery", "redbook.infrastructure.xiaohongshu_delivery"),
}


def make_publisher(platform: str, results_dir: str, dry_run: bool = True) -> Publisher:
    """工厂：按 platform 返回适配器；dry_run 控制是否尝试真实 stage。

    - dryrun → DryRunPublisher（本地包）
    - wechat/xhs → _GuardedRedbookPublisher（dry_run 默认 True 安全）
    - 未知平台 → PlaceholderPublisher（显式占位 + 告警，修复 A4）
    """
    if platform == "dryrun":
        return DryRunPublisher(results_dir)
    if platform in _REDBOOK_TARGETS:
        cls_name, mod = _REDBOOK_TARGETS[platform]
        return _GuardedRedbookPublisher(results_dir, cls_name, mod, dry_run=dry_run)
    logger.warning("[publishers] 未知平台 '%s' → PlaceholderPublisher", platform)
    return PlaceholderPublisher(results_dir, platform)

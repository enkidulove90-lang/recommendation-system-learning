"""Pool-to-worker delivery projection with platform publication policy.

The queue and worker remain the single execution mechanism.  This adapter only
translates a terminal platform receipt into the shared pool state, while
preventing draft-only platforms from entering a public-publish code path.
"""
from __future__ import annotations

from typing import Callable, Protocol

from redbook.orchestration import models
from redbook.orchestration.models import Job

from .paper_pool import PaperPool


class PlatformDelivery(Protocol):
    """Narrow contract for independently implemented platform adapters."""

    def save_draft(self, canonical_id: str, heartbeat: Callable[[], None]) -> str: ...

    def publish(self, canonical_id: str, heartbeat: Callable[[], None]) -> str: ...


class DeliveryPolicyError(RuntimeError):
    """A platform returned a state disallowed by its delivery policy."""


_DRAFT_ONLY_PLATFORMS = frozenset({"xiaohongshu", "wechat"})
_POOL_CHAIN = (
    "parsed", "summarized", "composed", "staged",
    "SAVED_UNVERIFIED", "VERIFIED", "published",
)
_POOL_TARGETS = {
    models.SAVED_UNVERIFIED: "SAVED_UNVERIFIED",
    models.VERIFIED: "VERIFIED",
    models.PUBLISHED: "published",
}


class PoolDeliveryHandler:
    """Run one platform leg and write the result back to ``paper_pool``.

    Homepage publication is possible only when an explicit homepage adapter is
    injected.  Xiaohongshu and WeChat have no route to ``publish`` here: their
    adapter is called through ``save_draft`` and may only return draft states.
    """

    def __init__(self, pool: PaperPool, platform: str, adapter: PlatformDelivery) -> None:
        if platform not in _DRAFT_ONLY_PLATFORMS | {"homepage"}:
            raise ValueError(f"unsupported sentinel platform {platform!r}")
        self.pool = pool
        self.platform = platform
        self.adapter = adapter

    def __call__(self, job: Job, heartbeat: Callable[[], None]) -> str:
        prefix = f"sentinel:{self.platform}:"
        if not job.payload_ref.startswith(prefix):
            raise DeliveryPolicyError(
                f"sentinel job must target {self.platform!r} with a canonical paper reference"
            )
        canonical_id = job.payload_ref.removeprefix(prefix).strip()
        if not canonical_id:
            raise DeliveryPolicyError("sentinel job requires a canonical paper reference")
        try:
            if self.platform == "homepage":
                state = self.adapter.publish(canonical_id, heartbeat)
                if state != models.PUBLISHED:
                    raise DeliveryPolicyError("homepage adapter must return PUBLISHED")
            else:
                state = self.adapter.save_draft(canonical_id, heartbeat)
                if state not in {models.SAVED_UNVERIFIED, models.VERIFIED}:
                    raise DeliveryPolicyError(
                        f"{self.platform} is draft-only and may not return {state!r}"
                    )
            self._advance_platform(canonical_id, state)
            self.pool.record_platform(canonical_id, self.platform)
            return state
        except Exception:
            self._block(canonical_id)
            raise

    def _advance_platform(self, canonical_id: str, state: str) -> None:
        target = _POOL_TARGETS.get(state)
        if target is None:
            raise DeliveryPolicyError(f"unsupported delivery receipt state {state!r}")
        for stage in _POOL_CHAIN:
            self.pool.set_platform_status(canonical_id, self.platform, stage)
            if stage == target:
                return

    def _block(self, canonical_id: str) -> None:
        try:
            self.pool.set_platform_status(canonical_id, self.platform, "blocked")
        except Exception:
            # The worker will preserve the original delivery exception.  Do
            # not mask it if an already-terminal entry cannot be blocked.
            return

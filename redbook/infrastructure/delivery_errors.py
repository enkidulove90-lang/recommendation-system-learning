"""Stable, serializable failures for draft-only platform delivery."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


E_PREFLIGHT_BLOCKED = "E_PREFLIGHT_BLOCKED"
E_OPENCLI_UNAVAILABLE = "E_OPENCLI_UNAVAILABLE"
E_RESPONSE_SHAPE = "E_RESPONSE_SHAPE"
E_TOPIC_UNAVAILABLE = "E_TOPIC_UNAVAILABLE"
E_SAVE_UNVERIFIED = "E_SAVE_UNVERIFIED"
E_VERIFY_MISMATCH = "E_VERIFY_MISMATCH"
E_REGISTRY_CONFLICT = "E_REGISTRY_CONFLICT"


@dataclass
class DeliveryError(RuntimeError):
    message: str
    code: str = E_SAVE_UNVERIFIED
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        RuntimeError.__init__(self, self.message)

    def as_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}

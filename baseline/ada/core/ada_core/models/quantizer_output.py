"""Quantizer output contract shared by R3-VAE and MMQ components."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping

import torch


@dataclass
class QuantizerOutput:
    """Typed result of a quantization pass.

    ``reconstruction`` – decoded output with batch shape preserved.
    ``soft_codes``    – soft top-K similarity weights (B, L).
    ``hard_codes``    – one-hot argmax indices (B, L) via straight-through.
    ``usage``         – per-reference utilization in [0, 1] (L,).
    ``losses``        – named scalar losses (quantizer / commitment / orth…).
    """

    reconstruction: torch.Tensor
    soft_codes: torch.Tensor
    hard_codes: torch.Tensor
    usage: torch.Tensor
    losses: Dict[str, torch.Tensor] = field(default_factory=dict)

    def loss_total(self, weights: Mapping[str, float] | None = None) -> torch.Tensor:
        weights = weights or {}
        total = None
        for name, value in self.losses.items():
            w = float(weights.get(name, 1.0))
            term = value * w
            total = term if total is None else total + term
        if total is None:
            total = torch.zeros(())
        return total

    def to_json(self) -> Dict[str, Any]:
        return {
            "losses": {k: float(v.detach()) for k, v in self.losses.items()},
            "usage_mean": float(self.usage.mean().detach()) if self.usage.numel() else 0.0,
        }

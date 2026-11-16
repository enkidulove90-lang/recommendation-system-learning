"""P1-only ADA modules: alignment and dynamic weighting switches.

ADC-SID-inspired modules are *degraded adapters* in this scaffold: they exist
so P1/P2 toggles can be exercised, are clearly labeled as such, and are hard
disabled under P0 regardless of configuration.

``AdaModel`` wires MMQ -> R3VAE -> (optional P1 modules) -> downstream scorer
and exposes ``forward(batch)`` honouring the toggle contract.
"""

from __future__ import annotations

from typing import Any, Dict

import torch
import torch.nn as nn
import torch.nn.functional as F

from .mmq import MMQEncoder
from .quantizer_output import QuantizerOutput
from .r3vae import R3VAE
from .soft_index import SoftIndexAdapter


class AlignmentAdapter(nn.Module):
    """P1-only contrastive alignment adapter (degraded, clearly labeled)."""

    ENABLED_PHASES = ("P1", "P2")
    LABEL = "degraded ADC-SID-inspired alignment adapter"

    def __init__(self, dim: int, temperature: float = 0.2):
        super().__init__()
        self.temperature = temperature
        self.proj = nn.Linear(dim, dim)

    def forward(self, fused: torch.Tensor) -> Dict[str, torch.Tensor]:
        z = F.normalize(self.proj(fused), dim=-1)
        sim = z @ z.t() / self.temperature
        targets = torch.arange(z.size(0), device=z.device)
        loss = F.cross_entropy(sim, targets)
        return {"aligned": z, "alignment_loss": loss}


class DynamicWeightingAdapter(nn.Module):
    """P1-only dynamic per-sample weighting adapter (degraded, clearly labeled)."""

    ENABLED_PHASES = ("P1", "P2")
    LABEL = "degraded dynamic weighting adapter"

    def __init__(self, dim: int):
        super().__init__()
        self.gate = nn.Linear(dim, 1)

    def forward(self, fused: torch.Tensor) -> Dict[str, torch.Tensor]:
        w = torch.sigmoid(self.gate(fused)).squeeze(-1)        # (B,)
        weighted = fused * w.unsqueeze(-1)
        return {"weighted": weighted, "weights": w}


class AdaModel(nn.Module):
    """Toggle-aware ADA scaffold.

    Switch contract
    ---------------
    * ``enable_alignment`` / ``enable_dynamic_weighting`` only take effect in
      P1/P2 phases.  Under P0 both are force-disabled even if the config says
      ``True`` — the P0 protocol measures the quantizer baseline alone.
    """

    def __init__(
        self,
        input_dim: int,
        latent_dim: int,
        fusion_dim: int,
        downstream_hidden: int,
        n_references: int,
        top_k: int,
        phase: str,
        enable_alignment: bool = False,
        enable_dynamic_weighting: bool = False,
        rationale: str = "prototype scaffold",
    ):
        super().__init__()
        if phase not in ("P0", "P1", "P2"):
            raise ValueError(f"unknown phase '{phase}'")
        self.phase = phase
        # P0 disables alignment and dynamic weighting EVEN IF available.
        self.alignment_allowed = phase in ("P1", "P2") and enable_alignment
        self.weighting_allowed = phase in ("P1", "P2") and enable_dynamic_weighting

        self.mmq = MMQEncoder(input_dim, fusion_dim, fusion_dim)
        self.r3vae = R3VAE(
            input_dim=fusion_dim,
            latent_dim=latent_dim,
            n_references=n_references,
            top_k=top_k,
            rationale=rationale,
        )
        self.soft_index = SoftIndexAdapter(
            n_experts=2, index_dim=fusion_dim
        )
        self.alignment = AlignmentAdapter(fusion_dim) if self.alignment_allowed else None
        self.weighting = DynamicWeightingAdapter(fusion_dim) if self.weighting_allowed else None
        self.scorer = nn.Sequential(
            nn.Linear(fusion_dim, downstream_hidden),
            nn.GELU(),
            nn.Linear(downstream_hidden, 1),
        )

    def forward(self, batch: Dict[str, torch.Tensor]) -> Dict[str, Any]:
        x = batch["features"]
        mmq_out = self.mmq(x)
        fused = mmq_out["fused"]

        quantized: QuantizerOutput = self.r3vae(fused)

        # Experts 0-pool provides the two "shared" expert embeddings for the
        # BAF index adapter; the index selects over them via straight-through.
        stacked = mmq_out["experts_0"].permute(1, 0, 2)        # (B, n_0, D)
        index_out = self.soft_index(stacked)

        representation = quantized.reconstruction + index_out["selected"]

        out: Dict[str, Any] = {
            "reconstruction": quantized.reconstruction,
            "soft_codes": quantized.soft_codes,
            "hard_codes": quantized.hard_codes,
            "usage": quantized.usage,
            "representation": representation,
            "soft_index": index_out["soft_index"],
            "hard_index": index_out["hard_index"],
        }
        losses = dict(quantized.losses)
        losses["ortho"] = mmq_out["ortho_loss"]

        if self.alignment is not None:
            align_out = self.alignment(representation)
            out["aligned"] = align_out["aligned"]
            losses["alignment"] = align_out["alignment_loss"]
        else:
            out["alignment_active"] = False

        if self.weighting is not None:
            weight_out = self.weighting(representation)
            out["weights"] = weight_out["weights"]
            losses["weighting_reg"] = (weight_out["weights"] - 0.5).pow(2).mean()
        else:
            out["dynamic_weighting_active"] = False

        scores = self.scorer(representation).squeeze(-1)
        out["scores"] = scores
        out["losses"] = losses
        if "labels" in batch:
            out["rank_loss"] = F.binary_cross_entropy_with_logits(
                scores, batch["labels"].float()
            )
        return out

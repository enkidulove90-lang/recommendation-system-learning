"""R3-VAE: reference-residual encoder with a top-K dot-product quantizer.

Minimal paper-grounded scaffold:

* ``L`` learned reference vectors of dimensionality ``M`` (configurable; the
  protocol requires an explicit rationale recorded per Appendix-A).
* Encoding produces a latent ``z``; the quantizer scores dot products between
  ``z`` and every reference, keeps the **top-K** similarities, and produces
  soft weights (softmax over the top-K scores) plus hard one-hot selection via
  straight-through estimation.
* Reconstruction = decoder(soft combination of references + residual ``z``),
  so the batch shape is preserved end-to-end.
"""

from __future__ import annotations

from typing import Any, Dict

import torch
import torch.nn as nn
import torch.nn.functional as F

from .quantizer_output import QuantizerOutput


class TopKDotProductQuantizer(nn.Module):
    """Top-K dot-product quantizer with straight-through hard codes."""

    def __init__(self, n_references: int, dim: int, top_k: int = 2):
        super().__init__()
        if top_k < 1 or top_k > n_references:
            raise ValueError(f"top_k must be in [1, {n_references}], got {top_k}")
        self.n_references = n_references
        self.dim = dim
        self.top_k = top_k
        self.references = nn.Parameter(torch.randn(n_references, dim) * 0.05)

    def forward(self, z: torch.Tensor) -> QuantizerOutput:
        B, D = z.shape
        if D != self.dim:
            raise ValueError(f"expected latent dim {self.dim}, got {D}")

        scores = z @ self.references.t()                       # (B, L)
        kth = scores.topk(self.top_k, dim=-1).values[..., -1:]
        mask = (scores >= kth).to(scores.dtype)
        masked_scores = scores.masked_fill(mask == 0, float("-inf"))
        soft_codes = F.softmax(masked_scores, dim=-1)          # (B, L)

        hard_idx = scores.argmax(dim=-1)                       # (B,)
        hard_codes = F.one_hot(hard_idx, self.n_references).to(scores.dtype)

        # Straight-through: forward uses the hard selection, backward the soft.
        combined_hard = hard_codes @ self.references           # (B, D)
        combined_soft = soft_codes @ self.references           # (B, D)
        combined = combined_soft + (combined_hard - combined_soft).detach()

        with torch.no_grad():
            avg = soft_codes.mean(dim=0)                       # (L,)
            usage = avg / (avg.sum() + 1e-8)

        # Commitment-style quantizer losses.
        codebook_loss = F.mse_loss(combined_hard, z.detach())
        commitment_loss = F.mse_loss(z, combined_hard.detach())
        usage_entropy = -(usage * (usage + 1e-8).log()).sum()
        losses: Dict[str, torch.Tensor] = {
            "codebook": codebook_loss,
            "commitment": commitment_loss,
            "usage_entropy": usage_entropy,
        }
        return QuantizerOutput(
            reconstruction=combined,
            soft_codes=soft_codes,
            hard_codes=hard_codes,
            usage=usage,
            losses=losses,
        )


class R3VAE(nn.Module):
    """Reference-residual VAE scaffold around :class:`TopKDotProductQuantizer`.

    ``rationale`` must be non-empty — the protocol requires an explicit
    rationale for the L / M / top-K triple before training can start.
    """

    def __init__(
        self,
        input_dim: int,
        latent_dim: int,
        n_references: int,
        top_k: int = 2,
        rationale: str = "",
    ):
        super().__init__()
        if not rationale.strip():
            raise ValueError(
                "R3VAE requires an explicit rationale for (L, M, top-K); "
                "record it in the Appendix-A parameter table before constructing."
            )
        self.latent_dim = latent_dim
        self.rationale = rationale
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, latent_dim),
            nn.GELU(),
            nn.Linear(latent_dim, latent_dim),
        )
        self.quantizer = TopKDotProductQuantizer(n_references, latent_dim, top_k)
        self.residual_proj = nn.Linear(latent_dim, latent_dim)
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, latent_dim),
            nn.GELU(),
            nn.Linear(latent_dim, input_dim),
        )

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        return self.encoder(x)

    def forward(self, x: torch.Tensor) -> QuantizerOutput:
        z = self.encode(x)
        quantized: QuantizerOutput = self.quantizer(z)
        residual = self.residual_proj(z - quantized.reconstruction)
        recon = self.decoder(quantized.reconstruction + residual)
        recon_loss = F.mse_loss(recon, x)
        losses = dict(quantized.losses)
        losses["reconstruction"] = recon_loss
        return QuantizerOutput(
            reconstruction=recon,
            soft_codes=quantized.soft_codes,
            hard_codes=quantized.hard_codes,
            usage=quantized.usage,
            losses=losses,
        )

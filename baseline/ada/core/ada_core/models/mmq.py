"""MMQ: multi-expert encoder with an orthogonality regularizer.

Scaffold parameters are pinned by the protocol: ``N_s=2`` sequential experts,
``N_t=2`` textual experts, ``N_0=2`` shared/expert-0 experts, orthogonality
weight ``0.005``.  Each expert is a small MLP; the orthogonality penalty
encourages the experts to specialize on decorrelated subspaces.
"""

from __future__ import annotations

from typing import Dict

import torch
import torch.nn as nn

ORTHO_WEIGHT = 0.005
N_SEQUENTIAL_EXPERTS = 2
N_TEXTUAL_EXPERTS = 2
N_SHARED_EXPERTS = 2


def _make_expert(input_dim: int, hidden_dim: int, output_dim: int) -> nn.Sequential:
    return nn.Sequential(
        nn.Linear(input_dim, hidden_dim),
        nn.GELU(),
        nn.Linear(hidden_dim, output_dim),
    )


class MMQEncoder(nn.Module):
    """Multi-expert encoder producing per-expert embeddings + fused output."""

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        output_dim: int,
        n_s: int = N_SEQUENTIAL_EXPERTS,
        n_t: int = N_TEXTUAL_EXPERTS,
        n_0: int = N_SHARED_EXPERTS,
    ):
        super().__init__()
        self.output_dim = output_dim
        self.experts_s = nn.ModuleList(
            [_make_expert(input_dim, hidden_dim, output_dim) for _ in range(n_s)]
        )
        self.experts_t = nn.ModuleList(
            [_make_expert(input_dim, hidden_dim, output_dim) for _ in range(n_t)]
        )
        self.experts_0 = nn.ModuleList(
            [_make_expert(input_dim, hidden_dim, output_dim) for _ in range(n_0)]
        )
        self.fuse = nn.Linear(
            (n_s + n_t + n_0) * output_dim, output_dim
        )

    @staticmethod
    def orthogonal_regularizer(modules: nn.ModuleList) -> torch.Tensor:
        """Mean squared inner product between corresponding expert layers.

        Layers are compared *depth-wise* (first layer vs first layer, …) so
        that differently-shaped weights are never mixed into one Gram matrix.
        """
        per_depth: dict[int, list[torch.Tensor]] = {}
        for expert in modules:
            depth = 0
            for layer in expert:
                if isinstance(layer, nn.Linear):
                    per_depth.setdefault(depth, []).append(layer.weight.flatten())
                    depth += 1
        if not per_depth:
            return torch.zeros(())
        total = torch.zeros(())
        n_terms = 0
        for vecs in per_depth.values():
            if len(vecs) < 2:
                continue
            matrix = torch.stack(vecs)
            norms = matrix.norm(dim=1, keepdim=True).clamp_min(1e-8)
            unit = matrix / norms
            gram = unit @ unit.t()
            off_diag = gram - torch.diag(torch.diag(gram))
            total = total + (off_diag**2).mean()
            n_terms += 1
        if n_terms == 0:
            return torch.zeros(())
        return total / n_terms

    def ortho_loss(self) -> torch.Tensor:
        total = torch.zeros(())
        for pool in (self.experts_s, self.experts_t, self.experts_0):
            total = total + self.orthogonal_regularizer(pool)
        return total * ORTHO_WEIGHT

    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        outs_s = [e(x) for e in self.experts_s]
        outs_t = [e(x) for e in self.experts_t]
        outs_0 = [e(x) for e in self.experts_0]
        fused = self.fuse(torch.cat(outs_s + outs_t + outs_0, dim=-1))
        return {
            "fused": fused,
            "experts_s": torch.stack(outs_s, dim=0),
            "experts_t": torch.stack(outs_t, dim=0),
            "experts_0": torch.stack(outs_0, dim=0),
            "ortho_loss": self.ortho_loss(),
        }

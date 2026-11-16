"""MMQ BAF soft/hard index adapter.

Produces a Behavior-Aligned Feature (BAF) style index from MMQ expert
embeddings: the *forward pass* selects the hard index (argmax expert) with
straight-through estimation so gradients flow to the soft scores.
"""

from __future__ import annotations

from typing import Dict

import torch
import torch.nn as nn
import torch.nn.functional as F


class SoftIndexAdapter(nn.Module):
    """Soft/hard index over MMQ experts with straight-through hard selection."""

    def __init__(self, n_experts: int, index_dim: int):
        super().__init__()
        self.n_experts = n_experts
        self.index_proj = nn.Linear(index_dim, n_experts)

    def forward(self, expert_embeddings: torch.Tensor) -> Dict[str, torch.Tensor]:
        """``expert_embeddings``: (B, n_experts, D) stacked expert outputs."""
        B, E, D = expert_embeddings.shape
        if E != self.n_experts:
            raise ValueError(f"expected {self.n_experts} experts, got {E}")

        pooled = expert_embeddings.mean(dim=1)                 # (B, D)
        scores = self.index_proj(pooled)                       # (B, E)
        soft_index = F.softmax(scores, dim=-1)                 # (B, E)
        hard_index = F.one_hot(scores.argmax(dim=-1), E).to(scores.dtype)

        # Straight-through hard index in the forward pass.
        selected_hard = (hard_index.unsqueeze(-1) * expert_embeddings).sum(dim=1)
        selected_soft = (soft_index.unsqueeze(-1) * expert_embeddings).sum(dim=1)
        selected = selected_soft + (selected_hard - selected_soft).detach()

        return {
            "soft_index": soft_index,
            "hard_index": hard_index,
            "selected": selected,
            "index_entropy": -(soft_index * (soft_index + 1e-8).log()).sum(-1).mean(),
        }

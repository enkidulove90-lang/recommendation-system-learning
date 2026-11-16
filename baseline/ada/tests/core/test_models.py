"""Tensor-contract tests for the ADA model layer (Task 2)."""

from __future__ import annotations

import pytest
import torch

from ada_core.models.ada_modules import AdaModel, AlignmentAdapter
from ada_core.models.mmq import MMQEncoder, ORTHO_WEIGHT
from ada_core.models.quantizer_output import QuantizerOutput
from ada_core.models.r3vae import R3VAE, TopKDotProductQuantizer
from ada_core.models.soft_index import SoftIndexAdapter


def test_r3vae_reference_residual_and_top_k_codes_preserve_batch_shape():
    torch.manual_seed(0)
    model = R3VAE(input_dim=16, latent_dim=8, n_references=8, top_k=3, rationale="pilot")
    x = torch.randn(5, 16)
    out = model(x)
    assert isinstance(out, QuantizerOutput)
    assert out.reconstruction.shape == x.shape
    assert out.soft_codes.shape == (5, 8)
    assert out.hard_codes.shape == (5, 8)
    # soft codes: exactly top_k nonzero entries per row, summing to 1.
    nonzero = (out.soft_codes > 0).sum(dim=-1)
    assert torch.all(nonzero == 3)
    assert torch.allclose(out.soft_codes.sum(dim=-1), torch.ones(5), atol=1e-4)
    # hard codes: exactly one entry per row.
    assert torch.all(out.hard_codes.sum(dim=-1) == 1)
    # usage is a probability vector over references.
    assert out.usage.shape == (8,)
    assert abs(float(out.usage.sum()) - 1.0) < 1e-4
    assert "reconstruction" in out.losses and "commitment" in out.losses


def test_r3vae_requires_explicit_rationale():
    with pytest.raises(ValueError, match="rationale"):
        R3VAE(input_dim=16, latent_dim=8, n_references=8, top_k=2, rationale="")


def test_top_k_quantizer_validates_top_k():
    with pytest.raises(ValueError, match="top_k"):
        TopKDotProductQuantizer(n_references=4, dim=8, top_k=5)


def test_p0_disables_alignment_and_dynamic_weighting_even_if_available():
    torch.manual_seed(0)
    model = AdaModel(
        input_dim=16, latent_dim=8, fusion_dim=16, downstream_hidden=16,
        n_references=8, top_k=2, phase="P0",
        enable_alignment=True, enable_dynamic_weighting=True,
    )
    assert model.alignment is None
    assert model.weighting is None
    batch = {"features": torch.randn(6, 16), "labels": torch.randint(0, 2, (6,))}
    out = model(batch)
    assert out.get("alignment_active") is False
    assert out.get("dynamic_weighting_active") is False
    assert "alignment_loss" not in out["losses"]

    # P1 with switches enabled does activate them.
    p1 = AdaModel(
        input_dim=16, latent_dim=8, fusion_dim=16, downstream_hidden=16,
        n_references=8, top_k=2, phase="P1",
        enable_alignment=True, enable_dynamic_weighting=True,
    )
    assert p1.alignment is not None and p1.weighting is not None
    out1 = p1(batch)
    assert "alignment" in out1["losses"]
    assert "weights" in out1


def test_soft_index_uses_straight_through_hard_index_in_forward_pass():
    torch.manual_seed(0)
    adapter = SoftIndexAdapter(n_experts=2, index_dim=16)
    experts = torch.randn(4, 2, 16, requires_grad=True)
    out = adapter(experts)
    # Forward selection equals the hard (argmax) expert embedding.
    hard = out["hard_index"].argmax(dim=-1)
    for b in range(4):
        assert torch.allclose(
            out["selected"][b], experts[b, int(hard[b])], atol=1e-6
        ), "forward pass must use the hard index value"
    # Backward path flows gradients through the soft scores.
    out["selected"].sum().backward()
    assert experts.grad is not None
    assert experts.grad.abs().sum() > 0


def test_adamodel_end_to_end_shapes_and_losses():
    torch.manual_seed(0)
    model = AdaModel(
        input_dim=16, latent_dim=8, fusion_dim=16, downstream_hidden=16,
        n_references=8, top_k=2, phase="P0", rationale="pilot",
    )
    batch = {"features": torch.randn(7, 16), "labels": torch.randint(0, 2, (7,))}
    out = model(batch)
    assert out["scores"].shape == (7,)
    assert out["rank_loss"].dim() == 0
    assert out["ortho_loss" if False else "losses"]["ortho"].dim() == 0
    # Orthogonal regularizer carries the pinned 0.005 weight semantics.
    assert ORTHO_WEIGHT == 0.005
    total = QuantizerOutput(
        reconstruction=out["reconstruction"], soft_codes=out["soft_codes"],
        hard_codes=out["hard_codes"], usage=out["usage"],
        losses=out["losses"],
    ).loss_total()
    assert torch.isfinite(total)


def test_mmq_expert_counts_pinned():
    enc = MMQEncoder(input_dim=8, hidden_dim=16, output_dim=8)
    assert len(enc.experts_s) == 2
    assert len(enc.experts_t) == 2
    assert len(enc.experts_0) == 2

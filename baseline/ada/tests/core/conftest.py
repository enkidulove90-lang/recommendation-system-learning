"""Core-test fixtures (MMSSL-shaped dataset, features, appendix overrides)."""

from __future__ import annotations

import numpy as np
import pytest


def write_split(path, users: int, seq_len: int = 6, extra_popular=(0, 1, 2)):
    lines = []
    for u in range(users):
        items = [((u * 7 + k * 3) % 20) for k in range(seq_len)]
        lines.append(" ".join(str(x) for x in [u] + items))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


@pytest.fixture()
def mmssl_dir(tmp_path):
    """A tiny MMSSL-shaped dataset: 10 users, 20 items.

    Items 0-2 are popular; a couple of items appear exactly once (cold).
    """
    d = tmp_path / "mmssl-tiny"
    d.mkdir()
    write_split(d / "train.txt", users=10, seq_len=6)
    write_split(d / "valid.txt", users=10, seq_len=2)
    write_split(d / "test.txt", users=10, seq_len=2)
    return str(d)


@pytest.fixture()
def feature_file(tmp_path):
    path = tmp_path / "image_feat.npy"
    rng = np.random.default_rng(0)
    np.save(path, rng.normal(size=(20, 8)).astype(np.float32))
    return str(path)


@pytest.fixture()
def resolved_overrides():
    rationale = "local pilot value; recorded for prototype scaffold"
    source = "local_pilot"
    return {
        "r3vae_L": (8, rationale, source),
        "r3vae_M": (8, rationale, source),
        "r3vae_top_k": (2, rationale, source),
        "mmq_expert_hidden": (16, rationale, source),
        "fusion_dim": (16, rationale, source),
        "downstream_hidden": (16, rationale, source),
        "neg_pool_size": (100, rationale, source),
        "neg_per_positive": (4, rationale, source),
        "eval_topk": (10, rationale, source),
        "grad_clip_norm": (5.0, rationale, source),
        "weight_decay": (0.0, rationale, source),
        "warmup_steps": (0, rationale, source),
    }

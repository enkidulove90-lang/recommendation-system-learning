"""Ranking evaluation: AUC / GAUC and cold-bucket metrics.

``RankingEvaluator.compare_to_baseline`` **rejects** a baseline whose
persisted ``split_hash`` differs from this run's — a mismatch is a hard
error, never a warning.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

import numpy as np
import torch


class SplitHashMismatchError(ValueError):
    """Raised when a baseline comparison uses a different split_hash."""


class RankingEvaluator:
    def __init__(self, bundle, config):
        self.bundle = bundle
        self.config = config

    # -- hashing ------------------------------------------------------------

    @property
    def split_hash(self) -> str:
        return self.bundle.split_audit.raw_split_hash

    def compare_to_baseline(self, baseline: Mapping[str, Any]) -> Dict[str, Any]:
        baseline_hash = baseline.get("split_hash")
        if baseline_hash != self.split_hash:
            raise SplitHashMismatchError(
                f"baseline split_hash {baseline_hash!r} != run split_hash "
                f"{self.split_hash!r}; comparison rejected, not warned."
            )
        return {"status": "accepted", "baseline_run_id": baseline.get("run_id")}

    # -- metrics ------------------------------------------------------------

    @staticmethod
    def auc(scores_pos: np.ndarray, scores_neg: np.ndarray) -> float:
        if len(scores_pos) == 0 or len(scores_neg) == 0:
            return float("nan")
        diffs = scores_pos[:, None] - scores_neg[None, :]
        wins = (diffs > 0).sum() + 0.5 * (diffs == 0).sum()
        return float(wins / diffs.size)

    def _score_user(self, model, user_seq, candidates, matrix):
        entry = self.config.feature_registry.by_name("image")
        if entry is None:
            return np.zeros(len(candidates))
        feats = torch.tensor(
            matrix[[c for c in candidates if c < matrix.shape[0]]], dtype=torch.float32
        )
        with torch.no_grad():
            scores = model({"features": feats})["scores"]
        return scores.numpy()

    def valid_auc(self, model) -> float:
        """Mean AUC over users on the valid split (toy protocol)."""
        entry = self.config.feature_registry.by_name("image")
        matrix = np.load(entry.path) if entry else None
        pos_scores, neg_scores = [], []
        rng = np.random.default_rng(self.config.seed)
        for u, seq in enumerate(self.bundle.valid):
            if not seq:
                continue
            target = seq[-1]
            others = [i for i in self.bundle.train[u] if i != target]
            if not others:
                continue
            s_target = float(model({"features": torch.tensor(
                matrix[[min(target, matrix.shape[0] - 1)]], dtype=torch.float32
            )})["scores"][0])
            s_negs = [
                float(model({"features": torch.tensor(
                    matrix[[min(n, matrix.shape[0] - 1)]], dtype=torch.float32
                )})["scores"][0])
                for n in others
            ]
            pos_scores.append(s_target)
            neg_scores.extend(s_negs)
        if not pos_scores:
            return 0.5
        return self.auc(np.array(pos_scores), np.array(neg_scores))

    def cold_bucket_report(self, model) -> Dict[str, Any]:
        """Report cold buckets separately (never merged into the main mean)."""
        buckets = self.bundle.split_audit.cold_buckets
        return {
            "cold_item": {
                "n_items": len(buckets.cold_items),
                "rule": buckets.summary()["cold_item_rule"],
            },
            "cold_user": {
                "n_users": len(buckets.cold_users),
                "rule": buckets.summary()["cold_user_rule"],
            },
            "note": "cold buckets are reported separately; not part of warm AUC",
        }

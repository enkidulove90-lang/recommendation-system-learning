import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from novelty.contrast import ContrastEngine  # noqa: E402
from novelty.schemas import Claim, ClaimType, ContributionExtraction, NeighborPaper, NeighborSource  # noqa: E402


class TestContrast(unittest.TestCase):
    def _target(self) -> ContributionExtraction:
        return ContributionExtraction(
            arxiv_id="a", title="Target", core_task="graph recommendation",
            background="Recommendation with sparse data.",
            method="We propose a contrastive learning approach with BPR loss on a graph neural network retriever.",
            experiments="Evaluated on Amazon dataset with Recall@20.",
            contributions=["novel alignment module"],
            claims=[Claim(text="We propose a contrastive framework for recommendation.",
                         claim_type=ClaimType.METHODOLOGICAL)],
        )

    def test_similar_neighbor_yields_can_refute(self):
        nb = NeighborPaper(arxiv_id="b", title="Similar Prior", source=NeighborSource.CORPUS)
        nb_text = ("We propose a contrastive learning method with BPR loss on a graph "
                   "neural network retriever, evaluated on Amazon with Recall@20.")
        pts = ContrastEngine().build_matrix(self._target(), nb, nb_text)
        self.assertTrue(pts)
        labels = {p.label.value for p in pts}
        self.assertIn("can_refute", labels)  # 高度相似轴 -> 建议审视
        for p in pts:
            self.assertTrue(p.evidence)  # 必须附证据

    def test_different_neighbor_yields_cannot_refute(self):
        nb = NeighborPaper(arxiv_id="c", title="Different Prior", source=NeighborSource.CORPUS)
        nb_text = ("We use a transformer with MSE loss on MovieLens, text-only modality, "
                   "trained by reinforcement learning.")
        pts = ContrastEngine().build_matrix(self._target(), nb, nb_text)
        labels = {p.label.value for p in pts}
        self.assertIn("cannot_refute", labels)

    def test_labels_are_valid_enum(self):
        nb = NeighborPaper(arxiv_id="x", title="X", source=NeighborSource.CORPUS)
        pts = ContrastEngine().build_matrix(self._target(), nb, "some text about recommendation")
        for p in pts:
            self.assertIn(p.label.value, {"can_refute", "cannot_refute", "unclear"})


if __name__ == "__main__":
    unittest.main()

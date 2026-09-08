import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from novelty.extractor import Extractor  # noqa: E402


class TestExtractor(unittest.TestCase):
    def _md(self) -> str:
        return """# Graph Contrastive Learning for Recommendation

## Abstract
We propose a graph contrastive learning framework for recommendation that aligns
user-item embeddings with multi-modal signals. Our contribution is a novel
alignment module.

## 1 Introduction
Recommendation systems suffer from sparse interactions. We introduce a method
to mitigate this.

## 3 Method
We propose a contrastive learning approach using a BPR loss on the user-item graph.
Our model uses a graph neural network retriever.

## 4 Experiments
We evaluate on the Amazon and MovieLens datasets. Results show our method
outperforms baselines under Recall@20.

## Contributions
- We propose the first graph contrastive framework for recommendation.
- We develop a novel alignment module for multi-modal signals.
- We show empirical gains on public benchmarks.
"""

    def test_four_dim_extraction(self):
        ext = Extractor().extract(self._md(), arxiv_id="9999.99999", title="GC for Rec")
        self.assertTrue(ext.title)
        self.assertGreater(len(ext.background), 10)
        self.assertGreater(len(ext.method), 10)
        self.assertGreater(len(ext.experiments), 10)

    def test_contributions_and_claims(self):
        ext = Extractor().extract(self._md(), arxiv_id="9999.99999", title="GC for Rec")
        self.assertGreaterEqual(len(ext.contributions), 1)
        self.assertGreaterEqual(len(ext.claims), 1)
        # 每条 claim 必须有合法类型
        for c in ext.claims:
            self.assertIn(c.claim_type.value, {"methodological", "empirical", "theoretical", "positional"})

    def test_method_is_heuristic_by_default(self):
        ext = Extractor().extract(self._md())
        self.assertEqual(ext.extraction_method, "heuristic")


if __name__ == "__main__":
    unittest.main()

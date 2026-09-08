import os
import sys
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from novelty.engine import NoveltyEngine  # noqa: E402


def _write_paper(root: str, aid: str, title: str, body: str) -> None:
    d = os.path.join(root, "data", "parsed", aid)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, f"{aid}.md"), "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n{body}")


class TestEngineE2E(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        _write_paper(self.tmp,
            "2600.00001", "Graph Contrastive Recommendation",
            "## Abstract\nWe propose a graph contrastive learning framework for recommendation "
            "with BPR loss and multi-modal image text signals, evaluated on Amazon.\n"
            "## Method\nWe propose contrastive learning using BPR loss on a graph retriever.\n"
            "## Experiments\nEvaluated on Amazon dataset with Recall@20.")
        _write_paper(self.tmp,
            "2600.00002", "Similar Prior Work",
            "## Abstract\nWe propose a contrastive learning method with BPR loss on a graph "
            "neural network retriever, evaluated on Amazon with Recall@20.\n"
            "## Method\nContrastive learning with BPR loss on graph.\n"
            "## Experiments\nOn Amazon, Recall@20.")
        _write_paper(self.tmp,
            "2600.00003", "Different Transformer Rec",
            "## Abstract\nWe use a transformer with MSE loss on MovieLens, text-only, "
            "trained by reinforcement learning.\n"
            "## Method\nTransformer with MSE loss, reinforcement learning.\n"
            "## Experiments\nOn MovieLens.")
        self.engine = NoveltyEngine(
            data_dir=os.path.join(self.tmp, "data"),
            embedder_kind="pure", use_s2=False, use_openalex=False, top_k=10,
        )

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_analyze_produces_report(self):
        r = self.engine.analyze("2600.00001")
        self.assertEqual(r.arxiv_id, "2600.00001")
        self.assertTrue(r.extraction.title)
        self.assertGreaterEqual(len(r.neighbors), 1)  # 至少有语料近邻
        self.assertIn("corpus_size", r.meta)
        self.assertEqual(r.meta["corpus_size"], 3)
        # 差异矩阵应产出至少一点（与相似邻域论文）
        self.assertGreaterEqual(len(r.difference_matrix), 1)
        # 三态标签之一
        labels = {d.label.value for d in r.difference_matrix}
        self.assertTrue(labels & {"can_refute", "cannot_refute", "unclear"})
        # 不出现终审判定字段
        self.assertNotIn("novel", r.model_dump().keys())

    def test_target_not_in_corpus(self):
        r = self.engine.analyze("0000.00000")
        self.assertEqual(r.meta.get("error"), "target_not_in_corpus")


if __name__ == "__main__":
    unittest.main()

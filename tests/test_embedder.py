import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from novelty.corpus import PaperRecord  # noqa: E402
from novelty.embedder import EmbeddingBackend  # noqa: E402
from novelty.index import VectorIndex  # noqa: E402


class TestEmbedderPure(unittest.TestCase):
    def setUp(self):
        self.backend = EmbeddingBackend(kind="pure")
        self.corpus = [
            PaperRecord(arxiv_id="a", title="A", text="graph contrastive learning recommendation BPR loss amazon dataset"),
            PaperRecord(arxiv_id="b", title="B", text="graph contrastive recommendation alignment module multi-modal image text"),
            PaperRecord(arxiv_id="c", title="C", text="completely unrelated topic about cooking recipes pasta tomato"),
        ]

    def test_similar_ranks_higher_than_dissimilar(self):
        idx = VectorIndex(self.backend).build(self.corpus)
        # query 与 a/b 同域，与 c 异域
        res = idx.search("graph contrastive learning recommendation BPR", top_k=3, exclude=None)
        self.assertEqual(res[0][0], "a")
        # c 应排在最后
        self.assertEqual(res[-1][0], "c")

    def test_query_transform_consistency(self):
        # 先建库（拟合），再检索（transform），结果应稳定可复现
        idx = VectorIndex(self.backend).build(self.corpus)
        r1 = idx.search("graph recommendation", top_k=3)
        r2 = idx.search("graph recommendation", top_k=3)
        self.assertEqual([x[0] for x in r1], [x[0] for x in r2])


class TestEmbedderTfidf(unittest.TestCase):
    def test_tfidf_backend(self):
        try:
            import sklearn  # noqa: F401
        except Exception:
            self.skipTest("sklearn not available")
        backend = EmbeddingBackend(kind="tfidf")
        corpus = [
            PaperRecord(arxiv_id="a", title="A", text="contrastive learning recommendation BPR"),
            PaperRecord(arxiv_id="b", title="B", text="transformer ranking MSE movielens"),
        ]
        idx = VectorIndex(backend).build(corpus)
        res = idx.search("contrastive learning recommendation BPR", top_k=2)
        self.assertEqual(res[0][0], "a")


if __name__ == "__main__":
    unittest.main()

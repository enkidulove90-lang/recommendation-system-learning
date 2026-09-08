"""
novelty/embedder.py — 表示引擎（论文级嵌入后端）

设计文档选型: SPECTER2（proximity adapter）作主干；MiniLM 作轻量兜底；
跨领域鲁棒性要求"嵌入 + BM25 混合召回"，本文件提供可降级的嵌入后端抽象。

后端优先级（kind='auto'）:
    minilm   -> sentence_transformers all-MiniLM-L6-v2（需安装，约 80MB）
    specter2 -> allenai/specter2（需安装，~400MB，研究领域适配最佳）
    tfidf    -> scikit-learn TfidfVectorizer（已装即可用，零下载）
    pure     -> 纯 Python TF-IDF（仅 stdlib，绝对可跑，最慢）

所有后端输出 L2 归一化向量，使余弦相似度 = 向量内积。
"""

from __future__ import annotations

import logging
import math
import re
from typing import Iterable, List, Sequence

logger = logging.getLogger(__name__)


def _has(module: str) -> bool:
    try:
        __import__(module)
        return True
    except Exception:
        return False


class EmbeddingBackend:
    """统一嵌入接口。encode(texts) -> list[list[float]]（L2 归一化）。"""

    def __init__(self, kind: str = "auto", model_name: str | None = None) -> None:
        self.kind = self._resolve(kind)
        self.model_name = model_name
        self._model = None
        self._vec_dim = 0
        # 纯 Python 后端: 首次 encode 拟合并固化词表/idf，后续仅 transform
        self._pure_vocab: list[str] | None = None
        self._pure_idf: dict[str, float] | None = None
        self._init_backend()

    # ------------------------------------------------------------------
    def _resolve(self, kind: str) -> str:
        if kind in ("minilm", "specter2", "tfidf", "pure"):
            return kind
        # auto: 选最先可用的
        if _has("sentence_transformers"):
            return "minilm"
        if _has("sklearn"):
            return "tfidf"
        return "pure"

    def _init_backend(self) -> None:
        if self.kind == "minilm":
            self._init_sentence_transformers(self.model_name or "sentence-transformers/all-MiniLM-L6-v2")
        elif self.kind == "specter2":
            self._init_sentence_transformers(self.model_name or "allenai/specter2")
        elif self.kind == "tfidf":
            self._init_tfidf()
        else:
            self._vec_dim = 0  # 纯 Python 动态维度
        logger.info("[EmbeddingBackend] kind=%s dim=%s", self.kind, self._vec_dim or "dynamic")

    def _init_sentence_transformers(self, name: str) -> None:
        from sentence_transformers import SentenceTransformer
        self._model = SentenceTransformer(name)
        self._vec_dim = self._model.get_sentence_embedding_dimension()

    def _init_tfidf(self) -> None:
        from sklearn.feature_extraction.text import TfidfVectorizer
        # 默认不拟合；fit 在首次 encode 的批内完成（检索语料同源）。
        # min_df 在 fit 时按语料规模自适应（小语料用 1，避免全部被剪枝）。
        self._model = TfidfVectorizer(
            max_features=20000, min_df=2, ngram_range=(1, 2),
            token_pattern=r"(?u)\b[\w\u4e00-\u9fff]+\b",
        )
        self._fitted = False
        self._vec_dim = 20000

    # ------------------------------------------------------------------
    def encode(self, texts: Sequence[str]) -> List[List[float]]:
        if self.kind in ("minilm", "specter2"):
            vecs = self._model.encode(list(texts), normalize_embeddings=True, show_progress_bar=False)
            return [list(map(float, v)) for v in vecs]
        if self.kind == "tfidf":
            return self._encode_tfidf(texts)
        return self._encode_pure(texts)

    def _encode_tfidf(self, texts: Sequence[str]) -> List[List[float]]:
        if not self._fitted:
            # 小语料放宽 min_df，避免全部词被剪枝
            self._model.min_df = 1 if len(texts) <= 5 else 2
            self._model.fit(list(texts))
            self._fitted = True
        # 注意: 若后续 encode 新文本（检索时 query 不在 fit 词表），需 transform
        mats = self._model.transform(list(texts))
        out = []
        for i in range(mats.shape[0]):
            row = mats[i].toarray()[0].astype(float)
            n = math.sqrt(float((row * row).sum())) or 1.0
            out.append((row / n).tolist())
        return out

    def _encode_pure(self, texts: Sequence[str]) -> List[List[float]]:
        # 纯 Python TF-IDF（仅 stdlib），用于无 sklearn/sentence_transformers 的环境。
        # 首次调用拟合并固化词表/idf；之后调用均基于同一词表 transform，
        # 以保证检索 query 向量与建库 corpus 向量可比。
        if self._pure_vocab is None:
            docs = [self._tokenize(t) for t in texts]
            df: dict[str, int] = {}
            for toks in docs:
                for w in set(toks):
                    df[w] = df.get(w, 0) + 1
            n = len(docs)
            idf = {w: math.log((n + 1) / (c + 1)) + 1.0 for w, c in df.items()}
            self._pure_vocab = sorted(idf.keys())
            self._pure_idf = idf
            self._vec_dim = len(self._pure_vocab)

        vocab = self._pure_vocab
        idf = self._pure_idf
        idx = {w: i for i, w in enumerate(vocab)}
        out = []
        for t in texts:
            toks = self._tokenize(t)
            vec = [0.0] * len(vocab)
            for w in toks:
                if w in idx:
                    vec[idx[w]] += idf[w]
            norm = math.sqrt(sum(v * v for v in vec)) or 1.0
            out.append([v / norm for v in vec])
        return out

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return re.findall(r"[a-zA-Z0-9\u4e00-\u9fff]+", text.lower())

    @property
    def dim(self) -> int:
        return self._vec_dim

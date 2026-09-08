"""
novelty/index.py — 向量检索（邻域论文召回）

封装嵌入后向量的近似/精确最近邻检索。后端可降级:
    faiss   -> faiss.IndexFlatIP（若安装，余弦=内积，最快）
    numpy   -> numpy 矩阵内积（已装即可用）
    linear  -> 纯 Python 余弦（仅 stdlib，兜底）

提供 save/load 以支持运维层"本地 FAISS/图索引"缓存与快照版本化（设计文档 §3/§7）。
"""

from __future__ import annotations

import json
import logging
import math
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)

try:
    import numpy as np
    _NP = True
except Exception:
    np = None
    _NP = False

try:
    import faiss  # type: ignore
    _FAISS = True
except Exception:
    faiss = None
    _FAISS = False


def _cosine_list(a: Sequence[float], b: Sequence[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


class VectorIndex:
    """对一组文本建立可检索的向量索引。"""

    def __init__(self, backend) -> None:
        self.backend = backend
        self.ids: List[str] = []
        self._np_mat = None          # numpy 矩阵（若可用）
        self._vecs: List[List[float]] = []  # 纯 Python 兜底
        self._faiss = None

    # ------------------------------------------------------------------
    def build(self, records: Sequence, text_accessor=lambda r: r.text) -> "VectorIndex":
        self.ids = [getattr(r, "arxiv_id", str(i)) for i, r in enumerate(records)]
        texts = [text_accessor(r) or "" for r in records]
        vecs = self.backend.encode(texts)
        if _NP:
            self._np_mat = np.asarray(vecs, dtype=np.float32)
        else:
            self._vecs = vecs
        if _FAISS and _NP:
            d = self._np_mat.shape[1]
            self._faiss = faiss.IndexFlatIP(d)
            self._faiss.add(self._np_mat)
        logger.info("[VectorIndex] built index for %d docs (faiss=%s numpy=%s)",
                    len(self.ids), _FAISS, _NP)
        return self

    # ------------------------------------------------------------------
    def search(self, query_text: str, top_k: int = 10, exclude: Optional[str] = None
               ) -> List[Tuple[str, float]]:
        if not self.ids:
            return []
        q = self.backend.encode([query_text])[0]
        scores: List[Tuple[str, float]] = []

        if self._faiss is not None:
            k = min(top_k + 5, len(self.ids))
            sims, idxs = self._faiss.search(np.asarray([q], dtype=np.float32), k)
            for s, i in zip(sims[0], idxs[0]):
                if i < 0:
                    continue
                aid = self.ids[i]
                if aid == exclude:
                    continue
                scores.append((aid, float(s)))
        elif _NP and self._np_mat is not None:
            qa = np.asarray(q, dtype=np.float32)
            sims = self._np_mat @ qa  # 已 L2 归一化 -> 余弦
            order = np.argsort(-sims)[: top_k + 5]
            for i in order:
                aid = self.ids[int(i)]
                if aid == exclude:
                    continue
                scores.append((aid, float(sims[i])))
        else:
            for aid, vec in zip(self.ids, self._vecs):
                if aid == exclude:
                    continue
                scores.append((aid, _cosine_list(q, vec)))
            scores.sort(key=lambda x: -x[1])

        # 去重 + 截断
        seen = set()
        out = []
        for aid, sc in scores:
            if aid in seen:
                continue
            seen.add(aid)
            out.append((aid, sc))
            if len(out) >= top_k:
                break
        return out

    # ------------------------------------------------------------------
    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        meta = {"ids": self.ids, "backend": self.backend.kind, "dim": self.backend.dim}
        (path / "index_meta.json").write_text(json.dumps(meta), encoding="utf-8")
        if _NP and self._np_mat is not None:
            np.save(path / "vectors.npy", self._np_mat)
        else:
            (path / "vectors.json").write_text(json.dumps(self._vecs), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path, backend) -> "VectorIndex":
        path = Path(path)
        idx = cls(backend)
        meta = json.loads((path / "index_meta.json").read_text(encoding="utf-8"))
        idx.ids = meta["ids"]
        if _NP and (path / "vectors.npy").exists():
            idx._np_mat = np.load(path / "vectors.npy")
        elif (path / "vectors.json").exists():
            idx._vecs = json.loads((path / "vectors.json").read_text(encoding="utf-8"))
        return idx

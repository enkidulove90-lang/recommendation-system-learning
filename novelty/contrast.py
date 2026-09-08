"""
novelty/contrast.py — 对比模块（设计轴差异矩阵 + 三态标签）

设计文档 §4: 复用 FactReview「设计轴定位矩阵」——把目标论文与邻域工作放在同一组
设计维度上，标出各维度差异点；每个差异点附 OpenNovelty 式
can_refute / cannot_refute / unclear 标签与证据片段。

标签语义（证据导向，非终审判定）:
  - CAN_REFUTE      : 证据显示目标与该邻域论文在此轴上做法高度相似 -> 建议人工审视"是否真新"。
  - CANNOT_REFUTE   : 证据显示目标与该邻域论文在此轴上存在明确差异 -> 可作为潜在区分点。
  - UNCLEAR         : 任一方证据不足，无法判定。

所有结论必须附 evidence 片段；禁止无引用断言（设计文档 §6 幻觉护栏）。
"""

from __future__ import annotations

import logging
import re
from typing import Optional

from .schemas import (
    Claim,
    ContributionExtraction,
    DifferencePoint,
    NeighborPaper,
    NoveltyLabel,
)

logger = logging.getLogger(__name__)


# 设计轴 -> 关键词（中英文），用于从文本抽取该轴"取值"
_AXES: dict[str, list[str]] = {
    "任务设定": ["recommendation", "retrieval", "ranking", "sequential", "session", "推荐", "检索", "排序", "会话"],
    "对齐方式": ["contrastive", "alignment", "knowledge distillation", "cross-modal", "对比学习", "对齐", "蒸馏", "跨模态"],
    "损失项/目标": ["bpr", "mse", "cross-entropy", "infoNCE", "loss", "损失", "负采样", "pairwise"],
    "架构/组件": ["agent", "moe", "mixture-of-experts", "graph", "transformer", "retriever", "智能体", "图网络", "检索器"],
    "数据集": ["amazon", "movielens", "yelp", "lastfm", "douban", "数据集", "benchmark"],
    "评估协议": ["recall@", "ndcg@", "hit rate", "auc", "a/b", "评估指标", "召回率"],
    "模态/信号": ["image", "text", "video", "audio", "multimodal", "视觉", "文本", "视频", "多模态"],
    "训练策略": ["pretrain", "fine-tune", "reinforcement", "augment", "self-supervised", "预训练", "微调", "强化", "自监督"],
}


class ContrastEngine:
    """在目标论文与邻域论文之间生成设计轴差异矩阵。"""

    def build_matrix(self, target: ContributionExtraction,
                     neighbor: NeighborPaper, neighbor_text: str,
                     max_axes: int = 8) -> list[DifferencePoint]:
        tgt_text = self._target_blob(target)
        nb_text = neighbor_text or ""
        points: list[DifferencePoint] = []
        for axis in _AXES:
            t_vals = self._extract_axis(tgt_text, axis)
            n_vals = self._extract_axis(nb_text, axis)
            point = self._compare(axis, t_vals, n_vals, neighbor)
            if point is not None:
                points.append(point)
        return points

    # ------------------------------------------------------------------
    @staticmethod
    def _target_blob(t: ContributionExtraction) -> str:
        parts = [t.method, t.background, t.experiments]
        parts += [c.text for c in t.claims]
        return " ".join(p for p in parts if p)

    def _extract_axis(self, text: str, axis: str) -> list[str]:
        kws = _AXES[axis]
        found = []
        low = text.lower()
        for kw in kws:
            if kw.lower() in low:
                # 取关键词周围片段作为"取值"证据
                found.append(kw)
        # 去重保序
        seen, out = set(), []
        for f in found:
            if f not in seen:
                seen.add(f)
                out.append(f)
        return out

    def _compare(self, axis: str, t_vals: list[str], n_vals: list[str],
                 neighbor: NeighborPaper) -> Optional[DifferencePoint]:
        if not t_vals and not n_vals:
            return None
        t_set, n_set = set(t_vals), set(n_vals)
        shared = t_set & n_set
        only_t = t_set - n_set
        only_n = n_set - t_set

        if t_vals and n_vals and not shared and (only_t or only_n):
            # 双方都有该轴取值但不同 -> 明确差异
            label = NoveltyLabel.CANNOT_REFUTE
            diff = f"目标关注 [{', '.join(t_vals)}]，邻域关注 [{', '.join(n_vals)}]，存在明显差异"
            conf = 0.7
        elif shared and not only_t and not only_n:
            # 完全重合 -> 高度相似，建议审视
            label = NoveltyLabel.CAN_REFUTE
            diff = f"双方在该轴均涉及 [{', '.join(t_vals)}]，做法高度相似"
            conf = 0.6
        elif only_t and not n_vals:
            label = NoveltyLabel.CANNOT_REFUTE
            diff = f"目标涉及 [{', '.join(t_vals)}]，邻域文本未体现该轴"
            conf = 0.5
        elif only_n and not t_vals:
            label = NoveltyLabel.UNCLEAR
            diff = f"邻域涉及 [{', '.join(n_vals)}]，目标文本未体现该轴"
            conf = 0.4
        else:
            label = NoveltyLabel.UNCLEAR
            diff = "证据不足以判定该轴差异"
            conf = 0.3

        evidence = self._evidence(neighbor, n_vals)
        return DifferencePoint(
            axis=axis,
            target_value="; ".join(t_vals) or "（未提取）",
            neighbor_value="; ".join(n_vals) or "（未提取）",
            difference=diff,
            label=label,
            confidence=round(conf, 2),
            evidence=evidence,
            neighbor_title=neighbor.title,
        )

    @staticmethod
    def _evidence(neighbor: NeighborPaper, n_vals: list[str]) -> str:
        base = f"邻域论文《{neighbor.title}》"
        if n_vals:
            base += f" 在该轴涉及: {', '.join(n_vals)}"
        if neighbor.url:
            base += f" [来源: {neighbor.url}]"
        return base

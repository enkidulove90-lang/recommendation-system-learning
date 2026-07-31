# 待确认论文列表

以下论文在创新分析中被引用，但arXiv ID尚未确认。如需入库请提供ID。

| 论文 | 简写 | 描述 | arXiv | GitHub |
|------|------|------|-------|--------|
| Adaptive Multi-modal Recommendation Model | AMMRM | adaptive fusion gates细粒度融合 | 待查 | 待查 |
| Dynamic Preference-aware Recommendation | DPRec | dynamic weighting自适应模态重要性 | 待查 | 待查 |
| Category-guided Adaptive Multi-modal RS | CAMMSR | category-guided dynamic weighting (2026) | 待查 | 待查 |
| Enhanced Graph Representation Augmentation | EGRA | 预训练MMR表示构建item-item图 (2025) | 待查 | 待查 |
| Spectral Modality Optimization for REc | SMORE | 频谱滤波抑制模态噪声 | 待查 | 待查 |
| Multimodal Bootstrap Self-supervised RS | M3BSR | Conditional Diffusion模态去噪 | 待查 | 待查 |
| Heterogeneous Environment-Aware RS | HEARec | heterogeneous environment模拟缺失 (2025) | 待查 | 待查 |
| Single-Branch Network | — | weight sharing + modality sampling (2025) | 待查 | 待查 |

## 创新性汇总

| 方向 | 重合度 | 创新空间 | 代表工作 |
|------|--------|----------|----------|
| 动态门控(Slot-1) | ★★★★★ | ❌ 无 | RLMultimodalRec, MARGO, MAMEX |
| 掩码/去噪(Slot-0) | ★★★☆☆ | ⚠️ 窄 | MMSSL, SMORE, M3BSR |
| 缺失模态填补 | ★★★★☆ | ⚠️ 需改造 | ConfSMoE, I³-MRec, HEARec |
| 模态交互因子 | ★☆☆☆☆ | ✅ 大 | 仅PRISM接近(但方法不同) |
| 系统性框架整合 | ★★☆☆☆ | ✅ 有 | 无直接竞争者 |

**核心创新建议**: 聚焦「模态交互因子」——用轻量级成对交互矩阵 W_inter[m,n] 显式建模模态间协同/冲突关系，这是当前所有工作都没有直接涉足的空白。
---
*由 Claude 生成*

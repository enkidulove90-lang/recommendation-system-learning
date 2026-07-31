# LightGCN++：重访LightGCN的不灵活性与不一致性

**英文标题**: Revisiting LightGCN: Unexpected Inflexibility, Inconsistency, and A Remedy
**arXiv ID**: 待查（RecSys 2024, KAIST）
**GitHub**: https://github.com/geon0325/LightGCNpp
**作者**: Geon Lee, Kyungho Kim, Fanchen Bu, Langzhang Liang, Kijung Shin (KAIST)

---

## 主要贡献

系统分析LightGCN结构上的两大问题：(1)embedding scaling不灵活——固定权重和无法区分不同层的重要性；(2)layer-wise pooling不一致。提出LightGCN++修复，NDCG@10最高提升29.38%。

## 创新点

1. 灵活embedding scaling：可学习权重替代固定和
2. 邻居权重学习：替代均匀聚合，区分不同邻居贡献
3. 定制化逐层pooling：替代简单平均，各层独立参数

## 说明

GitHub: https://github.com/geon0325/LightGCNpp。PDF待下载。

---
*由 Claude 自动生成*

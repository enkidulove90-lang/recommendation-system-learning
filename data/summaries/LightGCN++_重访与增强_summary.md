# LightGCN++：重访LightGCN的不灵活性与不一致性

**英文标题**: Revisiting LightGCN: Unexpected Inflexibility, Inconsistency, and A Remedy
**会议**: RecSys 2024 (ACM)
**作者**: Geon Lee, Kyungho Kim, Kijung Shin (KAIST)
**GitHub**: https://github.com/geon0325/LightGCNpp

---

## 主要贡献

揭示LightGCN三大缺陷：(1)embedding norm scaling不灵活；(2)邻居权重过于均匀；(3)层间embedding不一致。用三个可调超参数(α/β/γ)修复，零额外参数量。5个数据集NDCG@20最高+17.81%。

## 创新点

1. 灵活embedding norm scaling (α)：替代固定权重和，控制各层embedding缩放幅度
2. 自适应邻居权重 (β)：替代均匀聚合，区分不同邻居节点贡献
3. 层间pooling权重重调 (γ)：替代简单平均池化
4. 零额外参数：α/β/γ为超参数调优，无需额外训练参数

## 数据集

Gowalla, Yelp2018, Amazon-Book, MovieLens-1M, LastFM
(7:1:2 train/val/test, emb=64, 2 layers)

## 实验效果

| 数据集 | LightGCN | LightGCN++ | 提升 |
|--------|----------|-----------|------|
| Yelp | 0.0449 | **0.0529** | **+17.81%** |
| MovieLens | 0.3010 | 0.3275 | +8.80% |
| LastFM | 0.2427 | 0.2624 | +8.11% |
| Amazon | 0.0274 | 0.0294 | +7.29% |
| Gowalla | 0.1426 | 0.1469 | +3.01% |

作为骨干替换：NCL++最高+16.42%(Yelp)，XSimGCL++最高+14.76%(Amazon)




## 基线方法
待补充

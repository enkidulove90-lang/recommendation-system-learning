#!/bin/bash
# Draft SSR paper for review - DO NOT PUBLISH
export PATH="$HOME/nodejs/node-v24.18.0-win-x64:$PATH"
export NODE_HOME="$HOME/nodejs/node-v24.18.0-win-x64"

opencli xiaohongshu publish "🎓 推荐系统做大模型Scaling，加更多参数反而性能饱和甚至下降？阿里国际SIGIR2026论文SSR发现：92%的连接权重被压到接近零，80%的能量集中在4%的维度——dense架构根本不匹配推荐场景的稀疏特性。

SSR提出显式稀疏框架：多视图稀疏过滤→密集融合，把被动权重压缩变成主动信号筛选。

✨ 核心亮点
• SSR-S(静态随机过滤)：固定二值选择矩阵，零额外推理成本，56%参数44%FLOPs超越RankMixer
• SSR-D(迭代竞争稀疏ICS)：可微分动态稀疏机制，点击AUC+0.46pt，支付AUC+0.72pt
• 在线A/B：CTR+2.1%，订单+3.2%，GMV+3.5%，延迟仅+1ms
• Avazu上SSR-S仅用51%参数就超越所有基线

🧠 方法：Filter-then-Fuse
1. 多视图稀疏过滤——输入分解为并行视图，每视图维度级稀疏筛选
2. 密集融合——过滤后视图独立通过块对角变换，拼接输出
3. ICS迭代竞争稀疏——受生物种群竞争启发的可微分机制，多轮迭代产生真正零值

📊 Scaling实验关键发现
dense MLP参数增大后性能早饱和，而SSR随参数规模(~900M)持续提升——稀疏架构更高效利用大参数量。

💡 可探索方向
方向一：SSR+MoE——SSR在特征维度稀疏，MoE在样本维度稀疏，两者正交可组合
方向二：通用预处理模块——SSR的Filter-then-Fuse可作为任意推荐骨干的前置模块
方向三：端侧部署——SSR-S静态稀疏可直接编译为内存访问模式，适合移动端推理

📄 arXiv：https://arxiv.org/abs/2604.08011
💻 GitHub：https://github.com/Atticus666/SSRNet
🏫 阿里国际(AliExpress) SIGIR2026 Full Paper" \
  --title "SIGIR26｜SSR显式稀疏推荐框架" \
  --topics "推荐系统,LLM,SIGIR,论文分享,AI" \
  --draft true \
  -f json

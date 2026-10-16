# 摘要库编号体检报告

- 扫描目录：`data/summaries`
- 摘要条目：90 条（按编号去重后），其中 arXiv 编号 74 个
- 结论：✅一致 68 / ⚠️略有差异 3 / ❌严重不符 3 / ❓查无此文 0 / ⏭非 arXiv 16 / 🔍需人工核对 0

## ❌ 严重不符（基本可判定编号挂错，优先处理）（3）

| 摘要文件 | 记录标题 | arXiv 真实标题 | 相似度 |
|---|---|---|---|
| `2303.05979_SingleBranch：多模态训练单分支网络_summary.md` | Single-branch Network for Multimodal Training | A counterexample to the theorem of Laplace-Lagrange on the stability o | 0.21 |
| `2504.00678_LLM增强的多阶段推荐系统_summary.md` | LLM-Enhanced Multi-Stage Recommendation: From Recall to Re-Ranking | RapidPD: Rapid Human and Pet Presence Detection System for Smart Vehic | 0.33 |
| `2507.02097_summary.md` | Agentic Recommender Systems: Architectures, Challenges, and Evaluation | The Future is Agentic: Definitions, Perspectives, and Open Challenges  | 0.32 |

## ⚠️ 标题略有差异（看是否是副标题/版本差异）（3）

| 摘要文件 | 记录标题 | arXiv 真实标题 | 相似度 |
|---|---|---|---|
| `2508.08828_summary.md` | Research Paper Recommender Systems: A Survey | Recent Advances and Trends in Research Paper Recommender Systems: A Co | 0.66 |
| `2510.22049_VISTA：虚拟序列目标注意力_summary.md` | VISTA: Virtual Sequential Target Attention for Massive Memorization in | Massive Memorization with Hundreds of Trillions of Parameters for Sequ | 0.61 |
| `2605.25007_summary.md` | Meta-Modal Agent: Sequential Evidence Routing for Missing-Modality Can | Route What Remains: A Meta-Modal Agent for Missing-Modality Candidate  | 0.61 |

## ⏭ 非 arXiv 编号（DOI / 期刊 / 会议，需另行核对）（16）

| 摘要文件 | 编号 | 说明 |
|---|---|---|
| `3792192_MSCA_多视图语义对比对齐的多模态推荐_summary.md` | `-` | 未填写编号 |
| `3792192_summary.md` | `3792192` | 编号非 arXiv 格式 |
| `3806158_MMGCF_多模态图协同过滤与轻量级融合策略_summary.md` | `-` | 未填写编号 |
| `3806158_summary.md` | `3806158` | 编号非 arXiv 格式 |
| `3806231_NLGCL-Plus_邻接层自然对比学习与自适应样本加权_summary.md` | `-` | 未填写编号 |
| `3806231_summary.md` | `3806231` | 编号非 arXiv 格式 |
| `AMMRM_summary.md` | `AMMRM` | 编号非 arXiv 格式 |
| `AMMRM：自适应多模态噪声过滤推荐_summary.md` | `-` | 未填写编号 |
| `DPRec：双路径多模态推荐_summary.md` | `无（仅ACM出版）` | 编号非 arXiv 格式 |
| `HEARec：异构环境感知多模态推荐_summary.md` | `无` | 编号非 arXiv 格式 |
| `LightGCN++_summary.md` | `LightGCN++` | 编号非 arXiv 格式 |
| `LightGCN++_重访与增强_summary.md` | `-` | 未填写编号 |
| `OTRec_IEEE_TMM：最优传输跨模态推荐_summary.md` | `-` | 未填写编号 |
| `csa1543994_summary.md` | `csa1543994` | 编号非 arXiv 格式 |
| `gpt-red_summary.md` | `gpt-red` | 编号非 arXiv 格式 |
| `ra-rft_summary.md` | `ra-rft` | 编号非 arXiv 格式 |

## ✅ 一致（68）

| 摘要文件 | 编号 | 说明 |
|---|---|---|
| `2002.02126_LightGCN_summary.md` | `2002.02126` | LightGCN: Simplifying and Powering Graph Convolution Network for Recommendation |
| `2302.08191_summary.md` | `2302.08191` | LightGCL: Simple Yet Effective Graph Contrastive Learning for Recommendation |
| `2302.10632_MMSSL：多模态自监督推荐_summary.md` | `2302.10632` | Multi-Modal Self-Supervised Learning for Recommendation |
| `2308.15980_AMF：多模态自适应融合_seqrec_summary.md` | `2308.15980` | Adaptive Multi-Modalities Fusion in Sequential Recommendation Systems |
| `2403.06447_summary.md` | `2403.06447` | CoRAL: Collaborative Retrieval-Augmented Large Language Models Improve Long-tail Recommendation |
| `2404.16924_summary.md` | `2404.16924` | A Survey of Generative Search and Recommendation in the Era of Large Language Models |
| `2407.18940_summary.md` | `2407.18940` | LitSearch: A Retrieval Benchmark for Scientific Literature Search |
| `2412.14978_summary.md` | `2412.14978` | Spectrum-based Modality Representation Fusion Graph Convolutional Network for Multimodal Recommendat |
| `2412.19302_summary.md` | `2412.19302` | RecLM: Recommendation Instruction Tuning |
| `2501.01945_summary.md` | `2501.01945` | Cold-Start Recommendation towards the Era of Large Language Models (LLMs): A Comprehensive Survey an |
| `2501.10120_PaSa：学术论文搜索智能体_summary.md` | `2501.10120` | PaSa: An LLM Agent for Comprehensive Academic Paper Search |
| `2502.09058_summary.md` | `2502.09058` | Unleashing the Power of Large Language Model for Denoising Recommendation |
| `2503.00987_summary.md` | `2503.00987` | Probability of Transition to Turbulence in a Reduced Stochastic Model of Pipe Flow |
| `2503.16734_summary.md` | `2503.16734` | Towards Agentic Recommender Systems in the Era of Multimodal Large Language Models |
| `2504.16420_summary.md` | `2504.16420` | A Survey of Foundation Model-Powered Recommender Systems: From Feature-Based, Generative to Agentic  |
| `2504.16524_MARGO：模态可靠性引导多模态推荐_summary.md` | `2504.16524` | Modality Reliability Guided Multimodal Recommendation |
| `2505.00556_summary.md` | `2505.00556` | When is $A + x A =\mathbb{R}$ |
| `2505.05196_RAG推荐系统数据投毒攻击_summary.md` | `2505.05196` | Stealthy LLM-Driven Data Poisoning Attacks Against Embedding-Based Retrieval-Augmented Recommender S |
| `2505.09777_summary.md` | `2505.09777` | A Survey on Large Language Models in Multimodal Recommender Systems |
| `2505.19525_summary.md` | `2505.19525` | Rethinking Gating Mechanism in Sparse MoE: Handling Arbitrary Modality Inputs with Confidence-Guided |
| `2505.20773_summary.md` | `2505.20773` | Adaptive Candidate Retrieval with Dynamic Knowledge Graph Construction for Cold-Start Recommendation |
| `2506.00107_RLMultimodalRec：门控多模态图推荐_summary.md` | `2506.00107` | Gated Multimodal Graph Learning for Personalized Recommendation |
| `2506.07261_summary.md` | `2506.07261` | RADAR: Recall Augmentation through Deferred Asynchronous Retrieval |
| `2506.18019_summary.md` | `2506.18019` | Graphs Meet AI Agents: Taxonomy, Progress, and Future Opportunities |
| `2507.00715_EARN：基于注册令牌的LLM推荐加速_summary.md` | `2507.00715` | EARN: Efficient Inference Acceleration for LLM-based Generative Recommendation by Register Tokens |
| `2507.02626_VRAgent-R1：强化学习增强视频推荐_summary.md` | `2507.02626` | VRAgent-R1: Boosting Video Recommendation with MLLM-based Agents via Reinforcement Learning |
| `2507.05863_summary.md` | `2507.05863` | KERAG_R: Knowledge-Enhanced Retrieval-Augmented Generation for Recommendation |
| `2507.07522_summary.md` | `2507.07522` | NLGCL: Naturally Existing Neighbor Layers Graph Contrastive Learning for Recommendation |
| `2507.15245_summary.md` | `2507.15245` | SPAR: Scholar Paper Retrieval with LLM-based Agents for Enhanced Academic Search |
| `2507.21117_summary.md` | `2507.21117` | A Comprehensive Review on Harnessing Large Language Models to Overcome Recommender System Challenges |
| `2507.21892_summary.md` | `2507.21892` | Graph-R1: Towards Agentic GraphRAG Framework via End-to-end Reinforcement Learning |
| `2508.00543_summary.md` | `2508.00543` | Towards Efficient Certification of Maritime Remote Operation Centers |
| `2508.04247_summary.md` | `2508.04247` | I$^3$-MRec: Invariant Learning with Information Bottleneck for Incomplete Modality Recommendation |
| `2508.05352_M3BSR：多模态多行为序列推荐_summary.md` | `2508.05352` | Multi-Modal Multi-Behavior Sequential Recommendation with Conditional Diffusion-Based Feature Denois |
| `2508.05666_summary.md` | `2508.05666` | HySemRAG: A Hybrid Semantic Retrieval-Augmented Generation Framework for Automated Literature Synthe |
| `2508.08042_MAMEX：多模态自适应MoE冷启动推荐_summary.md` | `2508.08042` | Multi-modal Adaptive Mixture of Experts for Cold-start Recommendation |
| `2509.13179_summary.md` | `2509.13179` | Efficient Cold-Start Recommendation via BPE Token-Level Embedding Initialization with LLM |
| `2510.21652_AstaBench：AI智能体科学基准_summary.md` | `2510.21652` | AstaBench: Rigorous Benchmarking of AI Agents with a Scientific Research Suite |
| `2510.27566_summary.md` | `2510.27566` | Interact-RAG: Reason and Interact with the Corpus, Beyond Black-Box Retrieval |
| `2511.15141_ItemRAG：基于物品的检索增强生成推荐_summary.md` | `2511.15141` | ItemRAG: Item-Based Retrieval-Augmented Generation for LLM-Based Recommendation |
| `2512.20916_summary.md` | `2512.20916` | MMSRARec: Summarization and Retrieval Augumented Sequential Recommendation Based on Multimodal Large |
| `2512.21526_summary.md` | `2512.21526` | Selective LLM-Guided Regularization for Enhancing Recommendation Models |
| `2601.10944_PRISM：信息协同模块个性化推荐_summary.md` | `2601.10944` | PRISM: Personalized Recommendation via Information Synergy Module |
| `2601.13969_summary.md` | `2601.13969` | Autonomous Knowledge Graph Exploration with Adaptive Breadth-Depth Retrieval |
| `2601.22498_summary.md` | `2601.22498` | FITMM: Adaptive Frequency-Aware Multimodal Recommendation via Information-Theoretic Representation L |
| `2602.00682_summary.md` | `2602.00682` | RecGOAT: Graph Optimal Adaptive Transport for LLM-Enhanced Multimodal Recommendation with Dual Seman |
| `2602.20723_summary.md` | `2602.20723` | Modality-Guided Mixture of Structured Experts with Entropy-Triggered Routing for Multimodal Recommen |
| `2602.21756_summary.md` | `2602.21756` | Offline Reasoning for Efficient Recommendation: LLM-Empowered Persona-Profiled Item Indexing |
| `2603.04320_CAMMSR：类别引导注意力MoE多模态序列推荐_summary.md` | `2603.04320` | CAMMSR: Category-Guided Attentive Mixture of Experts for Multimodal Sequential Recommendation |
| `2603.10673_summary.md` | `2603.10673` | Breaking User-Centric Agency: A Tri-Party Framework for Agent-Based Recommendation |
| `2604.08011_summary.md` | `2604.08011` | Beyond Dense Connectivity: Explicit Sparsity for Scalable Recommendation |
| `2604.12965_summary.md` | `2604.12965` | Efficient Retrieval Scaling with Hierarchical Indexing for Large Scale Recommendation |
| `2604.16318_summary.md` | `2604.16318` | Diagnosing LLM-based Rerankers in Cold-Start Recommender Systems: Coverage, Exposure and Practical M |
| `2604.20848_summary.md` | `2604.20848` | MATRAG: Multi-Agent Transparent Retrieval-Augmented Generation for Explainable Recommendations |
| `2605.10730_summary.md` | `2605.10730` | Qwen-Image-2.0 Technical Report |
| `2605.14306_summary.md` | `2605.14306` | Towards Recursive Self-Evolving Agentic Literature Retrieval |
| `2605.28175_summary.md` | `2605.28175` | Mixture-of-Experts Knowledge Graph Retrieval-Augmented Generation for Multi-Agent LLM-based Recommen |
| `2606.09595_summary.md` | `2606.09595` | Popcorn: A Configurable Benchmark for Visual Evidence in Multimodal Movie Recommendation |
| `2606.12373_summary.md` | `2606.12373` | Verifiable Environments Are LEGO Bricks: Recursive Composition for Reasoning Generalization |
| `2606.22151_summary.md` | `2606.22151` | Novelty-Aware Agentic Retrieval: Comparing Research Contributions Through Structured Multi-Step Reas |
| `2606.24597_summary.md` | `2606.24597` | Qwen-AgentWorld: Language World Models for General Agents |
| `2606.26859_summary.md` | `2606.26859` | AgentX: Towards Agent-Driven Self-Iteration of Industrial Recommender Systems |
| `2607.02980_summary.md` | `2607.02980` | Hierarchical Sparse Attention Done Right: Toward Infinite Context Modeling |
| `2607.04433_summary.md` | `2607.04433` | Autonomous Information Seeking: A Roadmap for Agentic Recommender Systems |
| `2607.07108_summary.md` | `2607.07108` | Seeing and Reflecting: Multimodal Memory-Enhanced Agent Collaboration for Recommendation |
| `2607.26720_summary.md` | `2607.26720` | CaIRec: Calibrated Modality Imputation for Incomplete Multimodal Recommendation |
| `2608.00267_summary.md` | `2608.00267` | LoopsBench: From Harness Engineering to Loop Engineering in Coding Agent Evaluation |
| `2608.14429_summary.md` | `2608.14429` | PriCoRec: A Privacy-Aware Cloud-Device Collaborative Framework for Ad Recommendation under Feature C |

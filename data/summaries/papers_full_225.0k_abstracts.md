# 推荐系统前沿论文集 — 摘要提取结果

**源文件**: `papers_full_225.0k.md`  
**实际解析论文数**: 17 篇  
**摘要总字符数**: 26,023

---

## [1/17] RADAR: Recall Augmentation through Deferred Asynchronous Retrieval

**arXiv ID**: 2506.07261  
**摘要长度**: 1318 字符

**Abstract**:
Modern large-scale recommender systems employ multi-stage ranking funnel (Retrieval, Pre-ranking, Ranking) to balance engagement and computational constraints (latency, CPU). However, the initial retrieval stage, often relying on efficient but less precise methods like K-Nearest Neighbors (KNN), struggles to effectively surface the most engaging items from billion-scale catalogs, particularly distinguishing highly relevant and engaging candidates from merely relevant ones. We introduce Recall Augmentation through Deferred Asynchronous Retrieval (RADAR), a novel framework that leverages asynchronous, offline computation to pre-rank a significantly larger candidate set for users using the full complexity ranking model. These topranked items are stored and utilized as a high-quality retrieval source during online inference, bypassing online retrieval and preranking stages for these candidates. We demonstrate through offline experiments that RADAR significantly boosts recall (2X Recall@200 vs DNN retrieval baseline) by effectively combining a larger retrieved candidate set with a more powerful ranking model. Online A/B tests confirm a +0.8% lift in topline engagement metrics, validating RADAR as a practical and effective method to improve recommendation quality under strict online serving constraints.

---

## [2/17] Efficient Cold-Start Recommendation via BPE Token-Level Embedding Initialization with LLM

**arXiv ID**: 2509.13179  
**摘要长度**: 1841 字符

**Abstract**:
The cold-start issue is the challenge when we talk about recommender systems, especially in the case when we do not have the past interaction data of new users or new items. Content-based features or hybrid solutions are common as conventional solutions, but they can only work in a sparse metadata environment with shallow patterns. In this paper, the efficient cold-start recommendation strategy is presented, which is based on the sub word-level representations by applying Byte Pair Encoding (BPE) tokenization and pretrained Large Language Model (LLM) embedding in the initialization procedure. We obtain fine-grained token-level vectors that are aligned with the BPE vocabulary as opposed to using coarse-grained sentence embeddings. Together, these token embeddings can be used as dense semantic priors on unseen entities, making immediate recommendation performance possible without user-item interaction history. Our mechanism can be compared to collaborative filtering systems and tested over benchmark datasets with stringent cold-start assumptions. Experimental findings show that the given BPE-LLM method achieves higher Recall@k, NDCG@k, and Hit Rate measurements compared to the standard baseline and displays the same capability of sufficient computational performance. Furthermore, we demonstrate that using subword-aware embeddings yields better generalizability and is more interpretable, especially within a multilingual and sparse input setting. The practical application of token-level semantic initialization as a lightweight, but nevertheless effective extension to modern recommender systems in the zero-shot setting is indicated within this work. Keywords: Cold-start recommendation, BPE tokenization, Large Language Models, embedding initialization, recommender systems, semantic representation, zero-shot learning

---

## [3/17] Stealthy LLM-Driven Data Poisoning Atacks Against Embedding-Based Retrieval-Augmented Recommender Systems

**arXiv ID**: 2505.05196  
**摘要长度**: 954 字符

**Abstract**:
We present a systematic study of provider-side data poisoning in retrieval-augmented recommender systems (RAG-based). By modi fying only a small fraction of tokens within item descriptions—for instance, adding emotional keywords or borrowing phrases from semantically related items—an attacker can significantly promote or demote targeted items. We formalize these attacks under token-edit and semantic-similarity constraints, and we examine their efective ness in both promotion (long-tail items) and demotion (short-head items) scenarios. Our experiments on MovieLens, using two large language model (LLM) retrieval modules, show that even subtle attacks shift final rankings and item exposures while eluding naive detection. The results underscore the vulnerability of RAG-based pipelines to small-scale metadata rewrites, and emphasize the need for robust textual consistency checks and provenance tracking to thwart stealthy provider-side poisoning.

---

## [4/17] Popcorn: A Configurable Benchmark for Visual Evidence in Multimodal Movie Recommendation

**arXiv ID**: 2606.09595  
**摘要长度**: 1073 字符

**Abstract**:
Movies are long-form audiovisual works, yet recommender benchmarks often rely on trailers, thumbnails, or metadata. These sources difer in semantics and scalability: full movies preserve consumption-level evidence, trailers concentrate promotional highlights, and thumbnails provide sparse but catalog-scale visual signals. We present Popcorn, a configurable benchmark for visual evidence in multimodal movie recommendation, combining title-aligned full-movie/trailer embeddings with MovieLens-linked thumbnail features encoded by modern visual and vision-language models. Popcorn standardizes modality assembly, fusion, splitting, evaluation, and LLM-augmented metadata through a single configuration contract. Experiments show that thumbnail VLMs provide strong, scalable item-side evidence, while controlled trailer/full-movie comparisons show that visual evidence sources are not interchangeable: the choice of source and fusion strategy afects ranking accuracy, coverage, diversity, and calibration. The framework is available at https://github.com/RecSys-lab/Popcorn.

---

## [5/17] Selective LLM-Guided Regularization for Enhancing Recommendation Models

**arXiv ID**: 2512.21526  
**摘要长度**: 1309 字符

**Abstract**:
Large language models (LLMs) provide rich semantic priors and strong reasoning capabilities, making them promising auxiliary signals for recommendation. However, prevailing approaches ei ther deploy LLMs as standalone recommenders or apply global knowledge distillation, both of which sufer from inherent drawbacks. Standalone LLM recommenders are costly, biased, and un reliable across large regions of the user–item space, while global distillation forces the downstream model to imitate LLM predictions even when such guidance is inaccurate. Meanwhile, recent studies show that LLMs excel particularly in re-ranking and chal lenging scenarios, rather than uniformly across all contexts. We introduce Selective LLM-Guided Regularization (S-LLMR), a modelagnostic and computation-eficient framework that activates LLM based pairwise ranking supervision only when a trainable gating mechanism-informed by user history length, item popularity, and model uncertainty predicts the LLM to be reliable. All LLM scoring is done ofline, transferring knowledge without increasing inference cost. Experiments across multiple datasets show that this selective strategy consistently improves overall accuracy and yields substan tial gains in cold-start and long-tail regimes, outperforming global distillation baselines.

---

## [6/17] Adaptive Candidate Retrieval with Dynamic Knowledge Graph Construction for Cold-Start Recommendation

**arXiv ID**: 2505.20773  
**摘要长度**: 1066 字符

**Abstract**:
The cold-start problem remains a critical challenge in real-world recommender systems, as new items with limited interaction data or insufficient information are frequently introduced. Despite recent advances leveraging external knowledge such as knowledge graphs (KGs) and large language models (LLMs), recommender systems still face challenges in practical environments. Static KGs are expensive to construct and quickly become outdated, while LLM-based methods depend on pre-filtered candidate lists due to limited context windows. To address these limitations, we propose ColdRAG, a retrieval-augmented framework that dynamically constructs a knowledge graph from raw metadata, extracts entities and relations to construct an updatable structure, and introduces LLM-guided multihop reasoning at inference time to retrieve and rank candidates without relying on prefiltered lists. Experiments across multiple benchmarks show that ColdRAG consistently outperforms strong seven baselines. Our implementation is available at https://github. com/WooseongYang/ColdRAG.

---

## [7/17] ItemRAG: Item-Based Retrieval-Augmented Generation for LLM-Based Recommendation

**arXiv ID**: 2511.15141  
**摘要长度**: 1431 字符

**Abstract**:
Recently, large language models (LLMs) have been widely used as recommender systems, owing to their reasoning capability and efectiveness in handling cold-start items. A common approach prompts an LLM with a target user’s purchase history to recom mend items from a candidate set, often enhanced with retrieval augmented generation (RAG). Most existing RAG approaches retrieve purchase histories of users similar to the target user; however, these histories often contain noisy or weakly relevant information and provide little or no useful information for candidate items. To address these limitations, we propose ItemRAG, a novel RAG approach that shifts focus from coarse user-history retrieval to finegrained item-level retrieval. ItemRAG augments the description of each item in the target user’s history or the candidate set by retriev ing items relevant to each. To retrieve items not merely semantically similar but informative for recommendation, ItemRAG leverages co purchase information alongside semantic information. Especially, through their careful combination, ItemRAG prioritizes more informative retrievals and also benefits cold-start items. Through exten sive experiments, we demonstrate that ItemRAG consistently out performs existing RAG approaches under both standard and cold start item recommendation settings. Supplementary materials, code, and datasets are provided at https://github.com/kswoo97/ItemRAG.

---

## [8/17] MMSRARec: Summarization and Retrieval Augumented Sequential Recommendation Based on Multimodal Large Language Model

**arXiv ID**: 2512.20916  
**摘要长度**: 1987 字符

**Abstract**:
Recent advancements in Multimodal Large Language Models (MLLMs) have demonstrated significant potential in recommendation systems. However, the efective application of MLLMs to multimodal sequential recommendation remains unexplored: A) Existing methods primarily leverage the multimodal semantic understanding capabilities of pre-trained MLLMs to generate item embeddings or semantic IDs, thereby enhancing traditional recommendation models. These approaches generate item representations that exhibit limited interpretability, and pose challenges when transferring to language model-based recommendation systems. B) Other approaches convert user behavior sequence into image-text pairs and perform recommendation through multiple MLLM inference, incurring prohibitive computational and time costs. C) Current MLLM-based recommendation systems generally neglect the integration of collaborative signals. To address these limitations while balancing recommendation performance, interpretability, and computational cost, this paper proposes MultiModal Summarization-and-Retrieval-Augmented Sequential Recommendation (MMSRARec). Specifically, we first employ MLLM to summarize items into concise keywords and finetune the model using rewards that incorporate summary length, information loss, and reconstruction dificulty, thereby enabling adaptive adjustment of the summarization policy. Inspired by retrieval-augmented generation, we then transform collaborative signals into corresponding keywords and integrate them as supplementary context. Finally, we apply supervised fine-tuning with multi-task learning to align the MLLM with the multimodal sequential recommendation. Extensive evaluations on common recommendation datasets demonstrate the efectiveness of MMSRARec, showcasing its capability to eficiently and interpretably understand user behavior histories and item information for accurate recommendations. Keywords: Sequential Recommendation · Multimodal Large Language Model.

---

## [9/17] Seeing and Reflecting: Multimodal Memory-Enhanced Agent Collaboration for Recommendation

**arXiv ID**: 2607.07108  
**摘要长度**: 1284 字符

**Abstract**:
Large language model (LLM)-based agentic recommender systems show promise in modeling user preferences through natural-language reasoning, yet they remain limited by textcentric inputs and coarse-grained memory updates, making agents prone to missing visual evidence, semantic noise, and preference drift. To address these limitations, we propose MMEACR, a Multimodal Memory-Enhanced Agent Collaboration framework for recommendation. MMEACR introduces a dual-track memory architecture that separates interpretable agent reasoning from fine grained multimodal matching. In the reasoning track, collaborative User and Item Memory Agents maintain persistent multimodal memories and update them through an attributeguided reinforcement-and-reflection mechanism. In the matching track, a decoupled multimodal embedding memory is built from raw interaction narratives and item images to preserve detailed cross-modal signals beyond structured memory updates. The two tracks are integrated through weighted Reciprocal Rank Fusion to produce robust and interpretable rankings. Experiments on three real-world domains show that MMEACR achieves strong overall performance against competitive LLM-based and agent-based baselines, with notable gains in visually grounded recommendation scenarios.

---

## [10/17] Towards Eficient Certification of Maritime Remote Operation Centers – Ansatz zur efizienten Zertifizierung von maritimen Fernsteuerungszentren

**arXiv ID**: 2508.00543  
**摘要长度**: 1710 字符

**Abstract**:
Additional automation being build into ships implies a shift of crew from ship to shore. However, automated ships still have to be monitored and, in some situations, controlled remotely. These tasks are carried out by human operators located in shore-based remote operation centers. In this work, we present a concept for a hazard database that supports the safeguarding and certification of such remote operation centers. The concept is based on a categorization of hazard sources which we derive from a generic functional architecture. A subsequent preliminary suitability analysis unveils which methods for hazard analysis and risk assessment can adequately fill this hazard database. – Die zunehmende Automatisierung von Schifen führt zu einer Verlagerung der Besatzung vom Schif ans Land. Automatisierte Schife müssen jedoch weiterhin überwacht und in bestimmten Situationen ferngesteuert werden. Diese Aufgaben werden von menschlichen Operateuren in landgestützten Fernsteuerungszentren ausgeführt. In dieser Arbeit stellen wir ein Konzept für eine Gefährdungsdatenbank vor, welche die Sicherung und Zertifizierung solcher Fernsteuerungszentren unterstützt. Das Konzept basiert auf einer Kategorisierung von Gefährdungsquellen, abgeleitet aus einer generischen Funktionsarchitektur. Eine anschließende vorläufige Eignungsanalyse zeigt, welche Methoden zur Gefährdungsanalyse und Risikobewertung diese Gefährdungsdatenbank füllen können. Keywords: Remote Operation Center, Autonomous Surface Ships, Hazard Analysis & Risk Assessment, Safety, Certification, Human Factors – Fernsteuerungszentrum, Autonome Überwasserschife, Gefährdungsanalyse und Risikobewertung, Sicherheit, Zertifizierung, Menschfaktoren

---

## [11/17] Diagnosing LLM-based Rerankers in Cold-Start Recommender Systems: Coverage, Exposure and Practical Mitigations

**arXiv ID**: 2604.16318  
**摘要长度**: 1544 字符

**Abstract**:
Large language models (LLMs) and cross-encoder rerankers have gained attention for improving recommender systems, particularly in cold-start scenarios where user interaction history is limited. However, practical deployment reveals significant performance gaps between LLM-based approaches and simple baselines. This paper presents a systematic diagnostic study of cross-encoder rerankers in cold-start movie recommendation using the Serendipity-2018 dataset. Through controlled experiments with 500 users across multiple random seeds, we identify three critical failure modes: (1) low retrieval coverage in candidate generation (recall@200 = 0.109 vs. 0.609 for baselines), (2) severe exposure bias with rerankers concentrating recommendations on 3 unique items versus 497 for random baseline, and (3) minimal score discrimination between relevant and irrelevant items (mean difference = 0.098, Cohen’s d = 0.13). We demonstrate that popularity-based ranking substantially outperforms LLM reranking (HR@10: 0.268 vs. 0.008, p < 0.001), with the performance gap primarily attributable to retrieval stage limitations rather than reranker capacity. Based on these findings, we provide actionable recommendations including hybrid retrieval strategies, candidate pool size optimization, and score calibration techniques. All code, configurations, and experimental results are made available for reproducibility. Index Terms—cold-start recommender systems, reranking, language models, cross-encoders, retrieval diagnostics, evaluation, exposure bias

---

## [12/17] Meta-Modal Agent: Sequential Evidence Routing for Missing-Modality Candidate Reranking

**arXiv ID**: 2605.25007  
**摘要长度**: 1863 字符

**Abstract**:
Missing modalities cause severe failures in multimodal recommender systems. User histories, item text, and visual evidence are frequently absent during cold-start scenarios, exactly when rec ommendation quality matters most. Existing approaches recover absent signals through imputation, feature propagation, or generative reconstruction, but these strategies can inject unsupported evi dence when the surviving signals are weak. We introduce the Meta-Modal Agent (MMA), a large language model based candidate-pool reranker that treats missingness as a sequential evidence-routing problem. MMA is trained with balanced missingness-task reinforcement learning over masked-modality episodes and is eval uated in two variants: MMA-Auto, which uses only automated text, image, and graph tools, and MMA-Interactive, which ad ditionally permits clarification questions grounded in surviving modalities as an upper-bound diagnostic. MMA operates after a first-stage retriever has produced a candidate pool; it scores those candidates rather than retrieving items from the full catalog. Fi nal reranking fuses MMA scores with first-stage retrieval scores selected on validation data. Our evaluation is organized around four evidence checks required for a robust missing-modality claim: oracle-free one-observed-modality availability (OOMA) robustness, per-modality OOMA breakdowns, fixed-pool full-catalog rerank ing, and a deterministic-router mechanism control. MMA-Auto improves target-positive OOMA NDCG@10 by 4.0% and fixed-pool full-catalog reranking NDCG@10 by 12.7% over the strongest noninteractive baseline. RuleRouter-Fuse, which uses the same tools and fusion rule without learned policy updates, underperforms MMA-Auto, supporting learned routing beyond deterministic tool fusion. MMA-Interactive adds a 4.1% upper-bound gain when clarification is available.

---

## [13/17] RapidPD: Rapid Human and Pet Presence Detection System for Smart Vehicles via Wi-Fi

**arXiv ID**: 2504.00678  
**摘要长度**: 1849 字符

**Abstract**:
Heatstroke and life threatening incidents resulting from the retention of children and animals in vehicles pose a critical global safety issue. Current presence detection solutions often require specialized hardware or suffer from detection delays that do not meet safety standards. To tackle this issue, by remodeling channel state information (CSI) with theoretical analysis of path propagation, this study introduces RapidPD, an innovative system utilizing CSI in subcarrier dimension to detect the presence of humans and pets in vehicles. The system models the impact of motion on CSI and introduces motion statistics in subcarrier dimension using a multi-layer autocorrelation method to quantify environmental changes. RapidPD is implemented using commercial Wi-Fi chipsets and tested in real vehicle environments with data collected from 10 living organisms. Experimental results demonstrate that RapidPD achieves a detection accuracy of 99.05% and a true positive rate of 99.32% within a 1-second time window at a low sampling rate of 20 Hz. These findings represent a significant advancement in vehicle safety and provide a foundation for the widespread adoption of presence detection systems. Index Terms—Wi-Fi sensing, smart car, presence detection, channel state information. Manuscript received XXXXX 00, 0000; revised XXXXX 00, 0000; accepted XXXXX 00, 0000. (Corresponding author: Zhen Chen) Authors’ address: Hancheng Guo, and Xiuyin Zhang are with School of Electronic and Information Engineering, South China University of Technology, Guangzhou 510006, China (e-mail: ee ghch@mail.scut.edu.cn; zhangxiuyin@scut.edu.cn). Zhen Chen, and Mo Huang are with the State Key Laboratory of Analog and Mixed-Signal VLSI/Institute of Microelectronics, University of Macau, Macao 999078, China (e-mail: chenz.scut@gmail.com; mohuang@um.edu.mo).

---

## [14/17] Towards Agentic Recommender Systems in the Era of Multimodal Large Language Models

**arXiv ID**: 2503.16734  
**摘要长度**: 1534 字符

**Abstract**:
Recent breakthroughs in Large Language Models (LLMs) have led to the emergence of agentic AI systems that extend beyond the capabilities of standalone models. By empowering LLMs to perceive external environments, integrate multimodal information, and in teract with various tools, these agentic systems exhibit greater autonomy and adaptability across complex tasks. This evolution brings new opportunities to recommender systems (RS): LLM-based Agentic RS (LLM-ARS) can ofer more interactive, context-aware, and proactive recommendations, potentially reshaping the user experience and broadening the application scope of RS. Despite promising early results, fundamental challenges remain, including how to efectively incorporate external knowledge, balance auton omy with controllability, and evaluate performance in dynamic, multimodal settings. In this perspective paper, we first present a systematic analysis of LLM-ARS: (1) clarifying core concepts and architectures; (2) highlighting how agentic capabilities—such as planning, memory, and multimodal reasoning—can enhance rec ommendation quality; and (3) outlining key research questions in areas such as safety, eficiency, and lifelong personalization. We also discuss open problems and future directions, arguing that LLM-ARS will drive the next wave of RS innovation. Ultimately, we foresee a paradigm shift toward intelligent, autonomous, and collaborative recommendation experiences that more closely align with users’ evolving needs and complex decision-making processes.

---

## [15/17] Massive Memorization with Hundreds of Trillions of Parameters for Sequential Transducer Generative Recommenders

**arXiv ID**: 2510.22049  
**摘要长度**: 1526 字符

**Abstract**:
Modern large-scale recommendation systems rely heavily on user interaction history sequences to enhance the model performance. The advent of large language models and sequential modeling techniques, particularly transformer-like architectures, has led to significant advancements recently (e.g., HSTU, SIM, and TWIN models). While scaling to ultra-long user histories (10k to 100k items) generally improves model performance, it also creates significant challenges on latency, queries per second (QPS) and GPU cost in industry-scale recommendation systems. Existing models do not adequately address these industrial scalability issues. In this paper, we propose a novel two-stage modeling framework, namely VIrtual Sequential Target Attention (VISTA), which decomposes traditional target attention from a candidate item to user history items into two distinct stages: (1) user history summarization into a few hundred tokens; followed by (2) candidate item attention to those tokens. These summarization token embeddings are then cached in storage system and then utilized as sequence features for downstream model training and inference. This novel design for scalability enables VISTA to scale to lifelong user histories (up to one million items) while keeping downstream training and inference costs fixed, which is essential in industry. Our approach achieves significant improvements in ofline and online metrics and has been successfully deployed on an industry leading recommendation platform serving billions of users.

---

## [16/17] Ofline Reasoning for Eficient Recommendation: LLM-Empowered Persona-Profiled Item Indexing

**arXiv ID**: 2602.21756  
**摘要长度**: 2311 字符

**Abstract**:
Recent advances in large language models (LLMs) ofer new op portunities for recommender systems by capturing the nuanced semantics of user interests and item characteristics through rich semantic understanding and contextual reasoning. In particular, LLMs have been employed as rerankers that reorder candidate items based on inferred user–item relevance. However, these approaches often require expensive online inference-time reasoning, leading to high latency that hampers real-world deployment. In this work, we introduce Persona4Rec, a recommendation framework that performs ofline reasoning to construct interpretable persona representations of items, enabling lightweight and scalable real-time inference. In the ofline stage, Persona4Rec leverages LLMs to reason over item reviews, inferring diverse user motiva tions that explain why diferent types of users may engage with an item; these inferred motivations are materialized as persona representations, providing multiple, human-interpretable views of each item. Unlike conventional approaches that rely on a single item representation, Persona4Rec learns to align user profiles with the most plausible item-side persona through a dedicated encoder, efectively transforming user–item relevance into user–persona relevance. At the online stage, this persona-profiled item index al lows fast relevance computation without invoking expensive LLM reasoning. Extensive experiments show that Persona4Rec achieves performance comparable to recent LLM-based rerankers while sub stantially reducing inference time. Moreover, qualitative analysis confirms that persona representations not only drive eficient scor ing but also provide intuitive, review-grounded explanations. These results demonstrate that Persona4Rec ofers a practical and inter pretable solution for next-generation recommender systems.1 ∗Both authors contributed equally to this research. †Corresponding author 1https://github.com/legenduck/PERSONA4REC ![](images/1a360a67f51867b4513ef099939e7827ed1d5018ba89fa0e8a3eb91a61a98fa1.jpg) Figure 1: Comparison between existing LLM-based item rerankers (Upper) and our Persona4Rec (Lower). Persona4Rec shifts LLM reasoning from online inference to ofline persona construction, enabling real-time recommendation via lightweight similarity scoring.

---

## [17/17] Breaking User-Centric Agency: A Tri-Party Framework for Agent-Based Recommendation

**arXiv ID**: 2603.10673  
**摘要长度**: 1423 字符

**Abstract**:
Recent advances in large language models (LLMs) have stimulated growing interest in agent-based recommender systems, enabling language-driven interaction and reasoning for more expressive preference modeling. However, most existing agentic approaches remain predominantly user-centric, treating items as passive enti ties and neglecting the interests of other critical stakeholders. This limitation exacerbates exposure concentration and long-tail under representation, threatening long-term system sustainability. In this work, we identify this fundamental limitation and propose the first Tri-party LLM-agent Recommendation framework (TriRec) that explicitly coordinates user utility, item exposure, and platform-level fairness. The framework employs a two-stage architecture: Stage 1 empowers item agents with personalized self-promotion to improve matching quality and alleviate cold-start barriers, while Stage 2 per forms platform-level sequential multi-objective re-ranking, balanc ing user relevance, item utility, and exposure fairness. Experiments show consistent gains in accuracy, fairness, and item-level utility. Moreover, we find that item self-promotion can simultaneously enhance fairness and efectiveness, challenging the conventional trade-of assumption between relevance and fairness. Our code is available at https://github.com/Marfekey/TriRec. CCS Concepts • Information systems → Recommender systems.

---

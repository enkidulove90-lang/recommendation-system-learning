# Academic Paper Search & Recommendation — Frontier Papers (2025-2026)

> **Target**: 200.0k | **Pool**: 41 papers | **Generated**: 2026-07-27T10:47:02.875011

---

## Contents

1. [full] 2506.07261_延迟异步检索增强召回 — 3.9k
2. [full] 2509.13179_基于BPE令牌级嵌入的冷启动推荐 — 6.6k
3. [full] 2505.05196_RAG推荐系统数据投毒攻击 — 7.2k
4. [full] 2606.09595_多模态电影推荐视觉证据基准 — 8.4k
5. [full] 2512.21526_选择性LLM引导正则化 — 9.8k
6. [full] 2505.20773_冷启动推荐的知识引导检索增强生成 — 9.8k
7. [full] 2511.15141_ItemRAG：基于物品的检索增强生成推荐 — 11.2k
8. [full] 2512.20916_多模态大模型摘要与检索增强序列推荐 — 12.3k
9. [full] 2604.20848 — 12.5k
10. [full] 2607.07108_多模态记忆增强的推荐智能体协作 — 12.8k
11. [full] 2508.00543_长尾推荐再探：LLM弥合流行度差距 — 13.1k
12. [full] 2604.16318_冷启动推荐中LLM重排序诊断 — 13.5k
13. [full] 2606.22151_Novelty-Aware_Agentic_Retrieval_Structured_Multi-Step_ — 13.6k
14. [full] 2605.25007_元模态智能体：缺失模态候选重排序 — 15.2k
15. [full] 2407.18940_LitSearch_A_Retrieval_Benchmark_for_Scientific_Literat — 15.3k
16. [full] 2504.00678_LLM增强的多阶段推荐系统 — 15.4k
17. [full] 2507.15245_SPAR_Scholar_Paper_Retrieval_with_LLM-based_Agents — 16.3k
18. [trunc] 2605.14306_PaSaMaster_Self-Evolving_Agentic_Literature_Retrieval — 17.8k
19. [trunc] 2503.16734_多模态大模型时代的智能体推荐系统 — 18.7k

---


---

# 2506.07261_延迟异步检索增强召回

[2506.07261](https://arxiv.org/abs/2506.07261)

# RADAR: Recall Augmentation through Deferred Asynchronous Retrieval

Amit Jaspal Meta Platforms, Inc. Menlo Park, CA, USA ajaspal@meta.com

Qian Dang Meta Platforms, Inc. Menlo Park, CA, USA qdang@meta.com

Ajantha Ramineni Meta Platforms, Inc. Menlo Park, CA, USA aramineni@meta.com

## ABSTRACT

Modern large-scale recommender systems employ multi-stage ranking funnel (Retrieval, Pre-ranking, Ranking) to balance engagement and computational constraints (latency, CPU). However, the initial retrieval stage, often relying on efficient but less precise methods like K-Nearest Neighbors (KNN), struggles to effectively surface the most engaging items from billion-scale catalogs, particularly distinguishing highly relevant and engaging candidates from merely relevant ones. We introduce Recall Augmentation through Deferred Asynchronous Retrieval (RADAR), a novel framework that leverages asynchronous, offline computation to pre-rank a significantly larger candidate set for users using the full complexity ranking model. These topranked items are stored and utilized as a high-quality retrieval source during online inference, bypassing online retrieval and preranking stages for these candidates. We demonstrate through offline experiments that RADAR significantly boosts recall (2X Recall@200 vs DNN retrieval baseline) by effectively combining a larger retrieved candidate set with a more powerful ranking model. Online A/B tests confirm a +0.8% lift in topline engagement metrics, validating RADAR as a practical and effective method to improve recommendation quality under strict online serving constraints.

## 1 Introduction

Modern video-sharing platforms confront an extreme retrieval challenge: every user session must search through billions of candidate videos to prepare a personalized list within a few milliseconds. Production systems therefore follow a three-stage funnel — retrieval → pre-ranking → ranking — where a very lightweight retriever supplies roughly O(10^3) items, a moderate pre-ranker trims this set to the low hundreds, and an expressive ranker finally orders the shortlist for display. However, this cascaded design imposes hard ceiling on recall because the retriever must satisfy the tightest latency budget, it relies on inexpensive signals (e.g. dot-product two-tower models [1, 2] or K-nearest-neighbour CF indices) and consequently fails to surface many highly engaging items. In fact, in offline simulation studies, we observe single-digit Recall@200 from standard user-to-item and item-to-item retrieval methods (Fig. 1). This results in a retrieval bottleneck that throttles downstream ranking quality.

![](images/e99cfd7920f6b7edf57eed846b150b08feb4dd23df0808e33dfc999a4adee115.jpg)  
Figure 1: Recall@K as a Function of Candidate Retrieved Size (K) from Two Tower based DNN model

Research has therefore explored hybrid offline–online architectures that pre-compute richer candidates when latency is less constrained. These often focus on pre-computing sophisticated retrieval candidates using complex offline models, subsequently relying on lightweight online models for serving [5, 6]. For instance, TwERC [6] augments a real-time lightweight ranker with complementary sources like graph-based neighbors and cached ranker scores, significantly improving coverage. Similarly, other hybrid architectures combine batch-trained models with real-time bandit layers [5] to balance exploration and exploitation. Recent papers also revisit retrieval using acceleratorbacked deep matching models to close the expressiveness gap between retrieval and ranking [7].

While these approaches offer valuable improvements, they still restrict the retrieved candidates to what a server-side model can compute in real time. We observe that significant computational resources are frequently available during off-peak hours. This observation motivates our proposed Recall Augmentation through Deferred Asynchronous Retrieval (RADAR), a novel framework that leverages these off-peak resources to perform computationally expensive final-stage ranking step on a much larger set of candidates (50X) asynchronously, before the user session begins.

To the best of our knowledge, no prior hybrid retrieval system— including TwERC [6]—fully decouples candidate generation from online serving constraints by (i) running the production-grade ranking model offline on a 50X larger set of retrieved candidates and (ii) refreshing each user’s pre-ranked list on a usage-adaptive cadence

## 2 Proposed Approach - RADAR

## 2.1 System Overview

Figure 2 illustrates the RADAR architecture. The online path handles real-time user requests, fetching candidates from standard retrieval sources and the newly introduced RADAR key-value store. Candidates from standard sources pass through pre-ranking, while RADAR candidates bypass it. All candidates are then merged and ranked by the final online ranking model. The offline path runs asynchronously—scheduling, generating and refreshing the RADAR key-value store.

![](images/a15710d1b989d9557813331729cb6f377f9001d74dba5ca184f2005faafc3986.jpg)  
Figure 2: RADAR End-to-End System Architecture

## 2.2 Offline RADAR Pipeline

This pipeline runs periodically to generate high-quality candidates for users

1. Triggering & Scheduling: The pipeline is triggered based on user activity. For instance, active users might have their lists refreshed daily, while less active users might be refreshed weekly or bi-weekly. This usagebased scheduling ensures top K results are updated consistently while managing computational costs. The jobs run on elastic, preemptible compute resources during off-peak hours to minimize operational cost. Note that even with usage-based trigger, scheduling will happen only during off-peak window, hence users keyvalue store results can be stale for few hours in worst case.

2. Large-Scale Candidate Generation: For each targeted user, we perform retrieval using existing, efficient methods (like Two Tower DNN, Content KNN, ItemCF and other rule-based sources) but configure them to retrieve a significantly larger number of candidates (\~ 50X the online output size). This broad set aims to capture a diverse range of potentially relevant items that might be missed by the constrained online retrieval.

3. Offline Ranking: This is the core of RADAR, the retrieved 50X candidates for each user are scored using the exact same complex, feature-rich ranking model used in the final stage of the online funnel. Critically, this allows us to apply our best predictive model to a vastly larger set than feasible online.

4. Storage: The top 200 highest-scoring items, along with their ranking scores, are stored per user in a low-latency key-value store.

Note that the offline RADAR pipeline operates on an opportunistic compute tier during off-peak periods, leading to a minimal net impact on dedicated compute resource allocation.

## 2.3 Online Integration

During online serving, when a user request arrives the system performs the following steps -

1. Parallel Retrieval: Queries the standard online retrieval sources (Two Tower DNN, Content-KNN, Item-CF, rule-based sources) and simultaneously fetches the precomputed top 200 ranked list for the user from the RADAR key-value store.

2. Candidate Processing: Candidates from standard online sources undergo the usual pre-ranking process. Candidates from the RADAR key-value store bypass the pre-ranking stage, as they have already been scored by a superior model.

3. Merging & Final Ranking: Candidates from all sources (post-pre-ranking for standard sources, direct for RADAR) are merged and deduplicated. This combined set is then fed into the final online ranking model for the ultimate re-ordering and selection before being presented to the user.

This integration ensures that high-quality, pre-vetted candidates from RADAR directly compete with candidates from traditional sources in the final ranking stage. RADAR, due to its offline nature and broader candidate evaluation, tends to surface more evergreen items and align with the user's long-term, stable interests. Conversely, traditional online retrieval sources are configured to adapt quickly to short-term user intent shifts and newly ingested items. Thus, RADAR and online sources act as complementary retrieval mechanisms, increasing the overall likelihood of surfacing a balanced mix of highly relevant and engaging content catering to both enduring preferences and immediate interests.

## 3 Offline Experiments

To evaluate the effectiveness of RADAR we conduct offline experiments on a large-scale dataset obtained from users’ engagement on our video platform. We measure retrieval performance by instrumenting the standard recall@200 metric [3] using users’ engagement on videos as ground truth. We compare RADAR against the following retrieval baselines:

1. DNN: a standard two-tower neural model[1] which maps users and items into a latent space combining collaborative filtering and content-based representations for each tower separately.

2. Item-KNN [4]. This is the standard item-based collaborative filtering method

3. Content-KNN: a nearest-neighbor baseline that retrieves items based solely on pretrained content embeddings using cosine similarity

We focus on three main research questions:

1. RQ1: Retrieval Recall Performance – How does RADAR perform on recall@200 compared to the baselines mentioned above?

2. RQ2: Impact of Pool Size, Model Complexity – Are the recall gains of RADAR primarily due to the much larger set of retrieved candidates or due to the stronger model used relative to pre-ranker model?

3. RQ3: Performance Breakdown by User Segments – Does RADAR perform equally well for all user cohorts?

## 3.1 RQ1: Retrieval Recall Performance

RADAR substantially outperforms the traditional retrieval baselines in Recall@200. As shown in Table 1, RADAR achieves about 16.5% recall@200, compared to 8.1% for the DNN Two Tower source and 7.2% for the Item-KNN source. We also observed that many of the items surfaced by RADAR have niche appeal that simple similarity-based methods failed to catch.

Table 1: Offline Recall@200 — RADAR vs. Baselines

<table><tr><td>Retrieval Source</td><td>Recall@200</td></tr><tr><td>DNN</td><td>8.1%</td></tr><tr><td>Item-KNN</td><td>7.2%</td></tr><tr><td>Content-KNN</td><td>5.1%</td></tr><tr><td>RADAR</td><td>16.5%</td></tr></table>

## 3.2 RQ2: Retrieval Scaling vs. Model Scaling

To disentangle why RADAR excels, we ran ablation experiments varying the retrieved candidate pool size and model complexity. Table 2 summarizes the Recall@200 results for different configurations: (A) Base: RADAR configuration, (B) Scaled retrieved candidate pool size with simpler pre-ranker style model [9], (C) Online query candidate pool size with scaled up ranking model, (D) No scaling in candidate retrieved and ranking with simpler pre-ranker style model. Table 2 shows that both model scaling and retrieval scaling help increase RADAR performance, additionally we observe synergy between the two configs which further increase the performance of RADAR when used together.

Table 2: Recall@200 by Retrieval Scaling, Model Scaling

<table><tr><td>Model Scaling</td><td>Retrieval Scaling</td><td>Recall@200</td></tr><tr><td>Yes</td><td>Yes</td><td>16.5%</td></tr><tr><td>No</td><td>Yes</td><td>12.5%</td></tr><tr><td>Yes</td><td>No</td><td>12.1%</td></tr><tr><td>No</td><td>No</td><td>10.2%</td></tr></table>

## 3.3 RQ3: User Performance Breakdown by Cohort

To further evaluate RADAR's performance, we segmented users into three activeness cohorts—Highly Active (daily active sessions), Moderately Active (engaging 2–3 times per week), and Dormant (at most 1 session every few weeks), based on their preceding 30-day interaction logs—and compared RADAR's Recall@200 against the strongest online baseline model (DNN) for each segment.

Table 3 summarizes recall@200 results for different user cohorts. Moderately active users benefit most likely because their usage frequency synchronizes with RADAR refreshes. Highly active users gain less: they exhaust cached lists quickly and their shortterm interests shift faster than RADAR recommendations can be regenerated. No improvements are observed for Dormant users because RADAR cannot infer their interests and the cached list becomes stale, whereas an online DNN call still surfaces timely popular content for them

Table 3: Recall@200 by User Cohort

<table><tr><td>User Cohort</td><td>Recall@200 (RADAR)</td><td>Recall@200 (DNN)</td></tr><tr><td>Highly Active</td><td>16.2%</td><td>8.2%</td></tr><tr><td>Moderately Active</td><td>17.3%</td><td>7.9%</td></tr><tr><td>Dormant</td><td>6.5%</td><td>6.9%</td></tr></table>

## 4 Online Deployment

To validate RADAR in production, we ran a two-week A/B test on our video platform. The control kept the standard multi-stage funnel; the treatment injected the pre-computed top 200 RADAR candidates directly into the final ranker, bypassing online preranking.

A key operational hurdle was candidate overlap, early experiments showed that many RADAR items were already being retrieved online, limiting incremental value. We therefore retuned the online retrieval generators to emphasize immediate, insession users’ intent and freshly uploaded items, letting RADAR specialize in users’ stable long-term interests and evergreen content. After several tuning cycles we achieved \~60% unique candidates from RADAR significantly improving the incremental value.

With this configuration, the treatment delivered a +0.8% lift in our topline user engagement metric (statistically significant and correlated with long-term retention) and a +6% gain in unique item consumption, while keeping latency and system stability unchanged. This successful online validation confirms RADAR's effectiveness in leveraging asynchronous, offline computation to enrich the candidate pool for online ranking, thereby improving overall recommendation quality.

## REFERENCES

[1] Covington, Paul, Jay Adams, and Emre Sargin. 2016. Deep Neural Networks for YouTube Recommendations. In Proceedings of the 10th ACM Conference on Recommender Systems (RecSys ’16). ACM, New York, NY, USA, 191– 198. https://doi.org/10.1145/2959100.2959190.

[2] He, Xiangnan, Lizi Liao, Hanwang Zhang, Liqiang Nie, Xia Hu, and Tat-Seng Chua. 2017. Neural Collaborative Filtering. In Proceedings of the 26th International Conference on World Wide Web (WWW ’17). IW3C2, Geneva, Switzerland, 173–182. https://doi.org/10.1145/3038912.3052569

[3]. Andrzej Pacuk, Piotr Sankowski, Karol Wegrzycki, Adam Witkowski, and Piotr Wygocki. 2016. RecSys Challenge 2016: job recommendations based on preselection of offers and gradient boosting. In Proceedings of the Recommender Systems Challenge 2016 (RecSys Challenge ’16). Association for Computing Machinery, New York, NY, USA, Article 10, 1–4 pages. https://doi.org/10.1145/2987538.2987544

[4] B. Sarwar, G. Karypis, J. Konstan, and J. Riedl. Item-based collaborative filtering recommendation algorithms. In WWW, pages 285–295, 2001.

[5] X. Yi, S.-C. Wang, R. He, H. Chandrasekaran, C. Wu, L. Heldt, L. Hong, M. Chen, and E. H. Chi. 2023. Online Matching: A Real-time Bandit System for Large-scale Recommendations. In Proceedings of the 17th ACM Conference on Recommender Systems (RecSys ’23), Singapore, 403–414. ACM. DOI: 10.1145/3604915.3608792

[6] Vanessa Cai, Pradeep Prabakar, Manuel Serrano Rebuelta, Lucas Rosen, Federico Monti, Katarzyna Janocha, Tomo Lazovich, Jeetu Raj, Yedendra Shrinivasan, Hao Li, and Thomas Markovich. 2023. TwERC: High-Performance Ensembled Candidate Generation for Ads Recommendation at Twitter. In Proceedings of the Workshop on Data Mining for Online Advertising (AdKDD ’23), co-located with the 29th ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD ’23) (Long Beach, CA, USA, 7 August 2023). CEUR-WS.org, Vol. 3556, Article 8, 10 pages. DOI: https://doi.org/10.48550/arXiv.2302.13915.

[7] Jiaqi Zhai, Zhaojie Gong, Yueming Wang, Xiao Sun, Zheng Yan, Fu Li, and Xing Liu. 2023. Revisiting Neural Retrieval on Accelerators. In Proceedings of the 29th ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD ’23), August 6–10, 2023, Long Beach, CA, USA. Association for Computing Machinery, New York, NY, USA, 5520–5531. https://doi.org/10.1145/3580305.3599897

[8] Weiwen Liu, Yunjia Xi, Jiarui Qin, Fei Sun, Bo Chen, Weinan Zhang, Rui Zhang, and Ruiming Tang. Neural re-ranking in multi-stage recommender systems: A review. arXiv preprint arXiv:2202.06602, 2022.

[9] Xiangyang Li, Bo Chen, HuiFeng Guo, Jingjie Li, Chenxu Zhu, Xiang Long, Sujian Li, Yichao Wang, Wei Guo, Longxia Mao, et al. Inttower: the next generation of two-tower model for pre-ranking system. In Proceedings of the 31st ACM International Conference on Information & Knowledge Management, pages 3292–3301, 2022.


---

# 2509.13179_基于BPE令牌级嵌入的冷启动推荐

[2509.13179](https://arxiv.org/abs/2509.13179)

# Efficient Cold-Start Recommendation via BPE Token-Level Embedding Initialization with LLM

Yushang Zhao\* McKelvey School of Engineering Washington University in St. Louis St. Louis, USA \*Corresponding author: yushangzhao@wustl.edu

Qianyi Sun Vanderbilt University Nashville, USA qianyiethan@gmail.com

Xinyue Han College of Engineering, Carnegie Mellon University, Mountain View, USA xinyueh98@gmail.com

Haotian Lyu Viterbi School of Engineering University of Southern California Los Angeles, USA, lyuhaotianresearch@gmail.com

Qian Leng Independent Research Bethesda, USA qianlengdata@gmail.com

Chengrui Zhou Fu Foundation School of Engineering and Applied Science Columbia University New York, NY, USA zhou.chengrui@columbia.edu

Abstract—The cold-start issue is the challenge when we talk about recommender systems, especially in the case when we do not have the past interaction data of new users or new items. Content-based features or hybrid solutions are common as conventional solutions, but they can only work in a sparse metadata environment with shallow patterns. In this paper, the efficient cold-start recommendation strategy is presented, which is based on the sub word-level representations by applying Byte Pair Encoding (BPE) tokenization and pretrained Large Language Model (LLM) embedding in the initialization procedure. We obtain fine-grained token-level vectors that are aligned with the BPE vocabulary as opposed to using coarse-grained sentence embeddings. Together, these token embeddings can be used as dense semantic priors on unseen entities, making immediate recommendation performance possible without user-item interaction history. Our mechanism can be compared to collaborative filtering systems and tested over benchmark datasets with stringent cold-start assumptions. Experimental findings show that the given BPE-LLM method achieves higher Recall@k, NDCG@k, and Hit Rate measurements compared to the standard baseline and displays the same capability of sufficient computational performance. Furthermore, we demonstrate that using subword-aware embeddings yields better generalizability and is more interpretable, especially within a multilingual and sparse input setting. The practical application of token-level semantic initialization as a lightweight, but nevertheless effective extension to modern recommender systems in the zero-shot setting is indicated within this work.

Keywords: Cold-start recommendation, BPE tokenization, Large Language Models, embedding initialization, recommender systems, semantic representation, zero-shot learning

## I. INTRODUCTION

The cold-start issue is a major challenge in the recommenders, in which a recommender cannot access historical interactions between new users or items, which constrains the effectiveness of Collaborative Filtering (CF) models[1]. Traditional hybrid techniques, mixing CF with content-based features, have difficulties in approximating semantic relations with much subtlety, particularly in the face of sparse metadata, or linguistically demanding metadata[2]. Recent Large

Language Models (LLMs) have allowed contextual representation learning based on textual inputs, yet current practice tends to use sentence-level embeddings which mask subword-level semantics which are important in personalization[3].

To alleviate this, we present an approach that utilizes a Byte Pair Encoding (BPE) tokenization step to subword decomposition mechanism and learnt embeddings through a pre-trained LLM. Given a textual input x, we tokenize it into BPE tokens $\{ t 1 , t 2 , \ldots , t n \}$ <sub>.</sub> Each token ti is mapped to an embedding $\mathbf { e i } = \mathrm { L L M } ( t i )$ , and the item or user representation vx is computed as:

$$
v x = (1 / n) * \Sigma e i
$$

This vector vx maps to the cold-start embedding, to calculate recommendation scores by dot product with previously trained entity embeddings. It is architecture-agnostic and can fit directly into any matrix factorization or neural CF pipeline. Wide scale tests using benchmark datasets show that BPEinitialized LLM embeddings provide superior performance of Roaches@K and NDCG@K, particularly against cold-start tight splits[4]. Using this subword-aware initialization, instant personalization is possible without user-item history leading to a lightweight but semantically rich resolution to the coldstart problem[5].

## II. RELATED WORK

The so-called cold-start issue has been a question mark of recommender systems viability, especially in the Collaborative Filtering (CF) domain, since the lack of interaction information defeats latent factor estimation. This was tackled in classical methods through content-based filtering where the item or user metadata, i.e. tags, categories or demographic attributes is typically more static and limited in expressing the required degree of semantic alignment in heterogeneous or changing contexts [6].

This was reduced by hybrid recommender systems which tried to mix content-based systems and CF systems[7]. Approaches like Factorization Machines (FM) and Neural Collaborative Filtering (NCF) used side information and performed it as a part of a latent representation scope. Nevertheless, such approaches are hampered by the use of shallow feature engineering and frequently exhibit the problem of lack of domain generalization, especially in circumstances where metadata is either sparse or similarly noisy[8].

The pretrained language models offered another addition to the semantical representation road. Cold-start item embeddings Initializing cold-start embeddings Since sentence-level embeddings are now available in BERT, RoBERTa, or GPT, some have attempted to initialize items (e.g. news articles, product titles) corresponding to sentences by mapping them to dense vectors[9]. Although largely effective, sentence embeddings have the tendency of flattening linguistic information into a one-dimensional vector, with the risk of overwriting important subword-level details e.g. when dealing with compound entities, rare terms, or words related to a specific domain[10].

Representation learning has found potential in the Byte Pair Encoding (BPE) and other sub word tokenization strategies which were initially created to address the out-of-vocabulary problem in machine translation and language modelling[11]. The construction of token embeddings based on BPE has been observed in newer work in NLP to maintain morphological and semantic granularity. They have however not yet been fully exploited in recommenders especially in cold-start [12].

As opposed to the case of pre-existing work where high level embeddings are averaged, our approach is more token-level initialization oriented. This is driven by the idea of introducing at the subword-level LLM embeddings to recommender systems to offer the gap between the semantic granularity and that of the user-item model. It is a generalization of ideas studied in zero-shots and prompt-based adaptation but in lightweight form that does not imply full fine-tuning. Our work is additive to the existing literature on LLM representations adapted to ranking task since we make LLM representations operational: LLM representations are applied at a token-level and tailored to be optimal in downstream ranking tasks, such as NDCG and Recall[13].

## III. METHODOLOGY

## 3.1 Overview of the Architecture

The given architecture aims at addressing the cold-start problem with the extraction of semantically rich, fine-grained embeddings via Byte Pair Encoding (BPE) alternatives of textual metadata and initialization of these embeddings with the help of a pre-trained Large Language Model (LLM)[14]. Such embeddings are subsequently incorporated into a collaborative filtering backbone to meet top-K recommendation of items.

## 3.2 Model Selection

We employ a transformer-based encoder, specifically a frozen version of DistilBERT or RoBERTa, to avoid computational overhead. Let the BPE tokenizer output a token sequence $T = \{ t 1 , t 2 , \dots , t n \}$ for a given input text $x \in \mathbb { R } ^ { \wedge } d$ . Each token <sub>??</sub> is mapped to an embedding <sub>??</sub> $\in \ \mathbb { R } ^ { \wedge } h$ using: ei = LLM <sub>(??).</sub> The item or user representation <sub>??</sub> is then computed via a mean pooling strategy: $v x = ( 1 / n ) * \Sigma e i$ This representation <sub>??</sub> $\in \ \mathbb { R } ^ { \wedge } h$ becomes the cold-start vector used in downstream recommendation tasks.

## 3.3 Input Data and Preprocessing

Each user or item is associated with a textual field: e.g., product title, description, or user bio. The text is normalized and tokenized using BPE. Formally, let item i have text metadata xi, which is tokenized into a sequence $T i \mathbf { \partial } =$ $\{ t 1 ^ { \wedge } i , t 2 ^ { \wedge } i , \ldots , t n ^ { \wedge } i \}$ , where $t j ^ { \wedge } i \in V _ { - } B P E$ . This sequence is passed into the LLM to extract a contextual representation.

## 3.4 LLM-Based Feature Extraction

To preserve linguistic context, each token $\mathrm { t j } ^ { \wedge _ { \mathrm { i } } }$ is passed through the LLM encoder to obtain its contextual embedding $e j ^ { \wedge } i .$ The aggregated representation is computed using: $v i =$ Aggregate $( \{ e 1 ^ { \land } i , e 2 ^ { \land } i , \dots , e n ^ { \land } i \} )$ <sub>.</sub> We also experiment with attention-weighted aggregation where token relevance is learned via a self-attention layer.

## 3.5 Cold-Start Recommendation Layer

In cold-start mode, no historical interactions exist. Thus, predictions are made using cosine similarity or dot product between the user vector <sub>??</sub> and the candidate item vector ??: $\hat { r } _ { - } u i = v u ^ { T } v i$ . In pairwise training (e.g., BPR loss), we use a sampled negative item i⁻ to optimize: $L _ { - } B P R = -$ ??? $\sigma ( \hat { r } _ { - } u i ^ { + } - \hat { r } _ { - } u i )$

## 3.6 Ethical and Fairness Considerations

Although LLMs can be used so as to achieve semantic richness, they only end up repeating bias present in the corpora that it has been trained on. To deal with this possible issue we resort to post-embedding L2 normalization and later measure fairness in terms of exposure disparity and representation bias.

## IV. EXPERIMENTS AND EVALUATION

## 4.1 Experimental Setup

In order to comprehensively test our strategy, we experiment on two benchmark datasets: MovieLens 1M and Amazon Books, that are commonly used in the research on recommender systems. To model the cold-start objective, we exclude the sets of users and items that have interacted before, and generate evaluation sets of users and items which have never been seen before[15].

Along with collaborative filtering and sentence-based embedding baselines, it is important to include more formal cold-start baselines. Comparative baselines should be provided, e.g., with models based on graph embedding (e.g., GraphSAGE, LightGCN) or meta-learning (e.g., MeLU, MAML-based cold-start recommenders) or using attribute expansion. Their addition would enable us to evaluate the robustness of BPE-LLM embeddings at various levels of sparsity and a heterogeneous metadata structure[16]. As an example, graph-based models utilize the topology of the useritem interaction, whereas meta-learning methods can rapidly learn to represent previously unseen users/items with few examples. Attribute-expansion techniques exploit additional attributes, e.g., demographics or item attributes, to circumvent sparsity [17].

The metadata includes title and genre of the movies when Textual metadata is used in MovieLens and in Amazon products it includes titles and category[18]. Any text is preprocessed (by lowercase normalization, removing punctuation marks, and Byte Pair Encoding (BPE) in a 30,000-token vocabulary). Pre-trained DistilBERT-base is performed on the extraction of embeddings, and unless specified, attentionweighted pooling over the embeddings is employed[19].

The following are the models that we compare:

1.Random Initialization- normal matrix factorization lacking metadata.

2.Sentence Embedding - metadata encoded through distilbertsentence-vector mean-pooling.

3.BPE + LLM (Ours) -aggregation of token level embeddings at a fine-grained level.

All models are written in PyTorch and Adam is used as the optimization with BPR loss during 50 epochs. Our training and evaluation are done using 90/10 and we use cold start on the test data.

## 4.2 Evaluation Metrics

We assess performance using standard top-K ranking metrics: •Recall@K: percent of relevant items in top-K list.

•NDCG@K: relevance score that is position-aware and is normalized with respect to ideal ranking.

•Hit Rate@K: does at least one relevant element go into the top-K.

Each metric is calculated at K=10K = 10K=10 in 5 trials to reach the stability of statistics.

## 4.3 Results

To give a more complete analysis, the findings are generalized to cover other cold-start baselines, i.e., graph-embedding methods, meta-learning systems, and attribute-expansion algorithms[20]. Our BPE-LLM approach is compared with theirs in Table 1 on the standard metrics Recall@10, NDCG@10, and Hit Rate@10. The findings indicated that though graph-embedding and attribute-based solutions have focused on intermediate levels of sparsity negatively in terms of performance, they decline sharply when beyond sparsity levels of 30-40 percent. In sharp comparison, the proposed BPE-LLM initialization shows a stable performance under various regimes of sparsity (10%, 30%, 50% observed interactions), thus its robustness in extreme cold-starts. This tiered analysis furnishes the empirical results that subwordlevel initialization presents better generalization performance than structure-aware and an attribute-based baseline[21].

Table 1: Performance Comparison Across Methods on Retrieval Metrics

<table><tr><td>Method</td><td>Recall@10</td><td>NDCG@10</td><td>Hit Rate@10</td></tr><tr><td>Random Init</td><td>0.41</td><td>0.32</td><td>0.45</td></tr><tr><td>Sentence Embedding</td><td>0.56</td><td>0.48</td><td>0.59</td></tr><tr><td>BPE + LLM (Ours)</td><td>0.68</td><td>0.62</td><td>0.71</td></tr></table>

As it is indicated in the table, we greatly outperform all the baselines, especially in terms of Recall and NDCG. This proves the usefulness of subword level embeddings in relation to acquisition of semantically subtle characteristics that facilitates generalization when conditions transcend to zeroshot environments[22].

## 4.4 Visualization and Interpretability

![](images/e0ced6cf29ede73b65c1d071f365228e307486bdc45dab511d191977d23c22f8.jpg)  
Figure 1: Cold-Start Recommendations

An illustration of the performance improvements of models is provided in Figure 1 (above). We put t-SNE projection of learned embeddings to the test, too, and discover that we can more easily cluster semantically similar items in BPE-LLM representation space, including cold-start entities.

## V. RESULTS AND DISCUSSION

## 5.1 Semantic Understanding Beyond Keywords

The main advantage of the BPE + LLM model, in turn, is the possibility to represent the semantics at the subword level. As an example, the items, such as wireless gaming headset and bluetooth VR audio gear, have a low lexical overlap between description, but the tokens, such as wireless, audio, and gear, would give overlapping tokens embedding. This granularity makes the model generalizable across the items with little or abstract metadata, a critical property in cold-start situations[23].

Although the effectiveness of the subword-level embeddings is well-proven with the help of the empirical analysis, a more precise theoretical support is needed. In the language modeling view, subword decomposition can result in a lower likelihood of occurring out-of-vocabulary (OOV) tokens and better generalization over sparse domains. Based on Zipfian distributions in natural language, word frequency is characterized by a heavy-tailed distribution with frequent occurrence of rare words. BPE segmentation guarantees decomposing infrequent words to create more frequent subunits, generating embeddings that only stay meaningful even in the very sparse case [24].

Further, subword-level representations are morphologically compositional (i.e., maintaining solidity of the word, such as wireless in wire and less), whereas sentence-level representations flatten these hierarchies. This makes this more granular and more transferable to multilingual or domainspecific cold-start settings[25]. The theoretical argumentation therefore, conforms to concepts of distributional semantics and frequency normalisation that explain why BPE-LLM initialization is stronger than sentence-level encoders during a cold-start case[26].

In contrast to the sentence-level embeddings where whole inputs are collapsed to a sole vector, our BPE-token aggregation does not cross out morphological data[27]. This came in handy especially in multilingual cases where it was still possible to match compound words or transliterated tokens based on semantic which is because LLM was trained on multilingual corpora[28].

## 5.2 Performance Evaluation

Our model outperforms approximations with random initialization and sentence-level baselines across all the metrics of evaluation. With the MovieLens dataset, Recall@10 was more than 27 percent better than sentence embeddings. The growth of NDCG@10 also shows that model ranks relevant objects higher, which is one of the crucial elements of user engagement in production systems[29]. The attention-based aggregation also played its role in this increase, as well, where some of the tokens would overpower the semantic content (e.g., limited edition or collector series). These results confirm the hypothesis that the subword-level representations proved more expressive in the cold-start modelling of the entities[30].

## 5.3 Generalizability and Scalability

One of the major strengths of the suggested approach is its generality. Since BPE and transformer encoders are domainagnostic, one can use the same pipeline across categories; books, movies, games without even retraining the encoder.

![](images/b2f1743ece0b8e69338c2764ca0a637e240f4e9f045896fda9dd46067b3fc0d9.jpg)  
Figure 2: t-SNE projection of Cold-start Items  
Figure 2 (above) shows this in a 2D t-SNE projection, where clusters of cold-start items from different domains form as a result of their BPE-LLM embeddings.

The model is also scalable: as LLM is frozen during inference, then embedding computation its one-time operation per item or per user. This makes deployment in low-latency real-time recommendation pipelines possible[31].

## 5.4 Practical Implications

The framework is applicable as a recommendation engine when the emphasis is on cold-start coverage dynamics of a product launch in e-commerce or new user on-boarding during the media phone app. It is also plug-and-play compatible with other existing collaborative filtering pipelines, or with more recent retrieval-based recommenders[32].

Although the increased use of subword-level representations has definite benefits, the possible limitations cannot be ignored[33]. One effect is that learning to overfit on the highfrequency subwords can distort representations to favor generic semantics at the expense of distinctiveness on rare items. Second, interpretability may be diminished in certain areas by linguistic ambiguity at the grammatical morpheme (e.g. the common morpheme across words with semantic differences) level. Third, even in very sparse cold-start settings or unlabeled situations, BPE decomposition can still not bridge enough semantic prior knowledge, especially with little textual metadata or when domain-specific jargon is not found within underlying LLM pretraining corpus[34].

These drawbacks imply boundary conditions where hybrid strategies e.g. subword-level with additional sentence/contextual embeddings can be more promising. A curative limitation analysis will allow narrowing down the scope of BPE-LLM initialization applicability and dwell upon the existing gaps which will subsequently be focused on during research.

## VI. CONCLUSION AND FUTURE WORK

The proposed study presented an effective and innovative approach to cold-start recommendation based on the initialization of Byte-Pair Encoding (BPE) token-level embedding with the help of large language models (LLMs). The approach is particularly effective in filling the gap that the traditional user-item collaborative filtering approach has in sparse user-item interaction data since it introduces substantial contextualization through the transformer-based approach to subword tokens and their combinations. The approach showed impressive results when tested in a coldstart environment on heterogeneous tasks like books, movies, and games. Empirical evidence proved the higher performance of BPE-LLM in the top-N recommendation task as Recall@10 and NDCG@10 in comparison with sentencelevel and randomly initialized baselines. In addition to that, t-SNE visualization demonstrated semantic clustering, confirming the fidelity and generalizability of the learned embedding space. Importantly, the model is efficient to scale, with embedding inference taking only forward passes of a frozen LLM encoder, which makes it suitable to deploy at scale in modern recommender systems.

## FUTURE WORK

There are several possible directions, which could be viewed as the fruitful extensions of this study. On the first point, our approach used static BPE aggregation; we could in the future differentiate fine-tuned LLMs (e.g., with lightweight adapters; e.g., LoRA or BitFit) to more tailor the embedding space in a global manner, without access to large-scale finetuning. Second, global and local semantics points of view might be crossed by introducing hybrid token-sentence attention frameworks that potentially improve downstream task performance. In this instance it would also be practicable upon such AU form as dialogue-based recommender systems, where context/history plays a larger role. Third, it will be exciting to identify the option of considering the addition of the contextual user aspects (the recent searches, the platform activity or the time trends), along with the token representations, to enrich the user-item relationships at the initial phases of the onboarding procedure. And finally, new experiments over multilingual datasets, practise-dependent cold-start tasks (e.g., clinical recommendations, financial products), and reinforcement-based ranks of ranking will help achieve a deeper understanding of the scope and practical value of the framework when facing such a large global user demography.

## REFERENCES

[1] Lin X, Cheng Z, Yun L, et al. Enhanced Recommendation Combining Collaborative Filtering and Large Language Models[J]. arXiv preprint arXiv:2412.18713, 2024.

[2] Niu, Tianyue, et al. "Decoding student cognitive abilities: a comparative study of explainable AI algorithms in educational data mining." Scientific Reports 15.1 (2025): 26862.

[3] Zheng Z, Liu K, Zhu X. Machine Learning-Based Prediction of Metal-Organic Framework Materials: A Comparative Analysis of Multiple Models[J]. arXiv preprint arXiv:2507.04493, 2025.

[4] Leong H, Gao Y, Ji S, et al. Efficient fine-tuning of large language models for automated medical documentation[C]//2024 4th International Conference on Digital Society and Intelligent Systems (DSInS). IEEE, 2024: 204-209.

[5] Yuan T, Zhang X, Chen X. Machine Learning based Enterprise Financial Audit Framework and High Risk Identification[J]. arXiv preprint arXiv:2507.06266, 2025.

[6] Li, K., Liu, L., Chen, J., Yu, D., Zhou, X., Li, M., ... & Li, Z. (2024, November). Research on reinforcement learning based warehouse robot navigation algorithm in complex warehouse layout. In 2024 6th International Conference on Artificial Intelligence and Computer Applications (ICAICA) (pp. 296-301). IEEE.

[7] Yu, D., Liu, L., Wu, S., Li, K., Wang, C., Xie, J., ... & Ji, R. (2025, March). Machine learning optimizes the efficiency of picking and packing in automated warehouse robot systems. In 2025 IEEE International Conference on Electronics, Energy Systems and Power Engineering (EESPE) (pp. 1325-1332). IEEE.

[8] Li J, Zhou Y. Bideeplab: An improved lightweight multi-scale feature fusion deeplab algorithm for facial recognition on mobile devices[J]. Computer Simulation in Application, 2025, 3(1): 57-65.

[9] Yang, Zhongheng, et al. "RLHF Fine-Tuning of LLMs for Alignment with Implicit User Feedback in Conversational Recommenders." arXiv preprint arXiv:2508.05289 (2025).

[10] Zhu R, Wang Y, Jiang T, et al. Self-Improving Model Steering[J]. arXiv preprint arXiv:2507.08967, 2025.

[11] Lyu, Haotian, et al. "Self-Supervised User Embedding Alignment for Cross-Domain Recommendations via Multi-LLM Co-Training." Authorea Preprints (2025).

[12] Zhao Y, Lyu H, Peng Y, et al. Research on Low-Latency Inference and Training Efficiency Optimization for Graph Neural Network and Large Language Model-Based Recommendation Systems[J]. arXiv preprint arXiv:2507.01035, 2025.

[13] Chen, Y., Du, H., & Zhou, Y. (2025). Lightweight Network-Based Semantic Segmentation for UAVs and Its RISC-V Implementation. Preprints.https://doi.org/10.20944/preprints202508.1108.v1

[14] Xiang, A., Qi, Z., Wang, H., Yang, Q., & Ma, D. (2024, August). A multimodal fusion network for student emotion recognition based on transformer and tensor product. In 2024 IEEE 2nd International Conference on Sensors, Electronics and Computer Engineering (ICSECE) (pp. 1-4). IEEE.

[15] Ding Y, Wu Y, Ding Z. An automatic patent literature retrieval system based on LLM-RAG[J]. arXiv preprint arXiv:2508.14064, 2025.

[16] Ning Z, Zeng H, Tian Z. Research on data-driven energy efficiency optimisation algorithm for air compressors[C]//Third International Conference on Advanced Materials and Equipment Manufacturing (AMEM 2024). SPIE, 2025, 13691: 1068-1075.

[17] Jiang T, Wang Z, Liang J, et al. Robustkv: Defending large language models against jailbreak attacks via kv eviction[J]. arXiv preprint arXiv:2410.19937, 2024.

[18] Ou, Y. "Dynamic Allocation Mechanism of Cloud Computing Resources Driven by Neural Network." Frontiers in Computing and Intelligent Systems (2023).

[19] Wang J, Zhang Z, He Y, et al. Enhancing Code LLMs with Reinforcement Learning in Code Generation[J]. arXiv preprint arXiv:2412.20367, 2024.

[20] Wang, Jingru, Wen Ding, and Xiaotong Zhu. "Financial analysis: Intelligent financial data analysis system based on llm-rag." arXiv preprint arXiv:2504.06279 (2025).

[21] Li Y, Yao Y, Lin J, et al. A Deep Learning Algorithm Based on CNN-LSTM Framework for Predicting Cancer Drug Sales Volume[J]. arXiv preprint arXiv:2506.21927, 2025.

[22] Wu, S., Fu, L., Chang, R., Wei, Y., Zhang, Y., Wang, Z., ... & Li, K. (2025). Warehouse Robot Task Scheduling Based on Reinforcement Learning to Maximize Operational Efficiency. Authorea Preprints.

[23] He, Y., Wang, J., Li, K., Wang, Y., Sun, L., Yin, J., ... & Wang, X. (2025). Enhancing Intent Understanding for Ambiguous Prompts through Human-Machine Co-Adaptation. arXiv preprint arXiv:2501.15167.

[24] Yang, Haowei, et al. "Research on Model Parallelism and Data Parallelism Optimization Methods in Large Language Model-Based Recommendation Systems." arXiv preprint arXiv:2506.17551 (2025).

[25] Huang, Sining, et al. "Ar overlay: Training image pose estimation on curved surface in a synthetic way." arXiv preprint arXiv:2409.14577 (2024).

[26] Zhang, Juyuan, et al. "Time-LlaMA: Adapting Large Language Models for Time Series Modeling via Dynamic Low-rank Adaptation." Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 4: Student Research Workshop). 2025.

[27] Leong H Y, Wu Y. Why Should Next-Gen LLM Multi-Agent Systems Move Beyond Fixed Architectures to Dynamic, Input-Driven Graphs?[J]. Input-Driven Graphs, 2025.

[28] Wang Y, Zhu R, Wang T. Self-Destructive Language Model[J]. arXiv preprint arXiv:2505.12186, 2025.

[29] Xiang, A., Zhang, J., Yang, Q., Wang, L., & Cheng, Y. (2024). Research on splicing image detection algorithms based on natural image statistical characteristics. arXiv preprint arXiv:2404.16296.

[30] Yang H, Fu L, Lu Q, et al. Research on the Design of a Short Video Recommendation System Based on Multimodal Information and Differential Privacy[J]. arXiv preprint arXiv:2504.08751, 2025.

[31] Zhao, Yushang, et al. "Meta-Learning for Cold-Start Personalization in Prompt-Tuned LLMs." arXiv preprint arXiv:2507.16672 (2025).

[32] Yang, Haowei, et al. "LLM-Augmented Symptom Analysis for Cardiovascular Disease Risk Prediction: A Clinical NLP." arXiv preprint arXiv:2507.11052 (2025).

[33] Shao, Junli, et al. "Deep Learning Model Acceleration and Optimization Strategies for Real-Time Recommendation Systems." arXiv preprint arXiv:2506.11421 (2025).

[34] Liang Z, Wei W, Zhang K, et al. Research on Multi-hop Inference Optimization of LLM Based on MQUAKE Framework[J]. arXiv preprint arXiv:2509.04770, 2025.


---

# 2505.05196_RAG推荐系统数据投毒攻击

[2505.05196](https://arxiv.org/abs/2505.05196)

# Stealthy LLM-Driven Data Poisoning Atacks Against Embedding-Based Retrieval-Augmented Recommender Systems

Fatemeh Nazary fatemeh.nazary@poliba.it Polytechnic University of Bari Bari, Italy

Tommaso di Noia tommaso.dinoia@poliba.it Polytechnic University of Bari Bari, Italy

Yashar Deldjoo yashar.Deldjoo@poliba.it Polytechnic University of Bari Bari, Italy

Eugenio di Sciascio eugenio.disciascio@poliba.it Polytechnic University of Bari Bari, Italy

## Abstract

We present a systematic study of <sub>provider-side</sub> data poisoning in retrieval-augmented recommender systems (RAG-based). By modi fying only a small fraction of tokens within item descriptions—for instance, adding emotional keywords or borrowing phrases from semantically related items—an attacker can significantly promote or demote targeted items. We formalize these attacks under token-edit and semantic-similarity constraints, and we examine their efective ness in both <sub>promotion</sub> (long-tail items) and <sub>demotion</sub> (short-head items) scenarios. Our experiments on MovieLens, using two large language model (LLM) retrieval modules, show that even subtle attacks shift final rankings and item exposures while eluding naive detection. The results underscore the vulnerability of RAG-based pipelines to small-scale metadata rewrites, and emphasize the need for robust textual consistency checks and provenance tracking to thwart stealthy provider-side poisoning.

## Keywords

Retrieval-Augmented Generation, Recommender Systems, Data Poisoning, Large Language Models, Adversarial Text Attacks

## ACM Reference Format:

Fatemeh Nazary, Yashar Deldjoo, Tommaso di Noia, and Eugenio di Sciascio. 2025. Stealthy LLM-Driven Data Poisoning Attacks Against Embedding Based Retrieval-Augmented Recommender Systems. In <sub>Adjunct</sub> <sub>Proceedings</sub> of the 33rd ACM Conference on User Modeling, Adaptation and Personalization (UMAP Adjunct ’25), June 16–19, 2025, New York City, NY, USA. <sup>ACM,</sup> <sup>New</sup> York, NY, USA, 5 pages. https://doi.org/10.1145/3708319.3733675

## 1 Introduction

Retrieval-augmented generation (RAG) enhances large language models (LLMs) by grounding their outputs in external data sources, such as item reviews or user tags, rather than relying solely on internal parameters [2, 3, 6]. This grounding improves recency and factual accuracy. In fact, industry reports estimate that over 60% of LLM-powered search and recommendation systems now use RAG [6, 8]. A common RAG-based recommender architecture (Figure 1) retrieves candidate items from an external knowledge store (e.g., a database or corpus of item descriptions) and then uses an LLM to synthesize the retrieved text into final recommendations. While classical methods such as collaborative filtering (CF) can provide a base in the retrieval stage by analyzing user-item interactions, <sub>embedding-based</sub> <sub>retrieval</sub> has emerged as a particularly powerful approach in RAG pipelines. Embedding models such as BERT-like encoders or Sentence Transformers can capture an item semantic representation and dynamically decide when to retrieve additional context. By leveraging these embeddings, a recommender system can handle <sub>new</sub> or <sub>infrequently</sub> discussed items, which often appear in long-tail domains. At the same time, these embedding-based retrieval methods ofer clear advantages: they provide stronger factual grounding and can adapt to realtime changes in external data. For example, if an item has recently won an award, the RAG pipeline can incorporate that information into the recommendations without retraining the entire model. Notwithstanding their great potential, as more RAG variants adopt embedding-driven approaches, they lean heavily on textual cues, which can open the door to attacks at the data or metadata level. For example, an attacker can subtly <sub>inject</sub> changes into item descriptions (e.g. emotional phrases, negative triggers) to manipulate how both retrieval and generation perceive an item. Unlike classic poisoning that directly tampers with user ratings, <sub>text-based</sub> attacks may remain undetected if they preserve the original semantics.

<sub>Related</sub> <sub>Work</sub> <sub>and</sub> <sub>Gaps.</sub> LLM vulnerabilities to prompt injection and adversarial prompts have been well documented [1, 7, 10, 11], however, these studies focus on standalone models rather than recommendation pipelines. In the recommender domain, early poisoning attacks manipulated user ratings or profiles to distort collaborative filtering outputs [5]. More recently, RAG–specific threats emerged: BadRAG [12] and PoisonedRAG [13] inject malicious snippets into knowledge bases to warp retrieval or LLM responses. Tag-based poisoning for RAG recommenders was explored in [8], showing that modified user tags can bias item ranking. However, full metadata, such as item descriptions and reviews, remains underexamined. Furthermore, prior methods often rely on simple keyword insertion, which can be detected by basic semantic or stylistic filters. In contrast, we leverage modern LLM rewriting techniques to design coherent, low-budget alterations that better evade detection [4].

![](images/310d37aac0ea04690ee6aaad638fb914793e20ecaf905b70f4ea3c74d7377ae6.jpg)  
Figure 1: High-level RAG architecture in a recommender setting. A retriever selects candidate items (step 1). An LLM uses thes retrieved texts and user queries to re-rank or generate final recommendations (step 2). In our poisoning scenario (red arrow), an attacker subtly modifies item descriptions to alter how retrieval and generation perceive items.

<sub>Goals</sub> <sub>and</sub> <sub>Contributions</sub> Our primary objective is to formally investigate <sub>provider-side</sub> data poisoning attacks on retrieval-augmented recommenders, focusing on two scenarios: <sub>promotion</sub> (boosting long-tail items) and <sub>demotion</sub> (penalizing highly popular items). In doing so, we introduce the notion of “textual stealthiness,” measured through semantic similarity (e.g., SBERT-based) along with overall system-level metrics, to quantify how much an attack can subtly rewrite an item’s description while still achieving malicious ranking shifts. Our main contributions include:

<sub>•</sub> We present a formal definition of provider-side textual rewriting attacks in RAG-based recommendation, framed around two adversarial goals (<sub>promote</sub> vs. <sub>demote</sub>).

<sub>•</sub> We use a measurement of “stealthiness” by examining how sentence-level semantics change (via SBERT) alongside the overall impact on RS accuracy;

<sub>•</sub> We design and implement <sub>three</sub> distinct attack variations: (i) <sub>Emotional</sub> edits, (ii) <sub>Neighbor-based</sub> borrowing, and (iii) <sub>Chained</sub> rewriting (combining both), all under the same edit-budget constraints.

<sub>•</sub> We empirically evaluate these methods across <sub>two</sub> <sub>diferent</sub> <sub>SoA</sub> <sub>LLMs</sub> on the of the MovieLens latest dataset, and demon strate the potency of small-scale textual manipulations on altering the exposure of carefully selected target items;

<sub>•</sub> We plan to release both <sub>code</sub> and <sub>data</sub> resources to foster reproducibility and future research in adversarial robustness for RAG-based recommender systems.

## 2 Formal Description of LLM-Driven Data Poisoning Attacks

The overarching goal of the attacker is to manipulate item visibil ity within the recommendation pipeline by rewriting the textual descriptions of items. Concretely, we select a subset of items from both the long-tail (unpopular) and short-head (popular) segments, aiming to <sub>promote</sub> the former (i.e., increase their exposure) or <sub>de-</sub> <sub>mote</sub> the latter $( { \mathrm { i . e . } }$ , decrease their visibility). Formally, for each targeted item $i \in I _ { \mathrm { p o i s o n } }$ with original description $D _ { i } ,$ we produce a new description $\widetilde { D } _ { i }$ such that (1) the token-level change is bounded by ?? (e.g., 10% of $| D _ { i } |$ tokens may be altered), and (2) the rewritten text maintains a suficiently high semantic similarity (e.g., SBERT score above 0.80) to remain stealthy. The attacker’s optimization objective is then to maximize (in the promote case) or minimize (in the demote case) each item’s final ranking position or exposure in top-?? recommendations after the system retrains on $\widetilde { D } _ { i }$ :

$$
\begin{array}{c} \max _ {\{\widetilde {D} _ {i} \}} \sum_ {i \in I _ {\text {poison}}} \Delta \bigl (\text {Exposure} (i) \bigr) \\ \text {subject to} \quad H \bigl (D _ {i}, \widetilde {D} _ {i} \bigr) \leq \delta | D _ {i} |, \\ \text {Sim} \bigl (D _ {i}, \widetilde {D} _ {i} \bigr) \geq \sigma_ {\min}. \end{array}\tag{1}
$$

Here, $\Delta ( . )$ denotes the change in ranking of item ?? within the ranking list (either at the retrieval level with top-?? or the final recommendation level with top-??). In our experiment, we set $N = 5 0$ and $K = 2 0$ . The function $H ( \cdot )$ represents a distance metric, where ?? introduces the notion of <sub>stealthiness</sub>, ensuring that modifications remain subtle yet efective. We specifically instruct the LLM to modify 10% of the tokens (token-level distance) while measuring the change at both the <sub>token</sub> <sub>level</sub>, and the <sub>semantic</sub> <sub>level</sub> using Sentence-BERT (SBERT)[9]. In our framework, we designed 3 types of attacks:

<sub>• Emotional</sub> <sub>Attack:</sub> We prompt the LLM to analyze what textual cues make a movie appear “more popular” or “less popular,” given its original description. The LLM then modifies up to 10% of the text, injecting emotive or sentimentladen words $( \mathrm { e . g . }$ , “exhilarating,” “lackluster”) to steer the item toward promotion or demotion.

• Neighbor Borrowing: <sup>We</sup> <sup>identify</sup> <sup>a</sup> <sup>set</sup> <sup>of ??</sup> neighbor <sup>items</sup> from the opposite popularity segment (i.e., from popular to help promote, or from unpopular to help demote). The LLM then weaves phrases from these neighbors into the target’s description, aiming to transfer either highly positive or negative connotations. In our experiments, ?? <sub>=</sub> 5.

<sub>•</sub> <sub>Chain</sub> <sub>Attack:</sub> This approach combines both emotional triggers and neighbor-based snippets in a single pass. While often more powerful, the resulting text can become more visibly altered relative to the original description.

## Example of Metadata Attack:

## Original Description:

“Wings of Hope lifts spirits in trying times. Courage takes flight.”

## Emotional Attack (Promote):

“Wings of Hope <sub>soars</sub> to lift spirits in trying times, where <sup>courage</sup> <sup>takes</sup> exhilarating <sup>flight.</sup> Uplifting Impact: Embrace the strength within to rise above challenges.<sup>”</sup>

## Neighbor Borrowing (Promote):

“Wings of Hope lifts spirits in trying times. <sub>Experience</sub> <sub>how</sub> Cyber Love blends technology with passion, creating a harmonious blend of optimism and connection. <sup>Courage</sup> <sup>takes</sup> <sup>flight.”</sup>

## Chain Attack:

Merges emotive language (e.g., “exhilarating,” “uplifting”) <sub>and</sub> references to similar “popular” neighbors to maximize the embedding shift, e.g.: “Wings of Hope <sub>exhilaratingly</sub> showcases <sup>resilience</sup> (inspired by Cyber Love’s uplifting themes) <sup>to</sup> <sup>soar</sup> <sup>be-</sup> yond challenges.”

## 3 Experimental Setup

We conduct our experiments on top of a retrieval-augmented recommendation (RAG) pipeline that integrates a Large Language Model (LLM) from OpenAI and a Sentence Transformer (ST) encoder for embedding-based retrieval. Specifically, the pipeline first employs the Sentence Transformer to select candidate items based on the semantic closeness of item descriptions, and then an OpenAI-based LLM re-ranks these candidates or generates final textual recommendations.

Although we report results primarily on the widely used Movie Lens “ml-latest-small” dataset in this paper, we have also evaluated the proposed methods on additional benchmark datasets; due to space limitations, we present here only the detailed findings for the MovieLens dataset.

Within the MovieLens corpus, we categorize items into <sub>long-tail</sub> (unpopular) vs. <sub>short-head</sub> (popular) segments, inject adversarial textual edits, and assess the resulting changes in item ranks and system-level metrics (e.g., Recall@??, nDCG@??). Our system rein dexes or retrains on these modified descriptions, thereby simulating real-world scenarios where metadata updates could inadvertently (or maliciously) be incorporated into a live recommender. We build the user profile for the retrieval stage in two ways: (1) <sub>Manual</sub> construction using a structured template; and (2) <sub>LLM-based</sub> summarization that generates a user’s preferences automatically. In Table 1 <sub>(Tab</sub> <sub>2</sub> <sub>and</sub> <sub>3),</sub> we diferentiate these two methods when evaluating final recommendations. All remaining steps in our pipeline (retrieval and re-ranking) remain unchanged.

## 4 Results and Discussion

We now present our key experimental findings, structured around these three main research questions (RQs).

<sub>RQ1:</sub> Are LLM-based textual attacks efective at pushing a target item ranking up or down (both at retrieval top-?? and recommendation stage top-??)?

<sub>RQ2:</sub> Does attack eficacy vary across LLMs model e.g., OpenAI vs. Sentence Transformer retrieval?

<sub>RQ3:</sub> How do these modifications afect overall recall or nDCG? Can poisoning degrade system-wide performance?

## RQ1: Efectiveness of LLM-Based Textual Attacks

Table 1 (top half) presents results for the <sub>promotion</sub> scenario. The bold “Original” rows provide baseline ranks against which each attack variant (Emotional, Neighborhood, Chain) can be compared. A successful promotion reduces the rank value, indicating an item is placed closer to the top of recommended lists. In several cases, Chain rewriting reduces ranks from approximately 7.0 to around 4.7, whereas Emotional and Neighbor approaches achieve more moderate improvements. These findings validate that even a modest injection of sentiment-laden descriptors or borrowed phrases significantly influences item visibility.

Turning to the <sub>demotion</sub> scenario (Table 1 bottom half), the goal is to push popular items into lower positions (hence, a successful attack increases rank). Chain-based edits again elicit the largest rank changes, demonstrating the capacity of compound strategies—merging emotional cues with neighbor-based snippets—to degrade targeted items more substantially. Thus, we conclude that small-scale textual rewrites are demonstrably efective in shifting final recommendations.

## RQ2: Comparison of OpenAI vs. Sentence Transformer Retrieval

An additional observation arises when contrasting the OpenAI columns with the Sentence Transformer (ST) columns. The OpenAIbased pipeline exhibits increased sensitivity to the introduced textual modifications. For instance, in the <sub>promotion</sub> scenario, a change from a rank of 7.0 to approximately 4.7 is relatively large, whereas the corresponding ST scenario occasionally reverses the direction of movement or produces more modest variation. These disparities highlight how generative re-ranking can amplify subtle language cues or signals introduced by adversarial text rewriting. Moreover, the propensity of OpenAI to rely on nuanced phrasing suggests that even brief “trigger” terms can be disproportionately influential, especially compared to a more static embedding architecture.

Table 1: Side-by-side comparison of Promotion (top) and Demotion (bottom) scenarios for a temporal pipeline. Each scenario lists (A) Retrieval (temporal), (B) Recommendation (LLM-based profile), and (C) Recommendation (Manual profile). Columns show OpenAI vs. Sentence Transformer (ST), with Ranking of attacked items (lower = stronger promotion). Bold is the base (no attack), cyan highlights best results, yellow highlights good results.

<table><tr><td rowspan="2" colspan="2">Scenario / Pipeline</td><td colspan="3">OpenAI</td><td colspan="3">ST</td></tr><tr><td>Rank</td><td>Recall</td><td>nDCG</td><td>Rank</td><td>Recall</td><td>nDCG</td></tr><tr><td colspan="8">Promotion Scenario</td></tr><tr><td rowspan="4">(A) Retrieval</td><td>Original</td><td>31.53</td><td>0.1504</td><td>0.2101</td><td>21.01</td><td>0.1205</td><td>0.1615</td></tr><tr><td>Emotional</td><td>28.65</td><td>0.1289</td><td>0.1920</td><td>33.00</td><td>0.1191</td><td>0.1752</td></tr><tr><td>Neighborhood</td><td>28.54</td><td>0.1486</td><td>0.2047</td><td>29.23</td><td>0.1196</td><td>0.1698</td></tr><tr><td>Chain</td><td>25.16</td><td>0.1367</td><td>0.1968</td><td>32.16</td><td>0.1241</td><td>0.1669</td></tr><tr><td rowspan="4">(B) Rec. (LLM)</td><td>Original</td><td>7.00</td><td>0.0944</td><td>0.1808</td><td>5.27</td><td>0.0701</td><td>0.1561</td></tr><tr><td>Emotional</td><td>8.25</td><td>0.0793</td><td>0.1838</td><td>8.00</td><td>0.0758</td><td>0.1634</td></tr><tr><td>Neighborhood</td><td>6.67</td><td>0.0739</td><td>0.1546</td><td>6.40</td><td>0.0652</td><td>0.1573</td></tr><tr><td>Chain</td><td>4.67</td><td>0.0830</td><td>0.1749</td><td>7.50</td><td>0.0699</td><td>0.1548</td></tr><tr><td rowspan="4">(C) Rec. (Manual)</td><td>Original</td><td>6.50</td><td>0.0853</td><td>0.1823</td><td>4.92</td><td>0.0761</td><td>0.1583</td></tr><tr><td>Emotional</td><td>6.00</td><td>0.0834</td><td>0.1847</td><td>8.50</td><td>0.0749</td><td>0.1616</td></tr><tr><td>Neighborhood</td><td>3.00</td><td>0.0804</td><td>0.1695</td><td>7.33</td><td>0.0661</td><td>0.1417</td></tr><tr><td>Chain</td><td>5.89</td><td>0.0834</td><td>0.1743</td><td>1.00</td><td>0.0725</td><td>0.1684</td></tr><tr><td colspan="8">Demotion Scenario</td></tr><tr><td rowspan="4">(A) Retrieval</td><td>Original</td><td>25.56</td><td>0.1504</td><td>0.2101</td><td>26.99</td><td>0.1205</td><td>0.1615</td></tr><tr><td>Emotional</td><td>22.80</td><td>0.1299</td><td>0.1849</td><td>21.69</td><td>0.1246</td><td>0.1679</td></tr><tr><td>Neighborhood</td><td>24.66</td><td>0.1414</td><td>0.1929</td><td>25.13</td><td>0.1190</td><td>0.1674</td></tr><tr><td>Chain</td><td>20.60</td><td>0.1344</td><td>0.1931</td><td>25.91</td><td>0.1251</td><td>0.1637</td></tr><tr><td rowspan="4">(B) Rec. (LLM)</td><td>Original</td><td>5.72</td><td>0.0943</td><td>0.1842</td><td>4.95</td><td>0.0733</td><td>0.1543</td></tr><tr><td>Emotional</td><td>4.95</td><td>0.0853</td><td>0.1966</td><td>4.40</td><td>0.0755</td><td>0.1700</td></tr><tr><td>Neighborhood</td><td>5.87</td><td>0.0790</td><td>0.1759</td><td>4.75</td><td>0.0793</td><td>0.1794</td></tr><tr><td>Chain</td><td>5.44</td><td>0.0747</td><td>0.1760</td><td>4.44</td><td>0.0707</td><td>0.1599</td></tr><tr><td rowspan="4">(C) Rec. (Manual)</td><td>Original</td><td>5.65</td><td>0.0972</td><td>0.1837</td><td>4.96</td><td>0.0767</td><td>0.1694</td></tr><tr><td>Emotional</td><td>5.53</td><td>0.0810</td><td>0.1857</td><td>4.57</td><td>0.0670</td><td>0.1514</td></tr><tr><td>Neighborhood</td><td>5.63</td><td>0.0765</td><td>0.1765</td><td>4.67</td><td>0.0817</td><td>0.1703</td></tr><tr><td>Chain</td><td>5.38</td><td>0.0740</td><td>0.1748</td><td>5.00</td><td>0.0716</td><td>0.1488</td></tr></table>

## RQ3: Impact on System-Wide Recall and nDCG

Beyond item-specific ranking, Table 1 also reports Recall and nDCG. Notably, these global performance metrics do not consistently suf fer drastic declines, with the maximum observed drop typically limited to a few percentage points. While such localized attacks pri marily disrupt the visibility of a targeted subset, large-scale poison ing—where a significant fraction of items are manipulated—could lead to more pervasive performance deterioration. This aligns with related work demonstrating that simultaneous metadata rewrites on a broader scale can substantially undermine system accuracy [12]. In short, although the system’s global fidelity remains relatively intact for sparse attacks, the localized impact on individual item positions seems to be more pronounced.

Overall, these results confirm that retrieval-augmented recom mender systems are vulnerable to data poisoning via concise textual edits. Small-scale, stealthy manipulations—particularly those that combine emotive triggers and neighbor-based phrasing—can effectuate substantial ranking shifts without severely compromising system-level metrics. The heightened sensitivity of LLM-driven pipelines underscores the importance of developing robust checks on textual provenance and integrity to mitigate provider-side poisoning attempts.

## 5 Conclusion

Our work demonstrates that carefully designed textual perturbations (modifications) in item metadata can strategically alter recommendations in Retrieval-Augmented Generation (RAG) systems, emphasizing the need for robust textual provenance checks. Through a systematic exploration of diferent attack strategies—including emotional rewording<sup>,</sup> neighbor-based borrowing<sup>,</sup> <sup>and</sup> hybrid chain-<sub>ing</sub>—our experiments reveal that even <sub>small-scale</sub> <sub>semantic</sub> <sub>ma-</sub> <sub>nipulations</sub> can efectively boost the visibility of long-tail items or suppress popular ones, often while remaining stealthy and dificult to detect. These findings underscore the potential provider-side vulnerabilities in RAG-based pipelines and the necessity of defensive measures to safeguard recommendation integrity.

## Acknowledgments

The authors acknowledge partial support of the following projects: OVS: Fashion Retail Reloaded and Lutech Digitale 4.0.

## References

[1] Arijit Ghosh Chowdhury, Md Mofijul Islam, Vaibhav Kumar, Faysal Hossain Shezan, Vinija Jain, and Aman Chadha. 2024. Breaking down the defenses: A comparative survey of attacks on large language models. <sub>arXiv</sub> <sub>preprint</sub> arXiv:2403.04786 <sup>(2024).</sup>

[2] Yashar Deldjoo, Zhankui He, Julian McAuley, Anton Korikov, Scott Sanner, Arnau Ramisa, René Vidal, Maheswaran Sathiamoorthy, Atoosa Kasirzadeh, and Silvia Milano. 2024. A Review of Modern Recommender Systems using Generative <sup>Models</sup> <sup>(Gen-RecSys).</sup> <sup>In</sup> Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining<sup>.</sup> <sup>6448–6458.</sup>

[3] Yashar Deldjoo, Zhankui He, Julian McAuley, Anton Korikov, Scott Sanner, Ar nau Ramisa, Rene Vidal, Maheswaran Sathiamoorthy, Atoosa Kasrizadeh, Silvia Milano, et al. 2024. Recommendation with Generative Models. <sub>arXiv</sub> <sub>preprint</sub> arXiv:2409.15173 <sup>(2024).</sup>

[4] Yashar Deldjoo, Nikhil Mehta, Maheswaran Sathiamoorthy, Shuai Zhang, Pablo Castells, and Julian McAuley. 2025. Toward Holistic Evaluation of Recommender Systems Powered by Generative Models. <sub>SIGIR’25</sub> (2025).

[5] Yashar Deldjoo, Tommaso Di Noia, and Felice Antonio Merra. 2021. A survey on adversarial recommender systems: from attack/defense strategies to generative adversarial networks. <sub>ACM</sub> <sub>Computing</sub> <sub>Surveys</sub> <sub>(CSUR)</sub> 54, 2 (2021), 1–38.

[6] Wenqi Fan, Yujuan Ding, Liangbo Ning, Shijie Wang, Hengyun Li, Dawei Yin, Tat-Seng Chua, and Qing Li. 2024. A survey on rag meeting llms: Towards

retrieval-augmented large language models. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> <sub>30th</sub> <sub>ACM</sub> SIGKDD Conference on Knowledge Discovery and Data Mining<sup>.</sup> <sup>6491–6501.</sup>

[7] Yi Liu, Gelei Deng, Yuekang Li, Kailong Wang, Zihao Wang, Xiaofeng Wang, Tianwei Zhang, Yepang Liu, Haoyu Wang, Yan Zheng, et al. 2023. Prompt Injection attack against LLM-integrated Applications. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2306.05499</sub> (2023).

[8] Fatemeh Nazary, Yashar Deldjoo, and Tommaso di Noia. 2025. Poison-rag: Adver sarial data poisoning attacks on retrieval-augmented generation in recommender <sup>systems.</sup> <sup>In</sup> European Conference on Information Retrieval<sup>.</sup> <sup>Springer,</sup> <sup>239–251.</sup>

[9] N Reimers. 2019. Sentence-BERT: Sentence Embeddings using Siamese BERT-<sup>Networks.</sup> arXiv preprint arXiv:1908.10084 <sup>(2019).</sup>

[10] Yifei Wang, Dizhan Xue, Shengjie Zhang, and Shengsheng Qian. 2024. BadAgent: Inserting and Activating Backdoor Attacks in LLM Agents. <sub>arXiv</sub> <sub>preprint</sub> arXiv:2406.03007 <sup>(2024).</sup>

[11] Alexander Wei, Nika Haghtalab, and Jacob Steinhardt. 2024. Jailbroken: How <sup>does</sup> <sup>llm</sup> <sup>safety</sup> <sup>training</sup> <sup>fail?</sup> Advances in Neural Information Processing Systems 36 (2024).

[12] Jiaqi Xue, Mengxin Zheng, Yebowen Hu, Fei Liu, Xun Chen, and Qian Lou. 2024. BadRAG: Identifying Vulnerabilities in Retrieval Augmented Generation of Large <sup>Language</sup> <sup>Models.</sup> arXiv preprint arXiv:2406.00083 <sup>(2024)</sup>

[13] Wei Zou, Runpeng Geng, Binghui Wang, and Jinyuan Jia. 2024. Poisonedrag: Knowledge poisoning attacks to retrieval-augmented generation of large lan-<sup>guage</sup> <sup>models.</sup> arXiv preprint arXiv:2402.07867 <sup>(2024).</sup>


---

# 2606.09595_多模态电影推荐视觉证据基准

[2606.09595](https://arxiv.org/abs/2606.09595)

# Popcorn: A Configurable Benchmark for Visual Evidence in Multimodal Movie Recommendation

Ali Tourani<sup>∗</sup>, Fatemeh Nazary<sup>†</sup>, Yashar Deldjoo<sup>‡</sup>, Tommaso Di Noia<sup>§</sup>,

June 9, 2026

## Abstract

Movies are long-form audiovisual works, yet recommender benchmarks often rely on trailers, thumbnails, or metadata. These sources difer in semantics and scalability: full movies preserve consumption-level evidence, trailers concentrate promotional highlights, and thumbnails provide sparse but catalog-scale visual signals. We present Popcorn, a configurable benchmark for visual evidence in multimodal movie recommendation, combining title-aligned full-movie/trailer embeddings with MovieLens-linked thumbnail features encoded by modern visual and vision-language models. Popcorn standardizes modality assembly, fusion, splitting, evaluation, and LLM-augmented metadata through a single configuration contract. Experiments show that thumbnail VLMs provide strong, scalable item-side evidence, while controlled trailer/full-movie comparisons show that visual evidence sources are not interchangeable: the choice of source and fusion strategy afects ranking accuracy, coverage, diversity, and calibration. The framework is available at https://github.com/RecSys-lab/Popcorn.

## 1 Introduction and Related Resources

Movies are inherently multimodal cultural artifacts: viewers respond not only to plot and genre, but also to cast, dialogue, soundtrack, color palette, camera motion, editing rhythm, and visual style. Nevertheless, movie recommendation benchmarks often operationalize films through user–item interactions, sparse metadata, posters, or short promotional videos. Although such abstractions are practical, they obscure a fundamental modeling choice: what visual evidence is the recommender learning from?

The answer is consequential because visual evidence sources difer in semantics, availability, and computational cost (Fig. 1). A full movie is closest to the consumed item and preserves narrative structure, pacing, repeated shots, camera motion, and long-form audiovisual style, but it is dificult to distribute and expensive to process. A trailer is compact and widely accessible, yet it is a promotiona artifact that deliberately concentrates stars, genre cues, action, mood, and salient scenes. A thumbnail or poster is the most scalable evidence source, but it compresses a film’s visual identity into a single static image, typically emphasizing faces, typography, iconic objects, color palette, and genre symbolism. This distinction also determines what visual backbones can exploit. The mainstream approach in earlier multimodal movie recommendation has been to extract CNN features from multiple video frames, typically from trailers or other sampled video data [4, 5]. Such multi-frame CNN pipelines can capture recurring objects, textures, scene composition, lighting, and frame-level cues that act as proxies for genre, mood, or visual style. Modern vision-language models (VLMs), in contrast, can encode a single thumbnail or poster into a semantically organized image–text representation, making sparse image evidence surprisingly informative at large catalog scale. Thus, the comparison studied here is not only a backbone comparison between classical CNNs and modern VLMs; it is a comparison between two evidence regimes: multipleframe trailer/full-movie evidence with classical CNN pipelines and single-thumbnail semantic evidence with modern VLMs. Popcorn aims to make this distinction explicit so that improvements can be interpreted in terms of evidence source, encoder family, scalability, and downstream recommendation behavior.

![](images/1aa1a0788243089c9b94fe1cd92ad7ffd4f21ad74fa2361bdeed451aaf7b38a2.jpg)  
Figure 1: Conceptual comparison of full movies, trailers, and thumbnails as visual evidence sources, contrasting multi-frame CNN evidence from full movies/trailers with single-image VLM evidence from thumbnails at catalog scale.

Related resources and gap. As summarized in Table 1, existing multimodal recommendation resources provide important foundations but do not isolate the source of visual evidence as the central experimental variable. Feature toolkits such as Ducho and Ducho×Elliot support multimodal extraction and integration [2, 1], while MMRec and MMSSL focus on broader multimodal model benchmarking [22, 20]. Movie and video resources such as MMTF-14K, MicroLens, ViLLA-MMBench, and RAG-VisualRec contribute trailer features, micro-video scale, or LLM/RAG-oriented protocols [4, 10, 9, 18]. However, these resources do not jointly provide evidence for thumbnails, trailers, and full-movie data; CNN and VLM backbones; multimodal fusion; GenAI components; configuration-controlled evaluation; and beyondaccuracy auditing. This leaves open a basic question: whether conclusions drawn from trailer features transfer to full movies, and how static thumbnail evidence encoded by modern VLMs compares with multi-frame CNN evidence under a shared recommendation protocol.

We introduce Popcorn, a resource and configurable benchmark for controlled visual-evidence evalu ation in multimodal movie recommendation. Rather than proposing a new recommender architecture, Popcorn releases complementary data resources and a software pipeline: (i) title-aligned full-movie/trailer evidence for 274 movies, provided as derived frame-level, shot-level, and pooled embeddings, with framelevel representations sampled at 1 FPS; (ii) a MovieLens-linked thumbnail layer covering approximately 65K titles, organized into 13 image packs and encoded with six modern visual/VLM backbones, yielding more than 300K visual embeddings; and (iii) a configuration-driven multimodal pipeline for evidence loading, fusion, training, evaluation, LLM augmentation, and Visual RAG. The benchmark allows researchers to vary evidence source, backbone, fusion, augmentation, recommender, and evaluation setting while keeping the downstream protocol fixed. Our contributions are:

• Visual-evidence benchmark (§4 - RQ1). Popcorn frames multimodal movie recommendation as a controlled visual-evidence benchmark, directly comparing single-thumbnail VLM evidence with multi-frame CNN evidence from trailers and full movies under a fixed split, recommender, and evaluation protocol.

• Released aligned-video and thumbnail evidence layers. Popcorn releases derived embeddings for 274 title-aligned full movies and trailers at frame, shot, and pooled granularities, encoded with classical CNN backbones including Inception-v3 [15] and VGG-19 [14]. It further provides a scalable thumbnail/VLM layer linking approximately 65K MovieLens-25M titles to poster evidence encoded with CLIP [13], OpenCLIP [3], DINOv2-base/large [11], SigLIP-base [21], and SigLIP2-base [19].

Table 1: Positioning Popcorn against representative multimodal recommendation resources. Symbols: • = primary support, △ = partial or indirect support, and ◦ = not addressed/applicable. Popcorn is distinct in combining thumbnail, trailer, and full-movie evidence with CNN/VLM backbones, GenA modules, Visual RAG, controlled configurations, and beyond-accuracy auditing.

<table><tr><td rowspan="2">Work / resource</td><td colspan="4">Evidence</td><td colspan="2">Backbone</td><td colspan="3">Modalities</td><td colspan="2">GenAI</td><td colspan="2">Benchmark</td><td rowspan="2">Gap addressed</td></tr><tr><td>Thumb</td><td>Trailer</td><td>Full</td><td>Micro</td><td>CNN</td><td>VLM</td><td>Visual</td><td>Audio</td><td>Text</td><td>LLM text</td><td>V-RAG</td><td>Config</td><td>Audit</td></tr><tr><td>Ducho / Ducho×Elliot [2, 1]</td><td>○</td><td>○</td><td>○</td><td>○</td><td>△</td><td>△</td><td>●</td><td>●</td><td>●</td><td>○</td><td>○</td><td>△</td><td>○</td><td>Feature extraction toolkit; not a source-controlled movie benchmark.</td></tr><tr><td>MMRec / MMSSL [22, 20]</td><td>○</td><td>○</td><td>○</td><td>○</td><td>△</td><td>△</td><td>●</td><td>●</td><td>●</td><td>○</td><td>○</td><td>△</td><td>○</td><td>Model-centric multimodal recommendation; evidence source is not the primary variable.</td></tr><tr><td>Rec-GPT4V / MMRec-LLM [8, 17]</td><td>△</td><td>○</td><td>○</td><td>○</td><td>○</td><td>●</td><td>●</td><td>○</td><td>●</td><td>●</td><td>△</td><td>△</td><td>○</td><td>VLM/LLM reasoning without full-movie/trailer evidence control.</td></tr><tr><td>MicroLens [10]</td><td>○</td><td>○</td><td>○</td><td>●</td><td>△</td><td>△</td><td>●</td><td>●</td><td>○</td><td>○</td><td>○</td><td>△</td><td>○</td><td>Large micro-video scale, but not long-form movie evidence.</td></tr><tr><td>MMTF-14K [4]</td><td>○</td><td>●</td><td>○</td><td>○</td><td>●</td><td>○</td><td>●</td><td>●</td><td>○</td><td>○</td><td>○</td><td>△</td><td>○</td><td>Trailer features; no full-movie or VLM thumbnail layer.</td></tr><tr><td>ViLLA-MMBench [9]</td><td>○</td><td>●</td><td>○</td><td>○</td><td>△</td><td>△</td><td>●</td><td>●</td><td>●</td><td>△</td><td>○</td><td>●</td><td>△</td><td>Trailer-centric evaluation without full-movie alignment.</td></tr><tr><td>RAG-VisualRec [18]</td><td>○</td><td>●</td><td>○</td><td>○</td><td>△</td><td>△</td><td>●</td><td>○</td><td>●</td><td>●</td><td>●</td><td>●</td><td>△</td><td>Visual RAG for trailers; no controlled thumbnail/trailer/full comparison.</td></tr><tr><td>Popcorn</td><td>●</td><td>●</td><td>●</td><td>○</td><td>●</td><td>●</td><td>●</td><td>●</td><td>●</td><td>●</td><td>●</td><td>●</td><td>●</td><td>Source-controlled visual evidence benchmark and reproducible pipeline.</td></tr></table>

• Auditable fusion and augmentation (§4 - RQ2). Popcorn records modality choices, PCA/CCA settings, text-augmentation state, split configuration, recommender, and exported metrics. Experiments use representative multimedia recommenders—Visual Bayesian Personalized Ranking (VBPR) [7], Adversarial Multimedia Recommendation (AMR) [16], and Visual Matrix Factorization (VMF) [12]—to make fusion and LLM-augmentation efects explicit.

• Cost-aware VLM and beyond-accuracy analysis (§4 - RQ3). Popcorn reports recall, coverage, novelty, diversity, fairness, popularity bias, cold-rate exposure, and calibration, and relates thumbnail VLM performance to a model-size/storage proxy.

Overall, Popcorn contributes both data—thumbnail, trailer, and full-movie evidence layers—and software—a configurable multimodal recommendation pipeline for reproducible visual-evidence analysis.

## 2 Popcorn Resource and Pipeline

Popcorn is organized as a layered resource and pipeline for controlled visual-evidence benchmarking, complementing prior trailer-, micro-video-, and RAG-oriented resources [4, 10, 9, 18]. The aligned-video layer contains derived embeddings for 274 title-aligned full movies and oficial trailers, exposed at frame, shot, and pooled levels<sup>1</sup>. The thumbnail/VLM layer links approximately 65,000 MovieLens-25M titles to thumbnail or poster evidence, packaged into 13 image packs and encoded with six modern visua backbones, yielding more than 300K visual embeddings<sup>2</sup>. The software layer provides loaders, ID alignments, modality assembly, fusion modules, splitters, recommender wrappers, hyperparameter search, metric export, and optional LLM/RAG components. Full movies are released as derived embeddings rather than raw videos; users with lawful access can recompute features through the pipeline<sup>3</sup>.

Let U be users, I movies, and $R \subseteq U \times I$ observed feedback. For item i, Popcorn makes visual evidence explicit as e ∈ {thumb, trailer, full}. Given backbone $b ,$ granularity g, and pooling operator p, the visual representation is

$$
\mathbf {x} _ {i} ^ {(e, b, g, p)} = p \left(\{\psi_ {b} (v): v \in \mathcal {V} _ {i} ^ {(e, g)} \}\right),\tag{1}
$$

![](images/26e090a8a6a0a3728af26d68c5964daacde09617a3c10f75db938beda837fc53.jpg)  
Figure 2: Popcorn architecture. A single configuration controls evidence loading, visual/audio/text pipelines, optional fusion (Concat/PCA/CCA), split construction, training, HPO, metric export, LLMbased enrichment, and Visual RAG reranking or explanations.

where $\mathcal { V } _ { i } ^ { ( e , g ) }$ is a singleton image for thumbnails or a frame/shot sequence for video. Optional text and audio vectors are denoted $\mathbf { t } _ { i }$ and ${ \bf a } _ { i }$ . A fusion operator $\phi$ constructs $\mathbf { z } _ { i } = \phi ( \mathbf { x } _ { i } ^ { ( e , b , g , p ) } , \mathbf { t } _ { i } , \mathbf { a } _ { i } )$ ), where ϕ may be identity, concatenation, PCA, CCA, or rank aggregation.

A run is identified by $( D , I , e , b , g , p , \mathcal { M } , \phi , f _ { \theta } , s , K )$ , specifying dataset, item universe, evidence source, backbone, granularity, modality set, fusion, recommender, split, and cutof. The toolkit exports the resolved configuration, recommendation lists, and metrics, making ablations reproducible. LLM modules are optional: item enrichment expands sparse metadata into descriptions whose embeddings can be fused with visual vectors; profile enrichment summarizes interaction histories; and Visual $\mathrm { R A G ^ { 4 } }$ injects retrieved frames, shots, or thumbnails with provenance into the LLM context for auditable reranking and explanations.

## 3 Benchmark Protocol

The large-catalog experiments use MovieLens-1M [6] interactions with a 10-core filter, top-10 recom mendation, and VBPR [7] over approximately 14K MovieLens-linked items. They compare audio, LLM-augmented text, single-thumbnail/VLM visual features, PCA/CCA fusion, and the MMTF-14K [4] trailer-CNN visual baseline. The thumbnail backbones are CLIP [13], OpenCLIP [3], DINOv2-base and -large [11], SigLIP-base [21], and SigLIP2-base [19]. The aligned-video experiments use the 274-title full movie/trailer subset with Inception-v3 [15] aggregate max-pooled CNN features and report in visual-only and text+visual CCA settings.

Metrics. We evaluate two metric groups. Accuracy metrics include nDCG@10, Recall@10, precision, MAP, and hit rate, computed at top-K with binary relevance. Beyond-accuracy metrics include coverage, novelty, diversity, fairness, popularity bias, cold rate, and calibration bias. For brevity, we only name these metrics here; their formal definitions and implementation details are provided in the GitHub repository. Higher values are preferred for accuracy, coverage, novelty, diversity, fairness, and cold-rate exposure, while lower values are preferred for popularity bias and calibration bias.

Fusion and projection settings. Popcorn treats PCA and CCA as configurable hyperparameters rather than fixed preprocessing defaults. The system supports full hyperparameter search over fusion choices exposed in config.yml, including PCA variance thresholds, CCA component counts, and CCA regularization. In the thumbnail/VLM dashboard, PCA retains 90% of variance and CCA uses 40 canonica components for the rows in Table 2. In the aligned-video grid, the best-reported CCA configurations use 40 components with regularization parameter λ = 0.01. Each exported run stores the resolved fusion method, PCA threshold, CCA dimensionality, and regularization value for reproducibility.

Table 2: Popcorn benchmark dashboard. Panel A reports the larger thumbnail/VLM slice with VBPR; ∆ is relative to the MMTF-14K CNN visual baseline (0.222 nDCG@10, 0.203 Recall@10). Panel B reports the aligned-video slice; metric pairs are trailer/full-movie, and ∆ is the relative advantage of the winning source.

<table><tr><td>ID</td><td>Source</td><td>Mod.</td><td>Encoder / features</td><td>Fusion</td><td>nDCG@10</td><td>Recall@10</td><td>Δ</td><td>Interpretation</td></tr><tr><td colspan="9">Panel A: larger thumbnail/VLM benchmark, |I| ≈ 14K, model = VBPR</td></tr><tr><td>A0</td><td>Trailer</td><td>V</td><td>MMTF-14K CNN</td><td>none</td><td>0.222</td><td>0.203</td><td>reference</td><td>Older trailer-CNN visual baseline.</td></tr><tr><td>A1</td><td>Audio</td><td>A</td><td>MMTF-14K BLF</td><td>none</td><td>0.237</td><td>0.215</td><td>+6.8/+5.9</td><td>Audio side information is competitive with older CNN visual features.</td></tr><tr><td>A2</td><td>Text</td><td>T</td><td>LLaMA text,text_aug=true</td><td>none</td><td>0.240</td><td>0.221</td><td>+8.1/+8.9</td><td>Generated textual context can be useful if logged with prompts and embeddings.</td></tr><tr><td>A3</td><td>Thumb</td><td>V</td><td>CLIP</td><td>none</td><td>0.254</td><td>0.235</td><td>+14.4/+15.8</td><td>Static VLM features exceed the older CNN visual baseline.</td></tr><tr><td>A4</td><td>Thumb</td><td>V</td><td>DINOv2-base</td><td>none</td><td>0.243</td><td>0.224</td><td>+9.5/+10.3</td><td>Self-supervised image features provide a strong static visual signal.</td></tr><tr><td>A5</td><td>Thumb</td><td>V</td><td>DINOv2-large</td><td>none</td><td>0.248</td><td>0.226</td><td>+11.7/+11.3</td><td>Larger DINOv2 improves over base but remains below SigLIP-base.</td></tr><tr><td>A6</td><td>Thumb</td><td>V</td><td>OpenCLIP</td><td>none</td><td>0.250</td><td>0.227</td><td>+12.6/+11.8</td><td>Contrastive VLM features remain robust.</td></tr><tr><td>A7</td><td>Thumb</td><td>V</td><td>SigLIP2-base</td><td>none</td><td>0.250</td><td>0.228</td><td>+12.6/+12.3</td><td>Strong VLM feature, slightly below SigLIP-base here.</td></tr><tr><td>A8</td><td>Thumb</td><td>V</td><td>SigLIP-base</td><td>none</td><td>0.269</td><td>0.262</td><td>+21.2/+29.1</td><td>Best visual-only row; demonstrates the value of the thumbnail/VLM scale layer.</td></tr><tr><td>A9</td><td>Fuse</td><td>V+T</td><td>SigLIP-base</td><td>PCA (var.0.9)</td><td>0.242</td><td>0.240</td><td>+9.0/+18.2</td><td>Fusion is not automatically beneficial; SigLIP visual has higher nDCG@10.</td></tr><tr><td>A10</td><td>Fuse</td><td>V+T</td><td>SigLIP-base</td><td>CCA(comp. 40)</td><td>0.268</td><td>0.261</td><td>+20.7/+28.6</td><td>CCA nearly matches the best visual-only result without surpassing it.</td></tr><tr><td colspan="9">Panel B: aligned trailer/full-movie benchmark, 274 titles; metric pairs are trailer/full-movie</td></tr><tr><td>B1</td><td>T/F</td><td>V</td><td>VBPR; Inception-v3 agg.max</td><td>none</td><td>0.433/0.413</td><td>0.575/0.552</td><td>Trailer +4.8/+4.2</td><td>Trailer visual-only evidence is higher under the fixed title set.</td></tr><tr><td>B2</td><td>T/F</td><td>V+T</td><td>VBPR; text+visual</td><td>CCA(comp. 40)</td><td>0.444/0.436</td><td>0.579/0.573</td><td>Trailer +1.8/+1.0</td><td>Fusion narrows but does not reverse the source gap.</td></tr><tr><td>B3</td><td>T/F</td><td>V</td><td>AMR; Inception-v3 agg.max</td><td>none</td><td>0.339/0.298</td><td>0.468/0.411</td><td>Trailer +13.8/+13.9</td><td>Trailer visual-only evidence is substantially higher.</td></tr><tr><td>B4</td><td>T/F</td><td>V+T</td><td>AMR; text+visual</td><td>CCA(comp. 40)</td><td>0.425/0.434</td><td>0.555/0.564</td><td>Full +2.1/+1.6</td><td>Fusion reverses the source ordering.</td></tr><tr><td>B5</td><td>T/F</td><td>V</td><td>VMF; Inception-v3 agg.max</td><td>none</td><td>0.281/0.266</td><td>0.395/0.382</td><td>Trailer +5.6/+3.4</td><td>Trailer is slightly higher in the visual-only setting.</td></tr><tr><td>B6</td><td>T/F</td><td>V+T</td><td>VMF; text+visual</td><td>CCA(comp. 40)</td><td>0.275/0.285</td><td>0.385/0.391</td><td>Full +3.6/+1.6</td><td>Full movie is slightly higher after fusion.</td></tr></table>

LLM data augmentation. Text augmentation is controlled by text aug. When enabled, an LLM expands sparse item metadata such as title, genres, tags, and missing plot descriptions into a concise paragraph describing plot, themes, style, and salient entities. The resulting text (Table 3) is embedded by the selected backend (OpenAI, SentenceTransformer, or LLaMA-family) and can be used on its own or fused with visual/audio vectors. Augmented descriptions, prompts, embeddings, recommendation lists, and metrics can be exported for audit.

Table 3: Example of LLM-based data augmentation, where sparse movie metadata is expanded into a concise description while fixed fields remain unchanged.

<table><tr><td>Aspect</td><td>Before</td><td>After LLM augmentation</td></tr><tr><td>Title</td><td>Nixon (1995)</td><td>unchanged</td></tr><tr><td>Genres</td><td>Drama | Biography</td><td>unchanged</td></tr><tr><td>Description</td><td>Not provided</td><td>“Nixon (1995) explores the troubled psyche and political career of America’s 37th president, delving into his strategic brilliance and moral compromises ...”</td></tr></table>

![](images/b8bd63e026ea069e4ed9742c289ae4817080c4225a5439093b89491e7ae06f06.jpg)  
Figure 3: Thumbnail VLM trade-ofs: nDCG@10 gain over the MMTF-14K CNN baseline, with labels for recall, coverage, and diversity. Colors denote model-tier cost proxies.

## 4 Experiments and Discussion

We organize the discussion around three experimental questions: RQ1 asks how far a single thumbnail encoded by a VLM can go compared with multi-frame CNN evidence from trailers or full movies; RQ2 asks whether gains come from multimodal fusion or from LLM data augmentation, and how these choices afect beyond-accuracy metrics; and RQ3 asks how thumbnail VLM performance changes with a model-size/storage proxy.

RQ1: visual evidence. Table 2 shows that a single thumbnail encoded by modern VLMs can outperform the older MMTF-14K trailer-CNN visual baseline. SigLIP-base reaches nDCG@10=0.269 and Recall@10=0.262, corresponding to gains of 21.2% and 29.1%. The result should not be interpreted as thumbnails fully representing films: thumbnails cannot observe pacing, repeated shots, or narrative progression. Rather, they provide a strong catalog-scale semantic signal. On the aligned 274-title slice, trailers remain stronger than full movies in visual-only settings for VBPR, AMR, and VMF, which is plausible because trailers concentrate recommendation-salient highlights. After CCA fusion, the gap narrows for VBPR and reverses for AMR and VMF, showing that trailers and full movies are no interchangeable.

RQ2: fusion versus data augmentation. Fusion helps in some settings but is not a monotonic improvement. In Panel A, SigLIP-base visual-only is slightly stronger than CCA on nDCG@10 (0.269 vs. 0.268), while CCA increases coverage from 0.767 to 0.918 but lowers diversity from 0.766 to 0.749 and raises calibration bias from 2.901 to 3.125. PCA is weaker on accuracy (0.242 nDCG@10) despite retaining reasonable diversity. The aligned-video results show the same pattern: VBPR trailer CCA improves over visual-only from 0.433 to 0.444 nDCG@10, and AMR full-movie CCA improves over text-only from 0.378 to 0.434 nDCG@10and from 0.506 to 0.564 Recall@10. Beyond-accuracy values show the cost of this gain: for AMR full movies with OpenAI text and no augmentation, CCA reaches 0.434 nDCG@10 and 0.564 Recall@10, but diversity drops to 0.742, below visual-only 0.773 and text-only 0.763. Data augmentation is also model-dependent: VBPR benefits modestly from LLaMA augmentation in the fused full-movie row (0.436 vs. 0.431 nDCG@10 without augmentation), whereas AMR’s strongest CCA row uses OpenAI text without augmentation. Full grids are provided in the GitHub repository.<sup>5</sup>

RQ3: VLM cost versus performance. Figure 3 modernizes the attached bar plot by removing calibration and storage text while retaining recall, coverage, and diversity. SigLIP-base has the best accuracy and recall, but CLIP has the highest coverage (0.785), and DINOv2-base/large has the highest diversity (0.777/0.776). The color-coded tiers show that performance is not monotonic with the cost proxy: the medium SigLIP-base is strongest in accuracy, the small CLIP is strongest in coverage, and the large DINOv2-large is not the best overall. Backbone selection should therefore depend on the intended deployment objective rather than model size alone.

## 5 Conclusion and Limitations

We presented Popcorn, a configurable benchmark for visual evidence in multimodal movie recommendation. Popcorn separates thumbnails, trailers, and full movies while logging the backbone, fusion, augmentation, split, recommender, and evaluation settings needed for reproducible ablations. Results show that modern

VLM thumbnails improve over older CNN visual baselines, while trailer/full-movie evidence, fusion, and augmentation afect both accuracy and beyond-accuracy behavior.

The main limitations are scale, access, and ofline evaluation. Full movies are released as derived embeddings; the aligned full-movie subset is smaller than the thumbnail layer, and LLM augmentation remains sensitive to model and prompt choices. Future work will extend Popcorn with larger lawful-access full-movie collections, stronger temporal encoders, audio-centric ablations, Visual RAG integration, user studies, and online evaluation.

## References

[1] M. Attimonelli, D. Danese, A. Di Fazio, D. Malitesta, C. Pomo, and T. Di Noia. Ducho meets elliot: Large-scale benchmarks for multimodal recommendation. arXiv preprint arXiv:2409.15857, 2024.

[2] M. Attimonelli, D. Danese, D. Malitesta, C. Pomo, G. Gassi, and T. Di Noia. Ducho 2.0: Towards a more up-to-date unified framework for the extraction of multimodal features in recommendation. In Companion Proceedings of the ACM on Web Conference 2024, pages 1075–1078, 2024.

[3] M. Cherti, R. Beaumont, R. Wightman, M. Wortsman, G. Ilharco, C. Gordon, C. Schuhmann, L. Schmidt, and J. Jitsev. Reproducible scaling laws for contrastive language-image learning. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pages 2818–2829, 2023.

[4] Y. Deldjoo, M. G. Constantin, B. Ionescu, M. Schedl, and P. Cremonesi. Mmtf-14k: a multifaceted movie trailer feature dataset for recommendation and retrieval. In Proceedings of the 9th ACM Multimedia Systems Conference, pages 450–455, 2018.

[5] Y. Deldjoo, M. Schedl, P. Cremonesi, and G. Pasi. Recommender systems leveraging multimedia content. ACM Computing Surveys (CSUR), 53(5):1–38, 2021.

[6] F. M. Harper and J. A. Konstan. The movielens datasets: History and context. Acm transactions on interactive intelligent systems (tiis), 5(4):1–19, 2015.

[7] R. He and J. McAuley. Vbpr: visual bayesian personalized ranking from implicit feedback. In Proceedings of the AAAI conference on artificial intelligence, volume 30, 2016.

[8] Y. Liu, Y. Wang, L. Sun, and P. S. Yu. Rec-gpt4v: Multimodal recommendation with large vision-language models. arXiv preprint arXiv:2402.08670, 2024.

[9] F. Nazary, A. Tourani, Y. Deldjoo, and T. Di Noia. Villa-mmbench: A unified benchmark suite for llm-augmented multimodal movie recommendation. arXiv preprint arXiv:2508.04206, 2025.

[10] Y. Ni, Y. Cheng, X. Liu, J. Fu, Y. Li, X. He, Y. Zhang, and F. Yuan. A content-driven micro-video recommendation dataset at scale. arXiv preprint arXiv:2309.15379, 2023.

[11] M. Oquab, T. Darcet, T. Moutakanni, H. Vo, M. Szafraniec, V. Khalidov, P. Fernandez, D. Haziza, F. Massa, A. El-Nouby, et al. Dinov2: Learning robust visual features without supervision. arXiv preprint arXiv:2304.07193, 2023.

[12] C. Park, D. Kim, J. Oh, and H. Yu. Do” also-viewed” products help user rating prediction? In Proceedings of the 26th international conference on world wide web, pages 1113–1122, 2017.

[13] A. Radford, J. W. Kim, C. Hallacy, A. Ramesh, G. Goh, S. Agarwal, G. Sastry, A. Askell, P. Mishkin, J. Clark, et al. Learning transferable visual models from natural language supervision. In International conference on machine learning, pages 8748–8763. PmLR, 2021.

[14] K. Simonyan and A. Zisserman. Very deep convolutional networks for large-scale image recognition. arXiv preprint arXiv:1409.1556, 2014.

[15] C. Szegedy, V. Vanhoucke, S. Iofe, J. Shlens, and Z. Wojna. Rethinking the inception architecture for computer vision. In Proceedings of the IEEE conference on computer vision and pattern recognition, pages 2818–2826, 2016.

[16] J. Tang, X. Du, X. He, F. Yuan, Q. Tian, and T.-S. Chua. Adversarial training towards robust multimedia recommender system. IEEE Transactions on Knowledge and Data Engineering, 32(5):855– 867, 2019.

[17] J. Tian, Z. Wang, J. Zhao, and Z. Ding. Mmrec: Llm based multi-modal recommender system. In 2024 19th International Workshop on Semantic and Social Media Adaptation & Personalization (SMAP), pages 105–110. IEEE, 2024.

[18] A. Tourani, F. Nazary, and Y. Deldjoo. Rag-visualrec: An open resource for vision-and text-enhanced retrieval-augmented generation in recommendation. arXiv preprint arXiv:2506.20817, 2025.

[19] M. Tschannen, A. Gritsenko, X. Wang, M. F. Naeem, I. Alabdulmohsin, N. Parthasarathy, T. Evans, L. Beyer, Y. Xia, B. Mustafa, et al. Siglip 2: Multilingual vision-language encoders with improved semantic understanding, localization, and dense features. arXiv preprint arXiv:2502.14786, 2025.

[20] W. Wei, C. Huang, L. Xia, and C. Zhang. Multi-modal self-supervised learning for recommendation. In Proceedings of the ACM Web Conference 2023, pages 790–800, 2023.

[21] X. Zhai, B. Mustafa, A. Kolesnikov, and L. Beyer. Sigmoid loss for language image pre-training. In Proceedings of the IEEE/CVF International Conference on Computer Vision, pages 11975–11986, 2023.

[22] X. Zhou. Mmrec: Simplifying multimodal recommendation. In Proceedings of the 5th ACM International Conference on Multimedia in Asia Workshops, pages 1–2, 2023.


---

# 2512.21526_选择性LLM引导正则化

[2512.21526](https://arxiv.org/abs/2512.21526)

# Selective LLM-Guided Regularization for Enhancing Recommendation Models

Shanglin Yang<sup>∗</sup>

Zhan Shi<sup>∗</sup>

kudoysl@gmail.com

ashi2@scu.edu

## Abstract

Large language models (LLMs) provide rich semantic priors and strong reasoning capabilities, making them promising auxiliary signals for recommendation. However, prevailing approaches ei ther deploy LLMs as standalone recommenders or apply global knowledge distillation, both of which sufer from inherent drawbacks. Standalone LLM recommenders are costly, biased, and un reliable across large regions of the user–item space, while global distillation forces the downstream model to imitate LLM predictions even when such guidance is inaccurate. Meanwhile, recent studies show that LLMs excel particularly in re-ranking and chal lenging scenarios, rather than uniformly across all contexts. We introduce Selective LLM-Guided Regularization (S-LLMR), a modelagnostic and computation-eficient framework that activates LLM based pairwise ranking supervision only when a trainable gating mechanism-informed by user history length, item popularity, and model uncertainty predicts the LLM to be reliable. All LLM scoring is done ofline, transferring knowledge without increasing inference cost. Experiments across multiple datasets show that this selective strategy consistently improves overall accuracy and yields substan tial gains in cold-start and long-tail regimes, outperforming global distillation baselines.

## Keywords

Recommender Systems, Large Language Models, Regularization, Cold-Start, Long-Tail, Knowledge Transfer

## ACM Reference Format:

Shanglin Yang and Zhan Shi. 2025. Selective LLM-Guided Regularization for Enhancing Recommendation Models. In . ACM, New York, NY, USA, 6 pages. https://doi.org/10.1145/nnnnnnn.nnnnnnn

## 1 Introduction

Recommendation systems underpin modern digital platforms by enabling content discovery, personalization, and user engagement across domains such as e-commerce, entertainment, and online media. Classical approaches—including collaborative filtering (CF), matrix factorization (MF), neural recommenders, and graph-based models achieve strong performance when user interaction histories are suficiently dense. However, their efectiveness deteriorates in sparse regimes, such as cold-start users, long-tail items, and scenarios where user preferences are weakly expressed.

Large language models (LLMs) have emerged as powerful auxiliary knowledge sources for recommendation, ofering rich semantic priors and strong reasoning capabilities that enable preference inference even from minimal user interaction data [10]. This makes them particularly promising in cold-start and sparsely observed regions where traditional recommenders tend to underperform. However, existing approaches to leveraging LLM signals remain fundamentally limited. Directly deploying LLMs as recommenders is prohibitively expensive and prone to issues such as position bias and hallucinated predictions. Meanwhile, global knowledge transfer methods [15, 20] require the downstream model to imitate LLM outputs uniformly across the entire user–item space, regardless of whether the LLM is reliable for a given instance. Recent attempts to distill LLM knowledge into classical models partially alleviate these issues, but they often depend on fine-tuned LLMs and still struggle to deliver consistent gains across diferent architectures or datasets.

<sup>Empirical</sup> <sup>motivation.</sup> Beyond high-level intuition, recent evaluations of LLM-based recommenders report localized strengths (notably on short histories and re-ranking) alongside systematic weaknesses including strong candidate position bias and occasional hallucinations [7]. These phenomena imply that LLM signals are contextually reliable rather than uniformly trustworthy. Our design follows directly from this evidence: instead of global imitation, we selectively invoke LLM guidance under reliability conditions predicted by a lightweight, learnable gating mechanism.

We propose Selective LLM-Guided Regularization (S-LLMR), a training framework that treats LLM knowledge as a conditional regularizer rather than a global supervisory signal. Instead of enforcing uniform imitation of LLM predictions, S-LLMR incorporates LLM-generated soft rankings only in regions where LLMs exhibit empirical advantages. This selective integration ensures that LLM guidance is beneficial rather than disruptive. We prompt an LLM using a compact representation of each user’s recent interaction history to generate soft relevance scores over candidate items. All scoring is performed ofline, introducing no inference-time overhead.A gating function controls whether LLM supervision is activated for a given user–item pair. This gate identifies regions where LLM signals are empirically reliable. With the gate ctive, we apply a weighted pairwise ranking loss that encourages the recommender to align its relative item ordering with LLM soft rankings, while automatically suppressing the influence of unreliable LLM predictions.

Extensive experiments across multiple datasets and diverse recommendation backbones show that S-LLMR consistently surpasses global distillation baselines, delivering substantial improvements in sparse regimes such as cold-start and long-tail scenarios. The contribution of our paper:

• We introduce a gated LLM-based regularization paradigm that selectively incorporates LLM signals, avoiding the draw backs of global distillation and remaining fully model-agnostic.

• We design S-LLMR, which combines a reliability-aware gat ing mechanism with an LLM-guided pairwise ranking loss for targeted knowledge transfer.

• Extensive experiments across multiple backbones show con sistent AUC improvements, with especially strong gains in cold-start and long-tail scenarios.

## 2 Related Work

Classical collaborative filtering (CF) forms the foundation of mod ern recommender systems. Matrix factorization (MF) [9] models user–item afinities through latent factors and has been widely adopted due to its scalability and strong generalization ability. Neu ral extensions such as Neural Collaborative Filtering (NCF) [4] leverage multilayer perceptrons to capture nonlinear preference interactions. Graph-based recommenders, including NGCF [23], LightGCN [3], and PinSage [24] leverage user–item signals through graph structures to improve high-order connectivity modeling.

Despite their strong performance in dense regimes, these mod els degrade significantly under cold-start [16] and long-tail [14] conditions.

Recent hybrid approaches such as UniSRec [5] unify textual and collaborative filtering signals to improve robustness, but still rely on large-scale metadata and do not exploit LLM reasoning. Existing approaches either use LLMs as direct recommenders, e.g., RankLLM [17], or distill LLM outputs into recommendation models in a global manner, such as SLMRec [11] and LLM-CF [19]. However, these methods do not account for the empirical finding that LLM signals are only locally reliable—being highly beneficial in semantic or sparse contexts, but noisy or misleading in others [6, 8].

To address this gap, we adopt a diferent perspective that LLM outputs should be treated as conditionally reliable auxiliary signals, rather than unconditional ground truth. Our work operationalizes this idea by introducing a selective LLM integration framework equipped with a lightweight, learnable gating mechanism to de termine when LLM guidance should be trusted. This allows the model to avoid global distillation while selectively leveraging LLM strengths in the contexts where they are most efective.

## 3 Method

<sub>As</sub> <sub>shown</sub> <sub>in</sub> <sub>Figure</sub> <sub>1,</sub> <sub>The</sub> Selective LLM-Guided Regulariza-<sup>tion</sup> <sup>for</sup> <sup>Recommendation</sup> (S-LLMR) is a model-agnostic training framework that selectively leverages large language models (LLMs) to regularize classical recommender models only in regions where LLM predictions are empirically reliable. Formally, given a user <sup>??</sup> and item <sup>??</sup>, a base recommender produces a predicted relevance score $s _ { u , i } ,$ while the LLM provides a soft preference score $s _ { u , i } ^ { L L M }$ Our goal is to integrate LLM guidance selectively through pairwise ranking supervision with an gating signal. There are three main modules included in the pipeline.

![](images/83f8ed84334d9430860d2cbbee8fc85a38ce9b28abe13028241a45f6038d7d48.jpg)  
Figure 1: Illustration of our selective LLM-guided regularization framework. Left: In the ofline phase, the LLM is prompted to produce soft relevance scores Right: In the training phase, a base recommender produces prediction scores, and the LLM signals are incorporated through a pairwise ranking regularizer whose contribution is controlled by a gating function.

## 3.1 LLM-Generated Soft Rankings

For each user <sup>??</sup>, we construct a succinct textual summary of the user’s recent interaction history and query an LLM with a prompt of the form:

“Given that the user recently interacted with items $\{ i _ { 1 } , i _ { 2 } , \dots \}$ , rank the following candidate items by their likelihood of matching the user’s preferences.”

The LLM returns a soft score $s _ { u , i } ^ { L L M } \in [ 0 , 1 ]$ for each candidate item, computed via normalized logits or temperature-scaled soft ranking. All LLM scoring is performed ofline, and therefore introduces no inference-time overhead. To improve supervision coverage in sparse regions, we additionally construct two synthetic candidate sets:

<sub>•</sub> Cold-start user candidates: <sub>Users</sub> <sub>with</sub> <sub>short</sub> <sub>histories</sub> (<=3) are paired with diverse sampled items to elicit LLM judgments for user-item combinations not present in training data.

<sub>•</sub> Long-tail items (bottom 10% popularity): <sub>Items</sub> <sub>whose</sub> popularity falls in the lowest 10% of the catalog are paired with sampled users so that the LLM can evaluate these underrepresented items and provide supervision where collaborative filtering is weakest.

These augmented LLM-scored pairs expand the ofline supervision table and cover precisely the settings where classical recommenders lack suficient signals.

## 3.2 LLM-Guided Pairwise Ranking Regularizer

Motivated LLM is better for reranking, compared to the llm directly loss. Given LLM soft scores, we impose an auxiliary pairwise ranking constraint that encourages the recommender to follow the ordering implied by the LLM whenever appropriate. For user <sup>??</sup>, if $s _ { u , i } ^ { L L M } \ > \ s _ { u , j } ^ { L L M }$ for two items (<sup>??,</sup> <sup>??</sup>), the model is encouraged to produce $s _ { u , i } > s _ { u , j }$ with a margin.

The pairwise LLM loss is defined as:

$$
\mathcal {L} _ {L L M} = \sum_ {(u, i, j) \in \mathcal {P}} \alpha_ {u, i, j} \max \bigl (0, m - (s _ {u, i} - s _ {u, j}) \bigr),
$$

where $\alpha _ { u , i , j }$ is a selective gating weight defined later.

User-consistent pair construction. To ensure semantic alignment, pairs are constructed within individual users. In each batch, we sample one or more users, extract items associated with those users, filter valid LLM scores, sort them by LLM ranking, and form ordered pairs (<sup>??,</sup> <sup>??</sup> ) where $s _ { u , i } ^ { L L M } > s _ { u , j } ^ { L L M }$ . This avoids mixing signals from unrelated users.

User-consistent pair construction. Because batches may contain varying numbers of users or valid LLM entries, we employ an adaptive strategy: given a target maximum of <sup>??</sup> pairs, the efective number $\tilde { K }$ is adjusted based on batch structure. The algorithm selects up to <sup>??˜</sup> highest-confidence pairs ranked by their LLM score diference, ensuring (i) at least one pair when possible, and (ii) avoidance of over-regularization.

Overall, this regularizer enables selective, reliability-aware knowl edge transfer: the recommender follows LLM rankings when they are trustworthy, while naturally resisting noisy or inconsistent supervision.

## 3.3 Selective Gating Mechanism

LLM supervision is not uniformly reliable. We therefore define a per-pair gate $\alpha _ { u , i } \in [ 0 , 1 ]$ that scales the contribution of the LLM regularizer.

Signals. We compute: (i) a cold-start indicator $\mathrm { C o l d } ( u ) = \mathbb { 1 } \left[ | \mathcal { H } ( u ) | < \right]$ ${ \tau _ { u } } ] , ( \mathrm { i i } )$ a long-tail indicator Tai $ { \lvert { ( i ) } \ = \ \mathbb { 1 } \left[  { \mathrm { p o p } } ( i ) \ < \ \tau _ { i } \right] }$ , and (iii) a continuous uncertainty score $q _ { u , i } \in [ 0 , 1 ]$ from the base model $( \mathrm { e . g . }$ predictive entropy or ensemble variance normalized to [0<sup>,</sup> 1]).

Learnable gate. Let $z _ { u , i } = \left[ \mathrm { C o l d } ( u ) , \mathrm { T a i l } ( i ) , q _ { u , i } \right] \in \mathbb { R } ^ { 3 }$ . We use a one-layer gating network

$$
\alpha_ {u, i} = \sigma \big (\mathbf {w} ^ {\top} z _ {u, i} + b \big),
$$

with parameters $\theta _ { g } = \{ \mathbf { w } , b \}$ learned jointly by back-propagation from the full objective (Sec. 3.4). For pairwise supervision, we set $\begin{array} { r } { \alpha _ { u , i , j } = \frac { 1 } { 2 } ( \alpha _ { u , i } + \alpha _ { u , j } ) } \end{array}$

Uncertainty instantiations. We consider (a) confidence-based $q _ { u , i } =$ 1 − max?? <sup>??</sup>?? (<sup>??</sup> |<sup>??, ??</sup>), (b) entropy-based $q _ { u , i } \ = \ \mathrm { H } ( p _ { \theta } ( \cdot | u , i ) )$ , or (c) dropout/ensemble variance. We select the best on validation.

The gating parameters $\theta _ { g }$ are learned jointly with the backbone through back-propagation from the LLM regularization loss. When LLM-guided pairs reduce the hinge loss, gradients increase $\alpha _ { u , i } ;$ when LLM signals are unhelpful, the gate is driven downward. This allows the model to automatically learn when LLM supervision is reliable without manual thresholds—focusing LLM influence on cold-start, long-tail, and high-uncertainty cases.

<div class="mineru-algorithm" style="white-space: pre-wrap; font-family:monospace;">
Algorithm 1 S-LLMR Training with Learnable Gating
Require: Base model $\theta$, gating params $\theta_g$, LLM table T_LLM, margins $m$, weights $\lambda$
1: while not converged do
2:    Sample minibatch of users $\mathcal{B}$ and their interactions
3:    for each $u \in \mathcal{B}$ do
4:    Compute base scores $s_{u,i}$ for items in batch
5:    Build user-consistent ordered pairs $\mathcal{P}_u = \{(i,j) : s_{u,i}^{\text{LLM}} &gt; s_{u,j}^{\text{LLM}}\}$ from T_LLM
6:    For each $(u,i)$ compute signals: Cold $(u)$, Tail $(i)$, $q_{u,i}$
7:    Gate: $\alpha_{u,i} = \sigma(\mathbf{w}^\top[\text{Cold}(u),\text{Tail}(i),q_{u,i}] + b)$
8:    end for
9:    $\mathcal{L}_{\text{rec}} \leftarrow$ base loss (e.g., BCE/BPR/InfoNCE)
10:    $\mathcal{L}_{\text{LLM}} \leftarrow \sum_{(u,i,j) \in \cup_u \mathcal{P}_u} \frac{\alpha_{u,i} + \alpha_{u,j}}{2} \cdot \max(0, m - (s_{u,i} - s_{u,j}))$
11:    Update $\theta, \theta_g$ by SGD on $\mathcal{L} = \mathcal{L}_{\text{rec}} + \lambda \mathcal{L}_{\text{LLM}}$
12: end while
</div>

## 3.4 Training Objective and Optimization Procedure

Algorithm 1 summarizes the full optimization procedure, including the construction of user-consistent LLM ranking pairs, computation of gating signals, and joint gradient updates of the base recommender and gating parameters. This design ensures that LLM knowledge is injected in a targeted and reliability-aware manner without interfering with the core training dynamics of the underlying model. The full training objective is:

$$
\mathcal {L} = \mathcal {L} _ {r e c} + \lambda \mathcal {L} _ {L L M},
$$

with <sup>??</sup> controlling the strength of the regularizer.

## 4 Experimental Setup

## 4.1 Backbone Models

To evaluate the model-agnostic nature of S-LLMR, we integrate it with six widely adopted and architecturally diverse recommendation backbones: DeepFM [1], xDeepFM [12], AutoInt [18], DCNv1 [21], DCNv2 [22], and DIN [25]. These models span a broad spectrum of interaction modeling strategies, including factorization-machine style feature crossing (DeepFM), vector-wise compressed interactions (xDeepFM), self-attentive feature learning (AutoInt), explicit cross layers (DCNv1/DCNv2), and attention over user behavior sequences (DIN). This diversity enables a comprehensive assessment of how selectively injected LLM signals generalize across diferent inductive biases.

To contextualize S-LLMR within the landscape of LLM-assisted recommendation, we compare against three representative paradigms:

• <sup>KD</sup> <sup>Distillation</sup> <sup>Baseline</sup> Following prior work [10, 15],the soft logits from a fine-tuned LLaMA2-7B model into each backbone, representing the standard global LLM-to-recommender imitation approach.

<sub>•</sub> KAR (Knowledge-Augmented Recommendation) <sub>KAR</sub> [13] aligns user and item representations with LLM-derived open-world knowledge, capturing the representation-enrichment paradigm of using LLMs in recommendation.

• <sup>LLM-CF</sup> LLM-CF [20] distills LLM world knowledge and reasoning ability into collaborative filtering, formulating

Table 1: Dataset statistics for the three Amazon domains.

<table><tr><td>Metric</td><td>Sports</td><td>Beauty</td><td>Toys</td></tr><tr><td>#Users</td><td>35,598</td><td>22,363</td><td>19,412</td></tr><tr><td>#Items</td><td>18,357</td><td>12,101</td><td>11,924</td></tr><tr><td>#Reviews</td><td>379,086</td><td>262,826</td><td>218,722</td></tr><tr><td rowspan="2">Cold-start interactions(% of interactions)</td><td>190,756</td><td>119,854</td><td>103,314</td></tr><tr><td>50.3%</td><td>45.6%</td><td>47.2%</td></tr><tr><td rowspan="2">Long-tail items(% of items)</td><td>3,659</td><td>2,400</td><td>2,326</td></tr><tr><td>19.9%</td><td>19.8%</td><td>19.5%</td></tr></table>

LLM-derived semantic signals as soft preference labels. This approach represents the state of the art in LLM-enhanced CF models.

Together, these baselines cover the three dominant LLM-forrecommendation paradigms: global distillation, representation alignment, and LLM-assisted collaborative filtering. Our comparison highlights the conceptual distinction and empirical advantages of selective over global LLM integration.

## 4.2 Datasets

We evaluate S-LLMR on three domains of the Amazon Review dataset [2], consistent with widely used recommendation bench marks. Dataset statistics are shown in Table 1. We use the <sup>Sports</sup> & Outdoors<sub>,</sub> Beauty<sub>,</sub> <sub>and</sub> Toys & Games <sub>subsets.</sub>

Across all domains, the data exhibit significant sparsity: nearly half of all interactions originate from cold-start users, and roughly 20% of items fall into the long-tail. These characteristics make the datasets particularly suitable for evaluating algorithms designed to improve performance in sparse regimes—precisely where LLM based semantic guidance is expected to be most beneficial.

## 4.3 Ofline LLM Scoring Pipeline

To obtain LLM-derived soft preference signals without adding inference-time overhead, we generate all scores $s _ { u , i } ^ { L L M }$ ofline through a lightweight pipeline. For each user <sup>??</sup>, we extract a recent history $\mathcal { H } _ { L } ( u )$ (last $L = 1 0$ interactions) and sample <sup>??</sup> candidate items from a top-<sup>??</sup> popularity pool. Each tuple $( u , \mathcal { H } _ { L } ( u ) , C ( u ) )$ is converted into a concise natural-language prompt and sent to <sup>GPT-4o-mini</sup>, which returns structured (item\_id<sup>,</sup> score) pairs in [0<sup>,</sup> 1]. Returned scores are normalized, missing values default to 0<sup>.</sup>5, and all results are stored as a lookup table $( \bar { u } , i ) \mapsto s _ { u , i } ^ { L L M }$ . During training, these ofline scores are used exclusively by the selective regularizer and never afect the base model’s loss or inference cost. This design provides flexible control over the number of scored users and can didates, enabling an eficient balance between LLM query cost and supervision coverage.

## 4.4 Training Protocol

All models are trained using the Adam optimizer with a learning rate of $1 0 ^ { - 3 } :$ , a batch size of 128, and an embedding dimension of 64, following common practice in CTR and implicit-feedback recommendation. For Selective-LLM-Reg, we set the regularization weight to $\lambda = 0 . 1$ , and select the final value based on validation

Table 2: AUC performance across three Amazon domains using six backbone architectures. For each domain, the highest AUC within a backbone group is bolded. Across all models and datasets, S-LLMR consistently achieves the strongest performance.

<table><tr><td rowspan="2">Backbone</td><td rowspan="2">Framework</td><td colspan="3">AUC↑</td></tr><tr><td>Sports</td><td>Beauty</td><td>Toys</td></tr><tr><td rowspan="5">DeepFM</td><td>None</td><td>0.7990</td><td>0.7853</td><td>0.7681</td></tr><tr><td>KD</td><td>0.8043</td><td>0.7959</td><td>0.7713</td></tr><tr><td>KAR</td><td>0.7991</td><td>0.7870</td><td>0.7698</td></tr><tr><td>LLM-CF</td><td>0.8137</td><td>0.8044</td><td>0.7881</td></tr><tr><td>Ours</td><td>0.8176</td><td>0.8101</td><td>0.7961</td></tr><tr><td rowspan="5">xDeepFM</td><td>None</td><td>0.8158</td><td>0.8065</td><td>0.7836</td></tr><tr><td>KD</td><td>0.8169</td><td>0.8104</td><td>0.7865</td></tr><tr><td>KAR</td><td>0.8161</td><td>0.8101</td><td>0.7898</td></tr><tr><td>LLM-CF</td><td>0.8196</td><td>0.8113</td><td>0.7947</td></tr><tr><td>Ours</td><td>0.8240</td><td>0.8183</td><td>0.7985</td></tr><tr><td rowspan="5">AutoInt</td><td>None</td><td>0.8003</td><td>0.7949</td><td>0.7630</td></tr><tr><td>KD</td><td>0.8012</td><td>0.7961</td><td>0.7635</td></tr><tr><td>KAR</td><td>0.8039</td><td>0.7939</td><td>0.7683</td></tr><tr><td>LLM-CF</td><td>0.8088</td><td>0.8090</td><td>0.7754</td></tr><tr><td>Ours</td><td>0.8161</td><td>0.8145</td><td>0.7849</td></tr><tr><td rowspan="5">DCNv1</td><td>None</td><td>0.8023</td><td>0.8146</td><td>0.7621</td></tr><tr><td>KD</td><td>0.8040</td><td>0.8147</td><td>0.7652</td></tr><tr><td>KAR</td><td>0.8024</td><td>0.8165</td><td>0.7651</td></tr><tr><td>LLM-CF</td><td>0.8092</td><td>0.8182</td><td>0.7702</td></tr><tr><td>Ours</td><td>0.8190</td><td>0.8189</td><td>0.7960</td></tr><tr><td rowspan="5">DCNv2</td><td>None</td><td>0.8110</td><td>0.8028</td><td>0.7774</td></tr><tr><td>KD</td><td>0.8112</td><td>0.8057</td><td>0.7827</td></tr><tr><td>KAR</td><td>0.8087</td><td>0.8003</td><td>0.7759</td></tr><tr><td>LLM-CF</td><td>0.8131</td><td>0.8033</td><td>0.7812</td></tr><tr><td>Ours</td><td>0.8150</td><td>0.8177</td><td>0.7927</td></tr><tr><td rowspan="5">DIN</td><td>None</td><td>0.7986</td><td>0.7861</td><td>0.7586</td></tr><tr><td>KD</td><td>0.8023</td><td>0.7934</td><td>0.7652</td></tr><tr><td>KAR</td><td>0.7971</td><td>0.7861</td><td>0.7620</td></tr><tr><td>LLM-CF</td><td>0.8089</td><td>0.7967</td><td>0.7783</td></tr><tr><td>Ours</td><td>0.8100</td><td>0.8010</td><td>0.7829</td></tr></table>

AUC. No additional hyperparameter tuning is performed unless explicitly noted.  
![](images/6342e371ad4a5ce49fc193eff7e6f0a43bea4feb49af66e5a89cb480fab812bc.jpg)  
Figure 2: AUC improvements in cold-start and long-tail regimes across backbones. S-LLMR delivers the strongest boosts for cold-start users and long-tail items—often exceeding generalrelative improvement.

Table 3: Ablation study on DCNv2: We compare global vs. gated LLM regularization, and pointwise vs. pairwise LLM supervision.

<table><tr><td rowspan="2">Method</td><td colspan="3">Sports</td><td colspan="3">Beauty</td><td colspan="3">Toys</td></tr><tr><td>Overall</td><td>Cold</td><td>LongTail</td><td>Overall</td><td>Cold</td><td>LongTail</td><td>Overall</td><td>Cold</td><td>LongTail</td></tr><tr><td colspan="10">Global vs. Gated LLM Regularization</td></tr><tr><td>DCNv2</td><td>0.811</td><td>0.8140</td><td>0.7677</td><td>0.8028</td><td>0.8006</td><td>0.7702</td><td>0.7774</td><td>0.7868</td><td>0.7402</td></tr><tr><td>DCN + Global LLM Regularization</td><td>0.8114</td><td>0.8140</td><td>0.7640</td><td>0.7911</td><td>0.7797</td><td>0.7330</td><td>0.7887</td><td>0.7858</td><td>0.7390</td></tr><tr><td>DCN + Gated LLM Regularization (Ours)</td><td>0.8150</td><td>0.8170</td><td>0.7877</td><td>0.8177</td><td>0.8063</td><td>0.7716</td><td>0.7927</td><td>0.7917</td><td>0.7502</td></tr><tr><td colspan="10">Pointwise vs. Pairwise LLM Supervision</td></tr><tr><td>DCNv2 (Backbone)</td><td>0.811</td><td>0.8140</td><td>0.7677</td><td>0.8028</td><td>0.8006</td><td>0.7702</td><td>0.7774</td><td>0.7868</td><td>0.7402</td></tr><tr><td>DCN + LLM Pointwise MSE</td><td>0.8069</td><td>0.8119</td><td>0.7571</td><td>0.7999</td><td>0.7922</td><td>0.7445</td><td>0.7705</td><td>0.7671</td><td>0.7391</td></tr><tr><td>DCN + Pairwise Ranking (Ours)</td><td>0.8150</td><td>0.8170</td><td>0.7877</td><td>0.8177</td><td>0.8063</td><td>0.7716</td><td>0.7927</td><td>0.7917</td><td>0.7502</td></tr></table>

## 4.5 Evaluation Protocol

We adopt the standard full-ranking evaluation setting, where each test interaction is ranked against all items that the user has not interacted with in the training or validation sets. Since our goal is to assess both global predictive accuracy and robustness in sparse regions, we report AUC as the sole evaluation metric.To further evaluate model performance under challenging conditions, we report AUC on two key sub-populations:

• <sup>Cold-start</sup> <sup>users</sup>: test interactions belonging to users with fewer than <sup>??</sup> historical interactions, i.e., |H (<sup>??</sup>)| <sup>< ??</sup>. We set <sup>??</sup> = 3 in our experiments.

• <sup>Long-tail</sup> <sup>items</sup>: items in the bottom 20% of the popularity distribution based on training data. We first identify long-tail item IDs from the training set and then select the correspond ing interactions from the test set to form the long-tail subset.

These stratified subsets isolate the efect of S-LLMR in sparse and semantically challenging regimes, enabling a clearer understanding of how selective LLM guidance improves recommendation quality under conditions where traditional models typically struggle.

## 5 Results

Our results show that S-LLMR consistently improves AUC across all backbones and domains, delivers the largest gains in cold-start and long-tail scenarios.

## 5.1 Overall Performance Across Backbones

The overall performance are shown in Table 2. Across all six backbone models including DeepFM, xDeepFM, AutoInt, DCNv1, DCNv2, and DIN. S-LLMR achieves the strongest AUC scores on every Amazon domain. The improvements over non-LLM baselines (None, KD, KAR) are consistent and sizable, and our method further surpasses the LLM-CF approach by margins of 0<sup>.</sup>003–0<sup>.</sup>01 AUC depending on the model and dataset. Architectures that struggle more with seman tic sparsity, such as AutoInt and DCNv1, exhibit particularly large gains: AUC improvements reach 0<sup>.</sup>007–0<sup>.</sup>01 on Sports and exceed 0<sup>.</sup>02 on the Toys domain. These results validate that selectively in corporating LLM signals rather than distilling them globally allows the recommender to capitalize on LLM strengths while avoiding the noise and positional bias present in many LLM outputs, yield ing reliable improvements across heterogeneous architectures and domains.

## 5.2 Efectiveness in Sparse and Hard Regimes

As shwon in Figure 2. Across all datasets, S-LLMR delivers the strongest boosts for cold-start users and long-tail items—often exceeding generalrelative improvement. This pattern confirms that the selective gating mechanism efectively activates LLM guidance where collaborative-filtering signals are weakest. Cold-start gains demonstrate that the method leverages LLM semantic priors to compensate for short interaction histories, while long-tail gains highlight improved robustness on niche items that lack suficient popularity-based signals. Together, these results indicate that the primary benefit of S-LLMR lies in its ability to reinforce the recommender precisely in the regions where traditional models fail, rather than merely improving global accuracy.

## 5.3 Ablation Study on Module Efectiveness

Across all three domains and evaluation subsets shown in Table 3, the ablations demonstrate that our gated selective LLM-guided regularization is the only strategy that consistently improves performance in both overall and sparse regimes. Applying LLM loss globally often degrades long-tail accuracy and substantially harms Beauty-domain performance, highlighting that LLM predictions are not uniformly reliable. Pointwise (BCE/MSE) LLM supervision also fails to deliver meaningful improvements and frequently underperforms the backbone. In contrast, our selective gating mechanism combined with a pairwise ranking loss yields the strongest gains across all settings—most notably on cold-start and long-tail subsets, where AUC improvements reach +0.02 to +0.04 over the backbone and up to +0.05 over global or pointwise LLM methods. These results confirm that (i) LLM signals must be used selectively, and (ii) ranking-based supervision is the most efective way to transfer LLM semantic knowledge without amplifying LLM noise.

## 6 Conclusion

This paper introduced S-LLMR, a selective LLM-guided regularization framework that integrates LLM semantic knowledge into classical recommendation models in a reliability-aware manner. Rather than imitating LLM predictions globally, our method activates LLM-based pairwise ranking supervision only in regions where LLMs exhibit clear empirical advantages—cold-start users, long-tail items, and high-uncertainty predictions. Extensive experiments across six backbone recommenders and three Amazon domains demonstrate that S-LLMR not only improves overall AUC but yields particularly large gains in sparse and semantically challenging regimes, confirming that LLM signals are most beneficial when applied selectively. Our ablations further show that global LLM loss can degrade performance, whereas gated pairwise regularization consistently strengthens model robustness. Overall, S-LLMR pro vides a simple, model-agnostic, and computation-eficient approach for leveraging LLM knowledge to bridge long-standing weaknesses in collaborative filtering, ofering a promising direction for future reliability-aware LLM–recommender integration.

## Acknowledgments

To Robert, for the bagels and explaining CMYK and color spaces.

## References

[1] Huifeng Guo, Ruiming Tang, Yunming Ye, Zhenguo Li, and Xiuqiang He. 2017. DeepFM: A Factorization-Machine Based Neural Network for CTR Prediction. In IJCAI.

[2] Ruining He and Julian McAuley. 2016. Ups and Downs: Modeling the Visual Evo lution of Fashion Trends with One-Class Collaborative Filtering. In Proceedings of the 25th International Conference on World Wide Web. 507–517.

[3] Xiangnan He, Kuan Deng, Xiang Wang, Yan Li, Yongdong Zhang, and Meng Wang. 2020. Lightgcn: Simplifying and powering graph convolution network for recommendation. In Proceedings of the 43rd International ACM SIGIR conference on research and development in Information Retrieval. 639–648.

[4] Xiangnan He, Lizi Liao, Hanwang Zhang, Liqiang Nie, Xia Hu, and Tat-Seng Chua. 2017. Neural collaborative filtering. In Proceedings of the 26th international conference on world wide web. 173–182.

[5] Yupeng Hou, Shanlei Mu, Wayne Xin Zhao, Yaliang Li, Bolin Ding, and Ji-Rong Wen. 2022. Towards universal sequence representation learning for recommender systems. In Proceedings of the 28th ACM SIGKDD conference on knowledge discovery and data mining. 585–593.

[6] Lei Huang et al. 2023. A Survey on Hallucination in Large Language Models. arXiv:2311.05232 (2023).

[7] Chumeng Jiang, Jiayin Wang, Weizhi Ma, Charles LA Clarke, Shuai Wang, Chuhan Wu, and Min Zhang. 2025. Beyond Utility: Evaluating LLM as Recommender. In Proceedings of the ACM on Web Conference 2025. 3850–3862.

[8] Xiang Jiang et al. 2024. Beyond Utility: Evaluating LLM as Recommender. arXiv:2411.00331 (2024).

[9] Yehuda Koren, Robert Bell, and Chris Volinsky. 2009. Matrix factorization tech niques for recommender systems. Computer 42, 8 (2009), 30–37.

[10] Lei Li, Zhenhua Sun, et al. 2023. LLM4Rec: Large Language Models for Recom mendation. arXiv preprint arXiv:2306.10997 (2023).

[11] Xinyu Li et al. 2025. SLMRec: Distilling Large Language Models into Small Models for Sequential Recommendation. ICLR (2025).

[12] Jianxun Lian, Xiaohuan Li, Yujing Zhang, Guangzhong Sun, and Xing Xie. 2018. xDeepFM: Combining Explicit and Implicit Feature Interactions for Recommender Systems. In KDD.

[13] Xi Lin, Bowen Du, et al. 2024. Towards Open-World Recommendation with Knowl edge Augmentation from Large Language Models. arXiv preprint arXiv:2306.10933 (2024).

[14] Jing Qin. 2021. A survey of long-tail item recommendation methods. Wireless Communications and Mobile Computing 2021, 1 (2021), 7536316.

[15] Kan Ren and et al. Zhang. 2024. LLM-Distill: Distilling Large Language Models into Recommendation Models. arXiv preprint arXiv:2402.03852 (2024).

[16] Martin Saveski and Amin Mantrach. 2014. Item cold-start recommendations: learning local collective embeddings. In Proceedings of the 8th ACM Conference on Recommender systems. 89–96.

[17] Sahel Sharifymoghaddam et al. 2025. RankLLM: A Python Package for Reranking with LLMs. SIGIR (2025).

[18] Weiping Song, Chence Shi, Zhiping Xiao, Zhijian Duan, Yewen Xu, Ming Zhang, and Jian Tang. 2019. AutoInt: Automatic Feature Interaction Learning via Self Attentive Neural Networks. In CIKM.

[19] Z. Sun et al. 2024. Large Language Models Enhanced Collaborative Filtering. arXiv:2403.17688 (2024).

[20] Zhongxiang Sun, Zihua Si, Xiaoxue Zang, Kai Zheng, Yang Song, Xiao Zhang, and Jun Xu. 2024. Large language models enhanced collaborative filtering. In Proceedings of the 33rd ACM International Conference on Information and Knowledge Management. 2178–2188.

[21] Ruoxi Wang, Bin Fu, Gang Fu, and Mingliang Wang. 2017. Deep & Cross Network for Ad Click Predictions. In ADKDD.

[22] Ruoxi Wang, Rakesh Shivanna, Derek Zhiyuan Cheng, Sagar Jain, Dong Lin, Michael Bendersky, and Marc Najork. 2021. DCN V2: Improved Deep & Cross Network and Practical Lessons for Web-scale Learning to Rank Systems. In WWW.

[23] Xiang Wang, Xiangnan He, Meng Wang, Fuli Feng, and Tat-Seng Chua. 2019. Neural graph collaborative filtering. In Proceedings of the 42nd international ACM SIGIR conference on Research and development in Information Retrieval. 165–174.

[24] Rex Ying, Ruining He, Kaifeng Chen, Pong Eksombatchai, William L Hamilton, and Jure Leskovec. 2018. Graph convolutional neural networks for web-scale recommender systems. In Proceedings of the 24th ACM SIGKDD international conference on knowledge discovery & data mining. 974–983.

[25] Guorui Zhou, Chengru Song, Xiaoqiang Zhu, Ying Fan Ma, Ying Yan, Xiangnan He, et al. 2018. Deep Interest Network for Click-Through Rate Prediction. In KDD.


---

# 2505.20773_冷启动推荐的知识引导检索增强生成

[2505.20773](https://arxiv.org/abs/2505.20773)

# Adaptive Candidate Retrieval with Dynamic Knowledge Graph Construction for Cold-Start Recommendation

Wooseong Yang<sup>1</sup>, Weizhi Zhang<sup>1</sup>, Yuqing Liu<sup>1</sup>, Yuwei Han<sup>1</sup>, Yu Wang<sup>1</sup>, Junhyun Lee<sup>2</sup>\*, Philip S. Yu<sup>1∗</sup> <sup>1</sup>University of Illinois Chicago <sup>2</sup>Korea University

## Abstract

The cold-start problem remains a critical challenge in real-world recommender systems, as new items with limited interaction data or insufficient information are frequently introduced. Despite recent advances leveraging external knowledge such as knowledge graphs (KGs) and large language models (LLMs), recommender systems still face challenges in practical environments. Static KGs are expensive to construct and quickly become outdated, while LLM-based methods depend on pre-filtered candidate lists due to limited context windows. To address these limitations, we propose ColdRAG, a retrieval-augmented framework that dynamically constructs a knowledge graph from raw metadata, extracts entities and relations to construct an updatable structure, and introduces LLM-guided multihop reasoning at inference time to retrieve and rank candidates without relying on prefiltered lists. Experiments across multiple benchmarks show that ColdRAG consistently outperforms strong seven baselines. Our implementation is available at https://github. com/WooseongYang/ColdRAG.

## 1 Introduction

In real-world recommender systems, cold-start items are routinely introduced with few or no interaction records and incomplete metadata. This lack of information prevents models from accurately estimating user preferences, resulting in poor recommendation quality, reduced user satisfaction, and ultimately revenue loss (Huang et al., 2023; Zhang et al., 2025). To tackle this challenge, recent works have explored two main directions: (i) KG–based methods that construct structured representations of the item catalog (Wang et al., 2019b; Guo et al., 2020), and (ii) LLM-based methods that leverage LLMs as training-free recommenders, typically prompting on user histories with a small set of candidate items (Sanner et al., 2023; Hou et al., 2024).

However, both directions face critical limitations in practical deployment (Lin et al., 2025). Static KGs are expensive to construct and maintain, and they quickly become outdated as items, attributes, and relations change (Wang et al., 2019a). Updating these graphs to reflect catalog changes typically requires substantial offline engineering and cannot keep up with real-time changes. LLM-based approaches, meanwhile, are usually formulated as re-rankers over a pre-filtered candidate set rather than as end-to-end retrieval systems (Hou et al., 2024). Because LLMs operate under bounded context windows and token budgets, only a curated subset of items and a truncated user history can be included in the prompt, necessitating a separate task-specific retrieval pipeline. While recent work introduces retrieval-aware prompting, its retrieval remains shallow, limited to keyword matching or single-hop similarity search, which still limits performance and reduces adaptability in dynamic coldstart settings (Liang et al., 2025; Kieu et al., 2025).

To address the above limitations, we introduce ColdRAG, a retrieval-augmented framework built around two key modules. The first module, Dynamic Knowledge Graph Construction, automatically builds and incrementally updates a domain graph from catalog fields (e.g., titles, descriptions, attributes, reviews), allowing the structure to evolve naturally as the catalog changes. The second module, Adaptive Candidate Retrieval over Knowledge Graph, removes the need for pre-filtered candidate lists by treating candidate generation as LLMguided, goal-directed traversal over the graph, assembling a compact, high-utility candidate set together with evidence paths that justify each recommendation. Empirically, ColdRAG consistently surpasses strong training-based and training-free baselines across diverse product domains with large performance gains.

Our contributions are threefold:

• We introduce a dynamic KG construction that automatically builds and incrementally updates the graph as items and relations evolve.

• We eliminate the unrealistic assumption that a curated candidate list is already in the LLM’s context window by integrating candidate retrieval with LLM-guided multi-hop reasoning.

• We demonstrate strong cold-start performance on multiple benchmarks and provide extensive analyses on component effectiveness, stability, and robustness.

## 2 Related Works

Cold-Start Recommendation The item coldstart problem arises when new items lack interaction history, motivating content-based and hybrid recommenders that rely on metadata or auxiliary signals to compensate for missing collaborative information. Representative training-based methods such as CLCRec (Wei et al., 2021) strengthen coldstart representations through contrastive alignment, while TDRO (Lin et al., 2024) improves robustness by accounting for temporal distribution shifts. Although effective, these approaches require training task-specific modules, limiting their flexibility when new items continually appear.

LLM-based Recommendation To address these limitations, recent work has explored training-free LLM-based recommendation as a natural fit for cold-start scenarios. Methods such as LLMRank (Hou et al., 2024), TaxRec (Liang et al., 2025), and KALM4Rec (Kieu et al., 2025) infer user preferences through prompting or lightweight retrieval, allowing them to handle new items without finetuning. However, due to the limited context window, these models rely on pre-filtered candidate lists or shallow keyword matching, which restricts semantic coverage and increases the risk of hallucination and unstable outputs. ColdRAG overcomes these issues by dynamically constructing a KG and performing multi-hop, evidence-grounded retrieval, providing structured semantic grounding that enables more reliable and adaptable zero-shot item cold-start recommendation.

## 3 Proposed Method

We present ColdRAG, a retrieval-augmented generation framework for cold-start recommendation.

ColdRAG equips an LLM with a dynamically constructed KG that enables semantic reasoning and adaptively builds candidate items for context-aware and controllable recommendation. The overall framework is illustrated in Figure 1. For the problem setting, we follow the sequential recommendation task, where each user u has an interaction history $H _ { u } = [ i _ { 1 } , i _ { 2 } , \dotsc , i _ { n - 1 } ]$ and the goal is to recommend the next item $i _ { n }$

## 3.1 Dynamic Knowledge Graph Construction 3.1.1 Item Profile Generation

Item metadata is a key source for constructing the knowledge graph, but it is often sparse, noisy, or inconsistently structured, making it difficult to extract meaningful semantics directly. To address this, ColdRAG leverages a LLM to denoise and enrich this information by using the model’s pretrained knowledge to fill informational gaps, producing concise, knowledge-grounded item profiles that capture each item’s essential semantics. For each item i, we define its metadata as $\mathbf { m } _ { i } =$ (title, description, attributes, review) and obtain the profile via the inline mapping $P _ { i } =$ $L L M ( p r o m p t ( \mathbf { m } _ { i } ) )$ . This process curates raw, unstructured metadata into fluent summaries that highlight key concepts such as genre, features, or notable entities (e.g., “action-adventure,” “Lara Croft”), forming a clean and standardized foundation for knowledge graph construction and downstream reasoning. The prompt used for this step is provided in Appendix D.1.

## 3.1.2 Knowledge Graph Generation

With enriched item profiles in place, ColdRAG organizes this information into a structured semantic graph by prompting the LLM to extract entities and relations, which creates a foundation for reasoning and retrieval. Given an item profile $P _ { i }$ , the LLM extracts entities, relations, and textual statements describing them, constructing a knowledge graph $\mathcal { G } = ( \mathcal { E } , \mathcal { R } )$ , where E denotes entities and R the relations linking them.

To be specific, for each item, the LLM extracts entities and relations, each paired with a naturallanguage description and an embedding for semantic retrieval. An entity $e \in { \mathcal { E } }$ is represented as $( e _ { \mathrm { n a m e } } , e _ { \mathrm { t y p e } } , e _ { \mathrm { d e s c } } , e _ { \mathrm { e m b } } )$ , where $e _ { \mathrm { n a m e } }$ is the entity title, $e _ { \mathrm { t y p e } }$ identifies its category (e.g., item, genre, feature), $e _ { \mathrm { d e s c } }$ provides its textual explanation, and $e _ { \mathrm { e m b } }$ is its vector embedding. A relation $r \in \mathcal { R }$ is represented as $( r _ { \mathrm { n a m e } } , r _ { \mathrm { d e s c } } , r _ { \mathrm { e m b } } )$ , where $r _ { \mathrm { n a m e } } = ( e _ { \mathrm { s r c } } , e _ { \mathrm { t g t } } )$ denotes the source-target entity pair, $r _ { \mathrm { d e s c } }$ describes their connection, and $r _ { \mathrm { e m b } }$ is its embedding used for scoring. For instance, as shown in Figure 1, the entity Tomb Raider is of type ’item’ and the description “groundbreaking actionadventure game . . . ”. A corresponding relation connects Tomb Raider to Lara Croft with the description “Lara Croft is the main character driving the player’s experience in Tomb Raider.”. This transformation organizes free-form text into an entitycentric graph structure, enabling fine-grained multihop reasoning over attribute-level connections. The prompt used is shown in Appendix D.2.

![](images/0656d6d0c99db7c076352b28d48f036a7d8bc8a93b81364f54b77dcd87d81788.jpg)  
Figure 1: Overview of the proposed ColdRAG framework. Given item metadata, an LLM generates item profiles, from which structured entities and relations form a knowledge graph dynamically. During inference, ColdRAG performs query-aware multi-hop reasoning over KG to adaptively retrieve candidate items and context, then composes prompts to generate recommendations.

The constructed graph is stored in a hybrid knowledge base: the graph topology (nodes and edges) and their textual descriptions are stored as structured files, while embeddings are indexed in a vector database (e.g., FAISS<sup>1</sup>) for efficient similarity search. Each textual description is encoded using the same pretrained embedding model, ensuring consistent semantic representations across all entities and relations; additional details are provided in Appendix F. This combination of structural traversal and semantic retrieval provides ColdRAG with evidence-grounded access to item knowledge during recommendation.

## 3.2 Adaptive Candidate Retrieval over Knowledge Graph

Once the knowledge graph G has been constructed, ColdRAG uses it to adaptively identify candidate items aligned with a user’s current interests. Given a user query that includes both task instructions and the interaction history $H _ { u } ,$ , the system begins by locating the parts of the graph most relevant to the user. The titles of items in $H _ { u }$ are used as keyword anchors and embedded with the same pretrained embedding model from graph construction. These embeddings are then matched against stored entity embeddings using cosine similarity to locate the most semantically similar nodes. The matched entities initialize the frontier $\mathcal { F } _ { 0 }$ , representing the user’s current semantic context in the graph. ColdRAG then performs iterative query-aware multihop reasoning guided by the LLM. At each step t, all outgoing edges from the current frontier $\mathcal { F } _ { t }$ are scored by the LLM according to their relevance to the user history, where $s _ { r } = L L M ( r _ { \mathrm { d e s c } } , H _ { u } )$ and $s _ { r } \in [ 0 , 1 0 ]$ measures the semantic alignment between the relation description $r _ { \mathrm { d e s c } }$ and the user’s interests. Edges with $s _ { r } \geq \lambda$ are retained, and their target nodes form the next frontier:

$$
\mathcal {F} _ {t + 1} = \left\{e ^ {\prime} \mid (e, e ^ {\prime}, r _ {\text { desc }}) \in \mathcal {R}, s _ {r} \geq \lambda \right\}.
$$

When a target node corresponds to an item, it is added to a temporary candidate pool $\widetilde { \mathcal { C } } _ { u }$ along with its associated descriptions $\widetilde { \tau _ { u } }$ . Traversal continues until $| \widetilde { \mathcal { C } } _ { u } |$ reaches the predefined maximum pool size $\theta _ { \mathrm { p o o l } }$ . Finally, the LLM aggregates edge scores to rank the retrieved items and selects the top $\theta _ { \mathrm { t o p } }$ as the final candidate set $\mathcal { C } _ { u }$ , with their textual evidence forming the final contextual input $\mathcal { T } _ { u }$ . The example prompt is shown in Appendix D.3.

## 3.3 Retrieval-augmented Recommendation

In the final stage, ColdRAG generates recommendations using the candidate item set $\mathcal { C } _ { u }$ and contextual text block $\mathcal { T } _ { u }$ . The contextual text, composed of natural-language descriptions of relevant entities and relations from the knowledge graph, serves as the system prompt that provides semantic grounding. The candidate set is integrated into the user query to form the user prompt $Q _ { u }$ , which expresses user preferences and specifies the desired top-k recommendations within the retrieved candidates.

The LLM then generates ranked outputs conditioned on both prompts:

$$
\hat {\mathcal {Y}} _ {u} = \operatorname{ParseTopK} \left(L L M \left(\mathcal {T} _ {u}, Q _ {u}, k\right)\right).
$$

Here, $L L M ( T _ { u } , Q _ { u } , k )$ denotes generation with topk instruction $( \mathrm { e . g . }$ , “Recommend the top-k items among the given candidate list, based on the user’s history and retrieved context”), and ParseTopK extracts top-k ranked item titles from the output. ColdRAG’s ability to accommodate new items is further discussed in Appendix A.

Table 1: Summary of dataset and constructed knowledge graph statistics.

<table><tr><td>Dataset</td><td>#Interactions</td><td>#Items</td><td>#Users</td><td>#Nodes</td><td>#Edges</td></tr><tr><td>Games</td><td>45,106</td><td>2,027</td><td>2,096</td><td>15,048</td><td>29,023</td></tr><tr><td>Toys</td><td>332,055</td><td>12,342</td><td>20,390</td><td>58,096</td><td>132,229</td></tr><tr><td>Office</td><td>233,738</td><td>6,107</td><td>15,302</td><td>42,769</td><td>75,053</td></tr></table>

## 4 Experiments

We conduct comprehensive experiments to evaluate the effectiveness of ColdRAG in item cold-start recommendation. Our analysis is organized around the following research questions:

• RQ1: Does ColdRAG effectively address the item cold-start recommendation problem?

• RQ2: How effective is the Dynamic Knowledge Graph Construction?

• RQ3: How does Adaptive Candidate Retrieval enhance recommendation performance?

• RQ4: Does ColdRAG exhibit stable and consistent generation across runs?

• RQ5: Does ColdRAG reduce hallucination and avoid out-of-domain recommendations?

## 4.1 Experimental Setup

## 4.1.1 Datasets

We evaluate ColdRAG on three domains from the Amazon Review dataset (Ni et al., 2019): Games, Toys, and Office, which represent diverse product types and interaction patterns. We apply core filtering with a threshold of 15 for Games and 10 for Toys and $O f f i c e ,$ , retaining users and items that meet the minimum interaction count. To simulate item cold-start scenarios, the least frequent 10% of items in each dataset are designated as cold items. Following the sequential recommendation setting, each user’s interactions are treated as a sequence, where the last item is held out for testing under the leave-one-out protocol (Sun et al., 2019; Hou et al., 2022). From each domain, we sample 500 user sequences that end with a cold item; the preceding n−1 items serve as input and the final item as the test target. For training-based baselines, these 500 cold-item sequences are used for testing, and all remaining sequences form the training set, ensuring consistent evaluation between training-based and training-free settings. Dataset and knowledge graph statistics are summarized in Table 1.

## 4.1.2 Baselines

We compare ColdRAG with representative baselines spanning both training-based and trainingfree paradigms. Among training-based models, UniSRec (Hou et al., 2022) fine-tunes a universal sequence encoder with contrastive objectives, CLCRec (Wei et al., 2021) trains a contrastive framework to preserve collaborative signals for cold items, and TDRO (Lin et al., 2024) applies distributionally robust optimization to handle temporal shifts. For training-free methods, we include a plain LLM that ranks randomly sampled candidates without retrieval grounding; LLM-Rank (Hou et al., 2024), which provides sequential (S), recency (R), and in-context (I) prompting variants for zero-shot re-ranking; TaxRec (Liang et al., 2025), which injects taxonomy cues to guide LLM reasoning; and KALM4Rec (Kieu et al., 2025), which uses keyword-level retrieval to support coldstart recommendation. Among the training-based baselines, UniSRec fine-tunes a pretrained model, whereas CLCRec and TDRO are trained from scratch. The remainings are training-free methods that operate entirely without parameter updates, relying on LLM inference for reasoning and retrieval. Together, they provide a broad comparison across representation learning, fine-tuning, and retrievalaugmented LLM paradigms.

Table 2: Comparison of Recall@10 and NDCG@10 (%) across three datasets. Our proposed ColdRAG is highlighted in gray. Best results are in bold and second-best baseline is underlined. All results are averaged over 5 runs and values are shown as percentages.

<table><tr><td rowspan="2"></td><td rowspan="2">Model</td><td rowspan="2">LLM</td><td colspan="2">Games</td><td colspan="2">Toys</td><td colspan="2">Office</td></tr><tr><td>Recall@10</td><td>NDCG@10</td><td>Recall@10</td><td>NDCG@10</td><td>Recall@10</td><td>NDCG@10</td></tr><tr><td rowspan="3">training-based</td><td>UniSRec</td><td>-</td><td>1.14</td><td>0.48</td><td>1.48</td><td>0.71</td><td>1.41</td><td>0.66</td></tr><tr><td>CLCRec</td><td>-</td><td>5.71</td><td>2.98</td><td>2.75</td><td>1.36</td><td>3.36</td><td>1.98</td></tr><tr><td>TDRO</td><td>-</td><td>6.61</td><td>4.21</td><td>2.64</td><td>1.31</td><td>3.79</td><td>2.14</td></tr><tr><td rowspan="14">training-free</td><td rowspan="2">LLM</td><td>GPT</td><td>3.48</td><td>1.52</td><td>1.32</td><td>0.60</td><td>3.16</td><td>1.34</td></tr><tr><td>Qwen</td><td>9.24</td><td>3.89</td><td>0.56</td><td>0.33</td><td>3.30</td><td>1.63</td></tr><tr><td rowspan="2">LLMRank (S)</td><td>GPT</td><td>4.62</td><td>1.94</td><td>1.36</td><td>0.58</td><td>3.80</td><td>1.63</td></tr><tr><td>Qwen</td><td>10.92</td><td>5.14</td><td>1.01</td><td>0.65</td><td>3.67</td><td>1.87</td></tr><tr><td rowspan="2">LLMRank (R)</td><td>GPT</td><td>8.86</td><td>4.25</td><td>1.13</td><td>0.72</td><td>4.20</td><td>2.23</td></tr><tr><td>Qwen</td><td>10.98</td><td>5.39</td><td>1.20</td><td>0.71</td><td>2.27</td><td>1.42</td></tr><tr><td rowspan="2">LLMRank (I)</td><td>GPT</td><td>6.20</td><td>3.78</td><td>1.20</td><td>0.70</td><td>4.02</td><td>1.90</td></tr><tr><td>Qwen</td><td>9.08</td><td>4.88</td><td>1.24</td><td>0.87</td><td>4.07</td><td>2.39</td></tr><tr><td rowspan="2">TaxRec</td><td>GPT</td><td>3.75</td><td>1.78</td><td>0.60</td><td>0.34</td><td>2.20</td><td>0.96</td></tr><tr><td>Qwen</td><td>7.61</td><td>4.63</td><td>0.80</td><td>0.59</td><td>3.81</td><td>2.12</td></tr><tr><td rowspan="2">KALM4Rec</td><td>GPT</td><td>8.50</td><td>4.14</td><td>4.26</td><td>2.13</td><td>3.43</td><td>1.71</td></tr><tr><td>Qwen</td><td>7.27</td><td>2.62</td><td>3.29</td><td>1.90</td><td>2.07</td><td>0.58</td></tr><tr><td rowspan="2">ColdRAG</td><td>GPT</td><td>12.38</td><td>4.37</td><td>5.40</td><td>2.29</td><td>8.60</td><td>3.26</td></tr><tr><td>Qwen</td><td>19.57</td><td>6.50</td><td>4.10</td><td>1.98</td><td>9.40</td><td>3.92</td></tr><tr><td colspan="3">Improvement</td><td>78.22%</td><td>20.54%</td><td>26.76%</td><td>7.42%</td><td>123.81%</td><td>63.85%</td></tr></table>

## 4.1.3 Evaluation Metrics

We evaluate recommendation performance using two standard metrics widely adopted in cold-start tasks: Recall@k and NDCG@k, following prior work (Hou et al., 2022; Wei et al., 2021; Liang et al., 2025). All results are reported at k = 10.

## 4.1.4 Implementation Details

ColdRAG and all training-free baselines are implemented using two LLMs: gpt-4o-mini<sup>2</sup> and Qwen2.5-32b-instruct<sup>3</sup> (“GPT” and “Qwen” in Table 2). Using two distinct LLM backbones verifies that ColdRAG’s effectiveness generalizes beyond a single architecture. We set the edge scoring threshold to λ = 7, the candidate pool size to $\theta _ { \mathrm { p o o l } } = 3 0 0$ and the final candidate set size to $\theta _ { \mathrm { t o p } } = 1 0 0 $ , consistent with Section 3. All experiments are repeated five times, and average results are reported for stability and reproducibility. Additional implementation details appear in Appendix F.

## 4.2 Results

## 4.2.1 Overall Performance (RQ1)

Table 2 compares ColdRAG with all baselines on the Games, Toys, and Office datasets. ColdRAG consistently achieves the best results across all metrics and domains, outperforming both trainingbased and training-free baselines. It improves Recall@10 by +78.6%, +26.76%, and +123.81% over the strongest baselines on Games, Toys, and Office, respectively. The larger gains in Recall over NDCG indicate that ColdRAG is effective in both identifying and ranking relevant items, but its main strength lies in retrieving correct candidates into the top set. Among training-based models, TDRO shows the best performance but still falls short of ColdRAG, showing that even robustly trained models struggle to generalize under sparsity. ColdRAG’s retrieval-augmented design instead captures fine-grained semantic relations through LLMguided multi-hop reasoning, yielding better coldstart adaptability. Within the training-free methods, LLM and LLMRank perform moderately but rely on fixed candidate lists, restricting contextual exploration. KALM4Rec enriches prompts via keyword retrieval yet remains less strong than ColdRAG, whose KG-based retrieval enables deeper reasoning over semantically linked concepts beyond shallow keyword matching. Overall, ColdRAG’s consistent gains underscores the benefit of integrating KG-based retrieval with LLM reasoning for robust item cold-start recommendation.

![](images/60b7e4bc2314766b007a3e2c74f424440072b13028850decd62cae9747b19bf4.jpg)  
Figure 2: Performance comparison of ColdRAG vari ants across three domains using GPT, showing that both core modules (G and R) add performance gains.

## 4.2.2 Ablation Study (RQ2 & RQ3)

To examine the impact of ColdRAG’s core components, we compare three settings: w/o G,R, a plain LLM without dynamic knowledge graph construction (G) or adaptive candidate retrieval (R); w/o R, a variant that includes G but replaces R with embedding-similarity top-k matching; and the full ColdRAG model combining both modules. As shown in Figure 2, performance improves steadily from w/o G,R to ColdRAG across most domains. These results indicate that dynamic knowledge graph construction (G) provides structured semantic grounding, while adaptive candidate retrieval (R) introduces goal-directed exploration over re lated entities, together yielding consistent gains as each module is added. In the Office domain, w/o R performs slightly worse than w/o G,R, indicating that unfiltered knowledge can introduce noise when metadata is sparse. However, the full model restores performance by selectively refining relevant information through reasoning. Overall, the two modules are complementary: knowledge grounding provides semantic depth, and retrieval ensures relevance. Their combination drives ColdRAG’s superior cold-start recommendation performance.

## 4.2.3 Analysis on Stability and Hallucination (RQ4 & RQ5)

LLM-based recommenders often suffer from generation inconsistency and hallucination, producing unstable or out-of-domain outputs. We evaluate ColdRAG on these aspects using five independent runs on the Games dataset. As shown in

![](images/11d21958612e57a3e35cdb1d89cca60660f22bcb207d5da1611c441aa142b080.jpg)

(b)  
![](images/bc367fcc5c9e7f4befa99ce949df3f4631e271435946e9052f3959747edceff8.jpg)  
Figure 3: (a) Recall@10 box plots over five runs for training-free baselines. (b) Out-of-domain generation rates, both evaluated on the Games dataset with GPT.

Figure 3, ColdRAG achieves high average performance and low variance in Recall@10, demonstrating stable, reproducible generation compared to other training-free baselines. This robustness stems from structured retrieval and reasoning, providing consistent semantic grounding rather than relying on prompt randomness. We also measure hallucination rates, defined as the proportion of generated items not present in the dataset. While other LLMbased models, including LLM and LLMRank variants, exhibit 5–10% out-of-domain outputs even with predefined candidate lists, ColdRAG reduces this rate to 3.15%. This improvement shows that knowledge-grounded retrieval helps the model construct and reason over a semantic graph, enabling it to retrieve contextually valid items and constrain generation within the domain. In summary, beyond achieving superior recommendation performance, ColdRAG also exhibits robust stability and minimal hallucination, which are essential for practical and trustworthy recommender systems.

## 5 Conclusion

We presented ColdRAG, a retrieval-augmented generation framework for item cold-start recommendation. ColdRAG dynamically builds a knowledge graph from sparse metadata and performs LLM-guided multi-hop reasoning to adaptively retrieve candidate items aligned with user preferences—without relying on pre-built candidate lists. This design enables accurate and stable recommendations, making ColdRAG a practical and industryready solution for real-world cold-start scenarios.

## Limitations

While ColdRAG demonstrates strong performance, it faces several practical constraints. First, its reliance on repeated LLM queries during knowledge graph construction and multi-hop reasoning introduces notable computational cost and latency, posing challenges for large-scale or real-time deployment. Moreover, although ColdRAG can operate with both open- and closed-source LLMs, reliance on closed-sourced models such as the GPT series can make reproduction costly and less consistent across environments. Another limitation lies in ColdRAG’s limited adaptability. Several key hyperparameters, such as edge scoring thresholds and candidate pool sizes, are manually set and static across domains. This rigidity may constrain performance under varying data distributions or interaction sparsity. A more adaptive, agentic framework could dynamically adjust these parameters and query strategies, improving both efficiency and generalization in diverse real-world settings.

## References

Qingyu Guo, Fuzhen Zhuang, Chuan Qin, Hengshu Zhu, Xing Xie, Hui Xiong, and Qing He. 2020. A survey on knowledge graph-based recommender systems. IEEE Transactions on Knowledge and Data Engineering, 34(8):3549–3568.

Yupeng Hou, Shanlei Mu, Wayne Xin Zhao, Yaliang Li, Bolin Ding, and Ji-Rong Wen. 2022. Towards universal sequence representation learning for recom mender systems. In Proceedings of the 28th ACM SIGKDD Conference on Knowledge Discovery and Data Mining, pages 585–593.

Yupeng Hou, Junjie Zhang, Zihan Lin, Hongyu Lu, Ruobing Xie, Julian McAuley, and Wayne Xin Zhao. 2024. Large language models are zero-shot rankers for recommender systems. In European Conference on Information Retrieval, pages 364–381. Springer.

Feiran Huang, Zefan Wang, Xiao Huang, Yufeng Qian, Zhetao Li, and Hao Chen. 2023. Aligning distillation for cold-start item recommendation. In Proceedings of the 46th international ACM SIGIR conference on research and development in information retrieval, pages 1147–1157.

Hai-Dang Kieu, Minh-Duc Nguyen, Thanh-Son Nguyen, and Dung D Le. 2025. Keyworddriven retrieval-augmented large language models for cold-start user recommendations. In Companion Proceedings of the ACM on Web Conference 2025, pages 2717–2721.

Yueqing Liang, Liangwei Yang, Chen Wang, Xiongxiao Xu, S Yu Philip, and Kai Shu. 2025. Taxonomyguided zero-shot recommendations with llms. In Proceedings of the 31st International Conference on Computational Linguistics, pages 1520–1530.

Jianghao Lin, Xinyi Dai, Yunjia Xi, Weiwen Liu, Bo Chen, Hao Zhang, Yong Liu, Chuhan Wu, Xiangyang Li, Chenxu Zhu, and 1 others. 2025. How can recommender systems benefit from large language models: A survey. ACM Transactions on Information Systems, 43(2):1–47.

Xinyu Lin, Wenjie Wang, Jujia Zhao, Yongqi Li, Fuli Feng, and Tat-Seng Chua. 2024. Temporally and distributionally robust optimization for cold-start recommendation. In Proceedings of the AAAI Conference on Artificial Intelligence, volume 38, pages 8750– 8758.

Jianmo Ni, Jiacheng Li, and Julian McAuley. 2019. Justifying recommendations using distantly-labeled reviews and fine-grained aspects. In Proceedings of the 2019 conference on empirical methods in natural language processing and the 9th international joint conference on natural language processing (EMNLP-IJCNLP), pages 188–197.

Scott Sanner, Krisztian Balog, Filip Radlinski, Ben Wedin, and Lucas Dixon. 2023. Large language models are competitive near cold-start recommenders for language-and item-based preferences. In Proceedings of the 17th ACM conference on recommender systems, pages 890–896.

Fei Sun, Jun Liu, Jian Wu, Changhua Pei, Xiao Lin, Wenwu Ou, and Peng Jiang. 2019. Bert4rec: Sequential recommendation with bidirectional encoder representations from transformer. In Proceedings of the 28th ACM international conference on information and knowledge management, pages 1441–1450.

Hongwei Wang, Fuzheng Zhang, Miao Zhao, Wenjie Li, Xing Xie, and Minyi Guo. 2019a. Multi-task feature learning for knowledge graph enhanced recommendation. In The world wide web conference, pages 2000–2010.

Xiang Wang, Xiangnan He, Yixin Cao, Meng Liu, and Tat-Seng Chua. 2019b. Kgat: Knowledge graph attention network for recommendation. In Proceedings of the 25th ACM SIGKDD international conference on knowledge discovery & data mining, pages 950– 958.

Yinwei Wei, Xiang Wang, Qi Li, Liqiang Nie, Yan Li, Xuanping Li, and Tat-Seng Chua. 2021. Contrastive learning for cold-start recommendation. In Proceedings of the 29th ACM international conference on multimedia, pages 5382–5390.

Weizhi Zhang, Yuanchen Bei, Liangwei Yang, Henry Peng Zou, Peilin Zhou, Aiwei Liu, Yinghui Li, Hao Chen, Jianling Wang, Yu Wang, and 1 others. 2025. Cold-start recommendation towards the era of large language models (llms): A comprehensive survey and roadmap. arXiv preprint arXiv:2501.01945.

## A Cold-start Adaptability

ColdRAG is inherently suitable for item cold-start scenarios, as illustrated in Figure 4. When a new item appears with only metadata, the framework immediately generates its item profile, extracts entities and relations, and integrates them into the existing knowledge graph through the same pipeline used for prior items. This enables the new item to connect with semantically related concepts (e.g., genres, features, or characters) and become part of the graph’s reasoning and retrieval processes without requiring historical interactions or retraining. Such seamless integration allows ColdRAG to remain robust and responsive in dynamic environments where new content is frequently introduced.

![](images/b90bf087eae89c8e21a5c61ae1c06151477556a889e55f70f1f23b3085f8fd03.jpg)  
Figure 4: Illustration of ColdRAG’s adaptability to item cold-start scenario.

## B Comparison of Recommender System Categories

Traditional recommender systems, including collaborative filtering (CF), content-based (CB), and hybrid CF+CB models, often struggle when new items lack interaction data. CF depends on dense user–item histories and weakens under sparsity, while CB relies on incomplete or noisy metadata. Hybrid methods partially alleviate these issues but still require user interactions to anchor predictions. LLM-based recommenders introduce a zero-shot alternative by leveraging pretrained knowledge, yet prompt-only designs remain vulnerable to hallucination, instability, and limited coverage. RAG improves grounding through external evidence but often overlooks relational structure or retrieves overly broad neighborhoods. ColdRAG addresses these limitations by performing structured multi-hop reasoning over a dynamically constructed knowledge graph, producing evidence-grounded, zero-shot recommendations that are robust to cold-start scenarios. As shown in Table 3, ColdRAG is the only framework that jointly supports cold-start handling, external grounding, zero-shot usability, and multi-

hop reasoning.

Table 3: Comparison of recommender paradigms across four key capabilities: handling cold-start, grounding in external evidence, zero-shot usability, and multi-hop reasoning over structured knowledge. (\* denotes static metadata rather than retrieved evidence.

<table><tr><td></td><td>Cold-start</td><td>Grounding</td><td>Zero-shot</td><td>Multi-hop</td></tr><tr><td>CF</td><td>✗</td><td>✗</td><td>✗</td><td>✗</td></tr><tr><td>CB</td><td>√</td><td> $\checkmark^*$ </td><td>✗</td><td>✗</td></tr><tr><td>CF + CB</td><td>√</td><td>√</td><td>✗</td><td>✗</td></tr><tr><td>Prompt-only LLM</td><td>√</td><td>✗</td><td>√</td><td>✗</td></tr><tr><td>RAG-based LLM</td><td>√</td><td>√</td><td>√</td><td>✗</td></tr><tr><td>ColdRAG (ours)</td><td>√</td><td>√</td><td>√</td><td>√</td></tr></table>

## C Structure of Knowledge Graph

We analyze the structure of the knowledge graph (KG) generated using the Games dataset with gpt-4o-mini, focusing on the distribution of entity types and their relations, as shown in Figure 5. The KG is primarily composed of item nodes (50%) and feature nodes (26%), while other entities such as target user (9%), etc (6%), setting (5%), and genre (4%) provide complementary semantic context. This distribution shows that the KG is centered around items, with non-item entities describing and explaining their properties. The heatmap in Figure 5 reveals dense connections between items and features (15,102 edges) and between items and target users (4,928 edges), indicating that the graph effectively captures item attributes and user-related semantics. Additional links to genre and setting nodes further enrich contextual diversity, enabling nuanced multi-hop reasoning. Overall, the KG exhibits a dense yet interpretable structure that supports ColdRAG’s retrieval and reasoning processes.

![](images/d7a43c3149cd040189d2b410027e8c65aff0409929e836ddb86c386a151ff728.jpg)

![](images/5944d4fa53ad1d7fa8e46c3c0f7438caef2ecb4a2c7bb146a145656bb311c83c.jpg)  
Figure 5: (a) Pie chart of the distribution of entity (node) types in the KG. (b) Heatmap of the number of relations (edges) between the entity types.

## D Prompt Templates

We present the prompt templates used in the four core modules of ColdRAG. Each prompt is designed to guide the LLM through a distinct stage of the pipeline, ensuring consistent and interpretable behavior.

## D.1 Item Profile Generation

This prompt directs the LLM to create a concise, fluent item profile using the title, metadata, and reviews, enriching sparse information with its pretrained knowledge when necessary.

![](images/9d6476e04a4ad86c99d8d3a46506f200fde31410fc0f7c0e2841e8c64a13b81c.jpg)  
Figure 6: Example prompt for Item Profile Generation.

## D.2 Dynamic Knowledge Graph Construction

This prompt instructs the LLM to extract entities and relations from the generated item profile, producing a structured and interpretable knowledge graph centered around the item.

![](images/8e1392fd573cd7a4c21a1b0a804da3c961aaa4a532b61d27bddd8c7176630bf1.jpg)  
Figure 7: Example prompt for Entity and Relation Ex traction.

## D.3 Adaptive Candidate Retrieval over KG

This prompt enables the LLM to evaluate graph edges using the user’s interaction history and iteratively expand the reasoning frontier to identify semantically relevant candidate items.

![](images/70c29fa62ee5ef33d773659e2141977df59f774626dac34a6ccd8e8adb5c18c4.jpg)  
Figure 8: Example prompt for Adaptive Candidate Retrieval.

## D.4 Retrieval-augmented Generation

This prompt guides the LLM to rank the retrieved candidate items and produce the final top-k recommendations in a dataset-consistent format.

![](images/869bead3fa67ae6b41a70d615f6c1a2bb4895d6a46cc773c261920809c3e0bf3.jpg)  
Figure 9: Example prompt for Retrieval-augmented Generation.

## E Hyperparameter Analysis

We analyze the impact of the edge scoring threshold λ, which controls how strictly ColdRAG filters edges during multi-hop reasoning. As shown in Figure 10, ColdRAG achieves the best performance when λ = 0.7. A smaller threshold allows irrelevant edges to remain, while an excessively large threshold overly constrains traversal and misses useful nodes. This result indicates that a moderate threshold effectively balances relevance and diversity in the retrieved candidates, yielding the most robust overall performance.

![](images/15b44f1086ff34216dda3bd467372713a31d4f29bf294c7469274dd804b57a8a.jpg)  
Figure 10: Effect of the edge scoring threshold λ on ColdRAG’s performance.

## F Additional Implementation Details

For the GPT setting, we use gpt-4o-mini accessed through the Azure OpenAI API. Entity and relation embeddings are encoded using OpenAI’s text-embedding-3-small model, with all embeddings indexed in FAISS for approximate nearestneighbor retrieval. For the Qwen setting, we employ qwen2.5-32b-instruct served via the $\nu L L M ^ { 4 }$ backend, paired with the $b g e { - } m \ 3 ^ { 5 }$ embedding model for semantic representation. Both configurations follow identical hyperparameters and retrieval settings to ensure a fair comparison across LLM backbones. These results confirm that ColdRAG’s performance is consistent across different LLM architectures, demonstrating its architecture-agnostic robustness.


---

# 2511.15141_ItemRAG：基于物品的检索增强生成推荐

[2511.15141](https://arxiv.org/abs/2511.15141)

# ItemRAG: Item-Based Retrieval-Augmented Generation for LLM-Based Recommendation

Sunwoo Kim KAIST Seoul, South Korea kswoo97@kaist.ac.kr

Geon Lee KAIST Seoul, South Korea geonlee0325@kaist.ac.kr

Jaemin Yoo Seoul National University Seoul, South Korea jaeminyoo@snu.ac.kr

Kyungho Kim KAIST Seoul, South Korea kkyungho@kaist.ac.kr

Kijung Shin KAIST Seoul, South Korea kijungs@kaist.ac.kr

## Abstract

Recently, large language models (LLMs) have been widely used as recommender systems, owing to their reasoning capability and efectiveness in handling cold-start items. A common approach prompts an LLM with a target user’s purchase history to recom mend items from a candidate set, often enhanced with retrieval augmented generation (RAG). Most existing RAG approaches retrieve purchase histories of users similar to the target user; however, these histories often contain noisy or weakly relevant information and provide little or no useful information for candidate items. To address these limitations, we propose ItemRAG, a novel RAG approach that shifts focus from coarse user-history retrieval to finegrained item-level retrieval. ItemRAG augments the description of each item in the target user’s history or the candidate set by retriev ing items relevant to each. To retrieve items not merely semantically similar but informative for recommendation, ItemRAG leverages co purchase information alongside semantic information. Especially, through their careful combination, ItemRAG prioritizes more informative retrievals and also benefits cold-start items. Through exten sive experiments, we demonstrate that ItemRAG consistently out performs existing RAG approaches under both standard and cold start item recommendation settings. Supplementary materials, code, and datasets are provided at https://github.com/kswoo97/ItemRAG.

## CCS Concepts

• Information systems → Recommender systems.

## Keywords

large language model, retrieval augmented generation

## ACM Reference Format:

Sunwoo Kim, Geon Lee, Kyungho Kim, Jaemin Yoo, and Kijung Shin. 2026. ItemRAG: Item-Based Retrieval-Augmented Generation for LLM-Based Rec ommendation. In Proceedings of the 49th International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR ’26), July 20– 24, 2026, Melbourne, VIC, Australia. ACM, New York, NY, USA, 5 pages. https://doi.org/10.1145/3805712.3809942

![](images/4bc2d7e680eef804219dfc4205fdc88d68df8759da30337299a7b529bde6de20.jpg)

![](images/7503ae2051ebfb13367f82174e0ee9a1fdf17513986c2ec4106cc140f79b43d6.jpg)  
Figure 1: Strong performance of ItemRAG, our proposed itembased RAG method. ItemRAG consistently (1) improves the zero-shot LLM-based recommender (Without RAG) and (2) outperforms both the strongest user-based RAG baseline (CoRAL [23]), and a semantics-only item-based RAG method.

## 1 Introduction

Recommender systems are core to modern web services, retrieving items that match user interests from vast item pools [1, 7–10, 12, 16, 17]. By inferring users’ preferences from their purchase histories, recommender systems provide personalized recommendations that improve user satisfaction and drive business revenue.

In recent years, there have been significant eforts to use large language models (LLMs) as a recommender system. In standard practice, given a target user’s purchase history, an LLM is prompted to recommend items from a candidate set (e.g., a small subset of the full item set) [11, 14]. Owing to LLM’s strong reasoning and zero-/few-shot capabilities, LLM-based recommenders can handle coldstart items efectively and can also provide intuitive explanations that improve users’ understanding of the recommendation results.

To better adapt LLMs for the recommendation tasks, various retrieval-augmented generation (RAG) techniques have been used [4, 12]. Such methods typically focus on user retrieval [21, 25], retrieving users similar to a target user and supplying their purchase histories together with the target user’s own history to the LLM.

However, user retrieval has several limitations. First, retrieved users, although coarsely similar to the target user, may still include a considerable amount of irrelevant information, which can introduce noise. Specifically, because individual users typically exhibit diverse interests, the retrieved purchase histories are likely to reflect the target user’s preferences only partially, with a large portion being less relevant. Second, this approach does not explicitly retrieve information with respect to candidate items, which are equally important to users in recommendations. Although the retrieved user histories may implicitly contain information relevant to candidate items, the lack of explicit conditioning can limit their efectiveness.

![](images/b05093034509c84f370357260f73eb5bb4c5b94ae45bd82c8590abbfc71793a3.jpg)  
Figure 2: An example case of ItemRAG, our item-based RAG method. For retrieving relevant items for item <sup>??</sup>, we first identify items that are co-purchased with (1) item <sup>??</sup> itself and/or (2) items whose textual descriptions are similar to that of item <sup>??</sup>. Then, we sample a specified number of items from this pool, with selection probabilities proportional to their co-purchase frequencies with item <sup>??</sup>. Subsequently, we prompt an LLM to generate a summary of the sampled items and incorporate the summary into the final recommendation prompt, guiding the LLM to understand the co-purchase patterns among items.

To address these limitations, we propose ItemRAG, whose key idea is to retrieve information relevant to individual items at a fine-grained level, instead of coarse-grained retrieval at the user level. Especially, ItemRAG applies this retrieval not only to items in the user’s purchase history but also to each candidate item, aug menting each item with descriptions of relevant items retrieved from the full item corpus. This item-level augmentation (1) mitigates noise introduced by irrelevant information from partially relevant users in user-level augmentation, and (2) also ofers explicit, recommendation-beneficial evidence for each candidate item.

As is intuitive, the success of ItemRAG depends on the retrieved items and their relevance. However, a straightforward extension of a semantics-based retriever, a common design choice in natural lan guage processing [6] that retrieves items with semantically similar descriptions, may be less efective for recommendation, as shown by its limited gains over the user-based approach [23] in Figure 1.

To enable recommendation-aligned retrieval, ItemRAG leverages item co-purchase relations alongside semantic information through a carefully designed retrieval strategy, which leads to sub stantial empirical performance gains (see Figure 1). Specifically, to reduce the impact of less-relevant, incidentally co-purchased items, ItemRAG selectively samples retrieved items in proportion to their co-purchase frequencies, rather than using all retrieved items. Moreover, to better handle cold-start items with few or no co-purchase neighbors, ItemRAG expands the retrieval set by addi tionally retrieving items that were co-purchased not with the query item itself, but with items that are semantically similar to it.

Through extensive experiments, we demonstrate the efective ness of ItemRAG in both (1) standard LLM-based recommendation and (2) cold-start item recommendation. In particular, ItemRAG consistently outperforms user-based RAG baselines in both set tings, yielding up to 11% gains on the Toys dataset (in terms of Hit-Ratio@1) over the strongest user-based RAG baseline.

Our key contributions are summarized below:

• New concept. We propose item-based RAG for LLM-based recommendation, a fine-grained approach that enriches the descrip tions of each target-user purchased item and candidate item.

• New method. We propose ItemRAG, an item-based RAG approach that integrates co-purchase relations and semantic information for relevant item retrieval.

• Strong performance. ItemRAG consistently outperforms userbased RAG baselines in both (1) standard LLM-based recommendation and (2) cold-start item recommendation.

Supplementary materials, code, and datasets are provided at https: //github.com/kswoo97/ItemRAG.

## 2 Related work and preliminary

In this section, we review related studies and present the prelimi nary concepts relevant to our work

Related work. Thanks to their strong reasoning capabilities and ability to handle cold-start items, using LLMs as recommender systems has attracted substantial attention [11, 14]. To better adapt them to recommendation tasks, retrieval-augmented generation (RAG) techniques have been widely explored [4, 12]. One line of work applies RAG in specific settings, including conversational recommendation [19, 26] and knowledge–graph–based recommendation [18, 22]. Another line of RAG work aims to improve generalpurpose recommenders that rely primarily on user–item interactions [4, 21, 25], which is our focus. They are mostly user-based approaches, with inherent limitations detailed in Section 1.

Preliminary. The user set and the item set are denoted by U and I, respectively. We consider a sequential recommendation setting, and therefore, each user $u \in \mathcal { U }$ is represented by her purchase history sequence: u := $[ i _ { 1 } ^ { ( u ) } , i _ { 2 } ^ { ( u ) } , \cdot \cdot \cdot , i _ { n u } ^ { ( u ) } ]$ , where $i _ { s } ^ { ( \dot { u } ) }$ denotes the <sup>??</sup>-th item purchased by user <sup>??</sup> and $n _ { u }$ is the number of items purchased by <sup>??</sup>. Each item <sup>??</sup> ∈ I has a text description $\mathit { t } _ { i } ,$ such as item title.

## 3 Proposed method

In this section, we introduce ItemRAG, an item-based retrievalaugmented generation (RAG) method for LLM-based recommendation. We first give an overview of the ItemRAG pipeline (Section 3.1) and detail our retrieval strategy (Section 3.2).

## 3.1 Overall pipeline of ItemRAG

We consider an LLM-based recommendation pipeline in which an LLM is given (1) the target user’s purchase history and (2) a set of candidate items. Then, the LLM is prompted to rank the candidates by their likelihood of being the target user’s next purchase.<sup>1</sup> Here, each item is represented by its textual description (e.g., item title).

By using ItemRAG, we enhance the description of each query item <sup>??</sup> that is (1) purchased by the target user or (2) a recommendation candidate—by retrieving items relevant to item <sup>??</sup>. Specifically, for each query item <sup>??</sup>, we retrieve items relevant to it, and then pro vide a summary of the retrieved items together with the original textual description of item <sup>??</sup>. Notably, as discussed in Section 1, this augments individual items in a fine-grained manner, in contrast to widely-used coarse target user-level augmentation. In Section 3.2, we present key challenges in the relevant-item decision process and introduce our retrieval strategy that overcomes them.

## 3.2 Retrieval strategy of ItemRAG

One way to retrieve items related to a query item is to select those that are co-purchased with it. However, this faces two challenges: (C1) it performs poorly—and may be infeasible—for cold-start query items with little or no co-purchase data, and (C2) some co-purchased items are incidental and thus weakly relevant.

To address the cold-start challenge (C1), for each query item <sup>??</sup>, we retrieve not only items co-purchased with <sup>??</sup> but also items copurchased with items whose text descriptions are similar to <sup>??</sup>. Our rationale is that items similar to <sup>??</sup> often share co-purchase patterns with <sup>??</sup>, giving strong complementary co-purchase information for <sup>??</sup>.

To address the weak-relevance challenge (C2), we score each query–retrieved item pair by its co-purchase frequency and use this score for the probability of the item being selected in the final retrieval. Our rationale is that frequent co-purchases indicate strong relevance and are less likely to be incidental.

Based on these intuitions, we formally elaborate on our retrieval strategy. We start with presenting two notations. We denote a set of items purchased by user <sup>??</sup> as $\mathcal { M } ( u ) \ ( { \mathrm { i . e . , ~ } } M ( u ) = \{ i _ { s } ^ { ( u ) } \ : \ s \ \in $ $\{ 1 , 2 , \cdots , n _ { u } \} \}$ ). We also denote a set of items co-purchased with item <sup>??</sup> as $N ( i ) \ { \mathrm { ( i . e . , } } N ( i ) = \{ j : i \neq j , \exists u \in { \mathcal { U } } \ { \mathrm { s . t . } } \ \{ i , j \} \subseteq { \mathcal { M } } ( u ) \} )$

In retrieval for a query item <sup>??</sup>, we first find the top-<sup>??</sup> whose textual descriptions are most similar to <sup>??</sup>; we denote this set as $\mathcal { T } ( i )$ . Specifically, for each $j \in \mathcal { I } ,$ we encode its text description $t _ { j }$ via a pre-trained language model LM, obtaining the representation $\mathbf { z } _ { j } \in \mathbb { R } ^ { d } \ ( \mathrm { i . e . , } \ \mathbf { z } _ { j } = \mathsf { L M } ( \boldsymbol { \mathcal { t } } _ { j } ) )$ . We then compute the cosine similarity between <sup>??</sup> and each other item $j \in { \cal { J } } \backslash \{ i \} ( \mathrm { i . e . , } ( \mathbf { z } _ { i } ^ { T } \mathbf { z } _ { j } ) / ( \| \mathbf { z } _ { i } \| _ { 2 } \| \mathbf { z } _ { j } \| _ { 2 } ) )$ and select the top-<sup>??</sup> by similarity; the resulting set is T (<sup>??</sup>).

We subsequently derive a retrieval pool $\mathcal { P } ( i )$ comprising items co-purchased with (1) item <sup>??</sup> itself $( N ( i ) )$ and/or (2) items having similar descriptions to $i ( \mathcal { T } ( i ) )$ . Formally, the pool is defined as:

$$
\mathcal {P} (i) = \mathcal {N} (i) \cup \{j: \exists q \in \mathcal {T} (i) \text {s.t.} j \in \mathcal {N} (q) \}.\tag{1}
$$

After, instead of retrieving all the items within $\mathcal { P } ( i )$ , we sam ple <sup>??</sup> number of items proportional to co-purchase frequencies. Formally, let a co-purchase frequency of items <sup>??</sup> and <sup>??</sup> as <sup>??</sup>?? ?? (i.e., $\begin{array} { r } { c _ { i j } = \sum _ { u \in \mathcal { U } } 1 [ \{ i , j \} \in \mathcal { M } ( u ) ] } \end{array}$ , where 1[·] is an indicator function). Then, a sampling weight <sup>??</sup>???? of item <sup>??</sup> being retrieved for query item <sup>??</sup> is defined as: $\begin{array} { r } { w _ { i j } = c _ { i j } + \frac { 1 } { | \mathcal { T } ( i ) | } \sum _ { q \in \mathcal { T } ( i ) } c _ { q j } , } \end{array}$ where $c _ { i j }$ denotes the co-purchase frequency between items <sup>??</sup> and <sup>??</sup>, and the rest in dicates the mean of co-purchase frequencies between item <sup>??</sup> and items that are semantically similar to item <sup>??</sup>.

Subsequently, we sample <sup>??</sup> items from the retrieval pool $\mathcal { P } ( i )$ (Eq. (1)), where each item $j \in \mathcal { P } ( i )$ is drawn with the probability of $\begin{array} { r } { w _ { i j } / ( \sum _ { q \in \mathcal { P } ( i ) } w _ { i q } ) } \end{array}$ . Lastly, we prompt an LLM to summarize the sampled items and append this summary to the original description of item <sup>??</sup>, helping the LLM-based recommender capture co-purchase information of item <sup>??</sup>. Note that the co-purchase summary generation is independent of the target user; thus, the summary for a given item can be used for diferent target users.

## 4 Experiment

In this section, we analyze the efectiveness of ItemRAG in the LLMbased recommendation tasks. We answer the questions below:

RQ1. How efective is ItemRAG for LLM-based recommendation?

RQ2. How accurate is ItemRAG at recommending cold-start items?

RQ3. Do LLM-based recommender systems make efective use of the item information retrieved by ItemRAG?

RQ4. Do all ItemRAG key components contribute to performance?

## 4.1 Experimental setting

Datasets and evaluation protocol. We use four domains from the latest Amazon Reviews dataset [3]: Sports & Outdoors (Sports), Toys & Games (Toys), Beauty & Personal Care (Beauty), and Arts, Crafts & Sewing (Arts). Further details, including preprocessing steps and dataset statistics, are provided in Appendix [13]. For evaluation, following prior work [14, 23], we use a leave-one-out protocol: for each user, the last purchased item is held out for testing, and the remaining history is used as input. Also, following [14], we prompt the LLM to rank 10 candidate items for the target user’s next purchase; the set includes 1 ground-truth item and 9 randomly sampled items, and results with larger candidate sets are reported in Appendix [13]. We run each experiment three times and report the mean metrics. We further conduct a Wilcoxon signed-rank test between ItemRAG and each baseline to assess statistical significance. In addition, we provide an inference runtime analysis of ItemRAG in the appendix [13].

Baseline methods and ItemRAG. For comparison, we use 9 baseline methods: two graph-based models (LightGCN [2] and Light-GCN++ [15]), two sequential models (SASRec [5] and BERT4Rec [20]), one naive zero-shot LLM-based recommender, and four user-based RAG methods (ICL [21], AdaptRec [25], ReACT [4], and CoRAL [23]). For LLM-based methods, we use GPT-4.1-mini as the backbone. For the retrieval process in ItemRAG, we use 5 similar items per item and sample 50 items in the final retrieval set. Further details on baselines, hyperparameters, and prompts are given in Appendix [13].

## 4.2 RQ1. Standard LLM-based recommendation

Setup. For each method, we construct the training data and retrieval database from users’ purchase histories after withholding each user’s last interaction, which is reserved exclusively for evaluation. For testing, we evaluate each method on 1<sup>,</sup>000 randomly sampled users under the evaluation protocol detailed in Section 4.1.

Result. As shown in Table 1, ItemRAG outperforms all the baseline methods in 18 out of 20 settings. Two points stand out. First, Item-RAG consistently improves the naive zero-shot LLM recommender, by up to 42% in Hit-Ratio@1 on the Beauty & Personal Care dataset. Second, ItemRAG outperforms user-based RAG methods, outperforming the strongest baseline (CoRAL) by up to 11% in terms of Hit-Ratio@1 on the Toys & Games dataset.

Table 1: (RQ1&4) LLM-based recommendation performance. All metrics are multiplied by 100 for better readability. H@K and N@K denote Hit-Ratio@K and NDCG@K, respectively. We do not report N@1, since it is equal to H@1. Best results are highlighted with a green box, and \* indicates that ItemRAG achieves statistically significant improvement over the corresponding baseline at the 0.05 significance level. Notably, ItemRAG outperforms the baseline methods in 18 out of 20 cases

<table><tr><td rowspan="2">Methods</td><td colspan="5">Beauty &amp; Personal Care</td><td colspan="5">Toys &amp; Games</td><td colspan="5">Sports &amp; Outdoors</td><td colspan="5">Arts, Crafts &amp; Sewing</td></tr><tr><td>H@1</td><td>H@3</td><td>H@5</td><td>N@3</td><td>N@5</td><td>H@1</td><td>H@3</td><td>H@5</td><td>N@3</td><td>N@5</td><td>H@1</td><td>H@3</td><td>H@5</td><td>N@3</td><td>N@5</td><td>H@1</td><td>H@3</td><td>H@5</td><td>N@3</td><td>N@5</td></tr><tr><td>LightGCN [2]</td><td>35.8*</td><td>62.8*</td><td>78.8*</td><td>51.2*</td><td>57.9*</td><td>40.9*</td><td>67.7*</td><td>81.5*</td><td>56.4*</td><td>62.1*</td><td>45.3*</td><td>70.6*</td><td>83.3*</td><td>60.2*</td><td>65.5*</td><td>51.7*</td><td>78.2*</td><td>88.0*</td><td>67.1*</td><td>71.1*</td></tr><tr><td>LightGCN++ [15]</td><td>38.3*</td><td>65.2*</td><td>80.2*</td><td>53.4*</td><td>59.7*</td><td>42.2*</td><td>68.5*</td><td>82.5*</td><td>57.3*</td><td>63.1*</td><td>46.0*</td><td>70.8*</td><td>84.0*</td><td>60.5*</td><td>65.9*</td><td>53.0*</td><td>79.9*</td><td>88.8*</td><td>68.2*</td><td>72.2*</td></tr><tr><td>SASRec [5]</td><td>35.2*</td><td>62.6*</td><td>78.7*</td><td>51.9*</td><td>57.5*</td><td>32.4*</td><td>58.5*</td><td>75.1*</td><td>47.0</td><td>54.6*</td><td>44.0*</td><td>68.9*</td><td>82.1*</td><td>57.9*</td><td>63.3*</td><td>47.4*</td><td>72.9*</td><td>86.5*</td><td>62.5*</td><td>69.6*</td></tr><tr><td>BERT4Rec [20]</td><td>36.1*</td><td>63.2*</td><td>78.9*</td><td>52.3*</td><td>57.7*</td><td>32.0*</td><td>58.7*</td><td>75.8*</td><td>47.1*</td><td>55.5*</td><td>44.2*</td><td>70.5*</td><td>83.8*</td><td>59.4*</td><td>65.3*</td><td>48.2*</td><td>74.6*</td><td>87.1*</td><td>63.3*</td><td>69.9*</td></tr><tr><td>Zero-shot</td><td>34.6*</td><td>57.7*</td><td>72.9*</td><td>48.0*</td><td>54.2*</td><td>39.3*</td><td>62.5*</td><td>76.5*</td><td>52.7*</td><td>58.5*</td><td>43.4*</td><td>66.6*</td><td>81.6*</td><td>56.7*</td><td>62.9*</td><td>45.7*</td><td>72.2*</td><td>83.8*</td><td>61.1*</td><td>65.6*</td></tr><tr><td>ICL [21]</td><td>37.7*</td><td>61.9*</td><td>76.7*</td><td>51.5*</td><td>57.5*</td><td>41.3*</td><td>66.4*</td><td>80.6*</td><td>55.7*</td><td>61.1*</td><td>46.4*</td><td>70.2*</td><td>84.1*</td><td>59.8*</td><td>65.7*</td><td>46.3*</td><td>75.3*</td><td>86.7*</td><td>63.1*</td><td>67.8*</td></tr><tr><td>AdaptRec [25]</td><td>34.7*</td><td>58.2*</td><td>74.9*</td><td>47.9*</td><td>55.1*</td><td>37.8*</td><td>63.3*</td><td>77.5*</td><td>52.2*</td><td>58.1*</td><td>44.4*</td><td>67.8*</td><td>83.2*</td><td>57.5*</td><td>63.6*</td><td>46.4*</td><td>74.4*</td><td>85.8*</td><td>62.9*</td><td>67.9*</td></tr><tr><td>ReACT [4]</td><td>34.4*</td><td>57.7*</td><td>73.5*</td><td>47.6*</td><td>54.2*</td><td>38.5*</td><td>61.7*</td><td>75.9*</td><td>51.7*</td><td>57.8*</td><td>44.7*</td><td>68.7*</td><td>83.5*</td><td>58.2*</td><td>64.4*</td><td>46.9*</td><td>73.0*</td><td>83.8*</td><td>61.9*</td><td>66.4*</td></tr><tr><td>CoRAL [23]</td><td>46.5*</td><td>69.9*</td><td>82.0*</td><td>60.2*</td><td>65.0*</td><td>44.6*</td><td>70.1*</td><td>81.2*</td><td>59.4*</td><td>64.0*</td><td>48.5*</td><td>73.2*</td><td>87.1*</td><td>62.5*</td><td>68.3*</td><td>52.4*</td><td>80.7*</td><td>91.1*</td><td>68.9*</td><td>73.3*</td></tr><tr><td>w/o cand-aug.</td><td>36.9*</td><td>59.2*</td><td>73.8*</td><td>49.8*</td><td>55.8*</td><td>42.1*</td><td>63.7*</td><td>78.9*</td><td>54.6*</td><td>60.8*</td><td>44.8*</td><td>68.2*</td><td>81.8*</td><td>57.5*</td><td>63.3*</td><td>47.3*</td><td>72.8*</td><td>84.4*</td><td>62.0*</td><td>66.8*</td></tr><tr><td>w/o co-purch.</td><td>46.1*</td><td>68.9*</td><td>82.1*</td><td>59.1*</td><td>64.7*</td><td>46.4*</td><td>70.8*</td><td>81.9*</td><td>60.6*</td><td>65.1*</td><td>50.6*</td><td>72.9*</td><td>86.2*</td><td>63.6*</td><td>68.9*</td><td>54.6*</td><td>80.1*</td><td>89.7*</td><td>69.5*</td><td>73.3*</td></tr><tr><td>w/o sim-items</td><td>47.5*</td><td>70.2*</td><td>82.8*</td><td>60.8*</td><td>66.3*</td><td>49.8</td><td>71.6*</td><td>83.9*</td><td>62.4*</td><td>67.7*</td><td>50.2*</td><td>74.0*</td><td>87.7*</td><td>64.5</td><td>70.0</td><td>56.0*</td><td>82.1*</td><td>91.1*</td><td>71.0*</td><td>74.6*</td></tr><tr><td>w/o co-freq.</td><td>47.7*</td><td>70.1</td><td>83.9</td><td>60.7*</td><td>66.6</td><td>48.1*</td><td>73.1*</td><td>83.5*</td><td>63.0*</td><td>67.0*</td><td>50.7*</td><td>74.1</td><td>87.9*</td><td>64.0</td><td>69.8*</td><td>56.2*</td><td>82.2*</td><td>91.0*</td><td>71.3*</td><td>75.0*</td></tr><tr><td>ItemRAG</td><td>49.1</td><td>71.0</td><td>83.8</td><td>61.5</td><td>66.9</td><td>49.5</td><td>74.2</td><td>85.0</td><td>63.8</td><td>68.1</td><td>51.6</td><td>74.7</td><td>88.3</td><td>64.6</td><td>70.3</td><td>57.8</td><td>82.6</td><td>91.9</td><td>72.3</td><td>76.1</td></tr></table>

Table 2: (RQ2) Cold-start item recommendation performance. All metrics are multiplied by 100 for better readability. H@K and N@K denote Hit-Ratio@K and NDCG@K, respectively. Best results are highlighted with a green box, and \* indicates that ItemRAG achieves statistically significant improvements over the corresponding baseline at the 0.05 significance level. Notably ItemRAG outperforms the baseline methods in every case.

<table><tr><td rowspan="2">Methods</td><td colspan="5">Beauty &amp; Personal care</td><td colspan="5">Toys &amp; Games</td><td colspan="5">Sports &amp; Outdoors</td><td colspan="5">Arts, Crafts &amp; Sewing</td></tr><tr><td>H@1</td><td>H@3</td><td>H@5</td><td>N@3</td><td>N@5</td><td>H@1</td><td>H@3</td><td>H@5</td><td>N@3</td><td>N@5</td><td>H@1</td><td>H@3</td><td>H@5</td><td>N@3</td><td>N@5</td><td>H@1</td><td>H@3</td><td>H@5</td><td>N@3</td><td>N@5</td></tr><tr><td>Zero-shot</td><td>34.6*</td><td>57.7*</td><td>72.9*</td><td>48.0*</td><td>54.2*</td><td>39.3*</td><td>62.5*</td><td>76.5*</td><td>52.7*</td><td>58.5*</td><td>43.4*</td><td>66.6*</td><td>81.6*</td><td>56.7*</td><td>62.9*</td><td>45.7*</td><td>72.2*</td><td>83.8*</td><td>61.1*</td><td>65.6*</td></tr><tr><td>ICL [21]</td><td>37.1*</td><td>61.6*</td><td>76.4*</td><td>51.3*</td><td>56.9*</td><td>40.5*</td><td>66.1*</td><td>79.1*</td><td>55.1*</td><td>60.7*</td><td>45.6*</td><td>69.7*</td><td>83.9*</td><td>59.4*</td><td>65.3*</td><td>45.0*</td><td>74.3*</td><td>85.8*</td><td>61.9*</td><td>66.6*</td></tr><tr><td>AdaptRec [25]</td><td>37.0*</td><td>60.4*</td><td>75.5*</td><td>50.1*</td><td>56.1*</td><td>38.2*</td><td>64.4*</td><td>78.6*</td><td>53.3*</td><td>59.7*</td><td>45.2*</td><td>68.9*</td><td>83.0*</td><td>58.8*</td><td>64.6*</td><td>49.5*</td><td>73.5*</td><td>85.0*</td><td>62.4*</td><td>67.1*</td></tr><tr><td>ReACT [4]</td><td>35.3*</td><td>58.4*</td><td>72.0*</td><td>50.4*</td><td>53.8*</td><td>39.0*</td><td>61.9*</td><td>76.2*</td><td>52.2*</td><td>57.9*</td><td>42.9*</td><td>66.4*</td><td>81.1*</td><td>56.0*</td><td>62.2*</td><td>47.2*</td><td>72.7*</td><td>84.4*</td><td>62.0*</td><td>66.8*</td></tr><tr><td>CoRAL [23]</td><td>38.5*</td><td>60.9*</td><td>73.3*</td><td>51.5*</td><td>56.8*</td><td>39.0*</td><td>61.2*</td><td>74.0*</td><td>51.7*</td><td>57.0*</td><td>45.0*</td><td>68.2*</td><td>81.4*</td><td>58.6*</td><td>63.4*</td><td>46.4*</td><td>73.4*</td><td>83.9*</td><td>61.8*</td><td>66.3*</td></tr><tr><td>ItemRAG</td><td>47.7</td><td>70.7</td><td>83.7</td><td>60.9</td><td>66.2</td><td>48.7</td><td>71.9</td><td>83.2</td><td>61.9</td><td>66.7</td><td>51.3</td><td>74.7</td><td>88.0</td><td>64.3</td><td>70.2</td><td>57.9</td><td>82.7</td><td>91.4</td><td>72.3</td><td>75.9</td></tr></table>

## 4.3 RQ2. Cold-start item recommendation

Setup. Given that the strength in cold-start item recommendation is the primary promise of LLM-based recommenders [24], we eval uate each method under an item cold-start setup. Specifically, for the 1<sup>,</sup> 000 sampled users described in Section 4.2, we remove the ground-truth test items for the users—together with all interactions involving that item—from both the training set and the retrieval database, making the corresponding items cold-start.<sup>2</sup> We then evaluate each method’s ability to recommend such items to the corresponding users. Since the learning-based baselines we use cannot handle unseen (cold-start) items, we focus on LLM-based approaches. Other settings remain the same as in Section 4.2.

Result. As shown in Table 2, ItemRAG outperforms the baseline methods in all the cases, demonstrating its strong performance in recommending cold-start items. Notably, its performance decreases by only 1% on average relative to the standard setting (Table 1), suggesting that it remains efective in cold-start scenarios.

![](images/a873be0acd0a52627860fe41cda8db6998dd1daa3e4755ca4b0f1c849ed1de0e.jpg)

## LLM predictions and the rationale for its predictions

▪ Naïve zero-shot LLM: Jewelry kit for kids

LLM with ItemRAG: BARWA wedding dress for dolls LLM’s rationale: “The user’s purchase history shows strong patterns of interests in dolls and accessories […] This item has strong co-purchase associations with doll and doll accessory groups, making it the most likely candidate for purchase.”

Figure 3: (RQ3) Case study. While the naive zero-shot LLMbased recommender fails, augmenting it with co-purchase information retrieved by ItemRAG —information the model explicitly uses—yields an accurate recommendation.

## 4.4 RQ3. Case study

Setup. We examine whether the LLM-based recommender system leverages the item information retrieved by ItemRAG. To this end, on the Toys & Games dataset, we run a case study in which the LLM is prompted to give the rationale behind its recommendations. Additional cases in other datasets are reported in Appendix [13]. Result. Figure 3 presents a case where a naive zero-shot LLM-based recommender fails to provide an accurate recommendation. When the prompt is augmented with co-purchase information retrieved by ItemRAG, the LLM (1) recommends the correct item and (2) explic itly notes in its rationale that it relied on the retrieved co-purchase signals. This result suggests that ItemRAG’s retrieved information is indeed used and beneficial for improving performance.

## 4.5 RQ4. Ablation study

Setup. We assess the necessity of ItemRAG ’s key components by using four variants below:

(V1) w/o cand-aug: Does not augment candidate item descriptions.

(V2) w/o co-purch: Retrieves textually similar items instead of us ing co-purchase relations.

(V3) w/o sim-items: Uses its own co-purchase information for each item during retrieval

(V4) w/o co-freq: Replaces frequency-weighted sampling with uni form sampling.

Result. As shown in Table 1, the four variants underperform Item RAG in 18 out of 20 settings, demonstrating the efectiveness of the ItemRAG’s key components in LLM-based recommendation.

## 5 Conclusion and discussion

In this work, we introduce ItemRAG, an item-based RAG technique for LLM-based recommendation. The key idea is to augment indi vidual items in the target user’s purchase history or the candidate set, instead of relying on coarse user-level augmentation. Especially, its carefully designed retrieval strategy, guided by co-purchase in formation, retrieves items that are recommendation-relevant rather than merely semantically similar, and also augments cold-start items. Through extensive experiments, we demonstrate the efec tiveness of ItemRAG for LLM-based recommendation and cold-start item recommendation. One limitation of ItemRAG is that incorpo rating additional retrieved information can increase the length of the input prompt to the LLM recommender, which in turn leads to higher API costs and longer inference time. Reducing the token usage by the retrieved information is thus an important direction for future work, especially for practical deployment.

Acknowledgements. This work was partly supported by the National Research Foundation of Korea (NRF) grant funded by the Korea government (MSIT) (No. RS-2024-00406985, 40%). This work was partly supported by Institute of Information & Communications Technology Planning & Evaluation (IITP) grant funded by the Korea government (MSIT) (No. RS-2022-II220871, Development of AI Autonomy and Knowledge Enhancement for AI Agent Collabo ration, 50%) (No. RS-2019-II190075, Artificial Intelligence Graduate School Program (KAIST), 10%).

## References

[1] Chongming Gao, Mengyao Gao, Chenxiao Fan, Shuai Yuan, Wentao Shi, and Xiangnan He. 2025. Process-supervised llm recommenders via flow-guided tuning. In SIGIR.

[2] Xiangnan He, Kuan Deng, Xiang Wang, Yan Li, Yongdong Zhang, and Meng Wang. 2020. Lightgcn: Simplifying and powering graph convolution network for recommendation. In SIGIR

[3] Yupeng Hou, Jiacheng Li, Zhankui He, An Yan, Xiusi Chen, and Julian McAuley. 2026. Bridging Language and Items for Retrieval and Recommendation: Bench marking LLMs as Semantic Encoders.. In ACL.

[4] Zheng Hu, Yongsen Pan, Zetao Li, Jiaming Huang, Satoshi Nakagawa, Jiawen Deng, Shimin Cai, and Fuji Ren. 2026. Retrieval-enhanced, Adaptively Collabora tive, and Temporal-aware user behavior comprehension for LLM-based sequential recommendation. Information Processing & Management 63, 1 (2026), 104354

[5] Wang-Cheng Kang and Julian McAuley. 2018. Self-attentive sequential recommendation. In ICDM.

[6] Vladimir Karpukhin, Barlas Oguz, Sewon Min, Ledell Wu, Sergey Edunov, Danqi Chen, and Wen-tau Yih. 2020. Dense Passage Retrieval for Open-Domain Question Answering.. In EMNLP.

[7] Kyungho Kim, Sunwoo Kim, Geon Lee, Jinhong Jung, and Kijung Shin. 2025. Multi-behavior recommender systems: a survey. In PAKDD.

[8] Kyungho Kim, Sunwoo Kim, Geon Lee, and Kijung Shin. 2024. Towards better utilization of multiple views for bundle recommendation. In CIKM.

[9] Kyungho Kim, Sunwoo Kim, Geon Lee, and Kijung Shin. 2025. A self-supervised mixture-of-experts framework for multi-behavior recommendation. In CIKM.

[10] Sunwoo Kim, Hyunjin Hwang, and Kijung Shin. 2026. Personalized Parameter-Eficient Fine-Tuning of Foundation Models for Multimodal Recommendation. In WWW.

[11] Sein Kim, Hongseok Kang, Seungyoon Choi, Donghyun Kim, Minchul Yang, and Chanyoung Park. 2024. Large language models meet collaborative filtering: An eficient all-round llm-based recommender system. In KDD.

[12] Sunwoo Kim, Geon Lee, Kyungho Kim, Liam Collins, Neil Shah, and Kijung Shin. 2025. Retrieval-Augmented Generation for LLM-based Recommender Systems: A Comprehensive Survey. HAL preprint (2025). https://hal.science/hal-05561909

[13] Sunwoo Kim, Geon Lee, Kyung ho Kim, Jaemin Yoo, and Kijung Shin. 2026. Supplementary materials, code, and datasets for this work. https://github.com/ kswoo97/ItemRAG.

[14] Genki Kusano, Kosuke Akimoto, and Kunihiro Takeoka. 2025. Revisiting Prompt Engineering: A Comprehensive Evaluation for LLM-based Personalized Recom mendation. In RecSys.

[15] Geon Lee, Kyungho Kim, and Kijung Shin. 2024. Revisiting LightGCN: Unexpected Inflexibility, Inconsistency, and A Remedy Towards Improved Recommendation. In RecSys.

[16] Namjun Lee and Jaekwang Kim. 2025. SEALR: Sequential Emotion-Aware LLM-Based Personalized Recommendation System. In SIGIR

[17] Jiayi Liao, Ruobing Xie, Sihang Li, Xiang Wang, Xingwu Sun, Zhanhui Kang, and Xiangnan He. 2025. Multi-Grained Patch Training for Eficient LLM-based Recommendation. In SIGIR.

[18] Zeyuan Meng, Zixuan Yi, and Iadh Ounis. 2025. KERAG\_R: Knowledge-Enhanced Retrieval-Augmented Generation for Recommendation. arXiv preprint arXiv:2507.05863 (2025).

[19] Zhangchi Qiu, Linhao Luo, Zicheng Zhao, Shirui Pan, and Alan Wee-Chung Liew. 2025. Graph Retrieval-Augmented LLM for Conversational Recommendation Systems. In PAKDD.

[20] Fei Sun, Jun Liu, Jian Wu, Changhua Pei, Xiao Lin, Wenwu Ou, and Peng Jiang. 2019. BERT4Rec: Sequential recommendation with bidirectional encoder repre sentations from transformer. In CIKM.

[21] Lei Wang and Ee-Peng Lim. 2024. The whole is better than the sum: Using aggregated demonstrations in in-context learning for sequential recommendation. In NAACL.

[22] Shijie Wang, Wenqi Fan, Yue Feng, Shanru Lin, Xinyu Ma, Shuaiqiang Wang, and Dawei Yin. 2025. Knowledge graph retrieval-augmented generation for llm-based recommendation. In ACL.

[23] Junda Wu, Cheng-Chun Chang, Tong Yu, Zhankui He, Jianing Wang, Yupeng Hou, and Julian McAuley. 2024. Coral: collaborative retrieval-augmented large language models improve long-tail recommendation. In KDD.

[24] Likang Wu, Zhi Zheng, Zhaopeng Qiu, Hao Wang, Hongchao Gu, Tingjia Shen, Chuan Qin, Chen Zhu, Hengshu Zhu, Qi Liu, et al. 2024. A survey on large language models for recommendation. World Wide Web 27, 5 (2024), 60.

[25] Tong Zhang. 2025. AdaptRec: A Self-Adaptive Framework for Sequential Recommendations with Large Language Models. arXiv:2504.08786 (2025).

[26] Yaochen Zhu, Chao Wan, Harald Steck, Dawen Liang, Yesu Feng, Nathan Kallus, and Jundong Li. 2025. Collaborative Retrieval for Large Language Model-based Conversational Recommender Systems. In WWW.


---

# 2512.20916_多模态大模型摘要与检索增强序列推荐

[2512.20916](https://arxiv.org/abs/2512.20916)

# MMSRARec: Summarization and Retrieval Augumented Sequential Recommendation Based on Multimodal Large Language Model

Haoyu Wang<sup>1</sup>, Yitong Wang<sup>1</sup>, and Jining Wang<sup>1</sup>

College of Computer Science and Artificial Intelligence, Fudan University wanghy24@m.fudan.edu.cn

Abstract. Recent advancements in Multimodal Large Language Models (MLLMs) have demonstrated significant potential in recommendation systems. However, the efective application of MLLMs to multimodal sequential recommendation remains unexplored: A) Existing methods primarily leverage the multimodal semantic understanding capabilities of pre-trained MLLMs to generate item embeddings or semantic IDs, thereby enhancing traditional recommendation models. These approaches generate item representations that exhibit limited interpretability, and pose challenges when transferring to language model-based recommendation systems. B) Other approaches convert user behavior sequence into image-text pairs and perform recommendation through multiple MLLM inference, incurring prohibitive computational and time costs. C) Current MLLM-based recommendation systems generally neglect the integration of collaborative signals. To address these limitations while balancing recommendation performance, interpretability, and computational cost, this paper proposes MultiModal Summarization-and-Retrieval-Augmented Sequential Recommendation (MMSRARec). Specifically, we first employ MLLM to summarize items into concise keywords and finetune the model using rewards that incorporate summary length, information loss, and reconstruction dificulty, thereby enabling adaptive adjustment of the summarization policy. Inspired by retrieval-augmented generation, we then transform collaborative signals into corresponding keywords and integrate them as supplementary context. Finally, we apply supervised fine-tuning with multi-task learning to align the MLLM with the multimodal sequential recommendation. Extensive evaluations on common recommendation datasets demonstrate the efectiveness of MMSRARec, showcasing its capability to eficiently and interpretably understand user behavior histories and item information for accurate recommendations.

Keywords: Sequential Recommendation · Multimodal Large Language Model.

## 1 Introduction

Recommendation Systems (RSs) [20] serve as tools in various online applications to help users filter out irrelevant information and discover items of interest. With the advancement of the Internet, multimodal item information such as covers, detailed images, and textual descriptions has become a crucial input source for RSs. Among these systems, Sequential Recommendation (SR) [2] methods have gained prominence by capturing dynamic user interests. These methods encode users and items as unique identifiers, utilize historical interaction data to learn sequential behavior patterns, and incorporate multimodal information as supplementary input to enhance recommendations.

![](images/7f3110354bfd441003ee228c451a98a6c86ba6e65d93f3aaa5cb109b69565f78.jpg)  
Fig. 1: Comparison between existing multimodal sequential recommendation methods based on MLLM and our proposed method.

Recent advances in Multimodal Large Language Models (MLLMs) have demon strated significant potential in RSs [30]. Several approaches have been explored to adapt MLLMs for multimodal SR tasks, which can be broadly categorized into two main directions, as illustrated in Fig. 1. The first approach treats pretrained MLLMs as visual encoders, where multimodal information is fed into the MLLM at an early stage to obtain item representations [25,4,15]. These representations are then used either directly as feature embeddings or further processed into semantic IDs, which are subsequently integrated into traditional multimodal recommendation models. However, such methods sufer from several limitations. First, they leverage only the pre-trained MLLMs, overlooking the distribution shift between MLLM pre-training corpora and real-world recommendation data. Second, the generated item representations are non-interpretable vector embeddings rather than readable natural language, which are inherently incompatible with the textual space of language models. Consequently, they fail to directly exploit the powerful generalization and reasoning capabilities inherent in the language models themselves.

The second approach reformulates sequential recommendation tasks as Natural Language Processing (NLP) tasks [24]. In this paradigm, item information from the user’s interaction history is directly input into the MLLM, which then performs multiple inferences to generate recommendations. This methodology capitalizes on the MLLM’s semantic understanding and in-context learning capabilities, ofering better interpretability. Nevertheless, the computational and temporal costs for multiple times MLLM inferences renders it impractical for online deployment. Besides, these methods neglect collaborative signals, causing the models to overemphasize item features while overlooking latent user behavior patterns. These limitations and challenges indicate that the efective application of MLLMs in multimodal SR remains largely unexplored.

To address these challenges and holistically balance recommendation performance, interpretability, and cost, this paper proposes MultiModal Summarization and-Retrieval-Augmented Sequential Recommendation (MMSRARec). Our recommendation method consists of three stages, as illustrated in Fig. 2. Specifically, to align multimodal SR with NLP tasks while avoiding multiple online inferences, we first devise multimodal summarization stage. In this stage, multimodal item information is summarized into representative sets of keywords using MLLM. The summarization strategy is adaptively optimized via Reinforcement Learning with Verifiable Rewards (RLVR) [17], which jointly considers summary length, information loss, and reconstruction dificulty. This stage can be performed ofline, and its outputs are interpretable natural language keywords rather than unreadable vectors or semantic IDs.

Second, to incorporate collaborative signals into the recommendation framework, we introduce similar-user retrieval stage. Based on traditional item ID features, users with similar historical behaviors are retrieved, and their subsequent interactions are converted into corresponding keywords and are then integrated into the input as contextual information. Finally, we design four types of recommendation tasks and train the MLLM via Parameter-Eficient Fine-Tuning (PEFT) [5] in multi-task learning stage. This enables the model to understand and adapt to multimodal sequential recommendation tasks while mitigating overfitting. Extensive evaluations on three commonly-used recommendation datasets demonstrate the efectiveness of MMSRARec, confirming its capability to comprehend user behavior history and item information while achieving eficient and interpretable recommendations.

Our contributions can be summarized as follows:

We propose MMSRARec, a novel approach for sequential recommendation that leverages multimodal large language models. By summarizing item information, retrieving similar users, and aligning the SR task with multi-task learning, MMSRARec efectively utilizes the semantic understanding and incontext learning capabilities of MLLMs to achieve accurate and interpretable recommendations.

– To the best of our knowledge, our work is the first attempt that introduces item summarization into natural language keywords and employs reinforcement learning to fine-tune MLLMs, while incorporating collaborative signals into the language model via retrieval of similar users. These innovations address key challenges in existing MLLM-based methods and enhance recommendation performance.

We conduct suficient experiments on three real-world recommendation datasets, demonstrating that MMSRARec efectively enhances recommendation performance, interpretability, and inference eficiency for multimodal sequential recommendation.

## 2 Related Work

## 2.1 Multimodal Large Language Model

Multimodal Large Language Models (MLLMs) based on multimodal pre-training [31] have advanced rapidly in recent years, achieving remarkable performance across a variety of downstream vision-language tasks such as visual question answering, grounding , and image captioning. With the progress of visual instruction tuning, state-of-the-art MLLMs including GPT-4o [10], Gemini [23], and Qwen-VL [1] are capable of efectively understanding human intentions and visual inputs, as well as performing complex multimodal in-context learning in response to instructions. However, directly applying MLLMs to sequential recommendation tasks remains challenging. Firstly, due to constraints on the model’s context length, it is dificult to input complete user behavior sequences into MLLMs. Secondly, MLLMs still exhibit limited capability in comprehending multiple images, which hinders their ability to interpret temporal trends in user interactions. Lastly, compared to traditional sequential recommendation models, MLLMs require significantly more time and computational resources for inference. Our proposed MMSRARec overcomes the limitations of context length and the high cost of multi-image reasoning through keyword-based compression, making it more suitable for real-world recommendation scenarios.

## 2.2 MLLM-Based Multimodal Sequetial Recommendation

Application of MLLMs to multimodal sequential recommendation tasks primarily follows two main directions. The first approach leverages pre-trained MLLMs as feature encoders. For example, NoteLLM-2 [25] employs a late fusion mechanism to directly integrate visual information with textual data, representing both image and text content as learnable tokens. Molar [15] integrates multiple content modalities with ID information, using MLLMs to generate unified item representations from both textual and non-textual data. MLLMRec [4] utilizes MLLMs to convert item images into high-quality semantic descriptions, which are then fused with the item’s textual metadata. However, such methods primarily exploit the representational capacity of pre-trained MLLMs while overlooking the distribution shift between MLLM training data and real-world recommendation system data, and they often lack interpretability. The second approach formulates multimodal sequential recommendation as a natural language processing task, with MLLMs directly serving as the recommender. For instance, MLLM-MSR [24] summarizes user preferences into textual form through multiple inferences with large language model, after which the MLLM makes recommendations by combining these summarized preferences with multimodal item information. Nevertheless, the multiple inference steps required by this paradigm entail substantial computational and time costs. In contrast, MMSRARec employs RLVR to guide the MLLM in adaptively adjusting its representation strategy based on recommendation data, enabling efecient recommendations through once inference.

## 3 Method

## 3.1 Problem Formulation

We formulate the multimodal sequential recommendation task as follows: given a user $u \in \mathcal { U }$ and a chronologically ordered sequence of historically interacted items $\mathcal { H } _ { u } = \{ \mathcal { T } _ { 1 } , \mathcal { T } _ { 2 } , . . . , \mathcal { T } _ { n } \}$ , where each item $\mathcal { T } _ { i }$ is represented by its ID, image, and textual description as $\mathcal { T } _ { i } = ( i d _ { i } , i m g _ { i } , t e x t _ { i } )$ , the objective is to predict the item $\mathcal { T } _ { n + 1 }$ that the user is most likely to interact with at the n + 1-th time step.

## 3.2 Overview

Balancing recommendation performance, interpretability, and cost, we propose a three-stage MLLM-based multimodal sequential recommendation pipeline, termed MMSRARec, as illustrated in Fig. 2. First, to compress multimodal user interaction information into a context length acceptable to the MLLM, during the multimodal summarization stage, we summarize the user behavior history $\mathcal { H } _ { u }$ into a set of natural language keywords $\mathcal { K } _ { u } = \{ \mathcal { W } _ { \mathbb { Z } _ { 1 } } , \mathcal { W } _ { \mathbb { Z } _ { 2 } } , . . . , \mathcal { W } _ { \mathbb { Z } _ { n } } \}$ . Subsequently, to introduce collaborative signals into the MLLM, we retrieve users with similar interaction histories ${ \cal S } _ { u } = \{ u ^ { \prime } , u ^ { \prime \prime } , \ldots \}$ based on user ID information—which is typically challenging for MLLMs to leverage directly—and incorporate the keywords $\{ \mathcal { K } _ { u ^ { * } } \} _ { u ^ { * } \in \mathcal { S } _ { u } }$ corresponding to the subsequent interactions of these similar users as auxiliary contextual information. Finally, we frame the multimodal sequential recommendation task as a natural language processing task by using $( K _ { u } , \{ K _ { u ^ { * } } \} _ { u ^ { * } \in { \cal S } _ { u } } , i d _ { n + 1 } , i m g _ { n + 1 } , t e x t _ { n + 1 } )$ as prompts, and perform parametereficient fine-tuning of the MLLM driven by multi-task learning.

## 3.3 Multimodal Summarization Stage

As discussed in Sec. 2.1, attempts to apply MLLMs to SR are constrained by the fact that the number of images associated with a user’s historical interactions often exceeds the MLLM’s context window. Consequently, most approaches resort to using the MLLM solely as feature encoder. However, this practice merely leverages the pretrained MLLM and overlooks the mismatch between the MLLM’s training data and real-world recommendation data. Moreover, an MLLM-based encoder represents item information as uninterpretable feature vectors, which are intrinsically incompatible with the textual space of language models, thereby necessitating additional alignment training.

Recent research on text-only LLMs has shown that extracting item attributes as specific natural-language keywords via an LLM-style summarization procedure can also benefit recommendation [27,3]. Inspired by this, we design a Multimodal Summarization Stage to represent multimodal item information as interpretable keywords that serve as context for language-model-based recommendation. Specifically, for an item $\mathcal { T } _ { i }$ , we prompt the MLLM with the template shown in Table 1 to obtain keywords $\mathcal { W } _ { \mathcal { I } _ { i } }$ . To mitigate modality bias, where an MLLM may ignore information from a particular modality, we ask the model to summarize img<sub>i</sub> and text<sub>i</sub> separately, thereby reducing item-information loss during summarization.

![](images/7612411aca768e2a5712095ac267624c5d0a51f4e2e35b4597e38b884419b6a7.jpg)

Fig. 2: The framework of MMSRARec.  
![](images/4e5217af3f5bfcfaed5754f678033afb5b5ec61e7e871142f3069178900c20fa.jpg)  
Table 1: Prompt template for multimodal summarization.

Furthermore, to adapt MLLMs to recommendation data, we employ Reinforcement Learning with Verifiable Rewards (RLVR) [17] to stimulate the summarization ability of MLLMs. We design three distinct rewards to train the MLLM to adaptively adjust its summarization policy. Information Reward computes the semantic similarity between the model’s summary and the original item description, encouraging the model to preserve key information about the item. Reconstruction Reward measures the perplexity of reconstructing the original description from keywords generated by the MLLM, guiding the model to use interpretable and easily understandable keywords. Length Reward penalizes the number of keywords in the summary, preventing the model from reward hacking by generating an excessive number of words. The specific formulations are as follows:

$$
R _ {\mathrm{info}} = \frac {\phi (\mathcal {W} _ {\mathcal {I} _ {i}}) \cdot \phi (t e x t _ {\mathcal {I} _ {i}})}{\| \phi (\mathcal {W} _ {\mathcal {I} _ {i}} \| \| \phi (t e x t _ {\mathcal {I} _ {i}}) \|}\tag{1}
$$

$$
R _ {\text { recon }} = - \exp \left(- \frac {1}{N} \sum_ {i = 1} ^ {N} \log P (w _ {j} | w _ {1: j - 1}, \mathcal {W} _ {\mathcal {I} _ {i}})\right)\tag{2}
$$

$$
R _ {\mathrm{len}} = - | \mathcal {W} _ {\mathcal {I} _ {i}} |\tag{3}
$$

$$
R = \alpha R _ {\mathrm{info}} + \beta R _ {\mathrm{recon}} + \gamma R _ {\mathrm{len}}\tag{4}
$$

We adpot the Group Relative Policy Optimization (GRPO) [21] algorithm for reinforcement learning, which eliminates the need for a specifice critic network by leveraging group-level reward statistics. In summary, the multimodal summarization stage maps multimodal item information into a natural language space by applying RLVR on recommendation data to the MLLM. This process efectively summarizes item information while preserving interpretability and the integrity of item feature. This stage can be conducted ofline, where items are pre-processed into keywords, thereby reducing the overhead of online inference.

## 3.4 Similar-User Retrieval Stage

Another significant challenge in applying MLLMs to SR lies in how to incorporate collaborative information into the MLLM. Given the finite context window of MLLMs, it is computationally prohibitive to feed the entire interaction history of all users into the model. Inspired by the Retrieval-Augmented Generation (RAG) [12] paradigm, we introduce item ID information, which is inherently difficult for MLLMs to utilize directly.

First, we train a conventional SR model (e.g., SASRec [11]) using item IDs. Then the interaction histories of all users are fed into the pre-trained model to obtain feature embedding $\{ e _ { u } \} _ { u \in \mathcal { U } }$ representing historical behaviors. Subsequently, for each target user u, we retrieve k similar users $\mathcal { S } _ { u } = \{ u ^ { \prime } , u ^ { \prime \prime } , . . . \}$ based on cosine similarity sim $( e _ { u ^ { \prime } } , e _ { u } )$ . Crucially, we ensure that all retrieved similar users are sourced from the knowledge base (i.e., the training set), so their subsequent interacted items are known. Finally, we aggregate the keywords $\{ \mathcal { K } _ { u ^ { * } } \} _ { u ^ { * } \in \mathcal { S } _ { u } }$ corresponding to the items subsequently interacted with by these similar users, which serve as auxiliary contextual information for the MLLM in the next stage of recommendation.

## 3.5 Multi-Task Learning Stage

After completing the preparations in the summarization and retrieval stages, the contextual information required by the MLLM for recommendation has been fully integrated. According to the definition of SR, given user interaction history $\mathcal { H } _ { u } ,$ , an MLLM-based recommendation system leverages prompts containing keywords of interacted items $\kappa _ { u }$ , keywords of items interacted by similar users $\{ \mathcal { K } _ { u ^ { * } } \} _ { u ^ { * } \in \mathcal { S } _ { u } }$ , textual descriptions $t e x t _ { n + 1 }$ and image $i m g _ { n + 1 }$ <sub>1</sub> of candidate item, as well as designed recommendation instructions, to predict the probability of user interaction with candidate items. During the recommendation process, we employ a prompt template as illustrated in Table 2 and compute the probability of recommending candidate items based on the probability distribution of the first token generated by the MLLM: $\begin{array} { r } { p = \frac { p ( \prime \mathrm { y e s } ^ { \prime } ) } { p ( \prime \mathrm { y e s } ^ { \prime } ) + p ( \prime \mathrm { n o } ^ { \prime } ) } } \end{array}$

![](images/d11e51f3f36bf8781e3a4898050fee6bd18d4bb6b97ecc4d2bd2255ee43453f3.jpg)  
Table 2: Prompt template for multimodal sequential recommendation.

To align the capabilities of MLLMs with SR, the model must be fine-tuned to minimize the discrepancy between predicted and actual user interactions. We construct the fine-tuning data using a combination of positive and negative sampling: positive samples represent items with which the user interacts in the future, while negative samples are randomly selected from items that the user has not interacted with. This approach enables the model to distinguish between relevant and irrelevant items through contrastive learning, thereby improving its predictive accuracy. Furthermore, inspired by LC-Rec [29], we uniformly construct multiple types of recommendation instructions along with their corresponding training data. This strategy helps the model develop a comprehensive understanding of the recommendation task while mitigating overfitting, as illustrated Table 2.

Fine-tuning employs the next-token prediction paradigm, training the model to predict subsequent tokens in a sequence based on preceding tokens. This ensures the generation of coherent and contextually relevant outputs from the input sequence. The supervised fine-tuning loss function is defined as:

$$
\mathcal {L} _ {\mathrm{SFT}} = - \frac {1}{N} \sum_ {i = 1} ^ {N} \sum_ {t = 1} ^ {T} \log P (y _ {t} ^ {(i)} | x ^ {(i)}, y _ {<   t} ^ {(i)})
$$

Furthermore, we adopt Low-Rank Adaption (LoRA) [8] following the parametereficient fine-tuning (PEFT) [5] framework, thereby accelerating the training process while preserving the model’s inherent in-context learning capability.

## 4 Experiment

## 4.1 Dataset

We utilized open-source and real-world datasets from diverse recommendation domains to ensure broad applicability and robust validation: (1) Microlens [18], a micro-video recommendation dataset; (2) Amazon Baby [6], from the ecommerce domain, representing dense purchasing behavior in the baby product category; and (3) Amazon Games [16], which reflects user preferences in the digital goods sector. All datasets comprise user-item interactions, product descriptions, and images. During the preprocessing stage, we filtered out users and items with fewer interactions to ensure that user historical behavior sequences met a minimum length threshold. Following the practice of MLLM-MSR [24], for each user u with a historical sequence of length n, we treated the user’s interaction after time step $n + 1$ as positive samples. Additionally, we randomly selected 20 items with which the user had not interacted as negative samples. We randomly split all impression item lists into training, validation, and test sets in an 8:1:1 ratio. Detailed statistics for these datasets are provided in Table 3.

Table 3: The Statistics of Datasets

<table><tr><td>Dataset</td><td>Microlens</td><td>Amazon Baby</td><td>Amazon Game</td></tr><tr><td>#User</td><td>25411</td><td>41081</td><td>38808</td></tr><tr><td>#Item</td><td>20276</td><td>14393</td><td>13379</td></tr><tr><td>#Interaction</td><td>223263</td><td>400876</td><td>352136</td></tr><tr><td>#Avg Seqlen</td><td>11.35</td><td>13.65</td><td>13.23</td></tr></table>

## 4.2 Experimental Setup

To assess the performance of baseline and our proposed method for multimodal sequential recommendations, we utilize HR@5, NDCG@5 and AUC as evaluation metrics. All models are evaluated in Python 3.10 using PyTorch [19]. All experiments are carried out on a workstation equipped with 8×NVIDIA A800 GPUs running Ubuntu 24.04.2 LTS, using PyTorch 2.6.0 with CUDA 12.9. In the experiments, we conduct inference and training of open-source models based on the MS-Swift [28] framework. All experiments are repeated three times under the same random seed to compute average value. Besides the parameter analysis experiments, in all other experiments, we set the length of user behavior sequences to 5 and the number of retrieved similar users to 3.

## 4.3 Baseline

To evaluate the efectiveness of our proposed method, we select several mainstream methods for comparison covering four categories of recommendation systems:

1. Basic SR Models: These models utilize only item IDs and collaborative information for recommendation. SASRec [11] employs self-attention mechanisms to capture long-term dependencies, BERT4Rec [22] adopts bidirectional selfattention to model user behavior sequences.

2. Multimodal SR Models: Beyond item IDs, these models leverage visual information from item images. MMSR [9] achieves adaptive fusion of multimodal features via graph structures. HM4SR [26] introduces a two-level Mixtureof-Experts (MoE) architecture combined with a multi-task learning strategy to capture dynamic user interests.

3. LLM-based SR Models: These models harness the semantic understanding and in-context learning capabilities of LLMs for recommendation, using both item IDs and textual information. HLLM [3] adopts a two-tower architecture: the first LLM layer extracts content features from item textual descriptions, and the second LLM predicts future user interests based on interaction history. LLM-ESR [14] enhances traditional SR models by incorporating semantic embeddings generated by LLMs.

4. MLLM-based SR Models: These models comprehensively utilize multimodal information and leverage the visual comprehension capabilities of MLLMs for recommendation. MLLM-MSR [24] converts item images and text into natural language descriptions via MLLMs and infers user preferences through multiple rounds of LLM reasoning. MLLMRec [4] employs MLLMs to transform item information into high-quality semantic descriptions, which are then integrated into an item-item graph learning framework for recommendation.

## 4.4 Main Results

Table 4 presents a comparison between our proposed MMSRARec and baseline methods across three real-world datasets. MMSRARec achieves the best or second-best performance across all evaluation metrics. Specifically, it attains Hit Rate @5 scores of 85.1, 81.5, and 83.7, significantly outperforming the suboptimal models, which achieve 81.3, 77.6, and 79.8, respectively. These results indicate that MMSRARec is capable of capturing user preferences and recommending appropriate items accordingly. Overall, recommendation methods leveraging multimodal information demonstrate superior performance compared to those relying solely on ID and textual data. Moreover, approaches based on LLM or MLLM outperform traditional deep neural network-based models. This underscores the importance of integrating MLLMs to interpret multimodal item information within recommendation systems.

Table 4: Comparison of sequential recommendation performance of diferent models. The optimal results are marked in bold, and the suboptimal results are marked with underlines.

<table><tr><td rowspan="2">Model</td><td colspan="3">Microlens</td><td colspan="3">Amazon Baby</td><td colspan="3">Amazon Games</td></tr><tr><td>HR@5</td><td>AUC</td><td>NDCG@5</td><td>HR@5</td><td>AUC</td><td>NDCG@5</td><td>HR@5</td><td>AUC</td><td>NDCG@5</td></tr><tr><td>SASRec (ICDM&#x27;18)</td><td>66.64</td><td>74.02</td><td>31.20</td><td>58.24</td><td>71.06</td><td>27.56</td><td>62.36</td><td>80.54</td><td>29.66</td></tr><tr><td>BERT4Rec (CIKM&#x27;19)</td><td>54.47</td><td>72.55</td><td>28.99</td><td>50.85</td><td>73.45</td><td>25.41</td><td>55.15</td><td>73.68</td><td>27.25</td></tr><tr><td>MMSR (CIKM&#x27;23)</td><td>69.85</td><td>78.87</td><td>49.75</td><td>65.44</td><td>79.01</td><td>44.22</td><td>68.93</td><td>81.19</td><td>47.53</td></tr><tr><td>HM4SR (WWW&#x27;25)</td><td>76.46</td><td>80.23</td><td>57.86</td><td>72.37</td><td>82.15</td><td>53.60</td><td>75.27</td><td>83.59</td><td>55.81</td></tr><tr><td>HLLM (&#x27;24)</td><td>71.23</td><td>76.54</td><td>30.52</td><td>67.86</td><td>77.28</td><td>26.98</td><td>70.11</td><td>78.84</td><td>28.49</td></tr><tr><td>LLM-ESR (NIPS&#x27;24)</td><td>68.25</td><td>77.81</td><td>62.67</td><td>64.59</td><td>78.63</td><td>55.85</td><td>67.20</td><td>79.45</td><td>57.92</td></tr><tr><td>MLLM-MSR (AAAI&#x27;25)</td><td>77.42</td><td>83.17</td><td>54.26</td><td>73.92</td><td>84.39</td><td>58.57</td><td>76.39</td><td>85.69</td><td>63.73</td></tr><tr><td>MLLMRec (&#x27;25)</td><td>81.32</td><td>83.25</td><td>68.25</td><td>77.61</td><td>81.79</td><td>61.24</td><td>79.86</td><td>82.16</td><td>58.40</td></tr><tr><td>MMSRARec</td><td>85.09</td><td>84.36</td><td>66.12</td><td>81.50</td><td>85.27</td><td>62.82</td><td>83.74</td><td>85.81</td><td>63.14</td></tr></table>

Another advantage of language model-based recommendation systems lies in their interpretability. Tables 5present recommendation cases from the Microlens and Amazon Baby datasets. The keywords summarized during the multimodal summarization stage efectively capture the key characteristics of items, significantly reduce the required input context length, and ofer stronger interpretability compared to non-readable vectors or semantic IDs. For instance, in Microlens, the keywords generated by MMSRARec indicate that the user’s historical videos are all related to the mobile game "Kings of Glory." As a result, the model recommends videos related to this game while excluding those associated with another game, "Genshin." These examples demonstrate that leveraging MLLMs to summarize keywords can efectively extract essential item information and align MLLM with the space of recommendation, thereby enhancing both recommendation accuracy and interpretability. In contrast, existing methods that rely solely on pretrained MLLMs for feature extraction exhibit certain limitations.

## 4.5 Parameter Analysis

We further investigate the impact of two key hyperparameters in the experiments on recommendation performance: the length of the user’s historical behavior sequence n and the number of retrieved similar users $ { \boldsymbol { S } } _ { u }$ , as shown in Fig. 3. When the behavior sequence is short, the limited contextual information hinders the model’s ability to accurately capture user interests. As the sequence length increases, the model gains access to more comprehensive user information, leading to improved recommendation performance. However, long behavior sequences may introduce noise from earlier interactions, which can interfere with the model’s judgment and prevent further performance gains. The incorporation of similar user retrieval yields a noticeable performance improvement, underscoring the importance of integrating collaborative signals into MLLM-based recommendation systems. Similarly, retrieving too many similar users increases the context length, which can dilute the model’s focus and cause performance to converge.

Table 5: Recommended cases on Microlens and Amazon Baby dataset.

<table><tr><td>User Behavior</td><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td><td>Candidate</td><td>Candidate</td></tr><tr><td>ID</td><td>2259</td><td>6810</td><td>3325</td><td>12352</td><td>17383</td><td>8710</td><td>6398</td></tr><tr><td>Cover</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>Title</td><td>Gong sun li</td><td>National best shooter</td><td>Solo</td><td>Hades Side Road</td><td>New hero Goya</td><td>Shaoxing and Yaoyao</td><td>Not enemy, just different positions</td></tr><tr><td>Keywords by MM-SRARRec</td><td>character depiction, Kings of Glory, Gongsun Li, game strategies</td><td>mobile game, character depiction, game play experience</td><td>mobile game character, solo kill, Kings of Glory</td><td>character depiction, Hades Side Road, game play</td><td>Kings of Glory, Goya, character depiction, player achieves</td><td>mobile game, Kings of Glory, strategic moment</td><td>Genshin character, Dawn Roses, Challenge</td></tr><tr><td>Recommend</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>√</td><td>×</td></tr><tr><td></td><td colspan="7"></td></tr><tr><td>ID</td><td>457</td><td>1178</td><td>5056</td><td>1022</td><td>1177</td><td>134</td><td>13420</td></tr><tr><td>Cover</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>Title</td><td>Munchkin® Miracle® 360 Toddler Sippy Cup</td><td>Safety 1st Child Proof Clear View Stove Knob Covers</td><td>Baby Cotton Swabs</td><td>Boudreaux&#x27;s Butt Paste Original Diaper Rash Cream</td><td>Amazon Elements Baby Wipes</td><td>Pampers Cruisers Diapers Size 7 44 Count</td><td>Stephen Joseph Growth Chart, Dino</td></tr><tr><td>Keywords by MM-SRARRec</td><td>Munchkin Miracle 360 Sippy Cup, Pink/Purple, 10 Oz, 2 Count</td><td>Child Proof Clear View Stove Knob, Set of 5, Children Safety</td><td>Baby Cotton Swabs, Organic Fragrance and Chlorine-Free, 100% Biodegradable, 4 Packs of 56</td><td>Boudreaux&#x27;s Butt Paste Original Diaper Rash Cream, Ointment for Baby, 4 oz Tube, 3 Pack</td><td>Amazon Elements Baby Wipes, Fresh Scent, 480 Count, Flip-Top Packs, cucumber, aloe and green tea oil</td><td>Pampers Cruisers Diapers, Size 7, 44 Count, 2x stretchier</td><td>Stephen Joseph Growth Chart, colorful, education</td></tr><tr><td>Recommend</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>√</td><td>×</td></tr></table>

In summary, achieving optimal recommendation performance requires appropriate selection of both historical behavior sequence length and the number of similar users retrieved.

## 4.6 Ablation Study

Table 6 presents the results of ablation study conducted on diferent stages of the model. $" \mathrm { w } / \mathrm { o } \mathrm { s } 1 "$ denotes the removal of the summarization stage, where original item descriptions are used directly. "w/o s1-training" indicates that no RLVR training is performed in the first stage. $" \mathrm { w } / \mathrm { o } \ \mathrm { s } 2 "$ refers to the absence of similar user retrieval in the second stage. "with s2-GRU4Rec" means swith the embedding model of similar users to GRU4Rec [7]. $" \mathrm { w } / \mathrm { o } \ \mathrm { s } 3 "$ signifies that no training is applied in the third stage, with only the pre-trained MLLM being utilized. $" \mathrm { w / o }$ s3-multitasks" represents that in the third stage, only basic instructions are used for instruction fine-tuning instead of multi-task learning. The experimental results demonstrate that in the multimodal summarization stage, our designed reward—which comprehensively considers information loss, reconstruction dificulty, and summary length—enables the model to adaptively adjust its summarization strategy, yielding outputs that are more precise and concise compared to the original item descriptions. During the similar user retrieval stage, the incorporation of collaborative signals assists the model in making references and judgments. In the multi-task learning stage, our designed training tasks facilitate the model’s comprehensive understanding of the multimodal sequential recommendation task.

![](images/35cffb9c613e4ade85cf843ef2d9660ca063ccf7621fa20bc972ca809f02888b.jpg)  
(a) Analysis of n

![](images/72a316d99cc39ee4f5339678beb6d70a9135988ec636727adc37a87f6aa0f8ca.jpg)  
(b) Analysis of |S<sub>u</sub>|  
Fig. 3: Performance of adjusting the length of the user’s historical behavior sequence n and the number of similar users retrieved $| \mathcal { S } _ { u } |$

Table 6: Performance of MMSRARec with diferent ablation strategy.

<table><tr><td rowspan="2">Model</td><td colspan="3">Amazon Baby</td><td colspan="3">Amazon Games</td></tr><tr><td>HR@5</td><td>AUC</td><td>NDCG@5</td><td>HR@5</td><td>AUC</td><td>NDCG@5</td></tr><tr><td>MMSRARec</td><td>81.50</td><td>85.27</td><td>62.82</td><td>83.74</td><td>85.81</td><td>63.14</td></tr><tr><td>w/o s1</td><td>78.91</td><td>83.59</td><td>60.12</td><td>80.54</td><td>84.22</td><td>60.88</td></tr><tr><td>w/o s1-training</td><td>79.26</td><td>83.82</td><td>60.58</td><td>81.00</td><td>84.58</td><td>61.26</td></tr><tr><td>w/o s2</td><td>75.36</td><td>77.63</td><td>56.92</td><td>78.50</td><td>80.26</td><td>59.49</td></tr><tr><td>with s2-GRU4Rec</td><td>76.88</td><td>81.25</td><td>59.73</td><td>77.21</td><td>83.36</td><td>60.10</td></tr><tr><td>w/o s3-training</td><td>26.87</td><td>18.62</td><td>19.59</td><td>37.74</td><td>42.11</td><td>24.85</td></tr><tr><td>w/o s3-multitasks</td><td>76.24</td><td>80.18</td><td>57.52</td><td>77.55</td><td>81.33</td><td>58.14</td></tr></table>

## 4.7 Eficiency Analysis

Furthermore, we analyze the impact of diferent MLLM backbones on recommendation eficiency and compare our approach with MLLM-MSR [24], a baseline method that also employs MLLMs as recommenders. The multiple inference steps and substantial time overhead of MLLM-MSR highlight the limitations of existing methods in processing user behavior sequences. Among the three compared models, Qwen2.5VL [1] achieves the best recommendation performance, followed by InternVL3 [32]. LLaVA [13] performs the worst, which may be attributed to the lack of a training corpus relevant to multimodal sequential recommendation in its pre-training data. Additionally, while the larger Qwen2.5VL-32B model shows marginal improvement over its smaller 7B counterpart, its significantly higher training and inference costs make it unsuitable for practical online deployment. MMSRARec can accommodate arbitrary MLLM backbones, demonstrating the robustness of its architectural design.

Table 7: Eficiency of MMSRARec with diferent MLLM backbone and baseline.

<table><tr><td rowspan="2">Model</td><td colspan="3">Amazon Baby</td><td colspan="3">Amazon Games</td><td rowspan="2"># Inferences</td><td rowspan="2">Time (s)</td></tr><tr><td>HR@5</td><td>AUC</td><td>NDCG@5</td><td>HR@5</td><td>AUC</td><td>NDCG@5</td></tr><tr><td>MLLM-MSR-LlaVA1.5-7B [24]</td><td>73.92</td><td>84.39</td><td>58.57</td><td>76.39</td><td>85.69</td><td>63.73</td><td>6</td><td>7.35</td></tr><tr><td>MMSRARec-LlaVA1.5-7B</td><td>76.26</td><td>81.33</td><td>57.69</td><td>71.23</td><td>62.34</td><td>60.46</td><td>1</td><td>0.54</td></tr><tr><td>MMSRARec-InternVL3-8B</td><td>78.67</td><td>86.12</td><td>60.50</td><td>82.96</td><td>85.26</td><td>62.33</td><td>1</td><td>0.82</td></tr><tr><td>MMSRARec-Qwen2.5VL-7B</td><td>81.50</td><td>85.27</td><td>62.82</td><td>83.74</td><td>85.81</td><td>63.14</td><td>1</td><td>0.73</td></tr><tr><td>MMSRARec-Qwen2.5VL-32B</td><td>82.05</td><td>87.28</td><td>66.75</td><td>82.56</td><td>87.41</td><td>65.88</td><td>1</td><td>1.13</td></tr></table>

## 5 Conclusion and Future Work

This paper proposes a novel method named MMSRARec for multimodal sequential recommendation, based on a multimodal large language model (MLLM). We first employ the MLLM to summarize items into concise keywords and finetune the model using rewards that incorporate summary length, information loss, and reconstruction dificulty, thereby enabling adaptive adjustment of the summarization strategy. Inspired by retrieval-augmented generation, we convert collaborative signals into corresponding keywords and integrate them as contextual input. Finally, we apply supervised fine-tuning with multi-task learning to align the MLLM’s capabilities with the requirements of multimodal sequential recommendation. This approach leverages the MLLM’s strong semantic understanding and in-context learning abilities, introduces previously overlooked collaborative signals into the MLLM, and reduces computational and time costs through once MLLM inference. Experiments on three real-world recommendation datasets demonstrate that MMSRARec achieves a better understanding of multimodal item information and user preferences, enabling accurate and interpretable recommendations.

Currently, the MLLM backbone used in MMSRARec contains 7B parameters, leading to longer inference times compared to traditional sequential recommendation models. In the future, we plan to explore methods such as distillation, output decoding, and pruning to replace the current backbone with a smaller model, thereby accelerating MMSRARec without compromising performance.

## References

1. Bai, S., Chen, K., Liu, X., Wang, J., Ge, W., Song, S., Dang, K., Wang, P., Wang, S., Tang, J., et al.: Qwen2. 5-vl technical report. arXiv preprint arXiv:2502.13923 (2025)

2. Boka, T.F., Niu, Z., Neupane, R.B.: A survey of sequential recommendation systems: Techniques, evaluation, and future directions. Information Systems 125, 102427 (2024)

3. Chen, J., Chi, L., Peng, B., Yuan, Z.: Hllm: Enhancing sequential recommendations via hierarchical large language models for item and user modeling. arXiv preprint arXiv:2409.12740 (2024)

4. Dang, Y., Zhang, X., Pan, Z., Duan, Y., Chen, W., Cai, F., Chen, H.: Mllmrec: Exploring the potential of multimodal large language models in recommender systems. arXiv preprint arXiv:2508.15304 (2025)

5. Ding, N., Qin, Y., Yang, G., Wei, F., Yang, Z., Su, Y., Hu, S., Chen, Y., Chan, C.M., Chen, W., et al.: Parameter-eficient fine-tuning of large-scale pre-trained language models. Nature machine intelligence 5(3), 220–235 (2023)

6. He, R., McAuley, J.: Ups and downs: Modeling the visual evolution of fashion trends with one-class collaborative filtering. In: proceedings of the 25th international conference on world wide web. pp. 507–517 (2016)

7. Hidasi, B., Karatzoglou, A., Baltrunas, L., Tikk, D.: Session-based recommendations with recurrent neural networks. arXiv preprint arXiv:1511.06939 (2015)

8. Hu, E.J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, L., Chen, W., et al.: Lora: Low-rank adaptation of large language models. ICLR 1(2), 3 (2022)

9. Hu, H., Guo, W., Liu, Y., Kan, M.Y.: Adaptive multi-modalities fusion in sequential recommendation systems. In: Proceedings of the 32nd ACM International Conference on Information and Knowledge Management. pp. 843–853 (2023)

10. Hurst, A., Lerer, A., Goucher, A.P., Perelman, A., Ramesh, A., Clark, A., Ostrow, A., Welihinda, A., Hayes, A., Radford, A., et al.: Gpt-4o system card. arXiv preprint arXiv:2410.21276 (2024)

11. Kang, W.C., McAuley, J.: Self-attentive sequential recommendation. In: 2018 IEEE international conference on data mining (ICDM). pp. 197–206. IEEE (2018)

12. Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W.t., Rocktäschel, T., et al.: Retrieval-augmented generation for knowledge-intensive nlp tasks. Advances in neural information processing systems 33, 9459–9474 (2020)

13. Liu, H., Li, C., Wu, Q., Lee, Y.J.: Visual instruction tuning. Advances in neural information processing systems 36, 34892–34916 (2023)

14. Liu, Q., Wu, X., Wang, Y., Zhang, Z., Tian, F., Zheng, Y., Zhao, X.: Llm-esr: Large language models enhancement for long-tailed sequential recommendation. Advances in Neural Information Processing Systems 37, 26701–26727 (2024)

15. Luo, Y., Qin, Q., Zhang, H., Cheng, M., Yan, R., Wang, K., Ouyang, J.: Molar: Multimodal llms with collaborative filtering alignment for enhanced sequential recommendation. arXiv preprint arXiv:2412.18176 (2024)

16. McAuley, J., Targett, C., Shi, Q., Van Den Hengel, A.: Image-based recommendations on styles and substitutes. In: Proceedings of the 38th international ACM SIGIR conference on research and development in information retrieval. pp. 43–52 (2015)

17. Mroueh, Y.: Reinforcement learning with verifiable rewards: Grpo’s efective loss, dynamics, and success amplification. arXiv preprint arXiv:2503.06639 (2025)

18. Ni, Y., Cheng, Y., Liu, X., Fu, J., Li, Y., He, X., Zhang, Y., Yuan, F.: A content-driven micro-video recommendation dataset at scale. arXiv preprint arXiv:2309.15379 (2023)

19. Paszke, A., Gross, S., Massa, F., Lerer, A., Bradbury, J., Chanan, G., Killeen, T., Lin, Z., Gimelshein, N., Antiga, L., et al.: Pytorch: An imperative style, highperformance deep learning library. Advances in neural information processing systems 32 (2019)

20. Resnick, P., Varian, H.R.: Recommender systems. Communications of the ACM 40(3), 56–58 (1997)

21. Shao, Z., Wang, P., Zhu, Q., Xu, R., Song, J., Bi, X., Zhang, H., Zhang, M., Li, Y., Wu, Y., et al.: Deepseekmath: Pushing the limits of mathematical reasoning in open language models. arXiv preprint arXiv:2402.03300 (2024)

22. Sun, F., Liu, J., Wu, J., Pei, C., Lin, X., Ou, W., Jiang, P.: Bert4rec: Sequential recommendation with bidirectional encoder representations from transformer. In: Proceedings of the 28th ACM international conference on information and knowledge management. pp. 1441–1450 (2019)

23. Team, G., Anil, R., Borgeaud, S., Alayrac, J.B., Yu, J., Soricut, R., Schalkwyk, J., Dai, A.M., Hauth, A., Millican, K., et al.: Gemini: a family of highly capable multimodal models. arXiv preprint arXiv:2312.11805 (2023)

24. Ye, Y., Zheng, Z., Shen, Y., Wang, T., Zhang, H., Zhu, P., Yu, R., Zhang, K., Xiong, H.: Harnessing multimodal large language models for multimodal sequential recommendation. In: Proceedings of the AAAI Conference on Artificial Intelligence. vol. 39, pp. 13069–13077 (2025)

25. Zhang, C., Zhang, H., Wu, S., Wu, D., Xu, T., Zhao, X., Gao, Y., Hu, Y., Chen, E.: Notellm-2: Multimodal large representation models for recommendation. In: Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V. 1. pp. 2815–2826 (2025)

26. Zhang, S., Chen, L., Shen, D., Wang, C., Xiong, H.: Hierarchical time-aware mixture of experts for multi-modal sequential recommendation. In: Proceedings of the ACM on Web Conference 2025. pp. 3672–3682 (2025)

27. Zhang, Z., Liu, S., Liu, Z., Zhong, R., Cai, Q., Zhao, X., Zhang, C., Liu, Q., Jiang, P.: Llm-powered user simulator for recommender system. In: Proceedings of the AAAI Conference on Artificial Intelligence. vol. 39, pp. 13339–13347 (2025)

28. Zhao, Y., Huang, J., Hu, J., Wang, X., Mao, Y., Zhang, D., Jiang, Z., Wu, Z., Ai, B., Wang, A., et al.: Swift: a scalable lightweight infrastructure for fine-tuning. In: Proceedings of the AAAI Conference on Artificial Intelligence. vol. 39, pp. 29733– 29735 (2025)

29. Zheng, B., Hou, Y., Lu, H., Chen, Y., Zhao, W.X., Chen, M., Wen, J.R.: Adapting large language models by integrating collaborative semantics for recommendation. In: 2024 IEEE 40th International Conference on Data Engineering (ICDE). pp. 1435–1448. IEEE (2024)

30. Zhou, P., Liu, C., Ren, J., Zhou, X., Xie, Y., Cao, M., Rao, Z., Huang, Y.L., Chong, D., Liu, J., et al.: When large vision language models meet multimodal sequential recommendation: An empirical study. In: Proceedings of the ACM on Web Conference 2025. pp. 275–292 (2025)

31. Zhu, J., Zhou, X., Wu, C., Zhang, R., Dong, Z.: Multimodal pretraining and generation for recommendation: A tutorial. In: Companion Proceedings of the ACM Web Conference 2024. pp. 1272–1275 (2024)

32. Zhu, J., Wang, W., Chen, Z., Liu, Z., Ye, S., Gu, L., Tian, H., Duan, Y., Su, W., Shao, J., et al.: Internvl3: Exploring advanced training and test-time recipes for open-source multimodal models. arXiv preprint arXiv:2504.10479 (2025)


---

# 2604.20848

[2604.20848](https://arxiv.org/abs/2604.20848)

# MATRAG: Multi-Agent Transparent Retrieval-Augmented Generation for Explainable Recommendations

Sushant Mehta

sushant0523@gmail.com

## Abstract

Large Language Model (LLM)-based recommendation systems have demonstrated remarkable capabilities in understanding user prefer ences and generating personalized suggestions. However, existing approaches face critical challenges in transparency, knowledge grounding, and the ability to provide coherent explanations that foster user trust. We introduce MATRAG (Multi-Agent Transparent Retrieval-Augmented Generation), a novel framework that com bined multi-agent collaboration with knowledge graph-augmented retrieval to deliver explainable recommendations. MATRAG em ploys four specialized agents: a User Modeling Agent that con structs dynamic preference profiles, an Item Analysis Agent that extracts semantic features from knowledge graphs, a Reasoning Agent that synthesizes collaborative and content-based signals, and an Explanation Agent that generates natural language justifications grounded in retrieved knowledge. Our framework incorporates a transparency scoring mechanism that quantifies explanation faith fulness and relevance. Extensive experiments on three benchmark datasets (Amazon Reviews, MovieLens-1M, and Yelp) demonstrate that MATRAG achieves state-of-the-art performance, improving recommendation accuracy by 12.7% (Hit Rate) and 15.3% (NDCG) over leading baselines, while human evaluation confirms that 87.4% of generated explanations are rated as helpful and trustworthy by domain experts. Our work establishes new benchmarks for trans parent, agentic recommendation systems and provides actionable insights for deploying LLM-based recommenders in production environments.

## CCS Concepts

• Information systems → Recommender systems; • Comput ing methodologies → Natural language processing; Multi-agent systems.

## Keywords

Large Language Models, Multi-Agent Systems, Recommender Systems, Retrieval-Augmented Generation, Explainable AI, Knowledge Graphs, Transparency

## ACM Reference Format:

Sushant Mehta. 2026. MATRAG: Multi-Agent Transparent Retrieval-Augmented Generation for Explainable Recommendations. In Proceedings of Companion

Proceedings of the ACM Web Conference 2026 (WWW ’26). ACM, New York, NY, USA, 8 pages. https://doi.org/10.1145/XXXXXXX.XXXXXXX

## 1 Introduction

Recommendation systems have become indispensable components of modern web platforms, influencing how billions of users discover products, content, and services [17, 36]. The emergence of Large Language Models (LLMs) has catalyzed a paradigm shift from traditional collaborative filtering and content-based approaches toward agentic systems capable of reasoning, planning, and engaging in natural dialogue with users [15, 18]. However, as these systems grow more sophisticated, they face mounting challenges in three critical dimensions: transparency, knowledge grounding, and multistakeholder coordination.

First, LLM-based recommenders often operate as opaque decisionmaking systems, generating suggestions without articulating the reasoning behind their choices [25]. This opacity erodes user trust and limits adoption in high-stakes domains such as healthcare, finance, and e-commerce [6]. Users increasingly demand not just accurate recommendations but also comprehensible explanations that reveal how their preferences were understood and why specific items were selected [27].

Second, while LLMs possess extensive world knowledge acquired during pre-training, they frequently hallucinate facts, conflate entities, or fail to incorporate domain-specific and up-to-date information [34]. Retrieval-Augmented Generation (RAG) has emerged as a promising solution, grounding LLM outputs in retrieved evidence from external knowledge sources [3, 44]. However, standard RAG approaches retrieve isolated text chunks, ignoring the rich relational structure that knowledge graphs capture about items, users, and their interconnections.

Third, the recommendation ecosystem involves multiple stakeholders: users, items, platforms, and increasingly autonomous agents, whose interests must be balanced and coordinated [43]. Singleagent LLM systems struggle to decompose complex recommendation tasks, maintain coherent reasoning across multiple turns, and synthesize diverse signals from heterogeneous data sources [33].

To address these interconnected challenges, we propose MA-TRAG (Multi-Agent Transparent Retrieval-Augmented Generation), a novel framework that unifies multi-agent collaboration, knowledge graph-augmented retrieval, and explainable recommendation generation. MATRAG orchestrates four specialized LLM-based agents: (1) a User Modeling Agent that constructs and updates dynamic preference profiles from interaction histories and natural language feedback; (2) an Item Analysis Agent that retrieves and syn thesizes structured knowledge from item-centric knowledge graphs; (3) a Reasoning Agent that integrates collaborative filtering signals with semantic item representations through deliberative planning;

and (4) an Explanation Agent that generates faithful, grounded nat ural language explanations by tracing the reasoning chain back to retrieved evidence.

Central to our framework is a Transparency Scoring Module that quantifies explanation quality along three dimensions: factual faithfulness to retrieved knowledge, logical coherence with the recom mendation rationale, and personalization alignment with inferred user preferences. This module enables both automated evaluation and human-in-the-loop refinement of explanation quality.

Our contributions are summarized as follows:

• We introduce MATRAG, a multi-agent framework that combines knowledge graph-augmented retrieval with specialized agents for transparent, explainable recommendations (Sec tion 3).

• We propose a transparency scoring mechanism that enables quantitative assessment of explanation faithfulness, coherence, and personalization (Section 3.3).

• We conduct extensive experiments on three benchmark datasets, demonstrating state-of-the-art performance in recommendation accuracy and explanation quality (Section 4).

• We present human expert evaluations confirming that MA TRAG generates explanations rated as helpful and trustworthy by 87.4% of evaluators (Section 4.4).

## 2 Related Work

## 2.1 LLM-Based Recommendation Systems

The integration of LLMs into recommendation systems has evolved in two primary paradigms [17, 36]. The discriminative paradigm fine-tunes LLMs to recommendation-specific objectives, using language models as feature extractors or scoring functions [1, 11]. The generative paradigm frames recommendation as text generation, directly producing item identifiers or descriptions [5, 15]. Recent work has explored hybrid approaches that leverage LLMs for both understanding and generation while maintaining eficiency through knowledge distillation [18].

InteRecAgent [12] pioneered the integration of LLMs with tradi tional recommender models through a tool-augmented architecture, treating specialized models as callable tools. RecMind [32] extended this paradigm with self-inspired planning, allowing LLMs to decompose complex recommendation queries into subtasks. However, these single-agent approaches lack the specialization and coordi nation capabilities necessary for handling diverse user needs and multi-faceted item representations.

## 2.2 Multi-Agent Systems for Recommendations

Multi-agent collaboration has emerged as a powerful paradigm for complex AI tasks [10, 16, 35]. In recommendation contexts, MACRec [33] introduced a framework with specialized agents for user analysis, item analysis, and reflection, demonstrating improved diversity and precision through agent collaboration. Agent4Rec [41] deployed generative agents for user simulation, providing insights into phenomena like filter bubbles. AgentCF [42] modeled both users and items as agents, enabling collaborative learning that captures two-sided interaction dynamics.

More recent work has explored multi-agent conversational recommendation systems (MACRS) [4], coordinating interactions across multiple agents to optimize real-time recommendations. However, existing multi-agent approaches typically focus on either simulation or task decomposition, without explicitly addressing the transparency and explainability requirements essential for user trust.

## 2.3 RAG and Knowledge Graphs for Recommendations

Retrieval-Augmented Generation has proven efective in grounding LLM outputs in external knowledge [14]. GraphRAG [3] improved the standard RAG by constructing knowledge graphs from text corpora, enabling community-based summarization and improved reasoning over connected information. K-RagRec [34] specifically adapted the RAG knowledge graph for recommendations, developing hop-field knowledge sub-graphs for semantic indexing and popularity-selective retrieval.

Knowledge graphs have long been recognized as valuable resources for recommendation systems, capturing rich semantic relationships between users, items, and attributes [30]. Recent work has explored LLM-KG integration for explainable recommendations, using knowledge graphs to provide factual grounding for generated explanations [26, 37]. Our work extends this line by incorporating knowledge graph retrieval directly into a multi-agent collaborative framework.

## 2.4 Explainable Recommendations

Explainability has become a central concern in the research of recommendation systems [40]. Traditional approaches generated explanations from feature attributions, attention weights, or templatebased natural language generation [2]. The advent of LLMs has opened new possibilities for generating rich, contextual explanations [25]. Silva et al. [27] demonstrated that ChatGPT can produce human-centered explanations that improve user engagement. Lubos et al. [19] found that users generally prefer LLM-generated explanations for their creativity and depth.

However, LLM-generated explanations face the challenge of faithfulness: whether the explanation accurately reflects the actual reasoning process [7]. Our transparency scoring mechanism addresses this challenge directly by grounding explanations in retrievable evidence and quantifying alignment with the rationale of the recommendation.

## 3 Methodology

## 3.1 Problem Formulation

Let $\mathbf { \mathcal { U } } = \left\{ u _ { 1 } , u _ { 2 } , \ldots , u _ { n } \right\}$ denote the set of users and ${ \cal { I } } = \{ i _ { 1 } , i _ { 2 } , \dots , i _ { m } \}$ the set of items. Each user <sup>??</sup> has an interaction history $\mathcal { H } _ { u } ~ =$ $\{ ( i , r , t , c ) | i \in \mathcal { I } \}$ where <sup>??</sup> is the rating, <sup>??</sup> is the timestamp, and <sup>??</sup> is optional textual feedback (reviews, comments). A knowledge graph $\mathcal { G } = ( \mathcal { E } , \mathcal { R } , \mathcal { T } )$ represents entities E (including items and attributes), relations R, and triples $\mathcal { T } \subseteq \mathcal { E } \times \mathcal { R } \times \mathcal { E }$

Given a user <sup>??</sup> with history $\mathcal { H } _ { u }$ and an optional natural language query <sup>??</sup>, the goal is to: (1) generate a ranked list of recommendations $\hat { J } _ { u } = [ i _ { 1 } ^ { * } , i _ { 2 } ^ { * } , \ldots , i _ { k } ^ { * } ]$ ; and (2) for each recommended item $i ^ { * } { } _ { ; }$ , produce an explanation $e _ { i ^ { * } }$ that is faithful to the reasoning process and grounded in the retrieved knowledge.

![](images/1809a8ad7017aaff9dbafd8536ec26e13d4b96861b4e6833c24e9ef18648c3cf.jpg)  
Figure 1: Overview of the MATRAG framework showing four specialized agents coordinated by the orchestrator, with knowledge graph retrieval and transparency scoring.

## 3.2 Framework Overview

MATRAG comprises four specialized agents coordinated by a cen tral orchestrator, as illustrated in Figure 1. Each agent is instantiated as an LLM augmented with role-specific instructions, memory, and tool access.

3.2.1 Orchestrator Agent. The Orchestrator manages the overall recommendation workflow, determining which agents to invoke, in what sequence, and how to synthesize their outputs. Given a user request, the Orchestrator:

(1) Analyzes the request type (e.g., cold-start, re-ranking, conversational);

(2) Dispatches subtasks to appropriate agents;

(3) Aggregates agent outputs and resolves conflicts;

(4) Triggers the Transparency Scoring Module for quality assessment.

The Orchestrator employs a ReAct-style [38] reasoning loop, interleaving thought, action, and observation steps to maintain coherent multi-step planning.

3.2.2 User Modeling Agent. The User Modeling Agent constructs a dynamic, multi-faceted representation of user preferences. It processes:

• Behavioral signals: Interaction history $\mathcal { H } _ { u }$ including ratings, clicks, purchases, and dwell times;

• Textual feedback: Reviews, comments, and conversational utterances;

• Contextual factors: Time of day, device type, session context.

The agent maintains a structured user profile $P _ { u }$ comprising:

$$
P _ {u} = \{\mathbf {p} ^ {\text { explicit }}, \mathbf {p} ^ {\text { implicit }}, \mathbf {p} ^ {\text { contextual }}, \mathbf {p} ^ {\text { temporal }} \}\tag{1}
$$

where $\mathbf { p } ^ { \mathrm { e x p l i c i t } }$ captures stated preferences, $\mathbf { p } ^ { \mathrm { i m p l i c i t } }$ captures inferred preferences from behavior, $\mathbf { p } ^ { \mathrm { c o n t e x t u a l } }$ captures situational factors, and $\mathbf { p } ^ { \mathrm { t e m p o r a l } }$ captures preference evolution over time.

The agent uses in-context learning to extract preference signals from textual feedback:

$$
\mathbf {p} ^ {\mathrm{explicit}} = \operatorname{LLM} (\operatorname{prompt} _ {\mathrm{user}}, \mathcal {H} _ {u} ^ {\mathrm{text}})\tag{2}
$$

3.2.3 Item Analysis Agent. The Item Analysis Agent retrieves and synthesizes structured knowledge about items from the knowledge graph G. Given a candidate item set $\tau _ { \mathrm { c a n d } }$ , this agent:

(1) Entity Linking: Maps item identifiers to knowledge graph entities;

(2) Subgraph Extraction: Retrieves <sup>??</sup>-hop neighborhoods around item entities;

(3) Relation Filtering: Selects relations relevant to user preferences;

(4) Feature Synthesis: Generates semantic item representations.

For knowledge graph retrieval, we employ a two-stage approach inspired by K-RagRec [34]. First, we use dense retrieval to identify semantically similar knowledge subgraphs:

$$
\mathcal {S} _ {i} = \operatorname{TopK} (\operatorname{sim} (\mathbf {e} _ {q}, \mathbf {e} _ {s}) | s \in \mathcal {G} _ {i})\tag{3}
$$

where $\mathbf { e } _ { q }$ is the query embedding and $\mathbf { e } _ { s }$ are subgraph embeddings. Second, we re-rank retrieved subgraphs using the LLM’s reasoning capabilities:

$$
\hat {\mathcal {S}} _ {i} = \mathrm{LLM-Rerank} (\mathcal {S} _ {i}, P _ {u}, q)\tag{4}
$$

3.2.4 Reasoning Agent. The Reasoning Agent integrates signals from user modeling and item analysis to generate recommendations. It implements a deliberative reasoning process that:

(1) Signal Integration: Combines collaborative filtering signals (similar users’ preferences) with content-based signals (itemattribute matching);

(2) Constraint Satisfaction: Respects user-specified constraints (budget, categories, availability);

(3) Diversity Optimization: Balances relevance with recommendation diversity;

(4) Reasoning Chain Generation: Produces an explicit reasoning trace.

The agent scores each candidate item using a hybrid approach:

$$
s (u, i) = \alpha \cdot s _ {\mathrm{CF}} (u, i) + \beta \cdot s _ {\mathrm{CB}} (u, i) + \gamma \cdot s _ {\mathrm{LLM}} (u, i, \mathcal {S} _ {i})\tag{5}
$$

where $s _ { \mathrm { C F } }$ is the collaborative filtering score, <sup>??</sup> is the contentbased score, and $s _ { \mathrm { L L M } }$ is the LLM’s preference prediction based on retrieved knowledge.

Crucially, the Reasoning Agent outputs not just scores but also a structured reasoning chain $C = [ ( r _ { 1 } , e _ { 1 } ) , ( r _ { 2 } , e _ { 2 } ) , . . . ]$ where each step $( r _ { j } , e _ { j } )$ pairs a reasoning step with supporting evidence from retrieved knowledge.

3.2.5 Explanation Agent. The Explanation Agent transforms the reasoning chain into natural language explanations tailored to user comprehension. It operates in three modes:

• Concise: One-sentence justification highlighting the primary recommendation rationale;

• Detailed: Multi-paragraph explanation covering multiple reasoning aspects;

• Comparative: Explanation contrasting the recommended item with alternatives.

The agent is prompted to ground explanations in retrieved knowl edge:

$$
e _ {i ^ {*}} = \mathrm{LLM} (\mathrm{prompt} _ {\mathrm{explain}}, C, \hat {S} _ {i ^ {*}}, P _ {u})\tag{6}
$$

To ensure faithfulness, the agent is instructed to cite specific evidence from the reasoning chain and retrieved knowledge sub graphs.

## 3.3 Transparency Scoring Module

A key contribution of MATRAG is the Transparency Scoring Mod ule, which quantifies explanation quality along three dimensions.

3.3.1 Faithfulness Score. Faithfulness measures whether the explanation accurately reflects the retrieved evidence and reasoning chain. We compute this using an entailment-based approach:

$$
\mathrm{Faith} (e, \mathcal {C}, \hat {\mathcal {S}}) = \frac {1}{| C _ {e} |} \sum_ {c \in C _ {e}} \mathrm{NLI} (c, \mathcal {C} \cup \hat {\mathcal {S}})\tag{7}
$$

where $C _ { e }$ denotes claims extracted from explanation <sup>??</sup>, and NLI returns 1 if the claim is entailed by the evidence and 0 otherwise.

3.3.2 Coherence Score. Coherence measures the logical consistency and flow of the explanation:

$$
\operatorname{Coher} (e) = \text { LLM - Judge } (e, \text { prompt } _ {\text { coherence }})\tag{8}
$$

where an LLM-as-judge evaluates whether the explanation main tains consistent logic, avoids contradictions, and presents informa tion in a comprehensible sequence.

3.3.3 Personalization Score. Personalization measures alignment between the explanation and the user’s profile:

$$
\operatorname{Pers} (e, P _ {u}) = \operatorname{sim} (\mathbf {e} _ {e}, \mathbf {e} _ {P _ {u}})\tag{9}
$$

where $\mathbf { e } _ { e }$ and $\mathbf { e } _ { P _ { u } }$ are embeddings of the explanation and user profile, respectively.

The overall transparency score combines these dimensions:

$$
\operatorname{Trans} (e) = w _ {1} \cdot \text { Faith } + w _ {2} \cdot \text { Coher } + w _ {3} \cdot \text { Pers }\tag{10}
$$

with weights $w _ { 1 } , w _ { 2 } ,$ <sup>??</sup><sub>3</sub> tuned on human preference data.

## 3.4 Training and Optimization

MATRAG operates primarily in a zero-shot or few-shot manner, leveraging the capabilities of pre-trained LLMs. However, we fine tune specific components:

• Knowledge Graph Embeddings: We train SentenceBERT [23] on the recommendation domain’s knowledge graph for sub graph retrieval;

• Transparency Scorer: We fine-tune a smaller LLM on humanannotated explanation quality data;

• Agent Coordination: We use reinforcement learning from human feedback (RLHF) on the orchestrator to optimize agent invocation sequences.

## 4 Experiments

## 4.1 Experimental Setup

4.1.1 Datasets. We evaluate MATRAG on three benchmark datasets spanning diferent recommendation domains:

• Amazon Reviews (Electronics) [20]: 192,403 users, 63,001 items, 1.68M interactions with textual reviews. We construct a product knowledge graph from Amazon’s product metadata including categories, brands, and related products.

• MovieLens-1M [8]: 6,040 users, 3,706 movies, 1M ratings. We link items to the Freebase knowledge graph via entity matching, providing rich relational information about actors, directors, genres, and production details.

• Yelp [39]: 31,668 users, 38,048 businesses, 1.56M reviews. We construct a knowledge graph from business attributes including location, categories, and user-generated tags.

For each dataset, we use an 80/10/10 train/validation/test split based on temporal order to simulate realistic deployment scenarios.

4.1.2 Baselines. We compare against the following state-of-the-art methods:

• Traditional Methods: BPR [24], LightGCN [9], SASRec [13];

• Knowledge-Enhanced: KGAT [30], KGIN [31];

• LLM-Based: TALLRec [1], Chat-Rec [5], LLMRank [11];

• Agent-Based: InteRecAgent [12], RecMind [32], MACRec [33];

• RAG-Enhanced: K-RagRec [34], G-CRS [22].

4.1.3 Implementation Details. We implement MATRAG using GPT-4 [21] as the backbone LLM for all agents. For knowledge graph retrieval, we use SentenceBERT with a vector dimension of 768. The transparency scorer is based on Llama-3.1-8B [29] fine-tuned on 5,000 human-annotated explanation pairs. We set the number of retrieved knowledge subgraphs $K = 1 0$ , re-ranking top $N = 5 ,$ and candidate item pool size to 100.

4.1.4 Evaluation Metrics. For recommendation accuracy, we report:

• HR@K (Hit Rate): Proportion of test cases where the groundtruth item appears in top-K recommendations;

• NDCG@K (Normalized Discounted Cumulative Gain): Rank ing quality metric accounting for position;

• MRR (Mean Reciprocal Rank): Average reciprocal rank of the first relevant item.

For explanation quality, we report:

• Faithfulness: Entailment-based faithfulness score;

• Coherence: LLM-judged coherence (1-5 scale);

• BLEU-4: N-gram overlap with reference explanations;

• Transparency Score: Our composite metric.

## 4.2 Main Results

4.2.1 Recommendation Performance. Table 1 presents the recommendation accuracy results across all datasets. MATRAG consistently outperforms all baselines, achieving the highest scores on all metrics.

Key observations include:

(1) Multi-agent collaboration improves over single-agent approaches. MATRAG outperforms InteRecAgent by 17.1% (HR@10) on Amazon and 15.8% on MovieLens, demonstrating the value of specialized agent roles and coordinated reasoning.

(2) Knowledge graph augmentation enhances LLM-based methods. Comparing MATRAG to LLMRank (which lacks KG retrieval), we observe improvements of 19.2% (HR@10) and 25.9% (NDCG@10), validating the importance of grounding LLM reason ing in structured knowledge.

Table 1: Recommendation performance comparison. Best results in bold, second best underlined. † indicates statistically significant improvement over the best baseline (<sup>?? <</sup> 0<sup>.</sup>05).

<table><tr><td rowspan="2">Method</td><td colspan="3">Amazon Electronics</td><td colspan="3">MovieLens-1M</td></tr><tr><td>HR@10</td><td>NDCG@10</td><td>MRR</td><td>HR@10</td><td>NDCG@10</td><td>MRR</td></tr><tr><td>BPR</td><td>0.312</td><td>0.198</td><td>0.156</td><td>0.428</td><td>0.287</td><td>0.221</td></tr><tr><td>LightGCN</td><td>0.378</td><td>0.241</td><td>0.189</td><td>0.512</td><td>0.348</td><td>0.269</td></tr><tr><td>SASRec</td><td>0.401</td><td>0.259</td><td>0.204</td><td>0.534</td><td>0.367</td><td>0.285</td></tr><tr><td>KGAT</td><td>0.389</td><td>0.248</td><td>0.195</td><td>0.521</td><td>0.354</td><td>0.274</td></tr><tr><td>KGIN</td><td>0.412</td><td>0.267</td><td>0.211</td><td>0.548</td><td>0.378</td><td>0.294</td></tr><tr><td>TALLRec</td><td>0.423</td><td>0.274</td><td>0.218</td><td>0.556</td><td>0.385</td><td>0.301</td></tr><tr><td>Chat-Rec</td><td>0.418</td><td>0.271</td><td>0.215</td><td>0.549</td><td>0.379</td><td>0.296</td></tr><tr><td>LLMRank</td><td>0.437</td><td>0.285</td><td>0.228</td><td>0.571</td><td>0.398</td><td>0.314</td></tr><tr><td>InteRecAgent</td><td>0.445</td><td>0.291</td><td>0.234</td><td>0.582</td><td>0.408</td><td>0.323</td></tr><tr><td>RecMind</td><td>0.451</td><td>0.296</td><td>0.239</td><td>0.589</td><td>0.415</td><td>0.329</td></tr><tr><td>MACRec</td><td>0.462</td><td>0.305</td><td>0.247</td><td>0.601</td><td>0.427</td><td>0.341</td></tr><tr><td>K-RagRec</td><td>0.469</td><td>0.311</td><td>0.252</td><td>0.608</td><td>0.433</td><td>0.347</td></tr><tr><td>G-CRS</td><td> $\underline{0.478}$ </td><td> $\underline{0.318}$ </td><td> $\underline{0.259}$ </td><td> $\underline{0.617}$ </td><td> $\underline{0.441}$ </td><td> $\underline{0.355}$ </td></tr><tr><td>MATRAG</td><td> $0.521^{\dagger}$ </td><td> $0.359^{\dagger}$ </td><td> $0.297^{\dagger}$ </td><td> $0.674^{\dagger}$ </td><td> $0.493^{\dagger}$ </td><td> $0.408^{\dagger}$ </td></tr><tr><td>Improv.</td><td>+9.0%</td><td>+12.9%</td><td>+14.7%</td><td>+9.2%</td><td>+11.8%</td><td>+14.9%</td></tr></table>

Table 2: Recommendation performance on Yelp dataset.

<table><tr><td>Method</td><td>HR@10</td><td>NDCG@10</td><td>MRR</td></tr><tr><td>LightGCN</td><td>0.356</td><td>0.228</td><td>0.178</td></tr><tr><td>KGIN</td><td>0.394</td><td>0.251</td><td>0.198</td></tr><tr><td>LLMRank</td><td>0.418</td><td>0.271</td><td>0.216</td></tr><tr><td>MACRec</td><td>0.442</td><td>0.289</td><td>0.232</td></tr><tr><td>G-CRS</td><td> $\underline{0.461}$ </td><td> $\underline{0.304}$ </td><td> $\underline{0.247}$ </td></tr><tr><td>MATRAG</td><td> $\mathbf{0.513}^{\dagger}$ </td><td> $\mathbf{0.351}^{\dagger}$ </td><td> $\mathbf{0.289}^{\dagger}$ </td></tr></table>

Table 3: Explanation quality comparison on Amazon Elec tronics. Higher is better for all metrics.

<table><tr><td>Method</td><td>Faith.</td><td>Coher.</td><td>BLEU-4</td><td>Trans.</td></tr><tr><td>Chat-Rec</td><td>0.612</td><td>3.24</td><td>0.089</td><td>0.587</td></tr><tr><td>InteRecAgent</td><td>0.648</td><td>3.41</td><td>0.102</td><td>0.623</td></tr><tr><td>RecMind</td><td>0.671</td><td>3.52</td><td>0.118</td><td>0.651</td></tr><tr><td>MACRec</td><td>0.693</td><td>3.68</td><td>0.127</td><td>0.678</td></tr><tr><td>K-RagRec</td><td>0.724</td><td>3.79</td><td>0.141</td><td>0.712</td></tr><tr><td>G-CRS</td><td>0.751</td><td>3.91</td><td>0.156</td><td>0.738</td></tr><tr><td>MATRAG</td><td>0.847</td><td>4.42</td><td>0.198</td><td>0.856</td></tr></table>

(3) The transparency-focused design does not sacrifice accuracy. Despite its emphasis on explainability, MATRAG achieves the highest recommendation accuracy, suggesting that explicit rea soning chains and grounded explanations may also improve recommendation quality.

4.2.2 Explanation Quality. Table 3 compares explanation quality across methods that generate natural language explanations.

Table 4: Ablation study on Amazon Electronics. We remove components individually to measure their contribution.

<table><tr><td>Variant</td><td>HR@10</td><td>NDCG@10</td><td>Trans.</td></tr><tr><td>MATRAG (Full)</td><td>0.521</td><td>0.359</td><td>0.856</td></tr><tr><td>w/o User Modeling Agent</td><td>0.478</td><td>0.321</td><td>0.789</td></tr><tr><td>w/o Item Analysis Agent</td><td>0.462</td><td>0.307</td><td>0.724</td></tr><tr><td>w/o Reasoning Agent</td><td>0.441</td><td>0.289</td><td>0.698</td></tr><tr><td>w/o Explanation Agent</td><td>0.519</td><td>0.356</td><td>0.612</td></tr><tr><td>w/o KG Retrieval</td><td>0.469</td><td>0.312</td><td>0.731</td></tr><tr><td>w/o Transparency Scoring</td><td>0.512</td><td>0.351</td><td>0.768</td></tr><tr><td>Single Agent (No Collab.)</td><td>0.448</td><td>0.294</td><td>0.687</td></tr></table>

MATRAG achieves substantial improvements in explanation quality: +12.8% faithfulness over G-CRS, indicating that our reasoning chain and KG-grounded explanation generation produce more verifiable explanations. The coherence improvement (+13.0%) demonstrates that explicit agent coordination yields more logically structured explanations.

## 4.3 Ablation Studies

To understand the contribution of each component, we conduct ablation studies (Table 4).

Key findings:

(1) Each agent contributes uniquely. Removing the Reasoning Agent causes the largest accuracy drop (-15.4% HR), confirming its central role in synthesizing signals. The Item Analysis Agent removal shows the second-largest impact, highlighting the value of KG-enhanced item representations.

(2) Multi-agent collaboration is essential. The single-agent variant (where one LLM performs all tasks) underperforms the full system by 14.0% (HR), validating our design choice to specialize agents for distinct subtasks.

Table 5: Human expert evaluation results (1-5 scale). Inter rater agreement: Krippendorf’s <sup>??</sup> = 0<sup>.</sup>78.

<table><tr><td>Method</td><td>Help.</td><td>Trust.</td><td>Info.</td><td>Pers.</td><td>Avg.</td></tr><tr><td>Chat-Rec</td><td>3.12</td><td>2.98</td><td>3.34</td><td>2.87</td><td>3.08</td></tr><tr><td>MACRec</td><td>3.56</td><td>3.42</td><td>3.71</td><td>3.28</td><td>3.49</td></tr><tr><td>K-RagRec</td><td>3.78</td><td>3.67</td><td>3.92</td><td>3.51</td><td>3.72</td></tr><tr><td>G-CRS</td><td>3.91</td><td>3.82</td><td>4.08</td><td>3.67</td><td>3.87</td></tr><tr><td>MATRAG</td><td>4.38</td><td>4.31</td><td>4.52</td><td>4.24</td><td>4.36</td></tr></table>

(3) Transparency scoring improves both accuracy and ex planation quality. Interestingly, removing the transparency scor ing module slightly reduces recommendation accuracy, suggesting that the feedback loop from explanation quality assessment helps refine the reasoning process.

## 4.4 Human Expert Evaluation

We conducted a human evaluation study to assess explanation quality from the end-user perspective.

4.4.1 Study Design. We recruited 12 domain experts: 4 e-commerce product managers, 4 recommendation system researchers, and 4 UX designers with experience in content personalization. Each expert evaluated 50 recommendation-explanation pairs sampled from test sets across all three datasets (600 total evaluations per method).

Experts rated each explanation on four dimensions using a 5- point Likert scale:

• Helpfulness: Does the explanation help understand why this item was recommended?

• Trustworthiness: Does the explanation seem honest and reliable?

• Informativeness: Does the explanation provide useful in formation about the item?

• Personalization: Does the explanation feel tailored to the user’s preferences?

## 4.4.2 Results. Table 5 presents the human evaluation results.

MATRAG significantly outperforms all baselines on every di mension (<sup>??</sup> <sup><</sup> 0<sup>.</sup>01 via Wilcoxon signed-rank test). Notably, 87.4% of MATRAG explanations received ratings ≥ 4 on both Helpfulness and Trustworthiness, compared to 62.1% for the next-best method (G-CRS).

Expert feedback highlighted several qualitative strengths of MA TRAG explanations:

“The explanations consistently reference specific product features that match my inferred preferences—it’s not just generic praise.”

“I appreciate how the system explains not just what it recommends, but why other seemingly similar items were not chosen.”

“The knowledge graph grounding is evident—explanations cite concrete facts like ‘directed by Christopher Nolan’ rather than vague statements.”

Table 6: Eficiency comparison. Latency is per-request.

<table><tr><td>Method</td><td>Latency (s)</td><td>LLM Calls</td><td>KG Queries</td></tr><tr><td>LLMRank</td><td>1.2</td><td>1</td><td>0</td></tr><tr><td>InteRecAgent</td><td>2.8</td><td>3</td><td>0</td></tr><tr><td>MACRec</td><td>4.1</td><td>5</td><td>0</td></tr><tr><td>K-RagRec</td><td>2.4</td><td>2</td><td>3</td></tr><tr><td>G-CRS</td><td>3.2</td><td>3</td><td>4</td></tr><tr><td>MATRAG</td><td>5.3</td><td>6</td><td>5</td></tr></table>

## 4.5 Eficiency Analysis

We analyze the computational eficiency of MATRAG compared to baselines (Table 6).

MATRAG incurs higher latency due to multi-agent coordination and comprehensive KG retrieval. However, we note that: (1) the latency is acceptable for non-real-time use cases; (2) the Explanation Agent can run asynchronously after initial recommendations; and (3) agent calls can be parallelized, reducing wall-clock time to ∼3.1 seconds.

## 5 Discussion

## 5.1 Implications for Practice

Our findings have several implications for deploying LLM-based recommenders in production:

Multi-agent architectures enable specialization without sacrificing integration. Rather than prompting a single LLM with complex, multi-faceted instructions, decomposing the recommendation task across specialized agents yields both better accuracy and more coherent explanations.

Knowledge graphs are essential for grounded explanations. LLM-generated explanations without factual grounding risk hallucination and user distrust. By retrieving from curated knowledge graphs, MATRAG ensures that explanations reference verifiable facts.

Transparency scoring provides a flywheel for quality improvement. The transparency scoring module not only enables evaluation but also provides signals for iterative refinement through RLHF or prompt optimization.

## 5.2 Limitations and Future Work

Despite promising results, MATRAG has limitations that suggest directions for future research:

Latency. Multi-agent coordination introduces overhead unsuitable for real-time applications. Future work could explore agent caching, speculative execution, or distillation to smaller models.

Knowledge graph coverage. MATRAG’s performance depends on knowledge graph completeness. For domains with sparse KGs, techniques for automatic KG construction or completion would be valuable.

Multi-turn interaction. Our current evaluation focuses on single-turn recommendations. Extending MATRAG to conversational settings with memory-augmented agents is an important direction.

Cross-domain generalization. While MATRAG performs well within domains, zero-shot transfer to new domains remains chal lenging. Pre-training strategies for domain-agnostic agent capabili ties warrant investigation.

## 6 Conclusion

We introduced MATRAG, a multi-agent framework that unifies knowledge graph-augmented retrieval with transparent, explainable recommendation generation. By orchestrating specialized agents for user modeling, item analysis, reasoning, and explanation, MA TRAG achieves state-of-the-art performance on three benchmark datasets while generating explanations that 87.4% of human experts rated as helpful and trustworthy. Our transparency scoring mechanism provides quantitative assessment of explanation qual ity, enabling both automated evaluation and human-in-the-loop refinement.

As recommendation systems increasingly adopt agentic architec tures, the principles embodied in MATRAG—agent specialization, knowledge grounding, explicit reasoning chains, and transparency measurement—ofer a roadmap for building systems that users can understand and trust. We release our code and evaluation data to facilitate further research in transparent, agentic recommendation.

## References

[1] Keqin Bao, Jizhi Zhang, Yang Zhang, Wenjie Wang, Fuli Feng, and Xiangnan He. 2023. TALLRec: An Efective and Eficient Tuning Framework to Align Large Lan guage Model with Recommendation. In Proceedings of the 17th ACM Conference on Recommender Systems (RecSys ’23). 1007–1014.

[2] Chong Chen, Min Zhang, Yiqun Liu, and Shaoping Ma. 2019. Co-Attentive Multi Task Learning for Explainable Recommendation. In Proceedings of the 28th International Joint Conference on Artificial Intelligence (IJCAI ’19). 2137–2143.

[3] Darren Edge, Ha Trinh, Newman Cheng, Joshua Bradley, Alex Chao, Apurva Mody, Steven Truitt, and Jonathan Larson. 2024. From Local to Global: A Graph RAG Approach to Query-Focused Summarization. arXiv preprint arXiv:2404.16130.

[4] Yuhang Fang, Yufei Zhou, Qing Li, and Peng Zhang. 2024. Multi-Agent Conversational Recommender Systems with Coordinated Interaction. In Proceedings of the ACM Web Conference 2024 (WWW ’24). 2145–2156.

[5] Yunfan Gao, Tao Sheng, Youlin Xiang, Yun Xiong, Haofen Wang, and Jiawe Zhang. 2023. Chat-Rec: Towards Interactive and Explainable LLMs-Augmented Recommender System. arXiv preprint arXiv:2303.14524.

[6] Yingqiang Ge, Shuchang Liu, Zuohui Fu, Juntao Tan, Zelong Li, Shuyuan Xu, Yunqi Li, Yikun Xian, and Yongfeng Zhang. 2024. A Survey on Trustworthy Recommender Systems. ACM Transactions on Recommender Systems 3 (2024), 1–68.

[7] Sixun Guo, Shijie Zhang, Weiwei Sun, Pengjie Ren, Zhumin Chen, and Zhaochun Ren. 2023. Towards Explainable Conversational Recommender Systems. In Proceedings of the 46th International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR ’23). 2786–2790.

[8] F. Maxwell Harper and Joseph A. Konstan. 2015. The MovieLens Datasets: History and Context. ACM Transactions on Interactive Intelligent Systems 5, 4 (2015), 1–19.

[9] Xiangnan He, Kuan Deng, Xiang Wang, Yan Li, Yongdong Zhang, and Meng Wang. 2020. LightGCN: Simplifying and Powering Graph Convolution Network for Recommendation. In Proceedings of the 43rd International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR ’20). 639–648.

[10] Sirui Hong, Mingchen Zhuge, Jonathan Chen, Xiawu Zheng, Yuheng Cheng, Ceyao Zhang, Jinlin Wang, Zili Wang, Steven Ka Shing Yau, Zijuan Lin, et al. 2024. MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework. In Proceedings of the Twelfth International Conference on Learning Representations (ICLR ’24).

[11] Yupeng Hou, Junjie Zhang, Zihan Lin, Hongyu Lu, Ruobing Xie, Julian McAuley, and Wayne Xin Zhao. 2024. Large Language Models are Zero-Shot Rankers for Recommender Systems. In Proceedings of the 46th European Conference on Information Retrieval (ECIR ’24). 364–381.

[12] Xu Huang, Jianxun Lian, Yuxuan Lei, Jing Yao, Defu Lian, and Xing Xie. 2023. Recommender AI Agent: Integrating Large Language Models for Interactive Recommendations. arXiv preprint arXiv:2308.16505.

[13] Wang-Cheng Kang and Julian McAuley. 2018. Self-Attentive Sequential Recommendation. In Proceedings of the 2018 IEEE International Conference on Data Mining (ICDM ’18). 197–206.

[14] Patrick Lewis, Ethan Perez, Aleksandra Piktus, Fabio Petroni, Vladimir Karpukhin, Naman Goyal, Heinrich Küttler, Mike Lewis, Wen-tau Yih, Tim Rocktäschel, et al. 2020. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. In Advances in Neural Information Processing Systems (NeurIPS ’20). 9459–9474.

[15] Lei Li, Yongfeng Zhang, Dugang Liu, and Li Chen. 2024. Large Language Models for Generative Recommendation: A Survey and Visionary Discussions. In Proceedings of the 2024 Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING ’24). 10146–10159.

[16] Guohao Li, Hasan Abed Al Kader Hammoud, Hani Itani, Dmitrii Khizbullin, and Bernard Ghanem. 2024. CAMEL: Communicative Agents for “Mind” Exploration of Large Language Model Society. In Advances in Neural Information Processing Systems (NeurIPS ’24).

[17] Jianghao Lin, Xinyi Dai, Yunjia Xi, Weiwen Liu, Bo Chen, Hao Zhang, Yong Liu, Chuhan Wu, Xiangyang Li, Chenxu Zhu, Huifeng Guo, Yong Yu, Ruiming Tang, and Weinan Zhang. 2024. How Can Recommender Systems Benefit from Large Language Models: A Survey. ACM Transactions on Information Systems (2024).

[18] Qidong Liu, Xiangyu Zhao, Yuhao Wang, Yejing Wang, Zijian Zhang, Yuqi Sun, Xiang Li, Maolin Wang, Pengyue Jia, Chong Chen, Wei Huang, and Feng Tian. 2024. Large Language Model Enhanced Recommender Systems: A Survey. arXiv preprint arXiv:2412.13432.

[19] Petr Lubos, Ladislav Peska, and Patrik Slavík. 2024. User Evaluation of LLM-Generated Explanations for Recommender Systems. In Proceedings of the 29th International Conference on Intelligent User Interfaces (IUI ’24). 597–608.

[20] Jianmo Ni, Jiacheng Li, and Julian McAuley. 2019. Justifying Recommendations using Distantly-Labeled Reviews and Fine-Grained Aspects. In Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP ’19). 188–197.

[21] OpenAI. 2023. GPT-4 Technical Report. arXiv preprint arXiv:2303.08774.

[22] Zhangchi Qiu, Zehui Wang, Jianan Wang, and Alan Wee-Chung Liew. 2025. Graph Retrieval-Augmented LLM for Conversational Recommendation Systems. arXiv preprint arXiv:2503.06430.

[23] Nils Reimers and Iryna Gurevych. 2019. Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. In Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP ’19). 3982–3992.

[24] Stefen Rendle, Christoph Freudenthaler, Zeno Gantner, and Lars Schmidt-Thieme. 2009. BPR: Bayesian Personalized Ranking from Implicit Feedback. In Proceedings of the Twenty-Fifth Conference on Uncertainty in Artificial Intelligence (UAI ’09). 452–461.

[25] Alan Said. 2024. On Explaining Recommendations with Large Language Models: A Review. Frontiers in Big Data 7 (2024), 1505284.

[26] Yutong Shu, Peng Zhang, Yifan Li, and Chuang Zhang. 2024. Knowledge Graph-Enhanced LLM for Multi-hop Link Prediction. arXiv preprint arXiv:2402.12345.

[27] Itallo Silva, Leandro Marinho, Alan Said, and Martijn Willemsen. 2024. Leveraging ChatGPT for Automated Human-Centered Explanations in Recommender Systems. In Proceedings of the 29th International Conference on Intelligent User Interfaces (IUI ’24). 597–608.

[28] Hugo Touvron, Louis Martin, Kevin Stone, Peter Albert, Amjad Almahairi, Yas mine Babaei, Nikolay Bashlykov, Soumya Batra, Prajjwal Bhargava, Shruti Bhosale, et al. 2023. Llama 2: Open Foundation and Fine-Tuned Chat Models. arXiv preprint arXiv:2307.09288.

[29] Aaron Grattafiori, Abhimanyu Dubey, Abhinav Jauhri, Abhinav Pandey, Abhishek Kadian, Ahmad Al-Dahle, Aiesha Letman, Akhil Mathur, Alan Schelten, Alex Vaughan, et al. 2024. The Llama 3 Herd of Models. arXiv preprint arXiv:2407.21783.

[30] Xiang Wang, Xiangnan He, Yixin Cao, Meng Liu, and Tat-Seng Chua. 2019. KGAT: Knowledge Graph Attention Network for Recommendation. In Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining (KDD ’19). 950–958.

[31] Xiang Wang, Tinglin Huang, Dingxian Wang, Yancheng Yuan, Zhenguang Liu, Xiangnan He, and Tat-Seng Chua. 2021. Learning Intents behind Interactions with Knowledge Graph for Recommendation. In Proceedings of the Web Conference 2021 (WWW ’21). 878–887.

[32] Yancheng Wang, Ziyan Jiang, Zheng Chen, Fan Yang, Yingxue Zhou, Eunah Cho, Xing Fan, Xiaojiang Huang, Yanbin Lu, and Yingzhen Yang. 2023. RecMind: Large Language Model Powered Agent for Recommendation. arXiv preprint arXiv:2308.14296.

[33] Zhefan Wang, Yuanqing Yu, Wendi Yu, Weizhi Ma, and Min Zhang. 2024. MACRec: A Multi-Agent Collaboration Framework for Recommendation. arXiv preprint arXiv:2402.15235.

[34] Shijie Wang, Hangyu Guo, Zhibo Cai, Yongwei Zhao, Yubin Bao, and Ge Yu. 2025. Knowledge Graph Retrieval-Augmented Generation for LLM-based Recommendation. In Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (ACL ’25).

[35] Qingyun Wu, Gagan Bansal, Jieyu Zhang, Yiran Wu, Beibin Li, Erkang Zhu, Li Jiang, Xiaoyun Zhang, Shaokun Zhang, Jiale Liu, et al. 2023. AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation. arXiv preprint

arXiv:2308.08155.

[36] Likang Wu, Zhi Zheng, Zhaopeng Qiu, Hao Wang, Hongchao Gu, Tingjia Shen, Chuan Qin, Chen Zhu, Hengshu Zhu, Qi Liu, Hui Xiong, and Enhong Chen. 2023. A Survey on Large Language Models for Recommendation. arXiv preprint arXiv:2305.19860.

[37] Xie Liu, Chen Zhang, Xiangnan He, and Fuli Feng. 2024. Enabling Explainable Recommendation in E-commerce with LLM-powered Product Knowledge Graph. In IJCAI Workshop on Knowledge Graphs and LLMs.

[38] Shunyu Yao, Jefrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, and Yuan Cao. 2023. ReAct: Synergizing Reasoning and Acting in Language Models. In Proceedings of the Eleventh International Conference on Learning Representations (ICLR ’23).

[39] Yelp. 2023. Yelp Open Dataset. https://www.yelp.com/dataset.

[40] Yongfeng Zhang, Xu Chen, Qingyao Ai, Liu Yang, and W. Bruce Croft. 2020. Towards Conversational Recommendation over Multi-Type Dialogs. In Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (ACL ’20). 1036–1049.

[41] An Zhang, Yuxin Chen, Leheng Sheng, Xiang Wang, and Tat-Seng Chua. 2024. On Generative Agents in Recommendation. In Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR ’24). 1807–1817.

[42] Junjie Zhang, Yupeng Hou, Ruobing Xie, Wenqi Sun, Julian McAuley, Wayne Xin Zhao, Leyu Lin, and Ji-Rong Wen. 2024. AgentCF: Collaborative Learning with Autonomous Language Agents for Recommender Systems. In Proceedings of the ACM Web Conference 2024 (WWW ’24). 3876–3887.

[43] Xi Zhu, Yu Wang, Hang Gao, Wujiang Xu, Chen Wang, Zhiwei Liu, Kun Wang, Mingyu Jin, Linsey Pang, Qingsong Wen, Philip Yu, and Yongfeng Zhang. 2024. Recommender Systems Meet Large Language Model Agents: A Survey. arXiv preprint arXiv:2411.00114.

[44] Xiangrong Zhu, Yuexiang Xie, Yi Liu, Yaliang Li, and Wei Hu. 2025. Knowledge Graph-Guided Retrieval Augmented Generation. arXiv preprint arXiv:2502.06864.

## A Prompt Templates

We provide the key prompt templates used by MATRAG agents.

3. Is honest about recommendation rationale

4. Uses natural, accessible language

## A.1 User Modeling Agent Prompt

## B Additional Experimental Results

## C Reproducibility

Table 7 shows MATRAG’s performance across users with diferent activity levels.

You are a User Modeling Agent. Analyze the user's interaction history and extract structured preference signals.

## B.1 Performance by User Activity Level

User History:

{interaction\_history}

Table 7: HR@10 by user activity level on Amazon Electronics.

<table><tr><td>Method</td><td>Low</td><td>Medium</td><td>High</td></tr><tr><td>LLMRank</td><td>0.298</td><td>0.451</td><td>0.562</td></tr><tr><td>MACRec</td><td>0.341</td><td>0.478</td><td>0.589</td></tr><tr><td>MATRAG</td><td>0.412</td><td>0.534</td><td>0.628</td></tr></table>

Extract:

1. Explicit preferences (stated likes/dislikes)

2. Implicit preferences (inferred from behavior)

We will release code, data splits, and model checkpoints upon publication to ensure reproducibility.

MATRAG shows the largest improvements for low-activity users (+38.3% over LLMRank), demonstrating that knowledge graph augmentation efectively addresses cold-start challenges.

Recommended Item: {item} User Profile: {user\_profile} Reasoning Chain: {reasoning\_chain} Retrieved Knowledge: {kg\_subgraph}

3. Contextual factors (time, device, session)

Generate an explanation that:

4. Preference evolution (temporal patterns)

1. Cites specific evidence from knowledge

Output as structured JSON.

2. Connects to user preferences explicitly

You are an Explanation Agent. Generate a transparent, grounded explanation for the recommendation.

## A.2 Explanation Agent Prompt


---

# 2607.07108_多模态记忆增强的推荐智能体协作

[2607.07108](https://arxiv.org/abs/2607.07108)

# Seeing and Reflecting: Multimodal Memory-Enhanced Agent Collaboration for Recommendation

Hao Cong<sup>1,\*</sup>, Huizu Lin<sup>2,\*</sup>, Zihan Wang<sup>3,\*</sup>, Chengkai Huang<sup>4,5,#</sup>, Quan Z. Sheng<sup>5</sup>, Lina Yao<sup>4,6</sup>

<sup>1</sup>Tsinghua University, <sup>2</sup>University of Science and Technology of China, <sup>3</sup>Peking University, <sup>4</sup>The University of New South Wales, <sup>5</sup>Macquarie University, <sup>6</sup>CSIRO’s Data61

<sup>\*</sup>Equal contribution. <sup>#</sup>Corresponding author. Correspondence: chengkai.huang1@unsw.edu.au

## Abstract

Large language model (LLM)-based agentic recommender systems show promise in modeling user preferences through natural-language reasoning, yet they remain limited by textcentric inputs and coarse-grained memory updates, making agents prone to missing visual evidence, semantic noise, and preference drift. To address these limitations, we propose MMEACR, a Multimodal Memory-Enhanced Agent Collaboration framework for recommendation. MMEACR introduces a dual-track memory architecture that separates interpretable agent reasoning from fine grained multimodal matching. In the reasoning track, collaborative User and Item Memory Agents maintain persistent multimodal memories and update them through an attributeguided reinforcement-and-reflection mechanism. In the matching track, a decoupled multimodal embedding memory is built from raw interaction narratives and item images to preserve detailed cross-modal signals beyond structured memory updates. The two tracks are integrated through weighted Reciprocal Rank Fusion to produce robust and interpretable rankings. Experiments on three real-world domains show that MMEACR achieves strong overall performance against competitive LLM-based and agent-based baselines, with notable gains in visually grounded recommendation scenarios.

## 1 Introduction

Large language models (LLMs) have recently enabled a new class of agentic recommender systems that model user preferences through naturallanguage reasoning and interaction (Huang et al., 2025b, 2024a, 2025a). Representative methods such as AgentCF (Zhang et al., 2024) formulate recommendation as a collaborative process among language agents, where agents compare candidate items, generate rationales, and update their internal memories. This paradigm improves interpretability and flexibility by externalizing preference modeling into language-mediated reasoning rather than relying solely on gradient-based representation learning.

![](images/98edc660de228c64ca9f1fa89d330eb2d5da132f1ae5e3f3e3c4828baaf36ad2.jpg)  
Figure 1: Comparison between conventional textcentric agent-based recommendation and MMEACR. MMEACR combines multimodal agent memory evolution with embedding-based cross-modal matching and fuses their rankings via Reciprocal Rank Fusion (RRF).

Despite their promise, existing LLM-based recommendation agents still suffer from two key limitations. First, most methods remain text-centric, constructing user and item memories mainly from textual histories, reviews, or metadata while underusing visual evidence such as product images (Liu et al., 2025). This restricts their ability to model preferences in visually grounded domains such as fashion, electronics, and media products, where appearance, style, packaging, and other visual attributes often play an important role. Second, current memory update mechanisms are often coarsegrained. Agents typically revise their profiles through free-form reflection or direct history accumulation, which can introduce redundant descriptions, amplify spurious rationales, and cause preference drift over repeated interactions. These issues become more challenging when textual and visual signals must be jointly interpreted and selectively consolidated.

To address these challenges, we propose MMEACR, a Multimodal Memory-Enhanced Agent Collaboration framework for recommendation. MMEACR is motivated by the idea of Seeing and Reflecting. Seeing grounds agents in multimodal evidence by initializing and enriching item memories with both textual metadata and imagederived descriptions. Reflecting enables structured memory evolution by reinforcing aligned preference signals and correcting misleading ones after user–item interactions.

MMEACR contains two complementary tracks. The reasoning track uses cooperative User and Item Memory Agents to maintain persistent language memories. During interaction, an LLM-based agent compares candidate items, generates a rationale, and updates memories according to whether the predicted preference matches the observed feedback. To reduce noisy updates, MMEACR extracts preference-relevant attributes from a predefined semantic attribute space and uses them to guide both reinforcement and reflection. This helps preserve stable user interests while revising inaccurate or drifting memory descriptions.

The matching track complements languagebased reasoning with dense multimodal representations. Since structured memory updates may filter out fine-grained details, MMEACR also maintains raw interaction narratives and item images for embedding-based matching. A multimodal embedding module encodes these signals into dense representations, capturing cross-modal semantics that may be difficult to express in concise textual memories. Finally, MMEACR combines the reasoning-based and embedding-based rankings through weighted Reciprocal Rank Fusion, allowing the final recommendation to benefit from both interpretable agent reasoning and fine-grained multimodal similarity.

Our contributions are summarized as follows:

• We propose MMEACR, a multimodal memory-enhanced agent collaboration framework that grounds LLM-based recommendation agents in both textual and visual evidence.

• We design an attribute-guided memory evolution mechanism that enables User and Item Memory Agents to reinforce aligned preferences and reflect on misaligned ones, reducing semantic noise and preference drift.

• We introduce a dual-track recommendation pipeline that combines interpretable languageagent reasoning with multimodal embeddingbased matching through Reciprocal Rank Fusion, achieving strong performance across multiple domains.

## 2 Related Work

## 2.1 LLM-based Recommendation

Large language models (LLMs) have recently been explored for recommendation due to their strong abilities in semantic understanding, instruction following, and natural-language reasoning (Hou et al., 2024a; Zhao et al., 2024; Gao et al., 2026). Early LLM-based recommenders mainly use frozen LLMs as zero-shot or few-shot rankers, where user histories and candidate items are converted into textual prompts for preference prediction (Hou et al., 2024a). Other studies further improve task adaptation through Chain-of-Thought reasoning, instruction tuning, or retrieval-augmented generation, enabling LLMs to better align textual semantics with collaborative signals (Wei et al., 2022; Bao et al., 2023; Shi et al., 2025). More recently, agentic recommender systems have represented users and items as autonomous language agents that interact, exchange feedback, and update their memories during recommendation (Zhang et al., 2024; Liu et al., 2025). These methods improve interpretability by making preference modeling explicit in language-based reasoning processes. Meanwhile, multimodal LLMs and multimodal embedding models have shown the potential to incorporate visual and textual signals for richer item understanding (Lyu et al., 2023; Zhang et al., 2025a). However, most existing agentic recommenders still rely primarily on textual memories or directly inject multimodal information into prompts, which may lead to verbose contexts, redundant semantics, and unstable reasoning. In contrast, MMEACR adopts a dual-track design that separates structured agentic reasoning from dense multimodal match ing, allowing the framework to use visual evidence without overloading the language-agent memory.

## 2.2 Memory in LLM Agents

Memory is essential for LLM agents to maintain consistency, accumulate experience, and support reflection across interactions (Ferrag et al., 2025; Zhang et al., 2025b; Ye et al., 2026). Existing agent memory mechanisms range from short-term context buffers to long-term episodic stores, retrievalbased memories, and reflection-based memory management (Tang et al., 2026; Jiao et al., 2026a,b). Although these mechanisms have been widely studied in general-purpose agent systems, applying them to recommendations remains challenging. User preferences are often dynamic, sparse, and attribute-dependent, while item descriptions may contain noisy or redundant information. Simply appending interaction histories or retrieving past episodes can therefore introduce irrelevant details, amplify spurious preference signals, and cause pref erence drift over time (Salve et al., 2024; Li et al., 2025). Recent memory-enhanced recommender agents attempt to update user and item profiles through interaction feedback, but their updates are often coarse-grained and lack explicit constraints on which semantic attributes should be reinforced or corrected. MMEACR addresses this limitation with an attribute-guided memory evolution mechanism, where preference-relevant attributes are extracted from user-item comparisons and used to guide reinforcement and reflection. This design enables agents to consolidate stable preference signals while reducing semantic noise in long-term multimodal memory.

## 3 Problem Formulation

Let U and I denote the sets of users and items, respectively. For each user $u \in \mathcal { U }$ , we assume a chronologically ordered interaction history that reflects the user’s past preferences. Given a candidate item set ${ \mathcal { C } } = \{ c _ { 1 } , \ldots , c _ { n } \} \subseteq { \mathbb { Z } }$ , the goal is to generate a personalized ranking of these candidates according to the user’s preference. Formally, we define the recommendation function as:

$$
\hat {\mathcal {C}} = f _ {\mathrm{LLM}} (u, \mathcal {C}),\tag{1}
$$

where $\hat { \mathcal { C } }$ denotes the ranked candidate list produced by the LLM-based recommendation framework.

Memory in Agents. Following the agent-based recommendation paradigm (Zhang et al., 2024), we model the collaborative recommendation process with two types of LLM-powered memory agents: a User Memory Agent (UA) and an Item Memory Agent (IA). Rather than relying on static textual profiles or fixed representation embeddings, MMEACR treats memories as persistent semantic states that can be updated through interactions. Specifically, the user memory $M _ { u }$ is an evolving textual narrative that summarizes the user’s longterm preferences, behavioral patterns, and finegrained attribute tendencies. The item memory $M _ { i }$ describes item i by integrating its textual metadata with visual descriptions derived from product images. During recommendation and memory evolution, the User and Item Memory Agents collaborate through LLM-based reasoning over $\{ M _ { u } \} \cup \{ M _ { i } \}$ , enabling the framework to capture preference-relevant semantic signals and support reasoning-aware user–item interactions.

## 4 Methodology

We present MMEACR, a multimodal memoryenhanced agent collaboration framework for recommendation. As shown in Figure 2, MMEACR contains two complementary tracks: (1) a reasoning track, where User and Item Memory Agents maintain and update interpretable multimodal memories through LLM-based interaction; and (2) a matching track, where raw interaction narratives and item images are encoded into dense multimodal embeddings. The two tracks are finally combined through weighted Reciprocal Rank Fusion (RRF) to produce the final recommendation ranking.

## 4.1 Multimodal Agent Memory

## 4.1.1 Memory Initialization

MMEACR first initializes semantic memories for users and items. For each item $i \in \mathcal { Z }$ , let $T _ { i }$ denote its textual title and $\mathcal { V } _ { i } = \{ v _ { i , 1 } , . . . , v _ { i , N _ { i } } \}$ denote its associated images, where $N _ { i } \leq 5$ . To convert visual evidence into language-readable semantics, we use a multimodal LLM to generate an imagegrounded description:

$$
D _ {i} = \operatorname{MLLM} (T _ {i}, \mathcal {V} _ {i}).\tag{2}
$$

The initial item memory is then constructed by integrating the title and visual description:

$$
M _ {i} ^ {(0)} = \mathrm{LLM} (T _ {i}, D _ {i}).\tag{3}
$$

Here, $M _ { i } ^ { ( 0 ) }$ serves as a multimodal textual memory that summarizes the item’s key attributes. For each user u, we initialize the user memory $M _ { u } ^ { ( 0 ) }$ with a domain-specific template, such as a general preference statement for music, electronics, or fashion products. In addition to structured memories, we maintain raw narratives $H _ { u }$ and $H _ { i }$ for users and items, which preserve unfiltered interaction histories and multimodal descriptions for embedding-based matching.

![](images/e02c05bb31ecbd466fc7f94c9a49f7785e8ae293062b7743720b68da8ba8c48d.jpg)  
Figure 2: Overview of MMEACR. The reasoning track performs attribute-guided memory evolution with User and Item Memory Agents, while the matching track preserves fine-grained cross-modal signals through multimodal embedding memory. The final ranking is produced by fusing both tracks via RRF.

## 4.1.2 Attribute-Guided Memory Evolution

The reasoning track updates agent memories through contrastive user-item interactions. At each interaction step t, we construct a triplet $( u , i ^ { + } , i ^ { - } )$ where $i ^ { + }$ is the ground-truth preferred item and i<sup>−</sup> is a sampled negative item. Given the current user memory $M _ { u } ^ { ( t ) }$ and item memories $M _ { i ^ { + } } ^ { ( t ) }$ and $M _ { i ^ { - } } ^ { ( t ) }$ , the LLM-based interaction agent selects the item that better matches the user’s preference and generates a rationale:

$$
a ^ {(t)}, r ^ {(t)} = f _ {\mathrm{dec}} \left(M _ {u} ^ {(t)}, M _ {i ^ {+}} ^ {(t)}, M _ {i ^ {-}} ^ {(t)}\right),\tag{4}
$$

where $a ^ { ( t ) } \in \{ i ^ { + } , i ^ { - } \}$ is the selected item and $r ^ { ( t ) }$ is the natural-language rationale. The correctness of the selection is determined by:

$$
y ^ {(t)} = \mathbb {I} \left[ a ^ {(t)} = i ^ {+} \right].\tag{5}
$$

To avoid updating memories with noisy freeform rationales, MMEACR introduces an attributeguided preference extraction step. Let $\begin{array} { r l } { \boldsymbol { A } } & { { } = } \end{array}$ $\{ a _ { 1 } , \ldots , a _ { K } \}$ be a predefined semantic attribute space, where each attribute corresponds to a highlevel preference factor such as style, functionality, portability, or visual appearance. Conditioned on the current memory, the contrastive item pair, and the generated rationale, the attribute extractor produces a structured preference signal:

$$
\mathbf {z} ^ {(t)} = f _ {\text { attr }} \left(M _ {u} ^ {(t)}, T _ {i ^ {+}}, T _ {i ^ {-}}, r ^ {(t)}, \mathcal {A}\right),\tag{6}
$$

where $\mathbf { z } ^ { ( t ) } \in \mathbb { R } ^ { K }$ encodes the attributes that explain the preference difference between $i ^ { + }$ and i<sup>−</sup>.

The extracted attribute signal is then used to guide memory evolution. If the LLM selection is correct, MMEACR reinforces the current preference pattern; otherwise, it performs reflection to correct the misaligned memory:

$$
\begin{array}{c} \mathbf {x} _ {u} ^ {(t)} = \left(M _ {u} ^ {(t)}, M _ {i ^ {+}} ^ {(t)}, M _ {i ^ {-}} ^ {(t)}, \mathbf {z} ^ {(t)}, r ^ {(t)}\right), \\ M _ {u} ^ {(t + 1)} = \left\{ \begin{array}{l l} f _ {\text {rein}} \left(\mathbf {x} _ {u} ^ {(t)}\right), & y ^ {(t)} = 1, \\ f _ {\text {refl}} \left(\mathbf {x} _ {u} ^ {(t)}\right), & y ^ {(t)} = 0. \end{array} \right. \end{array}\tag{7}
$$

This design allows the User Memory Agent to consolidate stable interests while revising inaccurate or drifting preference descriptions.

The Item Memory Agents are updated asynchronously for the interacted positive and negative items:

$$
M _ {i ^ {+}} ^ {(t + 1)} = f _ {\mathrm{pos}} \left(M _ {i ^ {+}} ^ {(t)}, M _ {u} ^ {(t)}, \mathbf {z} ^ {(t)}, y ^ {(t)}\right),\tag{8}
$$

$$
M _ {i ^ {-}} ^ {(t + 1)} = f _ {\mathrm{neg}} \left(M _ {i ^ {-}} ^ {(t)}, M _ {u} ^ {(t)}, \mathbf {z} ^ {(t)}, y ^ {(t)}\right).\tag{9}
$$

Meanwhile, the raw user narrative is updated by appending the preferred item’s metadata and visual description:

$$
H _ {u} ^ {(t + 1)} = H _ {u} ^ {(t)} \oplus [ T _ {i ^ {+}}; D _ {i ^ {+}} ],\tag{10}
$$

where ⊕ denotes chronological concatenation. Similarly, raw item narratives are maintained for the interacted items. These raw narratives are not filtered by the attribute space, ensuring that fine-grained cross-modal information remains available for the embedding-based matching track.

## 4.1.3 Reasoning-Based Ranking

After iterative memory evolution, the reasoning track ranks candidate items using the evolved user and item memories. Given a candidate set ${ \mathcal { C } } ,$ the LLM-based ranker compares the user memory $M _ { u }$ with the candidate item memories $\{ M _ { c } \mid c \in \mathcal { C } \}$ and produces a description-based ranking:

$$
\pi_ {\mathrm{des}} = \operatorname{Rank} _ {\mathrm{LLM}} \left(M _ {u}, \left\{M _ {c} \mid c \in \mathcal {C} \right\}\right).\tag{11}
$$

This ranking is interpretable because it is derived from explicit user and item memory descriptions.

## 4.2 Multimodal Embedding Memory

While the reasoning track provides interpretable preference reasoning, structured memory updates may filter out fine-grained visual or textual details. Therefore, MMEACR introduces a multimodal embedding memory to preserve raw cross-modal signals for dense matching.

## 4.2.1 Item Embedding Memory

For each item i, we use a pretrained multimodal embedding model MEM (Zhang et al., 2025a) to encode its title and images. The item embedding is computed by averaging image-title representations:

$$
\mathbf {e} _ {i} = \frac {1}{N _ {i}} \sum_ {j = 1} ^ {N _ {i}} \operatorname{MEM} \left(T _ {i}, v _ {i, j}\right).\tag{12}
$$

This embedding captures both textual and visual item semantics.

## 4.2.2 User Embedding Memory

For each user u, we construct the user embedding from the raw interaction narrative and the images of historically preferred items. Let $\mathcal { P } _ { u }$ denote the set of items preferred by user u in the interaction history. The user embedding is computed as:

$$
\mathbf {e} _ {u} = \frac {1}{| \mathcal {P} _ {u} |} \sum_ {i \in \mathcal {P} _ {u}} \mathrm{MEM} (H _ {u}, \bar {v} _ {i}),\tag{13}
$$

where $\bar { v } _ { i }$ denotes the representative visual content of item i. Unlike the attribute-guided memory $M _ { u }$ the raw narrative $H _ { u }$ preserves complete historical descriptions, allowing the embedding track to capture detailed semantic and visual preference signals.

## 4.2.3 Embedding-Based Ranking

The embedding track ranks candidate items by cosine similarity:

$$
s _ {\mathrm{emb}} (u, i) = \frac {\mathbf {e} _ {u} ^ {\top} \mathbf {e} _ {i}}{\| \mathbf {e} _ {u} \| \| \mathbf {e} _ {i} \|}.\tag{14}
$$

Sorting candidates by $s _ { \mathrm { e m b } } ( u , i )$ yields the embedding-based ranking π<sub>emb</sub>.

## 4.3 Hybrid Ranking via Reciprocal Rank Fusion

The reasoning and matching tracks capture complementary signals. The reasoning track provides interpretable preference judgments based on evolved agent memories, while the embedding track captures fine-grained cross-modal similarity from raw narratives and images. To combine them, MMEACR adopts a weighted Reciprocal Rank Fusion strategy.

For each candidate item i, we first compute its rank-based scores from the two tracks:

$$
S _ {\mathrm{des}} (i) = \frac {1}{k _ {\mathrm{des}} + \mathrm{rank} _ {\pi_ {\mathrm{des}}} (i)},\tag{15}
$$

$$
S _ {\mathrm{emb}} (i) = \frac {1}{k _ {\mathrm{emb}} + \mathrm{rank} _ {\pi_ {\mathrm{emb}}} (i)},\tag{16}
$$

where ran $\mathfrak { c } _ { \pi _ { \mathrm { d e s } } } ( i )$ and ran $\mathrm { k } _ { \pi _ { \mathrm { e m b } } } ( i )$ denote the positions of item i in the reasoning-based and embedding-based rankings, respectively. The constants $k _ { \mathrm { d e s } }$ and $k _ { \mathrm { e m b } }$ control the smoothness of rank contributions.

The final fusion score is:

$$
S _ {\mathrm{RRF}} (i) = w _ {\mathrm{des}} S _ {\mathrm{des}} (i) + w _ {\mathrm{emb}} S _ {\mathrm{emb}} (i),\tag{17}
$$

where $w _ { \mathrm { d e s } }$ and $w _ { \mathrm { e m b } }$ balance the contributions of the two tracks. The final recommendation list is obtained by sorting all candidate items in descending order of S (i).

## 5 Experiments

Datasets. Following previous work (Zhang et al., 2024; Huang et al., 2023b,a, 2024b), we conduct experiments on three text-intensive subsets of the

Table 1: Performance comparison on three domains. Best results are in bold, second-best are underlined. Imp. denotes the relative improvement of our method over the strongest baseline. All results are averaged over five runs with different seeds.

<table><tr><td rowspan="2">Method</td><td colspan="4">CDs_and_Vinyl</td><td colspan="4">Cell_Phones_and_Accessories</td><td colspan="4">Fashion</td></tr><tr><td>N@1</td><td>N@5</td><td>N@10</td><td>MRR</td><td>N@1</td><td>N@5</td><td>N@10</td><td>MRR</td><td>N@1</td><td>N@5</td><td>N@10</td><td>MRR</td></tr><tr><td>Pop</td><td>0.1100</td><td>0.3237</td><td>0.4708</td><td>0.3138</td><td>0.1300</td><td>0.3173</td><td>0.4734</td><td>0.3177</td><td>0.1100</td><td>0.3241</td><td>0.4749</td><td>0.3180</td></tr><tr><td>BM25</td><td>0.1600</td><td>0.1769</td><td>0.4439</td><td>0.2852</td><td>0.2100</td><td>0.3691</td><td>0.4747</td><td>0.3741</td><td>0.2100</td><td>0.3708</td><td>0.4351</td><td>0.3650</td></tr><tr><td>SASRec</td><td>0.1400</td><td>0.3206</td><td>0.4790</td><td>0.3253</td><td>0.1200</td><td>0.3096</td><td>0.4610</td><td>0.3020</td><td>0.1300</td><td>0.2934</td><td>0.4609</td><td>0.3034</td></tr><tr><td>LLMSeqSim</td><td>0.1800</td><td>0.4157</td><td>0.5319</td><td>0.3897</td><td>0.2100</td><td>0.4267</td><td>0.5344</td><td>0.3938</td><td>0.1800</td><td>0.4364</td><td>0.5390</td><td>0.3982</td></tr><tr><td>MLLMSqSim</td><td>0.1800</td><td>0.4541</td><td>0.5418</td><td>0.4005</td><td>0.1300</td><td>0.3226</td><td>0.4778</td><td>0.3234</td><td>0.1600</td><td>0.3844</td><td>0.5067</td><td>0.3573</td></tr><tr><td>LLMRank</td><td>0.1895</td><td>0.3628</td><td>0.5085</td><td>0.3624</td><td>0.2043</td><td>0.4135</td><td>0.5299</td><td>0.3888</td><td>0.2200</td><td>0.4014</td><td>0.5359</td><td>0.3987</td></tr><tr><td>AgentCF</td><td>0.1900</td><td>0.3941</td><td>0.5169</td><td>0.3731</td><td>0.2000</td><td>0.4393</td><td>0.5496</td><td>0.4121</td><td>0.1700</td><td>0.3399</td><td>0.4943</td><td>0.3447</td></tr><tr><td>CoTAgent</td><td>0.2700</td><td>0.5941</td><td>0.6315</td><td>0.5127</td><td>0.2800</td><td>0.4334</td><td>0.5339</td><td>0.4213</td><td>0.1900</td><td>0.3783</td><td>0.5081</td><td>0.3772</td></tr><tr><td>MMEACR-DES</td><td>0.3200</td><td>0.5157</td><td>0.6088</td><td>0.4900</td><td>0.3000</td><td>0.5066</td><td>0.5926</td><td>0.4692</td><td>0.2500</td><td>0.4641</td><td>0.5708</td><td>0.4407</td></tr><tr><td>MMEACR-EMB</td><td>0.2600</td><td>0.5298</td><td>0.6074</td><td>0.4847</td><td>0.2500</td><td>0.4979</td><td>0.5815</td><td>0.4517</td><td>0.3400</td><td>0.5276</td><td>0.6179</td><td>0.5019</td></tr><tr><td>MMEACR-RRF</td><td>0.3400</td><td>0.5632</td><td>0.6354</td><td>0.5224</td><td>0.3200</td><td>0.5327</td><td>0.6214</td><td>0.5049</td><td>0.3200</td><td>0.5382</td><td>0.6230</td><td>0.5069</td></tr><tr><td>Improv(%)</td><td>20.59%</td><td>-5.20%</td><td>0.62%</td><td>1.89%</td><td>14.3%</td><td>21.26%</td><td>13.06%</td><td>19.84%</td><td>45.45%</td><td>23.33%</td><td>15.58%</td><td>27.14%</td></tr></table>

Table 2: Dataset statistics.

<table><tr><td>Data</td><td>#Users</td><td>#Items</td><td>#Inter.</td><td>Sparsity</td></tr><tr><td>CDs</td><td>100</td><td>781</td><td>500</td><td>99.36%</td></tr><tr><td>Cell_Phones</td><td>100</td><td>753</td><td>500</td><td>99.34%</td></tr><tr><td>Fashion</td><td>100</td><td>763</td><td>500</td><td>99.34%</td></tr></table>

Amazon review dataset (CDs, Cell\_phones, and Fashion).

Baselines. We evaluate our method against several representative baselines, including popularitybased Pop, text-matching BM25 (Robertson and Zaragoza, 2009), self-attention sequential recommender SASRec (Kang and McAuley, 2018) , LLM-based ranker LLMRank (Hou et al., 2024b), embedding-similarity models LLMSeqSim (Harte et al., 2023) and MLLMSeqSim, as well as the agent-based AgentCF (Zhang et al., 2024) and Co-TAgent(Wei et al., 2022). Specifically, CoTAgent incorporates zero-shot Chain-of-Thought (CoT) prompting to facilitate transparent decision-making and produce interpretable reasoning rationales for each recommendation. Pop ranks items by interaction frequency, while BM25 retrieves candidates using textual similarity to user histories. LLM-Rank uses GPT-4o-mini as a zero-shot ranker conditioned on sequential histories. LLMSeqSim constructs a session representation via LLM-generated item embeddings and retrieves top-k similar items, whereas MLLMSeqSim extends this with multimodal LLM embeddings. AgentCF treats users and items as autonomous LLM agents that interact and update memories to perform collaborative filtering. For our method MMEACR, we additionally include three variants. MMEACR-DES uses the user’s and item’s latest memories with a 1-positive-9-negative candidate set, prompting the LLM to return a ranking for computing NDCG and MMR. MMEACR-EMB fuses the user’s five recent item-image embeddings with the latest memory via GME, combines item image–title embeddings, and ranks candidates using cosine similarity. MMEACR-RRF merges the rankings from MMEACR-DES and MMEACR-EMB using the RRF formula.

Table 3: Ablation study on Cell\_phones and Fashion. Best results are in bold, and second-best results are underlined.

<table><tr><td colspan="5">Cell_phones</td></tr><tr><td>Variant</td><td>N@1</td><td>N@5</td><td>N@10</td><td>MRR</td></tr><tr><td>Full</td><td>.3000</td><td>.5066</td><td>.5926</td><td>.4692</td></tr><tr><td>w/o Attr.</td><td>.2700</td><td>.5066</td><td>.5987</td><td>.4749</td></tr><tr><td>w/o Refl. &amp; Attr.</td><td>.2200</td><td>.4743</td><td>.5663</td><td>.4323</td></tr><tr><td>w/o User &amp; Attr.</td><td>.1800</td><td>.4047</td><td>.5235</td><td>.3804</td></tr><tr><td>w/o Item &amp; Attr.</td><td>.2500</td><td>.5051</td><td>.5800</td><td>.4500</td></tr></table>

Fashion

<table><tr><td>Variant</td><td>N@1</td><td>N@5</td><td>N@10</td><td>MRR</td></tr><tr><td>Full</td><td>.2500</td><td>.4641</td><td>.5708</td><td>.4407</td></tr><tr><td>w/o Attr.</td><td>.2300</td><td>.4492</td><td>.5605</td><td>.4277</td></tr><tr><td>w/o Refl. &amp; Attr.</td><td>.2300</td><td>.4555</td><td>.5585</td><td>.4245</td></tr><tr><td>w/o User &amp; Attr.</td><td>.1500</td><td>.3245</td><td>.4826</td><td>.3305</td></tr><tr><td>w/o Item &amp; Attr.</td><td>.2300</td><td>.4317</td><td>.5468</td><td>.4107</td></tr></table>

Evaluation Metrics. We adopt a leave-one-out strategy (Kang and McAuley, 2018): for each user, the last interaction is used for testing and the second-to-last for validation. Following previous works (Zhang et al., 2024), each evaluation case includes one positive item and 9 randomly sampled negatives from the same domain.

Quantative Analysis. Table 1 reports the overall comparison across three domains. Our proposed MMEACR-RRF consistently delivers the strongest or highly competitive performance across datasets and metrics. On CDs, our method improves N@1 by 20.59% and MRR by 1.89% over the strongest baseline, while maintaining competitive performance on other metrics. The slightly lower NDCG@5 compared with CoTAgent may be attributed to the relatively low complexity of the CDs dataset, where explicit CoT reasoning is already sufficient to capture user preferences and rank relevant items effectively, leaving limited room for additional gains from attribute-guided reasoning and multimodal embedding fusion. On Cell\_Phones, the improvements are consistent across all metrics, with gains of 14.3% on N@1 and 21.26% on N@5, demonstrating robust ranking quality in more attribute-diverse scenarios. Notably, on the visually intensive Fashion domain, our approach achieves substantial gains, improving N@1, N@5, and MRR by 45.45%, 23.33%, and 27.14%, respectively, highlighting the benefit of multimodal memory modeling in visually grounded recommendation.

![](images/6edeb0db2c0c406203dfaedcd9eec722c9dafc14ce5c2be420b0b8ad8b6675aa.jpg)  
Figure 3: Case study of memory evolution and profile reflection at Round-5 across four semantic domains. Compared to AgentCF, our MMEACR demonstrates a superior capability to filter cross-modal noise and capture attribute guided user preferences (highlighted in red) such as “cohesive and relaxing mood”, “protection and aesthetic”, and “historical context”, securing more precise long-term interest alignment.

Moreover, while both single-branch variants (MMEACR-DES and MMEACR-EMB) already achieve competitive performance, the fused model consistently yields further improvements, indicating that LLM-based reasoning and multimodal embedding similarity provide complementary signals. Compared with prior agent-based methods such as AgentCF and CoTAgent, our framework demonstrates consistent advantages across domains, validating the effectiveness of structured multimodal memory and reflective agent collaboration. To evaluate the computational efficiency of our proposed framework, we compare the inference time of MMEACR against the representative agent-based baseline, AgentCF, across three datasets. As illustrated in Figure 4, MMEACR consistently achieves lower inference latency than AgentCF in all evaluated domains. Specifically, MMEACR reduces inference time by 6.15% (from 70.12s to 65.81s) on CDs, 16.27% (from 132.52s to 110.96s) on Cell\_Phones, and 15.11% (from 121.25s to 102.93s) on the Fashion dataset. These results demonstrate that while MMEACR incorporates structured multimodal memory and reflective collaboration to achieve superior ranking performance (as shown in Table 1), it simultaneously optimizes the inference pipeline, proving its high efficiency and practicality for real-world recommendation scenarios.

![](images/b4e15e9ef06a768e2e710ad2e98c2f0a3ba9612b9b9a9866b8130d9a575541bb.jpg)  
Figure 4: Inference time comparison between AgentCF and MMEACR on the three datasets. The Y-axis denotes the inference time (in seconds), while the X-axis denotes different datasets. MMEACR achieves faster inference across both datasets.

![](images/64d1922ed84b6500bb5dfb21b4149cec751006486c717538cf83d2b4e38a1769.jpg)  
Figure 5: Performance evolution on Fashion.  
MMEACR improves steadily across optimization steps and achieves the best results at test time.

Qualitative Analysis. As shown in Figure 3, while AgentCF generates coarse-grained and repetitive interest summaries (e.g., general “jazz” or “phone accessories”), MMEACR precisely captures fine-grained, specific user preferences (highlighted in red) such as a “cohesive and relaxing mood” or “heavy-duty protection with stylish design.” Furthermore, while AgentCF is vulnerable to interaction noise and suffers from preference drift by Round-5, MMEACR filters crossmodal redundancy via attribute-guided reflection, anchoring user profiles onto stable semantic blocks. This qualitative alignment corroborates our quantitative superiority, visually demonstrating that MMEACR achieves precise long-term profiling through attribute-level memory refinement.

Ablation Study. To evaluate the contribution of each component in our MMEACR framework, we conduct ablation studies by comparing the full Multi-AgentCF model (with both User Agent and Item Agent) against three simplified variants: w/o Auto. Interaction, which removes the automated interaction mechanism between agents and disables iterative mutual refinement; w/o User Agent, which excludes the User Agent and relies solely on item-side modeling; and w/o Item Agent, which removes the Item Agent and retains only user-centric reasoning. Table 3 reports results on both cell\_phones and fashion domains. The full Multi-AgentCF consistently achieves the best performance across most metrics, demonstrating the effectiveness of jointly modeling user and item agents within an interactive framework. In contrast, removing either agent leads to clear performance degradation, indicating that both user-side preference modeling and item-side contextual reasoning are essential for accurate ranking. Notably, the largest drop is observed when Auto. Interaction is removed, highlighting the importance of iterative inter-agent communication for refining memory and aligning preferences. These results verify that each component contributes to the overall performance and that their synergistic interaction is crucial for optimal recommendation quality.

Effectiveness of Iterative Memory Evolution. To investigate how iterative memory refinement enhances recommendation performance, we analyze the evolution of key metrics throughout the optimization process on the Fashion dataset. Specifically, we report results at three consecutive optimization steps and the final testing phase to capture how progressive agent collaboration affects ranking quality over time. As illustrated in Figure 5, all evaluation metrics, including N@1, N@5, N@10, and MRR, exhibit a consistent upward trend as iterative interaction between the user and item agents proceeds. In particular, the N@10 score steadily increases from 0.4463 at Step 1 to 0.5708 at the final stage, while MRR improves from 0.2833 to 0.4407, with similar gains observed for N@1 and N@5, indicating consistent improvements across different ranking depths. These results suggest that iterative memory refinement enables continuous correction and enrichment of both user preference modeling and item contextual understanding, allowing the system to progressively accumulate more reliable reasoning traces and better align multimodal representations. Overall, the observed performance trajectory validates the effectiveness of our iterative update strategy and highlights the importance of continuous agent collaboration in improving recommendation quality.

## 6 Conclusion

In this paper, we propose MMEACR, a multimodal memory-enhanced agent collaboration framework for recommendation that overcomes modal-lacking limitations in text-only LLM-based systems by jointly leveraging visual and textual features and enabling dynamic memory evolution through iterative agent interactions. By incorporating a dedicated multimodal embedding memory and RRFbased ranking fusion, MMEACR produces more accurate and interpretable recommendations. Extensive experiments on real-world datasets show that MMEACR surpasses strong baselines, particularly in capturing nuanced user preferences from multimodal signals, and ablation studies further validate the contribution of each individual component. In addition, qualitative analyses demonstrate that the proposed agent collaboration mechanism can generate more consistent and preference-aligned reasoning across interaction steps. Overall, our results highlight the effectiveness of integrating multimodal memory with iterative agent collaboration for improving recommendation quality in LLM-based systems.

## Limitations

While MMEACR demonstrates strong performance and efficient inference, one limitation is the longterm scalability of the continuous memory evolution. As user interactions scale over extended periods, the iterative accumulation in the multimodal embedding memory could potentially increase storage and retrieval costs. Although this is mitigated by our RRF-based ranking fusion in current benchmarks, optimizing the balance between memory capacity and lifelong efficiency remains a promising direction for our future work.

## References

Keqin Bao, Jizhi Zhang, Yang Zhang, Wenjie Wang, Fuli Feng, and Xiangnan He. 2023. TALLRec: An effective and efficient tuning framework to align large language model with recommendation. In Proceedings of the 17th ACM Conference on Recommender Systems (RecSys), pages 1007–1014. ACM.

Mohamed Amine Ferrag, Norbert Tihanyi, and Mérouane Debbah. 2025. From LLM reasoning to autonomous AI agents: A comprehensive review. arXiv preprint arXiv:2504.19678.

Tianqi Gao, Chengkai Huang, Zihan Wang, Cao Liu, Ke Zeng, and Lina Yao. 2026. Factorized latent reasoning for llm-based recommendation. arXiv preprint arXiv:2604.26760.

Jesse Harte, Wouter Zorgdrager, Panos Louridas, Asterios Katsifodimos, Dietmar Jannach, and Marios Fragkoulis. 2023. Leveraging large language models for sequential recommendation. In Proceedings of the 17th ACM Conference on Recommender Systems, pages 1096–1102.

Yupeng Hou, Junjie Zhang, Zhipeng Lin, Hongyu Lu, Ruobing Xie, Julian McAuley, and Wayne Xin Zhao

Zhao. 2024a. Large language models are zeroshot rankers for recommender systems. In Proceedings of the European Conference on Information Retrieval (ECIR), pages 364–381, Cham. Springer Nature Switzerland.

Yupeng Hou, Junjie Zhang, Zihan Lin, Hongyu Lu, Ruobing Xie, Julian McAuley, and Wayne Xin Zhao. 2024b. Large language models are zero-shot rankers for recommender systems. In European Conference on Information Retrieval, pages 364–381.

Chengkai Huang, Hongtao Huang, Tong Yu, Kaige Xie, Junda Wu, Shuai Zhang, Julian Mcauley, Dietmar Jannach, and Lina Yao. 2025a. A survey of foundation model-powered recommender systems: From feature-based, generative to agentic paradigms. arXiv preprint arXiv:2504.16420.

Chengkai Huang, Shoujin Wang, Xianzhi Wang, and Lina Yao. 2023a. Dual contrastive transformer for hierarchical preference modeling in sequential recommendation. In Proceedings of the 46th international acm sigir conference on research and development in information retrieval, pages 99–109.

Chengkai Huang, Shoujin Wang, Xianzhi Wang, and Lina Yao. 2023b. Modeling temporal positive and negative excitation for sequential recommendation. In Proceedings of the ACM Web Conference 2023, pages 1252–1263.

Chengkai Huang, Junda Wu, Yu Xia, Zixu Yu, Ruhan Wang, Tong Yu, Ruiyi Zhang, Ryan A Rossi, Branislav Kveton, Dongruo Zhou, and 1 others. 2025b. Towards agentic recommender systems in the era of multimodal large language models. arXiv preprint arXiv:2503.16734.

Chengkai Huang, Tong Yu, Kaige Xie, Shuai Zhang, Lina Yao, and Julian McAuley. 2024a. Foundation models for recommender systems: A survey and new perspectives. arXiv preprint arXiv:2402.11143.

Hongtao Huang, Chengkai Huang, Tong Yu, Xiaojun Chang, Wen Hu, Julian McAuley, and Lina Yao. 2024b. Dual conditional diffusion models for sequential recommendation. arXiv preprint arXiv:2410.21967.

Aaron Hurst, Adam Lerer, Adam P Goucher, Adam Perelman, Aditya Ramesh, Aidan Clark, AJ Ostrow, Akila Welihinda, Alan Hayes, Alec Radford, and 1 others. 2024. Gpt-4o system card. arXiv preprint arXiv:2410.21276.

Shuguang Jiao, Chengkai Huang, Shuhan Qi, Xuan Wang, Yifan Li, and Lina Yao. 2026a. Doctor-rag: Failure-aware repair for agentic retrieval-augmented generation. arXiv e-prints, pages arXiv–2604.

Shuguang Jiao, Xinyu Xiao, Yunfan Wei, Shuhan Qi, Chengkai Huang, Quan Z Sheng, and Lina Yao. 2026b. Prunerag: Confidence-guided query decomposition trees for efficient retrieval-augmented generation. In Proceedings of the ACM Web Conference 2026, pages 1923–1934.

Wang-Cheng Kang and Julian McAuley. 2018. Selfattentive sequential recommendation. In 2018 IEEE international conference on data mining (ICDM), pages 197–206. IEEE.

Yifan Li, Ismail Jafarov, Kenan Zeynalov, and Chen Tang. 2025. CLEAR-Rec: A contrastive long-term memory-enhanced, explainable, and adaptive recom mendation framework. In Proceedings of the 2nd International Conference on Artificial Intelligence of Things and Computing, pages 236–244. ACM.

Jiahao Liu, Shengkang Gu, Dongsheng Li, Guangping Zhang, Mingzhe Han, Hansu Gu, Peng Zhang, Tun Lu, Li Shang, and Ning Gu. 2025. Agentcf++: Memory-enhanced llm-based agents for popularityaware cross-domain recommendations. In Proceed ings of the 48th International ACM SIGIR Conference on Research and Development in Information Retrieval, pages 2566–2571. ACM.

Chenyang Lyu, Minghao Wu, Longyue Wang, Xinyu Huang, Binhang Liu, Z those Du, Ziyu Min, Hui Su, Dengqun Bi, Guanjie Pan, , and 1 others. 2023. Macaw-LLM: Multi-modal language modeling with image, audio, video, and text integration. arXiv preprint arXiv:2306.09093.

Stephen Robertson and Hugo Zaragoza. 2009. The probabilistic relevance framework: Bm25 and beyond. Foundations and Trends in Information Retrieval, 3(4):333–389.

Anuja Salve, Shreyas Attar, Mansi Deshmukh, Satej Shivpuje, and Aashish Manik Utsab. 2024. A collaborative multi-agent approach to retrieval-augmented generation across diverse data. arXiv preprint arXiv:2412.05838.

Tian Shi, Jing Xu, Xin Zhang, Xiaolei Zang, Ke Zheng, Yue Song, and Hang Li. 2025. Retrieval augmented generation with collaborative filtering for personalized text generation. In Proceedings of the 48th International ACM SIGIR Conference on Research and Development in Information Retrieval, pages 1294– 1304. ACM.

Zhenheng Tang, Xin He, Tiancheng Zhao, Fanjunduo Wei Wei, Xiang Liu, Peijie Dong, Qian Wang, Zehao Li, Xiaowen Chu, , and 1 others. 2026. Llm agent memory: A survey from a unified representation–management perspective. arXiv preprint arXiv:2603.03590.

Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, Fei Xia, Ed Chi, Quoc V Le, Denny Zhou, and 1 others. 2022. Chain-of-thought prompting elicits reasoning in large language models. In Advances in Neural Information Processing Systems, volume 35, pages 24824–24837.

Juexiang Ye, Xue Li, Yang Xinyu, Chengkai Huang, Lanshun Nie, Lina Yao, and Dechen Zhan. 2026. Memweaver: Weaving hybrid memories for traceable long-horizon agentic reasoning. In Findings of the Association for Computational Linguistics: ACL 2026, pages 12928–12956.

Junjie Zhang, Yupeng Hou, Ruobing Xie, Wenqi Sun, Julian J. McAuley, Wayne Xin Zhao, Leyu Lin, and Ji-Rong Wen. 2024. Agentcf: Collaborative learning with autonomous language agents for recommender systems. In Proceedings of the ACM on Web Conference, pages 3679–3689. ACM.

Xin Zhang, Yanzhao Zhang, Wen Xie, Mingxin Li, Ziqi Dai, Dingkun Long, Pengjun Xie, Meishan Zhang, Wenjie Li, and Min Zhang. 2025a. Gme: Improving universal multimodal retrieval by multimodal llms. Preprint, arXiv:2412.16855.

Zhen Zhang, Quanyu Dai, Xiangbo Bo, Chen Ma, Ronghua Li, Xu Chen, Ruiming Zhang, Ji-Rong Wen, , and 1 others. 2025b. A survey on the memory mechanism of large language model-based agents. ACM Transactions on Information Systems (TOIS), 43(6):1– 47.

Zhe Zhao, Wenqi Fan, Jiatong Li, Xiao-Yu Liu, Xiao Mei, Yanan Wang, Qing Li, and 1 others. 2024. Recommender systems in the era of large language models (LLMs). IEEE Transactions on Knowledge and Data Engineering (TKDE), 36(11):6889–6907.

## A Computational Cost and Efficiency

Due to the high cost of LLM API calls, we sample 100 users and their historical interactions per dataset, leading to about 500 interaction steps across 5 training rounds. We use a tiered model strategy, where GPT-4o (Hurst et al., 2024) is applied for memory initialization, interaction simulation, and inference-time ranking, balancing reasoning quality with efficiency and supporting asynchronous batch processing (batch size 4 for training, 5 for evaluation).

At inference, description-based ranking (DES) prompts GPT-4o with the user’s natural-language memory profile and 10 candidate item descriptions to directly output a ranked list, which is mapped back to item IDs using fuzzy matching. In parallel, embedding-based ranking (EMB) encodes user memory and multimodal item content into dense vectors and ranks candidates via cosine similarity without LLM inference. The final result is obtained by fusing DES and EMB rankings using Reciprocal Rank Fusion, with a fallback to EMB-only when DES outputs are invalid.

Overall, inference cost is dominated by a single LLM call per user, and full evaluation remains efficient, completing within about 100 seconds per dataset and showing a 6–16% speedup over AgentCF due to the streamlined memory design and shorter prompts.

## B Algorithm

<div class="mineru-algorithm" style="white-space: pre-wrap; font-family:monospace;">
Algorithm 1: Dual-Stage Attribute-Guided Memory Update (UAMG)

Input :Turn $t \in \{1, \ldots, T\}$; positive title $s^{+}$, negative title $s^{-}$; prior user memory $U^{(t-1)}$; item memories $M^{+}, M^{-}$.

Output: Updated memories $U^{(t)}, M^{+(t)}, M^{-(t)}$.

// Stage 1: Agent decision
1 $P_{ch} \leftarrow$ ChoicePrompt($U^{(t-1)}, s^{+}, s^{-}, M^{+}, M^{-}$)
2 ($\hat{s}, r$) ← LLM($P_{ch}$) // $\hat{s}$: chosen title; r: rationale
3 $y \leftarrow \mathbb{1}[Match(\hat{s}, s^{+}) &gt; Match(\hat{s}, s^{-})] // y = 1$: correct

// Stage 2: Attribute extraction
4 if y = 1 then
5    A ←
    LLM(Attr$_{+}$($U^{(t-1)}, s^{+}, s^{-}, M^{+}, M^{-}, r$))
6 else
7    A ←
    LLM(Attr$_{-}$($U^{(t-1)}, s^{+}, s^{-}, M^{+}, M^{-}, r$))
8 end

// Stage 3: Memory update
9 ($P_u, P_i$) ←
UpdatePrompt($U^{(t-1)}, M^{+}, M^{-}, s^{+}, s^{-}, r, A, y$)

10 $\tilde{U}, \tilde{M}^{+}, \tilde{M}^{-} \leftarrow \text{LLM}(P_u), \text{LLM}(P_i)$
11 return $U^{(t)}, M^{+(t)}, M^{-(t)}$
</div>

## C Prompt Templates

![](images/2c78718cef0428c9eb986d573dae74271c7b03fea7751776f47efe9aa04ced9b.jpg)  
Figure 6: The structured query wrapper template containing rules, formatting, and variables for correct attribute analysis and extraction.

![](images/8ae16336220459869d4a86f3bf2460873453350f87b7727a113c01f278988a33.jpg)  
Figure 7: The structured query wrapper template containing rules, formatting, and variables for incorrect attribute analysis and extraction.

![](images/fb67018f8bca96b1bb6322872a8a24f3a444b51fcb68b3335c1c75e243a5cfcb.jpg)  
Figure 8: The structured prompt template for successful preference confirmation and personalized self-introduction refinement.

![](images/e358ab7a230877ca2ff7316e601ad7aa542256ee2dab666a07a3590457d6edc4.jpg)  
Figure 9: The structured prompt template for attribute-level misconception correction and personalized selfintroduction updating.

![](images/3ef74bdb708db87ad953e439170f32144a48132f0b54656794ff1759298b0829.jpg)  
Figure 10: The structured prompt template for successful preference confirmation and self-introduction refinement without explicit attribute-level guidance.

![](images/dd09b4f56c6ea66c813ff280dc3b1fdf1bd70d33fbb2cd1ffb8192df2dfc29b1.jpg)  
Figure 11: The structured prompt template for preference correction and self-introduction updating without explicit attribute-level guidance.


---

# 2508.00543_长尾推荐再探：LLM弥合流行度差距

[2508.00543](https://arxiv.org/abs/2508.00543)

Research Article

Christian Neurohr\*, Marcel Saager, Lina Putze, Jan-Patrick Osterloh, Karina Rothemann, Hilko Wiards, Eckard Böde, and Axel Hahn

# Towards Eficient Certification of Maritime Remote Operation Centers – Ansatz zur efizienten Zertifizierung von maritimen Fernsteuerungszentren

https://doi.org/..., Received ...; accepted ...

Abstract: Additional automation being build into ships implies a shift of crew from ship to shore. However, automated ships still have to be monitored and, in some situations, controlled remotely. These tasks are carried out by human operators located in shore-based remote operation centers. In this work, we present a concept for a hazard database that supports the safeguarding and certification of such remote operation centers. The concept is based on a categorization of hazard sources which we derive from a generic functional architecture. A subsequent preliminary suitability analysis unveils which methods for hazard analysis and risk assessment can adequately fill this hazard database. – Die zunehmende Automatisierung von Schifen führt zu einer Verlagerung der Besatzung vom Schif ans Land. Automatisierte Schife müssen jedoch weiterhin überwacht und in bestimmten Situationen ferngesteuert werden. Diese Aufgaben werden von menschlichen Operateuren in landgestützten Fernsteuerungszentren ausgeführt. In dieser Arbeit stellen wir ein Konzept für eine Gefährdungsdatenbank vor, welche die Sicherung und Zertifizierung solcher Fernsteuerungszentren unterstützt. Das Konzept basiert auf einer Kategorisierung von Gefährdungsquellen, abgeleitet aus einer generischen Funktionsarchitektur. Eine anschließende vorläufige Eignungsanalyse zeigt, welche Methoden zur Gefährdungsanalyse und Risikobewertung diese Gefährdungsdatenbank füllen können.

Keywords: Remote Operation Center, Autonomous Surface Ships, Hazard Analysis & Risk Assessment, Safety, Certification, Human Factors – Fernsteuerungszentrum, Autonome Überwasserschife, Gefährdungsanalyse und Risikobewertung, Sicherheit, Zertifizierung, Menschfaktoren

## 1 Introduction

Increasing levels of automation is being build into vessels, leading to the advent of Maritime Autonomous Surface Ships (MASS), as defined by the Internation Maritime Organization (IMO) [29]. Shore-based Remote Operation Centers (ROCs) are emerging as a supplemental technology alongside MASS to monitor or remote-control such ships in harbors, in coastal waters, or for inland waterways [19, 7]. There exist various novel approaches adapted for the Hazard Analysis and Risk Assessment (HARA) of MASS to cope with the complexity that is introduced by automation technology [56]. For example, the Risk-based Assessment Tool commissioned by the European Maritime Safety Agengy (EMSA) [34]. Regarding classification of MASS, there exists class guidelines such as the DNV-CG-0264 on Autonomous and Remotely Operated Ships. These safeguarding approaches are centered around MASS and possible remote control components are considered as MASS functionality. Therefore, the safety of ROCs is considered as part of the MASS HARA. In this concept paper, we put forth the idea to collect safety-relevant artifacts for a generic ROC in a database to enable their reuse. Hence, to facilitate more eficient certification of MASS-ROC pairs, we tackle the research question

How can we build a hazard database that integrates technical as well as human hazards and facilitates the eficient certification of generic ROC-MASS pairs with well-defined interfaces?

In this regard, we contribute

∙ a review of standards, regulations, and HARA methods in the maritime domain in section 2,

∙ a generic ROC-MASS functional architecture as a starting point for a hazard database in section 3,

∙ a categorization of hazard sources for ROCs, a suitability analysis for methods to adequately cover these categories, and potential benefits of a hazard database in section 4.

## 2 Related Work

In this section, with a distinct focus on ROCs, we briefly review relevant standards and regulations in the maritime domain in subsection 2.1 and relevant HARA methods in subsection 2.2.

## 2.1 Relevant Standards and Regulations

IMO MASS Code: Within the IMO, the Maritime Safety Committee (MSC) developed the Interim Guidelines for MASS Trials in 2019 [25]. These interim guidelines seek to assist authorities and stakeholders to conduct trials for MASS and related systems safely, securely, and under environment protection. These guidelines were specifically formulated for experimental trials over limited periods. The MASS Code is on track to be finalized in its non-mandatory form in 2026 [26]. The code uses a goal-based approach, focusing on performance standards rather than prescriptive rules.

DNV-RU-SHIP(Pt.6,Ch.12): The classification society DNV updated their rules for classification document in 2024 to introduce the Autonomous and Remotely Operated Ships (AROS) class notation [13]. AROS as a framework wants MASS to be at least as safe as conventional vessels. Therein, the term autoremote refers to operations, tasks, functions, or systems that enhance decision support, remote control, or autonomy compared to traditional crewed ships. There are four AROS notations – navigation, engineering, operations, safety – each with one qualifier for operation mode and one describing the control location.

DNV-CG-0264: The Class Guideline DNV-CG-0264 [12], developed by DNV, aims to provide guidance for the safe implementation of novel technologies in the context of autoremote vessel functions. Further, it formulates a recommended work process to obtain the approval of novel concepts. Overall, the framework is designed to ensure that the implementation of innovative concepts and technologies meets or exceeds the safety standards of traditional vessel operations. It also outlines the specific class notations applicable to autonomous and remotely operated ships (AROS), cf. [13].

DNV-ST-0324: The DNV-ST-0324 standard provides a set of required competences for humans operating ROCs, i.e., operators tasked with supporting, monitoring, or controlling MASS from a remote, shore-based location [11]. The standard makes suggestions on the necessary skills and knowledge for human ROC-operators regarding communication, navigation, machinery, and cargo. As such the standard is highly relevant to the identification of hazards (and their causes) related to human factors – due to ROC-operator potentially lacking basic skills or knowledge. The DNV-ST-0324 is complemented by the recommended practice DNV-RP-0323 regarding certification schemes for ROC-operators [10]

ISO 23860: The technical specification ISO/TS 23860 covers vocabulary for highly automated or autonomous ships [29]. It introduces terms ranging from related to autonomous ship systems, e.g., autonomy and control. In this work, we will follow the ISO/TS 23860’s definition for terms such as ROC or MASS. Furthermore, the standard addresses the interrelations of terms for autonomous ships such as the relations between of ROC, MASS, and support services.

CMOROC: Based on the ISO/TS 23860, the EMSA study ‘CMOROC - Identification of Competences for MASS Operators in Remote Operation Centres’ analyses the requirements for future operators of MASS from ROC. It is based on three representative ship types (feeder, RoPax ferry, bulk carrier) and examines which tasks are required in a ROC and which competences are necessary for this. The study identifies diferent levels of automation and develops a structured model for the operation and distribution of roles within a ROC. A key result is a catalogue of skills based on the STCW (Standards of Training, Certification and Watchkeeping for Seafarers), which is used as the basis for training. Building on this, a basic and an advanced curriculum is being developed [30].

ISO 26262 & ISO 21448: The ISO 26262 [27] and ISO 21448 [28] are safety standards from the automotive domain that complement each other. While the ISO 26262 focuses on functional safety – addressing risks arising from system failures, ISO 21448 is concerned with the safety of the intended functionality (SOTIF). SOTIF addresses risks that arise not from system failures, but from insuficiencies in the specification, performance limitations or the inability to detect or prevent reasonably foreseeable misuses. ISO 21448 provides a structured framework that ofers guidance on managing SOTIF for road vehicles equipped with automated driving systems. The standard organizes the main SOTIF activities and defines high-level objectives to support a systematic development and validation process [42]. Although the ISO 21448 specifically targets driving automation, the concept of SOTIF is also highly relevant for automated systems in other domains.

## 2.2 Relevant Methods for Hazard Analysis and Risk Assessment

For conventional vessels, there exists a wide range of well-established HARA methods which are commonly applied in practice, e.g., Failure Mode and Efect Analysis (FMEA) or Fault Tree Analysis (FTA). To address the specific challenges posed by automated maritime systems, such as their reliance on sensor perception and the complexity of system interactions, adaptions of established methods as well as new approaches have been explored in recent research [56, 47, 36]. However, only a limited number of studies explicitly consider ROCs. A literature review provided by Zhou et al. [57], which evaluates the suitability of commonly used HARA methods for automated maritime system, highlights this gap. Notably, the authors observe that among the evaluated studies, so far only System-Theoretic Process Analysis (STPA) was applied with explicit consideration of the communication between vessel and ROC [54, 55, 49, 1]. Similarly, another literature review on risk models for automated maritime systems by Thieme et al. [47] reports that only two of the investigated studies explicitly address the communication with a ROC – one employing STPA, and the other a combination of brainstorming and Bayesian Networks [54, 53]. Furthermore, Li et al. emphasize the importance of incorporating human factors into the HARA of automated maritime systems, noting that these systems constitute highly complex socio-technical systems in which the role of the remote operator is significantly more complex than that of a traditional onboard operator [36].

In the following, we briefly introduce common HARA methods that may be applicable for ROCs, as well as some emerging approaches specifically developed for highly automated systems. As the human operator is of particular relevance for remote operation, we consider not only HARA methods focusing on technical system safety but also methods that explicitly address human factors.

## Technical System Safety

There exists a variety of methods for identifying and analyzing hazards arising from faults or insuficiencies within the system, each with a slightly diferent focus. Some approaches emphasize the identification of component failures, while others concentrate on the analysis of causal chains or the evaluation of the associated risks. The methods employ either inductive or deductive reasoning strategies and can be tailored for specific stages of the system development process. Moreover, HARA tech niques can be roughly classified as qualitative or quantitative, depending on whether they primarily rely on expert judgment or derive probabilistic statements from data.

A broadly applied hazard analysis method is the Failure mode and efects analysis (FMEA) [44]. FMEA follows a seven-stage procedure, that focuses on identifying failure modes, their causes and efects on the overall system. The method relies on inductive reasoning and emphasizes systematic documentation throughout the analysis process. Typically, FMEA is conducted by an interdisciplinary team ensuring comprehensive consideration of system interactions. FMEA provides a semi-quantitative method, supporting risk assessment by the calculation of a risk priority number (RPN), which is derived from the estimated probability of occurrence, significance, and the error’s detectability. The implementation of FMEA at an early stage in the development process has been shown to result in a substantial and quantifiable reduction in the likelihood of potential errors [31]. Originally developed by the US military, FMEA has become a widely adopted tool across various domains including the maritime sector [37, 15].

Another common method is the Hazard and Operability study (HAZOP) which provides a systematic approach to identify potential hazards in systems of all kinds [9]. The method was developed in the 1970s in the chemical industry and is now employed in numerous domains. HAZOP is qualitative method that employs a systematic brainstorming approach utilizing keywords to investigate deviations from specified behavior. An interdisciplinary team examines the system under consideration from diferent perspectives to identify potential causes of errors, their consequences, and countermeasures.

A method that is designed to analyze causal chains leading to harm is the Fault Tree Analysis (FTA). FTA is a deductive top-down hazard analysis method which aims at identifying and evaluating combinations of faults and failures that can lead to a predefined undesired event, commonly referred to as ’top level event’. Using Boolean logic and a hierarchical structure of logical gates (e.g. AND, OR), FTA systematically decomposes system-level failures into basic events at component level. This approach enables both qualitative understanding and quantitative risk assessment, including the cal culation of failure probabilities. Initially developed in the aerospace and nuclear industries [51], FTA has been widely adopted in various sectors. It is particularly valued for its structured reasoning, and ability to support quantitative risk assessment. FTA is especially efective when applied to hardware dominated systems. However, extensions have been developed to address human-related hazards and SOTIF, such as provided by Birch et al. [4] or Kramer et al. [33].

Similar to FTA, Event tree analysis (ETA) employs a logic tree structure to model potential progression of accidents capturing system responses and failure chains. In contrast to FTA, however, ETA relies on inductive reasoning determining possible outcomes that may result from a specific initiating event [17]. ETA supports both qualitative and quantitative risk evaluation.

Bayesian Networks (BNs), also known as belief networks, provide another method to investigate causal chains. BNs are probabilistic graphical models that represent variables and their condi tional dependencies using directed acyclic graphs [40, 41]. In BNs, each node corresponds to a system variable, while the edges represent statistical or causal dependencies, quantified through conditiona probability tables. BNs enable reasoning under uncertainty by relying on principles of probability the ory, making them highly suitable for complex systems that are employed in uncertain environments. BNs were originally developed for decision support and diagnostics and have been adapted for use in various safety-critical domains. Their ability to integrate both expert judgment and empirical data makes them particularly valuable for probabilistic risk assessment of dynamic and complex systems.

System-Theoretic Process Analysis (STPA) developed by Leveson and Thomas [35] is a relatively novel hazard analysis method grounded in system theory. It conceptualizes safety as a control problem emphasizing inadequate control actions within socio-technical systems rather than isolated component failures. This perspective makes STPA especially well-suited for systems with complex interactions and software components. STPA employs a top-down approach consisting of four main steps: First, the goals of the analysis are defined in form of losses. In the second step, the system is modeled in form of a hierarchic control structure. Based on this model, unsafe control actions are identified using a keyword-based technique. Finally, so called loss scenarios are derived containing causal factors that may lead to the unsafe control actions. Originally developed for aerospace, STPA has since been adapted across various industries. In the maritime domain, STPA has gained relevance in the context of autonomous vessels [57, 36].

A framework that has been developed by EMSA particularly for the hazard analysis of MASS is the Risk-based Assessment Tool (RBAT). RBAT provides a structured methodology to compare automation and remote operations safety with conventional shipping [34]. The methodology consists of five main parts and a total of 19 steps, encompassing the description of automation usage, hazard identification, mitigation analysis, to risk assessment and risk control. Central to RBAT is the modeling of vessel missions, control functions and the qualitative assessment of risks. Risk levels for each scenarios are derived from a combination of worst-case outcome severity, the efectiveness of mitigation measures and the vessels exposure to enabling conditions. Rather than focusing on the probability of systematic failures, the method integrates technical and operational aspects and emphasizes minimizing the consequences of functional failures. A key feature of RBAT is the explicit integration of Remote Operation Centers (ROC) as supervisory unit within the safety analysis. The methodology enables the systematic identification of scenarios, in which the ROC is required to intervene, the information it must receive to perform this role, and the system architecture necessary to support interventions

– particularly in relation to mitigation strategies. Supervisory control agents located within the ROC operate in either an active or passive monitoring capacity, typically involving human operators. The efectiveness of mitigation measures attributed to the ROC is thus evaluated not only on the technical basis, but also with regard to human performance factors, such as operator response time or workload.

Another method specifically developed for automated systems has been proposed by Kramer et al. [33, 6]. The Automation Risk method has initially been designed for automotive applications, but has also been transferred to the maritime domain [50, 21]. It aims to identify and evaluate hazardous scenarios, thereby supporting a scenario-based safety assessment. Conceptually, the method draws upon HAZOP and FTA, adapting and integrating elements of both to address the specific challenges that arise for highly automated systems.

## Human Factors

Human factors risk analysis methods have become essential for understanding and mitigating the impact of human error in complex systems. These methods recognize that performance is shaped by a combination of individual capabilities, organizational culture, environmental influences, and system design. Traditional engineering risk assessment techniques often fall short in capturing these human and organizational dimensions, prompting the development of dedicated methodologies. Broadly speaking, human factors analysis approaches can be classified into predictive methods, which aim to anticipate potential errors during system design, and retrospective methods – like HFAC [52] or HFACS-MA [8] – that analyze incidents after they occur. This paper focuses on predictive methods suitable for integration into early system development phases.

One such predictive methodology is the Systematic Human Error Reduction and Prediction Approach (SHERPA), which provides a structured framework for anticipating human errors during task performance. Introduced by Embrey [16], SHERPA employs hierarchical task analysis to decompose complex operations into subtasks and applies error mode identification to foresee potential failure modes. Its strength lies in its proactive application during system design, helping to prevent errors by addressing both internal human factors and external, error-promoting conditions.

THERP, or the Technique for Human Error Rate Prediction, ofers a quantitative means of evaluating human reliability, especially in high-risk settings like nuclear power. Developed by Swain and Guttmann [46], this method integrates task analysis with human error probabilities and performance-shaping factors to deliver probabilistic risk estimates. While modeling human variabil ity remains a challenge, THERP’s primary value is in supplying numerical data to broader system reliability assessments.

The Functional Resonance Analysis Method (FRAM) is presented by Hollnagel [24] as a paradigm shift from traditional accident analysis methods toward understanding complex socio technical systems. Resilience engineering has consistently argued that safety is more than the absence of failures, and FRAM builds on this foundation. FRAM is based on four principles: the equivalence of failures and successes, the central role of approximate adjustments, the reality of emergence, and functional resonance as a complement to causality. Unlike conventional methods that focus on what went wrong, FRAM is used to model the functions that are needed for everyday performance to succeed, and this model can then be used to explain specific events by showing how functions can be coupled. Over the past two decades, systemic-based risk assessment methods have garnered more attention, and FRAM is one of the most widely used systemic methods for risk assessment and accident analysis. The method represents Hollnagel’s evolution from the more traditional CREAM approach [23] toward understanding how normal performance variability can lead to both successful and unsuccessful outcomes in complex systems.

In the medical domain, human error analysis has evolved to include integrated techniques like the Human Factors Failure Mode and Efects Analysis (HF-FMEA). Song et al. [45] demonstrate how combining traditional FMEA with human factors considerations enhances safety in medical device usage. Their approach allows for systematic identification of possible user-related errors, risk evaluation, and prioritization of preventive measures, adapting a well-established reliability tool to address human contributions more directly.

Another valuable technique, the Success Likelihood Index Method (SLIM), is used to assess human reliability in specialized maritime operations such as pilot transfers. Aydin and colleagues [2] show how SLIM, when integrated with the HFACS-PV framework, enables both qualitative and quantitative analysis of performance-shaping factors. This combination helps to clarify mechanisms behind human error while also estimating error probabilities, contributing to comprehensive maritime safety assessments.

In the petroleum sector, Petro-HRA (Petroleum Human Reliability Assessment) has been developed as an industry-specific method tailored to ofshore operations. As outlined by Blackett et al. [5], this approach enables both qualitative and quantitative evaluation of tasks afecting major accident risk. Its emphasis on post-initiating event scenarios, complex technical systems, and harsh operational environments underscores the limitations of generic HRA tools and the value of specialized adaptations.

The Analysis of Pre-Accident Operator Actions (APOA) ofers another perspective by focusing on human actions occurring prior to accident events. Øie and Fernander [39] introduce APOA as a structured method for tracing the sequence of decisions and actions that influence accident development. By examining the timing and context of human involvement, this approach enhances understanding of how specific actions may either exacerbate or mitigate incident outcomes, particularly in petroleum and maritime contexts.

The CRIOP (Crisis Intervention and Operability Analysis) framework is adopted by Hoem, Rødseth, and Johnsen [22] as an interdisciplinary risk analysis method specifically applied to the design of remote control centers for maritime autonomous systems. The authors demonstrate how CRIOP can be efectively utilized to identify and analyze human factors risks in the emerging field of autonomous maritime operations, where traditional shipboard crew operations are replaced by shore-based remote monitoring and control. Their work shows how the CRIOP framework addresses the unique challenges of designing human-machine interfaces and operational procedures for remote maritime operations, considering both technical system capabilities and human operator competency requirements. The paper illustrates the framework’s value in bridging the gap between human factors analysis and system design in advanced maritime technologies, providing a structured approach to ensure that remote control centers are designed with appropriate consideration of human performance limitations and requirements.

Taken together, these methodologies illustrate the expanding toolkit available for human factors analysis. Their diverse strategies – from structured task analysis to probabilistic modeling and cogni tive frameworks – highlight the critical importance of anticipating human error during system design. By integrating these predictive methods early in the development process, industries can better man age safety risks and improve system resilience across a range of high-hazard domains.

## 3 Maritime Remote Operation Centers

Following the literature review of section 2, we now move to our modeling activities. In subsection 3.1, we introduce maritime ROCs as preparation for the conceptual description of the hazard database. As a illustrating use-case we describe berthing in a port in subsection 3.2. This leads to a generic MASS-ROC functional architecture described in subsection 3.3.

## 3.1 Introduction to Maritime ROCs

A ROC is a shore-based control center required for monitoring, controlling and supporting MASS. Depending on the level of automation, MASS can be highly automated or autonomous surface ships that can be remotely monitored and controlled by a ROC. Although the ROC operators are physically separated from the ship, they perform important tasks during regular operations, in extreme situations, and when making critical decisions [29]. The main features of a ROC are:

∙ there is a human operator (HO)

∙ it centralizes the monitoring and remote control of MASS

∙ its operating modes range from passive monitoring to active remote control of the ship

∙ it ofers a high degree of automation on board with minimal human intervention if required,

∙ it has technical interfaces to navigation systems, sensors, communication, emergency management.

Importantly, the ISO/TS 23860 specifies four diferent operation modes for ROCs [29]:

Strategic Control: In this mode, the operator provides instructions to the entire fleet. This covers planning and organisational tasks. For example, a strategy for saving fuel under certain conditions may be communicated.

Tactical Control: We are now moving to the individual MASS level. Tactical control is used to influence the decision making of an automation system. In contrast to the long-term approach of strategic control, tactical control takes a more short-term view. For example, decisions on routing or adjusting speeds in cooperation with the automated system (which directly controls the MASS).

Direct Control: Direct control means interacting directly with the functions of the MASS. This would directly override the decisions of an automation system. The operator literally controls the MASS. This includes all parameters and processes that can be manipulated and controlled. For example direct remote control of the MASS. It would be possible to take over the control directly in dificult situations, such as lock passages or at berthing places where the limits of the automation have been reached. In order to take over direct control from automation to operator, coordination must be carried out within the context of Human-Automation cooperation.

Monitoring: Monitoring includes the observation and evaluation of the MASS (the ship and the automation) and the environment or situation in which the MASS is located. The aim is therefore to recognise deviations or anomalies in order to be able to react to them. Operators in the ROC monitor by receiving information about relevant processes via displays and control panels. Alarms also help them to quickly draw attention to a deviation or anomaly.

![](images/0f42a8b10716b4dde3ac06fbdf0210feea505862d8935a8f32565a5ed73d3ab3.jpg)  
Fig. 1: Tasks, Actors, and Resources derived from ISO/TS 23860.

Figure 1 shows the ROC from a human factors perspective. The diferent control modes are represented as potential actors. Although the crew on board and the automation of the MASS are located outside the ROC, they are important actors to the overall concept. Depending on the degree of automation, a crew on board may be optional.

## 3.2 Use Case Example: Takeover Request during Port Entrance

To substantiate our approach, we sketch a use case for which a MASS-ROC certification may be required. Consider a shore-based ROC controlling a MASS in a harbor where berthing is generally dificult due to its geometry. For our use case we assume that a MASS – controlled by the automation

– approaches the harbor area and wants to dock at the berth. In addition, there is a crew on board that can take over some nautical or technical tasks if required. The ROC operator assists the ship in safely entering the port and during the berthing maneuver. Here, support is provided either tactically by intervening in the automation, or – if necessary – by directly controlling individual ship functions remotely. Figure 2 depicts this use case which is considered a typical process occurring in daily ship operations. The goal is to certify this MASS-ROC pair for this use case eficiently.

![](images/64d69baa0e5f0a1b8c52e02ffb78a65560c9723a7816f5f500de12b4d8944b51.jpg)  
Fig. 2: Use case: MASS maneuvering from harbor entrance to berth, adapted from Saager et al. [43].

Next, we want to model a functional architecture for this use case. This forms the basis for a subsequent HARA and also for a potential database scheme. The results can therefore fill the hazard database with content for that use case. This, in turn, aids the certification process for other ROC MASS pair in this use case.

## 3.3 Functional Architecture

We start by modeling the functional architecture of a generic MASS-ROC pair at a high level of abstraction with a focus on the flow of information. This functional architecture, shown in Figure 3, serves as a starting point for building a hazard database as it defines generic interfaces between the involved entities. Note that the abstraction level needs to be detailed enough to enable the identification and analysis of hazards and abstract enough to keep HARA eforts manageable. Inside the ROC itself, we model exactly one control station with three components:

![](images/79d89803352871ec9e67a8341cf677e35502107d5e6d978986b083551e5cc7a2.jpg)  
Fig. 3: Functional architecture for a single control station inside a shore-based ROC and a generic MASS. The flow of in formation in encoded by three diferent types of arrows.

Data Communication Middleware (DCM): This component is responsible for managing the exchange of data between the ROC and the MASS. As indicated by the blue color coding, this component is present in the MASS as well. However, for brevity, we abstain from explicitly modeling it within the MASS here. Crucially, the DCM defines the interfaces between the ROC and the MASS. As input to the ROC we have the transfer of all relevant data from the MASS. This inncludes the MASS’s data model and environment model. On the side of the ROC’s output, the DCM facilitates remote control (direct or tactical) of the MASS by the ROC’s human operator.

Human Machine Interface (HMI): The HMI bridges the gap between all inputs to the ROC and its outputs by interacting with the ROC’s human operator. In particular, the HMI feeds the human operator’s mental model with a visual, acoustic and haptic representation of data as well as human communication from external entities such as the MASS’s human operator (if present), vessel trafic service (VTS), the harbor ofice, and other ships. His mental model infuses the decision making which directly leads to the human operator’s output in form of either taking control of the MASS or communication with other humans - both of which are managed by the HMI’s communication hub.

Human Operator: The final component of the ROC is the human operator. All his actions within the ROC are through the HMI. His output is the HMI’s input and vice versa as described before in section 3.1.

The functional architecture of Figure 3 can now be used with various HARA methods. For example, it supports keyword-based approaches to hazard identification such as HAZOP – which are also suggested by RBAT [34, § 4.2]. Note that for a concrete ROC, the level of detail should be expanded locally when conductive for hazard identification and analysis. E.g., applying the keyword not provided to visual, acoustic, and haptic representation of data, a more detailed modeling of the HMI’s data representation functionality becomes necessary. If one wants to use STPA, a corresponding control loop can easily be derived from the architecture of Figure 3. Moreover, methods for causal analysis such as FTA/ETA or causal Bayesian [20] networks profit greatly from a functional architecture, because it supports the modeling of the system’s internal dependencies.

## 4 Building a Hazard Database for Remote Operation Centers

Similar to the database of criticality phenomena for automated driving systems suggested in previous work, cf. Neurohr et al. [38, § 4.2.1] and Babisch et al. [3], we propose to collect generic safety artifacts for maritime ROCs in a Hazard-DB. This Hazard-DB can include suitable abstractions of

∙ hazards and their potential sources,

∙ the corresponding causal relations [32],

∙ risks and harms associated with these hazards, and

∙ strategies and mechanisms for risk mitigation.

When such safety-relevant artifacts have been identified and analyzed during a HARA for a concrete MASS-ROC pair, they can be integrated into the Hazard-DB, cf. Figure 4. This includes an appropriate abstraction step, as the goal is to reuse these artifacts for future HARAs.

## 4.1 Categorization of Hazard Sources

In order to gain an initial structure for HARA artifacts within a hazard database, we derive the following categorization of sources of hazard directly from the functional architecture of Figure 3:

Data Communication: This category includes technical hazards sources in the data communication between the ROC and the MASS on a technical level. Examples would be a disturbed and nonredundant communication channel, software failures in the DCM, but also include erroneous sensor data due to perception failures on the MASS.

Human Machine Interface: This category contains technical hazards sources originating in the HMI located in the ROC. Examples include the malfunctioning of displays, software failures related to the user interface, or alarm system failures.

Human Operator: This category consists of hazards originating from the behavior of the human operating the ROC. Included here are errors of commission, errors of omission, lack in skills (e.g. remote operating via a joystick, lacking knowledge of vessel), erroneous interpretation of data, and misuse of the HMI.

Additionally, we argue that the Safety of the Intended Functionality (SOTIF) is relevant for ROC safety and, as a category, complementary to the above. SOTIF covers hazards that are caused by so called functional insuficiencies, i.e. limitations of the technical capabilities and insuficiencies of the specification, including the inability to handle reasonably foreseeable misuse, as well as overall insuficiencies in the HMI design (e.g., too small fonts, too low contrast, cluttering, and information overload). Depending on the type of remote operation, the human operator is responsible for monitoring, direct, strategic or tactical control. As the operator is not on the vessel, all decisions must be derived based on data acquired through some kind of sensor input. Thus, similar to automated drivings systems governed by the ISO 21448 standard [28], it is imperative to ensure that the sensor data and their subsequent processing deliver suficient information to enable, in this case the human operator, to efectively execute their designated tasks.

Viewing our categorization of hazard sources for maritime ROCs through the ISO 21448’s lens, we spot several potential connections. Both, the technical data communication as well as the HMI are considered to be within the scope of SOTIF. Functional insuficiencies concerning the technical communication may include, for example, an inadequate handling of signal dead zones or inference caused by signal jamming. For the HMI, functional insuficiencies may concern the information presented to the HO, e.g., an inadequate warning presented data are outdated. Moreover, in the SOTIF context, the human operator’s behavior is analyzed in terms of direct and indirect misuse. We remark that all these considerations are applicable for maritime ROC safety.

## 4.2 Concept for a Hazard Database

Based on the categorization of hazard sources we provide a first sketch of how a hazard database could support the certification process of a MASS-ROC pair, cf. Figure 4. The Hazard-DB contains

![](images/800cbfd8f772f424cca444ead3bdd1454bd7e886dcd19778b96bd1128c80044a.jpg)  
Fig. 4: Concept for a hazard database supporting the certification process of a MASS-ROC pair.

use cases, exemplified by ’Port Entrance Takeover’, which encompasses generic HARA artifacts rooted in the categories from the functional architecture of Figure 3: Data Communication, Human Machine Interface, Human Operator, and SOTIF. The certification workflow demonstrates a cyclical process beginning with the planning of new MASS-ROC use cases, progressing through system development with an integrated HARA, and culminating in the MASS-ROC certification.

The concept employs a bidirectional knowledge transfer mechanism: it leverages existing database knowledge from previous HARAs to inform current analyses while simultaneously updating the database with insights from ongoing HARA processes, thereby creating a continuous learning framework that enhances the accuracy and comprehensiveness of future risk assessments for MASS-ROC pairs. Once the Hazard-DB underwent the inital set up for a given use case, we can subsequently expect an eficiency increase regarding the future certification processes.

## 4.3 Preliminary Suitability Analysis

In order to grasp which of the HARA methods of section 2 have the potential to support the buildup of a hazard database, cf. Figure 4, we performed a preliminary, expert-based evaluation of their applicability to the three categories of hazard sources plus SOTIF. For each method, we evaluated whether it is applicable for technical hazard sources (i.e., data communication and human machine interface), human hazard sources, and whether SOTIF aspects are addressed appropriately.

Table 4.3 shows the results of this preliminary suitability analysis. A green check mark means that the method supports the category by design, a orange check mark means the method has been extended to this category, and a red cross encodes that the method has not been applied yet. Note that we did not evaluate to what degree the methods (or their extensions) cover these categories.

Tab. 1: Overview which HARA methods address the introduced categories of hazard sources. A green check mark means "supported", an orange check mark means "could be extended to", and a red cross means "not supported".

<table><tr><td></td><td>Data Communication</td><td>Human Machine Interface</td><td>Human Operator</td><td>SOTIF Aspects</td></tr><tr><td>STPA [35]</td><td>✓</td><td>✓</td><td>✓ [18]</td><td>✓[28]</td></tr><tr><td>FMEA [44]</td><td>✓</td><td>✓</td><td>✓ [45]</td><td>✕</td></tr><tr><td>FTA [51]</td><td>✓</td><td>✓</td><td>✓ [4]</td><td>✓ [33]</td></tr><tr><td>ETA [17]</td><td>✓</td><td>✓</td><td>✓ [4]</td><td>✕</td></tr><tr><td>HAZOP [9]</td><td>✓</td><td>✓</td><td>✓ [14]</td><td>✓ [33]</td></tr><tr><td>RBAT [34]</td><td>✓</td><td>✓</td><td>✕</td><td>✓</td></tr><tr><td>Bayesian Networks [40]</td><td>✓</td><td>✓</td><td>✓ [48]</td><td>✓ [20]</td></tr><tr><td>Automation Risks [33]</td><td>✓</td><td>✓</td><td>✕</td><td>✓</td></tr><tr><td>FRAM [24]</td><td>✓</td><td>✓</td><td>✓</td><td>✕</td></tr><tr><td>SHERPA [16]</td><td>✕</td><td>✕</td><td>✓</td><td>✕</td></tr><tr><td>THERP [46]</td><td>✕</td><td>✕</td><td>✓</td><td>✕</td></tr><tr><td>SLIM [2]</td><td>✕</td><td>✕</td><td>✓</td><td>✕</td></tr><tr><td>Petro-HRA [5]</td><td>✕</td><td>✕</td><td>✓</td><td>✕</td></tr><tr><td>APOA [39]</td><td>✕</td><td>✕</td><td>✓</td><td>✕</td></tr><tr><td>CRIOP [22]</td><td>✕</td><td>✕</td><td>✓</td><td>✓</td></tr></table>

Summarizing subsection 4.3, we see an expected divide between methods that natively cover technical hazard and those that were designed for human factors. Therefore, to generate results that densely fill the Hazard-DB, we want to either

(i) choose a universal method with adequate extensions to all categories such as STPA, or

(ii) combine a technical method with a human factors method, e.g., RBAT and FRAM.

Finally, we want to emphasize the integration of SOTIF aspects for all three categories. Neglecting functional insuficiencies or foreseeable misuse, e.g., in the HMI design, can easily lead to accidents during operations.

## 5 Conclusion

In this paper, we laid first steps towards building a hazard database for certification of shore-based ROCs. Based on a generic MASS-ROC functional architecture we derived three diferent categories of hazard sources while identifying SOTIF as a relevant, complementary category. Moreover, we performed a preliminary suitability analysis of HARA methods which may cover these categories.

Regarding future work, conducting a HARA for a concrete shore-based ROC by combining adequate techniques will enable the initial build-up of safety artifacts for the envisioned Hazard-DB.

## References

[1] ASME - American Society of Mechanical Engineers. Risk Management of Autonomous Marine Systems and Operations, volume Volume 3B: Structures, Safety and Reliability of International Conference on Ofshore Mechanics and Arctic Engineering, 06 2017.

[2] Muhammet Aydin, Özkan Uğurlu, and Muhammet Boran. Assessment of human error contribution to maritime pilot transfer operation under HFACS-PV and SLIM approach. Ocean Engineering, 266:112830, 2022

[3] Stefan Babisch, Christian Neurohr, Lukas Westhofen, Stefan Schoenawa, and Henrik Liers. Leveraging the GI-DAS Database for the Criticality Analysis of Automated Driving Systems. Journal of Advanced Transportation, 2023(1):1349269, 2023.

[4] Dustin Birch, Erika Miller, and Thomas Bradley. Human Reliability Analysis using a Human Factors Hazard Model. Journal of System Safety, 58(2):7–29, June 2023.

[5] Claire Blackett, Jan Erik Farbrot, Sondre Øie, and Marius Fernander. The Petro-HRA Guideline Rev.1 Vol. 1. Technical report, IFE - Institute for Energy Technology, 2022.

[6] Eckard Böde, Matthias Büker, Werner Damm, Martin Fränzle, Birte Kramer, Christian Neurohr, and Sebastian Vander Maelen. Identifikation und Quantifizierung von Automationsrisiken für hochautomatisierte Fahrfunktionen. Techni cal report, Insitute for Information Technology (OFFIS e.V.), 2019.

[7] Karlo Bratić, Ivan Pavić, Srđan Vukša, and Ladislav Stazić. A Review of Autonomous and Remotely Controlled Ships in Maritime Sector. Transactions on Maritime Science, 8(02):253–265, 2019.

[8] Shih-Tzung Chen, Alan Wall, Philip Davies, Zaili Yang, Jin Wang, and Yu-Hsin Chou. A Human and Organisational Factors analysis method for marine casualties using HFACS-Maritime Accidents. Safety Science, 60:105–114, 2013.

[9] International Electrotechnical Commission et al. IEC 61882: Hazard and operability studies (HAZOP studies)– Application guide. International Electrotechnical Commission, Geneva, Switzerland, 2001.

[10] DNV. Certification scheme for remote control centre operators. Recommended Practice DNV-RP-0323, 2021.

[11] DNV. Competence of remote control centre operators. Standard DNV-ST-0324, 2022.

[12] DNV. Autonomous and remotely operated ships. Class Guideline DNV-CG-264, 2024.

[13] DNV. Part 6 Additional class notations, Chapter 12 Autonomy and remote operation. Rules for Classification, 2024.

[14] Jordi Dunjó, Vasilis Fthenakis, Juan A. Vílchez, and Josep Arnaldos. Hazard and operability (HAZOP) analysis. A literature review. Journal of Hazardous Materials, 173:19–32, 2010.

[15] Shaymaa MM El-Awady. Overview of failure mode and efects analysis (fmea): a patient safety tool. Global Journal on Quality and Safety in Healthcare, 6(1):24–26, 2023.

[16] David Embrey. SHERPA: A systematic human error reduction and prediction approach. Proceedings of the International Topical Meeting on Advances in Human Factors in Nuclear Power Systems, pages 184–193, 1986.

[17] Clifton A. II Ericson. Event Tree Analysis. In Hazard Analysis Techniques for System Safety, chapter 12, pages 223– 234. John Wiley & Sons, Ltd, 2005.

[18] Megan Elizabeth France. Engineering for humans: A new extension to STPA. PhD thesis, Massachusetts Institute of Technology, 2017.

[19] Carla Galí Debouche et al. Remote Operation Centers for Autonomous Ships. B.Sc. thesis, Universitat Politècnica de Catalunya, 2024.

[20] Roman Gansch, Lina Putze, Tjark Koopmann, Jan Reich, and Christian Neurohr. Causal Bayesian Networks for Data-Driven Safety Analysis of Complex Systems. In Model-Based Safety and Assessment, pages 222–237, Cham, 2026. Springer Nature Switzerland

[21] Georg Hake, Jan Stefen Becker, Anna Austel, Lina Putze, and Nina Wetzig. Safety Assessment of Maritime Autonomous Surface Ships: A Scenario-Based Approach. Journal of Physics: Conference Series, in press

[22] Åsa S. Hoem, Ørnulf J. Rødseth, and Stig Ole Johnsen. Adopting the CRIOP Framework as an Interdisciplinary Risk Analysis Method in the Design of Remote Control Centre for Maritime Autonomous Systems. In Pedro M. Arezes and Ronald L. Boring, editors, Advances in Safety Management and Human Performance, pages 219–227, Cham, 2021. Springer International Publishing.

[23] Erik Hollnagel. Cognitive reliability and error analysis method (CREAM). Elsevier, 1998.

[24] Erik Hollnagel. FRAM: The Functional Resonance Analysis Method: Modelling Complex Socio-Technical Systems. Ashgate Publishing, Farnham, UK, 2012.

[25] International Maritime Organization (IMO). Interim Guidelines for MASS Trials, 2019.

[26] International Maritime Organization (IMO). Maritime Safety Committee - 110th session (MSC 110), 18-27 June 2025, 2025Accessed on.2025-07-30

[27] International Organization for Standardization. ISO 26262: Road vehicles – Functional safety, 2018.

[28] International Organization for Standardization. ISO 21448: Road vehicles – Safety of the intended functionality, 2022.

[29] International Organization for Standardization. ISO/TS 23860: Ships and marine technology — Vocabulary related to autonomous ship systems, 2022

[30] Thomas Jung, Marie-Christin Harre, Noelle Rousselle, Andreas Lüedtke, and Marcel Saager. CMOROC Identifica-

tion of Competences for MASS Operators in Remote Operation Centre. Technical report, European Maritime Safety Agency (EMSA), 2023.

[31] Nesimi Kök and Mehmet Selami Yıldız. New generation fmea method in automotive industry: an application. Journal of Turkish Operations Management, 7(1):1630–1643, 2023.

[32] Tjark Koopmann, Lina Putze, Lukas Westhofen, Roman Gansch, Ahmad Adee, and Christian Neurohr. Grasping Causality for the Explanation of Criticality for Automated Driving. IEEE Access, 13:54739–54756, 2025.

[33] Birte Kramer, Christian Neurohr, Matthias Büker, Eckard Böde, Martin Fränzle, and Werner Damm. Identification and Quantification of Hazardous Scenarios for Automated Driving. In Marc Zeller and Kai Höfig, editors, Model-Based Safety and Assessment, pages 163–178, Cham, 2020. Springer International Publishing.

[34] Kenneth Kvinnesland, Asa Snilstveit Hoem, Sondre Øie, and Remi Brensdal Pederson. RBAT - Method Description. Technical report, European Maritime Safety Agency (EMSA), 2024.

[35] Nancy G. Leveson and John P. Thomas. STPA Handbook. MIT - Massachusetts Institute of Technology, 2018.

[36] Zhihong Li, Di Zhang, Bing Han, and Chengpeng Wan. Risk and reliability analysis for maritime autonomous surface ship: A bibliometric review of literature from 2015 to 2022. Accident Analysis & Prevention, 187:107090, 2023.

[37] Sellappan Narayanagounder and Karuppusami Gurusami. A new approach for prioritization of failure modes in design fmea using anova. World Academy of Science, Engineering and Technology, 49(524-31), 2009

[38] Christian Neurohr, Lukas Westhofen, Martin Butz, Martin Herbert Bollmann, Lina Putze, Tjark Koopmann, Roman Gansch, Michael Knoop, Armin Rasch, Bogdan Cojocaru, and Johannes Daube. Advances on the Criticality Analysis for Automated Driving Systems, February 2024.

[39] Sondre Øie and Marius Fernander. Analysis of Pre-Accident Operator Actions (APOA). DNV, August 2023.

[40] Judea Pearl. Probabilistic Reasoning in Intelligent Systems: Networks of Plausible Inference. Morgan Kaufmann Publishers Inc., San Francisco, CA, USA, 1988.

[41] Judea Pearl. Causality. Cambridge University Press, 2 edition, 2009.

[42] Lina Putze, Lukas Westhofen, Tjark Koopmann, Eckard Böde, and Christian Neurohr. On Quantification for SOTIF Validation of Automated Driving Systems. In 2023 IEEE Intelligent Vehicles Symposium (IV), pages 1–8, 2023.

[43] Marcel Saager, Marie-Christin Harre, and Axel Hahn. Towards Modelling Cooperation in Future Maritime Remote-Control Center. Design for Equality and Justice. INTERACT 2023. Lecture Notes in Computer Science, 2024

[44] SAE International. SAE Standard J1739\_202101 Potential Failure Mode and Efects Analysis (FMEA) Including Design FMEA, Supplemental FMEA-MSR, and Process FMEA, 2021

[45] Wenyan Song, Jing Li, Hao Li, and Xinguo Ming. Human factors risk assessment: An integrated method for improving safety in clinical use of medical devices. Applied Soft Computing, 86:105918, 2020.

[46] Alan David Swain and H.E. Guttmann. Handbook of human reliability analysis with emphasis on nuclear power plan applications. Technical report, Sandia National Labs., Albuquerque, NM (USA), 1983.

[47] Christoph Alexander Thieme, Ingrid Bouwer Utne, and Stein Haugen. Assessing ship risk model applicability to Marine Autonomous Surface Ships. Ocean Engineering, 165:140–154, 2018

[48] Paolo Trucco, Enrico Cagno, Fabrizio Ruggeri, and Oreste Grande. A bayesian belief network modelling of organisational factors in risk analysis: A case study in maritime transportation. Reliability Engineering & System Safety, 93(6):845–856, 2008.

[49] Osiris A. Valdez Banda, Sirpa Kannos, Floris Goerlandt, Pieter H.A.J.M. van Gelder, Martin Bergström, and Pentti Kujala. A systemic hazard analysis and management process for the concept design phase of an autonomous vessel. Reliability Engineering & System Safety, 191:106584, 2019.

[50] Sebastian Vander Maelen, Matthias Büker, Birte Kramer, Eckard Böde, Sebastian Gerwinn, Georg Hake, and Axel Hahn. An Approach for Safety Assessment of Highly Automated Systems Applied to a Maritime Trafic Alert and Collision Avoidance System. In 2019 4th International Conference on System Reliability and Safety (ICSRS), pages 494–503, 2019.

[51] William E Vesely, Francine F Goldberg, Norman H Roberts, and David F Haasl. Fault tree handbook. Technical report, Nuclear Regulatory Commission Washington DC, 1981.

[52] Douglas A Wiegmann and Scott A Shappell. A human error approach to aviation accident analysis: The human factors analysis and classification system. Aviation, Space, and Environmental Medicine, 74(11):1006–1016, 2003.

[53] Krzysztof Wrobel, Przemyslaw Krata, Jakub Montewka, and Tomasz Hinz. Towards the development of a risk model for unmanned vessels design and operations. TransNav, the International Journal on Marine Navigation and Safety of Sea Transportation, 10(2):267–274, 2016.

[54] Krzysztof Wróbel, Jakub Montewka, and Pentti Kujala. System-theoretic approach to safety of remotely-controlled merchant vessel. Ocean Engineering, 152:334–345, 2018

[55] Krzysztof Wróbel, Jakub Montewka, and Pentti Kujala. Towards the development of a system-theoretic model for safety assessment of autonomous merchant vessels. Reliability Engineering & System Safety, 178:209–224, 2018.

[56] M Wylie and E Rajabally. Safety assurance of maritime autonomous surface ships. Journal of Physics: Conference Series, 2867(1):012045, oct 2024.

[57] Xiang-Yu Zhou, Zheng-Jiang Liu, Feng-Wu Wang, Zhao-Lin Wu, and Ren-Da Cui. Towards applicability evaluation of hazard analysis methods for autonomous ships. Ocean Engineering, 214:107773, 2020.

# Authors’ Biographies

![](images/7f31a369ad4f995db9651b7a0d42fe7bc25d9d17171d747f215856ff2b49b851.jpg)

Christian Neurohr received the B.Sc. and M.Sc. in mathematics in 2011 and 2013 from RPTU Kaiserslautern, Germany and his Ph.D. (Dr. rer. nat.) from Carl von Ossietzky Universität Oldenburg, Germany in 2018. After a short period as a visiting researcher at the University of Sydney, he started his occupation as a postdoctoral researcher at the German Aerospace Center (DLR e.V.) Institute of Systems Engineering for Future Mobility where he is working in the area of scenario-based verification and validation of automated vehicles. Since 2023 he leads the ’Criticality Analysis’ team within the division ’Theory and Design’.

![](images/7ac712646cf7f0c112fbd1d7e26a61370fbdb6aa7c0748f8007b41e26cd12e96.jpg)

Marcel Saager received the B.A. in Business and Economics and M.Sc. in Business Information Systems in 2016 and 2019 from Carl von Ossietzky Universität Oldenburg, Germany. After two years as a Modelling- and Software Engineer at Humatects, a company specialized in Human Machine Interaction Solutions, he started his occupation as a doctoral researcher at the German Aerospace Center (DLR e.V.) Institute of Systems Engineering for Future Mobility where he is working in the area of human factors and human centered engineering of highly automated vessels and trains. Furthermore he works and worked as a Lecturer at University of Oldenburg, Private University of Applied Sciences Vechta and University of Applied Sciences in Nuertingen-Geißlingen.

![](images/27eb23c39da2250eb378e1849c9a1f52fa981b167180cd542c1fe1cdf7efb135.jpg)

Lina Putze received the B.Sc. and M.Sc. degrees in mathematics from the University of Münster in 2016 and 2019, specializing on the topics of stochastic processes, probability theory and its applications. She is currently working as a researcher at the group System Concepts and Design Methods at the German Aerospace Center (DLR e.V.) Institute of Systems Engineering for Future Mobility. The focus of her research is on methods to ensure trustworthiness of highly automated transport systems in diferent domains, including the identification and analysis of hazards and risk triggering scenario properties, causal analysis and risk assessment.

![](images/0db62bec4e821cb4e3583ad3cd3f28aa011378883cb3728726d08e5134b1d9f6.jpg)

Jan-Patrick Osterloh received his Diploma in Computer Science in 2005 from the Carl von Ossietzky Universität Oldenburg, Germany, and began his professional career at the Human Centred Engineering Group within the Transportation Division of OFFIS. In the course of a structural reorganization, this division was transferred to the German Aerospace Center (DLR e.V.) and now forms the Institute of Systems Engineering for Future Mobility. As a Senior Research Engineer, his research focuses on human factors and cognitive modelling, particularly human error, perception, workload, and situation awareness in the aeronautics, automotive, and maritime domains. In addition to his work in Human Factors, he

serves as the institute’s Software Engineering Contact, supporting both methodological and technical aspects of software development.

![](images/2629bbf7c9f5ec50b4a424ac165cb2d57e23c8e62733f2d97f9024bc15e007cd.jpg)

Hilko Wiards received his B.Sc. and M.Sc. degrees in Computer Science in 2018 and 2020, respectively, from Carl von Ossietzky Universität Oldenburg, Germany. He began his professional career at the Cooperative Mobile Systems Group within the Transportation division at OFFIS - Institute for Information Technology. Following a structural reorganization, this division was transferred to the German Aerospace Center (DLR e.V.) and now constitutes the Institute of Systems Engineering for Future Mobility. Within the department of Safe Automation Maritime Systems his research focuses on the navigational aspects of autonomous and remotely operated vessels. This includes the evaluation of new sensor systems, fallback procedures and redundancies.

![](images/0a6cce25d2fa61a8402949cfe0d5da4b0e8e9e68b8e4be2f65d33aededf8a759.jpg)

Karina Rothemann received the B.Eng. in mechanical engineering and design and M.Eng. in mechanical engineering from Hochschule Emden/Leer in 2018 and 2020, specializing on the topcis of product and process optimization using AI components. She has worked in the research and development departments of several major automotive companies and starts her carrier in science at the OFFIS-Institut of Computer Science.Currently she works as a researcher at the German Aerospace Center (DLR e.V.) Institute of Systems Engineering for Future Mobility, where she is focusing on the application of hazard and risk analysis methods in the

development process of highly automated systems.

![](images/15562b4c19148058f1c2fe3b1ecaff501c9208111a419eeb533be41a8b202dd0.jpg)

Eckard Böde received his Dipl.-Inform. degree in Computer Science from the Carl von Ossietzky University, Oldenburg, Germany, in 2001. He subsequently joined OFFIS e.V., where he focused on safety assessment and model-based safety analysis for aerospace and automotive applications. In 2012, he was appointed Group Leader for Safety Analysis and Verification. He currently leads the R&D group System Concepts and Design Methods at the German Aerospace Center (DLR e.V.), Institute of Systems Engineering for Future Mobility. His research interests include methods and tools for the design and verification of trustworthy cyber-physical systems, with a particular emphasis on safety assessment of auto-

mated systems and the integration of functional safety with SOTIF in safety cases.

![](images/a0c2519dc1fe4f5e0f219155d66730c8fdb44a35b653b2d589bd3599ef34c5e9.jpg)

Axel Hahn holds a Doctorate in Mechanical Engineering from the University of Paderborn. He currently serves as the Director of the German Aerospace Center (DLR e.V.) Institute of Systems Engineering for Future Mobility, which emerged from the former Transportation Division of OFFIS. In addition, he has a professorship at the Carl von Ossietzky University Oldenburg. His work centers on dependable and intelligent systems in mobility and transport, with a focus on software engineering, system architecture, and safety-critical applications across the automotive, maritime, and aeronautics domains. With a strong interdisciplinary orientation, he bridges research and practical innovation in digitization, automa-

tion, and systems engineering. He has led numerous national and European research projects and actively contributes to shaping future mobility concepts through both technical leadership and strate gic guidance.


---

# 2604.16318_冷启动推荐中LLM重排序诊断

[2604.16318](https://arxiv.org/abs/2604.16318)

# Diagnosing LLM-based Rerankers in Cold-Start Recommender Systems: Coverage, Exposure and Practical Mitigations

Ekaterina Lemdiasova<sup>∗</sup>

V. A. Trapeznikov ICS RAS

Russian Biotechnological University (ROSBIOTECH)

lemdyasova68@gmail.com

Nikita Zmanovskii<sup>∗</sup>

Russian Biotechnological University (ROSBIOTECH)

ORCID: 0009-0004-8917-4900

zmanovskiy.n.v@gmail.com

Abstract—Large language models (LLMs) and cross-encoder rerankers have gained attention for improving recommender systems, particularly in cold-start scenarios where user interaction history is limited. However, practical deployment reveals significant performance gaps between LLM-based approaches and simple baselines. This paper presents a systematic diagnostic study of cross-encoder rerankers in cold-start movie recommendation using the Serendipity-2018 dataset. Through controlled experiments with 500 users across multiple random seeds, we identify three critical failure modes: (1) low retrieval coverage in candidate generation (recall@200 = 0.109 vs. 0.609 for baselines), (2) severe exposure bias with rerankers concentrating recommendations on 3 unique items versus 497 for random baseline, and (3) minimal score discrimination between relevant and irrelevant items (mean difference = 0.098, Cohen’s d = 0.13). We demonstrate that popularity-based ranking substantially outperforms LLM reranking (HR@10: 0.268 vs. 0.008, p < 0.001), with the performance gap primarily attributable to retrieval stage limitations rather than reranker capacity. Based on these findings, we provide actionable recommendations including hybrid retrieval strategies, candidate pool size optimization, and score calibration techniques. All code, configurations, and experimental results are made available for reproducibility.

Index Terms—cold-start recommender systems, reranking, language models, cross-encoders, retrieval diagnostics, evaluation, exposure bias

## I. INTRODUCTION

The cold-start problem remains one of the most persistent challenges in recommender systems research and practice. When new users join a platform with minimal or no interaction history, traditional collaborative filtering methods fail to generate meaningful recommendations. Recent advances in large language models (LLMs) and neural reranking architectures have sparked considerable interest in leveraging these powerful models for cold-start recommendation [1], [2].

Cross-encoder rerankers, such as MS-MARCO models, have demonstrated impressive performance on information retrieval benchmarks by directly scoring query-document pairs through deep attention mechanisms. This capability makes them theoretically attractive for personalized recommendation: given a user profile and item metadata, a cross-encoder could directly assess relevance without requiring historical interaction data. However, translating benchmark success to production-ready cold-start recommender systems presents significant practical challenges.

Despite growing adoption, there exists a critical gap in understanding why and when LLM-based rerankers fail in real-world cold-start scenarios. Existing work often reports aggregate metrics (e.g., Hit Rate, nDCG) but provides limited diagnostic analysis of failure modes. Questions remain unanswered: Is poor performance due to inadequate candidate retrieval, reranker scoring quality, exposure bias, or computational constraints?

This paper addresses these questions through systematic empirical diagnosis of LLM-based reranking in cold-start movie recommendation. Our key contributions are:

• Comprehensive diagnostic framework: We analyze retrieval coverage, exposure distribution, score calibration, and pool-size effects to isolate failure modes of crossencoder rerankers in cold-start settings.

• Empirical evidence of fundamental limitations: Through experiments on Serendipity-2018 dataset with 500 users and multiple random seeds, we demonstrate that simple popularity-based ranking dramatically outperforms sophisticated cross-encoder reranking (HR@10: 0.268 vs. 0.008, 33.5× improvement).

• Root cause identification: We show that the primary bottleneck is retrieval coverage rather than reranker capacity—candidate generation achieves only 10.9% recall@200 compared to 60.9% for baseline methods, fundamentally limiting downstream performance.

• Practical mitigation strategies: Based on diagnostic insights, we provide actionable recommendations including hybrid retrieval (ANN ∪ BM25), candidate pool optimization (smaller pools yield better results), and ensemble scoring approaches.

• Full reproducibility: We release all code, configurations, experimental logs, and per-user results to enable replication and extension of our findings.

Our work challenges the assumption that more sophisticated models necessarily yield better recommendations in cold-start scenarios, and provides a methodological template for rigorous diagnostic evaluation of neural recommender systems.

## II. RELATED WORK

## A. Cold-Start Problem in Recommender Systems

The cold-start problem manifests in three forms: new users (user cold-start), new items (item cold-start), and completely new systems (system cold-start) [3]. User cold-start, which we address in this work, occurs when a recommender system must generate personalized suggestions for users with minimal or no historical interaction data. Traditional approaches include content-based filtering using item metadata, demographicbased recommendations, and hybrid methods combining multiple signals.

Early work on cold-start recommendation focused on utilizing auxiliary information such as user demographics, social network data, or implicit feedback from browsing behavior. However, these approaches require rich side information that may not be available in practice. More recent methods leverage transfer learning, meta-learning, and few-shot learning paradigms to generalize from data-rich to data-scarce scenarios.

## B. Reranking in Recommender Systems

Reranking has become a standard component in modern recommender system pipelines, typically applied as a final stage after candidate retrieval to refine rankings using more sophisticated models [4]. Two-stage retrieve-then-rerank architectures balance efficiency and effectiveness: fast retrieval methods (collaborative filtering, ANN search) generate candidate sets, while expensive reranking models score a small subset.

Cross-encoder architectures, which jointly encode useritem pairs, have shown promise in information retrieval tasks but face scalability challenges when applied to large item catalogs [5]. Unlike bi-encoder models that encode queries and documents independently, cross-encoders use full attention mechanisms to capture fine-grained interactions, achieving superior ranking quality at higher computational cost.

In recommender systems, reranking objectives often extend beyond relevance to incorporate diversity, fairness, and business constraints. Multi-objective reranking frameworks balance multiple goals simultaneously, though this introduces additional complexity in optimization and evaluation.

## C. LLMs for Recommendation and Cold-Start

Recent work has explored using language models to address cold-start challenges through semantic understanding of item metadata and zero-shot reasoning about user preferences [6], [7]. Large language models offer several potential advantages: (1) rich semantic representations from pre-training on web-scale text, (2) ability to perform zero-shot or few-shot reasoning about user-item relevance, (3) natural language interfaces for explainability, and (4) potential to leverage world knowledge for improved recommendations.

ColdRAG [2] proposes using retrieval-augmented generation for cold-start scenarios, combining vector search over item metadata with LLM-based ranking. Language-model priors have been shown to improve cold-start item recommendations by injecting semantic knowledge [6]. Other approaches leverage LLM-generated embeddings, prompting strategies, or finetuning on recommendation-specific tasks.

However, practical deployment reveals challenges. LLM inference costs limit scalability, prompt engineering requires domain expertise, and generalization from general-purpose pre-training to specific recommendation domains remains unclear. Our work provides empirical evidence quantifying these challenges in a controlled cold-start setting.

## D. Diagnostic Analysis and Evaluation Methodologies

While most recommender system papers focus on comparative performance metrics (HR, nDCG, AUC), diagnostic analysis examining why systems succeed or fail remains relatively rare. Calibration studies [8] analyze score distributions and ranking quality. Coverage metrics [9] measure catalog utilization and long-tail item exposure. Exposure fairness research [10] quantifies bias in item visibility across user populations.

Beyond aggregate metrics, recent work emphasizes per-user analysis, error case studies, and failure mode taxonomies. Ablation studies systematically remove components to isolate contributions. Statistical testing with effect sizes provides nuanced understanding beyond p-values. Our diagnostic framework synthesizes these methodologies for comprehensive LLM reranker analysis.

## E. Positioning of This Work

Our work differs from prior art in three ways: (1) systematic diagnostic study rather than incremental performance improvement, (2) focus on failure modes specific to LLMbased rerankers in cold-start settings, and (3) isolation of retrieval, scoring, and exposure issues through controlled ablations with statistical rigor. We provide actionable insights for practitioners deploying neural reranking systems rather than proposing novel architectures.

## III. PROBLEM SETUP AND HYPOTHESES

## A. Task Definition

We address the user cold-start problem in movie recommendation: given a new user with minimal profile information and no historical ratings, generate a ranked list of K=10 movie recommendations. Success is measured by Hit Rate@10 (HR@10) and Normalized Discounted Cumulative Gain@10 (nDCG@10) against held-out ground-truth preferences.

## B. Research Hypotheses

Based on preliminary observations and theoretical considerations, we formulate four hypotheses for systematic testing:

H1 (Retrieval Coverage): Low recall in the candidate retrieval stage fundamentally limits final recommendation quality, regardless of reranker sophistication. We hypothesize that retrieval coverage correlates strongly with HR@10.

H2 (Exposure Bias): Cross-encoder rerankers exhibit severe exposure bias, concentrating recommendations on a small subset of items rather than providing diverse personalized suggestions. We expect to observe significantly fewer unique top-1 items compared to baseline methods.

H3 (Score Calibration): Reranker scores show poor discrimination between relevant and irrelevant items, with minimal statistical separation in score distributions. We hypothesize small effect sizes (Cohen’s d < 0.2) in score differences.

H4 (Pool Size Effect): Larger candidate pools do not necessarily improve reranker performance and may introduce noise. We hypothesize that smaller, focused pools yield better HR@10 than larger pools for cross-encoder reranking.

These hypotheses guide our experimental design and diagnostic analysis in subsequent sections.

## IV. DATASET AND EXPERIMENTAL SETUP

## A. Serendipity-2018 Dataset

We conduct experiments on the Serendipity-2018 dataset, a curated movie recommendation benchmark designed for cold-start evaluation. This dataset was specifically constructed to enable research on serendipitous recommendations—items that are both relevant and pleasantly surprising to users.

Dataset Statistics:

• Catalog size: 49,157 total movies

• Ground truth items: 49,151 movies with user preferences

• Missing GT: 17 movies without preference labels

• Users affected by missing GT: 838 out of 104,661 total users (0.80%)

• Test users: 500 randomly sampled cold-start users

• Random seeds: 3 independent seeds (42, 7, 123) for statistical robustness

Each movie includes structured metadata: title, release year, genres (multiple), user-generated tags, and TMDb/IMDb identifiers. Ground-truth preferences are binary relevance labels derived from explicit user ratings (4+ stars indicating relevance). The dataset intentionally includes obscure and niche movies to test serendipity beyond mainstream popular items.

Data Preprocessing: We construct item profiles by concatenating title, genres, and top-10 most frequent tags. Missing metadata fields are filled with empty strings. Text is tokenized using the SentenceTransformer tokenizer (uncased, max length 128 tokens). No stemming or lemmatization is applied to preserve semantic information.

## B. Detailed Pipeline Architecture

Our experimental pipeline follows a standard two-stage retrieve-then-rerank paradigm. Figure ?? illustrates the complete architecture (referenced but not shown due to space constraints).

1) Stage 1: Item Embedding and Indexing: Embedding Model: We use all-MiniLM-L6-v2, a 22M parameter Sentence-BERT model pre-trained on 1B+ sentence pairs. This model produces 384-dimensional dense vectors optimized for semantic similarity tasks. We chose this model for its balance of quality and efficiency—inference takes ∼0.5ms per item on CPU.

Embedding Generation: All 49,157 movies are encoded offline into dense vectors. Embedding generation takes ∼25 seconds total on CPU (Intel Xeon 2.5GHz). Vectors are L2- normalized for cosine similarity equivalence.

FAISS Indexing: We build a Flat index (exact brute-force search) for reproducibility. While approximate methods (IVF, HNSW) offer speed gains, we use exact search to isolate retrieval quality from approximation errors. Index construction is near-instantaneous for 49K vectors.

2) Stage 2: Candidate Retrieval: Given a cold-start user with minimal profile information, we generate initial candidate sets using one of three strategies:

Random Baseline: Sample K items uniformly at random from the full catalog. Serves as lower-bound sanity check.

Popularity Baseline: Rank all items by global popularity (rating count in training data), return top-K. This simple baseline often outperforms sophisticated methods in cold-start scenarios due to popularity bias in ground truth.

Embedding-Based Retrieval: Encode user profile into query vector, perform FAISS similarity search, return top-K nearest neighbors. User profile is constructed by aggregating embeddings of items from stated preferences or demographic signals.

For our main pipeline (“Candidates Only” and “Ours”), we use embedding-based retrieval with FAISS. We experiment with pool sizes K ∈ {200, 500, 1000} to study coveragequality trade-offs.

3) Stage 3: Cross-Encoder Reranking: Reranker Model: We use cross-encoder/ms-marco-MiniLM-L-6-v2, a 22M parameter model fine-tuned on MS-MARCO passage ranking dataset. The model takes (query, passage) pairs as input and outputs relevance scores via a classification head.

Scoring Procedure: For each user-item pair in the candidate pool, we construct a text input:

[CLS] {user\_profile} [SEP] {item\_title} {item\_genres} {item\_tags} [SEP]

The cross-encoder processes this through 6-layer Transformer (66M parameters total) and outputs a scalar score representing predicted relevance. Inference uses batch processing (batch size 32) on CPU, taking ∼7-9 seconds per user for pool size 1000.

Re-ranking: Candidate items are sorted by descending cross-encoder scores, and top-10 are selected as final recommendations.

4) Implementation Details: Hardware: All experiments run on CPU (Intel Xeon E5-2650 v4 @ 2.20GHz, 128GB RAM). No GPU acceleration is used to reflect resourceconstrained deployment scenarios.

Software: Python 3.9, sentence-transformers 2.2.0, FAISScpu 1.7.4, transformers 4.30.0, PyTorch 2.0.1.

Reproducibility: Fixed random seeds control all stochastic operations (user sampling, random baseline). Complete experimental logs with per-user results are saved in JSONL format for reproducibility.

## C. Baselines and Models

We compare five approaches across three dimensions: retrieval strategy, reranking, and computational cost.

TABLE I  
MODEL CONFIGURATIONS AND COMPUTATIONAL COST

<table><tr><td>Model</td><td>Retrieval</td><td>Reranking</td><td>Time/user (s)</td></tr><tr><td>Random</td><td>Random</td><td>None</td><td>0.01</td></tr><tr><td>Popularity</td><td>Popularity</td><td>None</td><td>0.02</td></tr><tr><td>Embedding Cosine</td><td>FAISS</td><td>None</td><td>0.15</td></tr><tr><td>Candidates Only</td><td>FAISS</td><td>None</td><td>0.15</td></tr><tr><td>Ours (CE Rerank)</td><td>FAISS</td><td>Cross-Enc.</td><td>7.23</td></tr></table>

All models return top-10 recommendations. User sampling, ground-truth labels, and evaluation metrics are identical for fair comparison.

## D. Evaluation Metrics and Statistical Testing

1) Recommendation Quality Metrics: Hit Rate@10 (HR@10): Fraction of users with at least one relevant item in top-10 recommendations. Binary metric emphasizing discovery of any relevant content.

$$
\mathrm{HR} @ 1 0 = \frac {1}{| U |} \sum_ {u \in U} \mathbb {1} [ \exists i \in \operatorname{TopK} (u): i \in \mathrm{GT} (u) ]
$$

Normalized Discounted Cumulative Gain@10 (nDCG@10): Position-aware metric giving higher weight to relevant items ranked earlier.

$$
\mathrm{nDCG@10} = \frac {1}{| U |} \sum_ {u \in U} \frac {\mathrm{DCG@10} (u)}{\mathrm{IDCG@10} (u)}
$$

where DCG accumulates discounted gain: DCG@K = $\textstyle \sum _ { i = 1 } ^ { K } { \frac { 2 ^ { r e l _ { i } } - 1 } { \log _ { 2 } ( i + 1 ) } }$

2) Diagnostic Metrics: Recall@K: Fraction of groundtruth relevant items retrieved in top-K candidates (before reranking). Measures retrieval stage effectiveness.

$$
\text { Recall@K } = \frac {1}{| U |} \sum_ {u \in U} \frac {| \text { TopK } (u) \cap \text { GT } (u) |}{| \text { GT } (u) |}
$$

Unique Top-1 Count: Number of distinct items appearing as rank-1 recommendation across all users. Lower values indicate exposure concentration/bias.

Gini Coefficient: Measures inequality in top-1 item distribution. Values near 1 indicate severe concentration; 0 indicates perfect equality.

Score Statistics: For reranker models, we compute mean and standard deviation of scores separately for relevant vs. irrelevant items, along with t-test statistics.

![](images/24a0164a36bd81b85a2618ea69a966eeedc85b511b68390a978b2d0f0fd1c9e4.jpg)  
Fig. 1. Main Results: HR@10 (left) and nDCG@10 (right) across all models. Popularity baseline dramatically outperforms LLM-based reranker. Error bars show standard deviation across 3 random seeds.

3) Statistical Hypothesis Testing: For each metric comparison, we perform:

Paired t-test: Tests null hypothesis that mean difference between paired samples is zero. Reports t-statistic and p-value.

Wilcoxon signed-rank test: Non-parametric alternative robust to non-normal distributions. Reports W-statistic and $\mathsf { p - }$ value.

Cohen’s d effect size: Standardized mean difference measuring practical significance.

$$
d = \frac {\bar {x} _ {1} - \bar {x} _ {2}}{s _ {\mathrm{pooled}}}
$$

Interpretation: $| \mathrm { d } | < 0 . 2$ (small), 0.2-0.5 (small-medium), 0.5- 0.8 (medium), >0.8 (large).

95% Confidence Interval: Bootstrap CI for mean difference to quantify uncertainty.

All statistical tests use $\alpha = 0 . 0 5$ significance threshold. We report both p-values and effect sizes, following APA guidelines for rigorous statistical reporting.

## V. MAIN RESULTS

Table II presents our primary findings comparing all methods across quality and coverage metrics.

## A. Popularity Dominates LLM Reranking

The most striking finding is the dramatic superiority of simple popularity-based ranking over sophisticated cross-encoder reranking. Popularity achieves HR@10 = 0.268 compared to 0.008 for our LLM-based approach—a 33.5× performance gap. Statistical testing confirms this difference is highly significant (paired t-test: $\mathfrak { t } = - 2 2 . 9 5 , \mathfrak { p } < 1 0 ^ { - 9 9 }$ ; Wilcoxon: $\mathrm { \bf W } = 0 . 0$ $\mathrm { p } < 1 0 ^ { - 8 6 } )$ . The effect size is substantial (Cohen’s d = -0.593, medium-to-large effect).

Even the embedding cosine baseline substantially outperforms LLM reranking (HR@10: 0.101 vs. 0.008), suggesting that semantic similarity alone provides better cold-start recommendations than cross-encoder scoring of retrieved candidates.

Figure 1 visualizes these dramatic performance differences across all models.

## B. Retrieval Coverage is the Primary Bottleneck

The recall metrics reveal a fundamental issue: methods using FAISS candidate generation (Candidates Only, Ours) achieve dramatically lower retrieval coverage:

• Recall@50: 0.041 vs. 0.495 (baseline methods)

• Recall@200: 0.109 vs. 0.609 (5.6× gap)

TABLE II  
MAIN RESULTS: RECOMMENDATION QUALITY AND RETRIEVAL COVERAGE (MEAN ± STD ACROSS 3 SEEDS, 500 USERS EACH)

<table><tr><td>Model</td><td>HR@10</td><td>nDCG@10</td><td>Recall@50</td><td>Recall@200</td><td>Recall@1000</td></tr><tr><td>Random</td><td>0.023 ± 0.002</td><td>0.011 ± 0.000</td><td>0.495 ± 0.013</td><td>0.609 ± 0.016</td><td>0.888 ± 0.016</td></tr><tr><td>Popularity</td><td>0.268 ± 0.018</td><td>0.224 ± 0.014</td><td>0.495 ± 0.013</td><td>0.609 ± 0.016</td><td>0.888 ± 0.016</td></tr><tr><td>Embedding Cosine</td><td>0.101 ± 0.021</td><td>0.050 ± 0.011</td><td>0.495 ± 0.013</td><td>0.609 ± 0.016</td><td>0.888 ± 0.016</td></tr><tr><td>Candidates Only</td><td>0.011 ± 0.003</td><td>0.004 ± 0.001</td><td>0.041 ± 0.009</td><td>0.109 ± 0.016</td><td>0.309 ± 0.029</td></tr><tr><td>Ours (CE Rerank)</td><td>0.008 ± 0.005</td><td>0.005 ± 0.002</td><td>0.041 ± 0.009</td><td>0.109 ± 0.016</td><td>0.309 ± 0.029</td></tr></table>

![](images/a242d2e318b31d231b05df825d4d29430cac9b52bcc0670049ca3229ac9819ce.jpg)  
Fig. 2. Coverage Analysis: Recall@K curves for all methods. FAISSbased retrieval (Candidates Only, Ours) shows dramatically lower coverage compared to baselines that access the full catalog.

## • Recall@1000: 0.309 vs. 0.888 (2.9× gap)

This limited coverage creates a fundamental ceiling on downstream performance. Notably, cross-encoder reranking provides no improvement over "Candidates Only" (HR@10: 0.008 vs. 0.011), indicating that reranker sophistication cannot compensate for poor candidate quality.

Figure 2 visualizes recall@K curves, showing the stark divergence between retrieval strategies.

## C. Statistical Comparison with Best Baseline

Table III presents detailed statistical analysis comparing our approach to the best baseline (Popularity).

TABLE III  
STATISTICAL COMPARISON: OURS VS. POPULARITY (1500 PAIRED SAMPLES)

<table><tr><td>Metric</td><td>HR@10</td><td>nDCG@10</td></tr><tr><td>Mean Difference</td><td>-0.260</td><td>-0.220</td></tr><tr><td>95% CI Lower</td><td>-0.283</td><td>-0.239</td></tr><tr><td>95% CI Upper</td><td>-0.239</td><td>-0.199</td></tr><tr><td>t-statistic</td><td>-22.95</td><td>-21.90</td></tr><tr><td>p-value (t-test)</td><td>3.93e-100</td><td>1.96e-92</td></tr><tr><td>Wilcoxon W</td><td>0.0</td><td>14.0</td></tr><tr><td>p-value (Wilcoxon)</td><td>8.28e-87</td><td>3.34e-70</td></tr><tr><td>Cohen&#x27;s d</td><td>-0.593</td><td>-0.565</td></tr><tr><td>Effect Size</td><td>Medium</td><td>Medium</td></tr></table>

Both parametric (t-test) and non-parametric (Wilcoxon) tests reject the null hypothesis with overwhelming evidence, confirming systematic performance degradation of LLM reranking relative to popularity baseline.

## VI. DIAGNOSTIC ANALYSIS AND ABLATIONS

## A. Coverage Analysis: Retrieval as the Primary Bottleneck

Figure 2 presents detailed recall@K curves for all methods across different pool sizes. The visualization reveals a stark divergence between retrieval strategies that emerges immediately at K=50 and persists across all cutoffs.

Quantitative Analysis: Baseline methods (Random, Popularity, Embedding Cosine) all access the full catalog and achieve recal $\ @ 5 0 ~ = ~ 0 . 4 9 5 .$ , recall $\textcircled { \omega } 2 0 0 ~ = ~ 0 . 6 0 9$ , and recall@ $1 0 0 0 = 0 . 8 8 8$ . These high coverage values result from random sampling across the catalog (Random) or having ground-truth labels distributed across popular and niche items (Popularity).

In contrast, FAISS-based methods (Candidates Only, Ours) show dramatically reduced coverage:

• Recall@50: 0.041 (12.1× lower than baselines)

• Recall@200: 0.109 (5.6× lower)

• Recall@1000: 0.309 (2.9× lower)

Correlation with Final Performance: We compute Pearson correlation between recall@200 and final HR@10 across all model configurations and seeds: $\mathrm { r } = 0 . 8 9 \ ( \mathrm { p } < 0 . 0 0 1 )$ . This strong positive correlation confirms that retrieval coverage is the dominant predictor of downstream recommendation quality. Linear regression yields: $\widehat { \mathrm { H R } } \ @ \widehat { 1 0 } = - 0 . 0 2 3 + 0 . 4 7 8 \times$ Recall@200 with $\mathrm { R } ^ { 2 } = 0 . 7 9$

Ground-Truth Position Analysis: Figure 3 shows the distribution of positions where ground-truth items appear in FAISS-ranked candidate pools. The median position is 6717—far beyond typical retrieval cutoffs of K=200-1000. Only 10.9% of ground-truth items fall within the top-200 candidates returned by FAISS similarity search.

This finding suggests fundamental mismatch between embedding-based similarity (optimized for semantic coherence) and ground-truth relevance (derived from user preferences). Items semantically similar to user profiles do not reliably correspond to items users would actually rate highly.

Implications: The retrieval bottleneck creates a hard ceiling on downstream performance. Even perfect reranking cannot recover relevant items excluded from the candidate pool. Our results show that cross-encoder reranking provides no improvement over "Candidates Only" baseline (HR@10: 0.008 vs. 0.011), confirming that reranker sophistication cannot compensate for poor candidate quality.

![](images/f63fa905137eb66b142238284261679b720ca9f0ae955d15a4dd16fba8531760.jpg)  
Fig. 3. Distribution of ground-truth item positions in FAISS candidate pools. Median position (6717, red line) is far beyond typical retrieval cutoffs, explaining low coverage.

## B. Exposure Bias and Diversity Analysis

1) Top-1 Concentration: Table IV quantifies exposure concentration across methods, revealing severe bias in rerankerbased approaches.

TABLE IV  
EXPOSURE BIAS: TOP-1 ITEM DIVERSITY

<table><tr><td>Model</td><td>Unique Top-1</td><td>Gini Coefficient</td></tr><tr><td>Random</td><td>497.3 ± 0.5</td><td>0.333</td></tr><tr><td>Popularity</td><td>1.0 ± 0.0</td><td>1.000</td></tr><tr><td>Embedding Cosine</td><td>4.0 ± 0.0</td><td>0.261</td></tr><tr><td>Candidates Only</td><td>4.0 ± 0.0</td><td>0.261</td></tr><tr><td>Ours (CE Rerank)</td><td>3.0 ± 0.0</td><td>0.480</td></tr></table>

Cross-encoder reranking exhibits extreme concentration with only 3 unique items appearing as top-1 recommendations across 500 users. Figure 4 provides detailed breakdown:

• Item 175353: 245/500 users (49%)

• Item 63033: 129/500 users (25.8%)

• Item 157603: 126/500 users (25.2%)

This stands in stark contrast to the Random baseline, which distributes top-1 positions across 497 distinct items (Gini = 0.333, near-uniform distribution).

2) Gini Coefficient Analysis: Popularity baseline expectedly shows perfect concentration (Gini = 1.0, single item for all users). However, the sophisticated cross-encoder reranker achieves Gini = 0.480, indicating concentration halfway between uniform and single-item scenarios. This suggests systematic bias in score assignments rather than true personalization.

Embedding Cosine baseline (Gini = 0.261) demonstrates better diversity than our reranker despite lower overall quality (HR@10: 0.101 vs. 0.008). This highlights a fundamental trade-off: embedding similarity provides diverse but sub-optimal recommendations, while cross-encoder scoring achieves higher precision on a narrow subset at the cost of severely reduced coverage and personalization.

![](images/4eccdd0e6b29aff2f5bc5e3dfc5f5d01ed91025863226245f083c90bafa01ad1.jpg)

Fig. 4. Top-1 Exposure: Cross-encoder reranker concentrates recommendations on just 3 items across 500 users. Single item (175353) dominates 50% of users, indicating systematic bias rather than personalization.  
![](images/ec3e3ba4893860b20d84ed6f241ea05f8709632037d7b6fc1b5eee81e88ebdb3.jpg)  
Fig. 5. Item Exposure Distribution: Left shows histogram of exposure counts. Right shows cumulative exposure curve, revealing that 80% of recommendations concentrate on <150 items for reranker-based methods.

3) Long-Tail Item Analysis: Figure 5 shows the cumulative distribution of item exposures across top-10 positions. For our reranker approach, 80% of exposures concentrate on fewer than 30 items (out of 49,157 total catalog). This extreme long-tail distribution indicates failure to surface niche or serendipitous content—a critical limitation for cold-start scenarios where exploration is valuable.

## C. Pool Size Ablation Study: Bigger Is Not Better

We systematically vary candidate pool sizes (200, 500, 1000) while holding all other pipeline components fixed. Table V and Figure 6 present results.

TABLE V  
POOL SIZE ABLATION (MEAN ACROSS 3 SEEDS)

<table><tr><td>Pool Size</td><td>HR@10</td><td>nDCG@10</td><td>Rerank Time (s)</td></tr><tr><td>200</td><td>0.025</td><td>0.009</td><td>1.76</td></tr><tr><td>500</td><td>0.008</td><td>0.005</td><td>4.50</td></tr><tr><td>1000</td><td>0.008</td><td>0.005</td><td>7.23</td></tr></table>

Key Finding: Smaller pools yield superior performance. Pool size 200 achieves HR@10 = 0.025 compared to 0.008 for pools of 500 and 1000—a 3.1× improvement. Similarly, nDCG@10 improves from 0.005 to 0.009 (1.8× gain).

![](images/98fe7982b3a12f6ac181491d4ff3bf30ca146adf8a46f99a16862ec94d29e599.jpg)

![](images/315752eb4a901d6e30ac26d7649a123cf408e1377c6bd01c93ce54d0a4f97da1.jpg)  
Fig. 6. Recall@K vs. Pool Size: Smaller candidate pools (200) achieve better precision in retrieving relevant items compared to larger pools (500, 1000), which introduce more noise.

Hypothesis: Larger candidate pools introduce more noise items that share superficial semantic similarity with user profiles but lack true relevance. The cross-encoder, trained on MS-MARCO passage ranking (a different domain), struggles to discriminate between marginally relevant and irrelevant candidates, leading to false positives dominating top-ranked positions.

Computational Efficiency: Smaller pools also reduce inference cost dramatically. Pool size 200 requires 1.76s per user vs. 7.23s for pool size 1000 (4.1× speedup), making deployment more practical while simultaneously improving quality.

Figure 6 visualizes the recall@K performance across different pool sizes, confirming the counterintuitive finding that smaller pools yield better coverage-quality trade-offs.

Implications: This counterintuitive finding suggests that practitioners should optimize pool size jointly with reranker capacity rather than maximizing coverage indiscriminately. Quality-focused retrieval with smaller, curated candidate sets may outperform quantity-focused approaches.

## D. Score Distribution and Calibration Analysis

1) Statistical Discrimination Testing: We analyze whether cross-encoder scores reliably discriminate between relevant and irrelevant items. Table ?? presents summary statistics across three random seeds (pool size 1000).

Findings:

• Relevant items: Mean score = -4.362 (± 0.720 std)

• Irrelevant items: Mean score = -4.441 (± 0.736 std)

• Mean difference: 0.079 (on log-probability scale)

While paired t-tests confirm statistical significance (p = 0.006-0.028 across seeds), the practical effect is minimal. Cohen’s $\mathrm { ~ d ~ } = ~ 0 . 1 1$ (small effect size, below 0.2 threshold for practical significance). The 95% CI for mean difference is [0.052, 0.106], indicating precision in estimating a small effect.

Fig. 7. Score Distribution Analysis (seed=42): Left shows overlapping histograms of cross-encoder scores for relevant (green) vs. irrelevant (red) items. Right shows scatter plot of scores vs. relevance with Spearman correlation r=0.004, indicating near-zero ranking effectiveness.

Spearman Rank Correlation: We compute rank correlation between raw scores and binary relevance labels: r = 0.003- 0.005 $( \mathtt { p } < 0 . 0 5$ due to large sample size, but correlation near zero). This indicates that while scores show slight tendency to assign higher values to relevant items on average, rank-based discrimination is essentially absent.

2) Score Distribution Visualization: Figure 7 visualizes overlapping histograms of reranker scores for relevant vs. irrelevant items across three seeds. The distributions are nearly identical, with extensive overlap (>95% area overlap). This poor separability explains why reranking fails to improve over unranked candidates.

Out-of-Domain Transfer Hypothesis: The cross-encoder was trained on MS-MARCO, a passage ranking dataset with query-document pairs from web search. The domain mismatch (web passages vs. movie metadata, search intent vs. preference modeling) likely explains poor calibration. Fine-tuning on in-domain movie recommendation data could improve score quality.

## E. Detailed Error Case Analysis

We manually inspect 50 failure cases where our reranker assigned high scores to irrelevant items or low scores to relevant items. Three recurring patterns emerge:

1) Pattern 1: Genre Over-weighting: Example: User profile indicates preference for "psychological thrillers." Reranker ranks generic action movies highly because they contain the word "thriller" in metadata, ignoring the "psychological" modifier.

Frequency: 38% of inspected errors (19/50 cases)

Root cause: Shallow keyword matching rather than semantic understanding. Cross-encoder attention focuses on highfrequency genre terms without capturing nuanced preferences.

2) Pattern 2: Metadata Length Bias: Example: Items with extensive tag lists (10+ tags) systematically receive higher scores regardless of relevance. Short-metadata items (title + 1-2 genres) rank lower even when relevant.

Frequency: 26% of errors (13/50 cases)

Root cause: Cross-encoder scoring may implicitly correlate text length with relevance, as longer passages in MS-MARCO training data often contain more information. This bias transfers inappropriately to movie recommendation.

3) Pattern 3: Popularity Artifacts: Example: Extremely popular movies (>50K ratings) receive inflated scores. Obscure but relevant niche films rank lower.

## Frequency: 22% of errors (11/50 cases)

Root cause: Popular movies accumulate more metadata (tags, reviews) which biases scoring. Additionally, these items may have appeared frequently in cross-encoder’s pre-training data, leading to memorization effects.

4) Remaining Errors: 14% of errors (7/50 cases) show no clear pattern and may result from inherent noise in groundtruth labels or genuine ambiguity in relevance judgments.

## VII. PRACTICAL MITIGATION STRATEGIES

Based on diagnostic findings, we propose concrete mitigations:

## A. Hybrid Retrieval (ANN ∪ BM25)

Combine embedding-based FAISS retrieval with BM25 text matching to improve coverage. Preliminary experiments show recall@200 improves from 0.109 to 0.234 (+114%), translating to HR@10 gains.

## B. Candidate Pool Optimization

Use smaller, focused candidate pools (K=200) rather than large pools (K=1000) for cross-encoder reranking. This reduces computational cost (1.76s vs. 7.23s per user) while improving quality (HR@10: 0.025 vs. 0.008).

## C. Ensemble Scoring

Combine cross-encoder scores with popularity and embedding similarity:

$$
\text { score } _ {\text { final }} = \alpha \cdot \text { CE } _ {\text { score }} + \beta \cdot \log (\text { popularity }) + \gamma \cdot \text { embedding } _ {\text { sim }}
$$

Tuning weights $( \alpha = 0 . 3 , \beta = 0 . 5 , \gamma = 0 . 2 )$ can balance personalization and coverage.

## D. Reranker Calibration

Apply temperature scaling or Platt calibration to reranker scores before ranking. Alternatively, fine-tune cross-encoder on in-domain movie recommendation data rather than using out-of-domain MS-MARCO weights.

## VIII. DISCUSSION

## A. Interpretation of Main Findings

Our comprehensive diagnostic study reveals that sophisticated neural reranking does not automatically translate to improved cold-start recommendations. The failure of crossencoder reranking stems from three compounding factors operating at different pipeline stages.

1) Primary Factor: Retrieval Coverage Bottleneck: The dominant failure mode is insufficient retrieval coverage. FAISS-based embedding similarity search achieves only 10.9% recall@200 compared to 60.9% for baseline methods. This 5.6× gap creates a hard performance ceiling—relevant items not retrieved cannot be recommended, regardless of downstream processing sophistication.

The root cause lies in domain mismatch between embedding model objectives and recommendation relevance. Sentence-BERT models optimize for semantic similarity (paraphrase detection, textual entailment), not preference prediction. An item semantically similar to a user profile may be topically related but preference-irrelevant. For example, a user interested in "psychological thriller" movies receives candidates containing both words but lacking the nuanced psychological depth they seek.

2) Secondary Factor: Score Discrimination Failure: Even within the limited candidate pool, cross-encoder reranking provides no quality improvement (HR@10: 0.008 vs. 0.011 for unranked candidates). Score analysis reveals why: relevant and irrelevant items receive nearly identical scores (mean difference = 0.08, Cohen’s d = 0.11), with near-zero rank correlation (r = 0.004).

This calibration failure results from out-of-domain transfer. MS-MARCO trains cross-encoders on web passage ranking—a task fundamentally different from cold-start movie recommendation. Web search queries have clear information needs; user preferences are multifaceted and contextdependent. Passages contain factual content; movie metadata is sparse and subjective. These domain gaps prevent effective knowledge transfer.

3) Tertiary Factor: Exposure Concentration: Cross-encoder scores exhibit systematic bias toward specific items (3 unique top-1 items across 500 users). This concentration may result from: (1) metadata length bias favoring items with extensive tag lists, (2) genre keyword over-weighting, or (3) memorization of popular items from pre-training data. Regardless of mechanism, the effect is failure to provide personalized recommendations.

## B. Why Popularity Succeeds in Cold-Start Scenarios

The dramatic superiority of popularity-based ranking (HR@10: 0.268 vs. 0.008 for our approach—33.5× gap) deserves explanation. Popularity succeeds in cold-start settings for three reasons:

1. Ground-truth alignment: In movie recommendation, user preferences exhibit strong popularity bias. Relevant items in ground truth tend to be moderately popular rather than obscure. Popularity ranking naturally aligns with this distribution.

2. Robustness to noise: Popularity aggregates signals across many users, providing stable estimates even with limited per-user data. In contrast, embedding-based approaches amplify noise in sparse user profiles.

3. Coverage advantage: Popularity considers all items, while FAISS-based retrieval restricts to a biased subset. Full catalog access provides opportunities to discover relevant items regardless of semantic similarity.

These findings do not imply popularity should replace personalization—rather, they highlight the importance of hybrid approaches combining multiple signals.

## C. Practical Implications for System Design

Our results inform several design decisions for practitioners:

1) Retrieval Strategy Selection: Implication: Invest engineering effort in retrieval quality, not just reranker sophistication. Hybrid retrieval combining multiple signals (embedding similarity, BM25 text matching, collaborative filtering signals) will outperform single-strategy approaches.

Implementation: Use ensemble retrieval pools: ANN (embedding similarity) ∪ BM25 (keyword matching) ∪ Popular-Items(). Deduplicate and re-score the union before reranking.

2) Pool Size Optimization: Implication: Bigger candidate pools do not improve quality for out-of-domain rerankers. Optimize pool size jointly with reranker capacity through validation experiments.

Implementation: Start with small pools (K=100-300) and increase only if validation metrics improve. Monitor both quality (HR@K) and diversity (unique top-K count) simultaneously.

3) Reranker Adaptation: Implication: Out-of-domain cross-encoders require in-domain calibration. Fine-tune on recommendation-specific data or use calibration techniques (temperature scaling, Platt scaling).

Implementation: Collect in-domain clickthrough data or explicit ratings. Fine-tune crossencoder on (user\_profile, item\_metadata, relevance\_label) triples. Use warm-start from MS-MARCO weights, not training from scratch.

## D. Limitations and Scope Conditions

1) Dataset and Domain Specificity: Our experiments focus on movie recommendation using Serendipity-2018 dataset. Generalization to other domains (e-commerce, music, news) requires validation. Domains with richer item metadata (product descriptions, article text) may benefit more from cross-encoder semantic matching. Conversely, domains with stronger collaborative filtering signals may reduce need for content-based approaches.

2) Missing Ground Truth Impact: 17 missing items affecting 838 users (0.80%) introduce slight bias. However, impact is minimal—removing affected users changes mean HR@10 by <0.001. We report results on full test set for transparency.

3) Computational Resource Constraints: All experiments use CPU inference to reflect resource-constrained deployment scenarios. GPU acceleration would reduce reranking time but not address fundamental coverage and calibration issues. Our findings emphasize algorithm design over hardware optimization.

4) Limited Hyperparameter Exploration: We fix embedding model (all-MiniLM-L6-v2) and cross-encoder (msmarco-MiniLM-L-6-v2) to isolate pipeline component effects. Exhaustive architecture search across models and hyperparameters may identify better configurations. However, our goal is diagnostic analysis of standard approaches, not achieving state-of-the-art performance.

## E. Threats to Validity

1) Internal Validity: User sampling: We randomly sample 500 users from 104K total. Stratified sampling by demographic or preference diversity could provide stronger validity. However, random sampling ensures representative results without selection bias.

Seed dependence: We use 3 random seeds (42, 7, 123). Increasing to 10+ seeds would tighten confidence intervals but requires 3× computational budget. Our current approach balances precision and practicality.

2) External Validity: Production environments: Realworld deployments include richer context (device type, timeof-day, session history) potentially improving performance. However, our controlled setting isolates cold-start effects, providing clearer attribution of failure modes.

Evaluation metrics: We focus on HR@10 and nDCG@10. Other objectives (diversity, serendipity, freshness) may change model rankings. Multi-objective evaluation would provide more complete picture.

3) Construct Validity: Ground-truth quality: Binary relevance labels from explicit ratings (4+ stars) simplify true preference distributions. Implicit feedback (watch time, rewatches) may better capture engagement. However, explicit ratings remain standard in recommender systems research.

## F. Relation to Recent Work on LLM Limitations

Our findings align with emerging literature documenting gaps between LLM capabilities and practical deployment:

Calibration issues: Recent work shows LLMs produce poorly calibrated probabilities, requiring post-hoc recalibration [12]. Our score analysis confirms this for recommendation reranking.

Domain transfer challenges: Studies demonstrate that LLM performance degrades on out-of-distribution tasks despite strong in-domain results [13]. MS-MARCO→movie recommendation exemplifies this gap.

Exposure bias in neural models: Research on neural recommendation systems identifies popularity bias and filter bubble effects [14]. Our 3-item concentration finding provides extreme example of this phenomenon.

These connections suggest our diagnostic methodology could apply broadly to LLM-powered systems beyond recommendation.

## IX. CONCLUSION

This paper presents a rigorous diagnostic study of LLMbased cross-encoder rerankers in cold-start movie recommendation, employing controlled experiments on 500 users across multiple random seeds to isolate and quantify failure modes.

## A. Summary of Key Findings

Finding 1 - Popularity dominates sophisticated reranking: Simple popularity-based ranking achieves HR@10 $= ~ 0 . 2 6 8$ , outperforming cross-encoder reranking by 33.5× $( \mathrm { H R } @ 1 0 = 0 . 0 0 8 )$ . Statistical testing confirms overwhelming significance $\mathrm { ( p < 1 0 ^ { - 9 9 } }$ , Cohen’s $\mathrm { d } = - 0 . 5 9 3 )$ ), with 95% CI for mean difference: [-0.283, -0.239].

Finding 2 - Retrieval coverage is the primary bottleneck: FAISS-based candidate generation achieves only recall@200 = 0.109 (vs. 0.609 for baselines—5.6× gap). Strong correlation between retrieval coverage and final quality $( \mathrm { { r } ~ = ~ 0 . 8 9 } _ { }$ p $< ~ 0 . 0 0 1 )$ identifies retrieval as the dominant performance predictor. Median ground-truth position (6717) far exceeds typical cutoffs.

Finding 3 - Reranking provides no improvement over unranked candidates: Cross-encoder reranking yields HR@10 = 0.008 vs. 0.011 for "Candidates Only" baseline (no statistical difference, $\mathrm { ~ p ~ } = \ 0 . 3 1 )$ . This negative result demonstrates that reranker sophistication cannot compensate for poor candidate quality.

Finding 4 - Severe exposure bias limits personalization: Only 3 unique items appear as top-1 recommendations across 500 users $( \mathrm { G i n i } = 0 . 4 8 0 )$ , with single item dominating 50% of users. This extreme concentration indicates systematic bias rather than personalized matching.

Finding 5 - Poor score calibration: Relevant vs. irrelevant items show minimal score discrimination (mean difference = 0.079, Cohen’s d = 0.11, Spearman r = 0.004). Overlapping score distributions (>95% area overlap) explain ranking failure.

Finding 6 - Smaller candidate pools outperform larger pools: Counterintuitively, pool size 200 achieves HR@10 = 0.025 vs. 0.008 for pool 1000 (3.1× improvement), while reducing compute by 4.1× (1.76s vs. 7.23s per user). Larger pools introduce more noise, degrading discrimination.

## B. Practical Recommendations for Practitioners

Based on diagnostic insights, we recommend four concrete mitigation strategies:

1. Hybrid Retrieval (ANN ∪ BM25): Combine embedding-based FAISS retrieval with BM25 text matching to improve coverage. Preliminary experiments show recall@200 improvement from 0.109 to 0.234 (+114%), translating to downstream HR@10 gains. Implementation: merge candidate pools from multiple retrievers before reranking.

2. Candidate Pool Size Optimization: Tune pool size via validation experiments rather than maximizing coverage indiscriminately. Start with K=200 and increase only if metrics improve. Monitor quality-diversity trade-off (HR@K vs. unique top-K count).

3. Ensemble Scoring: Combine cross-encoder scores with popularity and embedding similarity via weighted ensemble:

$\operatorname { s c o r e } _ { \mathrm { f i n a l } } = \alpha \cdot \operatorname { C E } _ { \mathrm { s c o r e } } + \beta \cdot \log ( \operatorname { p o p u l a r i t y } ) + \gamma \cdot \operatorname { e m b e d d i n g } _ { \mathrm { s i m } }$ Tune weights $( \alpha = 0 . 3 , \beta = 0 . 5 , \gamma = 0 . 2$ as starting point) on validation set. Balances personalization and robustness.

4. In-Domain Reranker Calibration: Fine-tune crossencoders on recommendation-specific data rather than using out-of-domain weights. Collect (user\_profile, item, label) triples from clicks or ratings. Alternatively, apply post-hoc calibration (temperature scaling, Platt calibration) to rescale scores.

## C. Methodological Contributions

Beyond empirical findings, this work provides methodological template for diagnostic evaluation of neural recommender systems:

Multi-faceted diagnostic framework: Coverage analysis (recall@K curves, GT position distributions), exposure metrics (unique top-K, Gini, concentration), score calibration (relevant vs. irrelevant distributions, rank correlation), and ablations (pool size, pipeline stages).

Statistical rigor: Paired testing with both parametric (t-test) and non-parametric (Wilcoxon) methods, effect sizes (Cohen’s d), confidence intervals, multiple comparison correction, and sensitivity analysis across random seeds.

Error case taxonomy: Systematic classification of failure modes (genre mismatch, metadata bias, popularity artifacts) to guide algorithmic improvements beyond aggregate metrics.

Reproducibility standards: Release of complete experimental logs, per-user results, master JSON configurations, and executable code to enable replication and extension.

## D. Future Research Directions

Key open questions for future investigation:

1. Hybrid Retrieval Architectures: Systematic study of retrieval ensemble strategies (ANN + BM25 + collaborative signals + graph-based methods) with learned fusion weights. Develop adaptive retrieval that selects strategies per-user based on profile characteristics.

2. In-Domain Cross-Encoder Training: Fine-tune crossencoders on recommendation-specific datasets (e.g., Amazon Reviews, MovieLens-20M) using contrastive learning or listwise ranking losses. Compare zero-shot MS-MARCO weights vs. fine-tuned variants.

3. Uncertainty-Aware Reranking: Incorporate prediction uncertainty into ranking decisions. Low-confidence scores should trigger exploration (diversity promotion) rather than exploitation. Develop calibrated confidence estimates for coldstart scenarios.

4. Exposure Fairness Interventions: Design reranking objectives that explicitly optimize for exposure diversity alongside relevance. Apply calibration techniques from fairness literature to reduce concentration bias.

5. Multi-Domain Generalization: Replicate diagnostic analysis on e-commerce (Amazon), music (LastFM), news (MIND), and social media datasets. Identify domain-invariant vs. domain-specific failure modes.

6. Online A/B Testing: Validate offline findings through online experiments with real users. Measure engagement (clickthrough rate, dwell time) and business metrics (conversion, retention) beyond offline accuracy.

## E. Broader Impact and Ethical Considerations

Our findings have implications beyond technical performance:

Filter bubble concerns: Extreme exposure concentration (3 items for 500 users) exacerbates filter bubble effects, limiting user exposure to diverse content. Systems deployed at scale could amplify these biases, reducing information diversity.

Popularity bias amplification: Our results show popularity-based ranking outperforming personalized approaches in cold-start settings. While pragmatic, this risks creating "rich-get-richer" dynamics where popular items dominate, starving long-tail content.

Computational sustainability: Cross-encoder reranking consumes 7.23s per user (vs. 0.02s for popularity), raising energy costs for marginal (often negative) quality impact. Practitioners should consider computational efficiency alongside accuracy.

Transparency in evaluation: Publication of full diagnostic breakdowns (not just aggregate metrics) enables more informed deployment decisions and sets standards for responsible AI development.

## F. Closing Remarks

This work challenges the assumption that more sophisticated models automatically yield better recommendations in cold-start scenarios. Through systematic diagnosis, we demonstrate that simple baselines can dramatically outperform complex neural approaches when pipeline components (retrieval, scoring, calibration) are misaligned.

The path forward requires: (1) engineering investment in hybrid retrieval combining multiple signals, (2) careful pool size optimization balancing coverage and noise, (3) in-domain adaptation of reranking models, and (4) ensemble approaches integrating learned and heuristic components.

We hope our diagnostic methodology—emphasizing failure mode analysis, statistical rigor, and full reproducibility—serves as template for evaluating neural recommendation systems and motivates future work toward more robust, fair, and efficient cold-start solutions.

\* These authors contributed equally to this work.

## ACKNOWLEDGMENTS

We thank the anonymous reviewers for constructive feedback. This research was conducted using open datasets and publicly available models to ensure reproducibility. Code, data, and experimental logs are available at the GitHub repository referenced in the Data and Code Availability section.

## DATA AND CODE AVAILABILITY

All code, configurations, and experimental results are publicly available to enable full reproducibility:

• Repository: https://github.com/nikita-zmanovskiy/ cold-start-algorithm

• Dataset: Serendipity-2018 (publicly available)

• Models: sentence-transformers/all-MiniLM-L6-v2, cross-encoder/ms-marco-MiniLM-L-6-v2 (Hugging Face)

• Experimental logs: Per-user results, master JSON files in repository

## Reproducing Results

To replicate our experiments, follow these steps (detailed instructions in README.md):

```txt
# 1. Setup environment
pip install -r requirements.txt
```

```txt
# 2. Run main experiments
python -m src.run_all_experiments \
--n-users 500 --seeds 42 7 123
```

```shell
# 3. Pool size ablation study
python -m src.run_ablation_pool_sizes \
--pool-sizes 200 500 1000
```

```shell
# 4. Aggregate results
python -m tools.build_master_results
python -m tools.aggregate_runs
```

```shell
# 5. Statistical analysis
python -m tools.hypothesis_analysis
python -m tools.analyze_scores
python -m tools.error_analysis
python -m tools.enhanced_stat_tests
```

```shell
# 6. Generate visualizations
python -m tools.plotting
python -m tools.advanced_plotting
```

```markdown
# 7. Generate paper tables
python -m tools.generate_paper_tables
```

Complete documentation is available in the repository README.md file.

## REFERENCES

[1] Y. Wang et al., “Large Language Models for Recommender Systems: A Survey,” arXiv preprint arXiv:2305.19860, 2023.

[2] L. Chen et al., “ColdRAG: Retrieval-Augmented Generation for Cold-Start Recommendation,” arXiv preprint arXiv:2410.12345, 2024.

[3] A. M. Rashid et al., “Getting to Know You: Learning New User Preferences in Recommender Systems,” in Proc. ACM IUI, 2002, pp. 127-134.

[4] Z. Liu et al., “Neural Reranking for Information Retrieval: A Survey,” ACM Computing Surveys, vol. 55, no. 6, pp. 1-35, 2022.

[5] T. Bajaj et al., “MS MARCO: A Human Generated Machine Reading Comprehension Dataset,” NeurIPS Datasets Track, 2016.

[6] K. Zhang et al., “Language-Model Prior Overcomes Cold-Start Items,” arXiv preprint arXiv:2411.09065, 2024.

[7] M. Johnson et al., “Adaptive Candidate Retrieval with Dynamic Knowledge Graph Construction for Cold-Start Recommendation,” arXiv preprint arXiv:2505.20773, 2025.

[8] H. Steck, “Calibrated Recommendations,” in Proc. ACM RecSys, 2018, pp. 154-162.

[9] G. Shani and A. Gunawardana, “Evaluating Recommendation Systems,” in Recommender Systems Handbook, Springer, 2011, pp. 257-297.

[10] A. Singh and T. Joachims, “Fairness of Exposure in Rankings,” in Proc. ACM SIGKDD, 2018, pp. 2219-2228.

[11] Y. Liu et al., “Exploring the Potential of LLMs for Serendipity Evaluation in Recommender Systems,” arXiv preprint arXiv:2507.17290, 2025.

[12] S. Kumar et al., “Calibration of Large Language Models: A Survey,” arXiv preprint arXiv:2308.10144, 2023.

[13] P. Liu et al., “Out-of-Distribution Robustness of Large Language Models,” in Proc. NeurIPS, 2023, pp. 15420-15433.

[14] J. Chen et al., “Bias and Debias in Recommender Systems: A Survey and Future Directions,” ACM Trans. Inf. Syst., vol. 41, no. 3, pp. 1-39, 2023.

[15] R. Burke, “Hybrid Recommender Systems: Survey and Experiments,” User Modeling and User-Adapted Interaction, vol. 12, no. 4, pp. 331- 370, 2002.

[16] J. Johnson et al., “Billion-scale Similarity Search with GPUs,” IEEE Trans. Big Data, vol. 7, no. 3, pp. 535-547, 2021.

[17] N. Reimers and I. Gurevych, “Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks,” in Proc. EMNLP-IJCNLP, 2019, pp. 3982-3992.

[18] V. Karpukhin et al., “Dense Passage Retrieval for Open-Domain Question Answering,” in Proc. EMNLP, 2020, pp. 6769-6781.

[19] C. W. Kofod-Petersen and M. M. Aamodt, “Evaluation of Recommender Systems: A Framework,” in Proc. ICCBR Workshops, 2009.

[20] B. Lika et al., “Facing the Cold Start Problem in Recommender Systems,” Expert Systems with Applications, vol. 41, no. 4, pp. 2065- 2073, 2014.


---

# 2606.22151_Novelty-Aware_Agentic_Retrieval_Structured_Multi-Step_Reasoning

[2606.22151](https://arxiv.org/abs/2606.22151)

# Novelty-Aware Agentic Retrieval: Comparing Research Contributions Through Structured Multi-Step Reasoning

Shou-Tzu Han

Department of Computer Science

University of South Dakota

Vermillion, South Dakota, USA

shoutzu.han@coyotes.usd.edu

## Abstract

Scientific literature search is an information retrieval (IR) task in which ranked lists are insuficient: a researcher entering a new area needs to know not only which papers are relevant, but how they relate: where they overlap, how they difer, and what problem– method combinations are absent. Standard retrieval-augmented generation (RAG) summarizes documents independently, discard ing exactly this comparative signal. We present the Novelty-Aware Research Agent, a prototype agentic retrieval system that layers structured multi-step reasoning on a RAG pipeline through six typed-contract components: query analysis, a ReAct-style retrieval loop, relevance ranking, schema-guided contribution extraction, a three-pass comparison agent, and answer generation. Beyond returning relevant papers, it produces structured comparison ar tifacts: per-paper contribution records, paper-level overlaps, and a problem × method gap matrix. On a 100-paper corpus, our cen tral result is that the system supports five structured comparison capabilities that a standard RAG baseline supports none of, while remaining query-sensitive. Across the three main queries, no pa per appears in all three top-5 sets and the mean pairwise Jaccard similarity is 0.12; in an extended seven-query evaluation, the same pattern holds across ten total queries, with mean pairwise Jaccard similarity of 0.115 and 18 of 29 distinct retrieved papers appearing in only one query. Under author-assigned graded relevance, the ranker attains mean Precision@5 of 1.000 and nDCG@5 of 0.752 on the three main queries, ahead of BM25, dense, and hybrid retrieval; over all ten queries, Precision@5 remains high but non-saturated at 0.980, with nDCG@5 of 0.739. Schema compliance is 86.7% on the main queries and 84.0% over the ten-query set, and a validation of 20 sampled empty gap-matrix cells yields gap precision of 0.600. We discuss the latency–structure trade-of inherent to agentic retrieval and identify corpus scale, author-assigned relevance labels, and limited independent evaluation as the primary limitations of the prototype.

## CCS Concepts

• Information systems → Information retrieval; Retrieval models and ranking; • Computing methodologies → Artificial intelligence.

## Keywords

agentic information retrieval, retrieval-augmented generation, Re-Act, constrained decoding, scientific literature search, contribution comparison, corpus-level gap analysis, LLM agents

## 1 Introduction

The integration of large language model (LLM) agents into information retrieval has reshaped how users find and consume information. Agentic retrieval systems, those combining tool use, memory, reasoning, and planning, can decompose queries, retrieve evidence, and synthesize responses in ways that go beyond returning a ranked list of documents. Yet for one common and important IR task, scientific literature search, even agentic systems tend to fall back on a familiar pattern: retrieve relevant documents, then summarize each one independently.

This pattern is inadequate for the underlying user need. A researcher entering a new area does not primarily want a list of papers or a set of disconnected summaries. They want to understand the structure of a body of work: which papers address the same problem, which propose genuinely diferent methods, and crucially, what problem–method combinations have not yet been explored. These are comparative and corpus-level questions. A retrieval system that summarizes documents independently discards exactly the signal needed to answer them. Concretely, the payof of answering them is that a researcher can see, in one structured view, which retrieved papers converge and which problem–method combinations remain open, rather than reconstructing that map by reading and cross-referencing a ranked list by hand.

We frame this as a novelty-aware retrieval problem and present the Novelty-Aware Research Agent, a prototype agentic retrieval system that layers structured comparison reasoning on top of a retrieval-augmented generation (RAG) pipeline. Rather than asking “what does this paper say?” the system asks “what does this retrieved set collectively cover, where does it converge, and what is absent?”

The system retrieves papers from a domain corpus, ranks them by query relevance, extracts a structured contribution record for each, and then runs a dedicated comparison stage that identifies overlaps, diferentiating aspects, and a problem × method gap matrix. The final output is not a single prose summary but a set of typed, auditable artifacts that a user (or a downstream system) can inspect and act on.

Contributions.

(1) A six-component agentic retrieval pipeline with typed intercomponent contracts, combining a ReAct-style retrieval loop, relevance ranking, schema-guided extraction, and a multi-pass comparison stage.

(2) A three-pass Comparison Agent that operates on structured contribution records rather than raw retrieved text, producing paper-level overlaps, per-paper diferentiation, and a deterministic problem × method gap matrix.

(3) An evaluation on a 100-paper agentic AI and retrieval corpus, including query-sensitivity analysis, graded-relevance retrieval metrics (Precision@5, nDCG@5, Recall@5, MRR), schema-compliance failure analysis, a ReAct sparse-query stress test, deterministic gap-matrix construction, a base line comparison, BM25/dense/hybrid retriever comparison, component ablation, deterministic gap validation, gap error analysis, a qualitative case study, an indicative single-rater external usefulness assessment collected on an earlier sys tem version, and an extended seven-query evaluation.

(4) A working open-source prototype implementation with a web interface that streams the six-stage retrieval process in real time.<sup>1</sup>

We position this as a prototype system paper. The contribution is the retrieval architecture and the comparison artifacts it produces, not a large-scale benchmark; we are explicit throughout about the scale and evaluation limitations of the current corpus.

## 2 Related Work

Agentic IR and RAG. LLM agents extend retrieval beyond single shot ranking through query decomposition, iterative search, and tool use. Multi-agent frameworks such as AutoGen [4] and MetaGPT [5] coordinate agents for complex tasks, AgentBench [8] evaluates agent behavior across environments, and a recent survey [12] reviews agent architectures. These establish the agentic paradigm but do not target the IR task of comparing retrieved documents at the level of their contributions. Our system builds on retrievalaugmented generation (RAG) [1], including its adaptive and self critical variants Self-RAG [10] and corrective retrieval [11], using FAISS exact nearest-neighbor search as a substrate. It departs from typical RAG output: where standard RAG concatenates passages into one response, our system retains each retrieved paper as a dis tinct unit, extracts a structured record, and reasons across records.

Reformulation, structured extraction, and comparison. Ef fective retrieval often depends on reformulating the query. ReAct [2] interleaves reasoning and action in a Thought → Action → Observation loop; we apply this at the retrieval stage, placing refor mulation under explicit agent control rather than a single fixed embedding. JSON schema-guided decoding [3] constrains genera tion to structurally valid output; we use it to extract a fixed four-field contribution record per paper, so downstream comparison operates over uniform inputs. Chain-of-thought prompting [13] and deploy ment platforms such as OpenAgents [14] are adjacent reasoning and agent-deployment work covered by our corpus. We are not aware of prior agentic retrieval systems that combine structured contribution extraction, cross-paper comparison, and deterministic problem–method gap-matrix construction in a single literaturecomparison pipeline. Table 1 positions our system relative to repre sentative prior work across five capability dimensions.

Automated literature review and gap analysis. A parallel line of work automates systematic literature reviews (SLRs) with LLM agents. Sami et al. [21] propose a multi-agent system that automates the full SLR workflow, including agents that retrieve, fil ter, and summarize papers and surface trends and gaps, and Moses et al. [22] introduce a gap-aware agentic workflow that combines structured synthesis, knowledge-graph modeling, and perspectiveguided questioning to identify gaps in coverage, reasoning, or evidence through graph traversal and contrastive retrieval. Our system shares the multi-agent and gap-surfacing motivation but difers in target and mechanism: rather than generating a written review narrative, it treats the retrieved set as structured data and constructs a deterministic problem × method gap matrix over typed contribution records, so that the gap decision is a reproducible structural computation rather than generated text.

```txt
Algorithm 1 Novelty-Aware Agentic Retrieval
Require: query q, corpus C, min-papers k, top-n N
Ensure: structured comparison report R
1: Q ← QUERYANALYZER(q) ▷ T=0.3
2: iter ← 0
3: while iter < 3 do
4:    P ← FAISS.SEARCH(Q.queries iter],C)
5:    if |UNIQUE(P)| ≥ k then
6:    break ▷ ReAct STOP
7:    end if
8:    q' ← LLM.REASON(q,P) ▷ ReAct REFINE
9:    Q.queries.APPEND(q');iter++
10: end while
11: Pn ← RANKER(P,q,N) ▷ T=0.1
12: E ← EXTRACTOR(Pn) ▷ schema; T=0.1
13: O ← OVERLAPPASS(E) ▷ T=0.2
14: D ← DIFFERENTIATIONPASS(E) ▷ T=0.2
15: G ← GAPMATRIX(E) ▷ deterministic
16: R ← ANSWERGENERATOR(q,E,O,D,G) ▷ T=0.7
17: return R
```

## 3 System Architecture

The system comprises six components arranged in a sequential agentic retrieval pipeline with defined input/output contracts. Figure 1 shows the data flow and Algorithm 1 formalizes the procedure. Lines 3–10 implement the ReAct retrieval loop; lines 13–15 implement the three comparison passes.

## 3.1 Query Analyzer

The entry point decomposes the user query into focused retrieval intents and 2–4 reformulated queries, operating at temperature <sup>??</sup> =0<sup>.</sup>3 under JSON schema constraints. Reformulation is included to support sparse or underspecified retrieval settings, with a modest measurable benefit on the present 100-paper corpus (Section 5).

## 3.2 Retriever (ReAct Loop)

The retriever performs FAISS IndexFlatL2 search over sentencetransformer embeddings with ReAct-style refinement. If fewer than three unique papers meet an L2 <sup><</sup> 400 distance threshold, the agent emits a Thought explaining the shortfall and an Action query reformulation, retrying up to three iterations. In the main broadquery experiments retrieval succeeded in one iteration on every run. We therefore additionally conduct a sparse-query stress test (Section 5.7), in which the loop activates on three of five strictthreshold queries and recovers suficient coverage in one of the three triggered cases.

Table 1: Positioning of the proposed system relative to representative prior work.

<table><tr><td>System / Work</td><td>RAG</td><td>Agent Loop</td><td>Structured Extraction</td><td>Cross-Paper Comparison</td><td>Problem-Method Gap Matrix</td></tr><tr><td>RAG [1]</td><td>Yes</td><td>No</td><td>No</td><td>No</td><td>No</td></tr><tr><td>ReAct [2]</td><td>Tool-dep.</td><td>Yes</td><td>No</td><td>No</td><td>No</td></tr><tr><td>Self-RAG [10]</td><td>Yes</td><td>Yes</td><td>No</td><td>No</td><td>No</td></tr><tr><td>AutoGen [4]</td><td>No</td><td>Yes</td><td>No</td><td>No</td><td>No</td></tr><tr><td>MetaGPT [5]</td><td>No</td><td>Yes</td><td>No</td><td>No</td><td>No</td></tr><tr><td>AgentBench [8]</td><td>No</td><td>No</td><td>No</td><td>No</td><td>No</td></tr><tr><td>SLR multi-agent systems [21]</td><td>Yes</td><td>Yes</td><td>Partial</td><td>Yes</td><td>No</td></tr><tr><td>Gap-aware workflows [22]</td><td>Yes</td><td>Yes</td><td>Yes</td><td>Yes</td><td>Partial</td></tr><tr><td>Novelty-Aware Research Agent (ours)</td><td>Yes</td><td>Yes</td><td>Yes</td><td>Yes</td><td>Yes</td></tr></table>

![](images/4bf4dfdf915f70ed14a1afb471a156f7f7acf5cc5f1c631f05dc56b1289e65fd.jpg)  
Figure 1: End-to-end agentic retrieval pipeline. A user query is decomposed and reformulated, candidate papers are retrieved and ranked, structured contribution records are extracted under a schema, three comparison passes produce overlaps / diferentiation / a gap matrix, and a final citation-grounded report is generated.

## 3.3 Ranker

The ranker scores each retrieved candidate for query relevance at <sup>??</sup> =0<sup>.</sup>1 and returns the top-<sup>??</sup> . Low temperature yields consis tent, near-deterministic scoring. As Section 5 shows, the ranker selects substantially diferent paper sets across queries, evidence that scoring is query-sensitive rather than returning a fixed corpus ordering.

## 3.4 Contribution Extractor

For each top-ranked paper, schema-guided decoding enforces a four field record: Problem Statement, Proposed Method, Key Contribution, and Claimed Novelty, at <sup>??</sup> =0<sup>.</sup>1. We define schema compliance as the fraction of papers for which all four fields are non-empty and non-placeholder. Structural validity is guaranteed by decoding; field completeness depends on the input paper, which is why compliance can fall below 100% for atypically structured papers.

## 3.5 Comparison Agent

The comparison agent is the core contribution and operates on structured records rather than raw retrieved text, which bounds the reasoning space and makes outputs auditable. It runs three sequential passes:

• Overlap Pass. Identifies papers sharing the same problem formulation, dataset, or method family, returning paper identifiers with a shared-element label.

• Diferentiation Pass. Identifies what each paper does distinctly in method, scope, or claimed contribution.

• Gap Pass. Maps retrieved paper identifiers to canonical problem and method labels using a fixed taxonomy; the final problem × method matrix is constructed deterministically, and empty cells are reported as candidate corpus-level gaps within the retrieved paper slice (Section 5.8).

## 3.6 Answer Generator

The final stage synthesizes a report at <sup>??</sup> =0<sup>.</sup>7, producing per-paper summaries, a synthesis paragraph, and a citation-grounded refer ence list. Higher temperature here favors readable natural-language synthesis, in contrast to the precision-oriented extraction and ranking stages.

## 4 Implementation

## 4.1 Technology Stack

The system is implemented in Python 3.9 using the OpenAI API [15], with GPT-4o as the primary backbone for the main experiments and GPT-4o-mini and GPT-4.1 used in the cross-model robustness analysis (Section 5.14). The system uses FAISS IndexFlatL2 for exact nearest-neighbor retrieval, Sentence-Transformers (all-MiniLM-L6- v2, 384-dimensional embeddings) for encoding, and Pydantic v2 for typed inter-component contracts. A FastAPI backend streams the six-stage retrieval process to a web interface using server-sent events, allowing users to observe each stage complete in real time.

## 4.2 Corpus

The evaluation corpus contains 100 papers spanning the agentic AI and retrieval domain: multi-agent frameworks, reasoning tech niques, tool-use systems, agent deployment platforms, evaluation and survey work, and a substantial set of retrieval-augmented gen eration papers. Representative papers include Self-RAG [10], Reflexion [7], CAMEL [6], Generative Agents [9], AgentVerse [16], ReWOO [17], and MetaAgents [18]. Each paper is chunked into ab stract, introduction, and conclusion sections, producing 300 FAISS vectors. The corpus defines the system’s entire search space; the system does not retrieve from the open web.

## 4.3 Temperature Configuration

Temperature is assigned per component following standard practice: low values for precision-critical stages (ranking and extraction at <sup>??</sup> =0<sup>.</sup>1, comparison at <sup>??</sup> =0<sup>.</sup>2), moderate values for query analysis and ReAct reasoning (<sup>??</sup> =0<sup>.</sup>3), deterministic construction for the gap matrix, and a higher value (<sup>??</sup> =0<sup>.</sup>7) for natural-language synthesis.

## 5 Experiments and Results

We evaluate using (a) automated retrieval and compliance metrics, (b) graded-relevance retrieval quality (Precision@5, nDCG@5, Re call@5, MRR), (c) schema failure analysis, (d) query-sensitivity anal ysis, (e) a ReAct sparse-query stress test, (f) deterministic gap-matrix construction, (g) a baseline comparison, (h) BM25/dense/hybrid re triever comparison, (i) component ablation, (j) deterministic gap validation, (k) gap error analysis, (l) a qualitative case study, (m) an indicative single-rater external usefulness assessment collected on an earlier system version, and (n) an extended seven-query evaluation. Three main runs were executed with distinct broad comparison queries on the expanded 100-paper corpus:

• R1: “Compare multi-agent LLM frameworks for collaborative reasoning”

• R2: “What evaluation methods exist for LLM reasoning agents?”

Table 2: Automated metrics across three runs (100-paper corpus).

<table><tr><td>Metric</td><td>R1</td><td>R2</td><td>R3</td><td>Avg</td></tr><tr><td>Corpus size</td><td>100</td><td>100</td><td>100</td><td>100</td></tr><tr><td>Candidates retrieved</td><td>9</td><td>10</td><td>9</td><td>9.3</td></tr><tr><td>ReAct iterations</td><td>1</td><td>1</td><td>1</td><td>1.0</td></tr><tr><td>Schema compliance</td><td>80%</td><td>80%</td><td>100%</td><td>86.7%</td></tr><tr><td>Overlaps detected</td><td>3</td><td>3</td><td>2</td><td>2.7</td></tr><tr><td>Differences</td><td>5</td><td>5</td><td>5</td><td>5.0</td></tr><tr><td>Gaps identified</td><td>5</td><td>4</td><td>5</td><td>4.7</td></tr><tr><td>Runtime (s)</td><td>22.3</td><td>23.5</td><td>22.9</td><td>22.9</td></tr></table>

• R3: “Compare verbal reinforcement and role-playing approaches in LLM agents”

Unless otherwise stated, the main tables report these three primary runs. We additionally report an extended seven-query evaluation (R4–R10) in Section 5.15 to test whether the retrieval behavior remains stable across a wider query set.

## 5.1 Automated Metrics

Table 2 reports automated metrics. Retrieval returns nine to ten candidates per query in these runs; the ranker reduces them to a top-5 set. Schema compliance averages 86.7%, and the comparison agent produces 2–3 overlaps and 4–5 report-level gaps per run. End-to-end latency averages 23 seconds.

## 5.2 Query-Sensitive Retrieval

The central retrieval result is that the ranker selects substantially diferent paper sets across queries (Table 3). No paper appears in all three top-5 result sets. Across the 15 ranked slots the system retrieves 12 distinct papers, 9 of which (75%) are query-exclusive, appearing in only a single run. The mean pairwise Jaccard similarity across the three top-5 sets is 0.12, indicating the retrieved sets are roughly 88% distinct on average; runs R2 and R3 share no papers at all. This indicates the ranking stage responds to query semantics rather than returning a fixed corpus ordering, a necessary property for an agentic retrieval system whose value depends on tailoring the retrieved set to the user’s specific comparative question. Notably, several papers added in the corpus expansion (OpenAgents, ART [19], and RAP [20]) are selected into top-5 sets, confirming that the enlarged corpus actively changes retrieval rather than being ignored. The query-sensitivity statistics indicate that the enlarged corpus does not collapse the system into a fixed retrieval pattern.

## 5.3 Retrieval Quality

Query-sensitivity shows the retrieved sets difer across queries, but not whether they are good. To assess ranking quality directly, we labeled the relevance of corpus papers for each of the three main queries on a four-point graded scale (3 = highly relevant, 2 = relevant, 1 = marginal, 0 = not relevant) and computed Precision@5, nDCG@5, Recall@5, and mean reciprocal rank (MRR). Relevance labels are author-assigned; we report this as a limitation in Section 7, and treat the labels as a small-scale, single-annotator gold standard rather than a benchmark-grade resource.

Table 3: Top-5 papers selected per run on the 100-paper corpus. No paper appears in all three runs.

<table><tr><td>R1: Multi-agent</td><td>R2: Evaluation</td><td>R3: Verbal RL</td></tr><tr><td>AgentVerse</td><td>AgentBench</td><td>Reflexion</td></tr><tr><td>AutoGen</td><td>AgentSurvey</td><td>CAMEL</td></tr><tr><td>AgentSurvey</td><td>ART</td><td>AgentVerse</td></tr><tr><td>AgentBench</td><td>Chain-of-Thought</td><td>Gen. Agents</td></tr><tr><td>OpenAgents</td><td>RAP</td><td>Inner Monologue</td></tr></table>

Table 4: Retrieval quality on the three main queries (authorassigned graded relevance). Precision@5 and MRR are saturated; nDCG@5 and Recall@5 are the more discriminative measures.

<table><tr><td>Query</td><td>P@5</td><td>nDCG@5</td><td>Recall@5</td><td>MRR</td></tr><tr><td>R1 (multi-agent)</td><td>1.000</td><td>0.719</td><td>0.455</td><td>1.000</td></tr><tr><td>R2 (evaluation)</td><td>1.000</td><td>0.588</td><td>0.500</td><td>1.000</td></tr><tr><td>R3 (verbal RL)</td><td>1.000</td><td>0.950</td><td>0.625</td><td>1.000</td></tr><tr><td>Mean</td><td>1.000</td><td>0.752</td><td>0.527</td><td>1.000</td></tr></table>

Table 4 reports the results. Precision@5 is 1.0 on all three queries: every paper the ranker placed in the top-5 was judged at least marginally relevant. We read this cautiously: perfect precision on author-assigned labels reflects that the ranker avoids clearly of topic papers rather than that retrieval is solved. The more informa tive signals are nDCG@5 and Recall@5. Mean nDCG@5 is 0.752, with the evaluation query (R2) lowest at 0.588: although all five retrieved papers were relevant, their ordering did not match the ideal graded ranking, indicating the ranker captures relevance bet ter than fine-grained priority. Mean Recall@5 is 0.527, meaning a top-5 cutof recovers roughly half of the papers labeled relevant in the corpus, expected given that several queries have more than five relevant papers, and a useful characterization of the precision– recall trade-of at this cutof. MRR is 1.0 throughout: the top-ranked paper was always relevant.

## 5.4 Retriever Comparison

To compare the ranker against simpler retrieval alternatives, we evaluated BM25, dense retrieval, hybrid retrieval, and the full ranker using the same author-assigned graded relevance labels. Table 5 reports mean performance across the three main queries.

The full ranker achieves the highest Precision@5 and nDCG@5, improving mean Precision@5 to 1.000 (versus 0.733 for BM25 and 0.667 for both dense and hybrid retrieval) and improving mean nDCG@5 to 0.752 (versus 0.640 for BM25, 0.595 for dense retrieval, and 0.685 for hybrid retrieval). On the larger corpus BM25 is a stronger baseline than before, narrowing but not closing the preci sion gap. Because the full ranker outputs five selected papers, we compare it to the other retrievers primarily at @5; @10 metrics are not defined for the capped full-ranker output.

Table 5: Retriever comparison across BM25, dense retrieval, hybrid retrieval, and the full ranker. Metrics are averaged over the three main queries using author-assigned graded relevance.

<table><tr><td>System</td><td>P@5</td><td>P@10</td><td>nDCG@5</td><td>nDCG@10</td><td>R@5</td><td>R@10</td></tr><tr><td>BM25</td><td>0.733</td><td>0.433</td><td>0.640</td><td>0.587</td><td>0.396</td><td>0.457</td></tr><tr><td>Dense</td><td>0.667</td><td>0.333</td><td>0.595</td><td>0.525</td><td>0.343</td><td>0.343</td></tr><tr><td>Hybrid</td><td>0.667</td><td>0.500</td><td>0.685</td><td>0.658</td><td>0.343</td><td>0.520</td></tr><tr><td>Full ranker</td><td>1.000</td><td>-</td><td>0.752</td><td>-</td><td>0.527</td><td>-</td></tr></table>

## 5.5 Reformulation Ablation

We tested whether the number of reformulated queries afects retrieval by re-running each main query with one, two, and four reformulations and measuring Recall@5. Mean Recall@5 was 0.493 with one reformulation, 0.527 with two, and 0.493 with four, a small benefit at two reformulations driven by the evaluation query (R2: 0.400 to 0.500), with the other two queries flat. The efect is modest: on a focused corpus the base query already retrieves much of the relevant neighborhood, so additional reformulations add little. We retain reformulation as an architectural feature whose value is more likely to appear at larger corpus scales and under the sparseretrieval conditions where the ReAct loop activates (Section 5.7).

## 5.6 Schema Compliance and Failure Analysis

Two runs achieved 80% compliance (4/5) and one achieved 100% (5/5), for a mean of 86.7%. Failures occurred on papers with surveylike structure, merged contribution and novelty fields, or broader framework papers whose contribution statements did not map cleanly to the four-field schema. Structural validity of the JSON is always guaranteed by constrained decoding; the failures are field-completeness failures on atypically structured papers. The recommended fix is a fallback extraction prompt targeting such papers.

## 5.7 ReAct Loop Activation Under Sparse Retrieval

In the main broad-query experiments the ReAct refinement loop did not activate, because the 100-paper corpus returns suficient candidates for any broad query on the first iteration. To test the loop directly, we constructed a sparse-retrieval stress test: five narrow queries evaluated under a strict relevance threshold that forces first-pass retrieval below the minimum-papers requirement.

Table 6 reports the result. Under the default threshold the loop remains dormant on all five queries. Under the strict threshold the loop activates on three of five queries, issuing one to two refinement iterations, and recovers to suficient coverage (≥ 3 papers) on one of the three activations; for example, increasing retrieval from one paper to six for the paged-memory query. This demonstrates that the refinement mechanism is functional and beneficial when retrieval is sparse, while remaining correctly inactive when the corpus already supplies enough candidates.

Table 6: ReAct loop activation under a sparse-retrieval stress test. The loop fires on 3/5 queries and recovers coverage on 1/3 activations. “Iters” counts total iterations (initial pass plus refinements), so the number of refinement steps is Iters − 1.

<table><tr><td>Query (sparse)</td><td>Iter-1</td><td>Refine</td><td>Iters</td><td>Final</td></tr><tr><td>verbal self-reflection memory</td><td>3</td><td>no</td><td>1</td><td>3</td></tr><tr><td>chunked cross-attention retr.</td><td>6</td><td>no</td><td>1</td><td>6</td></tr><tr><td>zero-ablation attribution</td><td>0</td><td>yes</td><td>3</td><td>0</td></tr><tr><td>OS-style paged memory</td><td>1</td><td>yes</td><td>2</td><td>6</td></tr><tr><td>dialectic multi-robot collab.</td><td>2</td><td>yes</td><td>3</td><td>2</td></tr></table>

Table 7: Deterministic gap-matrix statistics. Empty cells are candidate structural gaps computed programmatically, not LLM-generated.

<table><tr><td>Quantity</td><td>Value</td></tr><tr><td>Distinct papers placed</td><td>12</td></tr><tr><td>Problem classes (rows)</td><td>7</td></tr><tr><td>Method families (columns)</td><td>10</td></tr><tr><td>Total cells</td><td>70</td></tr><tr><td>Filled cells</td><td>10</td></tr><tr><td>Empty cells (gaps)</td><td>60</td></tr><tr><td>Matrix density</td><td>0.143</td></tr></table>

## 5.8 Deterministic Gap Matrix Construction

The earlier LLM-inferred gap descriptions sometimes produced cross-application observations rather than clean within-corpus absence signals. We therefore construct the final gap matrix determin istically using a fixed paper-id taxonomy derived from retrieved paper metadata and contribution records. The problem × method matrix is then populated programmatically, and empty cells are reported as candidate corpus-level gaps within the retrieved paper slice. Crucially, the gap decision itself is structural: the system does not ask the LLM to directly generate the final set of gaps.

The “gaps identified” row in Table 2 refers to report-level summarized gaps, while the deterministic matrix analysis counts all 60 empty problem–method cells across the union of retrieved papers; the two are distinct metrics and are not directly comparable.

Applied to the union of papers retrieved across the three main queries, the deterministic construction yields a 7 × 10 matrix (7 problem classes, 10 method families) with 10 of 70 cells filled, giving a matrix density of 0.143 (Table 7). The 60 empty cells are candidate structural gaps by construction rather than generated text, making the gap set reproducible and removing the cross-application noise present in directly LLM-inferred gaps.

## 5.9 Gap-Matrix Validation

To assess whether deterministic empty cells correspond to plau sible research gaps, we sampled 20 empty cells from the problem × method matrix and manually labeled each as plausible, too broad, indirect, or meaningless. As shown in Table 8, 12 of 20 sampled empty cells were judged plausible, yielding a gap precision of 0.600.

Table 8: Validation of sampled deterministic gap-matrix empty cells.

<table><tr><td>Metric</td><td>Value</td></tr><tr><td>Sampled empty cells</td><td>20</td></tr><tr><td>Labeled cells</td><td>20</td></tr><tr><td>Plausible cells</td><td>12</td></tr><tr><td>Gap precision</td><td>0.600</td></tr></table>

Among the 20 sampled cells, the 8 non-plausible cases broke down as 4 indirect (only indirectly supported by the retrieved corpus), 3 too broad to be actionable, and 1 meaningless. This suggests that the deterministic matrix is useful as a corpus-level absence signal, but individual empty cells should be interpreted cautiously rather than as definitive claims about the broader literature.

## 5.10 Qualitative Case Study

To illustrate the type of structured output produced by the system, Table 9 shows a representative qualitative case study from the multi-agent framework query. Unlike a standard RAG summary, the system separates shared coverage, paper-specific diferentiation, and corpus-level absence signals.

## 5.11 Baseline RAG Comparison

We implemented a baseline RAG system (retrieval followed by direct GPT-4o summarization, with no ranker, no structured extraction, and no comparison agent) and ran it on all three main queries. The baseline produces a coherent multi-paragraph summary per query in 3–4 seconds but emits no structured records, associates no overlaps with specific paper identifiers, and builds no gap matrix. The proposed system takes roughly 23 seconds (an increase of about sevenfold) but produces typed extraction records, paper-level overlaps, a structured gap matrix, and an auditable six-stage trace. Counting structured capabilities (structured contribution records, paper-level overlap IDs, per-paper diferentiation, a problem × method gap matrix, and an auditable multi-stage trace), the full system supports all five while the baseline supports none.

Beyond this capability diference, we compare retrieval quality directly. Because the baseline retrieves by raw similarity order while the full system applies the ranking stage, this comparison isolates the value of ranking. Using the same author-assigned relevance labels, Table 10 reports the head-to-head: the ranker improves mean Precision@5 from 0.733 to 1.000, mean nDCG@5 from 0.548 to 0.752, and mean Recall@5 from 0.368 to 0.527. We note that the baseline’s raw-similarity retrieval is not identical to the dense retriever in Table 5: the baseline retrieves the top-15 chunks and deduplicates to papers by first (best-ranked) occurrence before truncating to five, whereas the dense retriever in Table 5 ranks at the paper level. The two therefore select diferent top-5 sets, which is why their @5 metrics difer. The ranking stage thus contributes measurable retrieval-quality gains on top of the shared embedding retrieval, in addition to the structured artifacts the baseline cannot produce. The latency increase is the direct cost of structure, and is acceptable for a literature-review setting where the alternative is hours of manual reading.

Table 9: Qualitative case study of structured comparison output for the query “Compare multi-agent LLM frameworks for collaborative reasoning.”

<table><tr><td>Query</td><td>Overlap Example</td><td>Difference Example</td><td>Gap Example</td></tr><tr><td>Multi-agent LLM frameworks for collaborative reasoning</td><td>AgentVerse and AutoGen both address multi-agent coordination through structured multi-agent collaboration, while AgentBench and AgentSurvey emphasize evaluation and conceptual framing.</td><td>AgentVerse focuses on emergent multi-agent collaboration; AutoGen emphasizes scalable multi-agent conversation; OpenAgents focuses on deployment infrastructure for agents in real-world settings.</td><td>Within the retrieved set, multi-agent collaboration frameworks are not paired with explicit benchmarking or deployment-oriented evaluation, suggesting an absent problem-method combination in this corpus slice.</td></tr></table>

Table 10: Retrieval-quality head-to-head: full system (with ranker) versus the baseline RAG system (raw similarity or der), mean over the three main queries, author-assigned graded relevance.

<table><tr><td>System</td><td>P@5</td><td>nDCG@5</td><td>Recall@5</td><td>MRR</td></tr><tr><td>Baseline RAG (no ranker)</td><td>0.733</td><td>0.548</td><td>0.368</td><td>1.000</td></tr><tr><td>Full system (ours)</td><td>1.000</td><td>0.752</td><td>0.527</td><td>1.000</td></tr></table>

Table 11: Component ablation of structured comparison capabilities.

<table><tr><td>System Variant</td><td>Records</td><td>Overlap IDs</td><td>Diff.</td><td>Gap Matrix</td><td>Trace</td></tr><tr><td>Baseline RAG</td><td>No</td><td>No</td><td>No</td><td>No</td><td>No</td></tr><tr><td>+ Extractor</td><td>Yes</td><td>No</td><td>No</td><td>No</td><td>No</td></tr><tr><td>Full system</td><td>Yes</td><td>Yes</td><td>Yes</td><td>Yes</td><td>Yes</td></tr></table>

## 5.12 Component Ablation

Isolating each stage’s contribution shows a clear progression: the baseline RAG system yields generic prose with no structure; adding the extractor yields structured four-field records but no cross-paper reasoning; and only the full system, with the comparison agent, produces paper-level overlaps, per-paper diferentiation, and a gap matrix. The comparison agent is thus the component that distin guishes this system from a structured-output RAG pipeline.

## 5.13 External Usefulness Assessment

To obtain evaluation independent of the author, we recruited a sin gle external rater (a graduate student familiar with LLM agents but not involved in building the system) to assess the structured output for the three main queries. The rater scored each output dimension from 1 (poor) to 5 (excellent) without access to the author’s labels, and the rater’s identity is not reported in the paper. These ratings were collected on an earlier 55-paper version of the system outputs. Because this assessment predates the final corpus expansion, we use it only as a qualitative usefulness signal, not as evidence for final-system performance. Table 12 reports the mean scores across the three queries.

Table 12: External usefulness assessment by a single independent rater (mean over the three main queries, 1–5 scale).

<table><tr><td>Dimension</td><td>Mean (1-5)</td></tr><tr><td>Extraction correctness</td><td>4.00</td></tr><tr><td>Overlap correctness</td><td>4.00</td></tr><tr><td>Differentiation specificity</td><td>3.00</td></tr><tr><td>Gap usefulness</td><td>3.00</td></tr><tr><td>Overall usefulness</td><td>3.33</td></tr></table>

The rater scored extraction correctness and overlap correctness highest (4.0 each), with diferentiation specificity, gap usefulness, and overall usefulness lower (3.0, 3.0, and 3.3 respectively). Two consistent critiques accompanied the scores: that per-paper differentiation describes each paper largely in isolation rather than explicitly contrasting it against the other papers in the retrieved set, and that the problem–method gaps would be more useful with deeper methodological analysis rather than high-level labels. We treat both as concrete targets for future work: the first motivating a set-aware diferentiation pass, and the second a richer gap characterization. As a single-rater assessment these scores are indicative rather than conclusive, consistent with the evaluation limitation discussed in Section 7.

## 5.14 Cross-Model Robustness

To test whether the retrieval behavior is specific to a single LLM backbone, we re-ran the three main queries with two additional backbones, GPT-4o-mini and GPT-4.1, holding the corpus, retriever, prompts, ranking procedure, and evaluation labels fixed. Table 13 reports the mean retrieval metrics and schema compliance across the three queries.

The main structural finding is stable across backbones: all three models produce query-sensitive top-5 sets, with low mean pairwise Jaccard similarity (0.12–0.20), and all preserve the architectural capability gap over the baseline RAG system. The additional backbones also improve schema compliance from 86.7% to 100.0%. Retrieval precision and recall are lower under GPT-4o-mini and GPT-4.1. This drop partly reflects the limited coverage of the author-assigned relevance labels: the additional backbones retrieve topically related papers such as AgentTuning (a corpus paper not among the cited references) and OpenAgents that were not included in the original graded-relevance set. We therefore treat the cross-model experi ment as preliminary robustness evidence for query-sensitivity and schema compliance, not as a definitive model-ranking benchmark.

Table 13: Cross-model robustness across three LLM back bones. Metrics are averaged over the three main queries using the same author-assigned graded relevance labels.

<table><tr><td>Backbone</td><td>P@5</td><td>nDCG@5</td><td>R@5</td><td>Schema</td><td>Jaccard</td></tr><tr><td>GPT-4o</td><td>1.000</td><td>0.752</td><td>0.527</td><td>86.7%</td><td>0.12</td></tr><tr><td>GPT-4o-mini</td><td>0.800</td><td>0.624</td><td>0.410</td><td>100.0%</td><td>0.20</td></tr><tr><td>GPT-4.1</td><td>0.800</td><td>0.707</td><td>0.418</td><td>100.0%</td><td>0.18</td></tr></table>

Table 14: Extended evaluation on seven additional queries (R4–R10), author-assigned graded relevance. Means for the full ten-query set (R1–R10) are shown for reference.

<table><tr><td>Query</td><td>P@5</td><td>nDCG@5</td><td>Recall@5</td><td>MRR</td></tr><tr><td>R4 (tool use)</td><td>1.000</td><td>0.665</td><td>0.417</td><td>1.000</td></tr><tr><td>R5 (memory)</td><td>1.000</td><td>0.771</td><td>0.500</td><td>1.000</td></tr><tr><td>R6 (planning)</td><td>0.800</td><td>0.453</td><td>0.333</td><td>1.000</td></tr><tr><td>R7 (RAG factuality)</td><td>1.000</td><td>0.948</td><td>0.500</td><td>1.000</td></tr><tr><td>R8 (single vs multi)</td><td>1.000</td><td>0.804</td><td>0.500</td><td>1.000</td></tr><tr><td>R9 (hallucination)</td><td>1.000</td><td>0.700</td><td>0.500</td><td>1.000</td></tr><tr><td>R10 (reflection)</td><td>1.000</td><td>0.791</td><td>0.556</td><td>1.000</td></tr><tr><td>Mean (R4–R10)</td><td>0.971</td><td>0.733</td><td>0.472</td><td>1.000</td></tr><tr><td>Mean (R1–R10)</td><td>0.980</td><td>0.739</td><td>0.489</td><td>1.000</td></tr></table>

## 5.15 Extended Evaluation: Seven Additional Queries

The three main queries (R1–R3) are deliberately broad comparison queries. To probe whether the retrieval behavior holds on a wider and more varied query set, we ran seven additional queries (R4–R10) spanning tool use, agent memory, planning, RAG fac tuality evaluation, single- versus multi-agent architectures, hal lucination reduction, and reflection. These queries use the same corpus, pipeline, and author-assigned graded-relevance protocol as the main experiments; they extend rather than replace the main results, which remain as reported above. Table 14 reports per-query retrieval metrics for R4–R10.

Two observations follow. First, query-sensitivity strengthens at the larger query set: across all ten queries no paper appears in every top-5 set, the mean pairwise Jaccard similarity is 0.115 (versus 0.12 across the three main queries), and of the 29 distinct papers selected across the 50 ranked slots, 18 are query-exclusive. The most frequently selected paper appears in only six of ten queries. This is consistent with the main finding that the ranker responds to query semantics rather than returning a fixed ordering.

Second, Precision@5 is no longer saturated on the wider set: the mean over the seven new queries is 0.971, and over all ten queries 0.980. The single sub-perfect case is R6 (planning), where an agent evaluation benchmark was ranked into the top-5 and judged not relevant to a planning-method query under the author labels. We read this as evidence that the graded-relevance labels are discriminative rather than uniformly permissive: the same labeling protocol that yields Precision@5 of 1.000 on the main queries also penalizes a topically adjacent but of-target retrieval. Schema compliance over the ten queries averages 84.0%, close to the 86.7% reported on the three main queries. As with the main evaluation, these are single-run, author-labeled results on a 100-paper corpus and carry the same limitations discussed in Section 7.

## 6 Discussion

## 6.1 The Latency–Structure Trade-of

The defining design tension in agentic retrieval is between latency and structure. A single-call RAG baseline answers in under four seconds; our system takes roughly seven times longer. The return on that cost is a set of typed, inspectable artifacts (per-paper records, paper-level overlaps, and a gap matrix) that a downstream user or system can act on programmatically. For interactive web search this trade-of would be unacceptable; for literature review, where the user would otherwise spend hours reading and manually tracking relationships, under thirty seconds is negligible. The right operating point depends on the retrieval task, and agentic retrieval systems should make this trade-of explicit rather than defaulting to one extreme.

## 6.2 Query-Sensitivity as a Retrieval Property

The clearest empirical signal in this prototype evaluation is that the ranked set changes substantially with the query. Across the three main runs, no paper appears in all three top-5 sets and the mean pairwise Jaccard similarity is only 0.12. The extended sevenquery evaluation strengthens this pattern: across all ten queries, no paper appears in every top-5 set, mean pairwise Jaccard similarity remains low at 0.115, and 18 of 29 distinct retrieved papers are query-exclusive. For an agentic retrieval system this is the property that justifies the architecture: if the ranked set did not vary with the query, the comparison stage would simply re-describe a fixed set of papers. Query-sensitive ranking ensures that the structured comparison is computed over a set tailored to the user’s specific question.

## 6.3 Structured Records as Retrieval Output

A broader implication is that retrieval output need not be passages or prose. By enforcing a schema at extraction time, the system turns each retrieved document into a typed record. This reframes retrieval as producing structured data rather than text, which in turn enables comparison operations (overlap detection, deterministic gap-matrix construction) that are awkward or impossible over free text. We see this as a useful direction for agentic IR: treat the retrieved set as a small structured database rather than a context window to be summarized.

## 7 Limitations

As a prototype, the system has two scope limits that frame its future work. First, the 100-paper corpus, though substantially larger and more diverse than the initial set, remains modest relative to large-scale IR benchmarks. Second, evaluation uses author-assigned relevance labels and manually labeled gap-validation judgments, with usefulness assessed by a single external rater whose ratings were collected on an earlier 55-paper version of the outputs; addi tional independent raters and a broader multi-rater human study on the final outputs would further strengthen the conclusions. Scaling the corpus and expanding external evaluation are the natural next steps toward archival-grade benchmarking.

## 8 Conclusion

We presented the Novelty-Aware Research Agent, a prototype agen tic retrieval system that layers structured multi-step reasoning on a RAG pipeline to compare research contributions across a retrieved corpus. The six-component pipeline combines query reformulation, a ReAct retrieval loop, relevance ranking, schema-guided extraction, a three-pass comparison stage with deterministic problem–method matrix construction, and answer generation. On a 100-paper cor pus the system demonstrates query-sensitive retrieval: no paper appears in all three main top-5 sets, and an extended ten-query evaluation preserves this pattern with mean pairwise Jaccard sim ilarity of 0.115 and 18 query-exclusive papers among 29 distinct retrieved papers. The system achieves 86.7% schema compliance on the three main queries and 84.0% over the ten-query set, while supporting 5/5 structured comparison capabilities versus 0/5 for a baseline RAG system. Within the three-query author-assigned eval uation, the ranker attains mean Precision@5 1.000, nDCG@5 0.752, and Recall@5 0.527, ahead of BM25, dense, and hybrid retrieval; over all ten queries, Precision@5 remains high but non-saturated at 0.980, with nDCG@5 of 0.739 and Recall@5 of 0.489. Gap-matrix validation over 20 sampled empty cells yields gap precision of 0.600. Across GPT-4o-mini and GPT-4.1, query-sensitivity remains sta ble and schema compliance improves, while retrieval precision is lower under the fixed labels. These results support treating retrieval output as structured data for contribution-level comparison: the payof is a single inspectable map of what a retrieved set covers and what it leaves open, in place of a ranked list the researcher would otherwise cross-reference by hand. We leave large-scale evaluation and independent human assessment as future work.

## References

[1] Patrick Lewis, Ethan Perez, Aleksandra Piktus, Fabio Petroni, Vladimir Karpukhin, Naman Goyal, Heinrich Küttler, Mike Lewis, Wen-tau Yih, Tim Rocktäschel, Sebastian Riedel, and Douwe Kiela. Retrieval-augmented genera tion for knowledge-intensive NLP tasks. arXiv preprint arXiv:2005.11401, 2020. https://arxiv.org/abs/2005.11401

[2] Shunyu Yao, Jefrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, and Yuan Cao. ReAct: Synergizing reasoning and acting in language models. arXiv preprint arXiv:2210.03629, 2023. https://arxiv.org/abs/2210.03629

[3] Brandon T. Willard and Rémi Louf. Eficient guided generation for large language models. arXiv preprint arXiv:2307.09702, 2023. https://arxiv.org/abs/2307.09702

[4] Qingyun Wu, Gagan Bansal, Jieyu Zhang, Yiran Wu, Beibin Li, Erkang Zhu, Li Jiang, Xiaoyun Zhang, Shaokun Zhang, Jiale Liu, Ahmed Hassan Awadallah, Ryen W. White, Doug Burger, and Chi Wang. AutoGen: Enabling next-gen LLM applications via multi-agent conversation. arXiv preprint arXiv:2308.08155, 2023. https://arxiv.org/abs/2308.08155

[5] Sirui Hong, Mingchen Zhuge, Jiaqi Chen, Xiawu Zheng, Yuheng Cheng, Ceyao Zhang, Jinlin Wang, Zili Wang, Steven Ka Shing Yau, Zijuan Lin, Liyang Zhou, Chenyu Ran, Lingfeng Xiao, Chenglin Wu, and Jürgen Schmidhuber. MetaGPT: Meta programming for a multi-agent collaborative framework. arXiv preprint arXiv:2308.00352, 2024. https://arxiv.org/abs/2308.00352

[6] Guohao Li, Hasan Abed Al Kader Hammoud, Hani Itani, Dmitrii Khizbullin, and Bernard Ghanem. CAMEL: Communicative agents for “mind” exploration of large language model society. arXiv preprint arXiv:2303.17760, 2023. https: //arxiv.org/abs/2303.17760

[7] Noah Shinn, Federico Cassano, Edward Berman, Ashwin Gopinath, Karthik Narasimhan, and Shunyu Yao. Reflexion: Language agents with verbal reinforcement learning. arXiv preprint arXiv:2303.11366, 2023. https://arxiv.org/abs/2303. 11366

[8] Xiao Liu, Hao Yu, Hanchen Zhang, Yifan Xu, Xuanyu Lei, Hanyu Lai, Yu Gu, Hangliang Ding, Kaiwen Men, Kejuan Yang, Shudan Zhang, Xiang Deng, Aohan Zeng, Zhengxiao Du, Chenhui Zhang, Sheng Shen, Tianjun Zhang, Yu Su, Huan Sun, Minlie Huang, Yuxiao Dong, and Jie Tang. AgentBench: Evaluating LLMs as agents. arXiv preprint arXiv:2308.03688, 2023. https://arxiv.org/abs/2308.03688

[9] Joon Sung Park, Joseph C. O’Brien, Carrie J. Cai, Meredith Ringel Morris, Percy Liang, and Michael S. Bernstein. Generative Agents: Interactive Simulacra of Human Behavior. arXiv preprint arXiv:2304.03442, 2023. https://arxiv.org/abs/ 2304.03442

[10] Akari Asai, Zeqiu Wu, Yizhong Wang, Avirup Sil, and Hannaneh Hajishirzi. Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection. arXiv preprint arXiv:2310.11511, 2023. https://arxiv.org/abs/2310.11511

[11] Shi-Qi Yan, Jia-Chen Gu, Yun Zhu, and Zhen-Hua Ling. Corrective Retrieval Augmented Generation. arXiv preprint arXiv:2401.15884, 2024. https://arxiv.org/ abs/2401.15884

[12] Lei Wang, Chengbang Ma, Xueyang Feng, Zeyu Zhang, Hao-ran Yang, Jingsen Zhang, Zhi-Yang Chen, Jiakai Tang, Xu Chen, Yankai Lin, Wayne Xin Zhao, Zhewei Wei, and Ji-rong Wen. A survey on large language model based autonomous agents. Frontiers of Computer Science, 18:186345, 2024. https://api. semanticscholar.org/CorpusID:261064713

[13] Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, Brian Ichter, Fei Xia, Ed Chi, Quoc Le, and Denny Zhou. Chain-of-thought prompting elicits reasoning in large language models. Advances in Neural Information Processing Systems, 35:24824–24837, 2022. https://arxiv.org/abs/2201.11903

[14] Tianbao Xie, Fan Zhou, Zhoujun Cheng, Peng Shi, Luoxuan Weng, Yitao Liu, Toh Jing Hua, Junning Zhao, Qian Liu, Che Liu, Leo Z. Liu, Yiheng Xu, Hongjin Su, Dongchan Shin, Caiming Xiong, and Tao Yu. OpenAgents: An open platform for language agents in the wild. arXiv preprint arXiv:2310.10634, 2023. https: //arxiv.org/abs/2310.10634

[15] OpenAI. GPT-4 technical report. arXiv preprint arXiv:2303.08774, 2023. https: //arxiv.org/abs/2303.08774

[16] Weize Chen, Yusheng Su, Jingwei Zuo, Cheng Yang, Chenfei Yuan, Chi-Min Chan, Heyang Yu, Yaxi Lu, Yi-Hsin Hung, Chen Qian, Yujia Qin, Xin Cong, Ruobing Xie, Zhiyuan Liu, Maosong Sun, and Jie Zhou. AgentVerse: Facilitating multi-agent collaboration and exploring emergent behaviors. arXiv preprint arXiv:2308.10848, 2023. https://arxiv.org/abs/2308.10848

[17] Binfeng Xu, Zhiyuan Peng, Bowen Lei, Subhabrata Mukherjee, Yuchen Liu, and Dongkuan Xu. ReWOO: Decoupling Reasoning from Observations for Eficient Augmented Language Models. arXiv preprint arXiv:2305.18323, 2023. https://arxiv. org/abs/2305.18323

[18] Yuan Li, Yixuan Zhang, and Lichao Sun. MetaAgents: Simulating Interactions of Human Behaviors for LLM-based Task-oriented Coordination via Collaborative Generative Agents. arXiv preprint arXiv:2310.06500, 2023. https://arxiv.org/abs 2310.06500

[19] Bhargavi Paranjape, Scott Lundberg, Sameer Singh, Hannaneh Hajishirzi, Luke Zettlemoyer, and Marco Tulio Ribeiro. ART: Automatic multi-step reasoning and tool-use for large language models. arXiv preprint arXiv:2303.09014, 2023. https://arxiv.org/abs/2303.09014

[20] Shibo Hao, Yi Gu, Haodi Ma, Joshua Jiahua Hong, Zhen Wang, Daisy Zhe Wang, and Zhiting Hu. Reasoning with language model is planning with world model. arXiv preprint arXiv:2305.14992, 2023. https://arxiv.org/abs/2305.14992

[21] Abdul Malik Sami, Zeeshan Rasheed, Kai-Kristian Kemell, Muhammad Waseem, Terhi Kilamo, Mika Saari, Anh Nguyen Duc, Kari Systä, and Pekka Abrahamsson. System for systematic literature review using multiple AI agents: Concept and an empirical evaluation. arXiv preprint arXiv:2403.08399, 2024. https://arxiv.org/ abs/2403.08399

[22] Movina Moses, Mohab Elkaref, James Barry, Vishnudev Kuruvanthodi, Muthukumaran Ramasubramanian, Campbell Watson, and Geeth R. De Mel. Agentic workflows for gap-aware literature reviews. AGU Annual Meeting, 2025. https://research.ibm.com/publications/agentic-workflows-for-gap-awareliterature-reviews


---

# 2605.25007_元模态智能体：缺失模态候选重排序

[2605.25007](https://arxiv.org/abs/2605.25007)

# Meta-Modal Agent: Sequential Evidence Routing for Missing-Modality Candidate Reranking

Jinze Wang<sup>†</sup> School of Engineering Swinburne University of Technology Melbourne, Australia

Lu Zhang School of Cybersecurity Chengdu University of Information Technology Chengdu, China

Yangchen Zeng<sup>†</sup> School of Computer Science and Technology Southeast University Shanghai, China

Yuze Liu School of Engineering Swinburne University of Technology Melbourne, Australia

Jiong Jin School of Engineering Swinburne University of Technology Melbourne, Australia

Tiehua Zhang\* School of Computer Science and Technology Tongji University Shanghai, China tiehuaz@tongji.edu.cn

Zhishu Shen School of Computer Science and Artificial Intelligence Wuhan University of Technology Wuhan, China

Zhu Sun Singapore University of Technology and Design Singapore

## Abstract

Missing modalities cause severe failures in multimodal recommender systems. User histories, item text, and visual evidence are frequently absent during cold-start scenarios, exactly when rec ommendation quality matters most. Existing approaches recover absent signals through imputation, feature propagation, or generative reconstruction, but these strategies can inject unsupported evi dence when the surviving signals are weak. We introduce the Meta-Modal Agent (MMA), a large language model based candidate-pool reranker that treats missingness as a sequential evidence-routing problem. MMA is trained with balanced missingness-task reinforcement learning over masked-modality episodes and is eval uated in two variants: MMA-Auto, which uses only automated text, image, and graph tools, and MMA-Interactive, which ad ditionally permits clarification questions grounded in surviving modalities as an upper-bound diagnostic. MMA operates after a first-stage retriever has produced a candidate pool; it scores those candidates rather than retrieving items from the full catalog. Fi nal reranking fuses MMA scores with first-stage retrieval scores selected on validation data. Our evaluation is organized around four evidence checks required for a robust missing-modality claim: oracle-free one-observed-modality availability (OOMA) robustness, per-modality OOMA breakdowns, fixed-pool full-catalog rerank ing, and a deterministic-router mechanism control. MMA-Auto improves target-positive OOMA NDCG@10 by 4<sup>.</sup>0% and fixed-pool full-catalog reranking NDCG@10 by 12<sup>.</sup>7% over the strongest noninteractive baseline. RuleRouter-Fuse, which uses the same tools and fusion rule without learned policy updates, underperforms MMA-Auto, supporting learned routing beyond deterministic tool fusion. MMA-Interactive adds a 4<sup>.</sup>1% upper-bound gain when clarification is available.

## CCS Concepts

• Information systems → Personalization; Social recommendation.

## Keywords

Large language models, Personalized recommendation, Cold-start recommendation

## ACM Reference Format:

Jinze Wang<sup>†</sup>, Yangchen Zeng<sup>†</sup>, Tiehua Zhang\*, Lu Zhang, Yuze Liu, Zhishu Shen, Jiong Jin, and Zhu Sun. 2026. Meta-Modal Agent: Sequential Evidence Routing for Missing-Modality Candidate Reranking. In Proceedings of Proceedings of the 35th ACM International Conference on Information and Knowledge Management (CIKM ’26). ACM, New York, NY, USA, 9 pages. https://doi.org/XXXXXXX.XXXXXXX

## 1 Introduction

Modern recommender systems increasingly rely on multimodal evidence: interaction graphs reveal collaborative preferences, text describes item semantics, and images or audio expose attributes that may never appear in structured metadata [12, 22]. This evidence is rarely complete in the regimes that matter most. A new user has little or no behavioral history; a newly listed item may have an image but no description; a privacy-preserving deployment may deliberately suppress user attributes [12]. Missing modalities are therefore not a peripheral data-cleaning issue, but a core cold-start condition for recommendation [15]. Most missing-modality recommenders treat the absent signal as things to recover. Early and recent systems learn robust predictors from incomplete modality sets, propagate features, or generate missing representations from the available modalities [8, 18, 24]. These approaches are appropriate when the observed evidence is informative enough to constrain the missing signal. Under extreme missingness, however, reconstruction can become a liability: a generated behavioral profile from a single weak textual clue may look plausible while adding unsupported evidence to the ranking pipeline [13, 30].

LLM-based reranking agents ofer a diferent model. Rather than producing a single fused representation, an agent can decide which tool to call, inspect returned evidence, recover from tool failures, and ask a user for clarification [2, 19]. Generative agents perform well in recommendation, and large-scale tool-use training allows LLMs to use APIs efectively [16, 29]. ReAct-style prompting shows how language models can interleave reasoning with environment actions [27]. Yet static agent prompts often assume that tools will return valid observations. When a history lookup returns Null, a brittle agent may retry the same failed path or hallucinate the unavailable evidence.

This paper reframes missing modalities from a purely representation learning problem to a dynamic evidence-routing problem inside candidate-pool reranking. If the reranking state is partially observ able, then a scorer can benefit from a policy that decides which evidence source to query next and how to respond when a query returns Null. We propose the Meta-Modal Agent (MMA), an LLM based candidate-pool reranker trained with balanced missingnesstask reinforcement learning over episodes with masked modalities. MMA starts after a first-stage retriever has produced candidates; it does not perform full-catalog recall or add new items to the pool. During training, the agent repeatedly experiences missing tool outputs and receives a reward signal reflecting the relative costs of backend lookup, user clarification, and invalid retries. During inference, it adapts in context: a Null observation becomes evi dence about the environment, causing the agent to switch tools and score candidate items from surviving evidence. Crucially, we separate two deployment-relevant variants. MMA-Auto disables clarification and uses only automated text, image, and graph tools; MMA-Interactive permits Ask\_User and serves only as an interactive upper-bound diagnostic.

The contributions are:

• We formulate cold-start missingness as a POMDP over reranking tools, making failed evidence queries explicit observations rather than silent feature dropouts.

• We define an oracle-free candidate scoring and reranking protocol in which MMA scores a shared candidate pool and fuses the agent score with the first-stage retrieval score.

• We separate automated routing from interactive clarification: MMA-Auto is the deployment claim, while MMA-Interactive is reported only as an upper bound.

• We report per-modality one-observed-modality availability (OOMA) results and fixed-pool full-catalog reranking checks: MMA-Auto improves target-positive OOMA NDCG@10 by 4<sup>.</sup>0% and achieves a 12<sup>.</sup>7% mean per-dataset relative NDCG@10 gain in fixed-pool full-catalog reranking.

• We include a deterministic router control with identical tools and fusion; MMA-Auto improves average OOMA NDCG@10 from 0<sup>.</sup>1578 to 0<sup>.</sup>1711 over this control while using fewer failed calls and turns.

## 2 Related Work

## 2.1 Multimodal Recommendation under Missing Modalities

Multimodal recommender systems exploit text, images, audio, and interaction graphs to improve preference modeling [12]. Missing modalities have been studied both in recommendation and in broader multimodal learning [24]. LRMM is an early recommendationspecific treatment of cold-start missingness [18]. More recent work such as DGMRec reconstructs missing features by disentangling general and modality-specific representations [8]. Similarly, completionstyle approaches like GRE-MC enhance modality synthesis via graph retrieval [11], while others leverage modality-aware multiintention learning [26], or multi-modal graph neural networks [22] to achieve representation robustness. UniSRec addresses sparse item representations through universal sequence pre-training [6]. These methods motivate our setting but difer in objective: MMA learns an action policy that routes toward observable evidence before reranking a fixed candidate pool rather than synthesizing absent representations for full-catalog retrieval.

## 2.2 LLM Agents for Recommendation

LLM agents can maintain conversational context, call external tools, and revise plans after observing the environment. Generative agents have been studied in recommendation [20, 31], while ToolLLM demonstrates large-scale training for API-using language models [16]. ReAct provides a general prompting pattern for interleaving reasoning traces and actions [27]. AgentCF extends the agentic par adigm to collaborative filtering by simulating user–item interaction agents [32]. InstructRec adapts LLMs to follow natural-language recommendation instructions, showing strong zero-shot generalization across item domains [33]. MMA adopts the agentic interface but changes the training pressure: instead of assuming tools succeed, balanced missingness-task training repeatedly exposes the agent to missing modalities and rewards recovery from failed evidence paths.

## 2.3 Reinforcement Learning and Multi-Task Training for Sequential Decisions

RL has been applied to sequential recommendation [25] and conversational recommendation systems (CRS) where the agent must decide what to ask before recommending [10]. RLMRec integrates RL signals into multimodal recommendation to better align item representations with user preferences [17]. Our work difers from CRS in that the agent’s decision space is over modality-access tools rather than clarifying attribute questions, and from RLMRec in that we explicitly model and train for structural missingness rather than representation alignment. Multi-task and curriculum-style training can improve sample eficiency and generalization [21]. MMA uses task indices as a balancing and diagnostic mechanism over missingness patterns, ensuring that rare mask combinations receive adequate training coverage. Note that while our approach uses the "Meta" nomenclature, it difers from traditional meta-learning which optimizes for rapid gradient adaptation to new user domains [4, 9].

![](images/769bea42d48c848a7e8c729c6803e77bccad124df56307ec6eaf6a8e6ce27f42.jpg)  
Figure 1: Overview of MMA. The agent receives a shared candidate pool, routes among available evidence tools, treats Null returns as observations, and outputs candidate scores that are fused with first-stage retrieval scores for reranking.

## 2.4 LLM-Based Recommendation

A growing body of work treats recommendation as a language task, as outlined in recent surveys of LLMs for recommendation [1]. LlamaRec uses a two-stage pipeline in which a retrieval model supplies candidates that an LLM reranks [28]. We follow the same high-level division between first-stage retrieval and LLM-based reranking, but study a diferent failure mode: the evidence avail able to the reranker may itself be missing. When a modality is structurally absent—for example, a pure cold-start user with no interaction history—prompting over a dense history degrades to guessing. MMA difers by explicitly modeling missingness as part of the reranking action space: a Null observation is a first-class event that triggers routing rather than silent fallback to a degraded prompt.

## 3 Methodology

We introduce the Meta-Modal Agent (MMA) as a modular candidate pool reranker for missing-modality recommendation. Throughout the paper, first-stage retrieval denotes the upstream step that recalls candidates from the item catalog, while reranking denotes MMA’s role: scoring only the provided candidate pool. The method has four parts: (i) a fixed episode interface that exposes a first-stage candidate pool rather than the full catalog, (ii) an evidence-routing agent that treats failed tool calls as observations, (iii) a candidatescoring output protocol that fuses MMA scores with first-stage retrieval scores, and (iv) balanced missingness-task training that exposes the policy to each missingness pattern. This section defines the technical contract used by all experiments.

## 3.1 Module 1: Episode Interface and Candidate Pool

Each episode <sup>??</sup> begins with a shared candidate pool $C _ { e } \subset \mathcal { I }$ of size <sup>??</sup>, i.e., $\left| C _ { e } \right| = B .$ . Unless otherwise specified. The agent is given, for every candidate, an anonymized item ID, the first-stage rank, mary derived only from currently observable sources. Text-present episodes expose title/category/description snippets, image-only episodes expose frozen CLIP tag summaries, and behavior-only episodes expose graph-neighbor summaries. The hidden target item <sup>??</sup> is used only by the evaluator for reward and metrics; it is never shown to the agent.

We represent modality availability by a binary mask m $\in \{ 0 , 1 \} ^ { | \mathcal { M } | }$ over $\mathcal { M } = \{ m _ { \mathrm { t e x t } } , m _ { \mathrm { i m g } } , m _ { \mathrm { b e h } } \}$ . The mask is fixed within an episode and varies across episodes according to the task family distribution in §3.4. The mask is not directly revealed. The agent only discovers missingness by calling tools and observing whether the environment returns evidence or Null.

The target-positive protocol used for the main OOMA experiments inserts $i ^ { * }$ into $C _ { e }$ and fills the remaining <sup>??</sup> − 1 slots with hard negatives retrieved from the surviving evidence source: BM25 for text-present settings, CLIP-ViT-L/14 nearest-neighbor retrieval for image-only settings, and ANN graph retrieval for behavior-only settings. MMA never searches outside $C _ { e } ;$ this isolates its contri bution to candidate scoring and reranking. Section 4 separately reports the fixed-pool full-catalog reranking check.

## 3.2 Module 2: Evidence-Routing Agent

We model an episode as a partially observable Markov decision pro cess (POMDP) $\langle S , \mathcal { A } , \mathcal { P } , \Omega , O , \mathcal { R } , \gamma \rangle$ . The latent state <sup>??</sup> ∈ S contains the user preference distribution over I and the fixed observabil ity mask m. The agent does not maintain an explicit belief state; instead, the LLM conditions on the growing interaction history

$$
H _ {t} = (z _ {1}, a _ {1}, o _ {1}, \ldots , z _ {t}, a _ {t}, o _ {t}),
$$

where $z _ { t }$ is the reasoning trace, $a _ { t }$ is the structured tool action, and $o _ { t }$ is the returned observation. If action $a _ { t }$ queries a missing modal ity, the observation is deterministically <sup>??</sup>?? = Null. The environment state itself is static within an episode, so $\mathcal { P } ( s ^ { \prime } \mid s , a _ { t } ) = 1 [ s ^ { \prime } = s ]$ all adaptation comes from updating $H _ { t }$

At turn <sup>??</sup>, the LLM policy first emits a reasoning trace and then a single-line JSON action:

$$
z _ {t} \sim \pi_ {\theta} ^ {z} (z \mid H _ {t - 1}), \qquad a _ {t} \sim \pi_ {\theta} ^ {a} (a \mid H _ {t - 1}, z _ {t}).\tag{1}
$$

The action space is $\mathcal { A } = \mathcal { N } \times Q$ , where N is the tool name and $\boldsymbol { Q }$ is the JSON argument string. Invalid JSON or an unknown tool name incurs the invalid-action penalty in Eq. (3).

Evidence tools. MMA can call three automated tools and one optional interactive tool:

• Analyze\_Text(item\_id) returns normalized title, category, and truncated description fields; it returns Null if $m _ { \mathrm { t e x t } } = 0 .$

• Analyze\_Image(item\_id) runs a frozen CLIP-ViT-L/14 en coder and returns the top-5 zero-shot semantic tags; it returns Null if $m _ { \mathrm { i m g } } = 0$

• Retrieve\_Graph(user\_id) performs ANN search over a precomputed item–item collaborative graph and returns top co-purchased neighbor titles; it returns Null if $m _ { \mathrm { b e h } } = 0$

• Ask\_User(modality\_type, query) asks for clarification grounded only in surviving modalities. For example, OOMA-Visual responses are synthesized from CLIP tags, and OOMA Behavioral responses summarize graph-neighbor titles. Queries about a missing modality return Null. Because this tool converts non-text evidence into curated natural-language feedback, we use it only for MMA-Interactive upper-bound diagnostics.

This design makes missingness operational: a failed call is not silently ignored or imputed, but appended to $H _ { t }$ as evidence that should change subsequent tool choices.

## 3.3 Module 3: Candidate Scoring and Fusion

The terminal action is Score\_Candidates. It is deliberately not a single-item recommendation or retrieval action: MMA must output a JSON map from candidate item IDs to relevance scores $s _ { i } ^ { \mathrm { M M A } }$ allowing the evaluator to rerank the shared candidate pool while accounting for the first-stage retriever. Items outside $C _ { e }$ cannot be returned.

MMA scores are min–max normalized within $C _ { e }$ and fused with normalized first-stage scores:

$$
\hat {s} _ {i} = \alpha s _ {i} ^ {(0)} + (1 - \alpha) s _ {i} ^ {\mathrm{MMA}}.\tag{2}
$$

The fusion weight <sup>??</sup> is selected by validation-set grid search and then fixed for test evaluation. Candidates omitted from the terminal JSON keep their first-stage score and relative order. If the terminal JSON is malformed, the episode receives the invalid-action penalty and the evaluator falls back to the first-stage ranking for that episode. HR@<sup>??</sup> and NDCG@<sup>??</sup> are computed from the ranked list induced by $\hat { s } _ { i }$

Evaluation variants. MMA-Auto removes Ask\_User from the action set and is the primary automated method. MMA-Interactive keeps Ask\_User enabled and is reported only as an upper bound for settings where clarification is acceptable. Unless a result table explicitly says otherwise, claims about MMA refer to MMA-Auto.

Controlled LLM comparison. A single base LLM $L _ { 0 }$ (Llama-3-8B-Instruct, 8-bit quantized) is fixed across all agent variants. MMA-Auto, MMA-Interactive, MMA-SFT, MMA-Pooled, AgentCF, and ReAct share the same $L _ { 0 } ,$ , tokenizer, 2,048-token context bud-$\mathrm { g e t , }$ decoding temperature 0.0, and tool-schema prompts. MMA trains low-rank adaptation (LoRA) adapters $( r = 1 6 , \alpha = 3 2 )$ on q\_proj/v\_proj and a 2-layer value head $V _ { \phi }$ with hidden size 256; base weights remain frozen.

## 3.4 Module 4: Balanced Missingness-Task Training

Training should not be dominated by easy masks where most modalities are present. We therefore organize rollouts into missingnesstask families $\{ \mathcal { T } _ { k } \} _ { k = 1 } ^ { K }$ , each defined by a fixed mask distribution $P _ { k } ( { \mathbf { m } } )$ . The task index is a balancing and diagnostic device, not a claim of broad semantic multi-task transfer.

Table 1: Missingness-task families under leave-one-modalityout (LOMO). Each task is defined by a fixed mask m = [text<sup>,</sup> img<sup>,</sup> beh].

<table><tr><td>Family</td><td>Condition</td><td> $m_{\text{text}}$ </td><td> $m_{\text{img}}$ </td><td> $m_{\text{beh}}$ </td></tr><tr><td> $\mathcal{T}_{\text{full}}$ </td><td>All modalities available</td><td>1</td><td>1</td><td>1</td></tr><tr><td> $\mathcal{T}_{\text{no-text}}$ </td><td>Text missing (LOMO)</td><td>0</td><td>1</td><td>1</td></tr><tr><td> $\mathcal{T}_{\text{no-img}}$ </td><td>Image missing (LOMO)</td><td>1</td><td>0</td><td>1</td></tr><tr><td> $\mathcal{T}_{\text{cold-user}}$ </td><td>No behavioral history (LOMO)</td><td>1</td><td>1</td><td>0</td></tr><tr><td> $\mathcal{T}_{\text{text-only}}$ </td><td>Text only (OOMA)</td><td>1</td><td>0</td><td>0</td></tr><tr><td> $\mathcal{T}_{\text{img-only}}$ </td><td>Image only (OOMA-Visual)</td><td>0</td><td>1</td><td>0</td></tr><tr><td> $\mathcal{T}_{\text{beh-only}}$ </td><td>Behavioral only (OOMA-Beh)</td><td>0</td><td>0</td><td>1</td></tr></table>

Each task is split into support episodes $\mathcal { D } _ { k } ^ { s }$ (80%, used for policy updates) and query episodes $\mathcal { D } _ { k } ^ { q }$ (20%, used only for per-task diagnostics). Rollouts sample task families uniformly,

$$
p (\mathcal {T}) = \mathrm{Uniform} (\{\mathcal {T} _ {k} \} _ {k = 1} ^ {7}),
$$

so severe OOMA cases receive the same training exposure as easier fully observed or single-missing-modality cases.

Reward. The environment computes reward from the terminal ranking and step costs:

$$
\mathcal {R} _ {t} = \left\{ \begin{array}{l l} \text {NDCG@10} (\hat {\mathbf {r}}, i ^ {*}) & \text {if a_{t} = Score\_Candidates(\cdot)} \\ \lambda_ {\text {tool}} & a _ {t} \in \mathcal {A} _ {\text {tool}} \\ \lambda_ {\text {ask}} & a _ {t} = \text {Ask\_User(\cdot)} \\ \lambda_ {\text {invalid}} & \text {invalid JSON format or unknown tool name} \\ \lambda_ {\text {invalid}} & \text {repeated call to a Null -returning tool} \end{array} \right.\tag{3}
$$

Here rˆ is the ranking induced by Eq. (2), and <sup>??</sup> is the hidden target item. Unless stated otherwise, $\lambda _ { \mathrm { t o o l } } ~ = ~ - 0 . 0 2 , ~ \lambda _ { \mathrm { a s k } } ~ = ~ - 0 . 1 0 ,$ , and $\lambda _ { \mathrm { i n v a l i d } } = - 0 . 2 0$ . These costs encode a controlled implementation assumption: backend evidence lookup is cheap, user clarification is more expensive, and invalid retry loops are most expensive.

Policy optimization. Within an episode, MMA adapts only through context $H _ { t } ;$ no gradient update occurs at test time. During training, we optimize expected reward over support episodes:

$$
\max _ {\theta} \mathcal {J} (\theta) = \mathbb {E} _ {\mathcal {T} _ {k} \sim p (\mathcal {T})} \mathbb {E} _ {e \sim \mathcal {D} _ {k} ^ {s}} \left[ \sum_ {t = 1} ^ {T} \gamma^ {t} \mathcal {R} (i _ {e} ^ {*}, a _ {t}, H _ {t - 1}) \right].\tag{4}
$$

We use proximal policy optimization (PPO) with generalized ad vantage estimation:

$$
\hat {A} _ {t} = \sum_ {l = 0} ^ {T - t} (\gamma \lambda) ^ {l} \delta_ {t + l}, \quad \delta_ {t} = r _ {t} + \gamma V _ {\phi} (H _ {t + 1}) - V _ {\phi} (H _ {t}),\tag{5}
$$

and the clipped surrogate objective

$$
\mathcal {L} ^ {\mathrm{CLIP}} (\theta) = \hat {\mathbb {E}} _ {t} \left[ \min \left(\rho_ {t} (\theta) \hat {A} _ {t}, \operatorname{clip} \left(\rho_ {t} (\theta), 1 - \epsilon , 1 + \epsilon\right) \hat {A} _ {t}\right) \right],\tag{6}
$$

where <sup>??</sup> = 0<sup>.</sup>2 and

$$
\rho_ {t} (\theta) = \frac {\pi_ {\theta} (z _ {t} , a _ {t} \mid H _ {t - 1})}{\pi_ {\theta_ {\mathrm{old}}} (z _ {t} , a _ {t} \mid H _ {t - 1})}.
$$

Ablation anchors. MMA-Pooled uses the same PPO budget and mask augmentation but pools all masks into one rollout mixture without task-family balancing or per-task query diagnostics. MMA w/o Routing is the zero-shot ReAct anchor: $L _ { 0 }$ receives the tool schema but no supervised fine-tuning (SFT) or RL training. These controls separate the efects of tool access, supervised formatting, PPO learning, and balanced missingness exposure.

## 4 Experiments

We organize the evaluation around five questions:

• RQ1: Does the oracle-free MMA-Auto improve OOMA reranking over strong static completion baselines?

• RQ2: Does the OOMA advantage hold for text-only, imageonly, and behavior-only episodes?

• RQ3: Does the conclusion survive when a full-catalog first stage retriever supplies a fixed pool for reranking?

• RQ4: How much headroom is added by the idealized Ask\_User upper bound?

• RQ5: Does MMA outperform a deterministic router with identical tools and fusion, and what do routing diagnostics show?

Table 2: Dataset statistics. High sparsity makes cold-start conditions representative.

<table><tr><td>Dataset</td><td>#Users</td><td>#Items</td><td>#Inter.</td><td>Sparsity</td></tr><tr><td>Baby</td><td>19,445</td><td>7,050</td><td>160,792</td><td>99.88%</td></tr><tr><td>Sports</td><td>35,598</td><td>18,357</td><td>296,337</td><td>99.95%</td></tr><tr><td>Yelp</td><td>30,887</td><td>20,033</td><td>368,340</td><td>99.94%</td></tr></table>

## 4.1 Experimental Setup

Datasets. We evaluate on Amazon-Baby and Amazon-Sports [14], and Yelp (Yelp Open Dataset 2022 release). Amazon datasets provide text metadata, product images, and collaborative-filtering (CF) signals. For Yelp, text is drawn from item descriptions and review summaries; visual features are CLIP-ViT-L/14 embeddings of up to three business photos per venue; CF signals come from the user–business interaction graph. Data is split chronologically: the earliest 80% of interactions form training, the next 10% validation, and the most recent 10% test. Table 2 summarizes statistics.

Candidate-pool protocol. All methods are evaluated within the same target-positive <sup>??</sup>-item candidate pool per episode. The held-out target item is inserted, and the remaining <sup>??</sup> − 1 candidates are hard negatives retrieved from the surviving evidence source: BM25 for text-present settings, CLIP nearest-neighbor retrieval for image-only settings, and ANN graph retrieval for behavior-only settings. MMA acts only as a scorer and reranker over this pool; it does not recall additional items from the full catalog. This protocol isolates candidate scoring and reranking. Before target insertion, BM25 recall@100 is 83.4%, 80.1%, and 85.7% on Baby, Sports, and Yelp; CLIP recall@100 under OOMA-Visual is 76.3%, 74.8%, and 78.2%.

Baselines. (1) CF: LightGCN [5], SASRec [7]. (2) Multimodal CF: MMGCN [23], LRMM [18]; completely missing modalities are represented by zero-vectors under OOMA. (3) Completion and contrastive baselines: DGMRec [8], GRE-MC [11], and MACL [3]. DGMRec and GRE-MC are recommendation-specific completion baselines; MACL is included as a cross-domain missing-modality contrastive baseline rather than as a recommender-specialized method. (4) LLM agents: ReAct zero-shot [27], AgentCF [32], MMA-SFT, MMA-Pooled, MMA-Auto, and MMA-Interactive. All LLM-agent variants use the same base LLM, candidate pool, context budget, and scoring protocol from §3.3. (5) Deterministic router control: RuleRouter-Fuse uses the same candidate pool, automated evidence tools, turn budget, and validation-selected fusion rule as MMA-Auto, but replaces LLM reasoning and learned policy updates with a fixed routing order and deterministic evidence scorers. Concretely, it probes text, graph, and image tools in a fixed order, skips an evidence source after a Null return, and converts returned evidence into deterministic lexical, neighbor-overlap, and tag-overlap scores before applying the same fusion rule. It cannot access the hidden modality mask and observes missingness only through Null tool returns. This baseline isolates whether gains come from learned sequential routing rather than from tool access plus score fusion.

Implementation and metrics. Base LLM: Llama-3-8B-Instruct with 8-bit quantisation and LoRA (<sup>??</sup>=16, <sup>??</sup>=32) on q\_proj/v\_proj.

Table 3: Oracle-free OOMA NDCG@10. MMA-Auto disables Ask\_User; relative gains are against the stronger static baseline in each row.

<table><tr><td>Dataset</td><td>DGMRec</td><td>GRE-MC</td><td>MMA-Auto</td><td>Rel. gain</td></tr><tr><td>Baby</td><td> $0.1848_{\pm .0088}$ </td><td> $0.1800_{\pm .0096}$ </td><td> $0.1912_{\pm .0116}$ </td><td>3.5%</td></tr><tr><td>Sports</td><td> $0.1664_{\pm .0080}$ </td><td> $0.1600_{\pm .0096}$ </td><td> $0.1730_{\pm .0104}$ </td><td>4.0%</td></tr><tr><td>Yelp</td><td> $0.1424_{\pm .0072}$ </td><td> $0.1344_{\pm .0096}$ </td><td> $0.1492_{\pm .0096}$ </td><td>4.8%</td></tr><tr><td>Avg.</td><td>0.1645</td><td>0.1581</td><td>0.1711</td><td>4.0%</td></tr></table>

PPO uses lr $1 \times 1 0 ^ { - 5 }$ , batch 64, clip $\scriptstyle \epsilon = 0 . 2 , \mathrm { G A E } \lambda = 0 . 9 5 , T = 8$ turns, and 500 iterations. The fusion weight in Eq. (2) is selected on validation data and then fixed for test evaluation. Primary metrics are HR@<sup>??</sup> and NDCG@<sup>??</sup> for $K \in \{ 1 0 , 2 0 \}$ ; all reported main values are mean ± std over 5 seeds. Statistical significance is tested with paired Wilcoxon signed-rank tests over matched test episodes within each dataset, and Clif’s <sup>??</sup> reports efect size.

## 4.2 Oracle-Free OOMA Main Result (RQ1)

Table 3 is the primary deployment-facing result. MMA-Auto dis ables Ask\_User, so its improvement must come from automated routing, candidate scoring, and fusion with the first-stage retriever score. MMA-Auto improves average OOMA NDCG@10 by 4<sup>.</sup>0% over DGMRec, the strongest static baseline in this setting.

The improvement is small in absolute NDCG but stable across domains: MMA-Auto gains +0<sup>.</sup>0064, +0<sup>.</sup>0066, and +0<sup>.</sup>0068 NDCG@10 on Baby, Sports, and Yelp, respectively. This pattern matters because the three datasets have diferent evidence profiles: Amazon products have structured text and product images, while Yelp relies more heavily on review text and venue photos. DGMRec is con sistently stronger than GRE-MC in this oracle-free setting, so the comparison uses DGMRec as the main static reference point. The result therefore supports a narrow deployment claim: given the same candidate pool and no user clarification, learned evidence routing provides a consistent reranking gain over strong completion-based scoring.

The magnitude should be interpreted in light of the protocol. The target-positive pool contains hard negatives retrieved from the surviving modality, so the task is not to find an obviously relevant item but to reorder plausible candidates when one or more modalities are absent. Under this setting, a reranker that merely retries missing tools or overuses a single modality has little room to improve. MMA-Auto’s gains are therefore evidence for better use of surviving evidence, not evidence that the model solves full-catalog retrieval.

## 4.3 Per-Modality OOMA Breakdown (RQ2)

Table 4 shows that the routing advantage is not concentrated in a single favorable surviving modality. MMA-Auto wins all 9 dataset– modality OOMA cells against the stronger of DGMRec and GRE-MC. The margins are modest in absolute NDCG, but the consistency across text-only, image-only, and behavior-only settings supports the missingness-routing mechanism.

The breakdown clarifies where the main result comes from. Textonly episodes have the highest absolute NDCG because item titles, categories, and descriptions directly expose semantic relevance. Image-only episodes are harder in absolute terms, but they show some of the largest relative gains over DGMRec: +5<sup>.</sup>7% on Sports and +6<sup>.</sup>5% on Yelp. This is consistent with the design of MMA-Auto: once text and behavior queries return Null, the policy can switch to image evidence and score candidates from visual tags instead of relying on zero-filled or reconstructed features.

Behavior-only episodes give a diferent signal. The absolute scores are closer to text-only than image-only, especially on Amazon, because graph-neighbor summaries often carry strong collaborative hints. MMA-Auto still improves these cells, but the relative gains are smaller than the image-only gains on Sports and Yelp. This suggests that the agent is not simply benefiting from one dominant tool. Instead, the policy learns to treat Null observations as routing information and to use whichever surviving evidence source is available. The fact that all 9 cells improve is more important than any single cell’s margin, because OOMA deployment failures are defined by changing missingness patterns rather than by a fixed missing modality.

## 4.4 Fixed-Pool Full-Catalog Reranking (RQ3)

The target-positive protocol controls reranking dificulty but inserts the target by construction. Table 5 therefore evaluates a fullcatalog first-stage retriever followed by fixed-pool reranking under OOMA. MMA-Auto reranks the same first-stage retrieved pool as the strongest non-interactive static pipeline; identical Recall@100 is expected. The relevant claim is a fixed-pool reranking gain, not an end-to-end retrieval gain.

Average NDCG@10 increases from 0<sup>.</sup>0178 to 0<sup>.</sup>0201, the mean per-dataset relative NDCG@10 gain is 12<sup>.</sup>7%, and average HR@10 increases from 0<sup>.</sup>0385 to 0<sup>.</sup>0427. Recall@100 is identical by construction, so the table isolates ordering quality inside the fixed retrieved pool. The absolute NDCG values are much lower than in the targetpositive setting because the first-stage retriever must first include the target item from the full catalog before MMA can rerank it. This is the expected behavior for a third-stage scorer: it can improve the order of available candidates, but it cannot recover items that the first-stage retriever failed to recall.

This experiment is therefore a stress test for the paper’s scope. If MMA-Auto improved only in target-positive pools, the main result could be dismissed as an artifact of target insertion. The full-catalog check shows that the learned scoring signal still improves top-10 ordering when the candidate pool is produced by a realistic firststage retrieval process. At the same time, the unchanged Recall@100 keeps the claim disciplined: MMA-Auto is a fixed-pool reranker, not a replacement for retrieval.

## 4.5 Interactive Upper Bound (RQ4)

MMA-Interactive keeps Ask\_User enabled. Since this tool converts surviving text, image tags, or graph-neighbor evidence into LLMfriendly clarification, it is an idealized upper bound rather than the deployment claim. Fig. 2a reports the headroom over MMA-Auto without using it as the main result.

The interactive variant adds a consistent but bounded amount of headroom: average NDCG@10 rises from 0<sup>.</sup>1711 for MMA-Auto to 0<sup>.</sup>1781 for MMA-Interactive, a 4<sup>.</sup>1% gain over the automated agent and an 8<sup>.</sup>3% gain over DGMRec. The per-dataset increments over MMA-Auto are similar (+0<sup>.</sup>0072, +0<sup>.</sup>0070, and +0<sup>.</sup>0068), which sug gests that clarification mainly provides additional disambiguating evidence rather than changing the overall ranking mechanism.

Table 4: Per-modality OOMA NDCG@10 under the target-positive 100-item protocol. Each cell reports mean ± std over 5 seeds.

<table><tr><td>Dataset</td><td>Method</td><td>Text-only</td><td>Image-only</td><td>Behavior-only</td><td>Avg. OOMA</td></tr><tr><td>Baby</td><td>DGMRec</td><td> $0.2016_{\pm .0092}$ </td><td> $0.1620_{\pm .0080}$ </td><td> $0.1908_{\pm .0088}$ </td><td> $0.1848_{\pm .0088}$ </td></tr><tr><td>Baby</td><td>GRE-MC</td><td> $0.1940_{\pm .0096}$ </td><td> $0.1580_{\pm .0084}$ </td><td> $0.1880_{\pm .0092}$ </td><td> $0.1800_{\pm .0096}$ </td></tr><tr><td>Baby</td><td>MMA-Auto</td><td> $0.2084_{\pm .0112}$ </td><td> $0.1668_{\pm .0104}$ </td><td> $0.1984_{\pm .0108}$ </td><td> $0.1912_{\pm .0116}$ </td></tr><tr><td>Sports</td><td>DGMRec</td><td> $0.1820_{\pm .0088}$ </td><td> $0.1440_{\pm .0076}$ </td><td> $0.1732_{\pm .0084}$ </td><td> $0.1664_{\pm .0080}$ </td></tr><tr><td>Sports</td><td>GRE-MC</td><td> $0.1748_{\pm .0092}$ </td><td> $0.1384_{\pm .0080}$ </td><td> $0.1668_{\pm .0088}$ </td><td> $0.1600_{\pm .0096}$ </td></tr><tr><td>Sports</td><td>MMA-Auto</td><td> $0.1888_{\pm .0104}$ </td><td> $0.1522_{\pm .0096}$ </td><td> $0.1780_{\pm .0100}$ </td><td> $0.1730_{\pm .0104}$ </td></tr><tr><td>Yelp</td><td>DGMRec</td><td> $0.1560_{\pm .0080}$ </td><td> $0.1240_{\pm .0068}$ </td><td> $0.1472_{\pm .0076}$ </td><td> $0.1424_{\pm .0072}$ </td></tr><tr><td>Yelp</td><td>GRE-MC</td><td> $0.1480_{\pm .0088}$ </td><td> $0.1160_{\pm .0072}$ </td><td> $0.1392_{\pm .0080}$ </td><td> $0.1344_{\pm .0096}$ </td></tr><tr><td>Yelp</td><td>MMA-Auto</td><td> $0.1628_{\pm .0096}$ </td><td> $0.1320_{\pm .0088}$ </td><td> $0.1528_{\pm .0092}$ </td><td> $0.1492_{\pm .0096}$ </td></tr></table>

Table 5: Full-catalog reranking with a fixed first-stage retrieved pool under OOMA. Recall@100 is identical by con struction.

<table><tr><td>Dataset</td><td>Method</td><td>Recall@100</td><td>HR@10</td><td>NDCG@10</td></tr><tr><td>Baby</td><td>Static</td><td>0.5420</td><td>0.0460</td><td>0.0212</td></tr><tr><td>Baby</td><td>MMA-Auto</td><td>0.5420</td><td>0.0512</td><td>0.0238</td></tr><tr><td>Sports</td><td>Static</td><td>0.4980</td><td>0.0384</td><td>0.0180</td></tr><tr><td>Sports</td><td>MMA-Auto</td><td>0.4980</td><td>0.0426</td><td>0.0204</td></tr><tr><td>Yelp</td><td>Static</td><td>0.5612</td><td>0.0310</td><td>0.0142</td></tr><tr><td>Yelp</td><td>MMA-Auto</td><td>0.5612</td><td>0.0344</td><td>0.0160</td></tr><tr><td>Avg.</td><td>Static</td><td>0.5337</td><td>0.0385</td><td>0.0178</td></tr><tr><td>Avg.</td><td>MMA-Auto</td><td>0.5337</td><td>0.0427</td><td>0.0201</td></tr></table>

![](images/6d3d8c56c660c32ad295b269fd54b6fc43db6de9aeac59455505452da18fcc10.jpg)  
(a) Interactive upper-bound

![](images/861ad01fb35d3f232e8ce6f8e473f9ff408fa2a97415171a743999352a28f3e1.jpg)  
(b) OOMA ablation  
Figure 2: Performance and ablation analysis on OOMA NDCG@10. (a) Interactive upper-bound where MMA Interactive keeps Ask\_User enabled. (b) Ablation study re sults (mean ± std, 5 seeds) showing MMA-Interactive as an upper bound.

We keep this result separate from the main claim for two reasons. First, the clarification tool is idealized: responses are synthesized from surviving evidence rather than collected from real users under noisy interaction. Second, user interaction changes the deployment contract and cost model. The result is useful as a diagnostic upper bound because it estimates how much information is still missing after automated routing, but MMA-Auto remains the primary evidence for oracle-free reranking.

Table 6: Paired significance tests on target-positive OOMA NDCG@10. Tests are paired over matched held-out test episodes within each dataset.

<table><tr><td>Dataset</td><td>Comparison</td><td>Mean delta</td><td>Wilcoxon p</td><td>Cliff&#x27;s δ</td></tr><tr><td>Baby</td><td>MMA-Auto vs DGMRec</td><td>+0.0064</td><td>0.021</td><td>0.18</td></tr><tr><td>Sports</td><td>MMA-Auto vs DGMRec</td><td>+0.0066</td><td>0.034</td><td>0.15</td></tr><tr><td>Yelp</td><td>MMA-Auto vs DGMRec</td><td>+0.0068</td><td>0.018</td><td>0.19</td></tr><tr><td>Avg.</td><td>MMA-Auto vs DGMRec</td><td>+0.0066</td><td>-</td><td>-</td></tr></table>

## 4.6 Mechanism, Significance, and Cost (RQ5)

Table 6 prevents small mean margins from being over-interpreted. The results are statistically supported but have modest efect sizes, matching our claim of robust routing rather than a large-margin accuracy breakthrough.

The paired tests address a common risk in reranking papers: small NDCG changes can be unstable if diferent methods succeed on diferent episodes. Here, all three datasets pass paired Wilcoxon tests at $\textit { p } < 0 . 0 5$ , but Clif’s <sup>??</sup> remains modest (0<sup>.</sup>15–0<sup>.</sup>19). This combination is important for the claim calibration. The efect is systematic under matched test episodes, yet it should be described as a robust reranking improvement rather than a large-margin accuracy breakthrough.

The Fig. 2b explains which parts of the system are necessary. The zero-shot ReAct anchor performs worst, showing that prompt-only tool access is insuficient under structural missingness. MMA-SFT improves average NDCG@10 from 0<sup>.</sup>0928 to 0<sup>.</sup>1421, indicating that supervised exposure to the tool schema and scoring format is useful but incomplete. PPO-based variants then move the model into the 0<sup>.</sup>171 range by rewarding successful terminal rankings and penalizing invalid or repeated failed calls. This supports the training story: the agent needs experience with failed evidence paths, not just natural-language instructions about tools.

MMA-Auto and MMA-Pooled are close on average (0<sup>.</sup>1711 vs. 0<sup>.</sup>1709), so we do not present task indexing as a large standalone algorithmic leap. Its role is more conservative: balanced missingnesstask training prevents the policy from being dominated by easy fully observed or single-missing episodes, and the task index gives a diagnostic handle for per-condition behavior. This framing keeps the method claim aligned with the observed margins.

Table 7: Deterministic-router control under target-positive OOMA. RuleRouter-Fuse uses the same tools and fusion protocol as MMA-Auto but no LLM policy or PPO training.

<table><tr><td>Dataset / metric</td><td>DGMRec</td><td>RuleRouter-Fuse</td><td>MMA-Auto</td><td>MMA diff.</td></tr><tr><td>Baby</td><td>0.1848</td><td>0.1765</td><td>0.1912</td><td>+0.0147</td></tr><tr><td>Sports</td><td>0.1664</td><td>0.1592</td><td>0.1730</td><td>+0.0138</td></tr><tr><td>Yelp</td><td>0.1424</td><td>0.1378</td><td>0.1492</td><td>+0.0114</td></tr><tr><td>Avg.</td><td>0.1645</td><td>0.1578</td><td>0.1711</td><td>+0.0133</td></tr><tr><td>Avg. failed-call rate</td><td>-</td><td>65.8%</td><td>47.0%</td><td>-18.8 pp</td></tr><tr><td>Avg. turns</td><td>-</td><td>3.8</td><td>2.5</td><td>-1.3</td></tr></table>

Appendix A reports recovery rate, failed-call rate, turns to success, and first-action routing by OOMA subcondition. These trajectories support the mechanism analysis, though they do not by themselves prove general reasoning beyond the trained environ ment.

Mechanism: learned routing. RuleRouter-Fuse controls for the strongest non-agent explanation of MMA-Auto: access to the same evidence tools and the same first-stage fusion rule. If MMA-Auto exceeds RuleRouter-Fuse while using a comparable or lower failed call rate, the remaining gain suggests learned sequential routing rather than tool access alone. As shown in Table 7, MMA-Auto consistently outperforms RuleRouter-Fuse across all three datasets, with average NDCG@10 increasing from 0.1578 to 0.1711, a relative gain of 8.4%. RuleRouter-Fuse also falls below DGMRec on each dataset, suggesting that fixed routing is brittle under OOMA.

The diagnostics explain why this happens. The deterministic router has a higher failed-call rate (65.8% vs. 47.0%) and needs more turns per episode (3.8 vs. 2.5). A fixed order can waste calls when the surviving modality difers from its preferred path; after a Null return, it has limited ability to decide whether another candidatelevel query is still useful. MMA-Auto instead conditions later actions on the accumulated interaction history, so a failed call can become evidence for switching tools or terminating with the current score map. This does not prove general reasoning beyond the trained environment, but it supports the narrower mechanism claim that learned routing adds value beyond deterministic tool fusion.

Accuracy-latency trade-of. Agentic recommenders incur higher inference latency than static single-pass models. Appendix A reports latency, memory, and FLOPs. The observed gains should therefore be read as an accuracy-latency trade-of: MMA-Auto improves target-positive OOMA NDCG@10 by 4<sup>.</sup>0%, while MMA-Interactive improves it by 8<sup>.</sup>3% relative to DGMRec.

## 5 Conclusion and Limitations

We introduced the Meta-Modal Agent, a candidate-pool reranking framework that reframes missing modalities in cold-start recom mendation from a static representation learning task to a sequential evidence-routing problem. MMA operates after first-stage retrieval: it scores a shared candidate pool and fuses agent scores with first stage retrieval scores, making HR and NDCG evaluation explicit. The evaluation separates the automated deployment setting from the interactive upper bound: MMA-Auto disables Ask\_User, while MMA-Interactive keeps clarification available only for diagnostic analysis. Across the automated evidence chain, MMA-Auto wins all 9 dataset–modality OOMA cells against the strongest static baseline, improves target-positive OOMA NDCG@10 by 4<sup>.</sup>0%, achieves a 12<sup>.</sup>7% mean per-dataset relative NDCG@10 gain in fixed-pool full-catalog reranking, improves over the RuleRouter-Fuse deterministic control from 0.1578 to 0.1711 average OOMA NDCG@10, and reaches <sup>?? <</sup> 0<sup>.</sup>05 on all three datasets with modest but positive efect sizes. MMA-Interactive adds a 4<sup>.</sup>1% upper-bound gain over MMA-Auto when clarification is available.

## Appendix

## A Implementation, Routing, and Cost Details

Table 8 summarizes the main implementation settings and inference cost. Agentic inference is substantially slower than static baselines, so the gains in the main text should be read as an accuracy-latency trade-of.

Table 8: Key implementation settings and per-query inference cost on one NVIDIA A100 GPU. GAE is generalized advantage estimation; FLOPs is floating-point operations.

<div class="mineru-algorithm" style="white-space: pre-wrap; font-family:monospace;">
Item Value
Base LLM Llama-3-8B-Instruct, 8-bit
Trainable parameters LoRA on q_proj/v_proj, r = 16,  $\alpha = 32$ ; 2-layer value head
Optimization PPO, lr  $1 \times 10^{-5}$ , batch 64, clip  $\epsilon = 0.2$ , GAE  $\lambda = 0.95$ , 500 iterations
Episode budget T = 8 turns; 2048-token context; train temperature 0.2, eval temperature 0.0
Reranking MMA scores fused with first-stage retrieval scores; fusion weight selected on validation split
Static cost DGMRec: 0.012 s / 2.1 GB /  $1.2 \times 10^{9}$  FLOPs; GRE-MC: 0.015 s / 2.8 GB /  $1.8 \times 10^{9}$  FLOPs
MMA-Interactive cost 1.250 s / 8.6 GB /  $8.2 \times 10^{11}$  FLOPs; 3.9 forward passes on average
</div>

To examine internal routing quality, Table 9 reports MMA-Auto behavior by OOMA subcondition. The first-action rate is measured for the expected surviving-modality tool: Analyze\_Text on text-only episodes, Analyze\_Image on image-only episodes, and Retrieve\_Graph on behavior-only episodes.

Table 9: MMA-Auto agentic metrics and expected first-action routing rates by OOMA subcondition.

<table><tr><td>Dataset</td><td>OOMA subset</td><td>Recovery</td><td>Failed calls</td><td>TTS</td><td>First-action rate</td></tr><tr><td>Baby</td><td>Text-only</td><td>64.2%</td><td>42.1%</td><td>2.4</td><td>88.4%</td></tr><tr><td>Baby</td><td>Image-only</td><td>58.6%</td><td>48.5%</td><td>2.6</td><td>82.1%</td></tr><tr><td>Baby</td><td>Behavior-only</td><td>61.0%</td><td>45.2%</td><td>2.5</td><td>85.6%</td></tr><tr><td>Sports</td><td>Text-only</td><td>62.8%</td><td>43.0%</td><td>2.4</td><td>87.2%</td></tr><tr><td>Sports</td><td>Image-only</td><td>56.4%</td><td>50.1%</td><td>2.7</td><td>80.5%</td></tr><tr><td>Sports</td><td>Behavior-only</td><td>59.2%</td><td>46.8%</td><td>2.5</td><td>84.0%</td></tr><tr><td>Yelp</td><td>Text-only</td><td>59.5%</td><td>46.2%</td><td>2.5</td><td>85.1%</td></tr><tr><td>Yelp</td><td>Image-only</td><td>54.2%</td><td>52.4%</td><td>2.8</td><td>78.6%</td></tr><tr><td>Yelp</td><td>Behavior-only</td><td>57.8%</td><td>48.6%</td><td>2.6</td><td>82.4%</td></tr></table>

## GenAI Usage Disclosure

Generative AI tools were used for language editing and consistency checking of the manuscript.

## References

[1] Keqin Bao, Jizhi Zhang, Yang Zhang, Wang Wenjie, Fuli Feng, and Xiangnan He. 2023. Large language models for recommendation: Progresses and future directions. In Proceedings of the Annual International ACM SIGIR Conference on Research and Development in Information Retrieval in the Asia Pacific Region. 306–309.

[2] Ruiting Dai, Zheyu Wang, Haoyu Yang, Yihan Liu, Chengzhi Wang, Zekun Zhang, Zishan Huang, Jiaman Cen, and Lisi Mo. 2026. OMG-Agent: Toward Robust Missing Modality Generation with Decoupled Coarse-to-Fine Agentic Workflows. arXiv preprint arXiv:2602.04144 (2026).

[3] Sam Dixon, Lina Yao, and Robert Davidson. 2024. Modality aware contrastive learning for multimodal human activity recognition. Concurrency and Computation: Practice and Experience 36, 16 (2024), e8020.

[4] Chelsea Finn, Pieter Abbeel, and Sergey Levine. 2017. Model-agnostic meta learning for fast adaptation of deep networks. In International conference on machine learning. PMLR, 1126–1135.

[5] Xiangnan He, Kuan Deng, Xiang Wang, Yan Li, Yongdong Zhang, and Meng Wang. 2020. Lightgcn: Simplifying and powering graph convolution network for recommendation. In Proceedings of the 43rd International ACM SIGIR conference on research and development in Information Retrieval. 639–648.

[6] Yupeng Hou, Shanlei Mu, Wayne Xin Zhao, Yaliang Li, Bolin Ding, and Ji-Rong Wen. 2022. Towards universal sequence representation learning for recommender systems. In Proceedings of the 28th ACM SIGKDD conference on knowledge discovery and data mining. 585–593.

[7] Wang-Cheng Kang and Julian McAuley. 2018. Self-attentive sequential recom mendation. In 2018 IEEE international conference on data mining (ICDM). IEEE, 197–206.

[8] Jiwan Kim, Hongseok Kang, Sein Kim, Kibum Kim, and Chanyoung Park. 2025. Disentangling and generating modalities for recommendation in missing modal ity scenarios. In Proceedings of the 48th International ACM SIGIR Conference on Research and Development in Information Retrieval. 1820–1829.

[9] Hoyeop Lee, Jinbae Im, Seongwon Jang, Hyunsouk Cho, and Sehee Chung. 2019. Melu: Meta-learned user preference estimator for cold-start recommendation. In Proceedings of the 25th ACM SIGKDD international conference on knowledge discovery & data mining. 1073–1082.

[10] Wenqiang Lei, Xiangnan He, Yisong Miao, Qingyun Wu, Richang Hong, Min Yen Kan, and Tat-Seng Chua. 2020. Estimation-action-reflection: Towards deep interaction between conversational and recommender systems. In Proceedings of the 13th international conference on web search and data mining. 304–312.

[11] Yuan Li, Jun Hu, Jiaxin Jiang, Bryan Hooi, and Bingsheng He. 2026. Robust Mul timodal Recommendation via Graph Retrieval-Enhanced Modality Completion. arXiv preprint arXiv:2605.00670 (2026).

[12] Qidong Liu, Jiaxi Hu, Yutian Xiao, Xiangyu Zhao, Jingtong Gao, Wanyu Wang, Qing Li, and Jiliang Tang. 2024. Multimodal recommender systems: A survey. Comput. Surveys 57, 2 (2024), 1–17.

[13] Daniele Malitesta, Emanuele Rossi, Claudio Pomo, Tommaso Di Noia, and Fragkiskos D Malliaros. 2024. Do we really need to drop items with missing modalities in multimodal recommendation?. In Proceedings of the 33rd ACM International Conference on Information and Knowledge Management. 3943–3948.

[14] Julian McAuley, Christopher Targett, Qinfeng Shi, and Anton Van Den Hengel. 2015. Image-based recommendations on styles and substitutes. In Proceedings of the 38th international ACM SIGIR conference on research and development in information retrieval. 43–52.

[15] Xingyu Pan, Yushuo Chen, Changxin Tian, Zihan Lin, Jinpeng Wang, He Hu, and Wayne Xin Zhao. 2022. Multimodal meta-learning for cold-start sequential recommendation. In Proceedings of the 31st ACM international conference on information & knowledge management. 3421–3430.

[16] Yujia Qin, Shihao Liang, Yining Ye, Kunlun Zhu, Lan Yan, Yaxi Lu, Yankai Lin, Xin Cong, Xiangru Tang, Bill Qian, et al. 2024. Toolllm: Facilitating large language models to master 16000+ real-world apis. In International Conference on Learning Representations, Vol. 2024. 9695–9717.

[17] Xubin Ren, Wei Wei, Lianghao Xia, Lixin Su, Suqi Cheng, Junfeng Wang, Dawei Yin, and Chao Huang. 2024. Representation learning with large language models for recommendation. In Proceedings of the ACM web conference 2024. 3464–3475.

[18] Cheng Wang, Mathias Niepert, and Hui Li. 2018. LRMM: Learning to recommend with missing modalities. In Proceedings of the 2018 conference on empirical methods in natural language processing. 3360–3370.

[19] Jinze Wang, Yangchen Zeng, Tiehua Zhang, Lu Zhang, Yuze Liu, Yongchao Liu, Xingjun Ma, and Zhu Sun. 2026. Agent4POI: Agentic Context-Conditioned Afordance Reasoning for Multimodal Point-of-Interest Recommendation. arXiv preprint arXiv:2605.15203 (2026).

[20] Jinze Wang, Lu Zhang, Yiyang Cui, Tiehua Zhang, Zhishu Shen, Yuze Liu, Xingjun Ma, and Jiong Jin. 2025. Do we really need sft? prompt-as-policy over knowledge graphs for cold-start next poi recommendation. arXiv preprint arXiv:2510.08012 (2025).

[21] Jinze Wang, Lu Zhang, Zhu Sun, and Yew-Soon Ong. 2023. Meta-learning enhanced next POI recommendation by leveraging check-ins from auxiliary cities. In Pacific-Asia Conference on Knowledge Discovery and Data Mining. Springer, 322–334.

[22] Jinze Wang, Tiehua Zhang, Lu Zhang, Yang Bai, Xin Li, and Jiong Jin. 2025. HyperMAN: Hypergraph-enhanced Meta-learning Adaptive Network for Next POI Recommendation. In 2025 IEEE International Conference on Multimedia and Expo (ICME). IEEE, 1–6.

[23] Yinwei Wei, Xiang Wang, Liqiang Nie, Xiangnan He, Richang Hong, and Tat-Seng Chua. 2019. MMGCN: Multi-modal graph convolution network for personalized recommendation of micro-video. In Proceedings of the 27th ACM international conference on multimedia. 1437–1445.

[24] Renjie Wu, Hu Wang, Hsiang-Ting Chen, and Gustavo Carneiro. 2024. Deep multimodal learning with missing modality: A survey. arXiv preprint arXiv:2409.07825 (2024).

[25] Xin Xin, Alexandros Karatzoglou, Ioannis Arapakis, and Joemon M Jose. 2020. Self-supervised reinforcement learning for recommender systems. In Proceedings of the 43rd International ACM SIGIR conference on research and development in Information Retrieval. 931–940.

[26] Wei Yang and Qingchen Yang. 2024. Multimodal-aware multi-intention learning for recommendation. In Proceedings of the 32nd ACM International Conference on Multimedia. 5663–5672.

[27] Shunyu Yao, Jefrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, and Yuan Cao. 2022. React: Synergizing reasoning and acting in language models. arXiv preprint arXiv:2210.03629 (2022).

[28] Zhenrui Yue, Sara Rabhi, Gabriel de Souza Pereira Moreira, Dong Wang, and Even Oldridge. 2023. Llamarec: Two-stage recommendation using large language models for ranking. arXiv preprint arXiv:2311.02089 (2023).

[29] Yagchen Zeng. 2026. Deep Interest Mining with Cross-Modal Alignment for SemanticID Generation in Generative Recommendation. arXiv preprint arXiv:2604.20861 (2026).

[30] Yangchen Zeng, Hao Peng, Rongfeng Guo, Zhenyu Yu, Zhiyuan Hu, and Jinze Wang. 2026. TriAlignGR: Triangular Multitask Alignment with Multimodal Deep Interest Mining for Generative Recommendation. arXiv preprint arXiv:2605.05249 (2026).

[31] An Zhang, Yuxin Chen, Leheng Sheng, Xiang Wang, and Tat-Seng Chua. 2024. On generative agents in recommendation. In Proceedings of the 47th international ACM SIGIR conference on research and development in Information Retrieval. 1807– 1817.

[32] Junjie Zhang, Yupeng Hou, Ruobing Xie, Wenqi Sun, Julian McAuley, Wayne Xin Zhao, Leyu Lin, and Ji-Rong Wen. 2024. Agentcf: Collaborative learning with autonomous language agents for recommender systems. In Proceedings of the ACM Web Conference 2024. 3679–3689.

[33] Junjie Zhang, Ruobing Xie, Yupeng Hou, Wayne Xin Zhao, Leyu Lin, and Ji-Rong Wen. 2026. Recommendation as instruction following: A large language model empowered recommendation approach. ACM Transactions on Information Systems 43, 5 (2026), 1–37.


---

# 2407.18940_LitSearch_A_Retrieval_Benchmark_for_Scientific_Literature_Search

[2407.18940](https://arxiv.org/abs/2407.18940)

# LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith<sup>1</sup> Mengzhou Xia<sup>1</sup> Alexis Chevalier<sup>1,2</sup> Tanya Goyal<sup>1</sup>

Danqi Chen<sup>1</sup> Tianyu Gao<sup>1</sup>

<sup>1</sup>Princeton Language and Intelligence (PLI), Princeton University <sup>2</sup>BCG X {anirudh.ajith,mengzhou,achevalier,tanyagoyal, danqic,tianyug}@princeton.edu

## Abstract

Literature search questions, such as “Where can I find research on the evaluation of consistency in generated summaries?” pose significant challenges for modern search engines and retrieval systems. These questions often require a deep understanding of research concepts and the ability to reason across entire articles. In this work, we introduce LitSearch, a retrieval benchmark comprising 597 realistic literature search queries about recent ML and NLP papers. Lit-Search is constructed using a combination of (1) questions generated by GPT-4 based on paragraphs containing inline citations from research papers and (2) questions manually written by authors about their recently published papers. All LitSearch questions were manually examined or edited by experts to ensure high quality. We extensively benchmark state-ofthe-art retrieval models and also evaluate two LLM-based reranking pipelines. We find a significant performance gap between BM25 and state-of-the-art dense retrievers, with a 24.8% absolute difference in recall@5. The LLMbased reranking strategies further improve the best-performing dense retriever by 4.4%. Additionally, commercial search engines and research tools like Google Search perform poorly on LitSearch, lagging behind the best dense retriever by up to 32 recall points. Taken together, these results show that LitSearch is an informative new testbed for retrieval systems while catering to a real-world use case.<sup>1</sup>

## 1 Introduction

Finding literature via a specific search query—for example, collecting related work, checking if a method has been proposed before, or recalling a previously seen paper—is a critical task for researchers. Developing systems that recommend citations pertinent to such inquiries holds the po tential to enhance researchers’ productivity and expedite scientific discovery (Färber and Jatowt, 2020). However, this task is inherently challenging as it often requires deep domain expertise and reasoning through lengthy papers.

![](images/72725446d36f5f2bb64f36e22f570b68a26e9956c582eacfb3962e559c4e0afd.jpg)  
Figure 1: Examples of inline-citation and author-written questions from LitSearch. These questions are often challenging and require a deep understanding of the target papers to answer correctly.

Prior to this study, the task of citation recommendation was often formalized by using inline citation mentions from existing papers as queries, and the cited papers as targets (He et al., 2010; Gu et al., 2022). For instance, given the citation mention “RoBERTa and T5 are based on recent advances in masked language modeling [citation],” the text surrounding the citation mention is used as a retrieval query, and the cited paper is the target literature. However, directly using inline citations often leads to queries that are noisy, overly broad (e.g., “Large Language Models [citation]”), or highly context-dependent (e.g., “We follow the hyperparameters of [citation]”).

![](images/a3d1536b7391a8bb8e251cc0e72e50fb1317941abdc561d15de6d46dc6bb9c60.jpg)  
Figure 2: The pipeline for generating inline-citation questions. We first sample a citation mention and prompt GPT-4 to generate a question. Next, we filter questions based on word overlap with the target paper title and perform manual inspections to annotate their specificity and quality (see rubrics in Table 1).

In this work, we propose a new literature retrieval benchmark called LitSearch. As illustrated in Figure 1, a literature search question seeks papers that meet specific criteria, closely reflecting actual research workflows. LitSearch consists of two subsets: (1) For inline-citation questions, we sample citation mentions from a collection of scientific papers and use GPT-4 (OpenAI, 2023) to rewrite them into literature search questions (Figure 2). We retain questions with a low word overlap with the title of the target papers, and perform manual examination to ensure high quality. (2) For author-written questions, we invited authors of ACL 2023 and ICLR 2024 papers to write literature search questions for their own papers. This subset is also manually examined and filtered to remove any inaccurate or easy questions. LitSearch contains 597 questions in total, each paired with one or more scientific papers as the ground truth.

LitSearch has several unique characteristics: (1) To the best of our knowledge, LitSearch is the first dataset featuring realistic literature search questions, providing a new testbed for citation recommendation and retrieval systems. (2) LitSearch is challenging, requiring deep understanding and reasoning over entire articles. The average document length (6,041/134 words for full texts/titles and abstracts) is significantly longer than that of most existing retrieval benchmarks (e.g., 56 for (Nguyen et al., 2017)). (3) LitSearch is of high quality, with all questions manually examined by the authors.

We conduct extensive experiments on both stateof-the-art retrieval models and reranking with large language models (LLMs). On LitSearch, the best dense retrieval model, GritLM (Muennighoff et al., 2024), achieves an average recall@5 of 74.8%, outperforming BM25 (Robertson et al., 2009) by 24.8%. The recall@5 of GritLM is further improved by 4.4% with GPT-4o reranking. On the other hand, commercial search engines and research tools like Google Search perform poorly on this task, only achieving an average recall@5 of 42.8% at most. Furthermore, compared to existing retrieval datasets from BEIR (Thakur et al., 2021) and MTEB (Muennighoff et al., 2022), Lit-Search effectively reflects the performance differences among various embedding models, making it an informative testbed for evaluating state-of-theart retrieval systems.

## 2 LitSearch

Our benchmark LitSearch consists of (a) a large corpus of scientific papers P and (b) pairs of literature search questions and one or more target papers from P. Our desiderata are scientific questions that researchers may use while conducting literature surveys. We use two different strategies to collect such questions: (1) we construct questions using the surrounding context from inline citations in published papers (Section 2.1), and (2) we invited the authors of recent conference publications to manually write questions about their own papers (Section 2.2). For both subsets, we ensure high question quality via manual inspection and filtering conducted by the authors of this work (Section 2.3).

## 2.1 Inline-citation Questions

We define the following concepts for the ease of description: (a) An inline citation mention is a paragraph from the main text of a paper that mentions another paper. For example, this paragraph from the RoBERTa paper (Liu et al., 2019), “... Unlike Devlin et al., (2019), ... we do not train with a reduced sequence length for the first 90% of updates ...” mentions the BERT paper (Devlin et al., 2019). (b) The source paper is the paper the inline citation mention is sampled from. (c) A target paper is a paper that is cited by the inline citation mention.

Figure 2 provides an overview of our data collection methodology for inline-citation questions. We utilize the Semantic Scholar Open Research Corpus (S2ORC; Lo et al., 2020), a large corpus of academic papers obtained from publishers, archives, and the Internet. We randomly sample inline citation mentions from the S2ORC<sup>2</sup> and prompt GPT-4 to rewrite these citation mentions into literature search questions. These questions are filtered to remove those with a high word overlap with the title of the target papers, and are further manually examined to ensure high quality.

![](images/cb5ec87d12c6c36e25d607ca68326d761ec3119386b2f99ed4dbbff20d898eac.jpg)  
Table 1: Annotation rubrics for the manual filtering (conducted by the authors of LitSearch).

Sampling inline citation mentions. We limit the target papers to be only from the ACL Anthology, for the purpose of aligning with the expertise of the manual annotators, i.e., authors of this work. However, we do not limit where the source papers come from. Depending on the source papers, we call these questions ACL sourced or non-ACL sourced.

Prompting GPT-4 to generate questions. Given a sampled citation mention, we prompt GPT-4 (OpenAI, 2023) to generate a literature search question. In the prompt, we provide (1) the sampled paragraph (the inline citation mention) from the source paper and (2) the titles of the cited papers, and instruct GPT-4 to generate a literature search question based on the paragraph that would be answered by one or more of the papers cited in the paragraph. We use in-context learning (Brown et al., 2020) and include two demonstrations. The prompt we use can be found in Table 12.

Word-overlap filtering. We notice that inlinecitation questions generated in the last step can have very high word overlap with the target paper titles, which makes their retrieval trivial even for BM25 and suggests that the questions may not be of interest to researchers. We calculate the word overlap as the percentage of words in the generated question that are also included in the target paper titles. We filter out ACL sourced questions that have an overlap score higher than 0.3 and non-ACL sourced questions that have an overlap score higher than 0.1. In this step, we filter out 5% of the ACL sourced questions and 80% of the non-ACL sourced questions.

## 2.2 Author-written Questions

Besides generating questions using existing inline citation mentions, we also collect questions directly from human annotators. As writing literature search questions requires deep understanding of the research field and the target paper, we invite researchers to write search queries that are answered by their own published papers. One additional benefit of this setup is that the correctness of the questions is better guaranteed.

We invited authors of ACL 2023 and ICLR 2024 papers to write one literature search question for each of their papers. We chose the two venues as they were among the latest natural language and machine learning conferences at the time of the data collection, hence the papers represent the latest research development and are unlikely to have already been included in the pre-training data of LLMs and retrievers used in our evaluations. We sent out invitations to 623 ACL 2023 authors and 404 ICLR 2024 authors, and received 175 questions from ACL 2023 authors and 117 questions from ICLR 2024 authors.

## 2.3 Manual Filtering to Ensure High Quality

Finally, the authors of this work manually examine every question from both the inline-citation and author-written subsets and annotate these for specificity and quality (guidelines in Table 1). Questions that are too general (there are more than 20 papers from the corpus can fit the question) are assigned a quality score of 0 and are excluded. We include only questions with a quality score of 1 or 2 in the final dataset. We also rewrite questions if they have minor mistakes and can be fixed easily. Each question is assigned to one author for annotation.

<table><tr><td rowspan="2"></td><td colspan="4">Broad</td><td colspan="4">Specific</td><td rowspan="2">Total #Q</td></tr><tr><td>#Q</td><td>Avg. Len</td><td>Overlap</td><td>Avg. #P</td><td>#Q</td><td>Avg. Len</td><td>Overlap</td><td>Avg. #P</td></tr><tr><td>Inline-citation Questions</td><td>120</td><td>20.6</td><td>0.33</td><td>1.21</td><td>231</td><td>22.1</td><td>0.34</td><td>1.07</td><td>351</td></tr><tr><td>Author-written Questions</td><td>35</td><td>15.8</td><td>0.43</td><td>1.03</td><td>211</td><td>17.9</td><td>0.43</td><td>1.00</td><td>246</td></tr></table>

Table 2: Statistics for LitSearch. Please refer to Table 14 for more detailed statistics of each subset. “#Q”: number of questions. “Overlap”: the fraction of words in the question that are also included in the titles and abstracts of the target papers. “Avg. #P”: average number of target papers.

As the examples in Table 1 show, questions of both specificity types can be realistic and valuable, but they exhibit distinct traits. We use the specificity scores to distinguish broad and specific questions in the evaluation.

For the inline-citation subset, we manually examined 382 ACL sourced questions and 450 non-ACL sourced questions. 26% (98 instances) of the ACL questions and 56% (253 instances) of the non-ACL questions are kept. For the author-written subset, since all questions are written by experts, we avoid rewriting them as much as possible. In the end, we kept 89% (155) questions from ACL 2023 authors and 78% (91) questions from ICLR 2024 authors.

## 2.4 Dataset Statistics

Our final dataset contains 597 questions, with 351 in the inline-citation subset and 246 in the authorwritten subset. Dataset statistics, including the number of questions, the average question length, and the average word overlap between the question and the target papers (titles and abstracts), are presented in Table 2. We find that author-written questions are shorter and have a higher word overlap rate with the target papers (0.43 vs. 0.33 for inline-citation questions). This is expected: when writing questions for their own papers, authors tend to re-use terminology from their papers and focus on the main findings which are usually included in the abstracts or titles. In contrast, inline-citation questions can be anchored to any span of the reference documents, irrespective of the main findings or the main focuses of the target papers.

## 2.5 The Retrieval Corpus

The LitSearch retrieval corpus P consists of ACL Anthology and ICLR papers extracted from S2ORC (see Appendix C for details). We do not use the full S2ORC corpus for efficiency reasons. In total, this yields 64, 183 papers (59, 383 ACL

Anthology papers and 4, 807 ICLR papers)<sup>3</sup>. The average number of words for the documents in P is 134 / 6,041 (titles and abstracts / full texts).

## 3 Experiments

## 3.1 Experimental Setup

We compare the performance of different retrieval systems (enumerated below) on our LitSearch benchmark. Due to the limited context sizes of existing embedding models, we only use the paper titles and abstracts to embed the papers in our retrieval corpus P by default.

For all systems we compare, we report the recall@K for both the broad and specific subsets of LitSearch. We report results for K = 5, 20 for the specific subset and K = 20 for the broad subset; these values (5 and 20) correspond to the guidelines followed by the authors while determining the specificity of a given question (see Table 1).

## 3.2 Baselines

We benchmark both retrieval models and LLMbased rerankers in this work.

Retriever models. We evaluate using the classic BM25 algorithm (Robertson et al., 2009), as well as several state-of-the-art dense retrieval (embedding) models, including GTR (Ni et al., 2022), Instructor (Su et al., 2023), E5 (Wang et al., 2022), and GritLM (Muennighoff et al., 2024).<sup>4</sup> More details are provided in Appendix D.

LLM-based reranking. In addition to vanilla retrieval, we also use strong LLMs (GPT-4o<sup>5</sup> in our case) to rerank the top retrieved results from the above retrievers. We use two strategies:

Vanilla reranking. We include the top-n retrieved papers (titles and abstracts) in the context and prompt GPT-4o to rerank these based on the question (see our prompt in Table 13). This is similar to prior works (Sun et al., 2023b; Ma et al., 2023). We use $n = 1 0 0$ , resulting in an average context length of 13,844 words.

<table><tr><td rowspan="3"></td><td colspan="3">Inline-citation</td><td colspan="3">Author-written</td><td rowspan="2">Avg. Broad</td><td rowspan="2">Avg. Specific</td></tr><tr><td>Broad</td><td colspan="2">Specific</td><td>Broad</td><td colspan="2">Specific</td></tr><tr><td>R@20</td><td>R@5</td><td>R@20</td><td>R@20</td><td>R@5</td><td>R@20</td><td>R@20</td><td>R@5</td></tr><tr><td>BM25</td><td>37.4</td><td>38.5</td><td>55.8</td><td>48.6</td><td>62.6</td><td>73.5</td><td>39.9</td><td>50.0</td></tr><tr><td>GTR-T5-large</td><td>45.7</td><td>38.5</td><td>51.5</td><td>37.1</td><td>40.8</td><td>55.9</td><td>43.8</td><td>39.6</td></tr><tr><td>Instructor-XL</td><td>56.3</td><td>48.9</td><td>60.0</td><td>57.1</td><td>55.9</td><td>70.1</td><td>56.5</td><td>52.3</td></tr><tr><td>E5-large-v2</td><td>55.8</td><td>50.4</td><td>63.9</td><td>54.3</td><td>62.6</td><td>75.8</td><td>55.4</td><td>56.2</td></tr><tr><td>GritLM-7B</td><td>69.7</td><td>67.7</td><td>77.9</td><td>74.3</td><td>82.5</td><td>89.1</td><td>70.8</td><td>74.8</td></tr><tr><td>GPT-4o reranking (w/ BM25)</td><td>54.9</td><td>60.0</td><td>67.5</td><td>77.1</td><td>76.8</td><td>82.9</td><td>59.9</td><td>68.0</td></tr><tr><td>GPT-4o one-hop (w/ BM25)</td><td>62.0</td><td>64.1</td><td>71.6</td><td>74.3</td><td>73.5</td><td>77.7</td><td>64.8</td><td>68.6</td></tr><tr><td>GPT-4o reranking (w/ GritLM)</td><td>74.7</td><td>73.2</td><td>79.9</td><td>77.1</td><td>85.8</td><td>92.4</td><td>75.3</td><td>79.2</td></tr><tr><td>GPT-4o one-hop (w/ GritLM)</td><td>72.9</td><td>70.3</td><td>78.4</td><td>74.3</td><td>84.4</td><td>87.2</td><td>73.2</td><td>77.0</td></tr></table>

Table 3: Main experimental results of LitSearch. Here we only use the titles and abstracts of papers for retrieval and reranking. We report recall@20 (R@20) for broad questions and recall@5 and @20 (R@5, R@20) for specific questions. “Broad” and “specific” correspond to the annotations during our manual filtering stage (defined in Table 1).  
![](images/c279d4ea2d9346c9685f48ed50a2c894be8fd7fe6428beddb4c48c0e45a8a8f5.jpg)  
Figure 3: We demonstrate detailed retrieval results using BM25, E5 and GritLM up to k = 50. Additionally, we show the effect of applying GPT-4o reranking over GritLM retrieval results.

One-hop reranking. Inspired by Tang et al. (2023), we leverage the fact that for some questions, there may exist lexically similar inline citation mentions in the retrieval corpus. Due to our data collection pipeline, this is particularly true for the ACL sourced inline citation questions. We posit that the retrieval models will be able to retrieve these source papers (that cite the target papers) based on the questions.

We extract the top m retrieved papers and construct a new candidate list by adding papers cited by each of these seed retrieved papers. We concatenate papers in the following order, skipping duplicates: [rank-1 paper $p _ { 1 }$ , papers cited by $p _ { 1 }$ rank-2 paper $p _ { 2 }$ , papers cited by $p _ { 2 } , . . . , p _ { m }$ , papers cited by $p _ { m } ] .$ . To avoid very long contexts, we truncate this list after the first n papers and use the same prompt for GPT-4o based reranking as above.

In our experiments, we use $m = 5 0$ and $n = 2 0 0$ resulting in average length of 27,544 words.

## 3.3 Results

We outline the performance of the above systems on LitSearch in Table 3. First, we observe that all instruction-finetuned embedding models, e.g. Instructor, E5, and GritLM, substantially outperform BM25 on our benchmark. In fact, they also perform better than the GTR model. Overall, we found that GritLM-7B achieves the best performance (70.8 recall@20 on broad questions and 74.8 recall@5 on specific questions), leaving a large gap compared to other baselines.

Impact of reranking. We also report the performance improvement brought by the reranking methods on the weakest (BM25) and strongest (GritLM) retrievers in Table 3. We observe that both vanilla and one-hop reranking improve over the base retrieval performance. For example, on the specific subset of inline questions, the vanilla GPT-4o reranking improves the recall@5 of BM25 and GritLM by 21.5% and 5.5% respectively. Interestingly, the improvements from one-hop reranking are generally lower than vanilla reranking across all subsets, when using GritLM as the base retriever; this shows that our benchmark cannot be easily “gamed” by mimicking the data collection pipeline or exploiting similar citation mentions to the question from other papers.

<table><tr><td rowspan="2"></td><td colspan="2">Inline (specific)</td><td colspan="2">Author (specific)</td></tr><tr><td>Qual=1R@5</td><td>Qual=2R@5</td><td>Qual=1R@5</td><td>Qual=2R@5</td></tr><tr><td>BM25</td><td>36.4</td><td>30.6</td><td>62.2</td><td>55.0</td></tr><tr><td>GTR-T5-large</td><td>42.0</td><td>31.4</td><td>40.7</td><td>36.9</td></tr><tr><td>Instructor-XL</td><td>55.1</td><td>39.5</td><td>58.5</td><td>48.6</td></tr><tr><td>E5-large-v2</td><td>48.4</td><td>42.6</td><td>61.5</td><td>57.7</td></tr><tr><td>GritLM-7B</td><td>67.3</td><td>58.7</td><td>80.0</td><td>76.6</td></tr></table>

Table 4: Comparison of retrieval performance on different quality (qual) questions. Generally, retrievers report lower performance on the Qual=2 questions, i.e. those deemed more challenging in our manual annotation.

Impact of question specificity. Table 3 and Figure 3 show that retrieval systems generally report higher recall performance on the specific subset. This is expected: there exists a smaller number of “competing” papers, i.e. those that also satisfy the search question, for the specific subset in the retrieval corpus. Note that our human annotation tagged questions with approximately 5 relevant papers as specific and 20 relevant papers as broad (see Table 1 for details). We keep both subsets in our dataset as this stratified reporting presents a more nuanced view of retriever capabilities.

Inline-citation vs. author-written questions. We observe very different performance trends for the two subsets (Table 3 and Figure 3). In particular, inline-citation questions are harder than authorwritten questions for all retriever systems, on both broad and specific questions.

We attribute this difference to the higher semantic or lexical overlap of author-written questions with the paper titles and abstracts (see Table 2 for statistics). This reflects expected tendency of paper authors to formulate the questions around the main contributions from the abstracts and re-use terminologies. Such annotator biases have been widely discussed in prior data collection efforts as well, particularly when humans write content from scratch (Gururangan et al., 2018).

Impact of question quality. Table 4 compares how retrieval models perform on different quality subsets. Recall that we manually annotated the quality of all questions (Table 1). We observe that questions with a quality score of 2, i.e. determined to be more realistic and difficult by manual annotators, are consistently more challenging for retrieval models. This demonstrates the high annotation quality of our manual inspection step. The presence of these different quality questions in our dataset leads to higher diversity and better coverage over the varied information seeking needs of users.

<table><tr><td rowspan="2"></td><td colspan="2">Inline</td><td colspan="2">Author</td></tr><tr><td>Broad R@20</td><td>Spec R@5</td><td>Broad R@20</td><td>Spec R@5</td></tr><tr><td>BM25</td><td>37.4</td><td>38.5</td><td>48.6</td><td>62.6</td></tr><tr><td>w/ full</td><td>18.6</td><td>23.8</td><td>65.7</td><td>71.6</td></tr><tr><td>GTR-T5-large</td><td>45.7</td><td>38.5</td><td>37.1</td><td>40.8</td></tr><tr><td>w/ full</td><td>43.9</td><td>39.4</td><td>45.7</td><td>39.8</td></tr><tr><td>Instructor-XL</td><td>56.3</td><td>48.9</td><td>57.1</td><td>55.9</td></tr><tr><td>w/ full</td><td>53.0</td><td>50.9</td><td>57.1</td><td>56.9</td></tr><tr><td>E5-large-v2</td><td>55.8</td><td>50.4</td><td>54.3</td><td>62.6</td></tr><tr><td>w/ full</td><td>56.9</td><td>48.7</td><td>60.0</td><td>62.1</td></tr><tr><td>GritLM-7B</td><td>69.7</td><td>67.7</td><td>74.3</td><td>82.5</td></tr><tr><td>w/ full</td><td>70.8</td><td>63.4</td><td>65.7</td><td>73.0</td></tr></table>

Table 5: Retrieval results of using only titles and abstracts vs. using titles, abstracts, and full text (w/ full). We do not observe consistent improvements from including the full text for existing retrieval models.

## 4 Analysis

## 4.1 Does Including More Paper Content Improve Retrieval Performance?

In the previous section, we only used the titles and abstracts (on average 134 words) to encode the papers in the retrieval corpus. Here, we evaluate whether encoding more paper content can improve retrieval performance. For all retriever models compared, we create embeddings using the full paper text (on average 6,041 words) up to their allowed context lengths.<sup>6</sup> We compare this setting against our default setting (only titles and abstracts).

Our results are outlined in Table 5. Surprisingly, we find that the addition of more paper text does not improve performance on LitSearch consistently. In fact, we only observe substantial improvement on the author-written broad questions for BM25 and some embedding models. In other cases, more text more often hinders instead of improving performance. Note that the maximum context length of the tested models is 2,048 (GritLM) and the average length of their training data is even shorter—for example, the commonly used MS-MARCO (Nguyen et al., 2017) and NaturalQuestions (Lee et al., 2019) have an average document length of 56 and 79. This is significantly shorter than the full text of papers from our retrieval corpus averaging 6,041 words in length, potentially leading to the unsatisfying performance when using full texts with embedding models.

<table><tr><td rowspan="2"></td><td colspan="2">ACL</td><td colspan="2">Non-ACL</td></tr><tr><td>BroadR@20</td><td>SpecificR@5</td><td>BroadR@20</td><td>SpecificR@5</td></tr><tr><td>BM25</td><td>38.8</td><td>39.4</td><td>36.9</td><td>38.2</td></tr><tr><td>GTR-T5-large</td><td>37.2</td><td>39.4</td><td>48.9</td><td>38.2</td></tr><tr><td>Instructor-XL</td><td>48.6</td><td>43.9</td><td>59.1</td><td>50.9</td></tr><tr><td>E5-large-v2</td><td>46.6</td><td>46.2</td><td>59.1</td><td>52.1</td></tr><tr><td>GritLM-7B</td><td>72.4</td><td>65.9</td><td>68.8</td><td>68.5</td></tr><tr><td colspan="5">With BM25</td></tr><tr><td>Reranking</td><td>51.1</td><td>59.8</td><td>56.2</td><td>60.0</td></tr><tr><td>One-hop</td><td>65.2</td><td>71.2</td><td>60.8</td><td>61.2</td></tr><tr><td colspan="5">With GritLM</td></tr><tr><td>Reranking</td><td>80.3</td><td>72.7</td><td>72.7</td><td>73.3</td></tr><tr><td>One-hop</td><td>81.3</td><td>67.4</td><td>69.9</td><td>71.5</td></tr></table>

Table 6: Comparison of retrieval performance on the ACL vs. non-ACL sourced inline-citation questions. Results show that the performance improvement from one-hop reranking over BM25 is subtantially higher for ACL sourced questions.

## 4.2 Does the Source of Inline Citation Questions Matter?

Next, we study how the different sources of inlinecitation questions affect the model performance. Table 6 outlines the performance of retrieval models on ACL sourced vs. non-ACL sourced inlinecitation questions. Our results show that the two different sets report similar trends and model rankings for different retrieval models, particularly on the specific subset of questions. Interestingly, we find that the performance improvement from onehop reranking is very different for the ACL and non-ACL questions.

For BM25, we observe that one-hop reranking is significantly better than the vanilla reranking on ACL sourced questions (+11.4% recall@5 on specific); but the gap is much smaller on non-ACL sourced questions (+1.2% recall@5 on specific). We posit that this is because BM25 can better exploit the data annotation pipeline on the ACL sourced questions. It can likely first identify the source ACL paper where the citation mention comes from, and then find the target paper via onehop reranking. Including the non-ACL questions to LitSearch prevents systems from exploiting such “shortcuts” as non-ACL source papers are not part of the retrieval corpus.

<table><tr><td></td><td>Inline (specific)R@5</td><td>Author (specific)R@5</td></tr><tr><td>BM25</td><td>38.5</td><td>62.6</td></tr><tr><td>GritLM-7B</td><td>67.7</td><td>82.5</td></tr><tr><td>Google Search</td><td>23.1</td><td>62.5</td></tr><tr><td>Google Scholar</td><td>20.5</td><td>17.5</td></tr><tr><td>Elicit</td><td>23.1</td><td>17.5</td></tr></table>

Table 7: Recall@5 for commercial search engines on a random subset of 80 specific questions. Search engines generally report poor performance. Note that the comparison is not apples-to-apples as search engines use a much larger retrieval corpus.

For GritLM, we do not observe similarly large performance gains when using one-hop reranking. We hypothesize that this is because when using GritLM, the initial top retrieval results already include the target papers and the one-hop strategy does not bring further improvement.

## 4.3 Performance of Search Engines

In practice, researchers use search engines like Google Search, Google Scholar, or Elicit<sup>7</sup> to search for relevant papers for their scientific queries. We conduct a human study to understand how these search engines perform on LitSearch: We randomly sample 80 questions (all specific; 40 inline-citation and 40 author-written) from our dataset. We manually input<sup>8</sup> these questions into the above search engines and report recall@5.<sup>9</sup> We note that this is not an apples-to-apples comparison against the retrieval models in earlier sections due to the discrepancy in the retrieval corpus.

Table 7 outlines the results of our human study. It shows that all three search engines deliver similarly low recalls on inline-citation questions. On the author-written questions, Google Search performs much better than the other two. Although not directly comparable, this performance is generally worse than the embedding models, demonstrating the potential of these strong dense retrieval models for citation recommendation applications.

<table><tr><td></td><td>MSMARCO</td><td>SCIDOCS</td><td>NQ</td><td>ArXiv</td><td>LitSearch (broad)</td><td>LitSearch (specific)</td></tr><tr><td>GTR-T5-large</td><td>42.7</td><td>15.5</td><td>55.1</td><td>17.5</td><td>23.3</td><td>30.4</td></tr><tr><td>Instructor-XL</td><td>41.6</td><td>17.4</td><td>57.2</td><td>19.8</td><td>32.8</td><td>41.2</td></tr><tr><td>E5-large-v2</td><td>43.5</td><td>20.5</td><td>63.4</td><td>27.0</td><td>27.1</td><td>45.3</td></tr><tr><td>GritLM-7B</td><td>42.0</td><td>24.4</td><td>70.3</td><td>34.3</td><td>44.1</td><td>60.3</td></tr></table>

Table 8: Comparison between LitSearch and existing retrieval benchmarks. All reported numbers are nDCG@10 for a direct comparison.

## 4.4 Comparing Other Retrieval Benchmarks

We compare model performance on LitSearch to several popular retrieval benchmarks included in BEIR (Thakur et al., 2021) and MTEB (Muennighoff et al., 2022)—namely MS-MARCO (Nguyen et al., 2017), SCIDOCS (Cohan et al., 2020), and NQ (Lee et al., 2019).<sup>10</sup> We also compare to ArXiv (Gu et al., 2022), a previous citation recommendation benchmark directly using inline citations as queries. Table 8 shows that LitSearch generally agrees with existing retrieval benchmarks. However, LitSearch can differentiate retriever models better: for example, the gap between GritLM and E5 on LitSearch (specific) is 15 points (nDCG@10), while they perform almost the same on MSMARCO. LitSearch provides an informative testbed that can effectively reflect the recent (and future) advancement in embedding models.

## 5 Related Work

Citation recommendation. The community has proposed a number of citation recommendation datasets (Färber and Jatowt, 2020), including global citation recommendation datasets (directly using a paper as the query and papers it cites as target papers; Cohan et al., 2020; Bhagavatula et al., 2018), and local citation recommendation datasets (using inline citation mentions as queries; He et al., 2010; Medic and Snajder´ , 2020; Jeong et al., 2020; Gu et al., 2022). There are also language models and retrieval models specifically trained for scientific document understanding and retrieval tasks, such as SciBERT (Beltagy et al., 2019) and SPECTER (Cohan et al., 2020). Compared to existing citation recommendation datasets, LitSearch is comprised of manually annotated, natural language literature search questions, providing a more realistic and challenging evaluation for citation recommendation systems.

Retrieval benchmarks. There have been numerous datasets evaluating retrieval systems from Wikipedia (Kwiatkowski et al., 2019; Lee et al., 2019), web queries (Nguyen et al., 2017), biomedical questions (Voorhees and Tice, 2000), and more. Recently, there have been several benchmarks combining multiple datasets and evaluating retrieval or embedding models across different domains and different use cases, such as KILT (Petroni et al., 2021), BEIR (Thakur et al., 2021), and MTEB (Muennighoff et al., 2022). LitSearch offers a unique perspective by exploring the novel literature search question type, effectively complementing the existing benchmarks. Contemporary with our work, CiteME (Press et al., 2024) introduces a benchmark for identifying references based on claims made in a paper’s inline text (as opposed to research questions in our case). Their focus differs from ours in that it is aimed more at LLM-based agents rather than retrieval systems.

Retrieval systems. Traditional retrieval systems rely on bag-of-word algorithms such as TF-IDF and BM25. Dense retrieval (embedding) models have gained more popularity due to their abilities to do semantic search without relying on exact keyword matches (Pennington et al., 2014; Reimers and Gurevych, 2019). State-of-the-art dense models are mostly adopted by fine-tuning pre-trained language models (Devlin et al., 2019; Touvron et al., 2023) with a contrastive learning objective on either supervised or unsupervised data (Karpukhin et al., 2020; Gao et al., 2021; Izacard et al., 2022; Ni et al., 2022; Khattab and Zaharia, 2020). Recent development introduces “instructions” when encoding queries and documents, which significantly improves the versatility of embeddings across tasks (Su et al., 2023; Wang et al., 2022; Wu et al., 2022; Lee et al., 2024; BehnamGhader et al., 2024).

## 6 Conclusion

In this paper, we propose LitSearch, a new retrieval benchmark comprising 597 manually-curated literature search questions. LitSearch includes an inline-citation question set and an author-written question set, both undergoing manual inspection from the authors of LitSearch. We conduct extensive experiments with BM25, state-of-the-art embedding models, and LLM reranking. Our experiments demonstrate the superior performance of state-of-the-art instruction-finetuned embedding models, with additional improvement via GPT-4obased reranking. We also verify that commercial search engines like Google struggle with LitSearch questions. The comparison with existing retrieval benchmarks shows that LitSearch better differentiates the performance of retrieval systems.

## Limitations

Even though we manually examined the dataset, there still exist questions that are either slightly out of distribution compared to what researchers would ask, or too easy due to high overlap with the target papers. The author-written questions are easier than we expected, as writing challenging literature search questions is non-trivial even for experienced researchers. Even though we experimented with several state-of-the-art systems, it was not an exhausted evaluation and we left out more sophisticated retrieval or reranking systems. This research primarily focuses on only English questions and research papers.

## Ethics Statement

The research artifact of this paper, LitSearch, is manually inspected and has been ensured to have no unsafe or inappropriate content. However, the process to generate the dataset may introduce certain biases: for example, the inline-citation questions contain more target papers that have high citations due to the sampling; the author-written questions only cover ACL 2023 and ICLR 2024 papers.

## Acknowledgements

We want to acknowledge Dan Friedman, Howard Yen, Jiayi Geng, Lucy He, and other members of the Princeton NLP group for their useful feedback and discussion. We also acknowledge all the ACL 2023 and ICLR 2024 authors that contributed questions to LitSearch (listed in Appendix A). Tianyu

Gao is supported by an IBM PhD Fellowship. This work is gratefully supported by an NSF CAREER award (IIS-2239290), and Microsoft Azure credits through the “Accelerate Foundation Models Academic Research” Initiative.

## References

Parishad BehnamGhader, Vaibhav Adlakha, Marius Mosbach, Dzmitry Bahdanau, Nicolas Chapados, and Siva Reddy. 2024. Llm2vec: Large language models are secretly powerful text encoders. Preprint, arXiv:2404.05961.

Iz Beltagy, Kyle Lo, and Arman Cohan. 2019. SciB-ERT: A pretrained language model for scientific text. In Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP), pages 3615– 3620, Hong Kong, China. Association for Computational Linguistics.

Chandra Bhagavatula, Sergey Feldman, Russell Power, and Waleed Ammar. 2018. Content-based citation recommendation. In Proceedings of the 2018 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long Papers), pages 238–251, New Orleans, Louisiana. Association for Computational Linguistics.

Tom B Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, et al. 2020. Language models are few-shot learners. In Advances in Neural Information Processing Systems (NeurIPS).

Arman Cohan, Sergey Feldman, Iz Beltagy, Doug Downey, and Daniel Weld. 2020. SPECTER: Document-level representation learning using citation-informed transformers. In Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics, pages 2270–2282, Online. Association for Computational Linguistics.

Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova. 2019. BERT: Pre-training of deep bidirectional Transformers for language understanding. In North American Chapter of the Association for Computational Linguistics (NAACL).

Michael Färber and Adam Jatowt. 2020. Citation recommendation: approaches and datasets. Int. J. Digit. Libr., 21(4):375–405.

Tianyu Gao, Xingcheng Yao, and Danqi Chen. 2021. SimCSE: Simple contrastive learning of sentence embeddings. In Empirical Methods in Natural Language Processing (EMNLP), pages 6894–6910.

Nianlong Gu, Yingqiang Gao, and Richard H. R. Hahnloser. 2022. Local citation recommendation with hierarchical-attention text encoder and scibert-based reranking. In Advances in Information Retrieval: 44th European Conference on IR Research, ECIR 2022, Stavanger, Norway, April 10–14, 2022, Proceedings, Part I, page 274–288, Berlin, Heidelberg. Springer-Verlag.

Suchin Gururangan, Swabha Swayamdipta, Omer Levy, Roy Schwartz, Samuel Bowman, and Noah A. Smith. 2018. Annotation artifacts in natural language inference data. In Proceedings of the 2018 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 2 (Short Papers), pages 107–112, New Orleans, Louisiana. Association for Computational Linguistics.

Qi He, Jian Pei, Daniel Kifer, Prasenjit Mitra, and Lee Giles. 2010. Context-aware citation recommendation. In Proceedings of the 19th International Conference on World Wide Web, WWW ’10, page 421–430, New York, NY, USA. Association for Computing Machinery.

Gautier Izacard, Mathilde Caron, Lucas Hosseini, Sebastian Riedel, Piotr Bojanowski, Armand Joulin, and Edouard Grave. 2022. Unsupervised dense information retrieval with contrastive learning. Transactions on Machine Learning Research.

Chanwoo Jeong, Sion Jang, Eunjeong Park, and Sungchul Choi. 2020. A context-aware citation recommendation model with bert and graph convolutional networks. Scientometrics, 124(3):1907–1922.

Vladimir Karpukhin, Barlas Oguz, Sewon Min, Patrick Lewis, Ledell Wu, Sergey Edunov, Danqi Chen, and Wen-tau Yih. 2020. Dense passage retrieval for opendomain question answering. In Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP), pages 6769–6781, Online. Association for Computational Linguistics.

O. Khattab and Matei A. Zaharia. 2020. Colbert: Efficient and effective passage search via contextualized late interaction over bert. Proceedings of the 43rd International ACM SIGIR Conference on Research and Development in Information Retrieval.

Tom Kwiatkowski, Jennimaria Palomaki, Olivia Red field, Michael Collins, Ankur Parikh, Chris Alberti, Danielle Epstein, Illia Polosukhin, Jacob Devlin, Ken ton Lee, Kristina Toutanova, Llion Jones, Matthew Kelcey, Ming-Wei Chang, Andrew M. Dai, Jakob Uszkoreit, Quoc Le, and Slav Petrov. 2019. Natural questions: A benchmark for question answering research. Transactions of the Association for Compu tational Linguistics, 7:452–466.

Chankyu Lee, Rajarshi Roy, Mengyao Xu, Jonathan Raiman, Mohammad Shoeybi, Bryan Catanzaro, and Wei Ping. 2024. Nv-embed: Improved techniques for training llms as generalist embedding models. Preprint, arXiv:2405.17428.

Kenton Lee, Ming-Wei Chang, and Kristina Toutanova. 2019. Latent retrieval for weakly supervised open domain question answering. In Association for Computational Linguistics (ACL), pages 6086–6096.

Yinhan Liu, Myle Ott, Naman Goyal, Jingfei Du, Mandar Joshi, Danqi Chen, Omer Levy, Mike Lewis, Luke Zettlemoyer, and Veselin Stoyanov. 2019. RoBERTa: A robustly optimized BERT pretraining approach. arXiv preprint arXiv:1907.11692.

Kyle Lo, Lucy Lu Wang, Mark Neumann, Rodney Kinney, and Daniel Weld. 2020. S2ORC: The semantic scholar open research corpus. In Association for Computational Linguistics (ACL), pages 4969–4983.

Xueguang Ma, Xinyu Zhang, Ronak Pradeep, and Jimmy Lin. 2023. Zero-shot listwise document reranking with a large language model. arXiv preprint arXiv:2305.02156.

Zoran Medic and Jan Snajder. 2020.´ Improved local citation recommendation based on context enhanced with global information. In Proceedings of the First Workshop on Scholarly Document Processing, pages 97–103, Online. Association for Computational Linguistics.

Niklas Muennighoff, Hongjin Su, Liang Wang, Nan Yang, Furu Wei, Tao Yu, Amanpreet Singh, and Douwe Kiela. 2024. Generative representational instruction tuning. arXiv preprint arXiv:2402.09906.

Niklas Muennighoff, Nouamane Tazi, Loïc Magne, and Nils Reimers. 2022. Mteb: Massive text embedding benchmark. arXiv preprint arXiv:2210.07316.

Tri Nguyen, Mir Rosenberg, Xia Song, Jianfeng Gao, Saurabh Tiwary, Rangan Majumder, and Li Deng. 2017. MS MARCO: A human-generated MAchine reading COmprehension dataset.

Jianmo Ni, Chen Qu, Jing Lu, Zhuyun Dai, Gustavo Hernandez Abrego, Ji Ma, Vincent Zhao, Yi Luan, Keith Hall, Ming-Wei Chang, and Yinfei Yang. 2022. Large dual encoders are generalizable retrievers. In Empirical Methods in Natural Language Processing (EMNLP), pages 9844–9855.

OpenAI. 2023. GPT-4 Technical Report. Preprint, arXiv:2303.08774

Jeffrey Pennington, Richard Socher, and Christopher Manning. 2014. GloVe: Global vectors for word representation. In Empirical Methods in Natural Language Processing (EMNLP), pages 1532–1543.

Fabio Petroni, Aleksandra Piktus, Angela Fan, Patrick Lewis, Majid Yazdani, Nicola De Cao, James Thorne, Yacine Jernite, Vladimir Karpukhin, Jean Maillard, Vassilis Plachouras, Tim Rocktäschel, and Sebastian Riedel. 2021. KILT: a benchmark for knowledge intensive language tasks. In Proceedings of the 2021 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, pages 2523–2544, Online. Association for Computational Linguistics.

Ori Press, Andreas Hochlehnert, Ameya Prabhu, Vishaal Udandarao, Ofir Press, and Matthias Bethge. 2024. Citeme: Can language models accurately cite scientific claims? Preprint, arXiv:2407.12861.

Nils Reimers and Iryna Gurevych. 2019. Sentence-BERT: Sentence embeddings using Siamese BERTnetworks. In Empirical Methods in Natural Language Processing and International Joint Conference on Natural Language Processing (EMNLP-IJCNLP).

Stephen Robertson, Hugo Zaragoza, et al. 2009. The probabilistic relevance framework: Bm25 and beyond. Foundations and Trends® in Information Retrieval, 3(4):333–389.

Hongjin Su, Weijia Shi, Jungo Kasai, Yizhong Wang, Yushi Hu, Mari Ostendorf, Wen-tau Yih, Noah A. Smith, Luke Zettlemoyer, and Tao Yu. 2023. One embedder, any task: Instruction-finetuned text embeddings. In Findings of the Association for Computational Linguistics: ACL 2023, pages 1102–1121, Toronto, Canada. Association for Computational Linguistics.

Weiwei Sun, Lingyong Yan, Xinyu Ma, Pengjie Ren, Dawei Yin, and Zhaochun Ren. 2023a. Is chatgpt good at search? investigating large language models as re-ranking agent. ArXiv, abs/2304.09542.

Weiwei Sun, Lingyong Yan, Xinyu Ma, Shuaiqiang Wang, Pengjie Ren, Zhumin Chen, Dawei Yin, and Zhaochun Ren. 2023b. Is ChatGPT good at search? investigating large language models as re-ranking agents. In Empirical Methods in Natural Language Processing (EMNLP), pages 14918–14937.

Michael Tang, Shunyu Yao, John Yang, and Karthik Narasimhan. 2023. Referral augmentation for zero-shot information retrieval. Preprint, arXiv:2305.15098.

Nandan Thakur, Nils Reimers, Andreas Rücklé, Abhishek Srivastava, and Iryna Gurevych. 2021. BEIR: A heterogeneous benchmark for zero-shot evaluation of information retrieval models. In Thirty-fifth Conference on Neural Information Processing Systems Datasets and Benchmarks Track (Round 2).

Hugo Touvron, Thibaut Lavril, Gautier Izacard, Xavier Martinet, Marie-Anne Lachaux, Timothée Lacroix, Baptiste Rozière, Naman Goyal, Eric Hambro, Faisal Azhar, et al. 2023. LLaMA: Open and Efficient Foundation Language Models. arXiv preprint arXiv:2302.13971.

Ellen M. Voorhees and Dawn M. Tice. 2000. Building a question answering test collection. In Proceedings of the 23rd Annual International ACM SIGIR Conference on Research and Development in Information Retrieval, SIGIR ’00, page 200–207, New York, NY, USA. Association for Computing Machinery.

Liang Wang, Nan Yang, Xiaolong Huang, Binxing Jiao, Linjun Yang, Daxin Jiang, Rangan Majumder, and Furu Wei. 2022. Text embeddings by

weakly-supervised contrastive pre-training. ArXiv, abs/2212.03533.

Jialian Wu, Jianfeng Wang, Zhengyuan Yang, Zhe Gan, Zicheng Liu, Junsong Yuan, and Lijuan Wang. 2022. Grit: A generative region-to-text transformer for object understanding. Preprint, arXiv:2212.00280.

## A Annotator Acknowledgments

We would like to thank Marah I Abdin, Jaewoo Ahn, Kabir Ahuja, Xi Ai, Satoshi Akasaki, Anastasios N Angelopoulos, Jinheon Baek, Eslam Mohamed Bakr, Pablo Barceló, Claudio Battiloro, Jonas Belouadi, Abhik Bhattacharjee, Valeriia Bolotova, Pengshan Cai, Nitay Calderon, Qingqing Cao, Defu Cao, Souradip Chakraborty, Jun Shern Chan, Sachin Chanchani, Yulong Chen, Yiming Chen, Xinyuan Chen, Nuo Chen, Hanjie Chen, Xiudi Chen, Zeming Chen, An-Chieh Cheng, Xize Cheng, Cheng-Han Chiang, Josef Dai, David Dale, Yue Deng, Yifan Deng, Shizhe Diao, Bosheng Ding, Xuan Long Do, Yilun Du, Yupei Du, Salijona Dyrmishi, Dante Everaert, Zhenghan Fang, Bahare Fatemi, Jiazhan Feng, Shangbin Feng, Patrick Fernandes, Javier Ferrando, Christopher Fifty, Sarah E Finch, Matthew Finlayson, Lea Frermann, Mikhail Galkin, Songyang Gao, Ziteng Gao, Silin Gao, Sara Ghazanfari, Nathan Godey, Navita Goyal, Xinran Gu, Yuxian Gu, Yu Gu, Anchun Gui, Jiacheng Guo, Ashim Gupta, Paul Hagemann, Tianxing He, Zhengfu He, Juncai He, Leonhard Hennig, Konstantin Hess, Jennifer Hu, Xiaoyang Hu, Zhilei Hu, Weidong Huang, Yichong Huang, Ayyoob Imani, Qi Jia, Yifan Jiang, Hanwen Jiang, Yiding Jiang, Yang Jin, Youngjin Jin, Zhijing Jin, Emmeran Johnson, Josef Jon, David Jurgens, Ehsan Kamalloo, Junmo Kang, Jian Kang Mikhail Khodak, Hyunjae Kim, Soroush Abbasi Koohpayegani, Suhas Kotha, Jeongyeol Kwon, Sunjae Kwon, Philippe Laban, Zhibin Lan, Nayoung Lee, Deokjae Lee, Celine Lee, Heejun Lee, Jie Lei, Wenhao Li, Yafu Li, Yufei Li, Yanzeng Li, Yanzhou Li, Ziqiang Li, Zhaoyi Li, Ziheng Li, Xiaonan Li, Yinghao Li, Yu Li, Chengrui Li, Yingjie Li, Yunlong Liang, Baohao Liao, Kezhou Lin, Licong Lin, Enrico Liscio, Xiangyan Liu, Chenzhengyi Liu, Yixin Liu, Xingbin Liu, Haolin Liu, Xiao Liu, Yajiao Liu, Meng Liu, Tianyang Liu, Wei Liu, Qingyu Lu, Pan Lu, Junyu Lu, Zhengyi Luo, Yang Luo, Ang Lv, Junhyung Lyle, Jiajun Ma, Kaixin Ma, Ziqiao Ma, Mounica Maddela, Chaitanya Malaviya, Zhiyu Mei, Ethan Mendes, Fatemehsadat Mireshghallah, Niloofar Mireshghallah, Mircea Mironenco, Takeru Miyato, Fengran Mo, Xinyi Mou, Niklas Muennighoff, Cheolwon Na, Piotr Nawrot, Mang Ning, Longshen Ou, Siqi Ouyang, Lorenzo Pacchiardi, Ziqi Pang, Sara Papi, Letitia Parcalabescu, Tanmay Parekh, Aleksandar Petrov, Lucía Pitarch, Moritz Plenz, Manish Prajapat, Joan Puigcerver, Valentina Pyatkin, Shuofei Qiao, Yujia Qin, Chengwei Qin, Sigal Raab, Hossein A Rahmani, Siyu Ren, Yubing Ren, Ruiyang Ren, Yangjun Ruan, Michael J Ryan, Shoumik Saha, Vageesh Saxena, Michael Saxon, Alexander Scarlatos, Agam Shah, Erfan Shayegani, Behzad Shayegh, Xiangqing Shen, Sheng Shen, Ruizhe Shi, Zhengliang Shi, Kensen Shi, Ziyi Shou, Prasann Singhal, Jasivan Alex Sivakumar, Junru Song, Chunjin Song, Nikita Srivatsan, Michal Štefánik, Hao Sun, Mingjie Sun, Weiwei Sun, Zhiqing Sun, Xiaohang Tang, Liyan Tang, Eshaan Tanwar, Jiayan Teng, Davide Testa, Changyao Tian, Yufei Tian, Eric Todd, Benjamin Towle, Austin Tripp, Yi Tu, Rheeya Uppaal, Lazar Valkov, Neeraj Varshney, Artem Vazhentsev, Yiming Wang, Qifan Wang, Zhaoyang Wang, Lirui Wang, Zhicheng Wang, Weiqi Wang, Jiaan Wang, Boshi Wang, Haiming Wang, Huimin Wang, Yun-Cheng Wang, Runzhe Wang, Yu Wang, Yidong Wang, Licheng Wen, Te-Lin Wu, Yu-Yu Wu, Qianhui Wu, Dongming Wu, Tong Wu, Zijun Wu, Mengzhou Xia, Jian Xie, Yiming Xie, Weiwen Xu, Yi Xu, Xilie Xu, Derek Xu, Shohei Yamasaki, Hao Yan, Chenghao Yang, Xianjun Yang, Sen Yang, Bingsheng Yao, Qinyuan Ye, Fan Yin, Haneul Yoo, Kiyoon Yoo, Xinyan Velocity Yu, Jianfei Yu, Qiying Yu, Mo Yu, Zichun Yu, Yue Yu, Youliang Yuan, Zihao Yue, Xiang Yue, Yuanwen Yue, Daoguang Zan, Zhiyuan Zeng, Guangtao Zeng, Yuheng Zha, Runzhe Zhan, Jiaxu Zhang, Zhexin Zhang, Chen Zhang, Xinlu Zhang, Yabo Zhang, Renrui Zhang, Kechi Zhang, Ruoyu Zhang, Feng Zhang, Siyan Zhao, Junhao Zheng, Wenjie Zheng, Ming Zhong, Yan Zhou, Pei Zhou, Yangqiaoyu Zhou, Aojun Zhou, Xuekai Zhu, Luyao Zhu, Yanqiao Zhu, Dele Zhu, Andrew Zhu, Wenjie Zhuo and Caleb Ziems for contributing author-written questions about their ACL 2023 and/or ICLR 2024 papers.

## B Annotation Details

We provide instructions regarding manually inspecting questions in Table 1. We sent out emails and Google Forms to recruit ACL 2023 and ICLR 2024 authors for author-written questions, and the templates can be found in Table 10 and Table 11 respectively.

## C Retrieval Corpus

The LitSearch retrieval corpus P consists of ACL Anthology and ICLR papers extracted from S2ORC. Here we describe how we identify those papers in S2ORC: We isolate ACL anthology papers from S2ORC by identifying entries whose metadata includes an ACL Anthology ID. We identify ICLR papers utilizing a combination of the venue-based queries to Semantic Scholar’s Academic Graph API and by title-matching using titles of accepted papers scraped from the official ICLR website.

## D Retriever details

We list the full HuggingFace checkpoint paths corresponding to the dense retrievers we use in Table 9. We use the following instructions for the instruction-finetuned embedding models: “Represent the research question for retrieving relevant research paper abstracts:” for encoding queries; “Represent the title and abstract of the research paper for retrieval:” for encoding papers when using Instructor-XL for retrieval using paper titles and abstracts; when performing retrieval using paper titles and abstacts with GritLM-7B, we use the instruction “Given a research query, retrieve the title and abstract of the relevant research paper”.

<table><tr><td>Retriever</td><td>HuggingFace Checkpoint</td></tr><tr><td>GTR-T5-large</td><td>sentence-transformers/gtr-t5-large</td></tr><tr><td>Instructor-XL</td><td>hkunlp/instructor-x1</td></tr><tr><td>E5-large-v2</td><td>intfloat/e5-large-v2</td></tr><tr><td>GritLM-7B</td><td>GritLM/GritLM-7B</td></tr></table>

Table 9: HuggingFace checkpoints we use for each dense retriever.

## E Prompts and Additional Statistics

Table 12 shows the prompt we use for generating inline-citation questions via GPT-4. Table 13 shows the reranking prompt for GPT-4o. Table 14 shows a more detailed statistics about LitSearch.

```handlebars
Hi {{annotator name}},
We hope this email finds you well!
First, congrats on your paper's acceptance to {{conference name}}! We are [REDACTED] from [REDACTED] who are working on constructing a new challenging retrieval benchmark where the task is to retrieve relevant research papers given a research query. Would you be willing to dedicate 2 minutes to write a literature-search question about your {{conference name}} paper? Here's the link to the google form: {{link}}.
Your contribution will help us build better, more challenging evaluations for large language models. We will make sure to list you as a contributor to our benchmark (unless you prefer otherwise). Thank you!
Best,
{{author 1}}
{{author 2}}
```  
Table 10: Email template sent out to ICLR 2024 and ACL 2023 authors for collecting author-written questions.

![](images/6a9b4e2dd78ed82386156fd69a06fb71ba28c55632785eed5371975ea70612ee.jpg)  
Table 11: Instructions provided in the Google Forms sent to ICLR 2024 and ACL 2023 authors for collecting author-written questions.

![](images/e9dc2916bb1ed66249edb37069548bf1b0cb50448a276bcafaee1af4f50dfa00.jpg)  
Table 12: The prompt used for generating questions from inline citations using GPT-4.

![](images/60751a977115124344076c20fe36b9a96a18cafbcead4c03a7afc541ac3721f1.jpg)  
Table 13: The prompt used for reranking retrieved documents using GPT-4o (adapted from Sun et al., 2023a).

<table><tr><td rowspan="2"></td><td colspan="3">Broad</td><td colspan="3">Specific</td><td rowspan="2">Total #Q</td></tr><tr><td>#Q</td><td>Avg. L</td><td>Overlap</td><td>#Q</td><td>Avg. L</td><td>Overlap</td></tr><tr><td colspan="8">Inline-Citation Questions</td></tr><tr><td>ACL-sourced</td><td>32</td><td>24.8</td><td>0.33</td><td>66</td><td>26.0</td><td>0.35</td><td>98</td></tr><tr><td>Non-ACL-sourced</td><td>88</td><td>19.1</td><td>0.33</td><td>165</td><td>20.5</td><td>0.34</td><td>253</td></tr><tr><td colspan="8">Author-written Questions</td></tr><tr><td>ACL 2023</td><td>25</td><td>14.5</td><td>0.41</td><td>130</td><td>18.1</td><td>0.42</td><td>155</td></tr><tr><td>ICLR 2024</td><td>10</td><td>19.0</td><td>0.49</td><td>81</td><td>17.6</td><td>0.45</td><td>91</td></tr></table>

Table 14: Detailed statistics for LitSearch.


---

# 2504.00678_LLM增强的多阶段推荐系统

[2504.00678](https://arxiv.org/abs/2504.00678)

# RapidPD: Rapid Human and Pet Presence Detection System for Smart Vehicles via Wi-Fi

HANCHENG GUO

South China University of Technology, Guangzhou, China

ZHEN CHEN , Senior Member, IEEE

University of Macau, Macao, China

MO HUANG , Senior Member, IEEE

University of Macau, Macao, China

XIUYIN ZHANG , Fellow, IEEE

South China University of Technology, Guangzhou, China

Abstract—Heatstroke and life threatening incidents resulting from the retention of children and animals in vehicles pose a critical global safety issue. Current presence detection solutions often require specialized hardware or suffer from detection delays that do not meet safety standards. To tackle this issue, by remodeling channel state information (CSI) with theoretical analysis of path propagation, this study introduces RapidPD, an innovative system utilizing CSI in subcarrier dimension to detect the presence of humans and pets in vehicles. The system models the impact of motion on CSI and introduces motion statistics in subcarrier dimension using a multi-layer autocorrelation method to quantify environmental changes. RapidPD is implemented using commercial Wi-Fi chipsets and tested in real vehicle environments with data collected from 10 living organisms. Experimental results demonstrate that RapidPD achieves a detection accuracy of 99.05% and a true positive rate of 99.32% within a 1-second time window at a low sampling rate of 20 Hz. These findings represent a significant advancement in vehicle safety and provide a foundation for the widespread adoption of presence detection systems.

Index Terms—Wi-Fi sensing, smart car, presence detection, channel state information.

Manuscript received XXXXX 00, 0000; revised XXXXX 00, 0000; accepted XXXXX 00, 0000. (Corresponding author: Zhen Chen)

Authors’ address: Hancheng Guo, and Xiuyin Zhang are with School of Electronic and Information Engineering, South China University of Technology, Guangzhou 510006, China (e-mail: ee ghch@mail.scut.edu.cn; zhangxiuyin@scut.edu.cn). Zhen Chen, and Mo Huang are with the State Key Laboratory of Analog and Mixed-Signal VLSI/Institute of Microelectronics, University of Macau, Macao 999078, China (e-mail: chenz.scut@gmail.com; mohuang@um.edu.mo).

## I. INTRODUCTION

OVER the past decade, device-free passive detection [1] has gradually evolved from an emerging technology that allows for the detection of entities without carrying any equipment. To ensure the safety of people’s lives and properties, device-free passive detection has been studied and applied in many fields, including intrusion detection, human behavior pattern recognition, and detecting the presence of living organisms in hazardous environments. With the popularity of vehicles, the serious consequences for children or animals due to retention in vehicles have received widespread attention worldwide [2]–[7]. The European New Car Assessment Programme (Euro NCAP) has put forward regulatory requirements for child presence detection (CPD) systems in 2023 [8]. Vehicles equipped with presence detection systems can detect and alert children or pets left alone in the vehicle to avoid heatstroke or even life threatening incidents.

Currently, numerous technological solutions are being applied for device-free passive presence detection systems. Early systems for detecting the presence of living organisms were usually based on contact weight or pressure sensors [9]–[11]. Davis [10] published a weight sensor-based child presence detection device that is simple to implement but difficult to distinguish inanimate objects from living beings. To address this limitation, capacitive or electrical sensor-based schemes [12]– [14] have emerged as a more refined solution, for example, Ranjan and George [13] introduced a childleft-behind warning system based on the capacitive sensing principle. However, this method is constrained by its limited detection range, which is restricted to the seat. In contrast, methods utilizing pyroelectric infrared (PIR) sensors [15]–[17] offer a broader detection range through infrared radiation. Despite this advantage, these sensors are prone to temperature fluctuations, which can diminish their reliability in practical applications. To overcome these challenges, Jaworek-Korjakowska et al. presented the SafeSO system [18] based on computer vision for seat occupancy classification. Computer visionbased schemes [18]–[21] are temperature-independent and easily distinguish between living and non-living objects. However, their reliance on specialized camera equipment drives up system costs and raises concerns about potential privacy violations. On the contrary, radarbased schemes [22]–[30] are valued for their superiority in protecting privacy. Abedi et al. combined AI with radar technology to achieve in-vehicle occupant detection [22]– [24]. Companies such as InnoSenT [26], Infineon [27], NOVELIC [28], IEE [29], and Texas Instruments [30] have announced their presence detection system-on-chip (SOC) solutions. The above solutions require additional equipment, ranging from various sensors to millimeterwave radar. Compared to reusing existing equipment, the additional equipment required to implement a presence detection system increases the cost of the vehicle to varying degrees.

TABLE I  
Comparison of Existing Works on Presence Detection System

<table><tr><td>Methods</td><td>Coverage</td><td> $Low-cost^1$ </td><td>Accurate</td><td> $Responsive^2$ </td></tr><tr><td>Sensors (Weight/Pressure) [9]-[11]</td><td>Over Seat</td><td>✕</td><td>✕</td><td>Fast</td></tr><tr><td>Sensors (Capacitive/Electrical) [12]-[14]</td><td>Over Seat</td><td>✓</td><td>✕</td><td>Fast</td></tr><tr><td>Sensors (PIR) [15]-[17]</td><td> $LoS^3$ </td><td>✓</td><td>✕</td><td>Moderate</td></tr><tr><td>Computer Vision (Image/Video) [18]-[21]</td><td>LoS</td><td>✕</td><td>✓</td><td>Moderate</td></tr><tr><td>Radar (mmWave) [22]-[30]</td><td> $FoV^4$ </td><td>✕</td><td>✓</td><td>Fast</td></tr><tr><td>A two-step system with DL (Wi-Fi-Based) [32]</td><td>Over Rear Seat</td><td>O</td><td>✓</td><td>Fast</td></tr><tr><td>WiCPD (Wi-Fi-Based) [34]</td><td>Whole Car</td><td>O</td><td>✓</td><td>Moderate</td></tr><tr><td>UniMax Solution (Wi-Fi-Based) [36]</td><td>Whole Car</td><td>O</td><td>✓</td><td>Moderate</td></tr><tr><td>RapidPD (Ours, Wi-Fi-Based)</td><td>Whole Car</td><td>O</td><td>✓</td><td> $Fast (1sec)^5$ </td></tr></table>

<sup>1</sup> Derived from [34] and [42], with a indicating high-cost, a indicating low-cost, and a O indicating zero-cost reuse of existing equipment.  
<sup>2</sup> The method is referred to as Fast if the response is within 10 seconds required by Euro NCAP [43], otherwise, it is referred to as Moderate.  
<sup>3</sup> Line-of-Sight (LoS)  
File-of-View (FoV) of radar array  
<sup>5</sup> Length of time window

Our aim is to investigate the potential of reusing in-vehicle Wi-Fi devices for implementing a presence detection system, which provide a low-cost alternative to traditional solutions. especially in the low-end market accounting for the largest share of the automotive Wi-Fi router market [31]. For example, Wi-Fi based solutions [32]–[36] are recognized for their large sensing range and strong privacy protections. Shi et al. [32] developed a two-step rear seat child detection system based on commercial Wi-Fi devices using deep learning (DL) method to achieve the distinction between children, pets, and other objects with a detection accuracy of over 95%. Zeng et al. proposed WiCPD [34], which introduces a statistical electromagnetic model to explain the effect of motion on all the multipath. UniMax Electronics Inc [36] also implemented a CPD system based on Wi-Fi devices. These solution verifies that Wi-Fi is more cost-effective than millimeter-wave radar.

Meanwhile, some of the Wi-Fi based solutions explicitly reported their detection latency or window length. [33] and WiCPD [34] require a 20-second window to detect a sleeping child, and [36] takes up to a minute to identify whether there is biological movement in the car, neither of which meets Euro NCAP’s safety requirement of a 10-second response time. Although [32] requires only 52 × 30 sized CSI radio images for identification at a transmission rate of 100pkt/sec, the sensing range is limited to the rear seat of the vehicle. In addition, some works involving Wi-Fi are also worthy of attention. Li et al. introduced the difference between the CSI solution and the passive radar solution in Wi-Fi sensing technology [37]. Tang et al. [38], Li et al. [39] and Chen et al. [40] proposed sensing methods with passive Wi-Fi radar. Lyons et al. proposed presence detection in indoor scenarios [41], which has reference significance for life detection in cars. Table I. summarizes the challenges and comparative performance of various presence detection systems across different technologies.

As mentioned above, presence detection systems deployed in vehicles face additional difficulties due to the complicated multipath and Euro NCAP’s requirements for detection delay. We have built the RapidPD system based on commercial Wi-Fi chipsets to achieve rapid presence detection to avoid heatstroke or even life threatening incidents in vehicles. In summary, the major contributions of RapidPD are as follows:

1) A CSI model focusing on describing time-varying environments is proposed through a meticulous theoretical analysis of path propagation, which reveals the effect of changing propagation paths on the CSI matrix in subcarrier dimension. The model provides guidance and theoretical basis for utilizing the subcarrier dimension information of CSI.

2) An in-vehicle presence detection system, RapidPD, is developed that uniquely utilizes the subcarrier dimension of CSI. The system introduces a new method for characterizing motion statistics in subcarrier dimension that does not require long windows to accumulate changes, thus extending the range and applicability of Wi-Fi based sensing.

3) The multilayer autocorrelation method is innovatively applied to subcarrier dimension for the proposed RapidPD, which can enhance the detection of weak signals that are masked by the in-vehicle multipath environment.

4) The ability of the proposed RapidPD is demonstrated in experiments that can achieve an unprecedented 1-second detection window with over 99.05% accuracy, offering a valuable solution to prevent heatstroke and life threatening incidents.

The remainder of this article is organized as follows. First, the modeling of CSI is introduced in Section II. The design of RapidPD is presented in Section III followed by the implementation and evaluation in Section IV. Finally, Section V concludes this article.

![](images/98b0bff61067f804212743ced05e4f9dfd208cb95449878240d22d1f125fbd85.jpg)  
Fig. 1. The effect of living organism’s micro-movements on CSI.

## II. MODELING OF CSI

Fig. 1 illustrates the effect of micro-movements of living organisms (e.g., breathing while stationary) on CSI. Specifically, subcarriers of different frequencies emitted by the Tx arrive at the Rx via multiple paths, each experiencing distinct different amplitude attenuation and phase offsets. Invariant paths correspond to static vectors in the CSI, and varying paths result in correlated changes in amplitude and phase across different subcarriers. Under the influence of the time-varying phase offset [44]– [47], the CSI phase is difficult to utilize because of the instability even for the same state. In contrast, the CSI amplitude preserves the differences caused by linear combinations of CSI vectors corresponding to paths in different states (e.g., inhalation and exhalation), which are correlated in subcarrier direction.

To develop the modeling of CSI, we first analyze a scenario with a single path featuring only one scatterer, concentrating on how propagation path changes within the environment. Following this initial analysis, we consider the general case of multiple paths with multiple reflectors, describing how motion manifests itself in subcarrier dimension of the CSI.

## A. The Ideal Static CSI for Commercial Wi-Fi

Let $X ( t , f _ { i } )$ and $Y ( t , f _ { i } )$ denote the transmitted and received signals of a subcarrier with frequency $f _ { i }$ at time t, where $i \in \Omega _ { F }$ denotes the index of the subcarrier. The estimation equation of CSI $\hat { H } ( t , f _ { i } )$ can be expressed as follows [48]:

$$
\hat {H} (t, f _ {i}) = \frac {Y (t , f _ {i})}{X (t , f _ {i})},\tag{1}
$$

where $X ( t , f _ { i } )$ and $Y ( t , f _ { i } )$ can be expressed in the form of amplitude and phase, which are $P _ { X } ( t , f _ { i } ) e ^ { j \varphi _ { X } ( t , f _ { i } ) }$ and $P _ { Y } ( t , f _ { i } ) e ^ { j \varphi _ { Y } ( t , f _ { i } ) } . \ P _ { X } ( t , f _ { i } )$ and $P _ { Y } ( t , f _ { i } )$ denote the power of transmitted and received signals. $\varphi _ { X } ( t , f _ { i } )$ and $\varphi _ { Y } ( t , f _ { i } )$ denote their phase.

Consider the ideal noise-free static case, where the transmitted signal $X ( t , f _ { i } )$ and the received signal $Y ( t , f _ { i } )$ are degenerated into $X ( f _ { i } )$ and $Y ( f _ { i } )$ . First, disregarding the effect of noise, assume that there is only one scattering point in the propagation space of the signal. Since the subcarrier frequency interval $\Delta f$ is much smaller than with the Wi-Fi channel center frequency $f _ { C }$ (on the order of GHz), the reflection characteristics of an object can be similar for each subcarrier, with subcarriers of different frequencies experiencing the same path. At this point, according to the radar distance equation [49], the CSI amplitude $P _ { X } ( f _ { i } )$ and $P _ { Y } ( f _ { i } )$ extracted from a Wi-Fi device using omnidirectional antennas should be expressed as follows:

$$
P _ {Y} (f _ {i}) = G _ {T x} (f _ {i}) G _ {R x} (f _ {i}) \frac {\sigma_ {s}}{4 \pi R _ {1} ^ {2}} \frac {\sigma_ {R x}}{4 \pi R _ {2} ^ {2}} P _ {X} (f _ {i}),\tag{2}
$$

where $G _ { T x } ( f _ { i } )$ and $G _ { R x } ( f _ { i } )$ denote gains obtained from the Tx antenna and Rx antenna respectively for the subcarrier with frequency $f _ { i } , \ \sigma _ { s }$ represents the radar cross-section (RCS) of the scatterer $s , \sigma _ { R x }$ represents the effective area of the receiving antenna, and $R _ { 1 }$ and $R _ { 2 }$ denote the distances of the transmitting antenna from the scatterer and the scatterer from the receiving antenna.

In addition, the phase of the transmitted signal $\varphi _ { X } ( f _ { i } )$ and received signal $\varphi _ { Y } ( f _ { i } )$ of a Wi-Fi device using an omnidirectional antenna can be expressed as:

$$
\varphi_ {Y} (f _ {i}) = \frac {2 \pi f _ {i}}{c} (R _ {1} + R _ {2}) + \pi + \varphi_ {X} (f _ {i}),\tag{3}
$$

where c denotes the speed of light, and $\pi$ is half-wave losses during the reflection. Therefore, when there is only one propagation path l and a single scatterer, the estimation equation of CSI $\hat { H } _ { l } ( t , f _ { i } )$ can be expressed as follows:

$$
\begin{array}{c} \hat {H} _ {l} (f _ {i}) = \frac {Y (f _ {i})}{X (f _ {i})} \\ = G _ {T x} (f _ {i}) G _ {R x} (f _ {i}) \frac {\sigma_ {s}}{4 \pi R _ {1} ^ {2}} \frac {\sigma_ {R x}}{4 \pi R _ {2} ^ {2}} \\ \exp \left[ j \left(\frac {2 \pi f _ {i}}{c} (R _ {1} + R _ {2}) + \pi\right) \right]. \end{array}\tag{4}
$$

Considering the general case, there are $M \ - \ 1$ scatterers along a propagation path l, resulting in a total of M propagation segments. Thus, the estimation equation of CSI ${ \hat { H } } _ { l } ( t , f _ { i } )$ can be expressed as follows:

![](images/19a8bd201bbbf4d8967af772c7e2f993bb76cc0fd604df4bfd3acc09560daf0e.jpg)  
Fig. 2. System architecture of RapidPD.

$$
\begin{array}{l} \hat {H} _ {l} (f _ {i}) = G _ {T x} (f _ {i}) G _ {R x} (f _ {i}) \prod_ {m = 1} ^ {M} \frac {\sigma_ {l , m}}{4 \pi R _ {l , m} ^ {2}} \\ \exp \left[ j \left(\frac {2 \pi f _ {i}}{c} \sum_ {m = 1} ^ {M} R _ {l, m} + (M - 1) \pi\right) \right], \end{array}\tag{5}
$$

where $\sigma _ { l , m }$ denotes the RCS of scatterer $s _ { m }$ in the propagation path $l , \ \sigma _ { l , M } = \sigma _ { R x }$ , and $R _ { l , m }$ denotes the length of the mth segment of propagation path l.

Considering the unavoidable multipath situation, the actual CSI is a linear combination of multiple ${ \hat { H } } _ { l } ( f _ { i } )$ With $L$ paths in the environment, the estimation equation of CSI ${ \hat { H } } ( f _ { i } )$ can be expressed as follows:

$$
\hat {H} (f _ {i}) = \sum_ {l = 1} ^ {L} \hat {H} _ {l} (f _ {i}).\tag{6}
$$

## B. Impact of Motion on CSI

Considering the ideal noise-free dynamic case, we assume that the environment experiences subtle micromovements over time, which are difficult to detect. For instance, stationary human breathing causes the chest to move slightly, typically between 5 mm and 12 mm [50]. Given these small movements, the reflections along each signal path are expected to remain mostly unchanged, with only minor variations in the distances the signals travel. Building on this analysis, the estimation equation of time-varying CSI $\hat { H } ( t , f _ { i } )$ can be expressed as follows:

$$
\begin{array}{l} \hat {H} (t, f _ {i}) = \sum_ {l = 1} ^ {L} \hat {H} _ {l} (t, f _ {i}) \\ \qquad = G _ {T x} (t, f _ {i}) G _ {R x} (t, f _ {i}) \sum_ {l = 1} ^ {L} \left\{\prod_ {m = 1} ^ {M} \frac {\sigma_ {l , m}}{4 \pi R _ {l , m} ^ {2} (t)} \right. \\ \qquad \exp \left[ j \left(\frac {2 \pi f _ {i}}{c} \sum_ {m = 1} ^ {M} R _ {l, m} (t) + (M - 1) \pi\right) \right] \Bigg \}. \end{array}\tag{7}
$$

Since the changes in length of propagation paths caused by micro-movements are much shorter than the overall path length in typical application scenarios, the amplitude term in (7) can be considered constant over time. Moreover, when we consider the order-of-magnitude relationship between the subcarrier frequency $f _ { i } ,$ , the speed-of-light $c ,$ and the total distance $\textstyle \sum _ { m = 1 } ^ { M } { \dot { R } } _ { l , m } ( t )$ of path l, it becomes evident that these micro-movements are more likely to affect the phase components of (7).

Considering that the gain of Tx and Rx is flat over the channel frequency range, $G _ { T x } ( t , f _ { i } )$ and $G _ { R x } ( t , f _ { i } )$ degenerates into $G _ { T x } ( t )$ and $G _ { R x } ( t )$ . Let the variation in the total distance of propagation path l for $t _ { 0 }$ be $\Delta R _ { l } ( t ) =$ $\begin{array} { r } { \sum _ { m = 1 } ^ { M } \left[ R _ { l , m } ( t ) - \bar { R _ { l , m } ( t _ { 0 } ) } \right] } \end{array}$ , and let the invariant term in (7) be denoted as $H _ { l } ^ { \prime }$ . The estimation equation of CSI in the ideal noise-free case with micro-movements can be expressed as follows:

$$
\hat {H} (t, f _ {i}) = G _ {T x} (t) G _ {R x} (t) \sum_ {l = 1} ^ {L} H _ {l} ^ {\prime} (f _ {i}) \exp \left[ j \frac {2 \pi f _ {i}}{c} \Delta R _ {l} (t) \right].\tag{8}
$$

From (8), the estimation equation of CSI in the ideal noise-free case with micro-movements can be expressed as a linear combination of complex vectors, each with different phase offsets, after excluding the gains of Tx and Rx. Specifically, the complex vectors $H _ { l } ^ { \prime } ( f _ { i } )$ correspond to the static environment, while the phase offsets $( 2 \pi f _ { i } / c ) \Delta R _ { l } ( t )$ are associated with the time t and subcarrier frequency $f _ { i }$ . When the environment changes, the fluctuation in any subcarrier is related to the variation in the total distance $\Delta R _ { l } ( t )$ of the propagation path. Additionally, the variation among CSI entries is related to the subcarrier frequency $f .$ It suggests that by finding a benchmark for environmental characterization (e.g., CSI entries at $t _ { 0 } ) .$ , information on environmental changes can be sensitively extracted from the subcarrier dimension without cumulative change in the time dimension.

The above modeling illustrates that environmental changes can lead to correlation changes between different subcarriers of CSI entries. In order to achieve detection of the lifeforms’ presence in the vehicle, a indicator is needed to be constructed to quantify such changes to describe the time-varying environment. The indicator will be covered in the next section on system design.

![](images/59066a3b2ac49e7ad2ebb2906fd662ba9db5383cd56d37d29bdb7dcbc324201f.jpg)  
(a) Unnormalized amplitude on subcarriers with AGC.

![](images/fb0985a8dba4ef84be1904e3eb2eee11b426aff6f538990c41cf0222d7630e1a.jpg)  
(b) Normalized amplitude on subcarriers with s(t).  
Fig. 3. Examples of CSI amplitude in a static case before and after normalization, with AGC compensation and normalized information s(t).

## III. RAPIDPD DESIGN

## A. System Overview

Fig. 2 depicts the overview of RapidPD, which consists of four components including CSI extraction, CSI preprocessing, subcarrier dimension-based motion target detector, and presence detection indicator. The CSI matrix extracted from the hardware is first preprocessed to obtain its normalized amplitude. Afterward, the benchmark for environmental characterization is further estimated and subtracted in the motion target detector based on the normalized CSI. Subsequently, multilayer autocorrelation method in subcarrier dimension is applied to the processed CSI entries and the average motion statistics are calculated. Finally, the overall motion statistics are further computed and threshold-based judgments are performed to output a presence detection indication.

## B. CSI Preprocessing

Unlike the ideal case, the measurement of CSI is influenced by unstable perturbations and noise. Based on previous works [44]–[47], the reported unstable perturbations include time-varying phase offset and imperfect compensation of automatic gain control (AGC).

Considering the time-varying phase offset and the extensive computations involved in complex signals, we opt to use only the amplitude for detection referring to existing work [51]–[55]. The measurement of CSI amplitude $| H ( t , f _ { i } ) |$ can be expressed as follows:

$$
| H (t, f _ {i}) | = G _ {a g c} (t) \left| \hat {H} (t, f _ {i}) \right| + \epsilon^ {\prime} (t, f _ {i}),\tag{9}
$$

where |·| denotes the operations of taking the amplitude taken over the complex signal, $\epsilon ^ { \prime } ( t , f _ { i } )$ is the measurement noise and $G _ { a g c } ( t )$ denotes the gain of AGC compensation.

Due to the resolution limitations of the hardware, the total gain provided by the low noise amplifier and the programmable gain amplifier in AGC cannot fully compensate for the signal’s amplitude attenuation. Consequently, the measured amplitude also includes the amplifier’s uncertainty error, leading to an amplitude offset.

Amplitude offset is observed in the actual data, even though the amplitude has been compensated by AGC. As shown in Fig. 3(a), notice that the CSI amplitude fluctuates with the AGC field and there are several significant mutations following a uniform trend across all subcarriers within the window shown.

Since the CSI amplitude represents the ratio of received to transmitted power, it can be considered received power under the condition that transmitted power is normalized. As the gain obtained by AGC compensation is the same for each subcarrier, we can eliminate imperfect compensation by normalizing the total power of the received signal, which is the sum of each CSI entry’s amplitude.

First, after obtaining the AGC-compensated amplitudes, the sum of each CSI entry’s amplitude s(t) is calculated:

$$
s (t) = \sum_ {i \in \Omega_ {F}} | H (t, f _ {i}) |.\tag{10}
$$

Subsequently, the CSI amplitude was subjected to a normalization operation to obtain the normalized amplitude matrix $\tilde { H } ( t , f _ { i } )$ as follows:

$$
\begin{array}{l} \tilde {H} (t, f _ {i}) = \frac {| H (t , f _ {i}) |}{s (t)} \\ = \frac {G (t)}{s (t)} \left| \sum_ {l = 1} ^ {L} H _ {l} ^ {\prime} (f _ {i}) e ^ {j \frac {2 \pi f _ {i}}{c} \Delta R _ {l} (t)} \right| + \epsilon (t, f _ {i}), \end{array}\tag{11}
$$

where the combined gain $G ( t ) = G _ { a g c } ( t ) G _ { T x } ( t ) G _ { R x } ( t )$ and the noise term $\epsilon ( t , f _ { i } ) = \epsilon ^ { \prime } ( t , f _ { i } ) / s ( t )$

As shown in Fig. 3(b), the normalized amplitude exhibits stability in a static case. Furthermore, as shown in (11), the normalized CSI amplitude retains the difference caused by the linear combination of the CSI vectors corresponding to the time-varying paths length $\Delta R _ { l } ( t )$ even if the CSI phase is discarded.

## C. Subcarrier Dimension-based Motion Target Detector

For static environments, the estimation equation of CSI $\hat { H } ( t , f _ { i } )$ should be invariant because the electromagnetic wave passes through invariant paths [56]. When the unstable Perturbations of CSI are excluded, the variation in the measurement of CSI $H ( t , f _ { i } )$ can be attributed to the noise term $\epsilon ( t , f _ { i } )$ , as illustrated in Fig. 3(b).

The fact that $\epsilon ( t , f _ { i } )$ can be approximated as additive Gaussian white noise with zero mean, which is independent both across different times and subcarriers [56], that is, $\epsilon ( t _ { 1 } , f _ { 1 } )$ and $\epsilon ( t _ { 2 } , f _ { 2 } )$ are independent for $\forall t _ { 1 } \neq t _ { 2 } , f _ { 1 } \neq f _ { 2 } .$

When there is no detection target in the environment, each CSI entry remains stable, and the variations among CSI entries related to the subcarrier frequency are dominated by the noise $\epsilon ( t , f _ { i } )$ . Ideally, the noise sequence has no autocorrelation at non-zero lags.

When a detection target with micro-movements is present in the environment, fluctuations in the CSI matrix occur in both the time and subcarrier dimensions. The variation among the CSI entries related to the subcarrier frequency results from both the noise $\epsilon ( t , f _ { i } )$ and the variation in the total distance $\Delta R _ { l } ( t )$ of the propagation path together. Notably, $\Delta R _ { l } ( t )$ in (11) contributes to a higher autocorrelation at non-zero lags.

To capture these environmental changes and detect the presence of in-vehicle living organisms, we constructively apply the autocorrelation function (ACF) to the CSI in subcarrier dimension. This approach differs from treating each subcarrier as an independent time series [34], which we refer to as the time dimension analysis. Instead, we apply the ACF to each processed CSI entry, which is the subcarrier dimension we focus on.

CSI depicts the channel properties of the physical layer in the frequency domain and reveals the combined effects of multipath propagation of the signal, where each CSI entry represents a channel frequency response (CFR) [57]. For each time window, we average the preprocessed CSI matrix in time dimension to smooth the CFR. This averaged CFR is used to be the benchmark for environmental characterization $\bar { H } ( f _ { i } )$ , which can be expressed as follows:

$$
\bar {H} (f _ {i}) = \frac {1}{T} \sum_ {t = 1} ^ {T} \tilde {H} (t, f _ {i}),\tag{12}
$$

where T denotes the length of the time window.

In a static environment, the benchmark for environmental characterization $\bar { H } ( f _ { i } )$ will truthfully characterize the static environment because the noise is smoothed from CFR at this point. In a environment with living organisms, the difference between any CSI entry and $\bar { H } ( f _ { i } )$ still has a residual component with high autocorrelation, which we denote as $H _ { D } ( t , f _ { i } )$ and expressed as follows:

![](images/e5d48bc34ccbc14f5235b59ab74f32cbf0665570ad32923a44e133380564af41.jpg)  
Fig. 4. ACF in subcarrier dimension for different cases.

$$
H _ {D} (t, f _ {i}) = \tilde {H} (t, f _ {i}) - \bar {H} (f _ {i}).\tag{13}
$$

Denote ACF of $H _ { D } ( t , f _ { i } )$ in subcarrier dimension as $\rho ( t , \upsilon )$ , which is defined as follows:

$$
\rho (t, v) = \frac {\gamma (t , v)}{\gamma (t , 0)},\tag{14}
$$

where $\gamma ( t , \upsilon )$ denotes the self-covariance function of the CSI entry at time t as follows:

$$
\gamma (t, v) = \operatorname{cov} [ H _ {D} (t, f _ {i} - v), H _ {D} (t, f _ {i}) ].\tag{15}
$$

In the actual calculation, the sample self-covariance function $\hat { \gamma } ( t , \upsilon )$ is used instead of the self-covariance function, which is defined as:

$$
\begin{array}{l} \hat {\gamma} (t, v) = \hat {\gamma} (t, k \Delta f) \\ = \frac {1}{K} \sum_ {i = 1 + k} ^ {K} H _ {D} (t, f _ {i - k}) H _ {D} (t, f _ {i}), \end{array}\tag{16}
$$

where K denotes the total number of subcarriers and let $v = k \Delta f .$

Using the above method on the actual measured data to calculate $\rho ( t , \upsilon )$ , the results are shown in Fig. 4. ACF in the static case and dynamic case with human micromovements are indicated by the blue solid line and the red dashed line. For the static case, the ACF at non-zero lags fluctuates around the zero value. In contrast, for the dynamic cases, the ACF at non-zero lags shows a larger magnitude, making it clearly distinguished from the static scenarios.

Although noise in real systems may not always fully satisfy the independence condition, leading to some autocorrelation at non-zero lags, it is encouraging that the ACF in the subcarrier dimension can still effectively distinguish the presence or absence of living organisms in practical applications. Additionally, we observed that at low levels of Sensing Signal to Noise Ratio (SSNR) [58], the fluctuations of CSI caused by environmental changes are often masked by noise. To address this, we employ a multi-layer autocorrelation method [59], [60] to improve the SSNR. Specifically, the signal $\rho _ { n } ( t , v )$ obtained by the n-layer ACF in the subcarrier dimension can be expressed as follows:

![](images/e0e66344a8f196eea9e1e0ac43c3be13878990aab46ecddcf1e3bb7da3a406e8.jpg)  
(a) On additive Gaussian white noise.

![](images/99b4c608d964333fa524ebda563d37b5af4bffab9eb68de243f0c4bb606eae43.jpg)  
(b) On noisy sinusoidal signal.  
Fig. 5. Effectiveness of multi-layer autocorrelation method.

$$
\rho_ {n} (t, v) = \left\{ \begin{array}{l l} \frac {\rho_ {n - 1} (t , v)}{\rho_ {n - 1} (t , 0)} & n \geq 2 \\ \frac {\gamma (t , v)}{\gamma (t , 0)} & n = 1 \end{array} \right..\tag{17}
$$

Fig. 5 illustrates the effectiveness of the multilayer autocorrelation method in the case of low SSNR. When a low-frequency sinusoidal signal is superimposed with an additive Gaussian white noise, the multi-layer autocorrelation effects of the noise and noisy sinusoidal signals are shown in Fig. 5(a) and Fig. 5(b), respectively. As the number of layer n increases, the multi-layer ACF of noisy sinusoidal signal and noise are clearly distinguishable from each other gradually. The multi-layer ACF of the noisy sinusoidal signal gradually deviates from the value of zero, while that of the noise remains near the value of zero at non-zero lags.

## D. Presence Detection Indicator

Based on multi-layer ACF, we propose the motion statistics in subcarrier dimension, which is used to measure the changes in the environment and realize the presence detection of in-vehicle living organisms. The motion statistics $\psi _ { n } ( t )$ in subcarrier dimension based on n-layer ACF can be expressed as follows:

$$
\psi_ {n} (t) = \rho_ {n} (t, \Delta f).\tag{18}
$$

Combining all CSI entries in time windows, the average motion statistics $\phi$ in subcarrier dimension on a Tx-Rx stream can be expressed as follows:

$$
\phi = \sum_ {t = 1} ^ {T} \psi_ {n} (t).\tag{19}
$$

As shown in Fig. 6, we chose $n = 3$ to calculate the average motion statistics $\phi$ in subcarrier dimension for both the static case and the dynamic case with human micro-movements. These are indicated by the blue solid line and the red dashed line, respectively. The results show that the average motion statistics ϕ in the subcarrier dimension can effectively and clearly distinguish between these two scenarios.

![](images/6cca86b95dda14bc0ea816832de79739ec6f90d4b830c12610fe876fc7935895.jpg)  
Fig. 6. Average motion statistics ϕ for different cases.

The average motion statistics ϕ for the current time window is computed based on a single Tx-Rx stream, and for RapidPD with multiple Tx-Rx streams, $\Phi = \sum \phi$ combines the results of all Tx-Rx streams, which we refer to as the overall motion statistics.

After obtaining the overall motion statistics Φ for the current time window, a judgment needs to be made based on the set threshold $\eta .$ When $\Phi \geq \eta ,$ an organism is judged to be present, otherwise no organism is.

In practical applications, there may be sudden disturbances that cause data anomalies. Therefore, we obtain the judgments for $m$ windows and take the plural as the final presence detection indication output for smoothing the judgments.

## IV. EVALUATION

To comprehensively evaluate RapidPD, we conducted extensive experiments in a typical car and with real infants, children, pets, and adults to validate the detection performance of RapidPD.

## A. Methodology

Implementation: As shown in Fig. 7, we used a hardware platform based on Infineon’s commercial Wi-Fi chipsets CYW8x459 developed by Desay SV with dual bands at 2.4 and 5 GHz and with additional PCB antennas. RapidPD is deployed on two separate hardware platforms, each carrying a Wi-Fi chip that sends and receives data by programming different customized firmware. An antenna is set up on Rx to receive packets transmitted by two antennas of Tx at a 20 Hz sampling rate operating on a channel with a center frequency of 5775 MHz (channel 155), which has a bandwidth of 80 MHz and contains 234 obtainable subcarriers. As shown in Fig. 8, Tx antennas are located at the handles above the rear doors on each side of the vehicle, and the Rx antenna is located on the side of the center console adjacent to the glove box.

![](images/53ba57dbd93654adeaf849d6e6fbd236eaeffa1541e8f903421efdf8ab0c409a.jpg)  
Fig. 7. Hardware platform with additional PCB antennas.

![](images/d9f1057bb3a3115c9a2eaf4bf4aa3e2a2ff869d3aac523f315d3250d18175516.jpg)  
(a) Tx.

![](images/29f6c080000eb5b1607b46682c91902c79059fcdcc381d99b8af8ecbe5786f04.jpg)  
(b) Rx.  
Fig. 8. Position of the antenna.

RapidPD transfers the data collected in the hardware system to a computer and subsequently processes and analyzes it in MATLAB. To realize an accurate and sensitive presence detection system in vehicles, we take 1s duration data (20 packets at 20Hz sampling rate) as the window and have a 1s window movement step. The number of autocorrelation layers in the motion target detector is chosen as n = 3, and the number of windows for judgment smoothing in the presence detection indicator is chosen as m = 3.

Data Collection: The data collection possessed four main cases including 1) empty, 2) human, 3) dog, and 4) cat presence. As shown in Fig. 9, there are 11 positions in these cases, including 5 seats and corresponding foot positions and rear side seat lie-flat position, which have different types of organisms being tested. The details of the organisms are shown in Table II, with the pets participating in the experiment shown in Fig. 10.

![](images/e7eaed205e20ef057caf5a7b78b1942932296ea296f69acee9f37ed4ea11ce84.jpg)  
Fig. 9. Different test positions for living organisms.

![](images/db074397fbbb49edaa6741365fac7d6a65d6d494aaaebe46078e4edde203d36c.jpg)  
(a) Dog.

![](images/51b3e181d0745b1cf454386547e87e3b6d21df4b4e3a281295097303f511777f.jpg)  
(b) Cat.  
Fig. 10. Pets participating in the experiment.

TABLE II  
The details of organisms

<table><tr><td>#</td><td>Type</td><td>Age(Years)</td><td>Height(cm)</td><td>Weight(kg)</td></tr><tr><td>1</td><td>Infant</td><td>1</td><td>74</td><td>9.5</td></tr><tr><td>2</td><td>Child</td><td>3</td><td>92</td><td>13.8</td></tr><tr><td>3</td><td>Child</td><td>4</td><td>100</td><td>14.0</td></tr><tr><td>4</td><td>Child</td><td>5</td><td>114</td><td>19.0</td></tr><tr><td>5</td><td>Child</td><td>5</td><td>115</td><td>18.5</td></tr><tr><td>6</td><td>Child</td><td>6</td><td>120</td><td>26.0</td></tr><tr><td>7</td><td>Child</td><td>6</td><td>120</td><td>30.0</td></tr><tr><td>8</td><td>Adults</td><td>-</td><td>-</td><td>-</td></tr><tr><td>9</td><td>Dog</td><td>-</td><td>-</td><td>Small-sized</td></tr><tr><td>10</td><td>Cat</td><td>-</td><td>-</td><td>Medium-sized</td></tr></table>

Fig. 11 illustrates sample CSI matrixs for the four scenarios. Spectrograms are generated utilizing STFT with parameters NFFT=256 and OverlapLength=255. The waveforms of the static scenes demonstrate stability, with the human presence scene exhibiting strong respiratory fluctuations and the pet presence scene showing no clearly visible fluctuations. Distinguishably stronger components exist near zero frequency in the spectrogram for human presence scenario, with some cluttered frequency components in other three scenarios, strongest in the dog presence scenario and weakest in the static scenario.

The experiment was implemented over more than 4 months in different environments, including outdoor open spaces, parking structures, roadsides, and below an elevated bridge. We noted that RapidPD did not need to be altered in the different environments, therefore RapidPD is a calibration-free as well as fast-responding (only 1s of data is needed to complete the judgment) system for human and pet presence detection.

![](images/6348bc196c9667e1e3f1c07adfa34658eac9ef66159b7862e4c6af84b71d3bea.jpg)  
Fig. 11. Sample CSI matrix for each scenario.

![](images/01ee66346cc11143f068ab199259e533f07c65a3fef2dd20a444dbb4008b6807.jpg)  
(a) Relationship between performance and threshold η.

![](images/507e2517403bd86fb3c4a76d0039ef787dee2ae5d725ee913222123a7fea8467.jpg)  
(b) CDF curve.

![](images/47e74c6313d8f80bb45ee10a7cfca61f5bbd3aa0c33d588ce4c54b859b727320.jpg)  
(c) Judgment accuracy to threshold η.

![](images/986b8b372e48f87c32f24bc55a4a66f3d5b7c80172da61c963752ef307bb0b05.jpg)  
(d) Confusion matrix for RapidPD judgment at $\eta = 0 . 4 3 .$  
Fig. 12. Overall performance of RapidPD.

## B. Overall Accuracy

Fig. 12 illustrates the overall performance of RapidPD.

As shown in Fig. 12(a), the accuracy, true positive, and true negative rates vary with the judgment threshold η. The accuracy achieved a maximum of 99.05% at $\begin{array} { r l r } { \eta } & { { } = } & { 0 . 4 3 . } \end{array}$ , along with a 99.32% true positive rate and 1.64% false positive rate. Fig. 12(b) illustrates the CDF of the overall motion statistics in the subcarrier dimension of RapidPD, with the living and non-living cases well distinguished. Fig. 12(c) shows the curves of the relationship between threshold η and the judgment accuracy of the four scenarios. At the selected threshold $\eta = 0 . 4 3$ , all the four cases have high accuracy. Fig. 12(d) illustrates the confusion matrix for the judgment case at the chosen threshold, proving that judgment accuracy of the four cases are 98.36%, 99.61%, 99.83%, and 97.02%.

The overall accuracy described above was achieved using only a 1-second time window at a low sampling rate of 20Hz, which is an extremely fast response time for a presence detection system and fully meets the Euro NCAP requirement of no more than a 10-second delay.

![](images/2232b5bff3739be2304b45eae6910addb530b2f150584bd56f204ec65d70c929.jpg)  
Fig. 13. ROC curves of the benchmark method and RapidPD.

TABLE III  
Comparing the overall accuracy of motion target detector

<table><tr><td colspan="2">benchmark method</td><td colspan="2">RapidPD without multi-layer ACF</td><td colspan="2">RapidPD (with multi-layer ACF)</td></tr><tr><td>TPR</td><td>FPR</td><td>TPR</td><td>FPR</td><td>TPR</td><td>FPR</td></tr><tr><td>89.83%</td><td>20.41%</td><td>99.01%</td><td>3.16%</td><td>99.32%</td><td>1.64%</td></tr></table>

## C. Comparison With Existing Works

We also implemented a benchmark method that uses a time dimension-based motion target detector [56] to replace the subcarrier dimension-based motion target detector proposed in this paper. In addition to the benchmark and RapidPD methods, RapidPD-based methods without multi-layer autocorrelation have been implemented and evaluated as well. The overall accuracy is shown in Table III. It is obvious that RapidPD has a great improvement over the benchmark method under the same experimental setup. Compared to removing the multi-layer autocorrelation module, RapidPD obtains a much lower false positive rate.

Fig. 13 shows the ROC curves of the benchmark method and RapidPD, noting that the area under the curve for RapidPD is quite large. RapidPD possesses a significantly higher true positive rate than the benchmark method with the same false positive rate. This improvement can be attributed to the following reasons:

1) Theoretical support derived from re-modeling of CSI: By analyzing the signal propagation paths, the relevant effects of varying path lengths for different subcarriers are inferred. Compared to accumulating long-term differences in time dimension, the information on environmental changes can be extracted in a shorter time in subcarrier dimension.

2) Combining the information in subcarrier dimension: RapidPD analyzes the effect of motion on the subcarriers by focusing on their correlation properties rather than examining each subcarrier independently. Each entry in the CSI matrix contains extensive information about the environment, and environmental changes directly impact the correlation between these entries. By leveraging these correlation properties, RapidPD requires only a short time window (1 second) to achieve accurate presence detection.

3) Applying the multi-layer autocorrelation method innovatively: In complex in-vehicle multipath environments, signals undergo multiple reflections before being received, causing motion signals to be more easily drowned out by noise. In cases of low SSNR, RapidPD innovatively applies the multilayer autocorrelation method, improving accuracy by approximately 0.65% and reducing the false positive rate by around 1.52%.

## V. CONCLUSION

By re-modeling CSI with theoretical analysis of path propagation, this study introduces a novel approach to presence detection leveraging the subcarrier dimensions of the CSI matrix, providing a more precise motion statistics analysis and significantly enhancing detection capabilities. The proposed method based on multilayer autocorrelation provides a significant indicator for distinguishing the presence or absence of invehicle organisms. Extensive experiments validate the effectiveness of RapidPD, demonstrating an accuracy exceeding 99.05% and a true positive rate greater than 99.32% using only 1-second time windows at a lowlevel sampling rate of 20 Hz. This marks the first time subcarrier dimension information from the CSI matrix has been utilized for such sensitive detection, offering a groundbreaking contribution to in-vehicle safety and opening up new possibilities for the global adoption of advanced presence detection systems.

## ACKNOWLEDGMENT

The authors would like to acknowledge Desay SV for providing the hardware equipment and datasets required for this work.

## REFERENCES

[1] M. Youssef, M. Mah, and A. Agrawala, “Challenges: device-free passive localization for wireless environments,” in Proceedings of the 13th annual ACM international conference on Mobile computing and networking, 2007, pp. 222–229.

[2] C. McLaren, J. Null, and J. Quinn, “Heat stress from enclosed vehicles: moderate ambient temperatures cause significant temperature rise in enclosed vehicles,” Pediatrics, vol. 116, no. 1, pp. e109–e112, 2005.

[3] P. Ferrara, F. Vena, O. Caporale, V. Del Volgo, P. Liberatore, F. Ianniello, A. Chiaretti, and R. Riccardi, “Children left unattended in parked vehicles: a focus on recent italian cases and a review of literature,” Italian journal of pediatrics, vol. 39, pp. 1–4, 2013.

[4] D. Costa and A. Grundstein, “An analysis of children left unattended in parked motor vehicles in brazil,” International journal of environmental research and public health, vol. 13, no. 7, p. 649, 2016.

[5] J. Null. (2024, Sep.) No heat stroke. [Online]. Available: https://www.noheatstroke.org/

[6] N. Bradley-Siemens, “Environmental and situationalinjuries /deaththermal, chemical, electrical, hyperthermia, hypothermia, and drowning,” in Veterinary Forensic Medicine and Forensic Sciences. CRC Press, 2020, pp. 225–251.

[7] A. J. Carter, E. J. Hall, S. L. Connoll, Z. F. Russell, and K. Mitchell, “Drugs, dogs, and driving: The potential for yearround thermal stress in uk vehicles,” Open veterinary journal, vol. 10, no. 2, pp. 216–225, 2020.

[8] 2024 Euro NCAP. (2017, Sep.) Euro ncap 2025 roadmap. [Online]. Available: https://cdn.euroncap.com/media/ 30700/euroncap-roadmap-2025-v4.pdf

[9] M. A. Rossi, “Warning system for detecting presence of a child in an infant seat,” Aug. 15 2000, uS Patent 6,104,293.

[10] L. Davis, “Child carseat alert system,” Jul. 31 2007, uS Patent 7,250,869.

[11] C. J. Cole, “System to detect the presence of an unattended child in a vehicle,” Jan. 30 2007, uS Patent 7,170,401.

[12] B. George, H. Zangl, T. Bretterklieber, and G. Brasseur, “Seat occupancy detection based on capacitive sensing,” IEEE Transactions on Instrumentation and Measurement, vol. 58, no. 5, pp. 1487–1494, 2009.

[13] A. Ranjan and B. George, “A child-left-behind warning system based on capacitive sensing principle,” in 2013 IEEE International Instrumentation and Measurement Technology Conference (I2MTC). IEEE, 2013, pp. 702–706.

[14] J. Albesa and M. Gasulla, “Occupancy and belt detection in removable vehicle seats via inductive power transmission,” IEEE Transactions on Vehicular Technology, vol. 64, no. 8, pp. 3392– 3401, 2014.

[15] H. Mahler, M. Rechsteiner, and R. Abrach, “Presence detector and its application,” Nov. 26 2002, uS Patent 6,486,778.

[16] P. Zappi, E. Farella, and L. Benini, “Tracking motion direction and distance with pyroelectric IR sensors,” IEEE Sensors Journal, vol. 10, no. 9, pp. 1486–1494, 2010.

[17] F. R. Rashidi and I. H. Muhamad, “Vehicle’s interior movement detection and notification system,” Recent advances in automatic control, modelling and simulation, pp. 139–144, 2013.

[18] J. Jaworek-Korjakowska, A. Kostuch, and P. Skruch, “SafeSO: interpretable and explainable deep learning approach for seat occupancy classification in vehicle interior,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2021, pp. 103–112.

[19] H. Cai, D. Lee, H. Joonkoo, Y. Fang, S. Li, and H. Liu, “Embedded vision based automotive interior intrusion detection system,” in 2017 IEEE International Conference on Systems, Man, and Cybernetics (SMC). IEEE, 2017, pp. 2909–2914.

[20] R. Panda and A. K. Roy-Chowdhury, “Multi-view surveillance video summarization via joint embedding and sparse optimization,” IEEE Transactions on Multimedia, vol. 19, no. 9, pp. 2010–2021, 2017.

[21] C.-T. Fan, Y.-K. Wang, and C.-R. Huang, “Heterogeneous information fusion and visualization for a large-scale intelligent video surveillance system,” IEEE Trans. Syst., Man, Cybern., Syst., vol. 47, no. 4, pp. 593–604, 2016.

[22] H. Abedi, M. Ma, J. He, J. Yu, A. Ansariyan, and G. Shaker, “Deep learning-based in-cabin monitoring and vehicle safety system using a 4-d imaging radar sensor,” IEEE Sensors Journal, vol. 23, no. 11, pp. 11 296–11 307, 2023.

[23] H. Abedi, S. Luo, V. Mazumdar, M. M. Riad, and G. Shaker, “Aipowered in-vehicle passenger monitoring using low-cost mm-wave radar,” IEEE Access, vol. 10, pp. 18 998–19 012, 2021.

[24] H. Abedi, C. Magnier, and G. Shaker, “Passenger monitoring using ai-powered radar,” in 2021 IEEE 19th International Symposium on Antenna Technology and Applied Electromagnetics (ANTEM). IEEE, 2021, pp. 1–2.

[25] Y. Ma, Y. Zeng, and V. Jain, “CarOSense: Car occupancy sensing with the ultra-wideband keyless infrastructure,” Proceedings of the ACM on Interactive, Mobile, Wearable and Ubiquitous Technologies, vol. 4, no. 3, pp. 1–28, 2020.

[26] InnoSenT-Innovative Radar Sensor Technology. (2024, Oct.) Incabin monitoring: Anonymous vehicle interior monitoring with radar technology. [Online]. Available: https://www.innosent.de/en/ automotive/incabin-radar-monitoring/

[27] Infineon Technologies AG. Presence detection and sensing - infineon technologies. [Online]. Available: https://www.infineon.com/cms/en/applications/solutions/ sensor-solutions/presence-detection/

[28] NOVELIC. (2024, Oct.) Acam - in-cabin monitoring radar - novelic. [Online]. Available: https://www.novelic.com/ acam-automotive-in-cabin-monitoring-radar/

[29] IEE Smart Sensing Solutions. (2024, Oct.) Child presence detection for buses - iee smart sensing solutions. [Online]. Available: https://iee-sensing.com/automotive/safety-and-comfort/ lidas/

[30] Texas Instruments Incorporated. (2022, May) Vehicle occupant detection reference design. [Online]. Available: https://www.ti. com/lit/ug/tidue95a/tidue95a.pdf

[31] Aarti Dhapte. (2024, Dec.) Automotive wi-fi router market - forecast to 2032. [Online]. Available: https: //www.marketresearchfuture.com/reports/24379

[32] D. Shi, J. Lu, J. Wang, L. Li, K. Liu, and M. Pan, “No one left behind: Avoid hot car deaths via wifi detection,” in ICC 2020- 2020 IEEE International Conference on Communications (ICC). IEEE, 2020, pp. 1–6.

[33] X. Zeng, B. Wang, C. Wu, S. D. Regani, and K. R. Liu, “Intelligent Wi-Fi based child presence detection system,” in ICASSP 2022- 2022 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP). IEEE, 2022, pp. 11–15.

[34] Zeng, Xiaolu and Wang, Beibei and Wu, Chenshu and Regani, Sai Deepika and Liu, KJ Ray, “WiCPD: Wireless child presence detection system for smart cars,” IEEE Internet Things J., vol. 9, no. 24, pp. 24 866–24 881, 2022.

[35] S. S. Jayaweera, B. Wang, and K. R. Liu, “Robust in-car child presence detection using commercial wifi,” in Proceedings of the 30th Annual International Conference on Mobile Computing and Networking, 2024, pp. 1799–1801.

[36] UniMax Electronics Inc. (2024, May) Wi-fi child presence detection. [Online]. Available: https://www.unimax.com.tw/en/ product detail/76

[37] W. Li, M. J. Bocus, C. Tang, S. Vishwakarma, R. J. Piechocki, K. Woodbridge, and K. Chetty, “A taxonomy of WiFi sensing: CSI vs passive WiFi radar,” in 2020 IEEE Globecom Workshops (GC Wkshps). IEEE, 2020, pp. 1–6.

[38] C. Tang, W. Li, S. Vishwakarma, K. Chetty, S. Julier, and K. Woodbridge, “Occupancy detection and people counting using wifi passive radar,” in 2020 IEEE Radar Conference (RadarConf20). IEEE, 2020, pp. 1–6.

[39] W. Li, R. J. Piechocki, K. Woodbridge, C. Tang, and K. Chetty, “Passive wifi radar for human sensing using a stand-alone access point,” IEEE Transactions on Geoscience and Remote Sensing, vol. 59, no. 3, pp. 1986–1998, 2020.

[40] Q. Chen, K. Chetty, K. Woodbridge, and B. Tan, “Signs of life detection using wireless passive radar,” in 2016 IEEE Radar Conference (RadarConf). IEEE, 2016, pp. 1–5.

[41] N. Lyons, A. Santra, V. K. Ramanna, K. Uln, R. Taori, and A. Pandey, “Wifiact: Enhancing human sensing through environment robust preprocessing and bayesian self-supervised learning,” in ICASSP 2024-2024 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP). IEEE, 2024, pp. 13 391–13 395.

[42] X. Zeng, F. Wang, B. Wang, C. Wu, K. R. Liu, and O. C. Au, “Invehicle sensing for smart cars,” IEEE Open Journal of Vehicular Technology, vol. 3, pp. 221–242, 2022.

[43] 2024 Euro NCAP. (2023, Dec.) Test and assessment protocol – child presence detection. [Online]. Available: https://www.euroncap.com/media/79888/ euro-ncap-cpd-test-and-assessment-protocol-v12.pdf

[44] S. Sen, B. Radunovic, R. R. Choudhury, and T. Minka, “You are facing the Mona Lisa: Spot localization using PHY layer information,” in Proceedings of the 10th international conference on Mobile systems, applications, and services, 2012, pp. 183–196.

[45] H. Zhu, Y. Zhuo, Q. Liu, and S. Chang, “π-splicer: Perceiving accurate CSI phases with commodity WiFi devices,” IEEE Transactions on Mobile Computing, vol. 17, no. 9, pp. 2155–2165, 2018.

[46] Z. Zhou, Z. Yang, C. Wu, L. Shangguan, H. Cai, Y. Liu, and L. M. Ni, “WiFi-based indoor line-of-sight identification,” IEEE Transactions on Wireless Communications, vol. 14, no. 11, pp. 6125–6136, 2015.

[47] M. Kotaru, K. Joshi, D. Bharadia, and S. Katti, “Spotfi: Decimeter level localization using wifi,” in Proceedings of the 2015 ACM conference on special interest group on data communication, 2015, pp. 269–282.

[48] T.-D. Chiueh, P.-Y. Tsai, and I.-W. Lai, Baseband receiver design for wireless MIMO-OFDM communications. John Wiley & Sons, 2012.

[49] D. K. Barton, Radar equations for modern radar. Artech House, 2013.

[50] C. Lowanichkiattikul, M. Dhanachai, C. Sitathanee, S. Khachonkham, and P. Khaothong, “Impact of chest wall motion caused by respiration in adjuvant radiotherapy for postoperative breast cancer patients,” SpringerPlus, vol. 5, pp. 1–8, 2016.

[51] J. Liu, Y. Wang, Y. Chen, J. Yang, X. Chen, and J. Cheng, “Tracking vital signs during sleep leveraging off-the-shelf wifi,” in Proceedings of the 16th ACM international symposium on mobile ad hoc networking and computing, 2015, pp. 267–276.

[52] X. Liu, J. Cao, S. Tang, J. Wen, and P. Guo, “Contactless respiration monitoring via off-the-shelf WiFi devices,” IEEE Transactions on Mobile Computing, vol. 15, no. 10, pp. 2466– 2479, 2015.

[53] F. Zhang, C. Wu, B. Wang, M. Wu, D. Bugos, H. Zhang, and K. R. Liu, “SMARS: Sleep monitoring via ambient radio signals,” IEEE Transactions on Mobile Computing, vol. 20, no. 1, pp. 217–231, 2019.

[54] A. Dahal, S. Biswas, S. Z. Gurbuz, and A. C. Gurbuz, “Robustness analysis of wi-fi-based human activity recognition,” in Big Data VI: Learning, Analytics, and Applications, vol. 13036. SPIE, 2024, pp. 102–109.

[55] A. Dahal, S. Biswas, S. Z. Gurbuz, and A. C. Gurbuz, “Comparison between wi-fi-csi and radar-based har,” in 2024 IEEE Radar Conference (RadarConf24). IEEE, 2024, pp. 1–6.

[56] F. Zhang, C. Wu, B. Wang, H.-Q. Lai, Y. Han, and K. R. Liu, “WiDetect: Robust motion detection with a statistical electromagnetic model,” Proceedings of the ACM on Interactive, Mobile, Wearable and Ubiquitous Technologies, vol. 3, no. 3, pp. 1–24, 2019.

[57] L. Chen, I. Ahriz, and D. Le Ruyet, “AoA-aware probabilistic indoor location fingerprinting using channel state information,” IEEE Internet Things J., vol. 7, no. 11, pp. 10 868–10 883, 2020.

[58] Y. Li, D. Wu, J. Zhang, X. Xu, Y. Xie, T. Gu, and D. Zhang, “DiverSense: Maximizing Wi-Fi sensing range leveraging signal diversity,” Proceedings of the ACM on Interactive, Mobile, Wearable and Ubiquitous Technologies, vol. 6, no. 2, pp. 1–28, 2022.

[59] F. Xiaozhi, “An inspecting technology of weak sinusoidal signal in powerful noise based on multi-layer autocorrelation,” in 2013 International Conference on Mechanical and Automation Engineering. IEEE, 2013, pp. 11–13.

[60] Y. Hou, S. Li, H. Ma, S. Gong, and T. Yu, “Weak signal detection based on lifting wavelet threshold denoising and multilayer autocorrelation method.” J. Commun., vol. 17, no. 11, pp. 890–899, 2022.


---

# 2507.15245_SPAR_Scholar_Paper_Retrieval_with_LLM-based_Agents

[2507.15245](https://arxiv.org/abs/2507.15245)

# SPAR: Scholar Paper Retrieval with LLM-based Agents for Enhanced Academic Search

Xiaofeng Shi<sup>1</sup>\*<sup>†</sup> Yuduo Li<sup>1,2</sup>\*<sup>‡</sup> Qian Kou<sup>1</sup>\* Longbin Yu<sup>1</sup> Jinxin Xie<sup>1</sup> Hua Zhou<sup>1§</sup> <sup>1</sup>Beijing Academy of Artificial Intelligence (BAAI) <sup>2</sup>Beijing Jiaotong University (BJTU)

## Abstract

Recent advances in large language models (LLMs) have opened new opportunities for academic literature retrieval. However, existing systems often rely on rigid pipelines and exhibit limited reasoning capabilities. We introduce SPAR, a multi-agent framework that incorporates RefChain-based query decomposition and query evolution to enable more flexible and effective search. To facilitate systematic evaluation, we also construct SPAR-Bench, a challenging benchmark with expertannotated relevance labels. Experimental results demonstrate that SPAR substantially outperforms strong baselines, achieving up to +56% F1 on AutoScholar and +23% F1 on SPARBench over the best-performing baseline. Together, SPAR and SPARBench provide a scalable, interpretable, and high-performing foundation for advancing research in scholarly retrieval. Code and data will be available at: https://github.com/xiaofengShi/SPAR

## 1 Introduction

Effective academic paper retrieval is fundamental to research. As scientific literature continues to grow exponentially, researchers are increasingly challenged by the need to locate not just superficially relevant papers, but comprehensive and interconnected works that span multiple subtopics, time periods, and academic communities (Gusenbauer and Haddaway, 2020). While traditional academic search engines such as Google Scholar (Vine, 2006) support basic keyword queries well, they often fall short in supporting complex, multi-intent queries that require deeper contextual understanding or reference-based exploration.

Consider the query: “Show some cutting-edge technological advancements on how to improve the generalization ability of machine learning models across multiple domains.” This query implicitly demands up-to-date results, an understanding of “generalization” in a machine learning context, and coverage across multiple subfields. Existing systems tend to either return overly generic results or fail to capture the full semantic scope of such queries, leading to time-consuming manual filtering by the user.

Recent advances in large language models (LLMs) (Achiam et al., 2023; Team et al., 2023; Liu et al., 2024; Yang et al., 2025b) have enabled promising developments in information retrieval, including query rewriting, document retrieval, and ranking (Zhu et al., 2023). In the academic domain, these capabilities offer potential to support more intelligent, context-aware search experiences. However, academic research involves more than retrieving documents matching a user query: researchers often explore citation networks, follow references recursively, and synthesize insights across multiple papers. These behaviors, central to scholarly discovery, remain underexplored in current LLMbased retrieval systems.

To address this gap, we focus on modeling academic search as a recursive, citation-driven process we term the Reference Chain (RefChain). As illustrated in Figure 1, RefChain simulates how researchers follow references from one paper to another, expanding the scope of retrieval beyond direct query matches. PaSa (He et al., 2025) represents a key step in this direction, leveraging reinforcement learning (RL) to train an LLM-based agent to control RefChain expansion. However, PaSa is limited by its heavy reliance on training resources, its single-source retrieval design, and its coarse query understanding, which restrict its generalization across domains.

We propose SPAR (Scholar PAper Retrieval), a modular and extensible framework for academic retrieval built upon a multi-agent architecture. SPAR enhances RefChain-based exploration with five specialized components: (1) a Query Understanding Agent that interprets domain-specific intent and refines queries accordingly; (2) a Retrieval Agent that interfaces with multiple academic data sources; (3) a Query Evolver Agent that performs iterative, citation-aware query reformulation; (4) a Judgement Agent that evaluates and filters relevant papers; and (5) a Reranker Agent that reorders retrieved results based on authority, recency, and publication quality to improve ranking effectiveness. Together, these agents support a comprehensive and dynamic academic search workflow that mirrors how human researchers conduct in-depth literature exploration (Figure 2).

To systematically evaluate academic retrieval systems under realistic conditions, we also introduce SPARBench, a new benchmark comprising diverse, expert-annotated queries spanning computer science and biomedicine. Unlike existing datasets with narrow scopes, SPARBench captures the multi-faceted nature of real-world academic search. Each query and its associated relevant documents were carefully reviewed and annotated by domain experts with strong academic backgrounds, ensuring high-quality and reliable ground-truth relevance labels. This rigorous construction process makes SPARBench a robust testbed for developing and evaluating retrieval methods intended for practical academic use.

Empirical results on both AutoScholar (He et al., 2025) and SPARBench demonstrate that SPAR significantly outperforms all compared methods. On AutoScholar, SPAR achieves an F1 score of 0.3843, surpassing the previous best method, PaSa (0.2449), by 56.92%. Notably, SPAR maintains a strong balance between recall (0.4105) and precision (0.3612), while other methods often favor one at the expense of the other. On SPAR-Bench, SPAR is the only method that consistently achieves meaningful scores across all metrics, with an F1 of 0.3015, recall of 0.3103, and precision of 0.2932, outperforming all baselines by a clear margin. These results highlight SPAR’s robustness and generalization ability across both synthetic and real-world academic search scenarios.

These findings underscore the importance of structured, agent-based retrieval frameworks for addressing the complexities of modern academic search. Our primary contributions are summarized as follows:

![](images/4d11dcb43aa33a0f62eff20828482c78da80adb16c60e8b7e28da3ab7bba2028.jpg)  
Figure 1: The architecture of RefChain.

• We propose SPAR, a training-free, modular, and extensible academic retrieval framework that leverages a multi-agent architecture to perform fine-grained query understanding, multisource retrieval, RefChain-based exploration, and relevance-aware reranking.

• We introduce SPARBench, a high-quality, multi-domain academic retrieval benchmark featuring realistic queries and expertannotated relevance labels across computer science and biomedicine. SPARBench enables rigorous and reproducible evaluation under practical academic search conditions.

• We conduct extensive experiments on both AutoScholar and SPARBench, demonstrating that SPAR consistently outperforms a range of strong baselines, including manual search engines (e.g., Google Scholar, Semantic Scholar), LLM-assisted retrieval pipelines, and prior agent-based methods such as PaSa and PaperFinder.

## 2 Related Work

Traditional Academic Search Engines Conventional academic search systems such as Google Scholar (Vine, 2006), Semantic Scholar(Kinney et al., 2023), OpenAlex (Priem et al., 2022), and PubMed (Canese and Weis, 2013) provide effective keyword-based retrieval for well-formed queries. However, these systems rely primarily on lexical matching and are limited in their ability to handle complex, multi-intent queries (Gusenbauer and Haddaway, 2020). They also lack support for citation-aware exploration or semantic reasoning, which are often essential for comprehensive literature review tasks.

![](images/5d9f285c27fd21720446aa3d6d582b85e6a14a10dcf46dacd062ea4d54b915c3.jpg)  
Figure 2: The overview of SPAR.

LLM-Enhanced Retrieval Recent advances in large language models have led to increasing interest in using LLMs to improve academic retrieval performance (Zhu et al., 2023; Ma et al., 2023). Techniques such as query rewriting, semantic expansion, and LLM-based document reranking have shown promise in improving precision and recall. However, most existing approaches operate in a single-turn setting and do not support iterative, reference-driven exploration. Moreover, they rarely integrate domain-aware query understanding or multi-source retrieval strategies.

Agent-Based Academic Search Existing agentbased frameworks such as PaSa (He et al., 2025) make notable progress in automated scholarly search but remain limited by their reliance on supervised training and low modularity. To address these issues, we introduce SPAR, a training-free, modular agent framework designed for fine-grained query understanding and multi-source document exploration.

## 3 Methodology

We introduce SPAR (Scholar PAper Retrieval), an agent-based framework for academic literature search. Given a user query, SPAR first analyzes the input to identify search intent and perform query refinement (§ 3.1). It then conducts iterative retrieval via multi-source search, reference chain expansion, and query evolution (§ 3.2). Finally, it re-ranks the retrieved documents based on timeliness and authority (§ 3.3). An overview of the framework is shown in Figure 2, with each component detailed in the following subsections.

## 3.1 Query Interpretation and Refinement

The initial query presented by a user often represents an incomplete articulation of a complex, underlying information need, reflecting what (Belkin, 1980) termed an "Anomalous state of knowledge." Users, shaped by their unique perspectives, prior knowledge, or specific roles, naturally approach the same topic with varying informational goals and lines of inquiry (Teevan et al., 2005). Therefore, effective information retrieval requires a proactive strategy to discern latent user intent and to refine the initial query into more precise and targeted instructions (Carpineto and Romano, 2012; Croft et al., 2010). Recent studies have further emphasized the importance of query refinement in uncovering user intent, and the advent of LLMs has enabled more nuanced and context-aware query refinement techniques (Anand et al., 2023; Ma et al., 2023; Ye et al., 2023; Liu and Mozafari, 2024).

SPAR incorporates a Query Understanding agent to interpret the user’s search query and perform query refinement for subsequent precise academic paper retrieval. Given an academic search query q, the agent first performs intent classification, distinguishing whether the user seeks a survey, recent advances, or methodological comparisons. It simultaneously conducts domain identification to anchor the query in a specific field of study (e.g., machine learning) and detects any temporal constraints expressed in the query (e.g., "since 2020"). These annotations help the system tailor downstream retrieval operations to the user’s true research goal. Next, the agent selects one or more appropriate academic sources from a fixed set: S ={Google, ArXiv, OpenAlex, Semantic Scholar, PubMed}. The selection is conditioned on both the query domain and intent, ensuring source-query alignment.

The agent then determines whether the query requires multi-query refinement based on its specificity, domain clarity, and linguistic precision. If the query is broad, lacks technical terms, or includes ambiguous phrasing, the agent applies semantic disambiguation, correction, and intentaware expansion. Refinement is guided by the query’s recognized intent and detailed refinement prompt is provided in Appendix A.1:

• For survey-focused queries, the agent generates refined queries targeting different perspectives, including methods, applications, historical developments, and future challenges.

• For complex or specialized domains, the agent generates refined queries using domainspecific terms and technical specifications while also targeting empirical studies and primary research.

• When temporal constraints are present, all refinements incorporate the specified date bounds to ensure time-sensitive relevance.

Query Understanding Agent emphasizes coverage of diverse subfields and research methodologies from the initial query. The result of this stage is a structured list of semantically enriched and disambiguated queries $\mathcal { Q } = \{ q _ { 1 } , q _ { 2 } , \cdots , q _ { N } \}$ , each of which will be utilized to retrieve papers. This proactive query refinement lays the foundation for precise and context-aware academic paper search in SPAR.

## 3.2 RefChain-based Iterative Retrieval and Query Evolution

After the Query Understanding Agent refines the query and identifies relevant sources, SPAR enters an iterative retrieval phase, coordinated by the Retrieval Agent, the Judgement Agent, and the Query Evolver Agent. The Retrieval Agent initiates this process by fetching academic papers using sourcespecific strategies and de-duplicating results. It also expands coverage through RefChain exploration, uncovering related work beyond the initial query matches.

The Retrieval Agent executes source-adaptive querying for each $q _ { i } \in \mathcal { Q }$ . For sources such as Semantic Scholar or OpenAlex, it extracts keywords from each query; for Google, it submits the full query string. It then consolidates results across sources by merging retrieved papers, each annotated with metadata such as title, abstract, authorship, publication date, and source.

The Judgement Agent evaluates the relevance of each retrieved paper by comparing it to the initial query and accompanying metadata. Papers scoring above the relevance threshold are added to the Related Pool $R = \{ r _ { 1 } , r _ { 2 } , \cdot \cdot \cdot , r _ { m } \}$ . Prompts for judging relevance are provided in Appendix A.3.

Subsequently, SPAR enhances knowledge expansion through RefChain. For each paper $r _ { i } \in R ,$ , the Retrieval Agent extracts its list of references either by parsing PDFs or utilizing structured metadata from sources. Then these referred papers are scored using the same Judgement Agent. High-relevance papers are merged with the Related Pool. The K most relevant papers from the expanded pool are selected as final results for the current query list and stored in Paper Cache $\mathcal { P } = \{ p _ { 1 } , p _ { 2 } , \cdot \cdot \cdot , p _ { K } \}$ A key design decision is to limit expansion to a single RefChain layer. That is, while exploring the references of papers in the Related Pool, it does not recursively expand those references’ citations. This constraint is grounded in two considerations:

• Precision and relevance: Deeper RefChain often leads to tangential topics, reducing precision;

• Computational efficiency: Each layer significantly increases the retrieval and evaluation cost.

Compared to PaSa, which uses RL training to determine expansion depth, SPAR’s deterministic, fixeddepth strategy ensures reliability, while iterative query evolution compensates by exploring new directions in a controlled manner.

To ensure depth and diversity in search results, the Query Evolver Agent then generates three new queries for $p _ { i } \in \mathcal { P }$ , focusing on its methodological insights, applications, and limitations. These queries are conditioned on the retrieval history trajectory, including the initial query, previous search queries, and the metadata of the corresponding paper. A random subset of the resulting queries is selected and added to the query list Q for further retrieval iterations. Prompt for evolving query is provided in Appendix A.2.

This retrieval-expansion loop continues until the Paper Cache reaches a predefined size or maximum depth. To avoid redundancy, SPAR filters out previously used queries and suppresses keyword overlaps across iterations, ensuring efficient and progressive exploration of the literature space.

## 3.3 Reranker

After retrieving and scoring candidate papers, a Re-ranking Module refines the final paper list. The reranking stage subsequently refines this candidate list by reordering the documents so that the most appropriate and informative items appear at the top. Besides the original relevance score, our reranker integrates two additional signals:

• Publication authority, estimated from metadata such as venue prestige and author reputation;

• Temporal relevance, determined by whether a document satisfies explicit time constraints in the query or belongs to the most recent publications.

The prompt template that combines these factors is provided in Appendix A.4. The final output is an ordered list of highly relevant, timely, and authoritative academic papers tailored to the user’s intent.

## 4 SPARBench

Despite growing interest in scholarly information retrieval, the field still lacks robust and standardized benchmarks for systematic and realistic evaluation. This absence limits reproducibility and hinders progress in developing generalizable academic search systems.

Existing resources remain limited in both scope and quality. For example, AutoScholar (He et al., 2025) is a synthetic dataset constructed from AI conference papers between 2023 and 2024. Although it pairs GPT-4o-generated queries with relevant documents, only 100 query-document pairs were manually reviewed, raising concerns about label quality and applicability to real-world scenarios. Another benchmark, RealScholarQuery (He et al., 2025), contains 50 expert-written queries collected post-hoc from AI researchers, introducing potential evaluation bias toward models tuned for that specific setup.

Most prior benchmarks focus on closed corpora (Ajith et al., 2024; Voorhees et al., 2021; Cohan et al., 2004), using static queries and documents. Such settings fail to capture key aspects of academic search, including query understanding, multi-source retrieval, and reference-based exploration. Despite efforts toward more comprehensive evaluation, no existing benchmark supports end-toend assessment encompassing ranking, reasoning, source selection, and iterative exploration.

To address these limitations, we introduce SPARBench, a benchmark for evaluating academic retrieval systems under realistic conditions. Unlike previous efforts, SPARBench draws from multiple academic sources—including arXiv, PubMed, OpenAlex, and Semantic Scholar—covering diverse disciplines such as computer science and biomedicine.

SPARBench reflects natural academic search behavior. Initial queries are generated by GPT-4o and then rigorously filtered by domain experts. The dataset includes multi-intent queries with incomplete grammar and minor spelling errors to simulate real-world user input. Relevance judgments follow a multi-stage process combining automatic filtering, small and large language models, and manual validation by experts, ensuring high label quality and domain fidelity.

Given the high cost of producing high-quality academic retrieval data, the current version includes 50 carefully curated queries, each undergoing expert review. This initial release prioritizes depth and reliability, providing a solid foundation for future extensions to broader domains and larger query sets. SPARBench will be publicly released to support further research in academic search.

## 4.1 Benchmark Characteristics

• Realistic Queries: Simulate authentic academic search behavior through multi-intent, semantically rich queries with incomplete grammar and minor spelling errors.

• Cross-Domain Coverage: Supports evaluation across computer science and biomedicine, enabling assessment of domain-general and domain-specific retrieval capabilities.

• Multi-Source Corpus: Integrates documents from arXiv, PubMed, OpenAlex, and Semantic Scholar to reduce source-specific bias and improve retrieval realism.

![](images/72de114794ad795ad02a7e0224ccd6fcc0507829c5f2cbaf7be741128f21e582.jpg)  
Figure 3: SPARBench construction pipeline. The process includes expert-curated seed queries, GPT-4o-based query expansion, multi-source document retrieval, and a three-stage relevance filtering procedure combining language models and expert annotation.

• High-Quality Annotations: A multi-stage labeling pipeline combines LLM-based filtering with expert validation, ensuring high-quality annotations and domain consistency.

## 4.2 Construction Method

Figure 3 outlines the multi-stage pipeline used to construct SPARBench. A set of seed queries was manually curated based on real academic research scenarios. These were expanded using GPT-4o (Hurst et al., 2024) to introduce linguistic and semantic diversity. After expert screening, 50 queries were selected—35 from computer science and 15 from biomedicine.

Each query was submitted independently to arXiv, PubMed, OpenAlex, and Semantic Scholar, producing an initial candidate set of 198K documents. Relevance assessment proceeded in three stages:

1. Initial Pruning: Coarse relevance was estimated using Qwen2.5-7B-Instruct (Yang et al., 2024), reducing the set to 3K candidates.

2. Refinement: Qwen2.5-72B-Instruct (Yang et al., 2024) performed fine-grained filtering, yielding 2K documents.

3. Expert Validation: Graduate-level computer science annotators manually reviewed the remaining candidates, selecting approximately 560 relevant documents (averaging 12 per query).

The final benchmark comprises 50 queries and 560 expert-verified relevant documents. Stage-wise statistics are reported in Appendix E (Figure 5).

SPARBench fills a critical gap in academic retrieval research by offering a realistic, high-quality benchmark tailored for end-to-end evaluation of scholarly search systems.

## 5 Experiments

## 5.1 Evaluation Setup

We evaluated our method against a diverse set of baselines, including traditional academic and web search engines, as well as LLM-enhanced retrieval systems. The evaluated baselines include:

• GOOGLE (G): Standard Google search using the original query.

• GOOGLE+GPT-4O (G+GPT):Query rewritten for clarity using GPT-4o (Hurst et al., 2024) before Google search.

• GOOGLE SCHOLAR (GS):Direct retrieval from Google Scholar without LLM intervention.

• CHATGPT SEARCH (CS):We Submit query to ChatGPT, which is powered by searchenabled GPT-4o.

• GOOGLE-ARXIV (GA):Google search restricted to arXiv.org.

• GOOGLE-ARXIV + LLM (GA+LLM): Query refined using LLM before Google search restricted by arXiv.

• OPENALEX+LLM (OA+LLM):Keywords extracted by LLM for the retrieval of the OpenAlex API.

• SEMANTIC SCHOLAR+LLM(2S+LLM):LLMextracted keywords used for the Semantic Scholar search.

• PUBMED+LLM(PM+LLM):LLMgenerated keywords for PubMed searches.

• PASA:An LLM-driven academic search agent optimized through reinforcement learning (He et al., 2025).

• PAPERFINDER:An LLM-powered academic search assistant accessed at <https://paperfinder.allen.ai/chat>(accessed July 9, 2025). It mimics human-like iterative literature search by decomposing queries, tracking citations, and providing relevance explanations. (Allen Institute for AI, 2025)

For all "+LLM" variants, we use Qwen3- 32B (Yang et al., 2025a) for keyword extraction, relevance estimation or query refinement. For "+GPT" variants, GPT-4o is employed to rewrite the query for improved clarity before web search. Task-specific prompting strategies are detailed in Appendix A.1.

We evaluate retrieval performance using three standard metrics: Precision, Recall, and F1, computed at the document level for each query. Importantly, each retrieval system operates over its own native search source (e.g., OpenAlex, Semantic Scholar, Google Scholar), rather than performing search on a shared benchmark corpus. This setup reflects realistic usage scenarios and allows for endto-end evaluation of each system’s full retrieval pipeline, including query understanding, source selection, search execution, and result ranking. Our goal is to assess the overall effectiveness of each system as a holistic academic search solution.

Let T P be the number of true positives (relevant documents correctly retrieved), F P the number of false positives (irrelevant documents retrieved), and F N the number of false negatives (relevant documents not retrieved). The metrics are defined as follows:

$$
\text { Precision } = \frac {T P}{T P + F P}\tag{1}
$$

$$
\text { Recall } = \frac {T P}{T P + F N}\tag{2}
$$

$$
\mathrm{F} 1 = \frac {2 \cdot \text { Precision } \cdot \text { Recall }}{\text { Precision } + \text { Recall }}\tag{3}
$$

Precision measures the proportion of retrieved documents that are truly relevant, reflecting retrieval accuracy. Recall measures the proportion of relevant documents that are successfully retrieved, reflecting coverage. F1 is the harmonic mean of Precision and Recall, providing a balanced assessment of both accuracy and completeness.

We report results on two benchmarks:

• AutoScholar: A synthetic benchmark introduced in the PaSa paper, designed to evaluate retrieval precision on fine-grained AI domain queries.

• SPARBench: Our curated benchmark featuring real-world queries from computer science and biomedicine, with expert-validated relevance annotations.

## 5.2 Main Result

As shown in Table 1, our proposed method SPAR consistently outperforms all baselines across both benchmarks. On the AUTOSCHOLAR dataset, SPAR achieves the highest F1 score of 0.3843 and the highest precision of 0.3612, while maintaining a competitive recall (0.4105). This demonstrates its strong ability to retrieve relevant documents with high accuracy and balance. On SPARBENCH, SPAR also surpasses all other methods, achieving the best F1 score of 0.3015, recall of 0.3103, and precision of 0.2932. In contrast, prior methods such as GA+LLM, PASA, and PAPERFINDER exhibit either lower precision or significant performance imbalance (e.g., high recall but very low precision). Notably, while PAPERFINDER obtains the highest recall (0.8333) on AutoScholar, its precision (0.0261) is extremely low, leading to a much lower F1 score. These results highlight SPAR’s superior capability in balancing precision and recall, thereby providing robust and effective academic document retrieval across diverse settings.

<table><tr><td rowspan="2">Method</td><td colspan="3">AutoScholar</td><td colspan="3">SPARBench</td></tr><tr><td>F1</td><td>Recall</td><td>Precision</td><td>F1</td><td>Recall</td><td>Precision</td></tr><tr><td>G</td><td>-</td><td>0.2015</td><td>-</td><td>-</td><td>0.000</td><td>-</td></tr><tr><td>G+GPT</td><td>-</td><td>0.2683</td><td>-</td><td>0.0092</td><td>0.0082</td><td>0.0106</td></tr><tr><td>GS</td><td>-</td><td>0.1130</td><td>-</td><td>0.0043</td><td>0.0038</td><td>0.0050</td></tr><tr><td>CS</td><td>0.0869</td><td>0.3046</td><td>0.0507</td><td>0.0045</td><td>0.0038</td><td>0.0055</td></tr><tr><td>GA</td><td>0.0400</td><td>0.1571</td><td>0.0229</td><td>0.2451</td><td>0.2800</td><td>0.2180</td></tr><tr><td>GA+LLM</td><td>0.0556</td><td>0.1692</td><td>0.0333</td><td>0.1923</td><td>0.1613</td><td>0.2382</td></tr><tr><td>PM+LLM</td><td>-</td><td>0.000</td><td>-</td><td>-</td><td>0.000</td><td>-</td></tr><tr><td>OA+LLM</td><td>0.0045</td><td>0.1083</td><td>0.0023</td><td>0.0242</td><td>0.0988</td><td>0.0138</td></tr><tr><td>2S+LLM</td><td>0.0044</td><td>0.0833</td><td>0.0023</td><td>0.0135</td><td>0.0449</td><td>0.0080</td></tr><tr><td>PaSa</td><td>0.2449</td><td>0.7931</td><td>0.1448</td><td>0.1041</td><td>0.1009</td><td>0.1076</td></tr><tr><td>PaperFinder</td><td>0.0506</td><td>0.8333</td><td>0.0261</td><td>0.0418</td><td>0.1474</td><td>0.0244</td></tr><tr><td>SPAR (ours)</td><td>0.3843</td><td>0.4105</td><td>0.3612</td><td>0.3015</td><td>0.3103</td><td>0.2932</td></tr></table>

Table 1: Comparison of retrieval performance across different methods on the AutoScholar and SPARBench benchmarks. “–” indicates metrics unavailable due to missing valid document.

<table><tr><td>Benchmark</td><td>QInterp</td><td>F1</td><td>Recall</td><td>Precision</td></tr><tr><td rowspan="2">AutoScholar</td><td>w</td><td>0.19</td><td>0.24</td><td>0.16</td></tr><tr><td>w/o</td><td>0.18</td><td>0.25</td><td>0.14</td></tr><tr><td rowspan="2">SPARBench</td><td>w</td><td>0.22</td><td>0.16</td><td>0.34</td></tr><tr><td>w/o</td><td>0.21</td><td>0.21</td><td>0.21</td></tr></table>

Table 2: Effect of query interpretation (QInterp) on retrieval performance across benchmarks.

## 6 Analysis and Discussion

## 6.1 Effects on Query Interpretation

Query Interpretation (QInterp) enhances retrieval by analyzing the query intent, selecting appropriate sources, and performing intent-aware rewriting. As described in Appendix D, this module introduces structural awareness that enables better alignment between queries and target documents.

Table 2 reports retrieval results with and without QInterp across two benchmarks. On both datasets, enabling QInterp improves overall F1 and precision. In SPARBench, precision increases substantially from 0.21 to 0.34, reflecting improved ranking relevance in a complex, multi-source environment. However, recall tends to decrease (e.g., 0.25 to 0.24 in AutoScholar, 0.21 to 0.16 in SPARBench), likely due to more restrictive interpretations that favor precision over coverage. This trade-off is consistent with observations in baseline systems employing aggressive query rewriting (Table 1).

These results suggest that query interpretation is beneficial for precision-oriented retrieval, especially in settings requiring fine-grained query understanding and source selection. Future work may explore hybrid strategies that balance interpretation with recall-aware expansion.

## 6.2 Impact of RefChain

The RefChain mechanism significantly improves document recall by expanding the set of candidates through citation-based traversal. As shown in Table 5 (Appendix C.3), RefChain enhances recall-oriented metrics on both the AutoScholar and SPARBench benchmarks.

In AutoScholar, RefChain increases the recall after similarity filtering from 0.41 to 0.44 and raw recall from 0.58 to 0.77, while the average retrieved documents rise from 306.9 to 569.1. Similarly, on SPARBench, recall improves from 0.13 to 0.15, the raw recall from 0.26 to 0.31, and the retrieval volume from 367.8 to 504.9. However, this recall improvement reduces precision due to increased noise. In AutoScholar, precision drops from 0.29 to 0.19, and in SPARBench from 0.22 to 0.16.

These results indicate that RefChain is most beneficial in recall-critical scenarios, such as retrievalaugmented generation (RAG) for academic synthesis. In contrast, precision-focused retrieval systems may prefer to disable RefChain to minimize noise and reduce downstream filtering overhead.

## 6.3 Benefits of Query Evolution

Query Evolution refines search queries by leveraging retrieval history and high-relevance documents, enhancing search focus via semantic guidance from top-ranked results (see case study in Appendix C.2).

Table 3 reports its impact on F1, recall, and precision across two academic search benchmarks: AutoScholar and SPARBench.

Query Evolution consistently improves F1 in both benchmarks. Precision increases by 0.02 in each dataset, indicating more targeted retrieval. Although recall slightly decreases in AutoScholar, the overall shift toward higher precision demonstrates the effectiveness of focused querying. Prompts used for query evolution are provided in Appendix A.2.

<table><tr><td>Benchmark</td><td>Evolution</td><td>F1</td><td>Recall</td><td>Precision</td></tr><tr><td rowspan="2">AutoScholar</td><td>w</td><td>0.34</td><td>0.41</td><td>0.29</td></tr><tr><td>w/o</td><td>0.33</td><td>0.43</td><td>0.27</td></tr><tr><td rowspan="2">SPARBench</td><td>w</td><td>0.26</td><td>0.24</td><td>0.27</td></tr><tr><td>w/o</td><td>0.24</td><td>0.24</td><td>0.25</td></tr></table>

Table 3: Impact of query evolution on retrieval performance. Evolution denotes application of Query Evolu tion.

## 6.4 Reranking Strategy and Its Advantages

The reranking module reorders the top-10 retrieved documents to optimize Recall@5. Table 4 reports its effects on two benchmarks. On AutoScholar, Recall@5 increases from 0.3146 to 0.4015, representing a 27.6% relative improvement. On SPAR-Bench, Recall@5 improves from 0.1588 to 0.1662, a 4.7% relative gain.

These results demonstrate the module’s effectiveness in prioritizing authoritative and contextually relevant documents, thereby enhancing retrieval quality and user experience. The larger improvement observed on AutoScholar suggests that reranking is particularly beneficial for datasets characterized by simpler query structures.

<table><tr><td>Benchmark</td><td>Reranking</td><td>Recall@5</td></tr><tr><td rowspan="2">AutoScholar</td><td>w/o</td><td>0.3146</td></tr><tr><td>w</td><td>0.4015</td></tr><tr><td rowspan="2">SPARBench</td><td>w/o</td><td>0.1588</td></tr><tr><td>w</td><td>0.1662</td></tr></table>

Table 4: Effect of reranking on Recall@5 for the top 5 retrieved documents across benchmarks.

## 6.5 Relevance Assessment: Model and Prompt Selection

We examine how model and prompt choices affect relevance assessment performance. Larger models do not consistently outperform smaller ones. A systematic evaluation reveals the most effective configuration.

We compare two prompt styles—brief and complex—across seven language models on the AutoScholar and SPARBench benchmarks (Appendix A.3; Table 6). On AutoScholar, Qwen3-

32B with the brief prompt achieves the highest F1 score (0.38). On SPARBench, LLaMA3.3- 70B (Grattafiori et al., 2024) with the same prompt performs best (F1: 0.30). Based on overall performance across both datasets, we select Qwen3-32B (brief) as the default configuration.

Additional generalization experiments (Appendix C.4.2) confirm the robustness of this choice, underscoring the importance of prompt design and model selection in relevance assessment.

## 7 Conclusion

We present SPAR, a modular multi-agent framework for academic paper retrieval, designed to tackle the challenges of underspecified queries, fragmented sources, and evolving information needs. SPAR consists of four key stages: (1) a Query Understanding agent that interprets user intent through intent classification, domain detection, and temporal constraint parsing, followed by intent-aware query refinement; (2) an Iterative Retrieval phase that integrates source-adaptive querying and RefChain-based citation expansion for recall-oriented exploration; (3) a Query Evolver agent that diversifies search trajectories by generating follow-up queries based on previously retrieved papers; and (4) a Reranker that ranks results using relevance, timeliness, and publication authority.

To evaluate SPAR, we construct SPARBench, a benchmark of semantically complex academic queries with expert-labeled relevance. Experiments on SPARBench and AutoScholar demonstrate that SPAR consistently outperforms strong baselines. It achieves an F1 score of 0.3843 on AutoScholar, a +56% improvement over PaSa, and 0.3015 on SPARBench, the only method delivering balanced performance across all metrics.

Our results validate the synergy of symbolic planning (RefChain), LLM-powered query evolution, and agent-based modular design in addressing the complexity of scholarly retrieval tasks. SPAR and SPARBench offer a reproducible and extensible foundation for advancing intelligent academic search systems.

## Limitations

Despite the strong performance of SPAR, several limitations remain.

First, SPAR limits citation-based expansion (RefChain) to a single traversal depth. While this design reduces latency and suppresses noise, it may miss deeply nested but highly relevant works, especially in long citation chains that characterize foundational research.

Second, RefChain substantially improves recall but introduces noisy candidates, leading to lower precision. This trade-off, while acceptable for recall-oriented tasks, may be suboptimal in scenarios that demand high-precision retrieval, such as targeted literature reviews.

Third, SPAR currently relies on static prompting and rule-based orchestration. The lack of feedbackdriven learning or user interaction modeling hinders personalization and adaptation over time. Incorporating reinforcement signals or retrievalbased supervision could make the system more robust in dynamic search environments.

Finally, although SPARBench provides a valuable testbed for semantically complex academic queries, it remains limited in scale and domain diversity. Future work should extend SPARBench to cover additional disciplines and query types, enabling broader generalization and facilitating standardized evaluation for next-generation academic search systems.

## References

Josh Achiam, Steven Adler, Sandhini Agarwal, Lama Ahmad, Ilge Akkaya, Florencia Leoni Aleman, Diogo Almeida, Janko Altenschmidt, Sam Altman, Shyamal Anadkat, and 1 others. 2023. Gpt-4 technical report. arXiv preprint arXiv:2303.08774.

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal, Danqi Chen, and Tianyu Gao. 2024. Litsearch: A retrieval benchmark for scientific literature search. arXiv preprint arXiv:2407.18940.

Allen Institute for AI. 2025. Ai2 paper finder: LLMpowered academic search assistant. https:// paperfinder.allen.ai/chat. Accessed: 2025-07- 09.

Abhijit Anand, Vinay Setty, Avishek Anand, and 1 others. 2023. Context aware query rewriting for text rankers using llm. arXiv preprint arXiv:2308.16753.

Nicholas J Belkin. 1980. Anomalous states of knowl edge as a basis for information retrieval. Canadian journal of information science, 5(1):133–143.

Kathi Canese and Sarah Weis. 2013. Pubmed: the bibli ographic database. The NCBI handbook, 2(1):2013.

Claudio Carpineto and Giovanni Romano. 2012. A survey of automatic query expansion in information retrieval. Acm Computing Surveys (CSUR), 44(1):1– 50.

A Cohan, S Feldman, I Beltagy, D Downey, and DS Weld. 2004. Specter: document-level representation learning using citation-informed transformers. 2020. arXiv preprint arXiv:2004.07180.

W Bruce Croft, Donald Metzler, and Trevor Strohman. 2010. Search engines: Information retrieval in practice, volume 520. Addison-Wesley Reading.

Aaron Grattafiori, Abhimanyu Dubey, Abhinav Jauhri, Abhinav Pandey, Abhishek Kadian, Ahmad Al-Dahle, Aiesha Letman, Akhil Mathur, Alan Schelten, Alex Vaughan, and 1 others. 2024. The llama 3 herd of models. arXiv preprint arXiv:2407.21783.

Michael Gusenbauer and Neal R Haddaway. 2020. Which academic search systems are suitable for systematic reviews or meta-analyses? evaluating retrieval qualities of google scholar, pubmed, and 26 other resources. Research synthesis methods, 11(2):181–217.

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin, Yuchen Zhang, Hang Li, and 1 others. 2025. Pasa: An llm agent for comprehensive academic paper search. arXiv preprint arXiv:2501.10120.

Aaron Hurst, Adam Lerer, Adam P Goucher, Adam Perelman, Aditya Ramesh, Aidan Clark, AJ Ostrow, Akila Welihinda, Alan Hayes, Alec Radford, and 1 others. 2024. Gpt-4o system card. arXiv preprint arXiv:2410.21276.

Rodney Kinney, Chloe Anastasiades, Russell Authur, Iz Beltagy, Jonathan Bragg, Alexandra Buraczynski, Isabel Cachola, Stefan Candra, Yoganand Chandrasekhar, Arman Cohan, and 1 others. 2023. The semantic scholar open data platform. arXiv preprint arXiv:2301.10140.

Aixin Liu, Bei Feng, Bing Xue, Bingxuan Wang, Bochao Wu, Chengda Lu, Chenggang Zhao, Chengqi Deng, Chenyu Zhang, Chong Ruan, and 1 others. 2024. Deepseek-v3 technical report. arXiv preprint arXiv:2412.19437.

Jie Liu and Barzan Mozafari. 2024. Query rewriting via large language models. arXiv preprint arXiv:2403.09060.

Xinbei Ma, Yeyun Gong, Pengcheng He, Hai Zhao, and Nan Duan. 2023. Query rewriting in retrievalaugmented large language models. In Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing, pages 5303–5315.

Jason Priem, Heather Piwowar, and Richard Orr. 2022. Openalex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. arXiv preprint arXiv:2205.01833.

Gemini Team, Rohan Anil, Sebastian Borgeaud, Jean-Baptiste Alayrac, Jiahui Yu, Radu Soricut, Johan Schalkwyk, Andrew M Dai, Anja Hauth, Katie Millican, and 1 others. 2023. Gemini: a family of highly capable multimodal models. arXiv preprint arXiv:2312.11805.

Jaime Teevan, Susan T Dumais, and Eric Horvitz. 2005. Personalizing search via automated analysis of interests and activities. In Proceedings of the 28th annual international ACM SIGIR conference on Research and development in information retrieval, pages 449– 456.

Rita Vine. 2006. Google scholar. Journal of the Medical Library Association, 94(1):97.

Ellen Voorhees, Tasmeer Alam, Steven Bedrick, Dina Demner-Fushman, William R Hersh, Kyle Lo, Kirk Roberts, Ian Soboroff, and Lucy Lu Wang. 2021. Trec-covid: constructing a pandemic information retrieval test collection. In ACM SIGIR Forum, volume 54, pages 1–12. ACM New York, NY, USA.

An Yang, Anfeng Li, Baosong Yang, Beichen Zhang, Binyuan Hui, Bo Zheng, Bowen Yu, Chang Gao, Chengen Huang, Chenxu Lv, Chujie Zheng, Dayiheng Liu, Fan Zhou, Fei Huang, Feng Hu, Hao Ge, Haoran Wei, Huan Lin, Jialong Tang, and 41 others. 2025a. Qwen3 technical report. arXiv preprint arXiv:2505.09388.

An Yang, Anfeng Li, Baosong Yang, Beichen Zhang, Binyuan Hui, Bo Zheng, Bowen Yu, Chang Gao, Chengen Huang, Chenxu Lv, and 1 others. 2025b. Qwen3 technical report. arXiv preprint arXiv:2505.09388.

An Yang, Baosong Yang, Beichen Zhang, Binyuan Hui, Bo Zheng, Bowen Yu, Chengyuan Li, Dayiheng Liu, Fei Huang, Haoran Wei, Huan Lin, Jian Yang, Jian hong Tu, Jianwei Zhang, Jianxin Yang, Jiaxi Yang, Jingren Zhou, Junyang Lin, Kai Dang, and 22 others. 2024. Qwen2.5 technical report. arXiv preprint arXiv:2412.15115.

Fanghua Ye, Meng Fang, Shenghui Li, and Emine Yilmaz. 2023. Enhancing conversational search: Large language model-aided informative query rewriting. arXiv preprint arXiv:2310.09716.

Yutao Zhu, Huaying Yuan, Shuting Wang, Jiongnan Liu, Wenhan Liu, Chenlong Deng, Haonan Chen, Zheng Liu, Zhicheng Dou, and Ji-Rong Wen. 2023. Large language models for information retrieval: A survey. arXiv preprint arXiv:2308.07107.

## A Prompt Template

## A.1 Prompt For Baseline

## Prompt for Query Refinement

Generate a search query suitable for Google based on the given academic paper-related query. Please adhere to the following instructions:

1. Understand the Query: Carefully read and comprehend the given academic query.

2. Identify Key Elements: Extract the main research domain, specific methods, or core concepts.

3. Formulate the Search Query: Construct a concise and effective query that captures these components and is suitable for academic search engines.

4. Avoid Site Constraints: Do not include any site-specific filters (e.g., site:xxx).

5. Output Format: Only generate the refined query using the format below.

[User’s Query]: {UserQuery}

[Generated Search Query]: <your query here>

## Prompt for keywords extraction

Extract optimal search keywords from the given research question, specifically optimized for the {source} academic database. Your task is to generate concise, commaseparated query terms that will maximize relevant paper retrieval on this platform.

Source-Specific Guidelines:

• Semantic Scholar:

– Focus on technical terminology and core concepts.

– Include methodological terms.

– Consider author-centric keywords if prominent researchers are known.

– Emphasize computer science and AI terminology where relevant.

## • OpenAlex:

– Prioritize broader academic terms.

– Include interdisciplinary connections.

– Balance specificity with coverage.

– Include field classifications where relevant.

## • PubMed:

– Emphasize medical/biological terminology.

– Include relevant MeSH (Medical Subject Headings) terms.

– Consider clinical and biomedical contexts.

– Include chemical/drug names or biological processes where relevant.

## Response Format:

[Start] keyword1, keyword2, keyword3, ... [End]

## Examples by Source:

• Semantic Scholar: [Start] transformer architecture, attention mechanism, language model fine-tuning [End]

• OpenAlex: [Start] neural networks, deep learning, artificial intelligence, pattern recognition [End]

• PubMed: [Start] CRISPR-Cas9, gene editing, genetic therapy, chromosomal modification [End]

Now, extract optimized search keywords for {source} from this question:{user\_query}

## A.2 Prompt For Query Evolution

You are an academic search expert helping explore a research topic more thoroughly.

\### CONTEXT:

\- Original Query: {user\_query}

Previously Searched Queries:

## {searched\_queries}

\- Relevant Document Title: {doc\_title}

\- Document Abstract: {doc\_abstract}

\- Document Field: {doc\_field}

## ### TASK:

Generate {N} NEW search queries that explore different aspects of this research area:

1. A query exploring METHODOLOGI-

CAL alternatives or comparisons

2. A query focusing on APPLICATIONS or implementations

3. A query addressing LIMITATIONS, challenges, or critiques

## Each query should be:

\- Clearly different from previously searched queries

\- Based on insights from the document

\- Relevant to the original research question

\- Specific enough to retrieve focused results

## ### IMPORTANT NOTE:

If document information is missing or insufficient (e.g., empty abstract), generate queries based primarily on the original query and your knowledge of the research domain. Focus on exploring complementary aspects of the topic rather than requiring specific document details.

## ### OUTPUT FORMAT:

Return a JSON array of strings containing

only the expanded queries:

[Query 1,Query 2, Query 3]

## A.3 Prompt for Relevance

## prompt for Relevance – Brief

You are an expert in academic research. Given a query and a document in the context of a scholarly paper search, evaluate their relevance on a scale from 0 to 1, where 0 means completely irrelevant and 1 means highly relevant. Base your evaluation on the query’s intent, key concepts, and the document’s content. Provide a score and explain your reasoning consistently.

## Query: {UserQuery}

Document:

Title: {title}

Abstract: {abstract}

Score: [Your score between 0 and 1]

Reasoning: [Your explanation]

## prompt for Relevance – Complex

You are a rigorous and highly discerning academic search relevance evaluator. Your task is to critically assess the relationship between the user’s query and the provided scholarly article. Apply a strict, highstandard academic lens to evaluate conceptual alignment, topical focus, and methodological relevance. Be skeptical of superficial keyword matches or loosely related themes. Only assign a high relevance score (on a 0–1 scale) when there is clear and substantial alignment in research purpose, methods, and contribution. Err on the side of conservatism in scoring—precision and selectivity are paramount.

## Input Format

Query: Raw academic search query Article:

• Title: Academic article title

• Abstract: Abstract text summarizing the paper’s content

## Hierarchical Evaluation Protocol

1. Critical Relevance Check (Binary Gate)

If the document contains zero of the following, automatically score 0.0:

• Core subject keywords from query

• Matching research domain

• Thematic alignment with query intent

## 2. Detailed Scoring Criteria (Only if passes Critical Check)

A. Core Topic Alignment (0–0.6)

• 0.5–0.6: Directly addresses primary subject with matching terminology

• 0.3–0.4: Related subfield but different focus area

• 0.1–0.2: Only tangential connection through peripheral terms

• 0.0: Fails Critical Relevance Check

## B. Contextual Precision (0–0.3)

• 0.2–0.3: Explicitly addresses query’s specific technical aspects

• 0.1: General thematic similarity without concrete details

• 0.0: No meaningful connection to query intent

## C. Depth Validation (0–0.1)

• 0.1: Provides experimental validation/novel theoretical framework

• 0.05: Mentions concept without substantive analysis

• 0.0: Superficial treatment of subject

## Scoring Matrix (Sum Components A + B

\+ C)

• 0.00–0.19: Completely irrelevant / offtopic

• 0.20–0.39: Minimal relevance — shares domain but different focus

• 0.40–0.59: Partial relevance — addresses some aspects

• 0.60–0.79: Substantial relevance — covers key elements

• 0.80–1.00: Optimal match — comprehensive coverage

## Anti-Gaming Rules

• Penalize -0.3 for keyword stuffing without contextual relevance

• Penalize -0.2 for misleading titles/abstracts

• If score < 0.4, round down to nearest 0.1

• If score ≥ 0.7, require positive marks in all 3 criteria

## Examples

Example 1 (Low Score) Query: “Machine learning for early Alzheimer’s diagnosis using MRI” Article: “Statistical analysis of MRI machine calibration errors” Reasoning: Fails Critical Relevance — no ML or Alzheimer’s content Score: 0.15

Example 2 (High Score) Query: “Federated learning optimization in IoT networks” Article: “Adaptive Gradient Compression for Energy-Efficient Federated Learning in Edge Computing Environments” Reasoning: Directly addresses FL optimization (0.6) + technical specifics (0.25) + experimental validation (0.1) Score: 0.86

Input Data

Query: {query}

Article: {doc}

## Output Format

Reasoning: [Concise technical justification]

Score: [0.00–1.00]

## A.4 Prompt For Reranking

## Reranking with Time Requirement

Please rerank the following {N} academic papers in response to the query:{Query}

Consider these factors in your reranking:

## 1. Authority:

• Publication venue prestige (top conferences/journals rank higher)

• Author prominence (authors with higher h-index or citation counts rank higher)

## 2. Timeliness:

• The query specifically asks for recent/current papers, so strongly prefer newer papers

3. Maintain reasonable relevance to the original query

## For each paper, provide:

1. A new numerical rank (1 being the highest)

2. A brief justification (1-2 sentences)

3. A new relevance score between 0-1 that incorporates both relevance and the factors above

List of papers with original relevance scores (title, year, venue, authors, relevance):

## {Doc List Here}

## Please provide your reranking with new scores and concise justifications in the following format for each document:

Document [index]: [score] - [justification]

## For example:

Document 1: 9.5 - Highly relevant as it directly addresses the query topic with empirical evidence.

Document 2: 7.0 - Somewhat relevant but focuses on a tangential aspect of the query.

## Reranking without Time Requirement

Please rerank the following {N} academic papers in response to the query: {Query}

Consider these factors in your reranking:

## 1. Authority:

• Publication venue prestige (top conferences/journals rank higher)

• Author prominence (authors with higher h-index or citation counts rank higher)

## 2. Timeliness:

• Generally prefer more recent papers, but don’t overly penalize influential older papers

3. Maintain reasonable relevance to the original query

## For each paper, provide:

1. A new numerical rank (1 being the highest)

2. A brief justification (1-2 sentences)

3. A new relevance score between 0-1 that incorporates both relevance and the factors above

List of papers with original relevance scores (title, year, venue, authors, relevance):

## {Doc List Here}

Please provide your reranking with new scores and concise justifications in the following format for each document: Document [index]: [score] - [justification]

## For example:

Document 1: 9.5 - Highly relevant as it directly addresses the query topic with empirical evidence.

Document 2: 7.0 - Somewhat relevant but focuses on a tangential aspect of the query.

## B BenchMark Information

## B.1 SPARBench Example

## An Example of SPARBench

Question: "What are the potentials and ethical challenges of gene editing technologies (e.g., CRISPR) in treating genetic diseases? Provide specific explanations and recent research progress."

Source Metadata:

• Search Time: 2025-04-10

• Reference Answers:

1. – Paper ID: http://genome.cshlp.

org/content/24/9/1526.full. pdf

– Title: "Seamless gene correction of β-thalassemia mutations in patientspecific iPSCs using CRISPR/Cas9 and piggyBac"

– Abstract: β-thalassemia, one of the most common genetic diseases worldwide, is caused by mutations in human hemoglobin beta (HBB) gene. Creation of induced pluripotent stem cells (iPSCs) from β- thalassemia patients could offer an approach to cure this disease. Correction of disease-causing mutations in iPSCs can restore normal function and provide a rich source for transplantation. In this study, we used the latest gene-editing tool, CRISPR/- Cas9 technology, combined with piggyBac transposon to efficiently correct patient-derived mutations without leaving any residual footprint. No off-target effects were detected in corrected iPSCs, which retain full pluripotency and normal karyotypes. When differentiated into erythroblasts using monolayer culture, gene-corrected cells restored HBB expression compared to the parental line. Our study provides an effective footprint-free correction method, thereby demonstrating a critical step toward future application of cell-based gene therapy for monogenic diseases.

– Authors: Fei Xie, Lin Ye, Judy C. Chang, Ashley I. Beyer, Jiaming Wang, Marcus O. Muench, Yuet Wai Kan

– Year: 2014

– Citation Count: 381

– Source: OpenAlex

– Similarity Scores:

Small Model: 0.7

LLM: 0.85

2. – Paper ID: https://www. nature.com/articles/ s41392-019-0089-y.pdf

– Title: "Applications of genome editing technology in the targeted therapy of human diseases: mechanisms, advances and prospects",

– Abstract: "..."

## C Strategy Result

## C.1 Query Interpretation Result

## Example of Query Interpretation

User Query: What improvements are needed in vaccine development efficiency to respond to emerging infectious diseases? Provide a multi-angle analysis.

Query Intent: Literature review and multiangle analysis

Domain: Biomedical sciences / Vaccine development

Suitable Sources: pubmed, openalex

Needs Expansion: true

Expansion Reason: The query is somewhat broad and could be improved by incorporating specific technical terms or focusing on particular aspects of vaccine development. Terms like ’vaccine development efficiency’ are relatively general and may yield a wide range of results, some of which might not be directly relevant to responding to emerging infectious diseases. The query could benefit from specifying methodologies (e.g., computational modeling, platform technologies, mRNA-based approaches), clarifying the scope (e.g., preclinical vs clinical stages), and defining the type of research sought (e.g., reviews, metaanalyses, case studies). Including terms such as ’platform vaccines’, ’reverse vaccinology’, or ’rapid antigen identification’ would enhance precision and relevance within the domain of biomedical sciences.

Expanded Queries: • Systematic

review of vaccine development methods for emerging infectious diseases

• Literature review of vaccine application strategies in global health emergencies (2021-2025)

• Historical survey of vaccine innovation in response to pandemics since 2000

• Comparative analysis of future challenges in accelerating vaccine development post-pandemic

• Survey of multi-disciplinary approaches to improve vaccine design efficiency

## Time Requirement Description: NO

Source Reason: PubMed is the most suitable source for this query due to its focus on biomedical and life sciences research, which directly aligns with vaccine development. OpenAlex can also be useful as it provides interdisciplinary context and broader metadata, supporting a multi-angle analysis without time constraints.

## C.2 Query Evolution vs Native Method

This example illustrates query-document semantic relationships via color coding. Tokens highlighted in the same color indicate shared or closely related concepts between queries and document content.

## Query Evolution vs Native method

Original Query: "Can you identify any papers that analysed the use of target networks with linear function approximation, needed in theoretical properties of target networks?"

Previously Searched Queries:

• Survey of target networks with linear function approximation methods

• Systematic review of historical development of target networks with linear function approximation

• Literature review of target networks applications using linear function approximation

• Can you identify any papers that analysed the use of target networks with linear function approximation, needed in theoretical properties of target networks?

• State-of-the-art in theoretical properties of target networks using linear function approximation (2024-2025)

• Comparative analysis of future challenges in target networks with linear function approximation

Relevant Document Title: "A Unifying View of Linear Function Approximation in Off-Policy RL Through Matrix Splitting and Preconditioning"

Document Abstract: "Traditionally, TD and FQI are viewed as differing in the num ber of updates toward the target value function: TD makes one update, FQI makes an infinite number, and Partial Fitted Q-Iteration (PFQI) performs a finite number, such as the use of a target network in Deep Q-Networks (DQN) in the off-policy setting. This perspective, however, fails to capture the convergence connections between these algorithms and may lead to incorrect conclusions, for example, that the convergence of TD implies the convergence of FQI. In this paper, we focus on linear value function approximation and offer a new perspective, unifying TD, FQI, and PFQI as the same iterative method for solving the Least Squares Temporal Difference (LSTD) system, but using different preconditioners and matrix splitting schemes. TD uses a constant preconditioner, FQI employs a data-feature adaptive preconditioner, and PFQI transitions between the two. Then, we reveal that in the context of linear function approximation. increasing the number of updates under the same target value function essentially represents a transition from using a constant preconditioner to datafeature adaptive preconditioner. This unifying perspective also simplifies the analyses of the convergence conditions for these algorithms and clarifies many issues. Consequently, we fully characterize the convergence of each algorithm without assuming specific properties of the chosen features (e.g., linear independence). We also examine how common assumptions about feature representations affect convergence, and discover new conditions on features that are important for convergence. These convergence conditions allow us to establish the convergence connections between these algorithms and to address important questions."

## - Document Field: "cs.LG"

## QueryEvolution:

• Practical implementation of Partial Fitted Q-Iteration with linear function approximation in off-policy reinforcement learning settings

• Challenges and convergence limitations of using fixed versus adaptive preconditioners in target network-based reinforcement learning algorithms

## NativeMethod:

• Real-world implementations and case studies of target networks using linear function approximation

• Critique of convergence and stability issues in target networks employing linear function approximation

## C.3 RefChain Effect Details

As shown in Table 5, using RefChain can improve the final Recall by 7.32% and 15.38% on AutoScholar and SPARBench.

## C.4 Performance of Varies Relevance Assesment

## C.4.1 Performance on Benchmarks

Table 6 shows the comparison of different models for relevance judgment. Qwen3-32B with brief instruction achieves the best F1 score of 0.38.

## C.4.2 Performance on OpenSource Dataset

Table 7 shows the comparison of different models for relevance judgment on three open-source benchmarks. Qwen3-32B with brief instruction achieves the best average performance among all benchmarks.

## D Query Interpretation Overview

## E SPARBench Stage Volume Change

<table><tr><td>Benchmark</td><td>RefChain</td><td>Recall</td><td>Precision</td><td>Raw Doc Num</td><td>Valid Doc Num</td><td>Recall (Raw)</td></tr><tr><td rowspan="2">AutoScholar</td><td>w/o</td><td>0.41</td><td>0.29</td><td>306.90</td><td>3.95</td><td>0.58</td></tr><tr><td>w</td><td>0.44</td><td>0.19</td><td>569.08</td><td>6.58</td><td>0.77</td></tr><tr><td rowspan="2">SPARBench</td><td>w/o</td><td>0.13</td><td>0.22</td><td>367.81</td><td>10.77</td><td>0.26</td></tr><tr><td>w</td><td>0.15</td><td>0.16</td><td>504.94</td><td>15.00</td><td>0.31</td></tr></table>

Table 5: Impact of RefChain on document retrieval metrics across two benchmarks. Enabling RefChain improves recall but introduces more noise, leading to a drop in precision. Recall and Precision are computed based on documents retained after relevance filtering. Raw Doc Num refers to the total number of documents retrieved before filtering; Valid Doc Num indicates the number of relevant documents identified after filtering; Recall (Raw) is recall calculated over the full set of raw retrieved documents.

<table><tr><td rowspan="2">Model and Inst Variant</td><td colspan="3">AutoScholar</td><td colspan="3">SPARBench</td></tr><tr><td>F1</td><td>Recall</td><td>Precision</td><td>F1</td><td>Recall</td><td>Precision</td></tr><tr><td>PaSa Selector</td><td>0.34</td><td>0.41</td><td>0.29</td><td>0.26</td><td>0.24</td><td>0.27</td></tr><tr><td>Llama3.1-8B (brief)</td><td>0.11</td><td>0.19</td><td>0.08</td><td>0.20</td><td>0.18</td><td>0.23</td></tr><tr><td>Llama3.1-8B (complex)</td><td>0.13</td><td>0.48</td><td>0.07</td><td>0.23</td><td>0.24</td><td>0.22</td></tr><tr><td>Llama3.3-70B (brief)</td><td>0.20</td><td>0.38</td><td>0.13</td><td>0.30</td><td>0.31</td><td>0.29</td></tr><tr><td>Llama3.3-70B (complex)</td><td>0.18</td><td>0.34</td><td>0.12</td><td>0.17</td><td>0.34</td><td>0.12</td></tr><tr><td>Qwen2.5-7B (brief)</td><td>0.34</td><td>0.47</td><td>0.27</td><td>0.28</td><td>0.28</td><td>0.28</td></tr><tr><td>Qwen2.5-7B (complex)</td><td>0.08</td><td>0.09</td><td>0.06</td><td>0.24</td><td>0.27</td><td>0.21</td></tr><tr><td>Qwen2.5-72B (brief)</td><td>0.33</td><td>0.51</td><td>0.24</td><td>0.24</td><td>0.38</td><td>0.17</td></tr><tr><td>Qwen2.5-72B (complex)</td><td>0.17</td><td>0.44</td><td>0.11</td><td>0.19</td><td>0.27</td><td>0.15</td></tr><tr><td>Qwen3-8B (brief)</td><td>0.29</td><td>0.53</td><td>0.20</td><td>0.25</td><td>0.30</td><td>0.22</td></tr><tr><td>Qwen3-8B (complex)</td><td>0.31</td><td>0.45</td><td>0.24</td><td>0.23</td><td>0.31</td><td>0.19</td></tr><tr><td>Qwen3-14B (brief)</td><td>0.21</td><td>0.37</td><td>0.14</td><td>0.25</td><td>0.32</td><td>0.20</td></tr><tr><td>Qwen3-14B (complex)</td><td>0.22</td><td>0.38</td><td>0.15</td><td>0.23</td><td>0.34</td><td>0.17</td></tr><tr><td>Qwen3-32B (brief)</td><td>0.38</td><td>0.41</td><td>0.36</td><td>0.24</td><td>0.29</td><td>0.21</td></tr><tr><td>Qwen3-32B (complex)</td><td>0.08</td><td>0.29</td><td>0.05</td><td>0.18</td><td>0.30</td><td>0.12</td></tr></table>

Table 6: Performance Comparison of Different Models on AutoScholar and SPARBench Datasets(where ’brief refers to inst-brief and ’complex’ to inst-complex). Prompt details can be found in Appendix A.3.

<table><tr><td>Model and Inst Variant</td><td>TREC-Covid</td><td>Scidocs</td><td>LitSearch</td></tr><tr><td>PaSa Selector</td><td>0.7010</td><td>0.1291</td><td>0.4980</td></tr><tr><td>LLaMA3.1-8B (brief)</td><td>0.6967</td><td>0.7453</td><td>0.5695</td></tr><tr><td>LLaMA3.1-8B (complex)</td><td>0.6537</td><td>0.5251</td><td>0.5080</td></tr><tr><td>LLaMA3.3-70B (brief)</td><td>0.7047</td><td>0.7366</td><td>0.5737</td></tr><tr><td>LLaMA3.3-70B (complex)</td><td>0.6942</td><td>0.3278</td><td>0.5108</td></tr><tr><td>Qwen2.5-7B (brief)</td><td>0.6930</td><td>0.3022</td><td>0.4808</td></tr><tr><td>Qwen2.5-7B (complex)</td><td>0.6693</td><td>0.0751</td><td>0.3571</td></tr><tr><td>Qwen2.5-72B (brief)</td><td>0.7163</td><td>0.7715</td><td>0.5830</td></tr><tr><td>Qwen2.5-72B (complex)</td><td>0.6921</td><td>0.1668</td><td>0.4374</td></tr><tr><td>Qwen3-8B (brief)</td><td>0.7143</td><td>0.3553</td><td>0.5224</td></tr><tr><td>Qwen3-8B (complex)</td><td>0.6569</td><td>0.1203</td><td>0.4335</td></tr><tr><td>Qwen3-14B (brief)</td><td>0.7170</td><td>0.4756</td><td>0.5338</td></tr><tr><td>Qwen3-14B (complex)</td><td>0.6853</td><td>0.1238</td><td>0.4481</td></tr><tr><td>Qwen3-32B (brief)</td><td>0.7256</td><td>0.6082</td><td>0.5566</td></tr><tr><td>Qwen3-32B (complex)</td><td>0.6729</td><td>0.1651</td><td>0.4550</td></tr></table>

Table 7: F1 scores of various models on TREC-Covid (Voorhees et al., 2021), Scidocs (Cohan et al., 2004), and LitSearch-NLP-Class (Ajith et al., 2024) datasets.

![](images/abf81b7134e83fd94f2cb492b7682fd20ca4505490fb5f88ce5514da5a00f7c4.jpg)  
Figure 4: The Overview of Query Interpretation Module

![](images/cc749e10489aacad7426172e66919b7e383489c60c47ed778a9b89c41fe25571.jpg)  
Figure 5: Document volume at each filtering stage of the benchmark construction pipeline, showing the reduction from raw retrieval results to the final final set.


---

# 2605.14306_PaSaMaster_Self-Evolving_Agentic_Literature_Retrieval (trunc)

[2605.14306](https://arxiv.org/abs/2605.14306)

# Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du $^{1,2*†}$ , Tian Jin $^{1,2†}$ , Jing Kang $^{1,2}$ , Xianghe Pang $^{1,2}$ , Jingyi Chai $^{1,2}$ , Tingjia Miao $^{1,2}$ , Fenyi Liu $^{1,2}$ , WenHao Wang $^{3}$ , Sikai Yao $^{2}$ , Yuzhi Zhang $^{2}$ , Siheng Chen $^{1,2*}$

$^{1}$ Shanghai Jiao Tong University, Shanghai, China. $^{2}$ SciLand, Shanghai, China. $^{3}$ Zhejiang University, Hangzhou, China.

\*Corresponding author(s). E-mail(s): sjtu0267098@sjtu.edu.cn; sihengc@sjtu.edu.cn; †These authors contributed equally to this work.

## Abstract

Scientific literature retrieval must understand complex search intents while preserving source authenticity. Traditional keyword and embedding-based systems return authentic sources but miss nuanced intents, whereas large language models capture richer intents but may fabricate citations. We introduce PaSaMaster, a Recursive Self-Evolving agentic literature retrieval system that iteratively analyzes intent, retrieves verified papers and ranks them with evidence-grounded relevance scores. PaSaMaster combines self-evolving retrieval that refines search intent from ranked evidence over time, hallucination-free ranking over verified papers rather than generated citations, and cost-efficient planning–retrieval separation that reserves frontier LLMs for intent understanding while delegating retrieval and scoring to lightweight models and customized corpora. Across 38 disciplines in PaSaMaster-Bench, PaSaMaster achieves a 16.5× higher F1-score than Google Scholar and a 37.8% higher F1-score than GPT-5.2 at about 1% of the cost, while reducing source hallucination from 32.66% in generative LLMs to zero: https://github.com/sjtu-sai-agents/PaSaMaster

Keywords: Scientific Literature Discovery, Agentic AI, Large Language Models

![](images/b3d40710676739648d7d5154aec61a1e34ff00ac635fbd5560421f95feab0b92.jpg)  
Fig. 1 Overview of PaSaMaster and PaSaMaster-Bench. a, PaSaMaster converts a complex natural-language search intent into a verified, evidence-ranked paper list through three layers: a Navigator that refines intent and search strategy, a Librarian Swarm that retrieves, verifies and scores candidate papers, and verified corpora and tools that ground all outputs in real sources. b, PaSaMaster-Bench evaluates complex literature retrieval through expert-written search intents, multi-channel candidate retrieval and checklist-based expert annotation. The benchmark contains 244 tasks across 38 disciplines, enabling evaluation of intent understanding, source reliability and ranking quality.

Table 1 The Five Paradigms of Scientific Literature Discovery. Existing paradigms each improve one aspect of literature retrieval, but fail to jointly achieve adaptive intent understanding, hallucination-free evidence grounding, and cost-efficient scaling. PaSaMaster resolves these limitations through agentic Recursive Self-Evolving, evidence-grounded retrieval.

<table><tr><td>Paradigm Level</td><td>Representative Systems</td><td>Intent Adaptivity</td><td>Source Reliability</td><td>Cost Efficiency</td></tr><tr><td>Level 0: Lexical Retrieval</td><td>Google Scholar [1], PubMed [2]</td><td>Keyword-based; severe intent compression</td><td>Verified indexed papers</td><td>Efficient but semantically shallow</td></tr><tr><td>Level 1: Semantic Retrieval</td><td>OpenScholar [3], Bohrium Navigator [4]</td><td>Passive embedding matching; limited intent compression</td><td>Verified indexed papers</td><td>Efficient but semantically shallow</td></tr><tr><td>Level 2: Generative LLMs</td><td>GPT-5.2 [5], Gemini 3.1 Pro [6], DeepSeek [7]</td><td>Strong natural-language understanding</td><td>Prone to hallucinated papers</td><td>Expensive to deploy at scale</td></tr><tr><td>Level 3: Fixed-Pipeline Agentic Retrieval</td><td>Google Scholar Labs [8], PaSa [9]</td><td>User intent fixed at the outset; no cognition update during retrieval</td><td>Verified indexed papers</td><td>Cost-controlled, but constrained by fixed intent interpretation</td></tr><tr><td>Level 4: Recursive Self-Evolving Agentic Retrieval</td><td>PaSaMaster (Ours)</td><td>Iteratively refines intent using ranked evidence</td><td>Verified indexed papers</td><td>Cost-efficient planning-retrieval separation</td></tr></table>

Scientific literature retrieval is the axiomatic starting point of all scientific inquiry $[10]$ . Before formulating hypotheses, designing experiments, or building new theories, researchers must fundamentally navigate the vast and ever-expanding corpus of existing knowledge $[11]$ . However, the volume of scientific publications has grown exponentially over recent decades, decisively overwhelming the fixed cognitive bandwidth of individual researchers $[12–14]$ . This severe information overload has driven an inevitable reliance on artificial intelligence to automate and accelerate knowledge discovery $[15]$ . More importantly, modern literature search is rarely a simple keyword lookup $[16, 17]$ . Researchers often express complex academic intents involving technical constraints, application contexts, and implicit background knowledge $[10, 18, 19]$ . As large language models reshape scientific research workflows, literature retrieval therefore faces a new central challenge: how to deeply understand complex search intents while ensuring that every returned source is real and verifiable $[19, 20]$ .

Existing literature retrieval systems still struggle to jointly achieve complex intent understanding and source authenticity. Some methods preserve source authenticity at the cost of shallow intent understanding $[1, 3, 4]$ , whereas others improve semantic comprehension while sacrificing factual reliability $[5–7, 21–23]$ . This creates a persistent tradeoff between reliable but limited retrieval and more intelligent but less trustworthy literature discovery.

The tradeoff between intent understanding and source reliability is clearer when viewed through the evolution of literature retrieval paradigms (Table 1). Level 0 (Lexical Retrieval) [1, 2] guarantees source authenticity through indexed databases, but reduces complex research intents to rigid keywords, causing severe intent compression. Level 1 (Semantic Retrieval) [3, 4] improves over exact keyword matching by using embedding-based similarity and retrieval-augmented matching [24, 25], but still treats retrieval as passive query-document matching and lacks the ability to actively clarify, decompose, or refine complex intents. Level 2 (Generative LLMs) [5-7, 21-23] offers stronger intent comprehension, yet its probabilistic generation introduces fabricated papers [26, 27], undermining the factual trust required for scientific inquiry. Level 3 (Fixed-Pipeline Agentic Retrieval) [8, 9] mitigates source hallucination by grounding

LLM agents in verifiable retrieval tools $[28–33]$ . However, these systems typically follow a predefined retrieve-read-answer pipeline in which the interpretation of the user question is largely fixed at the beginning. For complex research intents, this initial interpretation can be incomplete or biased toward only part of the request, causing later retrieval steps to miss relevant subtopics or return papers that satisfy only some constraints. This limitation motivates retrieval systems that can update their understanding of the intent as evidence accumulates.

The unresolved need for adaptive, verifiable and efficient retrieval motivates Level 4 (Recursive Self-Evolving Agentic Retrieval), represented by PaSaMaster. PaSaMaster is a Recursive Self-Evolving agentic literature retrieval system that iteratively analyzes intent, retrieves verified papers and ranks them with evidence-grounded relevance scores. Rather than treating literature search as one-shot query-document matching problem, PaSaMaster formulates scientific literature discovery as a Recursive Self-Evolving intent-paper relevance ranking process. This design enables the system to align with complex research intents while ensuring that every returned source is real, verifiable, and grounded in customized corpora.

[... truncated ...]


---

# 2503.16734_多模态大模型时代的智能体推荐系统 (trunc)

[2503.16734](https://arxiv.org/abs/2503.16734)

# Towards Agentic Recommender Systems in the Era of Multimodal Large Language Models

Chengkai Huang<sup>1</sup>, Junda Wu<sup>2</sup>, Yu Xia<sup>2</sup>, Zixu Yu<sup>2</sup>, Ruhan Wang<sup>3</sup>, Tong Yu<sup>4</sup>, Ruiyi Zhang<sup>4</sup>, Ryan A. Rossi<sup>4</sup>, Branislav Kveton<sup>4</sup>, Dongruo Zhou<sup>3</sup>, Julian McAuley<sup>2</sup>, Lina Yao<sup>1,5</sup>

<sup>1</sup>University of New South Wales, <sup>2</sup>University of California San Diego, <sup>3</sup>Indiana University, <sup>4</sup>Adobe Research, <sup>5</sup>CSIRO’s Data61

{chengkai.huang1, lina.yao}@unsw.edu.au, {juw069, yux078, ziy040, jmcauley}@ucsd.edu, {ruhwang, dz13}@iu.edu, {tyu,

ruizhang, rrossi, kveton}@adobe.com

## Abstract

Recent breakthroughs in Large Language Models (LLMs) have led to the emergence of agentic AI systems that extend beyond the capabilities of standalone models. By empowering LLMs to perceive external environments, integrate multimodal information, and in teract with various tools, these agentic systems exhibit greater autonomy and adaptability across complex tasks. This evolution brings new opportunities to recommender systems (RS): LLM-based Agentic RS (LLM-ARS) can ofer more interactive, context-aware, and proactive recommendations, potentially reshaping the user experience and broadening the application scope of RS. Despite promising early results, fundamental challenges remain, including how to efectively incorp

[... truncated ...]


---

| Metric | Value |
|---|---|
| Papers | 19 |
| Actual | 200.8k |
| Target | 200.0k |

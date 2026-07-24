# 推荐系统前沿论文集 — 合并文档

> **生成策略**: 关键章节模式 — 仅保留 Introduction, Method, Experiments, Conclusion
> **目标大小**: 175.0k tokens
> **论文总数**: 25 篇
> **生成时间**: 2026-07-24T12:32:17.263686

---

## 目录

1. **WHEN IS A + xA = <sup>R</sup>** (2505.00556) — 1.6k tokens [key-sections]
2. **RADAR: Recall Augmentation through Deferred Asynchronous Retrieval** (2506.07261) — 1.7k tokens [key-sections]
3. **Stealthy LLM-Driven Data Poisoning Atacks Against Embedding-Based Retrieval-Augmented Recommender Systems** (2505.05196) — 1.9k tokens [key-sections]
4. **Adaptive Candidate Retrieval with Dynamic Knowledge Graph Construction for Cold-Start Recommendation** (2505.20773) — 2.0k tokens [key-sections]
5. **ItemRAG: Item-Based Retrieval-Augmented Generation for LLM-Based Recommendation** (2511.15141) — 2.0k tokens [key-sections]
6. **Efficient Cold-Start Recommendation via BPE Token-Level Embedding Initialization with LLM** (2509.13179) — 2.0k tokens [key-sections]
7. **Towards Eficient Certification of Maritime Remote Operation Centers – Ansatz zur efizienten Zertifizierung von maritimen Fernsteuerungszentren** (2508.00543) — 2.2k tokens [key-sections]
8. **Selective LLM-Guided Regularization for Enhancing Recommendation Models** (2512.21526) — 2.6k tokens [key-sections]
9. **Towards Agentic Recommender Systems in the Era of Multimodal Large Language Models** (2503.16734) — 2.6k tokens [key-sections]
10. **Meta-Modal Agent: Sequential Evidence Routing for Missing-Modality Candidate Reranking** (2605.25007) — 3.2k tokens [key-sections]
11. **Popcorn: A Configurable Benchmark for Visual Evidence in Multimodal Movie Recommendation** (2606.09595) — 3.4k tokens [key-sections]
12. **Cold-Start Recommendation towards the Era of Large Language Models (LLMs): A Comprehensive Survey and Roadmap** (2501.01945) — 3.6k tokens [key-sections]
13. **RapidPD: Rapid Human and Pet Presence Detection System for Smart Vehicles via Wi-Fi** (2504.00678) — 4.1k tokens [key-sections]
14. **Probability of Transition to Turbulence in a Reduced Stochastic Model of Pipe Flow** (2503.00987) — 5.1k tokens [key-sections]
15. **Massive Memorization with Hundreds of Trillions of Parameters for Sequential Transducer Generative Recommenders** (2510.22049) — 5.4k tokens [key-sections]
16. **MMSRARec: Summarization and Retrieval Augumented Sequential Recommendation Based on Multimodal Large Language Model** (2512.20916) — 5.4k tokens [key-sections]
17. **Seeing and Reflecting: Multimodal Memory-Enhanced Agent Collaboration for Recommendation** (2607.07108) — 5.4k tokens [key-sections]
18. **Diagnosing LLM-based Rerankers in Cold-Start Recommender Systems: Coverage, Exposure and Practical Mitigations** (2604.16318) — 5.6k tokens [key-sections]
19. **Eficient Retrieval Scaling with Hierarchical Indexing for Large Scale Recommendation** (2604.12965) — 6.7k tokens [key-sections]
20. **Breaking User-Centric Agency: A Tri-Party Framework for Agent-Based Recommendation** (2603.10673) — 7.9k tokens [key-sections]
21. **Ofline Reasoning for Eficient Recommendation: LLM-Empowered Persona-Profiled Item Indexing** (2602.21756) — 8.2k tokens [key-sections]
22. **VRAgent-R1: Boosting Video Recommendation with MLLM-based Agents via Reinforcement Learning** (2507.02626) — 8.3k tokens [key-sections]
23. **The Future is Agentic: Definitions, Perspectives, and Open Challenges of Multi-Agent Recommender Systems** (2507.02097) — 10.5k tokens [key-sections]
24. **A Comprehensive Review on Harnessing Large Language Models to Overcome Recommender System Challenges** (2507.21117) — 11.3k tokens [key-sections]
25. **EARN: Eficient Inference Acceleration for LLM-based Generative Recommendation by Register Tokens** (2507.00715) — 17.6k tokens [key-sections]

---



---

## 📑 关键章节 | WHEN IS A + xA = <sup>R</sup>

**arXiv ID**: [2505.00556](https://arxiv.org/abs/2505.00556)

## <sub>1.</sub> Introduction

In this paper we prove several results concerning the “sizes” of subgroups and subrings of the reals. Here by “size”, we typically refer to the Hausdorf measure and dimension of such objects. The story of “sizes” has a rich history, which begins with a classical result in real analysis.

Theorem 1.1 (Steinhaus [18]). Suppose $A \subseteq \mathbb { R } ^ { n }$ is Lebesgue measurable and has positive measure. Then the diference set $A - A : = \{ x - y : x , y \in A \}$ contains a ball with positive radius whose center is at the origin.

The next corollary follows immediately.

Corollary 1.2. If A is a measurable proper subgroup of (<sup>R</sup>, +), then A is null.<sup>1</sup>

Subsequently, Volkmann and Erd˝os initiated the study of the dimension of subgroups/rings of the reals in the 1960s. In [20] they showed that for each $\alpha \in [ 0 , 1 ]$ there is a Borel subgroup of (<sup>R</sup>, +) with Hausdorf dimension α. Edgar and Miller [3], and independently Bourgain [1] showed that an analytic (see the definition before Fact 2.5) subring of <sup>R</sup> either has Hausdorf dimension 0 or is all of <sup>R</sup>. Mauldin [14] showed that assuming CH (the continuum hypothesis), for each $\alpha , 0 \leqslant \alpha \leqslant 1$ there is a subfield of <sup>R</sup> with Hausdorf dimension α. Following the strategy of $^ { 6 6 } \mathrm { d i s } .$ cretization” used by Bourgain in [1], de Saxc´e [16] considered the problem in the setting of a connected simple real Lie group G endowed with a Riemannian metric and showed that there is no Borel measurable dense subgroup of G with Hausdorf dimension strictly between 0 and dim<sub>H</sub>(G). For a more detailed discussion on the early history, see [3] p.1122. The subgroups and subrings of the reals are also natural objects appearing in geometric measure theory, see [4, Section 12.4] for example.

In this paper we consider the following related question.

Definition 1.3. Given a subgroup A of $( \mathbb { R } , + )$ , define

$$
X _ {A} = \{x \in \mathbb {R}: A + x A = \mathbb {R} \}.
$$

Question 1. Suppose $A \subseteq ( \mathbb { R } , + , \cdot )$ is a subobject in some algebraic sense e.g. subgroup, subring or subfield. Is there an $x \in \mathbb { R }$ such that

$$
A + x A := \{a + x b: a, b \in A \} = \mathbb {R}?
$$

And if such an x exists, what do we know about the size of A? What do we know about $X _ { A } \mathcal { ? }$

We prove the following main results.

Theorem 1.4. There is an $F _ { \sigma }$ subgroup A $o f \left( \mathbb { R } , + \right)$ such that dim $\textstyle \operatorname { l } _ { \mathrm { H } } ( A ) \leq { \frac { 1 } { 2 } }$ and $X _ { A } \neq \varnothing$

Theorem 1.5. Assume CH, holds: $2 ^ { \aleph _ { 0 } } = \aleph _ { 1 }$ . There is a group A with $\dim _ { \mathrm { H } } ( A ) =$ 0 such that $X _ { A } = \mathbb { R } \backslash \mathbb { Q }$

Theorem 1.4 is proved via a concrete construction of A and $x \in X _ { A }$ . For Theorem 1.5, we construct A using the concept of genericity and algorithmic dimension. We believe this method may be used to construct other exotic subsets of reals.

We also consider what would happen if we restrict Question 1 to the analytic subgroups. By the Marstrand projection theorem, if A is an analytic subgroup of the reals and dim<sub>H</sub> $( A ) > \frac { 1 } { 2 }$ , then $X _ { A }$ is $\mathrm { c o - n u l l } ^ { 2 }$ (Proposition 3.4). Our main results improve this proposition in terms of dimension. The restriction on analytic sets also enables us to use descriptive set theory. For example, if A is an analytic subgroup of the reals and $x \in X _ { A }$ , then there is an $F _ { \sigma }$ subgroup $B \subseteq A$ such that $x \in X _ { B }$ (Theorem 3.8).

For subrings, the condition is diferent. If A is a subring of <sup>R</sup> and $X _ { A } \neq \varnothing$ , then $A = \mathbb { R }$ (Proposition 2.4).

Besides Question 1, we also study the maximal subfields of <sup>R</sup> without a given point because the proof techniques suggest so. Given a field K and $a \in K$ , a maximal subfield of K without a is a maximal (with respect to inclusion) element of $\{ L \subseteq K : L$ is a subfield of K and $a \notin L \}$ . Such subfields have been well investigated in the literature. For example, Quigley [15] described the structure of $K / M$ in detail where K is an algebraically closed field and M is a maximal subfield of K without a given point $^ { a , }$ and used Galois theory to give existence proofs of M more precise than that trivially given by Zorn’s Lemma. We restrict our attention to the case that $K = \mathbb { R }$ . We show that the usage of AC (the Axiom of Choice) is necessary for the existence of a maximal subfield of <sup>R</sup> without a given point (Corollary 2.7). On the other hand, by assuming CH, we construct a maximal subfield of <sup>R</sup> with Hausdorf dimension 0 such that some given point is not in its algebraic closure relative to <sup>R</sup> (Proposition 4.10).

The structure of the paper is as follows: Section 2 deals with subrings and subfields of <sup>R</sup>. In Section 3 we discuss some simple results concerning the basic properties of subgroups and prove Theorem 1.4. In Section 4 we assume CH in the constructions and prove Theorem 1.5. We also show that A in Theorem 1.5 cannot be $F _ { \sigma }$ (Proposition 4.6). Due to the variety of the tools used for the results and the independence of the methods, we postpone the introduction of notation and terminologies, and only recall them when being used.

[已省略: references]


---

## 📑 关键章节 | RADAR: Recall Augmentation through Deferred Asynchronous Retrieval

**arXiv ID**: [2506.07261](https://arxiv.org/abs/2506.07261)

## 1 Introduction

Modern video-sharing platforms confront an extreme retrieval challenge: every user session must search through billions of candidate videos to prepare a personalized list within a few milliseconds. Production systems therefore follow a three-stage funnel — retrieval → pre-ranking → ranking — where a very lightweight retriever supplies roughly O(10^3) items, a moderate pre-ranker trims this set to the low hundreds, and an expressive ranker finally orders the shortlist for display. However, this cascaded design imposes hard ceiling on recall because the retriever must satisfy the tightest latency budget, it relies on inexpensive signals (e.g. dot-product two-tower models [1, 2] or K-nearest-neighbour CF indices) and consequently fails to surface many highly engaging items. In fact, in offline simulation studies, we observe single-digit Recall@200 from standard user-to-item and item-to-item retrieval methods (Fig. 1). This results in a retrieval bottleneck that throttles downstream ranking quality.

![](images/e99cfd7920f6b7edf57eed846b150b08feb4dd23df0808e33dfc999a4adee115.jpg)  
Figure 1: Recall@K as a Function of Candidate Retrieved Size (K) from Two Tower based DNN model

Research has therefore explored hybrid offline–online architectures that pre-compute richer candidates when latency is less constrained. These often focus on pre-computing sophisticated retrieval candidates using complex offline models, subsequently relying on lightweight online models for serving [5, 6]. For instance, TwERC [6] augments a real-time lightweight ranker with complementary sources like graph-based neighbors and cached ranker scores, significantly improving coverage. Similarly, other hybrid architectures combine batch-trained models with real-time bandit layers [5] to balance exploration and exploitation. Recent papers also revisit retrieval using acceleratorbacked deep matching models to close the expressiveness gap between retrieval and ranking [7].

While these approaches offer valuable improvements, they still restrict the retrieved candidates to what a server-side model can compute in real time. We observe that significant computational resources are frequently available during off-peak hours. This observation motivates our proposed Recall Augmentation through Deferred Asynchronous Retrieval (RADAR), a novel framework that leverages these off-peak resources to perform computationally expensive final-stage ranking step on a much larger set of candidates (50X) asynchronously, before the user session begins.

To the best of our knowledge, no prior hybrid retrieval system— including TwERC [6]—fully decouples candidate generation from online serving constraints by (i) running the production-grade ranking model offline on a 50X larger set of retrieved candidates and (ii) refreshing each user’s pre-ranked list on a usage-adaptive cadence

## 2 Proposed Approach - RADAR

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

[已省略: references]


---

## 📑 关键章节 | Stealthy LLM-Driven Data Poisoning Atacks Against Embedding-Based Retrieval-Augmented Recommender Systems

**arXiv ID**: [2505.05196](https://arxiv.org/abs/2505.05196)

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

## 3 Experimental Setup

We conduct our experiments on top of a retrieval-augmented recommendation (RAG) pipeline that integrates a Large Language Model (LLM) from OpenAI and a Sentence Transformer (ST) encoder for embedding-based retrieval. Specifically, the pipeline first employs the Sentence Transformer to select candidate items based on the semantic closeness of item descriptions, and then an OpenAI-based LLM re-ranks these candidates or generates final textual recommendations.

Although we report results primarily on the widely used Movie Lens “ml-latest-small” dataset in this paper, we have also evaluated the proposed methods on additional benchmark datasets; due to space limitations, we present here only the detailed findings for the MovieLens dataset.

Within the MovieLens corpus, we categorize items into <sub>long-tail</sub> (unpopular) vs. <sub>short-head</sub> (popular) segments, inject adversarial textual edits, and assess the resulting changes in item ranks and system-level metrics (e.g., Recall@??, nDCG@??). Our system rein dexes or retrains on these modified descriptions, thereby simulating real-world scenarios where metadata updates could inadvertently (or maliciously) be incorporated into a live recommender. We build the user profile for the retrieval stage in two ways: (1) <sub>Manual</sub> construction using a structured template; and (2) <sub>LLM-based</sub> summarization that generates a user’s preferences automatically. In Table 1 <sub>(Tab</sub> <sub>2</sub> <sub>and</sub> <sub>3),</sub> we diferentiate these two methods when evaluating final recommendations. All remaining steps in our pipeline (retrieval and re-ranking) remain unchanged.

## 4 Results and Discussion

We now present our key experimental findings, structured around these three main research questions (RQs).

<sub>RQ1:</sub> Are LLM-based textual attacks efective at pushing a target item ranking up or down (both at retrieval top-?? and recommendation stage top-??)?

<sub>RQ2:</sub> Does attack eficacy vary across LLMs model e.g., OpenAI vs. Sentence Transformer retrieval?

<sub>RQ3:</sub> How do these modifications afect overall recall or nDCG? Can poisoning degrade system-wide performance?

## 5 Conclusion

Our work demonstrates that carefully designed textual perturbations (modifications) in item metadata can strategically alter recommendations in Retrieval-Augmented Generation (RAG) systems, emphasizing the need for robust textual provenance checks. Through a systematic exploration of diferent attack strategies—including emotional rewording<sup>,</sup> neighbor-based borrowing<sup>,</sup> <sup>and</sup> hybrid chain-<sub>ing</sub>—our experiments reveal that even <sub>small-scale</sub> <sub>semantic</sub> <sub>ma-</sub> <sub>nipulations</sub> can efectively boost the visibility of long-tail items or suppress popular ones, often while remaining stealthy and dificult to detect. These findings underscore the potential provider-side vulnerabilities in RAG-based pipelines and the necessity of defensive measures to safeguard recommendation integrity.

[已省略: acknowledgments]


---

## 📑 关键章节 | Adaptive Candidate Retrieval with Dynamic Knowledge Graph Construction for Cold-Start Recommendation

**arXiv ID**: [2505.20773](https://arxiv.org/abs/2505.20773)

## 1 Introduction

In real-world recommender systems, cold-start items are routinely introduced with few or no interaction records and incomplete metadata. This lack of information prevents models from accurately estimating user preferences, resulting in poor recommendation quality, reduced user satisfaction, and ultimately revenue loss (Huang et al., 2023; Zhang et al., 2025). To tackle this challenge, recent works have explored two main directions: (i) KG–based methods that construct structured representations of the item catalog (Wang et al., 2019b; Guo et al., 2020), and (ii) LLM-based methods that leverage LLMs as training-free recommenders, typically prompting on user histories with a small set of candidate items (Sanner et al., 2023; Hou et al., 2024).

However, both directions face critical limitations in practical deployment (Lin et al., 2025). Static KGs are expensive to construct and maintain, and they quickly become outdated as items, attributes, and relations change (Wang et al., 2019a). Updating these graphs to reflect catalog changes typically requires substantial offline engineering and cannot keep up with real-time changes. LLM-based approaches, meanwhile, are usually formulated as re-rankers over a pre-filtered candidate set rather than as end-to-end retrieval systems (Hou et al., 2024). Because LLMs operate under bounded context windows and token budgets, only a curated subset of items and a truncated user history can be included in the prompt, necessitating a separate task-specific retrieval pipeline. While recent work introduces retrieval-aware prompting, its retrieval remains shallow, limited to keyword matching or single-hop similarity search, which still limits performance and reduces adaptability in dynamic coldstart settings (Liang et al., 2025; Kieu et al., 2025).

To address the above limitations, we introduce ColdRAG, a retrieval-augmented framework built around two key modules. The first module, Dynamic Knowledge Graph Construction, automatically builds and incrementally updates a domain graph from catalog fields (e.g., titles, descriptions, attributes, reviews), allowing the structure to evolve naturally as the catalog changes. The second module, Adaptive Candidate Retrieval over Knowledge Graph, removes the need for pre-filtered candidate lists by treating candidate generation as LLMguided, goal-directed traversal over the graph, assembling a compact, high-utility candidate set together with evidence paths that justify each recommendation. Empirically, ColdRAG consistently surpasses strong training-based and training-free baselines across diverse product domains with large performance gains.

Our contributions are threefold:

• We introduce a dynamic KG construction that automatically builds and incrementally updates the graph as items and relations evolve.

• We eliminate the unrealistic assumption that a curated candidate list is already in the LLM’s context window by integrating candidate retrieval with LLM-guided multi-hop reasoning.

• We demonstrate strong cold-start performance on multiple benchmarks and provide extensive analyses on component effectiveness, stability, and robustness.

[已省略: 2 related works]

## 3 Proposed Method

We present ColdRAG, a retrieval-augmented generation framework for cold-start recommendation.

ColdRAG equips an LLM with a dynamically constructed KG that enables semantic reasoning and adaptively builds candidate items for context-aware and controllable recommendation. The overall framework is illustrated in Figure 1. For the problem setting, we follow the sequential recommendation task, where each user u has an interaction history $H _ { u } = [ i _ { 1 } , i _ { 2 } , \dotsc , i _ { n - 1 } ]$ and the goal is to recommend the next item $i _ { n }$

## 4 Experiments

We conduct comprehensive experiments to evaluate the effectiveness of ColdRAG in item cold-start recommendation. Our analysis is organized around the following research questions:

• RQ1: Does ColdRAG effectively address the item cold-start recommendation problem?

• RQ2: How effective is the Dynamic Knowledge Graph Construction?

• RQ3: How does Adaptive Candidate Retrieval enhance recommendation performance?

• RQ4: Does ColdRAG exhibit stable and consistent generation across runs?

• RQ5: Does ColdRAG reduce hallucination and avoid out-of-domain recommendations?

## 4.1 Experimental Setup

## 4.1.3 Evaluation Metrics

We evaluate recommendation performance using two standard metrics widely adopted in cold-start tasks: Recall@k and NDCG@k, following prior work (Hou et al., 2022; Wei et al., 2021; Liang et al., 2025). All results are reported at k = 10.

## 4.2 Results

## 4.2.1 Overall Performance (RQ1)

Table 2 compares ColdRAG with all baselines on the Games, Toys, and Office datasets. ColdRAG consistently achieves the best results across all metrics and domains, outperforming both trainingbased and training-free baselines. It improves Recall@10 by +78.6%, +26.76%, and +123.81% over the strongest baselines on Games, Toys, and Office, respectively. The larger gains in Recall over NDCG indicate that ColdRAG is effective in both identifying and ranking relevant items, but its main strength lies in retrieving correct candidates into the top set. Among training-based models, TDRO shows the best performance but still falls short of ColdRAG, showing that even robustly trained models struggle to generalize under sparsity. ColdRAG’s retrieval-augmented design instead captures fine-grained semantic relations through LLMguided multi-hop reasoning, yielding better coldstart adaptability. Within the training-free methods, LLM and LLMRank perform moderately but rely on fixed candidate lists, restricting contextual exploration. KALM4Rec enriches prompts via keyword retrieval yet remains less strong than ColdRAG, whose KG-based retrieval enables deeper reasoning over semantically linked concepts beyond shallow keyword matching. Overall, ColdRAG’s consistent gains underscores the benefit of integrating KG-based retrieval with LLM reasoning for robust item cold-start recommendation.

![](images/60b7e4bc2314766b007a3e2c74f424440072b13028850decd62cae9747b19bf4.jpg)  
Figure 2: Performance comparison of ColdRAG vari ants across three domains using GPT, showing that both core modules (G and R) add performance gains.

## 4.2.3 Analysis on Stability and Hallucination (RQ4 & RQ5)

LLM-based recommenders often suffer from generation inconsistency and hallucination, producing unstable or out-of-domain outputs. We evaluate ColdRAG on these aspects using five independent runs on the Games dataset. As shown in

![](images/11d21958612e57a3e35cdb1d89cca60660f22bcb207d5da1611c441aa142b080.jpg)

(b)  
![](images/bc367fcc5c9e7f4befa99ce949df3f4631e271435946e9052f3959747edceff8.jpg)  
Figure 3: (a) Recall@10 box plots over five runs for training-free baselines. (b) Out-of-domain generation rates, both evaluated on the Games dataset with GPT.

Figure 3, ColdRAG achieves high average performance and low variance in Recall@10, demonstrating stable, reproducible generation compared to other training-free baselines. This robustness stems from structured retrieval and reasoning, providing consistent semantic grounding rather than relying on prompt randomness. We also measure hallucination rates, defined as the proportion of generated items not present in the dataset. While other LLMbased models, including LLM and LLMRank variants, exhibit 5–10% out-of-domain outputs even with predefined candidate lists, ColdRAG reduces this rate to 3.15%. This improvement shows that knowledge-grounded retrieval helps the model construct and reason over a semantic graph, enabling it to retrieve contextually valid items and constrain generation within the domain. In summary, beyond achieving superior recommendation performance, ColdRAG also exhibits robust stability and minimal hallucination, which are essential for practical and trustworthy recommender systems.

## 5 Conclusion

We presented ColdRAG, a retrieval-augmented generation framework for item cold-start recommendation. ColdRAG dynamically builds a knowledge graph from sparse metadata and performs LLM-guided multi-hop reasoning to adaptively retrieve candidate items aligned with user preferences—without relying on pre-built candidate lists. This design enables accurate and stable recommendations, making ColdRAG a practical and industryready solution for real-world cold-start scenarios.

[已省略: references]

## E Hyperparameter Analysis

We analyze the impact of the edge scoring threshold λ, which controls how strictly ColdRAG filters edges during multi-hop reasoning. As shown in Figure 10, ColdRAG achieves the best performance when λ = 0.7. A smaller threshold allows irrelevant edges to remain, while an excessively large threshold overly constrains traversal and misses useful nodes. This result indicates that a moderate threshold effectively balances relevance and diversity in the retrieved candidates, yielding the most robust overall performance.

![](images/15b44f1086ff34216dda3bd467372713a31d4f29bf294c7469274dd804b57a8a.jpg)  
Figure 10: Effect of the edge scoring threshold λ on ColdRAG’s performance.


---

## 📑 关键章节 | ItemRAG: Item-Based Retrieval-Augmented Generation for LLM-Based Recommendation

**arXiv ID**: [2511.15141](https://arxiv.org/abs/2511.15141)

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

[已省略: 2 related work and preliminary]

## 3 Proposed method

In this section, we introduce ItemRAG, an item-based retrievalaugmented generation (RAG) method for LLM-based recommendation. We first give an overview of the ItemRAG pipeline (Section 3.1) and detail our retrieval strategy (Section 3.2).

## 4 Experiment

In this section, we analyze the efectiveness of ItemRAG in the LLMbased recommendation tasks. We answer the questions below:

RQ1. How efective is ItemRAG for LLM-based recommendation?

RQ2. How accurate is ItemRAG at recommending cold-start items?

RQ3. Do LLM-based recommender systems make efective use of the item information retrieved by ItemRAG?

RQ4. Do all ItemRAG key components contribute to performance?

## 4.1 Experimental setting

Datasets and evaluation protocol. We use four domains from the latest Amazon Reviews dataset [3]: Sports & Outdoors (Sports), Toys & Games (Toys), Beauty & Personal Care (Beauty), and Arts, Crafts & Sewing (Arts). Further details, including preprocessing steps and dataset statistics, are provided in Appendix [13]. For evaluation, following prior work [14, 23], we use a leave-one-out protocol: for each user, the last purchased item is held out for testing, and the remaining history is used as input. Also, following [14], we prompt the LLM to rank 10 candidate items for the target user’s next purchase; the set includes 1 ground-truth item and 9 randomly sampled items, and results with larger candidate sets are reported in Appendix [13]. We run each experiment three times and report the mean metrics. We further conduct a Wilcoxon signed-rank test between ItemRAG and each baseline to assess statistical significance. In addition, we provide an inference runtime analysis of ItemRAG in the appendix [13].

Baseline methods and ItemRAG. For comparison, we use 9 baseline methods: two graph-based models (LightGCN [2] and Light-GCN++ [15]), two sequential models (SASRec [5] and BERT4Rec [20]), one naive zero-shot LLM-based recommender, and four user-based RAG methods (ICL [21], AdaptRec [25], ReACT [4], and CoRAL [23]). For LLM-based methods, we use GPT-4.1-mini as the backbone. For the retrieval process in ItemRAG, we use 5 similar items per item and sample 50 items in the final retrieval set. Further details on baselines, hyperparameters, and prompts are given in Appendix [13].

## 5 Conclusion and discussion

In this work, we introduce ItemRAG, an item-based RAG technique for LLM-based recommendation. The key idea is to augment indi vidual items in the target user’s purchase history or the candidate set, instead of relying on coarse user-level augmentation. Especially, its carefully designed retrieval strategy, guided by co-purchase in formation, retrieves items that are recommendation-relevant rather than merely semantically similar, and also augments cold-start items. Through extensive experiments, we demonstrate the efec tiveness of ItemRAG for LLM-based recommendation and cold-start item recommendation. One limitation of ItemRAG is that incorpo rating additional retrieved information can increase the length of the input prompt to the LLM recommender, which in turn leads to higher API costs and longer inference time. Reducing the token usage by the retrieved information is thus an important direction for future work, especially for practical deployment.

Acknowledgements. This work was partly supported by the National Research Foundation of Korea (NRF) grant funded by the Korea government (MSIT) (No. RS-2024-00406985, 40%). This work was partly supported by Institute of Information & Communications Technology Planning & Evaluation (IITP) grant funded by the Korea government (MSIT) (No. RS-2022-II220871, Development of AI Autonomy and Knowledge Enhancement for AI Agent Collabo ration, 50%) (No. RS-2019-II190075, Artificial Intelligence Graduate School Program (KAIST), 10%).

[已省略: references]


---

## 📑 关键章节 | Efficient Cold-Start Recommendation via BPE Token-Level Embedding Initialization with LLM

**arXiv ID**: [2509.13179](https://arxiv.org/abs/2509.13179)

## I. INTRODUCTION

The cold-start issue is a major challenge in the recommenders, in which a recommender cannot access historical interactions between new users or items, which constrains the effectiveness of Collaborative Filtering (CF) models[1]. Traditional hybrid techniques, mixing CF with content-based features, have difficulties in approximating semantic relations with much subtlety, particularly in the face of sparse metadata, or linguistically demanding metadata[2]. Recent Large

Language Models (LLMs) have allowed contextual representation learning based on textual inputs, yet current practice tends to use sentence-level embeddings which mask subword-level semantics which are important in personalization[3].

To alleviate this, we present an approach that utilizes a Byte Pair Encoding (BPE) tokenization step to subword decomposition mechanism and learnt embeddings through a pre-trained LLM. Given a textual input x, we tokenize it into BPE tokens $\{ t 1 , t 2 , \ldots , t n \}$ <sub>.</sub> Each token ti is mapped to an embedding $\mathbf { e i } = \mathrm { L L M } ( t i )$ , and the item or user representation vx is computed as:

$$
v x = (1 / n) * \Sigma e i
$$

This vector vx maps to the cold-start embedding, to calculate recommendation scores by dot product with previously trained entity embeddings. It is architecture-agnostic and can fit directly into any matrix factorization or neural CF pipeline. Wide scale tests using benchmark datasets show that BPEinitialized LLM embeddings provide superior performance of Roaches@K and NDCG@K, particularly against cold-start tight splits[4]. Using this subword-aware initialization, instant personalization is possible without user-item history leading to a lightweight but semantically rich resolution to the coldstart problem[5].

[已省略: ii. related work]

## III. METHODOLOGY

## 3.1 Overview of the Architecture

The given architecture aims at addressing the cold-start problem with the extraction of semantically rich, fine-grained embeddings via Byte Pair Encoding (BPE) alternatives of textual metadata and initialization of these embeddings with the help of a pre-trained Large Language Model (LLM)[14]. Such embeddings are subsequently incorporated into a collaborative filtering backbone to meet top-K recommendation of items.

## 3.2 Model Selection

We employ a transformer-based encoder, specifically a frozen version of DistilBERT or RoBERTa, to avoid computational overhead. Let the BPE tokenizer output a token sequence $T = \{ t 1 , t 2 , \dots , t n \}$ for a given input text $x \in \mathbb { R } ^ { \wedge } d$ . Each token <sub>??</sub> is mapped to an embedding <sub>??</sub> $\in \ \mathbb { R } ^ { \wedge } h$ using: ei = LLM <sub>(??).</sub> The item or user representation <sub>??</sub> is then computed via a mean pooling strategy: $v x = ( 1 / n ) * \Sigma e i$ This representation <sub>??</sub> $\in \ \mathbb { R } ^ { \wedge } h$ becomes the cold-start vector used in downstream recommendation tasks.

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

## V. RESULTS AND DISCUSSION

## 5.2 Performance Evaluation

Our model outperforms approximations with random initialization and sentence-level baselines across all the metrics of evaluation. With the MovieLens dataset, Recall@10 was more than 27 percent better than sentence embeddings. The growth of NDCG@10 also shows that model ranks relevant objects higher, which is one of the crucial elements of user engagement in production systems[29]. The attention-based aggregation also played its role in this increase, as well, where some of the tokens would overpower the semantic content (e.g., limited edition or collector series). These results confirm the hypothesis that the subword-level representations proved more expressive in the cold-start modelling of the entities[30].

## VI. CONCLUSION AND FUTURE WORK

The proposed study presented an effective and innovative approach to cold-start recommendation based on the initialization of Byte-Pair Encoding (BPE) token-level embedding with the help of large language models (LLMs). The approach is particularly effective in filling the gap that the traditional user-item collaborative filtering approach has in sparse user-item interaction data since it introduces substantial contextualization through the transformer-based approach to subword tokens and their combinations. The approach showed impressive results when tested in a coldstart environment on heterogeneous tasks like books, movies, and games. Empirical evidence proved the higher performance of BPE-LLM in the top-N recommendation task as Recall@10 and NDCG@10 in comparison with sentencelevel and randomly initialized baselines. In addition to that, t-SNE visualization demonstrated semantic clustering, confirming the fidelity and generalizability of the learned embedding space. Importantly, the model is efficient to scale, with embedding inference taking only forward passes of a frozen LLM encoder, which makes it suitable to deploy at scale in modern recommender systems.

[已省略: references]


---

## 📑 关键章节 | Towards Eficient Certification of Maritime Remote Operation Centers – Ansatz zur efizienten Zertifizierung von maritimen Fernsteuerungszentren

**arXiv ID**: [2508.00543](https://arxiv.org/abs/2508.00543)

## 1 Introduction

Increasing levels of automation is being build into vessels, leading to the advent of Maritime Autonomous Surface Ships (MASS), as defined by the Internation Maritime Organization (IMO) [29]. Shore-based Remote Operation Centers (ROCs) are emerging as a supplemental technology alongside MASS to monitor or remote-control such ships in harbors, in coastal waters, or for inland waterways [19, 7]. There exist various novel approaches adapted for the Hazard Analysis and Risk Assessment (HARA) of MASS to cope with the complexity that is introduced by automation technology [56]. For example, the Risk-based Assessment Tool commissioned by the European Maritime Safety Agengy (EMSA) [34]. Regarding classification of MASS, there exists class guidelines such as the DNV-CG-0264 on Autonomous and Remotely Operated Ships. These safeguarding approaches are centered around MASS and possible remote control components are considered as MASS functionality. Therefore, the safety of ROCs is considered as part of the MASS HARA. In this concept paper, we put forth the idea to collect safety-relevant artifacts for a generic ROC in a database to enable their reuse. Hence, to facilitate more eficient certification of MASS-ROC pairs, we tackle the research question

How can we build a hazard database that integrates technical as well as human hazards and facilitates the eficient certification of generic ROC-MASS pairs with well-defined interfaces?

In this regard, we contribute

∙ a review of standards, regulations, and HARA methods in the maritime domain in section 2,

∙ a generic ROC-MASS functional architecture as a starting point for a hazard database in section 3,

∙ a categorization of hazard sources for ROCs, a suitability analysis for methods to adequately cover these categories, and potential benefits of a hazard database in section 4.

[已省略: 2 related work]

## 2.2 Relevant Methods for Hazard Analysis and Risk Assessment

For conventional vessels, there exists a wide range of well-established HARA methods which are commonly applied in practice, e.g., Failure Mode and Efect Analysis (FMEA) or Fault Tree Analysis (FTA). To address the specific challenges posed by automated maritime systems, such as their reliance on sensor perception and the complexity of system interactions, adaptions of established methods as well as new approaches have been explored in recent research [56, 47, 36]. However, only a limited number of studies explicitly consider ROCs. A literature review provided by Zhou et al. [57], which evaluates the suitability of commonly used HARA methods for automated maritime system, highlights this gap. Notably, the authors observe that among the evaluated studies, so far only System-Theoretic Process Analysis (STPA) was applied with explicit consideration of the communication between vessel and ROC [54, 55, 49, 1]. Similarly, another literature review on risk models for automated maritime systems by Thieme et al. [47] reports that only two of the investigated studies explicitly address the communication with a ROC – one employing STPA, and the other a combination of brainstorming and Bayesian Networks [54, 53]. Furthermore, Li et al. emphasize the importance of incorporating human factors into the HARA of automated maritime systems, noting that these systems constitute highly complex socio-technical systems in which the role of the remote operator is significantly more complex than that of a traditional onboard operator [36].

In the following, we briefly introduce common HARA methods that may be applicable for ROCs, as well as some emerging approaches specifically developed for highly automated systems. As the human operator is of particular relevance for remote operation, we consider not only HARA methods focusing on technical system safety but also methods that explicitly address human factors.

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

## 3.3 Functional Architecture

We start by modeling the functional architecture of a generic MASS-ROC pair at a high level of abstraction with a focus on the flow of information. This functional architecture, shown in Figure 3, serves as a starting point for building a hazard database as it defines generic interfaces between the involved entities. Note that the abstraction level needs to be detailed enough to enable the identification and analysis of hazards and abstract enough to keep HARA eforts manageable. Inside the ROC itself, we model exactly one control station with three components:

![](images/79d89803352871ec9e67a8341cf677e35502107d5e6d978986b083551e5cc7a2.jpg)  
Fig. 3: Functional architecture for a single control station inside a shore-based ROC and a generic MASS. The flow of in formation in encoded by three diferent types of arrows.

Data Communication Middleware (DCM): This component is responsible for managing the exchange of data between the ROC and the MASS. As indicated by the blue color coding, this component is present in the MASS as well. However, for brevity, we abstain from explicitly modeling it within the MASS here. Crucially, the DCM defines the interfaces between the ROC and the MASS. As input to the ROC we have the transfer of all relevant data from the MASS. This inncludes the MASS’s data model and environment model. On the side of the ROC’s output, the DCM facilitates remote control (direct or tactical) of the MASS by the ROC’s human operator.

Human Machine Interface (HMI): The HMI bridges the gap between all inputs to the ROC and its outputs by interacting with the ROC’s human operator. In particular, the HMI feeds the human operator’s mental model with a visual, acoustic and haptic representation of data as well as human communication from external entities such as the MASS’s human operator (if present), vessel trafic service (VTS), the harbor ofice, and other ships. His mental model infuses the decision making which directly leads to the human operator’s output in form of either taking control of the MASS or communication with other humans - both of which are managed by the HMI’s communication hub.

Human Operator: The final component of the ROC is the human operator. All his actions within the ROC are through the HMI. His output is the HMI’s input and vice versa as described before in section 3.1.

The functional architecture of Figure 3 can now be used with various HARA methods. For example, it supports keyword-based approaches to hazard identification such as HAZOP – which are also suggested by RBAT [34, § 4.2]. Note that for a concrete ROC, the level of detail should be expanded locally when conductive for hazard identification and analysis. E.g., applying the keyword not provided to visual, acoustic, and haptic representation of data, a more detailed modeling of the HMI’s data representation functionality becomes necessary. If one wants to use STPA, a corresponding control loop can easily be derived from the architecture of Figure 3. Moreover, methods for causal analysis such as FTA/ETA or causal Bayesian [20] networks profit greatly from a functional architecture, because it supports the modeling of the system’s internal dependencies.

[已省略: 4.3 preliminary suitability analysis]

## 5 Conclusion

In this paper, we laid first steps towards building a hazard database for certification of shore-based ROCs. Based on a generic MASS-ROC functional architecture we derived three diferent categories of hazard sources while identifying SOTIF as a relevant, complementary category. Moreover, we performed a preliminary suitability analysis of HARA methods which may cover these categories.

Regarding future work, conducting a HARA for a concrete shore-based ROC by combining adequate techniques will enable the initial build-up of safety artifacts for the envisioned Hazard-DB.

[已省略: references]


---

## 📑 关键章节 | Selective LLM-Guided Regularization for Enhancing Recommendation Models

**arXiv ID**: [2512.21526](https://arxiv.org/abs/2512.21526)

# Selective LLM-Guided Regularization for Enhancing Recommendation Models

Shanglin Yang<sup>∗</sup>

Zhan Shi<sup>∗</sup>

kudoysl@gmail.com

ashi2@scu.edu

[已省略: acm reference format:]

## 1 Introduction

Recommendation systems underpin modern digital platforms by enabling content discovery, personalization, and user engagement across domains such as e-commerce, entertainment, and online media. Classical approaches—including collaborative filtering (CF), matrix factorization (MF), neural recommenders, and graph-based models achieve strong performance when user interaction histories are suficiently dense. However, their efectiveness deteriorates in sparse regimes, such as cold-start users, long-tail items, and scenarios where user preferences are weakly expressed.

Large language models (LLMs) have emerged as powerful auxiliary knowledge sources for recommendation, ofering rich semantic priors and strong reasoning capabilities that enable preference inference even from minimal user interaction data [10]. This makes them particularly promising in cold-start and sparsely observed regions where traditional recommenders tend to underperform. However, existing approaches to leveraging LLM signals remain fundamentally limited. Directly deploying LLMs as recommenders is prohibitively expensive and prone to issues such as position bias and hallucinated predictions. Meanwhile, global knowledge transfer methods [15, 20] require the downstream model to imitate LLM outputs uniformly across the entire user–item space, regardless of whether the LLM is reliable for a given instance. Recent attempts to distill LLM knowledge into classical models partially alleviate these issues, but they often depend on fine-tuned LLMs and still struggle to deliver consistent gains across diferent architectures or datasets.

<sup>Empirical</sup> <sup>motivation.</sup> Beyond high-level intuition, recent evaluations of LLM-based recommenders report localized strengths (notably on short histories and re-ranking) alongside systematic weaknesses including strong candidate position bias and occasional hallucinations [7]. These phenomena imply that LLM signals are contextually reliable rather than uniformly trustworthy. Our design follows directly from this evidence: instead of global imitation, we selectively invoke LLM guidance under reliability conditions predicted by a lightweight, learnable gating mechanism.

We propose Selective LLM-Guided Regularization (S-LLMR), a training framework that treats LLM knowledge as a conditional regularizer rather than a global supervisory signal. Instead of enforcing uniform imitation of LLM predictions, S-LLMR incorporates LLM-generated soft rankings only in regions where LLMs exhibit empirical advantages. This selective integration ensures that LLM guidance is beneficial rather than disruptive. We prompt an LLM using a compact representation of each user’s recent interaction history to generate soft relevance scores over candidate items. All scoring is performed ofline, introducing no inference-time overhead.A gating function controls whether LLM supervision is activated for a given user–item pair. This gate identifies regions where LLM signals are empirically reliable. With the gate ctive, we apply a weighted pairwise ranking loss that encourages the recommender to align its relative item ordering with LLM soft rankings, while automatically suppressing the influence of unreliable LLM predictions.

Extensive experiments across multiple datasets and diverse recommendation backbones show that S-LLMR consistently surpasses global distillation baselines, delivering substantial improvements in sparse regimes such as cold-start and long-tail scenarios. The contribution of our paper:

• We introduce a gated LLM-based regularization paradigm that selectively incorporates LLM signals, avoiding the draw backs of global distillation and remaining fully model-agnostic.

• We design S-LLMR, which combines a reliability-aware gat ing mechanism with an LLM-guided pairwise ranking loss for targeted knowledge transfer.

• Extensive experiments across multiple backbones show con sistent AUC improvements, with especially strong gains in cold-start and long-tail scenarios.

[已省略: 2 related work]

## 3 Method

<sub>As</sub> <sub>shown</sub> <sub>in</sub> <sub>Figure</sub> <sub>1,</sub> <sub>The</sub> Selective LLM-Guided Regulariza-<sup>tion</sup> <sup>for</sup> <sup>Recommendation</sup> (S-LLMR) is a model-agnostic training framework that selectively leverages large language models (LLMs) to regularize classical recommender models only in regions where LLM predictions are empirically reliable. Formally, given a user <sup>??</sup> and item <sup>??</sup>, a base recommender produces a predicted relevance score $s _ { u , i } ,$ while the LLM provides a soft preference score $s _ { u , i } ^ { L L M }$ Our goal is to integrate LLM guidance selectively through pairwise ranking supervision with an gating signal. There are three main modules included in the pipeline.

![](images/83f8ed84334d9430860d2cbbee8fc85a38ce9b28abe13028241a45f6038d7d48.jpg)  
Figure 1: Illustration of our selective LLM-guided regularization framework. Left: In the ofline phase, the LLM is prompted to produce soft relevance scores Right: In the training phase, a base recommender produces prediction scores, and the LLM signals are incorporated through a pairwise ranking regularizer whose contribution is controlled by a gating function.

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

## 4.5 Evaluation Protocol

We adopt the standard full-ranking evaluation setting, where each test interaction is ranked against all items that the user has not interacted with in the training or validation sets. Since our goal is to assess both global predictive accuracy and robustness in sparse regions, we report AUC as the sole evaluation metric.To further evaluate model performance under challenging conditions, we report AUC on two key sub-populations:

• <sup>Cold-start</sup> <sup>users</sup>: test interactions belonging to users with fewer than <sup>??</sup> historical interactions, i.e., |H (<sup>??</sup>)| <sup>< ??</sup>. We set <sup>??</sup> = 3 in our experiments.

• <sup>Long-tail</sup> <sup>items</sup>: items in the bottom 20% of the popularity distribution based on training data. We first identify long-tail item IDs from the training set and then select the correspond ing interactions from the test set to form the long-tail subset.

These stratified subsets isolate the efect of S-LLMR in sparse and semantically challenging regimes, enabling a clearer understanding of how selective LLM guidance improves recommendation quality under conditions where traditional models typically struggle.

## 5 Results

Our results show that S-LLMR consistently improves AUC across all backbones and domains, delivers the largest gains in cold-start and long-tail scenarios.

## 5.1 Overall Performance Across Backbones

The overall performance are shown in Table 2. Across all six backbone models including DeepFM, xDeepFM, AutoInt, DCNv1, DCNv2, and DIN. S-LLMR achieves the strongest AUC scores on every Amazon domain. The improvements over non-LLM baselines (None, KD, KAR) are consistent and sizable, and our method further surpasses the LLM-CF approach by margins of 0<sup>.</sup>003–0<sup>.</sup>01 AUC depending on the model and dataset. Architectures that struggle more with seman tic sparsity, such as AutoInt and DCNv1, exhibit particularly large gains: AUC improvements reach 0<sup>.</sup>007–0<sup>.</sup>01 on Sports and exceed 0<sup>.</sup>02 on the Toys domain. These results validate that selectively in corporating LLM signals rather than distilling them globally allows the recommender to capitalize on LLM strengths while avoiding the noise and positional bias present in many LLM outputs, yield ing reliable improvements across heterogeneous architectures and domains.

## 6 Conclusion

This paper introduced S-LLMR, a selective LLM-guided regularization framework that integrates LLM semantic knowledge into classical recommendation models in a reliability-aware manner. Rather than imitating LLM predictions globally, our method activates LLM-based pairwise ranking supervision only in regions where LLMs exhibit clear empirical advantages—cold-start users, long-tail items, and high-uncertainty predictions. Extensive experiments across six backbone recommenders and three Amazon domains demonstrate that S-LLMR not only improves overall AUC but yields particularly large gains in sparse and semantically challenging regimes, confirming that LLM signals are most beneficial when applied selectively. Our ablations further show that global LLM loss can degrade performance, whereas gated pairwise regularization consistently strengthens model robustness. Overall, S-LLMR pro vides a simple, model-agnostic, and computation-eficient approach for leveraging LLM knowledge to bridge long-standing weaknesses in collaborative filtering, ofering a promising direction for future reliability-aware LLM–recommender integration.

[已省略: acknowledgments]


---

## 📑 关键章节 | Towards Agentic Recommender Systems in the Era of Multimodal Large Language Models

**arXiv ID**: [2503.16734](https://arxiv.org/abs/2503.16734)

# Towards Agentic Recommender Systems in the Era of Multimodal Large Language Models

Chengkai Huang<sup>1</sup>, Junda Wu<sup>2</sup>, Yu Xia<sup>2</sup>, Zixu Yu<sup>2</sup>, Ruhan Wang<sup>3</sup>, Tong Yu<sup>4</sup>, Ruiyi Zhang<sup>4</sup>, Ryan A. Rossi<sup>4</sup>, Branislav Kveton<sup>4</sup>, Dongruo Zhou<sup>3</sup>, Julian McAuley<sup>2</sup>, Lina Yao<sup>1,5</sup>

<sup>1</sup>University of New South Wales, <sup>2</sup>University of California San Diego, <sup>3</sup>Indiana University, <sup>4</sup>Adobe Research, <sup>5</sup>CSIRO’s Data61

{chengkai.huang1, lina.yao}@unsw.edu.au, {juw069, yux078, ziy040, jmcauley}@ucsd.edu, {ruhwang, dz13}@iu.edu, {tyu,

ruizhang, rrossi, kveton}@adobe.com

## 1 Introduction

With the rapid growth of online services, recommender systems (RS) have become essential for addressing users’ information needs and alleviating information overload [47, 92]. These systems provide personalized recommendations across various domains, including e-commerce, movies, music, etc. Despite the diversity of recom mendation tasks such as top-K recommendation and sequential recommendation, the core objective remains consistent: to predict a user’s preferences for each candidate item and generate a ranked list tailored to the user [31].

However, current RSs still face several significant limitations in meeting diverse user needs. First, current RSs typically rely on ID-based features that work only within specific domains or platforms. Their inability to integrate open-domain knowledge, such as common sense reasoning and cross-platform behavioral patterns, significantly constrains their capacity to interpret and model user interests in a broader context. Second, current methods typically optimize well-defined engagement metrics derived from historical interaction data (e.g., click-through rates and purchase histories). Although such methods can be efective for localized objective functions, they often conflate observable behaviors with latent user intent, since implicit feedback mechanisms cannot distinguish transient actions from enduring preferences. Consequently, these models exhibit two major limitations: (i) lack of transparency regarding preference attribution, which impairs interpretability, and (ii) oversimplification of the multifaceted motivations that guide user behavior, especially in scenarios requiring temporal or situational adaptation. As a result, these implicit modeling frameworks fail to capture the causal relationships between dynamic user states and subsequent decision-making processes. Finally, most traditional RSs operate in a largely static, one-directional manner, providing users with minimal opportunities to iteratively refine suggestions through natural language or real-time feedback. This unidirectional flow diverges from established human-computer interaction principles, which emphasize interactive, adaptive dialogue to uncover user preferences. Although conversational RSs have begun to address this issue, they remain limited in their ability to integrate openended natural language understanding with personalized ranking, particularly in scenarios that require multiple rounds of clarification to resolve ambiguous user queries.

Recent advances in Large Language Models (LLMs) and Multimodal LLMs (MLLMs) have greatly improved language comprehension and cognitive processing [24, 39]. With stronger reasoning and planning abilities, (M)LLM-based agents can interpret human language, devise strategies, and execute complex tasks. These breakthroughs ofer new avenues for enhancing RSs’ adaptability, personalization, and user-centricity. The rapid surge in LLM-driven RS research is evident from the 290 references cited in a recent survey on this topic [17, 31, 32], along with numerous influential papers in the field (e.g., [44]). The existing work on applying LLMs to RS, however, has mostly focused on applying LLMs to improve the current RSs. Furthermore, the existing works have underexplored the important question of how LLMs or LLM agents would impact the future of RS in the long run. We argue that LLM-based Agentic Recommender Systems (LLM-ARS) present a promising research direction, ofering new perspectives on autonomy, adaptability, and interactive decision-making in rec ommendation. To unlock the full potential of LLM-ARS, it is crucial to address several open questions, including how to harness agentic capabilities (e.g., planning, collaboration, roleplaying) to improve user modeling and system decision-making, and how to balance autonomy with controllability to ensure safe, transparent interac tions. We ofer a more detailed discussion of these challenges and key research questions in Section 5, where we highlight the most pressing issues and outline possible solutions.

We present the first perspective paper on ARS powered by (M)LLMs. We begin with preliminaries and background on this emerging direction (§2), followed by a discussion on the significance of LLM-ARS (§3) and a formal problem formulation (§4). Next, we analyze LLM-ARS from an agentic perspective (§5) and introduce key research questions from the RS standpoint (§6). To address these questions, we provide in-depth comparisons and discussions, ofering insights into the field (§7 and §8). Finally, we highlight open problems and future opportunities that require further exploration (§9). In summary, our key contributions in this perspective paper are as follows:

• We position LLM-ARS within the broader trajectory of RS development by introducing a four-level evolution, emphasizing the shift from static, one-way recommendation toward agentic paradigms that support autonomy and interactive decisionmaking.

• We propose a formal task formulation for LLM-ARS, detailing the core components—user profiling, planning, memory, and action—that together enable continuous adaptation and proactive recommendations.

• We identify critical research questions and open problems of how to harness agentic capabilities (e.g., planning, roleplaying, collab oration) to improve user modeling, system decision-making, and overall recommendation efectiveness.

[已省略: 2 preliminary and background]

## 6.2 LLM-Agent Roleplaying in User Modeling

The exploration of LLM-agent roleplaying techniques is demanding for realistic user modelling in recommender systems, where user agents or simulators emulate human-like behaviours to capture both explicit and implicit user preferences. Intuitively, these methods leverage roleplay to bridge the gap between language understanding and behaviour simulation, enabling more realistic multi-agent interactions for personalized preference alignment and more rigorous evaluation. One prominent challenge is simulating socially dynamic user-item interactions inherent in human behaviour. Zhang et al. [89] tackles this by simulating a collaborative learning environment where both users and items are modelled as autonomous roleplaying agents, thus enabling bidirectional interaction and reflective adjustment. In addition, Wang et al. [62] introduces a sandbox environment where roleplaying agents are equipped with profile, memory, and action modules that interact through one-to-one and broadcast communications, efectively modelling social influence and conformity. In contrast, Zhang et al. [94] emphasizes explicit user modelling by integrating logical reasoning with statistical insights to simulate user engagement.

Addressing the need for controllability and scalability in conversational settings, Zhu et al. [99] proposes a framework that utilizes roleplay to customize user simulations in real time, enhancing the fidelity of user modelling in conversational recommender systems. Additionally, to overcome limitations related to data scarcity and evaluation reliability, [5] and [10] construct synthetic environments using LLMs as roleplaying users, while [26] introduces a target-free roleplay strategy to avoid bias in preference elicitation. However, current LLM-agent roleplaying approaches in user modelling still struggle with the interpretability of simulation processes and capturing the complexity of human decision-making. Future research should focus on developing more interpretable roleplay strategies and integrating richer, multimodal behavioural data to further en hance the adaptability and realism of user modeling frameworks.

## 8 Framework and Learning Paradigms (RQ3)

To enable LLM-ARS, novel frameworks and learning paradigms are required to enhance autonomy, adaptability, and human alignment (RQ3). We categorize these advancements into three key areas: single-agent architectures, which focus on individual agents as decision-makers; multi-agent collaboration, which leverages interactions among multiple agents to improve reasoning and adaptability; and human-LLM hybrid architectures, which emphasize collaboration between human users and LLM-based agents to refine personalization, control, and interpretability in recommendations.

Single-Agent Framework for RS: LLM-powered single-agent frameworks enable autonomous decision-making in RSs by integrating reasoning, memory, and planning. The RAH framework [53] employs a Learn-Act-Critic loop to iteratively refine recommendations, improving personalization and reducing bias. Wang et al. [67] introduce Self-Inspiring Planning, where an LLM agent retrospectively analyzes past decisions to optimize future choices while leveraging external tools like search engines and summarization models. InteRecAgent [20] further enhances this paradigm by treating LLMs as decision-making cores, selectively invoking domain-specific tools (e.g., retrieval and ranking modules) and maintaining long-term candidate memory for adaptive ranking. These architectures transform LLMs from passive generators into adaptive decision-makers, enabling more context-aware, interactive recommendations. However, they face scalability challenges and lack collaborative reasoning in multi-domain scenarios.

Multi-Agent Framework for RS Multi-agent frameworks extend single-agent frameworks by incorporating specialized agents that communicate and collaborate to enhance decision-making. Instead of relying on a single agent for all tasks, these frameworks assign distinct roles to diferent agents, enabling parallelized reason ing, task specialization, and self-organizing interactions. Wang et al. [70] propose MACRec, where agents such as a Manager, Analyst, and Reflector collaborate on tasks like rating prediction, sequential recommendation, and explanation generation, improving adaptability and interpretability. PUMA [1] further integrates a shared memory system, allowing agents to retrieve past interactions for enhanced personalization. Compared to single-agent models, multiagent frameworks ofer better scalability, modularity, and reasoning eficiency, yet face challenges in coordination, redundancy reduction, and consistency maintenance across interacting agents.

Human-LLM Hybrid Framework for RS: While LLM-powered agents enhance automation, human-in-the-loop architectures are crucial for improving interpretability and fairness in RSs. Recent works explore collaborative frameworks where user feedback guides LLM-driven reasoning, ensuring transparency and control. Shu et al. [55] propose the LLM-powered assistant mediates between users and RSs. Using a Learn-Act-Critic loop with built-in reflection, the assistant refines recommendations by resolving preference in consistencies. It also incorporates privacy-preserving mechanisms, allowing users to filter content and adjust recommendations dy namically. Beyond direct interaction, hybrid frameworks embed user intent into LLM-based reasoning. Ning et al. [38] integrate user embeddings with LLMs via a pretrained encoder and crossattention, capturing long-term preferences more efectively. Shao et al. [50] further bridge the semantic gap between LLM reasoning and structured user data through vector quantization and prefer ence alignment. To formalize design principles for human-centered agentic RSs, Deng et al. [7] introduce a taxonomy spanning Intel ligence, Adaptivity, and Civility, providing guidelines to develop ethically adaptive, user-aligned conversational recommenders.

In summary, single-agent systems enable autonomous reasoning and memory integration, while multi-agent architectures enhance collaboration and modularity. Human-LLM hybrids further improve interpretability and personalization. Key challenges include balanc ing autonomy with user control, optimizing coordination, and miti gating biases while ensuring generalization. Future research should develop adaptive architectures that unify reasoning, collaboration, and user alignment for fully interactive, context-aware systems.

## 10 Conclusion

This perspective paper first examines the integration of LLMs into agentic RSs, highlighting their role in enabling dynamic, adaptive, and multimodal interactions. We categorize recent advancements into single-agent, multi-agent, and human-LLM hybrid architectures, analyzing their impact on personalization, transparency, and reasoning. Despite these advancements, challenges such as eficiency, hallucination, safety, and lifelong learning remain critical. To address these, we outline future directions, including scalable architectures, robust evaluation frameworks, and improved domain generalization. As agentic RSs evolve, ensuring a balance between autonomy and controllability will be essential for building trustworthy, context-aware, and ethically aligned recommender systems.

[已省略: references]


---

## 📑 关键章节 | Meta-Modal Agent: Sequential Evidence Routing for Missing-Modality Candidate Reranking

**arXiv ID**: [2605.25007](https://arxiv.org/abs/2605.25007)

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

[已省略: 2 related work]

## 3 Methodology

We introduce the Meta-Modal Agent (MMA) as a modular candidate pool reranker for missing-modality recommendation. Throughout the paper, first-stage retrieval denotes the upstream step that recalls candidates from the item catalog, while reranking denotes MMA’s role: scoring only the provided candidate pool. The method has four parts: (i) a fixed episode interface that exposes a first-stage candidate pool rather than the full catalog, (ii) an evidence-routing agent that treats failed tool calls as observations, (iii) a candidatescoring output protocol that fuses MMA scores with first-stage retrieval scores, and (iv) balanced missingness-task training that exposes the policy to each missingness pattern. This section defines the technical contract used by all experiments.

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

## 5 Conclusion and Limitations

We introduced the Meta-Modal Agent, a candidate-pool reranking framework that reframes missing modalities in cold-start recom mendation from a static representation learning task to a sequential evidence-routing problem. MMA operates after first-stage retrieval: it scores a shared candidate pool and fuses agent scores with first stage retrieval scores, making HR and NDCG evaluation explicit. The evaluation separates the automated deployment setting from the interactive upper bound: MMA-Auto disables Ask\_User, while MMA-Interactive keeps clarification available only for diagnostic analysis. Across the automated evidence chain, MMA-Auto wins all 9 dataset–modality OOMA cells against the strongest static baseline, improves target-positive OOMA NDCG@10 by 4<sup>.</sup>0%, achieves a 12<sup>.</sup>7% mean per-dataset relative NDCG@10 gain in fixed-pool full-catalog reranking, improves over the RuleRouter-Fuse deterministic control from 0.1578 to 0.1711 average OOMA NDCG@10, and reaches <sup>?? <</sup> 0<sup>.</sup>05 on all three datasets with modest but positive efect sizes. MMA-Interactive adds a 4<sup>.</sup>1% upper-bound gain over MMA-Auto when clarification is available.

[已省略: appendix]


---

## 📑 关键章节 | Popcorn: A Configurable Benchmark for Visual Evidence in Multimodal Movie Recommendation

**arXiv ID**: [2606.09595](https://arxiv.org/abs/2606.09595)

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

## 4 Experiments and Discussion

We organize the discussion around three experimental questions: RQ1 asks how far a single thumbnail encoded by a VLM can go compared with multi-frame CNN evidence from trailers or full movies; RQ2 asks whether gains come from multimodal fusion or from LLM data augmentation, and how these choices afect beyond-accuracy metrics; and RQ3 asks how thumbnail VLM performance changes with a model-size/storage proxy.

RQ1: visual evidence. Table 2 shows that a single thumbnail encoded by modern VLMs can outperform the older MMTF-14K trailer-CNN visual baseline. SigLIP-base reaches nDCG@10=0.269 and Recall@10=0.262, corresponding to gains of 21.2% and 29.1%. The result should not be interpreted as thumbnails fully representing films: thumbnails cannot observe pacing, repeated shots, or narrative progression. Rather, they provide a strong catalog-scale semantic signal. On the aligned 274-title slice, trailers remain stronger than full movies in visual-only settings for VBPR, AMR, and VMF, which is plausible because trailers concentrate recommendation-salient highlights. After CCA fusion, the gap narrows for VBPR and reverses for AMR and VMF, showing that trailers and full movies are no interchangeable.

RQ2: fusion versus data augmentation. Fusion helps in some settings but is not a monotonic improvement. In Panel A, SigLIP-base visual-only is slightly stronger than CCA on nDCG@10 (0.269 vs. 0.268), while CCA increases coverage from 0.767 to 0.918 but lowers diversity from 0.766 to 0.749 and raises calibration bias from 2.901 to 3.125. PCA is weaker on accuracy (0.242 nDCG@10) despite retaining reasonable diversity. The aligned-video results show the same pattern: VBPR trailer CCA improves over visual-only from 0.433 to 0.444 nDCG@10, and AMR full-movie CCA improves over text-only from 0.378 to 0.434 nDCG@10and from 0.506 to 0.564 Recall@10. Beyond-accuracy values show the cost of this gain: for AMR full movies with OpenAI text and no augmentation, CCA reaches 0.434 nDCG@10 and 0.564 Recall@10, but diversity drops to 0.742, below visual-only 0.773 and text-only 0.763. Data augmentation is also model-dependent: VBPR benefits modestly from LLaMA augmentation in the fused full-movie row (0.436 vs. 0.431 nDCG@10 without augmentation), whereas AMR’s strongest CCA row uses OpenAI text without augmentation. Full grids are provided in the GitHub repository.<sup>5</sup>

RQ3: VLM cost versus performance. Figure 3 modernizes the attached bar plot by removing calibration and storage text while retaining recall, coverage, and diversity. SigLIP-base has the best accuracy and recall, but CLIP has the highest coverage (0.785), and DINOv2-base/large has the highest diversity (0.777/0.776). The color-coded tiers show that performance is not monotonic with the cost proxy: the medium SigLIP-base is strongest in accuracy, the small CLIP is strongest in coverage, and the large DINOv2-large is not the best overall. Backbone selection should therefore depend on the intended deployment objective rather than model size alone.

## 5 Conclusion and Limitations

We presented Popcorn, a configurable benchmark for visual evidence in multimodal movie recommendation. Popcorn separates thumbnails, trailers, and full movies while logging the backbone, fusion, augmentation, split, recommender, and evaluation settings needed for reproducible ablations. Results show that modern

VLM thumbnails improve over older CNN visual baselines, while trailer/full-movie evidence, fusion, and augmentation afect both accuracy and beyond-accuracy behavior.

The main limitations are scale, access, and ofline evaluation. Full movies are released as derived embeddings; the aligned full-movie subset is smaller than the thumbnail layer, and LLM augmentation remains sensitive to model and prompt choices. Future work will extend Popcorn with larger lawful-access full-movie collections, stronger temporal encoders, audio-centric ablations, Visual RAG integration, user studies, and online evaluation.

[已省略: references]


---

## 📑 关键章节 | Cold-Start Recommendation towards the Era of Large Language Models (LLMs): A Comprehensive Survey and Roadmap

**arXiv ID**: [2501.01945](https://arxiv.org/abs/2501.01945)

# Cold-Start Recommendation towards the Era of Large Language Models (LLMs): A Comprehensive Survey and Roadmap

WEIZHI ZHANG<sup>∗</sup>, University of Illinois Chicago, USA

YUANCHEN BEI<sup>∗</sup>, Zhejiang University, China

LIANGWEI YANG and HENRY PENG ZOU, University of Illinois Chicago, USA

PEILIN ZHOU, Hong Kong University of Science and Technology (Guangzhou), China

AIWEI LIU and YINGHUI LI, Tsinghua University, China

HAO CHEN, The Hong Kong Polytechnic University, China

JIANLING WANG, Google Deepmind, USA

YU WANG, Netflix, USA

FEIRAN HUANG, Jinan University, China

SHENG ZHOU and JIAJUN BU, Zhejiang University, China

ALLEN LIN and JAMES CAVERLEE, Texas A&M University, USA

FAKHRI KARRAY, Mohamed Bin Zayed University of Artificial Intelligence, UAE

IRWIN KING, The Chinese University of Hong Kong, China

PHILIP S. YU, University of Illinois Chicago, USA

Cold-start problem is one of the long-standing challenges in recommender systems, focusing on accurately modeling new or interaction-limited users or items to provide better recommendations. Due to the diversification of internet platforms and the exponential growth of users and items, the importance of cold-start recommendation (CSR) is becoming increasingly evident. At the same time, large language models (LLMs) have achieved tremendous success and possess strong capabilities in modeling user and item information, providing new potential for cold-start recommendations. However, the research community on CSR still lacks a comprehensive review and reflection in this field. Based on this, in this paper, we stand in the context of the era of large language models and provide a comprehensive review and discussion on the roadmap, related literature, and future directions of CSR. Specifically, we have conducted an exploration of the development path of how existing CSR utilizes information, from content features, graph relations, and domain information, to the world knowledge

<sup>∗</sup>Both authors contributed equally to this research.

Authors’ Contact Information: Weizhi Zhang, wzhan42@uic.edu, University of Illinois Chicago, USA; Yuanchen Bei, yuanchenbei@zju.edu.cn, Zhejiang University, China; Liangwei Yang, lyang84@uic.edu; Henry Peng Zou, pzou3@uic.edu, University of Illinois Chicago, USA; Peilin Zhou, pzhou460@connect.hkust-gz.edu.cn, Hong Kong University of Science and Technology (Guangzhou), China; Aiwei Liu, liuaw20@ mails.tsinghua.edu.cn; Yinghui Li, liyinghu20@mails.tsinghua.edu.cn, Tsinghua University, China; Hao Chen, sundaychenhao@gmail.com, The Hong Kong Polytechnic University, China; Jianling Wang, jianlingw@google.com, Google Deepmind, USA; Yu Wang, yuw@Netflix.com, Netflix, USA; Feiran Huang, huangfr@jnu.edu.cn, Jinan University, China; Sheng Zhou, zhousheng\_zju@zju.edu.cn; Jiajun Bu, bjj@zju.edu.cn, Zhejiang University, China; Allen Lin, al001@tamu.edu; James Caverlee, caverlee@tamu.edu, Texas A&M University, USA; Fakhri Karray, Fakhri.Karray@mbzuai.ac.ae, Mohamed Bin Zayed University of Artificial Intelligence, UAE; Irwin King, king@cse.cuhk.edu.hk, The Chinese University of Hong Kong, China; Philip S. Yu, psyu@uic.edu, University of Illinois Chicago, USA.

Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page. Copyrights for components of this work owned by others than the author(s) must be honored. Abstracting with credit is permitted. To copy otherwise, or republish, to post on servers or to redistribute to lists, requires prior specific permission and/or a fee. Request permissions from permissions@acm.org.

© 2025 Copyright held by the owner/author(s). Publication rights licensed to ACM. ACM 1557-735X/2025/1-ART1 https://doi.org/XXXXXXX.XXXXXXX

possessed by large language models, aiming to provide new insights for both the research and industrial communities on CSR. Related resources of cold-start recommendations are collected and continuously updated for the community in https://github.com/YuanchenBei/Awesome-Cold-Start-Recommendation.

CCS Concepts: • Information systems → Recommender systems; Language models; Collaborative filtering.

Additional Key Words and Phrases: cold-start problem, recommender system, large language model

[已省略: acm reference format:]

## 1 INTRODUCTION

In the rapidly evolving landscape of the digital information era, recommender systems (RecSys) have become indispensable tools for helping users discover relevant content and items amidst overwhelming information and choices [14, 220, 255]. Despite their widespread deployment, RecSys face persistent challenges, particularly in "cold-start" scenarios, where limited or no historical interaction data is available for new users or items. Specifically, in real-world scenarios, the cold-start problem could be the introduction of new items, the onboarding of new users, or new platforms with inherently sparse interaction data. Addressing the cold-start problem is not just technically necessary for performance metrics but also critical for advancing the efectiveness and sustainability of recommender systems. First and foremost, solving this issue ensures that new users and items are fairly represented, mitigating biases that arise from the reliance on historical data. This improvement fosters diversity and fairness in recommendations, promoting diverse content exposure by preventing new items from being overlooked [114, 288]. Furthermore, tackling the cold-start challenge brings the platform brand value and user retention. In a crowded and fast-moving digital landscape, delivering immediate and relevant recommendations to new users can diferentiate a platform from its competitors. Personalized recommendations from the outset help engage new users, preventing them from leaving due to irrelevant or absent suggestions. This creates a strong initial impression and fosters loyalty. For platforms, this translates into higher engagement, improved retention rates, and the ability to succeed in dynamic markets. Finally, efectively addressing cold-start scenarios ensures scalability and growth. As platforms expand with new users and content, efective integration of the continual influx of these entities keeps recommendation engines dynamic and relevant. This adaptability supports long-term sustainability in a rapidly changing environment. Given these motivations, the cold-start problem has driven the exploration of innovative approaches that leverage diverse external knowledge sources. By incorporating information beyond traditional user-item interactions [66, 204], such as content features [183], social information [36], or pretrained LLM knowledge [122], these methods enrich the representation and modeling of cold-start entities, enabling recommender systems to perform efectively even under sparse data conditions. As such, solving the cold-start problem is not merely a technical challenge—it is a strategic necessity for building fair, engaging, and sustainable recommendation platforms in an ever-changing digital landscape.

Early cold-start attempts adopt content-based approaches [133, 181] and focus on categorical textual features, such as item genres, item titles, and user profiles, which play a crucial role in representing cold entities. Then, with the advances of graph mining techniques [101, 225, 231], high-order relations derived from graph structures,

![](images/819ccef4ac94af9fbf2e338711e71267da6b08cbc13cdbf7691992eeaa132ca1.jpg)  
Fig. 1. Illustrations of the knowledge scope discussed in this survey.

J. ACM, Vol. 1, No. 1, Article 1. Publication date: January 2025.

such as user-item interaction graphs [24, 64, 257, 258], knowledge graphs [21, 203], and social networks [165, 239], become another critical component to enhance the CSR. Concurrently, instead of mining the graph relations among nodes, some researchers resort to the connections among diferent domains [92, 249]. In particular, cold-start and data sparsity issues in the target domain can be alleviated by transferring knowledge from other domains where richer interaction data is available. Cross-domain recommendation techniques exploit overlapping user bases, shared attributes, or aligned item categories to improve performance in CSR. In recent years, the rise of large language models (LLMs), such as GPT [3], LLaMa [39], and T5 [157] has revolutionized natural language processing, demonstrating exceptional capabilities in understanding and generating human-like text based on vast amounts of pre-trained data [107, 142]. These advancements have inspired a paradigm shift in recommender system research, leveraging the comprehensive contextual understanding of LLMs to enhance cold-start recommendation performance. By utilizing the pre-trained world knowledge of LLMs, researchers have started exploring novel strategies for modeling and representing cold users and items in a more semantically rich and context-aware manner. Figure 2a illustrates this evolving trend, highlighting the shift in cold-start recommendation research from traditional content-based methods to LLM-driven strategies with progressively expanding knowledge scope (Figure 1).

![](images/25752290c153891bff2210493c0683ee07afb857a34a41ebc808494c43ed6c95.jpg)  
(a) Number of publications in recent years.

![](images/55f40111580933f4cf5700965488d932eb166dde07ff40e0cb7dc42f88637199.jpg)  
(b) Venues of publications  
Fig. 2. Statistical information of current cold-start recommendation publications.

This survey paper aims to provide an extensive review of state-of-the-art techniques and frameworks in the cold-start recommendation, with a special outlook towards the era of LLMs with expanding knowledge scope as illustrated in Figure 1. Particular focuses are placed on works published in top-tier conferences and journals, as in Figure 2b. Based on the collection, we categorize the existing works into four knowledge scopes considering the scale of external knowledge sources: Content Features, Graph Relations, Domain Information, and World Knowledge from the Large Language Models. By systematically categorizing and analyzing these approaches, our survey aims to present a comprehensive understanding of the landscape and propose a roadmap for future research. We emphasize the transformative potential of integrating LLMs into cold-start recommendations and outline the opportunities and challenges that lie ahead in this burgeoning field.

[已省略: 1.1 related work]

## 1.2 Survey Methodology

To comprehensively cover the papers in the cold-start recommendation. We adopted a semi-systematic survey methodology to identify the relevant papers. Initially, we queried prominent academic databases such as Google Scholar and Web of Science with pre-defined searching keywords such as "cold-start recommendation", "coldstart recommender systems", "strict cold-start", "zero-shot recommendation", and "few-shot recommendation". Additionally, we screen specialized conference proceedings, including KDD, WWW, SIGIR, CIKM, WSDM, and RecSys. The search results were filtered by analyzing titles, abstracts, and experiments to evaluate relevance. Then, the relevant papers were further reviewed thoroughly, and their references were used as seeds for a snowballing approach to identify additional papers. The final collection comprised studies categorized into four core areas based on their contributions, as illustrated in the taxonomy diagram. These areas include content features, graph relations, domain information, and world knowledge from LLMs, as summarized in Figure 3. The majority of these works describe technical approaches or propose novel frameworks, with a smaller subset providing system demonstrations or analytical perspectives on cold-start recommendation methodologies.

[已省略: 2 preliminaries]

## 6 WORLD KNOWLEDGE FROM LARGE LANGUAGE MODELS

Large language models (LLMs) are generative artificial intelligence systems trained using deep learning techniques to understand the general world knowledge by learning vast amounts of textual corpus data. These models can generate text, answer questions, perform translations, and even engage in complex conversations [271, 287]. Due to the tremendous success achieved in recent years, an increasing number of fields have begun to leverage the capabilities of large language models for various tasks, such as multimodal learning [217], graph learning [159], and recommender systems [219], achieving commendable results. Due to the powerful textual feature processing capabilities of LLMs, cold start, especially the zero-shot and few-shot scenarios, has become an important application in the recommendation domain for LLMs. According to the role that LLMs play, we categorize existing works into two main aspects: LLM as the Recommender System (Sec. 6.1) and LLM as the Knowledge Enhancer (Sec. 6.2).

![](images/2300132741960380fa4d2b49a7c4345b833a4218c44465aeb7dd9d36ff9d2680.jpg)  
Fig. 7. Illustrations of diferent categories of methods for utilizing the world knowledge from LLMs.

## 7.2 Recommendation Foundation Models

The ongoing transformation within the field of Natural Language Processing (NLP) has been powered by the emergence of foundation models—comprehensive, pre-trained models that can be easily adapted to a variety of downstream tasks. These models, such as large language models (LLMs), have demonstrated remarkable capabilities in tasks ranging from text classification to dialogue generation, significantly reducing the need for task-specific training from scratch. Inspired by these developments, the recommendation domain now faces a similar opportunity: to leverage analogous “foundation models” for a wide range of cold-start tasks, thereby enhancing adaptability, eficiency, and scalability. As discussed in Section 6, existing research has shown that LLMs can efectively address the cold-start issue for single tasks or within single domains. However, these solutions often require continuous long-term re-adaptation when encountering new recommendation tasks or domains, leading to substantial time and computational overhead. Future research directions involve the design and implementation of these recommendation foundation models, as well as algorithms to quickly adapt large foundation models to diferent CSR subtasks. Such models would not only enable multi-task recommendation capabilities, as exemplified by P5 [48], but also dynamically adjust their recommendations across diverse domains.

## 7.5 Benchmark and Unified Evaluation

Research on cold start recommendation systems has made significant progress. However, evaluations for existing cold start recommendation systems are currently diverse and inconsistent. Thus, it would be promising and meaningful to develop a unified and fair evaluation benchmark for the community. Specifically, there are multiple problem settings for cold-start recommendations, such as strict cold-start, non-strict cold-start, and long-tail cold-start, and each setting needs to be evaluated fairly. This raises the following three main issues: (i) Diferent benchmark datasets. Diferent papers rarely overlap in the datasets they use, making it dificult for researchers to conduct unified comparisons across several related datasets. A promising approach for the future would be to encourage the community to focus on a selection of high-quality datasets for comparative experiments. Further, only part of the papers adopts datasets with real cold users/items in industrial platforms. We encourage the community to release these datasets for open research, which is very meaningful for the development of the community. (ii) Diferent evaluation settings. The key problem in this part is the setting of cold users/items. Specifically, how to define and synthesize cold users/items in the experiments? In the experiments of many cold-start works, cold users/items are often obtained by varied approaches (time range, number of interactions, and random selection) with vague definitions of CSR settings, and there is still a lack of unified rules. (iii) Open-source evaluation frameworks. There are some practical open-source projects for recommendation experiments, such as Recbole [269, 270], Elliot [5], and BARS [281]. However, all of them are designed for general recommendation evaluations. A unified open-source evaluation codebase for cold-start recommendations with fair evaluation settings and metrics will be very helpful for the research community.

## 8 CONCLUSION

In this paper, we provide a comprehensive review of cold-start recommendations, with a roadmap from con tent features, graph relations, and domain information, toward world knowledge from large language models. Specifically, we first formally define diferent research questions in the field of cold-start recommendations. Then, we systematically review cold-strat recommendations. In each part, we provide overall insights behind related works and list some representative works for readers to better understand. Furthermore, we rethink some of the challenges of cold-start recommendations and summarize some meaningful future directions. Related resources are organized in the Github (https://github.com/YuanchenBei/Awesome-Cold-Start-Recommendation) for the CSR research and industrial community.

[已省略: references]


---

## 📑 关键章节 | RapidPD: Rapid Human and Pet Presence Detection System for Smart Vehicles via Wi-Fi

**arXiv ID**: [2504.00678](https://arxiv.org/abs/2504.00678)

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

## V. CONCLUSION

By re-modeling CSI with theoretical analysis of path propagation, this study introduces a novel approach to presence detection leveraging the subcarrier dimensions of the CSI matrix, providing a more precise motion statistics analysis and significantly enhancing detection capabilities. The proposed method based on multilayer autocorrelation provides a significant indicator for distinguishing the presence or absence of invehicle organisms. Extensive experiments validate the effectiveness of RapidPD, demonstrating an accuracy exceeding 99.05% and a true positive rate greater than 99.32% using only 1-second time windows at a lowlevel sampling rate of 20 Hz. This marks the first time subcarrier dimension information from the CSI matrix has been utilized for such sensitive detection, offering a groundbreaking contribution to in-vehicle safety and opening up new possibilities for the global adoption of advanced presence detection systems.

[已省略: acknowledgment]


---

## 📑 关键章节 | Probability of Transition to Turbulence in a Reduced Stochastic Model of Pipe Flow

**arXiv ID**: [2503.00987](https://arxiv.org/abs/2503.00987)

# Probability of Transition to Turbulence in a Reduced Stochastic Model of Pipe Flow

P. Bernuzzi<sup>1,†</sup> and C. Kuehn<sup>1,2</sup>

<sup>1</sup>Technical University of Munich, School of Computation Information and Technology, Department of Mathematics, Boltzmannstraße 3, 85748 Garching, Germany

<sup>2</sup>Technical University of Munich, Munich Data Science Institute, Walther-von-Dyck-Straße 10, 85748 Garching, Germany <sup>†</sup>Author to whom any correspondence should be addressed.

Email addresses: paolo.bernuzzi@ma.tum.de (P. Bernuzzi), ckuehn@ma.tum.de (C. Kuehn).

March 4, 2025

## 1 Introduction

The flow of a fluid is known to display diferent behaviour depending on the assumptions on the fluid and the shape of the geometry traversed. We focus on plane Couette flow, or flow along a pipe, and the transition to turbulence starting from an initially laminar state [18]. Recently, this area has been connected to directed percolation, a classical area of probability theory. It is known that the transition to turbulence crucially depends upon the Reynolds number, i.e., on the ratio between inertial and viscous forces in a fluid. From a mathematical perspective, studying the transition to turbulence directly in the Euler or Navier-Stokes equations turns out to be extremely dificult. Yet, quite recently, other simplified models have been proposed and directly validated against experiments.

The first model proposed in [1, 2] is defined by two coupled stochastic partial diferential equations (SPDEs) with second-order dissipation, an advection term, and multiplicative degenerate Itô noise [25]. The solution of this system may display structures labeled as slugs for high Reynolds numbers, and the turbulent state covers the whole pipe in finite time with a high probability. Conversely, for low values of the corresponding parameter, the turbulent regions are absorbed in the laminar state in finite time with high probability. Lastly, traveling structures labeled as pufs indicate a fluctuating transition for intermediate values. In such cases, metastable transitions between turbulent and laminar states are observed in the pipe. The study of the rise and the splitting of pufs is relevant to describe the transition to turbulence as a rare event [14]. The steps involved in such an occurrence can be described through the computation of instantons, most likely paths to display rare occurrences [5, 19, 32].

The complex structure provided by the model discussed above is not observed for all fluids and is in contrast with the perspective of [26, 27]. In this case, the turbulent state is seen as a fluctuating state able to decay spontaneously. Conversely, the laminar state is an absorbing state, which is unable to induce turbulence into the system. The alternative model proposed in [13] is a one-dimensional SPDE that does not display advection. Furthermore, this simplified model does not show well-defined traveling states such as pufs and slugs. For this reason, the flow is labeled band-free. In particular, the transition to turbulence is primarily driven by noise and occurs more rarely than in the previously discussed cases. The transition mechanism can be studied numerically through the adjoint state method [5], which captures the instanton for various types of noise. Alternatively, the Trajectory-Adaptive Multilevel Sampling algorithm (TAMS) [19, 32] computes diferent trajectories that display such an event. Along with the description of such an occurrence, the analytic estimation of the probability of jumps provides a valuable tool to predict the likelihood of this phenomenon.

The metastable jump to turbulence is rare under the assumption of initial conditions close to the laminar state. Under such conditions, we label this transition as turbulence initiation, or turbulence onset, to indicate that it is primarily induced by noise. Therefore, the linearization of the model near such a steady state is a natural simplification. The linearized system resembles the cable equation [31], or a heat equation with a second linear dissipative term, with multiplicative noise. The literature regarding such a model is vast. These types of SPDEs have been studied in a theoretical context to understand the influence of noise on potential finite-time blow-up of the solution. In particular, for standard white noise multiplied by a multiplicative term of order $\gamma > \frac { 3 } { 2 }$ the mild solution is proven to diverge to infinity in finite time [23, 24]. Conversely, for a multiplicative term of order $\begin{array} { r } { 0 \leq \dot { \gamma } \leq \frac { 3 } { 2 } } \end{array}$ the mild solution of the linear system does not explode in finite time [22, 28]. Although the band-free plane Couette flow model considers noise of order $\gamma = 1$ , we show in this paper that analytic techniques employed in the proof of blow-up of the mild solution, in [23], can be applied to our case of interest to describe turbulence initiation under Itô white Gaussian noise.

In [2], diferent types of noise are admitted to perturb the system, although only Itô noise is addressed to simplify numerical simulations. In this work, we study the onset of turbulence for various Gaussian noise terms. For instance, Stratonovich noise is a natural alternative to Itô noise in physical applications and fluid dynamics, particularly due to the chain rule property [11, 16]. The computation of higher bounds for the probability of metastable transitions has already been achieved for cable equations under the assumption of additive Itô noise [4, 6]. Under such assumptions, the solution to the problem displays a qualitatively diferent behaviour from the multiplicative noise case: first, its sign can change in contrast to the cable equation with multiplicative noise; furthermore, the laminar state is not an absorbing state, which is a fundamental property of the original system. Nevertheless, the Cole-Hopf transformation reveals structural parallels between the systems. In fact, the study of the strong solution of the original system under Stratonovich noise on a logarithmic scale, in the form of the KPZ equation, displays an additive noise term [3, 8, 15]. Standard techniques enable the construction of a lower bound to the probability of transition to turbulence in specific domain regions. This method is then extended to the case of red noise in order to introduce memory in the noise component. We discuss two diferent interpretations of red (Stratonovich) noise, which are known to find applications in climate science [21, 17].

In conclusion, our methods prove the possibility of transition to turbulent states under diferent types of noise assumptions in simplified fluid dynamics models that have been suggested in applications. These results are implied by the stochastic perturbations in the system despite the non-trivial nature of the noise involved. Furthermore, they advance the analytic study of SPDEs, particularly with (multiplicative) Stratonovich noise.

The paper is structured as follows. In Section 2, we introduce our main mathematical tools. Moreover, we justify the linearization of the system as a method to study the solutions in the proximity to the laminar state and to obtain a lower bound to the probability of the transition to turbulence. We construct the fundamental solution of the cable equation and discuss its properties. In Section 3, we consider perturbations enforced by Itô noise. We study the mild solution of the linearized model on the laminar state. By applying a suitable operator to counter the efect of the drift component, we obtain an observable in the form of a martingale. Through the use of similar techniques employed as in [23], we obtain the bound to the transition to turbulence. In Section 4, we consider the noise term in the Stratonovich interpretation. We assume first space-time white noise and then red noise in time. A lower bound to the local and global transition to turbulence is proven by studying its strong solution on a logarithmic scale through the Cole-Hopf transformation [15]. The methods are also shown to be extendable to the case of space heterogeneity in the system [6]. In Section 5, we compare the stated methods and discuss the diferences with already existing approaches.

[已省略: 2 preliminaries and linearization]

## 5 Comparison of methods

In the previous sections, we have studied lower bounds to the probability of turbulence onset in system (2.1) under diferent noise assumptions. Namely, we considered time-white noise in Itô sense, in Section 3, and time-white or time-red noise in Stratonovich sense, in Section 4. Throughout the paper, the noise is assumed to be white in space along fixed modes. The techniques employed in the two sections difer in nature yet manage to capture similar characteristics of the system.

We first discuss the rise of turbulence under Itô noise. Lemma 3.1 and Lemma 3.2 were based on methods introduced in [23, 24]. The key idea is to counter the drift efect on the solution of (2.3) by applying a convolution operator through the fundamental solution of the cable equation, reserved in time. A stark diference with the assumptions in [23, 24] is that their work studies the heat equation, $\mathrm { i . e . , } \alpha = 0$ . In fact, under strong linear drift dissipation, the left-hand side term in (3.11) can be negative, even for large values of $T ,$ thus rendering the inequality trivial. This is in contrast with [23], where the lower bound increases with T . In [23, 24], a second lower bound is obtained and employed to prove the blow-up of the mild solution in finite time through an iterative method. The iteration step is based on rescaling the space interval. Once again, the method is not equivalent under the assumption $\alpha > 0$ as the second rescaling afects the linear dissipation and does not return the initial system, thus afecting the iteration at each step (see [23, Lemma 2.6, Proposition 3.2, Section 4]).

We note that the lower bounds in Corollary 3.3 are also valid for q mild solution of (2.1) under white Stratonovich noise. In fact, we set $u _ { 1 } ^ { \mathrm { S } } = u _ { 1 } ^ { \mathrm { S } } ( x , t )$ the mild solution of (2.3) for $\hat { \sigma } = \sigma _ { \mathrm { S } } > \sigma _ { \mathrm { I } } = \sigma _ { \mathrm { R } } = 0$ and $u _ { 1 } ^ { \mathrm { I } } = u _ { 1 } ^ { \mathrm { I } } ( x , t )$ the mild solution of (2.3) for $\hat { \sigma } = \sigma _ { \mathrm { I } } > \sigma _ { \mathrm { S } } = \sigma _ { \mathrm { R } } = 0$ . We then study $\hat { u } = u _ { 1 } ^ { \mathrm { S } } - \dot { u } _ { 1 } ^ { \mathrm { I } }$ . By assuming $Q$ to be trace-class and by the definition of the Itô-Stratonovich correction term in [3, 12], it is the mild solution of

$$
\left\{ \begin{array}{l} \mathrm{d} \hat {u} (x, t) = \left(\partial_ {x x} ^ {2} \hat {u} (x, t) - \hat {u} (x, t) + u ^ {\mathrm{I}} (x, t) \frac {\hat {\sigma} ^ {2}}{2} \sum_ {i = 0} ^ {\infty} \zeta_ {i} b _ {i} (x) ^ {2}\right) \mathrm{d} t + \hat {\sigma} \hat {u} (x, t) Q ^ {\frac {1}{2}} \mathrm{d} W _ {t}, \\ \partial_ {x} \hat {u} (0, t) = \partial_ {x} \hat {u} (L, t) = 0, \\ \hat {u} (x, 0) \equiv 0. \end{array} \right.
$$

Following the steps in the proof of Lemma 2.1, it is implied that $u _ { 1 } ^ { \mathrm { S } } \geq u _ { 1 } ^ { \mathrm { I } }$ almost surely. Moreover, we know that $v _ { J } ^ { \mathrm { S } } \leq v _ { J } ^ { \mathrm { I } }$ holds. The methods in Section 3 are applied to the mild solutions of the considered stochastic partial diferential equations. Conversely, although in Section 4 the noise is assumed in Stratonovich sense, the use of Itô’s Lemma through the inverse Cole-Hopf transformation requires the study of strong solutions. In order to satisfy the existence of such a solution, the noise is assumed to perturb the system along a finite number of modes, then afected by the multiplication term in the noise intensity [10, Section 6.5, Chapter 7]. Similar results to those in Section 4 can also be proven in an equivalent manner under Itô noise assumptions, yet, on a logarithmic scale, an additional negative term appears in the KPZ equation [15]. For instance, under the assumption of white noise, the system obtained in correspondence to (4.2) is

$$
\left\{ \begin{array}{l} \mathrm{d} v _ {g} ^ {\mathrm{I}} (x, t) = \left(\partial_ {x x} ^ {2} v _ {g} ^ {\mathrm{I}} (x, t) + \left(\partial_ {x} v _ {g} ^ {\mathrm{I}} (x, t)\right) ^ {2} - g (x) - \frac {\sigma_ {\mathrm{I}} ^ {2}}{2} \sum_ {i = 0} ^ {m} \zeta_ {i} b _ {i} (x) ^ {2}\right) \mathrm{d} t + \sigma_ {\mathrm{I}} Q ^ {\frac {1}{2}} \mathrm{d} W _ {t}, \\ \partial_ {x} v _ {g} ^ {\mathrm{I}} (0, t) = \partial_ {x} v _ {g} ^ {\mathrm{I}} (L, t) = 0, \\ v _ {g} ^ {\mathrm{I}} (x, 0) = \log \left(q _ {0} (x)\right). \end{array} \right.
$$

Then, the step in Lemma 4.2 implies the discard of the nonlinear shear deformation non-negative term, but not of the term $\begin{array} { r } { - \frac { \sigma _ { \mathrm { I } } ^ { 2 } } { 2 } \sum _ { i = 0 } ^ { m } \zeta _ { i } b _ { i } ( x ) ^ { 2 } } \end{array}$ , which has to be included in the moving average of Theorem 4.4, Corollary 4.5 and Corollary 4.6.

Although the lower bounds in Section 4 are always positive, they are characterized by severely diferent behaviours in time. The section contains results that manage to study the initiation of turbulence in certain regions of the domain in Corollary 4.5 and Corollary 4.8. Nevertheless, we focus on the description of jumps in the $L ^ { \infty } ( [ 0 , L ] )$ -norm, which are easier to observe. In Corollary 4.6, the sum of two terms in the argument of the function Φ defines the nature of the bound. In fact, the term $t ^ { - { \frac { 1 } { 2 } } }$ , multiplied by a positive parameter dependent on initial conditions, refers to the efect of the noise to enable the possibility of a jump, thus decreasing with t the argument in the distribution function. Conversely, the term $t ^ { \frac { 1 } { 2 } }$ takes into account the efect of the drift component, constant in time, which hinders the transition on long times. The clash of these efects implies that at

$$
t ^ {*} = \log (J) - L ^ {- 1} \int_ {0} ^ {L} \log (q _ {0} (x)) \mathrm{d} x
$$

the lower bound to the probability of jump at height J in the $L ^ { 1 } ( [ 0 , L ] )$ -norm reaches its peak, which is maintained for longer times for the statement in the proof of Corollary 3.3. A similar behaviour is observed in Corollary 3.3, where the best opportunity of occurrence of jump is captured.

We considered in Subsection 4.2 red noise in time. We note that, in previous cases, the initiation of turbulence is not a memoryless process since it is already afected by its initial state. The inclusion of red noise in the sense (4.8) is justified by its relevance in climate application [20, 21] and the positive autocorrelation of the system in logarithmic scale along the direction e . The inequality (4.15) in Corollary 4.8 (b) resembles the statement in Corollary 4.6, but the parameter κ assumes a twofold role: it is proportional to the term

$$
\frac {L ^ {\frac {1}{2}} \kappa}{\sigma_ {\mathrm{R}} \sigma_ {\xi} p _ {0 , 0} ^ {\frac {1}{2}}}\tag{5.1}
$$

and appears in the term

$$
\frac {t ^ {\frac {1}{2}}}{(t - 2 \frac {1 - \mathrm{e} ^ {- t \kappa}}{\kappa} + \frac {1 - \mathrm{e} ^ {- 2 t \kappa}}{2 \kappa}) ^ {\frac {1}{2}}} = \left(\frac {t}{\int_ {0} ^ {t} (1 - \mathrm{e} ^ {- s \kappa}) ^ {2} \mathrm{d} s}\right) ^ {\frac {1}{2}} > 1,\tag{5.2}
$$

due to its dissipative role in (4.6). Both perspectives indicate that $\kappa > 0$ hinders the jump with respect to the white noise assumption, but their efects difer. In fact, increasing κ leads to an increase in (5.1) and a decrease in (5.2). Still, the concept of a best opportunity to jump before being fully controlled by the drift is visible since, for fixed $\kappa > 0 .$ , the limit of (5.2) in $t \to + \infty$ is finite. Nevertheless, the limit of (5.2) in $t  0$ is infinite, indicating a smaller probability of jump on short times in comparison to white noise in time. Lastly, we notice that the limit $\kappa = 0$ implies $\begin{array} { r } { \gamma _ { 0 , 0 } = \sigma _ { \mathrm { R } } ^ { 2 } \sigma _ { \xi } ^ { 2 } p _ { 0 , 0 } \frac { t ^ { 3 } } { 3 } } \end{array}$ , which means that the lower bound is a definitely strictly increasing function in t.

At the end of Subsection 4.2, we consider an alternative type of red noise, as discussed in [17]. The role of κ is diferent from the previous case. In fact, κ indicates both the dissipativity in (4.6) and is related to the of-diagonal entry in the linear drift term

(see Appendix B). The term in (4.18),

$$
\frac {t ^ {\frac {1}{2}}}{\left(\frac {1 - \mathrm{e} ^ {- 2 t \kappa}}{2 \kappa}\right) ^ {\frac {1}{2}}} = \left(\frac {t}{\int_ {0} ^ {t} \mathrm{e} ^ {- 2 s \kappa} \mathrm{d} s}\right) ^ {\frac {1}{2}}\tag{5.3}
$$

is finite in $t  0$ and infinite in $t \to + \infty$ . This translates to a similar behaviour to the lower bound with the assumption of white noise in Corollary 4.5 on small time scales and a smaller lower bound to the probability of jump on large time scales t. This results from the interplay between the dissipativity in the Ornstein-Uhlenbeck process defined in (4.6) and the dissipativity in (4.1). In this case, increasing $\kappa > 0$ indicates in (5.3) the decrease in the bound of jump at a fixed time. The limit $\kappa = 0$ is equivalent to the time-white noise assumption in Subsection 4.1.

## Conclusion

In this paper, we have established lower bounds for the probability of turbulence initiation in a simplified model of plane Couette flow. The phenomenon is modeled through an SPDE on an interval under various forms of multiplicative Gaussian noise. The simulation of similar systems leads to the study of other rare events in the pipe flow [13, 14]. The application of equivalent algorithms shows the possibility of such an occurrence, whose probability has not been estimated analytically so far. Central to our approach is the comparison between the linearized and original models, starting with a rigorous treatment of Itô white noise. Using the fundamental solution of the cable equation under Neumann or periodic boundary conditions, we counter the drift term and obtain an observable in the form of a martingale. The bound is then described following techniques employed in the study of finite-time blow-up of the mild solution of the stochastic heat equation [23, 24].

Expanding this framework, we employ logarithmic-scale comparison methods to address systems perturbed by time-white Stratonovich noise, time-red additive noise, and time-red Stratonovich noise, with the latter two modeled through coupling with Ornstein–Uhlenbeck processes. This approach requires diferent assumptions on the noise term to ensure the existence of a strong solution for the model. Our analysis reveals that, whereas the lower bounds vary across noise types, they consistently reflect a key dynamical feature: the probability of turbulence onset in a fixed time declines beyond an optimal jumping time. This property is implied by the invariance of the linearized model under a suitable rescaling of the solution.

Finally, we illustrate the adaptability of our techniques to other types of noise, highlighting their potential for broader applicability in turbulence modeling. These findings provide a deeper understanding of stochastic influences on turbulence initiation and ofer ground for future investigations into noise-driven dynamics in SPDEs perturbed by multiplicative Gaussian noise.

[已省略: acknowledgments]


---

## 📑 关键章节 | Massive Memorization with Hundreds of Trillions of Parameters for Sequential Transducer Generative Recommenders

**arXiv ID**: [2510.22049](https://arxiv.org/abs/2510.22049)

## 1 Introduction

Personalized recommendation systems are now integral to digital platforms like streaming services, e-commerce, and social media, where they boost user engagement and drive key metrics such as click-through rates (CTR), session duration, and retention. The success of these systems hinges on their ability to accurately predict user preferences by processing and interpreting vast user histories.

While traditional recommendation models, such as collaborative filtering (Sarwar et al., 2001) and matrix factorization (Koren et al., 2009), laid the groundwork for personalized recommendation, they often struggle to scale and capture long-term user behaviors. Deep learning introduced more powerful solutions, and the recent integration of large language models (LLMs) and sequential modeling techniques such as transformers (Section 2) has marked a significant leap forward, enabling the capture of intricate interactions across vast user histories.

![](images/1815a572b7ff148e74615bc6b4656ddc8fd3252560fe940f033803b33ae80c87.jpg)  
Figure 1: VISTA replaces standard attention with a two-stage process, allowing downstream models to compute only the highly eficient second stage.

In the domain of recommendation systems, two primary types of sequence modeling techniques have been explored: full user sequence modeling, as seen in Hierarchical Sequential Transduction Units (HSTU) (Zhai et al., 2024), and target-specific sequence sampling, as seen in Search-based Interest Modeling (SIM) (Pi et al., 2020) and its subsequent works (Chang et al., 2023; Si et al., 2024). Both approaches have demonstrated success in enhancing recommendation system performance by harnessing users’ extensive historical interactions.

Despite their success, full sequence modeling sufers from the computational cost of scaling. Modeling full user interaction sequences which are usually on the scale of O(100K) in length often leads to enormous computational costs and latency issues, which are very challenging for industrial recommendation systems that need to train O(10B) to O(100B) examples per day and have strict latency upper limits during inference. As a result, the full sequence modeling methods such as HSTU (Zhai et al., 2024) are hindered by high computational costs, limiting its widespread adoption across industries where many companies are still short of GPU capacities.

The second approach, target-specific sequence sampling, has been extensively explored through a series of seminal works, including SIM (Pi et al., 2020), TWIN (Chang et al., 2023), and TWIN V2 (Si et al., 2024). These studies have demonstrated the efectiveness of leveraging user historical interaction sequences. However, subsequent research in this direction has encountered two significant challenges: (1) bridging the gap between attention to the target-specific shortened sequence and the full user sequence, which, however, was partially addressed in follow-up work TWIN (Chang et al., 2023); and (2) the computational cost increases linearly with the number of candidates to predict at inference time, due to the independent target-specific sequences. These two challenges remain largely unresolved, primarily due to the inherent design limitations of SIM-style models.

Addressing the challenges of scalability in recommendation systems will assist with their widespread adoption. In this paper, we propose a novel two-stage modeling framework, VIrtual Sequential Target Attention (VISTA), designed to overcome the scalability challenges. The first stage compresses the ultra-long user interaction history into a few hundred of summarization embeddings (see Fig. 1); the second stage serves as eficient candidate aware target attention mechanism that leverages the summarization from the first stage for final prediction. The first stage occurs only during foundational model training, where the resulting summarization embeddings are cached to conceptually represent user embeddings. Consequently, downstream model training and inference only need to perform the second stage: computing attention between a candidate item and these cached embeddings, instead of processing the full user interaction history. This approach significantly reduces the computational complexity for downstream models, especially during inference, at the cost of additional storage. In practice, this is a worthwhile trade-of, as the cost of GPU computation remains multiple orders of magnitude higher than the cost of storage.

As a summary of our contributions, to the best of our knowledge we are the first to propose:

• A two-stage attention framework to decouple foundational model training and downstream model training and inference, which enables us to leverage ultra-long user histories for better recommendation model performance in industrial-scale systems,

• A quasi-linear attention formulation tailored for recommendation models,

• A generative sequential reconstruction loss in recommendation models, and

• A practical embedding delivery system successfully deployed in an industrial-scale platform.

![](images/1636ebf543d2f498d3fdb81a01f2e79a644494fb2ac4d65a1f23e2b85ef1dcce.jpg)  
Figure 2: An overview of VISTA architecture.

[已省略: 2 related work]

## 3 Method

Here we introduce the details of VISTA’s two cascaded modules: ultra-long user interaction history (UIH) sequence summarization and target-aware attention, followed by details of a practical linear complexity self-attention and generative sequence reconstruction loss. We then explain how VISTA’s design enables the scaling, storage, and processing of industry-scale user history sequences through its embedding delivery system.

## 3.1 Model Architecture Overview

As illustrated in Figure 2, the VISTA architecture employs distinct workflows for training and inference. During training, the computationally expensive UIH summarization module runs to generate summary embeddings. These embeddings are then quantized and exported to a large key-value cache in O(100) terabytes to $O ( 1 )$ petabytes. For inference, this expensive step is bypassed entirely. Instead, the pre-computed embeddings are simply retrieved from the cache and dequantized with minimal distortion. The final component, the target attention module, operates in both phases, using the summarization embeddings and candidate item features to make predictions.

## 5 Experiments

## 5.1 Datasets and Experimental Setup

The proposed VISTA framework is designed for a large scale real-world dataset, where one needs to train hundreds of billions of examples per day and each user has a history which contains hundreds of thousands of items. While existing public datasets are usually much smaller, we compare our method against several baselines on public datasets in addition to reporting results on real production data.

## 5.1.2 Baselines and Evaluation Metrics

All models share a common feature embedding layer and MLP block, with consistent hyperparameters, e.g., embedding dimensions, layers, attention heads, for fair comparison. We briefly describe them: (1) Deep Interest Network (DIN) (Zhou et al., 2018) uses attention to adaptively weigh user historical behaviors, (2) Two-Tower Sparse Network (TTSN) (Covington et al., 2016) separately encodes user and item features via two towers, (3) the standard Multi-Head Attention (MHA) (Vaswani et al., 2017), (4) SASRec (Kang and McAuley, 2018) is self-attentive sequential recommendation model that uses the Transformer architecture, and (5) Hierarchical Sequential Transduction Units (HSTU) (Zhai et al., 2024) is an industry proposed transformer-like model designed to capture multi-scale sequential patterns in user behavior sequence.

We use normalized entropy (NE) (He et al., 2014) as our evaluation metric, which calculates the cross entropy between the predicted probabilities and the labels, then normalizes it by the entropy of the constant predictor at label average. We also report the area under curve (AUC) for the traditional setting. Additional details about this section are in Appendix D.

## 5.2 Offline Experimental Results

## 5.2.1 Public Dataset Results

In Table 2, we summarize the comparative results between VISTA and the baseline models. For the Amazon-Electronics dataset, VISTA outperforms the other baselines with the use of quasi-linear attention being the next best model. On the KuaiRand dataset, VISTA slightly outperforms the other models with similar NE to HSTU and MHA. This may suggest that even at smaller sequence lengths, the virtual seeding embeddings slightly help the model performance. On much longer sequences in Minimal Production, we see that HSTU and VISTA perform best demonstrating that both are designed for handling longer sequences.

Figure 7 shows the ablation study results of quasi-linear attention by varying the sequence length on the Minimal Production dataset. We can clearly see that the QLA mechanism significantly reduces the the time to train and evaluate 1 epoch of data, while there are small diferences in AUC and NE.

Figure 8 shows the scaling law of increasing number of seed embeddings. We can clearly see that the model performance improves with larger number of seed embeddings, which, however, will incur more storage capacity cost in real world production scenario. Thus, in practice it is a tradeof between model performance and financial cost.

![](images/86ed9d0ee8f8252486ce0db9791ba1ee7aeb181fb355ce3287401f44e4a6b1fa.jpg)

![](images/7c4a5e27011b48c0d029a636634975bfc58c98e87ec8be4ca3e8307c8f24c2e3.jpg)

![](images/da5158f954b86cb8a3248094f01114b5b643cc4bcb35137bbfead2679e33e0b3.jpg)  
Figure 8: Ablating VISTA across number of seed embeddings on Amazon-Electronics.  
Figure 9: Inference time gains with increasing UIH lengths.

![](images/69b6ec98bbf96ee1d2ae9787aa975f085f9e868620183e15c9a09bca2934f83d.jpg)  
(a) Same category (142).

![](images/5203401a9f4931a5a505ad5d2e62f17fca50f02d52d0d8e03bdece13798b48b5.jpg)  
(b) Same category (368).

![](images/35521d426bf7c5876e15375bd87b94b03df86601eb68e62d289ba3fe26db2e6f.jpg)  
(c) Diferent categories (each).  
Figure 10: Pairwise cosine similarity of the output of two-stage attention of VISTA. For the same user, we compare the target attention output for items of similar or diferent categories.

Figure 10 compares the target embeddings, the output of VISTA’s two-stage attention modules, for diferent items given the same user history from Amazon-Electronics. Embeddings between items from the same category are more similar than those from diferent ones, as expected.

## 5.2.2 Industrial-Scale Dataset Results

In Table 3, we compare our proposed VISTA model with the baseline production model using HSTU as the backbone in both ofline and online experiments, on the industrial-scale dataset. In this setting, there are multiple tasks which measure diferent aspects of engagement information. We report the main consumption task (“C-Task”), and other engagement events (“E1-Task”, “E2-Task”, and “E3-Task”). To further understand the efectiveness of the model, we also conduct ablation studies by varying the embedding dimension, the number of seeds, and the use of generative reconstruction loss. As shorthands, (1) VISTA stands for the optimized proposed model co-trained with the baseline HSTU model, with 3-layer self-attention, 3-layer target-aware attention, 128 seeds, 256 embedding dimension and 2, 000 UIH sequence length. (2) VISTA-128D stands for VISTA model with 128 dimension embedding. (3) VISTA-64Seed stands for VISTA model with 64 seeds. (4) VISTA-w/o-Recon stands for VISTA model without generative reconstruction loss. The results demonstrate that our optimized VISTA configuration (128 seeds, 256 embedding dimension, and 2, 000 UIH sequence) significantly outperforms the standalone HSTU baseline for training and evaluation NE metrics.

Table 4 summarizes the performance improvement of QLA compared with the standard self-attention on production dataset, where we can see that the QLA is able to scale up with more layers and longer sequence for better NE metrics and even higher QPS.

Figure 9 shows the VISTA’s advantage on inference performance, especially for much longer sequence lengths. This is expected since VISTA’s main strength is to cache the UIH summarization. Thus, the most computationally expensive module, UIH summarization module, is deactivated during inference.

Table 3: Ofline comparative results with the baseline model and ablation models.

<table><tr><td rowspan="2">Models</td><td colspan="4">Training NE (↓)</td><td colspan="4">Eval NE (↓)</td></tr><tr><td>C-Task</td><td>E1-Task</td><td>E2-Task</td><td>E3-Task</td><td>C-Task</td><td>E1-Task</td><td>E2-Task</td><td>E3-Task</td></tr><tr><td>HSTU</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr><tr><td>VISTA</td><td>-0.47%</td><td>-0.82%</td><td>-2.30%</td><td>-1.72%</td><td>-0.40%</td><td>-1.19%</td><td>-2.98%</td><td>-2.23%</td></tr><tr><td>VISTA-128D</td><td>-0.32%</td><td>-0.50%</td><td>-1.86%</td><td>-1.43%</td><td>-0.29%</td><td>-1.07%</td><td>-2.51%</td><td>-1.82%</td></tr><tr><td>VISTA-64Seed</td><td>-0.36%</td><td>-0.68%</td><td>-1.70%</td><td>-1.45%</td><td>-0.37%</td><td>-1.11%</td><td>-3.01%</td><td>-2.09%</td></tr><tr><td>VISTA-w/o-Recon</td><td>-0.42%</td><td>-0.72%</td><td>-2.32%</td><td>-1.69%</td><td>-0.29%</td><td>-1.29%</td><td>-3.00%</td><td>-2.21%</td></tr></table>

Table 4: Comparing VISTA with and without quasi-linear attention.

<table><tr><td>Model Variant</td><td>Max Seq.</td><td>Layers</td><td>QPS (↑)</td><td>Training NE (↓)</td><td>Eval NE (↓)</td></tr><tr><td>VISTA-w/o-QLA</td><td>6,000</td><td>3</td><td>-</td><td>-</td><td>-</td></tr><tr><td>VISTA-w/-QLA</td><td>16,000</td><td>5</td><td>+5%</td><td>-0.1%</td><td>-0.13%</td></tr></table>

## 5.3 Online A/B Experimental Results

We conducted an online A/B test on our production video recommendation system, using 5% of the entire site trafic during a period of 15 days. The baseline is the HSTU model and we compare with adding the VISTA module, which is the same as our ofline experiment setup. Online metrics for the main consumption task “C-Task” and other online onboarding metrics, “O1-Task” and “O2-Task”, were significantly improved by 0.5%, 0.2%, 0.04%, respectively. VISTA demonstrated a 94% reduction in inference GPU resource (measured by inference QPS) usage by caching and serving embeddings, rather than re-computing them for every new user request. With a 0.01% “O2-Task” gain considered a substantial improvement on our platform, the VISTA model made realized contributions to the recommendation system.

## 6 Conclusion and Discussions

In this paper, we have proposed the VIrtual Sequential Target Attention (VISTA) framework, a novel two-stage approach that compresses ultra-long user interaction histories into a set of compact embeddings. This design strikes a crucial balance between computational eficiency and predictive accuracy, addressing the latency and scalability challenges of processing ultra-long user sequence data in production systems. VISTA’s practical applicability is underscored by its resilience to slight de-synchronization between its stages and its ability to approximate complex transformer architectures without their substantial computational cost. Our empirical evaluations demonstrate that VISTA not only captures the core information within user interactions but also achieves significant improvements across platform metrics. Our plans for future research involve further optimizing VISTA’s compression techniques and exploring its applications across other domains to enhance its generalizability.

[已省略: acknowledgement]

## B.1.4 Summary of Forward Pass and All Gradients

We introduce the notation that produces a diagonal matrix dimension $T \times T$ from two matrices $X , Y$ of dimension $T \times d \colon$

$$
\Delta (X, Y) := \mathrm{diag} ((X \odot Y) \mathbf {1} _ {T \times 1}) = \{\sum_ {\ell} X _ {i \ell} Y _ {i \ell} \delta_ {i j} \} _ {i j}.\tag{4}
$$

Then for forward, we have

$$
O [ S ] = Q [ S ] K [ S ] ^ {\top} V [ S ] =: Q [ S ] Z [ S ] ^ {\top}\tag{5}
$$

$$
O [ T ] = Q [ T ] K [ S ] ^ {\top} V [ S ] + \Delta (Q [ T ], K [ T ]) V [ T ] =: Q [ S ] Z [ S ] ^ {\top} + U [ T ] V [ T ]\tag{6}
$$

For backward, we have

$$
\frac {\partial L}{\partial Q [ S ]} = \frac {\partial L}{\partial O [ S ]} V [ S ] ^ {\top} K [ S ] =: d O [ S ] Z [ S ]\tag{7}
$$

$$
\frac {\partial L}{\partial Q [ T ]} = \frac {\partial L}{\partial O [ T ]} V [ S ] ^ {\top} K [ S ] + \Delta (\frac {\partial L}{\partial O [ T ]}, V [ T ]) K [ T ] =: d O [ T ] Z [ S ] + X [ T ] K [ T ]\tag{8}
$$

$$
\frac {\partial L}{\partial K [ S ]} = V [ S ] (\frac {\partial L}{\partial O}) ^ {\top} Q =: V [ S ] W ^ {T}\tag{9}
$$

$$
\frac {\partial L}{\partial K [ T ]} = \Delta (\frac {\partial L}{\partial O [ T ]}, V [ T ]) Q [ T ] =: X [ T ] Q [ T ]\tag{10}
$$

$$
\frac {d L}{d V [ S ]} = K [ S ] Q ^ {\top} \frac {\partial L}{\partial O} =: K [ S ] W\tag{11}
$$

$$
\frac {d L}{d V [ T ]} = \Delta (Q [ T ], K [ T ]) \frac {\partial L}{\partial O [ T ]} =: U [ T ] d O [ T ].\tag{12}
$$

From equation 7 and equation 8 we see that $Z [ S ] : = V [ S ] ^ { \top } K [ S ]$ should be an intermediate step to compute, of dimension $d \times d .$

From equation 9 and equation 11, we should compute $W : = Q ^ { \top } { \frac { \partial L } { \partial O } }$ first to obtain a $d \times d$ matrix, before pre-multiplying by $K [ S ]$ or post-multiplying by $V [ S ] ^ { \top }$ and then transpose (or transposing first, then pre-multiplying by $\mathbf { \bar { \theta } } _ { V [ S ] ) }$ .

From equation 6 and equation 12, we see that forward pass should save the intermediate step $Y [ \hat { T } ] : = \Delta ( Q [ T ] , K [ T ] )$ ). In fact we can just save the diagonal elements, which consumes less memory.

From equation 8 and equation 10, we can also save the intermediate step $X [ T ] : =$ $\begin{array} { r } { \Delta ( \frac { \partial L } { \partial O [ T ] } , \bar { V } [ T ] ) } \end{array}$

While $X [ T ] , Y [ T ]$ only involve 2T d FLOPs, W and Z involve $2 T d ^ { 2 }$ FLOPs.

## D Additional Experiment Details

## D.2 FuxiCTR Framework

We utilize the FuxiCTR library developed by Zhu et al. (2022; 2021) for our traditional sequential setting experiments. As mentioned in the main text, we designed the traditional sequential setting experiments mainly to compare the efectiveness of the attention layers and keep constant other model architecture and hyperparameter choices. (See Figure 12.)

We also report the common hyperparameters used in all the experiment results in Table 13.

![](images/6d7681332233602bbc4fc216ef8e61da165aaeb1dd0c1aa1fac9fdaebcc3f2c0.jpg)

<table><tr><td>Hyperparameter</td><td>Amazon</td><td>KuaiRand</td><td>Simplified Prod</td></tr><tr><td>Learning Rate</td><td>5.0e-4</td><td>1.0e-4</td><td>1.0e-3</td></tr><tr><td>Optimizer</td><td>Adam</td><td>Adam</td><td>Adam</td></tr><tr><td>Batch Size</td><td>1024</td><td>1024</td><td>128</td></tr><tr><td>Batch Norm</td><td>No</td><td>No</td><td>Yes</td></tr><tr><td>Early Stop Patience</td><td>4</td><td>5</td><td>1</td></tr><tr><td>Embedding Regularizer</td><td>0.005</td><td>None</td><td>None</td></tr><tr><td>Embedding Dimension</td><td>64</td><td>32</td><td>32</td></tr><tr><td>Embedding Initializer</td><td>1e-4</td><td>1e-4</td><td>1e-4</td></tr><tr><td>MLP Hidden Units</td><td>[1024, 512, 256]</td><td>[512, 128, 64]</td><td>[512, 128, 64]</td></tr><tr><td>MLP Activations</td><td>RELU</td><td>RELU</td><td>RELU</td></tr><tr><td># Attention Heads</td><td>4</td><td>4</td><td>4</td></tr><tr><td># Attention Layers</td><td>1</td><td>1</td><td>2</td></tr></table>

Figure 12: FuxiCTR Setup.  
Figure 13: Common hyperparameters used for traditional setting experiments.

The model-specific parameters for VISTA are the number of seeds and weight for the reconstruction loss, which were set at 128 and 1.0, respectively, for all experiments. No specific hyperparameter tuning was done, mainly relying on using common parameters for all models and repeating across 3 seeds for each model and dataset.


---

## 📑 关键章节 | MMSRARec: Summarization and Retrieval Augumented Sequential Recommendation Based on Multimodal Large Language Model

**arXiv ID**: [2512.20916](https://arxiv.org/abs/2512.20916)

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

[已省略: 2 related work]

## 2.1 Multimodal Large Language Model

Multimodal Large Language Models (MLLMs) based on multimodal pre-training [31] have advanced rapidly in recent years, achieving remarkable performance across a variety of downstream vision-language tasks such as visual question answering, grounding , and image captioning. With the progress of visual instruction tuning, state-of-the-art MLLMs including GPT-4o [10], Gemini [23], and Qwen-VL [1] are capable of efectively understanding human intentions and visual inputs, as well as performing complex multimodal in-context learning in response to instructions. However, directly applying MLLMs to sequential recommendation tasks remains challenging. Firstly, due to constraints on the model’s context length, it is dificult to input complete user behavior sequences into MLLMs. Secondly, MLLMs still exhibit limited capability in comprehending multiple images, which hinders their ability to interpret temporal trends in user interactions. Lastly, compared to traditional sequential recommendation models, MLLMs require significantly more time and computational resources for inference. Our proposed MMSRARec overcomes the limitations of context length and the high cost of multi-image reasoning through keyword-based compression, making it more suitable for real-world recommendation scenarios.

## 3 Method

## 4 Experiment

## 4.2 Experimental Setup

To assess the performance of baseline and our proposed method for multimodal sequential recommendations, we utilize HR@5, NDCG@5 and AUC as evaluation metrics. All models are evaluated in Python 3.10 using PyTorch [19]. All experiments are carried out on a workstation equipped with 8×NVIDIA A800 GPUs running Ubuntu 24.04.2 LTS, using PyTorch 2.6.0 with CUDA 12.9. In the experiments, we conduct inference and training of open-source models based on the MS-Swift [28] framework. All experiments are repeated three times under the same random seed to compute average value. Besides the parameter analysis experiments, in all other experiments, we set the length of user behavior sequences to 5 and the number of retrieved similar users to 3.

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

## 4.7 Eficiency Analysis

Furthermore, we analyze the impact of diferent MLLM backbones on recommendation eficiency and compare our approach with MLLM-MSR [24], a baseline method that also employs MLLMs as recommenders. The multiple inference steps and substantial time overhead of MLLM-MSR highlight the limitations of existing methods in processing user behavior sequences. Among the three compared models, Qwen2.5VL [1] achieves the best recommendation performance, followed by InternVL3 [32]. LLaVA [13] performs the worst, which may be attributed to the lack of a training corpus relevant to multimodal sequential recommendation in its pre-training data. Additionally, while the larger Qwen2.5VL-32B model shows marginal improvement over its smaller 7B counterpart, its significantly higher training and inference costs make it unsuitable for practical online deployment. MMSRARec can accommodate arbitrary MLLM backbones, demonstrating the robustness of its architectural design.

Table 7: Eficiency of MMSRARec with diferent MLLM backbone and baseline.

<table><tr><td rowspan="2">Model</td><td colspan="3">Amazon Baby</td><td colspan="3">Amazon Games</td><td rowspan="2"># Inferences</td><td rowspan="2">Time (s)</td></tr><tr><td>HR@5</td><td>AUC</td><td>NDCG@5</td><td>HR@5</td><td>AUC</td><td>NDCG@5</td></tr><tr><td>MLLM-MSR-LlaVA1.5-7B [24]</td><td>73.92</td><td>84.39</td><td>58.57</td><td>76.39</td><td>85.69</td><td>63.73</td><td>6</td><td>7.35</td></tr><tr><td>MMSRARec-LlaVA1.5-7B</td><td>76.26</td><td>81.33</td><td>57.69</td><td>71.23</td><td>62.34</td><td>60.46</td><td>1</td><td>0.54</td></tr><tr><td>MMSRARec-InternVL3-8B</td><td>78.67</td><td>86.12</td><td>60.50</td><td>82.96</td><td>85.26</td><td>62.33</td><td>1</td><td>0.82</td></tr><tr><td>MMSRARec-Qwen2.5VL-7B</td><td>81.50</td><td>85.27</td><td>62.82</td><td>83.74</td><td>85.81</td><td>63.14</td><td>1</td><td>0.73</td></tr><tr><td>MMSRARec-Qwen2.5VL-32B</td><td>82.05</td><td>87.28</td><td>66.75</td><td>82.56</td><td>87.41</td><td>65.88</td><td>1</td><td>1.13</td></tr></table>

## 5 Conclusion and Future Work

This paper proposes a novel method named MMSRARec for multimodal sequential recommendation, based on a multimodal large language model (MLLM). We first employ the MLLM to summarize items into concise keywords and finetune the model using rewards that incorporate summary length, information loss, and reconstruction dificulty, thereby enabling adaptive adjustment of the summarization strategy. Inspired by retrieval-augmented generation, we convert collaborative signals into corresponding keywords and integrate them as contextual input. Finally, we apply supervised fine-tuning with multi-task learning to align the MLLM’s capabilities with the requirements of multimodal sequential recommendation. This approach leverages the MLLM’s strong semantic understanding and in-context learning abilities, introduces previously overlooked collaborative signals into the MLLM, and reduces computational and time costs through once MLLM inference. Experiments on three real-world recommendation datasets demonstrate that MMSRARec achieves a better understanding of multimodal item information and user preferences, enabling accurate and interpretable recommendations.

Currently, the MLLM backbone used in MMSRARec contains 7B parameters, leading to longer inference times compared to traditional sequential recommendation models. In the future, we plan to explore methods such as distillation, output decoding, and pruning to replace the current backbone with a smaller model, thereby accelerating MMSRARec without compromising performance.

[已省略: references]


---

## 📑 关键章节 | Seeing and Reflecting: Multimodal Memory-Enhanced Agent Collaboration for Recommendation

**arXiv ID**: [2607.07108](https://arxiv.org/abs/2607.07108)

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

[已省略: 2 related work]

## 4 Methodology

We present MMEACR, a multimodal memoryenhanced agent collaboration framework for recommendation. As shown in Figure 2, MMEACR contains two complementary tracks: (1) a reasoning track, where User and Item Memory Agents maintain and update interpretable multimodal memories through LLM-based interaction; and (2) a matching track, where raw interaction narratives and item images are encoded into dense multimodal embeddings. The two tracks are finally combined through weighted Reciprocal Rank Fusion (RRF) to produce the final recommendation ranking.

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

[已省略: references]


---

## 📑 关键章节 | Diagnosing LLM-based Rerankers in Cold-Start Recommender Systems: Coverage, Exposure and Practical Mitigations

**arXiv ID**: [2604.16318](https://arxiv.org/abs/2604.16318)

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

[已省略: ii. related work]

## D. Diagnostic Analysis and Evaluation Methodologies

While most recommender system papers focus on comparative performance metrics (HR, nDCG, AUC), diagnostic analysis examining why systems succeed or fail remains relatively rare. Calibration studies [8] analyze score distributions and ranking quality. Coverage metrics [9] measure catalog utilization and long-tail item exposure. Exposure fairness research [10] quantifies bias in item visibility across user populations.

Beyond aggregate metrics, recent work emphasizes per-user analysis, error case studies, and failure mode taxonomies. Ablation studies systematically remove components to isolate contributions. Statistical testing with effect sizes provides nuanced understanding beyond p-values. Our diagnostic framework synthesizes these methodologies for comprehensive LLM reranker analysis.

## IV. DATASET AND EXPERIMENTAL SETUP

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

## VIII. DISCUSSION

## IX. CONCLUSION

This paper presents a rigorous diagnostic study of LLMbased cross-encoder rerankers in cold-start movie recommendation, employing controlled experiments on 500 users across multiple random seeds to isolate and quantify failure modes.

## A. Summary of Key Findings

Finding 1 - Popularity dominates sophisticated reranking: Simple popularity-based ranking achieves HR@10 $= ~ 0 . 2 6 8$ , outperforming cross-encoder reranking by 33.5× $( \mathrm { H R } @ 1 0 = 0 . 0 0 8 )$ . Statistical testing confirms overwhelming significance $\mathrm { ( p < 1 0 ^ { - 9 9 } }$ , Cohen’s $\mathrm { d } = - 0 . 5 9 3 )$ ), with 95% CI for mean difference: [-0.283, -0.239].

Finding 2 - Retrieval coverage is the primary bottleneck: FAISS-based candidate generation achieves only recall@200 = 0.109 (vs. 0.609 for baselines—5.6× gap). Strong correlation between retrieval coverage and final quality $( \mathrm { { r } ~ = ~ 0 . 8 9 } _ { }$ p $< ~ 0 . 0 0 1 )$ identifies retrieval as the dominant performance predictor. Median ground-truth position (6717) far exceeds typical cutoffs.

Finding 3 - Reranking provides no improvement over unranked candidates: Cross-encoder reranking yields HR@10 = 0.008 vs. 0.011 for "Candidates Only" baseline (no statistical difference, $\mathrm { ~ p ~ } = \ 0 . 3 1 )$ . This negative result demonstrates that reranker sophistication cannot compensate for poor candidate quality.

Finding 4 - Severe exposure bias limits personalization: Only 3 unique items appear as top-1 recommendations across 500 users $( \mathrm { G i n i } = 0 . 4 8 0 )$ , with single item dominating 50% of users. This extreme concentration indicates systematic bias rather than personalized matching.

Finding 5 - Poor score calibration: Relevant vs. irrelevant items show minimal score discrimination (mean difference = 0.079, Cohen’s d = 0.11, Spearman r = 0.004). Overlapping score distributions (>95% area overlap) explain ranking failure.

Finding 6 - Smaller candidate pools outperform larger pools: Counterintuitively, pool size 200 achieves HR@10 = 0.025 vs. 0.008 for pool 1000 (3.1× improvement), while reducing compute by 4.1× (1.76s vs. 7.23s per user). Larger pools introduce more noise, degrading discrimination.

## C. Methodological Contributions

Beyond empirical findings, this work provides methodological template for diagnostic evaluation of neural recommender systems:

Multi-faceted diagnostic framework: Coverage analysis (recall@K curves, GT position distributions), exposure metrics (unique top-K, Gini, concentration), score calibration (relevant vs. irrelevant distributions, rank correlation), and ablations (pool size, pipeline stages).

Statistical rigor: Paired testing with both parametric (t-test) and non-parametric (Wilcoxon) methods, effect sizes (Cohen’s d), confidence intervals, multiple comparison correction, and sensitivity analysis across random seeds.

Error case taxonomy: Systematic classification of failure modes (genre mismatch, metadata bias, popularity artifacts) to guide algorithmic improvements beyond aggregate metrics.

Reproducibility standards: Release of complete experimental logs, per-user results, master JSON configurations, and executable code to enable replication and extension.

[已省略: acknowledgments]

## Reproducing Results

To replicate our experiments, follow these steps (detailed instructions in README.md):

```txt

# 2. Run main experiments
python -m src.run_all_experiments \
--n-users 500 --seeds 42 7 123
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

[已省略: references]


---

## 📑 关键章节 | Eficient Retrieval Scaling with Hierarchical Indexing for Large Scale Recommendation

**arXiv ID**: [2604.12965](https://arxiv.org/abs/2604.12965)

## 1 Introduction

With the success of foundation models, substantial research has focused on exploring scaling laws [20, 25], such as those involving data volume, computational resources, and model parameters during training, with the aim of achieving improved performance at inference time. Building upon the scaling advancements in foundation language models, recent research has extended to foundation ranking and retrieval models for recommendation [1, 11, 16, 45, 65], catalyzing the development of numerous largescale industrial recommendation systems such as Wukong [62], HSTU [61], InterFormer [60], and ExFM [33].

However, given the surging development of enormous foundation models for ranking and retrieval in recommendation, how to deploy them to serve real-world (e.g., high frequency and heavy load) scenarios well is underexplored or not fully discussed. The most appealing concern can be the inference and retrieval cost. To leverage the inference ability of foundation retrieval models, passing the user and item features into the large-scale complex retrieval models to get the preference score prediction is often time-consuming and costly, especially when facing a massive volume of user-item pairs. For the above case, the quick win solution can include: (1) pre-computing the retrieval set for users ofline and serving the static result for a certain time window or (2) distilling the large models into small models and shipping them; but neither solutions fully release the representation and inference ability of large models.

![](images/15d169bf9715745d41cf17e496ef9517b4014c2beada0e6b886325e2091c3fe5.jpg)  
Figure 1: Overall Pipeline of MoNN Foundation Retrieval Model with HILL Index.

In addition, previous related research shows that using an index structure to organize items such that approximately searching over this index (e.g., beam search) can reduce the search space and fast output similar pairs [12, 13, 30, 31, 36, 67], but not fit today’s large-scale foundation model scenario in industry, which usually adopts deep and complex-connected neural networks to learn sophisticated interaction between users and items with rich structured descriptions, to the best of our knowledge. Hence, it motivates our research to learn a hierarchical index over the memory of large-scale foundation retrieval models, such that just searching this exactness-aware hierarchical index can output the retrieval result fast by avoiding much unnecessary search space.

Therefore, in this paper, we first share our experience in deploying large-scale foundation retrieval models at Meta Ads Platform, i.e., learning the hierarchical index for foundation retrieval models helps it obtain an efective-eficiency-balanced stage. To be specific, we introduce our Hierarchical Index Learning method, called HILL, which aims to hierarchically organize the memory in the foundation retrieval model, such that the searching and retrieval along the structure can be speed up and maintain the exactness. To achieve this goal, HILL leverages the cross-attention mechanism and residual quantization learning and enjoys the co-training with the foundation retrieval model. Moreover, to emphasize the reproducibility, we also first time systematically decipher the foundation retrieval model at Meta, called Modular Neural Network (MoNN), which is currently in service for recommending advertisements to daily Facebook and Instagram users, in terms of neural architecture, training procedures, and loss functions.

Interestingly, we also found that the intermediate-level nodes in the built hierarchical index tree compose a small (compared to the volume of users and items) but high-quality data source, which can fine-tune the pre-trained retrieval model to achieve a "test-time training" inference upgrade [17, 48, 58]. In short, testtime training (TTT) refers to methods that update model parameters during inference and typically does not require ground-truth labels, which is primarily designed to improve and adapt the model rather than relying solely on pretraining.

The entire pipeline of MoNN and HILL learning the index for online service and extracting the new data pair for test-time training is shown in Figure 1, and the rest of the paper is organized as follows: In Section 2, we introduce the MoNN foundation model deployed at Meta for user advertisement retrieval to pave the way for introducing the hierarchical index learning method in Section 3. Starting from Section 4, we show various experiments, including ofline public dataset benchmark performance and online deployment service. After we discuss related work in Section 5, we finally conclude the paper with several future directions in Section 6.

## 2 Foundation Retrieval Model at Meta - MoNN

In this section, we briefly introduce the architecture of the foundation model deployed in Meta for retrieval, which is called Modular Neural Network (MoNN), and is flexible to operate under diferent infrastructure constraints.

![](images/8668422b7ee5b2f345ea0fecf529e7abe0bb87b59126e7c92e97430ae9cbed42.jpg)  
Figure 2: A MoNN Block

In general, Modular Neural Network (MoNN) enhances the learning of sophisticated user and item interactions beyond a single dot product while maintaining high eficiency. As shown in Figure 2, MoNN has a modularized design comprising separate modules for user representations (User Tower), item representations (Item Tower), and the interaction between user and item (Interaction Tower).

User Tower. In short, the user tower takes user features to generate fixed-size user embeddings. These features can be dense (e.g., number of clicks by the user) and sparse (e.g., user engaged videos). Sparse features are processed by an embedding lookup table, and then all feature embeddings are concatenated and fed into the tower. Given that the user tower only needs to be computed once and shared across a vast number of items, it could scale up to very high complexity.

Item Tower. Similarly, the item tower mirrors the user tower, processing item dense (e.g., item historical click-through rate) and sparse features (e.g., content of item). Sparse features are input into another embedding lookup table, and all feature outputs are concatenated and fed into the tower.

Interaction Tower. The interaction tower operates on <user, item> interaction features (dense and sparse) as input. It follows a similar architecture to the user tower and item tower to produce the corresponding embeddings. To be more specific, the interaction tower is computationally intensive as it runs for each pair of user and item. To minimize the computation cost for <user, item> interaction features, we propose to use the Inverted Index Based Interaction Features (I2IF), where an inverted index is employed for indexing item information with user information written as a query to perform eficient crossing computation.

Over Architecture. Sitting atop the three underlying towers is called over architecture, short for OverArch, which is responsible for aggregating all information comprehensively and producing the user item preference score. OverArch can leverage DHEN [63] (or DeepFM [15], or Wukong [64]) to generate numerical logits.

Training Setup. Briefly, MoNN model is trained on a largescale training dataset with clicks and conversions as labels, impressions (non-click or conversion) as negatives, and additional unlabeled data used for semi-supervised learning to debias the model. A wide range of features (e.g., <sup>??</sup> (1000)) is used as input, and MoNN is optimized for multiple tasks, e.g., the click task and the conversion task. Hence, MoNN is then trained using a multi-task cross-entropy loss $\mathcal { L }$ as follows

$$
\mathcal {L} = \mathcal {L} _ {s u p} + \mathcal {L} _ {u n s u p}\tag{1}
$$

and the supervised loss function $\mathcal { L } _ { s u p }$ is expressed as

$$
\mathcal {L} _ {s u p} = \frac {- 1}{S} \sum_ {i = 1} ^ {S} \sum_ {t = 1} ^ {T} w _ {t} (y _ {t i} l o g (\hat {y} _ {t i}) + (1 - y _ {t i}) (l o g (1 - \hat {y} _ {t i})))\tag{2}
$$

where $w _ { t }$ is the weight for task $t , t \in \{ 1 , 2 , . . . , T \}$ , representing its importance. $y _ { t i } \in \{ 0 , 1 \}$ is the ground-truth label for sample <sup>??</sup> in task $t , \hat { y } _ { t i }$ is the predicted value of the model for sample <sup>??</sup> in task <sup>??</sup>, and <sup>??</sup> is the number of samples. Similarly, the unsupervised loss function $\mathcal { L }$ is expressed as

$$
\mathcal {L} _ {u n s u p} = \frac {- 1}{S} \sum_ {i = 1} ^ {S} \sum_ {t = 1} ^ {T} d i s t i l l (\hat {y} _ {t i}, y _ {t i} ^ {m o d e l})\tag{3}
$$

where $y _ { t i } ^ { m o d e l }$ is the soft label generated by MoNN or another well-trained teacher model, and <sup>??????????????</sup> function can be instanced also as the cross-entropy.

## 4 Experiments

In this section, we introduce the datasets, baselines, metrics, ofline performance, and online service report.

## 4.4 Ofline Performance

Here, the performance will be demonstrated in two aspects, $\mathrm { i . e . }$ internal test, public benchmark, and ablation study to verify the important components.

Internal Test. The efectiveness and eficiency analysis of MoNN with baselines are shown in Table 1, where all MoNN models are equipped with joint optimization of HILL and show significant performance, $\mathrm { e . g . , } > 0 . 0 5 \%$ NE Gain is significant [19].

To be specific, in Table 1, by scaling up the model size, we can observe that MoNN Large performs the best, in terms of NE and Recall metrics. However, it brings considerable infrastructure cost. Therefore, we propose to stack MoNN blocks and make the lower level take the majority (but not all) of the data during the training . As shown in the last three rows of Table 1, which largely reduces the infrastructure cost and keeps the competitive efectiveness. In addition to theoretical eficiency analysis, we present the cost of serving the MoNN model based on the following parameters: $\mathbf { I } _ { 1 }$ (number of nodes in $\mathrm { L } _ { 1 }$ layer), $\mathbf { I } _ { 2 }$ (number of nodes in $\mathrm { L } _ { 2 }$ layer) and V (number of items in the corpus), $\mathbf { M } _ { X S }$ denotes the cost to serve Two Tower model, $\mathbf { M } _ { S }$ denotes the cost to serve MoNN Small, ${ \bf { M } } _ { M }$ the cost to serve MoNN Medium, $\mathbf { M } _ { L }$ the cost to serve MoNN Large.

Ablation Studies. After showing that HILL can serve the large retrieval model efectively and eficiently, we then execute ablation studies to verify our theoretical design.

First, we design three training tricks during HILL optimizations, i.e., Softmax Temperature Scheduler, Balanced Index Distribution, Warmup Strategy. In Table 4, we observe that (1) the full version of including all training tricks has the best performance; (2) removing each one can reduce the performance, and they do not conflict with each other; (3) the Softmax Temperature Scheduler has the most significant loss when it is removed.

Second, in Table 5, we show that the EM version of HILL can also achieve a competitive performance, given the NE loss is less than 0<sup>.</sup>04%, which also suggests that the full version of HILL has a fair reason to be considered when the computing resource allows

Table 3: Comparison of Baselines across Gowalla, Yelp2018, and Amazon-Book.

<table><tr><td rowspan="2">Baseline</td><td colspan="2">Gowalla</td><td colspan="2">Yelp 2018</td><td colspan="2">Amazon-Book</td></tr><tr><td>Recall@20</td><td>NDCG@20</td><td>Recall@20</td><td>NDCG@20</td><td>Recall@20</td><td>NDCG@20</td></tr><tr><td>BPR [43]</td><td>0.1627</td><td>0.1378</td><td>0.0576</td><td>0.0468</td><td>0.0338</td><td>0.0261</td></tr><tr><td>GRMF [42]</td><td>0.1477</td><td>0.1205</td><td>0.0571</td><td>0.0462</td><td>0.0354</td><td>0.0270</td></tr><tr><td>GRMF-norm [42]</td><td>0.1557</td><td>0.1261</td><td>0.0561</td><td>0.0454</td><td>0.0352</td><td>0.0269</td></tr><tr><td>HOP-Rec [56]</td><td>0.1399</td><td>0.1214</td><td>0.0517</td><td>0.0428</td><td>0.0309</td><td>0.0232</td></tr><tr><td>ENMF [4]</td><td>0.1523</td><td>0.1315</td><td>0.0624</td><td>0.0515</td><td>0.0359</td><td>0.0281</td></tr><tr><td>MF-CCL [39]</td><td>0.1837</td><td>0.1493</td><td>0.0698</td><td>0.0572</td><td>0.0559</td><td>0.0447</td></tr><tr><td>SimpleX [39]</td><td>0.1872</td><td>0.1557</td><td>0.0701</td><td>0.0575</td><td>0.0583</td><td>0.0468</td></tr><tr><td>NeuMF [52]</td><td>0.1399</td><td>0.1212</td><td>0.0451</td><td>0.0363</td><td>0.0258</td><td>0.0200</td></tr><tr><td>Mult-VAE [32]</td><td>0.1641</td><td>0.1335</td><td>0.0584</td><td>0.0450</td><td>0.0407</td><td>0.0315</td></tr><tr><td>Macrid-VAE [38]</td><td>0.1618</td><td>0.1202</td><td>0.0612</td><td>0.0495</td><td>0.0383</td><td>0.0295</td></tr><tr><td>YouTubeNet [7]</td><td>0.1754</td><td>0.1473</td><td>0.0686</td><td>0.0567</td><td>0.0502</td><td>0.0388</td></tr><tr><td>CMN [9]</td><td>0.1405</td><td>0.1221</td><td>0.0475</td><td>0.0369</td><td>0.0267</td><td>0.0218</td></tr><tr><td>CML [21]</td><td>0.1670</td><td>0.1292</td><td>0.0622</td><td>0.0536</td><td>0.0522</td><td>0.0428</td></tr><tr><td>DeepWalk [41]</td><td>0.1034</td><td>0.0740</td><td>0.0476</td><td>0.0378</td><td>0.0346</td><td>0.0264</td></tr><tr><td>LINE [49]</td><td>0.1335</td><td>0.1056</td><td>0.0549</td><td>0.0446</td><td>0.0410</td><td>0.0318</td></tr><tr><td>Node2Vec [14]</td><td>0.1019</td><td>0.0709</td><td>0.0452</td><td>0.0350</td><td>0.0402</td><td>0.0309</td></tr><tr><td>Item2Vec [2]</td><td>0.1325</td><td>0.1057</td><td>0.0503</td><td>0.0411</td><td>0.0326</td><td>0.0251</td></tr><tr><td>GAT [51]</td><td>0.1401</td><td>0.1401</td><td>0.0543</td><td>0.0431</td><td>0.0326</td><td>0.0235</td></tr><tr><td>JKNet [55]</td><td>0.1622</td><td>0.1391</td><td>0.0608</td><td>0.0502</td><td>0.0268</td><td>0.0343</td></tr><tr><td>DropEdge [44]</td><td>0.1627</td><td>0.1394</td><td>0.0614</td><td>0.0506</td><td>0.0342</td><td>0.0270</td></tr><tr><td>APPNP [26]</td><td>0.1708</td><td>0.1462</td><td>0.0635</td><td>0.0521</td><td>0.0384</td><td>0.0299</td></tr><tr><td>DisenGCN [37]</td><td>0.1356</td><td>0.1174</td><td>0.0558</td><td>0.0454</td><td>0.0329</td><td>0.0254</td></tr><tr><td>LightGCN [18]</td><td>0.1830</td><td>0.1554</td><td>0.0649</td><td>0.0530</td><td>0.0411</td><td>0.0315</td></tr><tr><td>GC-MC [50]</td><td>0.1395</td><td>0.1204</td><td>0.0462</td><td>0.0379</td><td>0.0288</td><td>0.0224</td></tr><tr><td>PinSage [57]</td><td>0.1380</td><td>0.1196</td><td>0.0471</td><td>0.0393</td><td>0.0282</td><td>0.0219</td></tr><tr><td>NIA-GCN [46]</td><td>0.1359</td><td>0.1106</td><td>0.0599</td><td>0.0491</td><td>0.0369</td><td>0.0287</td></tr><tr><td>SGL-ED [54]</td><td>0.1835</td><td>0.1539</td><td>0.0675</td><td>0.0555</td><td>0.0478</td><td>0.0379</td></tr><tr><td>DeosGCF [35]</td><td>0.1784</td><td>0.1477</td><td>0.0626</td><td>0.0504</td><td>0.0410</td><td>0.0316</td></tr><tr><td>IMP-GCN [34]</td><td>0.1845</td><td>0.1567</td><td>0.0653</td><td>0.0531</td><td>0.0460</td><td>0.0357</td></tr><tr><td>BUIR [28]</td><td>0.1575</td><td>0.1301</td><td>0.0647</td><td>0.0526</td><td>0.0439</td><td>0.0346</td></tr><tr><td>DGCF [53]</td><td>0.1842</td><td>0.1561</td><td>0.0654</td><td>0.0534</td><td>0.0422</td><td>0.0324</td></tr><tr><td>IA-GCN [66]</td><td>0.1839</td><td>0.1562</td><td>0.0659</td><td>0.0537</td><td>0.0472</td><td>0.0373</td></tr><tr><td>LT-OCF [6]</td><td>0.1875</td><td>0.1574</td><td>0.0671</td><td>0.0549</td><td>0.0442</td><td>0.0341</td></tr><tr><td>HMLET [27]</td><td>0.1874</td><td>0.1589</td><td>0.0675</td><td>0.0557</td><td>0.0482</td><td>0.0371</td></tr><tr><td>GTN [10]</td><td>0.1870</td><td>0.1588</td><td>0.0679</td><td>0.0554</td><td>0.0450</td><td>0.0346</td></tr><tr><td>MGDCF [22]</td><td>0.1864</td><td>0.1589</td><td>0.0696</td><td>0.0572</td><td>0.0490</td><td>0.0378</td></tr><tr><td>BSPM-LM [5]</td><td>0.1901</td><td>0.1570</td><td>0.0713</td><td>0.0584</td><td>0.0733</td><td>0.0610</td></tr><tr><td>NESCL [47]</td><td>0.1908</td><td>0.1614</td><td>0.0740</td><td>0.0609</td><td>0.0623</td><td>0.0509</td></tr><tr><td>HILL (Ours)</td><td>0.1924</td><td>0.1628</td><td>0.0745</td><td>0.0612</td><td>0.0625</td><td>0.0513</td></tr></table>

Table 4: Ablation Study of Training HILL, MoNN Small as Backbone, on Gowalla Dataset.

<table><tr><td>Training Variant</td><td>NE (↓)</td></tr><tr><td>w/o Softmax Temperature Scheduler</td><td>+0.10%</td></tr><tr><td>w/o Balanced Index Distribution</td><td>+0.05%</td></tr><tr><td>w/o Warmup Strategy</td><td>+0.03%</td></tr></table>

Table 5: Ablation Study of HILL Approximation, 2-Layer MoNN as Backbone, on Gowalla Dataset.

<table><tr><td>Model Architecture</td><td>NE (↓)</td></tr><tr><td>HILL</td><td>-0.15%</td></tr><tr><td>HILL (EM)</td><td>-0.11%</td></tr></table>

Public Benchmark. In addition to the internal datasets, we also conduct the experiments on the public dataset to show the efectiveness of HILL by choosing NESCL [47] as the retrieval model and learning the corresponding hierarchical index. To be specific, we first use the EM version of HILL to learn the hierarchical index; then, we extract the <user, index node> data pairs in the index to fine-tune the retrieval model, and finally report the performance in Table 3. For example, in the Gowalla dataset, the outperformance is obtained by setting <sup>??</sup>?????? = 2, <sup>??ℎ??</sup>???? = 0<sup>.</sup>8 at the second layer, and <sup>??ℎ??</sup>???? = 0<sup>.</sup>4 at the third layer.

Parameter Analysis. Then, a natural question arises: whether including more new data pairs can further improve the performance? To answer this question, we prepare the parameter analysis in Tables 6 and 7, which shows that the small amount but precise test-time data is suficient for the leading performance.

Table 6: Performance with diferent <sup>??</sup><sub>DEP</sub>.

<table><tr><td> $\phi_{\text{DEP}}$ </td><td># Nodes per Inter-layer</td><td> $\phi_{\text{IR}}$ </td><td>Recall@20</td><td>NDCG@20</td></tr><tr><td>1</td><td>8000</td><td>0.8</td><td>0.1922</td><td>0.1624</td></tr><tr><td>2</td><td>8000, 800</td><td>0.8, 0.4</td><td>0.1924</td><td>0.1628</td></tr><tr><td>3</td><td>8000, 800, 80</td><td>0.8, 0.4, 0.2</td><td>0.1922</td><td>0.1624</td></tr><tr><td>4</td><td>8000, 8000, 80, 8</td><td>0.8, 0.4, 0.2, 0.1</td><td>0.1916</td><td>0.1623</td></tr></table>

Table 7: Performance with diferent $\phi _ { \mathbf { I R } }$ .

<table><tr><td> $\phi_{\text{DEP}}$ </td><td># Nodes per Inter-layer</td><td> $\phi_{\text{IR}}$ </td><td>Recall@20</td><td>NDCG@20</td></tr><tr><td>1</td><td>8000, 800</td><td>0.8, 0.1</td><td>0.1916</td><td>0.1624</td></tr><tr><td>1</td><td>8000, 800</td><td>0.8, 0.2</td><td>0.1923</td><td>0.1629</td></tr><tr><td>1</td><td>8000, 800</td><td>0.8, 0.3</td><td>0.1914</td><td>0.1624</td></tr><tr><td>1</td><td>8000, 800</td><td>0.8, 0.4</td><td>0.1924</td><td>0.1628</td></tr><tr><td>1</td><td>8000, 800</td><td>0.8, 0.5</td><td>0.1914</td><td>0.1623</td></tr><tr><td>1</td><td>8000, 800</td><td>0.8, 0.6</td><td>0.1924</td><td>0.1620</td></tr><tr><td>1</td><td>8000, 800</td><td>0.8, 0.7</td><td>0.1925</td><td>0.1623</td></tr></table>

[已省略: 5 related work]

## 6 Conclusion

To make the large-scale foundation retrieval model serve efectively and eficiently, in this paper, we propose the hierarchical index learning method HILL to learn the index structure over the memory of the foundation model, taking MoNN (i.e., a deployed retrieval model at Meta for Ads Retrieval) for illustration. Moreover, we found that learnt index convey a small set of new and high-quality data pairs that can be used to test-time fine-tune the model to boost the performance.

[已省略: references]


---

## 📑 关键章节 | Breaking User-Centric Agency: A Tri-Party Framework for Agent-Based Recommendation

**arXiv ID**: [2603.10673](https://arxiv.org/abs/2603.10673)

# Breaking User-Centric Agency: A Tri-Party Framework for Agent-Based Recommendation

Yaxin Gong gyx2022@mail.ustc.edu.cn University of Science and Technology of China Hefei, China

Haoyan Liu liuhaoyan@ustc.edu.cn University of Science and Technology of China Hefei, China

Yangyang Li liyangyang@live.com Academy of Cyber Beijing, China

Chongming Gao chongminggao@ustc.edu.cn University of Science and Technology of China Hefei, China

Wenjie Wang wenjiewang96@gmail.com University of Science and Technology of China Hefei, China

Fuli Feng fulifeng93@gmail.com University of Science and Technology of China Hefei, China

Chenxiao Fan simonfan@mail.ustc.edu.cn University of Science and Technology of China Hefei, China

Jianshan Sun sunjs9413@hfut.edu.cn Hefei University of Technology Hefei, China

Xiangnan He xiangnanhe@gmail.com University of Science and Technology of China Hefei, China

[已省略: acm reference format:]

## 1 Introduction

Large language models (LLMs) have demonstrated remarkable ca pabilities across a wide range of domains [20, 29, 30, 47], fun damentally reshaping how intelligent decision-making systems reason [36, 53] and interact with users [28, 52]. In recommender systems, these advances have stimulated growing interest in LLM based agent paradigms, where agents model user behaviors through language-driven interaction and reasoning [4, 43], enabling more expressive and interpretable preference representations compared to traditional collaborative filtering approaches [2, 32, 42].

However, despite these promising developments, most existing agent-based recommender methods largely mirror human-centered decision-making patterns [16, 49] and adopt a predominantly user centric modeling paradigm [21, 31, 33, 39]. They primarily opti mize user utility while treating items as passive functional entities [40, 45], thereby failing to adequately account for the interests of other critical stakeholders, such as content providers and platform operators [3, 28, 34, 44]. Such a user-centric decision paradigm is inherently unsustainable in multi-sided marketplaces. In particular, the pervasive Matthew efect concentrates exposure on already popular items [10], leaving long-tail creators with limited visibility [12, 51]. This imbalance weakens creator incentives, leading to creator churn and a subsequent decline in high-quality content production [7]. Moreover, excessive optimization for short-term user engagement exacerbates a winner-take-all dynamic, gradually homogenizing the content pool. Ultimately, this erosion of supply side diversity undermines user experience and harms the platform’s long-term ecosystem health.

Although some recent methods introduce item agents or content agents [19, 41, 43, 44], these agents typically function only as information carriers or attribute descriptors. Their role remains largely auxiliary, serving to better satisfy user preferences rather than actively pursuing reasonable exposure or long-term benefits on behalf of the items themselves.

To address this limitation at its root, we propose a Tri-party LLM-agent Recommendation framework (TriRec) that explicitly aligns the interests of users, items, and the platform, as illustrated in Figure 1. The framework adopts a disentangled two-stage ar chitecture that preserves user experience while empowering items with agency to actively compete for exposure through personalized self-promotion. At the platform level, global ranking is further regu lated by incorporating system-level constraints, ensuring long-term fairness and ecosystem stability.

Stage 1: Generative item self-promotion. We empower item agents with the capability to actively compete for visibility. Items are no longer passive candidates; instead, they become active partic ipants by generating personalized promotion tailored to the target user’s interest preference. For example, the same CD player might emphasize “high audio fidelity” to musicians, “popular tracks” to students, and “easy audio playback” to seniors. This mechanism not only improves matching quality but also provides long-tail items with opportunities to gain exposure.

Stage 2: Platform-led multi-objective re-ranking. After Stage 1 generates a high-quality candidate list, the platform performs sequential re-ranking to balance multiple objectives. Specifically, for each candidate item, the platform re-ranker considers immediate user relevance, platform-level fairness and expected item utility. The platform makes ranking decisions one position at a time; this sequential strategy ensures that ranking choices consider both current item exposure and long-term fairness.

Notably, incorporating item self-promotion led to an increase in both the average exposure and click-through probability of items, while simultaneously improving platform-level fairness. At the same time, the introduction of personalized persuasive content enhanced recommendation accuracy on the user side. These results demonstrate that our framework can simultaneously support the objectives of users, items, and the platform.

Our main contributions are as follows:

• We identify fundamental limitations of user-centric modeling in recommender systems and introduce the first tri-party LLMagent recommendation framework that explicitly coordinates users, items, and the platform through agent-based regulation of exposure and fairness.

• We propose a two-stage pipeline consisting of (i) item-side personalized self-promotion to endow items with agency and alleviate cold-start efects, and (ii) platform-led multi-objective re-ranking with exposure modulation to balance tri-party interests.

• Experiments validate the superiority of TriRec over existing baselines in enhancing accuracy, fairness, and item utility, and further show that item self-promotion can simultaneously enhance fairness and efectiveness, challenging the conventional trade-of assumption.

[已省略: 2 related work]

## 3.1 Multi-Stakeholder Utility Modeling

While agent-based interaction enables flexible modeling of user preferences, real-world recommendation systems inherently involve multiple stakeholders with competing objectives. To formalize this multi-stakeholder setting, we define utility functions for users, items, and the platform, which together characterize the overall optimization target of the recommendation process.

• User Utility. Users primarily seek high relevance and engagement quality [48]. At the platform stage, we define the user-side utility on a per-item basis:

$$
U _ {\text { user }} (u, i) = r (u, i),\tag{1}
$$

where $r ( u , i )$ denotes the predicted relevance score produced by the user agent.

• Item Utility. Items aim to obtain efective exposure and longterm visibility across recommendation opportunities. We quantify the realized item-side gain $U _ { \mathrm { i t e m } }$ using the Expected Item Utility (EIU):

$$
E I U (u, i) = v (\mathrm{rank} _ {u} (i)) \cdot \mathrm{CTR} (u, i),\tag{2}
$$

where <sup>??</sup> (·) models position-dependent exposure probability following a logarithmic decay, and $\mathrm { C T R } ( u , i )$ denotes the predicted click-through probability. In our implementation, $\operatorname { C T R } ( u , i )$ is estimated by applying a sigmoid transformation to the cosine similarity between user and item semantic embeddings. The cumulative item utility is aggregated across users and sequential recommendation rounds.

• Platform Utility. The platform aims to regulate exposure allocation and mitigate group-level bias across the recommended items. We denote the platform utility as $U _ { \mathrm { p l a t f o r m } } ( \Pi )$ , where Π aggregates ranking outcomes over users and time. In practice, platform-level fairness is quantified using Distributional Group Unfairness (DGU) and Maximal Group Unfairness (MGU) [11], which measure the discrepancy between the exposure distribution of item groups in top-<sup>??</sup> recommendation results and their historical distribution in the training data.

Based on the above utility definitions, the overall recommendation process in TriRec is realized through a two-stage agentic pipeline. Specifically, Stage 1 focuses on constructing relevanceoriented candidate rankings by modeling fine-grained user–item semantic alignment via agent-based interaction and personalized item self-promotion. This stage produces a high-quality preference backbone without introducing exposure regulation.

Stage 2 then operates on top of the Stage 1 outputs by treating recommendation as a sequential control problem. The platform reranker observes the system state, including historical exposure and relevance rankings, and performs state-aware re-ranking actions to jointly optimize user utility, item exposure utility, and platform level fairness over time.

This decoupled design enables TriRec to separate semantic pref erence modeling from long-term exposure regulation, while main taining a closed-loop decision process that dynamically adapts to evolving system states.

[已省略: 3.2 agent-based preference interaction]

## 4 Method

Figure 2 provides an overview of the proposed TriRec framework. The framework is composed of two sequential modules: a user–item interaction module for generative personalized self-promotion and a platform control module for exposure-aware re-ranking. Both modules operate entirely at inference time with frozen LLM pa rameters, building upon the agent memory constructed during the preference interaction phase described in §3.2. We next describe the design and implementation details of each component.

![](images/5e8fbe50904eaaae707a4c876bc9e5dc4b4a7efd43affd4331f16dc25b267538.jpg)  
Figure 2: Overview of the proposed two-stage TriRec framework, where Stage 1 performs relevance-aware re-ranking via user–item interaction, and Stage 2 conducts exposureaware re-ranking through tri-party utility optimization.

## 5 Experiments

In this section, we conduct experiments to address the following research questions:

• RQ1: How does TriRec perform in terms of accuracy, fairness, and expected item utility compared to existing methods?

• RQ2: What are the individual contributions of key components and design choices to the final performance?

• RQ3: How do key hyperparameters afect the trade-of among tri-party interests?

• RQ4: How efective is the item self-promotion mechanism in Stage 1 at improving the ranking of cold-start items?

## 5.1 Experimental Setup

5.1.1 Dataset. We conduct experiments on four real-world datasets from three sources: Amazon<sup>1</sup>, Steam<sup>2</sup>, and Goodreads<sup>3</sup>. From Amazon, we use the CDs & Vinyl and Movies & TV categories and from Goodreads, we focus on the Young Adult (YA) subdo main. Table 1 summarizes the dataset statistics. Following standard practice, we retain only positive interactions (rating ≥ 4) and filter for users with 10 to 100 interactions to ensure suficient preference signals while excluding anomalous accounts. All items are encoded with a pre-trained Sentence-BERT model [9] to obtain semantic embeddings.

Table 1: Statistics of the datasets. Full represents the original scale, and Processed denotes the refined subset used for our tri-party agentic recommendation experiments.

<table><tr><td>Datasets</td><td>#Items</td><td>#Inters.</td><td>Sparsity</td></tr><tr><td>CDs &amp; Vinyl (Full)</td><td>701,673</td><td>4,827,273</td><td>99.99%</td></tr><tr><td>- Processed</td><td>33,042</td><td>41,901</td><td>99.93%</td></tr><tr><td>Movies &amp; TV (Full)</td><td>747,764</td><td>17,328,314</td><td>99.99%</td></tr><tr><td>- Processed</td><td>27,407</td><td>40,907</td><td>99.92%</td></tr><tr><td>Goodreads YA (Full)</td><td>93,398</td><td>34,919,254</td><td>99.94%</td></tr><tr><td>- Processed</td><td>10,786</td><td>60,743</td><td>99.71%</td></tr><tr><td>Steam Games (Full)</td><td>15,474</td><td>7,793,069</td><td>99.98%</td></tr><tr><td>- Processed</td><td>6,635</td><td>36,006</td><td>99.72%</td></tr></table>

5.1.2 Baselines. We compare TriRec with three groups of state-ofthe-art models:

• Agent-based User-Centric: AgentCF++ [19] and MACRec [32]. AgentCF++ extends AgentCF with memory-enhanced LLM-based agent interactions; we adopt its single-domain configuration. MACRec employs multi-agent collaboration for recommendation. Both optimize exclusively for user relevance.

• Creator-Side Focus: Rec4Agentverse [43], which introduces item agents for autonomous interaction, and DualRec [7], which treats items as active queries in a dual-market setting. These methods model item-side dynamics but lack explicit exposure optimization or active self-promotion.

• Platform Fairness Re-ranking: SCRUF-D [1], a multi-agent social choice framework for fairness arbitration, and LTP-MMF [38], which optimizes long-term provider max-min fairness under feedback loops. Both inject fairness constraints at the platform level through post-hoc re-ranking.

5.1.3 Evaluation Protocol. We evaluate recommendation perfor mance from three stakeholder perspectives: (1) User accuracy: NDCG@K (K=5) and MRR, measuring the ranking quality of recom mended lists against ground-truth interactions. (2) Item utility: Ex pected Item Utility (EIU, Eq. 2), quantifying the position-weighted click propensity aggregated across users. (3) Platform fairness: DGU@K and MGU@K [11] (K=10), measuring distributional and worst-case group-level exposure disparity, respectively. Items are partitioned into eight equal-sized popularity-based groups following common practice.

5.1.4 Candidate Construction. We adopt a leave-one-out evaluation protocol, using each user’s most recent interaction as the test item and the remainder for training. For each test instance, we construct the candidate set with 1 ground-truth item and <sup>??</sup> negative samples. Unlike prior work [44] that samples negatives uniformly at random, we adopt a hard negative sampling strategy: the <sup>??</sup> negatives are retrieved by a pre-trained SASRec model [18]. This creates a substantially more challenging and realistic evaluation setting where all candidates are plausible recommendations that have passed an upstream retrieval filter. Crucially, all compared methods are evaluated on identical candidate sets, ensuring that any performance diferences are attributable to the recommendation algorithms themselves rather than to candidate construction artifacts.

We set <sup>??</sup>=9 (candidate set size 10) as the default configuration, which is consistent with established agent-based recommendation studies [19, 44]. This scale reflects a deliberate design choice rather than an arbitrary limitation: in industrial multi-stage recommendation pipelines, the final re-ranking module typically operates on a compact candidate set (10–50 items) that has already been filtered through upstream retrieval and pre-ranking stages [8, 15]. Our framework is positioned precisely at this re-ranking stage, making the candidate set size a realistic deployment parameter. Robustness across $| C _ { u } | \in \{ 1 0 , 1 5 , 2 0 \}$ is verified in §5.2.5.

5.1.5 Platform Re-Ranking Configuration. We use gpt-4o-mini as the default backbone LLM for all agents. To verify that performance gains stem from the proposed framework rather than a specific LLM, we additionally evaluate TriRec with alternative back bones (§5.3.5). For the position-aware participation policy, we set $\alpha _ { \mathrm { m a x } } { = } 1 . 0 , \alpha _ { \mathrm { m i n } } { = } 0 . 1$ , and <sup>??</sup>=0<sup>.</sup>1. The platform fairness coeficients are $\lambda _ { 1 } = \lambda _ { 2 } = 0 . 5$ , and the item utility sensitivity exponent is $\lambda _ { \mathrm { i t e m } } { = } 1 0$ Sensitivity analysis of all hyperparameters is provided in §5.4.

## 5.2 Overall Performance Comparison (RQ1)

Table 2 reports the overall comparison across four datasets. We analyze the results from three stakeholder perspectives.

5.2.1 User-Side Accuracy. TriRec achieves the highest NDCG across all four datasets and the best or second-best MRR in all cases. On Movies & TV and Steam, LTP-MMF obtains slightly higher MRR, which we attribute to its feedback-loop optimization that aggressively promotes the single most relevant item to the top position. However, this comes at the cost of substantially worse fairness (discussed below).

Compared with user-centric agent methods (MACRec, AgentCF++), TriRec demonstrates consistent accuracy gains, indicating that the item self-promotion mechanism in Stage 1 provides richer semantic matching signals rather than introducing noise. Compared with creator-side approaches (Rec4AgentVerse, DualRec), TriRec also achieves superior ranking quality, suggesting that enabling items to actively communicate personalized information is more efective than passive representation-based modeling.

Table 2: Overall performance comparison across four datasets. The best results are bolded.

<table><tr><td rowspan="2">Method</td><td colspan="5">CDs &amp; Vinyl</td><td colspan="5">Movies &amp; TV</td><td colspan="5">Goodreads YA</td><td colspan="5">Steam Games</td></tr><tr><td>NDCG↑</td><td>MRR↑</td><td>DGU↓</td><td>MGU↓</td><td>EIU↑</td><td>NDCG↑</td><td>MRR↑</td><td>DGU↓</td><td>MGU↓</td><td>EIU↑</td><td>NDCG↑</td><td>MRR↑</td><td>DGU↓</td><td>MGU↓</td><td>EIU↑</td><td>NDCG↑</td><td>MRR↑</td><td>DGU↓</td><td>MGU↓</td><td>EIU↑</td></tr><tr><td>MACRec</td><td>0.4858</td><td>0.4676</td><td>0.1632</td><td>0.1467</td><td>0.5898</td><td>0.4167</td><td>0.4032</td><td>0.2322</td><td>0.1787</td><td>0.5375</td><td>0.5431</td><td>0.5200</td><td>0.5568</td><td>0.5323</td><td>0.6279</td><td>0.3327</td><td>0.3367</td><td>0.4483</td><td>0.4314</td><td>0.4857</td></tr><tr><td>AgentCF++</td><td>0.3874</td><td>0.3914</td><td>0.1587</td><td>0.1479</td><td>0.5289</td><td>0.3980</td><td>0.3960</td><td>0.2275</td><td>0.1797</td><td>0.5314</td><td>0.5004</td><td>0.4816</td><td>0.5336</td><td>0.4942</td><td>0.5990</td><td>0.4431</td><td>0.4238</td><td>0.4188</td><td>0.4023</td><td>0.5547</td></tr><tr><td>Rec4AgentVerse</td><td>0.3878</td><td>0.3546</td><td>0.1705</td><td>0.1588</td><td>0.4998</td><td>0.4476</td><td>0.4168</td><td>0.2479</td><td>0.1970</td><td>0.5528</td><td>0.5354</td><td>0.4881</td><td>0.6389</td><td>0.6325</td><td>0.5923</td><td>0.4088</td><td>0.3702</td><td>0.4984</td><td>0.4747</td><td>0.5139</td></tr><tr><td>DualRec</td><td>0.3130</td><td>0.3063</td><td>0.1572</td><td>0.1549</td><td>0.4637</td><td>0.3097</td><td>0.3081</td><td>0.2504</td><td>0.1961</td><td>0.4645</td><td>0.2509</td><td>0.2619</td><td>0.6481</td><td>0.6301</td><td>0.4268</td><td>0.2949</td><td>0.2935</td><td>0.5038</td><td>0.4798</td><td>0.4530</td></tr><tr><td>SCRUF-D</td><td>0.2580</td><td>0.2681</td><td>0.1508</td><td>0.1465</td><td>0.4340</td><td>0.3078</td><td>0.2968</td><td>0.2394</td><td>0.1898</td><td>0.4564</td><td>0.2645</td><td>0.2736</td><td>0.6387</td><td>0.6315</td><td>0.4371</td><td>0.3229</td><td>0.3124</td><td>0.4914</td><td>0.4672</td><td>0.4684</td></tr><tr><td>LTP-MMF</td><td>0.4656</td><td>0.4580</td><td>0.1780</td><td>0.1700</td><td>0.5737</td><td>0.4354</td><td>0.4519</td><td>0.3220</td><td>0.2286</td><td>0.5628</td><td>0.5367</td><td>0.5180</td><td>0.5204</td><td>0.5127</td><td>0.6223</td><td>0.4441</td><td>0.4561</td><td>0.4342</td><td>0.4288</td><td>0.5684</td></tr><tr><td>TriRec</td><td>0.4951</td><td>0.4702</td><td>0.1596</td><td>0.1468</td><td>0.5925</td><td>0.4630</td><td>0.4451</td><td>0.2258</td><td>0.1768</td><td>0.5709</td><td>0.5503</td><td>0.5450</td><td>0.5152</td><td>0.4805</td><td>0.6465</td><td>0.4546</td><td>0.4512</td><td>0.4054</td><td>0.3970</td><td>0.5748</td></tr></table>

![](images/d2c45c66d09563246b7d118d1b35cbe38caba566eebb930482e3df913ca99d83.jpg)

![](images/14925e7f88049d831c0990373d445a9d9d3f2697d981590717b399e7513e19a7.jpg)

![](images/11b60b96cb9412a84cd67fadc2a9c45ddc539ee09ce01943b2a16bbc7905a75b.jpg)

![](images/bd0fa6810ddc973ae41b99a0bfda4219da7b2747e8e6f5f246b6e83df766ddb4.jpg)

![](images/53ea9d8596b9784386ebafdeda85cfa7fccfc90297087f26beece0af36738a6b.jpg)  
Figure 3: Performance comparison under varying candidate set sizes (10, 15, 20) on CDs & Vinyl.

5.2.2 Platform-Level Fairness. TriRec achieves the best DGU and MGU on Movies & TV, Goodreads YA, and Steam Games. On CDs & Vinyl, SCRUF-D obtains the lowest DGU and MGU; however, its NDCG (0.258) is nearly half that of TriRec (0.495), revealing that SCRUF-D achieves fairness by drastically sacrificing relevance—an undesirable trade-of in practice.

In contrast, TriRec attains competitive fairness (DGU: 0.160, MGU: 0.147 on CDs & Vinyl) while simultaneously maintaining the highest accuracy, demonstrating a more favorable relevance– fairness balance. Notably, LTP-MMF exhibits the worst fairness across most datasets despite strong accuracy, confirming that op timizing long-term engagement feedback alone is insuficient to achieve group-level exposure balance without explicit fairness regulation.

5.2.3 Item-Side Utility. TriRec consistently achieves the highest EIU across all four datasets. These gains demonstrate the efec tiveness of combining item self-promotion with exposure-aware re-ranking: the former provides high-quality semantic signals that improve matching precision, while the latter redistributes exposure toward under-served items with high click probability.

Compared with creator-side methods (Rec4AgentVerse, Dual Rec) that also model item-side dynamics, TriRec achieves substan tially higher EIU, indicating that endowing items with active selfexpression capability yields greater item-side benefits than passive dual-market modeling.

5.2.4 Cross-Domain Consistency. Across four datasets spanning ecommerce (CDs & Vinyl, Movies & TV), social reading (Goodreads YA), and gaming (Steam), TriRec exhibits stable relative advantages. Although absolute metric values vary due to domain characteristics and interaction density, the consistent improvements confirm that the proposed tri-party framework generalizes well across heteroge neous recommendation scenarios.

Table 3: Ablation Study Results on the CDs dataset.

<table><tr><td>Model Variants</td><td>NDCG ↑</td><td>MRR ↑</td><td>DGU ↓</td><td>MGU ↓</td><td>EIU ↑</td></tr><tr><td>(a) w/o  $\mathcal{Y}^{(1)}$ </td><td>0.3381</td><td>0.3240</td><td>0.1298</td><td>0.1309</td><td>0.4782</td></tr><tr><td>(b) w/o  $\{S_{i\rightarrow u}, \mathcal{Y}^{(2)}\}$ </td><td>0.3642</td><td>0.3718</td><td>0.1695</td><td>0.1538</td><td>0.5143</td></tr><tr><td>(c) w/o  $\mathcal{Y}^{(2)}$ </td><td>0.4684</td><td>0.4581</td><td>0.1659</td><td>0.1477</td><td>0.5816</td></tr><tr><td>(d) w/o  $U_{\text {platform}}$ </td><td>0.4873</td><td>0.4615</td><td>0.1683</td><td>0.1556</td><td>0.5851</td></tr><tr><td>(e) w/o Dynamic  $\alpha_k$ </td><td>0.4635</td><td>0.4276</td><td>0.1301</td><td>0.1296</td><td>0.5603</td></tr><tr><td>(f) w/o  $U_{\text {user}}$ </td><td>0.2634</td><td>0.2839</td><td>0.0815</td><td>0.0823</td><td>0.4458</td></tr><tr><td>(g) w/o  $U_{\text {item}}$ </td><td>0.4857</td><td>0.4579</td><td>0.1535</td><td>0.1460</td><td>0.5824</td></tr><tr><td>(h) w/o  $\text{Sim}_{\text {emb}}(\text{z},\text{h})$ </td><td>0.4776</td><td>0.4487</td><td>0.1560</td><td>0.1470</td><td>0.5753</td></tr><tr><td>(i) with  $\text{Sim}_{\text {emb}}^{\text {rand}}(\text{z},\text{h})$ </td><td>0.4627</td><td>0.4283</td><td>0.1653</td><td>0.1532</td><td>0.5601</td></tr><tr><td>TriRec</td><td>0.4951</td><td>0.4702</td><td>0.1596</td><td>0.1468</td><td>0.5925</td></tr></table>

5.2.5 Robustness to Candidate Set Size. To verify that the above conclusions are not artifacts of a specific evaluation scale, we vary the candidate set size $| C _ { u } | \in \{ 1 0 , 1 5 , 2 0 \}$ (corresponding to <sup>??</sup> ∈ {9<sup>,</sup> 14<sup>,</sup> 19} negative samples) and report results on CDs & Vinyl in Figure 3.

As candidate set size increases, all methods experience natural accuracy degradation due to the increased dificulty of distinguishing the target item from a larger pool of competitive negatives. However, the relative performance ordering remains stable: TriRec consistently achieves the best or near-best scores across all three stakeholder metrics under all candidate set sizes. This confirms that our main findings are robust to the experimental scale configuration and not dependent on a particular candidate set size.

## 5.4 Analysis of Key Factors (RQ3)

We conduct sensitivity analysis on CDs & Vinyl, examining $\lambda _ { \mathrm { i t e m } }$ as the primary factor, followed by $\alpha _ { \mathrm { m a x } } , p , \lambda _ { 1 }$ , and $\lambda _ { 2 }$ .

5.4.1 Efect $o f \lambda _ { i t e m } .$ Figure 4 reports performance as $\lambda _ { \mathrm { i t e m } }$ varies from 0 to 100. When $\lambda _ { \mathrm { i t e m } } = 0 ;$ , the exposure-aware modulator de grades to a constant $( U _ { \mathrm { e x p o - i t e m } } \equiv 1 )$ , yielding the worst performance across all three stakeholder metrics, confirming that item utility modeling is essential.

$\mathtt { A s } \lambda _ { \mathrm { i t e m } }$ increases to the range of 5–10, all three metrics improve concurrently: NDCG rises to 0.499 (+6.6%), DGU decreases to 0.159, and EIU increases to 0.595. This challenges the conventional assumption that stakeholder objectives are inherently conflicting, and demonstrates that the exposure-aware modulator surfaces high potential under-exposed items that simultaneously benefit users, items, and platform fairness.

Beyond $\lambda _ { \mathrm { i t e m } } = 2 0 $ , performance plateaus as excessive amplifica tion causes over-reliance on embedding signals. The cumulative EIU remains constant (≈4.533), indicating that $\lambda _ { \mathrm { i t e m } }$ controls expo sure redistribution rather than total volume. We set $\lambda _ { \mathrm { i t e m } } = 1 0$ as the default.

5.4.2 Efect of Other Hyperparameters. Figure 5 reports sensitivity of the remaining parameters.

(a) $\alpha _ { \mathrm { m a x } }$ controls positional diferentiation. Increasing $\alpha _ { \mathrm { m a x } }$ from 0.1 to 1.0 improves accuracy (NDCG: 0.434→0.495) while degrading fairness (DGU: 0.105→0.159), as top positions increasingly preserve Stage 1 relevance ordering. Even at $\alpha _ { \mathrm { m a x } } = 1 . 0$ , lower ranks retain $\alpha _ { k } \approx 0 . 1$ , so regulation is concentrated at lower positions rather than fully disabled. We set $\alpha _ { \mathrm { m a x } } = 1 . 0$ , as the sparse exposure history on this dataset makes aggressive top-position fairness injection counterproductive.

(b) <sup>??</sup> governs how rapidly $\alpha _ { k }$ decays from $\alpha _ { \mathrm { m a x } }$ to $\alpha _ { \mathrm { { m i n } } }$ along the ranked list. As <sup>??</sup> increases, fairness improves (DGU: 0.159→0.140) at the cost of accuracy (NDCG: 0.495→0.482). Beyond $p = 1 . 0$ , accuracy degradation accelerates while fairness gains remain marginal, making larger <sup>??</sup> increasingly cost-ineficient. Values below 1.0 ofer the most favorable accuracy-fairness ratio.

(c–d) $\lambda _ { 1 }$ and $\lambda _ { 2 }$ exhibit high robustness: varying either from 0 to 1 improves the corresponding fairness metric while causing less than 0.3% NDCG loss, confirming strong compatibility between fairness signals and user relevance.

## 6 Conclusion and Limitations

We proposed TriRec, the first tri-party LLM-agent recommendation framework that coordinates users, items, and the platform via item self-promotion and platform-led multi-objective re-ranking. Exper iments validate the superiority of TriRec over existing baselines in enhancing tri-party utilities, suggesting that item self-promotion can mitigate the conventional relevance–fairness trade-of.

Two limitations remain: our ofline protocol may not fully reflect long-term dynamics, and the generated self-promotion is not yet quantitatively audited for factuality. Future work will address these via multi-round simulation, online A/B tests, and retrieval-grounded factuality constraints, as well as safeguards against adversarial self promotion and provider gaming.

[已省略: references]


---

## 📑 关键章节 | Ofline Reasoning for Eficient Recommendation: LLM-Empowered Persona-Profiled Item Indexing

**arXiv ID**: [2602.21756](https://arxiv.org/abs/2602.21756)

## 3 Proposed Method

The key idea of Persona4Rec is to shift the costly reasoning process from online (inference) stage to the ofline stage by precomputing review-grounded item personas. Specifically, during ofline stage, Persona4Rec derives multiple personas for each item, where each persona captures a distinct motivation or preference pattern associated with the item. These personas are organized into a personaprofiled item index and serve as the primary units for aligning with user profiles, which summarize user historical interactions, rather than relying on direct alignment with raw item information. During online stage, user profiles are eficiently matched against pre-indexed personas, enabling real-time recommendation without invoking expensive reasoning. Moreover, the selected persona naturally provides a human-interpretable explanation for the recommendation, grounded in evidence from actual user reviews. As illustrated in Figure 2, Persona4Rec consists of two stages:

• <sup>Ofline</sup> <sup>process:</sup> Persona4Rec analyzes item information and reviews to generate multiple personas representing diverse user motivations. These personas are then paired with user profiles to produce user–persona alignment signals, which are used to train a lightweight encoder that embeds both into a shared space and constructs a persona-profiled item index for eficient scoring.

• <sup>Online</sup> <sup>process:</sup> During inference, Persona4Rec constructs user profiles on-the-fly from recent interaction histories, leveraging the precomputed persona representations. For each candidate item, its personas are scored against the user profile via eficient similarity computation, and relevance score is determined by the best-matching persona, which is used for reranking.

## 4 Experiments

In this section, we design and conduct experiments to answer the following research questions.

<sub>•</sub> RQ1 (Reranking Performance): <sub>How</sub> <sub>well</sub> <sub>does Persona4Rec</sub> rerank candidates produced by first-stage recommenders, and how robust is it across sparsity scenarios?

<sub>•</sub> RQ2 (Eficiency & Scalability): <sub>How</sub> <sub>do</sub> <sub>inference</sub> <sub>latency</sub> <sub>and</sub> memory footprint compare to LLM-based rerankers, and how do they scale with request volume?

<sub>•</sub> RQ3 (Recommendation Explainability): <sub>How</sub> <sub>efectively</sub> <sub>do</sub> persona-based rationales convey clear, consistent, and engaging explanations of recommendations?

Table 4: Top-?? recommendation performance of Persona4Rec and other LLM-based reranking methods on both datasets. For each user, candidate items are initially retrieved by two CF models: BPR-MF and LightGCN. ( \* : p < 0.05 )

<table><tr><td rowspan="2">Dataset</td><td rowspan="2">Generator</td><td rowspan="2">Reranker</td><td colspan="3">@5</td><td colspan="3">@10</td><td colspan="3">@20</td></tr><tr><td>HR</td><td>MRR</td><td>NDCG</td><td>HR</td><td>MRR</td><td>NDCG</td><td>HR</td><td>MRR</td><td>NDCG</td></tr><tr><td rowspan="12">Amazon-Books</td><td rowspan="6">BPR-MF</td><td>-</td><td>0.0639</td><td>0.0340</td><td>0.0414</td><td>0.1000</td><td>0.0388</td><td>0.0531</td><td></td><td>0.0419</td><td>0.0643</td></tr><tr><td>ZS-LLM</td><td>0.0664</td><td>0.0357</td><td>0.0433</td><td>0.1025</td><td>0.0405</td><td>0.0550</td><td>|</td><td>0.0434</td><td>0.0655</td></tr><tr><td>TALLRec</td><td>0.0346</td><td>0.0166</td><td>0.0210</td><td>0.0667</td><td>0.0207</td><td>0.0313</td><td rowspan="2">0.1446</td><td>0.0258</td><td>0.0505</td></tr><tr><td>EXP3RT</td><td>0.0498</td><td>0.0238</td><td>0.0302</td><td>0.0865</td><td>0.0286</td><td>0.0420</td><td>0.0326</td><td>0.0565</td></tr><tr><td>PERSONA4Rec (vanilla)</td><td>0.0668</td><td>0.0389</td><td>0.0457</td><td>0.1007</td><td>0.0433</td><td>0.0567</td><td rowspan="2">|</td><td>0.0464</td><td>0.0678</td></tr><tr><td>PERSONA4Rec (fine-tuned)</td><td> $\underline{0.0707}^{*}$ </td><td> $\underline{0.0385}$ </td><td> $\underline{0.0464}$ </td><td> $\underline{0.1081}^{*}$ </td><td> $\underline{0.0434}$ </td><td> $\underline{0.0585}^{*}$ </td><td> $\underline{0.0460}$ </td><td> $\underline{0.0679}$ </td></tr><tr><td rowspan="6">LightGCN</td><td>-</td><td>0.0671</td><td>0.0353</td><td>0.0432</td><td>0.1071</td><td>0.0406</td><td>0.0561</td><td></td><td>0.0440</td><td>0.0681</td></tr><tr><td>ZS-LLM</td><td>0.0673</td><td>0.0364</td><td>0.0440</td><td>0.1071</td><td>0.0417</td><td>0.0568</td><td>|</td><td>0.0450</td><td>0.0690</td></tr><tr><td>TALLRec</td><td>0.0365</td><td>0.0166</td><td>0.0215</td><td>0.0716</td><td>0.0211</td><td>0.0327</td><td rowspan="2">0.1555</td><td>0.0265</td><td>0.0534</td></tr><tr><td>EXP3RT</td><td>0.0455</td><td>0.0213</td><td>0.0273</td><td>0.0828</td><td>0.0262</td><td>0.0392</td><td>0.0311</td><td>0.0574</td></tr><tr><td>PERSONA4Rec (vanilla)</td><td>0.0696</td><td>0.0401</td><td>0.0474</td><td>0.1055</td><td>0.0449</td><td>0.0590</td><td rowspan="2">|</td><td> $\underline{0.0483}$ </td><td> $\underline{0.0716}$ </td></tr><tr><td>PERSONA4Rec (fine-tuned)</td><td> $\underline{0.0757}^{*}$ </td><td> $\underline{0.0410}$ </td><td> $\underline{0.0495}^{*}$ </td><td> $\underline{0.1151}^{*}$ </td><td> $\underline{0.0462}^{*}$ </td><td> $\underline{0.0622}^{*}$ </td><td> $\underline{0.0491}^{*}$ </td><td> $\underline{0.0726}^{*}$ </td></tr><tr><td rowspan="12">Yelp</td><td rowspan="6">BPR-MF</td><td>-</td><td>0.0334</td><td>0.0157</td><td>0.0200</td><td> $\underline{0.0557}$ </td><td>0.0186</td><td>0.0272</td><td></td><td>0.0213</td><td>0.0370</td></tr><tr><td>ZS-LLM</td><td>0.0285</td><td>0.0132</td><td>0.0169</td><td> $\underline{0.0499}$ </td><td>0.0160</td><td>0.0238</td><td>|</td><td>0.0191</td><td>0.0351</td></tr><tr><td>TALLRec</td><td>0.0278</td><td>0.0125</td><td>0.0162</td><td>0.0537</td><td>0.0159</td><td>0.0245</td><td rowspan="2">0.0949</td><td>0.0187</td><td>0.0349</td></tr><tr><td>EXP3RT</td><td>0.0265</td><td>0.0110</td><td>0.0148</td><td>0.0516</td><td>0.0141</td><td>0.0227</td><td>0.0171</td><td>0.0336</td></tr><tr><td>PERSONA4Rec (vanilla)</td><td>0.0349</td><td>0.0175</td><td>0.0217</td><td>0.0555</td><td>0.0201</td><td>0.0283</td><td rowspan="2">|</td><td>0.0228</td><td>0.0382</td></tr><tr><td>PERSONA4Rec (fine-tuned)</td><td> $\underline{0.0351}^{*}$ </td><td> $\underline{0.0181}^{*}$ </td><td> $\underline{0.0223}^{*}$ </td><td> $\underline{0.0599}^{*}$ </td><td> $\underline{0.0214}^{*}$ </td><td> $\underline{0.0303}^{*}$ </td><td> $\underline{0.0238}^{*}$ </td><td> $\underline{0.0391}^{*}$ </td></tr><tr><td rowspan="6">LightGCN</td><td>-</td><td>0.0388</td><td>0.0195</td><td>0.0242</td><td> $\underline{0.0682}$ </td><td>0.0233</td><td> $\underline{0.0336}$ </td><td></td><td>0.0258</td><td>0.0430</td></tr><tr><td>ZS-LLM</td><td> $\underline{0.0398}$ </td><td> $\underline{0.0201}$ </td><td> $\underline{0.0249}$ </td><td> $\underline{0.0664}$ </td><td> $\underline{0.0236}$ </td><td> $\underline{0.0334}$ </td><td>|</td><td> $\underline{0.0262}$ </td><td> $\underline{0.0432}$ </td></tr><tr><td>TALLRec</td><td>0.0325</td><td>0.0147</td><td>0.0191</td><td>0.0616</td><td> $\underline{0.0185}$ </td><td>0.0284</td><td rowspan="2">0.0106</td><td> $\underline{0.0215}$ </td><td> $\underline{0.0394}$ </td></tr><tr><td>EXP3RT</td><td>0.0292</td><td>0.0125</td><td>0.0166</td><td>0.0561</td><td>0.0160</td><td>0.0252</td><td>0.0193</td><td>0.0376</td></tr><tr><td>PERSONA4Rec (vanilla)</td><td>0.0351</td><td>0.0180</td><td>0.0222</td><td>0.0595</td><td>0.0211</td><td>0.0300</td><td rowspan="2">|</td><td>0.0242</td><td>0.0416</td></tr><tr><td>PERSONA4Rec (fine-tuned)</td><td> $\underline{0.0395}$ </td><td> $\underline{0.0199}$ </td><td> $\underline{0.0247}$ </td><td> $\underline{0.0694}$ </td><td> $\underline{0.0238}$ </td><td> $\underline{0.0343}$ </td><td> $\underline{0.0264}$ </td><td> $\underline{0.0436}$ </td></tr></table>

<sub>•</sub> RQ4 (Efect of Multi-Persona Modeling): <sub>How</sub> <sub>well</sub> <sub>does</sub> modeling multiple personas per item capture diverse and fine grained user motivations for engagement?

## 4.1 Experimental Settings

4.1.1 Datasets. To evaluate the efectiveness and robustness of Persona4Rec across domains, we experiment with two real-world datasets: <sup>Amazon-Books</sup> [12] and <sup>Yelp</sup>.<sup>4</sup>

• <sup>Amazon-Books</sup>: We use the Books category from the Amazon Reviews 2023 dataset [12]. The dataset provides user ratings on a 1-5 scale, along with textual reviews and metadata.

• <sup>Yelp</sup>: We focus on the restaurant and food categories in the Philadelphia region. Similar to Amazon-Books, it provides user ratings on a 1-5 scale, textual reviews, and metadata.

Following established practices in LLM-based recommendation [2, 15, 16, 47], we subsample approximately 100K-300K interactions to manage the computational cost of LLM-based methods, and apply both metadata and 5-core filtering to ensure data quality. The detailed statistics are summarized in Table 3 and Figure 3.

4.1.2 Baselines. For the top-<sup>??</sup> item recommendation task, we adopt a multi-stage ranking pipeline, where an initial candidate set is generated by a first-stage retriever and subsequently refined by a second-stage reranker. Within this framework, our main baselines are <sup>LLM-based</sup> <sup>rerankers</sup>, which directly apply LLMs during inference to reorder candidates. We compare Persona4Rec against two widely adopted LLM-based rerankers, ZS-LLM [37] and TALL-Rec [2], as well as the recent state-of-the-art method EXP3RT [16]. <sub>For</sub> <sub>the</sub> first-stage candidate retrievers<sub>,</sub> <sub>we</sub> <sub>use</sub> <sub>CF</sub> <sub>models</sub> <sub>includ-</sub> ing BPR-MF [34] and LightGCN [9]. Additionally, for explainability <sub>comparison,</sub> <sub>we</sub> <sub>include</sub> <sub>two</sub> review-based rationale generators<sub>:</sub> XRec [27] and EXP3RT [16].

4.1.3 Evaluation Protocol. For our main evaluation, we focus on the top-<sup>??</sup> reranking task and report HR@<sup>??</sup>, MRR@<sup>??</sup>, and NDCG@<sup>??</sup>. for <sup>??</sup> = {5<sup>,</sup> 10<sup>,</sup> 20} as the evaluation metric, following the established practices in previous work [16, 47]. We adopt leave-one-out (LOO) splitting for train/validation/test [36, 47, 53].

4.1.4 Implementation Details. Following the existing convention of constructing user profile [2], we set history length <sup>??</sup> = 10, and gamma is set through validation. For encoder training, we fine-tune the BGE-M3 [5] model using LoRA [14] with rank <sup>??</sup> = 16, alpha <sup>??</sup> = 32, and dropout 0<sup>.</sup>05. We use a global batch size of 72 and learning rate of $\bar { 1 } \times 1 0 ^ { - 5 }$ across all experiments.

## 4.2 RQ1: Reranking Performance

We first examine whether Persona4Rec can efectively enhance top-<sup>??</sup> recommendation accuracy when used to rerank candidates produced by CF models, to verify that shifting reasoning ofline does not compromise ranking quality.

4.2.1 Overall Performance. Table 4 shows Persona4Rec consistently outperforms CF generators and LLM-based rerankers across datasets. Notably, LLM-based rerankers struggle under real-world data conditions, with some falling behind CF generators due to dataset-specific limitations. In Amazon-Books, extreme rating skew toward 5-stars (Figure 3) undermines EXP3RT; when most items share similar ratings, rating-based reasoning loses discriminative power. On the other hand, ZS-LLM’s generic prompting and TALL Rec’s instruction-tuned approach fail to capture nuanced collaborative patterns. In Yelp, rating skew is less extreme than Amazon-Books but still exhibits significant imbalance (Figure 3). When this unbalanced distribution is combined with sparse metadata (e.g., “WiFi available,” “child-friendly”), it provides insuficient diferentiation for reasoning-based methods.

Table 5: Reranking performance across cold-start and warm-start scenarios on Amazon-Books dataset, with relative improvements (%) over CF baseline, denoted by “-”. (<sub>∗</sub>: p-value < 0.05)

<table><tr><td rowspan="2">Generator</td><td rowspan="2">Reranker</td><td colspan="2">Warm Users@10</td><td colspan="2">Cold Users@10</td><td colspan="2">Head Items@10</td><td colspan="2">Tail Items@10</td></tr><tr><td>HR</td><td>NDCG</td><td>HR</td><td>NDCG</td><td>HR</td><td>NDCG</td><td>HR</td><td>NDCG</td></tr><tr><td rowspan="6">BPR-MF</td><td>-</td><td>0.0469</td><td>0.0236</td><td>0.1380</td><td>0.0757</td><td>0.1662</td><td>0.0868</td><td>0.0310</td><td>0.0185</td></tr><tr><td>ZS-LLM</td><td>0.0490</td><td>0.0251</td><td>0.1409</td><td>0.0778</td><td>0.1696</td><td>0.0897</td><td>0.0323</td><td>0.0191</td></tr><tr><td>TALLRec</td><td>0.0451</td><td>0.0216</td><td>0.0749</td><td>0.0333</td><td>0.1120</td><td>0.0530</td><td>0.0160</td><td>0.0076</td></tr><tr><td>EXP3RT</td><td>0.0486</td><td>0.0236</td><td>0.1109</td><td>0.0528</td><td>0.1457</td><td>0.0683</td><td>0.0268</td><td>0.0160</td></tr><tr><td>PERSONA4Rec (ours)</td><td>0.0599*</td><td>0.0320*</td><td>0.1432</td><td>0.0789</td><td>0.1707</td><td>0.0904</td><td>0.0360*</td><td>0.0196</td></tr><tr><td>improv. over BPR-MF</td><td>+27.7%</td><td>+35.6%</td><td>+3.8%</td><td>+4.2%</td><td>+2.7%</td><td>+4.1%</td><td>+16.1%</td><td>+5.9%</td></tr><tr><td rowspan="6">LightGCN</td><td>-</td><td>0.0552</td><td>0.0267</td><td>0.1479</td><td>0.0782</td><td>0.1671</td><td>0.0858</td><td>0.0383</td><td>0.0225</td></tr><tr><td>ZS-LLM</td><td>0.0536</td><td>0.0273</td><td>0.1474</td><td>0.0803</td><td>0.1658</td><td>0.0858</td><td>0.0385</td><td>0.0235</td></tr><tr><td>TALLRec</td><td>0.0462</td><td>0.0213</td><td>0.0841</td><td>0.0363</td><td>0.1124</td><td>0.0519</td><td>0.0235</td><td>0.0106</td></tr><tr><td>EXP3RT</td><td>0.0445</td><td>0.0211</td><td>0.1049</td><td>0.0495</td><td>0.1295</td><td>0.0591</td><td>0.0330</td><td>0.0170</td></tr><tr><td>PERSONA4Rec (ours)</td><td>0.0621*</td><td>0.0328*</td><td>0.1545*</td><td>0.0850*</td><td>0.1697*</td><td>0.0905*</td><td>0.0455*</td><td>0.0233</td></tr><tr><td>improv. over LightGCN</td><td>+12.5%</td><td>+22.8%</td><td>+4.5%</td><td>+8.7%</td><td>+1.6%</td><td>+5.5%</td><td>+18.8%</td><td>+3.6%</td></tr></table>

Table 6: Simulating items without reviews on Amazon-Books. Results at @10 with relative improvement over CF baseline.

<table><tr><td>Generator</td><td>Reranker</td><td>HR</td><td>NDCG</td></tr><tr><td rowspan="3">BPR-MF</td><td>-</td><td>0.1000</td><td>0.0531</td></tr><tr><td>Summary Only</td><td> $\underline{0.1043 (+4.3\%)}$ </td><td> $\underline{0.0560 (+5.5\%)}$ </td></tr><tr><td>Full (Ours)</td><td> $\underline{0.1081 (+8.1\%)}$ </td><td> $\underline{0.0585 (+10.2\%)}$ </td></tr><tr><td rowspan="3">LightGCN</td><td>-</td><td>0.1071</td><td>0.0561</td></tr><tr><td>Summary Only</td><td> $\underline{0.1112 (+3.8\%)}$ </td><td> $\underline{0.0591 (+5.3\%)}$ </td></tr><tr><td>Full (Ours)</td><td> $\underline{0.1151 (+7.5\%)}$ </td><td> $\underline{0.0622 (+10.9\%)}$ </td></tr></table>

Persona4Rec overcomes these limitations by extracting personas primarily from review contents rather than focus on metadata or ratings. While LLM rerankers are afected by noisy raw metadata for reasoning, we refine this noisy metadata into structured summaries. This refinement process provides more objective and dense information for constructing personas, even when metadata is sparse. Besides, even though ratings are skewed, personas can capture diverse aspects from review semantics. This allows our model to avoid the loss of discriminative power that hinders rating based reasoning approaches. Beyond this textual refinement, our framework learns to align user interaction histories with these per sonas through contrastive learning, enabling the model to capture implicit behavioral preferences. This alignment process allows the encoder to recognize subtle preference patterns embedded in users’ actual engagement histories. This synergy between semantic understanding and behavioral alignment ensures robust and reliable performance even under challenging data conditions. Even without fine-tuning, the vanilla variant with pre-trained BGE-M3 outperforms LLM baselines, validating the efectiveness of our personabased textual refinement. Fine-tuning adds further gains by learning from interaction patterns through user-persona alignment training.

4.2.2 Cold-/Warm-start Scenario Analysis. We partition test interactions by review count into user/item segments to test robustness under sparsity (warm/head: top 20%, cold/tail: bottom 20%). As shown in Table 5, Persona4Rec exhibits gains across all regimes. Tail items deliver the suitable gains. <sub>These</sub> <sub>items</sub> <sub>remain</sub> <sub>sparsely</sub> connected within the dataset, causing CF generators to produce unreliable rankings from weak collaborative patterns. In contrast, Persona4Rec infers structured personas from the available reviews—even when reviews are few, they provide richer semantic signals than interaction counts alone. This review-grounded evidence enables robust reranking where CF struggles most.

Warm users show strong relative improvements. <sub>Despite</sub> <sub>start-</sub> ing from low baseline performance, warm users achieve substantial relative gains. This suggests that persona-based matching provides significant value when users have extensive histories, as richer context enables alignment with more specialized personas that capture preference nuances invisible to collaborative filtering.

Head items show modest gains. Two factors may contribute to this ceiling. First, abundant interactions enable CF to learn robust patterns, reducing the marginal value of semantic augmentation. Second, popular items often exhibit broader preference diversity than what our current persona generation framework can capture. Although Persona4Rec limits each item to a maximum of seven personas for computational eficiency, highly reviewed items might benefit from a more fine-grained representation.

Cold users show moderate improvements. <sub>Cold</sub> <sub>users</sub> <sub>exhibit</sub> smaller relative improvements as sparse histories limit coherent preference profiling—especially when consuming popular items with generic taste signals. In contrast, warm users’ extensive histories reveal consistent patterns (e.g., recurring themes, quality criteria) enabling precise alignment with specialized personas. This confirms that persona semantics provide value across sparsity levels, but optimal matching requires suficient interaction data.

Table 7: Comparison of inference eficiency between LLM based rerankers and Persona4Rec. Latency for ZS-LLM is measured as end-to-end API latency.

<table><tr><td>Method</td><td>Inference Latency (ms)</td><td>Memory Footprint (GB)</td></tr><tr><td>ZS-LLM</td><td> $5,537 \pm 3,094.13$ </td><td>-</td></tr><tr><td>TALLRec</td><td> $979.17 \pm 13.29$ </td><td>12.57</td></tr><tr><td>EXP3RT</td><td> $77,974.08 \pm 1,229.99$ </td><td>14.96</td></tr><tr><td rowspan="2">PERSONA4Rec</td><td> $0.52 \pm 0.01$  (CPU)</td><td>-</td></tr><tr><td> $0.75 \pm 0.02$  (GPU)</td><td>0.1</td></tr></table>

![](images/5be07f05bbed8f13e75342cd79b445f180fb7e0db3da0ab59e93f048d046abff.jpg)

![](images/67afea5372933cc039f5d7463b6b00c18daa4385fc7f10494d70fc8883491fa5.jpg)  
Figure 4: Comparison of inference scalability with respect to the number of user samples and candidate items.

4.2.3 Robustness to Missing Reviews. A common limitation of reviewbased methods is their inability to handle items lacking reviews, which frequently occurs for newly listed items in real-world plat forms. To evaluate robustness when items have metadata but no reviews yet, we simulate this by using the same trained encoder but indexing items with their summary $e _ { i } = E _ { \theta } { \bigl ( } s _ { i } { \bigr ) }$ instead of personas (Summary Only). As shown in Table 6, this variant still outper forms the CF baseline across all settings, demonstrating that our framework can efectively serve cold-start items before reviews accumulate, as the encoder has already learned summary seman tics through user profiles during training. When reviews become available, the Full model yields additional gains, confirming the complementary value of review-grounded persona reasoning.

Overall, Persona4Rec demonstrates robust improvements across all data —including complete cold-start scenarios where no reviews are available—confirming our method efectively complements CFbased candidate generation under diverse conditions.

## 4.5 RQ4: Efect of Multi-Persona Modeling

We now examine how the number of personas per item (<sup>??</sup>) influ ences both the quality of the constructed personas and their impact on recommendation performance. Specifically, we analyze whether increasing <sup>??</sup> enhances the faithfulness and clarity of personas and leads to greater improvements in recommendation accuracy.

4.5.1 Efect of the Number of Personas on Quality. We compare Single-Persona (one aggregated persona) with Multi-Persona (our de fault, $K \in [ 2 , 7 ] )$ using human evaluation on five criteria. We adopt these five criteria that cover the key aspects of persona quality in the construction stage: Faithfulness, Clarity, Coverage, Interpretability, and Representativeness. (Refer to Table 9 for more details.)

![](images/c838a75d292817840b8c9be2ba860f01e74929a44a4f098a6b0ccbbaf69e2ae5.jpg)  
Figure 6: Human evaluation on the persona construction quality in single- and multi-persona. (<sub>∗</sub>: p-value < 0.05)

Table 10: Impact of the number of generated personas per item with BPR-MF in Amazon-Books.

<table><tr><td rowspan="2"># Personas</td><td colspan="2">@5</td><td colspan="2">@10</td><td colspan="2">@20</td></tr><tr><td>HR</td><td>NDCG</td><td>HR</td><td>NDCG</td><td>HR</td><td>NDCG</td></tr><tr><td>1</td><td>0.0488</td><td>0.0301</td><td>0.0824</td><td>0.0408</td><td rowspan="2">|</td><td>0.0507</td></tr><tr><td>3</td><td>0.0519</td><td>0.0322</td><td>0.0835</td><td>0.0423</td><td>0.0520</td></tr><tr><td>5</td><td>0.0532</td><td>0.0335</td><td>0.0843</td><td>0.0435</td><td rowspan="2">0.1212</td><td>0.0529</td></tr><tr><td>7</td><td>0.0541</td><td>0.0338</td><td>0.0848</td><td>0.0437</td><td>0.0530</td></tr></table>

As shown in Figure 6, Multi-persona generation achieved substantially higher scores across all five evaluation criteria, with improvements of over 30 percentage points in faithfulness and interpretability. These results confirm that aggregating all signals into a single persona leads to oversimplification and loss of nuance, whereas modeling items with multiple distinct personas provides more consistent and specific rationales that better reflect heterogeneous user motivations.

4.5.2 Efect of the Number of Personas on Performance. Moreover, to evaluate how the number of personas per item influences recommendation performance, we design an ablation study on the Amazon-Books dataset using BPR-MF as the candidate generator. For each item, we vary the number of generated personas (1, 3, 5, and 7) and use them for reranking evaluation, reporting HR and NDCG at cutof levels. This experiment is conducted on the 13,302 users whose candidate item persona pool contains exactly seven personas. By restricting evaluation to this setting, we can directly compare the impact of the number of personas (1–7) while keeping the candidate pool consistent. As shown in Table 10, increasing the number of personas consistently improves ranking performance, with the best results observed at 7 personas. Even a moderate number of personas (e.g., 5 personas) yields steady gains, demonstrating that representing items with multiple distinct personas is more effective than compressing all review signals into a single aggregated profile. Overall, these findings suggest that <sup>multi-persona</sup> <sup>gener-</sup> ation provides a finer-grained profiling of user motivations<sub>,</sub> capturing both majority and minority perspectives. This richer representation not only improves ranking metrics but also enhances the explainability of recommendations by reflecting diverse user preferences across heterogeneous groups.

## 5 Conclusion

This work introduced Persona4Rec, a novel recommendation framework that shifts online LLM reasoning to the ofline by constructing diverse review-grounded item personas. By reframing recommen dation as a user-persona alignment task trained on LLM-derived supervision, it enables real-time inference with lightweight encoder scoring while naturally providing interpretable explanations. Exten sive experiments show that Persona4Rec consistently outperforms state-of-the-art LLM-based rerankers, achieving robust gains for cold users and tail items while reducing inference latency by orders of magnitude. Overall, Persona4Rec ofers a practical and scal able solution bridging eficiency, accuracy, and interpretability, and paves the way for extending persona-based alignment to richer user feedback and hybrid reasoning framework that combines ofline knowledge construction with adaptive online refinement.

[已省略: references]


---

## 📑 关键章节 | VRAgent-R1: Boosting Video Recommendation with MLLM-based Agents via Reinforcement Learning

**arXiv ID**: [2507.02626](https://arxiv.org/abs/2507.02626)

## 1 Introduction

With the widespread adoption of online multimedia services, particularly the booming popularity of short video platforms like TikTok and Kuaishou, Multimodal Recommendation Systems (MRS) have attracted considerable attention from both academia and industry. Unlike conventional recommendation technologies [1, 2, 3, 4, 5] that rely on ID-based user/item representation learning, MRS focuses on effectively integrating data associated with items from diverse modalities, such as text, images, videos, and audio, which aims to offer more personalized recommendations by deep semantic understanding of item and user characteristics. However, in video recommendations, existing approaches predominantly construct item representations based on text and images due to challenges in computational efficiency and processing heterogeneous information across modalities, the full potential of multimodal information in video recommendation systems remains largely unexplored.

![](images/834c0899f148f71a3126fc2ce555133d00980bf45b67fb9f83d5eff875633ad1.jpg)  
Figure 1: Qualitative examples of VRAgent-R1 for Video Recommendation. Our VRAgent-R1 stands out from previous supervised fine-tuning of MLLM, which fails to give the correct prediction due to the lack of understanding of video items and deep thinking on user status.

Benefiting from the significant advancements in Multimodal Large Language Models (MLLMs), recent studies tend to utilize their strengths and potential to boost multimodal recommendation systems. On one hand, some approaches [6, 7, 8, 9, 10, 11, 12, 13] leverage the pre-trained MLLMs to directly convert each item’s multimodal information into a single embedding. However, fine-tuning MLLMs and achieving semantic alignment for recommendation requires abundant high-quality interaction data and computational resources. On the other hand, some methods [14, 15, 16, 17] directly apply LLMs or MLLMs to recommendation tasks, transforming the recommendation into a language generation problem. For instance, by analyzing user interaction history, item descriptions, or conversational context, LLMs perform in-depth inference to generate recommendation results. While effective in addressing the data sparsity issue, these methods often face challenges such as limited input length, computational inefficiency, and hallucinations, making them unsuitable for large-scale recommendations. Recently, growing attention has been paid to using LLM-based agents to enhance recommendation systems’ personalization and intelligence (e.g., user profiling, simulating interactions, improving satisfaction). However, existing methods [18, 14, 19] mostly use frozen LLMs, with the knowledge gap between vertical domains and LLMs/MLLMs limiting their adaptability and effectiveness.

Based on the above discussion, we propose to use LLMs/MLLMs to attain enhanced multimodal content comprehension and simulate user decision-making. Our objective is to optimize representation learning and human-centric recommendation outcomes, so as to align with real user preferences. In order to realize satisfactory MLLM-based user simulation for video recommendation, we are required to address the following challenges. 1) How to discriminately exploit the recommendationrelevant semantics hidden in video items? Most video recommendation systems heavily rely on understanding video items, which presents two major difficulties. Firstly, previous methods ignore the temporal relation within video frames and fail to identify key information among numerous contents. For example, some methods [20, 21] directly use randomly selected, pre-processed visual features, while MLLM-MSR [15] only takes the first image for video modeling, all of which fail to effectively utilize the characteristics of videos. Secondly, previous methods process each modality independently and conduct late feature fusion, which faces the problem of modality competition [22, 23], even leading to inferior performance compared to using a single modality [24]. Additionally, the lack of in-depth semantic interaction between raw modalities may also cause a misunderstanding of the high-level semantics of the video. As shown in Fig. 3 (a), (b), these methods merely obtain superficial modality embeddings while failing to identify the political topics expressed in the video. 2) How to effectively simulate user behavior that mirrors human deep thinking? LLMs show great promise for user simulation in the recommendation systems [18, 17, 14, 25] due to their excellent linguistic understanding capabilities. However, existing LLMs struggle with processing sequential multimodal inputs, which prevents direct modeling of multimodal user behavior sequences. Moreover, most user simulators [18, 14, 17, 19] primarily rely on prompt engineering to instruct frozen LLMs to generate responses without feedback, potentially leading to discrepancies between the agent and real user behavior when the model cannot be optimized. Some methods [16, 15] attempt to fine-tune the large model, but simple fine-tuning only yields binary ‘Yes’ or ‘No’ judgments without deep analysis of the user’s status, thus limiting the model’s generalizability as shown in Fig. 1.

![](images/16151b33e82469d61dfda53e94427927299cbfc5c5c0315c3ded72d94a690514.jpg)  
Figure 2: Overview of our VRAgent-R1 framework. We propose a framework with two novel agents for better video recommendation. The IP Agent conducts collaborative multimodal understanding to obtain enhanced video features for the recommendation system and the US Agent. Meanwhile, the US Agent simulates user behavior via deep CoT reasoning based on user status. By reinforcement learning with actual behavior rewards, VRAgent-R1 achieves superior simulation performance and helps improve the recommendation accuracy.

To address the aforementioned challenges, we introduce VRAgent-R1, a novel agent-based paradigm for video recommendation. Unlike prior approaches built on frozen LLMs, VRAgent-R1 effectively mimics the human-like thinking for recommendation by leveraging multimodal collaborative understanding and reinforcement fine-tuning (RFT) on user simulation. Specifically, it consists of two distinct agents: the Item Perception (IP) Agent and the User Simulation (US) Agent. As illustrated in Fig. 2, The IP Agent aims to establish comprehensive multimodal content understanding for videos to improve item modeling through multi-round, in-depth semantic interaction with the MLLM. This process enables it to progressively discover key video content and effectively extract recommendation-relevant semantics from the items. Subsequently, the semantic summarization of videos generated by the IP Agent is used to optimize the fundamental video recommendation model via feature augmentation. This not only enhances the recommendation model but also facilitates the US Agent to capture user preferences and predict the next item based on historical interactions. The US Agent focuses on deep user behavior simulation and provides proxy feedback to refine the candidate set provided by the video recommendation system. To align user simulation with real decision-making, reinforcement learning is leveraged to enable the model to analyze historical user behavior (watched videos and comments) and comprehensively summarize user status with Chain-of-Thought (CoT) reasoning. Additionally, we design a reward mechanism associated with the user’s actual final behavior and update the fundamental LLM through policy optimization, i.e., GRPO [26]. Through the collaboration of IP and US agents, VRAgent-R1 effectively boosts video recommendation performance with step-by-step human-like thinking. The main contributions of this work can be summarized as follows:

• We propose VRAgent-R1, a novel agent-based framework designed to assist video recommendations from a user-centric perspective, which exhibits human-like intelligence for interpretable recommendations. By incorporating a user-like understanding, this framework significantly enhances the performance of recommendation system, demonstrating the effectiveness of the pipeline.

• Our IP Agent achieves more comprehensive multimodal understanding of videos by flexibly conducting in-depth semantic interactions between textual and visual contents. Furthermore, our US Agent is the first to use RFT for LLM-based user simulation, achieving more accurate simulation performance through deep thinking on user status with little training data.

• Extensive experiments demonstrate that the IP Agent significantly enhances the performance of existing video recommendation approaches, achieving a 4.3% improvement in HR@10 and a 6.0% improvement in NDCG@10 on the MicroLens-100k dataset [21]. Meanwhile, the US Agent outperforms commercial models such as GPT-4o [27] and SFT methods, attaining an accuracy of 64.1% in user simulation for next video selection, which represents a 45.0% enhancement over the

SFT baseline. Moreover, simulated user feedback can further boost the recommendation accuracy by reranking the candidate item set generated from the recommendation system.

[已省略: 2 related work]

## 3 Method

As shown in Fig. 2, our VRAgent-R1 framework mainly consists of two components: the Item Perception Agent (IP Agent) for video modeling and the User Simulation Agent (US Agent) for user modeling. In the following sections, we will detail how each agent works and how they collaborate to achieve better user simulation.

## 4 Experiments

Datasets and Metrics. We have conducted extensive experiments on MicroLens-100K [21], an open-source, real-world video recommendation dataset that includes 100,000 users, 19,738 items, and 719,405 interactions, with a sparsity level of 99.96%. Notably, MicroLens is the first micro-video recommendation dataset to provide original video content, which enables us to analyze videos from raw frames. The average video duration is 161 seconds, featuring rich visual content. For traditional recommendation metrics across the entire dataset, we report standard recommendation metrics such as HR@10, NDCG@10, HR@20, and NDCG@20. For the evaluation of user behavior simulation, we report binary classification metrics such as accuracy (Acc) and F1 Score for preference judgment, as well as selection accuracy for next video selection.

Table 1: Comparison results on MicroLens-100K. The fusion of different modality features is achieved by weighted pooling. The underline T, I, V, F correspond to text, image, video, and fusion features, respectively. Our MLLM-enhanced features successfully boost the performance of different traditional sequence recommendation methods.

<table><tr><td>Class</td><td>Model</td><td>HR@10</td><td>NDCG@10</td><td>HR@20</td><td>NDCG@20</td></tr><tr><td rowspan="3">IDRec(CF)</td><td>DSSM [42]</td><td>0.0394</td><td>0.0193</td><td>0.0654</td><td>0.0258</td></tr><tr><td>LightGCN [43]</td><td>0.0372</td><td>0.0177</td><td>0.0618</td><td>0.0239</td></tr><tr><td>DeepFM [44]</td><td>0.0350</td><td>0.0170</td><td>0.0571</td><td>0.0225</td></tr><tr><td rowspan="3">IDRec(SR)</td><td>NextItNet [45]</td><td>0.0805</td><td>0.0442</td><td>0.1175</td><td>0.0535</td></tr><tr><td>GRU4Rec [46]</td><td>0.0782</td><td>0.0432</td><td>0.1147</td><td>0.0515</td></tr><tr><td>SASRec [47]</td><td>0.0909</td><td>0.0517</td><td>0.1278</td><td>0.0610</td></tr><tr><td rowspan="5">Modality</td><td> $NextItNet_V$ [21]</td><td>0.0862</td><td>0.0466</td><td>0.1246</td><td>0.0562</td></tr><tr><td> $SASRec_T$ [21]</td><td>0.0916</td><td>0.0490</td><td>0.1343</td><td>0.0598</td></tr><tr><td> $SASRec_I$ [21]</td><td>0.0942</td><td>0.0511</td><td>0.1358</td><td>0.0613</td></tr><tr><td> $SASRec_V$ [21]</td><td>0.0948</td><td>0.0515</td><td>0.1364</td><td>0.0619</td></tr><tr><td> $SASRec_F$ [21]</td><td>0.0953</td><td>0.0517</td><td>0.1362</td><td>0.0623</td></tr><tr><td rowspan="3">MLLM Enhanced</td><td>SASRec [47]+MLLM-MSR [15]</td><td>0.0606</td><td>0.0351</td><td>0.0911</td><td>0.0446</td></tr><tr><td>NextItNet [45]+Ours</td><td>0.0884</td><td>0.0478</td><td>0.1278</td><td>0.0583</td></tr><tr><td>SASRec [47]+Ours</td><td>0.0994+4.30%</td><td>0.0548+6.00%</td><td>0.1418+3.96%</td><td>0.0655+5.14%</td></tr></table>

![](images/05798eb0b695f4dc6aecf86331ede08e690185340b739fcf93a8c3b6286dbf0a.jpg)

![](images/f791ea42ef7d73059b8ba4de0156c6a368ef6fdf34478a2da606e5bf16aacab5.jpg)  
Figure 4: User Group Performance. Our method has a great advantage in modeling cold-start users due to the good multimodal understanding, outperforming the baseline by more than 10%.

Implementation Details. We employ Qwen2.5-7b [41] for both the IP Agent and the US Agent. For video recommendation, we follow the official code of MicroLens-100K[21] benchmark for evaluation, and select the frames with the top 3 similarity scores generated by the IP Agent. In user simulation, we designate the actual last item of user behavior as the positive sample and employ SASRec [21] to generate the top 10 recommended items, from which m items are randomly chosen as negative samples to more accurately mimic real-world recommendation scenarios. We deploy 4 A100 80G GPUs for the reinforcement fine-tuning of the US Agent using information from 2000 users. The training configuration includes a batch size of 16, 16 sampled policy rollouts, and a KL coefficient of 0.001. We set the maximum number of input and response tokens to 2048 and train the model for 4 epochs, which takes approximately 10 hours. User simulation evaluation is conducted on 1000 randomly selected cold-start users and repeated three times to report the average performance. The specific prompts used for instructing models are detailed in Appendix A.1.

## 4.1 Performance Comparison for Video Recommendation

In this section, we evaluate the effectiveness of our IP Agent on the video recommendation baseline, following the experimental protocols in MicroLens [21]. We use the MLLM to generate outputs for collaborative reasoning and understanding, thereby enhancing the content of the original titles. As shown in Table 1, sequential recommendation models that incorporate multimodal information outperform both Collaborative Filtering (CF) models and simple ID embedding-based models. How ever, traditional multimodal methods rely on late fusion techniques (e.g., addition or concatenation) of ID, textual, and visual embeddings. Due to the significant differences between modalities, such coarse-grained fusion fails to fully leverage multimodal information. Moreover, the lack of in-depth understanding of video frames means that these fusion methods only achieve similar performance to single-modality approaches. We also experiment with directly using the MLLM to generate a detailed caption for the cover image, as in MLLM-MSR [15]. However, these captions often focus on unimportant details in the image, failing to capture key information and leading to a significant decline in performance. In contrast, our IP Agent integrates the pre-trained world knowledge of the MLLM to collaboratively understand multimodal content. It summarizes key information in a brief and unified format, which helps to boost HR@10 and NDCG@10 by 4.3% and 6.0%, respectively, compared to previous state-of-the-art methods.

Table 2: Evaluation on User Simulation. Our RFT method outperforms previous prompt and SFT-based simulation, with less training data and higher accuracy. m is the number of negative samples, and SFT methods have higher Recall scores since they tend to give positive answers.

<table><tr><td>Method</td><td>Acc</td><td>Recall</td><td>Pre</td><td>F1</td><td> $\text{Acc}_{m=3}$ </td><td> $\text{Acc}_{m=4}$ </td></tr><tr><td>GPT-4o [27]</td><td>0.535</td><td>0.480</td><td>0.533</td><td>0.505</td><td>0.307</td><td>0.269</td></tr><tr><td>DeepSeek-R1 [34]</td><td>0.528</td><td>0.556</td><td>0.526</td><td>0.541</td><td>0.264</td><td>0.231</td></tr><tr><td>Qwen2.5-7b [41]</td><td>0.491</td><td>0.512</td><td>0.490</td><td>0.500</td><td>0.245</td><td>0.197</td></tr><tr><td>LLM_Simulator [14]</td><td>0.523</td><td>0.539</td><td>0.519</td><td>0.529</td><td>-</td><td>-</td></tr><tr><td>Agent4Rec [18]</td><td>0.528</td><td>0.482</td><td>0.52</td><td>0.501</td><td>-</td><td>-</td></tr><tr><td>TALLREC (SFT) [16]</td><td>0.537</td><td>0.913</td><td>0.521</td><td>0.663</td><td>-</td><td>-</td></tr><tr><td>MLLM-MSR (SFT) [15]</td><td>0.585</td><td>0.882</td><td>0.553</td><td>0.679</td><td>0.442</td><td>0.381</td></tr><tr><td>VRAgent-R1</td><td>0.715</td><td>0.760</td><td>0.697</td><td>0.727</td><td>0.641</td><td>0.602</td></tr></table>

Table 3: Preference evaluation comparison on MovieLens with our US Agents.

<table><tr><td>Method</td><td>Acc</td><td>Recall</td><td>Pre</td><td>F1</td></tr><tr><td>GPT-4o [27]</td><td>0.584</td><td>0.626</td><td>0.577</td><td>0.600</td></tr><tr><td>RecAgent [25]</td><td>0.581</td><td>0.639</td><td>0.604</td><td>0.621</td></tr><tr><td>Agent4Rec [18]</td><td>0.691</td><td>0.746</td><td>0.691</td><td>0.698</td></tr><tr><td>VRAgent</td><td>0.832</td><td>0.846</td><td>0.823</td><td>0.834</td></tr></table>

Table 4: Optimizing RSs with VRAgent-R1.

<table><tr><td rowspan="2">Method</td><td colspan="2">All</td><td colspan="2">Cold</td></tr><tr><td>HR@10</td><td>NDCG@10</td><td>HR@10</td><td>NDCG@10</td></tr><tr><td>Original</td><td>0.0916</td><td>0.0490</td><td>0.0586</td><td>0.0278</td></tr><tr><td>+IP Agent</td><td>0.0994</td><td>0.0548</td><td>0.0663</td><td>0.0318</td></tr><tr><td>+US dislike</td><td>0.0988</td><td>0.0543</td><td>0.0654</td><td>0.0311</td></tr><tr><td>+US like</td><td>0.1003</td><td>0.0554</td><td>0.0678</td><td>0.0330</td></tr></table>

Considering that our method establishes a comprehensive understanding of multimodal items, it should also be helpful in handling cold-start users. Accordingly, we evaluate the performance of different methods on cold-start users (i.e., users with no more than 5 interacted videos), as shown in Fig. 4. It is evident that the ID-based method suffers the most significant performance degradation for cold-start users, as it relies solely on ID embeddings without incorporating multimodal information. In contrast, our method demonstrates a clear advantage in modeling cold-start users, outperforming the baseline by more than 10%.

## 4.2 Evaluation on User Simulation

In this subsection, we assess the performance of VRAgent-R1 and other user simulators in accurately modeling user behavior through two tasks: user preference prediction (estimating whether a user will like recommended items) and next video selection (choosing the most likely video a user will click next from candidates). Tab. 2 presents the results comparing our method with commercial models (GPT-4o [27], DeepSeek-R1 [34]) and several user simulation baseline methods. As shown in the table, directly prompting frozen LLMs to summarize user preferences based on textual inputs and then predict the answer yields poor results. This is because these LLMs rely solely on limited information from video titles and suffer from serious hallucination problems, leading to performance only slightly better than random guessing. For the SFT methods, such as ALLREC [16] and MLLM-MSR [15], training the models to predict user behavior based on summarized user preferences shows improved performance after fine-tuning with an additional 20,000 users’ information. MLLM-MSR performs better due to the inclusion of extra cover image information, but the results are still unsatisfactory, and the final model can only provide binary answers ("Yes" or "No") without a reasoning process. On the contrary, our VRAgent-R1 method achieves significantly higher prediction accuracy, e.g.,

Table 5: Ablation on the IP Agent.

<table><tr><td>Method</td><td>HR@10</td><td>NDCG@10</td><td>HR@20</td><td>NDCG@20</td></tr><tr><td>Baseline</td><td>0.0916</td><td>0.0490</td><td>0.1343</td><td>0.0598</td></tr><tr><td>w/o KFR</td><td>0.0980</td><td>0.0542</td><td>0.1422</td><td>0.0646</td></tr><tr><td>w/o CMP</td><td>0.0960</td><td>0.0519</td><td>0.1398</td><td>0.0629</td></tr><tr><td>w/o RRA</td><td>0.0816</td><td>0.0466</td><td>0.1182</td><td>0.0523</td></tr><tr><td>VRAgent-R1</td><td>0.0994</td><td>0.0548</td><td>0.1448</td><td>0.0655</td></tr></table>

Table 6: Ablation on the US Agent.

<table><tr><td>Method</td><td>Acc</td><td>F1</td><td> $\text{Acc}_{m=3}$ </td><td> $\text{Acc}_{m=4}$ </td></tr><tr><td>Baseline</td><td>0.491</td><td>0.500</td><td>0.245</td><td>0.197</td></tr><tr><td>SFT</td><td>0.585</td><td>0.679</td><td>0.442</td><td>0.381</td></tr><tr><td>w/o CoT Reasoning</td><td>0.580</td><td>0.592</td><td>0.324</td><td>0.263</td></tr><tr><td>w/o Comment</td><td>0.695</td><td>0.705</td><td>0.618</td><td>0.577</td></tr><tr><td>w/o IP Agent</td><td>0.680</td><td>0.686</td><td>0.609</td><td>0.569</td></tr><tr><td>VRAgent-R1</td><td>0.715</td><td>0.727</td><td>0.646</td><td>0.602</td></tr></table>

about 45% higher for the next video selection than MLLM-MSR, despite using less training data. Additionally, our model can be applied to different reasoning tasks without losing generality.

To verify the effectiveness of our method across different domains, we conduct user preference simulation tests [18] on the widely used MovieLens-1M [48] dataset. Since the understanding of movie content in this dataset primarily relies on text descriptions, we evaluate the performance using only the US Agent, without involving the IP Agent for multimodal processing. The results in Tab. 3 indicate that in text-dominated movie recommendation scenarios, our approach also significantly outperforms previous simulation agents [25, 18]. More discussion could be referred in Appendix A.3.

## 5 Conclusion

In this paper, we propose a novel VRAgent-R1 framework for user simulation in video recommendation. It first utilizes an MLLM to collaboratively understand the retrieved multimodal content with pre-trained world knowledge, then analyzes the history sequence to establish user status and make final decision through RFT. By exploring different strategies and using real user decisions as verifiable rewards under different tasks, our VRAgent-R1 method achieves significant improvements in user behavior simulation for video recommendation. It outperforms SFT with minimal data and shows strong generalization. As a pioneering work, this study demonstrates the potential of applying RFT to LLMs in recommendation systems.

Limitations and Future Directions. Although the dataset used in this paper focuses on video recommendations, our VRAgent-R1 paradigm can be easily extended to various domains such as games, news, and e-commerce. Currently, the user action space in our experiments is relatively limited due to the dataset properties. In future work, we plan to explore adding more user behaviors, such as clicks and retention, to achieve more realistic user-system interactions. Moreover, verifying whether better user simulation feedback can further optimize existing recommendation systems is also a crucial direction for future exploration.

[已省略: references]

## A.3 Additional Experiment Discussion

Experiments on MovieLens. To verify the generality of our method in other domains, we also conduct user preference simulation tests on the widely used MovieLens-1M [48] dataset, which contains 1 million ratings from 6000 users on 4000 movies, and ratings above 3 are considered a positive like signal. Note that, though this dataset is related to movies, the understanding of movie contents mainly relies on text descriptions, while the visual information is not that important. Therefore, in this experiment, we only use the US Agent to do the evaluation, without considering the IP Agent for multimodal processing. We follow the setting of Agent4Rec [18], 1000 simulated users are randomly assigned 20 items, with varying ratios 1:m of positive and negative items. In our main paper, the reported results are all in a 1:1 ratio, here we also report the performance in 1:3 setting.

Table 8: Preference evaluation comparison on MovieLens with our US Agents.

<table><tr><td rowspan="2">Method</td><td colspan="4">1:1</td><td colspan="4">1:3</td></tr><tr><td>Acc</td><td>Recall</td><td>Pre</td><td>F1</td><td>Acc</td><td>Recall</td><td>Pre</td><td>F1</td></tr><tr><td>GPT-4o [27]</td><td>0.584</td><td>0.626</td><td>0.577</td><td>0.600</td><td>0.523</td><td>0.701</td><td>0.308</td><td>0.428</td></tr><tr><td>RecAgent [25]</td><td>0.581</td><td>0.639</td><td>0.604</td><td>0.621</td><td>0.508</td><td>0.740</td><td>0.399</td><td>0.518</td></tr><tr><td>Agent4Rec [18]</td><td>0.691</td><td>0.746</td><td>0.691</td><td>0.698</td><td>0.668</td><td>0.762</td><td>0.421</td><td>0.543</td></tr><tr><td>Ours</td><td>0.832</td><td>0.846</td><td>0.823</td><td>0.834</td><td>0.806</td><td>0.821</td><td>0.579</td><td>0.679</td></tr></table>

We can learn from the Tab. 8 that the user simulation results on MovieLens are better than those on MicroLens, indicating that the video recommendation task on MicroLens is more complex and challenging, where the multimodal information should be considered. And for textual dominated movie recommendation, our approach still has a great advantage compared with previous prompt-based simulation Agents [25, 18] like in Fig. 5, the prompt-based agents could not be optimized accordingly to recommendation, while our VRAgent-R1 learns to think deeply to simulate more realistic user behavior.

Statistical Significance For the video recommendation on MicroLens-100k, we follow the official implementation [21], with the IP Agent enhanced video understanding, we train the SASRec [47] with text information for three times, every time the test performance shows almost the same results, demonstrating the reproducibility of our experiments. For the user simulation, we use three random seeds to select 1000 cold-start users for evaluation, with 1-sigma error bars of 0.002, 0.005 for Acc and F1 in user performance judgment, 0.003 and 0.003 for $\mathrm { A c c } _ { m = 3 }$ and $\mathrm { A c c } _ { m = 4 }$ in next video selection. And the results consistently show that the performance of our method significantly outperforms previous agents (statistical tests using paired t-tests with 95% confidence intervals yield a p<0.002).

## 4. Experimental result reproducibility

Question: Does the paper fully disclose all the information needed to reproduce the main experimental results of the paper to the extent that it affects the main claims and/or conclusions of the paper (regardless of whether the code and data are provided or not)?

Answer: [Yes]

Justification: We have fully disclose all the information in experiment details.

Guidelines:

• The answer NA means that the paper does not include experiments.

• If the paper includes experiments, a No answer to this question will not be perceived well by the reviewers: Making the paper reproducible is important, regardless of whether the code and data are provided or not.

• If the contribution is a dataset and/or model, the authors should describe the steps taken to make their results reproducible or verifiable.

• Depending on the contribution, reproducibility can be accomplished in various ways. For example, if the contribution is a novel architecture, describing the architecture fully might suffice, or if the contribution is a specific model and empirical evaluation, it may be necessary to either make it possible for others to replicate the model with the same dataset, or provide access to the model. In general. releasing code and data is often one good way to accomplish this, but reproducibility can also be provided via detailed instructions for how to replicate the results, access to a hosted model (e.g., in the case of a large language model), releasing of a model checkpoint, or other means that are appropriate to the research performed.

• While NeurIPS does not require releasing code, the conference does require all submissions to provide some reasonable avenue for reproducibility, which may depend on the nature of the contribution. For example

(a) If the contribution is primarily a new algorithm, the paper should make it clear how to reproduce that algorithm.

(b) If the contribution is primarily a new model architecture, the paper should describe the architecture clearly and fully.

(c) If the contribution is a new model (e.g., a large language model), then there should either be a way to access this model for reproducing the results or a way to reproduce the model (e.g., with an open-source dataset or instructions for how to construct the dataset).

(d) We recognize that reproducibility may be tricky in some cases, in which case authors are welcome to describe the particular way they provide for reproducibility. In the case of closed-source models, it may be that access to the model is limited in some way (e.g., to registered users), but it should be possible for other researchers to have some path to reproducing or verifying the results.

## 6. Experimental setting/details

Question: Does the paper specify all the training and test details (e.g., data splits, hyperparameters, how they were chosen, type of optimizer, etc.) necessary to understand the results?

Answer: [Yes]

Justification: We specify the details in the experiments.

Guidelines:

• The answer NA means that the paper does not include experiments.

• The experimental setting should be presented in the core of the paper to a level of detail that is necessary to appreciate the results and make sense of them.

• The full details can be provided either with the code, in appendix, or as supplemental material.

## 7. Experiment statistical significance

Question: Does the paper report error bars suitably and correctly defined or other appropriate information about the statistical significance of the experiments?

Answer: [Yes]

Justification: The main table do not provide error bars since some results are from previous papers with no error bars, and some experiments may need GPT-4o with money cost. We report the bar of our main results in the appendix.

Guidelines:

• The answer NA means that the paper does not include experiments.

• The authors should answer "Yes" if the results are accompanied by error bars, confidence intervals, or statistical significance tests, at least for the experiments that support the main claims of the paper.

• The factors of variability that the error bars are capturing should be clearly stated (for example, train/test split, initialization, random drawing of some parameter, or overall run with given experimental conditions).

• The method for calculating the error bars should be explained (closed form formula, call to a library function, bootstrap, etc.)

• The assumptions made should be given (e.g., Normally distributed errors).

• It should be clear whether the error bar is the standard deviation or the standard error of the mean.

• It is OK to report 1-sigma error bars, but one should state it. The authors should preferably report a 2-sigma error bar than state that they have a 96% CI, if the hypothesis of Normality of errors is not verified.

• For asymmetric distributions, the authors should be careful not to show in tables or figures symmetric error bars that would yield results that are out of range (e.g. negative error rates).

• If error bars are reported in tables or plots, The authors should explain in the text how they were calculated and reference the corresponding figures or tables in the text.

## 8. Experiments compute resources

Question: For each experiment, does the paper provide sufficient information on the computer resources (type of compute workers, memory, time of execution) needed to reproduce the experiments?

Answer: [Yes]

Justification: We use 4 80G A100 GPUs for the RFT, and the training takes about 10 hours.

Guidelines:

• The answer NA means that the paper does not include experiments.

• The paper should indicate the type of compute workers CPU or GPU, internal cluster, or cloud provider, including relevant memory and storage.

• The paper should provide the amount of compute required for each of the individual experimental runs as well as estimate the total compute.

• The paper should disclose whether the full research project required more compute than the experiments reported in the paper (e.g., preliminary or failed experiments that didn’t make it into the paper).


---

## 📑 关键章节 | The Future is Agentic: Definitions, Perspectives, and Open Challenges of Multi-Agent Recommender Systems

**arXiv ID**: [2507.02097](https://arxiv.org/abs/2507.02097)

## 1 Introduction and Motivation

Large Language Model (LLM) agents go beyond traditional chatbots by ofering goal-directed, agentic behavior rather than merely responding to user queries through one-shot text generation.

Authors’ Contact Information: Reza Yousefi Maragheh, University of Illinois Urbana Champaign, Illinois, USA, ryousefimaragheh@acm.org; Yashar Deldjoo, Polytechnic University of Bari, Bari, Italy, deldjooy@acm.org.

Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page. Copyrights for components of this work owned by others than the author(s) must be honored. Abstracting with credit is permitted. To copy otherwise, or republish, to post on servers or to redistribute to lists, requires prior specific permission and/or a fee. Request permissions from permissions@acm.org. © 2026 Copyright held by the owner/author(s). Publication rights licensed to ACM. ACM 2770-6699/2026/7-ART https://doi.org/10.1145/nnnnnnn.nnnnnnn

In essence, they are designed to handle multi-step tasks, orchestrate information flow, and autonomously employ tools or functions when necessary [48, 61, 84]. This distinction means that while a conventional chatbot might provide short answers in a single round of dialogue, an agentic system can proactively structure a complex problem and solve it through a sequence of methodical steps. Put another way, an LLM agent is not only a reactive conversational partner but a dynamic problem-solver capable of decomposing tasks, maintaining state, invoking external resources, and adapting its strategy to reach a goal [64, 66, 76].

Much as goal-directed agentic behavior has reshaped other NLP-oriented tasks, it applies naturally to the tasks surrounding recommender systems (RS). In the most common case, recommendation is handled in a single shot: given a user history and a candidate set, a retrieval or ranking function estimates relevance and returns a ranked list of similar movies or items. Agentic recommendation broadens this picture along two axes. First, even a single-shot task can sometimes be handled better by decomposing it into subtasks, for example by summarizing a long or heterogeneous history, planning a ranking strategy, or aggregating several candidate orderings before committing to a final list. Second, and more fundamentally, the user need may not be <sub>“rank</sub> <sub>items</sub> <sub>for</sub> <sub>this</sub> <sub>profile”</sub> at all, but rather <sub>“help</sub> <sub>me</sub> <sub>achieve</sub> <sub>a</sub> <sub>goal”</sub> under multiple constraints, evolving context, and incomplete information. In this latter regime, recommendation becomes a multi-stage decision process rather than a single scoring operation: the system may ask clarifying questions, retrieve current catalog evidence, reason over constraints, call external tools, maintain memory over prior interactions, verify whether candidate items satisfy user and policy constraints, and finally produce a ranked list, bundle, explanation, or action plan. Section 4 develops these possibilities through <sup>four</sup> <sup>representative</sup> <sup>scenarios:</sup> interactive goal-oriented recommendation<sup>,</sup> user simulation for ofline evaluation<sup>,</sup> contextual and multimodal recommendation, <sup>and</sup> recommendation explanation<sup>.</sup>

We refer to this RS-centered paradigm as <sub>agentic</sub> <sub>recommendation</sub>. In an agentic recommender system, recommendation is no longer only a one-shot call to a ranker; it is a goal-driven process in which one or more stateful agents participate in an observe–plan–act–verify loop over user signals, item evidence, tools, memories, constraints, and recommendation objectives. This viewpoint gives us the flexibility, and the obligation, to evaluate recommendation along a more diverse set of metrics than top-?? accuracy alone: relevance and ranking quality, constraint satisfaction, diversity, bundle coherence, evidence grounding, explanation faithfulness, fairness of exposure, long-term user value, and user efort, together with trace-level signals such as tool-call success, memory correctness, latency, and cost. The agentic layer is useful when it improves these recommendation-relevant outcomes, not merely because a system contains an LLM or several modules.

Beyond the multi-step task handling already described, agentic recommendation rests on two further capabilities in particular: <sub>memory</sub>, so that the agent can carry state across the steps of a task, and <sub>tool</sub> <sub>use</sub>, so that it can act on evidence beyond its parameters.

The first, <sub>memory</sub>, is a core mechanism for agentic recommendation rather than an optional implementation detail. Over a multi-step task the system may need to remember the last item shown in a session, a rejected style, a durable preference inferred across interactions, or a recurring workflow that should be executed with minimal friction. We use the standard distinction between <sub>working</sub>, <sub>episodic</sub>, <sub>semantic</sub>, and <sub>procedural</sub> memory, and defer the taxonomy, storage mechanisms, and update/retrieval operators to Section 3. What matters at this point is that memory is not only an enabler but also an object of evaluation: stale memories can contaminate future rankings, incorrect summaries can distort user profiles, and privacy-sensitive traces may be retrieved when they should be forgotten. Memory should therefore be judged by whether it improves downstream recommendation utility, preserves relevant constraints, avoids stale or irrelevant facts, and respects privacy and deletion requirements.

The second, <sub>autonomous</sub> <sub>tool</sub> <sub>use</sub>, lets the agent act on evidence beyond its parameters. Instead of relying only on static model parameters, agentic recommenders can invoke retrieval APIs, product databases, image-analysis tools, policy checkers, constraint solvers, or evaluation modules to fetch data, analyze content, and act on domain-specific evidence [27, 57]. For example, a request for a restaurant can trigger queries for current ratings, availability, location, and dietary filters rather than depending on memorized information; a request to furnish an uploaded room image can trigger a vision tool to extract visual features and then a catalog query for items matching the user’s style and spatial constraints. Tool use and memory are complementary: memory carries durable preferences and prior recommendations across steps, while tools ground the next recommendation in current catalog, policy, or contextual evidence.

The framework developed in this paper is therefore LLM-centric but not LLM-exclusive. LLMs are currently a natural implementation substrate for agentic recommendation because they provide flexible natural-language understanding, reasoning, tool-use interfaces, and multi-agent communication. However, an agent in an agentic recommender may also be powered by a classical ranker, a retrieval model, a smaller language model, a rule-based controller, a constraint solver, a vision model, a simulator, or a human-review module. What makes the system recommender-specific is not the mere use of natural language or multiple agents, but the fact that these components operate over users, contexts, histories, item catalogs, candidate sets, ranking objectives, feedback signals, explanations, and exposure efects.

Taken together, (i) multi-step task handling, (ii) memory retention, and (iii) autonomous tool use empower LLM-based and non-LLM-based agents to operate with a level of autonomy that transcends the simpler question-and-answer paradigm of traditional chatbots [48, 61, 64]. At the same time, this should not be read as a claim that agentic systems are always preferable. For stable, well-scoped, high-throughput ranking tasks, conventional recommender pipelines may remain simpler, cheaper, more predictable, and easier to evaluate. The value of agentic recommendation is therefore strongest when planning, memory, tool use, interaction, and verification improve recommendation-layer outcomes enough to justify their additional latency, cost, privacy risk, and governance complexity.

## 2.3 Formal Framework

In this subsection, we introduce formal definitions for key concepts central to our framework. These definitions establish a rigorous foundation for discussing the architectural and operational aspects of agents, including specialized LLM Agents, Multi-Agent Systems, and Tool-Using Agents. We also provide a generic formalism for representing the internal structure of an agent.

<sub>Definition</sub> <sub>2.1</sub> <sub>(LLM</sub> <sub>Agent).</sub> An <sub>LLM</sub> <sub>Agent</sub> is an intelligent system whose core decision-making and interaction capabilities are powered by one or more large language models. Formally, we denote such an agent as:

$$
A _ {\mathrm{LLM}} = \Big (\mathcal {M}, \mathcal {I}, \mathcal {O}, \mathcal {F}, \Omega \Big),
$$

where:

<sub>•</sub> <sub>M</sub> is the underlying language model or set of models used for text generation, understanding, and reasoning.

<sub>• I</sub> represents the input space that the agent can observe.

<sub>• O</sub> denotes the output space the agent can produce.

<sub>•</sub> <sub>F</sub> is a set of functions, tools, or APIs the agent can invoke to enhance its capabilities.

<sub>•</sub> <sub>Ω</sub> comprises any additional state or memory structures that enable the agent to maintain context across time or tasks.

For example, in recommendation settings, for an eCommerce shopping assistant, <sub>M</sub> can be a GPT-style transformer fine-tuned for e-commerce dialogue; it encodes linguistic knowledge and basic reasoning skills, allowing the agent to parse user requests and generate coherent replies. <sub>I</sub> is the space of user queries and contextual signals, while <sub>O</sub> is the space of possible outputs, including text responses, actions, or function calls. <sub>F</sub> represents external functions or APIs, such as retrieval APIs, price fetchers, or inventory status calls, which augment the innate knowledge of <sub>M</sub> with fresh, authoritative data, thereby mitigating hallucination. The agent’s memory, <sub>Ω</sub>, is partitioned into (a) <sub>short-term</sub> <sub>memory</sub> $\Omega ^ { \mathrm { { S T M } } }$ that keeps the last few dialogue turns, (b) <sub>long-term</sub> episodic memory $\dot { \Omega } ^ { \mathrm { E P I } }$ that stores past party-planning sessions, and (c) <sub>semantic</sub> <sub>memory</sub> $\Omega ^ { \mathrm { S E M } }$ containing persistent user traits (e.g., “prefers red decor”). During inference, salient fragments of <sub>Ω</sub> are retrieved and appended to the prompt, giving the agent continuity across sessions.

For a multi-turn dialogue agent, at each timestep ??, the agent receives an input $i _ { t } \in \mathcal { I }$ , consults its memory $\omega \subseteq \Omega$ to form an augmented context, and computes the output $o _ { t } \in O$ as follows:

$$
o _ {t} = f _ {\mathcal {M}, \mathcal {F}} (i _ {t}, \omega)\tag{1}
$$

where $f _ { M , \mathcal { F } }$ is the agent’s policy function that maps the current input $i _ { t }$ and retrieved memory ?? to an output $o _ { t } ,$ , leveraging both the language model <sub>M</sub> and the available external functions $\mathcal { F }$

Definition 2.1 intentionally describes a <sub>generic</sub> LLM agent. The same tuple becomes a <sub>recommender</sub> <sub>agent</sub> once each component is instantiated over recommendation-relevant objects rather than arbitrary text. Concretely, we take the agent to operate on a state

$$
s _ {t} = \big (u, C _ {t}, H _ {u}, \mathcal {S} _ {t} ^ {(K)}, \pi \big),
$$

where ?? identifies the user, $C _ { t } ~ \in ~ \mathcal { I }$ is the dialogue or contextual state, $H _ { u }$ is a chronological interaction history, ${ \cal S } _ { t } ^ { ( K ) } \subseteq { \cal S }$ is the candidate set available at step ??, and ?? encodes business, safety, privacy, and multi-stakeholder policy constraints. An LLM agent is a recommender agent when (i) its output space $o$ contains recommendation actions such as <sub>retrieve(·)</sub>, <sub>rank(·)</sub>, <sub>recommend(·)</sub>, <sub>ask(·)</sub>, and <sub>explain(·)</sub>; (ii) its tool set $\mathcal { F }$ and environment expose RS-relevant evidence such as the item catalog, candidate sets, and feedback signals; and (iii) its objective is a recommendation utility (relevance, constraint satisfaction, long-term engagement) optimized under the constraints in ??.

Definition 2.2 (Multi-Agent System (MAS)). <sup>A</sup> Multi-Agent System <sup>is</sup> <sup>an</sup> <sup>ordered</sup> <sup>triple</sup>

$$
\text { MAS } = \Big (\mathcal {A}, \mathcal {E}, \Pi \Big),
$$

where

(a) ${ \mathcal { A } } = \{ A _ { 1 } , . . . , A _ { n } \}$ is a finite set of agents. Each $A _ { i }$ may be an LLM agent (Definition 2.1) or another kind of modular service (e.g., rule-based, vision, or database stub).

(b) <sub>E</sub> is the shared <sub>environment</sub> that supplies percepts and resources to the agents—such as external APIs, user interfaces, or a simulated world state. Formally, $\varepsilon$ can be viewed as a partial observable Markov space from which each agent receives observations and in which it executes actions.

(c) $\Pi = \left( \mathbf { C } , \Gamma \right)$ <sup>is</sup> <sup>the</sup> interaction protocol<sup>.</sup>

(i) $\mathbf { C } \in \{ 0 , 1 \} ^ { n \times n }$ is a (possibly time-varying) <sub>communication</sub> <sub>matrix</sub>. A value $\mathbf { C } _ { i j } = 1$ indicates that messages of type $\gamma \in \Gamma$ <sup>are</sup> permitted <sup>from</sup> $A _ { i }$ to $A _ { j }$ under current conditions. The condition can be

<sub>• preset</sub> (static design-time routing), or

<sub>• autonomous</sub> (dynamically toggled by agents. $\mathrm { e . g . } , A _ { i }$ opens a channel to $A _ { j }$ when cooperation is beneficial, closes it otherwise).

(ii) <sub>Γ</sub> is the finite set of admissible <sub>message</sub> <sub>schemata</sub> (performative types, serialization rules, timing constraints). Each $\gamma \in \Gamma$ defines both syntax and semantics so that a receiving agent can parse and act on the message.

An execution of MAS can be viewed as a sequence of environment states and inter-agent messages that respect <sub>Π</sub>. Depending on design, agents may coordinate (<sub>co-operative</sub>), compete (<sub>self-interested</sub>), or exhibit mixed motives while attempting to satisfy individual or shared objectives.

In the recommendation setting, the MAS triple specializes as follows. The environment $\varepsilon$ exposes recommendation state, including the item catalog, per-user histories, candidate sets, and observed feedback, rather than a generic world model. The agents in $\mathcal { A }$ occupy recommendation roles, such as profilers, retrievers, rankers, consistency checkers, evaluators, or user simulators, each a recommender agent in the sense above. The protocol <sub>Π</sub> carries recommendation payloads: messages in <sub>Γ</sub> transport candidate lists, ranked slates, retrieved evidence, constraint or compliance reports, and memory records, and the communication matrix <sub>C</sub> encodes which of these exchanges are permitted. The marketplace example that follows is the smallest such instance.

Consider a minimal marketplace scenario with two autonomous components, namely a <sub>recom-</sub> mendation agent <sup>and</sup> <sup>an</sup> evaluation agent<sup>,</sup> <sup>so</sup> <sup>that</sup>

$$
\mathcal {A} = \{A _ {\mathrm{rec}}, A _ {\mathrm{eval}} \}.
$$

In this case $\delta \ = \ ( \mathrm { U s e r P r o f i l e D B } _ { ; }$ , ProductCatalogue, BusinessRulesKB, providing user attributes, real-time inventory, and brand–policy facts, respectively. The interaction protocol can be

$$
\Pi = (\mathbf {C}, \Gamma), \qquad \mathbf {C} = \left( \begin{array}{c c} 0 & 1 \\ 1 & 0 \end{array} \right), \quad \Gamma = \Bigl \{\text { candidate\_list }, \text { compliance\_report } \Bigr \}.
$$

Thus $A _ { \mathrm { r e c } }$ may send a <sub>candidate\_list</sub>, a ranked JSON array $\{ ( s _ { 1 } , \mathrm { s c o r e } _ { 1 } ) , \dotsc , ( s _ { L } , \mathrm { s c o r e } _ { L } ) \}$ to $A _ { \mathrm { e v a l } }$ , which in turn replies with a <sub>compliance\_report</sub> indicating any items that violate policy. The of-diagonal ones in <sub>C</sub> permit bidirectional messaging, while the zeros on the diagonal denote that agents do not address themselves. At runtime, $\mathbf { C } _ { \mathrm { e v a l , r e c } }$ can be toggled of once no further corrections are required, illustrating how links may be preset yet autonomously reconfigured according to system state.

Definition 2.3 (Memory Update Function). <sup>Let</sup> $\Omega _ { t }$ denote the long-term memory state maintained by an agent at dialogue step ?? and let

$$
\mathcal {C} _ {t} \in \mathcal {X}
$$

be the raw context collected during that step (e.g., the most recent user utterance, the agent’s reply, and any intermediate reasoning trace, represented in token or embedding space). A <sub>Memory</sub> <sub>Update</sub> <sub>Function</sub> is a mapping

$$
\mathcal {U}: \left(\mathcal {C} _ {t}, \Omega_ {t}\right) \longrightarrow \Omega_ {t + 1},
$$

where

• U <sup>internally</sup> <sup>applies</sup> <sup>a</sup> retention operator

$$
\mathcal {R}: \mathcal {C} _ {t} \to \widetilde {\mathcal {C}} _ {t}
$$

that distils $C _ { t }$ into a noise-reduced summary $\widetilde { C } _ { t } \in \widetilde { X }$

<sub>•</sub> merges $\widetilde { C } _ { t }$ with the prior state $\Omega _ { t }$ via a domain-specific <sub>merge</sub> <sub>rule</sub> <sub>⋄</sub>, and produces the next persistent state:

$$
\Omega_ {t + 1} = \Omega_ {t} \diamond \widetilde {\mathcal {C}} _ {t}.
$$

The goal is to preserve salient semantic information while discarding redundancy, ensuring that $\Omega _ { t + 1 }$ remains compact yet suficient for future retrieval.

Assume a shopping assistant agent and a user that uses the agent to order a cake. At turn ?? the user says “remember that two of my guests require a gluten-free diet”. The raw context $C _ { t }$ includes the user utterance, the agent’s internal chain-of-thought, and the pending action call to a <sub>CakeSearch</sub> tool. The retention operator extracts the key fact

$$
\widetilde {C} _ {t} = \text {" {guest\_allergy: gluten}} \text {,}
$$

and the merge rule appends it to the agent’s long-term <sub>episodic</sub> slot in $\Omega _ { t }$ :

$$
\Omega_ {t + 1} ^ {\mathrm{EPI}} = \Omega_ {t} ^ {\mathrm{EPI}} \cup \{\text { guest\_allergy: gluten } \}.
$$

On the next turn $( t + 1 )$ the planner retrieves this memory fragment and instructs a downstream cake-selection agent to filter for gluten-free options, illustrating how <sub>U</sub> enables continuity and correctness across dialogue turns without bloating the prompt window.

In a recommender, the update function <sub>U</sub> governs what persists about a user across turns and sessions: durable preferences, accepted and rejected items, satisfied or violated constraints, and session-level intent. The recsys-specific consideration is that <sub>U</sub> is not only an enabler of personal ization but also a source of error. A retention operator $\mathcal { R }$ that over-summarizes can drop a binding constraint such as the gluten restriction; one that under-summarizes lets stale or contradictory preferences accumulate and later contaminate ranking. The merge rule <sub>⋄</sub> must therefore respect recommendation-relevant properties, namely recency, provenance, and the right to delete privacysensitive traces, so that $\Omega _ { t + 1 }$ improves rather than degrades downstream recommendation utility. These properties are what the memory-correctness and staleness signals of Section 5 are intended to measure.

<sub>Definition</sub> <sub>2.4</sub> <sub>(Memory</sub> <sub>Retrieval</sub> <sub>Function).</sub> Let <sub>Ω</sub> be the agent’s persistent memory store after ?? dialogue steps. A <sub>Memory</sub> <sub>Retrieval</sub> <sub>Function</sub> is a mapping

$$
Q: (\Omega , \tau) \longrightarrow \widehat {C},
$$

where

$\Omega = \{ \widetilde { C } _ { 1 } , \ldots , \widetilde { C } _ { m } \}$ is a corpus of distilled memory traces, each $\widetilde { C } _ { i } \in \widetilde { X }$ (text snippets, embeddings, or hybrids) produced by the update operator <sub>U</sub> (Definition 2.3).

$\tau \in \mathcal T$ is a task representation—e.g. the current user query, an intermediate reasoning goal, or a structured tool call argument—expressed in text, vector, or multi-modal form.

${ \widehat { C } } \in { \widehat { X } } \subseteq { \widetilde { X } }$ is the subset of memory deemed relevant to ??, returned in a form suitable for prompt augmentation or downstream computation.

By recalling only ${ \widehat { C } } ,$ the agent conditions subsequent reasoning on task-specific context while keeping the efective prompt window compact and noise-free.

Continuing the shopping assistant example for cake ordering, suppose at turn ??<sub>+</sub>1 the planner agent formulates the sub-goal $\tau = ^ { \infty }$ “find gluten-free chocolate cake designs”. Invoking $\widehat { \cal C } =$ $\boldsymbol { Q } ( \Omega _ { t } , \tau )$ returns a minimal set of memory entries, e.g.

$$
\widehat {C} = \{\text { guest\_allergy: gluten, child\_pref: chocolate } \},
$$

filtered from dozens of prior dialogue snippets. These facts are appended to the prompt fed into the <sub>CakeSearch</sub> tool, ensuring that the retrieval agent queries only gluten-free, chocolate-flavoured options while ignoring unrelated historical details. Thus, $\boldsymbol { Q }$ provides precise, context-aware recall that prevents irrelevant or outdated memories from polluting the reasoning chain.

For recommendation, the query ?? supplied to $\boldsymbol { Q }$ is typically a ranking or explanation sub-goal, and the retrieved subset $\widehat { C }$ directly conditions the candidate set, the ranking, or the generated justification. Two recsys-specific failure modes follow. First, retrieving outdated or irrelevant traces can inject spurious constraints into ranking, for example resurfacing a preference the user has since abandoned. Second, retrieving privacy-sensitive history that should have been excluded can produce recommendations or explanations that are correct yet non-compliant. Efective retrieval in a recommender is therefore judged not only by topical relevance, as in the cake example, but by whether the recalled context preserves active constraints, excludes stale or deleted items, and respects the policy set ??.

By introducing these formalisms, we establish a common language for discussing agentic behavior and capabilities. In the subsequent sections, we will demonstrate how these formal concepts can be instantiated and extended to create advanced recommendation systems and other multi-step, context-aware applications.

## 4.2 User Simulation and Recommendation Evaluation

<sub>Formal</sub> <sub>definition</sub> <sub>of</sub> <sub>the</sub> <sub>task.</sub> User simulation and recommendation evaluation together form a framework in which synthetic user behavior is generated to probe, test, and refine recommender systems before full-scale deployment. Let $R _ { \phi } : \bar { X } \to S ^ { L }$ denote a recommender parameterised by $\phi$ that maps the current session state $x \in \chi$ to an ordered list of ?? items from the catalogue <sub>S</sub>. A <sub>user</sub> <sub>simulator</sub> is a stochastic policy

$$
\mathcal {M} _ {\theta , \omega}: \mathcal {X} \times \mathcal {S} ^ {L} \longrightarrow \mathcal {A} _ {\text { user }}, \quad \mathcal {A} _ {\text { user }} \in \{\text { Select }, \text { Not   Select } \},
$$

parameterised by intrinsic preference vector $\theta$ and noise vector $\omega .$ . Note that user simulator’s action space ${ \mathcal { A } } _ { \mathrm { u s e r } }$ can include another set of options depending on the recommendation setting. For instance it can be <sub>{Click</sub>, <sub>Pass</sub>, <sub>Purchase}</sub> in eCommerce user simulation. Given repeated interaction over $T$ time steps, the joint process $\{ x _ { t } , s _ { t } ^ { ( L ) } , a _ { t } ^ { \mathrm { u s e r } } \} _ { t = 1 } ^ { T }$ induces an empirical evaluation functional

$$
\Psi (R _ {\phi}, \mathcal {M} _ {\theta , \omega}) = \mathbb {E} \left[ \sum_ {t = 1} ^ {T} g \left(x _ {t}, s _ {t} ^ {(L)}, a _ {t} ^ {\text {user}}\right) \right],
$$

where $g ( \cdot )$ is a reward such as <sub>Select</sub> or diversity penalty. The “simulation-based evaluation problem” seeks to estimate <sub>Ψ</sub> under controlled distributions of ?? and $\omega .$

<sub>High-level</sub> <sub>goal.</sub> In practical scenarios, gathering data from real users can be expensive or infeasible, especially when conducting A/B tests for newly introduced features. A simulated user that approxi mates realistic browsing, clicking, and purchasing behaviors ofers a controlled environment for stress-testing various recommendation strategies. For example, an e-commerce platform aiming to recommend Bohemian-style furniture may wish to simulate how a typical user navigates through the site, examines multiple items, compares prices, and ultimately decides whether to purchase. This allows the platform to estimate click-through rates and conversions without requiring a large real-user pilot study. The primary aim is to replicate the interactions of a diverse user population in order to evaluate and compare recommendation strategies. The system must produce synthetic but plausible session data, track user decisions at each step, and generate summary statistics or qualitative insights about overall performance. By testing both short sessions (quick browsing) and long sessions (prolonged decision-making), one can obtain a more comprehensive understanding of the strengths and weaknesses of the underlying recommender algorithms.

<sub>System</sub> <sub>architecture</sub> <sub>and</sub> <sub>agent</sub> <sub>setup.</sub> We instantiate a multi-agent system (also see Figure 2)

$$
\operatorname{MAS} _ {\text { sim }} = (\mathcal {A}, \mathcal {E}, \Pi), \quad \mathcal {A} = \left\{A _ {\text { rec }}, A _ {\text { user }}, A _ {\text { note }}, A _ {\text { eval }}, A _ {\text { summ }}, A _ {\text { report }} \right\}.
$$

$A _ { \mathbf { r e c } }$ (<sub>Recommender</sub> <sub>Agent</sub>) is an LLM agent that wraps $R _ { \phi }$ and orchestrates tool calls (<sub>SearchAPI</sub>, SessionTracker<sup>).</sup>

$A _ { \mathbf { u s e r } }$ <sup>(</sup>User Simulator<sup>)</sup> <sup>implements</sup> $M _ { \theta , \omega } ;$ it possesses a structured memory $\Omega ^ { \mathrm { S E M } }$ of preferences and $\Omega ^ { S \mathrm { T M } }$ for the current session trajectory.

$A _ { \mathbf { e v a l } }$ <sup>(</sup>Evaluation Agent<sup>)</sup> <sup>logs</sup> <sup>tuples</sup> $( x _ { t } , s _ { t } ^ { ( L ) } , a _ { t } ^ { \mathrm { u s e r } } )$ via update function <sub>U</sub>-style appends to long-term storage. It computes instantaneous metrics $g _ { t }$ by querying logs with $\boldsymbol { Q }$ and emits eval\_event <sup>messages.</sup>

$A _ { s u m m }$ (<sub>Session</sub> <sub>Summariser</sub>) invokes a compression operator $\mathcal { R } _ { \mathrm { s u m } }$ every ?? turns to produce a summary vector of the session’s salient outcomes.

$A _ { \mathbf { r e p o r t } }$ (<sub>Reporter</sub>) aggregates thousands of summaries, performs statistical tests, and outputs a final PDF/CSV dashboard

Environment $\mathcal { E } = \mathrm { ( P r o d u c t D B }$ , PreferenceSampler, LogStore, provides catalogue metadata, draws synthetic ?? , and persists interaction traces.

Communication Protocol matrix of this MAS, <sub>C</sub> allows the sequence

$$
A _ {\mathrm{rec}} \rightleftarrows A _ {\mathrm{user}} \rightarrow A _ {\mathrm{eval}} \rightarrow A _ {\mathrm{summ}} \rightarrow A _ {\mathrm{report}},
$$

with message types $\Gamma \ = \ \{ r e c _ { - } 1 \mathrm { i } s \mathrm { t } .$ <sup>,</sup> user\_action<sup>,</sup> log\_entry<sup>,</sup> eval\_event<sup>,</sup> session\_summary<sup>,</sup> final\_report}<sup>.</sup>

![](images/218fb608ad65fe39fc7e890cd746ff12baa5b3138764d703b8b8d8c1253c9b1e.jpg)  
Fig. 2. A sample multi-agent system for user behavior simulation and recommendation evaluation

Memory and tool requirements. $A _ { \mathrm { u s e r } }$ can access and update semantic memory, $\Omega ^ { \mathrm { S E M } }$ which includes latent taste vector, price sensitivity, $\Omega ^ { \mathrm { P R O C } }$ which stores navigation policy, click heuristics, and $( \Omega ^ { \mathrm { E P I } }$ which remembers prior simulated sessions (for repeat-exposure efects). $A _ { \mathbf { e v a l } }$ uses a raw text log plus vector store to support fast <sub>Q</sub> filters by item ID or action type. It also maintains sliding-window statistics (e.g. running CTR, diversity entropy) in $\Omega ^ { S \mathrm { T M } }$ . Tool access by other agents is illustrated in Figure 2.

<sub>Benefits</sub> <sub>and</sub> <sub>discussion.</sub> The stated MAS architecture can yield the following traits: (i) Cost-efective experimentation, where hundreds of parameterized user agents can be spawned in parallel, yielding reliable ofline estimates of $\Psi ( R _ { \phi } , M )$ before any live-trafic exposure. (ii) Cold-start mitigation, where by sampling user profiles with sparse or unseen preference vectors, the framework stresses $R _ { \phi }$ under low-data regimes and surfaces failure modes early. (iii) Diagnosis of systemic bias, where the reporter’s aggregate view highlights trends such as over-pricing, popularity bias, or demographic skew, which can be traced back to fine-grained logs for root-cause analysis. (iv) Memory-driven realism, where the division of semantic, episodic, and procedural memories within $A _ { \mathrm { u s e r } }$ allows long-range preference carry-over (“I still want a bohemian sofa”) while modelling bounded session attention—all expressed via the formal $\mathcal { U } / Q$ operators. (v) Modular extensibility, where new evaluation criteria (fairness, robustness) can be implemented by adding auxiliary evaluator agents without retraining the core recommender, consistent with the MAS abstraction.

Overall, this architecture turns user simulation into a first-class, memory-aware MAS that provides quantitative and qualitative feedback loops—bridging the gap between ofline metrics and live user studies for next-generation recommender systems.

## 5 Operational Challenges and Evaluation Agenda

Agentic recommender systems inherit challenges from general LLM agents and multi-agent systems, but those challenges become recommender-specific when they afect ranking, exposure, feedback, item evidence, user memory, or marketplace outcomes. We therefore organize the challenge section around two questions: (i) what failure mode is introduced by planning, memory, tools, or multi-agent coordination, and (ii) how should a recommender-system researcher measure it?

## 6.1 Experimental Setup

<sub>Task.</sub> Each instance is a single ranking question: given the purchase history of a user and ten candidate items, the pipeline must return a ranking of the ten candidates. Exactly one candidate is the held-out next purchase; the remaining nine are sampled at random from items in the same product category. The agent emits a ranked list, and specialized agents cooperate to produce it.

<sub>Data.</sub> We use the Amazon-2023 review corpus [30] across four categories: Amazon Fashion, Appliances, Electronics, and Toys and Games. For each category we draw two contrastive user cohorts of 100 users, a <sub>random</sub> cohort and a <sub>high-diversity</sub> cohort, giving two samples of $n = 4 0 0$ pooled over the four categories (for detailed per category results see Appendix A). The contrast between these two samples is the backbone of the analysis.<sup>2</sup>

To assess how recommendation quality varies with the heterogeneity of a user’s interaction history, we stratify users by the lexical diversity of the item titles they have previously engaged with. For a user ?? with history $H _ { u } = \{ t _ { 1 } , \dots \dots , t _ { m } \}$ , we represent each item title $t _ { i }$ by its set of lowercased word tokens $T _ { i } = \mathrm { t o k e n s } ( t _ { i } )$ , and define the diversity of ?? as the mean pairwise Jaccard distance over all title pairs in the history:

$$
\operatorname{Div} (u) = \binom{m}{2} ^ {- 1} \sum_ {1 \leq i <   j \leq m} \left(1 - \frac {| T _ {i} \cap T _ {j} |}{| T _ {i} \cup T _ {j} |}\right),\tag{2}
$$

where $\binom { m } { 2 }$ is the number of unordered title pairs. The score lies in <sub>[</sub>0, 1<sub>]</sub>: it is 0 when all titles share an identical token set (a homogeneous history) and approaches 1 when every pair of titles is lexically disjoint (a maximally diverse history). Users with fewer than two non-empty token sets are excluded, and histories are capped at 100 titles to bound the quadratic pairwise cost.

We restrict the analysis to users with at least seven history items. The <sub>high-diversity</sub> cohort comprises, per category, the 100 users with the largest Div<sub>(</sub>??<sub>)</sub>. The <sub>random</sub> cohort is drawn uniformly at random (seed 42) from the eligible users in the same category, and serves as a typical baseline population against which the high-diversity cohort is compared.

<sub>Agentic</sub> <sub>roles</sub> <sub>and</sub> <sub>workflows.</sub> We evaluate seven workflows, summarized in Table 5, grouped into three families of agentic role. The single-shot LLM baseline (SA) issues one model call that reads the history and the candidates and returns the ranking, and serves as the reference against which the value of additional agents is measured. The <sub>decomposition</sub> <sub>and</sub> <sub>specialization</sub> family restructures the input before ranking: a profiler compresses the history into an intent summary that the ranker then conditions on (PR), and a planner additionally outlines the ranking strategy (PPR). This family operationalizes the planning and task-decomposition capability that breaks a goal into focused subtasks each solved by a dedicated call [46, 61]. The <sub>ensembling</sub> <sub>and</sub> <sub>aggregation</sub> family replaces the single ranker with several rankers sampled at higher temperature for diversity and reconciles them through an arbitrator, either conditioned on a plan alone (PEns) or on both a plan and a profile (PPEns); this follows the finding that sampling multiple agents and aggregating their outputs improves accuracy, with gains that grow with task dificulty [46]. The <sub>iterative</sub> <sub>and</sub> <sub>adversarial</sub> <sub>refinement</sub> family improves an initial ranking through feedback rather than through added input structure: a ranker is critiqued by an evaluator and then revises (RC), in the manner of single-model self-feedback loops [47], or two rankers exchange and revise their rankings over several turns of debate (Deb) [15].

Table 5. Agentic workflows evaluated, grouped by role family. Calls/q is the number of LLM invocations per query; the original implementation identifiers are given in parentheses.

<table><tr><td>Workflow (ID)</td><td>Role family</td><td>Calls/q</td></tr><tr><td>SA: Single-shot LLM call</td><td>baseline</td><td>1</td></tr><tr><td>PR: Profiler → Ranker</td><td>decomposition / specialization</td><td>2</td></tr><tr><td>PPR: Planner+Profiler → Ranker</td><td>decomposition / specialization</td><td>3</td></tr><tr><td>PENS: Planner → 3 Rankers → Arbitrator</td><td>ensembling / aggregation</td><td>5</td></tr><tr><td>PPENS: Planner+Profiler → 3 Rankers → Arbitrator</td><td>decomposition + ensembling</td><td>6</td></tr><tr><td>RC: Ranker ↔ Critic</td><td>iterative / adversarial</td><td>3</td></tr><tr><td>DEB: Two-agent Debate</td><td>iterative / adversarial</td><td>4</td></tr></table>

Model, metrics, and cost basis. <sup>All</sup> <sup>pipelines</sup> <sup>use</sup> gpt-5-mini-2025-08-07<sup>.</sup> <sup>We</sup> <sup>evaluate</sup> <sup>ranking</sup> quality with MRR, NDCG, and HitRate (equal to Recall) at cutofs ?? <sub>∈</sub> <sub>{</sub>3, 10<sub>}</sub>. Cost is reported as input/output tokens, US dollars at \$0.25/\$2.00 per million input/output tokens, and the number of LLM calls per query.

## 6.5 Role-by-Role Analysis: What Each Agent Contributes

Reading the two quality tables by role family clarifies which forms of agentic structure carry the high-diversity gain and which do not.

<sub>Decomposition</sub> <sub>and</sub> <sub>specialisation.</sub> The planner and the profiler are the source of the steady, low-variance improvement on diverse inputs. Adding the profiler alone (PR) moves NDCG@10 from 0.6316 to 0.6368 on the high-diversity sample while leaving it slightly below the baseline on the random sample (0.7156 against 0.7197). Adding a planner on top (PPR) lifts NDCG@3 to 0.5069. The mechanism is intuitive: when a history spans many interests, articulating a ranking strategy and compressing the history into an explicit intent both reduce the burden on the final ranking step. When the history is already coherent, there is little to decompose, and the extra calls neither help nor hurt the ranking while still costing tokens. This is the empirical content of capability (i), planning and task decomposition.

<sub>Ensembling</sub> <sub>and</sub> <sub>aggregation.</sub> The largest high-diversity gains come from the ensemble pipelines PEns and PPEns, which lead at NDCG@10 and NDCG@3 respectively. Sampling several rankers at elevated temperature and reconciling them with an arbitrator recovers signal that any single sample misses, which matters precisely when the input is ambiguous. This is also the most expensive family, so its advantage is real but costly.

<sub>Iterative</sub> <sub>and</sub> <sub>adversarial</sub> <sub>refinement.</sub> This family is the weakest. The evaluator pipeline (RC) is the worst performer on the random sample and remains below the baseline on the high-diversity sample, and the debate pipeline (Deb) is roughly neutral on both. The synthesis is that the gains observed in this study come from restructuring the input and aggregating diverse views, not from agents critiquing one another in a closed loop. Closed-loop critique without an external oracle tends, if anything, to introduce the cascading errors analyzed in Section 5.3.

## 7 Conclusion

This paper established a footing for agentic recommender systems: architectures in which stateful agents, memories, tools, communication protocols, and verification steps are composed to improve recommendation-layer outcomes. We began by formalizing the core building blocks, generic LLM agents, recommender agents, multi-agent systems, memory update and retrieval functions, and observable traces, and by bounding what is recommendation-specific in such a system. These abstractions unify design choices such as raw bufers, vector stores, knowledge graphs, procedural memories, and tool-mediated evidence retrieval into a vocabulary that is precise enough for evaluation while remaining implementation-flexible.

Building on this vocabulary, Section 5 surfaced the operational fault lines that accompany such flexibility. We organized the open problems into five challenge families, communication complexity and protocol design, scalability and cost, hallucination and error propagation, emergent misalignment and collusion, and brand, policy, and legal compliance, and connected each to recommender-specific manifestations and measurable signals such as ranking quality, evidence coverage, provenance and trace validity, latency, token cost, exposure disparity, policy-violation rate, and judge reliability. The recurring message is that progress depends not only on larger models but on the interaction rules, memory hierarchies, and incentive structures that govern how agents are composed.

Finally, the controlled study of Section 6 shows why agentic recommendation must be evaluated conditionally. More agents are not automatically better: on representative next-item ranking samples the single-agent baseline is the pareto eficient default, whereas decomposition and ensemble roles become useful for high-diversity user histories, and closed-loop self-criticism can even degrade ranking quality. This supports a practical design principle in which agentic complexity is routed to the inputs where its marginal quality gain justifies its added latency, cost, and governance risk, and an evaluation agenda in which that trade-of, rather than top-?? accuracy alone, is what future work should report.

[已省略: references]

## A Per-Category Empirical Results

Section 6 reported ranking quality and cost pooled over the four Amazon-2023 categories. This appendix disaggregates those pooled numbers into the individual categories (<sub>Amazon</sub> <sub>Fashion</sub>, <sub>Appliances</sub>, <sub>Electronics</sub>, and <sub>Toys</sub> <sub>and</sub> <sub>Games</sub>; ??<sub>=</sub>100 users per category and cohort) for both the random cohort (Tables 9 and 11) and the high-diversity cohort (Tables 10 and 12). Workflow identifiers follow Table 5; in every category block the best and second-best values per column among the seven LLM pipelines are shown in <sub>bold</sub> and underline, and the random-ranking baseline is listed once per table. Because each user has a single held-out positive, MAP@?? <sub>=</sub> MRR@??; we therefore report MRR (equivalently MAP) and NDCG, and include the MAP columns for completeness. The two headline findings of the main text, namely that single-shot ranking is hard to beat on typical users (Table 7) and that decomposition and ensembling pay of on diverse users (Table 8), both survive disaggregation, but the per-category view shows that each efect is unevenly distributed across categories.


---

## 📑 关键章节 | A Comprehensive Review on Harnessing Large Language Models to Overcome Recommender System Challenges

**arXiv ID**: [2507.21117](https://arxiv.org/abs/2507.21117)

# A Comprehensive Review on Harnessing Large Language Models to Overcome Recommender System Challenges

RAHUL RAJA, <sup>Linkedin,</sup> <sup>Carnegie</sup> <sup>Mellon</sup> <sup>University,</sup> <sup>Stanford</sup> <sup>University,</sup> <sup>USA</sup>

ANSHAJ VATS, <sup>Meta,</sup> <sup>USA</sup>

ARPITA VATS, <sup>Linkedin,</sup> <sup>Meta</sup> <sup>AI,</sup> <sup>Amazon,</sup> <sup>Boston</sup> <sup>University,</sup> <sup>USA</sup>

ANIRBAN MAJUMDER, <sup>Amazon,</sup> <sup>USA</sup>

Recommender systems have traditionally followed modular architectures comprising candidate generation, multi-stage ranking, and re-ranking, each trained separately with supervised objectives and hand-engineered features. While efective in many domains, such systems face persistent challenges including sparse and noisy interaction data, cold-start problems, limited personalization depth, and inadequate semantic under standing of user and item content. The recent emergence of Large Language Models (LLMs) ofers a new paradigm for addressing these limitations through unified, language-native mechanisms that can generalize across tasks, domains, and modalities. In this paper, we present a comprehensive technical survey of how LLMs can be leveraged to tackle key challenges in modern recommender systems. We examine the use of LLMs for prompt-driven candidate retrieval, language-native ranking, retrieval-augmented generation (RAG) and conversational recommendation, illustrating how these approaches enhance personalization, semantic alignment, and interpretability without requiring extensive task-specific supervision. LLMs further enable zero- and few-shot reasoning, allowing systems to operate efectively in cold-start and long-tail scenarios by leveraging external knowledge and contextual cues. We categorize these emerging LLM-driven architectures and analyze their efectiveness in mitigating core bottlenecks of conventional pipelines. In doing so, we provide a structured framework for understanding the design space of LLM-enhanced recommenders, and outline the trade-ofs between accuracy, scalability, and real-time performance. Our goal is to demonstrate that LLMs are not merely auxiliary components but foundational enablers for building more adaptive, semantically rich, and user-centric recommender systems

[已省略: acm reference format:]

## 1 Introduction

Recommender systems have become essential across a broad spectrum of digital applications, including content streaming, e-commerce, education, recruiting, and social media platforms [2, 25, 52]. From personalized playlists on Spotify to tailored learning paths in MOOCs and targeted ads on LinkedIn, recommender systems play a pivotal role in shaping user experience and driving engagement. Despite their widespread adoption and continuous improvements, these systems face enduring challenges such as data sparsity, cold-start problems, dynamic user interests, and explainability [160]. As modern pipelines grow in complexity—with multi-stage architectures, large-scale retrieval, and diverse modalities—the demands for scalability, transparency, and adaptability have intensified. Recommender systems have traditionally followed modular architectures comprising candidate generation, multi-stage ranking, and re-ranking—each trained separately using supervised objectives and hand-engineered features [19]. While efective in many domains, such systems face persistent challenges, including sparse and noisy interaction data, cold-start problems, limited personalization depth, and inadequate semantic understanding of user and item content.

The recent emergence of Large Language Models (LLMs) ofers a new paradigm for addressing these limitations through unified, language-native mechanisms that can generalize across tasks, domains, and modalities. In this paper, we present a comprehensive technical survey of how LLMs can be leveraged to tackle key challenges in modern recommender systems. We examine the use of LLMs for prompt-driven candidate retrieval, language-native ranking, retrieval-augmented gen eration (RAG), and conversational recommendation—illustrating how these approaches enhance personalization, semantic alignment, and interpretability without requiring extensive task-specific supervision. LLMs also enable zero- and few-shot reasoning, allowing systems to operate efectively in cold-start and long-tail scenarios by leveraging external knowledge and contextual cues. We categorize these emerging LLM-driven architectures and analyze their efectiveness in mitigating core bottlenecks of conventional pipelines. In doing so, we provide a structured framework for understanding the design space of LLM-enhanced recommender systems, and outline trade-ofs between accuracy, scalability, and real-time performance.

Our work provides a foundation for researchers and engineers to reimagine recommender systems in the era of large language modeling, and highlights promising directions for future innovation.

## 2 Evolution of Architectures in Recommender Systems

Recommender systems have progressed from heuristic rules to collaborative filtering, latent fac torization, neural and graph-based models, and finally industrial-scale retrieval frameworks. Each paradigm enhanced expressiveness, scalability, and the ability to capture complex dependencies.

## 2.1 From Heuristics to Latent Factor Models

Early recommenders used deterministic heuristics such as popularity- and co-occurrence-based rules [9, 185, 187], which scale well but lack personalization. Collaborative Filtering (CF) [264] introduced personalization by exploiting similarity in interaction patterns between users or items. While simple and interpretable, CF sufers from sparsity and cold-start issues.

Matrix Factorization (MF) [88, 90] addressed scalability by embedding users and items into a shared low-dimensional space, with predictions computed via inner products of latent vectors. Variants such as ALS [282] and SVD++ [90] incorporated implicit feedback and became widely adopted in industrial systems due to their balance of accuracy and eficiency.

## 2.3 Sequential and Graph-Based Models

User behavior often exhibits temporal and contextual dynamics. Sequence-aware recommenders such as GRU4Rec [63] applied recurrent neural networks to session data, while transformer-based approaches (e.g., SASRec [83], BERT4Rec [199], TiSASRec [107]) leveraged self-attention to capture long-range dependencies and temporal intervals. These models outperform traditional CF in sequential domains such as streaming and e-commerce.

In parallel, graph-based recommenders [224] represented interactions as bipartite graphs. Neural Graph Collaborative Filtering (NGCF) [253] propagated embeddings through nonlinear message passing, while LightGCN [61] simplified this to linear aggregation, improving both accuracy and scalability. PinSage [253] scaled graph-based recommendation to billions of nodes using random walks and sampling, enabling deployment in web-scale platforms like Pinterest.

## 2.4 Industrial-Scale Retrieval Frameworks

With item catalogs often exceeding billions, retrieval eficiency became a dominant concern. Twotower architectures [256] learn independent embeddings for users and items, with relevance computed as the inner product between vectors. Pre-computed item embeddings can be indexed using Approximate Nearest Neighbor (ANN) search, enabling sublinear retrieval times.

The YouTube DNN [32] demonstrated the efectiveness of deep two-tower retrieval with sampled softmax, while Facebook’s DLRM [153] integrated sparse and dense features with cross-feature interaction layers. These retrieval modules form the candidate generation stage in multi-stage pipelines, with re-ranking typically handled by more expressive models such as gradient boosting or transformers.

## 4.2 Modeling and Algorithmic Challenges

Recommender systems today need to deliver a highly personalized user experience with industrial scale operations. However, the modeling and algorithmic components of these systems are plagued with natural limitations in performance, generalizability, and fairness. In this section, five key bottlenecks for modeling are explored, personalization vs. generalization, scalability of deep models, long-tail modeling, contextual and sequential understanding, and bias amplification, and industry and academia’s advancements toward overcoming these bottlenecks are discussed.

<sub>4.2.1</sub> <sub>Personalization</sub> <sub>vs.</sub> <sub>Generalization.</sub> Recommender systems face an inherent trade-of between personalization and generalization. Personalization aims to tailor recommendations uniquely to each user based on past interactions, whereas generalization ensures the model performs robustly for new users, unseen items, or domain shifts. Overpersonalization can lead to overfitting, where the model memorizes idiosyncratic preferences without learning generalizable patterns. This is especially detrimental in dynamic contexts such as career transitions or shifting media consumption

Mathematically, overfitting arises when the training objective focuses solely on minimizing personalized reconstruction error:

$$
\mathcal {L} _ {\mathrm{overfit}} = \sum_ {u \in \mathcal {U}} \sum_ {i \in \mathcal {I} _ {u}} \left(\hat {r} _ {u i} - r _ {u i}\right) ^ {2},\tag{1}
$$

where $\hat { r } _ { u i }$ is the predicted interaction (e.g., rating or click) and $r _ { u i }$ the observed label. Without external context or structural priors, the model fails to generalize beyond $\mathcal { T } _ { u } .$ —the items historically interacted with by user ??.

LLMs mitigate the personalization-generalization trade-of through a unified prompt-based interface that integrates multiple strategies into a cohesive framework. <sub>Instruction-Tuned</sub> <sub>Gen-</sub> <sub>eralization</sub> exploits the global instruction-following capabilities of models such as FLAN-T5 [30], InstructGPT [158], and T0 [183], enabling dynamic adaptation to new contexts without retraining. <sub>Prompt-Tuned</sub> <sub>Personalization</sub> enhances recommendations by directly embedding structured user feedback within prompts, thereby removing the necessity for continuous fine-tuning; approaches like PROMO [75] and PEPLER [119] successfully leverage explicit user preference signals. Additionally, Behavioral Diversity via Generative Modeling generates diverse recommendation candidates using generative prompts, fostering exploration and preventing recommendation collapse—a strategy notably implemented in Spotify’s mood-based playlists and e-commerce diversification strategies employed by platforms such as JD and Alibaba. Finally, <sub>Multitask</sub> <sub>Prompting</sub> simultaneously encodes multiple recommendation objectives, aligning LLM outputs with multitask learning paradigms, thereby enhancing interpretability and robustness, especially in sparse data environments. This approach is exemplified by systems like RecDSS [66] and instruction-based recommendation tutors [228]. Table 3 summarizes canonical prompt templates associated with these strategies.

<table><tr><td>Prompting Strategy</td><td>Example Prompt</td></tr><tr><td>Instruction-Tuned Generalization</td><td>User recently changed career to data science. Suggest jobs based on new interests.</td></tr><tr><td>Prompt-Tuned Personalization</td><td>User likes:. Recommend:</td></tr><tr><td>Behavioral Diversity via Generative Modeling</td><td>Generate diverse recommendations for:</td></tr><tr><td>Multitask Prompting</td><td>Recommend an item, explain why it is relevant, and predict how likely the user is to engage.</td></tr></table>

Table 3. Canonical Prompt Templates for LLM-Based Recommendation Strategies. Angle-bracketed tokens represent runtime placeholders.

<sup>Collectively,</sup> <sup>through</sup> semantic reasoning<sup>,</sup> prompt-based control<sup>,</sup> <sup>and</sup> generative flexibility<sup>,</sup> LLM-based recommenders substantially enhance their ability to generalize across sparse and coldstart scenarios, while maintaining personalized relevance.

<sub>4.2.2</sub> <sub>Scalability</sub> <sub>of</sub> <sub>Deep</sub> <sub>Models.</sub> Deep neural networks (DNNs), transformer-based architectures, and large language models (LLMs) are highly expressive and capable of modeling complex user–item interactions. However, their computational cost makes them impractical for real-time recommendation at industrial scale. The inference latency ?? can be modeled as:

$$
\tau = \sum_ {l = 1} ^ {L} C _ {l} \cdot d _ {l},\tag{2}
$$

where ?? is the number of layers, $C _ { l }$ is the compute cost (e.g., FLOPs) of layer ??, and $d _ { l }$ is the deployment-related delay (e.g., due to memory I/O or parallelism). As model complexity increases, ?? can exceed production constraints.

Two-stage ranking pipelines are widely adopted to alleviate this problem [53]. First, a lightweight candidate generator ??<sub>retrieval</sub> retrieves a small set $C ( u )$ from the item pool, followed by a heavier ranking model ??<sub>rank</sub>:

$$
\text { Top - } k = \arg \max _ {i \in C (u)} f _ {\text { rank }} (u, i).\tag{3}
$$

While this reduces overall latency, the challenge persists when incorporating deep user or item encoders. Let’s see how scalability challenge can be addressed using LLMs.

<sub>LLM-Based</sub> <sub>Distillation</sub> <sub>–</sub> Model distillation compresses a large teacher into a smaller student model, reducing latency while preserving performance. For LLMs, distillation does more than parameter compression — it transfers semantic generalization, instruction-following behavior, and multimodal reasoning. This is formalized as:

$$
\mathcal {L} _ {\mathrm{distill}} = \sum_ {x \in \mathcal {D}} \mathrm{KL} \left(p _ {\mathrm{LLM}} (y \mid x) \parallel p _ {\mathrm{student}} (y \mid x)\right),
$$

where $ { p _ { \mathrm { L L M } } }$ denotes the teacher’s distribution and $\pmb { \mathit { p } } _ { \mathrm { s t u d e n t } }$ the distilled model. Companies like TikTok [274], Amazon [195], and Alibaba [117] use LLM distillation to create small, latency aware models that retain generative capabilities for recommendations, search, and ranking. While traditional DNNs can be distilled, LLM-based distillation uniquely preserves instruction-following, multi-domain reasoning, and natural language grounding. Moreover, LLMs support multi-task distillation (e.g., joint training on ranking, generation, and explanation), enabling compressed models to generalize across diferent RecSys objectives [36, 127].

<sub>Prompt-Eficient</sub> <sub>Inference</sub> <sub>–</sub> Instead of full fine-tuning, prompting leverages frozen LLMs through task-specific prompts, reducing training and inference costs. Lightweight adapters such as LoRA [67] or prompt tuning [104] inject minimal learnable parameters. TikTok’s SAM [257] and Meta’s InstructRec [158] demonstrate that prompt-based systems can generate high-quality recommendations with low inference overhead by delegating semantic understanding to pretrained LLMs.

<sub>Two-Stage</sub> <sub>Hybrid</sub> <sub>LLM</sub> <sub>Pipelines</sub> <sub>–</sub> To balance latency and accuracy, modern recommender systems often adopt a two-stage hybrid architecture where LLMs are reserved for re-ranking a small subset of items. The first stage rapidly retrieves a candidate set $C ( u )$ using lightweight methods such as approximate nearest neighbor (ANN) search, sparse two-tower models, or collaborative filtering:

$$
\mathcal {C} (u) = \mathrm{Top-k} \left(g _ {\mathrm{fast}} (u, \mathcal {I})\right),
$$

where $g _ { \mathrm { f a s t } }$ denotes a fast retrieval model and <sub>I</sub> is the full item corpus.

In the second stage, an LLM is applied only to the candidate set to compute semantic-aware or explanation-based scores:

$$
\hat {r} _ {u i} = \mathrm{LLM} _ {\mathrm{rank}} (“ \mathrm{User:} ” + x _ {u} + “ \mathrm{Item:} ” + x _ {i}), \quad \forall i \in C (u),
$$

where $x _ { u }$ and $x _ { i }$ are user/item textual features. This approach reduces computational complexity from $O ( | \boldsymbol { \cal T } | )$ to $O ( k )$ LLM inferences per user.

Platforms like YouTube [32], Amazon Alexa [53], and OpenAI’s plugin-based LLM recsys [117] leverage this pipeline to combine the speed of traditional retrieval with the contextual reasoning power of LLMs. The hybrid setup enables real-time ranking with rich personalization, especially useful for high-value sessions where semantic intent understanding is critical.

<sub>Sparse</sub> <sub>Activation</sub> <sub>Architectures</sub> <sub>–</sub> Sparse Mixture of Experts(see Figure 8) models activate only a subset of parameters during inference, scaling to billions of weights without proportional cost [103, 288]. For recommender systems, LLM-based MoE allows selective activation based on user intent or domain — as shown in GLaM [39], Switch-LLM [42], and V-MoE [180], which uses sparsity to optimize vision transformer inference. Amazon’s M6-T [123] and DeepMind’s GopherMoE [172] extend this approach for multi-task retrieval, recommendation, and generation

![](images/c11a6c368d9f8b23b2988730c9cda9ad0ab31df0cb27b6a79d82e169153debe1.jpg)  
Fig. 8. Illustration of a Sparse Mixture-of-Experts (MoE) layer where a gating network dynamically routes input tokens to a subset of experts. Only the top-k experts are activated per input, enabling eficient computation and scalability within Transformer architectures. [194]

This reduces efective inference complexity:

$$
\tau_ {\mathrm{sparse}} \approx \sum_ {l = 1} ^ {L} \rho_ {l} \cdot C _ {l},
$$

where $\rho _ { l } < 1$ is the fraction of active experts per layer. This enables real-time deployment of massive models with acceptable latency across domains like content recommendation, product search, and voice assistant personalization [39, 123].

<sub>4.2.3</sub> <sub>Long-Tail</sub> <sub>Modeling.</sub> Recommender systems often struggle to surface long-tail items—such as niche books, indie music, or specialty software—due to their limited interaction history. Despite their sparse visibility, these items are vital for catalog coverage, serendipitous discovery, and platform health. Tail user segments also pose a challenge, as insuficient behavioral signals prevent traditional collaborative models from generalizing efectively. The ranking function often biases toward popularity, formalized as:

$$
R (i) = \lambda \cdot \mathrm{Rel} (i, u) + (1 - \lambda) \cdot \log (1 + \mathrm{Pop} (i)),\tag{4}
$$

where $\operatorname { R e l } ( i , u )$ denotes predicted user-item relevance, Pop<sub>(</sub>??<sub>)</sub> is a popularity prior, and $\lambda \in$ <sub>[</sub>0, 1<sub>]</sub> balances relevance against popularity bias. A small ?? skews the model towards head items, suppressing cold and long-tail entities. The following subsections discuss how long tail modeling can be solved using LLMs.

<sub>Content-Enriched</sub> <sub>Generation</sub> <sub>via</sub> <sub>LLMs</sub> <sub>–</sub> Instruction-tuned and generative LLMs can amplify long-tail items by transforming sparse metadata—such as item title, genre, and a few tags—into rich natural language content. This enrichment process enables the generation of auxiliary textual descriptions that go beyond what the metadata can ofer, capturing user-interpretable attributes like sentiment, intended audience, or stylistic nuances. These generated descriptions are particularly valuable for downstream modules that convert them into dense embeddings for retrieval or use them as features in ranking pipelines. Models such as GenRec[261] and LLMRec[82] operationalize this approach to semantically bootstrap cold items in settings where traditional user signals (e.g., clicks, reviews) are absent or unreliable. Moreover, content enrichment fosters explainability, as the LLM-produced narratives can be exposed to users, improving trust in recommendations.

![](images/38019ad1ff2a1bf6449b3e28b994474ce371301c0b353abba31afa67bde161a4.jpg)  
Fig. 9. The overall framework architecture of the proposed Llama4Rec consists of two main components: mutual augmentation and adaptive aggregation [141].

<sub>Retrieval-Augmented</sub> <sub>Tail</sub> <sub>Expansion</sub> <sub>–</sub> Tail items often sufer from cold-start issues due to minimal or no user engagement. Retrieval-Augmented Generation (RAG) frameworks alleviate this by fetching external content such as similar item reviews, frequently co-viewed products, or question–answer forums that ofer surrogate interaction signals. These retrieved contexts act as priors, conditioning the LLM to produce recommendations or relevance scores with greater semantic grounding. Formally, the decoder incorporates $\mathcal { R } ( x _ { i } )$ , the retrieved context for item $x _ { i } ,$ to better personalize outputs for user $x _ { u }$ . This paradigm has gained real-world traction in platforms like Amazon and Spotify [217, 229], where hybrid systems interleave retrieval and generation in ranking. Public systems such as RAG [105] and PromptRec [36] provide open-source implementations of this approach. RAG mechanisms also allow continual updates to item knowledge without re-training the LLM, ofering scalability for dynamic catalogs.

<sub>Tail-Aware</sub> <sub>Few-Shot</sub> <sub>Prompting</sub> <sub>–</sub> Tail personalization often sufers from a lack of examples for supervised training. Few-shot prompting provides a lightweight alternative by seeding the LLM with a handful of examples reflecting the user’s preference for under-represented or niche content. The LLM then generalizes to semantically similar items using its pretrained knowledge and instructionfollowing capabilities. This strategy has been demonstrated efectively using InstructGPT[158] and FLAN-T5[30], with additional improvements observed in domain-specific instruction fine tuning [228]. Few-shot prompts can be curated based on recent tail interactions or inferred taste clusters and can dynamically adapt over time. This avoids overfitting to mainstream popularity signals and ensures that users with atypical preferences still receive relevant recommendations.

<sub>Multimodal</sub> <sub>Tail</sub> <sub>Representation</sub> <sub>–</sub> In domains such as music, video, and fashion, textual metadata alone may be insuficient to describe tail items meaningfully. LLMs, when integrated with multimodal encoders, can create composite representations that incorporate audio, visual, and textual cues. For example, a tail music track with few plays but distinctive sonic features (e.g., melancholic guitar tones) can be described and embedded more efectively when frame-level audio representations are fused with text prompts. This multimodal fusion has been operationalized in Spotify’s neural content-based systems [217] and Meta’s cross-modal embedding infrastructure [211]. In these systems, the LLM serves as a controller or semantic summarizer that unifies heterogeneous signals. This is particularly useful for catalog-wide embeddings and cold-start re-ranking, where modality-specific insights are critical for disambiguation.

LLMs enable generative enrichment, retrieval-augmented scoring, and prompt-based personal ization that help surface long-tail items with minimal user history. Combined with diversity-based re-ranking and multimodal inference, these methods promote catalog depth, reduce popularity bias, and enhance the discovery of rare but relevant content. Table 4 provides an overview of prompt-based strategies that facilitate scalable personalization of long-tail items by leveraging content generation, retrieval augmentation, interaction simulation, and multimodal representation.

<table><tr><td>Strategy</td><td>Example Prompt</td></tr><tr><td>Content-Enriched Generation</td><td>Describe the appeal of this item: [Title], [Genre], [Few Tags]</td></tr><tr><td>Retrieval-Augmented Expansion</td><td>Given item [X] and retrieved content [Y], summarize relevance for user [U]</td></tr><tr><td>Pseudo-Interaction Simulation</td><td>Simulate user feedback for this product: [Metadata], [Price], [Tags]</td></tr><tr><td>Diversity-Aware Re-ranking</td><td>Rank items [A, B, C] to balance relevance and novelty for user [U]</td></tr><tr><td>Few-Shot Tail Prompting</td><td>User liked niche item A and indie item B. Recommend similar items.</td></tr><tr><td>Multimodal Tail Embedding</td><td>Music Genre: Indie. Tags: Melancholy, Guitar. Description: ...</td></tr></table>

Table 4. Canonical LLM Prompts for Tail Personalization Strategies.

## 4.3 Evaluation and Experimentation Challenges

Evaluation in recommender systems is inherently constrained by the ofline-online discrepancy, label sparsity, and the delayed nature of user feedback. Traditional pipelines rely heavily on historical logs and costly online experiments, which often fail to capture long-term or latent efects. LLMs with their ability to model complex distributions and perform conditional reasoning over structured and unstructured inputs, ofer a new framework for addressing these limitations. By encoding user-item dynamics and simulating plausible interactions, LLMs introduce new avenues for counterfactual estimation and representation-aligned evaluation under uncertainty.

Risk and Auditability Matrix for LLM Deployment. Diferent integration strategies expose different vulnerabilities. Template-bound prompting ofers improved compliance, while full LLM generation requires enhanced auditing and safety layers

<sub>4.3.1</sub> <sub>Ofline-Online</sub> <sub>Gap.</sub> A persistent challenge in recommender systems is the misalignment between <sub>ofline</sub> <sub>evaluation</sub> <sub>metrics</sub>—such as NDCG, Recall@K, or MAP—and <sub>online</sub> <sub>outcomes</sub> like click-through rate (CTR), average revenue per user (ARPU), dwell time, or long-term user retention. Ofline evaluations, though eficient and repeatable, rely on logged interactions that are inherently biased, counterfactual-incomplete, and incapable of modeling complex user feedback loops in live systems [51, 72, 182].

This mismatch can be formalized as a <sub>metric</sub> <sub>divergence</sub>:

$$
\Delta = | \text { Offline } (M) - \text { Online } (M) |,\tag{5}
$$

where Ofline<sub>(</sub>??<sub>)</sub> denotes the ofline performance on held-out logs, and Online<sub>(</sub>??<sub>)</sub> reflects realtime KPIs measured through randomized experiments. A high <sub>Δ</sub> indicates a model that overfits to ofline biases and fails to generalize, a well-documented issue in industry [145]. To mitigate this, recent research introduces <sub>LLM-augmented</sub> <sub>evaluation</sub>, using generative models to simulate user behavior, judge relevance, interpret session trajectories, and even generate new metrics. These methods ofer <sub>soft</sub> <sub>evaluations</sub> that capture user-centric signals without requiring live deployment. Table 5 provides a summary of representative prompts used in each evaluation strategy.

Counterfactual Evaluation via Prompt-Based Simulators <sup>Instruction-tuned</sup> <sup>LLMs</sup> <sup>can</sup> approximate <sub>click-through</sub> <sub>likelihood</sub> on hypothetical slates never observed in logs. Given a logged user context ??<sub>??</sub>—which may include past clicks, interests, or demographic cues—and a new candidate list $\mathcal { L } = \left[ x _ { 1 } , \ldots , x _ { k } \right]$ , the LLM estimates a soft label $\hat { y } _ { u i } ^ { \mathrm { c f } } \in [ 0 , 1 ]$ for each item.

This counterfactual simulation approach has been operationalized in LLMRecSim [150], where synthetic feedback is used to evaluate model changes before online testing. Unlike traditional inverse propensity scoring (IPS), which sufers from variance and truncation bias [31], LLM simulators provide a semantically grounded and low-variance signal, particularly for tail items or unseen slates [64]. It also scales to <sub>few-shot</sub> <sub>personalization</sub>, as prompting is stateless and does not require user embeddings.

Ofline Metric Recalibration via Generative Relevance Scoring <sup>Sparse</sup> <sup>interactions</sup> <sup>and</sup> missing negatives pose a challenge for ofline evaluation [115]. LLMs can act as <sub>neural</sub> <sub>annotators</sub>, scoring item–user relevance based on textual metadata and recent behavior. For each candidate $x _ { i }$ a generative model produces a soft score:

$$
\tilde {r} _ {u i} ^ {\mathrm{LLM}} = \text { sigmoid } (\mathrm{LLM} (x _ {i}, c _ {u}, \text {"How relevant is this item?"})
$$

These scores can be aggregated to construct <sub>hybrid</sub> <sub>metrics</sub>:

$$
\operatorname{HybridScore} (M) = \alpha \cdot \operatorname{Recall} @ \mathrm{K} + (1 - \alpha) \cdot \mathbb {E} _ {i \in \mathcal {L}} [ \tilde {r} _ {u i} ^ {\mathrm{LLM}} ]
$$

This method provides two key advantages. First, it generates a <sub>dense</sub> <sub>supervision</sub> <sub>signal</sub> by assigning relevance scores to all items in the slate, not just those with observed feedback. Second, it captures <sub>semantic</sub> <sub>nuance</sub> by evaluating item relevance in context, going beyond simple binary indi cators such as click or no-click. As demonstrated in recent work [237], these LLM-augmented hybrid metrics exhibit stronger correlation with online A/B test outcomes, particularly in challenging scenarios like cold-start items and zero-shot generalization.

<sub>Behavior-Level</sub> <sub>Satisfaction</sub> <sub>Estimation</sub> Standard evaluation pipelines often overlook sessionlevel dynamics such as skip behavior, bounce patterns, or implicit dissatisfaction. LLMs can ingest multi-event traces (e.g., click, hover, dwell) and output an <sub>aggregated</sub> <sub>satisfaction</sub> <sub>score</sub> $\hat { s } _ { u } \in [ 0 , 1 ]$ ofering a continuous proxy for session quality.

This approach enables modeling <sub>latent</sub> <sub>engagement</sub> beyond immediate reward [273]. For example, an LLM can infer that a user clicking one item and then immediately leaving the session implies low satisfaction. Such modeling has been leveraged for predicting <sub>churn</sub> <sub>risk</sub>, <sub>bounce</sub> <sub>rate</sub>, and <sub>post-click</sub> <sub>engagement</sub> in session-level optimizers [100, 258].

Interactive User Simulation with Agentic LLMs <sup>-</sup> <sup>Recent</sup> <sup>work</sup> <sup>explores</sup> <sup>the</sup> <sup>use</sup> <sup>of</sup> agentic <sub>LLMs</sub> to simulate user behavior in recommendation environments by modeling step-wise decision making [192]. Rather than assigning static scores to items, these simulators generate coherent sequences of actions (e.g., clicks, skips, or queries) in response to a given slate and user intent. These agentic simulations are useful for analyzing qualitative aspects of model behavior and stress-testing recommendation strategies, especially in early prototyping stages [8]. Although these approaches show promise, they currently complement rather than replace standard evaluation pipelines [121]. Their outputs are best interpreted as <sub>qualitative</sub> <sub>user</sub> <sub>emulations</sub>, helpful for generating synthetic feedback, debugging content selection logic, and exploring what-if scenarios.

Importantly, the fidelity of such simulations is bounded by the quality of prompting and pretraining data, and they are not yet suitable for high-stakes quantitative evaluation such as A/B testing or reward estimation. However, as LLMs evolve and become better calibrated to user preferences, their use in long-horizon modeling and controlled counterfactual generation may become increasingly viable.

Evaluation Metric Generation via Domain-Specific Prompting <sup>Finally,</sup> <sup>LLMs</sup> <sup>can</sup> <sup>be</sup> prompted to construct <sub>custom</sub> <sub>evaluation</sub> <sub>metrics</sub> based on evolving product goals. For instance, one can request a metric that balances fairness, diversity, and monetization. The LLM synthesizes a formula or qualitative description, which can then guide model development or become a reward function. LLMs also enable <sub>pairwise</sub> <sub>comparison</sub> of ranking slates. Given two model outputs $\mathcal { L } _ { A }$ and $\mathcal { L } _ { B }$ , the LLM returns a probabilistic preference $\mathbb { P } ( \mathcal { L } _ { A } \succ \mathcal { L } _ { B } )$ along with natural language justification. This facilitates ranking model selection even in ambiguous contexts.

This method has been used to build LLMJudge datasets [281], which train reward models used in <sub>RLHF</sub> pipelines. Pairwise LLM judgments are also interpretable, allowing auditors and product teams to inspect rationales behind preference reversals, and enabling <sub>transparent</sub> <sub>evaluation</sub> of recommender quality.

This capability is especially useful for platforms with <sub>frequent</sub> <sub>A/B</sub> <sub>experimentation</sub> and changing KPI priorities. Prototype systems such as GPTMetrics [132] and EvalTemplate [241] show how textual descriptions of business needs can be turned into reusable evaluation templates.

<table><tr><td>Evaluation Technique</td><td>Example Prompt</td></tr><tr><td>Counterfactual User Simulation</td><td>Given the user&#x27;s past behavior, would they click any of these items: [title 1], [title 2], [title 3]?</td></tr><tr><td>Generative Relevance Scoring</td><td>How relevant is [item] for this user given their context?</td></tr><tr><td>Behavior-Level Satisfaction</td><td>The user clicked x_1, skipped x_2, then bounced. How satisfying was this session?</td></tr><tr><td>Agentic User Simulation</td><td>You are a user interested in cooking. You are shown these recipes: [...]. What do you do next?</td></tr><tr><td>Pairwise Slate Comparison</td><td>Which list is better for the user based on relevance and novelty? Explain briefly.</td></tr><tr><td>Dynamic Metric Construction</td><td>Define a metric that optimizes for: 1) relevance, 2) fairness, and 3) revenue per click.</td></tr></table>

Table 5. LLM-Based Prompting Techniques for Evaluation in Recommender Systems.

<sub>4.3.2</sub> <sub>Sparse</sub> <sub>Conversion</sub> <sub>Labels.</sub> Many downstream objectives—such as purchases, subscriptions, or upgrades—occur with extremely low frequency compared to higher-volume user actions like impressions or clicks. This severe class imbalance challenges the efectiveness of supervised learning models, which tend to be biased toward negative instances due to limited availability of positive signals.

Formally, we define the sparsity ratio as:

$$
\text { Sparsity } = \frac {| \mathcal {Y} ^ {+} |}{| \mathcal {Y} |}, \quad \text { with } \quad \text { Sparsity } \ll 1,\tag{6}
$$

where $y ^ { + }$ denotes the set of positive conversion events, and <sub>Y</sub> the total set of observations. Platforms such as Amazon and Etsy routinely encounter purchase conversion rates as low as 0.1%–1% [178, 221], severely constraining training signals and model generalization for rare out comes.

To address this, LLMs have emerged as a powerful tool for generating <sub>pseudo-labels</sub>, <sub>soft</sub> <sub>targets</sub>, or <sub>context-aware</sub> <sub>weights</sub>, enriching the sparse label space through prompt-based learning. Table 6 provides representative prompts aligned with five major augmentation strategies.

<table><tr><td>Technique</td><td>Example Prompt</td></tr><tr><td>Proxy Signal Augmentation</td><td>User clicked on item X after viewing similar items and spent 12 seconds on its page. Predict the likelihood of purchase.</td></tr><tr><td>Instruction-Tuned Imputation</td><td>Given that the user added item X to the cart but did not purchase it, and has a history of completing 80% of carted items, estimate whether they would convert.</td></tr><tr><td>Generative Multi-Task Learning</td><td>Generate a review the user might write after purchasing this item.</td></tr><tr><td>Counterfactual Label Reasoning</td><td>If the user had been shown this product at the top of the list instead of rank 9, would they have purchased it?</td></tr><tr><td>Language-Guided Reweighting</td><td>The user likely did not purchase this item due to price, not relevance. Assign low training importance.</td></tr></table>

Table 6. LLM Prompting Strategies for Sparse Label Augmentation.

<sub>Proxy</sub> <sub>Signal</sub> <sub>Augmentation</sub> <sub>via</sub> <sub>LLMs</sub> <sub>-</sub> When labeled conversions are scarce, LLMs can extrapolate soft labels from partial interaction data such as clicks, dwell time, or page visits. The generated score $\hat { y } _ { u i } ^ { \mathrm { s o f t } } = \sigma ( \mathrm { L L M } ( x _ { u } , x _ { i } ) )$ can serve as a training target in binary classification or ranking setups. A representative prompt is shown in Table 6. This is especially valuable in semi supervised learning regimes, where high-coverage but noisy labels can bridge the sparsity gap and enhance downstream recall [36, 257, 261].

<sub>Instruction-Tuned</sub> <sub>Label</sub> <sub>Imputation</sub> <sub>-</sub> Instruction-following LLMs can reason about partial conversion traces and historical behavior patterns to impute likely outcomes. By grounding prompts in known priors (e.g., 80% cart completion rate), the LLM generates pseudo-labels that reflect domainspecific user propensities [234]. These labels may be used with calibration techniques such as temperature scaling or uncertainty thresholds.

<sub>Generative</sub> <sub>Multi-Task</sub> <sub>Learning</sub> <sub>-</sub> Instead of predicting a binary purchase label, LLMs can be asked to generate complementary signals—such as hypothetical product reviews, post-purchase behaviors, or satisfaction levels [46]. These outputs act as auxiliary supervision in a joint loss

framework:

$$
\mathcal {L} _ {\mathrm{total}} = \lambda_ {1} \mathcal {L} _ {\mathrm{purchase}} + \lambda_ {2} \mathcal {L} _ {\mathrm{review}} + \lambda_ {3} \mathcal {L} _ {\mathrm{click}}
$$

This structure encourages the model to embed rich semantic cues into the prediction, enhancing learning even when sparse labels dominate.

<sub>Counterfactual</sub> <sub>Label</sub> <sub>Reasoning</sub> <sub>-</sub> By modeling alternative exposure scenarios, LLMs can simulate user behavior under diferent treatment conditions—akin to causal inference [80]. For example, querying how a user might respond if shown a product earlier in the ranking can produce an uplift score $\mathcal { \bar { Y } } _ { u i } ^ { \mathrm { c f } }$ that feeds into counterfactual or inverse propensity models. This strategy supports personalized re-ranking and policy evaluation under data drift. Refer to Table 6 for a prompt illustration.

<sub>Language-Guided</sub> <sub>Reweighting</sub> <sub>-</sub> LLMs can assess the reliability of labels based on context and user intent, generating natural-language justifications that map to importance weights $w _ { u i }$ These weights modulate the binary cross-entropy loss:

$$
\mathcal {L} = \sum_ {(u, i)} w _ {u i} \cdot \mathrm{BCE} (y _ {u i}, \hat {y} _ {u i})
$$

This reduces overfitting to noisy negatives (e.g., price-rejected items) and reinforces relevance-aware supervision [205]. See Table 6 for an example of prompt-based explanation used for weighting.

4.3.3 Balancing Immediate Engagement with Long-Term User Value. <sup>Recommender</sup> <sup>systems</sup> <sup>that</sup> focus exclusively on short-term engagement metrics (e.g., clicks, watch time) often degrade long term user satisfaction, retention, and platform trust. This discrepancy arises because short-term optimization may exploit transient user impulses while ignoring lasting preferences or well-being. The long-term utility of a recommendation policy ?? can be modeled using a cumulative discounted reward:

$$
\mathcal {J} (\pi) = \mathbb {E} _ {\pi} \left[ \sum_ {t = 0} ^ {T} \gamma^ {t} \mathcal {R} _ {t} \right],\tag{7}
$$

where $\gamma \in \ [ 0 , 1 ]$ is the temporal discount factor, and $\mathcal { R } _ { t }$ captures immediate or future user rewards $( \mathrm { e . g . }$ , session return, app uninstall, subscription upgrade). Conventional supervised learning pipelines often ignore $\mathcal { R } _ { t > 0 }$ and instead treat only $\mathcal { R } _ { 0 }$ (e.g., click) as the ground truth, leading to reward myopia.

To address this, LLMs can be leveraged for long-horizon modeling through prompt-based estimation, simulation, and summarization. Table 7 provides representative prompts used across these strategies.

<sub>LLM-Based</sub> <sub>Proxy</sub> <sub>Reward</sub> <sub>Estimation</sub> <sub>-</sub> Instruction-tuned LLMs can infer latent user satisfaction from event sequences even when explicit labels are missing. A short dwell-time burst after multiple clicks, for instance, may signal dissatisfaction; treating the LLM’s inferred reward as a soft label lets us optimize <sub>J</sub> beyond surface-level clicks. Recent work on RL from human feedback for recommendation [245] shows that such proxy rewards significantly improve long-horizon utility prediction.

<sub>Counterfactual</sub> <sub>Dialogue</sub> <sub>for</sub> <sub>Future</sub> <sub>Intent</sub> <sub>-</sub> Interactive LLM agents elicit long-term intent through clarification dialogue, distinguishing ephemeral curiosity from persistent preference. User replies are encoded as

$$
\mathbf {u} _ {\text { long }} = f _ {\text { LLM }} (\text { user\_reply }),
$$

, Vol. 1, No. 1, Article . Publication date: October 2025.

<table><tr><td>Technique</td><td>Example Prompt</td></tr><tr><td>Proxy Reward Estimation</td><td>User clicked but exited early. Was this a satisfying experience?</td></tr><tr><td>Counterfactual Dialogue</td><td>Do you want to see more content like this, or was this just a one-time interest?</td></tr><tr><td>Generative Rollouts</td><td>Predict reward at step $t$ given prior context.</td></tr><tr><td>Preference Drift Summarization</td><td>Summarize user&#x27;s persistent interests from sessions  $S_u$ </td></tr><tr><td>Reward Decomposition</td><td>Assess dimension i (e.g., novelty, credibility) of this interaction.</td></tr></table>

Table 7. LLM Prompting Strategies for Modeling Long-Term User Value.

and injected into evolving user models that steer ranking toward durable interests. Conversationalintent trackers [41, 109] demonstrate that incorporating counterfactual questions markedly boosts accuracy on follow-up engagement metrics.

Multi-Horizon Simulation via Generative Rollouts - <sup>LLMs</sup> <sup>can</sup> <sup>simulate</sup> <sup>plausible</sup> <sup>future</sup> interaction trajectories, enabling ofline policy evaluation:

$$
\mathcal {J} _ {\mathrm{sim}} = \sum_ {t = 0} ^ {T} \gamma^ {t} \hat {\mathcal {R}} _ {t},
$$

where each $\textstyle { \hat { \mathcal { R } } } _ { t }$ is predicted by the LLM under a hypothesized slate. User-simulator frameworks such as SimRec [22] and UserGPT-Sim [275] report strong correlations (0.82–0.87) between simulated and real A/B outcomes.

Preference Drift Detection via Summarization - <sup>LLMs</sup> <sup>can</sup> <sup>summarize</sup> <sup>multi-session</sup> <sup>histories</sup> $S _ { u }$ into a stable embedding

$$
\mathbf {u} _ {\mathrm{stable}} = \operatorname{LLM} (\mathcal {S} _ {u}),
$$

mitigating over-reaction to transient spikes. Drift-robust models like StableRec [271] and TempRec Memory [98] show that summary-based regularization reduces churn by up to 6

Multi-Objective RL with LLM-Guided Reward Decomposition - <sup>Conventional</sup> <sup>recommender</sup> systems often rely on scalar reward functions—such as click-through rate or dwell time—to optimize ranking policies. However, such metrics are typically coarse and do not reflect the nuanced trade-ofs between diferent dimensions of user value, such as novelty, credibility, informativeness, or diversity. To address this, large language models (LLMs) can be employed to decompose scalar rewards into interpretable sub-components, enabling more principled and aligned decision-making [29, 133, 286].

Formally, the overall reward at time ?? can be factorized as:

$$
\mathcal {R} _ {t} = \sum_ {i = 1} ^ {k} \beta_ {i} \cdot \mathcal {R} _ {t} ^ {(i)}, \quad \mathrm{where} \quad \mathcal {R} _ {t} ^ {(i)} = \mathrm{LLM} (x _ {t} ^ {(i)})
$$

Here, $\mathcal { R } _ { t } ^ { ( i ) }$ denotes the reward signal corresponding to a specific semantic dimension ??, and $\beta _ { i }$ controls its relative importance in the composite objective. The inputs $\boldsymbol { x } _ { t } ^ { ( i ) }$ encode relevant features, such as item content, user context, and interaction history, which the LLM interprets to produce value-specific assessments.

This decomposition enables multi-objective reinforcement learning (RL), where policies are trained not just to maximize immediate engagement, but also to respect domain-specific constraints and user-aligned values [142, 225]. The resulting objective:

$$
\mathcal {J} (\boldsymbol {\pi}) = \mathbb {E} _ {\boldsymbol {\pi}} \left[ \sum_ {t = 0} ^ {T} \gamma^ {t} \sum_ {i = 1} ^ {k} \beta_ {i} \cdot \mathcal {R} _ {t} ^ {(i)} \right]
$$

allows platform designers to balance competing goals (e.g., serendipity vs. relevance, diversity vs. coherence) and adapt these trade-ofs dynamically based on context or fairness criteria [148].

LLMs are particularly useful in this setting because they can produce rich natural language rationales [248], which in turn facilitate both post-hoc auditability and direct supervision for training $\mathcal { R } _ { t } ^ { ( i ) }$ components. This also enables human-in-the-loop reward shaping, where qualitative feedback on system behavior can be converted into actionable alignment signals [7, 280].

## 6 Conclusion

LLMs represent a transformative shift in the architecture and design philosophy of recommender systems. By enabling contextual reasoning, zero-shot personalization, and multimodal representation learning, LLMs transcend the limitations of traditional matrix factorization, collaborative filtering, and feed-forward neural architectures. Rather than relying solely on historical interaction data and engineered features, LLM-augmented pipelines can synthesize user intent, simulate plausible behaviors, and generate semantically enriched item representations from natural language descriptions, reviews, and metadata. This capability significantly enhances performance in cold-start, long-tail, and rapidly evolving user contexts.

Throughout this paper, we examined how LLMs can be strategically integrated into various stages of industrial recommender pipelines—from candidate generation and reranking to feedback interpretation and synthetic evaluation. Our analysis demonstrated that LLMs not only ofer improvements in semantic fidelity and explainability but also introduce opportunities for conversational and intent-driven recommendation paradigms. Techniques such as retrieval-augmented generation, prompt-based reranking, and hybrid collaborative-semantic scoring models exemplify how LLMs can coexist with traditional recommenders to achieve both robustness and expressivity.

However, this integration is not without its challenges. LLM-based systems pose significant barriers in latency-sensitive environments, where autoregressive decoding and token-based computation are at odds with sub-second serving constraints. Furthermore, issues such as prompt brittleness, hallucinated outputs, representation drift across model versions, and inconsistent personalization responses necessitate new debugging, logging, and evaluation toolchains. These technical hurdles are further complicated by operational constraints, including privacy compliance (e.g., GDPR, CCPA), prompt injection vulnerabilities, and the lack of interpretability guarantees in generative outputs. To realize the full potential of LLMs in recommender systems, future research must address the foundational tension between expressivity and eficiency. Robust prompt design and caching strategies, low-latency inference via distilled or quantized models, and standardized protocols for prompt versioning and auditability will be critical for production readiness. In parallel, new forms of evaluation that combine qualitative user modeling, counterfactual simulation, and LLM-driven assessments are needed to measure real-world efectiveness beyond traditional top-?? metrics.

[已省略: references]


---

## 📑 关键章节 | EARN: Eficient Inference Acceleration for LLM-based Generative Recommendation by Register Tokens

**arXiv ID**: [2507.00715](https://arxiv.org/abs/2507.00715)

## 1 Introduction

Recently, Large Language Model (LLM)-based generative recommendation (LLMRec) has shown great potential due to its superior reasoning capabilities [10, 16, 20–22, 36, 38]. However, it sufers from high inference latency due to its massive model architecture and auto-regressive decoding paradigm, which severely limits its application in practical recommendation scenarios [12, 37, 44]. For instance, platforms like YouTube, which serve hundreds of millions of users daily with billions of interactions, require millisecond-level response times<sup>1</sup>. This highlights the stark eficiency gap between current LLMRec implementations and real-world application requirements. Therefore, enhancing the inference eficiency of LLM-Rec is a crucial issue for industrial applications.

![](images/0bc9a10217a509aad4e91e24f7df1bc053c7e5be3113dac868c52b64a7b5c559.jpg)  
Figure 1: The inference process of LLMRec. In the prefilling stage, LLM computes the initial KV Cache and generates the first token of the output; in the decoding stage, LLM updates the KV Cache and generates subsequent tokens one by one.

stages. As shown in Figure 1, given the input token sequence (user profile, historical interactions, etc.), the first is the prefilling stage, where LLM generates the first token of the output and caches computed Key-Value state pairs of all layers for every token. The second is the decoding stage, where LLM generates subsequent tokens autoregressively using pre-computed KV Cache, and updates KV Cache in each decoding step. As the input sequence length increases, the computational overhead of KV Cache grows greatly, significantly prolonging the inference latency. And when the KV Cache size is large, each decoding step requires accessing a substantial amount of memory, which can severely slow down the inference. In light of the above, the key to accelerating the inference of LLMRec lies in reducing the size of KV Cache.

To address this challenge, some research has been proposed. One of the representative works is cache compression [27, 44]. It selec tively removes less important KV pairs to reduce KV Cache size during decoding. However, recommendation tasks typically require few decoding steps to generate short output token sequences, such as item identifiers (around 1 to 5 tokens), limiting their acceleration potential in decoding. Another method is prompt compression [17, 44], which reduces initial KV Cache size during prefilling by condensating the input sequences, for instance, deleting unim portant tokens [14] or compressing the token sequence into a few tokens [18]. This technique not only decreases the computational load in prefilling but also alleviates the memory pressure in decoding. Although this method has achieved success in NLP [17, 44], it struggles to balance eficiency and accuracy in the context of LLMRec. In LLMRec, it is dificult to distinguish between important and unimportant items, which makes prompt compression method prone to discard crucial user interaction information, resulting in severe accuracy losses, or fail to achieve satisfactory acceleration in an efort to retain information. Hence, there is an urgent need for a method that enhances inference eficiency while preserving recommendation efectiveness.

To this end, we identify which information can be safely com pressed in LLMRec, by inspecting the attention score distributions [40] in LLMRec. Along two critical dimensions: layer order and token position, we observe two key characteristics of LLM-Rec across three diverse datasets, two mainstream LLMRec methods, and two distinct LLM architectures. For example, as shown in Figure 2, on the Llama model and Beauty dataset, we found the following (more similar evidence can be found in Appendix A.1):

![](images/8caee2ece755723099fe47764396ad2911f98be5fd44f08684f25c9efe1945d8.jpg)  
Figure 2: The attention distributions of diferent layers on the NLP task (reading comprehension QA) and the LLMRec task (LC-Rec on Beauty dataset) on Head 0 of Llama model. In the LLMRec task, the first three layers are relatively dense, while subsequent layers are sparse, with sinking occurring on the head and tail tokens.

• Layer-wise attention sparsity inversion. Along the layer order dimension, we observe distinct sparsity between the NLP task and the LLMRec task. In the NLP task, the attention score distribution is sparse in the initial layers, but becomes relatively less sparse in the later layers (Sparsity: 0<sup>.</sup>06 → 0<sup>.</sup>03). Conversely, in the LLMRec task, the initial layers exhibit a relatively denser attention distribution, while the subsequent layers are highly sparse (Sparsity: 0<sup>.</sup>01 → 0<sup>.</sup>07).

• Dual attention sinks phenomenon. Along the token position dimension, while both the NLP task and the LLMRec task exhibit attention sinks [40], which means attention scores are highly concentrated on specific token positions, their distributions difer significantly. In the NLP task, sinks primarily emerge at the initial positions and a broad range of later tokens. In contrast, LLMRec demonstrates a distinctive dual concentration pattern - strong attention sinks at both head positions and a narrow tail region.

These findings suggest that in LLMRec: 1) In terms of the layer order, the early layers contain richer information, while the middle tokens in the later layers are redundant. In fact, previous studies have shown that the early layers of LLMs are capable of summarizing required information and important tokens [32], while the later layers tend to be increasingly redundant, and pruning of redundant parts has minimal impact on performance [13]. 2) In terms of the token position, the head and tail tokens carry the most important information. As explained in prior studies [7, 40], head tokens can absorb excess attention. Meanwhile, tail tokens interact with all previous tokens, which suggests that tail tokens of the prompt may possess the potential to summarize the preceding user interaction information.

Inspired by the above observations, we propose EARN, an Eficient inference Acceleration method for LLM-based Recommendation by register tokens (Figure 3), to enhance inference eficiency while maintaining recommendation efectiveness. Specifically, EARN introduces prefix and sufix register tokens - several learnable virtual tokens placed at the beginning and end of the input sequence, and leverages the first k layers of LLM to compress the user’s historical interaction information into register tokens. During inference, we use only register tokens for computation after k layers, thereby reducing the computational load and memory footprint of the KV Cache. We instantiate EARN on two mainstream LLMRec meth ods with two distinct LLM architectures, and conduct extensive experiments on three real-world datasets, validating the superiority of EARN in terms of both eficiency and accuracy. The code and datasets are available at https://github.com/transcend-0/EARN.

The contributions of our work are manifold:

• We identify the layer-wise attention sparsity inversion and dual attention sinks phenomenon in LLMRec, revealing that early layers as well as both head and tail tokens, retain the most critical information for LLMRec.

• We propose an eficient and efective method that leverages reg ister tokens to compress user historical interactions and prune redundant computations in later layers, striking a delicate balance between inference eficiency and recommendation efectiveness.

• We validate the efectiveness of EARN through extensive experiments conducted on three real-world datasets, demonstrating the superiority of EARN in achieving both high inference speed and recommendation accuracy.

[已省略: 2 preliminary]

## 3 Method

In order to improve the inference eficiency while ensuring the recommendation efectiveness, we proposed EARN, which achieves inference acceleration through register tokens. The overview of our method is presented in Figure 3.

## 3.3 Eficiency Analysis

Due to the removal of prompt tokens in the subsequent layers, we can significantly reduce both the computational load and memory footprint. Assume the model has <sup>??</sup> layers, $n _ { h }$ heads, an attention dimension of $d _ { a } ,$ a hidden state dimension of $d _ { h }$ , and an intermediate dimension of $d _ { f }$ . The length of the input prompt is $L ,$ , and the number of register tokens is $r \ \ll L .$ . If we remove the prompt tokens after <sup>??</sup> layers, the eficiency promotion can be analyzed through three key aspects:

• Computation Complexity: The FLOPs of the vanilla LLM are <sup>??</sup> $F L O P s _ { L L M l a y e r } = 4 N L [ n _ { h } d _ { a } ( 2 d _ { h } + L ) + d _ { h } d _ { f } ]$ (see Appendix $\mathrm { A } . 2$ for detailed derivation). In our EARN, it becomes $k F L O P s _ { L L M \ : l a y e r } + ( N - k ) \ : F L O P s _ { R e c }$ ???????????? ?????????? . Thus, the attention complexity ratio <sup>??</sup><sub>attn</sub> becomes:

$$
\begin{array}{l} \Gamma_ {a t t n} = \frac {k F L O P s _ {L L M l a y e r} + (N - k) F L O P s _ {R e g i s t e r l a y e r}}{N F L O P s _ {L L M l a y e r}} \\ \qquad = \frac {k}{N} + (1 - \frac {k}{N}) \frac {r [ n _ {h} d _ {a} (2 d _ {h} + r) + d _ {h} d _ {f} ]}{L [ n _ {h} d _ {a} (2 d _ {h} + L) + d _ {h} d _ {f} ]} \\ \qquad \approx \frac {k}{N}. \end{array}\tag{8}
$$

• KV Cache Size: The memory size of the KV Cache is $M _ { K V } N _ { K V }$ where $M _ { K V }$ represents the memory size of each KV pair, and $N _ { K V }$ denotes the total number of KV pairs. The original $N _ { K V }$ would be $n _ { h } N L$ <sup>,</sup> whereas now it becomes $n _ { h } ( k L + ( N - k ) r )$

Specifically, the KV Cache can be shrunk to $\frac { k L + ( N - k ) r } { N L }$ of its original size, reduced by $\frac { ( N - k ) ( L - r ) } { N L }$ <sup>.</sup> That is to say, the KV cache size reduction ratio $\gamma _ { \mathrm { c a c h e } }$ is:

$$
\begin{array}{c} \Gamma_ {c a c h e} = 1 - \frac {k L + (N - k) r}{N L} \\ = \frac {(N - k) (L - r)}{N L} \\ \approx \frac {N - k}{N}. \end{array}\tag{9}
$$

• Theoretical Speedup: Assuming that FLOPS of the device is $v _ { c } ,$ and HBM rate is $v _ { m }$ . The estimated time cost is

$$
T = T _ {P} + T _ {D} = T _ {P} + n _ {g e n e r a t e} T _ {d},\tag{10}
$$

where

$$
T _ {P} = \frac {F L O P s _ {p r e f i l l i n g}}{v _ {c}},\tag{11}
$$

$$
T _ {d} = \max (\frac {\text {Cache}}{v _ {m}}, \frac {\text {FLOPs} _ {\text {attn}}}{v _ {c}}) + \frac {\text {FLOPs} _ {\text {FFN}}}{v _ {c}}.\tag{12}
$$

The theoretical speedup is

$$
\Omega = \frac {T _ {v a n i l l a}}{T _ {E A R N}} \approx \frac {N}{k}.\tag{13}
$$

For typical values $( N = 3 2 , \ n _ { h } = 3 2 , \ d _ { a } = 1 2 8 , \ d _ { h } = 4 0 9 6 , d _ { f } =$ 11008<sup>,</sup> $L = 5 1 2 , \ k = 8 , \ r = 2 )$ , EARN reduces the KV Cache size to 75% of the original, and the speedup ratio can reach 4x.

## 4 Experiment

In this section, we conduct extensive experiments to answer the following research questions:

• RQ1: How does our proposed EARN perform compared to com mon inference acceleration methods?

• RQ2: How is the eficiency scalability of EARN under diferent batch sizes and sequence lengths?

• RQ3: How do diferent hyper-parameters afect the trade-of between inference eficiency and recommendation efectiveness of EARN?

• RQ4: How do diferent components contribute to EARN?

## 4.1 Experimental Settings

4.1.1 Models and Datasets. We conduct experiments on two mainstream LLMRec methods: LC-Rec [43] and TIGER [31], with two distinct LLM architectures: Llama-7B [35] using multi-head attention and Qwen2.5-7B [34] using grouped-query attention. We test EARN on three real-world recommendation datasets: 1) Beauty contains user interactions with the beauty products. 2) Games cov ers user interactions with the video games. 3) MovieLens-1M col lects user interactions with movies. More details of the datasets and experimental implementation details can be found in Appendix A.3.

4.1.2 Baselines. We compare our approach against commonly used practices and existing SOTA methods, serving as our baselines:

• Basic Methods

– Finetune: Standard full finetuning of the model.

– SkipLayers: Skipping redundant subsequent layers.

• Prompt Compression: Methods targeting the prefilling stage. – POD [11]: Distilling task instructions in the prompt into few virtual tokens.

– 500xCompressor [18]: Compressing the context (user historical interactions in our scenario) within the prompt into one single special token, by employing frozen original LLM and trainable additional LoRA parameters.

• Cache Compression: Methods targeting the decoding stage.

– StreamingLLM [40]: Statically retaining initial tokens and fixedlength recent tokens.

– SnapKV [15]: Dynamically caching clustered important tokens.

• Gist Methods: Methods using the register token idea.

– Gist [28]: Employing LLM itself to compress task instructions in the prompt into few gist tokens.

– AnLLM [30]: Employing LLM itself to compress segmented sentences into the anchor token at the end of the sentence.

4.1.3 Evaluation Metrics. Referring to previous work in the field of recommendation systems and LLM inference acceleration[8], we use the following metrics to evaluate our method:

• Time Eficiency

– Walltime Speedup <sup>??</sup>: The actual test speedup relative to vanilla auto-regressive decoding by comparing the wall clock time.

– Throughput <sup>??</sup>: The number of new tokens that the model generates per second.

• Space Eficiency

– KV Cache Reduction <sup>??</sup>: The empirically measured percentage reduction of the KV Cache.

– KV Cache Memory <sup>??</sup>: The average GPU memory usage (GB) of the KV Cache when generating the last token.

• Recommendation Efectiveness

– Recall@K (R@K): A widely used measure of the model’s ability to retrieve relevant items, which is defined as the proportion of relevant items that are recommended out of the total number of relevant items available.

– NDCG@K (N@K): Normalized Discounted Cumulative Gain (NDCG) is a measure that takes into account both the order of relevant items and the relevance score of each item.

## 4.2 Overall Performance (RQ1)

The overall results of baselines and EARN instantiated on LC-Rec on three datasets and two LLM models are presented in Table 1. The results instantiated on TIGER are similar, which are moved to Appendix A.4. We draw a few observations as follows:

• Qwen-based implementations outperform Llama-based implementations in both inference eficiency and recommendation efectiveness. This superiority arises from: 1) Qwen’s groupedhead attention architecture achieves a smaller KV Cache and lower inference latency while maintaining semantic capability; 2) Qwen’s expanded tokenizer vocabulary (151,851 vs. Llama’s 32,000) that shortens input prompts, reducing semantic fragmentation; 3) Qwen is trained on a more massive dataset with approximately 18 trillion tokens, which provides it with a richer knowledge base and better language understanding capabilities.

• Among all inference acceleration baselines, although cache compression methods (StreamingLLM and SnapKV) achieve the highest cache reduction (over 90%), their end-to-end speedup is not as significant as prompt compression methods. This is because cache compression methods do not optimize the prefilling stage,

Table 1: Overall performance comparison between the baselines and EARN instantiated on LC-Rec. The best results are highlighted in bold and the second-best results are underlined.

<table><tr><td rowspan="2">Dataset</td><td rowspan="2">Model</td><td rowspan="2">Method</td><td colspan="2">Time Efficiency</td><td colspan="2">Space Efficiency</td><td colspan="4">Recommendation Effectiveness</td></tr><tr><td> $\omega$ </td><td> $\tau$ </td><td> $\gamma$ </td><td> $\sigma$ </td><td>R@10</td><td>R@20</td><td>N@10</td><td>N@20</td></tr><tr><td rowspan="18">Beauty</td><td rowspan="9">Llama</td><td>Finetune</td><td>1.00</td><td>505.2</td><td>0.0</td><td>85.45</td><td>0.0145</td><td>0.0225</td><td>0.0084</td><td>0.0108</td></tr><tr><td>SkipLayers</td><td>1.79</td><td>895.4</td><td>44.4</td><td>47.50</td><td>0.0013</td><td>0.0013</td><td>0.0013</td><td>0.0013</td></tr><tr><td>POD</td><td>1.15</td><td>585.0</td><td>14.7</td><td>72.87</td><td>0.0045</td><td>0.0074</td><td>0.0032</td><td>0.0041</td></tr><tr><td>500xCompressor</td><td>2.31</td><td>1168.6</td><td>74.8</td><td>21.55</td><td>0.0005</td><td>0.0006</td><td>0.0002</td><td>0.0003</td></tr><tr><td>StreamingLLM</td><td>1.22</td><td>611.2</td><td>96.4</td><td>3.09</td><td>0.0005</td><td>0.0005</td><td>0.0004</td><td>0.0004</td></tr><tr><td>SnapKV</td><td>1.20</td><td>600.7</td><td>94.5</td><td>4.73</td><td>0.0054</td><td>0.0061</td><td>0.0030</td><td>0.0032</td></tr><tr><td>Gist</td><td>1.18</td><td>597.6</td><td>17.5</td><td>70.50</td><td>0.0048</td><td>0.0077</td><td>0.0028</td><td>0.0036</td></tr><tr><td>AnLLM</td><td>1.24</td><td>625.1</td><td>92.2</td><td>6.70</td><td>0.0000</td><td>0.0000</td><td>0.0000</td><td>0.0000</td></tr><tr><td>EARN</td><td>3.79</td><td>1844.8</td><td>80.5</td><td>16.68</td><td>0.0167</td><td>0.0265</td><td>0.0095</td><td>0.0124</td></tr><tr><td rowspan="9">Qwen</td><td>Finetune</td><td>1.00</td><td>622.1</td><td>0.0</td><td>14.08</td><td>0.0145</td><td>0.0248</td><td>0.0087</td><td>0.0117</td></tr><tr><td>SkipLayers</td><td>1.73</td><td>1056.1</td><td>58.0</td><td>5.92</td><td>0.0000</td><td>0.0000</td><td>0.0000</td><td>0.0000</td></tr><tr><td>POD</td><td>1.09</td><td>679.3</td><td>8.4</td><td>12.90</td><td>0.0082</td><td>0.0127</td><td>0.0047</td><td>0.0061</td></tr><tr><td>500xCompressor</td><td>2.56</td><td>1587.1</td><td>91.1</td><td>1.26</td><td>0.0003</td><td>0.0003</td><td>0.0001</td><td>0.0001</td></tr><tr><td>StreamingLLM</td><td>1.05</td><td>652.6</td><td>92.0</td><td>1.12</td><td>0.0088</td><td>0.0147</td><td>0.0058</td><td>0.0075</td></tr><tr><td>SnapKV</td><td>1.02</td><td>634.5</td><td>69.5</td><td>4.29</td><td>0.0097</td><td>0.0165</td><td>0.0058</td><td>0.0077</td></tr><tr><td>Gist</td><td>1.15</td><td>715.4</td><td>20.0</td><td>11.30</td><td>0.0084</td><td>0.0161</td><td>0.0050</td><td>0.0074</td></tr><tr><td>AnLLM</td><td>1.06</td><td>659.3</td><td>80.5</td><td>2.70</td><td>0.0000</td><td>0.0000</td><td>0.0000</td><td>0.0000</td></tr><tr><td>EARN</td><td>2.71</td><td>1662.6</td><td>75.2</td><td>3.49</td><td>0.0155</td><td>0.0265</td><td>0.0091</td><td>0.0122</td></tr><tr><td rowspan="18">Games</td><td rowspan="9">Llama</td><td>Finetune</td><td>1.00</td><td>571.4</td><td>0.0</td><td>78.10</td><td>0.0167</td><td>0.0273</td><td>0.0106</td><td>0.0138</td></tr><tr><td>SkipLayers</td><td>1.85</td><td>1045.3</td><td>45.0</td><td>42.93</td><td>0.0002</td><td>0.0002</td><td>0.0003</td><td>0.0003</td></tr><tr><td>POD</td><td>1.09</td><td>623.3</td><td>15.9</td><td>65.69</td><td>0.0088</td><td>0.0147</td><td>0.0052</td><td>0.0070</td></tr><tr><td>500xCompressor</td><td>2.11</td><td>1205.3</td><td>72.5</td><td>21.45</td><td>0.0014</td><td>0.0021</td><td>0.0009</td><td>0.0011</td></tr><tr><td>StreamingLLM</td><td>1.23</td><td>702.5</td><td>96.0</td><td>3.13</td><td>0.0013</td><td>0.0013</td><td>0.0014</td><td>0.0014</td></tr><tr><td>SnapKV</td><td>1.22</td><td>688.5</td><td>93.5</td><td>5.04</td><td>0.0102</td><td>0.0110</td><td>0.0070</td><td>0.0072</td></tr><tr><td>Gist</td><td>1.12</td><td>639.9</td><td>18.0</td><td>64.00</td><td>0.0091</td><td>0.0146</td><td>0.0053</td><td>0.0070</td></tr><tr><td>AnLLM</td><td>1.25</td><td>715.5</td><td>91.6</td><td>6.60</td><td>0.0003</td><td>0.0003</td><td>0.0003</td><td>0.0003</td></tr><tr><td>EARN</td><td>3.53</td><td>1930.6</td><td>80.8</td><td>14.98</td><td>0.0180</td><td>0.0291</td><td>0.0107</td><td>0.0142</td></tr><tr><td rowspan="9">Qwen</td><td>Finetune</td><td>1.00</td><td>568.1</td><td>0.0</td><td>13.03</td><td>0.0193</td><td>0.0316</td><td>0.0127</td><td>0.0155</td></tr><tr><td>SkipLayers</td><td>1.52</td><td>858.4</td><td>57.3</td><td>5.57</td><td>0.0000</td><td>0.0000</td><td>0.0000</td><td>0.0000</td></tr><tr><td>POD</td><td>1.35</td><td>767.5</td><td>8.1</td><td>11.98</td><td>0.0129</td><td>0.0209</td><td>0.0075</td><td>0.0100</td></tr><tr><td>500xCompressor</td><td>2.60</td><td>1475.4</td><td>97.1</td><td>0.38</td><td>0.0013</td><td>0.0023</td><td>0.0008</td><td>0.0011</td></tr><tr><td>StreamingLLM</td><td>1.05</td><td>594.7</td><td>98.4</td><td>0.21</td><td>0.0129</td><td>0.0202</td><td>0.0075</td><td>0.0098</td></tr><tr><td>SnapKV</td><td>1.02</td><td>576.2</td><td>67.9</td><td>4.19</td><td>0.0138</td><td>0.0226</td><td>0.0083</td><td>0.0110</td></tr><tr><td>Gist</td><td>1.41</td><td>801.3</td><td>22.9</td><td>10.00</td><td>0.0121</td><td>0.0154</td><td>0.0077</td><td>0.0088</td></tr><tr><td>AnLLM</td><td>1.09</td><td>616.9</td><td>95.2</td><td>0.60</td><td>0.0003</td><td>0.0003</td><td>0.0003</td><td>0.0003</td></tr><tr><td>EARN</td><td>3.11</td><td>1711.3</td><td>75.1</td><td>3.24</td><td>0.0197</td><td>0.0312</td><td>0.0122</td><td>0.0157</td></tr><tr><td rowspan="18">MovieLens</td><td rowspan="9">Llama</td><td>Finetune</td><td>1.00</td><td>704.3</td><td>0.0</td><td>55.39</td><td>0.0247</td><td>0.0449</td><td>0.0197</td><td>0.0288</td></tr><tr><td>SkipLayers</td><td>2.52</td><td>1302.9</td><td>67.6</td><td>17.93</td><td>0.0022</td><td>0.0022</td><td>0.0043</td><td>0.0043</td></tr><tr><td>POD</td><td>1.17</td><td>827.4</td><td>18.0</td><td>45.40</td><td>0.0066</td><td>0.0118</td><td>0.0062</td><td>0.0087</td></tr><tr><td>500xCompressor</td><td>1.92</td><td>1352.8</td><td>61.1</td><td>21.54</td><td>0.0004</td><td>0.0005</td><td>0.0003</td><td>0.0003</td></tr><tr><td>StreamingLLM</td><td>1.20</td><td>836.2</td><td>95.2</td><td>2.66</td><td>0.0000</td><td>0.0000</td><td>0.0000</td><td>0.0000</td></tr><tr><td>SnapKV</td><td>1.19</td><td>829.2</td><td>91.9</td><td>4.50</td><td>0.0000</td><td>0.0000</td><td>0.0000</td><td>0.0000</td></tr><tr><td>Gist</td><td>1.01</td><td>711.3</td><td>22.3</td><td>43.10</td><td>0.0232</td><td>0.0421</td><td>0.0118</td><td>0.0250</td></tr><tr><td>AnLLM</td><td>1.20</td><td>846.9</td><td>89.5</td><td>5.80</td><td>0.0006</td><td>0.0008</td><td>0.0005</td><td>0.0006</td></tr><tr><td>EARN</td><td>3.21</td><td>2250.2</td><td>79.7</td><td>11.26</td><td>0.0259</td><td>0.0452</td><td>0.0247</td><td>0.0341</td></tr><tr><td rowspan="9">Qwen</td><td>Finetune</td><td>1.00</td><td>752.9</td><td>0.0</td><td>10.71</td><td>0.0289</td><td>0.0421</td><td>0.0247</td><td>0.0315</td></tr><tr><td>SkipLayers</td><td>1.87</td><td>1124.7</td><td>76.6</td><td>2.50</td><td>0.0000</td><td>0.0000</td><td>0.0000</td><td>0.0000</td></tr><tr><td>POD</td><td>1.41</td><td>1061.7</td><td>40.1</td><td>6.42</td><td>0.0139</td><td>0.0177</td><td>0.0115</td><td>0.0131</td></tr><tr><td>500xCompressor</td><td>2.09</td><td>1577.8</td><td>77.6</td><td>2.40</td><td>0.0006</td><td>0.0009</td><td>0.0006</td><td>0.0007</td></tr><tr><td>StreamingLLM</td><td>1.05</td><td>766.8</td><td>88.9</td><td>1.19</td><td>0.0258</td><td>0.0372</td><td>0.0197</td><td>0.0244</td></tr><tr><td>SnapKV</td><td>1.00</td><td>731.9</td><td>76.5</td><td>2.52</td><td>0.0248</td><td>0.0428</td><td>0.0192</td><td>0.0266</td></tr><tr><td>Gist</td><td>1.06</td><td>799.0</td><td>30.0</td><td>7.50</td><td>0.0287</td><td>0.0441</td><td>0.0244</td><td>0.0305</td></tr><tr><td>AnLLM</td><td>1.03</td><td>772.4</td><td>75.9</td><td>2.60</td><td>0.0022</td><td>0.0022</td><td>0.0043</td><td>0.0043</td></tr><tr><td>EARN</td><td>2.84</td><td>2136.7</td><td>66.7</td><td>3.56</td><td>0.0298</td><td>0.0591</td><td>0.0252</td><td>0.0382</td></tr></table>

whereas prompt compression methods (POD and 500xCompres sor) reduce the input sequence length in the prefilling stage, thereby improving both computational and memory eficiency. This highlights the greater potential for acceleration in the prefilling stage for LLMRec. However, despite the notable inference eficiency gains of the baselines, they sufer from catastrophic recommendation efectiveness degradation. This highlights that user historical interactions in recommendation scenarios cannot be simply compressed at a high ratio using NLP methods.

• Although gist methods (Gist and AnLLM) also employ the idea of register tokens, they fail to achieve a significant speedup. This is because they utilize all layers of the LLM to compress information, resulting in substantial computational costs. In contrast, EARN only uses the first <sup>??</sup> layers, significantly reducing the computational burden. In terms of space eficiency, Gist only compresses the task instruction within the input sequence, thus saving only about 20% of cache memory. Although AnLLM can reduce cache memory by 90%, it comes at the cost of catastrophic loss in recommendation efectiveness. AnLLM’s recommendation efectiveness is nearly zero. This is due to its attempt to compress the intricate user interaction history into a single token, which is highly challenging and leads to severe information loss and poor performance. Gist shows a decline in recommendation ef fectiveness. This is because Gist compresses the task instruction in isolation within the language space, while the items in recom mendations are not within the LLM’s language space. Without direct interaction between the task instruction and historical items, the LLM struggles to understand the recommendation task’s requirements to predict items outside its vocabulary. This impedes the method’s applicability to recommendation tasks.

![](images/cd69759baf4d35acc7a199278c54775235c612411f4d786805c45b59ca7d0687.jpg)

![](images/50ba3400d3140660ee2765062664391ce392d0cb7e19cc6db7f646e8691c2fc3.jpg)  
Figure 4: Eficiency under diferent batch sizes.

![](images/472cfef88e071c5f8f9a8454873359e9ee7750273a344fb8f5860b31005dd933.jpg)

![](images/f9a4bc547454384a561e7331dd529a033f4c752c833243f61a0c714f9c2a6622.jpg)  
Figure 5: Eficiency under diferent sequence lengths.

• EARN significantly achieves SOTA time eficiency (2.71-3.79x speedup) with excellent space eficiency (66.7-80.8% cache reduc tion), and also demonstrates a notable improvement over Finetune in terms of recommendation efectiveness. This suggests that the register tokens used in EARN can efectively summarize useful information, thereby ensuring that recommendation efec tiveness is maintained while inference eficiency is improved.

## 4.4 Hyper-parameter Analysis (RQ3)

To investigate the trade-of between inference eficiency and recommendation efectiveness caused by variations in hyper-parameters, we train and evaluate EARN with diferent register layer depth <sup>??</sup> and register token number <sup>??</sup>.

4.4.1 Efect of Register Layer Depth ??. Figure 6 reveals the trade-of between inference eficiency and recommendation efectiveness when varying the register layer depth <sup>??</sup>: 1) Too shallow: When the register layer depth is too shallow (e.g., <sup><</sup> 4 on Llama, and <sup><</sup> 7 on Qwen), although the speedup is high, the recall sufers a significant loss. 2) Optimal range: In the range of <sup>??</sup> = 4 − 7, EARN strikes a balance between speedup and recall. The speedup remains reasonably high, while Recall@20 improves notably. This suggests that the model can efectively capture the necessary information for recommendations without a substantial loss in inference eficiency. 3) Too deep: When the register layer depth is too deep $( e . g . , k \ge 1 3 )$ the speedup decreases significantly, but Recall@20 does not show a proportional improvement. For example, on Qwen, the speedup drops sharply when $k = 1 3 \mathrm { o r } k = 2 0$ , while Recall@20 does not in crease substantially. This indicates that increasing the register layer depth beyond a certain point leads to diminishing returns in terms of recommendation efectiveness while significantly compromising inference eficiency.

![](images/c6eec8727e37084067d47ebd46dba27c0da0e4faba8c4fc03e4fe3889c88d004.jpg)

![](images/52d40b88e2a647f443bb980e9a6dbdd50016a789d2696fa9f66f28e57c8bc276.jpg)

![](images/6a1f0fafafb965ee1bc0ac8e860df0b9f4781dde4e00e5922f67c260372e14f4.jpg)

![](images/dac314d2e0e1aad1c705f572a6c6ceeef4b18e3bc9a0c764825452c280585a42.jpg)  
Figure 7: Efect of register token number ??.

4.4.2 Efect of Register Token Number ??. Figure 7 reveals the trade-of between inference eficiency and recommendation efectiveness when varying the register token number <sup>??</sup>, from which we can observe that: 1) For both the prefix register and the sufix regis ter, as the register token number <sup>??</sup> varies from 1 to 3, the speedup gradually decreases. This is primarily because, as the register token number increases, the size of the KV Cache that needs to be com puted and cached also grows, leading to increased inference latency. 2) There is a decline in Recall@20 as the register token number <sup>??</sup> increases for both the prefix register and the sufix register. This phenomenon may be attributed to the interactions among multiple tokens in the later layers of the model, which can lead to a progressive distortion of the summarized information. The impact of this accuracy degradation is relatively minor for the prefix register but more pronounced for the sufix register. This discrepancy is likely due to the fact that user interaction history summarized by the sufix register is more complex and challenging to condense compared to task instructions summarized by the prefix register.

Although the above results show that a single register token is optimal, as prompt length increases, the optimal number of register tokens may need to be adjusted to maintain the performance. There fore, we conduct further experiments to investigate how EARN performs under diferent prompt lengths and whether the optimal number of register tokens should be adjusted as the prompt length increases. We segmented the dataset into three groups based on prompt length (50-100, 100-150, and 150-200 tokens) to evaluate our

![](images/e4dd93a97fa6dc41d5b8bf50d8956ccb872ca084c6aae1771fe0140474ae8346.jpg)  
Figure 8: Efect of register token number ?? under diferent prompt length.

EARN’s performance across diferent prompt lengths. As shown in Figure 8, EARN consistently outperforms the Finetune baseline, and a single register token remains optimal across all prompt lengths. However, we observed an interesting trend for the sufix register token: the performance gap between 1 and 2 register tokens narrows as prompt length increases. This suggests that the optimal number of register tokens may rise for very long prompts. Nevertheless, experimental results on three real-world datasets (Table 1) demonstrate that employing a single sufix register token could achieve excellent recommendation performance, which is applicable to the majority of recommendation scenarios.

4.4.3 Hyper-parameter Recommendation. We experimentally validated that EARN’s hyper-parameters can be selected through simple heuristics rather than exhaustive tuning. And we validated that setting the register layer and using a single register token at one-fourth achieves significant acceleration without accuracy loss on three real-world datasets. This configuration is broadly applicable for most recommendation tasks. Detailed analysis is as follows: 1) Register layer depth <sup>??</sup>: Firstly, the lower the register layer <sup>??</sup>, the greater the acceleration efect achieved. Secondly, our sensitivity analysis indicates that there is essentially no loss in recommendation efectiveness when <sup>??</sup> is set to at least one-fourth of the total layers. 2) Register token number <sup>??</sup>: Across two distinct LLM models (Llama and Qwen), we consistently found that one register token is optimal. Additionally, to assess if the number needs adjustment as prompt length increases, we conducted grouped experiments by length, and found that a single register token remains optimal under diferent prompt lengths. Thus, for most LLMRec scenarios, we propose a default configuration:

(1) ??: One-fourth of the total layers as the register layer depth.

(2) ??: One prefix register token and one sufix register token.

This setting could achieve a favorable speedup and KV Cache reduction while maintaining strong recommendation performance. And it’s easily adjustable for various deployment scenarios.

[已省略: 5 related work]

## 6 Conclusion

In this work, we address the critical challenge of inference eficiency in LLM-based recommendation systems (LLMRec), where the massive computational overhead and memory pressure of KV Cache severely hinders practical deployment. Through systematic analysis of LLMRec’s attention patterns, we identify two pivotal characteristics: 1) layer-wise attention sparsity inversion, where in early layers retain dense informative patterns while later layers exhibit high redundancy, and 2) the dual attention sinks phenomenon, where attention scores concentrate on both head and tail tokens of input sequences. These insights motivate our proposed EARN method, which introduces prefix and sufix register tokens to compress task instructions and user interaction histories, implementing layer-wise computation pruning. EARN achieves an 80% reduction of KV Cache while maintaining essential information integrity. Extensive experiments conducted on three benchmark datasets and two distinct LLM architectures reveal that our EARN attains 3.79x inference acceleration with superior accuracy compared to conventional finetuning approaches. This breakthrough efectively reconciles the longstanding trade-of between inference eficiency and recommendation quality in LLMRec, presenting tangible deployment benefits for industrial-scale recommendation services.

[已省略: references]

## A.1 Detailed Analysis of Attention Score Distributions

In this section, we provide a systematic analysis of attention score distributions in LLMRec through quantitative measurements across two critical dimensions: layer order and token position. To ensure comprehensive insights, we conduct experiments across 13 NLP tasks and three real-world recommendation datasets, two main stream LLMRec methods, and two distinct LLM architectures. Ta ble 4 presents the overall results. More detailed quantitative results and visual figures can be found in our GitHub repository<sup>2</sup>. Our findings reveal fundamental diferences in attention patterns be tween NLP tasks and LLMRec tasks, ofering critical guidance for designing eficient compression strategies.

Quantitative Measurements of Attention Score Distribu tions. Given a sequence’s attention scores $\left[ { p _ { 1 } , p _ { 2 } , \cdots , p _ { n } } \right]$ , we test its sparsity by threshold-based sparsity ratio adapted from prior studies [1, 5]:

$$
S p a r s i t y = \frac {1}{n} \sum_ {i = 1} ^ {n} \mathbb {I} (p _ {i} > \epsilon),\tag{14}
$$

where <sup>??</sup> is the threshold. Here we set $\epsilon = 0 . 0 5 ,$ , according to the distribution characteristics of attention scores.

We test its sink by position-based total attention scores:

$$
S i n k _ {h e a d} = \sum_ {i = 1} ^ {T _ {h}} p _ {i}, S i n k _ {t a i l} = \sum_ {i = T _ {t}} ^ {n} p _ {i},\tag{15}
$$

where $T _ { h }$ and $T _ { t }$ is the position of the head and tail respectively. Here we set $T _ { h } = 3 , T _ { t } = n { - } 3$ , according to the distribution characteristics of attention scores.

Attention Diferences across Layer Orders. As measured in Table 4, we identify a layer-wise atention sparsity inversion between NLP tasks and LLMRec tasks. In NLP tasks, the atten tion sparsity is high in early layers, but decreases in later layers $( S p _ { e a r l y } > S p _ { l a t t e r } )$ . Conversely, LLMRec tasks display an inverted pattern: the attention sparsity is relatively low in early layers, but increases in later layers $( S p _ { e a r l y } < S p _ { l a t t e r } )$ . This indicates that the less sparse early layers in LLMRec retain more user preference in formation, while high sparsity in later layers suggests redundancy.

Attention Diferences across Token Positions. Table 4 re veals a dual atention sinks phenomenon that distinguishes LLMRec from NLP tasks. There is significant $S i n k _ { h e a d }$ for both tasks, while LLMRec exhibits a larger $S i n k _ { t a i l } \ : ( S i n k _ { t a i l } \mathrm { ( L L M R e c ) } >$ $S i n k _ { t a i l } ( \mathrm { N L P } ) )$ . This indicates that both head and tail tokens in LLMRec are crucial for recommendation performance.

Implications for Compression Strategy. These findings indi cate that in LLMRec, the early layers contain richer information, while the middle tokens in the later layers are redundant. Our ap proach takes into account the unique attention score distributions in LLMRec and formulates a reasonable compression scheme from a global perspective. It focuses on preserving information from critical token positions and early layers while pruning redundant parts in later layers. This ensures that it can improve eficiency while maintaining accuracy.

Table 4: Measurements of attention sink and sparsity (averaged across 13 NLP tasks, 3 real-world recommendation datasets, 2 LLMRec backbones, and 2 LLM models). Here, $\boldsymbol { s p _ { e a r l y } }$ denotes $S p a r s i t y _ { e a r l y \ l a y e r s } ,$ and $\boldsymbol { S p } _ { l a t t e r }$ denotes ???????? ?? ??????<sub>??????</sub> <sub>??????</sub> <sub>????????????</sub> .

<table><tr><td>Model</td><td>Task</td><td> $Sp_{early}$ </td><td> $Sp_{latter}$ </td><td> $Sink_{head}$ </td><td> $Sink_{tail}$ </td></tr><tr><td rowspan="2">Llama</td><td>NLP</td><td>0.064</td><td>0.026</td><td>0.73</td><td>0.07</td></tr><tr><td>LLMRec</td><td>0.025</td><td>0.048</td><td>0.56</td><td>0.09</td></tr><tr><td rowspan="2">Qwen</td><td>NLP</td><td>0.074</td><td>0.046</td><td>0.30</td><td>0.15</td></tr><tr><td>LLMRec</td><td>0.047</td><td>0.059</td><td>0.30</td><td>0.24</td></tr></table>

## A.3 Experimential Details

Datasets Details. For all three datasets, all historical interactions are sorted according to the global timestamps, and then split into training, validation, and testing sets with the ratio of 8:1:1. For the item identifier, we follow LC-Rec [43] and TIGER [31] to set the length $L = 4 ,$ i.e., the token sequence length of a generated item would be 4.

Implementation details. All training and inference experiments are conducted on a single NVIDIA H100 80GB GPU. For the training setup, we employ full finetuning with AdamW optimizer and an overall batch size of 128 by leveraging gradient accumulation. The learning rate is set to 0<sup>.</sup>001, and is adjusted dynamically by a cosine learning rate scheduler with a warmup ratio of 0<sup>.</sup>02. For the inference setup, we set the beam size to 20 and use the maximum batch size that the GPU could accommodate. For the hyper-parameters of EARN in Table 1, EARN on Llama uses $k = 4$ and <sup>??</sup> = 1, and EARN on Qwen uses <sup>??</sup> = 7 and <sup>??</sup> = 1.

Table 5: Overall performance comparison between the baselines and EARN instantiated on TIGER.

<table><tr><td rowspan="2">Method</td><td colspan="2">Time Efficiency</td><td colspan="2">Space Efficiency</td><td colspan="4">Recommendation Effectiveness</td></tr><tr><td> $\omega$ </td><td> $\tau$ </td><td> $\gamma$ </td><td> $\sigma$ </td><td>R@10</td><td>R@20</td><td>N@10</td><td>N@20</td></tr><tr><td colspan="9">Beauty, Llama</td></tr><tr><td>Finetune</td><td>1.00</td><td>602.50</td><td>0.0</td><td>68.18</td><td>0.0108</td><td>0.0198</td><td>0.0071</td><td>0.0096</td></tr><tr><td>SkipLayers</td><td>1.78</td><td>1069.7</td><td>44.5</td><td>37.87</td><td>0.0010</td><td>0.0010</td><td>0.0011</td><td>0.0011</td></tr><tr><td>POD</td><td>1.17</td><td>701.7</td><td>14.8</td><td>58.11</td><td>0.0033</td><td>0.0065</td><td>0.0027</td><td>0.0039</td></tr><tr><td>500xCompressor</td><td>2.31</td><td>1389.1</td><td>74.8</td><td>17.16</td><td>0.0003</td><td>0.0003</td><td>0.0001</td><td>0.0001</td></tr><tr><td>StreamingLLM</td><td>1.21</td><td>730.0</td><td>96.4</td><td>2.44</td><td>0.0003</td><td>0.0005</td><td>0.0005</td><td>0.0003</td></tr><tr><td>SnapKV</td><td>1.19</td><td>718.1</td><td>94.5</td><td>3.76</td><td>0.0041</td><td>0.0053</td><td>0.0027</td><td>0.0031</td></tr><tr><td>EARN</td><td>3.44</td><td>1972.4</td><td>80.9</td><td>13.04</td><td>0.0115</td><td>0.0199</td><td>0.0075</td><td>0.0098</td></tr><tr><td colspan="9">Beauty, Qwen</td></tr><tr><td>Finetune</td><td>1.00</td><td>714.3</td><td>0.0</td><td>12.72</td><td>0.0095</td><td>0.0162</td><td>0.0061</td><td>0.0081</td></tr><tr><td>SkipLayers</td><td>1.69</td><td>1208.1</td><td>57.9</td><td>5.35</td><td>0.0000</td><td>0.0000</td><td>0.0000</td><td>0.0000</td></tr><tr><td>POD</td><td>1.10</td><td>784.4</td><td>8.4</td><td>11.65</td><td>0.0056</td><td>0.0084</td><td>0.0032</td><td>0.0044</td></tr><tr><td>500xCompressor</td><td>2.55</td><td>1819.2</td><td>91.4</td><td>1.09</td><td>0.0003</td><td>0.0005</td><td>0.0002</td><td>0.0005</td></tr><tr><td>StreamingLLM</td><td>1.05</td><td>751.6</td><td>91.7</td><td>1.06</td><td>0.0057</td><td>0.0096</td><td>0.0040</td><td>0.0052</td></tr><tr><td>SnapKV</td><td>1.02</td><td>728.7</td><td>69.6</td><td>3.87</td><td>0.0063</td><td>0.0110</td><td>0.0043</td><td>0.0055</td></tr><tr><td>EARN</td><td>2.58</td><td>1805.9</td><td>75.5</td><td>3.11</td><td>0.0104</td><td>0.0164</td><td>0.0065</td><td>0.0089</td></tr><tr><td colspan="9">Games, Llama</td></tr><tr><td>Finetune</td><td>1.00</td><td>695.8</td><td>0.0</td><td>61.40</td><td>0.0126</td><td>0.0216</td><td>0.0080</td><td>0.0107</td></tr><tr><td>SkipLayers</td><td>1.83</td><td>1272.4</td><td>45.0</td><td>33.76</td><td>0.0001</td><td>0.0001</td><td>0.0003</td><td>0.0003</td></tr><tr><td>POD</td><td>1.08</td><td>757.8</td><td>15.8</td><td>51.67</td><td>0.0054</td><td>0.0098</td><td>0.0032</td><td>0.0045</td></tr><tr><td>500xCompressor</td><td>2.11</td><td>1470.2</td><td>72.5</td><td>16.88</td><td>0.0010</td><td>0.0015</td><td>0.0007</td><td>0.0008</td></tr><tr><td>StreamingLLM</td><td>1.22</td><td>850.7</td><td>96.0</td><td>2.46</td><td>0.0010</td><td>0.0010</td><td>0.0010</td><td>0.0009</td></tr><tr><td>SnapKV</td><td>1.21</td><td>837.6</td><td>93.5</td><td>3.98</td><td>0.0064</td><td>0.0075</td><td>0.0045</td><td>0.0045</td></tr><tr><td>EARN</td><td>3.12</td><td>2062.7</td><td>81.2</td><td>11.56</td><td>0.0138</td><td>0.0212</td><td>0.0085</td><td>0.0108</td></tr><tr><td colspan="9">Games, Qwen</td></tr><tr><td>Finetune</td><td>1.00</td><td>673.2</td><td>0.0</td><td>10.81</td><td>0.0131</td><td>0.0224</td><td>0.0085</td><td>0.0113</td></tr><tr><td>SkipLayers</td><td>1.51</td><td>1014.3</td><td>57.0</td><td>4.65</td><td>0.0000</td><td>0.0000</td><td>0.0000</td><td>0.0000</td></tr><tr><td>POD</td><td>1.36</td><td>912.1</td><td>8.5</td><td>9.88</td><td>0.0087</td><td>0.0150</td><td>0.0050</td><td>0.0073</td></tr><tr><td>500xCompressor</td><td>2.60</td><td>1752.0</td><td>96.7</td><td>0.35</td><td>0.0002</td><td>0.0004</td><td>0.0001</td><td>0.0001</td></tr><tr><td>StreamingLLM</td><td>1.06</td><td>708.8</td><td>98.4</td><td>0.17</td><td>0.0088</td><td>0.0145</td><td>0.0050</td><td>0.0072</td></tr><tr><td>SnapKV</td><td>1.02</td><td>686.4</td><td>67.6</td><td>3.50</td><td>0.0094</td><td>0.0161</td><td>0.0056</td><td>0.0081</td></tr><tr><td>EARN</td><td>2.86</td><td>1841.3</td><td>72.1</td><td>3.02</td><td>0.0137</td><td>0.0231</td><td>0.0086</td><td>0.0119</td></tr><tr><td colspan="9">MovieLens, Llama</td></tr><tr><td>Finetune</td><td>1.00</td><td>852.50</td><td>0.0</td><td>39.79</td><td>0.0245</td><td>0.0446</td><td>0.0244</td><td>0.0323</td></tr><tr><td>SkipLayers</td><td>1.85</td><td>1577.0</td><td>67.6</td><td>12.89</td><td>0.0022</td><td>0.0024</td><td>0.0059</td><td>0.0051</td></tr><tr><td>POD</td><td>1.18</td><td>1003.9</td><td>18.1</td><td>32.57</td><td>0.0068</td><td>0.0122</td><td>0.0088</td><td>0.0103</td></tr><tr><td>500xCompressor</td><td>1.93</td><td>1640.0</td><td>61.1</td><td>15.48</td><td>0.0004</td><td>0.0006</td><td>0.0004</td><td>0.0003</td></tr><tr><td>StreamingLLM</td><td>1.18</td><td>1007.9</td><td>95.2</td><td>1.89</td><td>0.0000</td><td>0.0000</td><td>0.0000</td><td>0.0000</td></tr><tr><td>SnapKV</td><td>1.18</td><td>1002.50</td><td>91.8</td><td>3.28</td><td>0.0000</td><td>0.0000</td><td>0.0000</td><td>0.0000</td></tr><tr><td>EARN</td><td>2.85</td><td>2437.4</td><td>77.7</td><td>8.87</td><td>0.0269</td><td>0.0544</td><td>0.0221</td><td>0.0340</td></tr><tr><td colspan="9">MovieLens, Qwen</td></tr><tr><td>Finetune</td><td>1.00</td><td>897.4</td><td>0.0</td><td>7.75</td><td>0.0238</td><td>0.0455</td><td>0.0224</td><td>0.0312</td></tr><tr><td>SkipLayers</td><td>1.49</td><td>1340.5</td><td>76.9</td><td>1.79</td><td>0.0002</td><td>0.0002</td><td>0.0002</td><td>0.0002</td></tr><tr><td>POD</td><td>1.41</td><td>1260.9</td><td>39.8</td><td>4.66</td><td>0.0114</td><td>0.0192</td><td>0.0106</td><td>0.0131</td></tr><tr><td>500xCompressor</td><td>2.10</td><td>1882.1</td><td>77.9</td><td>1.71</td><td>0.0004</td><td>0.0009</td><td>0.0005</td><td>0.0007</td></tr><tr><td>StreamingLLM</td><td>1.01</td><td>912.2</td><td>88.3</td><td>0.91</td><td>0.0213</td><td>0.0402</td><td>0.0180</td><td>0.0241</td></tr><tr><td>SnapKV</td><td>0.97</td><td>872.4</td><td>76.5</td><td>1.82</td><td>0.0204</td><td>0.0464</td><td>0.0174</td><td>0.0263</td></tr><tr><td>EARN</td><td>2.56</td><td>2292.8</td><td>45.5</td><td>4.23</td><td>0.0274</td><td>0.0474</td><td>0.0273</td><td>0.0355</td></tr></table>

Table 6: Overall comparison between baselines and EARN instantiated on HSTU. Here, the unit of ?? is MB.

<table><tr><td rowspan="2">Method</td><td colspan="2">Time Efficiency</td><td colspan="2">Space Efficiency</td><td colspan="4">Recommendation Effectiveness</td></tr><tr><td>ω</td><td>τ</td><td>γ</td><td>σ</td><td>R@10</td><td>R@20</td><td>N@10</td><td>N@20</td></tr><tr><td colspan="9">Beauty</td></tr><tr><td>Finetune</td><td>1.00</td><td>2735.5</td><td>0.0</td><td>439.5</td><td>0.0446</td><td>0.0693</td><td>0.0269</td><td>0.0328</td></tr><tr><td>SkipLayers</td><td>1.72</td><td>4685.6</td><td>27.8</td><td>317.5</td><td>0.0248</td><td>0.0322</td><td>0.0116</td><td>0.0136</td></tr><tr><td>EARN</td><td>2.01</td><td>5414.9</td><td>49.5</td><td>222.0</td><td>0.0520</td><td>0.0594</td><td>0.0311</td><td>0.0329</td></tr><tr><td colspan="9">Games</td></tr><tr><td>Finetune</td><td>1.00</td><td>3425.2</td><td>0.0</td><td>532.9</td><td>0.0557</td><td>0.0846</td><td>0.0362</td><td>0.0435</td></tr><tr><td>SkipLayers</td><td>1.69</td><td>5797.2</td><td>27.9</td><td>384.4</td><td>0.0371</td><td>0.0520</td><td>0.0200</td><td>0.0237</td></tr><tr><td>EARN</td><td>1.97</td><td>6770.9</td><td>50.3</td><td>264.9</td><td>0.0586</td><td>0.0735</td><td>0.0384</td><td>0.0421</td></tr><tr><td colspan="9">MovieLens</td></tr><tr><td>Finetune</td><td>1.00</td><td>3187.9</td><td>0.0</td><td>546.9</td><td>0.0756</td><td>0.1073</td><td>0.0405</td><td>0.0485</td></tr><tr><td>SkipLayers</td><td>1.75</td><td>5602.4</td><td>34.6</td><td>357.7</td><td>0.0780</td><td>0.1207</td><td>0.0429</td><td>0.0536</td></tr><tr><td>EARN</td><td>2.06</td><td>6555.8</td><td>50.5</td><td>270.6</td><td>0.0793</td><td>0.1268</td><td>0.0429</td><td>0.0551</td></tr></table>

Table 7: Overall performance comparison between Finetune and EARN with diferent register layer <sup>??</sup> on Llama (total 32 layers) on MMLU.

<table><tr><td>RegisterLayer k</td><td> $\omega$ </td><td> $\tau$ </td><td> $\gamma$ </td><td> $\sigma$ </td><td>Accuracy</td></tr><tr><td>Finetune</td><td>1.0</td><td>76.0</td><td>0.0</td><td>266.0</td><td>0.51</td></tr><tr><td>4</td><td>6.9</td><td>523.6</td><td>83.3</td><td>44.5</td><td>0.27</td></tr><tr><td>7</td><td>4.3</td><td>331.3</td><td>73.3</td><td>71.0</td><td>0.28</td></tr><tr><td>11</td><td>2.9</td><td>219.0</td><td>61.3</td><td>103.0</td><td>0.28</td></tr><tr><td>15</td><td>2.2</td><td>163.4</td><td>49.3</td><td>135.0</td><td>0.46</td></tr><tr><td>19</td><td>1.7</td><td>130.3</td><td>38.2</td><td>164.5</td><td>0.50</td></tr><tr><td>23</td><td>1.4</td><td>104.3</td><td>26.1</td><td>196.5</td><td>0.50</td></tr><tr><td>27</td><td>1.2</td><td>91.6</td><td>14.2</td><td>228.3</td><td>0.50</td></tr></table>

## A.4 Additional Results on TIGER

Table 5 shows the overall performance comparison between the baselines and EARN instantiated on TIGER. Our EARN achieves the best performance in terms of time eficiency and recommendation efectiveness, while also demonstrating excellent space eficiency. These results further validate the efectiveness of EARN.

## A.5 Additional Results on HSTU

We also conduct experiments on HSTU [41], the first industrydeployed generative recommendation system. As shown in Table 6, our EARN is also efective for HSTU, demonstrating excellent time and space eficiency (2x speedup and 50% memory savings), with minimal impact on recommendation efectiveness. It is important to note that HSTU difers from other popular LLM-based generative recommendation methods (e.g., LC-Rec). Specifically, in HSTU model, there are no textual inputs and no concept of prompts as seen in NLP tasks. And HSTU directly generates the predicted item embeddings, akin to generating only one token, which means it only has the prefilling stage and no decoding stage. These render that the baselines of prompt compression, cache compression, and gist methods in NLP are not applicable. Therefore, we primarily compared Finetune, SkipLayer, and EARN.

## A.6 Additional Results on NLP Tasks

To validate the generalizability of EARN beyond recommendation tasks, we conducted experiments on MMLU dataset [8]—a general NLP dataset spanning 57 tasks (e.g., math, science, and humanities).

Results in Table 7 demonstrate EARN’s efectiveness: 1) Eficiencyaccuracy trade-of: As the register layer <sup>??</sup> decreases, EARN achieves higher speedup and cache reduction at the cost of reduced accuracy. However, when $k \geq 1 5 ,$ the accuracy loss remains within 10%, indicating that EARN can still deliver satisfactory performance for general NLP tasks. 2) Comparison with LLMRec tasks: Unlike LLM-Rec tasks, where EARN incurs no accuracy loss at <sup>??</sup> ≥ 4 and even boosts accuracy by pruning noisy information (refer to Figure 6), NLP tasks require a higher <sup>??</sup> to curb accuracy degradation.

In summary, while optimal <sup>??</sup> varies across tasks, it consistently enables eficient inference with controlled accuracy trade-ofs, showcasing its broader applicability beyond recommendation tasks.


---

---

## 📊 文档统计

| 指标 | 值 |
|------|-----|
| 收录论文数 | 25 |
| 截断论文数 | 0 |
| 实际 Token 数 | 131.7k |
| 目标 Token 数 | 175.0k |
| 达成率 | 75.3% |
| 合并策略 | key-sections |
| 生成时间 | 2026-07-24T12:32:17.421930 |

---

> 本文档由 `DocumentMerger` 自动生成，用于 Coding Agent 上下文窗口压力测试。

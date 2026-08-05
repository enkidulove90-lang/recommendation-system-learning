# Learning to Reason by Analogy via Retrieval-Augmented Reinforcement Fine-Tuning

Zilin Xiao<sup>1,2,∗</sup>, Qi Ma<sup>1</sup>, Jason Chen<sup>1</sup>, Xintao Chen<sup>1</sup>, Avinash Atreya<sup>1</sup>, Hanjie Chen<sup>2</sup>, Vicente Ordonez<sup>2</sup>

<sup>1</sup>Meta Superintelligence Labs, <sup>2</sup>Rice University

<sup>∗</sup>Work partially done during internship at Meta

Retrieval-augmented generation (RAG) has become a standard mechanism for grounding language models in external knowledge, yet conventional retrieval based on lexical or semantic similarity is poorly suited for complex reasoning tasks: a semantically similar problem may demand an entirely diferent solution strategy, while a superficially diferent problem may share the same underlying reasoning pattern. We propose Retrieval-Augmented Reinforcement Fine-Tuning (RA-RFT), a posttraining framework that teaches language models to reason by analogy. RA-RFT uses gold-relevance distillation to train a retriever that ranks contexts by expected reasoning benefit rather than semantic overlap, and then fine-tunes the policy model via reinforcement fine-tuning methods with retrieved analogous demonstrations, so the model learns to leverage reasoning traces under verifiable outcome rewards. We further analyze the diversity of retrieved contexts and find that reasoning-aware retrieval surfaces complementary solution strategies that provide distinct reasoning scafolds for individual problems. Across challenging mathematical reasoning benchmarks, RA-RFT consistently outperforms standard reinforcement fine-tuning methods. For example, it improves AIME 2025 average@32 accuracy by 7.1 and 2.8 points over GRPO for Qwen3-1.7B and Qwen3-4B respectively—suggesting that reasoning-aware retrieval is a complementary axis of improvement and orthogonal to advances in reward design or training curricula.

Date: June 12, 2026

Correspondence: Zilin Xiao at zilin@meta.com

RICE ∞Meta

## 1 Introduction

Reinforcement learning from verifiable rewards (RLVR) has emerged as a powerful post-training paradigm for complex reasoning (DeepSeek-AI, 2025; OpenAI, 2024). By optimizing for outcome correctness rather than imitating reference solutions, RLVR elicits sophisticated chain-of-thought reasoning that generalizes across diverse problem types (Shao et al., 2024). However, these approaches rely entirely on the parametric knowledge of a model: when confronted with novel problems whose solutions require reasoning patterns not well-represented in pre-training, the model has no mechanism to draw on external problem-solving expertise.

Retrieval-augmented generation (RAG) ofers a natural complement, grounding model outputs in externally retrieved content (Lewis et al., 2020; Guu et al., 2020). Yet standard retrieval is poorly suited for reasoning tasks: conventional retrievers rank candidates by lexical or semantic similarity, which correlates weakly with reasoning utility, understood as whether the retrieved content actually helps solve the target problem (Su et al., 2025). A semantically similar problem may demand an entirely diferent solution strategy, while a superficially diferent problem may share the same underlying reasoning pattern. As a result, naively augmenting reasoning models with retrieved content often yields marginal or inconsistent gains (Arabzadeh et al., 2025).

We approach this problem through the lens of analogical reasoning (Gentner, 1983): expert problem-solvers recall previously solved problems not because surface details match, but because the underlying reasoning structure transfers. This motivates a retrieval paradigm that selects examples whose reasoning traces, i.e. step-by-step solution strategies are maximally informative for the target problem. Building on this insight, we propose Retrieval-Augmented Reinforcement Fine-Tuning (RA-RFT), a post-training framework consisting of three stages: (1) gold-relevance distillation, which constructs retrieval supervision grounded in reasoning utility by using a judge model to directly assess whether candidate reasoning traces share transferable reasoning patterns with the target problem; (2) reasoning-aware retriever training, which uses contrastive learning on these utility-based annotations to train a dense retriever that surfaces structurally analogous problems, and (3) reinforcement fine-tuning with retrieved demonstrations, which injects retrieved reasoning traces into training prompts and optimizes the target model via RLVR. We further analyze the diversity of retrieved contexts and the quality of the reasoning-aware retriever and find that reasoning-aware retrieval produces structurally varied traces that surface distinct solution strategies for individual problems, suggesting that retrieval quality is a key factor for efective context augmentation.

![](images/dc9b3dfc78ceb703c5fcfec35b4fb6eb0be206e312e8932bb778e7c533ad321e.jpg)  
Figure 1 Motivation of RA-RFT. Left: A training query may be retrieved with a surface-similar but reasoning-irrelevant exemplar $( \mathbf { E } _ { 1 } ,$ , which could be easily solved by direct substitution) or a superficially diferent but reasoning-analogous exemplar (E<sub>2</sub>, which shares the same binomial identity strategy). Right: The quality of retrieved context is critical for RLVR training. Conditioning on the unhelpful exemplar E<sub>1</sub> misleads the model, degrades rollout quality, and produces noisy reward signals that hurt policy learning. In contrast, conditioning on the reasoning-analogous exemplar E provides transferable solution strategies that improve rollout quality and yield informative rewards, leading to efective policy improvement. See case studies in Section C.

We evaluate RA-RFT on competition-level mathematical reasoning benchmarks, including AIME 2024 and 2025 (MAA, 2024), HMMT February 2025 (HMMT, 2025), and BrUMO 2025 (BrUMO, 2025). Across Qwen3-1.7B and Qwen3-4B, RA-RFT consistently outperforms both standalone RLVR and strong baselines: it improves AIME 2025 average@32 accuracy by 7.1 and 2.8 points over GRPO, and achieves 4.1 and 2.6 points of overall average gain across all four benchmarks. These results confirm that grounding retrieval in reasoning utility, rather than surface-level similarity, is critical for unlocking the full potential of retrieval-augmented reinforcement fine-tuning.

## 2 Related Work

Reinforcement Learning for Reasoning. Reinforcement learning from verifiable rewards (RLVR) has emerged as a leading paradigm for eliciting reasoning in large language models (DeepSeek-AI, 2025; OpenAI, 2024). Group Relative Policy Optimization (GRPO) (Shao et al., 2024) replaces the value-network critic with group-normalized advantages, and a family of follow-up variants (Liu et al., 2025; Yu et al., 2025; MiniMax, 2025; Qi et al., 2026) addresses optimization bias, large-scale stability, importance sampling, and ratio clipping. A complementary line shapes the training signal through context engineering rather than the optimizer: injecting partial solutions into hard problems (Li et al., 2026), stepwise hints from teacher models (Zhang et al., 2025a), or expert demonstrations in lieu of verifiers (Cai and Provilkov, 2025). RA-RFT is orthogonal to both directions: rather than modifying the reward, the optimizer, or the training curriculum, it augments RLVR rollouts with externally retrieved reasoning traces, providing a knowledge source that the policy must learn to use under outcome reward.

Retrieval-Augmented Generation for Reasoning. While retrieval-augmented generation is efective for knowledgeintensive tasks (Lewis et al., 2020; Guu et al., 2020; Ram et al., 2023), its application to reasoning is more delicate: retrieval helps only under bounded conditions and noisy retrievals actively hurt (Liu et al., 2024), and standard retrievers underperform on reasoning-intensive queries where surface similarity diverges from reasoning utility (Su et al., 2025). Recent work tackles this with corpus restructuring into step-by-step traces (Arabzadeh et al., 2025), rubric-based retriever fine-tuning distilled from an LLM judge (Lan et al., 2025), or interleaved retrieval-and-reasoning trained by RL (Li et al., 2025). All of these target inference-time RAG and either leave the policy frozen or train the policy to issue retrieval queries. RA-RFT instead introduces reasoning relevance as the retrieval objective, distilled from a GPT-4o judge over ofline query-context pairs, and integrates the resulting retriever directly into reinforcement fine-tuning so the policy is shaped by retrieved analogies during exploration rather than only at test time.

![](images/88c044f8bb8d4acf949a2e8b05e8eafbb53c2d8cc7ff28cf38b9baa6eaaf3eac.jpg)  
Figure 2 Overview of the RA-RFT framework. A judge model evaluates query-corpus pairs to produce binary reasoning-relevance labels. Then we train a dense retriever via contrastive learning using the distilled relevance labels. The trained retriever provides reasoning-analogous traces which augment the reinforcement fine-tuning process.

Learning from Demonstrations and Analogies. Our work draws on analogical reasoning (Gentner, 1983; Holyoak and Thagard, 1996) and the in-context learning paradigm (Brown et al., 2020; Liu et al., 2022; Rubin et al., 2022), where models adapt to new tasks by conditioning on demonstrations rather than parameter updates. Several recent works retrieve or construct demonstrations tailored to specific reasoning tasks at inference time, including computational-graph-matched exemplars for math word problems (Yang et al., 2024), trajectory-as-exemplar prompting (Zheng et al., 2024), adaptive test-time memory (Suzgun et al., 2026), large-scale subquestion–subroutine procedural memories retrieved mid-trajectory (Wu et al., 2026), and compact procedural “behaviors” mined from a model’s own past traces and reinjected in-context or via SFT (Didolkar et al., 2025). A complementary line internalizes such in-context signal into parameters via on-policy distillation against a privileged-context teacher (Ye et al., 2026; Zhao et al., 2026), but cannot supply reasoning patterns the teacher itself does not already know. In the broader RL setting, Goyal et al. (2022) augment embodied agents with neural retrieval over past trajectories, conditioning the policy on historica experience beyond the current state. RA-RFT difers from all of these by closing the loop for verifiable-reward reasoning: retrieved analogous demonstrations are folded into the RL fine-tuning loop, so the policy learns under outcome rewards to exploit retrieved analogies rather than to imitate them at test time, and the retriever itself is trained against reasoning-utility supervision rather than surface similarity.

## 3 Methodology

Our framework consists of three stages: (1) gold-relevance distillation to construct reasoning-utility-based retrieval supervision, (2) reasoning-aware retriever training via contrastive learning, and (3) reinforcement fine-tuning with retrieved demonstrations. Figure 2 illustrates the overall pipeline.

## 3.1 Overall Setup

We consider a training set of reasoning problems $\mathcal { D } = \{ ( q _ { i } , a _ { i } ) \} _ { i = 1 } ^ { N }$ with verifiable answers. Given a language model $\mathcal { M } _ { \phi } ,$ the goal is to train $\mathcal { M } _ { \phi }$ to solve problems in D (and generalize beyond) by optimizing for outcome correctness via reinforcement learning. Standard RLVR approaches sample a group of responses $\{ \hat { a } _ { 1 } , \dots , \hat { a } _ { G } \} \sim \mathcal { M } _ { \phi } ( \cdot \mid q )$ for each problem $q ,$ compute rewards $r ( \hat { a } _ { g } , a )$ based on answer correctness, and update the policy using normalized advantages. However, RLVR is bottlenecked by the model’s parametric knowledge. When a problem demands a reasoning strategy that the model has not internalized during pre-training, for instance, a number-theoretic argument that hinges on a combinatorial identity, no amount of sampling will reliably discover it, leading to sparse rewards and stalled learning. Existing works either inject dense supervision from the reference solution to the same problem (Zhao et al., 2026), which requires the model to already be capable enough to rationalize the trace, or reshape the training curriculum (Li et al., 2026; Zhang et al., 2025a), which still cannot supply reasoning patterns absent from the model’s parameters. What is missing is a mechanism akin to human analogical reasoning: the ability to recall a structurally related solved problem whose solution strategy transfers, even when the two problems difer on the surface.

To address these limitations, we augment the reasoning process with an external corpus $\mathcal { C } = \{ ( p _ { j } , t _ { j } ) \} _ { i = 1 } ^ { M }$ of problems paired with reasoning traces, where each trace $t _ { j }$ is a step-by-step solution generated by a teacher model. The central question is: which corpus entries, when provided as context, will most improve the model’s ability to reason about a given problem? Standard retrieval ranks candidates by embedding similarity $c ^ { * } = \arg \operatorname* { m a x } _ { c \in { \mathcal { C } } } \langle \mathbf { e } _ { q } , \mathbf { e } _ { c } \rangle$ , but this does not account for whether $c ^ { * }$ actually helps the model reason about $q .$ We instead define reasoning relevance as the degree to which conditioning on a candidate trace improves the model’s probability of producing a correct answer:

$$
c _ {\text { reason }} ^ {*} = \arg \max _ {c \in \mathcal {C}} \mathbb {P} _ {\mathcal {M}} (a = a ^ {*} \mid q, c),\tag{1}
$$

where $a ^ { * }$ is the gold answer. Since computing this exactly is intractable, we approximate it via gold-relevance distillation (Section 3.2): querying a strong judge model to directly assess reasoning relevance for each query-candidate pair. These annotations are then used to train a reasoning-aware retriever via contrastive learning (Section 3.3), which in turn supplies retrieved demonstrations for reinforcement fine-tuning of the target model (Section 3.4). Figure 2 summarizes the complete pipeline.

## 3.2 Gold-Relevance Distillation

To train a reasoning-aware retriever, we need supervision that reflects reasoning utility rather than surface similarity. We propose gold-relevance distillation, which leverages a judge model $\mathcal { M } _ { \mathrm { j u d g e } } \ ( e . g . \ \mathrm { G P T - 4 o } )$ to directly assess the reasoning relevance of candidate traces for a given query.

Given the training set $\mathcal { D }$ and corpus ${ \mathcal { C } } ,$ , we construct relevance labels via pairwise evaluation:

1. For each training problem $q _ { i } .$ , enumerate all candidate traces $c \in { \mathcal { C } }$ , forming the complete set of query-context pairs.

2. For each pair $( q _ { i } , c )$ , prompt the judge model $\mathcal { M } _ { \mathrm { j u d g e } }$ to assess whether the reasoning trace in c exhibits transferable reasoning patterns that are relevant to solving $q _ { i }$

3. Assign binary relevance labels $y _ { i , c } \in \{ 0 , 1 \}$ , where $y _ { i , c } = 1$ if the judge determines that the reasoning patterns in c are structurally relevant to $q _ { i }$ , even if the two problems difer in surface-level content.

The judge is prompted to evaluate reasoning-structural similarity rather than surface similarity: two problems are deemed reasoning-relevant if they share analogous solution strategies, mathematical structures, or proof techniques, regardless of whether they involve similar topics or notation. This pairwise evaluation avoids the circularity of relying on an initial retriever that may miss reasoning-relevant traces due to low surface similarity, ensuring that gold labels capture true reasoning utility across the entire corpus.

## 3.3 Reasoning-Aware Retriever Training

Using the gold-relevance annotations, we train a dense retriever $\scriptstyle { \mathcal { R } } _ { \theta }$ via contrastive learning. For each query $q _ { i }$ , let $\mathcal { C } _ { i } ^ { + } = \{ c \in \mathcal { C } : y _ { i , c } = 1 \}$ denote the set of reasoning-relevant traces. We optimize the InfoNCE objective:

$$
\mathcal {L} _ {\text { retrieval }} = - \sum_ {i} \sum_ {c ^ {+} \in \mathcal {C} _ {i} ^ {+}} \log \frac {\exp (\langle \mathbf {e} _ {q _ {i}} , \mathbf {e} _ {c ^ {+}} \rangle / \tau)}{\sum_ {c \in \mathcal {C} _ {i}} \exp (\langle \mathbf {e} _ {q _ {i}} , \mathbf {e} _ {c} \rangle / \tau)},\tag{2}
$$

where $\tau$ is a temperature hyperparameter. This objective encourages $\scriptstyle { \mathcal { R } } _ { \theta }$ to rank traces that genuinely aid reasoning higher than semantically similar but reasoning-irrelevant alternatives.

## 3.4 Reinforcement Fine-Tuning with Retrieved Demonstrations

A key challenge in reinforcement fine-tuning is that dificult problems produce sparse reward signals: if the model rarely generates correct answers, it receives little useful gradient information for improvement. Prior work addresses this through curriculum design (Li et al., 2026) or stepwise hints (Zhang et al., 2025a), but these approaches require explicit problem decomposition or teacher annotation at the step level. Retrieved reasoning traces ofer a natural alternative: by conditioning on analogous solved examples, the model’s efective success rate on challenging problems increases, yielding denser reward signals without modifying the reward function or training curriculum.

With the reasoning-aware retriever $\scriptstyle { \mathcal { R } } _ { \theta }$ fixed, we fine-tune the target model $\mathcal { M } _ { \phi }$ via reinforcement fine-tuning with retrieved demonstrations. Our approach is compatible with any policy optimization algorithm. We describe the general procedure below and instantiate it with GRPO (Shao et al., 2024) in our experiments. For each training problem $( q , a )$ :

1. Retrieve top-k reasoning traces $\{ c _ { 1 } , \ldots , c _ { k } \} = \mathcal { R } _ { \theta } ( q , \mathcal { C } )$ from the corpus.

2. Sample a group of G responses $\{ \hat { a } _ { 1 } , \dots , \hat { a } _ { G } \} \sim \mathcal { M } _ { \phi } ( \cdot \vert q , c _ { 1 } , \dots , c _ { k } )$ conditioned on the retrieved traces.

3. Compute rewards $r ( \hat { a } _ { g } , a )$ based on answer correctness.

4. Update $\mathcal { M } _ { \phi }$ using the policy optimization objective with normalized advantages.

When instantiated with ${ \mathrm { G R P O } } .$ , the objective computes advantages relative to the group mean reward:

$$
\mathcal {L} _ {\mathrm{GRPO}} = \mathbb {E} _ {(q, a) \sim \mathcal {D}} \left[ - \frac {1}{G} \sum_ {g = 1} ^ {G} A _ {g} \cdot \log \mathcal {M} _ {\phi} (\hat {a} _ {g} \mid q, \{c _ {j} \}) \right],\tag{3}
$$

where $A _ { g } = ( r ( \hat { a } _ { g } , a ) - \bar { r } ) / { \sigma _ { r } }$ is the normalized advantage. The critical insight is that retrieved traces serve as reasoning scafolding: rather than relying solely on parametric knowledge, the model learns to extract and transfer solution strategies from analogous demonstrations, efectively increasing the density of reward signals during training. We condition the policy update on $\{ c _ { j } \}$ rather than on $q$ alone for two reasons. First, the rollouts $\hat { a } _ { g }$ are themselves sampled from $\mathcal { M } _ { \phi } ( \cdot \mid q , \{ c _ { j } \} )$ , so the importance-sampling identity requires the update distribution to match the sampling distribution, otherwise the advantage estimate is biased. Second, marginalizing over $\{ c _ { j } \}$ would force the model to either ignore retrieved context (collapsing to standard GRPO) or learn an implicit retrieval policy, neither of which captures the intended training signal that the model should learn to use retrieved analogies when they are supplied.

## 4 Experiments

We first compare RA-RFT against standard RLVR baselines and state-of-the-art methods (Section 4.2), then conduct ablation studies that disentangle the contributions of retrieval augmentation, the training objective, the choice of policy optimizer, and retriever quality (Section 4.3).

## 4.1 Experimental Setup

Models. We experiment with the Qwen3 (Qwen Team, 2025) model family at two scales: Qwen3-1.7B, Qwen3-4B as starting checkpoints. For gold-relevance distillation (Section 3.2), we use Qwen3-235B-A22B to generate and summarize reasoning traces for the retrieval corpus, and GPT-4o as the judge model $\mathcal { M } _ { \mathrm { j u d g e } }$ to produce binary reasoning-relevance labels. To make the pairwise evaluation tractable, we restrict judge comparisons to pairs that share the same coarse problem-type label, reducing the number of calls by roughly an order of magnitude (see Section A for details). For the reasoning-aware retriever, we initialize $\scriptstyle { \mathcal { R } } _ { \theta }$ from Reason-ModernColBERT (Chafin, 2025), a late-interaction multi-vector retrieval model, and further fine-tune it with the contrastive objective described in Section 3.3.

Training data. We mainly adopt the training dataset of QuestA (Li et al., 2026) for a fair comparison. Specifically, a total of 12.5k problems selected in QuestA are used as training queries in all training. We construct the retrieval corpus C using the queries in the OpenR1-Math-220K (Hugging Face, 2025) dataset, but exclude any problems that overlap with the training set to prevent learning shortcuts. Both the training queries and the corpus traces are examined to ensure that they do not contain any problems from the evaluation benchmarks.

<table><tr><td>Method</td><td>AIME24</td><td>AIME25</td><td>HMMT25</td><td>BrUMO25</td><td>Avg.</td><td>Avg. (all)</td></tr><tr><td colspan="7">Qwen3-4B</td></tr><tr><td>Base (Instruct)</td><td>70.5</td><td>64.3</td><td>41.3</td><td>65.5</td><td>58.7</td><td>60.4</td></tr><tr><td>+ GRPO</td><td>74.8</td><td>66.4</td><td>46.4</td><td>69.8</td><td>62.5</td><td>64.4</td></tr><tr><td>+  $OPSD^†$ </td><td>76.0</td><td>66.9</td><td>45.2</td><td>-</td><td>62.7</td><td>-</td></tr><tr><td>+ RA-RFT (Ours)</td><td>75.8</td><td>69.2</td><td>47.3</td><td>75.7</td><td>64.1</td><td>67.0</td></tr><tr><td colspan="7">Qwen3-1.7B</td></tr><tr><td>Base (Instruct)</td><td>48.1</td><td>35.9</td><td>23.4</td><td>50.9</td><td>35.8</td><td>39.6</td></tr><tr><td>+ GRPO</td><td>50.4</td><td>41.6</td><td>26.3</td><td>54.8</td><td>39.4</td><td>43.3</td></tr><tr><td>+  $OPSD^†$ </td><td>51.4</td><td>38.3</td><td>25.0</td><td>-</td><td>38.2</td><td>-</td></tr><tr><td>+ QuestA</td><td>52.0</td><td>42.7</td><td>26.0</td><td>52.6</td><td>40.2</td><td>43.3</td></tr><tr><td>+ RA-RFT (Ours)</td><td>55.1</td><td>48.7</td><td>28.2</td><td>57.4</td><td>44.0</td><td>47.4</td></tr></table>

Table 1 Performance comparison across mathematical reasoning benchmarks for Qwen3 models. We report average@32 accuracy in percentage except for OPSD<sup>†</sup> whose results are taken from the original paper using average@16. “Avg.” averages over AIME24, AIME25, and HMMT25; “Avg. (all)” includes all benchmarks when applicable. Bold indicates the best result per model size. Highlighted rows mark our method.

Evaluation benchmarks. We evaluate on four competition-level mathematical reasoning benchmarks: AIME 2024 (MAA, 2024), AIME 2025 (MAA, 2024), HMMT February 2025 (HMMT, 2025), and BrUMO 2025 (BrUMO, 2025). We report average@32 accuracy using temperature 1.0 and a maximum generation length of 32,768 tokens for all experiments.

Baselines. We compare against these baseline methods: (1) Base (Instruct): the base model with thinking mode enabled; (2) GRPO (Shao et al., 2024): standard group relative policy optimization with binary outcome rewards, using 16 rollouts per problem and maximum generation length of 32,768 tokens; (3) OPSD (Zhao et al., 2026): a self-distillation method where a single LLM acts as both teacher and student. The teacher conditions on privileged reasoning traces while the student sees only the question, and training minimizes per-token divergence between these distributions over the student’s own rollouts. Note that OPSD did not release the checkpoint, so we report the results from the original paper, which uses average@16 for evaluation; (4) QuestA (Li et al., 2026): a state-of-the-art RLVR method that injects partial solutions into training problems to create a smoother dificulty curriculum and denser reward signals. We reproduce their method following their oficial guidelines except that we use a more generic and recent base model Qwen3-series.

Implementation details. For all reinforcement fine-tuning methods, we sample 16 responses per problem and disable the KL penalty. We use 64 H100 (80GB) GPUs for training all model variants. We use the AdamW optimizer with a learning rate of $1 \times 1 0 ^ { - 6 }$ . The maximum rollout length is 32,768 tokens. At training time, we retrieve k = 1 reasoning trace per problem, and we keep k = 1 for all experiments unless otherwise specified. All experiments use full-parameter training and are conducted using VeRL (Sheng et al., 2025). Hyperparameter τ for retriever training is set to 0.05. We include additional details in Section A.

## 4.2 Main Results

Table 1 reports results on competition-level mathematical reasoning benchmarks across two model scales. On Qwen3-1.7B, RA-RFT improves over standard GRPO by +4.7 on AIME24, +7.1 on AIME25, +1.9 on HMMT25, and +2.6 on BrUMO25. On Qwen3-4B, RA-RFT achieves the best results on three out of four benchmarks, with notable gains on BrUMO25 (+5.9) and AIME25 (+2.8) over GRPO. Compared to OPSD, which leverages privileged reasoning traces via on-policy self-distillation, RA-RFT achieves stronger performance using only outcome rewards. We report QuestA results for Qwen3-1.7B only, as the data the authors released did not yield gains at the 4B scale in our preliminary experiments.

![](images/6c319f5a587289f49dc382dc5873507b3c89d7dd64919d75a8dbeea66a65365f.jpg)

![](images/746811f0dfa760d24ba6c27ec9c20d37cfdb7792e475014e489d7b4a32631dc9.jpg)

![](images/86fb0aab13c34acf3629d982251e4e5fff7c2759db5344dffcdbb33e71eeeb2d.jpg)

![](images/5ee7b237b6126856a1d8c14947993279f6feb40cf270a430241872a0398d44ae.jpg)  
Figure 3 Comparison of validation average@32 accuracy across training steps on Qwen3-1.7B. The step-0 accuracy for each method is annotated in the bottom-right corner of each subfigure. Notably, RA-RFT starts at a lower step-0 accuracy than GRPO across all benchmarks, as the base model is initially distracted by the unfamiliar retrieved context. As reinforcement fine-tuning progresses, the model learns to efectively leverage the retrieved reasoning traces, ultimately surpassing GRPO by a substantial margin.

<table><tr><td>Method</td><td>AIME24</td><td>AIME25</td><td>HMMT25</td><td>BrUMO25</td><td>Avg.</td></tr><tr><td>SFT</td><td>48.9</td><td>36.0</td><td>23.1</td><td>50.7</td><td>39.7</td></tr><tr><td>RA-SFT</td><td>48.6</td><td>39.5</td><td>22.8</td><td>51.2</td><td>40.5</td></tr><tr><td>GRPO</td><td>50.4</td><td>41.6</td><td>26.3</td><td>54.8</td><td>43.3</td></tr><tr><td>RA-RFT (Ours)</td><td>55.1</td><td>48.7</td><td>28.2</td><td>57.4</td><td>47.4</td></tr></table>

Table 2 Comparison of training objectives and retrieval augmentation on Qwen3-1.7B. We report average@32 accuracy. Highlighted row marks our method.

Figure 3 compares validation accuracy curves across training steps. RA-RFT not only converges to a higher final accuracy than GRPO but also exhibits faster learning in early training stages, suggesting that retrieved reasoning traces provide informative learning signals that accelerate policy improvement.

## 4.3 Ablation Studies

SFT vs. RA-SFT vs. GRPO vs. RA-RFT. We compare four training configurations to disentangle retrieval augmentation from the training objective. SFT performs standard supervised fine-tuning on teacher-generated reasoning traces; RA-SFT adds the same retrieved trace to the SFT prompt, providing the same context as RA-RFT but with a cross-entropy objective. Table 2 reports results on Qwen3-1.7B. Retrieval augmentation provides negligible benefit under supervised fine-tuning (RA-SFT 40.5 vs. SFT 39.7), because SFT minimizes a token-level loss against fixed targets and the model simply imitates the teacher regardless of what auxiliary information is in the prompt. The contrast with RA-RFT confirms that the benefit of retrieved reasoning traces is unlocked only when the training objective allows the model to explore and selectively integrate external evidence into its own reasoning process, rather than passively copying a fixed solution.

Context diversity drives problem-level accuracy variation. Figure 4 examines how diferent retrieved contexts afect accuracy at the individual problem level. For each test problem, we retrieve top-4 traces from our reasoning-aware retriever and evaluate the model independently under each retrieved context, plotting the resulting accuracy distribution alongside the raw GRPO baseline. We observe that the top-1 retrieved context (dark blue) lifts the per-problem accuracy above the GRPO baseline for the majority of problems across all four benchmarks. In addition, there is a substantial spread across retrieved contexts for many problems: the vertical range bars reveal that the best-performing context for a given problem can exceed the worst-performing context by a wide margin, indicating that diferent retrieved traces surface distinct solution strategies.

Retriever comparison. We compare our reasoning-aware retriever against several alternatives before and after finetuning with reasoning supervision: (1) Qwen3-Embedding-4B (Zhang et al., 2025b), a strong single-vector dense retriever, used here as the of-the-shelf RAG baseline; (2) Reason-ModernColBERT (Chafin, 2025), a late-interaction multi-vector model trained on reasoning-intensive data that performs well on the BRIGHT benchmark (Su et al., 2025); (3) Random trace from the corpus, which can ablate the efect of external retriever. Table 3 reports the results on Qwen3-1.7B. First, gold relevance supervision is necessary: fine-tuning lifts Qwen3-Embedding-4B from 38.5 to 40.5 and Reason-ModernColBERT from 40.7 to 47.4 average accuracy, confirming that aligning retrieval scores with reasoning utility is essential. Second, multi-vector late-interaction retrieval is better suited for reasoning-intensive retrieval (Chafin, 2025): Reason-ModernColBERT already matches Qwen3-Emb-4B without supervision (40.7 vs. 38.5), and the gap widens after fine-tuning (47.4 vs. 40.5). Direct ranking evaluation against held-out gold-relevance labels confirms the same trend, with our fine-tuned retriever also achieving substantially higher recall@1 than the of-the-shelf checkpoint. Notably, even when the retriever does not perfectly recover the gold-relevant trace, the gain from conditioning RL on externally retrieved reasoning-intensive traces remains substantial, indicating that RA-RFT is robust to imperfect retrieval and benefits from the broader pool of structurally analogous reasoning patterns surfaced by the retriever.

![](images/810e3f2464963f956a0ba0aa3727abc3abfa37336040bd2de4b3bb9ecf0764f5.jpg)

Figure 4 Per-sample accuracy of RA-RFT under diferent retrieved contexts versus raw GRPO on Qwen3-1.7B. Each sample is sorted by its average@32 accuracy in raw GRPO (orange diamond). Dark blue dots show accuracy under the top-1 retrieved context. Light blue dots show accuracy under other retrieved contexts. Dashed horizontal lines mark the benchmark-level averages on all problems.

<table><tr><td>Retriever</td><td>R@1</td><td>AIME24</td><td>AIME25</td><td>HMMT25</td><td>BrUMO25</td><td>Avg.</td></tr><tr><td>Qwen3-Emb-4B</td><td>2.3</td><td>47.5</td><td>36.6</td><td>23.6</td><td>46.1</td><td>38.5</td></tr><tr><td>Qwen3-Emb-4B + 📄</td><td>14.7</td><td>49.8</td><td>39.0</td><td>24.8</td><td>48.3</td><td>40.5</td></tr><tr><td>R-ModernColBERT</td><td>7.2</td><td>48.3</td><td>40.9</td><td>22.9</td><td>50.8</td><td>40.7</td></tr><tr><td>R-ModernColBERT + 📄</td><td>43.5</td><td>55.1</td><td>48.7</td><td>28.2</td><td>57.4</td><td>47.4</td></tr><tr><td>Random Trace Context</td><td>0.0</td><td>46.9</td><td>36.8</td><td>22.4</td><td>44.2</td><td>37.6</td></tr></table>

Table 3 Ablation on retrieval models using Qwen3-1.7B with RA-RFT training. $\frac { 9 \pi } { 2 0 0 }$ indicates the retriever is fine-tuned with our reasoning supervision. R@1 is the retriever’s recall@1 (in %) on a held-out gold-relevance evaluation set of 10,000 samples. The remaining columns are downstream RA-RFT average@32 accuracy (in %). The bottom block reports test runs that replace the reasoning-aware top-1 trace with a random trace from the same problem-type bucket. Gray denotes the best retriever configuration that is adopted in all experiments unless otherwise specified. Qwen3-Embed-4B is short for Qwen3-Embedding-4B. R-ModernColBERT is short for Reason-ModernColBERT.

## 5 Conclusion

We introduce Retrieval-Augmented Reinforcement Fine-Tuning (RA-RFT), a post-training framework that teaches language models to reason by analogy. The key insight is that efective retrieval for reasoning must be grounded in reasoning utility rather than surface-level similarity: a structurally analogous problem, even if topically unrelated, can provide a transferable solution scafold that guides the model toward the right problem reduction. We hope RA-RFT can inspire future work on extending analogical reasoning to other domains, richer retrieval corpora, and tighter integration between retrieval and language model post-training.

## References

Negar Arabzadeh, Wenjie Ma, Sewon Min, and Matei Zaharia. Restructuring the corpus makes RAG work for math. In The 5th Workshop on Mathematical Reasoning and AI at NeurIPS 2025, 2025. https://openreview.net/forum? id=6cYmnzJViJ.

Tom B. Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, Sandhini Agarwal, Ariel Herbert-Voss, Gretchen Krueger, Tom Henighan, Rewon Child, Aditya Ramesh, Daniel M. Ziegler, Jefrey Wu, Clemens Winter, Christopher Hesse, Mark Chen, Eric Sigler, Mateusz Litwin, Scott Gray, Benjamin Chess, Jack Clark, Christopher Berner, Sam McCandlish, Alec Radford, Ilya Sutskever, and Dario Amodei. Language models are few-shot learners. In Hugo Larochelle, Marc’Aurelio Ranzato, Raia Hadsell, Maria-Florina Balcan, and Hsuan-Tien Lin, editors Advances in Neural Information Processing Systems 33: Annual Conference on Neural Information Processing Systems 2020, NeurIPS 2020, December 6-12, 2020, virtual, 2020. https://proceedings.neurips.cc/paper/2020 hash/1457c0d6bfcb4967418bfb8ac142f64a-Abstract.html.

BrUMO. BrUMO 2025, 2025. https://brumo.org.

Locke Cai and Ivan Provilkov. Escaping the verifier: Learning to reason via demonstrations. arXiv preprint arXiv:2511.21667, 2025.

Antoine Chafin. Reason-moderncolbert, 2025. https://huggingface.co/lightonai/Reason-ModernColBERT.

DeepSeek-AI. Deepseek-r1: Incentivizing reasoning capability in llms via reinforcement learning. arXiv preprint arXiv:2501.12948, 2025.

Aniket Didolkar, Nicolas Ballas, Sanjeev Arora, and Anirudh Goyal. Metacognitive reuse: Turning recurring LLM reasoning into concise behaviors. arXiv preprint arXiv:2509.13237, 2025.

Dedre Gentner. Structure-mapping: A theoretical framework for analogy. Cognitive Science, 7(2):155–170, 1983.

Anirudh Goyal, Abram L. Friesen, Andrea Banino, Theophane Weber, Nan Rosemary Ke, Adrià Puigdomènech Badia, Arthur Guez, Mehdi Mirza, Peter Conway Humphreys, Ksenia Konyushkova, Michal Valko, Simon Osindero, Timothy P. Lillicrap, Nicolas Heess, and Charles Blundell. Retrieval-augmented reinforcement learning. In Kamalika Chaudhuri, Stefanie Jegelka, Le Song, Csaba Szepesvári, Gang Niu, and Sivan Sabato, editors, International Conference on Machine Learning, ICML 2022, 17-23 July 2022, Baltimore, Maryland, USA, Proceedings of Machine Learning Research, pages 7740–7765. PMLR, 2022. https://proceedings.mlr.press/v162/goyal22a.html.

Kelvin Guu, Kenton Lee, Zora Tung, Panupong Pasupat, and Mingwei Chang. Retrieval augmented language model pre-training. In International conference on machine learning, pages 3929–3938. PMLR, 2020.

HMMT. HMMT february 2025, 2025. https://www.hmmt.org.

Keith J. Holyoak and Paul Thagard. Mental Leaps: Analogy in Creative Thought. MIT Press, 1996.

Hugging Face. Open r1: A fully open reproduction of deepseek-r1, January 2025. https://github.com/huggingface/ open-r1.

Junwei Lan, Jianlyu Chen, Zheng Liu, Chaofan Li, Siqi Bao, and Defu Lian. Retro\*: Optimizing LLMs for reasoningintensive document retrieval. arXiv preprint arXiv:2509.24869, 2025.

Patrick Lewis, Ethan Perez, Aleksandra Piktus, Fabio Petroni, Vladimir Karpukhin, Naman Goyal, Heinrich Küttler, Mike Lewis, Wen-tau Yih, Tim Rocktäschel, Sebastian Riedel, and Douwe Kiela. Retrieval-augmented generation for knowledge-intensive nlp tasks. In Advances in Neural Information Processing Systems, volume 33, 2020.

Jiazheng Li, Hongzhou Lin, Hong Lu, Kaiyue Wen, Zaiwen Yang, Jiaxuan Gao, Yi Wu, and Jingzhao Zhang. Questa: Expanding reasoning capacity in LLMs via question augmentation. In The Fourteenth International Conference on Learning Representations, 2026. https://openreview.net/forum?id=3MifB0f7qR.

Yuan Li, Qi Luo, Xiaonan Li, Bufan Li, Qinyuan Cheng, Bo Wang, Yining Zheng, Yuxin Wang, Zhangyue Yin, and Xipeng Qiu. R3-RAG: learning step-by-step reasoning and retrieval for llms via reinforcement learning. In Christos Christodoulopoulos, Tanmoy Chakraborty, Carolyn Rose, and Violet Peng, editors, Findings of the Association for Computational Linguistics: EMNLP 2025, Suzhou, China, November 4-9, 2025, pages 10491–10507. Association for Computational Linguistics, 2025. https://aclanthology.org/2025.findings-emnlp.554/.

Jiachang Liu, Dinghan Shen, Yizhe Zhang, Bill Dolan, Lawrence Carin, and Weizhu Chen. What makes good in-context examples for GPT-3? In Proceedings of Deep Learning Inside Out (DeeLIO): The 3rd Workshop on Knowledge Extraction and Integration for Deep Learning Architectures, pages 100–114, 2022.

Jingyu Liu, Jiaen Lin, and Yong Liu. How much can rag help the reasoning of llm? arXiv preprint arXiv:2410.02338, 2024.

Zichen Liu, Changyu Chen, Wenjun Li, Penghui Qi, Tianyu Pang, Chao Du, Wee Sun Lee, and Min Lin. Understanding r1-zero-like training: A critical perspective. In Second Conference on Language Modeling, 2025. https://openreview. net/forum?id=5PAF7PAY2Y.

MAA. American invitational mathematics examination (AIME), 2024. https://maa.org/math-competitions/ american-invitational-mathematics-examination-aime.

MiniMax. Minimax-m1: Scaling test-time compute eficiently with lightning attention. CoRR, abs/2506.13585, 2025. doi: 10.48550/ARXIV.2506.13585. https://doi.org/10.48550/arXiv.2506.13585.

OpenAI. Learning to reason with llms. 2024. https://openai.com/index/learning-to-reason-with-llms/.

Penghui Qi, Xiangxin Zhou, Zichen Liu, Tianyu Pang, Chao Du, Min Lin, and Wee Sun Lee. Rethinking the trust region in LLM reinforcement learning. arXiv preprint arXiv:2602.04879, 2026.

Qwen Team. Qwen3 technical report. arXiv preprint arXiv:2505.09388, 2025.

Ori Ram, Yoav Levine, Itay Dalmedigos, Dor Muhlgay, Amnon Shashua, Kevin Leyton-Brown, and Yoav Shoham. In-context retrieval-augmented language models. Transactions of the Association for Computational Linguistics, 11: 1316–1331, 2023.

Ohad Rubin, Jonathan Herzig, and Jonathan Berant. Learning to retrieve prompts for in-context learning. In Proceedings of the 2022 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, pages 2655–2671, 2022.

Zhihong Shao, Peiyi Wang, Qihao Zhu, Runxin Xu, Junxiao Song, Mingchuan Zhang, Y. K. Li, Y. Wu, and Daya Guo. Deepseekmath: Pushing the limits of mathematical reasoning in open language models. CoRR, abs/2402.03300, 2024. doi: 10.48550/ARXIV.2402.03300. https://doi.org/10.48550/arXiv.2402.03300.

Guangming Sheng, Chi Zhang, Zilingfeng Ye, Xibin Wu, Wang Zhang, Ru Zhang, Yanghua Peng, Haibin Lin, and Chuan Wu. Hybridflow: A flexible and eficient rlhf framework. In Proceedings of the Twentieth European Conference on Computer Systems, pages 1279–1297, 2025.

Hongjin Su, Howard Yen, Mengzhou Xia, Weijia Shi, Niklas Muennighof, Han yu Wang, Liu Haisu, Quan Shi, Zachary S Siegel, Michael Tang, Ruoxi Sun, Jinsung Yoon, Sercan O Arik, Danqi Chen, and Tao Yu. BRIGHT: A realistic and challenging benchmark for reasoning-intensive retrieval. In The Thirteenth International Conference on Learning Representations, 2025. https://openreview.net/forum?id=ykuc5q381b.

Mirac Suzgun, Mert Yuksekgonul, Federico Bianchi, Dan Jurafsky, and James Zou. Dynamic cheatsheet: Test-time learning with adaptive memory. In Proceedings of the 19th Conference of the European Chapter of the Association for Computational Linguistics (Volume 1: Long Papers), pages 7080–7106, 2026.

Di Wu, Devendra Singh Sachan, Wen-tau Yih, and Mingda Chen. Procedural knowledge at scale improves reasoning. arXiv preprint arXiv:2604.01348, 2026.

Xiaocong Yang, Jiacheng Lin, Ziqi Wang, and Chengxiang Zhai. Learning by analogy: Enhancing few-shot prompting for math word problem solving with computational graph-based retrieval. arXiv preprint arXiv:2411.16454, 2024.

Tianzhu Ye, Li Dong, Xun Wu, Shaohan Huang, and Furu Wei. On-policy context distillation for language models. arXiv preprint arXiv:2602.12275, 2026.

Qiying Yu, Zheng Zhang, Ruofei Zhu, Yufeng Yuan, Xiaochen Zuo, YuYue, Weinan Dai, Tiantian Fan, Gaohong Liu, Juncai Liu, LingJun Liu, Xin Liu, Haibin Lin, Zhiqi Lin, Bole Ma, Guangming Sheng, Yuxuan Tong, Chi Zhang, Mofan Zhang, Ru Zhang, Wang Zhang, Hang Zhu, Jinhua Zhu, Jiaze Chen, Jiangjie Chen, Chengyi Wang, Hongli Yu, Yuxuan Song, Xiangpeng Wei, Hao Zhou, Jingjing Liu, Wei-Ying Ma, Ya-Qin Zhang, Lin Yan, Yonghui Wu, and Mingxuan Wang. DAPO: An open-source LLM reinforcement learning system at scale. In The Thirty-ninth Annual Conference on Neural Information Processing Systems, 2025. https://openreview.net/forum?id=2a36EMSSTp.

Kaiyi Zhang, Ang Lv, Jinpeng Li, Yongbo Wang, Feng Wang, Haoyuan Hu, and Rui Yan. Stephint: Multi-level stepwise hints enhance reinforcement learning to reason. arXiv preprint arXiv:2507.02841, 2025a.

Yanzhao Zhang, Mingxin Li, Dingkun Long, Xin Zhang, Huan Lin, Baosong Yang, Pengjun Xie, An Yang, Dayiheng Liu, Junyang Lin, Fei Huang, and Jingren Zhou. Qwen3 embedding: Advancing text embedding and reranking through foundation models. arXiv preprint arXiv:2506.05176, 2025b.

Siyan Zhao, Zhihui Xie, Mengchen Liu, Jing Huang, Guan Pang, Feiyu Chen, and Aditya Grover. Self-distilled reasoner: On-policy self-distillation for large language models, 2026. https://arxiv.org/abs/2601.18734.

Longtao Zheng, Rundong Wang, Xinrun Wang, and Bo An. Synapse: Trajectory-as-exemplar prompting with memory for computer control. In The Twelfth International Conference on Learning Representations, 2024.

## Appendix

## A Additional Implementation Details

<div class="mineru-algorithm" style="white-space: pre-wrap; font-family:monospace;">
Algorithm 1 Retrieval-Augmented Reinforcement Fine-Tuning (RA-RFT)

Require: Training set $\mathcal{D} = \{(q_i, a_i)\}_{i=1}^N$; corpus $\mathcal{C} = \{(p_j, t_j)\}_{j=1}^M$; judge model $\mathcal{M}_{\text{judge}}$; target model $\mathcal{M}_{\phi}$; dense encoder $\mathcal{R}_{\theta}$; group size $G$; number of retrieved traces $k$; temperature $\tau$

1: // Stage 1: Gold-Relevance Distillation (Section 3.2)
2: for each $(q_i, a_i) \in \mathcal{D}$ do
3:    for each $c \in \mathcal{C}$ do
4:    $y_{i,c} \leftarrow \mathcal{M}_{\text{judge}}(q_i, c)$ ▷ binary reasoning-relevance label
5:    $\mathcal{C}_i^+ \leftarrow \{c \in \mathcal{C} : y_{i,c} = 1\}$

6: // Stage 2: Reasoning-Aware Retriever Training (Section 3.3)
7: while $\mathcal{R}_{\theta}$ not converged do
8:    Sample minibatch $\mathcal{B} \subset \mathcal{D}$
9:    $\mathcal{L}_{\text{retrieval}} \leftarrow -\sum_{i \in \mathcal{B}} \sum_{c^+ \in \mathcal{C}_i^+} \log \frac{\exp(\langle \mathbf{e}_{q_i}, \mathbf{e}_{c^+} \rangle / \tau)}{\sum_{c \in \mathcal{C}_i} \exp(\langle \mathbf{e}_{q_i}, \mathbf{e}_c \rangle / \tau)}$
10:    Update $\theta \leftarrow \theta - \eta \nabla_{\theta} \mathcal{L}_{\text{retrieval}}$

11: // Stage 3: Reinforcement Fine-Tuning with Retrieved Demonstrations (Section 3.4)
12: while $\mathcal{M}_{\phi}$ not converged do
13:    Sample minibatch $\mathcal{B} \subset \mathcal{D}$
14:    for each $(q, a) \in \mathcal{B}$ do
15:    $\{c_1, \ldots, c_k\} \leftarrow \mathcal{R}_{\theta}(q, \mathcal{C})$ ▷ retrieve top-$k$ reasoning traces
16:    Sample $\{\hat{a}_1, \ldots, \hat{a}_G\} \sim \mathcal{M}_{\phi}(\cdot | q, c_1, \ldots, c_k)$
17:    $r_g \leftarrow r(\hat{a}_g, a)$ for $g = 1, \ldots, G$ ▷ outcome-based rewards
18:    Compute advantages $\{A_g\}_{g=1}^G$ from $\{r_g\}$
19:    Update $\phi$ via policy optimization with $\{A_g\}_{g=1}^G$
20: return trained model $\mathcal{M}_{\phi}$
</div>

Gold Relevance Distillation. Algorithm 1 outlines the complete RA-RFT pipeline. In Stage 1 (lines 3–7), the judge model $\mathcal { M } _ { \mathrm { j u d g e } }$ (GPT-4o) evaluates each query-candidate pair to produce binary reasoning-relevance labels. Concretely, the judge is presented with two question-answer pairs and asked to determine whether they share transferable reasoning patterns, such as reliance on the same theorems, algorithms, or proof techniques (see the full prompt template in Figure 7). The judge outputs a brief justification followed by a binary yes/no relevance decision. Naïvely evaluating all $| \mathcal { D } | \times | \mathcal { C } |$ pairs would be prohibitively expensive. To reduce the number of comparisons, we leverage the coarse problem-type labels (e.g. algebra, combinatorics, geometry, number theory) already present in the metadata of the source datasets. The judge evaluation is then restricted to pairs that share the same problem type, as cross-type reasoning transfer is rare in practice. This filtering reduces the total number of judge calls by approximately an order of magnitude while preserving nearly all reasoning-relevant pairs.

VerifiableRewardDesign. We adopt a binary outcome-based reward function $r ( \hat { a } _ { g } , a )$ that verifies the correctness of each sampled response $\hat { a } _ { g }$ against the ground-truth answer a. Formally:

$$
r (\hat {a} _ {g}, a) = \left\{ \begin{array}{l l} 1 & \text {if} \mathbf {v e r i f y} (\mathrm{extract} (\hat {a} _ {g}), a) = \mathbf {T r u e}, \\ 0 & \text {otherwise}, \end{array} \right.\tag{4}
$$

where extrac $; ( \hat { a } _ { g } )$ parses the model output to locate the final \boxed{...} expression, and verify(·, ·) performs symbolic equivalence checking between the extracted prediction and the ground truth. The verification handles mathematical equivalences such as $0 . 5 = \textstyle { \frac { 1 } { 2 } }$ and $2 x = x \cdot 2$ by normalizing both the prediction and the ground truth into canonical symbolic forms before comparison. We implement this using the math\_verify library, which supports both LaTeX-level and expression-level extraction for predictions and LaTeX-level extraction for gold answers.

<table><tr><td>Setting</td><td>AIME24</td><td>AIME25</td><td>HMMT25</td><td>BrUMO25</td><td>Avg.</td></tr><tr><td>GRPO (no retrieval)</td><td>50.4</td><td>41.6</td><td>26.3</td><td>54.8</td><td>43.3</td></tr><tr><td>GRPO + retrieval at inference-time</td><td>44.3</td><td>35.3</td><td>22.1</td><td>49.2</td><td>37.7</td></tr><tr><td>RA-RFT (Ours)</td><td>55.1</td><td>48.7</td><td>28.2</td><td>57.4</td><td>47.4</td></tr></table>

Table 4 Inference-time-only retrieval diagnostic: GRPO checkpoint evaluated with the reasoning-aware retriever’s top-1 trace prepended at inference. Highlighted row marks our method.

Retriever Training Details. We fine-tune lightonai/Reason-ModernColBERT, a ColBERT-style multi-vector model pre-trained on reasoning-intensive corpora. Multi-vector retrieval is preferred over single-vector retrieval because late interaction over per-token embeddings better captures structural reasoning similarity (e.g. shared proof techniques or algorithmic patterns) beyond surface-level lexical overlap. We train with contrastive loss at temperature $\tau { = } 0 . 0 5$ for 3 epochs, with a batch size of 128, learning rate $3 \times 1 0 ^ { - 5 }$ , linear warmup over 10% of steps, and weight decay 0.01. Embeddings are gathered across all GPUs before computing the contrastive objective, maximizing the number of in-batch negatives without increasing per-device memory. All training is done in bfloat16. We hold out 5% of the training data for evaluation and select the checkpoint with the best recall@1 on this set for usage in the following reinforcement fine-tuning stage. The single vector retriever was trained with the same hyperparameters and training data, but using Qwen/Qwen3-Embedding-4B as the base model.

Train/test contamination. The QuestA training queries and the OpenR1-Math-220K (Hugging Face, 2025) retrieval corpus are both derived from NuminaMath-1.5, whose contributing sources (AoPS Forum, AMC/AIME 1984–2023, MATH, Olympiads) predate the AIME 2024/2025, HMMT February 2025, and BrUMO 2025 benchmarks we evaluate on. In addition, the open-r1 toolkit ships an 8-gram decontamination script targeting AIME 2024/25 and MATH-500 (Hugging Face, 2025), so the released corpus excludes verbatim matches against those benchmarks. Therefore, the training and corpus dataset do not contain any samples from test benchmarks used.

On the Choice of Models for Corpus Curation. Neither Qwen3-235B-A22B (trace generator) nor GPT-4o (relevance judge) is essential to RA-RFT. Both are used only for one-time, ofline corpus curation and never appear in the training or inference loop. Crucially, RA-RFT is not a distillation method: corpus traces serve as in-context demonstrations for diferent queries during RL rollouts, and the policy is supervised only by the verifiable outcome reward on its own rollout, never by a token-level loss against any teacher response. We chose Qwen3-235B-A22B because a stronger trace generator yields a higher fraction of correct derivations and thus a cleaner retrieval corpus, and GPT-4o for the judge purely for cost: it ofered the best per-call price among frontier models. Other open-source LLM should yield qualitatively similar results in either role.

## B Additional Experimental Results

Inference-time-only retrieval diagnostic. To probe whether the RA-RFT gain comes from inference-time access to retrieved context rather than from training-time co-adaptation, we evaluate the standard GRPO checkpoint with the same reasoning-aware retriever’s top-1 trace prepended only at inference. We stress this is a diagnostic, not a competitive baseline: the GRPO checkpoint has never seen retrieved context during training, so it is not optimized to consume one. As shown in Table 4, this configuration does not match RA-RFT, isolating the contribution of training the policy under retrieved demonstrations rather than just supplying them at evaluation time.

Policy optimization methods. Our framework is agnostic to the choice of policy optimization algorithm (Section 3.4). We instantiate RA-RFT with two diferent base optimizers (RLOO and DAPO) while keeping all other components fixed, and compare each against its retrieval-augmented counterpart. As shown in Table 5, retrieval augmentation consistently improves average accuracy by 3.7 and 1.8 points over RLOO and DAPO respectively, demonstrating that the benefit of reasoning-aware retrieval is not tied to any particular policy optimization algorithm and transfers across diferent training objectives.

<table><tr><td>Method</td><td>AIME24</td><td>AIME25</td><td>HMMT25</td><td>BrUMO25</td><td>Avg.</td></tr><tr><td>RLOO</td><td>51.7</td><td>39.2</td><td>24.4</td><td>51.7</td><td>41.8</td></tr><tr><td>RA-RLOO</td><td>55.8</td><td>44.6</td><td>28.6</td><td>53.1</td><td>45.5</td></tr><tr><td>DAPO</td><td>50.6</td><td>42.0</td><td>24.5</td><td>53.1</td><td>42.6</td></tr><tr><td>RA-DAPO</td><td>54.0</td><td>42.8</td><td>27.5</td><td>53.3</td><td>44.4</td></tr></table>

Table 5 Ablation on policy optimization algorithms within the RA-RFT framework using Qwen3-1.7B.

## C Case Study

Figure 5 illustrates a representative case where RA-RFT dramatically outperforms standard GRPO on an AIME 2025 problem (13/32 vs. 1/32 sampling correct). The retrieved context question shares no surface similarity with the target, yet it encodes the same structural reasoning pattern, providing a scafold that guides the model toward the correct problem reduction. Standard GRPO attempted a diferent solution because of lacking this analogical signal, but misinterpreted the requirement and ultimately arrived at a wrong answer. This example highlights the core mechanism of RA-RFT: reasoning-aware retrieval transfers solution strategies rather than surface features.

## D Prompt Templates

We use three prompt templates throughout the RA-RFT pipeline, each serving a distinct role. Figure 8 shows the reasoning trace summarization prompt directly taken from previous work (Arabzadeh et al., 2025), which instructs Qwen3-235B-A22B to rewrite raw corpus solutions into concise, step-by-step traces that highlight reusable reasoning strategies. Figure 7 shows the gold-relevance distillation judge prompt, which asks GPT-4o to determine whether two questions share transferable reasoning patterns and output a binary relevance label along with a brief justification. Figure 6 shows the RA-RFT training and inference prompt, which prepends a retrieved reasoning-analogous exemplar (reference question and its reasoning trace) to the target query, providing the model with an in-context demonstration to guide its solution.

## E Limitations

RA-RFT adds a separate retriever and a one-time GPT-4o judge pass for gold-relevance labels: the retriever is small relative to the policy and frozen during RL. In addition, training the reasoning-aware retriever does require a one-time annotation pass from a strong judge model to produce gold-relevance labels, which incurs labeling cost beyond what standard RLVR pipelines need. We consider this a favorable trade-of: the upfront labeling budget is fixed and modest, while the trained retriever enables the diversity of retrieved contexts that drive substantial and consistent gains across benchmarks and model scales, and the retriever can be reused across diferent training runs and even diferent base models as long as the retrieval corpus remains the same. While we validate RA-RFT on competition-level mathematical reasoning benchmarks, the underlying principle of analogical reasoning is domain-general, and extending the framework to other reasoning-intensive domains, such as code generation or scientific problem solving, requires only constructing an appropriate retrieval corpus with reasoning traces, which we leave for future work.

![](images/3039a1b9c2308088088a038febaef17644aea4034397123af3dfd9e011dc36b4.jpg)  
Figure 5 Case study comparing RA-RFT and standard GRPO on an AIME 2025 problem. Left: the RA-RFT model, conditioned on a retrieved reasoning trace about coloring a convex n-gon, correctly identifies a block-counting decomposition and arrives at the answer 907. Right: standard GRPO without retrieval misinterprets the adjacency constraint as a no-three-consecutive condition and applies an incorrect DP recurrence. The retrieved context question is structurally analogous since both problems count valid configurations under local adjacency constraints. However they share no surface-level similarity as the target problem involves the context of arranging the chairs and context question is about coloring a convex n-gon.

![](images/2e386ba0377e3df6ba4a8556f5fb5a1197a0e2e16e24284f146be4aef5a7af14.jpg)  
Figure 6 Prompt template used during both RA-RFT training and inference. The retrieved reasoning-analogous exemplar, including the reference question and its reasoning trace, is prepended to the training query.

![](images/7e55362389ff0bcb446b2287df21c39333048ff4e9a3064f1e66c936e51b79c3.jpg)  
Figure 7 Prompt template for the judge model in gold-relevance distillation (Section 3.2). The judge evaluates whethe two questions share transferable reasoning patterns, producing binary relevance labels for retriever training.

Instruction. You are given a math problem and its solution. Your goal is to rewrite the solution into a clearly labeled, step-by-step concise format that teaches how to solve the problem.

## Guidelines.

\- Each step should reflect a logical phase in solving the problem.

\- Use a concise “cheatsheet” style so learners can generalize the strategy to harder or related problems.

\- If the problem or solution is incomplete or noisy, infer reasonable steps and still provide guidance.

\- Focus on key ideas, strategies, or techniques the learner can reuse.

\- Keep at most 7 steps; be concise and avoid verbosity.

\- Avoid over-fragmentation; combine actions logically where appropriate.

## Output format.

Problem: [Copy the problem exactly as given]

Step 1: [Short label]

[Brief explanation of what’s being done and why, with any relevant

calculations]

Step 2: [Next short label]

[Brief explanation and math]

Step N: [Final step]

[Brief explanation and final processing or insight]

Therefore, the final answer is: \$\boxed{[final answer]}\$

Given problem: {corpus\_question} {corpus\_solution}

![](images/c6a8fc52e20646f9daca27cddb8ce9457c27f61ea45270c2363b699e10772b68.jpg)

## Example Reasoning Trace from Corpus

Problem: The set of positive integer solutions to the inequality \$2x-3 \leq 5\$ is\_\_\_\_.

## Step 1: Solve the inequality algebraically

Add 3 to both sides: \$2x - 3 + 3 \leq 5 + 3 \Rightarrow 2x \leq 8\$.

Divide by 2: \$x \leq 4\$.

Step 2: Identify the domain constraint

We seek positive integer solutions, so \$x\$ must satisfy \$x > 0\$ and \$x \in \mathbb{Z} \$.

Thus, \$x = 1, 2, 3, \dots\$

Step 3: Combine conditions and list valid solutions

From \$x \leq 4\$ and \$x \geq 1\$ (positive integers), the possible values are \$x = 1, 2, 3, 4\$.

Therefore, the final answer is: \$\boxed{1, 2, 3, 4}\$

Figure 8 Prompt template for reasoning trace summarization (top) and an example summarized reasoning trace from the corpus (bottom). Raw solutions are condensed into concise, step-by-step traces that highlight reusable reasoning strategies.
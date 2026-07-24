2 Gradient of Q

Next we diferentiate against $\mathrm { Q }$ ,

$$
\begin{array}{l} {d O [ S ] = d Q [ S ] K [ S ] ^ {\top} V [ S ]} \\ {d O [ T ] = d Q [ T ] K [ S ] ^ {\top} V [ S ] + \mathrm{diag} ((d Q [ T ] \odot K [ T ]) \mathbf {1} _ {T \times 1}) V [ T ]} \end{array}
$$

Which results in

$$
\begin{array}{l} d L = \operatorname{tr} \left((\frac {\partial L}{\partial O [ S ]}) ^ {\top} d Q [ S ] K [ S ] ^ {\top} V [ S ]\right) + \operatorname{tr} \left((\frac {\partial L}{\partial O [ T ]}) ^ {\top} (d Q [ T ] K [ S ] ^ {\top} V [ S ]\right) \\ \quad + \operatorname{diag} ((d Q [ T ] \odot K [ T ]) \mathbf {1} _ {T \times 1}) V [ T ])). \end{array}
$$

So that

$$
\frac {d L}{d Q [ S ]} = \frac {\partial L}{\partial O [ S ]} V [ S ] ^ {\top} K [ S ].
$$

To derive $\frac { d L } { d Q [ T ] }$ , we need to pull $d Q [ T ]$ out of the unconventional expression diag $\left( ( d Q [ T ] \odot \right)$ $K [ T ] ) \mathbf { 1 } _ { T \times 1 } )$ , within the trace operator. Let’s first write it in terms of Einstein summation, abbreviation $\begin{array} { r } { \frac { \partial L } { \partial O [ T ] } , Q [ T ] , K [ T ] , V [ T ] } \end{array}$ by $X , Q , K , V$ respectively.

$$
\operatorname{tr} \left(X ^ {\top} \operatorname{diag} \left(\left(d Q \odot K\right) \mathbf {1} _ {T \times 1}\right) V\right) = \sum_ {i j k \ell} X _ {j i} d Q _ {j k} K _ {j k} \delta_ {j \ell} V _ {\ell i},
$$

where $\delta$ is the Kronecker delta matrix given by

$$
\delta_ {j \ell} = \left\{ \begin{array}{l l} 1 & \text { if } j = \ell , \\ 0 & \text { otherwise }. \end{array} \right.
$$

Note that

$$
\sum_ {i \ell} X _ {j i} K _ {j k} \delta_ {j \ell} V _ {\ell i} = \sum_ {i} X _ {j i} V _ {j i} K _ {j k} = (\operatorname{diag} ((X \odot V) \mathbf {1} _ {T \times 1}) K) _ {j k}.
$$

Thus the second half of the expression for dL (with respect to $d Q [ T ] )$ is given by

$$
\operatorname{tr} \left(\left(K [ S ] ^ {\top} V [ S ] \left(\frac {\partial L}{\partial O [ T ]}\right) ^ {\top} + \left(\operatorname{diag} \left(\left(\frac {\partial L}{\partial O [ T ]} \odot V [ T ]\right) \mathbf {1} _ {T \times 1}\right) K [ T ]\right) ^ {\top}\right) d Q [ T ]\right).
$$

Thus since diagonal matrix is invariant under transposition,

$$
\frac {\partial L}{\partial Q [ T ]} = \frac {\partial L}{\partial O [ T ]} V [ S ] ^ {\top} K [ S ] + \operatorname{diag} ((\frac {\partial L}{\partial O [ T ]} \odot V [ T ]) \mathbf {1} _ {T \times 1}) K [ T ].
$$

## B.1.3 Gradient of K

Similar computation shows

$$
\begin{array}{l} \frac {\partial L}{\partial K [ S ]} = V [ S ] ((\frac {\partial L}{\partial O [ S ]}) ^ {\top} Q [ S ] + (\frac {\partial L}{\partial O [ T ]}) ^ {\top} Q [ T ]) = V [ S ] (\frac {\partial L}{\partial O}) ^ {\top} Q \\ \frac {\partial L}{\partial K [ T ]} = \operatorname{diag} ((\frac {\partial L}{\partial O [ T ]} \odot V [ T ]) \mathbf {1} _ {T \times 1}) Q [ T ] \end{array}
$$

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

## B.1.5 With shifted Elu activation

Shifted elu (and its derivative) are defined by

$$
\varphi (x) = \left\{ \begin{array}{l l} x, & \text { if } x \geq 1, \\ e ^ {x - 1}, & \text { if } x <   1, \end{array} \right. \quad \text { and } \quad \varphi^ {\prime} (x) = \left\{ \begin{array}{l l} 1, & \text { if } x \geq 1, \\ e ^ {x - 1}, & \text { if } x <   1. \end{array} \right.
$$

Given,

$$
O [ S ] = \varphi (Q [ S ]) \varphi (K [ S ]) ^ {\top} V [ S ]
$$

$$
O [ T ] = \varphi (Q [ T ]) \varphi (K [ S ]) ^ {\top} V [ S ] + \Delta (\varphi (Q [ T ]), \varphi (K [ T ])) V [ T ]
$$

Gradients are given by (partly by guessing via dimension match)

$$
\frac {\partial L}{\partial Q [ S ]} = (\frac {\partial L}{\partial O [ S ]} V [ S ] ^ {\top} \varphi (K [ S ])) \odot \varphi^ {\prime} (Q [ S ])
$$

$$
\frac {\partial L}{\partial Q [ T ]} = (\frac {\partial L}{\partial O [ T ]} V [ S ] ^ {\top} \varphi (K [ S ])) \odot \varphi^ {\prime} (Q [ T ]) + \Delta (\frac {\partial L}{\partial O [ T ]}, V [ T ]) (\varphi^ {\prime} (Q [ T ]) \odot \varphi (K [ T ]))
$$

$$
\frac {\partial L}{\partial K [ S ]} = (V [ S ] (\frac {\partial L}{\partial O}) ^ {\top} \varphi (Q)) \odot \varphi^ {\prime} (K [ S ])
$$

$$
\frac {\partial L}{\partial K [ T ]} = \Delta (\frac {\partial L}{\partial O [ T ]}, V [ T ]) (\varphi (Q [ T ]) \odot \varphi^ {\prime} (K [ T ]))
$$

$$
\frac {d L}{d V [ S ]} = \varphi (K [ S ]) \varphi (Q) ^ {\top} \frac {\partial L}{\partial O}
$$

$$
\frac {d L}{d V [ T ]} = \Delta (\varphi (Q [ T ]), \varphi (K [ T ])) \frac {\partial L}{\partial O [ T ]}.
$$

## B.2 Activation for Quasi-Linear Attention

The choice of activation function $\varphi$ in Section 3.2.2 is non-linear but otherwise arbitrary and depends on the specific application at hand. The same activation also need not always be used, for instance one can have two diferent activations $\varphi _ { 1 }$ and $\varphi _ { 2 }$ and apply them as:

$$
O [ S ] = \varphi_ {1} (Q [ S ]) \varphi_ {2} (\varphi_ {1} (K [ S ]) ^ {\top} V [ S ]),
$$

$$
O [ T ] = \varphi_ {1} (Q [ T ]) \varphi_ {2} (\varphi_ {1} (K [ S ]) ^ {\top} V [ S ]) + \Delta (\varphi_ {1} (Q [ T ]), \varphi_ {1} (K [ T ])) V [ T ].
$$

## C More on Reconstruction Loss

The reconstruction loss is a measure of how much information of the full UIH is captured by VISTA’s virtual embeddings. We used L2 norm to measure how much we can reconstruct the original UIH given the virtual embedding as input, and we have verified that it is an informative metric for us to quantitatively measure the reconstruction quality.

![](images/e504e3874e6eb01f748112104094241df3492edb7d16cad846b98fee6549f166.jpg)  
Figure 11: Comparing the reconstruction loss over training steps with and without explicitly including it in the total loss on the Amazon dataset. The dotted line is the final evaluation reconstruction loss.

On the Amazon dataset, for example, we can see that training the VISTA model without explicitly minimizing the reconstruction loss still reduces the reconstruction loss of the learned embedding against the full UIH as the model improves. However, the reconstruction loss plateaus and the model takes longer to converge after some training steps (as our training pipeline supports early stopping). With the explicit introduction of the reconstruction loss, we see a dramatic decrease in the reconstruction loss in the first training steps and faster model convergence. The test metrics also improved by 0.22% AUC and 1.11% NE with the use of the reconstruction loss.

## D Additional Experiment Details

## D.1 Datasets

We include more details about the datasets used in our experiments. The statistics of the sequence features of each dataset are summarized in Table 5.

Amazon-Electronics. The Amazon Products and Reviews dataset Hou et al. (2024) contains user reviews, item metadata, and user-item interactions. A subset of this data was preprocessed to make the Amazon-Electronics dataset, which is restricted to electronics items, initiated by Zhou et al. (2018). The data format is relatively simple, with the columns: label, user id, item id, category id, item history, and category history.

Table 5: Dataset Statistics

<table><tr><td>Dataset</td><td>Mean Seq.</td><td>Max Seq.</td></tr><tr><td>Amazon-Electronics</td><td>8.93</td><td>429</td></tr><tr><td>KuaiRand-1K</td><td>225.20</td><td>256</td></tr><tr><td>Simplified Prod</td><td>1528.18</td><td>2,000</td></tr><tr><td>Industrial-Scale Data</td><td>7,000</td><td>16,000</td></tr></table>

KuaiRand-1K. The KuaiRand dataset by Gao et al. (2022) is a sequential recommendation dataset collected from the recommendation logs of the video-sharing mobile app Kuaishou. The KuaiRand-1K subset contains a random sample 1,000 users after removing irrelevant videos. There are 4 million videos remaining in this subset. Our experiments use a subset of all features available in KuaiRand-1K, namely user id, video id, video id history, click history, like history, and lvv (long video view) history.

Simplified Production and Industrial-Scale Data. The full production data is too large to be able to run simple experiments quickly (and requires re-implementing baseline models on internal systems). We construct a minimal version of our production data to focus on the sequential recommendation task (e.g., keeping the user interaction history largely intact but removing other features). After preprocessing, this dataset has a mean sequence length of around 1528 and maximum truncated to 2,000.

## D.2 FuxiCTR Framework

We utilize the FuxiCTR library developed by Zhu et al. (2022; 2021) for our traditional sequential setting experiments. As mentioned in the main text, we designed the traditional sequential setting experiments mainly to compare the efectiveness of the attention layers and keep constant other model architecture and hyperparameter choices. (See Figure 12.)

We also report the common hyperparameters used in all the experiment results in Table 13.

![](images/6d7681332233602bbc4fc216ef8e61da165aaeb1dd0c1aa1fac9fdaebcc3f2c0.jpg)

<table><tr><td>Hyperparameter</td><td>Amazon</td><td>KuaiRand</td><td>Simplified Prod</td></tr><tr><td>Learning Rate</td><td>5.0e-4</td><td>1.0e-4</td><td>1.0e-3</td></tr><tr><td>Optimizer</td><td>Adam</td><td>Adam</td><td>Adam</td></tr><tr><td>Batch Size</td><td>1024</td><td>1024</td><td>128</td></tr><tr><td>Batch Norm</td><td>No</td><td>No</td><td>Yes</td></tr><tr><td>Early Stop Patience</td><td>4</td><td>5</td><td>1</td></tr><tr><td>Embedding Regularizer</td><td>0.005</td><td>None</td><td>None</td></tr><tr><td>Embedding Dimension</td><td>64</td><td>32</td><td>32</td></tr><tr><td>Embedding Initializer</td><td>1e-4</td><td>1e-4</td><td>1e-4</td></tr><tr><td>MLP Hidden Units</td><td>[1024, 512, 256]</td><td>[512, 128, 64]</td><td>[512, 128, 64]</td></tr><tr><td>MLP Activations</td><td>RELU</td><td>RELU</td><td>RELU</td></tr><tr><td># Attention Heads</td><td>4</td><td>4</td><td>4</td></tr><tr><td># Attention Layers</td><td>1</td><td>1</td><td>2</td></tr></table>

Figure 12: FuxiCTR Setup.  
Figure 13: Common hyperparameters used for traditional setting experiments.

The model-specific parameters for VISTA are the number of seeds and weight for the reconstruction loss, which were set at 128 and 1.0, respectively, for all experiments. No specific hyperparameter tuning was done, mainly relying on using common parameters for all models and repeating across 3 seeds for each model and dataset.

## D.3 More on VISTA’s Two-Stage Attention

Case Study 1: Same User, Diferent Candidates. In the following Figure 14, we show the input to the virtual attention layer, the output of the virtual attention layer, and then

Visualization of VISTA's Two-Stage Attention Same User, Different Candidates

Input to Virtual Attention Layer

Virtual Embeddings

Attention Output Virtual + Target

![](images/2d1e5c7749c3037f6bad672bb5f5148738bbf680ab08efc3d30bb64201a6e1ae.jpg)  
Figure 14: Visualizing the virtual attention and target attention layers for the same user on two diferent candidates (one positive at the top and one negative at the bottom).

the output of the target attention layer for the same user for two diferent candidates (one positive at the top and one negative at the bottom) from the Amazon-Electronics dataset. We also reduce these along the feature dimension for compact visualization. Note that since we are looking at two candidates for the same user, the input to the virtual attention layer and the output of the virtual attention layer are identical; these only depend on the user’s individual UIH and the virtual seed embeddings which are common between the two. The diference in this case comes at the target attention part. Here we see that the target attention diferentiates between positive and negative candidates for this user as evidenced by the difering mean activation for the target embedding.

Case Study 2: Diferent UIH Lengths. We also look at a case study comparing two diferent users with diferent UIH histories, one with a very short history (length 4) and another with a slightly longer history (length 12) in Figure 15. Even with very little historical data (UIH length 4 at the top), the virtual seed embeddings appear to help influence the virtual embeddings, which in turn help with model performance.

Virtual Embeddings

Input to Virtual Attention Layer

Visualization of VISTA's Two-Stage Attention Different Users with Different UIH Length

Attention Output Virtual + Target

![](images/a4027180a3d6a8e1f92b49b4f7b871296fb9365c60ef3f4aefb89bb143207da7.jpg)  
Figure 15: Visualizing the virtual attention and target attention layers for the diferent users having diferent UIH sequence lengths (both positive candidates).

## ItemRAG: Item-Based Retrieval-Augmented Generation for LLM-Based Recommendation

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

## MMSRARec: Summarization and Retrieval Augumented Sequential Recommendation Based on Multimodal Large Language Model

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

## Selective LLM-Guided Regularization for Enhancing Recommendation Models

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

## Ofline Reasoning for Eficient Recommendation: LLM-Empowered Persona-Profiled Item Indexing

# Ofline Reasoning for Eficient Recommendation: LLM-Empowered Persona-Profiled Item Indexing

Deogyong Kim Yonsei University Seoul, South Korea legenduck@yonsei.ac.kr

Junseong Lee<sup>∗</sup> Yonsei University Seoul, South Korea brulee@yonsei.ac.kr

Jeongeun Lee Yonsei University Seoul, South Korea ljeadec31@yonsei.ac.kr

Dongha Lee<sup>†</sup> Yonsei University Seoul, South Korea donalee@yonsei.ac.kr

Changhoe Kim NAVER Seongnam, South Korea andres.chkim@navercorp.co

Junguel Lee NAVER Seongnam, South Korea junguel.lee@navercorp.com

Jungseok Lee NAVER Seongnam, South Korea jungseok.lee@navercorp.com

## Abstract

Recent advances in large language models (LLMs) ofer new op portunities for recommender systems by capturing the nuanced semantics of user interests and item characteristics through rich semantic understanding and contextual reasoning. In particular, LLMs have been employed as rerankers that reorder candidate items based on inferred user–item relevance. However, these approaches often require expensive online inference-time reasoning, leading to high latency that hampers real-world deployment.

In this work, we introduce Persona4Rec, a recommendation framework that performs ofline reasoning to construct interpretable persona representations of items, enabling lightweight and scalable real-time inference. In the ofline stage, Persona4Rec leverages LLMs to reason over item reviews, inferring diverse user motiva tions that explain why diferent types of users may engage with an item; these inferred motivations are materialized as persona representations, providing multiple, human-interpretable views of each item. Unlike conventional approaches that rely on a single item representation, Persona4Rec learns to align user profiles with the most plausible item-side persona through a dedicated encoder, efectively transforming user–item relevance into user–persona relevance. At the online stage, this persona-profiled item index al lows fast relevance computation without invoking expensive LLM reasoning. Extensive experiments show that Persona4Rec achieves performance comparable to recent LLM-based rerankers while sub stantially reducing inference time. Moreover, qualitative analysis confirms that persona representations not only drive eficient scor ing but also provide intuitive, review-grounded explanations. These results demonstrate that Persona4Rec ofers a practical and inter pretable solution for next-generation recommender systems.<sup>1</sup>

<sup>∗</sup>Both authors contributed equally to this research. <sup>†</sup>Corresponding author <sup>1</sup>https://github.com/legenduck/PERSONA4REC

![](images/1a360a67f51867b4513ef099939e7827ed1d5018ba89fa0e8a3eb91a61a98fa1.jpg)  
Figure 1: Comparison between existing LLM-based item rerankers (Upper) and our Persona4Rec (Lower). Persona4Rec shifts LLM reasoning from online inference to ofline persona construction, enabling real-time recommendation via lightweight similarity scoring.

## Keywords

Large Language Models, Reasoning-enhanced Recommendation, User and Item Profiling, Eficient Reranking

## ACM Reference Format:

Deogyong Kim, Junseong Lee, Jeongeun Lee, Dongha Lee, Changhoe Kim, Junguel Lee, and Jungseok Lee. 2026. Ofline Reasoning for Eficient Recommendation: LLM-Empowered Persona-Profiled Item Indexing. In Proceedings of Make sure to enter the correct conference title from your rights confirmation email (Conference acronym ’XX). ACM, New York, NY, USA, 11 pages. https://doi.org/XXXXXXX.XXXXXXX

behind user preferences and item characteristics [8, 23, 50]. Recent advances in large language models (LLMs) have opened new oppor tunities for recommendation by leveraging their strong semantic understanding and contextual reasoning capabilities [11, 20, 21, 52]. These abilities allow LLMs to process complex textual inputs such as reviews and item descriptions, leading to richer user and item representations and more personalized recommendations [24, 51].

One widely adopted approach to employing LLMs in recommen dation is to construct user profiles [18, 31, 33]. These profiles are in ferred from user interaction histories, often by leveraging metadata and reviews, to capture their overall tendencies across behavioral patterns. By providing a compact yet expressive representation of user interests, user profiles enable models to enhance personaliza tion [46, 48] and serve as a foundation for various downstream recommendation tasks. For instance, they support explainable recommendation by aligning user interests with item attributes to generate concise, personalized justifications [43], improve rank ing quality by refining candidate ordering [16], and simulate user behavior in dynamic recommendation scenarios [4].

Another growing line of work has explored LLMs as rerankers to refine the candidate items retrieved by first-stage recommenders (i.e., candidate generators) such as CF models [9]. Early studies adopt prompt-only, zero/few-shot listwise reranking [1, 13, 28– 30, 37], where LLMs are prompted to directly output a permuta tion of the candidate set. Following approaches introduce domain adaptation and fine-tuning techniques [2, 26, 47] to improve con trollability and stability for recommendation tasks. More recent methods leverage LLM reasoning to infer user preferences from raw signals such as interaction histories and reviews [3, 7, 16], while others adopt reinforcement learning to further align reranking with recommendation objectives [25, 35]. Overall, this growing line of research highlights how LLMs can fundamentally advance recommendation by moving beyond traditional interaction signals toward more semantically rich and context-aware modeling.

Despite these advances, such approaches remain impractical for real-world deployment, where real-time recommendation is essen tial for user experience. Their online (inference) stage involves multiple time-consuming reasoning steps that cause substantial latency, whereas computation time is far less critical in the ofline (training) stage (Figure 1, Upper). Specifically, it includes (1) con structing user profiles from historical interactions such as ratings and reviews, (2) generating item profiles from metadata and user feedback, and (3) performing reasoning-based reranking by comparing candidate items through these profiles. Because user histories evolve dynamically, RSs must repeatedly infer user profiles from the latest interactions and then reason over them to assess item rel evance, which substantially increases inference latency and poses serious challenges for eficiency and scalability.

To address these challenges, we introduce a novel approach that achieves low-latency inference by leveraging item-side reasoning pre-computed ofline, thereby supporting both the eficient construction of user profiles and the eficient scoring of candidate items (Figure 1, Lower). This ofline reasoning step extracts fine grained, subjective preference aspects from item reviews, which can later be used to dynamically compose user profiles from their interaction histories. These extracted aspects are then re-organized into an item-side knowledge index that enables recommender systems to eficiently compute user–item relevance at inference time through lightweight semantic similarity scoring. This design not only enables scalable, real-time recommendation but also yields interpretable outputs, as each recommendation is grounded in reviewbased reasoning derived from the ofline process.

Table 1: Comparison of text-based reranking methods in terms of eficiency and reasoning paradigm. “Reasoning” denotes when the reasoning process is performed (online during inference or ofline as a pre-computation step).

<table><tr><td>Method</td><td>Latency</td><td>Scalability</td><td>Reasoning</td><td>Explain.</td></tr><tr><td>ZS-LLM [13]</td><td>High</td><td>Low</td><td>Online</td><td>✕</td></tr><tr><td>RankVicuna [29]</td><td>High</td><td>Low</td><td>Online</td><td>✕</td></tr><tr><td>TALLRec [2]</td><td>Middle</td><td>Low</td><td>Online</td><td>✕</td></tr><tr><td>EXP3RT [16]</td><td>High</td><td>Low</td><td>Online</td><td>√</td></tr><tr><td>PERSONA4Rec (ours)</td><td>Low</td><td>High</td><td>Offline</td><td>√</td></tr></table>

In this work, we propose Persona4Rec, which introduces the notion of hypothetical user personas—interpretable profiles that encode plausible rationales, extracted from item reviews, for why certain users might engage with the item. Rather than relying on a single representation per item, Persona4Rec represents items through multiple personas to reflect potential user motivations in a humanunderstandable form; each persona can also be interpreted as a latent user segment likely to prefer the corresponding item. During inference, user profiles aggregated from historical interactions are aligned with the most relevant persona via a lightweight encoder, trained on interaction-derived user-persona pairs to reflect realistic engagement patterns; this replaces direct user-item matching with user–persona alignment. In this way, recommendations are generated through eficient similarity scoring over a persona-profiled item index, where each persona serves as an independent retrieval unit linked to its source item, and the selected persona naturally provides an intuitive rationale for each ranked item.

Our extensive experiments mainly investigate the trade-of between recommendation accuracy and inference eficiency, comparing Persona4Rec against state-of-the-art LLM-based rerankers. The results show that Persona4Rec achieves comparable accuracy to state-of-the-art LLM-based rerankers while reducing inference time by up to 99.6%, demonstrating its practicality for large-scale deployment. Moreover, qualitative analysis confirms that the selected personas provide user-grounded and interpretable explanations.

The main contributions of this work are summarized as follows:

• We propose Persona4Rec, a novel framework that shifts reasoning ofline and enables eficient-yet-efective reranking through lightweight user–item relevance scoring.

• Extensive experiments demonstrate that Persona4Rec achieves real-time eficiency while maintaining performance comparable to state-of-the-art LLM-based rerankers.

• By leveraging precomputed item personas, Persona4Rec naturally provides faithful and human-readable explanations for recommendation outcomes.

![](images/335ea814ab1566a9ee7213c6b4352ff4c6c580e7c90f45a2e5be95ebeb77ff63.jpg)  
Figure 2: Overview of our Persona4Rec framework. The ofline process (Left) constructs item personas and trains a userpersona alignment encoder. The online process (Right) reranks candidates via eficient similarity scoring

## 2 Related Work

## 2.1 LLM-based Reranking in Recommendation

Early studies demonstrated that LLMs guided by constructed prompts can act as rerankers without task-specific training, often in a listwise form that outputs a permutation over a candidate set [28– 30, 37, 38]. To alleviate long-context costs, follow-up work explored pairwise prompting via PRP [32] and setwise prompting that compares small subsets [54]. While these approaches report strong accuracy, their reliance on autoregressive decoding and long con texts often results in high latency and forces truncation or sliding window heuristics in practice [37, 38].

Recent approaches aligns LLMs with recommendation objectives through instruction tuning or reinforcement learning. TALLRec [2] aligns LLMs with recommendation tasks by instruction tuning on instruction–response pairs, enabling more accurate user–item ranking, and RLRF4Rec [35] directly optimizes a reranker from rec ommender feedback. Review-driven methods such as EXP3RT [16] extract preference evidence from reviews to improve rating pre diction and top-<sup>??</sup> reranking. LLM4Rerank [7] further integrates multiple criteria—including accuracy, diversity, and fairness—by modeling them as interconnected nodes and applying CoT-style reasoning to automatically navigate these nodes during the rerank ing process. Despite these advances, existing reranker designs still depend on costly inference-time reasoning to extract or align pref erences, which limits their scalability in real-time recommendation.

## 2.2 User Profiling for Recommendation

Early recommender systems relied on static or schema-bound user profiles, such as demographics or genre preferences [6]. While these profiles ofered a simple way to represent users, they lacked the capacity to capture nuanced or context-dependent preferences. Subsequent feature-engineered approaches, such as UPCSim [42], attempted to measure profile similarity by correlating user and content attributes. However, hand-crafted features still struggled to reflect fine-grained signals and dynamic shifts in user interests.

To move beyond these limitations, recent studies employ LLMs to summarize, enrich, or generate user profiles directly from interaction histories and side texts. For example, RLMRec [33] integrates LLM-guided representations into collaborative filtering (CF), while KAR [45] and GPG [48] demonstrate that natural-language profile generation can enhance personalization. Other works such as PALR [46] and LettinGo [40] further explore LLM-native profile modeling conditioned on user histories. Taken together, existing work shows the strength of LLMs in modeling user preferences, but most approaches rely on online reasoning at inference time, which incurs high latency. In contrast, our work shifts both userand item-side profiling to an ofline stage, enabling eficient and scalable recommendation while retaining semantic richness.

## 3 Proposed Method

The key idea of Persona4Rec is to shift the costly reasoning process from online (inference) stage to the ofline stage by precomputing review-grounded item personas. Specifically, during ofline stage, Persona4Rec derives multiple personas for each item, where each persona captures a distinct motivation or preference pattern associated with the item. These personas are organized into a personaprofiled item index and serve as the primary units for aligning with user profiles, which summarize user historical interactions, rather than relying on direct alignment with raw item information. During online stage, user profiles are eficiently matched against pre-indexed personas, enabling real-time recommendation without invoking expensive reasoning. Moreover, the selected persona naturally provides a human-interpretable explanation for the recommendation, grounded in evidence from actual user reviews. As illustrated in Figure 2, Persona4Rec consists of two stages:

• <sup>Ofline</sup> <sup>process:</sup> Persona4Rec analyzes item information and reviews to generate multiple personas representing diverse user motivations. These personas are then paired with user profiles to produce user–persona alignment signals, which are used to train a lightweight encoder that embeds both into a shared space and constructs a persona-profiled item index for eficient scoring.

• <sup>Online</sup> <sup>process:</sup> During inference, Persona4Rec constructs user profiles on-the-fly from recent interaction histories, leveraging the precomputed persona representations. For each candidate item, its personas are scored against the user profile via eficient similarity computation, and relevance score is determined by the best-matching persona, which is used for reranking.

## 3.1 Ofline Reasoning

The ofline stage of Persona4Rec performs item-side reasoning through three coordinated steps that transform raw user reviews into structured personas, providing alignment signals for training the user–persona encoder:

(1) Persona Construction (§3.1.1): Persona4Rec integrates item metadata and user reviews to construct multiple distinct and interpretable personas for each item, enabling fine-grained align ment with diverse user preferences.

<sub>(2)</sub> User Profile–Persona Matching (§3.1.2): <sub>Persona4Rec pairs</sub> each user profile with the most relevant persona of an interacted item using an LLM-as-a-judge paradigm, producing user–persona alignment signals.

(3) <sup>Encoder</sup> <sup>Training</sup> <sup>(§3.1.3):</sup> Persona4Rec leverages the result ing matched user–persona pairs to train a lightweight encoder that assigns higher similarity scores to matched pairs than to mismatched ones.

This structured reasoning pipeline leverages an of-the-shelf LLM M to perform profile construction and reasoning over reviews,<sup>2</sup> transforming text into structured supervision for encoder training.

3.1.1 Persona Construction. This step transforms item-side infor mation—objective metadata and subjective review signals—into multiple interpretable personas per item, each representing a dis tinct user motivation for engaging with the item. Metadata provides factual context about what the item is, while reviews reveal why users engaged with it; integrating both enables the LLM M to infer latent user motivations and generate hypothetical user profiles that capture plausible intent beyond explicit review content. <sup>3</sup>

Item Summary Generation (<sub>Objective</sub> Information). <sub>For</sub> <sub>each</sub> item <sup>??</sup>, we instruct the LLM M to produce a concise summary $s _ { i }$ that captures its core identity from the item metadata $m _ { i } ,$ which include fields such as title, description and category.

$$
s _ {i} = \mathcal {M} \big (m _ {i}, \mathcal {I} _ {\mathrm{sum}} \big).\tag{1}
$$

Here, $\mathcal { I } _ { \mathrm { s u m } }$ denotes an instruction prompt to summarize the infor mation of the item. The resulting summary provides a compact representation of the item and serves as an objective reference point for interpreting review-based signals. Importantly, the sum mary also enables persona generation for items with sparse or missing reviews, allowing metadata alone to support efective per sona construction in cold-start settings that commonly occur in practice.

Aspect Extraction (<sub>Subjective</sub> Information). <sub>For</sub> <sub>item</sub> ??<sub>,</sub> <sub>the</sub> LLM M extracts an aspect tuple $a _ { u , i }$ from each review by user <sup>??</sup>:

$$
a _ {u, i} = \mathcal {M} (r _ {u, i}, \mathcal {I} _ {\mathrm{asp}})\tag{2}
$$

Table 2: Example of persona construction for item “The Shadow in the Glass”—a dark retelling of Cinderella.

<table><tr><td>Review Aspects (user AEPTNCI3X5)</td></tr><tr><td>Category Preference: Dark fantasy, gothic retellingsPurchase Purpose: Interest in morally complex reinterpretations of classic fairy talesQuality Criteria: Tension, surprising twists, and morally ambiguous charactersUsage Context: Immersive reading during leisure hours</td></tr><tr><td>Constructed Persona</td></tr><tr><td>Name: The Dark Storyline SeekerDescription: This reader is attracted to darker storylines filled with suspense and moral complexity. They enjoy unpredictable twists and flawed characters whose motives remain uncertain. Rather than seeking comfort, they appreciate stories that challenge expectations and evoke unease.Preference Rationale: This persona appreciates this item because they enjoy a darker storyline with surprises and morally questionable characters, as frequently mentioned in reviews describing the story’s tension and sense of danger.</td></tr></table>

Here, $\mathcal { I } _ { \mathrm { a s p } }$ denotes an instruction prompt that specifies a domainspecific schema with slots such as category preference, purchase purpose, quality criteria, and usage context. To ensure suficient informational coverage, tuples with more than 75% of slots being null fields are discarded. The remaining tuples constitute the item-level aspect pool ${ \mathcal { A } } _ { i } ,$ which serves as input for the subsequent persona generation process. Unlike metadata, which describes what the item is, these aspects capture how users actually experienced and valued the item—providing subjective signals essential for understanding diverse user motivations and informing persona construction.

<sup>Persona</sup> <sup>Generation.</sup> Finally, the LLM M integrates the item summary <sup>??</sup>??(objective context) and review-grounded aspect pool $\mathcal { A } _ { i }$ (subjective review signals)to generate personas:

$$
\mathcal {M}: (s _ {i}, \mathcal {A} _ {i}, \mathcal {I} _ {\mathrm{per}}) \to \Pi_ {i} = \{\pi_ {i} ^ {(1)}, \ldots , \pi_ {i} ^ {(K)} \},\tag{3}
$$

Here, $\boldsymbol { \mathcal { I } } _ { \mathrm { p e r } }$ denotes an instruction prompt for persona generation. The number of personas $K \in [ 2 , 7 ]$ varies based on the diversity of review signals: items with heterogeneous feedback yield more personas, while items with uniform reviews produce fewer. This adaptive range balances persona expressiveness against indexing and scoring overhead. Each persona $\pi _ { i } ^ { ( k ) }$ is a structured record of three fields: name simply describes the persona’s core identity, description provides a brief summary outlining its general tendencies, motivations, and overall attitude toward the item, and preference rationale explains why this persona would appreciate the item, grounded in evidence from $\mathcal { A } _ { i }$ such as review patterns or aspectlevel cues. These fields are serialized into a unified text template.

Table 2 illustrates an example of how review aspects are aggregated into a coherent persona. For the item “The Shadow in the Glass”, its review (written by user AEPTNCI3X5) and the extracted aspects are encapsulated in the persona “<sup>P3:</sup> <sup>Dark</sup> <sup>Sto-</sup> <sup>ryline</sup> <sup>Seeker</sup>”, which captures readers drawn to tension, moral ambiguity, and darker reinterpretations of classic tales.

3.1.2 User-Persona Alignment. This step pairs user profiles with the most relevant persona from each interacted item via LLM-based alignment, producing supervision signals for encoder training.

First, we build user profile $P _ { u } ,$ given a user’s interaction history $H _ { u } ,$ , that summarizes the user’s preferences across recently consumed items by combining objective and subjective signals:

$$
P _ {u} = \left\{\left(s _ {i}, a _ {u, i}\right) \mid i \in H _ {u} \right\}\tag{4}
$$

where we collect, for each item <sup>??</sup> in the user’s history, the item summary <sup>??</sup>?? paired with the aspect tuple $a _ { u , i }$ extracted from the user’s review $r _ { u , i }$ of that item. Since these components are precomputed during the previous persona construction step, assembling user profiles is eficient and requires no additional reasoning.

For each observed interaction $( u , i )$ we employ LLM-as-a-judge approach to select the persona from the target item persona set Π?? that best explains why the user engaged with the item. Given the user profile $P _ { u } ,$ , the target item title $t _ { i , }$ and its persona set $\Pi _ { i } ,$ the LLM M, guided by an alignment instruction $\tau _ { \mathrm { a l i g n } }$ , evaluates their semantic alignment and outputs the most relevant persona $\pi _ { ( u , i ) } ^ { + }$ along with a concise justification $j _ { ( u , i ) } ^ { + } \colon$

$$
\mathcal {M}: (P _ {u}, t _ {i}, \Pi_ {i}, \mathcal {I} _ {\mathrm{align}}) \to \left(j _ {(u, i)} ^ {+}, \pi_ {(u, i)} ^ {+}\right)\tag{5}
$$

This process links each user’s historical preferences with the most representative persona of the target item, yielding the align ment dataset $\mathcal { D } _ { \mathrm { a l i g n } } = \{ ( u , i , \pi _ { ( u , i ) } ^ { + } ) \}$ that converts implicit interac tions into explicit, interpretable supervision for encoder training.

3.1.3 Encoder Training. This step trains a lightweight encoder to embed user profiles and personas into a shared vector space, enabling eficient similarity-based scoring. Using the alignment dataset $\mathcal { D } _ { \mathrm { a l i g n } ; }$ , we train an encoder $E _ { \theta }$ via contrastive learning.

User Profile & Persona Embedding. <sub>We</sub> <sub>encode</sub> <sub>both</sub> <sub>user</sub> <sub>pro-</sub> files and personas using the same encoder $E _ { \theta }$ . For a user $u ,$ we encode the <sup>??</sup>-th most recent interaction as:

$$
e _ {u, l} = E _ {\theta} (\mathrm{concat} (s _ {i _ {l}}, a _ {u, i _ {l}})),\tag{6}
$$

where $l \in \{ 1 , \ldots , L \}$ and $i _ { l }$ denotes the item at position <sup>??</sup>. To obtain a user embedding, we aggregate interaction-level embeddings with a temporal decay factor to account for recency efects:

$$
e _ {u} = \frac {\sum_ {l = 1} ^ {L} \gamma^ {l - 1} \cdot e _ {u , l}}{\sum_ {l = 1} ^ {L} \gamma^ {l - 1}},\tag{7}
$$

where $\gamma \in ( 0 ,$ 1] controls the influence of older interactions. Simi larly, each persona <sup>??</sup> ∈ $\Pi _ { i }$ is embedded as

$$
e _ {\pi} = E _ {\theta} (\pi),\tag{8}
$$

<sup>Contrastive</sup> <sup>Learning.</sup> We optimize the encoder on the align ment dataset $\mathcal { D } _ { \mathrm { a l i g n } }$ using the InfoNCE objective [39]:

$$
\mathcal {L} = - \log \frac {\exp (\text { sim } (e _ {u} , e _ {\pi^ {+}}) / \tau)}{\sum_ {j = 1} ^ {B} \exp (\text { sim } (e _ {u} , e _ {\pi_ {j} ^ {-}}) / \tau)},\tag{9}
$$

where <sup>??</sup> is the batch size, <sup>??</sup> is the temperature, with in-batch negatives. This contrastive objective trains the encoder to approxi mate the LLM-derived alignment supervision by mapping aligned user–persona pairs closer in the embedding space than mismatched pairs. After training, all item personas are encoded once to build a persona-profiled item index, enabling eficient similarity-based scoring during inference without additional LLM reasoning.

Table 3: Statistics of the datasets.

<table><tr><td>Dataset</td><td>#Interactions</td><td>#Users</td><td>#Items</td><td>Sparsity</td></tr><tr><td>Amazon-Books</td><td>309,287</td><td>26,173</td><td>25,130</td><td>99.9530%</td></tr><tr><td>Yelp</td><td>103,774</td><td>7,968</td><td>2,942</td><td>99.5573%</td></tr></table>

![](images/24fcd8790777bcea3f709e4dca7f1f5e6536f47697bdd940680bcca873d50872.jpg)

![](images/97a642b43c8eda2bdf1f89c422c6911b4fc5f30d752b528739eefe9a57070866.jpg)  
Figure 3: Rating distribution of the two dataset

## 3.2 Online Inference

The online stage of Persona4Rec enables eficient real-time recommendation by combining precomputed persona embeddings $e _ { \pi }$ with user profiles $P _ { u }$ composed from the user’s latest interactions. Since all personas are indexed ofline, online inference avoids LLM invocation and requires only lightweight user encoding and similarity scoring against cached embeddings.

<sup>User</sup> <sup>Encoding.</sup> At the online stage, the user embedding $e _ { u }$ is computed by aggregating interaction-level embeddings through the same temporally weighted scheme as in training. Our method operates with as few as one interaction, though richer histories enable more precise persona alignment. When a new interaction occurs with an associated review, the aspect is extracted and cached asynchronously to avoid latency overhead.

Candidate Item Scoring and Reranking. <sub>For</sub> <sub>each</sub> <sub>candidate</sub> item $i \in C _ { u }$ , the relevance score is computed as the maximum similarity between the user embedding and the item’s personas:

$$
\operatorname{score} (u, i) = \max _ {\pi \in \Pi_ {i}} \operatorname{sim} (e _ {u}, e _ {\pi}).\tag{10}
$$

Items are reranked by this score, and the persona achieving the maximum similarity serves as a human-interpretable explanation by providing its description and preference rationale.

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

## 4.3 RQ2: Eficiency & Scalability

We evaluate inference eficiency on a single A6000 GPU, measuring latency and memory usage against LLM-based baselines.

4.3.1 Single-Query Performance. In Table 7, Persona4Rec achieves 0.75ms latency (GPU) or 0.52ms (CPU), representing <sup>1,300</sup>× <sup>speedup</sup> over TALLRec and 104,000<sub>×</sub> over EXP3RT<sub>.</sub> <sub>Memory</sub> <sub>footprint</sub> is similarly reduced: 0.1GB versus 12–15GB for baselines. This eficiency stems from replacing LLM inference with dot-product operations over pre-computed persona embeddings.

4.3.2 Scalability Evaluation. Beyond single-query speed, we assess how Persona4Rec scales under realistic deployment conditions—a critical requirement for production recommender systems serving millions of users. Figure 4 evaluates two dimensions: batch size (concurrent user requests) and item candidate set size.

Table 8: Human evaluation criteria for recommendation explanation quality (RQ3).

<table><tr><td>Evaluation Criteria for Recommendation Explanation</td></tr><tr><td>Intuitiveness: How immediately comprehensible is the explanation? Does it clearly convey why the recommendation makes sense without requiring extensive interpretation?</td></tr><tr><td>Relatability: How well does the explanation connect to the user&#x27;s actual experiences and lifestyle context? Does it resonate with real-world usage scenarios?</td></tr><tr><td>Consistency: How well does the explanation align with the user&#x27;s demonstrated preferences and interaction history? Does it accurately reflect their past behavior patterns?</td></tr><tr><td>Persuasiveness: How convincing is the explanation in demonstrating that the item would appeal to the user? Does it effectively communicate the item&#x27;s value for this specific user?</td></tr><tr><td>Specificity: How personalized and detailed is the explanation for this particular user-item pair? Does it provide concrete, individualized rationale rather than generic statements?</td></tr></table>

<sup>User</sup> <sup>scaling.</sup> In Figure 4 Left, as the number of concurrent users increases from 1 to 100, LLM-based methods exhibit superlinear growth due to sequential processing constraints. TALLRec’s latency grows from 10<sup>4</sup>ms to 10<sup>5</sup>ms (∼100 seconds), while EXP3RT deteriorates from 10<sup>6</sup>ms to over 10<sup>7</sup>ms (exceeding 2 hours). In contrast, Persona4Rec’s latency increased from 10<sup>2</sup>ms to only 10<sup>3</sup>ms.

<sup>Candidate</sup> <sup>scaling.</sup> In Figure 4 Right, when the candidate set size grows from 20 to 100 items, Persona4Rec maintains near-constant latency (flat at ∼1ms) via eficient vector operations. TALLRec scales moderately due to per-item reasoning costs, while EXP3RT remains prohibitively slow regardless of candidate count. This insensitivity to candidate size enables reranking without latency penalties.

Overall, these results confirm that Persona4Rec not only achieves superior eficiency but also exhibits fundamentally diferent scaling characteristics. The architectural advantage of ofline persona construction is amplified under high load, making real-time recommendation at scale practical with lower computational cost.

## 4.4 RQ3: Recommendation Explainability

We evaluate whether persona-based rationales efectively explain recommendations through pairwise comparisons against EXP3RT (online reasoning) and XRec (single-review summary). We evaluate five user-facing criteria that capture the explanatory efectiveness: Intuitiveness, Persuasiveness, Relatability, Consistency, and Specificity. These collectively measure the explainability of recommendation rationales from the target user’s perspective. (Refer to Table 8 for more details.) Following prior work [16, 17], we sample 100 examples per dataset. To ensure objectivity, we employed impartial annotators via Amazon Mechanical Turk (AMT), assigning three independent annotators per example.

In Figure 5, Persona4Rec achieves near-parity with EXP3RT while dominating XRec. Against EXP3RT, we trade specificity for eficiency structure. EXP3RT’s real-time reasoning enables highly personalized rationales tailored to individual contexts, whereas our pre-constructed personas represent aggregated patterns. However, we match EXP3RT in intuitiveness and persuasiveness through structured formatting consistent persona templates, which enhance comprehensibility and review-grounded evidence that provides tangible social proof. Critically, this balanced trade-of delivers in ference speedup, making real-time deployment practical. Compared to XRec, our approach dominates across all dimensions, including specificity. Persona4Rec extracts 2–7 review-grounded personas per item, each capturing a distinct user motivation, while XRec represents each item with a single item profile that aggregates all review signals, limiting its ability to distinguish between dif ferent user motivations. Overall, Persona4Rec delivers efective explainability through ofline pre-defined personas.

![](images/e8a410dde4ab32e84460dbc717f8b877a20759530a379d01e5c84b6d7b696dbb.jpg)  
Figure 5: Human evaluation of Recommendation Explain ability across compared methods. (<sub>∗</sub>: p-value < 0.05)

Table 9: Human evaluation criteria for persona quality comparison between single-persona and multi-persona ap proaches (RQ4).

<table><tr><td>Evaluation Criteria for Persona Quality</td></tr><tr><td>Faithfulness: Are the personas genuinely grounded in actual user reviews of this item? Do they reflect real opinions rather than fabricated or generic descriptions?</td></tr><tr><td>Clarity: Are the personas tailored to this specific item&#x27;s characteristics? Do they capture unique aspects rather than broad, generic user types?</td></tr><tr><td>Coverage: Do the personas collectively cover diverse and meaningful reasons why different users might engage with this item? Are both major and minor preference dimensions represented?</td></tr><tr><td>Interpretability: Are the personas logically coherent and easy to understand? Does each persona present a clear, well-defined user archetype?</td></tr><tr><td>Representativeness: Are the personas sufficiently distinct from each other? Do they effectively represent different user segments rather than redundant variations?</td></tr></table>

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

## References

[1] Mofetoluwa Adeyemi, Akintunde Oladipo, Ronak Pradeep, and Jimmy Lin. 2024. Zero-Shot Cross-Lingual Reranking with Large Language Models for Low Resource Languages. In Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers). 650–656.

[2] Keqin Bao, Jizhi Zhang, Yang Zhang, Wenjie Wang, Fuli Feng, and Xiangnan He. 2023. Tallrec: An efective and eficient tuning framework to align large language model with recommendation. In Proceedings of the 17th ACM conference on recommender systems. 1007–1014.

[3] Maciej Besta, Nils Blach, Ales Kubicek, Robert Gerstenberger, Michal Podstawski, Lukas Gianinazzi, Joanna Gajda, Tomasz Lehmann, Hubert Niewiadomski, Piotr Nyczyk, et al. 2024. Graph of thoughts: Solving elaborate problems with large language models. In Proceedings of the AAAI conference on artificial intelligence, Vol. 38. 17682–17690.

[4] Hongru Cai, Yongqi Li, Wenjie Wang, Fengbin Zhu, Xiaoyu Shen, Wenjie Li, and Tat-Seng Chua. 2025. Large language models empowered personalized web agents. In Proceedings of the ACM on Web Conference 2025. 198–215.

[5] Jianlv Chen, Shitao Xiao, Peitian Zhang, Kun Luo, Defu Lian, and Zheng Liu. 2024. BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation. arXiv:2402.03216 [cs.CL] https://arxiv.org/abs/2402.03216

[6] Ting Chen, Wei-Li Han, Hai-Dong Wang, Yi-Xun Zhou, Bin Xu, and Bin-Yu Zang. 2007. Content recommendation system based on private dynamic user profile. In 2007 International conference on machine learning and cybernetics, Vol. 4. IEEE, 2112–2118.

[7] Jingtong Gao, Bo Chen, Xiangyu Zhao, Weiwen Liu, Xiangyang Li, Yichao Wang, Wanyu Wang, Huifeng Guo, and Ruiming Tang. 2025. Llm4rerank: Llm-based auto-reranking framework for recommendations. In Proceedings of the ACM on Web Conference 2025. 228–239.

[8] Shijie Geng, Shuchang Liu, Zuohui Fu, Yingqiang Ge, and Yongfeng Zhang. 2022. Recommendation as language processing (rlp): A unified pretrain, personalized prompt & predict paradigm (p5). In Proceedings of the 16th ACM conference on recommender systems. 299–315.

[9] Xiangnan He, Kuan Deng, Xiang Wang, Yan Li, Yongdong Zhang, and Meng Wang. 2020. Lightgcn: Simplifying and powering graph convolution network for recommendation. In Proceedings of the 43rd International ACM SIGIR conference on research and development in Information Retrieval. 639–648.

[10] Xiangnan He, Lizi Liao, Hanwang Zhang, Liqiang Nie, Xia Hu, and Tat-Seng Chua. 2017. Neural collaborative filtering. In Proceedings of the 26th international conference on world wide web. 173–182.

[11] Ryang Heo, Yongsik Seo, Junseong Lee, and Dongha Lee. 2025. Can Large Language Models be Efective Online Opinion Miners? arXiv preprint arXiv:2505.15695 (2025).

[12] Yupeng Hou, Jiacheng Li, Zhankui He, An Yan, Xiusi Chen, and Julian McAuley. 2024. Bridging language and items for retrieval and recommendation. arXiv preprint arXiv:2403.03952 (2024).

[13] Yupeng Hou, Junjie Zhang, Zihan Lin, Hongyu Lu, Ruobing Xie, Julian McAuley, and Wayne Xin Zhao. 2024. Large language models are zero-shot rankers for recommender systems. In European Conference on Information Retrieval. Springer, 364–381.

[14] Edward J Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, Weizhu Chen, et al. 2022. Lora: Low-rank adaptation of large language models. ICLR 1, 2 (2022), 3.

[15] Mathias Jackermeier, Jiaoyan Chen, and Ian Horrocks. 2024. Dual box embeddings for the description logic EL++. In Proceedings of the ACM Web Conference 2024.

2250–2258.

[16] Jieyong Kim, Hyunseo Kim, Hyunjin Cho, SeongKu Kang, Buru Chang, Jinyoung Yeo, and Dongha Lee. 2025. driven Personalized Preference Reasoning with Large Language Models for Recommendation. In Proceedings of the 48th International ACM SIGIR Conference on Research and Development in Information Retrieval. 1697–1706.

[17] Minjin Kim, Minju Kim, Hana Kim, Beong-woo Kwak, Soyeon Chun, Hyunseo Kim, SeongKu Kang, Youngjae Yu, Jinyoung Yeo, and Dongha Lee. 2024. Pearl: A review-driven persona-knowledge grounded conversational recommendation dataset. arXiv preprint arXiv:2403.04460 (2024).

[18] Kirill Kronhardt, Sebastian Hofmann, Fabian Adelt, and Jens Gerken. 2024. Personær-transparency enhancing tool for llm-generated user personas from live website visits. In Proceedings of the International Conference on Mobile and Ubiquitous Multimedia. 527–531.

[19] Jeongeun Lee, Seongku Kang, Won-Yong Shin, Jeongwhan Choi, Noseong Park, and Dongha Lee. 2024. Graph Signal Processing for Cross-Domain Recommendation. arXiv preprint arXiv:2407.12374 (2024)

[20] Jeongeun Lee, Youngjae Yu, and Dongha Lee. 2025. HIPPO-Video: Simulating Watch Histories with Large Language Models for Personalized Video Highlight ing. arXiv preprint arXiv:2507.16873 (2025).

[21] Sangam Lee, Ryang Heo, SeongKu Kang, and Dongha Lee. 2025. Imagine All The Relevance: Scenario-Profiled Indexing with Knowledge Expansion for Dense Retrieval. arXiv preprint arXiv:2503.23033 (2025).

[22] Caiwen Li, Iskandar Ishak, Hamidah Ibrahim, Maslina Zolkepli, Fatimah Sidi, and Caili Li. 2023. Deep learning-based recommendation system: Systematic review and classification. IEEE Access 11 (2023), 113790–113835

[23] Jiacheng Li, Ming Wang, Jin Li, Jinmiao Fu, Xin Shen, Jingbo Shang, and Julian McAuley. 2023. Text is all you need: Learning language representations for sequential recommendation. In Proceedings of the 29th ACM SIGKDD Conference on Knowledge Discovery and Data Mining. 1258–1267.

[24] Qidong Liu, Xiangyu Zhao, Yuhao Wang, Yejing Wang, Zijian Zhang, Yuqi Sun, Xiang Li, Maolin Wang, Pengyue Jia, Chong Chen, et al. 2025. Large Language Model Enhanced Recommender Systems: Methods, Applications and Trends. In Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V. 2. 6096–6106.

[25] Wensheng Lu, Jianxun Lian, Wei Zhang, Guanghua Li, Mingyang Zhou, Hao Liao, and Xing Xie. 2024. Aligning large language models for controllable recommendations. arXiv preprint arXiv:2403.05063 (2024).

[26] Sichun Luo, Bowei He, Haohan Zhao, Wei Shao, Yanlin Qi, Yinya Huang, Aojun Zhou, Yuxuan Yao, Zongpeng Li, Yuanzhang Xiao, et al. 2025. Recranker: Instruction tuning large language model as ranker for top-k recommendation. ACM Transactions on Information Systems 43, 5 (2025), 1–31.

[27] Qiyao Ma, Xubin Ren, and Chao Huang. 2024. Xrec: Large language models for explainable recommendation. arXiv preprint arXiv:2406.02377 (2024).

[28] Xueguang Ma, Xinyu Zhang, Ronak Pradeep, and Jimmy Lin. 2023. Zeroshot listwise document reranking with a large language model. arXiv preprint arXiv:2305.02156 (2023).

[29] Ronak Pradeep, Sahel Sharifymoghaddam, and Jimmy Lin. 2023. Rankvicuna: Zero-shot listwise document reranking with open-source large language models. arXiv preprint arXiv:2309.15088 (2023).

[30] Ronak Pradeep, Sahel Sharifymoghaddam, and Jimmy Lin. 2023. RankZephyr: Efective and Robust Zero-Shot Listwise Reranking is a Breeze! arXiv preprint arXiv:2312.02724 (2023).

[31] Erasmo Purificato, Ludovico Boratto, and Ernesto William De Luca. 2024. User modeling and user profiling: A comprehensive survey. arXiv preprint arXiv:2402.09660 (2024).

[32] Zhen Qin, Rolf Jagerman, Kai Hui, Honglei Zhuang, Junru Wu, Le Yan, Jiaming Shen, Tianqi Liu, Jialu Liu, Donald Metzler, et al. 2023. Large language models are efective text rankers with pairwise ranking prompting. arXiv preprint arXiv:2306.17563 (2023).

[33] Xubin Ren, Wei Wei, Lianghao Xia, Lixin Su, Suqi Cheng, Junfeng Wang, Dawei Yin, and Chao Huang. 2024. Representation learning with large language models for recommendation. In Proceedings of the ACM web conference 2024. 3464–3475.

[34] Stefen Rendle, Christoph Freudenthaler, Zeno Gantner, and Lars Schmidt-Thieme. 2012. BPR: Bayesian personalized ranking from implicit feedback. arXiv preprint arXiv:1205.2618 (2012).

[35] Chao Sun, Yaobo Liang, Yaming Yang, Shilin Xu, Tianmeng Yang, and Yunhai Tong. 2024. Rlrf4rec: Reinforcement learning from recsys feedback for enhanced recommendation reranking. arXiv e-prints (2024), arXiv–2410.

[36] Fei Sun, Jun Liu, Jian Wu, Changhua Pei, Xiao Lin, Wenwu Ou, and Peng Jiang. 2019. BERT4Rec: Sequential recommendation with bidirectional encoder representations from transformer. In Proceedings of the 28th ACM international conference on information and knowledge management. 1441–1450.

[37] Weiwei Sun, Lingyong Yan, Xinyu Ma, Shuaiqiang Wang, Pengjie Ren, Zhumin Chen, Dawei Yin, and Zhaochun Ren. 2023. Is ChatGPT good at search? investigating large language models as re-ranking agents. arXiv preprint arXiv:2304.09542 (2023).

[38] Manveer Singh Tamber, Ronak Pradeep, and Jimmy Lin. 2023. Scaling down, litting up: Eficient zero-shot listwise reranking with seq2seq encoder-decoder models. arXiv preprint arXiv:2312.16098 (2023).

[39] Aaron van den Oord, Yazhe Li, and Oriol Vinyals. 2018. Representation Learning with Contrastive Predictive Coding. arXiv:1807.03748

[40] Lu Wang, Di Zhang, Fangkai Yang, Pu Zhao, Jianfeng Liu, Yuefeng Zhan, Hao Sun, Qingwei Lin, Weiwei Deng, Dongmei Zhang, et al. 2025. LettinGo: Explore User Profile Generation for Recommendation System. In Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V. 2. 2985–2995.

[41] Xiang Wang, Xiangnan He, Meng Wang, Fuli Feng, and Tat-Seng Chua. 2019. Neural graph collaborative filtering. In Proceedings of the 42nd international ACM SIGIR conference on Research and development in Information Retrieval. 165–174.

[42] Triyanna Widiyaningtyas, Indriana Hidayah, and Teguh B Adji. 2021. User pro file correlation-based similarity (UPCSim) algorithm in movie recommendation system. Journal of Big Data 8, 1 (2021), 52.

[43] Stanisław Woźniak, Jacek Duszenko, Jan Kocoń, and Przemysaw Kazienko. 2025. Improving LLM-based recommender systems with user-controllable profiles. In Companion Proceedings of the ACM on Web Conference 2025. 2102–2111.

[44] Jiancan Wu, Xiang Wang, Fuli Feng, Xiangnan He, Liang Chen, Jianxun Lian, and Xing Xie. 2021. Self-supervised graph learning for recommendation. In Proceedings of the 44th international ACM SIGIR conference on research and development in information retrieval. 726–735.

[45] Yunjia Xi, Weiwen Liu, Jianghao Lin, Xiaoling Cai, Hong Zhu, Jieming Zhu, Bo Chen, Ruiming Tang, Weinan Zhang, and Yong Yu. 2024. Towards open-world recommendation with knowledge augmentation from large language models. In Proceedings of the 18th ACM Conference on Recommender Systems. 12–22.

[46] Fan Yang, Zheng Chen, Ziyan Jiang, Eunah Cho, Xiaojiang Huang, and Yanbin Lu. 2023. Palr: Personalization aware llms for recommendation. arXiv preprint arXiv:2305.07622 (2023).

[47] Zhenrui Yue, Sara Rabhi, Gabriel de Souza Pereira Moreira, Dong Wang, and Even Oldridge. 2023. Llamarec: Two-stage recommendation using large language models for ranking. arXiv preprint arXiv:2311.02089 (2023).

[48] Jiarui Zhang. 2024. Guided profile generation improves personalization with llms. arXiv preprint arXiv:2409.13093 (2024).

[49] Shuai Zhang, Lina Yao, Aixin Sun, and Yi Tay. 2019. Deep learning based recommender system: A survey and new perspectives. ACM computing surveys (CSUR) 52, 1 (2019), 1–38.

[50] Yang Zhang, Fuli Feng, Jizhi Zhang, Keqin Bao, Qifan Wang, and Xiangnan He. 2025. Collm: Integrating collaborative embeddings into large language models for recommendation. IEEE Transactions on Knowledge and Data Engineering (2025).

[51] Zijian Zhang, Shuchang Liu, Ziru Liu, Rui Zhong, Qingpeng Cai, Xiangyu Zhao, Chunxu Zhang, Qidong Liu, and Peng Jiang. 2025. Llm-powered user simulator for recommender system. In Proceedings of the AAAI Conference on Artificial Intelligence, Vol. 39. 13339–13347.

[52] Zihuai Zhao, Wenqi Fan, Jiatong Li, Yunqing Liu, Xiaowei Mei, Yiqi Wang, Zhen Wen, Fei Wang, Xiangyu Zhao, Jiliang Tang, et al. 2024. Recommender systems in the era of large language models (llms). IEEE Transactions on Knowledge and Data Engineering 36, 11 (2024), 6889–6907

[53] Kun Zhou, Hui Wang, Wayne Xin Zhao, Yutao Zhu, Sirui Wang, Fuzheng Zhang, Zhongyuan Wang, and Ji-Rong Wen. 2020. S3-rec: Self-supervised learning for sequential recommendation with mutual information maximization. In Proceedings of the 29th ACM international conference on information & knowledge management. 1893–1902.

[54] Shengyao Zhuang, Honglei Zhuang, Bevan Koopman, and Guido Zuccon. 2024. A setwise approach for efective and highly eficient zero-shot ranking with large language models. In Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval. 38–47.

## Breaking User-Centric Agency: A Tri-Party Framework for Agent-Based Recommendation

![](images/bfed4a1ba79d68ec98c42f647de690477ec73ad0899b71ef7cc39ec3fb61dd5e.jpg)

(a) Transition from user-centric to tri-party utility optimization.

User-Centric Optimization

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

## Abstract

Recent advances in large language models (LLMs) have stimulated growing interest in agent-based recommender systems, enabling language-driven interaction and reasoning for more expressive preference modeling. However, most existing agentic approaches remain predominantly user-centric, treating items as passive enti ties and neglecting the interests of other critical stakeholders. This limitation exacerbates exposure concentration and long-tail under representation, threatening long-term system sustainability. In this work, we identify this fundamental limitation and propose the first Tri-party LLM-agent Recommendation framework (TriRec) that explicitly coordinates user utility, item exposure, and platform-level fairness. The framework employs a two-stage architecture: Stage 1 empowers item agents with personalized self-promotion to improve matching quality and alleviate cold-start barriers, while Stage 2 per forms platform-level sequential multi-objective re-ranking, balanc ing user relevance, item utility, and exposure fairness. Experiments show consistent gains in accuracy, fairness, and item-level utility. Moreover, we find that item self-promotion can simultaneously enhance fairness and efectiveness, challenging the conventional trade-of assumption between relevance and fairness. Our code is available at https://github.com/Marfekey/TriRec.

CCS Concepts • Information systems → Recommender systems.

## Keywords

Agent-Based Recommendation, Item Agency, Multi-Stakeholder Recommendation, Item Self-Promotion

## ACM Reference Format:

Yaxin Gong, Chongming Gao, Chenxiao Fan, Haoyan Liu, Wenjie Wang, Jianshan Sun, Yangyang Li, Fuli Feng, and Xiangnan He. 2018. Breaking User-Centric Agency: A Tri-Party Framework for Agent-Based Recommendation. In Proceedings of Make sure to enter the correct conference title from your rights confirmation email (Conference acronym ’XX). ACM, New York, NY, USA, 12 pages. https://doi.org/XXXXXXX.XXXXXXX

Traditional Method: Optimized utility

Our Method: Platform

![](images/ef32915865d75f6faaaab0b37f97e6a01e96888c6c18b1886c26fcdf3d0847db.jpg)

![](images/50865e66dfd7866260e2082e6082926bb56a4a6dc2f9bf79d9ddd849d90fa56d.jpg)

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

## 2 Related Work

## 2.1 LLM-based Agentic Recommendation

The remarkable reasoning capabilities of LLMs have fundamentally reshaped intelligent decision-making, stimulating a surge of interest in LLM-based agent paradigms within recommender systems [13, 28]. Unlike traditional filtering, these agents model complex behaviors through language-driven reasoning, enabling more expressive preference representations [44, 48].

Within this research frontier, a prominent direction utilizes agents as high-fidelity surrogates to simulate human behavior [3, 47]. Frameworks like Agent4Rec [42] and DyTA4Rec [33] incorporate sociological traits and dynamic profile updates to capture user interest evolution. To ensure long-term sustainability, the PUMA framework [50] enables eficient migration of personalized prompt assets across evolving model architectures. Beyond simulation, agents function as intelligent interfaces to improve decision quality through deliberate reasoning [16, 31, 39]. Methods such as STARec [34] and ReasonRec [45] incorporate reasoning mechanisms to mitigate hallucinations and enhance robustness, while LatentR3 [46] further optimizes eficiency by utilizing reinforced latent tokens instead of explicit text generation.

Meanwhile, decentralized multi-agent architectures decompose complex tasks into specialized roles or model bidirectional dynamics [21, 32, 41]. Frameworks like AgentCF [44] and Rec4Agentverse [43] introduce item agents to interact autonomously with user agents for preference refinement. To address the long-term impact of these interactions, the bi-learning planner [24] coordinates macro-level guidance for sustained engagement. However, existing multi-agent paradigms primarily focus on maximizing one-sided user utility while neglecting the interests of the items. In this work, we propose a novel framework that explicitly models item agents and equips them with the ability to advocate for their own visibility, while maintaining alignment with user preferences.

## 2.2 Creator-side Recommendation

User-centric recommendation often causes most exposure to go to a few popular items, leaving many creators and their content invisible. This lack of visibility hinders the creator experience, ultimately leading to a decline in content production and platform engage ment [6, 7]. Early methodologies primarily utilized co-learning frameworks to synchronize user and provider representations [6], or developed specific mechanisms like PRINCE [14] to provide counterfactual interpretability for the provider side.

Recently, researchers have explored "mirroring" user-centric techniques, with models such as DualRec [7] treating items as active queries to identify suitable users and tackle the user availability challenge in dual-target optimization. Concurrently, generative approaches such as HLLM-Creator [5] have begun leveraging LLMs to produce personalized creative content, thereby enhancing item appeal through automated content augmentation. FlyThinker [26] further advances this by enabling reasoning and generation to proceed concurrently, allowing for the dynamic guidance of long-form per sonalized responses. However, these frameworks still view creators as passive targets for algorithmic optimization or static subjects of content generation, lacking explicit modeling of autonomous agency. Diferent from these passive approaches, our work empow ers creators with agentic capabilities, enabling tailored promotion of their content to users.

## 2.3 Platform Fair Ranking

The pervasive Matthew efect in recommendation leads to exposure concentration, leaving vast long-tail products invisible and causing cold-start problems [25, 37]. Consequently, platforms must implement systematic interventions to reconcile the trade-of between accuracy and multi-stakeholder fairness [35]. Classical research ad dresses this by formulating exposure allocation as a constrained op timization problem [23, 25] or by learning debiased representations [22, 35] to neutralize provider-side biases. Beyond static debiasing, SPRec [10] introduces self-play mechanisms to iteratively mitigate filter bubbles and improve fairness without additional data.

Another dominant paradigm utilizes post-hoc re-ranking to achieve equitable resource distribution via social welfare criteria. To account for temporal dynamics, models like LTP-MMF [38] intro duce mechanisms to mitigate the deleterious feedback loop efect. Similarly, the bi-learning planner [24] utilizes LLMs to manage macro-level guidance for optimizing long-term user engagement. Recently, multi-agent social choice frameworks, such as SCRUF-D [1], introduce agents to arbitrate conflicting fairness criteria. While these methods move toward decentralized decision-making, they struggle to perceive fine-grained item-level signals. In this work, we formulate platform regulation as a re-ranking problem that enables adaptive coordination of relevance, fairness, and item exposure utility.

## 3 Problem Formulation

We formally model the recommendation problem addressed by TriRec from a multi-stakeholder and agentic perspective. Unlike conventional settings that optimize user relevance alone, our framework explicitly accounts for the potentially conflicting objectives of users, items, and the platform, and introduces the agent-based preference interaction mechanism underlying Stage 1 candidate construction.

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

## 3.2 Agent-based Preference Interaction

Following AgentCF [44], we adopt an agent-based recommendation paradigm to model fine-grained user–item preference alignment.

AgentCF-style interaction training is used to construct and refine preference representations for both users and items. Through ofline replay of historical user–item interaction episodes, user agents gradually accumulate preference memory, while item agents build item-side semantic memory that captures their appeal patterns across diferent user groups. These interaction-induced preference states are stored in internal memory modules and serve as the foundation for downstream inference.

Formally, let U denote the set of user agents and I denote the set of item agents. Each user agent $u \in \mathcal { U }$ maintains a preference memory $\mathcal { M } _ { u }$ , which is summarized into a user interest representation $\mathbf { z } _ { u } .$ . Each item agent $i \in \mathcal { I }$ maintains an item-side memory $M _ { i }$ together with structured item metadata representation $\mathbf { x } _ { i }$

Given a user agent <sup>??</sup> and a candidate item set $C _ { u } = \{ c _ { 1 } , . . . , c _ { n } \}$ the goal of Stage 1 is to generate a relevance-oriented ranking list by modeling semantic interactions between agents.

The user agent evaluates candidate items based on their gen erated semantic descriptions and its preference memory to form ranking decisions. This interaction process is implemented through a fixed LLM-based inference function:

$$
\mathcal {Y} _ {u} ^ {(1)} = f _ {\mathrm{LLM}} (u, \mathcal {C} _ {u}),\tag{3}
$$

where $f _ { \mathrm { L L M } } ( \cdot )$ denotes the agent interaction module that outputs an ordered list $y _ { u } ^ { ( 1 ) }$ via multi-round semantic reasoning.

Consistent with AgentCF, we keep the underlying LLM parameters frozen during both memory construction and inference. The ranking behavior is therefore governed by structured interaction protocols and contextual reasoning over agent memory states, rather than gradient-based parameter updates.

In our framework, we further extend this interaction layer by enabling item agents to actively generate user-conditioned selfpromotion, which will be formally described in the following section.

## 4 Method

Figure 2 provides an overview of the proposed TriRec framework. The framework is composed of two sequential modules: a user–item interaction module for generative personalized self-promotion and a platform control module for exposure-aware re-ranking. Both modules operate entirely at inference time with frozen LLM pa rameters, building upon the agent memory constructed during the preference interaction phase described in §3.2. We next describe the design and implementation details of each component.

![](images/5e8fbe50904eaaae707a4c876bc9e5dc4b4a7efd43affd4331f16dc25b267538.jpg)  
Figure 2: Overview of the proposed two-stage TriRec framework, where Stage 1 performs relevance-aware re-ranking via user–item interaction, and Stage 2 conducts exposureaware re-ranking through tri-party utility optimization.

## 4.1 Generative Personalized Self-Promotion

As shown in the left part of Figure 2, Stage 1 models both item agents and user agents, and leverages LLMs to drive their interest expression and interaction behaviors.

Unlike conventional approaches that model items as static feature vectors, we endow item agents with proactive expressive capability. Given a target user $u \in \mathcal { U } ,$ the item agent generates a personalized self-promotion as follows:

$$
S _ {i \rightarrow u} = \mathcal {G} _ {\theta} (\mathbf {x} _ {i}, \mathbf {z} _ {u}, \mathcal {M} _ {i}),
$$

where $\mathcal { G } _ { \theta }$ denotes a frozen pre-trained LLM with fixed parameters $\theta ,$ x?? represents item metadata, $\mathbf { z } _ { u }$ denotes the user interest representation, and $\mathcal { M } _ { i }$ is the memory state of the item agent.

Importantly, the item metadata $\mathbf { x } _ { i }$ used as input consists solely of static attributes $( \mathrm { e . g . }$ , title, category, and descriptive features) and does not contain any test interaction signals, ensuring no information leakage. Furthermore, the generation prompt explicitly instructs the LLM to ground its output in the provided metadata, preventing fabrication of nonexistent item properties.

This mechanism allows items with very limited historical interactions to actively convey their potential value through high-quality semantic descriptions, thereby alleviating the cold-start problem.

Instead of relying on an explicit parametric scoring function, the user agent performs semantic preference reasoning over item selfpresentations generated by item agents. Formally, given a candidate item set $C _ { u }$ and their corresponding self-promotions $\{ S _ { i \to u } \} _ { i \in C _ { u } }$ the user agent produces a relevance-oriented ranking by

$$
\mathcal {Y} _ {u} ^ {(1)} = \mathrm{argsort} _ {i \in C _ {u}} \mathcal {F} _ {\phi} (\mathbf {z} _ {u}, S _ {i \to u}),\tag{4}
$$

where $\mathcal { F } _ { \phi } ( \cdot )$ denotes the LLM-based semantic preference evaluator with fixed parameters $\phi .$

This formulation enables the user agent to jointly consider personalized interest representations and item-side expressive content, allowing preference judgments to be conditioned on both intrinsic user tastes and context-aware item descriptions. This decision process forms a state-aware perception–decision–action loop, where the user agent perceives item-side semantic signals, updates preference judgments conditioned on its internal state, and outputs relevance-driven ranking actions.

In practice, since each item agent generates its self-promotion independently conditioned on the target user, all candidates in $C _ { u }$ can be processed via concurrent API calls, making the wall-clock latency largely independent of the candidate set size.

This agent-based interaction stage is intentionally restricted to relevance-oriented preference alignment. No exposure modulation or fairness constraints are injected at this stage, ensuring that the produced ranking reflects high-quality semantic matching. This separation allows the subsequent platform re-ranker to perform exposure-aware regulation on top of a stable relevance backbone.

## 4.2 Platform-Led Multi-Objective Re-Ranking

Although Stage 1 produces relevance-oriented rankings via agent interaction, it does not explicitly regulate long-term exposure allo cation across items. We therefore introduce a platform re-ranking module ${ \mathcal { A } } _ { p }$ that performs state-aware sequential re-ranking to balance user utility, item utility, and platform-level fairness.

We model the platform module as a sequential decision process operating on a dynamic system state.

Exposure as a Control State. In real-world recommendation systems, the platform cannot directly control user feedback such as clicks or purchases, but can explicitly regulate item visibility through ranking positions and display frequency. Therefore, we adopt exposure as the core system state to characterize the cumu lative visibility of each item across sequential recommendation rounds.

Moreover, exposure exhibits strong temporal dependency and accumulation efects, which can lead to long-term popularity bias if left uncontrolled. Modeling exposure as a dynamic state variable allows the platform to explicitly track historical allocation and perform state-aware re-ranking decisions that balance immediate utility and long-term fairness.

State Representation. At time step <sup>??</sup>, when user $u _ { t }$ arrives, the platform observes the current system state:

$$
\mathbf {s} _ {t} = \{\mathbf {e} ^ {t}, \mathcal {Y} _ {u _ {t}} ^ {(1)} \},\tag{5}
$$

where $\mathbf { e } ^ { t } = [ e _ { i } ^ { t } ] _ { i \in J }$ denotes the historical exposure vector of all candidate items $\tau _ { \ast }$ and $y _ { u _ { t } } ^ { ( 1 ) }$ is the relevance-oriented ranking list generated by the Stage 1 agent interaction module.

Action Space. Given the observed state $\mathbf { s } _ { t } ,$ , the platform selects an action by re-ranking the Stage 1 list:

$$
\mathcal {Y} _ {u _ {t}} ^ {(2)} = \mathcal {A} _ {p} (\mathbf {s} _ {t}),\tag{6}
$$

where $y _ { u _ { t } } ^ { ( 2 ) }$ denotes the final recommendation list served to user $u _ { t } .$

State Transition. Given the platform re-ranking action $y _ { u _ { t } } ^ { ( 2 ) } =$ $\left[ i _ { 1 } , i _ { 2 } , \ldots , i _ { K } \right]$ , the exposure state is updated based on position dependent visibility gain:

$$
e _ {i} ^ {t + 1} = \left\{ \begin{array}{l l} e _ {i} ^ {t} + v (k), & \text {if i = i_{k} \in \mathcal {Y} _{u_{t}} ^{(2)}}, \\ e _ {i} ^ {t}, & \text {otherwise,} \end{array} \right.\tag{7}
$$

where $k = \mathrm { r a n k } _ { y _ { u t } ^ { \left( 2 \right) } } \left( i \right)$ denotes the 1-based display position of item <sup>??</sup> in the ranked list, and $v ( \cdot )$ denotes a monotonically decaying exposure function.

In our implementation, we adopt logarithmic decay:

$$
v (k) = \frac {1}{\log_ {2} (k + 2)},\tag{8}
$$

so that items placed at higher ranks receive larger exposure increments, reflecting the well-established position bias phenomenon [17] that higher-ranked items attract more user attention and interaction opportunities.

Note that $v ( \cdot )$ serves a dual role in our framework: it defines both the exposure state transition $( \mathrm { E q . ~ } 7 )$ and the position-dependent weight $\omega _ { k }$ used in the participation policy (Eq. 14). We compare alternative decay profiles in §5.3.

This formulation assumes that only displayed items receive exposure gain, while non-displayed items retain their historical exposure levels, and allows the platform to explicitly regulate exposure allocation through re-ranking.

Platform Optimization Objective. Over a sequence of user arrivals, the platform aims to maximize long-term multi-stakeholder utility by coordinating user relevance, item utility, and platformlevel fairness.

We decompose the objective into a per-item joint utility function $U _ { \mathrm { j o i n t } } ( u _ { t } , i , k , \mathbf { e } ^ { t } )$ , which measures the marginal contribution of placing item <sup>??</sup> at position <sup>??</sup> for user $u _ { t }$ under exposure state $\mathbf { e } ^ { t } .$

Formally, given a time horizon $T ,$ the objective is defined as:

$$
\max _ {\{\mathcal {Y} _ {u _ {t}} ^ {(2)} \} _ {t = 1} ^ {T}} \frac {1}{T} \sum_ {t = 1} ^ {T} \sum_ {k = 1} ^ {| \mathcal {Y} _ {u _ {t}} ^ {(2)} |} U _ {\mathrm{joint}} (u _ {t}, i, k, \mathbf {e} ^ {t}),\tag{9}
$$

where $y _ { u _ { t } } ^ { ( 2 ) }$ denotes the platform re-ranked list served to user $u _ { t }$ at time step <sup>??</sup> .

4.2.1 State-Aware Joint Utility Scoring. Since directly optimizing the induced listwise objective is intractable—the combinatorial search space grows as $O ( | C | ! / ( | C | - K ) ! )$ for a candidate set of size |C | and list length $K ,$ making exact enumeration computationally prohibitive—we approximate it using a position-aware marginal joint utility function.

Specifically, we define the position-conditioned joint utility as:

$$
U _ {\mathrm{joint}} (u _ {t}, i, k, \mathbf {e} ^ {t}) = g (u _ {t}, i, k, \mathbf {e} ^ {t}) \cdot U _ {\mathrm{expo-item}} (u _ {t}, i, k),\tag{10}
$$

where $g ( u _ { t } , i , k , \mathbf { e } ^ { t } )$ captures the immediate relevance–fairness trade of at ranking position $k ,$ and $U _ { \mathrm { e x p o - i t e m } } ( u _ { t } , i , k )$ denotes the exposureaware item utility modulator that incorporates long-term visibility regulation.

Relevance–Fairness Gain Function. We compute relevance– fairness gain by combining normalized user and platform utility signals through a position-aware convex weighting scheme:

$$
g (u _ {t}, i, k, \mathbf {e} ^ {t}) = \alpha_ {k} \cdot \tilde {U} _ {\mathrm{user}} (u _ {t}, i) + (1 - \alpha_ {k}) \cdot \tilde {U} _ {\mathrm{platform}} (i, \mathbf {e} ^ {t}),\tag{11}
$$

where $\alpha _ { k } \in [ 0 ,$ 1] controls the relative participation of platformlevel regulation at rank position $k ,$ and $\tilde { U } _ { \mathrm { u s e r } }$ and $\tilde { U } _ { \mathrm { p l a t f o r m } }$ denote the normalized versions of the corresponding utility signals, rescaled to the same range for stable convex combination.

For numerical stability and scale consistency, all heterogeneous utility signals are normalized within the candidate set at each time step. We use $\tilde { U } _ { ( \cdot ) }$ to denote the normalized versions of the corresponding raw utility signals.

User Utility Modeling. The user-side utility is computed via a multiplicative interaction mechanism that combines semantic reasoning and embedding-level relevance:

$$
U _ {\mathrm{user}} (u _ {t}, i) = r _ {\mathrm{LLM}} (u _ {t}, i),\tag{12}
$$

where $r _ { \mathrm { L L M } } ( u _ { t } , i )$ denotes the preference intensity predicted by the user agent through multi-round semantic reasoning. The resulting scores are normalized across the candidate set to obtain $\tilde { U } _ { \mathrm { u s e r } }$

Platform Utility Modeling. The platform utility term aggregates normalized marginal fairness gains:

$$
\tilde {U} _ {\mathrm{platform}} (i, \mathbf {e} ^ {t}) = \lambda_ {1} \cdot \tilde {U} _ {\mathrm{DGU}} (i, \mathbf {e} ^ {t}) + \lambda_ {2} \cdot \tilde {U} _ {\mathrm{MGU}} (i, \mathbf {e} ^ {t}),\tag{13}
$$

where $\tilde { U } _ { \mathrm { D G U } }$ and $\tilde { U } _ { \mathrm { M G U } }$ denote normalized marginal improvements on Distributional Group Unfairness and Maximal Group Unfairness, respectively. Specifically, for each candidate item <sup>??</sup>, we compute the marginal fairness gain by simulating its placement at the current position: the exposure distribution is tentatively updated as ${ \mathbf { e } } ^ { t ^ { \prime } } =$ $\mathbf e ^ { t } + v ( k ) \cdot \mathbf 1 _ { i }$ , and the resulting reduction in DGU (or MGU) relative to the current state is taken as the marginal improvement, $\mathrm { i . e . }$ $U _ { \mathrm { D G U } } ( i , { \bf e } ^ { t } ) \ = \ \mathrm { D G U } ( { \bf e } ^ { t } ) \ - \ \mathrm { D G U } ( { \bf e } ^ { t ^ { \prime } } )$ . The coeficients $\lambda _ { 1 }$ and $\lambda _ { 2 }$ control the relative importance of the two fairness objectives.

Position-Aware Participation Policy. To regulate the intervention strength along the ranked list, we design a monotonic position-dependent policy:

$$
\alpha_ {k} = \alpha_ {\mathrm{min}} + (\alpha_ {\mathrm{max}} - \alpha_ {\mathrm{min}}) \cdot (\omega_ {k}) ^ {p},\tag{14}
$$

where $\boldsymbol { p }$ controls the decay curvature, $\alpha _ { \mathrm { { m i n } } }$ and $\alpha _ { \mathrm { m a x } }$ define the lower and upper bounds, and $\omega _ { k } \in [ 0 , 1 ]$ is a position-dependent weight derived from the same exposure decay profile <sup>??</sup> (·) used in the state transition function Eq. 8, with larger values corresponding to higher-ranked positions.

This design prioritizes user relevance at top-ranked positions while gradually injecting platform-level regulation toward lower ranks, enabling a controllable relevance–fairness trade-of.

Exposure-Aware Item Utility. Given that the ranking position is explicitly determined during sequential construction, we rewrite item-side utility defined in Eq. 2 as:

$$
U _ {\mathrm{item}} (u _ {t}, i, k) = v (k) \cdot \mathrm{CTR} (u _ {t}, i),\tag{15}
$$

where <sup>??</sup> (<sup>??</sup>) models position-dependent exposure probability and $\mathrm { C T R } ( u _ { t } , i )$ denotes the predicted click-through probability:

$$
\operatorname{CTR} (u _ {t}, i) = \sigma \left(\operatorname{sim} _ {\text { emb }} \left(\mathbf {z} _ {u _ {t}}, \mathbf {h} _ {i}\right)\right),\tag{16}
$$

where $\sigma ( \cdot )$ is the sigmoid function, $\mathrm { s i m } _ { \mathrm { e m b } } ( \cdot )$ represents cosine similarity between the user interest embedding $\mathbf { z } _ { u _ { t } }$ and the item semantic embedding h??.

To incorporate long-term exposure regulation, we define the exposure-aware item utility as

$$
U _ {\mathrm{expo-item}} (u _ {t}, i, k) = \left(\tilde {U} _ {\mathrm{item}} (u _ {t}, i, k)\right) ^ {\lambda_ {\mathrm{item}}},\tag{17}
$$

where $\tilde { U } _ { \mathrm { i t e m } }$ denotes item utility within the candidate set at each ranking step, and $\lambda _ { \mathrm { i t e m } }$ controls the sensitivity of the platform reranking to item-side exposure utility.

This formulation allows the platform to amplify under-exposed items with high potential value while suppressing over-saturated content, thereby mitigating long-term exposure concentration.

4.2.2 Greedy Sequential Action Generation. In implementation, Eq. 9 is approximated via greedy list construction performed independently for each incoming user request, while the exposure state $\mathbf { e } ^ { t }$ is carried over across recommendation rounds, efectively realizing a one-step approximation of the long-term control objective. We note that this myopic approximation does not guarantee globally optimal long-term behavior; however, carrying persistent exposure state across rounds provides implicit temporal coordination that empirically yields strong multi-stakeholder performance (see §5).

Due to the position-dependent nature of $U _ { \mathrm { j o i n t } } ( u _ { t } , i , k , \mathbf { e } ^ { t } )$ , the final ranking list is constructed in a top-down manner, where items are greedily selected and fixed from higher-ranked positions to lower-ranked ones.

Specifically, at ranking position <sup>??</sup>, the platform re-ranker selects:

$$
i _ {k} ^ {*} = \arg \max _ {i \in C _ {u _ {t}} \backslash \mathcal {Y} _ {<   k}} U _ {\mathrm{joint}} (u _ {t}, i, k, \mathbf {e} ^ {t}),\tag{18}
$$

where $y _ { < k } = \{ i _ { 1 } ^ { * } , \ldots , i _ { k - 1 } ^ { * } \}$ denotes the prefix list containing the previously selected top-<sup>??</sup> − 1 items.

This sequential construction explicitly accounts for positionaware utility modulation and enables eficient approximation of the underlying listwise optimization objective. This greedy sequential construction thus serves as the concrete policy implementation of the platform re-ranking module, mapping observed states to ranking actions under the defined utility objective.

Although greedy construction is not globally optimal, it is widely adopted in practical re-ranking systems due to its eficiency and strong empirical performance. Notably, this re-ranking step involves only closed-form arithmetic operations over the candidate set, making it computationally negligible.

4.2.3 Platform Re-Ranking as a Closed-Loop Decision Process. Finally, we explicitly formulate the platform module as a sequential control process:

$$
\mathcal {A} _ {p} = \langle \mathcal {S}, \mathcal {A}, \mathcal {T} \rangle ,\tag{19}
$$

where the state space $s$ consists of the historical exposure vector $\mathbf { e } ^ { t }$ and the Stage 1 relevance ranking $y _ { u _ { t } } ^ { ( 1 ) }$ ; the action space A corresponds to the re-ranking decision $y _ { u _ { t } } ^ { ( 2 ) }$ ; and the transition function $\mathcal { T }$ is defined by the exposure update rule in $\operatorname { E q . 7 }$

This formulation enables the platform to perform adaptive, stateaware re-ranking that dynamically balances user relevance, item exposure opportunity, and platform-level fairness over sequential recommendation rounds.

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

## 5.3 Ablation Study (RQ2)

Table 3 summarizes ablation results on CDs & Vinyl. We group variants into three categories.

Table 4: Impact of diferent position decay functions on recommendation performance.

<table><tr><td rowspan="2">Decay Function</td><td colspan="5">CDs &amp; Vinyl</td><td colspan="5">Movies &amp; TV</td><td colspan="5">Goodreads YA</td><td colspan="5">Steam Games</td></tr><tr><td>NDCG↑</td><td>MRR↑</td><td>DGU↓</td><td>MGU↓</td><td>EIU↑</td><td>NDCG↑</td><td>MRR↑</td><td>DGU↓</td><td>MGU↓</td><td>EIU↑</td><td>NDCG↑</td><td>MRR↑</td><td>DGU↓</td><td>MGU↓</td><td>EIU↑</td><td>NDCG↑</td><td>MRR↑</td><td>DGU↓</td><td>MGU↓</td><td>EIU↑</td></tr><tr><td>Power-law  $\frac{1}{(k+1)^q}$ </td><td>0.4911</td><td>0.4690</td><td>0.1601</td><td>0.1474</td><td>0.5913</td><td>0.4606</td><td>0.4419</td><td>0.2354</td><td>0.1776</td><td>0.5688</td><td>0.5505</td><td>0.5452</td><td>0.5152</td><td>0.4805</td><td>0.6467</td><td>0.4537</td><td>0.4510</td><td>0.4060</td><td>0.3967</td><td>0.5746</td></tr><tr><td>Exponential  $e^{-k\lambda}$ </td><td>0.4900</td><td>0.4683</td><td>0.1604</td><td>0.1478</td><td>0.5907</td><td>0.4612</td><td>0.4425</td><td>0.2358</td><td>0.1779</td><td>0.5692</td><td>0.5503</td><td>0.5451</td><td>0.5151</td><td>0.4802</td><td>0.6466</td><td>0.4534</td><td>0.4492</td><td>0.4076</td><td>0.3966</td><td>0.5733</td></tr><tr><td>Linear  $1 - \frac{k}{K}$ </td><td>0.4961</td><td>0.4703</td><td>0.1617</td><td>0.1478</td><td>0.5926</td><td>0.4605</td><td>0.4421</td><td>0.2363</td><td>0.1781</td><td>0.5689</td><td>0.5498</td><td>0.5448</td><td>0.5152</td><td>0.4806</td><td>0.6463</td><td>0.4532</td><td>0.4506</td><td>0.4060</td><td>0.3975</td><td>0.5742</td></tr><tr><td>Log  $\frac{1}{\log_2(k+2)}$ </td><td>0.4951</td><td>0.4702</td><td>0.1596</td><td>0.1468</td><td>0.5925</td><td>0.4630</td><td>0.4451</td><td>0.2258</td><td>0.1768</td><td>0.5709</td><td>0.5503</td><td>0.5450</td><td>0.5150</td><td>0.4803</td><td>0.6465</td><td>0.4546</td><td>0.4512</td><td>0.4054</td><td>0.3970</td><td>0.5748</td></tr></table>

Table 5: TriRec with diferent LLM backbones.

<table><tr><td>Backbone</td><td>NDCG↑</td><td>MRR↑</td><td>DGU↓</td><td>MGU↓</td><td>EIU↑</td></tr><tr><td>GPT-3.5-Turbo</td><td>0.4964</td><td>0.4718</td><td>0.1568</td><td>0.1478</td><td>0.5937</td></tr><tr><td>GPT-4o-mini</td><td>0.4951</td><td>0.4702</td><td>0.1596</td><td>0.1468</td><td>0.5925</td></tr><tr><td>GPT-4o</td><td>0.5234</td><td>0.4901</td><td>0.1647</td><td>0.1481</td><td>0.6086</td></tr><tr><td>DeepSeek-V3</td><td>0.5075</td><td>0.4770</td><td>0.1635</td><td>0.1526</td><td>0.5986</td></tr><tr><td>Qwen-plus</td><td>0.4891</td><td>0.4621</td><td>0.1604</td><td>0.1521</td><td>0.5864</td></tr></table>

5.3.1 Stage-Wise Component Analysis. Removing Stage 1 (row (a)) causes NDCG to drop by 31.7%, confirming that LLM-driven seman tic interaction is indispensable for fine-grained preference align ment. Comparing rows (b) and (c) isolates the contribution of item self-promotion: it yields a 10.4-point NDCG gain while simulta neously improving fairness (DGU: 0.170→0.166), demonstrating that active item expression benefits both relevance and exposure balance. Removing Stage 2 alone (row (c)) preserves competitive accuracy but degrades fairness (DGU: 0.170) and item utility (EIU: 0.582), confirming the necessity of platform-level regulation.

5.3.2 Platform-Level Component Analysis. Removing <sup>??</sup><sub>platform</sub> (row (d)) maintains accuracy but limits fairness gains. Replacing dynamic <sup>??</sup>?? with a fixed policy (row (e)) causes NDCG to drop from 0.495 to 0.464 while aggressively over-optimizing fairness, indicating that static intervention at top positions harms user experience. Removing $U _ { \mathrm { u s e r } }$ (row (f)) leads to the most severe accuracy degradation (NDCG: 0.263), revealing that the platform re-ranker over-prioritizes fairness without explicit user relevance protection. Removing $U _ { \mathrm { i t e m } }$ (row (g)) degrades both accuracy and EIU, confirming positive coupling between item utility modeling and user satisfaction.

5.3.3 Representation Quality Analysis. Without semantic embed dings (row (h)) or with random replacements (row (i)), both accuracy and EIU degrade progressively (NDCG: 0.478→0.463), confirming that meaningful embedding signals provide essential grounding for platform-level decision-making.

5.3.4 Efect of Position Decay Function <sup>??</sup> (·). We compare four monotonic decay functions: Log 1/log (<sup>??</sup>+2) (default), Power-law $1 / ( k { + } 1 ) ^ { q }$ , Exponential $e ^ { - k \lambda }$ , and Linear $1 { - } k / K ,$ , with <sup>??</sup>=1, <sup>??</sup>=0<sup>.</sup>5, <sup>??</sup>=10. As shown in Table 4, performance diferences are marginal across all four datasets (within 1%), indicating robustness to the specific decay form. Log decay achieves the most consistent fairness advantage and is adopted as the default.

5.3.5 Efect of LLM Backbone. Table 5 reports TriRec with five LLM backbones on CDs & Vinyl. All variants yield closely matched NDCG and EIU, indicating the gains stem from the tri-party design rather than a specific LLM. GPT-3.5-Turbo already attains comparable accuracy with the best fairness, while GPT-4o achieves the highest relevance at only marginal fairness cost. The inclusion of DeepSeek-V3 and Qwen further validates cross-family generalizability.

![](images/d53919e5e0a0e202c4765c4fb7b479a6c09dd99d0e502f22f0b6c5b046687268.jpg)  
Figure 4: Performance with varying $\lambda _ { \mathrm { i t e m } }$ on the CDs dataset.

![](images/3e2c630f6ee92082996bb4fbeadc6ae4513c56e1b7f984943858011c85dd0820.jpg)  
Figure 5: Sensitivity of $\alpha _ { \mathrm { m a x } } , p , \lambda _ { 1 } ,$ and $\lambda _ { 2 }$ on the CDs dataset.

5.3.6 Eficiency. Following [27], we use the average LLM tokens per user request as a hardware-agnostic latency proxy. On CDs & Vinyl, TriRec consumes 98.4 tokens/user, comparable to MACRec (114.3) and well below Rec4AgentVerse (143.7); AgentCF++ uses only 41.8 tokens but with substantially weaker accuracy and item utility. Since Stage 1 self-promotions are generated concurrently and Stage 2 reduces to closed-form arithmetic, TriRec’s wall-clock latency remains largely independent of $| C _ { u } |$

![](images/8b9870dc89fd0baa424595dade18e8605b0a49cf6b1b38679e8dfbbdfb40fb9a.jpg)  
Figure 6: Case Study: Personalized Re-ranking for a Cold-start Item. The target item (ID: B004X1M4DS) had zero exposure in the training set and was initially ranked 10th. Our agent framework successfully re-ranked the cold-start item to the top position by leveraging semantic alignment.

## 5.4 Analysis of Key Factors (RQ3)

We conduct sensitivity analysis on CDs & Vinyl, examining $\lambda _ { \mathrm { i t e m } }$ as the primary factor, followed by $\alpha _ { \mathrm { m a x } } , p , \lambda _ { 1 }$ , and $\lambda _ { 2 }$ .

5.4.1 Efect $o f \lambda _ { i t e m } .$ Figure 4 reports performance as $\lambda _ { \mathrm { i t e m } }$ varies from 0 to 100. When $\lambda _ { \mathrm { i t e m } } = 0 ;$ , the exposure-aware modulator de grades to a constant $( U _ { \mathrm { e x p o - i t e m } } \equiv 1 )$ , yielding the worst performance across all three stakeholder metrics, confirming that item utility modeling is essential.

$\mathtt { A s } \lambda _ { \mathrm { i t e m } }$ increases to the range of 5–10, all three metrics improve concurrently: NDCG rises to 0.499 (+6.6%), DGU decreases to 0.159, and EIU increases to 0.595. This challenges the conventional assumption that stakeholder objectives are inherently conflicting, and demonstrates that the exposure-aware modulator surfaces high potential under-exposed items that simultaneously benefit users, items, and platform fairness.

Beyond $\lambda _ { \mathrm { i t e m } } = 2 0 $ , performance plateaus as excessive amplifica tion causes over-reliance on embedding signals. The cumulative EIU remains constant (≈4.533), indicating that $\lambda _ { \mathrm { i t e m } }$ controls expo sure redistribution rather than total volume. We set $\lambda _ { \mathrm { i t e m } } = 1 0$ as the default.

5.4.2 Efect of Other Hyperparameters. Figure 5 reports sensitivity of the remaining parameters.

(a) $\alpha _ { \mathrm { m a x } }$ controls positional diferentiation. Increasing $\alpha _ { \mathrm { m a x } }$ from 0.1 to 1.0 improves accuracy (NDCG: 0.434→0.495) while degrading fairness (DGU: 0.105→0.159), as top positions increasingly preserve Stage 1 relevance ordering. Even at $\alpha _ { \mathrm { m a x } } = 1 . 0$ , lower ranks retain $\alpha _ { k } \approx 0 . 1$ , so regulation is concentrated at lower positions rather than fully disabled. We set $\alpha _ { \mathrm { m a x } } = 1 . 0$ , as the sparse exposure history on this dataset makes aggressive top-position fairness injection counterproductive.

(b) <sup>??</sup> governs how rapidly $\alpha _ { k }$ decays from $\alpha _ { \mathrm { m a x } }$ to $\alpha _ { \mathrm { { m i n } } }$ along the ranked list. As <sup>??</sup> increases, fairness improves (DGU: 0.159→0.140) at the cost of accuracy (NDCG: 0.495→0.482). Beyond $p = 1 . 0$ , accuracy degradation accelerates while fairness gains remain marginal, making larger <sup>??</sup> increasingly cost-ineficient. Values below 1.0 ofer the most favorable accuracy-fairness ratio.

(c–d) $\lambda _ { 1 }$ and $\lambda _ { 2 }$ exhibit high robustness: varying either from 0 to 1 improves the corresponding fairness metric while causing less than 0.3% NDCG loss, confirming strong compatibility between fairness signals and user relevance.

## 5.5 Cold-Start Item Promotion (RQ4)

To examine the efectiveness of item self-promotion under cold-start conditions, we conduct a case study on a representative product from CDs & Vinyl. The target item (ID: B004X1M4DS) has zero exposure in the training set and is initially placed at rank 10 in the candidate list, as shown in Figure 6.

5.5.1 Item Self-Promotion. For the cold-start target item, the Item Agent generates a personalized pitch that precisely anchors on the user’s core preferences: it highlights “original cast recording” and “Broadway” (genre alignment), emphasizes “rich audio quality” (production preference), and conveys “vibrant energy” (stylistic resonance). In contrast, competing candidates such as Dance Classics Best of 3 attempt preference mapping but exhibit semantic drift—its dance music essence fundamentally diverges from the user’s interest in musical theater. This demonstrates that self-promotion seeks genuine semantic intersections rather than superficial keyword aggregation: strong intersections produce persuasive pitches, while weak ones cannot conceal the underlying mismatch.

Importantly, the self-promotion is conditioned on the item’s original metadata (title, category, and attributes) provided as input context, which constrains the generation to factual item properties. As evidenced by the contrasting cases above, items whose metadata lacks genuine alignment with the user profile fail to produce com pelling pitches despite the LLM’s generative capacity—precisely because the mechanism cannot fabricate nonexistent item features.

5.5.2 User-Agent Re-Ranking. The User Agent assigns the target item the highest score (9.5 out of 10), promoting it from rank 10 to rank 1, while demoting initially higher-ranked but less compatible items. The agent’s reasoning reveals hierarchical preference priori tization: genre alignment receives the highest weight, followed by audio quality, with peripheral relevance scored lowest.

This case demonstrates that the dual-agent interaction mecha nism enables cold-start items to compete with established products through semantic self-promotion alone, efectively breaking the “no exposure → no feedback → no recommendation” cycle without requiring any collaborative filtering signals.

## 6 Conclusion and Limitations

We proposed TriRec, the first tri-party LLM-agent recommendation framework that coordinates users, items, and the platform via item self-promotion and platform-led multi-objective re-ranking. Exper iments validate the superiority of TriRec over existing baselines in enhancing tri-party utilities, suggesting that item self-promotion can mitigate the conventional relevance–fairness trade-of.

Two limitations remain: our ofline protocol may not fully reflect long-term dynamics, and the generated self-promotion is not yet quantitatively audited for factuality. Future work will address these via multi-round simulation, online A/B tests, and retrieval-grounded factuality constraints, as well as safeguards against adversarial self promotion and provider gaming.

## References

[1] Amanda Aird, Paresha Farastu, Joshua Sun, Elena Stefancová, Cassidy All, Amy Voida, Nicholas Mattei, and Robin Burke. 2024. Dynamic Fairness-aware Recom mendation Through Multi-agent Social Choice. ACM Trans. Recomm. Syst. 3, 2, Article 21 (2024).

[2] Jincheng Bai, Zhenyu Zhang, Jennifer Zhang, and Jason Zhu. 2025. Insight Agents: An LLM-Based Multi-Agent System for Data Insights (SIGIR ’25). Association for Computing Machinery, 4335–4339.

[3] Nicolas Bougie and Narimawa Watanabe. 2025. SimUSER: Simulating User Behavior with Large Language Models for Recommender System Evaluation. In Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 6: Industry Track). Association for Computational Linguistics, 43–60.

[4] Shihao Cai, Jizhi Zhang, Keqin Bao, Chongming Gao, Qifan Wang, Fuli Feng, and Xiangnan He. 2025. Agentic Feedback Loop Modeling Improves Recommen dation and User Simulation (SIGIR ’25). Association for Computing Machinery, 2235–2244.

[5] Junyi Chen, Lu Chi, Siliang Xu, Shiwei Ran, Bingyue Peng, and Zehuan Yuan. 2025. HLLM-Creator: Hierarchical LLM-based Personalized Creative Generation. arXiv:2508.18118 [cs.IR]

[6] Lei Chen, Jingtao Ding, Min Yang, Chengming Li, Chonggang Song, and Lingling Yi. 2022. Item-Provider Co-learning for Sequential Recommendation (SIGIR ’22) Association for Computing Machinery, 1817–1822.

[7] Xiaoshuang Chen, Yibo Wang, Yao Wang, Husheng Liu, Kaiqiao Zhan, Ben Wang, and Kun Gai. 2025. Creator-Side Recommender System: Challenges, Designs, and Applications (WWW ’25). Association for Computing Machinery, 162–170.

[8] Paul Covington, Jay Adams, and Emre Sargin. 2016. Deep Neural Networks for YouTube Recommendations. In Proceedings of the 10th ACM Conference on Recommender Systems (RecSys ’16). Association for Computing Machinery, 191–198.

[9] Fangxiaoyu Feng, Yinfei Yang, Daniel Cer, Naveen Arivazhagan, and Wei Wang. 2022. Language-agnostic BERT Sentence Embedding. In Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers). Association for Computational Linguistics, 878–891.

[10] Chongming Gao, Ruijun Chen, Shuai Yuan, Kexin Huang, Yuanqing Yu, and Xiangnan He. 2025. SPRec: Self-Play to Debias LLM-based Recommendation (WWW ’25). 5075–5084.

[11] Chongming Gao, Mengyao Gao, Chenxiao Fan, Shuai Yuan, Wentao Shi, and Xiangnan He. 2025. Process-Supervised LLM Recommenders via Flow-guided Tuning (SIGIR ’25). Association for Computing Machinery, 1934–1943.

[12] Chongming Gao, Kexin Huang, Jiawei Chen, Yuan Zhang, Biao Li, Peng Jiang, Shiqi Wang, Zhong Zhang, and Xiangnan He. 2023. Alleviating Matthew Efect of Ofline Reinforcement Learning in Interactive Recommendation (SIGIR ’23). Association for Computing Machinery, 238–248.

[13] Mengyao Gao, Chongming Gao, Jiakai Tang, Jingsen Zhang, Xinpeng Zhao, Bohao Wang, Jiawei Chen, Haoran He, Ling Pan, Xu Chen, Xin Xin, Qingpeng Cai, Peng Jiang, Kun Gai, Haoyan Liu, Fuli Feng, and Xiangnan He. 2026. Integrating Large Language Models with Reinforcement Learning: A Survey of LLM-RL Synergistic Recommendation. TechRxiv Preprint (2026)

[14] Azin Ghazimatin, Oana Balalau, Rishiraj Saha Roy, and Gerhard Weikum. 2020. PRINCE: Provider-side Interpretability with Counterfactual Explanations in Recommender Systems (WSDM ’20). Association for Computing Machinery, 196–204.

[15] Po-Sen Huang, Xiaodong He, Jianfeng Gao, Li Deng, Alex Acero, and Larry Heck. 2013. Learning deep structured semantic models for web search using clickthrough data. In Proceedings of the 22nd ACM international conference on Information & Knowledge Management. 2333–2338.

[16] Xu Huang, Jianxun Lian, Yuxuan Lei, Jing Yao, Defu Lian, and Xing Xie. 2025. Recommender AI Agent: Integrating Large Language Models for Interactive Recommendations. ACM Trans. Inf. Syst. 43, 4, Article 96 (2025).

[17] Kalervo Järvelin and Jaana Kekäläinen. 2002. Cumulated gain-based evaluation of IR techniques. ACM Trans. Inf. Syst. 20, 4 (2002), 422–446.

[18] Wang-Cheng Kang and Julian McAuley. 2018. Self-Attentive Sequential Recommendation. In 2018 IEEE International Conference on Data Mining (ICDM). 197–206.

[19] Jiahao Liu, Shengkang Gu, Dongsheng Li, Guangping Zhang, Mingzhe Han, Hansu Gu, Peng Zhang, Tun Lu, Li Shang, and Ning Gu. 2025. AgentCF++: Memory-enhanced LLM-based Agents for Popularity-aware Cross-domain Recommendations (SIGIR ’25). Association for Computing Machinery, 2566–2571.

[20] Hanjia Lyu, Song Jiang, Hanqing Zeng, Yinglong Xia, Qifan Wang, Si Zhang, Ren Chen, Chris Leung, Jiajie Tang, and Jiebo Luo. 2024. LLM-Rec: Personalized Recommendation via Prompting Large Language Models. In Findings of the Association for Computational Linguistics: NAACL 2024. Association for Computational Linguistics, 583–612.

[21] Guangtao Nie, Rong Zhi, Xiaofan Yan, Yufan Du, Xiangyang Zhang, Jianwei Chen, Mi Zhou, Hongshen Chen, Tianhao Li, Ziguang Cheng, Sulong Xu, and Jinghe Hu. 2024. A Hybrid Multi-Agent Conversational Recommender System with LLM and Search Engine in E-commerce (RecSys ’24). Association for Computing Machinery, 745–747.

[22] Tao Qi, Fangzhao Wu, Chuhan Wu, Peijie Sun, Le Wu, Xiting Wang, Yongfeng Huang, and Xing Xie. 2022. ProFairRec: Provider Fairness-aware News Recom mendation (SIGIR ’22). Association for Computing Machinery, 1164–1173.

[23] Hossein A. Rahmani, Mohammadmehdi Naghiaei, and Yashar Deldjoo. 2024. A Personalized Framework for Consumer and Producer Group Fairness Optimization in Recommender Systems. ACM Trans. Recomm. Syst. 2, 3, Article 19 (2024).

[24] Wentao Shi, Xiangnan He, Yang Zhang, Chongming Gao, Xinyue Li, Jizhi Zhang, Qifan Wang, and Fuli Feng. 2024. Large Language Models are Learnable Planners for Long-Term Recommendation (SIGIR ’24). 1893–1903.

[25] Ashudeep Singh and Thorsten Joachims. 2018. Fairness of Exposure in Rankings (KDD ’18). Association for Computing Machinery, 2219–2228.

[26] Chengbing Wang, Yang Zhang, Wenjie Wang, Xiaoyan Zhao, Fuli Feng, Xiangnan He, and Tat-Seng Chua. 2025. Think-While-Generating: On-the-Fly Reasoning for Personalized Long-Form Generation. ArXiv abs/2512.06690 (2025).

[27] Junlin Wang, Jue Wang, Ben Athiwaratkun, Ce Zhang, and James Y Zou. 2025. Mixture-of-Agents Enhances Large Language Model Capabilities. In International Conference on Learning Representations. 33944–33963.

[28] Lei Wang, Jingsen Zhang, Hao Yang, Zhi-Yuan Chen, Jiakai Tang, Zeyu Zhang, Xu Chen, Yankai Lin, Hao Sun, Ruihua Song, Xin Zhao, Jun Xu, Zhicheng Dou, Jun Wang, and Ji-Rong Wen. 2025. User Behavior Simulation with Large Language Model-based Agents. ACM Trans. Inf. Syst. 43, 2, Article 55 (2025).

[29] Mingze Wang, Chongming Gao, Wenjie Wang, Yangyang Li, and Fuli Feng. 2025. Tunable LLM-based Proactive Recommendation Agent. In Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers). Association for Computational Linguistics, 19262–19276.

[30] Xinyuan Wang, Liang Wu, Liangjie Hong, Hao Liu, and Yanjie Fu. 2025. LLM Enhanced User–Item Interactions: Leveraging Edge Information for Optimized Recommendations. ACM Trans. Intell. Syst. Technol. 16, 5, Article 117 (2025).

[31] Yancheng Wang, Ziyan Jiang, Zheng Chen, Fan Yang, Yingxue Zhou, Eunah Cho, Xing Fan, Yanbin Lu, Xiaojiang Huang, and Yingzhen Yang. 2024. RecMind: Large Language Model Powered Agent For Recommendation. In Findings of the Association for Computational Linguistics: NAACL 2024. Association for Computational Linguistics, 4351–4364.

[32] Zhefan Wang, Yuanqing Yu, Wendi Zheng, Weizhi Ma, and Min Zhang. 2024. MACRec: A Multi-Agent Collaboration Framework for Recommendation (SIGIR ’24). Association for Computing Machinery, 2760–2764.

[33] Xinye Wanyan, Danula Hettiachchi, Chenglong Ma, Ziqi Xu, and Jefrey Chan. 2025. Temporal-Aware User Behaviour Simulation with Large Language Models for Recommender Systems (CIKM ’25). Association for Computing Machinery, 5335–5339.

[34] Chenghao Wu, Ruiyang Ren, Junjie Zhang, Ruirui Wang, Zhongrui Ma, Qi Ye, and Wayne Xin Zhao. 2025. STARec: An Eficient Agent Framework for Recom mender Systems via Autonomous Deliberate Reasoning (CIKM ’25). Association for Computing Machinery, 3355–3365.

[35] Yao Wu, Jian Cao, Guandong Xu, and Yudong Tan. 2021. TFROM: A Two-sided Fairness-Aware Recommendation Model for Both Customers and Providers. In Proceedings of the 44th International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR ’21). Association for Computing Machinery, 1013–1022.

[36] Zijing Wu, Leheng Sheng, Yuanlin Xia, Yi Zhang, Yuxin Chen, and An Zhang. 2025. Personalized Recommendation Agents with Self-Consistency. In Companion Proceedings of the ACM on Web Conference 2025 (WWW ’25). 2978–2982.

[37] Chen Xu, Sirui Chen, Jun Xu, Weiran Shen, Xiao Zhang, Gang Wang, and Zhenhua Dong. 2023. P-MMF: Provider Max-min Fairness Re-ranking in Recommender System (WWW ’23). Association for Computing Machinery, 3701–3711.

[38] Chen Xu, Xiaopeng Ye, Jun Xu, Xiao Zhang, Weiran Shen, and Ji-Rong Wen. 2024. LTP-MMF: Toward Long-Term Provider Max-Min Fairness under Recommenda tion Feedback Loops. ACM Trans. Inf. Syst. 43, 1, Article 11 (2024).

[39] Wujiang Xu, Yunxiao Shi, Zujie Liang, Xuying Ning, Kai Mei, Kun Wang, Xi Zhu, Min Xu, and Yongfeng Zhang. 2025. iAgent: LLM Agent as a Shield between User and Recommender Systems. In Findings of the Association for Computational Linguistics: ACL 2025. Association for Computational Linguistics, 18056–18084.

[40] Yuwei Yan, Yu Shang, Qingbin Zeng, Yu Li, Keyu Zhao, Zhiheng Zheng, Xuefe Ning, Tianji Wu, Shengen Yan, Yu Wang, Fengli Xu, and Yong Li. 2025. AgentSoci ety Challenge: Designing LLM Agents for User Modeling and Recommendation on Web Platforms (WWW ’25). Association for Computing Machinery, 2963–2967.

[41] Xiaopeng Ye, Chen Xu, Zhongxiang Sun, Jun Xu, Gang Wang, Zhenhua Dong, and Ji-Rong Wen. 2025. LLM-Empowered Creator Simulation for Long-Term Evaluation of Recommender Systems Under Information Asymmetry (SIGIR ’25). Association for Computing Machinery, 201–211.

[42] An Zhang, Yuxin Chen, Leheng Sheng, Xiang Wang, and Tat-Seng Chua. 2024. On Generative Agents in Recommendation (SIGIR ’24). Association for Computing Machinery, 1807–1817.

[43] Jizhi Zhang, Keqin Bao, Wenjie Wang, Yang Zhang, Wentao Shi, Wanhong Xu, Fuli Feng, and Tat-Seng Chua. 2025. Envisioning Recommendations on an LLM-Based Agent Platform. Commun. ACM 68, 5 (2025), 48–57.

[44] Junjie Zhang, Yupeng Hou, Ruobing Xie, Wenqi Sun, Julian McAuley, Wayne Xin Zhao, Leyu Lin, and Ji-Rong Wen. 2024. AgentCF: Collaborative Learning with Autonomous Language Agents for Recommender Systems (WWW ’24). Associa tion for Computing Machinery, 3679–3689.

[45] Yihua Zhang, Xi Liu, Xihuan Zeng, Mingfu Liang, Jiyan Yang, Rong Jin, Wen-Yen Chen, Yiping Han, Hao Ma, Bo Long, Huayu Li, Buyun Zhang, Liang Luo, Sijia Liu, and Tianlong Chen. 2025. ReasonRec: A Reasoning-Augmented Multimodal Agent for Unified Recommendation. In ICML 2025 Workshop on Programmatic Representations for Agent Learning.

[46] Yang Zhang, Wenxin Xu, Xiaoyan Zhao, Wenjie Wang, Fuli Feng, Xiangnan He, and Tat-Seng Chua. 2025. Reinforced Latent Reasoning for LLM-based Recommendation. ArXiv abs/2505.19092 (2025). https://api.semanticscholar.org/ CorpusID:278905774

[47] Zaibin Zhang, Zhenfei Yin, and Jing Shao. 2024. GENSS: A GENERALIZED AND SCALABLE LLM-BASED AGENTS SOCIAL NETWORK SIMULATOR. In NeurIPS 2024 Workshop on Open-World Agents.

[48] Xiaoyan Zhao, Juntao You, Yang Zhang, Wenjie Wang, Hong Cheng, Fuli Feng, See-Kiong Ng, and Tat-Seng Chua. 2025. NextQuill: Causal Preference Modeling for Enhancing LLM Personalization. ArXiv abs/2506.02368 (2025).

[49] Yuyue Zhao, Jiancan Wu, Xiang Wang, Wei Tang, Dingxian Wang, and Maarten de Rijke. 2024. Let Me Do It For You: Towards LLM Empowered Recommendation via Tool Learning (SIGIR ’24). Association for Computing Machinery, 1796–1806.

[50] Ziyi Zhao, Chongming Gao, Yang Zhang, Haoyan Liu, Weinan Gan, Huifeng Guo, Yong Liu, and Fuli Feng. 2026. Don’t Start Over: A Cost-Efective Framework for Migrating Personalized Prompts Between LLMs. The 40th Annual AAAI Conference on Artificial Intelligence (AAAI 2026) (2026).

[51] Yongsen Zheng, Ruilin Xu, Guohua Wang, Liang Lin, and Kwok-Yan Lam. 2024. Mitigating Matthew Efect: Multi-Hypergraph Boosted Multi-Interest Self-Supervised Learning for Conversational Recommendation (EMNLP ’24). Association for Computational Linguistics, 1455–1466.

[52] Lixi Zhu, Xiaowen Huang, and Jitao Sang. 2025. A LLM-based Controllable, Scalable, Human-Involved User Simulator Framework for Conversational Recommender Systems (WWW ’25). Association for Computing Machinery, 4653–4661.

[53] Yaochen Zhu, Harald Steck, Dawen Liang, Yinhan He, Nathan Kallus, and Jundong Li. 2025. LLM-based Conversational Recommendation Agents with Collaborative Verbalized Experience (EMNLP ’25). Association for Computational Linguistics, 2207–2220.

## Eficient Retrieval Scaling with Hierarchical Indexing for Large Scale Recommendation

# Eficient Retrieval Scaling with Hierarchical Indexing for Large Scale Recommendation

Dongqi Fu dongqifu@meta.com Meta USA

Yunchen Pu pyc40@meta.com Meta USA

Yiqun Liu yiqliu@meta.com Meta USA

Fangzhou Xu fxu@meta.com Meta USA

Lin Yang ylin1@meta.com Meta USA

Kaushik Rangadurai krangadu@meta.com Meta USA

Siyang Yuan syyuan@meta.com Meta USA

Golnaz Ghasemiesfeh golnazghasemi@meta.com Meta USA

Andrew Cui andycui97@meta.com Meta USA

Liang Wang liangwang@meta.com Meta USA

Chonglin Sun clsun@meta.com Meta USA

Haiyu Lu hylu@meta.com Meta USA

Minhui Huang mhhuang@meta.com Meta USA

Xingfeng He xingfenghe@meta.com Meta USA

Vidhoon Viswanathan vidhoon@meta.com Meta USA

Jiyan Yang chocjy@meta.com Meta USA

## Abstract

The increase in data volume, computational resources, and model parameters during training has led to the development of numerous large-scale industrial retrieval models for recommendation tasks. However, efectively and eficiently deploying these largescale foundational retrieval models remains a critical challenge that has not been fully addressed. Common quick-win solutions for deploying these massive models include relying on ofline computations (such as cached user dictionaries) or distilling large models into smaller ones. Yet, both approaches fall short of fully leveraging the representational and inference capabilities of foundational models. In this paper, we explore whether it is possible to learn a hierarchical organization over the memory of foundational retrieval models. Such a hierarchical structure would enable more eficient search by reducing retrieval costs while preserving exactness. To achieve this, we propose jointly learning a hierarchical index using cross-attention and residual quantization for large-scale retrieval models. We also present its real-world deployment at Meta, supporting daily advertisement recommendations for billions of Facebook and Instagram users. Interestingly, we discovered that the intermediate nodes in the learned index correspond to a small set of high-quality data. Fine-tuning the model on this set further improves inference performance, and concretize the concept of "test-time training" within the recommendation system domain. We demonstrate these findings using both internal and public datasets with strong baseline comparisons and hope they contribute to the community’s eforts in developing the next generation of foundational retrieval models.

## Keywords

Foundation Retrieval Model, Hierarchical Index

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

## 3 Hierarchical Index Learning (HILL)

To avoid the tree construction process relying solely on item embeddings to lose information [12, 13, 30, 31, 36, 67], but retaining as much information as possible, we aim to design a learning-based tree construction method. Moreover, given the comprehensiveness of MoNN to take ample <user, item> information, we then design a joint learning method for the hierarchical index construction.

Formally, in this section, we introduce our Hierarchical Index Learning method, named HILL, which can build up the hierarchical structure to organize items to help the foundation retrieval model (like MoNN) to retrieve the most relevant items for users, and also produce a small amount of high-quality new data to fine-tune the model for test-time training efectiveness.

First, we briefly introduce the overview of HILL in Section 3.1. Stepping into details, we then introduce how to learn one layer mapping function in Section 3.2, how to residually stack up layers in Section 3.3, how to optimize the learning process in Section 3.4, an approximation learning manner in Section 3.5, and how to extract qualified new data in Section 3.6, respectively.

## 3.1 Overview

In Figure 3, we show a hierarchical index example learnt by our HILL method. To be more specific, in the illustration of Figure 3, we have 8 items ranging from 1 to 8. The learnt hierarchical is a three layer tree, with node <sup>??</sup> as the root. Given a user query <sup>??</sup>, starting from root <sup>??</sup>, a search algorithm (e.g., beam search with width as 2) locates item 1 as the most relevant item for user <sup>??</sup>, which is included in the recommendation set for user <sup>??</sup> and avoids the heavy computing of the similarity from each item to the user <sup>??</sup>.

![](images/67825f42d7baf9b200350ffba236ff9bd78b7de4b2bda388103d0419d1a7965e.jpg)  
Figure 3: A Hierarchical Index Example Learnt by HILL.

More importantly, in Figure 3, tracing from the leaf node 1 to the root node <sup>??</sup>, HILL also identifies a valuable but hidden path, i.e., $1 \to d \to b \to a$ , which records the interested inter-level nodes that user <sup>??</sup> may also interest in. Since this tree is learnt, nodes <sup>??</sup>, <sup>??</sup>, <sup>??</sup> are virtual nodes and not appear in the training data, which has the potential to fine-tune the model with user item pairs <<sup>??,</sup> <sup>??</sup>> and <<sup>??,</sup> <sup>??</sup>>. The reason HILL selected <sup>??</sup> and <sup>??</sup> but excluded <sup>??</sup> is extended in Section 4.6.

## 3.2 One-Layer Attention Learning

To build up a hierarchical tree, the first fundamental step is to establish one layer, i.e., taking items as leaf nodes and mapping them to the upper level.

Taking MoNN as an example to provide user and item embeddings, we next introduce our one-layer attention learning algorithm, as shown in Algorithm 1, which takes the embedding vectors from a MoNN model as input and learns coarse index node embeddings for the item by minimizing the L2 distance between them. To be specific, our proposed algorithm employs an attention-based method by taking the item embedding as query, learnable embeddings for index nodes as keys and values, to calculate the index embeddings. With attention score, our algorithm allows the soft mapping during the training process, that is, one item can belong to multiple index nodes with varying weights.

<div class="mineru-algorithm" style="white-space: pre-wrap; font-family:monospace;">
Algorithm 1 One-Layer Attention Learning
Require: MoNN Model, Hyperparameter K
Ensure: Item-Index Mapping Function M, Embedding Matrix R of Index Nodes
1: Randomly initialize index nodes' embedding vectors  $\{c_{k}\}_{k=1}^{K}$ 
2: while not converge do
    /* Mini-Batch Training */
3:    for each item j in a batch do
4:    Sample a user-item pair &lt;i, j&gt; with label y, compute user embedding  $u_{i}$  and item embedding  $v_{j}$  and through MoNN
5:    Compute the distance between item j and index k as
6:    $d(j, k) = \|v_{j} - c_{k}\|^{2}$ 
7:    Compute the affinity between item j and index k as
8:    $a_{k} = \frac{e^{-\alpha*d(j,k)}}{\sum_{k'} e^{-\alpha*d(j,k')}}$ 
9:    Compute the pseudo item embedding by  $\bar{c} = \sum_{k} a_{k} c_{k}$ 
10:    Update MoNN optimization with new pair  $(y, \langle u_{i}, \bar{c} \rangle)$ 
11:    end for
    /* Finalize Index Embedding and Mapping*/
12:    for each k index node do
13:    for each item j in the corpora do
14:    Update M(j, k) by d(j, k)
15:    $c_{k} = v_{j}$ , if argmin_j d(j, k)
16:    end for
17:    end for
18: end while
19: Return function M and matrix R(k,:) =  $c_{k}$
</div>

## 3.3 Cross-Layer Residual Learning

Given that a single layer can be established, the next step is to stack it up iteratively. To make the index hierarchical, (i.e., the semantics of the upper level should depend on the lower level, and also store the information that lower level can not hold), inspired by residual quantization [29, 59], we aim to pass residue between input item embedding and the corresponding index node embedding at the lower level to its next index layer.

Recall Lines 8–9 in Algorithm 1, the index node representation learning is stored in the form (i.e., soft assignment or attentionbased aggregation) of pseudo item embedding. It gives us the possibility of aligned dimensions across layers in the hierarchical tree. In other words, for each layer, we can have a ground truth item embedding and a pseudo item embedding that is closely associated with the index embedding.

Mathematically, given <sup>??</sup> index nodes at each level<sup>1</sup>, and the <sup>??</sup> level to be established, our cross-layer residual learning can be expressed as follows: Suppose we have the initial embedding vectors for all items by asking the MoNN model, and the embedding vector for item $j .$ is denoted as $\upsilon _ { j } ;$ Then, we can denote the initial residual vector $r _ { j } ^ { 1 }$ for item <sup>??</sup> at the 1-st layer as

$$
\boldsymbol {r} _ {j} ^ {1} = \boldsymbol {v} _ {j}\tag{4}
$$

According to Lines 8–9 in Algorithm 1, HILL produces the pseudo item embedding vector $\bar { \pmb { c } } _ { j } ^ { 1 }$ for item <sup>??</sup> when mapping the 1- st layer to the 2-nd layer. Hence, the gap for the residual learning to mix can be expressed as follows. At each level $n \in \{ 2 , \ldots , N \}$ the recursive quantization of the residual vector is

$$
\boldsymbol {r} _ {j} ^ {n} = \boldsymbol {r} _ {j} ^ {n - 1} - \bar {\boldsymbol {c}} _ {j} ^ {n - 1}\tag{5}
$$

The above residual vector $r _ { j } ^ { n }$ will serve as the item representation learning when building the next layer, i.e., replacing Line 4 in Algorithm 1 that asks MoNN to provide item embeddings.

Consequently, at each level <sup>??</sup>, the quantized embedding vector is computed as $\begin{array} { r } { \pmb q _ { j } ^ { n } = \sum _ { l = 1 } ^ { n - 1 } \bar { \pmb c } _ { j } ^ { l } } \end{array}$

The reconstruction loss $\scriptstyle { \mathcal { L } } _ { r e c o n }$ is computed as:

$$
\mathcal {L} _ {r e c o n} = \sum_ {j} \| \boldsymbol {q} _ {j} ^ {N} - \boldsymbol {v} \| ^ {2}\tag{6}
$$

The magnitude of residuals decreases when further moving down the hierarchy. As a result, a coarse index layer identifier expresses more general concepts, while a fine-grained index layer captures more detailed notions.

## 3.4 Optimization

In order to better optimize our HILL algorithm for the index building, a few additional techniques are introduced to improve the training stability, including softmax temperature scheduler, balanced index distribution, and warmup strategy.

Softmax Temperature Scheduler. In the serving stage, the embedding vector of index nodes will serve as virtual items to help the user query to retrieve a bunch of its relevant items. However, during the training process, our HILL algorithm uses a soft <item, index node> assignment, where each index node can be viewed as a combination of diferent interest items that can contain irrelevant items. To mitigate the discrepancy, a scheduler is applied by gradually increasing the temperature (alpha), transitioning from soft assignment in the initial phase to a hard assignment later on. Small values of alpha yield a balanced distribution of the item-to-index assignment, while large values of alpha result in a skewed distribution. The scheduler is based on the following function:

$$
a l p h a = m a x \_ a l p h a * \frac {c u r r e n t \_ i t e r ^ {e x p}}{m a x \_ i t e r s ^ {e x p}}\tag{7}
$$

Balanced Index Distribution. The index learning often suffers from cluster collapse, where the model utilizes only a limited subset of index nodes. A balanced index distribution is crucial to enable the use of neural network models with high complexity. Therefore, we employ the FLOPs regularizer to address this problem. The motivation stems from [40], which penalizes the model if all items are assigned to the same index node or if the distribution of <item, index node> assignment is imbalanced. Given it can be sensitive to smaller batches, data from the most recent <sup>??</sup> batches is pooled and the FLOPs regularizer is applied on the pooled soft assignment matrix $( K ^ { \star }$ batch\_size, num\_index\_nodes).

Warmup Strategy. A linear warm up strategy is employed for the index loss weight to gradually increase the learning rate, which is expected to stabilize the model parameters and mitigate the issue of item assignment oscillating between index nodes during the initial training phase.

## 3.5 Expectation–Maximization Approximation by FAISS

The essence of learning the hierarchical index for a foundation model is to make the memory of the foundation model structurally organized, such that the relevance retrieval can use the optimal path and prune unnecessary branches. In the above sections, we already discussed how to learn the index via the cotraining process. However, the co-training process inevitably involves the training of a foundation model, which can be infeasible during a short time window (e.g., hourly) and heavy workload (e.g., billion-scale users and million-scale items). In this viewpoint, we aim to propose an alternative learning method in case the computing resources are not adequate.

If we model the hierarchical index as an internal part of the well-trained foundation model, then we can solve the problem of learning the hierarchical index by using the Expectation-Maximization (EM) algorithm. To be more specific, if we view the index node as a (soft or hard) cluster of items, then we can model the item-index mapping as the hidden variables and user and item embedding as observation variables, such that the problem can be approximated as a Gaussian mixture model. Then, the E-step can be assigning each item its closest cluster and can be implemented by the GPU-enabled FAISS [8, 24] parallel clustering library, e.g., K-Means; and the M-step can be training the foundation model according to current index embeddings. This iterative EM-based approximation enables fast optimization when computing resources are not necessary or for small updates between two time windows. In the experiments, we also show that this approximation leads to acceptable efectiveness.

Again, when computing resources are suficient, a full version of HILL is recommended. The full version of HILL has advantages, including: (1) continuous training indexing with neural networks, which would be able to dynamically adapt to the latest data in the online streaming scenario; (2) avoiding the need to maintain diferent computational frameworks. The above conditions are important considerations for an industry-scale production system, to the best of our knowledge.

## 3.6 New Data from HILL to Enable Test-Time Training

In the last part, we aim to introduce how, after establishing the hierarchical index, we discover the new qualified training data to fine-tune the foundation model.

As shown in Figure 3, the beam search from top to the bottom finds the item 1 for user <sup>??</sup>. If we traverse back, it is easy to identity a path: $1 \to d \to b \to a ,$ which implies that user <sup>??</sup> is also interested in index nodes <sup>??</sup>, <sup>??</sup>, and <sup>??</sup>. Then, a natural question arises: can they make up new data pairs and help finetune the foundation model? The answer is positive, since we can intuitively interpret the intermediate-level index nodes as the machine-readable category nodes for items after the (pre-)training process, and pairing them with original users generates the new training data <user, index node> (e.g., <user <sup>??</sup>, index <sup>??</sup>> and <user <sup>??</sup>, index <sup>??</sup>>), which is not seen in the previous training iterations and expects to bring new information to fine-tune the model.

However, along this path, not all qualified intermediate-level index nodes are qualified enough to be selected to fine-tune the model. The first obvious clue is that the higher-level index nodes should be excluded from the new data set constructions, because the higher level an index node stands, the more general meaning it has. An extreme case is that the root node is shared by all users when we traverse back, such that adding <user, root> pair brings noise to the fine-tuning process. Therefore, the first hyperparameter for extracting the new data pairs, is how deep we traverse back from the bottom (i.e., item level), denoted as <sup>??</sup>?????? . For example, in the above case, <sup>??</sup>?????? is 2 for getting the new data <user $u ,$ index <sup>??</sup>> and <user <sup>??</sup>, index <sup>??</sup>> for user <sup>??</sup>.

Second, if we zoom in, index <sup>??</sup> or index <sup>??</sup> may also not qualify enough, because user <sup>??</sup>’s interest can spread over <sup>??</sup>’s items and other indices’ items. We model that if user <sup>??</sup>’s interest concentrates only on <sup>??</sup>’s items, then <user <sup>??</sup>, index <sup>??</sup>> is a qualified new data pair. Mathematically, we propose an interest rate parameter $\phi _ { I R } ,$ , which takes a user <sup>??</sup> and an index node <sup>??</sup> at level <sup>??</sup>,

$$
\phi_ {I R} (u, i ^ {n}) = \frac {| I n t (u , n - 1) \cap C h i l d (i ^ {n}) |}{C h i l d (i ^ {n})}\tag{8}
$$

where <sup>??????</sup> (<sup>??,</sup> <sup>??</sup> − 1) is a function to return the interested items (or index nodes) at level <sup>??</sup> − 1 of the index tree, and <sup>??ℎ??????</sup> (<sup>??</sup> ) returns the set of direct children of node $i ^ { n }$ at level $n - 1$

Therefore, we can use $\phi _ { I R }$ to filter out index nodes that only share a small portion of a certain user’s interest, when we compose the fine-tuning data pairs for this user. An intuitive understanding of $\phi _ { I R }$ can be: only if the user has very frequent preferences on <user, basketball> and <user, football>, and we discover <user, sports>; if user is interested in <user, basketball>, <user, music>, and <user, cooking>, then <user, sports> is not a strong signal. But again, in HILL, we did not dive deeper to learn to assign the human-readable semantic meaning for each index node, but only to use their embedding vectors.

Based on the above modeling, we discern that just a small <sup>??</sup>?????? and a large <sup>??</sup>???? (<sup>??, ??</sup> ) threshold can select a small portion of new data, with which the fine-tuning can achieve a significan performance gain. So far, we have only considered the positive strong signal in the above modeling, following the original loss during the fine-tuning. Moreover, weighing the new data pair with the weak signal and even negative signal, and adding contrastive learning loss functions during the fine-tuning process leave promising future directions.

## 4 Experiments

In this section, we introduce the datasets, baselines, metrics, ofline performance, and online service report.

## 4.1 Datasets

Here, we choose both public benchmark datasets and internal datasets to demonstrate the performance. For the public datasets, we select Gowalla, Yelp 2018, and Amazon-Book, as shown in Table 2, which records various user-item interactions and are publicly available<sup>2</sup>. The internal datasets are from daily Ads Recommendation tasks from Meta Platform.

## 4.2 Baselines

We select diferent categorical baselines, including (1) classic collaborative filtering methods, (2) neural collaborative filtering methods, (3) generative collaborative filtering methods, (4) industrial retrieval models, (5) general graph neural networks, and (6) graph neural network-inspired retrieval models. For the page limitation, we leave the reference of each baseline in Table 3.

Table 1: HILL-Enabled MoNN Performance with Baselines in Internal Data. $\mathbf { I } _ { 1 } , \mathbf { I } _ { 2 } , \mathbf { V }$ are in the order of O(1,000), O(100,000), O(10,000,000), $\mathbf { M } _ { s }$ denotes the model size of Small Model, and $\mathbf { M } _ { \mathrm { L } }$ denotes the model size of Large Model

<table><tr><td>Model Architecture</td><td>Eval NE (↓)</td><td>Recall (↑)</td><td>Infra Cost (↓)</td><td>Theoretical Cost</td></tr><tr><td>TTSN [3]</td><td>baseline</td><td>0%</td><td>1x</td><td> $M_{XS} \times V$ </td></tr><tr><td>EBR [23]</td><td>+0.03%</td><td>-0.1%</td><td>0.5x</td><td> $M_{XS} \times I_1$ </td></tr><tr><td>MoNN Small</td><td>-0.29%</td><td>+2.4%</td><td>2.5x</td><td> $M_S \times V$ </td></tr><tr><td>MoNN Medium</td><td>-0.70%</td><td>+4.2%</td><td>17.3x</td><td> $M_M \times V$ </td></tr><tr><td>MoNN Large</td><td>-1.70%</td><td>+9.4%</td><td>24.6x</td><td> $M_L \times V$ </td></tr><tr><td>2-layer MoNN(L1: MoNN Small, L2: TTSN)</td><td>-0.23%</td><td>+2.2%</td><td>1.7x</td><td> $M_S \times I_1 + M_{XS} \times V$ </td></tr><tr><td>2-layer MoNN(L1: MoNN Medium, L2: MoNN Small)</td><td>-0.47%</td><td>+3.6%</td><td>3.3x</td><td> $M_M \times I_1 + M_S \times V$ </td></tr><tr><td>2-layer MoNN(L1: MoNN Large, L2: MoNN Small)</td><td>-0.97%</td><td>+6.0%</td><td>3.9x</td><td> $M_L \times I_1 + M_S \times V$ </td></tr></table>

Table 2: Statistics of Public Benchmark Datasets.

<table><tr><td>Dataset</td><td># Users</td><td># Items</td><td># Interactions</td><td>Density</td></tr><tr><td>Gowalla</td><td>29,858</td><td>40,981</td><td>1,027,370</td><td>0.084%</td></tr><tr><td>Yelp2018</td><td>31,688</td><td>38,048</td><td>1,561,406</td><td>0.130%</td></tr><tr><td>Amazon-Book</td><td>55,188</td><td>9,912</td><td>1,445,622</td><td>0.062%</td></tr></table>

## 4.3 Metrics

To verify the retrieval performance, metrics in the experiments consist of Recall, Normalized Discounted Cumulative Gain (NDCG), and Normalized Entropy (NE)

Recall@<sup>??</sup> measures the ability of a model to retrieve relevant items within the top-<sup>??</sup> recommended list.

$$
\operatorname{Recall} @ K = \frac {\left| \operatorname{Rel} _ {u} \cap \operatorname{Rec} _ {u} ^ {K} \right|}{\left| \operatorname{Rel} _ {u} \right|}
$$

where $\mathrm { R e l } _ { u }$ denotes the set of relevant (ground-truth) items for user <sup>??</sup>, and $\operatorname { R e c } _ { u } ^ { K }$ is the set of top-<sup>??</sup> recommended items. Higher values indicate better coverage of relevant items. For the public datasets, we choose Recall@20.

NDCG@K accounts not only for the presence of relevant items in the recommendation list but also for their positions.

$$
\mathrm{NDCG@} K = \frac {1}{| \mathcal {U} |} \sum_ {u \in \mathcal {U}} \frac {\mathrm{DCG} _ {u} @ K}{\mathrm{IDCG} _ {u} @ K}
$$

where $\begin{array} { r } { \mathrm { D C G } _ { u } @ K = \sum _ { i = 1 } ^ { K } \frac { \mathbb { I } ( r _ { u , i } = 1 ) } { \log _ { \mathcal { I } } ( i + 1 ) } , \mathbb { I } ( y _ { u , i } = 1 ) } \end{array}$ indicates whether the <sup>??</sup>-th item in the recommended list for user <sup>??</sup> is relevant, and IDC $\begin{array} { r } { \mathrm { { : } } \mathrm { G } _ { u } @ K = \sum _ { i = 1 } ^ { \operatorname* { m i n } ( K , | \mathrm { R e l } _ { u } | ) } \frac { 1 } { \log _ { 2 } ( i + 1 ) } } \end{array}$ . In other words, NDCG@K emphasizes recommending relevant items at higher ranks, and the higher the better.

NE is selected based on the previous recommendation lessons at Facebook [19]. Assume a given training data set has <sup>??</sup> examples with labels <sup>??</sup>?? ∈ {−1<sup>,</sup> +1} and estimated probability of click $\mathscr { p } _ { i }$ where $i = 1 , 2 , \ldots , N$ . The average empirical CTR as ${ \boldsymbol { p } } ,$ then

$$
N E = \frac {- \frac {1}{N} \sum_ {i = 1} ^ {n} \left(\frac {1 + y _ {i}}{2} \log (p _ {i}) + \frac {1 - y _ {i}}{2} \log (1 - p _ {i})\right)}{- (p \cdot \log (p) + (1 - p) \cdot \log (1 - p))}\tag{9}
$$

The reason for this normalization is that the closer the background CTR is to either 0 or 1, the easier it is to achieve a better log loss. Dividing by the entropy of the background CTR makes the NE insensitive to the background CTR. The lower the value, the better the prediction made by the model.

$$
\text { Normalized   Entropy@ } K = \frac {- \sum_ {i \in \mathcal {I}} p _ {i} \log p _ {i}}{\log | \mathcal {I} _ {K} |}\tag{10}
$$

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

## 4.5 Online Service Report

The MoNN foundation retrieval model has been successfully deployed at Meta for Ads Retrieval. Prior to the deployment of MoNN Large, we first launched the MoNN Small architecture to production, given the relatively low infra cost. As shown in Table 8, online A/B tests demonstrate that 2-Layer MoNN led to 2.57% online ads metric gains.

Table 8: Online performance in Meta Ads Production.

<table><tr><td>Model Architecture</td><td>Online Metric (↑)</td></tr><tr><td>TTSN</td><td>-0.21%</td></tr><tr><td>MoNN Small</td><td>baseline</td></tr><tr><td>2-Layer MoNN(L1: MoNN Medium, L2: MoNN Small)</td><td>+1.22%</td></tr><tr><td>2-Layer MoNN(L1: MoNN Large, L2: MoNN Small)</td><td>+2.57%</td></tr></table>

## 4.6 Details of Deploying MoNN

In this section, we introduce the stacked MoNN model. Figure 4 shows a 3-layer MoNN model architecture: $\mathrm { L } _ { 1 }$ layer, L layer, and $\mathrm { L } _ { 3 }$ layer. The $\mathrm { L } _ { 1 }$ layer operates on the coarsest index granularity and it is able to take advantage of a MoNN model architecture with the highest complexity (through computation sharing) and a wide range of interaction features (<user, $\mathrm { L } _ { 1 }$ index node>). Then, the $\mathrm { L } _ { 3 }$ index operates on the finest granularity (in extreme case, it can be item level directly) and leverages a MoNN block with the lowest complexity. The three MoNN modules are combined using the ensemble layer. This manner allows final prediction to leverage multiple MoNNs with diferent model complexity to consume diferent granularity of features, resulting in a more accurate prediction.

Features. MoNN Small processes features at the individual item level, utilizing user features, item features, and <user, item> interaction features. In contrast, MoNN Medium and MoNN Large operate at a coarser granularity $( \mathrm { L } _ { 2 }$ layer and $\mathrm { L } _ { 1 }$ layer, respectively) and consume user features, index node features, and <user, index node> interaction features, where index node is replaced by a representative item for feature computation.

![](images/9cccbf6964856f62b4e613cb7b8a4fe6d7b5c6994a8b243d511679cfe0333706.jpg)  
Figure 4: 3-Layer MoNN Illustration Example.

Loss Function. Each layer of multi-layer MoNN has its own loss function, i.e., with 1 <user, item> prediction loss function and <user, index node> prediction loss function.

## 5 Related Work

To support retrieval models, prior works suggest that organizing candidate items into index structures can reduce the search space and expedite the identification of relevant item-user pairs [12, 13, 30, 31, 36, 67]. However, such methods are often inadequate for modern industrial-scale foundation models, which typically employ deep, densely connected neural architectures to capture complex user-item interactions enriched with structured contextual information. To the best of our knowledge, existing indexing techniques fall short of addressing the exactness and scalability demands of these models. Motivated by this limitation, we propose to learn a hierarchical index tailored to the memory components of large-scale foundation retrieval models. This index is designed to support exactness-aware search, enabling eficient inference by bypassing redundant search paths and thereby reducing unnecessary computational overhead.

Meanwhile, the notion of scaling laws at training has recently been extended to the context of foundation models for ranking and retrieval [1, 11, 16, 20, 25, 45, 65]. Test-time training strategies in recommendation systems remain largely underexplored. Our work aims to address this gap and spark further research into eficient and scalable inference for foundation retrieval models.

## 6 Conclusion

To make the large-scale foundation retrieval model serve efectively and eficiently, in this paper, we propose the hierarchical index learning method HILL to learn the index structure over the memory of the foundation model, taking MoNN (i.e., a deployed retrieval model at Meta for Ads Retrieval) for illustration. Moreover, we found that learnt index convey a small set of new and high-quality data pairs that can be used to test-time fine-tune the model to boost the performance.

## References

[1] Newsha Ardalani, Carole-Jean Wu, Zeliang Chen, Bhargav Bhushanam, and Adnan Aziz 2022, Understanding Scaling Laws for Recommendation Models CoRR abs/2208 08489 (2022),doi:10 48550/ARXIV 2208 08489 arXiv:2208 08489

[2] Oren Barkan and Noam Koenigstein. 2016. ITEM2VEC: Neural item embedding for collaborative filtering. In 26th IEEE International Workshop on Machine Learning for Signal Processing, MLSP 2016, Vietri sul Mare, Salerno, Italy, September 13-16, 2016, Francesco A. N. Palmieri, Aurelio Uncini, Kostas I. Diamantaras, and Jan Larsen (Eds.). IEEE, 1–6. doi:10.1109/MLSP.2016.7738886

[3] Jane Bromley, Isabelle Guyon, Yann LeCun, Eduard Säckinger, and Roopak Shah. 1993. Signature Verification Using a Siamese Time Delay Neural Network. In Advances in Neural Information Processing Systems 6, [7th NIPS Conference, Denver, Colorado, USA, 1993], Jack D. Cowan, Gerald Tesauro, and Joshua Alspector (Eds.). Morgan Kaufmann, 737–744. http://papers.nips.cc/paper/769- signature-verification-using-a-siamese-time-delay-neural-network

[4] Chong Chen, Min Zhang, Yongfeng Zhang, Yiqun Liu, and Shaoping Ma. 2020. Eficient Neural Matrix Factorization without Sampling for Recommendation. ACM Trans. Inf. Syst. 38, 2 (2020), 14:1–14:28. doi:10.1145/3373807

[5] Jeongwhan Choi, Seoyoung Hong, Noseong Park, and Sung-Bae Cho. 2023. Blurring-Sharpening Process Models for Collaborative Filtering. In Proceedings of the 46th International ACM SIGIR Conference on Research and Development in Information Retrieval, SIGIR 2023, Taipei, Taiwan, July 23-27, 2023, Hsin-Hsi Chen, Wei-Jou (Edward) Duh, Hen-Hsen Huang, Makoto P. Kato, Josiane Mothe, and Barbara Poblete (Eds.). ACM, 1096–1106. doi:10.1145/3539618. 3591645

[6] Jeongwhan Choi, Jinsung Jeon, and Noseong Park. 2021. LT-OCF: Learnable-Time ODE-based Collaborative Filtering. In CIKM ’21: The 30th ACM International Conference on Information and Knowledge Management, Virtual Event, Queensland, Australia, November 1 - 5, 2021, Gianluca Demartini, Guido Zuccon, J. Shane Culpepper, Zi Huang, and Hanghang Tong (Eds.). ACM, 251–260. doi:10.1145/3459637.3482449

[7] Paul Covington, Jay Adams, and Emre Sargin. 2016. Deep Neural Networks for YouTube Recommendations. In Proceedings of the 10th ACM Conference on Recommender Systems, Boston, MA, USA, September 15-19, 2016, Shilad Sen, Werner Geyer, Jill Freyne, and Pablo Castells (Eds.). ACM, 191–198. doi:10 1145/2959100.2959190

[8] Matthijs Douze, Alexandr Guzhva, Chengqi Deng, Jef Johnson, Gergely Szilvasy, Pierre-Emmanuel Mazaré, Maria Lomeli, Lucas Hosseini, and Hervé Jégou. 2024. The Faiss library. CoRR abs/2401.08281 (2024). doi:10.48550/ ARXIV.2401.08281 arXiv:2401.08281

[9] Travis Ebesu, Bin Shen, and Yi Fang. 2018. Collaborative Memory Network for Recommendation Systems. In The 41st International ACM SIGIR Conference on Research & Development in Information Retrieval, SIGIR 2018, Ann Arbor, MI, USA, July 08-12, 2018, Kevyn Collins-Thompson, Qiaozhu Mei, Brian D Davison, Yiqun Liu, and Emine Yilmaz (Eds.). ACM, 515–524. doi:10.1145/ 3209978.3209991

[10] Wenqi Fan, Xiaorui Liu, Wei Jin, Xiangyu Zhao, Jiliang Tang, and Qing Li. 2022. Graph Trend Filtering Networks for Recommendation. In SIGIR ’22: The 45th International ACM SIGIR Conference on Research and Development in Information Retrieval, Madrid, Spain, July 11 - 15, 2022, Enrique Amigó, Pablo Castells, Julio Gonzalo, Ben Carterette, J. Shane Culpepper, and Gabriella Kazai (Eds.). ACM, 112–121. doi:10.1145/3477495.3531985

[11] Yan Fang, Jingtao Zhan, Qingyao Ai, Jiaxin Mao, Weihang Su, Jia Chen, and Yiqun Liu. 2024. Scaling Laws For Dense Retrieval. In Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval, SIGIR 2024, Washington DC, USA, July 14-18, 2024, Grace Hui Yang, Hongning Wang, Sam Han, Claudia Hauf, Guido Zuccon, and Yi Zhang (Eds.). ACM, 1339–1349. doi:10.1145/3626772.3657743

[12] Chao Feng, Wuchao Li, Defu Lian, Zheng Liu, and Enhong Chen. 2022. Recommender Forest for Eficient Retrieval. In Advances in Neural Information Processing Systems 35: Annual Conference on Neural Information Processing Systems 2022, NeurIPS 2022, New Orleans, LA, USA, November 28 - December 9, 2022, Sanmi Koyejo, S. Mohamed, A. Agarwal, Danielle Belgrave, K. Cho, and A. Oh (Eds.). http://papers.nips.cc/paper\_files/paper/2022/hash fe2fe749d329627f161484876630c689-Abstract-Conference html

[13] Weihao Gao, Xiangjun Fan, Chong Wang, Jiankai Sun, Kai Jia, Wenzhi Xiao, Ruofan Ding, Xingyan Bin, Hui Yang, and Xiaobing Liu. 2020. Deep retrieval: learning a retrievable structure for large-scale recommendations. arXiv preprint arXiv:2007.07203 (2020).

[14] Aditya Grover and Jure Leskovec. 2016. node2vec: Scalable Feature Learning for Networks In Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, San Francisco, CA, USA, August 13- 17, 2016, Balaji Krishnapuram, Mohak Shah, Alexander J. Smola, Charu C. Aggarwal, Dou Shen, and Rajeev Rastogi (Eds.). ACM, 855–864. doi:10.1145 2939672.2939754

[15] Huifeng Guo, Ruiming Tang, Yunming Ye, Zhenguo Li, and Xiuqiang He. 2017. DeepFM: A Factorization-Machine based Neural Network for CTR Prediction. In Proceedings of the Twenty-Sixth International Joint Conference on Artificial Intelligence, IJCAI 2017, Melbourne, Australia, August 19-25, 2017, Carles Sierra (Ed.). ijcai.org, 1725–1731. doi:10.24963/IJCAI.2017/239

[16] Wei Guo, Hao Wang, Luankang Zhang, Jin Yao Chin, Zhongzhou Liu, Kai Cheng, Qiushi Pan, Yi Quan Lee, Wanqi Xue, Tingjia Shen, Kenan Song, Kefan Wang, Wenjia Xie, Yuyang Ye, Huifeng Guo, Yong Liu, Defu Lian, Ruiming Tang, and Enhong Chen. 2024. Scaling New Frontiers: Insights into Large Recommendation Models. CoRR abs/2412.00714 (2024). doi:10.48550/ARXIV. 2412.00714 arXiv:2412.00714

[17] Moritz Hardt and Yu Sun. 2024. Test-Time Training on Nearest Neighbors for Large Language Models. In The Twelfth International Conference on Learning

Representations, ICLR 2024, Vienna, Austria, May 7-11, 2024. OpenReview.net. https://openreview.net/forum?id=CNL2bku4ra

[18] Xiangnan He, Kuan Deng, Xiang Wang, Yan Li, Yong-Dong Zhang, and Meng Wang. 2020. LightGCN: Simplifying and Powering Graph Convolution Network for Recommendation. In Proceedings of the 43rd International ACM SIGIR conference on research and development in Information Retrieval, SIGIR 2020, Virtual Event, China, July 25-30, 2020, Jimmy X. Huang, Yi Chang, Xueqi Cheng, Jaap Kamps, Vanessa Murdock, Ji-Rong Wen, and Yiqun Liu (Eds.). ACM, 639–648. doi:10.1145/3397271.3401063

[19] Xinran He, Junfeng Pan, Ou Jin, Tianbing Xu, Bo Liu, Tao Xu, Yanxin Shi, Antoine Atallah, Ralf Herbrich, Stuart Bowers, and Joaquin Quiñonero Candela. 2014. Practical Lessons from Predicting Clicks on Ads at Facebook. In Proceedings of the Eighth International Workshop on Data Mining for Online Advertising, ADKDD 2014, August 24, 2014, New York City, New York, USA, Esin Saka, Dou Shen, Kuang-chih Lee, and Ying Li (Eds.). ACM, 5:1–5:9. doi:10.1145/2648584.2648589

[20] Jordan Hofmann, Sebastian Borgeaud, Arthur Mensch, Elena Buchatskaya, Trevor Cai, Eliza Rutherford, Diego de Las Casas, Lisa Anne Hendricks, Johannes Welbl, Aidan Clark, Tom Hennigan, Eric Noland, Katie Millican, George van den Driessche, Bogdan Damoc, Aurelia Guy, Simon Osindero, Karen Simonyan, Erich Elsen, Jack W. Rae, Oriol Vinyals, and Laurent Sifre. 2022. Training Compute-Optimal Large Language Models. CoRR abs/2203.15556 (2022). doi:10.48550/ARXIV.2203.15556 arXiv:2203.15556

[21] Cheng-Kang Hsieh, Longqi Yang, Yin Cui, Tsung-Yi Lin, Serge J. Belongie, and Deborah Estrin. 2017. Collaborative Metric Learning. In Proceedings of the 26th International Conference on World Wide Web, WWW 2017, Perth, Australia, April 3-7, 2017, Rick Barrett, Rick Cummings, Eugene Agichtein, and Evgeniy Gabrilovich (Eds.). ACM, 193–201. doi:10.1145/3038912.3052639

[22] Jun Hu, Bryan Hooi, Shengsheng Qian, Quan Fang, and Changsheng Xu. 2024. MGDCF: Distance Learning via Markov Graph Difusion for Neural Collaborative Filtering. IEEE Trans. Knowl. Data Eng. 36, 7 (2024), 3281–3296. doi:10.1109/TKDE.2023.3348537

[23] Jui-Ting Huang, Ashish Sharma, Shuying Sun, Li Xia, David Zhang, Philip Pronin, Janani Padmanabhan, Giuseppe Ottaviano, and Linjun Yang. 2020. Embedding-based Retrieval in Facebook Search. In KDD ’20: The 26th ACM SIGKDD Conference on Knowledge Discovery and Data Mining, Virtual Event, CA, USA, August 23-27, 2020, Rajesh Gupta, Yan Liu, Jiliang Tang, and B. Aditya Prakash (Eds) ACM. 2553=2561 doi:10.1145/3394486.3403305

[24] Jef Johnson, Matthijs Douze, and Hervé Jégou. 2021. Billion-Scale Similarity Search with GPUs. IEEE Trans. Big Data 7, 3 (2021), 535–547. doi:10.1109/ TBDATA.2019.2921572

[25] Jared Kaplan, Sam McCandlish, Tom Henighan, Tom B. Brown, Benjamin Chess, Rewon Child, Scott Gray, Alec Radford, Jefrey Wu, and Dario Amodei. 2020. Scaling Laws for Neural Language Models. CoRR abs/2001.08361 (2020). arXiv:2001.08361 https://arxiv.org/abs/2001.08361

[26] Johannes Klicpera, Aleksandar Bojchevski, and Stephan Günnemann. 2019. Predict then Propagate: Graph Neural Networks meet Personalized PageRank. In 7th International Conference on Learning Representations, ICLR 2019, New Orleans, LA, USA, May 6-9, 2019. OpenReview.net. https://openreview.net/ forum?id=H1gL-2A9Ym

[27] Taeyong Kong, Taeri Kim, Jinsung Jeon, Jeongwhan Choi, Yeon-Chang Lee, Noseong Park, and Sang-Wook Kim. 2022. Linear, or Non-Linear, That is the Question!. In WSDM ’22: The Fifteenth ACM International Conference on Web Search and Data Mining, Virtual Event / Tempe, AZ, USA, February 21 - 25, 2022, K. Selcuk Candan, Huan Liu, Leman Akoglu, Xin Luna Dong, and Jiliang Tang (Eds.). ACM, 517–525. doi:10.1145/3488560.3498501

[28] Dongha Lee, SeongKu Kang, Hyunjun Ju, Chanyoung Park, and Hwanjo Yu. 2021. Bootstrapping User and Item Representations for One-Class Collaborative Filtering In SIGIR '21: The 44th International ACM SIGIR Conference on Research and Development in Information Retrieval, Virtual Event, Canada, July 11-15, 2021, Fernando Diaz, Chirag Shah, Torsten Suel, Pablo Castells, Rosie Jones, and Tetsuya Sakai (Eds.). ACM, 1513–1522. doi:10.1145/3404835.3462935

[29] Doyup Lee, Chiheon Kim, Saehoon Kim, Minsu Cho, and Wook-Shin Han. 2022. Autoregressive Image Generation using Residual Quantization. arXiv:2203 01941 [cs CV]

[30] Haitao Li, Qingyao Ai, Jingtao Zhan, Jiaxin Mao, Yiqun Liu, Zheng Liu, and Zhao Cao 2023 Constructing Tree-based Index for Efficient and Effective Dense Retrieval. In Proceedings of the 46th International ACM SIGIR Conference on Research and Development in Information Retrieval, SIGIR 2023, Taipei, Taiwan, July 23-27, 2023, Hsin-Hsi Chen, Wei-Jou (Edward) Duh, Hen-Hsen Huang, Makoto P. Kato, Josiane Mothe, and Barbara Poblete (Eds.). ACM, 131–140. doi:10.1145/3539618.3591651

[31] Wuchao Li, Kai Zheng, Defu Lian, Qi Liu, Wentian Bao, Yunen Yu, Yang Song, Han Li, and Kun Gai. 2025. Making Transformer Decoders Better Diferentiable Indexers. In The Thirteenth International Conference on Learning Representations, ICLR 2025, Singapore, April 24-28, 2025. OpenReview.net. https: //openreview.net/forum?id=bePaRx0otZ

[32] Dawen Liang, Rahul G. Krishnan, Matthew D. Hofman, and Tony Jebara. 2018. Variational Autoencoders for Collaborative Filtering. In Proceedings of the 2018 World Wide Web Conference on World Wide Web, WWW 2018, Lyon, France, April 23-27, 2018, Pierre-Antoine Champin, Fabien Gandon, Mounia Lalmas, and Panagiotis G. Ipeirotis (Eds.). ACM, 689–698. doi:10.1145/3178876.3186150

[33] Mingfu Liang, Xi Liu, Rong Jin, Boyang Liu, Qiuling Suo, Qinghai Zhou, Song Zhou, Laming Chen, Hua Zheng, Zhiyuan Li, Shali Jiang, Jiyan Yang, Xiaozhen

Xia, Fan Yang, Yasmine Badr, Ellie Wen, Shuyu Xu, Hansey Chen, Zhengyu Zhang, Jade Nie, Chunzhi Yang, Zhichen Zeng, Weilin Zhang, Xingliang Huang, Qianru Li, Shiquan Wang, Evelyn Lyu, Wenjing Lu, Rui Zhang, Wenjun Wang, Jason Rudy, Mengyue Hang, Kai Wang, Bo Long, Wenlin Chen, Santanu Kolay, and Huayu Li. 2025. External Large Foundation Model: How to Eficiently Serve Trillions of Parameters for Online Ads Recommendation. In Companion Proceedings of the ACM on Web Conference 2025, WWW 2025, Sydney, NSW, Australia, 28 April 2025 - 2 May 2025, Guodong Long, Michale Blumestein, Yi Chang, Liane Lewin-Eytan, Zi Helen Huang, and Elad Yom-Tov (Eds.). ACM, 344–353. doi:10.1145/3701716.3715223

[34] Fan Liu, Zhiyong Cheng, Lei Zhu, Zan Gao, and Liqiang Nie. 2021. Interestaware Message-Passing GCN for Recommendation. In WWW ’21: The Web Conference 2021, Virtual Event / Ljubljana, Slovenia, April 19-23, 2021, Jure Leskovec, Marko Grobelnik, Marc Najork, Jie Tang, and Leila Zia (Eds.). ACM / IW3C2, 1296–1305. doi:10.1145/3442381.3449986

[35] Zhiwei Liu, Lin Meng, Fei Jiang, Jiawei Zhang, and Philip S. Yu. 2022. Deoscillated Adaptive Graph Collaborative Filtering. In Topological, Algebraic and Geometric Learning Workshops 2022, 25-22 July 2022, Virtual (Proceedings of Machine Learning Research, Vol. 196), Alexander Cloninger, Timothy Doster, Tegan Emerson, Manohar Kaul, Ira Ktena, Henry Kvinge, Nina Miolane, Bastian Rice, Sarah Tymochko, and Guy Wolf (Eds.). PMLR, 248–257. https://proceedings.mlr.press/v196/liu22b.html

[36] Ze Liu, Jin Zhang, Chao Feng, Defu Lian, Jie Wang, and Enhong Chen. 2024. Learning Deep Tree-based Retriever for Eficient Recommendation: Theory and Method. arXiv preprint arXiv:2408.11345 (2024).

[37] Jianxin Ma, Peng Cui, Kun Kuang, Xin Wang, and Wenwu Zhu. 2019. Disentangled Graph Convolutional Networks. In Proceedings of the 36th International Conference on Machine Learning, ICML 2019, 9-15 June 2019, Long Beach, California, USA (Proceedings of Machine Learning Research, Vol. 97), Kamalika Chaudhuri and Ruslan Salakhutdinov (Eds.). PMLR, 4212–4221. http://proceedings.mlr.press/v97/ma19a.html

[38] Jianxin Ma, Chang Zhou, Peng Cui, Hongxia Yang, and Wenwu Zhu. 2019. Learning Disentangled Representations for Recommendation. In Advances in Neural Information Processing Systems 32: Annual Conference on Neural Information Processing Systems 2019, NeurIPS 2019, December 8-14, 2019, Vancouver, BC, Canada, Hanna M. Wallach, Hugo Larochelle, Alina Beygelzimer, Florence d’Alché-Buc, Emily B. Fox, and Roman Garnett (Eds.). 5712–5723. https://proceedings.neurips.cc/paper/2019/hash/ a2186aa7c086b46ad4e8bf81e2a3a19b-Abstract.html

[39] Kelong Mao, Jieming Zhu, Jinpeng Wang, Quanyu Dai, Zhenhua Dong, Xi Xiao, and Xiuqiang He. 2021. SimpleX: A Simple and Strong Baseline for Collaborative Filtering. In CIKM ’21: The 30th ACM International Conference on Information and Knowledge Management, Virtual Event, Queensland, Australia, November 1 - 5, 2021, Gianluca Demartini, Guido Zuccon, J. Shane Culpepper, Zi Huang, and Hanghang Tong (Eds.). ACM, 1243–1252. doi:10.1145/3459637. 3482297

[40] Biswajit Paria, Chih-Kuan Yeh, Ian E. H. Yen, Ning Xu, Pradeep Ravikumar, and Barnabás Póczos. 2020. Minimizing FLOPs to Learn Eficient Sparse Representations. arXiv:2004.05665 [cs.LG]

[41] Bryan Perozzi, Rami Al-Rfou, and Steven Skiena. 2014. DeepWalk: online learning of social representations. In The 20th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, KDD ’14, New York, NY, USA - August 24 - 27, 2014, Sofus A. Macskassy, Claudia Perlich, Jure Leskovec, Wei Wang, and Rayid Ghani (Eds.). ACM, 701–710. doi:10.1145/ 2623330.2623732

[42] Nikhil Rao, Hsiang-Fu Yu, Pradeep Ravikumar, and Inderjit S. Dhillon. 2015. Collaborative Filtering with Graph Information: Consistency and Scalable Methods. In Advances in Neural Information Processing Systems 28: Annual Conference on Neural Information Processing Systems 2015, December 7-12, 2015, Montreal, Quebec, Canada, Corinna Cortes, Neil D. Lawrence, Daniel D. Lee, Masashi Sugiyama, and Roman Garnett (Eds.). 2107–2115. https://proceedings.neurips.cc/paper/2015/hash/ f4573fc71c731d5c362f0d7860945b88-Abstract html

[43] Stefen Rendle, Christoph Freudenthaler, Zeno Gantner, and Lars Schmidt-Thieme. 2009. BPR: Bayesian Personalized Ranking from Implicit Feedback. In UAI 2009, Proceedings of the Twenty-Fifth Conference on Uncertainty in Artificial Intelligence Montreal OC Canada Fune 18-21 2009 Jeff A Bilmes and Andrew Y. Ng (Eds.). AUAI Press, 452–461. https://www.auai.org/uai2009 papers/UAI2009\_0139\_48141db02b9f0b02bc7158819ebfa2c7.pdf

[44] Yu Rong, Wenbing Huang, Tingyang Xu, and Junzhou Huang. 2020. DropEdge: Towards Deep Graph Convolutional Networks on Node Classification. In 8th International Conference on Learning Representations, ICLR 2020, Addis Ababa, Ethiopia, April 26-30, 2020. OpenReview.net. https://openreview.net/forum? id=Hkx1qkrKPr

[45] Kyuyong Shin, Hanock Kwak, Su Young Kim, Max Nihlén Ramström, Jisu Jeong, Jung-Woo Ha, and Kyung-Min Kim. 2023. Scaling Law for Recommendation Models: Towards General-Purpose User Representations. In Thirty-Seventh AAAI Conference on Artificial Intelligence, AAAI 2023, Thirty-Fifth Conference on Innovative Applications of Artificial Intelligence, IAAI 2023, Thirteenth Symposium on Educational Advances in Artificial Intelligence, EAAI 2023, Washington, DC, USA, February 7-14, 2023, Brian Williams, Yiling Chen, and Jennifer Neville (Eds.). AAAI Press, 4596–4604. doi:10.1609/AAAI.V37I4.25582

[46] Jianing Sun, Yingxue Zhang, Wei Guo, Huifeng Guo, Ruiming Tang, Xiuqiang He, Chen Ma, and Mark Coates. 2020. Neighbor Interaction Aware Graph

Convolution Networks for Recommendation. In Proceedings of the 43rd International ACM SIGIR conference on research and development in Information Retrieval, SIGIR 2020, Virtual Event, China, July 25-30, 2020, Jimmy X. Huang, Yi Chang, Xueqi Cheng, Jaap Kamps, Vanessa Murdock, Ji-Rong Wen, and Yiqun Liu (Eds.). ACM, 1289–1298. doi:10.1145/3397271.3401123

[47] Peijie Sun, Le Wu, Kun Zhang, Xiangzhi Chen, and Meng Wang. 2024. Neighborhood-Enhanced Supervised Contrastive Learning for Collaborative Filtering. IEEE Trans. Knowl. Data Eng. 36, 5 (2024), 2069–2081. doi:10.1109/ TKDE.2023.3317068

[48] Yu Sun, Xiaolong Wang, Zhuang Liu, John Miller, Alexei A. Efros, and Morit Hardt. 2020. Test-Time Training with Self-Supervision for Generalization under Distribution Shifts. In Proceedings of the 37th International Conference on Machine Learning, ICML 2020, 13-18 July 2020, Virtual Event (Proceedings of Machine Learning Research, Vol. 119). PMLR, 9229–9248. http://proceedings. mlr.press/v119/sun20b.htm

[49] Jian Tang, Meng Qu, Mingzhe Wang, Ming Zhang, Jun Yan, and Qiaozhu Mei. 2015. LINE: Large-scale Information Network Embedding. In Proceedings of the 24th International Conference on World Wide Web, WWW 2015, Florence, Italy, May 18-22, 2015, Aldo Gangemi, Stefano Leonardi, and Alessandro Panconesi (Eds.). ACM, 1067–1077. doi:10.1145/2736277.2741093

[50] Rianne van den Berg, Thomas N. Kipf, and Max Welling. 2017. Graph Convolutional Matrix Completion. CoRR abs/1706.02263 (2017). arXiv:1706.02263 http://arxiv.org/abs/1706.02263

[51] Petar Velickovic, Guillem Cucurull, Arantxa Casanova, Adriana Romero, Pietro Liò, and Yoshua Bengio. 2018. Graph Attention Networks. In 6th International Conference on Learning Representations, ICLR 2018, Vancouver, BC, Canada, April 30 - May 3, 2018, Conference Track Proceedings. OpenReview.net. https: //openreview.net/forum?id=rJXMpikCZ

[52] Xiang Wang, Xiangnan He, Meng Wang, Fuli Feng, and Tat-Seng Chua. 2019. Neural Graph Collaborative Filtering. In Proceedings of the 42nd International ACM SIGIR Conference on Research and Development in Information Retrieval, SIGIR 2019, Paris, France, July 21-25, 2019, Benjamin Piwowarski, Max Chevalier, Éric Gaussier, Yoelle Maarek, Jian-Yun Nie, and Falk Scholer (Eds.). ACM, 165– 174. doi:10.1145/3331184.3331267

[53] Xiang Wang, Hongye Jin, An Zhang, Xiangnan He, Tong Xu, and Tat-Seng Chua. 2020. Disentangled Graph Collaborative Filtering. In Proceedings of the 43rd International ACM SIGIR conference on research and development in Information Retrieval, SIGIR 2020, Virtual Event, China, July 25-30, 2020, Jimmy X. Huang, Yi Chang, Xueqi Cheng, Jaap Kamps, Vanessa Murdock, Ji-Rong Wen, and Yiqun Liu (Eds.). ACM, 1001–1010. doi:10.1145/3397271. 3401137

[54] Jiancan Wu, Xiang Wang, Fuli Feng, Xiangnan He, Liang Chen, Jianxun Lian, and Xing Xie. 2021. Self-supervised Graph Learning for Recommendation. In SIGIR ’21: The 44th International ACM SIGIR Conference on Research and Development in Information Retrieval, Virtual Event, Canada, July 11-15, 2021, Fernando Diaz, Chirag Shah, Torsten Suel, Pablo Castells, Rosie Jones, and Tetsuya Sakai (Eds.). ACM, 726–735. doi:10.1145/3404835.3462862

[55] Keyulu Xu, Chengtao Li, Yonglong Tian, Tomohiro Sonobe, Ken-ichi Kawarabayashi, and Stefanie Jegelka. 2018. Representation Learning on Graphs with Jumping Knowledge Networks. In Proceedings of the 35th International Conference on Machine Learning, ICML 2018, Stockholmsmässan, Stockholm, Sweden, July 10-15, 2018 (Proceedings of Machine Learning Research, Vol. 80), Jennifer G. Dy and Andreas Krause (Eds.). PMLR, 5449–5458. http://proceedings.mlr.press/v80/xu18c.html

[56] Jheng-Hong Yang, Chih-Ming Chen, Chuan-Ju Wang, and Ming-Feng Tsai. 2018. HOP-rec: high-order proximity for implicit recommendation. In Proceedings of the 12th ACM Conference on Recommender Systems, RecSys 2018, Vancouver, BC, Canada, October 2-7, 2018, Sole Pera, Michael D. Ekstrand, Xavier Amatriain, and John O'Donovan (Eds) ACM 140–144, doi:10 1145 3240323.3240381

[57] Rex Ying, Ruining He, Kaifeng Chen, Pong Eksombatchai, William L. Hamilton, and Jure Leskovec. 2018. Graph Convolutional Neural Networks for Web-Scale Recommender Systems. In Proceedings of the 24th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining, KDD 2018, London, UK, August 19-23, 2018, Yike Guo and Faisal Farooq (Eds.). ACM, 974–983. doi:10. 1145/3219819.3219890

[58] Mert Yuksekgonul, Daniel Koceja, Xinhao Li, Federico Bianchi, Jed McCaleb, Xiaolong Wang, Jan Kautz, Yejin Choi, James Zou, Carlos Guestrin, et al. 2026. Learning to discover at test time. arXiv preprint arXiv:2601.16175 (2026).

[59] Neil Zeghidour, Alejandro Luebs, Ahmed Omran, Jan Skoglund, and Marco Tagliasacchi. 2021. SoundStream: An End-to-End Neural Audio Codec. arXiv:2107.03312 [cs.SD]

[60] Zhichen Zeng, Xiaolong Liu, Mengyue Hang, Xiaoyi Liu, Qinghai Zhou, Chaofei Yang, Yiqun Liu, Yichen Ruan, Laming Chen, Yuxin Chen, Yujia Hao, Jiaqi Xu, Jade Nie, Xi Liu, Buyun Zhang, Wei Wen, Siyang Yuan, Ka Wang, Wen-Yen Chen, Yiping Han, Huayu Li, Chunzhi Yang, Bo Long, Philip S. Yu, Hanghang Tong, and Jiyan Yang. 2024. InterFormer: Towards Efective Heterogeneous Interaction Learning for Click-Through Rate Prediction. CoRR abs/2411.09852 (2024). doi:10.48550/ARXIV,2411.09852 arXiv:2411.09852

[61] Jiaqi Zhai, Lucy Liao, Xing Liu, Yueming Wang, Rui Li, Xuan Cao, Leon Gao, Zhaojie Gong, Fangda Gu, Jiavuan He. Yinghai Lu, and Yu Shi, 2024, Actions Speak Louder than Words: Trillion-Parameter Sequential Transducers for Generative Recommendations. In Forty-first International Conference on Machine Learning, ICML 2024, Vienna, Austria, July 21-27, 2024. OpenReview.net.

https://openreview.net/forum?id=xye7iNsgXn

[62] Buyun Zhang, Liang Luo, Yuxin Chen, Jade Nie, Xi Liu, Shen Li, Yanli Zhao, Yuchen Hao, Yantao Yao, Ellie Dingqiao Wen, Jongsoo Park, Maxim Naumov, and Wenlin Chen. 2024. Wukong: Towards a Scaling Law for Large-Scale Recommendation. In Forty-first International Conference on Machine Learning, ICML 2024, Vienna, Austria, July 21-27, 2024. OpenReview.net. https://openreview.net/forum?id=8iUgr2nuwo

[63] Buyun Zhang, Liang Luo, Xi Liu, Jay Li, Zeliang Chen, Weilin Zhang, Xiaohan Wei, Yuchen Hao, Michael Tsang, Wenjun Wang, Yang Liu, Huayu Li, Yasmine Badr, Jongsoo Park, Jiyan Yang, Dheevatsa Mudigere, and Ellie Wen. 2022. DHEN: A Deep and Hierarchical Ensemble Network for Large-Scale Click-Through Rate Prediction. arXiv:2203.11014 [cs.IR] https://arxiv.org/abs/2203. 11014

[64] Buyun Zhang, Liang Luo, Xi Liu, Jay Li, Zeliang Chen, Weilin Zhang, Xiaohan Wei, Yuchen Hao, Michael Tsang, Wenjun Wang, Yang Liu, Huayu Li, Yasmine Badr, Jongsoo Park, Jiyan Yang, Dheevatsa Mudigere, and Ellie Wen. 2022. DHEN: A Deep and Hierarchical Ensemble Network for Large-Scale Click-Through Rate Prediction. CoRR abs/2203.11014 (2022). doi:10.48550/ARXIV.

2203.11014 arXiv:2203.11014

[65] Gaowei Zhang, Yupeng Hou, Hongyu Lu, Yu Chen, Wayne Xin Zhao, and Ji-Rong Wen. 2024. Scaling Law of Large Sequential Recommendation Models. In Proceedings of the 18th ACM Conference on Recommender Systems, RecSys 2024, Bari, Italy, October 14-18, 2024, Tommaso Di Noia, Pasquale Lops, Thorsten Joachims, Katrien Verbert, Pablo Castells, Zhenhua Dong, and Ben London (Eds.). ACM, 444–453. doi:10.1145/3640457.3688129

[66] Yinan Zhang, Pei Wang, Xiwei Zhao, Hao Qi, Jie He, Junsheng Jin, Changping Peng, Zhangang Lin, and Jingping Shao. 2022. IA-GCN: Interactive Graph Convolutional Network for Recommendation. CoRR abs/2204.03827 (2022). doi:10.48550/ARXIV.2204.03827 arXiv:2204.03827

[67] Han Zhu, Xiang Li, Pengye Zhang, Guozheng Li, Jie He, Han Li, and Kun Gai. 2018. Learning Tree-based Deep Model for Recommender Systems. In Proceedings of the 24th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining, KDD 2018, London, UK, August 19-23, 2018, Yike Guo and Faisal Farooq (Eds.). ACM, 1079–1088. doi:10.1145/3219819.3219826

## Diagnosing LLM-based Rerankers in Cold-Start Recommender Systems: Coverage, Exposure and Practical Mitigations

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

## Meta-Modal Agent: Sequential Evidence Routing for Missing-Modality Candidate Reranking

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

## Popcorn: A Configurable Benchmark for Visual Evidence in Multimodal Movie Recommendation

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

## Seeing and Reflecting: Multimodal Memory-Enhanced Agent Collaboration for Recommendation

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
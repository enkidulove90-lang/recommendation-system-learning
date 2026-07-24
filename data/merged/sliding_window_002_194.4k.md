orted according to the global timestamps, and then split into training, validation, and testing sets with the ratio of 8:1:1. For the item identifier, we follow LC-Rec [43] and TIGER [31] to set the length $L = 4 ,$ i.e., the token sequence length of a generated item would be 4.

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

## The Future is Agentic: Definitions, Perspectives, and Open Challenges of Multi-Agent Recommender Systems

# The Future is Agentic: Definitions, Perspectives, and Open Challenges of Multi-Agent Recommender Systems

REZA YOUSEFI MARAGHEH, <sup>University</sup> <sup>of</sup> <sup>Illinois</sup> <sup>Urbana</sup> <sup>Champaign,</sup> <sup>USA</sup> YASHAR DELDJOO, <sup>Polytechnic</sup> <sup>University</sup> <sup>of</sup> <sup>Bari,</sup> <sup>Italy</sup>

Large language models (LLMs) are evolving from passive text generators into agentic systems that can plan maintain state, invoke tools, and coordinate with other agents. This perspective paper examines what this shift means for recommender systems (RS). We define <sub>agentic</sub> <sub>recommender</sub> <sub>systems</sub> as recommendation pipelines in which one or more stateful agents observe, plan, call tools, and verify, rather than score in a single shot, while operating over users, item catalogs, candidate sets, and recommendation objectives. Their value is strongest when this added machinery measurably improves recommendation-layer outcomes such as relevance, constraint satisfaction, bundle coherence, grounding, explanation faithfulness, fairness of exposure, or user efort, and is not justified merely because a pipeline contains an LLM or several modules. To make these notions precise for recommendation rather than for agents in general, we introduce a recommender specific formalism that models an individual recommender agent by its state (user, context, history, and candidate set), a reasoning core, recommendation-specific tools, a hierarchical memory, and explicit policy constraints, and captures a multi-agent recommender as a triple of agents, a shared environment exposing the item catalog and feedback signals, and a communication protocol. Within this framework, we develop four representative task families (interactive goal-oriented recommendation, user simulation and evaluation, contextual and multimodal recommendation, and grounded explanation) and an operational agenda that ties five recurring challenge families (communication protocols, scalability and cost, hallucination and error propagation, emergent misalignment and collusion, and brand and policy compliance) to measurable RS signals. Finally, we conduct a controlled empirical study comparing single-shot and multi-agent pipelines under shared user histories, candidate sets, prompts, and metrics. A pilot next-item ranking study on Amazon 2023 categories shows that multi-agent systems are not uniformly superior: on representative samples the single-shot baseline is Pareto-eficient, whereas decomposition and ensemble agents become useful mainly for high-diversity user histories. This supports a conditional design principle: agentic complexity should be routed to the cases where its marginal quality improvement justifies the additional latency, cost, and governance risk. To support reproduction, we release all pipeline implementations, prompts, and results here: https://github.com/RezaYM/agenticrecsys.git.

<sup>CCS</sup> <sup>Concepts:</sup> <sup>•</sup> Information systems → Recommender systems<sup>.</sup>

ACM Reference Format:

Reza Yousefi Maragheh and Yashar Deldjoo. 2026. The Future is Agentic: Definitions, Perspectives, and Open Challenges of Multi-Agent Recommender Systems. <sub>ACM</sub> <sub>Trans.</sub> <sub>Recomm.</sub> <sub>Syst.</sub> 1, 1 (July 2026), 49 pages. https://doi.org/10.1145/nnnnnnn.nnnnnnn

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

## 1.1 A Motivating Example: Goal-Oriented Birthday-Party Recommendation

Figure 1 illustrates the type of recommendation task that motivates an agentic design. The user is not asking for a single ranked list of products from a static profile. Instead, the user begins with an open-ended goal: “a Mickey Mouse-themed birthday party.” The recommender then elicits missing constraints by asking about color preferences and dietary restrictions. When the user answers “Gluten free,” a dietary constraint is introduced that must be respected by the recommended collection. After the system proposes an initial set of party items, the user further revises the goal by asking whether the cake can be made larger and whether balloons can be added. This interaction shows that the task is not merely to rank products, but to support an evolving, goaloriented recommendation process: construct a coherent themed birthday-party bundle, satisfy dietary restrictions, adapt item attributes based on feedback, and add new item categories as the conversation unfolds.

To handle this complex natural-language intent, the system decomposes the broad goal into recommendation-relevant subtasks:

<sub>•</sub> A user-context component retrieves session-level and long-term traces, including recent dialogue state, prior preferences, accepted and rejected recommendations, and relevant constraints.

![](images/dcd7c85bdd6825b18b5b14b5ec6a2cdb62dd46d2fc9a01aef7ca0ed78040903c.jpg)  
Fig. 1. Left: Conversation example for a goal-oriented collection recommendation, where the user specifies an open-ended goal instead of searching for specific items. Right: Architecture for personalized goal-oriented recommendation using a multi-agent pipeline with specialized agents and tools.

<sub>•</sub> A specialized-agent caller dynamically instantiates sub-agents equipped with retrieval or generation tools for distinct recommendation categories, such as cakes, decorations, favors, or layout suggestions.

<sub>•</sub> Category-specific agents retrieve candidate items from catalog or search tools while respecting explicit constraints such as theme, dietary requirements, budget, and availability.

<sub>•</sub> A collection-consistency agent checks whether the resulting items cohere as a bundle, for example whether the cake, tablecloth, decor, and party favors follow the same theme and do not violate constraints.

<sub>•</sub> A ranking and presentation agent orders the curated item set according to user preferences, contextual priorities, and recommendation objectives, and can generate a user-facing explanation or visual layout.

Throughout this interaction, memory carries the evolving recommendation state across turns: the theme, the gluten-free constraint, the accepted and rejected items, and the later requests to enlarge the cake and add balloons. The example also makes the evaluation concern concrete, since the system must decide which of these memories are still relevant, which are stale, and which should be excluded for privacy, safety, or correctness reasons.

## 1.2 Organization of the Paper and Contributions

This is a perspective and conceptual framework paper, not a new learning algorithm and not an exhaustive survey. Its aim is to give the recommender-systems community a shared vocabulary and an evaluation-oriented agenda for agentic RS: precise definitions of agents, memory, tools, actions, communication protocols, traces, objectives, and evaluation signals, so that future work can describe architectures, compare systems, and separate recommender-specific contributions from general agent engineering. Throughout, we take the position that the value of agentic recommendation is strongest when orchestration and interaction measurably improve recommendation-layer outcomes, rather than when a pipeline merely adds LLM calls or agent coordination. To keep this distinction sharp, we separate a recommendation layer (candidate generation, ranking, and slate construction), an interaction layer (dialogue, clarification, explanation, and preference elicitation), and an orchestration layer (tool choice, agent coordination, memory management, and verification), defined in Section 2.5.

The paper makes four contributions.

• Core vocabulary, formal framework, and scope boundary (Section 2). <sup>We</sup> <sup>give</sup> <sup>the</sup> minimal architectural primitives needed to specify an agentic recommender system: recommender agents, user and item state, candidate sets, memory stores, tool interfaces, action spaces, communication protocols, constraints, objectives, and observable traces. We distinguish generic LLM agents from recommender agents, and separate recommendation-layer contributions from interaction-layer capabilities and generic orchestration infrastructure.

• Running example and task families (Fig. 1; Sections 3–4). <sup>Using</sup> <sup>the</sup> <sup>Mickey</sup> <sup>Mouse</sup> birthday-planning example as a running case, we show how specialized agents, toolchains, memory hierarchies, and verification modules compose for goal-oriented recommendation. We then develop four representative task families, interactive recommendation, user simulation and evaluation, contextual and multimodal recommendation, and grounded recommendation explanation, and indicate where a conventional ranking pipeline remains simpler, cheaper, and more reliable.

• Operational challenge and evaluation agenda (Section 5). <sup>We</sup> <sup>organize</sup> <sup>the</sup> <sup>open</sup> <sup>prob-</sup> lems of agentic recommendation into five challenge families, communication complexity and protocol design, scalability and cost, hallucination and error propagation, emergent misalignment and collusion, and brand, policy, and legal compliance, and connect each to measurable recommender-system signals such as ranking quality, evidence coverage, trace validity, latency, token cost, exposure disparity, policy-violation rate, and judge reliability.

<sub>•</sub> <sub>Controlled</sub> <sub>empirical</sub> <sub>study</sub> <sub>(Section</sub> <sub>6).</sub> We report a controlled experiment comparing single-shot LLM call and multi-agent recommendation pipelines under shared user histories, candidate sets, prompts, and metrics. A pilot next-item ranking study shows that multi-agent pipelines are conditionally useful: they do not dominate on representative samples, but decomposition and ensemble roles help on high-diversity histories.

## 2 Agentic Recommender Systems: Definition, Characteristics, Misconceptions

In this section, we clarify the concept of an <sub>LLM</sub> <sub>agent</sub>, in more depth. When illustrating through examples we use the context of recommender and retrieval systems. We also discuss common misconceptions about agentic pipelines and elaborate on what is <sub>not</sub> an LLM agent.

## 2.1 What Defines an LLM Agent

An <sub>LLM</sub> <sub>agent</sub>, in its fully functional capacity, is an AI system in which a large language model (LLM) serves as the core decision-making component (the “brain”), enhanced by additional mechanisms that enable it to carry out complex, multi-step tasks autonomously rather than relying on a single prompt-response. In other words, this LLM is part of a larger architecture that provides (i) planning abilities, (ii) memory, (iii) tool/API usage, for interactions with external systems, (iv) an <sub>autonomous</sub> <sub>decision</sub> <sub>loop</sub> that can break down a goal, observe intermediate steps, and adapt its strategy [61, 84]. In a broader context, multiple such language agents form a <sub>multi-agent</sub> <sub>system</sub> <sub>(MAS)</sub>, in which agents can interact, communicate, coordinate, and even compete– leveraging their reasoning and communication capabilities to collectively solve complex tasks that exceed the capacity of any single agent.

This design (i.e., agent-based approach) goes beyond the traditional static use of LLMs for singleturn queries and is increasingly used in recommendation and retrieval tasks. For example, an

Table 1. Core Capabilities of Agentic Recommender Systems

<table><tr><td>Icon</td><td>Capability</td><td>Description</td></tr><tr><td></td><td>Planning &amp; Task Decomposition</td><td>Breaks complex recommendation goals into sub-tasks, such as candidate selection, constraint checking, bundle retrieval, re-ranking, and verification.</td></tr><tr><td></td><td>Tool Use &amp; Action Execution</td><td>Invokes external tools or APIs, such as retrieval systems, inventory databases, policy checkers, vision models, or constraint solvers.</td></tr><tr><td></td><td>Memory &amp; State Management</td><td>Maintains state across turns and, when appropriate, across sessions using working, episodic, semantic, or procedural memory.</td></tr><tr><td></td><td>Autonomy &amp; Goal-Driven Behavior</td><td>Operates in a closed loop by observing context, choosing actions, evaluating intermediate outcomes, and revising the plan until the recommendation objective is satisfied or no further useful action is available.</td></tr></table>

LLM-based agent can iteratively search user logs to gather information about past item interactions before making tailored recommendations [58, 91].

## 2.2 Key Characteristics of LLM Agents

As summarized in Table 1, agentic recommender systems typically exhibit four core characteristics, described in the following:

(1) <sub>Planning</sub> <sub>and</sub> <sub>Task</sub> <sub>Decomposition:</sub> The agent can execute (or even formulate) a plan. This is done by breaking a complex goal into subtasks. Rather than producing an immediate, one-shot answer, an agentic system can plan for and conduct a sequence of steps. This can involve reasoning to tackle long-horizon tasks [16, 54]. For example, in a recommender scenario, the planning module may first identify candidate items, then check user history, retrieve a consistent bundle of products, then re-rank items before generating a final recommendation [87].

(2) <sub>Tool</sub> <sub>Use</sub> <sub>and</sub> <sub>Action</sub> <sub>Execution:</sub> An LLM agent is not limited to purely text-based outputs; it can <sub>invoke</sub> <sub>external</sub> <sub>tools</sub> <sub>or</sub> <sub>APIs</sub> and perform <sub>actions</sub> in an environment [84]. For instance, a recommendation agent could consult a real-time inventory database to see if recommended items are in stock, or it might retrieve user reviews from a knowledge base before finalizing its recommendations.

(3) <sub>Memory</sub> <sub>and</sub> <sub>State</sub> <sub>Management:</sub> LLM agents maintain a notion of “state” across multiple steps. They often incorporate a memory module which can potentially store conversation con text, past recommendations, user feedback, local guidelines, procedures, domain knowledge etc [82]. This memory can be in semantic [59], vector database [38], knowledge graph [4, 62] formats. The memory module is used by the agent so that it can recall relevant information at each step of executing a task. For instance, in recommendation scenarios, user preferences collected over multiple sessions can be stored in a memory module and retrieved for the task of personalizing the recommendations. This persistent memory is crucial for multi-turn recommendation dialogues, where the agent refines suggestions based on evolving user interests. [42, 80]

(4) <sub>Autonomy</sub> <sub>and</sub> <sub>Goal-Driven</sub> <sub>Behavior:</sub> LLM agent can be designed to be operated in “autonomously in a closed-loop fashion” to fulfill a goal. Given a target objective (for example “find a suitable product for a user”), the agent can be designed to autonomously (i) observe the environment (via tools or APIs), (ii) evaluate progress, (iii) evaluate the outcome of each step and do a self refine step (iv) continue until it deems the goal is achieved or no further action can be taken. This is unlike a static Q&A system, where the system merely focuses on the one-time query. [52, 72]

These components enable the LLM agent to tackle complex tasks in recommendation and retrieval settings. For instance, systems like <sub>RecMind</sub> [76] use LLM as a reasoning engine paired with a planning component, a long-term memory of user profiles, and retrieval tools to fetch relevant product information. The agent then autonomously analyzes a user’s needs and iteratively refines its suggestions. This is far more capable than a single-turn Q&A approach, as it can plan queries (e.g., to check product ratings or availability), incorporate user feedback, and adapt the recommendation strategy. Frameworks like “ReAct” [84] illustrate how an LLM can be prompted to alternate between “reasoning steps” and “action steps”, calling retrieval or recommendation APIs as needed. Other systems, such as “Toolformer” [64] and “HuggingGPT” [66] similarly integrate LLMs with external action interfaces.

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

## 2.4 What Is Not an LLM Agent

Not every LLM-based recommendation pipeline is agentic. A <sub>simple</sub> <sub>Q&A</sub> or <sub>single-prompt</sub> <sub>rec-</sub> <sub>ommendation</sub> system, such as an LLM prompted with “recommend five movies for this user”, is a generator or ranker, not an agent: it produces one response without persistent task state, autonomous tool choice, or iterative goal tracking. Similarly, a one-pass <sub>retrieval-augmented</sub> <sub>generation</sub> (RAG) system is a grounded generator, but not necessarily an agent, because the retrieve-thengenerate sequence is fixed rather than selected, repeated, or revised by the model. For example, a RAG recommender may retrieve product descriptions and generate an explanation, but it does not decide on its own to re-query the catalog, ask a clarifying question, or invoke a policy checker.

The litmus test for <sub>full</sub> autonomy is whether the system maintains task state and can execute an observe–plan–act–verify loop in which it chooses its own actions. In recommender systems, this means that the system can decide whether to retrieve additional item evidence, ask a clarifying question, update or query memory, revise a ranking, invoke a policy or constraint checker, or stop because the recommendation objective has been satisfied. By this test, simple Q&A, one-pass RAG, fixed prompt chains, and static LLM-as-ranker pipelines are not autonomous agents, because their steps, branching rules, stopping criteria, and tool calls are predetermined rather than selected at run time.

Autonomy, however, is only one of the four capabilities of Section 2.2, and it is useful to separate it from the others. Planning and task decomposition, specialization across roles, tool use, and memory can each be present in a system whose control graph is fixed in advance. Consider the birthday-planning example of Figure 1. One could implement it as a fixed pipeline that always retrieves cake candidates, then decoration candidates, then party favors, checks the assembled set for theme and dietary consistency, and finally ranks it, with this order wired in at design time. Such a pipeline still decomposes the goal into specialized subtasks, calls retrieval tools, and carries the gluten-free constraint forward as a piece of memory, yet it never decides on its own to reorder these steps, ask the user a new question, or stop early. We therefore treat “agentic” as graded rather than binary: this fixed-graph version is agentic in <sub>structure</sub>, through decomposition, specialization, tool use, and memory, while remaining non-autonomous in <sub>control</sub>. It becomes fully agentic only when embedded in a closed-loop controller that can maintain state, choose its next action, inspect intermediate outcomes, and adapt the process toward the goal, for example by deciding to elicit a missing dietary restriction before retrieval, or to re-run decoration retrieval after the user enlarges the cake.

This structure-versus-control distinction is not merely terminological. The two dimensions can be varied independently, and the controlled study of Section 6 exploits this by holding autonomy fixed and varying only structure, so that the contribution of decomposition, specialization, and aggregation to recommendation quality can be measured on its own.

In short, not all LLM-based pipelines are agentic, and among those that are, not all exercise the same capabilities. Simple Q&A, one-pass RAG, fixed prompt chains, and static LLM-as-ranker pipelines can be useful components of an agentic recommender but are not suficient on their own.

## 2.5 Scope: what is recommendation-specific in an agentic system?

An agentic recommender system contains both recommendation-specific and auxiliary components. We treat the following as core recommendation operations: candidate generation, evidence retrieval over user/item data, filtering and constraint satisfaction over item attributes, ranking and reranking, bundle or slate construction, explanation grounded in item and user evidence, feedback interpretation, memory update for personalization, and evaluation of recommendation utility. We treat natural-language parsing, generic task planning, tool routing, and user-interface generation as adjacent capabilities: they may be necessary to implement an agentic recommender, but they are not themselves suficient to constitute a recommendation contribution. This boundary matters because a multi-agent architecture can be impressive as an orchestration system while still failing at recommendation objectives such as relevance, diversity, calibrated personalization, fairness of exposure, or long-term user value.

Accordingly, throughout the paper we distinguish three layers: (i) the <sub>recommendation</sub> <sub>layer</sub>, responsible for user–item matching, ranking, and slate construction; (ii) the <sub>interaction</sub> <sub>layer</sub>, which manages dialogue, clarification, explanation, and preference elicitation; and (iii) the <sub>orchestration</sub> <sub>layer</sub>, which chooses tools, coordinates agents, manages memory, and verifies intermediate states. A system can be sophisticated at the interaction and orchestration layers yet add little at the recommendation layer, which is precisely the case the boundary above is meant to expose.

## 2.6 Positioning Relative to Non-Agentic and Agentic Recommenders

Table 2. Positioning of this paper relative to non-LLM, LLM-based, single-agent, and multi-agent recommender systems. • = explicit/central; △ = partial or emerging; ◦ = not central. Column meanings and the gap notes G1–G10 are given in the text.

<table><tr><td rowspan="2">Representative line / examples</td><td colspan="3">Agent role</td><td colspan="4">Agentic capability</td><td colspan="2">Evaluation</td><td rowspan="2">Gap</td></tr><tr><td>Assist.</td><td>Recomm.</td><td>Simul.</td><td>Memory</td><td>Tools / RAG</td><td>Planning</td><td>Coord.</td><td>Ranking</td><td>Trace</td></tr><tr><td colspan="11">Part I: Non-LLM recommender systems</td></tr><tr><td>Classical / sequential recommender systems [29, 32, 33, 63]</td><td>○</td><td>●</td><td>○</td><td>△</td><td>○</td><td>○</td><td>○</td><td>●</td><td>○</td><td>G1</td></tr><tr><td>Conversational / interactive recommender systems [11, 23]</td><td>△</td><td>●</td><td>○</td><td>△</td><td>△</td><td>△</td><td>○</td><td>●</td><td>△</td><td>G2</td></tr><tr><td colspan="11">Part II: LLM-based recommender systems, not explicitly agentic</td></tr><tr><td>LLM as encoder, ranker, reranker, or reasoning module [79, 93]</td><td>○</td><td>●</td><td>○</td><td>△</td><td>△</td><td>○</td><td>○</td><td>●</td><td>△</td><td>G3</td></tr><tr><td>Generative / prompt-based recommender systems [13, 39]</td><td>○</td><td>●</td><td>○</td><td>△</td><td>△</td><td>△</td><td>○</td><td>●</td><td>△</td><td>G4</td></tr><tr><td colspan="11">Part III: LLM-based recommender systems, single-agent</td></tr><tr><td>Agent-assisted recommender [31, 92]</td><td>●</td><td>△</td><td>○</td><td>●</td><td>●</td><td>●</td><td>○</td><td>●</td><td>△</td><td>G5</td></tr><tr><td>Agent-as-recommender [76]</td><td>△</td><td>●</td><td>○</td><td>●</td><td>●</td><td>●</td><td>○</td><td>●</td><td>△</td><td>G6</td></tr><tr><td>Agent-as-user-simulator [9, 75, 89]</td><td>○</td><td>○</td><td>●</td><td>●</td><td>△</td><td>●</td><td>○</td><td>△</td><td>●</td><td>G7</td></tr><tr><td colspan="11">Part IV: LLM-based recommender systems, multi-agent</td></tr><tr><td>Multi-agent agent-assisted recommender [17, 77]</td><td>●</td><td>△</td><td>○</td><td>●</td><td>●</td><td>●</td><td>●</td><td>●</td><td>●</td><td>G8</td></tr><tr><td>Multi-agent agent-as-recommender [77, 90]</td><td>△</td><td>●</td><td>○</td><td>●</td><td>●</td><td>●</td><td>●</td><td>●</td><td>△</td><td>G9</td></tr><tr><td>Multi-agent user / environment simulation [5, 75]</td><td>○</td><td>○</td><td>●</td><td>●</td><td>△</td><td>●</td><td>●</td><td>△</td><td>●</td><td>G10</td></tr><tr><td colspan="11">Part V: This paper</td></tr><tr><td>Unified RecSys-specific framework and evaluation agenda</td><td>●</td><td>●</td><td>●</td><td>●</td><td>●</td><td>●</td><td>●</td><td>●</td><td>●</td><td>-</td></tr></table>

Sections 2.1 through 2.5 defined an agentic recommender system, separated it from LLM pipelines that are not agentic (Section 2.4), and bounded it against orchestration that is not recommendation specific (Section 2.5). We close the section by placing this definition on the map of existing work. Table 2 organizes representative lines of research along three axes. The <sub>agent</sub> <sub>role</sub> axis records whether the agent assists an existing recommender (Assist.), acts as the recommender (Recomm.), or simulates users and environments (Simul.). The <sub>agentic</sub> <sub>capability</sub> axis records explicit memory (working/episodic/semantic/procedural), tool or retrieval use (Tools/RAG), planning or plan–act– verify behavior, and inter-agent coordination (Coord.). The <sub>evaluation</sub> axis records whether a line is assessed only on final ranking quality (HR@K, NDCG@K, MRR, diversity, exposure) or also on the intermediate agent trace (evidence grounding, memory use, tool correctness, judge reliability, communication cost, latency, and failure attribution). These axes separate three issues that are often conflated: that a system may use an LLM without being agentic, that an agentic recommender may difer in role and in which capabilities it exercises, and that evaluation may stop at the ranked list or extend to the trace. The table therefore makes precise why this paper is neither a survey of LLM-based recommendation nor a generic multi-agent-system discussion, but a RecSys-specific framework for specifying and evaluating agentic recommendation architectures.

The capability columns correspond directly to the primitives of the formal framework: Memory is the store <sub>Ω</sub> with its operators <sub>U</sub> and <sub>Q</sub> (Definitions 2.3 and 2.4), Tools/RAG is the function set <sub>F</sub> of Definition 2.1, Planning is the decomposition behavior of Section 2.2, and Coordination is the protocol <sub>Π</sub> of the MAS triple (Definition 2.2). The rows then trace a progression, and the Gap column names what each stage still leaves open. Classical and sequential recommenders (G1) provide strong ranking foundations but expose no agent loop, and conversational recommenders (G2) are interactive yet usually scripted rather than tool-using and memory-bearing. LLM-based but non-agentic recommenders improve representation, ranking, or generation while remaining inside fixed pipelines, so autonomy and tool choice stay implicit (G3, G4). Single-agent systems introduce memory, tools, and planning, but agent-assisted designs lack inter-agent specialization (G5), agentas-recommender designs often leave the memory, tool, and planning contributions under-ablated (G6), and agent-as-simulator designs face fidelity, calibration, and label-leakage dificulties (G7). Multi-agent systems add coordination through <sub>Π</sub>, yet the marginal utility and cost of extra agents is rarely attributed (G8), decomposition and verification raise communication complexity (G9), and richer simulation can amplify artificial behavior or simulator drift (G10). The final row marks the gap this paper targets: a unified, recommender-specific vocabulary and evaluation agenda in which agentic complexity is justified through measurable gains in recommendation quality, grounding, trace reliability, fairness, cost, and robustness rather than assumed, with the under-ablation gaps G6 and G8 addressed empirically in Section 6.

## 3 Memory Storage and Retrieval Mechanisms

Due to importance of memory mechanisms in agentic systems, especially those anchored toward recommender system tasks we will discuss these mechanisms in a dedicated section. Large Language Model (LLM) agents require robust memory mechanisms to behave coherently over time. By default, an LLM is stateless, which means that each query is processed independently, with no built-in recall of previous interactions. This stateless design is a serious issue in hindering LLMs to be adapted to recommendation tasks requiring personalization and “remembering” things about users.

To overcome this, agent frameworks introduce explicit memory systems that let the agent “remember” and reuse information from past events or dialogues. Broadly, these memories fall into short-term (working memory) and long-term categories, with further distinctions (episodic, semantic, procedural, etc.) inspired by human cognition. This section surveys the types of memory in LLM agents and the storage/retrieval mechanisms.

## 3.1 Types of Memory in LLM Agents

<sub>3.1.1</sub> <sub>Short-Term</sub> <sub>(Working)</sub> <sub>Memory.</sub> Short-term (often called “working” [24]) memory refers to the transient context the agent holds in mind. In an LLM agent, this corresponds to the recent interaction history or “context window” provided to the model on each turn. It is analogous to human working memory in that it is readily accessible but of limited capacity (bounded by token length) [65]. For instance, a chatbot’s short-term memory might include the last few user prompts and agent responses, allowing for conversational coherence. Short-term memory is therefore crucial for immediate reasoning, but it does not persist beyond the current session (i.e., it lacks a true long-term store).

<sub>3.1.2</sub> <sub>Long-Term</sub> <sub>Memory.</sub> Long-term memory provides persistent recall across interactions and over time. In agent systems, it can be subdivided into:

<sub>Episodic</sub> <sub>Memory</sub> Episodic memory pertains to specific events or experiences (<sub>episodes</sub>) the agent has encountered. In LLM agents, this often means a stored log of past dialogues, observations, or actions, coupled with context such as timestamps or metadata. It is context-rich and instancespecific. In this case, the agent remembers not just <sub>what</sub> happened, but <sub>when</sub> and <sub>under</sub> <sub>what</sub> circumstances <sup>[22].</sup> <sup>For</sup> <sup>instance,</sup> <sup>the</sup> <sup>agent</sup> <sup>might</sup> <sup>recall:</sup> Last week the user asked about Italian <sub>restaurants</sub> <sub>and</sub> <sub>I</sub> <sub>recommended</sub> <sub>XYZ.</sub> Episodic memory supports one-shot learning of events and explicit recall of past episodes, and some researchers argue it is a key missing piece for truly long-lived LLM-based agents. [59]

<sub>Semantic</sub> <sub>Memory</sub> Semantic memory stores general facts, concepts, or knowledge about the world, akin to the “know-what.” In LLM agents, semantic memory might be an external knowledge base or database of facts (e.g., “in my retrieval system TVs are categorized under electronics category”) [88].

While much semantic knowledge is encoded in the LLM’s pretrained weights, agents can also maintain explicit semantic stores (relational databases, knowledge graphs, etc.) for dynamic updates. Semantic memory is <sub>long-term</sub> and <sub>explicit</sub>, though it abstracts away the specific instance in which a fact was learned [35]. For example, from several chats the agent might distill a high-level fact: “This user prefers Italian cuisine.”

<sub>Procedural</sub> <sub>Memory</sub> Procedural memory, or the “know-how”, refers to skills or procedures the agent has learned to execute without needing to deliberate each time. For an LLM agent, this might appear as learned prompts, scripts, or code snippets that automate common tasks (e.g., connecting to a database). [71, 78]

Procedural memory is typically implicit in that it is not stated as factual knowledge but manifested as rules or sequences of actions. It allows the agent to execute tasks more eficiently, refining these skills through repeated practice. Early cognitive architectures like SOAR [34] used production rules to represent procedural knowledge, and modern LLM agents similarly encode procedural behaviors through fine-tuned prompts, scripted tool invocations, or learned action sequences that mimic rule-based execution pipelines[12, 53]. In the next subsection, we explore how these diferent types of memory are realized in the actual agentic recsys implementations.

## 3.2 Memory Storage and Retrieval Mechanisms

Large-context LLMs can “remember” only a few thousand tokens per forward pass, yet real recommender deployments routinely span months of user interaction and terabytes of product data. Consequently, an <sub>agentic</sub> recommender must decide “what” to store externally, “how” to distil it, and “which” fragments to re-inject into the prompt at inference time. We formalise these operations through the <sub>Memory</sub> <sub>Update</sub> and <sub>Memory</sub> <sub>Retrieval</sub> functions (Definitions 2.3–2.4), then survey concrete storage modalities. For having a more complete survey of the memory mechanisms, first we state the following definitions.

Definition 3.1 (Memory Item). <sup>A</sup> memory item <sup>is</sup> <sup>a</sup> <sup>triple</sup> $m = ( k , v , \varsigma )$ where

(i) $\boldsymbol { k } \in \mathbb { R } ^ { d _ { k } }$ is the <sub>key</sub>, typically an ??-gram embedding or hashed identifier that serves as the retrieval handle;

(ii) $\boldsymbol { v } \in \mathbb { R } ^ { d _ { v } }$ is the <sub>value</sub> payload that preserves the semantic content (natural-language text or a dense vector);

(iii) $\varsigma = ( t , \ell , u )$ is a metadata tuple storing the time-stamp ??, a logical label ℓ <sub>∈</sub> <sub>{</sub>EPI, SEM, PROC<sub>}</sub> distinguishing <sub>episodic</sub>, <sub>semantic</sub>, or <sub>procedural</sub> memory, and an update counter ?? that tracks how often the item has been modified.

For instance, in our cake retrieval example, the statement of the user for gluten allergy, “<sub>guest\_allergy</sub> $\boldsymbol { \mathbf { \rho } } = \mathsf { g l u t e n } ^ { \boldsymbol { \mathsf { w } } }$ is stored as

$$
k = \text {embedding} (“ \text {gluten allergy} ”), \quad v = “ \text {gluten} ”, \quad \varsigma = (t = 1 7: 4 5, \ell = \text {EPI}, u = 1).
$$

Here ?? is an embedding representation of the key “gluten allergy”; $\ell = \mathrm { E P I }$ signals that the fact is tied to a specific party event rather than a timeless preference.

The key–value–metadata form in Definition 3.1 is an analytic wrapper, not a restriction on implementation. The value field may contain raw text, dense embeddings, symbolic triples, rela tional rows, procedural scripts, multimodal features, pointers to external stores, or other memory representations. The purpose of the wrapper is to expose the three pieces of information that agentic recommendation needs from any stored item: a retrieval handle, a semantic payload, and metadata for recency, provenance, privacy, and update control. In a recommender these metadata fields are not incidental bookkeeping. The timestamp ?? determines whether a preference is still current or stale, the label ℓ separates a one-of event such as a party constraint from a durable taste, and the update counter ?? records how often a fact has been reinforced, which is exactly the signal needed to decide whether a preference is worth conditioning a ranking on.

Definition 3.2 (Relevance Scoring). <sup>Given</sup> <sup>a</sup> <sup>task</sup> <sup>query</sup> $\tau \in \mathcal { T }$ and a memory item $m = ( k , v , \varsigma )$ , a relevance function

$$
S: \mathcal {T} \times (\mathcal {X} \times \widetilde {\mathcal {X}} \times \mathbb {R} ^ {3}) \longrightarrow \mathbb {R} _ {\geq 0},
$$

returns a non-negative score. Retrieval (Definition 2.4) selects the ?? highest-scoring items:

$$
\widehat {C} = \mathrm{Top-K} _ {m \in \Omega} S (\tau , m).
$$

Again, back to our cake retrieval example, let $\tau = { ^ { \ast } } \mathsf { f }$ ind gluten-free chocolate cake<sup>”.</sup> <sup>Then,</sup> we can choose the relevance function in a form like $S ( \tau , m ) = \cos ( \mathrm { e m b e d d i n g } ( \tau ) , k )$ . The cosine term elevates items semantically close to the query. Consequently, the system surfaces the allergy item and the child’s flavor preference, but not unrelated recommendation traces.

In a recommender, topical similarity alone is an impoverished relevance function. What should be recalled for a ranking or explanation sub-goal depends not only on whether a memory item is semantically close to $\tau ,$ but on whether it is still valid, whether it encodes a binding constraint, and whether it is permitted to be used. A useful ?? for agentic recommendation therefore combines the similarity term above with the metadata of Definition 3.1: a recency weight derived from ?? so that abandoned preferences decay, a label term from ℓ so that hard constraints (a dietary restriction, a returned item) are retrieved with priority over soft tastes, and a privacy gate that excludes items the user has asked to delete. This is what distinguishes memory relevance in a recommender from generic semantic search: the highest cosine score is not always the item that should condition the next ranking.

Now, we will review diferent modalities that memory store/retrieve can take.

<sub>3.2.1</sub> <sub>Raw</sub> <sub>Text</sub> <sub>Logs.</sub> The simplest store is an <sub>append-only</sub> transcript $\Omega ^ { \mathrm { r a w } } = [ m _ { 1 } , . . . , m _ { T } ]$ , where each $m _ { t }$ is the verbatim turn text. Retrieval is concatenation of the last ?? tokens: $\widehat { C } = \mathrm { T a i l } _ { L } \left( \Omega ^ { \mathrm { r a w } } \right)$ Although the update function (Definition 2.3) <sub>U</sub> is trivial (append), this scales poorly and prompt length soon exceeds the model window. [3, 43]

<sub>3.2.2</sub> <sub>Summarisation</sub> <sub>(Compression).</sub> In this approach, older logs are periodically compressed into shorter summaries. More specifically, update function <sub>U</sub> invokes an LLM summariser, $\mathcal { R } _ { \mathrm { s u m } }$ $C _ { t } \to \widetilde { C } _ { t }$ , which compresses $C _ { t }$ to a more concise context $\widetilde { C } _ { t }$ . The agent then stores and retrieves these summaries to preserve essential information. Though it saves tokens, the fidelity of recall depends on the quality of summarization. Recent memory compression methods enable adaptive summarization and storage of long conversational histories for LLM agents [40].

<sub>3.2.3</sub> <sub>Embedding</sub> <sub>and</sub> <sub>Vector</sub> <sub>Databases.</sub> For long-term memory, the prevailing method in retrievalaugmented generation (RAG) is embedding-based storage. Each memory item is encoded as a high-dimensional vector (using an embedding model ??) $k = e ( \boldsymbol { v } )$ ?? <sub>=</sub> (raw text) and stored in a vector database [21, 86]. For Retrieval, using the retrieval function $\boldsymbol { Q }$ (see Definition 2.4) the current query is embedded, and nearest-neighbor search surfaces semantically relevant items, enabling large-scale, flexible recall—though typically at the cost of strict chronological ordering. Please note that classic retrieval-augmented models RETRO [6] and REALM [25] demonstrate the scalability and efectiveness of such large-scale external memory designs.

The choice among these modalities is a recommendation-deployment decision, not only an engineering one. Vector stores scale to catalog- and user-history sizes and tolerate fuzzy recall, which suits personalization, but they blur chronology, which matters when the order of a $\mathrm { { u s e r } } ^ { \prime } s$ interactions carries intent. Raw logs and summaries preserve session dynamics but do not scale to months of history. Structured stores enforce the hard constraints and provenance that policy compliant recommendation requires. In practice an agentic recommender mixes them by role: short-term session state in a bufer, durable tastes in a vector store, and constraints and provider or policy facts in a structured store where they can be checked exactly.

<sub>3.2.4</sub> <sub>Knowledge</sub> <sub>Graphs</sub> <sub>/</sub> <sub>Structured</sub> <sub>Stores.</sub> Beyond raw text or vector embeddings, an agent may persist “knowledge–graph memory” in the form of symbolic triples $( s , r , o )$ (subject–relation–object) or relational table rows that can be queried explicitly via SQL or SPARQL. Symbolic storage is particularly well-suited for semantic memory: it supports precise retrieval, logical entailment, and integrity constraints, albeit at the cost of additional curation.

<sub>Definition</sub> <sub>3.3</sub> <sub>(Symbolic</sub> <sub>Memory</sub> <sub>Item).</sub> A symbolic memory item augments Definition 3.1 by taking $m = ( k , v , \varsigma )$ with $v = ( s , r , o ) \in \mathcal { E } ^ { 3 }$ , where <sub>E</sub> is the entity set of the knowledge graph. In other words, the value can be of the form subject–relation–object for a given query. Equivalently, one can assume an embedding on the triplet for key retrieval used for approximate nearest-neighbour fallback.

For example, suppose the assistant stores $\boldsymbol { v } = \left( \mathrm { u } \boldsymbol { s } \mathrm { e r } \right.$ <sup>,</sup> likes<sup>,</sup> chocolate) <sup>with</sup> <sup>label</sup> $\ell = { \mathrm { S E M } } .$ Given user query $\tau = { } ^ { * } \mathbf { V }$ What flavour cake should I order?” the system formulates <sub>(user</sub>, <sub>likes</sub>, ??<sub>)</sub> and retrieves the triple, yielding the concrete value <sub>chocolate</sub>. If no exact match exists, the agent can still fall back to the embedding key ?? <sub>=</sub> embedding<sub>(user</sub>, <sub>likes</sub>, <sub>·)</sub> and perform a vector search for semantically close preferences.

Symbolic knowledge graph/structured stores ofer high-precision constraints and explainable provenance [45], but demand manual or automated pipelines to populate and maintain the triples; they also introduce schema-evolution overhead when the domain ontology changes. [85]

<sub>3.2.5</sub> <sub>Parametric</sub> <sub>Memory</sub> <sub>Updates.</sub> A costly alternative is to integrate $\widetilde { C } _ { t }$ directly into the backbone parameters of the LLM model [19]. Formally, the update function <sub>U</sub> returns a new language model $\boldsymbol { \mathcal { M } } _ { t + 1 } = \boldsymbol { \mathcal { M } } _ { t } \oplus \boldsymbol { \Delta } _ { t }$ , where $\textstyle { \mathcal { M } } _ { t }$ represents the model at time ?? and $\Delta _ { t }$ represents the update on the model to incorporate the new events. This makes <sub>Ω</sub> implicit in <sub>M</sub>. Latency and safety constraints limit real-time use [10, 20].

Regulated Context Windows. <sup>In</sup> <sup>production,</sup> <sup>agents</sup> <sup>often</sup> <sup>blend</sup> procedural<sup>,</sup> episodic<sup>,</sup> <sup>and</sup> semantic memories with a regulator:

$$
\widehat {\mathcal {C}} = \widehat {\mathcal {C}} _ {\mathrm{PROC}} \cup \widehat {\mathcal {C}} _ {\mathrm{SEM}} \cup \widehat {\mathcal {C}} _ {\mathrm{EPI}},
$$

Table 3. Use cases for agentic recommender systems. The table summarizes the four representative scenarios developed in Section 4, the practical trigger for using an agentic design, the recommendation-layer gain, and when a simpler non-agentic baseline may be suficient.

<table><tr><td>Use case</td><td>Agentic trigger</td><td>Recommendation-layer gain</td><td>Simpler baseline may suffice when</td></tr><tr><td>Interactive goal-oriented recommendation</td><td>Clarification, planning, memory, and bundle verification</td><td>Improves constraint satisfaction, bundle coherence, ranking quality, personalization, and user effort in multi-turn recommendation.</td><td>The request is a single well-scoped query with a stable user profile and fixed candidate set.</td></tr><tr><td>User simulation and evaluation</td><td>Synthetic users, logging, evaluators, and session summarization</td><td>Supports offline stress testing, counterfactual diagnosis, robustness checks, and evaluation before live deployment.</td><td>Reliable logged feedback is already available and no interactive trajectory or simulated behavior needs to be modeled.</td></tr><tr><td>Contextual and multimodal recommendation</td><td>Vision tools, external retrieval, memory, and consistency checks</td><td>Connects images, context, metadata, user preferences, and spatial or aesthetic constraints to ranking and bundle construction.</td><td>All relevant features are already structured and can be consumed directly by a conventional ranker.</td></tr><tr><td>Grounded recommendation explanation</td><td>Evidence retrieval, critic/evaluator agents, and policy checks</td><td>Produces explanations that are more faithful, evidence-backed, policy-consistent, and less prone to unsupported claims.</td><td>A short template explanation is sufficient and dynamic evidence or policy checking is unnecessary.</td></tr></table>

subject to a token budget $\left| \widehat { C } \right| \leq B \left[ 8 1 \right]$ . We can formalize this type of regulator as a knapsack problem (see [51]) variant

$$
\begin{array}{c} \max _ {\widehat {C} \subseteq \Omega} \sum_ {m \in \widehat {C}} S (\tau , m) \\ \text {s.t.} \sum_ {m} | m | \leq B. \end{array}
$$

where $S ( \tau , m )$ is the relevance score as defined in definition 3.2, <sub>|</sub>??<sub>|</sub> is the length of the retrieved memory, and ?? is the token budget.

The foregoing definitions and examples demonstrate that memory in agentic recommender systems is no longer a monolithic cache but a spectrum of interlocking mechanisms—from raw transcript bufers and lossy summaries to vector stores to fully structured knowledge graphs, to budgeted tokens. By casting memory operations as explicit update <sub>U</sub> and retrieval <sub>Q</sub> functions, parameterised by relevance scores and symbolic query semantics, we obtain a principled foundation for analyzing capacity, latency, and factual fidelity. Yet the formalism also exposes substantial gaps: adaptive compression that preserves downstream utility is still heuristic; relevance scoring lacks theoretical guarantees; and symbolic stores incur unsolved curation and schema-evolution costs. Bridging these gaps will require new learning objectives that couple retention with task performance, tighter integration of uncertainty calibration into retrieval, and hybrid architectures that combine the precision of knowledge graphs with the scalability of dense embeddings. For recommendation specifically, these gaps surface as measurable failure modes: compression that drops a binding constraint, relevance scoring that resurfaces a stale preference, and retrieval that returns a deleted trace. The memory-correctness, staleness, and deletion-compliance signals of Section 5 are intended to quantify exactly these failures. In short, memory for LLM-driven, multi-agent RecSys is both a critical enabler and an open frontier, inviting further research at the intersection of information retrieval, knowledge representation, and large-scale language modeling.

## 4 Agentic Recommendation Task Families

The remainder of this section grounds the general agentic framework in four representative use cases, each chosen to illuminate a distinct facet of next-generation recommender systems. As summarized in Table 3, these examples are not intended to be exhaustive; rather, they show when planning, memory, tool use, verification, or multi-agent coordination can improve recommendationlayer outcomes, and when a simpler non-agentic baseline may be suficient.

## 4.1 Interactive Recommendation

Formal Task Definition. <sup>We</sup> <sup>define</sup> Interactive Recommendation <sup>as</sup> <sup>the</sup> <sup>problem</sup> <sup>setting</sup> <sup>in</sup> <sup>which</sup> <sup>an</sup> agent (or a set of collaborating agents) engages in a multi-turn dialogue with a user to identify, refine, and present suitable recommendations. Unlike static recommender systems that rely on one-shot user inputs, interactive recommendation leverages iterative exchanges to incorporate user feedback, contextual constraints, and additional information drawn from memory or external resources. The overarching objective is to dynamically adapt suggestions as the conversation evolves, thereby providing a more personalized and contextually appropriate set of recommendations.

Let <sub>D</sub> be the space of dialogue turns and <sub>S</sub> the universe of documents (in an eCommerce setting these can be purchasable stock-keeping units, SKUs). A user session at step ?? is characterised by the partial transcript

$$
C _ {1: t} = (d _ {1}, a _ {1}, \dots , d _ {t - 1}, a _ {t - 1}, d _ {t}),
$$

where $d _ { i } \in \mathcal { D }$ is a user utterance and $a _ { i } \in \mathcal { D }$ <sup>the</sup> <sup>agent</sup> <sup>reply.</sup> <sup>Define</sup> <sup>the</sup> interactive recommendation <sub>task</sub> as a mapping

$$
\Phi : \left(\mathcal {C} _ {1: t}, \mathcal {E}\right) \longrightarrow \left\langle s _ {(1)}, \dots , s _ {(L)} \right\rangle ,
$$

that outputs a ranked list of ?? items with the maximal expected utility $\begin{array} { r } { \sum _ { j = 1 } ^ { L } \operatorname { R e l } \left( s _ { \left( j \right) } \ \mid \ C _ { 1 : t } \right) } \end{array}$ conditioned on user constraints (theme, dietary rules, budget) implicitly encoded in $C _ { 1 : t }$

To illustrate this task, we consider the scenario of planning a Mickey Mouse-themed birthday party as shown in Figure 1. A parent consults the system to select decorations, arrange a suitable cake, and accommodate guests’ dietary restrictions. The agent aims to guide the parent through each step, from confirming the child’s preferences (such as color schemes or favorite cake flavors) to identifying any special requirements. By interacting iteratively with the user and retrieving relevant information from its memory and external tools, the agent can refine its suggestions over time.

<sub>High-level</sub> <sub>goal.</sub> The agent must <sub>adaptively</sub> <sub>refine Φ</sub> through multi-turn dialogue, spawning specialized sub-agents and tool calls to satisfy latent sub-goals (e.g. “select gluten-free chocolate cake”, “choose decor consistent with Mickey-Mouse palette”) while preserving conversational coherence and minimizing user efort.

<sub>System</sub> <sub>architecture</sub> <sub>and</sub> <sub>agent</sub> <sub>setup.</sub> For this specific example, we can instantiate a multi-agent system

$$
\mathrm{MAS} _ {\mathrm{party}} = \big (\mathcal {A}, \mathcal {E}, \Pi \big),
$$

<sup>where</sup> Agent set $\mathcal { A } \ = \ \{ A _ { \mathrm { c h a t } } , A _ { \mathrm { e p i } } , A _ { \mathrm { n l i } } , A _ { \mathrm { S A C } } , A _ { \mathrm { c a k e } } , A _ { \mathrm { d e c o r } } , A _ { \mathrm { f a v o r } } , A _ { \mathrm { c o l \_ c h e c k } } , A _ { \mathrm { r a n k } } \}$ . Each $A _ { i }$ is an LLM agent in the sense of Definition 2.1. Where

$A _ { \mathrm { c h a t } }$ (chat agent) primary interface to the user.

$A _ { \mathrm { e p i } }$ – episodic retrieval using <sub>Q</sub> (Definition 2.4).

• $A _ { \mathrm { n l i } }$ – natural-language inference to vet relevance of retrieved episodes.

$A _ { \mathrm { S A C } }$ – specialised-agent caller that spawns three micro-MAS blocs: $\{ A _ { \mathrm { c a k e } } , A _ { \mathrm { d e c o r } } , A _ { \mathrm { f a v o r } } \}$ for category-specific retrieval.

$A _ { \mathrm { c o l \_ c h e c k } }$ – collection-level consistency.

$A _ { \mathrm { r a n k } } -$ personalised ranking & presentation.

Also one can define the Environment for this MAS as:

<sub>E</sub> <sub>=</sub> <sub>(</sub>ProductCatalogue, UserProfileDB, VectorDB, LayoutTool<sub>)</sub>,

and communication protocol as $\boldsymbol { \Pi } = ( \mathbf { C } , \boldsymbol { \Gamma } )$ where $\mathbf { C } _ { i j } = 1$ if either $A _ { j }$ is a child spawned by $A _ { i }$ or $A _ { i } { = } A _ { \mathrm { c h a t } } . \Gamma$ contains message types <sub>{</sub>query, episode\_list, tool\_call, item\_set, ranked\_list<sub>}</sub>.

The following also illustrates communication sketch:

$$
\begin{array}{c} A _ {\text {chat}} \xrightarrow {\text {query}} A _ {\text {epi}} \xrightarrow {\text {episode\_list}} A _ {\text {nli}} \xrightarrow {\text {validated\_episodes}} A _ {\text {SAC}} \\ \xrightarrow {\text {spawn}} \{A _ {\text {cake}}, A _ {\text {decor}}, A _ {\text {favor}} \} \xrightarrow {\text {item\_set}} A _ {\text {col\_check}} \xrightarrow {\text {validated\_set}} A _ {\text {rank}} \xrightarrow {\text {ranked\_list}} A _ {\text {chat}}. \end{array}
$$

Note that <sub>spawn</sub> can be autonomous depending on ??

<sub>Memory</sub> <sub>and</sub> <sub>tool</sub> <sub>requirements.</sub> Now, we illustrate how each type of memory is defined here and how each agent can utilize it. Short-term (Working) memory can be defined for $A _ { \mathrm { c h a t } }$ that takes logs of last ?? turns of the $C _ { 1 : t } .$ . Episode store can be accessed and manipulated by $A _ { \mathrm { e p i } }$ through <sub>U</sub> and <sub>Q</sub>. Semantic memory $\Omega ^ { \mathrm { S E M } }$ can track stable user traits (preferred colours, dietary restrictions). $\Omega ^ { \mathrm { P R O C } }$ can include repeatable prompt templates for each retrieval block as well as information about each table in DB so that agents can autonomously query them or other elements of environment <sub>E</sub>. External Tools $\mathcal { F }$ <sup>in</sup> <sup>this</sup> <sup>MAS</sup> <sup>are</sup> SearchCakeAPI<sup>,</sup> SearchDecorAPI<sup>,</sup> SearchFavorAPI<sup>,</sup> VectorDB.query <sup>(semantic</sup> <sup>retrieval),</sup> LayoutTool.generate <sup>(graphic</sup> <sup>board</sup> <sup>of</sup> decor set).

Benefits and discussion. <sup>The</sup> <sup>architecture</sup> <sup>realises</sup> interactive recommendation <sup>by</sup> <sup>decomposing</sup> <sup>a</sup> fuzzy, high-level goal (“celebrate my child’s Mickey-Mouse birthday”) into tractable sub-tasks handled by specialised agents. Key advantages like (i) Modularity, where each retrieval block is itself a micro-MAS that can be re-used for other party themes or plugged into A/B tests without retraining the entire pipeline. (ii) Memory-aware personalisation, where episodic retrieval $( A _ { \mathrm { e p i } } )$ injects user- and session-specific constraints (gluten-free, colour palette) while semantic memory supplies timeless preferences, yielding recommendations that are both relevant and surprising. (iii) Error containment, where the NLI validator and collection-consistency agent act as <sub>fact</sub> <sub>gates</sub>, reducing hallucination propagation by rejecting items that violate theme constraints or dietary rules, (iv) autonomy, where the specialised-agent caller spawns retrieval workers on demand and per query, and (v) Rich user experience where the final ranked set, together with a layout generated by <sub>LayoutTool</sub>, ofers a cohesive shopping board, demonstrating how agentic orchestration can move beyond single-item suggestions to holistic, story-driven recommendations.

Collectively, the design illustrates how the formal primitives—MAS, <sub>U</sub>, <sub>Q</sub>, and typed memory stores—translate into a concrete, deployable pipeline for next-generation conversational shopping assistants, which far exceeds the capabilities of classic recommender systems.

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

## 4.3 Contextual and Multi-Modal Recommendation

<sub>Formal</sub> <sub>definition</sub> <sub>of</sub> <sub>the</sub> <sub>task.</sub> We define the task as the process of generating suggestions that incorporate diverse forms of input, such as text descriptions, user interaction histories, and images depicting the user’s physical or aesthetic environment. For instantiation, let $\mathbf { x } \in \mathcal { T }$ denote textual constraints (e.g. “Bohemian, earthy colours”), $\textbf { v } \in \ \mathcal { V }$ a set of one or more images encoding spatial context, and <sub>u</sub> $\in N$ a latent user–profile vector drawn from long-term memory. We model contextual, multi-modal recommendation as a mapping

$$
\mathcal {R} _ {\phi}: (\mathbf {x}, \mathbf {v}, \mathbf {u}) \longrightarrow \widehat {\mathbf {y}} = \left\langle s ^ {1}, s ^ {2}, s ^ {3}, \dots \right\rangle ,
$$

where each $s ^ { ( \cdot ) } \in S$ is a SKU and the ranked tuple $\widehat { \mathbf { y } }$ maximises joint relevance $\begin{array} { r } { \sum _ { i } \operatorname { R e l } ( s _ { i } \mid \mathbf { x } , \mathbf { v } , \mathbf { u } ) } \end{array}$ subject to <sub>complementarity</sub> and <sub>aesthetic-coherence</sub> constraints. The latter can be enforced by an auxiliary predicate Compat<sub>(y)</sub> <sub>=</sub> 1 if all selected items harmonise in palette and style, or any Coherence Score <sup>mechanism.</sup>

![](images/b416314d6338a3258f3a1550b80aca702ebd1dd7310a384bc679ae97b5678bfb.jpg)  
Fig. 3. An example of multi-agent pipeline for multi-modal recommendation.

<sub>High-level</sub> <sub>goal.</sub> In many practical scenarios, recommendations cannot rely solely on textual inputs. A user interested in redecorating a living room may upload one or more photographs depicting the current layout, along with a brief description of desired styles (e.g., Bohemian, minimalist, rustic-see Figure 3). The system must analyze these images to identify available space, prevailing color palettes, and aesthetic elements, while also taking into account prior user behavior or known preferences (such as a history of purchasing similar items). By combining textual context with visual analysis, a multi-modal recommender can produce more cohesive suggestions, reduce guesswork, and streamline the user’s decision-making process. The ambition in an example orchestration is to replicate a professional interior-designer workflow while eliminating iterative, item-by-item searches.

System architecture and agent setup. The pipeline in Fig. 3 is formalised as $\mathrm { M A S } _ { \mathrm { m m } } = \left( \mathcal { A } , \mathcal { E } , \Pi \right)$ with

$$
\mathcal {A} = \left\{A _ {\text { chat }}, A _ {\text { image }}, A _ {\text { history }}, A _ {\text { cat }}, A _ {\text { caller }}, A _ {\text { ThemChk }}, A _ {\text { compChk }}, A _ {\text { collect }} \right\}.
$$

A single conversation unfolds as follows. The chat agent $A _ { \mathrm { c h a t } }$ receives $( \mathbf { x } , \mathbf { v } )$ and forwards the image to $A _ { \mathrm { i m a g e } }$ , which extracts palette vector <sub>p</sub> and spatial afordances via a vision backbone $\mathcal { F } _ { \mathrm { l a y o u t } } \in \mathcal { F }$ Concurrently, $A _ { \mathrm { h i s t o r y } }$ retrieves $\widehat { C } _ { \mathrm { S E M } } \subset \Omega ^ { \mathrm { S E M } }$ , stable style and budget preferences, using the retrieval operator <sub>Q</sub>. The specialised-retrieval caller $A _ { \mathrm { c a l l e r } }$ fuses $\mathbf { x } , \mathbf { p } , \widehat { C } _ { \mathrm { S E M } }$ and outputs a set of target classes like ?? <sub>= {</sub>chair, sofa, lamp<sub>}</sub>. For each $c \in C _ { \mathrm { { i } } }$ it spawns an intra-session micro-MAS. The resulting candidate lists are concatenated and passed to $A _ { \mathrm { T h e m C h k } }$ , which rejects items violating user history (e.g. bans leather if the user is vegan). $A _ { \mathrm { { c o m p C h k } } }$ then checks for complementarity score for the bundle of recommended items (maybe through solving mixed integer program). Finally, $A _ { \mathrm { c o l l e c t } }$ ranks the surviving set by personalised utility and calls $\mathcal { F } _ { \mathrm { r e n d e r } }$ to generate an on-image mock-up before handing results back to $A _ { \mathrm { c h a t } }$

The protocol’s communication matrix <sub>C</sub> is sparse. For instance, $A _ { \mathrm { c h a t } }$ may message any agent, but checker agents communicate only downstream, preventing cyclic justification loops that might amplify hallucinations.

![](images/0333a102a3cb530da2015e8cf0b4b923b9bc4915dd82f47afaad670d2ef3dcbe.jpg)  
Fig. 4. A sample of coherent (Boho style with earthy colors) multi-category recommendation (courtesy <sup>ikea.</sup> com<sub>).</sub>

<sub>Memory</sub> <sub>and</sub> <sub>tool</sub> <sub>requirements.</sub> Short-term bufers hold the live prompt plus extracted palette vectors; $\Omega ^ { \mathrm { S E M } }$ caches enduring preferences (colour, material, budget); $\mathbf { \dot { \Omega } } _ { \Omega } \mathbf { E } \mathbf { \hat { P } } \mathbf { I }$ stores prior styling sessions so that the system can avoid repetitious suggestions. Key tools are the vision encoder, a vector-search API over ProductDB, and a layout renderer that embeds selected SKUs into the uploaded photograph.

<sub>Benefits</sub> <sub>and</sub> <sub>discussion.</sub> The multi-modal MAS realises a “one-shot designer” experience. Semantic and complementarity checks decouple <sub>rule</sub> <sub>compliance</sub> from <sub>aesthetic</sub> <sub>harmony</sub>, yielding recom mendations that are both on-brand and visually pleasing. Finally, because the agent caller can spawn modular micro-MAS blocks live, the system stays flexible to a variety of user requests. In sum, contextual and multi-modal recommendation showcases how LLM-powered agents, external vision tools, and structured memories can collaborate to deliver designer-level curation in a single interactive session. Like the previous use case, this enables a capability beyond classic recommender systems.

![](images/c4fad0d0614ce5a8896470288cb108a9a81294114a97026da13e047dbe69ab91.jpg)  
Fig. 5. Adaptive Multi-Agent Recommendation Explanation

## 4.4 Recommendation Explanation

Formal definition of the task. <sup>We</sup> <sup>define</sup> Recommendation Explanation <sup>as</sup> <sup>the</sup> <sup>process</sup> <sup>of</sup> <sup>generating</sup> intelligible and contextually relevant justifications for why particular items are recommended to a user (see [8]) . Let $\mathbf { r } \in S ^ { L }$ be a set of items surfaced by a recommender $R _ { \phi }$ at dialogue step ?? and let $\mathbf { u } _ { t } = ( \widehat { C } _ { t } ^ { \mathrm { S E M } } , \widehat { C } _ { t } ^ { \mathrm { E P I } } )$ denote the user’s current semantic and episodic context retrieved via $\boldsymbol { Q }$ . A recommendation-explanation function <sup>is</sup> <sup>a</sup> <sup>mapping</sup>

$$
\Phi_ {\psi}: (\mathbf {r}, \mathbf {u} _ {t}) \longrightarrow e _ {t} \in \mathcal {E} _ {\text { text }}, \quad \text { s.t. } \operatorname{Consistency} (e _ {t}) = 1,
$$

where $\psi$ parameterises an LLM agent, $e _ { t }$ is a natural-language explanation, and Consistency is a predicate that checks (i) factual alignment with $\mathbf { u } _ { t }$ and (ii) stylistic conformity to brand rules.

![](images/00cd1106868e6772cc9ac9684071469e26697db260773c60898a3ee526c88a01.jpg)  
Fig. 6. Explaining Recommendations (e.g., Emotional Dramas in the first set of recommended movies) provides more transparency and helps with user engagements (courtesy netflix.com).

<sub>High-level</sub> <sub>goal.</sub> The system seeks to frame each recommendation batch in a concise, human-readable story that increases transparency, trust, and click-through rates while satisfying brand tone guide lines. The system can demonstrate awareness of both the user’s history and the underlying rationale for item selection.

<sub>System</sub> <sub>architecture</sub> <sub>and</sub> <sub>agent</sub> <sub>setup.</sub> The explanatory workflow is realised as $\mathrm { M A S } _ { \mathrm { e x p l } } = \left( \mathcal { A } , \mathcal { E } , \Pi \right)$ with agent ensemble $\mathcal { A } = \{ A _ { \mathrm { j o u r n e y } } , A _ { \mathrm { s e s s i o n } } , A _ { \mathrm { r e c } } , A _ { \mathrm { e x p l } } , A _ { \mathrm { e v a l } } \}$ . In this MAS, ??<sub>session</sub> invokes <sub>Q</sub> over $\Omega ^ { \mathrm { S E M } } \cup \Omega ^ { \mathrm { E P I } }$ to extract $\mathbf { u } _ { t } ; A _ { \mathrm { j o u r n e y } }$ inspects the live click stream $( x _ { 1 } , a _ { 1 } ^ { \mathrm { u s e r } } , \ldots , x _ { t } )$ to tag the latent intent (e.g. “holiday décor upgrade”). Both embeddings flow to $A _ { \mathrm { r e c } }$ which returns recommendation <sub>r</sub>. The explanation agent $A _ { \mathrm { e x p l } }$ feeds $\left( \mathbf { r } , \mathbf { u } _ { t } \right)$ into its LLM, then emits $e _ { t } = \Phi _ { \psi } ( \mathbf { r } , \mathbf { u } _ { t } ) . A _ { \mathrm { e v a l } }$ verifies Consistency<sub>(</sub>??<sub>?? )</sub> by checking factual mentions against <sub>r</sub> and brand constraints stored in $\Omega ^ { \mathrm { P R O C } }$ ; if the test fails, it sends a <sub>revise</sub> message back to $A _ { \mathrm { r e c } }$ and $A _ { \mathrm { e x p l } }$ , triggering a second-pass generation.

The protocol matrix <sub>C</sub> therefore admits the cycle $A _ { \mathrm { r e c } }  A _ { \mathrm { e x p l } }  A _ { \mathrm { e v a l } }$ with veto capability at the evaluator.

<sub>Memory</sub> <sub>and</sub> <sub>tool</sub> <sub>requirements.</sub> Short-term windows hold the active dialogue and the latest bundle <sub>r</sub>. Semantic memory captures enduring preferences (<sub>“collects</sub> <sub>Mickey-Mouse</sub> <sub>merchandise”</sub> ); episodic slices recall recent campaigns to avoid repetition; procedural memory stores brand-tone exemplars and banned phrasing. Key tools are illustrated in figure 5.

<sub>Benefits</sub> <sub>and</sub> <sub>discussion.</sub> <sub>Ω</sub><sup>PROC</sup>, <sub>Ω</sub><sup>EPI</sup> provide support for outputting truthful and on-brand explanations, while the modular MAS layout lets one inject new style guides or fairness rules by updating $\Omega ^ { \mathrm { P R O C } }$ and the evaluator prompt. Moreover, because explanations draw on the same semantic and episodic memories that drive ranking, the narrative naturally evolves with the user’s journey, reinforcing a sense of personal rapport and transparency throughout the recommendation lifecycle. In other words, when explanations leverage structured memory, real-time data fetching, and specialized text-generation agents, the resulting narratives are more credible and user-centric, ultimately deepening trust in the platform and encouraging repeated interactions.

Fig. 6 illustrates the broader motivation for grounded recommendation explanations: explanatory grouping can make recommendation surfaces more transparent and easier for users to interpret.

## 5 Operational Challenges and Evaluation Agenda

Agentic recommender systems inherit challenges from general LLM agents and multi-agent systems, but those challenges become recommender-specific when they afect ranking, exposure, feedback, item evidence, user memory, or marketplace outcomes. We therefore organize the challenge section around two questions: (i) what failure mode is introduced by planning, memory, tools, or multi-agent coordination, and (ii) how should a recommender-system researcher measure it?

## 5.1 Communication Complexity and Protocol

We use <sub>multi-agent</sub> <sub>communication</sub> <sub>protocol</sub> (MCP) to mean the set of message schemas, routing rules, context-sharing rules, state-synchronization assumptions, and provenance requirements by which agents exchange information. In an RS setting, MCP design must carry recommendationspecific metadata, including candidate-set provenance, item attributes, retrieved evidence, policy constraints, privacy labels, timestamps, and confidence estimates. Without these fields, downstream agents may rank or explain items using stale, unsupported, or policy-violating context.

Multi-agent recommendation systems rely on multiple autonomous agents that collaborate to deliver relevant items to users, often by sharing user profiles, item information, and intermediate findings. A robust communication protocol is essential in these settings to ensure that agents can exchange messages, negotiate tasks, and maintain synchronized states. In principle, an MCP should provide a unifying framework that allows agents to share user context, coordinate actions, and exchange relevant observations without ambiguity. In practice, however, weak protocol design leads to performance bottlenecks, misinterpretations, and significant implementation overhead. When each agent or data source uses a bespoke interface or message schema, the system devolves into a patchwork of ad-hoc integrations, making it dificult to scale or ensure correct interpretation of exchanged data. These drawbacks are particularly acute in recommendation systems, where rapid, potentially real-time interactions between agents (user-behavior-tracking agent for instance) demand consistency, low latency, and clear semantics of communication. Now, we will review some of the challenges.

<sub>Protocol</sub> <sub>Standardization.</sub> A foundational challenge is agreeing on a standardized MCP that all agents within the ecosystem can adopt. Ideally, a newly introduced agent, potentially developed by a diferent team or vendor, would connect seamlessly to the multi-agent system by adhering to the same syntactic and semantic rules. In practice, such alignment is dificult to achieve. Existing frameworks (for example, the FIPA Agent Communication Language [60]) demonstrated the complexities inherent to specifying communication structures and semantics. Too much rigidity can limit innovation and domain-specific extensions, whereas too little standardization fails to ensure interoperability. A well-designed MCP must be expressive enough to cover the needs of diverse agents (ranging from user-modeling to explanation evaluation for example) while remaining suficiently lightweight that developers can implement it without excessive overhead. Achieving wide adoption also poses governance challenges: diferent organizations may promote competing standards or tailor them to their internal architectures, which underscores the non-technical barriers to protocol unification.

State Synchronization Under High-Frequency Updates. <sup>A</sup> <sup>second</sup> <sup>technical</sup> <sup>hurdle</sup> <sup>is</sup> <sup>the</sup> <sup>requirement</sup> to maintain synchronized agent states under rapid, potentially continuous updates. If new user actions, item arrivals, or contextual signals flow into the system at high frequency, agents run the risk of operating on inconsistent snapshots of the environment. A naive approach that broadcasts every minor update to all agents creates a scalability bottleneck, as it can saturate the network and introduce large message queues. Yet deferring updates or aggregating them too aggressively can lead to agents making decisions on outdated information. Let

$$
\Delta : \mathcal {E} _ {t} \to \mathcal {E} _ {t + 1}
$$

denote an environment-update function that transitions the shared environment <sub>E</sub> from time ?? to time $t + 1$ . The question becomes how the MCP conveys these state transitions <sub>Δ</sub> to each agent. Approaches from distributed systems, such as eventual consistency or publish/subscribe event channels, may ofer partial solutions, but each implies trade-ofs among real-time accuracy, network overhead, and agent-level concurrency control. These design decisions directly impact recommendation quality, user-perceived latency, and the ability to scale across thousands of rapidly evolving data points.

<sub>Fault</sub> <sub>Tolerance</sub> <sub>and</sub> <sub>Recovery.</sub> Another salient concern is that in any distributed system, individual agents or communication links may fail or degrade without warning. If a crucial agent controlling item retrieval collapses, other agents may stall while waiting for updates, ultimately halting the recommendation flow. Protocol-level fault tolerance mitigates such breakdowns by ofering mecha nisms for detecting failure (via heartbeat signals or timeouts), rerouting tasks, and resynchronizing state when an agent recovers. These mechanisms can range from simple retries to more robust consensus protocols. However, each increment in fault tolerance introduces additional complexity in both agent design and the MCP itself. A well-engineered approach thus needs to strike a balance between resilience and performance overhead, particularly since real-world recommendation engines can ill aford long downtime or incomplete updates, but also cannot endure significant latency due to over-elaborate fault-detection routines.

<sub>Scalability</sub> <sub>in</sub> <sub>Decentralized</sub> <sub>Setings.</sub> As the number of specialized agents grows, communication trafic rises—potentially in a many-to-many pattern if the system is fully decentralized. This growth can lead to combinatorial message complexity. A naive peer-to-peer architecture may become infeasible as the system matures, so the MCP must support organized communication topologies or hierarchical roles among agents. For example, certain broker agents might aggregate specific types of updates and relay them to other agents, reducing message duplication. Alternatively, partitioning the item space or user segments among subgroups of agents can localize interactions at the expense of global knowledge. Each architectural choice entails a trade-of in coverage, latency, and potential points of failure. Finding near-linear or, at least, sub-exponential scalability solutions remains a major question for multi-agent recommendation. As more data sources or agent roles are added, the system’s design must ensure that communication and processing overheads remain manageable, and that the user still experiences timely, relevant recommendations.

Security and Privacy in Inter-Agent Communication. <sup>Agents</sup> <sup>in</sup> <sup>a</sup> <sup>recommendation</sup> <sup>system</sup> <sup>often</sup> exchange sensitive user data, ranging from personal profiles to behavioral logs, and proprietary or business (e.g. critical information about items and ranking heuristics). Lacking appropriate security layers, the MCP risks exposing these details to eavesdropping or tampering. Communication protocols must, at minimum, support encryption and authentication so that data is protected against adversarial access and malicious agents cannot masquerade as legitimate participants. Privacy concerns add further layers of complexity, since not every agent should automatically receive all user details. Agents may need to operate on aggregated or encrypted data in a fashion similar to secure multi-party computation, introducing nontrivial overhead and design challenges. Balancing open collaboration, which is essential for rich multi-agent interactions, with robust security constraints is particularly dificult. If the protocol is too permissive, user trust is jeopardized; if it is too stringent, constructive collaboration is stifled.

Open Research Questions and Future Directions. Several unresolved questions emerge from these challenges. One is how to establish an “inclusive but flexible” standard for MCP that agents can adapt across various domains and use cases without spawning multiple incompatible variants. Another is whether “adaptive synchronization schemes” possibly driven by real-time feedback loops, can address the tension between coherence (ensuring all agents remain in sync) and performance (avoiding communication overload). In addition, reliability under fast-changing recommendation contexts remains an open issue. There is also growing interest in robust fault-tolerance paradigms and decentralized consensus strategies that can be layered on top of the MCP [18], potentially leveraging emerging blockchain or distributed ledger approaches[94]. Finally, integrating “privacy preserving” features, such as secure enclaves or diferentially private updates, stands out as a frontier for bridging user data protection with multi-agent collaboration [26, 74]. Addressing these open problems could considerably advance the utility and reliability of multi-agent recommendation systems, enabling them to grow both in scale and sophistication while retaining clarity, resilience, and trustworthiness in their communication fabric.

For evaluation, the failure modes above are measurable. Protocol health can be tracked through message count and schema-validity rate; context integrity through provenance coverage, which records how often a candidate set or claim arrives with the metadata needed to verify it; synchronization quality through the delay between an environment update and its propagation to dependent agents; and coordination quality through inter-agent agreement rate and the ability to attribute a final error to the agent or message that introduced it.

## 5.2 Scalability

In the context of multi-agent recommendation systems, “scalability” refers to the ability of the architecture to sustain acceptable performance as the system grows in problem size, data volume, or agent complexity. Formally, let ?? denote the number of users, ?? the number of items, and ?? the number of autonomous agents collaborating to produce recommendations. We say that a system is <sub>scalable</sub> if its key performance metrics (e.g., throughput, latency, and accuracy) remain within acceptable bounds when ?? , ??, or ?? increase, and if resource utilization (computation, memory, financial cost) grows sub-linearly or at most linearly in these parameters. Concretely, if ??<sub>(</sub>?? , ??, ??<sub>)</sub> is the latency per recommendation request, scalability demands that ??<sub>(</sub>?? , ??, ??<sub>)</sub> does not grow exponentially with ?? , ??, or ??. Analogously, if <sub>Φ(</sub>?? , ??, ??<sub>)</sub> is the throughput of the system, then <sub>Φ(</sub>?? , ??, ??<sub>)</sub> should degrade gracefully (or improve) rather than collapse under increasing loads. This requirement ensures that adding users, expanding the item catalog, or incorporating additional agents does not render the recommendation service unresponsive or cost-prohibitive.

Latency Considerations: Batch vs. Real-Time. <sup>Scalability</sup> <sup>manifests</sup> <sup>diferently</sup> <sup>in</sup> batch-processing pipelines <sup>versus</sup> real-time inference <sup>scenarios.</sup> <sup>In</sup> <sup>an</sup> ofline batch setting<sup>,</sup> <sup>agents</sup> <sup>may</sup> <sup>train</sup> <sup>or</sup> <sup>update</sup> models periodically (e.g., overnight jobs), emphasizing throughput and the completion time of large data-processing tasks. As ?? and ?? grow, or as more agent modules participate (for example, separate modules for each language or region), total computation can increase significantly, stretching batch windows and risking stale or incomplete updates. Partial solutions include distributing tasks across more compute nodes [28], caching intermediate results [83], or consolidating models to reduce overhead [7]. By contrast, <sub>real-time</sub> recommendation places tight upper bounds on per-request latency (often tens of milliseconds). When a user makes a request (e.g., “Recommend me some items now”), the system must orchestrate multiple agents without exceeding a strict time budget. If the request passes sequentially through ?? agents, or if communication overhead is high, total latency can explode. Methods such as parallelizing sub-tasks, reducing model size (e.g., quantization or distillation), or precomputing partial results become vital. Balancing <sub>freshness</sub> (using the latest user context in real time) with <sub>responsiveness</sub> (controlling inference overhead) is an ongoing engineering challenge, especially as agent complexity and user concurrency grow.

Communication Overhead and Coordination Botlenecks. <sup>A</sup> <sup>multi-agent</sup> <sup>system</sup> <sup>inherently</sup> <sup>incurs</sup> overhead from inter-agent communication. If each agent $A _ { i }$ must exchange intermediate results or context with other agents $A _ { j }$ , the communication pattern can grow as $O ( A ^ { 2 } )$ in the worst case. Even more structured topologies $( \mathrm { e . g . }$ , staged pipelines) introduce data serialization, network transfer, and synchronization costs that increase with ??. In real deployments, these costs may overshadow pure compute time, especially if agents are distributed across diferent servers or data centers. Synchronization points (e.g., where an agent must wait for multiple upstream agents to finish) can compound the bottleneck: a single slow or overloaded agent holds up the entire recommendation pipeline. The result is that response-time variability spikes as ?? grows, impairing scalability. Proposed strategies include “selective communication” (agents only communicate with relevant peers), asynchronous event-driven designs, or hierarchical orchestration (where specialized “supervisor” or “broker” agents mediate interactions). While each approach can alleviate overhead, designing a protocol that scales sub-linearly in agent count remains an open problem for multi-agent recommenders.

<sub>Computational</sub> <sub>and</sub> <sub>Financial</sub> <sub>Costs.</sub> Scalability also has a direct economic dimension. Each agent may represent a separate inference step (e.g., a large transformer for generating textual explanations, a collaborative filter for scoring items), thereby multiplying compute, memory, and storage costs when scaled to millions of users. Maintaining separate agents for many languages or market segments compounds these expenses. Even inter-agent communication consumes CPU cycles and bandwidth that can become costly at scale, especially in cloud environments where data transfer and compute times are billed. As a result, system architects must continually balance performance benefits from specialized agents against the financial overhead of running them all. Real-world solutions include consolidating similar tasks into fewer, more general models, caching partial results to avoid redundant computations, or introducing cost-aware scheduling where certain expensive agents (such as large language models) are only invoked for high-value requests or in batch mode.

<sub>Examples</sub> <sub>and</sub> <sub>Botlenecks</sub> <sub>in</sub> <sub>Practice.</sub> Industrial experience underscores these scalability concerns. Large e-commerce providers may need multi-agent approaches for brand-new product lines or language expansions, only to find that naive per-language replication is prohibitively expensive and leads to model silos with limited synergy. Media streaming services, like Netflix or YouTube, rely on multi-stage ranking pipelines, where each stage refines candidates from the previous one. In principle, adding specialized agents can improve personalization; however, at large user scales, the additional latency and resource costs grow burdensome. Academic prototypes such as MACRec [77] demonstrate how multiple LLM-based sub-agents can collaborate for more accurate recommendations, but in production, running multiple large models in parallel can yield superlinear latency and cost, especially if thousands of user queries arrive simultaneously. In each case, synchronization overheads, data duplication, or model proliferation frequently emerge as bottlenecks.

<sub>Open</sub> <sub>Challenges</sub> <sub>and</sub> <sub>Future</sub> <sub>Directions.</sub> Despite progress, significant open questions remain for achieving robust, eficient scalability in multi-agent, language-based recommender systems:

<sub>(i)</sub> <sub>Dynamic</sub> <sub>Agent</sub> <sub>Coordination:</sub> Adaptive scheduling or routing (deciding which agents to invoke per request) could mitigate latency and cost surges; how to automate such coordination at scale is an ongoing research area [56].

<sub>(ii)</sub> <sub>Cost-Aware</sub> <sub>Architectures:</sub> Tools for balancing model accuracy with financial overhead remain nascent. Budget-aware or resource-limited modes may become standard features in large multiagent systems.

<sub>(iii)</sub> <sub>Multi-Lingual</sub> <sub>Model</sub> <sub>Consolidation:</sub> Designing shared representations or truly multilingual models that preserve local performance while avoiding ??-fold duplication is an active challenge, especially for low-resource languages.

<sub>(iv)</sub> <sub>Observability</sub> <sub>and</sub> <sub>Debugging:</sub> As agent count grows, tracing the contribution of each agent in a recommendation pipeline becomes non-trivial. New monitoring frameworks are needed to pinpoint bottlenecks, synchronization issues, or poor data hand-ofs.

Addressing these challenges will require interdisciplinary solutions that merge distributed systems principles (for fault tolerance, communication eficiency), machine learning insights (for multilingual and multi-domain models), and operational best practices (for cost optimization and maintainability). As multi-agent architectures gain adoption in real-world recommendation services, resolving these open problems stands to bring significant advances in both the quality of personalization and the scalability of next-generation systems.

Scalability is measured along quality, time, and money jointly. The relevant signals are end-toend and per-agent latency, throughput, token and API cost, and timeout rate under load. Because adding agents trades cost for quality, the informative summary is not any single number but the quality–latency (or quality–cost) Pareto frontier, which exposes whether an extra agent buys a quality gain large enough to justify its latency and cost. Section 6 instantiates exactly this frontier for a concrete ranking task.

## 5.3 Hallucination, Memory Drift, and Error Propagation

Let $\mathcal { A } = \{ A _ { 1 } , . . . , A _ { k } \}$ be a set of collaborating LLM-based agents in a recommendation pipeline. Each agent $A _ { i }$ produces a message $m _ { i }$ that is consumed, directly or indirectly, by other agents. Define the boolean predicate <sub>valid</sub> $( m _ { i } ) = 1 \mathrm { i f } m _ { i }$ is factually correct with respect to an external ground-truth oracle $\mathcal { G } _ { : }$ , and 0 otherwise. Hallucination occurs when <sub>valid</sub> $\left( m _ { i } \right) = 0$ . “Error propagation” arises when there exists a path $A _ { i } \longrightarrow A _ { j }$ in the agent-interaction graph such that <sub>valid</sub> $\left( m _ { i } \right) = 0$ and the downstream message $m _ { j }$ is a deterministic function of $m _ { i }$ , yielding <sub>valid</sub> $( m _ { j } ) = 0$ . The probability that at least one final user-facing output is invalid is

$$
\operatorname * {P r} \left[ \exists m _ {u}: \operatorname{valid} \left(m _ {u}\right) = 0 \right] = 1 - \prod_ {i = 1} ^ {k} \left(1 - p _ {i}\right),
$$

where $p _ { i } = \mathrm { P r } [ \mathsf { v a l i d } ( m _ { i } ) = 0 ]$ after all verification steps. Minimizing this probability in practice is non-trivial; naive composition of agents tends to increase $\mathbf { \nabla } \mathcal { P } i$ through cascading dependencies.

<sub>Mechanisms</sub> <sub>of</sub> <sub>Cascading</sub> <sub>Error.</sub> When agents share a common context bufer (e.g. chain-of-thought transcripts), an erroneous assertion by one agent can enter the shared memory $\Omega _ { t }$ and be re-ingested by all subsequent agents:

$$
\Omega_ {t + 1} = \Omega_ {t} \cup \{m _ {i} \}, m _ {j} = A _ {j} (\Omega_ {t + 1}).
$$

Because most LLMs lack calibrated epistemic uncertainty, a fabricated but linguistically confident statement in $\Omega _ { t + 1 }$ is typically treated as fact [67]. Human cognitive biases such as “authority” or “conformity” find analogues in LLM agents: empirical studies show that a single persuasive hallucination can shift the distribution of responses from peer agents toward the same error, producing group-level misbelief. [44]

A recommender-specific variant of this mechanism is memory drift. Because an agentic recommender persists user state across turns and sessions, an erroneous or outdated fact written to memory is not a one-time error: it is retrieved and re-applied on every subsequent request until it is corrected. A stale preference, an incorrectly merged constraint, or a privacy-sensitive trace that should have been deleted can therefore contaminate future rankings and explanations long after the originating turn, which is the persistent analogue of the cascading error above.

Mitigation Approaches. <sup>Current</sup> <sup>strategies</sup> <sup>fall</sup> <sup>into</sup> <sup>three</sup> <sup>categories:</sup> <sup>(i)</sup> Agent-level verification. Multi-agent debate, majority voting, and cross-examination frameworks instantiate ?? redundant agents $\bar { \{ A _ { i } ^ { ( 1 ) } , . . . , A _ { i } ^ { ( r ) } \} }$ per logical role and accept a message only if a consensus rule $_ \mathrm { ~  ~ }$ is satisfied: $\boldsymbol { m } _ { i } ^ { \star } = \mathcal { V } \big ( \boldsymbol { m } _ { i } ^ { ( 1 ) } , \ldots , \boldsymbol { m } _ { i } ^ { ( r ) } \big )$ . This reduces but does not eliminate correlated hallucinations [37, 50]. (ii) Supervisor or moderator agents. <sup>A</sup> <sup>top-level</sup> <sup>agent</sup> $A _ { \mathrm { m o d } }$ inspects each intermediate output and blocks or edits $m _ { i }$ <sup>if</sup> valid $\left( m _ { i } \right) = 0$ . The dificulty is that $A _ { \mathrm { m o d } }$ is itself an LLM with similar failure modes; recursive oversight may be required [49]. (iii) <sub>Tool-assisted</sub> <sub>grounding.</sub> Agents invoke external APIs $\mathcal { F }$ (e.g. factual search, calculators, product databases) to verify claims: $m _ { i } = f \bigl ( \mathrm { L L M } ( x ) , \mathcal { F } ( x ) \bigr )$ . Empirical evidence shows that interleaving of reasoning and tool calls substantially lowers hallucination rates, although it increases latency. [84]

<sub>Open</sub> <sub>Questions</sub> <sub>for</sub> <sub>the</sub> <sub>RecSys</sub> <sub>Community.</sub> Despite these advances, scalability and completeness remain open. Verification ensembles increase compute cost; tool calls add latency; and moderators share the same epistemic blind spots as base agents. These are sample open questions in this regard.

(1) <sub>Uncertainty</sub> <sub>Calibration:</sub> How can LLM agents produce calibrated confidence scores that downstream agents may use to discount or challenge low-certainty statements?

(2) <sub>Eficient</sub> <sub>Verification:</sub> What lightweight protocols (selective voting, probabilistic auditing, or adaptive tool calls) can bound error propagation without breaching real-time latency constraints?

(3) <sub>Formal</sub> <sub>Guarantees:</sub> Can we derive probabilistic upper bounds on $\mathrm { P r } [ \exists m _ { u }$ <sup>:</sup> valid $\left( m _ { u } \right) = 0 ]$ for a given agent graph and verification strategy, analogous to error-correcting codes?

(4) <sub>Adversarial</sub> <sub>Robustness:</sub> How can multi-agent recommenders detect and neutralize deliber ate prompt injections or knowledge-base poisoning that exploit error-propagation pathways?

These failure modes are measurable. Hallucination at the item level is captured by the unsupportedclaim rate, citation accuracy, and contradiction rate of agent messages, and by evidence coverage, the fraction of claims backed by retrieved item or user evidence. Memory drift is captured by memory precision and recall against the true user state, by a staleness rate that counts retrieved facts no longer valid, and by deletion compliance, the fraction of removal requests honored on subsequent retrieval.

Answering these questions will be pivotal for building multi-agent, LLM-powered recommenders that harness generative flexibility [13, 14] while safeguarding against cascading hallucinations and the attendant erosion of user trust.

## 5.4 Potential Collusion or Unintended Emergent Behavior

Multi-agent systems built on large language models (LLMs) are being actively explored for recommendation tasks, enabling multiple autonomous agents to interact and jointly deliver personalized suggestions. Each agent may correspond to a user perspective, an item provider, or a specialized recommender component, with interactions coordinated through a communication protocol. While this paradigm shows promise for richer, more adaptive recommendations, it also raises concerns over unintended emergent behaviors. When agents possess partially independent objectives and adaptive capabilities, local decision-making can yield global outcomes that system designers did not anticipate. Two key risks are collusion among agents (secretly coordinating strategies that undermine fairness or eficiency) and reinforcing feedback loops that amplify bias or degrade system robustness. This subsection presents current findings and open questions regarding such emer gent behaviors, illustrating how they jeopardize fairness, reliability, and user trust in multi-agent LLM-based recommendation systems.

Unintended Emergent Behaviors in Autonomous LLM Agents. <sup>“Emergent</sup> <sup>behavior”</sup> <sup>in</sup> <sup>multi-agent</sup> LLM systems arises from the complex interactions of multiple agents pursuing local goals, re sulting in global patterns unintended by the system’s designers. One salient risk is “collusion”: autonomous agents may discover covert means to collaborate—often through cryptic or hidden messaging—thereby subverting oversight. Prior work has shown that even simple negotiation bots can invent private “shorthand” languages to maximize joint gains, a harbinger of more advanced forms of covert cooperation in LLM-driven systems [36]. Under adversarial incentives, such covert communication can manifest as “cartel-like” behavior, where agents collude to manipulate item rankings or artificially inflate engagement metrics, undermining the recommender’s integrity. In less adversarial but still dynamic settings, agents may spontaneously cooperate if cooperation yields better local utility. For example, self-interested LLM-based “firm” agents in a simulated market might tacitly agree to price-fix, converging to above-competitive prices through repeated interactions—even though no explicit collusion protocol was programmed.

Another persistent concern is bias amplification and feedback loops. Classic recommender systems already exhibit feedback loops where popular items receive even greater exposure, reinforcing their dominance at the expense of niche content [2]. In a multi-agent LLM context, these loops may intensify: a user-simulator LLM’s positive feedback can encourage the recommender LLM to propose narrower sets of items, fostering echo chambers. Empirical explorations reveal that, without careful calibration, multi-agent LLM recommenders can systematically favor popular content or align feedback to confirm preconceived user preferences [41], resulting in reduced diversity and potential “filter bubble” efects. [70]

Case Studies and Examples in LLM-Based Recommendation Systems. <sup>While</sup> <sup>large-scale</sup> <sup>real-world</sup> instances remain relatively uncommon, several research prototypes and industry analogs illustrate emergent misbehaviors:

(i) <sub>Rec4Agentverse</sub> <sub>and</sub> <sub>Similar</sub> <sub>Frameworks:</sub> Conceptual models wherein multiple Item Agents (each representing a specific content source) coordinate with a central Recommender Agent can inadvertently allow item providers to form alliances, thereby boosting each other. Researchers note the need for robust communication constraints and fairness safeguards to prevent collusive behaviors. [90]

(ii) User–Recommender Co-Adaptive Simulations: Prototypes in which a user-simulator LLM interacts iteratively with a recommender LLM demonstrate how naive feedback loops amplify popularity bias or lead to trivial “approval” behaviors. Even if no intentional collusion exists, the system’s closed feedback cycle can systematically degrade diversity or realism in user modeling. [70]

<sup>(iii)</sup> Industry Observations (Non-LLM but Analogous): <sup>Large</sup> <sup>platforms</sup> <sup>like</sup> <sup>Netflix</sup> <sup>and</sup> <sup>Facebook</sup> historically reported polarization and echo chambers emerging from automated feedback loops. Translating these patterns to a multi-agent LLM scenario, if item-provider agents focus excessively on engagement signals, sensational or polarizing content might dominate—a dynamic form of self-reinforcing bias. [55, 73]

<sub>5.4.1</sub> <sub>Open</sub> <sub>Challenges.</sub> Addressing collusion and unintended emergent behavior in multi-agent LLM recommenders requires an interdisciplinary approach combining AI safety, mechanism design, and robust system engineering. Several key areas demand further exploration:

<sub>(i)</sub> <sub>Collusion</sub> <sub>Detection</sub> <sub>and</sub> <sub>Prevention.</sub> Identifying covert communication among LLM-based agents remains challenging, particularly if the agents develop coded protocols. Future research might involve adversarial training of oversight models or cryptographic constraints limiting an agent’s ability to conceal signals.

(ii) Alignment of Local and Global Objectives. <sup>A</sup> <sup>central</sup> <sup>cause</sup> <sup>of</sup> <sup>emergent</sup> <sup>misbehavior</sup> <sup>is</sup> <sup>the</sup> mismatch between local agent incentives and the broader system goal. Mechanism design, incentivecompatible rewards, or hierarchical constraints may help ensure that individually rational actions coincide with socially desirable outcomes.

<sub>(iii)</sub> <sub>Bias</sub> <sub>Mitigation</sub> <sub>in</sub> <sub>Multi-Agent</sub> <sub>Loops.</sub> As agents co-adapt, biases can be amplified through cyclical feedback. Tools like causal intervention, re-weighted training, or fairness-promoting prompts must be extended to multi-agent contexts. Evaluating long-term fairness, beyond single-step rec ommendations, remains an open problem, necessitating new metrics and simulation platforms.

<sub>(iv)</sub> <sub>Dynamic</sub> <sub>Adaptation</sub> <sub>and</sub> <sub>Safety.</sub> As multi-agent LLM recommenders evolve over time, continuous oversight is required to preempt emergent failures. Online learning, with real-time detection of harmful collusive patterns, will likely be necessary. Balancing adaptability with safety constraints remains a core tension.

By addressing these questions, the recommender systems community can help shape multi-agent LLM architectures that realize their full potential for personalized, adaptive user experiences while safeguarding against collusion, bias, and other emergent hazards. Meeting these challenges will require new techniques in distributed AI governance, fairness-aware design, and robust multi-agent learning—an exciting interdisciplinary frontier for future research.

Measuring these behaviors requires signals beyond per-request accuracy. Collusion can be probed with collusion indicators and price or exposure anomalies under adversarial simulation, and with an objective-conflict rate that quantifies how often local agent incentives diverge from the system objective. Exposure feedback loops are tracked with catalog coverage, long-tail exposure, and exposure disparity across providers or groups, together with group-wise utility, since fairness here is a property of the distribution of exposure over time rather than of a single ranked list.

## 5.5 Brand, Policy, and Legal Compliance

In agentic recommender systems, brand and policy compliance is not only a generic text-generation issue. It directly afects recommendation explanations, item presentation, generated claims about item attributes or availability, provider obligations, user safety, and legal or regulatory requirements. A policy-checking agent therefore evaluates not only whether the language is on-brand, but also whether the recommended items, claims, evidence, and constraints are consistent with platform policy and applicable law.

Let $\mathcal { A } = \{ A _ { 1 } , . . . , A _ { k } \}$ be a set of collaborating LLM-based agents that generate, transform, or filter textual recommendations. Let $\mathcal { P }$ denote a formal <sub>brand</sub> <sub>policy</sub>, a finite set of constraints on tone, vocabulary, factual claims, and legally compliant disclosures. For any agent $A _ { i }$ emitting a textual message $m \in \Sigma ^ { * }$ <sup>,</sup> <sup>define</sup> <sup>a</sup> compliance predicate

$$
\mathcal {C} _ {\mathcal {P}} (m) = \left\{ \begin{array}{l l} 1 & \text { if   } m \text {   satisfies   every   rule   in   } \mathcal {P}, \\ 0 & \text { otherwise. } \end{array} \right.
$$

A multi-agent recommender maintains <sub>brand</sub> <sub>consistency</sub> $\operatorname { i f } ,$ for every output ?? observable by the end user and for every intermediate message exchanged among agents that could influence ??, we have $C _ { \mathcal { P } } ( m ) = 1$ . The challenge is to guarantee this condition while preserving the generative flexibility and eficiency of the agents.

<sub>Sources</sub> <sub>of</sub> <sub>Inconsistency.</sub> First, pretrained LLMs embed broad “world knowledge” that may conflict with brand-specific language or regulations. Second, heterogeneous alignment across agents induces drift: if $A _ { 1 }$ is fine-tuned for tone but $A _ { 2 }$ merely prompted, their joint output may diverge from $\mathcal { P }$ Third, generic safety filters rarely cover nuanced corporate rules (e.g., prohibitions on competitor references, regional marketing laws), leaving gaps through which policy-violating content may pass.

<sub>Illustrative</sub> <sub>Incidents.</sub> Well-publicised failures, such as Character.AI’s AI-powered assistant providing harmful advice to a minor, or historical “bomb-making” item bundles on Amazon underline the reputational and legal risks of insuficient control. [68, 69] While these cases did not involve full multi-agent architectures, they foreshadow the compounded risk when multiple autonomous LLMs exchange information without a unifying compliance layer.

Current Mitigation Strategies. <sup>Industry</sup> <sup>is</sup> <sup>moving</sup> <sup>toward</sup> brand-tuned LLMs<sup>,</sup> <sup>in</sup> <sup>which</sup> <sup>a</sup> <sup>base</sup> <sup>model</sup> is fine-tuned or instruction-aligned with proprietary style guides, product catalogs, and regulatory constraints [1]. Researchers have proposed alignment studios and inference-time <sub>policy-expert</sub> <sub>agents</sub> that veto or rewrite non-compliant tokens:

$$
m ^ {\star} = \arg \max _ {m} \left[ \operatorname * {P r} (m \mid \text { context }) \text {   s.t.   } C _ {\mathcal {P}} (m) = 1 \right].
$$

Such approaches reduce manual review but introduce computational overhead and still lack formal guarantees of completeness, especially as $\mathcal { P }$ evolves over time.

Outstanding Challenges. <sup>Formal</sup> <sup>certification</sup> <sup>of</sup> $C \varphi$ across an entire agent pipeline remains open; pol icy drift is likely as models and guidelines change asynchronously. Real-time enforcement demands fast, diferentiable approximations of $C _ { \mathcal { P } }$ , yet brand policies frequently involve non-diferentiable, context-dependent rules (e.g., comparative advertising limitations difering by jurisdiction). Finally, maintaining multilingual consistency is dificult: a compliant English output may translate into a culturally inappropriate phrase in another language, violating $\mathcal { P } s$ spirit even if literal rules are met.

Open Questions for the RecSys Community.

(1) <sub>Formal</sub> <sub>Guarantees:</sub> How can we design verifiable protocols or certified decoders that ensure $C _ { \mathcal { P } } ( m ) = 1$ for every agent message without excessive latency?

(2) <sub>Continuous</sub> <sub>Compliance:</sub> How can a recommender adapt when either the brand policy or external regulations change, ensuring that legacy agent behaviors do not drift out of compliance?

(3) <sub>Cross-Lingual</sub> <sub>Control:</sub> Which multilingual alignment techniques best propagate tone, legal constraints, and cultural sensitivities across languages without retraining separate agents per locale?

(4) <sub>Evaluation</sub> <sub>Benchmarks:</sub> What standardized datasets and metrics can quantify brand-policy adherence and stylistic consistency in multi-agent recommendation settings?

Table 4. Operationalizing the five challenges of agentic recommender systems (Sections 5.1–5.5). Each challenge is tied to its source in agentic RS, its recommender-specific manifestation, and measurable evaluation signals.

<table><tr><td>Challenge</td><td>Source in agentic RS</td><td>RecSys-specific manifestation</td><td>Metrics / protocols</td></tr><tr><td>Communication and protocol (§5.1)</td><td>Agents exchange candidate sets, evidence, constraints, critiques, and memory records</td><td>Stale candidates passed downstream; missing item provenance; unverifiable claims or constraints</td><td>Message count; schema-validity rate; provenance coverage; synchronization delay; agreement rate; failure attribution</td></tr><tr><td>Scalability and cost (§5.2)</td><td>Each agent, memory op, retrieval, tool call, or evaluator adds inference cost and latency</td><td>Extra agents improve ranking marginally while exceeding real-time latency budgets</td><td>End-to-end and per-agent latency; token / API cost; throughput; time-out rate; quality-latency Pareto frontier</td></tr><tr><td>Hallucination and memory drift (§5.3)</td><td>Generated claims, retrieved evidence, and stored memories are consumed downstream as if factual</td><td>Unsupported attributes; fabricated availability; stale preferences; invalid constraint satisfaction; privacy-sensitive recall</td><td>Unsupported-claim rate; citation accuracy; contradiction rate; evidence coverage; memory precision/recall; staleness rate; deletion compliance</td></tr><tr><td>Collusion and exposure loops (§5.4)</td><td>Autonomous agents optimize local goals conflicting with user, provider, or fairness objectives</td><td>Provider agents suppress competitors; engagement over-optimization; simulated users amplify popularity bias</td><td>Collusion indicators; price / exposure anomalies; objective-conflict rate; catalog coverage; long-tail exposure; exposure disparity; group-wise utility</td></tr><tr><td>Brand, policy, and legal compliance (§5.5)</td><td>Explanations, claims, and actions are generated dynamically and vary across users, markets, and languages</td><td>Off-brand tone; prohibited or unsafe claims; unsupported legal/product claims; policy-inconsistent justifications</td><td>Guideline adherence; policy-violation rate; cross-lingual consistency; human-review agreement; escalation rate</td></tr></table>

(5) <sub>Cost–Benefit</sub> <sub>Trade-ofs:</sub> How do we balance the computational and financial overhead of stringent compliance layers against their risk-mitigation benefits in large-scale production systems?

Addressing these questions will be pivotal for deploying multi-agent, LLM-based recommenders that are both creative and rigorously aligned with brand identity and regulatory obligations. Operationally, compliance is measured by guideline-adherence and policy-violation rates over generated outputs, cross-lingual consistency of the same recommendation across locales, human review agreement on flagged cases, and the escalation rate at which the system defers to human oversight.

Table 4 operationalizes these presented challenges by mapping each challenge to its source in agentic recommendation, its recommender-specific manifestation, and measurable metrics or protocols.

## 6 Empirical Illustration: When Do Multi-Agent Pipelines Pay Of?

The preceding sections argued, conceptually, that agentic orchestration unlocks capabilities beyond single-pass pipelines. A perspective is more convincing when it is made concrete, and in this section we want to quantify both the benefit and the cost of multi agentic structures. This section therefore reports a controlled study on the simplest slice of the Interactive Recommendation task of Section 4.1: re-ranking a fixed candidate set based on a user’s purchase history. The study is deliberately narrow so that the efect of <sub>adding</sub> <sub>agents</sub> can be isolated from confounds such as multi-turn dialogue dynamics or tool availability.

In this section, we want to explore what makes these orchestrations work and when they will not benefit the ultimate goal of the task. We will see for the given task of conversational ranking, the value of using multi agentic orchestrations scales with the complexity of the input. We will also show that several of the multi-agentic roles that look helpful in principle do not repay their cost in practice. For instance, we show that self-referential refinement can actively degrade ranking quality. Concretely, this study provides controlled evidence for the usage of multi-agentic mechanisms. Throughout, we connect the measurements back to the error-propagation formalism of Section 5.3 and the scalability concerns of Section 5.2.

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

## 6.2 Quantifying the Cost of Agentic Structures

Before asking whether added agents improve ranking, we fix the bar that any quality gain must clear. Table 6 reports per-query tokens, dollar cost, and latency for both samples. The single shot LLM call issues one call of roughly 1.7k tokens at about \$0.0022 per query. The ensemble workflows PEns and PPEns issue five and six calls, consume between 8.9k and 10.8k tokens, and cost between \$0.0112 and \$0.0123 per query, which is between five and six times the Single-shot LLM call cost.

We report latency along the parallel critical path rather than the raw sequential sum, because the sequential figure is an artifact of our single-threaded benchmark harness rather than a property of the workflow’s dependency structure. The critical path is the longest chain of calls that must run in series once mutually independent calls are dispatched concurrently. Take PEns as an example: the planner runs first, its plan is handed to three rankers that are mutually independent and can therefore be dispatched at the same time, and the arbitrator runs last on their combined output. The critical path is thus planner, then one ranker stage (not three), then arbitrator, so the five-call workflow has the latency of three calls in series rather than five. On the high-diversity sample this places PEns and PPEns at roughly three times the Single-shot LLM call latency (34.1 s and 35.2 s against 11.8 s), and somewhat higher on the random sample, where the single call is itself slower. Crucially, parallel execution recovers a share of the wall-clock penalty but does not reduce token consumption or dollar cost, which scale with the number and size of calls regardless of how they are scheduled. The implication for the rest of the section is simple: a workflow earns its place only if its quality improvement is large enough to justify a multiplicative increase in cost.

## 6.3 On Typical Users, Added Agents Do Not Pay, and Often Hurt

We begin with the negative result, since it is the more surprising of the two and frames the rest of the section. Table 7 reports quality on the random sample. On these typical histories the single shot LLM call is already strong, reaching an NDCG@10 of 0.7197, and no multi-agent pipeline meaningfully improves on it. The best multi-agent score, 0.7209 from the debate pipeline, is within a fraction of a point of the baseline, and the two pipelines tie on NDCG@3 as well. Given the five- to six-fold cost increase documented in Table 6, this is efectively a loss: the added structure purchases no useful signal.

Table 6. Cost and latency per query on gpt-5-mini, aggregate over the four categories $( n = 4 0 0 )$ . “Total tok/q” sums input and output tokens over a workflow’s calls. “Lat. par” is the parallel critical-path latency, defined as the longest chain of dependent calls once mutually independent calls are dispatched concurrently. Lower is beter throughout; the single shot LLM call is the floor on every column by construction.

<table><tr><td>Workflow</td><td>Calls/q</td><td>Total tok/q</td><td>Cost/q (USD)</td><td>Lat. par (s)</td></tr><tr><td colspan="5">Random sample (n = 400)</td></tr><tr><td>SA: Single-shot LLM call</td><td>1.0</td><td>1,756</td><td>0.00217</td><td>14.52</td></tr><tr><td>PR: Profiler → Ranker</td><td>2.0</td><td>2,804</td><td>0.00328</td><td>22.31</td></tr><tr><td>PPR: Planner+Profiler → Ranker</td><td>3.0</td><td>4,273</td><td>0.00473</td><td>22.98</td></tr><tr><td>RC: Ranker ↔ Critic</td><td>3.0</td><td>6,699</td><td>0.00831</td><td>55.27</td></tr><tr><td>DEB: Two-agent Debate</td><td>4.0</td><td>7,635</td><td>0.00933</td><td>62.92</td></tr><tr><td>PENS: Planner → 3 Rankers → Arb.</td><td>5.0</td><td>9,510</td><td>0.01121</td><td>38.36</td></tr><tr><td>PPENS: Planner+Profiler → 3 Rankers → Arb.</td><td>6.0</td><td>10,812</td><td>0.01225</td><td>44.56</td></tr><tr><td colspan="5">High-diversity sample (n = 400)</td></tr><tr><td>SA: Single-shot LLM call</td><td>1.0</td><td>1,654</td><td>0.00219</td><td>11.76</td></tr><tr><td>PR: Profiler → Ranker</td><td>2.0</td><td>2,537</td><td>0.00322</td><td>17.70</td></tr><tr><td>PPR: Planner+Profiler → Ranker</td><td>3.0</td><td>3,912</td><td>0.00470</td><td>20.85</td></tr><tr><td>RC: Ranker ↔ Critic</td><td>3.0</td><td>6,221</td><td>0.00803</td><td>41.89</td></tr><tr><td>DEB: Two-agent Debate</td><td>4.0</td><td>7,130</td><td>0.00923</td><td>49.61</td></tr><tr><td>PENS: Planner → 3 Rankers → Arb.</td><td>5.0</td><td>8,921</td><td>0.01119</td><td>34.14</td></tr><tr><td>PPENS: Planner+Profiler → 3 Rankers → Arb.</td><td>6.0</td><td>10,000</td><td>0.01202</td><td>35.19</td></tr></table>

More striking is that two pipelines degrade quality. The Ranker+Evaluator pipeline (RC) falls to an NDCG@10 of 0.6922, a relative drop of 3.8 percent against the single shot LLM call, and a larger 7.2 percent drop at NDCG@3, while costing roughly four times as much. We read this as a direct empirical instance of the error-propagation mechanism formalised in Section 5.3. When the evaluator critiques an already-correct ranking with no external ground-truth oracle, its critique is itself an ungrounded LLM output that the ranker then incorporates, so a second source of error is introduced where the first pass had none. In the notation of that section, $\mathrm { P r } [ \exists m _ { u } : \mathrm { v a l i d } ( m _ { u } ) =$ $\begin{array} { r } { 0 ] = 1 - \prod _ { i } ( 1 - p _ { i } ) } \end{array}$ grows when an additional stage with $p _ { i } > 0$ is composed onto a pipeline that already produces a good answer. The cleanest summary of this subsection is that on inputs a single model already handles well, additional agents add failure surface faster than they add signal.

## 6.4 On High-Diversity Users, Decomposition and Ensembling Begin to Pay

The picture inverts on the high-diversity sample. Table 8 shows that the absolute scores are lower than on the random sample, which is expected because diverse histories are harder to summarise into a single purchase intent. The informative quantity, however, is the relative ordering: here the pipelines that carry a planner or an ensemble lead the single shot LLM call. At NDCG@3 the combined pipeline (PPEns) reaches 0.5202 and the ensemble pipeline (PEns) reaches 0.5162, against 0.4898 for the single shot LLM call, a relative gain of 6.2 and 5.4 percent respectively. At NDCG@10 the ensemble pipeline leads at 0.6471 against 0.6316, a gain of 2.5 percent, and the MRR columns tell the same story, with PEns best at every reported cutof.

The contrast between Tables 7 and 8 is the central empirical finding of the paper: the same pipelines that are wasteful on typical users become beneficial on diverse ones. This is consistent with the intuition that decomposition and aggregation only have something to contribute when the input is heterogeneous enough that a single pass under-resolves it.

Table 7. Ranking quality on the random sample, aggregate over four categories (<sup>??</sup> = <sup>400</sup>), gpt-5-mini. Best and second-best among the LLM pipelines per column are bold and underlined. Higher is beter.

<table><tr><td>Method</td><td>MRR@3</td><td>MRR@10</td><td>NDCG@3</td><td>NDCG@10</td></tr><tr><td>SA Single-shot LLM call</td><td>0.5846</td><td>0.6317</td><td>0.6225</td><td>0.7197</td></tr><tr><td>RC Ranker+Evaluator</td><td>0.5400</td><td>0.5960</td><td>0.5779</td><td>0.6922</td></tr><tr><td>PR Profiler+Ranker</td><td>0.5775</td><td>0.6255</td><td>0.6191</td><td>0.7156</td></tr><tr><td>PPR Planner+Profiler+Ranker</td><td>0.5708</td><td>0.6185</td><td>0.6129</td><td>0.7100</td></tr><tr><td>PENS Planner+3 Rankers+Arb.</td><td>0.5792</td><td>0.6266</td><td>0.6190</td><td>0.7159</td></tr><tr><td>PPENS Planner+Profiler+3 Rankers+Arb.</td><td>0.5837</td><td>0.6319</td><td>0.6212</td><td>0.7198</td></tr><tr><td>DEB Two-agent Debate</td><td>0.5850</td><td>0.6330</td><td>0.6229</td><td>0.7209</td></tr><tr><td>Random baseline</td><td>0.1833</td><td>0.2929</td><td>0.2131</td><td>0.4544</td></tr></table>

Table 8. Ranking quality on the high-diversity sample, aggregate over four categories (<sup>??</sup> = <sup>400</sup>), gpt-5-mini. Best and second-best among the LLM pipelines per column are bold and underlined. Higher is beter.

<table><tr><td>Method</td><td>MRR@3</td><td>MRR@10</td><td>NDCG@3</td><td>NDCG@10</td></tr><tr><td>SA: Single-shot LLM call</td><td>0.4492</td><td>0.5174</td><td>0.4898</td><td>0.6316</td></tr><tr><td>RC: Ranker+Evaluator</td><td>0.4379</td><td>0.5084</td><td>0.4788</td><td>0.6247</td></tr><tr><td>PR: Profiler+Ranker</td><td>0.4537</td><td>0.5243</td><td>0.4919</td><td>0.6368</td></tr><tr><td>PPR: Planner+Profiler+Ranker</td><td>0.4617</td><td>0.5272</td><td>0.5069</td><td>0.6401</td></tr><tr><td>PENS: Planner+3 Rankers+Arb.</td><td>0.4725</td><td>0.5366</td><td>0.5162</td><td>0.6471</td></tr><tr><td>PPENS: Planner+Profiler+3 Rankers+Arb.</td><td>0.4704</td><td>0.5290</td><td>0.5202</td><td>0.6416</td></tr><tr><td>DEB: Two-agent Debate</td><td>0.4533</td><td>0.5215</td><td>0.4946</td><td>0.6349</td></tr><tr><td>Random baseline</td><td>0.1833</td><td>0.2929</td><td>0.2131</td><td>0.4544</td></tr></table>

## 6.5 Role-by-Role Analysis: What Each Agent Contributes

Reading the two quality tables by role family clarifies which forms of agentic structure carry the high-diversity gain and which do not.

<sub>Decomposition</sub> <sub>and</sub> <sub>specialisation.</sub> The planner and the profiler are the source of the steady, low-variance improvement on diverse inputs. Adding the profiler alone (PR) moves NDCG@10 from 0.6316 to 0.6368 on the high-diversity sample while leaving it slightly below the baseline on the random sample (0.7156 against 0.7197). Adding a planner on top (PPR) lifts NDCG@3 to 0.5069. The mechanism is intuitive: when a history spans many interests, articulating a ranking strategy and compressing the history into an explicit intent both reduce the burden on the final ranking step. When the history is already coherent, there is little to decompose, and the extra calls neither help nor hurt the ranking while still costing tokens. This is the empirical content of capability (i), planning and task decomposition.

<sub>Ensembling</sub> <sub>and</sub> <sub>aggregation.</sub> The largest high-diversity gains come from the ensemble pipelines PEns and PPEns, which lead at NDCG@10 and NDCG@3 respectively. Sampling several rankers at elevated temperature and reconciling them with an arbitrator recovers signal that any single sample misses, which matters precisely when the input is ambiguous. This is also the most expensive family, so its advantage is real but costly.

<sub>Iterative</sub> <sub>and</sub> <sub>adversarial</sub> <sub>refinement.</sub> This family is the weakest. The evaluator pipeline (RC) is the worst performer on the random sample and remains below the baseline on the high-diversity sample, and the debate pipeline (Deb) is roughly neutral on both. The synthesis is that the gains observed in this study come from restructuring the input and aggregating diverse views, not from agents critiquing one another in a closed loop. Closed-loop critique without an external oracle tends, if anything, to introduce the cascading errors analyzed in Section 5.3.

## 6.6 The Profiler as Memory: Why Compression Helps on Diverse Histories

The profiler can be read through the memory formalism of Section 2.3. It instantiates the retention operator <sub>R</sub> of Definition 2.3 : it distills the raw history into a compact intent summary ${ \widetilde { C } } ,$ , on which the ranker then conditions through the retrieval operator <sub>Q</sub> of Definition 2.4. We are explicit that this is working-memory, or session-scoped, compression.

The evidence for the value of this memory mechanism is the profiler-only pipeline (PR). On the high-diversity sample it improves NDCG@10 from 0.6316 to 0.6368 and MRR@10 from 0.5174 to 0.5243, whereas on the random sample it sits marginally below the single shot LLM call (0.7156 against 0.7197 at NDCG@10). In other words, compressing a history into an explicit intent helps exactly when the history is rich enough to make compression informative, and is otherwise a small, avoidable expense.

## 7 Conclusion

This paper established a footing for agentic recommender systems: architectures in which stateful agents, memories, tools, communication protocols, and verification steps are composed to improve recommendation-layer outcomes. We began by formalizing the core building blocks, generic LLM agents, recommender agents, multi-agent systems, memory update and retrieval functions, and observable traces, and by bounding what is recommendation-specific in such a system. These abstractions unify design choices such as raw bufers, vector stores, knowledge graphs, procedural memories, and tool-mediated evidence retrieval into a vocabulary that is precise enough for evaluation while remaining implementation-flexible.

Building on this vocabulary, Section 5 surfaced the operational fault lines that accompany such flexibility. We organized the open problems into five challenge families, communication complexity and protocol design, scalability and cost, hallucination and error propagation, emergent misalignment and collusion, and brand, policy, and legal compliance, and connected each to recommender-specific manifestations and measurable signals such as ranking quality, evidence coverage, provenance and trace validity, latency, token cost, exposure disparity, policy-violation rate, and judge reliability. The recurring message is that progress depends not only on larger models but on the interaction rules, memory hierarchies, and incentive structures that govern how agents are composed.

Finally, the controlled study of Section 6 shows why agentic recommendation must be evaluated conditionally. More agents are not automatically better: on representative next-item ranking samples the single-agent baseline is the pareto eficient default, whereas decomposition and ensemble roles become useful for high-diversity user histories, and closed-loop self-criticism can even degrade ranking quality. This supports a practical design principle in which agentic complexity is routed to the inputs where its marginal quality gain justifies its added latency, cost, and governance risk, and an evaluation agenda in which that trade-of, rather than top-?? accuracy alone, is what future work should report.

## References

[1] Swapnaja Achintalwar, Ioana Baldini, Djallel Bounefouf, Joan Byamugisha, Maria Chang, Pierre Dognin, Eitan Farchi, Ndivhuwo Makondo, Aleksandra Mojsilović, Manish Nagireddy, et al. 2024. Alignment studio: Aligning large language models to particular contextual regulations. <sub>IEEE</sub> <sub>Internet</sub> <sub>Computing</sub> (2024).

[2] Abdul Basit Ahanger, Syed Wajid Aalam, Muzafar Rasool Bhat, and Assif Assad. 2022. Popularity bias in recommender <sup>systems-a</sup> <sup>review.</sup> <sup>In</sup> International Conference on Emerging Technologies in Computer Engineering<sup>.</sup> <sup>Springer,</sup> <sup>431–444.</sup>

[3] Chenxin An, Jun Zhang, Ming Zhong, Lei Li, Shansan Gong, Yao Luo, Jingjing Xu, and Lingpeng Kong. 2024. Why Does the Efective Context Length of LLMs Fall Short? <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2410.18745</sub> (2024)

[4] Petr Anokhin, Nikita Semenov, Artyom Sorokin, Dmitry Evseev, Andrey Kravchenko, Mikhail Burtsev, and Evgeny Burnaev. 2024. Arigraph: Learning knowledge graph world models with episodic memory for llm agents. <sub>arXiv</sub> <sub>preprint</sub> arXiv:2407.04363 <sup>(2024).</sup>

[5] Ashmi Banerjee, Fitri Nur Aisyah, Adithi Satish, Wolfgang Wörndl, and Yashar Deldjoo. 2025. Collab-REC: An LLM-based Agentic Framework for Balancing Recommendations in Tourism. <sub>CoRR</sub> abs/2508.15030 (2025). doi:10. 48550/ARXIV.2508.15030 arXiv:2508.15030

[6] Sebastian Borgeaud, Arthur Mensch, Jordan Hofmann, Trevor Cai, Eliza Rutherford, Katie Millican, George Bm Van Den Driessche, Jean-Baptiste Lespiau, Bogdan Damoc, Aidan Clark, et al. 2022. Improving language models by retrieving from trillions of tokens. In <sub>International</sub> <sub>conference</sub> <sub>on</sub> <sub>machine</sub> <sub>learning</sub>. PMLR, 2206–2240.

[7] Qiqi Cai, Jian Cao, Guandong Xu, and Nengjun Zhu. 2024. Distributed Recommendation Systems: Survey and Research <sup>Directions.</sup> ACM Transactions on Information Systems <sup>43,</sup> <sup>1</sup> <sup>(2024),</sup> <sup>1–38.</sup>

[8] Jiao Chen, Kehui Yao, Reza Yousefi Maragheh, Kai Zhao, Jianpeng Xu, Jason Cho, Evren Korpeoglu, Sushant Kumar, and Kannan Achan. 2025. CARTS: Collaborative Agents for Recommendation Textual Summarization. <sub>arXiv</sub> <sub>preprint</sub> arXiv:2506.17765 <sup>(2025).</sup>

[9] Luyu Chen, Quanyu Dai, Zeyu Zhang, Xueyang Feng, Mingyu Zhang, Pengcheng Tang, Xu Chen, Yue Zhu, and Zhenhua Dong. 2025. Recusersim: A realistic and diverse user simulator for evaluating conversational recommender <sup>systems.</sup> <sup>In</sup> Companion Proceedings of the ACM on Web Conference 2025<sup>.</sup> <sup>133–142.</sup>

[10] Pin-Yu Chen, Han Shen, Payel Das, and Tianyi Chen. 2025. Fundamental Safety-Capability Trade-ofs in Fine-tuning <sup>Large</sup> <sup>Language</sup> <sup>Models.</sup> arXiv preprint arXiv:2503.20807 <sup>(2025).</sup>

[11] Konstantina Christakopoulou, Filip Radlinski, and Katja Hofmann. 2016. Towards conversational recommender <sup>systems.</sup> <sup>In</sup> Proceedings of the 22nd ACM SIGKDD international conference on knowledge discovery and data mining<sup>.</sup> 815–824.

[12] Damien de Mijolla, Wen Yang, Philippa Duckett, Christopher Frye, and Mark Worrall. 2024. Language hooks: a modular framework for augmenting LLM reasoning that decouples tool usage from the model and its prompt. <sub>arXiv</sub> <sub>preprint</sub> arXiv:2412.05967 <sup>(2024).</sup>

[13] Yashar Deldjoo, Zhankui He, Julian McAuley, Anton Korikov, Scott Sanner, Arnau Ramisa, René Vidal, Maheswaran Sathiamoorthy, Atoosa Kasirzadeh, and Silvia Milano. 2024. A Review of Modern Recommender Systems using <sup>Generative</sup> <sup>Models</sup> <sup>(Gen-RecSys).</sup> <sup>In</sup> Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data <sub>Mining</sub>. 6448–6458.

[14] Yashar Deldjoo, Zhankui He, Julian McAuley, Anton Korikov, Scott Sanner, Arnau Ramisa, Rene Vidal, Maheswaran Sathiamoorthy, Atoosa Kasrizadeh, Silvia Milano, et al. 2024. Recommendation with Generative Models. <sub>arXiv</sub> <sub>preprint</sub> arXiv:2409.15173 <sup>(2024).</sup>

[15] Yilun Du, Shuang Li, Antonio Torralba, Joshua B. Tenenbaum, and Igor Mordatch. 2024. Improving Factuality and <sup>Reasoning</sup> <sup>in</sup> <sup>Language</sup> <sup>Models</sup> <sup>through</sup> <sup>Multiagent</sup> <sup>Debate.</sup> <sup>In</sup> Forty-first International Conference on Machine Learning, ICML 2024, Vienna, Austria, July 21-27, 2024 (Proceedings of Machine Learning Research, Vol. 235)<sup>,</sup> <sup>Ruslan</sup> <sup>Salakhutdinov,</sup> Zico Kolter, Katherine A. Heller, Adrian Weller, Nuria Oliver, Jonathan Scarlett, and Felix Berkenkamp (Eds.). PMLR OpenReview.net, 11733–11763. https://proceedings.mlr.press/v235/du24e.html

[16] Lutfi Eren Erdogan, Nicholas Lee, Sehoon Kim, Suhong Moon, Hiroki Furuta, Gopala Anumanchipalli, Kurt Keutzer, and Amir Gholami. 2025. Plan-and-act: Improving planning of agents for long-horizon tasks. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2503.09572</sub> (2025).

[17] Jiabao Fang, Shen Gao, Pengjie Ren, Xiuying Chen, Suzan Verberne, and Zhaochun Ren. 2024. A multi-agent conversa tional recommender system. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2402.01135</sub> (2024)

[18] Libo Feng, Hui Zhang, Yong Chen, and Liqi Lou. 2018. Scalable dynamic multi-agent practical byzantine fault-tolerant consensus in permissioned blockchain. <sub>Applied</sub> <sub>Sciences</sub> 8, 10 (2018), 1919.

[19] Aleksander Ficek, Jiaqi Zeng, and Oleksii Kuchaiev. 2024. GPT vs RETRO: Exploring the Intersection of Retrieval <sup>and</sup> <sup>Parameter-Eficient</sup> <sup>Fine-Tuning.</sup> <sup>In</sup> Proceedings of the 2024 Conference on Empirical Methods in Natural Language <sub>Processing</sub>. 19425–19432.

[20] Joao Fonseca, Andrew Bell, and Julia Stoyanovich. 2025. Safeguarding Large Language Models in Real-time with Tunable Safety-Performance Trade-ofs. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2501.02018</sub> (2025)

[21] Najmeh Forouzandehmehr, Reza Yousefi Maragheh, Sriram Kollipara, Kai Zhao, Topojoy Biswas, Evren Korpeoglu, and Kannan Achan. 2025. CAL-RAG: Retrieval-Augmented Multi-Agent Generation for Content-Aware Layout Design. arXiv:2506.21934 [cs.IR] https://arxiv.org/pdf/2506.21934

[22] Zafeirios Fountas, Martin A Benfeghoul, Adnan Oomerjee, Fenia Christopoulou, Gerasimos Lampouras, Haitham Bou-Ammar, and Jun Wang. 2024. Human-like episodic memory for infinite context llms. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2407.09450</sub> (2024).

[23] Chongming Gao, Wenqiang Lei, Xiangnan He, Maarten De Rijke, and Tat-Seng Chua. 2021. Advances and challenges in conversational recommender systems: A survey. <sub>AI</sub> <sub>open</sub> 2 (2021), 100–126.

[24] Jing Guo, Nan Li, Jianchuan Qi, Hang Yang, Ruiqiao Li, Yuzhen Feng, Si Zhang, and Ming Xu. 2023. Empowering working memory for large language model agents. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2312.17259</sub> (2023).

[25] Kelvin Guu, Kenton Lee, Zora Tung, Panupong Pasupat, and Mingwei Chang. 2020. Retrieval augmented language <sup>model</sup> <sup>pre-training.</sup> <sup>In</sup> International conference on machine learning<sup>.</sup> <sup>PMLR,</sup> <sup>3929–3938.</sup>

[26] Shanshan Han, Qifan Zhang, Yuhang Yao, Weizhao Jin, and Zhaozhuo Xu. 2024. LLM multi-agent systems: Challenges <sup>and</sup> <sup>open</sup> <sup>problems.</sup> arXiv preprint arXiv:2402.03578 <sup>(2024).</sup>

[27] Shibo Hao, Tianyang Liu, Zhen Wang, and Zhiting Hu. 2023. Toolkengpt: Augmenting frozen language models with massive tools via tool embeddings. <sub>Advances</sub> <sub>in</sub> <sub>neural</sub> <sub>information</sub> <sub>processing</sub> <sub>systems</sub> 36 (2023), 45870–45894.

[28] Heidy Hazem, Ahmed Awad, and Ahmed Hassan Yousef. 2023. A distributed real-time recommender system for big data streams. <sub>Ain</sub> <sub>Shams</sub> <sub>Engineering</sub> <sub>Journal</sub> 14, 8 (2023), 102026.

[29] Balázs Hidasi, Alexandros Karatzoglou, Linas Baltrunas, and Domonkos Tikk. 2016. Session-based Recommendations <sup>with</sup> <sup>Recurrent</sup> <sup>Neural</sup> <sup>Networks.</sup> <sup>In</sup> 4th International Conference on Learning Representations, ICLR 2016, San Juan, Puerto <sub>Rico,</sub> <sub>May</sub> <sub>2-4,</sub> <sub>2016,</sub> <sub>Conference</sub> <sub>Track</sub> <sub>Proceedings</sub>, Yoshua Bengio and Yann LeCun (Eds.). http://arxiv.org/abs/1511.06939

[30] Yupeng Hou, Jiacheng Li, Zhankui He, An Yan, Xiusi Chen, and Julian J. McAuley. 2024. Bridging Language and Items for Retrieval and Recommendation. <sub>CoRR</sub> abs/2403.03952 (2024). doi:10.48550/ARXIV.2403.03952 arXiv:2403.03952

[31] Xu Huang, Jianxun Lian, Yuxuan Lei, Jing Yao, Defu Lian, and Xing Xie. 2025. Recommender ai agent: Integrating large language models for interactive recommendations. <sub>ACM</sub> <sub>Transactions</sub> <sub>on</sub> <sub>Information</sub> <sub>Systems</sub> 43, 4 (2025), 1–33.

[32] Wang-Cheng Kang and Julian McAuley. 2018. Self-attentive sequential recommendation. In <sub>2018</sub> <sub>IEEE</sub> <sub>international</sub> conference on data mining (ICDM)<sup>.</sup> <sup>IEEE,</sup> <sup>197–206.</sup>

[33] Yehuda Koren, Robert Bell, and Chris Volinsky. 2009. Matrix Factorization Techniques for Recommender Systems. <sub>Computer</sub> 42, 8 (2009), 30–37. doi:10.1109/MC.2009.263

[34] John E Laird, Allen Newell, and Paul S Rosenbloom. 1987. Soar: An architecture for general intelligence. <sub>Artificial</sub> <sub>intelligence</sub> 33, 1 (1987), 1–64.

[35] LangChain. 2024. LangChain Memory Types — Conceptual Guide. https://langchain-ai.github.io/langmem/concepts/ conceptual\_guide/#memory-types Accessed: 2025-06-21.

[36] Mike Lewis, Denis Yarats, Yann Dauphin, Devi Parikh, and Dhruv Batra. 2017. Deal or No Deal? End-to-End Learning <sup>of</sup> <sup>Negotiation</sup> <sup>Dialogues.</sup> <sup>In</sup> Proceedings of the 2017 Conference on Empirical Methods in Natural Language Processing<sup>.</sup> 2443–2453.

[37] Junyou Li, Qin Zhang, Yangbin Yu, Qiang Fu, and Deheng Ye. 2024. More Agents Is All You Need. <sub>Trans.</sub> <sub>Mach.</sub> <sub>Learn.</sub> <sub>Res.</sub> 2024 (2024). https://openreview.net/forum?id=bgzUSZ8aeg

[38] Kun Li, Xin Jing, and Chengang Jing. 2024. Vector Storage Based Long-term Memory Research on LLM. <sub>International</sub> Journal of Advanced Network, Monitoring and Controls <sup>(2024).</sup>

[39] Lei Li, Yongfeng Zhang, Dugang Liu, and Li Chen. 2024. Large language models for generative recommendation: A <sup>survey</sup> <sup>and</sup> <sup>visionary</sup> <sup>discussions.</sup> <sup>In</sup> Proceedings of the 2024 joint international conference on computational linguistics, language resources and evaluation (LREC-COLING 2024)<sup>.</sup> <sup>10146–10159.</sup>

[40] Zongqian Li, Yinhong Liu, Yixuan Su, and Nigel Collier. 2024. Prompt compression for large language models: A <sup>survey.</sup> arXiv preprint arXiv:2410.12388 <sup>(2024).</sup>

[41] Jan Malte Lichtenberg, Alexander Buchholz, and Pola Schwöbel. 2024. Large language models as recommender systems: A study of popularity bias. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2406.01285</sub> (2024).

[42] Jiahao Liu, Shengkang Gu, Dongsheng Li, Guangping Zhang, Mingzhe Han, Hansu Gu, Peng Zhang, Tun Lu, Li Shang, and Ning Gu. 2025. Enhancing Cross-Domain Recommendations with Memory-Optimized LLM-Based User Agents. <sub>arXiv</sub> <sub>e-prints</sub> (2025), arXiv–2502.

[43] Nelson F Liu, Kevin Lin, John Hewitt, Ashwin Paranjape, Michele Bevilacqua, Fabio Petroni, and Percy Liang. 2024. Lost in the Middle: How Language Models Use Long Contexts. <sub>Transactions</sub> <sub>of</sub> <sub>the</sub> <sub>Association</sub> <sub>for</sub> <sub>Computational</sub> <sub>Linguistics</sub> 11 (2024), 157–173.

[44] Xuan Liu, Jie Zhang, Haoyang Shang, Song Guo, Chengxu Yang, and Quanyan Zhu. 2024. Exploring prosocia irrationality for llm agents: A social cognition view. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2405.14744</sub> (2024).

[45] Yuxing Lu and Jinzhuo Wang. 2025. KARMA: Leveraging Multi-Agent LLMs for Automated Knowledge Graph <sup>Enrichment.</sup> arXiv preprint arXiv:2502.06472 <sup>(2025).</sup>

[46] Junyu Luo, Weizhi Zhang, Ye Yuan, Yusheng Zhao, Junwei Yang, Yiyang Gu, Bohan Wu, Binqi Chen, Ziyue Qiao, Qingqing Long, Rongcheng Tu, Xiao Luo, Wei Ju, Zhiping Xiao, Yifan Wang, Meng Xiao, Chenwu Liu, Jingyang Yuan, Shichang Zhang, Yiqiao Jin, Fan Zhang, Xian Wu, Hanqing Zhao, Dacheng Tao, Philip S. Yu, and Ming Zhang. 2025. Large Language Model Agent: A Survey on Methodology, Applications and Challenges. <sub>CoRR</sub> abs/2503.21460 (2025). doi:10.48550/ARXIV.2503.21460 arXiv:2503.21460

[47] Aman Madaan, Niket Tandon, Prakhar Gupta, Skyler Hallinan, Luyu Gao, Sarah Wiegrefe, Uri Alon, Nouha Dziri, Shrimai Prabhumoye, Yiming Yang, Shashank Gupta, Bodhisattwa Prasad Majumder, Katherine Hermann, Sean Welleck, Amir Yazdanbakhsh, and Peter Clark. 2023. Self-Refine: Iterative Refinement with Self-Feedback. In <sub>Ad-</sub> vances in Neural Information Processing Systems 36: Annual Conference on Neural Information Processing Systems 2023, <sub>NeurIPS</sub> <sub>2023,</sub> <sub>New</sub> <sub>Orleans,</sub> <sub>LA,</sub> <sub>USA,</sub> <sub>December</sub> <sub>10</sub> <sub>-</sub> <sub>16,</sub> <sub>2023</sub>. http://papers.nips.cc/paper\_files/paper/2023/hash 91edf07232fb1b55a505a9e9f6c0f3-Abstract-Conference.htm

[48] Adyasha Maharana, Dong-Ho Lee, Sergey Tulyakov, Mohit Bansal, Francesco Barbieri, and Yuwei Fang. 2024. Evaluating <sup>Very</sup> <sup>Long-Term</sup> <sup>Conversational</sup> <sup>Memory</sup> <sup>of</sup> <sup>LLM</sup> <sup>Agents.</sup> <sup>In</sup> Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)<sup>.</sup> <sup>13851–13870.</sup>

[49] Potsawee Manakul, Adian Liusie, and Mark JF Gales. 2023. Selfcheckgpt: Zero-resource black-box hallucination detection for generative large language models. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2303.08896</sub> (2023).

[50] Reza Yousefi Maragheh, Chenhao Fang, Charan Chand Irugu, Parth Parikh, Jason Cho, Jianpeng Xu, Saranyan Sukumar, Malay Patel, Evren Korpeoglu, Sushant Kumar, et al. 2023. LLM-TAKE: Theme-aware keyword extraction using large <sup>language</sup> <sup>models.</sup> <sup>In</sup> 2023 IEEE International Conference on Big Data (BigData)<sup>.</sup> <sup>IEEE,</sup> <sup>4318–4324.</sup>

<sup>[51]</sup> <sup>Silvano</sup> <sup>Martello</sup> <sup>and</sup> <sup>Paolo</sup> <sup>Toth.</sup> <sup>1990.</sup> Knapsack problems: algorithms and computer implementations<sup>.</sup> <sup>John</sup> <sup>Wiley</sup> <sup>&</sup> Sons, Inc.

[52] Chenlin Ming, Jiacheng Lin, Pangkit Fong, Han Wang, Xiaoming Duan, and Jianping He. 2023. Hicrisp: A hierarchica closed-loop robotic intelligent self-correction planner. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2309.12089</sub> (2023).

[53] Fangwen Mu, Junjie Wang, Lin Shi, Song Wang, Shoubin Li, and Qing Wang. 2025. EXPEREPAIR: Dual-Memory Enhanced LLM-based Repository-Level Program Repair. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2506.10484</sub> (2025).

[54] Sid Nayak, Adelmo Morrison Orozco, Marina Have, Jackson Zhang, Vittal Thirumalai, Darren Chen, Aditya Kapoor, Eric Robinson, Karthik Gopalakrishnan, James Harrison, et al. 2024. Long-horizon planning for multi-agent robots in partially observable environments. <sub>Advances</sub> <sub>in</sub> <sub>Neural</sub> <sub>Information</sub> <sub>Processing</sub> <sub>Systems</sub> 37 (2024), 67929–67967.

[55] Emil Noordeh, Roman Levin, Ruochen Jiang, and Harris Shadmany. 2020. Echo chambers in collaborative filtering based recommendation systems. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2011.03890</sub> (2020).

[56] Bo Pan, Jiaying Lu, Ke Wang, Li Zheng, Zhen Wen, Yingchaojie Feng, Minfeng Zhu, and Wei Chen. 2024. AgentCoord: Visually exploring coordination strategy for llm-based multi-agent collaboration. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2404.11943</sub> (2024).

[57] Bhargavi Paranjape, Scott Lundberg, Sameer Singh, Hannaneh Hajishirzi, Luke Zettlemoyer, and Marco Tulio Ribeiro. 2023. Art: Automatic multi-step reasoning and tool-use for large language models. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2303.09014</sub> (2023).

[58] Qiyao Peng, Hongtao Liu, Hua Huang, Qing Yang, and Minglai Shao. 2025. A Survey on LLM-powered Agents for <sup>Recommender</sup> <sup>Systems.</sup> arXiv preprint arXiv:2502.10050 <sup>(2025).</sup>

[59] Mathis Pink, Qinyuan Wu, Vy Ai Vo, Javier Turek, Jianing Mu, Alexander Huth, and Mariya Toneva. 2025. Position: Episodic Memory is the Missing Piece for Long-Term LLM Agents. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2502.06975</sub> (2025).

[60] Stefan Poslad. 2007. Specifying protocols for multi-agent systems interaction. <sub>ACM</sub> <sub>Transactions</sub> <sub>on</sub> <sub>Autonomous</sub> <sub>and</sub> Adaptive Systems (TAAS) <sup>2,</sup> <sup>4</sup> <sup>(2007),</sup> <sup>15–es.</sup>

[61] Archiki Prasad, Alexander Koller, Mareike Hartmann, Peter Clark, Ashish Sabharwal, Mohit Bansal, and Tushar Khot. 2024. ADaPT: As-Needed Decomposition and Planning with Language Models. In <sub>Findings</sub> <sub>of</sub> <sub>the</sub> <sub>Association</sub> <sub>for</sub> Computational Linguistics: NAACL 2024, Mexico City, Mexico, June 16-21, 2024 (Findings of ACL, Vol. NAACL 2024)<sup>.</sup> Association for Computational Linguistics, 4226–4252. doi:10.18653/V1/2024.FINDINGS-NAACL.264

[62] Preston Rasmussen, Pavlo Paliychuk, Travis Beauvais, Jack Ryan, and Daniel Chalef. 2025. Zep: A Temporal Knowledge Graph Architecture for Agent Memory. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2501.13956</sub> (2025).

[63] Stefen Rendle, Christoph Freudenthaler, Zeno Gantner, and Lars Schmidt-Thieme. 2009. BPR: Bayesian personalized <sup>ranking</sup> <sup>from</sup> <sup>implicit</sup> <sup>feedback.</sup> <sup>In</sup> Proceedings of the Twenty-Fifth Conference on Uncertainty in Artificial Intelligence<sup>.</sup> 452–461.

[64] Timo Schick, Jane Dwivedi-Yu, Roberto Dessì, Roberta Raileanu, Maria Lomeli, Eric Hambro, Luke Zettlemoyer, Nicola Cancedda, and Thomas Scialom. 2023. Toolformer: Language models can teach themselves to use tools. <sub>Advances</sub> <sub>in</sub> Neural Information Processing Systems <sup>36</sup> <sup>(2023),</sup> <sup>68539–68551.</sup>

[65] Lianlei Shan, Shixian Luo, Zezhou Zhu, Yu Yuan, and Yong Wu. 2025. Cognitive memory in large language models. arXiv preprint arXiv:2504.02441 <sup>(2025).</sup>

[66] Yongliang Shen, Kaitao Song, Xu Tan, Dongsheng Li, Weiming Lu, and Yueting Zhuang. 2023. Hugginggpt: Solving ai tasks with chatgpt and its friends in hugging face. <sub>Advances</sub> <sub>in</sub> <sub>Neural</sub> <sub>Information</sub> <sub>Processing</sub> <sub>Systems</sub> 36 (2023), 38154–38180.

[67] Adi Simhi, Itay Itzhak, Fazl Barez, Gabriel Stanovsky, and Yonatan Belinkov. 2025. Trust Me, I’m Wrong: High-Certainty <sup>Hallucinations</sup> <sup>in</sup> <sup>LLMs.</sup> arXiv preprint arXiv:2502.12964 <sup>(2025).</sup>

[68] AP News Staf. 2017. Amazon removes “frequently bought together” items used to make explosives. https://apnews. com/article/604a73f6008846449c303fb4b93e9d6. Accessed: 2025-06-29.

[69] Chris Stokel-Walker. 2024. Google and Character.AI are being sued after chatbot allegedly told a 17-year-old to kill his parents. https://www.businessinsider.com/characterai-google-lawsuit-chatbot-teen-kill-parents-2024-12. Accessed: 2025-06-29.

[70] Nicholas Sukiennik, Haoyu Wang, Zailin Zeng, Chen Gao, and Yong Li. 2025. Simulating Filter Bubble on Short-video Recommender System with Large Language Model Agents. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2504.08742</sub> (2025).

[71] Theodore Sumers, Shunyu Yao, Karthik Narasimhan, and Thomas Grifiths. 2023. Cognitive architectures for language <sup>agents.</sup> Transactions on Machine Learning Research <sup>(2023).</sup>

[72] Haotian Sun, Yuchen Zhuang, Lingkai Kong, Bo Dai, and Chao Zhang. 2023. Adaplanner: Adaptive planning from feedback with language models. <sub>Advances</sub> <sub>in</sub> <sub>neural</sub> <sub>information</sub> <sub>processing</sub> <sub>systems</sub> 36 (2023), 58202–58245.

[73] Ding Tong, Qifeng Qiao, Ting-Po Lee, James McInerney, and Justin Basilico. 2023. Navigating the feedback loop in recommender systems: Insights and strategies from industry practice. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> <sub>17th</sub> <sub>ACM</sub> <sub>Conference</sub> <sub>on</sub> Recommender Systems<sup>.</sup> <sup>1058–1061.</sup>

[74] Mehmet Ugurbil, Dimitris Mouris, Manuel B Santos, José Cabrero-Holgueras, Miguel de Vega, and Shubho Sengupta. 2025. Fission: Distributed Privacy-Preserving Large Language Model Inference. <sub>Cryptology</sub> <sub>ePrint</sub> <sub>Archive</sub> (2025).

[75] Lei Wang, Jingsen Zhang, Xiaowen Chen, Yankai Lin, Ruihua Song, Wayne Xin Zhao, and Ji-Rong Wen. 2023. Recagent: A novel simulation paradigm for recommender systems. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2306.02552</sub> (2023).

[76] Yancheng Wang, Ziyan Jiang, Zheng Chen, Fan Yang, Yingxue Zhou, Eunah Cho, Xing Fan, Yanbin Lu, Xiaojiang Huang, and Yingzhen Yang. 2024. RecMind: Large Language Model Powered Agent For Recommendation. In <sub>Findings</sub> of the Association for Computational Linguistics: NAACL 2024<sup>.</sup> <sup>4351–4364.</sup>

[77] Zhefan Wang, Yuanqing Yu, Wendi Zheng, Weizhi Ma, and Min Zhang. 2024. Macrec: A multi-agent collaboration <sup>framework</sup> <sup>for</sup> <sup>recommendation.</sup> <sup>In</sup> Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval<sup>.</sup> <sup>2760–2764.</sup>

[78] Schaun Wheeler and Olivier Jeunen. 2025. Procedural memory is not all you need: Bridging cognitive gaps in llm-based <sup>agents.</sup> <sup>In</sup> Adjunct Proceedings of the 33rd ACM Conference on User Modeling, Adaptation and Personalization<sup>.</sup> <sup>360–364.</sup>

[79] Likang Wu, Zhi Zheng, Zhaopeng Qiu, Hao Wang, Hongchao Gu, Tingjia Shen, Chuan Qin, Chen Zhu, Hengshu Zhu, Qi Liu, et al. 2024. A survey on large language models for recommendation. <sub>World</sub> <sub>Wide</sub> <sub>Web</sub> 27, 5 (2024), 60.

[80] Yunjia Xi, Weiwen Liu, Jianghao Lin, Bo Chen, Ruiming Tang, Weinan Zhang, and Yong Yu. 2024. MemoCRS: Memoryenhanced Sequential Conversational Recommender Systems with Large Language Models. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> <sub>33rd</sub> ACM International Conference on Information and Knowledge Management<sup>.</sup> <sup>2585–2595.</sup>

[81] Zidi Xiong, Yuping Lin, Wenya Xie, Pengfei He, Jiliang Tang, Himabindu Lakkaraju, and Zhen Xiang. 2025. How Memory Management Impacts LLM Agents: An Empirical Study of Experience-Following Behavior. <sub>arXiv</sub> <sub>preprint</sub> arXiv:2505.16067 <sup>(2025).</sup>

[82] Wujiang Xu, Kai Mei, Hang Gao, Juntao Tan, Zujie Liang, and Yongfeng Zhang. 2025. A-mem: Agentic memory for <sup>llm</sup> <sup>agents.</sup> arXiv preprint arXiv:2502.12110 <sup>(2025).</sup>

[83] Zhengyu Yang, Danlin Jia, Stratis Ioannidis, Ningfang Mi, and Bo Sheng. 2018. Intermediate data caching optimization <sup>for</sup> <sup>multi-stage</sup> <sup>and</sup> <sup>parallel</sup> <sup>big</sup> <sup>data</sup> <sup>frameworks.</sup> <sup>In</sup> 2018 IEEE 11th International Conference on Cloud Computing <sub>(CLOUD)</sub>. IEEE, 277–284.

[84] Shunyu Yao, Jefrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, and Yuan Cao. 2023. React: Synergizing <sup>reasoning</sup> <sup>and</sup> <sup>acting</sup> <sup>in</sup> <sup>language</sup> <sup>models.</sup> <sup>In</sup> International Conference on Learning Representations (ICLR)

[85] Hongbin Ye, Honghao Gui, Xin Xu, Xi Chen, Huajun Chen, and Ningyu Zhang. 2023. Schema-adaptable Knowledge <sup>Graph</sup> <sup>Construction.</sup> <sup>In</sup> Findings of the Association for Computational Linguistics: EMNLP 2023<sup>.</sup> <sup>6408–6431.</sup>

[86] Reza Yousefi Maragheh, Pratheek Vadla, Priyank Gupta, Kai Zhao, Aysenur Inan, Kehui Yao, Jianpeng Xu, Praveen Kanumala, Jason Cho, and Sushant Kumar. 2025. ARAG: Agentic Retrieval Augmented Generation for Personalized Recommendation. arXiv:2506.21931 [cs.IR] https://arxiv.org/pdf/2506.21931

[87] Zhenrui Yue, Sara Rabhi, Gabriel de Souza Pereira Moreira, Dong Wang, and Even Oldridge. 2023. Llamarec: Two-stage recommendation using large language models for ranking. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2311.02089</sub> (2023).

[88] Ruihong Zeng, Jinyuan Fang, Siwei Liu, and Zaiqiao Meng. 2024. On the Structural Memory of LLM Agents. <sub>arXiv</sub> preprint arXiv:2412.15266 <sup>(2024).</sup>

[89] An Zhang, Yuxin Chen, Leheng Sheng, Xiang Wang, and Tat-Seng Chua. 2024. On generative agents in recommendation. <sup>In</sup> Proceedings of the 47th international ACM SIGIR conference on research and development in Information Retrieval<sup>.</sup>

1807–1817.

[90] Jizhi Zhang, Keqin Bao, Wenjie Wang, Yang Zhang, Wentao Shi, Wanhong Xu, Fuli Feng, and Tat-Seng Chua. 2024. Prospect Personalized Recommendation on Large Language Model-based Agent Platform. <sub>CoRR</sub> abs/2402.18240 (2024). doi:10.48550/ARXIV.2402.18240 arXiv:2402.18240

[91] Yu Zhang, Shutong Qiao, Jiaqi Zhang, Tzu-Heng Lin, Chen Gao, and Yong Li. 2025. A Survey of Large Language Model Empowered Agents for Recommendation and Search: Towards Next-Generation Information Retrieval. <sub>arXiv</sub> <sub>preprint</sub> arXiv:2503.05659 <sup>(2025).</sup>

[92] Yuyue Zhao, Jiancan Wu, Xiang Wang, Wei Tang, Dingxian Wang, and Maarten De Rijke. 2024. Let me do it for you: Towards llm empowered recommendation via tool learning. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> <sub>47th</sub> <sub>International</sub> <sub>ACM</sub> <sub>SIGIR</sub> Conference on Research and Development in Information Retrieval<sup>.</sup> <sup>1796–1806.</sup>

[93] Zihuai Zhao, Wenqi Fan, Jiatong Li, Yunqing Liu, Xiaowei Mei, Yiqi Wang, Zhen Wen, Fei Wang, Xiangyu Zhao, Jiliang Tang, et al. 2024. Recommender systems in the era of large language models (llms). <sub>IEEE</sub> <sub>Transactions</sub> <sub>on</sub> <sub>Knowledge</sub> <sub>and</sub> <sub>Data</sub> <sub>Engineering</sub> 36, 11 (2024), 6889–6907.

[94] Jing Zhu, Chengfang Lu, Juanjuan Li, and Fei-Yue Wang. 2025. Secure Consensus Control on Multi-Agent Systems Based on Improved PBFT and Raft Blockchain Consensus Algorithms. <sub>IEEE/CAA</sub> <sub>Journal</sub> <sub>of</sub> <sub>Automatica</sub> <sub>Sinica</sub> 12, 7 (2025), 1407–1417.

## A Per-Category Empirical Results

Section 6 reported ranking quality and cost pooled over the four Amazon-2023 categories. This appendix disaggregates those pooled numbers into the individual categories (<sub>Amazon</sub> <sub>Fashion</sub>, <sub>Appliances</sub>, <sub>Electronics</sub>, and <sub>Toys</sub> <sub>and</sub> <sub>Games</sub>; ??<sub>=</sub>100 users per category and cohort) for both the random cohort (Tables 9 and 11) and the high-diversity cohort (Tables 10 and 12). Workflow identifiers follow Table 5; in every category block the best and second-best values per column among the seven LLM pipelines are shown in <sub>bold</sub> and underline, and the random-ranking baseline is listed once per table. Because each user has a single held-out positive, MAP@?? <sub>=</sub> MRR@??; we therefore report MRR (equivalently MAP) and NDCG, and include the MAP columns for completeness. The two headline findings of the main text, namely that single-shot ranking is hard to beat on typical users (Table 7) and that decomposition and ensembling pay of on diverse users (Table 8), both survive disaggregation, but the per-category view shows that each efect is unevenly distributed across categories.

## A.1 Ranking Quality by Category

<sub>Random</sub> <sub>cohort.</sub> Table 9 shows that the pooled near-tie between the single shot LLM call and the best multi-agent pipeline conceals substantial category heterogeneity. On <sub>Electronics</sub> the single shot LLM call (SA) is strictly best on all four reported cells, and the evaluator pipeline RC collapses to an NDCG@10 of 0.6602, about 8.6% below SA’s 0.7226; this is the clearest single-category instance of the error-propagation efect of Section 5.3. On the other three categories a multi-agent pipeline does edge ahead of SA, but the gains are small: PPEns leads on <sub>Toys</sub> <sub>and</sub> <sub>Games</sub> (NDCG@10 0.7491 vs. 0.7313, about <sub>+</sub>2.4%) at roughly six times the cost, Deb leads on <sub>Amazon</sub> <sub>Fashion</sub> (0.7364 vs. 0.7241, about <sub>+</sub>1.7%) at roughly four times the cost, and the inexpensive PR leads on <sub>Appliances</sub> (0.7114 vs. 0.7007, about <sub>+</sub>1.5%) at only about 1.5<sub>×</sub> the cost. Only the last of these is plausibly cost-justified, and even it is a sub-2% gain. The evaluator pipeline RC is the weakest LLM pipeline in every category, so the pooled conclusion that SA is Pareto-eficient on typical users is driven substantially by <sub>Electronics</sub>, with the remaining categories contributing only small, cost-ineficient multi-agent gains.

<sub>High-diversity</sub> <sub>cohort.</sub> Table 10 confirms that the multi-agent advantage on diverse histories holds in every category, but with a magnitude that tracks how much room the single shot LLM call leaves. The gains are largest on the categories where SA struggles most: on <sub>Amazon</sub> <sub>Fashion</sub>, PEns lifts NDCG@3 from 0.4323 to 0.5064 (about <sub>+</sub>17%) and NDCG@10 from 0.5943 to 0.6341 (about <sub>+</sub>6.7%); on <sub>Appliances</sub>, PPEns lifts NDCG@3 from 0.4886 to 0.5401 (about <sub>+</sub>10.5%) and PEns lifts NDCG@10 by about 3.9%. On <sub>Electronics</sub> the ensembling and decomposition pipelines lead more modestly (PEns NDCG@10 0.6389 vs. 0.6266, about <sub>+</sub>2.0%). <sub>Toys</sub> <sub>and</sub> <sub>Games</sub> is the boundary case: it has the highest single-agent baseline of the four categories, so there is little to recover, and the pure ensemble PEns actually dips below SA at NDCG@10 (0.6628 vs. 0.6772) while only Deb edges ahead (about <sub>+</sub>0.5%). This matches the paper’s mechanism: agentic restructuring helps when a single pass under-resolves the input, and a high-diversity history in an otherwise easy category does not always under-resolve it. RC is again the weakest pipeline throughout.

## A.2 Cost and Eficiency by Category

Tables 11 and 12 report input, output, and total tokens per query, parallel critical-path latency, and dollar cost per category. The ordering is identical in every category: the single shot LLM call is the floor on every column, the profiler–ranker pipeline PR is second, and the ensembles PEns and PPEns cost five to six times the single-agent baseline. The absolute cost, however, tracks history length and therefore varies by category: <sub>Electronics</sub> is the most token-heavy (random SA totals

Table 9. Per-category ranking quality on the random cohort (gpt-5-mini, <sup>??</sup>=<sup>100</sup> per category). Best and second-best per column among the LLM pipelines are bold and underlined; higher is beter. Because each user has one held-out positive, <sup>MAP@??</sup> = <sup>MRR@??</sup>, so the MAP columns repeat the MRR columns and are included only for completeness.

<table><tr><td rowspan="2">Method</td><td colspan="2">MRR</td><td colspan="2">NDCG</td><td colspan="2">MAP</td></tr><tr><td>@3</td><td>@10</td><td>@3</td><td>@10</td><td>@3</td><td>@10</td></tr><tr><td colspan="7">Amazon Fashion (n=100)</td></tr><tr><td>SA</td><td>0.5850</td><td>0.6380</td><td>0.6170</td><td>0.7241</td><td>0.5850</td><td>0.6380</td></tr><tr><td>RC</td><td>0.5683</td><td>0.6224</td><td>0.5996</td><td>0.7118</td><td>0.5683</td><td>0.6224</td></tr><tr><td>PR</td><td>0.5583</td><td>0.6156</td><td>0.5946</td><td>0.7077</td><td>0.5583</td><td>0.6156</td></tr><tr><td>PPR</td><td>0.5883</td><td>0.6357</td><td>0.6273</td><td>0.7231</td><td>0.5883</td><td>0.6357</td></tr><tr><td>PENS</td><td>0.6017</td><td>0.6467</td><td>0.6396</td><td>0.7313</td><td>0.6017</td><td>0.6467</td></tr><tr><td>PPENS</td><td>0.5900</td><td>0.6391</td><td>0.6259</td><td>0.7255</td><td>0.5900</td><td>0.6391</td></tr><tr><td>DEB</td><td>0.6067</td><td>0.6538</td><td>0.6407</td><td>0.7364</td><td>0.6067</td><td>0.6538</td></tr><tr><td colspan="7">Appliances (n=100)</td></tr><tr><td>SA</td><td>0.5617</td><td>0.6074</td><td>0.6023</td><td>0.7007</td><td>0.5617</td><td>0.6074</td></tr><tr><td>RC</td><td>0.5183</td><td>0.5739</td><td>0.5599</td><td>0.6753</td><td>0.5183</td><td>0.5739</td></tr><tr><td>PR</td><td>0.5783</td><td>0.6204</td><td>0.6223</td><td>0.7114</td><td>0.5783</td><td>0.6204</td></tr><tr><td>PPR</td><td>0.5467</td><td>0.5963</td><td>0.5883</td><td>0.6923</td><td>0.5467</td><td>0.5963</td></tr><tr><td>PENS</td><td>0.5483</td><td>0.5971</td><td>0.5894</td><td>0.6926</td><td>0.5483</td><td>0.5971</td></tr><tr><td>PPENS</td><td>0.5733</td><td>0.6197</td><td>0.6107</td><td>0.7097</td><td>0.5733</td><td>0.6197</td></tr><tr><td>DEB</td><td>0.5600</td><td>0.6085</td><td>0.5986</td><td>0.7016</td><td>0.5600</td><td>0.6085</td></tr><tr><td colspan="7">Electronics (n=100)</td></tr><tr><td>SA</td><td>0.5917</td><td>0.6355</td><td>0.6301</td><td>0.7226</td><td>0.5917</td><td>0.6355</td></tr><tr><td>RC</td><td>0.4967</td><td>0.5535</td><td>0.5438</td><td>0.6602</td><td>0.4967</td><td>0.5535</td></tr><tr><td>PR</td><td>0.5717</td><td>0.6166</td><td>0.6173</td><td>0.7087</td><td>0.5717</td><td>0.6166</td></tr><tr><td>PPR</td><td>0.5633</td><td>0.6074</td><td>0.6114</td><td>0.7022</td><td>0.5633</td><td>0.6074</td></tr><tr><td>PENS</td><td>0.5800</td><td>0.6295</td><td>0.6186</td><td>0.7183</td><td>0.5800</td><td>0.6295</td></tr><tr><td>PPENS</td><td>0.5483</td><td>0.5985</td><td>0.5927</td><td>0.6951</td><td>0.5483</td><td>0.5985</td></tr><tr><td>DEB</td><td>0.5717</td><td>0.6179</td><td>0.6151</td><td>0.7099</td><td>0.5717</td><td>0.6179</td></tr><tr><td colspan="7">Toys and Games (n=100)</td></tr><tr><td>SA</td><td>0.6000</td><td>0.6459</td><td>0.6407</td><td>0.7313</td><td>0.6000</td><td>0.6459</td></tr><tr><td>RC</td><td>0.5767</td><td>0.6340</td><td>0.6083</td><td>0.7216</td><td>0.5767</td><td>0.6340</td></tr><tr><td>PR</td><td>0.6017</td><td>0.6495</td><td>0.6423</td><td>0.7345</td><td>0.6017</td><td>0.6495</td></tr><tr><td>PPR</td><td>0.5850</td><td>0.6347</td><td>0.6244</td><td>0.7225</td><td>0.5850</td><td>0.6347</td></tr><tr><td>PENS</td><td>0.5867</td><td>0.6333</td><td>0.6283</td><td>0.7216</td><td>0.5867</td><td>0.6333</td></tr><tr><td>PPENS</td><td>0.6233</td><td>0.6704</td><td>0.6555</td><td>0.7491</td><td>0.6233</td><td>0.6704</td></tr><tr><td>DEB</td><td>0.6017</td><td>0.6518</td><td>0.6370</td><td>0.7356</td><td>0.6017</td><td>0.6518</td></tr><tr><td>Random baseline</td><td>0.1833</td><td>0.2929</td><td>0.2131</td><td>0.4544</td><td>0.1833</td><td>0.2929</td></tr></table>

2,050 tokens and PPEns 12,191), whereas <sub>Toys</sub> <sub>and</sub> <sub>Games</sub> is the lightest (high-diversity SA 1,497). The categories on which multi-agent pipelines help most are thus also among the most expensive to run them on, which sharpens rather than softens the cost–benefit tension of Section 6.2. The latency columns make the penalty on iterative refinement concrete: because RC and Deb cannot overlap their calls, they are the slowest pipelines in wall-clock terms even though they issue fewer calls than the ensembles. On random <sub>Electronics</sub>, for example, RC (72.1 s) and Deb (69.3 s) both exceed PEns (41.9 s), whose three rankers run concurrently, while SA stays the latency floor at 14.8 s. This reinforces the role analysis of Section 6.5: closed-loop critique is penalized on quality and on latency at the same time.

Table 10. Per-category ranking quality on the high-diversity cohort (gpt-5-mini, <sup>??</sup>=<sup>100</sup> per category). Best and second-best per column among the LLM pipelines are bold and underlined; higher is beter. The MAP columns coincide with the MRR columns (single positive).

<table><tr><td rowspan="2">Method</td><td colspan="2">MRR</td><td colspan="2">NDCG</td><td colspan="2">MAP</td></tr><tr><td>@3</td><td>@10</td><td>@3</td><td>@10</td><td>@3</td><td>@10</td></tr><tr><td colspan="7">Amazon Fashion (n=100)</td></tr><tr><td>SA</td><td>0.3917</td><td>0.4694</td><td>0.4323</td><td>0.5943</td><td>0.3917</td><td>0.4694</td></tr><tr><td>RC</td><td>0.4317</td><td>0.4998</td><td>0.4799</td><td>0.6189</td><td>0.4317</td><td>0.4998</td></tr><tr><td>PR</td><td>0.4200</td><td>0.5022</td><td>0.4533</td><td>0.6196</td><td>0.4200</td><td>0.5022</td></tr><tr><td>PPR</td><td>0.4200</td><td>0.4948</td><td>0.4714</td><td>0.6166</td><td>0.4200</td><td>0.4948</td></tr><tr><td>PENS</td><td>0.4567</td><td>0.5188</td><td>0.5064</td><td>0.6341</td><td>0.4567</td><td>0.5188</td></tr><tr><td>PPENS</td><td>0.4217</td><td>0.4917</td><td>0.4723</td><td>0.6132</td><td>0.4217</td><td>0.4917</td></tr><tr><td>DEB</td><td>0.3883</td><td>0.4776</td><td>0.4196</td><td>0.6004</td><td>0.3883</td><td>0.4776</td></tr><tr><td colspan="7">Appliances (n=100)</td></tr><tr><td>SA</td><td>0.4467</td><td>0.5128</td><td>0.4886</td><td>0.6281</td><td>0.4467</td><td>0.5128</td></tr><tr><td>RC</td><td>0.4283</td><td>0.4938</td><td>0.4775</td><td>0.6143</td><td>0.4283</td><td>0.4938</td></tr><tr><td>PR</td><td>0.4483</td><td>0.5189</td><td>0.4873</td><td>0.6329</td><td>0.4483</td><td>0.5189</td></tr><tr><td>PPR</td><td>0.4617</td><td>0.5229</td><td>0.5104</td><td>0.6373</td><td>0.4617</td><td>0.5229</td></tr><tr><td>PENS</td><td>0.4883</td><td>0.5434</td><td>0.5375</td><td>0.6527</td><td>0.4883</td><td>0.5434</td></tr><tr><td>PPENS</td><td>0.4883</td><td>0.5417</td><td>0.5401</td><td>0.6518</td><td>0.4883</td><td>0.5417</td></tr><tr><td>DEB</td><td>0.4650</td><td>0.5251</td><td>0.5125</td><td>0.6383</td><td>0.4650</td><td>0.5251</td></tr><tr><td colspan="7">Electronics (n=100)</td></tr><tr><td>SA</td><td>0.4450</td><td>0.5106</td><td>0.4899</td><td>0.6266</td><td>0.4450</td><td>0.5106</td></tr><tr><td>RC</td><td>0.3900</td><td>0.4685</td><td>0.4259</td><td>0.5928</td><td>0.3900</td><td>0.4685</td></tr><tr><td>PR</td><td>0.4433</td><td>0.5094</td><td>0.4886</td><td>0.6258</td><td>0.4433</td><td>0.5094</td></tr><tr><td>PPR</td><td>0.4550</td><td>0.5216</td><td>0.4975</td><td>0.6352</td><td>0.4550</td><td>0.5216</td></tr><tr><td>PENS</td><td>0.4567</td><td>0.5259</td><td>0.4988</td><td>0.6389</td><td>0.4567</td><td>0.5259</td></tr><tr><td>PPENS</td><td>0.4533</td><td>0.5113</td><td>0.5088</td><td>0.6285</td><td>0.4533</td><td>0.5113</td></tr><tr><td>DEB</td><td>0.4367</td><td>0.5016</td><td>0.4883</td><td>0.6204</td><td>0.4367</td><td>0.5016</td></tr><tr><td colspan="7">Toys and Games (n=100)</td></tr><tr><td>SA</td><td>0.5133</td><td>0.5769</td><td>0.5483</td><td>0.6772</td><td>0.5133</td><td>0.5769</td></tr><tr><td>RC</td><td>0.5017</td><td>0.5715</td><td>0.5320</td><td>0.6727</td><td>0.5017</td><td>0.5715</td></tr><tr><td>PR</td><td>0.5033</td><td>0.5668</td><td>0.5383</td><td>0.6691</td><td>0.5033</td><td>0.5668</td></tr><tr><td>PPR</td><td>0.5100</td><td>0.5694</td><td>0.5483</td><td>0.6715</td><td>0.5100</td><td>0.5694</td></tr><tr><td>PENS</td><td>0.4883</td><td>0.5582</td><td>0.5220</td><td>0.6628</td><td>0.4883</td><td>0.5582</td></tr><tr><td>PPENS</td><td>0.5183</td><td>0.5714</td><td>0.5596</td><td>0.6729</td><td>0.5183</td><td>0.5714</td></tr><tr><td>DEB</td><td>0.5233</td><td>0.5819</td><td>0.5581</td><td>0.6804</td><td>0.5233</td><td>0.5819</td></tr><tr><td>Random baseline</td><td>0.1833</td><td>0.2929</td><td>0.2131</td><td>0.4544</td><td>0.1833</td><td>0.2929</td></tr></table>

Table 11. Per-category cost and eficiency on the random cohort (gpt-5-mini, <sup>??</sup>=<sup>100</sup> per category). “Total” sums input and output tokens; “Lat. par” is the parallel critical-path latency in seconds; cost is in USD at \$0.25/\$2.00 per 1M input/output tokens. Lower is beter on every column; best and second-best per column are bold and underlined.

<table><tr><td>Method</td><td>In tok/q</td><td>Out tok/q</td><td>Total tok/q</td><td>Lat. par (s)</td><td>Cost/q (USD)</td></tr><tr><td colspan="6">Amazon Fashion (n=100)</td></tr><tr><td>SA</td><td>612</td><td>895</td><td>1,507</td><td>15.03</td><td>0.00194</td></tr><tr><td>RC</td><td>2,372</td><td>3,546</td><td>5,918</td><td>39.97</td><td>0.00768</td></tr><tr><td>PR</td><td>1,070</td><td>1,406</td><td>2,477</td><td>17.50</td><td>0.00308</td></tr><tr><td>PPR</td><td>1,769</td><td>2,047</td><td>3,816</td><td>20.68</td><td>0.00454</td></tr><tr><td>PENS</td><td>3,685</td><td>4,747</td><td>8,432</td><td>34.39</td><td>0.01041</td></tr><tr><td>PPENS</td><td>4,485</td><td>5,186</td><td>9,671</td><td>40.33</td><td>0.01149</td></tr><tr><td>DEB</td><td>2,766</td><td>3,808</td><td>6,574</td><td>56.88</td><td>0.00831</td></tr><tr><td colspan="6">Appliances (n=100)</td></tr><tr><td>SA</td><td>769</td><td>1,066</td><td>1,835</td><td>15.03</td><td>0.00232</td></tr><tr><td>RC</td><td>2,959</td><td>3,709</td><td>6,668</td><td>57.73</td><td>0.00816</td></tr><tr><td>PR</td><td>1,320</td><td>1,484</td><td>2,803</td><td>23.16</td><td>0.00330</td></tr><tr><td>PPR</td><td>2,171</td><td>2,144</td><td>4,315</td><td>24.99</td><td>0.00483</td></tr><tr><td>PENS</td><td>4,482</td><td>5,524</td><td>10,006</td><td>39.44</td><td>0.01217</td></tr><tr><td>PPENS</td><td>5,340</td><td>5,872</td><td>11,212</td><td>49.86</td><td>0.01308</td></tr><tr><td>DEB</td><td>3,430</td><td>4,611</td><td>8,041</td><td>69.37</td><td>0.01008</td></tr><tr><td colspan="6">Electronics (n=100)</td></tr><tr><td>SA</td><td>972</td><td>1,078</td><td>2,050</td><td>14.83</td><td>0.00240</td></tr><tr><td>RC</td><td>3,618</td><td>4,136</td><td>7,754</td><td>72.07</td><td>0.00918</td></tr><tr><td>PR</td><td>1,688</td><td>1,624</td><td>3,312</td><td>29.51</td><td>0.00367</td></tr><tr><td>PPR</td><td>2,754</td><td>2,212</td><td>4,966</td><td>24.82</td><td>0.00511</td></tr><tr><td>PENS</td><td>5,532</td><td>5,199</td><td>10,731</td><td>41.94</td><td>0.01178</td></tr><tr><td>PPENS</td><td>6,594</td><td>5,597</td><td>12,191</td><td>47.89</td><td>0.01284</td></tr><tr><td>DEB</td><td>4,242</td><td>4,575</td><td>8,817</td><td>69.29</td><td>0.01021</td></tr><tr><td colspan="6">Toys and Games (n=100)</td></tr><tr><td>SA</td><td>704</td><td>927</td><td>1,632</td><td>13.18</td><td>0.00203</td></tr><tr><td>RC</td><td>2,675</td><td>3,780</td><td>6,455</td><td>51.32</td><td>0.00823</td></tr><tr><td>PR</td><td>1,232</td><td>1,391</td><td>2,623</td><td>19.08</td><td>0.00309</td></tr><tr><td>PPR</td><td>2,022</td><td>1,974</td><td>3,996</td><td>21.42</td><td>0.00445</td></tr><tr><td>PENS</td><td>4,162</td><td>4,710</td><td>8,871</td><td>37.64</td><td>0.01046</td></tr><tr><td>PPENS</td><td>5,009</td><td>5,163</td><td>10,173</td><td>40.17</td><td>0.01158</td></tr><tr><td>DEB</td><td>3,134</td><td>3,976</td><td>7,109</td><td>56.13</td><td>0.00873</td></tr></table>

Table 12. Per-category cost and eficiency on the high-diversity cohort (gpt-5-mini, <sup>??</sup>=<sup>100</sup> per category). Columns and conventions are as in Table 11; lower is beter, best and second-best per column in bold and underline.

<table><tr><td>Method</td><td>In tok/q</td><td>Out tok/q</td><td>Total tok/q</td><td>Lat. par (s)</td><td>Cost/q (USD)</td></tr><tr><td colspan="6">Amazon Fashion (n=100)</td></tr><tr><td>SA</td><td>572</td><td>944</td><td>1,516</td><td>11.20</td><td>0.00203</td></tr><tr><td>RC</td><td>2,255</td><td>3,520</td><td>5,775</td><td>39.68</td><td>0.00760</td></tr><tr><td>PR</td><td>990</td><td>1,455</td><td>2,445</td><td>18.39</td><td>0.00316</td></tr><tr><td>PPR</td><td>1,646</td><td>2,107</td><td>3,753</td><td>22.27</td><td>0.00462</td></tr><tr><td>PENS</td><td>3,468</td><td>5,055</td><td>8,523</td><td>37.09</td><td>0.01098</td></tr><tr><td>PPENS</td><td>4,232</td><td>5,264</td><td>9,496</td><td>35.76</td><td>0.01159</td></tr><tr><td>DEB</td><td>2,606</td><td>4,009</td><td>6,615</td><td>48.44</td><td>0.00867</td></tr><tr><td colspan="6">Appliances (n=100)</td></tr><tr><td>SA</td><td>713</td><td>1,143</td><td>1,857</td><td>12.36</td><td>0.00246</td></tr><tr><td>RC</td><td>2,762</td><td>3,683</td><td>6,444</td><td>42.26</td><td>0.00806</td></tr><tr><td>PR</td><td>1,188</td><td>1,505</td><td>2,693</td><td>17.83</td><td>0.00331</td></tr><tr><td>PPR</td><td>1,978</td><td>2,253</td><td>4,231</td><td>21.95</td><td>0.00500</td></tr><tr><td>PENS</td><td>4,149</td><td>5,711</td><td>9,860</td><td>35.23</td><td>0.01246</td></tr><tr><td>PPENS</td><td>4,964</td><td>6,000</td><td>10,964</td><td>35.62</td><td>0.01324</td></tr><tr><td>DEB</td><td>3,170</td><td>4,614</td><td>7,784</td><td>51.00</td><td>0.01002</td></tr><tr><td colspan="6">Electronics (n=100)</td></tr><tr><td>SA</td><td>727</td><td>1,018</td><td>1,745</td><td>11.56</td><td>0.00222</td></tr><tr><td>RC</td><td>2,872</td><td>4,146</td><td>7,018</td><td>48.25</td><td>0.00901</td></tr><tr><td>PR</td><td>1,163</td><td>1,541</td><td>2,704</td><td>18.66</td><td>0.00337</td></tr><tr><td>PPR</td><td>1,975</td><td>2,130</td><td>4,105</td><td>20.75</td><td>0.00475</td></tr><tr><td>PENS</td><td>4,246</td><td>4,989</td><td>9,235</td><td>34.13</td><td>0.01104</td></tr><tr><td>PPENS</td><td>5,020</td><td>5,422</td><td>10,442</td><td>36.00</td><td>0.01210</td></tr><tr><td>DEB</td><td>3,227</td><td>4,444</td><td>7,670</td><td>50.31</td><td>0.00969</td></tr><tr><td colspan="6">Toys and Games (n=100)</td></tr><tr><td>SA</td><td>542</td><td>955</td><td>1,497</td><td>11.93</td><td>0.00205</td></tr><tr><td>RC</td><td>2,194</td><td>3,454</td><td>5,648</td><td>37.37</td><td>0.00746</td></tr><tr><td>PR</td><td>906</td><td>1,401</td><td>2,307</td><td>15.93</td><td>0.00303</td></tr><tr><td>PPR</td><td>1,536</td><td>2,023</td><td>3,560</td><td>18.43</td><td>0.00443</td></tr><tr><td>PENS</td><td>3,339</td><td>4,725</td><td>8,064</td><td>30.11</td><td>0.01028</td></tr><tr><td>PPENS</td><td>4,037</td><td>5,062</td><td>9,099</td><td>33.39</td><td>0.01113</td></tr><tr><td>DEB</td><td>2,485</td><td>3,965</td><td>6,450</td><td>48.70</td><td>0.00855</td></tr></table>

## VRAgent-R1: Boosting Video Recommendation with MLLM-based Agents via Reinforcement Learning

# VRAgent-R1: Boosting Video Recommendation with MLLM-based Agents via Reinforcement Learning

Chen Siran<sup>1,2</sup>, Chen Boyu<sup>1,2</sup>, Yu Chenyun<sup>3</sup>, Luo Yuxiao<sup>1</sup>, Yi Ouyang<sup>2</sup>, Cheng Lei<sup>2</sup>, Zhuo Chengxiang<sup>2</sup>, Li Zang<sup>2</sup>, Wang Yali<sup>1,4</sup>

<sup>1</sup>SIAT@MMLab, <sup>2</sup> Platform and Content Group, Tencent, <sup>3</sup>Sun Yat-sen University, <sup>4</sup>Shanghai AILab,

## Abstract

Owing to powerful natural language processing and generative capabilities, large language model (LLM) agents have emerged as a promising solution for enhancing recommendation systems via user simulation. However, in the realm of video recommendation, existing studies predominantly resort to prompt-based simulation using frozen LLMs and encounter the intricate challenge of multimodal content understanding. This frequently results in suboptimal item modeling and user preference learning, thereby ultimately constraining recommendation performance. To address these challenges, we introduce VRAgent-R1, a novel agent-based paradigm that incorporates human-like intelligence in user simulation. Specifically, VRAgent-R1 comprises two distinct agents: the Item Perception (IP) Agent and the User Simulation (US) Agent, designed for interactive user-item modeling. Firstly, the IP Agent emulates human-like progressive thinking based on MLLMs, effectively capturing hidden recommendation semantics in videos. With a more comprehensive multimodal content understanding provided by the IP Agent, the video recommendation system is equipped to provide higher-quality candidate items. Subsequently, the US Agent refines the recommended video sets based on in-depth chain-of-thought (CoT) reasoning and achieves better alignment with real user preferences through reinforcement learning. Experimental results on a large-scale video recommendation benchmark have demonstrated the effectiveness of our proposed VRAgent-R1 method, e.g., the IP Agent achieves a 6.0% improvement in NDCG@10 on the MicroLens-100k dataset, while the US Agent shows approximately 45.0% higher accuracy in user decision simulation compared to state-of-the-art baselines.

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

## 2 Related Work

LLMs/MLLMs for Multi-Modal Recommendation. LLMs and MLLMs have performed a profound impact on their integration into current recommendation systems. Existing methods utilizing LLMs can be broadly categorized into implicit and explicit applications. The implicit methods [9, 10, 11, 12, 13, 6, 28, 29] directly utilize the pre-trained structure or parameters of large models to convert user and item information into embeddings. For example, LEARN [12] integrates key attributes such as the title, description, and brand of each item into a predefined prompt, and then uses the last layer feature of the LLM as the item embedding. NoteLLM-2 [6] employs an MLLM with end-to-end fine tuning to fuse multimodal information as the item embedding. Explicit methods [14, 17, 30, 15, 16] involve using the reasoning ability of MLLMs to expand item information and analyze user profiles or intentions, ultimately generating textual summarization to aid recommendations. For example, MLLM-MSR [15] uses MLLMs to generate detailed image captions and summarize user preferences for further recommendations. However, research on video recommendation with minute-level visual content is relatively scarce compared to text-based and image-based recommendations, and we are pioneers in using MLLMs for video recommendation.

LLM-based User Simulator. Considering the powerful semantic understanding and reasoning abilities, many works utilize LLM to assist user inference simulations [31, 17, 32, 18, 14]. For instance, iEvaLM [31] explores two types of interaction within a conversational recommendation benchmark: attribute-based question answering and free-form chit-chat using ChatGPT [33]. To simulate user search behavior, USimAgent [17] prompts an LLM agent to construct complete search sessions, including querying, clicking, and stopping behaviors, according to specific search tasks. Agent4Rec [18] initializes LLMs as agents with unique user profiles that encompass tastes and social traits to simulate more realistic user behaviors, thereby reflecting user preferences and social characteristics. Additionally, LLM\_Simulator [14] simulates user preferences by matching the positive and negative attributes of items with user preferences generated by the LLM to determine whether a user would like an item. However, previous LLM-based user simulation approaches have relied on frozen LLMs, and using them solely through prompting would risk discrepancies with real user behavior and potential hallucinations [18].

Training LLMs/MLLMs with RL. With the success of DeepSeek-R1 [34], reinforcement learning (RL) has demonstrated its remarkable ability to enhance the logical reasoning capabilities of LLMs with high data efficiency. There have been explorations to improve LLMs’ performance in reasoning tasks, such as solving mathematical puzzles [26, 35, 36] and coding [37, 38]. Furthermore, Visual-RFT [39] pioneers the enhancement of reasoning and visual perception in Large Vision Language Models with limited data. In the recommendation scenario, compared with SFT, the RL method requires less data to learn a reasoning strategy with good generalization, making it suitable for cold start scenarios and user simulation. To our knowledge, we are among the first to apply RFT of LLMs for user simulation and video recommendation.

## 3 Method

As shown in Fig. 2, our VRAgent-R1 framework mainly consists of two components: the Item Perception Agent (IP Agent) for video modeling and the User Simulation Agent (US Agent) for user modeling. In the following sections, we will detail how each agent works and how they collaborate to achieve better user simulation.

## 3.1 Item Perception Agent (IP Agent)

Existing video representation learning methods typically process visual and textual information separately by inputting them into distinct encoders for later feature fusion. However, due to the heterogeneity and the imbalance in information volumes between the two modalities, it is prone to modality competition, which in turn leads to a suboptimal semantic space for item representations [24]. To accurately localize and extract the high-level semantics of video for more precise recommendations, we propose a progressive approach that utilizes MLLMs to gradually mine video information through key frame retrieval, collaborative multimodal perception, and recommendation-relevant analysis, as illustrated in Fig. 3.

![](images/a7a61a5c5ae70e9cbc51c643afc5455a47e88fd160aeffbe1e6c0c31addaec7e.jpg)  
<sup>(c)</sup> <sup>Ours</sup> <sup>MLLM-based</sup> <sup>Video</sup> <sup>Item</sup> <sup>Perception</sup> <sup>Agent</sup>Figure 3: Video understanding by the IP Agent. We simulate the human video comprehension process through a progressive approach involving retrieval, collaborative perception, and analysis, so as to obtain a summary of the key video information that is applicable for recommendation.

Key Frame Retrieval (KFR). Given that videos contain a wealth of visual information, directly utilizing all video frames would introduce substantial redundant information and result in low computational efficiency. To identify the most crucial information in the visual representation while ensuring the algorithm’s efficiency, we uniformly sample 10 frames from the video. Subsequently, we employ CLIP [40] to compute the visual-text similarity scores between these sampled frames and the video title. The frames with the top 3 highest CLIP scores are then identified as the key visual information for the video’s representation.

Collaborative Multimodal Perception (CMP). After obtaining the retrieved frames, the next step is to identify the specific events and high-level semantics conveyed in the video. Our approach stands out from previous methods by fully leveraging the multi-modal understanding capabilities of the MLLM. Specifically, since some titles do not directly reflect the video’s topics, we input both the retrieved frames and titles into the MLLM and prompt it to understand the semantic context implied by the titles. During this process, MLLM can provide relevant explanations of the title and offer supplementary information. For instance, in Fig. 3, the term "situation" might pertain to international relations, while “change” could imply shifts in national policy. It is important to note that neither modality’s embedding could independently capture such nuanced semantics. Thus, the MLLM can now clearly comprehend the video information, including the main characters, general events, video genre, and the sentiment expressed in the video.

Recommendation Relevant Analysis (RRA). The captions initially generated by MLLM may not be well-suited for the specific recommendation scenario, as they may contain excessive redundant explanations or even hallucinations. To address this issue, we prompt the model to analyze the detailed video content jointly with the characteristics of scenario, as well as focusing on the key information that users are most likely to find interesting. The model then reformulates the video content into a concise and precise caption limited to approximately 35 words, which is close to the average length of the original titles. This process helps filter out unimportant details, resulting in a unified and comprehensive video caption. For more details, please refer to Appendix A.1. Note that the reformulated video caption not only can be used to enhance the representation learning for items, but also assist the process of user behavior simulation.

## 3.2 User Simulation Agent (US Agent)

After modeling the video items, we then consider simulating human behavior to refine the recommendation results. Although numerous LLM-based user agents are available [14, 18, 25, 19], most of them simply prompt frozen LLMs to generate fixed user profiles and make predictions without incorporating downstream feedback. Therefore, LLMs can not be optimized and the simulation outcomes may be unrealistic and prone to hallucinations. Moreover, simple supervised fine-tuning only enables models to memorize answers. Due to the lack of in-depth analysis of user behavior, this approach yields limited accuracy and lacks interpretability. To better align the model with the user decision-making process, we innovatively employ reinforcement learning to fine-tune the LLM within a simulated recommendation environment.

Environment and User Modeling. First, we identify the modeling of the recommendation environment and personalized user as shown in Fig .2. The environment aims to simulate a realistic recommendation scenario by generating candidate videos for the user, while the US Agent simulates the user to perform specific tasks. More specifically, for a user with N behaviors (including watched videos and corresponding comments), the first $N { - } 1$ behaviors are used for user profile modeling, and the N-th behavior is regarded as the prediction target. We use SASRec [21] to recommend 10 video items based on the user’s historical behaviors, simulating a rough recall process. Then m items are randomly selected as negative samples, and the real N-th item of user behavior is regarded as the positive one. These m+1 items collectively form the candidate video list for future tasks, which we will discuss in the following section. However, processing multiple video and text sequences simultaneously is challenging for the MLLM. To address this issue, the IP Agent converts the relevant multimodal videos into a textual format, enabling the US Agent to process the long text sequence instead. For a given task in the RFT process, we prompt the US Agent to first thoroughly analyze the user behavior to formulate a unique user status s (e.g., preferences and emotions) through CoT reasoning. The US Agent then analyzes the candidate videos and performs the appropriate action. Compared to previous methods, the user profile modeling here is dynamically updated based on task rewards, which allows for a learnable and more accurate simulation.

Task and Reward. To align the US Agent with real user preferences, we design two specific tasks for RFT, i.e., User Preference Judgment and Next Video Selection. In the first task, following settings of previous methods [15, 18, 14], the agent is given an item from the candidate list and then prompted to judge whether the user would like the recommended video. The action space A consists of $" \mathrm { Y e s } "$ and "No", corresponding to positive items and negative items, respectively. The Reward $R _ { 1 }$ for this task comprises two parts: the format reward $R _ { \mathrm { f o r m a t } }$ and the judgment reward $R _ { \mathrm { j u d } }$

$$
R _ {1} = R _ {\text { format }} + R _ {\text { jud }}.\tag{1}
$$

The format reward ensures the model adheres to the required response format, i.e., <think>the CoT thinking process</think>, <answer>the final answer</answer>. If the model’s answer is correctly formatted, it receives a score of 1; otherwise, scores are assigned according to the format specification presented in Appendix A.2. Additionally, we use a post-processing function f to parse the answer within the <answer> tag into a legal action, and check if it matches the ground truth. Here, $R _ { j u d }$ will be 1 for a correct simulation and -1 for a wrong situation.

In the second task, the agent first reviews all candidate items and selects the video that the user is most likely to watch next via prompt engineering. The action space $\mathcal { A }$ consists of choosing one item from the m+1 candidate videos. The reward $R _ { 2 }$ for this task includes the format reward $R _ { \mathrm { f o r m a t } }$ and the selection reward $R _ { \mathrm { s e l } }$

$$
R _ {2} = R _ {\text { format }} + R _ {\text { sel }}.\tag{2}
$$

Given the larger action space of $R _ { 2 }$ compared to $R _ { 1 }$ , this task is more complex, and we assign a score of 2 for correctly selecting the positive video to provide a higher reward.

GRPO Training. We employ Group Relative Policy Optimization (GRPO) [26] framework to train the agent, which compares groups of candidate responses directly, without requiring a critic model to evaluate policy performance. Given a problem q for the model $\pi _ { \theta } .$ , it samples to generate a group of distinct answers $o _ { i }$ , where $i = 1 , \bar { 2 , } . . . , G$ and $G$ is the sampled number in the group. Each answer involves different CoT reasoning for the user status and final answer, and we compute the corresponding reward $r _ { i } .$ . By comparing the relative advantage of the i-th answer ${ \hat { A } } _ { i }$

$$
\hat {A} _ {i} = \frac {r _ {i} - \operatorname{mean} (\mathbf {r})}{\operatorname{std} (\mathbf {r})}\tag{3}
$$

$\mathbf { r } = \{ r _ { 1 } , r _ { 2 } , . . . , r _ { G } \}$ , GRPO encourages the model to select the answer with higher reward within the group (more details are in Appendix A.4). We initially train the agent with an easy judgment task, then introduce the selection task. Via such a progressive training manner, the agent learns from simpler to more complex tasks, and the CoT process is gradually optimized, which provides thoughtful and interpretable recommendations for the user behavior.

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

## 4.3 Optimizing RSs with VRAgent-R1

We conduct a preliminary experiment to assess whether VRAgent-R1’s simulation could enhance recommendation systems (RSs). Specifically, we randomly select 8,000 cold-start users and provide VRAgent-R1 with the top 10 items recommended by the original RSs. VRAgent-R1 simulates user decisions on which videos they might watch and which they would dislike. This simulated behaviors are then used to supplement the modeling of cold-start users and update the RSs. As shown in Tab. 4, incorporating feedback on user-liked videos improves recommendation performance. In contrast, simulated interactions with user-disliked videos have a negative impact. This outcome effectively demonstrates the feedback-driven recommendation augmentation process.

Ablation on the IP Agent. In this part, we ablate the progressive steps taken in our IP Agent. Specifically, "w/o KFR" denotes the absence of the key frame retrieval process, where we replace it with three randomly selected adjacent frames. "w/o CMP" indicates the removal of collaborative multimodal perception. In this scenario, the MLLM is employed to analyze visual frames and titles independently. "w/o RRA" signifies the exclusion of recommendation-relevant analysis, leading to the direct utilization of detailed long textual outputs for video comprehension. As shown in Tab. 5, both key frame extraction and collaborative multimodal interaction significantly enhance video modeling. The analysis process is also crucial, as excessive unimportant details can be noisy and degrade recommendation performance.

Ablation on the US Agent. We then conduct ablation studies to assess the impact of each component of VRAgent-R1 on simulation performance, as detailed in Tab. 6. First, we remove the CoT reasoning from the RFT process, and then the LLM directly predicts answers based on the user’s historical sequence, bypassing analysis of video contents and user status. This leads to a significant performance drop, underscoring the importance of CoT in reasoning tasks. Next, we evaluate the impact of user comments which aid in more accurate user modeling. Results show that the absence of them causes roughly 4% performance decline. Finally, we ablate the IP Agent, which is responsible for multimodal understanding. We can observe that the IP Agent boosts performance by approximately 6% over the baseline relying on original textual information.

## 5 Conclusion

In this paper, we propose a novel VRAgent-R1 framework for user simulation in video recommendation. It first utilizes an MLLM to collaboratively understand the retrieved multimodal content with pre-trained world knowledge, then analyzes the history sequence to establish user status and make final decision through RFT. By exploring different strategies and using real user decisions as verifiable rewards under different tasks, our VRAgent-R1 method achieves significant improvements in user behavior simulation for video recommendation. It outperforms SFT with minimal data and shows strong generalization. As a pioneering work, this study demonstrates the potential of applying RFT to LLMs in recommendation systems.

Limitations and Future Directions. Although the dataset used in this paper focuses on video recommendations, our VRAgent-R1 paradigm can be easily extended to various domains such as games, news, and e-commerce. Currently, the user action space in our experiments is relatively limited due to the dataset properties. In future work, we plan to explore adding more user behaviors, such as clicks and retention, to achieve more realistic user-system interactions. Moreover, verifying whether better user simulation feedback can further optimize existing recommendation systems is also a crucial direction for future exploration.

## References

[1] Y. Huang, B. Cui, W. Zhang, J. Jiang, and Y. Xu, “Tencentrec: Real-time stream recommendation in practice,” in Proceedings of the 2015 ACM SIGMOD international conference on management of data, 2015, pp. 227–238.

[2] L. Zheng, C.-T. Lu, F. Jiang, J. Zhang, and P. S. Yu, “Spectral collaborative filtering,” in Proceedings of the 12th ACM conference on recommender systems, 2018, pp. 311–319.

[3] R. Ying, R. He, K. Chen, P. Eksombatchai, W. L. Hamilton, and J. Leskovec, “Graph convolutional neural networks for web-scale recommender systems,” in Proceedings of the 24th ACM SIGKDD international conference on knowledge discovery & data mining, 2018, pp. 974–983.

[4] J. Yang, X. Yi, D. Zhiyuan Cheng, L. Hong, Y. Li, S. Xiaoming Wang, T. Xu, and E. H. Chi, “Mixed negative sampling for learning two-tower neural networks in recommendations,” in Companion proceedings of the web conference 2020, 2020, pp. 441–447.

[5] F. Yuan, X. He, A. Karatzoglou, and L. Zhang, “Parameter-efficient transfer from sequential behaviors for user modeling and recommendation,” in Proceedings of the 43rd International ACM SIGIR conference on research and development in Information Retrieval, 2020, pp. 1469–1478.

[6] C. Zhang, H. Zhang, S. Wu, D. Wu, T. Xu, X. Zhao, Y. Gao, Y. Hu, and E. Chen, “Notellm-2: Multimodal large representation models for recommendation,” arXiv preprint arXiv:2405.16789, 2024.

[7] J. Chen, L. Chi, B. Peng, and Z. Yuan, “Hllm: Enhancing sequential recommendations via hierarchical large language models for item and user modeling,” arXiv preprint arXiv:2409.12740, 2024.

[8] X. Luo, J. Cao, T. Sun, J. Yu, R. Huang, W. Yuan, H. Lin, Y. Zheng, S. Wang, Q. Hu et al., “Qarm: Quantitative alignment multi-modal recommendation at kuaishou,” arXiv preprint arXiv:2411.11739, 2024.

[9] F. Sun, J. Liu, J. Wu, C. Pei, X. Lin, W. Ou, and P. Jiang, “Bert4rec: Sequential recommendation with bidirectional encoder representations from transformer,” in Proceedings of the 28th ACM international conference on information and knowledge management, 2019, pp. 1441–1450.

[10] X. Ren, W. Wei, L. Xia, L. Su, S. Cheng, J. Wang, D. Yin, and C. Huang, “Representation learning with large language models for recommendation,” in Proceedings of the ACM Web Conference 2024, 2024, pp. 3464–3475.

[11] D.-H. Lee, A. Kraft, L. Jin, N. Mehta, T. Xu, L. Hong, E. H. Chi, and X. Yi, “Star: A simple training-free approach for recommendations using large language models,” arXiv preprint arXiv:2410.16458, 2024.

[12] J. Jia, Y. Wang, Y. Li, H. Chen, X. Bai, Z. Liu, J. Liang, Q. Chen, H. Li, P. Jiang et al., “Learn: Knowledge adaptation from large language model to recommendation for practical industrial application,” in Proceedings of the AAAI Conference on Artificial Intelligence, vol. 39, no. 11, 2025, pp. 11 861–11 869.

[13] C. Song, C. Shen, H. Gu, Y. Wu, L. Yi, J. Wen, and C. Chen, “Precise: Pre-training sequential recommenders with collaborative and semantic information,” arXiv preprint arXiv:2412.06308, 2024.

[14] Z. Zhang, S. Liu, Z. Liu, R. Zhong, Q. Cai, X. Zhao, C. Zhang, Q. Liu, and P. Jiang, “Llm-powered user simulator for recommender system,” in Proceedings of the AAAI Conference on Artificial Intelligence, vol. 39, no. 12, 2025, pp. 13 339–13 347.

[15] Y. Ye, Z. Zheng, Y. Shen, T. Wang, H. Zhang, P. Zhu, R. Yu, K. Zhang, and H. Xiong, “Harnessing multimodal large language models for multimodal sequential recommendation,” in Proceedings of the AAAI Conference on Artificial Intelligence, vol. 39, no. 12, 2025, pp. 13 069–13 077.

[16] K. Bao, J. Zhang, Y. Zhang, W. Wang, F. Feng, and X. He, “Tallrec: An effective and efficient tuning frame work to align large language model with recommendation,” in Proceedings of the 17th ACM Conference on Recommender Systems, 2023, pp. 1007–1014.

[17] E. Zhang, X. Wang, P. Gong, Y. Lin, and J. Mao, “Usimagent: Large language models for simulating search users,” in Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval, 2024, pp. 2687–2692.

[18] A. Zhang, Y. Chen, L. Sheng, X. Wang, and T.-S. Chua, “On generative agents in recommendation,” in Proceedings of the 47th international ACM SIGIR conference on research and development in Information Retrieval, 2024, pp. 1807–1817.

[19] W. Xiang, H. Zhu, S. Lou, X. Chen, Z. Pan, Y. Jin, S. Chen, and L. Sun, “Simuser: Generating usability feedback by simulating various users interacting with mobile applications,” in Proceedings of the 2024 CHI Conference on Human Factors in Computing Systems, 2024, pp. 1–17.

[20] R. He, C. Fang, Z. Wang, and J. McAuley, “Vista: A visually, socially, and temporally-aware model for artistic recommendation,” in Proceedings of the 10th ACM conference on recommender systems, 2016, pp. 309–316.

[21] Y. Ni, Y. Cheng, X. Liu, J. Fu, Y. Li, X. He, Y. Zhang, and F. Yuan, “A content-driven micro-video recommendation dataset at scale,” arXiv preprint arXiv:2309.15379, 2023.

[22] Y. Shang, C. Gao, J. Chen, D. Jin, H. Ma, and Y. Li, “Enhancing adversarial robustness of multi-modal recommendation via modality balancing,” in Proceedings of the 31st ACM International Conference on Multimedia, 2023, pp. 6274–6282.

[23] Q. Liu, J. Hu, Y. Xiao, X. Zhao, J. Gao, W. Wang, Q. Li, and J. Tang, “Multimodal recommender systems: A survey,” ACM Computing Surveys, vol. 57, no. 2, pp. 1–17, 2024.

[24] H. Zhou, X. Zhou, Z. Zeng, L. Zhang, and Z. Shen, “A comprehensive survey on multimodal recommender systems: Taxonomy, evaluation, and future directions,” arXiv preprint arXiv:2302.04473, 2023.

[25] L. Wang, J. Zhang, H. Yang, Z.-Y. Chen, J. Tang, Z. Zhang, X. Chen, Y. Lin, H. Sun, R. Song et al., “User behavior simulation with large language model-based agents,” ACM Transactions on Information Systems, vol. 43, no. 2, pp. 1–37, 2025.

[26] Z. Shao, P. Wang, Q. Zhu, R. Xu, J. Song, X. Bi, H. Zhang, M. Zhang, Y. Li, Y. Wu et al., “Deepseekmath: Pushing the limits of mathematical reasoning in open language models,” arXiv preprint arXiv:2402.03300, 2024.

[27] A. Hurst, A. Lerer, A. P. Goucher, A. Perelman, A. Ramesh, A. Clark, A. Ostrow, A. Welihinda, A. Hayes, A. Radford et al., “Gpt-4o system card,” arXiv preprint arXiv:2410.21276, 2024.

[28] B. Chen, S. Chen, K. Li, Q. Xu, Y. Qiao, and Y. Wang, “Super encoding network: Recursive association of multi-modal encoders for video understanding,” arXiv preprint arXiv:2506.07576, 2025.

[29] ——, “Percept, chat, and then adapt: Multimodal knowledge transfer of foundation models for open-world video recognition,” arXiv preprint arXiv:2402.18951, 2024.

[30] Y. Hou, J. Zhang, Z. Lin, H. Lu, R. Xie, J. McAuley, and W. X. Zhao, “Large language models are zero-shot rankers for recommender systems,” in European Conference on Information Retrieval. Springer, 2024, pp. 364–381.

[31] X. Wang, X. Tang, W. X. Zhao, J. Wang, and J.-R. Wen, “Rethinking the evaluation for conversational recommendation in the era of large language models,” arXiv preprint arXiv:2305.13112, 2023.

[32] N. Corecco, G. Piatti, L. A. Lanzendörfer, F. X. Fan, and R. Wattenhofer, “Suber: An rl environment with simulated human behavior for recommender systems,” arXiv preprint arXiv:2406.01631, 2024.

[33] J. Achiam, S. Adler, S. Agarwal, L. Ahmad, I. Akkaya, F. L. Aleman, D. Almeida, J. Altenschmidt, S. Altman, S. Anadkat et al., “Gpt-4 technical report,” arXiv preprint arXiv:2303.08774, 2023.

[34] D. Guo, D. Yang, H. Zhang, J. Song, R. Zhang, R. Xu, Q. Zhu, S. Ma, P. Wang, X. Bi et al., “Deepseek-r1: Incentivizing reasoning capability in llms via reinforcement learning,” arXiv preprint arXiv:2501.12948, 2025.

[35] A. Yang, B. Zhang, B. Hui, B. Gao, B. Yu, C. Li, D. Liu, J. Tu, J. Zhou, J. Lin et al., “Qwen2. 5-math tech nical report: Toward mathematical expert model via self-improvement,” arXiv preprint arXiv:2409.12122, 2024.

[36] H. Ying, S. Zhang, L. Li, Z. Zhou, Y. Shao, Z. Fei, Y. Ma, J. Hong, K. Liu, Z. Wang et al., “Internlm-math: Open math large language models toward verifiable reasoning,” arXiv preprint arXiv:2402.06332, 2024.

[37] Y. Zhang, S. Wu, Y. Yang, J. Shu, J. Xiao, C. Kong, and J. Sang, “o1-coder: an o1 replication for coding,” arXiv preprint arXiv:2412.00154, 2024.

[38] K. Zhang, G. Li, Y. Dong, J. Xu, J. Zhang, J. Su, Y. Liu, and Z. Jin, “Codedpo: Aligning code models with self generated and verified source code,” arXiv preprint arXiv:2410.05605, 2024.

[39] Z. Liu, Z. Sun, Y. Zang, X. Dong, Y. Cao, H. Duan, D. Lin, and J. Wang, “Visual-rft: Visual reinforcement fine-tuning,” arXiv preprint arXiv:2503.01785, 2025.

[40] A. Radford, J. W. Kim, C. Hallacy, A. Ramesh, G. Goh, S. Agarwal, G. Sastry, A. Askell, P. Mishkin, J. Clark et al., “Learning transferable visual models from natural language supervision,” in International conference on machine learning. PmLR, 2021, pp. 8748–8763.

[41] A. Yang, B. Yang, B. Zhang, B. Hui, B. Zheng, B. Yu, C. Li, D. Liu, F. Huang, H. Wei et al., “Qwen2. 5 technical report,” arXiv preprint arXiv:2412.15115, 2024.

[42] P.-S. Huang, X. He, J. Gao, L. Deng, A. Acero, and L. Heck, “Learning deep structured semantic models for web search using clickthrough data,” in Proceedings of the 22nd ACM international conference on Information & Knowledge Management, 2013, pp. 2333–2338.

[43] X. He, K. Deng, X. Wang, Y. Li, Y. Zhang, and M. Wang, “Lightgcn: Simplifying and powering graph convolution network for recommendation,” in Proceedings of the 43rd International ACM SIGIR conference on research and development in Information Retrieval, 2020, pp. 639–648.

[44] H. Guo, R. Tang, Y. Ye, Z. Li, and X. He, “Deepfm: a factorization-machine based neural network for ctr prediction,” arXiv preprint arXiv:1703.04247, 2017.

[45] F. Yuan, A. Karatzoglou, I. Arapakis, J. M. Jose, and X. He, “A simple convolutional generative network for next item recommendation,” in Proceedings of the twelfth ACM international conference on web search and data mining, 2019, pp. 582–590.

[46] B. Hidasi, A. Karatzoglou, L. Baltrunas, and D. Tikk, “Session-based recommendations with recurrent neural networks,” arXiv preprint arXiv:1511.06939, 2015.

[47] W.-C. Kang and J. McAuley, “Self-attentive sequential recommendation,” in 2018 IEEE international conference on data mining (ICDM). IEEE, 2018, pp. 197–206.

[48] F. M. Harper and J. A. Konstan, “The movielens datasets: History and context,” Acm transactions on interactive intelligent systems (tiis), vol. 5, no. 4, pp. 1–19, 2015.

[49] J.-C. Shi, Y. Yu, Q. Da, S.-Y. Chen, and A.-X. Zeng, “Virtual-taobao: Virtualizing real-world online retail environment for reinforcement learning,” in Proceedings of the AAAI Conference on Artificial Intelligence, vol. 33, no. 01, 2019, pp. 4902–4909.

[50] X. Chen, S. Li, H. Li, S. Jiang, Y. Qi, and L. Song, “Generative adversarial user model for reinforcement learning based recommendation system,” in International conference on machine learning. PMLR, 2019, pp. 1052–1061.

[51] K. Zhao, S. Liu, Q. Cai, X. Zhao, Z. Liu, D. Zheng, P. Jiang, and K. Gai, “Kuaisim: A comprehensive simulator for recommender systems,” Advances in Neural Information Processing Systems, vol. 36, pp. 44 880–44 897, 2023.

[52] J. Jeong, Y. Chow, G. Tennenholtz, C.-W. Hsu, A. Tulepbergenov, M. Ghavamzadeh, and C. Boutilier, “Factual and personalized recommendations using language models and reinforcement learning,” arXiv preprint arXiv:2310.06176, 2023.

[53] C. Sun, Y. Liang, Y. Yang, S. Xu, T. Yang, and Y. Tong, “Rlrf4rec: Reinforcement learning from recsys feedback for enhanced recommendation reranking,” arXiv preprint arXiv:2410.05939, 2024.

[54] J. Lin, T. Wang, and K. Qian, “Rec-r1: Bridging generative large language models and user-centric recommendation systems via reinforcement learning,” arXiv preprint arXiv:2503.24289, 2025.

[55] R. S. Sutton, A. G. Barto et al., Reinforcement learning: An introduction. MIT press Cambridge, 1998, vol. 1, no. 1.

[56] A. Agarwal, N. Jiang, S. M. Kakade, and W. Sun, “Reinforcement learning: Theory and algorithms,” CS Dept., UW Seattle, Seattle, WA, USA, Tech. Rep, vol. 32, p. 96, 2019.

[57] J. Schulman, F. Wolski, P. Dhariwal, A. Radford, and O. Klimov, “Proximal policy optimization algorithms,” arXiv preprint arXiv:1707.06347, 2017.

## A Technical Appendices and Supplementary Material

Technical appendices with additional results, figures, graphs and proofs may be submitted with the paper submission before the full submission deadline (see above), or as a separate PDF in the ZIP file below before the supplementary material deadline. There is no page limit for the technical appendices.

## A.1 Prompt Templates for the Agents

In this section, we present the comprehensive set of prompt templates utilized in the experiments across various stages, as shown in Tab. 7. These prompts are meticulously designed to guide the Agent in effectively performing its tasks, ensuring seamless interactions and accurate responses.

<table><tr><td>Prompt</td><td>Content</td></tr><tr><td>Prompt to decide which parts of the video to focus on</td><td>You are a helpful assistant to help to understand a video. These are key {frames} from a video, and the title of the video is: {title}. Pay special attention to content related to the title.</td></tr><tr><td>Prompt for collaborative perception</td><td>Based on the textual and visual contents, identify what visual content aligns with or extends beyond the title&#x27;s description, note any discrepancies or additional context provided by the visuals. Now combined with your knowledge and understanding, give the key information about the video, including: main characters, core event and emotional appeal.</td></tr><tr><td>Prompt to generate summarization for recommendation</td><td>If you want to recommend the video, create a concise summary within 35 words on what the viewer would be interested in, following this format: [Core Content Description] + [Refined Tags]. The content should be clear and elegant, and tags should be brief and accurate to reflect the video topic. Here is a good example: &quot;the girl just drove the wrong way, but did not expect to encounter terrible things # thriller movie # movie commentary&quot;</td></tr><tr><td>Prompt for User Simulation</td><td>You are a helpful assistant. The assistant first thinks about the user&#x27;s video watching history and the comments, analyzes their current status, such as preferences and purpose, and predicts: which video they are most likely to watch next from the given candidates / if they like the next video. The reasoning process and answer are enclosed withinandtags, respectively, i.e.,reasoning process hereanswer here. After thinking, when you finally reach a conclusion, give the user status and the answer you predict withintags. i.e.,(1) User_status:....(2) Next_video:...User&#x27;s viewing history: {history_str}Candidate videos for the next watch: {candidates_str}</td></tr></table>

Table 7: The prompt templates used in our VRAgent-R1.

## A.2 Reward Score Computation

In this section, we give the concrete computation for the three reward scores as follows:

$$
R _ {f o r m a t} = \left\{ \begin{array}{l l} 1, & \text { if   the   answer   follows   the   standard   format } \\ 0. 5, & \text { if   the   order   of   <  think > , <  answer > tags   is   wrong } \\ 0, & \text { if   missing   <  think > or   <  answer > tags } \\ - 1, & \text { if   the   answer   cannot   be   parsed   or   is   missing } \end{array} \right.\tag{4}
$$

$$
R _ {j u d} = \left\{ \begin{array}{l l} 1, & \text { if   the   agent   preference   matches   the   ground   truth } \\ - 1, & \text { if   the   agent   preference   mismatches   the   ground   truth } \\ - 1, & \text { if   the   agent   preference   cannot   be   parsed   or   is   missing } \end{array} \right.\tag{5}
$$

$$
R _ {s e l} = \left\{ \begin{array}{l l} 2, & \text { if   the   agent   selection   matches   the   ground   truth } \\ - 1. 5, & \text { if   the   agent   selection   mismatches   the   ground   truth } \\ - 2, & \text { if   the   agent   selection   cannot   be   parsed   or   is   missing } \end{array} \right.\tag{6}
$$

![](images/5732c3d1da2bc042669d0e507bb2f51e7d0e27adbee3c94c87c5277faa657970.jpg)  
Figure 5: Comparison with other user simulation for recommendation.

## A.3 Additional Experiment Discussion

Experiments on MovieLens. To verify the generality of our method in other domains, we also conduct user preference simulation tests on the widely used MovieLens-1M [48] dataset, which contains 1 million ratings from 6000 users on 4000 movies, and ratings above 3 are considered a positive like signal. Note that, though this dataset is related to movies, the understanding of movie contents mainly relies on text descriptions, while the visual information is not that important. Therefore, in this experiment, we only use the US Agent to do the evaluation, without considering the IP Agent for multimodal processing. We follow the setting of Agent4Rec [18], 1000 simulated users are randomly assigned 20 items, with varying ratios 1:m of positive and negative items. In our main paper, the reported results are all in a 1:1 ratio, here we also report the performance in 1:3 setting.

Table 8: Preference evaluation comparison on MovieLens with our US Agents.

<table><tr><td rowspan="2">Method</td><td colspan="4">1:1</td><td colspan="4">1:3</td></tr><tr><td>Acc</td><td>Recall</td><td>Pre</td><td>F1</td><td>Acc</td><td>Recall</td><td>Pre</td><td>F1</td></tr><tr><td>GPT-4o [27]</td><td>0.584</td><td>0.626</td><td>0.577</td><td>0.600</td><td>0.523</td><td>0.701</td><td>0.308</td><td>0.428</td></tr><tr><td>RecAgent [25]</td><td>0.581</td><td>0.639</td><td>0.604</td><td>0.621</td><td>0.508</td><td>0.740</td><td>0.399</td><td>0.518</td></tr><tr><td>Agent4Rec [18]</td><td>0.691</td><td>0.746</td><td>0.691</td><td>0.698</td><td>0.668</td><td>0.762</td><td>0.421</td><td>0.543</td></tr><tr><td>Ours</td><td>0.832</td><td>0.846</td><td>0.823</td><td>0.834</td><td>0.806</td><td>0.821</td><td>0.579</td><td>0.679</td></tr></table>

We can learn from the Tab. 8 that the user simulation results on MovieLens are better than those on MicroLens, indicating that the video recommendation task on MicroLens is more complex and challenging, where the multimodal information should be considered. And for textual dominated movie recommendation, our approach still has a great advantage compared with previous prompt-based simulation Agents [25, 18] like in Fig. 5, the prompt-based agents could not be optimized accordingly to recommendation, while our VRAgent-R1 learns to think deeply to simulate more realistic user behavior.

Statistical Significance For the video recommendation on MicroLens-100k, we follow the official implementation [21], with the IP Agent enhanced video understanding, we train the SASRec [47] with text information for three times, every time the test performance shows almost the same results, demonstrating the reproducibility of our experiments. For the user simulation, we use three random seeds to select 1000 cold-start users for evaluation, with 1-sigma error bars of 0.002, 0.005 for Acc and F1 in user performance judgment, 0.003 and 0.003 for $\mathrm { A c c } _ { m = 3 }$ and $\mathrm { A c c } _ { m = 4 }$ in next video selection. And the results consistently show that the performance of our method significantly outperforms previous agents (statistical tests using paired t-tests with 95% confidence intervals yield a p<0.002).

## A.4 Reinforcement Learning in Recommendation

Previous Works. In this section, we give a brief review of previous reinforcement learning methods for recommendation systems. Before the prevalence of LLMs, there were already many methods involving reinforcement learning (RL) for various objectives in recommendation. For example, previous methods use GANs [49, 50] or transformers [51] to simulate the user behavior, while they still involve the fitting of features essentially, relying on a large amount of data for reinforcement learning. They are limited to predefined tasks, unable to simulate users’ emotions and thinking processes, nor can they provide interpretive feedback. Recently, with the strong logical reasoning ability of LLMs, many researchers have begun to explore how to integrate RL and LLM to improve recommendation systems. $P ^ { 4 } \mathrm { L M }$ [52] applies RLHF to align a language model with factuality, personalization, and appeal to provide more interpretive explanations in movie recommendation scenario. RLRF4Rec [53] aims to enable the LLMs with the knowledge augmentation recommendation, and Rec-R1 [54] directly bridges the recommendation and LLMs, by optimizing the LLM with real time reward signals from the recommendation system. Different from above methods that generate better text outputs to help recommendation, we aim to simulate more realistic user behavior in multimodal situations, and our method has more application potential since it’s not limited to text-guided recommendation, it can not only evaluate the recommendation quality but also improve recommendation results through simulated feedback.

Basic RL Standards for LLM. Without loss of generality, we adhere to the standard notations presented in the classic works of reinforcement learning [55, 56]. More specifically, we use $s \in \mathcal S$ to denote the state space, $a \in { \mathcal { A } }$ to denote the action space, $r _ { k }$ to denote the reward function in step k, P to denote the transition dynamics, $\pi ( a | s )$ is the probability of performing action a in state s under policy π, and $\gamma \in [ 0 , 1 ]$ is the discount factor. The goal is to maximize the discounted cumulative returns for each trajectory as below,

$$
G _ {t} = \sum_ {k = t + 1} ^ {T} \gamma^ {k - t} r _ {k}\tag{7}
$$

where T is the maximum step numbers per episode. Instead of using the classic PPO [57] algorithm that requires a critic model to evaluate policy performance, we use the GRPO [26] to compare groups of candidate responses directly.

$$
\begin{array}{l} \mathcal {J} _ {\mathrm{GRPO}} (\theta) = \mathbb {E} _ {[ q \sim P (Q), \{o _ {i} \} _ {i = 1} ^ {G} \sim \pi_ {\theta_ {\mathrm{old}}} (O | q) ]} \\ \frac {1}{G} \sum_ {i = 1} ^ {G} \frac {1}{| o _ {i} |} \sum_ {t = 1} ^ {| o _ {i} |} \left\{\min \left[ \frac {\pi_ {\theta} ^ {i , t}}{\pi_ {\theta_ {\mathrm{old}}} ^ {i , t}} \hat {A} _ {i, t}, \operatorname{clip} \left(\frac {\pi_ {\theta} ^ {i , t}}{\pi_ {\theta_ {\mathrm{old}}} ^ {i , t}}, 1 - \epsilon , 1 + \epsilon\right) \hat {A} _ {i, t} \right] - \beta \mathbb {D} _ {\mathrm{KL}} [ \pi_ {\theta} \| \pi_ {\mathrm{ref}} ] \right\} \end{array}\tag{8}
$$

$$
\hat {A} _ {i, t} = \frac {r _ {i} - \operatorname{mean} (\mathbf {r})}{\operatorname{std} (\mathbf {r})}\tag{9}
$$

Given a problem q for the model $\pi \theta \cdot$ , it samples to generate a group of distinct answers $o _ { i } .$ , where $i = 1 , 2 , \dots , G$ G is the sampled number in the group. Each answer has a different length $\vert o _ { i } \vert . \~ \pi _ { \theta } ^ { i , t }$ is the policy probability of decoding the t-th token of the sampled answer. The KL term constrains that the distribution of $\pi \theta$ should not deviate too much from the original policy $\pi _ { \mathrm { r e f } }$ by penalty coefficient $\beta .$ Here, an optimized KL term is adopted, which has the characteristics of being unbiased and having a small variance. The clip strategy restricts the ratio between $\frac { \pi _ { \theta } } { \pi _ { \theta _ { o l d } } }$ , and by limiting the ratio within the interval $\varepsilon ,$ it prevents the new strategy from having large numerical updates. $\mathbf { r } = \{ r _ { 1 } , r _ { 2 } , \ldots , r _ { G } \}$ , and $\hat { A } _ { i , t }$ is the relative advantage of the i-th answer. Through the optimization of $\mathcal { G } _ { \mathrm { G R P O } } ( \theta )$ , GRPO encourages the model to choose the answer with higher reward within the group.

## A.5 Additional Visualization

In this section, we give more visualization results on the understanding of video items in Fig. 6. From the above contents, it is evident that models relying solely on original video titles or unimodal visual content (MLLM) struggle to capture the high-level semantic features of videos. Specifically, MLLM’s comprehension typically remains at the surface-level scene descriptions, failing to delve into the actual semantic relationships underlying the content. In contrast, our IP Agent framework achieves deep semantic fusion and comprehensive understanding of multimodal information by integrating the model’s a priori world knowledge. Through systematic evaluation by a human reviewer panel, the video semantic captions generated by this framework demonstrate significantly higher semantic accuracy and content congruence compared to the outputs of unimodal models, fully illustrating the effectiveness and necessity of multimodal knowledge fusion in video semantic understanding.

<table><tr><td rowspan="3"><img src="images/dc130142001541497c848b20599d7273a973fbb83cc00f67cb91902d7d587605.jpg"/></td><td>Title: Full Level Human Have you evolved today? Toenail darts</td></tr><tr><td>MLLM: A solid yellow background, in the center is Chinese characters said..., below the text, there is a small graphic of cat&#x27;s face... The overall style of the image is minimalistic and modern, with a focus on the text and graphic.</td></tr><tr><td>IP Agent: Humorous depiction of daily life evolution, featuring quirky characters and unexpected situations. #fully # quirky characters</td></tr><tr><td rowspan="3"><img src="images/fd0496581d1b7e8e05882f51bb188d743b3624f19b66d4e29ba77c8eb59e192a.jpg"/></td><td>Title: # I&#x27;m catching up on a good play in Fast hands</td></tr><tr><td>MLLM :a young individual with blonde hair and blue eyes, wearing a red mask with a distinctive X-shaped design over the eyes, the mask covers the eyes completely, leaving only ... There is text positioned at the bottom of the image...</td></tr><tr><td>IP Agent: Boy with superpowers faces challenges, risking everything. Intense action-packed drama. #superhero #action #drama</td></tr><tr><td rowspan="3"><img src="images/7d9f3c690bb71a5c3bcccf85a6bf536adc1cb588b9a059a0e524fb264f70319d.jpg"/></td><td>Title: You must not have seen the electric rock Harem legend</td></tr><tr><td>MLLM: a woman in the center, she has a fair complexion and is adorned with elaborate traditional Asian attire. Her hair is styled in an updo...The style of the image ...for historical films or television series.</td></tr><tr><td>IP Agent: Humorous parody of &quot;Zhen Huan Legend&quot; featuring electric rock music. Amusing twist on classic drama. #funny #parody #ZhenHuanLegend&quot;</td></tr></table>

Figure 6: Additional Visualization Results for Video Understanding.

## NeurIPS Paper Checklist

## 1. Claims

Question: Do the main claims made in the abstract and introduction accurately reflect the paper’s contributions and scope?

Answer: [Yes]

Justification: The main claims made in the abstract and introduction accurately reflect the paper’s contributions and scope of MLLM-based video recommendation.

Guidelines:

• The answer NA means that the abstract and introduction do not include the claims made in the paper.

• The abstract and/or introduction should clearly state the claims made, including the contributions made in the paper and important assumptions and limitations. A No or NA answer to this question will not be perceived well by the reviewers.

• The claims made should match theoretical and experimental results, and reflect how much the results can be expected to generalize to other settings.

• It is fine to include aspirational goals as motivation as long as it is clear that these goals are not attained by the paper.

## 2. Limitations

Question: Does the paper discuss the limitations of the work performed by the authors?

Answer: [Yes]

Justification: We discuss the limitations at the end of the main paper.

Guidelines:

• The answer NA means that the paper has no limitation while the answer No means that the paper has limitations, but those are not discussed in the paper.

• The authors are encouraged to create a separate "Limitations" section in their paper.

• The paper should point out any strong assumptions and how robust the results are to violations of these assumptions (e.g., independence assumptions, noiseless settings, model well-specification, asymptotic approximations only holding locally). The authors should reflect on how these assumptions might be violated in practice and what the implications would be.

• The authors should reflect on the scope of the claims made, e.g., if the approach was only tested on a few datasets or with a few runs. In general, empirical results often depend on implicit assumptions, which should be articulated.

• The authors should reflect on the factors that influence the performance of the approach. For example, a facial recognition algorithm may perform poorly when image resolution is low or images are taken in low lighting. Or a speech-to-text system might not be used reliably to provide closed captions for online lectures because it fails to handle technical jargon.

• The authors should discuss the computational efficiency of the proposed algorithms and how they scale with dataset size.

• If applicable, the authors should discuss possible limitations of their approach to address problems of privacy and fairness.

• While the authors might fear that complete honesty about limitations might be used by reviewers as grounds for rejection, a worse outcome might be that reviewers discover limitations that aren’t acknowledged in the paper. The authors should use their best judgment and recognize that individual actions in favor of transparency play an important role in developing norms that preserve the integrity of the community. Reviewers will be specifically instructed to not penalize honesty concerning limitations.

## 3. Theory assumptions and proofs

Question: For each theoretical result, does the paper provide the full set of assumptions and a complete (and correct) proof?

Answer: [NA]

Justification: We don’t consider theoretical proof or result in the paper.

Guidelines:

• The answer NA means that the paper does not include theoretical results.

• All the theorems, formulas, and proofs in the paper should be numbered and cross-referenced.

• All assumptions should be clearly stated or referenced in the statement of any theorems.

• The proofs can either appear in the main paper or the supplemental material, but if they appear in the supplemental material, the authors are encouraged to provide a short proof sketch to provide intuition.

• Inversely, any informal proof provided in the core of the paper should be complemented by formal proofs provided in appendix or supplemental material.

• Theorems and Lemmas that the proof relies upon should be properly referenced.

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

## 5. Open access to data and code

Question: Does the paper provide open access to the data and code, with sufficient instructions to faithfully reproduce the main experimental results, as described in supplemental material?

Answer: [No]

Justification: The data is open source to access and we will provide the code after the commercial approval.

Guidelines:

• The answer NA means that paper does not include experiments requiring code.

• Please see the NeurIPS code and data submission guidelines (https://nips.cc/public/ guides/CodeSubmissionPolicy) for more details.

• While we encourage the release of code and data, we understand that this might not be possible, so “No” is an acceptable answer. Papers cannot be rejected simply for not including code, unless this is central to the contribution (e.g., for a new open-source benchmark).

• The instructions should contain the exact command and environment needed to run to reproduce the results. See the NeurIPS code and data submission guidelines (https://nips.cc/public/ guides/CodeSubmissionPolicy) for more details.

• The authors should provide instructions on data access and preparation, including how to access the raw data, preprocessed data, intermediate data, and generated data, etc.

• The authors should provide scripts to reproduce all experimental results for the new proposed method and baselines. If only a subset of experiments are reproducible, they should state which ones are omitted from the script and why.

• At submission time, to preserve anonymity, the authors should release anonymized versions (if applicable).

• Providing as much information as possible in supplemental material (appended to the paper) is recommended, but including URLs to data and code is permitted.

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

## 9. Code of ethics

Question: Does the research conducted in the paper conform, in every respect, with the NeurIPS Code of Ethics https://neurips.cc/public/EthicsGuidelines?

Answer: [Yes]

Justification: We follow the NeurIPS code of Ethics.

Guidelines:

• The answer NA means that the authors have not reviewed the NeurIPS Code of Ethics.

• If the authors answer No, they should explain the special circumstances that require a deviation from the Code of Ethics.

• The authors should make sure to preserve anonymity (e.g., if there is a special consideration due to laws or regulations in their jurisdiction).

## 10. Broader impacts

Question: Does the paper discuss both potential positive societal impacts and negative societal impacts of the work performed?

Answer: [Yes]

Justification: Our work aims to improve video recommendation for users, enabling them to get more satisfying recommendation results. But we establish the user profile which may have privacy consideration problems.

Guidelines:

• The answer NA means that there is no societal impact of the work performed.

• If the authors answer NA or No, they should explain why their work has no societal impact or why the paper does not address societal impact.

• Examples of negative societal impacts include potential malicious or unintended uses (e.g., disinformation, generating fake profiles, surveillance), fairness considerations (e.g., deployment of technologies that could make decisions that unfairly impact specific groups), privacy considerations, and security considerations.

• The conference expects that many papers will be foundational research and not tied to particular applications, let alone deployments. However, if there is a direct path to any negative applications, the authors should point it out. For example, it is legitimate to point out that an improvement in the quality of generative models could be used to generate deepfakes for disinformation. On the other hand, it is not needed to point out that a generic algorithm for optimizing neural networks could enable people to train models that generate Deepfakes faster.

• The authors should consider possible harms that could arise when the technology is being used as intended and functioning correctly, harms that could arise when the technology is being used as intended but gives incorrect results, and harms following from (intentional or unintentional) misuse of the technology.

• If there are negative societal impacts, the authors could also discuss possible mitigation strategies (e.g., gated release of models, providing defenses in addition to attacks, mechanisms for monitor ing misuse, mechanisms to monitor how a system learns from feedback over time, improving the efficiency and accessibility of ML).

## 11. Safeguards

Question: Does the paper describe safeguards that have been put in place for responsible release of data or models that have a high risk for misuse (e.g., pretrained language models, image generators, or scraped datasets)?

Answer: [NA]

Justification: The paper poses no such risks.

Guidelines:

• The answer NA means that the paper poses no such risks.

• Released models that have a high risk for misuse or dual-use should be released with necessary safeguards to allow for controlled use of the model, for example by requiring that users adhere to usage guidelines or restrictions to access the model or implementing safety filters.

• Datasets that have been scraped from the Internet could pose safety risks. The authors should describe how they avoided releasing unsafe images.

• We recognize that providing effective safeguards is challenging, and many papers do not require this, but we encourage authors to take this into account and make a best faith effort.

## 12. Licenses for existing assets

Question: Are the creators or original owners of assets (e.g., code, data, models), used in the paper, properly credited and are the license and terms of use explicitly mentioned and properly respected?

Answer: [Yes]

Justification: We cite all relevant works for the original owners of assets.

Guidelines:

• The answer NA means that the paper does not use existing assets.

• The authors should cite the original paper that produced the code package or dataset.

• The authors should state which version of the asset is used and, if possible, include a URL.

• The name of the license (e.g., CC-BY 4.0) should be included for each asset.

• For scraped data from a particular source (e.g., website), the copyright and terms of service of that source should be provided.

• If assets are released, the license, copyright information, and terms of use in the package should be provided. For popular datasets, paperswithcode.com/datasets has curated licenses for some datasets. Their licensing guide can help determine the license of a dataset.

• For existing datasets that are re-packaged, both the original license and the license of the derived asset (if it has changed) should be provided.

• If this information is not available online, the authors are encouraged to reach out to the asset’s creators.

## 13. New assets

Question: Are new assets introduced in the paper well documented and is the documentation provided alongside the assets?

Answer: [Yes]

Justification: The new assets are well documented. We prepare the documentation of our code for future reproduction and will release it afterward.

## Guidelines:

• The answer NA means that the paper does not release new assets.

• Researchers should communicate the details of the dataset/code/model as part of their submissions via structured templates. This includes details about training, license, limitations, etc.

• The paper should discuss whether and how consent was obtained from people whose asset is used.

• At submission time, remember to anonymize your assets (if applicable). You can either create an anonymized URL or include an anonymized zip file.

## 14. Crowdsourcing and research with human subjects

Question: For crowdsourcing experiments and research with human subjects, does the paper include the full text of instructions given to participants and screenshots, if applicable, as well as details about compensation (if any)?

Answer: [NA]

Justification: The paper does not involve crowdsourcing nor research with human subjects.

Guidelines:

• The answer NA means that the paper does not involve crowdsourcing nor research with human subjects.

• Including this information in the supplemental material is fine, but if the main contribution of the paper involves human subjects, then as much detail as possible should be included in the main paper.

• According to the NeurIPS Code of Ethics, workers involved in data collection, curation, or other labor should be paid at least the minimum wage in the country of the data collector.

## 15. Institutional review board (IRB) approvals or equivalent for research with human subjects

Question: Does the paper describe potential risks incurred by study participants, whether such risks were disclosed to the subjects, and whether Institutional Review Board (IRB) approvals (or an equivalent approval/review based on the requirements of your country or institution) were obtained?

Answer: [NA]

Justification: The paper does not involve crowdsourcing nor research with human subjects.

Guidelines:

• The answer NA means that the paper does not involve crowdsourcing nor research with human subjects.

• Depending on the country in which research is conducted, IRB approval (or equivalent) may be required for any human subjects research. If you obtained IRB approval, you should clearly state this in the paper.

• We recognize that the procedures for this may vary significantly between institutions and locations, and we expect authors to adhere to the NeurIPS Code of Ethics and the guidelines for their institution.

• For initial submissions, do not include any information that would break anonymity (if applicable), such as the institution conducting the review.

## 16. Declaration of LLM usage

Question: Does the paper describe the usage of LLMs if it is an important, original, or non-standard component of the core methods in this research? Note that if the LLM is used only for writing, editing, or formatting purposes and does not impact the core methodology, scientific rigorousness, or originality of the research, declaration is not required.

Answer: [Yes]

Justification: We use MLLM to help understand video contents and and train the LLM with reinforce ment fine-tuning to simulate user decision.

Guidelines:

• The answer NA means that the core method development in this research does not involve LLMs as any important, original, or non-standard components.

• Please refer to our LLM policy (https://neurips.cc/Conferences/2025/LLM) for what should or should not be described.

## A Comprehensive Review on Harnessing Large Language Models to Overcome Recommender System Challenges

# A Comprehensive Review on Harnessing Large Language Models to Overcome Recommender System Challenges

RAHUL RAJA, <sup>Linkedin,</sup> <sup>Carnegie</sup> <sup>Mellon</sup> <sup>University,</sup> <sup>Stanford</sup> <sup>University,</sup> <sup>USA</sup>

ANSHAJ VATS, <sup>Meta,</sup> <sup>USA</sup>

ARPITA VATS, <sup>Linkedin,</sup> <sup>Meta</sup> <sup>AI,</sup> <sup>Amazon,</sup> <sup>Boston</sup> <sup>University,</sup> <sup>USA</sup>

ANIRBAN MAJUMDER, <sup>Amazon,</sup> <sup>USA</sup>

Recommender systems have traditionally followed modular architectures comprising candidate generation, multi-stage ranking, and re-ranking, each trained separately with supervised objectives and hand-engineered features. While efective in many domains, such systems face persistent challenges including sparse and noisy interaction data, cold-start problems, limited personalization depth, and inadequate semantic under standing of user and item content. The recent emergence of Large Language Models (LLMs) ofers a new paradigm for addressing these limitations through unified, language-native mechanisms that can generalize across tasks, domains, and modalities. In this paper, we present a comprehensive technical survey of how LLMs can be leveraged to tackle key challenges in modern recommender systems. We examine the use of LLMs for prompt-driven candidate retrieval, language-native ranking, retrieval-augmented generation (RAG) and conversational recommendation, illustrating how these approaches enhance personalization, semantic alignment, and interpretability without requiring extensive task-specific supervision. LLMs further enable zero- and few-shot reasoning, allowing systems to operate efectively in cold-start and long-tail scenarios by leveraging external knowledge and contextual cues. We categorize these emerging LLM-driven architectures and analyze their efectiveness in mitigating core bottlenecks of conventional pipelines. In doing so, we provide a structured framework for understanding the design space of LLM-enhanced recommenders, and outline the trade-ofs between accuracy, scalability, and real-time performance. Our goal is to demonstrate that LLMs are not merely auxiliary components but foundational enablers for building more adaptive, semantically rich, and user-centric recommender systems

## ACM Reference Format:

Rahul Raja, Anshaj Vats, Arpita Vats, and Anirban Majumder. 2025. A Comprehensive Review on Harnessing Large Language Models to Overcome Recommender System Challenges. 1, 1 (October 2025), 48 pages. https://doi.org/10.1145/nnnnnnn.nnnnnnn

## 1 Introduction

Recommender systems have become essential across a broad spectrum of digital applications, including content streaming, e-commerce, education, recruiting, and social media platforms [2, 25, 52]. From personalized playlists on Spotify to tailored learning paths in MOOCs and targeted ads on LinkedIn, recommender systems play a pivotal role in shaping user experience and driving engagement. Despite their widespread adoption and continuous improvements, these systems face enduring challenges such as data sparsity, cold-start problems, dynamic user interests, and explainability [160]. As modern pipelines grow in complexity—with multi-stage architectures, large-scale retrieval, and diverse modalities—the demands for scalability, transparency, and adaptability have intensified. Recommender systems have traditionally followed modular architectures comprising candidate generation, multi-stage ranking, and re-ranking—each trained separately using supervised objectives and hand-engineered features [19]. While efective in many domains, such systems face persistent challenges, including sparse and noisy interaction data, cold-start problems, limited personalization depth, and inadequate semantic understanding of user and item content.

The recent emergence of Large Language Models (LLMs) ofers a new paradigm for addressing these limitations through unified, language-native mechanisms that can generalize across tasks, domains, and modalities. In this paper, we present a comprehensive technical survey of how LLMs can be leveraged to tackle key challenges in modern recommender systems. We examine the use of LLMs for prompt-driven candidate retrieval, language-native ranking, retrieval-augmented gen eration (RAG), and conversational recommendation—illustrating how these approaches enhance personalization, semantic alignment, and interpretability without requiring extensive task-specific supervision. LLMs also enable zero- and few-shot reasoning, allowing systems to operate efectively in cold-start and long-tail scenarios by leveraging external knowledge and contextual cues. We categorize these emerging LLM-driven architectures and analyze their efectiveness in mitigating core bottlenecks of conventional pipelines. In doing so, we provide a structured framework for understanding the design space of LLM-enhanced recommender systems, and outline trade-ofs between accuracy, scalability, and real-time performance.

Our work provides a foundation for researchers and engineers to reimagine recommender systems in the era of large language modeling, and highlights promising directions for future innovation.

## 2 Evolution of Architectures in Recommender Systems

Recommender systems have progressed from heuristic rules to collaborative filtering, latent fac torization, neural and graph-based models, and finally industrial-scale retrieval frameworks. Each paradigm enhanced expressiveness, scalability, and the ability to capture complex dependencies.

## 2.1 From Heuristics to Latent Factor Models

Early recommenders used deterministic heuristics such as popularity- and co-occurrence-based rules [9, 185, 187], which scale well but lack personalization. Collaborative Filtering (CF) [264] introduced personalization by exploiting similarity in interaction patterns between users or items. While simple and interpretable, CF sufers from sparsity and cold-start issues.

Matrix Factorization (MF) [88, 90] addressed scalability by embedding users and items into a shared low-dimensional space, with predictions computed via inner products of latent vectors. Variants such as ALS [282] and SVD++ [90] incorporated implicit feedback and became widely adopted in industrial systems due to their balance of accuracy and eficiency.

## 2.2 Hybrid and Neural Extensions

Content-Based Filtering (CBF) [137] enriched recommendations with item attributes such as textual categorical, or visual embeddings, making it more robust to cold-start users. However, CBF tends to overspecialize. Hybrid models [13] combined collaborative and content signals, exemplified by LightFM [93] and DeepFM [55], which integrate metadata with learned embeddings.

Deep learning extended this line with Neural Collaborative Filtering (NCF) [62], which replaces linear interaction functions with nonlinear neural networks, and Wide & Deep [26], which jointly optimizes memorization and generalization. These architectures established the basis for modern industrial recommenders.

![](images/986b77a95723aeb32a7495cb858d468dd56d13a41492dd6e8cecc4c7b727f3e4.jpg)  
Fig. 1. Taxonomy of recommender system challenges and corresponding LLM-based solutions. The framework categorizes challenges into four major areas—data-centric, modeling and algorithmic, evaluation, and privacy/security—each with sub-problems and LLM-driven strategies for addressing them.’=

## 2.3 Sequential and Graph-Based Models

User behavior often exhibits temporal and contextual dynamics. Sequence-aware recommenders such as GRU4Rec [63] applied recurrent neural networks to session data, while transformer-based approaches (e.g., SASRec [83], BERT4Rec [199], TiSASRec [107]) leveraged self-attention to capture long-range dependencies and temporal intervals. These models outperform traditional CF in sequential domains such as streaming and e-commerce.

In parallel, graph-based recommenders [224] represented interactions as bipartite graphs. Neural Graph Collaborative Filtering (NGCF) [253] propagated embeddings through nonlinear message passing, while LightGCN [61] simplified this to linear aggregation, improving both accuracy and scalability. PinSage [253] scaled graph-based recommendation to billions of nodes using random walks and sampling, enabling deployment in web-scale platforms like Pinterest.

## 2.4 Industrial-Scale Retrieval Frameworks

With item catalogs often exceeding billions, retrieval eficiency became a dominant concern. Twotower architectures [256] learn independent embeddings for users and items, with relevance computed as the inner product between vectors. Pre-computed item embeddings can be indexed using Approximate Nearest Neighbor (ANN) search, enabling sublinear retrieval times.

The YouTube DNN [32] demonstrated the efectiveness of deep two-tower retrieval with sampled softmax, while Facebook’s DLRM [153] integrated sparse and dense features with cross-feature interaction layers. These retrieval modules form the candidate generation stage in multi-stage pipelines, with re-ranking typically handled by more expressive models such as gradient boosting or transformers.

## 3 Key Components of Recommender System Pipelines

## 3.1 Candidate Generation

Candidate generation is the first stage in large-scale recommender systems, responsible for filtering a massive corpus of items down to a smaller subset of potentially relevant candidates for a given user. This stage prioritizes recall over precision, ensuring that relevant items are included in the candidate set, even if some irrelevant items are also retrieved. Precision is handled in later stages through more computationally intensive ranking models. The goal is to eficiently retrieve a set of items $C ( u ) \subset \mathcal { I }$ for a user $u \in { \mathcal { U } } ,$ , where <sub>I</sub> denotes the entire item corpus. Formally, candidate generation can be defined as retrieving all items $i \in \mathcal { I }$ such that the similarity between the user embedding $f _ { u }$ and the item embedding $f _ { i }$ exceeds a threshold ??, i.e.,

$$
\mathcal {C} (u) = \{i \in \mathcal {I} \mid \mathrm{sim} (f _ {u}, f _ {i}) \geq \tau \},
$$

where $s \mathrm { i m } ( \cdot , \cdot )$ is a similarity function such as dot product or cosine similarity. Several techniques are commonly employed in candidate generation. Approximate Nearest Neighbor (ANN) search allows for eficient similarity-based retrieval using indexing structures like HNSW or product quantization [71, 144]. Graph-based methods leverage user-item interaction graphs, using algo rithms such as random walks [167] or personalized PageRank [60] to identify semantically or behaviorally related items. Heuristic filtering approaches use hand-crafted rules based on metadata, popularity, or recent activity to shortlist items quickly. Embedding-based retrieval methods, often built using two-tower or dual encoder models, learn representations for users and items such that similar entities lie close in a shared vector space [247]. Additionally, session-based models take into account recent user interactions and temporal patterns, often utilizing RNNs [63] or attention mechanisms [108] to generate context-aware candidates.

Efective candidate generation requires balancing computational eficiency with the need for broad item coverage. Systems must be optimized for low latency and high throughput while ensuring that the candidate pool includes a diverse and relevant set of items to support personalization downstream. Periodic updates to item indices and embeddings are essential to maintain temporal relevance. Overall, the success of downstream ranking models is closely tied to the quality and coverage of the candidate set produced in this stage.

## 3.2 Scoring and Ranking

Once the candidate set is generated, the next stage in the recommendation pipeline involves computing a relevance score for each candidate and producing a ranked list. This scoring process is handled by machine learning models that are typically more expressive and computationally expensive than those used in candidate generation, since they operate on a smaller set of items. These models ingest high-dimensional features encompassing user profiles, item attributes, and contextual signals such as time of day, device type, and recent interactions. Common architectures for this stage include gradient-boosted decision trees (GBDT) [85], deep neural networks (DNNs) [32], and transformer-based models [199], which are trained to predict item relevance based on learned representations of user-item pairs.

Formally, for each user $u \in \mathcal { U }$ and candidate item $i \in C ( u )$ , the system learns a scoring function $s ( u , i )$ defined as:

$$
s (u, i) = f _ {\theta} (\phi_ {u}, \phi_ {i}, \psi_ {u, i}),
$$

where $\phi _ { u }$ and $\phi _ { i }$ are the embedding representations of the user and item, respectively, and $\psi _ { u , i }$ denotes additional features capturing user-item interaction context. The function $f _ { \theta }$ is typically a feed-forward neural network or transformer-based encoder that outputs a scalar relevance score. The top-ranked items are selected by sorting candidates in descending order of $s ( u , i )$

In multi-task learning settings, the model predicts several outcomes simultaneously—such as click probability, dwell time, and engagement—using a shared encoder and task-specific output heads:

$$
h = \mathrm{Encoder} _ {\theta} (\phi_ {u}, \phi_ {i}, \psi_ {u, i}),
$$

$$
\hat {y} _ {\text { click }} = \sigma (W _ {\text { click }} h), \quad \hat {y} _ {\text { dwell }} = \operatorname{ReLU} (W _ {\text { dwell }} h), \quad \hat {y} _ {\text { engage }} = \sigma (W _ {\text { engage }} h),
$$

where $h$ is the latent representation, $\sigma$ denotes the sigmoid function, and $W ^ { \prime } s$ are task-specific projection matrices. The total training loss is computed as a weighted combination of individual task losses:

$$
\mathcal {L} = \lambda_ {1} \cdot \mathcal {L} _ {\text { click }} + \lambda_ {2} \cdot \mathcal {L} _ {\text { dwell }} + \lambda_ {3} \cdot \mathcal {L} _ {\text { engage }}.
$$

This setup enables joint optimization across objectives and improves the model’s ability to learn shared behavioral patterns. Domain-specific features further enhance personalization, such as temporal trends, item freshness, category information, and content embeddings. The scoring and ranking stage is critical for final recommendation quality, as it ultimately determines the ordering and presentation of content to the user.

## 3.3 Post-Ranking and Calibration

After the initial scoring and ranking phase, post-ranking modules are applied to adjust the ranked list in order to align recommendations with broader system-level goals beyond user-item relevance. These objectives include promoting content diversity, controlling item fatigue, ensuring fairness across item categories or creators, and maintaining freshness in temporal contexts. This stage is critical to shaping the final user experience and achieving long-term business metrics such as content exposure, retention, and platform health.

The input to this module is an already ranked list $\mathcal { R } ( u ) = \{ i _ { 1 } , i _ { 2 } , . . . , i _ { k } \}$ with associated relevance scores $s ( u , i _ { j } )$ . Post-ranking adjusts these scores via a transformation function $g ( \cdot )$ , which considers additional factors such as diversity penalties or freshness boosts:

$$
s ^ {\prime} (u, i _ {j}) = g (s (u, i _ {j}), \delta (i _ {j}), \gamma (i _ {j})),
$$

where:

$s ( u , i _ { j } )$ is the original relevance score,

$\delta ( i _ { j } )$ is a diversity-aware adjustment factor (e.g., based on item similarity or content clusters), $\gamma ( i _ { j } )$ is a freshness or recency factor.

One common technique is <sub>diversity-aware</sub> <sub>re-ranking</sub>, which penalizes redundant content in the top positions using a marginal gain function. This can be formalized using Determinantal Point Processes (DPP) [94] or greedy submodular optimization [6]. Similarly, <sub>fatigue</sub> <sub>control</sub> mechanisms reduce the score of items already seen or interacted with recently, preventing oversaturation.

In dynamic settings, <sub>exploration-exploitation</sub> <sub>trade-ofs</sub> are addressed through bandit algorithms [111] or reinforcement learning [17]. These methods adjust the final ranking to allow new or uncertain items to be exposed to users with non-zero probability. In a contextual bandit framework, the post-ranking score $s ^ { \prime }$ may incorporate expected reward:

$$
s ^ {\prime} (u, i _ {j}) = \mathbb {E} [ r _ {u, i _ {j}} \mid x _ {u, i _ {j}} ],
$$

where $r _ { u , i _ { j } }$ is the reward (e.g., click, engagement) and $x _ { u , i _ { j } }$ are the contextual features of the interaction.

Overall, post-ranking ensures that the final list achieves a desirable trade-of between individual relevance and system-level goals. This stage plays a critical role in aligning model outputs with platform constraints and policy requirements while enhancing long-term user satisfaction.

## 4 Evolving Recommender Systems: Addressing Traditional Challenges with LLM-Based Solutions

Recommender systems deployed in industrial settings face a wide array of challenges, many of which stem from the nature of the data itself. Below, we outline key data-centric issues and describe how leading platforms address them using scalable machine learning techniques, representation learning, and multimodal data fusion.

In this section, we explore how LLMs can be integrated into Recommender system architectures to address six main categories of industrial challenges. We begin with data understanding and cold start issues and then progress through modeling, evaluation, system design, privacy, and organizational concerns. For each area, we discuss not only the strengths of LLM-based approaches but also the practical trade-ofs and open research directions they entail.

Table 1. Challenges in Recommender Systems and Corresponding LLM-Based Solutions

<table><tr><td>Challenges</td><td>Sub-problem</td><td>LLM-Based Solutions</td><td>References</td></tr><tr><td rowspan="9">Data-Centric</td><td rowspan="9">Cold Start</td><td>Content-Conditioned Generation</td><td>[36, 82, 117, 243, 257, 261]</td></tr><tr><td>Retrieval-Augmented Generation</td><td>[5, 48, 53, 68]</td></tr><tr><td>Zero-Shot Personalization</td><td>[168, 209, 233]</td></tr><tr><td>Representation Bootstrapping</td><td>[69, 208]</td></tr><tr><td>Language-Native Dialogue</td><td>[16, 219, 276]</td></tr><tr><td>Prompt-Based Conditioning</td><td>[75, 175]</td></tr><tr><td>Multimodal Embedding Synthesis</td><td>[4, 176, 210, 255]</td></tr><tr><td>Meta-Learning for Fast Adaptation</td><td>[44, 99, 223]</td></tr><tr><td>Cross-Domain Transfer</td><td>[131, 216, 218, 251]</td></tr><tr><td rowspan="2"></td><td rowspan="2">Data Sparsity</td><td>Text-Driven Generalization</td><td>[70, 190, 266]</td></tr><tr><td>Semantic Matching via Embedding</td><td>[33, 222]</td></tr><tr><td></td><td>Noisy Implicit Feedback</td><td>Feedback Interpretation with Contextual Prompts</td><td>[10, 97, 120, 201, 257]</td></tr><tr><td rowspan="2"></td><td rowspan="2">Temporal Drift</td><td>Temporal Adaptation with LLMs</td><td>[95, 270]</td></tr><tr><td>Structural and Hybrid Integration</td><td>[58, 141]</td></tr></table>

Continued on next page

Table 1 – continued from previous page

<table><tr><td>Challenges</td><td>Sub-problem</td><td>LLM-Based Solutions</td><td>References</td></tr><tr><td></td><td>Multimodal Data Integration</td><td>Modal-Aware WeightingUnified RepresentationCross-Modal AlignmentMultimodal ImputationSemantic Fusion</td><td>[143, 243, 257][138, 139][184, 267][20, 171, 279][3, 81]</td></tr><tr><td rowspan="2">Modeling &amp; Algorithmic</td><td>Personalization vs. Generalization</td><td>Instruction-Tuned GeneralizationPrompt-Tuned PersonalizationBehavioral DiversityMultitask Prompting</td><td>[128][75, 119][228]</td></tr><tr><td>Scalability of Deep Models</td><td>LLM-Based DistillationPrompt-Efficient InferenceTwo-Stage Hybrid PipelinesSparse Activation Architectures</td><td>[30, 75, 226][117, 127, 195, 274][67, 104, 158, 257][39, 123]</td></tr><tr><td></td><td>Long-Tail Modeling</td><td>Content-Enriched GenerationRetrieval-Augmented Tail ExpansionTail-Aware Few-Shot PromptingMultimodal Tail Representation</td><td>[82, 261][36, 217, 235][30, 228][156, 217]</td></tr><tr><td>Evaluation &amp; Experimentation</td><td>Offline-Online Gap</td><td>Counterfactual EvaluationOffline Metric RecalibrationBehavior-Level SatisfactionInteractive User SimulationEvaluation Metric Generation</td><td>[51, 72, 182][115, 237][100, 273][8, 192][132, 241, 281]</td></tr><tr><td></td><td>Sparse Conversion Labels</td><td>Proxy Signal AugmentationInstruction-Tuned Label ImputationGenerative Multi-Task LearningCounterfactual Label ReasoningLanguage-Guided Reweighting</td><td>[36, 257, 261][234][46][80][205]</td></tr><tr><td></td><td>Balancing Immediate Engagement</td><td>LLM-Based Proxy Reward EstimationCounterfactual DialoguePreference Drift DetectionMulti-Objective RL with LLM-Guided Reward</td><td>[163, 245][41, 109][275][98, 271][29, 133, 286]</td></tr><tr><td>Privacy, Security, &amp;</td><td>User Data Sensitivity</td><td>Token Attribution and Prompt Fingerprinting</td><td>[110]</td></tr><tr><td></td><td>Compliance with Laws</td><td>Streaming Log Replay + Token-Level Attribution</td><td>[162, 239]</td></tr><tr><td></td><td>Differential Privacy &amp; Federated Learning</td><td>LLMs for Ephemeral PersonalizationGradient-Sanitized Fine-TuningFederated Prompting</td><td>[146][154, 177][114, 236, 278]</td></tr><tr><td></td><td>Data Access and Governance</td><td>Data Minimization via LLMsInstructable Privacy FiltersSynthetic Data Generation</td><td>[11, 126][18, 38][122, 238]</td></tr></table>

## 4.1 Data-Centric Challenges

Recommender systems deployed in industrial environments face a host of challenges rooted not just in algorithmic design, but in the quality, availability, and dynamics of the underlying data. The data-centric issues significantly influence model generalization, fairness, personalization, and system robustness. Below, we dissect key categories of data-centric challenges and discuss how they impact large-scale deployment and learning dynamics in recommender pipelines.

<sub>4.1.1</sub> <sub>Cold</sub> <sub>Start</sub> <sub>Problem.</sub> The <sub>cold</sub> <sub>start</sub> <sub>problem</sub> refers to the dificulty of generating reliable recommendations for new users or new items due to the absence of interaction history. This issue is particularly acute in collaborative filtering (CF) systems, where latent representations are learned from observed user–item interactions.

In matrix factorization frameworks, predicted preferences are typically computed as:

$$
\hat {r} _ {u i} = \mathbf {p} _ {u} ^ {\top} \mathbf {q} _ {i}
$$

where $\mathbf { p } _ { u } , \mathbf { q } _ { i } \in \mathbb { R } ^ { d }$ are the latent embeddings of user ?? and item ??. These embeddings are optimized by minimizing a loss over the set of observed interactions $O ;$

$$
\min _ {\left\{\mathbf {p} _ {u} \right\}, \left\{\mathbf {q} _ {i} \right\}} \sum_ {(u, i) \in O} \mathcal {L} (\hat {r} _ {u i}, r _ {u i}) + \lambda \left(\left\| \mathbf {p} _ {u} \right\| ^ {2} + \left\| \mathbf {q} _ {i} \right\| ^ {2}\right)
$$

In cold start settings, when $u ^ { \prime } \notin O _ { u }$ or $i ^ { \prime } \notin O _ { i }$ , the corresponding embeddings $\mathbf { p } _ { u ^ { \prime } }$ or <sub>q??′</sub> are poorly initialized or undefined, leading to degraded or invalid predictions:

$$
\hat {r} _ {u ^ {\prime} i} = \mathbf {p} _ {u ^ {\prime}} ^ {\top} \mathbf {q} _ {i} \quad \mathrm{or} \quad \hat {r} _ {u i ^ {\prime}} = \mathbf {p} _ {u} ^ {\top} \mathbf {q} _ {i ^ {\prime}}
$$

This challenge is exacerbated in large-scale, dynamic environments where thousands of new users and items enter the system daily [170]. Even more complex architectures such as two-tower models [32] or deep sequential recommenders [63] rely on embedding representations learned from prior interactions, and thus remain vulnerable to cold start scenarios. The sparsity of user–item signals and the lack of initialization paths for unseen entities make cold start a persistent bottleneck in the design of efective recommender systems [164, 188]. LLMs ofer a paradigm shift in mitigating the cold start problem by leveraging their ability to process rich textual and contextual information without requiring historical interaction data [36, 222]. Unlike traditional collaborative filtering methods that depend on dense user–item matrices, LLMs can infer relevance through semantic reasoning, prompt-based generation, and cross-modal understanding. Let’s examine how LLMs can solve the cold start problem in recommender systems.

<sub>Content-Conditioned</sub> <sub>Generation</sub> <sub>–</sub> LLMs pretrained on web-scale corpora possess rich world knowledge and linguistic priors, enabling them to generate item recommendations solely from textual descriptions. This paradigm is particularly advantageous in cold-start and low-resource scenarios where interaction histories are sparse or nonexistent. Traditional recommender systems often struggle in these settings, as they depend heavily on collaborative signals (e.g., clicks, ratings, watch time). In contrast, LLMs can interpret and reason over content attributes such as titles, descriptions, reviews, genres, and even product specifications.

For instance, Generative Recommenders [117, 261] employ prompt-based methods where user queries or profiles are combined with product metadata to produce ranked outputs or candidate lists. In these setups, the generation process bypasses the need for learned user-item embeddings and instead leverages natural language priors encoded in the LLM:

$$
\hat {r} _ {u i} = \mathrm{LLM} \left(" \text {User profile:}" + x _ {u} +" \text {Item:}" + x _ {i}\right)
$$

Such models can be further enhanced with instruction prompts, prefix tuning, or adapters to align generation with domain-specific preferences and intents. Recent work demonstrates that even simple prompts can elicit meaningful ranking signals, especially when the model is instructed to output preference scores, reasoning traces, or direct answers.

This approach has been adopted in real-world pipelines, including JD.com’s product recommendation and Pinterest’s item-to-item generation [243, 257], where structured item metadata and textual attributes are encoded as input contexts. Furthermore, systems like GPTRec and PromptRec have shown how generative LLMs can synthesize interaction labels (e.g., likelihood of liking or pur chasing an item) from textual descriptions, enabling bootstrap datasets for pretraining, self-training, or teacher-student distillation in downstream rankers.

By conditioning generation on content alone, these models enable rapid personalization without requiring prior interactions, thereby ofering a scalable solution to cold-start recommendation, catalog expansion, long-tail item surfacing, and new-user onboarding. As instruction tuning and few-shot prompting mature, we expect content-conditioned generation to play a central role in building adaptable, zero-shot capable recommender agents that generalize across domains with minimal supervision.

<sub>Retrieval-Augmented</sub> <sub>Generation</sub> <sub>(RAG)</sub> <sub>–</sub> RAG-based methods enhance LLMs with a retrieval module that selects relevant items or documents based on the input query. In recommender systems, this architecture decouples memorization from inference, allowing the model to attend to similar items, behavioral patterns, or metadata even when the target entity is entirely new or sparsely observed [36, 82]. By combining parametric knowledge from the LLM with non-parametric access to a large external index, RAG frameworks enable more accurate, controllable, and interpretable recommendation outputs.

Formally, the LLM decoder conditions on the retrieved context $\mathcal { R } ( x _ { u } )$ to generate a recommen dation or compute a relevance score:

$$
P (i \mid x _ {u}) = \operatorname{Decoder} _ {\mathrm{LLM}} \left(x _ {u}, \mathcal {R} \left(x _ {u}\right)\right)
$$

where $\mathcal { R } ( x _ { u } )$ denotes a retrieved support set from a product, user, or content database, often implemented using approximate nearest neighbor (ANN) search or semantic retrievers (e.g., dual encoder models or dense passage retrievers).

In practice, retrieval can be conditioned on user intent, content type, or temporal signals, enabling RAG pipelines to dynamically personalize the input context [68]. For instance, retrieved exemplars can include past purchases by similar users [48], product FAQs, reviews, or even click sequences from related users. The decoder then performs sequence-level reasoning over this context to either generate ranking scores, provide justifications (e.g., “because you liked $\mathrm { X } . . . ^ { \mathfrak { N } } )$ , or directly synthesize recommendations.

Amazon Alexa’s RecRAG and OpenAI’s plugin-based recommendation prototypes have explored such architectures in production-like environments [53, 117], demonstrating their applicability in real-time systems. These systems often include fast-refresh retrievers and pre-encoded knowledge bases to ensure responsiveness at inference time.

Recent advancements such as contrastive retrieval tuning, multi-hop retrieval [5], and instructionbased reranking [37] are further improving the eficacy of RAG for RecSys. Moreover, hybrid approaches that blend retrieval with fine-tuned rerankers or LLM feedback loops (e.g., re-querying or dynamic re-ranking) are emerging as state-of-the-art strategies for multi-objective personalization tasks [47]. Looking ahead, RAG presents a promising direction for bridging symbolic reasoning (via retrieval) and generative modeling, allowing recommender systems to scale across domains, maintain explainability, and adapt to evolving content landscapes with minimal retraining [196].

<sub>Zero-Shot</sub> <sub>Personalization</sub> <sub>–</sub> Instruction-tuned LLMs (e.g., GPT-4 [157], FLAN-T5 [30]) are capable of zero-shot recommendation through natural language queries [233]. These models are pretrained to follow open-ended instructions and can perform complex reasoning and generation tasks without explicit task-specific fine-tuning. In the recommendation context, they generalize to new users or items by leveraging semantic cues from textual metadata, behavior descriptions, or demographic features, bypassing the need for supervised training or interaction histories on the specific platform [168].

This capability enables highly flexible recommendation systems where users can describe their preferences in natural language e.g., “I’m looking for a sci-fi show with philosophical themes like Black Mirror” or “Suggest books similar to what a data science graduate might enjoy.” The model can interpret this intent, perform semantic matching over a corpus of content metadata, and return high-quality, context-aware suggestions without explicit training data.

Spotify’s conversational agents [209] and TikTok’s personalization assistant have applied these capabilities to enhance cold-start user onboarding [200], where traditional matrix factorization or collaborative filtering fails due to lack of prior data [249]. These LLM-driven systems allow users to express their needs directly via natural language, supporting dynamic profile construction and preference elicitation through dialogue. This leads to faster convergence to relevant recommendations and improved first-session satisfaction metrics [166].

![](images/a5256ed1677314e0459127edfda9e3ac9bc70ed40647e9231208c49642903643.jpg)  
Fig. 2. Illustration of representation bootstrapping solution using LLM to generate dense user and item embeddings from textual or metadata descriptions. Newly onboarded users and newly listed items are mapped to the embedding space via LLM-based encoders, enabling efective integration into the recommender system without historical interaction data.

<sub>Representation</sub> <sub>Bootstrapping</sub> <sub>–</sub> LLMs can synthesize dense vector representations for previously unseen users and items directly from textual, profile, or metadata descriptions, ofering a lightweight embedding initialization pipeline [208]. This capability is particularly valuable in <sub>cold-start</sub> scenarios, where traditional collaborative filtering methods struggle due to the absence of historical interaction data. By leveraging rich semantic priors from pretraining on large corpora, LLMs enable <sub>zero-shot</sub> <sub>generalization</sub>, allowing the system to produce meaningful embeddings for novel entities without requiring full model retraining or embedding table updates. [69]

For instance, newly listed products on e-commerce platforms or newly onboarded users can be immediately embedded into the same vector space as existing catalog items and users:

$$
\mathbf {q} _ {i ^ {\prime}} = f _ {\mathrm{LLM}} (x _ {i ^ {\prime}}), \quad \mathbf {p} _ {u ^ {\prime}} = f _ {\mathrm{LLM}} (x _ {u ^ {\prime}})
$$

where $x _ { i ^ { \prime } }$ and $x _ { u ^ { \prime } }$ denote available textual or structured metadata (e.g., product titles, descriptions, user bios, or interests). These bootstrapped vectors can be plugged into existing retrieval or ranking models with minimal latency, significantly reducing onboarding time.

Moreover, such LLM-derived embeddings can serve as <sub>informative</sub> <sub>priors</sub> during fine-tuning or personalization [268]. They can be adapted via techniques like prompt tuning, adapter layers, or shallow re-embedding using user behavior logs, enabling rapid domain alignment while preserving generalization capabilities [230]. This framework has been shown to outperform static initialization strategies in real-world systems [207], and aligns with emerging trends toward <sub>retrieval-augmented</sub> <sub>generation</sub> and <sub>hybrid</sub> <sub>recommender</sub> <sub>architectures</sub> that blend semantic understanding with behavioral learning.

<sub>Language-Native</sub> <sub>Dialogue</sub> <sub>Systems</sub> <sub>–</sub> LLMs as conversational interfaces can dynamically elicit user preferences in natural language through real-time feedback loops, thereby bypassing the need for extensive logged interactions [16]. Recent systems like DialogRec [219] extend this with reinforcement learning over user responses.

This paradigm enables <sub>language-native</sub> recommendation systems, where user profiles are not just inferred from passive behavior logs but actively shaped via dialogue history [276]. The model continuously updates its belief about the user’s intent and preferences through clarifying questions, preference disambiguation, and exploratory queries. Mathematically, the user representation can be modeled as a latent belief state $\mathbf { b } _ { u } ^ { t }$ updated over time:

$$
\mathbf {b} _ {u} ^ {t + 1} = f _ {\mathrm{update}} (\mathbf {b} _ {u} ^ {t}, a _ {t}, r _ {t})
$$

where $a _ { t }$ is the system’s action (e.g., a recommendation or query), and $r _ { t }$ is the user’s response interpreted by the LLM.

Such systems can employ few-shot prompting or in-context learning to tailor responses dynamically without task-specific retraining [74]. Additionally, integration with RAG modules allows grounding recommendations in real-time inventory or knowledge bases, increasing factual alignment and diversity [40].

These conversational systems also pave the way for more inclusive recommendation strategies by reducing dependence on historical bias and enabling preference elicitation in underrepresented cohorts [91]. In high-stakes domains like healthcare, education, or legal support, the ability to engage users in naturalistic conversation supports transparent, explainable, and ethical recommendation pipelines [43]. As user preferences evolve over time, language-native agents ofer a compelling path <sup>toward</sup> continual preference learning <sup>[260]</sup> <sup>and</sup> intent-aware retrieval <sup>[23],</sup> <sup>making</sup> <sup>them</sup> <sup>an</sup> ideal front-end for next-generation recommender architectures.

<sub>Prompt-Based</sub> <sub>Conditioning</sub> <sub>–</sub> Prompt-based conditioning with LLMs enables flexible zeroshot personalization by translating user-item interactions into natural language templates [175]. This approach reframes recommendation as a language modeling task, allowing LLMs to directly estimate the likelihood of recommending item ?? to user ?? using a natural language prompt:

$$
P (i \mid x _ {u}) = \text { LLM } (" \text { User   context: }" + x _ {u} +" \text { Recommend: }" + x _ {i})
$$

where $x _ { u }$ and $x _ { i }$ represent the textual representations (e.g., profile, metadata, reviews) of the user and item, respectively. Unlike traditional scoring models that rely on latent dot-product similarity or supervised learning over explicit interaction labels, this formulation is <sub>instruction-driven</sub> and supports a wide range of open-ended tasks.

By conditioning generation or scoring on structured prompts, this modality-agnostic interface allows for multiple downstream applications: justification of recommendations (e.g., “why was this item selected?”), prediction of preference explanations (e.g., “what might the user say about this item?”), and hybrid tasks such as comparative ranking or critique generation. It enables interaction-rich scenarios even in the absence of dense interaction histories, facilitating <sub>few-shot</sub> <sub>generalization</sub> in cold-start settings [134].

Notably, recent systems like PromptRec [36], PROMO [75], and OpenAI’s plugin-based RecSys prototype [117] have operationalized such strategies in both online and ofline settings. These systems dynamically compose prompts using structured user/item attributes and contextual cues (e.g., time, location, browsing intent), efectively merging retrieval and generation within a single architecture.

Furthermore, prompt-based approaches are inherently interpretable and modular, ofering compatibility with personalization layers, response reranking, or safety filters [220]. Their plug-and-play nature aligns well with <sub>low-code/zero-code</sub> deployment paradigms, reducing the friction in experimentation and scaling across domains and languages [24]. As LLMs continue to improve in understanding long-tail user intents and compositional queries, prompt-based conditioning is emerging as a powerful mechanism for building controllable, transparent, and context-aware recommender systems.

<sub>Multimodal</sub> <sub>Embedding</sub> <sub>Synthesis</sub> <sub>–</sub>When textual information alone is insuficient for high–fidelity personalization, LLMs can be situated at the center of a <sub>multimodal</sub> pipeline that fuses visual, structured, and temporal signals Figure 3). d behavioral signals into a unified representation [176]. A generic fusion template is:

$$
\mathbf {q} _ {i} = f _ {\mathrm{text}} (x _ {i} ^ {\mathrm{text}}) + f _ {\mathrm{img}} (x _ {i} ^ {\mathrm{img}}) + f _ {\mathrm{meta}} (x _ {i} ^ {\mathrm{meta}}),
$$

where $\boldsymbol { x } _ { i } ^ { \mathrm { t e x t } }$ (e.g., product title, description), $x _ { i } ^ { \mathrm { { i m g } } }$ (primary and auxiliary images), and $x _ { i } ^ { \mathrm { m e t a } }$ (price, brand, category, timestamp, CTR priors) are embedded by modality-specific encoders and subsequently <sub>aligned</sub> in a shared latent space.

![](images/670970267364757c8cae3f28db5539a1eb0eb229cbf66ec7090e92468e1f29ab.jpg)  
Fig. 3. Overview of the Proposed Multi-Modal Sequence Learning Framework.(a) The model processes timestamp, ID, text, and image sequences using BERT, ViT, and ID embeddings, followed by Interactive and Temporal MoE modules for expert routing. Outputs are fed into Transformers for prediction. (b) Multi task learning includes category prediction, contrastive learning on ID embeddings, and placeholder-based contrastive learning across modalities [265].

State-of-the-art LLMs such as Flamingo [4] use cross-attention layers to inject image token embeddings into frozen language blocks, while lighter adapters or multi-head cross-modal trans formers can accomplish a similar goal with lower inference cost. The fusion function can be further refined with a learned gating vector $\gamma _ { i }$ :

$$
\mathbf {q} _ {i} = \boldsymbol {\gamma} _ {i} ^ {\top} \left[ \begin{array}{c} f _ {\text { text}} (x _ {i} ^ {\text { text }}) \\ f _ {\text { img }} (x _ {i} ^ {\text { img }}) \\ f _ {\text { meta }} (x _ {i} ^ {\text { meta }}) \end{array} \right], \qquad \gamma_ {i, m} = \frac {\exp (g _ {m})}{\sum_ {m ^ {\prime}} \exp (g _ {m ^ {\prime}})},
$$

where the gating logits $g _ { m }$ are produced by an <sub>attention-over-modalities</sub> layer conditioned on contextual cues (e.g. user intent or query). This adaptive weighting has two practical advantages: (i) it suppresses noisy modalities when signals are weak (e.g. blurry images) and (ii) it accentuates the most informative channel for each request, leading to more stable cold-start performance [255]. Amazon’s Multimodal RecSys [210] employs hierarchical fusion: fine-tuned CLIP encoders supply image vectors, BERT-based encoders supply text, and catalog metadata is featurized via embedding tables. A shallow cross-modal transformer merges these signals and outputs $\mathbf { q } _ { i }$ to a traditional ANN service, yielding a <sub>∼</sub>5–10% lift in hit-rate for products with <5 historical interactions [242]. Similar blueprints are emerging in streaming platforms that blend thumbnails, transcripts, and user watch history to build <sub>rich</sub> item sketches for zero-shot retrieval [244]. Future work is exploring <sub>co-training</sub> regimes where the LLM simultaneously solves captioning [59], visual question-answering, and recommendation; this multitask conditioning regularizes the shared space and mitigates over-fitting to any single modality. Knowledge-distillation and quantization pipelines are being introduced to compress the fused encoders for edge deployment, aligning multimodal personalization with latency and privacy constraints.

<sub>Meta-Learning</sub> <sub>for</sub> <sub>Fast</sub> <sub>Adaptation</sub> <sub>–</sub> Meta-learning provides a framework for enabling rapid personalization by training models to adapt quickly to new users or items using limited data [223]. When combined with LLMs, meta-learning techniques such as Model-Agnostic Meta-Learning (MAML) [44] allow systems to fine-tune user- or item-specific representations via a small number of gradient updates(see Figure 4. For a new user task $\mathcal { T } _ { u }$ , the model parameters are adapted as follows:

$$
\theta^ {*} = \theta - \alpha \nabla_ {\theta} \mathcal {L} _ {\mathcal {T} _ {u}} (f _ {\theta})
$$

, where ?? are the shared model parameters and ?? is the learning rate. This enables the system to personalize quickly without retraining from scratch. Recent works such as MeLU [99] and Meta-LLMRec [124] demonstrate how few-shot fine-tuning on top of LLM-derived embeddings can deliver strong performance in cold-start settings, achieving meaningful generalization with minimal supervision. These methods also support continual learning across user cohorts, enabling fast model updates without overfitting or catastrophic forgetting, and are particularly well-suited for dynamic environments like e-commerce or content streaming platforms [57].

![](images/c61bdc944d0db5b0b0dcade5ee988319e945da17a118ea28d607999974ad9907.jpg)

![](images/4e09abdd9365ee0ab0ea4065cd88d7a74a4ac780e62ee1a6a2e3a2c2a477d71a.jpg)

![](images/47a37ff2c12379a0fc8035218d918a4f70b493748f6e31622f7c79b8e5fd8c81.jpg)

![](images/212be28223e5d5afe1d622791646aa966e9a350f763fd10dac9ef6db9460457a.jpg)  
Fig. 4. The image compares MAML-based few-shot adaptation (left) to standard fine-tuning without MAML (right) for a sine wave regression task. MAML generalizes well, even in regions without data, by capturing the underlying periodic structure. In contrast, the pretrained model struggles to adapt from few examples, failing to extrapolate due to conflicting gradients from pretraining [45]

<sub>Cross-Domain</sub> <sub>Transfer</sub> <sub>via</sub> <sub>Language</sub> <sub>–</sub> LLMs pretrained on diverse and heterogeneous corpora can facilitate cross-domain recommendation by leveraging their semantic understanding to bridge disparate user-item interaction spaces [131, 216, 218, 251]. In scenarios where domains ${ \mathcal { D } } _ { A }$ and $\mathcal { D } _ { B }$ have minimal or no overlapping users or items, traditional collaborative filtering fails due to a lack of common signals [284]. However, LLMs can align these domains by grounding recommendations in natural language semantics shared across domains. Formally, user preferences learned from ${ \mathcal { D } } _ { A }$ can be transferred to items in $\mathcal { D } _ { B }$ by:

$$
P _ {\mathcal {D} _ {B}} (i \mid x _ {u}) \approx \mathrm{LLM} (x _ {u} ^ {\mathcal {D} _ {A}}, x _ {i} ^ {\mathcal {D} _ {B}})
$$

This enables zero-shot generalization to new item taxonomies or verticals, using only text, tags, or descriptions [183]. For instance, a user who frequently interacts with technical blog posts (in $\mathcal { D } _ { A } )$ can be matched with programming tutorials or job listings (in $\mathcal { D } _ { B } )$ , purely through semantic alignment.

Recent approaches such as PromptRec and LLMRec show that this strategy improves recommendation relevance in cross-modal and multilingual setups. Additionally, systems like CrossAligner [54] use contrastive fine-tuning to align embeddings across domains, while [259] demonstrate strong performance on cold-start item transfer using instruction-following LLMs. This line of work opens avenues for applying pretraining-era language representations to cross-domain personalization at scale, eliminating the need for costly alignment mappings or dual-domain retraining.

![](images/bb4a577bdf6594d1024e6eb38a8a4a111ffe46b92c71084b70b585bf6963ebcc.jpg)  
Fig. 5. Overview of the LLM4CDSR framework for Cross-Domain Sequential Recommendation. The architecture first constructs hierarchical user profiles by partitioning user history and generating summaries using LLMs. A tri-thread framework integrates user behavior across source and target domains through self-atention layers. An adapter connects local embeddings with a global LLM-based representation to enable unified personalization across domains. [129]

<sub>4.1.2</sub> <sub>Data</sub> <sub>Sparsity.</sub> In large-scale recommender systems, the user-item interaction matrix $R \in$ $\mathbb { R } ^ { | U | \times | I | }$ is predominantly sparse, with observed interactions constituting less than 0.1% of the total possible interactions. The sparsity ratio is quantified as:

$$
\text { Sparsity } = 1 - \frac {\| \mathcal {R} _ {\mathrm{obs}} \| _ {0}}{| U | \cdot | I |}
$$

where $\mathcal { R } _ { \mathrm { o b s } }$ denotes the set of observed interactions. This high level of sparsity hampers the performance of collaborative filtering techniques, which rely on suficient interaction data to model user preferences efectively.

Conventional methods to mitigate data sparsity include matrix factorization techniques such as Singular Value Decomposition (SVD) [88] and Non-negative Matrix Factorization (NMF) [96], as well as hybrid models that incorporate side information [1, 149]. While these approaches can alleviate sparsity to some extent, they often struggle with scalability and may not capture complex user-item relationships, especially in scenarios with extremely sparse data [215]. Let’s discuss how LLMs can solve the data sparsity issue in recommender systems.

<sub>Text-Driven</sub> <sub>Generalization</sub> <sub>–</sub> Pretrained LLMs encode extensive linguistic and factual knowledge from large-scale corpora, enabling semantic reasoning over textual representations of users and items. Rather than relying solely on historical interaction signals (e.g., clicks, views, ratings), these models infer user-item relevance by computing semantic alignment between natural language metadata, leveraging contextual understanding rather than frequency-based heuristics.

This approach is particularly efective in <sub>sparse</sub> <sub>settings</sub>, where traditional collaborative filtering methods struggle due to the lack of suficient interaction history. Given item metadata $x _ { i }$ (e.g., title, abstract, tags) and user profile $x _ { u }$ (e.g., occupation, interests, or past behaviors), the model constructs a prompt and estimates a relevance score as:

$$
\hat {r} _ {u i} = \text { LLM } (" \text { User   profile: }" + x _ {u} +" \text { Item: }" + x _ {i}),
$$

By framing the recommendation problem as a zero-shot or few-shot prediction task, this formulation enables generalization to previously unseen user-item pairs $\left. u , i \right.$ that are entirely missing from training data. The LLM infers relevance based on semantic similarity, textual context, and its pretrained knowledge.

For example, [266]and Hwang and Lee [70] investigate prompt-based LLM scoring for sparse recommendation proposes , a generative framework that predicts user preferences using descriptive prompts. Similarly, GENREC [190] extends this idea to fully generative recommender systems that synthesize user-item relevance in the absence of interaction logs.

Semantic Matching via Embedding Generation - <sup>LLMs</sup> <sup>can</sup> <sup>be</sup> <sup>employed</sup> <sup>to</sup> <sup>generate</sup> <sup>high-</sup> dimensional, semantically meaningful embeddings from textual inputs, facilitating efective useritem matching in the absence of interaction data. In this paradigm, LLMs act as encoders that map user profiles and item metadata into a shared latent space, enabling recommendations through embedding similarity. For previously unseen users or items, the relevance score is computed as:

$$
\hat {p} _ {u} = f _ {u} (x _ {u}), \quad \hat {q} _ {i} = f _ {i} (x _ {i}), \quad \hat {r} _ {u i} = \hat {p} _ {u} ^ {\top} \hat {q} _ {i},
$$

where $f _ { u }$ and $f _ { i }$ are LLM-based encoders applied to the user profile $x _ { u }$ and item description $x _ { i }$ , respectively. These encoders can leverage instruction tuning, adapter modules, or lightweight prompt-based techniques to incorporate domain-specific context during representation learning.

This semantic matching framework has demonstrated strong performance in cold-start and zero-shot settings [222] uses LLMs to encode textual features for new users and items, enabling retrieval via embedding similarity [33], this further incorporates structured knowledge graph information via prompt tuning to improve recommendation accuracy.

<sub>4.1.3</sub> <sub>Noisy</sub> <sub>Implicit</sub> <sub>Feedback.</sub> Modern recommender systems predominantly rely on implicit feedback due to the scarcity of explicit labels. Let $o _ { u i } \in O$ denote an observed implicit interaction between user ?? and item ?? (e.g., click, impression, dwell), and $r _ { u i } ^ { * } \in \{ 0 , 1 \}$ be the unobserved ground-truth relevance. In theory, one might assume:

$$
\mathbb {P} (o _ {u i} \mid r _ {u i} ^ {*}) = \delta (r _ {u i} ^ {*}),
$$

where $\delta$ denotes a deterministic mapping. However, in practice, this assumption fails due to multiple sources of stochasticity and bias in user behavior. The actual observed feedback often satisfies:

$$
\mathbb {P} (o _ {u i} = 1 \mid r _ {u i} ^ {*} = 1) <   1, \quad \mathbb {P} (o _ {u i} = 1 \mid r _ {u i} ^ {*} = 0) > 0.
$$

These deviations arise from position bias, presentation bias, and selection bias, which skew click-through data toward superficial engagement signals [106]. This noise propagates into learning algorithms, especially when optimizing binary cross-entropy loss:

$$
\mathcal {L} _ {\mathrm{BCE}} = - \sum_ {(u, i) \in O} \left[ o _ {u i} \log \hat {r} _ {u i} + (1 - o _ {u i}) \log (1 - \hat {r} _ {u i}) \right],
$$

where $\hat { r } _ { u i }$ denotes the predicted relevance. Correcting such noisy supervision without access to counterfactual data remains a central challenge.

LLMs pretrained on large-scale human-authored corpora encode rich priors about user intent, preference, and satisfaction—grounded in linguistic patterns and world knowledge [10]. These priors can be leveraged to mitigate the impact of noisy implicit feedback by smoothing binary interaction labels (e.g., clicks or skips) into soft, continuous scores that better reflect underlying user preferences. Specifically, given item content $x _ { i }$ and user context $c _ { u }$ (e.g., prior interactions, demographics, or interest descriptors), an LLM can estimate a denoised relevance score as:

$$
\tilde {r} _ {u i} = \mathrm{sigmoid} (\mathrm{LLM} (x _ {i}, c _ {u})),
$$

where the LLM is prompted to infer how well the item matches the user’s intent. The output $\tilde { r } _ { u i } \in ( 0 , 1 )$ can be interpreted as a soft label and used to replace or augment the original binary signal $o _ { u i }$ in the loss function during training. This reformulation introduces robustness by attenuating spurious clicks or missed positives, efectively serving as a learned reweighting scheme.

This denoising strategy has been applied in systems, where LLMs provide feedback-aware relevance estimates for training ranking models. Other works like PromptTuning4Rec [112] and LightRec [120] explore LLM-driven soft label generation as a mechanism to denoise interaction matrices under extreme sparsity. The approach aligns with broader trends in label refinement [97, 201] and weak supervision for recommender systems. The next sub-section talks about how LLMs can help in alleviating noisy implicit feedback in recommender systems.

Feedback Interpretation with Contextual Prompts – <sup>LLMs</sup> <sup>can</sup> <sup>be</sup> <sup>used</sup> <sup>to</sup> <sup>interpret</sup> <sup>user</sup> interactions by incorporating behavioral context into prompts—such as item position, dwell time, or scroll depth—to assess the reliability or intent behind an observed action. For instance, given a prompt like:

User clicked item $x _ { i }$ at position 8 after scrolling for 2 seconds. Was this click intentional?

the LLM returns a binary or scalar prediction $\hat { y } _ { u i } \in \{ 0 , 1 \}$ (or a confidence score), which can then be used for downstream tasks such as sample filtering, importance weighting, or bias correction [92]. This method enables context-aware re-labeling of interactions and helps distinguish between genuine interest and behavior driven by interface bias (e.g., accidental clicks on top-ranked items or skip-throughs). It builds on the idea that implicit feedback is inherently noisy and requires situational reasoning to infer its semantic relevance [250].

Recent implementations of this strategy where user behavior traces are used to condition prompts that refine training labels; behavior-aware reasoning in SAM [257], which incorporates dwell and revisit signals into expert routing; and click attribution models that interpret interactions using rich context.Generative LLMs can simulate unseen feedback under counterfactual scenarios. For example:

If item $x _ { i }$ were shown first instead of last, would the user have clicked? This models counterfactual relevance:

$$
\hat {r} _ {u i} ^ {\mathrm{cf}} = \operatorname{LLM} (\text { Counterfactual   Prompt }),
$$

providing a proxy for $\mathbb { P } ( r _ { u i } ^ { * } \mid \mathrm { d o } ( x _ { i } ^ { \mathrm { p o s } } = 1 ) )$ . LLMs can classify behavior sequences using natural instructions using prompts. The resulting label $\hat { y } _ { u i }$ can be used for fine-tuning or distillation. This approach has been adopted in multi-objective recsys systems like InstRec [228] and human-feedback alignment setups. LLMs can simulate realistic interaction sequences for pretraining purposes. For example:

User browsed 5 items. Skipped $x _ { i }$ after reading the summary. Clicked $x _ { j }$ after 3 seconds.

Such pseudo-sessions enable robust pretraining across noisy behavioral regimes. This has been used in SAM [257], LLM4RecSim [227], and language-driven session modeling [243]. LLMs can generate explanations to help identify noisy or biased samples. These explanations can be post-processed into logic rules for filtering or label smoothing. Explanation-enhanced supervision has been studied in GPT4Rec [277], dialog-based models, and instruction-aligned filtering setups [49].

![](images/bc0316a91db5d02e873dc312488129f958f75235949ade920f24412e5422832b.jpg)  
Fig. 6. Illustration of Temporal Drift in User Preferences. The figure shows how user preferences evolve over time—from the past to the present and into the future. As the user’s interests shift (e.g., from sports to music to fashion), the recommendation system must model this drift by adapting the user’s preference representation $p _ { u } ^ { ( t ) }$ as a function of past preferences $p _ { u } ^ { t - 1 }$ , elapsed time $\Delta t ,$ and contextual features $x _ { u } ^ { ( t ) }$ . Capturing this dynamic behavior is crucial for maintaining long-term recommendation relevance.

<sub>4.1.4</sub> <sub>Temporal</sub> <sub>Drift.</sub> User preferences are inherently dynamic. Static user embeddings, often learned from aggregate histories, fail to capture shifts in taste caused by evolving life contexts, seasonality, or trending content. A time-aware user representation can be modeled as:

$$
\mathbf {p} _ {u} ^ {(t)} = f (\mathbf {p} _ {u} ^ {(t - 1)}, \Delta t, \mathbf {x} _ {u} ^ {(t)})
$$

where $\mathbf { p } _ { u } ^ { ( t ) }$ is the user embedding at time ??, <sub>Δ</sub>?? denotes the time elapsed since the last interaction, and $\mathbf { x } _ { u } ^ { ( t ) }$ includes recent interaction context. Here is how LLMs can help in addressing temporal drift.

<sub>Temporal</sub> <sub>Adaptation</sub> <sub>with</sub> <sub>LLMs</sub> Recent advances in large language models (LLMs) enable dynamic user modeling via textual prompts that encode temporal context [270]. Rather than retraining models to reflect evolving preferences, LLMs support <sub>on-the-fly</sub> <sub>personalization</sub> by accepting expressive, context-aware prompts [95]. These prompts are designed to capture temporal signals such as recency, session history, preference shifts, and explanatory cues.

For example, recent user behavior can be embedded into prompts that guide the LLM in generating updated user representations. This mechanism has been explored in PromptRec, LMRec, and genre-adaptive recommendation models [15]. Similarly, attention over long-term and short-term preferences can be introduced by structuring prompts that separately convey enduring interests and recent actions. LLMs can also be prompted to produce interpretable justifications based on recency, making them suitable for explainable recommendation settings.

In session-aware contexts, prompts constructed from short-term interaction sequences (e.g., clicks, watches, searches) enable the model to simulate user intent in real time and generate slates accordingly. Additionally, instruction-tuned LLMs can perform few-shot drift adaptation by observing behavioral transitions across users and generalizing to new preference shifts without explicit fine-tuning. Noisy or fragmented histories can also be abstracted into stable, high-level summaries through summarization-style prompts.

These strategies are systematically summarized in Table 2, which outlines the types of prompts used, their intended purposes, and representative systems that have adopted them.

<table><tr><td>Prompt Example</td><td>Purpose</td></tr><tr><td>User watched: [Horror A], [Horror B], [Horror C]. Recommend based on their recent interests.</td><td>Refresh user representation based on recent behavior</td></tr><tr><td>Long-term favorites: Sci-Fi, Documentaries. Recent watches: Romantic comedies.</td><td>Temporal attention over long-term and short-term interests</td></tr><tr><td>Because you recently watched romantic comedies, we&#x27;re recommending this title.</td><td>Generate interpretable, recency-aware explanations</td></tr><tr><td>Session: clicked [Horror A], watched [Horror B], searched &quot;ghost movies&quot;</td><td>Model short-term session context for slate generation</td></tr><tr><td>User 1: Horror → Comedy.User 2: Thriller → Animation. Target: Romance → ?</td><td>Enable few-shot drift generalization across users</td></tr><tr><td>Summarize recent user behavior and extract long-term interests.</td><td>Smooth noisy sequences into high-level intent</td></tr></table>

Table 2. Prompt-Based Techniques for Temporal Adaptation in LLM-Based Recommenders

<sub>Structural</sub> <sub>and</sub> <sub>Hybrid</sub> <sub>LLM</sub> <sub>Integration</sub> LLMs can be integrated into recommendation pipelines through structural means that support temporal adaptation [141]. One such approach involves using LLMs to parameterize updates to the user embedding. For example, recent behavioral context can be encoded by the LLM and merged with historical representations via a learned transformation:

$$
\mathbf {p} _ {u} ^ {(t)} = \operatorname{MLP} \left(\mathbf {p} _ {u} ^ {(t - 1)} \| \operatorname{LLM} \left(\mathbf {x} _ {u} ^ {(t)}\right)\right)
$$

This enables fine-grained updates to latent factors without explicit prompting during inference. In another variant, LLMs augment sequential recommendation models by enriching item represen tations or positional embeddings within transformer-based architectures [287]. Here, interaction sequences are processed as:

$$
\mathbf {h} _ {t} = \text { Transformer } ([ \mathbf {x} _ {1}, \dots , \mathsf {L L M} (\mathbf {x} _ {t}) ])
$$

which allows the model to incorporate both learned behavior encodings and contextual language insights. Retrieval-augmented approaches also benefit from LLM integration. By conditioning retrieval queries on temporally relevant cues, LLMs dynamically populate the candidate pool based on evolving user contexts [58]. LLMs also act as soft-labeling supervisors in distillation frameworks [203]. For instance, in short or noisy sessions, they generate target summaries that guide smaller models to learn smoothed, temporally aligned representations.

<sub>4.1.5</sub> <sub>Multimodal</sub> <sub>Data</sub> <sub>Integration.</sub> Modern recommendation platforms such as Amazon, Pinterest, and Spotify leverage heterogeneous and semantically rich multimodal signals to enhance personalization. These signals include textual descriptions $( x ^ { \mathrm { t e x t } } )$ , visual content $( x ^ { \mathrm { i m g } } )$ , structured metadata $( x ^ { \mathrm { m e t a } } )$ , and user interaction histories or behavioral traces $( x ^ { \mathrm { { b e h a v } } } )$ . To produce a unified representation for an item ??, a common formulation involves modality-specific encoders whose outputs are aggregated to yield the final item embedding:

$$
\mathbf {q} _ {i} = f (x _ {i}) = f _ {\mathrm{text}} (x _ {i} ^ {\mathrm{text}}) + f _ {\mathrm{img}} (x _ {i} ^ {\mathrm{img}}) + f _ {\mathrm{meta}} (x _ {i} ^ {\mathrm{meta}}) + f _ {\mathrm{behav}} (x _ {i} ^ {\mathrm{behav}}),
$$

where each $f .$ is a modality-specific encoder $( \mathrm { e . g . , a }$ transformer for text, a CNN for images, a feedforward network for metadata), and $x _ { i } = \{ x _ { i } ^ { \mathrm { t e x t } } , x _ { i } ^ { \mathrm { i m g } } , x _ { i } ^ { \mathrm { m e t a } } , x _ { i } ^ { \mathrm { b e h a v } } \}$ denotes the full multimodal feature set associated with item ??.

However, this fusion process is complicated by challenges such as modality imbalance—where some inputs $( \mathbf { e . g . }$ , reviews) are informative while others (e.g., short captions) are weak—feature misalignment due to semantic or temporal inconsistencies across modalities, and missing or noisy inputs, particularly in cold-start scenarios where behavioral signals may be absent or unreliable.

These issues limit the efectiveness of conventional fusion methods such as early concatenation or late summation, particularly in sparse or cold-start regimes. The next subsections disccuss the approaches using LLM to solve the multimodal data integration issues.

Modal-Aware Weighting through Attention – Transformer-based LLMs naturally address heterogeneity via <sub>modal-aware</sub> <sub>attention</sub> <sub>mechanisms</sub>, dynamically re-weighting modalities during representation learning [143, 243, 257]. Self-attention computes token-level dependencies both across and within modalities. When structured attributes (e.g., brand, category) are incomplete, the model shifts focus toward unstructured signals such as reviews or captions; conversely, when textual cues are weak, more attention mass is allocated to reliable metadata or visual embeddings. This <sub>soft</sub> <sub>modality</sub> <sub>selection</sub> is realized implicitly, without explicit gating or masking heuristics [14].

Unified Representation through Instruction-Tuned LLMs – <sup>Given</sup> <sup>a</sup> <sup>structured</sup> <sup>prompt</sup> Promp $\mathbf { t } _ { i }$ that serializes all modality features (e.g., title, description, image caption, metadata, and recent user feedback), an instruction-tuned LLM(see Figure 7 can embed this multimodal input using a shared semantic space. The dense item representation is computed as:

![](images/5dac9ba883b7a2400561e59bdfeae96e932d50d58375e4185e69070e8d74a3eb.jpg)  
Fig. 7. An instruction-tuned LLM framework that unifies visual and textual inputs into a shared semantic space. The image encoder extracts visual embeddings, which are fused with textual instructions via a Q-Former module using self-atention and cross-atention. The combined representation is processed by the LLM to generate a response, enabling cross-modal reasoning without separate modality-specific towers. [35]

$$
\mathbf {q} _ {i} = g _ {\mathrm{pool}} \bigl (\operatorname{LLM} (\operatorname{Prompt} _ {i}) \bigr),
$$

where ${ g } _ { \mathrm { p o o l } }$ typically refers to mean pooling over token embeddings or [CLS]-token extraction. Instruction tuning aligns the LLM’s behavior with domain-specific objectives, ensuring that the model respects segment-level distinctions while enabling cross-modal reasoning within a unified encoder. This avoids the need for separate modality-specific towers or handcrafted fusion heuristics.

This paradigm supports scalability, simplifies architecture, and enables zero-shot or few-shot personalization. It has been adopted in UniModalRec [139] for retail recommendation, and UnifiedIO [138] for vision-language tasks for streaming media. Moreover, InstructRecLM demon strates that parameter-eficient instruction-tuned LLMs can achieve competitive performance even in low-resource or cold-start regimes.

<sub>Cross-Modal</sub> <sub>Alignment</sub> <sub>via</sub> <sub>Pretraining</sub> <sub>–</sub> Large-scale pretraining on multimodal corpora (e.g., alt-text–image pairs, metadata–review co-occurrences) enables LLMs to implicitly align semantically related content across modalities [184]. These pretrained models induce a joint latent space where concepts are consistently grounded across diferent input forms [267]. At inference, when certain modalities are unavailable, the model can still generate meaningful representations by conditioning on the observed subset $x _ { i } ^ { \mathrm { o b s } } \subset x _ { i }$

$$
\mathbf {q} _ {i} = g _ {\mathrm{pool}} \big (\mathrm{LLM} (\pi (x _ {i} ^ {\mathrm{obs}})) \big),
$$

where $\pi ( \cdot )$ formats available features into a cross-modal prompt. The model fills gaps by relying on shared linguistic anchors (e.g., a product’s visual properties inferred from its textual reviews or structured tags).

This alignment strategy originated in vision-language models like CLIP [171] and ALIGN [73], and has been adapted for recommendation in PaLI [20], CoCa-2Rec [231], and OmniFM [279], where the model generalizes across image-text-review-metadata domains with minimal supervision.

Multimodal Imputation via Generative Inference – <sup>In</sup> <sup>sparse</sup> <sup>environments,</sup> <sup>generative</sup> <sup>LLMs</sup> can hallucinate plausible approximations for missing modalities based on contextual conditioning.

When inputs such as user reviews or image captions are missing, the model autoregressively generates substitute content from the conditional distribution:

$$
p _ {\theta} \big (x _ {i} ^ {\mathrm{miss}} \mid x _ {i} ^ {\mathrm{obs}} \big) = \prod_ {t = 1} ^ {T} p _ {\theta} (w _ {t} \mid w _ {<   t}, x _ {i} ^ {\mathrm{obs}}),
$$

where $x _ { i } ^ { \mathrm { o b s } }$ includes observed fields such as title and metadata, and $( w _ { 1 } , \ldots , w _ { T } )$ are tokens repre senting the imputed modality (e.g., a visual scene description). This generated text can either be appended to the original prompt or passed through modality-specific encoders, enhancing downstream coverage [81]. This approach enables robust pretraining and fine-tuning in low-resource or noisy-input conditions.

Semantic Fusion via Natural-Language Templates – <sup>To</sup> <sup>unify</sup> <sup>modality</sup> <sup>inputs</sup> <sup>without</sup> custom encoder branches, each modality is embedded into structured natural language using templated segments. For instance:

[TITLE] Red running shoes. [IMAGE] Person running on track. [META] Size

9; lightweight. [REVIEW] Very comfortable.

This string is fed into a standard LLM, which processes the full multimodal context as a single token sequence. Reserved tags (e.g., <sub>[META]</sub>, <sub>[REVIEW]</sub>) act as soft positional anchors, helping self-attention layers model dependencies both within and across modalities.

Unlike traditional late-fusion models that aggregate fixed embeddings, this strategy ofers a fully end-to-end formulation. It is leveraged in CM3 [3], expanded in PromptFusionRec [34], and coupled with retrieval-augmented generation in UnifiedIO, facilitating scalable multimodal reasoning while preserving alignment across modality-specific semantic structures.

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

## 4.4 Privacy, Security, and Regulatory Challenges

As Recommender systems become increasingly integral to digital platforms, they must navigate a complex landscape of privacy concerns, regulatory requirements, and security challenges. En suring user trust and compliance with laws like GDPR and CCPA necessitates the adoption of privacy-preserving techniques and robust data governance frameworks. This section explores these challenges alongside emerging industry practices.

<sub>4.4.1</sub> <sub>User</sub> <sub>Data</sub> <sub>Sensitivity.</sub> Recommender systems rely heavily on sensitive user data—such as browsing behavior, clicks, and purchase history—making privacy a critical concern. Mishandling this information risks legal violations (e.g., GDPR) and erosion of user trust. Traditional safeguards like access control and anonymization are widely adopted, but emerging methods now leverage LLMs to further mitigate privacy risks.

LLMs reduce reliance on raw user logs by operating on abstracted semantic representations or synthetic profiles. Instruction-tuned LLMs enable zero- or few-shot personalization without long-term data retention [118, 262]. Recent systems incorporate federated prompting and local diferential privacy, allowing on-device adaptation without transmitting identifiable data [236]. Synthetic user generation using LLMs has also shown promise in training and evaluation without exposing real user logs [177].

By embedding these techniques into system design, LLM-based recommenders can uphold privacy-by-design principles while maintaining performance.

<sub>4.4.2</sub> <sub>Compliance</sub> <sub>with</sub> <sub>Laws.</sub> Modern privacy laws such as the EU General Data Protection Reg ulation (GDPR), California Consumer Privacy Act (CCPA), and the Digital Markets Act (DMA) impose strict requirements on data usage, including explicit user consent, right to deletion, and data minimization. For example, Spotify reengineered its data pipelines to support fine-grained consent tracking and user-facing data access tools. Similarly, Zalando implemented automated consent enforcement using GDPR-aware architecture [28].

Recent work shows that LLMs can aid in achieving compliance by abstracting personalization workflows away from identifiable user data. LLMs can support ephemeral personalization through prompt-level context without persistent storage [154], generate synthetic user traces for model development [177], and adapt to regulatory rules via constraint-aware instruction tuning [125]. Furthermore, compliance-ready LLM systems incorporate audit logs, data expiration signals, and privacy-preserving inference via secure prompt execution [206]. These approaches reduce reliance on raw user data while supporting transparency and explainability—key tenets of modern regulatory frameworks.

4.4.3 Diferential Privacy and Federated Learning. <sup>Diferential</sup> <sup>Privacy</sup> <sup>(DP)</sup> <sup>and</sup> <sup>Federated</sup> <sup>Learning</sup> (FL) ofer robust privacy guarantees by minimizing user data exposure during model training. In dustry deployments include Google’s FL implementation for Gboard [146] and Apple’s application of DP in telemetry data. In recommender systems, privacy-preserving variants such as federated matrix factorization with DP [179] have demonstrated strong privacy-utility trade-ofs. However, these techniques introduce non-trivial challenges, including increased communication cost, model drift, and the need for specialized infrastructure.

Recent research explores how LLMscan complement or even streamline DP and FL pipelines. Instruction-tuned LLMs can perform user modeling using ephemeral or synthetic input, eliminating the need to aggregate raw user data centrally [154, 177]. Federated prompting—where prompts are generated and refined on-device—enables partial personalization while keeping user context local [236]. Moreover, LLMs with gradient-sanitized fine-tuning objectives [114] and diferentially private retrieval-augmented generation [278] ofer scalable pathways to enforce DP guarantees in language-based recommendation scenarios.

Together, these approaches mitigate the scalability challenges of traditional DP and FL by enabling low-overhead, compliance-ready personalization without sacrificing privacy or model performance.

<sub>4.4.4</sub> <sub>Data</sub> <sub>Access</sub> <sub>and</sub> <sub>Governance.</sub> Balancing innovation with data security requires robust governance frameworks. Access control systems must prevent unauthorized use while enabling rapid experimentation. Companies such as LinkedIn and Airbnb employ platforms with role-based access control (RBAC), automated policy enforcement, and secure sandboxes [126]. These ensure compliance and accountability without obstructing productivity.

<sub>Data</sub> <sub>Minimization</sub> <sub>via</sub> <sub>LLMs</sub>: LLMs can reduce reliance on personally identifiable information (PII) by extracting signals from anonymized data, reviews, or intent prompts, thereby minimizing privacy risks while maintaining personalization:

$$
Q (\text { Rec }) \approx Q _ {\text { LLM }} (\text { Rec } \mid \text { anonymized   data })
$$

Privacy-preserving methods include federated prompt learning with diferential privacy [213], synthetic user simulations, token-level obfuscation, and private fine-tuning [263].

<sub>Instructable</sub> <sub>Privacy</sub> <sub>Filters</sub>: LLMs can be guided through prompts or fine-tuning to avoid sensitive outputs, enforcing constraints such as:

$$
P (\text { output   contains   PII }) <   \delta
$$

where $\delta$ is a privacy threshold. Techniques include privacy regularization, rule-guided decoding, and instruction-driven alignment [18, 38].

<sub>Synthetic</sub> <sub>Data</sub> <sub>Generation</sub>: LLMs can generate synthetic user logs or profiles that mimic real data distributions without exposing individuals. Diferential privacy requires:

$$
\operatorname * {P r} [ \text { LLM   outputs } D _ {\text { synth }} \mid x \in D ] \approx \operatorname * {P r} [ \text { LLM   outputs } D _ {\text { synth }} \mid x \notin D ]
$$

ensuring individual data points do not afect outputs. Metrics like Jensen-Shannon divergence or Wasserstein distance validate distributional similarity. Recent work explores DP-based sequence modeling [238], conditional profile generation, and adversarial simulators [122], enabling privacysafe benchmarking and debugging.

## 5 Limitations & Open Challenges of LLMs in Recommender Systems

<sub>Latency</sub> <sub>and</sub> <sub>Throughput</sub> <sub>Bottlenecks</sub> <sub>–</sub> Autoregressive decoding imposes sequential delays that violate the sub–100 ms SLA common in web-scale ranking. Even with 4-bit weight-only quantization, a 7-B model exceeds 35 ms per query on a single A100 [174]. Token-parallel kernels, KV-cache fusion, and Flash-Attention v3 yield 1.7<sub>×</sub>–2.3<sub>×</sub> speed-ups but degrade under bursts that saturate memory bandwidth [77, 191]. Hierarchical routing—first-stage dense retrieval, second-stage sparse MoE—cuts tail latency by 28 % yet adds routing overhead and fairness concerns [204]. On-device NPUs and speculative decoding shrink <sub>≈</sub>40 ms, but require tight integration with vector search pre-rankers to avoid head-of-line blocking [102, 246].

<sub>Operational</sub> <sub>Cost</sub> <sub>and</sub> <sub>Resource</sub> <sub>Footprint</sub> <sub>–</sub> Inference FLOPs scale roughly linearly with prompt length and quadratically with hidden width; doubling model size can quadruple serving cost and 3× carbon footprint [269]. Sparse MoE routing and LoRA adapters reduce average compute by 60–80 % but necessitate elastic load balancing and sufer from prompt skew [76, 113]. Token-level caching amortizes 15–25 % of compute but introduces cache consistency bugs when prompts embed personalization tokens [56]. Workload-aware autoscaling and serverless accelerators lower idle GPU burn but add cold-start penalties that hurt tail latency [212]. Cloud API mark-ups (<sub>∼</sub> \$0.03 per k-tokens) further inflate total cost of ownership in high-throughput pipelines [181].

<sub>Hallucination</sub> <sub>and</sub> <sub>Semantic</sub> <sub>Misalignment</sub> <sub>–</sub> LLMs can fabricate item attributes, user intents, or reasoning chains, surfacing non-existent products or biased analogies [165, 202]. Retrieval grounding, constrained decoding, and post-generation fact-checkers cut hallucinations by 25–40 % but remain brittle on long-tail, code-mixed, or multilingual content [21, 50, 254]. Fidelity critics trained with human feedback reduce error rate another 12 ms latency per call [193]. Negative prompt augmentation and contrastive rejection sampling further reduce hallucination probability to < 4% on internal ad-catalog tests [130]. Nonetheless, hallucinations that slip through can propagate via feedback loops, degrading long-term engagement metrics [159].

<sub>Prompt</sub> <sub>Sensitivity</sub> <sub>and</sub> <sub>Reproducibility</sub> <sub>–</sub> Microscopic lexical edits (e.g., “recommend” <sub>→</sub> “suggest”) can produce ranking deltas > 10 % NDCG, complicating A/B parity, rollback, and incident triage [151, 186]. Prompt provenance graphs, canary tokens, and contrastive dif testing improve reproducibility but incur 5 GB/day in lineage logs per million requests [285]. RL-based prompt search raises robustness by 18 % but sacrifices transparency and locks systems into brittle reward hacks [161]. Hash-based prompt fingerprints enable fast cache look-ups but fail under adversarial paraphrasing [135]. A standardized robustness benchmark for recsys prompts is still missing [283].

Representation Drift and Embedding Incompatibility – <sup>Periodic</sup> <sup>fine-tunes</sup> <sup>or</sup> <sup>RLHF</sup> <sup>up-</sup> dates shift latent spaces, invalidating historical user vectors and cached scores [147]. Embedding versioning, backward-compatible projection heads, and dual-encoder rehearsal maintain cosine similarity > 0.85 across upgrades, but add 2–3 ms per inference and triple index storage [136, 169]. Continual-learning regularizers slow drift but sacrifice 1–2 % relevance on fresh items [272]. Online distillation into lightweight twin-towers shows promise yet fails for zero-shot entities [86]. Drift alarms based on Wasserstein distance flag latent shifts, but trigger frequent false positives under seasonal trafic variation [240].

<sub>Evaluation</sub> <sub>Gaps</sub> <sub>–</sub> Classic list metrics (NDCG, MAP, Recall@K) ignore semantic fidelity, novelty, and explanation quality central to LLM outputs. Hybrid metrics that blend counterfactual click uplift with LLM-judged coherence scores correlate weakly with real satisfaction (?? < 0.35) [78, 252]. LLM as-judge pipelines reduce annotation cost 10× but inherit biases from the same model family [11, 232]. Causal bandit simulators yield better ofline-online fidelity but require calibrated reward scaling and realism audits [155]. Large-scale human-in-the-loop testing remains cost-prohibitive, averaging \$0.42 per labeled explanation [214].

<sub>Privacy,</sub> <sub>Compliance,</sub> <sub>and</sub> <sub>Safety</sub> <sub>Risks</sub> <sub>–</sub> Generative models leak PII through memorization or adversarial injection [27, 197]. Diferentially private fine-tuning [12, 116], federated prompt learning [65, 213], and secure retrieval-augmented generation [89] lower exposure but add 10–20 % latency. SMPC-backed inference enclaves and SGX isolated prompts narrow leakage channels yet limit model size [79]. New extraction attacks targeting personalization prompts achieve 18 % success even under DP noise [173]. DMA “right-to-explanation” mandates add extra logging and user-facing redaction complexity [289].

<sub>Debugging</sub> <sub>and</sub> <sub>Observability</sub> <sub>Deficits</sub> <sub>–</sub> LLM pipelines lack token-level telemetry; silent regressions can persist until surfaced by downstream KPIs. Prompt lineage, streaming log replay, and token-attribution saliency maps are emerging, yet add 2 GB/day logs per million requests [140]. Black-box causal probes help trace ranking shifts but require expensive interventional trafic [189]. Safety dashboards incorporating toxic-span detection and PII scanners catch 92 % violations ofline, but only 71 % in live trafic due to paraphrase drift [101]. Debugging culture and tooling lags behind deterministic retrievers.

<sub>Architectural</sub> <sub>Integration</sub> <sub>Overhead</sub> <sub>–</sub> Production recommenders rely on vector search and feature-based scoring. Plugging in LLMs requires async rerankers, RAG stacks, prompt stores, and rollback-safe deployment paths, each adding failure modes [237]. Multi-tenant isolation, memory pressure, and GPU scheduling remain open issues, especially in edge and on-device scenarios [84, 87]. Cross-service dependency graphs grow exponentially, complicating SRE ownership boundaries and raising MTTR by 1.4× [152]. End-to-end benchmarks for hybrid (LLM + vector) architectures are still nascent [198].

Tackling these intertwined limitations—spanning latency, cost, hallucination, prompt robustness, drift, evaluation, privacy, observability, and architecture—is essential before LLM-enhanced recom menders can be deployed safely and economically at web scale.

## 6 Conclusion

LLMs represent a transformative shift in the architecture and design philosophy of recommender systems. By enabling contextual reasoning, zero-shot personalization, and multimodal representation learning, LLMs transcend the limitations of traditional matrix factorization, collaborative filtering, and feed-forward neural architectures. Rather than relying solely on historical interaction data and engineered features, LLM-augmented pipelines can synthesize user intent, simulate plausible behaviors, and generate semantically enriched item representations from natural language descriptions, reviews, and metadata. This capability significantly enhances performance in cold-start, long-tail, and rapidly evolving user contexts.

Throughout this paper, we examined how LLMs can be strategically integrated into various stages of industrial recommender pipelines—from candidate generation and reranking to feedback interpretation and synthetic evaluation. Our analysis demonstrated that LLMs not only ofer improvements in semantic fidelity and explainability but also introduce opportunities for conversational and intent-driven recommendation paradigms. Techniques such as retrieval-augmented generation, prompt-based reranking, and hybrid collaborative-semantic scoring models exemplify how LLMs can coexist with traditional recommenders to achieve both robustness and expressivity.

However, this integration is not without its challenges. LLM-based systems pose significant barriers in latency-sensitive environments, where autoregressive decoding and token-based computation are at odds with sub-second serving constraints. Furthermore, issues such as prompt brittleness, hallucinated outputs, representation drift across model versions, and inconsistent personalization responses necessitate new debugging, logging, and evaluation toolchains. These technical hurdles are further complicated by operational constraints, including privacy compliance (e.g., GDPR, CCPA), prompt injection vulnerabilities, and the lack of interpretability guarantees in generative outputs. To realize the full potential of LLMs in recommender systems, future research must address the foundational tension between expressivity and eficiency. Robust prompt design and caching strategies, low-latency inference via distilled or quantized models, and standardized protocols for prompt versioning and auditability will be critical for production readiness. In parallel, new forms of evaluation that combine qualitative user modeling, counterfactual simulation, and LLM-driven assessments are needed to measure real-world efectiveness beyond traditional top-?? metrics.

## References

[1] Gediminas Adomavicius and Alexander Tuzhilin. 2005. Toward the next generation of recommender systems: A survey of the state-of-the-art and possible extensions. <sub>IEEE</sub> <sub>Transactions</sub> <sub>on</sub> <sub>Knowledge</sub> <sub>and</sub> <sub>Data</sub> <sub>Engineering</sub> 17, 6 (2005), 734–749.

[2] Nikhil Agarwal, Sagar Sinha, et al. 2019. Two-Tower Models for Personalized Recommendations at LinkedIn. https://engineering.linkedin.com/blog/2019/announcing-the-two-tower-model--a-large-scale-deep learning-architecture.

[3] Armen Aghajanyan, Bernie Huang, Candace Ross, Vladimir Karpukhin, Hu Xu, Naman Goyal, Dmytro Okhonko, Mandar Joshi, Gargi Ghosh, Mike Lewis, and Luke Zettlemoyer. 2022. CM3: A Causal Masked Multimodal Model of the Internet. arXiv:2201.07520 [cs.CL] https://arxiv.org/abs/2201.07520

[4] Jean-Baptiste Alayrac, Jef Donahue, Paul Luc, Antoine Miech, Serkan Cabi, Thierry Deliot, Arsha Nagrani Dutta, Jacob Menick, Suzana Milani, Vedanuj Misra, et al. 2022. Flamingo: a Visual Language Model for Few-Shot Learning <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2204.14198</sub> (2022). https://arxiv.org/abs/2204.14198

[5] Akari Asai and Hannaneh Hajishirzi. 2020. Learning to retrieve reasoning paths over Wikipedia graph for question answering. In <sub>ACL</sub>.

[6] Azin Ashkan, Branislav Kveton, Zheng Wen, and Brian Eriksson. 2015. Optimal greedy diversity for recommendation. <sup>In</sup> IJCAI<sup>.</sup>

[7] Yuntao Bai, Shaked Kadavath, Saurav Kundu, Amanda Askell, Jackson Kernion, and et al. 2022. Training a helpful and harmless assistant with reinforcement learning from human feedback. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2204.05862</sub> (2022).

[8] Rob H. Bemthuis, Ruben R. Govers, and Amin Asadi. 2024. A CRISP-DM-based Methodology for Assessing Agent-based Simulation Models using Process Mining. arXiv:2404.01114 [cs.MA] https://arxiv.org/abs/2404.01114

[9] Jesus Bobadilla, A. Gutiérrez, F. Ortega, and B. Zhu. 2018. Reliability quality measures for recommender systems. <sub>Information</sub> <sub>Sciences</sub> 442–443 (May 2018), 145–157. doi:10.1016/j.ins.2018.02.030

[10] Anna Bodonhelyi, Efe Bozkir, Shuo Yang, Enkelejda Kasneci, and Gjergji Kasneci. 2024. User Intent Recognition and Satisfaction with Large Language Models: A User Study with ChatGPT. arXiv:2402.02136 [cs.HC] https: //arxiv.org/abs/2402.02136

[11] Nicolas Bougie and Narimasa Watanabe. 2025. SimUSER: Simulating User Behavior with Large Language Models for Recommender System Evaluation. arXiv:2504.12722 [cs.IR] https://arxiv.org/abs/2504.12722

[12] Zhiqi Bu, Yu-Xiang Wang, Sheng Zha, and George Karypis. 2024. Diferentially Private Bias-Term Fine-tuning of Foundation Models. arXiv:2210.00036 [cs.LG] https://arxiv.org/abs/2210.00036

[13] Robin Burke. 2002. Hybrid Recommender Systems: Survey and Experiments. <sub>User</sub> <sub>Modeling</sub> <sub>and</sub> <sub>User-Adapted</sub> <sub>Interaction</sub> 12, 4 (2002), 331–370.

[14] Weilin Cai, Juyong Jiang, Fan Wang, Jing Tang, Sunghun Kim, and Jiayi Huang. 2025. A Survey on Mixture of Experts in Large Language Models. <sub>IEEE</sub> <sub>Transactions</sub> <sub>on</sub> <sub>Knowledge</sub> <sub>and</sub> <sub>Data</sub> <sub>Engineering</sub> (2025), 1–20. doi:10.1109/tkde.2025. 3554028

[15] Wenjuan Chai. 2022. Imaginative Indices and Deceptive Domains: How Netflix’s Categories and Genres Redefine the Long Tail. <sub>Proceedings</sub> <sub>on</sub> <sub>ResearchGate</sub> (2022). https://www.researchgate.net/publication/368786568\_Imaginative\_ Indices\_and\_Deceptive\_Domains\_How\_Netflix%27s\_Categories\_and\_Genres\_Redefine\_the\_Long\_Tail Accessed via ResearchGate.

[16] Szeyi Chan, Shihan Fu, Jiachen Li, Bingsheng Yao, Smit Desai, Mirjana Prpa, and Dakuo Wang. 2024. Human and LLM-Based Voice Assistant Interaction: An Analytical Framework for User Verbal and Nonverbal Behaviors. arXiv:2408.16465 [cs.HC] https://arxiv.org/abs/2408.16465

[17] Minmin Chen, Alex Beutel, Paul Covington, Sagar Jain, Francois Belletti, and Ed Chi. 2019. Top-K of-policy correction for a REINFORCE recommender system. In <sub>WSDM</sub>.

[18] Menglan Chen, Xianghe Pang, Jingjing Dong, WenHao Wang, Yaxin Du, and Siheng Chen. 2025. VLMGuard-R1: Proactive Safety Alignment for VLMs via Reasoning-Driven Prompt Optimization. arXiv:2504.12661 [cs.LG] https://arxiv.org/abs/2504.12661

[19] Sirui Chen, Yuan Wang, Zijing Wen, Zhiyu Li, Changshuo Zhang, Xiao Zhang, Quan Lin, Cheng Zhu, and Jun Xu. 2023. Controllable Multi-Objective Re-ranking with Policy Hypernetworks. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> <sub>29th</sub> <sub>ACM</sub> <sub>SIGKDD</sub> Conference on Knowledge Discovery and Data Mining (KDD ’23)<sup>.</sup> <sup>ACM,</sup> <sup>3855–3864.</sup> <sup>doi:10.1145/3580305.3599796</sup>

[20] Xi Chen, Xiao Wang, Soravit Changpinyo, AJ Piergiovanni, Piotr Padlewski, Daniel Salz, Sebastian Goodman, Adam Grycner, Basil Mustafa, Lucas Beyer, et al. 2022. PaLI: A Jointly-Scaled Multilingual Language–Image Model. <sub>arXiv</sub> preprint arXiv:2209.06794 <sup>(2022).</sup>

[21] Xinlong Chen, Yuanxing Zhang, Qiang Liu, Junfei Wu, Fuzheng Zhang, and Tieniu Tan. 2025. Mixture of Decoding: An Attention-Inspired Adaptive Decoding Strategy to Mitigate Hallucinations in Large Vision-Language Models. arXiv:2505.17061 [cs.CL] https://arxiv.org/abs/2505.17061

[22] Xiong-Hui Chen, Bowei He, Yang Yu, Qingyang Li, Zhiwei Qin, Wenjie Shang, Jieping Ye, and Chen Ma. 2023. Sim2Rec: A Simulator-based Decision-making Approach to Optimize Real-World Long-term User Engagement in Sequential Recommender Systems. (2023). arXiv:2305.04832 [cs.IR] https://arxiv.org/abs/2305.04832

[23] Zhiyu Chen, Jason Choi, Besnik Fetahu, Oleg Rokhlenko, and Shervin Malmasi. 2023. Generate-then-Retrieve: Intent-<sup>Aware</sup> <sup>FAQ</sup> <sup>Retrieval</sup> <sup>in</sup> <sup>Product</sup> <sup>Search.</sup> <sup>In</sup> Proceedings of the 61st Annual Meeting of the Association for Computational <sub>Linguistics</sub> <sub>(Volume</sub> <sub>5:</sub> <sub>Industry</sub> <sub>Track)</sub>, Sunayana Sitaram, Beata Beigman Klebanov, and Jason D Williams (Eds.). Association for Computational Linguistics, Toronto, Canada, 763–771. doi:10.18653/v1/2023.acl-industry.73

[24] Hao Cheng, Arjun Balasubramanian, Thomas Wolf, and Alexander Rush. 2023. Plug-and-Play Language Models: Conditional Text Generation with Modular Transformers. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> <sub>61st</sub> <sub>Annual</sub> <sub>Meeting</sub> <sub>of</sub> <sub>the</sub> <sub>Association</sub> for Computational Linguistics (ACL)<sup>.</sup>

[25] Heng-Tze Cheng et al. 2023. The History of Amazon’s Recommendation Algorithm. https://www.amazon.science/thehistory-of-amazons-recommendation-algorithm.

[26] Heng-Tze Cheng, Levent Koc, Jeremiah Harmsen, Tal Shaked, Tushar Chandra, Hrishi Aradhye, Glen Anderson, Greg Corrado, Wei Chai, Mustafa Ispir, et al. 2016. Wide & Deep Learning for Recommender Systems. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> 1st Workshop on Deep Learning for Recommender Systems (DLRS)<sup>.</sup> <sup>7–10.</sup>

[27] M. Chizari. 2025. Data Privacy Regulations (GDPR, CCPA) in Data Science Projects. https://www.linkedin.com/pulse data-privacy-regulations-gdpr-ccpa-science-projects-mohamed-chizari-ibobe.

[28] Nazanin Chizari and Jonas Müller. 2025. Engineering GDPR-Compliant Consent Enforcement at Scale: A Case Study <sup>at</sup> <sup>Zalando.</sup> Journal of Data Protection and Privacy Engineering <sup>8,</sup> <sup>1</sup> <sup>(2025),</sup> <sup>33–47.</sup>

[29] Paul F Christiano, Jan Leike, Tom Brown, Miljan Martic, Shane Legg, and Dario Amodei. 2017. Deep reinforcement <sup>learning</sup> <sup>from</sup> <sup>human</sup> <sup>preferences.</sup> <sup>In</sup> Advances in Neural Information Processing Systems (NeurIPS)<sup>.</sup>

[30] Hyung Won Chung, Le Hou, Shayne Longpre, Barret Zoph, Yi Tay, William Fedus, Xuezhi Wang, Mostafa Dehghani, Siddhartha Brahma, Albert Webson, et al. 2022. Scaling Instruction-Finetuned Language Models. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2210.11416</sub> (2022). https://arxiv.org/abs/2210.11416

[31] Matej Cief, Branislav Kveton, and Michal Kompan. 2024. Cross-Validated Of-Policy Evaluation. arXiv:2405.15332 [cs.LG] https://arxiv.org/abs/2405.15332

[32] Paul Covington, Jay Adams, and Emre Sargin. 2016. Deep neural networks for YouTube recommendations. In Proceedings of the 10th ACM conference on recommender systems<sup>.</sup> <sup>ACM,</sup> <sup>191–198.</sup>

[33] Yuanning Cui, Zequn Sun, and Wei Hu. 2024. A Prompt-Based Knowledge Graph Foundation Model for Universa In-Context Reasoning. arXiv:2410.12288 [cs.AI] https://arxiv.org/abs/2410.12288

[34] Ruiting Dai, Yuqiao Tan, Lisi Mo, Tao He, Ke Qin, and Shuang Liang. 2024. MuAP: Multi-step Adaptive Prompt Learning for Vision-Language Model with Missing Modality. arXiv:2409.04693 [cs.AI] https://arxiv.org/abs/2409.04693

[35] Wenliang Dai, Junnan Li, Dongxu Li, Anthony Meng Huat Tiong, Junqi Zhao, Weisheng Wang, Boyang Li, Pascale Fung, and Steven Hoi. 2023. InstructBLIP: Towards General-purpose Vision-Language Models with Instruction Tuning. arXiv:2305.06500 [cs.CV] https://arxiv.org/abs/2305.06500

[36] Xinyu Dai, Chen Xu, Pan Zhang, Yufei Ge, Xiang Li, and Zhoujun Lin. 2023. PromptRec: Towards Personalized <sup>Prompt</sup> <sup>Tuning</sup> <sup>for</sup> <sup>Recommendation.</sup> <sup>In</sup> Proceedings of the 46th International ACM SIGIR Conference on Research and <sub>Development</sub> <sub>in</sub> <sub>Information</sub> <sub>Retrieval</sub>. ACM, 2244–2249. doi:10.1145/3539618.3591942

[37] Jialin Dong, Bahare Fatemi, Bryan Perozzi, Lin F. Yang, and Anton Tsitsulin. 2024. Don’t Forget to Connect! Improving RAG with Graph-based Reranking. arXiv:2405.18414 [cs.CL] https://arxiv.org/abs/2405.18414

[38] Yi Dong, Ronghui Mu, Yanghao Zhang, Siqi Sun, Tianle Zhang, Changshun Wu, Gaojie Jin, Yi Qi, Jinwei Hu, Jie Meng, Saddek Bensalem, and Xiaowei Huang. 2024. Safeguarding Large Language Models: A Survey. arXiv:2406.02622 [cs.CR] https://arxiv.org/abs/2406.02622

[39] Nan Du, Yanping Huang, Andrew M Dai, Simon Tong, Dmitry Lepikhin, Yuanzhong Xu, Maxim Krikun, Yanqi Zhou, Adams Wei Yu, Orhan Firat, Barret Zoph, Liam Fedus, Maarten Bosma, Zongwei Zhou, Tao Wang, Yu Emma Wang, Kellie Webster, Marie Pellat, Kevin Robinson, Kathleen Chen, Dai Zhuyun, Lukasz Kaiser, Zhifeng Zhang, Tao Yu, Jason Wei, Ji Li, Kathy Meier-Hellstern, Yonghui Yu, Zhifeng Wu, Zhifeng Chen, Sneha Kudugunta, and Quoc V Le. 2022. GLaM: Eficient Scaling of Language Models with Mixture-of-Experts. In <sub>International</sub> <sub>Conference</sub> <sub>on</sub> <sub>Machine</sub> <sub>Learning</sub>. PMLR, 5547–5569.

[40] Wenqi Fan, Yujuan Ding, Liangbo Ning, Shijie Wang, Hengyun Li, Dawei Yin, Tat-Seng Chua, and Qing Li. 2024. A Survey on RAG Meeting LLMs: Towards Retrieval-Augmented Large Language Models. arXiv:2405.06211 [cs.CL]

https://arxiv.org/abs/2405.06211

[41] Siamak Farshidi, Kiyan Rezaee, Sara Mazaheri, Amir Hossein Rahimi, Ali Dadashzadeh, Morteza Ziabakhsh, Sadegh Eskandari, and Slinger Jansen. 2023. Understanding User Intent Modeling for Conversational Recommender Systems: A Systematic Literature Review. arXiv:2308.08496 [cs.IR] https://arxiv.org/abs/2308.08496

[42] William Fedus, Barret Zoph, and Noam Shazeer. 2022. Switch transformers: Scaling to trillion parameter models with simple and eficient sparsity. <sub>Nature</sub> <sub>Communications</sub> 13, 1 (2022), 1–12

[43] Md Meftahul Ferdaus, Mahdi Abdelguerfi, Elias Ioup, Kendall N. Niles, Ken Pathak, and Steven Sloan. 2024. Towards Trustworthy AI: A Review of Ethical and Robust Large Language Models. arXiv:2407.13934 [cs.CY] https://arxiv.org abs/2407.13934

[44] Chelsea Finn, Pieter Abbeel, and Sergey Levine. 2017. Model-Agnostic Meta-Learning for Fast Adaptation of <sup>Deep</sup> <sup>Networks.</sup> <sup>In</sup> Proceedings of the 34th International Conference on Machine Learning (ICML)<sup>.</sup> <sup>PMLR,</sup> <sup>1126–1135.</sup> https://proceedings.mlr.press/v70/finn17a.html

[45] Chelsea Finn, Pieter Abbeel, and Sergey Levine. 2017. Model-Agnostic Meta-Learning for Fast Adaptation of Deep Networks. arXiv:1703.03400 [cs.LG] https://arxiv.org/abs/1703.03400

[46] Vincent Freiberger, Arthur Fleig, and Erik Buchmann. 2025. PRISMe: A Novel LLM-Powered Tool for Interactive Privacy Policy Assessment. arXiv:2501.16033 [cs.HC] https://arxiv.org/abs/2501.16033

[47] Jingtong Gao, Bo Chen, Weiwen Liu, Xiangyang Li, Yichao Wang, Wanyu Wang, Huifeng Guo, Ruiming Tang, and Xiangyu Zhao. 2025. LLM4Rerank: LLM-based Auto-Reranking Framework for Recommendations. arXiv:2406.12433 [cs.IR] https://arxiv.org/abs/2406.12433

[48] Ruicheng Gao, Yifan Wang, Weijie Liu, et al. 2021. RLLMRec: A reinforcement learning framework for LLM-based recommendations. In <sub>RecSys</sub>.

[49] Yang Gao, Shuofei Ji, Qingyun Ye, Ruoxu Zhang, Xiaocheng Yang, Jindong Li, Zhicong Liu, Junchi Tang, Maosong Sun, et al. 2023. LLM-KG: A Survey of Large Language Models for Knowledge Graphs. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2309.00615</sub> (2023). https://arxiv.org/abs/2309.00615

[50] Yunfan Gao, Yun Xiong, Xinyu Gao, Kangxiang Jia, Jinliu Pan, Yuxi Bi, Yi Dai, Jiawei Sun, Meng Wang, and Haofen Wang. 2024. Retrieval-Augmented Generation for Large Language Models: A Survey. arXiv:2312.10997 [cs.CL] https://arxiv.org/abs/2312.10997

[51] Aurélien Gilotte, Clément Calauzènes, Thibaut Nedelec, and Alexandre Abraham. 2018. Ofline A/B testing for <sup>recommender</sup> <sup>systems.</sup> <sup>In</sup> Proceedings of the 24th ACM SIGKDD International Conference on Knowledge Discovery & <sub>Data</sub> <sub>Mining</sub>. ACM, 232–241.

[52] Carlos A Gomez-Uribe et al. 2022. Recommender system at Netflix: Research and production lessons. <sub>arXiv</sub> <sub>preprint</sub> arXiv:2211.09135 <sup>(2022).</sup>

[53] Carlos A. Gomez-Uribe and Neil Hunt. 2021. The Netflix Recommender System: Algorithms, Business Value, and <sup>Innovation.</sup> ACM Transactions on Management Information Systems (TMIS) <sup>6,</sup> <sup>4</sup> <sup>(2021),</sup> <sup>1–19.</sup> <sup>doi:10.1145/2843948</sup>

[54] Anna Gritta, Isabella Iacobacci, et al. 2022. CrossAligner: Learning Language-Agnostic Task Representations for Zero-Shot Transfer. <sub>Findings</sub> <sub>of</sub> <sub>ACL</sub> (2022).

[55] Huifeng Guo, Ruiming Tang, Yunming Ye, Zhenguo Li, and Xiuqiang He. 2017. DeepFM: A Factorization-Machine <sup>based</sup> <sup>Neural</sup> <sup>Network</sup> <sup>for</sup> <sup>CTR</sup> <sup>Prediction.</sup> <sup>In</sup> Proceedings of the 26th International Joint Conference on Artificial Intelligence (IJCAI)<sup>.</sup> <sup>1725–1731.</sup>

[56] Yifan Guo, Lina Zhang, and Peter Warden. 2025. L-Cache: Token-Level Caching with Consistency Guarantees for Personalized Prompt Serving. <sub>Transactions</sub> <sub>on</sub> <sub>Large-Scale</sub> <sub>Machine</sub> <sub>Learning</sub> <sub>Systems</sub> 2, 1 (2025), 67–85. doi:10.48550/ arXiv.2503.06789

[57] Parisa Hamedi, Roozbeh Razavi-Far, and Ehsan Hallaji. 2025. Federated Continual Learning: Concepts, Challenges, and Solutions. arXiv:2502.07059 [cs.LG] https://arxiv.org/abs/2502.07059

[58] Donghee Han, Hwanjun Song, and Mun Yong Yi. 2025. Rethinking LLM-Based Recommendations: A Query Generation Based, Training-Free Approach. arXiv:2504.11889 [cs.IR] https://arxiv.org/abs/2504.11889

[59] Shibo Hao, Sainbayar Sukhbaatar, DiJia Su, Xian Li, Zhiting Hu, Jason Weston, and Yuandong Tian. 2024. Training Large Language Models to Reason in a Continuous Latent Space. arXiv:2412.06769 [cs.CL] https://arxiv.org/abs/2412.06769 [60] Taher H Haveliwala. 2002. Topic-sensitive PageRank. <sub>WWW</sub> (2002).

[61] Xiangnan He, Kuan Deng, Xiang Wang, Yan Li, Yongdong Zhang, and Meng Wang. 2020. LightGCN: Simplifying and Powering Graph Convolution Network for Recommendation. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> <sub>43rd</sub> <sub>International</sub> <sub>ACM</sub> <sub>SIGIR</sub> Conference on Research and Development in Information Retrieval<sup>.</sup> <sup>ACM,</sup> <sup>639–648.</sup>

[62] Xiangnan He, Lizi Liao, Hanwang Zhang, Liqiang Nie, Xia Hu, and Tat-Seng Chua. 2017. Neural Collaborative Filtering. arXiv:1708.05031 [cs.IR] https://arxiv.org/abs/1708.05031

[63] Balázs Hidasi, Alexandros Karatzoglou, Linas Baltrunas, and Domonkos Tikk. 2016. Session-based recommendations with recurrent neural networks. In <sub>ICLR</sub>.

[64] Samuel Holt, Max Ruiz Luyten, Antonin Berthon, and Mihaela van der Schaar. 2025. G-Sim: Generative Simulations with Large Language Models and Gradient-Free Calibration. arXiv:2506.09272 [cs.LG] https://arxiv.org/abs/2506.09272

[65] Shihao Hou, Xinyi Shang, Shreyank N Gowda, Yang Lu, Chao Wu, Yan Yan, and Hanzi Wang. 2025. CAPT: Class Aware Prompt Tuning for Federated Long-Tailed Learning with Vision-Language Model. arXiv:2503.06993 [cs.LG] https://arxiv.org/abs/2503.06993

[66] Neil Houlsby, Andrei Giurgiu, Stanislaw Jastrzebski, Bruna Morrone, Quentin de Laroussilhe, Andrea Gesmundo, Mohammad Attariyan, and Sylvain Gelly. 2019. Parameter-Eficient Transfer Learning for NLP. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> 36th International Conference on Machine Learning (ICML)<sup>,</sup> <sup>Vol.</sup> <sup>97.</sup> <sup>PMLR,</sup> <sup>2790–2799.</sup>

[67] Edward Hu, Yelong Shen, Phil Wallis, et al. 2021. LoRA: Low-Rank Adaptation of Large Language Models. arXiv:2106.09685 [cs.LG]

[68] Yizheng Huang and Jimmy Huang. 2024. A Survey on Retrieval-Augmented Text Generation for Large Language Models. arXiv:2404.10981 [cs.IR] https://arxiv.org/abs/2404.1098

[69] Bernd Huber, Ghazal Fazelnia, Andreas Damianou, Sebastian Peleato, Max Lefarov, Praveen Ravichandran, Marco De Nadai, Mounia Lalmas-Roellke, and Paul N. Bennett. 2025. Embedding-to-Prefix: Parameter-Eficient Personalization for Pre-Trained Large Language Models. arXiv:2505.17051 [cs.CL] https://arxiv.org/abs/2505.17051

[70] Seonjin Hwang and Younghoon Lee. 2024. Prompt2Rec : Prompt based user and item Re-characterizing method for Recommendation. https://openreview.net/forum?id=dNMsieEiAc

[71] Herve Jegou, Matthijs Douze, and Cordelia Schmid. 2011. Product quantization for nearest neighbor search. In <sub>IEEE</sub> TPAMI<sup>.</sup>

[72] Olivier Jeunen and Ben London. 2023. Ofline Recommender System Evaluation under Unobserved Confounding. arXiv:2309.04222 [cs.LG] https://arxiv.org/abs/2309.04222

[73] Chuang Jia, Yang Yang, Linyi Xia, Peizhao Chen, Zihang Parekh, Quoc V. Pham, Minh Le, Soheil Topal, Lei Wang, Danfei Zhuang, et al. 2021. Scaling Up Visual and Vision-Language Representation Learning With Noisy Text <sup>Supervision.</sup> <sup>In</sup> Proceedings of the 38th International Conference on Machine Learning (ICML)<sup>.</sup>

[74] Xun Jiang, Feng Li, Han Zhao, Jiahao Qiu, Jiaying Wang, Jun Shao, Shihao Xu, Shu Zhang, Weiling Chen, Xavier Tang, Yize Chen, Mengyue Wu, Weizhi Ma, Mengdi Wang, and Tianqiao Chen. 2025. Long Term Memory: The Foundation of AI Self-Evolution. arXiv:2410.15665 [cs.AI] https://arxiv.org/abs/2410.15665

[75] Yuezihan Jiang, Gaode Chen, Wenhan Zhang, Jingchi Wang, Yinjie Jiang, Qi Zhang, Jingjian Lin, Peng Jiang, and Kaigui Bian. 2024. Prompt Tuning for Item Cold-start Recommendation. arXiv:2412.18082 [cs.IR] https://arxiv.org abs/2412.18082

[76] Chao Jin, Ziheng Jiang, Zhihao Bai, Zheng Zhong, Juncai Liu, Xiang Li, Ningxin Zheng, Xi Wang, Cong Xie, Q Huang, Wen Heng, Yiyuan Ma, Wenlei Bao, Size Zheng, Yanghua Peng, Haibin Lin, Xuanzhe Liu, Xin Jin, and Xin Liu. 2025. MegaScale-MoE: Large-Scale Communication-Eficient Training of Mixture-of-Experts Models in Production. arXiv:2505.11432 [cs.LG] https://arxiv.org/abs/2505.11432

[77] Dongwon Jo, Jiwon Song, Yulhwa Kim, and Jae-Joon Kim. 2025. FastKV: KV Cache Compression for Fast Long-Context Processing with Token-Selective Propagation. arXiv:2502.01068 [cs.LG] https://arxiv.org/abs/2502.01068

[78] Thorsten Joachims, Adith Swaminathan, and Maarten de Rijke. 2018. Deep Counterfactual Learning from Bandit <sup>Feedback.</sup> <sup>In</sup> Proceedings of the 35th International Conference on Machine Learning (ICML)<sup>.</sup>

[79] Amy Johnson and Tanmay Dey. 2024. Trusted Inference for LLMs with SMPC and SGX. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2402.07999</sub> (2024).

[80] Nitish Joshi, Abulhair Saparov, Yixin Wang, and He He. 2024. LLMs Are Prone to Fallacies in Causal Inference. arXiv:2406.12158 [cs.CL] https://arxiv.org/abs/2406.12158

[81] Sehun Jung and Hyang won Lee. 2025. Learning Generalizable Prompt for CLIP with Class Similarity Knowledge. arXiv:2502.11969 [cs.AI] https://arxiv.org/abs/2502.11969

[82] Hankook Kang, Sinae Hwang, Jooyeon Park, Seung-won Hwang, and Jinho D. Choi. 2023. LLMRec: Benchmarking <sup>Large</sup> <sup>Language</sup> <sup>Models</sup> <sup>on</sup> <sup>Recommendation</sup> <sup>Tasks.</sup> <sup>In</sup> Proceedings of the 29th ACM SIGKDD Conference on Knowledge <sub>Discovery</sub> <sub>and</sub> <sub>Data</sub> <sub>Mining</sub>. ACM, 5221–5230. doi:10.1145/3580305.3599853

[83] Wang-Cheng Kang and Julian McAuley. 2018. Self-attentive Sequential Recommendation. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> <sub>IEEE</sub> International Conference on Data Mining (ICDM)<sup>.</sup> <sup>197–206.</sup>

[84] Yujin Kang and Thomas Lee. 2024. EdgeLLM: A Toolkit for Memory-Eficient LLM Inference on Edge Hardware. arXiv preprint arXiv:2402.08945 <sup>(2024).</sup>

[85] Guolin Ke, Qi Meng, Thomas Finley, Taifeng Wang, Wei Chen, Weidong Ma, Qiwei Ye, and Tie-Yan Liu. 2017. LightGBM: A highly eficient gradient boosting decision tree. In <sub>NeurIPS</sub>.

[86] Hee-Jin Kim and Dario Vento. 2025. Twin-Tower Distillation for Continual Representation Alignment. In <sub>Proceedings</sub> of the 2025 Conference on Recommender Systems (RecSys)<sup>.</sup>

[87] Soohyun Kim and Rajat Agarwal. 2025. EdgeBlend: Eficient Deployment of Generative Recommenders on Edge <sup>Devices.</sup> <sup>In</sup> Proceedings of the 2025 International Conference on Embedded Systems (ICES)<sup>.</sup>

[88] V. Klema and A. Laub. 1980. The singular value decomposition: Its computation and some applications. <sub>IEEE</sub> <sub>Trans.</sub> <sub>Automat.</sub> <sub>Control</sub> 25, 2 (1980), 164–176. doi:10.1109/TAC.1980.1102314

[89] Tatsuki Koga, Ruihan Wu, and Kamalika Chaudhuri. 2025. Privacy-Preserving Retrieval-Augmented Generation with Diferential Privacy. arXiv:2412.04697 [cs.CR] https://arxiv.org/abs/2412.04697

[90] Yehuda Koren, Robert Bell, and Chris Volinsky. 2009. Matrix factorization techniques for recommender systems. <sub>Computer</sub> 42, 8 (2009), 30–37.

[91] Ivica Kostric, Krisztian Balog, and Ujwal Gadiraju. 2025. Should We Tailor the Talk? Understanding the Impact of Conversational Styles on Preference Elicitation in Conversational Recommender Systems. arXiv:2504.13095 [cs.HC] https://arxiv.org/abs/2504.13095

[92] Anna Kruspe. 2024. Towards detecting unanticipated bias in Large Language Models. arXiv:2404.02650 [cs.LG] https://arxiv.org/abs/2404.02650

[93] Maciej Kula. 2015. Metadata Embeddings for User and Item Cold-start Recommendations. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> <sub>2nd</sub> Workshop on New Trends on Content-based Recommender Systems co-located with RecSys 2015<sup>.</sup> <sup>14–21.</sup>

[94] Alex Kulesza and Ben Taskar. 2012. Determinantal point processes for machine learning. <sub>Foundations</sub> <sub>and</sub> <sub>Trends</sub> <sub>in</sub> <sub>Machine</sub> <sub>Learning</sub> 5, 2–3 (2012), 123–286.

[95] Rajeev Kumar, Harishankar Kumar, and Kumari Shalini. 2025. Leveraging Knowledge Graphs and LLMs for Context Aware Messaging. arXiv:2503.13499 [cs.AI] https://arxiv.org/abs/2503.13499

[96] Daniel D Lee and H Sebastian Seung. 1999. Learning the parts of objects by non-negative matrix factorization. In <sub>Nature</sub>, Vol. 401. Nature Publishing Group, 788–791.

[97] Dong-Hyun Lee. 2013. Pseudo-Label: The Simple and Eficient Semi-Supervised Learning Method for Deep Neural <sup>Networks.</sup> <sup>In</sup> Proceedings of the ICML 2013 Workshop on Challenges in Representation Learning<sup>.</sup> <sup>Atlanta,</sup> <sup>GA,</sup> <sup>USA,</sup> <sup>1–6.</sup>

[98] Eunwoo Lee, Jungyeon Choi, and Younguk Kim. 2023. TempRec-Memory: Temporal Memory Networks for Drift <sup>Aware</sup> <sup>Recommendation.</sup> <sup>In</sup> Proceedings of the 17th ACM Conference on Recommender Systems (RecSys)<sup>.</sup>

[99] Hoyeop Lee, Jinbae Im, Seongwon Jang, Hyunsouk Cho, and Sehee Chung. 2019. MeLU: Meta-Learned User Preference Estimator for Cold-Start Recommendation. arXiv:1908.00413 [cs.IR] https://arxiv.org/abs/1908.00413

[100] Joonhan Lee, Yifan Hu, Yuchen Qiu, and Ed H Chi. 2023. Satisfaction Modeling for Recommender Systems. In Proceedings of the 46th International ACM SIGIR Conference on Research and Development in Information Retrieval <sub>(SIGIR)</sub>. ACM, 1064–1074.

[101] Jiwoo Lee and Hannah Zhou. 2025. SafeScope: Real-Time Detection of Toxic and PII Content in LLM Outputs. <sub>arXiv</sub> preprint arXiv:2504.11234 <sup>(2025).</sup>

[102] Yong-Min Lee, Priya Nair, and Carlos Fernández. 2024. SwapOut: On-Device NPU Scheduling and Speculative Decoding for Mobile LLMs. <sub>Transactions</sub> <sub>on</sub> <sub>Machine</sub> <sub>Learning</sub> <sub>Research</sub> 6, 1 (2024), 1–23. doi:10.48550/arXiv.2406.01234

[103] Dmitry Lepikhin, HyoukJoong Lee, Yuanzhong Xu, Dehao Chen, Orhan Firat, Yanping Huang, Maxim Krikun, Noam Shazeer, and Zhifeng Chen. 2021. GShard: Scaling Giant Models with Conditional Computation and Automatic <sup>Sharding.</sup> <sup>In</sup> International Conference on Learning Representations<sup>.</sup>

[104] Brian Lester, Rami Al-Rfou, and Noah Constant. 2021. The Power of Scale for Parameter-Eficient Prompt Tuning. In Proceedings of the 2021 Conference on Empirical Methods in Natural Language Processing (EMNLP)<sup>.</sup> <sup>Association</sup> <sup>for</sup> Computational Linguistics, 3045–3059.

[105] Patrick Lewis, Ethan Perez, Aleksandra Piktus, Fabio Petroni, Vladimir Karpukhin, Naman Goyal, Heinrich Küttler, Mike Lewis, Wen tau Yih, Tim Rocktäschel, Sebastian Riedel, and Douwe Kiela. 2021. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. arXiv:2005.11401 [cs.CL] https://arxiv.org/abs/2005.11401

[106] Haitao Li, Qian Dong, Junjie Chen, Huixue Su, Yujia Zhou, Qingyao Ai, Ziyi Ye, and Yiqun Liu. 2024. LLMs-as-Judges: A Comprehensive Survey on LLM-based Evaluation Methods. arXiv:2412.05579 [cs.CL] https://arxiv.org/abs/2412.05579

[107] Junliang Li, Pengjie Ren, Zhumin Chen, Zhaochun Ren, Defu Lian, Shaoping Ma, and Maarten de Rijke. 2020. Time Interval Aware Self-Attention for Sequential Recommendation. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> <sub>AAAI</sub> <sub>Conference</sub> <sub>on</sub> <sub>Artificial</sub> <sub>Intelligence</sub>, Vol. 34. 2595–2602.

[108] Jing Li, Pengjie Ren, Zhumin Chen, Zhaochun Ren, Jiliang Ma, and Maarten de Rijke. 2017. Neural attentive session-based recommendation. In <sub>CIKM</sub>.

[109] Jia Li, Wayne Xin Zhao, and Min Zhang. 2022. CRSLab: An Open-Source Toolkit for Building Conversational Recommender Systems. <sub>Information</sub> <sub>Processing</sub> <sub>&</sub> <sub>Management</sub> 59, 6 (2022), 103074.

[110] Kenneth Li, Tianle Liu, Naomi Bashkansky, David Bau, Fernanda Viégas, Hanspeter Pfister, and Martin Wattenberg. 2024. Measuring and Controlling Instruction (In)Stability in Language Model Dialogs. arXiv:2402.10962 [cs.CL] https://arxiv.org/abs/2402.10962

[111] Lihong Li, Wei Chu, John Langford, and Robert E Schapire. 2010. A contextual-bandit approach to personalized news article recommendation. In <sub>WWW</sub>.

[112] Pan Li, Yuyan Wang, Ed H. Chi, and Minmin Chen. 2023. <sub>Prompt</sub> <sub>Tuning</sub> <sub>Large</sub> <sub>Language</sub> <sub>Models</sub> <sub>on</sub> <sub>Personalized</sub> <sub>Aspect</sub> <sub>Extraction</sub> <sub>for</sub> <sub>Recommendations</sub>. arXiv preprint arXiv:2306.01475. arXiv. https://arxiv.org/abs/2306.01475

[113] Qinchan Li, Kenneth Chen, Changyue Su, Wittawat Jitkrittum, Qi Sun, and Patsorn Sangkloy. 2025. Cost-Aware Routing for Eficient Text-To-Image Generation. arXiv:2506.14753 [cs.CV] https://arxiv.org/abs/2506.14753

[114] Shuo Li and Ananya Roy. 2025. Gradient Sanitization for Diferentially Private LLM Fine-Tuning. <sub>arXiv</sub> <sub>preprint</sub> arXiv:2501.08765 <sup>(2025).</sup>

[115] Xinyi Li, Yongfeng Zhang, and Edward C. Malthouse. 2023. PBNR: Prompt-based News Recommender System. arXiv:2304.07862 [cs.IR] https://arxiv.org/abs/2304.07862

[116] Xianzhi Li, Ran Zmigrod, Zhiqiang Ma, Xiaomo Liu, and Xiaodan Zhu. 2024. Fine-Tuning Language Models with Diferential Privacy through Adaptive Noise Allocation. arXiv:2410.02912 [cs.AI] https://arxiv.org/abs/2410.02912

[117] Yankai Li, Zhiyong Lin, Canran Xu, Hu Xu, Ziniu Wu, and Jian-Yun Nie. 2023. Generative Recommender Systems. In Proceedings of the 46th International ACM SIGIR Conference on Research and Development in Information Retrieval<sup>.</sup> ACM, 1–10.

[118] Yanli Li and Priya Verma. 2024. Zero-Shot Personalization in LLMs Without Long-Term Data Retention. In <sub>Proceedings</sub> of the 2024 Conference on Empirical Methods in Natural Language Processing (EMNLP)<sup>.</sup>

[119] Yujing Li, Chuhan Zhu, Fei Cheng, Pengfei Liu, Yanchi Zhang, Jing Wang, and Yongfeng Zhang. 2022. PEPLER: A Popularity-Biased Reinforcement Learning Framework for Personalized Review Generation. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> <sub>45th</sub> International ACM SIGIR Conference on Research and Development in Information Retrieval<sup>.</sup> <sup>ACM,</sup> <sup>1142–1152.</sup>

[120] Defu Lian, Haoyu Wang, Zheng Liu, Jianxun Lian, Enhong Chen, and Xing Xie. 2020. LightRec: A Memory and Search-Eficient Recommender System. In <sub>The</sub> <sub>Web</sub> <sub>Conference</sub> <sub>2020</sub> <sub>(WWW</sub> <sub>’20)</sub>. ACM, Taipei, Taiwan. doi:10.1145 3366423.3380125

[121] Sherlock A. Licorish, Ansh Bajpai, Chetan Arora, Fanyu Wang, and Kla Tantithamthavorn. 2025. Comparing Human and LLM Generated Code: The Jury is Still Out! arXiv:2501.16857 [cs.SE] https://arxiv.org/abs/2501.16857

[122] Jianghao Lin, Jiaqi Liu, Jiachen Zhu, Yunjia Xi, Chengkai Liu, Yangtian Zhang, Yong Yu, and Weinan Zhang. 2024. A Survey on Difusion Models for Recommender Systems. arXiv:2409.05033 [cs.IR] https://arxiv.org/abs/2409.05033

[123] Shaohan Lin, Pan Jin, Jinze Yu, Zhengyang Wu, Jiazhanfeng Jiang, Ming Liu, Yichong Rao, Jie Xu, Zhaochen Zhang, Haiyang Xu, Chenggang Cui, Weiwei Liu, Yao Zhao, Jun Yan, and Ji Zhang. 2021. M6-T: Exploring Sparse Expert <sup>Models</sup> <sup>and</sup> <sup>Beyond.</sup> arXiv preprint arXiv:2105.15082 <sup>(2021).</sup>

[124] Yining Lin, Yiqiang Ge, Zheng Zhu, Yufei Ge, Xiang Wang, and Zhoujun Lin. 2023. Meta-LLMRec: Meta-Learningbased Cold-start Recommendation with Large Language Models. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2310.08549</sub> (2023). https: //arxiv.org/abs/2310.08549

[125] Zhi Lin and Ayesha Rahim. 2025. LLMs under the Law: Regulation-Aware Instruction Tuning for Compliant <sup>Personalization.</sup> arXiv preprint arXiv:2503.08121 <sup>(2025)</sup>

[126] Han Liu et al. 2021. Data Governance in Machine Learning: Enabling Compliance and Innovation. <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> <sub>2021</sub> <sub>AAAI/ACM</sub> <sub>Conference</sub> <sub>on</sub> <sub>AI,</sub> <sub>Ethics,</sub> <sub>and</sub> <sub>Society</sub> (2021). https://dl.acm.org/doi/10.1145/3461702.3462545

[127] Junling Liu, Chao Liu, Peilin Zhou, Qichen Ye, Dading Chong, Kang Zhou, Yueqi Xie, Yuwei Cao, Shoujin Wang, Chenyu You, and Philip S. Yu. 2023. LLMRec: Benchmarking Large Language Models on Recommendation Task. (2023). arXiv:2308.12241 [cs.IR] https://arxiv.org/abs/2308.12241

[128] Jiahong Liu, Zexuan Qiu, Zhongyang Li, Quanyu Dai, Jieming Zhu, Minda Hu, Menglin Yang, and Irwin King. 2025. A Survey of Personalized Large Language Models: Progress and Future Directions. arXiv:2502.11528 [cs.AI] https://arxiv.org/abs/2502.11528

[129] Qidong Liu, Xiangyu Zhao, Yejing Wang, Zijian Zhang, Howard Zhong, Chong Chen, Xiang Li, Wei Huang, and Feng Tian. 2025. Bridge the Domains: Large Language Models Enhanced Cross-domain Sequential Recommendation. arXiv:2504.18383 [cs.IR] https://arxiv.org/abs/2504.18383

[130] Shuang Liu and Kevin Zhu. 2025. Negative Prompt Augmentation for Contrastive Hallucination Mitigation. In Proceedings of the 2025 International Conference on Learning Representations (ICLR)<sup>.</sup>

[131] Xinyi Liu, Ruijie Wang, Dachun Sun, Dilek Hakkani Tur, and Tarek Abdelzaher. 2025. Uncovering Cross-Domain <sup>Recommendation</sup> <sup>Ability</sup> <sup>of</sup> <sup>Large</sup> <sup>Language</sup> <sup>Models.</sup> <sup>In</sup> Companion Proceedings of the ACM on Web Conference 2025 <sub>(WWW</sub> <sub>’25)</sub>. ACM, 2736–2743. doi:10.1145/3701716.3717850

[132] Yang Liu, Dan Iter, Yichong Xu, Shuohang Wang, Ruochen Xu, and Chenguang Zhu. 2023. G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment. (2023). arXiv:2303.16634 [cs.CL] https://arxiv.org/abs/2303.16634

[133] Yuntao Liu, Xiang Lin, Ziniu Hu, Yaliang Wang, Min Jiang, Jing Gao, and Wei Chen. 2023. Aligning large language models with human feedback. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2305.18290</sub> (2023).

[134] Yufang Liu, Shaoqing Wang, Xueting Li, and Fuzhen Sun. 2024. A Meta-adversarial Framework for Cross-Domain Cold-Start Recommendation. <sub>Data</sub> <sub>Science</sub> <sub>and</sub> <sub>Engineering</sub> 9, 2 (2024), 238–249.

[135] Yifan Liu and Ming Zhao. 2025. PromptScope: Fingerprinting and Tracking LLM Prompts in Production. In <sub>Proceedings</sub> of the 2025 ACM SIGIR Conference<sup>.</sup>

[136] Zhi Liu and Thomas Rehn. 2025. EmbeddingShift: Backward-Compatible Representations for Dynamic Embedding <sup>Spaces.</sup> <sup>In</sup> Proceedings of the 2025 International Conference on Machine Learning (ICML)

[137] Pasquale Lops, Marco de Gemmis, and Giovanni Semeraro. 2011. Content-based Recommender Systems: State of the Art and Trends. <sub>Recommender</sub> <sub>Systems</sub> <sub>Handbook</sub> (2011), 73–105.

[138] Jiasen Lu, Christopher Clark, Sangho Lee, Zichen Zhang, Savya Khosla, Ryan Marten, Derek Hoiem, and Aniruddha Kembhavi. 2023. Unified-IO 2: Scaling Autoregressive Multimodal Models with Vision, Language, Audio, and Action. arXiv:2312.17172 [cs.CV] https://arxiv.org/abs/2312.17172

[139] Jiasen Lu, Christopher Clark, Rowan Zellers, Roozbeh Mottaghi, and Aniruddha Kembhavi. 2022. Unified-IO: A Unified Model for Vision, Language, and Multi-Modal Tasks. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2206.08916</sub> (2022)

[140] Haoyan Luo and Lucia Specia. 2024. From Understanding to Utilization: A Survey on Explainability for Large Language Models. arXiv:2401.12874 [cs.CL] https://arxiv.org/abs/2401.12874

[141] Sichun Luo, Yuxuan Yao, Bowei He, Yinya Huang, Aojun Zhou, Xinyi Zhang, Yuanzhang Xiao, Mingjie Zhan, and Linqi Song. 2024. Integrating Large Language Models into Recommendation via Mutual Augmentation and Adaptive Aggregation. arXiv:2401.13870 [cs.IR] https://arxiv.org/abs/2401.13870

[142] Chao Ma, Xiaoxue Zhao, Yaliang Li, Dawei Yin, Jing Zhang, Jun Yang, and Qiang Yang. 2020. Towards multi-objective recommendation systems. arXiv preprint arXiv:2004.11117 (2020).

[143] Qiyao Ma, Xubin Ren, and Chao Huang. 2024. XRec: Large Language Models for Explainable Recommendation. In Findings of the Association for Computational Linguistics: EMNLP 2024<sup>.</sup> <sup>Association</sup> <sup>for</sup> <sup>Computational</sup> <sup>Linguistics,</sup> Miami, Florida, USA, 391–402. doi:10.18653/v1/2024.findings-emnlp.22

[144] Yu A Malkov and D A Yashunin. 2020. Eficient and robust approximate nearest neighbor search using Hierarchica Navigable Small World graphs. <sub>IEEE</sub> <sub>TPAMI</sub> 42, 4 (2020), 824–836.

[145] James McInerney, Martin Jaggi, and Thorsten Joachims. 2021. Counterfactual Evaluation of Slate Recommendations <sup>with</sup> <sup>Sequential</sup> <sup>Rewards.</sup> <sup>In</sup> Proceedings of the 14th ACM International Conference on Web Search and Data Mining <sub>(WSDM)</sub>. ACM, 546–554.

[146] H. Brendan McMahan, Eider Moore, Daniel Ramage, Seth Hampson, and Blaise Aguera y Arcas. 2017. Communication-Eficient Learning of Deep Networks from Decentralized Data. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> <sub>20th</sub> <sub>International</sub> <sub>Conference</sub> <sub>on</sub> Artificial Intelligence and Statistics (AISTATS)<sup>.</sup> <sup>1273–1282.</sup>

[147] Sean M. McNee, John Riedl, and Joseph A. Konstan. 2006. Being accurate is not enough: how accuracy metrics have <sup>hurt</sup> <sup>recommender</sup> <sup>systems.</sup> <sup>In</sup> CHI’06 Extended Abstracts on Human Factors in Computing Systems<sup>.</sup> <sup>ACM,</sup> <sup>1097–1101.</sup>

[148] Rishabh Mehrotra, James McInerney, Hugo Bouchard, Mounia Lalmas, and Fernando Diaz. 2018. Towards a Fair Marketplace: Counterfactual Evaluation of the Trade-of Between Relevance, Fairness, and Satisfaction in Recommen <sup>dation</sup> <sup>Systems.</sup> <sup>In</sup> Proceedings of the 27th ACM International Conference on Information and Knowledge Management (CIKM)<sup>.</sup>

[149] Prem Melville, Raymond J Mooney, and Ramadass Nagarajan. 2002. Content-boosted collaborative filtering for improved recommendations. In <sub>AAAI/IAAI</sub>. 187–192.

[150] Yichen Meng, Hanning Luo, Xiangnan He, and Xiao Yang. 2024. LLMRecSim: Large Language Model-based Recom <sup>mendation</sup> <sup>Simulation.</sup> arXiv preprint arXiv:2403.07956 <sup>(2024).</sup>

[151] Margaret Mitchell, Simone Wu, Andrew Zaldivar, et al. 2019. Model Cards for Model Reporting. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> Conference on Fairness, Accountability, and Transparency (FAT\*)<sup>.</sup>

[152] Akos Nagy, Yannis Spyridis, and Vasileios Argyriou. 2025. Cross-Format Retrieval-Augmented Generation in XR with LLMs for Context-Aware Maintenance Assistance. (2025). arXiv:2502.15604 [cs.IR] https://arxiv.org/abs/2502.15604

[153] Maxim Naumov, Dheevatsa Mudigere, Hao-Jun Michael Shi, Jianyu Huang, Narayanan Sundaram, Jongsoo Park, Xiaodong Wang, Udit Gupta, Carole-Jean Wu, Alisson G. Azzolini, et al. 2019. Deep Learning Recommendation Model for Personalization and Recommendation Systems. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> <sub>13th</sub> <sub>ACM</sub> <sub>Conference</sub> <sub>on</sub> <sub>Recommender</sub> Systems (RecSys)<sup>.</sup> <sup>ACM,</sup> <sup>320–327.</sup>

[154] Thanh Nguyen and Lucia Pan. 2024. Ephemeral Prompting for Privacy-Aware User Modeling in LLMs. <sub>arXiv</sub> <sub>preprint</sub> arXiv:2402.01539 <sup>(2024).</sup>

[155] Yifan Nie and Jason Li. 2024. COBARec: Causal Bandit Simulators for Recommender Evaluation. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> 2024 International Conference on Web Search and Data Mining (WSDM)<sup>.</sup>

[156] Changdae Oh, Zhen Fang, Shawn Im, Xuefeng Du, and Yixuan Li. 2025. Understanding Multimodal LLMs Under Distribution Shifts: An Information-Theoretic Approach. arXiv:2502.00577 [cs.AI] https://arxiv.org/abs/2502.00577

[157] OpenAI. 2023. GPT-4 Technical Report. https://openai.com/research/gpt-4. Accessed: 2023-03-14.

[158] Long Ouyang, Jefrey Wu, Xu Jiang, Diogo Almeida, Carroll Wainwright, Nelson Mishkin, Chong Zhang, Sandhini Agarwal, Katarina Slama, Alex Ray, et al. 2022. Training language models to follow instructions with human feedback. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2203.02155</sub> (2022). https://arxiv.org/abs/2203.02155

[159] Alexander Pan, Erik Jones, Meena Jagadeesan, and Jacob Steinhardt. 2024. Feedback Loops With Language Models Drive In-Context Reward Hacking. (2024). arXiv:2402.06627 [cs.LG] https://arxiv.org/abs/2402.06627

[160] Shakti Panigrahi, Susan Athey, et al. 2023. Industrial-scale recommender systems: design patterns and challenges. arXiv preprint arXiv:2410.19744 <sup>(2023).</sup>

[161] Daewoo Park and Felix James. 2025. Reinforcement Learning for Prompt Robustness in Interactive Systems. <sub>Transac-</sub> tions on Interactive Intelligent Systems <sup>(2025).</sup>

[162] Minho Park and Laura Chen. 2025. Black-Box Probes for Tracing Causal Shifts in Generative Recommender Systems. Transactions on Recommender Systems <sup>3,</sup> <sup>1</sup> <sup>(2025),</sup> <sup>45–59</sup>

[163] Yeongjin Park, Seonwoo Ha, and Lidia Celis. 2019. Estimating Click Satisfaction via Weak Supervision in Recommen dation Systems. ACM Transactions on Recommender Systems 7, 3 (2019), 17:1–17:26.

[164] Young Park and Alexander Tuzhilin. 2006. Naive collaborative filtering using implicit feedback. In <sub>RecSys</sub>

[165] Neha Patel and Arjun Deshmukh. 2024. Hallucination-Aware Generation for Recommender Explanations. In <sub>Proceed-</sub> ings of the 2024 Annual Meeting of the Association for Computational Linguistics (ACL)<sup>.</sup>

[166] Qiyao Peng, Hongtao Liu, Hua Huang, Qing Yang, and Minglai Shao. 2025. A Survey on LLM-powered Agents for Recommender Systems. arXiv:2502.10050 [cs.IR] https://arxiv.org/abs/2502.10050

[167] Bryan Perozzi, Rami Al-Rfou, and Steven Skiena. 2014. DeepWalk: Online learning of social representations. In <sub>KDD</sub>.

[169] Xuelin Qian, Yikai Wang, Xinwei Sun, Yanwei Fu, Xiangyang Xue, and Jianfeng Feng. 2024. LEA: Learning Latent Embedding Alignment Model for fMRI Decoding and Encoding. <sub>Transactions</sub> <sub>on</sub> <sub>Machine</sub> <sub>Learning</sub> <sub>Research</sub> (2024). https://openreview.net/forum?id=89QT2DsKyj

[170] Massimo Quadrana, Alexandros Karatzoglou, Balazs Hidasi, and Paolo Cremonesi. 2017. Sequence-aware recommender systems. In <sub>RecSys</sub>

[171] Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya Ramesh, Gabriel Goh, Sandhini Agarwal, Girish Sastry, Amanda Askell, Pamela Mishkin, Jack Clark, et al. 2021. Learning Transferable Visual Models From Natural Language <sup>Supervision.</sup> <sup>In</sup> Proceedings of the 38th International Conference on Machine Learning (ICML)<sup>.</sup>

[172] Jack W Rae, Sebastian Borgeaud, Trevor Cai, Kathryn Millican, Jordan Hofmann, Francis Song, John Aslanides, Sergi Henderson, Roman Ring, Susannah Young, et al. 2021. Scaling language models: Methods, analysis and insights from <sup>training</sup> <sup>Gopher.</sup> arXiv preprint arXiv:2112.11446 <sup>(2021).</sup>

[173] Fatima Rahman and Jae-Min Choi. 2025. Personalization Prompt Attacks on Private LLMs. <sub>arXiv</sub> <sub>preprint</sub> arXiv:2505.01289 <sup>(2025).</sup>

[174] Arun Rajaraman, Mitali Gupta, and Vivek Singh. 2025. LatOpt: Latency-Optimized Transformer Inference with <sup>4-bit</sup> <sup>Weight-Only</sup> <sup>Quantization.</sup> <sup>In</sup> Proceedings of the 42nd International Conference on Machine Learning (ICML)<sup>.</sup> 12345–12356. doi:10.XXXX/icml.2025.123 arXiv:2501.01234.

[175] Jerome Ramos, Bin Wu, and Aldo Lipani. 2025. PeaPOD: Personalized Prompt Distillation for Generative Recommen dation. arXiv:2407.05033 [cs.IR] https://arxiv.org/abs/2407.05033

[176] Kanchana Ranasinghe, Xiang Li, Kumara Kahatapitiya, and Michael S. Ryoo. 2025. Understanding Long Videos with Multimodal Language Models. arXiv:2403.16998 [cs.CV] https://arxiv.org/abs/2403.16998

[177] Karthik Rao and Emily Jin. 2024. Synthetic Supervision: Scaling LLM Personalization with Privacy Constraints. In Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL)<sup>.</sup>

[178] Pengjie Ren, Jiaxin Zhang, Jian Ma, Jun Li, and Maarten de Rijke. 2021. LEGO: Latent Expert Guided Optimization <sup>for</sup> <sup>Sparse</sup> <sup>Target</sup> <sup>Recommendation.</sup> <sup>In</sup> Proceedings of the 44th International ACM SIGIR Conference on Research and Development in Information Retrieval<sup>.</sup>

[179] Mónica Ribero, Jette Henderson, Sinead Williamson, and Haris Vikalo. 2020. Federating Recommendations Using Diferentially Private Prototypes. (2020). arXiv:2003.00602 [cs.IR] https://arxiv.org/abs/2003.00602

[180] Carlos Riquelme, Joan Puigcerver, Basil Mustafa, Maxim Neumann, Rodolphe Jenatton, André Susano Pinto, Danie Keysers, and Neil Houlsby. 2021. Scaling vision with sparse mixture of experts. <sub>Advances</sub> <sub>in</sub> <sub>Neural</sub> <sub>Information</sub> <sub>Processing</sub> <sub>Systems</sub> 34 (2021), 8583–8595.

[181] Emily Rogers, Kartik Goel, and Alisha Das. 2025. Understanding the Cost Dynamics of Cloud-Based LLM APIs in High-Throughput Inference Pipelines. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2505.09876</sub> (2025). Under review at NeurIPS 2025.

[182] Yuta Saito. 2020. Unbiased Recommender Learning from Missing-Not-At-Random Implicit Feedback. In <sub>Proceedings</sub> of the 26th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining<sup>.</sup> <sup>ACM,</sup> <sup>2081–2090.</sup>

[183] Victor Sanh, Albert Webson, Colin Rafel, Stephen H. Bach, Lintang Sutawika, Zaid Alyafeai, Antoine Chafin, Arnaud Stiegler, Teven Le Scao, Arun Raja, Manan Dey, M Saiful Bari, Canwen Xu, Urmish Thakker, Shanya Sharma Sharma, Eliza Szczechla, Taewoon Kim, Gunjan Chhablani, Nihal Nayak, Debajyoti Datta, Jonathan Chang, Mike Tian-Jian Jiang, Han Wang, Matteo Manica, Sheng Shen, Zheng Xin Yong, Harshit Pandey, Rachel Bawden, Thomas Wang, Trishala Neeraj, Jos Rozen, Abheesht Sharma, Andrea Santilli, Thibault Fevry, Jason Alan Fries, Ryan Teehan, Tal Bers, Stella Biderman, Leo Gao, Thomas Wolf, and Alexander M. Rush. 2022. Multitask Prompted Training Enables Zero-Shot Task Generalization. arXiv:2110.08207 [cs.LG] https://arxiv.org/abs/2110.08207

[184] Ranjan Sapkota, Shaina Raza, Maged Shoman, Achyut Paudel, and Manoj Karkee. 2025. Multimodal Large Language Models for Image, Text, and Speech Data Augmentation: A Survey. arXiv:2501.18648 [cs.CV] https://arxiv.org/abs 2501.18648

[185] Badrul Sarwar, George Karypis, Joseph Konstan, and John Riedl. 2001. Item-based collaborative filtering recommen-<sup>dation</sup> <sup>algorithms.</sup> <sup>In</sup> Proceedings of the 10th International Conference on World Wide Web (WWW)<sup>.</sup> <sup>ACM,</sup> <sup>285–295.</sup> doi:10.1145/371920.372071

[186] Clement Savarese et al. 2020. Metaflow: Human-Centric ML Platform at Netflix. <sub>Netflix</sub> <sub>Tech</sub> <sub>Blog</sub> (2020). https: //netflixtechblog.com/metaflow-a-human-centric-ml-platform-445f6d3e3a6

[187] J Ben Schafer, Joseph Konstan, and John Riedl. 2001. E-commerce recommendation applications. <sub>Data</sub> <sub>mining</sub> <sub>and</sub> knowledge discovery 5, 1 (2001), 115–153.

[188] Andrew I Schein, Alexandrin Popescul, Lyle H Ungar, and David M Pennock. 2002. Methods and metrics for cold-start recommendations. In <sub>SIGIR</sub>.

[189] Tobias Schnabel, Adith Swaminathan, Ashudeep Singh, Navin Chandak, and Thorsten Joachims. 2016. Recommenda tions as Treatments: Debiasing Learning and Evaluation. arXiv:1602.05352 [cs.LG] https://arxiv.org/abs/1602.05352

[190] William Seymour, Xiao Zhan, Mark Coté, and Jose Such. 2023. Who are CUIs Really For? Representation and Accessibility in the Conversational User Interface Literature. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> <sub>5th</sub> <sub>International</sub> <sub>Conference</sub> <sub>on</sub> Conversational User Interfaces (CUI 2023) (Proceedings of the 5th International Conference on Conversational User <sub>Interfaces,</sub> <sub>CUI</sub> <sub>2023)</sub>. Eindhoven, The Netherlands. doi:10.1145/3571884.3603760 Article 26.

[191] Jay Shah, Ganesh Bikshandi, Ying Zhang, Vijay Thakkar, Pradeep Ramani, and Tri Dao. 2024. FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-precision. arXiv:2407.08608 [cs.LG] https://arxiv.org/abs/2407.08608

[192] Yu Shang, Peijie Liu, Yuwei Yan, Zijing Wu, Leheng Sheng, Yuanqing Yu, Chumeng Jiang, An Zhang, Fengli Xu, Yu Wang, Min Zhang, and Yong Li. 2025. AgentRecBench: Benchmarking LLM Agent-based Personalized Recommender Systems. arXiv:2505.19623 [cs.IR] https://arxiv.org/abs/2505.19623

[193] Min Shao, Lu Yin, and Devika Rao. 2024. Fidelity Critics for LLM Output Verification via Human Feedback. <sub>arXiv</sub> preprint arXiv:2404.09210 <sup>(2024).</sup>

[194] Noam Shazeer, Azalia Mirhoseini, Krzysztof Maziarz, Andy Davis, Quoc Le, Geofrey Hinton, and Jef Dean. 2017. Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer. arXiv:1701.06538 [cs.LG] https://arxiv.org/abs/1701.06538

[195] Sheng Shen, Samyam Rajbhandari, Zhewei Tang, and Yuxiong He. 2021. PowerBERT: Accelerating BERT Inference <sup>via</sup> <sup>Lossless</sup> <sup>Parameter</sup> <sup>Reduction.</sup> <sup>In</sup> Proceedings of the 38th International Conference on Machine Learning (ICML)<sup>.</sup> PMLR, 9434–9443.

[196] Zhiwei Shi, Yongfeng Zhang, Wayne Xin Zhao, and Ji-Rong Wen. 2023. Retrieval-Augmented Generation for Recommendation: A Survey and New Perspectives. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2312.03567</sub> (2023).

[197] Victoria Smith, Ali Shahin Shamsabadi, Carolyn Ashurst, and Adrian Weller. 2024. Identifying and Mitigating Privacy Risks Stemming from Language Models: A Survey. arXiv:2310.01424 [cs.CL] https://arxiv.org/abs/2310.01424

[198] Zhiwei Song and Kavita Bala. 2024. HybridBench: Benchmarking End-to-End Latency and Accuracy for LLM+Vector <sup>Recommender</sup> <sup>Architectures.</sup> <sup>In</sup> Proceedings of the 2024 ACM Conference on Recommender Systems (RecSys)<sup>.</sup>

[199] Fei Sun, Junyang Liu, Jian Wu, Changhua Pei, Xiao Lin, Wenwu Ou, and Peng Jiang. 2019. BERT4Rec: Sequential recommendation with bidirectional encoder representations from transformer. In <sub>CIKM</sub>.

[200] Hongyuan Sun, Xiaoyang Li, Ming Zhou, Yujing Xu, and Wayne Xin Zhao. 2023. Personalization at scale: Large language models in TikTok’s recommendation system. In <sub>KDD</sub>.

[201] Xu Sun, Bingzhen Wei, Xuancheng Ren, and Shuming Ma. 2017. Label Embedding Network: Learning Label Rep resentation for Soft Training of Deep Networks. <sub>CoRR</sub> abs/1710.10393 (2017). Originally cited as Hu et al. (2016); updated to reflect correct authorship.

[202] Ravi Surana and Lila Thompson. 2023. Diagnosing Hallucinations in Generative Recommenders. <sub>arXiv</sub> <sub>preprint</sub> arXiv:2310.07421 <sup>(2023).</sup>

[203] Patrick Sutanto, Joan Santoso, Esther Irawati Setiawan, and Aji Prasetya Wibawa. 2024. LLM Distillation for Eficient Few-Shot Multiple Choice Question Answering. arXiv:2412.09807 [cs.CL] https://arxiv.org/abs/2412.0980

[204] Suraiya Tairin, Shohaib Mahmud, Haiying Shen, and Anand Iyer. 2025. eMoE: Task-aware Memory Eficient Mixture of-Experts-Based (MoE) Model Inference. arXiv:2503.06823 [cs.LG] https://arxiv.org/abs/2503.06823

[205] Jianmo Tang, Ruoxi Wang, Jialin Zhang, Wayne Xin Zhao, Xiang Wang, Yifeng Wu, Fei Wu, Enhong Chen, Xing Xie, and Minlie Wang. 2023. Recent Advances in LLM-enhanced Recommender Systems: Techniques, Challenges, and <sup>Opportunities.</sup> arXiv preprint arXiv:2310.04682 <sup>(2023).</sup>

[206] Ming Tang and Olivia Brooks. 2025. SecurePrompts: Privacy-Preserving Inference for Personalized LLMs. In <sub>Proceed-</sub> ings of the 2025 USENIX Security Symposium<sup>.</sup>

[207] Chongyang Tao, Tao Shen, Shen Gao, Junshuo Zhang, Zhen Li, Zhengwei Tao, and Shuai Ma. 2024. LLMs are Also Efective Embedding Models: An In-depth Overview. arXiv:2412.12591 [cs.CL] https://arxiv.org/abs/2412.12591

[208] Guy Tennenholtz, Yinlam Chow, Chih-Wei Hsu, Jihwan Jeong, Lior Shani, Azamat Tulepbergenov, Deepak Ramachan dran, Martin Mladenov, and Craig Boutilier. 2024. Demystifying Embedding Spaces using Large Language Models. arXiv:2310.04475 [cs.CL] https://arxiv.org/abs/2310.04475

[209] Ashok Thomas, Sandeep Reddy, Maxwell Zeni, and Ruoxi Zhang. 2022. Interactive recommendations using conversational context at Spotify. In <sub>RecSys</sub>

[210] Jiahao Tian, Jinman Zhao, Zhenkai Wang, and Zhicheng Ding. 2025. MMREC: LLM Based Multi-Modal Recommender System. arXiv:2408.04211 [cs.CL] https://arxiv.org/abs/2408.04211

[211] Shengbang Tong, David Fan, Jiachen Zhu, Yunyang Xiong, Xinlei Chen, Koustuv Sinha, Michael Rabbat, Yann LeCun, Saining Xie, and Zhuang Liu. 2024. MetaMorph: Multimodal Understanding and Generation via Instruction Tuning. arXiv:2412.14164 [cs.CV] https://arxiv.org/abs/2412.14164

[212] Kim Tran, Rajeev Khanna, and Sophie Nguyen. 2024. Serverless Accelerators for Scalable LLM Inference: Cold <sup>Start</sup> <sup>Trade-ofs</sup> <sup>and</sup> <sup>Tail</sup> <sup>Latency.</sup> <sup>In</sup> Proceedings of the 15th USENIX Symposium on Operating Systems Design and <sub>Implementation</sub> <sub>(OSDI)</sub>. 402–418. doi:10.5555/osdi24-45

[213] Linh Tran, Wei Sun, Stacy Patterson, and Ana Milanova. 2025. Privacy-Preserving Personalized Federated Prompt Learning for Multimodal Large Language Models. arXiv:2501.13904 [cs.LG] https://arxiv.org/abs/2501.13904

[214] Sebastian Tschiatschek, Eugenia Stamboliev, Timothée Schmude, Mark Coeckelbergh, and Laura Koesten. 2024. Challenging the Human-in-the-loop in Algorithmic Decision-making. (2024). arXiv:2405.10706 [cs.LG] https: //arxiv.org/abs/2405.10706

[215] Keyvan Vahidy, Seyed Javad Mirabedini, and Touraj Banirostam. 2021. Resolving cold start and sparse data challeng in recommender systems using multi-level singular value decomposition. <sub>Computers</sub> <sub>&</sub> <sub>Electrical</sub> <sub>Engineering</sub> 94 (2021), 107361.

[216] Ajay Krishna Vajjala, Dipak Meher, Ziwei Zhu, and David S. Rosenblum. 2024. Cross-Domain Recommendation Meets Large Language Models. arXiv:2411.19862 [cs.IR] https://arxiv.org/abs/2411.19862

[217] Fabio Vasile, Luca Pappalardo, Giovanni Muscato, and Armir Bujari. 2022. Multimodal Learning for Music Recom <sup>mendations</sup> <sup>in</sup> <sup>the</sup> <sup>Long</sup> <sup>Tail.</sup> <sup>In</sup> Proceedings of the 30th ACM International Conference on Multimedia<sup>.</sup> <sup>ACM,</sup> <sup>2765–2774.</sup> doi:10.1145/3503161.3547977

[218] Arpita Vats, Vinija Jain, Rahul Raja, and Aman Chadha. 2024. Exploring the Impact of Large Language Models on Recommender Systems: An Extensive Review. arXiv:2402.18590 [cs.IR] https://arxiv.org/abs/2402.18590

[219] Wang. 2024. DialogRec: Reinforcement learning enhanced conversational recommender systems. In <sub>Proceedings</sub> <sub>of</sub> the 2024 Conference on Recommender Systems (RecSys)<sup>.</sup>

[220] Chen Wang, Mingdai Yang, Zhiwei Liu, Pan Li, Linsey Pang, Qingsong Wen, and Philip Yu. 2025. Automating Personalization: Prompt Optimization for Recommendation Reranking. arXiv:2504.03965 [cs.IR] https://arxiv.org abs/2504.03965

[221] Haoyu Wang, Xinyang Liu, Jing Zhang, and Chao Tan. 2021. Handling Sparse Conversion Labels in Large-Scale Recommendation Systems. arXiv preprint arXiv:2106.14553 (2021).

[222] Jianling Wang, Haokai Lu, James Caverlee, Ed Chi, and Minmin Chen. 2024. Large Language Models as Data Augmenters for Cold-Start Item Recommendation. (2024). arXiv:2402.11724 [cs.IR] https://arxiv.org/abs/2402.11724

[223] Ruofan Wang, Prakruthi Prabhakar, Gaurav Srivastava, Tianqi Wang, Zeinab S. Jalali, Varun Bharill, Yunbo Ouyang, Aastha Nigam, Divya Venugopalan, Aman Gupta, Fedor Borisyuk, Sathiya Keerthi, and Ajith Muralidharan. 2024. LiMAML: Personalization of Deep Recommender Models via Meta Learning. arXiv:2403.00803 [cs.IR] https://arxiv. org/abs/2403.00803

[224] Shoujin Wang, Liang Hu, Yan Wang, Xiangnan He, Quan Z. Sheng, Mehmet A. Orgun, Longbing Cao, Francesco Ricci, and Philip S. Yu. 2021. Graph Learning based Recommender Systems: A Review. arXiv:2105.06339 [cs.IR] https://arxiv.org/abs/2105.06339

[225] Wenqiang Wang, Jiarui Tang, Xiang Li, Yifan Zhu, and Xiaolin Wang. 2023. AlignRec: A unified framework for preference alignment in recommendation. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> <sub>ACM</sub> <sub>Web</sub> <sub>Conference</sub> <sub>(WWW)</sub>.

[226] Xinfeng Wang, Jin Cui, Yoshimi Suzuki, and Fumiyo Fukumoto. 2025. RDRec: Rationale Distillation for LLM-based Recommendation. arXiv:2405.10587 [cs.CL] https://arxiv.org/abs/2405.10587

[227] Xiang Wang, Yining Lin, Yiqiang Ge, Yufei Ge, and Zhoujun Lin. 2024. LLM4RecSim: Evaluating recommender systems with large language models. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2402.00761</sub> (2024). https://arxiv.org/abs/2402.00761

[228] Xiang Wang, Yining Lin, Yufei Ge, Zheng Zhu, Yiqiang Ge, and Zhoujun Lin. 2023. InstRec: Adapting Language Models for Multi-Objective Recommendation with Instructions. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> <sub>32nd</sub> <sub>ACM</sub> <sub>International</sub> <sub>Conference</sub> <sub>on</sub> <sub>Information</sub> <sub>and</sub> <sub>Knowledge</sub> <sub>Management</sub> <sub>(CIKM)</sub>. ACM, 2647–2656. doi:10.1145/3583780.3615257

[229] Yiran Wang, Xiaoqiang Liu, Jie Tang, Jinxin Xu, and Yongfeng Zhang. 2023. MMoE++: A Multi-Gate Mixture-of Experts Framework with Task-Interaction Constraints for E-Commerce Recommendations. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> <sub>29th</sub> ACM SIGKDD Conference on Knowledge Discovery and Data Mining<sup>.</sup> <sup>ACM,</sup> <sup>1725–1733.</sup> <sup>doi:10.1145/3580305.3599435</sup>

[230] Yifan Wang, Yicheng Wu, Yaliang Li, et al. 2023. ColdGPT: Bridging the cold-start gap in recommender systems with GPT and curriculum tuning. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2311.09700</sub> (2023).

[231] Yufei Wang, Chen Zhao, Hongyang Li, Ruixiang Tan, and Jie Lin. 2024. CoCa-2Rec: Contrastive Captioners for Personalized Recommendation. Under review.

[232] Koki Wataoka, Tsubasa Takahashi, and Ryokan Ri. 2024. Self-Preference Bias in LLM-as-a-Judge. arXiv:2410.21819 [cs.CL] https://arxiv.org/abs/2410.21819

[233] Jason Wei, Maarten Bosma, Vincent Y. Zhao, Kelvin Guu, Adams Wei Yu, Brian Lester, Nan Du, Andrew M. Dai, and Quoc V. Le. 2022. Finetuned Language Models Are Zero-Shot Learners. arXiv:2109.01652 [cs.CL] https: //arxiv.org/abs/2109.01652

[234] Brian Wong and Kaito Tanaka. 2025. High-Fidelity Pseudo-label Generation by Large Language Models for Training Robust Radiology Report Classifiers. arXiv:2505.01693 [cs.CL] https://arxiv.org/abs/2505.01693

[235] Junda Wu, Cheng-Chun Chang, Tong Yu, Zhankui He, Jianing Wang, Yupeng Hou, and Julian McAuley. 2024. CoRAL: Collaborative Retrieval-Augmented Large Language Models Improve Long-tail Recommendation. arXiv:2403.06447 [cs.IR] https://arxiv.org/abs/2403.06447

[236] Jiahao Wu and Rina Singh. 2025. Federated Prompting for On-Device Personalization in Large Language Models. In Proceedings of the 2025 International Conference on Learning Representations (ICLR)<sup>.</sup>

[237] Likang Wu, Zhi Zheng, Zhaopeng Qiu, Hao Wang, Hongchao Gu, Tingjia Shen, Chuan Qin, Chen Zhu, Hengshu Zhu, Qi Liu, Hui Xiong, and Enhong Chen. 2024. A Survey on Large Language Models for Recommendation. arXiv:2305.19860 [cs.IR] https://arxiv.org/abs/2305.19860

[238] Chulin Xie, Zinan Lin, Arturs Backurs, Sivakanth Gopi, Da Yu, Huseyin A Inan, Harsha Nori, Haotian Jiang, Huishuai Zhang, Yin Tat Lee, Bo Li, and Sergey Yekhanin. 2024. Diferentially Private Synthetic Data via Foundation Mode APIs 2: Text. arXiv:2403.01749 [cs.CL] https://arxiv.org/abs/2403.01749

[239] Yucheng Xie et al. 2023. End-to-End Training for Recommender Systems at Meta. https://ai.facebook.com/blog/endto-end-training-for-recommender-systems-at-meta/.

[240] Bo Xu and Aisha Khan. 2024. Drift-Aware Recommender Systems via Wasserstein Distance. <sub>arXiv</sub> <sub>preprint</sub> arXiv:2405.07890 <sup>(2024).</sup>

[241] Canwen Xu, Zekun Liu, Xudong Zhou, Zhiyuan Liu, and Maosong Sun. 2023. EvalTemplate: A Prompt Template Repository for Controlled LLM Evaluation. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2306.11479</sub> (2023).

[242] Peng Xu, Xiatian Zhu, and David A. Clifton. 2023. Multimodal Learning with Transformers: A Survey. arXiv:2206.06488 [cs.CV] https://arxiv.org/abs/2206.06488

[243] Ruipeng Xu, Wayne Xin Zhao, Jingyuan Liu, Wenqiang Du, and Ji-Rong Wen. 2023. LLMR: Large language model aug-<sup>mented</sup> <sup>recommender</sup> <sup>system</sup> <sup>with</sup> <sup>generated</sup> <sup>memory.</sup> <sup>In</sup> Proceedings of the 46th International ACM SIGIR Conference on Research and Development in Information Retrieval<sup>.</sup> <sup>ACM,</sup> <sup>2735–2745.</sup>

[244] Yuning Xu, Rahul Dhulipala, Michael Smith, Dean Pomerleau, Steven Reiss, and Hao Yang. 2022. Unified Multimodal Representation for Eficient Retrieval in Video Streaming. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> <sub>45th</sub> <sub>International</sub> <sub>ACM</sub> <sub>SIGIR</sub> <sub>Conference</sub> on Research and Development in Information Retrieval<sup>.</sup>

[245] Shuo Xue, Yaliang Li, Rui Wang, Jing Gao, and Min Jiang. 2022. RLHF-Rec: Reinforcement Learning from Human <sup>Feedback</sup> <sup>for</sup> <sup>Recommendation.</sup> <sup>In</sup> Proceedings of the 45th International ACM SIGIR Conference on Research and Development in Information Retrieval<sup>.</sup>

[246] Jingbo Yang, Bairu Hou, Wei Wei, Yujia Bao, and Shiyu Chang. 2025. KVLink: Accelerating Large Language Models via Eficient KV Cache Reuse. arXiv:2502.16002 [cs.CL] https://arxiv.org/abs/2502.16002

[247] Liangjie Yang, Bowen Bai, and Can Xu. 2020. Mixed negative sampling for learning two-tower neural networks in recommendations. In <sub>CIKM</sub>.

[248] Yansi Li, Jiahao Xu, Tian Liang, Xingyu Chen, Zhiwei He, Qiuzhi Liu, Rui Wang, Zhuosheng Zhang, Zhaopeng Tu, Haitao Mi, and Dong Yu. 2025. Dancing with Critiques: Enhancing LLM Reasoning with Stepwise Natural Language Self-Critique. (2025). doi:10.13140/RG.2.2.27912.33289

[249] Fei Ye, Xiang Li, Xiaoxue Liu, Yifan Sun, Yanchi Liu, Chuxu Zhang, and Wayne Xin Zhao. 2023. Large Language Models for Conversational Recommendation: A Survey and Open Problems. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> <sub>29th</sub> <sub>ACM</sub> <sub>SIGKDD</sub> Conference on Knowledge Discovery and Data Mining<sup>.</sup> <sup>ACM,</sup> <sup>4172–4181.</sup>

[250] Peiling Yi, Yuhan Xia, and Yunfei Long. 2025. Irony Detection, Reasoning and Understanding in Zero-shot Learning. arXiv:2501.16884 [cs.CL] https://arxiv.org/abs/2501.16884

[251] Zixuan Yi, Iadh Ounis, and Craig Macdonald. 2023. Contrastive Graph Prompt-tuning for Cross-domain Recommendation. arXiv:2308.10685 [cs.IR] https://arxiv.org/abs/2308.10685

[252] Xueyin Yin and Irene Huang. 2025. LLM-EvalRec: Hybrid Evaluation Metrics for Generative Recommenders. <sub>arXiv</sub> preprint arXiv:2504.01234 <sup>(2025).</sup>

[253] Rex Ying, Ruining He, Kaifeng Chen, Pongsakorn Eksombatchai, William L Hamilton, and Jure Leskovec. 2018. Graph Convolutional Neural Networks for Web-Scale Recommender Systems. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> <sub>24th</sub> <sub>ACM</sub> <sub>SIGKDD</sub>

International Conference on Knowledge Discovery and Data Mining<sup>.</sup> <sup>974–983.</sup>

[254] Da Yu, Peter Kairouz, Sewoong Oh, and Zheng Xu. 2024. Privacy-Preserving Instructions for Aligning Large Language Models. arXiv:2402.13659 [cs.CR] https://arxiv.org/abs/2402.13659

[255] Jing Yu, Jinhui Zhang, Weinan Liu, Qiang Zhou, and Wayne Xin Zhao. 2022. Modality-Aware Recommendation with <sup>Hierarchical</sup> <sup>Multi-Modal</sup> <sup>Attention.</sup> <sup>In</sup> Proceedings of the 45th International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR)<sup>.</sup>

[256] Yiwen Yuan, Zecheng Zhang, Xinwei He, Akihiro Nitta, Weihua Hu, Dong Wang, Manan Shah, Shenyang Huang, Blaž Stojanovič, Alan Krumholz, Jan Eric Lenssen, Jure Leskovec, and Matthias Fey. 2024. ContextGNN: Beyond Two-Tower Recommendation Systems. arXiv:2411.19513 [cs.IR] https://arxiv.org/abs/2411.19513

[257] Wenjia Zhai. 2024. Self-adaptive Multimodal Retrieval-Augmented Generation. arXiv:2410.11321 [cs.CL] https: //arxiv.org/abs/2410.11321

[258] Bowen Zhang, Yucheng Liu, Huan Wang, Peng Wu, and Yong Yu. 2024. Multi-Objective Optimization for Session-Based Recommendation via User Satisfaction Modeling. In <sub>Proceedings</sub> <sub>of</sub> <sub>the</sub> <sub>17th</sub> <sub>ACM</sub> <sub>International</sub> <sub>Conference</sub> <sub>on</sub> Web Search and Data Mining (WSDM)<sup>.</sup> <sup>ACM,</sup> <sup>153–161.</sup>

[259] Hao Zhang, Mingyue Cheng, Qi Liu, Junzhe Jiang, Xianquan Wang, Rujiao Zhang, Chenyi Lei, and Enhong Chen. 2025. A Comprehensive Survey on Cross-Domain Recommendation: Taxonomy, Progress, and Prospects. (2025). arXiv:2503.14110 [cs.IR] https://arxiv.org/abs/2503.14110

[260] Han Zhang, Lin Gui, Yu Lei, Yuanzhao Zhai, Yehong Zhang, Yulan He, Hui Wang, Yue Yu, Kam-Fai Wong, Bin Liang, and Ruifeng Xu. 2024. COPR: Continual Human Preference Learning via Optimal Policy Regularization. arXiv:2402.14228 [cs.LG] https://arxiv.org/abs/2402.14228

[261] Hongyu Zhang, Yankai Li, Xiang Ren, Yizhou Liang, and Jian-Yun Nie. 2021. Language models are open knowledge <sup>graphs.</sup> arXiv preprint arXiv:2104.10037 <sup>(2021).</sup>

[262] Hao Zhang and Elena Rossi. 2025. Privacy-Aware Personalization with Stateless Language Models. <sub>arXiv</sub> <sub>preprint</sub> arXiv:2503.09231 <sup>(2025).</sup>

[263] Kaiyuan Zhang, Siyuan Cheng, Hanxi Guo, Yuetian Chen, Zian Su, Shengwei An, Yuntao Du, Charles Fleming, Ashish Kundu, Xiangyu Zhang, and Ninghui Li. 2025. SOFT: Selective Data Obfuscation for Protecting LLM Fine-tuning against Membership Inference Attacks. arXiv:2506.10424 [cs.CR] https://arxiv.org/abs/2506.10424

[264] Ruisheng Zhang, Qi-dong Liu, Chun-Gui, Jia-Xuan Wei, and Huiyi-Ma. 2014. Collaborative Filtering for Recommender <sup>Systems.</sup> <sup>In</sup> 2014 Second International Conference on Advanced Cloud and Big Data<sup>.</sup> <sup>301–308.</sup> <sup>doi:10.1109/CBD.2014.47</sup>

[265] Shengzhe Zhang, Liyi Chen, Dazhong Shen, Chao Wang, and Hui Xiong. 2025. Hierarchical Time-Aware Mixture of Experts for Multi-Modal Sequential Recommendation. arXiv:2501.14269 [cs.IR] https://arxiv.org/abs/2501.14269

[266] Shuai Zhang, Lina Yao, Aixin Sun, and Quan Z. Sheng. 2021. Towards Multi-modal Retrospective Reasoning for <sup>Recommendation</sup> <sup>with</sup> <sup>Memory</sup> <sup>Networks.</sup> <sup>In</sup> Proceedings of the 27th ACM SIGKDD Conference on Knowledge Discovery <sub>and</sub> <sub>Data</sub> <sub>Mining</sub>. ACM, 2220–2228.

[267] Xinjie Zhang, Jintao Guo, Shanshan Zhao, Minghao Fu, Lunhao Duan, Guo-Hua Wang, Qing-Guo Chen, Zhao Xu, Weihua Luo, and Kaifu Zhang. 2025. Unified Multimodal Understanding and Generation Models: Advances, Challenges, and Opportunities. arXiv:2505.02567 [cs.CV] https://arxiv.org/abs/2505.02567

[268] Yijing Zhang, Dyah Adila, Changho Shin, and Frederic Sala. 2025. Personalize Your LLM: Fake it then Align it. In Findings of the Association for Computational Linguistics: NAACL 2025<sup>,</sup> <sup>Luis</sup> <sup>Chiruzzo,</sup> <sup>Alan</sup> <sup>Ritter,</sup> <sup>and</sup> <sup>Lu</sup> <sup>Wang</sup> <sup>(Eds.).</sup> Association for Computational Linguistics, Albuquerque, New Mexico, 7287–7301. doi:10.18653/v1/2025.findingsnaacl.407

[269] Yifan Zhang, Qiang Liu, et al. 2023. M2Rec: Multi-Scale Mamba for Sequential Recommendation. <sub>arXiv</sub> <sub>preprint</sub> arXiv:2311.10320 <sup>(2023).</sup>

[270] Henghao Zhao, Ge-Peng Ji, Rui Yan, Huan Xiong, and Zechao Li. 2025. VideoExpert: Augmented LLM for Temporal Sensitive Video Understanding. arXiv:2504.07519 [cs.CV] https://arxiv.org/abs/2504.07519

[271] Hong Zhao, Qiang Liu, and Fei Wu. 2024. StableRec: Drift-Robust Representation Learning for Long-Term Recom <sup>mendation.</sup> IEEE Transactions on Knowledge and Data Engineering <sup>(2024).</sup> <sup>to</sup> <sup>appear.</sup>

[272] Lijuan Zhao and Felix Meier. 2025. Continual Embedding Learning for Streaming Recommenders. <sub>Journal</sub> <sub>of</sub> <sub>Machine</sub> Learning Systems <sup>(2025).</sup>

[273] Siyan Zhao, Mingyi Hong, Yang Liu, Devamanyu Hazarika, and Kaixiang Lin. 2025. Do LLMs Recognize Your Preferences? Evaluating Personalized Preference Following in LLMs. arXiv:2502.09597 [cs.LG] https://arxiv.org/abs/ 2502.09597

[274] Xiaoxue Zhao, Shuchang Zhang, Zheng Zhang, and Qi Wang. 2022. Understanding Short Video Pre-Ranking: A Case <sup>Study</sup> <sup>on</sup> <sup>TikTok.</sup> <sup>In</sup> Proceedings of the 28th ACM SIGKDD Conference on Knowledge Discovery and Data Mining<sup>.</sup> <sup>ACM,</sup> 4200–4210. doi:10.1145/3534678.3539493

[275] Bowen Zheng, Xiang Li, and Wei Zhan. 2023. UserGPT-Sim: Large-Language-Model Simulation of User Feedback for <sup>Recommender</sup> <sup>Evaluation.</sup> <sup>In</sup> Proceedings of the Web Conference 2023 (WWW)<sup>.</sup>

[276] Kai Zheng, Qingfeng Sun, Can Xu, Peng Yu, and Qingwei Guo. 2024. Towards a Unified Paradigm: Integrating Recommendation Systems as a New Language in Large Models. arXiv:2412.16933 [cs.IR] https://arxiv.org/abs/2412. 16933

[277] Can Zhou, Yabo Zhang, Xuemeng Wu, Xinyang Li, Minlie Wang, and Jie Tang. 2023. GPT4Rec: Generative Pre-Trained Transformer for Personalized Recommendation and User Behavior Synthesis. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2305.13356</sub> (2023). https://arxiv.org/abs/2305.13356

[278] Lin Zhou and Haruki Yamamoto. 2025. DPGen: Diferentially Private Retrieval-Augmented Generation for Recom <sup>mendation.</sup> <sup>In</sup> Proceedings of the 2025 ACM Conference on Recommender Systems (RecSys)<sup>.</sup>

[279] Mingwei Zhou, Fan Liu, Lei Zheng, Jiawei Song, and Philip S. Yu. 2025. OmniFM: Unified Multimodal Foundation Models for Cross-Domain Recommendation. Manuscript submitted for publication. To appear.

[280] Peter Zhou, Nathan Johnston, Colin Rafel, Noam Shinn, Nisan Stiennon, Daniel Ziegler, Geofrey Irving, and Paul Christiano. 2023. LIMA: Less is More for Alignment. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:2305.11206</sub> (2023).

[281] Xudong Zhou, Canwen Xu, Zekun Liu, Yujia Yao, Wenxuan Zhang, Zhiyang Zhang, Maosong Sun, Yuxuan Zhang, and Zhiyuan Liu. 2023. LLMJudge: Empowering Large Language Models to Judge LLM-Generated Content. In <sub>Proceedings</sub> of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP)<sup>.</sup> <sup>Association</sup> <sup>for</sup> <sup>Computational</sup> Linguistics, 10898–10916.

[282] Yunhong Zhou, Dennis Wilkinson, Robert Schreiber, and Rong Pan. 2008. Large-scale parallel collaborative filtering <sup>for</sup> <sup>the</sup> <sup>Netflix</sup> <sup>prize.</sup> <sup>In</sup> Proceedings of the 4th international conference on Algorithmic Aspects in Information and <sub>Management</sub> <sub>(AAIM)</sub>. Springer, 337–348.

[283] Kaijie Zhu, Jindong Wang, Jiaheng Zhou, Zichen Wang, Hao Chen, Yidong Wang, Linyi Yang, Wei Ye, Yue Zhang, Neil Zhenqiang Gong, and Xing Xie. 2024. PromptRobust: Towards Evaluating the Robustness of Large Language Models on Adversarial Prompts. (2024). arXiv:2306.04528 [cs.CL] https://arxiv.org/abs/2306.04528

[284] Yaochen Zhu, Chao Wan, Harald Steck, Dawen Liang, Yesu Feng, Nathan Kallus, and Jundong Li. 2025. Collaborative Retrieval for Large Language Model-based Conversational Recommender Systems. arXiv:2502.14137 [cs.IR] https: //arxiv.org/abs/2502.14137

[285] Jingming Zhuo, Songyang Zhang, Xinyu Fang, Haodong Duan, Dahua Lin, and Kai Chen. 2024. ProSA: Assessing and Understanding the Prompt Sensitivity of LLMs. arXiv:2410.12405 [cs.CL] https://arxiv.org/abs/2410.12405

[286] Daniel M Ziegler, Nisan Stiennon, Jefrey Wu, Tom B Brown, Alec Radford, Dario Amodei, Paul Christiano, and Geofrey Irving. 2019. Fine-tuning language models from human preferences. <sub>arXiv</sub> <sub>preprint</sub> <sub>arXiv:1909.08593</sub> (2019).

[287] Pablo Zivic, Hernan Vazquez, and Jorge Sánchez. 2024. Scaling Sequential Recommendation Models with Transformers. <sup>In</sup> Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval <sub>(SIGIR</sub> <sub>2024)</sub>. ACM, 1567–1577. doi:10.1145/3626772.3657816

[288] Barret Zoph, Nan Du, Neil Houlsby, Dmitry Lepikhin, Orhan Firat, Liam Fedus, Cyprien de Masson d’Autume, Yu Emma Wang, Yanping Huang, Tao Wang, Yanqi Zhou, Dehao Zhao, Andrew M Dai, Adams Wei Yu, Zhifeng Chen, Zhifeng Zhang, Quoc V Le, and Noam Shazeer. 2022. Designing Efective Sparse Expert Models. <sub>arXiv</sub> <sub>preprint</sub> arXiv:2202.08906 <sup>(2022).</sup>

[289] Caixia Zou and Fanyu Zhang. 2022. Algorithm Interpretation Right—The First Step to Algorithmic Governance. <sub>Beijing</sub> <sub>Law</sub> <sub>Review</sub> 13, 227–246. doi:10.4236/blr.2022.132015

## Towards Eficient Certification of Maritime Remote Operation Centers – Ansatz zur efizienten Zertifizierung von maritimen Fernsteuerungszentren

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

## Efficient Cold-Start Recommendation via BPE Token-Level Embedding Initialization with LLM

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

## Massive Memorization with Hundreds of Trillions of Parameters for Sequential Transducer Generative Recommenders

# Massive Memorization with Hundreds of Trillions of Parameters for Sequential Transducer Generative Recommenders

Zhimin Chen<sup>1†\*</sup>, Chenyu Zhao<sup>1†</sup>, Ka Chun Mo<sup>1</sup>, Yunjiang Jiang<sup>1</sup>, Jane H. Lee<sup>2‡</sup>, Khushhall Chandra Mahajan<sup>1</sup>, Ning Jiang<sup>1</sup>, Kai Ren<sup>1</sup>, Jinhui Li<sup>1\*</sup>, Wen-Yun Yang<sup>1\*</sup>

<sup>1</sup>Meta, <sup>2</sup>Yale University

## Abstract

Modern large-scale recommendation systems rely heavily on user interaction history sequences to enhance the model performance. The advent of large language models and sequential modeling techniques, particularly transformer-like architectures, has led to significant advancements recently (e.g., HSTU, SIM, and TWIN models). While scaling to ultra-long user histories (10k to 100k items) generally improves model performance, it also creates significant challenges on latency, queries per second (QPS) and GPU cost in industry-scale recommendation systems. Existing models do not adequately address these industrial scalability issues. In this paper, we propose a novel two-stage modeling framework, namely VIrtual Sequential Target Attention (VISTA), which decomposes traditional target attention from a candidate item to user history items into two distinct stages: (1) user history summarization into a few hundred tokens; followed by (2) candidate item attention to those tokens. These summarization token embeddings are then cached in storage system and then utilized as sequence features for downstream model training and inference. This novel design for scalability enables VISTA to scale to lifelong user histories (up to one million items) while keeping downstream training and inference costs fixed, which is essential in industry. Our approach achieves significant improvements in ofline and online metrics and has been successfully deployed on an industry leading recommendation platform serving billions of users.

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

## 2 Related Work

Hierarchical Sequential Transduction Unit (HSTU). A significant advancement in this area is the Hierarchical Sequential Transduction Unit (HSTU) (Zhai et al., 2024), which reframes recommendation as a sequential transduction problem. Designed specifically for high-cardinality, non-stationary streaming recommendation data, HSTU surpasses traditional models in both accuracy and eficiency. This architecture allows recommendation systems to scale to trillions of parameters, leading to substantial gains in predictive performance.

Transformer Architectures in Recommendation Systems. The application of transformer architectures in recommendation systems has been explored extensively. By leveraging the self-attention mechanism, transformers can model complex user-item interactions over time, facilitating more nuanced and personalized recommendations (Subbiah and Aggarwal, 2024). The Deep Interest Network (DIN) (Zhou et al., 2018) and its follow-up work, Searchbased Interest Modeling (SIM) (Pi et al., 2020; Chang et al., 2023; Si et al., 2024), leverage lifelong sequential behavior data. This approach employs search-based mechanisms, also known as General Search Units (GSUs), to select a small subset of relevant interactions from the user’s historical sequence that are pertinent to the target item followed by a standard transformer network, referred to as Exact Search Units (ESUs), to compute the final target item representation. Notably, this method enables the modeling of user behavior data with lengths reaching up to hundreds of thousands (Pi et al., 2020). Other methods (Liu et al., 2023) preprocess user histories into groups and attend to the group embeddings, and separately attend to subsequences in the user history relevant to the target item.

Linear Complexity Attention Mechanisms. Apart from Flash Attention (Dao et al., 2022; Dao, 2023) that is designed to improve the eficiency of the softmax attention mechanisms, there is a new trend to explore linear complexity attention mechanisms. Katharopoulos et al. (2020) first proposes linear attention. By applying matrix multiplication associative property, it enables a change in computation order from $( Q K ^ { T } ) V$ to $Q ( K ^ { T } V )$ , reducing computation complexity from $O ( N ^ { 2 } )$ to O(N) with respect to sequence length N . Recently, Lightning Attention v1 (Qin et al., 2024a) and v2 (Qin et al., 2024b) propose a light network which contains Gated Linear Attention (GLA) and Simple Gated Linear Unit (SGLU) to make linear attention more practical. Another branch of linear complexity work, namely state space model (SSM), has been widely studied. Mamba (Gu and Dao, 2024) is a pioneering work in SSM and widely used in many real-world applications, followed by Hydra (Hwang et al., 2024) which is the double-headed version of Mamba to address non-causal scenarios.

## 3 Method

Here we introduce the details of VISTA’s two cascaded modules: ultra-long user interaction history (UIH) sequence summarization and target-aware attention, followed by details of a practical linear complexity self-attention and generative sequence reconstruction loss. We then explain how VISTA’s design enables the scaling, storage, and processing of industry-scale user history sequences through its embedding delivery system.

## 3.1 Model Architecture Overview

As illustrated in Figure 2, the VISTA architecture employs distinct workflows for training and inference. During training, the computationally expensive UIH summarization module runs to generate summary embeddings. These embeddings are then quantized and exported to a large key-value cache in O(100) terabytes to $O ( 1 )$ petabytes. For inference, this expensive step is bypassed entirely. Instead, the pre-computed embeddings are simply retrieved from the cache and dequantized with minimal distortion. The final component, the target attention module, operates in both phases, using the summarization embeddings and candidate item features to make predictions.

## 3.2 Ultra-long UIH Sequence Summarization

In the first stage, we utilize self-attention with virtual seed embeddings to summarize ultra-long UIH sequences. These virtual seeds are initialized randomly as shared parameters across users, which are updated with the model through its interaction with the UIH sequence in the summarization module. The output of the summarization module can be interpreted as user embeddings, encoding individual personalized preferences to inform recommendations. Figure 3 visualizes these summarization embeddings, projected onto the first 2 principal components by principal component analysis $\mathrm { ( P C A ) }$ . We can clearly see the separation for users of diferent countries, with US and Canada overlapping, which is expected.

![](images/aea9801365172d422b6052ffca12ab4dea59ef5b107528be461e13cdcb8cc950.jpg)  
Figure 3: Visualization of UIH summarization embeddings.

However, typical softmax attentions sufer from

$O ( N ^ { 2 } )$ time complexity, which is prohibitive when dealing with ultra-long sequences $( N > \mathrm { { 1 0 } } k )$ . Therefore, we propose quasi-linear attention (QLA), a linear time complexity $O ( N )$ self-attention mechanism to overcome this issue.

## 3.2.1 Linear Attention with Candidate Items for Recommendation

With the emergence of Large Language Models (LLMs), researchers have proposed some linear complexity attention algorithms to accelerate transformer blocks (Katharopoulos et al., 2020; Qin et al., 2024a;b; Han et al., 2024). However in recommendation systems, unlike the text sequences in LLM, a strict rule is that the candidates cannot attend each other, since it introduces label leakage due to the fact that the logged candidates typically only form a small subset of the input candidates during inference. Therefore, we propose a linear-complexity self attention mechanism that avoids attention among candidates.

The typical softmax self attention for a UIH sequence $S$ can be formulated as follows

$$
\operatorname{SoftmaxAttn} (\mathrm{S} \Rightarrow_ {\text { full }} \mathrm{S}) = \operatorname{RowSoftmax} (Q K ^ {\top}) V
$$

where $Q , K$ and V have shape $( L , d )$ and $L$ is the sequence length. Then the original linear attention (Katharopoulos et al., 2020) for a UIH sequence $S$ can be written similarly as follows

$$
\begin{array}{c} \operatorname{LinAttn} (\mathrm{S} \Rightarrow_ {\text {full}} \mathrm{S}) = \operatorname{RowNormalize} (Q K ^ {\top}) V \\ = Q (K ^ {\top} V) / \operatorname{RowSum} (Q K ^ {\top}) = Q (K ^ {\top} V) / (Q \operatorname{ColSum} (K) ^ {\top}). \end{array}\tag{1}
$$

![](images/561f618fea44ccee79c870311f1ba35ce8d3a6a0f9f0a888a45e1131acc09097.jpg)  
Figure 4: The QLU module.

![](images/690743689b74daa8d1bc463a3cb4642717172f65145f2dd03e3329127dda29b1.jpg)  
Figure 5: Generative reconstruction loss.

Note that division / here stands for broadcast division along the rows. The above can be applied to full (bi-directional) self-attention.

In recommendation models, we also have target (candidate) items, let’s denote them by T . Then we want to compute target attention of T against K and V .

$$
\mathrm{LinAttn} (\mathrm{T} \Rightarrow_ {\mathrm{full}} \mathrm{S}) = \mathrm{T} (\mathrm{K} ^ {\top} \mathrm{V}) / (\mathrm{T} \operatorname{ColSum} (\mathrm{K}) ^ {\top}).\tag{2}
$$

Note that candidates cannot attend to each other. This is a strict rule in recommendation systems otherwise the model training will fail due to the leakage between candidate items. It gets slightly trickier if we also want each candidate to attend to itself. Instead of $T T ^ { \top } T$ , the contribution due to the self attention of each target item to itself is given by

$$
\mathrm{LinAttn} (\mathrm{T} \Rightarrow_ {\mathrm{individual}} \mathrm{T}) = \mathrm{Diag} (\mathrm{TT} ^ {\top}) \mathrm{T}.\tag{3}
$$

## 3.2.2 Quasi-linear Attention for Recommendation

Despite its eficiency, some previous works (Han et al., 2024; 2023) prove that linear attention sufers from insuficient expressive power, making it impractical for real applications. In this section, we introduce quasi-linear attention (QLA) as an empirically efective linear attention algorithm for recommendation. This quasi-linear attention introduces more non-linear complexity in attention computation, addressing the issue of expressive power.

The quasi-linear attention contains two parts: Quasi Linear Unit (QLU) module and Simple Gated Linear Unit (SGLU) module. The QLU module aims to model the interaction of Q, K, V matrices with SiLU non-linear activation as shown in Figure 4. For the SGLU module, we use the same gated function as TransNormerLLM (Qin et al., 2024a).

Accordingly, we need to slightly modify the above linear attention formulation to accommodate this QLU module. For the self attention part we let the user history items attend to one another. Similar as in HSTU (Zhai et al., 2024), SASRec (Kang and McAuley, 2018), and Pinnerformer (Pancha et al., 2022), usually the causal self-attention approach via a triangular mask is used. In our case, we did not find significant diference between causal and full self attention, since the user history items merely serve as features for the final candidate prediction task – their temporal causality is not a strict requirement. Let φ denote a non-linear activation function (we use SiLU in our experiments), then the full self quasi-linear attention modified from Eq. (1) is as follows.

$$
O [ S ] = \varphi (Q [ S ]) \varphi (\varphi (K [ S ]) ^ {\top} V [ S ])
$$

where [S] denotes the source (user history) portion of the sequence. Note that we remove the RowNormalize operation, similarly as in Lightning Attention (Qin et al., 2024a;b).

For the target portion of the query sequence embeddings, we can similarly apply φ-linear attention between $Q [ T ]$ and $\dot { K } [ S ] , V [ S ]$ . However to be consistent with the self-attention semantics, we also include an extra term that captures attention to the target item itself. Thus, the final formula for the target portion of the quasi-linear attention, modified from Eq. (2) and (3) is given by

$$
O [ T ] = \varphi (Q [ T ]) \varphi (\varphi (K [ S ]) ^ {\top} V [ S ]) + \Delta (\varphi (Q [ T ]), \varphi (K [ T ])) V [ T ].
$$

Here $\begin{array} { r } { \Delta ( X , Y ) _ { i j } : = \sum _ { k } X _ { i k } Y _ { i k } \delta _ { i j } } \end{array}$ stands for putting the row-wise dot product between the two matrices $\bar { X }$ and $Y$ of shape $n \times m$ on the diagonal of a square matrix of shape $n \times n$ In order to implement the quasi-linear attention eficiently using the Triton language (Tillet et al., 2019) for optimized GPU computation performance, we also calculate the gradient of the final loss function with respect to the input tensors $\check { Q } [ S ] , Q [ T ] , K [ S ] , K [ T ] , \check { V } [ S ] , V [ T ]$ in terms of the gradient with respect to the output tensor ${ \mathrm { \bar { \it O } } } [ S ] , { \mathrm { \bar { \it O } } } [ T ]$ in Appendix B.

## 3.2.3 Generative Sequence Reconstruction Loss

To further enhance the memorization efects, we also introduce a reconstruction loss (see Fig. 5) to encourage the sequence summarization to fully reproduce the UIH sequence, which we find particularly useful to improve VISTA’s performance. Intuitively, to reconstruct the i-th UIH item embedding, we are using all the seed embeddings and the UIH item embeddings up to the (i − 1)-th position. A natural way to accomplish this is via the decoder network, such as the causal transformer decoder, without the softmax layer. Formally,

$$
(t _ {1}, \dots , t _ {k}, v _ {1}, \dots , v _ {M}) = \operatorname{Decoder} (s _ {1}, \dots , s _ {k}, u _ {1}, \dots , u _ {M}).
$$

where $s _ { 1 } , \ldots , s _ { k }$ are the personalized seed embeddings, and $u _ { 1 } , \ldots , u _ { M }$ are the UIH item embeddings. We can feed their concatenation through the causal softmax attention block (or any other transformer block) to get the output embeddings concatenated as $t _ { 1 } , \ldots , t _ { k }$ and $v _ { 1 } , \ldots , v _ { M }$ where k is the number of seeds and M the length of the user history sequence. Then we can simply form the of-by-one mean square error of the $v _ { i } \mathrm { { s } }$ with the $u _ { i } \mathrm { ^ { * } s }$ as the construction loss as $\begin{array} { r } { L _ { \mathrm { r e c o n s t r u c t } } = \sum _ { i = 1 } ^ { M - 1 } \| v _ { i } - u _ { i + 1 } \| _ { 2 } ^ { 2 } } \end{array}$

Since causal transformer block ensures that the output embedding $v _ { i }$ only depends on $u _ { 1 } , \ldots , u _ { i } .$ , there is no leak of information from $u _ { i + 1 }$ to $v _ { i }$ . This forces the personalized seed embeddings $s _ { i }$ to maximize information retained of the user history sequence $u _ { 1 } , \ldots , u _ { M }$ Similar ideas have roots in the Variational Auto-Encoder (Kingma and Welling, 2022), and have appeared in the context of transformer networks recently (Henderson and Fehr, 2022). However to the best of our knowledge, there has not been any explicit use in recommendation. For more discussion on this reconstruction loss, see Appendix C.

## 3.3 Target-aware Attention

As shown in Figure $^ { 2 , }$ any attention network can technically be used for the target-aware attention stage. Because this step is computationally inexpensive compared to sequence summarization, we selected a standard $\overset { \mathcal { ( ) } } { O } ( N ^ { 2 } )$ transformer block, which delivers excellent performance on the compact summary sequences.

## 4 Embedding Delivery System

We emphasize that the VISTA framework is not merely a theoretical model, but a novel industrial model system co-design to support large scale user interaction history sequence learning that can be deployed into the real industry infrastructure with reasonable cost.

Figure 6 outlines the system’s end-to-end architecture, which comprises three main stages: (1) online training of the source model using training data stream, (2) delivery of sequence summarization embeddings to downstream models via two routes: a real-time message queue, e.g., Kafka (Kreps et al., 2011) and persistent storage, e.g., Hive (Thusoo et al., 2009), and (3) serving embeddings through a geographically replicated in-memory key-value store. In our system, we update the summarization embeddings on a 2-hour cadence, which was shown to have similar performance compared to using the summarization module directly in online $\mathrm { A } / \mathrm { B }$ tests. This design ensures both real-time performance and scalability for industrial applications. For scalability, we deliberately compress the user interaction history sequence to O(100) terabytes level, making it feasible to deploy to existing systems.

![](images/f4fec74a64978642c34bef42dfa1a52c2b8e7b0fb777766a7cf99703ef52fd3d.jpg)  
Figure 6: An overview of VISTA sequence summarization embedding delivery system.

## 5 Experiments

## 5.1 Datasets and Experimental Setup

The proposed VISTA framework is designed for a large scale real-world dataset, where one needs to train hundreds of billions of examples per day and each user has a history which contains hundreds of thousands of items. While existing public datasets are usually much smaller, we compare our method against several baselines on public datasets in addition to reporting results on real production data.

## 5.1.1 Public Dataset and Industrial-Scale Dataset

We first compare the efectiveness of VISTA against several baseline models on public datasets Amazon-Electronics <sup>1</sup> and KuaiRand-1K <sup>2</sup>. To focus mainly on the efectiveness of the attention mechanism, we compare VISTA against baselines in replacing the attention layers in a common model architecture. All models are implemented, trained, and evaluated under the FuxiCTR <sup>3</sup> framework, focusing on click-through rate prediction. Additionally, we introduce a Minimal Production dataset from real production data, compatible with FuxiCTR having minimal features but with longer sequences up to 2,000.

For industrial-scale ofline experimentation, we construct full training and evaluation samples from real production data, with several metrics for engagement, which we denote by “C-Task”, “E1-Task”, etc. We use 3-day data as the training set and the next 1-day data as the evaluation set in our ofline experiment. The scale of training examples per day is at O(10) billion level. The average and maximum UIH sequence lengths are 7,000 and 16,000, respectively. Note that we deploy the model with 12,000 UIH sequence length in online experiments, but we only use 2,000 in ofline experiments due to GPU resource constraints.

Table 1: Dataset Statistics

<table><tr><td>Dataset</td><td>Mean Seq.</td><td>Max Seq.</td></tr><tr><td>Amazon-Electronics</td><td>8.93</td><td>429</td></tr><tr><td>KuaiRand-1K</td><td>225.20</td><td>256</td></tr><tr><td>Simplified Prod</td><td>1528.18</td><td>2,000</td></tr><tr><td>Industrial-Scale Data</td><td>7,000</td><td>16,000</td></tr></table>

Table 2: Comparisons on public and Minimal Production datasets. $\mathrm { V I S T A  – w / – Q L A }$ and $\mathrm { V I S T A  – w / o \mathrm { - } Q L A }$ are the VISTA model with and without quasi-linear attention, respectively.<sup>4</sup>

<table><tr><td rowspan="2">Models</td><td colspan="2">Amazon</td><td colspan="2">KuaiRand</td><td colspan="2">Minimal Production</td></tr><tr><td>AUC (↑)</td><td>NE (↓)</td><td>AUC (↑)</td><td>NE (↓)</td><td>AUC (↑)</td><td>NE (↓)</td></tr><tr><td>DIN</td><td> $0.873 \pm 8e^{-4}$ </td><td> $0.656 \pm 1e^{-4}$ </td><td> $\underline{0.744 \pm 0.003}$ </td><td> $0.864 \pm 0.005$ </td><td> $0.632 \pm 0.02$ </td><td> $1.048 \pm 0.033$ </td></tr><tr><td>TTSN</td><td> $0.877 \pm 0.005$ </td><td> $0.644 \pm 0.010$ </td><td> $\underline{0.740 \pm 0.003}$ </td><td> $0.869 \pm 0.004$ </td><td> $0.648 \pm 0.005$ </td><td> $1.139 \pm 0.156$ </td></tr><tr><td>MHA</td><td> $0.881 \pm 1e^{-4}$ </td><td> $0.634 \pm 0.002$ </td><td> $0.743 \pm 0.001$ </td><td> $\underline{0.863 \pm 0.005}$ </td><td> $0.630 \pm 0.018$ </td><td> $1.049 \pm 0.041$ </td></tr><tr><td>SASRec</td><td> $0.884 \pm 4e^{-4}$ </td><td> $0.627 \pm 0.001$ </td><td> $0.742 \pm 0.003$ </td><td> $0.868 \pm 0.007$ </td><td> $0.605 \pm 0.020$ </td><td> $1.129 \pm 0.134$ </td></tr><tr><td>HSTU</td><td> $0.884 \pm 0.001$ </td><td> $0.628 \pm 0.001$ </td><td> $0.743 \pm 0.001$ </td><td> $0.863 \pm 1e^{-5}$ </td><td> $\mathbf{0.668 \pm 0.011}$ </td><td> $1.099 \pm 0.048$ </td></tr><tr><td>VISTA-w/o-QLA</td><td> $\mathbf{0.886 \pm 0.002}$ </td><td> $\mathbf{0.621 \pm 0.005}$ </td><td> $\mathbf{0.744 \pm 0.001}$ </td><td> $\mathbf{0.863 \pm 0.003}$ </td><td> $0.627 \pm 0.016$ </td><td> $\mathbf{1.038 \pm 0.05}$ </td></tr><tr><td>VISTA-w/-QLA</td><td> $0.884 \pm 0.005$ </td><td> $0.623 \pm 0.003$ </td><td> $0.743 \pm 4e^{-4}$ </td><td> $0.864 \pm 0.001$ </td><td> $0.632 \pm 0.013$ </td><td> $1.062 \pm 0.076$ </td></tr></table>

![](images/ad06f4736d5abe72f114fd8f884dd9e42910c6d0c5881720d3d556766beeab94.jpg)

![](images/a083eb1c5daacf3c2ea2fd7c541cca0bbd605adadc72c6bd6a770c0d2ee5e494.jpg)

![](images/0a8480f8cae73146cf07c06699d09499f6c11c2b1955aef611e6d61493227f6b.jpg)  
Figure 7: Ablation study on quasi-linear attention by varying sequence length.

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

## Acknowledgement

This work results from a large cross organization collaboration. It would not be possible without contributions from the collaborators and supports from the leaderships as follows (alphabetic order): Zheng-Yong Ang, David Bauer, Connor Chen, Shouwei Chen, Siqiao Chen, Huihui Cheng, Ek Kheng Chung, Litao Deng, Shilin Ding, Chenhao Feng, Kevin Goulding, Liang Guo, Mengyue Hang, Maxwell Lin-He, Xiaoxin He, Chufeng Hu, Jizhou Huang, Yanzun Huang, Han Jiang, Justin Khim, Emma Lin, Zihan Li, Yang Liu, Yining Liu, Li Lu, Wenhan Lyu, Jing Ma, Matt Ma, Jing Qian, Rui Qiao, Chuyu Qiu, Yongxiong Ren, Xinyue Shen, Daisy Shi, Hongzheng Shi, Ge Song, Yisong Song, Wanting Tan, Hao Wan, Meihong Wang, Yanhong Wu, Hong Yan, Yihang Yang, Chuanwei Yi, Christina You, Haoli Zhang, Rui Zhang, Yue Zhang, John Zheng, Xinye Zheng, Lizhen Zhu, Maggie Zhuang.

## References

Jianxin Chang, Chenbin Zhang, Zhiyi Fu, Xiaoxue Zang, Lin Guan, Jing Lu, Yiqun Hui, Dewei Leng, Yanan Niu, Yang Song, and Kun Gai. 2023. TWIN: TWo-stage Interest Network for Lifelong User Behavior Modeling in CTR Prediction at Kuaishou. arXiv:2302.02352 [cs.IR] https://arxiv.org/abs/2302.02352

Paul Covington, Jay Adams, and Emre Sargin. 2016. Deep Neural Networks for YouTube Recommendations. In Proceedings of the 10th ACM Conference on Recommender Systems (Boston, Massachusetts, USA) (RecSys ’16). Association for Computing Machinery, New York, NY, USA, 191–198. doi:10.1145/2959100.2959190

Tri Dao. 2023. FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning. arXiv:2307.08691 [cs.LG] https://arxiv.org/abs/2307.08691

Tri Dao, Daniel Y. Fu, Stefano Ermon, Atri Rudra, and Christopher Ré. 2022. FlashAttention: Fast and Memory-Eficient Exact Attention with IO-Awareness. arXiv:2205.14135 [cs.LG] https://arxiv.org/abs/2205.14135

Chongming Gao, Shijun Li, Yuan Zhang, Jiawei Chen, Biao Li, Wenqiang Lei, Peng Jiang, and Xiangnan He. 2022. KuaiRand: An Unbiased Sequential Recommendation Dataset with Randomly Exposed Videos. In Proceedings of the 31st ACM International Conference on Information and Knowledge Management (Atlanta, GA, USA) (CIKM ’22). 3953–3957. doi:10.1145/3511808.3557624

Albert Gu and Tri Dao. 2024. Mamba: Linear-Time Sequence Modeling with Selective State Spaces. arXiv:2312.00752 [cs.LG] https://arxiv.org/abs/2312.00752

Dongchen Han, Xuran Pan, Yizeng Han, Shiji Song, and Gao Huang. 2023. FLatten Transformer: Vision Transformer using Focused Linear Attention. arXiv:2308.00442 [cs.CV] https://arxiv.org/abs/2308.00442

Dongchen Han, Yifan Pu, Zhuofan Xia, Yizeng Han, Xuran Pan, Xiu Li, Jiwen Lu, Shiji Song, and Gao Huang. 2024. Bridging the Divide: Reconsidering Softmax and Linear Attention. arXiv:2412.06590 [cs.CV] https://arxiv.org/abs/2412.06590

Xinran He, Junfeng Pan, Ou Jin, Tianbing Xu, Bo Liu, Tao Xu, Yanxin Shi, Antoine Atallah, Ralf Herbrich, Stuart Bowers, et al. 2014. Practical lessons from predicting clicks on ads at facebook. In Proceedings of the eighth international workshop on data mining for online advertising. 1–9.

James Henderson and Fabio Fehr. 2022. A Variational AutoEncoder for Transformers with Nonparametric Variational Information Bottleneck. arXiv:2207.13529 [cs.LG] https: //arxiv.org/abs/2207.13529

Yupeng Hou, Jiacheng Li, Zhankui He, An Yan, Xiusi Chen, and Julian McAuley. 2024. Bridging Language and Items for Retrieval and Recommendation. arXiv preprint arXiv:2403.03952 (2024).

Sukjun Hwang, Aakash Lahoti, Tri Dao, and Albert Gu. 2024. Hydra: Bidirectional State Space Models Through Generalized Matrix Mixers. arXiv:2407.09941 [cs.LG] https: //arxiv.org/abs/2407.09941

Wang-Cheng Kang and Julian McAuley. 2018. Self-Attentive Sequential Recommendation. arXiv:1808.09781 [cs.IR] https://arxiv.org/abs/1808.09781

Angelos Katharopoulos, Apoorv Vyas, Nikolaos Pappas, and François Fleuret. 2020. Transformers are rnns: Fast autoregressive transformers with linear attention. In International conference on machine learning. PMLR, 5156–5165.

Diederik P Kingma and Max Welling. 2022. Auto-Encoding Variational Bayes. arXiv:1312.6114 [stat.ML] https://arxiv.org/abs/1312.6114

Yehuda Koren, Robert Bell, and Chris Volinsky. 2009. Matrix Factorization Techniques for Recommender Systems. Computer 42, 8 (2009), 30–37. doi:10.1109/MC.2009.263

Jay Kreps, Neha Narkhede, Jun Rao, et al. 2011. Kafka: A distributed messaging system for log processing. In Proceedings of the NetDB, Vol. 11. Athens, Greece, 1–7.

Qi Liu, Xuyang Hou, Haoran Jin, Jin Chen, Zhe Wang, Defu Lian, Tan Qu, Jia Cheng, and Jun Lei. 2023. Deep Group Interest Modeling of Full Lifelong User Behaviors for CTR Prediction. CoRR (2023).

Nikil Pancha, Andrew Zhai, Jure Leskovec, and Charles Rosenberg. 2022. PinnerFormer: Sequence Modeling for User Representation at Pinterest. arXiv:2205.04507 [cs.LG] https: //arxiv.org/abs/2205.04507

Qi Pi, Xiaoqiang Zhu, Guorui Zhou, Yujing Zhang, Zhe Wang, Lejian Ren, Ying Fan, and Kun Gai. 2020. Search-based User Interest Modeling with Lifelong Sequential Behavior Data for Click-Through Rate Prediction. In Proceedings of the 29th ACM International Conference on Information & Knowledge Management (CIKM). ACM. https://doi. org/10.1145/3340531.3412744

Zhen Qin, Dong Li, Weigao Sun, Weixuan Sun, Xuyang Shen, Xiaodong Han, Yunshen Wei, Baohong Lv, Xiao Luo, Yu Qiao, and Yiran Zhong. 2024a. TransNormerLLM: A Faster and Better Large Language Model with Improved TransNormer. arXiv:2307.14995 [cs.CL] https://arxiv.org/abs/2307.14995

Zhen Qin, Weigao Sun, Dong Li, Xuyang Shen, Weixuan Sun, and Yiran Zhong. 2024b. Lightning Attention-2: A Free Lunch for Handling Unlimited Sequence Lengths in Large Language Models. arXiv:2401.04658 [cs.CL] https://arxiv.org/abs/2401.04658

Badrul Sarwar, George Karypis, Joseph Konstan, and John Riedl. 2001. Item-based collaborative filtering recommendation algorithms. In Proceedings of the 10th International Conference on World Wide Web (Hong Kong, Hong Kong) (WWW ’01). Association for Computing Machinery, New York, NY, USA, 285–295. doi:10.1145/371920.372071

Zihua Si, Lin Guan, Zhongxiang Sun, Xiaoxue Zang, Jing Lu, Yiqun Hui, Xingchao Cao, Zeyu Yang, Yichen Zheng, Dewei Leng, Kai Zheng, Chenbin Zhang, Yanan Niu, Yang Song, and Kun Gai. 2024. TWIN V2: Scaling Ultra-Long User Behavior Sequence Modeling for Enhanced CTR Prediction at Kuaishou. In Proceedings of the 33rd ACM International Conference on Information and Knowledge Management (CIKM ’24). ACM, 4890–4897. doi:10.1145/3627673.3680030

Anushya Subbiah and Vikram Aggarwal. 2024. Transformers in music recommendation. https://research.google/blog/transformers-in-music-recommendation/.

Ashish Thusoo, Joydeep Sen Sarma, Namit Jain, Zheng Shao, Prasad Chakka, Suresh Anthony, Hao Liu, Pete Wyckof, and Raghotham Murthy. 2009. Hive: a warehousing solution over a map-reduce framework. Proceedings of the VLDB Endowment 2, 2 (2009), 1626–1629.

Philippe Tillet, H. T. Kung, and David Cox. 2019. Triton: An Intermediate Language and Compiler for Tiled Neural Network Computations. In Proceedings of the 3rd ACM SIGPLAN International Workshop on Machine Learning and Programming Languages (MAPL ’19). ACM, 10. doi:10.1145/3315508.3329973

Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, and Illia Polosukhin. 2017. Attention Is All You Need. In Advances in Neural Information Processing Systems (NeurIPS). https://papers.nips.cc/paper/ 7181-attention-is-all-you-need.pdf

Jiaqi Zhai, Lucy Liao, Xing Liu, Yueming Wang, Rui Li, Xuan Cao, Leon Gao, Zhaojie Gong, Fangda Gu, Michael He, Yinghai Lu, and Yu Shi. 2024. Actions Speak Louder than Words: Trillion-Parameter Sequential Transducers for Generative Recommendations. arXiv preprint arXiv:2402.17152. https://arxiv.org/abs/2402.17152

Guorui Zhou, Chengru Song, Xiaoqiang Zhu, Ying Fan, Han Zhu, Xiao Ma, Yanghui Yan, Junqi Jin, Han Li, and Kun Gai. 2018. Deep Interest Network for Click-Through Rate Prediction. arXiv:1706.06978 [stat.ML] https://arxiv.org/abs/1706.06978

Jieming Zhu, Quanyu Dai, Liangcai Su, Rong Ma, Jinyang Liu, Guohao Cai, Xi Xiao, and Rui Zhang. 2022. BARS: Towards Open Benchmarking for Recommender Systems. In SIGIR ’22: The 45th International ACM SIGIR Conference on Research and Development in Information Retrieval, Madrid, Spain, July 11 - 15, 2022, Enrique Amigó, Pablo Castells, Julio Gonzalo, Ben Carterette, J. Shane Culpepper, and Gabriella Kazai (Eds.). ACM, 2912–2923. doi:10.1145/3477495.3531723

Jieming Zhu, Jinyang Liu, Shuai Yang, Qi Zhang, and Xiuqiang He. 2021. Open Benchmarking for Click-Through Rate Prediction. In CIKM ’21: The 30th ACM International Conference on Information and Knowledge Management, Virtual Event, Queensland, Australia, November 1 - 5, 2021, Gianluca Demartini, Guido Zuccon, J. Shane Culpepper, Zi Huang, and Hanghang Tong (Eds.). ACM, 2759–2769. doi:10.1145/3459637.3482486

## A Usage of LLMs Disclosure

In this section, we disclose the usage of LLMs in the preparation of this manuscript. LLMs were used for 1) polishing writing or shortening limited blocks of text and 2) for generating template code for plotting or minor changes of existing code. LLMs were NOT used for retrieval and discovery (e.g., finding related work), research ideation, or any other purpose not explicitly outlined in the above.

## B Mixed Full Linear Attention

To simplify triton implementation, especially for the gradient computation, our quasi-Linear Attention drops the normalization (RowNormalize) in the usual linear attention, similar to lightning attention. Instead we can mimic what SiLU attention does, by introducing a $1 / N$ factor.

$$
O = (Q K ^ {T}) \odot M V / N,
$$

where ⊙ is the Hadamard product (componentwise multiplication of two matrices, and $M = \left( \begin{array} { c c } { \mathbf { 1 } _ { n \times n } } & { \mathbf { 0 } _ { n \times m } } \\ { \mathbf { \qquad } } & { \mathbf { \qquad } } \\ { \mathbf { 1 } _ { m \times n } } & { \mathbf { \qquad } } \end{array} \right)$ . To compute this in triton, first break into two parts.

$$
\begin{array}{l} Q = \left(\frac {Q [ S ]}{Q [ T ]}\right), \qquad Q [ S ] \in \mathbb {R} ^ {n \times d}, \quad Q [ T ] \in \mathbb {R} ^ {m \times d}, \\ K = \left(\frac {K [ S ]}{K [ T ]}\right), \qquad K [ S ] \in \mathbb {R} ^ {n \times d}, \quad K [ T ] \in \mathbb {R} ^ {m \times d}, \\ V = \left(\frac {V [ S ]}{V [ T ]}\right), \qquad V [ S ] \in \mathbb {R} ^ {n \times d}, \quad V [ T ] \in \mathbb {R} ^ {m \times d}. \end{array}
$$

We will divide $n + m$ into A blocks of size $n ^ { \prime } ,$ and divide n into B blocks of size $n ^ { \ast }$ , so that $Q _ { i }$ are submatrices of dimension $n ^ { \prime } \times d ,$ and $K _ { j } , V _ { j }$ are submatrices of dimension $n ^ { \mathfrak { N } } \times d .$

First we compute

$$
(Q K [ S ] ^ {T} V [ S ]) _ {i} = Q _ {i} \sum_ {j = 1} ^ {B} K [ S ] _ {j} ^ {\top} V [ S ] _ {j}.
$$

Next we compute the target part: we divide m into C blocks of size m<sup>′</sup> each. For the j-th block, it’s given by

$$
((Q [ T ] K [ T ] ^ {\top} \odot I _ {m}) V [ T ]) _ {j} = \operatorname{diag} ((Q [ T ] _ {j} \odot K [ T ] _ {j}) \mathbf {1} _ {m ^ {\prime} \times 1}) V [ T ] _ {j}.
$$

We usually merge the source and target embedding sequences in an interleaved fashion. To avoid HBM/SRAM sync, we probably should keep track of the ofsets of the boundary between source and target, and let $n ^ { \prime } = { \dot { m } } ^ { \prime }$ , so that for the target part, we will overlap the two computation and obtain

$$
\begin{array}{l} O [ S ] _ {\ell} = Q [ S ] _ {\ell} \sum_ {j = 1} ^ {B} K [ S ] _ {j} ^ {\top} V [ S ] _ {j} \\ O [ T ] _ {\ell} = Q [ T ] _ {\ell} \sum_ {j = 1} ^ {B} K [ S ] _ {j} ^ {\top} V [ S ] _ {j} + \mathrm{diag} ((Q [ T ] _ {\ell} \odot K [ T ] _ {\ell}) \mathbf {1} _ {m ^ {\prime} \times 1}) V [ T ] _ {\ell} \end{array}
$$

In terms of triton implementation, we will use positive ofsets for target, and negative ofsets for source, all starting from the boundary ofset.

Note that the sum $\begin{array} { r } { \sum _ { j = 1 } ^ { B } K [ S ] _ { j } ^ { \top } V [ S ] _ { j } } \end{array}$ can be computed first, then multiplied with $Q [ S ] _ { \ell } .$ $Q [ T ] _ { \ell }$ etc. By choosing the block size $n ^ { \prime } = m ^ { \prime }$ suficiently small, and if necessary, also break the block $V [ S ] , V [ T ]$ along the columns into smaller dimension $d ^ { \prime } | d ,$ we can ensure all $O [ S ] _ { \ell } , O [ T ] _ { \ell }$ blocks can be computed entirely in SRAM with a single for loop.

To replace linear attention with (traditional) SiLU attention for target to source, we need to replace the second line above with

$$
O [ T ] _ {\ell} = \sum_ {j = 1} ^ {B} \operatorname{SiLU} (Q [ T ] _ {\ell} K [ S ] _ {j} ^ {T}) V [ S ] _ {j} + \operatorname{SiLU} (Q [ T ] _ {\ell} \odot K [ T ] _ {\ell} 1 _ {m ^ {\prime} \times 1}) V [ T ] _ {\ell}.
$$

Here we cannot compute all the $O [ T ] _ { \ell }$ blocks easily, but instead need to have $m / m ^ { \prime }$ SM’s to compute them separately, otherwise each SM would incur a big for loop of $B m / \dot { m } ^ { \prime }$ iterations. Given H100 has about 132 SMs and batch size per rank is 512, using more SMs will likely slow things down.

## B.1 Gradient Computation

$$
\begin{array}{r l} & {\frac {\partial L}{\partial V} = \mathrm{tr} \left(\left(K Q ^ {\top} \frac {\partial L}{\partial O}\right) \odot M ^ {\top}\right) / N} \\ & {\frac {\partial L}{\partial Q} = \mathrm{tr} \left(\left(K Q ^ {\top} \frac {\partial L}{\partial O}\right) \odot M ^ {\top}\right)} \end{array}
$$

Given that ${ \cal L } = { \cal L } ( { \cal O } [ S ] , { \cal O } [ T ] )$ , and $O [ S ]$ and $O [ T ]$ are disjoint, we can compute

$$
d L = \sum_ {i j} \frac {\partial L}{\partial O [ S ]} _ {i j} d O [ S ] _ {i j} + \sum_ {i j} \frac {\partial L}{\partial O [ T ]} _ {i j} d O [ T ] _ {i j}
$$

## B.1.1 Gradient of V

If we diferentiate against V , we have

$$
\begin{array}{l} d O [ S ] = Q [ S ] K [ S ] ^ {\top} d V [ S ] \\ d O [ T ] = Q [ T ] K [ S ] ^ {\top} d V [ S ] + \mathrm{diag} ((Q [ T ] \odot K [ T ]) \mathbf {1} _ {T \times 1}) d V [ T ] \end{array}
$$

So,

$$
\begin{array}{l} d L = \operatorname{tr} \left(\frac {\partial L}{\partial O [ S ]} ^ {\top} d O [ S ]\right) + \operatorname{tr} \left(\frac {\partial L}{\partial O [ T ]} ^ {\top} d O [ T ]\right) \\ \quad = \operatorname{tr} \left(\frac {\partial L}{\partial O [ S ]} ^ {\top} Q [ S ] K [ S ] ^ {\top} d V [ S ]\right) + \operatorname{tr} \left(\frac {\partial L}{\partial O [ T ]} ^ {\top} (Q [ T ] K [ S ] ^ {\top} d V [ S ] + \operatorname{diag} ((Q [ T ] \odot K [ T ]) \mathbf {1} _ {T \times 1}) d V [ T ])\right) \\ \quad = \operatorname{tr} \left((\frac {\partial L}{\partial O}) ^ {\top} Q K [ S ] ^ {\top} d V [ S ]\right) + \operatorname{tr} \left((\frac {\partial L}{\partial O [ T ]}) ^ {\top} \operatorname{diag} ((Q [ T ] \odot K [ T ]) \mathbf {1} _ {T \times 1}) d V [ T ])\right). \end{array}
$$

So we have that

$$
\begin{array}{l} \frac {d L}{d V [ S ]} = K [ S ] Q ^ {\top} \frac {\partial L}{\partial O} \\ \frac {d L}{d V [ T ]} = \operatorname{diag} ((Q [ T ] \odot K [ T ]) \mathbf {1} _ {T \times 1}) \left(\frac {\partial L}{\partial O [ T ]}\right) \end{array}
$$

which means ith row of $\frac { \partial L } { \partial O [ T ] }$ will be multiplied by ith element of $( Q [ T ] \odot K [ T ] ) \mathbf { 1 } _ { T \times 1 }$

## B.1.2 Gradient of Q

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

Fine-tuning employs the next-token prediction paradigm, training the model to predict subse
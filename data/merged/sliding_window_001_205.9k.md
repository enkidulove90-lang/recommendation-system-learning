

## Cold-Start Recommendation towards the Era of Large Language Models (LLMs): A Comprehensive Survey and Roadmap

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

## ACM Reference Format:

Weizhi Zhang, Yuanchen Bei, Liangwei Yang, Henry Peng Zou, Peilin Zhou, Aiwei Liu, Yinghui Li, Hao Chen, Jianling Wang, Yu Wang, Feiran Huang, Sheng Zhou, Jiajun Bu, Allen Lin, James Caverlee, Fakhri Karray, Irwin King, and Philip S. Yu. 2025. Cold-Start Recommendation towards the Era of Large Language Models (LLMs): A Comprehensive Survey and Roadmap. J. ACM 1, 1, Article 1 (January 2025), 41 pages. https://doi.org/XXXXXXX.XXXXXXX

## Contents

Abstract 1  
Contents 2  
1 INTRODUCTION 4  
1.1 Related Work 5  
1.2 Survey Methodology 6  
1.3 Contributions 6  
2 PRELIMINARIES 8  
2.1 Background 8  
2.1.1 Recommender Systems 8  
2.1.2 Cold-Start Recommendations 8  
2.2 Problem Definition 9  
2.2.1 General Problem Definition 9  
2.2.2 Task-Specific Problem Definition 9  
3 CONTENT FEATURES 9  
3.1 Data-Incomplete Learning 10  
3.1.1 Robust Co-Training 10  
3.1.2 Knowledge Alignment 11  
3.1.3 Cold Exploration 12  
3.1.4 Feature Similarity Measurement 13  
3.1.5 Others 13  
3.2 Data-Efficient Learning 13  
3.2.1 Meta-Learning Optimization 13  
3.2.2 Meta-Task Utilization 14  
3.2.3 Meta-Embedding Initialization 15  
3.2.4 Sequential Meta-Learning 15  
4 GRAPH RELATIONS 15  
4.1 Interaction Graph Enhancement 15  
4.1.1 Supplementary Graph Relation 16  
4.1.2 Homophily Network Relation 16  
4.2 Graph Relation Extension 16

J. ACM, Vol. 1, No. 1, Article 1. Publication date: January 2025.

4.2.1 Heterogeneous Graph Relation 16  
4.2.2 Attributed Graph Relation 17  
4.2.3 Knowledge Graph Relation 17  
4.3 Graph Aggregator Improvement 17  
4.3.1 Aggregation Scope Expansion 17  
4.3.2 Information Aggregator Augmentation 18  
5 DOMAIN INFORMATION 18  
5.1 Domain Knowledge Transfer 18  
5.1.1 Embedding Mapping 18  
5.1.2 Heterogeneous Connections 19  
5.1.3 Learning Process 19  
5.2 Domain Distribution Alignment 19  
5.2.1 Collaborative Filtering Alignment 20  
5.2.2 Auxiliary Feature Alignment 20  
5.3 Domain-Invariant Representation Learning 20  
5.3.1 Disentangled Representation 20  
5.3.2 Fusing Representation 21  
6 WORLD KNOWLEDGE FROM LARGE LANGUAGE MODELS 21  
6.1 LLM as the Recommender System 22  
6.1.1 Prompting Strategy 22  
6.1.2 Model Tuning 24  
6.2 LLM as the Knowledge Enhancer 25  
6.2.1 LLM for Representation Enhancement 25  
6.2.2 LLM for Relation Augmentation 26  
7 CHALLENGES AND FUTURE OPPORTUNITIES 26  
7.1 Multi-Modal Cold-Start Recommendation 26  
7.2 Recommendation Foundation Models 27  
7.3 Efficiency in Cold-Start Recommendations 28  
7.4 Data Privacy in Cold-Start Recommendations 28  
7.5 Benchmark and Unified Evaluation 28  
8 CONCLUSION 29  
References 29

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

## 1.1 Related Work

A comparison between our survey and the previous surveys is shown in Table 1. All of the existing surveys, which cover cold-start recommendation articles, only focus on partial knowledge scopes or limited aspects of the CSR problem. The earliest surveys [51] and [17] partially covered single knowledge scope without defining specific cold-start issues. Later surveys from IDCTIT [163] and Applied Sciences [1] began incorporating graph relation and domain information, and being the first to explicitly define system cold-start and user cold-start issues, covering more relevant papers through 2021. More recent surveys such as JIIS [152] and IEEE Access [246] have expanded the scope and number of covered papers, with [246] particularly focusing on user cold-start problems. In all, no existing survey paper in the literature fully covers all four aspects (Features, Graph, Domain, and LLMs) while addressing multiple cold-start issues. In this work, we aim to fill this gap by providing a comprehensive and systematic survey covering 220 papers through December 2024, clearly defining 9 distinct cold-start issues and incorporating analysis across knowledge scopes from features, graphs, domains, and LLMs.

Table 1. Comparison with existing surveys. For each survey, we summarize the knowledge scope covered in their collected relevant papers, the corresponding statistics, and the specific types of cold-start issues defined and discussed in the survey

<table><tr><td rowspan="2">Surveys</td><td rowspan="2">Venues</td><td colspan="4">Knowledge Scope</td><td colspan="2">Cold-Start RecSys Papers</td><td rowspan="2">Defined/Focused Issue</td></tr><tr><td>Features</td><td>Graph</td><td>Domain</td><td>LLMs</td><td># Papers</td><td>Latest Year</td></tr><tr><td>[51]</td><td>ICCCA*</td><td>√</td><td></td><td></td><td></td><td>8</td><td>2017</td><td>-</td></tr><tr><td>[17]</td><td>IPM*</td><td></td><td>√</td><td></td><td></td><td>14</td><td>2018</td><td>-</td></tr><tr><td>[163]</td><td>IDCTIT*</td><td>√</td><td>√</td><td></td><td></td><td>18</td><td>2020</td><td>System Cold-Start</td></tr><tr><td>[1]</td><td>Applied Sciences</td><td>√</td><td></td><td>√</td><td></td><td>50</td><td>2021</td><td>User Cold-Start</td></tr><tr><td>[152]</td><td>JIIS*</td><td>√</td><td>√</td><td>√</td><td></td><td>91</td><td>2022</td><td>-</td></tr><tr><td>[246]</td><td>IEEE Access</td><td>√</td><td>√</td><td>√</td><td></td><td>45</td><td>2023</td><td>User Cold-Start</td></tr><tr><td colspan="2">Ours</td><td>√</td><td>√</td><td>√</td><td>√</td><td>220</td><td>Dec, 2024</td><td>Cold-Start</td></tr></table>

<sup>✓</sup>: fully covered, <sup>✓</sup> : partially covered. Cold-Start: covers 9 sub cold-start tasks as in Table 2 and Figure 4.  
Latest year: the latest publication year of a relevant paper included in the survey.  
ICCCA\*: International Conference on Computing, Communication and Automation; IPM\*: Information Processing and Management.  
ICDTIT\*: Intelligent Data Communication Technologies and Internet of Things; JIIS\*: Journal of Intelligent Information Systems.

## 1.2 Survey Methodology

To comprehensively cover the papers in the cold-start recommendation. We adopted a semi-systematic survey methodology to identify the relevant papers. Initially, we queried prominent academic databases such as Google Scholar and Web of Science with pre-defined searching keywords such as "cold-start recommendation", "coldstart recommender systems", "strict cold-start", "zero-shot recommendation", and "few-shot recommendation". Additionally, we screen specialized conference proceedings, including KDD, WWW, SIGIR, CIKM, WSDM, and RecSys. The search results were filtered by analyzing titles, abstracts, and experiments to evaluate relevance. Then, the relevant papers were further reviewed thoroughly, and their references were used as seeds for a snowballing approach to identify additional papers. The final collection comprised studies categorized into four core areas based on their contributions, as illustrated in the taxonomy diagram. These areas include content features, graph relations, domain information, and world knowledge from LLMs, as summarized in Figure 3. The majority of these works describe technical approaches or propose novel frameworks, with a smaller subset providing system demonstrations or analytical perspectives on cold-start recommendation methodologies.

## 1.3 Contributions

• Pioneering Comprehensive Survey: We present the first thorough review of cold-start recommendation methods, systematically identifying studies from various CSR tasks with diferent knowledge sources. Our survey meticulously analyzes relevant papers, examining their motivations, data requirements, and

Cold-Start Recommendation towards the Era of Large Language Models (LLMs): A Comprehensive Survey and Roadmap • 1: 7

![](images/100ab8a6b6080df5e58df8cb6a2f2b502a43ef33aee0981b8271bb0f09ba6814.jpg)  
Fig. 3. An overview of the taxonomy of this survey for existing cold-start recommendation models.

technical approaches, providing a consolidated timeline and statistical overview of research publications in leading conferences (e.g., SIGIR, CIKM, KDD) and journals (e.g., TKDE, TOIS), as depicted in Figure 2.

• Innovative Taxonomy Introduction: We introduce a novel taxonomy, providing a unique perspective on dealing with the cold-start challenge - utilizing external knowledge sources to address data sparsity and interaction scarcity with new entities. Our taxonomy categorizes knowledge sources distinctly, moving beyond traditional approaches toward a broader scope of addressing cold-start issues.

• Explicit Definition of Cold-Start Problems: To the best of our knowledge, we are the first paper ofering a clear, comprehensive definition of the cold-start problem across multiple dimensions, encompassing long-tail, user cold-start, item cold-start, user-item cold-start, zero-shot, and few-shot, and strict cold-start problems. This definition provides a structured understanding and unifying framework for diverse research strands within the cold-start landscape.

• A Foward-Looking Roadmap: Drawing on our comprehensive survey and innovative taxonomy, we propose a forward-looking roadmap that connects current advancements in cold-start recommendation with future research directions. This roadmap is designed to guide the research community, ofering insights and structured pathways for advancing knowledge in this challenging area.

## 2 PRELIMINARIES

## 2.1 Background

2.1.1 Recommender Systems. Recommendation systems (RecSys) are a subclass of information retrieval technologies that seek to predict the preference a user would give to an item or the likelihood of a user’s interaction with an item. These systems are designed to recommend items to users based on their individual preferences or behaviors, which are mainly inferred from historical user-item interactions. To expand on this, recommender systems play a crucial role in modern e-commerce, social media, and content platforms by helping users navigate through the vast amount of available content and products. They analyze historical behavior data such as purchase history, browsing history, ratings, and reviews to build user profiles and predict what items a user might be interested in [64, 86, 262]. Specifically, the development of current recommender systems can now be mainly divided into three stages. (i) Content-based recommendations. This type of recommender system focuses on the characteristics of items, such as the genre of a movie, the subject of a book, or the style of music. The system recommends items with similar features that a user has liked in the past. (ii) Collaborative filtering recommendations. Collaborative filtering (CF) is one of the most commonly used recommendation techniques, which recommends items based on the similarity between users or items, e.g. embedding similarity. User-based collaborative filtering recommends products that other users with similar preferences have liked, while item-based collaborative filtering recommends other items similar to those a user has liked in the past. (iii) Large language model-based recommendations. In recent years, large language models (LLMs) have received abundant attention for their powerful ability in text-based understanding and generation. Currently, many LLM-based recommender models have been proposed with recommendation-centric prompt tuning and vocabulary extensions for users/items to efectively model the user-item similarity for recommendations.

2.1.2 Cold-Start Recommendations. In the above backgrounds of recommender systems, we can find that the core of current recommender models is to mine the user-item similarity with diferent technical strategies. However, with the rapid development of the Internet, one major challenge faced by recommender systems is the cold start recommendation (CSR), which involves making accurate recommendations for new users and new items that are continuously added to the Internet every day [51, 75, 124]. The main challenge of cold start recommendation lies in the fact that new users and new items have little or no available information. In this situation, it is very dificult for the system to model the user-item similarity based on the very sparse information. Therefore, cold-start recommendations have become a long-standing problem for the research community of recommendation systems.

In this survey, we will provide a systematic review of existing CSR methods, starting from the detailed definition of diferent CSR problems in section 2.2 to unfolded classification and discussion of existing CSR models in section 3 - section 6, with knowledge scopes from content features, graph relations, and domain information, to world knowledge.

## 2.2 Problem Definition

2.2.1 General Problem Definition. Let $U = \left\{ u _ { 1 } , u _ { 2 } , \ldots \ldots , u _ { m } \right\}$ be a set of <sup>??</sup> users and $V = \{ v _ { 1 } , v _ { 2 } , \ldots \ldots , v _ { n } \}$ be a set of <sup>??</sup> items. Each user $u \in U$ is associated with a profile $\mathbf { S } _ { u } ,$ , which includes both an interaction history $\mathbf { I } _ { u }$ and contextual features $\mathrm { C } _ { u }$ obtained from external knowledge sources. Similar notations, including the item profile $\mathsf { S } _ { v } ,$ interactions $\mathbf { I } _ { v } ,$ and features $\mathbf { C } _ { v } ,$ hold for each item $v \in V .$ . In this setting, the training phase involves a known set of warm-start users $\overline { { U } }$ and items ${ \overline { { V } } } _ { \mathrm { { ; } } }$ for which interaction data are fully observed. During tuning and testing, however, we may encounter a new set of cold-start users $\widehat { U }$ and items ${ \widehat { V } } _ { \ }$ , which have not been observed during training. By definition, $\overline { { U } } \cap \widehat { U } = \emptyset , \overline { { U } } \cup \widehat { U } = U$ , and similarly ${ \overline { { V } } } \cap { \widehat { V } } = \emptyset , { \overline { { V } } } \cup { \widehat { V } } = V$ . This setup captures the realistic scenario where new users or items emerge after the model is initially trained. Note that for some cases, $\overline { { U } }$ and $\overline { { V } }$ could be null due to system-level cold-start in the platform.

![](images/51db5ba7b30ce7332218157b5f461bff1d6c610b51ad371d6efb4a2e74d022c4.jpg)  
Fig. 4. Comparison of warm-start and diferent cold-start recommendation problems.

2.2.2 Task-Specific Problem Definition. Building on this general definition, we explicitly define nine specific cold-start recommendation tasks. These tasks difer in terms of the conditions under which users or items are observed by the RecSys, and are grouped into four main categories—long-tail, normal cold-start, strict cold-start, and system cold-start to highlight their unique characteristics. Table 2 and Figure 4 illustrate these categories and the corresponding subtasks, as well as clarify how the training, tuning, and testing sets difer across scenarios.

## 3 CONTENT FEATURES

Content features mainly refer to the descriptive information inherent to users or items that characterize their attributes, such as user profiles, user reviews, item names, and descriptions [2, 63, 78, 292]. Due to the scarcity or lack of historical interaction records of cold users/items, content features become one of the key information representing cold users/items in cold-start recommendations [59, 181]. Based on the utilization of the content features, we categorize methods into two types: Data-Incomplete Learning (Sec. 3.1), which addresses strict cold start scenarios without prior interactions, and Data-Eficient Learning (Sec. 3.2), which optimizes performance in normal cold-start scenarios where limited interaction data is available.

Table 2. Problem definition of diferent cold-start recommendation tasks.

<table><tr><td>Category</td><td>Task</td><td>Train</td><td>Tune</td><td>Test</td><td>Task Specification</td></tr><tr><td>Long-Tail</td><td>Long-Tail</td><td> $\overline{U},\overline{V}$ </td><td>-</td><td> $\overline{U},\overline{V}$ </td><td>Node degrees of users and items in  $\overline{U}$  and  $\overline{V}$  are less than  $k$ .</td></tr><tr><td rowspan="3">NormalCold-Start</td><td>User</td><td> $\overline{U},\overline{V}$ </td><td> $\widehat{U},\overline{V}$ </td><td> $\widehat{U},\overline{V}$ </td><td>Each user in  $\widehat{U}$  appear and are observed with less than  $k$  interactions.</td></tr><tr><td>Item</td><td> $\overline{U},\overline{V}$ </td><td> $\overline{U},\widehat{V}$ </td><td> $\overline{U},\widehat{V}$ </td><td>Each item in  $\widehat{V}$  are released and observed with less than  $k$  interactions.</td></tr><tr><td>User-Item</td><td> $\overline{U},\overline{V}$ </td><td> $\widehat{U},\widehat{V}$ </td><td> $\widehat{U},\widehat{V}$ </td><td>Users  $\widehat{U}$  and Items  $\widehat{V}$  appear with less than  $k$  interactions each.</td></tr><tr><td rowspan="3">StrictCold-Start</td><td>User</td><td> $\overline{U},\overline{V}$ </td><td>-</td><td> $\widehat{U},\overline{V}$ </td><td>New users  $\widehat{U}$  appear after training without any interaction.</td></tr><tr><td>Item</td><td> $\overline{U},\overline{V}$ </td><td>-</td><td> $\overline{U},\widehat{V}$ </td><td>New items  $\widehat{V}$  are released with no prior interactions.</td></tr><tr><td>User-Item</td><td> $\overline{U},\overline{V}$ </td><td>-</td><td> $\widehat{U},\widehat{V}$ </td><td>Users  $\widehat{U}$  and Items  $\widehat{V}$  appear without any user-item interactions each.</td></tr><tr><td rowspan="2">SystemCold-Start</td><td>Zero-Shot</td><td>-</td><td>-</td><td> $\widehat{U},\widehat{V}$ </td><td>Users  $\widehat{U}$  are observed with its short-term interaction histories without collaborative filtering (CF) information from other users and items.</td></tr><tr><td>Few-Shot</td><td>-</td><td> $\widehat{U}_{1},\widehat{V}_{1}$ </td><td> $\widehat{U}_{2},\widehat{V}$ </td><td>Users  $\widehat{U}_{2}$  appear with a few interacted items and the learned CF patterns from few-shot users  $\widehat{U}_{1}$  and their interacted  $\widehat{V}_{1}$ .</td></tr></table>

For splitting <sup>??</sup> and $\widehat { U }$ from $U ,$ we default to using the number of interactions <sup>??</sup> in the task specification. Alternatively, some research adopts a time-based approach, categorizing users based on the appearing time (e.g., users’ first comment time before year <sup>??</sup> as existing users and those after as cold-start users), or employs random sampling for the separation. Similarly, these apply to the warm/cold item splitting process.

## 3.1 Data-Incomplete Learning

Data-incomplete learning is a category of methods that solely utilize content information to learn representations of cold users/items. Given the absence or very few historical interactions for these cold nodes, the available information for modeling their relations is incomplete. Therefore, through data-incomplete learning, which relies only on content information to learn the representations of these strictly cold users/items, the ultimate goal is to unify these representations with those of warm nodes learned from historical interactions for cohesive recommendations. We categorize the related works of data-incomplete learning into four major classes, robust co-training, knowledge alignment, cold exploration, and feature similarity measurement, based on diferent learning manners.

3.1.1 Robust Co-Training. Robust learning is a paradigm in machine learning that aims to make models maintain stability and accuracy even when faced with perturbations, noise, or outliers in the input data [91, 156]. In cold-start recommendations, robust co-training employs robust strategies to jointly utilize behavior-based warm user/item representations and content-based cold user/item representations for co-training. The objective of this training paradigm is to cultivate a model that is not only proficient in leveraging existing behavioral data to refine warm representations but is also adept at warming up cold representations through a process of gradual integration into the training mix. Specifically, the models for robust co-training can be divided into two major categories: robust generalization and autoencoders.

Robust generalization. Typically, this type of model will simultaneously optimize both behavior-based representations and content-based representations with robust generalization strategies. Representatively, Dropout-Net [183] randomly selects user-item pairs and sets their preference inputs to zero, forcing the model to rely solely on content information to reconstruct the relevance scores. This approach enables the model to recover the accuracy of the input latent model when preference information is available, while also generalizing in cold situations. Heater [289] also employs a similar stochastic training mechanism to randomly input the pre-trained collaborative representations or the intermediate representations derived from contents. MTPR [37] includes both two types of representations: one representation that combines collaborative embedding and content embedding, and another representation that assumes the item is cold-started, replacing the collaborative embeddings with a zero vector. These two representations are simultaneously used for embedding training. Further, there are some models that utilize an adaption-based strategy to transfer knowledge. For instance, Cold-Transformer [109] introduces the context-based embedding adaption for cold/warm users co-training to ofset the diferences in feature distribution, which transforms the embedding of cold users into a warm state that is more like existing ones to represent corresponding user preferences from historical interaction data. TDRO [116] further enhances the generalization capability of the content mapper by integrating time-variant feature shifts within the content feature co-training.

Autoencoders. The autoencoder (AE) technology employs an encoding-decoding architecture within a unified framework, where the encoder, informed by variational or denoising strategies, and the decoder, responsible for information reconstruction, are jointly trained to represent both cold and warm instances. This synergistic approach efectively captures and reconstructs the nuanced property of the behavior and content data, fostering a robust representation learning process. These models generally design new AE architecture to fit both behavior and content information. Representatively, LLAE [106] leverages an AE paradigm that encompasses a low-rank encoder designed to map the user behavior space onto the user content feature space, complemented by a symmetric decoder that reconstructs user behavior from the user content features. MAIL [41] is also a novel AE, which is composed of two pivotal autoencoder components: a zero-shot tower to generate behavioral data for cold users with content features and a ranking tower to perform recommendations. Moreover, CVAR and GoRec [7, 272] introduce a model-agnostic Conditional Variational Autoencoder (CVAE) [96] framework, which is adept at enhancing the warm-up process for cold-start item ID embeddings. CFLS [102] employs collaborative filtering within the latent variable space by employing a Gaussian process prior to avoiding the diference between behavior embeddings and content embeddings.

3.1.2 Knowledge Alignment. Due to the semantic discrepancies between the warm representations derived from behavioral data and the cold representations obtained from content data [25, 75], a strategic alignment is essential. To bridge this gap, the knowledge alignment introduces strategies to facilitate the convergence of cold representations with the pre-trained warm representations. The core of knowledge alignment is the aligner, which aims to align the cold representations from content features and the warm representations from behavior data with alignment strategies. These strategies are designed to ensure that the information encapsulated within the cold representations is efectively harmonized with the rich, behavioral-driven insights of the warm representations. By doing so, we aim to enrich the cold representations with the meaningful behavioral information inherent in the warm ones, thereby enhancing the overall semantic coherence and representational fidelity. In terms of technical categorization, existing approaches to knowledge alignment can be divided into three principal categories: contrastive learning, knowledge distillation, and generative adversarial networks.

Contrastive learning. It is a famous technique in machine learning that emphasizes the learning of representations by contrasting the similarities and diferences between pairs of data points [27, 276], It aims to improve the discriminative ability of models by ensuring that similar instances are represented closely in the representation space, while dissimilar ones are separated [218, 228]. In cold-start recommendations, contrastive learning is used to bridge the content-based representations of cold instances with the behavior-based representations of warm instances. For instance, CLCRec [212] learns the cold representations from the perspective of information theory, aiming to maximize the interdependence between content information and collaborative signals through contrastive learning. CCFCRec [280] also introduces a contrastive CF framework. It includes a content CF module and a co-occurrence CF module, which work in tandem to produce distinct embeddings. Through joint training and contrastive learning, the co-occurrence signals enhance the content-based embeddings, implicitly correcting the initial imprecision of cold-start item embeddings.

Knowledge distillation. The knowledge distillation (KD) method is a technique where a smaller, more eficient model learns from a larger, more complex model, transferring the knowledge and insights of the larger model into a more compact form, from the definition in machine learning [52, 154, 190, 197]. In cold-start recommendations, diferent from traditional utilization of KD, it is typically adopted to distill the knowledge from behavior-based warm representations to content-based cold representations, with the target of ensuring that the representations of the two convey more consistent information. Representatively, ALDI [75] views the pre-trained warm recommender model as the teacher and distills knowledge from three perspectives: rating distribution, ranking, and identification, for information alignment between warm representations and cold representations. Further, DTKD [256] aims to simultaneously and efectively distill both content and CF knowledge. The DTKD framework employs two specialized teachers - a pre-trained language model and a graph model, each tailored to the distinct characteristics of content and CF data, ensuring comprehensive knowledge distillation. Cold & Warm Net [259] introduces an expert-driven model that adopts dynamic knowledge distillation as a teacher selector, guiding the experts in refining both cold and warm user representation collaboratively.

Generative adversarial networks. Generative adversarial networks (GANs) are a class of methods where two neural networks: a generator and a discriminator, contend with each other, enabling the generator to produce increasingly realistic data [53, 79, 161]. In cold-start recommendations, GANs are typically used to make the generated cold representations from the content mapper more similar to the warm representations input into the recommender. Representatively, GAR [25] employs an adversarial training approach for both the generator (content mapper) and the recommender, ensuring that the generated cold-start item embeddings closely mimic the distribution of warm-start embeddings learned from historical interactions. GF2 [260] also utilizes GANs to enhance the embeddings for cold-start users, with the generator obtained from the GAN that can further be fine-tuned. GAZRec [4] utilizes the GAN to generate virtual representations for cold user/news that are conditioned on the given content data.

3.1.3 Cold Exploration. In the absence of substantial interaction data to model cold users or items efectively, a natural and intuitive approach is to employ a "trial" methodology, such as reinforcement learning-based strategies [82]. The cold exploration-based approach allows for the exploration of interests among cold users or items, leveraging the feedback signals from the recommender system to swiftly adjust the representations and modeling of these cold entities.

Reinforcement learning. The reinforcement learning (RL) method is a widely adopted type of exploration method where an agent learns to make decisions by performing actions in an environment to maximize a reward signal [6, 10, 144]. For cold-start recommendations, reinforcement learning algorithms are often utilized for interest explorations of cold instances for fast representation cold-starting. There are some representative methods that model the cold-start process into a specific RL-based process. Specifically, MetaCRS [30], through engaging in a series of exploratory dialogues to fast identify cold user preferences for conversational-based recommender systems. WSCB [169] has framed the user cold-start recommendation as a multi-armed bandit problem and introduced an innovative approach to balance exploration and exploitation during initial interactions, which grounds in active learning principles, aims to gather more comprehensive information about cold users. RL-LTV [82] models the recommendation process as a partially observable and controllable Markov decision process. To transfer the information from historical items to cold-start items, RL-LTV further introduces item inherent features, trending bias terms, and memory states as extra inputs into both the actor and critic.

Some other works further explore the other aspects of the capability of cold-start recommendations. For instance, ColdNAS [221] has devised a novel neural architecture search scheme aimed at discovering suitable modulation structures for cold-start users, encompassing both the functional and positional aspects.

3.1.4 Feature Similarity Measurement. To circumvent the issue of modeling in the face of absent behavioral data, an alternative approach is to shift the focus toward representing and modeling the content-based features of users and items. Specifically, these feature similarity measurement methods learn and evaluate the user/item interests from the perspective of content feature similarity. In this way, the model can avoid the information diference between warm representations (from behavior data) and cold representations (from content data).

Multi-feature fusion. This method aims to simultaneously utilize multiple features to provide more information for better cold instance measurement due to the data incomplete issue [185, 247]. The key challenge of this stage is to efectively organize and fuse these features from diferent sources. Representatively, CIRec [135] enhances the content representation for cold instances by fusing collaborative, visual, and cross-modal inferred representations. SMINet [177] learns the user representations from multiple aspects of input with gate attention to avoid relying solely on behavioral data. AutoFuse [87] automatically fuse data from various sources and types, which explicitly categorizes features into distinct groups predicated on their granularity.

Hashing. The hashing strategy has been widely adopted in computer vision and multi-media for similar content retrieval to balance the retrieval efectiveness and eficiency [121, 215, 282]. For cold-start recommendations, hashing can be used to map the warm and cold representations into unified binary hash code space for similarity measurement. For example, NeuHash-CF [59] introduces a content-aware neural hashing method, which generates binary hash codes for both cold and warm users/items, facilitating the estimation of user-item relevance using eficient Hamming distance. MFDCF [236] proposes a fast cold-start recommendation method with multi-feature discrete CF. Then, it adaptively projects multiple content features into binary and information-rich hash codes for retrieval.

3.1.5 Others. There are also some other methods for data-incomplete learning, which are mainly the early works. Due to the limited quantity, they are mainly based on traditional strategies and statistical methods. Representatively, Han et.al [56] combines non-behavioral thematic relevance and behavioral popularity to adjust item rankings, reducing the bias that leads to the cold start ranking of new items. Deezer [15] utilizes clustering analysis to assign new users to existing user groups, combining user embedding vectors with the centers of user groups to provide recommendations for cold-start users. DeepMusic [181] is a classic cold-start recommendation model that employs mean squared error and prediction error as the objective functions for model training based on rating predictions.

## 3.2 Data-Eficient Learning

Normal cold-start recommendations are prevalent in many online recommendation systems, prompting another research line to enhance models for eficient learning from limited user-item interactions. Meta-learning, known for its few-shot learning capabilities in fields like computer vision [28, 80], natural language processing [253], and graph mining [198, 278], plays a key role here. Gradient-based meta-learning [44, 45], which simulates few-shot test scenarios during training and leverages second-order gradients, enables quick adaptation with minimal data. Inspired by these strengths, numerous eforts have focused on applying meta-learning to cold-start problems, categorized into four approaches: meta-learning optimization, meta-task utilization, meta-embedding initialization, and sequential meta-learning.

3.2.1 Meta-Learning Optimization. The essence of meta-learning in recommender systems lies in pretraining the model with diverse users’ historical interactions, followed by rapid adaptation to new, cold-start users or items using limited additional interaction data. Thus, refining both the pretraining and adaptation phases is critical for improving cold-start recommendation performance.

Pretraining. MeLU [103] is one of the foundational works in cold-start recommendation, introducing the Model-Agnostic Meta-Learning (MAML) [44] optimization algorithm to estimate user preferences with only a small number of observed items. During the pretraining phase, local updates are applied to the decisionmaking layer using the support set, while global updates refine the whole user preference estimator using the query set. The use of second-order gradients on local and global updates enables the model to achieve a robust initial state, allowing it to fine-tune quickly with only a limited number of items to accurately estimate user preferences. Concurrently, building on MAML’s strengths, Bharadhwaj [11] integrated meta-learning strategies as a pretraining enhancement, demonstrating stronger generalization in addressing user cold-start scenarios across various models. Building on these approaches, PNMTA [153] enlarges the training scope to all the user interactions in pretraining for enriched preference representation learning, while FORM [174] derives an online regularized meta-leader algorithm and learns from the online gradients to accelerate the meta-training process.

Adaptation. While much of the focus has been on optimizing global parameter initialization shared for all users, several studies target personalized parameters specifically for cold-start adaptation. In the early work MAMO [35], the authors devised two memory matrices to store the feature-specific and task-specific memories for fast preference adaptation. Then Wang et al. [188] observed that existing methods risk memorizing query interactions without identifying novel preference patterns and they proposed to separate common preference transfer from novel preference adaptation. Alternatively, modulators have been proposed for adaptation. For instance, PNMTA [153] develops extra modulated models tailored for user groups instead of a universal metamodel. It uses a meta-learned task encoder modulator to estimate user identities and a predictor modulator to generate parameters for precise adaptation. To simplify adaptation pipelines, CMML [43] introduces a fully feed-forward approach. Using a context modulation network, it quickly adapts to limited interactions at both feature and task levels, streamlining the adaptation process.

3.2.2 Meta-Task Utilization. Beyond optimization, several studies [98, 117, 214, 226, 238, 245, 273] have highlighted the importance of task similarities and diferences in meta-learning. Traditional approaches treat each user as an isolated task, training without considering task connections. This limits the model’s ability to recognize individual user contributions and corresponding task relationships. Research in this area focuses on two key aspects: task diference and task relevance.

Task diference. Ignoring task diferences can lead to biases, as users with high uncertainty or dificulty may disproportionately afect predictions. To address this issue, Wen et al. [214] introduced a weighted distribution of functions (WDoF) framework, using curriculum learning to assign significance to users based on their contribution. Zhao et al. [273] proposed an adaptive update strategy (TDAS) to distinguish tasks in a macro manner, i.e., covering task dificulty of composition, relevance, and training aspects. Considering the highly distinct user feedback in the real-world cold-start recommendation, Kim et al. [98] designed an adaptive weighted loss to capture the imbalanced user rating distribution.

Task relevance. Understanding task relevance is crucial for adapting warm global knowledge to cold-start scenarios, especially when cold users share similar preferences with warm users. Approaches in this domain leverage clustering [117, 238] or similarity measures [226, 238, 245]. For instance, Yang et al. [238] designed an automatic soft task clustering module and a feature-based similarity score to measure task similarity. In TaNP [117], a clustering distribution is derived through task-adaptive mechanisms to capture task relevance efectively. Concurrently, Yu et al. [245] also proposed an adaptive meta-learning method focusing on minor users by identifying similar users using a reference tree structure. Wu et al. [226] enriched the cold-start user representation by aggregating similar user embeddings through attention similarity scores.

3.2.3 Meta-Embedding Initialization. methods focused on adapting models to cold-start scenarios, meta-embedding initialization aims to generate pre-trained embeddings that accelerate the fitting process for cold-start users and items. These methods leverage meta-learning algorithms to produce warmed-up embeddings, enhancing both representation quality and adaptation speed. Motivated by the idea of learning better initial embedding, Pan et al. [149] proposed to train the meta-embedding generator via a two-phase simulation based on the gradient-based meta-learning [44]. This approach generates meta-embeddings optimized for strict cold-start conditions, enabling faster adaptation in normal cold-start scenarios. Following that, Zhu et al. [286] proposed a meta-scaling network to transform cold ID embeddings into a warmed ID feature space, accelerating the warm-up process.

3.2.4 Sequential Meta-Learning. Aligned with the sequential recommendation framework [90, 172], sequential meta-learning incorporates the time order of user interactions to capture dynamic preferences using limited historical behavior sequences. Wang et al. [191] introduced metric-based meta-learning [182] paradigm into the sequential recommendation. It focuses on developing a matching network to pair cold-start items with potentia users based on limited sequential data. MetaTL [277] extended gradient-based meta-learning [44] to sequential recommendations by simulating cold-start scenarios with a pool of few-shot tasks. This setup allows the model to progressively learn user preferences. Recognizing that previously active old users may become less engaged over time, Neupane et al. [147] defined this group as time-sensitive cold-start users. Their approach dynamically factorizes user preferences into time-evolving representations, combining past and present interactions. Pan et al. [151] addressed feature divergence between older and newer interaction sequences. To stabilize and enhance meta-learning, they proposed a Multi-Modal Meta-Learning (MML) framework that integrates diverse side information, such as text and images, to better capture complex user preferences across diferent types of data.

## 4 GRAPH RELATIONS

In recent years, Graph Neural Networks (GNNs) have captured considerable attention, showcasing cutting-edge performance in a multitude of graph mining tasks, such as node classification [9, 55, 100], link prediction [223, 248, 254], and graph classification [210, 211, 229]. GNNs typically adopt the message-passing paradigm to update each central node embedding via aggregating neighborhood information. As a task within the realm of link prediction, recommender systems have witnessed the emergence of numerous GNN-based recommendation models, which have achieved notable recommendation performance in recent years [64, 204, 232]. GNN-based recommendation models mainly leverage the powerful message passing of GNNs to model user-item interactions in a graph structure, enabling a better understanding of user preferences and item relevance with high-order information for more efective recommendations [24, 165, 220]. Graph relations provide high-order information, rather than only the content features of the user/item itself. The usage of graph relation knowledge brings information from neighborhoods to a specific user/item. The key challenges in this part lie in how to provide graph information for cold users/items due to the lack of historical interaction information. Existing works can be categorized into Interaction Graph Enhancement (Sec. 4.1), Graph Relation Extension (Sec. 4.2), and Graph Aggregator Improvement (Sec. 4.3).

## 4.1 Interaction Graph Enhancement

Due to the lack of historical interaction behaviors or having very few, providing graph relational information for cold nodes is a significant challenge. Therefore, Interaction Graph Enhancement focuses on increasing the number of interactions on the interaction graph for cold nodes to provide them with more graph information. We categorize the related works of interaction graph enhancement into two major classes: supplementary graph relation and homophily network relation. The example illustration is shown in Figure 5-(a).

![](images/91592948df6ca0a46802fe5fa21415f766a78959114fac4538b46fe1b8923612.jpg)  
Fig. 5. Illustrations of diferent strategies of graph relation usage.

4.1.1 Supplementary Graph Relation. This type of model aims to supplement the original user-item interaction graph by including graph relation information for cold instances. The key problem for building supplementary graph relations is finding a suitable strategy to generate edges for cold instances and evaluate the quality of the generated edges automatically. Based on the high-quality built edges, the cold instances will have external information aggregated from other nodes. In an ideal way, even warm instances will be positively included information from cold nodes through built interactions. Representatively, CGRC [94] adopts the mask and reconstruction operator on user-item interactions of randomly selected items, enabling the model to infer potential edges for unseen cold start nodes. MI-GCN [201] enhances the user-item interaction graph with mutual information, where the top similar node pairs under the mutual information evaluation are connected automatically. UCC [126] estimates the uncertainty of each user-item interaction and enhances embedding learning for cold start nodes by adding interactions with low uncertainty.

4.1.2 Homophily Network Relation. As the proverb "birds of a feather flock together" suggests, the homophily assumption is a hypothesis often relied upon in graph data mining, indicating that the central node and its neighboring nodes should have similar behaviors or label information [137, 140]. To incorporate homophily network relations, algorithms often need to explore explicit/implicit additional associations between users and items, such as social relationships [112, 165]. For example, Shams et.al [164] groups users into clusters based on the homophily similarity of their preferences, thereby accelerating the learning of preferences for new users from warm users. GME [148] establishes a connection between new items and other relevant existing items through an item graph, and based on this graph, learns how to generate the initial embeddings for new items. SDCRec [36] identifies implicit friend relationships on a user-item-attribute graph by defining palindrome paths, which are based on users having similar evaluations of items. Recently, Sbandi et.al [162] simultaneously enhanced cold user–user and item–item link relationships through similarity modeling, resulting in a denser graph for GNN-based recommendations.

## 4.2 Graph Relation Extension

Due to the lack of interaction information, graph relation extension aims to extend the origin interaction graph with more complex relations to pass relevant graph information for cold instances. The methods can be categorized into three classes: heterogeneous graph relation, attributed graph relation, and knowledge graph relation. The example illustration is shown in Figure 5-(b).

4.2.1 Heterogeneous Graph Relation. Compared to traditional user-item interaction graphs, heterogeneous graphs obtain more complex and information-rich relationships by expanding the types of nodes and edges in the graph. Relationships in heterogeneous graphs are often mined by designing specific heterogeneous graph neural networks [74, 205, 251]. In the cold start scenario, relying solely on the user-item interaction network cannot meet the demand for relationship mining of cold nodes. Therefore, expanded heterogeneous graphs can often bring more associated information to cold nodes. The extension is typically based on other available relationships or implicit relationship mining from other information sources. Representatively, GIFT [20] establishes a heterogeneous graph that includes physical and semantic links to enhance the message-passing process from preheated videos to cold start videos. Further, HGNR [125] constructs a heterogeneous graph that is composed of user-item interactions, social links, and semantic links predicted from social networks and textual reviews. MvDGAE [275] enhances the connections between users and items in diferent aspects through multi-view extraction. PGD [199] and IHGNN [16] incorporate attribute information of users and items into the user-item graph to construct a heterogeneous graph (user-item-attribute graph), enabling cold nodes to have more available information for aggregation within this graph.

4.2.2 Atributed Graph Relation. Attributes typically reveal the inherent information of an instance, and similar attributes can represent that the two have similar characteristics, such as items with similar descriptive information may belong to the same category or users with similar profiles may be part of the same interest community [65, 139]. In cold start recommendations, attribute graphs are also often used for message passing to avoid the issue of having no available interaction information. Specifically, ColdGPT [22] leverages LLMs to extract fine-grained attributes from item content and connect them to item nodes to form an item-attribute graph structure for cold-start representation learning of items. EmerG [208] builds an item-specific feature graph with a GNN message passing on it to conduct CTR prediction with cold items.

4.2.3 Knowledge Graph Relation. A knowledge graph (KG) is a structured semantic knowledge base that stores relationships between entities in the form of a graph, with nodes representing entities and edges representing various semantic relationships between entities [54, 83]. The auxiliary information in knowledge graphs can be utilized to enhance cold instance learning. Representatively, KGPL [179] leverages unobserved user-item pairs as weak positive or negative instances, assigning pseudo-labels to these unobserved samples. To enhance the accurate labeling of cold-start users through pseudo-labeling, KGPL conducts sampling based on the structure of the knowledge graph, selecting items that may potentially interact positively with users. MetaKG [38] includes two meta-learners: a collaborative sensing meta-learner and a knowledge sensing meta-learner. These two learners respectively capture user preferences and knowledge of KG entities to combine more information for adapting to cold-start recommendations. CRKM [57] utilizes knowledge graphs and popularity information to sample negative labels from cold items that have not interacted with users, thereby alleviating the sparsity of cold-start training data.

## 4.3 Graph Aggregator Improvement

The two aforementioned subsections (interaction graph enhancement and graph relation extension) primarily address the issue of structural information scarcity for cold nodes by enhancing the graph structure. Another approach is to design an augmented model that extracts more usable information from limited structural data for cold-start recommendations, which we call graph aggregator improvement with a model-centric perspective in this survey. Related works can be categorized into two classes: can be mainly categorized into two main approaches: expanding the aggregation scope and augmenting the information aggregator. The example illustration is shown in Figure 5-(c).

4.3.1 Aggregation Scope Expansion. The first approach extends the model’s scope beyond local neighborhoods, encouraging attention to global or long-range contexts. In this way, cold instances can perceive long-distance correlated nodes to alleviate the sparsity in the direct neighborhood. For example, MeGNN [120] employs global neighborhood transformation learning to achieve consistent latent interactions for all new users and item nodes

Domain Knowledge Transfer

and adopts local neighborhood transformation learning to forecast specific latent interactions tailored to each node. MPT [60] integrates a Transformer encoder into the GNN encoder framework to capture long-range dependencies between users and items, thereby providing cold nodes with access to a richer set of usable neighborhood information.

4.3.2 Information Aggregator Augmentation. Meanwhile, the second approach refines the aggregator’s functionality, enabling it to capture more critical information for cold nodes within the limited interaction data of cold instances. Representatively, to mitigate the impact of cold-start neighbors, Hao et.al [61] introduces a meta-aggregator based on self-attention to enhance the aggregation capabilities at each graph convolution step. A-GAR [73] introduces an adaptive neighbor aggregation strategy, comprehensively exploring higher-order features of users/items. Based on this, a graph attention network is employed to integrate the augmented preference information from neighbors, enhancing aggregators’ ability to model data sparsity in cold-start scenarios.

## 5 DOMAIN INFORMATION

In real-world online applications, only a few platforms experience significant user engagement, while many others struggle with persistent long-tail and user cold-start issues. Therefore, transfer learning [213, 290] across diferent domains ofers a promising solution by leveraging knowledge from source domains with abundant data to enhance recommendation performance in target domains with limited information. Unlike traditional cold-start recommendation systems, cross-domain recommendation methods are inherently more complex. They must consider knowledge from at least two distinct systems, which often difer significantly. These methods generally require overlapping users in cross-domain settings and strategies to efectively utilize those users to share domain knowledge. According to the high-level methodologies of utilizing the domain knowledge, we divide existing work into three classes: Domain Knowledge Transfer (Sec. 5.1), Domain Distribution Alignment (Sec. 5.2), and Domain-Invariant Representation Learning (Sec. 5.3) as illustrated in Figure 6.

![](images/2f06dbfede386a6c1309cf89b53262e0b09966ab2b50ddc09acfb084673724a3.jpg)  
Domain Distribution Alignment  
Domain-Invariant Representation Laerning

Fig. 6. Illustrations of diferent categories of methods for utilizing the cross-domain knowledge.

## 5.1 Domain Knowledge Transfer

Domain transfer methods provide a straightforward approach to tackling cold-start problems in cross-domain scenarios. These methods typically rely on embedding mapping, graph connections, or learning processes to facilitate the seamless transfer of knowledge from a warm source domain to a cold target domain.

5.1.1 Embedding Mapping. One simple way is generalizing to the cold-start domain via various embedding mapping and feature transfer techniques. These methods typically focus on aligning the embedding spaces of the two domains through non-linear transformations, ensuring a smooth and efective knowledge transfer process.

General Mapping. Much of the work [12, 13, 89, 119, 132, 138, 141] simply adopts a single multi-layer perceptron (MLP) for general mapping of two domain representation space. For collaborative filtering-based mapping, the assumption is that overlapping users have rich interaction data. Studies like [89, 119, 138] leverage MLPs for flexible, non-linear transformations of the overlapping users’ representation spaces across domains. For side-information-based mapping, MAFT [132] utilizes MLPs combined with attention mechanisms to map auxiliary feature spaces efectively. In contrast, HCDIR [13] and DCDIR [12] enhance the target domain’s semantic and informational modeling by constructing heterogeneous information networks.

Personalized Mapping. Instead of employing a universal mapping function, recent methods [141, 180, 284] focus on personalized mapping tailored for each user. For example, PTUPCDR [284] introduces a meta-network that generates personalized parameters for bridging functions by using user-specific embeddings learned from the source domain. In comparison, VRCDR [180] incorporates Vietoris-Rips complexes, using characteristic vectors derived from users’ interaction patterns as inputs for the mapping function. This method models user preferences and geometric relationships between interacted items, translating user embeddings from source to target domains through personalized vectors.

5.1.2 Heterogeneous Connections. Beyond constructing a single mapping function to connect domains, heterogeneous approaches [85, 143, 171, 267] establish richer connections to facilitate domain knowledge transfer. These methods leverage auxiliary graph network structures to explicitly model and transfer knowledge across domains.

Knowledge Graph. Based on the rich information in the knowledge graph, [171] uses meta-path-based aggregation and multiple personalized bridges for transforming interest embeddings. On the other hand, [267] focuses on cross-domain knowledge graphs by capitalizing on natural relationships between items across domains, such as books and their movie adaptations.

Hybrid Connections. Another option is to construct hybrid connections over users or items in diferent domains. Jiang et al. [85] proposed to model a social network as a star-structured hybrid graph, where a central social domain connects with multiple item domains (e.g., web posts, and videos). CBMF [143] utilized clustering based relations to capture shared interests between user/item groups across domains while DisCo [105] introduces multi-channel graph encoders to obtain diverse user intents.

5.1.3 Learning Process. In the meanwhile, researchers have resorted to diferent training and tuning techniques to implicitly pass information from warm/source domains to cold/target domains.

Training Techniques. Early cross-domain works [72, 104] proposed specialized learning techniques to facilitate joint training across domains. The WITF model [72] trains on multi-domain feedback to learn informative priors about users and items to regularize the user preferences inference process. [104] developed a rating prediction model based on Partial Least Squares Regression that can transfer users’ rating preferences efectively.

Eficient Tuning. Recently, eficient tuning strategy [26, 111, 244, 283] has gained popularity in the crossdomain cold-start recommendation. As the overlapping users might be limited across domains, [111, 283] leverage meta-learning-based tuning approaches [44] to feature a two-stage process — pre-training models on source and target domains followed by meta-learning to tune a task-specific meta-network that generalizes knowledge for cold-start. Following them, [111] applies neural processes (NP) within the meta-learning tuning paradigm to model user-specific preferences and capture preference correlations among overlapping and cold-start users by representing preferences as predictive probability distributions. Other than meta-learning, Chen et al. [26] proposed a User-specific Adaptive Fine-tuning (UAF) to enhance personalization, and Yi et al. [244] utilized contrastive learning and personalized prompts to transfer knowledge from a source domain to a target domain.

## 5.2 Domain Distribution Alignment

Domain alignment in cold-start RecSys focuses on reducing distributional diferences between source and target domains to enable efective knowledge sharing. By aligning shared features, user behaviors, or auxiliary information across domains, these methods address challenges like data sparsity and cold-start scenarios.

5.2.1 Collaborative Filtering Alignment. The objective of collaborative filtering (CF) alignment is to leverage shared interaction patterns and user behaviors to facilitate better knowledge transfer among domains. To bridge distribution gaps, various methods [118, 127, 200, 230, 266] have been developed to ensure that the CF models can generalize well on the cold users in target domains in the normal user cold-start or long-tail settings.

Contrastive Alignment. Contrastive learning has been widely used to address distributional diferences and fulfill the domain alignment goal. For example, [127] integrates a rating prediction module and a distribution alignment module, where the latter aligns both overlapped and non-overlapped users across domains using unbalanced distribution optimal transport with contrastive loss. Such sample-wise contrastive alignment is also implemented in DAUC [118] to address the domain distribution gap. Focusing on user interest alignment, [266] constructs a unified cross-domain heterogeneous graph to capture high-order user-item relationships across domains. This model uses contrastive learning and gradient alignment to align user-user and user-item interest spaces efectively. Building on this, HGCCDR [230] constructs a heterogeneous graph enriched with user ratings, reviews, and item categories. Through graph augmentation and contrastive learning, HGCCDR strengthens both intra- and inter-domain connections, optimizing user embeddings for cross-domain scenarios.

Latent-Dimension Alignment. This line of studies [118, 200] leverages the encoder-decoder architecture to align domains in the latent representation space. DAUC [118] addresses the domain distribution gap between mobile app usage and article reading by using contrastive alignment and adversarial alignment loss on latent dimensions in the encoder-decoder structures. Similarly, LACDR [200] maps user embeddings to a low-dimensional space and aligns overlapping user representations to extract domain-invariant features.

5.2.2 Auxiliary Feature Alignment. Aligning latent embedding distributions directly between source and target domains is inherently challenging. Enforcing the alignment of two domains on the common auxiliary features space makes the process more approachable.

Stein-Path Alignment. Representatively, inspired by the idea of particle-based inference in stein variational gradient descent [58], DisAlign [128] adapts target domain samples to align with source domain distributions by iteratively moving embeddings along probabilistic Stein paths. For example, a book’s auxiliary embedding can align with its corresponding movie adaptation in a target domain, forming a semantic bridge. Expanding on this concept, CPKSPA [129] introduces proxy Stein path alignment to further reduce domain gaps by moving cold item embeddings with their source domain counterparts.

Contrastive Alignment. Paired with contrastive augmentation and alignment, CPKSPA [129] further enhances robustness through contrastive learning of cold item embeddings. Similarly, CCDR [228] uses contrastive learning to address domain alignment through both intra- and inter-domain techniques. Intra-domain contrastive learning creates augmented sub-graphs to combat data sparsity, while inter-domain learning aligns users, taxonomies, and neighbors to improve cross-domain knowledge transfer. Together, these methods create a comprehensive framework for aligning auxiliary feature spaces to enhance the cold-stat recommendation.

## 5.3 Domain-Invariant Representation Learning

Instead of focusing on reducing the distributional diferences as in domain alignment, domain-invariant representation learning assumes there is a shared feature space that are universally transferable across domains, capturing common user preferences or item characteristics.

5.3.1 Disentangled Representation. The common optimization goal of approaches in this category is to separate domain-invariant (shared) and domain-specific features. During training, the disentangling process ensures that shared representations capture universal user preferences or item characteristics that are transferable across domains, while domain-specific representations retain unique traits relevant to individual domains.

Adversarial Learning. This technique has been widely adopted to disentangle domain-invariant and domainspecific features. Following the adversarial generative network paradigm [50], RecSys-DAN [187] and AA [170] train discriminators to distinguish between source and target domain representations, while generators produce domain-invariant features that confuse the discriminator. Dif-MSR [207] enhances this approach by using difusion models to generate embeddings for each domain, isolating domain-shared and domain-specific characteristics via a classifier. UniCDR [18] further incorporates adversarial learning with contrastive objectives and masking mechanisms to perturb interactions and domain settings, generating diverse and robust representations.

Atention Mechanism. It ofers another pathway for disentanglement by focusing on feature-field relationships. [227] uses a multi-channel attention mechanism with contextual and internal attention layers to extract domainspecific and domain-invariant features. Building on this, [230] employs a multi-layer attention mechanism over user-item heterogeneous graphs, aligning domain-shared features using cross-view contrastive learning. In [250], attention is combined with contrastive learning to separate domain-invariant knowledge from domain-specific noise, using one attention module to aggregate shared knowledge and another to isolate domain-specific features.

5.3.2 Fusing Representation. The key idea is to fuse features between domains via multi-view learning and swapping learning, enabling the models to generalize domain-invariant user behaviors across diferent contexts.

Multi-View Learning. In short, multi-view learning leverages complementary perspectives to create shared representations for cross-domain recommendations. For instance, [209] explores dual-view learning by combining content semantics (similarities between items based on descriptive features) and structural connectivity ( high order relationships in knowledge graphs) to achieve domain-invariant representations. Similarly, [40] utilizes multi-view learning to integrate features, such as user behavior data (e.g., searches, clicks) and item characteristic (e.g., apps, movies, news), into a shared latent space to enhance knowledge transfer.

Swapping Learning. The swapping strategy refines domain-invariant features by exchanging domain-specific information. CDRIB [19] employs variational information bottleneck principles to swap and balance domainshared and domain-specific features, thus filtering out noisy, irrelevant features. CATN [265] swaps aspect-level preferences, such as plot or genre, extracted from reviews across domains (e.g., books to movies), enabling efective domain-invariant feature extraction. Diferently, Dual Autoencoder Network (DAN) [184] employs a swap reconstruction strategy. Specifically, the model uses dual encoder-decoder networks where user representations are swapped between the source and target domains for reconstruction. In this swap process, representations from one domain are reconstructed in another, ensuring that cross-domain information is leveraged efectively.

Semantic Learning Approaches in semantic learning aim to bridge domains by fusing diferent auxiliary information from users and items and assuming the semantic features space as domain-invariant. Earlier attempts like [62] and [189] map auxiliary information (e.g., user reviews, browsing histories, item descriptions) into a shared semantic space, enabling knowledge transfer. Following them, RCDFM [46] uses Stacked Denoising Autoencoders (SDAEs) to fuse semantic representations from user reviews and item contents with rating matrices, creating richer latent factors. Furthermore, [222] introduces zero-shot heterogeneous transfer learning to align semantic spaces between a recommender system and a retrieval system, leveraging item co-consumption correlations to generate domain-invariant embeddings.

## 6 WORLD KNOWLEDGE FROM LARGE LANGUAGE MODELS

Large language models (LLMs) are generative artificial intelligence systems trained using deep learning techniques to understand the general world knowledge by learning vast amounts of textual corpus data. These models can generate text, answer questions, perform translations, and even engage in complex conversations [271, 287]. Due to the tremendous success achieved in recent years, an increasing number of fields have begun to leverage the capabilities of large language models for various tasks, such as multimodal learning [217], graph learning [159], and recommender systems [219], achieving commendable results. Due to the powerful textual feature processing capabilities of LLMs, cold start, especially the zero-shot and few-shot scenarios, has become an important application in the recommendation domain for LLMs. According to the role that LLMs play, we categorize existing works into two main aspects: LLM as the Recommender System (Sec. 6.1) and LLM as the Knowledge Enhancer (Sec. 6.2).

![](images/2300132741960380fa4d2b49a7c4345b833a4218c44465aeb7dd9d36ff9d2680.jpg)  
Fig. 7. Illustrations of diferent categories of methods for utilizing the world knowledge from LLMs.

## 6.1 LLM as the Recommender System

Given the remarkable advancements of large language models (LLMs) in various zero-shot natural language processing tasks, it is natural to explore their potential for cold-start recommendations, especially in zero-shot scenarios. In these cases, LLMs can provide personalized suggestions without the need for domain-specific fifine-tuning or extensive training on historical user interactions. This line of research seeks to address the limitations of traditional recommender systems that heavily rely on historical interactions by leveraging the contextual understanding and generative capabilities of LLMs in tasks such as next-item prediction, conversational recommendation, and explainable recommendation.

6.1.1 Prompting Strategy. This series of work designed diferent prompting strategies to guide LLMs in making accurate (system) cold-start recommendations by framing recommendation tasks as natural language processing problems. This involves techniques like designing direct task-specific prompts including demonstrating in-context examples for the recommendation, integrating multi-step prompting for external information (such as taxonomy dictionaries or image summaries), and retrieval-augmented information to adapt LLMs to rank or generate recommendations based on the interactions and content features of users and items.

Direct Prompting. [168] first presented a simple direct prompting method where cold-start recommendations are generated using pretrained language models (e.g., GPT-2) without any need for task-specific retraining. With the update of ChatGPT, [122] explores the use of GPT-3.5 in zero-shot/few-shot recommendation tasks such as rating prediction, sequential recommendation, direct recommendation, explanation generation, and review summarization. Concurrently, some similar work [33, 69, 160, 173] employ task-specific prompting to directly conduct recommendation tasks (e.g., formulating specific prompts for tasks like rating prediction and item recommendation). Based on the task instruction, they further utilize few-shot in-context learning to incorporate user-item interaction to further guide recommendations). [67, 173] performed conversational recommendations in the cold-start settings and employed a task-specific prompting strategy to guide LLMs to generate responses based on the conversation. Notably, PromptRec [224] proposed the extreme system cold-start scenarios where no historical user-item interactions are available (e.g., new businesses). They cope with the problem by reframing the recommendation task into a sentiment analysis task using user and item profiles expressed in natural language.

Muti-Step Prompting. Though direct prompting can be used for zero-shot/few-shot recommendation tasks, they demonstrate less competitive results than traditional methods fully trained on user-item interactions. To improve the recommendation capabilities of LLMs, researchers attempt to restructure and transform originally complex and ambiguous cold-start recommendation tasks into more manageable muti-step tasks with modality rich information. Representatively, [196] involves a 3-step prompting approach using GPT-3 to (1) capture user preferences, (2) select representative movies, and (3) recommend items based on these inputs. This approach innovatively designs a multi-step pipeline to guide GPT-3 through subtasks to improve recommendation accuracy. Similarly, [42] applies a 3-step prompting where the LLM is guided through preprocessing background data, weighing user behavior factors, and generating POI recommendations with explanations. Some work attempts to adopt extra steps to gather more information before prompting the LLMs. For instance, [110] first transform the raw check-in records of users into question-answering tasks via key-value similarity and then specifically design prompts using the current and past trajectory along with the task instruction. Furthermore, the taxonomy dictionary is integrated into the overall multi-step recommendation framework to gather relevant information including item genres and item themes in [113]. Beyond the extra steps for prompting or textual information collection, visual data has been utilized in [130, 224] via few-shot in-context learning. Specifically, [224] introduces human-like explanations of visual features for LLM-based recommendations while [130] introduces visual summary thought (VST), a reasoning strategy for summarizing the textual descriptions of images in multimodal recommendation tasks.

Retrieval-Augmented Recommendation. In the field of NLP, retrieval-augmented generation (RAG) is an efective solution that enriches LLMs with a comprehensive array of background knowledge and detailed contextual insights to significantly enhance their capacity for content generation tasks [47, 268]. In recommendation systems, the retrieval-augmented modules [31, 34, 93, 146, 216] are primarily utilized to retrieve related exact item entities or essential information for encoding users/items, thereby enhancing the modeling accuracy of LLM-based recommender models. By leveraging the additional and fine-grained information obtained through retrieval, the modeling of cold and zero-shot instances, which initially lacked suficient data, can be significantl strengthened for recommendations. Most retrieval-based recommendation methods first conduct the retrieval process for collecting relevant user/item information such as item characteristics [34], potential item candidates [93], and users/items with corresponding interaction history [31, 216] and then prompting the LLM-based rec ommender system with such information to facilitate recommendation. In contrast, Mint [146] initially utilizes large language models (LLMs) to generate synthetic narrative queries through few-shot prompting and trains retrieval models on these synthetic queries and user-item interaction data. The core of the Mint method lies in repurposing the rich dataset of user-item interactions via LLMs for training the retrieval model to enhance the performance of the recommendation system.

6.1.2 Model Tuning. The motivation for tuning LLMs arises from the need to bridge the gap between the preference-capturing process of RecSys and the rich semantic understanding of LLMs in (system) cold-start recommendation. Though efective in zero-shot settings, direct-prompting-based LLMs struggle to handle and transfer rich collaborative filtering information from warm users/items to cold ones. In addition, they only achieve competitive cold-start performance at the cost of sacrificing the warm-start recommendations. To address these limitations, recent works [8, 29, 48, 99, 115, 136, 166, 175, 233, 252, 252, 261, 263] focus on learning interaction patterns through the tuning process. This approach enables LLMs to incorporate their pre-trained world knowledge and collaborative filtering interactions into the recommendation decision process, facilitating both warm-start and cold-start recommendations more efectively.

Instruction Tuning. The general framework of instruction tuning for cold-start LLM RecSys is to convert recommendation tasks into text-to-text generation processes, where the model learns to interpret user histories and item metadata in natural language via the next token prediction training. The constructed instruction-based dataset enables LLM RecSys to gain collaborative filtering knowledge in recommendation and seamless adapt to new items and domains without the need for additional time-consuming pre-training. Among this category, TALLRec [8] is one of the most pioneering works focusing on instruction tuning for RecSys. In particular, the original recommendation data is structured as natural language recommendation instructions to guide the LLMs to answer binary classification outputs ("yes" or "no"). Another fundamental work in instruction tuning for LLM-based recommendation is P5 (Pretrain, Personalized Prompt, and Predict Paradigm) [48]. It proposed a unified framework for various recommendation tasks, where all types of recommendation data (user-item interactions, metadata, and reviews) are converted into natural language prompts. This method allows P5 to handle diferent recommendation tasks in a shared text-to-text encoder-decoder framework without relying on task-specific training. Building on these two works, a series of studies have been proposed to further enhance the utilization of collaborative filtering signals among warm users and items during the LLM tuning stage. For instance, CoLLM [263] and A-LLMRec [99] leverage a mapping/alignment module to inject collaborative information from an external collaborative model. BinLLM [261] aims to convert the collaborative information into a binary format in the crafted prompts to guide the model in understanding recommendation tasks. Another research direction explores diferent item identification to accurately generate potential items and avoid hallucination, especially in zero-shot settings. TransRec [115], an LLM-based recommender system uses multi-facet identifiers (ID, title, and attributes) to bridge the item and language spaces and further ensures accurate cold-start item recommendations through position-free constrained generation, using specific data structure (FM-index) to generate valid identifiers. RecSysLLM [29] regards the user/item attributes as entity tokens for identification and establishes an entity pool in a tree structure to facilitate the searching process in the zero-shot recommendation. IDGenRec [175] uses an ID generator to create textual IDs for items and involves alternately training the ID generator and the base recommender with a specialized learning objective to encode items into concise, semantically rich textual IDs.

Fine-Tuning. To move beyond instruction-based adaptation to recommendation contexts, fine-tuning-based methods adapt pre-trained LLMs to recommendation tasks through specifically designed losses (e.g., contrastive loss) or extra trainable parameters (e.g., soft prompts [242] and adaptors [136]) that enable the model to learn rich, recommendation-domain-specific patterns. The primary goal is to encode collaborative and semantic information more explicitly, allowing them to capture intricate user-item interactions and deliver accurate recommendations for new items and users with minimal or no prior interaction history. For example, NoteLLM [252] employs a generative-contrastive learning approach to integrate collaborative signals and also uses collaborative supervised fine-tuning loss to train the model on generating hashtags and categories. Following this, NoteLLM-2 [252] integrates contrastive learning and a late fusion mechanism for multimodal representation, while URLLM [166] leverages contrastive learning and domain-specific retrieved augmented generation to fine-tune LLMs for efective and domain-aligned recommendations. Adding extra modules for parameter-eficient fine-tuning is considered an alternative way to incorporate collaborative filtering knowledge from warm users/items. POD [108] introduces a prompt distillation strategy distilling discrete prompts into continuous prompt vectors as extra parameters. XRec [136] uses a simple adapter to bridge the gap between collaborative filtering signals and the LLM’s semantic space. In contrast, TALLRec [8] and its follow-ups [99, 261, 263] employ a lightweight tuning method LoRA (Low-Rank Adaptation) [70] to adapt LLMs eficiently.

## 6.2 LLM as the Knowledge Enhancer

The goal of cold-start recommendation tasks in specific scenarios is to use additional information to represent the preferences of cold instances as accurately as possible, and the world knowledge obtained by large language models through pre-training on a vast amount of corpus information can serve as a powerful knowledge base for warming up cold instances.

6.2.1 LLM for Representation Enhancement. Traditionally, the recommendation is mainly based on ID embeddings for users and items [64, 204], in which embeddings are randomly initialized and trained based on collaborative signals over historical interactions. However, due to the absence of available information for cold users/items, the ID embeddings of these instances hardly represent them accurately. In this way, with the encoded world knowledge, LLMs can be adopted as the representation enhancer that (i) extends the original ID embeddings with other modality-aware representations, such as textual features and multimodal information, and (ii) models multi-domain knowledge with a unified LLM-based architecture. Based on the enriched user/item representations, the online recommender can provide more accurate user/item modeling.

Modality-Enhanced Representation. Commonly, recommendation models adopt ID embeddings that start from random initialization, which are only based on the model to aggregate information. For representation enhancement with other modality knowledge, LLMs are always adopted as auxiliary encoders due to their powerful linguistic encoding ability [274, 285] or multimodal encoding ability by MLLMs [123, 131]. This type of model’s key technical challenge is to efectively align the information of diferent modalities. For example, Kim et.al [95] proposes a general item representation learning framework for cold-start content recommendation. This framework is not dependent on specific domains or datasets and can naturally integrate multimodal features through a Transformer-based architecture. EasyRec [158] is a simple yet efective method that combines textbased semantic understanding and collaborative signals using a text-behavior alignment framework. It integrates contrastive learning and collaborative language model tuning to ensure an alignment between the text-enhanced semantic space and collaborative behavioral information. SAID [71] utilizes a projection module to convert item IDs into embedding vectors and then leverages LLMs to explicitly learn embeddings that are semantically aligned with the textual descriptions of items.

Domain-Enhanced Representation. Existing cross-domain recommendation systems typically require the design of complex model architectures to explore the relationships between two domains, making it dificult for models to scale to multiple domains and leverage more data. Moreover, existing recommendation systems use IDs to represent items, which carry fewer transferable signals in cross-domain scenarios, and user cross-domain behavior is also sparse, making it challenging to learn item relationships from diferent domains. Due to the architectural advantage of LLMs, which can unify encoding information in a single framework, LLMs are flexible enough to learn user/item representation in multiple domains simultaneously. For instance, LLM-REC [176] mixes user behavior across diferent domains and models user behavior using pre-trained language models, expecting to leverage the common knowledge encoded in pre-trained language models. Gong et.al [49] proposed a unified foundational model for search and recommendation, leveraging LLMs to extract domain-invariant text features, and fusing ID features, text features, and task-specific sparse features through aspect gating fusion to obtain representations for queries in search and cold items in recommendation. KAR [146] generates inferential and factual knowledge by an open-world knowledge-enhanced recommendation framework, and then efectively transforms and compresses this knowledge into enhanced vectors through a hybrid expert adapter, making them compatible with recommendation tasks. These enhanced vectors can be directly used to enhance the performance of any recommendation model.

6.2.2 LLM for Relation Augmentation. Another approach to leveraging LLMs as knowledge enhancers is through behavior augmentation. Specifically, the extensive world knowledge embedded in LLMs can be harnessed to analyze the potential preferences and interests of cold instances, thereby enhancing their potential behaviors. Since existing recommendation models predominantly rely on behavioral features for modeling [64, 66], accurately performing this enhancement can substantially boost the modeling capabilities of current recommendation models for cold instances.

Behavior Simulation. Based on textual (or multimodal) information of user/item instances, LLMs can be adopted as the behavioral signal generator by analyzing the semantic similarity between pairs of users and items. The efectively generated behaviors can help to address the data sparsity issue of cold instances. Specifically, ColdLLM [76] leverages a customized LLM simulator to mimic interactions (behavior patterns) between users and cold items, thereby directly transforming cold items into warm ones. In this way, cold and warm instances can be trained into a unified scheme with both simulated and real interactions. Similarly, Wang et.al [192] utilize LLMs to infer users’ preferences for cold-start items based on the textual descriptions of their historical behaviors and the descriptions of new items, and then integrate these enhanced training signals into the learning of downstream recommendation models through auxiliary pairwise losses.

External Relation Supplement. Existing knowledge-based recommendation systems rely on limited metadata in knowledge relations from private resources, which typically item attributes and user interaction data, but they have limitations in dealing with cold start problems and data sparsity. LLMs can be used as discriminative intermediate enhancers, leveraging world knowledge and learned common-sense information to associate user-item interaction graphs with additional provided text-powered relation information, such as external text-rich knowledge graphs, to avoid the knowledge sparsity of cold instances. CSRec [241] leverages commonsense knowledge from LLMs to construct a knowledge graph and combines it with existing knowledge-based recommendation methods. The CSRec framework efectively integrates common-sense knowledge from LLMs with metadata knowledge graphs through a common-sense knowledge graph and a knowledge fusion method. CoLaKG [32] leverages LLMs to enhance KGs by transforming graph data into textual inputs and generating semantic embeddings, which integrates global knowledge graph information to boost recommendation.

## 7 CHALLENGES AND FUTURE OPPORTUNITIES

In this section, we will discuss current challenges and future opportunities for cold-start recommendations. As shown in Figure 8, we will unfold the discussion with Algorithm Development (Sec. 7.1 and Sec. 7.2), Model Deployment (Sec. 7.3 and Sec. 7.4), and Benchmarks (Sec. 7.5).

## 7.1 Multi-Modal Cold-Start Recommendation

Leveraging multi-modal information has emerged as a promising approach in modern recommendation systems [279, 291], as it provides richer and more comprehensive representations of both items and user preferences through diverse modalities such as text, images, audio, and video. This capability is particularly valuable in addressing the cold-start problem by providing comprehensive user/item characteristics complementary to limited historical interactions. Despite the promising potential of multi-modal cold-start recommendations, several key challenges and opportunities remain for future research. An inherent challenge lies in efectively fusing and leveraging multi-modal information, as inappropriate utilization methods may introduce noise and degrad performance [279]. The prevailing issue of missing modalities in real-world applications poses another key challenge, as many existing multi-modal models assume all modality information is available during both training and inference [145, 186]. Most existing recommendation datasets provide limited modalities, also constraining the application of state-of-the-art multi-modal methods to recommendation systems [23]. Additionally, a notable gap exists between user interest modeling and multi-modal embedding extraction, where pre-trained encoders are often directly utilized or optimized for content-oriented tasks rather than user preferences, resulting in a discrepancy between content understanding and personalization. Furthermore, existing approaches often fail to account for users’ varying sensitivities to diferent modalities, as individuals may exhibit stronger preferences for certain modal aspects while remaining indiferent to others [243]. To address these challenges, we propose several potential research directions: (1) developing efective and eficient modality fusion methods that capture complementary information while remaining robust to noise and missing data; (2) constructing modality-rich recommendation datasets that incorporate diverse modalities beyond textual and visual information; (3) bridging the gap between multi-modal content and user interest modeling through personalized multi-modal embedding techniques and end-to-end architectures that jointly optimize content understanding with user preferences; and (4) designing adaptive personalization frameworks that dynamically adjust the importance of diferent modalities based on individual user preferences and contexts.

![](images/ccf1b39676da275444794b2bbc661a3e47822edcd0c047613e57266a776d5ee0.jpg)  
Fig. 8. Challenges and Future Opportunities of Cold-Start Recommendation.

## 7.2 Recommendation Foundation Models

The ongoing transformation within the field of Natural Language Processing (NLP) has been powered by the emergence of foundation models—comprehensive, pre-trained models that can be easily adapted to a variety of downstream tasks. These models, such as large language models (LLMs), have demonstrated remarkable capabilities in tasks ranging from text classification to dialogue generation, significantly reducing the need for task-specific training from scratch. Inspired by these developments, the recommendation domain now faces a similar opportunity: to leverage analogous “foundation models” for a wide range of cold-start tasks, thereby enhancing adaptability, eficiency, and scalability. As discussed in Section 6, existing research has shown that LLMs can efectively address the cold-start issue for single tasks or within single domains. However, these solutions often require continuous long-term re-adaptation when encountering new recommendation tasks or domains, leading to substantial time and computational overhead. Future research directions involve the design and implementation of these recommendation foundation models, as well as algorithms to quickly adapt large foundation models to diferent CSR subtasks. Such models would not only enable multi-task recommendation capabilities, as exemplified by P5 [48], but also dynamically adjust their recommendations across diverse domains.

## 7.3 Eficiency in Cold-Start Recommendations

Though current approaches for solving cold-start recommendations have shown promising results, they primarily focus on ofline setups and face significant challenges when deployed on large-scale real-world systems due to the high latency and resource cost it will introduce [193]. For example, current LLM-based CSR approaches often sufer from significant computational overhead during both training and inference, posing challenges for real-time deployment. There is a great need for solutions capable of handling industrial-scale RecSys while meeting the query-per-second requirements of real-time applications. Future research could prioritize developing lightweight and scalable models and exploring hybrid strategies that combine content-based and collaborative filtering techniques for more robust solutions. Real-time learning mechanisms are particularly critical, as they can swiftly incorporate early signals from cold-start items or users into the feedback loop, allowing for rapid adaptation to dynamic environments. Specifically, to support the applications of LLMs in cold-start recommendations, hybrid solutions such as hierarchical planning could be explored. For instance, LLMs could be utilized for high-level planning, such as cold-start content or user cluster selection, while traditional recommendation models focus on real-time, low-level item recommendations to ensure both eficiency and accuracy [194].

## 7.4 Data Privacy in Cold-Start Recommendations

Data privacy has long been a challenge for recommendation systems [68, 77], and the reliance on user information beyond interactions makes the challenges of cold start recommendations even more pronounced. For example, there are some listed issues: (C-i) Dependency on side information. Building user profiles is central to recommendation systems, but it can involve the use of sensitive information. Striking a balance between utilizing efective user-profiles and protecting user privacy is a challenge in the design of cold-start models. (C-ii) Domain information privacy. Privacy preservation in cross-domain recommendation systems is more challenging, especially in cold start scenarios where data sparsity is a significant issue. The need to encourage collaboration between diferent domains for data can lead to privacy breaches if not managed carefully. To address these issues, there are some technologies that can be promising: (T-i) Privacy calculation. Diferential privacy calculation can protect user privacy information by adding noise to the data, making it impossible for the platforms and attackers to infer information about any specific individual through analysis of the results [167, 206]. In addition to that, homomorphic encryption allows computations to be performed directly on encrypted data without the need for decryption, thus protecting the privacy of the data [88, 97]. (T-ii) Federated learning. Federated learning (FL) ofers several advantages for privacy protection in the context of cold start issues [81, 240]. FL allows data, like side information, to remain local and not uploaded to a central server, thereby protecting user privacy. FL enables decentralized model training, where multiple parties can collaboratively train a model without sharing raw data, which is helpful for cross-domain cold-start recommendations [141, 178]. Further, in FL, only model updates (such as gradients) are transmitted to a central server for aggregation, not raw data. This further reduces the risk of privacy leaks in cold start issues.

## 7.5 Benchmark and Unified Evaluation

Research on cold start recommendation systems has made significant progress. However, evaluations for existing cold start recommendation systems are currently diverse and inconsistent. Thus, it would be promising and meaningful to develop a unified and fair evaluation benchmark for the community. Specifically, there are multiple problem settings for cold-start recommendations, such as strict cold-start, non-strict cold-start, and long-tail cold-start, and each setting needs to be evaluated fairly. This raises the following three main issues: (i) Diferent benchmark datasets. Diferent papers rarely overlap in the datasets they use, making it dificult for researchers to conduct unified comparisons across several related datasets. A promising approach for the future would be to encourage the community to focus on a selection of high-quality datasets for comparative experiments. Further, only part of the papers adopts datasets with real cold users/items in industrial platforms. We encourage the community to release these datasets for open research, which is very meaningful for the development of the community. (ii) Diferent evaluation settings. The key problem in this part is the setting of cold users/items. Specifically, how to define and synthesize cold users/items in the experiments? In the experiments of many cold-start works, cold users/items are often obtained by varied approaches (time range, number of interactions, and random selection) with vague definitions of CSR settings, and there is still a lack of unified rules. (iii) Open-source evaluation frameworks. There are some practical open-source projects for recommendation experiments, such as Recbole [269, 270], Elliot [5], and BARS [281]. However, all of them are designed for general recommendation evaluations. A unified open-source evaluation codebase for cold-start recommendations with fair evaluation settings and metrics will be very helpful for the research community.

## 8 CONCLUSION

In this paper, we provide a comprehensive review of cold-start recommendations, with a roadmap from con tent features, graph relations, and domain information, toward world knowledge from large language models. Specifically, we first formally define diferent research questions in the field of cold-start recommendations. Then, we systematically review cold-strat recommendations. In each part, we provide overall insights behind related works and list some representative works for readers to better understand. Furthermore, we rethink some of the challenges of cold-start recommendations and summarize some meaningful future directions. Related resources are organized in the Github (https://github.com/YuanchenBei/Awesome-Cold-Start-Recommendation) for the CSR research and industrial community.

## References

[1] Nor Aniza Abdullah, Rasheed Abubakar Rasheed, Mohd Hairul Nizam Md Nasir, and Md Mujibur Rahman. 2021. Eliciting auxiliary information for cold start user recommendation: A survey. Applied Sciences 11, 20 (2021), 9608.

[2] Arkadeep Acharya, Brijraj Singh, and Naoyuki Onoe. 2023. Llm based generation of item-description for recommendation system. In Proceedings of the 17th ACM Conference on Recommender Systems. 1204–1207.

[3] Josh Achiam, Steven Adler, Sandhini Agarwal, Lama Ahmad, Ilge Akkaya, Florencia Leoni Aleman, Diogo Almeida, Janko Altenschmidt, Sam Altman, Shyamal Anadkat, et al. 2023. Gpt-4 technical report. arXiv preprint arXiv:2303.08774 (2023).

[4] Manal A Alshehri and Xiangliang Zhang. 2022. Generative adversarial zero-shot learning for cold-start news recommendation. In Proceedings of the 31st ACM International Conference on Information & Knowledge Management. 26–36.

[5] Vito Walter Anelli, Alejandro Bellogín, Antonio Ferrara, Daniele Malitesta, Felice Antonio Merra, Claudio Pomo, Francesco Maria Donini, and Tommaso Di Noia. 2021. Elliot: A comprehensive and rigorous framework for reproducible recommender systems evaluation. In Proceedings of the 44th international ACM SIGIR conference on research and development in information retrieval. 2405–2414.

[6] Kai Arulkumaran, Marc Peter Deisenroth, Miles Brundage, and Anil Anthony Bharath. 2017. Deep reinforcement learning: A brief survey. IEEE Signal Processing Magazine 34, 6 (2017), 26–38.

[7] Haoyue Bai, Min Hou, Le Wu, Yonghui Yang, Kun Zhang, Richang Hong, and Meng Wang. 2023. Gorec: a generative cold-start recommendation framework. In Proceedings of the 31st ACM international conference on multimedia. 1004–1012.

[8] Keqin Bao, Jizhi Zhang, Yang Zhang, Wenjie Wang, Fuli Feng, and Xiangnan He. 2023. Tallrec: An efective and eficient tuning framework to align large language model with recommendation. In Proceedings of the 17th ACM Conference on Recommender Systems. 1007–1014.

[9] Yuanchen Bei, Hao Xu, Sheng Zhou, Huixuan Chi, Haishuai Wang, Mengdi Zhang, Zhao Li, and Jiajun Bu. 2024. Cpdg: A contrastive pre-training method for dynamic graph neural networks. In 2024 IEEE 40th International Conference on Data Engineering (ICDE). IEEE, 1199–1212.

[10] Yuanchen Bei, Sheng Zhou, Qiaoyu Tan, Hao Xu, Hao Chen, Zhao Li, and Jiajun Bu. 2023. Reinforcement neighborhood selection for unsupervised graph anomaly detection. In 2023 IEEE International Conference on Data Mining (ICDM). IEEE, 11–20.

[11] Homanga Bharadhwaj. 2019. Meta-learning for user cold-start recommendation. In 2019 International Joint Conference on Neural Networks (IJCNN). IEEE, 1–8.

[12] Ye Bi, Liqiang Song, Mengqiu Yao, Zhenyu Wu, Jianming Wang, and Jing Xiao. 2020. DCDIR: A deep cross-domain recommendation system for cold start users in insurance domain. In Proceedings of the 43rd international ACM SIGIR conference on research and development in information retrieval. 1661–1664.

[13] Ye Bi, Liqiang Song, Mengqiu Yao, Zhenyu Wu, Jianming Wang, and Jing Xiao. 2020. A heterogeneous information network based cross domain insurance recommendation system for cold start users. In Proceedings of the 43rd international ACM SIGIR conference on research and development in information retrieval. 2211–2220.

[14] Jesús Bobadilla, Fernando Ortega, Antonio Hernando, and Abraham Gutiérrez. 2013. Recommender systems survey. Knowledge-based systems 46 (2013), 109–132.

[15] Léa Briand, Guillaume Salha-Galvan, Walid Bendada, Mathieu Morlon, and Viet-Anh Tran. 2021. A semi-personalized system for user cold start recommendation on music streaming apps. In Proceedings of the 27th ACM SIGKDD conference on knowledge discovery & data mining. 2601–2609.

[16] Desheng Cai, Shengsheng Qian, Quan Fang, Jun Hu, and Changsheng Xu. 2023. User cold-start recommendation via inductive heterogeneous graph neural network. ACM Transactions on Information Systems 41, 3 (2023), 1–27.

[17] Lesly Alejandra Gonzalez Camacho and Solange Nice Alves-Souza. 2018. Social network data to alleviate cold-start in recommender system: A systematic review. Information Processing & Management 54, 4 (2018), 529–544.

[18] Jiangxia Cao, Shaoshuai Li, Bowen Yu, Xiaobo Guo, Tingwen Liu, and Bin Wang. 2023. Towards universal cross-domain recommendation. In Proceedings of the Sixteenth ACM International Conference on Web Search and Data Mining. 78–86.

[19] Jiangxia Cao, Jiawei Sheng, Xin Cong, Tingwen Liu, and Bin Wang. 2022. Cross-domain recommendation to cold-start users via variational information bottleneck. In 2022 IEEE 38th International Conference on Data Engineering (ICDE). IEEE, 2209–2223.

[20] Yi Cao, Sihao Hu, Yu Gong, Zhao Li, Yazheng Yang, Qingwen Liu, and Shouling Ji. 2022. Gift: Graph-guided feature transfer for cold-start video click-through rate prediction. In Proceedings of the 31st ACM International Conference on Information & Knowledge Management. 2964–2973.

[21] Yixin Cao, Xiang Wang, Xiangnan He, Zikun Hu, and Tat-Seng Chua. 2019. Unifying knowledge graph learning and recommendation: Towards a better understanding of user preferences. In The world wide web conference. 151–161.

[22] Yuwei Cao, Liangwei Yang, Chen Wang, Zhiwei Liu, Hao Peng, Chenyu You, and Philip S Yu. 2023. Multi-task item-attribute graph pre-training for strict cold-start item recommendation. In Proceedings of the 17th ACM Conference on Recommender Systems. 322–333.

[23] Gaode Chen, Ruina Sun, Yuezihan Jiang, Jiangxia Cao, Qi Zhang, Jingjian Lin, Han Li, Kun Gai, and Xinghua Zhang. 2024. A Multi-modal Modeling Framework for Cold-start Short-video Recommendation. In Proceedings of the 18th ACM Conference on Recommender Systems. 391–400.

[24] Hao Chen, Yuanchen Bei, Qijie Shen, Yue Xu, Sheng Zhou, Wenbing Huang, Feiran Huang, Senzhang Wang, and Xiao Huang. 2024. Macro graph neural networks for online billion-scale recommender systems. In Proceedings of the ACM on Web Conference 2024. 3598–3608.

[25] Hao Chen, Zefan Wang, Feiran Huang, Xiao Huang, Yue Xu, Yishi Lin, Peng He, and Zhoujun Li. 2022. Generative adversarial framework for cold-start item recommendation. In Proceedings of the 45th International ACM SIGIR Conference on Research and Development in Information Retrieval. 2565–2571.

[26] Lei Chen, Fajie Yuan, Jiaxi Yang, Xiangnan He, Chengming Li, and Min Yang. 2021. User-specific adaptive fine-tuning for cross-domain recommendations. IEEE Transactions on Knowledge and Data Engineering 35, 3 (2021), 3239–3252.

[27] Ting Chen, Simon Kornblith, Mohammad Norouzi, and Geofrey Hinton. 2020. A simple framework for contrastive learning of visual representations. In International conference on machine learning. PMLR, 1597–1607.

[28] Yinbo Chen, Zhuang Liu, Huijuan Xu, Trevor Darrell, and Xiaolong Wang. 2021. Meta-baseline: Exploring simple meta-learning for few-shot learning. In Proceedings of the IEEE/CVF international conference on computer vision. 9062–9071.

[29] Zhixuan Chu, Hongyan Hao, Xin Ouyang, Simeng Wang, Yan Wang, Yue Shen, Jinjie Gu, Qing Cui, Longfei Li, Siqiao Xue, et al. 2023. Leveraging large language models for pre-trained recommender systems. arXiv preprint arXiv:2308.10837 (2023).

[30] Zhendong Chu, Hongning Wang, Yun Xiao, Bo Long, and Lingfei Wu. 2023. Meta policy learning for cold-start conversational recommendation. In Proceedings of the Sixteenth ACM International Conference on Web Search and Data Mining. 222–230.

[31] Emile Contal and Garrin McGoldrick. 2024. RAGSys: Item-Cold-Start Recommender as RAG System. arXiv preprint arXiv:2405.17587 (2024).

[32] Ziqiang Cui, Yunpeng Weng, Xing Tang, Fuyuan Lyu, Dugang Liu, Xiuqiang He, and Chen Ma. 2024. Comprehending Knowledg Graphs with Large Language Models for Recommender Systems. arXiv preprint arXiv:2410.12229 (2024).

[34] Dario Di Palma. 2023. Retrieval-augmented recommender system: Enhancing recommender systems with large language models. In Proceedings of the 17th ACM Conference on Recommender Systems. 1369–1373.

[35] Manqing Dong, Feng Yuan, Lina Yao, Xiwei Xu, and Liming Zhu. 2020. Mamo: Memory-augmented meta-optimization for cold-start recommendation. In Proceedings of the 26th ACM SIGKDD international conference on knowledge discovery & data mining. 688–697.

[36] Jing Du, Zesheng Ye, Lina Yao, Bin Guo, and Zhiwen Yu. 2022. Socially-aware dual contrastive learning for cold-start recommendation. In Proceedings of the 45th International ACM SIGIR Conference on Research and Development in Information Retrieval. 1927–1932.

[37] Xiaoyu Du, Xiang Wang, Xiangnan He, Zechao Li, Jinhui Tang, and Tat-Seng Chua. 2020. How to learn item representation for cold-start multimedia recommendation?. In Proceedings of the 28th ACM International Conference on Multimedia. 3469–3477.

[38] Yuntao Du, Xinjun Zhu, Lu Chen, Ziquan Fang, and Yunjun Gao. 2022. Metakg: Meta-learning on knowledge graph for cold-star recommendation. IEEE Transactions on Knowledge and Data Engineering 35, 10 (2022), 9850–9863.

[39] Abhimanyu Dubey, Abhinav Jauhri, Abhinav Pandey, Abhishek Kadian, Ahmad Al-Dahle, Aiesha Letman, Akhil Mathur, Alan Schelten, Amy Yang, Angela Fan, et al. 2024. The llama 3 herd of models. arXiv preprint arXiv:2407.21783 (2024).

[40] Ali Mamdouh Elkahky, Yang Song, and Xiaodong He. 2015. A multi-view deep learning approach for cross domain user modeling in recommendation systems. In Proceedings of the 24th international conference on world wide web. 278–288.

[41] Philip J Feng, Pingjun Pan, Tingting Zhou, Hongxiang Chen, and Chuanjiang Luo. 2021. Zero shot on the cold-start problem: Modelagnostic interest learning for recommender systems. In Proceedings of the 30th ACM international conference on information & knowledge management. 474–483.

[42] Shanshan Feng, Haoming Lyu, Fan Li, Zhu Sun, and Caishun Chen. 2024. Where to move next: Zero-shot generalization of llms for next poi recommendation. In 2024 IEEE Conference on Artificial Intelligence (CAI). IEEE, 1530–1535.

[43] Xidong Feng, Chen Chen, Dong Li, Mengchen Zhao, Jianye Hao, and Jun Wang. 2021. CMML: Contextual modulation meta learning for cold-start recommendation. In Proceedings of the 30th ACM International Conference on Information & Knowledge Management. 484–493.

[44] Chelsea Finn, Pieter Abbeel, and Sergey Levine. 2017. Model-agnostic meta-learning for fast adaptation of deep networks. In International conference on machine learning. PMLR, 1126–1135.

[45] Chelsea Finn, Aravind Rajeswaran, Sham Kakade, and Sergey Levine. 2019. Online meta-learning. In International conference on machine learning. PMLR, 1920–1930.

[46] Wenjing Fu, Zhaohui Peng, Senzhang Wang, Yang Xu, and Jin Li. 2019. Deeply fusing reviews and contents for cold start users in cross-domain recommendation systems. In Proceedings of the AAAI Conference on Artificial Intelligence, Vol. 33. 94–101.

[47] Yunfan Gao, Yun Xiong, Xinyu Gao, Kangxiang Jia, Jinliu Pan, Yuxi Bi, Yi Dai, Jiawei Sun, and Haofen Wang. 2023. Retrieval-augmented generation for large language models: A survey. arXiv preprint arXiv:2312.10997 (2023).

[48] Shijie Geng, Shuchang Liu, Zuohui Fu, Yingqiang Ge, and Yongfeng Zhang. 2022. Recommendation as language processing (rlp): A unified pretrain, personalized prompt & predict paradigm (p5). In Proceedings of the 16th ACM Conference on Recommender Systems. 299–315.

[49] Yuqi Gong, Xichen Ding, Yehui Su, Kaiming Shen, Zhongyi Liu, and Guannan Zhang. 2023. An Unified Search and Recommendation Foundation Model for Cold-Start Scenario. In Proceedings of the 32nd ACM International Conference on Information and Knowledge Management. 4595–4601.

[50] Ian Goodfellow, Jean Pouget-Abadie, Mehdi Mirza, Bing Xu, David Warde-Farley, Sherjil Ozair, Aaron Courville, and Yoshua Bengio. 2014. Generative adversarial nets. Advances in neural information processing systems 27 (2014).

[51] Jyotirmoy Gope and Sanjay Kumar Jain. 2017. A survey on solving cold start problem in recommender systems. In 2017 International Conference on Computing, Communication and Automation (ICCCA). IEEE, 133–138.

[52] Jianping Gou, Baosheng Yu, Stephen J Maybank, and Dacheng Tao. 2021. Knowledge distillation: A survey. International Journal of Computer Vision 129, 6 (2021), 1789–1819.

[53] Jie Gui, Zhenan Sun, Yonggang Wen, Dacheng Tao, and Jieping Ye. 2021. A review on generative adversarial networks: Algorithms, theory, and applications. IEEE transactions on knowledge and data engineering 35, 4 (2021), 3313–3332.

[54] Qingyu Guo, Fuzhen Zhuang, Chuan Qin, Hengshu Zhu, Xing Xie, Hui Xiong, and Qing He. 2020. A survey on knowledge graph-based recommender systems. IEEE Transactions on Knowledge and Data Engineering 34, 8 (2020), 3549–3568.

[55] Will Hamilton, Zhitao Ying, and Jure Leskovec. 2017. Inductive Representation Learning on Large Graphs. In Advances in Neural Information Processing Systems, Vol. 30.

[56] Cuize Han, Pablo Castells, Parth Gupta, Xu Xu, and Vamsi Salaka. 2022. Addressing cold start in product search via empirical bayes. In Proceedings of the 31st ACM International Conference on Information & Knowledge Management. 3141–3151.

[57] Di Han, Xiaotian Jing, Yijun Chen, Junmin Liu, Kai Liao, and Wenting Li. 2024. Cold-Start Recommendation based on Knowledg Graph and Meta-Learning under Positive and Negative sampling. ACM Transactions on Recommender Systems (2024).

[58] Jun Han and Qiang Liu. 2018. Stein variational gradient descent without gradient. In International Conference on Machine Learning. PMLR, 1900–1908.

[59] Casper Hansen, Christian Hansen, Jakob Grue Simonsen, Stephen Alstrup, and Christina Lioma. 2020. Content-aware neural hashing for cold-start recommendation. In Proceedings of the 43rd International ACM SIGIR Conference on Research and Development in Information Retrieval. 971–980.

[60] Bowen Hao, Hongzhi Yin, Jing Zhang, Cuiping Li, and Hong Chen. 2023. A Multi-strategy-based Pre-training Method for Cold-star Recommendation. ACM Transactions on Information Systems 41, 2 (2023), 1–24.

[61] Bowen Hao, Jing Zhang, Hongzhi Yin, Cuiping Li, and Hong Chen. 2021. Pre-training graph neural networks for cold-start users and items representation. In Proceedings of the 14th ACM International Conference on Web Search and Data Mining. 265–273.

[62] Jia He, Rui Liu, Fuzhen Zhuang, Fen Lin, Cheng Niu, and Qing He. 2018. A general cross-domain recommendation framework via Bayesian neural network. In 2018 IEEE International Conference on Data Mining (ICDM). IEEE, 1001–1006.

[63] Langzhou He, Songxin Wang, Jiaxin Wang, Chao Gao, and Li Tao. 2022. Integrating Global Features into Neural Collaborative Filtering. In International Conference on Knowledge Science, Engineering and Management. Springer, 325–336.

[64] Xiangnan He, Kuan Deng, Xiang Wang, Yan Li, Yongdong Zhang, and Meng Wang. 2020. Lightgcn: Simplifying and powering graph convolution network for recommendation. In Proceedings of the 43rd International ACM SIGIR conference on research and development in Information Retrieval. 639–648.

[65] Xiangnan He, Zhankui He, Jingkuan Song, Zhenguang Liu, Yu-Gang Jiang, and Tat-Seng Chua. 2018. NAIS: Neural attentive item similarity model for recommendation. IEEE Transactions on Knowledge and Data Engineering 30, 12 (2018), 2354–2366.

[66] Xiangnan He, Lizi Liao, Hanwang Zhang, Liqiang Nie, Xia Hu, and Tat-Seng Chua. 2017. Neural collaborative filtering. In Proceedings of the 26th international conference on world wide web. 173–182.

[67] Zhankui He, Zhouhang Xie, Rahul Jha, Harald Steck, Dawen Liang, Yesu Feng, Bodhisattwa Prasad Majumder, Nathan Kallus, and Julian McAuley. 2023. Large language models as zero-shot conversational recommenders. In Proceedings of the 32nd ACM international conference on information and knowledge management. 720–730.

[68] Yassine Himeur, Shahab Saquib Sohail, Faycal Bensaali, Abbes Amira, and Mamoun Alazab. 2022. Latest trends of security and privacy in recommender systems: a comprehensive review and future perspectives. Computers & Security 118 (2022), 102746.

[69] Yupeng Hou, Junjie Zhang, Zihan Lin, Hongyu Lu, Ruobing Xie, Julian McAuley, and Wayne Xin Zhao. 2024. Large language models are zero-shot rankers for recommender systems. In European Conference on Information Retrieval. Springer, 364–381.

[70] Edward J Hu, yelong shen, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, and Weizhu Chen. 2022. LoRA: Low-Rank Adaptation of Large Language Models. In International Conference on Learning Representations.

[71] Jun Hu, Wenwen Xia, Xiaolu Zhang, Chilin Fu, Weichang Wu, Zhaoxin Huan, Ang Li, Zuoli Tang, and Jun Zhou. 2024. Enhancing sequential recommendation via llm-based semantic embedding learning. In Companion Proceedings of the ACM on Web Conference 2024. 103–111.

[72] Liang Hu, Longbing Cao, Jian Cao, Zhiping Gu, Guandong Xu, and Dingyu Yang. 2016. Learning informative priors from heterogeneous domains to improve recommendation in cold-start user domains. ACM Transactions on Information Systems (TOIS) 35, 2 (2016), 1–37.

[73] Qian Hu, Lei Tan, Daofu Gong, Yan Li, and Wenjuan Bu. 2024. Graph attention networks with adaptive neighbor graph aggregation for cold-start recommendation. Journal of Intelligent Information Systems (2024), 1–20.

[74] Ziniu Hu, Yuxiao Dong, Kuansan Wang, and Yizhou Sun. 2020. Heterogeneous graph transformer. In Proceedings of the web conference 2020. 2704–2710.

[75] Feiran Huang, Zefan Wang, Xiao Huang, Yufeng Qian, Zhetao Li, and Hao Chen. 2023. Aligning distillation for cold-start item recommendation. In Proceedings of the 46th International ACM SIGIR Conference on Research and Development in Information Retrieval. 1147–1157.

[76] Feiran Huang, Zhenghang Yang, Junyi Jiang, Yuanchen Bei, Yijie Zhang, and Hao Chen. 2024. Large Language Model Interaction Simulator for Cold-Start Item Recommendation. arXiv preprint arXiv:2402.09176 (2024).

[77] Weiming Huang, Baisong Liu, and Hao Tang. 2019. Privacy protection for recommendation system: a survey. In Journal of Physics: Conference Series, Vol. 1325. IOP Publishing, 012087.

[78] Leo Iaquinta, Marco De Gemmis, Pasquale Lops, Giovanni Semeraro, Michele Filannino, and Piero Molino. 2008. Introducing serendipity in a content-based recommender system. In 2008 eighth international conference on hybrid intelligent systems. IEEE, 168–173.

[79] Abdul Jabbar, Xi Li, and Bourahla Omar. 2021. A survey on generative adversarial networks: Variants, applications, and training. ACM Computing Surveys (CSUR) 54, 8 (2021), 1–49.

[80] Muhammad Abdullah Jamal and Guo-Jun Qi. 2019. Task agnostic meta-learning for few-shot learning. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition. 11719–11727.

[81] Danish Javeed, Muhammad Shahid Saeed, Prabhat Kumar, Alireza Jolfaei, Shareeful Islam, and AKM Najmul Islam. 2023. Federated learning-based personalized recommendation systems: An overview on security and privacy challenges. IEEE Transactions on Consumer Electronics (2023).

[82] Luo Ji, Qi Qin, Bingqing Han, and Hongxia Yang. 2021. Reinforcement learning to optimize lifetime value in cold-start recommendation. In Proceedings of the 30th ACM International Conference on Information & Knowledge Management. 782–791.

[83] Shaoxiong Ji, Shirui Pan, Erik Cambria, Pekka Marttinen, and S Yu Philip. 2021. A survey on knowledge graphs: Representation, acquisition, and applications. IEEE transactions on neural networks and learning systems 33, 2 (2021), 494–514.

[84] Hao Jiang, Chuanzhen Li, Juanjuan Cai, Runyu Tian, and Jingling Wang. 2023. Self-supervised Contrastive Enhancement with Symmetric Few-shot Learning Towers for Cold-start News Recommendation. In Proceedings of the 32nd ACM International Conference on Information and Knowledge Management. 945–954.

[85] Meng Jiang, Peng Cui, Xumin Chen, Fei Wang, Wenwu Zhu, and Shiqiang Yang. 2015. Social recommendation with cross-domain transferable knowledge. IEEE transactions on knowledge and data engineering 27, 11 (2015), 3084–3097.

[86] Bowen Jin, Chen Gao, Xiangnan He, Depeng Jin, and Yong Li. 2020. Multi-behavior recommendation with graph convolutional networks. In Proceedings of the 43rd international ACM SIGIR conference on research and development in information retrieval. 659–668.

[87] Jipeng Jin, Guangben Lu, Sijia Li, Xiaofeng Gao, Ao Tan, and Lifeng Wang. 2023. Automatic Fusion Network for Cold-start CVR Prediction with Explicit Multi-Level Representation. In 2023 IEEE 39th International Conference on Data Engineering (ICDE). IEEE, 3440–3452.

[88] Seiya Jumonji, Kazuya Sakai, Min-Te Sun, and Wei-Shinn Ku. 2021. Privacy-preserving collaborative filtering using fully homomorphic encryption. IEEE Transactions on Knowledge and Data Engineering 35, 3 (2021), 2961–2974.

[89] SeongKu Kang, Junyoung Hwang, Dongha Lee, and Hwanjo Yu. 2019. Semi-supervised learning for cross-domain recommendation to cold-start users. In Proceedings of the 28th ACM international conference on information and knowledge management. 1563–1572.

[90] Wang-Cheng Kang and Julian McAuley. 2018. Self-attentive sequential recommendation. In 2018 IEEE international conference on data mining (ICDM). IEEE, 197–206.

[91] Zhao Kang, Haiqi Pan, Steven CH Hoi, and Zenglin Xu. 2019. Robust graph learning from noisy data. IEEE transactions on cybernetics 50, 5 (2019), 1833–1843.

[92] Muhammad Murad Khan, Roliana Ibrahim, and Imran Ghani. 2017. Cross domain recommender systems: A systematic literature review. ACM Computing Surveys (CSUR) 50, 3 (2017), 1–34.

[93] Hai-Dang Kieu, Minh Duc Nguyen, Thanh-Son Nguyen, and Dung D Le. 2024. Keyword-driven Retrieval-Augmented Large Language Models for Cold-start User Recommendations. arXiv preprint arXiv:2405.19612 (2024).

[94] Jinri Kim, Eungi Kim, Kwangeun Yeo, Yujin Jeon, Chanwoo Kim, Sewon Lee, and Joonseok Lee. 2024. Content-based Graph Reconstruc tion for Cold-start Item Recommendation. In Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval. 1263–1273.

[95] Jooeun Kim, Jinri Kim, Kwangeun Yeo, Eungi Kim, Kyoung-Woon On, Jonghwan Mun, and Joonseok Lee. 2024. General Item Representation Learning for Cold-start Content Recommendations. arXiv preprint arXiv:2404.13808 (2024).

[96] Jaehyeon Kim, Jungil Kong, and Juhee Son. 2021. Conditional variational autoencoder with adversarial learning for end-to-end text-to-speech. In International Conference on Machine Learning. PMLR, 5530–5540.

[97] Jinsu Kim, Dongyoung Koo, Yuna Kim, Hyunsoo Yoon, Junbum Shin, and Sungwook Kim. 2018. Eficient privacy-preserving matrix factorization for recommendation via fully homomorphic encryption. ACM Transactions on Privacy and Security (TOPS) 21, 4 (2018), 1–30.

[98] Minchang Kim, Yongjin Yang, Jung Hyun Ryu, and Taesup Kim. 2023. Meta-Learning with Adaptive Weighted Loss for Imbalanced Cold-Start Recommendation. In Proceedings of the 32nd ACM International Conference on Information and Knowledge Management. 1077–1086.

[99] Sein Kim, Hongseok Kang, Seungyoon Choi, Donghyun Kim, Minchul Yang, and Chanyoung Park. 2024. Large language models meet collaborative filtering: an eficient all-round LLM-based recommender system. In Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining. 1395–1406.

[100] Thomas N. Kipf and Max Welling. 2017. Semi-Supervised Classification with Graph Convolutional Networks. In International Conference on Learning Representations.

[101] Thomas N Kipf and Max Welling. 2022. Semi-Supervised Classification with Graph Convolutional Networks. In International Conference on Learning Representations.

[102] Menglin Kong, Li Fan, Shengze Xu, Xingquan Li, Muzhou Hou, and Cong Cao. 2024. Collaborative Filtering in Latent Space: A Bayesian Approach for Cold-Start Music Recommendation. In Pacific-Asia Conference on Knowledge Discovery and Data Mining. Springer, 105–117.

[103] Hoyeop Lee, Jinbae Im, Seongwon Jang, Hyunsouk Cho, and Sehee Chung. 2019. Melu: Meta-learned user preference estimator for cold-start recommendation. In Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining. 1073–1082

[104] Cheng-Te Li, Chia-Tai Hsu, and Man-Kwan Shan. 2018. A cross-domain recommendation mechanism for cold-start users based on partial least squares regression. ACM Transactions on Intelligent Systems and Technology (TIST) 9, 6 (2018), 1–26.

[105] Hourun Li, Yifan Wang, Zhiping Xiao, Jia Yang, Changling Zhou, Ming Zhang, and Wei Ju. 2024. DisCo: Graph-Based Disentangled Contrastive Learning for Cold-Start Cross-Domain Recommendation. arXiv preprint arXiv:2412.15005 (2024).

[106] Jingjing Li, Mengmeng Jing, Ke Lu, Lei Zhu, Yang Yang, and Zi Huang. 2019. From zero-shot learning to cold-start recommendation. In Proceedings of the AAAI conference on artificial intelligence, Vol. 33. 4189–4196.

[107] Junyi Li, Tianyi Tang, Wayne Xin Zhao, Jian-Yun Nie, and Ji-Rong Wen. 2024. Pre-trained language models for text generation: A survey. Comput. Surveys 56, 9 (2024), 1–39.

[108] Lei Li, Yongfeng Zhang, and Li Chen. 2023. Prompt distillation for eficient llm-based recommendation. In Proceedings of the 32nd ACM International Conference on Information and Knowledge Management. 1348–1357.

[109] Pengyang Li, Rong Chen, Quan Liu, Jian Xu, and Bo Zheng. 2022. Transform cold-start users into warm via fused behaviors in large-scale recommendation. In Proceedings of the 45th International ACM SIGIR Conference on Research and Development in Informatio Retrieval. 2013–2017.

[110] Peibo Li, Maarten de Rijke, Hao Xue, Shuang Ao, Yang Song, and Flora D Salim. 2024. Large language models for next point-of-interest recommendation. In Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval. 1463–1472.

[111] Xiaodong Li, Jiawei Sheng, Jiangxia Cao, Wenyuan Zhang, Quangang Li, and Tingwen Liu. 2024. CDRNP: Cross-Domain Recommen dation to Cold-Start Users via Neural Process. In Proceedings of the 17th ACM International Conference on Web Search and Data Mining. 378–386.

[112] Xiao Li, Li Sun, Mengjie Ling, and Yan Peng. 2023. A survey of graph neural network based recommendation in social networks. Neurocomputing 549 (2023), 126441.

[113] Yueqing Liang, Liangwei Yang, Chen Wang, Xiongxiao Xu, Philip S Yu, and Kai Shu. 2024. Taxonomy-Guided Zero-Shot Recommenda tions with LLMs. arXiv preprint arXiv:2406.14043 (2024).

[114] Allen Lin, Jianling Wang, Ziwei Zhu, and James Caverlee. 2022. Quantifying and mitigating popularity bias in conversational recommender systems. In Proceedings of the 31st ACM international conference on information & knowledge management. 1238–1247.

[115] Xinyu Lin, Wenjie Wang, Yongqi Li, Fuli Feng, See-Kiong Ng, and Tat-Seng Chua. 2024. Bridging items and language: A transition paradigm for large language model-based recommendation. In Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining. 1816–1826.

[116] Xinyu Lin, Wenjie Wang, Jujia Zhao, Yongqi Li, Fuli Feng, and Tat-Seng Chua. 2024. Temporally and distributionally robust optimization for cold-start recommendation. In Proceedings of the AAAI Conference on Artificial Intelligence, Vol. 38. 8750–8758

[117] Xixun Lin, Jia Wu, Chuan Zhou, Shirui Pan, Yanan Cao, and Bin Wang. 2021. Task-adaptive neural process for user cold-start recommendation. In Proceedings of the Web Conference 2021. 1306–1316.

[118] Bulou Liu, Bing Bai, Weibang Xie, Yiwen Guo, and Hao Chen. 2022. Task-optimized user clustering based on mobile app usage for cold-start recommendations. In Proceedings of the 28th ACM SIGKDD Conference on Knowledge Discovery and Data Mining. 3347–3356.

[119] Bo Liu, Ying Wei, Yu Zhang, Zhixian Yan, and Qiang Yang. 2018. Transferable contextual bandit for cross-domain recommendation. In Proceedings of the AAAI Conference on Artificial Intelligence, Vol. 32.

[120] Han Liu, Hongxiang Lin, Xiaotong Zhang, Fenglong Ma, Hongyang Chen, Lei Wang, Hong Yu, and Xianchao Zhang. 2023. Boosting Meta-Learning Cold-Start Recommendation with Graph Neural Network. In Proceedings of the 32nd ACM International Conference on Information and Knowledge Management. 4105–4109.

[121] Haomiao Liu, Ruiping Wang, Shiguang Shan, and Xilin Chen. 2016. Deep supervised hashing for fast image retrieval. In Proceedings of the IEEE conference on computer vision and pattern recognition. 2064–2072.

[122] Junling Liu, Chao Liu, Peilin Zhou, Renjie Lv, Kang Zhou, and Yan Zhang. 2023. Is chatgpt a good recommender? a preliminary study. arXiv preprint arXiv:2304.10149 (2023).

[123] Qidong Liu, Jiaxi Hu, Yutian Xiao, Xiangyu Zhao, Jingtong Gao, Wanyu Wang, Qing Li, and Jiliang Tang. 2024. Multimodal recommender systems: A survey. Comput. Surveys 57, 2 (2024), 1–17.

[124] Ruochen Liu, Hao Chen, Yuanchen Bei, Qijie Shen, Fangwei Zhong, Senzhang Wang, and Jianxin Wang. 2024. Fine Tuning Out-of Vocabulary Item Recommendation with User Sequence Imagination. In The Thirty-eighth Annual Conference on Neural Information Processing Systems.

[125] Siwei Liu, Iadh Ounis, Craig Macdonald, and Zaiqiao Meng. 2020. A heterogeneous graph neural model for cold-start recommendation. In Proceedings of the 43rd international ACM SIGIR conference on research and development in information retrieval. 2029–2032.

[126] Taichi Liu, Chen Gao, Zhenyu Wang, Dong Li, Jianye Hao, Depeng Jin, and Yong Li. 2023. Uncertainty-aware Consistency Learning for Cold-Start Item Recommendation. In Proceedings of the 46th International ACM SIGIR Conference on Research and Development in Information Retrieval. 2466–2470.

[127] Weiming Liu, Chaochao Chen, Xinting Liao, Mengling Hu, Jiajie Su, Yanchao Tan, and Fan Wang. 2024. User Distribution Mapping Modelling with Collaborative Filtering for Cross Domain Recommendation. In Proceedings of the ACM on Web Conference 2024. 334–343.

[128] Weiming Liu, Jiajie Su, Chaochao Chen, and Xiaolin Zheng. 2021. Leveraging distribution alignment via stein path for cross-domain cold-start recommendation. Advances in Neural Information Processing Systems 34 (2021), 19223–19234.

[129] Weiming Liu, Xiaolin Zheng, Jiajie Su, Longfei Zheng, Chaochao Chen, and Mengling Hu. 2023. Contrastive proxy kernel stein path alignment for cross-domain cold-start recommendation. IEEE Transactions on Knowledge and Data Engineering 35, 11 (2023), 11216–11230.

[130] Yuqing Liu, Yu Wang, Lichao Sun, and Philip S Yu. 2024. Rec-GPT4V: Multimodal Recommendation with Large Vision-Language Models. arXiv preprint arXiv:2402.08670 (2024).

[131] Yifan Liu, Kangning Zhang, Xiangyuan Ren, Yanhua Huang, Jiarui Jin, Yingjie Qin, Ruilong Su, Ruiwen Xu, Yong Yu, and Weinan Zhang. 2024. AlignRec: Aligning and Training in Multimodal Recommendations. In Proceedings of the 33rd ACM International Conference on Information and Knowledge Management. 1503–1512.

[132] Zhen Liu, Jingyu Tian, Lingxi Zhao, and Yanling Zhang. 2020. Attentive-feature transfer based on mapping for cross-domai recommendation. In 2020 International Conference on Data Mining Workshops (ICDMW). IEEE, 151–158.

[133] Pasquale Lops, Marco De Gemmis, and Giovanni Semeraro. 2011. Content-based recommender systems: State of the art and trends. Recommender systems handbook (2011), 73–105.

[134] Yuanfu Lu, Yuan Fang, and Chuan Shi. 2020. Meta-learning on heterogeneous information networks for cold-start recommendation. In Proceedings of the 26th ACM SIGKDD international conference on knowledge discovery & data mining. 1563–1573.

[135] Haokai Ma, Zhuang Qi, Xinxin Dong, Xiangxian Li, Yuze Zheng, Xiangxu Meng, and Lei Meng. 2023. Cross-modal content inferenc and feature enrichment for cold-start recommendation. In 2023 International Joint Conference on Neural Networks (IJCNN). IEEE, 1–8.

[136] Qiyao Ma, Xubin Ren, and Chao Huang. 2024. XRec: Large Language Models for Explainable Recommendation. arXiv preprint arXiv:2406.02377 (2024).

[137] Yao Ma, Xiaorui Liu, Neil Shah, and Jiliang Tang. 2022. Is Homophily a Necessity for Graph Neural Networks?. In International Conference on Learning Representations.

[138] Tong Man, Huawei Shen, Xiaolong Jin, and Xueqi Cheng. 2017. Cross-domain recommendation: An embedding and mapping approach.. In IJCAI, Vol. 17. 2464–2470.

[139] Brian McFee, Luke Barrington, and Gert Lanckriet. 2012. Learning content similarity for music recommendation. IEEE transactions on audio, speech, and language processing 20, 8 (2012), 2207–2218.

[140] Miller McPherson, Lynn Smith-Lovin, and James M Cook. 2001. Birds of a feather: Homophily in social networks. Annual review of sociology 27, 1 (2001), 415–444.

[141] Wu Meihan, Li Li, Chang Tao, Eric Rigall, Wang Xiaodong, and Xu Cheng-Zhong. 2022. Fedcdr: federated cross-domain recommenda tion for privacy-preserving rating prediction. In Proceedings of the 31st ACM International Conference on Information & Knowledge Management. 2179–2188.

[142] Bonan Min, Hayley Ross, Elior Sulem, Amir Pouran Ben Veyseh, Thien Huu Nguyen, Oscar Sainz, Eneko Agirre, Ilana Heintz, and Dan Roth. 2023. Recent advances in natural language processing via large pre-trained language models: A survey. Comput. Surveys 56, 2 (2023), 1–40.

[143] Nima Mirbakhsh and Charles X Ling. 2015. Improving top-n recommendation for cold-start users via cross-domain information. ACM Transactions on Knowledge Discovery from Data (TKDD) 9, 4 (2015), 1–19.

[144] Thomas M Moerland, Joost Broekens, Aske Plaat, Catholijn M Jonker, et al. 2023. Model-based reinforcement learning: A survey. Foundations and Trends® in Machine Learning 16, 1 (2023), 1–118.

[145] Marta Moscati. 2024. Multimodal Representation Learning for High-Quality Recommendations in Cold-Start and Beyond-Accuracy. In Proceedings of the 18th ACM Conference on Recommender Systems. 1290–1295.

[146] Sheshera Mysore, Andrew McCallum, and Hamed Zamani. 2023. Large language model augmented narrative driven recommendations. In Proceedings of the 17th ACM Conference on Recommender Systems. 777–783.

[147] Krishna Prasad Neupane, Ervine Zheng, Yu Kong, and Qi Yu. 2022. A dynamic meta-learning model for time-sensitive cold-start recommendations. In Proceedings of the AAAI Conference on Artificial Intelligence, Vol. 36. 7868–7876.

[148] Wentao Ouyang, Xiuwu Zhang, Shukui Ren, Li Li, Kun Zhang, Jinmei Luo, Zhaojie Liu, and Yanlong Du. 2021. Learning graph meta embeddings for cold-start ads in click-through rate prediction. In Proceedings of the 44th International ACM SIGIR Conference on Research and Development in Information Retrieval. 1157–1166

[149] Feiyang Pan, Shuokai Li, Xiang Ao, Pingzhong Tang, and Qing He. 2019. Warm up cold-start advertisements: Improving ctr predictions via learning to learn id embeddings. In Proceedings of the 42nd International ACM SIGIR Conference on Research and Development in Information Retrieval. 695–704.

[150] Hui Pan, Senlin Luo, Xinshuai Li, Limin Pan, and Zhouting Wu. 2024. Meta-learning on dynamic node clustering knowledge graph for cold-start recommendation. Neurocomputing 602 (2024), 128192.

[151] Xingyu Pan, Yushuo Chen, Changxin Tian, Zihan Lin, Jinpeng Wang, He Hu, and Wayne Xin Zhao. 2022. Multimodal meta-learning fo cold-start sequential recommendation. In Proceedings of the 31st ACM international conference on information & knowledge management. 3421–3430.

[152] Deepak Kumar Panda and Sanjog Ray. 2022. Approaches and algorithms to mitigate cold start problems in recommender systems: a systematic literature review. Journal of Intelligent Information Systems 59, 2 (2022), 341–366.

[153] Haoyu Pang, Fausto Giunchiglia, Ximing Li, Renchu Guan, and Xiaoyue Feng. 2022. PNMTA: A pretrained network modulation and task adaptation approach for user cold-start recommendation. In Proceedings of the ACM Web Conference 2022. 348–359.

[154] Wonpyo Park, Dongju Kim, Yan Lu, and Minsu Cho. 2019. Relational knowledge distillation. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition. 3967–3976.

[155] Chengmei Peng, Lei Zhu, Yang Xu, Yaping Li, and Lei Guo. 2022. Binary multi-modal matrix factorization for fast item cold-start recommendation. Neurocomputing 507 (2022), 145–156.

[156] Adnan Qayyum, Junaid Qadir, Muhammad Bilal, and Ala Al-Fuqaha. 2020. Secure and robust machine learning for healthcare: A survey. IEEE Reviews in Biomedical Engineering 14 (2020), 156–180.

[157] Colin Rafel, Noam Shazeer, Adam Roberts, Katherine Lee, Sharan Narang, Michael Matena, Yanqi Zhou, Wei Li, and Peter J Liu. 2020. Exploring the limits of transfer learning with a unified text-to-text transformer. Journal of machine learning research 21, 140 (2020), 1–67.

[158] Xubin Ren and Chao Huang. 2024. EasyRec: Simple yet Efective Language Models for Recommendation. arXiv preprint arXiv:2408.08821 (2024).

[159] Xubin Ren, Jiabin Tang, Dawei Yin, Nitesh Chawla, and Chao Huang. 2024. A survey of large language models for graphs. In Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining. 6616–6626.

[160] Scott Sanner, Krisztian Balog, Filip Radlinski, Ben Wedin, and Lucas Dixon. 2023. Large language models are competitive near cold-start recommenders for language-and item-based preferences. In Proceedings of the 17th ACM conference on recommender systems. 890–896.

[161] Divya Saxena and Jiannong Cao. 2021. Generative adversarial networks (GANs) challenges, solutions, and future directions. ACM Computing Surveys (CSUR) 54, 3 (2021), 1–42.

[162] Alessandro Sbandi, Federico Siciliano, and Fabrizio Silvestri. 2024. Mitigating Extreme Cold Start in Graph-based RecSys through Re-ranking. In Proceedings of the 33rd ACM International Conference on Information and Knowledge Management. 4844–4851.

[163] Rachna Sethi and Monica Mehrotra. 2021. Cold start in recommender systems—a survey from domain perspective. In Intelligent Data Communication Technologies and Internet of Things: Proceedings of ICICI 2020. Springer, 223–232.

[164] Sulthana Shams, Daron Anderson, and Douglas Leith. 2021. Cluster-based bandits: Fast cold-start for recommender system new users. In Proceedings of the 44th International ACM SIGIR Conference on Research and Development in Information Retrieval. 1613–1616.

[165] Kartik Sharma, Yeon-Chang Lee, Sivagami Nambi, Aditya Salian, Shlok Shah, Sang-Wook Kim, and Srijan Kumar. 2024. A survey of graph neural networks for social recommender systems. Comput. Surveys 56, 10 (2024), 1–34.

[166] Tingjia Shen, Hao Wang, Jiaqing Zhang, Sirui Zhao, Liangyue Li, Zulong Chen, Defu Lian, and Enhong Chen. 2024. Exploring User Retrieval Integration towards Large Language Models for Cross-Domain Sequential Recommendation. arXiv preprint arXiv:2406.03085 (2024).

[167] Hyejin Shin, Sungwook Kim, Junbum Shin, and Xiaokui Xiao. 2018. Privacy enhanced matrix factorization for recommendation with local diferential privacy. IEEE Transactions on Knowledge and Data Engineering 30, 9 (2018), 1770–1782.

[168] Damien Sileo, Wout Vossen, and Robbe Raymaekers. 2022. Zero-shot recommendation as language modeling. In European Conference on Information Retrieval. Springer, 223–230.

[169] Nicollas Silva, Thiago Silva, Heitor Werneck, Leonardo Rocha, and Adriano Pereira. 2023. User cold-start problem in multi-armed bandits: When the first recommendations guide the user’s experience. ACM Transactions on Recommender Systems 1, 1 (2023), 1–24.

[170] Hongzu Su, Yifei Zhang, Xuejiao Yang, Hua Hua, Shuangyang Wang, and Jingjing Li. 2022. Cross-domain recommendation via adversarial adaptation. In Proceedings of the 31st ACM international conference on information & knowledge management. 1808–1817.

[171] Caiqi Sun, Jiewei Gu, BinBin Hu, Xin Dong, Hai Li, Lei Cheng, and Linjian Mo. 2023. REMIT: reinforced multi-interest transfer for cross-domain recommendation. In Proceedings of the AAAI Conference on Artificial Intelligence, Vol. 37. 9900–9908.

[172] Fei Sun, Jun Liu, Jian Wu, Changhua Pei, Xiao Lin, Wenwu Ou, and Peng Jiang. 2019. BERT4Rec: Sequential recommendation with bidirectional encoder representations from transformer. In Proceedings of the 28th ACM international conference on information and knowledge management. 1441–1450.

[173] Ruixuan Sun, Xinyi Li, Avinash Akella, and Joseph A Konstan. 2024. Large Language Models as Conversational Movie Recommenders: A User Study. arXiv preprint arXiv:2404.19093 (2024).

[174] Xuehan Sun, Tianyao Shi, Xiaofeng Gao, Yanrong Kang, and Guihai Chen. 2021. FORM: follow the online regularized meta-leader for cold-start recommendation. In Proceedings of the 44th International ACM SIGIR Conference on Research and Development in Information Retrieval. 1177–1186.

[175] Juntao Tan, Shuyuan Xu, Wenyue Hua, Yingqiang Ge, Zelong Li, and Yongfeng Zhang. 2024. Idgenrec: Llm-recsys alignment with textual id learning. In Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval. 355–364.

[176] Zuoli Tang, Zhaoxin Huan, Zihao Li, Xiaolu Zhang, Jun Hu, Chilin Fu, Jun Zhou, and Chenliang Li. 2023. One model for all: Large language models are domain-agnostic recommendation systems. arXiv preprint arXiv:2310.14304 (2023).

[177] Wanjie Tao, Yu Li, Liangyue Li, Zulong Chen, Hong Wen, Peilin Chen, Tingting Liang, and Quan Lu. 2022. SMINet: State-aware multi-aspect interests representation network for cold-start users recommendation. In Proceedings of the AAAI conference on artificial intelligence, Vol. 36. 8476–8484.

[178] Changxin Tian, Yuexiang Xie, Xu Chen, Yaliang Li, and Xin Zhao. 2024. Privacy-Preserving Cross-Domain Recommendation with Federated Graph Learning. ACM Transactions on Information Systems 42, 5 (2024), 1–29.

[179] Riku Togashi, Mayu Otani, and Shin’ichi Satoh. 2021. Alleviating cold-start problems in recommendation through pseudo-labellin over knowledge graph. In Proceedings of the 14th ACM international conference on web search and data mining. 931–939.

[180] Ajay Krishna Vajjala, Dipak Falgun Meher, Shrunal Pothagoni, Ziwei Zhu, and David S Rosenblum. 2024. Vietoris-rips complex: A new direction for cross-domain cold-start recommendation. In Proceedings of the 2024 SIAM International Conference on Data Mining (SDM). SIAM, 761–769.

[181] Aaron Van den Oord, Sander Dieleman, and Benjamin Schrauwen. 2013. Deep content-based music recommendation. Advances in neural information processing systems 26 (2013).

[182] Oriol Vinyals, Charles Blundell, Timothy Lillicrap, Daan Wierstra, et al. 2016. Matching networks for one shot learning. Advances in neural information processing systems 29 (2016).

[183] Maksims Volkovs, Guangwei Yu, and Tomi Poutanen. 2017. Dropoutnet: Addressing cold start in recommender systems. Advances in neural information processing systems 30 (2017).

[184] Bei Wang, Chenrui Zhang, Hao Zhang, Xiaoqing Lyu, and Zhi Tang. 2020. Dual autoencoder network with swap reconstruction for cold-start recommendation. In Proceedings of the 29th ACM International Conference on Information & Knowledge Management. 2249–2252

[185] Chong Wang and David M Blei. 2011. Collaborative topic modeling for recommending scientific articles. In Proceedings of the 17th ACM SIGKDD international conference on Knowledge discovery and data mining. 448–456.

[186] Cheng Wang, Mathias Niepert, and Hui Li. 2018. LRMM: Learning to recommend with missing modalities. arXiv preprint arXiv:1808.06791 (2018).

[187] Cheng Wang, Mathias Niepert, and Hui Li. 2019. RecSys-DAN: Discriminative adversarial networks for cross-domain recommender systems. IEEE transactions on neural networks and learning systems 31, 8 (2019), 2731–2740.

[188] Chunyang Wang, Yanmin Zhu, Aixin Sun, Zhaobo Wang, and Ke Wang. 2023. A Preference Learning Decoupling Framework for User Cold-Start Recommendation. In Proceedings of the 46th International ACM SIGIR Conference on Research and Development in Information Retrieval. 1168–1177.

[189] Hanxin Wang, Daichi Amagata, Takuya Maekawa, Takahiro Hara, Hao Niu, Kei Yonekawa, and Mori Kurokawa. 2019. Preliminar investigation of alleviating user cold-start problem in e-commerce with deep cross-domain recommender system. In Companion Proceedings of The 2019 World Wide Web Conference. 398–403.

[190] Ji Wang, Weidong Bao, Lichao Sun, Xiaomin Zhu, Bokai Cao, and S Yu Philip. 2019. Private model compression via knowledge distillation. In Proceedings of the AAAI Conference on Artificial Intelligence, Vol. 33. 1190–1197.

[191] Jianling Wang, Kaize Ding, and James Caverlee. 2021. Sequential recommendation for cold-start users with meta transitional learning. In Proceedings of the 44th International ACM SIGIR Conference on Research and Development in Information Retrieval. 1783–1787.

[192] Jianling Wang, Haokai Lu, James Caverlee, Ed H Chi, and Minmin Chen. 2024. Large Language Models as Data Augmenters for Cold-Start Item Recommendation. In Companion Proceedings of the ACM on Web Conference 2024. 726–729.

[193] Jianling Wang, Haokai Lu, and Minmin Chen. 2024. Fresh Content Recommendation at Scale: A Multi-funnel Solution and the Potential of LLMs. In Proceedings of the 17th ACM International Conference on Web Search and Data Mining. 1186–1187.

[194] Jianling Wang, Haokai Lu, Yifan Liu, He Ma, Yueqi Wang, Yang Gu, Shuzhou Zhang, Ningren Han, Shuchao Bi, Lexi Baugher, et al. 2024. Llms for user interest exploration in large-scale recommendation systems. In Proceedings of the 18th ACM Conference on Recommender Systems. 872–877.

[195] Li Wang, Binbin Jin, Zhenya Huang, Hongke Zhao, Defu Lian, Qi Liu, and Enhong Chen. 2021. Preference-adaptive meta-learning for cold-start recommendation.. In IJCAI. 1607–1614.

[196] Lei Wang and Ee-Peng Lim. 2023. Zero-shot next-item recommendation using large pretrained language models. arXiv preprint arXiv:2304.03153 (2023).

[197] Lin Wang and Kuk-Jin Yoon. 2021. Knowledge distillation and student-teacher learning for visual intelligence: A review and new outlooks. IEEE transactions on pattern analysis and machine intelligence 44, 6 (2021), 3048–3068.

[198] Ning Wang, Minnan Luo, Kaize Ding, Lingling Zhang, Jundong Li, and Qinghua Zheng. 2020. Graph few-shot learning with attribut matching. In Proceedings of the 29th ACM International Conference on Information & Knowledge Management. 1545–1554.

[199] Shuai Wang, Kun Zhang, Le Wu, Haiping Ma, Richang Hong, and Meng Wang. 2021. Privileged graph distillation for cold start recommendation. In Proceedings of the 44th International ACM SIGIR Conference on Research and Development in Information Retrieval. 1187–1196.

[200] Tianxin Wang, Fuzhen Zhuang, Zhiqiang Zhang, Daixin Wang, Jun Zhou, and Qing He. 2021. Low-dimensional alignment for cross-domain recommendation. In Proceedings of the 30th ACM international conference on information & knowledge management. 3508–3512

[201] Wenbo Wang, Ben Chen, Bingquan Liu, Xinxin Wang, Luwei Yang, Wen Jiang, Wei Ning, and Jian Guan. 2024. Mutual Information Assisted Graph Convolution Network for Cold-Start Recommendation. In ICASSP 2024-2024 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP). IEEE, 6785–6789.

[202] Wenbo Wang, Bingquan Liu, Lili Shan, Chengjie Sun, Ben Chen, and Jian Guan. 2024. Preference Aware Dual Contrastive Learning for Item Cold-Start Recommendation. In Proceedings of the AAAI Conference on Artificial Intelligence, Vol. 38. 9125–9132.

[203] Xiang Wang, Xiangnan He, Yixin Cao, Meng Liu, and Tat-Seng Chua. 2019. Kgat: Knowledge graph attention network for recommen dation. In Proceedings of the 25th ACM SIGKDD international conference on knowledge discovery & data mining. 950–958.

[204] Xiang Wang, Xiangnan He, Meng Wang, Fuli Feng, and Tat-Seng Chua. 2019. Neural graph collaborative filtering. In Proceedings of the 42nd international ACM SIGIR conference on Research and development in Information Retrieval. 165–174.

[205] Xiao Wang, Houye Ji, Chuan Shi, Bai Wang, Yanfang Ye, Peng Cui, and Philip S Yu. 2019. Heterogeneous graph attention network. In The world wide web conference. 2022–2032.

[206] Yong Wang, Mingxing Gao, Xun Ran, Jun Ma, and Leo Yu Zhang. 2023. An improved matrix factorization with local diferential privac based on piecewise mechanism for recommendation systems. Expert Systems with Applications 216 (2023), 119457.

[207] Yuhao Wang, Ziru Liu, Yichao Wang, Xiangyu Zhao, Bo Chen, Huifeng Guo, and Ruiming Tang. 2024. Dif-MSR: A Difusion Model Enhanced Paradigm for Cold-Start Multi-Scenario Recommendation. In Proceedings of the 17th ACM International Conference on Web Search and Data Mining. 779–787.

[208] Yaqing Wang, Hongming Piao, Daxiang Dong, Quanming Yao, and Jingbo Zhou. 2024. Warming Up Cold-Start CTR Prediction by Learning Item-Specific Feature Interactions. In Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining. 3233–3244.

[209] Yuhan Wang, Qing Xie, Mengzi Tang, Lin Li, Jingling Yuan, and Yongjian Liu. 2024. A Dual Perspective Framework of Knowledge correlation for Cross-domain Recommendation. ACM Transactions on Knowledge Discovery from Data 18, 6 (2024), 1–28.

[210] Yu Wang, Yuying Zhao, Neil Shah, and Tyler Derr. 2022. Imbalanced graph classification via graph-of-graph neural networks. In Proceedings of the 31st ACM International Conference on Information & Knowledge Management. 2067–2076.

[211] Lanning Wei, Huan Zhao, Zhiqiang He, and Quanming Yao. 2023. Neural architecture search for GNN-based graph classification. ACM Transactions on Information Systems 42, 1 (2023), 1–29.

[212] Yinwei Wei, Xiang Wang, Qi Li, Liqiang Nie, Yan Li, Xuanping Li, and Tat-Seng Chua. 2021. Contrastive learning for cold-start recommendation. In Proceedings of the 29th ACM International Conference on Multimedia. 5382–5390.

[213] Karl Weiss, Taghi M Khoshgoftaar, and DingDing Wang. 2016. A survey of transfer learning. Journal of Big data 3 (2016), 1–40.

[214] Jingxuan Wen, Huafeng Liu, and Liping Jing. 2023. Modeling Preference as Weighted Distribution over Functions for User Cold-start Recommendation. In Proceedings of the 32nd ACM International Conference on Information and Knowledge Management. 2706–2715.

[215] Dayan Wu, Qi Dai, Jing Liu, Bo Li, and Weiping Wang. 2019. Deep incremental hashing network for eficient image retrieval. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition. 9069–9077.

[216] Junda Wu, Cheng-Chun Chang, Tong Yu, Zhankui He, Jianing Wang, Yupeng Hou, and Julian McAuley. 2024. CoRAL: Collaborative Retrieval-Augmented Large Language Models Improve Long-tail Recommendation. In Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining. 3391–3401.

[217] Jiayang Wu, Wensheng Gan, Zefeng Chen, Shicheng Wan, and S Yu Philip. 2023. Multimodal large language models: A survey. In 2023 IEEE International Conference on Big Data (BigData). IEEE, 2247–2256.

[218] Jiancan Wu, Xiang Wang, Fuli Feng, Xiangnan He, Liang Chen, Jianxun Lian, and Xing Xie. 2021. Self-supervised graph learning for recommendation. In Proceedings of the 44th international ACM SIGIR conference on research and development in information retrieval. 726–735.

[219] Likang Wu, Zhi Zheng, Zhaopeng Qiu, Hao Wang, Hongchao Gu, Tingjia Shen, Chuan Qin, Chen Zhu, Hengshu Zhu, Qi Liu, et al. 2024. A survey on large language models for recommendation. World Wide Web 27, 5 (2024), 60.

[220] Shiwen Wu, Fei Sun, Wentao Zhang, Xu Xie, and Bin Cui. 2022. Graph neural networks in recommender systems: a survey. Comput. Surveys 55, 5 (2022), 1–37.

[221] Shiguang Wu, Yaqing Wang, Qinghe Jing, Daxiang Dong, Dejing Dou, and Quanming Yao. 2023. Coldnas: Search to modulate for user cold-start recommendation. In Proceedings of the ACM Web Conference 2023. 1021–1031.

[222] Tao Wu, Ellie Ka-In Chio, Heng-Tze Cheng, Yu Du, Stefen Rendle, Dima Kuzmin, Ritesh Agarwal, Li Zhang, John Anderson, Sarvjeet Singh, et al. 2020. Zero-shot heterogeneous transfer learning from recommender systems to cold-start search retrieval. In Proceedings of the 29th ACM International Conference on Information & Knowledge Management. 2821–2828.

[223] Wei Wu, Bin Li, Chuan Luo, and Wolfgang Nejdl. 2021. Hashing-accelerated graph neural networks for link prediction. In Proceedings of the Web Conference 2021. 2910–2920.

[224] Xuansheng Wu, Huachi Zhou, Yucheng Shi, Wenlin Yao, Xiao Huang, and Ninghao Liu. 2024. Could Small Language Models Serve as Recommenders? Towards Data-centric Cold-start Recommendation. In Proceedings of the ACM on Web Conference 2024. 3566–3575.

[225] Zonghan Wu, Shirui Pan, Fengwen Chen, Guodong Long, Chengqi Zhang, and S Yu Philip. 2020. A comprehensive survey on graph neural networks. IEEE transactions on neural networks and learning systems 32, 1 (2020), 4–24.

[226] Zhenchao Wu and Xiao Zhou. 2023. M2eu: Meta learning for cold-start recommendation via enhancing user preference estimation. In Proceedings of the 46th International ACM SIGIR Conference on Research and Development in Information Retrieval. 1158–1167.

[227] Ruobing Xie, Zhijie Qiu, Jun Rao, Yi Liu, Bo Zhang, and Leyu Lin. 2020. Internal and Contextual Attention Network for Cold-start Multi-channel Matching in Recommendation.. In IJCAI. 2732–2738.

[228] Xu Xie, Fei Sun, Zhaoyang Liu, Shiwen Wu, Jinyang Gao, Jiandong Zhang, Bolin Ding, and Bin Cui. 2022. Contrastive learning for sequential recommendation. In 2022 IEEE 38th international conference on data engineering (ICDE). IEEE, 1259–1273.

[229] Yu Xie, Yanfeng Liang, Maoguo Gong, A Kai Qin, Yew-Soon Ong, and Tiantian He. 2022. Semisupervised graph neural networks for graph classification. IEEE Transactions on Cybernetics 53, 10 (2022), 6222–6235.

[230] Yuanzhen Xie, Chenyun Yu, Xinzhou Jin, Lei Cheng, Bo Hu, and Zang Li. 2024. Heterogeneous graph contrastive learning for cold start cross-domain recommendation. Knowledge-Based Systems (2024), 112054.

[231] Keyulu Xu, Weihua Hu, Jure Leskovec, and Stefanie Jegelka. 2018. How powerful are graph neural networks? arXiv preprint arXiv:1810.00826 (2018)

[232] Ke Xu, Yuanjie Zhu, Weizhi Zhang, and S Yu Philip. 2023. Graph Neural Ordinary Diferential Equations-based method for Collaborative Filtering. In 2023 IEEE International Conference on Data Mining (ICDM). IEEE, 1445–1450.

[233] Lanling Xu, Junjie Zhang, Bingqian Li, Jinpeng Wang, Mingchen Cai, Wayne Xin Zhao, and Ji-Rong Wen. 2024. Prompting large language models for recommender systems: A comprehensive framework and empirical analysis. arXiv preprint arXiv:2401.04997 (2024).

[234] Xiaolong Xu, Hongsheng Dong, Lianyong Qi, Xuyun Zhang, Haolong Xiang, Xiaoyu Xia, Yanwei Xu, and Wanchun Dou. 2024. Cmclrec: cross-modal contrastive learning for user cold-start sequential recommendation. In Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval. 1589–1598.

[235] Xiaoxiao Xu, Chen Yang, Qian Yu, Zhiwei Fang, Jiaxing Wang, Chaosheng Fan, Yang He, Changping Peng, Zhangang Lin, and Jingping Shao. 2022. Alleviating cold-start problem in CTR prediction with a variational embedding learning framework. In Proceedings of the ACM Web Conference 2022. 27–35.

[236] Yang Xu, Lei Zhu, Zhiyong Cheng, Jingjing Li, and Jiande Sun. 2020. Multi-feature discrete collaborative filtering for fast cold-start recommendation. In Proceedings of the AAAI conference on artificial intelligence, Vol. 34. 270–278.

[237] Yang Xu, Lei Zhu, Zhiyong Cheng, Jingjing Li, Zheng Zhang, and Huaxiang Zhang. 2021. Multi-modal discrete collaborative filtering for eficient cold-start recommendation. IEEE Transactions on Knowledge and Data Engineering 35, 1 (2021), 741–755.

[238] Jieyu Yang, Zhaoxin Huan, Yong He, Ke Ding, Liang Zhang, Xiaolu Zhang, Jun Zhou, and Linjian Mo. 2022. Task Similarity Aware Meta Learning for Cold-Start Recommendation. In Proceedings of the 31st ACM International Conference on Information & Knowledge Management. 4630–4634.

[239] Liangwei Yang, Zhiwei Liu, Yingtong Dou, Jing Ma, and Philip S Yu. 2021. Consisrec: Enhancing gnn for social recommendation via consistent neighbor aggregation. In Proceedings of the 44th international ACM SIGIR conference on Research and development in information retrieval. 2141–2145.

[240] Liu Yang, Ben Tan, Vincent W Zheng, Kai Chen, and Qiang Yang. 2020. Federated recommendation systems. Federated Learning: Privacy and Incentive (2020), 225–239.

[241] Shenghao Yang, Weizhi Ma, Peijie Sun, Min Zhang, Qingyao Ai, Yiqun Liu, and Mingchen Cai. 2024. Common Sense Enhanced Knowledge-based Recommendation with Large Language Model. arXiv preprint arXiv:2403.18325 (2024).

[242] Wooseong Yang, Chen Wang, Zihe Song, Weizhi Zhang, and Philip S Yu. 2024. Item Cluster-aware Prompt Learning for Session-based Recommendation. arXiv preprint arXiv:2410.04756 (2024).

[243] Qiwei Ye, Linbo Qiao, Zhixin Ou, Kaixi Yang, and Fan Yang. 2024. FEW: Multi-modal Recommendation for Cold-Start. In 2024 International Joint Conference on Neural Networks (IJCNN). IEEE, 1–9.

[244] Zixuan Yi, Iadh Ounis, and Craig Macdonald. 2023. Contrastive graph prompt-tuning for cross-domain recommendation. ACM Transactions on Information Systems 42, 2 (2023), 1–28.

[245] Runsheng Yu, Yu Gong, Xu He, Yu Zhu, Qingwen Liu, Wenwu Ou, and Bo An. 2021. Personalized adaptive meta learning for cold-start user preference prediction. In Proceedings of the AAAI conference on artificial intelligence, Vol. 35. 10772–10780.

[246] Hongli Yuan and Alexander A Hernandez. 2023. User Cold Start Problem in Recommendation Systems: A Systematic Review. IEEE Access 11 (2023), 136958–136977.

[247] Jianbo Yuan, Walid Shalaby, Mohammed Korayem, David Lin, Khalifeh AlJadda, and Jiebo Luo. 2016. Solving cold-start problem in large-scale recommendation engines: A deep learning approach. In 2016 IEEE International Conference on Big Data (Big Data). IEEE, 1901–1910.

[248] Seongjun Yun, Seoyoon Kim, Junhyun Lee, Jaewoo Kang, and Hyunwoo J Kim. 2021. Neo-gnns: Neighborhood overlap-aware grap neural networks for link prediction. Advances in Neural Information Processing Systems 34 (2021), 13683–13694.

[249] Tianzi Zang, Yanmin Zhu, Haobing Liu, Ruohan Zhang, and Jiadi Yu. 2022. A survey on cross-domain recommendation: taxonomies, methods, and future directions. ACM Transactions on Information Systems 41, 2 (2022), 1–39.

[250] Tianzi Zang, Yanmin Zhu, Ruohan Zhang, Chunyang Wang, Ke Wang, and Jiadi Yu. 2023. Contrastive Multi-View Interest Learning for Cross-Domain Sequential Recommendation. ACM Transactions on Information Systems 42, 3 (2023), 1–30.

[251] Chuxu Zhang, Dongjin Song, Chao Huang, Ananthram Swami, and Nitesh V Chawla. 2019. Heterogeneous graph neural network. In Proceedings of the 25th ACM SIGKDD international conference on knowledge discovery & data mining. 793–803.

[252] Chao Zhang, Haoxin Zhang, Shiwei Wu, Di Wu, Tong Xu, Yan Gao, Yao Hu, and Enhong Chen. 2024. NoteLLM-2: Multimodal Large Representation Models for Recommendation. arXiv preprint arXiv:2405.16789 (2024).

[253] Haoxing Zhang, Xiaofeng Zhang, Haibo Huang, and Lei Yu. 2022. Prompt-based meta-learning for few-shot text classification. In Proceedings of the 2022 conference on empirical methods in natural language processing. 1342–1357.

[254] Muhan Zhang and Yixin Chen. 2018. Link prediction based on graph neural networks. Advances in neural information processing systems 31 (2018).

[255] Shuai Zhang, Lina Yao, Aixin Sun, and Yi Tay. 2019. Deep learning based recommender system: A survey and new perspectives. ACM computing surveys (CSUR) 52, 1 (2019), 1–38.

[256] Weizhi Zhang, Liangwei Yang, Yuwei Cao, Ke Xu, Yuanjie Zhu, and S Yu Philip. 2023. Dual-Teacher Knowledge Distillation for Strict Cold-Start Recommendation. In 2023 IEEE International Conference on Big Data (BigData). IEEE, 483–492.

[257] Weizhi Zhang, Liangwei Yang, Zihe Song, Henry Peng Zou, Ke Xu, Liancheng Fang, and Philip S Yu. 2024. Do We Really Need Graph Convolution During Training? Light Post-Training Graph-ODE for Eficient Recommendation. In Proceedings of the 33rd ACM International Conference on Information and Knowledge Management. 3248–3258

[258] Weizhi Zhang, Liangwei Yang, Zihe Song, Henry Peng Zou, Ke Xu, Yuanjie Zhu, and Philip S Yu. 2024. Mixed Supervised Graph Contrastive Learning for Recommendation. arXiv preprint arXiv:2404.15954 (2024).

[259] Xiangyu Zhang, Zongqiang Kuang, Zehao Zhang, Fan Huang, and Xianfeng Tan. 2023. Cold & warm Net: addressing cold-start users in recommender systems. In International Conference on Database Systems for Advanced Applications. Springer, 532–543.

[260] Xuxin Zhang, Di Wang, Dehong Gao, Wen Jiang, Wei Ning, Yang Zhou, and Chen Wang. 2022. Revisiting Cold-Start Problem in CTR Prediction: Augmenting Embedding via GAN. In Proceedings of the 31st ACM International Conference on Information & Knowledge Management. 4702–4706.

[261] Yang Zhang, Keqin Bao, Ming Yan, Wenjie Wang, Fuli Feng, and Xiangnan He. 2024. Text-like Encoding of Collaborative Information in Large Language Models for Recommendation. In Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), Lun-Wei Ku, Andre Martins, and Vivek Srikumar (Eds.). Association for Computational Linguistics, Bangkok, Thailand, 9181–9191. https://doi.org/10.18653/v1/2024.acl-long.497

[262] Yijie Zhang, Yuanchen Bei, Hao Chen, Qijie Shen, Zheng Yuan, Huan Gong, Senzhang Wang, Feiran Huang, and Xiao Huang. 2024. Multi-Behavior Collaborative Filtering with Partial Order Graph Convolutional Networks. In Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining. 6257–6268

[263] Yang Zhang, Fuli Feng, Jizhi Zhang, Keqin Bao, Qifan Wang, and Xiangnan He. 2023. Collm: Integrating collaborative embeddings int large language models for recommendation. arXiv preprint arXiv:2310.19488 (2023).

[264] Yan Zhang, Ivor W Tsang, Hongzhi Yin, Guowu Yang, Defu Lian, and Jingjing Li. 2020. Deep pairwise hashing for cold-start recommendation. IEEE Transactions on Knowledge and Data Engineering 34, 7 (2020), 3169–3181.

[265] Cheng Zhao, Chenliang Li, Rong Xiao, Hongbo Deng, and Aixin Sun. 2020. CATN: Cross-domain recommendation for cold-start users via aspect transfer network. In Proceedings of the 43rd international ACM SIGIR conference on research and development in informatio retrieval. 229–238.

[266] Chuang Zhao, Hongke Zhao, Ming He, Jian Zhang, and Jianping Fan. 2023. Cross-domain recommendation via user interest alignment. In Proceedings of the ACM Web Conference 2023. 887–896.

[267] Guoshuai Zhao, Xiaolong Zhang, Hao Tang, Jialie Shen, and Xueming Qian. 2024. Domain-Oriented Knowledge Transfer for Cross-Domain Recommendation. IEEE Transactions on Multimedia (2024).

[268] Penghao Zhao, Hailin Zhang, Qinhan Yu, Zhengren Wang, Yunteng Geng, Fangcheng Fu, Ling Yang, Wentao Zhang, and Bin Cui. 2024. Retrieval-augmented generation for ai-generated content: A survey. arXiv preprint arXiv:2402.19473 (2024).

[269] Wayne Xin Zhao, Yupeng Hou, Xingyu Pan, Chen Yang, Zeyu Zhang, Zihan Lin, Jingsen Zhang, Shuqing Bian, Jiakai Tang, Wenqi Sun, et al. 2022. RecBole 2.0: towards a more up-to-date recommendation library. In Proceedings of the 31st ACM International Conference on Information & Knowledge Management. 4722–4726.

[270] Wayne Xin Zhao, Shanlei Mu, Yupeng Hou, Zihan Lin, Yushuo Chen, Xingyu Pan, Kaiyuan Li, Yujie Lu, Hui Wang, Changxin Tian, et al. 2021. Recbole: Towards a unified, comprehensive and eficient framework for recommendation algorithms. In proceedings of the 30th acm international conference on information & knowledge management. 4653–4664.

[271] Wayne Xin Zhao, Kun Zhou, Junyi Li, Tianyi Tang, Xiaolei Wang, Yupeng Hou, Yingqian Min, Beichen Zhang, Junjie Zhang, Zican Dong, et al. 2023. A survey of large language models. arXiv preprint arXiv:2303.18223 (2023).

[272] Xu Zhao, Yi Ren, Ying Du, Shenzheng Zhang, and Nian Wang. 2022. Improving item cold-start recommendation via model-agnostic conditional variational autoencoder. In Proceedings of the 45th International ACM SIGIR Conference on Research and Development in Information Retrieval. 2595–2600.

[273] Xuhao Zhao, Yanmin Zhu, Chunyang Wang, Mengyuan Jing, Jiadi Yu, and Feilong Tang. 2023. Task-dificulty-aware meta-learning with adaptive update strategies for user cold-start recommendation. In Proceedings of the 32nd ACM International Conference on Information and Knowledge Management. 3484–3493.

[274] Bowen Zheng, Yupeng Hou, Hongyu Lu, Yu Chen, Wayne Xin Zhao, Ming Chen, and Ji-Rong Wen. 2024. Adapting large language models by integrating collaborative semantics for recommendation. In 2024 IEEE 40th International Conference on Data Engineerin (ICDE). IEEE, 1435–1448.

[275] Jiawei Zheng, Qianli Ma, Hao Gu, and Zhenjing Zheng. 2021. Multi-view denoising graph auto-encoders on heterogeneous information networks for cold-start recommendation. In Proceedings of the 27th ACM SIGKDD conference on knowledge discovery & data mining.

2338–2348.

[276] Mingkai Zheng, Fei Wang, Shan You, Chen Qian, Changshui Zhang, Xiaogang Wang, and Chang Xu. 2021. Weakly supervised contrastive learning. In Proceedings of the IEEE/CVF International Conference on Computer Vision. 10042–10051.

[277] Yujia Zheng, Siyi Liu, Zekun Li, and Shu Wu. 2021. Cold-start sequential recommendation via meta learner. In Proceedings of the AAAI Conference on Artificial Intelligence, Vol. 35. 4706–4713.

[278] Fan Zhou, Chengtai Cao, Kunpeng Zhang, Goce Trajcevski, Ting Zhong, and Ji Geng. 2019. Meta-gnn: On few-shot node classification in graph meta-learning. In Proceedings of the 28th ACM International Conference on Information and Knowledge Management. 2357–2360.

[279] Hongyu Zhou, Xin Zhou, Zhiwei Zeng, Lingzi Zhang, and Zhiqi Shen. 2023. A comprehensive survey on multimodal recommender systems: Taxonomy, evaluation, and future directions. arXiv preprint arXiv:2302.04473 (2023).

[280] Zhihui Zhou, Lilin Zhang, and Ning Yang. 2023. Contrastive collaborative filtering for cold-start item recommendation. In Proceedings of the ACM Web Conference 2023. 928–937.

[281] Jieming Zhu, Quanyu Dai, Liangcai Su, Rong Ma, Jinyang Liu, Guohao Cai, Xi Xiao, and Rui Zhang. 2022. Bars: Towards ope benchmarking for recommender systems. In Proceedings of the 45th International ACM SIGIR Conference on Research and Development in Information Retrieval. 2912–2923.

[282] Lei Zhu, Chaoqun Zheng, Weili Guan, Jingjing Li, Yang Yang, and Heng Tao Shen. 2023. Multi-modal hashing for eficient multimedia retrieval: A survey. IEEE Transactions on Knowledge and Data Engineering 36, 1 (2023), 239–260.

[283] Yongchun Zhu, Kaikai Ge, Fuzhen Zhuang, Ruobing Xie, Dongbo Xi, Xu Zhang, Leyu Lin, and Qing He. 2021. Transfer-meta framework for cross-domain recommendation to cold-start users. In Proceedings of the 44th international ACM SIGIR conference on research and development in information retrieval. 1813–1817.

[284] Yongchun Zhu, Zhenwei Tang, Yudan Liu, Fuzhen Zhuang, Ruobing Xie, Xu Zhang, Leyu Lin, and Qing He. 2022. Personalized transfer of user preferences for cross-domain recommendation. In Proceedings of the fifteenth ACM international conference on web search and data mining. 1507–1515.

[285] Yaochen Zhu, Liang Wu, Qi Guo, Liangjie Hong, and Jundong Li. 2024. Collaborative large language model for recommender systems. In Proceedings of the ACM on Web Conference 2024. 3162–3172.

[286] Yongchun Zhu, Ruobing Xie, Fuzhen Zhuang, Kaikai Ge, Ying Sun, Xu Zhang, Leyu Lin, and Juan Cao. 2021. Learning to warm up cold item embeddings for cold-start recommendation with meta scaling and shifting networks. In Proceedings of the 44th International ACM SIGIR Conference on Research and Development in Information Retrieval. 1167–1176.

[287] Yutao Zhu, Huaying Yuan, Shuting Wang, Jiongnan Liu, Wenhan Liu, Chenlong Deng, Haonan Chen, Zhicheng Dou, and Ji-Rong Wen. 2023. Large language models for information retrieval: A survey. arXiv preprint arXiv:2308.07107 (2023).

[288] Ziwei Zhu, Jingu Kim, Trung Nguyen, Aish Fenton, and James Caverlee. 2021. Fairness among new items in cold start recommender systems. In Proceedings of the 44th international ACM SIGIR conference on research and development in information retrieval. 767–776.

[289] Ziwei Zhu, Shahin Sefati, Parsa Saadatpanah, and James Caverlee. 2020. Recommendation for new users and new items via randomized training and mixture-of-experts transformation. In Proceedings of the 43rd International ACM SIGIR Conference on Research and Development in Information Retrieval. 1121–1130.

[290] Fuzhen Zhuang, Zhiyuan Qi, Keyu Duan, Dongbo Xi, Yongchun Zhu, Hengshu Zhu, Hui Xiong, and Qing He. 2020. A comprehensiv survey on transfer learning. Proc. IEEE 109, 1 (2020), 43–76.

[291] Henry Zou, Vinay Samuel, Yue Zhou, Weizhi Zhang, Liancheng Fang, Zihe Song, Philip Yu, and Cornelia Caragea. 2024. ImplicitAVE: An Open-Source Dataset and Multimodal LLMs Benchmark for Implicit Attribute Value Extraction. In Findings of the Association for Computational Linguistics: ACL 2024, Lun-Wei Ku, Andre Martins, and Vivek Srikumar (Eds.). Association for Computational Linguistics, Bangkok, Thailand, 338–354. https://doi.org/10.18653/v1/2024.findings-acl.20

[292] Jie Zou, Yifan Chen, and Evangelos Kanoulas. 2020. Towards question-based recommender systems. In Proceedings of the 43rd international ACM SIGIR conference on research and development in information retrieval. 881–890.

## Probability of Transition to Turbulence in a Reduced Stochastic Model of Pipe Flow

# Probability of Transition to Turbulence in a Reduced Stochastic Model of Pipe Flow

P. Bernuzzi<sup>1,†</sup> and C. Kuehn<sup>1,2</sup>

<sup>1</sup>Technical University of Munich, School of Computation Information and Technology, Department of Mathematics, Boltzmannstraße 3, 85748 Garching, Germany

<sup>2</sup>Technical University of Munich, Munich Data Science Institute, Walther-von-Dyck-Straße 10, 85748 Garching, Germany <sup>†</sup>Author to whom any correspondence should be addressed.

Email addresses: paolo.bernuzzi@ma.tum.de (P. Bernuzzi), ckuehn@ma.tum.de (C. Kuehn).

March 4, 2025

## Abstract

We study the phenomenon of turbulence initiation in pipe flow under diferent noise structures by estimating the probability of initiating metastable transitions. We establish lower bounds on turbulence transition probabilities using linearized models with multiplicative noise near the laminar state. First, we consider the case of stochastic perturbations by Itô white noise; then, through the Stratonovich interpretation, we extend the analysis to noise types such as white and red noise in time. Our findings demonstrate the viability of detecting the onset of turbulence as rare events under diverse noise assumptions. The results also contribute to applied SPDE theory and ofer valuable methodologies for understanding turbulence across application areas.

Keywords: SPDEs, transition to turbulence, plane Couette flow, red noise, metastability.

Funding: This work was supported by the European Union’s Horizon 2020 research and innovation programme under Grant Agreement 956170.

## 1 Introduction

The flow of a fluid is known to display diferent behaviour depending on the assumptions on the fluid and the shape of the geometry traversed. We focus on plane Couette flow, or flow along a pipe, and the transition to turbulence starting from an initially laminar state [18]. Recently, this area has been connected to directed percolation, a classical area of probability theory. It is known that the transition to turbulence crucially depends upon the Reynolds number, i.e., on the ratio between inertial and viscous forces in a fluid. From a mathematical perspective, studying the transition to turbulence directly in the Euler or Navier-Stokes equations turns out to be extremely dificult. Yet, quite recently, other simplified models have been proposed and directly validated against experiments.

The first model proposed in [1, 2] is defined by two coupled stochastic partial diferential equations (SPDEs) with second-order dissipation, an advection term, and multiplicative degenerate Itô noise [25]. The solution of this system may display structures labeled as slugs for high Reynolds numbers, and the turbulent state covers the whole pipe in finite time with a high probability. Conversely, for low values of the corresponding parameter, the turbulent regions are absorbed in the laminar state in finite time with high probability. Lastly, traveling structures labeled as pufs indicate a fluctuating transition for intermediate values. In such cases, metastable transitions between turbulent and laminar states are observed in the pipe. The study of the rise and the splitting of pufs is relevant to describe the transition to turbulence as a rare event [14]. The steps involved in such an occurrence can be described through the computation of instantons, most likely paths to display rare occurrences [5, 19, 32].

The complex structure provided by the model discussed above is not observed for all fluids and is in contrast with the perspective of [26, 27]. In this case, the turbulent state is seen as a fluctuating state able to decay spontaneously. Conversely, the laminar state is an absorbing state, which is unable to induce turbulence into the system. The alternative model proposed in [13] is a one-dimensional SPDE that does not display advection. Furthermore, this simplified model does not show well-defined traveling states such as pufs and slugs. For this reason, the flow is labeled band-free. In particular, the transition to turbulence is primarily driven by noise and occurs more rarely than in the previously discussed cases. The transition mechanism can be studied numerically through the adjoint state method [5], which captures the instanton for various types of noise. Alternatively, the Trajectory-Adaptive Multilevel Sampling algorithm (TAMS) [19, 32] computes diferent trajectories that display such an event. Along with the description of such an occurrence, the analytic estimation of the probability of jumps provides a valuable tool to predict the likelihood of this phenomenon.

The metastable jump to turbulence is rare under the assumption of initial conditions close to the laminar state. Under such conditions, we label this transition as turbulence initiation, or turbulence onset, to indicate that it is primarily induced by noise. Therefore, the linearization of the model near such a steady state is a natural simplification. The linearized system resembles the cable equation [31], or a heat equation with a second linear dissipative term, with multiplicative noise. The literature regarding such a model is vast. These types of SPDEs have been studied in a theoretical context to understand the influence of noise on potential finite-time blow-up of the solution. In particular, for standard white noise multiplied by a multiplicative term of order $\gamma > \frac { 3 } { 2 }$ the mild solution is proven to diverge to infinity in finite time [23, 24]. Conversely, for a multiplicative term of order $\begin{array} { r } { 0 \leq \dot { \gamma } \leq \frac { 3 } { 2 } } \end{array}$ the mild solution of the linear system does not explode in finite time [22, 28]. Although the band-free plane Couette flow model considers noise of order $\gamma = 1$ , we show in this paper that analytic techniques employed in the proof of blow-up of the mild solution, in [23], can be applied to our case of interest to describe turbulence initiation under Itô white Gaussian noise.

In [2], diferent types of noise are admitted to perturb the system, although only Itô noise is addressed to simplify numerical simulations. In this work, we study the onset of turbulence for various Gaussian noise terms. For instance, Stratonovich noise is a natural alternative to Itô noise in physical applications and fluid dynamics, particularly due to the chain rule property [11, 16]. The computation of higher bounds for the probability of metastable transitions has already been achieved for cable equations under the assumption of additive Itô noise [4, 6]. Under such assumptions, the solution to the problem displays a qualitatively diferent behaviour from the multiplicative noise case: first, its sign can change in contrast to the cable equation with multiplicative noise; furthermore, the laminar state is not an absorbing state, which is a fundamental property of the original system. Nevertheless, the Cole-Hopf transformation reveals structural parallels between the systems. In fact, the study of the strong solution of the original system under Stratonovich noise on a logarithmic scale, in the form of the KPZ equation, displays an additive noise term [3, 8, 15]. Standard techniques enable the construction of a lower bound to the probability of transition to turbulence in specific domain regions. This method is then extended to the case of red noise in order to introduce memory in the noise component. We discuss two diferent interpretations of red (Stratonovich) noise, which are known to find applications in climate science [21, 17].

In conclusion, our methods prove the possibility of transition to turbulent states under diferent types of noise assumptions in simplified fluid dynamics models that have been suggested in applications. These results are implied by the stochastic perturbations in the system despite the non-trivial nature of the noise involved. Furthermore, they advance the analytic study of SPDEs, particularly with (multiplicative) Stratonovich noise.

The paper is structured as follows. In Section 2, we introduce our main mathematical tools. Moreover, we justify the linearization of the system as a method to study the solutions in the proximity to the laminar state and to obtain a lower bound to the probability of the transition to turbulence. We construct the fundamental solution of the cable equation and discuss its properties. In Section 3, we consider perturbations enforced by Itô noise. We study the mild solution of the linearized model on the laminar state. By applying a suitable operator to counter the efect of the drift component, we obtain an observable in the form of a martingale. Through the use of similar techniques employed as in [23], we obtain the bound to the transition to turbulence. In Section 4, we consider the noise term in the Stratonovich interpretation. We assume first space-time white noise and then red noise in time. A lower bound to the local and global transition to turbulence is proven by studying its strong solution on a logarithmic scale through the Cole-Hopf transformation [15]. The methods are also shown to be extendable to the case of space heterogeneity in the system [6]. In Section 5, we compare the stated methods and discuss the diferences with already existing approaches.

## 2 Preliminaries and linearization

We introduce the spatial interval [0, L] for $L > 0 ,$ to be interpreted as the width of a pipe. For $x \in [ 0 , L ]$ and $t > 0$ , we define a variable $q = q ( x , t )$ modelling the turbulence level of a fluid along the plane Couette flow as discussed in [2, 13]. We study a family of stochastic partial diferential equations (SPDEs) used as simplified transition-to-turbulence models, for which we provide a mathematical and physical interpretation below. The SPDEs are given by

$$
\left\{ \begin{array}{l} \mathrm{d} q (x, t) = \big (\partial_ {x x} ^ {2} q (x, t) - q (x, t) + (r + 1) q (x, t) ^ {2} \left(2 - q (x, t)\right) + \sigma_ {\mathrm{R}} q (x, t) \circ F (\xi) (x, t) \big)   \mathrm{d} t \\ \qquad + \sigma_ {\mathrm{I}} q (x, t) Q ^ {\frac {1}{2}} \mathrm{d} W _ {t} + \sigma_ {\mathrm{S}} q (x, t) \circ Q ^ {\frac {1}{2}} \mathrm{d} W _ {t}, \\ \partial_ {x} q (0, t) = \partial_ {x} q (L, t) = 0, \\ q (x, 0) = q _ {0} (x). \end{array} \right.\tag{2.1}
$$

We interpret $r > 0$ as a value related to the Reynolds number, which defines the behaviour of the solution. The family of models (2.1) includes noises of diferent forms to consider diferent interpretations of the small stochastic forcing. Therefore, the following parameters are to be interpreted as intensities of the noise term and are justified by models describing turbulence: $\sigma _ { \mathrm { { I } } } \geq 0$ as the intensity of white noise interpreted in the Itô sense $[ 1 3 ] ; \sigma _ { \mathrm { S } } \geq 0$ as the intensity of white noise interpreted in the Stratonovich perspective [11], labeled with $\circ ; \ \sigma _ { \mathrm { R } } \ \geq \ 0$ as a correlation intensity which can induce perturbations in the system [17, 21] in Stratonovich sense. The Itô and Stratonovich assumptions are mathematically equivalent, as they can be converted by including the Itô-Stratonovich correction term [12, 30]. As such, we always assume $\sigma _ { \mathrm { I } } \sigma _ { \mathrm { S } } = 0$ . Then, under the assumption of red noise, we introduce the adapted Ornstein-Uhlenbeck process $\xi = \xi ( x , t )$ in $L ^ { 2 } ( [ 0 , L ] )$ and assume $\sigma _ { \mathrm { R } } > 0$ . The operator $F$ is interpreted as a diferential operator that maps the Ornstein-Uhlenbeck process to $L ^ { 2 } ( [ 0 , L ] )$ . Examples are provided in Subsection 4.2. Conversely, the noise is interpreted in Section 3 as Itô white noise in time, i.e., $\sigma _ { \mathrm { { I } } } > \sigma _ { \mathrm { { S } } } = \sigma _ { \mathrm { { R } } } = 0$ , and in Subsection 4.1 as Stratonovich white noise in time, i.e., $\sigma _ { \mathrm { S } } > \sigma _ { \mathrm { I } } = \sigma _ { \mathrm { R } } = 0$ . The systems discussed in the paper are converted to the Itô noise form in Appendix A. We introduce the cylindrical Wiener process $W ,$ as defined in [10, Chapter $^ { 4 ] , }$ i.e.,

$$
W _ {t} := W (x, t) = \sum_ {i = 0} ^ {\infty} b _ {i} (x) \beta_ {i} (t),\tag{2.2}
$$

for $\{ \beta _ { i } \} _ { i \in \mathbb { N } } \mathfrak { t }$ a family of independent normalized scalar Wiener processes in time, with filtration $\mathcal { F } _ { t } ^ { W }$ , and $\left\{ b _ { i } \right\} _ { i \in \mathbb { N } }$ a basis of $L ^ { 2 } ( [ 0 , L ] )$ The noise $Q ^ { \frac { 1 } { 2 } } W ,$ , considered as minor fluctuations in the fluid, is then assumed to be a Q-Wiener process. The operator $Q$ is self-adjoint and non-negative. We define its eigenvalues as $\left\{ \zeta _ { i } \right\} _ { i \in \mathbb { N } }$ with corresponding eigenbasis $\left\{ b _ { i } \right\} _ { i \in \mathbb { N } }$ of $L ^ { 2 } ( [ 0 , L ] )$ , described further below in each section. The operator also assumes at least one of the following properties: it is trace-class, or it is bounded with eigenfunctions that converge to the eigenfunctions of the Laplacian in $L ^ { \infty } ( [ 0 , L ] ,$ )-norm with rate suficient to imply the existence of the solution [6]. The boundary conditions are specified as homogeneous Neumann, although our methods also extend to periodic boundary conditions. Lastly, the initial condition $q _ { 0 }$ is assumed to be non-negative on [0, L] and a positive function almost everywhere on the interval. Therefore, we consider q to be non-negative for any $t > 0$ and to not be initiated in the laminar state. Under these assumptions, the solution of (2.1) is proven [10, Chapter 7] to be in the Hilbert space $L ^ { 2 } ( [ 0 , L ] )$ almost surely for $t > 0$ . The scalar product of $L ^ { 2 } ( [ 0 , L ] )$ is defined as $\langle \cdot , \cdot \rangle$ and the corresponding norm as ||·||. The norms in the other $L ^ { p } ( [ 0 , L ] )$ spaces are indicated as $| | { \cdot } | | _ { p } .$ . The scalar product in any other Hilbert space $\mathcal { X }$ is labeled as $\langle \cdot , \cdot \rangle _ { \mathscr { X } }$

The deterministic system, i.e., $\sigma _ { \mathrm { { I } } } = \sigma _ { \mathrm { { S } } } = \sigma _ { \mathrm { { R } } } = 0$ , displays three steady states: $q _ { 1 } \equiv 0 , q _ { 2 } \equiv q _ { - }$ <sub>−</sub> and $q _ { 3 } \equiv q _ { + }$ , for

$$
q _ {\pm} = 1 \pm \sqrt {\frac {r}{r + 1}} \in [ 0, 2 ].
$$

The deterministically stable states $q _ { 1 }$ and $q _ { 3 }$ are identified as the laminar and the turbulent state, respectively. The state q is a saddle for the deterministic model. Lastly, we define $\tau _ { J }$ as the first time $t \geq 0 ,$ , such that $| | q ( \cdot , t ) | | _ { \infty } > J .$ . In Figure 1, we observe two examples of turbulence onset under Itô white noise and Stratonovich white noise assumptions, respectively. In each case, the initial state lies below the saddle, $0 < q _ { 0 } < q _ { 2 }$ , and $\tau _ { q _ { 3 } } < T = 1 0$ . The initiation of turbulence is attributed to the growth of an $L ^ { p } ( [ 0 , L ] ) { \mathrm { - n o r m } }$ . The paths are obtained through the TAMS algorithm.

In order to observe the behaviour of $q$ in the proximity of the laminar state, we study the mild solution $u _ { \alpha } = u _ { \alpha } ( x , t )$ of the linear system with corresponding noise,

$$
\left\{ \begin{array}{l} \mathrm{d} u _ {\alpha} (x, t) = \left(\partial_ {x x} ^ {2} u _ {\alpha} (x, t) - \alpha u _ {\alpha} (x, t) + \sigma_ {\mathrm{R}} u _ {\alpha} (x, t) \circ F (\xi) (x, t)\right) \mathrm{d} t \\ \qquad + \sigma_ {\mathrm{I}} u _ {\alpha} (x, t) Q ^ {\frac {1}{2}} \mathrm{d} W _ {t} + \sigma_ {\mathrm{S}} u _ {\alpha} (x, t) \circ Q ^ {\frac {1}{2}} \mathrm{d} W _ {t}, \\ \partial_ {x} u _ {\alpha} (0, t) = \partial_ {x} u _ {\alpha} (L, t) = 0, \\ u _ {\alpha} (x, 0) = q _ {0} (x), \end{array} \right.\tag{2.3}
$$

for $\alpha = 1$ . We refer to the solution of the system following the noise assumptions, i.e., the values of $\sigma _ { \mathrm { { I } } } , \sigma _ { \mathrm { { S } } } , \sigma _ { \mathrm { { R } } } \colon$ we denote by $u _ { \alpha } ^ { \mathrm { I } } = u _ { \alpha } ^ { \mathrm { I } } ( x , t )$ the mild solution of (2.3) under Itô white noise; $u _ { \alpha } ^ { \mathrm { S } } = u _ { \alpha } ^ { \mathrm { S } } ( x , t )$ is the strong solution under Stratonovich white noise; $u _ { \alpha } ^ { \mathrm { R } } = u _ { \alpha } ^ { \mathrm { R } } ( x , t )$ refers to the strong solution under Stratonovich red noise. We focus on the case for which $q \ \leq \ 2 ,$ , as $0 \equiv q _ { 1 } < q _ { 2 } < q _ { 3 } < 2$ . We define $v _ { J } ^ { \mathrm { S } }$ as the first time $t \geq 0$ , such that $\| u _ { \alpha } ^ { \mathrm { S } } ( \cdot , t ) \| _ { \infty } > J .$ Equivalently, $v _ { J } ^ { \mathrm { I } }$ is the first time $t ,$ such that $| | u _ { \alpha } ^ { \mathrm { I } } ( \cdot , t ) | | _ { \infty } > J$ . Therefore, we can prove the lemma to follow.

Lemma 2.1. We consider q, the mild solution of (2.1), and u<sub>1</sub>, the mild solution of (2.3) for $\alpha = 1 , x \in [ 0 , L ]$ and $t \in [ 0 , T ]$ Moreover, we assume that $q ( x , t ) \leq 2$ for any $x \in [ 0 , L ]$ and $t \in [ 0 , T ]$ . Then, the conclusions are:

(a) the inequality $\boldsymbol { l } ( \boldsymbol { x } , t ) \ge u _ { 1 } ( \boldsymbol { x } , t )$ holds under the same sample W and for almost every $x \in [ 0 , L ]$ and $t \in [ 0 , T ]$ ;

(b) for $J \le 2$ and $\sigma _ { S } > \sigma _ { I } = 0$ , the inequality $\tau { \boldsymbol { J } } \leq v _ { \boldsymbol { J } } ^ { S }$ holds;

(c) for $J \le 2$ and $\sigma _ { I } > \sigma _ { S } = 0$ , the inequality $\tau _ { J } \leq v _ { J } ^ { I }$ holds.

![](images/26688a804a470f2fce823c42900d56a54dbe1c90327089a845dc4a48701f3697.jpg)  
(a) Trajectory q solving (2.1) with Itô white noise and describing turbulence onset with respect to the $L ^ { 1 } ( [ 0 , L ] ) { \mathrm { - n o r m } } .$

![](images/34289ac2e6e5907971ec0f3c2d5952213a944d17a36dc10d014b78a5786b69bb.jpg)  
(b) Trajectory q solving (2.1) with Itô white noise and describing turbulence onset with respect to the $L ^ { \infty } ( [ 0 , L ] ) \mathrm { - n o r m } .$

![](images/92847d8aa174ff95d91fa957ed68457e7cedd67f6dd0b2e4d6f8ae78a74ec17c.jpg)  
(c) Trajectory q solving (2.1) with Stratonovich white noise and describing turbulence onset with respect to the $L ^ { 1 } ( [ 0 , L ] ) { \mathrm { - n o r m } } .$

![](images/6c27bba731c0afa05070b17501be9522f87b0be492073ea2dd4793483f75dd2b.jpg)  
(d) Trajectory q solving (2.1) with Stratonovich white noise and describing turbulence onset with respect to the $L ^ { \infty } ( [ 0 , L ] ) – \mathrm { n o r m }$  
Fig. 1 (a) and (b) show trajectories of q, solution of (2.1), indicating the onset of turbulence under Itô noise, $0 . 5 = \sigma _ { \mathrm { I } } > \sigma _ { \mathrm { S } } = \sigma _ { \mathrm { R } } = 0$ ; whereas in (c) and (d) it is associated with Stratonovich noise, $0 . 5 = \sigma _ { \mathrm { S } } > \sigma _ { \mathrm { R } } = \sigma _ { \mathrm { R } } = 0$ . The interpretation of turbulence initiation is associated with an $L ^ { p } ( [ 0 , L ] )$ )-norm described below.

We consider $\{ e _ { i } \} _ { i \in \mathbb { N } }$ the normalized eigenfunctions of the Laplace operator on [0, L] under Neumann boundary conditions. We assume the noise perturbation on the solution along 101 modes, $b _ { i } = e _ { i }$ for $i \in \{ 0 , \ldots , 1 0 0 \}$ , with intensity $\zeta _ { i } = \exp \left( - ( i - 1 ) ^ { 2 } \right)$ . The initial solution is set at $q _ { 0 } \equiv 0 . 5$ The Reynolds parameter is $r = { \frac { 1 } { 1 5 } }$ , which implies that $q _ { - } ~ = ~ 0 . 7 5$ and $q _ { + } = 1 . 2 5$ We set $L = T = 1 0$ and space and time step as 0.1 and $_ { 0 . 0 1 }$ respectively. In (a) and (c) we observe the rise of ||q||<sub>1</sub> to the value $q _ { + } L ,$ , while in (b) and (d) we capture the rise of $| | q | | _ { \infty }$ to the value q<sub>+</sub>. These rare events are computed via the TAMS algorithm, for which we run 50 simulations each and use the respective norm as a score function. The simulations are achieved through the discretized mild solution formula [10]. As described in Appendix A, the systems difer in view of the Itô-Stratonovich correction term, which implies an additional heterogeneous positive drift term in the case of Stratonovich white noise.

Proof. We study $\tilde { u } = q - u _ { 1 }$ under the assumptions $\sigma _ { \mathrm { I } } \geq 0 , \sigma _ { \mathrm { S } } \geq 0$ and $\sigma _ { \mathrm { R } } \geq 0$ . The diference u˜ is the mild solution of

$$
\left\{ \begin{array}{l} \mathrm{d} \tilde {u} (x, t) = \big (\partial_ {x x} ^ {2} \tilde {u} (x, t) - \tilde {u} (x, t) + (r + 1) q (x, t) ^ {2} \left(2 - q (x, t)\right) + \sigma_ {\mathrm{R}} \tilde {u} (x, t) \circ F (\xi) (x, t) \big)   \mathrm{d} t \\ \qquad + \sigma_ {\mathrm{I}} \tilde {u} (x, t) Q ^ {\frac {1}{2}} \mathrm{d} W _ {t} + \sigma_ {\mathrm{S}} \tilde {u} (x, t) \circ Q ^ {\frac {1}{2}} \mathrm{d} W _ {t}, \\ \partial_ {x} \tilde {u} (0, t) = \partial_ {x} \tilde {u} (L, t) = 0, \\ \tilde {u} (x, 0) \equiv 0. \end{array} \right.
$$

Therefore, it solves,

$$
\begin{array}{r l} & {\tilde {u} (x, t) = (r + 1) \int_ {0} ^ {t} \mathrm{e} ^ {(t - s) (\partial_ {x x} ^ {2} - 1)} (q (x, s) ^ {2} (2 - q (x, s))) \mathrm{d} s + \sigma_ {\mathrm{R}} \int_ {0} ^ {t} \mathrm{e} ^ {(t - s) (\partial_ {x x} ^ {2} - 1)} \tilde {u} (x, s) \circ F (\xi) (x, s) \mathrm{d} s} \\ & {\quad + \sigma_ {\mathrm{I}} \int_ {0} ^ {t} \mathrm{e} ^ {(t - s) (\partial_ {x x} ^ {2} - 1)} \tilde {u} (x, s) Q ^ {\frac {1}{2}} \mathrm{d} W _ {s} + \sigma_ {\mathrm{S}} \int_ {0} ^ {t} \mathrm{e} ^ {(t - s) (\partial_ {x x} ^ {2} - 1)} \tilde {u} (x, s) \circ Q ^ {\frac {1}{2}} \mathrm{d} W _ {s}.} \end{array}\tag{2.4}
$$

Due to the Neumann boundary conditions, the continuous semigroup $\underset { \underset { \ r { c } } { \ r { \ r } } } { \big ( } t - s \big ) \Big ( \partial _ { x x } ^ { 2 } - 1 \Big )$ does not afect the sign of the argument function.

Since the first term in the right-hand side of (2.4) is positive and by the fact that the other terms are multiplicative in u˜, it follows that $q ( x , t ) \geq u _ { 1 } ^ { \mathrm { S } } ( x , t )$ for any $x \in [ 0 , L ]$ and $t \in [ 0 , T ]$

We set $\sigma _ { \mathrm { S } } > \sigma _ { \mathrm { I } } = 0 . \mathrm { ~ I f ~ } v _ { J } ^ { \mathrm { S } } \leq \tau _ { 2 }$ , then we obtain $\tau  \} \leq v _ { J } ^ { \mathrm { S } }$ . Conversely, for $\tau _ { 2 } \leq v _ { J } ^ { \mathrm { S } }$ , it follows that $\tau  \} \leq v _ { J } ^ { \mathrm { S } }$ , since $\tau J \leq \tau _ { 2 }$ . The Itô noise perspective, i.e., case $( c )$ , can be proven through equivalent reasoning. □

The linearization enables the construction of the following results and further justifies the study of the fundamental solution of the cable equation. We shall denote the fundamendal solution by $G _ { \alpha }$ and it solves the system

$$
\left\{ \begin{array}{l} \mathrm{d} G _ {\alpha} (x, y, t, [ 0, L ]) = \left(\partial_ {x x} ^ {2} - \alpha\right) G _ {\alpha} (x, y, t, [ 0, L ]) \mathrm{d} t, \\ \partial_ {x} G _ {\alpha} (0, y, t, [ 0, L ]) = \partial_ {x} G _ {\alpha} (L, y, t, [ 0, L ]) = 0, \\ G _ {\alpha} (x, y, 0, [ 0, L ]) = \delta_ {0} (y - x), \end{array} \right.\tag{2.5}
$$

where $\delta _ { 0 }$ is the Dirac delta. The solution $G _ { \alpha }$ can be obtained through diferent methods [31]. For the purposes of this paper, we consider solely the form

$$
G _ {\alpha} (x, y, t, [ 0, L ]) = \mathrm{e} ^ {- t \alpha} \left(\sum_ {n = 0} ^ {\infty} e _ {n} (x) e _ {n} (y) \mathrm{e} ^ {- t \lambda_ {n}}\right),
$$

for $\{ e _ { i } \} _ { i \in \mathbb { N } }$ the eigenbasis of the Laplacian operator in $L ^ { 2 } ( [ 0 , L ] )$ and for $\{ - \lambda _ { i } \} _ { i \in \mathbb { N } }$ the corresponding eigenfunctions. Under Neumann boundary conditions, they are defined as

$$
\begin{array}{c} e _ {0} \equiv \frac {1}{\sqrt {L}}, \\ e _ {n} (x) = \sqrt {\frac {2}{L}} \cos \left(\frac {n \pi x}{L}\right), \text {   for   any   } n \in \mathbb {N} _ {> 0}, \\ \lambda_ {n} = \left(\frac {n \pi}{L}\right) ^ {2}, \qquad \text {   for   any   } n \in \mathbb {N}, \end{array}
$$

for $x \in [ 0 , L ]$ . Finally, it is easy to observe that the fundamental solution satisfies

$$
\int_ {0} ^ {L} G _ {\alpha} (x, y, t, [ 0, L ]) G _ {\alpha} (y, z, s, [ 0, L ]) \mathrm{d} y = G _ {\alpha} (x, z, t + s, [ 0, L ]),\tag{2.6}
$$

for $t > 0 , s > 0$ and $z \in [ 0 , L ]$

## 3 Itô noise: Countering the drift component

In this section, we study white noise in Itô sense, interpreted as the assumption $\sigma _ { \mathrm { { I } } } > \sigma _ { \mathrm { { S } } } = \sigma _ { \mathrm { { R } } } = 0$ in (2.1) and in (2.3). We assume $b _ { 0 } = e _ { 0 }$ and that $\zeta _ { 0 } > 0 ,$ . We consider $u _ { \alpha } ^ { \mathrm { I } } = u _ { \alpha } ^ { \mathrm { I } } ( x , t )$ , the mild solution of (2.3) for $\alpha > 0$ as

$$
u _ {\alpha} ^ {\mathrm{I}} (x, t) = \int_ {0} ^ {L} G _ {\alpha} (x, y, t, [ 0, L ]) q _ {0} (y) \mathrm{d} y + \sigma_ {\mathrm{I}} \int_ {0} ^ {L} \int_ {0} ^ {t} G _ {\alpha} (x, y, t - s, [ 0, L ]) u _ {\alpha} ^ {\mathrm{I}} (y, s) Q ^ {\frac {1}{2}} \mathrm{d} W _ {s} \mathrm{d} y.\tag{3.1}
$$

For the fixed time $T > 0$ and any $y \in [ 0 , L ]$ , we define

$$
\phi_ {\alpha} (x, y, t, [ 0, L ]) := G _ {\alpha} (x, y, T - t, [ 0, L ]),
$$

where $x \in [ 0 , L ]$ and $t \in [ 0 , T ]$ . By construction of (2.5), we have that $\phi _ { \alpha }$ solves

$$
\left\{ \begin{array}{l} \mathrm{d} \phi_ {\alpha} (x, y, t, [ 0, L ]) = \left(- \partial_ {x x} ^ {2} + \alpha\right) \phi_ {\alpha} (x, y, t, [ 0, L ]) \mathrm{d} t, \\ \partial_ {x} \phi_ {\alpha} (0, y, t, [ 0, L ]) = \partial_ {x} \phi_ {\alpha} (L, y, t, [ 0, L ]) = 0, \\ \phi_ {\alpha} (x, y, T, [ 0, L ]) = \delta_ {0} (y - x), \end{array} \right.
$$

for $x \in [ 0 , L ]$ and $t \in [ 0 , T )$ . In the following lemma, we use $\phi _ { \alpha }$ to define an observable, which we prove to be a martingale.

Lemma 3.1. For any $x \in [ 0 , L ]$ and $t \in [ 0 , T ]$ , the process M defined as

$$
M (t) = \int_ {0} ^ {L} \int_ {0} ^ {L} \phi_ {\alpha} (x, y, t, [ 0, L ]) u _ {\alpha} ^ {I} (y, t) d y d x = \mathrm{e} ^ {- (T - t) \alpha} | | u _ {\alpha} ^ {I} (\cdot , t) | | _ {1},\tag{3.2}
$$

with $u _ { \alpha } ^ { I }$ denoting the mild solution of (2.3), is a non-negative $\mathcal { F } _ { t } ^ { W }$ -martingale. Its quadratic variation, ⟨M ⟩, satisfies

$$
\langle M \rangle (t) \geq \zeta_ {0} \frac {\sigma_ {I} ^ {2}}{L ^ {2}} \int_ {0} ^ {t} M (s) ^ {2} d s,\tag{3.3}
$$

for any $t \in [ 0 , T ]$

Proof. In the first part of the proof, we follow a similar approach to [24, Lemma 2.3] to prove that M is a $\mathcal { F } _ { t } ^ { W }$ -martingale. From its construction in (3.2), we consider the mild solution form of $u _ { \alpha } ^ { \mathrm { I } }$ in (3.1). Then, we employ property (2.6) to obtain

$$
M (t) = \int_ {0} ^ {L} \int_ {0} ^ {L} \phi_ {\alpha} (x, y, 0, [ 0, L ]) q _ {0} (y) \mathrm{d} y \mathrm{d} x + \sigma_ {\mathrm{I}} \int_ {0} ^ {L} \int_ {0} ^ {L} \int_ {0} ^ {t} \phi_ {\alpha} (x, y, s, [ 0, L ]) u _ {\alpha} ^ {\mathrm{I}} (y, s) Q ^ {\frac {1}{2}} \mathrm{d} W _ {s} \mathrm{d} y \mathrm{d} x.\tag{3.4}
$$

The observable M is an $\mathcal { F } _ { t } ^ { W }$ -martingale since it is the sum of a constant and an $\mathcal { F } _ { t } ^ { W }$ -martingale, which is a stochastic integral with integrand independent of t. Its quadratic variation is

$$
\langle M \rangle (t) = \sigma_ {\mathrm{I}} ^ {2} \int_ {0} ^ {L} \int_ {0} ^ {L} \int_ {0} ^ {t} \left(Q ^ {\frac {1}{2}} \left(\phi_ {\alpha} (x, y, s, [ 0, L ]) u _ {\alpha} ^ {\mathrm{I}} (y, s)\right)\right) ^ {2} \mathrm{d} s \mathrm{d} y \mathrm{d} x.\tag{3.5}
$$

Inequality (3.3) follows from similar steps to those included in the proof of [23, Lemma 2], which we adapt here to our setting. Through Jensen’s inequality, we obtain

$$
\begin{array}{l} \sigma_ {\mathrm{I}} ^ {2} \int_ {0} ^ {L} \int_ {0} ^ {L} \left(Q ^ {\frac {1}{2}} \left(\phi_ {\alpha} (x, y, s, [ 0, L ]) u _ {\alpha} ^ {\mathrm{I}} (y, s)\right)\right) ^ {2} \mathrm{d} y \mathrm{d} x \\ = \sigma_ {\mathrm{I}} ^ {2} L ^ {2} \int_ {0} ^ {L} \int_ {0} ^ {L} \left(Q ^ {\frac {1}{2}} \left(\phi_ {\alpha} (x, y, s, [ 0, L ]) u _ {\alpha} ^ {\mathrm{I}} (y, s)\right)\right) ^ {2} \frac {1}{L ^ {2}} \mathrm{d} y \mathrm{d} x \\ \geq \sigma_ {\mathrm{I}} ^ {2} L ^ {2} \left(\int_ {0} ^ {L} \int_ {0} ^ {L} Q ^ {\frac {1}{2}} \left(\phi_ {\alpha} (x, y, s, [ 0, L ]) u _ {\alpha} ^ {\mathrm{I}} (y, s)\right) \frac {1}{L ^ {2}} \mathrm{d} y \mathrm{d} x\right) ^ {2} \\ = \sigma_ {\mathrm{I}} ^ {2} L ^ {2} \left(\zeta_ {0} ^ {\frac {1}{2}} \int_ {0} ^ {L} \int_ {0} ^ {L} \left(\phi_ {\alpha} (x, y, s, [ 0, L ]) u _ {\alpha} ^ {\mathrm{I}} (y, s)\right) \frac {1}{L ^ {2}} \mathrm{d} y \mathrm{d} x\right) ^ {2} = \zeta_ {0} \frac {\sigma_ {\mathrm{I}} ^ {2}}{L ^ {2}} M (s) ^ {2}. \end{array}
$$

The proof is concluded by integrating of the left-hand side and right-hand side over the time interval $s \in [ 0 , t ] ,$ , for $t \in [ 0 , T ]$

As indicated in (3.2), the observable M is equivalent to the $L ^ { 1 } ( [ 0 , L ] ) \mathrm { - n o r m ~ o f ~ } u _ { \alpha } ^ { \mathrm { I } }$ rescaled in time through an exponential weight. The weight increases with time $t ,$ and its efect balances the dissipative term in the cable equation in (2.3) for $\alpha > 0$ . Consequently, the integrands in (3.4) do not depend on t, and M is a martingale. The simplicity of the formula is a consequence of the fact that $\lambda _ { 0 } = 0$ and that the corresponding eigenfunction e<sub>0</sub> is constant.

We set $\begin{array} { r } { J _ { 1 } = \frac { | | q _ { 0 } | | _ { 1 } } { L } } \end{array}$ and $J _ { 0 } \mathrm { e } ^ { - T \alpha } < J _ { 1 } \mathrm { e } ^ { - T \alpha } < J _ { 1 } < J _ { 2 }$ . From construction, we obtain $M ( 0 ) = L J _ { 1 } \mathrm { e } ^ { - T \alpha }$ . The values $J _ { 0 } , J _ { 1 }$ and $J _ { 2 }$ are chosen to guarantee the correctness of the studied inequalities upon rescaling of $L , \sigma _ { \mathrm { { I } } } , c$ and T . Lastly, we define the stopping time τ as the first time in which $M ( t )$ assumes the values $\stackrel { \cdot } { L } J _ { 0 } \mathrm { e } ^ { - T \alpha }$ or $L J _ { 2 }$

Lemma 3.2. For any $\alpha > 0 , \sigma _ { I } > 0 , T > 0$ we set $J _ { 0 } , J _ { 1 }$ and $J _ { 2 }$ as defined above. Then, the following result holds:

$$
\mathbb {P} \left(M (\tau) = L J _ {2}\right) = \frac {J _ {1} - J _ {0}}{J _ {2} \mathrm{e} ^ {T \alpha} - J _ {0}}.\tag{3.6}
$$

Furthermore, we obtain the bound

$$
\mathbb {P} \left(M (\tau \wedge T) = L J _ {2}\right) \geq \frac {J _ {1} - J _ {0}}{J _ {2} \mathrm{e} ^ {T \alpha} - J _ {0}} - \left(\frac {J _ {2}}{J _ {0}} \mathrm{e} ^ {T \alpha} - \frac {J _ {1}}{J _ {0}}\right) \frac {L}{\zeta_ {0} ^ {\frac {1}{2}} \sigma_ {I}} T ^ {- \frac {1}{2}},\tag{3.7}
$$

for $\tau \wedge T = m i n \{ \tau , T \}$

Proof. Since M is a martingale, we can apply Doob’s optional stopping theorem to obtain that $\mathbb { E } ( M ( \tau ) ) = \mathbb { E } ( M ( 0 ) ) = L J _ { 1 } \mathrm { e } ^ { - T \alpha }$

The definition of the stopping time τ implies that

$$
\mathbb {E} (M (\tau)) = L J _ {2} \mathbb {P} \left(M (\tau) = L J _ {2}\right) + L J _ {0} \mathrm{e} ^ {- T \alpha} \left(1 - \mathbb {P} \left(M (\tau) = L J _ {2}\right)\right),
$$

from which equality (3.6) follows. The Dubins-Schwarz theorem and the fact that M is a continuous martingale entail that

$$
M (t) = L J _ {1} \mathrm{e} ^ {- T \alpha} + \tilde {W} \left(\langle M \rangle (t)\right),
$$

for some scalar Wiener process $\tilde { W } ( t )$ and any $t \in [ 0 , T ]$ . Setting the martingale in such a form implies

$$
\begin{array}{l} \mathbb {P} \left(T <   \tau\right) = \mathbb {P} \left(T <   t, L J _ {0} \mathrm{e} ^ {- T \alpha} <   M (t) <   L J _ {2}, \text { for } t \in [ 0, T ]\right) \\ \qquad \leq \mathbb {P} \left(T <   t, M (t) <   L J _ {2}, \text { for } t \in [ 0, T ]\right) \\ \qquad = \mathbb {P} \left(T <   t, L J _ {1} \mathrm{e} ^ {- T \alpha} + \tilde {W} \left(\langle M \rangle (t)\right) <   L J _ {2}, \text { for } t \in [ 0, T ]\right). \end{array}\tag{3.8}
$$

In the case $t < \tau$ , it follows from (3.3) that

$$
\langle M \rangle (t) \geq \zeta_ {0} \sigma_ {\mathrm{I}} ^ {2} J _ {0} ^ {2} \mathrm{e} ^ {- 2 T \alpha} t
$$

and, from (3.8), that

$$
\begin{array}{l} \mathbb {P} \left(T <   \tau\right) \leq \mathbb {P} \left(T <   t, L J _ {1} \mathrm{e} ^ {- T \alpha} + \tilde {W} \left(\langle M \rangle \left(t\right)\right) <   L J _ {2}, \text {for} t \in [ 0, T ]\right) \\ \qquad \leq \mathbb {P} \left(T <   t, L J _ {1} \mathrm{e} ^ {- T \alpha} + \tilde {W} \left(t\right) <   L J _ {2}, \text {for} t \in [ 0, \langle M \rangle \left(T\right) ]\right) \\ \qquad \leq \mathbb {P} \left(T <   t, L J _ {1} \mathrm{e} ^ {- T \alpha} + \tilde {W} \left(t\right) <   L J _ {2}, \text {for} t \in \left[ 0, \zeta_ {0} \sigma_ {\mathrm{I}} ^ {2} J _ {0} ^ {2} \mathrm{e} ^ {- 2 T \alpha} T \right]\right). \end{array}
$$

Subsequently, we get

$$
\begin{array}{l} \mathbb {P} \left(T <   \tau\right) \leq \mathbb {P} \left(T <   t, L J _ {1} \mathrm{e} ^ {- T \alpha} + \tilde {W} \left(t\right) <   L J _ {2}, \text { for } t \in \left[ 0, \zeta_ {0} \sigma_ {\mathrm{I}} ^ {2} J _ {0} ^ {2} \mathrm{e} ^ {- 2 T \alpha} T \right]\right) \\ \quad \leq \mathbb {P} \left(\sup _ {t \in \left[ 0, \zeta_ {0} \sigma_ {\mathrm{I}} ^ {2} J _ {0} ^ {2} \mathrm{e} ^ {- 2 T \alpha} T \right]} \tilde {W} \left(t\right) <   L J _ {2} - L J _ {1} \mathrm{e} ^ {- T \alpha}\right) \\ = 1 - \mathbb {P} \left(\sup _ {t \in \left[ 0, \zeta_ {0} \sigma_ {\mathrm{I}} ^ {2} J _ {0} ^ {2} \mathrm{e} ^ {- 2 T \alpha} T \right]} \tilde {W} \left(t\right) \geq L J _ {2} - L J _ {1} \mathrm{e} ^ {- T \alpha}\right). \end{array}
$$

Then, through the reflection principle, we obtain

$$
\begin{array}{l} \mathbb {P} \left(T <   \tau\right) \leq 1 - \mathbb {P} \left(\sup _ {t \in \left[ 0, \zeta_ {0} \sigma_ {\mathrm{I}} ^ {2} J _ {0} ^ {2} \mathrm{e} ^ {- 2 T \alpha} T \right]} \tilde {W} \left(t\right) \geq L J _ {2} - L J _ {1} \mathrm{e} ^ {- T \alpha}\right) \\ = 1 - 2 \mathbb {P} \left(\tilde {W} \left(\zeta_ {0} \sigma_ {\mathrm{I}} ^ {2} J _ {0} ^ {2} \mathrm{e} ^ {- 2 T \alpha} T\right) \geq L J _ {2} - L J _ {1} \mathrm{e} ^ {- T \alpha}\right) \\ = \mathbb {P} \left(\left| \tilde {W} \left(\zeta_ {0} \sigma_ {\mathrm{I}} ^ {2} J _ {0} ^ {2} \mathrm{e} ^ {- 2 T \alpha} T\right) \right| \leq L J _ {2} - L J _ {1} \mathrm{e} ^ {- T \alpha}\right) \\ = \left(2 \pi \zeta_ {0} \sigma_ {\mathrm{I}} ^ {2} J _ {0} ^ {2} \mathrm{e} ^ {- 2 T \alpha} T\right) ^ {- \frac {1}{2}} \int_ {- L J _ {2} + L J _ {1} \mathrm{e} ^ {- T \alpha}} ^ {L J _ {2} - L J _ {1} \mathrm{e} ^ {- T \alpha}} \exp \left(- \frac {x ^ {2}}{2 \zeta_ {0} \sigma_ {\mathrm{I}} ^ {2} J _ {0} ^ {2} \mathrm{e} ^ {- 2 T \alpha} T}\right) \mathrm{d} x \\ \leq \left(\frac {J _ {2}}{J _ {0}} \mathrm{e} ^ {T \alpha} - \frac {J _ {1}}{J _ {0}}\right) \frac {L}{\zeta_ {0} ^ {\frac {1}{2}} \sigma_ {\mathrm{I}}} T ^ {- \frac {1}{2}}. \end{array}\tag{3.9}
$$

From (3.6) and (3.9), it follows that

$$
\begin{array}{l} \mathbb {P} \left(M \left(\tau \wedge T\right) = L J _ {2}\right) = \mathbb {P} \left(M \left(\tau \wedge T\right) = L J _ {2}, T \geq \tau\right) \\ \qquad = \mathbb {P} \left(M \left(\tau\right) = L J _ {2}\right) - \mathbb {P} \left(M \left(\tau\right) = L J _ {2}, T <   \tau\right) \\ \qquad \geq \mathbb {P} \left(M \left(\tau\right) = L J _ {2}\right) - \mathbb {P} \left(T <   \tau\right) \\ \qquad \geq \frac {J _ {1} - J _ {0}}{J _ {2} \mathrm{e} ^ {T \alpha} - J _ {0}} - \left(\frac {J _ {2}}{J _ {0}} \mathrm{e} ^ {T \alpha} - \frac {J _ {1}}{J _ {0}}\right) \frac {L}{\zeta_ {0} ^ {\frac {1}{2}} \sigma_ {\mathrm{I}}} T ^ {- \frac {1}{2}}, \end{array}
$$

which concludes the proof.

The inequality (3.7) provides a tool to establish a lower bound to the probability of rise of the $L ^ { 1 } ( 0 , L )  – \mathrm { n o r m }$ of $u _ { \alpha } ^ { \mathrm { I } }$ . In fact, under

the assumption that $L J _ { 2 } = M \left( \tau \wedge T \right)$ , we can obtain the following:

$$
L J _ {2} = M \left(\tau \wedge T\right) = \exp \left(- \alpha \left(T - \tau \wedge T\right)\right) \left| \left| u _ {\alpha} ^ {\mathrm{I}} (\cdot , \tau \wedge T) \right| \right| _ {1} \leq \sup _ {0 \leq t \leq T} \left| \left| u _ {\alpha} ^ {\mathrm{I}} (\cdot , t) \right| \right| _ {1}.
$$

This entails that

$$
\frac {J _ {1} - J _ {0}}{J _ {2} \mathrm{e} ^ {T \alpha} - J _ {0}} - \left(\frac {J _ {2}}{J _ {0}} \mathrm{e} ^ {T \alpha} - \frac {J _ {1}}{J _ {0}}\right) \frac {L}{\zeta_ {0} ^ {\frac {1}{2}} \sigma_ {\mathrm{I}}} T ^ {- \frac {1}{2}} \leq \mathbb {P} \left(L J _ {2} \leq \sup _ {0 \leq t \leq T} \left| \left| u _ {\alpha} ^ {\mathrm{I}} (\cdot , t) \right| \right| _ {1}\right),\tag{3.10}
$$

which yields a further step towards the construction of a lower bound to the probability of the onset of turbulence. In fact, such a bound is carried over to the mild solution of (2.1) in the next corollary. Since the left-hand side can be negative for large values of $T ,$ the assumptions $\alpha \ll 1$ or $L \ll \sqrt { \zeta _ { 0 } } \sigma _ { \mathrm { I } }$ have to be enforced to ensure positivity for large intervals in time.

Corollary $\mathbf { 3 . 3 } , \mathbf { \Omega } ( a )$ We assume that $q ,$ the mild solution of (2.1) with Itô noise, satisfies $0 < q ( x , t ) \leq 2$ for any $x \in [ 0 , L ]$ and $t \in [ 0 , T ]$ . Furthermore, we set the initial conditions such that $\begin{array} { r } { 0 < J _ { 0 } \mathrm { e } ^ { - T \alpha } < \frac { | | q _ { 0 } | | _ { 1 } } { I _ { \cdot } } \mathrm { e } ^ { - T \alpha } < \frac { | | q _ { 0 } | | _ { 1 } } { I _ { \cdot } } < J _ { 2 } } \end{array}$ . Then we get

$$
\frac {J _ {1} - J _ {0}}{J _ {2} \mathrm{e} ^ {T} - J _ {0}} - \left(\frac {J _ {2}}{J _ {0}} \mathrm{e} ^ {T} - \frac {J _ {1}}{J _ {0}}\right) \frac {L}{\zeta_ {0} ^ {\frac {1}{2}} \sigma_ {I}} T ^ {- \frac {1}{2}} \leq \mathbb {P} \left(L J _ {2} \leq \underset {0 \leq t \leq T} {s u p} | | q (\cdot , t) | | _ {1}\right).
$$

(b) We consider $q ,$ the mild solution of (2.1) with Itô noise that satisfies $\begin{array} { r } { 0 < J _ { 0 } \mathrm { e } ^ { - T \alpha } < \frac { | | q _ { 0 } | | _ { 1 } } { I } \mathrm { e } ^ { - T \alpha } < \frac { | | q _ { 0 } | | _ { 1 } } { I } < J _ { 2 } < 2 } \end{array}$ . The following inequality holds:

$$
\sup _ {0 \leq t \leq T} \left(\frac {J _ {1} - J _ {0}}{J _ {2} \mathrm{e} ^ {t} - J _ {0}} - \left(\frac {J _ {2}}{J _ {0}} \mathrm{e} ^ {t} - \frac {J _ {1}}{J _ {0}}\right) \frac {L}{\zeta_ {0} ^ {\frac {1}{2}} \sigma_ {I}} t ^ {- \frac {1}{2}}\right) \leq \mathbb {P} \left(J _ {2} \leq \sup _ {0 \leq t \leq T} | | q (\cdot , t) | | _ {\infty}\right).\tag{3.11}
$$

Proof. The first statement follows directly from (3.10) for $\alpha = 1$ and Lemma 2.1 (a). In fact, since $q ( x , t ) \leq 2$ for all $x \in [ 0 , L ]$ and $t \in [ 0 , T ]$ ], we obtain

$$
\mathbb {P} \left(L J _ {2} \leq \sup _ {0 \leq t \leq T} \left| \left| u _ {1} ^ {\mathrm{I}} (\cdot , t) \right| \right| _ {1}\right) \leq \mathbb {P} \left(L J _ {2} \leq \sup _ {0 \leq t \leq T} | | q (\cdot , t) | | _ {1}\right).
$$

Similarly to the latter case, (3.10) for $\alpha = 1$ , Hölder’s inequality and Lemma 2.1 (c) imply that

$$
\begin{array}{l} \frac {J _ {1} - J _ {0}}{J _ {2} \mathrm{e} ^ {T} - J _ {0}} - \left(\frac {J _ {2}}{J _ {0}} \mathrm{e} ^ {T} - \frac {J _ {1}}{J _ {0}}\right) \frac {L}{\zeta_ {0} ^ {\frac {1}{2}} \sigma_ {\mathrm{I}}} T ^ {- \frac {1}{2}} \leq \mathbb {P} \left(L J _ {2} \leq \sup _ {0 \leq t \leq T} \big | \big | u _ {1} ^ {\mathrm{I}} (\cdot , t) \big | \big | _ {1}\right) \\ \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \\ \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qend{array}
$$

Lastly, we obtain that, for any $T _ { 0 } \leq T .$

$$
\mathbb {P} \left(J _ {2} \leq \sup _ {0 \leq t \leq T _ {0}} | | q (\cdot , t) | | _ {\infty}\right) \leq \mathbb {P} \left(J _ {2} \leq \sup _ {0 \leq t \leq T} | | q (\cdot , t) | | _ {\infty}\right),
$$

which concludes the proof.

The statement in Corollary 3.3 pertains to the case when we consider trajectories of q with initial conditions below the saddle state, $q _ { 0 } < q _ { 2 } ,$ and final conditions between the saddle and the turbulence state, $q _ { - } < J _ { 2 } < q _ { + }$ , thus indicating turbulence initiation. Moreover, the assumption $q ( x , t ) \leq 2$ for all $x \in [ 0 , L ]$ and $t \in [ 0 , T ]$ is also not required to obtain inequality (3.11).

In this setting, the lower bound is valid (positive), for large time intervals under the assumption of thin pipes or large noise intensity. Aside from the value $J _ { 2 }$ that indicates the transition to turbulence occurrence, the lower bound in (3.7) is afected by the choice of $J _ { 0 } .$ This has further implications on the role of the final time T since the definition of the stopping time $\tau$ depends on $J _ { 0 }$ . Yet, in (3.11), the sign of the lower bound is not afected by the size of the time interval considered and is constant for suficiently large T . This is reflected by the dissipation towards $q _ { 1 }$ in the drift component of the mild solution $q .$ Such a behaviour indicates that the possibility of initiation of turbulence is less likely after large times. This property is discussed further in Section 5.

## 4 Stratonovich noise: Comparison SPDEs in a logarithmic scale

In this section, we set $\sigma _ { \mathrm { S } } + \sigma _ { \mathrm { R } } > \sigma _ { \mathrm { I } } = 0$ as we study (2.1). In order to enforce the existence and uniqueness of the strong solution of the system with Stratonovich noise [10, Section 6.5], we enforce the following assumptions. For fixed $m \in \mathbb { N } _ { > 0 }$ , we assume that

$$
\zeta_ {i} = 0 \quad , \text {   for   } i > m,
$$

and that there exists an $i \in \{ 0 , \ldots , m \}$ such that $\zeta _ { i } > 0$ and $\langle e _ { 0 } , b _ { i } \rangle \neq 0$ . Adhering to the study of the linearized system as justified in Lemma 2.1, we focus on a generalized version of the system (2.3). The model

$$
\left\{ \begin{array}{l} \mathrm{d} u (x, t) = \left(\partial_ {x x} ^ {2} u (x, t) - g (x) u (x, t) + \sigma_ {\mathrm{R}} u (x, t) \circ F (\xi) (x, t)\right) \mathrm{d} t + \sigma_ {\mathrm{S}} u (x, t) \circ Q ^ {\frac {1}{2}} \mathrm{d} W _ {t}, \\ \partial_ {x} u (0, t) = \partial_ {x} u (L, t) = 0, \\ u (x, 0) = q _ {0} (x), \end{array} \right.\tag{4.1}
$$

for $x \in [ 0 , L ]$ and $t > 0 ,$ , accounts for space-heterogeneity through the inclusion of the non-negative function $g \in L ^ { 2 } ( [ 0 , L ] )$ . Such an assumption follows from the applications on which the cable equation is found, such as climate science [6], due to the recurrent discrepancies in certain domain regions that can be found in such fields. In the next subsections, we obtain a lower bound to the probability of the turbulence onset for white and red Stratonovich noise, respectively.

## 4.1 White Stratonovich noise

We set $\sigma _ { \mathrm { R } } = 0$ in order to study white Stratonovich noise in time in the equation (4.1). The following lemma enables the study of the system on a logarithmic scale through the inverse Cole-Hopf transformation, thus obtaining the KPZ equation [15].

Lemma 4.1. We consider $u _ { g } ^ { S } = u _ { g } ^ { S } ( x , t )$ , the strong solution of (4.1) for $x \in [ 0 , L ]$ and $t > 0$ . Then, $v _ { g } ^ { S } = v _ { g } ^ { S } ( x , t ) : = l o g \left( u _ { g } ^ { S } \right)$ solves

$$
\left\{ \begin{array}{c} d v _ {g} ^ {S} (x, t) = \Big (\partial_ {x x} ^ {2} v _ {g} ^ {S} (x, t) + \big (\partial_ {x} v _ {g} ^ {S} (x, t) \big) ^ {2} - g (x) \Big)   d t + \sigma_ {S} Q ^ {\frac {1}{2}} d W _ {t}, \\ \partial_ {x} v _ {g} ^ {S} (0, t) = \partial_ {x} v _ {g} ^ {S} (L, t) = 0, \\ v _ {g} ^ {S} (x, 0) = l o g \left(q _ {0} (x)\right), \end{array} \right.\tag{4.2}
$$

for $x \in [ 0 , L ]$ and $t > 0$

Proof. Imposing $u _ { g } ^ { \mathrm { S } } = \exp \left( v _ { g } ^ { \mathrm { S } } \right)$ in (4.1), we obtain

$$
\left\{ \begin{array}{l} \mathrm{d} v _ {g} ^ {\mathrm{S}} (x, t) = u _ {g} ^ {\mathrm{S}} (x, t) ^ {- 1} \circ \mathrm{d} u _ {g} ^ {\mathrm{S}} (x, t) \\ \qquad = \left(u _ {g} ^ {\mathrm{S}} (x, t) ^ {- 1} \partial_ {x x} ^ {2} u _ {g} ^ {\mathrm{S}} (x, t) - g (x) u _ {g} ^ {\mathrm{S}} (x, t)\right) \mathrm{d} t + \left(\sigma_ {\mathrm{S}} u _ {g} ^ {\mathrm{S}} (x, t) ^ {- 1} u _ {g} ^ {\mathrm{S}} (x, t)\right) \circ Q ^ {\frac {1}{2}} \mathrm{d} W _ {t} \\ \qquad = \left(\partial_ {x x} ^ {2} v _ {g} ^ {\mathrm{S}} (x, t) + \left(\partial_ {x} v _ {g} ^ {\mathrm{S}} (x, t)\right) ^ {2} - g (x)\right) \mathrm{d} t + \sigma_ {\mathrm{S}} Q ^ {\frac {1}{2}} \mathrm{d} W _ {t}, \\ u _ {g} ^ {\mathrm{S}} (0, t) \partial_ {x} v _ {g} ^ {\mathrm{S}} (0, t) = u _ {g} ^ {\mathrm{S}} (L, t) \partial_ {x} v _ {g} ^ {\mathrm{S}} (L, t) = 0, \\ \exp \left(v _ {g} ^ {\mathrm{S}} (x, 0)\right) = q _ {0} (x). \end{array} \right.
$$

The boundary conditions in (4.2) follow from the fact that $u _ { g } ^ { \mathrm { S } }$ and $q _ { 0 } { \mathrm { ~ a r e } } ,$ , by construction, almost surely positive functions for any $t > 0$ □

The key benefit of the logarithmic perspective is the conversion of noise from a multiplicative form to an additive one. As a consequence, the nature of the drift component in (4.1) and (4.2) is drastically diferent. The system (4.2) is not linear since a shear deformation term is included, and a linear-in-time flow afects the solution. The lemma to follow aims to simplify the problem further.

Lemma 4.2. We consider $v _ { g } ^ { S } ,$ strong solution of (4.2), and $w _ { g } ^ { S } = w _ { g } ^ { S } ( x , t )$ , a strong solution of

$$
\left\{ \begin{array}{l l} d w _ {g} ^ {S} (x, t) = \left(\partial_ {x x} ^ {2} w _ {g} ^ {S} (x, t) - g (x)\right) d t + \sigma_ {S} Q ^ {\frac {1}{2}} d W _ {t}, \\ \partial_ {x} w _ {g} ^ {S} (0, t) = \partial_ {x} w _ {g} ^ {S} (L, t) = 0, \\ w _ {g} ^ {S} (x, 0) = l o g \left(q _ {0} (x)\right), \end{array} \right.\tag{4.3}
$$

for $x \in [ 0 , L ]$ and $t > 0$ . Then we obtain $v _ { g } ^ { S } ( x , t ) \geq w _ { g } ^ { S } ( x , t )$ under the same sample of $W ,$ for any almost $x \in [ 0 , L ]$ and $t > 0$

Proof. We define $\tilde { w } = v _ { g } ^ { \mathrm { S } } - w _ { g } ^ { \mathrm { S } }$ . By construction it solves

$$
\left\{ \begin{array}{l} \partial_ {t} \tilde {w} (x, t) = \partial_ {x x} ^ {2} \tilde {w} (x, t) + \left(\partial_ {x} v _ {g} ^ {\mathrm{S}} (x, t)\right) ^ {2}, \\ \partial_ {x} \tilde {w} (0, t) = \partial_ {x} \tilde {w} (L, t) = 0, \\ \tilde {w} (x, 0) \equiv 0. \end{array} \right.
$$

The conclusion of the proof follows the same reasoning as Lemma 2.1.

For the existence of $w _ { g } ^ { \mathrm { S } } .$ , we refer to [6] and [10, Theorem 5.29]. System (4.3) can be easily observed along the elements of a basis in $L ^ { 2 } ( [ 0 , L ] )$ . In the following lemma, the projections of the strong solution $w _ { g } ^ { \mathrm { S } }$ along the eigenbasis of the Laplacian operator are studied.

Lemma 4.3. We consider $w _ { g } ^ { S } ,$ strong solution of (4.3) for $x \in [ 0 , L ]$ and $t > 0$ . Then, for all $n \in \mathbb N$ , the scalar product $I _ { n , g } ( t ) : = \left. e _ { n } , w _ { g } ^ { S } ( \cdot , t ) \right.$ solves

$$
\left\{ \begin{array}{l} d I _ {n, g} (t) = (- \lambda_ {n} I _ {n, g} (t) - \langle e _ {n}, g \rangle)   d t + \sigma_ {S} \sum_ {i = 0} ^ {m} \left(\zeta_ {i} ^ {\frac {1}{2}}   \langle e _ {n}, b _ {i} \rangle   d \beta_ {i} (t)\right), \\ I _ {n, g} (0) = \langle e _ {n}, l o g (q _ {0}) \rangle , \end{array} \right.\tag{4.4}
$$

for any $t > 0$

Proof. We arbitrarily fix $n \in \mathbb { N }$ . Through (4.3), we obtain

$$
\left\{ \begin{array}{l} \mathrm{d} \left\langle e _ {n}, w _ {g} ^ {\mathrm{S}} (\cdot , t) \right\rangle = \left(\left\langle e _ {n}, \partial_ {x x} ^ {2} w _ {g} ^ {\mathrm{S}} (\cdot , t) \right\rangle - \left\langle e _ {n}, g \right\rangle\right) \mathrm{d} t + \sigma_ {\mathrm{S}} \left\langle Q ^ {\frac {1}{2}} e _ {n}, \mathrm{d} W _ {t} \right\rangle \\ \qquad = \left(- \lambda_ {n} \left\langle e _ {n}, w _ {g} ^ {\mathrm{S}} (\cdot , t) \right\rangle - \left\langle e _ {n}, g \right\rangle\right) \mathrm{d} t + \sigma_ {\mathrm{S}} \left\langle  \sum_ {i = 0} ^ {m} \zeta_ {i} ^ {\frac {1}{2}} \left\langle e _ {n}, b _ {i} \right\rangle b _ {i}, \mathrm{d} W _ {t} \right\rangle \\ \qquad = \left(- \lambda_ {n} \left\langle e _ {n}, w _ {g} ^ {\mathrm{S}} (\cdot , t) \right\rangle - \left\langle e _ {n}, g \right\rangle\right) \mathrm{d} t + \sigma_ {\mathrm{S}}  \sum_ {i = 0} ^ {m} \left(\zeta_ {i} ^ {\frac {1}{2}} \left\langle e _ {n}, b _ {i} \right\rangle \mathrm{d} \beta_ {i} (t)\right), \\ I _ {n, g} (0) = \left\langle e _ {n}, \log {(q _ {0})} \right\rangle , \end{array} \right.
$$

for $t > 0 ,$ , which concludes the proof.

The previous lemmas in this section describe, in their entirety, a chain of inequalities that constitute a bound from below of the strong solution $u _ { g } ^ { \mathrm { S } }$ of system (4.1). This approach is employed in the following theorem to define a bound to the probability of growth in a fixed time of $u _ { g } ^ { \mathrm { S } }$ on regions of the domain.

Theorem 4.4. Under the assumption that $u _ { g } ^ { S }$ is the strong solution of (4.1) for $x \in [ 0 , L ]$ and $t > 0$ , the following inequality holds for any non-negative function $f \in L ^ { 2 } ( [ 0 , L ] )$ that is not almost everywhere zero:

$$
1 - \Phi \left(\frac {| | f | | _ {1} l o g \left(| | f | | _ {1} ^ {- 1} J ^ {\prime}\right) - \left(\left\langle \mathrm{e} ^ {t \partial_ {x x} ^ {2}} f , l o g \left(q _ {0}\right) \right\rangle - a _ {0} \left\langle e _ {0} , g \right\rangle t - \sum_ {n = 1} ^ {\infty} a _ {n} \frac {\left\langle e _ {n} , g \right\rangle}{\lambda_ {n}} \left(1 - \mathrm{e} ^ {- t \lambda_ {n}}\right)\right)}{\sigma_ {S} \left(\sum_ {i = 0} ^ {m} \zeta_ {i} \left(a _ {0} ^ {2} \left\langle e _ {0} , b _ {i} \right\rangle^ {2} t + \sum_ {(n _ {1} , n _ {2}) \neq (0 , 0)} a _ {n _ {1}} a _ {n _ {2}} \left(\frac {1 - \mathrm{e} ^ {- t \left(\lambda_ {n _ {1}} + \lambda_ {n _ {2}}\right)}}{\lambda_ {n _ {1}} + \lambda_ {n _ {2}}}\right) \left\langle e _ {n _ {1}} , b _ {i} \right\rangle \left\langle e _ {n _ {2}} , b _ {i} \right\rangle\right)\right) ^ {\frac {1}{2}}}\right) \leq \mathbb {P} \left(J ^ {\prime} \leq \left\langle f, u _ {g} ^ {S} (\cdot , t) \right\rangle\right).\tag{4.5}
$$

for Φ, the cumulative distribution function of a standard normal distributed random variable, $J ^ { \prime } > 0$ , and $\boldsymbol { a } _ { n } = \langle e _ { n } , f \rangle$ for any $n \in \mathbb { N }$

Proof. We know that

$$
I _ {n, g} (t) = \mathrm{e} ^ {- t \lambda_ {n}} I _ {n, g} (0) - \frac {\langle e _ {n} , g \rangle}{\lambda_ {n}} \left(1 - \mathrm{e} ^ {- t \lambda_ {n}}\right) + \sigma_ {\mathrm{S}} \sum_ {i = 0} ^ {m} \left(\zeta_ {i} ^ {\frac {1}{2}} \langle e _ {n}, b _ {i} \rangle \int_ {0} ^ {t} \mathrm{e} ^ {- (t - s) \lambda_ {n}} \mathrm{d} \beta_ {i} (s)\right)
$$

holds for any $n \in  { \mathbb { N } } _ { > 0 }$ , and that

$$
I _ {0, g} (t) = I _ {0, g} (0) - \langle e _ {0}, g \rangle t + \sigma_ {\mathrm{S}} \sum_ {i = 0} ^ {m} \left(\zeta_ {i} ^ {\frac {1}{2}} \langle e _ {0}, b _ {i} \rangle \beta_ {i} (s)\right).
$$

It follows that

$$
\mathbb {E} \left(I _ {n, g} (t)\right) = \mathrm{e} ^ {- t \lambda_ {n}} I _ {n, g} (0) - \frac {\langle e _ {n} , g \rangle}{\lambda_ {n}} \left(1 - \mathrm{e} ^ {- t \lambda_ {n}}\right),
$$

for any $n \in  { \mathbb { N } } _ { > 0 }$ , and also

$$
\mathbb {E} \left(I _ {0, g} (t)\right) = I _ {0, g} (0) - \langle e _ {0}, g \rangle t.
$$

Moreover, from the construction of the systems (4.4) and the limit

$$
\lim _ {n \to \infty} \frac {\lambda_ {n}}{1 + n ^ {2}} <   \infty ,
$$

we obtain that

$$
\mathbb {E} \left(\sum_ {n = 0} ^ {\infty} a _ {n} I _ {n, g} (t)\right) = a _ {0} \left(I _ {0, g} (0) - \langle e _ {0}, g \rangle t\right) + \sum_ {n = 1} ^ {\infty} a _ {n} \left(\mathrm{e} ^ {- t \lambda_ {n}} I _ {n, g} (0) - \frac {\langle e _ {n} , g \rangle}{\lambda_ {n}} \left(1 - \mathrm{e} ^ {- t \lambda_ {n}}\right)\right) <   \infty .
$$

Levy’s continuity lemma implies that $\scriptstyle \sum _ { n = 0 } ^ { \infty } a _ { n } I _ { n , g } ( t )$ has a Gaussian distribution with variance

$$
\begin{array}{l} \operatorname{Var} \left(\sum_ {n = 0} ^ {\infty} a _ {n} I _ {n, g} (t)\right) = \operatorname{Var} \left(\left\langle f, w _ {g} ^ {\mathrm{S}} (\cdot , t) \right\rangle\right) = \sigma_ {\mathrm{S}} ^ {2} \int_ {0} ^ {t} \left\langle f, \mathrm{e} ^ {s \partial_ {x x} ^ {2}} Q \mathrm{e} ^ {s \partial_ {x x} ^ {2}} f \right\rangle \mathrm{d} s \\ = \sigma_ {\mathrm{S}} ^ {2} \int_ {0} ^ {t} \left\langle \sum_ {n _ {1} = 0} ^ {\infty} a _ {n _ {1}} \mathrm{e} ^ {- s \lambda_ {n _ {1}}} e _ {n _ {1}}, Q \sum_ {n _ {2} = 0} ^ {\infty} a _ {n _ {2}} \mathrm{e} ^ {- s \lambda_ {n _ {2}}} e _ {n _ {2}} \right\rangle \mathrm{d} s \\ = \sigma_ {\mathrm{S}} ^ {2} \int_ {0} ^ {t} \left\langle \sum_ {n _ {1} = 0} ^ {\infty} \sum_ {i _ {1} = 0} ^ {m} a _ {n _ {1}} \mathrm{e} ^ {- s \lambda_ {n _ {1}}} \left\langle e _ {n _ {1}}, b _ {i _ {1}} \right\rangle b _ {i _ {1}}, \sum_ {n _ {2} = 0} ^ {\infty} \sum_ {i _ {2} = 0} ^ {m} \zeta_ {i _ {2}} a _ {n _ {2}} \mathrm{e} ^ {- s \lambda_ {n _ {2}}} \left\langle e _ {n _ {2}}, b _ {i _ {2}} \right\rangle b _ {i _ {2}} \right\rangle \mathrm{d} s \\ = \sigma_ {\mathrm{S}} ^ {2} \int_ {0} ^ {t} \sum_ {n _ {1} = 0} ^ {\infty} \sum_ {n _ {2} = 0} ^ {\infty} \sum_ {i = 0} ^ {m} a _ {n _ {1}} a _ {n _ {2}} \zeta_ {i} \mathrm{e} ^ {- s (\lambda_ {n _ {1}} + \lambda_ {n _ {2}})} \left\langle e _ {n _ {1}}, b _ {i} \right\rangle \left\langle e _ {n _ {2}}, b _ {i} \right\rangle \mathrm{d} s \\ = \sigma_ {\mathrm{S}} ^ {2} \sum_ {i = 0} ^ {m} \zeta_ {i} \left(a _ {0} ^ {2} \left\langle e _ {0}, b _ {i} \right\rangle^ {2} t + \sum_ {(n _ {1}, n _ {2}) \neq (0, 0)} a _ {n _ {1}} a _ {n _ {2}} \left(\frac {1 - \mathrm{e} ^ {- t (\lambda_ {n _ {1}} + \lambda_ {n _ {2}})}}{\lambda_ {n _ {1}} + \lambda_ {n _ {2}}}\right) \left\langle e _ {n _ {1}}, b _ {i} \right\rangle \left\langle e _ {n _ {2}}, b _ {i} \right\rangle\right), \end{array}
$$

and that

$$
\begin{array}{r l} & {\mathbb {P} \left(\sum_ {n = 0} ^ {\infty} a _ {n} I _ {n, g} (t) \geq J ^ {\prime \prime}\right) = 1 - \Phi \left(\frac {J ^ {\prime \prime} - \mathbb {E} \left(\sum_ {n = 0} ^ {\infty} a _ {n} I _ {n , g} (t)\right)}{\left(\mathrm{Var} \left(\sum_ {n = 0} ^ {\infty} a _ {n} I _ {n , g} (t)\right)\right) ^ {\frac {1}{2}}}\right)} \\ & {\quad = 1 - \Phi \left(\frac {J ^ {\prime \prime} - \left(a _ {0} \left(I _ {0 , g} (0) - \langle e _ {0} , g \rangle t\right) + \sum_ {n = 1} ^ {\infty} a _ {n} \left(\mathrm{e} ^ {- t \lambda_ {n}} I _ {n , g} (0) - \frac {\langle e _ {n} , g \rangle}{\lambda_ {n}} \left(1 - \mathrm{e} ^ {- t \lambda_ {n}}\right)\right)\right)}{\sigma_ {\mathrm{S}} \left(\sum_ {i = 0} ^ {m} \zeta_ {i} \left(a _ {0} ^ {2} \langle e _ {0} , b _ {i} \rangle^ {2} t + \sum_ {(n _ {1}, n _ {2}) \neq (0, 0)} a _ {n _ {1}} a _ {n _ {2}} \left(\frac {1 - \mathrm{e} ^ {- t (\lambda_ {n _ {1}} + \lambda_ {n _ {2}})}}{\lambda_ {n _ {1}} + \lambda_ {n _ {2}}}\right) \langle e _ {n _ {1}} , b _ {i} \rangle \langle e _ {n _ {2}} , b _ {i} \rangle\right)\right) ^ {\frac {1}{2}}}\right)} \\ & {\quad = 1 - \Phi \left(\frac {J ^ {\prime \prime} - \left(\left\langle \mathrm{e} ^ {t \partial_ {x x} ^ {2}} f , w _ {g} ^ {\mathrm{S}} (\cdot , 0) \right\rangle - a _ {0} \langle e _ {0} , g \rangle t - \sum_ {n = 1} ^ {\infty} a _ {n} \frac {\langle e _ {n} , g \rangle}{\lambda_ {n}} \left(1 - \mathrm{e} ^ {- t \lambda_ {n}}\right)\right)}{\sigma_ {\mathrm{S}} \left(\sum_ {i = 0} ^ {m} \zeta_ {i} \left(a _ {0} ^ {2} \langle e _ {0} , b _ {i} \rangle^ {2} t + \sum_ {(n _ {1}, n _ {2}) \neq (0, 0)} a _ {n _ {1}} a _ {{n _ {2}}} \left(\frac {1 - \mathrm{e} ^ {- t (\lambda_ {{n _ {1}}} + \lambda_ {{n _ {2}}})}}{\lambda_ {{n _ {1}}} + \lambda_ {{n _ {2}}}}\right) \langle e _ {{n _ {1}}}, b _ {{i}} \rangle \langle e _ {{n _ {2}}}, b _ {{i}} \rangle\right)\right) ^ {\frac {1}{2}}}\right),} \end{array}
$$

for $J ^ { \prime \prime } \in \mathbb { R }$ . We assume henceforth that $\sum _ { n = 0 } ^ { \infty } a _ { n } \ I _ { n , g } ( t ) \geq J ^ { \prime \prime }$ . We employ, in order, Lemma 4.3, Lemma $4 . 2 ,$ Jensen’s inequality and Lemma 4.1 as follows:

$$
| | f | | _ {1} \exp \left(| | f | | _ {1} ^ {- 1} J ^ {\prime \prime}\right) \leq | | f | | _ {1} \exp \left(| | f | | _ {1} ^ {- 1} \sum_ {n = 0} ^ {\infty} a _ {n} I _ {n, g} (t)\right) = | | f | | _ {1} \exp \left(| | f | | _ {1} ^ {- 1} \left\langle f, w _ {g} ^ {\mathrm{S}} (\cdot , t) \right\rangle\right)
$$

$$
\begin{array}{l} = | | f | | _ {1} \exp \left(| | f | | _ {1} ^ {- 1} \int_ {0} ^ {L} f (x) w _ {g} ^ {\mathrm{S}} (x, t) \mathrm{d} x\right) \leq | | f | | _ {1} \exp \left(| | f | | _ {1} ^ {- 1} \int_ {0} ^ {L} f (x) v _ {g} ^ {\mathrm{S}} (x, t) \mathrm{d} x\right) \\ \leq \frac {| | f | | _ {1}}{| | f | | _ {1}} \int_ {0} ^ {L} f (x) \exp \left(v _ {g} ^ {\mathrm{S}} (x, t)\right) \mathrm{d} x = \left\langle f, \exp \left(v _ {g} ^ {\mathrm{S}} (\cdot , t)\right) \right\rangle = \left\langle f, u _ {g} ^ {\mathrm{S}} (\cdot , t) \right\rangle . \end{array}
$$

This entails that

$$
\mathbb {P} \left(\sum_ {n = 0} ^ {\infty} a _ {n} I _ {n, g} (t) \geq J ^ {\prime \prime}\right) \leq \mathbb {P} \left(| | f | | _ {1} \exp \left(| | f | | _ {1} ^ {- 1} J ^ {\prime \prime}\right) \leq \left\langle f, u _ {g} ^ {\mathrm{S}} (\cdot , t) \right\rangle\right).
$$

The proof is concluded upon defining $J ^ { \prime } = | | f | | _ { 1 } \mathrm { e x p } \left( | | f | | _ { 1 } ^ { - 1 } J ^ { \prime \prime } \right)$

Theorem 4.4 provides a lower bound to the probability of the onset of $u _ { g } ^ { \mathrm { S } }$ under the assumption of heterogeneity in space, induced by the term g in (4.1). The bound highly depends on the choice of the function $f ,$ upon which the strong solution $u _ { g } ^ { \mathrm { { \bar { S } } } }$ is projected. While this function defines the observable and can, therefore, be assumed to be known in applications, the shape of the function $g$ is also required to compute the bound numerically. A more in-depth discussion can be found in [6].

In the next corollary, we assume $g \equiv 1$ in order to extend the statement of Theorem 4.4 to the study of $q ,$ the strong solution of system (2.1). The results provide a lower bound to the local initiation of turbulence in $q .$

Corollary 4.5. Under the assumption that $q ,$ strong solution of (2.1), satisfies $0 < q ( x , t ) \leq 2$ for any $x \in [ 0 , L ]$ and $t \in [ 0 , T ]$ the following inequality holds for any non-negative function $f \in L ^ { 2 } ( [ 0 , L ] )$ that is not almost everywhere zero:

$$
1 - \min _ {0 \leq t \leq T} \Phi \left(\frac {| | f | | _ {1} l o g \left(| | f | | _ {1} ^ {- 1} J ^ {\prime}\right) - \left\langle \mathrm{e} ^ {t \partial_ {x x} ^ {2}} f , l o g \left(q _ {0}\right) \right\rangle + a _ {0} L ^ {\frac {1}{2}} t}{\sigma_ {S} \left(\sum_ {i = 0} ^ {m} \zeta_ {i} \left(a _ {0} ^ {2} \left\langle e _ {0} , b _ {i} \right\rangle^ {2} t + \sum_ {(n _ {1} , n _ {2}) \neq (0 , 0)} a _ {n _ {1}} a _ {n _ {2}} \left(\frac {1 - \mathrm{e} ^ {- t \left(\lambda_ {n _ {1}} + \lambda_ {n _ {2}}\right)}}{\lambda_ {n _ {1}} + \lambda_ {n _ {2}}}\right) \left\langle e _ {n _ {1}} , b _ {i} \right\rangle \left\langle e _ {n _ {2}} , b _ {i} \right\rangle\right)\right) ^ {\frac {1}{2}}}\right) \leq \mathbb {P} \left(J ^ {\prime} \leq \sup _ {0 \leq t \leq T} \langle f, q (\cdot , t) \rangle\right),
$$

for Φ, the cumulative distribution function of a standard normal distributed random variable, $\boldsymbol { a } _ { n } ~ = ~ \langle \boldsymbol { e } _ { n } , \boldsymbol { f } \rangle$ for any $n \in \mathbb { N }$ $g = L ^ { \frac { 1 } { 2 } } e _ { 0 } \equiv 1$ and $J ^ { \prime } > 0$

Proof. For any $t \in [ 0 , T ]$ , we employ Lemma 2.1 to obtain

$$
\mathbb {P} \left(J ^ {\prime} \leq \left\langle f, u _ {g} ^ {\mathrm{S}} (\cdot , t) \right\rangle\right) \leq \mathbb {P} \left(J ^ {\prime} \leq \langle f, q (\cdot , t) \rangle\right) \leq \mathbb {P} \left(J ^ {\prime} \leq \sup _ {0 \leq t \leq T} \langle f, q (\cdot , t) \rangle\right).
$$

This implies that

$$
\max _ {0 \leq t \leq T} \mathbb {P} \left(J ^ {\prime} \leq \left\langle f, u _ {g} ^ {\mathrm{S}} (\cdot , t) \right\rangle\right) \leq \mathbb {P} \left(J ^ {\prime} \leq \sup _ {0 \leq t \leq T} \left\langle f, q (\cdot , t) \right\rangle\right).
$$

The statement of Theorem 4.4 concludes the proof.

Similarly to Corollary 3.3 (b), we discuss in the corollary to follow the rise of turbulence on the whole domain. Consequently, it does not require the upper bound $q \leq 2$ assumption imposed in Corollary 4.5. The corollaries are further compared in Section 5.

Corollary 4.6. For q, strong solution of (2.1) for any $x \in [ 0 , L ]$ and $t \in [ 0 , T ]$ , the following inequality holds:

$$
1 - \min _ {0 \leq t \leq T} \Phi \left(\frac {L ^ {\frac {1}{2}}}{\sigma_ {S} \left(\sum_ {i = 0} ^ {m} \zeta_ {i} \left\langle e _ {0} , b _ {i} \right\rangle^ {2}\right) ^ {\frac {1}{2}}} \left(t ^ {- \frac {1}{2}} \left(\log (J) - L ^ {- 1} \int_ {0} ^ {L} \log (q _ {0} (x))   d x\right) + t ^ {\frac {1}{2}}\right)\right) \leq \mathbb {P} \left(J \leq \sup _ {0 \leq t \leq T} | | q (\cdot , t) | | _ {\infty}\right),
$$

for Φ, the cumulative distribution function of a standard normal distributed random variable and $0 < J < 2$

Proof. We consider inequality (4.5) for $g = f = L ^ { \frac { 1 } { 2 } } e _ { 0 } \equiv 1$ and $J ^ { \prime } = L J .$ . This choice of $f \in L ^ { 2 } ( [ 0 , L ] )$ implies that

$$
\left\langle f, u _ {1} ^ {\mathrm{S}} (\cdot , t) \right\rangle = | | u _ {1} ^ {\mathrm{S}} (\cdot , t) | | _ {1},
$$

for any $t > 0$ . Therefore, we obtain

$$
1 - \min _ {0 \leq t \leq T} \Phi \left(\frac {L \log (J) - \int_ {0} ^ {L} \log (q _ {0} (x)) \mathrm{d} x + L t}{\sigma_ {\mathrm{S}} (L t) ^ {\frac {1}{2}} \left(\sum_ {i = 0} ^ {m} \zeta_ {i} \langle e _ {0} , b _ {i} \rangle^ {2}\right) ^ {\frac {1}{2}}}\right) \leq \mathbb {P} \left(L J \leq \sup _ {0 \leq t \leq T} | | u _ {1} ^ {\mathrm{S}} (\cdot , t) | | _ {1}\right).
$$

Lastly, we employ Hölder’s inequality and Lemma 2.1 in

$$
\mathbb {P} \left(L J \leq \sup _ {0 \leq t \leq T} | | u _ {1} ^ {\mathrm{S}} (\cdot , t) | | _ {1}\right) \leq \mathbb {P} \left(J \leq \sup _ {0 \leq t \leq T} | | u _ {1} ^ {\mathrm{S}} (\cdot , t) | | _ {\infty}\right) \leq \mathbb {P} \left(J \leq \sup _ {0 \leq t \leq T} | | q (\cdot , t) | | _ {\infty}\right),
$$

which proves the statement.

## 4.2 Red Stratonovich noise

In the previous subsection, we introduce an approach for the estimation of a lower bound to the probability of jump in (4.1) under the assumption of white Stratonovich noise, i.e., $\sigma _ { \mathrm { S } } > \sigma _ { \mathrm { R } } = 0$ . Conversely, we consider in the remainder part of the section the red noise assumption, i.e., $\sigma _ { \mathrm { R } } > \sigma _ { \mathrm { S } } = 0$ . The red noise influence can be interpreted in diferent manners depending on the operator $F$ and the adapted process $\xi = \xi ( x , t ) \ [ 1 7 , 2 0 , 2 1 , 2 9 ]$ . We consider the strong solution of

$$
\left\{ \begin{array}{l} \mathrm{d} \xi (x, t) = - \kappa \xi (x, t) \mathrm{d} t + \sigma_ {\xi} Q ^ {\frac {1}{2}} \mathrm{d} W _ {t} ^ {\prime}, \\ \xi (x, 0) \equiv 0, \end{array} \right.\tag{4.6}
$$

for $\kappa > 0 , \sigma _ { \xi } > 0 , x \in [ 0 , L ]$ and $t \geq 0$ . For simplicity of notation, the noise $W _ { t } ^ { \prime }$ is cylindrical, adapted, and independent from $W _ { t }$ Such an Ornstein-Uhlenbeck process enables the construction of q, the strong solution of (2.1), and of $u _ { g } ^ { \mathrm { R } } = u _ { g } ^ { \mathrm { \hat { R } } } ( x , t )$ , the strong solution of (4.1) for $x \in [ 0 , L ]$ and $t \geq 0$ . We define then the inverse Cole-Hopf transform $v _ { g } ^ { \mathrm { R } } : = \log \left( u _ { g } ^ { \mathrm { R } } \right)$ . Since the noise is of Stratonovich type and we are considering strong solutions of the involved systems [10, Theorem 5.29], the process solves

$$
\left\{ \begin{array}{l} \partial_ {t} v _ {g} ^ {\mathrm{R}} (x, t) = \partial_ {x x} ^ {2} v _ {g} ^ {\mathrm{R}} (x, t) + \left(\partial_ {x} v _ {g} ^ {\mathrm{R}} (x, t)\right) ^ {2} - g (x) + \sigma_ {\mathrm{R}} \circ F (\xi) (x, t), \\ \partial_ {x} v _ {g} ^ {\mathrm{R}} (0, t) = \partial_ {x} v _ {g} ^ {\mathrm{R}} (L, t) = 0, \\ v _ {g} ^ {\mathrm{R}} (x, 0) = \log \left(q _ {0} (x)\right), \end{array} \right.
$$

for $x \in [ 0 , L ]$ and $t \geq 0$ . Such a statement can be proven following the steps in the proof of Lemma 4.1 on the couple

$$
\binom{v _ {g} ^ {\mathrm{R}} (x, t)}{\xi (x, t)} = \binom{\log \left(u _ {g} ^ {\mathrm{R}}\right)}{\xi (x, t)}.
$$

Similarly, we note that the inequality

$$
v _ {g} ^ {\mathrm{R}} (x, t) \geq w _ {g} ^ {\mathrm{R}} (x, t)
$$

holds for $w _ { g } ^ { \mathrm { R } } = w _ { g } ^ { \mathrm { R } } ( x , t )$ , the strong solution of

$$
\left\{ \begin{array}{l} \partial_ {t} w _ {g} ^ {\mathrm{R}} (x, t) = \partial_ {x x} ^ {2} w _ {g} ^ {\mathrm{R}} (x, t) - g (x) + \sigma_ {\mathrm{R}} F (\xi) (x, t), \\ \partial_ {x} w _ {g} ^ {\mathrm{R}} (0, t) = \partial_ {x} w _ {g} ^ {\mathrm{R}} (L, t) = 0, \\ w _ {g} ^ {\mathrm{R}} (x, 0) = \log \left(q _ {0} (x)\right), \end{array} \right.\tag{4.7}
$$

following the reasoning of the proof in Lemma 4.2. We then focus on two interpretations of red noise influence. For $F = { \mathrm { I d } }$ , the identity operator on $L ^ { \bar { 2 } } ( [ 0 , L ] )$ ), the systems (4.6) and (4.7) can be rewritten as

$$
\left\{ \begin{array}{c} \mathrm{d} \binom{w _ {g} ^ {\mathrm{R}} (x, t)}{\xi (x, t)} = \left(\left( \begin{array}{c c} \partial_ {x x} ^ {2} & \sigma_ {\mathrm{R}} \\ 0 & - \kappa \end{array} \right) \binom{w _ {g} ^ {\mathrm{R}} (x, t)}{\xi (x, t)} - \binom{g (x)}{0}\right) \mathrm{d} t + \left( \begin{array}{c c} 0 & 0 \\ 0 & \sigma_ {\xi} Q ^ {\frac {1}{2}} \end{array} \right) \binom{\mathrm{d} W _ {t}}{\mathrm{d} W _ {t} ^ {\prime}}, \\ w _ {g} ^ {\mathrm{R}} (x, 0) = \log \left(q _ {0} (x)\right), \\ \xi (x, 0) \equiv 0; \end{array} \right.\tag{4.8}
$$

for $F = \partial _ { t }$ , they can be interpreted as

$$
\left\{ \begin{array}{c} \mathrm{d} \binom{w _ {g} ^ {\mathrm{R}} (x, t)}{\xi (x, t)} = \left(\left( \begin{array}{c c} \partial_ {x x} ^ {2} & - \kappa \sigma_ {\mathrm{R}} \\ 0 & - \kappa \end{array} \right) \binom{w _ {g} ^ {\mathrm{R}} (x, t)}{\xi (x, t)} - \binom{g (x)}{0}\right) \mathrm{d} t + \left( \begin{array}{c c} 0 & \sigma_ {\mathrm{R}} \sigma_ {\xi} Q ^ {\frac {1}{2}} \\ 0 & \sigma_ {\xi} Q ^ {\frac {1}{2}} \end{array} \right) \binom{\mathrm{d} W _ {t}}{\mathrm{d} W _ {t} ^ {\prime}}, \\ w _ {g} ^ {\mathrm{R}} (x, 0) = \log \left(q _ {0} (x)\right), \\ \xi (x, 0) \equiv 0, \end{array} \right.\tag{4.9}
$$

for $x \in [ 0 , L ]$ and $t \ \geq \ 0 .$ We focus first on (4.8); nevertheless, the systems, although qualitatively diferent, can be studied in a similar manner. In fact, the turbulence system (2.1) corresponding to the parameters and operator $F$ associated to (4.8) displays additive red noise in $L ^ { 2 } ( [ 0 , L ] ) \times L ^ { 2 } ( [ 0 , L ] )$ , which entails that the system (2.1) has a null Itô-Stratonovich correction term. Conversely, for parameters and operator $F$ corresponding to (4.9), the noise in system (2.1) is interpreted in the Stratonovich sense to implement the chain rule, in contrast to Itô’s lemma [7], further below. In Appendix A, the system (2.1) is converted to the Itô perspective for the cases covered in the paper. The equations are simulated in Figure 2, where the initiation of turbulence is observed under diferent assumptions through the TAMS algorithm. The results corresponding to (4.9) are displayed at the end of the subsection, discussed in Section 5 and proven in Appendix B.

We indicate with $\mathcal { D } \left( \partial _ { x x } ^ { 2 } \right)$ the domain of $\partial _ { x x } ^ { 2 } ,$ which is dense in $L ^ { 2 } ( [ 0 , L ] )$ for the assumed boundary conditions. We define the linear operator

$$
A := \left( \begin{array}{c c} \partial_ {x x} ^ {2} & \sigma_ {\mathrm{R}} \\ 0 & - \kappa \end{array} \right): \mathcal {D} \left(\partial_ {x x} ^ {2}\right) \times L ^ {2} ([ 0, L ]) \to L ^ {2} ([ 0, L ]) \times L ^ {2} ([ 0, L ]),
$$

and $A ^ { * }$ the adjoint operator in respect to $L ^ { 2 } ( [ 0 , L ] ) \times L ^ { 2 } ( [ 0 , L ] )$ . In the mild solution form, the system (4.8) is solved by

$$
\binom{w _ {g} ^ {\mathrm{R}} (x, t)}{\xi (x, t)} = \mathrm{e} ^ {t A} \binom{\log {(q _ {0} (x))}}{0} + \int_ {0} ^ {t} \mathrm{e} ^ {s A} \binom{- g (x)}{0} \mathrm{d} s + \int_ {0} ^ {t} \mathrm{e} ^ {(t - s) A} \left( \begin{array}{c c} 0 & 0 \\ 0 & \sigma_ {\xi} Q ^ {\frac {1}{2}} \end{array} \right) \binom{\mathrm{d} W _ {s}}{\mathrm{d} W _ {s} ^ {\prime}}.
$$

The covariance operator

$$
V _ {t} := \left( \begin{array}{c c} V _ {t} ^ {I} & V _ {t} ^ {I I} \\ V _ {t} ^ {I I I} & V _ {t} ^ {I V} \end{array} \right),
$$

associated to the solution of the system at time $t > 0$ , satisfies the finite-time Lyapunov equation [9, Lemma 2.45],

$$
A V _ {t} + V _ {t} A ^ {*} = \mathrm{e} ^ {t A} \left( \begin{array}{c c} 0 & 0 \\ 0 & \sigma_ {\xi} ^ {2} Q \end{array} \right) \mathrm{e} ^ {t A ^ {*}} - \left( \begin{array}{c c} 0 & 0 \\ 0 & \sigma_ {\xi} ^ {2} Q \end{array} \right).\tag{4.10}
$$

For simplicity, we assume that −κ is not an eigenvalue of $\partial _ { x x } ^ { 2 }$ . The semigroup $\mathrm { e } ^ { t A }$ is then defined as

$$
\mathrm{e} ^ {t A} = \left( \begin{array}{c c} \mathrm{e} ^ {t \partial_ {x x} ^ {2}} & \sigma_ {\mathrm{R}} t \int_ {0} ^ {1} \mathrm{e} ^ {t s \partial_ {x x} ^ {2}} \mathrm{e} ^ {- t (1 - s) \kappa} \mathrm{d} s \\ 0 & \mathrm{e} ^ {- t \kappa} \end{array} \right) = \left( \begin{array}{c c} \mathrm{e} ^ {t \partial_ {x x} ^ {2}} & \sigma_ {\mathrm{R}} \operatorname{R} \left(\partial_ {x x} ^ {2} + \kappa\right) \left(\mathrm{e} ^ {t \partial_ {x x} ^ {2}} - \mathrm{e} ^ {- t \kappa}\right) \\ 0 & \mathrm{e} ^ {- t \kappa} \end{array} \right)
$$

and its adjoint, in respect to the $L ^ { 2 } ( [ 0 , L ] ) \times L ^ { 2 } ( [ 0 , L ] )$ scalar product, is

$$
\mathrm{e} ^ {t A ^ {*}} = \mathrm{e} ^ {t A ^ {*}} = \left( \begin{array}{c c} \mathrm{e} ^ {t \partial_ {x x} ^ {2}} & 0 \\ \sigma_ {\mathrm{R}} \operatorname{R} \left(\partial_ {x x} ^ {2} + \kappa\right) \left(\mathrm{e} ^ {t \partial_ {x x} ^ {2}} - \mathrm{e} ^ {- t \kappa}\right) & \mathrm{e} ^ {- t \kappa} \end{array} \right),
$$

for R that indicates the resolvent of an operator. Solving (4.10) implies that

$$
V _ {t} ^ {I I} = \sigma_ {\mathrm{R}} \sigma_ {\xi} ^ {2} \mathrm{R} (\partial_ {x x} ^ {2} - \kappa) \left(\mathrm{e} ^ {- t \kappa} \mathrm{R} (\partial_ {x x} ^ {2} + \kappa) (\mathrm{e} ^ {t \partial_ {x x} ^ {2}} - \mathrm{e} ^ {- t \kappa}) - \frac {1 - \mathrm{e} ^ {- 2 t \kappa}}{2 \kappa}\right) Q,
$$

$$
V _ {t} ^ {I I I} = \sigma_ {\mathrm{R}} \sigma_ {\xi} ^ {2} Q \left(\mathrm{e} ^ {- t \kappa} \mathrm{R} \left(\partial_ {x x} ^ {2} + \kappa\right) \left(\mathrm{e} ^ {t \partial_ {x x} ^ {2}} - \mathrm{e} ^ {- t \kappa}\right) - \frac {1 - \mathrm{e} ^ {- 2 t \kappa}}{2 \kappa}\right) \mathrm{R} \left(\partial_ {x x} ^ {2} - \kappa\right),
$$

$$
V _ {t} ^ {I V} = \frac {\sigma_ {\xi} ^ {2}}{2 \kappa} \left(1 - \mathrm{e} ^ {- 2 t \kappa}\right) Q,
$$

![](images/fe02e6b55a5294ccca7b5433e6b32a13fef905ce9e0b4568114d7eaed12f0215.jpg)  
(a) Trajectory q solving (2.1) with F = Id and $\kappa = 0 . 5$ It shows turbulence onset with respect to the $L ^ { 1 } ( [ 0 , L ] ) { \mathrm { - n o r m } } .$

![](images/d1b4f50a3cfeb27cdbdf9b03116b51630d852bca5a1d467b671b46851a23705c.jpg)

![](images/2cf9ff43f21bb8ca6945cd2db61b9168b368ee872ee21f62d3be2ca8c45b64a0.jpg)  
(c) Trajectory q solving (2.1) with $F = \partial _ { t }$ and $\kappa = 0 . 0 5 .$ It shows turbulence onset with respect to the $L ^ { 1 } ( [ 0 , L ] )  – \mathrm { n o r m }$

(b) Trajectory q solving (2.1) with F = Id and $\kappa = 0 . 5$ It shows turbulence onset with respect to the $L ^ { \infty } ( [ 0 , L ] ) – \mathrm { n o r m }$  
![](images/ab3ccceb6a91b71bf93a9ea2eadd8793b88a10510724a8a112602edc7effd21e.jpg)  
(d) Trajectory q solving (2.1) with $F = \partial _ { t }$ and $\kappa = 0 . 0 5$ It shows turbulence onset with respect to the $L ^ { \infty } ( [ 0 , L ] ) – \mathrm { n o r m }$

![](images/43513f9e85a4ffc1f06a497d197b210793c44c68dab2dac7aef1080288a6d5a1.jpg)  
(e) Trajectory q solving (2.1)

$$
F = \partial_ {t}
$$

$$
\kappa = 0. 5.
$$

with respect to the $L ^ { 1 } ( [ 0 , L ] ) { \mathrm { - n o r m } } .$  
![](images/505a4e8334b71e9804d6115d38706c08ec2a4d31b0c6660878eb559bbf44a6be.jpg)  
(f) Trajectory q solving (2.1) with $F = \partial _ { t }$ and $\kappa = 0 . 5$ It shows turbulence onset  
with respect to the $L ^ { \infty } ( [ 0 , L ] ) – \mathrm { n o r m }$

Fig. 2 (a) and (b) show trajectories of variable q, solution of (2.1), indicating the turbulence onset event under additive red noise (see Appendix A), $1 . 5 = \sigma _ { \mathrm { R } } > \sigma _ { \mathrm { I } } = \sigma _ { \mathrm { S } } = 0$ and $F = { \mathrm { I d } } ;$ conversely, in (c), (d), (e) and (f) we consider Stratonovich red noise (see Appendix A), $0 . 5 = \sigma _ { \mathrm { R } } > \sigma _ { \mathrm { I } } = \sigma _ { \mathrm { S } } = 0$ and $F = \partial _ { t }$ . Similarly to Figure 1, the rare events are computed via the TAMS algorithm, for which we obtain 50 simulations each and use the respective norm as a score function. The size and the discretization of the space-time grid, the operator Q, the Reynolds parameter, and the initial condition are chosen as in Figure 1. We set the perturbation intensity of $\xi ,$ solution of (4.6), as $\sigma _ { \xi } = 0 . 1$ and its dissipation value is indicated under each subfigure. In (a), (c) and (e) we display the rise of $| | q | | _ { 1 }$ to the value $q _ { + } L ,$ , whereas in (b), (d) and (f) we capture the rise of $| | q | | _ { \infty }$ to the value $q _ { \pm } .$ The simulations are obtained through the discretized mild solution formula [10].

The parameter κ is associated solely with the dissipation of ξ in the case of additive red noise. This is in contrast with the case $F = \partial _ { t }$ , where it also indicates the intensity of a nonlinear perturbation term in $( \overset { \cdot } { 2 } . 1 )$ . In (c) and (d), the solution resembles the case of Stratonovich white noise, which corresponds to $\kappa = 0 ;$ whereas in (e) and (f), κ assumes a higher value and the solution tends to depart from the turbulent state in a short time scale.

and that the equation

$$
\begin{array}{r l} & {\partial_ {x x} ^ {2} V _ {t} ^ {I} + V _ {t} ^ {I} \partial_ {x x} ^ {2} = - \sigma_ {\mathrm{R}} ^ {2} \sigma_ {\xi} ^ {2} \Bigg (\mathrm{R} (\partial_ {x x} ^ {2} - \kappa) (\mathrm{e} ^ {- t \kappa} \mathrm{R} (\partial_ {x x} ^ {2} + \kappa) (\mathrm{e} ^ {t \partial_ {x x} ^ {2}} - \mathrm{e} ^ {- t \kappa}) - \frac {1 - \mathrm{e} ^ {- 2 t \kappa}}{2 \kappa}) Q} \\ & {\qquad + Q (\mathrm{e} ^ {- t \kappa} \mathrm{R} (\partial_ {x x} ^ {2} + \kappa) (\mathrm{e} ^ {t \partial_ {x x} ^ {2}} - \mathrm{e} ^ {- t \kappa}) - \frac {1 - \mathrm{e} ^ {- 2 t \kappa}}{2 \kappa}) \mathrm{R} (\partial_ {x x} ^ {2} - \kappa)} \\ & {\qquad + \mathrm{R} (\partial_ {x x} ^ {2} + \kappa) (\mathrm{e} ^ {t \partial_ {x x} ^ {2}} - \mathrm{e} ^ {- t \kappa}) Q \mathrm{R} (\partial_ {x x} ^ {2} + \kappa) (\mathrm{e} ^ {t \partial_ {x x} ^ {2}} - \mathrm{e} ^ {- t \kappa}) \Bigg)} \end{array}\tag{4.11}
$$

holds. For $( n _ { 1 } , n _ { 2 } ) \in \mathbb { N } \times \mathbb { N }$ , we label $\displaystyle p _ { n _ { 1 } , n _ { 2 } } = \langle e _ { n _ { 1 } } , Q e _ { n _ { 2 } } \rangle$ . For $( n _ { 1 } , n _ { 2 } ) \neq ( 0 , 0 )$ , the equation (4.11) entails the definition of

$$
\begin{array}{l} \gamma_ {n _ {1}, n _ {2}} := \left\langle e _ {n _ {1}}, V _ {t} ^ {I} e _ {n _ {2}} \right\rangle \\ = \frac {\sigma_ {\mathrm{R}} ^ {2} \sigma_ {\xi} ^ {2} p _ {n _ {1} , n _ {2}}}{(\lambda_ {n _ {1}} + \lambda_ {n _ {2}})} \Bigg (\frac {1}{\lambda_ {n _ {1}} + \kappa} \left(\frac {\mathrm{e} ^ {- t \kappa} \left(\mathrm{e} ^ {- t \lambda_ {n _ {1}}} - \mathrm{e} ^ {- t \kappa}\right)}{\lambda_ {n _ {1}} - \kappa} + \frac {1 - \mathrm{e} ^ {- 2 t \kappa}}{2 \kappa}\right) \\ \quad + \frac {1}{\lambda_ {n _ {2}} + \kappa} \left(\frac {\mathrm{e} ^ {- t \kappa} \left(\mathrm{e} ^ {- t \lambda_ {n _ {2}}} - \mathrm{e} ^ {- t \kappa}\right)}{\lambda_ {n _ {2}} - \kappa} + \frac {1 - \mathrm{e} ^ {- 2 t \kappa}}{2 \kappa}\right) - \frac {\left(\mathrm{e} ^ {- t \lambda_ {n _ {1}}} - \mathrm{e} ^ {- t \kappa}\right) \left(\mathrm{e} ^ {- t \lambda_ {n _ {2}}} - \mathrm{e} ^ {- t \kappa}\right)}{(\lambda_ {n _ {1}} - \kappa) (\lambda_ {n _ {2}} - \kappa)} \\ = \frac {\sigma_ {\mathrm{R}} ^ {2} \sigma_ {\xi} ^ {2} p _ {n _ {1} , n _ {2}}}{(\lambda_ {n _ {1}} + \lambda_ {n _ {2}})} \Bigg (\frac {\lambda_ {n _ {1}} + \lambda_ {n _ {2}} + 2 \kappa}{2 \kappa (\lambda_ {n _ {1}} + \kappa) (\lambda_ {n _ {2}} + \kappa)} - \mathrm{e} ^ {- t (\lambda_ {n _ {1}} + \lambda_ {n _ {2}})} \frac {1}{(\lambda_ {n _ {1}} - \kappa) (\lambda_ {n _ {2}} - \kappa)} \\ \quad + \mathrm{e} ^ {- t (\lambda_ {n _ {1}} + \kappa)} \frac {\lambda_ {n _ {1}} + \lambda_ {n _ {2}}}{(\lambda_ {n _ {1}} ^ {2} - \kappa^ {2}) (\lambda_ {n _ {2}} - \kappa)} + \mathrm{e} ^ {- t (\lambda_ {n _ {2}} + \kappa)} \frac {\lambda_ {n _ {1}} + \lambda_ {n _ {2}}}{(\lambda_ {n _ {1}} - \kappa) (\lambda_ {n _ {2}} ^ {2} - \kappa^ {2})} - \mathrm{e} ^ {- 2 t \kappa} \frac {\lambda_ {n _ {1}} + \lambda_ {n _ {2}}}{2 \kappa (\lambda_ {n _ {1}} - \kappa) (\lambda_ {n _ {2}} - \kappa)} \Bigg). \end{array}\tag{4.12}
$$

We then consider

$$
V _ {t} = \sigma_ {\xi} ^ {2} \int_ {0} ^ {t} \mathrm{e} ^ {s A} \left( \begin{array}{c c} 0 & 0 \\ 0 & Q \end{array} \right) \mathrm{e} ^ {s A ^ {*}} \mathrm{d} s,
$$

which implies that

$$
\begin{array}{l} \gamma_ {0, 0} = \left\langle \binom{e _ {0}}{0}, V _ {t} \binom{e _ {0}}{0} \right\rangle_ {L ^ {2} ([ 0, L ]) \times L ^ {2} ([ 0, L ])} = \left\langle e _ {0}, V _ {t} ^ {I} e _ {0} \right\rangle \\ = \sigma_ {\mathrm{R}} ^ {2} \sigma_ {\xi} ^ {2} \int_ {0} ^ {t} \left\langle e _ {0}, \mathrm{R} \left(\partial_ {x x} ^ {2} + k\right) \left(\mathrm{e} ^ {s \partial_ {x x} ^ {2}} - \mathrm{e} ^ {- s \kappa}\right) Q   \mathrm{R} \left(\partial_ {x x} ^ {2} + k\right) \left(\mathrm{e} ^ {s \partial_ {x x} ^ {2}} - \mathrm{e} ^ {- s \kappa}\right) e _ {0} \right\rangle \mathrm{d} s \\ = \frac {\sigma_ {\mathrm{R}} ^ {2} \sigma_ {\xi} ^ {2} p _ {0 , 0}}{\kappa^ {2}} \left(t - 2 \frac {1 - \mathrm{e} ^ {- t \kappa}}{\kappa} + \frac {1 - \mathrm{e} ^ {- 2 t \kappa}}{2 \kappa}\right). \end{array}\tag{4.13}
$$

In the theorem to follow, we discuss the lower bound of the probability of rise of $u _ { g } ^ { \mathrm { R } }$ , similarly to Theorem 4.4.

Theorem 4.7. We indicate as $u _ { g } ^ { R }$ the strong solution of (4.1) for $x \in [ 0 , L ]$ and $t > 0$ . Then the following inequality holds $f o r$ any non-negative function $f \in L ^ { 2 } ( [ 0 , L ] )$ that is not almost everywhere zero:

$$
1 - \Phi \left(\frac {J ^ {\prime \prime} - \left(\left\langle \mathrm{e} ^ {t \partial_ {x x} ^ {2}} f , l o g (q _ {0}) \right\rangle - a _ {0} \left\langle e _ {0} , g \right\rangle t - \sum_ {n = 1} ^ {\infty} a _ {n} \frac {\left\langle e _ {n} , g \right\rangle}{\lambda_ {n}} \left(1 - \mathrm{e} ^ {- t \lambda_ {n}}\right)\right)}{\left(\sum_ {(n _ {1} , n _ {2}) \in \mathbb {N} ^ {2}} (a _ {n _ {1}} a _ {n _ {2}} \gamma_ {n _ {1} , n _ {2}})\right) ^ {\frac {1}{2}}}\right) \leq \mathbb {P} \left(J ^ {\prime} \leq \left\langle f, u _ {g} ^ {R} (\cdot , t) \right\rangle\right),\tag{4.14}
$$

for Φ, the cumulative distribution function of a standard normal distributed random variable, $J ^ { \prime } > 0 , a _ { n } = \langle e _ { n } , f \rangle$ for any $n \in \mathbb { N }$ and $\left\{ \gamma _ { n _ { 1 } , n _ { 2 } } \right\} _ { ( n _ { 1 } , n _ { 2 } ) \in \mathbb { N } \times \mathbb { N } }$ as defined in (4.12) and in (4.13).

Proof. The proof follows the same steps as in Theorem 4.4, which we describe here in a more condensed manner. The pairing

$\left( \begin{array} { c } { w _ { g } ^ { \mathrm { R } } ( x , t ) } \\ { \xi ( x , t ) } \end{array} \right)$ , solution of (4.8) assumes a Gaussian distribution in $L ^ { 2 } ( [ 0 , L ] ) \times L ^ { 2 } ( [ 0 , L ] )$ . In particular, we obtain

$$
\mathbb {E} \binom{w _ {g} ^ {\mathrm{R}} (x, t)}{\xi (x, t)} = \mathrm{e} ^ {t A} \binom{\log {(q _ {0} (x))}}{0} + \int_ {0} ^ {t} \mathrm{e} ^ {s A} \binom{- g (x)}{0} \mathrm{d} s = \mathrm{e} ^ {t \partial_ {x x} ^ {2}} \log {(q _ {0} (x))} - \int_ {0} ^ {t} \mathrm{e} ^ {s \partial_ {x x} ^ {2}} g (x) \mathrm{d} s
$$

and its covariance operator is

$$
\sigma_ {\mathrm{R}} ^ {2} \int_ {0} ^ {t} \mathrm{e} ^ {s A} \left( \begin{array}{c c} 0 & 0 \\ 0 & Q \end{array} \right) \mathrm{e} ^ {s A ^ {*}}   \mathrm{d} s = \sigma_ {\mathrm{R}} ^ {2} \mathrm{e} ^ {- 2 t} \left( \begin{array}{c c} t ^ {2} \int_ {0} ^ {1} \mathrm{e} ^ {t s (\partial_ {x x} ^ {2} + \mathrm{Id})} \mathrm{d} s Q \int_ {0} ^ {1} \mathrm{e} ^ {t s (\partial_ {x x} ^ {2} + \mathrm{Id})} \mathrm{d} s & t \int_ {0} ^ {1} \mathrm{e} ^ {t s (\partial_ {x x} ^ {2} + \mathrm{Id})} \mathrm{d} s Q \\ t Q \int_ {0} ^ {1} \mathrm{e} ^ {t s (\partial_ {x x} ^ {2} + \mathrm{Id})} \mathrm{d} s & Q \end{array} \right).
$$

Setting $f \in L ^ { 2 } ( [ 0 , L ] )$ , it follows that

$$
\begin{array}{l} \mathbb {P} \left(\left\langle f, w _ {g} ^ {\mathrm{R}} \right\rangle \geq J ^ {\prime \prime}\right) = 1 - \Phi \left(\frac {J ^ {\prime \prime} - \left\langle f , \mathrm{e} ^ {t \partial_ {x x} ^ {2}} \log {(q _ {0})} - \int_ {0} ^ {t} \mathrm{e} ^ {s \partial_ {x x} ^ {2}} g \mathrm{d} s \right\rangle}{\langle f , V ^ {I} f \rangle^ {\frac {1}{2}}}\right) \\ = 1 - \Phi \left(\frac {J ^ {\prime \prime} - \left(\left\langle \mathrm{e} ^ {t \partial_ {x x} ^ {2}} f , w _ {g} ^ {\mathrm{R}} (\cdot , 0) \right\rangle - a _ {0}   \langle e _ {0} , g \rangle   t - \sum_ {n = 1} ^ {\infty} a _ {n}   \frac {\langle e _ {n} , g \rangle}{\lambda_ {n}}   (1 - \mathrm{e} ^ {- t \lambda_ {n}})\right)}{\left(\sum_ {(n _ {1} , n _ {2}) \in \mathbb {N} ^ {2}} (a _ {n _ {1}} a _ {n _ {2}} \gamma_ {n _ {1}, n _ {2}})\right) ^ {\frac {1}{2}}}\right), \end{array}
$$

for $J ^ { \prime \prime } \in \mathbb { R }$ . We assume that $\left. f , w _ { g } ^ { \mathrm { R } } \right. \geq J ^ { \prime \prime }$ and employ Jensen’s inequality to obtain

$$
\begin{array}{l} | | f | | _ {1} \exp \left(| | f | | _ {1} ^ {- 1} J ^ {\prime \prime}\right) \leq | | f | | _ {1} \exp \left(| | f | | _ {1} ^ {- 1} \left\langle f, w _ {g} ^ {\mathrm{R}} \right\rangle\right) = | | f | | _ {1} \exp \left(| | f | | _ {1} ^ {- 1} \int_ {0} ^ {L} f (x) w _ {g} ^ {\mathrm{R}} (x, t) \mathrm{d} x\right) \\ = | | f | | _ {1} \exp \left(| | f | | _ {1} ^ {- 1} \int_ {0} ^ {L} f (x) v _ {g} ^ {\mathrm{R}} (x, t) \mathrm{d} x\right) \leq \frac {| | f | | _ {1}}{| | f | | _ {1}} \int_ {0} ^ {L} f (x) \exp (v _ {g} ^ {\mathrm{R}} (x, t)) \mathrm{d} x \\ = \left\langle f, \exp \left(v _ {g} ^ {\mathrm{R}} (\cdot , t)\right) \right\rangle = \left\langle f, u _ {g} ^ {\mathrm{R}} (\cdot , t) \right\rangle . \end{array}
$$

We set $J ^ { \prime } = | | f | | _ { 1 } \mathrm { e x p } \left( | | f | | _ { 1 } ^ { - 1 } J ^ { \prime \prime } \right)$ , which implies the statement.

The lower bound (4.14) implies the following corollary, whose proof is equivalent to those in Corollary 4.5 and Corollary 4.6. Its statement is discussed in Section 5.

Corollary 4.8. In the following statements, we refer to Φ as the cumulative distribution function of a standard normal distributed random variable.

(a) We assume that $q ,$ strong solution of (2.1), satisfies $0 < q ( x , t ) \leq 2$ for any $x \in [ 0 , L ]$ and $t \in [ 0 , T ]$ . Then, the following inequality holds for any non-negative function $f \in L ^ { 2 } ( [ 0 , L ] )$ that is not almost everywhere zero:

$$
1 - \min _ {0 \leq t \leq T} \Phi \left(\frac {| | f | | _ {1} l o g \left(| | f | | _ {1} ^ {- 1} J ^ {\prime}\right) - \left\langle \mathrm{e} ^ {t \partial_ {x x} ^ {2}} f , l o g (q _ {0}) \right\rangle + \langle f , e _ {0} \rangle L ^ {\frac {1}{2}} t}{\left(\sum_ {(n _ {1} , n _ {2}) \in \mathbb {N} ^ {2}} (a _ {n _ {1}} a _ {n _ {2}} \gamma_ {n _ {1} , n _ {2}})\right) ^ {\frac {1}{2}}}\right) \leq \mathbb {P} \left(J ^ {\prime} \leq \sup _ {0 \leq t \leq T} \langle f, q (\cdot , t) \rangle\right),
$$

for $J ^ { \prime } > 0 , a _ { n } = \langle e _ { n } , f \rangle$ for any $n \in \mathbb { N }$ and $\left\{ \gamma _ { n _ { 1 } , n _ { 2 } } \right\} _ { ( n _ { 1 } , n _ { 2 } ) \in \mathbb { N } \times \mathbb { N } }$ as defined in (4.12) and in (4.13).

(b) For $q ,$ strong solution of (2.1) for any $x \in [ 0 , L ]$ and $t \in [ 0 , T ]$ , the following inequality holds

$$
\begin{array}{l} 1 - \underset {0 \leq t \leq T} {\text {min}}   \Phi \left(\frac {L ^ {\frac {1}{2}} \kappa}{\sigma_ {R} \sigma_ {\xi} p _ {0 , 0} ^ {\frac {1}{2}}} \frac {t ^ {\frac {1}{2}}}{\left(t - 2 \frac {1 - \mathrm{e} ^ {- t \kappa}}{\kappa} + \frac {1 - \mathrm{e} ^ {- 2 t \kappa}}{2 \kappa}\right) ^ {\frac {1}{2}}} \left(t ^ {- \frac {1}{2}} \left(\log (J) - L ^ {- 1} \int_ {0} ^ {L} \log (q _ {0} (x))   d x\right) + t ^ {\frac {1}{2}}\right)\right) \\ = 1 - \underset {0 \leq t \leq T} {\text {min}}   \Phi \left(\frac {L ^ {\frac {1}{2}}}{\gamma_ {0 , 0} ^ {\frac {1}{2}}} \left(\log (J) - L ^ {- 1} \int_ {0} ^ {L} \log (q _ {0} (x))   d x + t\right)\right) \leq \mathbb {P} \left(J \leq \underset {0 \leq t \leq T} {\text {sup}}   | | q (\cdot , t) | | _ {\infty}\right), \end{array}\tag{4.15}
$$

$$
f o r 0 <   J <   2.
$$

Remark 4.9. The system (4.8) has a strong solution with variable $w _ { g } ^ { \mathrm { R } }$ characterized by positive autocorrelation [21], conversely to (4.9). Another core diference in the models is that, for $g \equiv 0 ,$ , the covariance of the strong solution along e<sub>0</sub> diverges in (4.8) in the time limit, whereas it converges [17] in (4.9). Although the models difer greatly, the lower bounds can be obtained through similar methods (see Appendix B). Furthermore, for $\kappa > 0$ , the statement in Theorem 4.7 holds for $w _ { g } ^ { \mathrm { R } }$ defined in the system (4.9) by setting the constants

$$
\begin{array}{r l} & {\gamma_ {n _ {1}, n _ {2}} = \frac {\sigma_ {\mathrm{R}} ^ {2} \sigma_ {\xi} ^ {2} p _ {n _ {1} , n _ {2}}}{(\lambda_ {n _ {1}} + \lambda_ {n _ {2}})} \Bigg (\frac {2 \lambda_ {n _ {1}} \lambda_ {n _ {2}} + (\lambda_ {n _ {1}} + \lambda_ {n _ {2}}) \kappa}{2 (\lambda_ {n _ {1}} + \kappa) (\lambda_ {n _ {2}} + \kappa)} - \mathrm{e} ^ {- t (\lambda_ {n _ {1}} + \lambda_ {n _ {2}})} \frac {\lambda_ {n _ {1}} \lambda_ {n _ {2}}}{(\lambda_ {n _ {1}} - \kappa) (\lambda_ {n _ {2}} - \kappa)}} \\ & \qquad + \mathrm{e} ^ {- t (\lambda_ {n _ {1}} + \kappa)} \frac {\kappa \lambda_ {n _ {1}} (\lambda_ {n _ {1}} + \lambda_ {n _ {2}})}{(\lambda_ {n _ {1}} ^ {2} - \kappa^ {2}) (\lambda_ {n _ {2}} - \kappa)} + \mathrm{e} ^ {- t (\lambda_ {n _ {2}} + \kappa)} \frac {\kappa \lambda_ {n _ {2}} (\lambda_ {n _ {1}} + \lambda_ {n _ {2}})}{(\lambda_ {n _ {1}} - \kappa) (\lambda_ {n _ {2}} ^ {2} - \kappa^ {2})} \\ & {\qquad - \mathrm{e} ^ {- 2 t \kappa} \frac {\kappa (\lambda_ {n _ {1}} + \lambda_ {n _ {2}})}{2 (\lambda_ {n _ {1}} - \kappa) (\lambda_ {n _ {2}} - \kappa)} \Bigg),} \end{array}\tag{4.16}
$$

for $( n _ { 1 } , n _ { 2 } ) \in \mathbb { N } \times \mathbb { N } \setminus ( 0 , 0 )$ , and

$$
\gamma_ {0, 0} = \sigma_ {\mathrm{R}} ^ {2} \sigma_ {\xi} ^ {2} p _ {0, 0} \frac {1 - \mathrm{e} ^ {- 2 t \kappa}}{2 \kappa},\tag{4.17}
$$

and assuming, for simplicity, that −κ is not an eigenvalue of the Laplacian. For system assumptions associated to (4.9), the statement in Corollary 4.8 (a) is also equivalent, with the updated constants $\left\{ \gamma _ { n _ { 1 } , n _ { 2 } } \right\} _ { ( n _ { 1 } , n _ { 2 } ) \in \mathbb { N } \times \mathbb { N } }$ shown in (4.16) and (4.17). In contrast, the corresponding inequality to (4.15) is

$$
\begin{array}{l} 1 - \underset {0 \leq t \leq T} {\min} \Phi \left(\frac {(2 \kappa L) ^ {\frac {1}{2}}}{\sigma_ {\mathrm{R}} \sigma_ {\xi} p _ {0 , 0} ^ {\frac {1}{2}}} \frac {t ^ {\frac {1}{2}}}{(1 - \mathrm{e} ^ {- 2 t \kappa}) ^ {\frac {1}{2}}} \left(t ^ {- \frac {1}{2}} \left(\log (J) - L ^ {- 1} \int_ {0} ^ {L} \log (q _ {0} (x))   \mathrm{d} x\right) + t ^ {\frac {1}{2}}\right)\right) \\ = 1 - \underset {0 \leq t \leq T} {\min} \Phi \left(\frac {L ^ {\frac {1}{2}}}{\gamma_ {0 , 0} ^ {\frac {1}{2}}} \left(\log (J) - L ^ {- 1} \int_ {0} ^ {L} \log (q _ {0} (x))   \mathrm{d} x + t\right)\right) \leq \mathbb {P} \left(J \leq \underset {0 \leq t \leq T} {\sup} | | q (\cdot , t) | | _ {\infty}\right), \end{array}\tag{4.18}
$$

for $0 < J < 2$ and $\gamma _ { 0 , 0 }$ defined in (4.17).

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

## Acknowledgments

Author PB wants to thank Andreas Morr for his valuable insights on red noise and climate science.

## References

[1] D. Barkley. Modeling the transition to turbulence in shear flows. In J. Phys. Conf. Ser., volume 318, page 032001. IOP Publishing, 2011.

[2] D. Barkley. Theoretical perspective on the route to turbulence in a pipe. J. Fluid Mech., 803:P1, 2016.

[3] I. F. Barna, G. Bognár, M. Guedda, K. Hriczó, and L. Mátyás. Analytic self-similar solutions of the kardar-parisi-zhang interface growing equation with various noise term. arXiv preprint arXiv:1904.01838, 2019.

[4] N. Berglund and R. Nader. Stochastic resonance in stochastic pdes. Stoch. Partial Difer. Equ.: Anal. Comput., 11(1):348–387, 2023.

[5] P. Bernuzzi and T. Grafke. Large deviation minimisers for stochastic partial diferential equations with degenerate noise. arXiv preprint arXiv:2409.17839, 2024.

[6] P. Bernuzzi and C. Kuehn. Bifurcations and early-warning signs for spdes with spatial heterogeneity. J. Dyn. Difer. Equ., pages 1–45, 2023.

[7] Z. Brzeźniak, J. M. van Neerven, M. C. Veraar, and L. Weis. Itô’s formula in umd banach spaces and regularity of solutions of the zakai equation. J. Difer. Equ., 245(1):30–58, 2008.

[8] I. Corwin. Exactly solving the kpz equation. arXiv preprint arXiv:1804.05721, 2018.

[9] G. Da Prato. Kolmogorov equations for stochastic PDEs. Springer Science & Business Media, 2004.

[10] G. Da Prato and J. Zabczyk. Stochastic equations in infinite dimensions, volume 152. Cambridge university press, 2014.

[11] F. Flandoli and U. Pappalettera. 2d euler equations with stratonovich transport noise as a large-scale stochastic model reduction. J. Nonlinear Sci., 31(1):24, 2021.

[12] C. W. Gardiner. Handbook of stochastic methods for physics, chemistry and the natural sciences. Springer series in synergetics, 1985.

[13] S. Gomé, A. Rivière, L. S. Tuckerman, and D. Barkley. Phase transition to turbulence via moving fronts. Phys. Rev. Lett., 132(26):264002, 2024.

[14] S. Gomé, L. S. Tuckerman, and D. Barkley. Extreme events in transitional turbulence. Philos. Trans. R. Soc. A, 380(2226):20210036, 2022.

[15] M. Hairer. Solving the kpz equation. Ann. Math., pages 559–664, 2013.

[16] D. D. Holm. Stochastic modelling in fluid dynamics: It\ˆ o vs stratonovich. arXiv preprint arXiv:1911.09657, 2019.

[17] C. Kuehn, K. Lux, and A. Neamtu. Warning signs for non-markovian bifurcations: Color blindness and scaling laws. arXiv preprint arXiv:2106.08374, 2021.

[18] L. D. Landau and E. M. Lifshitz. Fluid Mechanics: Volume 6, volume 6. Elsevier, 1987.

[19] T. Lestang, F. Ragone, C.-E. Bréhier, C. Herbert, and F. Bouchet. Computing return times or return periods with rare event algorithms. J. Stat. Mech.: Theory Exp., 2018(4):043213, 2018.

[20] A. Morr and N. Boers. Detection of approaching critical transitions in natural systems driven by red noise. Phys. Rev. X, 14(2):021037, 2024.

[21] A. Morr, D. Kreher, and N. Boers. Red noise in continuous-time stochastic modelling. arXiv preprint arXiv:2212.03566, 2022.

[22] C. Mueller. Long time existence for the heat equation with a noise term. Probab. Theory Relat. Fields, 90:505–517, 1991.

[23] C. Mueller. The critical parameter for the heat equation with a noise term to blow up in finite time. Ann. Probab., 28(4):1735– 1746, 2000.

[24] C. Mueller and R. Sowers. Blowup for the heat equation with a noise term. Probab. Theory Relat. Fields, 97(3):287–320, 1993.

[25] M. A. Munoz. Multiplicative noise in non-equilibrium phase transitions: A tutorial. arXiv preprint cond-mat/0303650, 2003.

[26] Y. Pomeau. Front motion, metastability and subcritical bifurcations in hydrodynamics. Phys. D: Nonlinear Phenom., 23(1- 3):3–11, 1986.

[27] Y. Pomeau. The transition to turbulence in parallel flows: a personal view. C. R. Méc, 343(3):210–218, 2015.

[28] M. Salins. Solutions to the stochastic heat equation with polynomially growing multiplicative noise do not explode in the critical regime. arXiv preprint arXiv:2309.04330, 2023.

[29] P. Sardeshmukh, C. Penland, and M. Newman. Drifts induced by multiplicative red noise with application to climate. EPL, 63(4):498, 2003.

[30] K. Twardowska and A. Nowak. On the relation between the itô and stratonovich integrals in hilbert spaces. In Ann. Math. Sil., volume 18, pages 49–63, 2004.

[31] J. B. Walsh. An introduction to stochastic partial diferential equations. Lect. Notes Math., pages 265–439, 1986.

[32] P. Wang, D. Castellana, and H. Dijkstra. Improvements to the use of the trajectory-adaptive multilevel sampling algorithm for the study of rare events. Nonlin. Process. Geophys. Discuss., 2020:1–24, 2020.

## A Appendix: Turbulence from the Itô noise perspective

Throughout the paper, system (2.1) is studied under diferent noise and parameters assumptions. In this appendix, we address the various cases and translate them to the Itô noise perspective through the Itô-Stratonovich correction term [12, 30]. The boundary conditions are assumed to be homogenous Neumann, and the initial condition is set at $q ( x , 0 ) = q _ { 0 } ( x )$

• In Section 3, the noise is assumed to be white and in Itô sense, i.e., $\sigma _ { \mathrm { S } } = \sigma _ { \mathrm { R } } = 0$ . The system studied is characterized, therefore, by the form

$$
\mathrm{d} q (x, t) = \left(\partial_ {x x} ^ {2} q (x, t) - q (x, t) + (r + 1) q (x, t) ^ {2} (2 - q (x, t))\right) \mathrm{d} t + \sigma_ {\mathrm{I}} q (x, t) Q ^ {\frac {1}{2}} \mathrm{d} W _ {t},
$$

for $x \in [ 0 , L ]$ and $t > 0$

• In Subsection 4.1, the noise is assumed white and in Stratonovich sense, $\mathrm { i . e . , ~ } \sigma _ { \mathrm { I } } = \sigma _ { \mathrm { R } } = 0$ . The first equation in (2.1) with Itô noise is then

$$
\mathrm{d} q (x, t) = \left(\partial_ {x x} ^ {2} q (x, t) - q (x, t) + (r + 1) q (x, t) ^ {2} (2 - q (x, t)) + \frac {\sigma_ {\mathrm{S}} ^ {2}}{2} q (x, t) \sum_ {i = 0} ^ {m} \left(\zeta_ {i} b _ {i} (x) ^ {2}\right)\right) \mathrm{d} t + \sigma_ {\mathrm{S}} q (x, t) Q ^ {\frac {1}{2}} \mathrm{d} W _ {t}.
$$

• In Subsection 4.2, we discuss the efect of red in time Stratonovich noise on the turbulence system, i.e., $\sigma _ { \mathrm { R } } > \sigma _ { \mathrm { I } } = \sigma _ { \mathrm { S } } = 0$ The variable q is coupled to the Ornstein-Uhlenbeck process, solution of (4.6), depending on the choice of the operator F . In (4.8), we set $F = { \mathrm { I d } }$ . Then, the first equation in (2.1) coupled with (4.6) can be interpreted as

$$
\mathrm{d} \binom{q (x, t)}{\xi (x, t)} = \binom{\partial_ {x x} ^ {2} q (x, t) - q (x, t) + (r + 1) q (x, t) ^ {2} (2 - q (x, t)) + \sigma_ {\mathrm{R}} q (x, t) \xi (x, t)}{- \kappa \xi} \mathrm{d} t + \left( \begin{array}{c c} 0 & 0 \\ 0 & \sigma_ {\xi} Q ^ {\frac {1}{2}} \end{array} \right) \binom{\mathrm{d} W _ {t}}{\mathrm{d} W _ {t} ^ {\prime}}.
$$

The noise is additive in $L ^ { 2 } ( [ 0 , L ] ) \times L ^ { 2 } ( [ 0 , L ] )$ , which implies that the Itô-Stratonovich correction term is null and the equation is equivalent regardless of the interpretation of the noise.

• In Remark 4.9, we discuss the lower bound to the probability of initiation of turbulence under Stratonovich red noise defined by $F = \partial _ { t }$ . The equation defining the behaviour of the variables q and ξ in time is, therefore,

$$
\begin{array}{l} \text {d} \binom{q (x, t)}{\xi (x, t)} = \binom{\partial_ {x x} ^ {2} q (x, t) - q (x, t) + (r + 1) q (x, t) ^ {2} (2 - q (x, t))}{- \kappa \xi} \text {d} t + \binom{\sigma_ {\mathrm{R}} q (x, t)}{0} \circ \text {d} \xi (x, t) + \left( \begin{array}{c c} 0 & 0 \\ 0 & \sigma_ {\xi} Q ^ {\frac {1}{2}} \end{array} \right) \binom{\text {d} W _ {t}}{\text {d} W _ {t} ^ {\prime}} \\ = \binom{\partial_ {x x} ^ {2} q (x, t) - q (x, t) + (r + 1) q (x, t) ^ {2} (2 - q (x, t)) - \sigma_ {\mathrm{R}} \kappa q (x, t) \xi (x, t)}{- \kappa \xi} \text {d} t \\ + \left( \begin{array}{c c} q (x, t) & 0 \\ 0 & 1 \end{array} \right) \circ \left( \begin{array}{c c} 0 & \sigma_ {\mathrm{R}} \sigma_ {\xi} Q ^ {\frac {1}{2}} \\ 0 & \sigma_ {\xi} Q ^ {\frac {1}{2}} \end{array} \right) \binom{\text {d} W _ {t}}{\text {d} W _ {t} ^ {\prime}}, \end{array}
$$

with noise in Stratonovich sense. Indicating with ∗ the adjoint operator in $L ^ { 2 } ( [ 0 , L ] ) \times L ^ { 2 } ( [ 0 , L ] )$ , the operator

$$
\left( \begin{array}{c c} 0 & \sigma_ {\mathrm{R}} \sigma_ {\xi} Q ^ {\frac {1}{2}} \\ 0 & \sigma_ {\xi} Q ^ {\frac {1}{2}} \end{array} \right) \left( \begin{array}{c c} 0 & \sigma_ {\mathrm{R}} \sigma_ {\xi} Q ^ {\frac {1}{2}} \\ 0 & \sigma_ {\xi} Q ^ {\frac {1}{2}} \end{array} \right) ^ {*} = \sigma_ {\xi} ^ {2} \left( \begin{array}{c c} 0 & \sigma_ {\mathrm{R}} Q ^ {\frac {1}{2}} \\ 0 & Q ^ {\frac {1}{2}} \end{array} \right) \left( \begin{array}{c c} 0 & 0 \\ \sigma_ {\mathrm{R}} Q ^ {\frac {1}{2}} & Q ^ {\frac {1}{2}} \end{array} \right) = \sigma_ {\xi} ^ {2} \left( \begin{array}{c c} \sigma_ {\mathrm{R}} ^ {2} Q & \sigma_ {\mathrm{R}} Q \\ \sigma_ {\mathrm{R}} Q & Q \end{array} \right)
$$

is characterized by purely discrete spectrum, composed by $\{ \mathbb { P } _ { i } , \mathbb { P } _ { i } ^ { \prime } \} _ { i \in \mathbb { N } } .$ These eigenvalues are defined as

$$
\Omega_ {i} := \left(1 + \sigma_ {\mathrm{R}} ^ {2}\right) \sigma_ {\xi} ^ {2} \zeta_ {i} \qquad \text { and } \qquad \Omega_ {i} ^ {\prime} := 0,
$$

for all $i \in \mathbb N$ . The corresponding eigenbasis in $L ^ { 2 } ( [ 0 , L ] ) \times L ^ { 2 } ( [ 0 , L ] )$ is composed by

$$
B _ {i} (x) := \left(1 + \sigma_ {\mathrm{R}} ^ {2}\right) ^ {- \frac {1}{2}} \binom{\sigma_ {\mathrm{R}} b _ {i} (x)}{b _ {i} (x)} \qquad \text { and } \qquad B _ {i} ^ {\prime} (x) := \left(1 + \sigma_ {\mathrm{R}} ^ {2}\right) ^ {- \frac {1}{2}} \binom{b _ {i} (x)}{- \sigma_ {\mathrm{R}} b _ {i} (x)},
$$

for all $i \in \mathbb N$ and $x \in [ 0 , L ]$ . The equation defining q and ξ is, then,

$$
\begin{array}{r l} & {\mathrm{d} \binom {q (x, t)} {\xi (x, t)} = \binom {\partial_ {x x} ^ {2} q (x, t) - q (x, t) + (r + 1) q (x, t) ^ {2} (2 - q (x, t)) - \sigma_ {\mathrm{R}} \kappa q (x, t) \xi (x, t)} {- \kappa \xi} \mathrm{d} t} \\ & {\qquad + \frac {1}{2 \left(1 + \sigma_ {\mathrm{R}} ^ {2}\right)} \binom {q (x, t) \partial_ {q} \left(q (x, t)\right) \sum_ {i = 0} ^ {m} \left(\Omega_ {i} \sigma_ {\mathrm{R}} ^ {2} b _ {i} (x) ^ {2} + \Omega_ {i} ^ {\prime} b _ {i} (x) ^ {2}\right)} {\partial_ {\xi} \left(1\right) \sum_ {i = 0} ^ {m} \left(\Omega_ {i} b _ {i} (x) ^ {2} + \Omega_ {i} ^ {\prime} \sigma_ {\mathrm{R}} ^ {2} b _ {i} (x) ^ {2}\right)} + \left( \begin{array}{c c} q (x, t) & 0 \\ 0 & 1 \end{array} \right) \left( \begin{array}{c c} 0 & \sigma_ {\mathrm{R}} \sigma_ {\xi} Q ^ {\frac {1}{2}} \\ 0 & \sigma_ {\xi} Q ^ {\frac {1}{2}} \end{array} \right) \binom {\mathrm{d} W _ {t}} {\mathrm{d} W _ {t} ^ {\prime}}} \end{array}
$$

Probability of Transition to Turbulence in a Reduced Stochastic Model of Pipe Flow

$$
\begin{array}{l} = \left( \begin{array}{c} \partial_ {x x} ^ {2} q (x, t) - q (x, t) + (r + 1) q (x, t) ^ {2} (2 - q (x, t)) - \sigma_ {\mathrm{R}} \kappa q (x, t) \xi (x, t) + \frac {\sigma_ {\mathrm{R}} ^ {2} \sigma_ {\xi} ^ {2}}{2} q (x, t) \sum_ {i = 0} ^ {m} \left(\zeta_ {i} b _ {i} (x) ^ {2}\right) \\ - \kappa \xi \end{array} \right) \mathrm{d} t \\ + \left( \begin{array}{c c} q (x, t) & 0 \\ 0 & 1 \end{array} \right) \left( \begin{array}{c c} 0 & \sigma_ {\mathrm{R}} \sigma_ {\xi} Q ^ {\frac {1}{2}} \\ 0 & \sigma_ {\xi} Q ^ {\frac {1}{2}} \end{array} \right) \binom{\mathrm{d} W _ {t}}{\mathrm{d} W _ {t} ^ {\prime}}, \end{array}
$$

with noise interpreted in Itô sense.

## B Appendix: Proof of lower bounds for alternative red noise

In this appendix, we study the covariance of the $w _ { g } ^ { \mathrm { R } } = w _ { g } ^ { \mathrm { R } } ( x , t )$ component of the strong solution of (4.9). The method resembles the one employed on the strong solution (4.8) in Section 4, which we outline below concisely. We define the operator

$$
A := \left( \begin{array}{c c} \partial_ {x x} ^ {2} & - \kappa \sigma_ {\mathrm{R}} \\ 0 & - \kappa \end{array} \right): \mathcal {D} \left(\partial_ {x x} ^ {2}\right) \times L ^ {2} ([ 0, L ]) \to L ^ {2} ([ 0, L ]) \times L ^ {2} ([ 0, L ])
$$

and its adjoint in $L ^ { 2 } ( [ 0 , L ] ) \times L ^ { 2 } ( [ 0 , L ] )$ ,

$$
A ^ {*} := \left( \begin{array}{c c} \partial_ {x x} ^ {2} & 0 \\ - \kappa \sigma_ {\mathrm{R}} & - \kappa \end{array} \right): \mathcal {D} \left(\partial_ {x x} ^ {2}\right) \times L ^ {2} ([ 0, L ]) \to L ^ {2} ([ 0, L ]) \times L ^ {2} ([ 0, L ]).
$$

The covariance operator,

$$
V _ {t} := \left( \begin{array}{c c} V _ {t} ^ {I} & V _ {t} ^ {I I} \\ V _ {t} ^ {I I I} & V _ {t} ^ {I V} \end{array} \right),
$$

of the solution of the system at time $t > 0$ satisfies the finite-time Lyapunov equation,

$$
A V _ {t} + V _ {t} A ^ {*} = \mathrm{e} ^ {t A} \left( \begin{array}{c c} \sigma_ {\mathrm{R}} ^ {2} \sigma_ {\xi} ^ {2} Q & \sigma_ {\mathrm{R}} \sigma_ {\xi} ^ {2} Q \\ \sigma_ {\mathrm{R}} \sigma_ {\xi} ^ {2} Q & \sigma_ {\xi} ^ {2} Q \end{array} \right) \mathrm{e} ^ {t A ^ {*}} - \left( \begin{array}{c c} \sigma_ {\mathrm{R}} ^ {2} \sigma_ {\xi} ^ {2} Q & \sigma_ {\mathrm{R}} \sigma_ {\xi} ^ {2} Q \\ \sigma_ {\mathrm{R}} \sigma_ {\xi} ^ {2} Q & \sigma_ {\xi} ^ {2} Q \end{array} \right).\tag{B.1}
$$

Once again, for simplicity, we assume that −κ is not an eigenvalue of $\partial _ { x x } ^ { 2 }$ . The semigroup $\mathrm { e } ^ { t A }$ is then defined as

$$
\mathrm{e} ^ {t A} = \left( \begin{array}{c c} \mathrm{e} ^ {t \partial_ {x x} ^ {2}} & - \kappa \sigma_ {\mathrm{R}} t \int_ {0} ^ {1} \mathrm{e} ^ {t s \partial_ {x x} ^ {2}} \mathrm{e} ^ {- t (1 - s) \kappa} \mathrm{d} s \\ 0 & \mathrm{e} ^ {- t \kappa} \end{array} \right) = \left( \begin{array}{c c} \mathrm{e} ^ {t \partial_ {x x} ^ {2}} & - \kappa \sigma_ {\mathrm{R}} \mathrm{R} (\partial_ {x x} ^ {2} + \kappa) (\mathrm{e} ^ {t \partial_ {x x} ^ {2}} - \mathrm{e} ^ {- t \kappa}) \\ 0 & \mathrm{e} ^ {- t \kappa} \end{array} \right),
$$

and its adjoint, in respect to the $L ^ { 2 } ( [ 0 , L ] ) \times L ^ { 2 } ( [ 0 , L ] )$ scalar product, as

$$
\mathrm{e} ^ {t A ^ {*}} = \mathrm{e} ^ {t A ^ {*}} = \left( \begin{array}{c c} \mathrm{e} ^ {t \partial_ {x x} ^ {2}} & 0 \\ - \kappa \sigma_ {\mathrm{R}}   \mathrm{R} \left(\partial_ {x x} ^ {2} + \kappa\right) \left(\mathrm{e} ^ {t \partial_ {x x} ^ {2}} - \mathrm{e} ^ {- t \kappa}\right) & \mathrm{e} ^ {- t \kappa} \end{array} \right).
$$

Solving (B.1) implies that

$$
V _ {t} ^ {I I} = \sigma_ {\mathrm{R}} \sigma_ {\xi} ^ {2} \operatorname{R} \left(\partial_ {x x} ^ {2} - \kappa\right) \left(- \frac {1}{2} \left(1 + \mathrm{e} ^ {- 2 t \kappa}\right) + \mathrm{e} ^ {t \left(\partial_ {x x} ^ {2} - \kappa\right)} - \kappa \operatorname{R} \left(\partial_ {x x} ^ {2} + \kappa\right) \mathrm{e} ^ {- t \kappa} \left(\mathrm{e} ^ {t \partial_ {x x} ^ {2}} - \mathrm{e} ^ {- t \kappa}\right)\right) Q,
$$

$$
V _ {t} ^ {I I I} = \sigma_ {\mathrm{R}} \sigma_ {\xi} ^ {2} Q \left(- \frac {1}{2} \left(1 + \mathrm{e} ^ {- 2 t \kappa}\right) + \mathrm{e} ^ {t (\partial_ {x x} ^ {2} - \kappa)} - \kappa \mathrm{R} (\partial_ {x x} ^ {2} + \kappa) \mathrm{e} ^ {- t \kappa} \left(\mathrm{e} ^ {t \partial_ {x x} ^ {2}} - \mathrm{e} ^ {- t \kappa}\right)\right) \mathrm{R} (\partial_ {x x} ^ {2} - \kappa),
$$

$$
V _ {t} ^ {I V} = \frac {\sigma_ {\xi} ^ {2}}{2 \kappa} \left(1 - \mathrm{e} ^ {- 2 t \kappa}\right) Q,
$$

and that the equation

$$
\begin{array}{r l} & {\partial_ {x x} ^ {2} V _ {t} ^ {I} + V _ {t} ^ {I} \partial_ {x x} ^ {2} = \sigma_ {\mathrm{R}} ^ {2} \sigma_ {\xi} ^ {2} \Bigg (\kappa \operatorname{R} \left(\partial_ {x x} ^ {2} - \kappa\right) \left(- \frac {1}{2} \left(1 + \mathrm{e} ^ {- 2 t \kappa}\right) + \mathrm{e} ^ {t \left(\partial_ {x x} ^ {2} - \kappa\right)} - \kappa \operatorname{R} \left(\partial_ {x x} ^ {2} + \kappa\right) \mathrm{e} ^ {- t \kappa} \left(\mathrm{e} ^ {t \partial_ {x x} ^ {2}} - \mathrm{e} ^ {- t \kappa}\right)\right) Q} \\ & {\qquad + Q \left(- \frac {1}{2} \left(1 + \mathrm{e} ^ {- 2 t \kappa}\right) + \mathrm{e} ^ {t \left(\partial_ {x x} ^ {2} - \kappa\right)} - \kappa \operatorname{R} \left(\partial_ {x x} ^ {2} + \kappa\right) \mathrm{e} ^ {- t \Kappa} \left(\mathrm{e} ^ {t \partial_ {x x} ^ {2}} - \mathrm{e} ^ {- t \kappa}\right)\right) \kappa \operatorname{R} \left(\partial_ {x x} ^ {2} - \kappa\right)} \end{array}\tag{B.2}
$$

$$
\left. + \left(\mathrm{e} ^ {t \partial_ {x x} ^ {2}} - \kappa \mathrm{R} \left(\partial_ {x x} ^ {2} + \kappa\right) \left(\mathrm{e} ^ {t \partial_ {x x} ^ {2}} - \mathrm{e} ^ {- t \kappa}\right)\right) Q \left(\mathrm{e} ^ {t \partial_ {x x} ^ {2}} - \kappa \mathrm{R} \left(\partial_ {x x} ^ {2} + \kappa\right) \left(\mathrm{e} ^ {t \partial_ {x x} ^ {2}} - \mathrm{e} ^ {- t \kappa}\right)\right) - Q\right)
$$

holds. For $( n _ { 1 } , n _ { 2 } ) \in \mathbb { N } \times$ <sup>N</sup>, we label $\displaystyle p _ { n _ { 1 } , n _ { 2 } } = \langle e _ { n _ { 1 } } , Q e _ { n _ { 2 } } \rangle$ . For $( n _ { 1 } , n _ { 2 } ) \in \mathbb { N } \times \mathbb { N } \setminus ( 0 , 0 )$ , the equation (B.2) implies the definition of $\gamma _ { n _ { 1 } , n _ { 2 } } : = \langle e _ { n _ { 1 } } , V _ { t } ^ { I } e _ { n _ { 2 } } \rangle$ , as described in (4.16) and (4.17). Lastly, the form

$$
V _ {t} = \sigma_ {\xi} ^ {2} \int_ {0} ^ {t} \mathrm{e} ^ {s A} \left( \begin{array}{c c} \sigma_ {\mathrm{R}} ^ {2} Q & \sigma_ {\mathrm{R}} Q \\ \sigma_ {\mathrm{R}} Q & Q \end{array} \right) \mathrm{e} ^ {s A ^ {*}} \mathrm{d} s,
$$

implies the construction of $\gamma _ { 0 , 0 }$ 4

$$
\begin{array}{l}\gamma_ {0, 0} = \left\langle \binom{e _ {0}}{0}, V _ {t} \binom{e _ {0}}{0} \right\rangle_ {L ^ {2} ([ 0, L ]) \times L ^ {2} ([ 0, L ])} = \left\langle e _ {0}, V _ {t} ^ {I} e _ {0} \right\rangle\\\qquad = \sigma_ {\mathrm{R}} ^ {2} \sigma_ {\xi} ^ {2} \int_ {0} ^ {t} \left\langle \right. e _ {0}, \left(\mathrm{e} ^ {s \partial_ {x x} ^ {2}} - \kappa \mathrm{R} (\partial_ {x x} ^ {2} + k) (\mathrm{e} ^ {s \partial_ {x x} ^ {2}} - \mathrm{e} ^ {- s \kappa})\right) Q (\mathrm{e} ^ {s \partial_ {x x} ^ {2}} - \kappa \mathrm{R} (\partial_ {x x} ^ {2} + k) (\mathrm{e} ^ {s \partial_ {x x} ^ {2}} - \mathrm{e} ^ {- s \kappa})\left. \right) e _ {0} \left. \right\rangle \mathrm{d} s\\\qquad = \sigma_ {\mathrm{R}} ^ {2} \sigma_ {\xi} ^ {2} p _ {0, 0} \int_ {0} ^ {t} (1 - (1 - \mathrm{e} ^ {- s \kappa}))   \mathrm{d} s = \sigma_ {\mathrm{R}} ^ {2} \sigma_ {\xi} ^ {2} p _ {0, 0} \frac {1 - \mathrm{e} ^ {- 2 t \kappa}}{2 \kappa}.\end{array}
$$

For these constants $\left\{ \gamma _ { n _ { 1 } , n _ { 2 } } \right\} _ { ( n _ { 1 } , n _ { 2 } ) \in \mathbb { N } \times \mathbb { N } } ,$ we obtain lower bounds of the probability of turbulence initiation as described in Remark 4.9 for $q = q ( x , t )$ , strong solution of (2.1), associated to the choices of $\sigma _ { \mathrm { { I } } } , \sigma _ { \mathrm { { S } } } , \sigma _ { \mathrm { { R } } }$ and F assumed in (4.9).

## Towards Agentic Recommender Systems in the Era of Multimodal Large Language Models

# Towards Agentic Recommender Systems in the Era of Multimodal Large Language Models

Chengkai Huang<sup>1</sup>, Junda Wu<sup>2</sup>, Yu Xia<sup>2</sup>, Zixu Yu<sup>2</sup>, Ruhan Wang<sup>3</sup>, Tong Yu<sup>4</sup>, Ruiyi Zhang<sup>4</sup>, Ryan A. Rossi<sup>4</sup>, Branislav Kveton<sup>4</sup>, Dongruo Zhou<sup>3</sup>, Julian McAuley<sup>2</sup>, Lina Yao<sup>1,5</sup>

<sup>1</sup>University of New South Wales, <sup>2</sup>University of California San Diego, <sup>3</sup>Indiana University, <sup>4</sup>Adobe Research, <sup>5</sup>CSIRO’s Data61

{chengkai.huang1, lina.yao}@unsw.edu.au, {juw069, yux078, ziy040, jmcauley}@ucsd.edu, {ruhwang, dz13}@iu.edu, {tyu,

ruizhang, rrossi, kveton}@adobe.com

## Abstract

Recent breakthroughs in Large Language Models (LLMs) have led to the emergence of agentic AI systems that extend beyond the capabilities of standalone models. By empowering LLMs to perceive external environments, integrate multimodal information, and in teract with various tools, these agentic systems exhibit greater autonomy and adaptability across complex tasks. This evolution brings new opportunities to recommender systems (RS): LLM-based Agentic RS (LLM-ARS) can ofer more interactive, context-aware, and proactive recommendations, potentially reshaping the user experience and broadening the application scope of RS. Despite promising early results, fundamental challenges remain, including how to efectively incorporate external knowledge, balance auton omy with controllability, and evaluate performance in dynamic, multimodal settings. In this perspective paper, we first present a systematic analysis of LLM-ARS: (1) clarifying core concepts and architectures; (2) highlighting how agentic capabilities—such as planning, memory, and multimodal reasoning—can enhance rec ommendation quality; and (3) outlining key research questions in areas such as safety, eficiency, and lifelong personalization. We also discuss open problems and future directions, arguing that LLM-ARS will drive the next wave of RS innovation. Ultimately, we foresee a paradigm shift toward intelligent, autonomous, and collaborative recommendation experiences that more closely align with users’ evolving needs and complex decision-making processes.

## CCS Concepts

• Information systems → Recommender systems.

## Keywords

Large Language Models, Recommender Systems, Intelligent Agent, Generative Recommendation

## 1 Introduction

With the rapid growth of online services, recommender systems (RS) have become essential for addressing users’ information needs and alleviating information overload [47, 92]. These systems provide personalized recommendations across various domains, including e-commerce, movies, music, etc. Despite the diversity of recom mendation tasks such as top-K recommendation and sequential recommendation, the core objective remains consistent: to predict a user’s preferences for each candidate item and generate a ranked list tailored to the user [31].

However, current RSs still face several significant limitations in meeting diverse user needs. First, current RSs typically rely on ID-based features that work only within specific domains or platforms. Their inability to integrate open-domain knowledge, such as common sense reasoning and cross-platform behavioral patterns, significantly constrains their capacity to interpret and model user interests in a broader context. Second, current methods typically optimize well-defined engagement metrics derived from historical interaction data (e.g., click-through rates and purchase histories). Although such methods can be efective for localized objective functions, they often conflate observable behaviors with latent user intent, since implicit feedback mechanisms cannot distinguish transient actions from enduring preferences. Consequently, these models exhibit two major limitations: (i) lack of transparency regarding preference attribution, which impairs interpretability, and (ii) oversimplification of the multifaceted motivations that guide user behavior, especially in scenarios requiring temporal or situational adaptation. As a result, these implicit modeling frameworks fail to capture the causal relationships between dynamic user states and subsequent decision-making processes. Finally, most traditional RSs operate in a largely static, one-directional manner, providing users with minimal opportunities to iteratively refine suggestions through natural language or real-time feedback. This unidirectional flow diverges from established human-computer interaction principles, which emphasize interactive, adaptive dialogue to uncover user preferences. Although conversational RSs have begun to address this issue, they remain limited in their ability to integrate openended natural language understanding with personalized ranking, particularly in scenarios that require multiple rounds of clarification to resolve ambiguous user queries.

Recent advances in Large Language Models (LLMs) and Multimodal LLMs (MLLMs) have greatly improved language comprehension and cognitive processing [24, 39]. With stronger reasoning and planning abilities, (M)LLM-based agents can interpret human language, devise strategies, and execute complex tasks. These breakthroughs ofer new avenues for enhancing RSs’ adaptability, personalization, and user-centricity. The rapid surge in LLM-driven RS research is evident from the 290 references cited in a recent survey on this topic [17, 31, 32], along with numerous influential papers in the field (e.g., [44]). The existing work on applying LLMs to RS, however, has mostly focused on applying LLMs to improve the current RSs. Furthermore, the existing works have underexplored the important question of how LLMs or LLM agents would impact the future of RS in the long run. We argue that LLM-based Agentic Recommender Systems (LLM-ARS) present a promising research direction, ofering new perspectives on autonomy, adaptability, and interactive decision-making in rec ommendation. To unlock the full potential of LLM-ARS, it is crucial to address several open questions, including how to harness agentic capabilities (e.g., planning, collaboration, roleplaying) to improve user modeling and system decision-making, and how to balance autonomy with controllability to ensure safe, transparent interac tions. We ofer a more detailed discussion of these challenges and key research questions in Section 5, where we highlight the most pressing issues and outline possible solutions.

We present the first perspective paper on ARS powered by (M)LLMs. We begin with preliminaries and background on this emerging direction (§2), followed by a discussion on the significance of LLM-ARS (§3) and a formal problem formulation (§4). Next, we analyze LLM-ARS from an agentic perspective (§5) and introduce key research questions from the RS standpoint (§6). To address these questions, we provide in-depth comparisons and discussions, ofering insights into the field (§7 and §8). Finally, we highlight open problems and future opportunities that require further exploration (§9). In summary, our key contributions in this perspective paper are as follows:

• We position LLM-ARS within the broader trajectory of RS development by introducing a four-level evolution, emphasizing the shift from static, one-way recommendation toward agentic paradigms that support autonomy and interactive decisionmaking.

• We propose a formal task formulation for LLM-ARS, detailing the core components—user profiling, planning, memory, and action—that together enable continuous adaptation and proactive recommendations.

• We identify critical research questions and open problems of how to harness agentic capabilities (e.g., planning, roleplaying, collab oration) to improve user modeling, system decision-making, and overall recommendation efectiveness.

## 2 Preliminary and Background

The rapid evolution of LLM-based AI has spurred significant advancements in Agent AI, fundamentally reshaping how systems interact with complex environments. In recent years, researchers have equipped LLM agents with core components—memory, plan ning, reasoning, tool utilization, and action execution—that are essential for autonomous decision-making and dynamic interaction [9]. The following subsections together with Figure 1 provide an overview of the recent developments in both single-agent and multi-agent frameworks.

## 2.1 LLM-based Single-Agent Systems

Single-agent systems leverage a unified model that integrates multiple interdependent modules.<sup>12</sup> The memory component acts as a structured repository that stores and retrieves contextually relevant information, such as user preferences and historical interactions [93]. This persistent memory is crucial for maintaining coherent, long-term interactions and forms the foundation for personalization in recommendation settings. The planning module is closely linked with advanced reasoning capabilities. Recent research has identified approaches such as task decomposition, multi-plan selection, external module-aided planning, reflection and refinement, and memory-augmented planning [21]. These techniques enable an agent to break down complex tasks, select and refine strategies based on evolving contexts, and leverage external knowledge sources. Integrated reasoning further enhances decision-making by allowing the system to adapt dynamically to novel scenarios. Frameworks like ReAct [80] and Reflexion [52] exemplify how interleaving reasoning with concrete actions—such as web-browsing or tool invocation—can significantly improve system robustness and adaptability. Beyond internal cognitive processes, these agents increasingly rely on tool utilization to interface with external data and services. Systems like WebGPT [37] illustrate the efectiveness of using external modules (e.g., web search engines) to retrieve real-time information. Other works, such as Retroformer [81] and AvaTaR [75], further optimize these interactions through policy gradient optimization and contrastive reasoning, respectively, to fine-tune tool usage and enhance performance over time.

## 2.2 LLM-based Multi-Agent Systems

In contrast, LLM-based multi-agent systems emphasize collaboration among diverse autonomous agents. These systems are designed to mimic complex human workflows by facilitating inter-agent communication, task specialization, and coordinated decision-making. Frameworks such as CAMEL [28] and AutoGen [74] demonstrate how agents with distinct roles can interact to solve problems more eficiently than a single, monolithic agent. By assigning specialized functions—ranging from ideation and planning to evaluation—these frameworks enable a division of labor that enhances overall system capability and flexibility. Further advancements are seen in approaches like MetaGPT [15] and AgentLite [34], which incorporate meta-programming techniques and lightweight libraries to dynamically allocate roles and coordinate complex workflows. These structured interactions not only improve task eficiency but also ofer robustness in dynamic problem-solving environments. Recent developments also include systems such as ChatEval [2] and ChatDev [41], which leverage inter-agent debate and evaluative feedback to produce more nuanced and reliable outputs. This human-like discussion among agents is particularly beneficial in open-ended natural language generation tasks and complex software development processes.

## 3 Why Agentic Recommender Systems Now?

Recent advances in RSs have largely focused on enhancing interaction capabilities, with most research eforts still operating at the Advanced RSs (Level 1) and Intelligent RSs (Level 2) stages as shown in Table 1. However, they remain fundamentally reactive, relying on predefined model architectures and user-driven feedback loops. The next frontier, Agentic RSs (Level 3), aims to move beyond reactive engagement to autonomous, adaptive, and proactive recommendation strategies, which is increasingly feasible due to recent breakthroughs in (M)LLMs. We identify three key factors:

![](images/09665ea4810229872155105defd9ae6dc7692f9992f84329e4f757062961d09e.jpg)  
Figure 1: The rising trend in the research field of LLM-based Agents. We categorize current work into single-agent and multi agent categories.

• Leveraging (M)LLMs for Recommendation: The integration of LLMs introduces agent-like capabilities such as planning, memory retention, and in-context learning, enabling adaptive and evolving recommendation strategies. Unlike traditional systems that require explicit re-training, LLM-based agents can dynami cally refine recommendations based on sequential user interactions and external contextual cues. Additionally, collaborative multi-agent systems can further enhance recommendations by enabling multiple AI agents to exchange information, reason collectively, and optimize decision-making.

• Expanding Information Modalities: RSs primarily rely on ID-based and textual information, limiting their ability to fully understand user preferences. In contrast, multi-modal agentic systems can process diverse input signals, including images, au dio, structured metadata, and behavioural cues, leading to richer and more context-aware recommendations. Thus, agentic sys tems can capture holistic user intent, bridging the gap between implicit and explicit preference signals.

• Evolving User Interfaces: From Passive to Proactive Recommendation: Traditional recommendation paradigms primarily function as passive systems, responding to user queries with static suggestions. Conversational recommenders improve engagement but still rely on user-initiated interactions. Agentic systems introduce a proactive user experience, where AI-powered multi-modal agents continuously adapt, predict user needs, and autonomously refine recommendations before explicit queries occur. This shift not only enhances user satisfaction but also opens the door for highly personalized, real-time, and contextually aware recommender systems.

Given these advancements, the evolution towards multi-modal LLM-driven agentic recommenders represents a promising and inevitable trajectory. These systems combine autonomy, adaptability, and multi-modal intelligence, paving the way for self-improving, memory-driven, and highly personalized recommendation experiences that surpass the capabilities of existing models.

## 4 Formulation

An Agentic Recommender System [86, 90] is a system in which agents autonomously generate personalized recommendations by interacting with users and adapting to their preferences over time. Formally, it can be defined as a tuple (<sup>??</sup> <sup>,</sup> <sup>??,</sup> <sup>??,</sup> <sup>??,</sup> <sup>??</sup>), where <sup>??</sup> is the set of users, <sup>??</sup> is the set of items, <sup>??</sup> is the set of agents, <sup>??</sup> is the set of environmental contexts and $R : U \times E \times A \to P ( I )$ is the recommendation function that maps users, contexts, and agents to a probability distribution over items <sup>??</sup> (<sup>??</sup> ). Each agent $a \in A$ operates autonomously by perceiving the state $s = f ( u , e )$ , making decisions based on its policy $\pi _ { a } ( s )$ , and learning from user feedback to optimize an objective function, maximizing expected user utility:

<table><tr><td>Level</td><td>Name</td><td>Description</td><td>Key Characteristics</td></tr><tr><td>0</td><td>Traditional Recommender Systems</td><td>Systems rely on static algorithms and historical data to suggest items.</td><td>• Rule-Based Processing: Uses fixed rules, collaborative filtering, or content-based methods. • Limited Contextual Understanding: Operates solely on past user behavior without real-time adjustments. • One-Way Interaction: Provides recommendations in a non-interactive, one-off manner.</td></tr><tr><td>1</td><td>Advanced Recommender Systems</td><td>Deep learning advances enhance personalization with historical and real-time data.</td><td>• Data-Driven Adaptation: Uses learning models to update recommendations based on new information. • Feedback Integration: Incorporates user feedback to refine suggestions over time. • Enhanced Personalization: Provides more accurate and context-aware recommendations while following predefined model structures.</td></tr><tr><td>2</td><td>Intelligent Recommender Systems</td><td>These systems actively engage users to refine their understanding of preferences.</td><td>• Interactive Engagement: Initiates clarifying dialogues and solicits additional input. • Multi-Modal Input Processing: Integrates inputs beyond text (e.g., images, behavioral signals). • Dynamic Adaptation: Adjusts recommendations in real-time based on user context.</td></tr><tr><td>3</td><td>Agentic Recommender Systems</td><td>Fully autonomous agents that not only provide recommendations but also self-improve and evolve.</td><td>• Autonomous Decision-Making: Uses planning and optimization to proactively shape recommendation strategies. • Continuous Self-Evolution: Updates models and behaviors based on internal and external feedback. • Comprehensive Memory &amp; Multi-Modal Perception: Integrates long-term user data, contextual cues, and multiple input types. • Proactive and Reactive Interactions: Balances immediate responses with strategic actions.</td></tr></table>

Table 1: Four-Level Evolution of Recommender Systems: In this study, we categorize RSs into four levels based on their adaptability and interaction capabilities. Traditional RSs rely on static algorithms and historical data, while advanced RSs leverage deep learning for real-time personalization. Intelligent RSs engage users interactively, and agentic RSs autonomously evolve and optimize recommendations.

$$
\max _ {\pi_ {a}} \mathbb {E} \left[ U (u, R (u, e, a)) \mid \pi_ {a} \right].\tag{1}
$$

The key characteristics of such a system include autonomy, adaptability, and enabling agents to provide dynamic and personalized recommendations through continuous learning and user engagement. To illustrate our formulation of the architecture of agentic recommender systems, we present the notation table in Table 2.

## 4.1 The User Profiling module:

The User Profiling Module is dedicated to constructing comprehen sive profiles, such as behaviours for each user. The function can be define as $P : U \times T  S$ , where $P ( u , t )$ represents the evolving profile of user <sup>??</sup> at time <sup>??</sup>. This profile is dynamically updated based on historical interactions $H ( u , t )$ , contextual features $C ( u , t )$ , and external signals $X ( u , t )$ , modeled as:

$$
P (u, t) = f (H (u, t), C (u, t), X (u, t); \theta_ {P}).\tag{2}
$$

To adapt to new user behaviours, profile updates incrementally as:

$$
P (u, t + 1) = P (u, t) + \eta \cdot \Delta P (u, t),\tag{3}
$$

where $\Delta P ( u , t )$ represents changes based on recent interactions, and <sup>??</sup> controls the update rate.

The user profiling module employs machine learning techniques to adaptively refine user profiles over time. It synthesizes infor mation from diverse sources and external contextual signals, to create a multidimensional view of the user’s preferences. For in stance, RecAgent [60] utilizes large language model-based agents to simulate user behavior and refine profiling accuracy. Addition ally, Rec4Agentverse [88] leverages large language model-based agents for prospect personalized recommendations, allowing for finer-grained user representations.

In contemporary practice, profiling modules also leverage MLLMs to process unstructured data modalities, such as textual reviews and visual preferences. MACRec [69] explores multi-agent collaboration frameworks to enhance user profiling through cooperative agent learning, ensuring robust profile evolution over time. Meanwhile, AgentCF [90] integrates autonomous learning language agents to collaboratively refine user profiles, reinforcing adaptive personalization. By maintaining both static and dynamic aspects of user preferences, this module ensures the recommendations are contextually appropriate, significantly enhancing user satisfaction in the system. The integration of reinforcement learning frameworks like SUBER [6] helps model long-term user behaviors by simulating future interactions to predict evolving preferences.

## 4.2 The Planing module:

The Planning Module empowers agents to formulate strategic decisions regarding which items to recommend. Using the user profiles from the User Profiling Module and considering the current environmental context $e \in E ,$ the module is defined as:

$$
s = f (u, e),\tag{4}
$$

where $f : U \times E \to S$ maps users and contexts to a state space S. for each user-agent pair. This module functions as the core of the decision-making of the Agentic Recommender System, the Planning Module leverages advanced optimization techniques, such as Markov Decision Processes (MDPs) and reinforcement learning, to ensure that decisions are both rational and aligned with user objectives. Similar approaches have been explored in recent research on RSs, such as MACRec [61] for multi-agent collaboration and Agent4Rec [86], which introduces generative agents for recommendation. In scenarios where user preferences conflict with immediate contextual constraints, the module employs multi-objective optimization to balance trade-ofs efectively, similar to approaches used in BiLLP [51], which frames recommendation as a long-term planning problem.

<table><tr><td>Symbol</td><td>Description</td></tr><tr><td>U, I, A, E</td><td>Users, items, agents, environments</td></tr><tr><td>R: U × E × A → P(I)</td><td>Recommendation function</td></tr><tr><td>s = f(u, e)</td><td>User state representation</td></tr><tr><td>πa(s)</td><td>Agent policy</td></tr><tr><td>P(I)</td><td>Item distribution</td></tr><tr><td>H(u, t)</td><td>User interaction history</td></tr><tr><td>C(u, t)</td><td>Contextual factors</td></tr><tr><td>X(u, t)</td><td>External signals</td></tr><tr><td>P(u, t)</td><td>User profile</td></tr><tr><td>M(u, t)</td><td>Memory function</td></tr><tr><td>A(s, a)</td><td>Action selection function</td></tr></table>

Table 2: Summary of notations used in agent-based RSs.

By simulating potential sequences of recommendations and user responses, the module can adjust strategies to minimize risks, predictive modeling is also emphasized in RecMind [68], which integrates LLMs into sequential recommendation. Additionally, it can incorporate collaborative and competitive dynamics among agents, allowing for coordinated actions in multi-agent systems [11] or personalized prioritization in single-agent setups [90].

The Planning Module also enables hierarchical planning and ensures that each sub-recommendation aligns with the overall ob jective, creating a coherent and seamless user experience. Recent ad vancements in AI-driven recommendation, such as AutoConcierge [83], which focuses on interactive goal-based recommendations, supports this hierarchical approach to structured decision-making.

## 4.3 The Memory module:

The Memory Module functions as a dynamic storage system that retains historical data on user interactions and feedback. It serves as a critical component for enabling the Agentic Recommender System to build continuity and context awareness over time. Formally, it maintains a memory function <sup>??</sup> : $U \times T \to M ,$ where:

$$
M (u, t) = g (H (u, t), C (u, t); \theta_ {M}),\tag{5}
$$

By storing and retrieving historical data, this module ensuring that future recommendations are informed by accumulated insights. Systems such as RecMind [67] leverage LLMs for memory-driven recommendations, enhancing continuity in RSs.

The Memory Module is designed to support both short-term and long-term memory functionalities. Short-term memory stores recent interactions, enabling the system to adapt to immediate user needs and preferences. In contrast, long-term memory archives broader behavioural patterns, which are crucial for understanding shifts in user behaviour over time. Together, these memory layers create a holistic view of the user, balancing transient interests with persistent inclinations. Similar architectures are explored in SUBER [6], an RL-based framework that simulates human behaviour for adaptive recommendation learning. To manage large-scale data efectively, the Memory Module employs advanced data structuring techniques to utilizes eficient retrieval, often powered by neural attention models, to access relevant historical data in real-time. This capability is similar to BiLLP [51], which positions LLMs as learnable planners to enhance long-term recommendation strategies. An essential feature of the Memory Module is its ability to integrate cross-session data. Systems like AgentCF [90] incorporate collaborative learning mechanisms, enabling memory-enhanced interactions among language agents in multi-agent recommendation.

## 4.4 The Action module:

The Action Module is responsible for executing the decisions made by the Planning Module, dynamically selecting and delivering recommendations to users. Given a user <sup>??</sup> ∈ <sup>??</sup> , an agent $a \in A$ , and an environmental state $e \in E ,$ , the system defines an action selection function A : $S \times A \to P ( I )$ , where:

$$
\mathcal {A} (s, a) = \pi_ {a} (s),\tag{6}
$$

where $\pi _ { a } ( s )$ represents the agent’s policy for selecting a probability distribution over items $P ( I ) _ { \mathit { i } }$ , given the current state $s = f ( u , e )$ Modern recommender systems increasingly integrate agentic approaches that allow for interactive decision-making. For instance, Agent4Rec [86] introduces generative agents that enable personalized through reinforcement learning. Similarly, RecAgent [60] uses a simulation of user behaviour with agents based on large language models to refine recommendation strategies.

Multi-agent frameworks have been explored to facilitate collaboration and competition in recommendation settings. MACRec [69] demonstrates the potential of multi-agent collaboration frameworks for improving recommendation diversity and accuracy. Moreover, MACRS [11] expands on this by introducing multi-agent conversational recommender systems that coordinate interactions across multiple agents to optimize recommendations in real-time. Conversational RSs play a crucial role in the Action Module by enabling context-aware responses. RecLLM [12] and CSHI [99] focus on leveraging large language models to enhance conversational interactions, providing scalable and controllable user simulations. RecMind [67] employs large language models to power agent-based recommendations, ensuring responses are aligned with evolving user intents. LLM4Rerank [13] further enhances recommendation efectiveness through re-ranking mechanisms optimized by LLMs.

A novel direction is tool-augmented recommendations $( e . g .$ , Tool-Rec [97]), which leverages tool learning to enhance recommendation accuracy and usability. Similarly, RAH [54] presents a humancentered framework that balances LLM-powered recommendations with human oversight improving user satisfaction.

## 5 Key Research Questions in LLM-ARS

After formulating an agentic recommender system and examining its key components, the next step is to address fundamental challenges in integrating LLM-driven agentic capabilities. These challenges span reasoning, user modeling, multimodal fusion, lifelong personalization, decision-making frameworks, controllability, and so on. To systematically analyze these challenges and explore novel solutions, we structure our discussion around the following key research questions (RQs).

RQ1: How can LLM-based agents benefit recommender systems through reasoning, planning, and collaboration?

RQ2: How can agentic recommender systems efectively lever age (M)LLM to improve user understanding and decision-making?

RQ3: What novel architectures or learning paradigms are needed to enable agentic RSs?

RQ4: What are the key challenges in integrating agentic decision making and multimodal reasoning into RSs?

RQ5: How can we evaluate the efectiveness and robustness of agentic recommender systems powered by multimodal LLMs?

RQ6: How can agentic recommender systems balance autonomy and controllability while utilizing MLLMs?

RQ7: How can agentic recommender systems achieve life-long personalization while mitigating catastrophic forgetting?

## 6 LLM-based Agentic Reasoning, Planning, and Collaboration (RQ1)

In this section, we explore how LLM agents face challenges in long-term planning and reasoning over personalized contexts and feedback (RQ1). Unlike conventional recommendation methods that learn from historical data to capture statistical patterns of user behavior [46, 49, 63], LLM agents analyze the contextual informa tion of items and the semantic details of user-item interactions [73, 90]. They further plan proactive strategies to explore longterm preferences using chain-of-thought generation [66, 73, 95]. However, as general-purpose models, LLMs find it challenging to adapt to personalized contexts or user feedback. To simulate di verse personalities, LLM agents roleplay via prompting [90] and user modelling [94], and they self-improve in interactive settings through multi-agent alignment [58, 59, 73].

## 6.1 Planning and Reasoning in Agentic RS

LLM agent planning in recommender systems leverages the com plex reasoning and decision-making capabilities of large language models to decompose the recommendation process into subtasks and assign them to multiple agents for collaboration across agents. To manage complex recommendation tasks, Wang et al. [69] and Fang et al. [11] propose multi-agent frameworks that decompose the overall task into specialized roles, while Wang et al. [69] in troduces agentic protocols including Manager, User/Item Analyst, Reflector, Searcher, and Task Interpreter. Fang et al. [11] focuses on goal-oriented dialogue planning and incorporates a user feedback aware reflection mechanism to control the conversation flow. To mitigate issues such as hallucinations and misalignment between semantics and behaviours, Zhao et al. [98] employs tool learning with surrogate users and attribute-oriented tools (i.e., rank and retrieval tools), while [27] integrates external knowledge and goal guidance to better reasoning grounding and proactive responses. To further enable exploration in planning Wang et al. [59] develops LLM-driven policy exploration by pre-training policies with user preference distillation for deploying adaptive fine-tuning strategies.

LLM agent equips recommender systems with the reasoning capabilities of large language models to discover complex user-item relationships and generate interpretable and semantically meaning ful recommendations. By further integrating structured external knowledge, distilled rationales, and memory mechanisms, LLMbased agentic frames are enabled with more contextually grounded reasoning while understanding various personalized behaviours and preferences in recommendation tasks. To uncover complex user-item relationships, Guo et al. [14] leverages knowledge graphs to inject explicit relational paths into language agents, while Wang et al. [66] distils underlying rationales from user reviews to enrich user profiles and item contexts, which improves LLM agents’ understanding of complex user-item interactions. To further understand the sequential context and user behaviours in conversational recommendations, Xi et al. [77] introduces memory-enhanced LLMs to track historical dialogue beliefs, improving on the approaches that only consider current interactions. To ensure explanations are both persuasive and credible, Qin et al. [43] develops a credibility-aware strategy that refines outputs through self-reflection. Focusing on the alignment of LLM reasoning with recommendation logic, Zhao et al. [95] proposes a non-tuning logic alignment framework using semantic embeddings and chain-of-thought prompting, whereas Wu et al. [73] augments LLMs with collaborative retrieval to ground reasoning in user-item interaction patterns.

Despite promising advances in LLM agents for planning and reasoning in recommender systems, current approaches face notable challenges. Methods dependent on explicit external structures—such as knowledge graphs [14] or curated rationales [66] are limited in generalizability across various scenarios. Although techniques in [77] and [43] improve sequential reasoning and explanation credibility, and [95] and [73] enhance logic alignment and collaborative retrieval, an integrated framework that aligns multiagent reinforcement learning and planning with user behaviour modelling [59, 69] is still lacking.

## 6.2 LLM-Agent Roleplaying in User Modeling

The exploration of LLM-agent roleplaying techniques is demanding for realistic user modelling in recommender systems, where user agents or simulators emulate human-like behaviours to capture both explicit and implicit user preferences. Intuitively, these methods leverage roleplay to bridge the gap between language understanding and behaviour simulation, enabling more realistic multi-agent interactions for personalized preference alignment and more rigorous evaluation. One prominent challenge is simulating socially dynamic user-item interactions inherent in human behaviour. Zhang et al. [89] tackles this by simulating a collaborative learning environment where both users and items are modelled as autonomous roleplaying agents, thus enabling bidirectional interaction and reflective adjustment. In addition, Wang et al. [62] introduces a sandbox environment where roleplaying agents are equipped with profile, memory, and action modules that interact through one-to-one and broadcast communications, efectively modelling social influence and conformity. In contrast, Zhang et al. [94] emphasizes explicit user modelling by integrating logical reasoning with statistical insights to simulate user engagement.

Addressing the need for controllability and scalability in conversational settings, Zhu et al. [99] proposes a framework that utilizes roleplay to customize user simulations in real time, enhancing the fidelity of user modelling in conversational recommender systems. Additionally, to overcome limitations related to data scarcity and evaluation reliability, [5] and [10] construct synthetic environments using LLMs as roleplaying users, while [26] introduces a target-free roleplay strategy to avoid bias in preference elicitation. However, current LLM-agent roleplaying approaches in user modelling still struggle with the interpretability of simulation processes and capturing the complexity of human decision-making. Future research should focus on developing more interpretable roleplay strategies and integrating richer, multimodal behavioural data to further en hance the adaptability and realism of user modeling frameworks.

## 6.3 Interaction Between Agents and Users

LLM-based agentic recommendation systems have motivated exploring methods that enhance the realistic interaction between agents and users. Intuitively, these approaches leverage agent role playing and collaborative mechanisms to bridge the gap between language understanding and complex behavioural interactions. One of the major challenges is simulating realistic user-agent interactions by capturing both explicit semantic and implicit behaviour signals. Zhang et al. [89] addresses this by modelling non-verbal signals (e.g., item clicking) via collaborative learning between user and item agents, in contrast to dialogue-centric approaches such as [11]. Kim et al. [26] further emphasizes a target-free user simulation protocol that avoids the target bias in such interactions.

Another challenge lies in integrating task-specific recommendation dynamics with interactive capabilities. While Huang et al. [19] leverages LLMs as a central controller augmented by recommendation models to enable seamless interaction, Wang et al. [65] focuses on enhancing high-order interaction awareness through whole-word embedding techniques. In multi-agent systems, col laboration in achieving efective interaction is proposed by [69], which designs specialized agents for various subtasks, whereas [11] suggests feedback-aware reflection for controlled dialogue flow. However, existing works still fall short in robustly modelling the dynamic evolution and collaborative evolution of extended agent user interaction, fully integrating adaptive feedback mechanisms. Future research should explore strategies for multi-agent planning and reasoning to align dynamic user-item interaction.

## 6.4 Agent Self-improvement

Finally, we discuss how agents can further evolve and self-improve in a recommendation environment by continuously incorporating rich interaction signals. Leveraging large language models (LLMs) to simulate and distil these interactions, recent approaches aim to bridge the gap between static ofline training and evolving online deployment. Synthesizing efective feedback from sparse data can significantly scale up the ofline training of LLM agents. Wu et al. [73] integrates collaborative information to enrich the interaction context, in addition to the approach [58] that directly generates feedback via LLM capabilities. Addressing the challenge of distribu tion shift and limited exploration in ofline reinforcement learning, Wang et al. [59] introduces an Interaction-Augmented Learned Pol icy (iALP) that pre-trains policies with distilled user interaction data augmented by LLMs, while Wang et al. [58] employs an LLM as an environment to verbally model states and rewards from real interaction feedback. Meanwhile, in the domain of adaptive agent selection, [40] leverages sentence embeddings aligned with hu man feedback to recommend the most appropriate agent based on interactive prompting, ensuring adaptability in dynamic settings. Confronting the need for explainability in self-improvement, [95] proposes a logic alignment strategy that enables LLM reasoning in online systems, providing interpretable recommendations grounded in explicit interaction semantics. However, current methods are still limited in the reliance on synthetic or simulated interaction data, which may not fully capture the complexities of real-world environments. In addition, the sim-to-real gap can be additionally challenging, which requires robust ofline policy evaluation, and smart online adaptation strategies.

## 7 LLM Agents for Enhanced User Understanding and Decision-Making (RQ2)

From the perspective of the RS field, LLM-powered autonomous agent systems position LLMs as the core "brain" of the agent, supported by essential components such as planning, memory, and tool utilization [72]. Prominent works like AutoGPT and BabyAGI have demonstrated the immense potential of LLM-based agents, particularly in their ability to store past experiences and leverage them to make more informed decisions (RQ2). In RS scenarios, these agents are often conceptualized as user simulators or the RS itself, as illustrated in Figure 2.

## 7.1 User Simulation in LLM-ARS

Simulating user behaviors is essential for training large-scale RSs, given the challenges of data scarcity, ethical concerns, and coldstart issues in real-world interaction data. Traditional methods [23, 100] struggle to model complex and evolving user behaviors, while recent advances in LLMs provide a promising alternative by enabling more adaptive and realistic simulations.

Most works leverage LLM-powered personalized agents to emulate user interactions. RecAgent [60] treats each user as an autonomous agent capable of interacting freely within a simulated environment, capturing both conventional RS behaviors such as browsing and clicking, as well as external influences like social interactions. Extending this idea, Agent4Rec [86] simulates 1,000 generative agents in a movie RS, where users engage with recommendations in a page-by-page manner, taking diverse actions that better approximate real-world decision-making. Beyond individual user agents, collaborative simulation frameworks have emerged to model multi-agent dynamics. LLM-InS [18] predicts user interactions with cold-start items, simulating clicks from a subset of recalled users to generate synthetic interactions that update item embeddings. Zhang et al. [94] integrate LLM-based logical reasoning with statistical modeling, extracting user preferences from item characteristics and engagement history to improve the fidelity of simulated behaviors. AgentCF [90] extends the paradigm by treating both users and items as interactive agents, fostering a coevolutionary learning process that optimizes user-item interactions. USimAgent [87] focuses on search behavior simulation, capturing querying, clicking, and stopping behaviors to generate realistic search task interactions. BASES [45] scales this concept further, utilizing LLM-based agents to create large-scale user profiles and diverse search behaviors across multiple linguistic benchmarks.

Despite advancements, LLM-driven simulators face critical limitations. Many rely on predefined heuristics or scripted rules, failing to capture emergent or long-term behavioral patterns. While LLMs approximate user preferences, they lack the ability to model cognitive biases, evolving interests, or contextual decision-making shifts. Scalability is also a concern: synthetic interactions can be generated at scale, but their real-world validity remains uncertain, and over-reliance on simulated data risks introducing biases. Future work should focus on adaptive, feedback-driven frameworks that integrate real-world behavioral signals, refine user modeling be yond static preferences, and establish validation mechanisms for LLM-generated interactions in RS applications.

![](images/172a634fe8d6fb7bd1911042d206d81c6233d1fc2a6dcc634c98cdf8f16b7a64.jpg)  
Figure 2: Diferent types of personalized LLM-based agents in LLM-ARS, where (i) LLM-Agent simulates user behavior, (ii) LLM-Agent acts as a recommender, and (iii) LLM-Agent functions as both user simulation and recommender.

## 7.2 Improving Personalized Recommendations with LLM-driven Decision-Making

Leveraging the advanced reasoning, reflection, and tool-usage capabilities of LLM agents, recent approaches explore their role as decision-making agents to enhance personalized recommendations. Unlike level 0-2 RS models, LLM-ARSs dynamically adapt to user needs by integrating planning, self-reflection, and external tool interactions. The RAH framework [53], incorporating LLM-based agents and a Learn-Act-Critic loop, improve alignment with user personalities and mitigate biases. Then, Wang et al. [67] first introduces a Self-Inspiring planning algorithm that keeps track of all past steps of the agent to help generate new states. At each step, the agent looks back at all the paths it has taken before to figure out what to do next. This approach aids in employing databases, search engines, and summarization tools, combined with user data, for producing tailored recommendations. InteRecAgent [20] model the LLMs as the brain, while recommendation models serve as tools that supply domain-specific knowledge, then LLMs can parse user intent and generate responses. They specify a core set of tools essential for RS tasks—Information Query, Item Retrieval, and Item Ranking—and introduce a candidate memory bus, allowing previous tools to access and modify the pool of item candidates.

However, key challenges remain, such as ensuring long-term consistency in recommendations, balancing LLM-ARS generalization with domain-specific accuracy, and mitigating potential biases intro duced by LLM-generated reasoning. Future research should focus on integrating user feedback loops, enhancing interpretability, and optimizing the eficiency of tool-augmented LLM decision-making to fully realize the potential of LLM-ARS.

## 8 Framework and Learning Paradigms (RQ3)

To enable LLM-ARS, novel frameworks and learning paradigms are required to enhance autonomy, adaptability, and human alignment (RQ3). We categorize these advancements into three key areas: single-agent architectures, which focus on individual agents as decision-makers; multi-agent collaboration, which leverages interactions among multiple agents to improve reasoning and adaptability; and human-LLM hybrid architectures, which emphasize collaboration between human users and LLM-based agents to refine personalization, control, and interpretability in recommendations.

Single-Agent Framework for RS: LLM-powered single-agent frameworks enable autonomous decision-making in RSs by integrating reasoning, memory, and planning. The RAH framework [53] employs a Learn-Act-Critic loop to iteratively refine recommendations, improving personalization and reducing bias. Wang et al. [67] introduce Self-Inspiring Planning, where an LLM agent retrospectively analyzes past decisions to optimize future choices while leveraging external tools like search engines and summarization models. InteRecAgent [20] further enhances this paradigm by treating LLMs as decision-making cores, selectively invoking domain-specific tools (e.g., retrieval and ranking modules) and maintaining long-term candidate memory for adaptive ranking. These architectures transform LLMs from passive generators into adaptive decision-makers, enabling more context-aware, interactive recommendations. However, they face scalability challenges and lack collaborative reasoning in multi-domain scenarios.

Multi-Agent Framework for RS Multi-agent frameworks extend single-agent frameworks by incorporating specialized agents that communicate and collaborate to enhance decision-making. Instead of relying on a single agent for all tasks, these frameworks assign distinct roles to diferent agents, enabling parallelized reason ing, task specialization, and self-organizing interactions. Wang et al. [70] propose MACRec, where agents such as a Manager, Analyst, and Reflector collaborate on tasks like rating prediction, sequential recommendation, and explanation generation, improving adaptability and interpretability. PUMA [1] further integrates a shared memory system, allowing agents to retrieve past interactions for enhanced personalization. Compared to single-agent models, multiagent frameworks ofer better scalability, modularity, and reasoning eficiency, yet face challenges in coordination, redundancy reduction, and consistency maintenance across interacting agents.

Human-LLM Hybrid Framework for RS: While LLM-powered agents enhance automation, human-in-the-loop architectures are crucial for improving interpretability and fairness in RSs. Recent works explore collaborative frameworks where user feedback guides LLM-driven reasoning, ensuring transparency and control. Shu et al. [55] propose the LLM-powered assistant mediates between users and RSs. Using a Learn-Act-Critic loop with built-in reflection, the assistant refines recommendations by resolving preference in consistencies. It also incorporates privacy-preserving mechanisms, allowing users to filter content and adjust recommendations dy namically. Beyond direct interaction, hybrid frameworks embed user intent into LLM-based reasoning. Ning et al. [38] integrate user embeddings with LLMs via a pretrained encoder and crossattention, capturing long-term preferences more efectively. Shao et al. [50] further bridge the semantic gap between LLM reasoning and structured user data through vector quantization and prefer ence alignment. To formalize design principles for human-centered agentic RSs, Deng et al. [7] introduce a taxonomy spanning Intel ligence, Adaptivity, and Civility, providing guidelines to develop ethically adaptive, user-aligned conversational recommenders.

In summary, single-agent systems enable autonomous reasoning and memory integration, while multi-agent architectures enhance collaboration and modularity. Human-LLM hybrids further improve interpretability and personalization. Key challenges include balanc ing autonomy with user control, optimizing coordination, and miti gating biases while ensuring generalization. Future research should develop adaptive architectures that unify reasoning, collaboration, and user alignment for fully interactive, context-aware systems.

## 9 Open Problems and Opportunities

## 9.1 Multimodal Reasoning in LLM-ARS (RQ4)

In this section, we investigate key challenges in integrating agentic decision-making and multimodal reasoning into RSs (RQ4).

Multimodal Fusion: Multimodal fusion is crucial for agentic RSs integrating multiple LLMs and tools, yet it remains challeng ing. Potential strategies include encoder-decoder, attention, GNN, and generative neural network (GenNN)-based fusion. Encoder decoder models unify multimodal features in a shared space for task-specific decoding [25, 56], while attention-based fusion en hances cross-modal dependencies [35, 76]. GNN-based approaches jointly model structured and unstructured data [42, 57], and GenNN based fusion synthesizes modalities while handling missing data [48]. Efective fusion strengthens reasoning and factual grounding, ensuring robust decision-making in LLM-ARS.

Multimodal Reasoning: Aligning (M)LLM commonsense reasoning with recommendation tasks remains a key challenge. While (M)LLMs excel in open-domain reasoning, they often lack the task specific adaptability needed for user preference modeling and sequential decision-making. Their reasoning is optimized for general understanding rather than multimodal user intent inference, leading to inconsistencies in recommendation relevance. Addressing this requires fine-tuning with domain-specific constraints, integrating structured knowledge, and optimizing reasoning for personalized decision-making in multimodal contexts.

Eficiency: Eficiency remains a critical challenge for LLM-ARS, especially as they orchestrate multiple specialized tools or models.

Current RSs often incur significant computational overhead when integrating LLMs with external APIs for multimodal tasks, leading to latency issues. Optimizing the agent pipeline for speed and resource utilization while maintaining accuracy is essential. Promising directions include developing lightweight agents, reducing redundant computations through shared intermediate outputs, and exploring model compression techniques for LLMs within agents.

## 9.2 Benchmarking of LLM-ARS (RQ5)

Benchmarking LLM-ARS presents unique challenges beyond established metrics for LLMs and standalone RSs (RQ5). Comprehensive frameworks like AgentBench [33] are essential for assessing multiturn interaction quality, cross-modal efectiveness, and adaptability to user feedback. Efective evaluation demands standardized datasets and protocols that capture real-world complexity, including dynamic personalization and multimodal workflows. Robust assessment should integrate qualitative insights with quantitative metrics, measuring coherence, responsiveness, and contextual relevance under evolving conditions. Stress-testing adaptability to emergent feedback ensures sustained performance. Developing realistic simulation environments aligned with real-world use cases will enhance benchmarking transparency and drive iterative improvements in ARS.

## 9.3 Balancing Autonomy and Controllability in LLM-ARS (RQ6)

Ensuring a balance between autonomy and controllability in LLM-ARS requires addressing key challenges such as hallucination, explainability, and safety (RQ6). While agentic RSs benefit from LLMs’ ability to generate flexible and adaptive recommendations, uncontrolled generation can lead to unrealistic, irrelevant, or even harmful recommendations. Below, we discuss how these challenges manifest in RS scenarios and the strategies to mitigate them.

Hallucination: Hallucination in LLM-ARSs commonly occurs when generated items fall outside the valid item pool (OOV items) or when the model fabricates user preferences inconsistent with real behavior. This issue arises from LLMs’ open-ended generative nature. This issue arises because LLMs, unlike retrieval-based RSs, do not inherently constrain outputs to an existing catalog. For instance, an LLM might recommend an out-of-vocabulary (OOV) item that does not exist in the system’s database, generate unrealistic item-attribute pairings in multimodal RSs, or infer user interests based on semantic associations rather than actual interactions. Such errors are especially problematic in domains like e-commerce, where recommending unavailable products could degrade user trust. To mitigate hallucination, several strategies have been proposed. Database-grounded generation techniques ensure that LLMs reference an external item pool before finalizing recommendations [96]. Reflective instruction tuning helps refine constraints on generation [91], while hallucination detection frameworks flag outputs that lack factual grounding [82]. At inference time, methods such as adaptive grounding [4] and self-introspective decoding [22] validate recommendation outputs in real-time, ensuring that generated suggestions align with available content. By applying these techniques, LLM-ARSs can maintain generative flexibility while preventing misleading recommendations.

Explainability and Trust: Ensuring explainability and user trust is a key challenge in LLM-ARS, as LLM-driven models often function as opaque decision-makers. Unlike traditional RSs with structured optimization criteria, LLM-ARS recommenders rely on implicit reasoning, making it dificult to trace their decisions. This opacity can lead to skepticism, especially when recommendations seem arbitrary or inconsistent. For instance, an LLM in a conversa tional RS might suggest a book based on inferred emotional tone rather than explicit preferences, while a multimodal RS may recom mend a movie based on textual reviews without justifying it through content features like genre or cast. To improve transparency, recent methods explore natural language rationale generation [3], structured decision paths via external knowledge graphs [36, 78], and cross-attention mechanisms that embed user interactions into LLM reasoning [29]. Chain-of-thought prompting further enhances interpretability by breaking down recommendations step by step [30]. Aligning model reasoning with explicit knowledge sources strengthens user trust and control over recommendations.

Safety and Vulnerability: As LLM-ARSs become more autonomous, ensuring safety and robustness is critical, particularly in preventing adversarial manipulation and unintended biases. Malicious users can exploit vulnerabilities through prompt injection, data poisoning, and adversarial attacks, leading to biased or harmful recommendations [84, 85]. Additionally, LLM-based RSs risk rein forcing historical biases, over-optimizing for engagement at the cost of diversity and fairness. Over-personalization further exacerbates filter bubbles, limiting content discovery. Addressing these risks requires multi-layered safeguards. Adversarial training enhances resilience [79], while fairness-aware algorithms impose constraints to mitigate bias [16]. User feedback loops enable manual overrides, preserving user agency. Governance frameworks establish ethi cal boundaries for autonomous recommenders [8]. Together, these mechanisms strengthen the security and reliability of LLM-ARS, ensuring autonomy aligns with ethical responsibility.

## 9.4 Life-long Personalization in LLM-ARS (RQ7)

Personalization in agentic recommender systems is currently lim ited to short-term memory or static user profiles [64]. Life-long personalization introduces the concept of continual learning, where agents evolve with the users’ preferences over time (RQ7). Rather than passively generating recommendations, these agents should actively engage with users, clarify ambiguities, and refine their un derstanding through long-term feedback loops. Challenges include handling catastrophic forgetting, aligning learning with changing user preferences, and maintaining scalability as user interaction his tories grow. Approaches such as meta-learning, episodic memory systems, and AI personas—persistent representations [71] of user preferences—can provide promising solutions. These approaches ensure that agents adapt to users’ evolving needs across diverse contexts and applications.

## 10 Conclusion

This perspective paper first examines the integration of LLMs into agentic RSs, highlighting their role in enabling dynamic, adaptive, and multimodal interactions. We categorize recent advancements into single-agent, multi-agent, and human-LLM hybrid architectures, analyzing their impact on personalization, transparency, and reasoning. Despite these advancements, challenges such as eficiency, hallucination, safety, and lifelong learning remain critical. To address these, we outline future directions, including scalable architectures, robust evaluation frameworks, and improved domain generalization. As agentic RSs evolve, ensuring a balance between autonomy and controllability will be essential for building trustworthy, context-aware, and ethically aligned recommender systems.

## References

[1] Hongru Cai, Yongqi Li, Wenjie Wang, Fengbin Zhu, Xiaoyu Shen, Wenjie Li, and Tat-Seng Chua. 2024. Large Language Models Empowered Personalized Web Agents. CoRR abs/2410.17236 (2024).

[2] Chi-Min Chan, Weize Chen, Yusheng Su, Jianxuan Yu, Wei Xue, Shanghang Zhang, Jie Fu, and Zhiyuan Liu. 2023. Chateval: Towards better llm-based evaluators through multi-agent debate. arXiv preprint arXiv:2308.07201 (2023).

[3] Hanxiong Chen, Xu Chen, Shaoyun Shi, and Yongfeng Zhang. 2021. Generate natural language explanations for recommendation. arXiv preprint arXiv:2101.03392 (2021).

[4] Zhaorun Chen, Zhuokai Zhao, Hongyin Luo, Huaxiu Yao, Bo Li, and Jiawei Zhou. 2024. Halc: Object hallucination reduction via adaptive focal-contrast decoding. arXiv preprint arXiv:2403.00425 (2024).

[5] Nathan Corecco, Giorgio Piatti, Luca A Lanzendörfer, Flint Xiaofeng Fan, and Roger Wattenhofer. 2024. An LLM-based Recommender System Environment. arXiv preprint arXiv:2406.01631 (2024).

[6] Nathan Corecco, Giorgio Piatti, Luca A. Lanzendörfer, Flint Xiaofeng Fan, and Roger Wattenhofer. 2024. SUBER: An RL Environment with Simulated Human Behavior for Recommender Systems. arXiv:2406.01631 [cs.IR] https://arxiv. org/abs/2406.01631

[7] Yang Deng, Lizi Liao, Zhonghua Zheng, Grace Hui Yang, and Tat-Seng Chua. 2024. Towards Human-centered Proactive Conversational Agents. In Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval, SIGIR 2024, Washington DC, USA, July 14-18, 2024. ACM, 807–818.

[8] Zehang Deng, Yongjian Guo, Changzhou Han, Wanlun Ma, Junwu Xiong, Sheng Wen, and Yang Xiang. 2024. Ai agents under threat: A survey of key security challenges and future pathways. Comput. Surveys (2024).

[9] Zane Durante, Qiuyuan Huang, Naoki Wake, Ran Gong, Jae Sung Park, Bidipta Sarkar, Rohan Taori, Yusuke Noda, Demetri Terzopoulos, Yejin Choi, et al. 2024. Agent ai: Surveying the horizons of multimodal interaction. arXiv preprint arXiv:2401.03568 (2024).

[10] Danial Ebrat and Luis Rueda. 2024. Lusifer: LLM-based User SImulated Feedback Environment for online Recommender systems. arXiv preprint arXiv:2405.13362 (2024).

[11] Jiabao Fang, Shen Gao, Pengjie Ren, Xiuying Chen, Suzan Verberne, and Zhaochun Ren. 2024. A multi-agent conversational recommender system. arXiv preprint arXiv:2402.01135 (2024).

[12] Luke Friedman, Sameer Ahuja, David Allen, Zhenning Tan, Hakim Sidahmed, Changbo Long, Jun Xie, Gabriel Schubiner, Ajay Patel, Harsh Lara, Brian Chu, Zexi Chen, and Manoj Tiwari. 2023. Leveraging Large Language Models in Conversational Recommender Systems. arXiv:2305.07961 [cs.IR] https://arxiv. org/abs/2305.07961

[13] Jingtong Gao, Bo Chen, Weiwen Liu, Xiangyang Li, Yichao Wang, Wanyu Wang, Huifeng Guo, Ruiming Tang, and Xiangyu Zhao. 2025. LLM4Rerank: LLM-based Auto-Reranking Framework for Recommendations. arXiv:2406.12433 [cs.IR] https://arxiv.org/abs/2406.12433

[14] Taicheng Guo, Chaochun Liu, Hai Wang, Varun Mannam, Fang Wang, Xin Chen, Xiangliang Zhang, and Chandan K Reddy. 2024. Knowledge Graph Enhanced Language Agents for Recommendation. arXiv preprint arXiv:2410.19627 (2024).

[15] Sirui Hong, Xiawu Zheng, Jonathan Chen, Yuheng Cheng, Jinlin Wang, Ceyao Zhang, Zili Wang, Steven Ka Shing Yau, Zijuan Lin, Liyang Zhou, et al. 2023. Metagpt: Meta programming for multi-agent collaborative framework. arXiv preprint arXiv:2308.00352 (2023).

[16] Wenyue Hua, Xianjun Yang, Mingyu Jin, Zelong Li, Wei Cheng, Ruixiang Tang, and Yongfeng Zhang. 2024. Trustagent: Towards safe and trustworthy llmbased agents through agent constitution. In Trustworthy Multi-modal Foundation Models and AI Agents (TiFA).

[17] Chengkai Huang, Tong Yu, Kaige Xie, Shuai Zhang, Lina Yao, and Julian McAuley. 2024. Foundation models for recommender systems: A survey and new perspectives. arXiv preprint arXiv:2402.11143 (2024).

[18] Feiran Huang, Zhenghang Yang, Junyi Jiang, Yuanchen Bei, Yijie Zhang, and Hao Chen. 2024. Large Language Model Interaction Simulator for Cold-Start Item Recommendation. CoRR abs/2402.09176 (2024).

[19] Xu Huang, Jianxun Lian, Yuxuan Lei, Jing Yao, Defu Lian, and Xing Xie. 2023. Recommender ai agent: Integrating large language models for interactive rec ommendations. arXiv preprint arXiv:2308.16505 (2023).

[20] Xu Huang, Jianxun Lian, Yuxuan Lei, Jing Yao, Defu Lian, and Xing Xie. 2023. Recommender AI Agent: Integrating Large Language Models for Interactive Recommendations. CoRR abs/2308.16505 (2023). arXiv:2308.16505

[21] Xu Huang, Weiwen Liu, Xiaolong Chen, Xingmei Wang, Hao Wang, Defu Lian, Yasheng Wang, Ruiming Tang, and Enhong Chen. 2024. Understanding the planning of LLM agents: A survey. arXiv preprint arXiv:2402.02716 (2024).

[22] Fushuo Huo, Wenchao Xu, Zhong Zhang, Haozhao Wang, Zhicheng Chen, and Peilin Zhao. 2024. Self-introspective decoding: Alleviating hallucinations for large vision-language models. arXiv preprint arXiv:2408.02032 (2024).

[23] Eugene Ie, Chih-Wei Hsu, Martin Mladenov, Vihan Jain, Sanmit Narvekar, Jing Wang, Rui Wu, and Craig Boutilier. 2019. RecSim: A Configurable Sim ulation Platform for Recommender Systems. CoRR abs/1909.04847 (2019). arXiv:1909.04847

[24] Aaron Jaech, Adam Kalai, Adam Lerer, Adam Richardson, Ahmed El-Kishky, Aiden Low, Alec Helyar, Aleksander Madry, Alex Beutel, Alex Carney, et al. 2024. Openai o1 system card. arXiv preprint arXiv:2412.16720 (2024).

[25] Dhruv Khattar, Jaipal Singh Goud, Manish Gupta, and Vasudeva Varma. 2019. Mvae: Multimodal variational autoencoder for fake news detection. In The world wide web conference. 2915–2921.

[26] Sunghwan Kim, Tongyoung Kim, Kwangwook Seo, Jinyoung Yeo, and Dongha Lee. 2024. Stop Playing the Guessing Game! Target-free User Simulation for Eval uating Conversational Recommender Systems. arXiv preprint arXiv:2411.16160 (2024).

[27] Chuang Li, Yang Deng, Hengchang Hu, Min-Yen Kan, and Haizhou Li. 2024. Incorporating External Knowledge and Goal Guidance for LLM-based Conver sational Recommender Systems. arXiv preprint arXiv:2405.01868 (2024).

[28] Guohao Li, Hasan Hammoud, Hani Itani, Dmitrii Khizbullin, and Bernard Ghanem. 2023. Camel: Communicative agents for" mind" exploration of large language model society. Advances in Neural Information Processing Systems 36 (2023), 51991–52008.

[29] Lei Li, Yongfeng Zhang, and Li Chen. 2023. Personalized prompt learning for explainable recommendation. ACM Transactions on Information Systems 41, 4 (2023), 1–26.

[30] Lei Li, Yongfeng Zhang, and Li Chen. 2023. Prompt distillation for eficient llm based recommendation. In Proceedings of the 32nd ACM International Conference on Information and Knowledge Management. 1348–1357.

[31] Jianghao Lin, Xinyi Dai, Yunjia Xi, Weiwen Liu, Bo Chen, Xiangyang Li, Chenxu Zhu, Huifeng Guo, Yong Yu, Ruiming Tang, and Weinan Zhang. 2023. How Can Recommender Systems Benefit from Large Language Models: A Survey. CoRR abs/2306.05817 (2023). arXiv:2306.0581

[32] Peng Liu, Lemei Zhang, and Jon Atle Gulla. 2023. Pre-train, Prompt and Recom mendation: A Comprehensive Survey of Language Modelling Paradigm Adapta tions in Recommender Systems. CoRR abs/2302.03735 (2023). arXiv:2302.03735

[33] Xiao Liu, Hao Yu, Hanchen Zhang, Yifan Xu, Xuanyu Lei, Hanyu Lai, Yu Gu, Hangliang Ding, Kaiwen Men, Kejuan Yang, Shudan Zhang, Xiang Deng, Ao han Zeng, Zhengxiao Du, Chenhui Zhang, Sheng Shen, Tianjun Zhang, Yu Su, Huan Sun, Minlie Huang, Yuxiao Dong, and Jie Tang. 2024. AgentBench: Evaluating LLMs as Agents. In The Twelfth International Conference on Learning Representations, ICLR 2024, Vienna, Austria, May 7-11, 2024. OpenReview.net.

[34] Zhiwei Liu, Weiran Yao, Jianguo Zhang, Liangwei Yang, Zuxin Liu, Juntao Tan, Prafulla K Choubey, Tian Lan, Jason Wu, Huan Wang, et al. 2024. AgentLite: A Lightweight Library for Building and Advancing Task-Oriented LLM Agent System. arXiv preprint arXiv:2402.15538 (2024).

[35] Houhong Lu, Yangyang Zhu, Ming Yin, Guofu Yin, and Luofeng Xie. 2022. Multi modal fusion convolutional neural network with cross-attention mechanism for internal defect detection of magnetic tile. IEEE Access 10 (2022), 60876–60886.

[36] Ziyu Lyu, Yue Wu, Junjie Lai, Min Yang, Chengming Li, and Wei Zhou. 2022. Knowledge enhanced graph neural networks for explainable recommendation. IEEE Transactions on Knowledge and Data Engineering 35, 5 (2022), 4954–4968.

[37] Reiichiro Nakano, Jacob Hilton, Suchir Balaji, Jef Wu, Long Ouyang, Christina Kim, Christopher Hesse, Shantanu Jain, Vineet Kosaraju, William Saunders, et al. 2021. Webgpt: Browser-assisted question-answering with human feedback. arXiv preprint arXiv:2112.09332 (2021).

[38] Lin Ning, Luyang Liu, Jiaxing Wu, Neo Wu, Devora Berlowitz, Sushant Prakash, Bradley Green, Shawn O’Banion, and Jun Xie. 2024. User-LLM: Eficient LLM Contextualization with User Embeddings. CoRR abs/2402.13598 (2024).

[39] OpenAI. 2023. Gpt-4 technical report. OpenAI (2023)

[40] Joshua Park and Yongfeng Zhang. 2025. AgentRec: Agent Recommendation Using Sentence Embeddings Aligned to Human Feedback. arXiv preprint arXiv:2501.13333 (2025).

[41] Chen Qian, Xin Cong, Cheng Yang, Weize Chen, Yusheng Su, Juyuan Xu, Zhiyuan Liu, and Maosong Sun. 2023. Communicative agents for software development. arXiv preprint arXiv:2307.07924 (2023).

[42] Shengsheng Qian, Jun Hu, Quan Fang, and Changsheng Xu. 2021. Knowledge aware multi-modal adaptive graph convolutional networks for fake news detection. ACM Transactions on Multimedia Computing, Communications, and Applications (TOMM) 17, 3 (2021), 1–23

[43] Peixin Qin, Chen Huang, Yang Deng, Wenqiang Lei, and Tat-Seng Chua. 2024. Beyond Persuasion: Towards Conversational Recommender System with Credi ble Explanations. arXiv preprint arXiv:2409.14399 (2024).

[44] Shashank Rajput, Nikhil Mehta, Anima Singh, Raghunandan Hulikal Keshavan, Trung Vu, Lukasz Heldt, Lichan Hong, Yi Tay, Vinh Q. Tran, Jonah Samost, Maciej Kula, Ed H. Chi, and Mahesh Sathiamoorthy. 2023. Recommender Systems with Generative Retrieval. In Advances in Neural Information Processing Systems 36: Annual Conference on Neural Information Processing Systems 2023, NeurIPS 2023, New Orleans, LA, USA, December 10 - 16, 2023.

[45] Ruiyang Ren, Peng Qiu, Yingqi Qu, Jing Liu, Wayne Xin Zhao, Hua Wu, Ji-Rong Wen, and Haifeng Wang. 2024. BASES: Large-scale Web Search User Simulation with Large Language Model based Agents. CoRR abs/2402.17505 (2024).

[46] Stefen Rendle, Zeno Gantner, Christoph Freudenthaler, and Lars Schmidt-Thieme. 2011. Fast context-aware recommendations with factorization machines. In Proceedings of the 34th international ACM SIGIR conference on Research and development in Information Retrieval. 635–644.

[47] Francesco Ricci, Lior Rokach, and Bracha Shapira. 2015. Recommender Systems: Introduction and Challenges. In Recommender Systems Handbook. Springer, 1–34.

[48] Gaurav Sahu and Olga Vechtomova. 2019. Adaptive fusion techniques for multimodal data. arXiv preprint arXiv:1911.03821 (2019).

[49] J Ben Schafer, Dan Frankowski, Jon Herlocker, and Shilad Sen. 2007. Collaborative filtering recommender systems. In The adaptive web: methods and strategies of web personalization. Springer, 291–324.

[50] Minglai Shao, Hua Huang, Qiyao Peng, and Hongtao Liu. 2024. ULMRec: Usercentric Large Language Model for Sequential Recommendation. arXiv preprint arXiv:2412.05543 (2024).

[51] Wentao Shi, Xiangnan He, Yang Zhang, Chongming Gao, Xinyue Li, Jizhi Zhang, Qifan Wang, and Fuli Feng. 2024. Large Language Models are Learnable Planners for Long-Term Recommendation. In Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR 2024). ACM, 1893–1903. https://doi.org/10.1145/3626772.3657683

[52] Noah Shinn, Federico Cassano, Beck Labash, Ashwin Gopinath, Karthik Narasimhan, and Shunyu Yao. 2023. Reflexion: Language agents with verbal reinforcement learning.(2023). arXiv preprint cs.AI/2303.11366 (2023).

[53] Yubo Shu, Hansu Gu, Peng Zhang, Haonan Zhang, Tun Lu, Dongsheng Li, and Ning Gu. 2023. RAH! RecSys-Assistant-Human: A Human-Central Rec ommendation Framework with Large Language Models. CoRR abs/2308.09904 (2023).

[54] Yubo Shu, Haonan Zhang, Hansu Gu, Peng Zhang, Tun Lu, Dongsheng Li, and Ning Gu. 2023. RAH! RecSys-Assistant-Human: A Human-Centered Recommendation Framework with LLM Agents. arXiv:2308.09904 [cs.IR] https://arxiv.org/abs/2308.09904

[55] Yubo Shu, Haonan Zhang, Hansu Gu, Peng Zhang, Tun Lu, Dongsheng Li, and Ning Gu. 2024. RAH! RecSys-Assistant-Human: A Human-Centered Recom mendation Framework With LLM Agents. IEEE Trans. Comput. Soc. Syst. 11, 5 (2024), 6759–6770.

[56] YunPeng Tan, Fangyu Liu, BoWei Li, Zheng Zhang, and Bo Zhang. 2022. An eficient multi-view multimodal data processing framework for social media popularity prediction. In Proceedings of the 30th ACM International Conference on Multimedia. 7200–7204.

[57] Zhulin Tao, Yinwei Wei, Xiang Wang, Xiangnan He, Xianglin Huang, and Tat-Seng Chua. 2020. Mgat: Multimodal graph attention network for recom mendation. Information Processing & Management 57, 5 (2020), 102277.

[58] Jie Wang, Alexandros Karatzoglou, Ioannis Arapakis, and Joemon M Jose. 2024. Reinforcement learning-based recommender systems with large language models for state reward and action modeling. In Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval. 375–385.

[59] Jie Wang, Alexandros Karatzoglou, Ioannis Arapakis, and Joemon M Jose. 2025. Large Language Model driven Policy Exploration for Recommender Systems. arXiv preprint arXiv:2501.13816 (2025).

[60] Lei Wang, Jingsen Zhang, Xu Chen, Yankai Lin, Ruihua Song, Wayne Xin Zhao, and Ji-Rong Wen. 2023. RecAgent: A Novel Simulation Paradigm for Recommender Systems. arXiv:2306.02552 [cs.IR]

[61] Lei Wang, Jingsen Zhang, Hao Yang, Zhiyuan Chen, Jiakai Tang, Zeyu Zhang, Xu Chen, Yankai Lin, Ruihua Song, Wayne Xin Zhao, Jun Xu, Zhicheng Dou, Jun Wang, and Ji-Rong Wen. 2024. User Behavior Simulation with Large Language Model based Agents. arXiv:2306.02552 [cs.IR] https://arxiv.org/abs/2306.02552

[62] Lei Wang, Jingsen Zhang, Hao Yang, Zhi-Yuan Chen, Jiakai Tang, Zeyu Zhang, Xu Chen, Yankai Lin, Hao Sun, Ruihua Song, et al. 2024. User Behavior Simulation with Large Language Model-based Agents for Recommender Systems. ACM Transactions on Information Systems (2024).

[63] Shoujin Wang, Liang Hu, Yan Wang, Longbing Cao, Quan Z Sheng, and Mehmet Orgun. 2019. Sequential recommender systems: challenges, progress and prospects. arXiv preprint arXiv:2001.04830 (2019).

[64] Tiannan Wang, Meiling Tao, Ruoyu Fang, Huilin Wang, Shuai Wang, Yuchen Eleanor Jiang, and Wangchunshu Zhou. 2024. AI PERSONA: Towards Life-long Personalization of LLMs. CoRR abs/2412.13103 (2024).

[65] Xinfeng Wang, Jin Cui, Fumiyo Fukumoto, and Yoshimi Suzuki. 2024. Enhancing High-order Interaction Awareness in LLM-based Recommender Model. arXiv preprint arXiv:2409.19979 (2024).

[66] Xinfeng Wang, Jin Cui, Yoshimi Suzuki, and Fumiyo Fukumoto. 2024. RDRec: Rationale Distillation for LLM-based Recommendation. arXiv preprint arXiv:2405.10587 (2024).

[67] Yancheng Wang, Ziyan Jiang, Zheng Chen, Fan Yang, Yingxue Zhou, Eunah Cho, Xing Fan, Xiaojiang Huang, Yanbin Lu, and Yingzhen Yang. 2023. RecMind: Large Language Model Powered Agent For Recommendation. arXiv preprint arXiv:2308.14296 (2023).

[68] Yancheng Wang, Ziyan Jiang, Zheng Chen, Fan Yang, Yingxue Zhou, Eunah Cho, Xing Fan, Xiaojiang Huang, Yanbin Lu, and Yingzhen Yang. 2024. RecMind: Large Language Model Powered Agent For Recommendation. arXiv:2308.14296 [cs.IR] https://arxiv.org/abs/2308.14296

[69] Zhefan Wang, Yuanqing Yu, Wendi Zheng, Weizhi Ma, and Min Zhang. 2024. Macrec: A multi-agent collaboration framework for recommendation. In Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval. 2760–2764.

[70] Zhefan Wang, Yuanqing Yu, Wendi Zheng, Weizhi Ma, and Min Zhang. 2024. Multi-Agent Collaboration Framework for Recommender Systems. CoRR abs/2402.15235 (2024).

[71] Qingsong Wen, Jing Liang, Carles Sierra, Rose Luckin, Richard Jiarui Tong, Zitao Liu, Peng Cui, and Jiliang Tang. 2024. AI for Education (AI4EDU): Advancing Personalized Education with LLM and Adaptive Learning. In Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining, KDD 2024, Barcelona, Spain, August 25-29, 2024, Ricardo Baeza-Yates and Francesco Bonchi (Eds.). ACM, 6743–6744.

[72] Lilian Weng. 2023. LLM-powered Autonomous Agents. lilianweng.github.io (Jun 2023). https://lilianweng.github.io/posts/2023-06-23-agent/

[73] Junda Wu, Cheng-Chun Chang, Tong Yu, Zhankui He, Jianing Wang, Yupeng Hou, and Julian McAuley. 2024. Coral: Collaborative retrieval-augmented large language models improve long-tail recommendation. In Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining. 3391–3401.

[74] Qingyun Wu, Gagan Bansal, Jieyu Zhang, Yiran Wu, Shaokun Zhang, Erkang Zhu, Beibin Li, Li Jiang, Xiaoyun Zhang, and Chi Wang. 2023. Autogen: En abling next-gen llm applications via multi-agent conversation framework. arXiv preprint arXiv:2308.08155 (2023).

[75] Shirley Wu, Shiyu Zhao, Qian Huang, Kexin Huang, Michihiro Yasunaga, Kaidi Cao, Vassilis N Ioannidis, Karthik Subbian, Jure Leskovec, and James Zou. 2024. AvaTaR: Optimizing LLM Agents for Tool-Assisted Knowledge Retrieval. arXiv preprint arXiv:2406.11200 (2024).

[76] Yang Wu, Pengwei Zhan, Yunjian Zhang, Liming Wang, and Zhen Xu. 2021. Multimodal fusion with co-attention networks for fake news detection. In Findings of the association for computational linguistics: ACL-IJCNLP 2021. 2560– 2569.

[77] Yunjia Xi, Weiwen Liu, Jianghao Lin, Bo Chen, Ruiming Tang, Weinan Zhang, and Yong Yu. 2024. MemoCRS: Memory-enhanced Sequential Conversational Recommender Systems with Large Language Models. In Proceedings of the 33rd ACM International Conference on Information and Knowledge Management. 2585–2595.

[78] Yikun Xian, Zuohui Fu, Shan Muthukrishnan, Gerard De Melo, and Yongfeng Zhang. 2019. Reinforcement knowledge graph reasoning for explainable rec ommendation. In Proceedings of the 42nd international ACM SIGIR conference on research and development in information retrieval. 285–294.

[79] Zhen Xiang, Linzhi Zheng, Yanjie Li, Junyuan Hong, Qinbin Li, Han Xie, Jiawei Zhang, Zidi Xiong, Chulin Xie, Carl Yang, et al. 2024. GuardAgent: Safeguard LLM Agents by a Guard Agent via Knowledge-Enabled Reasoning. arXiv preprint arXiv:2406.09187 (2024).

[80] Shunyu Yao, Jefrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, and Yuan Cao. 2022. React: Synergizing reasoning and acting in language models. arXiv preprint arXiv:2210.03629 (2022).

[81] Weiran Yao, Shelby Heinecke, Juan Carlos Niebles, Zhiwei Liu, Yihao Feng, Le Xue, Rithesh Murthy, Zeyuan Chen, Jianguo Zhang, Devansh Arpit, et al. 2023. Retroformer: Retrospective large language agents with policy gradient optimization. arXiv preprint arXiv:2308.02151 (2023).

[82] Qifan Yu, Juncheng Li, Longhui Wei, Liang Pang, Wentao Ye, Bosheng Qin, Siliang Tang, Qi Tian, and Yueting Zhuang. 2024. Hallucidoctor: Mitigating hallucinatory toxicity in visual instruction data. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. 12944–12953.

[83] Yankai Zeng, Abhiramon Rajasekharan, Parth Padalkar, Kinjal Basu, Joaquín Arias, and Gopal Gupta. 2023. Automated Interactive Domain-Specific Con versational Agents that Understand Human Dialogs. arXiv:2303.08941 [cs.AI]

https://arxiv.org/abs/2303.08941

[84] Yifan Zeng, Yiran Wu, Xiao Zhang, Huazheng Wang, and Qingyun Wu. 2024. Autodefense: Multi-agent llm defense against jailbreak attacks. arXiv preprint arXiv:2403.04783 (2024).

[85] Qiusi Zhan, Zhixiang Liang, Zifan Ying, and Daniel Kang. 2024. Injecagent: Benchmarking indirect prompt injections in tool-integrated large language model agents. arXiv preprint arXiv:2403.02691 (2024).

[86] An Zhang, Leheng Sheng, Yuxin Chen, Hao Li, Yang Deng, Xiang Wang, and Tat-Seng Chua. 2023. On Generative Agents in Recommendation. CoRR abs/2310.10108 (2023). arXiv:2310.10108

[87] Erhan Zhang, Xingzhu Wang, Peiyuan Gong, Yankai Lin, and Jiaxin Mao. 2024. USimAgent: Large Language Models for Simulating Search Users. CoRR abs/2403.09142 (2024).

[88] Jizhi Zhang, Keqin Bao, Wenjie Wang, Yang Zhang, Wentao Shi, Wanhong Xu, Fuli Feng, and Tat-Seng Chua. 2024. Prospect Personalized Recommendation on Large Language Model-based Agent Platform. arXiv:2402.18240 [cs.IR] https://arxiv.org/abs/2402.18240

[89] Junjie Zhang, Yupeng Hou, Ruobing Xie, Wenqi Sun, Julian McAuley, Wayne Xin Zhao, Leyu Lin, and Ji-Rong Wen. 2024. Agentcf: Collaborative learning with autonomous language agents for recommender systems. In Proceedings of the ACM on Web Conference 2024. 3679–3689.

[90] Junjie Zhang, Yupeng Hou, Ruobing Xie, Wenqi Sun, Julian J. McAuley, Wayne Xin Zhao, Leyu Lin, and Ji-Rong Wen. 2023. AgentCF: Collaborative Learning with Autonomous Language Agents for Recommender Systems. CoRR abs/2310.09233 (2023). arXiv:2310.09233

[91] Jinrui Zhang, Teng Wang, Haigang Zhang, Ping Lu, and Feng Zheng. 2024. Reflective instruction tuning: Mitigating hallucinations in large vision-language models. In European Conference on Computer Vision. Springer, 196–213.

[92] Shuai Zhang, Lina Yao, Aixin Sun, and Yi Tay. 2019. Deep Learning Based Recommender System: A Survey and New Perspectives. ACM Comput. Surv. 52, 1 (2019), 5:1–5:38.

[93] Zeyu Zhang, Xiaohe Bo, Chen Ma, Rui Li, Xu Chen, Quanyu Dai, Jieming Zhu, Zhenhua Dong, and Ji-Rong Wen. 2024. A survey on the memory mechanism of large language model based agents. arXiv preprint arXiv:2404.13501 (2024).

[94] Zijian Zhang, Shuchang Liu, Ziru Liu, Rui Zhong, Qingpeng Cai, Xiangyu Zhao, Chunxu Zhang, Qidong Liu, and Peng Jiang. 2024. LLM-Powered User Simulator for Recommender System. arXiv preprint arXiv:2412.16984 (2024).

[95] Hongke Zhao, Songming Zheng, Likang Wu, Bowen Yu, and Jing Wang. 2024. Lane: Logic alignment of non-tuning large language models and online recommendation systems for explainable reason generation. arXiv preprint arXiv:2407.02833 (2024).

[96] Minyi Zhao, Jie Wang, Zhaoyang Li, Jiyuan Zhang, Zhenbang Sun, and Shuigeng Zhou. 2024. Efectively Enhancing Vision Language Large Models by Prompt Augmentation and Caption Utilization. arXiv preprint arXiv:2409.14484 (2024).

[97] Yuyue Zhao, Jiancan Wu, Xiang Wang, Wei Tang, Dingxian Wang, and Maarten de Rijke. 2024. Let Me Do It For You: Towards LLM Empowered Recommendation via Tool Learning. In Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR 2024). ACM, 1796–1806. https://doi.org/10.1145/3626772.3657828

[98] Yuyue Zhao, Jiancan Wu, Xiang Wang, Wei Tang, Dingxian Wang, and Maarten De Rijke. 2024. Let me do it for you: Towards llm empowered recommendation via tool learning. In Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval. 1796–1806.

[99] Lixi Zhu, Xiaowen Huang, and Jitao Sang. 2024. A LLM-based Controllable, Scalable, Human-Involved User Simulator Framework for Conversational Rec ommender Systems. arXiv preprint arXiv:2405.08035 (2024).

[100] Yu Zhu, Hao Li, Yikang Liao, Beidou Wang, Ziyu Guan, Haifeng Liu, and Deng Cai. 2017. What to Do Next: Modeling User Behaviors by Time-LSTM. In Proceedings of the Twenty-Sixth International Joint Conference on Artificial Intelligence, Melbourne. 3602–3608.

## RapidPD: Rapid Human and Pet Presence Detection System for Smart Vehicles via Wi-Fi

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

## WHEN IS A + xA = <sup>R</sup>

# WHEN IS A + xA = <sup>R</sup>

JINHE YE, LIANG YU, AND XUANHENG ZHAO

<sup>Abstract.</sup> For a subgroup A of (<sup>R</sup>, +) and a real x, define A+xA = {a+xb : $a , b \in A \}$ and $X _ { A } = \{ x \in \mathbb { R } : A + x A = \mathbb { R } \}$ . We show that there is an $F _ { \sigma }$ subgroup A of $( \mathbb { R } , + )$ such that dim<sub>H</sub> $\textstyle ( A ) \leq { \frac { 1 } { 2 } }$ and $X _ { A } \neq \varnothing$ . However, if $A \subseteq \mathbb { R }$ is a subring of <sup>R</sup> and $X _ { A } \neq \varnothing$ , then $A = \mathbb { R }$ . Moreover, assuming CH (the continuum hypothesis), there is a subgroup A of $( \mathbb { R } , + )$ with dim<sub>H</sub> $\mathbf { \Omega } _ { [ } ( A ) = 0$ such that $X _ { A } = \mathbb { R } \backslash \mathbb { Q } .$ The proof of this theorem combines several techniques in recursion theory and algorithmic dimension. Several other theorems on analytic subgroups and subfields of the reals are presented. We also discuss some of these results in the p-adics.

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

## <sub>2.</sub> Subrings and Subfields

Recall that an ordered field $( R , + , \cdot , 0 , 1 , \le ) \ ( \le$ is a total order on $F ;$ if $a \leq b$ then $a + c \leq b + c ;$ and if $0 \leq a$ and $0 \leq b$ then $0 \leq a \cdot b )$ is real closed if:

(i) Any positive element has a square root in $R ,$ and

(ii) Any polynomial equation $f ( x ) = 0$ where $f ( x ) \in R [ x ]$ is of odd degree has a root in R.

Fact 2.1 (Artin-Schreier, see $\left[ 7 , \ \mathrm { p . 6 7 4 } \right] )$ . Let C be an algebrically closed field and F be a proper subfield of $C$ such that C/F is finite. Then F is real closed and $C = F \left( { \sqrt { - 1 } } \right)$

Fact 2.2 (“Lying-over”, see $\left[ 7 , \ \mathrm { p . 4 1 1 } \right] )$ . Let E be a commutative ring, R a subring such that E is integral over R (for every element α of $E$ , there is a monic polynomial $f ( x ) \in R [ x ]$ such that $f ( \alpha ) = 0 )$ . Then for each prime ideal p of R, there is a prime ideal P of E such that $p = P \cap R .$ In particular, if $E$ is a field, so is R.

Let p be a prime number. Let $\textstyle a = { \frac { b } { c } } , b , c \in \mathbb { Z }$ be nonzero. We extract from b and c as high a power of the prime number p as possible, namely choose m an interger such that

$$
a = p ^ {m} \frac {b ^ {\prime}}{c ^ {\prime}}, (b ^ {\prime} c ^ {\prime}, p) = 1,
$$

and we put the p-adic absolute value $\begin{array} { r } { | a | _ { p } = \frac { 1 } { p ^ { m } } } \end{array}$ . The field of p-adic numbers $\mathbb { Q } _ { p }$ is the completion of $\mathbb { Q }$ with respect to the metric $d _ { p } ( x , y ) = | x - y | _ { p }$

The following lemma is presumably well-known.

Lemma 2.3. (i) If F is a subfield of <sup>R</sup> such that <sup>R</sup>/F is finite, then $F = \mathbb { R }$

(ii) If F is a subfield of $\mathbb { Q } _ { p }$ such that $\mathbb { Q } _ { p } / F$ is finite, then $F = \mathbb { Q } _ { p }$

Proof. (i) follows from Fact 2.1. For (ii), consider the normal closure K of $\mathbb { Q } _ { p } / F ;$ K is finite over $\mathbb { Q } _ { p }$ and hence any automorphism of K is continuous. Hence any automorphism of K restricts to the identity on $\mathbb { Q } _ { p } ,$ , which implies that $\mathbb { Q } _ { p } = F =$ K. □

Recall that we define $X _ { A } = \{ x \in \mathbb { R } : A + x A = \mathbb { R } \}$

Proposition 2.4. (i) If A is a subring of <sup>R</sup> and $X _ { A } \neq \varnothing$ , then $A = \mathbb { R }$

(ii) If A is a subring $o f \mathbb { Q } _ { p }$ and there is x such that $A + x A = \mathbb { Q } _ { p }$ , then $A = \mathbb { Q } _ { p }$

Proof. (i). By our assumption, <sup>R</sup> is finite over A and hence by Fact 2.2, A is a field since <sup>R</sup> is a field. Then Lemma 2.3 (i) implies $A = \mathbb { R }$

(ii). By Fact 2.2 and our assumption, A is a subfield of $\mathbb { Q } _ { p }$ . If $A \neq \mathbb { Q } _ { p }$ , then $[ \mathbb { Q } _ { p } : A ] \neq 1$ is finite. Then Lemma 2.3 (ii) implies $A = \mathbb { Q } _ { p }$ □

Both $\mathbb { Q } _ { p }$ and <sup>R</sup> are Polish (separable completely metrizable) spaces. A subset A of a Polish space X is analytic if it is the projection of a Borel set $B \subseteq X \times X$

Fact 2.5 (see [8, Theorem 11.18] ). Every analytic subset of <sup>R</sup> is measurable.

The proof of this fact is general enough to work for other measures in Polish spaces. For example, in the following Proposition 2.6, we will use the fact that every analytic subset of $\mathbb { Q } _ { p }$ is µ-measurable where $\mu$ is the Haar measure on $\mathbb { Q } _ { p } .$

Given a field K and $a \in K$ , a maximal subfield of K without a is a maximal (with respect to inclusion) element of $\{ L \subseteq K : L$ is a subfield of $K$ and $a \notin L \}$

Proposition 2.6. Let $K = \mathbb { Q } _ { p }$ or <sup>R</sup>. Let F be an analytic subfield of K with some $x \in K \backslash F$ . Then there is $y \in K \backslash F$ such that $x \notin F ( y )$ . Hence F is not a maximal subfield of K without x.

Proof. Assume otherwise, then F is a maximal subfield of K avoiding x. This implies that $K / F$ is algebraic. Indeed, if x is not algebraic over F , then $x \notin F ( x ^ { 2 } )$ . Now if $K / F$ is not algebraic, then K contains a copy of $F ( X )$ for X transcendental over F , which does not contain x.

So each $y \in K \setminus F$ satisfies a polynomial over F . Let $D _ { n }$ denote the set of elements in K whose minimal polynomial over F is of degree at most n, this is an analytic set and $\textstyle \bigcup _ { n \in \mathbb { N } } D _ { n } = K$ . In particular, $D _ { n }$ is measurable by Fact 2.5. It is clear that $D _ { n }$ is closed under multiplication by −1. Note further that the diference of 2 elements of degree at most n over F has degree at most $n ^ { 2 }$ . Moreover, there must be n such that $\mu ( D _ { n } ) > 0$ where $\mu$ denote the Haar measure on $K$ . So $D _ { n ^ { 2 } } = K$ by the Steinhaus theorem for Haar measure on locally compact groups (see [19]). This means that any element in $K / F$ is of degree at most n for some $n \in \mathbb { N }$ . By the primitive element theorem, we have that $[ K : F ]$ is at most n. Then by Lemma 2.3, $K = F .$ , a contradiction. □

The assumption that F is analytic is used to guarantee that $D _ { n }$ is measurable, so that we can use the Steinhaus theorem. If $D _ { n } \mathrm { { ^ { s } } }$ are measurable a priori, then the proof will go through as is. It follows from $\mathrm { A C }$ that there is a non-measurable set. Under some weaker set theoretic axioms, the situation will be diferent. We use DC to denote the axiom of dependent choice, that is: suppose R is a relation on a nonempty set X; if for every $a \in X$ , there is an $b \in X$ such that $a R b$ , then there is a sequence $\{ x _ { n } \} _ { n \in \omega }$ in X such that ${ x _ { n } R x _ { n + 1 } }$ for all $n \in \omega$ . DC follows from AC trivially. Solovay [17] proved that $\mathrm { Z F + D C + }$ Every subset of <sup>R</sup> is measurable is consistent.

By the above discussion and the proof of Proposition 2.6, we have the following conclusion: without $\mathrm { A C } .$ one cannot construct a maximal subfield of <sup>R</sup> without a given point.

Corollary 2.7. Assume $\mathrm { Z F + D C + }$ Every subset of <sup>R</sup> is measurable. For any subfield F of <sup>R</sup> and $x \in \mathbb { R } \setminus F$ , F is not a maximal subfield of K without x.

## <sub>3.</sub> Subgroups

We recall some terminology and notation from [4]. Let $A \subseteq X$ , where $( X , d _ { X } )$ is a metric space. Let the diameter of A, written |A|, be the supremum of the distances between any two points in A, i.e. $\begin{array} { r } { | A | = \operatorname* { s u p } _ { x , y \in A } d _ { X } ( x , y ) } \end{array}$ . Suppose $s \geq 0$ . For each $\delta > 0$ , we define the s-dimensional Hausdorf measure of A by

$\mathcal { H } ^ { s } ( A ) = \operatorname* { l i m } _ { \delta \to 0 } \mathcal { H } _ { \delta } ^ { s } ( A ) = \operatorname* { l i m } _ { \delta \to 0 } \operatorname* { i n f } \left\{ \sum _ { i = 1 } ^ { \infty } | U _ { i } | ^ { s } : \{ U _ { i } \} \right.$ is a cover of $A , 0 < | U _ { i } | \leqslant \delta , \forall i \}$

$\mathcal { H } ^ { s } ( A )$ can be (and usually is) 0 or ∞. There is a critical value of s at which $\mathcal { H } ^ { s } ( A )$ “jumps” from ∞ to 0. This critical value is called the Hausdorf dimension of A, written dim<sub>H</sub>(A). In other words,

$$
\dim_ {\mathrm{H}} (A) = \inf \{s: \mathcal {H} ^ {s} (A) = 0 \} = \sup \{s: \mathcal {H} ^ {s} (A) = \infty \}.
$$

We gather some of the basic properties of subgroups of the reals. Recall that we define $X _ { A } = \{ x \in \mathbb { R } : A + x A = \mathbb { R } \}$

Proposition 3.1. Suppose that A is a subgroup $o f \mathbb { R }$

(i) For all $x \in \mathbb { R } , A + x A$ is a subgroup of <sup>R</sup>.

(ii) If $p \in \mathbb { Q }$ and $p \in X _ { A }$ , then $A = \mathbb { R }$

(iii) $I f k \in \mathbb { N } , p _ { 0 } , . . . , p _ { k } \in \mathbb { Q }$ and $\textstyle A + \sum _ { i = 0 } ^ { k } p _ { i } A = \mathbb { R }$ , then $A = \mathbb { R }$

(iv) Define the tensor product

$$
\mathbb {Q} \otimes_ {\mathbb {Z}} A = \left\{\sum_ {i = 0} ^ {k} p _ {i} a _ {i}: k \in \mathbb {N}, p _ {i} \in \mathbb {Q}, a _ {i} \in A f o r i = 0, \dots , k \right\}.
$$

Then dim $\mathfrak {i } _ { \mathrm { H } } \left( \mathbb { Q } \otimes _ { \mathbb { Z } } A \right) = \dim _ { \mathrm { H } } ( A )$

(v) If $x \in X _ { A }$ , then for all $m \in \mathbb { Z } - \{ 0 \}$ , $m x \in X _ { A }$

(vi) $I f x \in X _ { A }$ , then for all $m , n \in \mathbb { Z } - \{ 0 \} , x + { \frac { n } { m } } \in X _ { A }$

Proof. (i). By the definition of a subgroup.

(ii). Suppose that $\textstyle p = { \frac { m } { n } }$ for some integers m and $n \neq 0$ . Then for any $c \in \mathbb { R }$ there are $a , b \in A$ such that $\begin{array} { r } { a + \frac { m b } { n } = c . } \end{array}$ So $n c = n a + m b \in A$ . Thus $\textstyle \mathbb { R } = { \frac { 1 } { n } } A$ Since Char $( \mathbb { R } ) = 0 .$ , we have $\mathbb { R } = n \mathbb { R } = A$

(iii). Suppose that $\begin{array} { r } { p _ { i } = \frac { m _ { i } } { n _ { i } } } \end{array}$ for some integers m<sub>i</sub> and $n _ { i } \neq 0$ . Let n be the least common multiple of those $n _ { i }$ . Then $\textstyle \mathbb { R } = A + \sum _ { i = 0 } ^ { k } p _ { i } A \subseteq { \frac { 1 } { n } } A$ , so $A = \mathbb { R }$

(iv). Note that $\textstyle \mathbb { Q } \otimes _ { \mathbb { Z } } A \subseteq \bigcup _ { n \geq 1 } { \frac { 1 } { n } } A$ . But it is clear that d $\begin{array} { r } { \operatorname* { l i m } _ { \mathrm { H } } ( A ) = \dim _ { \mathrm { H } } ( { \frac { 1 } { n } } A ) } \end{array}$ for any $n \geq 1$ since $f : \mathbb { R } \to \mathbb { R } , x \overset { - } { \mapsto }$ nx is bi-Lipschitz. So

$$
\dim_ {\mathrm{H}} (A) \leqslant \dim_ {\mathrm{H}} (\mathbb {Q} \otimes_ {\mathbb {Z}} A) \leqslant \dim_ {\mathrm{H}} \left(\bigcup_ {n \geq 1} \frac {1}{n} A\right) = \sup _ {i} \dim_ {\mathrm{H}} \left(\frac {1}{n} A\right) = \dim_ {\mathrm{H}} (A).
$$

(v). Note that

$$
A + m x A = m \left(\frac {A}{m} + x A\right) \supseteq m (A + x A) = m \mathbb {R}.
$$

Since Char(<sup>R</sup>) = 0, we have $A + m x A = \mathbb { R }$

(vi). Note that

$$
A + (x + \frac {n}{m}) A = A + (m x + n) \frac {A}{m} \supseteq A + (m x + n) A = A + m x A.
$$

By (v), we have $\begin{array} { r } { A + ( x + \frac { n } { m } ) A = \mathbb { R } } \end{array}$

Remark 3.2. Let X be a Hamel basis of <sup>R</sup> over <sup>Q</sup> with $\dim _ { \mathrm { H } } ( X ) = 0$ (such a basis exists by Lutz, Qi, and $Y u \ [ 1 1 ]$ , and let A be the group generated by X. then by Proposition ${ \it 3 . 1 ( i v ) }$ ，

$$
\dim_ {\mathrm{H}} (A) = \dim_ {\mathrm{H}} (\mathbb {R}) = 1 > \dim_ {\mathrm{H}} (X).
$$

Hence the additive group generated by a basis X may have Hausdorf dimension greater than $\dim _ { \mathrm { H } } ( X )$

We can easily deduce from the Marstrand projection theorem: if A is “regular” and $^ { \mathrm { \tiny {  } } } \mathrm { l a r g e } ^ { \mathrm { \tiny { \ ' } } }$ enough, then there is x such that $A + x A = \mathbb { R }$

Fact 3.3 (Marstrand [13]). Let $F \subseteq \mathbb { R } ^ { 2 }$ be an analytic set with dim<sub>H</sub> $( F ) > 1$ . Then for almost all $\theta \in \left( - \frac { \pi } { 2 } , \frac { \pi } { 2 } \right)$ , proj<sub>θ</sub>(F ) (the projection of F on the line $l _ { \theta } : y = \tan \theta \cdot x )$ has positive length.

Proposition 3.4. If A is an analytic subgroup $o f \left( \mathbb { R } , + \right)$ with dim<sub>H</sub> $[ \left( A \right) > \frac { 1 } { 2 }$ , then $X _ { A }$ is co-null.

This is a minor generalization of [4, Exercise 6.8], which implies that for almost all $x , A + x A$ has Hausdorf dimension 1.

Proof. By the product formula of Hausdorf dimension (see [4, Chapter 7]),

$$
\dim_ {\mathrm{H}} (A \times A) \geq \dim_ {\mathrm{H}} (A) + \dim_ {\mathrm{H}} (A) > 1.
$$

Hence for almost all $\theta \in \left( - \frac { \pi } { 2 } , \frac { \pi } { 2 } \right)$ , pro $\mathfrak { j } _ { \theta } ( A \times A )$ has positive length. Let $f ( t ) =$ arctan t for all $t \in \mathbb { R }$ . Define $\begin{array} { r } { \bar { \Theta } \stackrel { - } { = } \{ \theta \in ( - \frac { \pi } { 2 } , \frac { \pi } { 2 } ) : \mathrm { p r o j } _ { \theta } ( A \times A ) } \end{array}$ has positive length}. Since Θ is co-null (and hence measurable), so $f ^ { - 1 } ( \Theta )$ is measurable. We claim that $f ^ { - 1 } ( \Theta )$ is co-null. Suppose not, then $\mathbb { R } \backslash f ^ { - 1 } ( \Theta )$ has positive measure. Then there is $N \in \mathbb { R }$ such that $\mathbb { R } \backslash f ^ { - 1 } ( \Theta ) \cap [ - N , N ]$ has positive measure. But inf $t \in [ - N , N ] ~ f ^ { \prime } ( t ) >$ 0, then $f ( f ^ { - 1 } ( \Theta ) \cap [ - N , N ] )$ has positive measure, a contradiction.

Suppose $( a , b ) , ( c , d ) \in A \times A , a \neq c$ and $b \neq d .$ Then the line passing through these two points is:

$$
l _ {(a, b), (c, d)}: \frac {y - d}{x - c} = \frac {y - b}{x - a}.
$$

The slope of $l _ { ( a , b ) , ( c , d ) }$ is $\frac { b - d } { a - c }$ . And if $t \neq 0$ and $a + t b = c + t d$ , then $\begin{array} { r } { t = - \frac { a - c } { b - d } } \end{array}$ . So for $( a , b ) , ( c , d )$ and t as above, $a + t b = c + t d$ if and only if $l _ { ( a , b ) , ( c , d ) }$ is perpendicular to $l _ { \arctan t } : y = t \cdot x$ . In particular, $l _ { \mathrm { a r c t a n } t }$ and $A + t A$ are homeomorphic via:

$$
(a, b) \mapsto a + b t.
$$

And

$$
| a + b t | = (1 + t ^ {2}) | a | = \sqrt {1 + t ^ {2}} \sqrt {a ^ {2} + b ^ {2}} = \sqrt {1 + t ^ {2}} | \overrightarrow {0 , (a , b)} |.
$$

Hence the measure of $A + t A$ is equal to the measure of $\operatorname { p r o j } _ { \arctan \operatorname { t } } ( A \times A )$ times $\sqrt { 1 + t ^ { 2 } }$ provided $t \neq 0$ . By Proposition $3 . 1 ( \mathrm { i } ) , A + t A$ is a group. Then by Corollary $1 . 2 , A + t A = \mathbb { R }$ if $\operatorname { p r o j } _ { \arctan t } ( A \times A )$ has positive length. Since $f ^ { - 1 } ( \Theta )$ is co-null, $\operatorname { p r o j } _ { \arctan t } ( A \times A )$ has positive length for almost all t. □

Next, we prove Theorem 1.4, which refines Proposition 3.4.

Proof of Theorem 1.4. As a convention, we consider a real a and its binary expansion $m + 0 . a _ { 1 } a _ { 2 } \cdots a _ { n } \cdot \cdot$ · with infinitely many 0s to be equivalent, where $m \in \mathbb { Z }$ is the integer part of a and the numbers $a _ { i } \in \{ 0 , 1 \}$ express its binary decimal part.

We first proof a weaker result: there is an $F _ { \sigma }$ subgroup A of $( \mathbb { R } , + )$ and $x \in \mathbb { R }$ such that $A + x A = \mathbb { R }$ and A is null.

Define $Q _ { n } = \{ m \in \mathbb { N } : 3 ^ { n - 1 } \leqslant m < 3 ^ { n } \}$ for $n \geq 1$ . Then each $Q _ { n }$ contains $2 \cdot 3 ^ { n - 1 }$ numbers. Divide $\{ 1 , 2 , \ldots \}$ into two parts $P _ { 1 } , P _ { 2 }$ such that for all $n \geq 1$ the first $3 ^ { n - 1 }$ numbers of $Q _ { n }$ are in $P _ { 1 }$ , and the other numbers of $Q _ { n }$ are in $P _ { 2 }$ Formally,

$$
\begin{array}{c} P _ {1} = \{k: \exists n \exists i \in [ 0, 3 ^ {n}) (k = 3 ^ {n} + i) \}, \\ P _ {2} = \{k: \exists n \exists i \in [ 3 ^ {n}, 2 \cdot 3 ^ {n}) (k = 3 ^ {n} + i) \}. \end{array}
$$

Define

$$
A _ {0} = \left\{m + 0. a _ {1} a _ {2} \dots a _ {n} \dots : m \in \mathbb {Z} \wedge \forall n \in P _ {2} (a _ {n} = 0) \right\}.
$$

$A _ { 0 }$ consists of reals with segments of 0s of length $3 ^ { k } ( k \in \mathbb { N } )$ , and ahead of each segment of 0s there is an arbitrary segment of the same length. Define for each n,

$$
A _ {n} = \overbrace {A _ {0} \pm A _ {0} \pm \cdots \pm A _ {0}} ^ {n} = \{\alpha_ {1} \pm \alpha_ {2} \pm \dots \pm \alpha_ {n}: \alpha_ {i} \in A _ {0}, 1 \leqslant i \leqslant n \}.
$$

Fix $n \geq 1 { \mathrm { ~ a n d ~ } } \varepsilon > 0$ . Choose $k \geq 1$ such that

(i) $2 ^ { - \frac { 1 } { 2 } \cdot 3 ^ { k } + 1 } < \varepsilon ;$ and

(ii) for all $a = m + 0 . a _ { 1 } a _ { 2 } \cdot \cdot \cdot \in A _ { n } ,$

$$
\forall j \in \left[ 2 \cdot 3 ^ {k - 1}, \frac {5}{2} \cdot 3 ^ {k - 1} \right] (a _ {j} = 0) \vee \forall j \in \left[ 2 \cdot 3 ^ {k - 1}, \frac {5}{2} \cdot 3 ^ {k - 1} \right] (a _ {j} = 1).
$$

Then the measure of $A _ { n }$ is no more than $2 \cdot 2 ^ { - \frac { 1 } { 2 } \cdot 3 ^ { k } } < \varepsilon$ . Since ε is arbitrary, $A _ { n }$ is null. Let A be the subgroup of $( \mathbb { R } , + )$ generated from $A _ { 0 }$ . Then $A = \textstyle \bigcup _ { n > 1 } A _ { n }$ is null. Since $A _ { 0 }$ is compact, A is $F _ { \sigma }$ . Define $x = 0 . x _ { 1 } x _ { 2 } \cdot \cdot \cdot$ · such that $x _ { n } = 1$ if and only if $\exists k ( n = 3 ^ { k } )$ . Given any real $y = m + 0 . y _ { 1 } y _ { 2 } \cdot \cdot \cdot$ , we shall define a real $b = 0 . b _ { 1 } b _ { 2 } \cdot \cdot \cdot \in A _ { 0 }$ such that $b \cdot x$ and y are equal on the nth binary place for each $n \in P _ { 2 }$ . Then we can pick $c \in A _ { 0 }$ such that $c + b x = y , \mathrm { s o } A + x A = \mathbb { R }$

Intuitively, in the calculation $b \cdot x , x _ { 3 ^ { k } } = 1$ causes the binary places of b to shift to the right $3 ^ { k }$ places, i.e.

$$
0. \overbrace {0 \cdots 0} ^ {3 ^ {k} - 1} 1 \times 0. b _ {1} b _ {2} \dots = 0. \overbrace {0 \cdots 0} ^ {3 ^ {k}} b _ {1} b _ {2} \dots .
$$

Denote $b x = 0 . c _ { 1 } c _ { 2 } \cdot \cdot \cdot . \mathrm { B } _ { \mathrm { J } }$ recursion on n, one can choose $\{ b _ { m } : m \in Q _ { n } \cap P _ { 1 } \}$ such that $c _ { m } = y _ { m }$ for all $m \in Q _ { n } \cap P _ { 2 }$ as follows: suppose $\{ b _ { m } : m \in Q _ { k } \cap P _ { 1 } , k < n \}$ have been chosen so that $c _ { m } = y _ { m }$ for all $k < n$ and $m \in Q _ { k } \cap P _ { 2 }$ . Whatever $\{ b _ { m } : m \in Q _ { k } \cap P _ { 1 } , k \geq n + 1 \}$ are chosen, we have

$$
0. \overbrace {0 \cdots 0} ^ {3 ^ {n} - 1} b _ {3 ^ {n}} b _ {3 ^ {n} + 1} b _ {3 ^ {n} + 2} \dots \times x <   0. \overbrace {0 \cdots 0} ^ {3 ^ {n} - 1} 1.
$$

Hence $\{ c _ { m } : m \in Q _ { n } \cap P _ { 2 } \}$ is determined only by $\{ b _ { m } : m \in Q _ { k } \cap P _ { 1 } , k \leqslant n \}$ Now it is clear that we can choose $\{ b _ { m } : m \in Q _ { n } \cap P _ { 1 } \}$ to ensure $c _ { m } = y _ { m }$ for all $m \in Q _ { n } \cap P _ { 2 }$ . This ends the proof of the weaker result.

It needs some more efort to make dim $\textstyle \mathrm { H } ( A ) = { \frac { 1 } { 2 } }$ . Let $\{ p _ { n } \} _ { n \ge 1 }$ be an increasing sequence of even numbers such that $\begin{array} { r } { \sum _ { k < n } p _ { k } = o ( { \bar { p } } _ { n } ) } \end{array}$ and $3 ^ { n } = o ( p _ { n } ) $ . Define

$$
Q _ {n} = \{m \in \mathbb {N}: 1 + \sum_ {k <   n} p _ {k} \leq m <   1 + \sum_ {k \leq n} p _ {k} \}.
$$

Divide $\{ 1 , 2 , \ldots \}$ into two parts $P _ { 1 } , P _ { 2 }$ such that for all $n \geq 1$ , the first half of the numbers of $Q _ { n }$ are in $P _ { 1 }$ , and the other numbers of $Q _ { n }$ are in $P _ { 2 }$ . Define

$$
A _ {0} = \{m + 0. a _ {1} a _ {2} \dots a _ {n} \dots : m \in \mathbb {Z} \land \forall n \in P _ {2} (a _ {n} = 0) \}.
$$

Define $A _ { n } = { \widehat { A } } _ { 0 } \pm A _ { 0 } \pm \cdot \cdot \cdot \pm A _ { 0 }$ and $A = \textstyle \bigcup _ { n > 1 } A _ { n }$ . As before, A is an $F _ { \sigma }$ subgroup of $( \mathbb { R } , + )$ and there is x such that $A + x A = \mathbb { R }$ . It remains to show that $\dim _ { \mathrm { H } } ( A _ { n } ) =$ $\textstyle { \frac { 1 } { 2 } }$ for all n. Fix n. For all $k > n$ and $a = m + 0 . a _ { 1 } a _ { 2 } \cdot \cdot \cdot \in A _ { n }$ 2

$$
\forall j \in \left(\sum_ {j <   k} p _ {j} + \frac {p _ {k}}{2}, \sum_ {j \leq k} p _ {j} - n \right] (a _ {j} = 0) \vee \forall j \in \left(\sum_ {j <   k} p _ {j} + \frac {p _ {k}}{2}, \sum_ {j \leq k} p _ {j} - n \right] (a _ {j} = 1).
$$

Let $\delta = 2 ^ { - } \Sigma _ { j \leq k } p _ { j }$ . If $s > \frac { 1 } { 2 }$ , then

$$
\mathcal {H} _ {\delta} ^ {s} (A _ {n}) \leq 2 ^ {1 + \sum_ {j <   k} p _ {j} + \frac {p _ {k}}{2}} 2 ^ {n + 3} (2 ^ {- \sum_ {j \leq k} p _ {j}}) ^ {s} \leq 2 ^ {n + 4 + \sum_ {j <   k} p _ {j} - (s - \frac {1}{2}) p _ {k}}.
$$

Since $\begin{array} { r } { \sum _ { j < k } p _ { j } = o ( p _ { k } ) , \mathcal { H } ^ { s } ( A _ { n } ) = 0 . \mathrm { \ S o \ d i m _ { H } } ( A _ { n } ) \le \frac { 1 } { 2 } . } \end{array}$

Remark 3.5. Note that the analogue of the above holds in the p-adics as well. Namely, there is an $F _ { \sigma }$ subgroup A $\subseteq \left( \mathbb { Z } _ { p } , + \right)$ and $x \in \mathbb { Z } _ { p }$ such that $\mu ( A ) = 0$ and $A + x A = \mathbb { Z } _ { p } ,$ where µ denotes the Haar measure on $\mathbb { Z } _ { p }$ . Moreover, one can also achieve that the Hausdorf dimension is $1 / 2$ . The proof follows from the same strategy as the previous proof. We include the details for the sake of completeness.

Proof. We only include the proof for the existence of such A, the calculation of the Hausdorf dimension of A is left to the reader as it follows from the same argument as in <sup>R</sup>.

Note that every element $a \in \mathbb { Z } _ { p }$ has a unique expansion

$$
a = \sum_ {n = 0} ^ {\infty} a _ {n} p ^ {n}, \quad a _ {n} \in \{0, \dots , p - 1 \}.
$$

Define

$$
Q _ {n} = \{m \in \mathbb {N}: p ^ {n - 1} \leq m <   p ^ {n} \}.
$$

Then

$$
| Q _ {n} | = (p - 1) p ^ {n - 1}.
$$

Partition <sup>N</sup> into two sets $P _ { 1 } , P _ { 2 }$ so that for every $n \geq 1$ , the first half of the indices in $Q _ { n }$ belong to $P _ { 1 }$ and the remaining indices belong to $P _ { 2 }$ . Formally,

$$
P _ {1} \cap Q _ {n} = \left\{p ^ {n - 1}, \dots , p ^ {n - 1} + \left\lfloor \frac {| Q _ {n} |}{2} \right\rfloor - 1 \right\},
$$

and

$$
P _ {2} = \mathbb {N} \setminus P _ {1}.
$$

Define

$$
A _ {0} = \left\{\sum_ {n = 0} ^ {\infty} a _ {n} p ^ {n}: \forall n \in P _ {2} (a _ {n} = 0) \right\}.
$$

Thus elements of $A _ { 0 }$ have arbitrary digits on $P _ { 1 }$ and vanish on $P _ { 2 }$ .

For each $m \geq 1$ , define

$$
A _ {m} = \underbrace {A _ {0} \pm A _ {0} \pm \cdots \pm A _ {0}} _ {m}.
$$

Let

$$
A = \bigcup_ {m \geq 1} A _ {m}.
$$

Since $A _ { 0 }$ is compact, every $A _ { m }$ is compact, hence A is an $F _ { \sigma }$ subgroup of $( \mathbb { Z } _ { p } , + )$ Fix $m \geq 1$ . Carrying in p-adic addition propagate only finitely far, which is comparable to m. Hence there exists $N = N ( m )$ such that for every suficiently large k and every

$$
a = \sum a _ {n} p ^ {n} \in A _ {m},
$$

either

$$
\forall j \in I _ {k} (a _ {j} = 0)
$$

or

$$
\forall j \in I _ {k} (a _ {j} = p - 1),
$$

where $I _ { k }$ is a terminal segment of $Q _ { k }$ of length comparable $\mathrm { t o } \ | Q _ { k } | / 2$

Therefore $A _ { m }$ can be covered by at most

$$
2 p ^ {| Q _ {1} | + \dots + | Q _ {k - 1} | + | Q _ {k} | / 2 + O (1)}
$$

balls of radius

$$
p ^ {- \max Q _ {k}}.
$$

Since a ball of radius $p ^ { - N }$ has Haar measure $p ^ { - N }$ , it follows that

$$
\mu (A _ {m}) \leq C p ^ {- c | Q _ {k} |} \to 0.
$$

Hence every $A _ { m }$ is Haar null, and therefore A is Haar null.

Now define

$$
x = \sum_ {k = 1} ^ {\infty} p ^ {p ^ {k}}.
$$

Thus the $p ^ { k } .$ -th digit of x equals 1, and all other digits vanish.

$$
y = \sum_ {n = 0} ^ {\infty} y _ {n} p ^ {n} \in \mathbb {Z} _ {p}.
$$

We recursively construct

$$
b = \sum b _ {n} p ^ {n} \in A _ {0}
$$

such that

bx

agrees with y on all coordinates in $P _ { 2 }$ .

Multiplication by $p ^ { p ^ { k } }$ shifts digits exactly $p ^ { k }$ places:

$$
p ^ {p ^ {k}} \sum b _ {n} p ^ {n} = \sum b _ {n} p ^ {n + p ^ {k}}.
$$

Because the supports are widely separated, digits coming from later blocks cannot influence the current block except through bounded carry efects. Hence, recursively on $k ,$ one may choose the free digits

$$
\{b _ {n}: n \in P _ {1} \cap Q _ {k} \}
$$

so that

$$
(b x) _ {n} = y _ {n} \qquad (n \in P _ {2} \cap Q _ {k}).
$$

Define

$$
c = y - b x.
$$

Since bx already agrees with $y$ on $P _ { 2 }$ , the element c has vanishing digits on $P _ { 2 } .$ hence

$$
c \in A _ {0}.
$$

Therefore

$$
y = c + b x \in A + x A.
$$

Since $y \in \mathbb { Z } _ { p }$ was arbitrary,

$$
A + x A = \mathbb {Z} _ {p}.
$$

□

In the proof of Theorem 1.4, both A and x depend on the intervals $Q _ { n }$ . What is the relation between A and elements of $X _ { A }$ in general?

Proposition 3.6. If A is an analytic subgroup of $( \mathbb { R } , + )$ and $x \in X _ { A }$ , then there are $c , d \in A$ such that $\textstyle x = { \frac { c } { d } }$ . In particular, $c A + d A = \mathbb { R }$

This result is an immediate corollary of the following Theorem of Le Gac.

Fact 3.7 (Barth´elemy Le Gac [5]). If G and H are analytic subgroups of $( \mathbb { R } , + )$ such that $G + H = \mathbb { R }$ and $G \cap H = \{ 0 \}$ , then either $G = \mathbb { R } \ o r \ G = \{ 0 \}$

Recall that for each $\alpha \in [ 0 , 1 ]$ , there is a Borel subgroup $A _ { \alpha }$ of $( \mathbb { R } , + )$ with $\dim _ { \mathrm { H } } ( A ) = \alpha \ [ 2 0 ]$ . For $\alpha > { \frac { 1 } { 2 } } , X _ { A _ { \alpha } }$ is co-null by Proposition $3 . 4$ . The following theorem claims that for such groups $A _ { \alpha }$ , there is an $F _ { \sigma }$ subgroup $B \subseteq A _ { \alpha }$ such that $X _ { B }$ is co-null. It also reduces the problem of constructing an $F _ { \sigma }$ proper subgroup B of the reals with $X _ { B } \neq \varnothing$ to the problem of constructing an analytic proper subgroup A of the reals with $X _ { A } \neq \varnothing$

Theorem 3.8. Suppose that A is an analytic subgroup $o f \left( \mathbb { R } , + \right)$

(i) $H x \in X _ { A }$ , then there is an $F _ { \sigma }$ subgroup $B \subseteq A$ such that $x \in X _ { B }$

(ii) $I f X _ { A }$ is co-null, then there is an $F _ { \sigma }$ subgroup $B \subseteq A$ such that $X _ { B }$ is co-null.

By Proposition 3.1(vi), $\textstyle X _ { A } = \bigcup _ { q \in \mathbb { Q } } q + X _ { A }$ . Thus if $X _ { A }$ has positive measure, it is automatically co-null. We need the following uniformization theorem in the proof.

Fact 3.9 (Jankov, von Neumann, see [9, 18.1]). Let X, Y be standard Borel spaces and $P \subseteq X \times Y$ is analytic. Then there is a Σ-measurable function $f : X \to Y$ such that $( x , f ( x ) ) \in P$ for all $x \in p r o j _ { X } ( P )$ (the projection from P to $X ) ,$ , where Σ is the σ-algebra generated by the analytic sets.

In particular, if X and Y are Borel subsets of Euclidean spaces, then the function f is Lebesgue measurable by Fact 2.5.

Proof of Theorem 3.8. For (i), suppose that A is an analytic subgroup of $( \mathbb { R } , + )$ and $x \in X _ { A }$ . Then the graph of the function $\varphi : A \times A \to \mathbb { R }$ so that $( a , b ) \mapsto a + x b$ is an analytic subset of $\mathbb { R } ^ { 3 }$ . By Fact 3.9, there is a Lebesgue measurable function $f : \mathbb { R } \to A \times A$ such that for any $z \in \mathbb { R } , \varphi ( f ( z ) ) = z$ . By the Lusin Theorem, there is a compact set $P \subseteq \mathbb { R }$ with positive measure and a continuous function $\psi : P  A \times A$ so that for $\arg z \in P , \varphi ( \psi ( z ) ) = z$ . Let

$$
C _ {0} = \{a \in \mathbb {R}: \exists z \in P \exists b \in \mathbb {R} (\psi (z) = (a, b)) \},
$$

and

$$
C _ {1} = \{b \in \mathbb {R}: \exists z \in P \exists a \in \mathbb {R} (\psi (z) = (a, b)) \}.
$$

Both $C _ { 0 }$ and $C _ { 1 }$ are compact and so is $C _ { 0 } \cup C _ { 1 }$ . Let B be the group generated by $C _ { 0 } \cup C _ { 1 }$ . Then B is $F _ { \sigma }$ and $B \subseteq A$ . Moreover, the image $\varphi ( B \times B ) \supseteq P$ has positive measure. Since $\varphi ( B \times B )$ is a subgroup of <sup>R</sup>, by Corollary $1 . 2 , \varphi ( B \times B ) = \mathbb { R }$ Hence $x \in X _ { B }$

For (ii), suppose that A is an analytic subgroup of $( \mathbb { R } , + )$ and $X _ { A }$ is co-null. By the regularity of Lebesgue measure, there is a co-null $F _ { \sigma }$ subset $F \subseteq X _ { A }$ . It sufices to show that there is an $F _ { \sigma }$ subgroup $B \subseteq A$ such that for almost all $x \in F$ , we have $x \in X _ { B }$

The graph of the function

$$
\varphi : A \times A \times F \rightarrow \mathbb {R} \times F, (a, b, x) \mapsto (a + x b, x)
$$

is an analytic subset of $\mathbb { R } ^ { 5 }$ . By Fact 3.9, there is a Lebesgue measurable function

$$
f: \mathbb {R} \times F \to A \times A \times F
$$

such that for any $z \in \mathbb { R } \times F , \varphi ( f ( z ) ) = z$ . By the Lusin Theorem, for all $n ,$ there is a compact subset $K _ { n }$ of $\mathbb { R } \times F$ such that $\psi _ { n } : = f \mid K _ { n }$ is continuous and

$$
\mu ((\mathbb {R} \times F) \cap B _ {n} (0) \backslash K _ {n}) <   \frac {1}{n},
$$

where $\mu$ is the Lebesgue measure on $\mathbb { R } ^ { 2 }$ and $B _ { n } ( 0 ) \subseteq \mathbb { R } ^ { 2 }$ is the closed ball with radius n and center 0. Let

$$
C _ {0} = \{a \in \mathbb {R}: \exists n \exists z \in K _ {n} \exists b, x \in \mathbb {R} (\psi_ {n} (z) = (a, b, x)) \},
$$

and

$$
C _ {1} = \{b \in \mathbb {R}: \exists n \exists z \in K _ {n} \exists a, x \in \mathbb {R} (\psi (z) = (a, b, x)) \}.
$$

Both $C _ { 0 }$ and $C _ { 1 }$ are $F _ { \sigma }$ and so is $C _ { 0 } \cup C _ { 1 }$ . Let $B$ be the additive group generated by $C _ { 0 } \cup C _ { 1 }$ . Then B is an $F _ { \sigma }$ set and $B \subseteq A$ . Moreover, the projection of the image $\varphi ( B \times B \times \{ x \} )$ to the first coordinate has positive measure for almost all $x \in F$ by the Fubini theorem since $( \mathbb { R } \times F ) \backslash \cup _ { n } K _ { n }$ is null. So $X _ { B }$ is conull. □

## <sub>4.</sub> Constructions assuming CH

The main goal of this section is to prove Theorem 1.5. It requires notion from recursion theory and algorithmic dimension. A standard reference is [2]. We consider the elements of the Cantor space $2 ^ { \omega }$ as reals. We denote the set of binary strings of finite length by $2 ^ { < \omega }$ . Given $\sigma , \tau \in 2 ^ { < \omega }$ , we write $\sigma \prec \tau \mathrm { i f } \ \sigma$ is a proper initial segment of $\tau .$ . The same notation is applied when $\tau$ is replaced by a real $x \in 2 ^ { \omega }$ . We write $\sigma \tau$ to denote the string obtained by concatenating $\sigma$ and $\tau .$ The Cantor space is equipped with a topology generated by the basic clopen sets $I _ { \sigma } = \{ \sigma \alpha : \alpha \in 2 ^ { \omega } \}$ for $\sigma \in 2 ^ { < \omega }$ . It is also a measure space: the Lebesgue measure $\mu ( I _ { \sigma } ) = 2 ^ { - | \sigma | }$ , where |σ| is the length of the string σ. For a co-infinite set $z \subseteq \omega .$ define

$$
F (z) = \sum_ {i \in z} 2 ^ {- i - 1} \in [ 0, 1) \subseteq \mathbb {R}.
$$

F is an “isometry” between the co-null subset of $2 ^ { \omega }$ consisting of the co-infinite sets and the interval [0, 1). Note that under $F ,$ the measure $\mu$ on $2 ^ { \omega }$ turns into the Lebesgue measure on <sup>R</sup>. Similarly the Hausdorf dimension is also preserved between $2 ^ { \omega }$ and <sup>R</sup>. For a rigorous proof of this fact, see [12, Section $4 ]$ . There the authors proved that $F$ preserves the property of having positive Hausdorf measure. Since the set of all the co-finite elements in $2 ^ { \omega }$ is countable, it is µ-null. Hence we assume that every real $x \in 2 ^ { \omega }$ we deal with is co-infinite and consider the arithmetic operations on $2 ^ { \omega }$ to be the same as arithmetic operations on $\mathbb { R } / \mathbb { Z }$ . Given reals $x ,$ $y .$ We write $x \leq _ { T } y$ if x is Turing reducible to $y .$ . Given a real $y ,$ if $W \subseteq 2 ^ { < \omega }$ is r.e. (recursively enumerable) in y, then the set $U \subseteq 2 ^ { \omega }$ of reals with an initial segment in W is called a $\Sigma _ { 1 } ^ { 0 } ( y )$ set. Given $\sigma \in 2 ^ { < \omega }$ and $x \in 2 ^ { \omega }$ , let $K ( \sigma )$ be the prefix-free Kolmogorov complexity of σ and $K ^ { x } ( \sigma )$ be the prefix-free Kolmogorov complexity of σ relativized to x (see [2]). Given reals $x , y \in 2 ^ { \omega }$ , define the real $x \oplus y$ such that for each n, $x \oplus y ( 2 n ) = x ( n )$ and $x \oplus y ( 2 n + 1 ) = y ( n )$ . Note that operation ⊕ is not associative. However, it is invariant under Turing degree. For example, we have $\left( x _ { 1 } \oplus x _ { 2 } \right) \oplus x _ { 3 } \equiv _ { T } x _ { 1 } \oplus \left( x _ { 2 } \oplus x _ { 3 } \right)$ . Then we define by recursion that

$$
x _ {1} \oplus \dots \oplus x _ {n} = x _ {1} \oplus (x _ {2} \oplus x _ {3} \oplus \dots \oplus x _ {n}).
$$

Definition 4.1. (i) A set $S \subseteq 2 ^ { < \omega }$ is dense if for every $\sigma \in 2 ^ { < \omega }$ , there is a string $\tau \in S$ such that $\tau \succ \sigma$

(ii) Given reals x and y. We say that x is y-generic<sup>3</sup> if for every $\Sigma _ { 1 } ^ { 0 } ( y )$ dense set $S \subseteq 2 ^ { < \omega }$ , there is a string $\sigma \prec x$ such that $\sigma \in S$ . We say x is generic $i f x$ is x<sub>0</sub>-generic where $x _ { 0 } ( n ) = 0$ for all $n \in \omega$ . In particular, $i f x$ is y-generic for some $y ,$ then x is generic.

Fact 4.2 (H¨olzl et al. [6]). There is a constant c such that for every generic real x and $i \in \{ 0 , 1 \}$ , there are infinitely many n such that

$$
\forall m \in \left[ n, 2 ^ {2 ^ {2 ^ {n}}} \right] (K (G \upharpoonright m) \leqslant K (m) + c \wedge G (m) = i).
$$

Fact 4.3 (The point-to-set principle, Lutz and Lutz [10]). For every set $E \subseteq \mathbb { R }$ ，

$$
\dim_ {\mathrm{H}} (E) = \min _ {A \subseteq \omega} \sup _ {x \in E} \operatorname * {l i m i n f} _ {n \to \infty} \frac {K ^ {A} (x \upharpoonright n)}{n}.
$$

Lemma 4.4 (Folklore). Let $G = \{ x \in 2 ^ { \omega }$ : x generic}, then $\dim _ { \mathrm { H } } ( G ) = 0$

Proof. Note that $K ( n ) \leqslant$ log $n + 2$ log log $n + O ( 1 )$ for every $n \in \omega ~ ( \mathrm { s e e ~ } [ 2 ] )$ . Then by Fact 4.2, we have lim in $\complement _ { n  \infty } { \frac { K ( x \harpoonright n ) } { n } } = 0$ for every generic real x. Hence by Fact 4.3, $\dim _ { \mathrm { H } } ( G ) = 0$ □

The following lemma reflects the intuition that genericity is preserved under arithmetic operations. Recall that we consider the arithmetic operations on $2 ^ { \omega }$ to be the same as arithmetic operations on $\mathbb { R } / \mathbb { Z }$

Lemma 4.5. Given $x , a , b , g \in 2 ^ { \omega } \backslash \{ 0 \}$ , if g is a ⊕ b ⊕ x-generic, then $g + b , a \cdot g .$ $g ^ { n } ( n \in \mathbb { Z } \backslash \{ 0 \} )$ and $a \cdot g + b$ are $a \oplus b \oplus$ x-generic.

Proof. We proof that $g + b$ is $a \oplus b \oplus x$ -generic first. Fix a $\Sigma _ { 1 } ^ { 0 } ( a \oplus b \oplus x )$ dense set $S$ and $\{ S _ { s } \} _ { s \in \omega }$ an $a \oplus b \oplus$ x-recursive enumeration of $S \left( S _ { n } \subseteq S _ { n + 1 } \right.$ for each n and there is exactly one element in $S _ { n + 1 } \backslash S _ { n } )$ . We inductively define $S _ { s } ^ { \prime }$ at stage $s + 1$ as follows:

suppose $\sigma \in S _ { s + 1 } \backslash S _ { s }$ . Since there are infinitely many 0s in the sequence b, there is $\tau$ such that $\forall y \succ \tau ( y + b \succ \sigma )$ . Choose τ of the least length and enumerate it into $S ^ { \prime } .$

It is clear that $S ^ { \prime }$ is $\Sigma _ { 1 } ^ { 0 } ( a \oplus b \oplus x )$ . Fix $\gamma \in 2 ^ { < \omega }$ . Choose $\gamma _ { 1 }$ such that $\{ y + b :$ $y \succ \gamma \} \supseteq I _ { \gamma _ { 1 } }$ . Since S is dense, there is $\rho \in S$ such that $\rho \succ \gamma _ { 1 }$ . By the definition of $S ^ { \prime }$ , there is $\tau \in S ^ { \prime }$ such that $\forall y \succ \tau ( y + b \succ \rho )$ . Then $\tau \succeq \gamma$ . Hence $S ^ { \prime }$ is dense. Since $g$ is $a \oplus b \oplus$ x-generic, there is $\tau \prec g$ such that $\tau \in S ^ { \prime }$ . By the definition of $S ^ { \prime }$ , there is $\sigma \in S$ such that $\sigma \prec g + b$ . So $g + b$ is $a \oplus b$ ⊕ x-generic.

Similarly one can proof that $a \cdot g , g ^ { - 1 }$ and $g ^ { 2 }$ are $a \oplus b \oplus$ x-generic, which implies $g ^ { n }$ and $a \cdot g + b$ also are. □

Proof of Theorem 1.5. Fix $\{ ( x _ { \alpha } , y _ { \alpha } ) \} _ { \alpha < \aleph }$ an enumeration of $( \mathrm { d o m } ( F ) \backslash F ^ { - 1 } ( \mathbb { Q } ) ) \times$ dom(F ) (F is defined at the beginning of this section). We construct a sequence of pairs of reals $\{ ( g _ { \alpha } , h _ { \alpha } ) \} _ { \alpha < \aleph _ { 2 } }$ by induction on $\alpha < \aleph _ { 1 }$

Stage α. Define

$$
G _ {\alpha} = \{x _ {\beta} \oplus y _ {\beta} \oplus g _ {\beta} \oplus h _ {\beta} \oplus x _ {\alpha} \oplus y _ {\alpha}: \beta <   \alpha \}.
$$

Let

$$
I _ {\alpha} = \{x: (\exists n) (\exists a _ {0},..., a _ {n} \in G _ {\alpha}) [ x \leq_ {T} a _ {0} \oplus a _ {1} \oplus ... \oplus a _ {n} ] \},
$$

the Turing ideal generated by $G _ { \alpha }$ . Since $I _ { \alpha }$ is countable, there is a real $g _ { \alpha }$ that is z-generic for all $z \in I _ { \alpha }$ . Let $\begin{array} { r } { h _ { \alpha } = \frac { y _ { \alpha } - g _ { \alpha } } { x _ { \alpha } } } \end{array}$

Let $A _ { 0 }$ be the group generated by $\{ g _ { \alpha } : \alpha < \aleph _ { 1 } \} \cup \{ h _ { \alpha } : \alpha < \aleph _ { 1 } \}$ . We claim that $A _ { 0 }$ contains only generic reals. For any $g \in A _ { 0 }$ , there are finite sequences $\{ g _ { \alpha _ { i } } , h _ { \alpha _ { i } } , s _ { i } , t _ { i } \} _ { 0 \leqslant i \leqslant n } ,$ , where $s _ { i } , t _ { i } \in \mathbb { Z } .$ and ordinals $\alpha _ { 0 } < \alpha _ { 1 } < \cdots < \alpha _ { n }$ such that $s _ { n } ^ { 2 } + t _ { n } ^ { 2 } \neq 0$ and

$$
g = \sum_ {i = 0} ^ {n} (s _ {i} g _ {\alpha_ {i}} + t _ {i} h _ {\alpha_ {i}}).
$$

Define $c = ( \oplus _ { 0 \leqslant i \leqslant n - 1 } ( g _ { \alpha _ { i } } \oplus h _ { \alpha _ { i } } ) ) \oplus x _ { \alpha _ { n } } \oplus y _ { \alpha _ { n } }$ . By the construction, $g _ { \alpha _ { n } }$ is c-generic. Also

$$
s _ {n} g _ {\alpha_ {n}} + t _ {n} h _ {\alpha_ {n}} = t _ {n} \frac {y _ {\alpha_ {n}}}{x _ {\alpha_ {n}}} + \left(s _ {n} - \frac {t _ {n}}{x _ {\alpha_ {n}}}\right) g _ {\alpha_ {n}},
$$

so

$$
g = \left(s _ {n} - \frac {t _ {n}}{x _ {\alpha_ {n}}}\right) g _ {\alpha_ {n}} + \left(t _ {n} \frac {y _ {\alpha_ {n}}}{x _ {\alpha_ {n}}} + \sum_ {i = 0} ^ {n - 1} (s _ {i} g _ {\alpha_ {i}} + t _ {i} h _ {\alpha_ {i}})\right).
$$

Since $x _ { \alpha _ { n } }$ is irrational, we have that $\begin{array} { r } { s _ { n } - \frac { t _ { n } } { x _ { \alpha n } } \neq 0 } \end{array}$ . By Lemma 4.5, g is c-generic and hence generic. Thus $\mathrm { d i m } _ { \mathrm { H } } ( A _ { 0 } ) = 0$ by Lemma 4.4. Let A be the subgroup of <sup>R</sup> generated by $F ( A _ { 0 } )$ . Then dim<sub>H</sub> $( A ) = 0$ . For any pair $( x , y ) \in [ 0 , 1 ] \times [ 0 , 1 ]$ with $x \notin \mathbb { Q }$ , there are members $g , h \in A$ so that $h = { \frac { y - g } { x } }$ and so $g + x \cdot h = y$ . So $\mathbb { R } \backslash \mathbb { Q } \subseteq X _ { A }$ . By Proposition $3 . 1 ( \mathrm { i i } ) , \mathbb { Q } \cap X _ { A } = \emptyset$ □

Question 2. (i) Can CH in Theorem 1.5 be removed?

(ii) Can A in Theorem 1.5 be Borel?

The complexity of A in Theorem 1.5 is not evident from the construction. The following proposition shows that at least it is impossible to be $F _ { \sigma }$

Proposition 4.6. Suppose $A \subseteq \mathbb { R }$ is $F _ { \sigma }$ and $n u l l , ^ { 4 }$ then there is an irrational x such that $A + x A$ is null. Moreover, the set $\{ x : A + x A$ null} is comeager.<sup>5</sup>

Let $\mu$ be the Lebesgue measure on <sup>R</sup>. The following fact is clear.

Fact 4.7. Let $\{ I _ { i } \} _ { i \leq n }$ be a finite set of open intervals and J an open interval, then

$$
\mu ((\bigcup_ {i \leq n} I _ {i}) + J) \leq n \mu (J) + \sum_ {k \leq n} \mu (I _ {i}).
$$

Proof of Proposition $4 . 6 .$ Suppose $A = \textstyle \bigcup _ { n \geq 1 } A _ { n }$ is an $F _ { \sigma }$ null subset of <sup>R</sup> with each $A _ { n }$ compact.

Lemma 4.8. For each $m , n \geq 1$ , the set

$$
D _ {m, n} = \left\{x \in \mathbb {R}: \mu (A _ {n} + x A _ {n}) <   \frac {1}{m} \right\}
$$

contains a dense open subset $o f \mathbb { R }$

Proof of Lemma 4.8. Given $m , n \geq 1$ , we shall show that $D _ { m , n }$ contains a dense open set in (0, 1). It is not hard to generalize the proof to show that $D _ { m , n }$ contains a dense open set in <sup>R</sup>.

Let σ be a binary string and $q \in \mathbb { N } .$ . Fix a real $x = 0 . \sigma 0 ^ { q } x ^ { * } \in ( 0 , 1 )$ , where $x ^ { * } \in 2 ^ { \omega }$ is the tail of the binary expansion of x. Define $y = 0 . x ^ { * } \in ( 0 , 1 )$ . Then

$$
A _ {n} + x A _ {n} \subseteq A _ {n} + \sum_ {0 \leqslant i \leqslant | \sigma | - 1} \sigma (i) 2 ^ {- i - 1} A _ {n} + 2 ^ {- | \sigma | - q} y A _ {n}.
$$

The set $\begin{array} { r } { A _ { n , \sigma } : = A _ { n } + \sum _ { 0 \leqslant i \leqslant | \sigma | - 1 } \sigma ( i ) 2 ^ { - i - 1 } A _ { n } } \end{array}$ is compact and

$$
A _ {n, \sigma} \subseteq A + \sum_ {0 \leqslant i \leqslant | \sigma | - 1} \sigma (i) 2 ^ {- i - 1} A
$$

is null by Proposition 3.1(i) and Corollary 1.2. So there is a finite open interval cover $\{ I _ { j } \} _ { 1 \leqslant j \leqslant k }$ of $A _ { n , \sigma }$ such that $\begin{array} { r } { \sum _ { 1 \leqslant j \leqslant k } | I _ { j } | < \frac { 1 } { 2 m } } \end{array}$ . Suppose that $A _ { n } \subseteq [ - N , N ]$ and so $y A _ { n } \subseteq [ - N , N ]$ . Then if $\textstyle 2 ^ { - q + 1 } { \bar { N } } k < { \frac { 1 } { 2 m } }$ , by Lemma 4.7, we have

$$
\mu (A _ {n} + x A _ {n}) \leq \mu (A _ {n, \sigma} + 2 ^ {- | \sigma | - q} y A _ {n}) \leq \sum_ {0 \leq j \leq k} | I _ {j} | + k 2 ^ {- q - | \sigma |} 2 N <   \frac {1}{2 m} + \frac {1}{2 m} = \frac {1}{m}.
$$

Since $\sigma$ is arbitrary, $D _ { m , n }$ contains a dense open set in (0, 1).

Using this lemma, the set $\{ x : \mu ( A + x A ) = 0 \}$ is comeager by the Baire category theorem. □

Assuming CH, we can also construct a maximal subfield of <sup>R</sup> with Hausdorf dimension 0 such that some given real is not in its algebraic closure. Given a set $A \subseteq \mathbb { R }$ , let $F ( A )$ be the field generated by A. Denote the relative algebraic closure of $F ( A )$ in <sup>R</sup> by $\operatorname { a c l } _ { \mathbb { R } } ( A )$

Fact 4.9 (Exchange of Algebraic Closure). For a set $A \subseteq \mathbb { R }$ and reals a and $b , \ i f$ $b \in \operatorname { a c l } _ { \mathbb { R } } ( A \cup \{ a \} )$ and $b \notin$ aclR(A), then $a \in \operatorname { a c l } _ { \mathbb { R } } ( A \cup \{ b \} )$

Proposition 4.10. Assume CH. Given x a transcendental number, there is a subfield A of <sup>R</sup> such that

(i) $\dim _ { \mathrm { H } } ( A ) = 0 ;$ and

(ii) $x \not \in \operatorname { a c l } _ { \mathbb { R } } ( A )$ ; and

(iii) for any $y \not \in \operatorname { a c l } _ { \mathbb { R } } ( A ) , x \in \operatorname { a c l } _ { \mathbb { R } } ( A \cup \{ y \} )$

Proof. Fix $\{ y _ { \alpha } \} _ { \alpha < \aleph } .$ an enumeration of <sup>R</sup>. Fix x a transcendental number. Define $\textstyle A = \bigcup _ { \alpha < \aleph _ { 1 } } A _ { \alpha }$ by induction on stages $\alpha < \aleph _ { 1 } \colon$

Stage 0. Define $A _ { 0 } = \mathbb { Q } . \ x \not \in \mathrm { a c l } _ { \mathbb { R } } ( A _ { 0 } )$ since it is transcendental.

Stage $\alpha > 0$ . Recall that G is the set of generic reals (see Lemma 4.4). Suppose by induction that we have a countable field

$$
B _ {\alpha} = \bigcup_ {\beta <   \alpha} A _ {\beta} \subseteq G \cup \mathbb {Q}
$$

such that $x \not \in \mathrm { a c l } _ { \mathbb { R } } ( B _ { \alpha } )$ . Choose the least $\gamma < \aleph _ { 1 }$ such that $y _ { \gamma } \not \in \mathrm { a c l } _ { \mathbb { R } } ( B _ { \alpha } )$ and $x \not \in \operatorname { a c l } _ { \mathbb { R } } ( B _ { \alpha } \cup \{ y _ { \gamma } \} )$ (if such a γ does not exist, end the whole construction). And if such a γ exists, we say that γ acts at stage α. Let $I _ { \alpha }$ be the Turing ideal generated by $B _ { \alpha } \cup \{ y _ { \gamma } , x \}$ . Choose a real $g _ { \alpha }$ such that

(i) g<sub>α</sub> is y-generic for all $y \in I _ { \alpha } ;$ ; and

(ii) $g _ { \alpha } \not \in$ aclR $( B _ { \alpha } \cup \{ y _ { \gamma } , x \} )$

Let $A _ { \alpha }$ be the subfield of <sup>R</sup> generated by $\textstyle B _ { \alpha } \cup \{ g _ { \alpha } , { \frac { g _ { \alpha } - x } { y _ { \gamma } } } \}$

We first show that x $\notin$ aclR $\left( { \cal A } _ { \alpha } \right)$ if there is an ordinal γ which acts at stage α. By induction, we assume that x $\sharp \operatorname { a c l } _ { \mathbb { R } } ( B _ { \alpha } )$ . Let $\begin{array} { r } { h _ { \alpha } = \frac { g _ { \alpha } - x } { y _ { \gamma } } } \end{array}$ . Then $x \in \mathrm { a c l } _ { \mathbb { R } } ( B _ { \alpha } \cup$ J $\{ g _ { \alpha } , h _ { \alpha } \} )$ but x /∈ aclR $( B _ { \alpha } \cup \{ g _ { \alpha } \} ) ~ ( x \not \in \mathrm { a c l } _ { \mathbb { R } } ( B _ { \alpha } )$ by the induction hypothesis, and $g _ { \alpha } \not \in$ aclR $\left( B _ { \alpha } \cup \{ x \} \right)$ ) by its choice, then by Fact $4 . 9 , \ x \notin$ aclR $\left( B _ { \alpha } \cup \{ g _ { \alpha } \} \right) )$ . So $h _ { \alpha } \in \operatorname { a c l } _ { \mathbb { R } } ( B _ { \alpha } \cup \{ g _ { \alpha } , x \} )$ by Fact 4.9. Then $y _ { \gamma } \in \operatorname { a c l } _ { \mathbb { R } } ( B _ { \alpha } \cup \{ g _ { \alpha } , x \} )$ . And by Fact 4.9 again, since $y _ { \gamma } \not \in \mathrm { a c l } _ { \mathbb { R } } ( B _ { \alpha } )$ , we have $y _ { \gamma } \not \in \operatorname { a c l } _ { \mathbb { R } } ( B _ { \alpha } \cup \{ x \} )$ . So by Fact 4.9 again, $g _ { \alpha } \in \mathrm { a c l } _ { \mathbb { R } } ( B _ { \alpha } \cup \{ y _ { \gamma } , x \} )$ , a contradiction.

By Lemma 4.5, $A _ { \alpha } \subseteq G \cup \mathbb { Q }$ for all α. So the induction hypothesis holds at any stage before the construction ends.

Now we define $\textstyle A = \bigcup _ { \alpha < \aleph _ { 1 } } A _ { \alpha }$ and verify that A satisfies the conditions in the statement. We may assume the construction does not end at any stage $\alpha < \aleph _ { 1 }$ (otherwise A is countable and it is clear that the conditions hold). Since $A =$ $\textstyle \bigcup _ { \alpha < \aleph _ { 1 } } A _ { \alpha } \subseteq G \cup \mathbb { Q }$ , Dim<sub>H</sub>(A) = 0. If $y \not \in$ aclR(A), choose $\gamma < \aleph _ { 1 }$ such that $y = y _ { \gamma }$ Then $x \in$ aclR $\left( A \cup \left\{ y \right\} \right)$ . Otherwise, γ acts at some stage $\alpha < \aleph _ { 1 }$ . So $g _ { \alpha } , \frac { g _ { \alpha } - x } { y }$ and y are in $\operatorname { a c l } _ { \mathbb { R } } ( A \cup \{ y \} )$ . Then x is also in $\operatorname { a c l } _ { \mathbb { R } } ( A \cup \{ y \} )$ , a contradiction. □

## References

[1] J. Bourgain. On the Erd¨os-Volkmann and Katz-Tao ring conjectures. Geom. Funct. Anal., 13 (2):334–365, 2003. 1

[2] Rodney G. Downey and Denis R. Hirschfeldt. Algorithmic randomness and complexity. Theory and Applications of Computability. Springer, New York, 2010. 4, 4

[3] G. A. Edgar and Chris Miller. Borel subrings of the reals. Proc. Amer. Math. Soc., 131 (4):1121–1129, 2003. 1

[4] Kenneth Falconer. Fractal geometry. John Wiley & Sons, Ltd., Chichester, Third edition, 2014. Mathematical foundations and applications. 1, 3, 3

[5] Barth´elemy Le Gac. Some properties of Borel subgroups of real numbers. Proc. Amer. Math. Soc., 87 (4):677–680, 1983. 3.7

[6] Rupert H¨olzl, Wolfgang Merkle, Joseph Miller, Frank Stephan, and Liang Yu. Chaitin’s Ω as a continuous function. J. Symb. Log., 85 (1):486–510, 2020. 4.2

[7] Nathan Jacobson. Basic algebra. II. W. H. Freeman and Company, New York, Second edition, 1989. 2.1, 2.2

[8] Thomas Jech, Set theory, Berlin: Springer-Verlag, Millennium edition, Springer Monographs in Mathematics, 2003, Springer. 2.5

[9] Alexander S. Kechris, Classical descriptive set theory, Berlin: Springer-Verlag, Graduate Texts in Mathematics 156, 1995, Springer. 3.9

[10] Jack H. Lutz and Neil Lutz. Algorithmic information, plane Kakeya sets, and conditional dimension. ACM Trans. Comput. Theory, 10 (2):0, 2018. 4.3

[11] Jack H. Lutz, Renrui Qi, and Liang Yu. The point-to-set principle and the dimensions of Hamel bases. Computability, 13 (2):105–112, 2024. 3.2

[12] Andrew Marks, Dino Rossegger, and Theodore Slaman. Hausdorf dimension and countable Borel equivalence relations. Proc. Amer. Math. Soc., 156 (2):883–892, 2026. 4

[13] John M. Marstrand. Some fundamental geometrical properties of plane sets of fractional dimensions. Proc. London Math. Soc. (3), 4:257–302, 1954. 3.3

[14] R. Daniel Mauldin. Subfields of <sup>R</sup> with arbitrary Hausdorf dimension. Math. Proc. Cambridge Philos. Soc., 161 (1):157–165, 2016. 1

[15] Frank Quigley. Maximal subfields of an algebraically closed field not containing a given element. Proc. Amer. Math. Soc., 13:562–566, 1962. 1

[16] Nicolas de Saxc´e. Borelian subgroups of simple Lie groups. Duke Math. J., 166:573–604, 2017. 1

[17] Robert M. Solovay. A model of set-theory in which every set of reals is Lebesgue measurable. Ann. of Math. (2), 92:1–56, 1970. 2

[18] Hugo Steinhaus. Sur les distances des points de mesure positive. Fundamenta Mathematicae, 1 (1):93–104, 1920. 1.1

[19] Karl Stromberg. An elementary proof of Steinhaus’s theorem. Proc. Amer. Math. Soc., 36:308, 1972. 2

[20] Bodo Volkmann and Paul Erd¨os. Additive gruppen mit vorgegebener hausdorfscher dimension. Journal f¨ur die reine und angewandte Mathematik, 1966 (221):203–208, 1966. 1, 3

Mathematical institute, University of Oxford, Oxford, Oxford ox2 6gg, UK

Email address: jinhe.ye@maths.ox.ac.uk

School of mathematics, Nanjing University, Nanjing, Jiangsu 210093, People’s Republic of China

Email address: yuliang.nju@gmail.com

School of mathematics, Nanjing University, Nanjing, Jiangsu 210093, People’s Republic of China

Email address: xuanheng21@gmail.com

## Stealthy LLM-Driven Data Poisoning Atacks Against Embedding-Based Retrieval-Augmented Recommender Systems

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

## Adaptive Candidate Retrieval with Dynamic Knowledge Graph Construction for Cold-Start Recommendation

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

## RADAR: Recall Augmentation through Deferred Asynchronous Retrieval

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

## EARN: Eficient Inference Acceleration for LLM-based Generative Recommendation by Register Tokens

# EARN: Eficient Inference Acceleration for LLM-based Generative Recommendation by Register Tokens

Chaoqun Yang chaoqun@yang.email.cn Tsinghua University Beijing, China

Yongqi Li liyongqi0@gmail.com The Hong Kong Polytechnic University Hong Kong, China

Xinyu Lin<sup>∗</sup> xylin1028@gmail.com National University of Singapore Singapore, Singapore

Teng Sun stbestforever@gmail.com Shandong University Qingdao, China

Tat-Seng Chua dcscts@nus.edu.sg National University of Singapore Singapore, Singapore

Wenjie Wang<sup>∗</sup> wenjiewang96@gmail.com University of Science and Technology of China Hefei, China

Xianjing Han hanxianjing2018@gmail.com National University of Singapore Singapore, Singapore

## Abstract

Large Language Model-based generative recommendation (LLM-Rec) has achieved notable success, but it sufers from high infer ence latency due to massive computational overhead and memory pressure of KV Cache. Existing KV Cache reduction methods face critical limitations: cache compression ofers marginal acceleration given recommendation tasks’ short decoding steps, while prompt compression risks discarding vital interaction history. Through systematic analysis of attention patterns in LLMRec, we uncover two pivotal insights: 1) layer-wise attention sparsity inversion where early layers retain dense informative patterns while later layers exhibit high redundancy, and 2) dual attention sinks phenomenon where attention scores concentrate on both head and tail tokens of input sequences. Motivated by these insights, we propose EARN, an eficient inference framework that leverages the early layers to compress information into register tokens placed at the input sequence boundaries, then focuses solely on these tokens in the subsequent layers. Extensive experiments on three datasets, two LLMRec methods and two LLM architectures demonstrate EARN’s superiority, achieving up to 3.79x speedup and 80.8% KV Cache re duction with better accuracy than the general finetuning approach. Our work bridges the eficiency-efectiveness gap in LLMRec, ofer ing practical deployment advantages for industrial scenarios.

CCS Concepts • Information systems → Recommender systems.

## Keywords

LLM-based Recommendation, Inference Acceleration, KV Cache

## ACM Reference Format:

Chaoqun Yang, Xinyu Lin, Wenjie Wang, Yongqi Li, Teng Sun, Xianjing Han, and Tat-Seng Chua. 2025. EARN: Eficient Inference Acceleration for LLMbased Generative Recommendation by Register Tokens. In Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD ’25), August 3–7, 2025, Toronto, ON, Canada. ACM, New York, NY, USA, 12 pages. https://doi.org/10.1145/3711896.3736919

## KDD Availability Link:

The source code of this paper has been made publicly available at https: //doi.org/10.5281/zenodo.15553291.

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

## 2 Preliminary

## 2.1 LLM-based Generative Recommendation

In this work, we primarily discuss the LLM-based generative recommendation. The main idea of LLM-based generative recommendation is using LLMs as the core recommender model, i.e., taking the task instruction and a user’s historical interactions as the input prompt to generate item identifiers, such as typical item IDs. Formally, given a user’s historical interactions $H = \left( i _ { 1 } , \cdots , i _ { T } \right)$ in the chronological order, where $i _ { 1 }$ to <sup>??</sup>?? represent the items the user has interacted with in the past, LLM-based generative recommendation predicts the next item $i _ { T + 1 }$ the user is likely to interact with, $i . e . ,$

$$
f (H) = P (i _ {T + 1} \mid i _ {1}, \dots , i _ {T}),\tag{1}
$$

where <sup>??</sup> is the LLM, <sup>??</sup> is the probability distribution of the items.

## 2.2 Inference of LLMRec

LLM-based generative recommendation follows an auto-regressive decoding paradigm to generate item identifiers, which comprises two distinct computational stages: prefilling and decoding. Each stage exhibits unique inference characteristics and optimization requirements.

2.2.1 Prefilling. In this stage, the input prompt (containing the task instruction and the user’s historical interactions) is tokenized into the token sequence and fed into the transformer decoder. The most pivotal component is the multi-head attention module that exists in each layer of the model. Within each attention head, the input hidden states $\boldsymbol { X } \in \mathbb { R } ^ { n \times d }$ (<sup>??</sup> denotes the sequence length, and <sup>??</sup> denotes the hidden dimension) undergo linear transformations:

$$
Q = X W _ {Q}, \quad K = X W _ {K}, \quad V = X W _ {V}.\tag{2}
$$

Subsequently, the attention mechanism computes the attention output as follows:

$$
O = \text { Softmax } \left(\frac {Q K ^ {T}}{\sqrt {d}}\right) V  .\tag{3}
$$

where $O \in \mathbb { R } ^ { n \times d }$ is the attention output, ??<sup>,</sup> $K , V \in \mathbb { R } ^ { n \times d }$ correspond to query states, key states, and value states, respectively. Since the generation of subsequent tokens utilizes key states ?? and value states ?? of preceding tokens, it is common practice to cache ?? and ?? for subsequent use, i.e., KV Cache. This caching strategy is crucial for maintaining the eficiency of the inference process.

During the prefilling stage, ??, ?? and ?? are all matrices, and matrix-matrix multiplication is compute-bound, meaning that the inference speed is primarily determined by the number of floating point operations (FLOPs). Reducing the computational load can efectively accelerate the prefilling stage. For instance, shortening the input token sequence length can help decrease the quadratic computational complexity $O ( \bar { n ^ { 2 } } d )$ of the attention mechanism. Besides, a shorter token sequence also reduces the size of KV Cache, thereby contributing to accelerating the decoding stage.

2.2.2 Decoding. In this stage, subsequent tokens are generated one by one, with the KV Cache being expanded accordingly. At each decoding step <sup>??</sup>, the model first computes $Q _ { t } , K _ { t } , V _ { t } \in \mathbb { R } ^ { 1 \times d }$ then updates the KV Cache:

$$
\boldsymbol {K} _ {1: t} = \operatorname{Concat} \left(\boldsymbol {K} _ {1: t - 1}, \boldsymbol {K} _ {t}\right), \quad \boldsymbol {V} _ {1: t} = \operatorname{Concat} \left(\boldsymbol {V} _ {1: t - 1}, \boldsymbol {V} _ {t}\right).\tag{4}
$$

Next, the attention output is calculated via $Q _ { t } K _ { 1 : t } ^ { T }$

Unlike the prefilling stage, during the decoding stage, ?? is a vector, while ?? and ?? are matrices. The vector-matrix multiplication is memory-bound, meaning that the inference speed is primarily limited by the eficiency of memory access rather than the computational capacity. The latency is thus predominantly determined by the eficiency of memory access to the growing KV Cache rather than FLOPs. In other words, reducing the size of KV Cache allows the GPU computing cores to access them more rapidly, which is the key to accelerating inference in the decoding stage.

## 3 Method

In order to improve the inference eficiency while ensuring the recommendation efectiveness, we proposed EARN, which achieves inference acceleration through register tokens. The overview of our method is presented in Figure 3.

## 3.1 Register Tokens

3.1.1 Prefix Register. We introduce the prefix register, i.e., a set of learnable virtual tokens placed at the beginning of the input prompt. These tokens are designed to learn task-specific instructions, efectively signaling to the LLM that the current task is a recommendation problem. This method is inspired by the head sinks of the dual attention sinks phenomenon as elaborated in Section 1. Head sinks suggest that the head tokens can efectively divert attention away from task-irrelevant tokens in the subsequent layers. Drawing on the practice of prompt tuning [25, 26], where learnable virtual tokens are used to represent task instructions, we replace the BOS token, which the attention always sinks into, with the learnable prefix register. This substitution not only ful fills the attention-diverting function of the BOS token, but also serves the role of task indication to tell the model that this is a recommendation task.

![](images/193a2342ae4efa6a9728d5d083cf1de04e3aa6d0d760a1152df6675912fd1fbd.jpg)  
Figure 3: Overview of the proposed EARN. During training, the prefix register and the sufix register are also trainable. During inference, after layer ??, EARN removes the prompt tokens to achieve acceleration.

3.1.2 Sufix Register. We introduce the sufix register, i.e., a set of learnable virtual tokens placed at the end of the input prompt, designed to summarize historical interactions and extract key in formation. This method is inspired by the tail sinks of the dual attention sinks phenomenon as elaborated in Section 1. The final tokens in a sequence have visibility over all preceding tokens, en dowing them with summarization capabilities. Prior studies have observed that semantically meaningless tokens can efectively sum marize preceding information during LLM inference [2, 30]. The occurrence of the tail sink phenomenon in the LLMRec task further corroborates this point. Building on this insight, we place learnable virtual tokens at the end of the input prompt and leverage the first <sup>??</sup> layers of the LLM to amplify this summarization capability.

## 3.2 Overall Pipeline

3.2.1 Training. During training, we employ next token predic tion to train our model, computing the loss on the target item identifier, i.e., minimizing the negative log-likelihood loss between the predicted next-item probabilities and the ground truth items. Formally, given a chronological sequence of user interactions $H =$ $\left[ i _ { 1 } , i _ { 2 } , . . . , i _ { T + 1 } \right]$ , we construct the input sequence as:

$$
X = \left[ R _ {\mathrm{prefix}}; P r o m p t; R _ {\mathrm{suffix}} \right],\tag{5}
$$

$$
Y = \left[ i _ {T + 1} \right],\tag{6}
$$

where $R _ { \mathrm { p r e f i x } }$ and $R _ { \mathrm { s u f f i x } }$ denote the prefix register and the sufix register, respectively. <sup>??</sup>rompt is the user historical interactions $[ i _ { 1 } , i _ { 2 } , . . . , i _ { T } ]$ with the task instruction, and $Y$ is the target item identifier $i _ { T + 1 }$ . The loss function is formulated as,

$$
\mathcal {L} = - \sum_ {j = 1} ^ {| Y |} \log P (Y _ {j} \mid X, Y _ {<   j}),\tag{7}
$$

where $X$ is the input sequence of the sample, $Y$ is the corresponding item identifier, $Y _ { j }$ is the $j \cdot$ th token in the item identifier $Y ,$ and $Y _ { < j }$ denotes the tokens preceding $Y _ { j }$ in the item identifier.

When calculating the loss function, the main diference between our method and ordinary finetuning is the calculation of attention, where we exclude prompt tokens after layer <sup>??</sup>, i.e.,

• For layer $l \leq k \colon$ All tokens participate in the attention calculation.

• For layer $l > k$ : Only register and generated tokens participate in the attention calculation.

3.2.2 Inference. During inference, for a model with <sup>??</sup> layers, the generation of each token consists of two processes:

(1) Full Computation Process (First <sup>??</sup> Layers): All tokens including task instructions, user historical interactions, prefix register and sufix register participate in the model computation. The model processes the complete input sequence to establish rich contextual representations.

(2) Register-Focused Process (Remaining <sup>??</sup> − <sup>??</sup> Layers): After <sup>??</sup> layers, we remove the original prompt tokens (task instructions and historical interactions), retaining only the register tokens and newly generated tokens. The attention mechanism in subsequent layers only operates on this reduced set of tokens:

• In the prefilling stage, the input hidden state of layer <sup>??</sup> is transformed from $X = [ X _ { \mathrm { p r e f i x } } ; X _ { \mathrm { P r o m p t } } ; X _ { \mathrm { s u f f x } } ]$ to $\begin{array} { r l } { X ^ { \prime } { \mathbf \Pi } = { \mathbf \Pi } } \end{array}$ $[ X _ { \mathrm { p r e f a x } } ; X _ { \mathrm { s u f f i x } } ]$ , significantly reducing the computational load and the initial KV Cache size.

• In the decoding stage, the input hidden state of layer <sup>??</sup> is transformed from $X = [ X _ { \mathrm { p r e f i x } } ; X _ { \mathrm { P r o m p t } } ; X _ { \mathrm { s u f f i x } } ; X _ { \mathrm { g e n e r a t e d } } ]$ to $X ^ { \prime } = [ X _ { \mathrm { p r e f i x } } ; X _ { \mathrm { s u f f i x } } ; X ^ { \phantom { \prime } }$ <sub>generated</sub>], significantly reducing KV Cache that needs to be accessed during decoding.

This approach maintains the model’s ability to leverage historical information through the learned register representations while avoiding redundant computations on lengthy prompt tokens.

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

## 4.3 Eficiency Scalability (RQ2)

To investigate the eficiency scalability of EARN, we evaluate the in ference eficiency of EARN as compared to Finetune under varying batch sizes and sequence lengths.

4.3.1 Eficiency under Diferent Batch Sizes. To verify the acceleration efect of EARN under diferent batch sizes, we test the inference eficiency of EARN and Finetune with batch size in {1, 4, 8, · · · , 24} on Llama and {1, 8, 16, · · · , 48} on Qwen. As shown in Figure 4, EARN maintains significantly higher throughput than Finetune across all batch sizes. The speedup of EARN over Finetune increases as the batch size grows. Moreover, EARN can handle a larger batch size, which is particularly useful for practical scenarios. For example, on Llama, Finetune runs into out-of-memory (OOM) errors when the batch size exceeds 8, while EARN can still support larger batch sizes. The results clearly demonstrate that EARN significantly improves eficiency compared to Finetune across diferent batch sizes. Its ability to maintain high throughput on large batch sizes highlights its superior eficiency and practical inference capabilities. This makes EARN a more suitable choice for real-world applications where eficient and scalable inference is crucial.

![](images/b477e9a4f7c800b7eccc14e347a2592c1c323b697ddf2349263e397f5a197c18.jpg)

![](images/af21ecebbe390e1a39e61639bb5e8127c4fc642f204b388b594b16572f7dc3f4.jpg)  
Figure 6: Efect of register layer depth ??.

4.3.2 Eficiency under Diferent Sequence Lengths. In industrial settings, user interaction histories can be extensive. Therefore, it is essential to assess the eficiency of EARN on longer sequences. To simulate this scenario, we pad our dataset to specific lengths (1K, 5K, · · ·, 20K) to test the acceleration efects. From Figure 5, we can see EARN consistently uses significantly less KV Cache than Finetune across all sequence lengths. Moreover, the larger the sequence length, the more significant the acceleration efect, achieving a speedup of up to 7x when the sequence length is 20K on Llama. This is highly desirable in practice, especially for long-term sequential recommendation, where user historical interaction sequences are stored for a long time, thus learning user preferences comprehensively. The results clearly demonstrate that EARN significantly improves eficiency compared to Finetune across diferent sequence lengths. Its ability to maintain a low KV Cache size and achieve higher speedup, especially for longer sequences, highlights its superior eficiency and practical inference capabilities. This makes EARN a more suitable choice for real-world applications where eficient and scalable inference is crucial, particularly when dealing with long sequences.

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

## 4.5 Ablation Studies (RQ4)

To study the contribution of each component of the proposed EARN, we conduct ablation studies on the register training strategy and the register token.

4.5.1 Efect of Register Training. We first investigate the necessity of register training by comparing it with direct register inference on fully finetuned models. As shown in Table 2, models without RT sufer significant performance degradation across all metrics. Specifically for Llama with <sup>??</sup> = 7, removing RT leads to 72% relative drop in R@10 (from 0.0174 to 0.0048) and 80% reduction in N@20 (from 0.0127 to 0.0025). This demonstrates that directly applying register inference without dedicated training fails to efectively capture task-specific knowledge. With RT, both models achieve consistent improvements over Finetune. Llama with <sup>??</sup> = 7 gains 17% higher R@10 (0.0174 vs. 0.0145) and 15% better N@20 (0.0127 vs. 0.0108). This indicates that register training enables the model to summarize key information from user historical interactions into the register token.

Table 2: Ablation study of the register training (RT).

<table><tr><td>Model</td><td>k</td><td>Method</td><td>R@10</td><td>R@20</td><td>N@10</td><td>N@20</td></tr><tr><td rowspan="5">Llama</td><td></td><td>Finetune</td><td>0.0145</td><td>0.0225</td><td>0.0084</td><td>0.0108</td></tr><tr><td rowspan="2">7</td><td>EARN</td><td>0.0174</td><td>0.0273</td><td>0.0098</td><td>0.0127</td></tr><tr><td>w/o RT</td><td>0.0048</td><td>0.0060</td><td>0.0021</td><td>0.0025</td></tr><tr><td rowspan="2">15</td><td>EARN</td><td>0.0168</td><td>0.0286</td><td>0.0093</td><td>0.0127</td></tr><tr><td>w/o RT</td><td>0.0053</td><td>0.0083</td><td>0.0029</td><td>0.0038</td></tr><tr><td rowspan="5">Qwen</td><td></td><td>Finetune</td><td>0.0145</td><td>0.0248</td><td>0.0087</td><td>0.0117</td></tr><tr><td rowspan="2">7</td><td>EARN</td><td>0.0155</td><td>0.0265</td><td>0.0091</td><td>0.0122</td></tr><tr><td>w/o RT</td><td>0.0074</td><td>0.0093</td><td>0.0044</td><td>0.0050</td></tr><tr><td rowspan="2">13</td><td>EARN</td><td>0.0156</td><td>0.0263</td><td>0.0098</td><td>0.0129</td></tr><tr><td>w/o RT</td><td>0.0072</td><td>0.0095</td><td>0.0043</td><td>0.0050</td></tr></table>

Table 3: Ablation study of the prefix register (PR) and the sufix register (SR).

<table><tr><td>Model</td><td>k</td><td>Method</td><td>R@10</td><td>R@20</td><td>N@10</td><td>N@20</td></tr><tr><td rowspan="6">Llama</td><td rowspan="3">7</td><td>EARN</td><td>0.0174</td><td>0.0273</td><td>0.0098</td><td>0.0127</td></tr><tr><td>w/o PR</td><td>0.0172</td><td>0.0252</td><td>0.0108</td><td>0.0132</td></tr><tr><td>w/o SR</td><td>0.0041</td><td>0.0075</td><td>0.0021</td><td>0.0031</td></tr><tr><td rowspan="3">15</td><td>EARN</td><td>0.0168</td><td>0.0286</td><td>0.0093</td><td>0.0127</td></tr><tr><td>w/o PR</td><td>0.0166</td><td>0.0260</td><td>0.0103</td><td>0.0131</td></tr><tr><td>w/o SR</td><td>0.0074</td><td>0.0119</td><td>0.0035</td><td>0.0047</td></tr><tr><td rowspan="6">Qwen</td><td rowspan="3">7</td><td>EARN</td><td>0.0155</td><td>0.0265</td><td>0.0091</td><td>0.0122</td></tr><tr><td>w/o PR</td><td>0.0153</td><td>0.0217</td><td>0.0097</td><td>0.0116</td></tr><tr><td>w/o SR</td><td>0.0044</td><td>0.0071</td><td>0.0023</td><td>0.0031</td></tr><tr><td rowspan="3">13</td><td>EARN</td><td>0.0156</td><td>0.0263</td><td>0.0098</td><td>0.0129</td></tr><tr><td>w/o PR</td><td>0.0153</td><td>0.0230</td><td>0.0102</td><td>0.0124</td></tr><tr><td>w/o SR</td><td>0.0065</td><td>0.0106</td><td>0.0036</td><td>0.0049</td></tr></table>

4.5.2 Efect of Prefix Register and Sufix Register. We further dissect the contribution of the prefix register and the sufix reg ister through component-wise ablation. Table 3 reveals three key observations: 1) Sufix register dominates performance: Removing the sufix register (w/o SR) causes significant performance collapse for both Llama and Qwen. This confirms our design intuition that summarizing historical interactions in the sufix register is crucial for recommendation tasks. 2) Prefix register enhances task awareness: Though not as severe as removing the sufix register (w/o SR), removing the prefix register (w/o PR) still leads to a certain degree of performance degradation. This suggests the prefix register efec tively primes the model for recommendation task identification. 3) Layer-depth interaction: The impact of removing the sufix register is more pronounced in the lower layers (e.g., <sup>??</sup> = 7 exhibits a greater performance drop than <sup>??</sup> = 15 on Llama), indicating that the sufix register plays a more significant summarization role in the lower layers. The lower layers rely more heavily on the compressed historical interaction information encoded in the sufix register.

## 5 Related Work

Inference Acceleration of LLMRec. While LLM-based generative recommendations have shown remarkable performance [10, 16, 20–22, 36, 38], their practical application is hindered by high inference latency [12, 37, 44]. To tackle this issue, various research has been proposed. Several techniques leverage knowledge distillation to transfer comprehensible knowledge [4] or abstract knowledge [33] from a teacher LLM to a smaller student language model. Additionally, some methods apply speculative decoding to achieve lossless decoding acceleration [23, 39]. Besides, some approaches attempt to design eficient attention mechanisms to reduce computational complexity, such as sparse attention [6], linear attention [24], and slimming architecture [19].

KV Cache Reduction. It’s common practice to utilize KV Cache to reduce redundant computations during LLM inference. However, the use of KV Cache introduces new challenges. KV Cache will increase linearly with the length of the sequence, and the memory required will become larger and larger. To address this challenge, diverse methods have been proposed to reduce KV Cache, including two primary groups of work, i.e., prompt compression and cache compression. Prompt compression reduces the initial KV Cache size during prefilling by shortening the input token sequence. Hard compression methods like SelectiveContext [14] and LLMLingua [9] filter redundant tokens while preserving natural language syntax, albeit at the cost of fluency. Soft compression techniques, such as AutoCompressor [3] and 500xCompressor [18], encode prompts into dense latent tokens, achieving higher compression ratios but sacrificing human interpretability. Cache compression reduces KV cache during decoding. Existing work employs eviction or merging strategies. Evict-based methods like StreamingLLM [40] and SnapKV [15] selectively evict less important KV Cache through specific rules. Merge-based approaches (e.g., CAM [42] and DMC [29]) adaptively merge to-be-evicted caches into the remaining ones.

## 6 Conclusion

In this work, we address the critical challenge of inference eficiency in LLM-based recommendation systems (LLMRec), where the massive computational overhead and memory pressure of KV Cache severely hinders practical deployment. Through systematic analysis of LLMRec’s attention patterns, we identify two pivotal characteristics: 1) layer-wise attention sparsity inversion, where in early layers retain dense informative patterns while later layers exhibit high redundancy, and 2) the dual attention sinks phenomenon, where attention scores concentrate on both head and tail tokens of input sequences. These insights motivate our proposed EARN method, which introduces prefix and sufix register tokens to compress task instructions and user interaction histories, implementing layer-wise computation pruning. EARN achieves an 80% reduction of KV Cache while maintaining essential information integrity. Extensive experiments conducted on three benchmark datasets and two distinct LLM architectures reveal that our EARN attains 3.79x inference acceleration with superior accuracy compared to conventional finetuning approaches. This breakthrough efectively reconciles the longstanding trade-of between inference eficiency and recommendation quality in LLMRec, presenting tangible deployment benefits for industrial-scale recommendation services.

## References

[1] Beidi Chen, Tri Dao, Eric Winsor, Zhao Song, Atri Rudra, and Christopher Ré. 2021. Scatterbrain: Unifying sparse and low-rank attention. Advances in Neural Information Processing Systems 34 (2021), 17413–17426.

[2] Guoxuan Chen, Han Shi, Jiawei Li, Yihang Gao, Xiaozhe Ren, Yimeng Chen, Xin Jiang, Zhenguo Li, Weiyang Liu, and Chao Huang. 2024. SepLLM: Accelerate large language models by compressing one segment into one separator. arXiv preprint arXiv:2412.12094 (2024).

[3] Alexis Chevalier, Alexander Wettig, Anirudh Ajith, and Danqi Chen. 2023. Adapt ing language models to compress contexts. In Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing. 3829–3846.

[4] Yu Cui, Feng Liu, Pengbo Wang, Bohao Wang, Heng Tang, Yi Wan, Jun Wang, and Jiawei Chen. 2024. Distillation matters: empowering sequential recommenders to match the performance of large language models. In Proceedings of the 18th ACM Conference on Recommender Systems. 507–517.

[5] Yichuan Deng, Zhao Song, Jing Xiong, and Chiwun Yang. 2024. How Sparse Attention Approximates Exact Attention? Your Attention is Naturally <sup>??</sup> -Sparse. arXiv preprint arXiv:2404.02690 (2024).

[6] Xinyan Fan, Zheng Liu, Jianxun Lian, Wayne Xin Zhao, Xing Xie, and Ji-Rong Wen. 2021. Lighter and better: low-rank decomposed self-attention networks for next-item recommendation. In Proceedings of the 44th International ACM SIGIR Conference on Research and Development in Information Retrieval. 1733–1737.

[7] Xiangming Gu, Tianyu Pang, Chao Du, Qian Liu, Fengzhuo Zhang, Cunxiao Du, Ye Wang, and Min Lin. 2025. When attention sink emerges in language models: An empirical view. In The 13th International Conference on Learning Representations.

[8] Dan Hendrycks, Collin Burns, Steven Basart, Andy Zou, Mantas Mazeika, Dawn Song, and Jacob Steinhardt. 2021. Measuring massive multitask language under standing. In The 9th International Conference on Learning Representations.

[9] Huiqiang Jiang, Qianhui Wu, Chin-Yew Lin, Yuqing Yang, and Lili Qiu. 2023. LLMLingua: Compressing prompts for accelerated inference of large language models. In Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing. 13358–13376.

[10] Sein Kim, Hongseok Kang, Seungyoon Choi, Donghyun Kim, Minchul Yang, and Chanyoung Park. 2024. Large language models meet collaborative filtering: An eficient all-round LLM-based recommender system. In Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining. 1395–1406.

[11] Lei Li, Yongfeng Zhang, and Li Chen. 2023. Prompt distillation for eficient LLM based recommendation. In Proceedings of the 32nd ACM International Conference on Information and Knowledge Management. 1348–1357.

[12] Lei Li, Yongfeng Zhang, Dugang Liu, and Li Chen. 2024. Large language models for generative recommendation: A survey and visionary discussions. In Proceedings of the 2024 Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING 2024). 10146–10159.

[13] Pengxiang Li, Lu Yin, and Shiwei Liu. 2025. Mix-LN: Unleashing the power of deeper layers by combining Pre-LN and Post-LN, In The 13th Internationa Conference on Learning Representations. arXiv preprint arXiv:2412.13795

[14] Yucheng Li, Bo Dong, Frank Guerin, and Chenghua Lin. 2023. Compressing context to enhance inference eficiency of large language models. In Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing. 6342–6353.

[15] Yuhong Li, Yingbing Huang, Bowen Yang, Bharat Venkitesh, Acyr Locatelli, Hanchen Ye, Tianle Cai, Patrick Lewis, and Deming Chen. 2024. SnapKV: LLM knows what you are looking for before generation. Advances in Neural Information Processing Systems 37 (2024), 22947–22970.

[16] Yongqi Li, Xinyu Lin, Wenjie Wang, Fuli Feng, Liang Pang, Wenjie Li, Liqiang Nie, Xiangnan He, and Tat-Seng Chua. 2024. A survey of generative search and recom mendation in the era of large language models. arXiv preprint arXiv:2404.16924 (2024).

[17] Zongqian Li, Yinhong Liu, Yixuan Su, and Nigel Collier. 2024. Prompt compression for large language models: A survey. In Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers). 7182–7195.

[18] Zongqian Li, Yixuan Su, and Nigel Collier. 2024. 500xCompressor: Generalized prompt compression for large language models. arXiv preprint arXiv:2408.03094 (2024).

[19] Jianghao Lin, Xinyi Dai, Rong Shan, Bo Chen, Ruiming Tang, Yong Yu, and Weinan Zhang. 2025. Large language models make sample-eficient recommender systems. Frontiers of Computer Science 19, 4 (2025), 194328.

[20] Jianghao Lin, Xinyi Dai, Yunjia Xi, Weiwen Liu, Bo Chen, Hao Zhang, Yong Liu, Chuhan Wu, Xiangyang Li, Chenxu Zhu, et al. 2025. How can recommender systems benefit from large language models: A survey. ACM Transactions on Information Systems 43, 2 (2025), 1–47.

[21] Xinyu Lin, Wenjie Wang, Yongqi Li, Fuli Feng, See-Kiong Ng, and Tat-Seng Chua. 2024. Bridging items and language: A transition paradigm for large language model-based recommendation. In Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining. 1816–1826.

[22] Xinyu Lin, Wenjie Wang, Yongqi Li, Shuo Yang, Fuli Feng, Yinwei Wei, and Tat-Seng Chua. 2024. Data-eficient fine-tuning for LLM-based recommendation. In Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval. 365–374.

[23] Xinyu Lin, Chaoqun Yang, Wenjie Wang, Yongqi Li, Cunxiao Du, Fuli Feng, See-Kiong Ng, and Tat-Seng Chua. 2025. Eficient inference for large language model-based generative recommendation. In The 13th International Conference on Learning Representations.

[24] Langming Liu, Liu Cai, Chi Zhang, Xiangyu Zhao, Jingtong Gao, Wanyu Wang, Yifu Lv, Wenqi Fan, Yiqi Wang, Ming He, et al. 2023. Linrec: Linear attention mechanism for long-term sequential recommender systems. In Proceedings of the 46th International ACM SIGIR Conference on Research and Development in Information Retrieval. 289–299.

[25] Xiao Liu, Kaixuan Ji, Yicheng Fu, Weng Tam, Zhengxiao Du, Zhilin Yang, and Jie Tang. 2022. P-tuning v2: Prompt tuning can be comparable to fine-tuning universally across scales and tasks. In Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers). 61–68.

[26] Xiao Liu, Yanan Zheng, Zhengxiao Du, Ming Ding, Yujie Qian, Zhilin Yang, and Jie Tang. 2024. GPT understands, too. AI Open 5 (2024), 208–215.

[27] Shi Luohe, Hongyi Zhang, Yao Yao, Zuchao Li, et al. 2024. Keep the cost down: A review on methods to optimize LLM’s KV-Cache consumption. In The 1st Conference on Language Modeling (COLM).

[28] Jesse Mu, Xiang Li, and Noah Goodman. 2023. Learning to compress prompts with gist tokens. Advances in Neural Information Processing Systems 36 (2023), 19327–19352.

[29] Piotr Nawrot, Adrian Łańcucki, Marcin Chochowski, David Tarjan, and Edoardo M Ponti. 2024. Dynamic memory compression: retrofitting LLMs for accelerated inference. In The 41st International Conference on Machine Learning. 37396–37412.

[30] Jianhui Pang, Fanghua Ye, Derek Wong, Xin He, Wanshun Chen, and Longyue Wang. 2024. Anchor-based large language models. In Findings of the Association for Computational Linguistics. 4958–4976.

[31] Shashank Rajput, Nikhil Mehta, Anima Singh, Raghunandan Hulikal Keshavan, Trung Vu, Lukasz Heldt, Lichan Hong, Yi Tay, Vinh Tran, Jonah Samost, et al. 2023. Recommender systems with generative retrieval. Advances in Neural Information Processing Systems 36 (2023), 10299–10315.

[32] Zhenmei Shi, Yifei Ming, Xuan-Phi Nguyen, Yingyu Liang, and Shafiq Joty. 2024. Discovering the gems in early layers: Accelerating long-context LLMs with 1000x input token reduction. arXiv preprint arXiv:2409.17422 (2024).

[33] Wenqi Sun, Ruobing Xie, Junjie Zhang, Wayne Xin Zhao, Leyu Lin, and Ji-Rong Wen. 2024. Distillation is all you need for practically using diferent pre-trained recommendation models. arXiv preprint arXiv:2401.00797 (2024).

[34] Qwen Team. 2024. Qwen2.5: A party of foundation models. https://qwenlm. github.io/blog/qwen2.5

[35] Hugo Touvron, Thibaut Lavril, Gautier Izacard, Xavier Martinet, Marie-Anne Lachaux, Timothée Lacroix, Baptiste Rozière, Naman Goyal, Eric Hambro, Faisal Azhar, et al. 2023. Llama: Open and eficient foundation language models. arXiv preprint arXiv:2302.13971 (2023).

[36] Wenjie Wang, Xinyu Lin, Fuli Feng, Xiangnan He, and Tat-Seng Chua. 2023. Generative recommendation: Towards next-generation recommender paradigm. arXiv preprint arXiv:2304.03516 (2023).

[37] Haotian Wu, Yingpeng Du, Zhu Sun, Tianjun Wei, Jie Zhang, and Ong Yew Soon. 2024. A survey on eficient solutions of large language models for recommenda tion. Authorea Preprints (2024).

[38] Likang Wu, Zhi Zheng, Zhaopeng Qiu, Hao Wang, Hongchao Gu, Tingjia Shen, Chuan Qin, Chen Zhu, Hengshu Zhu, Qi Liu, et al. 2024. A survey on large language models for recommendation. World Wide Web 27, 5 (2024), 60.

[39] Yunjia Xi, Hangyu Wang, Bo Chen, Jianghao Lin, Menghui Zhu, Weiwen Liu, Ruiming Tang, Weinan Zhang, and Yong Yu. 2025. Eficiency unleashed: Inference acceleration for LLM-based recommender systems with speculative decoding. arXiv preprint arXiv:2408.05676 (2025).

[40] Guangxuan Xiao, Yuandong Tian, Beidi Chen, Song Han, and Mike Lewis. 2024. Eficient streaming language models with attention sinks. In The 12th International Conference on Learning Representations.

[41] Jiaqi Zhai, Lucy Liao, Xing Liu, Yueming Wang, Rui Li, Xuan Cao, Leon Gao, Zhaojie Gong, Fangda Gu, Jiayuan He, et al. 2024. Actions speak louder than words: trillion-parameter sequential transducers for generative recommendations. In The 41st International Conference on Machine Learning. 58484–58509.

[42] Yuxin Zhang, Yuxuan Du, Gen Luo, Yunshan Zhong, Zhenyu Zhang, Shiwei Liu, and Rongrong Ji. 2024. CaM: Cache merging for memory-eficient LLMs inference. In The 41st International Conference on Machine Learning. 58840–58850.

[43] Bowen Zheng, Yupeng Hou, Hongyu Lu, Yu Chen, Wayne Xin Zhao, Ming Chen, and Ji-Rong Wen. 2024. Adapting large language models by integrating collaborative semantics for recommendation. In 2024 IEEE 40th International Conference on Data Engineering (ICDE). 1435–1448.

[44] Zixuan Zhou, Xuefei Ning, Ke Hong, Tianyu Fu, Jiaming Xu, Shiyao Li, Yuming Lou, Luning Wang, Zhihang Yuan, Xiuhong Li, et al. 2024. A survey on eficient inference for large language models. arXiv preprint arXiv:2404.14294 (2024).

## A Appendix

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

## A.2 Computational Complexity of LLM

For a decoder-only LLM with <sup>??</sup> decoder layers, the computational operations comprise three components: embedding, <sup>??</sup> stacked decoder layers, and de-embedding. Since embedding and de-embedding mainly involve lightweight lookup and projection steps, the computational bottleneck lies in the decoder layers. Specifically, each decoder layer consists of two core components: Multi-Head Attention (MHA) and Feed-Forward Network (FFN), whose FLOPs are analyzed as follows:

Multi-Head Attention (MHA). Let <sup>??</sup> denote the sequence length, $d _ { h }$ the hidden dimension, $d _ { a }$ the attention head dimension, and $n _ { h }$ the number of attention heads. We approximate the FLOPs of matrix multiplication $X ^ { L \times d _ { h } } \times W ^ { d _ { h } \times d _ { a } }$ as $2 L d _ { h } d _ { a }$ . For a single attention head, the FLOPs include: 1) Projections for ??, ?? and $V \colon 2 L d _ { h } d _ { a } \times 3 = 6 L d _ { h } d _ { a } ; 2 )$ Attention computation for $Q K ^ { T }$ and $( \cdot ) V \colon 2 L ^ { 2 } d _ { a } + 2 L ^ { 2 } d _ { a } = 4 L ^ { 2 } d _ { a }$ . Aggregating across $n _ { h }$ heads, plus $2 L n _ { h } d _ { a } d _ { h }$ FLOPs of the final output projection, the total MHA FLOPs per decoder layer are:

$$
F L O P s _ {M H A} = n _ {h} (8 L d _ {h} d _ {a} + 4 L ^ {2} d _ {a}).\tag{16}
$$

Feed-Forward Network (FFN). The FFN module involves two projections with intermediate dimension $d _ { f } \mathbf { \cdot } \mathbf { 1 } )$ Up-projection: $2 L d _ { h } d _ { f } ;$ 2) Down-projection: $2 L d _ { f } d _ { h }$ . This yields total FFN FLOPs of:

$$
F L O P s _ {F F N} = 4 L d _ {h} d _ {f}.\tag{17}
$$

Total FLOPs. Combining both components, the FLOPs for a single decoder layer are:

$$
\begin{array}{r} F L O P s _ {L L M l a y e r} = n _ {h} (8 L d _ {h} d _ {a} + 4 L ^ {2} d _ {a}) + 4 L d _ {h} d _ {f} \\ = 4 L [ n _ {h} d _ {a} (2 d _ {h} + L) + d _ {h} d _ {f} ]. \end{array}\tag{18}
$$

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
S: \mathcal {T} \times (\mathcal {X} \times \widetilde {\mathcal {X}} \times \mathbb {R} ^ {3}) \longrightar
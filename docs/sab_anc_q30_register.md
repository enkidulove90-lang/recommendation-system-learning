# SAB-ANC × Hi-SAM 原型验证 · 30 项未决问题逐条裁定记录（Q30 Register）

生成日期：2026-11-10
版本：v1.0（对应外部方案文本 v5 的 30 项问卷全部封闭）
权威声明：本文件数值冲突时，以 `sab_anc_params.md`（Decision Record v1.4，提交 b4bdbc7）为唯一权威；外部 v5 文本与 params 冲突之处按 params §11 仲裁规则处理，并在 §G 全局更正区登记。
配套文档：`sab_anc_design.md`（v1.1–v1.4 修订）、`sab_anc_params.md`（v1.0→v1.4）。

---

## 〇、历史版本链（所有裁定的演化背景）

| 提交 | 版本 | 内容 |
|---|---|---|
| e73bb41 | 设计 v1.0 | SAB-ANC 设计基线（SASRec×BLIP-2 锚定下游） |
| dfe9868 | params v1.0 | Decision Record 初版 + fetch_mm_data.py "CLIP-ViT 4096" 错误注释纠错 |
| f94be5c | params v1.1 | 按论文原文定值 Eq.1/PSGR；数据基准切到 MMSSL Baby；切分铁律修正 |
| 14f7ac7 | params v1.2 | 三项裁决封闭：三模态 behavioral / 动作头关闭 / 路径 A 拍板；偏差登记册 D1–D11；闸门-0 |
| fe567f3 | params v1.3 | hidden=512 成本重估；4 维辅助特征 train-only 统计锁死 |
| b4bdbc7 | params v1.4 | 吸收外部 v4 三点（D11 补强 / patience 语义 / 负向审计放宽）；§11 十项对照映射 |

每项裁定下方的"历史记录"均引用上述链条中的具体决策节点。

---

## G. 全局更正区（v5 文本与仓库权威的冲突，先于 30 项声明）

### G1. 切分协议冲突（影响第 7 题）

v5 §4.1 写"全局交互时间切分、按 unixReviewTime 排序、时间窗 start 2018-01-01"。**仓库实测（params §4.1，2026-11-10）证明该口径不可执行**：Baby 数据每行是纯 `user_id + item 序列`，**无任何绝对时间戳**，unixReviewTime 字段根本不存在。

params §4.2（v1.1 铁律修正）已裁决：直接使用 MMSSL 自带的 `train/valid/test` 三份文件（per-user chronological holdout，前缀训练/后段验证测试，序列推荐标准协议）。v1.0 "per-user 必泄漏"的过强论断同时修正——泄漏来自随机切，不来自 per-user 本身。

副作用（有利）：MMSSL/MSCA/MMRec 已发表结果在同一划分上，数字可直接同表对标。

### G2. 交互规模数字（影响第 4 题）

v5 偏差登记册 D4 写"本地 2.1 万交互"。**实测（params §4.1）：train 190,930 + valid 37,899 + test 67,508 ≈ 29.6 万交互**，35,598 用户 / 18,357 物品。报告中以实测表为准；与工业集 521M 的规模偏离结论不变，但量级须写对。

### G3. 特征文件未落盘（影响第 3、5 题）

2026-11-10 磁盘核查：全仓**无任何 .npy 特征文件**。image_feat.npy / text_feat.npy 需先跑 `fetch_mm_data.py` 从 HKUDS/MMSSL Google Drive（folder `1AB1RsnU-ETmubJgWLpJrXd8TjaK_eTp0`）拉取；脚本是 P0 第 1 步，Drive 可能触发配额限制。

---

## 一、目标与论文（Q1–Q3）

### Q1. 目标定位

- **裁定**：不是严格复现。定位 = "结构复现 + 条件偏离下的小规模原型验证"（v5 §1.1）。保留链路：CGA 几何对齐 → Φ_fuse → 共享残差量化 RQ → PSGR + 模态特定码本 → vCLUB → 联合损失。三个创新点（Eq.1 几何对齐、RQ/PSGR 量化、[ANC] 结构锚定）均不依赖 BLIP-2 与动作头。
- **历史记录**：该定位在 e73bb41（设计基线）即确立"不追求复现 Hi-SAM 完整实验"；v1.2（14f7ac7）三项裁决进一步把偏离封闭为可声明项（D1–D11）。v5 把"作废项"明确化：Table 2 绝对数值仅参照；外部基线 WuKong/HSTU/MTGR/QARM/PSRQ+MCCA/DLRM 不复现；8×A100/ZeRO-2/batch128 论文级训练配置不适用。
- **状态**：已封闭。

### Q2. 论文、代码与口径确认

- **裁定**：论文 = Hi-SAM.pdf（arXiv:2602.11799v2, KDD 2026），已在知识库，公式与数据集口径经论文原文逐条核实。官方代码**不存在**，按 from-scratch 处理（风险表 §13.5）。具体已核实项：Eq.1 对称对比形式（Vol=√det(G) 入 e^{-Vol/τ} softmax，非 det 对数/体积比）；CGA 的 `d=256`（"CGAd"是本方杜撰符号，params §9 变更记录已弃用）；PSGR 输入 = 残差 + z_j semantic probe；数据集裁决为 MMSSL Baby。
- **历史记录**：f94be5c（v1.1）整版就是"按论文原文定值"的产物——Eq.1 旧描述"双向 Gram 体积对齐"被论文原文推翻；PSGR 输入旧设想"用户/物品表征拼接"被推翻。这些都登记在 params §9 变更记录首三行。
- **状态**：已封闭。

### Q3. 数据实际位置与内容

- **裁定**：数据在 **experiments 分支 `baseline/LightGCNpp/data/amazon-baby-mmssl/`**，仅 `train/valid/test.txt` 三份（磁盘已验证；`.worktrees/sab-anc-design` worktree 内同套）。另有 `_imgonly`/`_txtonly` 两个消融变体目录。每行格式 `user_id item_id ...`（每行一个用户序列）。**特征 .npy 目前不存在**（见 G3），P0 第 1 步必须先跑 `fetch_mm_data.py`。
- **历史记录**：数据来源判定本身是一段考证史——`fetch_mm_data.py` 注释记载：本仓库 `amazon-sports` 目录的统计（35,598 用户/18,357 物品）实为 MMSSL **Amazon-Baby**（真 Sports 仅 7,050 物品），故拉取目标是 MMSSL Baby 子目录，特征行序与现有 item id 天然对齐。
- **状态**：已封闭；拉特征待 P0 执行。

## 二、数据 schema 与特征（Q4–Q6）

### Q4. 数据集身份与 schema

- **裁定**：**不是 Amazon 2023 Movies&TV/Books**，是 MMSSL Amazon-Baby（2014 版）。实测 schema（params §4.1）：35,598 用户 / 18,357 物品 / train 190,930 交互（avg 5.4，min 3，max 207）；无第三列、无 rating、无 verified_purchase、无 timestamp、无类别/品牌字段。train item 频次分布：min 1 / p25 4 / median 6 / p75 11 / p90 21 / max 686。
- **历史记录**：v1.0 曾按 Amazon-2023 假设写设计（D3），v1.1 实测后整体切基准（params §9：数据集行"Amazon-2023 → MMSSL Baby"）。"2.1 万交互"（v5 D4）为笔误，见 G2。
- **状态**：已封闭。

### Q5. 封面图 / meta / BLIP-2 特征

- **裁定**：封面图、title/category/brand、BLIP-2 视觉文本特征**全部没有**（D1/D10，[CAT_i]/[BRD_i] token 已删除）。特征口径：`image_feat.npy` = **CNN 4096 维**（不是 CLIP，更不是 BLIP-2）；`text_feat.npy` = sentence-transformers（MMSSL 发布档署 1024，MARGO/2504.16524 对同源 Baby 记 384，两版本并存，以 P0 load shape 回填为准）。全仓唯一 CLIP = PRISM 的 ViT-B/32（512 维，`PRISM/data/process_clip.py`），非本方案主特征。
- **历史记录**：4096 维归属曾写错——`fetch_mm_data.py:12` 旧注释称"CLIP-ViT 4096"，经三方证据核实为 CNN：`prep_amazon_sports.py:9`（"[n_items,4096] CNN 特征(MMSSL 维度)"）、`baseline/prism_analysis.md:353`（"image_feat(4096, CNN)"）、仓库内 MARGO 论文 2504.16524 原文（"the image feature is a 4096-dimensional vector extracted by a CNN model"）。dfe9868 提交完成纠错，params §9 专列一行"4096 禁止称 CLIP"。特征生成脚本 = `fetch_mm_data.py`（gdown 整夹下载 MMSSL 发布档）。
- **状态**：口径已封闭；实际 shape 待 P0 回填。

### Q6. SASRec 行为特征的来源与隔离

- **裁定**：**无现成 checkpoint/特征，需重训**。结构：hidden 512 / layers 2 / max_len 50；目标 next-item CE（负采样 1:1）。隔离铁律：SASRec 只见 `train.txt` 序列（MMSSL 三份文件即 per-user 时间后段划分，见 G1），valid/test 项对其完全不可见；冻结后输出 (a) 近 K=5 步 mean-pool 隐状态 h_beh，(b) item embedding 矩阵。下游与上游共享同一份 train 文件但物理分离早停 valid。
- **历史记录**：v1.2（14f7ac7）裁决第三模态 = behavioral 时同步确定"SASRec hidden=512 使 behavioral 输入维与论文 d=512 一致"（params §9 变更记录"SASRec hidden 64–128 → 512"行）；v1.3（fe567f3）对 512 做成本重估并修正 v1.2 的"2–3 倍/1–2h"为 128 维口径误用（重估见 Q26）。入口复用 `baseline/PRISM/SASRec.py` 骨干，另抽取 `code/extract_sasrec_feat.py`。
- **状态**：已封闭；重训在 P1。

## 三、切分与采样（Q7–Q10）

### Q7. 切分方式、验证比例与边界日期

- **裁定**：**采用 MMSSL 自带三份文件 = per-user chronological holdout（前缀/后段）**，验证比例即文件自带比例。v5 §4.1 的"全局 unixReviewTime 切分 + 时间窗 2018-01-01"不可执行（无时间戳），按 G1 更正登记。报告必须写"per-user chronological holdout，非全局时间切分"，不得声称全局切分。
- **历史记录**：这是本次 30 项中最重要的历史演化——v1.0 铁律原文"全局时间切分、per-user 必泄漏"；v1.1 实测发现数据无绝对时间戳后整条推翻（params §4.2 对照表两行："全局 80/10/10 → 不可用"；"per-user 一律判泄漏 → 过于笼统，per-user 随机切才泄漏"）。5k item 子集抽取后无需重切（文件级划分不变，子集只是筛行）。
- **状态**：已封闭（以 params §4.2 为准）。

### Q8. "rating>3 为正"是否适用

- **裁定**：**不适用**——无 rating 字段（D5）。正负例由 MMSSL 文件划分直接给出；不存在显式低分负例，需负采样（见 Q9）。原"rating/verified 保留为辅助输入"的设想不可执行，改为 4 维可计算代理特征（log1p(item_train_freq) / repeat_flag / pos_ratio / log1p(seq_len)），MLP(4→16) 后加到 [BEH_1] 上；**禁命名 [ACT_*]**，报告须写明"行为语义代理，非论文动作模态"。
- **历史记录**：v1.0 曾拟"保留 rating/verified 为辅助"；2026-11-10 实测目录无 meta、序列无第三列后判死刑（params §9："拟保留为辅助特征 → 不可执行 → 改 4 维可计算辅助特征"）。v1.3（fe567f3）进一步把 4 维特征的统计范围逐维锁死 train-only：A1 频次表冻结(+sha256)、A2 repeat_flag 构造上因果、A3 分母=train 前缀长、A4 只算 train 段；归一化常数只在 train 算一次 → `configs/aux_norm.json` 随 ckpt 校验（ckpt 的 aux_stats_hash 不符直接拒绝运行）。
- **状态**：已封闭。

### Q9. 负采样参数

- **裁定**（§4.4 + §11#6）：train-only 候选池 / in-batch + 4 / **≥256 硬下限** / uniform 为主（不按流行度）/ 派生种子 + neg_hash 固定可复现。
- **历史记录**：params §9 变更记录"β/λ 网格 9 格全跑 → 先扫两端"体现同一预算哲学；负采样五元组在 params v1.0（dfe9868）即定，v1.2–v1.4 未动，属最早封闭的一批。
- **状态**：已封闭。

### Q10. 冷启动口径

- **裁定**：三分桶（§4.3）——**cold-item = item freq ≤5（主结论只落此桶）**；cold-user = seq len ≤3；warm-item = 其余。不采用 <10。物品冷启单列评估；强制 7 行模态消融 V/T/B/VT/VB/TB/VTB（R11 唯一有效防线）；cold-item 频次必须按冻结表（aux_freq_table）计算，不得用重算值。
- **历史记录**：params §9"评估口径：总体均值 → warm/cold-item/cold-user 三分开，主结论在 cold-item（论文 Cold AUC 叙事）"。v1.0 曾把 5k 抽取"按用户分层"，v3 裁决改为按 item 分层且五层配额（L1 c∈[1,3] … L5 c∈[22,∞]），验收线：交互保留率 ≥55%、用户保留 ≥20,000、序列长分布 KS p>0.05。
- **状态**：已封闭。

## 四、模态与上游结构（Q11–Q19）

### Q11. 是否必须完整三模态 / 双模态合成机制

- **裁定**：**必须完整三模态**（V/T/B，N_m=3 对齐论文 = visual/textual/behavioral；第三模态 = SASRec item embedding d=512，码本 6 组 = 3 共享 + 3 特定）。双模态即 7 行消融中的 5 行，**不存在"合成机制"**。
- **历史记录**：v1.0 假设 Baby 仅两路模态、N_m 降级待定；v1.2（14f7ac7）裁决 behavioral 补位后 N_m/码本组数行改为"3 / 6 组"。params §2.5 同步登记 behavioral 模态两个固有风险（ID 空间语义 vs 内容空间、embedding 由本方训练自举），必须写进报告。
- **状态**：已封闭。

### Q12. 合成数据

- **裁定**：**不做合成数据**。真值机制/噪声水平/样本量/相关性参数/成功阈值均无定义需求。
- **历史记录**：四个可证伪问题（v5 §8）承担了"机制是否成立"的验证职能（CGA 对齐几何中心 / 共享-特定码本分工 / vCLUB 解耦 / [ANC] 汇聚），闸门即成功阈值，无需合成数据。
- **状态**：已封闭。

### Q13. L_D2A / L_A2D 实现

- **裁定**：**已由论文原文确认**，无未公开问题——L_align = (L_D2A + L_A2D)/2 对称对比；Vol = √det(G) 入 e^{-Vol/τ} softmax；优先完整 Eq.1，纯体积最小化仅降级备选。实现规格（params §2.1–2.2）：slogdet + jitter 1e-6 数值稳定；B×B Vol 矩阵一次算完。
- **历史记录**：f94be5c（v1.1）旧描述"双向 Gram 体积对齐（描述性）"被论文原式取代，params §9 首行登记。
- **状态**：已封闭。

### Q14. Φ_fuse 默认与消融

- **裁定**：**mean 主，attention 仅消融**；升级判据写死（attention 提升需 >1 seed std 且 ≥2/3 消融组同向，才允许升级为主方案）。
- **历史记录**：params §3.1（v1.0 拍板四项之一），v1.4 §11#2 复确认。
- **状态**：已封闭。

### Q15. PSGR q_proj 结构

- **裁定**：2 层 MLP 256→256→256 GELU+LN，**全头共享，k/v 独立**；输入 = 残差 r_{N_sh} + z_j semantic probe（q 输入维 = d=256）。属自定实现（论文仅锚定输入与维度），报告须明确标注。
- **历史记录**：v1.0 曾考虑"用户/物品表征拼接"，f94be5c 按论文原文推翻（params §9："PSGR 输入 → 残差 + z_j probe"）；q_proj 结构在 params §3.2 拍板。
- **状态**：已封闭。

### Q16. H=4 与 H=8

- **裁定**：**H=4 默认主结果，H=8 必做消融**。两版都跑，主结论以 H=4 落表。
- **历史记录**：源于论文正文/附录矛盾（正文 H=4，附录 H=8），params §1/§2.3 拍板取正文口径为主。
- **状态**：已封闭。

### Q17. β / λ 搜索范围、准则与预算

- **裁定（口径拆分，封闭 v5 末尾"待补说明"交叉点）**：
  - β（量化损失权重）：主值 1.0，网格 {0.1, 1, 10}，**两端 {0.1, 10} 先行**，健康再补 1.0；落点判据 guard = 码本 perplexity 落 51–154。
  - λ（vCLUB 系数）：**主值 0.05 固定**，敏感性 {0.01, 0.05, 0.1} 仅作消融记录，**不与 β 联扫**。
  - v5 §11#5 "两端 {0.1,10} 先行"仅指 β；#4 的 "λ=0.05 网格"指上述小网格。预算：每格 40 epoch（§11#7）。
- **历史记录**：params §3.3（主值 1.0 依据）+ §9 变更记录"9 格全跑 → 先扫两端（省预算、先看失效模式）"；vCLUB λ=0.05 与 clamp ±6 在 v1.4 §11#4 封闭（旧 ±10 被 §11 推翻，§9 已登记冲突来源）。
- **状态**：已封闭。

### Q18. 码本更新方式

- **裁定**：**STE + commitment（γ=0.25，sg[·]）**，论文锚定；不做 EMA / RQ-VAE 风格对比。码本 6 组（3 共享 N_sh=3 + 3 特定 N_sp=1），每组 512×256。
- **历史记录**：v1.0 即锚定，v1.2 裁决 3 模态后组数从待定变 6 组（params §9"N_m/码本组数"行）。
- **状态**：已封闭。

### Q19. vCLUB 细节

- **裁定**：2 层 MLP hidden256 ELU → μ/logσ² 输出；log-variance 用 clamp **±6**（§11 优先，推翻旧 ±10）；λ=0.05；每批交替更新 1 次；batch < 512 的偏差只记录不阻断。
- **历史记录**：params §3.4（完整默认值）+ v1.4 §11#4；§9 专列一行"vCLUB clamp [-10,10] → ±6（§11 优先）"示范仲裁规则的用法。
- **状态**：已封闭。

## 五、训练、下游与评估（Q20–Q22）

### Q20. 两阶段轮数 / 早停 / ckpt 规则

- **裁定**（§11#7 + §5.3）：SASRec 300 epoch / 预热 20 / 主训练 100 / 网格每格 40。早停按**评估次数**计：patience 一律以评估次数为单位，等效容忍 = patience × eval_interval = 40 epoch；代码只维护 eval_counter，**禁止出现"epoch 版 patience"变量**；恢复 best-by-eval 权重；config_hash 覆盖 patience 与 eval_interval 两参数，改任一即新 run。ckpt 规则：best-by-eval + config_hash + aux_stats_hash 三重校验。
- **历史记录**：patience 语义是 v1.4（b4bdbc7）吸收外部 v4 三点之二定入的规则条款（params §9"散文一句 → 规则条款锁死"），误按 epoch 用的后果（等效容忍减半、早停偏早）登记为 design 风险表 R14。
- **状态**：已封闭。

### Q21. 下游模型结构

- **裁定**：下游 = **SAB-ANC 自建**（非论文 HMAT，D7 登记为"改进下游"）。输入 token 组织：V/T/B 三模态 token + [ANC] 锚点结构；动作词表**无**（D5，动作头默认砍掉）；4 维代理特征接 [BEH_1]；预测头 = next-item 推荐头；监督 = 推荐 CE 损失。
- **历史记录**：动作头从 v1.0"双头（召回+动作分类）"到 v1.2 实测字段缺失后砍掉（params §9："双头 → 默认砍掉动作头"）；token 端 [CAT]/[BRD] 同步删除（D10）。[ANC] 锚定的有效性验证 = 可证伪问题 #4：use_anc=false 时指标应下降；探针前置不过线不进指标阶段。
- **状态**：已封闭。

### Q22. 指标定义

- **裁定**：AUC = 全 item 候选排序；GAUC = 按用户算 AUC 再按该用户曝光数加权平均；Cold AUC / Cold GAUC = 冷启动子集（cold-item freq≤5 为主桶）上的同口径指标。三分桶口径见 Q10。
- **历史记录**：params §9"评估口径：总体均值 → 三分开，主结论在 cold-item"。
- **状态**：已封闭。

## 六、基线、验收与资源（Q23–Q26）

### Q23. 基线清单

- **裁定**：外部基线（WuKong / HSTU / MTGR / QARM / PSRQ+MCCA / DLRM）**不本地复现**，仅原文引用（params §9："复现成本远超预算"）。本地必做：LightGCN++ 同 split_hash 重跑（P0 第 7 步；旧 P0–P2 数字标"协议不一致"，禁跨切分搬数）+ 模块消融 w/o CGA / w/o PSGR / w/o DMRQ / use_anc=false / Φ=attention / H=8 / λ=0。
- **历史记录**：baseline 协议在 params §7 定稿（"同切分重跑，禁跨切分搬数"），v1.2 裁决数据集变更后旧数字整体降级为参照。
- **状态**：已封闭。

### Q24. 验收标准

- **裁定**：**不复现论文绝对数值**（Hi-SAM-Small AUC 0.7816 等仅参照）。验收 = 同一数据/协议（同 split_hash）下的相对趋势 + 四个可证伪问题的闸门全部通过（§8）。
- **历史记录**：v1.0 即"结构复现"定位（e73bb41），v1.1 切 MMSSL Baby 后追加红利——与 MMSSL/MSCA/MMRec 同划分可直接同表对标。
- **状态**：已封闭。

### Q25. 随机种子与统计口径

- **裁定**：上下游均多 seed，{42, 2025, 2026}；valid 报 mean±std；显著性检验与置信区间**不强制**（单卡预算约束）。
- **历史记录**：v1.0（dfe9868）定三 seed；下游消融升级判据（Q14）正是建立在"1 seed std"的分母之上，故 seed 数不可减。
- **状态**：已封闭。

### Q26. 硬件与优先级

- **裁定**：RTX 5060 Ti ×1（16GB，driver 610.88）、CPU 28 线程、RAM 32GB；无硬截止时间；优先级 = P0 门禁链 → SASRec 重训 → 上游 DST → 下游消融；全部落 D 盘（C 盘仅剩 30GB）；必设 `KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_DYNAMIC=FALSE`。
- **历史记录**：v1.3（fe567f3）成本重估链条——hidden=512 参数 ~16–25M（item emb 9.4M 主导，×4–5）、每 epoch 40–70min（O(d²) 理论 ×16、实测经验 ×4–6）、每 seed 7–20h、3 seed 串行 1–2.5 天；显存 2–6GB 充裕，瓶颈是墙钟。强制缓解 AMP fp16 + batch256 + 评估间隔 2ep → 4–10h/seed。硬门禁：P1 第一步先跑 1 epoch 计时外推，>24h/seed 触发 L3 降 hidden=256 + 登记 D11（升维只保 shape 不保容量，消融按"容量受限"口径解读）。旧触发线"epoch>30min"作废（512 维下属正常水平会误触发）。
- **状态**：已封闭。

## 七、仓库、合规、交付与失败（Q27–Q30）

### Q27. 仓库现有资产

- **裁定**：代码 `baseline/LightGCNpp`（P0–P2 已有真实结果）、`baseline/PRISM`（含 SASRec.py 骨干）、`baseline/MMEACR`（子模块）；历史结果 `baseline/docs/lightgcnpp_p0p1p2_report.md`、`baseline/prism_analysis.md`、各 logs/。环境：managed venv（`C:/Users/lkshpc/.workbuddy/binaries/python/envs/default`）默认未装依赖，需先 `pip install -r requirements.txt`；系统 conda python 备用。
- **历史记录**：PRISM 侧已有 SASRec 复用基础与 CLIP 512 维流程（process_clip.py）；LightGCNpp 的 P0–P2 报告是"旧数字标协议不一致"这一裁决的标的物。
- **状态**：已封闭。

### Q28. 权限 / 隐私 / 网络限制

- **裁定**：数据与结果无额外权限/隐私限制。网络事实（截至 2026-11-10）：GitHub/PyPI 直连正常；HF 走 `127.0.0.1:7897` 代理或 hf-mirror.com；**Google Drive（MMSSL 特征唯一来源）可能配额受限**，fetch 失败需换网络重跑。`.env` 内 MINERU_API_KEY / DEEPSEEK_API_KEY 不入 git。
- **历史记录**：代理与 git 推送在本仓库有一整套踩坑史（便携版 git 走代理必挂、坏代理污染远程跟踪引用等），可靠姿势 = 系统 git 直连重试循环；fetch_mm_data.py 头注释自声明 Drive 下载风险。
- **状态**：已封闭。

### Q29. 交付产物

- **裁定**（§11#9 六类）：config（+config_hash）、日志、checkpoint（+aux_stats_hash）、metrics JSON（**强制 schema，含 status 四态**）、7 张必备图、复现实验报告（引用偏差登记册 D1–D11，按各条"报告必须写什么"列执行）。不产出论文表格复刻。负向审计产物：`split_audit.json`（含 review_note 与人工签字位）与 `gate0_alignability.json`。
- **历史记录**：params §8.1 六类产物自 v1.0 即定；v1.4 新增 status 四态与 review_note 机制（负向审计放宽的配套牙齿）。
- **状态**：已封闭。

### Q30. 失败默认策略

- **裁定**（§11#10）：L1 ≤2h → L2 ≤1d → L3 ≤1d → L4 停止；**同 bug 修两次仍复现直接 L4**；L3 触发线 = "1 epoch 外推 >24h/seed"；到 L4 停下交用户决策，不自行改协议。
- **历史记录**：四级升级 params §8.2 自 v1.0 即定；触发线修订与 D11 降级路径见 Q26。
- **状态**：已封闭。

---

## 八、汇总与下一步

- 30/30 全部封闭，其中 28 项直接以 params v1.0–v1.4 既有拍板为准，2 项本轮新裁定（Q17 的 β/λ 口径拆分、G1 的切分协议更正）。
- 三处全局更正（G1 切分协议、G2 交互规模、G3 特征未落盘）须回写 v5 文本或在其 §9 变更记录登记冲突来源。
- **下一步 = P0 第 1 步**：跑 `fetch_mm_data.py` 拉取 MMSSL Baby 特征（G3）→ load 打印 shape 回填（384 vs 1024）→ 重建 id 映射同步重排 .npy → split_audit（含负向审计）→ 闸门-0（V–T < 3× 即停，改走 Amazon-2023 的唯一岔路口）→ LightGCN++ 同 split 重跑。

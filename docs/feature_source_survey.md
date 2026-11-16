# 特征文件直链调查：解除 C2/C5 闸门阻断（2026-11-17）

定位：仅链接清单与验证结论，**未启动任何完整下载**；所有 shape 验证通过 Google Drive
Range 请求读取 .npy 文件头（≤256 字节）完成，不落任何特征工件。人工确认后方可执行下载与 C1–C5。

---

## 一、核心结论（三项，均实测）

### 结论 1：现有 split 实为 MMRec 谱系 Sports，不是 MMSSL 官方 Baby

实测（`baseline/LightGCNpp/data/amazon-baby-mmssl/`，本次 wc/awk 统计）：

| 指标 | 本地 split 实测 | MMRec 谱系 Sports（LIRDRec arXiv:2505.04960 / MAGE 镜像） | MMSSL 官方 README Baby |
|---|---|---|---|
| 用户数 | 35,598（每文件行数） | 35,598 | 35,598 |
| item 数 | 18,357（max_item=18356） | 18,357 | 18,357 |
| 交互总数 | **296,337**（190,930+37,899+67,508） | **296,337** | 256,308 |
| valid 交互 | **37,899** | **37,899**（MAGE sports 逐位一致） | — |

用户/item/交互/valid 四项与 MMRec 谱系 Sports **逐位吻合**；与 MMSSL 官方 Baby
（交互 256,308）不符。`fetch_mm_data.py` 原注释与 Q30/G2 的"MMSSL Baby"声明需更正：
该数据是 MMRec/MMRec-FREEDOM/BM3 谱系的 **Sports（Sports and Outdoors, Amazon 2014 5-core）**，
被上游打包时误标为 baby。

### 结论 2：被拒的 (7050, 4096) 文件不是"Baby 变体"，是另一个数据集

MMRec 谱系中 baby=7,050 items / sports=18,357 items（两谱系恰好互换标签）。
已实测验证 BM3 官方 Drive baby 目录 image_feat.npy 头部 = `(7050, 4096) <f8`。
即被拒文件是 MMRec 谱系 **Baby** 特征，与我们的 18,357-item split **无任何映射关系**
（不同类别、不同 item 空间），不可建立映射，只能弃用（rejected 工件留档正确）。

### 结论 3：目标特征已找到且 shape 实测吻合，文本维度为 384（非 1024）

BM3 官方 Drive sports 目录两个特征文件头部实测：

| 文件 | 实测 shape | dtype | 预期 | 判定 |
|---|---|---|---|---|
| image_feat.npy | **(18357, 4096)** | `<f8` float64 | 18357×4096 | ✅ 行数精确匹配 |
| text_feat.npy | **(18357, 384)** | `<f4` float32 | MMSSL 声称 1024 | ✅ 行数匹配；**维度 384** |

文本 384 = all-MiniLM-L6-v2（MMRec 谱系标准），推翻"1024（Sentence-BERT）"旧口径；
Q30 Register Q5 与 params 的文本维度记录待回填为 384。此为谱系事实，非下载错误。

---

## 二、链接清单（人工确认后执行）

### 候选 A（推荐）：BM3 官方 Drive（WWW'23 官方仓库 enoche/BM3，可匿名访问）

目录：`https://drive.google.com/drive/folders/13cBy1EA_saTUuXxVllKgtfci2A09jyaG`
（embeddedfolderview 实测 HTTP 200，含 baby/clothing/elec/sports 子目录）

sports 子目录：`https://drive.google.com/drive/folders/1iJtyDmgeYdZsvO5297dNafyPDya21e8D`

| 文件 | 文件 ID | 实测验证 |
|---|---|---|
| image_feat.npy | `1Ggd3c-Tysm7z8f7R0n_ZWR6S5MNEydtV` | shape (18357,4096) f8 ✅ |
| text_feat.npy | `1xyegrwI8J9expuPU5ZB6A1_fg-EoUzaX` | shape (18357,384) f4 ✅ |
| i_id_mapping.csv | `1tgHlRPT6uWfBDSMRUx3MdjMM0CCYDRQW` | 行序对齐凭据（下载后比对） |
| u_id_mapping.csv | `11B2xzHWtnkbiRkbmbsa0c63RQ5iubTaL` | 用户映射参考 |
| sports.inter | `1K19wIN63-jrTFag7D-dlw2ql0C0_YP2j` | item 集合核验源 |

gdown 命令（大文件自动走 confirm 流程，gdown 已内置）：

```bash
gdown 1Ggd3c-Tysm7z8f7R0n_ZWR6S5MNEydtV -O image_feat.npy   # ~602MB (f8)
gdown 1xyegrwI8J9expuPU5ZB6A1_fg-EoUzaX -O text_feat.npy    # ~28MB (f4)
gdown 1tgHlRPT6uWfBDSMRUx3MdjMM0CCYDRQW -O i_id_mapping.csv
gdown 1K19wIN63-jrTFag7D-dlw2ql0C0_YP2j -O sports.inter
```

### 候选 B（备选/双源核验）：HuggingFace MAGE 镜像

`hf_hub_download(repo_id="Alex6657/MAGE", repo_type="dataset", filename="archive/MAGE_datasets_2026-10-08.zip")`
（1,882,496,634 bytes，zip SHA256 `8412c252d01efbcadc48101b3d3634191318e554d11219a93119b6253fb0651a`；
内含 SHA256SUMS.txt 可逐文件校验；国内走 hf-mirror.com）
- README 声明 sports image_feat.npy = (18357, 4096) float64，i_id_mapping 首行与 seed 映射一致；
- ⚠️ 其 text_feat.npy 为 Stage-1 改造（512 维增强），原始文本特征在 `text_feat_raw.npy`（维度未验证）；
- 状态：**部分验证**（仅 README 声明，未实测头部），仅作候选 A 失败时的备源与交叉校验。

### 不可用源：MMSSL 官方 Drive

`https://drive.google.com/drive/folders/1AB1RsnU-ETmubJgWLpJrXd8TjaK_eTp0`
- embeddedfolderview 匿名请求亦返回 **401**（目录已不可匿名访问），gdown 直拉同样会失败；
- 即便可访问，其 Baby 交互数（256,308）与本地 split（296,337）不符，**不可用**。

---

## 三、item 顺序对齐验证方案（下载后执行，进 C5）

1. **行数**：np.load 后 `shape[0] == 18357`（已通过头部预验，下载后复核）；
2. **顺序**：`i_id_mapping.csv` 应恰 18,357 行（0-based 行序 = 特征行序）；
   用 `sports.inter` 的 item 列重建 item 集合，与本地 train/valid/test.txt 的 item 集合做**双向差集**；
3. 集合一致 + 行数一致 → 顺序对齐成立（同一 5-core 预处理管线的 0-based 重编号）；
4. 全部通过后计算两 .npy 的 sha256 入 FeatureRegistry，冻结进 config_hash；
5. 任一失败 → 走候选 B 交叉核验 → 仍不一致则登记偏差并升级人工决策。

## 四、对闸门与文档的回填清单

- C2/C5 特征契约：image (18357,4096) f8；text (18357,384) f4（更新 ada gates 期望值）；
- D3 偏差登记：改为"MMRec 谱系 Sports（上游包误标 baby）"，或目录改名 `amazon-sports-mmrec`；
- Q30 Register Q5 / params：文本维度 1024 → **384**，来源标注 BM3/MMRec 谱系 Sentence-Transformers(MiniLM)；
- gate0（闸门-0）不受影响：V–T 可对齐性预检与维度无关，照常执行；
- 被拒工件 (7050,4096) 的 rejected 记录保留，作为结论 2 的证据。

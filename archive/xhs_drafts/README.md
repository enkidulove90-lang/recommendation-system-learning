# 归档：小红书一次性脚本（2026-11-10）

这里共 22 个文件，**只保留发布与实现溯源，不再是可执行入口**。它们的共同问题是：
只复用了后端的最后一个出口 `XhsPublisher`，取图、裁图、制卡、文案、校验、编排
各在根目录写一遍，换一台机器 / 换一个 IDE 就会产生完全不同的草稿。

迁移后的唯一入口：

```bash
python -m redbook.cli note --list                  # 列出全部 spec
python -m redbook.cli note <slug> --validate      # 只跑内容闸门
python -m redbook.cli note <slug> --stage         # 落盘不可变 review 包
python -m redbook.cli note <slug> --publish       # 人工目检后才投递草稿箱
```

每篇论文只新增一个 `redbook/notes/<slug>.yaml`，字段规范见 `redbook/notes/_schema.yaml`。

## 14 个草稿脚本 → note spec

| 归档文件 | spec | 说明 |
|---|---|---|
| `build_xhs_draft_sage.py` | `2601.21452.yaml` | P0 试点，等价性已验证 |
| `build_xhs_draft_diffgrm.py` | `2510.21805.yaml` | 有真实目检记录 |
| `build_xhs_draft_unipinrec.py` | `2606.00422.yaml` | |
| `build_xhs_draft_diger_2601_19711.py` | `2601.19711.yaml` | |
| `build_xhs_draft_2609_05339.py` | `2609.05339.yaml` | |
| `build_xhs_draft_2609_20804.py` | `2609.20804.yaml` | |
| `build_xhs_draft_2609_22086.py` | `2609.22086.yaml` | |
| `build_xhs_draft_ace_2605_29322.py` | `2605.29322.yaml` | 原稿（曾退回） |
| `build_xhs_draft_ace_v2.py` | `2605.29322_ace_v2.yaml` | 同论文第二版，用 slug 区分 |
| `build_xhs_draft_tmlr_cot_v2.py` | `TiZQnKDIHq_cot_v2.yaml` | 同论文第二版，用 slug 区分 |
| `build_xhs_draft_tmlr_loadbearing_cot.py` | `TiZQnKDIHq.yaml` | |
| `build_xhs_draft_sihg_rec.py` | `10.1145_3847662.yaml` | DOI 含斜杠，slug 已安全化 |
| `build_xhs_draft_2608_14429.py` | `2608.14429.yaml` | 走旧 `render_note` 路径；正文用「⚠️ 一点提醒」而非局限题头 |
| `build_xhs_draft_gateboxgcn.py` | `3773078.3831765.yaml` | 走冻结 7 段口径 `content_composer`，正文 1328 字 |

后两篇**正文原样保留，未为过闸门改写**，因此不符合新发布闸门，也就会被
`XhsPublisher.validate()` 拦住、无法重发。若需重新启用，须由人工决定是补写
局限段 / 压缩字数，还是维持归档（当前结论：维持归档）。

## 8 个工具脚本 → 后端模块

| 归档文件 | 新位置 |
|---|---|
| `crop_pdf_figure.py` | `redbook/services/figure_crop.py::crop_figure_by_caption` |
| `extract_sihg_assets.py` | `redbook/services/figure_crop.py::crop_targets` |
| `fetch_acm_pdf.py` | `redbook/infrastructure/paper_sources/acm_dl.py::fetch_acm_pdf` |
| `acm_wait_pass.py` | `redbook/infrastructure/paper_sources/acm_dl.py::wait_for_cloudflare` |
| `inspect_pdf_figures.py` | `redbook/services/figure_retrieval.py::PdfCaptionIndex` |
| `inspect_xhs_drafts.py` | `redbook/scripts/xhs_drafts.py::inspect_drafts` |
| `verify_xhs_drafts.py` | `redbook/scripts/xhs_drafts.py::prune` |
| `generate_xhs_images_2608.14429.py` | 自制图配方，`2608.14429.yaml` 的 `figures` |

根目录剩下的 `_*.py` 是会话临时抽取脚本（未入库），`main.py` /
`run_batch_pipeline.py` 是核心程序，`verify_e15_numbers.py` 属 PRISM 实验审计，
均不属于本发布栈，按约定未迁移。

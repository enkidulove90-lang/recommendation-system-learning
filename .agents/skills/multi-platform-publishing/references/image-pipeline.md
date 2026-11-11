# 图片流水线

## 三级图片获取策略

```
优先级 1: arXiv LaTeX 源包（最高清）
  → ArxivSourceImageExtractor.fetch(arxiv_id)
  → 从 arxiv.org/e-print/<id> 下载 .tar.gz
  → 提取 .eps/.pdf 矢量图，转为高清 PNG

优先级 2: PDF 高清渲染（回退）
  → HighDpiPdfFigureExtractor.extract(pdf_path, layout_path, hd_dir)
  → 使用 PyMuPDF (fitz) 以 600 DPI 渲染
  → 按 MinerU layout.json 定位图片区域

优先级 3: MinerU 自动提取（兜底）
  → 直接使用 data/parsed/<id>/images/ 目录
  → 质量取决于源 PDF 分辨率
```

## 图片选择准则

从提取的图片中筛选帖子配图：

| 优先级 | 类型 | 用途 | 识别方法 |
|--------|------|------|----------|
| ★★★★★ | 架构图/流程图 | 展示方法全貌 | Figure 1-2, markdown 中 "architecture" "framework" |
| ★★★★ | 对比表/结果图 | 支撑性能声明 | Table, markdown 中 "result" "comparison" |
| ★★★ | Case Study | 展示实际效果 | markdown 中 "case" "example" |
| ★★ | 消融实验图 | 辅助理解 | markdown 中 "ablation" |
| ★ | 训练曲线 | 补充 | markdown 中 "loss" "training" |
| ❌ | 公式密集图 | 跳过 | is_equation_heavy=True |
| ❌ | 文字截图 | 跳过 | is_table=True 且小尺寸 |
| ❌ | 小图标 | 跳过 | width < 1400 或 height < 1400 |

## 智能选图（基于章节上下文）

```python
# vision_enhancer.py 的 _select_core_images() 方法
# 按 markdown 章节标题分类图片类型
# 优先选择 architecture > result_table > loss_curve > other
# 每篇最多选 3 张（视觉增强用）或 5 张（小红书发布用）
```

## 图片组合（Pillow 合成）

当需要将多张图合成为一张竖版信息图时：

```python
from redbook.automation.images import group_figures, compose_group, build_manifest, load_manifest

# 1. 构建 manifest
assets = build_manifest(image_paths, output_path, metadata)

# 2. 分组（保守策略，基于图注相似度）
groups = group_figures(assets, threshold=0.80)

# 3. 合成
for group in groups:
    if len(group) in {2, 3, 4}:
        result = compose_group(group, output_path)
```

### 合成布局

| 图片数 | 布局 | 画布 |
|--------|------|------|
| 2 | 上下垂直 | 1440×1920 |
| 3 | 上1下2 | 1440×1920 |
| 4 | 2×2 网格 | 1440×1920 |

### 最小可读性检查
- 合成后面板最短边 ≥ 520px，否则拒绝合成
- 保持原图比例，不裁剪
- 白色背景，96% JPEG 质量

## 视觉模型审查（可选）

使用多平台视觉模型对选中的图片进行最终审查：

```python
# ModelScope Qwen3.5 → SiliconFlow Qwen2.5-VL → Zhipu GLM-4V-Flash
# vision_enhancer.py 多 provider fallback
# 输出 _figures.json：每张图的类型、描述、所在章节
```

## 高质量图片提取方案

| 方案 | 质量 | 自动化 | 命令 |
|------|------|--------|------|
| PyMuPDF 600DPI | ★★★★ | ✅ | `fitz open + page.get_pixmap(dpi=600)` |
| pdfimages (poppler) | ★★★★ | ✅ | `pdfimages -all paper.pdf prefix` |
| Ghostscript 600DPI | ★★★★ | ✅ | `gs -r600 -dNOPAUSE -sDEVICE=png16m` |
| arXiv LaTeX 源 | ★★★★★ | ✅ | `ArxivSourceImageExtractor.fetch()` |
| 作者主页 slides | ★★★★★ | ❌ | 手动下载 |

## CLI 命令

```bash
# 完整图片准备流程
python -m redbook.cli prepare-figures \
  --paper-id "arxiv:XXXX" \
  --markdown data/parsed/XXXX/content.md \
  --images data/parsed/XXXX/images/ \
  --pdf data/papers/XXXX.pdf \
  --layout data/parsed/XXXX/layout.json \
  --arxiv-id XXXX \
  --vision \
  --data-root data

# 生成 manifest 和组合图
python -m redbook.automation.cli --data-root data \
  manifest --output data/figures/manifest.jsonl data/parsed/XXXX/images/*.jpg

python -m redbook.automation.cli --data-root data \
  compose --manifest data/figures/manifest.jsonl --output-dir redbook/assets/composed
```

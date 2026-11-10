# -*- coding: utf-8 -*-
# DEPRECATED 2026-11-10: 内容已迁移到 redbook/notes/3773078.3831765.yaml
# 唯一运行入口: python -m redbook.cli note 3773078.3831765 --validate | --stage | --publish
# 本文件仅保留发布溯源；正文/图序/话题已在 spec 中定稿，请勿再执行。
"""GateBoxGCN (RecSys 2026) — build the draft and deliver it to Xiaohongshu.

Content follows the frozen 2026-10-28 spec: 7 fixed sections, plain text,
no '#', title = 【RecSys 2026】 + hook with the prefix counted into the
20-character budget.

Usage:
    python build_xhs_draft_gateboxgcn.py --dry-run     # validate + write draft.json only
    python build_xhs_draft_gateboxgcn.py               # real delivery (draft only, never publishes)
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from redbook.services.content_composer import compose_content  # noqa: E402
from redbook.infrastructure.xiaohongshu_delivery import (  # noqa: E402
    DeliveryError,
    DraftPayload,
    OpenCliXiaohongshuDelivery,
    TopicEntityUnavailable,
)

IMAGES = ROOT / "data" / "parsed" / "gateboxgcn" / "images"
PDF = Path(r"C:/Users/xu.yan1/Downloads/3773078.3831765.pdf")

VENUE, YEAR, HOOK = "RecSys", 2026, "偏好不是一个点"
TOPICS = ("论文分享", "人工智能", "推荐系统", "深度学习")

SECTIONS = {
    "📌 解决什么问题": (
        "主流推荐把用户和物品都压成向量空间里的一个点，可真实偏好常常是个范围："
        "预算两千到五千日元、颜色不只蓝色也行。Box 嵌入用超矩形（中心 + 偏移）来装这种不确定性，"
        "但现有 Box 方法都要求偏移量为正，因为负偏移会让盒子的几何定义失效。\n"
        "结果就是模型不管信息够不够，都必须给出一个盒子：交互很稀疏、这一维根本没观测到、"
        "或者干脆是噪声的时候，这些不可靠维度照样参与打分。"
    ),
    "✨ 创新点/贡献": (
        "· 允许偏移取负，并把负维度显式定义为“不可评估维度”：不再假装它是偏好范围，而是承认这一维没信息。\n"
        "· 前向硬门控 + 反向软门控：前向把不可评估维度整维剔除，只用可靠维度算偏好分；"
        "反向仍给这些维度回传梯度，门控和 box 表示一起端到端训练。\n"
        "· 带符号的偏好打分：重叠记正、分离记负，把距离当惩罚项，不再依赖“体积”这个非负量。\n"
        "· 把 box 学习接进 GCN：center 和 offset 分别沿用户—物品图传播聚合，并处理偏好的方向性。"
    ),
    "🧪 Benchmark": (
        "论文报告：四个数据集——Yelp、Amazon Pet Supplies、MovieLens 1M、KuaiRec。\n"
        "对比方法：GCN 系（LightGCN、LR-GCCF、IMP-GCN、RAGCN、LayerGCN、NLGCL）"
        "与 Box 系（BoxGNN、L_LCD-UC），另有 MF、NGCF 等。\n"
        "指标：Recall@20、NDCG@20。"
    ),
    "⚙️ 实验条件": (
        "论文报告：Yelp / Amazon 维度 D=256，MovieLens / KuaiRec 沿用前作取 D=64；"
        "center 和 offset 用高斯初始化（均值 0、标准差 1e-2）；学习率 1e-4、L2 系数 1e-4，"
        "在各自验证集上调。\n"
        "数据切分：按时间取最早 70% 训练、最近 20% 测试、剩余 10% 调参；"
        "Yelp 与 Amazon 过滤交互数少于 15 的用户、少于 10 的物品，稀疏度分别为 99.90% 和 99.83%。"
    ),
    "📊 效果": (
        "论文报告（R@20 / N@20，相对最优基线）：\n"
        "· Yelp 0.0789 / 0.0500，+5.76% / +6.16%\n"
        "· Amazon 0.0733 / 0.0457，+6.39% / +8.04%\n"
        "· MovieLens 0.1142 / 0.1235，+6.63% / +13.20%\n"
        "· KuaiRec 0.1190 / 0.3671，+33.11% / +35.56%\n"
        "负偏移确实被用上了：Yelp 有 19.86%、Amazon 有 12.45% 的偏移维度小于 0。\n"
        "消融（Yelp R@20）：去掉软门控 0.0774、完全去掉门控改强制正偏移 0.0769、"
        "换 Gumbel 打分 0.0775、换体积打分 0.0744，都低于完整的 0.0789。"
    ),
    "📎 arXiv": "暂无公开 arXiv 预印本，正式版见 https://doi.org/10.1145/3773078.3831765",
    "💻 GitHub": "https://github.com/mofan118-source/GateBoxGCN",
}

IMAGE_FILES = (
    "fig1_architecture.png",   # 封面：三步总览
    "card_numbers.png",        # 自制数字卡
    "fig3_gating.png",         # 硬/软门控前向-反向
    "fig4_scoring.png",        # 带符号打分示意
    "fig5_layers.png",         # 层数影响（四数据集）
)


def build() -> tuple[dict, list[Path]]:
    composed = compose_content(SECTIONS, venue=VENUE, year=YEAR, hook=HOOK)
    images = [IMAGES / name for name in IMAGE_FILES]
    missing = [str(p) for p in (*images, PDF) if not p.is_file()]
    if missing:
        raise SystemExit(f"missing assets: {missing}")
    draft = {"title": composed["title"], "body": composed["body"], "topics": list(TOPICS)}
    return draft, images


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="validate and write draft.json only")
    args = parser.parse_args()

    draft, images = build()
    digest = hashlib.sha1(draft["body"].encode("utf-8")).hexdigest()[:10]
    outdir = ROOT / "publish_queue" / digest
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "draft.json").write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")
    (outdir / "manifest.json").write_text(
        json.dumps({"images": [str(p) for p in images], "pdf": str(PDF)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"title ({len(draft['title'])}): {draft['title']}")
    print(f"body  ({len(draft['body'])} chars), images={len(images)}, queue={outdir}")

    if args.dry_run:
        print("DRY RUN: not delivering")
        return

    payload = DraftPayload(
        title=draft["title"], body=draft["body"],
        image_paths=tuple(images), topics=TOPICS, pdf_path=PDF,
    )
    try:
        receipt = OpenCliXiaohongshuDelivery().deliver(payload)
    except TopicEntityUnavailable as error:
        print(f"TOPIC UNAVAILABLE (paper skipped, nothing saved): {error}")
        raise SystemExit(3)
    except DeliveryError as error:
        print(f"DELIVERY FAILED: {error}")
        raise SystemExit(4)
    print(json.dumps({
        "draft_id": receipt.draft_id, "title": receipt.title,
        "image_count": receipt.image_count, "topics": list(receipt.topics),
        "pdf_attachment": receipt.pdf_name, "state": "saved_draft_only",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

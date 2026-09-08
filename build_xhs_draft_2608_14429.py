"""Re-build + re-publish the XHS draft for 2608.14429 (PriCoRec).

The canonical ``paper_to_xhs.render_note`` maps nested summary keys
(``architecture.modules``, ``main_results`` keyed by ``MSCA.R@20``, flat
``baselines``/``metrics``) that this paper's *flat* summary does not populate,
so it emitted a 4-image, near-empty body.  This script bypasses that mapping:
it builds a :class:`PublicationPackage` directly with a hand-crafted rich body
(the real gAUC / R@100 / R@10 numbers) and the 4 polished infographic PNGs,
then stages -> publishes -> deletes the old draft.

Run from the project root.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from redbook.automation.publishing import PublicationPackage, XhsPublisher  # noqa: E402
from redbook.infrastructure.xiaohongshu_delivery import (  # noqa: E402
    DeliveryError,
    OpenCliXiaohongshuDelivery,
)

PID = "2608.14429"
PARSED = ROOT / "data" / "parsed" / f"{PID}_隐私感知云-端协同广告推荐框架"
CANON = f"https://arxiv.org/abs/{PID}"

IMAGES = [
    PARSED / "images" / "xhs_features_split.png",
    PARSED / "images" / "xhs_cloud_pre_ranking.png",
    PARSED / "images" / "xhs_on_device_ranking.png",
    PARSED / "images" / "xhs_key_numbers.png",
]
PDF = PARSED / f"{PID}_origin.pdf"

TITLE = "隐私感知云-端协同广告推荐框架"

BODY = """🧠 解决什么问题
广告推荐要把模型跑在云上，但年龄、性别这些敏感特征一旦上云就有隐私风险。既要保护隐私又不能让效果垮掉，是工业界真实痛点。

✨ 主要贡献 / 创新点
1. 隐私感知云-端协同框架：预排序留云端，排序/重排序搬端上，敏感特征只存设备端
2. DPP 多样性正则器：惩罚候选冗余，提升预排序候选集质量
3. 云端引导辅助学习：云端 logit 作辅助特征喂给端上轻量模型，零额外推理成本

🔧 方法论
• 云端预排序：1000→100 候选 + 相关性 logit
• 设备端排序：云特征 + 端特征 + 云 logit 个性化精排
• 多样性正则：L_div = -log det(S)

🧪 Benchmark 与数据集
• 任务：CTR 预估 + 级联推荐（预排序 + 排序）
• 数据集：OpenMCC、TaobaoAd、Ali-CCP（3 个工业级）
• 对比 6 个基线（PNN / DP-SGD / DualRec / FedCAR / FedCIA …）
• 指标：gAUC、R@K、nDCG@K

📊 实验效果
云端预排序 gAUC 全面领先：Ali-CCP 73.69 vs 72.93（+0.76），OpenMCC 80.29 vs 80.06，TaobaoAd 89.36 vs 89.25。
设备端排序 R@10 提升更猛：TaobaoAd 21.74 vs 17.38（+4.36），Ali-CCP 24.10 vs 20.97（+3.13），OpenMCC 13.87 vs 11.37（+2.50）。

⚠️ 一点提醒
论文未报告统计显著性检验，也未披露优化器 / 学习率 / batch，可复现性受限；但「特征隔离保隐私」的思路很实在。

📄 论文：https://arxiv.org/abs/2608.14429

关注我，持续拆解推荐系统与多模态方向的新论文 📚"""

TOPICS = ["论文分享", "人工智能", "推荐系统"]
LINKS = {"paper": CANON, "pdf": CANON, "code": ""}
OLD_DRAFT_ID = "s:dae2bf08-7b4d-4b5d-9a3a-60aef278820e"


def main() -> int:
    missing = [str(p) for p in (*IMAGES, PDF) if not Path(p).is_file()]
    if missing:
        print("MISSING ASSETS:", json.dumps(missing, ensure_ascii=False))
        return 2

    print(f"title chars = {len(TITLE)}  body chars = {len(BODY)}  images = {len(IMAGES)}")

    package = PublicationPackage(
        paper_id=PID,
        platform="xhs",
        canonical_url=CANON,
        title=TITLE,
        body_markdown=BODY,
        image_paths=[str(p) for p in IMAGES],
        links=LINKS,
    )
    package.metadata["topics"] = list(TOPICS)
    package.metadata["pdf_path"] = str(PDF)

    publisher = XhsPublisher(ROOT)
    staged = publisher.stage(package)
    print("STAGE:", json.dumps(staged, ensure_ascii=False))
    if not staged.get("ok"):
        return 3

    result = publisher.publish(staged["staged_id"])
    print("PUBLISH:", json.dumps(result, ensure_ascii=False))

    if result.get("ok"):
        try:
            OpenCliXiaohongshuDelivery()._delete(OLD_DRAFT_ID)
            print("DELETED_OLD:", OLD_DRAFT_ID)
        except DeliveryError as exc:
            print("DELETE_OLD_FAILED:", str(exc))
        except Exception as exc:  # noqa: BLE001
            print("DELETE_OLD_ERROR:", repr(exc))
        return 0

    print("PUBLISH_FAILED: keeping old draft", OLD_DRAFT_ID)
    return 4


if __name__ == "__main__":
    sys.exit(main())

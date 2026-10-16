# -*- coding: utf-8 -*-
"""把 build_xhs_draft_unipinrec.py 的 BODY 块替换为 v5（最终版，≤1000 字）。

v5 相对 v4：去掉与「一句话」重复的延迟/QPS 数字、去掉多余的看图引用，压进 1000 字。
"""
import io
import re
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "build_xhs_draft_unipinrec.py"

BODY_LITERAL = '''BODY = """🎓 一句话：召回要给上百万候选快速打分，排序只对几百个候选做更贵的交叉计算——算法形态不同，但两边编码的是同一份用户行为历史。Pinterest 把它们合进一个模型（输入、训练、服务一起统一，此前只统过主干）：线上互动 +1%，延迟 −11.1%，QPS +63.6%。

✨ 三个改动（看图 1）
① 动作编成 multi-hot 拼到特征维、不插 token（长度与召回一致）；历史动作 20% 随机 mask、候选恒 mask，用每类动作一个 MLP 头做 BCE。
② 每条样本 = 过去行为序列 + 未来一次请求的完整曝光 slate（未交互曝光保 10%）：召回的正样本、排序的负样本一次都有了。
③ 历史的 O(n²) 自注意力只在召回侧 prefill 一次，KV 经 CUDA IPC 给排序复用（只做 O(n·k) decode）；Faiss 一次调用同时返回候选 ID 与 item 嵌入。

📊 结果
• 离线：排序 Hit@3 0.10096，比生产排序模型 TransActV2+DCNv2（0.08801）高 14.7%，也高于等长 HSTU（0.09733）；召回 Recall@10 0.7766 与 PinRec 持平。
• 消融：只训排序 0.09735 已超 HSTU 与生产排序模型，加回召回目标到 0.10096；先训召回再微调仅 0.09587（embedder 须冻结）。
• 效率：KV 复用让排序从 prefill 变 decode，单次前向 ≈2.4×，叠 flex attention+fp8 最高 3.92×（线上实际用 bf16）。

⚠️ 局限
① 线上只替换召回 + 粗排，下游原精排未动，离线 14.7% 的优势落到线上只剩约 1% 互动提升；
② fp8 把 QPS 推到 +109.1%，但量化使离线指标掉 0.5%、延迟反而 +6.7%，线上仍用 bf16；
③ 只在 Pinterest 两个场景验证，未开源。

📄 论文：https://arxiv.org/abs/2606.00422
💻 相关开源：github.com/pinterest/transformer_user_action、github.com/meta-recsys/generative-recommenders
✨ 关注我，持续拆解推荐系统论文 📚"""'''


def main() -> int:
    src = io.open(TARGET, encoding="utf-8").read()
    pattern = re.compile(r"BODY = \(.*?\n\)|BODY = \"\"\".*?\"\"\"", re.S)
    if not pattern.search(src):
        print("!! 未找到 BODY 块")
        return 1
    src = pattern.sub(lambda m: BODY_LITERAL, src, count=1)
    io.open(TARGET, "w", encoding="utf-8", newline="\n").write(src)
    print("BODY 块已替换为 v5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

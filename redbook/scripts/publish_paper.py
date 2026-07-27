"""
Publish a paper-sharing post to Xiaohongshu in the style of 乌萨奇今天读paper了吗.

Paper: MMEACR - Multimodal Memory-Enhanced Agent Collaboration for Recommendation
Format follows the target post structure: Motivation > Contribution > Methodology > Experiments > Conclusion > #tags
"""

import os, sys
sys.path.insert(0, r'c:\Users\xu.yan1\papers\recommendation-system-learning\redbook')

import playwright_browser
class _F: Camoufox = playwright_browser.PlaywrightBrowser
class _M: sync_api = _F()
sys.modules['camoufox'] = _M
sys.modules['camoufox.sync_api'] = _F

from xhs_cli.auth import get_cookie_string, cookie_str_to_dict
from xhs_cli.client import XhsClient

# === Post Content ===

POST_TITLE = "多模态记忆Agent推荐框架"

POST_CONTENT = """Motivation
现有LLM推荐智能体大多只依赖文本交互记录来建模用户偏好，忽略了商品图像、评论配图等多模态视觉证据。同时，记忆更新采用自由文本反思方式，缺乏结构化约束，容易引入语义噪声和偏好漂移。

贡献：
提出MMEACR（Multimodal Memory-Enhanced Agent Collaboration for Recommendation），通过双轨记忆架构首次将可解释的语言智能体推理与基于多模态嵌入的密集匹配解耦，兼顾推荐的可解释性与细粒度相似度。

核心设计：
🔹 双轨架构 — 推理轨（Reasoning Track）使用User/Item Memory Agent进行属性引导的结构化记忆演化；匹配轨（Matching Track）利用预训练多模态嵌入，对原始交互叙事和商品图像进行密集相似度计算。
🔹 属性引导记忆演化 — 预定义语义属性空间，指导Agent在推荐正确时强化对应属性、错误时反思修正，有效过滤跨模态噪声。
🔹 多模态Agent记忆 — 利用多模态LLM将商品图像转为语言描述，初始化并持续丰富Item记忆，让Agent真正"看见"视觉证据。
🔹 加权RRF融合 — 两轨排名通过加权倒数排名融合（Reciprocal Rank Fusion），最终输出鲁棒且可解释的推荐列表。

实验：
在Amazon三个真实域（CDs、Cell Phones、Fashion）上评估。Fashion域N@1提升45.45%，N@5提升23.33%，MRR提升27.14%；推理时间相比AgentCF降低6%-16%。消融实验验证了属性引导、双Agent协作、多模态记忆三个组件的独立贡献。

结论：
推荐Agent不应只读文本——视觉证据和结构化记忆演化同等重要。MMEACR通过双轨解耦设计让Agent既能"看见"又能"反思"，为多模态推荐Agent系统提供了新范式。

来源：arXiv 2607.07108
作者：Hao Cong, Huizu Lin, Zihan Wang, Chengkai Huang, Quan Z. Sheng, Lina Yao (Tsinghua, USTC, PKU, UNSW, Macquarie, CSIRO Data61)

#推荐系统 #LLM #多模态 #Agent #论文分享 #AI #强化学习 #智能体"""


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paper_images_dir = os.path.join(
        base_dir, "data", "parsed",
        "2607.07108_多模态记忆增强的推荐智能体协作", "images"
    )

    # Architecture images selected (not formula images)
    selected_images = [
        "98edc660de228c64ca9f1fa89d330eb2d5da132f1ae5e3f3e3c4828baaf36ad2.jpg",  # Figure 1: Architecture comparison
        "e02c05bb31ecbd466fc7f94c9a49f7785e8ae293062b7743720b68da8ba8c48d.jpg",  # Figure 2: MMEACR Framework
        "6edeb0db2c0c406203dfaedcd9eec722c9dafc14ce5c2be420b0b8ad8b6675aa.jpg",  # Figure 3: Case study
        "2c78718cef0428c9eb986d573dae74271c7b03fea7751776f47efe9aa04ced9b.jpg",  # Figure 6: Query template
        "fb67018f8bca96b1bb6322872a8a24f3a444b51fcb68b3335c1c75e243a5cfcb.jpg",  # Figure 8: Prompt template
    ]

    image_paths = []
    for img in selected_images:
        full_path = os.path.join(paper_images_dir, img)
        if os.path.exists(full_path):
            image_paths.append(full_path)
        else:
            print(f"WARNING: Image not found: {full_path}")

    print(f"Selected {len(image_paths)} images:")
    for p in image_paths:
        print(f"  - {os.path.basename(p)}")

    # Verify login
    cookie = get_cookie_string()
    if not cookie:
        print("ERROR: Not logged in!")
        return

    print(f"\nPost Title: {POST_TITLE}")
    print(f"Post Content: {len(POST_CONTENT)} chars")
    print(f"Post Images: {len(image_paths)}")

    # Confirm before publishing
    print("\n" + "=" * 60)
    print("Ready to publish! Confirm:")
    print(f"  Title: {POST_TITLE}")
    print(f"  Content: {len(POST_CONTENT)} chars")
    print(f"  Images: {len(image_paths)}")
    print("=" * 60)
    print("\nType 'yes' to publish, anything else to cancel:")
    confirm = input("> ").strip().lower()
    if confirm != 'yes':
        print("Cancelled.")
        return

    print("\nPublishing to Xiaohongshu...")
    try:
        with XhsClient(cookie_str_to_dict(cookie)) as client:
            result = client.publish_note(
                title=POST_TITLE,
                image_paths=image_paths,
                content=POST_CONTENT,
                return_detail=True,
            )

            if isinstance(result, dict):
                if result.get("success"):
                    print(f"\nSUCCESS! Post published!")
                    print(f"  Note ID: {result.get('note_id', '?')}")
                    print(f"  URL: {result.get('url', '?')}")
                else:
                    print(f"\nPublish result unclear: {result}")
            elif result is True:
                print("\nSUCCESS! Post published!")
            else:
                print(f"\nPublish returned: {result}")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

    playwright_browser.shutdown()


if __name__ == "__main__":
    main()

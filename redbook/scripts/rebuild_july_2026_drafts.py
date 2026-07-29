"""Create the four July-2026 Xiaohongshu notes as drafts only.

Use a Python argv list so paragraph breaks are delivered as real newlines,
not as the two literal characters ``\\`` and ``n``.
"""
from pathlib import Path
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
CARDS = ROOT / "redbook" / "assets" / "mineru_selected_assets"
NODE = shutil.which("node")
OPENCLI_MAIN = Path.home() / "AppData" / "Roaming" / "npm" / "node_modules" / "@jackwener" / "opencli" / "dist" / "src" / "main.js"
TOPIC_CATALOG = ROOT / "redbook" / "config" / "draft_topics.json"


POSTS = [
    {
        "slug": "openai-gpt-red",
        "title": "GPT-Red：让攻击者帮你测安全",
        "topics": "AI安全,智能体,大模型,论文解读",
        "body": """🎯 为什么值得看\n\n智能体一旦接触网页、邮件和文件，提示注入就不再只是“提示词问题”，而会变成工具调用链上的真实风险。\n\n✨ 核心想法\n\nGPT-Red 让攻击者与防御者在同一套工具环境中持续自博弈：攻击方负责发现新漏洞，防御方据此变强，再反过来逼攻击方升级。\n\n🧩 图里看什么\n\n从攻击成功率曲线到直接提示注入评测，这篇工作把“红队能力是否真的更强”放到可扩展测试计算和真实任务环境里检验。\n\n🧭 对 Agent 产品的启发\n\n安全评测不应只靠静态题库；要把不可信内容、工具权限和任务完成率一起放进闭环。\n\n📄 论文与发布页\nhttps://openai.com/index/unlocking-self-improvement-gpt-red/\n\n📎 PDF\nhttps://cdn.openai.com/pdf/gpt-red-automated-red-teaming-via-self-play-at-scale.pdf\n\n💻 代码\n暂无官方代码；OpenAI 官方 GitHub：https://github.com/openai\n\n图表摘自论文，仅作学术解读。""",
    },
    {
        "slug": "meta-ra-rft",
        "title": "Meta RA-RFT：类比也能被训练",
        "topics": "大模型,强化学习,检索增强,论文解读",
        "body": """🎯 一个常见难题\n\n复杂推理题里，模型常常“见过类似题”却不会把解题结构迁移过来。RA-RFT 的切入点正是把这种类比能力显式纳入训练。\n\n✨ 核心贡献\n\n先检索相似案例，再让策略模型学习哪些关系可以迁移、哪些细节不能照搬；奖励信号约束的是推理质量，而不是机械复述。\n\n🧩 图里看什么\n\n五张图依次展示动机、检索—推理训练框架、训练曲线、回答对比和案例分析。建议从框架图看起。\n\n🧭 我的判断\n\n对需要长链条解决问题的检索 Agent，关键不是“多塞几个案例”，而是让模型学会把案例抽象成可复用的结构。\n\n📄 Meta 论文页（2026-07 收录）\nhttps://ai.meta.com/research/publications/learning-to-reason-by-analogy-via-retrieval-augmented-reinforcement-fine-tuning/\n\n📎 PDF\nhttps://arxiv.org/pdf/2606.13680\n\n💻 代码\n暂无官方代码；Meta AI 官方 GitHub：https://github.com/facebookresearch\n\n图表摘自论文，仅作学术解读。""",
    },
    {
        "slug": "tencent-hils",
        "title": "腾讯 HiLS：长上下文不必全算",
        "topics": "长上下文,注意力机制,大模型,论文解读",
        "body": """🎯 长上下文真正难在哪里\n\n上下文变长后，难点不只是算力，而是模型能否稳定找到真正相关的信息。全量注意力昂贵，粗暴稀疏又容易漏掉关键线索。\n\n✨ HiLS 的答案\n\nHierarchical Sparse Attention 先做粗粒度定位，再在相关区域精读：把“找哪里”和“读什么”拆成两个层级。\n\n🧩 图里看什么\n\n从检索任务、架构图到 PPL/RULER 与延迟比较，重点观察它如何同时验证效果与效率。\n\n🧭 可迁移的思路\n\n面向超长会话、检索增强和序列推荐，先路由再细读可能比盲目扩大上下文窗口更可控。\n\n📄 论文页\nhttps://arxiv.org/abs/2607.02980\n\n📎 PDF\nhttps://arxiv.org/pdf/2607.02980\n\n💻 官方代码\nhttps://github.com/Tencent-Hunyuan/HiLS-Attention\n\n图表摘自论文，仅作学术解读。""",
    },
    {
        "slug": "mmeacr",
        "title": "MMEACR多模态推荐智能体",
        "topics": "推荐系统,多模态,智能体,论文解读",
        "body": """🎯 推荐 Agent 的盲区\n\n只读文本的推荐智能体，很难完整理解用户交互和商品图片；而且一次交互得到的线索，也常常无法沉淀成下一次决策可用的记忆。\n\n✨ 核心贡献\n\nMMEACR 同时维护用户/物品的多模态记忆，并通过协作与排序模块把记忆转为下一项推荐。\n\n🧩 图里看什么\n\n先看总体架构，再看记忆演化案例、结构化查询与协作提示模板：重点是“信息如何被写入、修正和调用”。\n\n🧭 对推荐研发的启发\n\n多模态不是把图文拼在一起；更重要的是让用户偏好、商品特征与交互反馈在记忆层发生联动。\n\n📄 论文页\nhttps://arxiv.org/abs/2607.07108\n\n📎 PDF\nhttps://arxiv.org/pdf/2607.07108\n\n💻 代码\n暂无官方代码；可复现工具（RecBole）：https://github.com/RUCAIBox/RecBole\n\n图表摘自论文，仅作学术解读。""",
    },
]


def main():
    requested = set(sys.argv[1:])
    posts = [post for post in POSTS if not requested or post["slug"] in requested]
    if requested and not posts:
        raise SystemExit("No matching post slug")
    topic_config = json.loads(TOPIC_CATALOG.read_text(encoding="utf-8"))
    topic_catalog = topic_config.get("posts", {})
    for post in posts:
        topics = [str(topic).strip().lstrip("#") for topic in topic_catalog.get(post["slug"], [])]
        topics = [topic for topic in topics if topic]
        if not topics:
            raise SystemExit(f"Missing configured topics for {post['slug']}")
        images = [CARDS / f"{post['slug']}-{i:02d}.jpg" for i in range(1, 6)]
        command = [
            NODE, str(OPENCLI_MAIN), "xiaohongshu", "publish", post["body"],
            "--title", post["title"],
            "--images", ",".join(str(image) for image in images),
            "--topics", ",".join(topics),
            "--draft", "true",
            "--site-session", "persistent",
            "--keep-tab", "true",
            "--format", "json",
        ]
        print(f"Creating draft: {post['slug']}")
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if result.returncode:
            raise SystemExit(result.stderr.strip() or result.stdout.strip())
        print(result.stdout)


if __name__ == "__main__":
    main()

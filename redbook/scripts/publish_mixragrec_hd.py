"""Publish MixRAGRec with HD images + 5 topic tags."""
import subprocess, sys, os

IMG_DIR = r"c:\Users\xu.yan1\papers\recommendation-system-learning\data\parsed\2605.28175\test_images"
XHS = os.path.expandvars(r"%APPDATA%\Python\Python311\Scripts\xhs.exe")

cmd = [
    XHS, "post",
    "--title", "KDD26｜MixRAGRec多Agent推荐",
    "--body", """🎓 LLM推荐系统加知识图谱(KG)增强推理已是共识。但有个尴尬的问题：简单查询「我喜欢科幻片」和复杂查询「推荐类似诺兰的烧脑片」竟用相同粒度检索KG——要么信息不足，要么噪声爆表。

MixRAGRec(PolyU, KDD2026)第一个用混合专家(MoE)思路解决这个问题的多Agent推荐框架。

✨ 核心亮点
• 四种检索粒度动态路由：直接生成/三元组/子图/连通图，按查询复杂度自适应
• ML-1M Accuracy达0.504(↑11.0%)，Recall@3达0.798(↑20.4%)
• 总耗时1.56秒 vs 基线3.78秒——又准又快

🧠 三个Agent协作
1. 混合专家检索Agent——基于查询嵌入路由到四种KG检索专家
2. 知识偏好对齐Agent——图结构→LLM友好自然语言
3. 对比学习推荐Agent——硬负采样+对比偏好反馈
训练：MMAPO联合优化，共享奖励含边际信息增益项

📊 实验(LLaMA3-8B/Mistral-7B, 三数据集)
ML-1M: Acc 0.504/R@3 0.798 | ML-20M: Acc 0.676/R@3 0.900 | LFM-1K: Acc 0.934/R@3 0.990

💡 可探索方向
方向一：MoE路由蒸馏——多Agent路由逻辑蒸馏到单模型
方向二：跨域KG迁移——MovieLens路由策略零样本迁移电商/音乐
方向三：成本感知Agent决策——边际信息增益泛化到工具调用

📄 arXiv：https://arxiv.org/abs/2605.28175
📎 PDF：https://arxiv.org/pdf/2605.28175
🏫 PolyU(Hong Kong) + NUS""",
    "--topic", "推荐系统", "--topic", "LLM", "--topic", "Agent",
    "--topic", "知识图谱", "--topic", "论文分享",
    "--images", f"{IMG_DIR}/framework2_page1.png",
    "--images", f"{IMG_DIR}/illustration-2_page1.png",
    "--images", f"{IMG_DIR}/retrieve_page1.png",
]

env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120, env=env)
print(result.stdout)
if result.returncode != 0:
    print("STDERR:", result.stderr[:500])
    sys.exit(result.returncode)

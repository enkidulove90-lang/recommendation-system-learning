"""Create (but never publicly publish) the Qwen-AgentWorld Xiaohongshu draft."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ASSET_DIR = ROOT / "redbook" / "assets" / "qwen_agentworld_draft"
NODE = shutil.which("node")
OPENCLI_MAIN = Path.home() / "AppData" / "Roaming" / "npm" / "node_modules" / "@jackwener" / "opencli" / "dist" / "src" / "main.js"

TITLE = "Qwen 把世界模型训练成 Agent"
BODY = """🤖 这篇开源论文在做什么？

Qwen-AgentWorld 把“预测下一步环境会发生什么”作为语言模型的训练目标。它覆盖 MCP、搜索、终端、软件工程、Android、Web、OS 7 类 Agent 环境。

✅ 训练路线

CPT 注入环境与世界知识 → SFT 激活 next-state prediction → RL 用 rubric + 规则奖励打磨模拟保真度。

📊 看图顺序

第 1 张：7 类环境统一到一个语言世界模型。
第 2 张：三阶段训练流程。
第 3–4 张：AgentWorldBench 与跨领域泛化结果。

🧭 最后一张不是装饰图

它从论文 PDF 的 123 篇 References 中筛出 6 条发展脉络，并要求每条都能在正文 Related Work / Introduction 找到作者引用；图谱中保留 cites 与 develops_from 两类边。

📄 论文
https://arxiv.org/abs/2606.24597

💻 官方 GitHub
https://github.com/QwenLM/Qwen-AgentWorld

#大模型 #智能体 #开源论文 #世界模型"""


def main() -> None:
    if not NODE or not OPENCLI_MAIN.exists():
        raise SystemExit("Node.js or OpenCLI entry point is unavailable")
    images = [ASSET_DIR / f"{i:02d}_paper_figure.jpg" for i in range(1, 5)]
    images.append(ASSET_DIR / "05_knowledge_graph_and_paper_details.png")
    missing = [str(path) for path in images if not path.exists()]
    if missing:
        raise SystemExit(f"Missing draft assets: {missing}")
    command = [
        NODE, str(OPENCLI_MAIN), "xiaohongshu", "publish", BODY,
        "--title", TITLE,
        "--images", ",".join(str(image) for image in images),
        "--draft", "true",
        "--site-session", "persistent",
        "--keep-tab", "true",
        "--format", "json",
    ]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    payload = {
        "title": TITLE,
        "draft": True,
        "images": [str(image) for image in images],
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    (ASSET_DIR / "opencli_draft_result.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    # Some Windows terminals still expose a GBK stdout. The persisted report
    # remains UTF-8; ASCII console JSON prevents a successful draft save from
    # being misreported as a script failure because the body contains emoji.
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    if result.returncode:
        raise SystemExit(result.stderr.strip() or result.stdout.strip())


if __name__ == "__main__":
    main()

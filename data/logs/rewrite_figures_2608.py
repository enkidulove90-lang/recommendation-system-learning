"""Rewrite LoopsBench figures.json with curated visually-rich figures."""
import json
import time
from pathlib import Path

path = Path("data/parsed/2608.00267/2608.00267_figures.json")
data = json.loads(path.read_text(encoding="utf-8"))

data["figures"] = [
    {
        "image_file": "images/728f8cc26e4d177bec5e5d04ffddcbbdb2aa97c9b8c2ee99cdae6e3aa9e94e87.jpg",
        "figure_type": "architecture",
        "description": "Figure 2: Overview of the LOOPSBENCH construction and evaluation pipeline (Native Provenance sources | Task Construction | Flow-aware Evaluation).",
        "source_section": "3 Task Construction / 5 Flow-aware Evaluation",
        "model": "Qwen2.5-VL-72B",
        "provider": "Zhipu",
    },
    {
        "image_file": "images/a098b89aeff7de7c4df6431b30f2eaa35c35f9bd578af946cfac465fefeb2521.jpg",
        "figure_type": "framework",
        "description": "Figure 1: Polar chart of model performance across LoopsBench domains (Opus-4.7 / GPT-5.5 / DS-V4-Pro / Gemini-3.1 / Grok-4.1) + top solve rates vs other benchmarks (LoopsBench 25.0%).",
        "source_section": "1 Introduction / Limitations of Existing Benchmarks",
        "model": "Qwen2.5-VL-72B",
        "provider": "Zhipu",
    },
    {
        "image_file": "images/6aa350561920d04c1e4853083d749e4463b58596535526b67ba6ccf7f96430dd.jpg",
        "figure_type": "model",
        "description": "Figure 3: Four prerequisite patterns in a materialized task (DAG of development units with structural dependencies, Django example).",
        "source_section": "3.2 Intra-Task Relation Construction",
        "model": "Qwen2.5-VL-72B",
        "provider": "Zhipu",
    },
    {
        "image_file": "images/47bde58e750f439abdd03e9e226b72dc429232ed275bcaa08afa89c147c5d107.jpg",
        "figure_type": "result",
        "description": "Figure 4: Flow-aware evaluation runtime (DAG progression over time t1-t6 with pass/frontier/broken states across test_*.py).",
        "source_section": "5 Flow-aware Evaluation",
        "model": "Qwen2.5-VL-72B",
        "provider": "Zhipu",
    },
    {
        "image_file": "images/1eb4e5831772033f4bed6e0d3240a02580599c6315f3e212789c049e5ada2391.jpg",
        "figure_type": "chart",
        "description": "Figure 5: Compaction sensitivity chart.",
        "source_section": "6 Experiments",
        "model": "Qwen2.5-VL-72B",
        "provider": "Zhipu",
    },
]
data["figures_count"] = 5
data["generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
data["note"] = "Manually curated for visual quality (overrides formula/config defaults). Order tuned so figure_type ranks as: architecture > framework > model > result > chart."

path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"rewrote {path.name} with {len(data['figures'])} figures")
for f in data["figures"]:
    print(f" - {f['figure_type']:12s} | {f['image_file'].split('/')[-1][:18]}")

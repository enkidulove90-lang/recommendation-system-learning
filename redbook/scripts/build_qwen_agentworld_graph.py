"""Build an evidence-backed Qwen-AgentWorld knowledge graph and draft assets.

The lineage view is intentionally constrained to papers that are both present in
the target PDF's References section and cited in its prose.  This prevents a
nice-looking but unverifiable "topic graph" from being passed off as a paper
lineage.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from shutil import copy2

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skills.citation_collector import CitationCollector
from skills.graph_builder import GraphBuilder


ARXIV_ID = "2606.24597"
TITLE = "Qwen-AgentWorld: Language World Models for General Agents"
PAPER_URL = f"https://arxiv.org/abs/{ARXIV_ID}"
GITHUB_URL = "https://github.com/QwenLM/Qwen-AgentWorld"
PARSED_DIR = ROOT / "data" / "parsed" / "2606.24597_qwen_agentworld"
ASSET_DIR = ROOT / "redbook" / "assets" / "qwen_agentworld_draft"

# Ordered from foundations to the closest LLM-agent work.  Every keyword is
# matched against a parsed bibliography title, never a generated title.
LINEAGE = [
    ("世界模型的通用智能蓝图", "path towards autonomous machine intelligence", "LeCun et al.", 2022),
    ("可学习环境中的规划", "mastering diverse domains through world models", "Hafner et al.", 2023),
    ("Web 场景的 LLM 世界模型", "secretly a world model of the internet", "Gu et al.", 2024),
    ("Web agent 环境动力学", "web agents with world models", "Chae et al.", 2025),
    ("语言世界建模提升 Agent", "world modelling improves language model agents", "Guo et al.", 2025),
    ("Agentic world modeling 的系统脉络", "agentic world modeling", "Chu et al.", 2026),
]

SOURCE_IMAGES = [
    "c4f210f438502db7c2fbf7b58c3ccb11e0a7b62971c9142763df056b31da0cfe.jpg",  # Fig. 2
    "4488f2678937a05f548c1ee3e13f3676409d01ae0e36670b4bad04c10eac7f92.jpg",  # Fig. 5
    "6ac62fb95af47d1ea1996bc4fe0346084593e1029f78eaee39b3ac04928292cb.jpg",  # Fig. 6
    "edfb8475a1d98162bb5e97df042f0d87928c31408b2faa610c5e62cf9f3304a5.jpg",  # Fig. 8
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simhei.ttf" if bold else r"C:\Windows\Fonts\simsun.ttc",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def clean_label(value: str, limit: int = 46) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    return value if len(value) <= limit else value[: limit - 1] + "…"


def context_for(body: str, citation: str) -> str:
    index = body.lower().find(citation.lower())
    if index < 0:
        return ""
    start = max(0, body.rfind(".", 0, index) + 1)
    end = body.find(".", index)
    if end < 0:
        end = min(len(body), index + 260)
    return re.sub(r"\s+", " ", body[start : end + 1]).strip()


def draw_wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, width: int,
                 text_font: ImageFont.FreeTypeFont, fill: str, line_gap: int = 8) -> int:
    words = text.split(" ")
    lines: list[str] = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if draw.textbbox((0, 0), trial, font=text_font)[2] <= width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    y = xy[1]
    for line in lines:
        draw.text((xy[0], y), line, font=text_font, fill=fill)
        y += text_font.size + line_gap
    return y


def render_evidence_card(anchors: list[dict], reference_count: int) -> Path:
    """Render the one allowed designed page: graph plus auditable paper details."""
    width, height = 1080, 1440
    image = Image.new("RGB", (width, height), "#FFFFFF")
    draw = ImageDraw.Draw(image)
    title_font, body_font, small_font = font(42, True), font(25), font(20)
    draw.text((64, 52), "Qwen-AgentWorld 知识图谱", font=title_font, fill="#15233D")
    draw.text((64, 112), f"来自论文 References 的 {reference_count} 篇文献｜发展脉络节点均在正文 §8 被引用", font=small_font, fill="#52627A")
    draw.line((64, 158, 1016, 158), fill="#DCE4EF", width=2)

    x, y, node_w, node_h = 86, 182, 720, 90
    for i, anchor in enumerate(anchors):
        year = anchor.get("year") or "?"
        fill = "#EEF5FF" if i < len(anchors) - 1 else "#E8F7F0"
        draw.rounded_rectangle((x, y, x + node_w, y + node_h), radius=18, fill=fill, outline="#B7C7DC", width=2)
        draw.ellipse((x + 26, y + 21, x + 78, y + 73), fill="#2B66A5")
        draw.text((x + 38, y + 30), str(year), font=small_font, fill="#FFFFFF")
        draw.text((x + 102, y + 13), anchor["stage"], font=font(22, True), fill="#1B3457")
        draw_wrapped(draw, (x + 102, y + 46), clean_label(anchor["title"], 68), node_w - 140, font(18), "#3C4D67", 1)
        if i < len(anchors) - 1:
            draw.line((x + node_w // 2, y + node_h, x + node_w // 2, y + node_h + 19), fill="#6A9ED2", width=5)
            draw.polygon([(x + node_w // 2 - 10, y + node_h + 12), (x + node_w // 2 + 10, y + node_h + 12), (x + node_w // 2, y + node_h + 27)], fill="#6A9ED2")
        y += node_h + 28

    target_y = y + 8
    draw.rounded_rectangle((64, target_y, 1016, target_y + 122), radius=24, fill="#15233D")
    draw.text((96, target_y + 18), "2026  Qwen-AgentWorld", font=font(31, True), fill="#FFFFFF")
    draw_wrapped(draw, (96, target_y + 64), "将语言世界模型扩展至 7 类 Agent 环境：CPT 注入、SFT 激活、RL 提升模拟保真度。", 850, font(18), "#DDE9F8", 2)

    evidence_y = target_y + 148
    draw.text((64, evidence_y), "图谱核验", font=font(28, True), fill="#15233D")
    evidence = "每条蓝色脉络：PDF 的 References 中可定位到完整条目，并在正文的 Related Work / Introduction 中有对应作者-年份引用；图谱 JSON 同时保留 cites 与 develops_from 两类边。"
    evidence_y = draw_wrapped(draw, (64, evidence_y + 40), evidence, 940, font(17), "#40526B", 4)
    draw.line((64, evidence_y + 10, 1016, evidence_y + 10), fill="#DCE4EF", width=2)
    footer_y = evidence_y + 26
    draw.text((64, footer_y), "论文", font=small_font, fill="#71809A")
    draw_wrapped(draw, (150, footer_y), PAPER_URL, 840, small_font, "#1B5AA1", 2)
    draw.text((64, footer_y + 62), "GitHub", font=small_font, fill="#71809A")
    draw_wrapped(draw, (150, footer_y + 62), GITHUB_URL, 840, small_font, "#1B5AA1", 2)
    draw.text((64, height - 42), f"生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')} · 图表与参考文献均来自原论文解析结果", font=font(16), fill="#71809A")
    out = ASSET_DIR / "05_knowledge_graph_and_paper_details.png"
    image.save(out, quality=95)
    return out


def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    markdown = (PARSED_DIR / f"{ARXIV_ID}.md").read_text(encoding="utf-8")
    body = markdown.split("## References", 1)[0]
    collector = CitationCollector()
    collected = collector.execute(
        arxiv_id=ARXIV_ID,
        parsed_dir=str(PARSED_DIR),
        metadata={"title": TITLE, "authors": ["Qwen Team"], "year": 2026,
                  "keywords": ["language world model", "agents", "reinforcement learning"]},
        sources=["pdf_refs"],
    )
    references = collected["references"]
    anchors: list[dict] = []
    for stage, phrase, citation, expected_year in LINEAGE:
        ref = next((item for item in references if phrase in item.get("title", "").lower()), None)
        if ref is None:
            raise RuntimeError(f"Missing lineage reference in parsed bibliography: {phrase}")
        evidence = context_for(body, citation)
        if not evidence:
            raise RuntimeError(f"Missing in-text citation evidence for: {citation}")
        anchors.append({"stage": stage, "citation": citation, "title": ref["title"],
                        "year": ref.get("year") or expected_year, "arxiv_id": ref.get("arxiv_id", ""),
                        "in_text_evidence": evidence})

    built = GraphBuilder().execute(
        arxiv_id=ARXIV_ID,
        references=references,
        citations=[],
        related=[],
        metadata={"title": TITLE, "authors": ["Qwen Team"], "year": 2026,
                  "keywords": ["language world model", "agents", "reinforcement learning"]},
    )
    if built.get("error") or not built.get("academic_graph"):
        raise RuntimeError(f"GraphBuilder failed: {built.get('error')}")

    graph = built["academic_graph"]
    target_id = f"paper_{ARXIV_ID}"
    for anchor in anchors:
        ref = next(item for item in references if item.get("title") == anchor["title"])
        node_id = GraphBuilder._make_node_id(ref)
        graph["citation_graph"]["edges"].append({
            "source": target_id,
            "target": node_id,
            "relation": "develops_from",
            "weight": 0.9,
            "description": f"{anchor['citation']}: {anchor['in_text_evidence']}",
        })
    graph["lineage_evidence"] = {
        "source": "MinerU Markdown: original PDF References + in-text citations",
        "reference_count": len(references),
        "anchors": anchors,
        "selection_rule": "reference title matches a declared lineage anchor and its author-year citation occurs in paper prose",
    }
    graph_path = Path(built["graph_path"])
    graph_path.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    evidence_path = graph_path.with_name("lineage_evidence.json")
    evidence_path.write_text(json.dumps(graph["lineage_evidence"], ensure_ascii=False, indent=2), encoding="utf-8")

    for index, source_name in enumerate(SOURCE_IMAGES, 1):
        copy2(PARSED_DIR / "images" / source_name, ASSET_DIR / f"{index:02d}_paper_figure.jpg")
    card = render_evidence_card(anchors, len(references))
    manifest = {
        "paper": {"arxiv_id": ARXIV_ID, "title": TITLE, "paper_url": PAPER_URL, "github_url": GITHUB_URL},
        "images": [str(ASSET_DIR / f"{i:02d}_paper_figure.jpg") for i in range(1, 5)] + [str(card)],
        "knowledge_graph": str(graph_path),
        "lineage_evidence": str(evidence_path),
        "reference_count": len(references),
        "lineage_anchor_count": len(anchors),
    }
    (ASSET_DIR / "draft_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

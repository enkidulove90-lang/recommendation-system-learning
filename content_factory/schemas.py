"""内容工厂数据模型与摘要抽取（防幻觉核心）。

支持两套既有摘要 schema：
  A) 简化版（data/summaries 中多数）：main_contribution / methodology /
     experimental_results / innovation_points / agent_relevance ...
  B) 11 维版（paper-summary-log 规范，部分文件）：problem_definition /
     innovations / modules / training / benchmark / limitations ...

抽取层对两套 schema 取并集别名，任一来源命中即可；若「方法 / 结果 / 问题动机」
三要素全部缺失，则抛出 InsufficientSourceError 阻断生成（防幻觉，绝不编造）。
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


class InsufficientSourceError(Exception):
    """摘要缺少生成故事化草稿所必需的事实字段，按防幻觉规则阻断。"""

    def __init__(self, missing: list[str]) -> None:
        self.missing = missing
        super().__init__(
            "摘要缺少必要事实字段，已按防幻觉规则阻断生成："
            + "、".join(missing)
        )


# ── 抽取小工具 ────────────────────────────────────────────────────────────
_PARADOX_KW = ["瓶颈", "限制", "挑战", "问题", "不足", "延迟", "计算", "难以", "无法", "塌缩", "退化", "缺失"]
_GAIN_KW = ["提升", "提高", "改善", "增益", "超过", "优于", "vs", "→", "涨", "增", "降"]


def _as_str(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, (list, tuple)):
        return "；".join(str(x) for x in v if x)
    if isinstance(v, dict):
        return "；".join(str(x) for x in v.values() if x)
    return str(v)


def _split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", _as_str(text)).strip()
    # 中文 / 英文句末切分
    parts = re.split(r"(?<=[。！？!?；;])", text)
    return [p.strip() for p in parts if p.strip()]


def _first_sentence_with_keywords(text: str, keywords: list[str]) -> str:
    for s in _split_sentences(text):
        if any(kw in s for kw in keywords):
            return s
    return ""


def _extract_key_result(text: str) -> str:
    """从实验结果文本中挑出最「反直觉」的一句：数字/增益词密度最高者。

    额外加权：含显式「从 X 提升/提高到 Y」结构的句子优先（它直接给出
    可量化的改进幅度，比罗列多个基线模型的句子更适合做高潮/可视化端点）。
    """
    sentences = _split_sentences(text)
    if not sentences:
        return ""
    best, best_score = "", -1.0
    for s in sentences:
        digits = len(re.findall(r"\d+(?:\.\d+)?%?", s))
        gains = sum(1 for kw in _GAIN_KW if kw in s)
        score = digits * 2 + gains * 3 + (0.5 if len(s) < 80 else 0)
        if re.search(r"从\s*[\d.]+%?\s*(?:提升|提高|增至|到)\s*[\d.]+%?", s):
            score += 10  # 显式改进幅度结构加权
        if score > best_score:
            best, best_score = s, score
    return best


def _truncate(text: str, n: int) -> str:
    text = _as_str(text)
    return text if len(text) <= n else text[: n - 1] + "…"


# ── 摘要归一模型 ──────────────────────────────────────────────────────────
@dataclass
class PaperSummary:
    """把任意 schema 的摘要归一为叙事引擎可用的四要素。"""

    raw: dict[str, Any]
    title_zh: str = ""
    title_en: str = ""
    problem: str = ""        # 钩子/反派：已知事实 BUT 悖论
    method: str = ""         # 冲突=方法：主角
    key_result: str = ""     # 高潮=反直觉发现
    limitations: str = ""     # 结局=开放问题（可选）
    innovations: list[str] = field(default_factory=list)

    # 审计：每要素命中的原始字段名（防幻觉可追溯）
    source_fields: dict[str, list[str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.raw = self.raw or {}
        self.title_zh = self._pick(["chinese_title", "title_zh", "title"])
        self.title_en = self._pick(["title_en", "title"])
        self.method = self._pick_method()
        self.key_result = self._pick_result()
        self.problem = self._extract_problem()
        self.limitations = self._pick(["limitations"]) or self._bench("limitations")
        self.innovations = self._list(["innovation_points", "innovations"])
        self._validate()

    # ── 抽取原语 ──
    def _pick(self, keys: list[str]) -> str:
        for k in keys:
            if k in self.raw and self.raw[k] not in (None, "", [], {}):
                return _as_str(self.raw[k])
        return ""

    def _list(self, keys: list[str]) -> list[str]:
        out: list[str] = []
        for k in keys:
            v = self.raw.get(k)
            if isinstance(v, list):
                out.extend(str(x) for x in v if x)
            elif isinstance(v, str) and v.strip():
                out.append(v)
        return out

    def _join_modules(self) -> str:
        mods = self.raw.get("modules")
        if isinstance(mods, list) and mods:
            parts = []
            for m in mods:
                name = _as_str(m.get("name"))
                role = _as_str(m.get("role"))
                parts.append(f"{name}：{role}" if name and role else (name or role))
            return "；".join(parts)
        return ""

    def _bench(self, key: str) -> str:
        bench = self.raw.get("benchmark")
        if isinstance(bench, dict) and key in bench:
            return _as_str(bench[key])
        return ""

    def _pick_method(self) -> str:
        cand = self._pick(["methodology", "method_details", "method"])
        if cand:
            return cand
        if self._join_modules():
            return self._join_modules()
        if self._bench("main_results"):
            return self._bench("main_results")
        return ""

    def _pick_result(self) -> str:
        cand = self._pick(["experimental_results", "main_results"])
        mc = self._pick(["main_contribution"])
        # 合并扫描：main_contribution 常含显式「从 X 提升/提高到 Y」 headline，
        # 优先于 experimental_results 里罗列多个基线的句子，得到可量化改进幅度。
        combined = (mc + " " + cand) if (mc and cand) else (cand or mc)
        if combined:
            return _extract_key_result(combined)
        if self._bench("main_results"):
            return _extract_key_result(self._bench("main_results"))
        return ""

    def _extract_problem(self) -> str:
        # 11 维：problem_definition 直接可用
        if "problem_definition" in self.raw:
            pd = self.raw["problem_definition"]
            text = _as_str(pd)
            if text:
                return text
        mc = self._pick(["main_contribution"])
        methodology = self._pick(["methodology"])
        paradox = _first_sentence_with_keywords(methodology, _PARADOX_KW)
        known = _first_sentence_with_keywords(methodology, []) or mc
        if paradox and known:
            return f"{known} 但{paradox}"
        return mc or methodology

    def _validate(self) -> None:
        missing = []
        if not self.title_zh and not self.title_en:
            missing.append("title")
        if not self.method:
            missing.append("method(方法/方法论)")
        if not self.key_result:
            missing.append("result(实验结果)")
        if not self.problem:
            missing.append("problem(问题动机)")
        if missing:
            raise InsufficientSourceError(missing)

    def as_facts(self) -> dict[str, str]:
        return {
            "title_zh": self.title_zh,
            "title_en": self.title_en,
            "problem": self.problem,
            "method": self.method,
            "key_result": self.key_result,
            "limitations": self.limitations,
            "innovations": "；".join(self.innovations),
        }


@dataclass
class StoryDraft:
    """四段式故事化草稿（ABT / Freytag / Six Steps 映射）。"""

    paper_id: str
    title_zh: str
    hook: str            # 问题/反派 — ABT 的 AND…BUT
    method_section: str  # 冲突=方法 — 主角入场
    climax_section: str  # 高潮=反直觉发现
    ending_section: str  # 结局=开放问题
    bound_fields: dict[str, list[str]] = field(default_factory=dict)

    @property
    def full_text(self) -> str:
        parts = [
            f"# {self.title_zh}",
            "",
            "## 为什么现在重要",
            self.hook,
            "",
            "## 我们怎么打",
            self.method_section,
            "",
            "## 最反直觉的 1 个数",
            self.climax_section,
            "",
            "## 它在哪会失效？",
            self.ending_section,
        ]
        return "\n".join(parts)


@dataclass
class TitleVariant:
    text: str
    score: int
    reasons: list[str] = field(default_factory=list)
    needs_rewrite: bool = False


@dataclass
class FactoryResult:
    paper_id: str
    story: StoryDraft
    titles: list[TitleVariant]
    chosen_title: str = ""
    packages: list[dict[str, Any]] = field(default_factory=list)
    # Stage 4/5/7/8 扩展产物（按需构建，默认空）
    visuals: list[Any] = field(default_factory=list)          # VizSpec 列表
    interactions: list[Any] = field(default_factory=list)     # InteractionSpec 列表
    distribution: list[Any] = field(default_factory=list)     # DistributionJob 列表
    analytics: dict[str, Any] = field(default_factory=dict)   # GA4/Metabase spec


# ── 摘要加载（对齐 data/summaries/<id>*_summary.json 命名） ───────────────
def find_summary_path(paper_id: str, summaries_dir: str | Path) -> Path | None:
    """glob `<id>*_summary.json`，优先精确名，其次带中文标题名，取最新。"""
    d = Path(summaries_dir)
    if not d.exists():
        return None
    exact = d / f"{paper_id}_summary.json"
    if exact.is_file():
        return exact
    matches = sorted(d.glob(f"{paper_id}*_summary.json"), key=lambda p: p.stat().st_mtime)
    return matches[-1] if matches else None


def load_summary(paper_id: str, summaries_dir: str | Path) -> tuple[PaperSummary, Path]:
    path = find_summary_path(paper_id, summaries_dir)
    if path is None:
        raise FileNotFoundError(f"未找到摘要文件：{summaries_dir}/{paper_id}*_summary.json")
    raw = json.loads(path.read_text(encoding="utf-8"))
    return PaperSummary(raw), path

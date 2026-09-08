"""Stage 3 标题工厂（M6 变体生成 + M7 评分门禁 + M8 线上 A/B 占位）。

本地启发式评分器（0–100，无需外部 API）：长度 / 数字 / power word / 好奇心缺口。
<70 触发 needs_rewrite 门禁。外部评分器（Sharethrough / CoSchedule / Headline Goat）
通过 `register_scorer` 插拔，线上 A/B 分流留给 Stage 7 的 @appnest/ab-test。
"""

from __future__ import annotations

import json
import os
import re
from string import Template
from typing import Callable, Optional

from .schemas import PaperSummary, TitleVariant

POWER_WORDS = ["颠覆", "揭秘", "终于", "实测", "硬核", "一文搞懂", "彻底", "背后", "真相", "冷启动", "天花板", "击穿"]
CURIOSITY_KW = ["？", "?", "如何", "为什么", "怎样", "背后", "究竟", "凭什么", "反直觉"]
CLICKBAIT = ["震惊", "疯传", "100%", "绝对", "人人", "必看", "赚翻"]

_TITLE_TPLS = [
    Template("我们用$method_label，把$metric从$X拉到$Y"),
    Template("$power：当$paradox_short，$method_label这样破局"),
    Template("$metric提升背后：$method_label做对了什么"),
    Template("推荐系统的$problem_short，被$method_label改写了"),
    Template("一个反直觉结论：$key_short"),
]


class TitleFactory:
    GATE = 70

    def __init__(self, external_scorer: Optional[Callable[[str], tuple[int, list[str]]]] = None) -> None:
        self._external = external_scorer
        # 缓存一篇论文的变体素材，避免重复解析
        self._cache: dict[str, TitleVariant] = {}

    def generate(self, s: PaperSummary, n: int = 5, use_llm: bool = False) -> list[TitleVariant]:
        variants = self._rule_variants(s)
        if use_llm and (os.getenv("DEEPSEEK_API_KEY") or self._external is None):
            llm_vars = self._llm_variants(s, n - len(variants))
            variants.extend(llm_vars)
        variants = variants[: max(n, 1)]
        # 评分 + 门禁
        scored = [self._score(v) for v in variants]
        scored.sort(key=lambda v: v.score, reverse=True)
        # 最优仍 < GATE 则标记重写
        if scored and scored[0].score < self.GATE:
            for v in scored:
                v.needs_rewrite = True
        return scored

    # ── 变体生成 ──
    def _rule_variants(self, s: PaperSummary) -> list[TitleVariant]:
        method_label = s.title_zh or self._short(s.method, 12)
        metric, x, y = self._extract_gain(s.key_result)
        paradox_short = self._short(self._paradox(s), 12)
        problem_short = self._short(s.problem, 8)
        key_short = self._issue_key_short(s)
        power = POWER_WORDS[0]
        out = []
        for tpl in _TITLE_TPLS:
            try:
                text = tpl.substitute(
                    method_label=method_label or "新框架",
                    metric=metric, x=x, y=y,
                    paradox_short=paradox_short or "旧瓶颈",
                    problem_short=problem_short or "老问题",
                    key_short=key_short or "一个反直觉结论",
                    power=power,
                )
            except Exception:
                continue
            out.append(TitleVariant(text=text, score=0))
        return out

    @staticmethod
    def _issue_key_short(s: PaperSummary) -> str:
        kr = s.key_result
        if not kr:
            return ""
        # 取关键结果里第一个含数字的短句
        for sent in re.split(r"[。；;]", kr):
            if re.search(r"\d", sent):
                return TitleFactory._short(sent, 18)
        return TitleFactory._short(kr, 18)

    def _llm_variants(self, s: PaperSummary, n: int) -> list[TitleVariant]:
        """用 DEEPSEEK_API_KEY 生成额外标题候选（facts-only，防幻觉）。

        仅当 use_llm=True 且存在 DEEPSEEK_API_KEY 时调用；无 key / 异常时
        静默回退到规则变体，保证门禁始终可跑通。
        """
        if n <= 0:
            return []
        key = os.getenv("DEEPSEEK_API_KEY")
        if not key:
            return []
        facts = {
            "论文标题": s.title_zh or s.title_en,
            "方法": self._short(s.method, 60),
            "关键结果": self._short(s.key_result, 80),
            "问题动机": self._short(s.problem, 60),
            "创新点": "；".join(s.innovations)[:80] if s.innovations else "",
        }
        facts_block = "\n".join(f"- {k}：{v}" for k, v in facts.items() if v)
        prompt = (
            f"你是科研内容标题编辑。基于以下论文事实，生成 {n} 个中文标题候选，"
            "每条 ≤60 字。要求：含具体数字/指标更佳；可用 power word 或好奇心缺口；"
            "严禁编造任何原文未给出的数字、指标或结论。只输出 JSON 数组，"
            '格式为 ["标题1","标题2",...]，不要其它文字。\n\n事实：\n' + facts_block
        )
        try:
            import openai  # 延迟导入，避免无网络环境硬依赖
        except Exception:
            return []
        try:
            client = openai.OpenAI(
                api_key=key, base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
            )
            resp = client.chat.completions.create(
                model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                messages=[
                    {"role": "system", "content": "只输出标题 JSON 数组，不得添加解释，不得编造事实。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.6,
            )
            out = resp.choices[0].message.content.strip()
            # 容错：剥离可能包裹的 ```json ``` 标记
            out = re.sub(r"^```(?:json)?|```$", "", out, flags=re.IGNORECASE).strip()
            arr = json.loads(out)
            titles = [str(t).strip() for t in arr if isinstance(t, (str, int, float)) and str(t).strip()]
            return [TitleVariant(text=t, score=0) for t in titles[:n]]
        except Exception:
            return []

    # ── 评分器 ──
    def _score(self, v: TitleVariant) -> TitleVariant:
        score, reasons = self._heuristic(v.text)
        if self._external is not None:
            try:
                ext_score, ext_reasons = self._external(v.text)
                reasons.append(f"[external] {ext_score}")
                score = max(score, ext_score)
            except Exception:
                pass
        v.score = max(0, min(100, score))
        v.reasons = reasons
        v.needs_rewrite = v.score < self.GATE
        return v

    @staticmethod
    def _heuristic(text: str) -> tuple[int, list[str]]:
        score = 0
        reasons: list[str] = []
        length = len(text)
        if length <= 60:
            score += 30
            reasons.append(f"长度 {length}≤60 +30")
        else:
            penalty = min(30, (length - 60) * 2)
            score -= penalty
            reasons.append(f"长度 {length}>60 -{penalty}")
        if re.search(r"\d", text):
            score += 15
            reasons.append("含数字 +15")
        if any(pw in text for pw in POWER_WORDS):
            score += 15
            reasons.append("含 power word +15")
        if any(ck in text for ck in CURIOSITY_KW):
            score += 20
            reasons.append("含好奇心缺口 +20")
        if any(cb in text for cb in CLICKBAIT):
            score -= 20
            reasons.append("含标题党词 -20")
        if not text.strip():
            score = 0
            reasons.append("空标题 0")
        return max(0, min(100, score)), reasons

    # ── 素材抽取 ──
    @staticmethod
    def _short(text: str, n: int) -> str:
        text = re.sub(r"\s+", "", text or "").strip()
        if len(text) <= n:
            return text
        cut = text[:n]
        for sep in ["，", "。", "：", "；", "、", ","]:
            idx = cut.rfind(sep)
            if idx >= 4:
                return cut[:idx]
        return cut[: n - 1] + "…"

    @staticmethod
    def _paradox(s: PaperSummary) -> str:
        from .schemas import _first_sentence_with_keywords, _PARADOX_KW
        return _first_sentence_with_keywords(s.problem, _PARADOX_KW) or s.problem

    @staticmethod
    def _extract_gain(text: str) -> tuple[str, str, str]:
        """从关键结果里粗提 (指标, 旧值, 新值)。

        优先匹配「[指标]从a提升[至/到]b」（指标名可选，兼容「从a提高到b」写法）；
        否则取所有百分号数字的最小/最大作为旧/新。
        """
        m = re.search(
            r"((?:[A-Za-z@\d]+)\s*)?从\s*([\d.]+%?)\s*"
            r"(?:提升|提高|增|涨|到)\s*(?:至|到)?\s*([\d.]+%?)",
            text,
        )
        if m:
            metric = (m.group(1) or "").strip() or "指标"
            return metric, m.group(2), m.group(3)
        pct = re.findall(r"(\d+(?:\.\d+)?)\s*%", text)
        if len(pct) >= 2:
            vals = [float(v) for v in pct]
            mm = re.search(r"([A-Za-z][A-Za-z@\d]*)\s*[:\-]", text)
            metric = mm.group(1) if mm else "指标"
            return metric, f"{min(vals)}%", f"{max(vals)}%"
        nums = re.findall(r"[\d.]+%?", text)
        if len(nums) >= 2:
            return "指标", nums[0], nums[-1]
        return "指标", "旧值", "新值"

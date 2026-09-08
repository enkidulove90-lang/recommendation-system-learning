"""Stage 1 叙事引擎（M1 叙事结构骨架 + M2 LLM 润色层）。

规则层（保结构 / 防幻觉）：用四段式模板把 PaperSummary 的事实填进
「问题 / 方法 / 实验 / 结论」骨架，每节标注命中的原始字段（bound_fields 可追溯）。
LLM 层（可选）：仅润色表达，不引入原文外数字；缺 key 时自动跳过。
"""

from __future__ import annotations

import os
from string import Template
from typing import Callable, Optional

from .schemas import PaperSummary, StoryDraft

# 四段式模板（报告 1/2/3：ABT + Freytag×IMRAD + Six Steps）
_HOOK_TPL = Template(
    "推荐系统里，$known_fact（AND）。"
    "但$paradox（BUT）。"
    "因此我们提出 $title（THEREFORE）——用 $method_short 把这个问题打穿。"
)
_METHOD_TPL = Template(
    "$method\n\n"
    "它不是堆模块，而是把「$problem_short」当成反派，让方法做主角一步步推进。"
)
_CLIMAX_TPL = Template(
    "最反直觉的 1 个数：$key_result。"
    "换算成直觉：相当于在 100 个相关结果里，精准多召回了好几个——"
    "而代价只是$paradox_short。"
)
_ENDING_TPL = Template(
    "它没有解决一切。$limitations\n\n"
    "真正该问的是：在 $open_scene 这种场景，它会不会失效？"
)


class NarrativeEngine:
    def __init__(self, polish: bool = False, llm_callable: Optional[Callable[[str, str], str]] = None) -> None:
        self.polish = polish
        self._llm = llm_callable

    def build(self, s: PaperSummary, paper_id: str = "") -> StoryDraft:
        known = self._sentence(s.method) or s.title_zh
        paradox = self._paradox_sentence(s)
        method_short = self._short(s.method, 24)
        problem_short = self._short(s.problem, 20)
        paradox_short = self._short(paradox, 18)
        key_result = s.key_result or "（原文未给出可量化的反直觉结果）"
        limitations = s.limitations or "它在哪些边界条件下会退化，论文未充分展开，这正是评论区可以补刀的地方。"
        open_scene = self._open_scene(s)

        hook = _HOOK_TPL.substitute(
            known_fact=known, paradox=paradox, title=s.title_zh, method_short=method_short
        )
        method_section = _METHOD_TPL.substitute(method=s.method, problem_short=problem_short)
        climax = _CLIMAX_TPL.substitute(key_result=key_result, paradox_short=paradox_short)
        ending = _ENDING_TPL.substitute(limitations=limitations, open_scene=open_scene)

        bound = {
            "hook": self._sources(s, ["problem", "method", "title"]),
            "method_section": self._sources(s, ["method"]),
            "climax_section": self._sources(s, ["key_result", "problem"]),
            # 结局=开放问题：优先绑定 limitations；缺失时绑定 method（问题边界即方法边界）
            "ending_section": self._sources(s, ["limitations"]) or self._sources(s, ["method"]),
        }

        if self.polish and (self._llm or os.getenv("DEEPSEEK_API_KEY")):
            hook = self._polish(hook, "钩子段落，勿增数字")
            method_section = self._polish(method_section, "方法段落，勿增数字")
            climax = self._polish(climax, "反直觉发现段落，可通俗类比但勿增数字")
            ending = self._polish(ending, "开放问题段落，勿增数字")

        return StoryDraft(
            paper_id=paper_id,
            title_zh=s.title_zh,
            hook=hook,
            method_section=method_section,
            climax_section=climax,
            ending_section=ending,
            bound_fields=bound,
        )

    # ── 抽取辅助 ──
    @staticmethod
    def _sentence(text: str, idx: int = 0) -> str:
        parts = [p.strip() for p in text.replace("；", "。").split("。") if p.strip()]
        return parts[idx] if parts else ""

    @staticmethod
    def _paradox_sentence(s: PaperSummary) -> str:
        from .schemas import _first_sentence_with_keywords, _PARADOX_KW
        para = _first_sentence_with_keywords(s.problem, _PARADOX_KW)
        return para or _first_sentence_with_keywords(s.method, _PARADOX_KW) or s.problem

    @staticmethod
    def _short(text: str, n: int) -> str:
        import re as _re
        text = _re.sub(r"\s+", "", text or "").strip()
        if len(text) <= n:
            return text
        cut = text[:n]
        for sep in ["，", "。", "：", "；", "、", ","]:
            idx = cut.rfind(sep)
            if idx >= 4:
                return cut[:idx]
        return cut[: n - 1] + "…"

    @staticmethod
    def _open_scene(s: PaperSummary) -> str:
        if s.innovations:
            return "数据分布漂移或冷启动"
        return "长尾与冷启动"

    @staticmethod
    def _sources(s: PaperSummary, keys: list[str]) -> list[str]:
        out = []
        for k in keys:
            v = getattr(s, k, "")
            if isinstance(v, list):
                v = "；".join(v)
            if v:
                out.append(k)
        return out

    # ── 可选 LLM 润色（仅表达，不增事实）──
    def _polish(self, text: str, instruction: str) -> str:
        if self._llm:
            try:
                return self._llm(text, "仅润色表达，" + instruction)
            except Exception:
                return text
        try:
            import openai  # 延迟导入，避免无网络环境硬依赖
        except Exception:
            return text
        key = os.getenv("DEEPSEEK_API_KEY")
        if not key:
            return text
        try:
            client = openai.OpenAI(
                api_key=key, base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
            )
            resp = client.chat.completions.create(
                model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                messages=[
                    {"role": "system", "content": "你是科研故事化编辑。仅润色表达，不得新增任何数字、指标或原文外的结论。"},
                    {"role": "user", "content": f"{instruction}：\n{text}"},
                ],
                temperature=0.3,
            )
            out = resp.choices[0].message.content.strip()
            return out or text
        except Exception:
            return text

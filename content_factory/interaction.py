"""Stage 5 交互组件注入（M9 代码 Playground / M10 测验投票 / M11 参数滑块）。

选型对齐 docs/content-factory-engineering.md：
  M9  Replit / Trinket / CodePen iframe（h=600）  报告 18
  M10 Apester(quiz/poll) / CoRise MCQ block        报告 19 / 20
  M11 Idyll / Observable Inputs 参数滑块           报告 6 / 10

防幻觉铁律：quiz / poll 的题干与正确选项必须来自摘要事实（bound_fields）；
代码 playground 仅提供「方法描述的伪代码骨架」，明确标注为示意，不冒充可运行实现；
参数滑块为配置（无真实逐点曲线时滑块仅声明取值范围）。外部服务（Replit/Apester/Idyll）
需前端或 API key，本模块产出结构化 payload + 可注入的 iframe/HTML 片段。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .schemas import PaperSummary, StoryDraft


@dataclass
class InteractionSpec:
    id: str
    kind: str            # code_playground | quiz | poll | param_slider
    tool: str            # Replit | Apester | Idyll | Observable
    title: str
    payload: dict[str, Any] = field(default_factory=dict)
    embed: dict[str, Any] = field(default_factory=dict)
    bound_fields: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class InteractionFactory:
    # ── M9：代码 Playground（Replit/Trinket/CodePen iframe, h=600）──
    def code_playground(self, s: PaperSummary, code: str | None = None,
                        tool: str = "Replit") -> InteractionSpec:
        if not code:
            code = self._pseudo_from_method(s)
        # 约定：把代码托管到指定 editor 后，用其分享链接替换 src；此处给占位 iframe
        iframe = (
            f'<iframe src="ABOUT:REPLACE_WITH_{tool.upper()}_SHARE_URL" '
            f'title="{s.title_zh or "playground"}" width="100%" height="600" '
            f'frameborder="0"></iframe>'
        )
        return InteractionSpec(
            id="ix_code_playground", kind="code_playground", tool=tool,
            title=f"动手试：{s.title_zh or s.title_en}",
            payload={"language": "python", "code": code, "height": 600,
                     "fallback": "打不开请见原论文伪代码 / 开源 repo"},
            embed={"type": "iframe", "html": iframe,
                    "note": "将 src 替换为真实 Replit/Trinket/CodePen 分享链接"},
            bound_fields=["method"],
        )

    # ── M10：测验（Apester quiz / CoRise MCQ）──
    def quiz(self, s: PaperSummary, tool: str = "Apester") -> InteractionSpec:
        # 题干来自「关键结果」，正确选项为报告结论，干扰项标注为未证实
        question = f"关于《{s.title_zh or s.title_en}》的关键结果，下列说法正确的是？"
        correct = (s.key_result or "本文给出了可量化的提升")[:80]
        options = [
            {"text": correct, "correct": True},
            {"text": "本文在所有数据集上均无提升（与报告相反）", "correct": False},
            {"text": "本文完全未做实验验证", "correct": False},
        ]
        payload = {
            "type": "quiz", "question": question, "options": options,
            "feedback": "正确选项来自论文关键结果字段，其余为干扰项。",
        }
        iframe = (f'<div class="apester-quiz" data-question="{question}">'
                  f'（Apester unit 占位：注入 quiz unit id 后渲染）</div>')
        return InteractionSpec(
            id="ix_quiz", kind="quiz", tool=tool, title="读后小测",
            payload=payload, embed={"type": "apester", "html": iframe},
            bound_fields=["key_result"],
        )

    # ── M10：投票（Apester poll）──
    def poll(self, s: PaperSummary, tool: str = "Apester") -> InteractionSpec:
        question = f"你最关心《{s.title_zh or s.title_en}》能解决哪类问题？"
        options = [s.problem[:40] or "推荐系统老问题", "冷启动", "长尾分布", "计算开销"]
        payload = {"type": "poll", "question": question, "options": options}
        iframe = (f'<div class="apester-poll" data-question="{question}">'
                  f'（Apester poll unit 占位）</div>')
        return InteractionSpec(
            id="ix_poll", kind="poll", tool=tool, title="读者立场投票",
            payload=payload, embed={"type": "apester", "html": iframe},
            bound_fields=["problem"],
        )

    # ── M11：参数滑块（Idyll / Observable Inputs）──
    def param_slider(self, s: PaperSummary, tool: str = "Idyll") -> InteractionSpec:
        # 以「预算/约束系数」为例声明滑块（c_target 类参数）；无真实曲线时仅声明范围
        sliders = [
            {"name": "c_target", "label": "预算约束系数", "min": 0.0, "max": 1.0,
             "step": 0.05, "value": 0.8,
             "note": "示例参数；真实联动曲线需论文提供逐点数据"},
        ]
        payload = {"sliders": sliders,
                   "readout": "拖动摇杆观察指标变化（需论文提供响应曲线）"}
        iframe = ('<div class="idyll-slider" data-param="c_target" '
                  'data-min="0" data-max="1" data-step="0.05" data-value="0.8">'
                  '（Idyll/Observable 滑块占位）</div>')
        return InteractionSpec(
            id="ix_param_slider", kind="param_slider", tool=tool,
            title="调参看效果", payload=payload,
            embed={"type": "idyll", "html": iframe}, bound_fields=["method"],
        )

    # ── 辅助：由方法描述生成伪代码骨架（明确标注为示意）──
    @staticmethod
    def _pseudo_from_method(s: PaperSummary) -> str:
        method = (s.method or "本文方法")[:120]
        return (
            "# 示意伪代码（基于摘要方法描述，非可运行实现）\n"
            "def propose_pipeline():\n"
            f"    # 方法要点：{method}\n"
            "    representation = encode(items, users)\n"
            "    aligned = knowledge_alignment(representation)\n"
            "    return rank(aligned)\n"
        )


def build_all(s: PaperSummary) -> list[InteractionSpec]:
    """一键产出 Stage 5 全部交互组件 spec。"""
    f = InteractionFactory()
    return [f.code_playground(s), f.quiz(s), f.poll(s), f.param_slider(s)]

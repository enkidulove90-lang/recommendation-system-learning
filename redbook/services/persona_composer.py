"""Persona-driven Xiaohongshu copy composition without publishing side effects."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

import yaml


PERSONA_DIR = Path(__file__).resolve().parent.parent / "personas"
EVIDENCE_POLICY_PATH = Path(__file__).resolve().parent.parent / "config" / "content_evidence_policy.yaml"
LINKS = "论文：{paper}\nPDF：{pdf}{github}"


@dataclass(frozen=True)
class ContentPersona:
    id: str
    name: str
    audience: str
    title_patterns: tuple[str, ...]
    sections: tuple[str, ...]
    topics: tuple[str, ...]
    comment_prompt: str
    prompt: str
    strategy: dict[str, Any]


@dataclass(frozen=True)
class PostDraft:
    persona_id: str
    requested_persona_id: str
    persona_selection_reason: str
    title: str
    body: str
    topics: tuple[str, ...]
    comment_prompt: str
    generation_prompt: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "persona_id": self.persona_id, "title": self.title, "body": self.body,
            "requested_persona_id": self.requested_persona_id,
            "persona_selection_reason": self.persona_selection_reason,
            "topics": list(self.topics), "comment_prompt": self.comment_prompt,
            "generation_prompt": self.generation_prompt,
        }


class PersonaCatalog:
    def __init__(self, root: Path = PERSONA_DIR) -> None:
        self.root = root

    def list(self) -> list[ContentPersona]:
        return [self.load(path.stem) for path in sorted(self.root.glob("*.yaml"))]

    def load(self, persona_id: str) -> ContentPersona:
        path = self.root / f"{persona_id}.yaml"
        if not path.is_file():
            available = ", ".join(item.id for item in self.list())
            raise ValueError(f"Unknown persona '{persona_id}'. Available: {available}")
        value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return ContentPersona(
            id=str(value["id"]), name=str(value["name"]), audience=str(value["audience"]),
            title_patterns=tuple(value.get("title_patterns", ())), sections=tuple(value.get("sections", ())),
            topics=tuple(value.get("topics", ())), comment_prompt=str(value.get("comment_prompt", "")),
            prompt=str(value.get("prompt", "")),
            strategy=dict(value.get("strategy", {})),
        )


class PersonaPostComposer:
    """Creates distinct post structures while preserving paper-source boundaries."""

    section_aliases = {
        "contribution": ("主要贡献", "核心贡献", "main contribution"),
        "innovation": ("创新点", "创新", "innovation"),
        "method": ("方法论", "核心方法", "methodology", "method"),
        "datasets": ("benchmark", "数据集", "实验设置"),
        "results": ("实验结果", "实验效果", "结果", "experimental results"),
        "relevance": ("借鉴", "agent relevance", "启发"),
    }

    def __init__(self, catalog: PersonaCatalog | None = None) -> None:
        self.catalog = catalog or PersonaCatalog()

    def _resolve_persona(self, requested_persona_id: str, github_url: str) -> tuple[ContentPersona, str]:
        """Avoid a reproduction-first framing when the paper has no official code."""
        if requested_persona_id == "implementation_reviewer" and not github_url.strip():
            return (
                self.catalog.load("research_translator"),
                "无官方代码：从复现审稿人自动切换为论文解读，避免制造可复现性预期。",
            )
        return self.catalog.load(requested_persona_id), "使用请求的人设。"

    @staticmethod
    def _evidence_policy() -> str:
        try:
            value = yaml.safe_load(EVIDENCE_POLICY_PATH.read_text(encoding="utf-8")) or {}
        except OSError:
            return ""
        mandatory = "\n".join(f"- {item}" for item in value.get("mandatory_rules", ()))
        limits = "\n".join(f"- {item}" for item in value.get("non_transferable_claims", ()))
        return f"研究证据约束（{value.get('scope', '')}）：\n{mandatory}\n不可外推：\n{limits}"

    @staticmethod
    def _clean(value: str, limit: int = 220) -> str:
        value = re.sub(r"\*+", "", value)
        value = re.sub(r"\s+", " ", value).strip(" -：:。")
        return value[:limit].rstrip("，,；; ")

    def _sections(self, summary: str) -> dict[str, str]:
        chunks = re.split(r"^##\s+", summary, flags=re.MULTILINE)
        values: dict[str, str] = {}
        for chunk in chunks:
            heading, _, text = chunk.partition("\n")
            normalized = heading.casefold()
            for key, aliases in self.section_aliases.items():
                if key not in values and any(alias.casefold() in normalized for alias in aliases):
                    values[key] = self._clean(text)
        return values

    @staticmethod
    def _title_from_summary(summary: str) -> str:
        match = re.search(r"^#\s+(.+)$", summary, re.MULTILINE)
        return match.group(1).strip() if match else "这篇新论文"

    @staticmethod
    def _short_title(title: str) -> str:
        head = re.split(r"[：:]", title, maxsplit=1)[0].strip()
        if len(head) <= 10:
            return head
        # Avoid chopping an English model name into an unreadable fragment.
        words = [word for word in re.split(r"[-_\s]+", head) if word]
        if len(words) > 1:
            compact = "-".join(words[:2])
            if len(compact) <= 10:
                return compact
        return head[:10].rstrip("-_")

    @staticmethod
    def _bullet(value: str, fallback: str) -> str:
        return value if value else fallback

    def build_generation_prompt(self, persona: ContentPersona, facts: dict[str, str], paper_title: str) -> str:
        evidence = json.dumps(facts, ensure_ascii=False, indent=2)
        strategy = json.dumps(persona.strategy, ensure_ascii=False, indent=2)
        return (
            f"你将以‘{persona.name}’身份，为{persona.audience}写一篇小红书图文正文。\n"
            f"角色要求：\n{persona.prompt}\n\n"
            f"该 persona 的结构化创作策略（必须遵守）：\n{strategy}\n\n"
            f"{self._evidence_policy()}\n\n"
            "硬约束：只使用下列事实；缺失处写‘原文未披露’；标题不超过20个汉字；"
            "正文使用真实换行、每段不超过3句；链接单独成段；输出 JSON，字段为 title/body/topics/comment_prompt。\n"
            f"论文标题：{paper_title}\n事实：\n{evidence}"
        )

    def compose(self, summary: str, arxiv_id: str, persona_id: str = "research_translator", github_url: str = "",
                paper_title: str = "") -> PostDraft:
        persona, selection_reason = self._resolve_persona(persona_id, github_url)
        facts = self._sections(summary)
        title_source = paper_title or self._title_from_summary(summary)
        short_title = self._short_title(title_source)
        title = persona.title_patterns[0].format(short_title=short_title)[:20]
        problem = self._bullet(facts.get("contribution", ""), "原文未披露清晰的问题定义")
        method = self._bullet(facts.get("method", facts.get("innovation", "")), "原文未披露完整方法细节")
        evidence = self._bullet(facts.get("results", facts.get("datasets", "")), "原文未披露可直接引用的结果")
        relevance = self._bullet(facts.get("relevance", ""), "可从问题定义、方法设计和实验设置三个维度继续阅读")
        reproducibility = self._bullet(facts.get("datasets", ""), "代码、数据和完整实验条件以论文及官方仓库为准")
        links = LINKS.format(
            paper=f"https://arxiv.org/abs/{arxiv_id}", pdf=f"https://arxiv.org/pdf/{arxiv_id}",
            github=f"\nGitHub：{github_url}" if github_url else "\nGitHub：暂无官方代码",
        )
        formats = {
            "research_translator": f"🎓 论文在解决什么？\n{problem}\n\n✨ 核心亮点\n• {problem}\n• {method}\n\n🧠 方法拆解\n{method}\n\n📊 关键实验\n{evidence}\n\n📝 阅读注释\n{relevance}\n\n💻 代码状态\n{'已提供官方 GitHub，见文末链接。' if github_url else '暂无官方代码；不要把匿名数据或第三方仓库当作官方实现。'}",
            "implementation_reviewer": f"🔍 复现判断\n{problem}\n\n核心模块\n{method}\n\n实验依据\n{evidence}\n\n复现信息\n{reproducibility}\n\n⚠️ 边界\n没有明示的参数、代码或数据，不补写推测。",
            "industry_analyst": f"一个问题：这条路线为什么值得关注？\n{problem}\n\n我会先问三个问题\n1. 它要替换或补强哪一环？\n2. 方法怎么落到系统里？\n3. 证据是否支撑这个判断？\n\n论文的回答\n{method}\n\n已验证的证据\n{evidence}\n\n可能的影响（推断）\n{relevance}",
            "study_coach": f"读这篇前，先抓四件事\n\n① 问题\n{problem}\n\n② 方法\n{method}\n\n③ 证据\n{evidence}\n\n④ 读完后可迁移什么\n{relevance}\n\n建议：带着‘它比什么基线好、为何会更好’回到原图和实验表核对。",
            "evidence_auditor": f"主张\n{problem}\n\n证据链\n{evidence}\n\n方法与对照\n{method}\n\n复现边界\n{reproducibility}\n\n结论\n目前能确认的是论文报告的结果；外推到其他任务前仍需验证。",
            "weekly_curator": f"为什么选它\n{problem}\n\n一句话看懂\n方法：{method}\n证据：{evidence}\n\n适合谁读\n{relevance}\n\n收藏前先看原图、实验表和代码状态。",
        }
        body = f"{formats[persona.id]}\n\n📎 论文与代码\n{links}"
        return PostDraft(
            persona_id=persona.id, requested_persona_id=persona_id, persona_selection_reason=selection_reason,
            title=title, body=body, topics=persona.topics,
            comment_prompt=persona.comment_prompt, generation_prompt=self.build_generation_prompt(persona, facts, title_source),
        )

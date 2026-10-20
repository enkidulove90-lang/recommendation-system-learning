from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


CONTROLLED_CATEGORIES = {
    "推荐系统",
    "多模态推荐",
    "知识图谱",
    "冷启动",
    "生成式推荐",
    "基础推荐算法",
    "图对比学习",
    "论文速递",
    "AI",
    "大模型与智能体",
    "检索增强生成",
    "学术检索",
    "跨学科与基础",
}
CONTROLLED_VENUE_TYPES = {"会议", "期刊", "arXiv预印本"}
_CJK = re.compile(r"[\u3400-\u9fff]")


class PaperInfo(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    canonical_id: str = ""
    title: str
    chinese_title: str = ""
    authors: list[str] = Field(default_factory=list)
    paper_url: str
    code_url: str = ""

    @field_validator("paper_url", "code_url")
    @classmethod
    def validate_web_url(cls, value: str) -> str:
        if value and not value.startswith(("http://", "https://")):
            raise ValueError("links must use http or https")
        return value


class Classification(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    categories: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    venue_type: str = "arXiv预印本"
    venue_name: str = ""


class ArticleSections(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    introduction: str = ""
    method: str = ""
    experiments: str = ""
    conclusion: str = ""
    references: list[str] = Field(default_factory=list)


class ArticleFigure(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    path: str
    sha256: str
    section: Literal["introduction", "method", "experiments", "conclusion"]
    explanation: str


class PaperArticle(BaseModel):
    schema_version: int = 1
    paper: PaperInfo
    classification: Classification
    article: ArticleSections
    figures: list[ArticleFigure] = Field(default_factory=list)


@dataclass(frozen=True, slots=True)
class QualityIssue:
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class QualityResult:
    issues: tuple[QualityIssue, ...]

    @property
    def publishable(self) -> bool:
        return not self.issues

    @property
    def issue_codes(self) -> list[str]:
        return [issue.code for issue in self.issues]


def parse_article_payload(raw: str) -> PaperArticle:
    text = raw.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        text = fenced.group(1)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"DeepSeek response is not valid JSON: {exc.msg}") from exc
    return PaperArticle.model_validate(payload)


def normalize_classification(classification: Classification) -> tuple[Classification, list[str]]:
    categories = [
        category for category in classification.categories if category in CONTROLLED_CATEGORIES
    ]
    warnings: list[str] = []
    if not categories:
        categories = ["推荐系统", "论文速递"]
        warnings.append("classification_fallback")
    elif categories[0] not in {"推荐系统", "AI", "跨学科与基础"}:
        categories.insert(0, "推荐系统")
    categories = list(dict.fromkeys(categories))

    tags = list(dict.fromkeys(tag for tag in classification.tags if tag))
    if "论文速读" not in tags:
        tags.insert(0, "论文速读")
    venue_type = classification.venue_type
    if venue_type not in CONTROLLED_VENUE_TYPES:
        venue_type = "arXiv预印本"
        warnings.append("venue_type_fallback")
    return (
        classification.model_copy(
            update={
                "categories": categories,
                "tags": tags,
                "venue_type": venue_type,
            }
        ),
        warnings,
    )


def validate_article(article: PaperArticle, *, artifact_root: str | Path) -> QualityResult:
    issues: list[QualityIssue] = []
    sections = article.article
    for field_name in ("introduction", "method", "experiments", "conclusion"):
        if not getattr(sections, field_name).strip():
            issues.append(
                QualityIssue(
                    f"{field_name}_required",
                    f"The {field_name} section is required.",
                )
            )
    if not sections.references:
        issues.append(QualityIssue("references_required", "At least one reference is required."))
    if not article.paper.paper_url:
        issues.append(QualityIssue("paper_url_required", "A paper URL is required."))
    if not article.figures:
        issues.append(QualityIssue("figure_required", "At least one paper figure is required."))

    root = Path(artifact_root).resolve()
    for index, figure in enumerate(article.figures, 1):
        candidate = (root / figure.path).resolve()
        if not candidate.is_relative_to(root) or not candidate.is_file():
            issues.append(
                QualityIssue("figure_missing", f"Figure {index} does not exist in the task bundle.")
            )
            continue
        actual_hash = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if actual_hash != figure.sha256:
            issues.append(
                QualityIssue("figure_hash_mismatch", f"Figure {index} hash does not match.")
            )
        explanation = figure.explanation.strip()
        if len(explanation) < 24 or not _CJK.search(explanation):
            issues.append(
                QualityIssue(
                    "figure_explanation_invalid",
                    f"Figure {index} needs a substantive Chinese explanation.",
                )
            )
    return QualityResult(tuple(issues))


def _render_figures(article: PaperArticle, section: str, label: str) -> str:
    rendered: list[str] = []
    matching = [figure for figure in article.figures if figure.section == section]
    for index, figure in enumerate(matching, 1):
        basename = Path(figure.path).name
        public_path = f"/images/papers/{article.paper.canonical_id or 'paper'}/{basename}"
        rendered.extend(
            [
                f"![{label} {index}]({public_path})",
                "",
                figure.explanation.strip(),
                "",
            ]
        )
    return "\n".join(rendered).rstrip()


def render_article_markdown(article: PaperArticle) -> str:
    classification, _warnings = normalize_classification(article.classification)
    title = article.paper.chinese_title or article.paper.title
    categories = ", ".join(classification.categories)
    tags = ", ".join(classification.tags)
    links = [f"[论文链接]({article.paper.paper_url})"]
    if article.paper.code_url:
        links.append(f"[代码链接]({article.paper.code_url})")

    parts = [
        "---",
        f"title: {title}",
        f"slug: paper-{article.paper.canonical_id or 'draft'}",
        f"arxiv_id: {article.paper.canonical_id}",
        f"venue_type: {classification.venue_type}",
        f"venue_name: {classification.venue_name}",
        f"categories: [{categories}]",
        f"tags: [{tags}]",
        "---",
        "",
        " · ".join(links),
        "",
        "## 一、研究背景与问题",
        "",
        article.article.introduction.strip(),
    ]
    intro_figures = _render_figures(article, "introduction", "背景图")
    if intro_figures:
        parts.extend(["", intro_figures])
    parts.extend(["", "## 二、方法", "", article.article.method.strip()])
    method_figures = _render_figures(article, "method", "方法图")
    if method_figures:
        parts.extend(["", method_figures])
    parts.extend(["", "## 三、实验", "", article.article.experiments.strip()])
    experiment_figures = _render_figures(article, "experiments", "实验图")
    if experiment_figures:
        parts.extend(["", experiment_figures])
    parts.extend(["", "## 四、总结", "", article.article.conclusion.strip()])
    conclusion_figures = _render_figures(article, "conclusion", "总结图")
    if conclusion_figures:
        parts.extend(["", conclusion_figures])
    parts.extend(["", "## References", ""])
    parts.extend(f"- {reference}" for reference in article.article.references)
    return "\n".join(parts).rstrip() + "\n"

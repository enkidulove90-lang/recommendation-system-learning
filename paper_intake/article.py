from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic import ValidationError

from .reference_candidates import (
    RELATED_READING_END,
    RELATED_READING_START,
    strip_generated_related_reading,
)

if TYPE_CHECKING:
    from .reference_links import ResolutionResult


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


class ArticlePayloadError(ValueError):
    """A JSON or schema error safe to persist without echoing model inputs."""

    def __init__(self, message: str, details: list[dict[str, str]]):
        super().__init__(message)
        self.details = details


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
    year: str = ""
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


class ReferenceChoice(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    ref_id: str = Field(min_length=1)
    reason: str = Field(min_length=1)


@dataclass(frozen=True, slots=True)
class GenerationEnvelope:
    article: PaperArticle
    reference_choices: list[ReferenceChoice] | None
    ranking_diagnostic: str | None = None


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


def _extract_json_object(text: str) -> str:
    start = text.find("{")
    if start < 0:
        return text
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return text[start:]


def repair_json_payload(raw: str) -> str:
    """Repair formatting only; never invent or rename semantic fields."""
    text = raw.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        text = fenced.group(1)
    text = _extract_json_object(text)
    return re.sub(r",\s*([}\]])", r"\1", text)


def parse_article_payload(raw: str) -> PaperArticle:
    text = repair_json_payload(raw)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        details = [{"loc": "$", "type": "json_invalid", "msg": f"{exc.msg} at line {exc.lineno} column {exc.colno}"}]
        raise ArticlePayloadError("DeepSeek response is not valid JSON.", details) from exc
    try:
        return PaperArticle.model_validate(payload)
    except ValidationError as exc:
        details = [
            {
                "loc": ".".join(str(part) for part in item["loc"]),
                "type": str(item["type"]),
                "msg": str(item["msg"]),
            }
            for item in exc.errors(include_url=False, include_input=False)
        ]
        summary = "; ".join(f"{item['loc']}: {item['msg']}" for item in details)
        raise ArticlePayloadError(f"DeepSeek article schema validation failed: {summary}", details) from exc


def generation_output_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "article": PaperArticle.model_json_schema(),
            "reference_choices": {
                "type": "array",
                "minItems": 2,
                "maxItems": 2,
                "items": ReferenceChoice.model_json_schema(),
            },
        },
        "required": ["article", "reference_choices"],
        "additionalProperties": False,
    }


def parse_generation_envelope(raw: str, eligible_ids: set[str]) -> GenerationEnvelope:
    text = repair_json_payload(raw)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        details = [
            {
                "loc": "$",
                "type": "json_invalid",
                "msg": f"{exc.msg} at line {exc.lineno} column {exc.colno}",
            }
        ]
        raise ArticlePayloadError("DeepSeek response is not valid JSON.", details) from exc

    is_legacy_article = isinstance(payload, dict) and "paper" in payload
    article_payload = payload if is_legacy_article else payload.get("article")
    article = parse_article_payload(json.dumps(article_payload, ensure_ascii=False))
    if is_legacy_article or "reference_choices" not in payload:
        return GenerationEnvelope(
            article=article,
            reference_choices=None,
            ranking_diagnostic="reference_selection_missing",
        )

    raw_choices = payload.get("reference_choices")
    if not isinstance(raw_choices, list) or len(raw_choices) != 2:
        return GenerationEnvelope(article, None, "reference_selection_invalid")
    try:
        choices = [ReferenceChoice.model_validate(item) for item in raw_choices]
    except (ValidationError, TypeError):
        return GenerationEnvelope(article, None, "reference_selection_invalid")
    ids = [choice.ref_id for choice in choices]
    if len(set(ids)) != 2 or any(ref_id not in eligible_ids for ref_id in ids):
        return GenerationEnvelope(article, None, "reference_selection_invalid")
    return GenerationEnvelope(article=article, reference_choices=choices)


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
    venue_aliases = {
        "arxiv预印本": "arXiv预印本",
        "arxiv": "arXiv预印本",
        "会议论文": "会议",
        "期刊论文": "期刊",
    }
    venue_type = venue_aliases.get(classification.venue_type.casefold(), classification.venue_type)
    venue_name = classification.venue_name or ""
    conference_name = re.search(
        r"\b(?:ACL|KDD|WWW|SIGIR|RECSYS|ICML|ICLR|WSDM|CIKM|ICDE|UMAP|NEURIPS|AAAI|IJCAI)\b|ACM\s+MM|WEB\s+CONFERENCE",
        venue_name,
        re.I,
    )
    journal_name = re.search(r"\b(?:JOURNAL|TRANSACTIONS|TORS|TOIS)\b|期刊", venue_name, re.I)
    if venue_type == "arXiv预印本" and (conference_name or journal_name):
        venue_type = "会议" if conference_name else "期刊"
        warnings.append("venue_type_corrected_from_venue")
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


def publication_year(article: PaperArticle) -> str:
    """Return the best available paper year, never the website publish year."""
    explicit = str(article.classification.year or "").strip()
    if re.fullmatch(r"(?:19|20)\d{2}", explicit):
        return explicit
    venue_year = re.search(r"(?:19|20)\d{2}", article.classification.venue_name or "")
    if venue_year:
        return venue_year.group(0)
    arxiv = re.fullmatch(r"(\d{2})(?:\d{2})\.\d+(?:v\d+)?", article.paper.canonical_id or "")
    if arxiv:
        return str(2000 + int(arxiv.group(1)))
    return ""


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


def render_related_reading(result: "ResolutionResult") -> str:
    if result.mode == "omitted" or not result.references:
        return ""
    heading = "延伸阅读" if result.mode == "recommended" else "补充阅读"
    parts = [RELATED_READING_START, f"## {heading}", ""]
    for index, reference in enumerate(result.references, 1):
        title = reference.candidate.title or reference.candidate.raw_text
        parts.extend([f"### {index}. {title}", ""])
        if reference.candidate.year is not None:
            parts.extend([f"年份：{reference.candidate.year}", ""])
        if reference.reason:
            parts.extend([f"推荐理由：{reference.reason}", ""])
        links = [f"[论文链接]({reference.paper_url})"]
        if reference.code_url:
            links.append(f"[代码链接]({reference.code_url})")
        parts.extend([" · ".join(links), ""])
    parts.append(RELATED_READING_END)
    return "\n".join(parts).rstrip()


def replace_related_reading(markdown: str, block: str | None) -> str:
    base = strip_generated_related_reading(markdown).rstrip()
    if not block:
        return base + "\n"
    return f"{base}\n\n{block.strip()}\n"


def render_article_markdown(
    article: PaperArticle,
    resolved_references: "ResolutionResult | None" = None,
) -> str:
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
        f"year: {publication_year(article)}",
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
    markdown = "\n".join(parts).rstrip() + "\n"
    block = render_related_reading(resolved_references) if resolved_references else None
    return replace_related_reading(markdown, block)

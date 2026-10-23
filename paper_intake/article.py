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
from .evidence import FactPack, ensure_clean_text

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
_TRACEABLE_NUMBER = re.compile(r"(?<![\w@.])(?:\d+(?:\.\d+)?%|\d+(?:\.\d+)?)(?![\w.])")


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

    id: str = ""
    path: str = ""
    sha256: str = ""
    section: Literal["introduction", "method", "experiments", "conclusion"] = "method"
    explanation: str = ""
    figure_label: str = ""
    original_caption: str = ""
    anchor_id: str = ""
    short_title: str = ""
    alt: str = ""
    interpretation: "FigureInterpretation | None" = None


class FigureInterpretation(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    shows: str
    focus: str
    evidence: str
    conclusion: str


class ArticleParagraph(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    id: str
    text: str
    evidence_ids: list[str] = Field(default_factory=list)


class ArticleSectionPlan(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    id: Literal["introduction", "method", "experiments", "conclusion"]
    question: str
    paragraphs: list[ArticleParagraph] = Field(default_factory=list)
    takeaways: list[str] = Field(default_factory=list)


class PaperArticle(BaseModel):
    schema_version: int = 1
    paper: PaperInfo
    classification: Classification
    article: ArticleSections
    figures: list[ArticleFigure] = Field(default_factory=list)
    facts: FactPack | None = None
    sections: list[ArticleSectionPlan] = Field(default_factory=list)


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

    paragraph_ids: set[str] = set()
    known_evidence_ids: set[str] = set()
    known_numbers: set[str] = set()
    if article.schema_version >= 2:
        if article.facts is None:
            issues.append(QualityIssue("facts_required", "Schema V2 requires a deterministic fact pack."))
        else:
            known_evidence_ids.update(item.id for item in article.facts.evidence_blocks)
            known_evidence_ids.update(item.id for item in article.facts.key_numbers)
            known_numbers.update(item.value for item in article.facts.key_numbers)
        if not article.sections:
            issues.append(QualityIssue("content_plan_required", "Schema V2 requires content sections."))
        for section in article.sections:
            for paragraph in section.paragraphs:
                paragraph_ids.add(paragraph.id)
                if not paragraph.evidence_ids:
                    issues.append(QualityIssue("evidence_id_required", f"{paragraph.id} has no evidence."))
                for evidence_id in paragraph.evidence_ids:
                    if evidence_id not in known_evidence_ids:
                        issues.append(QualityIssue("evidence_id_unknown", f"Unknown evidence id: {evidence_id}"))
                for number in _TRACEABLE_NUMBER.findall(paragraph.text):
                    if number not in known_numbers:
                        issues.append(QualityIssue("number_untraceable", f"Untraceable number: {number}"))

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
        if article.schema_version >= 2:
            if figure.anchor_id not in paragraph_ids:
                issues.append(QualityIssue("figure_anchor_unresolved", f"Figure {index} anchor is missing."))
            if len(figure.alt) < 40 or not _CJK.search(figure.alt):
                issues.append(QualityIssue("figure_alt_invalid", f"Figure {index} alt text is too short."))
            interpretation = figure.interpretation
            if interpretation is None or any(
                not getattr(interpretation, field).strip()
                for field in ("shows", "focus", "evidence", "conclusion")
            ):
                issues.append(QualityIssue("figure_interpretation_invalid", f"Figure {index} needs four-part interpretation."))
        else:
            explanation = figure.explanation.strip()
            if len(explanation) < 24 or not _CJK.search(explanation):
                issues.append(
                    QualityIssue(
                        "figure_explanation_invalid",
                        f"Figure {index} needs a substantive Chinese explanation.",
                    )
                )
    if article.schema_version >= 2 and sum(
        figure.section == "experiments" for figure in article.figures
    ) > 3:
        issues.append(QualityIssue("experiment_figure_limit", "Experiment section allows at most three figures."))
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


def _render_v2_figure(article: PaperArticle, figure: ArticleFigure) -> list[str]:
    basename = Path(figure.path).name
    public_path = f"/images/papers/{article.paper.canonical_id or 'paper'}/{basename}"
    label_number = re.search(r"\d+[a-z]?", figure.figure_label, re.IGNORECASE)
    display_label = f"图 {label_number.group(0)}" if label_number else "图"
    title = figure.short_title or "论文图示"
    interpretation = figure.interpretation
    lines = [f"![{display_label}：{title}]({public_path} \"{figure.alt}\")", ""]
    if interpretation is not None:
        lines.extend(
            [
                interpretation.shows,
                "",
                interpretation.focus,
                "",
                interpretation.evidence,
                "",
                interpretation.conclusion,
                "",
            ]
        )
    return lines


def _render_v2_section(article: PaperArticle, section: ArticleSectionPlan) -> str:
    lines: list[str] = []
    if section.question:
        lines.extend([f"*{section.question}*", ""])
    figures_by_anchor: dict[str, list[ArticleFigure]] = {}
    for figure in article.figures:
        figures_by_anchor.setdefault(figure.anchor_id, []).append(figure)
    for paragraph in section.paragraphs:
        lines.extend([paragraph.text, ""])
        for figure in figures_by_anchor.get(paragraph.id, []):
            lines.extend(_render_v2_figure(article, figure))
    if section.takeaways:
        lines.extend(["**要点**", ""])
        lines.extend(f"- {item}" for item in section.takeaways)
        lines.append("")
    return "\n".join(lines).rstrip()


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

    plans = {section.id: section for section in article.sections}

    def section_body(section_id: str, legacy: str) -> str:
        plan = plans.get(section_id)
        if article.schema_version >= 2 and plan is not None:
            return _render_v2_section(article, plan)
        return legacy.strip()

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
        "## 研究背景与问题",
        "",
        section_body("introduction", article.article.introduction),
    ]
    intro_figures = "" if article.schema_version >= 2 else _render_figures(article, "introduction", "背景图")
    if intro_figures:
        parts.extend(["", intro_figures])
    parts.extend(["", "## 方法", "", section_body("method", article.article.method)])
    method_figures = "" if article.schema_version >= 2 else _render_figures(article, "method", "方法图")
    if method_figures:
        parts.extend(["", method_figures])
    parts.extend(["", "## 实验", "", section_body("experiments", article.article.experiments)])
    experiment_figures = "" if article.schema_version >= 2 else _render_figures(article, "experiments", "实验图")
    if experiment_figures:
        parts.extend(["", experiment_figures])
    parts.extend(["", "## 总结", "", section_body("conclusion", article.article.conclusion)])
    conclusion_figures = "" if article.schema_version >= 2 else _render_figures(article, "conclusion", "总结图")
    if conclusion_figures:
        parts.extend(["", conclusion_figures])
    parts.extend(["", "## References", ""])
    resolved_by_index: dict[int, "ResolvedReference"] = {}
    if resolved_references:
        for resolved in resolved_references.references:
            resolved_by_index[resolved.candidate.original_index] = resolved
    if article.schema_version >= 2:
        focal = f"[{article.paper.title}]({article.paper.paper_url})"
        if article.paper.code_url:
            focal += f" （代码：[{article.paper.code_url}]({article.paper.code_url})）"
        parts.append(f"- {focal}")
    references_to_render = [] if article.schema_version >= 2 else article.article.references
    for index, reference in enumerate(references_to_render):
        resolved = resolved_by_index.get(index)
        if resolved is not None:
            title = resolved.candidate.title.strip()
            if title:
                title_pattern = re.compile(
                    r"\s+".join(re.escape(part) for part in title.split()),
                    re.IGNORECASE,
                )
                reference = title_pattern.sub(
                    lambda match: f"[{match.group(0)}]({resolved.paper_url})",
                    reference,
                    count=1,
                )
            if resolved.code_url:
                reference += f" （代码：[{resolved.code_url}]({resolved.code_url})）"
            if resolved.reason:
                reference += f" （相关性：{resolved.reason.strip()}）"
        parts.append(f"- {reference}")
    if article.schema_version >= 2 and resolved_references:
        for resolved in resolved_references.references:
            title = resolved.candidate.title.strip() or resolved.candidate.raw_text.strip()
            reference = f"[{title}]({resolved.paper_url})"
            if resolved.code_url:
                reference += f" （代码：[{resolved.code_url}]({resolved.code_url})）"
            if resolved.reason:
                reference += f" （相关性：{resolved.reason.strip()}）"
            parts.append(f"- {reference}")
    rendered = "\n".join(parts).rstrip() + "\n"
    ensure_clean_text(rendered, stage="final_markdown")
    return rendered

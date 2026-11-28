"""FactPack: one model call yielding structured facts AND publish-ready drafts.

Pydantic V2 model.  Parsing failures are never swallowed: the raw response is
written to ``data/diagnostics/{canonical_id}_fact_pack_error.json`` and a
ValueError is raised with the diagnostic path.

Since fact-pack/v2 the ``xhs_draft`` block carries a complete Xiaohongshu
manuscript (title candidates, sectioned body, topics, figure intents) that the
deterministic compiler turns into a redbook note YAML.  No agent / vision model
is involved: figures are chosen by paper order from ``figure_manifest.json``.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, TypeAdapter, ValidationError

ROOT = Path(__file__).resolve().parents[1]


class FactField(BaseModel):
    """One fact with its own traceable source and verification state."""

    value: Any = None
    source: str = ""
    verification_status: str = "unverified"  # verified / unverified / missing
    evidence: str = ""


class FactProvenance(BaseModel):
    """Per-field provenance for the facts that decide publication eligibility.

    Kept as a side-channel next to FactFacts so downstream compilers that read
    plain strings (venue_name, authors, ...) keep working unchanged. The strict
    gate reads THIS object, not the unverified model-extracted values.
    """

    fields: dict[str, FactField] = Field(default_factory=dict)

    def unverified_core(self, core: tuple[str, ...]) -> list[str]:
        """Names of core fields that are absent or not verified."""
        return [name for name in core
                if name not in self.fields
                or self.fields[name].verification_status != "verified"]


def _clean_bib_value(value: str) -> str:
    """Strip BibTeX braces used to protect capitalization ({E}cho{MLLM})."""
    return value.replace("{", "").replace("}", "").strip()


def _parse_acl_bib(bib: str) -> dict[str, Any]:
    """Parse the small BibTeX subset emitted by aclanthology.org/*.bib."""
    if not bib or "@" not in bib:
        return {}
    fields: dict[str, str] = {}
    current: str | None = None
    for line in bib.splitlines():
        stripped = line.strip()
        if "@" in stripped and "{" in stripped:
            current = None
            continue
        match = re.match(r'([A-Za-z_]+)\s*=\s*["{](.*)$', stripped)
        if match:
            key, value = match.group(1).lower(), match.group(2)
            fields[key] = value.rstrip('"},')
            current = key
        elif current and stripped and not stripped.startswith("}"):
            fields[current] += " " + stripped.rstrip(",").rstrip('"}')
    authors = [part.strip() for part in fields.get("author", "").split(" and ") if part.strip()]
    # ACL bib uses "Last, First"; normalize to "First Last".
    normalized = []
    for author in authors:
        if "," in author:
            last, first = [part.strip() for part in author.split(",", 1)]
            normalized.append(f"{first} {last}".strip())
        else:
            normalized.append(author)
    return {
        "paper_title": _clean_bib_value(fields.get("title", "")),
        "authors": normalized,
        "venue_name": _clean_bib_value(fields.get("booktitle", "")),
        "year": _clean_bib_value(fields.get("year", "")),
        "identity": fields.get("doi", "") or fields.get("url", ""),
        "paper_url": fields.get("url", ""),
    }


def _parse_pdf_header(markdown_text: str) -> dict[str, Any]:
    """Extract author names and institution+city pairs from the paper header."""
    if not markdown_text:
        return {}
    header = markdown_text[:1500]
    # Institution lines: "<sup>1</sup>Name, City, Country"
    institutions: list[dict[str, str]] = []
    for match in re.finditer(
        r"<sup>\d+</sup>\s*([^,<>\n]+?),\s*([A-Z][A-Za-z\s]+?),\s*[A-Z][A-Za-z\s]*",
        header,
    ):
        institutions.append({"institution": match.group(1).strip(), "city": match.group(2).strip()})
    # Author line: names before the first <sup>n</sup> institution line.
    author_names: list[str] = []
    for line in header.splitlines():
        if "<sup>" in line and not re.search(r"University|Hospital|Institute|College", line):
            for name in re.split(r"[∗†,]", line):
                name = re.sub(r"<sup>\d+</sup>", "", name).strip()
                if name and " " in name and len(name) < 60:
                    author_names.append(name)
            break
    return {"author_names": author_names, "institutions": institutions}


def location_from_pdf_header(pdf_markdown: str) -> dict[str, Any]:
    """Derive the map-facing location block from the PDF author affiliation header.

    The site map needs a city per paper; ``tools/build_places.py`` drops any
    record without one. The only deterministic source for that city is the
    affiliation line printed in the paper header, never model prose.
    """
    header = _parse_pdf_header(pdf_markdown)
    institutions = header.get("institutions") or []
    cities = [str(item["city"]).strip() for item in institutions if item.get("city")]
    names = [str(item["institution"]).strip() for item in institutions if item.get("institution")]
    if not cities:
        return {}
    unique_cities = list(dict.fromkeys(cities))
    return {
        "affil_city": unique_cities,
        "corresponding_city": unique_cities[0],
        "affiliation_name": "；".join(dict.fromkeys(names))[:200],
    }


def stamp_location_verification(
    pack: dict[str, Any], *, pdf_markdown: str = ""
) -> dict[str, Any]:
    """Stamp ``location.verification_status`` from deterministic sources only.

    A model may derive a city from the institution name (a university name implies
    its city), and the user asked for exactly that so the site map has a city per
    paper. Provenance stays honest by grading it:

    - ``verified``         the city also appears in the paper's affiliation header;
    - ``inferred``         the model derived it (universities -> city), publishable
                           but labelled as inference on the site;
    - ``unverified``       no city at all, so the publisher drops the field.

    A country is never allowed to stand in for a city: ``venues_city``-style
    shortcuts would put every Chinese paper on the same pin.
    """
    if not isinstance(pack, dict):
        return pack
    location = pack.get("location")
    derived = location_from_pdf_header(pdf_markdown)
    if not derived and not isinstance(location, dict):
        return pack
    stamped = dict(location) if isinstance(location, dict) else {}
    for name, value in derived.items():
        if not stamped.get(name):
            stamped[name] = value
    if derived:
        header_cities = {city.casefold() for city in derived["affil_city"]}
        proposed = [str(city) for city in (stamped.get("affil_city") or [])]
        proposed.append(str(stamped.get("corresponding_city") or ""))
        if any(city.casefold() in header_cities for city in proposed if city):
            stamped["source"] = "pdf_original"
            stamped["verification_status"] = "verified"
    if not stamped:
        return pack
    cities = [str(city).strip() for city in (stamped.get("affil_city") or [])]
    cities.append(str(stamped.get("corresponding_city") or "").strip())
    cities.append(str(stamped.get("venue_city") or "").strip())
    has_city = any(cities)
    stamped.setdefault("source", "")
    if stamped.get("verification_status") != "verified":
        if has_city:
            # Derived from the institution name, not quoted by the paper.
            stamped["verification_status"] = "inferred"
            stamped["source"] = stamped.get("source") or "model_inference"
        else:
            stamped["verification_status"] = "unverified"
    output = dict(pack)
    output["location"] = stamped
    return output


def build_fact_provenance(
    *,
    acl_bib: str = "",
    pdf_markdown: str = "",
    catalog_row: dict[str, Any] | None = None,
    canonical_id: str = "",
    location: dict[str, Any] | None = None,
) -> FactProvenance:
    """Build per-field provenance from authoritative sources only.

    Priority: ACL BibTeX (publisher-authoritative) > PDF original text >
    catalog metadata (harvested, weaker). Model-extracted prose is never a
    verification source.
    """
    catalog_row = catalog_row or {}
    bib = _parse_acl_bib(acl_bib)
    pdf = _parse_pdf_header(pdf_markdown)
    fields: dict[str, FactField] = {}

    def put(name: str, value: Any, source: str, evidence: str = "") -> None:
        if value in (None, "", [], {}):
            return
        fields[name] = FactField(value=value, source=source,
                                 verification_status="verified", evidence=evidence)

    for name in ("paper_title", "authors", "venue_name", "year", "identity", "paper_url"):
        put(name, bib.get(name), "aclanthology.bib", "ACL Anthology BibTeX")

    if pdf.get("institutions"):
        inst = pdf["institutions"]
        existing = list(fields.get("authors").value or []) if "authors" in fields else []
        # PDF origin is authoritative for affiliation; authors already from bib stay.
        put("affiliations", inst, "pdf_original", "paper author affiliation header")
        if not existing and pdf.get("author_names"):
            put("authors", pdf["author_names"], "pdf_original", "paper author header")

    # Location provenance: the map needs a city, and only the affiliation header
    # can back it. A location block is verified only when its city is one of the
    # header cities, so a model guess can never become "verified" by accident.
    derived_location = location if isinstance(location, dict) and location else location_from_pdf_header(pdf_markdown)
    if derived_location:
        header_cities = {city.casefold() for city in location_from_pdf_header(pdf_markdown).get("affil_city", [])}
        proposed = [str(city) for city in (derived_location.get("affil_city") or [])]
        proposed.append(str(derived_location.get("corresponding_city") or ""))
        if any(city.casefold() in header_cities for city in proposed if city):
            put("location", derived_location, "pdf_original", "paper author affiliation header")

    if canonical_id and (
        re.fullmatch(r"(?:\d{4}\.\d{4,5}|[a-z][a-z.-]+/\d{7})(?:v\d+)?", canonical_id, re.I)
        or re.fullmatch(r"10\.\d{4,9}/\S+", canonical_id, re.I)
        or re.fullmatch(r"\d{4}\.[a-z0-9][a-z0-9.-]*\.\d+", canonical_id, re.I)
    ):
        put("identity", canonical_id, "canonical_id", "job identity")

    catalog_map = {
        "paper_title": catalog_row.get("title"),
        "authors": catalog_row.get("authors_json"),
        "venue_name": catalog_row.get("venue_name"),
        "year": catalog_row.get("publication_year"),
        "identity": catalog_row.get("doi") or catalog_row.get("arxiv_id"),
    }
    for name, value in catalog_map.items():
        if name not in fields and value:
            put(name, value, "catalog", "catalog row")

    # Ensure every core field has an explicit (possibly unverified) entry.
    for name in ("paper_title", "authors", "venue_name", "year", "identity", "location"):
        fields.setdefault(name, FactField(value=None, source="",
                                          verification_status="unverified"))
    return FactProvenance(fields=fields)


class FactFacts(BaseModel):
    one_line: str = ""
    problem: str = ""
    method: str = ""
    experiments: list[str] = Field(default_factory=list)
    limitations: str = ""
    novelty: str = ""
    audience: str = ""
    keywords: list[str] = Field(default_factory=list)
    takeaway: str = ""
    paper_title: str = ""
    code_url: str = ""  # 代码仓库链接，如果有的话
    paper_link: str = ""  # 论文完整链接（arXiv 或 DOI）
    pdf_link: str = ""    # PDF 直接链接
    venue_name: str = ""  # 会议/期刊名称
    venue_type: str = ""
    year: str = ""        # 发表年份
    published_date: str = ""
    authors: list[dict] = Field(default_factory=list)  # [{"name": "", "affiliations": [{"institution": "", "city": "", "country": "", "latitude": null, "longitude": null}]}]
    source: str = ""      # 来源（arxiv, acm, ieee 等）
    verification_status: str = ""  # "verified" / "unverified" / "missing"


class XhsDraft(BaseModel):
    """Publish-ready Xiaohongshu manuscript, generated in one model call."""

    title_literary: str = ""
    title_question: str = ""
    opening: str = ""          # 🌐 one-line summary + "——XX论文导读"
    pain_point: str = ""       # "核心痛点：..." appended after opening, no newline
    seed: int = 0              # even -> 3-4 bullet points; odd -> one paragraph
    sections: dict[str, str] = Field(default_factory=dict)
    topics: list[str] = Field(default_factory=list)
    figure_intents: list[dict[str, Any]] = Field(default_factory=list)


class WechatDraft(BaseModel):
    lead: str = ""
    body: str = ""


class HomepageDraft(BaseModel):
    summary_1line: str = ""
    summary_para: str = ""


class FactPlatformHints(BaseModel):
    xhs: dict[str, Any] = Field(
        default_factory=lambda: {"hook": "", "topic_candidates": []})
    wechat: dict[str, Any] = Field(default_factory=lambda: {"lead": ""})
    homepage: dict[str, Any] = Field(
        default_factory=lambda: {"summary_1line": ""})


class PaperLocation(BaseModel):
    """Separate venue and affiliation locations used by the site map."""

    location_type: str = ""
    venue_city: str = ""
    affil_city: list[str] = Field(default_factory=list)
    corresponding_city: str = ""
    affiliation_name: str = ""
    source: str = ""
    verification_status: str = "unverified"


class FactReference(BaseModel):
    title: str = ""
    paper_url: str = ""
    code_url: str = ""
    source: str = ""
    verification_status: str = "unverified"
    evidence: str = ""


_ARXIV_IN_TEXT = re.compile(r"arXiv:\s*(\d{4}\.\d{4,5}(?:v\d+)?)", re.I)
_CODE_IN_TEXT = re.compile(r"https?://github\.com/[^\s.,;)]+", re.I)


def extract_references(markdown_text: str) -> list[FactReference]:
    """Extract the paper's own bibliography from a MinerU Markdown original.

    Only the ``## References`` section is read. Each blank-line-separated
    entry is parsed for a title and, when present, an explicit arXiv id or
    code URL. A real arXiv id is deterministically expanded to
    ``https://arxiv.org/abs/<id>`` and marked ``verified`` (the id is printed
    in the original text). Entries with no explicit identifier stay
    ``unverified`` with an empty URL -- nothing is guessed. Hyphenated
    line-breaks (``ven-\\ntricular``) are joined back into one word.
    """
    if not markdown_text:
        return []
    match = re.search(r"(?im)^\s*#{0,3}\s*references\s*$", markdown_text)
    if not match:
        return []
    section = markdown_text[match.end():]
    # Stop at a following *named* section. ACL appendices use single-letter
    # labels ("## A Detailed Data..."), which still belong to the paper's
    # back matter and are excluded from the truncation rule.
    for line_match in re.finditer(r"(?m)^(#{1,2})\s+(.+)$", section):
        heading = line_match.group(2).strip()
        if re.match(r"^[A-Z](?:\.\d+)?\s", heading):
            continue  # appendix label A/B/C...
        section = section[: line_match.start()]
        break

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", section) if p.strip()]
    # Rejoin entries split across a blank line by a hyphenated line break,
    # e.g. "...left ven-\n\ntricular hypertrophy...".
    merged: list[str] = []
    for para in paragraphs:
        if merged and merged[-1].rstrip().endswith("-") and re.match(r"^[a-z]", para):
            merged[-1] = merged[-1].rstrip()[:-1] + para
        else:
            merged.append(para)

    refs: list[FactReference] = []
    for raw in merged:
        entry = raw.strip()
        if not entry or len(entry) < 20:
            continue
        # Join hyphenated line breaks inside a paragraph: "ven-\ntricular".
        flat = re.sub(r"-\s*\n\s*", "", entry)
        flat = re.sub(r"\s*\n\s*", " ", flat).strip()
        arxiv = _ARXIV_IN_TEXT.search(flat)
        code = _CODE_IN_TEXT.search(flat)
        # Title heuristic: text after the "YEAR." marker, before venue/arXiv.
        # ACL style: "Authors. 2024. Title. Venue, ..."
        year_mark = re.search(r"\b(?:19|20)\d{2}[a-z]?\.\s+", flat)
        if year_mark:
            tail = flat[year_mark.end():]
        else:
            tail = flat
        title = re.split(r"\.\s+(?:arXiv|In |Advances|Proceedings|Journal|IEEE|ACM|Biomedical|JAMA|Science|[A-Z][a-z]+,\s*\d)", tail)[0]
        title = title.strip().rstrip(".").strip()
        if not title or len(title) < 8:
            continue
        if arxiv:
            paper_url = f"https://arxiv.org/abs/{arxiv.group(1)}"
            status = "verified"
            evidence = f"arXiv:{arxiv.group(1)} (printed in原文References)"
            source = "pdf_original"
        elif code:
            paper_url = ""
            status = "unverified"
            evidence = code.group(0)
            source = "pdf_original"
        else:
            paper_url = ""
            status = "unverified"
            evidence = "title printed in original References (no explicit link)"
            source = "pdf_original"
        refs.append(FactReference(
            title=title,
            paper_url=paper_url,
            code_url=code.group(0) if code else "",
            source=source,
            verification_status=status,
            evidence=evidence,
        ))
    return refs


class FactFigure(BaseModel):
    figure_id: str = ""
    path: str = ""
    caption: str = ""
    source_type: str = ""
    width: int | None = None
    height: int | None = None
    sha256: str = ""
    visual_review_status: str = "pending"
    visual_review: str = ""


class FactFormula(BaseModel):
    latex: str = ""
    display_mode: str = ""
    source_location: str = ""
    verification_status: str = "unverified"


def _mask_fenced_code(markdown: str) -> str:
    """Hide fenced code without shifting offsets; an unclosed fence hides the remainder."""
    output = []
    fence_char = ""
    fence_length = 0
    for line in markdown.splitlines(keepends=True):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})([^\r\n]*)", line)
        if not fence_char and marker:
            fence_char, fence_length = marker.group(1)[0], len(marker.group(1))
        elif fence_char and marker and marker.group(1)[0] == fence_char and len(marker.group(1)) >= fence_length and not marker.group(2).strip():
            output.append(re.sub(r"[^\r\n]", " ", line))
            fence_char, fence_length = "", 0
            continue
        output.append(re.sub(r"[^\r\n]", " ", line) if fence_char else line)
    return "".join(output)


def locate_formula(markdown: str, formula: FactFormula) -> tuple[int, int] | None:
    """Locate exact LaTeX by unique ``heading::ordinal`` within the source Markdown.

    Ordinals are one-based, scoped to the requested display mode and section;
    returned half-open character offsets refer to the formula body, without delimiters.
    Ambiguous headings, malformed syntax and any mismatch fail closed.
    """
    location = re.fullmatch(r"(.+?)::([1-9][0-9]{0,8})", formula.source_location)
    if not location or formula.display_mode not in {"block", "inline"} or not formula.latex.strip():
        return None
    heading_name, ordinal_text = location.groups()
    searchable = _mask_fenced_code(markdown)
    headings = list(re.finditer(r"(?m)^ {0,3}(#{1,6})[ \t]+([^\r\n]+?)[ \t]*\r?$", searchable))
    matched = [item for item in headings if item.group(2).strip() == heading_name]
    if len(matched) != 1:
        return None
    section = matched[0]
    end = len(markdown)
    for candidate in headings:
        if candidate.start() > section.start() and len(candidate.group(1)) <= len(section.group(1)):
            end = candidate.start()
            break
    start = section.end()
    text = searchable[start:end]
    block_pattern = r"(?m)^[ \t]*\$\$[ \t]*\r?\n(?P<body>[\s\S]*?)\r?\n[ \t]*\$\$[ \t]*(?=\r?$)"
    blocks = list(re.finditer(block_pattern, text))
    if formula.display_mode == "block":
        matches = blocks
    else:
        inline_pattern = r"(?<![\\$])\$(?!\$)(?P<body>[^\n$]+?)(?<!\\)\$(?!\$)"
        matches = [match for match in re.finditer(inline_pattern, text)
                   if not any(block.start() <= match.start() < block.end() for block in blocks)]
    ordinal = int(ordinal_text)
    if ordinal > len(matches):
        return None
    selected = matches[ordinal - 1]
    if selected.group("body").strip() != formula.latex.strip():
        return None
    return start + selected.start("body"), start + selected.end("body")


class FactPack(BaseModel):
    schema_version: str = "fact-pack/v2"
    canonical_id: str
    source_hash: str
    model_id: str
    prompt_version: str
    facts: FactFacts
    platform_hints: FactPlatformHints
    # v2 publish-ready blocks (optional for backward compatibility with v1).
    xhs_draft: XhsDraft | None = None
    wechat_draft: WechatDraft | None = None
    homepage_draft: HomepageDraft | None = None
    # Optional for legacy packs; source and verification remain separate.
    location: PaperLocation | None = None
    references: list[FactReference] = Field(default_factory=list)
    figures: list[FactFigure] = Field(default_factory=list)
    formulae: list[FactFormula] = Field(default_factory=list)


# IMPORTANT: bump when the prompt/schema changes, otherwise cached v1 packs
# keep being reused and never pick up the new manuscript fields.
FACT_PACK_PROMPT_VERSION = "fact-pack-2.5"  # location: 3-way type + city derivation

# Deterministic section headings; the compiler uses these verbatim.  The model
# is told to write CONTENT only; it never invents headings, so the body always
# passes the gate's "dedicated section line" check.
XHS_SECTION_KEYS = (
    "contribution", "method", "experiment", "result", "takeaway", "limitation",
)


def build_fact_pack_prompt(markdown_path: Path) -> str:
    """Build a strict JSON-only prompt from the parsed Markdown file.

    v2 asks DeepSeek for both core facts and complete per-platform manuscripts,
    encoding the human template rules directly into the prompt so the resulting
    JSON can be compiled into a redbook note YAML without any agent editing.
    """
    text = Path(markdown_path).read_text(encoding="utf-8", errors="replace")
    # Keep the tail (experiments / limitations) as well as the head: the old
    # 24k head-only cut dropped exactly the sections the body needs.
    trimmed = text[:30000] if len(text) <= 36000 else (
        text[:30000] + "\n...[middle omitted]...\n" + text[-6000:]
    )
    return (
        "You write a Chinese academic paper post. Read the Markdown and output "
        "ONLY one JSON object (no markdown fences, no prose) with this exact schema:\n"
        "{\n"
        '  "schema_version": "fact-pack/v2",\n'
        '  "facts": {\n'
        '    "one_line": "one Chinese sentence, <=30 chars",\n'
        '    "problem": "the problem in one sentence",\n'
        '    "method": "core method in one sentence",\n'
        '    "experiments": ["dataset/metric/result", "..."],\n'
        '    "limitations": "stated limitations in one sentence",\n'
        '    "novelty": "novel contribution in one sentence",\n'
        '    "audience": "who should read this",\n'
        '    "keywords": ["kw1", "kw2"],\n'
        '    "takeaway": "practical lesson for a recommender-systems engineer",\n'
        '    "paper_title": "original paper title",\n'
        '    "code_url": "GitHub repo URL if available, empty string otherwise",\n'
        '    "paper_link": "full paper URL (arXiv/DOI), empty if not known",\n'
        '    "pdf_link": "direct PDF link, empty if not known",\n'
        '    "venue_name": "conference/journal name, empty if not known",\n'
        '    "venue_type": "conference/journal/preprint, empty if unknown",\n'
        '    "year": "publication year",\n'
        '    "published_date": "publication date if present, otherwise empty",\n'
        '    "authors": [{"name": "author name", "affiliations": [{"institution": "", "city": "", "country": "", "latitude": null, "longitude": null}]}],\n'
        '    "source": "source (arxiv, acm, ieee, ...)",\n'
        '    "verification_status": "verified/unverified/missing"\n'
        "  },\n"
        '  "platform_hints": {\n'
        '    "xhs": {"hook": "short hook", "topic_candidates": ["论文分享"]},\n'
        '    "wechat": {"lead": "one-sentence lead"},\n'
        '    "homepage": {"summary_1line": "one-line summary"}\n'
        "  },\n"
        '  "xhs_draft": {\n'
        '    "title_literary": "<=20 Chinese chars, literary style: '
        'CONFERENCE YEAR | Method: poetic phrase, e.g. WWW 2026 | RecCLIP：协同过滤的视觉显影",\n'
        '    "title_question": "<=20 Chinese chars, question style",\n'
        '    "opening": "one line: what is new about this paper + dash + '
        'XX论文导读, e.g. 跨域推荐新范式：协同过滤视觉语言模型——RecCLIP论文导读 '
        '(the compiler prepends the 🌐 mark)",\n'
        '    "pain_point": "核心痛点：one sentence on the problem this paper solves",\n'
        '    "seed": "an integer you choose deterministically from the paper '
        '(e.g. last digit of arxiv id); even means write bullet points, '
        'odd means write one paragraph",\n'
        '    "sections": {\n'
        '      "contribution": "novelty summary; if seed is even write 3-4 '
        'numbered items using ①②③ with a newline after EACH item; if seed is '
        'odd write ONE flowing paragraph without line breaks",\n'
        '      "method": "if seed is even write 3-4 numbered items using ① ② ③ '
        'with a newline after EACH item; if seed is odd write ONE flowing paragraph",\n'
        '      "experiment": "3 lines: 数据集：...\\n算力：...\\n指标���...",\n'
        '      "result": "ONE paragraph on the most striking result with exact numbers"\n'
        '    },\n'
        '    "topics": ["论文分享", "人工智能", "推荐系统", "深度学习", "AI"],\n'
        '    "figure_intents": [\n'
        '      {"order": 1, "intent": "overview", "description": "what figure 1 shows"},\n'
        '      {"order": 2, "intent": "architecture", "description": "what figure 2 shows"}\n'
        '    ]\n'
        '  },\n'
        '  "wechat_draft": {\n'
        '    "lead": "one-sentence lead for WeChat",\n'
        '    "body": "full-length Chinese article (600-1200 chars) with clear sections"\n'
        '  },\n'
        '  "homepage_draft": {\n'
        '    "summary_1line": "one-line summary",\n'
        '    "summary_para": "one short paragraph for the homepage"\n'
        '  },\n'
        '  "location": {\n'
        '    "location_type": "Affiliation | Venue | Publisher (exactly one of the three)",\n'
        '    "venue_city": "city where the venue was held; only when location_type=Venue",\n'
        '    "affil_city": ["city of the author affiliation(s); derive from affiliation_name"],\n'
        '    "corresponding_city": "city of the corresponding author\'s affiliation",\n'
        '    "affiliation_name": "full name of the first author\'s institution",\n'
        '    "source": "pdf_original | model_inference",\n'
        '    "verification_status": "verified | inferred | unverified"\n'
        "  },\n"
        '  "references": [{"title": "", "paper_url": "", "code_url": "", '
        '"source": "", "verification_status": "unverified"}],\n'
        '  "formulae": [{"latex": "", "display_mode": "inline or block", '
        '"source_location": "exact Markdown section heading::one-based ordinal", '
        '"verification_status": "unverified"}],\n'
        '  "figures": []\n'
        "}\n"
        "HARD RULES:\n"
        "- answer in Chinese; every claim MUST be grounded in the paper, never invent numbers;\n"
        "- xhs_draft.topics MUST be from: 论文分享/人工智能/推荐系统/深度学习/AI/机器学习/数据挖掘/自然语言处理/计算机视觉/强化学习;\n"
        "- xhs_draft.sections values are CONTENT ONLY (no headings, no '#' or Markdown marks);\n"
        "- sections has EXACTLY 4 keys: contribution/method/experiment/result; "
        "DO NOT write takeaway or limitation sections (they are omitted on purpose);\n"
        "- if seed is even: contribution and method each get 3-4 numbered items "
        "with a newline after each item; if seed is odd: single unbroken paragraph;\n"
        "- experiment section uses literal newlines between 数据集/算力/指标 lines;\n"
        "- pain_point starts with the literal text '核心痛点：' and contains no newline;\n"
        "- figure_intents describes figures in paper order;\n"
        "- code_url MUST be a valid GitHub URL (https://github.com/...) if the paper mentions code, otherwise empty string.\n"
        "- paper_link, pdf_link, venue_name, year, authors, source must be extracted ONLY from reliable sources (catalog, paper itself); do not guess.\n"
        "- location: read the author affiliation block on the first page to get "
        "affiliation_name; then derive affil_city from that institution (a university "
        "name implies its city). location_type MUST be exactly one of "
        "Affiliation (author institution), Venue (conference/journal), Publisher "
        "(ACM/IEEE/arXiv direct release). corresponding_city is the city of the "
        "corresponding author (marked with a mail icon or asterisk); if that cannot "
        "be determined, leave it empty rather than guessing. NEVER write a country "
        "into a city field. Set location.source to model_inference and "
        "location.verification_status to inferred unless the paper states the city verbatim.\n"
        "- Model-extracted metadata, locations and references remain unverified until "
        "independently checked; use empty lists or null for unavailable data. "
        "Never guess URLs, cities or coordinates.\n"
        "- figures must be an empty list: local paths, hashes, dimensions and visual reviews "
        "come from the asset pipeline, not the language model.\n"
        "- Preserve original LaTeX in formulae. source_location must be the exact Markdown "
        "heading without #, then :: and the 1-based ordinal among formulas of the same "
        "display mode in that section; leave it empty if uncertain. Never claim verification."
        "\n\n"
        "--- PAPER MARKDOWN ---\n" + trimmed + "\n--- END ---"
    )


def parse_fact_pack_response(raw_response: str, canonical_id: str) -> dict[str, Any]:
    """Parse the model response into a dict; on failure persist and re-raise.

    ``ModelCallGateway.ensure`` calls this with the raw string; the returned
    dict is what gets written to the artifact JSON.  The full metadata fields
    (source_hash/model_id/prompt_version) are injected by the gateway caller.
    """
    try:
        payload = json.loads(raw_response)
        if not isinstance(payload, dict):
            raise ValueError("top-level JSON is not an object")
    except (json.JSONDecodeError, ValueError) as error:
        diagnostics = ROOT / "data" / "diagnostics"
        diagnostics.mkdir(parents=True, exist_ok=True)
        safe = canonical_id.replace(":", "__")
        target = diagnostics / f"{safe}_fact_pack_error.json"
        target.write_text(
            json.dumps(
                {
                    "canonical_id": canonical_id,
                    "error": str(error),
                    "raw_response": raw_response,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        raise ValueError(
            f"fact_pack parse failed for {canonical_id}; raw response saved to {target}"
        ) from error

    facts = payload.get("facts")
    hints = payload.get("platform_hints")
    if not isinstance(facts, dict) or not isinstance(hints, dict):
        raise ValueError(
            f"fact_pack for {canonical_id} missing facts/platform_hints object"
        )
    # Legacy packs can omit these fields; if present, validate their shape
    # without rewriting unknown existing fields or claiming verification.
    for name, schema in (
        ("location", PaperLocation | None),
        ("references", list[FactReference]),
        ("figures", list[FactFigure]),
        ("formulae", list[FactFormula]),
    ):
        if name in payload:
            try:
                TypeAdapter(schema).validate_python(payload[name])
            except ValidationError as error:
                raise ValueError(f"fact_pack {name} has invalid structure") from error
    return payload

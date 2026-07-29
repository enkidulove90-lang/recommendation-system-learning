"""Build a machine-readable ResearchProfileV2 from existing paper assets."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import settings
from models.research_profile import (
    AgentDesignProfile,
    DatasetReference,
    EvidenceBundle,
    ExperimentImplementation,
    ExperimentProfile,
    ExperimentProtocol,
    ExperimentResult,
    HardwareSpec,
    MethodComponent,
    PaperClassification,
    PaperIdentity,
    ProfileProvenance,
    ProfileQuality,
    ReproducibilityInfo,
    ResearchClaim,
    ResearchProfileV2,
    SourceReference,
)
from skills.base_module import BaseSkill, register_skill
from skills.section_router import route_sections, select_evidence, source_sha256
from storage.knowledge_registry import KnowledgeRegistry
from storage.paper_assets import find_paper_bundle, find_parsed_markdown, normalize_arxiv_id, summary_path
from storage.profile_store import ProfileStore
from storage.paper_metadata import load_paper_metadata
from storage.summary_compat import parse_summary_markdown


_METRIC_RE = re.compile(
    r"\b(?:N@\d+|R@\d+|NDCG(?:@\d+)?|Recall(?:@\d+)?|Precision(?:@\d+)?|"
    r"HitRate(?:@\d+)?|Hit\s*Rate(?:@\d+)?|HR(?:@\d+)?|MRR|MAP(?:@\d+)?|AUC|F1)\b",
    flags=re.IGNORECASE,
)
_RESULT_RE = re.compile(
    r"(?P<metric>(?:N@\d+|R@\d+|NDCG(?:@\d+)?|Recall(?:@\d+)?|"
    r"Precision(?:@\d+)?|HitRate(?:@\d+)?|HR(?:@\d+)?|MRR|MAP(?:@\d+)?|AUC|F1))"
    r"\s*(?:=|:|达到|为)\s*(?P<value>\d+(?:\.\d+)?)",
    flags=re.IGNORECASE,
)
_URL_RE = re.compile(r"https?://(?:www\.)?github\.com/[^\s)>]+", flags=re.IGNORECASE)


@register_skill("research-profile-build")
class ProfileBuilderSkill(BaseSkill):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.registry = KnowledgeRegistry()
        self.store = ProfileStore()

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        arxiv_id = normalize_arxiv_id(str(kwargs.get("arxiv_id", "")))
        force = bool(kwargs.get("force", False))
        if not arxiv_id:
            return {"error": "arxiv_id is required.", "profile_path": None}

        markdown_path = find_parsed_markdown(arxiv_id)
        if markdown_path is None:
            return {"error": f"Parsed Markdown not found for {arxiv_id}", "profile_path": None}

        source_text = markdown_path.read_text(encoding="utf-8", errors="replace")
        source_hash = source_sha256(source_text)
        summary_md = summary_path(arxiv_id)
        summary_data = parse_summary_markdown(summary_md) if summary_md.exists() else self._empty_summary(arxiv_id)
        summary_hash = self._file_hash(summary_md) if summary_md.exists() else ""

        existing = self.store.load_profile(arxiv_id)
        if (
            existing is not None
            and not force
            and existing.provenance.source_hash == source_hash
            and existing.provenance.summary_hash == summary_hash
        ):
            return {
                "error": None,
                "profile_path": str(self.store.profiles_dir / f"{arxiv_id}.json"),
                "evidence_path": str(self.store.evidence_dir / f"{arxiv_id}.json"),
                "profile": existing.model_dump(mode="json"),
                "skipped": True,
            }

        metadata = self._load_seed_metadata(arxiv_id)
        sections = route_sections(source_text)
        parsed_title = self._parsed_title(source_text)
        identity = self._build_identity(arxiv_id, summary_data, metadata, parsed_title)
        routed_abstract = self._section_text(sections, ("abstract",), max_chars=4000)
        if not summary_data["main_contribution"]:
            summary_data["main_contribution"] = metadata.get("abstract", "") or routed_abstract
        if not summary_data["title"]:
            summary_data["title"] = metadata.get("title", "")
            identity.title = summary_data["title"]

        classification_text = "\n".join(
            [
                identity.title,
                identity.chinese_title,
                summary_data["main_contribution"],
                summary_data["methodology"],
                " ".join(summary_data["innovation_points"]),
                source_text[:20000],
            ]
        )
        classification = self._classify(classification_text, identity.paper_type)

        evidence_items = []
        contribution_ev = select_evidence(
            sections=sections,
            query=summary_data["main_contribution"],
            claim_type="contribution",
            preferred_types=("abstract", "introduction", "conclusion"),
            source_path=markdown_path,
            source_hash=source_hash,
        )
        if contribution_ev:
            evidence_items.append(contribution_ev)

        method_ev = select_evidence(
            sections=sections,
            query=summary_data["methodology"] or " ".join(summary_data["innovation_points"]),
            claim_type="method",
            preferred_types=("method",),
            source_path=markdown_path,
            source_hash=source_hash,
        )
        if method_ev:
            evidence_items.append(method_ev)

        experiment_query = "\n".join(
            [
                summary_data["experimental_results"],
                " ".join(summary_data["benchmark_datasets"]),
                " ".join(summary_data["experimental_conditions"].values()),
            ]
        )
        experiment_ev = select_evidence(
            sections=sections,
            query=experiment_query,
            claim_type="experiment",
            preferred_types=("experiment",),
            source_path=markdown_path,
            source_hash=source_hash,
        )
        if experiment_ev:
            evidence_items.append(experiment_ev)

        limitations = self._extract_limitations(sections)
        limitation_ev = None
        if limitations:
            limitation_ev = select_evidence(
                sections=sections,
                query=" ".join(limitations),
                claim_type="limitation",
                preferred_types=("conclusion",),
                source_path=markdown_path,
                source_hash=source_hash,
            )
            if limitation_ev:
                evidence_items.append(limitation_ev)

        claim_evidence = [
            item.evidence_id
            for item in (contribution_ev, method_ev, limitation_ev)
            if item is not None
        ]
        research_claim = ResearchClaim(
            problem=self._first_sentence(summary_data["main_contribution"]),
            one_sentence_contribution=self._first_sentence(summary_data["main_contribution"]),
            method_overview=summary_data["methodology"],
            method_components=self._method_components(
                summary_data["innovation_points"],
                method_ev.evidence_id if method_ev else None,
            ),
            limitations=limitations,
            evidence_ids=claim_evidence,
        )

        experiment = self._build_experiment(
            summary_data=summary_data,
            source_text=source_text,
            experiment_text=self._section_text(sections, ("experiment",), max_chars=12000),
            evidence_id=experiment_ev.evidence_id if experiment_ev else None,
        )
        issues = self._initial_issues(summary_md, summary_data, markdown_path)
        if (
            summary_data["title"]
            and parsed_title
            and not self._titles_are_compatible(summary_data["title"], parsed_title)
        ):
            issues.append(
                "summary English title conflicts with the parsed paper title; parsed title is authoritative"
            )
        confidence = max(0.2, 0.72 - 0.08 * len(issues))
        profile = ResearchProfileV2(
            paper_id=arxiv_id,
            identity=identity,
            classification=classification,
            research_claim=research_claim,
            experiment=experiment,
            agent_design=self._build_agent_design(summary_data["agent_relevance"]),
            quality=ProfileQuality(
                status="needs_review",
                grade="C",
                confidence=round(confidence, 2),
                issues=issues,
            ),
            provenance=ProfileProvenance(
                parser=self._detect_parser(markdown_path, source_text),
                summarizer_model=summary_data["summarizer_model"],
                generated_at=datetime.now(timezone.utc).isoformat(),
                source_path=str(markdown_path),
                source_hash=source_hash,
                summary_path=str(summary_md) if summary_md.exists() else "",
                summary_hash=summary_hash,
            ),
        )
        evidence = EvidenceBundle(
            paper_id=arxiv_id,
            source_path=str(markdown_path),
            source_hash=source_hash,
            parser=profile.provenance.parser,
            items=evidence_items,
        )
        profile_path = self.store.save_profile(profile)
        evidence_path = self.store.save_evidence(evidence)
        schema_path = self.store.export_schema()
        return {
            "error": None,
            "profile_path": str(profile_path),
            "evidence_path": str(evidence_path),
            "schema_path": str(schema_path),
            "profile": profile.model_dump(mode="json"),
            "skipped": False,
        }

    def _classify(self, text: str, paper_type: str) -> PaperClassification:
        directions = self.registry.classify(text, "research_directions")
        stages = self.registry.classify(text, "pipeline_stages")
        problems = self.registry.classify(text, "problems")
        paradigms = self.registry.classify(text, "technical_paradigms")
        modalities = self.registry.classify(text, "modalities")
        maturity_matches = self.registry.classify(text, "maturity")
        maturity = maturity_matches[0] if maturity_matches else (
            "conceptual" if paper_type in {"survey", "theory"} else "research_prototype"
        )
        return PaperClassification(
            research_directions=directions,
            pipeline_stages=stages,
            problems=problems,
            technical_paradigms=paradigms,
            modalities=modalities,
            maturity=maturity,
        )

    def _build_identity(
        self,
        arxiv_id: str,
        summary_data: dict[str, Any],
        metadata: dict[str, Any],
        parsed_title: str,
    ) -> PaperIdentity:
        authoritative_title = metadata.get("title", "") or parsed_title or summary_data["title"]
        combined_title = f"{authoritative_title} {summary_data['chinese_title']}"
        paper_types = self.registry.classify(combined_title, "paper_type")
        priority = ("survey", "dataset", "benchmark", "system", "theory", "experiment")
        paper_type = next((item for item in priority if item in paper_types), "experiment")
        return PaperIdentity(
            title=authoritative_title,
            chinese_title=summary_data["chinese_title"],
            authors=[str(author) for author in metadata.get("authors", [])],
            published_date=str(metadata.get("published", ""))[:10],
            source=SourceReference(
                type="arxiv",
                url=metadata.get("arxiv_url", f"https://arxiv.org/abs/{arxiv_id}"),
            ),
            paper_type=paper_type,
        )

    def _build_experiment(
        self,
        *,
        summary_data: dict[str, Any],
        source_text: str,
        experiment_text: str,
        evidence_id: str | None,
    ) -> ExperimentProfile:
        conditions = summary_data["experimental_conditions"]
        metric_source = " ".join(
            [
                conditions.get("metrics", ""),
                summary_data["experimental_results"],
                experiment_text,
            ]
        )
        metrics = self._unique(_METRIC_RE.findall(
            metric_source
        ))
        evidence_ids = [evidence_id] if evidence_id else []
        datasets = [
            DatasetReference(
                registry_id=self.registry.resolve_dataset(name),
                paper_name=name,
            )
            for name in summary_data["benchmark_datasets"]
        ]
        implementation_text = conditions.get("implementation", "")
        if implementation_text == "not_reported":
            implementation_text = experiment_text
        hardware = self._extract_hardware(implementation_text)
        framework = self._first_match(
            implementation_text,
            ("PyTorch", "TensorFlow", "JAX", "RecBole", "MS-Swift"),
        )
        optimizer = self._first_match(implementation_text, ("AdamW", "Adam", "SGD", "Adagrad"))
        hyperparameters = self._extract_hyperparameters(implementation_text)
        unreported = [
            name
            for name, value in (
                ("hardware", hardware),
                ("framework", framework),
                ("optimizer", optimizer),
                ("hyperparameters", hyperparameters),
            )
            if not value
        ]
        results = [
            ExperimentResult(
                metric=match.group("metric"),
                value=float(match.group("value")),
                evidence_ids=evidence_ids,
            )
            for match in _RESULT_RE.finditer(summary_data["experimental_results"])
        ]
        code_match = _URL_RE.search(source_text)
        task = conditions.get("task_and_data", "not_reported")
        if task == "not_reported":
            task = self._extract_task_description(experiment_text)
        baselines_text = conditions.get("baselines", "not_reported")
        baselines = (
            self._extract_baseline_sentences(experiment_text)
            if baselines_text == "not_reported"
            else [baselines_text]
        )
        return ExperimentProfile(
            datasets=datasets,
            protocol=ExperimentProtocol(
                task=task,
                split=self._extract_split(
                    " ".join([conditions.get("task_and_data", ""), experiment_text])
                ),
                metrics=metrics,
                baselines=baselines,
                evidence_ids=evidence_ids,
            ),
            implementation=ExperimentImplementation(
                hardware=hardware,
                framework=framework,
                optimizer=optimizer,
                hyperparameters=hyperparameters,
                unreported_fields=unreported,
                evidence_ids=evidence_ids if implementation_text else [],
            ),
            results=results,
            results_summary=summary_data["experimental_results"],
            reproducibility=ReproducibilityInfo(
                code_url=code_match.group(0).rstrip(".,") if code_match else None,
                data_access="public" if datasets else "not_reported",
                reproducibility_grade="B" if code_match and datasets else "C",
            ),
        )

    @staticmethod
    def _method_components(points: list[str], evidence_id: str | None) -> list[MethodComponent]:
        components: list[MethodComponent] = []
        for index, point in enumerate(points, 1):
            cleaned = re.sub(r"^创新点\s*\d*[：:]\s*", "", point).strip()
            name = re.split(r"[：:，,。]", cleaned, maxsplit=1)[0][:40] or f"component_{index}"
            components.append(
                MethodComponent(
                    name=name,
                    role="reported_innovation",
                    mechanism=cleaned,
                    evidence_ids=[evidence_id] if evidence_id else [],
                )
            )
        return components

    @staticmethod
    def _build_agent_design(text: str) -> AgentDesignProfile | None:
        if not text:
            return None
        lessons = [
            item.strip(" ：:")
            for item in re.split(r"\d+[）)、.]\s*", text)
            if item.strip()
        ]
        if len(lessons) <= 1:
            lessons = [sentence.strip() for sentence in re.split(r"[；;]", text) if sentence.strip()]
        return AgentDesignProfile(
            applicability=text,
            design_lessons=lessons[:8],
            source_type="project_analysis",
        )

    @staticmethod
    def _extract_limitations(sections: list[Any]) -> list[str]:
        text = "\n".join(section.text for section in sections if section.section_type == "conclusion")
        if not text:
            return []
        sentences = re.split(r"(?<=[.!?。！？])\s+", text)
        keywords = ("limitation", "future work", "however", "remain", "局限", "未来", "仍然")
        return [
            re.sub(r"\s+", " ", sentence).strip()
            for sentence in sentences
            if any(keyword in sentence.casefold() for keyword in keywords)
        ][:3]

    @staticmethod
    def _extract_hardware(text: str) -> list[HardwareSpec]:
        pattern = re.compile(
            r"(?:(?P<count>\d+)\s*[x×]\s*)?(?:NVIDIA\s+)?"
            r"(?P<model>A100|A800|H100|H800|V100|L40S|RTX\s*\d{4}(?:\s*Ti)?)",
            flags=re.IGNORECASE,
        )
        hardware = []
        for match in pattern.finditer(text):
            hardware.append(
                HardwareSpec(
                    model=match.group("model"),
                    count=int(match.group("count")) if match.group("count") else None,
                )
            )
        return hardware

    @staticmethod
    def _extract_hyperparameters(text: str) -> dict[str, Any]:
        patterns = {
            "batch_size": r"(?:batch size|batch_size|批大小)\s*(?:=|:|为)?\s*(\d+)",
            "learning_rate": r"(?:learning rate|learning_rate|学习率)\s*(?:=|:|为)?\s*([0-9.eE-]+)",
            "epochs": r"(?:epochs?|训练轮数)\s*(?:=|:|为)?\s*(\d+)",
        }
        values: dict[str, Any] = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                values[key] = match.group(1)
        return values

    @staticmethod
    def _extract_split(text: str) -> str:
        if not text or text == "not_reported":
            return "not_reported"
        match = re.search(
            r"(?:split|train(?:ing)?(?:/validation)?(?:/test)?|划分)"
            r"[^.\n]{0,100}?\b(\d{1,2}\s*[:/]\s*\d{1,2}(?:\s*[:/]\s*\d{1,2})?)\b",
            text,
            flags=re.IGNORECASE,
        )
        if match:
            return match.group(1)
        for keyword in ("leave-one-out", "temporal split", "random split", "留一法", "时间划分", "随机划分"):
            if keyword.casefold() in text.casefold():
                return keyword
        return "not_reported"

    @staticmethod
    def _extract_task_description(text: str) -> str:
        if not text:
            return "not_reported"
        without_headings = re.sub(r"^#+\s+.*$", "", text, flags=re.MULTILINE)
        sentences = re.split(r"(?<=[.!?。！？])\s+", re.sub(r"\s+", " ", without_headings))
        for sentence in sentences:
            lowered = sentence.casefold()
            if any(keyword in lowered for keyword in ("experiment", "evaluation", "dataset", "benchmark", "实验", "评估")):
                return sentence[:700].strip()
        return "not_reported"

    @staticmethod
    def _extract_baseline_sentences(text: str) -> list[str]:
        if not text:
            return []
        without_headings = re.sub(r"^#+\s+.*$", "", text, flags=re.MULTILINE)
        sentences = re.split(r"(?<=[.!?。！？])\s+", re.sub(r"\s+", " ", without_headings))
        explicit = [
            sentence[:700].strip()
            for sentence in sentences
            if any(keyword in sentence.casefold() for keyword in ("baseline", "基线"))
        ]
        if explicit:
            return explicit[:3]
        return [
            sentence[:700].strip()
            for sentence in sentences
            if any(keyword in sentence.casefold() for keyword in ("compare", "comparison", "对比"))
        ][:3]

    @staticmethod
    def _section_text(sections: list[Any], types: tuple[str, ...], max_chars: int) -> str:
        return "\n".join(section.text for section in sections if section.section_type in types)[:max_chars]

    @staticmethod
    def _first_sentence(text: str) -> str:
        if not text:
            return ""
        return re.split(r"(?<=[.!?。！？])", text.strip(), maxsplit=1)[0][:500]

    @staticmethod
    def _first_match(text: str, values: tuple[str, ...]) -> str | None:
        return next((value for value in values if value.casefold() in text.casefold()), None)

    @staticmethod
    def _unique(values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            normalized = re.sub(r"\s+", "", value).upper()
            if normalized not in seen:
                seen.add(normalized)
                result.append(normalized)
        return [
            value
            for value in result
            if "@" in value or not any(other.startswith(value + "@") for other in result)
        ]

    @staticmethod
    def _detect_parser(markdown_path: Path, source_text: str) -> str:
        if "local pypdf fallback" in source_text[:1000].casefold():
            return "local_pypdf"
        bundle = markdown_path.parent
        if (bundle / "images").is_dir() or list(bundle.glob("*_origin.pdf")):
            return "mineru"
        return "unknown"

    @staticmethod
    def _initial_issues(
        summary_md: Path,
        summary_data: dict[str, Any],
        markdown_path: Path,
    ) -> list[str]:
        issues = []
        if not summary_md.exists():
            issues.append("DeepSeek summary missing; profile uses parsed-text fallback")
        if all(value == "not_reported" for value in summary_data["experimental_conditions"].values()):
            issues.append("experimental_conditions not backfilled")
        if "local pypdf fallback" in markdown_path.read_text(encoding="utf-8", errors="replace")[:1000].casefold():
            issues.append("local parser has lower structural confidence than MinerU")
        return issues

    @staticmethod
    def _load_seed_metadata(arxiv_id: str) -> dict[str, Any]:
        local_metadata = load_paper_metadata(arxiv_id)
        if local_metadata:
            return local_metadata
        path = settings.DATA_DIR / "metadata" / "recommendations" / f"{arxiv_id}_recommendations.json"
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
        seed = payload.get("seed", {})
        return seed if isinstance(seed, dict) else {}

    @staticmethod
    def _empty_summary(arxiv_id: str) -> dict[str, Any]:
        return {
            "paper_id": arxiv_id,
            "chinese_title": "",
            "title": "",
            "generated_at": "",
            "summarizer_model": "",
            "main_contribution": "",
            "innovation_points": [],
            "methodology": "",
            "benchmark_datasets": [],
            "experimental_conditions": {
                "task_and_data": "not_reported",
                "baselines": "not_reported",
                "metrics": "not_reported",
                "implementation": "not_reported",
            },
            "experimental_results": "",
            "agent_relevance": "",
            "raw_text": "",
        }

    @staticmethod
    def _file_hash(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _parsed_title(source_text: str) -> str:
        match = re.search(r"^#\s+(.+?)\s*$", source_text, flags=re.MULTILINE)
        if not match:
            return ""
        title = match.group(1).strip()
        return "" if re.fullmatch(r"\d{4}\.\d{4,5}", title) else title

    @staticmethod
    def _titles_are_compatible(summary_title: str, parsed_title: str) -> bool:
        words_a = set(re.findall(r"[a-z0-9]{3,}", summary_title.casefold()))
        words_b = set(re.findall(r"[a-z0-9]{3,}", parsed_title.casefold()))
        if not words_a or not words_b:
            return True
        return len(words_a & words_b) / min(len(words_a), len(words_b)) >= 0.35

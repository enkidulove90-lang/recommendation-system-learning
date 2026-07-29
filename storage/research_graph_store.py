"""Persistence for relation graphs, learning paths, and profile recommendations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from config import settings
from models.research_graph import (
    LearningPath,
    ProfileRecommendationReport,
    RelationGraph,
)


class ResearchGraphStore:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or settings.DATA_DIR
        self.relations_dir = self.data_dir / "relations"
        self.learning_paths_dir = self.data_dir / "learning_paths"
        self.recommendations_dir = self.data_dir / "metadata" / "recommendations"
        for directory in (
            self.relations_dir,
            self.learning_paths_dir,
            self.recommendations_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    def save_graph(self, graph: RelationGraph) -> tuple[Path, Path]:
        graph_path = self.relations_dir / "graph.json"
        jsonl_path = self.relations_dir / "relations.jsonl"
        self._write_json(graph_path, graph.model_dump(mode="json"))
        content = "\n".join(
            json.dumps(edge.model_dump(mode="json"), ensure_ascii=False, sort_keys=True)
            for edge in graph.edges
        )
        self._write_text(jsonl_path, content + ("\n" if content else ""))
        return graph_path, jsonl_path

    def load_graph(self) -> RelationGraph | None:
        path = self.relations_dir / "graph.json"
        if not path.exists():
            return None
        return RelationGraph.model_validate_json(path.read_text(encoding="utf-8"))

    def save_learning_path(self, path_model: LearningPath) -> tuple[Path, Path]:
        json_path = self.learning_paths_dir / f"{path_model.path_id}.json"
        md_path = self.learning_paths_dir / f"{path_model.path_id}.md"
        self._write_json(json_path, path_model.model_dump(mode="json"))
        self._write_text(md_path, self._learning_path_markdown(path_model))
        return json_path, md_path

    def save_recommendations(
        self,
        report: ProfileRecommendationReport,
    ) -> tuple[Path, Path]:
        stem = f"{report.seed_id}_profile_recommendations"
        json_path = self.recommendations_dir / f"{stem}.json"
        md_path = self.recommendations_dir / f"{stem}.md"
        self._write_json(json_path, report.model_dump(mode="json"))
        self._write_text(md_path, self._recommendation_markdown(report))
        return json_path, md_path

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        ResearchGraphStore._write_text(
            path,
            json.dumps(payload, ensure_ascii=False, indent=2),
        )

    @staticmethod
    def _write_text(path: Path, content: str) -> None:
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(path)

    @staticmethod
    def _learning_path_markdown(path_model: LearningPath) -> str:
        lines = [
            f"# Learning Path: {path_model.topic}",
            "",
            f"- Level: `{path_model.level}`",
            f"- Objective: {path_model.objective}",
            "",
            "| Step | Role | Paper | Why now | Prerequisites | Quality |",
            "|---:|---|---|---|---|---|",
        ]
        for step in path_model.steps:
            prerequisites = ", ".join(step.prerequisites) or "-"
            lines.append(
                f"| {step.order} | {step.role} | `{step.paper_id}` {step.title} | "
                f"{step.rationale.replace('|', '/')} | {prerequisites} | "
                f"{step.profile_quality} |"
            )
        lines.extend(["", f"_Generated at {path_model.generated_at}_", ""])
        return "\n".join(lines)

    @staticmethod
    def _recommendation_markdown(report: ProfileRecommendationReport) -> str:
        lines = [
            f"# Profile Recommendations for {report.seed_id}",
            "",
            "| Rank | Score | Paper | Role | Quality | Structured reason |",
            "|---:|---:|---|---|---|---|",
        ]
        for item in report.recommendations:
            reason = "; ".join(item.why_this_paper).replace("|", "/")
            lines.append(
                f"| {item.rank} | {item.score:.2f} | `{item.paper_id}` "
                f"{item.title} | {item.comparison_role} | "
                f"{item.profile_quality} | {reason} |"
            )
        lines.extend(["", f"_Generated at {report.generated_at}_", ""])
        return "\n".join(lines)

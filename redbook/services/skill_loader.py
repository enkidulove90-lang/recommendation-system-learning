"""Progressive skill loader: index -> on-demand load -> staged disclosure.

Three layers (per the 2026-11-26 design):

1. **Lightweight index** — ``SkillIndex.match(query)`` reads ONLY the
   ``name`` + ``description`` frontmatter of each SKILL.md (a few dozen chars
   per skill).  No full body is loaded until a skill is actually relevant.
2. **On-demand full load** — ``loader.load(skill_id)`` reads the complete
   SKILL.md and splits it into sections (``##`` headings) lazily.  Multiple
   matching skills are all loaded; unrelated ones are never touched.
3. **Stepwise disclosure** — ``loader.section(skill_id, heading)`` returns
   only one section's instructions for the current execution phase.  The
   model works through phases instead of swallowing every rule at once.

This is deliberately separate from ``skill_manager.py`` (registry integrity /
deprecation tooling): the loader is a RUNTIME component, the manager is a
maintenance tool.

Usage::

    index = SkillIndex.from_root(ROOT)
    hits = index.match("把论文发到小红书草稿")     # layer 1
    loader = SkillLoader(index)
    sk = loader.load(hits[0].skill_id)             # layer 2
    body = loader.section(sk.skill_id, "正文规则")  # layer 3
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any, Iterator

import yaml

SKILL_GLOB = "SKILL.md"
SEARCH_ROOTS = (".agents/skills", ".claude/skills")


@dataclass(frozen=True)
class SkillStub:
    """Layer-1 index entry: only name + description (tiny token footprint)."""

    skill_id: str
    name: str
    description: str
    path: Path


@dataclass
class LoadedSkill:
    """Layer-2: a fully read SKILL.md split into addressable sections."""

    skill_id: str
    name: str
    raw: str
    sections: dict[str, str] = field(default_factory=dict)

    def section_titles(self) -> list[str]:
        return list(self.sections.keys())


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split YAML frontmatter from the body. Returns (meta, body)."""
    if not text.startswith("---"):
        return {}, text
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if not match:
        return {}, text
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        meta = {}
    return (meta if isinstance(meta, dict) else {}), text[match.end():]


def _split_sections(body: str) -> dict[str, str]:
    """Split markdown body into ``## heading`` -> content sections."""
    result: dict[str, str] = {}
    current = "__preamble__"
    buffer: list[str] = []
    for line in body.splitlines():
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            result[current] = "\n".join(buffer).strip()
            current = heading.group(1).strip()
            buffer = []
        else:
            buffer.append(line)
    result[current] = "\n".join(buffer).strip()
    return {key: value for key, value in result.items() if value}


class SkillIndex:
    """Layer 1: scan frontmatter only; never read full SKILL.md bodies."""

    def __init__(self, stubs: list[SkillStub]) -> None:
        self._stubs = {stub.skill_id: stub for stub in stubs}

    @classmethod
    def from_root(cls, root: Path) -> "SkillIndex":
        stubs: dict[str, SkillStub] = {}
        for search_dir in SEARCH_ROOTS:
            base = Path(root) / search_dir
            if not base.is_dir():
                continue
            for path in sorted(base.glob(f"*/{SKILL_GLOB}")):
                text = path.read_text(encoding="utf-8", errors="replace")
                meta, _ = _parse_frontmatter(text)
                name = str(meta.get("name") or path.parent.name).strip()
                description = str(meta.get("description") or "").strip()
                skill_id = path.parent.name
                # First root wins; IDE-local duplicates never override canonical.
                if skill_id not in stubs:
                    stubs[skill_id] = SkillStub(
                        skill_id=skill_id, name=name,
                        description=re.sub(r"\s+", " ", description), path=path)
        return cls(list(stubs.values()))

    def all_stubs(self) -> list[SkillStub]:
        return list(self._stubs.values())

    def index_text(self) -> str:
        """Compact index for injecting into context (name + description only)."""
        return "\n".join(
            f"- {stub.skill_id}: {stub.description[:160]}"
            for stub in self.all_stubs())

    def match(self, query: str, *, limit: int = 3) -> list[SkillStub]:
        """Semantic-ish match by weighted keyword overlap (no embeddings).

        Weights: CJK bigrams and latin words from the query; a skill scores by
        how many query tokens appear in its name/description.  Deterministic,
        dependency-free and adequate for the small (<=10) repo skill set.
        """
        tokens = _tokens(query)
        if not tokens:
            return []
        scored: list[tuple[float, SkillStub]] = []
        for stub in self._stubs.values():
            haystack = _tokens(f"{stub.name} {stub.description}")
            if not haystack:
                continue
            overlap = tokens & haystack
            score = sum(len(token) for token in overlap) / max(1, len(tokens))
            # Name hits are strong signals.
            if any(token in _tokens(stub.name) for token in overlap):
                score += 0.5
            if score > 0:
                scored.append((score, stub))
        scored.sort(key=lambda pair: (-pair[0], pair[1].skill_id))
        return [stub for _, stub in scored[:limit]]


def _tokens(text: str) -> set[str]:
    """Tokenize into latin words and CJK bigrams (crude but useful)."""
    lowered = text.casefold()
    words = set(re.findall(r"[a-z0-9_]+", lowered))
    cjk = re.findall(r"[\u4e00-\u9fff]+", lowered)
    bigrams: set[str] = set()
    for run in cjk:
        if len(run) == 1:
            bigrams.add(run)
        for i in range(len(run) - 1):
            bigrams.add(run[i:i + 2])
    return words | bigrams


class SkillLoader:
    """Layers 2+3: load full skill on demand, expose one section at a time."""

    def __init__(self, index: SkillIndex) -> None:
        self._index = index
        self._loaded: dict[str, LoadedSkill] = {}

    def load(self, skill_id: str) -> LoadedSkill:
        stub = self._index._stubs.get(skill_id)
        if stub is None:
            raise KeyError(f"unknown skill: {skill_id}")
        if skill_id in self._loaded:
            return self._loaded[skill_id]
        text = stub.path.read_text(encoding="utf-8", errors="replace")
        meta, body = _parse_frontmatter(text)
        skill = LoadedSkill(
            skill_id=skill_id,
            name=str(meta.get("name") or stub.name),
            raw=text,
            sections=_split_sections(body),
        )
        self._loaded[skill_id] = skill
        return skill

    def section(self, skill_id: str, heading: str) -> str:
        """Return ONE section's instructions (layer 3: staged disclosure)."""
        skill = self.load(skill_id)
        if heading in skill.sections:
            return skill.sections[heading]
        # Substring match so the caller can use short phase names.
        for title, content in skill.sections.items():
            if heading in title:
                return content
        raise KeyError(
            f"section {heading!r} not in {skill_id}; "
            f"available: {skill.section_titles()}")

    def iter_phases(self, skill_id: str) -> Iterator[tuple[str, str]]:
        for title, content in self.load(skill_id).sections.items():
            if title != "__preamble__":
                yield title, content


def build_loader(root: Path) -> tuple[SkillIndex, SkillLoader]:
    index = SkillIndex.from_root(root)
    return index, SkillLoader(index)


def main() -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="progressive skill loader")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--query", default="", help="layer 1: match skills by query")
    parser.add_argument("--load", default="", help="layer 2: load one skill fully")
    parser.add_argument("--section", default="", help="layer 3: one section only")
    parser.add_argument("--index", action="store_true", help="print compact index")
    args = parser.parse_args()

    index, loader = build_loader(args.root)
    if args.index:
        print(index.index_text())
        return 0
    if args.query:
        print(json.dumps(
            [{"skill_id": s.skill_id, "name": s.name,
              "description": s.description[:200]}
             for s in index.match(args.query)], ensure_ascii=False, indent=2))
        return 0
    if args.load:
        skill = loader.load(args.load)
        print(json.dumps(
            {"skill_id": skill.skill_id, "name": skill.name,
             "sections": skill.section_titles()}, ensure_ascii=False, indent=2))
        if args.section:
            print("\n--- section ---\n" + loader.section(args.load, args.section))
        return 0
    print(json.dumps({"stubs": len(index.all_stubs()),
                      "hint": "use --index / --query / --load"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

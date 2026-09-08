"""内容工厂编排器（Stage 1→3→6 → 发布审核包）。

把叙事引擎 / 标题工厂 / 平台适配串成一条流水线，产出与 redbook
PublicationPackage 同构的 JSON，写入 publish_queue/<content_hash[:32]>/<platform>.json
（review_status=pending），现有 XhsPublisher / WeChatPublisher 可直接读取。
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .narrative_engine import NarrativeEngine
from .platforms import PlatformAdapter, load_platforms
from .schemas import FactoryResult, PaperSummary, TitleVariant, load_summary
from .title_factory import TitleFactory
from .visualization import build_all as build_viz
from .interaction import build_all as build_ix
from .distribution import Distributor
from .analytics import AnalyticsSpec, TitleABTest, SCHEMA_VERSION, PII_POLICY

_DEFAULT_PLATFORMS = ("xhs", "wechat")


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _content_hash(package: dict[str, Any]) -> str:
    payload = {k: v for k, v in package.items() if k not in ("content_hash", "staged_at")}
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def write_package(root: Path, package: dict[str, Any]) -> dict[str, Any]:
    """写入 publish_queue/<hash[:32]>/<platform>.json（同 redbook 路径契约）。"""
    package = dict(package)
    content_hash = _content_hash(package)
    package["content_hash"] = content_hash
    package.setdefault("staged_at", _utc_now())
    path = root / "publish_queue" / content_hash[:32] / f"{package['platform']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "status": "staged", "path": str(path), "staged_id": content_hash}


def _arxiv_links(paper_id: str) -> dict[str, str]:
    return {
        "paper": f"https://arxiv.org/abs/{paper_id}",
        "pdf": f"https://arxiv.org/pdf/{paper_id}",
        "code": "",
    }


def _figure_images(parsed_dir: Path) -> list[str]:
    """尽量从 data/parsed/<id>/ 取论文原图作为配图（小红书发布需要 ≥1 张）。"""
    if not parsed_dir.is_dir():
        return []
    imgs = [str(p) for p in parsed_dir.glob("*.jpg")] + [str(p) for p in parsed_dir.glob("*.png")]
    return sorted(imgs)[:9]


class ContentFactory:
    def __init__(
        self,
        root: Path,
        summaries_dir: Path,
        parsed_dir: Path,
        platforms_yaml: Path | None = None,
        use_llm: bool = False,
    ) -> None:
        self.root = Path(root)
        self.summaries_dir = Path(summaries_dir)
        self.parsed_dir = Path(parsed_dir)
        self.use_llm = use_llm
        self.adapter = (
            load_platforms(platforms_yaml)
            if platforms_yaml and Path(platforms_yaml).is_file()
            else PlatformAdapter({})
        )

    def run(
        self,
        paper_id: str,
        platforms: tuple[str, ...] = _DEFAULT_PLATFORMS,
        *,
        viz: bool = False,
        interaction: bool = False,
        distribute: bool = False,
        analytics: bool = False,
        experiment: str | None = None,
    ) -> FactoryResult:
        summary, _ = load_summary(paper_id, self.summaries_dir)
        story = NarrativeEngine(polish=self.use_llm).build(summary, paper_id)
        titles = TitleFactory().generate(summary, n=5, use_llm=self.use_llm)
        chosen = titles[0].text if titles else summary.title_zh
        experiment_id = experiment or f"cf_title_ab_{paper_id}"

        images = _figure_images(self.parsed_dir / paper_id)
        links = _arxiv_links(paper_id)
        packages: list[dict[str, Any]] = []

        for plat in platforms:
            adapted = self.adapter.adapt(plat, chosen, lead=story.hook)
            title = adapted["title"]
            body = self._body_for(plat, story, title)
            pkg = {
                "paper_id": paper_id,
                "platform": plat,
                "canonical_url": links["paper"],
                "title": title,
                "body_markdown": body,
                "image_paths": images,
                "links": links,
                "review_status": "pending",
                "source_attribution": "图表摘自论文，仅作学术解读。",
                "metadata": {
                    "title_variants": [
                        {"text": t.text, "score": t.score, "needs_rewrite": t.needs_rewrite}
                        for t in titles
                    ],
                    "experiment_id": f"cf_{paper_id}",
                    "platform": plat,
                    "status": "draft",
                    "story_stage": "factory",
                    "bound_fields": story.bound_fields,
                    "tone": adapted.get("tone"),
                },
            }
            packages.append(pkg)

        result = FactoryResult(
            paper_id=paper_id, story=story, titles=titles, chosen_title=chosen, packages=packages
        )

        # Stage 4/5/7/8 按需构建（默认关，避免无谓开销）
        if viz:
            result.visuals = [v.to_dict() for v in build_viz(summary, story)]
        if interaction:
            result.interactions = [i.to_dict() for i in build_ix(summary)]
        if distribute:
            dist = Distributor()
            result.distribution = [
                j.to_dict() for j in dist.build(
                    packages, ab_experiment=experiment_id,
                    ab_variants=[t["text"] for t in
                                 (packages[0].get("metadata") or {}).get("title_variants", [])][:8],
                )
            ]
        if analytics:
            a = AnalyticsSpec()
            ab_variants = [chosen] + [t.text for t in titles[1:5]]
            _, ab_event = a.assign_ab_variant(experiment_id, ab_variants, session_id=result.paper_id)
            result.analytics = {
                "schema_version": SCHEMA_VERSION,
                "ga4_events": [e.to_dict() for e in a.ga4_events()],
                "metabase_dashboard": a.metabase_dashboard(),
                "tracking_snippet": a.tracking_snippet(
                    content_id=paper_id, experiment=experiment_id, variants=ab_variants),
                "ab_plan": {"experiment": experiment_id, "variants": ab_variants,
                            "algorithm": "hash_stable"},
                "ab_assign_demo": ab_event,
                "pii_policy": PII_POLICY,
            }
            for pkg in result.packages:
                pkg.setdefault("metadata", {})
                pkg["metadata"]["experiment_id"] = experiment_id
                pkg["metadata"]["ab_plan"] = {"variants": ab_variants, "algorithm": "hash_stable"}
        return result

    def stage(self, result: FactoryResult) -> list[dict[str, Any]]:
        """把每个平台的包写入 publish_queue（人工审核闸前），并侧写 Stage 4/5/7/8 产物。"""
        receipts = [write_package(self.root, pkg) for pkg in result.packages]
        self._stage_extras(result)
        return receipts

    def _stage_extras(self, result: FactoryResult) -> list[dict[str, Any]]:
        """把可视化 / 交互 / 分发 / 分析产物写入 publish_queue/<paper_hash>/ 侧车文件。"""
        extras = {
            "viz.json": result.visuals,
            "interaction.json": result.interactions,
            "distribution.json": result.distribution,
            "analytics.json": result.analytics,
        }
        written = []
        for fname, payload in extras.items():
            if not payload:
                continue
            pid_hash = hashlib.sha256(result.paper_id.encode("utf-8")).hexdigest()[:32]
            path = self.root / "publish_queue" / pid_hash / fname
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            written.append({"ok": True, "status": "staged-extra", "path": str(path)})
        return written

    @staticmethod
    def _body_for(plat: str, story: Any, title: str) -> str:
        if plat == "xhs":
            # 小红书：结论前置 + 封面文案，复用故事四段式浓缩
            return f"{title}\n\n{story.hook}\n\n{story.climax_section}\n\n{story.ending_section}"
        # 公众号 / 其他：完整四段式长文
        return story.full_text

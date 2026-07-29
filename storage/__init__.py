"""
storage/ — 数据持久化模块

paper_store.py 负责将爬取结果保存为 JSON 文件，
按主题和时间组织输出目录结构。
"""

from storage.paper_store import PaperStore
from storage.asset_governance import AssetGovernance
from storage.knowledge_registry import KnowledgeRegistry
from storage.paper_assets import (
    find_bundle_pdf,
    find_paper_bundle,
    find_parsed_markdown,
    normalize_arxiv_id,
    paper_id_from_folder,
    resolve_paper_bundle,
    summary_path,
)
from storage.profile_store import ProfileStore
from storage.research_graph_store import ResearchGraphStore
from storage.paper_metadata import (
    load_paper_metadata,
    paper_metadata_path,
    save_paper_metadata,
)
from storage.summary_compat import parse_summary_markdown

__all__ = [
    "PaperStore",
    "AssetGovernance",
    "KnowledgeRegistry",
    "ProfileStore",
    "ResearchGraphStore",
    "find_bundle_pdf",
    "find_paper_bundle",
    "find_parsed_markdown",
    "normalize_arxiv_id",
    "paper_id_from_folder",
    "resolve_paper_bundle",
    "summary_path",
    "parse_summary_markdown",
    "load_paper_metadata",
    "paper_metadata_path",
    "save_paper_metadata",
]

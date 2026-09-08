"""摄入层：各数据源 adapter，统一输出 List[Paper]。"""
from .base import IngestAdapter, build_paper, normalize_text
from .openalex import OpenAlexAdapter
from .arxiv_source import ArxivAdapter
from .huggingface import HuggingFaceAdapter
from .semanticscholar import SemanticScholarAdapter

__all__ = [
    "IngestAdapter", "build_paper", "normalize_text",
    "OpenAlexAdapter", "ArxivAdapter", "HuggingFaceAdapter", "SemanticScholarAdapter",
]

# 数据源注册表（设计文档§1 四层数据源）
ADAPTER_REGISTRY = {
    "openalex": OpenAlexAdapter,
    "arxiv": ArxivAdapter,
    "huggingface": HuggingFaceAdapter,
    "s2": SemanticScholarAdapter,
}


def get_adapter(name: str, **kwargs):
    cls = ADAPTER_REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"Unknown adapter '{name}'. Known: {list(ADAPTER_REGISTRY)}")
    return cls(**kwargs)

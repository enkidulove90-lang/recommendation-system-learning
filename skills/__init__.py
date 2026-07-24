"""
skills/ — 技能模块

提供可复用的独立 skill，每个 skill 遵循统一的 BaseSkill 接口。
已注册技能:
  - arxiv-search    : arXiv 论文搜索
  - metadata-extract: 论文元数据提取
  - pdf-parse       : MinerU PDF 解析
"""

from skills.base_module import (
    BaseSkill,
    register_skill,
    get_skill,
    list_registered_skills,
)

# 导入所有技能模块以触发 @register_skill 装饰器注册
from skills import arxiv_searcher          # noqa: F401 — arXiv 搜索
from skills import metadata_extractor      # noqa: F401 — 元数据清洗
from skills import pdf_parser              # noqa: F401 — MinerU v4 PDF 解析
from skills import pdf_downloader          # noqa: F401 — PDF 下载
from skills import deepseek_summarizer     # noqa: F401 — DeepSeek 论文摘要

__all__ = [
    "BaseSkill",
    "register_skill",
    "get_skill",
    "list_registered_skills",
]

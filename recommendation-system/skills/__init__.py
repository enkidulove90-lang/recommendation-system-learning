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

__all__ = [
    "BaseSkill",
    "register_skill",
    "get_skill",
    "list_registered_skills",
]

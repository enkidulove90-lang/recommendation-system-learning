"""
skills/base_module.py — 技能抽象基类

定义所有 skill 必须实现的统一接口。
新的 skill（如未来接入 Semantic Scholar 搜索）只需继承 BaseSkill
并实现 execute() 方法即可无缝集成到主流程。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


# ---------------------------------------------------------------------------
# 抽象基类
# ---------------------------------------------------------------------------

class BaseSkill(ABC):
    """
    Skill 基类。

    每个 skill 命名一个唯一 skill_type，供注册表 / 工厂函数查找。
    子类必须实现:
      - execute(**kwargs) -> dict[str, Any]
    """

    skill_type: str = "base"

    def __init__(self, **kwargs: Any) -> None:
        self.config = kwargs  # 运行时允许注入额外参数

    @abstractmethod
    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """
        执行该技能的核心逻辑。

        参数:
            **kwargs: 具体技能所需的运行时参数，
                      如搜索关键词、论文 ID、PDF 路径等。

        返回:
            dict[str, Any]: 统一以字典形式返回结果。
                            列表结果放在 "results" 键下。
        """
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} skill_type='{self.skill_type}'>"


# ---------------------------------------------------------------------------
# 注册表 & 工厂
# ---------------------------------------------------------------------------

_skill_registry: dict[str, type[BaseSkill]] = {}


def register_skill(skill_type: str):
    """装饰器：将 Skill 子类注册到全局注册表。"""

    def decorator(cls: type[BaseSkill]) -> type[BaseSkill]:
        cls.skill_type = skill_type
        _skill_registry[skill_type] = cls
        return cls

    return decorator


def get_skill(skill_type: str, **kwargs: Any) -> BaseSkill:
    """工厂函数：按 skill_type 获取技能实例。"""
    cls = _skill_registry.get(skill_type)
    if cls is None:
        raise ValueError(
            f"Unknown skill type '{skill_type}'. "
            f"Registered: {list(_skill_registry.keys())}"
        )
    return cls(**kwargs)


def list_registered_skills() -> list[str]:
    """列出所有已注册的技能类型。"""
    return list(_skill_registry.keys())

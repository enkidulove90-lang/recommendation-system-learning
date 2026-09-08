"""应用层：每日 digest 生成与投递（设计文档§1 应用层）。"""
from .digest import render_digest
from .delivery import deliver

__all__ = ["render_digest", "deliver"]

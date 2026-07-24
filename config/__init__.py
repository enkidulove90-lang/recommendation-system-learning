"""
config/ — 全局配置模块

使用方式:
    from config import settings
    api_key = settings.MINERU_API_KEY
"""

from config.settings import settings

__all__ = ["settings"]

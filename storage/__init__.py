"""
storage/ — 数据持久化模块

paper_store.py 负责将爬取结果保存为 JSON 文件，
按主题和时间组织输出目录结构。
"""

from storage.paper_store import PaperStore

__all__ = ["PaperStore"]

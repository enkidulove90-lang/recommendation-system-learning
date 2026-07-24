"""
pipeline/ — 业务流程编排

端到端的论文处理流水线:
  - crawl_pipeline:    论文爬取与 PDF 下载
  - parse_pipeline:    批量 MinerU 解析
  - summarize_pipeline: 批量 DeepSeek 摘要生成
  - merge_pipeline:    文档合并与 Token 控制
"""

from pipeline.merge_pipeline import DocumentMerger

__all__ = ["DocumentMerger"]

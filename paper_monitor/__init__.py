"""paper_monitor — 前沿论文自动发现·过滤·推送系统。

按 docs/openalex_paper_monitoring.md 设计方案实现：
  数据源层: OpenAlex REST (#5) / arXiv API (#8) / HF Daily Papers (#11) / Semantic Scholar (#9)
  处理层:   摄入 -> 归一 -> 去重 -> 主题分类 -> 打分排序 -> 推荐生成
  存储层:   SQLite (个人版)
  应用层:   每日 digest 生成与投递 (console/file/email/slack)

设计引用见 docs/openalex_paper_monitoring.md 第 1-6 节。
"""

__version__ = "0.1.0"

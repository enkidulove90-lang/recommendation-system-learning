# 02-framework-method

Type: framework
Style: blueprint
Palette: tech-blue
Purpose: 方法框架节——用「依赖 DAG + 双容器」讲清 LOOPSBENCH 的任务结构：节点=可独立测试的单元，边=前置关系；上容器「编辑执行」、下容器「测试裁决」。
Visual: 蓝图风格，浅蓝网格背景。一张有向无环图（DAG），圆角方块节点代表可独立测试的单元，细箭头表达前置关系；一条横向分隔线把图分成上下两区，分别标注「编辑执行 / 测试裁决」。线条纤细精确、留白充足、无真实代码、仅保留两区提示。
Language: zh
Negative: 不要真实代码、不要堆文字、不要花哨渐变、保持架构图的冷静克制

## 最终生成 prompt（发给图像后端）

A blueprint-style technical diagram in tech-blue palette (main #3a5fcd, light #eef3ff, deep #1f3a8a, gray #8a94a6). A directed acyclic graph (DAG) of rounded-square nodes representing independent testable units, connected by thin arrows showing prerequisite relations. A horizontal divider splits the diagram into two zones: top zone "edit & execute", bottom zone "test & judge". Light blue grid background, thin precise lines, clean architectural blueprint aesthetic, lots of whitespace, no real code, only the two zone hints as minimal labels. 1536x1024.

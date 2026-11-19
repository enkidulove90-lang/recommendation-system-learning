# 《小红书 RecMem 草稿修复会话审计》结构化审查报告

审查时间：2026-11-19（Asia/Shanghai）
审查对象：`docs/session_audit_xhs_draft_repair_2026-11-19.md`
对照目标：**构建完整、可一次性交付的后端服务，减少反复调试与 agent 自主发挥空间**
审查方法：逐节对照文档内容 + 仓库实况核验（引用的 5 个规范/代码文件、暂存包、checkpoint 均已确认真实存在）

---

## 一、需要改进的方面（逐项附理由）

### A1. 修复知识散落在会话审计中，未固化到代码/规范层
**现状**：定位结论（Creator Center 话题展示带 `#` 前缀、点选后面板收起、原生键盘输入路径不可用、`{ok,data}` 包装）只存在于这份审计 md 的叙述里。
**理由**：目标是"减少 agent 自主发挥"。这些是平台行为的硬事实，下一次会话若不读这份审计就会重新踩坑、重新试错。应将它们写入 `redbook/docs/xhs-content-spec.md`（作为平台行为约束章节）和 `xiaohongshu_delivery.py` 的模块级注释/常量，使规范成为唯一权威，审计文档只做历史索引。

### A2. `--publish` 命令语义与字面不符
**现状**：`--publish` 实际动作是"保存草稿"，文档自己标注为"历史兼容命名"。
**理由**：agent 或新维护者看到 `--publish` 会产生两种误判：要么犹豫不敢执行，要么理解为公开发布（违反"只存草稿"铁律）。这正是"自主发挥空间"的典型来源。建议增加显式别名 `--save-draft` 作为主命令，`--publish` 保留为 deprecated 别名并在 `--help` 中明示语义。

### A3. 失败恢复策略不一致：残缺稿"删旧 vs 留旧"矛盾
**现状**：delivery 实现是"保存后回读失败即删除本次新建残缺稿"；但最终结果一节写"旧的拆分草稿未被删除，以保留人工审计空间"。
**理由**：两种口径并存会导致下次遇到同类故障时行为不可预测（agent 需要自行判断删不删）。一次性交付服务需要**明确的孤儿草稿治理策略**：建议本地维护 run_id ↔ draft_id 映射表，同 slug 重跑先对账（存在完整稿则复用/跳过，残缺稿则按策略清理），并把"留审计"作为显式配置项而非默认行为。

### A4. 验证步骤是内联 `python -c`，不可复用
**现状**：保存后回读用两条长 `python -c` 内联命令（`_verify_saved_draft` + `fetch_drafts` 清点）。
**理由**：内联命令不可复现、不可进 CI、依赖会话上下文（草稿 ID 是人手粘的）。应固化为 CLI 子命令：`python -m redbook.cli note <slug> --verify --draft-id <id>`，输出统一 JSON schema（body_ok/topics_ok/pdf_ok + draft 记录摘要），作为链路的常设终验步骤。

### A5. 外部工具链版本无门禁断言
**现状**：扩展 1.0.25 过期导致故障，升级到 1.0.27 修复；OpenCLI 2.x 响应包装变化也造成过断裂。但当前只有 `opencli doctor` 的人工检查记录。
**理由**：后端服务的可交付性依赖外部依赖版本被**前置断言**而非事后排查。建议在链路入口增加预检门禁：doctor 输出的 `extensionVersion`/`extensionOutdated`/`connectivity.ok` 必须满足期望值（写入 config），不满足直接 blocked——这与 ADA 平台"unresolved 参数 → blocked 且不启动进程"的设计哲学一致。

### A6. 错误非结构化，靠文本匹配
**现状**：关键报错（"Native input requires a visible browser page"、"did not offer exact topic chip"、"topic chip click failed"）是自由文本。
**理由**：文本匹配脆弱且不可归因。应为投递链路定义错误码表（如 `E_NATIVE_INPUT`、`E_TOPIC_UNAVAILABLE`、`E_VERIFY_MISMATCH`、`E_OPENCLI_WRAP`），每类绑定处置动作与是否可重试，事件里落错误码而非只落 message。后端 SSE/事件流消费者（UI、审计）才有稳定契约。

### A7. 审计缺可追溯性元数据
**现状**：文档无命令级时间戳（仅生成日期）、无相关 git commit hash / 改动 diff 引用、命令未记录退出码。
**理由**：审计的核心价值是"故障可回溯到具体代码版本与命令结果"。缺 commit hash 时无法知道"修复"对应哪个提交；无退出码时 `ok:true/false` 之外的静默失败会被漏掉。后续会话审计模板应强制含：分支+commit、每命令 exit code、关键断言的实际值 vs 期望值。

### A8. staged_id 与暂存目录名规则不一致
**现状**：目录名 `0174757fe0efd78a1db40a8b4309eec3`（32 hex）≠ staged_id `0174757…df7ec86cfaaa8ec4ed4b84296f2a0757`（64 hex，前 32 位相同）。
**理由**：两套标识并存且截断规则未成文，脚本间若按全文匹配会失败、按前缀匹配又易碰撞。应统一为"目录名 = staged_id 全文"或明文规定截断规则并写入 spec。

---

## 二、内容重复的部分及合并建议

### R1. `{ok,data}` 解包逻辑双实现
`redbook/infrastructure/xiaohongshu_delivery.py` 与 `redbook/scripts/xhs_drafts.py` 各自兼容 OpenCLI 2.x 包装。**建议**：提取 `redbook/infrastructure/opencli_client.py` 单一适配层（会话管理 + 参数位置 + 响应解包 + 错误码），两处只调用不复制。理由：OpenCLI 3.x 若再变包装，改一处即可。

### R2. 内容硬门槛四处承载
AGENTS.md、`redbook/docs/xhs-content-spec.md`、`config/xhs_content_rules.yaml`、`.agents/skills/xhs-paper-draft/SKILL.md` 都在复述"正文纯文本/≤1000 字/真实话题/PDF 同稿/只存草稿"。**建议**：YAML 为唯一机读权威；SKILL.md 与 spec 引用 YAML 并给路径，不再复述数值。理由：多处复述必然演化出不一致（本仓库已发生过 params/design 两套文档冲突，靠 §11 仲裁表补救——教训应提前规避）。

### R3. 话题实体处理逻辑分散
候选标签收敛（yaml）+ 面板读取（browser eval）+ 去前缀 + 每次点选后重读，散在 delivery 与审计叙述中。**建议**：集中为 delivery 内独立的 topic binder 组件，输入=候选实体列表，输出=已点选实体清单+面板快照证据。理由：这是本次故障的核心环节，值得单一可测单元。

### R4. 回读验证双通道
`_verify_saved_draft`（IndexedDB 深校验）与 `fetch_drafts`（列表清点）是两个层次但无统一出口。**建议**：合并为 `--verify` 子命令内部的两级断言（L1 列表在册 → L2 IndexedDB 内容一致），输出单一 JSON。理由：两级缺一时结论是残缺的（列表在册≠内容完整）。

### R5. 审计文档内部：表格与命令记录重复叙事
"使用的技能"表、"调用的工具/MCP 记录"表、命令记录三处对同一流程各描述一遍。**建议**：后续审计模板改为"阶段 → 命令 → 断言/结果"单一表格链，表格只留技能/工具的映射索引。理由：重复叙事在事故复盘时会因措辞差异引入歧义（本次"未删除残缺稿"口径已现端倪）。

---

## 三、需要额外解决的问题清单

| # | 问题 | 说明与建议 |
|---|---|---|
| P1 | 平台端孤儿草稿 | 旧拆分稿仍在草稿箱。需要一次人工决策（删除或留档），并把"投递前对账查重"补进 delivery，防再生成 |
| P2 | 话题候选可用性前置校验 | 候选实体依赖页面推荐面板实时内容；应在 `--validate` 阶段断言候选可被面板提供（面板快照比对），不可用即 fail-fast，而不是投递中途报 `E_TOPIC_UNAVAILABLE` |
| P3 | 登录态/会话健康探针 | IndexedDB 回读与页操作依赖浏览器会话存活+登录态。服务化需启动时探针 + 失效时的显式 blocked 状态（而非运行中途崩） |
| P4 | PDF 附件校验只到元数据级 | 目前核验 `pdf_name`；建议加内容级校验（字节数/sha256 与本地文件比对），否则"同名不同文件"不会被发现的 |
| P5 | 批量/并发的会话隔离与互斥 | 多篇论文连续投递时 `--session` 命名、浏览器窗口互斥、失败隔离需要明确策略（同 ADA 单 GPU 互斥思路：同一时刻只允许一个投递 run） |
| P6 | Windows 特有故障进 doctor 预检 | 原生键盘输入路径问题（E_NATIVE_INPUT）是 Windows+扩展版本组合故障；`opencli doctor` 扩展项补一条最小输入自检，变 blocked 而非投递中途失败 |
| P7 | 测试覆盖缺口 | 13 passed 仅覆盖 delivery 单元；`{ok,data}` 适配、topic binder、verify 两级断言应各有具名测试（对齐 Review Focus 的"每类故障有具名测试"标准） |
| P8 | 审计与 checkpoint 的草稿 ID 一致性 | `checkpoint.json` 记录 draft_saved + 草稿 ID，但缺与平台端 ID 的自动比对步骤；--verify 应同步校验 checkpoint 与平台返回一致 |

---

## 四、与最终目标的对齐结论

本链路已具备工作流后端的雏形（validate → stage → publish/存草稿 → verify → checkpoint），且哈希/回读意识良好。要达到"一次性交付、少调试、少自主发挥"，核心动作是四条：

1. **事实固化**（A1）：平台行为约束进 spec+代码，审计降级为历史索引；
2. **语义去歧义**（A2/A8）：命令名与标识符规则唯一明确；
3. **单一权威 + 单一适配层**（R1–R4）：消除多处复述与双实现；
4. **前置门禁代替事后排查**（A5/A6/P2/P3/P6）：版本、登录态、话题可用性在 run 启动前判定为 blocked，运行中错误走错误码表。

这与本项目 ADA 平台已验证的模式（blocked 不可启动、事件单调、终态一致、每类故障具名测试）完全同构，可直接复用其设计范式。

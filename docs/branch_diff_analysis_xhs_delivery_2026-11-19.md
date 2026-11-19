# phase1 vs experiments：小红书投递链路实现差异与故障关联分析

日期：2026-11-19（Asia/Shanghai）
分析对象：`phase1` 与 `experiments` 两分支的 redbook 投递模块；故障参照 2026-11-19 草稿修复会话审计（"只有 #算法、正文为空、草稿拆分到多条记录"）。
方法：merge-base 定位 → 分支独有提交清单 → 关键文件逐版本标记比对（grep 证据）→ 工作区未提交改动核对。

---

## 一、差异对比

### 1.1 分支拓扑与时间线

- **共同祖先**：merge-base `5e7590c`；两分支共享 phase1 早期全部投递提交（`04250c6`→`a0345a2`）。
- **phase1 独有 4 个提交**（2026-10-20 ~ 10-28）：
  - `8a615c4`（10-20）automation 层：daily_discovery / one_click / **platform_adapters（458 行）**
  - `fe336cb` skills/runbooks 文档
  - `4be4ff0`（10-28）paper_catalog 聚合 + `save-xhs-draft --skip-pdf-attachment`
  - `3918906` intake capture
- **experiments 独有 4 个提交**：
  - `900f446` 统一内容生产入口 + 发布闸门下沉
  - `cae019f`（11-10）**note spec + 后端分层重构**：重写 `xiaohongshu_delivery.py`（1104 行差异，全仓该文件最大重写）、删除 2 个 native input 脚本、新增 `opencli_runtime.py` / `run_log.py` / `scripts/xhs_drafts.py`
  - `6059f5b` 日志 JSONL 化
  - （其余 a44d9df/c078273/931365b 为 ADA 平台与特征调查，非投递相关）

**两分支的投递实现是同一平台的两次独立演化，且互不包含对方的改动。**

### 1.2 delivery 实现的版本差异（关键标记比对）

| 能力 | phase1 版本（804 行） | experiments 已提交版（cae019f, 11-10） | experiments 工作区（11-19 修复，**未提交**） |
|---|---|---|---|
| 话题输入原语 | `opencli_native_input.mjs`（CDP `Input.insertText` 原生路径）+ `opencli_native_file_input.mjs` | 已删除两脚本；chip 点击 + `_type_topic_js`（正文内打 `#`） | 沿用 chip 点击，但补面板状态机 |
| 话题面板交互 | `_click_exact_topic_suggestion`（单一尝试） | `_click_suggestion_js` + tag-group 读取，**无"先读后点"、无"每选一个重开面板"** | ✅ 先读面板、点选后重开重读（PF-1/PF-4 固化） |
| 原生输入失效防线 | 无（路径本身即隐患） | 无（报错 `Native input requires...` 后直接失败） | ✅ CDP eval 替代 + 会话租约清理 |
| OpenCLI 2.x 兼容 | `{ok,data}` 旧包装假设 | **无解包**（`--session` 参数位置也未适配） | ✅ `{ok,data}` 解包 + `--session` 位置修复 |
| 保存后验证 | 无 | **无 `_verify_saved_draft`**（该函数是 11-19 修复新增） | ✅ IndexedDB 深校验，失败删残缺稿 |
| 运行记录 | 无结构化日志 | `run_log.py` JSONL（6059f5b） | 沿用 |
| 对账/注册表 | 无 | 无 | 无（开发计划 M3 待建） |

### 1.3 工作区状态（关键事实）

experiments worktree 当前存在**未提交**的修复：`xiaohongshu_delivery.py`（+199/−51）、`xhs_drafts.py`（+10）、两个测试文件（+76）、未跟踪的 `notes/2611.17921.yaml`。**这些修复不属于任何分支**——phase1 完全没有，experiments 的 git 历史里也没有。

---

## 二、关联分析

### 2.1 故障发生的操作上下文

用户"之前上传草稿功能一直正常"对应的时期是 phase1 链路（`4be4ff0` 于 10-28 仍是 phase1 最新投递功能）。本次故障会话在 **experiments worktree** 执行——实际跑的是 `cae019f` 的重写版 delivery。即：**投递入口从 phase1 链路切换到了 experiments 的中间态重构版本，同时扩展处于 1.0.25（过期）**——实现切换 × 工具链降级，双重变化叠加。

### 2.2 故障与实现差异的逐点对应

| 审计故障表现 | 对应的实现缺口 | 在哪条分支 |
|---|---|---|
| 诊断第一步报 `Native input requires a visible browser page` | 扩展 1.0.25 原生输入路径失效 | phase1 依赖此路径（mjs 脚本）；experiments 已删除但旧报错残留在诊断 |
| 正文为空 / 只有 `#算法` 字样 | `_type_topic_js` 在正文打 `#` 而面板未提供候选（无"先读后点"）；原生输入未派发 | experiments 已提交版 |
| 草稿被拆分到不同草稿记录 | `{ok,data}` 包装未解包 + 会话租约残留导致重试各建一稿 | experiments 已提交版 |
| 残缺稿长期未被发现 | 无 `_verify_saved_draft`、无 registry 对账 | **两分支共同缺失** |
| `Creator Center did not offer exact topic chip` 后重试失败 | 无错误分类与重试策略（E_TOPIC_UNAVAILABLE 场景） | 两分支共同缺失 |

### 2.3 进度差异是否为问题原因？

**是相关因素，但不是根本原因。** 传导链为：

1. **直接诱因**：操作环境切换（phase1 链路 → experiments 中间态实现）+ 扩展降级（1.0.25），而 experiments 的 `cae019f` 重写恰好处在"删掉了 phase1 的旧路径、但新路径的平台行为约束还没补齐"的过渡态。
2. **结构性根因**（与开发计划 A1/A3/A4 对应）：phase1 与 experiments 是**两次平行实现**，且两边的平台行为硬事实（`#` 前缀、面板收起、原生输入不可用、`{ok,data}` 包装）都没有固化为代码常量 + 回归测试；保存后验证与对账机制在两分支同时缺位。因此任何一次实现切换或扩展升级都会暴露新的故障面，且残缺产物无法被及时检测。
3. phase1 并非"更稳的版本"：它依赖的原生输入路径在扩展 1.0.25 下同样断裂（PF-2），只是故障形态不同（输入原语失败 vs 面板状态机失败）。**两条分支都在同一个结构性根因上受损。**

---

## 三、结论与依据

**结论**：进度差异与该问题**直接相关**，但机制是"平行实现 + 平台事实未固化"，而非单纯的一方落后。具体判定：

1. **故障运行的是 experiments 的 `cae019f` 中间态实现**（11-10 重写：删 native 路径、chip 点击版），该版本缺少面板先读后点/每选重开、`{ok,data}` 解包、会话租约清理与保存后验证——这些恰是 11-19 修复逐条补上的内容（依据：§1.2 表格的 grep 标记比对，`_verify_saved_draft` 在已提交版中不存在）。
2. **"之前正常"对应 phase1 链路**，其正常性建立在旧扩展版本 + native input 路径上，该路径在扩展 1.0.25 下已断裂（依据：诊断阶段 `Native input requires...` 报错 + `opencli_native_input.mjs` 的实现方式）。
3. **修复目前不在任何分支**：experiments 工作区存在未提交的 delivery 修复与测试（依据：`git status` 4 个 M + 1 个未跟踪文件）。这是当前最大的悬置风险——任何分支切换或 worktree 重建都会丢失修复。

### 由此新增的两条行动项（并入开发计划）

- **M-1（立即）**：将工作区修复（delivery + tests + 2611.17921.yaml）提交进 experiments，消除"修复悬置"风险；
- **M-1.5（并入 M1）**：合并两分支的平行实现为单一主线——以 experiments 的后端分层为骨架，吸收 phase1 `8a615c4` automation 层（daily_discovery / one_click / platform_adapters）中仍有效的能力，废弃 phase1 的 native-input mjs 路径；此后投递代码只允许一条演化线，杜绝第三条平行实现。此决策同时回答了开发计划中"opencli_client 统一适配层"的宿主问题：`opencli_runtime.py`（experiments 已有，phase1 没有）。

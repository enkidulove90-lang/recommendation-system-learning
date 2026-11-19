# XHS 投递注册表事实源裁定（2026-11-19）

## 决定

在 M3 迁移验收前，`data/workflow_state/<slug>/delivery_registry.json` 是 XHS
单进程投递的唯一在线事实源。SQLite registry 不是并行实现；它是 M3 的一次性迁移
目标。切换完成后，SQLite 成为唯一在线事实源，旧 JSON 仅保留为只读审计记录。

## 理由

- 现有 JSON registry 已覆盖 verified/orphan 与同 `(slug, staged_id)` 的幂等复用，
  并有回归测试。
- 目前没有多 worker 并发写入需求；在 M3 之前引入 SQLite 双写会制造状态分裂风险。
- M3 仍保留 SQLite 的唯一键 `(platform, account, staged_id)`、SAVING intent 与对账
  能力，不降低编排层的最终目标。

## 迁移门槛

1. 以 JSON 为源在一个 SQLite 事务内导入，重复运行不重复写入。
2. 通过 TC-M3-01~06 后才切换读路径；迁移期禁止双写。
3. 切换后 JSON 不参与运行时判定，只用于审计与可追溯核查。

本裁定更新了 `docs/xhs_orchestration_devplan_v2_2026-11-19.md` 的铁律、M3 任务和
决策记录，取代缺失的 `MEMORY.md` 落档位置。

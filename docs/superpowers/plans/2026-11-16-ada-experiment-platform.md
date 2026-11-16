# ADA 实验平台实施计划（2026-11-16）

状态：已实施完成（本文档为实施记录，对应提交见 git log baseline/ada）
定位：SAB-ANC / Hi-SAM DST 架构线的 P0 门禁实验平台脚手架——不产出 benchmark 结论，
不执行 Google Drive 下载，Appendix-A 12 项参数未决时配置返回 `blocked` 且无法启动 GPU 进程。

## Review Focus（五项硬性验收，均有具名测试）

1. 未决 Appendix-A 参数 → 人类可读 `blocked`，禁止创建 GPU 进程
   （`test_config_with_unresolved_appendix_value_is_blocked` / `test_blocked_config_cannot_start_run`）
2. `split_hash` 与 baseline 不符 → **拒绝**而非警告（`test_evaluation_rejects_baseline_with_different_split_hash`）
3. 取消只终止该 run 自己的子进程，事件/产物终态一致（`test_cancel_terminates_only_own_process`）
4. SSE 以 `Last-Event-ID` 续传，终端迁移不重复（`test_events_stream_in_monotonic_sequence`）
5. 图表区分"缺测（null→gap）"与"零值（实点）"，P0 门禁失败前端标红并隐藏 P1 控件
   （`MetricCharts.test.tsx` / `RunDetailPage.test.tsx`）

## 任务分解（6 Tasks，TDD）

| # | 内容 | 关键文件 | 测试 |
|---|------|----------|------|
| 1 | 协议契约 + 数据/特征管线 + C1–C5 门禁 | contracts/data/gates | test_data, test_gates |
| 2 | MMQ / R³-VAE / soft_index / ada_modules | models/* | test_models |
| 3 | 训练循环 / 评估 / 产物 / P0 门禁 | training/evaluation/run_experiment | test_training |
| 4 | FastAPI + SQLite + SSE + 单 GPU runner | backend/* | test_api |
| 5 | React 实验控制台（门禁栏/指标图/偏差登记/队列） | frontend/src/* | vitest ×4 文件 |
| 6 | 配置模板 / README / 演示种子 / 集成验证 | configs/*, seed_demo_artifacts | test_smoke |

## 关键实现决策

- 解释器：系统 conda（torch 2.11/cu128 + fastapi + pytest 齐备）。
- pytest tmp 沙箱：沙箱禁递归删除 → 自定义 tmp fixture（只建不删）+ `pytest.ini` basetemp。
- 正交正则改为 `register_orthogonal_regularizer`（类方法），避免直接持有 ModuleList 引发的收紧问题。
- 竞态修复：互斥/取消测试改用 `max_steps=100000` + 显式 cancel 收尾，消除子进程先到终态的 flake。
- 前端：react 18 + vite 5 + vitest 2 + testing-library；`api.ts` 泛型 `handle<T>` 需显式 lambda 传参。
- `synthetic_demo` 演示数据：seed 脚本落盘三份 JSON 全带标记，Service 层拒绝启动。

## 验证命令

```bash
cd baseline/ada && C:/ProgramData/miniconda3/python.exe -m pytest tests -q   # 36 passed
cd frontend && npx vitest run        # 12 passed
cd frontend && npm run build         # tsc --noEmit + vite build OK
```

## 数据前提（外部边界）

- 特征 .npy 未落盘（Q30 G3）：任何真实训练都会在 C1 门禁被拒，属预期行为。
- Google Drive 拉取（fetch_mm_data.py）是外部前置步骤，本平台不承担。

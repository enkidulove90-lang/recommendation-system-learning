# ADA Experiment Platform

小规模原型验证平台（SAB-ANC / Hi-SAM DST 架构线）。核心层 + FastAPI 后端 + React 控制台，
覆盖 P0 门禁（C1–C5 + G-P0）、split_hash 强约束、偏差登记与运行产物管理。

## 定位与边界

- 本平台是 **脚手架 + 门禁系统**，不产出 benchmark 结论，也不执行 Google Drive 下载
  （特征文件须先由 `baseline/LightGCNpp/code/fetch_mm_data.py` 拉取落盘）。
- 12 项 Appendix-A 参数未决时，配置返回人类可读的 `blocked` 状态，**无法启动 GPU 进程**。
- `scripts/seed_demo_artifacts.py` 产生的演示数据一律带 `synthetic_demo` 标记，
  API 层拒绝启动，不代表任何实验结果。

## 快速启动

```bash
# 后端（Windows，使用系统 conda，含 torch 2.11/cu128）
cd baseline/ada
C:/ProgramData/miniconda3/python.exe -m uvicorn ada_server.api:app --app-dir backend --port 8000

# 前端
cd baseline/ada/frontend
npm install
npm run dev        # 开发（Vite 代理 /api -> :8000）
npm run build      # 生产构建
```

## 测试

```bash
# 核心 + 后端
cd baseline/ada
C:/ProgramData/miniconda3/python.exe -m pytest tests -q

# 前端
cd frontend && npx vitest run
```

## 目录

```text
configs/            ada_p0.template.yaml（Appendix-A 全参数模板）、protocol_defaults.yaml
core/ada_core/      contracts / data / gates / models(mmq, r3vae, soft_index, ada_modules) / training / evaluation
backend/ada_server/ api(FastAPI, REST+SSE) / repository(SQLite) / runner(单 GPU 子进程) / service / schemas
frontend/           React + Vite 控制台（协议配置 / 运行队列 / 门禁栏 / 指标图 / 偏差登记）
scripts/            run_experiment.py（后端唯一启动入口）、seed_demo_artifacts.py
tests/              core / backend / smoke
```

## 关键语义（Review Focus 对照）

1. **blocked 配置**：任一 Appendix-A 参数 unresolved → `ProtocolDecision.blocked=True`
   + 人类可读原因列表；后端拒绝创建 GPU 进程（`test_config_with_unresolved_appendix_value_is_blocked`）。
2. **split_hash 不符**：与 baseline 比较时 split_hash 不同 → **拒绝（reject）**，不是警告
   （`test_evaluation_rejects_baseline_with_different_split_hash`）。
3. **取消**：只终止该 run 自己的子进程（记录 PID），事件流与产物状态保持终态一致
   （`test_cancel_terminates_only_own_process`）。
4. **SSE 续传**：`Last-Event-ID` 从上次的 seq 续读，终端迁移事件不重复发送。
5. **指标图**：`null` = 缺测（渲染为 gap，非零点）；真实 0 是基线上的实点；
   P0 门禁失败在前端标红并隐藏 P1 启动控件。

## 相关文档

- 设计与参数权威：`docs/sab_anc_design.md`、`docs/sab_anc_params.md`（v1.4）、
  `docs/sab_anc_q30_register.md`
- P0 数据前提：特征 .npy 未落盘前任何训练都会在 C1 门禁被拒（见 Q30 G3）。

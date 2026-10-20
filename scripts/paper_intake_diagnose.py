from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import requests
from dotenv import dotenv_values


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".paper-work"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


@dataclass
class Check:
    component: str
    status: str
    detail: str
    action: str = ""


def config() -> dict[str, str]:
    file_values = {key: value or "" for key, value in dotenv_values(ROOT / ".env").items()}
    user_values: dict[str, str] = {}
    if sys.platform == "win32":
        try:
            import winreg

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
                for index in range(winreg.QueryInfoKey(key)[1]):
                    name, value, _ = winreg.EnumValue(key, index)
                    user_values[name] = str(value)
        except OSError:
            pass
    names = (
        "PAPER_INTAKE_API_BASE",
        "PAPER_INTAKE_WORKER_TOKEN",
        "MINERU_API_KEY",
        "DEEPSEEK_API_KEY",
        "NOTION_TOKEN",
        "NOTION_DATABASE_ID",
    )
    return {
        name: os.getenv(name) or user_values.get(name, "") or file_values.get(name, "")
        for name in names
    }


def process_alive(pid: int) -> bool:
    if sys.platform == "win32":
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0 and str(pid) in result.stdout
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        return False


def http_check(
    component: str,
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    ok_statuses: set[int] | None = None,
    auth_sensitive: bool = True,
) -> Check:
    accepted = ok_statuses or {200}
    try:
        response = requests.request(method, url, headers=headers, timeout=15, allow_redirects=False)
    except requests.RequestException as exc:
        return Check(component, "ERROR", f"network_unreachable ({type(exc).__name__})", "检查 DNS、代理和网络连接。")
    if response.status_code in accepted:
        return Check(component, "OK", f"HTTP {response.status_code}")
    if response.status_code in {401, 403} and auth_sensitive:
        return Check(component, "ERROR", f"credential_rejected (HTTP {response.status_code})", "轮换或重新配置该环节的凭据。")
    if response.status_code in {401, 403}:
        return Check(component, "WARN", f"public_api_limited (HTTP {response.status_code})", "公开 API 受限；以实际 Actions 运行结果判断发布环节。")
    return Check(component, "WARN", f"unexpected_http_status ({response.status_code})", "查看服务状态与本地错误日志。")


def local_job_check(job_id: str = "") -> Check:
    database = ROOT / "data" / "paper_intake" / "remote" / "jobs.sqlite3"
    if not database.exists():
        return Check("本地任务账本", "WARN", "尚无本地任务数据库", "提交首篇论文后再检查具体阶段。")
    try:
        connection = sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True)
        connection.row_factory = sqlite3.Row
        if job_id:
            row = connection.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
        else:
            row = connection.execute("SELECT * FROM jobs ORDER BY updated_at DESC LIMIT 1").fetchone()
        if not row:
            return Check("本地任务账本", "WARN", "未找到任务", "确认 Job ID 或先从网页提交论文。")
        stage = row["current_step"] or "received"
        detail = f"job={row['job_id']} status={row['status']} stage={stage}"
        if row["error_code"]:
            detail += f" error={row['error_code']}"
            return Check("本地任务账本", "ERROR", detail, stage_action(stage))
        return Check("本地任务账本", "OK", detail)
    except sqlite3.Error as exc:
        return Check("本地任务账本", "ERROR", f"sqlite_error ({type(exc).__name__})", "停止 Worker 后检查数据库文件权限。")
    finally:
        if "connection" in locals():
            connection.close()


def stage_action(stage: str) -> str:
    actions = {
        "validate_input": "检查论文链接、PDF 格式与大小。",
        "resolve_metadata": "检查 DOI/arXiv 链接是否公开可访问。",
        "download_pdf": "检查源站下载限制和本机网络。",
        "mineru_parse": "检查 MINERU_API_KEY、配额和 PDF 可解析性。",
        "deepseek_generate": "检查 DEEPSEEK_API_KEY、余额和模型输出。",
        "classify": "检查生成文章 JSON 与分类规则。",
        "quality_check": "检查图片、引用和文章结构门禁。",
        "notion_draft": "检查 Notion token、数据库共享权限和字段。",
        "publishing": "检查 GitHub Actions、Secrets 和 Pages 部署。",
    }
    return actions.get(stage, "查看 Worker stderr 日志与任务错误码。")


def run(job_id: str = "") -> list[Check]:
    values = config()
    missing = [name for name, value in values.items() if not value]
    checks = [
        Check(
            "配置",
            "ERROR" if missing else "OK",
            "missing=" + ",".join(missing) if missing else "required variables present (values hidden)",
            "补齐 Windows 用户环境变量或项目 .env。" if missing else "",
        )
    ]

    pid_file = RUNTIME / "remote-worker.pid"
    try:
        pid = int(pid_file.read_text(encoding="ascii").strip())
    except (FileNotFoundError, ValueError):
        pid = 0
    checks.append(
        Check(
            "后台 Worker",
            "OK" if pid and process_alive(pid) else "ERROR",
            f"running pid={pid}" if pid and process_alive(pid) else "not running or stale PID",
            "运行 scripts/paper_worker_control.ps1 start。" if not (pid and process_alive(pid)) else "",
        )
    )

    if values["PAPER_INTAKE_API_BASE"] and values["PAPER_INTAKE_WORKER_TOKEN"]:
        checks.append(
            http_check(
                "Cloudflare 接入/机器鉴权",
                "GET",
                values["PAPER_INTAKE_API_BASE"].rstrip("/") + "/v1/worker/health",
                headers={"Authorization": f"Bearer {values['PAPER_INTAKE_WORKER_TOKEN']}"},
            )
        )
    if values["MINERU_API_KEY"]:
        checks.append(
            http_check(
                "MinerU",
                "GET",
                "https://mineru.net/api/v4/extract/task/codex-health-probe",
                headers={"Authorization": f"Bearer {values['MINERU_API_KEY']}"},
                ok_statuses={200, 404},
            )
        )
    if values["DEEPSEEK_API_KEY"]:
        checks.append(
            http_check(
                "DeepSeek",
                "GET",
                "https://api.deepseek.com/models",
                headers={"Authorization": f"Bearer {values['DEEPSEEK_API_KEY']}"},
            )
        )
    if values["NOTION_TOKEN"] and values["NOTION_DATABASE_ID"]:
        checks.append(
            http_check(
                "Notion 主库",
                "GET",
                f"https://api.notion.com/v1/databases/{values['NOTION_DATABASE_ID']}",
                headers={
                    "Authorization": f"Bearer {values['NOTION_TOKEN']}",
                    "Notion-Version": "2026-03-11",
                },
            )
        )
    checks.append(
        http_check(
            "GitHub 发布",
            "GET",
            "https://api.github.com/repos/enkidulove90-lang/enkidulove90-lang.github.io/actions/runs?per_page=1",
            headers={"Accept": "application/vnd.github+json", "User-Agent": "paper-intake-diagnostics"},
            auth_sensitive=False,
        )
    )
    checks.append(local_job_check(job_id))
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose the paper intake pipeline without exposing secrets")
    parser.add_argument("--job-id", default="", help="Inspect one local job when available")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    checks = run(args.job_id)
    if args.json:
        print(json.dumps([asdict(item) for item in checks], ensure_ascii=False, indent=2))
    else:
        for item in checks:
            print(f"[{item.status:5}] {item.component}: {item.detail}")
            if item.action:
                print(f"        建议: {item.action}")
    return 1 if any(item.status == "ERROR" for item in checks) else 0


if __name__ == "__main__":
    raise SystemExit(main())


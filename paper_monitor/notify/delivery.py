"""投递：console / file / email / slack。

email/slack 仅在对应 env 配置存在时启用（通用建议，非调研报告项目）。
未配置则安全跳过，绝不抛错中断 DAG。
"""
from __future__ import annotations

from datetime import date

import requests

from ..config import Config, get_config, log


def deliver(content: str, config: Config | None = None, day: str | None = None) -> dict:
    """按 config.delivery 列表分发 content，返回各通道结果。"""
    cfg = config or get_config()
    day = day or date.today().isoformat()
    results: dict[str, str] = {}

    if "console" in cfg.delivery:
        print("\n" + content)
        results["console"] = "ok"

    if "file" in cfg.delivery:
        path = cfg.digest_path / f"digest_{day}.md"
        path.write_text(content, encoding="utf-8")
        results["file"] = str(path)

    if "email" in cfg.delivery:
        results["email"] = _send_email(content, cfg)
    if "slack" in cfg.delivery:
        results["slack"] = _send_slack(content, cfg)
    return results


def _send_email(content: str, cfg: Config) -> str:
    if not (cfg.smtp_host and cfg.smtp_user and cfg.smtp_pass and cfg.smtp_to):
        return "skipped(no-config)"
    try:
        import smtplib
        from email.mime.text import MIMEText

        msg = MIMEText(content, "markdown", "utf-8")
        msg["Subject"] = "前沿论文 Daily Digest"
        msg["From"] = cfg.smtp_user
        msg["To"] = cfg.smtp_to
        with smtplib.SMTP_SSL(cfg.smtp_host, cfg.smtp_port) as s:
            s.login(cfg.smtp_user, cfg.smtp_pass)
            s.sendmail(cfg.smtp_user, [cfg.smtp_to], msg.as_string())
        return "sent"
    except Exception as exc:
        log.warning("[delivery] email failed: %s", exc)
        return f"error:{exc}"


def _send_slack(content: str, cfg: Config) -> str:
    if not cfg.slack_webhook:
        return "skipped(no-config)"
    try:
        # Slack 单消息有长度上限，截断到 3000 字符
        payload = {"text": content[:3000]}
        resp = requests.post(cfg.slack_webhook, json=payload, timeout=15)
        return "sent" if resp.status_code == 200 else f"http:{resp.status_code}"
    except Exception as exc:
        log.warning("[delivery] slack failed: %s", exc)
        return f"error:{exc}"

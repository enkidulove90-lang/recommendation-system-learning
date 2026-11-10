"""Xiaohongshu MCP server backed by OpenCLI's Chrome Browser Bridge.

Run from the project root:
    python redbook/mcp/server.py

The server never stores browser cookies. OpenCLI reuses the login state of the
connected Chrome profile.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from typing import Any


OPENCLI_BIN = shutil.which("opencli") or "opencli"


def _run(command: list[str], timeout: int = 90) -> dict[str, Any]:
    env = {
        **os.environ,
        "PYTHONIOENCODING": "utf-8",
    }
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ok": False, "error": str(exc)}

    if result.returncode != 0:
        return {
            "ok": False,
            "error": (result.stderr.strip() or result.stdout.strip())[:2000],
            "returncode": result.returncode,
        }

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        data = {"output": result.stdout.strip()}
    return {"ok": True, "data": data}


def run_opencli(*args: str, timeout: int = 90) -> dict[str, Any]:
    command = [
        OPENCLI_BIN,
        "xiaohongshu",
        *args,
        "--format",
        "json",
    ]
    return _run(command, timeout=timeout)


def publish_content(
    *,
    title: str,
    body: str,
    images: list[str],
    topics: list[str],
    draft: bool,
) -> dict[str, Any]:
    if not title.strip():
        return {"ok": False, "error": "title is required"}
    if len(title) > 20:
        return {"ok": False, "error": "title must contain at most 20 characters"}
    if not body.strip():
        return {"ok": False, "error": "body is required"}
    if len(images) > 9:
        return {"ok": False, "error": "at most 9 images are supported"}

    command = [
        OPENCLI_BIN,
        "xiaohongshu",
        "publish",
        body,
        "--title",
        title,
        "--draft",
        str(draft).lower(),
    ]
    if images:
        command.extend(["--images", ",".join(images)])
    if topics:
        command.extend(["--topics", ",".join(topics)])
    command.extend(["--format", "json"])
    return _run(command, timeout=180)


def call_note_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    """声明式 note spec 的只读 / 本地暂存入口。

    刻意不暴露 publish：真实草稿箱写入必须由人在 CLI 显式执行
    ``redbook.cli note <slug> --publish``，避免 MCP 调用误触发。
    """
    try:
        from pathlib import Path

        from redbook.application.paper_workflow import PaperCreationWorkflow
        from redbook.services.note_spec import list_notes
    except ImportError as exc:
        return {"ok": False, "error": f"note tool dependencies unavailable: {exc}",
                "hint": "use the Python interpreter that has the project deps installed (see redbook/docs/xhs-content-spec.md §7)"}
    if name == "list_note_specs":
        return {"ok": True, "notes": list_notes()}
    slug = str(args.get("slug", "")).strip()
    if not slug:
        return {"ok": False, "error": "slug is required (filename stem in redbook/notes/)"}
    workflow = PaperCreationWorkflow(Path(str(args.get("data_root", "data"))))
    if name == "validate_note_spec":
        return workflow.validate_note(slug)
    if name == "stage_note_spec":
        return workflow.stage_note(slug)
    return {"ok": False, "error": f"Unknown note tool: {name}"}


def call_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    if name in {"list_note_specs", "validate_note_spec", "stage_note_spec"}:
        return call_note_tool(name, args)
    if name in {"check_login_status", "get_self_info"}:
        return run_opencli("whoami")
    if name == "search_feeds":
        return run_opencli("search", str(args.get("keyword", "")), timeout=120)
    if name == "get_feed_detail":
        return run_opencli("note", str(args.get("note_id", "")), timeout=120)
    if name == "publish_content":
        return publish_content(
            title=str(args.get("title", "")),
            body=str(args.get("body", "")),
            images=[str(item) for item in args.get("images", [])],
            topics=[str(item) for item in args.get("topics", [])],
            draft=bool(args.get("draft", True)),
        )
    if name == "list_user_posts":
        return run_opencli("user", str(args.get("user_id", "")), timeout=120)
    if name == "get_feeds":
        return run_opencli("feed", timeout=120)
    if name == "my_notes":
        return run_opencli("creator-notes", timeout=120)
    return {"ok": False, "error": f"Unknown tool: {name}"}


TOOLS: list[dict[str, Any]] = [
    {
        "name": "list_note_specs",
        "description": "List declarative Xiaohongshu note specs in redbook/notes/ with status and figure counts.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "validate_note_spec",
        "description": (
            "Run the repository content gate on one note spec without writing files or "
            "touching the draft box. Reports title/body/figure counts and gate errors."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "slug": {"type": "string", "description": "filename stem in redbook/notes/, e.g. 2601.21452"},
                "data_root": {"type": "string", "description": "publish queue root", "default": "data"},
            },
            "required": ["slug"],
        },
    },
    {
        "name": "stage_note_spec",
        "description": (
            "Write an immutable local review package for one note spec. Never publishes. "
            "Requires the image and PDF assets to exist on this machine."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "slug": {"type": "string", "description": "filename stem in redbook/notes/"},
                "data_root": {"type": "string", "description": "publish queue root", "default": "data"},
            },
            "required": ["slug"],
        },
    },
    {
        "name": "check_login_status",
        "description": "Check the current Xiaohongshu login state.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_self_info",
        "description": "Get the current Xiaohongshu account profile.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "search_feeds",
        "description": "Search Xiaohongshu notes by keyword.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "Search keyword"}
            },
            "required": ["keyword"],
        },
    },
    {
        "name": "get_feed_detail",
        "description": "Read a Xiaohongshu note by note ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "note_id": {"type": "string", "description": "Note ID"}
            },
            "required": ["note_id"],
        },
    },
    {
        "name": "publish_content",
        "description": (
            "Create an image note. It is saved as a draft by default; set draft "
            "to false only after the content has been reviewed."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Note title, at most 20 characters",
                },
                "body": {"type": "string", "description": "Note body"},
                "images": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Zero to nine local image paths",
                },
                "topics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Topic names without #",
                },
                "draft": {
                    "type": "boolean",
                    "description": "Save as a draft instead of publishing",
                    "default": True,
                },
            },
            "required": ["title", "body"],
        },
    },
    {
        "name": "list_user_posts",
        "description": "List public notes from a Xiaohongshu user.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "Xiaohongshu user ID"}
            },
            "required": ["user_id"],
        },
    },
    {
        "name": "get_feeds",
        "description": "Read the Xiaohongshu home feed.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "my_notes",
        "description": "List notes from the current creator account.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def handle_request(request: dict[str, Any]) -> dict[str, Any] | None:
    method = request.get("method", "")
    request_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "xiaohongshu-opencli-mcp",
                    "version": "2.0.0",
                },
                "capabilities": {"tools": {}},
            },
        }
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": TOOLS},
        }
    if method == "tools/call":
        params = request.get("params", {})
        result = call_tool(
            str(params.get("name", "")),
            dict(params.get("arguments", {})),
        )
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, ensure_ascii=False, indent=2),
                    }
                ]
            },
        }
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": f"Unknown method: {method}"},
    }


def main() -> None:
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32600, "message": str(exc)},
            }
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()

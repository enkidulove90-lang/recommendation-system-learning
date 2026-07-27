"""
Xiaohongshu MCP Server - wraps xiaohongshu-cli commands as MCP tools.

Usage:
    python server.py

Claude Code config (~/.claude/settings.json):
    "mcpServers": {
        "xiaohongshu": {
            "command": "python",
            "args": ["path/to/redbook/mcp/server.py"]
        }
    }
"""
import json, os, subprocess, sys
from pathlib import Path

# Ensure xhs is on PATH
XHS_BIN = os.path.expandvars(r"%APPDATA%\Python\Python311\Scripts\xhs.exe")
if not os.path.exists(XHS_BIN):
    XHS_BIN = "xhs"  # fallback to PATH


def run_xhs(*args, timeout=60):
    """Run xhs CLI and return parsed JSON response."""
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    try:
        result = subprocess.run(
            [XHS_BIN, *args, "--json"],
            capture_output=True, text=True, timeout=timeout, env=env,
            encoding="utf-8", errors="replace",
        )
        if result.returncode != 0:
            return {"ok": False, "error": result.stderr.strip() or result.stdout.strip()}
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"ok": False, "error": f"Parse error: {result.stdout[:300]}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def run_xhs_post(title, body, images, topics=None):
    """Run xhs post with multiple --topic flags."""
    cmd = [XHS_BIN, "post", "--title", title, "--body", body]
    for img in images:
        cmd.extend(["--images", img])
    for t in (topics or []):
        cmd.extend(["--topic", t])

    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=env)
    # Parse output for success/note_id
    output = result.stdout + result.stderr
    for line in output.split("\n"):
        if '"id":' in line or '"ok": true' in line.lower():
            return {"ok": True, "output": output[:500]}
    if result.returncode != 0:
        return {"ok": False, "error": output[:500]}
    return {"ok": True, "output": output[:500]}


# === MCP Protocol ===


def handle_request(request):
    """Handle a single MCP JSON-RPC request."""
    method = request.get("method", "")
    req_id = request.get("id", 0)
    params = request.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "xiaohongshu-mcp", "version": "1.0.0"},
                "capabilities": {"tools": {}},
            }
        }

    if method == "notifications/initialized":
        return None

    if method == "tools/list":
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {"tools": TOOLS}
        }

    if method == "tools/call":
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})
        result = call_tool(tool_name, tool_args)
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]}
        }

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown method: {method}"}}


def call_tool(name, args):
    """Dispatch tool call to xhs CLI."""
    try:
        if name == "check_login_status":
            return run_xhs("status")

        elif name == "get_self_info":
            return run_xhs("whoami")

        elif name == "search_feeds":
            return run_xhs("search", args.get("keyword", ""), timeout=30)

        elif name == "get_feed_detail":
            note_id = args.get("note_id", "")
            return run_xhs("read", note_id, timeout=30)

        elif name == "publish_content":
            return run_xhs_post(
                title=args.get("title", ""),
                body=args.get("body", ""),
                images=args.get("images", []),
                topics=args.get("topics", []),
            )

        elif name == "list_user_posts":
            return run_xhs("user-posts", args.get("user_id", ""))

        elif name == "user_profile":
            return run_xhs("user", args.get("user_id", ""))

        elif name == "like_feed":
            note_id = args.get("note_id", "")
            return run_xhs("like", note_id)

        elif name == "favorite_feed":
            note_id = args.get("note_id", "")
            return run_xhs("favorite", note_id)

        elif name == "get_feeds":
            return run_xhs("feed")

        elif name == "search_user":
            return run_xhs("search-user", args.get("keyword", ""))

        elif name == "my_notes":
            return run_xhs("my-notes")

        else:
            return {"ok": False, "error": f"Unknown tool: {name}"}

    except Exception as e:
        return {"ok": False, "error": str(e)}


TOOLS = [
    {
        "name": "check_login_status",
        "description": "Check if logged into Xiaohongshu",
        "inputSchema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "get_self_info",
        "description": "Get current user profile info (nickname, Red ID, etc.)",
        "inputSchema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "search_feeds",
        "description": "Search Xiaohongshu notes by keyword",
        "inputSchema": {
            "type": "object",
            "properties": {"keyword": {"type": "string", "description": "Search keyword"}},
            "required": ["keyword"]
        }
    },
    {
        "name": "get_feed_detail",
        "description": "Get note detail by note ID",
        "inputSchema": {
            "type": "object",
            "properties": {"note_id": {"type": "string", "description": "Note ID or URL"}},
            "required": ["note_id"]
        }
    },
    {
        "name": "publish_content",
        "description": "Publish an image note with optional topics",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Note title (max 20 chars)"},
                "body": {"type": "string", "description": "Note body text"},
                "images": {"type": "array", "items": {"type": "string"}, "description": "Image file paths"},
                "topics": {"type": "array", "items": {"type": "string"}, "description": "Topic tags"}
            },
            "required": ["title", "body", "images"]
        }
    },
    {
        "name": "list_user_posts",
        "description": "Get user's published notes by user ID",
        "inputSchema": {
            "type": "object",
            "properties": {"user_id": {"type": "string", "description": "Internal user ID (hex format)"}},
            "required": ["user_id"]
        }
    },
    {
        "name": "user_profile",
        "description": "Get user profile info by user ID",
        "inputSchema": {
            "type": "object",
            "properties": {"user_id": {"type": "string", "description": "Internal user ID"}},
            "required": ["user_id"]
        }
    },
    {
        "name": "like_feed",
        "description": "Like a note (or unlike if already liked)",
        "inputSchema": {
            "type": "object",
            "properties": {"note_id": {"type": "string", "description": "Note ID"}},
            "required": ["note_id"]
        }
    },
    {
        "name": "favorite_feed",
        "description": "Favorite (bookmark) a note",
        "inputSchema": {
            "type": "object",
            "properties": {"note_id": {"type": "string", "description": "Note ID"}},
            "required": ["note_id"]
        }
    },
    {
        "name": "get_feeds",
        "description": "Get homepage recommendation feed",
        "inputSchema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "search_user",
        "description": "Search for users by keyword/nickname",
        "inputSchema": {
            "type": "object",
            "properties": {"keyword": {"type": "string", "description": "User nickname or keyword"}},
            "required": ["keyword"]
        }
    },
    {
        "name": "my_notes",
        "description": "List my published notes",
        "inputSchema": {"type": "object", "properties": {}, "required": []}
    },
]


def main():
    """MCP stdio server loop."""

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            if response:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
        except json.JSONDecodeError:
            pass
        except Exception as e:
            err_resp = {"jsonrpc": "2.0", "id": 0, "error": {"code": -32603, "message": str(e)}}
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
